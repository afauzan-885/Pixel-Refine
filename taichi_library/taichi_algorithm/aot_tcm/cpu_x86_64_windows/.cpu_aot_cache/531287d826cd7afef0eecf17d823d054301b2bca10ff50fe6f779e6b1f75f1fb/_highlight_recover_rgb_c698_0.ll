; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { i8*, %struct.LLVMRuntime.5*, i32, i64* }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.2*], [1024 x %struct.NodeManager.3*], [1024 x i8*], i8*, %struct.RandState.4*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { i8*, i8*, i64 }
%struct.ListManager.2 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.5* }
%struct.NodeManager.3 = type { %struct.LLVMRuntime.5*, i32, i32, i32, i32, %struct.ListManager.2*, %struct.ListManager.2*, %struct.ListManager.2*, i32 }
%struct.RandState.4 = type { i32, i32, i32, i32, i32 }
%struct.range_task_helper_context = type { %struct.RuntimeContext.6*, void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*)*, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_highlight_recover_rgb_c698_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %1, i64 0, i32 6
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %11, i64 0, i32 7
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_highlight_recover_rgb_c698_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast %struct.range_task_helper_context* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 0
  store %struct.RuntimeContext.6* %context, %struct.RuntimeContext.6** %4, align 8
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.6*, i8*, i32)* @function_body, void (%struct.RuntimeContext.6*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %4, i64 0, i32 14
  %6 = bitcast i8** %5 to i32**
  %7 = load i32*, i32** %6, align 8
  %8 = load i32, i32* %7, align 4
  %9 = add i32 %8, 7
  %10 = sdiv i32 %9, 8
  %11 = icmp slt i32 %9, 0
  %12 = shl nsw i32 %10, 3
  %13 = icmp ne i32 %12, %9
  %14 = and i1 %11, %13
  %.neg = sext i1 %14 to i32
  %15 = add nsw i32 %10, %.neg
  %16 = tail call i32 @llvm.smax.i32(i32 %15, i32 512)
  %17 = mul i32 %16, %2
  %18 = add i32 %17, %16
  %19 = tail call i32 @llvm.smin.i32(i32 %8, i32 %18)
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 2
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 3
  %25 = bitcast float* %24 to <2 x float>*
  %26 = load <2 x float>, <2 x float>* %25, align 4
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 5
  %28 = load float, float* %27, align 4
  %29 = extractelement <2 x float> %26, i64 0
  %30 = extractelement <2 x float> %26, i64 1
  %31 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %29, float %30)
  %32 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %23, float 0x3F1A36E2E0000000)
  %33 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %26, <2 x float> <float 0x3F1A36E2E0000000, float 0x3F1A36E2E0000000>)
  %34 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %28, float 0.000000e+00)
  %35 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %23, float %31)
  %36 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %34, float 1.000000e+00)
  %37 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %35, float 0x3F1A36E2E0000000)
  %38 = icmp slt i32 %17, %19
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 0, i32 1
  %40 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %41 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %42 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 1, i32 1
  %43 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %44 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %broadcast.splatinsert58 = insertelement <8 x float> poison, float %32, i64 0
  %broadcast.splat59 = shufflevector <8 x float> %broadcast.splatinsert58, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splat61 = shufflevector <2 x float> %33, <2 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splat64 = shufflevector <2 x float> %33, <2 x float> poison, <8 x i32> <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %45 = extractelement <2 x float> %33, i64 0
  %shift = shufflevector <2 x float> %33, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.01743 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %322, %after_if ]
  %46 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %47 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %46, i64 0, i32 14
  %48 = load i8*, i8** %47, align 8
  %49 = getelementptr inbounds i8, i8* %48, i64 4
  %50 = bitcast i8* %49 to i32*
  %51 = load i32, i32* %50, align 4
  %52 = sdiv i32 %.01743, %51
  %53 = mul i32 %52, %51
  %54 = xor i32 %51, %.01743
  %55 = icmp slt i32 %54, 0
  %56 = icmp ne i32 %.01743, 0
  %57 = icmp ne i32 %53, %.01743
  %58 = and i1 %56, %55
  %59 = and i1 %58, %57
  %.neg19 = sext i1 %59 to i32
  %60 = add i32 %52, %.neg19
  %61 = mul i32 %60, %51
  %62 = sub i32 %.01743, %61
  %63 = load float*, float** %39, align 8
  %64 = load i32, i32* %40, align 4
  %65 = load i32, i32* %41, align 4
  %66 = mul i32 %60, %64
  %67 = add i32 %62, %66
  %68 = mul i32 %67, %65
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, float* %63, i64 %69
  %71 = load float, float* %70, align 4
  %72 = insertelement <2 x i32> poison, i32 %68, i64 0
  %73 = shufflevector <2 x i32> %72, <2 x i32> poison, <2 x i32> zeroinitializer
  %74 = add <2 x i32> %73, <i32 1, i32 2>
  %75 = sext <2 x i32> %74 to <2 x i64>
  %76 = insertelement <2 x float*> poison, float* %63, i64 0
  %77 = shufflevector <2 x float*> %76, <2 x float*> poison, <2 x i32> zeroinitializer
  %78 = getelementptr float, <2 x float*> %77, <2 x i64> %75
  %79 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %78, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %80 = fdiv reassoc ninf nsz <2 x float> %79, %33
  %81 = extractelement <2 x float> %80, i64 1
  %82 = getelementptr inbounds i8, i8* %48, i64 8
  %83 = bitcast i8* %82 to i32*
  %84 = load i32, i32* %83, align 4
  %85 = add i32 %84, -1
  %86 = getelementptr inbounds i8, i8* %48, i64 12
  %87 = bitcast i8* %86 to i32*
  %88 = load i32, i32* %87, align 4
  %89 = add i32 %88, -1
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %60, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert47 = insertelement <8 x i32> poison, i32 %85, i64 0
  %broadcast.splat48 = shufflevector <8 x i32> %broadcast.splatinsert47, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert49 = insertelement <8 x i32> poison, i32 %62, i64 0
  %broadcast.splat50 = shufflevector <8 x i32> %broadcast.splatinsert49, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert51 = insertelement <8 x i32> poison, i32 %89, i64 0
  %broadcast.splat52 = shufflevector <8 x i32> %broadcast.splatinsert51, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert53 = insertelement <8 x i32> poison, i32 %64, i64 0
  %broadcast.splat54 = shufflevector <8 x i32> %broadcast.splatinsert53, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert55 = insertelement <8 x i32> poison, i32 %65, i64 0
  %broadcast.splat56 = shufflevector <8 x i32> %broadcast.splatinsert55, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %for_loop_body
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ 120, %for_loop_body ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %for_loop_body ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %for_loop_body ], [ %predphi66, %vector.body ]
  %vec.phi45 = phi <8 x float> [ zeroinitializer, %for_loop_body ], [ %predphi65, %vector.body ]
  %vec.phi46 = phi <8 x float> [ zeroinitializer, %for_loop_body ], [ %predphi, %vector.body ]
  %90 = udiv <8 x i32> %vec.ind, <i32 11, i32 11, i32 11, i32 11, i32 11, i32 11, i32 11, i32 11>
  %91 = mul <8 x i32> %90, <i32 -11, i32 -11, i32 -11, i32 -11, i32 -11, i32 -11, i32 -11, i32 -11>
  %92 = add <8 x i32> %91, %vec.ind
  %93 = add nsw <8 x i32> %90, <i32 -5, i32 -5, i32 -5, i32 -5, i32 -5, i32 -5, i32 -5, i32 -5>
  %94 = add <8 x i32> %93, %broadcast.splat
  %95 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %94, <8 x i32> zeroinitializer)
  %96 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat48, <8 x i32> %95)
  %97 = add <8 x i32> %92, <i32 -5, i32 -5, i32 -5, i32 -5, i32 -5, i32 -5, i32 -5, i32 -5>
  %98 = add <8 x i32> %97, %broadcast.splat50
  %99 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %98, <8 x i32> zeroinitializer)
  %100 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat52, <8 x i32> %99)
  %101 = mul <8 x i32> %96, %broadcast.splat54
  %102 = add <8 x i32> %100, %101
  %103 = mul <8 x i32> %102, %broadcast.splat56
  %104 = add <8 x i32> %103, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %105 = sext <8 x i32> %104 to <8 x i64>
  %106 = getelementptr float, float* %63, <8 x i64> %105
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %106, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %107 = fcmp reassoc ninf nsz ogt <8 x float> %wide.masked.gather, <float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000>
  %108 = sext <8 x i32> %103 to <8 x i64>
  %109 = getelementptr float, float* %63, <8 x i64> %108
  %wide.masked.gather57 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %109, i32 4, <8 x i1> %107, <8 x float> undef)
  %110 = fdiv reassoc ninf nsz <8 x float> %wide.masked.gather57, %broadcast.splat59
  %111 = fdiv reassoc ninf nsz <8 x float> %wide.masked.gather, %broadcast.splat61
  %112 = add <8 x i32> %103, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %113 = sext <8 x i32> %112 to <8 x i64>
  %114 = getelementptr float, float* %63, <8 x i64> %113
  %wide.masked.gather62 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %114, i32 4, <8 x i1> %107, <8 x float> undef)
  %115 = fdiv reassoc ninf nsz <8 x float> %wide.masked.gather62, %broadcast.splat64
  %116 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %111, <8 x float> %115)
  %117 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %110, <8 x float> %116)
  %118 = call <8 x i32> @llvm.abs.v8i32(<8 x i32> %93, i1 true)
  %119 = call <8 x i32> @llvm.abs.v8i32(<8 x i32> %97, i1 true)
  %120 = add nuw <8 x i32> %119, %118
  %121 = sitofp <8 x i32> %120 to <8 x float>
  %122 = fmul reassoc ninf nsz <8 x float> %117, <float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000>
  %123 = fsub reassoc ninf nsz <8 x float> <float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000, float 0x4020AAAAC0000000>, %122
  %124 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %123, <8 x float> zeroinitializer)
  %125 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %124, <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %126 = fmul reassoc ninf nsz <8 x float> %125, %125
  %127 = fmul reassoc ninf nsz <8 x float> %125, <float -2.000000e+00, float -2.000000e+00, float -2.000000e+00, float -2.000000e+00, float -2.000000e+00, float -2.000000e+00, float -2.000000e+00, float -2.000000e+00>
  %128 = fadd reassoc ninf nsz <8 x float> %127, <float 3.000000e+00, float 3.000000e+00, float 3.000000e+00, float 3.000000e+00, float 3.000000e+00, float 3.000000e+00, float 3.000000e+00, float 3.000000e+00>
  %129 = fmul reassoc ninf nsz <8 x float> %126, %128
  %130 = fadd reassoc ninf nsz <8 x float> %121, <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>
  %131 = fdiv reassoc ninf nsz <8 x float> %129, %130
  %132 = fdiv reassoc ninf nsz <8 x float> %wide.masked.gather57, %wide.masked.gather
  %133 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %132, <8 x float> <float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000>)
  %134 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %133, <8 x float> <float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000>)
  %135 = fmul reassoc ninf nsz <8 x float> %131, %134
  %136 = fdiv reassoc ninf nsz <8 x float> %wide.masked.gather62, %wide.masked.gather
  %137 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %136, <8 x float> <float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000>)
  %138 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %137, <8 x float> <float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000>)
  %139 = fmul reassoc ninf nsz <8 x float> %131, %138
  %140 = select <8 x i1> %107, <8 x float> %135, <8 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>
  %predphi = fadd reassoc ninf nsz <8 x float> %vec.phi46, %140
  %141 = select <8 x i1> %107, <8 x float> %139, <8 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>
  %predphi65 = fadd reassoc ninf nsz <8 x float> %vec.phi45, %141
  %142 = select <8 x i1> %107, <8 x float> %131, <8 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>
  %predphi66 = fadd reassoc ninf nsz <8 x float> %vec.phi, %142
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %lsr.iv.next = add nsw i32 %lsr.iv, -8
  %143 = icmp eq i32 %lsr.iv.next, 0
  br i1 %143, label %middle.block, label %vector.body, !llvm.loop !9

middle.block:                                     ; preds = %vector.body
  %144 = extractelement <2 x float> %80, i64 0
  %145 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %144, float %81)
  %146 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %predphi)
  %147 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %predphi65)
  %148 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %predphi66)
  %149 = insertelement <2 x float> poison, float %147, i64 0
  %150 = insertelement <2 x float> %149, float %146, i64 1
  %151 = add i32 %60, 5
  %152 = tail call i32 @llvm.smax.i32(i32 %151, i32 0)
  %153 = tail call i32 @llvm.smin.i32(i32 %85, i32 %152)
  %154 = add i32 %62, 5
  %155 = tail call i32 @llvm.smax.i32(i32 %154, i32 0)
  %156 = tail call i32 @llvm.smin.i32(i32 %89, i32 %155)
  %157 = mul i32 %153, %64
  %158 = add i32 %156, %157
  %159 = mul i32 %158, %65
  %160 = add i32 %159, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %63, i64 %161
  %163 = load float, float* %162, align 4
  %164 = fcmp reassoc ninf nsz ogt float %163, 0x3EE4F8B580000000
  br i1 %164, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %middle.block
  %165 = fdiv reassoc ninf nsz float %163, %45
  %166 = add i32 %159, 2
  %167 = insertelement <2 x i32> poison, i32 %166, i64 0
  %168 = insertelement <2 x i32> %167, i32 %159, i64 1
  %169 = sext <2 x i32> %168 to <2 x i64>
  %170 = getelementptr float, <2 x float*> %77, <2 x i64> %169
  %171 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %170, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %172 = extractelement <2 x float> %171, i64 1
  %173 = fdiv reassoc ninf nsz float %172, %32
  %174 = fdiv reassoc ninf nsz <2 x float> %171, %shift
  %175 = extractelement <2 x float> %174, i64 0
  %176 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %165, float %175)
  %177 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %173, float %176)
  %178 = fmul reassoc ninf nsz float %177, 0x4020AAAAC0000000
  %179 = fsub reassoc ninf nsz float 0x4020AAAAC0000000, %178
  %180 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %179, float 0.000000e+00)
  %181 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %180, float 1.000000e+00)
  %182 = fmul reassoc ninf nsz float %181, %181
  %factor38 = fmul reassoc ninf nsz float %181, -2.000000e+00
  %183 = fadd reassoc ninf nsz float %factor38, 3.000000e+00
  %184 = fmul reassoc ninf nsz float %182, %183
  %185 = fdiv reassoc ninf nsz float %184, 1.100000e+01
  %186 = insertelement <2 x float> poison, float %163, i64 0
  %187 = shufflevector <2 x float> %186, <2 x float> poison, <2 x i32> zeroinitializer
  %188 = fdiv reassoc ninf nsz <2 x float> %171, %187
  %189 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %188, <2 x float> <float 0x3FDCCCCCC0000000, float 0x3FDCCCCCC0000000>)
  %190 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %189, <2 x float> <float 0x3FFCCCCCC0000000, float 0x3FFCCCCCC0000000>)
  %191 = insertelement <2 x float> poison, float %185, i64 0
  %192 = shufflevector <2 x float> %191, <2 x float> poison, <2 x i32> zeroinitializer
  %193 = fmul reassoc ninf nsz <2 x float> %192, %190
  %194 = fadd reassoc ninf nsz <2 x float> %193, %150
  %195 = fadd reassoc ninf nsz float %185, %148
  br label %after_if

after_if:                                         ; preds = %true_block, %middle.block
  %.1 = phi float [ %195, %true_block ], [ %148, %middle.block ]
  %196 = phi <2 x float> [ %194, %true_block ], [ %150, %middle.block ]
  %197 = fdiv reassoc ninf nsz float %71, %32
  %198 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %197, float %145)
  %199 = fcmp reassoc ninf nsz ogt float %.1, 0x3EE4F8B580000000
  %200 = extractelement <2 x float> %196, i64 1
  %201 = fdiv reassoc ninf nsz float %200, %.1
  %202 = select reassoc ninf nsz i1 %199, float %201, float 1.000000e+00
  %203 = extractelement <2 x float> %196, i64 0
  %204 = fdiv reassoc ninf nsz float %203, %.1
  %205 = select reassoc ninf nsz i1 %199, float %204, float 1.000000e+00
  %206 = fmul reassoc ninf nsz float %198, 5.000000e+00
  %207 = fadd reassoc ninf nsz float %206, -4.000000e+00
  %208 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %207, float 0.000000e+00)
  %209 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %208, float 1.000000e+00)
  %factor = fmul reassoc ninf nsz float %209, -2.000000e+00
  %210 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %211 = fmul reassoc ninf nsz float %209, %209
  %212 = fmul reassoc ninf nsz float %211, %36
  %213 = fmul reassoc ninf nsz float %212, %210
  %214 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %144, float %81)
  %215 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %197, float %214)
  %216 = fmul reassoc ninf nsz float %215, 0x4030AAAAC0000000
  %217 = fadd reassoc ninf nsz float %216, 0xC02F555580000000
  %218 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %217, float 0.000000e+00)
  %219 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %218, float 1.000000e+00)
  %factor26 = fmul reassoc ninf nsz float %219, -2.000000e+00
  %220 = fadd reassoc ninf nsz float %factor26, 3.000000e+00
  %221 = fmul reassoc ninf nsz float %219, %219
  %222 = fmul reassoc ninf nsz float %221, 0x3FD6666660000000
  %223 = fmul reassoc ninf nsz float %222, %220
  %224 = fmul reassoc ninf nsz float %223, %213
  %225 = fsub reassoc ninf nsz float 1.000000e+00, %224
  %226 = fmul reassoc ninf nsz float %202, %225
  %227 = fadd reassoc ninf nsz float %226, %224
  %228 = fmul reassoc ninf nsz float %205, %225
  %229 = fadd reassoc ninf nsz float %228, %224
  %230 = fmul reassoc ninf nsz float %197, 0x4020AAAAC0000000
  %231 = fsub reassoc ninf nsz float 0x4020AAAAC0000000, %230
  %232 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %231, float 0.000000e+00)
  %233 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %232, float 1.000000e+00)
  %234 = fmul reassoc ninf nsz <2 x float> %80, <float 0x4020AAAAC0000000, float 0x4020AAAAC0000000>
  %235 = fmul reassoc ninf nsz float %233, %233
  %factor29 = fmul reassoc ninf nsz float %233, -2.000000e+00
  %236 = fadd reassoc ninf nsz float %factor29, 3.000000e+00
  %237 = fmul reassoc ninf nsz float %235, %236
  %238 = fsub reassoc ninf nsz <2 x float> <float 0x4020AAAAC0000000, float 0x4020AAAAC0000000>, %234
  %239 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %238, <2 x float> zeroinitializer)
  %240 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %239, <2 x float> <float 1.000000e+00, float 1.000000e+00>)
  %241 = fmul reassoc ninf nsz <2 x float> %240, %240
  %242 = fmul reassoc ninf nsz <2 x float> %240, <float -2.000000e+00, float -2.000000e+00>
  %243 = fadd reassoc ninf nsz <2 x float> %242, <float 3.000000e+00, float 3.000000e+00>
  %244 = fmul reassoc ninf nsz <2 x float> %241, %243
  %245 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %227, float 0x3F1A36E2E0000000)
  %246 = fdiv reassoc ninf nsz float %71, %245
  %247 = fmul reassoc ninf nsz float %246, %237
  %248 = extractelement <2 x float> %244, i64 0
  %249 = extractelement <2 x float> %79, i64 0
  %250 = fmul reassoc ninf nsz <2 x float> %244, %79
  %251 = extractelement <2 x float> %250, i64 0
  %252 = fadd reassoc ninf nsz float %247, %251
  %253 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %229, float 0x3F1A36E2E0000000)
  %254 = extractelement <2 x float> %79, i64 1
  %255 = fdiv reassoc ninf nsz float %254, %253
  %256 = extractelement <2 x float> %244, i64 1
  %257 = fmul reassoc ninf nsz float %255, %256
  %258 = fadd reassoc ninf nsz float %252, %257
  %259 = fadd reassoc ninf nsz float %248, %237
  %260 = fadd reassoc ninf nsz float %259, %256
  %261 = fcmp reassoc ninf nsz ogt float %260, 0x3F1A36E2E0000000
  %262 = fdiv reassoc ninf nsz float %258, %260
  %263 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %246, float %255)
  %264 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %249, float %263)
  %265 = select reassoc ninf nsz i1 %261, float %262, float %264
  %266 = fmul reassoc ninf nsz float %265, %227
  %267 = fsub reassoc ninf nsz float %71, %266
  %268 = fmul reassoc ninf nsz float %267, %237
  %269 = fadd reassoc ninf nsz float %268, %266
  %270 = fsub reassoc ninf nsz float 1.000000e+00, %248
  %271 = fmul reassoc ninf nsz float %265, %270
  %272 = fadd reassoc ninf nsz float %271, %251
  %273 = fmul reassoc ninf nsz float %265, %229
  %274 = fsub reassoc ninf nsz float %254, %273
  %275 = fmul reassoc ninf nsz float %274, %256
  %276 = fadd reassoc ninf nsz float %275, %273
  %277 = fsub reassoc ninf nsz float 1.000000e+00, %213
  %278 = fmul reassoc ninf nsz float %277, %71
  %279 = fmul reassoc ninf nsz float %269, %213
  %280 = fadd reassoc ninf nsz float %279, %278
  %281 = fdiv reassoc ninf nsz float %280, %37
  %282 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %281, float 0.000000e+00)
  %283 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %282, float 1.000000e+00)
  %284 = load float*, float** %42, align 8
  %285 = load i32, i32* %43, align 4
  %286 = load i32, i32* %44, align 4
  %287 = mul i32 %285, %60
  %288 = add i32 %287, %62
  %289 = mul i32 %288, %286
  %290 = sext i32 %289 to i64
  %291 = getelementptr float, float* %284, i64 %290
  store float %283, float* %291, align 4
  %292 = fmul reassoc ninf nsz float %277, %249
  %293 = fmul reassoc ninf nsz float %272, %213
  %294 = fadd reassoc ninf nsz float %293, %292
  %295 = fdiv reassoc ninf nsz float %294, %37
  %296 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %295, float 0.000000e+00)
  %297 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %296, float 1.000000e+00)
  %298 = load float*, float** %42, align 8
  %299 = load i32, i32* %43, align 4
  %300 = load i32, i32* %44, align 4
  %301 = mul i32 %299, %60
  %302 = add i32 %301, %62
  %303 = mul i32 %302, %300
  %304 = add i32 %303, 1
  %305 = sext i32 %304 to i64
  %306 = getelementptr float, float* %298, i64 %305
  store float %297, float* %306, align 4
  %307 = fmul reassoc ninf nsz float %277, %254
  %308 = fmul reassoc ninf nsz float %276, %213
  %309 = fadd reassoc ninf nsz float %308, %307
  %310 = fdiv reassoc ninf nsz float %309, %37
  %311 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %310, float 0.000000e+00)
  %312 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %311, float 1.000000e+00)
  %313 = load float*, float** %42, align 8
  %314 = load i32, i32* %43, align 4
  %315 = load i32, i32* %44, align 4
  %316 = mul i32 %314, %60
  %317 = add i32 %316, %62
  %318 = mul i32 %317, %315
  %319 = add i32 %318, 2
  %320 = sext i32 %319 to i64
  %321 = getelementptr float, float* %313, i64 %320
  store float %312, float* %321, align 4
  %322 = add nsw i32 %.01743, 1
  %exitcond44.not = icmp eq i32 %322, %19
  br i1 %exitcond44.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.6**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.6*, %struct.RuntimeContext.6** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.7.0..sroa_cast, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 32
  %.sroa.8.0..sroa_cast = bitcast i8* %.sroa.8.0..sroa_idx to i64*
  %.sroa.8.0.copyload = load i64, i64* %.sroa.8.0..sroa_cast, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 40
  %.sroa.9.0..sroa_cast = bitcast i8* %.sroa.9.0..sroa_idx to i32*
  %.sroa.9.0.copyload = load i32, i32* %.sroa.9.0..sroa_cast, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 44
  %.sroa.12.0..sroa_cast = bitcast i8* %.sroa.12.0..sroa_idx to i32*
  %.sroa.12.0.copyload = load i32, i32* %.sroa.12.0..sroa_cast, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 48
  %.sroa.15.0..sroa_cast = bitcast i8* %.sroa.15.0..sroa_idx to i32*
  %.sroa.15.0.copyload = load i32, i32* %.sroa.15.0..sroa_cast, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 52
  %.sroa.17.0..sroa_cast = bitcast i8* %.sroa.17.0..sroa_idx to i32*
  %.sroa.17.0.copyload = load i32, i32* %.sroa.17.0..sroa_cast, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.6* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.6* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %4, i64 0, i32 2
  store i32 %1, i32* %10, align 8
  switch i32 %.sroa.17.0.copyload, label %.loopexit [
    i32 1, label %11
    i32 -1, label %19
  ]

11:                                               ; preds = %7
  %12 = mul nsw i32 %.sroa.15.0.copyload, %2
  %13 = add nsw i32 %12, %.sroa.9.0.copyload
  %14 = add nsw i32 %13, %.sroa.15.0.copyload
  %15 = call i32 @llvm.smin.i32(i32 %.sroa.12.0.copyload, i32 %14)
  %16 = icmp slt i32 %13, %15
  br i1 %16, label %.lr.ph.preheader, label %.loopexit

.lr.ph.preheader:                                 ; preds = %11
  br label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %.lr.ph.preheader
  %.02038 = phi i32 [ %17, %.lr.ph ], [ %13, %.lr.ph.preheader ]
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !11

19:                                               ; preds = %7
  %20 = mul nsw i32 %.sroa.15.0.copyload, %2
  %21 = sub nsw i32 %.sroa.12.0.copyload, %20
  %22 = mul nsw i32 %21, %.sroa.15.0.copyload
  %23 = call i32 @llvm.smax.i32(i32 %.sroa.9.0.copyload, i32 %22)
  %.not25.not39 = icmp sgt i32 %21, %23
  br i1 %.not25.not39, label %.lr.ph41.preheader, label %.loopexit

.lr.ph41.preheader:                               ; preds = %19
  br label %.lr.ph41

.lr.ph41:                                         ; preds = %.lr.ph41, %.lr.ph41.preheader
  %.0.in40 = phi i32 [ %.0, %.lr.ph41 ], [ %21, %.lr.ph41.preheader ]
  %.0 = add nsw i32 %.0.in40, -1
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !13

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.maxnum.v8f32(<8 x float>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.abs.v8i32(<8 x i32>, i1 immarg) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.minnum.v8f32(<8 x float>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.maxnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.minnum.v2f32(<2 x float>, <2 x float>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone willreturn }

!llvm.linker.options = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}
!llvm.module.flags = !{!6, !7, !8}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"clang version 14.0.6"}
!6 = !{i32 1, !"wchar_size", i32 2}
!7 = !{i32 7, !"PIC Level", i32 2}
!8 = !{i32 7, !"uwtable", i32 1}
!9 = distinct !{!9, !10}
!10 = !{!"llvm.loop.isvectorized", i32 1}
!11 = distinct !{!11, !12}
!12 = !{!"llvm.loop.mustprogress"}
!13 = distinct !{!13, !12}
