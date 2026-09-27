; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @splat_rgb_hann_tile_kernel_c104_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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
  %12 = getelementptr i8, ptr %11, i64 112
  %13 = load i32, ptr %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = getelementptr i8, ptr %11, i64 116
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

define void @splat_rgb_hann_tile_kernel_c104_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 148
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 152
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 128
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 140
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 144
  %29 = load i32, ptr %28, align 4
  %30 = icmp slt i32 %16, %18
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = sitofp i32 %25 to float
  %32 = getelementptr i8, ptr %19, i64 80
  %33 = getelementptr i8, ptr %19, i64 76
  %34 = getelementptr i8, ptr %19, i64 120
  %35 = getelementptr i8, ptr %19, i64 116
  %36 = getelementptr i8, ptr %19, i64 104
  %37 = getelementptr i8, ptr %19, i64 92
  %38 = getelementptr i8, ptr %19, i64 96
  %39 = sub i32 0, %29
  %40 = add i32 %39, -3
  %41 = sub i32 -3, %29
  %42 = sub i32 -3, %27
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.02745 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %131, %after_for3 ]
  %43 = load ptr, ptr %3, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 4
  %47 = load i32, ptr %46, align 4
  %48 = sdiv i32 %.02745, %47
  %49 = mul i32 %48, %47
  %50 = xor i32 %47, %.02745
  %51 = icmp slt i32 %50, 0
  %52 = icmp ne i32 %49, %.02745
  %53 = and i1 %51, %52
  %.neg33 = sext i1 %53 to i32
  %54 = add i32 %48, %.neg33
  %55 = mul i32 %54, %47
  %56 = sub i32 %.02745, %55
  %57 = add i32 %54, %21
  %58 = add i32 %56, %23
  %59 = sdiv i32 %57, %25
  %60 = mul i32 %59, %25
  %61 = xor i32 %57, %25
  %62 = icmp slt i32 %61, 0
  %63 = icmp ne i32 %60, %57
  %64 = and i1 %63, %62
  %.neg34 = sext i1 %64 to i32
  %65 = add i32 %59, %.neg34
  %66 = sub i32 %65, %27
  %67 = sdiv i32 %58, %25
  %68 = mul i32 %67, %25
  %69 = xor i32 %58, %25
  %70 = icmp slt i32 %69, 0
  %71 = icmp ne i32 %68, %58
  %72 = and i1 %71, %70
  %.neg35 = sext i1 %72 to i32
  %invariant.op = add i32 %66, -3
  %invariant.op38 = add i32 %65, -3
  %73 = sitofp i32 %57 to float
  %74 = sitofp i32 %58 to float
  %75 = add i32 %67, %.neg35
  %76 = add i32 %42, %59
  %77 = add i32 %76, %.neg34
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %after_if13, %for_loop_body
  %.01944 = phi i32 [ 0, %for_loop_body ], [ %177, %after_if13 ]
  %.02043 = phi float [ 0.000000e+00, %for_loop_body ], [ %.1, %after_if13 ]
  %.02142 = phi float [ 0.000000e+00, %for_loop_body ], [ %.122, %after_if13 ]
  %.02341 = phi float [ 0.000000e+00, %for_loop_body ], [ %.124, %after_if13 ]
  %.02540 = phi float [ 0.000000e+00, %for_loop_body ], [ %.126, %after_if13 ]
  %78 = udiv i32 %.01944, 7
  %79 = mul nuw nsw i32 %78, 7
  %80 = sub i32 %75, %79
  %81 = add i32 %77, %78
  %tmp = trunc i32 %.01944 to i8
  %82 = udiv i8 %tmp, 7
  %.zext = zext nneg i8 %82 to i32
  %.reass = add i32 %invariant.op, %.zext
  %83 = add i32 %40, %.01944
  %84 = add i32 %83, %80
  %85 = icmp sgt i32 %.reass, -1
  br i1 %85, label %true_block, label %after_if13

after_for3:                                       ; preds = %after_if13
  %86 = fcmp reassoc ninf nsz ogt float %.126, 0x3E45798EE0000000
  %87 = load ptr, ptr %32, align 8
  %88 = load i32, ptr %33, align 4
  %89 = mul i32 %88, %54
  %90 = add i32 %89, %56
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %87, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = select reassoc ninf nsz i1 %86, float %93, float 0.000000e+00
  %95 = fmul reassoc ninf nsz float %94, %.126
  %96 = load ptr, ptr %34, align 8
  %97 = load i32, ptr %35, align 4
  %98 = mul i32 %97, %54
  %99 = add i32 %98, %56
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %96, i64 %100
  store float %95, ptr %101, align 4
  %102 = fmul reassoc ninf nsz float %94, %.124
  %103 = load ptr, ptr %36, align 8
  %104 = load i32, ptr %37, align 4
  %105 = load i32, ptr %38, align 4
  %106 = mul i32 %104, %54
  %107 = add i32 %106, %56
  %108 = mul i32 %107, %105
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %103, i64 %109
  store float %102, ptr %110, align 4
  %111 = fmul reassoc ninf nsz float %94, %.122
  %112 = load ptr, ptr %36, align 8
  %113 = load i32, ptr %37, align 4
  %114 = load i32, ptr %38, align 4
  %115 = mul i32 %113, %54
  %116 = add i32 %115, %56
  %117 = mul i32 %116, %114
  %118 = add i32 %117, 1
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %112, i64 %119
  store float %111, ptr %120, align 4
  %121 = fmul reassoc ninf nsz float %94, %.1
  %122 = load ptr, ptr %36, align 8
  %123 = load i32, ptr %37, align 4
  %124 = load i32, ptr %38, align 4
  %125 = mul i32 %123, %54
  %126 = add i32 %125, %56
  %127 = mul i32 %126, %124
  %128 = add i32 %127, 2
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %122, i64 %129
  store float %121, ptr %130, align 4
  %131 = add nsw i32 %.02745, 1
  %exitcond46.not = icmp eq i32 %131, %18
  br i1 %exitcond46.not, label %after_for.loopexit, label %for_loop_body

true_block:                                       ; preds = %for_loop_body1
  %132 = load ptr, ptr %0, align 8
  %133 = load i32, ptr %132, align 4
  %134 = icmp slt i32 %.reass, %133
  %135 = icmp sgt i32 %84, -1
  %or.cond = select i1 %134, i1 %135, i1 false
  br i1 %or.cond, label %true_block8, label %after_if13

true_block8:                                      ; preds = %true_block
  %136 = getelementptr i8, ptr %132, i64 4
  %137 = load i32, ptr %136, align 4
  %138 = icmp slt i32 %84, %137
  br i1 %138, label %true_block11, label %after_if13

true_block11:                                     ; preds = %true_block8
  %.reass39 = add i32 %invariant.op38, %.zext
  %139 = sitofp i32 %.reass39 to float
  %140 = getelementptr i8, ptr %132, i64 48
  %141 = load ptr, ptr %140, align 8
  %142 = getelementptr i8, ptr %132, i64 44
  %143 = load i32, ptr %142, align 4
  %144 = mul i32 %143, %81
  %145 = add i32 %41, %.01944
  %146 = add i32 %145, %144
  %147 = add i32 %146, %80
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %141, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = fadd reassoc ninf nsz float %150, %139
  %152 = fmul reassoc ninf nsz float %151, %31
  %153 = add i32 %.01944, -3
  %154 = add i32 %153, %80
  %155 = sitofp i32 %154 to float
  %156 = getelementptr i8, ptr %132, i64 64
  %157 = load ptr, ptr %156, align 8
  %158 = getelementptr i8, ptr %132, i64 60
  %159 = load i32, ptr %158, align 4
  %160 = mul i32 %159, %81
  %161 = add i32 %145, %160
  %162 = add i32 %161, %80
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %157, i64 %163
  %165 = load float, ptr %164, align 4
  %166 = fadd reassoc ninf nsz float %165, %155
  %167 = fmul reassoc ninf nsz float %166, %31
  %168 = fsub reassoc ninf nsz float %73, %152
  %169 = fmul reassoc ninf nsz float %168, %168
  %170 = fsub reassoc ninf nsz float %74, %167
  %171 = fmul reassoc ninf nsz float %170, %170
  %172 = fadd reassoc ninf nsz float %171, %169
  %173 = getelementptr i8, ptr %132, i64 132
  %174 = load float, ptr %173, align 4
  %175 = fmul reassoc ninf nsz float %174, %174
  %176 = fcmp reassoc ninf nsz ugt float %172, %175
  br i1 %176, label %after_if13, label %true_block14

after_if13:                                       ; preds = %true_block14, %true_block11, %true_block8, %true_block, %for_loop_body1
  %.126 = phi float [ %196, %true_block14 ], [ %.02540, %true_block11 ], [ %.02540, %true_block8 ], [ %.02540, %for_loop_body1 ], [ %.02540, %true_block ]
  %.124 = phi float [ %212, %true_block14 ], [ %.02341, %true_block11 ], [ %.02341, %true_block8 ], [ %.02341, %for_loop_body1 ], [ %.02341, %true_block ]
  %.122 = phi float [ %218, %true_block14 ], [ %.02142, %true_block11 ], [ %.02142, %true_block8 ], [ %.02142, %for_loop_body1 ], [ %.02142, %true_block ]
  %.1 = phi float [ %224, %true_block14 ], [ %.02043, %true_block11 ], [ %.02043, %true_block8 ], [ %.02043, %for_loop_body1 ], [ %.02043, %true_block ]
  %177 = add nuw nsw i32 %.01944, 1
  %exitcond.not = icmp eq i32 %177, 49
  br i1 %exitcond.not, label %after_for3, label %for_loop_body1

true_block14:                                     ; preds = %true_block11
  %178 = getelementptr i8, ptr %132, i64 32
  %179 = load ptr, ptr %178, align 8
  %180 = getelementptr i8, ptr %132, i64 28
  %181 = load i32, ptr %180, align 4
  %182 = mul i32 %181, %81
  %183 = add i32 %145, %182
  %184 = add i32 %183, %80
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, ptr %179, i64 %185
  %187 = load float, ptr %186, align 4
  %neg = fneg reassoc ninf nsz float %172
  %188 = load ptr, ptr %3, align 8
  %189 = getelementptr inbounds nuw i8, ptr %188, i64 32872
  %190 = load ptr, ptr %189, align 8
  %191 = getelementptr inbounds nuw i8, ptr %190, i64 8
  %192 = load float, ptr %191, align 4
  %193 = fmul reassoc ninf nsz float %192, %neg
  %194 = tail call noundef float @expf(float noundef %193) #8
  %195 = fmul reassoc ninf nsz float %194, %187
  %196 = fadd reassoc ninf nsz float %195, %.02540
  %197 = load ptr, ptr %0, align 8
  %198 = getelementptr i8, ptr %197, i64 16
  %199 = load ptr, ptr %198, align 8
  %200 = getelementptr i8, ptr %197, i64 4
  %201 = load i32, ptr %200, align 4
  %202 = getelementptr i8, ptr %197, i64 8
  %203 = load i32, ptr %202, align 4
  %204 = mul i32 %201, %81
  %205 = add i32 %145, %204
  %206 = add i32 %205, %80
  %207 = mul i32 %206, %203
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %199, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = fmul reassoc ninf nsz float %210, %195
  %212 = fadd reassoc ninf nsz float %211, %.02341
  %213 = add i32 %207, 1
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, ptr %199, i64 %214
  %216 = load float, ptr %215, align 4
  %217 = fmul reassoc ninf nsz float %216, %195
  %218 = fadd reassoc ninf nsz float %217, %.02142
  %219 = add i32 %207, 2
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, ptr %199, i64 %220
  %222 = load float, ptr %221, align 4
  %223 = fmul reassoc ninf nsz float %222, %195
  %224 = fadd reassoc ninf nsz float %223, %.02043
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
