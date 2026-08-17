; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_reduce_row_max_kernel_c300_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  store i32 %1, ptr %5, align 4
  ret void
}

define void @_reduce_row_max_kernel_c300_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %20 = load ptr, ptr %0, align 8
  %21 = getelementptr i8, ptr %20, i64 8
  %22 = getelementptr i8, ptr %20, i64 4
  %23 = getelementptr i8, ptr %20, i64 24
  %24 = getelementptr i8, ptr %20, i64 20
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01218 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %76, %after_for3 ]
  %25 = load ptr, ptr %0, align 8
  %26 = getelementptr i8, ptr %25, i64 4
  %27 = load i32, ptr %26, align 4
  %28 = icmp sgt i32 %27, 0
  br i1 %28, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %29 = load ptr, ptr %21, align 8
  %30 = load i32, ptr %22, align 4
  %wide.trip.count = zext nneg i32 %27 to i64
  %xtraiter = and i64 %wide.trip.count, 3
  %31 = icmp ult i32 %27, 4
  br i1 %31, label %after_for3.loopexit.unr-lcssa, label %for_loop_body1.lr.ph.new

for_loop_body1.lr.ph.new:                         ; preds = %for_loop_body1.lr.ph
  %unroll_iter = and i64 %wide.trip.count, 2147483644
  %32 = mul i32 %30, %.01218
  %33 = zext i32 %32 to i64
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.lr.ph.new
  %indvars.iv = phi i64 [ 0, %for_loop_body1.lr.ph.new ], [ %indvars.iv.next.3, %for_loop_body1 ]
  %.0915 = phi i32 [ 0, %for_loop_body1.lr.ph.new ], [ %.1.3, %for_loop_body1 ]
  %.01014 = phi float [ -1.000000e+10, %for_loop_body1.lr.ph.new ], [ %.111.3, %for_loop_body1 ]
  %34 = add i64 %33, %indvars.iv
  %tmp29 = trunc i64 %34 to i32
  %35 = sext i32 %tmp29 to i64
  %36 = getelementptr float, ptr %29, i64 %35
  %37 = load float, ptr %36, align 4
  %38 = fcmp reassoc ninf nsz ogt float %37, %.01014
  %.111 = select i1 %38, float %37, float %.01014
  %tmp28 = trunc i64 %indvars.iv to i32
  %.1 = select i1 %38, i32 %tmp28, i32 %.0915
  %39 = add i64 %indvars.iv, 1
  %40 = add i64 %34, 1
  %tmp26 = trunc i64 %40 to i32
  %41 = sext i32 %tmp26 to i64
  %42 = getelementptr float, ptr %29, i64 %41
  %43 = load float, ptr %42, align 4
  %44 = fcmp reassoc ninf nsz ogt float %43, %.111
  %.111.1 = select i1 %44, float %43, float %.111
  %tmp27 = trunc i64 %39 to i32
  %.1.1 = select i1 %44, i32 %tmp27, i32 %.1
  %45 = add i64 %indvars.iv, 2
  %46 = add i64 %34, 2
  %tmp24 = trunc i64 %46 to i32
  %47 = sext i32 %tmp24 to i64
  %48 = getelementptr float, ptr %29, i64 %47
  %49 = load float, ptr %48, align 4
  %50 = fcmp reassoc ninf nsz ogt float %49, %.111.1
  %.111.2 = select i1 %50, float %49, float %.111.1
  %tmp25 = trunc i64 %45 to i32
  %.1.2 = select i1 %50, i32 %tmp25, i32 %.1.1
  %51 = add i64 %indvars.iv, 3
  %52 = add i64 %34, 3
  %tmp = trunc i64 %52 to i32
  %53 = sext i32 %tmp to i64
  %54 = getelementptr float, ptr %29, i64 %53
  %55 = load float, ptr %54, align 4
  %56 = fcmp reassoc ninf nsz ogt float %55, %.111.2
  %.111.3 = select i1 %56, float %55, float %.111.2
  %tmp23 = trunc i64 %51 to i32
  %.1.3 = select i1 %56, i32 %tmp23, i32 %.1.2
  %indvars.iv.next.3 = add nuw nsw i64 %indvars.iv, 4
  %niter.ncmp.3 = icmp eq i64 %unroll_iter, %indvars.iv.next.3
  br i1 %niter.ncmp.3, label %after_for3.loopexit.unr-lcssa.loopexit, label %for_loop_body1

after_for3.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body1
  br label %after_for3.loopexit.unr-lcssa

after_for3.loopexit.unr-lcssa:                    ; preds = %after_for3.loopexit.unr-lcssa.loopexit, %for_loop_body1.lr.ph
  %.111.lcssa.ph = phi float [ poison, %for_loop_body1.lr.ph ], [ %.111.3, %after_for3.loopexit.unr-lcssa.loopexit ]
  %.1.lcssa.ph = phi i32 [ poison, %for_loop_body1.lr.ph ], [ %.1.3, %after_for3.loopexit.unr-lcssa.loopexit ]
  %indvars.iv.unr = phi i64 [ 0, %for_loop_body1.lr.ph ], [ %indvars.iv.next.3, %after_for3.loopexit.unr-lcssa.loopexit ]
  %.0915.unr = phi i32 [ 0, %for_loop_body1.lr.ph ], [ %.1.3, %after_for3.loopexit.unr-lcssa.loopexit ]
  %.01014.unr = phi float [ -1.000000e+10, %for_loop_body1.lr.ph ], [ %.111.3, %after_for3.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_for3.loopexit, label %for_loop_body1.epil.preheader

for_loop_body1.epil.preheader:                    ; preds = %after_for3.loopexit.unr-lcssa
  %57 = trunc i64 %indvars.iv.unr to i32
  %58 = mul i32 %30, %.01218
  br label %for_loop_body1.epil

for_loop_body1.epil:                              ; preds = %for_loop_body1.epil, %for_loop_body1.epil.preheader
  %lsr.iv30 = phi i64 [ %xtraiter, %for_loop_body1.epil.preheader ], [ %lsr.iv.next31, %for_loop_body1.epil ]
  %lsr.iv = phi i32 [ %57, %for_loop_body1.epil.preheader ], [ %lsr.iv.next, %for_loop_body1.epil ]
  %.0915.epil = phi i32 [ %.1.epil, %for_loop_body1.epil ], [ %.0915.unr, %for_loop_body1.epil.preheader ]
  %.01014.epil = phi float [ %.111.epil, %for_loop_body1.epil ], [ %.01014.unr, %for_loop_body1.epil.preheader ]
  %59 = add i32 %58, %lsr.iv
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %29, i64 %60
  %62 = load float, ptr %61, align 4
  %63 = fcmp reassoc ninf nsz ogt float %62, %.01014.epil
  %.111.epil = select i1 %63, float %62, float %.01014.epil
  %.1.epil = select i1 %63, i32 %lsr.iv, i32 %.0915.epil
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 1
  %lsr.iv.next31 = add nsw i64 %lsr.iv30, -1
  %epil.iter.cmp.not = icmp eq i64 %lsr.iv.next31, 0
  br i1 %epil.iter.cmp.not, label %after_for3.loopexit.loopexit, label %for_loop_body1.epil, !llvm.loop !10

after_for3.loopexit.loopexit:                     ; preds = %for_loop_body1.epil
  br label %after_for3.loopexit

after_for3.loopexit:                              ; preds = %after_for3.loopexit.loopexit, %after_for3.loopexit.unr-lcssa
  %.111.lcssa = phi float [ %.111.lcssa.ph, %after_for3.loopexit.unr-lcssa ], [ %.111.epil, %after_for3.loopexit.loopexit ]
  %.1.lcssa = phi i32 [ %.1.lcssa.ph, %after_for3.loopexit.unr-lcssa ], [ %.1.epil, %after_for3.loopexit.loopexit ]
  %64 = uitofp nneg i32 %.1.lcssa to float
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.010.lcssa = phi float [ -1.000000e+10, %for_loop_body ], [ %.111.lcssa, %after_for3.loopexit ]
  %.09.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %64, %after_for3.loopexit ]
  %65 = load ptr, ptr %23, align 8
  %66 = load i32, ptr %24, align 4
  %67 = mul i32 %66, %.01218
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %65, i64 %68
  store float %.010.lcssa, ptr %69, align 4
  %70 = load ptr, ptr %23, align 8
  %71 = load i32, ptr %24, align 4
  %72 = mul i32 %71, %.01218
  %73 = add i32 %72, 1
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, ptr %70, i64 %74
  store float %.09.lcssa, ptr %75, align 4
  %76 = add nsw i32 %.01218, 1
  %exitcond20.not = icmp eq i32 %76, %18
  br i1 %exitcond20.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !12

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !14

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
!11 = !{!"llvm.loop.unroll.disable"}
!12 = distinct !{!12, !13}
!13 = !{!"llvm.loop.mustprogress"}
!14 = distinct !{!14, !13}
