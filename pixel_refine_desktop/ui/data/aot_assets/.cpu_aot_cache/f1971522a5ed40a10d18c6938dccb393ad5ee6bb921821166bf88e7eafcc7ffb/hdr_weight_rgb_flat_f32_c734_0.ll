; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @hdr_weight_rgb_flat_f32_c734_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 52
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 8
  store i32 %5, ptr %10, align 4
  %11 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %12 = load ptr, ptr %6, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 4
  store i32 %11, ptr %15, align 4
  %16 = mul i32 %11, %3
  %17 = load ptr, ptr %6, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  store i32 %16, ptr %19, align 4
  ret void
}

define void @hdr_weight_rgb_flat_f32_c734_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #8
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %0)
  ret void
}

; Function Attrs: nofree nounwind memory(readwrite, inaccessiblemem: write)
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
  %24 = getelementptr i8, ptr %19, i64 64
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 68
  %27 = load float, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 72
  %29 = load float, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 76
  %31 = load float, ptr %30, align 4
  %32 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %21, float 0x3EB0C6F7A0000000)
  %33 = fmul reassoc ninf nsz float %27, 0x3FD5555560000000
  %34 = fmul reassoc ninf nsz float %25, %25
  %35 = fmul reassoc ninf nsz float %34, 2.000000e+00
  %36 = icmp slt i32 %16, %18
  br i1 %36, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %37 = getelementptr i8, ptr %19, i64 8
  %38 = getelementptr i8, ptr %19, i64 24
  %39 = getelementptr i8, ptr %19, i64 20
  %40 = getelementptr i8, ptr %19, i64 40
  %41 = getelementptr i8, ptr %19, i64 36
  %42 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %42, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %133, %for_loop_body ]
  %43 = load ptr, ptr %3, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 4
  %47 = load i32, ptr %46, align 4
  %48 = sdiv i32 %.05, %47
  %49 = mul i32 %48, %47
  %50 = xor i32 %47, %.05
  %51 = icmp slt i32 %50, 0
  %52 = icmp ne i32 %.05, %49
  %53 = and i1 %51, %52
  %.neg4 = sext i1 %53 to i32
  %54 = add i32 %48, %.neg4
  %55 = getelementptr inbounds nuw i8, ptr %45, i64 8
  %56 = load i32, ptr %55, align 4
  %57 = sub i32 %56, %47
  %58 = mul i32 %57, 3
  %59 = mul i32 %58, %54
  %60 = add i32 %lsr.iv, %59
  %61 = load ptr, ptr %37, align 8
  %62 = sext i32 %60 to i64
  %63 = getelementptr float, ptr %61, i64 %62
  %64 = load float, ptr %63, align 4
  %65 = add i32 %60, 1
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %61, i64 %66
  %68 = load float, ptr %67, align 4
  %69 = add i32 %60, 2
  %70 = sext i32 %69 to i64
  %71 = getelementptr float, ptr %61, i64 %70
  %72 = load float, ptr %71, align 4
  %73 = fmul reassoc ninf nsz float %64, 0x3FD322D0E0000000
  %74 = fmul reassoc ninf nsz float %68, 0x3FE2C8B440000000
  %75 = fadd reassoc ninf nsz float %74, %73
  %76 = fmul reassoc ninf nsz float %72, 0x3FBD2F1AA0000000
  %77 = fadd reassoc ninf nsz float %75, %76
  %78 = fdiv reassoc ninf nsz float %77, %32
  %79 = fadd reassoc ninf nsz float %78, 5.000000e-01
  %80 = fdiv reassoc ninf nsz float %78, %79
  %81 = tail call noundef float @powf(float noundef %80, float noundef %23) #8
  %82 = fadd reassoc ninf nsz float %64, -5.000000e-01
  %83 = fneg reassoc ninf nsz float %82
  %neg = fmul reassoc ninf nsz float %82, %83
  %84 = fdiv reassoc ninf nsz float %neg, %35
  %85 = tail call noundef float @expf(float noundef %84) #8
  %86 = fadd reassoc ninf nsz float %68, -5.000000e-01
  %87 = fneg reassoc ninf nsz float %86
  %neg1 = fmul reassoc ninf nsz float %86, %87
  %88 = fdiv reassoc ninf nsz float %neg1, %35
  %89 = tail call noundef float @expf(float noundef %88) #8
  %90 = fadd reassoc ninf nsz float %72, -5.000000e-01
  %91 = fneg reassoc ninf nsz float %90
  %neg2 = fmul reassoc ninf nsz float %90, %91
  %92 = fdiv reassoc ninf nsz float %neg2, %35
  %93 = tail call noundef float @expf(float noundef %92) #8
  %94 = fmul reassoc ninf nsz float %89, %85
  %95 = fmul reassoc ninf nsz float %94, %93
  %96 = tail call noundef float @powf(float noundef %95, float noundef %33) #8
  %97 = load ptr, ptr %38, align 8
  %98 = load i32, ptr %39, align 4
  %99 = sub i32 %98, %47
  %100 = mul i32 %99, %54
  %101 = add i32 %.05, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, ptr %97, i64 %102
  %104 = load float, ptr %103, align 4
  %105 = tail call noundef float @llvm.fabs.f32(float %104)
  %106 = fadd reassoc ninf nsz float %105, 0x3EB0C6F7A0000000
  %107 = tail call noundef float @powf(float noundef %106, float noundef %29) #8
  %108 = fadd reassoc ninf nsz float %68, %64
  %109 = fadd reassoc ninf nsz float %108, %72
  %110 = fmul reassoc ninf nsz float %109, 0x3FD5555560000000
  %111 = fsub reassoc ninf nsz float %64, %110
  %112 = fmul reassoc ninf nsz float %111, %111
  %113 = fsub reassoc ninf nsz float %68, %110
  %114 = fmul reassoc ninf nsz float %113, %113
  %115 = fadd reassoc ninf nsz float %112, %114
  %116 = fsub reassoc ninf nsz float %72, %110
  %117 = fmul reassoc ninf nsz float %116, %116
  %118 = fadd reassoc ninf nsz float %115, %117
  %119 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %118)
  %120 = fmul reassoc ninf nsz float %119, 0x3FD5555560000000
  %121 = fadd reassoc ninf nsz float %120, 0x3EB0C6F7A0000000
  %122 = tail call noundef float @powf(float noundef %121, float noundef %31) #8
  %123 = fmul reassoc ninf nsz float %96, %81
  %124 = fmul reassoc ninf nsz float %123, %107
  %125 = fmul reassoc ninf nsz float %124, %122
  %126 = load ptr, ptr %40, align 8
  %127 = load i32, ptr %41, align 4
  %128 = sub i32 %127, %47
  %129 = mul i32 %128, %54
  %130 = add i32 %.05, %129
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, ptr %126, i64 %131
  store float %125, ptr %132, align 4
  %133 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %133
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @powf(float noundef, float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #8
  %14 = add i32 %.02040, 1
  %15 = icmp slt i32 %14, %.sroa.speculated28
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !11

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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
  %.not24.not = icmp sgt i32 %.0, %.sroa.speculated
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !13

.loopexit.loopexit:                               ; preds = %.lr.ph41
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %16, %9, %7
  %.not25 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not25, label %21, label %20

20:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nounwind }

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
!12 = !{!"llvm.loop.mustprogress"}
!13 = distinct !{!13, !12}
