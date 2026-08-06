; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.36*, void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.36 = type { i8*, %struct.LLVMRuntime.35*, i32, i64* }
%struct.LLVMRuntime.35 = type { %struct.PreallocatedMemoryChunk.31, %struct.PreallocatedMemoryChunk.31, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.32*], [1024 x %struct.NodeManager.33*], [1024 x i8*], i8*, %struct.RandState.34*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.31 = type { i8*, i8*, i64 }
%struct.ListManager.32 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.35* }
%struct.NodeManager.33 = type { %struct.LLVMRuntime.35*, i32, i32, i32, i32, %struct.ListManager.32*, %struct.ListManager.32*, %struct.ListManager.32*, i32 }
%struct.RandState.34 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_mlri_admm_reconstruct_and_postprocess_kernel_c88_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %1, i64 0, i32 5
  %3 = load float, float* %2, align 4
  %4 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3, float 0x3FB99999A0000000)
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 8
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %13 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %12, i64 0, i32 6
  %14 = load float, float* %13, align 4
  %15 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %12, i64 0, i32 8
  %16 = load float, float* %15, align 4
  %17 = fadd reassoc ninf nsz float %16, %14
  %18 = fmul reassoc ninf nsz float %17, 5.000000e-01
  %19 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %18, float 0x3FB99999A0000000)
  %20 = fdiv reassoc ninf nsz float 1.000000e+00, %19
  %21 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %21, i64 0, i32 14
  %23 = load i8*, i8** %22, align 8
  %24 = getelementptr inbounds i8, i8* %23, i64 12
  %25 = bitcast i8* %24 to float*
  store float %20, float* %25, align 4
  %26 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %26, i64 0, i32 7
  %28 = load float, float* %27, align 4
  %29 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %28, float 0x3FB99999A0000000)
  %30 = fdiv reassoc ninf nsz float 1.000000e+00, %29
  %31 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 16
  %35 = bitcast i8* %34 to float*
  store float %30, float* %35, align 4
  %36 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %37 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %36, i64 0, i32 9
  %38 = load i32, i32* %37, align 4
  %39 = tail call i32 @llvm.smax.i32(i32 %38, i32 0)
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %36, i64 0, i32 10
  %41 = load i32, i32* %40, align 4
  %42 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %43 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %44 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %43, i64 0, i32 14
  %45 = load i8*, i8** %44, align 8
  %46 = getelementptr inbounds i8, i8* %45, i64 4
  %47 = bitcast i8* %46 to i32*
  store i32 %42, i32* %47, align 4
  %48 = mul i32 %42, %39
  %49 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %50 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %49, i64 0, i32 14
  %51 = bitcast i8** %50 to i32**
  %52 = load i32*, i32** %51, align 8
  store i32 %48, i32* %52, align 4
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_mlri_admm_reconstruct_and_postprocess_kernel_c88_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #2 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.36* %context, %struct.RuntimeContext.36** %4, align 8
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.36*, i8*, i32)* @function_body, void (%struct.RuntimeContext.36*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.36* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 3, i32 1
  %23 = load float*, float** %22, align 8
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr float, float* %23, i64 1
  %27 = getelementptr float, float* %23, i64 2
  %28 = sext i32 %25 to i64
  %29 = getelementptr float, float* %23, i64 %28
  %30 = add i32 %25, 1
  %31 = sext i32 %30 to i64
  %32 = getelementptr float, float* %23, i64 %31
  %33 = add i32 %25, 2
  %34 = sext i32 %33 to i64
  %35 = getelementptr float, float* %23, i64 %34
  %36 = shl i32 %25, 1
  %37 = sext i32 %36 to i64
  %38 = getelementptr float, float* %23, i64 %37
  %39 = getelementptr float, float* %38, i64 1
  %40 = add i32 %36, 2
  %41 = sext i32 %40 to i64
  %42 = getelementptr float, float* %23, i64 %41
  %43 = icmp slt i32 %17, %19
  br i1 %43, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 1, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 0, i32 1
  %47 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 2, i32 1
  %49 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %50 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 4, i32 1
  %51 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 4, i32 0, i32 1
  %52 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %21, i64 0, i32 4, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.010 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %229, %for_loop_body ]
  %53 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %53, i64 0, i32 14
  %55 = load i8*, i8** %54, align 8
  %56 = getelementptr inbounds i8, i8* %55, i64 4
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = sdiv i32 %.010, %58
  %60 = mul i32 %59, %58
  %61 = xor i32 %58, %.010
  %62 = icmp slt i32 %61, 0
  %63 = icmp ne i32 %.010, 0
  %64 = icmp ne i32 %.010, %60
  %65 = and i1 %63, %62
  %66 = and i1 %65, %64
  %.neg4 = sext i1 %66 to i32
  %67 = add i32 %59, %.neg4
  %68 = load float*, float** %44, align 8
  %69 = load i32, i32* %45, align 4
  %70 = sub i32 %69, %58
  %71 = mul i32 %70, %67
  %72 = add i32 %.010, %71
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, float* %68, i64 %73
  %75 = load float, float* %74, align 4
  %76 = load float*, float** %46, align 8
  %77 = load i32, i32* %47, align 4
  %78 = sub i32 %77, %58
  %79 = mul i32 %78, %67
  %80 = add i32 %.010, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %76, i64 %81
  %83 = load float, float* %82, align 4
  %84 = load float*, float** %48, align 8
  %85 = load i32, i32* %49, align 4
  %86 = sub i32 %85, %58
  %87 = mul i32 %86, %67
  %88 = add i32 %.010, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, float* %84, i64 %89
  %91 = load float, float* %90, align 4
  %92 = getelementptr inbounds i8, i8* %55, i64 8
  %93 = bitcast i8* %92 to float*
  %94 = load float, float* %93, align 4
  %95 = fmul reassoc ninf nsz float %94, %75
  %96 = getelementptr inbounds i8, i8* %55, i64 12
  %97 = bitcast i8* %96 to float*
  %98 = load float, float* %97, align 4
  %99 = fmul reassoc ninf nsz float %98, %83
  %100 = getelementptr inbounds i8, i8* %55, i64 16
  %101 = bitcast i8* %100 to float*
  %102 = load float, float* %101, align 4
  %103 = fmul reassoc ninf nsz float %102, %91
  %104 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %99, float %103)
  %105 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %95, float %104)
  %106 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %99, float %103)
  %107 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %95, float %106)
  %108 = fmul reassoc ninf nsz float %105, 0x40029ACA60000000
  %109 = fadd reassoc ninf nsz float %108, 0xBFF47711E0000000
  %110 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %109, float 0.000000e+00)
  %111 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %110, float 1.000000e+00)
  %factor = fmul reassoc ninf nsz float %111, -2.000000e+00
  %112 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %113 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %105, float 0x3EE4F8B580000000)
  %114 = fmul reassoc ninf nsz float %107, 0x4001C71C80000000
  %115 = fdiv reassoc ninf nsz float %114, %113
  %116 = fadd reassoc ninf nsz float %115, 0xBFEC71C740000000
  %117 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %116, float 0.000000e+00)
  %118 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %117, float 1.000000e+00)
  %factor9 = fmul reassoc ninf nsz float %118, -2.000000e+00
  %119 = fadd reassoc ninf nsz float %factor9, 3.000000e+00
  %120 = fmul reassoc ninf nsz float %118, %111
  %121 = fmul reassoc ninf nsz float %120, %120
  %122 = fmul reassoc ninf nsz float %121, %112
  %123 = fmul reassoc ninf nsz float %122, %119
  %124 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %83, float %91)
  %125 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %75, float %124)
  %126 = fsub reassoc ninf nsz float 1.000000e+00, %123
  %127 = fmul reassoc ninf nsz float %126, %75
  %128 = fmul reassoc ninf nsz float %123, %125
  %129 = fadd reassoc ninf nsz float %127, %128
  %130 = fmul reassoc ninf nsz float %126, %83
  %131 = fadd reassoc ninf nsz float %130, %128
  %132 = fmul reassoc ninf nsz float %126, %91
  %133 = fadd reassoc ninf nsz float %132, %128
  %134 = load float, float* %23, align 4
  %135 = fmul reassoc ninf nsz float %129, %134
  %136 = load float, float* %26, align 4
  %137 = fmul reassoc ninf nsz float %131, %136
  %138 = fadd reassoc ninf nsz float %135, %137
  %139 = load float, float* %27, align 4
  %140 = fmul reassoc ninf nsz float %133, %139
  %141 = fadd reassoc ninf nsz float %138, %140
  %142 = load float, float* %29, align 4
  %143 = fmul reassoc ninf nsz float %129, %142
  %144 = load float, float* %32, align 4
  %145 = fmul reassoc ninf nsz float %131, %144
  %146 = fadd reassoc ninf nsz float %143, %145
  %147 = load float, float* %35, align 4
  %148 = fmul reassoc ninf nsz float %133, %147
  %149 = fadd reassoc ninf nsz float %146, %148
  %150 = load float, float* %38, align 4
  %151 = fmul reassoc ninf nsz float %129, %150
  %152 = load float, float* %39, align 4
  %153 = fmul reassoc ninf nsz float %131, %152
  %154 = fadd reassoc ninf nsz float %151, %153
  %155 = load float, float* %42, align 4
  %156 = fmul reassoc ninf nsz float %133, %155
  %157 = fadd reassoc ninf nsz float %154, %156
  %158 = fmul reassoc ninf nsz float %141, %141
  %159 = fadd reassoc ninf nsz float %158, 1.000000e+00
  %160 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %159)
  %161 = fdiv reassoc ninf nsz float %141, %160
  %162 = fmul reassoc ninf nsz float %149, %149
  %163 = fadd reassoc ninf nsz float %162, 1.000000e+00
  %164 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %163)
  %165 = fdiv reassoc ninf nsz float %149, %164
  %166 = fmul reassoc ninf nsz float %157, %157
  %167 = fadd reassoc ninf nsz float %166, 1.000000e+00
  %168 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %167)
  %169 = fdiv reassoc ninf nsz float %157, %168
  %170 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %161, float 0.000000e+00)
  %171 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %170, float 1.000000e+00)
  %172 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %171)
  %173 = fmul reassoc ninf nsz float %172, 0x3FD3A00620000000
  %174 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %173
  %175 = fmul reassoc ninf nsz float %174, %172
  %176 = fadd reassoc ninf nsz float %175, 0xBFE9435AA0000000
  %177 = fmul reassoc ninf nsz float %176, %172
  %178 = fadd reassoc ninf nsz float %177, 0x3FF4E33660000000
  %179 = fmul reassoc ninf nsz float %178, %172
  %180 = load float*, float** %50, align 8
  %181 = load i32, i32* %51, align 4
  %182 = load i32, i32* %52, align 4
  %183 = sub i32 %181, %58
  %184 = mul i32 %183, %67
  %185 = add i32 %.010, %184
  %186 = mul i32 %185, %182
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, float* %180, i64 %187
  store float %179, float* %188, align 4
  %189 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %165, float 0.000000e+00)
  %190 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %189, float 1.000000e+00)
  %191 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %190)
  %192 = fmul reassoc ninf nsz float %191, 0x3FD3A00620000000
  %193 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %192
  %194 = fmul reassoc ninf nsz float %193, %191
  %195 = fadd reassoc ninf nsz float %194, 0xBFE9435AA0000000
  %196 = fmul reassoc ninf nsz float %195, %191
  %197 = fadd reassoc ninf nsz float %196, 0x3FF4E33660000000
  %198 = fmul reassoc ninf nsz float %197, %191
  %199 = load float*, float** %50, align 8
  %200 = load i32, i32* %51, align 4
  %201 = load i32, i32* %52, align 4
  %202 = sub i32 %200, %58
  %203 = mul i32 %202, %67
  %204 = add i32 %.010, %203
  %205 = mul i32 %204, %201
  %206 = add i32 %205, 1
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, float* %199, i64 %207
  store float %198, float* %208, align 4
  %209 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %169, float 0.000000e+00)
  %210 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %209, float 1.000000e+00)
  %211 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %210)
  %212 = fmul reassoc ninf nsz float %211, 0x3FD3A00620000000
  %213 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %212
  %214 = fmul reassoc ninf nsz float %213, %211
  %215 = fadd reassoc ninf nsz float %214, 0xBFE9435AA0000000
  %216 = fmul reassoc ninf nsz float %215, %211
  %217 = fadd reassoc ninf nsz float %216, 0x3FF4E33660000000
  %218 = fmul reassoc ninf nsz float %217, %211
  %219 = load float*, float** %50, align 8
  %220 = load i32, i32* %51, align 4
  %221 = load i32, i32* %52, align 4
  %222 = sub i32 %220, %58
  %223 = mul i32 %222, %67
  %224 = add i32 %.010, %223
  %225 = mul i32 %224, %221
  %226 = add i32 %225, 2
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, float* %219, i64 %227
  store float %218, float* %228, align 4
  %229 = add nsw i32 %.010, 1
  %exitcond.not = icmp eq i32 %19, %229
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.sqrt.f32(float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.36, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.36**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.36*, %struct.RuntimeContext.36** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.36* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.36* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
