; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.84*, void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.84 = type { i8*, %struct.LLVMRuntime.83*, i32, i64* }
%struct.LLVMRuntime.83 = type { %struct.PreallocatedMemoryChunk.79, %struct.PreallocatedMemoryChunk.79, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.80*], [1024 x %struct.NodeManager.81*], [1024 x i8*], i8*, %struct.RandState.82*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.79 = type { i8*, i8*, i64 }
%struct.ListManager.80 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.83* }
%struct.NodeManager.81 = type { %struct.LLVMRuntime.83*, i32, i32, i32, i32, %struct.ListManager.80*, %struct.ListManager.80*, %struct.ListManager.80*, i32 }
%struct.RandState.82 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @math_reduce_sum_kernel_c712_0_kernel_0_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %1 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %0, align 8
  %2 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %1, i64 0, i32 14
  %3 = load i8*, i8** %2, align 8
  %4 = getelementptr inbounds i8, i8* %3, i64 12
  %5 = bitcast i8* %4 to float*
  store float 0.000000e+00, float* %5, align 4
  %6 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32 }, float* }, { { i32 }, float* } }**
  %7 = load { { { i32, i32 }, float* }, { { i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32 }, float* } }** %6, align 8
  %8 = getelementptr { { { i32, i32 }, float* }, { { i32 }, float* } }, { { { i32, i32 }, float* }, { { i32 }, float* } }* %7, i64 0, i32 0, i32 0, i32 0
  %9 = load i32, i32* %8, align 4
  %10 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %0, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 14
  %12 = load i8*, i8** %11, align 8
  %13 = getelementptr inbounds i8, i8* %12, i64 8
  %14 = bitcast i8* %13 to i32*
  store i32 %9, i32* %14, align 4
  %15 = load { { { i32, i32 }, float* }, { { i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32 }, float* } }** %6, align 8
  %16 = getelementptr { { { i32, i32 }, float* }, { { i32 }, float* } }, { { { i32, i32 }, float* }, { { i32 }, float* } }* %15, i64 0, i32 0, i32 0, i32 1
  %17 = load i32, i32* %16, align 4
  %18 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %0, align 8
  %19 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %18, i64 0, i32 14
  %20 = load i8*, i8** %19, align 8
  %21 = getelementptr inbounds i8, i8* %20, i64 4
  %22 = bitcast i8* %21 to i32*
  store i32 %17, i32* %22, align 4
  %23 = mul i32 %17, %9
  %24 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %0, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %24, i64 0, i32 14
  %26 = bitcast i8** %25 to i32**
  %27 = load i32*, i32** %26, align 8
  store i32 %23, i32* %27, align 4
  ret void
}

; Function Attrs: nounwind
define void @math_reduce_sum_kernel_c712_0_kernel_1_range_for(%struct.RuntimeContext.84* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.84* %context, %struct.RuntimeContext.84** %4, align 8
  store void (%struct.RuntimeContext.84*, i8*)* @function_body, void (%struct.RuntimeContext.84*, i8*)** %2, align 8
  store i64 4, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.84*, i8*, i32)* @function_body.1, void (%struct.RuntimeContext.84*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.84*, i8*)* @function_body.2, void (%struct.RuntimeContext.84*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: argmemonly mustprogress nofree norecurse nosync nounwind willreturn writeonly
define internal void @function_body(%struct.RuntimeContext.84* nocapture readnone %0, i8* nocapture writeonly %1) #2 {
allocs:
  %2 = bitcast i8* %1 to float*
  store float 0.000000e+00, float* %2, align 4
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body.1(%struct.RuntimeContext.84* nocapture readonly %0, i8* nocapture %1, i32 %2) #3 {
allocs:
  %3 = bitcast i8* %1 to float*
  %4 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %0, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  %9 = load i32, i32* %8, align 4
  %10 = add i32 %9, 7
  %11 = sdiv i32 %10, 8
  %12 = icmp slt i32 %10, 0
  %13 = shl nsw i32 %11, 3
  %14 = icmp ne i32 %13, %10
  %15 = and i1 %12, %14
  %.neg = sext i1 %15 to i32
  %16 = add nsw i32 %11, %.neg
  %17 = tail call i32 @llvm.smax.i32(i32 %16, i32 512)
  %18 = mul i32 %17, %2
  %19 = add i32 %18, %17
  %20 = tail call i32 @llvm.smin.i32(i32 %9, i32 %19)
  %21 = icmp slt i32 %18, %20
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = bitcast %struct.RuntimeContext.84* %0 to { { { i32, i32 }, float* }, { { i32 }, float* } }**
  %23 = load { { { i32, i32 }, float* }, { { i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32 }, float* } }** %22, align 8
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32 }, float* } }, { { { i32, i32 }, float* }, { { i32 }, float* } }* %23, i64 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32 }, float* } }, { { { i32, i32 }, float* }, { { i32 }, float* } }* %23, i64 0, i32 0, i32 0, i32 1
  %.pre = load float, float* %3, align 4
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %26 = phi float [ %.pre, %for_loop_body.lr.ph ], [ %46, %for_loop_body ]
  %.04 = phi i32 [ %18, %for_loop_body.lr.ph ], [ %47, %for_loop_body ]
  %27 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 4
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = srem i32 %.04, %32
  %34 = sdiv i32 %.04, %32
  %35 = getelementptr inbounds i8, i8* %29, i64 8
  %36 = bitcast i8* %35 to i32*
  %37 = load i32, i32* %36, align 4
  %38 = srem i32 %34, %37
  %39 = load float*, float** %24, align 8
  %40 = load i32, i32* %25, align 4
  %41 = mul i32 %40, %38
  %42 = add i32 %41, %33
  %43 = sext i32 %42 to i64
  %44 = getelementptr float, float* %39, i64 %43
  %45 = load float, float* %44, align 4
  %46 = fadd reassoc ninf nsz float %26, %45
  store float %46, float* %3, align 4
  %47 = add nsw i32 %.04, 1
  %exitcond.not = icmp eq i32 %20, %47
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nofree norecurse nounwind willreturn
define internal void @function_body.2(%struct.RuntimeContext.84* nocapture readonly %0, i8* nocapture readonly %1) #4 {
allocs:
  %2 = bitcast i8* %1 to float*
  %3 = load float, float* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %0, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to float*
  %10 = atomicrmw fadd float* %9, float %3 seq_cst, align 4
  ret void
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @math_reduce_sum_kernel_c712_0_kernel_2_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %1 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %0, align 8
  %2 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %1, i64 0, i32 14
  %3 = load i8*, i8** %2, align 8
  %4 = getelementptr inbounds i8, i8* %3, i64 12
  %5 = bitcast i8* %4 to float*
  %6 = load float, float* %5, align 4
  %7 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32 }, float* }, { { i32 }, float* } }**
  %8 = load { { { i32, i32 }, float* }, { { i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32 }, float* } }** %7, align 8
  %9 = getelementptr { { { i32, i32 }, float* }, { { i32 }, float* } }, { { { i32, i32 }, float* }, { { i32 }, float* } }* %8, i64 0, i32 1, i32 1
  %10 = load float*, float** %9, align 8
  store float %6, float* %10, align 4
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #5 {
  %4 = alloca %struct.RuntimeContext.84, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.84**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.84*, %struct.RuntimeContext.84** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.84* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.84* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #7

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #8

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #8

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { argmemonly mustprogress nofree norecurse nosync nounwind willreturn writeonly }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { mustprogress nofree norecurse nounwind willreturn }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #7 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #8 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
