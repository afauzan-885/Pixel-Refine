; ModuleID = 'kernel'
source_filename = "kernel"
target triple = "nvptx64-nvidia-cuda"

%struct.RuntimeContext = type { i8*, %struct.LLVMRuntime*, i32, i64* }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager*], [1024 x %struct.NodeManager*], [1024 x i8*], i8*, %struct.RandState*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { i8*, i8*, i64 }
%struct.ListManager = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime* }
%struct.NodeManager = type { %struct.LLVMRuntime*, i32, i32, i32, i32, %struct.ListManager*, %struct.ListManager*, %struct.ListManager*, i32 }
%struct.RandState = type { i32, i32, i32, i32, i32 }
%struct.float2 = type { float, float }

@"$str" = private addrspace(1) constant [11 x i8] c"__CUDA_FTZ\00"

define void @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_0_serial(%struct.RuntimeContext* byval(%struct.RuntimeContext) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %context, i32 0, i32 0
  %1 = bitcast i8** %0 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %2 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %1, align 8
  %3 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %2, i32 0, i32 4
  %4 = load i32, i32* %3, align 4
  %5 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %context)
  %6 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %5, i64 12)
  %7 = bitcast i8* %6 to i32*
  store i32 %4, i32* %7, align 4
  %8 = call i32 @max_i32(i32 0, i32 %4)
  %9 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %context, i32 0, i32 0
  %10 = bitcast i8** %9 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %11 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %10, align 8
  %12 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %11, i32 0, i32 5
  %13 = load i32, i32* %12, align 4
  %14 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %context)
  %15 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %14, i64 8)
  %16 = bitcast i8* %15 to i32*
  store i32 %13, i32* %16, align 4
  %17 = call i32 @max_i32(i32 0, i32 %13)
  %18 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %context)
  %19 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %18, i64 4)
  %20 = bitcast i8* %19 to i32*
  store i32 %17, i32* %20, align 4
  %21 = mul i32 %8, %17
  %22 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %context)
  %23 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %22, i64 0)
  %24 = bitcast i8* %23 to i32*
  store i32 %21, i32* %24, align 4
  br label %final
}

define void @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_1_range_for(%struct.RuntimeContext* byval(%struct.RuntimeContext) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %context)
  %1 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %0, i64 0)
  %2 = bitcast i8* %1 to i32*
  %3 = load i32, i32* %2, align 4
  call void @gpu_parallel_range_for(%struct.RuntimeContext* %context, i32 0, i32 %3, void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*, i32)* @function_body, void (%struct.RuntimeContext*, i8*)* null, i64 1)
  br label %final
}

define internal void @function_body(%struct.RuntimeContext* %0, i8* %1, i32 %2) {
allocs:
  %3 = alloca i32, align 4
  %4 = alloca float, align 4
  br label %entry

final:                                            ; preds = %after_if6
  ret void

entry:                                            ; preds = %allocs
  br label %function_body

function_body:                                    ; preds = %entry
  store i32 %2, i32* %3, align 4
  %5 = load i32, i32* %3, align 4
  %6 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %0)
  %7 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %6, i64 4)
  %8 = bitcast i8* %7 to i32*
  %9 = load i32, i32* %8, align 4
  %10 = sdiv i32 %5, %9
  %11 = icmp slt i32 %5, 0
  %12 = icmp slt i32 %9, 0
  %13 = mul i32 %9, %10
  %14 = icmp ne i1 %11, %12
  %15 = icmp ne i32 %5, 0
  %16 = icmp ne i32 %13, %5
  %17 = icmp ne i1 %14, false
  %18 = icmp ne i1 %15, false
  %19 = and i1 %17, %18
  %20 = icmp ne i1 %19, false
  %21 = icmp ne i1 %16, false
  %22 = and i1 %20, %21
  %23 = zext i1 %22 to i32
  %24 = sub i32 %10, %23
  %25 = mul i32 %24, %9
  %26 = sub i32 %5, %25
  %27 = sitofp i32 %26 to float
  %28 = fadd reassoc ninf nsz float %27, 5.000000e-01
  %29 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %0)
  %30 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %29, i64 8)
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sitofp i32 %32 to float
  %34 = fdiv reassoc ninf nsz float %28, %33
  %35 = sitofp i32 %24 to float
  %36 = fadd reassoc ninf nsz float %35, 5.000000e-01
  %37 = call %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* %0)
  %38 = call i8* @get_temporary_pointer(%struct.LLVMRuntime* %37, i64 12)
  %39 = bitcast i8* %38 to i32*
  %40 = load i32, i32* %39, align 4
  %41 = sitofp i32 %40 to float
  %42 = fdiv reassoc ninf nsz float %36, %41
  %43 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %44 = bitcast i8** %43 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %45 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %44, align 8
  %46 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %45, i32 0, i32 3
  %47 = load i32, i32* %46, align 4
  %48 = sitofp i32 %47 to float
  %49 = fmul reassoc ninf nsz float %34, %48
  %50 = fsub reassoc ninf nsz float %49, 5.000000e-01
  %51 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %52 = bitcast i8** %51 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %53 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %52, align 8
  %54 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %53, i32 0, i32 2
  %55 = load i32, i32* %54, align 4
  %56 = sitofp i32 %55 to float
  %57 = fmul reassoc ninf nsz float %42, %56
  %58 = fsub reassoc ninf nsz float %57, 5.000000e-01
  %59 = call reassoc ninf nsz float @llvm.floor.f32(float %50)
  %60 = fptosi float %59 to i32
  %61 = call reassoc ninf nsz float @llvm.floor.f32(float %58)
  %62 = fptosi float %61 to i32
  %63 = sitofp i32 %60 to float
  %64 = fsub reassoc ninf nsz float %50, %63
  %65 = sitofp i32 %62 to float
  %66 = fsub reassoc ninf nsz float %58, %65
  %67 = sub i32 %47, 2
  %68 = call i32 @max_i32(i32 0, i32 %60)
  %69 = call i32 @min_i32(i32 %67, i32 %68)
  %70 = sub i32 %55, 2
  %71 = call i32 @max_i32(i32 0, i32 %62)
  %72 = call i32 @min_i32(i32 %70, i32 %71)
  %73 = add i32 %69, 1
  %74 = add i32 %72, 1
  %75 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %76 = bitcast i8** %75 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %77 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %76, align 8
  %78 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %77, i32 0, i32 0
  %79 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 1
  %80 = load i32*, i32** %79, align 8
  %81 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 0
  %82 = load i32, i32* %81, align 4
  %83 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 1
  %84 = load i32, i32* %83, align 4
  %85 = mul i32 0, %82
  %86 = add i32 %85, %72
  %87 = mul i32 %86, %84
  %88 = add i32 %87, %69
  %89 = getelementptr i32, i32* %80, i32 %88
  %90 = load i32, i32* %89, align 4
  %91 = sitofp i32 %90 to float
  %92 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 1
  %93 = load i32*, i32** %92, align 8
  %94 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 0
  %95 = load i32, i32* %94, align 4
  %96 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 1
  %97 = load i32, i32* %96, align 4
  %98 = mul i32 0, %95
  %99 = add i32 %98, %72
  %100 = mul i32 %99, %97
  %101 = add i32 %100, %73
  %102 = getelementptr i32, i32* %93, i32 %101
  %103 = load i32, i32* %102, align 4
  %104 = sitofp i32 %103 to float
  %105 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 1
  %106 = load i32*, i32** %105, align 8
  %107 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 0
  %108 = load i32, i32* %107, align 4
  %109 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 1
  %110 = load i32, i32* %109, align 4
  %111 = mul i32 0, %108
  %112 = add i32 %111, %74
  %113 = mul i32 %112, %110
  %114 = add i32 %113, %69
  %115 = getelementptr i32, i32* %106, i32 %114
  %116 = load i32, i32* %115, align 4
  %117 = sitofp i32 %116 to float
  %118 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 1
  %119 = load i32*, i32** %118, align 8
  %120 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 0
  %121 = load i32, i32* %120, align 4
  %122 = getelementptr { { i32, i32 }, i32* }, { { i32, i32 }, i32* }* %78, i32 0, i32 0, i32 1
  %123 = load i32, i32* %122, align 4
  %124 = mul i32 0, %121
  %125 = add i32 %124, %74
  %126 = mul i32 %125, %123
  %127 = add i32 %126, %73
  %128 = getelementptr i32, i32* %119, i32 %127
  %129 = load i32, i32* %128, align 4
  %130 = sitofp i32 %129 to float
  %131 = fsub reassoc ninf nsz float 1.000000e+00, %64
  %132 = fmul reassoc ninf nsz float %91, %131
  %133 = fmul reassoc ninf nsz float %104, %64
  %134 = fadd reassoc ninf nsz float %132, %133
  %135 = fmul reassoc ninf nsz float %117, %131
  %136 = fmul reassoc ninf nsz float %130, %64
  %137 = fadd reassoc ninf nsz float %135, %136
  %138 = fsub reassoc ninf nsz float 1.000000e+00, %66
  %139 = fmul reassoc ninf nsz float %134, %138
  %140 = fmul reassoc ninf nsz float %137, %66
  %141 = fadd reassoc ninf nsz float %139, %140
  %142 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %143 = bitcast i8** %142 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %144 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %143, align 8
  %145 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %144, i32 0, i32 6
  %146 = load float, float* %145, align 4
  %147 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %148 = bitcast i8** %147 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %149 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %148, align 8
  %150 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %149, i32 0, i32 7
  %151 = load i32, i32* %150, align 4
  %152 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %153 = bitcast i8** %152 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %154 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %153, align 8
  %155 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %154, i32 0, i32 8
  %156 = load float, float* %155, align 4
  %157 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %158 = bitcast i8** %157 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %159 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %158, align 8
  %160 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %159, i32 0, i32 9
  %161 = load float, float* %160, align 4
  %162 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %163 = bitcast i8** %162 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %164 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %163, align 8
  %165 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %164, i32 0, i32 10
  %166 = load float, float* %165, align 4
  %167 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %168 = bitcast i8** %167 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %169 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %168, align 8
  %170 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %169, i32 0, i32 11
  %171 = load float, float* %170, align 4
  %172 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %173 = bitcast i8** %172 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %174 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %173, align 8
  %175 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %174, i32 0, i32 12
  %176 = load i32, i32* %175, align 4
  %177 = fdiv reassoc ninf nsz float %141, %146
  store float 0.000000e+00, float* %4, align 4
  store float %177, float* %4, align 4
  %178 = icmp ne i32 %151, 0
  br i1 %178, label %true_block, label %false_block

true_block:                                       ; preds = %function_body
  %179 = fmul reassoc ninf nsz float %177, %156
  %180 = fcmp reassoc ninf nsz olt float %179, %171
  %181 = icmp ne i1 %180, false
  br i1 %181, label %true_block1, label %false_block2

false_block:                                      ; preds = %function_body
  br label %after_if

after_if:                                         ; preds = %after_if3, %false_block
  %182 = icmp ne i32 %176, 0
  br i1 %182, label %true_block4, label %false_block5

true_block1:                                      ; preds = %true_block
  %183 = fmul reassoc ninf nsz float %179, %166
  store float %183, float* %4, align 4
  br label %after_if3

false_block2:                                     ; preds = %true_block
  %184 = fdiv reassoc ninf nsz float 1.000000e+00, %161
  %185 = call reassoc ninf nsz float @__nv_powf(float %179, float %184)
  %186 = fmul reassoc ninf nsz float %185, 0x3FF1958100000000
  %187 = fsub reassoc ninf nsz float %186, 0x3FB9581060000000
  store float %187, float* %4, align 4
  br label %after_if3

after_if3:                                        ; preds = %false_block2, %true_block1
  br label %after_if

true_block4:                                      ; preds = %after_if
  %188 = load float, float* %4, align 4
  %189 = fsub reassoc ninf nsz float %188, 5.000000e-01
  %190 = fmul reassoc ninf nsz float %189, 0x3FE6666660000000
  %191 = fadd reassoc ninf nsz float %190, 5.000000e-01
  store float %191, float* %4, align 4
  br label %after_if6

false_block5:                                     ; preds = %after_if
  br label %after_if6

after_if6:                                        ; preds = %false_block5, %true_block4
  %192 = load float, float* %4, align 4
  %193 = call reassoc ninf nsz float @llvm.maxnum.f32(float 0.000000e+00, float %192)
  %194 = call reassoc ninf nsz float @llvm.minnum.f32(float 1.000000e+00, float %193)
  %195 = getelementptr %struct.RuntimeContext, %struct.RuntimeContext* %0, i32 0, i32 0
  %196 = bitcast i8** %195 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }**
  %197 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }** %196, align 8
  %198 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, i32, float, float, float, float, i32 }* %197, i32 0, i32 1
  %199 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %198, i32 0, i32 1
  %200 = load float*, float** %199, align 8
  %201 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %198, i32 0, i32 0, i32 0
  %202 = load i32, i32* %201, align 4
  %203 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %198, i32 0, i32 0, i32 1
  %204 = load i32, i32* %203, align 4
  %205 = mul i32 0, %202
  %206 = add i32 %205, %24
  %207 = mul i32 %206, %204
  %208 = add i32 %207, %26
  %209 = getelementptr float, float* %200, i32 %208
  store float %194, float* %209, align 4
  br label %final
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #0

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @min_i32(i32 noundef %0, i32 noundef %1) #1 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 %1, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  %5 = load i32, i32* %4, align 4
  %6 = load i32, i32* %3, align 4
  %7 = icmp slt i32 %5, %6
  br i1 %7, label %8, label %10

8:                                                ; preds = %2
  %9 = load i32, i32* %4, align 4
  br label %12

10:                                               ; preds = %2
  %11 = load i32, i32* %3, align 4
  br label %12

12:                                               ; preds = %10, %8
  %13 = phi i32 [ %9, %8 ], [ %11, %10 ]
  ret i32 %13
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @max_i32(i32 noundef %0, i32 noundef %1) #1 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 %1, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  %5 = load i32, i32* %4, align 4
  %6 = load i32, i32* %3, align 4
  %7 = icmp sgt i32 %5, %6
  br i1 %7, label %8, label %10

8:                                                ; preds = %2
  %9 = load i32, i32* %4, align 4
  br label %12

10:                                               ; preds = %2
  %11 = load i32, i32* %3, align 4
  br label %12

12:                                               ; preds = %10, %8
  %13 = phi i32 [ %9, %8 ], [ %11, %10 ]
  ret i32 %13
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal %struct.LLVMRuntime* @RuntimeContext_get_runtime(%struct.RuntimeContext* noundef %0) #1 {
  %2 = alloca %struct.RuntimeContext*, align 8
  store %struct.RuntimeContext* %0, %struct.RuntimeContext** %2, align 8
  %3 = load %struct.RuntimeContext*, %struct.RuntimeContext** %2, align 8
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %3, i32 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  ret %struct.LLVMRuntime* %5
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i8* @get_temporary_pointer(%struct.LLVMRuntime* noundef %0, i64 noundef %1) #1 {
  %3 = alloca i64, align 8
  %4 = alloca %struct.LLVMRuntime*, align 8
  store i64 %1, i64* %3, align 8
  store %struct.LLVMRuntime* %0, %struct.LLVMRuntime** %4, align 8
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i32 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = load i64, i64* %3, align 8
  %9 = getelementptr inbounds i8, i8* %7, i64 %8
  ret i8* %9
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @gpu_parallel_range_for(%struct.RuntimeContext* noundef %0, i32 noundef %1, i32 noundef %2, void (%struct.RuntimeContext*, i8*)* noundef %3, void (%struct.RuntimeContext*, i8*, i32)* noundef %4, void (%struct.RuntimeContext*, i8*)* noundef %5, i64 noundef %6) #1 {
  %8 = alloca i64, align 8
  %9 = alloca void (%struct.RuntimeContext*, i8*)*, align 8
  %10 = alloca void (%struct.RuntimeContext*, i8*, i32)*, align 8
  %11 = alloca void (%struct.RuntimeContext*, i8*)*, align 8
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca %struct.RuntimeContext*, align 8
  %15 = alloca i32, align 4
  %16 = alloca i8*, align 8
  %17 = alloca i64, align 8
  %18 = alloca i8*, align 8
  store i64 %6, i64* %8, align 8
  store void (%struct.RuntimeContext*, i8*)* %5, void (%struct.RuntimeContext*, i8*)** %9, align 8
  store void (%struct.RuntimeContext*, i8*, i32)* %4, void (%struct.RuntimeContext*, i8*, i32)** %10, align 8
  store void (%struct.RuntimeContext*, i8*)* %3, void (%struct.RuntimeContext*, i8*)** %11, align 8
  store i32 %2, i32* %12, align 4
  store i32 %1, i32* %13, align 4
  store %struct.RuntimeContext* %0, %struct.RuntimeContext** %14, align 8
  %19 = call i32 @thread_idx()
  %20 = call i32 @block_dim()
  %21 = call i32 @block_idx()
  %22 = mul nsw i32 %20, %21
  %23 = add nsw i32 %19, %22
  %24 = load i32, i32* %13, align 4
  %25 = add nsw i32 %23, %24
  store i32 %25, i32* %15, align 4
  %26 = load i64, i64* %8, align 8
  %27 = call i8* @llvm.stacksave()
  store i8* %27, i8** %16, align 8
  %28 = alloca i8, i64 %26, align 8
  store i64 %26, i64* %17, align 8
  %29 = getelementptr inbounds i8, i8* %28, i64 0
  store i8* %29, i8** %18, align 8
  %30 = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %11, align 8
  %31 = icmp ne void (%struct.RuntimeContext*, i8*)* %30, null
  br i1 %31, label %32, label %36

32:                                               ; preds = %7
  %33 = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %11, align 8
  %34 = load i8*, i8** %18, align 8
  %35 = load %struct.RuntimeContext*, %struct.RuntimeContext** %14, align 8
  call void %33(%struct.RuntimeContext* noundef %35, i8* noundef %34)
  br label %36

36:                                               ; preds = %32, %7
  br label %37

37:                                               ; preds = %41, %36
  %38 = load i32, i32* %15, align 4
  %39 = load i32, i32* %12, align 4
  %40 = icmp slt i32 %38, %39
  br i1 %40, label %41, label %51

41:                                               ; preds = %37
  %42 = load void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*, i32)** %10, align 8
  %43 = load i32, i32* %15, align 4
  %44 = load i8*, i8** %18, align 8
  %45 = load %struct.RuntimeContext*, %struct.RuntimeContext** %14, align 8
  call void %42(%struct.RuntimeContext* noundef %45, i8* noundef %44, i32 noundef %43)
  %46 = call i32 @block_dim()
  %47 = call i32 @grid_dim()
  %48 = mul nsw i32 %46, %47
  %49 = load i32, i32* %15, align 4
  %50 = add nsw i32 %49, %48
  store i32 %50, i32* %15, align 4
  br label %37, !llvm.loop !20

51:                                               ; preds = %37
  %52 = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %9, align 8
  %53 = icmp ne void (%struct.RuntimeContext*, i8*)* %52, null
  br i1 %53, label %54, label %58

54:                                               ; preds = %51
  %55 = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %9, align 8
  %56 = load i8*, i8** %18, align 8
  %57 = load %struct.RuntimeContext*, %struct.RuntimeContext** %14, align 8
  call void %55(%struct.RuntimeContext* noundef %57, i8* noundef %56)
  br label %58

58:                                               ; preds = %54, %51
  %59 = load i8*, i8** %16, align 8
  call void @llvm.stackrestore(i8* %59)
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @thread_idx() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.tid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_dim() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ntid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_idx() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare i8* @llvm.stacksave() #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @grid_dim() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.nctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare void @llvm.stackrestore(i8*) #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.nctaid.x() #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ctaid.x() #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ntid.x() #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.tid.x() #0

; Function Attrs: alwaysinline inlinehint
define internal float @__nv_powf(float %a, float %b) #3 {
  %x.addr.i.i = alloca %struct.float2, align 8
  %y.addr.i.i = alloca %struct.float2, align 8
  %z.i.i = alloca %struct.float2, align 8
  %res.i.i = alloca %struct.float2, align 8
  %prod.i = alloca %struct.float2, align 8
  %1 = bitcast float %b to i32
  %2 = and i32 %1, 2139095040
  %3 = ashr i32 %2, 23
  %4 = sub nsw i32 %3, 127
  %5 = add nsw i32 %4, 8
  %6 = fmul float 5.000000e-01, %b
  %call.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %7 = icmp ne i32 %call.i, 0
  br i1 %7, label %8, label %10

8:                                                ; preds = %0
  %9 = call float @llvm.nvvm.trunc.ftz.f(float %6)
  br label %__nv_truncf.exit

10:                                               ; preds = %0
  %11 = call float @llvm.nvvm.trunc.f(float %6)
  br label %__nv_truncf.exit

__nv_truncf.exit:                                 ; preds = %10, %8
  %retval.0.i = phi float [ %9, %8 ], [ %11, %10 ]
  %12 = fmul float 2.000000e+00, %retval.0.i
  %13 = fsub float %b, %12
  %call.i1 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %14 = icmp ne i32 %call.i1, 0
  br i1 %14, label %15, label %17

15:                                               ; preds = %__nv_truncf.exit
  %16 = call float @llvm.nvvm.fabs.ftz.f(float %13)
  br label %__nv_fabsf.exit

17:                                               ; preds = %__nv_truncf.exit
  %18 = call float @llvm.nvvm.fabs.f(float %13)
  br label %__nv_fabsf.exit

__nv_fabsf.exit:                                  ; preds = %17, %15
  %retval.0.i2 = phi float [ %16, %15 ], [ %18, %17 ]
  %19 = fcmp oeq float %retval.0.i2, 1.000000e+00
  %20 = zext i1 %19 to i32
  %call.i3 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %21 = icmp ne i32 %call.i3, 0
  br i1 %21, label %22, label %24

22:                                               ; preds = %__nv_fabsf.exit
  %23 = call float @llvm.nvvm.fabs.ftz.f(float %a)
  br label %__nv_fabsf.exit5

24:                                               ; preds = %__nv_fabsf.exit
  %25 = call float @llvm.nvvm.fabs.f(float %a)
  br label %__nv_fabsf.exit5

__nv_fabsf.exit5:                                 ; preds = %24, %22
  %retval.0.i4 = phi float [ %23, %22 ], [ %25, %24 ]
  %26 = bitcast %struct.float2* %prod.i to i8*
  call void @llvm.lifetime.start.p0i8(i64 -1, i8* %26)
  %27 = bitcast %struct.float2* %res.i.i to i8*
  call void @llvm.lifetime.start.p0i8(i64 -1, i8* %27)
  %call.i.i6 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %28 = icmp ne i32 %call.i.i6, 0
  %29 = xor i1 %28, true
  br i1 %29, label %30, label %35

30:                                               ; preds = %__nv_fabsf.exit5
  %31 = fcmp olt float %retval.0.i4, 0x3810000000000000
  br i1 %31, label %32, label %34

32:                                               ; preds = %30
  %33 = fmul float %retval.0.i4, 0x4170000000000000
  br label %34

34:                                               ; preds = %32, %30
  %expo.0.i.i = phi float [ -1.510000e+02, %32 ], [ -1.270000e+02, %30 ]
  %a.addr.0.i.i = phi float [ %33, %32 ], [ %retval.0.i4, %30 ]
  br label %35

35:                                               ; preds = %34, %__nv_fabsf.exit5
  %expo.1.i.i = phi float [ %expo.0.i.i, %34 ], [ -1.270000e+02, %__nv_fabsf.exit5 ]
  %a.addr.1.i.i = phi float [ %a.addr.0.i.i, %34 ], [ %retval.0.i4, %__nv_fabsf.exit5 ]
  %36 = bitcast float %a.addr.1.i.i to i32
  %37 = and i32 %36, 8388607
  %38 = or i32 %37, 1065353216
  %39 = bitcast i32 %38 to float
  %40 = lshr i32 %36, 23
  %41 = uitofp i32 %40 to float
  %42 = fadd float %expo.1.i.i, %41
  %43 = fcmp ogt float %39, 0x3FF6A09E60000000
  br i1 %43, label %44, label %47

44:                                               ; preds = %35
  %45 = fmul float %39, 5.000000e-01
  %46 = fadd float %42, 1.000000e+00
  br label %47

47:                                               ; preds = %44, %35
  %m.0.i.i = phi float [ %45, %44 ], [ %39, %35 ]
  %expo.2.i.i = phi float [ %46, %44 ], [ %42, %35 ]
  %48 = fsub float %m.0.i.i, 1.000000e+00
  %49 = fadd float %m.0.i.i, 1.000000e+00
  %50 = call float asm "rcp.approx.ftz.f32 $0,$1;", "=f,f"(float %49) #7
  %51 = fmul float 2.000000e+00, %48
  %52 = fmul float %51, %50
  %53 = fmul float %52, %52
  %call.i.i.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %54 = icmp ne i32 %call.i.i.i.i, 0
  br i1 %54, label %55, label %57

55:                                               ; preds = %47
  %56 = call float @llvm.nvvm.fma.rn.ftz.f(float 0x3F631E1FC0000000, float %53, float 0x3F8995EC60000000)
  br label %__internal_fmad.exit.i.i

57:                                               ; preds = %47
  %58 = call float @llvm.nvvm.fma.rn.f(float 0x3F631E1FC0000000, float %53, float 0x3F8995EC60000000)
  br label %__internal_fmad.exit.i.i

__internal_fmad.exit.i.i:                         ; preds = %57, %55
  %retval.0.i.i.i.i = phi float [ %56, %55 ], [ %58, %57 ]
  %call.i.i4.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %59 = icmp ne i32 %call.i.i4.i.i, 0
  br i1 %59, label %60, label %62

60:                                               ; preds = %__internal_fmad.exit.i.i
  %61 = call float @llvm.nvvm.fma.rn.ftz.f(float %retval.0.i.i.i.i, float %53, float 0x3FB55557A0000000)
  br label %__internal_fmad.exit6.i.i

62:                                               ; preds = %__internal_fmad.exit.i.i
  %63 = call float @llvm.nvvm.fma.rn.f(float %retval.0.i.i.i.i, float %53, float 0x3FB55557A0000000)
  br label %__internal_fmad.exit6.i.i

__internal_fmad.exit6.i.i:                        ; preds = %62, %60
  %retval.0.i.i5.i.i = phi float [ %61, %60 ], [ %63, %62 ]
  %call.i7.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %64 = icmp ne i32 %call.i7.i.i, 0
  br i1 %64, label %65, label %67

65:                                               ; preds = %__internal_fmad.exit6.i.i
  %66 = call float @llvm.nvvm.mul.rn.ftz.f(float %retval.0.i.i5.i.i, float %53)
  br label %__nv_fmul_rn.exit9.i.i

67:                                               ; preds = %__internal_fmad.exit6.i.i
  %68 = call float @llvm.nvvm.mul.rn.f(float %retval.0.i.i5.i.i, float %53)
  br label %__nv_fmul_rn.exit9.i.i

__nv_fmul_rn.exit9.i.i:                           ; preds = %67, %65
  %retval.0.i8.i.i = phi float [ %66, %65 ], [ %68, %67 ]
  %call.i10.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %69 = icmp ne i32 %call.i10.i.i, 0
  br i1 %69, label %70, label %72

70:                                               ; preds = %__nv_fmul_rn.exit9.i.i
  %71 = call float @llvm.nvvm.mul.rn.ftz.f(float %retval.0.i8.i.i, float %52)
  br label %__nv_fmul_rn.exit12.i.i

72:                                               ; preds = %__nv_fmul_rn.exit9.i.i
  %73 = call float @llvm.nvvm.mul.rn.f(float %retval.0.i8.i.i, float %52)
  br label %__nv_fmul_rn.exit12.i.i

__nv_fmul_rn.exit12.i.i:                          ; preds = %72, %70
  %retval.0.i11.i.i = phi float [ %71, %70 ], [ %73, %72 ]
  %74 = fsub float %48, %52
  %75 = fmul float 2.000000e+00, %74
  %76 = fsub float -0.000000e+00, %52
  %call.i13.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %77 = icmp ne i32 %call.i13.i.i, 0
  br i1 %77, label %78, label %80

78:                                               ; preds = %__nv_fmul_rn.exit12.i.i
  %79 = call float @llvm.nvvm.fma.rn.ftz.f(float %76, float %48, float %75)
  br label %__nv_fmaf_rn.exit.i.i

80:                                               ; preds = %__nv_fmul_rn.exit12.i.i
  %81 = call float @llvm.nvvm.fma.rn.f(float %76, float %48, float %75)
  br label %__nv_fmaf_rn.exit.i.i

__nv_fmaf_rn.exit.i.i:                            ; preds = %80, %78
  %retval.0.i14.i.i = phi float [ %79, %78 ], [ %81, %80 ]
  %call.i15.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %82 = icmp ne i32 %call.i15.i.i, 0
  br i1 %82, label %83, label %85

83:                                               ; preds = %__nv_fmaf_rn.exit.i.i
  %84 = call float @llvm.nvvm.mul.rn.ftz.f(float %50, float %retval.0.i14.i.i)
  br label %__nv_fmul_rn.exit17.i.i

85:                                               ; preds = %__nv_fmaf_rn.exit.i.i
  %86 = call float @llvm.nvvm.mul.rn.f(float %50, float %retval.0.i14.i.i)
  br label %__nv_fmul_rn.exit17.i.i

__nv_fmul_rn.exit17.i.i:                          ; preds = %85, %83
  %retval.0.i16.i.i = phi float [ %84, %83 ], [ %86, %85 ]
  %87 = fadd float %52, %retval.0.i11.i.i
  %88 = fsub float %52, %87
  %89 = fadd float %88, %retval.0.i11.i.i
  %90 = fadd float %89, %retval.0.i16.i.i
  %91 = fadd float %87, %90
  %92 = fsub float %87, %91
  %93 = fadd float %92, %90
  %call.i1.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %94 = icmp ne i32 %call.i1.i.i, 0
  br i1 %94, label %95, label %97

95:                                               ; preds = %__nv_fmul_rn.exit17.i.i
  %96 = call float @llvm.nvvm.mul.rn.ftz.f(float %expo.2.i.i, float 0x3FE62E4000000000)
  br label %__nv_fmul_rn.exit3.i.i

97:                                               ; preds = %__nv_fmul_rn.exit17.i.i
  %98 = call float @llvm.nvvm.mul.rn.f(float %expo.2.i.i, float 0x3FE62E4000000000)
  br label %__nv_fmul_rn.exit3.i.i

__nv_fmul_rn.exit3.i.i:                           ; preds = %97, %95
  %retval.0.i2.i.i = phi float [ %96, %95 ], [ %98, %97 ]
  %call.i.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %99 = icmp ne i32 %call.i.i.i, 0
  br i1 %99, label %100, label %102

100:                                              ; preds = %__nv_fmul_rn.exit3.i.i
  %101 = call float @llvm.nvvm.mul.rn.ftz.f(float %expo.2.i.i, float 0x3EB7F7D1C0000000)
  br label %__internal_log_ep.exit.i

102:                                              ; preds = %__nv_fmul_rn.exit3.i.i
  %103 = call float @llvm.nvvm.mul.rn.f(float %expo.2.i.i, float 0x3EB7F7D1C0000000)
  br label %__internal_log_ep.exit.i

__internal_log_ep.exit.i:                         ; preds = %102, %100
  %retval.0.i.i.i = phi float [ %101, %100 ], [ %103, %102 ]
  %104 = fadd float %retval.0.i2.i.i, %91
  %105 = fsub float %retval.0.i2.i.i, %104
  %106 = fadd float %105, %91
  %107 = fadd float %106, %93
  %108 = fadd float %107, %retval.0.i.i.i
  %109 = fadd float %104, %108
  %110 = getelementptr inbounds %struct.float2, %struct.float2* %res.i.i, i32 0, i32 1
  store float %109, float* %110, align 4
  %111 = fsub float %104, %109
  %112 = fadd float %111, %108
  %113 = getelementptr inbounds %struct.float2, %struct.float2* %res.i.i, i32 0, i32 0
  store float %112, float* %113, align 8
  %114 = load %struct.float2, %struct.float2* %res.i.i, align 8
  %115 = bitcast %struct.float2* %res.i.i to i8*
  call void @llvm.lifetime.end.p0i8(i64 -1, i8* %115)
  %call.i1.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %116 = icmp ne i32 %call.i1.i, 0
  br i1 %116, label %117, label %119

117:                                              ; preds = %__internal_log_ep.exit.i
  %118 = call float @llvm.nvvm.fabs.ftz.f(float %b)
  br label %__nv_fabsf.exit.i

119:                                              ; preds = %__internal_log_ep.exit.i
  %120 = call float @llvm.nvvm.fabs.f(float %b)
  br label %__nv_fabsf.exit.i

__nv_fabsf.exit.i:                                ; preds = %119, %117
  %retval.0.i.i7 = phi float [ %118, %117 ], [ %120, %119 ]
  %121 = fcmp ogt float %retval.0.i.i7, 0x46FED09BE0000000
  br i1 %121, label %122, label %124

122:                                              ; preds = %__nv_fabsf.exit.i
  %123 = fmul float %b, 0x3F20000000000000
  br label %124

124:                                              ; preds = %122, %__nv_fabsf.exit.i
  %b.addr.0.i = phi float [ %123, %122 ], [ %b, %__nv_fabsf.exit.i ]
  %125 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 1
  store float %b.addr.0.i, float* %125, align 4
  %126 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 0
  store float 0.000000e+00, float* %126, align 8
  %127 = load %struct.float2, %struct.float2* %prod.i, align 8
  %128 = bitcast %struct.float2* %x.addr.i.i to i8*
  call void @llvm.lifetime.start.p0i8(i64 -1, i8* %128)
  %129 = bitcast %struct.float2* %y.addr.i.i to i8*
  call void @llvm.lifetime.start.p0i8(i64 -1, i8* %129)
  %130 = bitcast %struct.float2* %z.i.i to i8*
  call void @llvm.lifetime.start.p0i8(i64 -1, i8* %130)
  store %struct.float2 %127, %struct.float2* %x.addr.i.i, align 8
  store %struct.float2 %114, %struct.float2* %y.addr.i.i, align 8
  %131 = getelementptr inbounds %struct.float2, %struct.float2* %x.addr.i.i, i32 0, i32 1
  %132 = load float, float* %131, align 4
  %133 = getelementptr inbounds %struct.float2, %struct.float2* %y.addr.i.i, i32 0, i32 1
  %134 = load float, float* %133, align 4
  %call.i.i2.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %135 = icmp ne i32 %call.i.i2.i, 0
  br i1 %135, label %136, label %138

136:                                              ; preds = %124
  %137 = call float @llvm.nvvm.mul.rn.ftz.f(float %132, float %134)
  br label %__nv_fmul_rn.exit.i.i

138:                                              ; preds = %124
  %139 = call float @llvm.nvvm.mul.rn.f(float %132, float %134)
  br label %__nv_fmul_rn.exit.i.i

__nv_fmul_rn.exit.i.i:                            ; preds = %138, %136
  %retval.0.i.i3.i = phi float [ %137, %136 ], [ %139, %138 ]
  %140 = getelementptr inbounds %struct.float2, %struct.float2* %x.addr.i.i, i32 0, i32 1
  %141 = load float, float* %140, align 4
  %142 = getelementptr inbounds %struct.float2, %struct.float2* %y.addr.i.i, i32 0, i32 1
  %143 = load float, float* %142, align 4
  %144 = fsub float -0.000000e+00, %retval.0.i.i3.i
  %call.i1.i4.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %145 = icmp ne i32 %call.i1.i4.i, 0
  br i1 %145, label %146, label %148

146:                                              ; preds = %__nv_fmul_rn.exit.i.i
  %147 = call float @llvm.nvvm.fma.rn.ftz.f(float %141, float %143, float %144)
  br label %__nv_fmaf_rn.exit.i6.i

148:                                              ; preds = %__nv_fmul_rn.exit.i.i
  %149 = call float @llvm.nvvm.fma.rn.f(float %141, float %143, float %144)
  br label %__nv_fmaf_rn.exit.i6.i

__nv_fmaf_rn.exit.i6.i:                           ; preds = %148, %146
  %retval.0.i2.i5.i = phi float [ %147, %146 ], [ %149, %148 ]
  %150 = getelementptr inbounds %struct.float2, %struct.float2* %x.addr.i.i, i32 0, i32 1
  %151 = load float, float* %150, align 4
  %152 = getelementptr inbounds %struct.float2, %struct.float2* %y.addr.i.i, i32 0, i32 0
  %153 = load float, float* %152, align 8
  %call.i3.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %154 = icmp ne i32 %call.i3.i.i, 0
  br i1 %154, label %155, label %157

155:                                              ; preds = %__nv_fmaf_rn.exit.i6.i
  %156 = call float @llvm.nvvm.fma.rn.ftz.f(float %151, float %153, float %retval.0.i2.i5.i)
  br label %__nv_fmaf_rn.exit5.i.i

157:                                              ; preds = %__nv_fmaf_rn.exit.i6.i
  %158 = call float @llvm.nvvm.fma.rn.f(float %151, float %153, float %retval.0.i2.i5.i)
  br label %__nv_fmaf_rn.exit5.i.i

__nv_fmaf_rn.exit5.i.i:                           ; preds = %157, %155
  %retval.0.i4.i.i = phi float [ %156, %155 ], [ %158, %157 ]
  %159 = getelementptr inbounds %struct.float2, %struct.float2* %x.addr.i.i, i32 0, i32 0
  %160 = load float, float* %159, align 8
  %161 = getelementptr inbounds %struct.float2, %struct.float2* %y.addr.i.i, i32 0, i32 1
  %162 = load float, float* %161, align 4
  %call.i6.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %163 = icmp ne i32 %call.i6.i.i, 0
  br i1 %163, label %164, label %166

164:                                              ; preds = %__nv_fmaf_rn.exit5.i.i
  %165 = call float @llvm.nvvm.fma.rn.ftz.f(float %160, float %162, float %retval.0.i4.i.i)
  br label %__nv_fmaf_rn.exit8.i.i

166:                                              ; preds = %__nv_fmaf_rn.exit5.i.i
  %167 = call float @llvm.nvvm.fma.rn.f(float %160, float %162, float %retval.0.i4.i.i)
  br label %__nv_fmaf_rn.exit8.i.i

__nv_fmaf_rn.exit8.i.i:                           ; preds = %166, %164
  %retval.0.i7.i.i = phi float [ %165, %164 ], [ %167, %166 ]
  %call.i9.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %168 = icmp ne i32 %call.i9.i.i, 0
  br i1 %168, label %169, label %171

169:                                              ; preds = %__nv_fmaf_rn.exit8.i.i
  %170 = call float @llvm.nvvm.add.rn.ftz.f(float %retval.0.i.i3.i, float %retval.0.i7.i.i)
  br label %__nv_fadd_rn.exit.i.i

171:                                              ; preds = %__nv_fmaf_rn.exit8.i.i
  %172 = call float @llvm.nvvm.add.rn.f(float %retval.0.i.i3.i, float %retval.0.i7.i.i)
  br label %__nv_fadd_rn.exit.i.i

__nv_fadd_rn.exit.i.i:                            ; preds = %171, %169
  %retval.0.i10.i.i = phi float [ %170, %169 ], [ %172, %171 ]
  %173 = getelementptr inbounds %struct.float2, %struct.float2* %z.i.i, i32 0, i32 1
  store float %retval.0.i10.i.i, float* %173, align 4
  %174 = fsub float -0.000000e+00, %retval.0.i10.i.i
  %call.i11.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %175 = icmp ne i32 %call.i11.i.i, 0
  br i1 %175, label %176, label %178

176:                                              ; preds = %__nv_fadd_rn.exit.i.i
  %177 = call float @llvm.nvvm.add.rn.ftz.f(float %retval.0.i.i3.i, float %174)
  br label %__nv_fadd_rn.exit13.i.i

178:                                              ; preds = %__nv_fadd_rn.exit.i.i
  %179 = call float @llvm.nvvm.add.rn.f(float %retval.0.i.i3.i, float %174)
  br label %__nv_fadd_rn.exit13.i.i

__nv_fadd_rn.exit13.i.i:                          ; preds = %178, %176
  %retval.0.i12.i.i = phi float [ %177, %176 ], [ %179, %178 ]
  %call.i14.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %180 = icmp ne i32 %call.i14.i.i, 0
  br i1 %180, label %181, label %183

181:                                              ; preds = %__nv_fadd_rn.exit13.i.i
  %182 = call float @llvm.nvvm.add.rn.ftz.f(float %retval.0.i12.i.i, float %retval.0.i7.i.i)
  br label %__internal_dsmul.exit.i

183:                                              ; preds = %__nv_fadd_rn.exit13.i.i
  %184 = call float @llvm.nvvm.add.rn.f(float %retval.0.i12.i.i, float %retval.0.i7.i.i)
  br label %__internal_dsmul.exit.i

__internal_dsmul.exit.i:                          ; preds = %183, %181
  %retval.0.i15.i.i = phi float [ %182, %181 ], [ %184, %183 ]
  %185 = getelementptr inbounds %struct.float2, %struct.float2* %z.i.i, i32 0, i32 0
  store float %retval.0.i15.i.i, float* %185, align 8
  %186 = load %struct.float2, %struct.float2* %z.i.i, align 8
  %187 = bitcast %struct.float2* %x.addr.i.i to i8*
  call void @llvm.lifetime.end.p0i8(i64 -1, i8* %187)
  %188 = bitcast %struct.float2* %y.addr.i.i to i8*
  call void @llvm.lifetime.end.p0i8(i64 -1, i8* %188)
  %189 = bitcast %struct.float2* %z.i.i to i8*
  call void @llvm.lifetime.end.p0i8(i64 -1, i8* %189)
  store %struct.float2 %186, %struct.float2* %prod.i, align 8
  %190 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 1
  %191 = load float, float* %190, align 4
  %192 = bitcast float %191 to i32
  %193 = icmp eq i32 %192, 1118925336
  br i1 %193, label %194, label %205

194:                                              ; preds = %__internal_dsmul.exit.i
  %195 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 1
  %196 = load float, float* %195, align 4
  %197 = bitcast float %196 to i32
  %198 = sub nsw i32 %197, 1
  %199 = bitcast i32 %198 to float
  %200 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 1
  store float %199, float* %200, align 4
  %201 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 0
  %202 = load float, float* %201, align 8
  %203 = fadd float %202, 0x3EE0000000000000
  %204 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 0
  store float %203, float* %204, align 8
  br label %205

205:                                              ; preds = %194, %__internal_dsmul.exit.i
  %206 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 1
  %207 = load float, float* %206, align 4
  %208 = fmul float %207, 0x3FF7154760000000
  %call.i.i.i.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %209 = icmp ne i32 %call.i.i.i.i.i, 0
  br i1 %209, label %210, label %212

210:                                              ; preds = %205
  %211 = call float @llvm.nvvm.trunc.ftz.f(float %208)
  br label %__nv_truncf.exit.i.i.i.i

212:                                              ; preds = %205
  %213 = call float @llvm.nvvm.trunc.f(float %208)
  br label %__nv_truncf.exit.i.i.i.i

__nv_truncf.exit.i.i.i.i:                         ; preds = %212, %210
  %retval.0.i.i.i.i.i = phi float [ %211, %210 ], [ %213, %212 ]
  %call.i.i.i.i.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %214 = icmp ne i32 %call.i.i.i.i.i.i, 0
  br i1 %214, label %215, label %217

215:                                              ; preds = %__nv_truncf.exit.i.i.i.i
  %216 = call float @llvm.nvvm.fma.rn.ftz.f(float %retval.0.i.i.i.i.i, float 0xBFE62E4000000000, float %207)
  br label %__internal_fmad.exit.i.i.i.i

217:                                              ; preds = %__nv_truncf.exit.i.i.i.i
  %218 = call float @llvm.nvvm.fma.rn.f(float %retval.0.i.i.i.i.i, float 0xBFE62E4000000000, float %207)
  br label %__internal_fmad.exit.i.i.i.i

__internal_fmad.exit.i.i.i.i:                     ; preds = %217, %215
  %retval.0.i.i.i.i.i.i = phi float [ %216, %215 ], [ %218, %217 ]
  %call.i.i1.i.i.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %219 = icmp ne i32 %call.i.i1.i.i.i.i, 0
  br i1 %219, label %220, label %222

220:                                              ; preds = %__internal_fmad.exit.i.i.i.i
  %221 = call float @llvm.nvvm.fma.rn.ftz.f(float %retval.0.i.i.i.i.i, float 0xBEB7F7D1C0000000, float %retval.0.i.i.i.i.i.i)
  br label %__internal_expf_arg_reduction.exit.i.i.i

222:                                              ; preds = %__internal_fmad.exit.i.i.i.i
  %223 = call float @llvm.nvvm.fma.rn.f(float %retval.0.i.i.i.i.i, float 0xBEB7F7D1C0000000, float %retval.0.i.i.i.i.i.i)
  br label %__internal_expf_arg_reduction.exit.i.i.i

__internal_expf_arg_reduction.exit.i.i.i:         ; preds = %222, %220
  %retval.0.i.i2.i.i.i.i = phi float [ %221, %220 ], [ %223, %222 ]
  %224 = fmul float %retval.0.i.i2.i.i.i.i, 0x3FF7154760000000
  %225 = call float @llvm.nvvm.ex2.approx.ftz.f(float %224)
  %226 = fadd float %retval.0.i.i.i.i.i, 0.000000e+00
  %call.i.i1.i.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %227 = icmp ne i32 %call.i.i1.i.i.i, 0
  br i1 %227, label %228, label %230

228:                                              ; preds = %__internal_expf_arg_reduction.exit.i.i.i
  %229 = call float @llvm.nvvm.ex2.approx.ftz.f(float %226)
  br label %__internal_expf_kernel.exit.i.i

230:                                              ; preds = %__internal_expf_arg_reduction.exit.i.i.i
  %231 = call float @llvm.nvvm.ex2.approx.f(float %226)
  br label %__internal_expf_kernel.exit.i.i

__internal_expf_kernel.exit.i.i:                  ; preds = %230, %228
  %retval.0.i.i2.i.i.i = phi float [ %229, %228 ], [ %231, %230 ]
  %232 = fmul float %225, %retval.0.i.i2.i.i.i
  %233 = fcmp olt float %207, -1.050000e+02
  br i1 %233, label %234, label %235

234:                                              ; preds = %__internal_expf_kernel.exit.i.i
  br label %235

235:                                              ; preds = %234, %__internal_expf_kernel.exit.i.i
  %z.0.i.i = phi float [ 0.000000e+00, %234 ], [ %232, %__internal_expf_kernel.exit.i.i ]
  %236 = fcmp ogt float %207, 1.050000e+02
  br i1 %236, label %237, label %__internal_accurate_expf.exit.i

237:                                              ; preds = %235
  %238 = bitcast i32 2139095040 to float
  br label %__internal_accurate_expf.exit.i

__internal_accurate_expf.exit.i:                  ; preds = %237, %235
  %z.1.i.i = phi float [ %238, %237 ], [ %z.0.i.i, %235 ]
  %239 = bitcast i32 2139095040 to float
  %240 = fcmp une float %z.1.i.i, %239
  br i1 %240, label %241, label %__internal_accurate_powf.exit

241:                                              ; preds = %__internal_accurate_expf.exit.i
  %242 = getelementptr inbounds %struct.float2, %struct.float2* %prod.i, i32 0, i32 0
  %243 = load float, float* %242, align 8
  %call.i.i7.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %244 = icmp ne i32 %call.i.i7.i, 0
  br i1 %244, label %245, label %247

245:                                              ; preds = %241
  %246 = call float @llvm.nvvm.fma.rn.ftz.f(float %z.1.i.i, float %243, float %z.1.i.i)
  br label %__internal_fmad.exit.i

247:                                              ; preds = %241
  %248 = call float @llvm.nvvm.fma.rn.f(float %z.1.i.i, float %243, float %z.1.i.i)
  br label %__internal_fmad.exit.i

__internal_fmad.exit.i:                           ; preds = %247, %245
  %retval.0.i.i8.i = phi float [ %246, %245 ], [ %248, %247 ]
  br label %__internal_accurate_powf.exit

__internal_accurate_powf.exit:                    ; preds = %__internal_fmad.exit.i, %__internal_accurate_expf.exit.i
  %t.0.i = phi float [ %retval.0.i.i8.i, %__internal_fmad.exit.i ], [ %z.1.i.i, %__internal_accurate_expf.exit.i ]
  %249 = bitcast %struct.float2* %prod.i to i8*
  call void @llvm.lifetime.end.p0i8(i64 -1, i8* %249)
  %250 = fcmp olt float %a, 0.000000e+00
  br i1 %250, label %251, label %253

251:                                              ; preds = %__internal_accurate_powf.exit
  %252 = icmp ne i32 %20, 0
  br label %253

253:                                              ; preds = %251, %__internal_accurate_powf.exit
  %254 = phi i1 [ false, %__internal_accurate_powf.exit ], [ %252, %251 ]
  br i1 %254, label %255, label %259

255:                                              ; preds = %253
  %256 = bitcast float %t.0.i to i32
  %257 = xor i32 %256, -2147483648
  %258 = bitcast i32 %257 to float
  br label %259

259:                                              ; preds = %255, %253
  %t.0 = phi float [ %258, %255 ], [ %t.0.i, %253 ]
  %260 = fcmp oeq float %a, 0.000000e+00
  br i1 %260, label %261, label %272

261:                                              ; preds = %259
  %262 = icmp ne i32 %20, 0
  br i1 %262, label %263, label %266

263:                                              ; preds = %261
  %264 = fadd float %a, %a
  %265 = bitcast float %264 to i32
  br label %266

266:                                              ; preds = %263, %261
  %ti.0 = phi i32 [ %265, %263 ], [ 0, %261 ]
  %267 = fcmp olt float %b, 0.000000e+00
  br i1 %267, label %268, label %270

268:                                              ; preds = %266
  %269 = or i32 %ti.0, 2139095040
  br label %270

270:                                              ; preds = %268, %266
  %ti.1 = phi i32 [ %269, %268 ], [ %ti.0, %266 ]
  %271 = bitcast i32 %ti.1 to float
  br label %286

272:                                              ; preds = %259
  %273 = fcmp olt float %a, 0.000000e+00
  br i1 %273, label %274, label %281

274:                                              ; preds = %272
  %call.i8 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %275 = icmp ne i32 %call.i8, 0
  br i1 %275, label %276, label %278

276:                                              ; preds = %274
  %277 = call float @llvm.nvvm.trunc.ftz.f(float %b)
  br label %__nv_truncf.exit10

278:                                              ; preds = %274
  %279 = call float @llvm.nvvm.trunc.f(float %b)
  br label %__nv_truncf.exit10

__nv_truncf.exit10:                               ; preds = %278, %276
  %retval.0.i9 = phi float [ %277, %276 ], [ %279, %278 ]
  %280 = fcmp une float %b, %retval.0.i9
  br label %281

281:                                              ; preds = %__nv_truncf.exit10, %272
  %282 = phi i1 [ false, %272 ], [ %280, %__nv_truncf.exit10 ]
  br i1 %282, label %283, label %285

283:                                              ; preds = %281
  %284 = bitcast i32 2147483647 to float
  br label %285

285:                                              ; preds = %283, %281
  %t.1 = phi float [ %284, %283 ], [ %t.0, %281 ]
  br label %286

286:                                              ; preds = %285, %270
  %t.2 = phi float [ %271, %270 ], [ %t.1, %285 ]
  %call.i11 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %287 = icmp ne i32 %call.i11, 0
  br i1 %287, label %288, label %290

288:                                              ; preds = %286
  %289 = call float @llvm.nvvm.fabs.ftz.f(float %a)
  br label %__nv_fabsf.exit13

290:                                              ; preds = %286
  %291 = call float @llvm.nvvm.fabs.f(float %a)
  br label %__nv_fabsf.exit13

__nv_fabsf.exit13:                                ; preds = %290, %288
  %retval.0.i12 = phi float [ %289, %288 ], [ %291, %290 ]
  %call.i14 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %292 = icmp ne i32 %call.i14, 0
  br i1 %292, label %293, label %295

293:                                              ; preds = %__nv_fabsf.exit13
  %294 = call float @llvm.nvvm.fabs.ftz.f(float %b)
  br label %__nv_fabsf.exit16

295:                                              ; preds = %__nv_fabsf.exit13
  %296 = call float @llvm.nvvm.fabs.f(float %b)
  br label %__nv_fabsf.exit16

__nv_fabsf.exit16:                                ; preds = %295, %293
  %retval.0.i15 = phi float [ %294, %293 ], [ %296, %295 ]
  %297 = fadd float %retval.0.i12, %retval.0.i15
  %298 = bitcast float %297 to i32
  %299 = bitcast i32 2139095040 to float
  %300 = bitcast float %299 to i32
  %301 = icmp sge i32 %298, %300
  br i1 %301, label %302, label %381

302:                                              ; preds = %__nv_fabsf.exit16
  %call.i.i17 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %303 = icmp ne i32 %call.i.i17, 0
  br i1 %303, label %304, label %306

304:                                              ; preds = %302
  %305 = call float @llvm.nvvm.fabs.ftz.f(float %a)
  br label %__nv_isnanf.exit

306:                                              ; preds = %302
  %307 = call float @llvm.nvvm.fabs.f(float %a)
  br label %__nv_isnanf.exit

__nv_isnanf.exit:                                 ; preds = %306, %304
  %retval.0.i.i18 = phi float [ %305, %304 ], [ %307, %306 ]
  %308 = bitcast i32 2139095040 to float
  %309 = fcmp ole float %retval.0.i.i18, %308
  %310 = xor i1 %309, true
  %311 = zext i1 %310 to i32
  %312 = icmp ne i32 %311, 0
  br i1 %312, label %324, label %313

313:                                              ; preds = %__nv_isnanf.exit
  %call.i.i20 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %314 = icmp ne i32 %call.i.i20, 0
  br i1 %314, label %315, label %317

315:                                              ; preds = %313
  %316 = call float @llvm.nvvm.fabs.ftz.f(float %b)
  br label %__nv_isnanf.exit23

317:                                              ; preds = %313
  %318 = call float @llvm.nvvm.fabs.f(float %b)
  br label %__nv_isnanf.exit23

__nv_isnanf.exit23:                               ; preds = %317, %315
  %retval.0.i.i21 = phi float [ %316, %315 ], [ %318, %317 ]
  %319 = bitcast i32 2139095040 to float
  %320 = fcmp ole float %retval.0.i.i21, %319
  %321 = xor i1 %320, true
  %322 = zext i1 %321 to i32
  %323 = icmp ne i32 %322, 0
  br label %324

324:                                              ; preds = %__nv_isnanf.exit23, %__nv_isnanf.exit
  %325 = phi i1 [ true, %__nv_isnanf.exit ], [ %323, %__nv_isnanf.exit23 ]
  br i1 %325, label %326, label %328

326:                                              ; preds = %324
  %327 = fadd float %a, %b
  br label %380

328:                                              ; preds = %324
  %call.i.i24 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %329 = icmp ne i32 %call.i.i24, 0
  br i1 %329, label %330, label %332

330:                                              ; preds = %328
  %331 = call float @llvm.nvvm.fabs.ftz.f(float %b)
  br label %__nv_isinff.exit27

332:                                              ; preds = %328
  %333 = call float @llvm.nvvm.fabs.f(float %b)
  br label %__nv_isinff.exit27

__nv_isinff.exit27:                               ; preds = %332, %330
  %retval.0.i.i25 = phi float [ %331, %330 ], [ %333, %332 ]
  %334 = bitcast i32 2139095040 to float
  %335 = fcmp oeq float %retval.0.i.i25, %334
  %336 = zext i1 %335 to i32
  %337 = icmp ne i32 %336, 0
  br i1 %337, label %338, label %355

338:                                              ; preds = %__nv_isinff.exit27
  %call.i28 = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %339 = icmp ne i32 %call.i28, 0
  br i1 %339, label %340, label %342

340:                                              ; preds = %338
  %341 = call float @llvm.nvvm.fabs.ftz.f(float %a)
  br label %__nv_fabsf.exit30

342:                                              ; preds = %338
  %343 = call float @llvm.nvvm.fabs.f(float %a)
  br label %__nv_fabsf.exit30

__nv_fabsf.exit30:                                ; preds = %342, %340
  %retval.0.i29 = phi float [ %341, %340 ], [ %343, %342 ]
  %344 = fcmp ogt float %retval.0.i29, 1.000000e+00
  br i1 %344, label %345, label %346

345:                                              ; preds = %__nv_fabsf.exit30
  br label %346

346:                                              ; preds = %345, %__nv_fabsf.exit30
  %ti.2 = phi i32 [ 2139095040, %345 ], [ 0, %__nv_fabsf.exit30 ]
  %347 = fcmp olt float %b, 0.000000e+00
  br i1 %347, label %348, label %350

348:                                              ; preds = %346
  %349 = xor i32 %ti.2, 2139095040
  br label %350

350:                                              ; preds = %348, %346
  %ti.3 = phi i32 [ %349, %348 ], [ %ti.2, %346 ]
  %351 = fcmp oeq float %a, -1.000000e+00
  br i1 %351, label %352, label %353

352:                                              ; preds = %350
  br label %353

353:                                              ; preds = %352, %350
  %ti.4 = phi i32 [ 1065353216, %352 ], [ %ti.3, %350 ]
  %354 = bitcast i32 %ti.4 to float
  br label %379

355:                                              ; preds = %__nv_isinff.exit27
  %call.i.i = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %356 = icmp ne i32 %call.i.i, 0
  br i1 %356, label %357, label %359

357:                                              ; preds = %355
  %358 = call float @llvm.nvvm.fabs.ftz.f(float %a)
  br label %__nv_isinff.exit

359:                                              ; preds = %355
  %360 = call float @llvm.nvvm.fabs.f(float %a)
  br label %__nv_isinff.exit

__nv_isinff.exit:                                 ; preds = %359, %357
  %retval.0.i.i = phi float [ %358, %357 ], [ %360, %359 ]
  %361 = bitcast i32 2139095040 to float
  %362 = fcmp oeq float %retval.0.i.i, %361
  %363 = zext i1 %362 to i32
  %364 = icmp ne i32 %363, 0
  br i1 %364, label %365, label %378

365:                                              ; preds = %__nv_isinff.exit
  %366 = fcmp oge float %b, 0.000000e+00
  br i1 %366, label %367, label %368

367:                                              ; preds = %365
  br label %368

368:                                              ; preds = %367, %365
  %ti.5 = phi i32 [ 2139095040, %367 ], [ 0, %365 ]
  %369 = fcmp olt float %a, 0.000000e+00
  br i1 %369, label %370, label %372

370:                                              ; preds = %368
  %371 = icmp ne i32 %20, 0
  br label %372

372:                                              ; preds = %370, %368
  %373 = phi i1 [ false, %368 ], [ %371, %370 ]
  br i1 %373, label %374, label %376

374:                                              ; preds = %372
  %375 = xor i32 %ti.5, -2147483648
  br label %376

376:                                              ; preds = %374, %372
  %ti.6 = phi i32 [ %375, %374 ], [ %ti.5, %372 ]
  %377 = bitcast i32 %ti.6 to float
  br label %378

378:                                              ; preds = %376, %__nv_isinff.exit
  %t.3 = phi float [ %377, %376 ], [ %t.2, %__nv_isinff.exit ]
  br label %379

379:                                              ; preds = %378, %353
  %t.4 = phi float [ %354, %353 ], [ %t.3, %378 ]
  br label %380

380:                                              ; preds = %379, %326
  %t.5 = phi float [ %327, %326 ], [ %t.4, %379 ]
  br label %381

381:                                              ; preds = %380, %__nv_fabsf.exit16
  %t.6 = phi float [ %t.5, %380 ], [ %t.2, %__nv_fabsf.exit16 ]
  %382 = fcmp oeq float %a, 1.000000e+00
  br i1 %382, label %385, label %383

383:                                              ; preds = %381
  %384 = fcmp oeq float %b, 0.000000e+00
  br label %385

385:                                              ; preds = %383, %381
  %386 = phi i1 [ true, %381 ], [ %384, %383 ]
  br i1 %386, label %387, label %388

387:                                              ; preds = %385
  br label %388

388:                                              ; preds = %387, %385
  %t.7 = phi float [ 1.000000e+00, %387 ], [ %t.6, %385 ]
  ret float %t.7
}

; Function Attrs: alwaysinline
declare i32 @__nvvm_reflect(i8*) #4

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.trunc.ftz.f(float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.trunc.f(float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.fabs.ftz.f(float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.fabs.f(float) #0

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.fma.rn.ftz.f(float, float, float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.fma.rn.f(float, float, float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.mul.rn.ftz.f(float, float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.mul.rn.f(float, float) #0

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.add.rn.ftz.f(float, float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.add.rn.f(float, float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.nvvm.ex2.approx.ftz.f(float) #6

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.nvvm.ex2.approx.f(float) #6

attributes #0 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #1 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { nocallback nofree nosync nounwind willreturn }
attributes #3 = { alwaysinline inlinehint }
attributes #4 = { alwaysinline }
attributes #5 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #6 = { nocallback nofree nosync nounwind readnone willreturn }
attributes #7 = { nounwind }

!nvvm.annotations = !{!0, !1, !2, !3, !4, !5, !6, !7, !6, !8, !8, !8, !8, !9, !9, !8}
!llvm.linker.options = !{!10, !11, !12, !13, !14}
!llvm.ident = !{!15}
!nvvmir.version = !{!16}
!llvm.module.flags = !{!17, !18, !19}

!0 = !{void (%struct.RuntimeContext*)* @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_0_serial, !"kernel", i32 1}
!1 = !{void (%struct.RuntimeContext*)* @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_0_serial, !"maxntidx", i32 1}
!2 = !{void (%struct.RuntimeContext*)* @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_0_serial, !"minctasm", i32 2}
!3 = !{void (%struct.RuntimeContext*)* @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_1_range_for, !"kernel", i32 1}
!4 = !{void (%struct.RuntimeContext*)* @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_1_range_for, !"maxntidx", i32 128}
!5 = !{void (%struct.RuntimeContext*)* @_fused_full_pipeline_i32_2d_aot_c200_0_kernel_1_range_for, !"minctasm", i32 2}
!6 = !{null, !"align", i32 8}
!7 = !{null, !"align", i32 8, !"align", i32 65544, !"align", i32 131080}
!8 = !{null, !"align", i32 16}
!9 = !{null, !"align", i32 16, !"align", i32 65552, !"align", i32 131088}
!10 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!11 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!12 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!13 = !{!"/DEFAULTLIB:libcpmt.lib"}
!14 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!15 = !{!"clang version 14.0.6"}
!16 = !{i32 1, i32 4}
!17 = !{i32 1, !"wchar_size", i32 2}
!18 = !{i32 7, !"PIC Level", i32 2}
!19 = !{i32 7, !"uwtable", i32 1}
!20 = distinct !{!20, !21}
!21 = !{!"llvm.loop.mustprogress"}
