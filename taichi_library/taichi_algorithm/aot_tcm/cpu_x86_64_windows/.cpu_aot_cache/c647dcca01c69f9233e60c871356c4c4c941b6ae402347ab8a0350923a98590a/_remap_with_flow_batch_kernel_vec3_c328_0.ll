; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.23 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_remap_with_flow_batch_kernel_vec3_c328_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 72
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 84
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 16
  store i32 %5, ptr %10, align 4
  %11 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %12 = load ptr, ptr %context, align 8
  %13 = getelementptr i8, ptr %12, i64 88
  %14 = load i32, ptr %13, align 4
  %15 = load ptr, ptr %6, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 32872
  %17 = load ptr, ptr %16, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 12
  store i32 %14, ptr %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %14, i32 0)
  %20 = mul i32 %19, 3
  %21 = load ptr, ptr %6, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 8
  store i32 %20, ptr %24, align 4
  %25 = mul i32 %20, %11
  %26 = load ptr, ptr %6, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  store i32 %25, ptr %29, align 4
  %30 = mul i32 %25, %3
  %31 = load ptr, ptr %6, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  store i32 %30, ptr %33, align 4
  ret void
}

define void @_remap_with_flow_batch_kernel_vec3_c328_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 96
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 92
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 100
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 104
  %27 = load float, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 80
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 76
  %31 = load i32, ptr %30, align 4
  %32 = add i32 %21, -1
  %33 = add i32 %23, -1
  %34 = add i32 %29, -1
  %35 = add i32 %31, -1
  %36 = sitofp i32 %32 to float
  %37 = sitofp i32 %33 to float
  %38 = icmp slt i32 %16, %18
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr i8, ptr %19, i64 40
  %40 = getelementptr i8, ptr %19, i64 28
  %41 = getelementptr i8, ptr %19, i64 32
  %42 = getelementptr i8, ptr %19, i64 36
  %43 = getelementptr i8, ptr %19, i64 16
  %44 = getelementptr i8, ptr %19, i64 4
  %45 = getelementptr i8, ptr %19, i64 8
  %46 = getelementptr i8, ptr %19, i64 12
  %47 = getelementptr i8, ptr %19, i64 64
  %48 = getelementptr i8, ptr %19, i64 52
  %49 = getelementptr i8, ptr %19, i64 56
  %50 = getelementptr i8, ptr %19, i64 60
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.09 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %271, %for_loop_body ]
  %51 = load ptr, ptr %3, align 8
  %52 = getelementptr inbounds nuw i8, ptr %51, i64 32872
  %53 = load ptr, ptr %52, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 4
  %55 = load i32, ptr %54, align 4
  %56 = sdiv i32 %.09, %55
  %57 = mul i32 %56, %55
  %58 = xor i32 %55, %.09
  %59 = icmp slt i32 %58, 0
  %60 = icmp ne i32 %.09, %57
  %61 = and i1 %59, %60
  %.neg4 = sext i1 %61 to i32
  %62 = add i32 %56, %.neg4
  %63 = mul i32 %62, %55
  %64 = mul i32 %55, -1
  %65 = mul i32 %64, %62
  %66 = add i32 %.09, %65
  %67 = getelementptr inbounds nuw i8, ptr %53, i64 8
  %68 = load i32, ptr %67, align 4
  %69 = sdiv i32 %66, %68
  %70 = mul i32 %69, %68
  %71 = xor i32 %66, %68
  %72 = icmp slt i32 %71, 0
  %73 = icmp ne i32 %.09, %63
  %74 = icmp ne i32 %66, %70
  %75 = and i1 %73, %72
  %76 = and i1 %74, %75
  %.neg5 = sext i1 %76 to i32
  %77 = add i32 %69, %.neg5
  %78 = mul i32 %77, %68
  %79 = mul i32 %68, -1
  %80 = mul i32 %79, %77
  %81 = sub i32 %80, %63
  %82 = add i32 %.09, %81
  %83 = sdiv i32 %82, 3
  %84 = icmp slt i32 %82, 0
  %85 = mul nsw i32 %83, 3
  %86 = icmp ne i32 %82, %85
  %87 = and i1 %84, %86
  %.neg6 = sext i1 %87 to i32
  %88 = add i32 %83, %.neg6
  %89 = sitofp i32 %88 to float
  %90 = fmul reassoc ninf nsz float %89, %36
  %91 = getelementptr inbounds nuw i8, ptr %53, i64 12
  %92 = load i32, ptr %91, align 4
  %93 = add i32 %92, -1
  %94 = sitofp i32 %93 to float
  %95 = fdiv reassoc ninf nsz float %90, %94
  %96 = sitofp i32 %77 to float
  %97 = fmul reassoc ninf nsz float %96, %37
  %98 = getelementptr inbounds nuw i8, ptr %53, i64 16
  %99 = load i32, ptr %98, align 4
  %100 = add i32 %99, -1
  %101 = sitofp i32 %100 to float
  %102 = fdiv reassoc ninf nsz float %97, %101
  %103 = tail call reassoc ninf nsz float @llvm.floor.f32(float %95)
  %104 = fptosi float %103 to i32
  %105 = tail call reassoc ninf nsz float @llvm.floor.f32(float %102)
  %106 = fptosi float %105 to i32
  %107 = add i32 %104, 1
  %108 = tail call i32 @llvm.smin.i32(i32 %107, i32 %32)
  %109 = add i32 %106, 1
  %110 = tail call i32 @llvm.smin.i32(i32 %109, i32 %33)
  %111 = sitofp i32 %104 to float
  %112 = fsub reassoc ninf nsz float %95, %111
  %113 = sitofp i32 %106 to float
  %114 = fsub reassoc ninf nsz float %102, %113
  %115 = load ptr, ptr %39, align 8
  %116 = load i32, ptr %40, align 4
  %117 = load i32, ptr %41, align 4
  %118 = load i32, ptr %42, align 4
  %119 = mul i32 %116, %62
  %120 = add i32 %119, %106
  %121 = mul i32 %120, %117
  %122 = add i32 %121, %104
  %123 = mul i32 %122, %118
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %115, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = add i32 %108, %121
  %128 = mul i32 %127, %118
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %115, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = add i32 %110, %119
  %133 = mul i32 %132, %117
  %134 = add i32 %133, %104
  %135 = mul i32 %134, %118
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %115, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = add i32 %108, %133
  %140 = mul i32 %139, %118
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %115, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = add i32 %123, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %115, i64 %145
  %147 = load float, ptr %146, align 4
  %148 = add i32 %128, 1
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %115, i64 %149
  %151 = load float, ptr %150, align 4
  %152 = add i32 %135, 1
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %115, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = add i32 %140, 1
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %115, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = fsub reassoc ninf nsz float 1.000000e+00, %112
  %161 = fmul reassoc ninf nsz float %160, %126
  %162 = fmul reassoc ninf nsz float %112, %131
  %163 = fadd reassoc ninf nsz float %161, %162
  %164 = fsub reassoc ninf nsz float 1.000000e+00, %114
  %165 = fmul reassoc ninf nsz float %163, %164
  %166 = fmul reassoc ninf nsz float %160, %138
  %167 = fmul reassoc ninf nsz float %112, %143
  %168 = fadd reassoc ninf nsz float %166, %167
  %169 = fmul reassoc ninf nsz float %168, %114
  %170 = fadd reassoc ninf nsz float %165, %169
  %171 = fmul reassoc ninf nsz float %160, %147
  %172 = fmul reassoc ninf nsz float %112, %151
  %173 = fadd reassoc ninf nsz float %171, %172
  %174 = fmul reassoc ninf nsz float %173, %164
  %175 = fmul reassoc ninf nsz float %160, %155
  %176 = fmul reassoc ninf nsz float %112, %159
  %177 = fadd reassoc ninf nsz float %175, %176
  %178 = fmul reassoc ninf nsz float %177, %114
  %179 = fadd reassoc ninf nsz float %174, %178
  %180 = fmul reassoc ninf nsz float %170, %25
  %181 = fadd reassoc ninf nsz float %180, %89
  %182 = fmul reassoc ninf nsz float %179, %27
  %183 = fadd reassoc ninf nsz float %182, %96
  %184 = tail call reassoc ninf nsz float @llvm.floor.f32(float %181)
  %185 = fptosi float %184 to i32
  %186 = tail call reassoc ninf nsz float @llvm.floor.f32(float %183)
  %187 = fptosi float %186 to i32
  %188 = sitofp i32 %185 to float
  %189 = fsub reassoc ninf nsz float %181, %188
  %190 = sitofp i32 %187 to float
  %191 = fsub reassoc ninf nsz float %183, %190
  %192 = tail call i32 @llvm.smax.i32(i32 %185, i32 0)
  %193 = tail call i32 @llvm.smin.i32(i32 %192, i32 %34)
  %194 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %195 = tail call i32 @llvm.smin.i32(i32 %194, i32 %35)
  %196 = add i32 %193, 1
  %197 = tail call i32 @llvm.smin.i32(i32 %196, i32 %34)
  %198 = add i32 %195, 1
  %199 = tail call i32 @llvm.smin.i32(i32 %198, i32 %35)
  %200 = load ptr, ptr %43, align 8
  %201 = load i32, ptr %44, align 4
  %202 = load i32, ptr %45, align 4
  %203 = load i32, ptr %46, align 4
  %204 = mul i32 %201, %62
  %205 = add i32 %195, %204
  %206 = mul i32 %205, %202
  %207 = add i32 %206, %193
  %208 = mul i32 %207, %203
  %209 = sub i32 %208, %78
  %210 = sub i32 %209, %63
  %211 = mul i32 %88, 3
  %212 = sub i32 %210, %211
  %213 = add i32 %.09, %212
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, ptr %200, i64 %214
  %216 = load float, ptr %215, align 4
  %217 = add i32 %206, %197
  %218 = mul i32 %217, %203
  %219 = sub i32 %218, %78
  %220 = sub i32 %219, %63
  %221 = sub i32 %220, %211
  %222 = add i32 %.09, %221
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %200, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = add i32 %199, %204
  %227 = mul i32 %226, %202
  %228 = add i32 %227, %193
  %229 = mul i32 %228, %203
  %230 = sub i32 %229, %78
  %231 = sub i32 %230, %63
  %232 = sub i32 %231, %211
  %233 = add i32 %.09, %232
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, ptr %200, i64 %234
  %236 = load float, ptr %235, align 4
  %237 = add i32 %227, %197
  %238 = mul i32 %237, %203
  %239 = sub i32 %238, %78
  %240 = sub i32 %239, %63
  %241 = sub i32 %240, %211
  %242 = add i32 %.09, %241
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, ptr %200, i64 %243
  %245 = load float, ptr %244, align 4
  %246 = fsub reassoc ninf nsz float 1.000000e+00, %189
  %247 = fmul reassoc ninf nsz float %246, %216
  %248 = fmul reassoc ninf nsz float %189, %225
  %249 = fadd reassoc ninf nsz float %247, %248
  %250 = fmul reassoc ninf nsz float %246, %236
  %251 = fmul reassoc ninf nsz float %189, %245
  %252 = fadd reassoc ninf nsz float %250, %251
  %253 = fsub reassoc ninf nsz float %252, %249
  %254 = fmul reassoc ninf nsz float %253, %191
  %255 = fadd reassoc ninf nsz float %254, %249
  %256 = load ptr, ptr %47, align 8
  %257 = load i32, ptr %48, align 4
  %258 = load i32, ptr %49, align 4
  %259 = load i32, ptr %50, align 4
  %260 = mul i32 %257, %62
  %261 = add i32 %260, %77
  %262 = mul i32 %261, %258
  %263 = add i32 %262, %88
  %264 = mul i32 %263, %259
  %265 = sub i32 %264, %78
  %266 = sub i32 %265, %63
  %267 = sub i32 %266, %211
  %268 = add i32 %.09, %267
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, ptr %256, i64 %269
  store float %255, ptr %270, align 4
  %271 = add nsw i32 %.09, 1
  %exitcond.not = icmp eq i32 %18, %271
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.23, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
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
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
