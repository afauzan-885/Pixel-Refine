; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jbf_1ch_r1_c698_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 52
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

define void @_jbf_1ch_r1_c698_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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

; Function Attrs: nofree nounwind memory(readwrite, inaccessiblemem: write)
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
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load float, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 60
  %23 = load float, ptr %22, align 4
  %24 = fmul reassoc ninf nsz float %21, -2.000000e+00
  %25 = fneg reassoc ninf nsz float %21
  %26 = icmp slt i32 %16, %18
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr i8, ptr %19, i64 24
  %28 = getelementptr i8, ptr %19, i64 20
  %29 = getelementptr i8, ptr %19, i64 8
  %30 = getelementptr i8, ptr %19, i64 4
  %31 = fneg reassoc ninf nsz float %23
  %32 = getelementptr i8, ptr %19, i64 40
  %33 = getelementptr i8, ptr %19, i64 36
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %281, %for_loop_body ]
  %34 = load ptr, ptr %3, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 4
  %38 = load i32, ptr %37, align 4
  %39 = sdiv i32 %.05, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.05
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.05, %40
  %44 = and i1 %42, %43
  %.neg4 = sext i1 %44 to i32
  %45 = add i32 %39, %.neg4
  %46 = mul i32 %38, -1
  %47 = mul i32 %46, %45
  %48 = add i32 %.05, %47
  %49 = load ptr, ptr %27, align 8
  %50 = load i32, ptr %28, align 4
  %51 = sub i32 %50, %38
  %52 = mul i32 %51, %45
  %53 = add i32 %.05, %52
  %54 = sext i32 %53 to i64
  %55 = getelementptr float, ptr %49, i64 %54
  %56 = load float, ptr %55, align 4
  %57 = add i32 %45, -1
  %58 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %59 = load i32, ptr %58, align 4
  %60 = add i32 %59, -1
  %61 = tail call i32 @llvm.smax.i32(i32 %57, i32 0)
  %62 = tail call i32 @llvm.smin.i32(i32 %60, i32 %61)
  %63 = add i32 %48, -1
  %64 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %65 = load i32, ptr %64, align 4
  %66 = add i32 %65, -1
  %67 = tail call i32 @llvm.smax.i32(i32 %63, i32 0)
  %68 = tail call i32 @llvm.smin.i32(i32 %66, i32 %67)
  %69 = mul i32 %62, %50
  %70 = add i32 %68, %69
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, ptr %49, i64 %71
  %73 = load float, ptr %72, align 4
  %74 = fsub reassoc ninf nsz float %73, %56
  %75 = fmul reassoc ninf nsz float %74, %74
  %76 = fmul reassoc ninf nsz float %75, %23
  %77 = fsub reassoc ninf nsz float %24, %76
  %78 = tail call noundef float @expf(float noundef %77) #7
  %79 = load ptr, ptr %29, align 8
  %80 = load i32, ptr %30, align 4
  %81 = mul i32 %80, %62
  %82 = add i32 %81, %68
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, ptr %79, i64 %83
  %85 = load float, ptr %84, align 4
  %86 = fmul reassoc ninf nsz float %85, %78
  %87 = fadd reassoc ninf nsz float %78, 0x3D71979980000000
  %88 = tail call i32 @llvm.smax.i32(i32 %48, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %66, i32 %88)
  %90 = load ptr, ptr %27, align 8
  %91 = load i32, ptr %28, align 4
  %92 = mul i32 %91, %62
  %93 = add i32 %92, %89
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %90, i64 %94
  %96 = load float, ptr %95, align 4
  %97 = fsub reassoc ninf nsz float %96, %56
  %98 = fmul reassoc ninf nsz float %97, %97
  %99 = fmul reassoc ninf nsz float %98, %23
  %100 = fsub reassoc ninf nsz float %25, %99
  %101 = tail call noundef float @expf(float noundef %100) #7
  %102 = load ptr, ptr %29, align 8
  %103 = load i32, ptr %30, align 4
  %104 = mul i32 %103, %62
  %105 = add i32 %104, %89
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %102, i64 %106
  %108 = load float, ptr %107, align 4
  %109 = fmul reassoc ninf nsz float %108, %101
  %110 = fadd reassoc ninf nsz float %109, %86
  %111 = fadd reassoc ninf nsz float %87, %101
  %112 = add i32 %48, 1
  %113 = tail call i32 @llvm.smax.i32(i32 %112, i32 0)
  %114 = tail call i32 @llvm.smin.i32(i32 %66, i32 %113)
  %115 = load ptr, ptr %27, align 8
  %116 = load i32, ptr %28, align 4
  %117 = mul i32 %116, %62
  %118 = add i32 %117, %114
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %115, i64 %119
  %121 = load float, ptr %120, align 4
  %122 = fsub reassoc ninf nsz float %121, %56
  %123 = fmul reassoc ninf nsz float %122, %122
  %124 = fmul reassoc ninf nsz float %123, %23
  %125 = fsub reassoc ninf nsz float %24, %124
  %126 = tail call noundef float @expf(float noundef %125) #7
  %127 = load ptr, ptr %29, align 8
  %128 = load i32, ptr %30, align 4
  %129 = mul i32 %128, %62
  %130 = add i32 %129, %114
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, ptr %127, i64 %131
  %133 = load float, ptr %132, align 4
  %134 = fmul reassoc ninf nsz float %133, %126
  %135 = fadd reassoc ninf nsz float %110, %134
  %136 = fadd reassoc ninf nsz float %111, %126
  %137 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %138 = tail call i32 @llvm.smin.i32(i32 %60, i32 %137)
  %139 = load ptr, ptr %27, align 8
  %140 = load i32, ptr %28, align 4
  %141 = mul i32 %140, %138
  %142 = add i32 %141, %68
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %139, i64 %143
  %145 = load float, ptr %144, align 4
  %146 = fsub reassoc ninf nsz float %145, %56
  %147 = fmul reassoc ninf nsz float %146, %146
  %148 = fmul reassoc ninf nsz float %147, %23
  %149 = fsub reassoc ninf nsz float %25, %148
  %150 = tail call noundef float @expf(float noundef %149) #7
  %151 = load ptr, ptr %29, align 8
  %152 = load i32, ptr %30, align 4
  %153 = mul i32 %152, %138
  %154 = add i32 %153, %68
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %151, i64 %155
  %157 = load float, ptr %156, align 4
  %158 = fmul reassoc ninf nsz float %157, %150
  %159 = fadd reassoc ninf nsz float %135, %158
  %160 = fadd reassoc ninf nsz float %136, %150
  %161 = load ptr, ptr %27, align 8
  %162 = load i32, ptr %28, align 4
  %163 = mul i32 %162, %138
  %164 = add i32 %163, %89
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %161, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = fsub reassoc ninf nsz float %167, %56
  %169 = fmul reassoc ninf nsz float %168, %168
  %170 = fmul reassoc ninf nsz float %169, %31
  %171 = tail call noundef float @expf(float noundef %170) #7
  %172 = load ptr, ptr %29, align 8
  %173 = load i32, ptr %30, align 4
  %174 = mul i32 %173, %138
  %175 = add i32 %174, %89
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, ptr %172, i64 %176
  %178 = load float, ptr %177, align 4
  %179 = fmul reassoc ninf nsz float %178, %171
  %180 = fadd reassoc ninf nsz float %159, %179
  %181 = fadd reassoc ninf nsz float %160, %171
  %182 = load ptr, ptr %27, align 8
  %183 = load i32, ptr %28, align 4
  %184 = mul i32 %183, %138
  %185 = add i32 %184, %114
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %182, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = fsub reassoc ninf nsz float %188, %56
  %190 = fmul reassoc ninf nsz float %189, %189
  %191 = fmul reassoc ninf nsz float %190, %23
  %192 = fsub reassoc ninf nsz float %25, %191
  %193 = tail call noundef float @expf(float noundef %192) #7
  %194 = load ptr, ptr %29, align 8
  %195 = load i32, ptr %30, align 4
  %196 = mul i32 %195, %138
  %197 = add i32 %196, %114
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %194, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = fmul reassoc ninf nsz float %200, %193
  %202 = fadd reassoc ninf nsz float %180, %201
  %203 = fadd reassoc ninf nsz float %181, %193
  %204 = add i32 %45, 1
  %205 = tail call i32 @llvm.smax.i32(i32 %204, i32 0)
  %206 = tail call i32 @llvm.smin.i32(i32 %60, i32 %205)
  %207 = load ptr, ptr %27, align 8
  %208 = load i32, ptr %28, align 4
  %209 = mul i32 %208, %206
  %210 = add i32 %209, %68
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %207, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = fsub reassoc ninf nsz float %213, %56
  %215 = fmul reassoc ninf nsz float %214, %214
  %216 = fmul reassoc ninf nsz float %215, %23
  %217 = fsub reassoc ninf nsz float %24, %216
  %218 = tail call noundef float @expf(float noundef %217) #7
  %219 = load ptr, ptr %29, align 8
  %220 = load i32, ptr %30, align 4
  %221 = mul i32 %220, %206
  %222 = add i32 %221, %68
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %219, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = fmul reassoc ninf nsz float %225, %218
  %227 = fadd reassoc ninf nsz float %202, %226
  %228 = fadd reassoc ninf nsz float %203, %218
  %229 = load ptr, ptr %27, align 8
  %230 = load i32, ptr %28, align 4
  %231 = mul i32 %230, %206
  %232 = add i32 %231, %89
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %229, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = fsub reassoc ninf nsz float %235, %56
  %237 = fmul reassoc ninf nsz float %236, %236
  %238 = fmul reassoc ninf nsz float %237, %23
  %239 = fsub reassoc ninf nsz float %25, %238
  %240 = tail call noundef float @expf(float noundef %239) #7
  %241 = load ptr, ptr %29, align 8
  %242 = load i32, ptr %30, align 4
  %243 = mul i32 %242, %206
  %244 = add i32 %243, %89
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, ptr %241, i64 %245
  %247 = load float, ptr %246, align 4
  %248 = fmul reassoc ninf nsz float %247, %240
  %249 = fadd reassoc ninf nsz float %227, %248
  %250 = fadd reassoc ninf nsz float %228, %240
  %251 = load ptr, ptr %27, align 8
  %252 = load i32, ptr %28, align 4
  %253 = mul i32 %252, %206
  %254 = add i32 %253, %114
  %255 = sext i32 %254 to i64
  %256 = getelementptr float, ptr %251, i64 %255
  %257 = load float, ptr %256, align 4
  %258 = fsub reassoc ninf nsz float %257, %56
  %259 = fmul reassoc ninf nsz float %258, %258
  %260 = fmul reassoc ninf nsz float %259, %23
  %261 = fsub reassoc ninf nsz float %24, %260
  %262 = tail call noundef float @expf(float noundef %261) #7
  %263 = load ptr, ptr %29, align 8
  %264 = load i32, ptr %30, align 4
  %265 = mul i32 %264, %206
  %266 = add i32 %265, %114
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, ptr %263, i64 %267
  %269 = load float, ptr %268, align 4
  %270 = fmul reassoc ninf nsz float %269, %262
  %271 = fadd reassoc ninf nsz float %249, %270
  %272 = fadd reassoc ninf nsz float %250, %262
  %273 = fdiv reassoc ninf nsz float %271, %272
  %274 = load ptr, ptr %32, align 8
  %275 = load i32, ptr %33, align 4
  %276 = sub i32 %275, %38
  %277 = mul i32 %276, %45
  %278 = add i32 %.05, %277
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, ptr %274, i64 %279
  store float %273, ptr %280, align 4
  %281 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %18, %281
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
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
