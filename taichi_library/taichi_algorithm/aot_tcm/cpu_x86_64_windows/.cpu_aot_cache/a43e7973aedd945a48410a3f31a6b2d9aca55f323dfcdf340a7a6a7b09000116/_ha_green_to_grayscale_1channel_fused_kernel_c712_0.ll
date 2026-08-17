; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_ha_green_to_grayscale_1channel_fused_kernel_c712_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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
  %20 = load ptr, ptr %5, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 20
  store i32 %19, ptr %23, align 4
  %24 = tail call i32 @llvm.smax.i32(i32 %19, i32 0)
  %25 = load ptr, ptr %context, align 8
  %26 = getelementptr i8, ptr %25, i64 60
  %27 = load i32, ptr %26, align 4
  %28 = load ptr, ptr %5, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 16
  store i32 %27, ptr %31, align 4
  %32 = tail call i32 @llvm.smax.i32(i32 %27, i32 0)
  %33 = load ptr, ptr %5, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 4
  store i32 %32, ptr %36, align 4
  %37 = mul i32 %32, %24
  %38 = load ptr, ptr %5, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 32872
  %40 = load ptr, ptr %39, align 8
  store i32 %37, ptr %40, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @_ha_green_to_grayscale_1channel_fused_kernel_c712_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
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
  br i1 %28, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.03766 = phi i32 [ %181, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.03766, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.03766
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.03766, %35
  %39 = and i1 %37, %38
  %.neg40 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg40
  %41 = mul i32 %40, %33
  %42 = mul i32 %33, -1
  %43 = mul i32 %42, %40
  %44 = add i32 %.03766, %43
  %45 = sdiv i32 %40, 2
  %46 = icmp slt i32 %40, 0
  %47 = shl nsw i32 %45, 1
  %48 = icmp ne i32 %47, %40
  %49 = and i1 %46, %48
  %.neg41 = sext i1 %49 to i32
  %50 = add nsw i32 %45, %.neg41
  %51 = shl i32 %50, 1
  %52 = sdiv i32 %44, 2
  %53 = icmp slt i32 %44, 0
  %54 = shl nsw i32 %52, 1
  %55 = icmp ne i32 %44, %54
  %56 = and i1 %53, %55
  %.neg42 = sext i1 %56 to i32
  %57 = add nsw i32 %52, %.neg42
  %58 = shl i32 %57, 1
  %.not = icmp eq i32 %40, %51
  %.not43 = icmp eq i32 %44, %58
  %59 = select i1 %.not43, i32 %21, i32 %23
  %60 = select i1 %.not43, i32 %25, i32 %27
  %61 = select i1 %.not, i32 %59, i32 %60
  switch i32 %61, label %false_block2 [
    i32 3, label %true_block1
    i32 1, label %true_block1
  ]

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body, %for_loop_body
  %.not54 = icmp eq i32 %61, 1
  %62 = load ptr, ptr %0, align 8
  %63 = getelementptr i8, ptr %62, i64 8
  %64 = load ptr, ptr %63, align 8
  %65 = getelementptr i8, ptr %62, i64 4
  %66 = load i32, ptr %65, align 4
  %67 = sub i32 %66, %33
  %68 = mul i32 %67, %40
  %69 = add i32 %.03766, %68
  %70 = sext i32 %69 to i64
  %71 = getelementptr float, ptr %64, i64 %70
  %72 = load float, ptr %71, align 4
  %73 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %74 = load float, ptr %73, align 4
  %75 = fsub reassoc ninf nsz float %72, %74
  %76 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %77 = load float, ptr %76, align 4
  %78 = fmul reassoc ninf nsz float %75, %77
  %79 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %78, float 0.000000e+00)
  %80 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %79, float 1.000000e+00)
  %.035.in.v = select i1 %.not54, i64 36, i64 44
  %.035.in = getelementptr i8, ptr %62, i64 %.035.in.v
  %.035 = load float, ptr %.035.in, align 4
  %81 = fmul reassoc ninf nsz float %80, %.035
  br label %after_if3

false_block2:                                     ; preds = %for_loop_body
  %82 = add i32 %44, -1
  %83 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %84 = getelementptr inbounds nuw i8, ptr %31, i64 16
  %85 = load i32, ptr %84, align 4
  %86 = add i32 %85, -1
  %87 = add i32 %44, 1
  %88 = tail call i32 @llvm.smin.i32(i32 %86, i32 %87)
  %89 = add i32 %40, -1
  %90 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %91 = getelementptr inbounds nuw i8, ptr %31, i64 20
  %92 = load i32, ptr %91, align 4
  %93 = add i32 %92, -1
  %94 = add i32 %40, 1
  %95 = tail call i32 @llvm.smin.i32(i32 %93, i32 %94)
  %96 = load ptr, ptr %0, align 8
  %97 = getelementptr i8, ptr %96, i64 8
  %98 = load ptr, ptr %97, align 8
  %99 = getelementptr i8, ptr %96, i64 4
  %100 = load i32, ptr %99, align 4
  %101 = mul i32 %100, %40
  %102 = add i32 %101, %83
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, ptr %98, i64 %103
  %105 = load float, ptr %104, align 4
  %106 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %107 = load float, ptr %106, align 4
  %108 = fsub reassoc ninf nsz float %105, %107
  %109 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %110 = load float, ptr %109, align 4
  %111 = fmul reassoc ninf nsz float %108, %110
  %112 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %111, float 0.000000e+00)
  %113 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %112, float 1.000000e+00)
  %114 = add i32 %101, %88
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %98, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = fsub reassoc ninf nsz float %117, %107
  %119 = fmul reassoc ninf nsz float %118, %110
  %120 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %119, float 0.000000e+00)
  %121 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %120, float 1.000000e+00)
  %122 = mul i32 %100, %90
  %123 = sub i32 %122, %41
  %124 = add i32 %.03766, %123
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %98, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = fsub reassoc ninf nsz float %127, %107
  %129 = fmul reassoc ninf nsz float %128, %110
  %130 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %129, float 0.000000e+00)
  %131 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %130, float 1.000000e+00)
  %132 = mul i32 %100, %95
  %133 = sub i32 %132, %41
  %134 = add i32 %.03766, %133
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, ptr %98, i64 %135
  %137 = load float, ptr %136, align 4
  %138 = fsub reassoc ninf nsz float %137, %107
  %139 = fmul reassoc ninf nsz float %138, %110
  %140 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %139, float 0.000000e+00)
  %141 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %140, float 1.000000e+00)
  %142 = getelementptr i8, ptr %96, i64 36
  %143 = load float, ptr %142, align 4
  %144 = getelementptr i8, ptr %96, i64 44
  %145 = load float, ptr %144, align 4
  %146 = and i32 %83, 1
  %.not45 = icmp eq i32 %146, 0
  %. = select i1 %.not45, i32 %21, i32 %23
  %.55 = select i1 %.not45, i32 %25, i32 %27
  %.034 = select i1 %.not, i32 %., i32 %.55
  %.not46 = icmp eq i32 %.034, 1
  %.56 = select i1 %.not46, float %143, float %145
  %147 = sdiv i32 %88, 2
  %148 = icmp slt i32 %88, 0
  %149 = shl nsw i32 %147, 1
  %150 = icmp ne i32 %149, %88
  %151 = and i1 %148, %150
  %.neg47 = sext i1 %151 to i32
  %152 = add nsw i32 %147, %.neg47
  %153 = shl i32 %152, 1
  %.not48 = icmp eq i32 %88, %153
  %.57 = select i1 %.not48, i32 %21, i32 %23
  %.58 = select i1 %.not48, i32 %25, i32 %27
  %.030 = select i1 %.not, i32 %.57, i32 %.58
  %.not49 = icmp eq i32 %.030, 1
  %.59 = select i1 %.not49, float %143, float %145
  %154 = and i32 %90, 1
  %155 = icmp eq i32 %154, 0
  %.026 = select i1 %155, i32 %59, i32 %60
  %.not51 = icmp eq i32 %.026, 1
  %.62 = select i1 %.not51, float %143, float %145
  %156 = sdiv i32 %95, 2
  %157 = icmp slt i32 %95, 0
  %158 = shl nsw i32 %156, 1
  %159 = icmp ne i32 %158, %95
  %160 = and i1 %157, %159
  %.neg52 = sext i1 %160 to i32
  %161 = add nsw i32 %156, %.neg52
  %162 = shl i32 %161, 1
  %163 = icmp eq i32 %95, %162
  %.022 = select i1 %163, i32 %59, i32 %60
  %.not53 = icmp eq i32 %.022, 1
  %.65 = select i1 %.not53, float %143, float %145
  %164 = fmul reassoc ninf nsz float %.56, %113
  %165 = fmul reassoc ninf nsz float %.59, %121
  %166 = fmul reassoc ninf nsz float %131, %.62
  %167 = fmul reassoc ninf nsz float %141, %.65
  %168 = fadd reassoc ninf nsz float %166, %164
  %169 = fadd reassoc ninf nsz float %168, %165
  %170 = fadd reassoc ninf nsz float %169, %167
  %171 = fmul reassoc ninf nsz float %170, 2.500000e-01
  br label %after_if3

after_if3:                                        ; preds = %false_block2, %true_block1
  %.sink76 = phi ptr [ %96, %false_block2 ], [ %62, %true_block1 ]
  %.sink = phi float [ %171, %false_block2 ], [ %81, %true_block1 ]
  %172 = getelementptr i8, ptr %.sink76, i64 24
  %173 = load ptr, ptr %172, align 8
  %174 = getelementptr i8, ptr %.sink76, i64 20
  %175 = load i32, ptr %174, align 4
  %176 = sub i32 %175, %33
  %177 = mul i32 %176, %40
  %178 = add i32 %.03766, %177
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, ptr %173, i64 %179
  store float %.sink, ptr %180, align 4
  %181 = add nsw i32 %.03766, 1
  %exitcond.not = icmp eq i32 %18, %181
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
