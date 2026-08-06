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
define void @_bm_grid_track_kernel_c702_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 8
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %18, i64 0, i32 3, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %18, i64 0, i32 3, i32 0, i32 1
  %22 = load i32, i32* %21, align 4
  %23 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %24 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %25 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  store i32 %24, i32* %29, align 4
  %30 = mul i32 %24, %23
  %31 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %31, i64 0, i32 14
  %33 = bitcast i8** %32 to i32**
  %34 = load i32*, i32** %33, align 8
  store i32 %30, i32* %34, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bm_grid_track_kernel_c702_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 6
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 5
  %25 = load i32, i32* %24, align 4
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 3, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 3, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 3, i32 0, i32 2
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 4, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 4, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 4, i32 0, i32 2
  %33 = mul i32 %25, %25
  %34 = sitofp i32 %33 to float
  %35 = fmul reassoc ninf nsz float %34, 0x3FA47AE140000000
  %36 = fmul reassoc ninf nsz float %34, 0x3FC99999A0000000
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.0244392 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %140, %after_if3 ]
  %37 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.0244392, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.0244392
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.0244392, 0
  %48 = icmp ne i32 %44, %.0244392
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg250 = sext i1 %50 to i32
  %51 = add i32 %43, %.neg250
  %52 = mul i32 %51, %42
  %53 = sub i32 %.0244392, %52
  %54 = mul i32 %53, %25
  %55 = add i32 %54, %23
  %56 = sitofp i32 %55 to float
  %57 = mul i32 %51, %25
  %58 = add i32 %57, %23
  %59 = load float*, float** %27, align 8
  %60 = load i32, i32* %28, align 4
  %61 = load i32, i32* %29, align 4
  %62 = mul i32 %51, %60
  %63 = add i32 %53, %62
  %64 = mul i32 %63, %61
  %65 = sext i32 %64 to i64
  %66 = getelementptr float, float* %59, i64 %65
  store float 0.000000e+00, float* %66, align 4
  %67 = load float*, float** %27, align 8
  %68 = load i32, i32* %28, align 4
  %69 = load i32, i32* %29, align 4
  %70 = mul i32 %68, %51
  %71 = add i32 %70, %53
  %72 = mul i32 %71, %69
  %73 = add i32 %72, 1
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, float* %67, i64 %74
  store float 0.000000e+00, float* %75, align 4
  %76 = load float*, float** %27, align 8
  %77 = load i32, i32* %28, align 4
  %78 = load i32, i32* %29, align 4
  %79 = mul i32 %77, %51
  %80 = add i32 %79, %53
  %81 = mul i32 %80, %78
  %82 = add i32 %81, 2
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, float* %76, i64 %83
  store float 0.000000e+00, float* %84, align 4
  %85 = load float*, float** %30, align 8
  %86 = load i32, i32* %31, align 4
  %87 = load i32, i32* %32, align 4
  %88 = mul i32 %86, %51
  %89 = add i32 %88, %53
  %90 = mul i32 %89, %87
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, float* %85, i64 %91
  store float 0.000000e+00, float* %92, align 4
  %93 = load float*, float** %30, align 8
  %94 = load i32, i32* %31, align 4
  %95 = load i32, i32* %32, align 4
  %96 = mul i32 %94, %51
  %97 = add i32 %96, %53
  %98 = mul i32 %97, %95
  %99 = add i32 %98, 1
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %93, i64 %100
  store float 0.000000e+00, float* %101, align 4
  %102 = load float*, float** %30, align 8
  %103 = load i32, i32* %31, align 4
  %104 = load i32, i32* %32, align 4
  %105 = mul i32 %103, %51
  %106 = add i32 %105, %53
  %107 = mul i32 %106, %104
  %108 = add i32 %107, 2
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %102, i64 %109
  store float 2.000000e+00, float* %110, align 4
  %111 = load float*, float** %30, align 8
  %112 = load i32, i32* %31, align 4
  %113 = load i32, i32* %32, align 4
  %114 = mul i32 %112, %51
  %115 = add i32 %114, %53
  %116 = mul i32 %115, %113
  %117 = add i32 %116, 3
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, float* %111, i64 %118
  store float 0.000000e+00, float* %119, align 4
  %120 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %121 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %120, i64 0, i32 14
  %122 = load i8*, i8** %121, align 8
  %123 = getelementptr inbounds i8, i8* %122, i64 8
  %124 = bitcast i8* %123 to i32*
  %125 = load i32, i32* %124, align 4
  %126 = sub i32 %125, %23
  %127 = sitofp i32 %126 to float
  %128 = fcmp reassoc ninf nsz olt float %56, %127
  br i1 %128, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %129 = sitofp i32 %58 to float
  %130 = getelementptr inbounds i8, i8* %122, i64 12
  %131 = bitcast i8* %130 to i32*
  %132 = load i32, i32* %131, align 4
  %133 = sub i32 %132, %23
  %134 = sitofp i32 %133 to float
  %135 = fcmp reassoc ninf nsz olt float %129, %134
  br i1 %135, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %136 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %20, align 8
  %137 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 8
  %138 = load i32, i32* %137, align 4
  %139 = icmp eq i32 %138, 1
  br i1 %139, label %true_block4, label %after_if6

after_if3:                                        ; preds = %after_if207, %true_block, %for_loop_body
  %140 = add nsw i32 %.0244392, 1
  %exitcond.not = icmp eq i32 %140, %19
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %141 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 2, i32 0, i32 1
  %142 = load i32, i32* %141, align 4
  %143 = add i32 %142, -1
  %144 = tail call i32 @llvm.smin.i32(i32 %53, i32 %143)
  %145 = tail call i32 @llvm.smax.i32(i32 %144, i32 0)
  %146 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 2, i32 0, i32 0
  %147 = load i32, i32* %146, align 4
  %148 = add i32 %147, -1
  %149 = tail call i32 @llvm.smin.i32(i32 %51, i32 %148)
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 2, i32 1
  %152 = load float*, float** %151, align 8
  %153 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 2, i32 0, i32 2
  %154 = load i32, i32* %153, align 4
  %155 = mul i32 %150, %142
  %156 = add i32 %155, %145
  %157 = mul i32 %156, %154
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, float* %152, i64 %158
  %160 = load float, float* %159, align 4
  %factor = fmul reassoc ninf nsz float %160, 2.000000e+00
  %161 = tail call reassoc ninf nsz float @llvm.round.f32(float %factor)
  %162 = fptosi float %161 to i32
  %163 = add i32 %157, 1
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %152, i64 %164
  %166 = load float, float* %165, align 4
  %factor279 = fmul reassoc ninf nsz float %166, 2.000000e+00
  %167 = tail call reassoc ninf nsz float @llvm.round.f32(float %factor279)
  %168 = fptosi float %167 to i32
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.0242 = phi i32 [ %162, %true_block4 ], [ 0, %true_block1 ]
  %.0241 = phi i32 [ %168, %true_block4 ], [ 0, %true_block1 ]
  %169 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 7
  %170 = load i32, i32* %169, align 4
  %neg = sub i32 0, %170
  %171 = add i32 %132, -1
  %172 = add i32 %125, -1
  %.not284 = icmp slt i32 %170, %neg
  br i1 %.not284, label %false_block8.thread, label %while_loop_body10.preheader.lr.ph

false_block8.thread:                              ; preds = %after_if6
  %173 = add i32 %.0241, -2
  br label %false_block22.thread

while_loop_body10.preheader.lr.ph:                ; preds = %after_if6
  %174 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 1, i32 1
  %175 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 1, i32 0, i32 1
  %176 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 0, i32 1
  %177 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %136, i64 0, i32 0, i32 0, i32 1
  %178 = load float*, float** %174, align 8
  %179 = load i32, i32* %175, align 4
  %180 = load float*, float** %176, align 8
  %181 = load i32, i32* %177, align 4
  %182 = add i32 %23, %.0242
  %183 = add i32 %182, %54
  br label %after_if14.lr.ph

after_if14.lr.ph:                                 ; preds = %false_block13, %while_loop_body10.preheader.lr.ph
  %.0226286 = phi i32 [ %neg, %while_loop_body10.preheader.lr.ph ], [ %194, %false_block13 ]
  %.0227285 = phi float [ 0.000000e+00, %while_loop_body10.preheader.lr.ph ], [ %211, %false_block13 ]
  %184 = add i32 %.0226286, %58
  %185 = add i32 %184, %.0241
  %186 = tail call i32 @llvm.smin.i32(i32 %185, i32 %171)
  %187 = tail call i32 @llvm.smax.i32(i32 %186, i32 0)
  %188 = tail call i32 @llvm.smin.i32(i32 %184, i32 %171)
  %189 = tail call i32 @llvm.smax.i32(i32 %188, i32 0)
  %190 = mul i32 %179, %187
  %191 = mul i32 %181, %189
  br label %after_if14

false_block8:                                     ; preds = %false_block13
  %192 = fcmp reassoc ninf nsz olt float %211, 0x46293E5940000000
  %.0229 = select i1 %192, float %211, float 0x46293E5940000000
  %193 = add i32 %.0241, -2
  br i1 false, label %false_block22.thread, label %while_loop_body25.preheader.lr.ph

while_loop_body25.preheader.lr.ph:                ; preds = %false_block8
  br label %after_if29.lr.ph

false_block13:                                    ; preds = %after_if14
  %194 = add i32 %.0226286, 2
  %.not = icmp sgt i32 %194, %170
  br i1 %.not, label %false_block8, label %after_if14.lr.ph

after_if14:                                       ; preds = %after_if14, %after_if14.lr.ph
  %.0225283 = phi i32 [ %neg, %after_if14.lr.ph ], [ %212, %after_if14 ]
  %.1228282 = phi float [ %.0227285, %after_if14.lr.ph ], [ %211, %after_if14 ]
  %195 = add i32 %55, %.0225283
  %196 = add i32 %183, %.0225283
  %197 = tail call i32 @llvm.smin.i32(i32 %196, i32 %172)
  %198 = tail call i32 @llvm.smax.i32(i32 %197, i32 0)
  %199 = tail call i32 @llvm.smin.i32(i32 %195, i32 %172)
  %200 = tail call i32 @llvm.smax.i32(i32 %199, i32 0)
  %201 = add i32 %190, %198
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %178, i64 %202
  %204 = load float, float* %203, align 4
  %205 = add i32 %191, %200
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, float* %180, i64 %206
  %208 = load float, float* %207, align 4
  %209 = fsub reassoc ninf nsz float %204, %208
  %210 = tail call float @llvm.fabs.f32(float %209)
  %211 = fadd reassoc ninf nsz float %210, %.1228282
  %212 = add i32 %.0225283, 2
  %.not278 = icmp sgt i32 %212, %170
  br i1 %.not278, label %false_block13, label %after_if14

after_if29.lr.ph:                                 ; preds = %false_block28, %while_loop_body25.preheader.lr.ph
  %.0222294 = phi i32 [ %neg, %while_loop_body25.preheader.lr.ph ], [ %225, %false_block28 ]
  %.0223293 = phi float [ 0.000000e+00, %while_loop_body25.preheader.lr.ph ], [ %242, %false_block28 ]
  %213 = add i32 %.0222294, %58
  %214 = add i32 %213, %193
  %215 = tail call i32 @llvm.smin.i32(i32 %214, i32 %171)
  %216 = tail call i32 @llvm.smax.i32(i32 %215, i32 0)
  %217 = tail call i32 @llvm.smin.i32(i32 %213, i32 %171)
  %218 = tail call i32 @llvm.smax.i32(i32 %217, i32 0)
  %219 = mul i32 %179, %216
  %220 = mul i32 %181, %218
  br label %after_if29

false_block22.thread:                             ; preds = %false_block8, %false_block8.thread
  %.ph = phi i32 [ %173, %false_block8.thread ], [ %193, %false_block8 ]
  %.0229408.ph = phi float [ 0.000000e+00, %false_block8.thread ], [ %.0229, %false_block8 ]
  %221 = fcmp reassoc ninf nsz ogt float %.0229408.ph, 0.000000e+00
  %.0237411 = select i1 %221, i32 %.ph, i32 %.0241
  %.1230412 = select i1 %221, float 0.000000e+00, float %.0229408.ph
  %222 = add i32 %.0241, 2
  br label %false_block37.thread

false_block22:                                    ; preds = %false_block28
  %223 = fcmp reassoc ninf nsz olt float %242, %.0229
  %.0237 = select i1 %223, i32 %193, i32 %.0241
  %.1230 = select i1 %223, float %242, float %.0229
  %224 = add i32 %.0241, 2
  br i1 false, label %false_block37.thread, label %while_loop_body40.preheader.lr.ph

while_loop_body40.preheader.lr.ph:                ; preds = %false_block22
  br label %after_if44.lr.ph

false_block28:                                    ; preds = %after_if29
  %225 = add i32 %.0222294, 2
  %.not251 = icmp sgt i32 %225, %170
  br i1 %.not251, label %false_block22, label %after_if29.lr.ph

after_if29:                                       ; preds = %after_if29, %after_if29.lr.ph
  %.0221290 = phi i32 [ %neg, %after_if29.lr.ph ], [ %243, %after_if29 ]
  %.1224289 = phi float [ %.0223293, %after_if29.lr.ph ], [ %242, %after_if29 ]
  %226 = add i32 %55, %.0221290
  %227 = add i32 %183, %.0221290
  %228 = tail call i32 @llvm.smin.i32(i32 %227, i32 %172)
  %229 = tail call i32 @llvm.smax.i32(i32 %228, i32 0)
  %230 = tail call i32 @llvm.smin.i32(i32 %226, i32 %172)
  %231 = tail call i32 @llvm.smax.i32(i32 %230, i32 0)
  %232 = add i32 %219, %229
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, float* %178, i64 %233
  %235 = load float, float* %234, align 4
  %236 = add i32 %220, %231
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, float* %180, i64 %237
  %239 = load float, float* %238, align 4
  %240 = fsub reassoc ninf nsz float %235, %239
  %241 = tail call float @llvm.fabs.f32(float %240)
  %242 = fadd reassoc ninf nsz float %241, %.1224289
  %243 = add i32 %.0221290, 2
  %.not277 = icmp sgt i32 %243, %170
  br i1 %.not277, label %false_block28, label %after_if29

after_if44.lr.ph:                                 ; preds = %false_block43, %while_loop_body40.preheader.lr.ph
  %.0218302 = phi i32 [ %neg, %while_loop_body40.preheader.lr.ph ], [ %256, %false_block43 ]
  %.0219301 = phi float [ 0.000000e+00, %while_loop_body40.preheader.lr.ph ], [ %273, %false_block43 ]
  %244 = add i32 %.0218302, %58
  %245 = add i32 %244, %224
  %246 = tail call i32 @llvm.smin.i32(i32 %245, i32 %171)
  %247 = tail call i32 @llvm.smax.i32(i32 %246, i32 0)
  %248 = tail call i32 @llvm.smin.i32(i32 %244, i32 %171)
  %249 = tail call i32 @llvm.smax.i32(i32 %248, i32 0)
  %250 = mul i32 %179, %247
  %251 = mul i32 %181, %249
  br label %after_if44

false_block37.thread:                             ; preds = %false_block22, %false_block22.thread
  %.ph415 = phi i32 [ %222, %false_block22.thread ], [ %224, %false_block22 ]
  %.1230414.ph = phi float [ %.1230412, %false_block22.thread ], [ %.1230, %false_block22 ]
  %.0237413.ph = phi i32 [ %.0237411, %false_block22.thread ], [ %.0237, %false_block22 ]
  %252 = fcmp reassoc ninf nsz ogt float %.1230414.ph, 0.000000e+00
  %.1238419 = select i1 %252, i32 %.ph415, i32 %.0237413.ph
  %.2231420 = select i1 %252, float 0.000000e+00, float %.1230414.ph
  %253 = add i32 %.0242, -2
  br label %false_block52.thread

false_block37:                                    ; preds = %false_block43
  %254 = fcmp reassoc ninf nsz olt float %273, %.1230
  %.1238 = select i1 %254, i32 %224, i32 %.0237
  %.2231 = select i1 %254, float %273, float %.1230
  %255 = add i32 %.0242, -2
  br i1 false, label %false_block52.thread, label %while_loop_body55.preheader.lr.ph

while_loop_body55.preheader.lr.ph:                ; preds = %false_block37
  br label %after_if59.lr.ph

false_block43:                                    ; preds = %after_if44
  %256 = add i32 %.0218302, 2
  %.not252 = icmp sgt i32 %256, %170
  br i1 %.not252, label %false_block37, label %after_if44.lr.ph

after_if44:                                       ; preds = %after_if44, %after_if44.lr.ph
  %.0217298 = phi i32 [ %neg, %after_if44.lr.ph ], [ %274, %after_if44 ]
  %.1220297 = phi float [ %.0219301, %after_if44.lr.ph ], [ %273, %after_if44 ]
  %257 = add i32 %55, %.0217298
  %258 = add i32 %183, %.0217298
  %259 = tail call i32 @llvm.smin.i32(i32 %258, i32 %172)
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = tail call i32 @llvm.smin.i32(i32 %257, i32 %172)
  %262 = tail call i32 @llvm.smax.i32(i32 %261, i32 0)
  %263 = add i32 %250, %260
  %264 = sext i32 %263 to i64
  %265 = getelementptr float, float* %178, i64 %264
  %266 = load float, float* %265, align 4
  %267 = add i32 %251, %262
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, float* %180, i64 %268
  %270 = load float, float* %269, align 4
  %271 = fsub reassoc ninf nsz float %266, %270
  %272 = tail call float @llvm.fabs.f32(float %271)
  %273 = fadd reassoc ninf nsz float %272, %.1220297
  %274 = add i32 %.0217298, 2
  %.not276 = icmp sgt i32 %274, %170
  br i1 %.not276, label %false_block43, label %after_if44

after_if59.lr.ph:                                 ; preds = %false_block58, %while_loop_body55.preheader.lr.ph
  %.0214310 = phi i32 [ %neg, %while_loop_body55.preheader.lr.ph ], [ %287, %false_block58 ]
  %.0215309 = phi float [ 0.000000e+00, %while_loop_body55.preheader.lr.ph ], [ %305, %false_block58 ]
  %275 = add i32 %.0214310, %58
  %276 = add i32 %275, %.0241
  %277 = tail call i32 @llvm.smin.i32(i32 %276, i32 %171)
  %278 = tail call i32 @llvm.smax.i32(i32 %277, i32 0)
  %279 = tail call i32 @llvm.smin.i32(i32 %275, i32 %171)
  %280 = tail call i32 @llvm.smax.i32(i32 %279, i32 0)
  %281 = mul i32 %179, %278
  %282 = mul i32 %181, %280
  br label %after_if59

false_block52.thread:                             ; preds = %false_block37, %false_block37.thread
  %.ph423 = phi i32 [ %253, %false_block37.thread ], [ %255, %false_block37 ]
  %.2231422.ph = phi float [ %.2231420, %false_block37.thread ], [ %.2231, %false_block37 ]
  %.1238421.ph = phi i32 [ %.1238419, %false_block37.thread ], [ %.1238, %false_block37 ]
  %283 = fcmp reassoc ninf nsz ogt float %.2231422.ph, 0.000000e+00
  %.2235427 = select i1 %283, i32 %.ph423, i32 %.0242
  %.3232428 = select i1 %283, float 0.000000e+00, float %.2231422.ph
  %284 = add i32 %.0242, 2
  br label %false_block67.thread

false_block52:                                    ; preds = %false_block58
  %285 = fcmp reassoc ninf nsz olt float %305, %.2231
  %.2235 = select i1 %285, i32 %255, i32 %.0242
  %.3232 = select i1 %285, float %305, float %.2231
  %286 = add i32 %.0242, 2
  br i1 false, label %false_block67.thread, label %while_loop_body70.preheader.lr.ph

while_loop_body70.preheader.lr.ph:                ; preds = %false_block52
  br label %after_if74.lr.ph

false_block58:                                    ; preds = %after_if59
  %287 = add i32 %.0214310, 2
  %.not253 = icmp sgt i32 %287, %170
  br i1 %.not253, label %false_block52, label %after_if59.lr.ph

after_if59:                                       ; preds = %after_if59, %after_if59.lr.ph
  %.0213306 = phi i32 [ %neg, %after_if59.lr.ph ], [ %306, %after_if59 ]
  %.1216305 = phi float [ %.0215309, %after_if59.lr.ph ], [ %305, %after_if59 ]
  %288 = add i32 %55, %.0213306
  %289 = add i32 %183, %.0213306
  %290 = add i32 %289, -2
  %291 = tail call i32 @llvm.smin.i32(i32 %290, i32 %172)
  %292 = tail call i32 @llvm.smax.i32(i32 %291, i32 0)
  %293 = tail call i32 @llvm.smin.i32(i32 %288, i32 %172)
  %294 = tail call i32 @llvm.smax.i32(i32 %293, i32 0)
  %295 = add i32 %281, %292
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, float* %178, i64 %296
  %298 = load float, float* %297, align 4
  %299 = add i32 %282, %294
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, float* %180, i64 %300
  %302 = load float, float* %301, align 4
  %303 = fsub reassoc ninf nsz float %298, %302
  %304 = tail call float @llvm.fabs.f32(float %303)
  %305 = fadd reassoc ninf nsz float %304, %.1216305
  %306 = add i32 %.0213306, 2
  %.not275 = icmp sgt i32 %306, %170
  br i1 %.not275, label %false_block58, label %after_if59

after_if74.lr.ph:                                 ; preds = %false_block73, %while_loop_body70.preheader.lr.ph
  %.0210318 = phi i32 [ %neg, %while_loop_body70.preheader.lr.ph ], [ %321, %false_block73 ]
  %.0211317 = phi float [ 0.000000e+00, %while_loop_body70.preheader.lr.ph ], [ %339, %false_block73 ]
  %307 = add i32 %.0210318, %58
  %308 = add i32 %307, %.0241
  %309 = tail call i32 @llvm.smin.i32(i32 %308, i32 %171)
  %310 = tail call i32 @llvm.smax.i32(i32 %309, i32 0)
  %311 = tail call i32 @llvm.smin.i32(i32 %307, i32 %171)
  %312 = tail call i32 @llvm.smax.i32(i32 %311, i32 0)
  %313 = mul i32 %179, %310
  %314 = mul i32 %181, %312
  br label %after_if74

false_block67.thread:                             ; preds = %false_block52, %false_block52.thread
  %.ph432 = phi i32 [ %284, %false_block52.thread ], [ %286, %false_block52 ]
  %.3232431.ph = phi float [ %.3232428, %false_block52.thread ], [ %.3232, %false_block52 ]
  %.2235430.ph = phi i32 [ %.2235427, %false_block52.thread ], [ %.2235, %false_block52 ]
  %.ph433 = phi i1 [ %283, %false_block52.thread ], [ %285, %false_block52 ]
  %.1238421429.ph = phi i32 [ %.1238421.ph, %false_block52.thread ], [ %.1238, %false_block52 ]
  %315 = fcmp reassoc ninf nsz ogt float %.3232431.ph, 0.000000e+00
  %316 = or i1 %.ph433, %315
  %.3240438 = select i1 %316, i32 %.0241, i32 %.1238421429.ph
  %.3236439 = select i1 %315, i32 %.ph432, i32 %.2235430.ph
  br label %false_block82.thread

false_block67:                                    ; preds = %false_block73
  %317 = fcmp reassoc ninf nsz olt float %339, %.3232
  %318 = or i1 %285, %317
  %.3240 = select i1 %318, i32 %.0241, i32 %.1238
  %.3236 = select i1 %317, i32 %286, i32 %.2235
  br i1 false, label %false_block82.thread, label %while_loop_body85.preheader.lr.ph

while_loop_body85.preheader.lr.ph:                ; preds = %false_block67
  %319 = add i32 %23, %.3236
  %320 = add i32 %319, %54
  br label %after_if89.lr.ph

false_block73:                                    ; preds = %after_if74
  %321 = add i32 %.0210318, 2
  %.not254 = icmp sgt i32 %321, %170
  br i1 %.not254, label %false_block67, label %after_if74.lr.ph

after_if74:                                       ; preds = %after_if74, %after_if74.lr.ph
  %.0209314 = phi i32 [ %neg, %after_if74.lr.ph ], [ %340, %after_if74 ]
  %.1212313 = phi float [ %.0211317, %after_if74.lr.ph ], [ %339, %after_if74 ]
  %322 = add i32 %55, %.0209314
  %323 = add i32 %183, %.0209314
  %324 = add i32 %323, 2
  %325 = tail call i32 @llvm.smin.i32(i32 %324, i32 %172)
  %326 = tail call i32 @llvm.smax.i32(i32 %325, i32 0)
  %327 = tail call i32 @llvm.smin.i32(i32 %322, i32 %172)
  %328 = tail call i32 @llvm.smax.i32(i32 %327, i32 0)
  %329 = add i32 %313, %326
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, float* %178, i64 %330
  %332 = load float, float* %331, align 4
  %333 = add i32 %314, %328
  %334 = sext i32 %333 to i64
  %335 = getelementptr float, float* %180, i64 %334
  %336 = load float, float* %335, align 4
  %337 = fsub reassoc ninf nsz float %332, %336
  %338 = tail call float @llvm.fabs.f32(float %337)
  %339 = fadd reassoc ninf nsz float %338, %.1212313
  %340 = add i32 %.0209314, 2
  %.not274 = icmp sgt i32 %340, %170
  br i1 %.not274, label %false_block73, label %after_if74

after_if89.lr.ph:                                 ; preds = %false_block88, %while_loop_body85.preheader.lr.ph
  %.0194326 = phi i32 [ %neg, %while_loop_body85.preheader.lr.ph ], [ %352, %false_block88 ]
  %.0195325 = phi float [ 0.000000e+00, %while_loop_body85.preheader.lr.ph ], [ %369, %false_block88 ]
  %341 = add i32 %.0194326, %58
  %342 = add i32 %341, %.3240
  %343 = tail call i32 @llvm.smin.i32(i32 %342, i32 %171)
  %344 = tail call i32 @llvm.smax.i32(i32 %343, i32 0)
  %345 = tail call i32 @llvm.smin.i32(i32 %341, i32 %171)
  %346 = tail call i32 @llvm.smax.i32(i32 %345, i32 0)
  %347 = mul i32 %179, %344
  %348 = mul i32 %181, %346
  br label %after_if89

false_block82.thread:                             ; preds = %false_block67, %false_block67.thread
  %.3236441.ph = phi i32 [ %.3236439, %false_block67.thread ], [ %.3236, %false_block67 ]
  %.3240440.ph = phi i32 [ %.3240438, %false_block67.thread ], [ %.3240, %false_block67 ]
  %349 = add i32 %.3240440.ph, -1
  br label %false_block97.thread

false_block82:                                    ; preds = %false_block88
  %350 = fcmp reassoc ninf nsz olt float %369, 0x46293E5940000000
  %.0197 = select i1 %350, float %369, float 0x46293E5940000000
  %351 = add i32 %.3240, -1
  br i1 false, label %false_block97.thread, label %while_loop_body100.preheader.lr.ph

while_loop_body100.preheader.lr.ph:               ; preds = %false_block82
  br label %after_if104.lr.ph

false_block88:                                    ; preds = %after_if89
  %352 = add i32 %.0194326, 2
  %.not255 = icmp sgt i32 %352, %170
  br i1 %.not255, label %false_block82, label %after_if89.lr.ph

after_if89:                                       ; preds = %after_if89, %after_if89.lr.ph
  %.0193322 = phi i32 [ %neg, %after_if89.lr.ph ], [ %370, %after_if89 ]
  %.1196321 = phi float [ %.0195325, %after_if89.lr.ph ], [ %369, %after_if89 ]
  %353 = add i32 %55, %.0193322
  %354 = add i32 %320, %.0193322
  %355 = tail call i32 @llvm.smin.i32(i32 %354, i32 %172)
  %356 = tail call i32 @llvm.smax.i32(i32 %355, i32 0)
  %357 = tail call i32 @llvm.smin.i32(i32 %353, i32 %172)
  %358 = tail call i32 @llvm.smax.i32(i32 %357, i32 0)
  %359 = add i32 %347, %356
  %360 = sext i32 %359 to i64
  %361 = getelementptr float, float* %178, i64 %360
  %362 = load float, float* %361, align 4
  %363 = add i32 %348, %358
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, float* %180, i64 %364
  %366 = load float, float* %365, align 4
  %367 = fsub reassoc ninf nsz float %362, %366
  %368 = tail call float @llvm.fabs.f32(float %367)
  %369 = fadd reassoc ninf nsz float %368, %.1196321
  %370 = add i32 %.0193322, 2
  %.not273 = icmp sgt i32 %370, %170
  br i1 %.not273, label %false_block88, label %after_if89

after_if104.lr.ph:                                ; preds = %false_block103, %while_loop_body100.preheader.lr.ph
  %.0190334 = phi i32 [ %neg, %while_loop_body100.preheader.lr.ph ], [ %383, %false_block103 ]
  %.0191333 = phi float [ 0.000000e+00, %while_loop_body100.preheader.lr.ph ], [ %400, %false_block103 ]
  %371 = add i32 %.0190334, %58
  %372 = add i32 %371, %351
  %373 = tail call i32 @llvm.smin.i32(i32 %372, i32 %171)
  %374 = tail call i32 @llvm.smax.i32(i32 %373, i32 0)
  %375 = tail call i32 @llvm.smin.i32(i32 %371, i32 %171)
  %376 = tail call i32 @llvm.smax.i32(i32 %375, i32 0)
  %377 = mul i32 %179, %374
  %378 = mul i32 %181, %376
  br label %after_if104

false_block97.thread:                             ; preds = %false_block82, %false_block82.thread
  %.ph449 = phi i32 [ %349, %false_block82.thread ], [ %351, %false_block82 ]
  %.0197448.ph = phi float [ 0.000000e+00, %false_block82.thread ], [ %.0197, %false_block82 ]
  %.3240440447.ph = phi i32 [ %.3240440.ph, %false_block82.thread ], [ %.3240, %false_block82 ]
  %.3236441446.ph = phi i32 [ %.3236441.ph, %false_block82.thread ], [ %.3236, %false_block82 ]
  %379 = fcmp reassoc ninf nsz ogt float %.0197448.ph, 0.000000e+00
  %.0205454 = select i1 %379, i32 %.ph449, i32 %.3240440447.ph
  %.1198455 = select i1 %379, float 0.000000e+00, float %.0197448.ph
  %380 = add i32 %.3240440447.ph, 1
  br label %false_block112.thread

false_block97:                                    ; preds = %false_block103
  %381 = fcmp reassoc ninf nsz olt float %400, %.0197
  %.0205 = select i1 %381, i32 %351, i32 %.3240
  %.1198 = select i1 %381, float %400, float %.0197
  %382 = add i32 %.3240, 1
  br i1 false, label %false_block112.thread, label %while_loop_body115.preheader.lr.ph

while_loop_body115.preheader.lr.ph:               ; preds = %false_block97
  br label %after_if119.lr.ph

false_block103:                                   ; preds = %after_if104
  %383 = add i32 %.0190334, 2
  %.not256 = icmp sgt i32 %383, %170
  br i1 %.not256, label %false_block97, label %after_if104.lr.ph

after_if104:                                      ; preds = %after_if104, %after_if104.lr.ph
  %.0189330 = phi i32 [ %neg, %after_if104.lr.ph ], [ %401, %after_if104 ]
  %.1192329 = phi float [ %.0191333, %after_if104.lr.ph ], [ %400, %after_if104 ]
  %384 = add i32 %55, %.0189330
  %385 = add i32 %320, %.0189330
  %386 = tail call i32 @llvm.smin.i32(i32 %385, i32 %172)
  %387 = tail call i32 @llvm.smax.i32(i32 %386, i32 0)
  %388 = tail call i32 @llvm.smin.i32(i32 %384, i32 %172)
  %389 = tail call i32 @llvm.smax.i32(i32 %388, i32 0)
  %390 = add i32 %377, %387
  %391 = sext i32 %390 to i64
  %392 = getelementptr float, float* %178, i64 %391
  %393 = load float, float* %392, align 4
  %394 = add i32 %378, %389
  %395 = sext i32 %394 to i64
  %396 = getelementptr float, float* %180, i64 %395
  %397 = load float, float* %396, align 4
  %398 = fsub reassoc ninf nsz float %393, %397
  %399 = tail call float @llvm.fabs.f32(float %398)
  %400 = fadd reassoc ninf nsz float %399, %.1192329
  %401 = add i32 %.0189330, 2
  %.not272 = icmp sgt i32 %401, %170
  br i1 %.not272, label %false_block103, label %after_if104

after_if119.lr.ph:                                ; preds = %false_block118, %while_loop_body115.preheader.lr.ph
  %.0186342 = phi i32 [ %neg, %while_loop_body115.preheader.lr.ph ], [ %414, %false_block118 ]
  %.0187341 = phi float [ 0.000000e+00, %while_loop_body115.preheader.lr.ph ], [ %431, %false_block118 ]
  %402 = add i32 %.0186342, %58
  %403 = add i32 %402, %382
  %404 = tail call i32 @llvm.smin.i32(i32 %403, i32 %171)
  %405 = tail call i32 @llvm.smax.i32(i32 %404, i32 0)
  %406 = tail call i32 @llvm.smin.i32(i32 %402, i32 %171)
  %407 = tail call i32 @llvm.smax.i32(i32 %406, i32 0)
  %408 = mul i32 %179, %405
  %409 = mul i32 %181, %407
  br label %after_if119

false_block112.thread:                            ; preds = %false_block97, %false_block97.thread
  %.ph460 = phi i32 [ %380, %false_block97.thread ], [ %382, %false_block97 ]
  %.1198459.ph = phi float [ %.1198455, %false_block97.thread ], [ %.1198, %false_block97 ]
  %.0205458.ph = phi i32 [ %.0205454, %false_block97.thread ], [ %.0205, %false_block97 ]
  %.3236441446457.ph = phi i32 [ %.3236441446.ph, %false_block97.thread ], [ %.3236, %false_block97 ]
  %.3240440447456.ph = phi i32 [ %.3240440447.ph, %false_block97.thread ], [ %.3240, %false_block97 ]
  %410 = fcmp reassoc ninf nsz ogt float %.1198459.ph, 0.000000e+00
  %.1206466 = select i1 %410, i32 %.ph460, i32 %.0205458.ph
  %.2199467 = select i1 %410, float 0.000000e+00, float %.1198459.ph
  %411 = add i32 %.3236441446457.ph, -1
  br label %false_block127.thread

false_block112:                                   ; preds = %false_block118
  %412 = fcmp reassoc ninf nsz olt float %431, %.1198
  %.1206 = select i1 %412, i32 %382, i32 %.0205
  %.2199 = select i1 %412, float %431, float %.1198
  %413 = add i32 %.3236, -1
  br i1 false, label %false_block127.thread, label %while_loop_body130.preheader.lr.ph

while_loop_body130.preheader.lr.ph:               ; preds = %false_block112
  br label %after_if134.lr.ph

false_block118:                                   ; preds = %after_if119
  %414 = add i32 %.0186342, 2
  %.not257 = icmp sgt i32 %414, %170
  br i1 %.not257, label %false_block112, label %after_if119.lr.ph

after_if119:                                      ; preds = %after_if119, %after_if119.lr.ph
  %.0185338 = phi i32 [ %neg, %after_if119.lr.ph ], [ %432, %after_if119 ]
  %.1188337 = phi float [ %.0187341, %after_if119.lr.ph ], [ %431, %after_if119 ]
  %415 = add i32 %55, %.0185338
  %416 = add i32 %320, %.0185338
  %417 = tail call i32 @llvm.smin.i32(i32 %416, i32 %172)
  %418 = tail call i32 @llvm.smax.i32(i32 %417, i32 0)
  %419 = tail call i32 @llvm.smin.i32(i32 %415, i32 %172)
  %420 = tail call i32 @llvm.smax.i32(i32 %419, i32 0)
  %421 = add i32 %408, %418
  %422 = sext i32 %421 to i64
  %423 = getelementptr float, float* %178, i64 %422
  %424 = load float, float* %423, align 4
  %425 = add i32 %409, %420
  %426 = sext i32 %425 to i64
  %427 = getelementptr float, float* %180, i64 %426
  %428 = load float, float* %427, align 4
  %429 = fsub reassoc ninf nsz float %424, %428
  %430 = tail call float @llvm.fabs.f32(float %429)
  %431 = fadd reassoc ninf nsz float %430, %.1188337
  %432 = add i32 %.0185338, 2
  %.not271 = icmp sgt i32 %432, %170
  br i1 %.not271, label %false_block118, label %after_if119

after_if134.lr.ph:                                ; preds = %false_block133, %while_loop_body130.preheader.lr.ph
  %.0182350 = phi i32 [ %neg, %while_loop_body130.preheader.lr.ph ], [ %445, %false_block133 ]
  %.0183349 = phi float [ 0.000000e+00, %while_loop_body130.preheader.lr.ph ], [ %463, %false_block133 ]
  %433 = add i32 %.0182350, %58
  %434 = add i32 %433, %.3240
  %435 = tail call i32 @llvm.smin.i32(i32 %434, i32 %171)
  %436 = tail call i32 @llvm.smax.i32(i32 %435, i32 0)
  %437 = tail call i32 @llvm.smin.i32(i32 %433, i32 %171)
  %438 = tail call i32 @llvm.smax.i32(i32 %437, i32 0)
  %439 = mul i32 %179, %436
  %440 = mul i32 %181, %438
  br label %after_if134

false_block127.thread:                            ; preds = %false_block112, %false_block112.thread
  %.ph472 = phi i32 [ %411, %false_block112.thread ], [ %413, %false_block112 ]
  %.2199471.ph = phi float [ %.2199467, %false_block112.thread ], [ %.2199, %false_block112 ]
  %.1206470.ph = phi i32 [ %.1206466, %false_block112.thread ], [ %.1206, %false_block112 ]
  %.3240440447456469.ph = phi i32 [ %.3240440447456.ph, %false_block112.thread ], [ %.3240, %false_block112 ]
  %.3236441446457468.ph = phi i32 [ %.3236441446457.ph, %false_block112.thread ], [ %.3236, %false_block112 ]
  %441 = fcmp reassoc ninf nsz ogt float %.2199471.ph, 0.000000e+00
  %.2203478 = select i1 %441, i32 %.ph472, i32 %.3236441446457468.ph
  %.3200479 = select i1 %441, float 0.000000e+00, float %.2199471.ph
  %442 = add i32 %.3236441446457468.ph, 1
  br label %false_block142.thread

false_block127:                                   ; preds = %false_block133
  %443 = fcmp reassoc ninf nsz olt float %463, %.2199
  %.2203 = select i1 %443, i32 %413, i32 %.3236
  %.3200 = select i1 %443, float %463, float %.2199
  %444 = add i32 %.3236, 1
  br i1 false, label %false_block142.thread, label %while_loop_body145.preheader.lr.ph

while_loop_body145.preheader.lr.ph:               ; preds = %false_block127
  br label %after_if149.lr.ph

false_block133:                                   ; preds = %after_if134
  %445 = add i32 %.0182350, 2
  %.not258 = icmp sgt i32 %445, %170
  br i1 %.not258, label %false_block127, label %after_if134.lr.ph

after_if134:                                      ; preds = %after_if134, %after_if134.lr.ph
  %.0181346 = phi i32 [ %neg, %after_if134.lr.ph ], [ %464, %after_if134 ]
  %.1184345 = phi float [ %.0183349, %after_if134.lr.ph ], [ %463, %after_if134 ]
  %446 = add i32 %55, %.0181346
  %447 = add i32 %320, %.0181346
  %448 = add i32 %447, -1
  %449 = tail call i32 @llvm.smin.i32(i32 %448, i32 %172)
  %450 = tail call i32 @llvm.smax.i32(i32 %449, i32 0)
  %451 = tail call i32 @llvm.smin.i32(i32 %446, i32 %172)
  %452 = tail call i32 @llvm.smax.i32(i32 %451, i32 0)
  %453 = add i32 %439, %450
  %454 = sext i32 %453 to i64
  %455 = getelementptr float, float* %178, i64 %454
  %456 = load float, float* %455, align 4
  %457 = add i32 %440, %452
  %458 = sext i32 %457 to i64
  %459 = getelementptr float, float* %180, i64 %458
  %460 = load float, float* %459, align 4
  %461 = fsub reassoc ninf nsz float %456, %460
  %462 = tail call float @llvm.fabs.f32(float %461)
  %463 = fadd reassoc ninf nsz float %462, %.1184345
  %464 = add i32 %.0181346, 2
  %.not270 = icmp sgt i32 %464, %170
  br i1 %.not270, label %false_block133, label %after_if134

after_if149.lr.ph:                                ; preds = %false_block148, %while_loop_body145.preheader.lr.ph
  %.0178358 = phi i32 [ %neg, %while_loop_body145.preheader.lr.ph ], [ %479, %false_block148 ]
  %.0179357 = phi float [ 0.000000e+00, %while_loop_body145.preheader.lr.ph ], [ %497, %false_block148 ]
  %465 = add i32 %.0178358, %58
  %466 = add i32 %465, %.3240
  %467 = tail call i32 @llvm.smin.i32(i32 %466, i32 %171)
  %468 = tail call i32 @llvm.smax.i32(i32 %467, i32 0)
  %469 = tail call i32 @llvm.smin.i32(i32 %465, i32 %171)
  %470 = tail call i32 @llvm.smax.i32(i32 %469, i32 0)
  %471 = mul i32 %179, %468
  %472 = mul i32 %181, %470
  br label %after_if149

false_block142.thread:                            ; preds = %false_block127, %false_block127.thread
  %.ph484 = phi i32 [ %442, %false_block127.thread ], [ %444, %false_block127 ]
  %.3200483.ph = phi float [ %.3200479, %false_block127.thread ], [ %.3200, %false_block127 ]
  %.2203482.ph = phi i32 [ %.2203478, %false_block127.thread ], [ %.2203, %false_block127 ]
  %.ph485 = phi i1 [ %441, %false_block127.thread ], [ %443, %false_block127 ]
  %.3240440447456469481.ph = phi i32 [ %.3240440447456469.ph, %false_block127.thread ], [ %.3240, %false_block127 ]
  %.1206470480.ph = phi i32 [ %.1206470.ph, %false_block127.thread ], [ %.1206, %false_block127 ]
  %473 = fcmp reassoc ninf nsz ogt float %.3200483.ph, 0.000000e+00
  %474 = or i1 %.ph485, %473
  %.3208491 = select i1 %474, i32 %.3240440447456469481.ph, i32 %.1206470480.ph
  %.3204492 = select i1 %473, i32 %.ph484, i32 %.2203482.ph
  %.4493 = select i1 %473, float 0.000000e+00, float %.3200483.ph
  br label %false_block193

false_block142:                                   ; preds = %false_block148
  %475 = fcmp reassoc ninf nsz olt float %497, %.3200
  %476 = or i1 %443, %475
  %.3208 = select i1 %476, i32 %.3240, i32 %.1206
  %.3204 = select i1 %475, i32 %444, i32 %.2203
  %.4 = select i1 %475, float %497, float %.3200
  br i1 false, label %false_block142.false_block193_crit_edge, label %while_loop_body160.preheader.lr.ph

false_block142.false_block193_crit_edge:          ; preds = %false_block142
  br label %false_block193

while_loop_body160.preheader.lr.ph:               ; preds = %false_block142
  %477 = add i32 %23, %.3204
  %478 = add i32 %477, %54
  br label %after_if164.lr.ph

false_block148:                                   ; preds = %after_if149
  %479 = add i32 %.0178358, 2
  %.not259 = icmp sgt i32 %479, %170
  br i1 %.not259, label %false_block142, label %after_if149.lr.ph

after_if149:                                      ; preds = %after_if149, %after_if149.lr.ph
  %.0177354 = phi i32 [ %neg, %after_if149.lr.ph ], [ %498, %after_if149 ]
  %.1180353 = phi float [ %.0179357, %after_if149.lr.ph ], [ %497, %after_if149 ]
  %480 = add i32 %55, %.0177354
  %481 = add i32 %320, %.0177354
  %482 = add i32 %481, 1
  %483 = tail call i32 @llvm.smin.i32(i32 %482, i32 %172)
  %484 = tail call i32 @llvm.smax.i32(i32 %483, i32 0)
  %485 = tail call i32 @llvm.smin.i32(i32 %480, i32 %172)
  %486 = tail call i32 @llvm.smax.i32(i32 %485, i32 0)
  %487 = add i32 %471, %484
  %488 = sext i32 %487 to i64
  %489 = getelementptr float, float* %178, i64 %488
  %490 = load float, float* %489, align 4
  %491 = add i32 %472, %486
  %492 = sext i32 %491 to i64
  %493 = getelementptr float, float* %180, i64 %492
  %494 = load float, float* %493, align 4
  %495 = fsub reassoc ninf nsz float %490, %494
  %496 = tail call float @llvm.fabs.f32(float %495)
  %497 = fadd reassoc ninf nsz float %496, %.1180353
  %498 = add i32 %.0177354, 2
  %.not269 = icmp sgt i32 %498, %170
  br i1 %.not269, label %false_block148, label %after_if149

while_loop_body166.preheader:                     ; preds = %false_block163
  br i1 false, label %while_loop_body166.preheader.false_block193_crit_edge, label %while_loop_body172.preheader.lr.ph

while_loop_body166.preheader.false_block193_crit_edge: ; preds = %while_loop_body166.preheader
  br label %false_block193

while_loop_body172.preheader.lr.ph:               ; preds = %while_loop_body166.preheader
  br label %after_if176.lr.ph

after_if164.lr.ph:                                ; preds = %false_block163, %while_loop_body160.preheader.lr.ph
  %.0167366 = phi i32 [ %neg, %while_loop_body160.preheader.lr.ph ], [ %507, %false_block163 ]
  %.0175365 = phi float [ 0.000000e+00, %while_loop_body160.preheader.lr.ph ], [ %525, %false_block163 ]
  %499 = add i32 %.0167366, %58
  %500 = add i32 %499, %.3208
  %501 = tail call i32 @llvm.smin.i32(i32 %500, i32 %171)
  %502 = tail call i32 @llvm.smax.i32(i32 %501, i32 0)
  %503 = tail call i32 @llvm.smin.i32(i32 %499, i32 %171)
  %504 = tail call i32 @llvm.smax.i32(i32 %503, i32 0)
  %505 = mul i32 %179, %502
  %506 = mul i32 %181, %504
  br label %after_if164

false_block163:                                   ; preds = %after_if164
  %507 = add i32 %.0167366, 2
  %.not260 = icmp sgt i32 %507, %170
  br i1 %.not260, label %while_loop_body166.preheader, label %after_if164.lr.ph

after_if164:                                      ; preds = %after_if164, %after_if164.lr.ph
  %.0166362 = phi i32 [ %neg, %after_if164.lr.ph ], [ %526, %after_if164 ]
  %.1176361 = phi float [ %.0175365, %after_if164.lr.ph ], [ %525, %after_if164 ]
  %508 = add i32 %55, %.0166362
  %509 = add i32 %478, %.0166362
  %510 = add i32 %509, -1
  %511 = tail call i32 @llvm.smin.i32(i32 %510, i32 %172)
  %512 = tail call i32 @llvm.smax.i32(i32 %511, i32 0)
  %513 = tail call i32 @llvm.smin.i32(i32 %508, i32 %172)
  %514 = tail call i32 @llvm.smax.i32(i32 %513, i32 0)
  %515 = add i32 %505, %512
  %516 = sext i32 %515 to i64
  %517 = getelementptr float, float* %178, i64 %516
  %518 = load float, float* %517, align 4
  %519 = add i32 %506, %514
  %520 = sext i32 %519 to i64
  %521 = getelementptr float, float* %180, i64 %520
  %522 = load float, float* %521, align 4
  %523 = fsub reassoc ninf nsz float %518, %522
  %524 = tail call float @llvm.fabs.f32(float %523)
  %525 = fadd reassoc ninf nsz float %524, %.1176361
  %526 = add i32 %.0166362, 2
  %.not268 = icmp sgt i32 %526, %170
  br i1 %.not268, label %false_block163, label %after_if164

while_loop_body178.preheader:                     ; preds = %false_block175
  br i1 false, label %while_loop_body178.preheader.false_block193_crit_edge, label %while_loop_body184.preheader.lr.ph

while_loop_body178.preheader.false_block193_crit_edge: ; preds = %while_loop_body178.preheader
  br label %false_block193

while_loop_body184.preheader.lr.ph:               ; preds = %while_loop_body178.preheader
  %527 = add i32 %.3208, -1
  br label %after_if188.lr.ph

after_if176.lr.ph:                                ; preds = %false_block175, %while_loop_body172.preheader.lr.ph
  %.1168374 = phi i32 [ %neg, %while_loop_body172.preheader.lr.ph ], [ %536, %false_block175 ]
  %.0173373 = phi float [ 0.000000e+00, %while_loop_body172.preheader.lr.ph ], [ %554, %false_block175 ]
  %528 = add i32 %.1168374, %58
  %529 = add i32 %528, %.3208
  %530 = tail call i32 @llvm.smin.i32(i32 %529, i32 %171)
  %531 = tail call i32 @llvm.smax.i32(i32 %530, i32 0)
  %532 = tail call i32 @llvm.smin.i32(i32 %528, i32 %171)
  %533 = tail call i32 @llvm.smax.i32(i32 %532, i32 0)
  %534 = mul i32 %179, %531
  %535 = mul i32 %181, %533
  br label %after_if176

false_block175:                                   ; preds = %after_if176
  %536 = add i32 %.1168374, 2
  %.not261 = icmp sgt i32 %536, %170
  br i1 %.not261, label %while_loop_body178.preheader, label %after_if176.lr.ph

after_if176:                                      ; preds = %after_if176, %after_if176.lr.ph
  %.0165370 = phi i32 [ %neg, %after_if176.lr.ph ], [ %555, %after_if176 ]
  %.1174369 = phi float [ %.0173373, %after_if176.lr.ph ], [ %554, %after_if176 ]
  %537 = add i32 %55, %.0165370
  %538 = add i32 %478, %.0165370
  %539 = add i32 %538, 1
  %540 = tail call i32 @llvm.smin.i32(i32 %539, i32 %172)
  %541 = tail call i32 @llvm.smax.i32(i32 %540, i32 0)
  %542 = tail call i32 @llvm.smin.i32(i32 %537, i32 %172)
  %543 = tail call i32 @llvm.smax.i32(i32 %542, i32 0)
  %544 = add i32 %534, %541
  %545 = sext i32 %544 to i64
  %546 = getelementptr float, float* %178, i64 %545
  %547 = load float, float* %546, align 4
  %548 = add i32 %535, %543
  %549 = sext i32 %548 to i64
  %550 = getelementptr float, float* %180, i64 %549
  %551 = load float, float* %550, align 4
  %552 = fsub reassoc ninf nsz float %547, %551
  %553 = tail call float @llvm.fabs.f32(float %552)
  %554 = fadd reassoc ninf nsz float %553, %.1174369
  %555 = add i32 %.0165370, 2
  %.not267 = icmp sgt i32 %555, %170
  br i1 %.not267, label %false_block175, label %after_if176

while_loop_body190.preheader:                     ; preds = %false_block187
  br i1 false, label %while_loop_body190.preheader.false_block193_crit_edge, label %while_loop_body196.preheader.lr.ph

while_loop_body190.preheader.false_block193_crit_edge: ; preds = %while_loop_body190.preheader
  br label %false_block193

while_loop_body196.preheader.lr.ph:               ; preds = %while_loop_body190.preheader
  %556 = add i32 %.3208, 1
  br label %after_if200.lr.ph

after_if188.lr.ph:                                ; preds = %false_block187, %while_loop_body184.preheader.lr.ph
  %.2382 = phi i32 [ %neg, %while_loop_body184.preheader.lr.ph ], [ %565, %false_block187 ]
  %.0171381 = phi float [ 0.000000e+00, %while_loop_body184.preheader.lr.ph ], [ %582, %false_block187 ]
  %557 = add i32 %.2382, %58
  %558 = add i32 %527, %557
  %559 = tail call i32 @llvm.smin.i32(i32 %558, i32 %171)
  %560 = tail call i32 @llvm.smax.i32(i32 %559, i32 0)
  %561 = tail call i32 @llvm.smin.i32(i32 %557, i32 %171)
  %562 = tail call i32 @llvm.smax.i32(i32 %561, i32 0)
  %563 = mul i32 %179, %560
  %564 = mul i32 %181, %562
  br label %after_if188

false_block187:                                   ; preds = %after_if188
  %565 = add i32 %.2382, 2
  %.not262 = icmp sgt i32 %565, %170
  br i1 %.not262, label %while_loop_body190.preheader, label %after_if188.lr.ph

after_if188:                                      ; preds = %after_if188, %after_if188.lr.ph
  %.0164378 = phi i32 [ %neg, %after_if188.lr.ph ], [ %583, %after_if188 ]
  %.1172377 = phi float [ %.0171381, %after_if188.lr.ph ], [ %582, %after_if188 ]
  %566 = add i32 %55, %.0164378
  %567 = add i32 %478, %.0164378
  %568 = tail call i32 @llvm.smin.i32(i32 %567, i32 %172)
  %569 = tail call i32 @llvm.smax.i32(i32 %568, i32 0)
  %570 = tail call i32 @llvm.smin.i32(i32 %566, i32 %172)
  %571 = tail call i32 @llvm.smax.i32(i32 %570, i32 0)
  %572 = add i32 %563, %569
  %573 = sext i32 %572 to i64
  %574 = getelementptr float, float* %178, i64 %573
  %575 = load float, float* %574, align 4
  %576 = add i32 %564, %571
  %577 = sext i32 %576 to i64
  %578 = getelementptr float, float* %180, i64 %577
  %579 = load float, float* %578, align 4
  %580 = fsub reassoc ninf nsz float %575, %579
  %581 = tail call float @llvm.fabs.f32(float %580)
  %582 = fadd reassoc ninf nsz float %581, %.1172377
  %583 = add i32 %.0164378, 2
  %.not266 = icmp sgt i32 %583, %170
  br i1 %.not266, label %false_block187, label %after_if188

after_if200.lr.ph:                                ; preds = %false_block199, %while_loop_body196.preheader.lr.ph
  %.3390 = phi i32 [ %neg, %while_loop_body196.preheader.lr.ph ], [ %596, %false_block199 ]
  %.0169389 = phi float [ 0.000000e+00, %while_loop_body196.preheader.lr.ph ], [ %613, %false_block199 ]
  %584 = add i32 %.3390, %58
  %585 = add i32 %556, %584
  %586 = tail call i32 @llvm.smin.i32(i32 %585, i32 %171)
  %587 = tail call i32 @llvm.smax.i32(i32 %586, i32 0)
  %588 = tail call i32 @llvm.smin.i32(i32 %584, i32 %171)
  %589 = tail call i32 @llvm.smax.i32(i32 %588, i32 0)
  %590 = mul i32 %179, %587
  %591 = mul i32 %181, %589
  br label %after_if200

false_block193.loopexit:                          ; preds = %false_block199
  br label %false_block193

false_block193:                                   ; preds = %false_block193.loopexit, %while_loop_body190.preheader.false_block193_crit_edge, %while_loop_body178.preheader.false_block193_crit_edge, %while_loop_body166.preheader.false_block193_crit_edge, %false_block142.false_block193_crit_edge, %false_block142.thread
  %.0171.lcssa526 = phi float [ %582, %while_loop_body190.preheader.false_block193_crit_edge ], [ 0.000000e+00, %while_loop_body178.preheader.false_block193_crit_edge ], [ 0.000000e+00, %while_loop_body166.preheader.false_block193_crit_edge ], [ 0.000000e+00, %false_block142.thread ], [ 0.000000e+00, %false_block142.false_block193_crit_edge ], [ %582, %false_block193.loopexit ]
  %.0175.lcssa504510525 = phi float [ %525, %while_loop_body190.preheader.false_block193_crit_edge ], [ %525, %while_loop_body178.preheader.false_block193_crit_edge ], [ %525, %while_loop_body166.preheader.false_block193_crit_edge ], [ 0.000000e+00, %false_block142.thread ], [ 0.000000e+00, %false_block142.false_block193_crit_edge ], [ %525, %false_block193.loopexit ]
  %.3208494503511524 = phi i32 [ %.3208, %while_loop_body190.preheader.false_block193_crit_edge ], [ %.3208, %while_loop_body178.preheader.false_block193_crit_edge ], [ %.3208, %while_loop_body166.preheader.false_block193_crit_edge ], [ %.3208491, %false_block142.thread ], [ %.3208, %false_block142.false_block193_crit_edge ], [ %.3208, %false_block193.loopexit ]
  %.3204495502512523 = phi i32 [ %.3204, %while_loop_body190.preheader.false_block193_crit_edge ], [ %.3204, %while_loop_body178.preheader.false_block193_crit_edge ], [ %.3204, %while_loop_body166.preheader.false_block193_crit_edge ], [ %.3204492, %false_block142.thread ], [ %.3204, %false_block142.false_block193_crit_edge ], [ %.3204, %false_block193.loopexit ]
  %.4496501513522 = phi float [ %.4, %while_loop_body190.preheader.false_block193_crit_edge ], [ %.4, %while_loop_body178.preheader.false_block193_crit_edge ], [ %.4, %while_loop_body166.preheader.false_block193_crit_edge ], [ %.4493, %false_block142.thread ], [ %.4, %false_block142.false_block193_crit_edge ], [ %.4, %false_block193.loopexit ]
  %.0173.lcssa514521 = phi float [ %554, %while_loop_body190.preheader.false_block193_crit_edge ], [ %554, %while_loop_body178.preheader.false_block193_crit_edge ], [ 0.000000e+00, %while_loop_body166.preheader.false_block193_crit_edge ], [ 0.000000e+00, %false_block142.thread ], [ 0.000000e+00, %false_block142.false_block193_crit_edge ], [ %554, %false_block193.loopexit ]
  %.0169.lcssa = phi float [ 0.000000e+00, %while_loop_body190.preheader.false_block193_crit_edge ], [ 0.000000e+00, %while_loop_body178.preheader.false_block193_crit_edge ], [ 0.000000e+00, %while_loop_body166.preheader.false_block193_crit_edge ], [ 0.000000e+00, %false_block142.thread ], [ 0.000000e+00, %false_block142.false_block193_crit_edge ], [ %613, %false_block193.loopexit ]
  %factor280 = fmul reassoc ninf nsz float %.4496501513522, 2.000000e+00
  %592 = fsub reassoc ninf nsz float %.0173.lcssa514521, %factor280
  %593 = fadd reassoc ninf nsz float %592, %.0175.lcssa504510525
  %594 = tail call float @llvm.fabs.f32(float %593)
  %595 = fcmp reassoc ninf nsz ogt float %594, 0x3F1A36E2E0000000
  br i1 %595, label %true_block202, label %after_if204

false_block199:                                   ; preds = %after_if200
  %596 = add i32 %.3390, 2
  %.not263 = icmp sgt i32 %596, %170
  br i1 %.not263, label %false_block193.loopexit, label %after_if200.lr.ph

after_if200:                                      ; preds = %after_if200, %after_if200.lr.ph
  %.0163386 = phi i32 [ %neg, %after_if200.lr.ph ], [ %614, %after_if200 ]
  %.1170385 = phi float [ %.0169389, %after_if200.lr.ph ], [ %613, %after_if200 ]
  %597 = add i32 %55, %.0163386
  %598 = add i32 %478, %.0163386
  %599 = tail call i32 @llvm.smin.i32(i32 %598, i32 %172)
  %600 = tail call i32 @llvm.smax.i32(i32 %599, i32 0)
  %601 = tail call i32 @llvm.smin.i32(i32 %597, i32 %172)
  %602 = tail call i32 @llvm.smax.i32(i32 %601, i32 0)
  %603 = add i32 %590, %600
  %604 = sext i32 %603 to i64
  %605 = getelementptr float, float* %178, i64 %604
  %606 = load float, float* %605, align 4
  %607 = add i32 %591, %602
  %608 = sext i32 %607 to i64
  %609 = getelementptr float, float* %180, i64 %608
  %610 = load float, float* %609, align 4
  %611 = fsub reassoc ninf nsz float %606, %610
  %612 = tail call float @llvm.fabs.f32(float %611)
  %613 = fadd reassoc ninf nsz float %612, %.1170385
  %614 = add i32 %.0163386, 2
  %.not265 = icmp sgt i32 %614, %170
  br i1 %.not265, label %false_block199, label %after_if200

true_block202:                                    ; preds = %false_block193
  %615 = fsub reassoc ninf nsz float %.0173.lcssa514521, %.0175.lcssa504510525
  %616 = fmul reassoc ninf nsz float %615, -5.000000e-01
  %617 = fdiv reassoc ninf nsz float %616, %593
  %618 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %617, float 5.000000e-01)
  %619 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %618, float -5.000000e-01)
  br label %after_if204

after_if204:                                      ; preds = %true_block202, %false_block193
  %.0162 = phi float [ %619, %true_block202 ], [ 0.000000e+00, %false_block193 ]
  %620 = fsub reassoc ninf nsz float %.0169.lcssa, %factor280
  %621 = fadd reassoc ninf nsz float %620, %.0171.lcssa526
  %622 = tail call float @llvm.fabs.f32(float %621)
  %623 = fcmp reassoc ninf nsz ogt float %622, 0x3F1A36E2E0000000
  br i1 %623, label %true_block205, label %after_if207

true_block205:                                    ; preds = %after_if204
  %624 = fsub reassoc ninf nsz float %.0169.lcssa, %.0171.lcssa526
  %625 = fmul reassoc ninf nsz float %624, -5.000000e-01
  %626 = fdiv reassoc ninf nsz float %625, %621
  %627 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %626, float 5.000000e-01)
  %628 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %627, float -5.000000e-01)
  br label %after_if207

after_if207:                                      ; preds = %true_block205, %after_if204
  %.0161 = phi float [ %628, %true_block205 ], [ 0.000000e+00, %after_if204 ]
  %629 = sitofp i32 %.3204495502512523 to float
  %630 = fadd reassoc ninf nsz float %.0162, %629
  %631 = sitofp i32 %.3208494503511524 to float
  %632 = fadd reassoc ninf nsz float %.0161, %631
  %633 = shl i32 %170, 1
  %634 = add i32 %170, %25
  %635 = shl i32 %634, 1
  %636 = sitofp i32 %635 to float
  %neg208 = fneg reassoc ninf nsz float %636
  %637 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %636, float %630)
  %638 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg208, float %637)
  %639 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %636, float %632)
  %640 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg208, float %639)
  %641 = sdiv i32 %633, 2
  %642 = icmp slt i32 %633, 0
  %643 = shl nsw i32 %641, 1
  %644 = icmp ne i32 %643, %633
  %645 = and i1 %642, %644
  %.neg264 = sext i1 %645 to i32
  %646 = add nsw i32 %641, 1
  %647 = add nsw i32 %646, %.neg264
  %648 = mul i32 %647, %647
  %649 = sitofp i32 %648 to float
  %650 = fdiv reassoc ninf nsz float %.4496501513522, %649
  store float %638, float* %66, align 4
  store float %640, float* %75, align 4
  store float 1.000000e+00, float* %84, align 4
  %651 = fmul reassoc ninf nsz float %638, %638
  %652 = fmul reassoc ninf nsz float %640, %640
  %653 = fadd reassoc ninf nsz float %652, %651
  %654 = fcmp reassoc ninf nsz ogt float %653, %35
  %655 = fcmp reassoc ninf nsz ogt float %650, 1.000000e+01
  %.0159 = select i1 %654, i1 true, i1 %655
  %.0160 = select i1 %.0159, float 1.000000e+00, float 0.000000e+00
  %656 = fcmp reassoc ninf nsz ogt float %653, %36
  %657 = fcmp reassoc ninf nsz ogt float %650, 2.200000e+01
  %.0 = select i1 %656, i1 true, i1 %657
  %.1 = select i1 %.0, float 2.000000e+00, float %.0160
  store float %650, float* %92, align 4
  store float 1.000000e+00, float* %101, align 4
  store float %.1, float* %110, align 4
  store float %653, float* %119, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.round.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

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
