; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.20 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @postprocess_spatial_weight_kernel_c100_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 40
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 44
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

define void @postprocess_spatial_weight_kernel_c100_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 32
  %21 = load float, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 36
  %23 = load float, ptr %22, align 4
  %24 = fcmp reassoc ninf nsz ueq float %21, 1.000000e+00
  %25 = icmp slt i32 %16, %18
  br i1 %25, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %26 = fcmp reassoc ninf nsz ogt float %23, 0.000000e+00
  %27 = getelementptr i8, ptr %19, i64 8
  %28 = getelementptr i8, ptr %19, i64 4
  %29 = fsub reassoc ninf nsz float 1.000000e+00, %23
  %30 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %29, float 0x3EE4F8B580000000)
  %31 = getelementptr i8, ptr %19, i64 24
  %32 = getelementptr i8, ptr %19, i64 20
  br i1 %26, label %for_loop_body.lr.ph.split.us, label %for_loop_body.lr.ph.split

for_loop_body.lr.ph.split.us:                     ; preds = %for_loop_body.lr.ph
  br i1 %24, label %for_loop_body.us.us.preheader, label %for_loop_body.us.preheader

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph.split.us
  br label %for_loop_body.us

for_loop_body.us.us.preheader:                    ; preds = %for_loop_body.lr.ph.split.us
  br label %for_loop_body.us.us

for_loop_body.us.us:                              ; preds = %for_loop_body.us.us, %for_loop_body.us.us.preheader
  %.059.us.us = phi i32 [ %64, %for_loop_body.us.us ], [ %16, %for_loop_body.us.us.preheader ]
  %33 = load ptr, ptr %3, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 4
  %37 = load i32, ptr %36, align 4
  %38 = sdiv i32 %.059.us.us, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %.059.us.us
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %.059.us.us, %39
  %43 = and i1 %41, %42
  %.neg8.us.us = sext i1 %43 to i32
  %44 = add i32 %38, %.neg8.us.us
  %45 = load ptr, ptr %27, align 8
  %46 = load i32, ptr %28, align 4
  %47 = sub i32 %46, %37
  %48 = mul i32 %47, %44
  %49 = add i32 %.059.us.us, %48
  %50 = sext i32 %49 to i64
  %51 = getelementptr float, ptr %45, i64 %50
  %52 = load float, ptr %51, align 4
  %53 = fsub reassoc ninf nsz float %52, %23
  %54 = fdiv reassoc ninf nsz float %53, %30
  %55 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %54, float 1.000000e+00)
  %56 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %55, float 0.000000e+00)
  %57 = load ptr, ptr %31, align 8
  %58 = load i32, ptr %32, align 4
  %59 = sub i32 %58, %37
  %60 = mul i32 %59, %44
  %61 = add i32 %.059.us.us, %60
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, ptr %57, i64 %62
  store float %56, ptr %63, align 4
  %64 = add nsw i32 %.059.us.us, 1
  %exitcond20.not = icmp eq i32 %18, %64
  br i1 %exitcond20.not, label %after_for.loopexit, label %for_loop_body.us.us

for_loop_body.us:                                 ; preds = %for_loop_body.us, %for_loop_body.us.preheader
  %.059.us = phi i32 [ %98, %for_loop_body.us ], [ %16, %for_loop_body.us.preheader ]
  %65 = load ptr, ptr %3, align 8
  %66 = getelementptr inbounds nuw i8, ptr %65, i64 32872
  %67 = load ptr, ptr %66, align 8
  %68 = getelementptr inbounds nuw i8, ptr %67, i64 4
  %69 = load i32, ptr %68, align 4
  %70 = sdiv i32 %.059.us, %69
  %71 = mul i32 %70, %69
  %72 = xor i32 %69, %.059.us
  %73 = icmp slt i32 %72, 0
  %74 = icmp ne i32 %.059.us, %71
  %75 = and i1 %73, %74
  %.neg8.us = sext i1 %75 to i32
  %76 = add i32 %70, %.neg8.us
  %77 = load ptr, ptr %27, align 8
  %78 = load i32, ptr %28, align 4
  %79 = sub i32 %78, %69
  %80 = mul i32 %79, %76
  %81 = add i32 %.059.us, %80
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, ptr %77, i64 %82
  %84 = load float, ptr %83, align 4
  %85 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %84, float 0.000000e+00)
  %86 = tail call noundef float @powf(float noundef %85, float noundef %21) #8
  %87 = fsub reassoc ninf nsz float %86, %23
  %88 = fdiv reassoc ninf nsz float %87, %30
  %89 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %88, float 1.000000e+00)
  %90 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %89, float 0.000000e+00)
  %91 = load ptr, ptr %31, align 8
  %92 = load i32, ptr %32, align 4
  %93 = sub i32 %92, %69
  %94 = mul i32 %93, %76
  %95 = add i32 %.059.us, %94
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %91, i64 %96
  store float %90, ptr %97, align 4
  %98 = add nsw i32 %.059.us, 1
  %exitcond19.not = icmp eq i32 %18, %98
  br i1 %exitcond19.not, label %after_for.loopexit30, label %for_loop_body.us

for_loop_body.lr.ph.split:                        ; preds = %for_loop_body.lr.ph
  br i1 %24, label %for_loop_body.us10.preheader, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph.split
  br label %for_loop_body

for_loop_body.us10.preheader:                     ; preds = %for_loop_body.lr.ph.split
  br label %for_loop_body.us10

for_loop_body.us10:                               ; preds = %for_loop_body.us10, %for_loop_body.us10.preheader
  %.059.us11 = phi i32 [ %126, %for_loop_body.us10 ], [ %16, %for_loop_body.us10.preheader ]
  %99 = load ptr, ptr %3, align 8
  %100 = getelementptr inbounds nuw i8, ptr %99, i64 32872
  %101 = load ptr, ptr %100, align 8
  %102 = getelementptr inbounds nuw i8, ptr %101, i64 4
  %103 = load i32, ptr %102, align 4
  %104 = sdiv i32 %.059.us11, %103
  %105 = mul i32 %104, %103
  %106 = xor i32 %103, %.059.us11
  %107 = icmp slt i32 %106, 0
  %108 = icmp ne i32 %.059.us11, %105
  %109 = and i1 %107, %108
  %.neg8.us12 = sext i1 %109 to i32
  %110 = add i32 %104, %.neg8.us12
  %111 = load ptr, ptr %27, align 8
  %112 = load i32, ptr %28, align 4
  %113 = sub i32 %112, %103
  %114 = mul i32 %113, %110
  %115 = add i32 %.059.us11, %114
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %111, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = load ptr, ptr %31, align 8
  %120 = load i32, ptr %32, align 4
  %121 = sub i32 %120, %103
  %122 = mul i32 %121, %110
  %123 = add i32 %.059.us11, %122
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %119, i64 %124
  store float %118, ptr %125, align 4
  %126 = add nsw i32 %.059.us11, 1
  %exitcond18.not = icmp eq i32 %18, %126
  br i1 %exitcond18.not, label %after_for.loopexit31, label %for_loop_body.us10

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.059 = phi i32 [ %156, %for_loop_body ], [ %16, %for_loop_body.preheader ]
  %127 = load ptr, ptr %3, align 8
  %128 = getelementptr inbounds nuw i8, ptr %127, i64 32872
  %129 = load ptr, ptr %128, align 8
  %130 = getelementptr inbounds nuw i8, ptr %129, i64 4
  %131 = load i32, ptr %130, align 4
  %132 = sdiv i32 %.059, %131
  %133 = mul i32 %132, %131
  %134 = xor i32 %131, %.059
  %135 = icmp slt i32 %134, 0
  %136 = icmp ne i32 %.059, %133
  %137 = and i1 %135, %136
  %.neg8 = sext i1 %137 to i32
  %138 = add i32 %132, %.neg8
  %139 = load ptr, ptr %27, align 8
  %140 = load i32, ptr %28, align 4
  %141 = sub i32 %140, %131
  %142 = mul i32 %141, %138
  %143 = add i32 %.059, %142
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %139, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %146, float 0.000000e+00)
  %148 = tail call noundef float @powf(float noundef %147, float noundef %21) #8
  %149 = load ptr, ptr %31, align 8
  %150 = load i32, ptr %32, align 4
  %151 = sub i32 %150, %131
  %152 = mul i32 %151, %138
  %153 = add i32 %.059, %152
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %149, i64 %154
  store float %148, ptr %155, align 4
  %156 = add nsw i32 %.059, 1
  %exitcond.not = icmp eq i32 %18, %156
  br i1 %exitcond.not, label %after_for.loopexit32, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body.us.us
  br label %after_for

after_for.loopexit30:                             ; preds = %for_loop_body.us
  br label %after_for

after_for.loopexit31:                             ; preds = %for_loop_body.us10
  br label %after_for

after_for.loopexit32:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit32, %after_for.loopexit31, %after_for.loopexit30, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @powf(float noundef, float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.20, align 8
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
