; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_inpaint_level_1ch_kernel_c466_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 52
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 12
  store i32 %11, ptr %15, align 4
  %16 = tail call i32 @llvm.smax.i32(i32 %11, i32 0)
  %17 = load ptr, ptr %3, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 4
  store i32 %16, ptr %20, align 4
  %21 = mul i32 %16, %8
  %22 = load ptr, ptr %3, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 32872
  %24 = load ptr, ptr %23, align 8
  store i32 %21, ptr %24, align 4
  ret void
}

define void @_inpaint_level_1ch_kernel_c466_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
cpu_parallel_range_for.exit:
  %0 = alloca %struct.range_task_helper_context, align 8
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %0)
  %1 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %2 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %4 = getelementptr inbounds nuw i8, ptr %0, i64 32
  store ptr %context, ptr %0, align 8
  store ptr null, ptr %1, align 8
  store i64 1, ptr %4, align 8
  store ptr @function_body, ptr %2, align 8
  store ptr null, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %0, i64 40
  store i32 0, ptr %5, align 8
  %6 = getelementptr inbounds nuw i8, ptr %0, i64 44
  store i32 8, ptr %6, align 4
  %7 = getelementptr inbounds nuw i8, ptr %0, i64 52
  store i32 1, ptr %7, align 4
  %8 = getelementptr inbounds nuw i8, ptr %0, i64 48
  store i32 1, ptr %8, align 8
  %9 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 8288
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %10, i64 8280
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #7
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %0)
  ret void
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #1 {
allocs:
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = load i32, ptr %6, align 4
  %8 = add i32 %7, 7
  %9 = sdiv i32 %8, 8
  %10 = icmp slt i32 %8, 0
  %11 = shl nsw i32 %9, 3
  %12 = icmp ne i32 %11, %8
  %13 = and i1 %10, %12
  %.neg = sext i1 %13 to i32
  %14 = add nsw i32 %9, %.neg
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load float, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 60
  %23 = load float, ptr %22, align 4
  %24 = fptosi float %23 to i32
  %25 = fmul reassoc ninf nsz float %23, %23
  %26 = add i32 %24, 2
  %neg = xor i32 %24, -1
  %27 = icmp slt i32 %16, %18
  br i1 %27, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %28 = getelementptr i8, ptr %19, i64 24
  %29 = getelementptr i8, ptr %19, i64 20
  %30 = icmp sgt i32 %26, %neg
  %31 = getelementptr i8, ptr %19, i64 40
  %32 = getelementptr i8, ptr %19, i64 36
  %33 = getelementptr i8, ptr %19, i64 8
  %34 = getelementptr i8, ptr %19, i64 4
  %.fr = freeze i1 %30
  br i1 %.fr, label %for_loop_body.us.preheader, label %after_for

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %35 = sub i32 0, %24
  %smax = tail call i32 @llvm.smax.i32(i32 %35, i32 %26)
  %36 = sub i32 -1, %24
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %for_loop_inc.us, %for_loop_body.us.preheader
  %.02769.us = phi i32 [ %74, %for_loop_inc.us ], [ %16, %for_loop_body.us.preheader ]
  %37 = load ptr, ptr %3, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 32872
  %39 = load ptr, ptr %38, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 4
  %41 = load i32, ptr %40, align 4
  %42 = sdiv i32 %.02769.us, %41
  %43 = mul i32 %42, %41
  %44 = xor i32 %41, %.02769.us
  %45 = icmp slt i32 %44, 0
  %46 = icmp ne i32 %43, %.02769.us
  %47 = and i1 %45, %46
  %.neg36.us = sext i1 %47 to i32
  %48 = add i32 %42, %.neg36.us
  %49 = mul i32 %48, %41
  %50 = sub i32 %.02769.us, %49
  %51 = load ptr, ptr %28, align 8
  %52 = load i32, ptr %29, align 4
  %53 = mul i32 %48, %52
  %54 = add i32 %50, %53
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, ptr %51, i64 %55
  %57 = load float, ptr %56, align 4
  %58 = fsub reassoc ninf nsz float %57, %21
  %59 = tail call noundef float @llvm.fabs.f32(float %58)
  %60 = fcmp reassoc ninf nsz ogt float %59, 5.000000e-01
  br i1 %60, label %for_loop_inc.us, label %for_loop_test4.preheader.us

true_block33.us:                                  ; preds = %for_loop_test4.after_for3_crit_edge.split.us.us
  %61 = fdiv reassoc ninf nsz float %.us-phi44.us.us, %.us-phi.us.us
  %62 = load ptr, ptr %33, align 8
  %63 = load i32, ptr %34, align 4
  %64 = mul i32 %63, %48
  %65 = add i32 %64, %50
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %62, i64 %66
  store float %61, ptr %67, align 4
  %68 = load ptr, ptr %31, align 8
  %69 = load i32, ptr %32, align 4
  %70 = mul i32 %69, %48
  %71 = add i32 %70, %50
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, ptr %68, i64 %72
  store float 1.000000e+00, ptr %73, align 4
  br label %for_loop_inc.us

for_loop_inc.us:                                  ; preds = %for_loop_test4.after_for3_crit_edge.split.us.us, %true_block33.us, %for_loop_body.us
  %74 = add nsw i32 %.02769.us, 1
  %exitcond74.not = icmp eq i32 %74, %18
  br i1 %exitcond74.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_test4.preheader.us:                      ; preds = %for_loop_body.us
  %75 = getelementptr inbounds nuw i8, ptr %39, i64 8
  %76 = getelementptr inbounds nuw i8, ptr %39, i64 12
  %77 = add i32 %36, %42
  %78 = add i32 %77, %.neg36.us
  br label %for_loop_body1.us.us

for_loop_body1.us.us:                             ; preds = %for_loop_test8.after_for7_crit_edge.us.us, %for_loop_test4.preheader.us
  %lsr.iv = phi i32 [ %lsr.iv.next, %for_loop_test8.after_for7_crit_edge.us.us ], [ %78, %for_loop_test4.preheader.us ]
  %.02258.us.us = phi i32 [ %neg, %for_loop_test4.preheader.us ], [ %111, %for_loop_test8.after_for7_crit_edge.us.us ]
  %.02357.us.us = phi float [ 0.000000e+00, %for_loop_test4.preheader.us ], [ %.us-phi44.us.us, %for_loop_test8.after_for7_crit_edge.us.us ]
  %.02456.us.us = phi float [ 0.000000e+00, %for_loop_test4.preheader.us ], [ %.us-phi.us.us, %for_loop_test8.after_for7_crit_edge.us.us ]
  %79 = add i32 %.02258.us.us, %48
  %80 = mul i32 %.02258.us.us, %.02258.us.us
  %81 = icmp slt i32 %79, 0
  br i1 %81, label %for_loop_test8.after_for7_crit_edge.us.us, label %for_loop_body5.lr.ph.split.us64.us

for_loop_body5.us61.us:                           ; preds = %for_loop_body5.us61.us.preheader, %for_loop_inc6.us.us
  %.02142.us62.us = phi i32 [ %109, %for_loop_inc6.us.us ], [ %neg, %for_loop_body5.us61.us.preheader ]
  %.241.us.us = phi float [ %.1.us.us, %for_loop_inc6.us.us ], [ %.02357.us.us, %for_loop_body5.us61.us.preheader ]
  %.22640.us.us = phi float [ %.125.us.us, %for_loop_inc6.us.us ], [ %.02456.us.us, %for_loop_body5.us61.us.preheader ]
  %82 = add i32 %50, %.02142.us62.us
  %83 = icmp slt i32 %82, 0
  br i1 %83, label %for_loop_inc6.us.us, label %false_block16.us.us

false_block16.us.us:                              ; preds = %for_loop_body5.us61.us
  %84 = load i32, ptr %76, align 4
  %.not39.us.us = icmp slt i32 %82, %84
  br i1 %.not39.us.us, label %after_if20.us.us, label %for_loop_inc6.us.us

after_if20.us.us:                                 ; preds = %false_block16.us.us
  %85 = load ptr, ptr %31, align 8
  %86 = load i32, ptr %32, align 4
  %87 = mul i32 %lsr.iv, %86
  %88 = add i32 %82, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, ptr %85, i64 %89
  %91 = load float, ptr %90, align 4
  %92 = fcmp reassoc ninf nsz olt float %91, 5.000000e-01
  br i1 %92, label %for_loop_inc6.us.us, label %after_if24.us.us

after_if24.us.us:                                 ; preds = %after_if20.us.us
  %93 = mul i32 %.02142.us62.us, %.02142.us62.us
  %94 = add i32 %93, %80
  %95 = sitofp i32 %94 to float
  %96 = fcmp reassoc ninf nsz olt float %25, %95
  %97 = icmp slt i32 %94, 1
  %.0.us.us = or i1 %97, %96
  br i1 %.0.us.us, label %for_loop_inc6.us.us, label %after_if31.us.us

after_if31.us.us:                                 ; preds = %after_if24.us.us
  %98 = fdiv reassoc ninf nsz float 1.000000e+00, %95
  %99 = fadd reassoc ninf nsz float %98, %.22640.us.us
  %100 = load ptr, ptr %33, align 8
  %101 = load i32, ptr %34, align 4
  %102 = mul i32 %lsr.iv, %101
  %103 = add i32 %82, %102
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %100, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = fmul reassoc ninf nsz float %106, %98
  %108 = fadd reassoc ninf nsz float %107, %.241.us.us
  br label %for_loop_inc6.us.us

for_loop_inc6.us.us:                              ; preds = %after_if31.us.us, %after_if24.us.us, %after_if20.us.us, %false_block16.us.us, %for_loop_body5.us61.us
  %.125.us.us = phi float [ %.22640.us.us, %false_block16.us.us ], [ %.22640.us.us, %after_if20.us.us ], [ %.22640.us.us, %after_if24.us.us ], [ %99, %after_if31.us.us ], [ %.22640.us.us, %for_loop_body5.us61.us ]
  %.1.us.us = phi float [ %.241.us.us, %false_block16.us.us ], [ %.241.us.us, %after_if20.us.us ], [ %.241.us.us, %after_if24.us.us ], [ %108, %after_if31.us.us ], [ %.241.us.us, %for_loop_body5.us61.us ]
  %109 = add nsw i32 %.02142.us62.us, 1
  %exitcond.not = icmp eq i32 %smax, %109
  br i1 %exitcond.not, label %for_loop_test8.after_for7_crit_edge.us.us.loopexit, label %for_loop_body5.us61.us

for_loop_body5.lr.ph.split.us64.us:               ; preds = %for_loop_body1.us.us
  %110 = load i32, ptr %75, align 4
  %.not.us.us = icmp sge i32 %79, %110
  %.not.fr.us.us = freeze i1 %.not.us.us
  br i1 %.not.fr.us.us, label %for_loop_test8.after_for7_crit_edge.us.us, label %for_loop_body5.us61.us.preheader

for_loop_body5.us61.us.preheader:                 ; preds = %for_loop_body5.lr.ph.split.us64.us
  br label %for_loop_body5.us61.us

for_loop_test8.after_for7_crit_edge.us.us.loopexit: ; preds = %for_loop_inc6.us.us
  br label %for_loop_test8.after_for7_crit_edge.us.us

for_loop_test8.after_for7_crit_edge.us.us:        ; preds = %for_loop_test8.after_for7_crit_edge.us.us.loopexit, %for_loop_body5.lr.ph.split.us64.us, %for_loop_body1.us.us
  %.us-phi.us.us = phi float [ %.02456.us.us, %for_loop_body1.us.us ], [ %.02456.us.us, %for_loop_body5.lr.ph.split.us64.us ], [ %.125.us.us, %for_loop_test8.after_for7_crit_edge.us.us.loopexit ]
  %.us-phi44.us.us = phi float [ %.02357.us.us, %for_loop_body1.us.us ], [ %.02357.us.us, %for_loop_body5.lr.ph.split.us64.us ], [ %.1.us.us, %for_loop_test8.after_for7_crit_edge.us.us.loopexit ]
  %111 = add i32 %.02258.us.us, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond73.not = icmp eq i32 %111, %smax
  br i1 %exitcond73.not, label %for_loop_test4.after_for3_crit_edge.split.us.us, label %for_loop_body1.us.us

for_loop_test4.after_for3_crit_edge.split.us.us:  ; preds = %for_loop_test8.after_for7_crit_edge.us.us
  %112 = fcmp reassoc ninf nsz ogt float %.us-phi.us.us, 0x3D71979980000000
  br i1 %112, label %true_block33.us, label %for_loop_inc.us

after_for.loopexit:                               ; preds = %for_loop_inc.us
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %for_loop_body.lr.ph, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.5, align 8
  %.sroa.0.0.copyload = load ptr, ptr %0, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 8
  %.sroa.4.0.copyload = load ptr, ptr %.sroa.4.0..sroa_idx, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 16
  %.sroa.5.0.copyload = load ptr, ptr %.sroa.5.0..sroa_idx, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 24
  %.sroa.7.0.copyload = load ptr, ptr %.sroa.7.0..sroa_idx, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 32
  %.sroa.8.0.copyload = load i64, ptr %.sroa.8.0..sroa_idx, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 40
  %.sroa.9.0.copyload = load i32, ptr %.sroa.9.0..sroa_idx, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 44
  %.sroa.12.0.copyload = load i32, ptr %.sroa.12.0..sroa_idx, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 48
  %.sroa.15.0.copyload = load i32, ptr %.sroa.15.0..sroa_idx, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 52
  %.sroa.17.0.copyload = load i32, ptr %.sroa.17.0..sroa_idx, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq ptr %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #7
  br label %7

7:                                                ; preds = %6, %3
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %4, ptr noundef nonnull align 8 dereferenceable(32) %.sroa.0.0.copyload, i64 32, i1 false)
  %8 = getelementptr inbounds nuw i8, ptr %4, i64 16
  store i32 %1, ptr %8, align 8
  switch i32 %.sroa.17.0.copyload, label %.loopexit [
    i32 1, label %9
    i32 -1, label %16
  ]

9:                                                ; preds = %7
  %10 = mul nsw i32 %.sroa.15.0.copyload, %2
  %11 = add nsw i32 %10, %.sroa.9.0.copyload
  %12 = add nsw i32 %11, %.sroa.15.0.copyload
  %.sroa.speculated28 = call i32 @llvm.smin.i32(i32 %.sroa.12.0.copyload, i32 %12)
  %13 = icmp slt i32 %11, %.sroa.speculated28
  br i1 %13, label %.lr.ph41.preheader, label %.loopexit

.lr.ph41.preheader:                               ; preds = %9
  br label %.lr.ph41

.lr.ph41:                                         ; preds = %.lr.ph41, %.lr.ph41.preheader
  %.02040 = phi i32 [ %14, %.lr.ph41 ], [ %11, %.lr.ph41.preheader ]
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #7
  %14 = add i32 %.02040, 1
  %15 = icmp slt i32 %14, %.sroa.speculated28
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !10

16:                                               ; preds = %7
  %17 = mul nsw i32 %.sroa.15.0.copyload, %2
  %18 = sub nsw i32 %.sroa.12.0.copyload, %17
  %19 = mul nsw i32 %18, %.sroa.15.0.copyload
  %.sroa.speculated = call i32 @llvm.smax.i32(i32 %.sroa.9.0.copyload, i32 %19)
  %.not24.not38 = icmp sgt i32 %18, %.sroa.speculated
  br i1 %.not24.not38, label %.lr.ph.preheader, label %.loopexit

.lr.ph.preheader:                                 ; preds = %16
  br label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %.lr.ph.preheader
  %.0.in39 = phi i32 [ %.0, %.lr.ph ], [ %18, %.lr.ph.preheader ]
  %.0 = add i32 %.0.in39, -1
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
  %.not24.not = icmp sgt i32 %.0, %.sroa.speculated
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !12

.loopexit.loopexit:                               ; preds = %.lr.ph41
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %16, %9, %7
  %.not25 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not25, label %21, label %20

20:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #7
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

!llvm.linker.options = !{!0, !1, !2, !3, !4, !5}
!llvm.ident = !{!6}
!llvm.module.flags = !{!7, !8, !9}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"/alternatename:_Avx2WmemEnabled=_Avx2WmemEnabledWeakValue"}
!6 = !{!"clang version 14.0.6"}
!7 = !{i32 1, !"wchar_size", i32 2}
!8 = !{i32 8, !"PIC Level", i32 2}
!9 = !{i32 7, !"uwtable", i32 1}
!10 = distinct !{!10, !11}
!11 = !{!"llvm.loop.mustprogress"}
!12 = distinct !{!12, !11}
