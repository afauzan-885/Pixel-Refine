; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.132*, void (%struct.RuntimeContext.132*, i8*)*, void (%struct.RuntimeContext.132*, i8*, i32)*, void (%struct.RuntimeContext.132*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.132 = type { i8*, %struct.LLVMRuntime.131*, i32, i64* }
%struct.LLVMRuntime.131 = type { %struct.PreallocatedMemoryChunk.127, %struct.PreallocatedMemoryChunk.127, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.128*], [1024 x %struct.NodeManager.129*], [1024 x i8*], i8*, %struct.RandState.130*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.127 = type { i8*, i8*, i64 }
%struct.ListManager.128 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.131* }
%struct.NodeManager.129 = type { %struct.LLVMRuntime.131*, i32, i32, i32, i32, %struct.ListManager.128*, %struct.ListManager.128*, %struct.ListManager.128*, i32 }
%struct.RandState.130 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_dcb_rgb_half_c728_0_kernel_0_serial(%struct.RuntimeContext.132* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.132* %context to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 8
  %3 = load i32, i32* %2, align 4
  %4 = sdiv i32 %3, 2
  %5 = icmp slt i32 %3, 0
  %6 = shl nsw i32 %4, 1
  %7 = icmp ne i32 %6, %3
  %8 = and i1 %5, %7
  %.neg = sext i1 %8 to i32
  %9 = add nsw i32 %4, %.neg
  %10 = tail call i32 @llvm.smax.i32(i32 %9, i32 0)
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 9
  %12 = load i32, i32* %11, align 4
  %13 = sdiv i32 %12, 2
  %14 = icmp slt i32 %12, 0
  %15 = shl nsw i32 %13, 1
  %16 = icmp ne i32 %15, %12
  %17 = and i1 %14, %16
  %.neg1 = sext i1 %17 to i32
  %18 = add nsw i32 %13, %.neg1
  %19 = tail call i32 @llvm.smax.i32(i32 %18, i32 0)
  %20 = getelementptr inbounds %struct.RuntimeContext.132, %struct.RuntimeContext.132* %context, i64 0, i32 1
  %21 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %20, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %21, i64 0, i32 14
  %23 = load i8*, i8** %22, align 8
  %24 = getelementptr inbounds i8, i8* %23, i64 4
  %25 = bitcast i8* %24 to i32*
  store i32 %19, i32* %25, align 4
  %26 = mul i32 %19, %10
  %27 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %20, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %27, i64 0, i32 14
  %29 = bitcast i8** %28 to i32**
  %30 = load i32*, i32** %29, align 8
  store i32 %26, i32* %30, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_rgb_half_c728_0_kernel_1_range_for(%struct.RuntimeContext.132* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.132* %context, %struct.RuntimeContext.132** %4, align 8
  store void (%struct.RuntimeContext.132*, i8*)* null, void (%struct.RuntimeContext.132*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.132*, i8*, i32)* @function_body, void (%struct.RuntimeContext.132*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.132*, i8*)* null, void (%struct.RuntimeContext.132*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.132, %struct.RuntimeContext.132* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.132* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.132, %struct.RuntimeContext.132* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.132* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %25 = load float, float* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %29 = load float, float* %28, align 4
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %31 = load float, float* %30, align 4
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %33 = load float, float* %32, align 4
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 10
  %35 = load i32, i32* %34, align 4
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 11
  %37 = load i32, i32* %36, align 4
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 12
  %39 = load i32, i32* %38, align 4
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 13
  %41 = load i32, i32* %40, align 4
  %42 = fsub reassoc ninf nsz float %25, %23
  %43 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %42, float 1.000000e+00)
  %44 = icmp slt i32 %17, %19
  br i1 %44, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %47 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %49 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %50 = shl i32 %17, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if126, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %50, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if126 ]
  %.081119 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %175, %after_if126 ]
  %51 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %3, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %51, i64 0, i32 14
  %53 = load i8*, i8** %52, align 8
  %54 = getelementptr inbounds i8, i8* %53, i64 4
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = sdiv i32 %.081119, %56
  %58 = mul i32 %57, %56
  %59 = xor i32 %56, %.081119
  %60 = icmp slt i32 %59, 0
  %61 = icmp ne i32 %.081119, 0
  %62 = icmp ne i32 %.081119, %58
  %63 = and i1 %61, %60
  %64 = and i1 %63, %62
  %.neg82 = sext i1 %64 to i32
  %65 = add i32 %57, %.neg82
  %66 = mul i32 %65, %56
  %67 = shl i32 %65, 1
  %68 = mul i32 %56, -2
  %69 = mul i32 %68, %65
  %70 = add i32 %lsr.iv, %69
  %71 = sdiv i32 %67, 2
  %72 = icmp slt i32 %67, 0
  %73 = shl nsw i32 %71, 1
  %74 = icmp ne i32 %73, %67
  %75 = and i1 %72, %74
  %.neg83.neg120 = zext i1 %75 to i32
  %.neg116 = sub i32 %65, %71
  %76 = add i32 %.neg116, %.neg83.neg120
  %.mask = and i32 %76, 2147483647
  %77 = icmp eq i32 %.mask, 0
  %78 = sdiv i32 %70, 2
  %79 = icmp slt i32 %70, 0
  %80 = shl nsw i32 %78, 1
  %81 = icmp ne i32 %70, %80
  %82 = and i1 %79, %81
  %.neg84.neg121 = zext i1 %82 to i32
  %83 = sub i32 %.neg84.neg121, %66
  %84 = sub i32 %83, %78
  %85 = add i32 %.081119, %84
  %.mask85 = and i32 %85, 2147483647
  %.not = icmp eq i32 %.mask85, 0
  %. = select i1 %.not, i32 %35, i32 %37
  %.86 = select i1 %.not, i32 %39, i32 %41
  %.066 = select i1 %77, i32 %., i32 %.86
  %86 = load float*, float** %45, align 8
  %87 = load i32, i32* %46, align 4
  %88 = shl i32 %87, 1
  %89 = shl i32 %56, 1
  %90 = sub i32 %88, %89
  %91 = mul i32 %90, %65
  %92 = add i32 %lsr.iv, %91
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, float* %86, i64 %93
  %95 = load float, float* %94, align 4
  %96 = fsub reassoc ninf nsz float %95, %23
  %97 = fdiv reassoc ninf nsz float %96, %43
  %98 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %97, float 0.000000e+00)
  %99 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %98, float 1.000000e+00)
  switch i32 %.066, label %after_if9 [
    i32 0, label %after_if9.thread91
    i32 2, label %after_if9.thread93
    i32 3, label %after_if9.thread
  ]

after_if9.thread91:                               ; preds = %for_loop_body
  %100 = fmul reassoc ninf nsz float %99, %27
  br label %after_if27

after_for.loopexit:                               ; preds = %after_if126
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if9:                                        ; preds = %for_loop_body
  %101 = fmul reassoc ninf nsz float %99, %29
  br label %after_if27

after_if9.thread93:                               ; preds = %for_loop_body
  %102 = fmul reassoc ninf nsz float %99, %31
  br label %after_if27

after_if9.thread:                                 ; preds = %for_loop_body
  %103 = fmul reassoc ninf nsz float %99, %33
  br label %after_if27

after_if27:                                       ; preds = %after_if9.thread, %after_if9.thread93, %after_if9, %after_if9.thread91
  %.077 = phi float [ 0.000000e+00, %after_if9.thread93 ], [ %100, %after_if9.thread91 ], [ 0.000000e+00, %after_if9 ], [ 0.000000e+00, %after_if9.thread ]
  %.073 = phi float [ 0.000000e+00, %after_if9.thread93 ], [ 0.000000e+00, %after_if9.thread91 ], [ %101, %after_if9 ], [ %103, %after_if9.thread ]
  %.069 = phi float [ %102, %after_if9.thread93 ], [ 0.000000e+00, %after_if9.thread91 ], [ 0.000000e+00, %after_if9 ], [ 0.000000e+00, %after_if9.thread ]
  %.067 = phi float [ 0.000000e+00, %after_if9.thread93 ], [ 0.000000e+00, %after_if9.thread91 ], [ 1.000000e+00, %after_if9 ], [ 1.000000e+00, %after_if9.thread ]
  %spec.select = select i1 %77, i32 %37, i32 %41
  %104 = add i32 %92, 1
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, float* %86, i64 %105
  %107 = load float, float* %106, align 4
  %108 = fsub reassoc ninf nsz float %107, %23
  %109 = fdiv reassoc ninf nsz float %108, %43
  %110 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %109, float 0.000000e+00)
  %111 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %110, float 1.000000e+00)
  switch i32 %spec.select, label %false_block62 [
    i32 0, label %after_if42.thread96
    i32 2, label %after_if42.thread98
    i32 3, label %after_if42.thread
  ]

after_if42.thread96:                              ; preds = %after_if27
  %112 = fmul reassoc ninf nsz float %111, %27
  br label %after_if60

after_if42.thread98:                              ; preds = %after_if27
  %113 = fmul reassoc ninf nsz float %111, %31
  br label %after_if60

after_if42.thread:                                ; preds = %after_if27
  br label %false_block62

after_if60:                                       ; preds = %false_block62, %after_if42.thread98, %after_if42.thread96
  %.178 = phi float [ %.077, %after_if42.thread98 ], [ %.077, %false_block62 ], [ %112, %after_if42.thread96 ]
  %.174 = phi float [ %.073, %after_if42.thread98 ], [ %128, %false_block62 ], [ %.073, %after_if42.thread96 ]
  %.170 = phi float [ %113, %after_if42.thread98 ], [ %.069, %false_block62 ], [ %.069, %after_if42.thread96 ]
  %.168 = phi float [ %.067, %after_if42.thread98 ], [ %129, %false_block62 ], [ %.067, %after_if42.thread96 ]
  %114 = or i32 %67, 1
  %115 = mul i32 %114, %87
  %116 = mul i32 %89, %65
  %117 = sub i32 %115, %116
  %118 = add i32 %lsr.iv, %117
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, float* %86, i64 %119
  %121 = load float, float* %120, align 4
  %122 = fsub reassoc ninf nsz float %121, %23
  %123 = fdiv reassoc ninf nsz float %122, %43
  %124 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %123, float 0.000000e+00)
  %125 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %124, float 1.000000e+00)
  switch i32 %.86, label %false_block95 [
    i32 0, label %after_if75.thread101
    i32 2, label %after_if75.thread103
    i32 3, label %after_if75.thread
  ]

after_if75.thread101:                             ; preds = %after_if60
  %126 = fmul reassoc ninf nsz float %125, %27
  br label %after_if105

false_block62:                                    ; preds = %after_if42.thread, %after_if27
  %.pn = phi float [ %33, %after_if42.thread ], [ %29, %after_if27 ]
  %127 = fmul reassoc ninf nsz float %.pn, %111
  %128 = fadd reassoc ninf nsz float %127, %.073
  %129 = fadd reassoc ninf nsz float %.067, 1.000000e+00
  br label %after_if60

after_if75.thread103:                             ; preds = %after_if60
  %130 = fmul reassoc ninf nsz float %125, %31
  br label %after_if105

after_if75.thread:                                ; preds = %after_if60
  br label %false_block95

false_block95:                                    ; preds = %after_if75.thread, %after_if60
  %.pn113 = phi float [ %33, %after_if75.thread ], [ %29, %after_if60 ]
  %131 = fmul reassoc ninf nsz float %.pn113, %125
  %132 = fadd reassoc ninf nsz float %131, %.174
  %133 = fadd reassoc ninf nsz float %.168, 1.000000e+00
  br label %after_if105

after_if105:                                      ; preds = %false_block95, %after_if75.thread103, %after_if75.thread101
  %.279 = phi float [ %.178, %after_if75.thread103 ], [ %.178, %false_block95 ], [ %126, %after_if75.thread101 ]
  %.275 = phi float [ %.174, %after_if75.thread103 ], [ %132, %false_block95 ], [ %.174, %after_if75.thread101 ]
  %.271 = phi float [ %130, %after_if75.thread103 ], [ %.170, %false_block95 ], [ %.170, %after_if75.thread101 ]
  %.2 = phi float [ %.168, %after_if75.thread103 ], [ %133, %false_block95 ], [ %.168, %after_if75.thread101 ]
  %134 = add i32 %118, 1
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %86, i64 %135
  %137 = load float, float* %136, align 4
  %138 = fsub reassoc ninf nsz float %137, %23
  %139 = fdiv reassoc ninf nsz float %138, %43
  %140 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %139, float 0.000000e+00)
  %141 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %140, float 1.000000e+00)
  switch i32 %41, label %false_block128 [
    i32 0, label %after_if108.thread106
    i32 2, label %after_if108.thread108
    i32 3, label %after_if108.thread
  ]

after_if108.thread106:                            ; preds = %after_if105
  %142 = fmul reassoc ninf nsz float %141, %27
  br label %after_if126

after_if108.thread108:                            ; preds = %after_if105
  %143 = fmul reassoc ninf nsz float %141, %31
  br label %after_if126

after_if108.thread:                               ; preds = %after_if105
  br label %false_block128

after_if126:                                      ; preds = %false_block128, %after_if108.thread108, %after_if108.thread106
  %.380 = phi float [ %.279, %after_if108.thread108 ], [ %.279, %false_block128 ], [ %142, %after_if108.thread106 ]
  %.376 = phi float [ %.275, %after_if108.thread108 ], [ %177, %false_block128 ], [ %.275, %after_if108.thread106 ]
  %.372 = phi float [ %143, %after_if108.thread108 ], [ %.271, %false_block128 ], [ %.271, %after_if108.thread106 ]
  %.3 = phi float [ %.2, %after_if108.thread108 ], [ %178, %false_block128 ], [ %.2, %after_if108.thread106 ]
  %144 = load float*, float** %47, align 8
  %145 = load i32, i32* %48, align 4
  %146 = load i32, i32* %49, align 4
  %147 = sub i32 %145, %56
  %148 = mul i32 %147, %65
  %149 = add i32 %.081119, %148
  %150 = mul i32 %149, %146
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %144, i64 %151
  store float %.380, float* %152, align 4
  %153 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.3, float 1.000000e+00)
  %154 = fdiv reassoc ninf nsz float %.376, %153
  %155 = load float*, float** %47, align 8
  %156 = load i32, i32* %48, align 4
  %157 = load i32, i32* %49, align 4
  %158 = sub i32 %156, %56
  %159 = mul i32 %158, %65
  %160 = add i32 %.081119, %159
  %161 = mul i32 %160, %157
  %162 = add i32 %161, 1
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %155, i64 %163
  store float %154, float* %164, align 4
  %165 = load float*, float** %47, align 8
  %166 = load i32, i32* %48, align 4
  %167 = load i32, i32* %49, align 4
  %168 = sub i32 %166, %56
  %169 = mul i32 %168, %65
  %170 = add i32 %.081119, %169
  %171 = mul i32 %170, %167
  %172 = add i32 %171, 2
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, float* %165, i64 %173
  store float %.372, float* %174, align 4
  %175 = add nsw i32 %.081119, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %175
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

false_block128:                                   ; preds = %after_if108.thread, %after_if105
  %.pn114 = phi float [ %33, %after_if108.thread ], [ %29, %after_if105 ]
  %176 = fmul reassoc ninf nsz float %.pn114, %141
  %177 = fadd reassoc ninf nsz float %176, %.275
  %178 = fadd reassoc ninf nsz float %.2, 1.000000e+00
  br label %after_if126
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.132, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.132**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.132*, %struct.RuntimeContext.132** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.132*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.132*, i8*)*, void (%struct.RuntimeContext.132*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.132*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.132*, i8*, i32)*, void (%struct.RuntimeContext.132*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.132*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.132*, i8*)*, void (%struct.RuntimeContext.132*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.132*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.132* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.132* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.132* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.132, %struct.RuntimeContext.132* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.132* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.132* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.132*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.132* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
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
