; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @robust_splat_gray_kernel_c716_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 136
  %2 = load float, ptr %1, align 4
  %3 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2, float 0x3F1A36E2E0000000)
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fdiv reassoc ninf nsz float 5.000000e-01, %4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 8
  store float %5, ptr %10, align 4
  %11 = load ptr, ptr %context, align 8
  %12 = getelementptr i8, ptr %11, i64 96
  %13 = load i32, ptr %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = getelementptr i8, ptr %11, i64 100
  %16 = load i32, ptr %15, align 4
  %17 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %18 = load ptr, ptr %6, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 4
  store i32 %17, ptr %21, align 4
  %22 = mul i32 %17, %14
  %23 = load ptr, ptr %6, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 32872
  %25 = load ptr, ptr %24, align 8
  store i32 %22, ptr %25, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @robust_splat_gray_kernel_c716_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 128
  %21 = load i32, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = sitofp i32 %21 to float
  %24 = getelementptr i8, ptr %19, i64 104
  %25 = getelementptr i8, ptr %19, i64 100
  %26 = getelementptr i8, ptr %19, i64 120
  %27 = getelementptr i8, ptr %19, i64 116
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01937 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %98, %after_for3 ]
  %28 = load ptr, ptr %3, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 4
  %32 = load i32, ptr %31, align 4
  %33 = sdiv i32 %.01937, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.01937
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %34, %.01937
  %38 = and i1 %36, %37
  %.neg25 = sext i1 %38 to i32
  %39 = add i32 %33, %.neg25
  %40 = mul i32 %39, %32
  %41 = sub i32 %.01937, %40
  %42 = load ptr, ptr %0, align 8
  %43 = load i32, ptr %42, align 4
  %44 = tail call i32 @llvm.smax.i32(i32 %43, i32 0)
  %45 = mul i32 %44, 49
  %46 = icmp sgt i32 %45, 0
  br i1 %46, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %47 = sdiv i32 %41, %21
  %48 = mul i32 %47, %21
  %49 = icmp ne i32 %48, %41
  %50 = icmp ne i32 %.01937, %40
  %51 = xor i32 %41, %21
  %52 = icmp slt i32 %51, 0
  %53 = and i1 %50, %52
  %54 = and i1 %49, %53
  %.neg27 = sext i1 %54 to i32
  %55 = sdiv i32 %39, %21
  %56 = mul i32 %55, %21
  %57 = icmp ne i32 %56, %39
  %58 = xor i32 %39, %21
  %59 = icmp slt i32 %58, 0
  %60 = and i1 %57, %59
  %.neg26 = sext i1 %60 to i32
  %61 = add i32 %55, -3
  %62 = add i32 %61, %.neg26
  %63 = sitofp i32 %39 to float
  %64 = sitofp i32 %41 to float
  %65 = add i32 %47, -3
  %66 = add i32 %65, %.neg27
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %after_if13, %for_loop_body1.lr.ph
  %67 = phi ptr [ %42, %for_loop_body1.lr.ph ], [ %157, %after_if13 ]
  %.01535 = phi i32 [ 0, %for_loop_body1.lr.ph ], [ %158, %after_if13 ]
  %.01634 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.1, %after_if13 ]
  %.01733 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.118, %after_if13 ]
  %68 = udiv i32 %.01535, 49
  %69 = mul nuw nsw i32 %68, 49
  %70 = sub i32 %66, %69
  %71 = mul nsw i32 %68, -49
  %72 = add i32 %.01535, %71
  %73 = sdiv i32 %72, 7
  %74 = icmp slt i32 %72, 0
  %75 = mul nsw i32 %73, 7
  %76 = icmp ne i32 %72, %75
  %77 = and i1 %74, %76
  %.neg30 = sext i1 %77 to i32
  %78 = add nsw i32 %73, %.neg30
  %.neg31 = mul i32 %78, -7
  %79 = add i32 %62, %78
  %80 = add i32 %.01535, %.neg31
  %81 = add i32 %80, %70
  %82 = icmp sgt i32 %79, -1
  br i1 %82, label %true_block, label %after_if13

after_for3.loopexit:                              ; preds = %after_if13
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.017.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.118, %after_for3.loopexit ]
  %.016.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.1, %after_for3.loopexit ]
  %83 = fcmp reassoc ninf nsz ogt float %.016.lcssa, 0x3E45798EE0000000
  %84 = fdiv reassoc ninf nsz float %.017.lcssa, %.016.lcssa
  %85 = select reassoc ninf nsz i1 %83, float %84, float 0.000000e+00
  %86 = load ptr, ptr %24, align 8
  %87 = load i32, ptr %25, align 4
  %88 = mul i32 %87, %39
  %89 = add i32 %88, %41
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %86, i64 %90
  store float %85, ptr %91, align 4
  %92 = load ptr, ptr %26, align 8
  %93 = load i32, ptr %27, align 4
  %94 = mul i32 %93, %39
  %95 = add i32 %94, %41
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %92, i64 %96
  store float %.016.lcssa, ptr %97, align 4
  %98 = add nsw i32 %.01937, 1
  %exitcond38.not = icmp eq i32 %98, %18
  br i1 %exitcond38.not, label %after_for.loopexit, label %for_loop_body

true_block:                                       ; preds = %for_loop_body1
  %99 = getelementptr i8, ptr %67, i64 4
  %100 = load i32, ptr %99, align 4
  %101 = icmp slt i32 %79, %100
  %102 = icmp sgt i32 %81, -1
  %or.cond = select i1 %101, i1 %102, i1 false
  br i1 %or.cond, label %true_block8, label %after_if13

true_block8:                                      ; preds = %true_block
  %103 = getelementptr i8, ptr %67, i64 8
  %104 = load i32, ptr %103, align 4
  %105 = icmp slt i32 %81, %104
  br i1 %105, label %true_block11, label %after_if13

true_block11:                                     ; preds = %true_block8
  %106 = uitofp nneg i32 %79 to float
  %107 = getelementptr i8, ptr %67, i64 64
  %108 = load ptr, ptr %107, align 8
  %109 = getelementptr i8, ptr %67, i64 52
  %110 = load i32, ptr %109, align 4
  %111 = getelementptr i8, ptr %67, i64 56
  %112 = load i32, ptr %111, align 4
  %113 = mul i32 %73, -7
  %114 = mul nsw i32 %.neg30, 7
  %115 = sub i32 %113, %114
  %116 = add i32 %62, %73
  %117 = mul i32 %110, %68
  %118 = add i32 %116, %117
  %119 = add i32 %118, %.neg30
  %120 = mul i32 %112, %119
  %121 = add i32 %.01535, %120
  %122 = add i32 %121, %115
  %123 = add i32 %122, %70
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %108, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = fadd reassoc ninf nsz float %126, %106
  %128 = fmul reassoc ninf nsz float %127, %23
  %129 = uitofp nneg i32 %81 to float
  %130 = getelementptr i8, ptr %67, i64 88
  %131 = load ptr, ptr %130, align 8
  %132 = getelementptr i8, ptr %67, i64 76
  %133 = load i32, ptr %132, align 4
  %134 = getelementptr i8, ptr %67, i64 80
  %135 = load i32, ptr %134, align 4
  %136 = mul i32 %133, %68
  %137 = add i32 %116, %136
  %138 = add i32 %137, %.neg30
  %139 = mul i32 %135, %138
  %140 = add i32 %.01535, %139
  %141 = add i32 %140, %115
  %142 = add i32 %141, %70
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %131, i64 %143
  %145 = load float, ptr %144, align 4
  %146 = fadd reassoc ninf nsz float %145, %129
  %147 = fmul reassoc ninf nsz float %146, %23
  %148 = fsub reassoc ninf nsz float %63, %128
  %149 = fmul reassoc ninf nsz float %148, %148
  %150 = fsub reassoc ninf nsz float %64, %147
  %151 = fmul reassoc ninf nsz float %150, %150
  %152 = fadd reassoc ninf nsz float %151, %149
  %153 = getelementptr i8, ptr %67, i64 132
  %154 = load float, ptr %153, align 4
  %155 = fmul reassoc ninf nsz float %154, %154
  %156 = fcmp reassoc ninf nsz ugt float %152, %155
  br i1 %156, label %after_if13, label %true_block14

after_if13:                                       ; preds = %true_block14, %true_block11, %true_block8, %true_block, %for_loop_body1
  %157 = phi ptr [ %183, %true_block14 ], [ %67, %true_block11 ], [ %67, %true_block8 ], [ %67, %for_loop_body1 ], [ %67, %true_block ]
  %.118 = phi float [ %201, %true_block14 ], [ %.01733, %true_block11 ], [ %.01733, %true_block8 ], [ %.01733, %for_loop_body1 ], [ %.01733, %true_block ]
  %.1 = phi float [ %202, %true_block14 ], [ %.01634, %true_block11 ], [ %.01634, %true_block8 ], [ %.01634, %for_loop_body1 ], [ %.01634, %true_block ]
  %158 = add nuw nsw i32 %.01535, 1
  %exitcond.not = icmp eq i32 %45, %158
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1

true_block14:                                     ; preds = %true_block11
  %159 = getelementptr i8, ptr %67, i64 40
  %160 = load ptr, ptr %159, align 8
  %161 = getelementptr i8, ptr %67, i64 28
  %162 = load i32, ptr %161, align 4
  %163 = getelementptr i8, ptr %67, i64 32
  %164 = load i32, ptr %163, align 4
  %165 = mul i32 %162, %68
  %166 = add i32 %116, %165
  %167 = add i32 %166, %.neg30
  %168 = mul i32 %164, %167
  %169 = add i32 %.01535, %168
  %170 = add i32 %169, %115
  %171 = add i32 %170, %70
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %160, i64 %172
  %174 = load float, ptr %173, align 4
  %neg = fneg reassoc ninf nsz float %152
  %175 = load ptr, ptr %3, align 8
  %176 = getelementptr inbounds nuw i8, ptr %175, i64 32872
  %177 = load ptr, ptr %176, align 8
  %178 = getelementptr inbounds nuw i8, ptr %177, i64 8
  %179 = load float, ptr %178, align 4
  %180 = fmul reassoc ninf nsz float %179, %neg
  %181 = tail call noundef float @expf(float noundef %180) #8
  %182 = fmul reassoc ninf nsz float %181, %174
  %183 = load ptr, ptr %0, align 8
  %184 = getelementptr i8, ptr %183, i64 16
  %185 = load ptr, ptr %184, align 8
  %186 = getelementptr i8, ptr %183, i64 4
  %187 = load i32, ptr %186, align 4
  %188 = getelementptr i8, ptr %183, i64 8
  %189 = load i32, ptr %188, align 4
  %190 = mul i32 %187, %68
  %191 = add i32 %116, %190
  %192 = add i32 %191, %.neg30
  %193 = mul i32 %189, %192
  %194 = add i32 %.01535, %193
  %195 = add i32 %194, %115
  %196 = add i32 %195, %70
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %185, i64 %197
  %199 = load float, ptr %198, align 4
  %200 = fmul reassoc ninf nsz float %199, %182
  %201 = fadd reassoc ninf nsz float %200, %.01733
  %202 = fadd reassoc ninf nsz float %182, %.01634
  br label %after_if13
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

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
attributes #1 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
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
