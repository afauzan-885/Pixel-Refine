; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.48*, void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.48 = type { i8*, %struct.LLVMRuntime.47*, i32, i64* }
%struct.LLVMRuntime.47 = type { %struct.PreallocatedMemoryChunk.43, %struct.PreallocatedMemoryChunk.43, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.44*], [1024 x %struct.NodeManager.45*], [1024 x i8*], i8*, %struct.RandState.46*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.43 = type { i8*, i8*, i64 }
%struct.ListManager.44 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.47* }
%struct.NodeManager.45 = type { %struct.LLVMRuntime.47*, i32, i32, i32, i32, %struct.ListManager.44*, %struct.ListManager.44*, %struct.ListManager.44*, i32 }
%struct.RandState.46 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_bilinear_rgb_half_res_fused_kernel_c706_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 8
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 8
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 12
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 9
  %22 = load i32, i32* %21, align 4
  %23 = sdiv i32 %22, 2
  %24 = icmp slt i32 %22, 0
  %25 = shl nsw i32 %23, 1
  %26 = icmp ne i32 %25, %22
  %27 = and i1 %24, %26
  %.neg = sext i1 %27 to i32
  %28 = add nsw i32 %23, %.neg
  %29 = tail call i32 @llvm.smax.i32(i32 %28, i32 0)
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 10
  %31 = load i32, i32* %30, align 4
  %32 = sdiv i32 %31, 2
  %33 = icmp slt i32 %31, 0
  %34 = shl nsw i32 %32, 1
  %35 = icmp ne i32 %34, %31
  %36 = and i1 %33, %35
  %.neg1 = sext i1 %36 to i32
  %37 = add nsw i32 %32, %.neg1
  %38 = tail call i32 @llvm.smax.i32(i32 %37, i32 0)
  %39 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %40 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %39, i64 0, i32 14
  %41 = load i8*, i8** %40, align 8
  %42 = getelementptr inbounds i8, i8* %41, i64 4
  %43 = bitcast i8* %42 to i32*
  store i32 %38, i32* %43, align 4
  %44 = mul i32 %38, %29
  %45 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %46 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %45, i64 0, i32 14
  %47 = bitcast i8** %46 to i32**
  %48 = load i32*, i32** %47, align 8
  store i32 %44, i32* %48, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_bilinear_rgb_half_res_fused_kernel_c706_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #2 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.48* %context, %struct.RuntimeContext.48** %4, align 8
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.48*, i8*, i32)* @function_body, void (%struct.RuntimeContext.48*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.48* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 11
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 12
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 13
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 14
  %29 = load i32, i32* %28, align 4
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %31 = load float, float* %30, align 4
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %33 = load float, float* %32, align 4
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %35 = load float, float* %34, align 4
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %37 = load float, float* %36, align 4
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %39 = load float*, float** %38, align 8
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %41 = load i32, i32* %40, align 4
  %42 = getelementptr float, float* %39, i64 1
  %43 = getelementptr float, float* %39, i64 2
  %44 = sext i32 %41 to i64
  %45 = getelementptr float, float* %39, i64 %44
  %46 = add i32 %41, 1
  %47 = sext i32 %46 to i64
  %48 = getelementptr float, float* %39, i64 %47
  %49 = add i32 %41, 2
  %50 = sext i32 %49 to i64
  %51 = getelementptr float, float* %39, i64 %50
  %52 = shl i32 %41, 1
  %53 = sext i32 %52 to i64
  %54 = getelementptr float, float* %39, i64 %53
  %55 = getelementptr float, float* %54, i64 1
  %56 = add i32 %52, 2
  %57 = sext i32 %56 to i64
  %58 = getelementptr float, float* %39, i64 %57
  %59 = icmp slt i32 %17, %19
  br i1 %59, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %60 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %61 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %62 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %63 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %64 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 2
  %65 = shl i32 %17, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if27, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %65, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if27 ]
  %.01930 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %263, %after_if27 ]
  %66 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %67 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %66, i64 0, i32 14
  %68 = load i8*, i8** %67, align 8
  %69 = getelementptr inbounds i8, i8* %68, i64 4
  %70 = bitcast i8* %69 to i32*
  %71 = load i32, i32* %70, align 4
  %72 = sdiv i32 %.01930, %71
  %73 = mul i32 %72, %71
  %74 = xor i32 %71, %.01930
  %75 = icmp slt i32 %74, 0
  %76 = icmp ne i32 %.01930, 0
  %77 = icmp ne i32 %.01930, %73
  %78 = and i1 %76, %75
  %79 = and i1 %78, %77
  %.neg24 = sext i1 %79 to i32
  %80 = add i32 %72, %.neg24
  %81 = shl i32 %80, 1
  %82 = load float*, float** %60, align 8
  %83 = load i32, i32* %61, align 4
  %84 = shl i32 %83, 1
  %85 = shl i32 %71, 1
  %86 = sub i32 %84, %85
  %87 = mul i32 %86, %80
  %88 = add i32 %lsr.iv, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, float* %82, i64 %89
  %91 = load float, float* %90, align 4
  %92 = getelementptr inbounds i8, i8* %68, i64 8
  %93 = bitcast i8* %92 to float*
  %94 = load float, float* %93, align 4
  %95 = fsub reassoc ninf nsz float %91, %94
  %96 = getelementptr inbounds i8, i8* %68, i64 12
  %97 = bitcast i8* %96 to float*
  %98 = load float, float* %97, align 4
  %99 = fmul reassoc ninf nsz float %95, %98
  %100 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %99, float 0.000000e+00)
  %101 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %100, float 1.000000e+00)
  %102 = add i32 %88, 1
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %82, i64 %103
  %105 = load float, float* %104, align 4
  %106 = fsub reassoc ninf nsz float %105, %94
  %107 = fmul reassoc ninf nsz float %106, %98
  %108 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %107, float 0.000000e+00)
  %109 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %108, float 1.000000e+00)
  %110 = or i32 %81, 1
  %111 = mul i32 %110, %83
  %112 = mul i32 %85, %80
  %113 = sub i32 %111, %112
  %114 = add i32 %lsr.iv, %113
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, float* %82, i64 %115
  %117 = load float, float* %116, align 4
  %118 = fsub reassoc ninf nsz float %117, %94
  %119 = fmul reassoc ninf nsz float %118, %98
  %120 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %119, float 0.000000e+00)
  %121 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %120, float 1.000000e+00)
  %122 = add i32 %114, 1
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, float* %82, i64 %123
  %125 = load float, float* %124, align 4
  %126 = fsub reassoc ninf nsz float %125, %94
  %127 = fmul reassoc ninf nsz float %126, %98
  %128 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %127, float 0.000000e+00)
  %129 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %128, float 1.000000e+00)
  switch i32 %23, label %false_block5 [
    i32 0, label %after_if
    i32 1, label %true_block1
    i32 2, label %true_block4
  ]

after_for.loopexit:                               ; preds = %after_if27
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %false_block5, %true_block4, %true_block1, %for_loop_body
  %.015 = phi float [ 0.000000e+00, %true_block1 ], [ 0.000000e+00, %true_block4 ], [ 0.000000e+00, %false_block5 ], [ %101, %for_loop_body ]
  %.011 = phi float [ %101, %true_block1 ], [ 0.000000e+00, %true_block4 ], [ 0.000000e+00, %false_block5 ], [ 0.000000e+00, %for_loop_body ]
  %.07 = phi float [ 0.000000e+00, %true_block1 ], [ %101, %true_block4 ], [ 0.000000e+00, %false_block5 ], [ 0.000000e+00, %for_loop_body ]
  %.0 = phi float [ 0.000000e+00, %true_block1 ], [ 0.000000e+00, %true_block4 ], [ %101, %false_block5 ], [ 0.000000e+00, %for_loop_body ]
  switch i32 %25, label %false_block14 [
    i32 0, label %after_if9
    i32 1, label %true_block10
    i32 2, label %true_block13
  ]

true_block1:                                      ; preds = %for_loop_body
  br label %after_if

true_block4:                                      ; preds = %for_loop_body
  br label %after_if

false_block5:                                     ; preds = %for_loop_body
  br label %after_if

after_if9:                                        ; preds = %false_block14, %true_block13, %true_block10, %after_if
  %.116 = phi float [ %.015, %true_block10 ], [ %.015, %true_block13 ], [ %.015, %false_block14 ], [ %109, %after_if ]
  %.112 = phi float [ %109, %true_block10 ], [ %.011, %true_block13 ], [ %.011, %false_block14 ], [ %.011, %after_if ]
  %.18 = phi float [ %.07, %true_block10 ], [ %109, %true_block13 ], [ %.07, %false_block14 ], [ %.07, %after_if ]
  %.1 = phi float [ %.0, %true_block10 ], [ %.0, %true_block13 ], [ %109, %false_block14 ], [ %.0, %after_if ]
  switch i32 %27, label %false_block23 [
    i32 0, label %after_if18
    i32 1, label %true_block19
    i32 2, label %true_block22
  ]

true_block10:                                     ; preds = %after_if
  br label %after_if9

true_block13:                                     ; preds = %after_if
  br label %after_if9

false_block14:                                    ; preds = %after_if
  br label %after_if9

after_if18:                                       ; preds = %false_block23, %true_block22, %true_block19, %after_if9
  %.217 = phi float [ %.116, %true_block19 ], [ %.116, %true_block22 ], [ %.116, %false_block23 ], [ %121, %after_if9 ]
  %.213 = phi float [ %121, %true_block19 ], [ %.112, %true_block22 ], [ %.112, %false_block23 ], [ %.112, %after_if9 ]
  %.29 = phi float [ %.18, %true_block19 ], [ %121, %true_block22 ], [ %.18, %false_block23 ], [ %.18, %after_if9 ]
  %.2 = phi float [ %.1, %true_block19 ], [ %.1, %true_block22 ], [ %121, %false_block23 ], [ %.1, %after_if9 ]
  switch i32 %29, label %false_block32 [
    i32 0, label %after_if27
    i32 1, label %true_block28
    i32 2, label %true_block31
  ]

true_block19:                                     ; preds = %after_if9
  br label %after_if18

true_block22:                                     ; preds = %after_if9
  br label %after_if18

false_block23:                                    ; preds = %after_if9
  br label %after_if18

after_if27:                                       ; preds = %false_block32, %true_block31, %true_block28, %after_if18
  %.318 = phi float [ %.217, %true_block28 ], [ %.217, %true_block31 ], [ %.217, %false_block32 ], [ %129, %after_if18 ]
  %.314 = phi float [ %129, %true_block28 ], [ %.213, %true_block31 ], [ %.213, %false_block32 ], [ %.213, %after_if18 ]
  %.310 = phi float [ %.29, %true_block28 ], [ %129, %true_block31 ], [ %.29, %false_block32 ], [ %.29, %after_if18 ]
  %.3 = phi float [ %.2, %true_block28 ], [ %.2, %true_block31 ], [ %129, %false_block32 ], [ %.2, %after_if18 ]
  %130 = fadd reassoc ninf nsz float %.3, %.314
  %131 = fmul reassoc ninf nsz float %130, 5.000000e-01
  %132 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %131, float %.310)
  %133 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %.318, float %132)
  %134 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %131, float %.310)
  %135 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.318, float %134)
  %136 = fmul reassoc ninf nsz float %135, 0x40029ACA60000000
  %137 = fadd reassoc ninf nsz float %136, 0xBFF47711E0000000
  %138 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %137, float 0.000000e+00)
  %139 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %138, float 1.000000e+00)
  %factor = fmul reassoc ninf nsz float %139, -2.000000e+00
  %140 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %141 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %135, float 0x3EE4F8B580000000)
  %142 = fmul reassoc ninf nsz float %133, 0x4001C71C80000000
  %143 = fdiv reassoc ninf nsz float %142, %141
  %144 = fadd reassoc ninf nsz float %143, 0xBFEC71C740000000
  %145 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %144, float 0.000000e+00)
  %146 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %145, float 1.000000e+00)
  %factor29 = fmul reassoc ninf nsz float %146, -2.000000e+00
  %147 = fadd reassoc ninf nsz float %factor29, 3.000000e+00
  %148 = fmul reassoc ninf nsz float %146, %139
  %149 = fmul reassoc ninf nsz float %148, %148
  %150 = fmul reassoc ninf nsz float %149, %140
  %151 = fmul reassoc ninf nsz float %150, %147
  %152 = fmul reassoc ninf nsz float %.318, %31
  %153 = fmul reassoc ninf nsz float %.314, %33
  %154 = fmul reassoc ninf nsz float %.3, %35
  %155 = fadd reassoc ninf nsz float %154, %153
  %156 = fmul reassoc ninf nsz float %155, 5.000000e-01
  %157 = fmul reassoc ninf nsz float %.310, %37
  %158 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %156, float %157)
  %159 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %152, float %158)
  %160 = fsub reassoc ninf nsz float 1.000000e+00, %151
  %161 = fmul reassoc ninf nsz float %160, %152
  %162 = fmul reassoc ninf nsz float %151, %159
  %163 = fadd reassoc ninf nsz float %161, %162
  %164 = fmul reassoc ninf nsz float %160, %156
  %165 = fadd reassoc ninf nsz float %164, %162
  %166 = fmul reassoc ninf nsz float %160, %157
  %167 = fadd reassoc ninf nsz float %166, %162
  %168 = load float, float* %39, align 4
  %169 = fmul reassoc ninf nsz float %163, %168
  %170 = load float, float* %42, align 4
  %171 = fmul reassoc ninf nsz float %165, %170
  %172 = fadd reassoc ninf nsz float %169, %171
  %173 = load float, float* %43, align 4
  %174 = fmul reassoc ninf nsz float %167, %173
  %175 = fadd reassoc ninf nsz float %172, %174
  %176 = load float, float* %45, align 4
  %177 = fmul reassoc ninf nsz float %163, %176
  %178 = load float, float* %48, align 4
  %179 = fmul reassoc ninf nsz float %165, %178
  %180 = fadd reassoc ninf nsz float %177, %179
  %181 = load float, float* %51, align 4
  %182 = fmul reassoc ninf nsz float %167, %181
  %183 = fadd reassoc ninf nsz float %180, %182
  %184 = load float, float* %54, align 4
  %185 = fmul reassoc ninf nsz float %163, %184
  %186 = load float, float* %55, align 4
  %187 = fmul reassoc ninf nsz float %165, %186
  %188 = fadd reassoc ninf nsz float %185, %187
  %189 = load float, float* %58, align 4
  %190 = fmul reassoc ninf nsz float %167, %189
  %191 = fadd reassoc ninf nsz float %188, %190
  %192 = fmul reassoc ninf nsz float %175, %175
  %193 = fadd reassoc ninf nsz float %192, 1.000000e+00
  %194 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %193)
  %195 = fdiv reassoc ninf nsz float %175, %194
  %196 = fmul reassoc ninf nsz float %183, %183
  %197 = fadd reassoc ninf nsz float %196, 1.000000e+00
  %198 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %197)
  %199 = fdiv reassoc ninf nsz float %183, %198
  %200 = fmul reassoc ninf nsz float %191, %191
  %201 = fadd reassoc ninf nsz float %200, 1.000000e+00
  %202 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %201)
  %203 = fdiv reassoc ninf nsz float %191, %202
  %204 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %195, float 0.000000e+00)
  %205 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %204, float 1.000000e+00)
  %206 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %205)
  %207 = fmul reassoc ninf nsz float %206, 0x3FD3A00620000000
  %208 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %207
  %209 = fmul reassoc ninf nsz float %208, %206
  %210 = fadd reassoc ninf nsz float %209, 0xBFE9435AA0000000
  %211 = fmul reassoc ninf nsz float %210, %206
  %212 = fadd reassoc ninf nsz float %211, 0x3FF4E33660000000
  %213 = fmul reassoc ninf nsz float %212, %206
  %214 = load float*, float** %62, align 8
  %215 = load i32, i32* %63, align 4
  %216 = load i32, i32* %64, align 4
  %217 = sub i32 %215, %71
  %218 = mul i32 %217, %80
  %219 = add i32 %.01930, %218
  %220 = mul i32 %219, %216
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %214, i64 %221
  store float %213, float* %222, align 4
  %223 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %199, float 0.000000e+00)
  %224 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %223, float 1.000000e+00)
  %225 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %224)
  %226 = fmul reassoc ninf nsz float %225, 0x3FD3A00620000000
  %227 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %226
  %228 = fmul reassoc ninf nsz float %227, %225
  %229 = fadd reassoc ninf nsz float %228, 0xBFE9435AA0000000
  %230 = fmul reassoc ninf nsz float %229, %225
  %231 = fadd reassoc ninf nsz float %230, 0x3FF4E33660000000
  %232 = fmul reassoc ninf nsz float %231, %225
  %233 = load float*, float** %62, align 8
  %234 = load i32, i32* %63, align 4
  %235 = load i32, i32* %64, align 4
  %236 = sub i32 %234, %71
  %237 = mul i32 %236, %80
  %238 = add i32 %.01930, %237
  %239 = mul i32 %238, %235
  %240 = add i32 %239, 1
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, float* %233, i64 %241
  store float %232, float* %242, align 4
  %243 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %203, float 0.000000e+00)
  %244 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %243, float 1.000000e+00)
  %245 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %244)
  %246 = fmul reassoc ninf nsz float %245, 0x3FD3A00620000000
  %247 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %246
  %248 = fmul reassoc ninf nsz float %247, %245
  %249 = fadd reassoc ninf nsz float %248, 0xBFE9435AA0000000
  %250 = fmul reassoc ninf nsz float %249, %245
  %251 = fadd reassoc ninf nsz float %250, 0x3FF4E33660000000
  %252 = fmul reassoc ninf nsz float %251, %245
  %253 = load float*, float** %62, align 8
  %254 = load i32, i32* %63, align 4
  %255 = load i32, i32* %64, align 4
  %256 = sub i32 %254, %71
  %257 = mul i32 %256, %80
  %258 = add i32 %.01930, %257
  %259 = mul i32 %258, %255
  %260 = add i32 %259, 2
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, float* %253, i64 %261
  store float %252, float* %262, align 4
  %263 = add nsw i32 %.01930, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %263
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block28:                                     ; preds = %after_if18
  br label %after_if27

true_block31:                                     ; preds = %after_if18
  br label %after_if27

false_block32:                                    ; preds = %after_if18
  br label %after_if27
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.sqrt.f32(float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.48, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.48**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.48*, %struct.RuntimeContext.48** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.48* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.48* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
