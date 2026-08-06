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
define void @_hs_coarsest_level_kernel_c702_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 8
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %18, i64 0, i32 4
  %20 = load float, float* %19, align 4
  %21 = fmul reassoc ninf nsz float %20, %20
  %22 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 16
  %26 = bitcast i8* %25 to float*
  store float %21, float* %26, align 4
  %27 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %28 = tail call i32 @llvm.smax.i32(i32 %12, i32 0)
  %29 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  store i32 %28, i32* %33, align 4
  %34 = mul i32 %28, %27
  %35 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %35, i64 0, i32 14
  %37 = bitcast i8** %36 to i32**
  %38 = load i32*, i32** %37, align 8
  store i32 %34, i32* %38, align 4
  ret void
}

; Function Attrs: nounwind
define void @_hs_coarsest_level_kernel_c702_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 1, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 2, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 2, i32 0, i32 2
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 3, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32 }* %21, i64 0, i32 3, i32 0, i32 2
  %35 = icmp sgt i32 %23, 0
  %min.iters.check = icmp ult i32 %23, 16
  %n.vec = and i32 %23, -8
  %cmp.n = icmp eq i32 %23, %n.vec
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.0615 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %272, %after_for3 ]
  %36 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %37 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %36, i64 0, i32 14
  %38 = load i8*, i8** %37, align 8
  %39 = getelementptr inbounds i8, i8* %38, i64 4
  %40 = bitcast i8* %39 to i32*
  %41 = load i32, i32* %40, align 4
  %42 = sdiv i32 %.0615, %41
  %43 = mul i32 %42, %41
  %44 = xor i32 %41, %.0615
  %45 = icmp slt i32 %44, 0
  %46 = icmp ne i32 %.0615, 0
  %47 = icmp ne i32 %43, %.0615
  %48 = and i1 %46, %45
  %49 = and i1 %48, %47
  %.neg7 = sext i1 %49 to i32
  %50 = add i32 %42, %.neg7
  %51 = mul i32 %50, %41
  %52 = sub i32 %.0615, %51
  %53 = getelementptr inbounds i8, i8* %38, i64 8
  %54 = bitcast i8* %53 to i32*
  %55 = load i32, i32* %54, align 4
  %56 = add i32 %55, -1
  %57 = getelementptr inbounds i8, i8* %38, i64 12
  %58 = bitcast i8* %57 to i32*
  %59 = load i32, i32* %58, align 4
  %60 = add i32 %59, -1
  %61 = load float*, float** %25, align 8
  %62 = load i32, i32* %26, align 4
  %63 = mul i32 %50, %62
  %64 = load float*, float** %27, align 8
  %65 = load i32, i32* %28, align 4
  %66 = mul i32 %65, %50
  %67 = insertelement <2 x i32> poison, i32 %52, i64 0
  %68 = shufflevector <2 x i32> %67, <2 x i32> poison, <2 x i32> zeroinitializer
  %69 = add <2 x i32> %68, <i32 1, i32 -1>
  %70 = insertelement <2 x i32> poison, i32 %56, i64 0
  %71 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %72 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %69, <2 x i32> %71)
  %73 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %72, <2 x i32> zeroinitializer)
  %74 = extractelement <2 x i32> %73, i64 0
  %75 = add i32 %74, %63
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, float* %61, i64 %76
  %78 = load float, float* %77, align 4
  %79 = insertelement <2 x i32> poison, i32 %66, i64 0
  %80 = shufflevector <2 x i32> %79, <2 x i32> poison, <2 x i32> zeroinitializer
  %81 = add <2 x i32> %73, %80
  %82 = sext <2 x i32> %81 to <2 x i64>
  %83 = extractelement <2 x i64> %82, i64 0
  %84 = getelementptr float, float* %64, i64 %83
  %85 = load float, float* %84, align 4
  %86 = extractelement <2 x i32> %73, i64 1
  %87 = add i32 %86, %63
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, float* %61, i64 %88
  %90 = load float, float* %89, align 4
  %91 = extractelement <2 x i64> %82, i64 1
  %92 = getelementptr float, float* %64, i64 %91
  %93 = load float, float* %92, align 4
  %94 = insertelement <2 x i32> poison, i32 %50, i64 0
  %95 = shufflevector <2 x i32> %94, <2 x i32> poison, <2 x i32> zeroinitializer
  %96 = add <2 x i32> %95, <i32 1, i32 -1>
  %97 = insertelement <2 x i32> poison, i32 %60, i64 0
  %98 = shufflevector <2 x i32> %97, <2 x i32> poison, <2 x i32> zeroinitializer
  %99 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %96, <2 x i32> %98)
  %100 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %99, <2 x i32> zeroinitializer)
  %101 = extractelement <2 x i32> %100, i64 0
  %102 = mul i32 %101, %62
  %103 = add i32 %102, %52
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, float* %61, i64 %104
  %106 = load float, float* %105, align 4
  %107 = insertelement <2 x i32> poison, i32 %65, i64 0
  %108 = shufflevector <2 x i32> %107, <2 x i32> poison, <2 x i32> zeroinitializer
  %109 = mul <2 x i32> %100, %108
  %110 = add <2 x i32> %109, %68
  %111 = sext <2 x i32> %110 to <2 x i64>
  %112 = extractelement <2 x i64> %111, i64 0
  %113 = getelementptr float, float* %64, i64 %112
  %114 = load float, float* %113, align 4
  %115 = extractelement <2 x i32> %100, i64 1
  %116 = mul i32 %115, %62
  %117 = add i32 %116, %52
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, float* %61, i64 %118
  %120 = load float, float* %119, align 4
  %121 = extractelement <2 x i64> %111, i64 1
  %122 = getelementptr float, float* %64, i64 %121
  %123 = load float, float* %122, align 4
  %.neg10 = fadd reassoc ninf nsz float %85, %78
  %124 = fadd reassoc ninf nsz float %90, %93
  %125 = fsub reassoc ninf nsz float %.neg10, %124
  %126 = fmul reassoc ninf nsz float %125, 2.500000e-01
  %.neg13 = fadd reassoc ninf nsz float %114, %106
  %127 = fadd reassoc ninf nsz float %120, %123
  %128 = fsub reassoc ninf nsz float %.neg13, %127
  %129 = fmul reassoc ninf nsz float %128, 2.500000e-01
  %130 = add i32 %66, %52
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, float* %64, i64 %131
  %133 = load float, float* %132, align 4
  %134 = add i32 %52, %63
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %61, i64 %135
  %137 = load float, float* %136, align 4
  %138 = fsub reassoc ninf nsz float %133, %137
  %139 = load float*, float** %29, align 8
  %140 = load i32, i32* %30, align 4
  %141 = load i32, i32* %31, align 4
  %142 = mul i32 %140, %50
  %143 = add i32 %142, %52
  %144 = mul i32 %143, %141
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %139, i64 %145
  store float 0.000000e+00, float* %146, align 4
  %147 = load float*, float** %29, align 8
  %148 = load i32, i32* %30, align 4
  %149 = load i32, i32* %31, align 4
  %150 = mul i32 %148, %50
  %151 = add i32 %150, %52
  %152 = mul i32 %151, %149
  %153 = add i32 %152, 1
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %147, i64 %154
  store float 0.000000e+00, float* %155, align 4
  %156 = load float*, float** %32, align 8
  %157 = load i32, i32* %33, align 4
  %158 = load i32, i32* %34, align 4
  %159 = mul i32 %157, %50
  %160 = add i32 %159, %52
  %161 = mul i32 %160, %158
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, float* %156, i64 %162
  store float 0.000000e+00, float* %163, align 4
  %164 = load float*, float** %32, align 8
  %165 = load i32, i32* %33, align 4
  %166 = load i32, i32* %34, align 4
  %167 = mul i32 %165, %50
  %168 = add i32 %167, %52
  %169 = mul i32 %168, %166
  %170 = add i32 %169, 1
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %164, i64 %171
  store float 0.000000e+00, float* %172, align 4
  %173 = fmul reassoc ninf nsz float %126, %126
  %174 = fmul reassoc ninf nsz float %129, %129
  %175 = tail call i32 @llvm.smin.i32(i32 %52, i32 %56)
  %176 = tail call i32 @llvm.smin.i32(i32 %50, i32 %60)
  %177 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %178 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %177, i64 0, i32 14
  %179 = load i8*, i8** %178, align 8
  %180 = getelementptr inbounds i8, i8* %179, i64 16
  %181 = bitcast i8* %180 to float*
  %182 = load float, float* %181, align 4
  %183 = tail call i32 @llvm.smax.i32(i32 %175, i32 0)
  %184 = tail call i32 @llvm.smax.i32(i32 %176, i32 0)
  %185 = fadd reassoc ninf nsz float %174, %173
  %186 = fadd reassoc ninf nsz float %185, %182
  %187 = load float*, float** %29, align 8
  %188 = load i32, i32* %30, align 4
  %189 = load i32, i32* %31, align 4
  %190 = mul i32 %188, %101
  %191 = add i32 %190, %183
  %192 = mul i32 %191, %189
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, float* %187, i64 %193
  %195 = add i32 %192, 1
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, float* %187, i64 %196
  %198 = mul i32 %188, %184
  %199 = add i32 %198, %74
  %200 = mul i32 %199, %189
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, float* %187, i64 %201
  %203 = add i32 %200, 1
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, float* %187, i64 %204
  %206 = mul i32 %188, %115
  %207 = add i32 %206, %183
  %208 = mul i32 %207, %189
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %187, i64 %209
  %211 = add i32 %208, 1
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, float* %187, i64 %212
  %214 = add i32 %198, %86
  %215 = mul i32 %214, %189
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, float* %187, i64 %216
  %218 = add i32 %215, 1
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, float* %187, i64 %219
  br i1 %35, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  br i1 %min.iters.check, label %for_loop_body1.preheader138, label %vector.memcheck

vector.memcheck:                                  ; preds = %for_loop_body1.preheader
  %scevgep = getelementptr float, float* %139, i64 1
  %scevgep17 = getelementptr float, float* %scevgep, i64 %145
  %scevgep19 = getelementptr float, float* %147, i64 1
  %scevgep20 = getelementptr float, float* %scevgep19, i64 %154
  %scevgep22 = getelementptr float, float* %187, i64 1
  %scevgep23 = getelementptr float, float* %scevgep22, i64 %204
  %scevgep26 = getelementptr float, float* %scevgep22, i64 %201
  %scevgep29 = getelementptr float, float* %scevgep22, i64 %219
  %scevgep32 = getelementptr float, float* %scevgep22, i64 %216
  %scevgep35 = getelementptr float, float* %scevgep22, i64 %196
  %scevgep38 = getelementptr float, float* %scevgep22, i64 %193
  %scevgep41 = getelementptr float, float* %scevgep22, i64 %212
  %scevgep44 = getelementptr float, float* %scevgep22, i64 %209
  %bound0 = icmp ult float* %146, %scevgep20
  %bound1 = icmp ult float* %155, %scevgep17
  %found.conflict = and i1 %bound0, %bound1
  %bound046 = icmp ult float* %146, %scevgep23
  %bound147 = icmp ult float* %205, %scevgep17
  %found.conflict48 = and i1 %bound046, %bound147
  %conflict.rdx = or i1 %found.conflict, %found.conflict48
  %bound049 = icmp ult float* %146, %scevgep26
  %bound150 = icmp ult float* %202, %scevgep17
  %found.conflict51 = and i1 %bound049, %bound150
  %conflict.rdx52 = or i1 %conflict.rdx, %found.conflict51
  %bound053 = icmp ult float* %146, %scevgep29
  %bound154 = icmp ult float* %220, %scevgep17
  %found.conflict55 = and i1 %bound053, %bound154
  %conflict.rdx56 = or i1 %conflict.rdx52, %found.conflict55
  %bound057 = icmp ult float* %146, %scevgep32
  %bound158 = icmp ult float* %217, %scevgep17
  %found.conflict59 = and i1 %bound057, %bound158
  %conflict.rdx60 = or i1 %conflict.rdx56, %found.conflict59
  %bound061 = icmp ult float* %146, %scevgep35
  %bound162 = icmp ult float* %197, %scevgep17
  %found.conflict63 = and i1 %bound061, %bound162
  %conflict.rdx64 = or i1 %conflict.rdx60, %found.conflict63
  %bound065 = icmp ult float* %146, %scevgep38
  %bound166 = icmp ult float* %194, %scevgep17
  %found.conflict67 = and i1 %bound065, %bound166
  %conflict.rdx68 = or i1 %conflict.rdx64, %found.conflict67
  %bound069 = icmp ult float* %146, %scevgep41
  %bound170 = icmp ult float* %213, %scevgep17
  %found.conflict71 = and i1 %bound069, %bound170
  %conflict.rdx72 = or i1 %conflict.rdx68, %found.conflict71
  %bound073 = icmp ult float* %146, %scevgep44
  %bound174 = icmp ult float* %210, %scevgep17
  %found.conflict75 = and i1 %bound073, %bound174
  %conflict.rdx76 = or i1 %conflict.rdx72, %found.conflict75
  %bound077 = icmp ult float* %155, %scevgep23
  %bound178 = icmp ult float* %205, %scevgep20
  %found.conflict79 = and i1 %bound077, %bound178
  %conflict.rdx80 = or i1 %conflict.rdx76, %found.conflict79
  %bound081 = icmp ult float* %155, %scevgep26
  %bound182 = icmp ult float* %202, %scevgep20
  %found.conflict83 = and i1 %bound081, %bound182
  %conflict.rdx84 = or i1 %conflict.rdx80, %found.conflict83
  %bound085 = icmp ult float* %155, %scevgep29
  %bound186 = icmp ult float* %220, %scevgep20
  %found.conflict87 = and i1 %bound085, %bound186
  %conflict.rdx88 = or i1 %conflict.rdx84, %found.conflict87
  %bound089 = icmp ult float* %155, %scevgep32
  %bound190 = icmp ult float* %217, %scevgep20
  %found.conflict91 = and i1 %bound089, %bound190
  %conflict.rdx92 = or i1 %conflict.rdx88, %found.conflict91
  %bound093 = icmp ult float* %155, %scevgep35
  %bound194 = icmp ult float* %197, %scevgep20
  %found.conflict95 = and i1 %bound093, %bound194
  %conflict.rdx96 = or i1 %conflict.rdx92, %found.conflict95
  %bound097 = icmp ult float* %155, %scevgep38
  %bound198 = icmp ult float* %194, %scevgep20
  %found.conflict99 = and i1 %bound097, %bound198
  %conflict.rdx100 = or i1 %conflict.rdx96, %found.conflict99
  %bound0101 = icmp ult float* %155, %scevgep41
  %bound1102 = icmp ult float* %213, %scevgep20
  %found.conflict103 = and i1 %bound0101, %bound1102
  %conflict.rdx104 = or i1 %conflict.rdx100, %found.conflict103
  %bound0105 = icmp ult float* %155, %scevgep44
  %bound1106 = icmp ult float* %210, %scevgep20
  %found.conflict107 = and i1 %bound0105, %bound1106
  %conflict.rdx108 = or i1 %conflict.rdx104, %found.conflict107
  br i1 %conflict.rdx108, label %for_loop_body1.preheader138, label %vector.ph

vector.ph:                                        ; preds = %vector.memcheck
  %broadcast.splatinsert123 = insertelement <8 x float> poison, float %126, i64 0
  %broadcast.splat124 = shufflevector <8 x float> %broadcast.splatinsert123, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert125 = insertelement <8 x float> poison, float %129, i64 0
  %broadcast.splat126 = shufflevector <8 x float> %broadcast.splatinsert125, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert127 = insertelement <8 x float> poison, float %138, i64 0
  %broadcast.splat128 = shufflevector <8 x float> %broadcast.splatinsert127, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert129 = insertelement <8 x float> poison, float %186, i64 0
  %broadcast.splat130 = shufflevector <8 x float> %broadcast.splatinsert129, <8 x float> poison, <8 x i32> zeroinitializer
  %221 = load float, float* %210, align 4, !alias.scope !9
  %222 = load float, float* %213, align 4, !alias.scope !12
  %223 = load float, float* %194, align 4, !alias.scope !14
  %.scalar = fadd reassoc ninf nsz float %223, %221
  %224 = load float, float* %197, align 4, !alias.scope !16
  %.scalar131 = fadd reassoc ninf nsz float %224, %222
  %225 = load float, float* %217, align 4, !alias.scope !18
  %.scalar132 = fadd reassoc ninf nsz float %.scalar, %225
  %226 = load float, float* %220, align 4, !alias.scope !20
  %.scalar133 = fadd reassoc ninf nsz float %.scalar131, %226
  %227 = load float, float* %202, align 4, !alias.scope !22
  %.scalar134 = fadd reassoc ninf nsz float %.scalar132, %227
  %228 = load float, float* %205, align 4, !alias.scope !24
  %.scalar135 = fadd reassoc ninf nsz float %.scalar133, %228
  %.scalar136 = fmul reassoc ninf nsz float %.scalar134, 2.500000e-01
  %229 = insertelement <8 x float> poison, float %.scalar136, i64 0
  %230 = shufflevector <8 x float> %229, <8 x float> poison, <8 x i32> zeroinitializer
  %.scalar137 = fmul reassoc ninf nsz float %.scalar135, 2.500000e-01
  %231 = insertelement <8 x float> poison, float %.scalar137, i64 0
  %232 = shufflevector <8 x float> %231, <8 x float> poison, <8 x i32> zeroinitializer
  %233 = fmul reassoc ninf nsz <8 x float> %230, %broadcast.splat124
  %234 = fmul reassoc ninf nsz <8 x float> %232, %broadcast.splat126
  %235 = fadd reassoc ninf nsz <8 x float> %233, %broadcast.splat128
  %236 = fadd reassoc ninf nsz <8 x float> %235, %234
  %237 = fmul reassoc ninf nsz <8 x float> %236, %broadcast.splat124
  %238 = fdiv reassoc ninf nsz <8 x float> %237, %broadcast.splat130
  %239 = fsub reassoc ninf nsz <8 x float> %230, %238
  %240 = fmul reassoc ninf nsz <8 x float> %236, %broadcast.splat126
  %241 = fdiv reassoc ninf nsz <8 x float> %240, %broadcast.splat130
  %242 = extractelement <8 x float> %239, i64 7
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  br i1 true, label %middle.block, label %vector.body, !llvm.loop !26

middle.block:                                     ; preds = %vector.body
  %243 = fsub reassoc ninf nsz <8 x float> %232, %241
  %244 = extractelement <8 x float> %243, i64 7
  store float %242, float* %146, align 4, !alias.scope !28, !noalias !30
  store float %244, float* %155, align 4, !alias.scope !32, !noalias !33
  br i1 %cmp.n, label %after_for3, label %for_loop_body1.preheader138

for_loop_body1.preheader138:                      ; preds = %middle.block, %vector.memcheck, %for_loop_body1.preheader
  %.014.ph = phi i32 [ 0, %vector.memcheck ], [ 0, %for_loop_body1.preheader ], [ %n.vec, %middle.block ]
  %245 = sub i32 %23, %.014.ph
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader138
  %lsr.iv139 = phi i32 [ %245, %for_loop_body1.preheader138 ], [ %lsr.iv.next140, %for_loop_body1 ]
  %246 = load float, float* %210, align 4
  %247 = load float, float* %213, align 4
  %248 = load float, float* %194, align 4
  %249 = fadd reassoc ninf nsz float %248, %246
  %250 = load float, float* %197, align 4
  %251 = fadd reassoc ninf nsz float %250, %247
  %252 = load float, float* %217, align 4
  %253 = fadd reassoc ninf nsz float %249, %252
  %254 = load float, float* %220, align 4
  %255 = fadd reassoc ninf nsz float %251, %254
  %256 = load float, float* %202, align 4
  %257 = fadd reassoc ninf nsz float %253, %256
  %258 = load float, float* %205, align 4
  %259 = fadd reassoc ninf nsz float %255, %258
  %260 = fmul reassoc ninf nsz float %257, 2.500000e-01
  %261 = fmul reassoc ninf nsz float %259, 2.500000e-01
  %262 = fmul reassoc ninf nsz float %260, %126
  %263 = fmul reassoc ninf nsz float %261, %129
  %264 = fadd reassoc ninf nsz float %262, %138
  %265 = fadd reassoc ninf nsz float %264, %263
  %266 = fmul reassoc ninf nsz float %265, %126
  %267 = fdiv reassoc ninf nsz float %266, %186
  %268 = fsub reassoc ninf nsz float %260, %267
  %269 = fmul reassoc ninf nsz float %265, %129
  %270 = fdiv reassoc ninf nsz float %269, %186
  %271 = fsub reassoc ninf nsz float %261, %270
  store float %268, float* %146, align 4
  store float %271, float* %155, align 4
  %lsr.iv.next140 = add i32 %lsr.iv139, -1
  %exitcond.not = icmp eq i32 %lsr.iv.next140, 0
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1, !llvm.loop !34

after_for3.loopexit:                              ; preds = %for_loop_body1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %middle.block, %for_loop_body
  %272 = add nsw i32 %.0615, 1
  %exitcond16.not = icmp eq i32 %272, %19
  br i1 %exitcond16.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !35

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !37

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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
!9 = !{!10}
!10 = distinct !{!10, !11}
!11 = distinct !{!11, !"LVerDomain"}
!12 = !{!13}
!13 = distinct !{!13, !11}
!14 = !{!15}
!15 = distinct !{!15, !11}
!16 = !{!17}
!17 = distinct !{!17, !11}
!18 = !{!19}
!19 = distinct !{!19, !11}
!20 = !{!21}
!21 = distinct !{!21, !11}
!22 = !{!23}
!23 = distinct !{!23, !11}
!24 = !{!25}
!25 = distinct !{!25, !11}
!26 = distinct !{!26, !27}
!27 = !{!"llvm.loop.isvectorized", i32 1}
!28 = !{!29}
!29 = distinct !{!29, !11}
!30 = !{!31, !25, !23, !21, !19, !17, !15, !13, !10}
!31 = distinct !{!31, !11}
!32 = !{!31}
!33 = !{!25, !23, !21, !19, !17, !15, !13, !10}
!34 = distinct !{!34, !27}
!35 = distinct !{!35, !36}
!36 = !{!"llvm.loop.mustprogress"}
!37 = distinct !{!37, !36}
