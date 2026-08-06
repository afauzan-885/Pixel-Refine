; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.588*, void (%struct.RuntimeContext.588*, i8*)*, void (%struct.RuntimeContext.588*, i8*, i32)*, void (%struct.RuntimeContext.588*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.588 = type { i8*, %struct.LLVMRuntime.587*, i32, i64* }
%struct.LLVMRuntime.587 = type { %struct.PreallocatedMemoryChunk.583, %struct.PreallocatedMemoryChunk.583, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.584*], [1024 x %struct.NodeManager.585*], [1024 x i8*], i8*, %struct.RandState.586*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.583 = type { i8*, i8*, i64 }
%struct.ListManager.584 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.587* }
%struct.NodeManager.585 = type { %struct.LLVMRuntime.587*, i32, i32, i32, i32, %struct.ListManager.584*, %struct.ListManager.584*, %struct.ListManager.584*, i32 }
%struct.RandState.586 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_pad_replicate_kernel_2d_c540_1_kernel_0_serial(%struct.RuntimeContext.588* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.588* %context to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }**
  %1 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.588, %struct.RuntimeContext.588* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.587*, %struct.LLVMRuntime.587** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.587, %struct.LLVMRuntime.587* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %10, i64 0, i32 1, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.587*, %struct.LLVMRuntime.587** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.587, %struct.LLVMRuntime.587* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 4
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = mul i32 %12, %3
  %19 = load %struct.LLVMRuntime.587*, %struct.LLVMRuntime.587** %4, align 8
  %20 = getelementptr inbounds %struct.LLVMRuntime.587, %struct.LLVMRuntime.587* %19, i64 0, i32 14
  %21 = bitcast i8** %20 to i32**
  %22 = load i32*, i32** %21, align 8
  store i32 %18, i32* %22, align 4
  ret void
}

; Function Attrs: nounwind
define void @_pad_replicate_kernel_2d_c540_1_kernel_1_range_for(%struct.RuntimeContext.588* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.588* %context, %struct.RuntimeContext.588** %4, align 8
  store void (%struct.RuntimeContext.588*, i8*)* null, void (%struct.RuntimeContext.588*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.588*, i8*, i32)* @function_body, void (%struct.RuntimeContext.588*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.588*, i8*)* null, void (%struct.RuntimeContext.588*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.588, %struct.RuntimeContext.588* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.587*, %struct.LLVMRuntime.587** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.587, %struct.LLVMRuntime.587* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.587, %struct.LLVMRuntime.587* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.588* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.588, %struct.RuntimeContext.588* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.587*, %struct.LLVMRuntime.587** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.587, %struct.LLVMRuntime.587* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.588* %0 to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }**
  %21 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %21, i64 0, i32 2
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %21, i64 0, i32 3
  %25 = load i32, i32* %24, align 4
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %21, i64 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %21, i64 0, i32 1, i32 1
  %30 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.04 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %69, %for_loop_body ]
  %31 = load %struct.LLVMRuntime.587*, %struct.LLVMRuntime.587** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.587, %struct.LLVMRuntime.587* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = srem i32 %.04, %36
  %38 = sdiv i32 %.04, %36
  %39 = getelementptr inbounds i8, i8* %33, i64 8
  %40 = bitcast i8* %39 to i32*
  %41 = load i32, i32* %40, align 4
  %42 = srem i32 %38, %41
  %43 = sub i32 %42, %23
  %44 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }** %20, align 8
  %45 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %44, i64 0, i32 0, i32 0, i32 0
  %46 = load i32, i32* %45, align 4
  %47 = add i32 %46, -1
  %48 = tail call i32 @llvm.smax.i32(i32 %43, i32 0)
  %49 = tail call i32 @llvm.smin.i32(i32 %47, i32 %48)
  %50 = sub i32 %37, %25
  %51 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, i32, i32 }* %44, i64 0, i32 0, i32 0, i32 1
  %52 = load i32, i32* %51, align 4
  %53 = add i32 %52, -1
  %54 = tail call i32 @llvm.smax.i32(i32 %50, i32 0)
  %55 = tail call i32 @llvm.smin.i32(i32 %53, i32 %54)
  %56 = load i32*, i32** %27, align 8
  %57 = load i32, i32* %28, align 4
  %58 = mul i32 %57, %49
  %59 = add i32 %58, %55
  %60 = sext i32 %59 to i64
  %61 = getelementptr i32, i32* %56, i64 %60
  %62 = load i32, i32* %61, align 4
  %63 = load i32*, i32** %29, align 8
  %64 = load i32, i32* %30, align 4
  %65 = mul i32 %64, %42
  %66 = add i32 %65, %37
  %67 = sext i32 %66 to i64
  %68 = getelementptr i32, i32* %63, i64 %67
  store i32 %62, i32* %68, align 4
  %69 = add nsw i32 %.04, 1
  %exitcond.not = icmp eq i32 %19, %69
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.588, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.588**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.588*, %struct.RuntimeContext.588** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.588*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.588*, i8*)*, void (%struct.RuntimeContext.588*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.588*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.588*, i8*, i32)*, void (%struct.RuntimeContext.588*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.588*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.588*, i8*)*, void (%struct.RuntimeContext.588*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.588*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.588* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.588* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.588* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.588, %struct.RuntimeContext.588* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.588* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.588* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.588*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.588* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
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
