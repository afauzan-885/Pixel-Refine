; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext*, void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { i8*, %struct.LLVMRuntime*, i32, i64* }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager*], [1024 x %struct.NodeManager*], [1024 x i8*], i8*, %struct.RandState*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { i8*, i8*, i64 }
%struct.ListManager = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime* }
%struct.NodeManager = type { %struct.LLVMRuntime*, i32, i32, i32, i32, %struct.ListManager*, %struct.ListManager*, %struct.ListManager*, i32 }
%struct.RandState = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_threshold_kernel_c358_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %1, i64 0, i32 5
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %1, i64 0, i32 6
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_threshold_kernel_c358_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext* %context, %struct.RuntimeContext** %4, align 8
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext*, i8*, i32)* @function_body, void (%struct.RuntimeContext*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %21, i64 0, i32 2
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %21, i64 0, i32 4
  %26 = load i32, i32* %25, align 4
  %27 = icmp eq i32 %26, 0
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  br i1 %27, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  br label %for_loop_body

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %after_if3.us, %for_loop_body.us.preheader
  %.057.us = phi i32 [ %66, %after_if3.us ], [ %17, %for_loop_body.us.preheader ]
  %30 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %.057.us, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.057.us
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.057.us, 0
  %41 = icmp ne i32 %.057.us, %37
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg6.us = sext i1 %43 to i32
  %44 = add i32 %36, %.neg6.us
  %45 = load float*, float** %28, align 8
  %46 = load i32, i32* %29, align 4
  %47 = sub i32 %46, %35
  %48 = mul i32 %47, %44
  %49 = add i32 %.057.us, %48
  %50 = sext i32 %49 to i64
  %51 = getelementptr float, float* %45, i64 %50
  %52 = load float, float* %51, align 4
  %53 = fcmp reassoc ninf nsz ogt float %52, %23
  %54 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }** %20, align 8
  br i1 %53, label %true_block1.us, label %after_if3.us

true_block1.us:                                   ; preds = %for_loop_body.us
  %55 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %54, i64 0, i32 3
  %56 = load float, float* %55, align 4
  br label %after_if3.us

after_if3.us:                                     ; preds = %true_block1.us, %for_loop_body.us
  %.0.us = phi float [ %56, %true_block1.us ], [ 0.000000e+00, %for_loop_body.us ]
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %54, i64 0, i32 1, i32 1
  %58 = load float*, float** %57, align 8
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %54, i64 0, i32 1, i32 0, i32 1
  %60 = load i32, i32* %59, align 4
  %61 = sub i32 %60, %35
  %62 = mul i32 %61, %44
  %63 = add i32 %.057.us, %62
  %64 = sext i32 %63 to i64
  %65 = getelementptr float, float* %58, i64 %64
  store float %.0.us, float* %65, align 4
  %66 = add nsw i32 %.057.us, 1
  %exitcond.not = icmp eq i32 %19, %66
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %after_if6, %for_loop_body.preheader
  %.057 = phi i32 [ %102, %after_if6 ], [ %17, %for_loop_body.preheader ]
  %67 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %68 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %67, i64 0, i32 14
  %69 = load i8*, i8** %68, align 8
  %70 = getelementptr inbounds i8, i8* %69, i64 4
  %71 = bitcast i8* %70 to i32*
  %72 = load i32, i32* %71, align 4
  %73 = sdiv i32 %.057, %72
  %74 = mul i32 %73, %72
  %75 = xor i32 %72, %.057
  %76 = icmp slt i32 %75, 0
  %77 = icmp ne i32 %.057, 0
  %78 = icmp ne i32 %.057, %74
  %79 = and i1 %77, %76
  %80 = and i1 %79, %78
  %.neg6 = sext i1 %80 to i32
  %81 = add i32 %73, %.neg6
  %82 = load float*, float** %28, align 8
  %83 = load i32, i32* %29, align 4
  %84 = sub i32 %83, %72
  %85 = mul i32 %84, %81
  %86 = add i32 %.057, %85
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, float* %82, i64 %87
  %89 = load float, float* %88, align 4
  %90 = fcmp reassoc ninf nsz ogt float %89, %23
  %.pre = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }** %20, align 8
  br i1 %90, label %after_if6, label %false_block5

after_for.loopexit:                               ; preds = %after_if3.us
  br label %after_for

after_for.loopexit14:                             ; preds = %after_if6
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit14, %after_for.loopexit, %allocs
  ret void

false_block5:                                     ; preds = %for_loop_body
  %91 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %.pre, i64 0, i32 3
  %92 = load float, float* %91, align 4
  br label %after_if6

after_if6:                                        ; preds = %false_block5, %for_loop_body
  %.1 = phi float [ %92, %false_block5 ], [ 0.000000e+00, %for_loop_body ]
  %93 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %.pre, i64 0, i32 1, i32 1
  %94 = load float*, float** %93, align 8
  %95 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, i32, i32, i32 }* %.pre, i64 0, i32 1, i32 0, i32 1
  %96 = load i32, i32* %95, align 4
  %97 = sub i32 %96, %72
  %98 = mul i32 %97, %81
  %99 = add i32 %.057, %98
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %94, i64 %100
  store float %.1, float* %101, align 4
  %102 = add nsw i32 %.057, 1
  %exitcond9.not = icmp eq i32 %19, %102
  br i1 %exitcond9.not, label %after_for.loopexit14, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext**
  %.sroa.0.0.copyload = load %struct.RuntimeContext*, %struct.RuntimeContext** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
