; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @robust_splat_gray_offset_kernel_c100_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @robust_splat_gray_offset_kernel_c100_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 140
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 144
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 128
  %25 = load i32, ptr %24, align 4
  %26 = icmp slt i32 %16, %18
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = sitofp i32 %25 to float
  %28 = getelementptr i8, ptr %19, i64 104
  %29 = getelementptr i8, ptr %19, i64 100
  %30 = getelementptr i8, ptr %19, i64 120
  %31 = getelementptr i8, ptr %19, i64 116
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01937 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %102, %after_for3 ]
  %32 = load ptr, ptr %3, align 8
  %33 = getelementptr inbounds nuw i8, ptr %32, i64 32872
  %34 = load ptr, ptr %33, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 4
  %36 = load i32, ptr %35, align 4
  %37 = sdiv i32 %.01937, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.01937
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %38, %.01937
  %42 = and i1 %40, %41
  %.neg25 = sext i1 %42 to i32
  %43 = add i32 %37, %.neg25
  %44 = mul i32 %43, %36
  %45 = sub i32 %.01937, %44
  %46 = load ptr, ptr %0, align 8
  %47 = load i32, ptr %46, align 4
  %48 = tail call i32 @llvm.smax.i32(i32 %47, i32 0)
  %49 = mul i32 %48, 49
  %50 = icmp sgt i32 %49, 0
  br i1 %50, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %51 = add i32 %45, %23
  %52 = sdiv i32 %51, %25
  %53 = mul i32 %52, %25
  %54 = icmp ne i32 %53, %51
  %55 = xor i32 %51, %25
  %56 = icmp slt i32 %55, 0
  %57 = and i1 %54, %56
  %.neg27 = sext i1 %57 to i32
  %58 = add i32 %43, %21
  %59 = sdiv i32 %58, %25
  %60 = mul i32 %59, %25
  %61 = icmp ne i32 %60, %58
  %62 = xor i32 %58, %25
  %63 = icmp slt i32 %62, 0
  %64 = and i1 %61, %63
  %.neg26 = sext i1 %64 to i32
  %65 = add i32 %59, -3
  %66 = add i32 %65, %.neg26
  %67 = sitofp i32 %58 to float
  %68 = sitofp i32 %51 to float
  %69 = add i32 %52, -3
  %70 = add i32 %69, %.neg27
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %after_if13, %for_loop_body1.lr.ph
  %71 = phi ptr [ %46, %for_loop_body1.lr.ph ], [ %161, %after_if13 ]
  %.01535 = phi i32 [ 0, %for_loop_body1.lr.ph ], [ %162, %after_if13 ]
  %.01634 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.1, %after_if13 ]
  %.01733 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.118, %after_if13 ]
  %72 = udiv i32 %.01535, 49
  %73 = mul nuw nsw i32 %72, 49
  %74 = sub i32 %70, %73
  %75 = mul nsw i32 %72, -49
  %76 = add i32 %.01535, %75
  %77 = sdiv i32 %76, 7
  %78 = icmp slt i32 %76, 0
  %79 = mul nsw i32 %77, 7
  %80 = icmp ne i32 %76, %79
  %81 = and i1 %78, %80
  %.neg30 = sext i1 %81 to i32
  %82 = add nsw i32 %77, %.neg30
  %.neg31 = mul i32 %82, -7
  %83 = add i32 %66, %82
  %84 = add i32 %.01535, %.neg31
  %85 = add i32 %84, %74
  %86 = icmp sgt i32 %83, -1
  br i1 %86, label %true_block, label %after_if13

after_for3.loopexit:                              ; preds = %after_if13
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.017.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.118, %after_for3.loopexit ]
  %.016.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.1, %after_for3.loopexit ]
  %87 = fcmp reassoc ninf nsz ogt float %.016.lcssa, 0x3E45798EE0000000
  %88 = fdiv reassoc ninf nsz float %.017.lcssa, %.016.lcssa
  %89 = select reassoc ninf nsz i1 %87, float %88, float 0.000000e+00
  %90 = load ptr, ptr %28, align 8
  %91 = load i32, ptr %29, align 4
  %92 = mul i32 %91, %43
  %93 = add i32 %92, %45
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %90, i64 %94
  store float %89, ptr %95, align 4
  %96 = load ptr, ptr %30, align 8
  %97 = load i32, ptr %31, align 4
  %98 = mul i32 %97, %43
  %99 = add i32 %98, %45
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %96, i64 %100
  store float %.016.lcssa, ptr %101, align 4
  %102 = add nsw i32 %.01937, 1
  %exitcond38.not = icmp eq i32 %102, %18
  br i1 %exitcond38.not, label %after_for.loopexit, label %for_loop_body

true_block:                                       ; preds = %for_loop_body1
  %103 = getelementptr i8, ptr %71, i64 4
  %104 = load i32, ptr %103, align 4
  %105 = icmp slt i32 %83, %104
  %106 = icmp sgt i32 %85, -1
  %or.cond = select i1 %105, i1 %106, i1 false
  br i1 %or.cond, label %true_block8, label %after_if13

true_block8:                                      ; preds = %true_block
  %107 = getelementptr i8, ptr %71, i64 8
  %108 = load i32, ptr %107, align 4
  %109 = icmp slt i32 %85, %108
  br i1 %109, label %true_block11, label %after_if13

true_block11:                                     ; preds = %true_block8
  %110 = uitofp nneg i32 %83 to float
  %111 = getelementptr i8, ptr %71, i64 64
  %112 = load ptr, ptr %111, align 8
  %113 = getelementptr i8, ptr %71, i64 52
  %114 = load i32, ptr %113, align 4
  %115 = getelementptr i8, ptr %71, i64 56
  %116 = load i32, ptr %115, align 4
  %117 = mul i32 %77, -7
  %118 = mul nsw i32 %.neg30, 7
  %119 = sub i32 %117, %118
  %120 = add i32 %66, %77
  %121 = mul i32 %114, %72
  %122 = add i32 %120, %121
  %123 = add i32 %122, %.neg30
  %124 = mul i32 %116, %123
  %125 = add i32 %.01535, %124
  %126 = add i32 %125, %119
  %127 = add i32 %126, %74
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %112, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = fadd reassoc ninf nsz float %130, %110
  %132 = fmul reassoc ninf nsz float %131, %27
  %133 = uitofp nneg i32 %85 to float
  %134 = getelementptr i8, ptr %71, i64 88
  %135 = load ptr, ptr %134, align 8
  %136 = getelementptr i8, ptr %71, i64 76
  %137 = load i32, ptr %136, align 4
  %138 = getelementptr i8, ptr %71, i64 80
  %139 = load i32, ptr %138, align 4
  %140 = mul i32 %137, %72
  %141 = add i32 %120, %140
  %142 = add i32 %141, %.neg30
  %143 = mul i32 %139, %142
  %144 = add i32 %.01535, %143
  %145 = add i32 %144, %119
  %146 = add i32 %145, %74
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %135, i64 %147
  %149 = load float, ptr %148, align 4
  %150 = fadd reassoc ninf nsz float %149, %133
  %151 = fmul reassoc ninf nsz float %150, %27
  %152 = fsub reassoc ninf nsz float %67, %132
  %153 = fmul reassoc ninf nsz float %152, %152
  %154 = fsub reassoc ninf nsz float %68, %151
  %155 = fmul reassoc ninf nsz float %154, %154
  %156 = fadd reassoc ninf nsz float %155, %153
  %157 = getelementptr i8, ptr %71, i64 132
  %158 = load float, ptr %157, align 4
  %159 = fmul reassoc ninf nsz float %158, %158
  %160 = fcmp reassoc ninf nsz ugt float %156, %159
  br i1 %160, label %after_if13, label %true_block14

after_if13:                                       ; preds = %true_block14, %true_block11, %true_block8, %true_block, %for_loop_body1
  %161 = phi ptr [ %187, %true_block14 ], [ %71, %true_block11 ], [ %71, %true_block8 ], [ %71, %for_loop_body1 ], [ %71, %true_block ]
  %.118 = phi float [ %205, %true_block14 ], [ %.01733, %true_block11 ], [ %.01733, %true_block8 ], [ %.01733, %for_loop_body1 ], [ %.01733, %true_block ]
  %.1 = phi float [ %206, %true_block14 ], [ %.01634, %true_block11 ], [ %.01634, %true_block8 ], [ %.01634, %for_loop_body1 ], [ %.01634, %true_block ]
  %162 = add nuw nsw i32 %.01535, 1
  %exitcond.not = icmp eq i32 %49, %162
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1

true_block14:                                     ; preds = %true_block11
  %163 = getelementptr i8, ptr %71, i64 40
  %164 = load ptr, ptr %163, align 8
  %165 = getelementptr i8, ptr %71, i64 28
  %166 = load i32, ptr %165, align 4
  %167 = getelementptr i8, ptr %71, i64 32
  %168 = load i32, ptr %167, align 4
  %169 = mul i32 %166, %72
  %170 = add i32 %120, %169
  %171 = add i32 %170, %.neg30
  %172 = mul i32 %168, %171
  %173 = add i32 %.01535, %172
  %174 = add i32 %173, %119
  %175 = add i32 %174, %74
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, ptr %164, i64 %176
  %178 = load float, ptr %177, align 4
  %neg = fneg reassoc ninf nsz float %156
  %179 = load ptr, ptr %3, align 8
  %180 = getelementptr inbounds nuw i8, ptr %179, i64 32872
  %181 = load ptr, ptr %180, align 8
  %182 = getelementptr inbounds nuw i8, ptr %181, i64 8
  %183 = load float, ptr %182, align 4
  %184 = fmul reassoc ninf nsz float %183, %neg
  %185 = tail call noundef float @expf(float noundef %184) #8
  %186 = fmul reassoc ninf nsz float %185, %178
  %187 = load ptr, ptr %0, align 8
  %188 = getelementptr i8, ptr %187, i64 16
  %189 = load ptr, ptr %188, align 8
  %190 = getelementptr i8, ptr %187, i64 4
  %191 = load i32, ptr %190, align 4
  %192 = getelementptr i8, ptr %187, i64 8
  %193 = load i32, ptr %192, align 4
  %194 = mul i32 %191, %72
  %195 = add i32 %120, %194
  %196 = add i32 %195, %.neg30
  %197 = mul i32 %193, %196
  %198 = add i32 %.01535, %197
  %199 = add i32 %198, %119
  %200 = add i32 %199, %74
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, ptr %189, i64 %201
  %203 = load float, ptr %202, align 4
  %204 = fmul reassoc ninf nsz float %203, %186
  %205 = fadd reassoc ninf nsz float %204, %.01733
  %206 = fadd reassoc ninf nsz float %186, %.01634
  br label %after_if13
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext, align 8
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
