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
define void @_zncc_spatial_kernel_c292_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %10, i64 0, i32 1, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 12
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %18, i64 0, i32 4, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %18, i64 0, i32 4, i32 0, i32 1
  %23 = load i32, i32* %22, align 4
  %24 = tail call i32 @llvm.smax.i32(i32 %23, i32 0)
  %25 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  store i32 %24, i32* %29, align 4
  %30 = mul i32 %24, %21
  %31 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %31, i64 0, i32 14
  %33 = bitcast i8** %32 to i32**
  %34 = load i32*, i32** %33, align 8
  store i32 %30, i32* %34, align 4
  ret void
}

; Function Attrs: nounwind
define void @_zncc_spatial_kernel_c292_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 8
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 5
  %25 = load float, float* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 7
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 6
  %29 = load float, float* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 2, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 3, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 0, i32 1
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %37 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 1, i32 1
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %39 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 4, i32 1
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, i32 }* %21, i64 0, i32 4, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for27, %for_loop_body.lr.ph
  %.01834 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %235, %after_for27 ]
  %41 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %41, i64 0, i32 14
  %43 = load i8*, i8** %42, align 8
  %44 = getelementptr inbounds i8, i8* %43, i64 4
  %45 = bitcast i8* %44 to i32*
  %46 = load i32, i32* %45, align 4
  %47 = sdiv i32 %.01834, %46
  %48 = mul i32 %47, %46
  %49 = xor i32 %46, %.01834
  %50 = icmp slt i32 %49, 0
  %51 = icmp ne i32 %.01834, 0
  %52 = icmp ne i32 %48, %.01834
  %53 = and i1 %51, %50
  %54 = and i1 %53, %52
  %.neg27 = sext i1 %54 to i32
  %55 = add i32 %47, %.neg27
  %56 = mul i32 %55, %46
  %57 = sub i32 %.01834, %56
  %58 = mul i32 %55, %23
  %59 = mul i32 %57, %23
  %60 = getelementptr inbounds i8, i8* %43, i64 8
  %61 = bitcast i8* %60 to i32*
  %62 = load i32, i32* %61, align 4
  %63 = add i32 %58, -1
  %64 = add i32 %63, %62
  %65 = getelementptr inbounds i8, i8* %43, i64 12
  %66 = bitcast i8* %65 to i32*
  %67 = load i32, i32* %66, align 4
  %68 = add i32 %59, -1
  %69 = add i32 %68, %67
  %70 = load float*, float** %31, align 8
  %71 = load i32, i32* %32, align 4
  %72 = mul i32 %64, %71
  %73 = add i32 %69, %72
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, float* %70, i64 %74
  %76 = load float, float* %75, align 4
  %77 = icmp sgt i32 %63, -1
  br i1 %77, label %after_if, label %after_if.thread

after_for.loopexit:                               ; preds = %after_for27
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %78 = mul i32 %63, %71
  %79 = add i32 %69, %78
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, float* %70, i64 %80
  %82 = load float, float* %81, align 4
  %83 = fsub reassoc ninf nsz float %76, %82
  %84 = icmp sgt i32 %68, -1
  br i1 %84, label %true_block22, label %after_if17

after_if.thread:                                  ; preds = %for_loop_body
  %85 = icmp sgt i32 %68, -1
  br i1 %85, label %true_block15, label %after_if17.thread

true_block15:                                     ; preds = %after_if.thread
  %86 = add i32 %72, %68
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, float* %70, i64 %87
  %89 = load float, float* %88, align 4
  %90 = fsub reassoc ninf nsz float %76, %89
  %91 = load float*, float** %33, align 8
  %92 = load i32, i32* %34, align 4
  %93 = mul i32 %92, %64
  %94 = add i32 %93, %69
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, float* %91, i64 %95
  %97 = load float, float* %96, align 4
  %98 = add i32 %93, %68
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %91, i64 %99
  %101 = load float, float* %100, align 4
  %102 = fsub reassoc ninf nsz float %97, %101
  br label %after_if24

after_if17.thread:                                ; preds = %after_if.thread
  %103 = load float*, float** %33, align 8
  %104 = load i32, i32* %34, align 4
  %105 = mul i32 %104, %64
  %106 = add i32 %105, %69
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, float* %103, i64 %107
  %109 = load float, float* %108, align 4
  br label %after_if24

after_if17:                                       ; preds = %after_if
  %110 = load float*, float** %33, align 8
  %111 = load i32, i32* %34, align 4
  %112 = mul i32 %111, %64
  %113 = add i32 %112, %69
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, float* %110, i64 %114
  %116 = load float, float* %115, align 4
  %117 = mul i32 %111, %63
  %118 = add i32 %117, %69
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, float* %110, i64 %119
  %121 = load float, float* %120, align 4
  %122 = fsub reassoc ninf nsz float %116, %121
  br label %after_if24

true_block22:                                     ; preds = %after_if
  %123 = add i32 %72, %68
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %70, i64 %124
  %126 = load float, float* %125, align 4
  %127 = fsub reassoc ninf nsz float %83, %126
  %128 = add i32 %68, %78
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %70, i64 %129
  %131 = load float, float* %130, align 4
  %132 = fadd reassoc ninf nsz float %131, %127
  %133 = load float*, float** %33, align 8
  %134 = load i32, i32* %34, align 4
  %135 = mul i32 %134, %64
  %136 = add i32 %135, %69
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, float* %133, i64 %137
  %139 = load float, float* %138, align 4
  %140 = mul i32 %134, %63
  %141 = add i32 %140, %69
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, float* %133, i64 %142
  %144 = load float, float* %143, align 4
  %145 = add i32 %135, %68
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, float* %133, i64 %146
  %148 = load float, float* %147, align 4
  %149 = fadd reassoc ninf nsz float %144, %148
  %150 = fsub reassoc ninf nsz float %139, %149
  %151 = add i32 %140, %68
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, float* %133, i64 %152
  %154 = load float, float* %153, align 4
  %155 = fadd reassoc ninf nsz float %154, %150
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if17, %after_if17.thread, %true_block15
  %.222425163 = phi float [ %132, %true_block22 ], [ %83, %after_if17 ], [ %76, %after_if17.thread ], [ %90, %true_block15 ]
  %.2 = phi float [ %155, %true_block22 ], [ %122, %after_if17 ], [ %109, %after_if17.thread ], [ %102, %true_block15 ]
  %156 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %157 = tail call i32 @llvm.smax.i32(i32 %67, i32 0)
  %158 = mul i32 %157, %156
  %159 = icmp sgt i32 %158, 0
  br i1 %159, label %for_loop_body25.lr.ph, label %after_for27

for_loop_body25.lr.ph:                            ; preds = %after_if24
  %160 = load float*, float** %35, align 8
  %161 = load i32, i32* %36, align 4
  %162 = load float*, float** %37, align 8
  %163 = load i32, i32* %38, align 4
  %xtraiter = and i32 %158, 1
  %164 = icmp eq i32 %158, 1
  br i1 %164, label %after_for27.loopexit.unr-lcssa, label %for_loop_body25.lr.ph.new

for_loop_body25.lr.ph.new:                        ; preds = %for_loop_body25.lr.ph
  %unroll_iter = and i32 %158, -2
  %165 = add i32 %unroll_iter, -2
  %166 = lshr i32 %165, 1
  %167 = shl nuw i32 %166, 1
  br label %for_loop_body25

for_loop_body25:                                  ; preds = %for_loop_body25, %for_loop_body25.lr.ph.new
  %.033 = phi i32 [ 0, %for_loop_body25.lr.ph.new ], [ %199, %for_loop_body25 ]
  %.01732 = phi float [ 0.000000e+00, %for_loop_body25.lr.ph.new ], [ %198, %for_loop_body25 ]
  %168 = udiv i32 %.033, %157
  %.recomposed = urem i32 %.033, %157
  %169 = add i32 %168, %58
  %170 = add i32 %.recomposed, %59
  %171 = mul i32 %161, %169
  %172 = add i32 %170, %171
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, float* %160, i64 %173
  %175 = load float, float* %174, align 4
  %176 = mul i32 %163, %168
  %177 = add i32 %176, %.recomposed
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %162, i64 %178
  %180 = load float, float* %179, align 4
  %181 = fmul reassoc ninf nsz float %180, %175
  %182 = fadd reassoc ninf nsz float %181, %.01732
  %183 = add nuw nsw i32 %.033, 1
  %184 = udiv i32 %183, %157
  %.recomposed74 = urem i32 %183, %157
  %185 = add i32 %184, %58
  %186 = add i32 %.recomposed74, %59
  %187 = mul i32 %161, %185
  %188 = add i32 %186, %187
  %189 = sext i32 %188 to i64
  %190 = getelementptr float, float* %160, i64 %189
  %191 = load float, float* %190, align 4
  %192 = mul i32 %163, %184
  %193 = add i32 %192, %.recomposed74
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %162, i64 %194
  %196 = load float, float* %195, align 4
  %197 = fmul reassoc ninf nsz float %196, %191
  %198 = fadd reassoc ninf nsz float %197, %182
  %199 = add nuw i32 %.033, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %199
  br i1 %niter.ncmp.1, label %after_for27.loopexit.unr-lcssa.loopexit, label %for_loop_body25

after_for27.loopexit.unr-lcssa.loopexit:          ; preds = %for_loop_body25
  %200 = add i32 %167, 2
  br label %after_for27.loopexit.unr-lcssa

after_for27.loopexit.unr-lcssa:                   ; preds = %after_for27.loopexit.unr-lcssa.loopexit, %for_loop_body25.lr.ph
  %.lcssa.ph = phi float [ undef, %for_loop_body25.lr.ph ], [ %198, %after_for27.loopexit.unr-lcssa.loopexit ]
  %.033.unr = phi i32 [ 0, %for_loop_body25.lr.ph ], [ %200, %after_for27.loopexit.unr-lcssa.loopexit ]
  %.01732.unr = phi float [ 0.000000e+00, %for_loop_body25.lr.ph ], [ %198, %after_for27.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_for27, label %for_loop_body25.epil

for_loop_body25.epil:                             ; preds = %after_for27.loopexit.unr-lcssa
  %201 = udiv i32 %.033.unr, %157
  %.recomposed75 = urem i32 %.033.unr, %157
  %202 = add i32 %201, %58
  %203 = add i32 %.recomposed75, %59
  %204 = mul i32 %161, %202
  %205 = add i32 %203, %204
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, float* %160, i64 %206
  %208 = load float, float* %207, align 4
  %209 = mul i32 %163, %201
  %210 = add i32 %209, %.recomposed75
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %162, i64 %211
  %213 = load float, float* %212, align 4
  %214 = fmul reassoc ninf nsz float %213, %208
  %215 = fadd reassoc ninf nsz float %214, %.01732.unr
  br label %after_for27

after_for27:                                      ; preds = %for_loop_body25.epil, %after_for27.loopexit.unr-lcssa, %after_if24
  %.017.lcssa = phi float [ 0.000000e+00, %after_if24 ], [ %.lcssa.ph, %after_for27.loopexit.unr-lcssa ], [ %215, %for_loop_body25.epil ]
  %216 = fmul reassoc ninf nsz float %.222425163, %25
  %217 = fdiv reassoc ninf nsz float %216, %27
  %218 = fsub reassoc ninf nsz float %.017.lcssa, %217
  %219 = fmul reassoc ninf nsz float %.222425163, %.222425163
  %220 = fdiv reassoc ninf nsz float %219, %27
  %221 = fsub reassoc ninf nsz float %.2, %220
  %222 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %221, float 0.000000e+00)
  %223 = fmul reassoc ninf nsz float %222, %29
  %224 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %223, float 0x3D71979980000000)
  %225 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %224)
  %226 = fdiv reassoc ninf nsz float %218, %225
  %227 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %226, float -1.000000e+00)
  %228 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %227, float 1.000000e+00)
  %229 = load float*, float** %39, align 8
  %230 = load i32, i32* %40, align 4
  %231 = mul i32 %230, %55
  %232 = add i32 %231, %57
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, float* %229, i64 %233
  store float %228, float* %234, align 4
  %235 = add nsw i32 %.01834, 1
  %exitcond35.not = icmp eq i32 %235, %19
  br i1 %exitcond35.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.sqrt.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

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
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
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
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
