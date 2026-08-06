; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.78*, void (%struct.RuntimeContext.78*, i8*)*, void (%struct.RuntimeContext.78*, i8*, i32)*, void (%struct.RuntimeContext.78*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.78 = type { i8*, %struct.LLVMRuntime.77*, i32, i64* }
%struct.LLVMRuntime.77 = type { %struct.PreallocatedMemoryChunk.73, %struct.PreallocatedMemoryChunk.73, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.74*], [1024 x %struct.NodeManager.75*], [1024 x i8*], i8*, %struct.RandState.76*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.73 = type { i8*, i8*, i64 }
%struct.ListManager.74 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.77* }
%struct.NodeManager.75 = type { %struct.LLVMRuntime.77*, i32, i32, i32, i32, %struct.ListManager.74*, %struct.ListManager.74*, %struct.ListManager.74*, i32 }
%struct.RandState.76 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_mlri_admm_green_half_res_fused_kernel_c92_0_kernel_0_serial(%struct.RuntimeContext.78* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.78* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 6
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.78, %struct.RuntimeContext.78* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 8
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 12
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 8
  %22 = load i32, i32* %21, align 4
  %23 = sdiv i32 %22, 2
  %24 = icmp slt i32 %22, 0
  %25 = shl nsw i32 %23, 1
  %26 = icmp ne i32 %25, %22
  %27 = and i1 %24, %26
  %.neg = sext i1 %27 to i32
  %28 = add nsw i32 %23, %.neg
  %29 = tail call i32 @llvm.smax.i32(i32 %28, i32 0)
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 9
  %31 = load i32, i32* %30, align 4
  %32 = sdiv i32 %31, 2
  %33 = icmp slt i32 %31, 0
  %34 = shl nsw i32 %32, 1
  %35 = icmp ne i32 %34, %31
  %36 = and i1 %33, %35
  %.neg1 = sext i1 %36 to i32
  %37 = add nsw i32 %32, %.neg1
  %38 = tail call i32 @llvm.smax.i32(i32 %37, i32 0)
  %39 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %6, align 8
  %40 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %39, i64 0, i32 14
  %41 = load i8*, i8** %40, align 8
  %42 = getelementptr inbounds i8, i8* %41, i64 4
  %43 = bitcast i8* %42 to i32*
  store i32 %38, i32* %43, align 4
  %44 = mul i32 %38, %29
  %45 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %6, align 8
  %46 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %45, i64 0, i32 14
  %47 = bitcast i8** %46 to i32**
  %48 = load i32*, i32** %47, align 8
  store i32 %44, i32* %48, align 4
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_mlri_admm_green_half_res_fused_kernel_c92_0_kernel_1_range_for(%struct.RuntimeContext.78* %context) local_unnamed_addr #2 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.78* %context, %struct.RuntimeContext.78** %4, align 8
  store void (%struct.RuntimeContext.78*, i8*)* null, void (%struct.RuntimeContext.78*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.78*, i8*, i32)* @function_body, void (%struct.RuntimeContext.78*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.78*, i8*)* null, void (%struct.RuntimeContext.78*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.78, %struct.RuntimeContext.78* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.78* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.78, %struct.RuntimeContext.78* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %4, i64 0, i32 14
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
  %21 = bitcast %struct.RuntimeContext.78* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %22 = shl i32 %17, 1
  %23 = add nuw nsw i32 %22, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if72, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %23, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if72 ]
  %.06479 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %216, %after_if72 ]
  %24 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %3, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 4
  %28 = bitcast i8* %27 to i32*
  %29 = load i32, i32* %28, align 4
  %30 = sdiv i32 %.06479, %29
  %31 = mul i32 %30, %29
  %32 = xor i32 %29, %.06479
  %33 = icmp slt i32 %32, 0
  %34 = icmp ne i32 %.06479, 0
  %35 = icmp ne i32 %.06479, %31
  %36 = and i1 %34, %33
  %37 = and i1 %36, %35
  %.neg69 = sext i1 %37 to i32
  %38 = add i32 %30, %.neg69
  %39 = mul i32 %38, %29
  %40 = shl i32 %38, 1
  %41 = mul i32 %29, -2
  %42 = mul i32 %41, %38
  %43 = add i32 %lsr.iv, %42
  %44 = add i32 %43, -1
  %45 = sdiv i32 %40, 2
  %46 = icmp slt i32 %40, 0
  %47 = shl nsw i32 %45, 1
  %48 = icmp ne i32 %47, %40
  %49 = and i1 %46, %48
  %.neg70.neg80 = zext i1 %49 to i32
  %.neg76 = sub i32 %38, %45
  %50 = add i32 %.neg76, %.neg70.neg80
  %51 = sdiv i32 %44, 2
  %52 = icmp slt i32 %44, 0
  %53 = shl nsw i32 %51, 1
  %54 = icmp ne i32 %44, %53
  %55 = and i1 %52, %54
  %.neg71.neg81 = zext i1 %55 to i32
  %56 = sub i32 %.neg71.neg81, %39
  %57 = sub i32 %56, %51
  %58 = add i32 %.06479, %57
  %.mask = and i32 %50, 2147483647
  %59 = icmp eq i32 %.mask, 0
  %.mask72 = and i32 %58, 2147483647
  %.not = icmp eq i32 %.mask72, 0
  %60 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  br i1 %59, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if72
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  br i1 %.not, label %true_block1, label %false_block2

false_block:                                      ; preds = %for_loop_body
  br i1 %.not, label %true_block4, label %false_block5

after_if:                                         ; preds = %false_block5, %true_block4, %false_block2, %true_block1
  %.057.in = phi i32* [ %61, %true_block1 ], [ %62, %false_block2 ], [ %63, %true_block4 ], [ %64, %false_block5 ]
  %.057 = load i32, i32* %.057.in, align 4
  switch i32 %.057, label %after_if12 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

true_block1:                                      ; preds = %true_block
  %61 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 10
  br label %after_if

false_block2:                                     ; preds = %true_block
  %62 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 11
  br label %after_if

true_block4:                                      ; preds = %false_block
  %63 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 12
  br label %after_if

false_block5:                                     ; preds = %false_block
  %64 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 13
  br label %after_if

true_block10:                                     ; preds = %after_if, %after_if
  %65 = icmp eq i32 %.057, 1
  %66 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 1
  %67 = load float*, float** %66, align 8
  %68 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 0, i32 1
  %69 = load i32, i32* %68, align 4
  %70 = shl i32 %69, 1
  %71 = shl i32 %29, 1
  %72 = sub i32 %70, %71
  %73 = mul i32 %72, %38
  %74 = add i32 %lsr.iv, %73
  %75 = add i32 %74, -1
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, float* %67, i64 %76
  %78 = load float, float* %77, align 4
  %79 = getelementptr inbounds i8, i8* %26, i64 8
  %80 = bitcast i8* %79 to float*
  %81 = load float, float* %80, align 4
  %82 = fsub reassoc ninf nsz float %78, %81
  %83 = getelementptr inbounds i8, i8* %26, i64 12
  %84 = bitcast i8* %83 to float*
  %85 = load float, float* %84, align 4
  %86 = fmul reassoc ninf nsz float %82, %85
  %87 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %86, float 0.000000e+00)
  %88 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %87, float 1.000000e+00)
  %89 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 3
  %90 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 5
  %.053.in = select i1 %65, float* %89, float* %90
  %.053 = load float, float* %.053.in, align 4
  %91 = fmul reassoc ninf nsz float %88, %.053
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if
  %.060 = phi float [ %91, %true_block10 ], [ 0.000000e+00, %after_if ]
  %.058 = phi float [ 1.000000e+00, %true_block10 ], [ 0.000000e+00, %after_if ]
  %92 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 11
  %93 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 13
  %.052.in = select i1 %59, i32* %92, i32* %93
  %.052 = load i32, i32* %.052.in, align 4
  switch i32 %.052, label %after_if30 [
    i32 3, label %true_block28
    i32 1, label %true_block28
  ]

true_block28:                                     ; preds = %after_if12, %after_if12
  %94 = icmp eq i32 %.052, 1
  %95 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 1
  %96 = load float*, float** %95, align 8
  %97 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 0, i32 1
  %98 = load i32, i32* %97, align 4
  %99 = shl i32 %98, 1
  %100 = shl i32 %29, 1
  %101 = sub i32 %99, %100
  %102 = mul i32 %101, %38
  %103 = add i32 %lsr.iv, %102
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, float* %96, i64 %104
  %106 = load float, float* %105, align 4
  %107 = getelementptr inbounds i8, i8* %26, i64 8
  %108 = bitcast i8* %107 to float*
  %109 = load float, float* %108, align 4
  %110 = fsub reassoc ninf nsz float %106, %109
  %111 = getelementptr inbounds i8, i8* %26, i64 12
  %112 = bitcast i8* %111 to float*
  %113 = load float, float* %112, align 4
  %114 = fmul reassoc ninf nsz float %110, %113
  %115 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %114, float 0.000000e+00)
  %116 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %115, float 1.000000e+00)
  %117 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 3
  %118 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 5
  %.048.in = select i1 %94, float* %117, float* %118
  %.048 = load float, float* %.048.in, align 4
  %119 = fmul reassoc ninf nsz float %116, %.048
  %120 = fadd reassoc ninf nsz float %119, %.060
  %121 = fadd reassoc ninf nsz float %.058, 1.000000e+00
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if12
  %.161 = phi float [ %120, %true_block28 ], [ %.060, %after_if12 ]
  %.159 = phi float [ %121, %true_block28 ], [ %.058, %after_if12 ]
  %122 = or i32 %40, 1
  %123 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 12
  %.146.in = select i1 %.not, i32* %123, i32* %93
  %.146 = load i32, i32* %.146.in, align 4
  switch i32 %.146, label %false_block59 [
    i32 3, label %true_block46
    i32 1, label %true_block46
  ]

true_block46:                                     ; preds = %after_if30, %after_if30
  %124 = icmp eq i32 %.146, 1
  %125 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 1
  %126 = load float*, float** %125, align 8
  %127 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 0, i32 1
  %128 = load i32, i32* %127, align 4
  %129 = mul i32 %128, %122
  %130 = shl i32 %29, 1
  %131 = mul i32 %130, %38
  %132 = sub i32 %129, %131
  %133 = add i32 %lsr.iv, %132
  %134 = add i32 %133, -1
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %126, i64 %135
  %137 = load float, float* %136, align 4
  %138 = getelementptr inbounds i8, i8* %26, i64 8
  %139 = bitcast i8* %138 to float*
  %140 = load float, float* %139, align 4
  %141 = fsub reassoc ninf nsz float %137, %140
  %142 = getelementptr inbounds i8, i8* %26, i64 12
  %143 = bitcast i8* %142 to float*
  %144 = load float, float* %143, align 4
  %145 = fmul reassoc ninf nsz float %141, %144
  %146 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %145, float 0.000000e+00)
  %147 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %146, float 1.000000e+00)
  %148 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 3
  %149 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 5
  %.043.in = select i1 %124, float* %148, float* %149
  %.043 = load float, float* %.043.in, align 4
  %150 = fmul reassoc ninf nsz float %147, %.043
  %151 = fadd reassoc ninf nsz float %150, %.161
  %152 = fadd reassoc ninf nsz float %.159, 1.000000e+00
  br label %false_block59

false_block59:                                    ; preds = %true_block46, %after_if30
  %.262 = phi float [ %151, %true_block46 ], [ %.161, %after_if30 ]
  %.2 = phi float [ %152, %true_block46 ], [ %.159, %after_if30 ]
  %153 = load i32, i32* %93, align 4
  switch i32 %153, label %after_if66 [
    i32 3, label %true_block64
    i32 1, label %true_block64
  ]

true_block64:                                     ; preds = %false_block59, %false_block59
  %154 = icmp eq i32 %153, 1
  %155 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 1
  %156 = load float*, float** %155, align 8
  %157 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 0, i32 1
  %158 = load i32, i32* %157, align 4
  %159 = mul i32 %158, %122
  %160 = shl i32 %29, 1
  %161 = mul i32 %160, %38
  %162 = sub i32 %159, %161
  %163 = add i32 %lsr.iv, %162
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %156, i64 %164
  %166 = load float, float* %165, align 4
  %167 = getelementptr inbounds i8, i8* %26, i64 8
  %168 = bitcast i8* %167 to float*
  %169 = load float, float* %168, align 4
  %170 = fsub reassoc ninf nsz float %166, %169
  %171 = getelementptr inbounds i8, i8* %26, i64 12
  %172 = bitcast i8* %171 to float*
  %173 = load float, float* %172, align 4
  %174 = fmul reassoc ninf nsz float %170, %173
  %175 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %174, float 0.000000e+00)
  %176 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %175, float 1.000000e+00)
  %177 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 3
  %178 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 5
  %.0.in = select i1 %154, float* %177, float* %178
  %.0 = load float, float* %.0.in, align 4
  %179 = fmul reassoc ninf nsz float %176, %.0
  %180 = fadd reassoc ninf nsz float %179, %.262
  %181 = fadd reassoc ninf nsz float %.2, 1.000000e+00
  br label %after_if66

after_if66:                                       ; preds = %true_block64, %false_block59
  %.363 = phi float [ %180, %true_block64 ], [ %.262, %false_block59 ]
  %.3 = phi float [ %181, %true_block64 ], [ %.2, %false_block59 ]
  %182 = fcmp reassoc ninf nsz ogt float %.3, 0.000000e+00
  br i1 %182, label %true_block70, label %false_block71

true_block70:                                     ; preds = %after_if66
  %183 = fdiv reassoc ninf nsz float %.363, %.3
  br label %after_if72

false_block71:                                    ; preds = %after_if66
  %184 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 1
  %185 = load float*, float** %184, align 8
  %186 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 0, i32 0, i32 1
  %187 = load i32, i32* %186, align 4
  %188 = shl i32 %187, 1
  %189 = shl i32 %29, 1
  %190 = sub i32 %188, %189
  %191 = mul i32 %190, %38
  %192 = add i32 %lsr.iv, %191
  %193 = add i32 %192, -1
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %185, i64 %194
  %196 = load float, float* %195, align 4
  %197 = getelementptr inbounds i8, i8* %26, i64 8
  %198 = bitcast i8* %197 to float*
  %199 = load float, float* %198, align 4
  %200 = fsub reassoc ninf nsz float %196, %199
  %201 = getelementptr inbounds i8, i8* %26, i64 12
  %202 = bitcast i8* %201 to float*
  %203 = load float, float* %202, align 4
  %204 = fmul reassoc ninf nsz float %200, %203
  %205 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %204, float 0.000000e+00)
  %206 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %205, float 1.000000e+00)
  br label %after_if72

after_if72:                                       ; preds = %false_block71, %true_block70
  %.sink = phi float [ %206, %false_block71 ], [ %183, %true_block70 ]
  %207 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 1, i32 1
  %208 = load float*, float** %207, align 8
  %209 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %60, i64 0, i32 1, i32 0, i32 1
  %210 = load i32, i32* %209, align 4
  %211 = sub i32 %210, %29
  %212 = mul i32 %211, %38
  %213 = add i32 %.06479, %212
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, float* %208, i64 %214
  store float %.sink, float* %215, align 4
  %216 = add nsw i32 %.06479, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %216
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.78, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.78**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.78*, %struct.RuntimeContext.78** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.78*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.78*, i8*)*, void (%struct.RuntimeContext.78*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.78*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.78*, i8*, i32)*, void (%struct.RuntimeContext.78*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.78*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.78*, i8*)*, void (%struct.RuntimeContext.78*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.78*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.78* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.78* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.78* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.78, %struct.RuntimeContext.78* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.78* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.78* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.78*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.78* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #1

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #1

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
