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
define void @_remap_with_flow_batch_kernel_c320_0_kernel_0_serial(%struct.RuntimeContext.132* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.132* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %1, i64 0, i32 6
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.132, %struct.RuntimeContext.132* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 16
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %15 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %14, i64 0, i32 7
  %16 = load i32, i32* %15, align 4
  %17 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %7, align 8
  %18 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %17, i64 0, i32 14
  %19 = load i8*, i8** %18, align 8
  %20 = getelementptr inbounds i8, i8* %19, i64 12
  %21 = bitcast i8* %20 to i32*
  store i32 %16, i32* %21, align 4
  %22 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %23 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %7, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 8
  %27 = bitcast i8* %26 to i32*
  store i32 %22, i32* %27, align 4
  %28 = mul i32 %22, %13
  %29 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %7, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  store i32 %28, i32* %33, align 4
  %34 = mul i32 %28, %4
  %35 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %7, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %35, i64 0, i32 14
  %37 = bitcast i8** %36 to i32**
  %38 = load i32*, i32** %37, align 8
  store i32 %34, i32* %38, align 4
  ret void
}

; Function Attrs: nounwind
define void @_remap_with_flow_batch_kernel_c320_0_kernel_1_range_for(%struct.RuntimeContext.132* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.132* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 9
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 8
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 10
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 11
  %29 = load float, float* %28, align 4
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 5
  %31 = load i32, i32* %30, align 4
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 4
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
  %41 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %42 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %43 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 2
  %44 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 3
  %45 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %47 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 2
  %48 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %49 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %50 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.07 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %244, %for_loop_body ]
  %51 = load %struct.LLVMRuntime.131*, %struct.LLVMRuntime.131** %3, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.131, %struct.LLVMRuntime.131* %51, i64 0, i32 14
  %53 = load i8*, i8** %52, align 8
  %54 = getelementptr inbounds i8, i8* %53, i64 4
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = sdiv i32 %.07, %56
  %58 = mul i32 %57, %56
  %59 = xor i32 %56, %.07
  %60 = icmp slt i32 %59, 0
  %61 = icmp ne i32 %.07, 0
  %62 = icmp ne i32 %.07, %58
  %63 = and i1 %61, %60
  %64 = and i1 %63, %62
  %.neg4 = sext i1 %64 to i32
  %65 = add i32 %57, %.neg4
  %66 = mul i32 %65, %56
  %67 = mul i32 %56, -1
  %68 = mul i32 %67, %65
  %69 = add i32 %.07, %68
  %70 = getelementptr inbounds i8, i8* %53, i64 8
  %71 = bitcast i8* %70 to i32*
  %72 = load i32, i32* %71, align 4
  %73 = sdiv i32 %69, %72
  %74 = mul i32 %73, %72
  %75 = xor i32 %69, %72
  %76 = icmp slt i32 %75, 0
  %77 = icmp ne i32 %.07, %66
  %78 = icmp ne i32 %69, %74
  %79 = and i1 %77, %76
  %80 = and i1 %78, %79
  %.neg5 = sext i1 %80 to i32
  %81 = add i32 %73, %.neg5
  %82 = mul i32 %81, %72
  %83 = mul i32 %72, -1
  %84 = mul i32 %83, %81
  %85 = add i32 %.07, %84
  %86 = add i32 %85, %68
  %87 = sitofp i32 %86 to float
  %88 = fmul reassoc ninf nsz float %87, %38
  %89 = getelementptr inbounds i8, i8* %53, i64 12
  %90 = bitcast i8* %89 to i32*
  %91 = load i32, i32* %90, align 4
  %92 = add i32 %91, -1
  %93 = sitofp i32 %92 to float
  %94 = fdiv reassoc ninf nsz float %88, %93
  %95 = sitofp i32 %81 to float
  %96 = fmul reassoc ninf nsz float %95, %39
  %97 = getelementptr inbounds i8, i8* %53, i64 16
  %98 = bitcast i8* %97 to i32*
  %99 = load i32, i32* %98, align 4
  %100 = add i32 %99, -1
  %101 = sitofp i32 %100 to float
  %102 = fdiv reassoc ninf nsz float %96, %101
  %103 = tail call reassoc ninf nsz float @llvm.floor.f32(float %94)
  %104 = fptosi float %103 to i32
  %105 = tail call reassoc ninf nsz float @llvm.floor.f32(float %102)
  %106 = fptosi float %105 to i32
  %107 = add i32 %104, 1
  %108 = tail call i32 @llvm.smin.i32(i32 %107, i32 %34)
  %109 = add i32 %106, 1
  %110 = tail call i32 @llvm.smin.i32(i32 %109, i32 %35)
  %111 = sitofp i32 %104 to float
  %112 = fsub reassoc ninf nsz float %94, %111
  %113 = sitofp i32 %106 to float
  %114 = fsub reassoc ninf nsz float %102, %113
  %115 = load float*, float** %41, align 8
  %116 = load i32, i32* %42, align 4
  %117 = load i32, i32* %43, align 4
  %118 = load i32, i32* %44, align 4
  %119 = mul i32 %116, %65
  %120 = add i32 %119, %106
  %121 = mul i32 %120, %117
  %122 = add i32 %121, %104
  %123 = mul i32 %122, %118
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %115, i64 %124
  %126 = load float, float* %125, align 4
  %127 = add i32 %108, %121
  %128 = mul i32 %127, %118
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %115, i64 %129
  %131 = load float, float* %130, align 4
  %132 = add i32 %110, %119
  %133 = mul i32 %132, %117
  %134 = add i32 %133, %104
  %135 = mul i32 %134, %118
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, float* %115, i64 %136
  %138 = load float, float* %137, align 4
  %139 = add i32 %133, %108
  %140 = mul i32 %139, %118
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %115, i64 %141
  %143 = load float, float* %142, align 4
  %144 = add i32 %123, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %115, i64 %145
  %147 = load float, float* %146, align 4
  %148 = add i32 %128, 1
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, float* %115, i64 %149
  %151 = load float, float* %150, align 4
  %152 = add i32 %135, 1
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %115, i64 %153
  %155 = load float, float* %154, align 4
  %156 = add i32 %140, 1
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %115, i64 %157
  %159 = load float, float* %158, align 4
  %160 = fsub reassoc ninf nsz float 1.000000e+00, %112
  %161 = fmul reassoc ninf nsz float %160, %126
  %162 = fmul reassoc ninf nsz float %112, %131
  %163 = fadd reassoc ninf nsz float %161, %162
  %164 = fsub reassoc ninf nsz float 1.000000e+00, %114
  %165 = fmul reassoc ninf nsz float %163, %164
  %166 = fmul reassoc ninf nsz float %160, %138
  %167 = fmul reassoc ninf nsz float %112, %143
  %168 = fadd reassoc ninf nsz float %166, %167
  %169 = fmul reassoc ninf nsz float %168, %114
  %170 = fadd reassoc ninf nsz float %165, %169
  %171 = fmul reassoc ninf nsz float %160, %147
  %172 = fmul reassoc ninf nsz float %112, %151
  %173 = fadd reassoc ninf nsz float %171, %172
  %174 = fmul reassoc ninf nsz float %173, %164
  %175 = fmul reassoc ninf nsz float %160, %155
  %176 = fmul reassoc ninf nsz float %112, %159
  %177 = fadd reassoc ninf nsz float %175, %176
  %178 = fmul reassoc ninf nsz float %177, %114
  %179 = fadd reassoc ninf nsz float %174, %178
  %180 = fmul reassoc ninf nsz float %170, %27
  %181 = fadd reassoc ninf nsz float %180, %87
  %182 = fmul reassoc ninf nsz float %179, %29
  %183 = fadd reassoc ninf nsz float %182, %95
  %184 = tail call reassoc ninf nsz float @llvm.floor.f32(float %181)
  %185 = fptosi float %184 to i32
  %186 = tail call reassoc ninf nsz float @llvm.floor.f32(float %183)
  %187 = fptosi float %186 to i32
  %188 = sitofp i32 %185 to float
  %189 = fsub reassoc ninf nsz float %181, %188
  %190 = sitofp i32 %187 to float
  %191 = fsub reassoc ninf nsz float %183, %190
  %192 = tail call i32 @llvm.smax.i32(i32 %185, i32 0)
  %193 = tail call i32 @llvm.smin.i32(i32 %192, i32 %36)
  %194 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %195 = tail call i32 @llvm.smin.i32(i32 %194, i32 %37)
  %196 = add i32 %193, 1
  %197 = tail call i32 @llvm.smin.i32(i32 %196, i32 %36)
  %198 = add i32 %195, 1
  %199 = tail call i32 @llvm.smin.i32(i32 %198, i32 %37)
  %200 = load float*, float** %45, align 8
  %201 = load i32, i32* %46, align 4
  %202 = load i32, i32* %47, align 4
  %203 = mul i32 %201, %65
  %204 = add i32 %195, %203
  %205 = mul i32 %204, %202
  %206 = add i32 %205, %193
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, float* %200, i64 %207
  %209 = load float, float* %208, align 4
  %210 = add i32 %205, %197
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %200, i64 %211
  %213 = load float, float* %212, align 4
  %214 = add i32 %199, %203
  %215 = mul i32 %214, %202
  %216 = add i32 %215, %193
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, float* %200, i64 %217
  %219 = load float, float* %218, align 4
  %220 = add i32 %215, %197
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %200, i64 %221
  %223 = load float, float* %222, align 4
  %224 = fsub reassoc ninf nsz float 1.000000e+00, %189
  %225 = fmul reassoc ninf nsz float %224, %209
  %226 = fmul reassoc ninf nsz float %189, %213
  %227 = fadd reassoc ninf nsz float %225, %226
  %228 = fmul reassoc ninf nsz float %224, %219
  %229 = fmul reassoc ninf nsz float %189, %223
  %230 = fadd reassoc ninf nsz float %228, %229
  %231 = fsub reassoc ninf nsz float %230, %227
  %232 = fmul reassoc ninf nsz float %231, %191
  %233 = fadd reassoc ninf nsz float %232, %227
  %234 = load float*, float** %48, align 8
  %235 = load i32, i32* %49, align 4
  %236 = load i32, i32* %50, align 4
  %237 = mul i32 %235, %65
  %238 = add i32 %237, %81
  %239 = mul i32 %238, %236
  %240 = sub i32 %239, %82
  %241 = add i32 %69, %240
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, float* %234, i64 %242
  store float %233, float* %243, align 4
  %244 = add nsw i32 %.07, 1
  %exitcond.not = icmp eq i32 %19, %244
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
