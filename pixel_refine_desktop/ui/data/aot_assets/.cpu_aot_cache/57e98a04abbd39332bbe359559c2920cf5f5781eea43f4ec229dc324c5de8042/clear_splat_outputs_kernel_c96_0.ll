; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @clear_splat_outputs_kernel_c96_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 24
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 28
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 32872
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 4
  store i32 %6, ptr %11, align 4
  %12 = mul i32 %6, %3
  %13 = load ptr, ptr %7, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  store i32 %12, ptr %15, align 4
  ret void
}

define void @clear_splat_outputs_kernel_c96_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %20 = load ptr, ptr %0, align 8
  %21 = getelementptr i8, ptr %20, i64 32
  %22 = getelementptr i8, ptr %20, i64 28
  %23 = getelementptr i8, ptr %20, i64 16
  %24 = getelementptr i8, ptr %20, i64 4
  %25 = getelementptr i8, ptr %20, i64 8
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.0710 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %100, %after_for3 ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.0710, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.0710
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %32, %.0710
  %36 = and i1 %34, %35
  %.neg8 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg8
  %38 = mul i32 %37, %30
  %39 = sub i32 %.0710, %38
  %40 = load ptr, ptr %21, align 8
  %41 = load i32, ptr %22, align 4
  %42 = sext i32 %41 to i64
  %43 = sext i32 %37 to i64
  %44 = mul nsw i64 %43, %42
  %45 = sext i32 %39 to i64
  %46 = getelementptr float, ptr %40, i64 %44
  %47 = getelementptr float, ptr %46, i64 %45
  store float 0.000000e+00, ptr %47, align 4
  %48 = load ptr, ptr %0, align 8
  %49 = getelementptr i8, ptr %48, i64 8
  %50 = load i32, ptr %49, align 4
  %51 = icmp sgt i32 %50, 0
  br i1 %51, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  %wide.trip.count = zext nneg i32 %50 to i64
  %xtraiter = and i64 %wide.trip.count, 3
  %52 = icmp ult i32 %50, 4
  br i1 %52, label %after_for3.loopexit.unr-lcssa, label %for_loop_body1.preheader.new

for_loop_body1.preheader.new:                     ; preds = %for_loop_body1.preheader
  %unroll_iter = and i64 %wide.trip.count, 2147483644
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader.new
  %indvars.iv = phi i64 [ 0, %for_loop_body1.preheader.new ], [ %indvars.iv.next.3, %for_loop_body1 ]
  %53 = load ptr, ptr %23, align 8
  %54 = load i32, ptr %24, align 4
  %55 = sext i32 %54 to i64
  %56 = load i32, ptr %25, align 4
  %57 = sext i32 %56 to i64
  %58 = mul nsw i64 %55, %43
  %59 = add nsw i64 %45, %58
  %60 = shl i64 %59, 2
  %61 = mul i64 %60, %57
  %scevgep21 = getelementptr i8, ptr %53, i64 %61
  %62 = shl nuw nsw i64 %indvars.iv, 2
  %scevgep22 = getelementptr i8, ptr %scevgep21, i64 %62
  store float 0.000000e+00, ptr %scevgep22, align 4
  %63 = load ptr, ptr %23, align 8
  %64 = load i32, ptr %24, align 4
  %65 = sext i32 %64 to i64
  %66 = load i32, ptr %25, align 4
  %67 = sext i32 %66 to i64
  %68 = mul nsw i64 %65, %43
  %69 = add nsw i64 %45, %68
  %70 = shl i64 %69, 2
  %71 = mul i64 %70, %67
  %scevgep18 = getelementptr i8, ptr %63, i64 %71
  %scevgep19 = getelementptr i8, ptr %scevgep18, i64 %62
  %scevgep20 = getelementptr i8, ptr %scevgep19, i64 4
  store float 0.000000e+00, ptr %scevgep20, align 4
  %72 = load ptr, ptr %23, align 8
  %73 = load i32, ptr %24, align 4
  %74 = sext i32 %73 to i64
  %75 = load i32, ptr %25, align 4
  %76 = sext i32 %75 to i64
  %77 = mul nsw i64 %74, %43
  %78 = add nsw i64 %45, %77
  %79 = shl i64 %78, 2
  %80 = mul i64 %79, %76
  %scevgep15 = getelementptr i8, ptr %72, i64 %80
  %scevgep16 = getelementptr i8, ptr %scevgep15, i64 %62
  %scevgep17 = getelementptr i8, ptr %scevgep16, i64 8
  store float 0.000000e+00, ptr %scevgep17, align 4
  %81 = load ptr, ptr %23, align 8
  %82 = load i32, ptr %24, align 4
  %83 = sext i32 %82 to i64
  %84 = load i32, ptr %25, align 4
  %85 = sext i32 %84 to i64
  %86 = mul nsw i64 %83, %43
  %87 = add nsw i64 %45, %86
  %88 = shl i64 %87, 2
  %89 = mul i64 %88, %85
  %scevgep = getelementptr i8, ptr %81, i64 %89
  %scevgep13 = getelementptr i8, ptr %scevgep, i64 %62
  %scevgep14 = getelementptr i8, ptr %scevgep13, i64 12
  store float 0.000000e+00, ptr %scevgep14, align 4
  %indvars.iv.next.3 = add nuw nsw i64 %indvars.iv, 4
  %niter.ncmp.3 = icmp eq i64 %unroll_iter, %indvars.iv.next.3
  br i1 %niter.ncmp.3, label %after_for3.loopexit.unr-lcssa.loopexit, label %for_loop_body1

after_for3.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body1
  br label %after_for3.loopexit.unr-lcssa

after_for3.loopexit.unr-lcssa:                    ; preds = %after_for3.loopexit.unr-lcssa.loopexit, %for_loop_body1.preheader
  %indvars.iv.unr = phi i64 [ 0, %for_loop_body1.preheader ], [ %indvars.iv.next.3, %after_for3.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_for3, label %for_loop_body1.epil.preheader

for_loop_body1.epil.preheader:                    ; preds = %after_for3.loopexit.unr-lcssa
  br label %for_loop_body1.epil

for_loop_body1.epil:                              ; preds = %for_loop_body1.epil, %for_loop_body1.epil.preheader
  %lsr.iv = phi i64 [ %xtraiter, %for_loop_body1.epil.preheader ], [ %lsr.iv.next, %for_loop_body1.epil ]
  %indvars.iv.epil = phi i64 [ %indvars.iv.next.epil, %for_loop_body1.epil ], [ %indvars.iv.unr, %for_loop_body1.epil.preheader ]
  %90 = load ptr, ptr %23, align 8
  %91 = load i32, ptr %24, align 4
  %92 = sext i32 %91 to i64
  %93 = load i32, ptr %25, align 4
  %94 = sext i32 %93 to i64
  %95 = mul nsw i64 %92, %43
  %96 = add nsw i64 %45, %95
  %97 = shl i64 %96, 2
  %98 = mul i64 %97, %94
  %scevgep23 = getelementptr i8, ptr %90, i64 %98
  %99 = shl nuw nsw i64 %indvars.iv.epil, 2
  %scevgep24 = getelementptr i8, ptr %scevgep23, i64 %99
  store float 0.000000e+00, ptr %scevgep24, align 4
  %indvars.iv.next.epil = add nuw nsw i64 %indvars.iv.epil, 1
  %lsr.iv.next = add nsw i64 %lsr.iv, -1
  %epil.iter.cmp.not = icmp eq i64 %lsr.iv.next, 0
  br i1 %epil.iter.cmp.not, label %after_for3.loopexit, label %for_loop_body1.epil, !llvm.loop !11

after_for3.loopexit:                              ; preds = %for_loop_body1.epil
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %after_for3.loopexit.unr-lcssa, %for_loop_body
  %100 = add nsw i32 %.0710, 1
  %exitcond12.not = icmp eq i32 %100, %18
  br i1 %exitcond12.not, label %after_for.loopexit, label %for_loop_body
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !13

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !15

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
attributes #2 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

!llvm.linker.options = !{!0, !1, !2, !3, !4, !5}
!llvm.ident = !{!6}
!llvm.module.flags = !{!7, !8, !9, !10}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"/alternatename:_Avx2WmemEnabled=_Avx2WmemEnabledWeakValue"}
!6 = !{!"clang version 20.1.5"}
!7 = !{i32 1, !"wchar_size", i32 2}
!8 = !{i32 8, !"PIC Level", i32 2}
!9 = !{i32 7, !"uwtable", i32 2}
!10 = !{i32 1, !"MaxTLSAlign", i32 65536}
!11 = distinct !{!11, !12}
!12 = !{!"llvm.loop.unroll.disable"}
!13 = distinct !{!13, !14}
!14 = !{!"llvm.loop.mustprogress"}
!15 = distinct !{!15, !14}
