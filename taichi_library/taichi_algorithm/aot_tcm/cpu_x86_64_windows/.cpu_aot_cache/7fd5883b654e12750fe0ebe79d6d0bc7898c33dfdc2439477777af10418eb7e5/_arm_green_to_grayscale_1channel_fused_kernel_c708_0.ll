; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.66*, void (%struct.RuntimeContext.66*, i8*)*, void (%struct.RuntimeContext.66*, i8*, i32)*, void (%struct.RuntimeContext.66*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.66 = type { i8*, %struct.LLVMRuntime.65*, i32, i64* }
%struct.LLVMRuntime.65 = type { %struct.PreallocatedMemoryChunk.61, %struct.PreallocatedMemoryChunk.61, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.62*], [1024 x %struct.NodeManager.63*], [1024 x i8*], i8*, %struct.RandState.64*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.61 = type { i8*, i8*, i64 }
%struct.ListManager.62 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.65* }
%struct.NodeManager.63 = type { %struct.LLVMRuntime.65*, i32, i32, i32, i32, %struct.ListManager.62*, %struct.ListManager.62*, %struct.ListManager.62*, i32 }
%struct.RandState.64 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_arm_green_to_grayscale_1channel_fused_kernel_c708_0_kernel_0_serial(%struct.RuntimeContext.66* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.66* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 6
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.66, %struct.RuntimeContext.66* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 8
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 12
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 8
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %6, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 20
  %27 = bitcast i8* %26 to i32*
  store i32 %22, i32* %27, align 4
  %28 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %29 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %29, i64 0, i32 9
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 16
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %6, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  store i32 %37, i32* %42, align 4
  %43 = mul i32 %37, %28
  %44 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %6, align 8
  %45 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %44, i64 0, i32 14
  %46 = bitcast i8** %45 to i32**
  %47 = load i32*, i32** %46, align 8
  store i32 %43, i32* %47, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_arm_green_to_grayscale_1channel_fused_kernel_c708_0_kernel_1_range_for(%struct.RuntimeContext.66* %context) local_unnamed_addr #2 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.66* %context, %struct.RuntimeContext.66** %4, align 8
  store void (%struct.RuntimeContext.66*, i8*)* null, void (%struct.RuntimeContext.66*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.66*, i8*, i32)* @function_body, void (%struct.RuntimeContext.66*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.66*, i8*)* null, void (%struct.RuntimeContext.66*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.66, %struct.RuntimeContext.66* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.66* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.66, %struct.RuntimeContext.66* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.66* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
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
  br i1 %30, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  %31 = sub i32 0, %17
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %lsr.iv = phi i32 [ %31, %for_loop_body.preheader ], [ %lsr.iv.next, %after_if3 ]
  %.03776 = phi i32 [ %190, %after_if3 ], [ %17, %for_loop_body.preheader ]
  %32 = load %struct.LLVMRuntime.65*, %struct.LLVMRuntime.65** %3, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.65, %struct.LLVMRuntime.65* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 4
  %36 = bitcast i8* %35 to i32*
  %37 = load i32, i32* %36, align 4
  %38 = sdiv i32 %.03776, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %.03776
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %.03776, 0
  %43 = icmp ne i32 %.03776, %39
  %44 = and i1 %42, %41
  %45 = and i1 %44, %43
  %.neg40 = sext i1 %45 to i32
  %46 = add i32 %38, %.neg40
  %47 = mul i32 %46, %37
  %48 = mul i32 %37, -1
  %49 = mul i32 %48, %46
  %50 = add i32 %.03776, %49
  %51 = sdiv i32 %46, 2
  %52 = icmp slt i32 %46, 0
  %53 = shl nsw i32 %51, 1
  %54 = icmp ne i32 %53, %46
  %55 = and i1 %52, %54
  %.neg41.neg = zext i1 %55 to i32
  %.neg43 = sub nsw i32 %.neg41.neg, %51
  %.neg42 = shl i32 %.neg43, 1
  %56 = sdiv i32 %50, 2
  %57 = icmp slt i32 %50, 0
  %58 = shl nsw i32 %56, 1
  %59 = icmp ne i32 %50, %58
  %60 = and i1 %57, %59
  %.neg44.neg = zext i1 %60 to i32
  %.neg46 = sub nsw i32 %.neg44.neg, %56
  %.neg45 = shl i32 %.neg46, 1
  %61 = sub i32 0, %46
  %62 = icmp eq i32 %.neg42, %61
  %63 = add i32 %lsr.iv, %47
  %.not = icmp eq i32 %63, %.neg45
  %64 = select i1 %.not, i32 %23, i32 %25
  %65 = select i1 %.not, i32 %27, i32 %29
  %66 = select i1 %62, i32 %64, i32 %65
  switch i32 %66, label %false_block2 [
    i32 3, label %true_block1
    i32 1, label %true_block1
  ]

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body, %for_loop_body
  %67 = icmp eq i32 %66, 1
  %68 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %69 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %68, i64 0, i32 0, i32 1
  %70 = load float*, float** %69, align 8
  %71 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %68, i64 0, i32 0, i32 0, i32 1
  %72 = load i32, i32* %71, align 4
  %73 = sub i32 %72, %37
  %74 = mul i32 %73, %46
  %75 = add i32 %.03776, %74
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, float* %70, i64 %76
  %78 = load float, float* %77, align 4
  %79 = getelementptr inbounds i8, i8* %34, i64 8
  %80 = bitcast i8* %79 to float*
  %81 = load float, float* %80, align 4
  %82 = fsub reassoc ninf nsz float %78, %81
  %83 = getelementptr inbounds i8, i8* %34, i64 12
  %84 = bitcast i8* %83 to float*
  %85 = load float, float* %84, align 4
  %86 = fmul reassoc ninf nsz float %82, %85
  %87 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %86, float 0.000000e+00)
  %88 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %87, float 1.000000e+00)
  %89 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %68, i64 0, i32 3
  %90 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %68, i64 0, i32 5
  %.035.in = select i1 %67, float* %89, float* %90
  %.035 = load float, float* %.035.in, align 4
  %91 = fmul reassoc ninf nsz float %88, %.035
  br label %after_if3

false_block2:                                     ; preds = %for_loop_body
  %92 = add i32 %50, -1
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = getelementptr inbounds i8, i8* %34, i64 16
  %95 = bitcast i8* %94 to i32*
  %96 = load i32, i32* %95, align 4
  %97 = add i32 %96, -1
  %98 = add i32 %50, 1
  %99 = tail call i32 @llvm.smin.i32(i32 %97, i32 %98)
  %100 = add i32 %46, -1
  %101 = tail call i32 @llvm.smax.i32(i32 %100, i32 0)
  %102 = getelementptr inbounds i8, i8* %34, i64 20
  %103 = bitcast i8* %102 to i32*
  %104 = load i32, i32* %103, align 4
  %105 = add i32 %104, -1
  %106 = add i32 %46, 1
  %107 = tail call i32 @llvm.smin.i32(i32 %105, i32 %106)
  %108 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %109 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %108, i64 0, i32 0, i32 1
  %110 = load float*, float** %109, align 8
  %111 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %108, i64 0, i32 0, i32 0, i32 1
  %112 = load i32, i32* %111, align 4
  %113 = mul i32 %112, %46
  %114 = getelementptr inbounds i8, i8* %34, i64 8
  %115 = bitcast i8* %114 to float*
  %116 = load float, float* %115, align 4
  %117 = getelementptr inbounds i8, i8* %34, i64 12
  %118 = bitcast i8* %117 to float*
  %119 = load float, float* %118, align 4
  %120 = mul i32 %112, %101
  %121 = mul i32 %112, %107
  %122 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %108, i64 0, i32 3
  %123 = load float, float* %122, align 4
  %124 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %108, i64 0, i32 5
  %125 = load float, float* %124, align 4
  %126 = and i32 %93, 2147483646
  %.not50 = icmp eq i32 %93, %126
  %. = select i1 %.not50, i32 %23, i32 %25
  %.65 = select i1 %.not50, i32 %27, i32 %29
  %127 = sdiv i32 %99, 2
  %128 = icmp slt i32 %99, 0
  %129 = shl nsw i32 %127, 1
  %130 = icmp ne i32 %129, %99
  %131 = and i1 %128, %130
  %.neg52.neg = zext i1 %131 to i32
  %.neg54 = sub nsw i32 %.neg52.neg, %127
  %.neg53 = shl i32 %.neg54, 1
  %132 = sub i32 0, %99
  %.not55 = icmp eq i32 %.neg53, %132
  %.67 = select i1 %.not55, i32 %23, i32 %25
  %.68 = select i1 %.not55, i32 %27, i32 %29
  %133 = and i32 %101, 2147483646
  %134 = icmp eq i32 %101, %133
  %135 = sdiv i32 %107, 2
  %136 = icmp slt i32 %107, 0
  %137 = shl nsw i32 %135, 1
  %138 = icmp ne i32 %137, %107
  %139 = and i1 %136, %138
  %.neg61.neg = zext i1 %139 to i32
  %.neg63 = sub nsw i32 %.neg61.neg, %135
  %.neg62 = shl i32 %.neg63, 1
  %140 = sub i32 0, %107
  %141 = icmp eq i32 %.neg62, %140
  %142 = insertelement <4 x i32> poison, i32 %113, i64 0
  %143 = insertelement <4 x i32> %142, i32 %120, i64 1
  %144 = insertelement <4 x i32> %143, i32 %113, i64 2
  %145 = insertelement <4 x i32> %144, i32 %121, i64 3
  %146 = insertelement <4 x i32> poison, i32 %93, i64 0
  %147 = insertelement <4 x i32> %146, i32 %50, i64 1
  %148 = insertelement <4 x i32> %147, i32 %99, i64 2
  %149 = insertelement <4 x i32> %148, i32 %50, i64 3
  %150 = add <4 x i32> %145, %149
  %151 = sext <4 x i32> %150 to <4 x i64>
  %152 = insertelement <4 x float*> poison, float* %110, i64 0
  %shuffle88 = shufflevector <4 x float*> %152, <4 x float*> poison, <4 x i32> zeroinitializer
  %153 = getelementptr float, <4 x float*> %shuffle88, <4 x i64> %151
  %154 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %153, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %155 = insertelement <4 x float> poison, float %116, i64 0
  %shuffle89 = shufflevector <4 x float> %155, <4 x float> poison, <4 x i32> zeroinitializer
  %156 = fsub reassoc ninf nsz <4 x float> %154, %shuffle89
  %157 = insertelement <4 x float> poison, float %119, i64 0
  %shuffle90 = shufflevector <4 x float> %157, <4 x float> poison, <4 x i32> zeroinitializer
  %158 = fmul reassoc ninf nsz <4 x float> %156, %shuffle90
  %159 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %158, <4 x float> zeroinitializer)
  %160 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %159, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %161 = insertelement <4 x i1> poison, i1 %62, i64 0
  %162 = insertelement <4 x i1> %161, i1 %134, i64 1
  %163 = insertelement <4 x i1> %162, i1 %62, i64 2
  %164 = insertelement <4 x i1> %163, i1 %141, i64 3
  %165 = insertelement <4 x i32> poison, i32 %., i64 0
  %166 = insertelement <4 x i32> %165, i32 %64, i64 1
  %167 = insertelement <4 x i32> %166, i32 %.67, i64 2
  %168 = insertelement <4 x i32> %167, i32 %64, i64 3
  %169 = insertelement <4 x i32> poison, i32 %.65, i64 0
  %170 = insertelement <4 x i32> %169, i32 %65, i64 1
  %171 = insertelement <4 x i32> %170, i32 %.68, i64 2
  %172 = insertelement <4 x i32> %171, i32 %65, i64 3
  %173 = select <4 x i1> %164, <4 x i32> %168, <4 x i32> %172
  %174 = icmp eq <4 x i32> %173, <i32 1, i32 1, i32 1, i32 1>
  %175 = insertelement <4 x float> poison, float %123, i64 0
  %shuffle = shufflevector <4 x float> %175, <4 x float> poison, <4 x i32> zeroinitializer
  %176 = insertelement <4 x float> poison, float %125, i64 0
  %shuffle87 = shufflevector <4 x float> %176, <4 x float> poison, <4 x i32> zeroinitializer
  %177 = select <4 x i1> %174, <4 x float> %shuffle, <4 x float> %shuffle87
  %178 = fmul reassoc ninf nsz <4 x float> %177, %160
  %179 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %178)
  %180 = fmul reassoc ninf nsz float %179, 2.500000e-01
  br label %after_if3

after_if3:                                        ; preds = %false_block2, %true_block1
  %.sink86 = phi { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* [ %108, %false_block2 ], [ %68, %true_block1 ]
  %.sink = phi float [ %180, %false_block2 ], [ %91, %true_block1 ]
  %181 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink86, i64 0, i32 1, i32 1
  %182 = load float*, float** %181, align 8
  %183 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink86, i64 0, i32 1, i32 0, i32 1
  %184 = load i32, i32* %183, align 4
  %185 = sub i32 %184, %37
  %186 = mul i32 %185, %46
  %187 = add i32 %.03776, %186
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, float* %182, i64 %188
  store float %.sink, float* %189, align 4
  %190 = add nsw i32 %.03776, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %19, %190
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.66, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.66**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.66*, %struct.RuntimeContext.66** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.66*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.66*, i8*)*, void (%struct.RuntimeContext.66*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.66*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.66*, i8*, i32)*, void (%struct.RuntimeContext.66*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.66*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.66*, i8*)*, void (%struct.RuntimeContext.66*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.66*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.66* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.66* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.66* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.66, %struct.RuntimeContext.66* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.66* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.66* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.66*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.66* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
