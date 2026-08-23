; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.6 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_compute_inlier_mean_kernel_c216_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr inbounds nuw i8, ptr %1, i64 32872
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 20
  store float 0.000000e+00, ptr %4, align 4
  %5 = load ptr, ptr %0, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 32872
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 24
  store float 0.000000e+00, ptr %8, align 4
  %9 = load ptr, ptr %0, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 32872
  %11 = load ptr, ptr %10, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 28
  store float 0.000000e+00, ptr %12, align 4
  %13 = load ptr, ptr %context, align 8
  %14 = getelementptr i8, ptr %13, i64 56
  %15 = load i32, ptr %14, align 4
  %16 = load ptr, ptr %0, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 32872
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 12
  store i32 %15, ptr %19, align 4
  %20 = load ptr, ptr %context, align 8
  %21 = getelementptr i8, ptr %20, i64 64
  %22 = load i32, ptr %21, align 4
  %23 = load ptr, ptr %0, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 32872
  %25 = load ptr, ptr %24, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 8
  store i32 %22, ptr %26, align 4
  %27 = add i32 %22, -1
  %28 = add i32 %27, %15
  %29 = sdiv i32 %28, %22
  %30 = mul i32 %29, %22
  %31 = xor i32 %28, %22
  %32 = icmp slt i32 %31, 0
  %33 = icmp ne i32 %30, %28
  %34 = and i1 %32, %33
  %.neg = sext i1 %34 to i32
  %35 = add i32 %29, %.neg
  %36 = tail call i32 @llvm.smax.i32(i32 %35, i32 0)
  %37 = load ptr, ptr %context, align 8
  %38 = getelementptr i8, ptr %37, i64 60
  %39 = load i32, ptr %38, align 4
  %40 = load ptr, ptr %0, align 8
  %41 = getelementptr inbounds nuw i8, ptr %40, i64 32872
  %42 = load ptr, ptr %41, align 8
  %43 = getelementptr inbounds nuw i8, ptr %42, i64 16
  store i32 %39, ptr %43, align 4
  %44 = add i32 %27, %39
  %45 = sdiv i32 %44, %22
  %46 = mul i32 %45, %22
  %47 = xor i32 %44, %22
  %48 = icmp slt i32 %47, 0
  %49 = icmp ne i32 %46, %44
  %50 = and i1 %48, %49
  %.neg1 = sext i1 %50 to i32
  %51 = add i32 %45, %.neg1
  %52 = tail call i32 @llvm.smax.i32(i32 %51, i32 0)
  %53 = load ptr, ptr %0, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 32872
  %55 = load ptr, ptr %54, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 4
  store i32 %52, ptr %56, align 4
  %57 = mul i32 %52, %36
  %58 = load ptr, ptr %0, align 8
  %59 = getelementptr inbounds nuw i8, ptr %58, i64 32872
  %60 = load ptr, ptr %59, align 8
  store i32 %57, ptr %60, align 4
  ret void
}

define void @_compute_inlier_mean_kernel_c216_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
cpu_parallel_range_for.exit:
  %0 = alloca %struct.range_task_helper_context, align 8
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %0)
  %1 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %2 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %4 = getelementptr inbounds nuw i8, ptr %0, i64 32
  store ptr %context, ptr %0, align 8
  store ptr @function_body, ptr %1, align 8
  store i64 12, ptr %4, align 8
  store ptr @function_body.1, ptr %2, align 8
  store ptr @function_body.2, ptr %3, align 8
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

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: write)
define internal void @function_body(ptr nocapture readnone %0, ptr nocapture writeonly initializes((0, 12)) %1) #1 {
allocs:
  store float 0.000000e+00, ptr %1, align 4
  %2 = getelementptr i8, ptr %1, i64 4
  store float 0.000000e+00, ptr %2, align 4
  %3 = getelementptr i8, ptr %1, i64 8
  store float 0.000000e+00, ptr %3, align 4
  ret void
}

; Function Attrs: nofree norecurse nosync nounwind memory(read, argmem: readwrite, inaccessiblemem: none)
define internal void @function_body.1(ptr nocapture readonly %0, ptr nocapture %1, i32 %2) #2 {
allocs:
  %3 = getelementptr i8, ptr %1, i64 8
  %4 = getelementptr i8, ptr %1, i64 4
  %5 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = load i32, ptr %8, align 4
  %10 = add i32 %9, 7
  %11 = sdiv i32 %10, 8
  %12 = icmp slt i32 %10, 0
  %13 = shl nsw i32 %11, 3
  %14 = icmp ne i32 %13, %10
  %15 = and i1 %12, %14
  %.neg = sext i1 %15 to i32
  %16 = add nsw i32 %11, %.neg
  %17 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %16, i32 512)
  %18 = mul i32 %17, %2
  %19 = add i32 %18, %17
  %20 = tail call i32 @llvm.smin.i32(i32 %9, i32 %19)
  %21 = icmp slt i32 %18, %20
  br i1 %21, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.047 = phi i32 [ %58, %after_if3 ], [ %18, %for_loop_body.preheader ]
  %22 = load ptr, ptr %5, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 32872
  %24 = load ptr, ptr %23, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 4
  %26 = load i32, ptr %25, align 4
  %27 = sdiv i32 %.047, %26
  %28 = mul i32 %27, %26
  %29 = xor i32 %26, %.047
  %30 = icmp slt i32 %29, 0
  %31 = icmp ne i32 %.047, %28
  %32 = and i1 %30, %31
  %.neg6 = sext i1 %32 to i32
  %33 = add i32 %27, %.neg6
  %34 = mul i32 %26, -1
  %35 = mul i32 %34, %33
  %36 = add i32 %.047, %35
  %37 = getelementptr inbounds nuw i8, ptr %24, i64 8
  %38 = load i32, ptr %37, align 4
  %39 = mul i32 %33, %38
  %40 = mul i32 %36, %38
  %41 = getelementptr inbounds nuw i8, ptr %24, i64 12
  %42 = load i32, ptr %41, align 4
  %43 = icmp slt i32 %39, %42
  br i1 %43, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %44 = getelementptr inbounds nuw i8, ptr %24, i64 16
  %45 = load i32, ptr %44, align 4
  %46 = icmp slt i32 %40, %45
  br i1 %46, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %47 = load ptr, ptr %0, align 8
  %48 = getelementptr i8, ptr %47, i64 32
  %49 = load ptr, ptr %48, align 8
  %50 = getelementptr i8, ptr %47, i64 28
  %51 = load i32, ptr %50, align 4
  %52 = mul i32 %51, %39
  %53 = add i32 %52, %40
  %54 = sext i32 %53 to i64
  %55 = getelementptr i32, ptr %49, i64 %54
  %56 = load i32, ptr %55, align 4
  %57 = icmp eq i32 %56, 1
  br i1 %57, label %true_block4, label %after_if3

after_if3:                                        ; preds = %true_block4, %true_block1, %true_block, %for_loop_body
  %58 = add nsw i32 %.047, 1
  %exitcond.not = icmp eq i32 %20, %58
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %59 = getelementptr i8, ptr %47, i64 16
  %60 = load ptr, ptr %59, align 8
  %61 = getelementptr i8, ptr %47, i64 4
  %62 = load i32, ptr %61, align 4
  %63 = getelementptr i8, ptr %47, i64 8
  %64 = load i32, ptr %63, align 4
  %65 = mul i32 %62, %39
  %66 = add i32 %65, %40
  %67 = mul i32 %66, %64
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %60, i64 %68
  %70 = load float, ptr %69, align 4
  %71 = load float, ptr %1, align 4
  %72 = fadd reassoc ninf nsz float %71, %70
  store float %72, ptr %1, align 4
  %73 = load ptr, ptr %59, align 8
  %74 = load i32, ptr %61, align 4
  %75 = load i32, ptr %63, align 4
  %76 = mul i32 %74, %39
  %77 = add i32 %76, %40
  %78 = mul i32 %77, %75
  %79 = add i32 %78, 1
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, ptr %73, i64 %80
  %82 = load float, ptr %81, align 4
  %83 = load float, ptr %4, align 4
  %84 = fadd reassoc ninf nsz float %83, %82
  store float %84, ptr %4, align 4
  %85 = load float, ptr %3, align 4
  %86 = fadd reassoc ninf nsz float %85, 1.000000e+00
  store float %86, ptr %3, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nofree norecurse nounwind willreturn memory(readwrite, inaccessiblemem: none)
define internal void @function_body.2(ptr nocapture readonly %0, ptr nocapture readonly %1) #3 {
allocs:
  %2 = load float, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 20
  %8 = atomicrmw fadd ptr %7, float %2 seq_cst, align 4
  %9 = getelementptr i8, ptr %1, i64 4
  %10 = load float, ptr %9, align 4
  %11 = load ptr, ptr %3, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 32872
  %13 = load ptr, ptr %12, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 24
  %15 = atomicrmw fadd ptr %14, float %10 seq_cst, align 4
  %16 = getelementptr i8, ptr %1, i64 8
  %17 = load float, ptr %16, align 4
  %18 = load ptr, ptr %3, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 28
  %22 = atomicrmw fadd ptr %21, float %17 seq_cst, align 4
  ret void
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_compute_inlier_mean_kernel_c216_0_kernel_2_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr inbounds nuw i8, ptr %1, i64 32872
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 28
  %5 = load float, ptr %4, align 4
  %6 = fcmp reassoc ninf nsz ogt float %5, 0.000000e+00
  br i1 %6, label %true_block, label %after_if

true_block:                                       ; preds = %entry
  %7 = getelementptr inbounds nuw i8, ptr %3, i64 20
  %8 = load float, ptr %7, align 4
  %9 = fdiv reassoc ninf nsz float %8, %5
  %10 = load ptr, ptr %context, align 8
  %11 = getelementptr i8, ptr %10, i64 48
  %12 = load ptr, ptr %11, align 8
  store float %9, ptr %12, align 4
  %13 = load ptr, ptr %0, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 24
  %17 = load float, ptr %16, align 4
  %18 = fdiv reassoc ninf nsz float %17, %5
  %19 = load ptr, ptr %11, align 8
  %20 = getelementptr i8, ptr %19, i64 4
  store float %18, ptr %20, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %entry
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.6, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
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
attributes #1 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: write) }
attributes #2 = { nofree norecurse nosync nounwind memory(read, argmem: readwrite, inaccessiblemem: none) }
attributes #3 = { mustprogress nofree norecurse nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nounwind }

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
