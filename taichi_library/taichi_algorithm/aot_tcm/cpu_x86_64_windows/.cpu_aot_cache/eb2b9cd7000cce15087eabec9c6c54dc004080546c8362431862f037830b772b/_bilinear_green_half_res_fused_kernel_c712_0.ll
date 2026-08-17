; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bilinear_green_half_res_fused_kernel_c712_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 52
  %2 = load float, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 48
  %4 = load float, ptr %3, align 4
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 8
  store float %4, ptr %9, align 4
  %10 = fsub reassoc ninf nsz float %2, %4
  %11 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %10, float 1.000000e+00)
  %12 = fdiv reassoc ninf nsz float 1.000000e+00, %11
  %13 = load ptr, ptr %5, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 12
  store float %12, ptr %16, align 4
  %17 = load ptr, ptr %context, align 8
  %18 = getelementptr i8, ptr %17, i64 56
  %19 = load i32, ptr %18, align 4
  %20 = sdiv i32 %19, 2
  %21 = icmp slt i32 %19, 0
  %22 = shl nsw i32 %20, 1
  %23 = icmp ne i32 %22, %19
  %24 = and i1 %21, %23
  %.neg = sext i1 %24 to i32
  %25 = add nsw i32 %20, %.neg
  %26 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 %25, i32 range(i32 -1073741825, 1073741824) 0)
  %27 = getelementptr i8, ptr %17, i64 60
  %28 = load i32, ptr %27, align 4
  %29 = sdiv i32 %28, 2
  %30 = icmp slt i32 %28, 0
  %31 = shl nsw i32 %29, 1
  %32 = icmp ne i32 %31, %28
  %33 = and i1 %30, %32
  %.neg1 = sext i1 %33 to i32
  %34 = add nsw i32 %29, %.neg1
  %35 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 %34, i32 range(i32 -1073741825, 1073741824) 0)
  %36 = load ptr, ptr %5, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 32872
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 4
  store i32 %35, ptr %39, align 4
  %40 = mul i32 %35, %26
  %41 = load ptr, ptr %5, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  store i32 %40, ptr %43, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @_bilinear_green_half_res_fused_kernel_c712_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
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
  %15 = tail call range(i32 -1073741825, 1073741824) i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  %20 = shl i32 %16, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if72, %for_loop_body.preheader
  %lsr.iv = phi i32 [ %20, %for_loop_body.preheader ], [ %lsr.iv.next, %after_if72 ]
  %.06473 = phi i32 [ %167, %after_if72 ], [ %16, %for_loop_body.preheader ]
  %21 = load ptr, ptr %3, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 4
  %25 = load i32, ptr %24, align 4
  %26 = sdiv i32 %.06473, %25
  %27 = mul i32 %26, %25
  %28 = xor i32 %25, %.06473
  %29 = icmp slt i32 %28, 0
  %30 = icmp ne i32 %.06473, %27
  %31 = and i1 %29, %30
  %.neg69 = sext i1 %31 to i32
  %32 = add i32 %26, %.neg69
  %33 = shl i32 %32, 1
  %34 = load ptr, ptr %0, align 8
  %35 = getelementptr i8, ptr %34, i64 64
  %36 = load i32, ptr %35, align 4
  switch i32 %36, label %after_if12 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

after_for.loopexit:                               ; preds = %after_if72
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block10:                                     ; preds = %for_loop_body, %for_loop_body
  %.not = icmp eq i32 %36, 1
  %37 = getelementptr i8, ptr %34, i64 8
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr i8, ptr %34, i64 4
  %40 = load i32, ptr %39, align 4
  %41 = shl i32 %40, 1
  %42 = shl i32 %25, 1
  %43 = sub i32 %41, %42
  %44 = mul i32 %43, %32
  %45 = add i32 %lsr.iv, %44
  %46 = sext i32 %45 to i64
  %47 = getelementptr float, ptr %38, i64 %46
  %48 = load float, ptr %47, align 4
  %49 = getelementptr inbounds nuw i8, ptr %23, i64 8
  %50 = load float, ptr %49, align 4
  %51 = fsub reassoc ninf nsz float %48, %50
  %52 = getelementptr inbounds nuw i8, ptr %23, i64 12
  %53 = load float, ptr %52, align 4
  %54 = fmul reassoc ninf nsz float %51, %53
  %55 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %54, float 0.000000e+00)
  %56 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %55, float 1.000000e+00)
  %.053.in.v = select i1 %.not, i64 36, i64 44
  %.053.in = getelementptr i8, ptr %34, i64 %.053.in.v
  %.053 = load float, ptr %.053.in, align 4
  %57 = fmul reassoc ninf nsz float %56, %.053
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %for_loop_body
  %.060 = phi float [ %57, %true_block10 ], [ 0.000000e+00, %for_loop_body ]
  %.058 = phi float [ 1.000000e+00, %true_block10 ], [ 0.000000e+00, %for_loop_body ]
  %58 = getelementptr i8, ptr %34, i64 68
  %59 = load i32, ptr %58, align 4
  switch i32 %59, label %after_if30 [
    i32 3, label %true_block28
    i32 1, label %true_block28
  ]

true_block28:                                     ; preds = %after_if12, %after_if12
  %.not70 = icmp eq i32 %59, 1
  %60 = getelementptr i8, ptr %34, i64 8
  %61 = load ptr, ptr %60, align 8
  %62 = getelementptr i8, ptr %34, i64 4
  %63 = load i32, ptr %62, align 4
  %64 = shl i32 %63, 1
  %65 = shl i32 %25, 1
  %66 = sub i32 %64, %65
  %67 = mul i32 %66, %32
  %68 = add i32 %lsr.iv, %67
  %69 = add i32 %68, 1
  %70 = sext i32 %69 to i64
  %71 = getelementptr float, ptr %61, i64 %70
  %72 = load float, ptr %71, align 4
  %73 = getelementptr inbounds nuw i8, ptr %23, i64 8
  %74 = load float, ptr %73, align 4
  %75 = fsub reassoc ninf nsz float %72, %74
  %76 = getelementptr inbounds nuw i8, ptr %23, i64 12
  %77 = load float, ptr %76, align 4
  %78 = fmul reassoc ninf nsz float %75, %77
  %79 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %78, float 0.000000e+00)
  %80 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %79, float 1.000000e+00)
  %.048.in.v = select i1 %.not70, i64 36, i64 44
  %.048.in = getelementptr i8, ptr %34, i64 %.048.in.v
  %.048 = load float, ptr %.048.in, align 4
  %81 = fmul reassoc ninf nsz float %80, %.048
  %82 = fadd reassoc ninf nsz float %81, %.060
  %83 = fadd reassoc ninf nsz float %.058, 1.000000e+00
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if12
  %.161 = phi float [ %82, %true_block28 ], [ %.060, %after_if12 ]
  %.159 = phi float [ %83, %true_block28 ], [ %.058, %after_if12 ]
  %84 = or disjoint i32 %33, 1
  %85 = getelementptr i8, ptr %34, i64 72
  %86 = load i32, ptr %85, align 4
  switch i32 %86, label %false_block59 [
    i32 3, label %true_block46
    i32 1, label %true_block46
  ]

true_block46:                                     ; preds = %after_if30, %after_if30
  %.not71 = icmp eq i32 %86, 1
  %87 = getelementptr i8, ptr %34, i64 8
  %88 = load ptr, ptr %87, align 8
  %89 = getelementptr i8, ptr %34, i64 4
  %90 = load i32, ptr %89, align 4
  %91 = mul i32 %90, %84
  %92 = shl i32 %25, 1
  %93 = mul i32 %92, %32
  %94 = sub i32 %91, %93
  %95 = add i32 %lsr.iv, %94
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %88, i64 %96
  %98 = load float, ptr %97, align 4
  %99 = getelementptr inbounds nuw i8, ptr %23, i64 8
  %100 = load float, ptr %99, align 4
  %101 = fsub reassoc ninf nsz float %98, %100
  %102 = getelementptr inbounds nuw i8, ptr %23, i64 12
  %103 = load float, ptr %102, align 4
  %104 = fmul reassoc ninf nsz float %101, %103
  %105 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %104, float 0.000000e+00)
  %106 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %105, float 1.000000e+00)
  %.043.in.v = select i1 %.not71, i64 36, i64 44
  %.043.in = getelementptr i8, ptr %34, i64 %.043.in.v
  %.043 = load float, ptr %.043.in, align 4
  %107 = fmul reassoc ninf nsz float %106, %.043
  %108 = fadd reassoc ninf nsz float %107, %.161
  %109 = fadd reassoc ninf nsz float %.159, 1.000000e+00
  br label %false_block59

false_block59:                                    ; preds = %true_block46, %after_if30
  %.262 = phi float [ %108, %true_block46 ], [ %.161, %after_if30 ]
  %.2 = phi float [ %109, %true_block46 ], [ %.159, %after_if30 ]
  %110 = getelementptr i8, ptr %34, i64 76
  %111 = load i32, ptr %110, align 4
  switch i32 %111, label %after_if66 [
    i32 3, label %true_block64
    i32 1, label %true_block64
  ]

true_block64:                                     ; preds = %false_block59, %false_block59
  %.not72 = icmp eq i32 %111, 1
  %112 = getelementptr i8, ptr %34, i64 8
  %113 = load ptr, ptr %112, align 8
  %114 = getelementptr i8, ptr %34, i64 4
  %115 = load i32, ptr %114, align 4
  %116 = mul i32 %115, %84
  %117 = shl i32 %25, 1
  %118 = mul i32 %117, %32
  %119 = sub i32 %116, %118
  %120 = add i32 %lsr.iv, %119
  %121 = add i32 %120, 1
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %113, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = getelementptr inbounds nuw i8, ptr %23, i64 8
  %126 = load float, ptr %125, align 4
  %127 = fsub reassoc ninf nsz float %124, %126
  %128 = getelementptr inbounds nuw i8, ptr %23, i64 12
  %129 = load float, ptr %128, align 4
  %130 = fmul reassoc ninf nsz float %127, %129
  %131 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %130, float 0.000000e+00)
  %132 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %131, float 1.000000e+00)
  %.0.in.v = select i1 %.not72, i64 36, i64 44
  %.0.in = getelementptr i8, ptr %34, i64 %.0.in.v
  %.0 = load float, ptr %.0.in, align 4
  %133 = fmul reassoc ninf nsz float %132, %.0
  %134 = fadd reassoc ninf nsz float %133, %.262
  %135 = fadd reassoc ninf nsz float %.2, 1.000000e+00
  br label %after_if66

after_if66:                                       ; preds = %true_block64, %false_block59
  %.363 = phi float [ %134, %true_block64 ], [ %.262, %false_block59 ]
  %.3 = phi float [ %135, %true_block64 ], [ %.2, %false_block59 ]
  %136 = fcmp reassoc ninf nsz ogt float %.3, 0.000000e+00
  br i1 %136, label %true_block70, label %false_block71

true_block70:                                     ; preds = %after_if66
  %137 = fdiv reassoc ninf nsz float %.363, %.3
  br label %after_if72

false_block71:                                    ; preds = %after_if66
  %138 = getelementptr i8, ptr %34, i64 8
  %139 = load ptr, ptr %138, align 8
  %140 = getelementptr i8, ptr %34, i64 4
  %141 = load i32, ptr %140, align 4
  %142 = shl i32 %141, 1
  %143 = shl i32 %25, 1
  %144 = sub i32 %142, %143
  %145 = mul i32 %144, %32
  %146 = add i32 %lsr.iv, %145
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %139, i64 %147
  %149 = load float, ptr %148, align 4
  %150 = getelementptr inbounds nuw i8, ptr %23, i64 8
  %151 = load float, ptr %150, align 4
  %152 = fsub reassoc ninf nsz float %149, %151
  %153 = getelementptr inbounds nuw i8, ptr %23, i64 12
  %154 = load float, ptr %153, align 4
  %155 = fmul reassoc ninf nsz float %152, %154
  %156 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %155, float 0.000000e+00)
  %157 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %156, float 1.000000e+00)
  br label %after_if72

after_if72:                                       ; preds = %false_block71, %true_block70
  %.sink = phi float [ %157, %false_block71 ], [ %137, %true_block70 ]
  %158 = getelementptr i8, ptr %34, i64 24
  %159 = load ptr, ptr %158, align 8
  %160 = getelementptr i8, ptr %34, i64 20
  %161 = load i32, ptr %160, align 4
  %162 = sub i32 %161, %25
  %163 = mul i32 %162, %32
  %164 = add i32 %.06473, %163
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %159, i64 %165
  store float %.sink, ptr %166, align 4
  %167 = add nsw i32 %.06473, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %167
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
attributes #1 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
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
