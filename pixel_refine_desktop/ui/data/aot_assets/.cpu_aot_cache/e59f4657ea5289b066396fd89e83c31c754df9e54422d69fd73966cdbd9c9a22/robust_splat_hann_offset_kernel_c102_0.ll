; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @robust_splat_hann_offset_kernel_c102_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 160
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
  %12 = getelementptr i8, ptr %11, i64 172
  %13 = load i32, ptr %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = getelementptr i8, ptr %11, i64 176
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

define void @robust_splat_hann_offset_kernel_c102_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 164
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 168
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 152
  %25 = load i32, ptr %24, align 4
  %26 = icmp slt i32 %16, %18
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = sitofp i32 %25 to float
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if19, %for_loop_body.lr.ph
  %.02850 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %258, %after_if19 ]
  %28 = load ptr, ptr %3, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 4
  %32 = load i32, ptr %31, align 4
  %33 = sdiv i32 %.02850, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.02850
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %34, %.02850
  %38 = and i1 %36, %37
  %.neg34 = sext i1 %38 to i32
  %39 = add i32 %33, %.neg34
  %40 = mul i32 %39, %32
  %41 = sub i32 %.02850, %40
  %42 = add i32 %39, %21
  %43 = add i32 %41, %23
  %44 = load ptr, ptr %0, align 8
  %45 = load i32, ptr %44, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %47 = mul i32 %46, 49
  %48 = icmp sgt i32 %47, 0
  br i1 %48, label %for_loop_body1.lr.ph, label %after_if19

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %49 = sdiv i32 %43, %25
  %50 = mul i32 %49, %25
  %51 = icmp ne i32 %50, %43
  %52 = xor i32 %43, %25
  %53 = icmp slt i32 %52, 0
  %54 = and i1 %51, %53
  %.neg36 = sext i1 %54 to i32
  %55 = sdiv i32 %42, %25
  %56 = mul i32 %55, %25
  %57 = icmp ne i32 %56, %42
  %58 = xor i32 %42, %25
  %59 = icmp slt i32 %58, 0
  %60 = and i1 %57, %59
  %.neg35 = sext i1 %60 to i32
  %61 = add i32 %55, -3
  %62 = add i32 %61, %.neg35
  %63 = sitofp i32 %42 to float
  %64 = sitofp i32 %43 to float
  %65 = add i32 %49, -3
  %66 = add i32 %65, %.neg36
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_if19
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %after_if13, %for_loop_body1.lr.ph
  %67 = phi ptr [ %44, %for_loop_body1.lr.ph ], [ %142, %after_if13 ]
  %.02046 = phi i32 [ 0, %for_loop_body1.lr.ph ], [ %143, %after_if13 ]
  %.02145 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.1, %after_if13 ]
  %.02244 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.123, %after_if13 ]
  %.02443 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.125, %after_if13 ]
  %.02642 = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.127, %after_if13 ]
  %68 = udiv i32 %.02046, 49
  %69 = mul nuw nsw i32 %68, 49
  %70 = sub i32 %66, %69
  %71 = mul nsw i32 %68, -49
  %72 = add i32 %.02046, %71
  %73 = sdiv i32 %72, 7
  %74 = icmp slt i32 %72, 0
  %75 = mul nsw i32 %73, 7
  %76 = icmp ne i32 %72, %75
  %77 = and i1 %74, %76
  %.neg39 = sext i1 %77 to i32
  %78 = add nsw i32 %73, %.neg39
  %.neg40 = mul i32 %78, -7
  %79 = add i32 %62, %78
  %80 = add i32 %.02046, %.neg40
  %81 = add i32 %80, %70
  %82 = icmp sgt i32 %79, -1
  br i1 %82, label %true_block, label %after_if13

after_for3:                                       ; preds = %after_if13
  %83 = fcmp reassoc ninf nsz ogt float %.127, 0x3E45798EE0000000
  br i1 %83, label %true_block17, label %after_if19

true_block:                                       ; preds = %for_loop_body1
  %84 = getelementptr i8, ptr %67, i64 4
  %85 = load i32, ptr %84, align 4
  %86 = icmp slt i32 %79, %85
  %87 = icmp sgt i32 %81, -1
  %or.cond = select i1 %86, i1 %87, i1 false
  br i1 %or.cond, label %true_block8, label %after_if13

true_block8:                                      ; preds = %true_block
  %88 = getelementptr i8, ptr %67, i64 8
  %89 = load i32, ptr %88, align 4
  %90 = icmp slt i32 %81, %89
  br i1 %90, label %true_block11, label %after_if13

true_block11:                                     ; preds = %true_block8
  %91 = uitofp nneg i32 %79 to float
  %92 = getelementptr i8, ptr %67, i64 64
  %93 = load ptr, ptr %92, align 8
  %94 = getelementptr i8, ptr %67, i64 52
  %95 = load i32, ptr %94, align 4
  %96 = getelementptr i8, ptr %67, i64 56
  %97 = load i32, ptr %96, align 4
  %98 = mul i32 %73, -7
  %99 = mul nsw i32 %.neg39, 7
  %100 = sub i32 %98, %99
  %101 = add i32 %62, %73
  %102 = mul i32 %95, %68
  %103 = add i32 %101, %102
  %104 = add i32 %103, %.neg39
  %105 = mul i32 %97, %104
  %106 = add i32 %.02046, %105
  %107 = add i32 %106, %100
  %108 = add i32 %107, %70
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %93, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = fadd reassoc ninf nsz float %111, %91
  %113 = fmul reassoc ninf nsz float %112, %27
  %114 = uitofp nneg i32 %81 to float
  %115 = getelementptr i8, ptr %67, i64 88
  %116 = load ptr, ptr %115, align 8
  %117 = getelementptr i8, ptr %67, i64 76
  %118 = load i32, ptr %117, align 4
  %119 = getelementptr i8, ptr %67, i64 80
  %120 = load i32, ptr %119, align 4
  %121 = mul i32 %118, %68
  %122 = add i32 %101, %121
  %123 = add i32 %122, %.neg39
  %124 = mul i32 %120, %123
  %125 = add i32 %.02046, %124
  %126 = add i32 %125, %100
  %127 = add i32 %126, %70
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %116, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = fadd reassoc ninf nsz float %130, %114
  %132 = fmul reassoc ninf nsz float %131, %27
  %133 = fsub reassoc ninf nsz float %63, %113
  %134 = fmul reassoc ninf nsz float %133, %133
  %135 = fsub reassoc ninf nsz float %64, %132
  %136 = fmul reassoc ninf nsz float %135, %135
  %137 = fadd reassoc ninf nsz float %136, %134
  %138 = getelementptr i8, ptr %67, i64 156
  %139 = load float, ptr %138, align 4
  %140 = fmul reassoc ninf nsz float %139, %139
  %141 = fcmp reassoc ninf nsz ugt float %137, %140
  br i1 %141, label %after_if13, label %true_block14

after_if13:                                       ; preds = %true_block14, %true_block11, %true_block8, %true_block, %for_loop_body1
  %142 = phi ptr [ %169, %true_block14 ], [ %67, %true_block11 ], [ %67, %true_block8 ], [ %67, %for_loop_body1 ], [ %67, %true_block ]
  %.127 = phi float [ %168, %true_block14 ], [ %.02642, %true_block11 ], [ %.02642, %true_block8 ], [ %.02642, %for_loop_body1 ], [ %.02642, %true_block ]
  %.125 = phi float [ %190, %true_block14 ], [ %.02443, %true_block11 ], [ %.02443, %true_block8 ], [ %.02443, %for_loop_body1 ], [ %.02443, %true_block ]
  %.123 = phi float [ %196, %true_block14 ], [ %.02244, %true_block11 ], [ %.02244, %true_block8 ], [ %.02244, %for_loop_body1 ], [ %.02244, %true_block ]
  %.1 = phi float [ %202, %true_block14 ], [ %.02145, %true_block11 ], [ %.02145, %true_block8 ], [ %.02145, %for_loop_body1 ], [ %.02145, %true_block ]
  %143 = add nuw nsw i32 %.02046, 1
  %exitcond.not = icmp eq i32 %47, %143
  br i1 %exitcond.not, label %after_for3, label %for_loop_body1

true_block14:                                     ; preds = %true_block11
  %144 = getelementptr i8, ptr %67, i64 40
  %145 = load ptr, ptr %144, align 8
  %146 = getelementptr i8, ptr %67, i64 28
  %147 = load i32, ptr %146, align 4
  %148 = getelementptr i8, ptr %67, i64 32
  %149 = load i32, ptr %148, align 4
  %150 = mul i32 %147, %68
  %151 = add i32 %101, %150
  %152 = add i32 %151, %.neg39
  %153 = mul i32 %149, %152
  %154 = add i32 %.02046, %153
  %155 = add i32 %154, %100
  %156 = add i32 %155, %70
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %145, i64 %157
  %159 = load float, ptr %158, align 4
  %neg = fneg reassoc ninf nsz float %137
  %160 = load ptr, ptr %3, align 8
  %161 = getelementptr inbounds nuw i8, ptr %160, i64 32872
  %162 = load ptr, ptr %161, align 8
  %163 = getelementptr inbounds nuw i8, ptr %162, i64 8
  %164 = load float, ptr %163, align 4
  %165 = fmul reassoc ninf nsz float %164, %neg
  %166 = tail call noundef float @expf(float noundef %165) #8
  %167 = fmul reassoc ninf nsz float %166, %159
  %168 = fadd reassoc ninf nsz float %167, %.02642
  %169 = load ptr, ptr %0, align 8
  %170 = getelementptr i8, ptr %169, i64 16
  %171 = load ptr, ptr %170, align 8
  %172 = getelementptr i8, ptr %169, i64 4
  %173 = load i32, ptr %172, align 4
  %174 = getelementptr i8, ptr %169, i64 8
  %175 = load i32, ptr %174, align 4
  %176 = getelementptr i8, ptr %169, i64 12
  %177 = load i32, ptr %176, align 4
  %178 = mul i32 %173, %68
  %179 = add i32 %101, %178
  %180 = add i32 %179, %.neg39
  %181 = mul i32 %175, %180
  %182 = add i32 %.02046, %181
  %183 = add i32 %182, %100
  %184 = add i32 %183, %70
  %185 = mul i32 %184, %177
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %171, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = fmul reassoc ninf nsz float %188, %167
  %190 = fadd reassoc ninf nsz float %189, %.02443
  %191 = add i32 %185, 1
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, ptr %171, i64 %192
  %194 = load float, ptr %193, align 4
  %195 = fmul reassoc ninf nsz float %194, %167
  %196 = fadd reassoc ninf nsz float %195, %.02244
  %197 = add i32 %185, 2
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %171, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = fmul reassoc ninf nsz float %200, %167
  %202 = fadd reassoc ninf nsz float %201, %.02145
  br label %after_if13

true_block17:                                     ; preds = %after_for3
  %203 = getelementptr i8, ptr %142, i64 104
  %204 = load ptr, ptr %203, align 8
  %205 = getelementptr i8, ptr %142, i64 100
  %206 = load i32, ptr %205, align 4
  %207 = mul i32 %206, %39
  %208 = add i32 %207, %41
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, ptr %204, i64 %209
  %211 = load float, ptr %210, align 4
  %212 = fmul reassoc ninf nsz float %211, %.127
  %213 = getelementptr i8, ptr %142, i64 144
  %214 = load ptr, ptr %213, align 8
  %215 = getelementptr i8, ptr %142, i64 140
  %216 = load i32, ptr %215, align 4
  %217 = mul i32 %216, %42
  %218 = add i32 %217, %43
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, ptr %214, i64 %219
  %221 = atomicrmw fadd ptr %220, float %212 seq_cst, align 4
  %222 = fmul reassoc ninf nsz float %211, %.125
  %223 = load ptr, ptr %0, align 8
  %224 = getelementptr i8, ptr %223, i64 128
  %225 = load ptr, ptr %224, align 8
  %226 = getelementptr i8, ptr %223, i64 116
  %227 = load i32, ptr %226, align 4
  %228 = getelementptr i8, ptr %223, i64 120
  %229 = load i32, ptr %228, align 4
  %230 = mul i32 %227, %42
  %231 = add i32 %230, %43
  %232 = mul i32 %231, %229
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %225, i64 %233
  %235 = atomicrmw fadd ptr %234, float %222 seq_cst, align 4
  %236 = fmul reassoc ninf nsz float %211, %.123
  %237 = load ptr, ptr %224, align 8
  %238 = load i32, ptr %226, align 4
  %239 = load i32, ptr %228, align 4
  %240 = mul i32 %238, %42
  %241 = add i32 %240, %43
  %242 = mul i32 %241, %239
  %243 = add i32 %242, 1
  %244 = sext i32 %243 to i64
  %245 = getelementptr float, ptr %237, i64 %244
  %246 = atomicrmw fadd ptr %245, float %236 seq_cst, align 4
  %247 = fmul reassoc ninf nsz float %211, %.1
  %248 = load ptr, ptr %224, align 8
  %249 = load i32, ptr %226, align 4
  %250 = load i32, ptr %228, align 4
  %251 = mul i32 %249, %42
  %252 = add i32 %251, %43
  %253 = mul i32 %252, %250
  %254 = add i32 %253, 2
  %255 = sext i32 %254 to i64
  %256 = getelementptr float, ptr %248, i64 %255
  %257 = atomicrmw fadd ptr %256, float %247 seq_cst, align 4
  br label %after_if19

after_if19:                                       ; preds = %true_block17, %after_for3, %for_loop_body
  %258 = add nsw i32 %.02850, 1
  %exitcond51.not = icmp eq i32 %258, %18
  br i1 %exitcond51.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.3, align 8
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
