; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jacobi_step_c476_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 64
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 68
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 12
  store i32 %11, ptr %15, align 4
  %16 = tail call i32 @llvm.smax.i32(i32 %11, i32 0)
  %17 = load ptr, ptr %3, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 4
  store i32 %16, ptr %20, align 4
  %21 = mul i32 %16, %8
  %22 = load ptr, ptr %3, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 32872
  %24 = load ptr, ptr %23, align 8
  store i32 %21, ptr %24, align 4
  ret void
}

define void @_jacobi_step_c476_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = getelementptr i8, ptr %20, i64 56
  %22 = getelementptr i8, ptr %20, i64 52
  %23 = getelementptr i8, ptr %20, i64 8
  %24 = getelementptr i8, ptr %20, i64 4
  %25 = getelementptr i8, ptr %20, i64 40
  %26 = getelementptr i8, ptr %20, i64 36
  %27 = getelementptr i8, ptr %20, i64 24
  %28 = getelementptr i8, ptr %20, i64 20
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %.049 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %61, %for_loop_inc ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.049, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.049
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.049, %35
  %39 = and i1 %37, %38
  %.neg5 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg5
  %41 = mul i32 %40, %33
  %42 = mul i32 %33, -1
  %43 = mul i32 %42, %40
  %44 = add i32 %.049, %43
  %45 = load ptr, ptr %21, align 8
  %46 = load i32, ptr %22, align 4
  %47 = sub i32 %46, %33
  %48 = mul i32 %47, %40
  %49 = add i32 %.049, %48
  %50 = sext i32 %49 to i64
  %51 = getelementptr float, ptr %45, i64 %50
  %52 = load float, ptr %51, align 4
  %53 = fcmp reassoc ninf nsz olt float %52, 5.000000e-01
  br i1 %53, label %true_block, label %after_if

for_loop_inc:                                     ; preds = %after_if27, %true_block25, %true_block
  %.sink = phi float [ %179, %after_if27 ], [ %143, %true_block25 ], [ %69, %true_block ]
  %54 = load ptr, ptr %27, align 8
  %55 = load i32, ptr %28, align 4
  %56 = sub i32 %55, %33
  %57 = mul i32 %56, %40
  %58 = add i32 %.049, %57
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, ptr %54, i64 %59
  store float %.sink, ptr %60, align 4
  %61 = add nsw i32 %.049, 1
  %exitcond.not = icmp eq i32 %18, %61
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %62 = load ptr, ptr %23, align 8
  %63 = load i32, ptr %24, align 4
  %64 = sub i32 %63, %33
  %65 = mul i32 %64, %40
  %66 = add i32 %.049, %65
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, ptr %62, i64 %67
  %69 = load float, ptr %68, align 4
  br label %for_loop_inc

after_if:                                         ; preds = %for_loop_body
  %70 = add i32 %40, -1
  %71 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %72 = load i32, ptr %71, align 4
  %73 = add i32 %72, -1
  %74 = tail call i32 @llvm.smax.i32(i32 %70, i32 0)
  %75 = tail call i32 @llvm.smin.i32(i32 %73, i32 %74)
  %76 = add i32 %44, -1
  %77 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %78 = load i32, ptr %77, align 4
  %79 = add i32 %78, -1
  %80 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %81 = tail call i32 @llvm.smin.i32(i32 %79, i32 %80)
  %82 = mul i32 %75, %46
  %83 = add i32 %82, %81
  %84 = sext i32 %83 to i64
  %85 = getelementptr float, ptr %45, i64 %84
  %86 = load float, ptr %85, align 4
  %87 = fcmp reassoc ninf nsz olt float %86, 5.000000e-01
  %88 = tail call i32 @llvm.smax.i32(i32 %44, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %79, i32 %88)
  %90 = add i32 %82, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %45, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = fcmp reassoc ninf nsz olt float %93, 5.000000e-01
  %.1 = select i1 %94, i1 true, i1 %87
  %95 = add i32 %44, 1
  %96 = tail call i32 @llvm.smax.i32(i32 %95, i32 0)
  %97 = tail call i32 @llvm.smin.i32(i32 %79, i32 %96)
  %98 = add i32 %82, %97
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %45, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = fcmp reassoc ninf nsz olt float %101, 5.000000e-01
  br i1 %102, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if
  %.2 = phi i1 [ true, %true_block7 ], [ %.1, %after_if ]
  %103 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %104 = tail call i32 @llvm.smin.i32(i32 %73, i32 %103)
  %105 = mul i32 %104, %46
  %106 = add i32 %105, %81
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, ptr %45, i64 %107
  %109 = load float, ptr %108, align 4
  %110 = fcmp reassoc ninf nsz olt float %109, 5.000000e-01
  %.3 = select i1 %110, i1 true, i1 %.2
  %111 = add i32 %105, %97
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %45, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = fcmp reassoc ninf nsz olt float %114, 5.000000e-01
  br i1 %115, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if9
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if9
  %.4 = phi i1 [ true, %true_block13 ], [ %.3, %after_if9 ]
  %116 = add i32 %40, 1
  %117 = tail call i32 @llvm.smax.i32(i32 %116, i32 0)
  %118 = tail call i32 @llvm.smin.i32(i32 %73, i32 %117)
  %119 = mul i32 %118, %46
  %120 = add i32 %119, %89
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %45, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = fcmp reassoc ninf nsz olt float %123, 5.000000e-01
  br i1 %124, label %true_block25, label %after_if21

after_if21:                                       ; preds = %after_if15
  %125 = add i32 %119, %81
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %45, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = fcmp reassoc ninf nsz olt float %128, 5.000000e-01
  %130 = add i32 %119, %97
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, ptr %45, i64 %131
  %133 = load float, ptr %132, align 4
  %134 = fcmp reassoc ninf nsz olt float %133, 5.000000e-01
  %135 = select i1 %134, i1 true, i1 %129
  %.7 = select i1 %135, i1 true, i1 %.4
  br i1 %.7, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if21, %after_if15
  %136 = load ptr, ptr %23, align 8
  %137 = load i32, ptr %24, align 4
  %138 = sub i32 %137, %33
  %139 = mul i32 %138, %40
  %140 = add i32 %.049, %139
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %136, i64 %141
  %143 = load float, ptr %142, align 4
  br label %for_loop_inc

after_if27:                                       ; preds = %after_if21
  %144 = load ptr, ptr %23, align 8
  %145 = load i32, ptr %24, align 4
  %146 = mul i32 %145, %75
  %147 = sub i32 %146, %41
  %148 = add i32 %.049, %147
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %144, i64 %149
  %151 = load float, ptr %150, align 4
  %152 = mul i32 %145, %118
  %153 = sub i32 %152, %41
  %154 = add i32 %.049, %153
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %144, i64 %155
  %157 = load float, ptr %156, align 4
  %158 = mul i32 %145, %40
  %159 = add i32 %158, %81
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %144, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = add i32 %158, %97
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %144, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = fadd reassoc ninf nsz float %157, %151
  %168 = fadd reassoc ninf nsz float %167, %162
  %169 = fadd reassoc ninf nsz float %168, %166
  %170 = load ptr, ptr %25, align 8
  %171 = load i32, ptr %26, align 4
  %172 = sub i32 %171, %33
  %173 = mul i32 %172, %40
  %174 = add i32 %.049, %173
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %170, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = fsub reassoc ninf nsz float %169, %177
  %179 = fmul reassoc ninf nsz float %178, 2.500000e-01
  br label %for_loop_inc
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
