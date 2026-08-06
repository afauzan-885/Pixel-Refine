; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.144*, void (%struct.RuntimeContext.144*, i8*)*, void (%struct.RuntimeContext.144*, i8*, i32)*, void (%struct.RuntimeContext.144*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.144 = type { i8*, %struct.LLVMRuntime.143*, i32, i64* }
%struct.LLVMRuntime.143 = type { %struct.PreallocatedMemoryChunk.139, %struct.PreallocatedMemoryChunk.139, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.140*], [1024 x %struct.NodeManager.141*], [1024 x i8*], i8*, %struct.RandState.142*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.139 = type { i8*, i8*, i64 }
%struct.ListManager.140 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.143* }
%struct.NodeManager.141 = type { %struct.LLVMRuntime.143*, i32, i32, i32, i32, %struct.ListManager.140*, %struct.ListManager.140*, %struct.ListManager.140*, i32 }
%struct.RandState.142 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_remap_with_flow_batch_kernel_vec3_c322_0_kernel_0_serial(%struct.RuntimeContext.144* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.144* %context to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }**
  %1 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %1, i64 0, i32 6
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.144, %struct.RuntimeContext.144* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 16
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %15 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %14, i64 0, i32 7
  %16 = load i32, i32* %15, align 4
  %17 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %7, align 8
  %18 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %17, i64 0, i32 14
  %19 = load i8*, i8** %18, align 8
  %20 = getelementptr inbounds i8, i8* %19, i64 12
  %21 = bitcast i8* %20 to i32*
  store i32 %16, i32* %21, align 4
  %22 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %23 = mul i32 %22, 3
  %24 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %7, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 8
  %28 = bitcast i8* %27 to i32*
  store i32 %23, i32* %28, align 4
  %29 = mul i32 %23, %13
  %30 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %7, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  store i32 %29, i32* %34, align 4
  %35 = mul i32 %29, %4
  %36 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %7, align 8
  %37 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %36, i64 0, i32 14
  %38 = bitcast i8** %37 to i32**
  %39 = load i32*, i32** %38, align 8
  store i32 %35, i32* %39, align 4
  ret void
}

; Function Attrs: nounwind
define void @_remap_with_flow_batch_kernel_vec3_c322_0_kernel_1_range_for(%struct.RuntimeContext.144* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.144* %context, %struct.RuntimeContext.144** %4, align 8
  store void (%struct.RuntimeContext.144*, i8*)* null, void (%struct.RuntimeContext.144*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.144*, i8*, i32)* @function_body, void (%struct.RuntimeContext.144*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.144*, i8*)* null, void (%struct.RuntimeContext.144*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.144, %struct.RuntimeContext.144* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.144* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.144, %struct.RuntimeContext.144* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.144* %0 to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }**
  %21 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 9
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 8
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 10
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 11
  %29 = load float, float* %28, align 4
  %30 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 5
  %31 = load i32, i32* %30, align 4
  %32 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 4
  %33 = load i32, i32* %32, align 4
  %34 = add i32 %23, -1
  %35 = add i32 %25, -1
  %36 = add i32 %31, -1
  %37 = add i32 %33, -1
  %38 = sitofp i32 %34 to float
  %39 = sitofp i32 %35 to float
  %40 = icmp slt i32 %17, %19
  br i1 %40, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %41 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %42 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %43 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 2
  %44 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 3
  %45 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %47 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 2
  %48 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 3
  %49 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %50 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %51 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 2
  %52 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.09 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %277, %for_loop_body ]
  %53 = load %struct.LLVMRuntime.143*, %struct.LLVMRuntime.143** %3, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.143, %struct.LLVMRuntime.143* %53, i64 0, i32 14
  %55 = load i8*, i8** %54, align 8
  %56 = getelementptr inbounds i8, i8* %55, i64 4
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = sdiv i32 %.09, %58
  %60 = mul i32 %59, %58
  %61 = xor i32 %58, %.09
  %62 = icmp slt i32 %61, 0
  %63 = icmp ne i32 %.09, 0
  %64 = icmp ne i32 %.09, %60
  %65 = and i1 %63, %62
  %66 = and i1 %65, %64
  %.neg4 = sext i1 %66 to i32
  %67 = add i32 %59, %.neg4
  %68 = mul i32 %67, %58
  %69 = mul i32 %58, -1
  %70 = mul i32 %69, %67
  %71 = add i32 %.09, %70
  %72 = getelementptr inbounds i8, i8* %55, i64 8
  %73 = bitcast i8* %72 to i32*
  %74 = load i32, i32* %73, align 4
  %75 = sdiv i32 %71, %74
  %76 = mul i32 %75, %74
  %77 = xor i32 %71, %74
  %78 = icmp slt i32 %77, 0
  %79 = icmp ne i32 %.09, %68
  %80 = icmp ne i32 %71, %76
  %81 = and i1 %79, %78
  %82 = and i1 %80, %81
  %.neg5 = sext i1 %82 to i32
  %83 = add i32 %75, %.neg5
  %84 = mul i32 %83, %74
  %85 = sub i32 %70, %84
  %86 = add i32 %.09, %85
  %87 = sdiv i32 %86, 3
  %88 = icmp slt i32 %86, 0
  %89 = mul nsw i32 %87, 3
  %90 = icmp ne i32 %86, %89
  %91 = and i1 %88, %90
  %.neg6 = sext i1 %91 to i32
  %92 = add i32 %87, %.neg6
  %93 = sitofp i32 %92 to float
  %94 = fmul reassoc ninf nsz float %93, %38
  %95 = getelementptr inbounds i8, i8* %55, i64 12
  %96 = bitcast i8* %95 to i32*
  %97 = load i32, i32* %96, align 4
  %98 = add i32 %97, -1
  %99 = sitofp i32 %98 to float
  %100 = fdiv reassoc ninf nsz float %94, %99
  %101 = sitofp i32 %83 to float
  %102 = fmul reassoc ninf nsz float %101, %39
  %103 = getelementptr inbounds i8, i8* %55, i64 16
  %104 = bitcast i8* %103 to i32*
  %105 = load i32, i32* %104, align 4
  %106 = add i32 %105, -1
  %107 = sitofp i32 %106 to float
  %108 = fdiv reassoc ninf nsz float %102, %107
  %109 = tail call reassoc ninf nsz float @llvm.floor.f32(float %100)
  %110 = fptosi float %109 to i32
  %111 = tail call reassoc ninf nsz float @llvm.floor.f32(float %108)
  %112 = fptosi float %111 to i32
  %113 = add i32 %110, 1
  %114 = tail call i32 @llvm.smin.i32(i32 %113, i32 %34)
  %115 = add i32 %112, 1
  %116 = tail call i32 @llvm.smin.i32(i32 %115, i32 %35)
  %117 = sitofp i32 %110 to float
  %118 = fsub reassoc ninf nsz float %100, %117
  %119 = sitofp i32 %112 to float
  %120 = fsub reassoc ninf nsz float %108, %119
  %121 = load float*, float** %41, align 8
  %122 = load i32, i32* %42, align 4
  %123 = load i32, i32* %43, align 4
  %124 = load i32, i32* %44, align 4
  %125 = mul i32 %122, %67
  %126 = add i32 %125, %112
  %127 = mul i32 %126, %123
  %128 = add i32 %127, %110
  %129 = mul i32 %128, %124
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, float* %121, i64 %130
  %132 = load float, float* %131, align 4
  %133 = add i32 %114, %127
  %134 = mul i32 %133, %124
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %121, i64 %135
  %137 = load float, float* %136, align 4
  %138 = add i32 %116, %125
  %139 = mul i32 %138, %123
  %140 = add i32 %139, %110
  %141 = mul i32 %140, %124
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, float* %121, i64 %142
  %144 = load float, float* %143, align 4
  %145 = add i32 %114, %139
  %146 = mul i32 %145, %124
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %121, i64 %147
  %149 = load float, float* %148, align 4
  %150 = add i32 %129, 1
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %121, i64 %151
  %153 = load float, float* %152, align 4
  %154 = add i32 %134, 1
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %121, i64 %155
  %157 = load float, float* %156, align 4
  %158 = add i32 %141, 1
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %121, i64 %159
  %161 = load float, float* %160, align 4
  %162 = add i32 %146, 1
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %121, i64 %163
  %165 = load float, float* %164, align 4
  %166 = fsub reassoc ninf nsz float 1.000000e+00, %118
  %167 = fmul reassoc ninf nsz float %166, %132
  %168 = fmul reassoc ninf nsz float %118, %137
  %169 = fadd reassoc ninf nsz float %167, %168
  %170 = fsub reassoc ninf nsz float 1.000000e+00, %120
  %171 = fmul reassoc ninf nsz float %169, %170
  %172 = fmul reassoc ninf nsz float %166, %144
  %173 = fmul reassoc ninf nsz float %118, %149
  %174 = fadd reassoc ninf nsz float %172, %173
  %175 = fmul reassoc ninf nsz float %174, %120
  %176 = fadd reassoc ninf nsz float %171, %175
  %177 = fmul reassoc ninf nsz float %166, %153
  %178 = fmul reassoc ninf nsz float %118, %157
  %179 = fadd reassoc ninf nsz float %177, %178
  %180 = fmul reassoc ninf nsz float %179, %170
  %181 = fmul reassoc ninf nsz float %166, %161
  %182 = fmul reassoc ninf nsz float %118, %165
  %183 = fadd reassoc ninf nsz float %181, %182
  %184 = fmul reassoc ninf nsz float %183, %120
  %185 = fadd reassoc ninf nsz float %180, %184
  %186 = fmul reassoc ninf nsz float %176, %27
  %187 = fadd reassoc ninf nsz float %186, %93
  %188 = fmul reassoc ninf nsz float %185, %29
  %189 = fadd reassoc ninf nsz float %188, %101
  %190 = tail call reassoc ninf nsz float @llvm.floor.f32(float %187)
  %191 = fptosi float %190 to i32
  %192 = tail call reassoc ninf nsz float @llvm.floor.f32(float %189)
  %193 = fptosi float %192 to i32
  %194 = sitofp i32 %191 to float
  %195 = fsub reassoc ninf nsz float %187, %194
  %196 = sitofp i32 %193 to float
  %197 = fsub reassoc ninf nsz float %189, %196
  %198 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %199 = tail call i32 @llvm.smin.i32(i32 %198, i32 %36)
  %200 = tail call i32 @llvm.smax.i32(i32 %193, i32 0)
  %201 = tail call i32 @llvm.smin.i32(i32 %200, i32 %37)
  %202 = add i32 %199, 1
  %203 = tail call i32 @llvm.smin.i32(i32 %202, i32 %36)
  %204 = add i32 %201, 1
  %205 = tail call i32 @llvm.smin.i32(i32 %204, i32 %37)
  %206 = load float*, float** %45, align 8
  %207 = load i32, i32* %46, align 4
  %208 = load i32, i32* %47, align 4
  %209 = load i32, i32* %48, align 4
  %210 = mul i32 %207, %67
  %211 = add i32 %201, %210
  %212 = mul i32 %211, %208
  %213 = add i32 %212, %199
  %214 = mul i32 %213, %209
  %215 = sub i32 %214, %68
  %216 = sub i32 %215, %84
  %217 = mul i32 %92, 3
  %218 = sub i32 %216, %217
  %219 = add i32 %.09, %218
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %206, i64 %220
  %222 = load float, float* %221, align 4
  %223 = add i32 %212, %203
  %224 = mul i32 %223, %209
  %225 = sub i32 %224, %68
  %226 = sub i32 %225, %84
  %227 = sub i32 %226, %217
  %228 = add i32 %.09, %227
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %206, i64 %229
  %231 = load float, float* %230, align 4
  %232 = add i32 %205, %210
  %233 = mul i32 %232, %208
  %234 = add i32 %233, %199
  %235 = mul i32 %234, %209
  %236 = sub i32 %235, %68
  %237 = sub i32 %236, %84
  %238 = sub i32 %237, %217
  %239 = add i32 %.09, %238
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %206, i64 %240
  %242 = load float, float* %241, align 4
  %243 = add i32 %233, %203
  %244 = mul i32 %243, %209
  %245 = sub i32 %244, %68
  %246 = sub i32 %245, %84
  %247 = sub i32 %246, %217
  %248 = add i32 %.09, %247
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, float* %206, i64 %249
  %251 = load float, float* %250, align 4
  %252 = fsub reassoc ninf nsz float 1.000000e+00, %195
  %253 = fmul reassoc ninf nsz float %252, %222
  %254 = fmul reassoc ninf nsz float %195, %231
  %255 = fadd reassoc ninf nsz float %253, %254
  %256 = fmul reassoc ninf nsz float %252, %242
  %257 = fmul reassoc ninf nsz float %195, %251
  %258 = fadd reassoc ninf nsz float %256, %257
  %259 = fsub reassoc ninf nsz float %258, %255
  %260 = fmul reassoc ninf nsz float %259, %197
  %261 = fadd reassoc ninf nsz float %260, %255
  %262 = load float*, float** %49, align 8
  %263 = load i32, i32* %50, align 4
  %264 = load i32, i32* %51, align 4
  %265 = load i32, i32* %52, align 4
  %266 = mul i32 %263, %67
  %267 = add i32 %266, %83
  %268 = mul i32 %267, %264
  %269 = add i32 %268, %92
  %270 = mul i32 %269, %265
  %271 = sub i32 %270, %68
  %272 = sub i32 %271, %84
  %273 = sub i32 %272, %217
  %274 = add i32 %.09, %273
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, float* %262, i64 %275
  store float %261, float* %276, align 4
  %277 = add nsw i32 %.09, 1
  %exitcond.not = icmp eq i32 %19, %277
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.144, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.144**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.144*, %struct.RuntimeContext.144** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.144*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.144*, i8*)*, void (%struct.RuntimeContext.144*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.144*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.144*, i8*, i32)*, void (%struct.RuntimeContext.144*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.144*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.144*, i8*)*, void (%struct.RuntimeContext.144*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.144*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.144* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.144* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.144* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.144, %struct.RuntimeContext.144* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.144* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.144* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.144*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.144* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
