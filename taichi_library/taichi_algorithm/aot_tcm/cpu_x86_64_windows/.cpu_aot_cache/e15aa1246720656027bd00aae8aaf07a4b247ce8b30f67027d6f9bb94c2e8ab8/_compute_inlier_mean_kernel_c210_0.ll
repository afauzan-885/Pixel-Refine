; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.30*, void (%struct.RuntimeContext.30*, i8*)*, void (%struct.RuntimeContext.30*, i8*, i32)*, void (%struct.RuntimeContext.30*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.30 = type { i8*, %struct.LLVMRuntime.29*, i32, i64* }
%struct.LLVMRuntime.29 = type { %struct.PreallocatedMemoryChunk.25, %struct.PreallocatedMemoryChunk.25, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.26*], [1024 x %struct.NodeManager.27*], [1024 x i8*], i8*, %struct.RandState.28*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.25 = type { i8*, i8*, i64 }
%struct.ListManager.26 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.29* }
%struct.NodeManager.27 = type { %struct.LLVMRuntime.29*, i32, i32, i32, i32, %struct.ListManager.26*, %struct.ListManager.26*, %struct.ListManager.26*, i32 }
%struct.RandState.28 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_compute_inlier_mean_kernel_c210_0_kernel_0_serial(%struct.RuntimeContext.30* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = getelementptr inbounds %struct.RuntimeContext.30, %struct.RuntimeContext.30* %context, i64 0, i32 1
  %1 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %2 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %1, i64 0, i32 14
  %3 = load i8*, i8** %2, align 8
  %4 = getelementptr inbounds i8, i8* %3, i64 20
  %5 = bitcast i8* %4 to float*
  store float 0.000000e+00, float* %5, align 4
  %6 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %6, i64 0, i32 14
  %8 = load i8*, i8** %7, align 8
  %9 = getelementptr inbounds i8, i8* %8, i64 24
  %10 = bitcast i8* %9 to float*
  store float 0.000000e+00, float* %10, align 4
  %11 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %12 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %11, i64 0, i32 14
  %13 = load i8*, i8** %12, align 8
  %14 = getelementptr inbounds i8, i8* %13, i64 28
  %15 = bitcast i8* %14 to float*
  store float 0.000000e+00, float* %15, align 4
  %16 = bitcast %struct.RuntimeContext.30* %context to { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }**
  %17 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }** %16, align 8
  %18 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %17, i64 0, i32 3
  %19 = load i32, i32* %18, align 4
  %20 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 12
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }** %16, align 8
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %25, i64 0, i32 5
  %27 = load i32, i32* %26, align 4
  %28 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %28, i64 0, i32 14
  %30 = load i8*, i8** %29, align 8
  %31 = getelementptr inbounds i8, i8* %30, i64 8
  %32 = bitcast i8* %31 to i32*
  store i32 %27, i32* %32, align 4
  %33 = add i32 %27, -1
  %34 = add i32 %33, %19
  %35 = sdiv i32 %34, %27
  %36 = mul i32 %35, %27
  %37 = xor i32 %34, %27
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %34, 0
  %40 = icmp ne i32 %36, %34
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg = sext i1 %42 to i32
  %43 = add i32 %35, %.neg
  %44 = tail call i32 @llvm.smax.i32(i32 %43, i32 0)
  %45 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }** %16, align 8
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %45, i64 0, i32 4
  %47 = load i32, i32* %46, align 4
  %48 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %49 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %48, i64 0, i32 14
  %50 = load i8*, i8** %49, align 8
  %51 = getelementptr inbounds i8, i8* %50, i64 16
  %52 = bitcast i8* %51 to i32*
  store i32 %47, i32* %52, align 4
  %53 = add i32 %33, %47
  %54 = sdiv i32 %53, %27
  %55 = mul i32 %54, %27
  %56 = xor i32 %53, %27
  %57 = icmp slt i32 %56, 0
  %58 = icmp ne i32 %53, 0
  %59 = icmp ne i32 %55, %53
  %60 = and i1 %58, %57
  %61 = and i1 %60, %59
  %.neg1 = sext i1 %61 to i32
  %62 = add i32 %54, %.neg1
  %63 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %64 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %65 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %64, i64 0, i32 14
  %66 = load i8*, i8** %65, align 8
  %67 = getelementptr inbounds i8, i8* %66, i64 4
  %68 = bitcast i8* %67 to i32*
  store i32 %63, i32* %68, align 4
  %69 = mul i32 %63, %44
  %70 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %71 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %70, i64 0, i32 14
  %72 = bitcast i8** %71 to i32**
  %73 = load i32*, i32** %72, align 8
  store i32 %69, i32* %73, align 4
  ret void
}

; Function Attrs: nounwind
define void @_compute_inlier_mean_kernel_c210_0_kernel_1_range_for(%struct.RuntimeContext.30* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.30* %context, %struct.RuntimeContext.30** %4, align 8
  store void (%struct.RuntimeContext.30*, i8*)* @function_body, void (%struct.RuntimeContext.30*, i8*)** %2, align 8
  store i64 12, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.30*, i8*, i32)* @function_body.1, void (%struct.RuntimeContext.30*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.30*, i8*)* @function_body.2, void (%struct.RuntimeContext.30*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.30, %struct.RuntimeContext.30* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: argmemonly mustprogress nofree norecurse nosync nounwind willreturn writeonly
define internal void @function_body(%struct.RuntimeContext.30* nocapture readnone %0, i8* nocapture writeonly %1) #2 {
allocs:
  %2 = bitcast i8* %1 to <2 x float>*
  store <2 x float> zeroinitializer, <2 x float>* %2, align 4
  %3 = getelementptr i8, i8* %1, i64 8
  %4 = bitcast i8* %3 to float*
  store float 0.000000e+00, float* %4, align 4
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body.1(%struct.RuntimeContext.30* nocapture readonly %0, i8* nocapture %1, i32 %2) #3 {
allocs:
  %3 = getelementptr i8, i8* %1, i64 4
  %4 = bitcast i8* %1 to float*
  %5 = getelementptr inbounds %struct.RuntimeContext.30, %struct.RuntimeContext.30* %0, i64 0, i32 1
  %6 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %6, i64 0, i32 14
  %8 = bitcast i8** %7 to i32**
  %9 = load i32*, i32** %8, align 8
  %10 = load i32, i32* %9, align 4
  %11 = add i32 %10, 7
  %12 = sdiv i32 %11, 8
  %13 = icmp slt i32 %11, 0
  %14 = shl nsw i32 %12, 3
  %15 = icmp ne i32 %14, %11
  %16 = and i1 %13, %15
  %.neg = sext i1 %16 to i32
  %17 = add nsw i32 %12, %.neg
  %18 = tail call i32 @llvm.smax.i32(i32 %17, i32 512)
  %19 = mul i32 %18, %2
  %20 = add i32 %19, %18
  %21 = tail call i32 @llvm.smin.i32(i32 %10, i32 %20)
  %22 = icmp slt i32 %19, %21
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = bitcast %struct.RuntimeContext.30* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }**
  %24 = bitcast i8* %3 to <2 x float>*
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.047 = phi i32 [ %19, %for_loop_body.lr.ph ], [ %67, %after_if3 ]
  %25 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %5, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  %30 = load i32, i32* %29, align 4
  %31 = sdiv i32 %.047, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.047
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %.047, 0
  %36 = icmp ne i32 %.047, %32
  %37 = and i1 %35, %34
  %38 = and i1 %37, %36
  %.neg6 = sext i1 %38 to i32
  %39 = add i32 %31, %.neg6
  %40 = mul i32 %30, -1
  %41 = mul i32 %40, %39
  %42 = add i32 %.047, %41
  %43 = getelementptr inbounds i8, i8* %27, i64 8
  %44 = bitcast i8* %43 to i32*
  %45 = load i32, i32* %44, align 4
  %46 = mul i32 %39, %45
  %47 = mul i32 %42, %45
  %48 = getelementptr inbounds i8, i8* %27, i64 12
  %49 = bitcast i8* %48 to i32*
  %50 = load i32, i32* %49, align 4
  %51 = icmp slt i32 %46, %50
  br i1 %51, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %52 = getelementptr inbounds i8, i8* %27, i64 16
  %53 = bitcast i8* %52 to i32*
  %54 = load i32, i32* %53, align 4
  %55 = icmp slt i32 %47, %54
  br i1 %55, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %56 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }** %23, align 8
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %56, i64 0, i32 1, i32 1
  %58 = load i32*, i32** %57, align 8
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %56, i64 0, i32 1, i32 0, i32 1
  %60 = load i32, i32* %59, align 4
  %61 = mul i32 %60, %46
  %62 = add i32 %61, %47
  %63 = sext i32 %62 to i64
  %64 = getelementptr i32, i32* %58, i64 %63
  %65 = load i32, i32* %64, align 4
  %66 = icmp eq i32 %65, 1
  br i1 %66, label %true_block4, label %after_if3

after_if3:                                        ; preds = %true_block4, %true_block1, %true_block, %for_loop_body
  %67 = add nsw i32 %.047, 1
  %exitcond.not = icmp eq i32 %21, %67
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %68 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %56, i64 0, i32 0, i32 1
  %69 = load float*, float** %68, align 8
  %70 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %56, i64 0, i32 0, i32 0, i32 1
  %71 = load i32, i32* %70, align 4
  %72 = mul i32 %71, %46
  %73 = add i32 %72, %47
  %74 = shl i32 %73, 1
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, float* %69, i64 %75
  %77 = load float, float* %76, align 4
  %78 = load float, float* %4, align 4
  %79 = fadd reassoc ninf nsz float %78, %77
  store float %79, float* %4, align 4
  %80 = load float*, float** %68, align 8
  %81 = load i32, i32* %70, align 4
  %82 = mul i32 %81, %46
  %83 = add i32 %82, %47
  %84 = shl i32 %83, 1
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, float* %80, i64 %85
  %87 = getelementptr float, float* %86, i64 1
  %88 = load float, float* %87, align 4
  %89 = load <2 x float>, <2 x float>* %24, align 4
  %90 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %88, i64 0
  %91 = fadd reassoc ninf nsz <2 x float> %89, %90
  store <2 x float> %91, <2 x float>* %24, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nofree norecurse nounwind willreturn
define internal void @function_body.2(%struct.RuntimeContext.30* nocapture readonly %0, i8* nocapture readonly %1) #4 {
allocs:
  %2 = bitcast i8* %1 to float*
  %3 = load float, float* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.30, %struct.RuntimeContext.30* %0, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 20
  %9 = bitcast i8* %8 to float*
  %10 = atomicrmw fadd float* %9, float %3 seq_cst, align 4
  %11 = getelementptr i8, i8* %1, i64 4
  %12 = bitcast i8* %11 to float*
  %13 = load float, float* %12, align 4
  %14 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 24
  %18 = bitcast i8* %17 to float*
  %19 = atomicrmw fadd float* %18, float %13 seq_cst, align 4
  %20 = getelementptr i8, i8* %1, i64 8
  %21 = bitcast i8* %20 to float*
  %22 = load float, float* %21, align 4
  %23 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %4, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 28
  %27 = bitcast i8* %26 to float*
  %28 = atomicrmw fadd float* %27, float %22 seq_cst, align 4
  ret void
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_compute_inlier_mean_kernel_c210_0_kernel_2_serial(%struct.RuntimeContext.30* nocapture readonly %context) local_unnamed_addr #5 {
entry:
  %0 = getelementptr inbounds %struct.RuntimeContext.30, %struct.RuntimeContext.30* %context, i64 0, i32 1
  %1 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %2 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %1, i64 0, i32 14
  %3 = load i8*, i8** %2, align 8
  %4 = getelementptr inbounds i8, i8* %3, i64 28
  %5 = bitcast i8* %4 to float*
  %6 = load float, float* %5, align 4
  %7 = fcmp reassoc ninf nsz ogt float %6, 0.000000e+00
  br i1 %7, label %true_block, label %after_if

true_block:                                       ; preds = %entry
  %8 = getelementptr inbounds i8, i8* %3, i64 20
  %9 = bitcast i8* %8 to float*
  %10 = load float, float* %9, align 4
  %11 = fdiv reassoc ninf nsz float %10, %6
  %12 = bitcast %struct.RuntimeContext.30* %context to { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }**
  %13 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }** %12, align 8
  %14 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, i32, i32, i32 }* %13, i64 0, i32 2, i32 1
  %15 = load float*, float** %14, align 8
  store float %11, float* %15, align 4
  %16 = load %struct.LLVMRuntime.29*, %struct.LLVMRuntime.29** %0, align 8
  %17 = getelementptr inbounds %struct.LLVMRuntime.29, %struct.LLVMRuntime.29* %16, i64 0, i32 14
  %18 = load i8*, i8** %17, align 8
  %19 = getelementptr inbounds i8, i8* %18, i64 24
  %20 = bitcast i8* %19 to float*
  %21 = load float, float* %20, align 4
  %22 = fdiv reassoc ninf nsz float %21, %6
  %23 = load float*, float** %14, align 8
  %24 = getelementptr float, float* %23, i64 1
  store float %22, float* %24, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %entry
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #6 {
  %4 = alloca %struct.RuntimeContext.30, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.30**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.30*, %struct.RuntimeContext.30** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.30*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.30*, i8*)*, void (%struct.RuntimeContext.30*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.30*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.30*, i8*, i32)*, void (%struct.RuntimeContext.30*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.30*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.30*, i8*)*, void (%struct.RuntimeContext.30*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.30*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.30* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.30* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.30* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.30, %struct.RuntimeContext.30* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.30* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !9

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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.30* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.30*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.30* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #7

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #8

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #8

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #9

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { argmemonly mustprogress nofree norecurse nosync nounwind willreturn writeonly }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { mustprogress nofree norecurse nounwind willreturn }
attributes #5 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #6 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #7 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #8 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #9 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
!10 = !{!"llvm.loop.mustprogress"}
!11 = distinct !{!11, !10}
