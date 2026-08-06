; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.24*, void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.24 = type { i8*, %struct.LLVMRuntime.23*, i32, i64* }
%struct.LLVMRuntime.23 = type { %struct.PreallocatedMemoryChunk.19, %struct.PreallocatedMemoryChunk.19, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.20*], [1024 x %struct.NodeManager.21*], [1024 x i8*], i8*, %struct.RandState.22*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.19 = type { i8*, i8*, i64 }
%struct.ListManager.20 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.23* }
%struct.NodeManager.21 = type { %struct.LLVMRuntime.23*, i32, i32, i32, i32, %struct.ListManager.20*, %struct.ListManager.20*, %struct.ListManager.20*, i32 }
%struct.RandState.22 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_hs_refinement_level_kernel_c704_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 8
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %18, i64 0, i32 4, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %21, i64 0, i32 14
  %23 = load i8*, i8** %22, align 8
  %24 = getelementptr inbounds i8, i8* %23, i64 16
  %25 = bitcast i8* %24 to i32*
  store i32 %20, i32* %25, align 4
  %26 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }** %0, align 8
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %26, i64 0, i32 4, i32 0, i32 1
  %28 = load i32, i32* %27, align 4
  %29 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 20
  %33 = bitcast i8* %32 to i32*
  store i32 %28, i32* %33, align 4
  %34 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }** %0, align 8
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %34, i64 0, i32 5
  %36 = load float, float* %35, align 4
  %37 = fmul reassoc ninf nsz float %36, %36
  %38 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 24
  %42 = bitcast i8* %41 to float*
  store float %37, float* %42, align 4
  %43 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %44 = tail call i32 @llvm.smax.i32(i32 %12, i32 0)
  %45 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %46 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %45, i64 0, i32 14
  %47 = load i8*, i8** %46, align 8
  %48 = getelementptr inbounds i8, i8* %47, i64 4
  %49 = bitcast i8* %48 to i32*
  store i32 %44, i32* %49, align 4
  %50 = mul i32 %44, %43
  %51 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %51, i64 0, i32 14
  %53 = bitcast i8** %52 to i32**
  %54 = load i32*, i32** %53, align 8
  store i32 %50, i32* %54, align 4
  ret void
}

; Function Attrs: nounwind
define void @_hs_refinement_level_kernel_c704_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.24* %context, %struct.RuntimeContext.24** %4, align 8
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.24*, i8*, i32)* @function_body, void (%struct.RuntimeContext.24*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 7
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 6
  %25 = load i32, i32* %24, align 4
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 1, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %31 = sitofp i32 %23 to float
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 2, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 2
  %35 = icmp sgt i32 %25, 0
  %min.iters.check = icmp ult i32 %25, 16
  %n.vec = and i32 %25, -8
  %cmp.n = icmp eq i32 %25, %n.vec
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for6, %for_loop_body.lr.ph
  %.01123 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %300, %after_for6 ]
  %36 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %37 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %36, i64 0, i32 14
  %38 = load i8*, i8** %37, align 8
  %39 = getelementptr inbounds i8, i8* %38, i64 4
  %40 = bitcast i8* %39 to i32*
  %41 = load i32, i32* %40, align 4
  %42 = sdiv i32 %.01123, %41
  %43 = mul i32 %42, %41
  %44 = xor i32 %41, %.01123
  %45 = icmp slt i32 %44, 0
  %46 = icmp ne i32 %.01123, 0
  %47 = icmp ne i32 %43, %.01123
  %48 = and i1 %46, %45
  %49 = and i1 %48, %47
  %.neg13 = sext i1 %49 to i32
  %50 = add i32 %42, %.neg13
  %51 = mul i32 %50, %41
  %52 = sub i32 %.01123, %51
  %53 = getelementptr inbounds i8, i8* %38, i64 8
  %54 = bitcast i8* %53 to i32*
  %55 = load i32, i32* %54, align 4
  %56 = add i32 %55, -1
  %57 = getelementptr inbounds i8, i8* %38, i64 12
  %58 = bitcast i8* %57 to i32*
  %59 = load i32, i32* %58, align 4
  %60 = add i32 %59, -1
  %61 = load float*, float** %27, align 8
  %62 = load i32, i32* %28, align 4
  %63 = mul i32 %50, %62
  %64 = load float*, float** %29, align 8
  %65 = load i32, i32* %30, align 4
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
  %.neg18 = fadd reassoc ninf nsz float %85, %78
  %124 = fadd reassoc ninf nsz float %90, %93
  %125 = fsub reassoc ninf nsz float %.neg18, %124
  %126 = fmul reassoc ninf nsz float %125, 2.500000e-01
  %.neg21 = fadd reassoc ninf nsz float %114, %106
  %127 = fadd reassoc ninf nsz float %120, %123
  %128 = fsub reassoc ninf nsz float %.neg21, %127
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
  %139 = sdiv i32 %50, %23
  %140 = mul i32 %139, %23
  %141 = xor i32 %50, %23
  %142 = icmp slt i32 %141, 0
  %143 = icmp ne i32 %50, 0
  %144 = icmp ne i32 %140, %50
  %145 = and i1 %143, %142
  %146 = and i1 %145, %144
  %.neg14 = sext i1 %146 to i32
  %147 = add i32 %139, %.neg14
  %148 = sdiv i32 %52, %23
  %149 = mul i32 %148, %23
  %150 = xor i32 %52, %23
  %151 = icmp slt i32 %150, 0
  %152 = icmp ne i32 %.01123, %51
  %153 = icmp ne i32 %149, %52
  %154 = and i1 %152, %151
  %155 = and i1 %154, %153
  %.neg15 = sext i1 %155 to i32
  %156 = add i32 %148, %.neg15
  %157 = getelementptr inbounds i8, i8* %38, i64 16
  %158 = bitcast i8* %157 to i32*
  %159 = load i32, i32* %158, align 4
  %160 = icmp slt i32 %147, %159
  br i1 %160, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_for6
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %161 = getelementptr inbounds i8, i8* %38, i64 20
  %162 = bitcast i8* %161 to i32*
  %163 = load i32, i32* %162, align 4
  %164 = icmp slt i32 %156, %163
  br i1 %164, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %165 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }** %20, align 8
  %166 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %165, i64 0, i32 4, i32 1
  %167 = load float*, float** %166, align 8
  %168 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %165, i64 0, i32 4, i32 0, i32 1
  %169 = load i32, i32* %168, align 4
  %170 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, i32, i32 }* %165, i64 0, i32 4, i32 0, i32 2
  %171 = load i32, i32* %170, align 4
  %172 = mul i32 %169, %147
  %173 = add i32 %172, %156
  %174 = mul i32 %173, %171
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, float* %167, i64 %175
  %177 = load float, float* %176, align 4
  %178 = fmul reassoc ninf nsz float %177, %31
  %179 = add i32 %174, 1
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, float* %167, i64 %180
  %182 = load float, float* %181, align 4
  %183 = fmul reassoc ninf nsz float %182, %31
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %true_block, %for_loop_body
  %.010 = phi float [ %178, %true_block1 ], [ 0.000000e+00, %true_block ], [ 0.000000e+00, %for_loop_body ]
  %.09 = phi float [ %183, %true_block1 ], [ 0.000000e+00, %true_block ], [ 0.000000e+00, %for_loop_body ]
  %184 = load float*, float** %32, align 8
  %185 = load i32, i32* %33, align 4
  %186 = load i32, i32* %34, align 4
  %187 = mul i32 %185, %50
  %188 = add i32 %187, %52
  %189 = mul i32 %188, %186
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %184, i64 %190
  store float %.010, float* %191, align 4
  %192 = load float*, float** %32, align 8
  %193 = load i32, i32* %33, align 4
  %194 = load i32, i32* %34, align 4
  %195 = mul i32 %193, %50
  %196 = add i32 %195, %52
  %197 = mul i32 %196, %194
  %198 = add i32 %197, 1
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, float* %192, i64 %199
  store float %.09, float* %200, align 4
  %201 = fmul reassoc ninf nsz float %126, %126
  %202 = fmul reassoc ninf nsz float %129, %129
  %203 = tail call i32 @llvm.smin.i32(i32 %52, i32 %56)
  %204 = tail call i32 @llvm.smin.i32(i32 %50, i32 %60)
  %205 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %206 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %205, i64 0, i32 14
  %207 = load i8*, i8** %206, align 8
  %208 = getelementptr inbounds i8, i8* %207, i64 24
  %209 = bitcast i8* %208 to float*
  %210 = load float, float* %209, align 4
  %211 = tail call i32 @llvm.smax.i32(i32 %203, i32 0)
  %212 = tail call i32 @llvm.smax.i32(i32 %204, i32 0)
  %213 = fadd reassoc ninf nsz float %202, %201
  %214 = fadd reassoc ninf nsz float %213, %210
  %215 = load float*, float** %32, align 8
  %216 = load i32, i32* %33, align 4
  %217 = load i32, i32* %34, align 4
  %218 = mul i32 %216, %101
  %219 = add i32 %218, %211
  %220 = mul i32 %219, %217
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %215, i64 %221
  %223 = add i32 %220, 1
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %215, i64 %224
  %226 = mul i32 %216, %212
  %227 = add i32 %226, %74
  %228 = mul i32 %227, %217
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %215, i64 %229
  %231 = add i32 %228, 1
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, float* %215, i64 %232
  %234 = mul i32 %216, %115
  %235 = add i32 %234, %211
  %236 = mul i32 %235, %217
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, float* %215, i64 %237
  %239 = add i32 %236, 1
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %215, i64 %240
  %242 = add i32 %226, %86
  %243 = mul i32 %242, %217
  %244 = sext i32 %243 to i64
  %245 = getelementptr float, float* %215, i64 %244
  %246 = add i32 %243, 1
  %247 = sext i32 %246 to i64
  %248 = getelementptr float, float* %215, i64 %247
  br i1 %35, label %for_loop_body4.preheader, label %after_for6

for_loop_body4.preheader:                         ; preds = %after_if3
  br i1 %min.iters.check, label %for_loop_body4.preheader146, label %vector.memcheck

vector.memcheck:                                  ; preds = %for_loop_body4.preheader
  %scevgep = getelementptr float, float* %184, i64 1
  %scevgep25 = getelementptr float, float* %scevgep, i64 %190
  %scevgep27 = getelementptr float, float* %192, i64 1
  %scevgep28 = getelementptr float, float* %scevgep27, i64 %199
  %scevgep30 = getelementptr float, float* %215, i64 1
  %scevgep31 = getelementptr float, float* %scevgep30, i64 %232
  %scevgep34 = getelementptr float, float* %scevgep30, i64 %229
  %scevgep37 = getelementptr float, float* %scevgep30, i64 %247
  %scevgep40 = getelementptr float, float* %scevgep30, i64 %244
  %scevgep43 = getelementptr float, float* %scevgep30, i64 %224
  %scevgep46 = getelementptr float, float* %scevgep30, i64 %221
  %scevgep49 = getelementptr float, float* %scevgep30, i64 %240
  %scevgep52 = getelementptr float, float* %scevgep30, i64 %237
  %bound0 = icmp ult float* %191, %scevgep28
  %bound1 = icmp ult float* %200, %scevgep25
  %found.conflict = and i1 %bound0, %bound1
  %bound054 = icmp ult float* %191, %scevgep31
  %bound155 = icmp ult float* %233, %scevgep25
  %found.conflict56 = and i1 %bound054, %bound155
  %conflict.rdx = or i1 %found.conflict, %found.conflict56
  %bound057 = icmp ult float* %191, %scevgep34
  %bound158 = icmp ult float* %230, %scevgep25
  %found.conflict59 = and i1 %bound057, %bound158
  %conflict.rdx60 = or i1 %conflict.rdx, %found.conflict59
  %bound061 = icmp ult float* %191, %scevgep37
  %bound162 = icmp ult float* %248, %scevgep25
  %found.conflict63 = and i1 %bound061, %bound162
  %conflict.rdx64 = or i1 %conflict.rdx60, %found.conflict63
  %bound065 = icmp ult float* %191, %scevgep40
  %bound166 = icmp ult float* %245, %scevgep25
  %found.conflict67 = and i1 %bound065, %bound166
  %conflict.rdx68 = or i1 %conflict.rdx64, %found.conflict67
  %bound069 = icmp ult float* %191, %scevgep43
  %bound170 = icmp ult float* %225, %scevgep25
  %found.conflict71 = and i1 %bound069, %bound170
  %conflict.rdx72 = or i1 %conflict.rdx68, %found.conflict71
  %bound073 = icmp ult float* %191, %scevgep46
  %bound174 = icmp ult float* %222, %scevgep25
  %found.conflict75 = and i1 %bound073, %bound174
  %conflict.rdx76 = or i1 %conflict.rdx72, %found.conflict75
  %bound077 = icmp ult float* %191, %scevgep49
  %bound178 = icmp ult float* %241, %scevgep25
  %found.conflict79 = and i1 %bound077, %bound178
  %conflict.rdx80 = or i1 %conflict.rdx76, %found.conflict79
  %bound081 = icmp ult float* %191, %scevgep52
  %bound182 = icmp ult float* %238, %scevgep25
  %found.conflict83 = and i1 %bound081, %bound182
  %conflict.rdx84 = or i1 %conflict.rdx80, %found.conflict83
  %bound085 = icmp ult float* %200, %scevgep31
  %bound186 = icmp ult float* %233, %scevgep28
  %found.conflict87 = and i1 %bound085, %bound186
  %conflict.rdx88 = or i1 %conflict.rdx84, %found.conflict87
  %bound089 = icmp ult float* %200, %scevgep34
  %bound190 = icmp ult float* %230, %scevgep28
  %found.conflict91 = and i1 %bound089, %bound190
  %conflict.rdx92 = or i1 %conflict.rdx88, %found.conflict91
  %bound093 = icmp ult float* %200, %scevgep37
  %bound194 = icmp ult float* %248, %scevgep28
  %found.conflict95 = and i1 %bound093, %bound194
  %conflict.rdx96 = or i1 %conflict.rdx92, %found.conflict95
  %bound097 = icmp ult float* %200, %scevgep40
  %bound198 = icmp ult float* %245, %scevgep28
  %found.conflict99 = and i1 %bound097, %bound198
  %conflict.rdx100 = or i1 %conflict.rdx96, %found.conflict99
  %bound0101 = icmp ult float* %200, %scevgep43
  %bound1102 = icmp ult float* %225, %scevgep28
  %found.conflict103 = and i1 %bound0101, %bound1102
  %conflict.rdx104 = or i1 %conflict.rdx100, %found.conflict103
  %bound0105 = icmp ult float* %200, %scevgep46
  %bound1106 = icmp ult float* %222, %scevgep28
  %found.conflict107 = and i1 %bound0105, %bound1106
  %conflict.rdx108 = or i1 %conflict.rdx104, %found.conflict107
  %bound0109 = icmp ult float* %200, %scevgep49
  %bound1110 = icmp ult float* %241, %scevgep28
  %found.conflict111 = and i1 %bound0109, %bound1110
  %conflict.rdx112 = or i1 %conflict.rdx108, %found.conflict111
  %bound0113 = icmp ult float* %200, %scevgep52
  %bound1114 = icmp ult float* %238, %scevgep28
  %found.conflict115 = and i1 %bound0113, %bound1114
  %conflict.rdx116 = or i1 %conflict.rdx112, %found.conflict115
  br i1 %conflict.rdx116, label %for_loop_body4.preheader146, label %vector.ph

vector.ph:                                        ; preds = %vector.memcheck
  %broadcast.splatinsert131 = insertelement <8 x float> poison, float %126, i64 0
  %broadcast.splat132 = shufflevector <8 x float> %broadcast.splatinsert131, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert133 = insertelement <8 x float> poison, float %129, i64 0
  %broadcast.splat134 = shufflevector <8 x float> %broadcast.splatinsert133, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert135 = insertelement <8 x float> poison, float %138, i64 0
  %broadcast.splat136 = shufflevector <8 x float> %broadcast.splatinsert135, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert137 = insertelement <8 x float> poison, float %214, i64 0
  %broadcast.splat138 = shufflevector <8 x float> %broadcast.splatinsert137, <8 x float> poison, <8 x i32> zeroinitializer
  %249 = load float, float* %238, align 4, !alias.scope !9
  %250 = load float, float* %241, align 4, !alias.scope !12
  %251 = load float, float* %222, align 4, !alias.scope !14
  %.scalar = fadd reassoc ninf nsz float %251, %249
  %252 = load float, float* %225, align 4, !alias.scope !16
  %.scalar139 = fadd reassoc ninf nsz float %252, %250
  %253 = load float, float* %245, align 4, !alias.scope !18
  %.scalar140 = fadd reassoc ninf nsz float %.scalar, %253
  %254 = load float, float* %248, align 4, !alias.scope !20
  %.scalar141 = fadd reassoc ninf nsz float %.scalar139, %254
  %255 = load float, float* %230, align 4, !alias.scope !22
  %.scalar142 = fadd reassoc ninf nsz float %.scalar140, %255
  %256 = load float, float* %233, align 4, !alias.scope !24
  %.scalar143 = fadd reassoc ninf nsz float %.scalar141, %256
  %.scalar144 = fmul reassoc ninf nsz float %.scalar142, 2.500000e-01
  %257 = insertelement <8 x float> poison, float %.scalar144, i64 0
  %258 = shufflevector <8 x float> %257, <8 x float> poison, <8 x i32> zeroinitializer
  %.scalar145 = fmul reassoc ninf nsz float %.scalar143, 2.500000e-01
  %259 = insertelement <8 x float> poison, float %.scalar145, i64 0
  %260 = shufflevector <8 x float> %259, <8 x float> poison, <8 x i32> zeroinitializer
  %261 = fmul reassoc ninf nsz <8 x float> %258, %broadcast.splat132
  %262 = fmul reassoc ninf nsz <8 x float> %260, %broadcast.splat134
  %263 = fadd reassoc ninf nsz <8 x float> %261, %broadcast.splat136
  %264 = fadd reassoc ninf nsz <8 x float> %263, %262
  %265 = fmul reassoc ninf nsz <8 x float> %264, %broadcast.splat132
  %266 = fdiv reassoc ninf nsz <8 x float> %265, %broadcast.splat138
  %267 = fsub reassoc ninf nsz <8 x float> %258, %266
  %268 = fmul reassoc ninf nsz <8 x float> %264, %broadcast.splat134
  %269 = fdiv reassoc ninf nsz <8 x float> %268, %broadcast.splat138
  %270 = extractelement <8 x float> %267, i64 7
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  br i1 true, label %middle.block, label %vector.body, !llvm.loop !26

middle.block:                                     ; preds = %vector.body
  %271 = fsub reassoc ninf nsz <8 x float> %260, %269
  %272 = extractelement <8 x float> %271, i64 7
  store float %270, float* %191, align 4, !alias.scope !28, !noalias !30
  store float %272, float* %200, align 4, !alias.scope !32, !noalias !33
  br i1 %cmp.n, label %after_for6, label %for_loop_body4.preheader146

for_loop_body4.preheader146:                      ; preds = %middle.block, %vector.memcheck, %for_loop_body4.preheader
  %.022.ph = phi i32 [ 0, %vector.memcheck ], [ 0, %for_loop_body4.preheader ], [ %n.vec, %middle.block ]
  %273 = sub i32 %25, %.022.ph
  br label %for_loop_body4

for_loop_body4:                                   ; preds = %for_loop_body4, %for_loop_body4.preheader146
  %lsr.iv147 = phi i32 [ %273, %for_loop_body4.preheader146 ], [ %lsr.iv.next148, %for_loop_body4 ]
  %274 = load float, float* %238, align 4
  %275 = load float, float* %241, align 4
  %276 = load float, float* %222, align 4
  %277 = fadd reassoc ninf nsz float %276, %274
  %278 = load float, float* %225, align 4
  %279 = fadd reassoc ninf nsz float %278, %275
  %280 = load float, float* %245, align 4
  %281 = fadd reassoc ninf nsz float %277, %280
  %282 = load float, float* %248, align 4
  %283 = fadd reassoc ninf nsz float %279, %282
  %284 = load float, float* %230, align 4
  %285 = fadd reassoc ninf nsz float %281, %284
  %286 = load float, float* %233, align 4
  %287 = fadd reassoc ninf nsz float %283, %286
  %288 = fmul reassoc ninf nsz float %285, 2.500000e-01
  %289 = fmul reassoc ninf nsz float %287, 2.500000e-01
  %290 = fmul reassoc ninf nsz float %288, %126
  %291 = fmul reassoc ninf nsz float %289, %129
  %292 = fadd reassoc ninf nsz float %290, %138
  %293 = fadd reassoc ninf nsz float %292, %291
  %294 = fmul reassoc ninf nsz float %293, %126
  %295 = fdiv reassoc ninf nsz float %294, %214
  %296 = fsub reassoc ninf nsz float %288, %295
  %297 = fmul reassoc ninf nsz float %293, %129
  %298 = fdiv reassoc ninf nsz float %297, %214
  %299 = fsub reassoc ninf nsz float %289, %298
  store float %296, float* %191, align 4
  store float %299, float* %200, align 4
  %lsr.iv.next148 = add i32 %lsr.iv147, -1
  %exitcond.not = icmp eq i32 %lsr.iv.next148, 0
  br i1 %exitcond.not, label %after_for6.loopexit, label %for_loop_body4, !llvm.loop !34

after_for6.loopexit:                              ; preds = %for_loop_body4
  br label %after_for6

after_for6:                                       ; preds = %after_for6.loopexit, %middle.block, %after_if3
  %300 = add nsw i32 %.01123, 1
  %exitcond24.not = icmp eq i32 %300, %19
  br i1 %exitcond24.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.24, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.24**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.24*, %struct.RuntimeContext.24** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.24* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.24* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !37

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
