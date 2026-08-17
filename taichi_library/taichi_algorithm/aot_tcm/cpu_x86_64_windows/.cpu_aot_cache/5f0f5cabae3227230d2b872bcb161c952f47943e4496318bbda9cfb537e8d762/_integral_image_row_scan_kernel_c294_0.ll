; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_integral_image_row_scan_kernel_c294_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  store i32 %2, ptr %6, align 4
  ret void
}

define void @_integral_image_row_scan_kernel_c294_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #6
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
  %15 = tail call range(i32 -268435457, 268435456) i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 52
  %21 = load i32, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_test4.preheader.lr.ph, label %after_for

for_loop_test4.preheader.lr.ph:                   ; preds = %allocs
  %23 = icmp sgt i32 %21, 0
  %24 = getelementptr i8, ptr %19, i64 8
  %25 = getelementptr i8, ptr %19, i64 4
  %26 = getelementptr i8, ptr %19, i64 24
  %27 = getelementptr i8, ptr %19, i64 20
  %28 = getelementptr i8, ptr %19, i64 40
  %29 = getelementptr i8, ptr %19, i64 36
  br i1 %23, label %for_loop_test4.preheader.us.preheader, label %after_for

for_loop_test4.preheader.us.preheader:            ; preds = %for_loop_test4.preheader.lr.ph
  %xtraiter = and i32 %21, 1
  %30 = icmp eq i32 %21, 1
  %unroll_iter = and i32 %21, 2147483646
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br label %for_loop_test4.preheader.us

for_loop_test4.preheader.us:                      ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_test4.preheader.us.preheader
  %.01014.us = phi i32 [ %101, %for_loop_test4.after_for3_crit_edge.us ], [ %16, %for_loop_test4.preheader.us.preheader ]
  br i1 %30, label %for_loop_test4.after_for3_crit_edge.us.unr-lcssa, label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %for_loop_test4.preheader.us
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader
  %.013.us = phi i32 [ %78, %for_loop_body1.us ], [ 0, %for_loop_body1.us.preheader ]
  %.0812.us = phi float [ %63, %for_loop_body1.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.0911.us = phi float [ %61, %for_loop_body1.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %31 = load ptr, ptr %24, align 8
  %32 = load i32, ptr %25, align 4
  %33 = mul i32 %.01014.us, %32
  %34 = add i32 %.013.us, %33
  %35 = sext i32 %34 to i64
  %36 = getelementptr float, ptr %31, i64 %35
  %37 = load float, ptr %36, align 4
  %38 = fadd reassoc ninf nsz float %37, %.0911.us
  %39 = fmul reassoc ninf nsz float %37, %37
  %40 = fadd reassoc ninf nsz float %39, %.0812.us
  %41 = load ptr, ptr %26, align 8
  %42 = load i32, ptr %27, align 4
  %43 = mul i32 %.01014.us, %42
  %44 = add i32 %.013.us, %43
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, ptr %41, i64 %45
  store float %38, ptr %46, align 4
  %47 = load ptr, ptr %28, align 8
  %48 = load i32, ptr %29, align 4
  %49 = mul i32 %.01014.us, %48
  %50 = add i32 %.013.us, %49
  %51 = sext i32 %50 to i64
  %52 = getelementptr float, ptr %47, i64 %51
  store float %40, ptr %52, align 4
  %53 = load ptr, ptr %24, align 8
  %54 = load i32, ptr %25, align 4
  %55 = mul i32 %.01014.us, %54
  %56 = add i32 %.013.us, %55
  %57 = add i32 %56, 1
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, ptr %53, i64 %58
  %60 = load float, ptr %59, align 4
  %61 = fadd reassoc ninf nsz float %60, %38
  %62 = fmul reassoc ninf nsz float %60, %60
  %63 = fadd reassoc ninf nsz float %62, %40
  %64 = load ptr, ptr %26, align 8
  %65 = load i32, ptr %27, align 4
  %66 = mul i32 %.01014.us, %65
  %67 = add i32 %.013.us, %66
  %68 = add i32 %67, 1
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, ptr %64, i64 %69
  store float %61, ptr %70, align 4
  %71 = load ptr, ptr %28, align 8
  %72 = load i32, ptr %29, align 4
  %73 = mul i32 %.01014.us, %72
  %74 = add i32 %.013.us, %73
  %75 = add i32 %74, 1
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, ptr %71, i64 %76
  store float %63, ptr %77, align 4
  %78 = add nuw i32 %.013.us, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %78
  br i1 %niter.ncmp.1, label %for_loop_test4.after_for3_crit_edge.us.unr-lcssa.loopexit, label %for_loop_body1.us

for_loop_test4.after_for3_crit_edge.us.unr-lcssa.loopexit: ; preds = %for_loop_body1.us
  br label %for_loop_test4.after_for3_crit_edge.us.unr-lcssa

for_loop_test4.after_for3_crit_edge.us.unr-lcssa: ; preds = %for_loop_test4.after_for3_crit_edge.us.unr-lcssa.loopexit, %for_loop_test4.preheader.us
  %.013.us.unr = phi i32 [ 0, %for_loop_test4.preheader.us ], [ %78, %for_loop_test4.after_for3_crit_edge.us.unr-lcssa.loopexit ]
  %.0812.us.unr = phi float [ 0.000000e+00, %for_loop_test4.preheader.us ], [ %63, %for_loop_test4.after_for3_crit_edge.us.unr-lcssa.loopexit ]
  %.0911.us.unr = phi float [ 0.000000e+00, %for_loop_test4.preheader.us ], [ %61, %for_loop_test4.after_for3_crit_edge.us.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us.epil

for_loop_body1.us.epil:                           ; preds = %for_loop_test4.after_for3_crit_edge.us.unr-lcssa
  %79 = load ptr, ptr %24, align 8
  %80 = load i32, ptr %25, align 4
  %81 = mul i32 %80, %.01014.us
  %82 = add i32 %81, %.013.us.unr
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, ptr %79, i64 %83
  %85 = load float, ptr %84, align 4
  %86 = fadd reassoc ninf nsz float %85, %.0911.us.unr
  %87 = fmul reassoc ninf nsz float %85, %85
  %88 = fadd reassoc ninf nsz float %87, %.0812.us.unr
  %89 = load ptr, ptr %26, align 8
  %90 = load i32, ptr %27, align 4
  %91 = mul i32 %90, %.01014.us
  %92 = add i32 %91, %.013.us.unr
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %89, i64 %93
  store float %86, ptr %94, align 4
  %95 = load ptr, ptr %28, align 8
  %96 = load i32, ptr %29, align 4
  %97 = mul i32 %96, %.01014.us
  %98 = add i32 %97, %.013.us.unr
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %95, i64 %99
  store float %88, ptr %100, align 4
  br label %for_loop_test4.after_for3_crit_edge.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us.epil, %for_loop_test4.after_for3_crit_edge.us.unr-lcssa
  %101 = add nsw i32 %.01014.us, 1
  %exitcond16.not = icmp eq i32 %101, %18
  br i1 %exitcond16.not, label %after_for.loopexit, label %for_loop_test4.preheader.us

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %for_loop_test4.preheader.lr.ph, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.0, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
