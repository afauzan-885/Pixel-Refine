"""Reproducible WeightNet native/ORT comparison; run from repository root.

Synthetic image values are analytic/deterministic. Expected neural weight maps
come from the unchanged ONNX model, not an invented ideal confidence map.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import threading
import time
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def fixtures(size):
    yy, xx = np.mgrid[:size, :size].astype(np.float32)
    ramp = (0.1 + 0.6 * xx / (size-1) + 0.15 * yy / (size-1)).astype(np.float32)
    pattern = np.clip(ramp + 0.08*np.sin(xx*0.17)*np.cos(yy*0.11), 0, 1).astype(np.float32)
    rng = np.random.default_rng(20261014)
    cases = {
        "black_identity": (np.zeros_like(ramp), np.zeros_like(ramp)),
        "white_identity": (np.ones_like(ramp), np.ones_like(ramp)),
        "gray_identity": (np.full_like(ramp, 0.5), np.full_like(ramp, 0.5)),
        "ramp_identity": (ramp, ramp.copy()),
        "noise_sigma_002": (pattern, np.clip(pattern+rng.normal(0,0.02,pattern.shape).astype(np.float32),0,1)),
        "translation_dx3_dy2": (pattern, np.roll(pattern,(2,3),(0,1))),
        "exposure_plus_01": (pattern, np.clip(pattern+np.float32(0.1),0,1)),
        "checker_inverse": (((xx.astype(int)//8+yy.astype(int)//8)%2).astype(np.float32),
                            (1-(xx.astype(int)//8+yy.astype(int)//8)%2).astype(np.float32)),
    }
    return {k:{"ref_img":np.ascontiguousarray(r[None,None]), "support_img":np.ascontiguousarray(s[None,None])} for k,(r,s) in cases.items()}


def errors(actual, expected):
    diff = actual.astype(np.float64)-expected.astype(np.float64)
    return {"max_abs":float(np.max(np.abs(diff))), "mean_abs":float(np.mean(np.abs(diff))),
            "rmse":float(np.sqrt(np.mean(diff*diff))), "finite":bool(np.isfinite(actual).all()),
            "range":[float(actual.min()),float(actual.max())],
            "cutoff_005_disagreements":int(np.count_nonzero((actual>=0.05)!=(expected>=0.05)))}


def _process_memory_bytes(process):
    info=process.memory_info()
    return {
        "rss_bytes":int(info.rss),
        "peak_working_set_bytes":int(getattr(info,"peak_wset",0) or 0) or None,
        "private_bytes":int(getattr(info,"private",0) or 0) or None,
        "peak_pagefile_bytes":int(getattr(info,"peak_pagefile",0) or 0) or None,
    }


def _gpu_process_memory_snapshot():
    """Read Windows WDDM memory counters for this Python process by adapter."""
    if sys.platform != "win32":
        return {"status":"unsupported_platform","process_id":os.getpid(),"samples":[]}
    command=r"""
$targetPid = [int]$env:TI_WEIGHTNET_BENCHMARK_PID
$diagnosticsModule = Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Diagnostics\Microsoft.PowerShell.Diagnostics.psd1'
Import-Module -Name $diagnosticsModule -ErrorAction Stop
$targetInstancePrefix = "pid_{0}_" -f $targetPid
$targetPaths = @(
  (Get-Counter -ListSet 'GPU Process Memory' -ErrorAction Stop).PathsWithInstances |
    Where-Object {
      $_.IndexOf($targetInstancePrefix, [StringComparison]::OrdinalIgnoreCase) -ge 0
    }
)
$samples = @()
if ($targetPaths.Count -gt 0) {
  $samples = @(Get-Counter -Counter $targetPaths -MaxSamples 1 -ErrorAction Stop |
    ForEach-Object { $_.CounterSamples } |
    Where-Object {
      $_.Status -eq 0 -and $_.InstanceName.StartsWith(
        $targetInstancePrefix, [StringComparison]::OrdinalIgnoreCase
      )
    } |
    ForEach-Object {
      [pscustomobject]@{
        instance = $_.InstanceName
        counter = ($_.Path -split '\\')[-1]
        value_bytes = [int64][Math]::Max(0, [Math]::Round($_.CookedValue))
      }
    })
}
[pscustomobject]@{
  status = if ($samples.Count -gt 0) { 'sampled' } else { 'no_process_counter_instances' }
  process_id = $targetPid
  samples = $samples
} | ConvertTo-Json -Depth 5 -Compress
"""
    environment=os.environ.copy()
    environment["TI_WEIGHTNET_BENCHMARK_PID"]=str(os.getpid())
    try:
        result=subprocess.run(
            ["powershell.exe","-NoLogo","-NoProfile","-NonInteractive","-Command",command],
            check=False,capture_output=True,text=True,timeout=20,env=environment)
    except (OSError,subprocess.TimeoutExpired) as exc:
        return {"status":"counter_query_failed","process_id":os.getpid(),
                "samples":[],"error":f"{type(exc).__name__}: {exc}"}
    if result.returncode != 0:
        return {"status":"counter_query_failed","process_id":os.getpid(),
                "samples":[],"error":(result.stderr or result.stdout).strip()[-2000:]}
    try:
        snapshot=json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {"status":"counter_output_invalid","process_id":os.getpid(),
                "samples":[],"error":str(exc)}
    if not isinstance(snapshot,dict) or not isinstance(snapshot.get("samples"),list):
        return {"status":"counter_output_invalid","process_id":os.getpid(),
                "samples":[],"error":"WDDM counter response had an unexpected shape"}
    return snapshot


class _NvidiaMemorySampler:
    """Samples device-global NVIDIA memory outside the timed benchmark loop."""

    def __init__(self, target_hint):
        self.target_hint=str(target_hint or "NVIDIA").lower()
        self.samples=[]
        self.error=None
        self.process=None
        self.reader=None

    def start(self):
        executable=shutil.which("nvidia-smi")
        if not executable:
            self.error="nvidia-smi unavailable"
            return
        command=[executable,"--query-gpu=index,name,uuid,memory.used,memory.total",
                 "--format=csv,noheader,nounits","--loop-ms=100"]
        options={"stdout":subprocess.PIPE,"stderr":subprocess.DEVNULL,
                 "text":True,"bufsize":1}
        if os.name=="nt":
            options["creationflags"]=getattr(subprocess,"CREATE_NO_WINDOW",0)
        try:
            self.process=subprocess.Popen(command,**options)
            self.reader=threading.Thread(target=self._read,daemon=True,
                                         name="taichi-nvidia-memory-sampler")
            self.reader.start()
            deadline=time.monotonic()+0.5
            while not self.samples and self.process.poll() is None and time.monotonic()<deadline:
                time.sleep(0.01)
        except Exception as exc:
            self.error=f"{type(exc).__name__}: {exc}"
            self.process=None

    def _read(self):
        try:
            for line in self.process.stdout:
                try:
                    fields=next(csv.reader([line],skipinitialspace=True))
                    if len(fields)<5 or self.target_hint not in fields[1].lower():
                        continue
                    used,total=int(fields[3]),int(fields[4])
                    self.samples.append({"index":fields[0].strip(),"name":fields[1].strip(),
                                         "uuid":fields[2].strip(),"used_mib":used,
                                         "total_mib":total,"time_ns":time.perf_counter_ns()})
                except (StopIteration,ValueError,IndexError):
                    continue
        except Exception as exc:
            self.error=f"{type(exc).__name__}: {exc}"

    def stop(self):
        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                    self.process.wait(timeout=2)
                except Exception:
                    pass
        if self.reader is not None:
            self.reader.join(timeout=2)

    def report(self):
        if not self.samples:
            return {"available":False,"scope":"device-global sampled memory",
                    "error":self.error or "no matching NVIDIA device sample"}
        values=[sample["used_mib"] for sample in self.samples]
        first=self.samples[0]
        return {"available":True,"scope":"device-global; includes other processes",
                "device_index":first["index"],"device":first["name"],
                "device_uuid":first["uuid"],"total_mib":first["total_mib"],
                "baseline_used_mib":values[0],"peak_sampled_used_mib":max(values),
                "peak_delta_mib":max(values)-values[0],"sample_count":len(values),
                "sample_period_ms":100,"error":self.error}


class _MemoryWindow:
    """Captures process working set and optional GPU memory around one probe."""

    def __init__(self, target_hint=None):
        self.target_hint=target_hint
        self.process=None
        self.before=None
        self.samples=[]
        self.wddm_before=None
        self.wddm_after=None
        self.stop_event=threading.Event()
        self.sampler=None
        self.thread=None

    def __enter__(self):
        import psutil
        self.process=psutil.Process(os.getpid())
        self.before=_process_memory_bytes(self.process)
        self.samples.append(self.before["rss_bytes"])
        if self.target_hint and sys.platform=="win32":
            self.wddm_before=_gpu_process_memory_snapshot()
        is_nvidia=bool(self.target_hint and "nvidia" in str(self.target_hint).lower())
        self.sampler=_NvidiaMemorySampler(self.target_hint) if is_nvidia else None
        if self.sampler is not None:
            self.sampler.start()
        self.thread=threading.Thread(target=self._sample_process,daemon=True,
                                     name="taichi-process-memory-sampler")
        self.thread.start()
        return self

    def _sample_process(self):
        while not self.stop_event.is_set():
            try:
                self.samples.append(int(self.process.memory_info().rss))
            except Exception:
                pass
            self.stop_event.wait(0.01)

    def __exit__(self, exc_type, exc, traceback):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=1)
        if self.sampler is not None:
            self.sampler.stop()
        if self.target_hint and sys.platform=="win32":
            self.wddm_after=_gpu_process_memory_snapshot()

    def report(self):
        after=_process_memory_bytes(self.process)
        result={"process":{"before":self.before,"after":after,
                           "peak_sampled_rss_bytes":max(self.samples),
                           "sample_period_ms":10,"sample_count":len(self.samples)}}
        if self.sampler is not None:
            result["gpu"]=self.sampler.report()
        if self.target_hint and sys.platform=="win32":
            result["device_process_memory"]={
                "measurement_source":"Windows GPU Process Memory WDDM counters",
                "scope":"process-wide allocations, reported separately by adapter LUID; includes Taichi, ONNX Runtime, and driver-managed memory",
                "sampling":"before/after boundary snapshots; not a continuous peak trace",
                "before":self.wddm_before,"after":self.wddm_after}
        return result


def _native_graph_memory(graph):
    """Reports executor-owned ndarray bytes, not allocator/driver fragmentation."""
    if graph is None:
        return {"available":False,"reason":"model has no native graph"}
    unique={}
    for name,buffer in graph.buffers.items():
        if buffer is None:
            continue
        key=id(buffer)
        if key not in unique:
            unique[key]={"bytes":int(np.prod(tuple(buffer.shape) or (1)))*4,
                         "names":[]}
        unique[key]["names"].append(name)
    scratch_bytes=sum(int(np.prod(tuple(buf.shape) or (1)))*4
                      for buf in graph.scratch.values())
    dummy_bytes=int(np.prod(tuple(graph.dummy.shape) or (1)))*4
    return {"available":True,"dtype":"float32",
            "unique_persistent_buffer_count":len(unique)+len(graph.scratch)+1,
            "persistent_tensor_bytes":sum(item["bytes"] for item in unique.values()),
            "scratch_bytes":scratch_bytes,"dummy_bytes":dummy_bytes,
            "known_executor_bytes":sum(item["bytes"] for item in unique.values())+scratch_bytes+dummy_bytes,
            "liveness_buffer_plan":dict(graph.buffer_plan_stats),
            "includes_backend_workspace_or_allocator_fragmentation":False}


def select_oracle_adapter(adapters, vendor, device_id=None):
    """Select one explicit hardware adapter; never guess among same-vendor GPUs."""
    normalized_vendor=str(vendor or "").strip().lower()
    if normalized_vendor not in ("intel", "nvidia", "amd"):
        raise ValueError(f"Unsupported DirectML oracle vendor: {vendor!r}")
    candidates=[a for a in adapters if str(a.get("vendor","")).lower()==normalized_vendor]
    if device_id is not None:
        candidates=[a for a in candidates if int(a.get("device_id",-1))==device_id]
    if not candidates:
        suffix=f" with device_id={device_id}" if device_id is not None else ""
        raise RuntimeError(f"No DirectML {normalized_vendor} adapter{suffix}")
    if len(candidates)!=1:
        ids=[a.get("device_id") for a in candidates]
        raise RuntimeError(
            f"Multiple DirectML {normalized_vendor} adapters match {ids}; "
            "specify --oracle-device-id"
        )
    return candidates[0]


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--size",type=int,choices=(512,1024),required=True)
    p.add_argument("--backend",default="cuda",choices=("cuda","cpu","vulkan","opengl"))
    p.add_argument("--oracle-vendor",choices=("intel","nvidia","amd"),default=None,
                   help="DirectML oracle vendor; inferred for CUDA or from TARGET_VENDOR/OpenGL context otherwise")
    p.add_argument("--oracle-device-id",type=int,default=None,
                   help="DXGI adapter ordinal when more than one adapter matches the oracle vendor")
    p.add_argument("--cpu-threads",type=int,default=8,
                   help="Taichi CPU worker threads used for the CPU profile")
    p.add_argument("--runs",type=int,default=10)
    p.add_argument("--cases",default="all")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--profile",action="store_true")
    p.add_argument("--trace",action="store_true")
    p.add_argument("--paired",action="store_true")
    p.add_argument("--fast-math",action="store_true")
    p.add_argument("--application",action="store_true")
    args=p.parse_args()
    import onnxruntime as ort
    import taichi as ti
    if args.application and args.backend != "cuda":
        p.error("--application currently validates the Taichi CUDA application route only")
    adapter=None
    oracle_vendor=None
    if args.backend != "cpu":
        from pixel_refine_desktop.enhance_stack.core.algorithm.onnx_utils import scan_directml_adapters
        adapters=scan_directml_adapters()
        oracle_vendor=args.oracle_vendor
        if oracle_vendor is None and args.backend=="cuda":
            oracle_vendor="nvidia"
        if oracle_vendor is None:
            oracle_vendor=(os.environ.get("OPENGL_EXPECTED_VENDOR") if args.backend=="opengl" else None)
            oracle_vendor=oracle_vendor or os.environ.get("TARGET_VENDOR") or os.environ.get("ONNX_TARGET_VENDOR")
        if not oracle_vendor:
            p.error("Set --oracle-vendor or TARGET_VENDOR for a non-CUDA GPU backend")
        adapter=select_oracle_adapter(adapters,oracle_vendor,args.oracle_device_id)
    bundle=ROOT/"database/Learning_Model/weightNet/weightnet_master.bundle"
    profile="cpu" if args.backend == "cpu" else "gpu"
    member=f"weightnet_{args.size}_{profile}_1c_fp32.onnx"
    with zipfile.ZipFile(bundle) as z:
        raw=z.read(member)
    options=ort.SessionOptions()
    options.graph_optimization_level=(ort.GraphOptimizationLevel.ORT_ENABLE_ALL if profile=="cpu"
                                     else ort.GraphOptimizationLevel.ORT_DISABLE_ALL)
    options.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
    options.enable_mem_pattern=profile=="cpu"
    options.add_session_config_entry("session.use_device_allocator_for_initializers","1")
    oracle_providers=(["CPUExecutionProvider"] if profile=="cpu" else
                      [("DmlExecutionProvider",{"device_id":adapter["device_id"]})])
    if profile=="gpu":
        options.add_session_config_entry("session.disable_cpu_ep_fallback","1")
    oracle=ort.InferenceSession(raw,sess_options=options,providers=oracle_providers)
    data=fixtures(args.size)
    if args.cases!="all":
        data={k:data[k] for k in args.cases.split(",")}
    expected={k:oracle.run(None,v) for k,v in data.items()}
    from taichi_vision.taichi_aot import neural_engine
    init_options={"arch":getattr(ti,args.backend),"enable_fallback":False,
                  "fast_math":args.fast_math,"kernel_profiler":args.profile}
    if args.backend=="cpu":
        init_options["cpu_max_num_threads"]=args.cpu_threads
    ti.init(**init_options)
    opengl_context = (neural_engine._get_opengl_context_info()
                      if args.backend=="opengl" else None)
    model=neural_engine.onnx(raw,backend=args.backend)
    report={"shape":[1,1,args.size,args.size],"dtype":"float32","native_backend":args.backend,
            "taichi_cpu_threads":args.cpu_threads if args.backend=="cpu" else None,
            "taichi_visible_device":os.environ.get("TI_VISIBLE_DEVICE") if args.backend=="vulkan" else None,
            "taichi_opengl_context":opengl_context,
            "oracle_provider":oracle.get_providers(),"oracle_adapter":adapter,
            "oracle_selection":{"vendor":oracle_vendor,"requested_device_id":args.oracle_device_id,
                                "selection":"explicit vendor/device; CPU fallback disabled for GPU profile"},
            "model_member":member,"model_sha256":hashlib.sha256(raw).hexdigest(),
            "ort":ort.__version__,"taichi":str(ti.__version__),"fast_math":args.fast_math,
            "boundary":"host input to owned host output; sequential calls",
            "gates":{"weight_max_abs":1e-3,"weight_rmse":5e-5,"alpha_max_abs":1e-5},
            "cases":{}}
    memory_target=str(adapter.get("name") or "") if adapter else None
    if args.trace:
        import onnx
        graph_model=onnx.shape_inference.infer_shapes(onnx.load_model_from_string(raw))
        metadata={v.name:v for v in list(graph_model.graph.value_info)+list(graph_model.graph.output)}
        trace_outputs=[(n,o) for n in graph_model.graph.node for o in n.output]
        trace_names=[o for _,o in trace_outputs]
        del graph_model.graph.output[:]
        graph_model.graph.output.extend(metadata[n] for n in trace_names)
        diagnostic=ort.InferenceSession(graph_model.SerializeToString(),sess_options=options,providers=oracle_providers)
        feed=data.get("noise_sigma_002",next(iter(data.values())))
        ref=diagnostic.run(None,feed)
        model.run(None,feed)
        trace=[]
        for (node, output), target in zip(trace_outputs,ref):
            actual=model._native_graph.buffers[output].to_numpy().reshape(target.shape)
            trace.append({"op":node.op_type,"output":output,**errors(actual,target)})
        report["trace"]=trace
        del diagnostic
    for name,feed in data.items():
        start=time.perf_counter()
        actual=model.run(None,feed)
        report["cases"][name]={"weight_map":errors(actual[0],expected[name][0]),"alpha":errors(actual[1],expected[name][1]),
                               "first_call_ms":(time.perf_counter()-start)*1000}
        print(name,json.dumps(report["cases"][name]),flush=True)
        if args.paired:
            model._native_graph.optimized=False
            baseline=model.run(None,feed)
            model._native_graph.optimized=True
            report["cases"][name]["optimized_vs_scalar"]=[errors(a,b) for a,b in zip(actual,baseline)]
            assert all(np.array_equal(a,b) for a,b in zip(actual,baseline)), name
    feed=data.get("noise_sigma_002",next(iter(data.values())))
    for _ in range(3):
        oracle.run(None,feed)
        model.run(None,feed)
        if args.paired:
            model._native_graph.optimized=False
            model.run(None,feed)
            model._native_graph.optimized=True
    samples={"onnx":[],"native":[]}
    if args.paired:
        samples["native_scalar"]=[]
    if args.profile:
        ti.profiler.clear_kernel_profiler_info()
    for i in range(args.runs):
        order=list(samples) if i%2==0 else list(reversed(samples))
        for name in order:
            model._native_graph.optimized=name!="native_scalar"
            start=time.perf_counter()
            (oracle if name=="onnx" else model).run(None,feed)
            samples[name].append((time.perf_counter()-start)*1000)
    model._native_graph.optimized=True
    report["timing"]={k:{"median_ms":statistics.median(v),"mean_ms":statistics.mean(v),"samples_ms":v} for k,v in samples.items()}
    if args.profile:
        ti.profiler.print_kernel_profiler_info()
    memory_case=data.get("noise_sigma_002",next(iter(data.values())))
    with _MemoryWindow(memory_target if args.backend!="cpu" else None) as window:
        host_memory_output=model.run(None,memory_case)
    host_memory_metrics=window.report()
    host_memory_expected=expected[next(name for name,feed in data.items() if feed is memory_case)]
    host_output_bytes=sum(np.asarray(value).nbytes for value in host_memory_output)
    input_bytes=sum(np.asarray(value).nbytes for value in memory_case.values())
    host_memory_metrics["boundary"]={"mode":"numpy input to owned host output",
        "input_bytes_h2d_per_call":input_bytes if args.backend!="cpu" else 0,
        "input_bytes_host_to_taichi_array_per_call":input_bytes if args.backend=="cpu" else 0,
        "output_bytes_d2h_per_call":host_output_bytes if args.backend!="cpu" else 0,
        "output_bytes_extra_host_copy_per_call":host_output_bytes,
        "readback_inside_call":args.backend!="cpu",
        "note":"Boundary byte counts are derived from tensor sizes; internal backend workspace is not included."}
    host_memory_metrics["output_parity"]=[errors(actual,target)
        for actual,target in zip(host_memory_output,host_memory_expected)]

    device_inputs={}
    device_flat_inputs={}
    for name,array in memory_case.items():
        device_inputs[name]=ti.ndarray(ti.f32,array.shape)
        device_inputs[name].from_numpy(array)
        device_flat_inputs[name]=ti.ndarray(ti.f32,(array.size,))
        device_flat_inputs[name].from_numpy(array.reshape(-1))
    with _MemoryWindow(memory_target if args.backend!="cpu" else None) as window:
        resident_memory_output=model.run(None,device_inputs,return_gpu=True)
    resident_memory_metrics=window.report()
    resident_host_output=[value.to_numpy().reshape(model._native_graph.shapes[name])
                          for name,value in zip(model._native_graph.outputs,resident_memory_output)]
    resident_memory_metrics["boundary"]={"mode":"Taichi-array input to Taichi-array output",
        "host_to_device_bytes_during_call":0,
        "taichi_array_input_copy_bytes_per_call":input_bytes,
        "taichi_array_output_copy_bytes_per_call":host_output_bytes,
        "device_input_copy_bytes_per_call":input_bytes if args.backend!="cpu" else 0,
        "device_output_copy_bytes_per_call":host_output_bytes if args.backend!="cpu" else 0,
        "device_output_new_allocation_bytes_per_call":host_output_bytes,
        "readback_inside_call":False,
        "validation_readback_bytes_after_probe":host_output_bytes if args.backend!="cpu" else 0,
        "validation_host_copy_bytes_after_probe":host_output_bytes,
        "note":"Current executor copies device inputs into graph buffers and copies outputs into new arrays; only the accuracy readback occurs after the measured call."}
    resident_memory_metrics["output_parity"]=[errors(actual,target)
        for actual,target in zip(resident_host_output,host_memory_expected)]
    resident_memory_metrics["setup_input_upload_bytes_outside_call"]=input_bytes

    # Measure steady resident execution with and without executor-owned output
    # copies. Synchronize both paths so elapsed time includes completed kernels.
    resident_timing={"owned_output_copy_ms":[],"borrowed_output_view_ms":[]}
    for _ in range(3):
        model.run(None,device_inputs,return_gpu=True)
        model.run(None,device_flat_inputs,return_gpu=True,borrowed_outputs=True)
        ti.sync()
    for i in range(args.runs):
        names=("owned_output_copy_ms","borrowed_output_view_ms")
        if i%2:
            names=tuple(reversed(names))
        for mode in names:
            start=time.perf_counter()
            inputs=(device_flat_inputs if mode=="borrowed_output_view_ms" else device_inputs)
            result=model.run(None,inputs,return_gpu=True,
                             borrowed_outputs=mode=="borrowed_output_view_ms")
            ti.sync()
            resident_timing[mode].append((time.perf_counter()-start)*1000)
    report["resident_timing"]={k:{"median_ms":statistics.median(v),
                                 "mean_ms":statistics.mean(v),"samples_ms":v}
                               for k,v in resident_timing.items()}

    with _MemoryWindow(memory_target if args.backend!="cpu" else None) as window:
        borrowed_memory_output=model.run(None,device_flat_inputs,return_gpu=True,borrowed_outputs=True)
    borrowed_memory_metrics=window.report()
    borrowed_host_output=[value.to_numpy().reshape(model._native_graph.shapes[name])
                          for name,value in zip(model._native_graph.outputs,borrowed_memory_output)]
    borrowed_memory_metrics["boundary"]={"mode":"borrowed Taichi-array input and graph-owned output view",
        "host_to_device_bytes_during_call":0,
        "taichi_array_input_copy_bytes_per_call":0,
        "taichi_array_output_copy_bytes_per_call":0,
        "device_input_copy_bytes_per_call":0,
        "device_output_copy_bytes_per_call":0,
        "device_output_new_allocation_bytes_per_call":0,
        "readback_inside_call":False,
        "validation_readback_bytes_after_probe":host_output_bytes if args.backend!="cpu" else 0,
        "validation_host_copy_bytes_after_probe":host_output_bytes,
        "borrowed_view_lifetime":"until the next call to this model; output storage is executor-owned",
        "note":"Input Taichi arrays are substituted for graph input buffers during the call; returned outputs alias preallocated graph buffers. Validation readback occurs after the measured call."}
    borrowed_memory_metrics["output_parity"]=[errors(actual,target)
        for actual,target in zip(borrowed_host_output,host_memory_expected)]
    borrowed_memory_metrics["setup_input_upload_bytes_outside_call"]=input_bytes
    report["memory"]={"measurement":"separate probes after latency sampling; process RSS plus Windows WDDM process-memory boundary snapshots for GPU profiles; NVIDIA device-global samples are supplemental",
                       "native_graph":_native_graph_memory(model._native_graph),
                       "host_boundary_probe":host_memory_metrics,
                       "resident_boundary_probe":resident_memory_metrics,
                       "borrowed_resident_boundary_probe":borrowed_memory_metrics,
                       "limitations":["WDDM memory is process-wide and can include ONNX Runtime plus Taichi allocations; adapter instances are keyed by LUID.",
                                      "WDDM measurements are boundary snapshots, not continuous per-process peaks.",
                                      "NVIDIA device-global samples include other processes and can miss short-lived peaks.",
                                      "Executor buffer bytes exclude Taichi runtime workspace and driver allocator fragmentation."]}
    memory_gate_passed=all(
        errors_value["finite"]
        and errors_value["max_abs"]<=report["gates"]["weight_max_abs"]
        and errors_value["rmse"]<=report["gates"]["weight_rmse"]
        for errors_value in (host_memory_metrics["output_parity"][0],
                             resident_memory_metrics["output_parity"][0],
                             borrowed_memory_metrics["output_parity"][0]))
    memory_gate_passed=memory_gate_passed and all(
        errors_value["finite"] and errors_value["max_abs"]<=report["gates"]["alpha_max_abs"]
        for errors_value in (host_memory_metrics["output_parity"][1],
                             resident_memory_metrics["output_parity"][1],
                             borrowed_memory_metrics["output_parity"][1]))
    report["memory"]["parity_gate_passed"]=memory_gate_passed
    if args.application:
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import load_weightnet_onnx, infer_single_support_weight_map
        loaded=load_weightnet_onnx(bundle,runtime="taichi_cuda",patch_size=args.size)
        raw=loaded.run(None,feed)
        np.testing.assert_array_equal(raw[0],model.run(None,feed)[0])
        app_kwargs={"tile_size":args.size,"overlap":0.0,"return_scalar":True}
        app_native=infer_single_support_weight_map(loaded,feed["ref_img"][0],feed["support_img"][0],**app_kwargs)
        app_oracle=infer_single_support_weight_map(oracle,feed["ref_img"][0],feed["support_img"][0],**app_kwargs)
        wn,wo=app_native[0],app_oracle[0]
        rn,sn=feed["ref_img"][0],feed["support_img"][0]
        fused_native=(rn+sn*wn)/(1+wn)
        fused_oracle=(rn+sn*wo)/(1+wo)
        report["application"]={"weight_map":errors(wn,wo),"fused_image":errors(fused_native,fused_oracle),
                               "scope":"one tile, overlap=0, Hann stitching, cutoff=0.05, unit reference weight"}
        assert report["application"]["fused_image"]["max_abs"] < 5e-5
        resident=loaded.run(None,device_inputs,return_gpu=True)
        np.testing.assert_array_equal(resident[0].to_numpy(),raw[0])
        saved=resident[0].to_numpy()
        loaded.run(None,{k:np.zeros_like(v) for k,v in feed.items()})
        np.testing.assert_array_equal(resident[0].to_numpy(),saved)
        report["resident_output_owned_and_equal"]=True
    report["passed"]=all(
        c["weight_map"]["finite"] and c["alpha"]["finite"]
        and c["weight_map"]["max_abs"]<=report["gates"]["weight_max_abs"]
        and c["weight_map"]["rmse"]<=report["gates"]["weight_rmse"]
        and c["alpha"]["max_abs"]<=report["gates"]["alpha_max_abs"]
        for c in report["cases"].values()) and memory_gate_passed
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report["timing"]),flush=True)
    assert report["passed"], "Native/ONNX numerical gate failed; see JSON evidence"


if __name__=="__main__":
    main()
