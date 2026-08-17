; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_ha_green_half_res_fused_kernel_c714_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_ha_green_half_res_fused_kernel_c714_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 64
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 68
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 72
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 76
  %27 = load i32, ptr %26, align 4
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %.not = icmp eq i32 %21, 1
  %.025.in.v = select i1 %.not, i64 36, i64 44
  %.not42 = icmp eq i32 %23, 1
  %.023.in.v = select i1 %.not42, i64 36, i64 44
  %.not43 = icmp eq i32 %25, 1
  %.021.in.v = select i1 %.not43, i64 36, i64 44
  %.not44 = icmp eq i32 %27, 1
  %.0.in.v = select i1 %.not44, i64 36, i64 44
  %29 = shl i32 %16, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if36, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if36 ]
  %.03248 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %173, %after_if36 ]
  %30 = load ptr, ptr %3, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 32872
  %32 = load ptr, ptr %31, align 8
  %33 = getelementptr inbounds nuw i8, ptr %32, i64 4
  %34 = load i32, ptr %33, align 4
  %35 = sdiv i32 %.03248, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.03248
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.03248, %36
  %40 = and i1 %38, %39
  %.neg41 = sext i1 %40 to i32
  %41 = add i32 %35, %.neg41
  %42 = shl i32 %41, 1
  switch i32 %21, label %after_if3 [
    i32 3, label %true_block1
    i32 1, label %true_block1
  ]

after_for.loopexit:                               ; preds = %after_if36
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body, %for_loop_body
  %43 = load ptr, ptr %0, align 8
  %44 = getelementptr i8, ptr %43, i64 8
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr i8, ptr %43, i64 4
  %47 = load i32, ptr %46, align 4
  %48 = shl i32 %47, 1
  %49 = shl i32 %34, 1
  %50 = sub i32 %48, %49
  %51 = mul i32 %50, %41
  %52 = add i32 %lsr.iv, %51
  %53 = sext i32 %52 to i64
  %54 = getelementptr float, ptr %45, i64 %53
  %55 = load float, ptr %54, align 4
  %56 = getelementptr inbounds nuw i8, ptr %32, i64 8
  %57 = load float, ptr %56, align 4
  %58 = fsub reassoc ninf nsz float %55, %57
  %59 = getelementptr inbounds nuw i8, ptr %32, i64 12
  %60 = load float, ptr %59, align 4
  %61 = fmul reassoc ninf nsz float %58, %60
  %62 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %61, float 0.000000e+00)
  %63 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %62, float 1.000000e+00)
  %.025.in = getelementptr i8, ptr %43, i64 %.025.in.v
  %.025 = load float, ptr %.025.in, align 4
  %64 = fmul reassoc ninf nsz float %63, %.025
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %for_loop_body
  %.028 = phi float [ %64, %true_block1 ], [ 0.000000e+00, %for_loop_body ]
  %.027 = phi float [ 1.000000e+00, %true_block1 ], [ 0.000000e+00, %for_loop_body ]
  switch i32 %23, label %after_if12 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

true_block10:                                     ; preds = %after_if3, %after_if3
  %65 = load ptr, ptr %0, align 8
  %66 = getelementptr i8, ptr %65, i64 8
  %67 = load ptr, ptr %66, align 8
  %68 = getelementptr i8, ptr %65, i64 4
  %69 = load i32, ptr %68, align 4
  %70 = shl i32 %69, 1
  %71 = shl i32 %34, 1
  %72 = sub i32 %70, %71
  %73 = mul i32 %72, %41
  %74 = add i32 %lsr.iv, %73
  %75 = add i32 %74, 1
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, ptr %67, i64 %76
  %78 = load float, ptr %77, align 4
  %79 = getelementptr inbounds nuw i8, ptr %32, i64 8
  %80 = load float, ptr %79, align 4
  %81 = fsub reassoc ninf nsz float %78, %80
  %82 = getelementptr inbounds nuw i8, ptr %32, i64 12
  %83 = load float, ptr %82, align 4
  %84 = fmul reassoc ninf nsz float %81, %83
  %85 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %84, float 0.000000e+00)
  %86 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %85, float 1.000000e+00)
  %.023.in = getelementptr i8, ptr %65, i64 %.023.in.v
  %.023 = load float, ptr %.023.in, align 4
  %87 = fmul reassoc ninf nsz float %86, %.023
  %88 = fadd reassoc ninf nsz float %87, %.028
  %89 = fadd reassoc ninf nsz float %.027, 1.000000e+00
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if3
  %.129 = phi float [ %88, %true_block10 ], [ %.028, %after_if3 ]
  %.1 = phi float [ %89, %true_block10 ], [ %.027, %after_if3 ]
  %90 = or disjoint i32 %42, 1
  switch i32 %25, label %after_if21 [
    i32 3, label %true_block19
    i32 1, label %true_block19
  ]

true_block19:                                     ; preds = %after_if12, %after_if12
  %91 = load ptr, ptr %0, align 8
  %92 = getelementptr i8, ptr %91, i64 8
  %93 = load ptr, ptr %92, align 8
  %94 = getelementptr i8, ptr %91, i64 4
  %95 = load i32, ptr %94, align 4
  %96 = mul i32 %95, %90
  %97 = shl i32 %34, 1
  %98 = mul i32 %97, %41
  %99 = sub i32 %96, %98
  %100 = add i32 %lsr.iv, %99
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %93, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = getelementptr inbounds nuw i8, ptr %32, i64 8
  %105 = load float, ptr %104, align 4
  %106 = fsub reassoc ninf nsz float %103, %105
  %107 = getelementptr inbounds nuw i8, ptr %32, i64 12
  %108 = load float, ptr %107, align 4
  %109 = fmul reassoc ninf nsz float %106, %108
  %110 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %109, float 0.000000e+00)
  %111 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %110, float 1.000000e+00)
  %.021.in = getelementptr i8, ptr %91, i64 %.021.in.v
  %.021 = load float, ptr %.021.in, align 4
  %112 = fmul reassoc ninf nsz float %111, %.021
  %113 = fadd reassoc ninf nsz float %112, %.129
  %114 = fadd reassoc ninf nsz float %.1, 1.000000e+00
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if12
  %.230 = phi float [ %113, %true_block19 ], [ %.129, %after_if12 ]
  %.2 = phi float [ %114, %true_block19 ], [ %.1, %after_if12 ]
  switch i32 %27, label %after_if30 [
    i32 3, label %true_block28
    i32 1, label %true_block28
  ]

true_block28:                                     ; preds = %after_if21, %after_if21
  %115 = load ptr, ptr %0, align 8
  %116 = getelementptr i8, ptr %115, i64 8
  %117 = load ptr, ptr %116, align 8
  %118 = getelementptr i8, ptr %115, i64 4
  %119 = load i32, ptr %118, align 4
  %120 = mul i32 %119, %90
  %121 = shl i32 %34, 1
  %122 = mul i32 %121, %41
  %123 = sub i32 %120, %122
  %124 = add i32 %lsr.iv, %123
  %125 = add i32 %124, 1
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %117, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = getelementptr inbounds nuw i8, ptr %32, i64 8
  %130 = load float, ptr %129, align 4
  %131 = fsub reassoc ninf nsz float %128, %130
  %132 = getelementptr inbounds nuw i8, ptr %32, i64 12
  %133 = load float, ptr %132, align 4
  %134 = fmul reassoc ninf nsz float %131, %133
  %135 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %134, float 0.000000e+00)
  %136 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %135, float 1.000000e+00)
  %.0.in = getelementptr i8, ptr %115, i64 %.0.in.v
  %.0 = load float, ptr %.0.in, align 4
  %137 = fmul reassoc ninf nsz float %136, %.0
  %138 = fadd reassoc ninf nsz float %137, %.230
  %139 = fadd reassoc ninf nsz float %.2, 1.000000e+00
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if21
  %.331 = phi float [ %138, %true_block28 ], [ %.230, %after_if21 ]
  %.3 = phi float [ %139, %true_block28 ], [ %.2, %after_if21 ]
  %140 = fcmp reassoc ninf nsz ogt float %.3, 0.000000e+00
  br i1 %140, label %true_block34, label %false_block35

true_block34:                                     ; preds = %after_if30
  %141 = fdiv reassoc ninf nsz float %.331, %.3
  %142 = load ptr, ptr %0, align 8
  br label %after_if36

false_block35:                                    ; preds = %after_if30
  %143 = load ptr, ptr %0, align 8
  %144 = getelementptr i8, ptr %143, i64 8
  %145 = load ptr, ptr %144, align 8
  %146 = getelementptr i8, ptr %143, i64 4
  %147 = load i32, ptr %146, align 4
  %148 = shl i32 %147, 1
  %149 = shl i32 %34, 1
  %150 = sub i32 %148, %149
  %151 = mul i32 %150, %41
  %152 = add i32 %lsr.iv, %151
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %145, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = getelementptr inbounds nuw i8, ptr %32, i64 8
  %157 = load float, ptr %156, align 4
  %158 = fsub reassoc ninf nsz float %155, %157
  %159 = getelementptr inbounds nuw i8, ptr %32, i64 12
  %160 = load float, ptr %159, align 4
  %161 = fmul reassoc ninf nsz float %158, %160
  %162 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %161, float 0.000000e+00)
  %163 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %162, float 1.000000e+00)
  br label %after_if36

after_if36:                                       ; preds = %false_block35, %true_block34
  %.sink58 = phi ptr [ %143, %false_block35 ], [ %142, %true_block34 ]
  %.sink = phi float [ %163, %false_block35 ], [ %141, %true_block34 ]
  %164 = getelementptr i8, ptr %.sink58, i64 24
  %165 = load ptr, ptr %164, align 8
  %166 = getelementptr i8, ptr %.sink58, i64 20
  %167 = load i32, ptr %166, align 4
  %168 = sub i32 %167, %34
  %169 = mul i32 %168, %41
  %170 = add i32 %.03248, %169
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %165, i64 %171
  store float %.sink, ptr %172, align 4
  %173 = add nsw i32 %.03248, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %173
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

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
