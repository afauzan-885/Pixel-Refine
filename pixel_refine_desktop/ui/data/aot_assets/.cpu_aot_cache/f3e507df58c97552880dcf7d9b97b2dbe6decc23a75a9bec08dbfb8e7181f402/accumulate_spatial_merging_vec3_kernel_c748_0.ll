; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.14 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @accumulate_spatial_merging_vec3_kernel_c748_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 104
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 16
  store i32 %2, ptr %7, align 4
  %8 = sitofp i32 %2 to float
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 96
  %11 = load i32, ptr %10, align 4
  %12 = sitofp i32 %11 to float
  %13 = fdiv reassoc ninf nsz float %8, %12
  %14 = load ptr, ptr %3, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 32872
  %16 = load ptr, ptr %15, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 8
  store float %13, ptr %17, align 4
  %18 = load ptr, ptr %context, align 8
  %19 = getelementptr i8, ptr %18, i64 108
  %20 = load i32, ptr %19, align 4
  %21 = load ptr, ptr %3, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 20
  store i32 %20, ptr %24, align 4
  %25 = sitofp i32 %20 to float
  %26 = load ptr, ptr %context, align 8
  %27 = getelementptr i8, ptr %26, i64 100
  %28 = load i32, ptr %27, align 4
  %29 = sitofp i32 %28 to float
  %30 = fdiv reassoc ninf nsz float %25, %29
  %31 = load ptr, ptr %3, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 12
  store float %30, ptr %34, align 4
  %35 = tail call i32 @llvm.smax.i32(i32 %11, i32 0)
  %36 = tail call i32 @llvm.smax.i32(i32 %28, i32 0)
  %37 = load ptr, ptr %3, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 32872
  %39 = load ptr, ptr %38, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 4
  store i32 %36, ptr %40, align 4
  %41 = mul i32 %36, %35
  %42 = load ptr, ptr %3, align 8
  %43 = getelementptr inbounds nuw i8, ptr %42, i64 32872
  %44 = load ptr, ptr %43, align 8
  store i32 %41, ptr %44, align 4
  ret void
}

define void @accumulate_spatial_merging_vec3_kernel_c748_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 112
  %21 = load i32, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = icmp sgt i32 %21, 0
  %24 = getelementptr i8, ptr %19, i64 40
  %25 = getelementptr i8, ptr %19, i64 28
  %26 = getelementptr i8, ptr %19, i64 32
  %27 = getelementptr i8, ptr %19, i64 88
  %28 = getelementptr i8, ptr %19, i64 76
  %29 = getelementptr i8, ptr %19, i64 80
  %30 = getelementptr i8, ptr %19, i64 16
  %31 = getelementptr i8, ptr %19, i64 4
  %32 = getelementptr i8, ptr %19, i64 8
  %33 = getelementptr i8, ptr %19, i64 64
  %34 = getelementptr i8, ptr %19, i64 52
  %35 = getelementptr i8, ptr %19, i64 56
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.0718 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %146, %after_for3 ]
  %36 = load ptr, ptr %3, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 32872
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 4
  %40 = load i32, ptr %39, align 4
  %41 = sdiv i32 %.0718, %40
  %42 = mul i32 %41, %40
  %43 = xor i32 %40, %.0718
  %44 = icmp slt i32 %43, 0
  %45 = icmp ne i32 %42, %.0718
  %46 = and i1 %44, %45
  %.neg8 = sext i1 %46 to i32
  %47 = add i32 %41, %.neg8
  %48 = mul i32 %47, %40
  %49 = sub i32 %.0718, %48
  %50 = sitofp i32 %47 to float
  %51 = getelementptr inbounds nuw i8, ptr %38, i64 8
  %52 = load float, ptr %51, align 4
  %53 = fmul reassoc ninf nsz float %52, %50
  %54 = sitofp i32 %49 to float
  %55 = getelementptr inbounds nuw i8, ptr %38, i64 12
  %56 = load float, ptr %55, align 4
  %57 = fmul reassoc ninf nsz float %56, %54
  %58 = tail call reassoc ninf nsz float @llvm.floor.f32(float %53)
  %59 = fptosi float %58 to i32
  %60 = tail call reassoc ninf nsz float @llvm.floor.f32(float %57)
  %61 = fptosi float %60 to i32
  %62 = add i32 %59, 1
  %63 = getelementptr inbounds nuw i8, ptr %38, i64 16
  %64 = load i32, ptr %63, align 4
  %65 = add i32 %64, -1
  %66 = tail call i32 @llvm.smin.i32(i32 %62, i32 %65)
  %67 = add i32 %61, 1
  %68 = getelementptr inbounds nuw i8, ptr %38, i64 20
  %69 = load i32, ptr %68, align 4
  %70 = add i32 %69, -1
  %71 = tail call i32 @llvm.smin.i32(i32 %67, i32 %70)
  %72 = tail call i32 @llvm.smax.i32(i32 %59, i32 0)
  %73 = tail call i32 @llvm.smax.i32(i32 %61, i32 0)
  %74 = uitofp nneg i32 %72 to float
  %75 = fsub reassoc ninf nsz float %53, %74
  %76 = uitofp nneg i32 %73 to float
  %77 = fsub reassoc ninf nsz float %57, %76
  %78 = fsub reassoc ninf nsz float 1.000000e+00, %75
  %79 = fsub reassoc ninf nsz float 1.000000e+00, %77
  %factor.op.fmul = fmul reassoc ninf nsz float %79, %75
  %factor.op.fmul11 = fmul reassoc ninf nsz float %77, %75
  %factor.op.fmul13 = fmul reassoc ninf nsz float %79, %78
  %factor.op.fmul15 = fmul reassoc ninf nsz float %77, %78
  br i1 %23, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  %80 = mul i32 %40, -1
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader
  %.017 = phi i32 [ %145, %for_loop_body1 ], [ 0, %for_loop_body1.preheader ]
  %81 = load ptr, ptr %24, align 8
  %82 = load i32, ptr %25, align 4
  %83 = load i32, ptr %26, align 4
  %84 = mul i32 %82, %72
  %85 = add i32 %84, %73
  %86 = mul i32 %85, %83
  %87 = add i32 %.017, %86
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %81, i64 %88
  %90 = load float, ptr %89, align 4
  %.reass14 = fmul reassoc ninf nsz float %90, %factor.op.fmul13
  %91 = add i32 %84, %71
  %92 = mul i32 %91, %83
  %93 = add i32 %.017, %92
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %81, i64 %94
  %96 = load float, ptr %95, align 4
  %.reass16 = fmul reassoc ninf nsz float %96, %factor.op.fmul15
  %97 = mul i32 %82, %66
  %98 = add i32 %97, %73
  %99 = mul i32 %98, %83
  %100 = add i32 %.017, %99
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %81, i64 %101
  %103 = load float, ptr %102, align 4
  %.reass = fmul reassoc ninf nsz float %103, %factor.op.fmul
  %104 = add i32 %97, %71
  %105 = mul i32 %104, %83
  %106 = add i32 %.017, %105
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, ptr %81, i64 %107
  %109 = load float, ptr %108, align 4
  %.reass12 = fmul reassoc ninf nsz float %109, %factor.op.fmul11
  %reass.add = fadd reassoc ninf nsz float %.reass12, %.reass
  %reass.add9 = fadd reassoc ninf nsz float %.reass16, %.reass14
  %110 = fadd reassoc ninf nsz float %reass.add, %reass.add9
  %111 = load ptr, ptr %27, align 8
  %112 = load i32, ptr %28, align 4
  %113 = load i32, ptr %29, align 4
  %114 = add i32 %80, %112
  %115 = mul i32 %47, %114
  %116 = add i32 %.0718, %115
  %117 = mul i32 %113, %116
  %118 = add i32 %.017, %117
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %111, i64 %119
  %121 = atomicrmw fadd ptr %120, float %110 seq_cst, align 4
  %122 = load ptr, ptr %30, align 8
  %123 = load i32, ptr %31, align 4
  %124 = load i32, ptr %32, align 4
  %125 = add i32 %80, %123
  %126 = mul i32 %47, %125
  %127 = add i32 %.0718, %126
  %128 = mul i32 %124, %127
  %129 = add i32 %.017, %128
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %122, i64 %130
  %132 = load float, ptr %131, align 4
  %133 = fmul reassoc ninf nsz float %132, %110
  %134 = load ptr, ptr %33, align 8
  %135 = load i32, ptr %34, align 4
  %136 = load i32, ptr %35, align 4
  %137 = add i32 %80, %135
  %138 = mul i32 %47, %137
  %139 = add i32 %.0718, %138
  %140 = mul i32 %136, %139
  %141 = add i32 %.017, %140
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %134, i64 %142
  %144 = atomicrmw fadd ptr %143, float %133 seq_cst, align 4
  %145 = add nuw nsw i32 %.017, 1
  %exitcond.not = icmp eq i32 %21, %145
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1

after_for3.loopexit:                              ; preds = %for_loop_body1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %146 = add nsw i32 %.0718, 1
  %exitcond19.not = icmp eq i32 %146, %18
  br i1 %exitcond19.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.14, align 8
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
attributes #1 = { nofree norecurse nounwind memory(readwrite, inaccessiblemem: none) }
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
