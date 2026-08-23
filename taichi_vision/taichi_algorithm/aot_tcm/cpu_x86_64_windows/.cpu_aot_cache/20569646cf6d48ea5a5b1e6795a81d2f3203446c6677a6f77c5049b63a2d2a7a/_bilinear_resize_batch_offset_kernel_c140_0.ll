; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bilinear_resize_batch_offset_kernel_c140_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 16
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 20
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = getelementptr i8, ptr %0, i64 24
  %8 = load i32, ptr %7, align 4
  %9 = tail call i32 @llvm.smax.i32(i32 %8, i32 0)
  %10 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %11 = load ptr, ptr %10, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 32872
  %13 = load ptr, ptr %12, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 8
  store i32 %9, ptr %14, align 4
  %15 = mul i32 %9, %6
  %16 = load ptr, ptr %10, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 32872
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 4
  store i32 %15, ptr %19, align 4
  %20 = mul i32 %15, %3
  %21 = load ptr, ptr %10, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  store i32 %20, ptr %23, align 4
  ret void
}

define void @_bilinear_resize_batch_offset_kernel_c140_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 64
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 60
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 68
  %27 = load i32, ptr %26, align 4
  %28 = sitofp i32 %21 to float
  %29 = sitofp i32 %23 to float
  %30 = sitofp i32 %25 to float
  %31 = sitofp i32 %27 to float
  %32 = add i32 %21, -1
  %33 = add i32 %25, -1
  %34 = icmp slt i32 %16, %18
  br i1 %34, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %35 = getelementptr i8, ptr %19, i64 48
  %36 = getelementptr i8, ptr %19, i64 44
  %37 = getelementptr i8, ptr %19, i64 8
  %38 = getelementptr i8, ptr %19, i64 4
  %39 = getelementptr i8, ptr %19, i64 32
  %40 = getelementptr i8, ptr %19, i64 20
  %41 = getelementptr i8, ptr %19, i64 24
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.07 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %151, %for_loop_body ]
  %42 = load ptr, ptr %3, align 8
  %43 = getelementptr inbounds nuw i8, ptr %42, i64 32872
  %44 = load ptr, ptr %43, align 8
  %45 = getelementptr inbounds nuw i8, ptr %44, i64 4
  %46 = load i32, ptr %45, align 4
  %47 = sdiv i32 %.07, %46
  %48 = mul i32 %47, %46
  %49 = xor i32 %46, %.07
  %50 = icmp slt i32 %49, 0
  %51 = icmp ne i32 %.07, %48
  %52 = and i1 %50, %51
  %.neg4 = sext i1 %52 to i32
  %53 = add i32 %47, %.neg4
  %54 = mul i32 %53, %46
  %55 = mul i32 %46, -1
  %56 = mul i32 %55, %53
  %57 = add i32 %.07, %56
  %58 = getelementptr inbounds nuw i8, ptr %44, i64 8
  %59 = load i32, ptr %58, align 4
  %60 = sdiv i32 %57, %59
  %61 = mul i32 %60, %59
  %62 = xor i32 %57, %59
  %63 = icmp slt i32 %62, 0
  %64 = icmp ne i32 %.07, %54
  %65 = icmp ne i32 %57, %61
  %66 = and i1 %64, %63
  %67 = and i1 %65, %66
  %.neg5 = sext i1 %67 to i32
  %68 = add i32 %60, %.neg5
  %69 = mul i32 %68, %59
  %70 = load ptr, ptr %35, align 8
  %71 = load i32, ptr %36, align 4
  %72 = mul i32 %53, %71
  %73 = sext i32 %72 to i64
  %74 = getelementptr i32, ptr %70, i64 %73
  %75 = load i32, ptr %74, align 4
  %76 = add i32 %68, %75
  %77 = add i32 %72, 1
  %78 = sext i32 %77 to i64
  %79 = getelementptr i32, ptr %70, i64 %78
  %80 = load i32, ptr %79, align 4
  %81 = sub i32 %80, %69
  %82 = add i32 %57, %81
  %83 = sitofp i32 %76 to float
  %84 = fadd reassoc ninf nsz float %83, 5.000000e-01
  %85 = fmul reassoc ninf nsz float %84, %28
  %86 = fdiv reassoc ninf nsz float %85, %29
  %87 = fadd reassoc ninf nsz float %86, -5.000000e-01
  %88 = sitofp i32 %82 to float
  %89 = fadd reassoc ninf nsz float %88, 5.000000e-01
  %90 = fmul reassoc ninf nsz float %89, %30
  %91 = fdiv reassoc ninf nsz float %90, %31
  %92 = fadd reassoc ninf nsz float %91, -5.000000e-01
  %93 = tail call reassoc ninf nsz float @llvm.floor.f32(float %87)
  %94 = fptosi float %93 to i32
  %95 = tail call reassoc ninf nsz float @llvm.floor.f32(float %92)
  %96 = fptosi float %95 to i32
  %97 = sitofp i32 %94 to float
  %98 = fsub reassoc ninf nsz float %87, %97
  %99 = sitofp i32 %96 to float
  %100 = fsub reassoc ninf nsz float %92, %99
  %101 = add i32 %94, 1
  %102 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %103 = tail call i32 @llvm.smin.i32(i32 %32, i32 %102)
  %104 = tail call i32 @llvm.smax.i32(i32 %101, i32 0)
  %105 = tail call i32 @llvm.smin.i32(i32 %32, i32 %104)
  %106 = add i32 %96, 1
  %107 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %108 = tail call i32 @llvm.smin.i32(i32 %33, i32 %107)
  %109 = tail call i32 @llvm.smax.i32(i32 %106, i32 0)
  %110 = tail call i32 @llvm.smin.i32(i32 %33, i32 %109)
  %111 = load ptr, ptr %37, align 8
  %112 = load i32, ptr %38, align 4
  %113 = mul i32 %103, %112
  %114 = add i32 %108, %113
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %111, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = add i32 %110, %113
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %111, i64 %119
  %121 = load float, ptr %120, align 4
  %122 = mul i32 %105, %112
  %123 = add i32 %122, %108
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %111, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = add i32 %110, %122
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %111, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = fsub reassoc ninf nsz float 1.000000e+00, %100
  %132 = fmul reassoc ninf nsz float %131, %117
  %133 = fmul reassoc ninf nsz float %100, %121
  %134 = fadd reassoc ninf nsz float %132, %133
  %135 = fmul reassoc ninf nsz float %131, %126
  %136 = fmul reassoc ninf nsz float %100, %130
  %137 = fadd reassoc ninf nsz float %135, %136
  %138 = fsub reassoc ninf nsz float %137, %134
  %139 = fmul reassoc ninf nsz float %138, %98
  %140 = fadd reassoc ninf nsz float %139, %134
  %141 = load ptr, ptr %39, align 8
  %142 = load i32, ptr %40, align 4
  %143 = load i32, ptr %41, align 4
  %144 = mul i32 %142, %53
  %145 = add i32 %144, %68
  %146 = mul i32 %145, %143
  %147 = sub i32 %146, %69
  %148 = add i32 %57, %147
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %141, i64 %149
  store float %140, ptr %150, align 4
  %151 = add nsw i32 %.07, 1
  %exitcond.not = icmp eq i32 %18, %151
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.7, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
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
attributes #3 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
