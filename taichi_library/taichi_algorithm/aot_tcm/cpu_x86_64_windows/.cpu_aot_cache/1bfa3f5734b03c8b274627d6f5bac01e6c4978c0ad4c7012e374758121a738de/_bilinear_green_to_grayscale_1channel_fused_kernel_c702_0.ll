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
define void @_bilinear_green_to_grayscale_1channel_fused_kernel_c702_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 6
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 8
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 12
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 8
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 20
  %27 = bitcast i8* %26 to i32*
  store i32 %22, i32* %27, align 4
  %28 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %29 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %29, i64 0, i32 9
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 16
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  store i32 %37, i32* %42, align 4
  %43 = mul i32 %37, %28
  %44 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %45 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %44, i64 0, i32 14
  %46 = bitcast i8** %45 to i32**
  %47 = load i32*, i32** %46, align 8
  store i32 %43, i32* %47, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_bilinear_green_to_grayscale_1channel_fused_kernel_c702_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #2 {
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
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %22 = sub i32 0, %17
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if12, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %22, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if12 ]
  %.04583 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %189, %after_if12 ]
  %23 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 4
  %27 = bitcast i8* %26 to i32*
  %28 = load i32, i32* %27, align 4
  %29 = sdiv i32 %.04583, %28
  %30 = mul i32 %29, %28
  %31 = xor i32 %28, %.04583
  %32 = icmp slt i32 %31, 0
  %33 = icmp ne i32 %.04583, 0
  %34 = icmp ne i32 %.04583, %30
  %35 = and i1 %33, %32
  %36 = and i1 %35, %34
  %.neg47 = sext i1 %36 to i32
  %37 = add i32 %29, %.neg47
  %38 = mul i32 %37, %28
  %39 = mul i32 %28, -1
  %40 = mul i32 %39, %37
  %41 = add i32 %.04583, %40
  %42 = sdiv i32 %37, 2
  %43 = icmp slt i32 %37, 0
  %44 = shl nsw i32 %42, 1
  %45 = icmp ne i32 %44, %37
  %46 = and i1 %43, %45
  %.neg48.neg = zext i1 %46 to i32
  %.neg50 = sub nsw i32 %.neg48.neg, %42
  %.neg49 = shl i32 %.neg50, 1
  %47 = sdiv i32 %41, 2
  %48 = icmp slt i32 %41, 0
  %49 = shl nsw i32 %47, 1
  %50 = icmp ne i32 %41, %49
  %51 = and i1 %48, %50
  %.neg51.neg = zext i1 %51 to i32
  %.neg53 = sub nsw i32 %.neg51.neg, %47
  %.neg52 = shl i32 %.neg53, 1
  %52 = sub i32 0, %37
  %53 = icmp eq i32 %.neg49, %52
  %54 = add i32 %lsr.iv, %38
  %.not = icmp eq i32 %54, %.neg52
  %55 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  br i1 %53, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if12
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  br i1 %.not, label %true_block1, label %false_block2

false_block:                                      ; preds = %for_loop_body
  br i1 %.not, label %true_block4, label %false_block5

after_if:                                         ; preds = %false_block5, %true_block4, %false_block2, %true_block1
  %.044.in = phi i32* [ %56, %true_block1 ], [ %57, %false_block2 ], [ %58, %true_block4 ], [ %59, %false_block5 ]
  %.044 = load i32, i32* %.044.in, align 4
  switch i32 %.044, label %false_block11 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

true_block1:                                      ; preds = %true_block
  %56 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 10
  br label %after_if

false_block2:                                     ; preds = %true_block
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 11
  br label %after_if

true_block4:                                      ; preds = %false_block
  %58 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 12
  br label %after_if

false_block5:                                     ; preds = %false_block
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 13
  br label %after_if

true_block10:                                     ; preds = %after_if, %after_if
  %60 = icmp eq i32 %.044, 1
  %61 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 0, i32 1
  %62 = load float*, float** %61, align 8
  %63 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 0, i32 0, i32 1
  %64 = load i32, i32* %63, align 4
  %65 = sub i32 %64, %28
  %66 = mul i32 %65, %37
  %67 = add i32 %.04583, %66
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, float* %62, i64 %68
  %70 = load float, float* %69, align 4
  %71 = getelementptr inbounds i8, i8* %25, i64 8
  %72 = bitcast i8* %71 to float*
  %73 = load float, float* %72, align 4
  %74 = fsub reassoc ninf nsz float %70, %73
  %75 = getelementptr inbounds i8, i8* %25, i64 12
  %76 = bitcast i8* %75 to float*
  %77 = load float, float* %76, align 4
  %78 = fmul reassoc ninf nsz float %74, %77
  %79 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %78, float 0.000000e+00)
  %80 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %79, float 1.000000e+00)
  %81 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 3
  %82 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 5
  %.040.in = select i1 %60, float* %81, float* %82
  %.040 = load float, float* %.040.in, align 4
  %83 = fmul reassoc ninf nsz float %80, %.040
  br label %after_if12

false_block11:                                    ; preds = %after_if
  %84 = add i32 %41, -1
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %86 = getelementptr inbounds i8, i8* %25, i64 16
  %87 = bitcast i8* %86 to i32*
  %88 = load i32, i32* %87, align 4
  %89 = add i32 %88, -1
  %90 = add i32 %41, 1
  %91 = tail call i32 @llvm.smin.i32(i32 %89, i32 %90)
  %92 = add i32 %37, -1
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = getelementptr inbounds i8, i8* %25, i64 20
  %95 = bitcast i8* %94 to i32*
  %96 = load i32, i32* %95, align 4
  %97 = add i32 %96, -1
  %98 = add i32 %37, 1
  %99 = tail call i32 @llvm.smin.i32(i32 %97, i32 %98)
  %100 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 0, i32 1
  %101 = load float*, float** %100, align 8
  %102 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 0, i32 0, i32 1
  %103 = load i32, i32* %102, align 4
  %104 = mul i32 %103, %37
  %105 = getelementptr inbounds i8, i8* %25, i64 8
  %106 = bitcast i8* %105 to float*
  %107 = load float, float* %106, align 4
  %108 = getelementptr inbounds i8, i8* %25, i64 12
  %109 = bitcast i8* %108 to float*
  %110 = load float, float* %109, align 4
  %111 = mul i32 %103, %93
  %112 = mul i32 %103, %99
  %113 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 10
  %114 = load i32, i32* %113, align 4
  %115 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 11
  %116 = load i32, i32* %115, align 4
  %117 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 12
  %118 = load i32, i32* %117, align 4
  %119 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 13
  %120 = load i32, i32* %119, align 4
  %121 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 3
  %122 = load float, float* %121, align 4
  %123 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 5
  %124 = load float, float* %123, align 4
  %125 = and i32 %85, 2147483646
  %.not57 = icmp eq i32 %85, %125
  %. = select i1 %.not57, i32 %114, i32 %116
  %.72 = select i1 %.not57, i32 %118, i32 %120
  %126 = sdiv i32 %91, 2
  %127 = icmp slt i32 %91, 0
  %128 = shl nsw i32 %126, 1
  %129 = icmp ne i32 %128, %91
  %130 = and i1 %127, %129
  %.neg59.neg = zext i1 %130 to i32
  %.neg61 = sub nsw i32 %.neg59.neg, %126
  %.neg60 = shl i32 %.neg61, 1
  %131 = sub i32 0, %91
  %.not62 = icmp eq i32 %.neg60, %131
  %.74 = select i1 %.not62, i32 %114, i32 %116
  %.75 = select i1 %.not62, i32 %118, i32 %120
  %132 = and i32 %93, 2147483646
  %133 = icmp eq i32 %93, %132
  %.77 = select i1 %.not, i32 %114, i32 %116
  %.78 = select i1 %.not, i32 %118, i32 %120
  %134 = sdiv i32 %99, 2
  %135 = icmp slt i32 %99, 0
  %136 = shl nsw i32 %134, 1
  %137 = icmp ne i32 %136, %99
  %138 = and i1 %135, %137
  %.neg68.neg = zext i1 %138 to i32
  %.neg70 = sub nsw i32 %.neg68.neg, %134
  %.neg69 = shl i32 %.neg70, 1
  %139 = sub i32 0, %99
  %140 = icmp eq i32 %.neg69, %139
  %141 = insertelement <4 x i32> poison, i32 %104, i64 0
  %142 = insertelement <4 x i32> %141, i32 %104, i64 1
  %143 = insertelement <4 x i32> %142, i32 %111, i64 2
  %144 = insertelement <4 x i32> %143, i32 %112, i64 3
  %145 = insertelement <4 x i32> poison, i32 %91, i64 0
  %146 = insertelement <4 x i32> %145, i32 %85, i64 1
  %147 = insertelement <4 x i32> %146, i32 %41, i64 2
  %148 = insertelement <4 x i32> %147, i32 %41, i64 3
  %149 = add <4 x i32> %144, %148
  %150 = sext <4 x i32> %149 to <4 x i64>
  %151 = insertelement <4 x float*> poison, float* %101, i64 0
  %shuffle93 = shufflevector <4 x float*> %151, <4 x float*> poison, <4 x i32> zeroinitializer
  %152 = getelementptr float, <4 x float*> %shuffle93, <4 x i64> %150
  %153 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %152, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %154 = insertelement <4 x float> poison, float %107, i64 0
  %shuffle94 = shufflevector <4 x float> %154, <4 x float> poison, <4 x i32> zeroinitializer
  %155 = fsub reassoc ninf nsz <4 x float> %153, %shuffle94
  %156 = insertelement <4 x float> poison, float %110, i64 0
  %shuffle95 = shufflevector <4 x float> %156, <4 x float> poison, <4 x i32> zeroinitializer
  %157 = fmul reassoc ninf nsz <4 x float> %155, %shuffle95
  %158 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %157, <4 x float> zeroinitializer)
  %159 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %158, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %160 = insertelement <4 x i1> poison, i1 %53, i64 0
  %161 = insertelement <4 x i1> %160, i1 %53, i64 1
  %162 = insertelement <4 x i1> %161, i1 %133, i64 2
  %163 = insertelement <4 x i1> %162, i1 %140, i64 3
  %164 = insertelement <4 x i32> poison, i32 %.74, i64 0
  %165 = insertelement <4 x i32> %164, i32 %., i64 1
  %166 = insertelement <4 x i32> %165, i32 %.77, i64 2
  %167 = insertelement <4 x i32> %166, i32 %.77, i64 3
  %168 = insertelement <4 x i32> poison, i32 %.75, i64 0
  %169 = insertelement <4 x i32> %168, i32 %.72, i64 1
  %170 = insertelement <4 x i32> %169, i32 %.78, i64 2
  %171 = insertelement <4 x i32> %170, i32 %.78, i64 3
  %172 = select <4 x i1> %163, <4 x i32> %167, <4 x i32> %171
  %173 = icmp eq <4 x i32> %172, <i32 1, i32 1, i32 1, i32 1>
  %174 = insertelement <4 x float> poison, float %122, i64 0
  %shuffle = shufflevector <4 x float> %174, <4 x float> poison, <4 x i32> zeroinitializer
  %175 = insertelement <4 x float> poison, float %124, i64 0
  %shuffle92 = shufflevector <4 x float> %175, <4 x float> poison, <4 x i32> zeroinitializer
  %176 = select <4 x i1> %173, <4 x float> %shuffle, <4 x float> %shuffle92
  %177 = fmul reassoc ninf nsz <4 x float> %176, %159
  %178 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %177)
  %179 = fmul reassoc ninf nsz float %178, 2.500000e-01
  br label %after_if12

after_if12:                                       ; preds = %false_block11, %true_block10
  %.sink = phi float [ %179, %false_block11 ], [ %83, %true_block10 ]
  %180 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 1, i32 1
  %181 = load float*, float** %180, align 8
  %182 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %55, i64 0, i32 1, i32 0, i32 1
  %183 = load i32, i32* %182, align 4
  %184 = sub i32 %183, %28
  %185 = mul i32 %184, %37
  %186 = add i32 %.04583, %185
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, float* %181, i64 %187
  store float %.sink, float* %188, align 4
  %189 = add nsw i32 %.04583, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %19, %189
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #1

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.maxnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.minnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
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
!10 = !{!"llvm.loop.mustprogress"}
!11 = distinct !{!11, !10}
