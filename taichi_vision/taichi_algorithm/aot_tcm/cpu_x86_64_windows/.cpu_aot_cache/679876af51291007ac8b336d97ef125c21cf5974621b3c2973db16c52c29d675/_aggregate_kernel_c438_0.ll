; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_aggregate_kernel_c438_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 120
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  store i32 %2, ptr %6, align 4
  ret void
}

define void @_aggregate_kernel_c438_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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

; Function Attrs: nofree norecurse nounwind memory(readwrite, inaccessiblemem: none)
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
  %20 = getelementptr i8, ptr %19, i64 124
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 128
  %23 = load i32, ptr %22, align 4
  %.fr44 = freeze i32 %23
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr i8, ptr %19, i64 32
  %26 = icmp sgt i32 %21, 0
  %27 = getelementptr i8, ptr %19, i64 80
  %28 = getelementptr i8, ptr %19, i64 76
  %29 = getelementptr i8, ptr %19, i64 48
  %30 = getelementptr i8, ptr %19, i64 44
  %31 = getelementptr i8, ptr %19, i64 64
  %32 = getelementptr i8, ptr %19, i64 60
  %33 = icmp sgt i32 %.fr44, 0
  %or.cond = and i1 %26, %33
  br i1 %or.cond, label %for_loop_body.us.us.preheader, label %after_for

for_loop_body.us.us.preheader:                    ; preds = %for_loop_body.lr.ph
  %34 = sext i32 %16 to i64
  %wide.trip.count = sext i32 %18 to i64
  br label %for_loop_body.us.us

for_loop_body.us.us:                              ; preds = %for_loop_test4.after_for3_crit_edge.split.us.us.us, %for_loop_body.us.us.preheader
  %indvars.iv = phi i64 [ %34, %for_loop_body.us.us.preheader ], [ %indvars.iv.next, %for_loop_test4.after_for3_crit_edge.split.us.us.us ]
  %lsr54 = trunc i64 %indvars.iv to i32
  %35 = load ptr, ptr %25, align 8
  %36 = getelementptr float, ptr %35, i64 %indvars.iv
  %37 = load float, ptr %36, align 4
  br label %for_loop_body1.us.us.us

for_loop_body1.us.us.us:                          ; preds = %for_loop_inc2.us.us.us, %for_loop_body.us.us
  %.01934.us.us.us = phi i32 [ 0, %for_loop_body.us.us ], [ %60, %for_loop_inc2.us.us.us ]
  %38 = load ptr, ptr %27, align 8
  %39 = load i32, ptr %28, align 4
  %40 = mul i32 %39, %lsr54
  %41 = add i32 %40, %.01934.us.us.us
  %42 = sext i32 %41 to i64
  %43 = getelementptr i32, ptr %38, i64 %42
  %44 = load i32, ptr %43, align 4
  %45 = icmp eq i32 %44, 0
  br i1 %45, label %for_loop_inc2.us.us.us, label %after_if.us.us.us

after_if.us.us.us:                                ; preds = %for_loop_body1.us.us.us
  %46 = load ptr, ptr %29, align 8
  %47 = load i32, ptr %30, align 4
  %48 = mul i32 %47, %lsr54
  %49 = add i32 %48, %.01934.us.us.us
  %50 = sext i32 %49 to i64
  %51 = getelementptr i32, ptr %46, i64 %50
  %52 = load i32, ptr %51, align 4
  %53 = load ptr, ptr %31, align 8
  %54 = load i32, ptr %32, align 4
  %55 = mul i32 %54, %lsr54
  %56 = add i32 %55, %.01934.us.us.us
  %57 = sext i32 %56 to i64
  %58 = getelementptr i32, ptr %53, i64 %57
  %59 = load i32, ptr %58, align 4
  br label %for_loop_body5.us.us.us.us

for_loop_inc2.us.us.us.loopexit:                  ; preds = %for_loop_test12.after_for11_crit_edge.us.us.us.us
  br label %for_loop_inc2.us.us.us

for_loop_inc2.us.us.us:                           ; preds = %for_loop_inc2.us.us.us.loopexit, %for_loop_body1.us.us.us
  %60 = add nuw nsw i32 %.01934.us.us.us, 1
  %exitcond49.not = icmp eq i32 %60, %21
  br i1 %exitcond49.not, label %for_loop_test4.after_for3_crit_edge.split.us.us.us, label %for_loop_body1.us.us.us

for_loop_body5.us.us.us.us:                       ; preds = %for_loop_test12.after_for11_crit_edge.us.us.us.us, %after_if.us.us.us
  %lsr.iv52 = phi i32 [ %lsr.iv.next53, %for_loop_test12.after_for11_crit_edge.us.us.us.us ], [ %52, %after_if.us.us.us ]
  %.01828.us.us.us.us = phi i32 [ 0, %after_if.us.us.us ], [ %63, %for_loop_test12.after_for11_crit_edge.us.us.us.us ]
  %61 = add i32 %.01828.us.us.us.us, %52
  %62 = icmp sgt i32 %61, -1
  br i1 %62, label %for_loop_body9.us.us.us.us.us.preheader, label %for_loop_test12.after_for11_crit_edge.us.us.us.us

for_loop_body9.us.us.us.us.us.preheader:          ; preds = %for_loop_body5.us.us.us.us
  br label %for_loop_body9.us.us.us.us.us

for_loop_test12.after_for11_crit_edge.us.us.us.us.loopexit: ; preds = %after_if24.us.us.us.us.us
  br label %for_loop_test12.after_for11_crit_edge.us.us.us.us

for_loop_test12.after_for11_crit_edge.us.us.us.us: ; preds = %for_loop_test12.after_for11_crit_edge.us.us.us.us.loopexit, %for_loop_body5.us.us.us.us
  %63 = add nuw nsw i32 %.01828.us.us.us.us, 1
  %lsr.iv.next53 = add i32 %lsr.iv52, 1
  %exitcond48.not = icmp eq i32 %63, %.fr44
  br i1 %exitcond48.not, label %for_loop_inc2.us.us.us.loopexit, label %for_loop_body5.us.us.us.us

for_loop_body9.us.us.us.us.us:                    ; preds = %after_if24.us.us.us.us.us, %for_loop_body9.us.us.us.us.us.preheader
  %.01727.us.us.us.us.us = phi i32 [ %110, %after_if24.us.us.us.us.us ], [ 0, %for_loop_body9.us.us.us.us.us.preheader ]
  %64 = add i32 %59, %.01727.us.us.us.us.us
  %65 = load ptr, ptr %0, align 8
  %66 = getelementptr i8, ptr %65, i64 132
  %67 = load i32, ptr %66, align 4
  %68 = icmp slt i32 %61, %67
  %69 = icmp sgt i32 %64, -1
  %or.cond.us.us.us.us.us = select i1 %68, i1 %69, i1 false
  br i1 %or.cond.us.us.us.us.us, label %true_block19.us.us.us.us.us, label %after_if24.us.us.us.us.us

true_block19.us.us.us.us.us:                      ; preds = %for_loop_body9.us.us.us.us.us
  %70 = getelementptr i8, ptr %65, i64 136
  %71 = load i32, ptr %70, align 4
  %72 = icmp slt i32 %64, %71
  br i1 %72, label %true_block22.us.us.us.us.us, label %after_if24.us.us.us.us.us

true_block22.us.us.us.us.us:                      ; preds = %true_block19.us.us.us.us.us
  %73 = getelementptr i8, ptr %65, i64 16
  %74 = load ptr, ptr %73, align 8
  %75 = getelementptr i8, ptr %65, i64 4
  %76 = load i32, ptr %75, align 4
  %77 = getelementptr i8, ptr %65, i64 8
  %78 = load i32, ptr %77, align 4
  %79 = getelementptr i8, ptr %65, i64 12
  %80 = load i32, ptr %79, align 4
  %81 = mul i32 %lsr54, %76
  %82 = add i32 %.01934.us.us.us, %81
  %83 = mul i32 %78, %82
  %84 = add i32 %.01828.us.us.us.us, %83
  %85 = mul i32 %80, %84
  %86 = add i32 %.01727.us.us.us.us.us, %85
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, ptr %74, i64 %87
  %89 = load float, ptr %88, align 4
  %90 = fmul reassoc ninf nsz float %89, %37
  %91 = getelementptr i8, ptr %65, i64 96
  %92 = load ptr, ptr %91, align 8
  %93 = getelementptr i8, ptr %65, i64 92
  %94 = load i32, ptr %93, align 4
  %95 = mul i32 %lsr.iv52, %94
  %96 = add i32 %64, %95
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %92, i64 %97
  %99 = atomicrmw fadd ptr %98, float %90 seq_cst, align 4
  %100 = load ptr, ptr %0, align 8
  %101 = getelementptr i8, ptr %100, i64 112
  %102 = load ptr, ptr %101, align 8
  %103 = getelementptr i8, ptr %100, i64 108
  %104 = load i32, ptr %103, align 4
  %105 = mul i32 %lsr.iv52, %104
  %106 = add i32 %64, %105
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, ptr %102, i64 %107
  %109 = atomicrmw fadd ptr %108, float %37 seq_cst, align 4
  br label %after_if24.us.us.us.us.us

after_if24.us.us.us.us.us:                        ; preds = %true_block22.us.us.us.us.us, %true_block19.us.us.us.us.us, %for_loop_body9.us.us.us.us.us
  %110 = add nuw nsw i32 %.01727.us.us.us.us.us, 1
  %exitcond.not = icmp eq i32 %.fr44, %110
  br i1 %exitcond.not, label %for_loop_test12.after_for11_crit_edge.us.us.us.us.loopexit, label %for_loop_body9.us.us.us.us.us

for_loop_test4.after_for3_crit_edge.split.us.us.us: ; preds = %for_loop_inc2.us.us.us
  %indvars.iv.next = add nsw i64 %indvars.iv, 1
  %exitcond51.not = icmp eq i64 %indvars.iv.next, %wide.trip.count
  br i1 %exitcond51.not, label %after_for.loopexit, label %for_loop_body.us.us

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.split.us.us.us
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %for_loop_body.lr.ph, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.3, align 8
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
attributes #1 = { nofree norecurse nounwind memory(readwrite, inaccessiblemem: none) }
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
