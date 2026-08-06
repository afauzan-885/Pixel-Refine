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
define void @_ha_reconstruct_and_postprocess_kernel_c708_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %1, i64 0, i32 5
  %3 = load float, float* %2, align 4
  %4 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3, float 0x3FB99999A0000000)
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %7, i64 0, i32 14
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
  %21 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %21, i64 0, i32 14
  %23 = load i8*, i8** %22, align 8
  %24 = getelementptr inbounds i8, i8* %23, i64 12
  %25 = bitcast i8* %24 to float*
  store float %20, float* %25, align 4
  %26 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %0, align 8
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %26, i64 0, i32 7
  %28 = load float, float* %27, align 4
  %29 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %28, float 0x3FB99999A0000000)
  %30 = fdiv reassoc ninf nsz float 1.000000e+00, %29
  %31 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %31, i64 0, i32 14
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
  %43 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %44 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %43, i64 0, i32 14
  %45 = load i8*, i8** %44, align 8
  %46 = getelementptr inbounds i8, i8* %45, i64 4
  %47 = bitcast i8* %46 to i32*
  store i32 %42, i32* %47, align 4
  %48 = mul i32 %42, %39
  %49 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %50 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %49, i64 0, i32 14
  %51 = bitcast i8** %50 to i32**
  %52 = load i32*, i32** %51, align 8
  store i32 %48, i32* %52, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_ha_reconstruct_and_postprocess_kernel_c708_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #2 {
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
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 2, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 2, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 4, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 4, i32 0, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, i32, i32 }* %22, i64 0, i32 4, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.010 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %147, %for_loop_body ]
  %32 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 4
  %36 = bitcast i8* %35 to i32*
  %37 = load i32, i32* %36, align 4
  %38 = sdiv i32 %.010, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %.010
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %.010, 0
  %43 = icmp ne i32 %.010, %39
  %44 = and i1 %42, %41
  %45 = and i1 %44, %43
  %.neg4 = sext i1 %45 to i32
  %46 = add i32 %38, %.neg4
  %47 = load float*, float** %23, align 8
  %48 = load i32, i32* %24, align 4
  %49 = sub i32 %48, %37
  %50 = mul i32 %49, %46
  %51 = add i32 %.010, %50
  %52 = sext i32 %51 to i64
  %53 = getelementptr float, float* %47, i64 %52
  %54 = load float, float* %53, align 4
  %55 = load float*, float** %25, align 8
  %56 = load i32, i32* %26, align 4
  %57 = sub i32 %56, %37
  %58 = mul i32 %57, %46
  %59 = add i32 %.010, %58
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, float* %55, i64 %60
  %62 = load float, float* %61, align 4
  %63 = fadd reassoc ninf nsz float %62, %54
  %64 = load float*, float** %27, align 8
  %65 = load i32, i32* %28, align 4
  %66 = sub i32 %65, %37
  %67 = mul i32 %66, %46
  %68 = add i32 %.010, %67
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, float* %64, i64 %69
  %71 = load float, float* %70, align 4
  %72 = fadd reassoc ninf nsz float %71, %54
  %73 = getelementptr inbounds i8, i8* %34, i64 8
  %74 = bitcast i8* %73 to float*
  %75 = load float, float* %74, align 4
  %76 = fmul reassoc ninf nsz float %75, %63
  %77 = getelementptr inbounds i8, i8* %34, i64 12
  %78 = bitcast i8* %77 to float*
  %79 = load float, float* %78, align 4
  %80 = fmul reassoc ninf nsz float %79, %54
  %81 = getelementptr inbounds i8, i8* %34, i64 16
  %82 = bitcast i8* %81 to float*
  %83 = load float, float* %82, align 4
  %84 = fmul reassoc ninf nsz float %83, %72
  %85 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %80, float %84)
  %86 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %76, float %85)
  %87 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %80, float %84)
  %88 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %76, float %87)
  %89 = fmul reassoc ninf nsz float %86, 0x40029ACA60000000
  %90 = fadd reassoc ninf nsz float %89, 0xBFF47711E0000000
  %91 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %90, float 0.000000e+00)
  %92 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %91, float 1.000000e+00)
  %factor = fmul reassoc ninf nsz float %92, -2.000000e+00
  %93 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %94 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %86, float 0x3EE4F8B580000000)
  %95 = fmul reassoc ninf nsz float %88, 0x4001C71C80000000
  %96 = fdiv reassoc ninf nsz float %95, %94
  %97 = fadd reassoc ninf nsz float %96, 0xBFEC71C740000000
  %98 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %97, float 0.000000e+00)
  %99 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %98, float 1.000000e+00)
  %factor9 = fmul reassoc ninf nsz float %99, -2.000000e+00
  %100 = fadd reassoc ninf nsz float %factor9, 3.000000e+00
  %101 = fmul reassoc ninf nsz float %99, %92
  %102 = fmul reassoc ninf nsz float %101, %101
  %103 = fmul reassoc ninf nsz float %102, %93
  %104 = fmul reassoc ninf nsz float %103, %100
  %105 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %54, float %72)
  %106 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %63, float %105)
  %107 = fsub reassoc ninf nsz float 1.000000e+00, %104
  %108 = fmul reassoc ninf nsz float %107, %63
  %109 = fmul reassoc ninf nsz float %104, %106
  %110 = fadd reassoc ninf nsz float %108, %109
  %111 = fmul reassoc ninf nsz float %107, %54
  %112 = fadd reassoc ninf nsz float %111, %109
  %113 = fmul reassoc ninf nsz float %107, %72
  %114 = fadd reassoc ninf nsz float %113, %109
  %115 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %110, float 0.000000e+00)
  %116 = load float*, float** %29, align 8
  %117 = load i32, i32* %30, align 4
  %118 = load i32, i32* %31, align 4
  %119 = sub i32 %117, %37
  %120 = mul i32 %119, %46
  %121 = add i32 %.010, %120
  %122 = mul i32 %121, %118
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, float* %116, i64 %123
  store float %115, float* %124, align 4
  %125 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %112, float 0.000000e+00)
  %126 = load float*, float** %29, align 8
  %127 = load i32, i32* %30, align 4
  %128 = load i32, i32* %31, align 4
  %129 = sub i32 %127, %37
  %130 = mul i32 %129, %46
  %131 = add i32 %.010, %130
  %132 = mul i32 %131, %128
  %133 = add i32 %132, 1
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %126, i64 %134
  store float %125, float* %135, align 4
  %136 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %114, float 0.000000e+00)
  %137 = load float*, float** %29, align 8
  %138 = load i32, i32* %30, align 4
  %139 = load i32, i32* %31, align 4
  %140 = sub i32 %138, %37
  %141 = mul i32 %140, %46
  %142 = add i32 %.010, %141
  %143 = mul i32 %142, %139
  %144 = add i32 %143, 2
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %137, i64 %145
  store float %136, float* %146, align 4
  %147 = add nsw i32 %.010, 1
  %exitcond.not = icmp eq i32 %19, %147
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
