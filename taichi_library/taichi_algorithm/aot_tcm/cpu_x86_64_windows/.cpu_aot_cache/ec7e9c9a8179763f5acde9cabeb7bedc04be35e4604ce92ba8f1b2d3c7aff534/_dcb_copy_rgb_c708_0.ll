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
define void @_dcb_copy_rgb_c708_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_copy_rgb_c708_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 2
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %111, %for_loop_body ]
  %29 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.05, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.05
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.05, 0
  %40 = icmp ne i32 %.05, %36
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg4 = sext i1 %42 to i32
  %43 = add i32 %35, %.neg4
  %44 = load float*, float** %23, align 8
  %45 = load i32, i32* %24, align 4
  %46 = load i32, i32* %25, align 4
  %47 = sub i32 %45, %34
  %48 = mul i32 %47, %43
  %49 = add i32 %.05, %48
  %50 = mul i32 %49, %46
  %51 = sext i32 %50 to i64
  %52 = getelementptr float, float* %44, i64 %51
  %53 = load float, float* %52, align 4
  %54 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %53, float 0.000000e+00)
  %55 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %54, float 1.000000e+00)
  %56 = load float*, float** %26, align 8
  %57 = load i32, i32* %27, align 4
  %58 = load i32, i32* %28, align 4
  %59 = sub i32 %57, %34
  %60 = mul i32 %59, %43
  %61 = add i32 %.05, %60
  %62 = mul i32 %61, %58
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, float* %56, i64 %63
  store float %55, float* %64, align 4
  %65 = load float*, float** %23, align 8
  %66 = load i32, i32* %24, align 4
  %67 = load i32, i32* %25, align 4
  %68 = sub i32 %66, %34
  %69 = mul i32 %68, %43
  %70 = add i32 %.05, %69
  %71 = mul i32 %70, %67
  %72 = add i32 %71, 1
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, float* %65, i64 %73
  %75 = load float, float* %74, align 4
  %76 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %75, float 0.000000e+00)
  %77 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %76, float 1.000000e+00)
  %78 = load float*, float** %26, align 8
  %79 = load i32, i32* %27, align 4
  %80 = load i32, i32* %28, align 4
  %81 = sub i32 %79, %34
  %82 = mul i32 %81, %43
  %83 = add i32 %.05, %82
  %84 = mul i32 %83, %80
  %85 = add i32 %84, 1
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, float* %78, i64 %86
  store float %77, float* %87, align 4
  %88 = load float*, float** %23, align 8
  %89 = load i32, i32* %24, align 4
  %90 = load i32, i32* %25, align 4
  %91 = sub i32 %89, %34
  %92 = mul i32 %91, %43
  %93 = add i32 %.05, %92
  %94 = mul i32 %93, %90
  %95 = add i32 %94, 2
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, float* %88, i64 %96
  %98 = load float, float* %97, align 4
  %99 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %98, float 0.000000e+00)
  %100 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %99, float 1.000000e+00)
  %101 = load float*, float** %26, align 8
  %102 = load i32, i32* %27, align 4
  %103 = load i32, i32* %28, align 4
  %104 = sub i32 %102, %34
  %105 = mul i32 %104, %43
  %106 = add i32 %.05, %105
  %107 = mul i32 %106, %103
  %108 = add i32 %107, 2
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %101, i64 %109
  store float %100, float* %110, align 4
  %111 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %111
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

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
