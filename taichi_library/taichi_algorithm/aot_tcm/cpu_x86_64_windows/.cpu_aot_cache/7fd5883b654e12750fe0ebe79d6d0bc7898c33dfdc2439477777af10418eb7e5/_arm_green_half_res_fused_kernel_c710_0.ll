; ModuleID = 'kernel'
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
define void @_arm_green_half_res_fused_kernel_c710_0_kernel_0_serial(%struct.RuntimeContext.78* nocapture readonly %context) local_unnamed_addr #0 {
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

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_arm_green_half_res_fused_kernel_c710_0_kernel_1_range_for(%struct.RuntimeContext.78* %context) local_unnamed_addr #2 {
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
  %20 = bitcast %struct.RuntimeContext.78* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 10
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 11
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 12
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 13
  %29 = load i32, i32* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = icmp eq i32 %29, 1
  %32 = shl i32 %17, 1
  %33 = add nuw nsw i32 %32, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if36, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %33, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if36 ]
  %.03253 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %225, %after_if36 ]
  %34 = load %struct.LLVMRuntime.77*, %struct.LLVMRuntime.77** %3, align 8
  %35 = getelementptr inbounds %struct.LLVMRuntime.77, %struct.LLVMRuntime.77* %34, i64 0, i32 14
  %36 = load i8*, i8** %35, align 8
  %37 = getelementptr inbounds i8, i8* %36, i64 4
  %38 = bitcast i8* %37 to i32*
  %39 = load i32, i32* %38, align 4
  %40 = sdiv i32 %.03253, %39
  %41 = mul i32 %40, %39
  %42 = xor i32 %39, %.03253
  %43 = icmp slt i32 %42, 0
  %44 = icmp ne i32 %.03253, 0
  %45 = icmp ne i32 %.03253, %41
  %46 = and i1 %44, %43
  %47 = and i1 %46, %45
  %.neg41 = sext i1 %47 to i32
  %48 = add i32 %40, %.neg41
  %49 = mul i32 %48, %39
  %50 = shl i32 %48, 1
  %51 = mul i32 %39, -2
  %52 = mul i32 %51, %48
  %53 = add i32 %lsr.iv, %52
  %54 = add i32 %53, -1
  %55 = sdiv i32 %50, 2
  %56 = icmp slt i32 %50, 0
  %57 = shl nsw i32 %55, 1
  %58 = icmp ne i32 %57, %50
  %59 = and i1 %56, %58
  %.neg42.neg54 = zext i1 %59 to i32
  %.neg50 = sub i32 %48, %55
  %60 = add i32 %.neg50, %.neg42.neg54
  %61 = sdiv i32 %54, 2
  %62 = icmp slt i32 %54, 0
  %63 = shl nsw i32 %61, 1
  %64 = icmp ne i32 %54, %63
  %65 = and i1 %62, %64
  %.neg43.neg55 = zext i1 %65 to i32
  %66 = sub i32 %.neg43.neg55, %49
  %67 = sub i32 %66, %61
  %68 = add i32 %.03253, %67
  %.mask = and i32 %60, 2147483647
  %.not = icmp eq i32 %.mask, 0
  %.mask44 = and i32 %68, 2147483647
  %.not45 = icmp eq i32 %.mask44, 0
  %69 = select i1 %.not45, i32 %23, i32 %25
  %70 = select i1 %.not45, i32 %27, i32 %29
  %71 = select i1 %.not, i32 %69, i32 %70
  switch i32 %71, label %after_if3 [
    i32 3, label %true_block1
    i32 1, label %true_block1
  ]

after_for.loopexit:                               ; preds = %after_if36
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body, %for_loop_body
  %72 = icmp eq i32 %71, 1
  %73 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %74 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 0, i32 1
  %75 = load float*, float** %74, align 8
  %76 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 0, i32 0, i32 1
  %77 = load i32, i32* %76, align 4
  %78 = shl i32 %77, 1
  %79 = shl i32 %39, 1
  %80 = sub i32 %78, %79
  %81 = mul i32 %80, %48
  %82 = add i32 %lsr.iv, %81
  %83 = add i32 %82, -1
  %84 = sext i32 %83 to i64
  %85 = getelementptr float, float* %75, i64 %84
  %86 = load float, float* %85, align 4
  %87 = getelementptr inbounds i8, i8* %36, i64 8
  %88 = bitcast i8* %87 to float*
  %89 = load float, float* %88, align 4
  %90 = fsub reassoc ninf nsz float %86, %89
  %91 = getelementptr inbounds i8, i8* %36, i64 12
  %92 = bitcast i8* %91 to float*
  %93 = load float, float* %92, align 4
  %94 = fmul reassoc ninf nsz float %90, %93
  %95 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %94, float 0.000000e+00)
  %96 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %95, float 1.000000e+00)
  %97 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 3
  %98 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 5
  %.025.in = select i1 %72, float* %97, float* %98
  %.025 = load float, float* %.025.in, align 4
  %99 = fmul reassoc ninf nsz float %96, %.025
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %for_loop_body
  %.028 = phi float [ %99, %true_block1 ], [ 0.000000e+00, %for_loop_body ]
  %.027 = phi float [ 1.000000e+00, %true_block1 ], [ 0.000000e+00, %for_loop_body ]
  %100 = select i1 %.not, i32 %25, i32 %29
  switch i32 %100, label %after_if12 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

true_block10:                                     ; preds = %after_if3, %after_if3
  %101 = icmp eq i32 %100, 1
  %102 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %103 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 0, i32 1
  %104 = load float*, float** %103, align 8
  %105 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 0, i32 0, i32 1
  %106 = load i32, i32* %105, align 4
  %107 = shl i32 %106, 1
  %108 = shl i32 %39, 1
  %109 = sub i32 %107, %108
  %110 = mul i32 %109, %48
  %111 = add i32 %lsr.iv, %110
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, float* %104, i64 %112
  %114 = load float, float* %113, align 4
  %115 = getelementptr inbounds i8, i8* %36, i64 8
  %116 = bitcast i8* %115 to float*
  %117 = load float, float* %116, align 4
  %118 = fsub reassoc ninf nsz float %114, %117
  %119 = getelementptr inbounds i8, i8* %36, i64 12
  %120 = bitcast i8* %119 to float*
  %121 = load float, float* %120, align 4
  %122 = fmul reassoc ninf nsz float %118, %121
  %123 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %122, float 0.000000e+00)
  %124 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %123, float 1.000000e+00)
  %125 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 3
  %126 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 5
  %.023.in = select i1 %101, float* %125, float* %126
  %.023 = load float, float* %.023.in, align 4
  %127 = fmul reassoc ninf nsz float %124, %.023
  %128 = fadd reassoc ninf nsz float %127, %.028
  %129 = fadd reassoc ninf nsz float %.027, 1.000000e+00
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if3
  %.129 = phi float [ %128, %true_block10 ], [ %.028, %after_if3 ]
  %.1 = phi float [ %129, %true_block10 ], [ %.027, %after_if3 ]
  %130 = or i32 %50, 1
  switch i32 %70, label %after_if21 [
    i32 3, label %true_block19
    i32 1, label %true_block19
  ]

true_block19:                                     ; preds = %after_if12, %after_if12
  %131 = icmp eq i32 %70, 1
  %132 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %133 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %132, i64 0, i32 0, i32 1
  %134 = load float*, float** %133, align 8
  %135 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %132, i64 0, i32 0, i32 0, i32 1
  %136 = load i32, i32* %135, align 4
  %137 = mul i32 %136, %130
  %138 = shl i32 %39, 1
  %139 = mul i32 %138, %48
  %140 = sub i32 %137, %139
  %141 = add i32 %lsr.iv, %140
  %142 = add i32 %141, -1
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %134, i64 %143
  %145 = load float, float* %144, align 4
  %146 = getelementptr inbounds i8, i8* %36, i64 8
  %147 = bitcast i8* %146 to float*
  %148 = load float, float* %147, align 4
  %149 = fsub reassoc ninf nsz float %145, %148
  %150 = getelementptr inbounds i8, i8* %36, i64 12
  %151 = bitcast i8* %150 to float*
  %152 = load float, float* %151, align 4
  %153 = fmul reassoc ninf nsz float %149, %152
  %154 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %153, float 0.000000e+00)
  %155 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %154, float 1.000000e+00)
  %156 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %132, i64 0, i32 3
  %157 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %132, i64 0, i32 5
  %.021.in = select i1 %131, float* %156, float* %157
  %.021 = load float, float* %.021.in, align 4
  %158 = fmul reassoc ninf nsz float %155, %.021
  %159 = fadd reassoc ninf nsz float %158, %.129
  %160 = fadd reassoc ninf nsz float %.1, 1.000000e+00
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if12
  %.230 = phi float [ %159, %true_block19 ], [ %.129, %after_if12 ]
  %.2 = phi float [ %160, %true_block19 ], [ %.1, %after_if12 ]
  switch i32 %29, label %after_if30 [
    i32 3, label %true_block28
    i32 1, label %true_block28
  ]

true_block28:                                     ; preds = %after_if21, %after_if21
  %161 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %162 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %161, i64 0, i32 0, i32 1
  %163 = load float*, float** %162, align 8
  %164 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %161, i64 0, i32 0, i32 0, i32 1
  %165 = load i32, i32* %164, align 4
  %166 = mul i32 %165, %130
  %167 = shl i32 %39, 1
  %168 = mul i32 %167, %48
  %169 = sub i32 %166, %168
  %170 = add i32 %lsr.iv, %169
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %163, i64 %171
  %173 = load float, float* %172, align 4
  %174 = getelementptr inbounds i8, i8* %36, i64 8
  %175 = bitcast i8* %174 to float*
  %176 = load float, float* %175, align 4
  %177 = fsub reassoc ninf nsz float %173, %176
  %178 = getelementptr inbounds i8, i8* %36, i64 12
  %179 = bitcast i8* %178 to float*
  %180 = load float, float* %179, align 4
  %181 = fmul reassoc ninf nsz float %177, %180
  %182 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %181, float 0.000000e+00)
  %183 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %182, float 1.000000e+00)
  %184 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %161, i64 0, i32 3
  %185 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %161, i64 0, i32 5
  %.0.in = select i1 %31, float* %184, float* %185
  %.0 = load float, float* %.0.in, align 4
  %186 = fmul reassoc ninf nsz float %183, %.0
  %187 = fadd reassoc ninf nsz float %186, %.230
  %188 = fadd reassoc ninf nsz float %.2, 1.000000e+00
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if21
  %.331 = phi float [ %187, %true_block28 ], [ %.230, %after_if21 ]
  %.3 = phi float [ %188, %true_block28 ], [ %.2, %after_if21 ]
  %189 = fcmp reassoc ninf nsz ogt float %.3, 0.000000e+00
  br i1 %189, label %true_block34, label %false_block35

true_block34:                                     ; preds = %after_if30
  %190 = fdiv reassoc ninf nsz float %.331, %.3
  %191 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  br label %after_if36

false_block35:                                    ; preds = %after_if30
  %192 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %193 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %192, i64 0, i32 0, i32 1
  %194 = load float*, float** %193, align 8
  %195 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %192, i64 0, i32 0, i32 0, i32 1
  %196 = load i32, i32* %195, align 4
  %197 = shl i32 %196, 1
  %198 = shl i32 %39, 1
  %199 = sub i32 %197, %198
  %200 = mul i32 %199, %48
  %201 = add i32 %lsr.iv, %200
  %202 = add i32 %201, -1
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, float* %194, i64 %203
  %205 = load float, float* %204, align 4
  %206 = getelementptr inbounds i8, i8* %36, i64 8
  %207 = bitcast i8* %206 to float*
  %208 = load float, float* %207, align 4
  %209 = fsub reassoc ninf nsz float %205, %208
  %210 = getelementptr inbounds i8, i8* %36, i64 12
  %211 = bitcast i8* %210 to float*
  %212 = load float, float* %211, align 4
  %213 = fmul reassoc ninf nsz float %209, %212
  %214 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %213, float 0.000000e+00)
  %215 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %214, float 1.000000e+00)
  br label %after_if36

after_if36:                                       ; preds = %false_block35, %true_block34
  %.sink65 = phi { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* [ %192, %false_block35 ], [ %191, %true_block34 ]
  %.sink = phi float [ %215, %false_block35 ], [ %190, %true_block34 ]
  %216 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink65, i64 0, i32 1, i32 1
  %217 = load float*, float** %216, align 8
  %218 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink65, i64 0, i32 1, i32 0, i32 1
  %219 = load i32, i32* %218, align 4
  %220 = sub i32 %219, %39
  %221 = mul i32 %220, %48
  %222 = add i32 %.03253, %221
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, float* %217, i64 %223
  store float %.sink, float* %224, align 4
  %225 = add nsw i32 %.03253, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %225
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
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

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
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
