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
define void @_apply_ransac_result_kernel_c212_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2, i32 1
  %3 = load float*, float** %2, align 8
  %4 = load float, float* %3, align 4
  %5 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %6 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %6, i64 0, i32 14
  %8 = load i8*, i8** %7, align 8
  %9 = getelementptr inbounds i8, i8* %8, i64 8
  %10 = bitcast i8* %9 to float*
  store float %4, float* %10, align 4
  %11 = load float*, float** %2, align 8
  %12 = getelementptr float, float* %11, i64 1
  %13 = load float, float* %12, align 4
  %14 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %5, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to float*
  store float %13, float* %18, align 4
  %19 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %20 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %19, i64 0, i32 4
  %21 = load i32, i32* %20, align 4
  %22 = tail call i32 @llvm.smax.i32(i32 %21, i32 0)
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %19, i64 0, i32 5
  %24 = load i32, i32* %23, align 4
  %25 = tail call i32 @llvm.smax.i32(i32 %24, i32 0)
  %26 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %5, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %26, i64 0, i32 14
  %28 = load i8*, i8** %27, align 8
  %29 = getelementptr inbounds i8, i8* %28, i64 4
  %30 = bitcast i8* %29 to i32*
  store i32 %25, i32* %30, align 4
  %31 = mul i32 %25, %22
  %32 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %5, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %32, i64 0, i32 14
  %34 = bitcast i8** %33 to i32**
  %35 = load i32*, i32** %34, align 8
  store i32 %31, i32* %35, align 4
  ret void
}

; Function Attrs: nounwind
define void @_apply_ransac_result_kernel_c212_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.48* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %25 = shl i32 %17, 1
  %26 = add nuw nsw i32 %25, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %26, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if ]
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %120, %after_if ]
  %27 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 4
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sdiv i32 %.05, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.05
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.05, 0
  %38 = icmp ne i32 %.05, %34
  %39 = and i1 %37, %36
  %40 = and i1 %39, %38
  %.neg4 = sext i1 %40 to i32
  %41 = add i32 %33, %.neg4
  %42 = load i32*, i32** %23, align 8
  %43 = load i32, i32* %24, align 4
  %44 = sub i32 %43, %32
  %45 = mul i32 %44, %41
  %46 = add i32 %.05, %45
  %47 = sext i32 %46 to i64
  %48 = getelementptr i32, i32* %42, i64 %47
  %49 = load i32, i32* %48, align 4
  %50 = icmp eq i32 %49, 1
  %51 = load { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  br i1 %50, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %52 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %51, i64 0, i32 0, i32 1
  %53 = load float*, float** %52, align 8
  %54 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %51, i64 0, i32 0, i32 0, i32 1
  %55 = load i32, i32* %54, align 4
  %56 = sub i32 %55, %32
  %57 = shl i32 %56, 1
  %58 = mul i32 %57, %41
  %59 = add i32 %lsr.iv, %58
  %60 = add i32 %59, -1
  %61 = sext i32 %60 to i64
  %62 = getelementptr float, float* %53, i64 %61
  %63 = load float, float* %62, align 4
  %64 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %51, i64 0, i32 3, i32 1
  %65 = load float*, float** %64, align 8
  %66 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %51, i64 0, i32 3, i32 0, i32 1
  %67 = load i32, i32* %66, align 4
  %68 = sub i32 %67, %32
  %69 = shl i32 %68, 1
  %70 = mul i32 %69, %41
  %71 = add i32 %lsr.iv, %70
  %72 = add i32 %71, -1
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, float* %65, i64 %73
  store float %63, float* %74, align 4
  %75 = load float*, float** %52, align 8
  %76 = load i32, i32* %54, align 4
  %77 = sub i32 %76, %32
  %78 = shl i32 %77, 1
  %79 = mul i32 %78, %41
  %80 = add i32 %lsr.iv, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %75, i64 %81
  %83 = load float, float* %82, align 4
  %84 = load float*, float** %64, align 8
  %85 = load i32, i32* %66, align 4
  %86 = sub i32 %85, %32
  %87 = shl i32 %86, 1
  %88 = mul i32 %87, %41
  %89 = add i32 %lsr.iv, %88
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, float* %84, i64 %90
  store float %83, float* %91, align 4
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %92 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %51, i64 0, i32 3, i32 1
  %93 = load float*, float** %92, align 8
  %94 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %51, i64 0, i32 3, i32 0, i32 1
  %95 = load i32, i32* %94, align 4
  %96 = sub i32 %95, %32
  %97 = shl i32 %96, 1
  %98 = mul i32 %97, %41
  %99 = add i32 %lsr.iv, %98
  %100 = add i32 %99, -1
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %93, i64 %101
  %103 = getelementptr inbounds i8, i8* %29, i64 8
  %104 = bitcast i8* %103 to float*
  %105 = load float, float* %104, align 4
  store float %105, float* %102, align 4
  %106 = load float*, float** %92, align 8
  %107 = load i32, i32* %94, align 4
  %108 = sub i32 %107, %32
  %109 = shl i32 %108, 1
  %110 = mul i32 %109, %41
  %111 = add i32 %lsr.iv, %110
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, float* %106, i64 %112
  %114 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %115 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %114, i64 0, i32 14
  %116 = load i8*, i8** %115, align 8
  %117 = getelementptr inbounds i8, i8* %116, i64 12
  %118 = bitcast i8* %117 to float*
  %119 = load float, float* %118, align 4
  store float %119, float* %113, align 4
  br label %after_if

after_if:                                         ; preds = %false_block, %true_block
  %120 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %120
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
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
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
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
