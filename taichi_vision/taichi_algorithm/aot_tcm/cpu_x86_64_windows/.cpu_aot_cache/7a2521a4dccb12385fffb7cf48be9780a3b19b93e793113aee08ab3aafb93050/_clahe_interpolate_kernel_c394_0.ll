; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_clahe_interpolate_kernel_c394_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 52
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

define void @_clahe_interpolate_kernel_c394_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 72
  %21 = load float, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 76
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 60
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 56
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 64
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 68
  %31 = load i32, ptr %30, align 4
  %32 = sitofp i32 %23 to float
  %33 = add i32 %23, -1
  %34 = sitofp i32 %25 to float
  %35 = sitofp i32 %27 to float
  %36 = add i32 %29, -1
  %37 = add i32 %31, -1
  %38 = fmul reassoc ninf nsz float %34, 5.000000e-01
  %39 = fmul reassoc ninf nsz float %35, 5.000000e-01
  %40 = sitofp i32 %33 to float
  %41 = icmp slt i32 %16, %18
  br i1 %41, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %42 = getelementptr i8, ptr %19, i64 8
  %43 = getelementptr i8, ptr %19, i64 4
  %44 = getelementptr i8, ptr %19, i64 24
  %45 = getelementptr i8, ptr %19, i64 20
  %46 = getelementptr i8, ptr %19, i64 40
  %47 = getelementptr i8, ptr %19, i64 36
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.06 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %148, %for_loop_body ]
  %48 = load ptr, ptr %3, align 8
  %49 = getelementptr inbounds nuw i8, ptr %48, i64 32872
  %50 = load ptr, ptr %49, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 4
  %52 = load i32, ptr %51, align 4
  %53 = sdiv i32 %.06, %52
  %54 = mul i32 %53, %52
  %55 = xor i32 %52, %.06
  %56 = icmp slt i32 %55, 0
  %57 = icmp ne i32 %.06, %54
  %58 = and i1 %56, %57
  %.neg4 = sext i1 %58 to i32
  %59 = add i32 %53, %.neg4
  %60 = mul i32 %52, -1
  %61 = mul i32 %60, %59
  %62 = add i32 %.06, %61
  %63 = load ptr, ptr %42, align 8
  %64 = load i32, ptr %43, align 4
  %65 = sub i32 %64, %52
  %66 = mul i32 %65, %59
  %67 = add i32 %.06, %66
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %63, i64 %68
  %70 = load float, ptr %69, align 4
  %71 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %70, float 0.000000e+00)
  %72 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %21, float %71)
  %73 = fmul reassoc ninf nsz float %72, %32
  %74 = fdiv reassoc ninf nsz float %73, %21
  %75 = fptosi float %74 to i32
  %76 = tail call i32 @llvm.smin.i32(i32 %75, i32 %33)
  %77 = sitofp i32 %62 to float
  %78 = fsub reassoc ninf nsz float %77, %38
  %79 = fdiv reassoc ninf nsz float %78, %34
  %80 = sitofp i32 %59 to float
  %81 = fsub reassoc ninf nsz float %80, %39
  %82 = fdiv reassoc ninf nsz float %81, %35
  %83 = tail call reassoc ninf nsz float @llvm.floor.f32(float %79)
  %84 = fptosi float %83 to i32
  %85 = tail call reassoc ninf nsz float @llvm.floor.f32(float %82)
  %86 = fptosi float %85 to i32
  %87 = add i32 %84, 1
  %88 = add i32 %86, 1
  %89 = sitofp i32 %84 to float
  %90 = fsub reassoc ninf nsz float %79, %89
  %91 = sitofp i32 %86 to float
  %92 = fsub reassoc ninf nsz float %82, %91
  %93 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %94 = tail call i32 @llvm.smin.i32(i32 %36, i32 %93)
  %95 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %36, i32 %95)
  %97 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %98 = tail call i32 @llvm.smin.i32(i32 %37, i32 %97)
  %99 = tail call i32 @llvm.smax.i32(i32 %88, i32 0)
  %100 = tail call i32 @llvm.smin.i32(i32 %37, i32 %99)
  %101 = mul i32 %98, %29
  %102 = add i32 %94, %101
  %103 = add i32 %96, %101
  %104 = mul i32 %100, %29
  %105 = add i32 %104, %94
  %106 = add i32 %96, %104
  %107 = load ptr, ptr %44, align 8
  %108 = load i32, ptr %45, align 4
  %109 = mul i32 %102, %108
  %110 = add i32 %109, %76
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, ptr %107, i64 %111
  %113 = load float, ptr %112, align 4
  %114 = mul i32 %103, %108
  %115 = add i32 %114, %76
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %107, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = mul i32 %105, %108
  %120 = add i32 %119, %76
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %107, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = mul i32 %106, %108
  %125 = add i32 %124, %76
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %107, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = fsub reassoc ninf nsz float 1.000000e+00, %90
  %130 = fmul reassoc ninf nsz float %129, %113
  %131 = fmul reassoc ninf nsz float %90, %118
  %132 = fadd reassoc ninf nsz float %130, %131
  %133 = fmul reassoc ninf nsz float %129, %123
  %134 = fmul reassoc ninf nsz float %90, %128
  %135 = fadd reassoc ninf nsz float %133, %134
  %136 = fsub reassoc ninf nsz float %135, %132
  %137 = fmul reassoc ninf nsz float %136, %92
  %138 = fadd reassoc ninf nsz float %137, %132
  %139 = fmul reassoc ninf nsz float %138, %21
  %140 = fdiv reassoc ninf nsz float %139, %40
  %141 = load ptr, ptr %46, align 8
  %142 = load i32, ptr %47, align 4
  %143 = sub i32 %142, %52
  %144 = mul i32 %143, %59
  %145 = add i32 %.06, %144
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, ptr %141, i64 %146
  store float %140, ptr %147, align 4
  %148 = add nsw i32 %.06, 1
  %exitcond.not = icmp eq i32 %18, %148
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
