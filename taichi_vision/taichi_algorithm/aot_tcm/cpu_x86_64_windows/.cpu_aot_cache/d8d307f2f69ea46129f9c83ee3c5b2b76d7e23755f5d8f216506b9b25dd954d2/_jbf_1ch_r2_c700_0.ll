; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jbf_1ch_r2_c700_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_jbf_1ch_r2_c700_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %24 = fmul reassoc ninf nsz float %21, -8.000000e+00
  %25 = fmul reassoc ninf nsz float %21, -5.000000e+00
  %26 = fmul reassoc ninf nsz float %21, -4.000000e+00
  %27 = fmul reassoc ninf nsz float %21, -2.000000e+00
  %28 = fneg reassoc ninf nsz float %21
  %29 = icmp slt i32 %16, %18
  br i1 %29, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %30 = getelementptr i8, ptr %19, i64 24
  %31 = getelementptr i8, ptr %19, i64 20
  %32 = getelementptr i8, ptr %19, i64 8
  %33 = getelementptr i8, ptr %19, i64 4
  %34 = fneg reassoc ninf nsz float %23
  %35 = getelementptr i8, ptr %19, i64 40
  %36 = getelementptr i8, ptr %19, i64 36
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %648, %for_loop_body ]
  %37 = load ptr, ptr %3, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 32872
  %39 = load ptr, ptr %38, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 4
  %41 = load i32, ptr %40, align 4
  %42 = sdiv i32 %.05, %41
  %43 = mul i32 %42, %41
  %44 = xor i32 %41, %.05
  %45 = icmp slt i32 %44, 0
  %46 = icmp ne i32 %.05, %43
  %47 = and i1 %45, %46
  %.neg4 = sext i1 %47 to i32
  %48 = add i32 %42, %.neg4
  %49 = mul i32 %41, -1
  %50 = mul i32 %49, %48
  %51 = add i32 %.05, %50
  %52 = load ptr, ptr %30, align 8
  %53 = load i32, ptr %31, align 4
  %54 = sub i32 %53, %41
  %55 = mul i32 %54, %48
  %56 = add i32 %.05, %55
  %57 = sext i32 %56 to i64
  %58 = getelementptr float, ptr %52, i64 %57
  %59 = load float, ptr %58, align 4
  %60 = add i32 %48, -2
  %61 = getelementptr inbounds nuw i8, ptr %39, i64 8
  %62 = load i32, ptr %61, align 4
  %63 = add i32 %62, -1
  %64 = tail call i32 @llvm.smax.i32(i32 %60, i32 0)
  %65 = tail call i32 @llvm.smin.i32(i32 %63, i32 %64)
  %66 = add i32 %51, -2
  %67 = getelementptr inbounds nuw i8, ptr %39, i64 12
  %68 = load i32, ptr %67, align 4
  %69 = add i32 %68, -1
  %70 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %71 = tail call i32 @llvm.smin.i32(i32 %69, i32 %70)
  %72 = mul i32 %65, %53
  %73 = add i32 %71, %72
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, ptr %52, i64 %74
  %76 = load float, ptr %75, align 4
  %77 = fsub reassoc ninf nsz float %76, %59
  %78 = fmul reassoc ninf nsz float %77, %77
  %79 = fmul reassoc ninf nsz float %78, %23
  %80 = fsub reassoc ninf nsz float %24, %79
  %81 = tail call noundef float @expf(float noundef %80) #7
  %82 = load ptr, ptr %32, align 8
  %83 = load i32, ptr %33, align 4
  %84 = mul i32 %83, %65
  %85 = add i32 %84, %71
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %82, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = fmul reassoc ninf nsz float %88, %81
  %90 = fadd reassoc ninf nsz float %81, 0x3D71979980000000
  %91 = add i32 %51, -1
  %92 = tail call i32 @llvm.smax.i32(i32 %91, i32 0)
  %93 = tail call i32 @llvm.smin.i32(i32 %69, i32 %92)
  %94 = load ptr, ptr %30, align 8
  %95 = load i32, ptr %31, align 4
  %96 = mul i32 %95, %65
  %97 = add i32 %96, %93
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %94, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = fsub reassoc ninf nsz float %100, %59
  %102 = fmul reassoc ninf nsz float %101, %101
  %103 = fmul reassoc ninf nsz float %102, %23
  %104 = fsub reassoc ninf nsz float %25, %103
  %105 = tail call noundef float @expf(float noundef %104) #7
  %106 = load ptr, ptr %32, align 8
  %107 = load i32, ptr %33, align 4
  %108 = mul i32 %107, %65
  %109 = add i32 %108, %93
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %106, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = fmul reassoc ninf nsz float %112, %105
  %114 = fadd reassoc ninf nsz float %113, %89
  %115 = fadd reassoc ninf nsz float %90, %105
  %116 = tail call i32 @llvm.smax.i32(i32 %51, i32 0)
  %117 = tail call i32 @llvm.smin.i32(i32 %69, i32 %116)
  %118 = load ptr, ptr %30, align 8
  %119 = load i32, ptr %31, align 4
  %120 = mul i32 %119, %65
  %121 = add i32 %120, %117
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %118, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = fsub reassoc ninf nsz float %124, %59
  %126 = fmul reassoc ninf nsz float %125, %125
  %127 = fmul reassoc ninf nsz float %126, %23
  %128 = fsub reassoc ninf nsz float %26, %127
  %129 = tail call noundef float @expf(float noundef %128) #7
  %130 = load ptr, ptr %32, align 8
  %131 = load i32, ptr %33, align 4
  %132 = mul i32 %131, %65
  %133 = add i32 %132, %117
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %130, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = fmul reassoc ninf nsz float %136, %129
  %138 = fadd reassoc ninf nsz float %114, %137
  %139 = fadd reassoc ninf nsz float %115, %129
  %140 = add i32 %51, 1
  %141 = tail call i32 @llvm.smax.i32(i32 %140, i32 0)
  %142 = tail call i32 @llvm.smin.i32(i32 %69, i32 %141)
  %143 = load ptr, ptr %30, align 8
  %144 = load i32, ptr %31, align 4
  %145 = mul i32 %144, %65
  %146 = add i32 %145, %142
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %143, i64 %147
  %149 = load float, ptr %148, align 4
  %150 = fsub reassoc ninf nsz float %149, %59
  %151 = fmul reassoc ninf nsz float %150, %150
  %152 = fmul reassoc ninf nsz float %151, %23
  %153 = fsub reassoc ninf nsz float %25, %152
  %154 = tail call noundef float @expf(float noundef %153) #7
  %155 = load ptr, ptr %32, align 8
  %156 = load i32, ptr %33, align 4
  %157 = mul i32 %156, %65
  %158 = add i32 %157, %142
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %155, i64 %159
  %161 = load float, ptr %160, align 4
  %162 = fmul reassoc ninf nsz float %161, %154
  %163 = fadd reassoc ninf nsz float %138, %162
  %164 = fadd reassoc ninf nsz float %139, %154
  %165 = add i32 %51, 2
  %166 = tail call i32 @llvm.smax.i32(i32 %165, i32 0)
  %167 = tail call i32 @llvm.smin.i32(i32 %69, i32 %166)
  %168 = load ptr, ptr %30, align 8
  %169 = load i32, ptr %31, align 4
  %170 = mul i32 %169, %65
  %171 = add i32 %170, %167
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %168, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = fsub reassoc ninf nsz float %174, %59
  %176 = fmul reassoc ninf nsz float %175, %175
  %177 = fmul reassoc ninf nsz float %176, %23
  %178 = fsub reassoc ninf nsz float %24, %177
  %179 = tail call noundef float @expf(float noundef %178) #7
  %180 = load ptr, ptr %32, align 8
  %181 = load i32, ptr %33, align 4
  %182 = mul i32 %181, %65
  %183 = add i32 %182, %167
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, ptr %180, i64 %184
  %186 = load float, ptr %185, align 4
  %187 = fmul reassoc ninf nsz float %186, %179
  %188 = fadd reassoc ninf nsz float %163, %187
  %189 = fadd reassoc ninf nsz float %164, %179
  %190 = add i32 %48, -1
  %191 = tail call i32 @llvm.smax.i32(i32 %190, i32 0)
  %192 = tail call i32 @llvm.smin.i32(i32 %63, i32 %191)
  %193 = load ptr, ptr %30, align 8
  %194 = load i32, ptr %31, align 4
  %195 = mul i32 %194, %192
  %196 = add i32 %195, %71
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %193, i64 %197
  %199 = load float, ptr %198, align 4
  %200 = fsub reassoc ninf nsz float %199, %59
  %201 = fmul reassoc ninf nsz float %200, %200
  %202 = fmul reassoc ninf nsz float %201, %23
  %203 = fsub reassoc ninf nsz float %25, %202
  %204 = tail call noundef float @expf(float noundef %203) #7
  %205 = load ptr, ptr %32, align 8
  %206 = load i32, ptr %33, align 4
  %207 = mul i32 %206, %192
  %208 = add i32 %207, %71
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, ptr %205, i64 %209
  %211 = load float, ptr %210, align 4
  %212 = fmul reassoc ninf nsz float %211, %204
  %213 = fadd reassoc ninf nsz float %188, %212
  %214 = fadd reassoc ninf nsz float %189, %204
  %215 = load ptr, ptr %30, align 8
  %216 = load i32, ptr %31, align 4
  %217 = mul i32 %216, %192
  %218 = add i32 %217, %93
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, ptr %215, i64 %219
  %221 = load float, ptr %220, align 4
  %222 = fsub reassoc ninf nsz float %221, %59
  %223 = fmul reassoc ninf nsz float %222, %222
  %224 = fmul reassoc ninf nsz float %223, %23
  %225 = fsub reassoc ninf nsz float %27, %224
  %226 = tail call noundef float @expf(float noundef %225) #7
  %227 = load ptr, ptr %32, align 8
  %228 = load i32, ptr %33, align 4
  %229 = mul i32 %228, %192
  %230 = add i32 %229, %93
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, ptr %227, i64 %231
  %233 = load float, ptr %232, align 4
  %234 = fmul reassoc ninf nsz float %233, %226
  %235 = fadd reassoc ninf nsz float %213, %234
  %236 = fadd reassoc ninf nsz float %214, %226
  %237 = load ptr, ptr %30, align 8
  %238 = load i32, ptr %31, align 4
  %239 = mul i32 %238, %192
  %240 = add i32 %239, %117
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %237, i64 %241
  %243 = load float, ptr %242, align 4
  %244 = fsub reassoc ninf nsz float %243, %59
  %245 = fmul reassoc ninf nsz float %244, %244
  %246 = fmul reassoc ninf nsz float %245, %23
  %247 = fsub reassoc ninf nsz float %28, %246
  %248 = tail call noundef float @expf(float noundef %247) #7
  %249 = load ptr, ptr %32, align 8
  %250 = load i32, ptr %33, align 4
  %251 = mul i32 %250, %192
  %252 = add i32 %251, %117
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, ptr %249, i64 %253
  %255 = load float, ptr %254, align 4
  %256 = fmul reassoc ninf nsz float %255, %248
  %257 = fadd reassoc ninf nsz float %235, %256
  %258 = fadd reassoc ninf nsz float %236, %248
  %259 = load ptr, ptr %30, align 8
  %260 = load i32, ptr %31, align 4
  %261 = mul i32 %260, %192
  %262 = add i32 %261, %142
  %263 = sext i32 %262 to i64
  %264 = getelementptr float, ptr %259, i64 %263
  %265 = load float, ptr %264, align 4
  %266 = fsub reassoc ninf nsz float %265, %59
  %267 = fmul reassoc ninf nsz float %266, %266
  %268 = fmul reassoc ninf nsz float %267, %23
  %269 = fsub reassoc ninf nsz float %27, %268
  %270 = tail call noundef float @expf(float noundef %269) #7
  %271 = load ptr, ptr %32, align 8
  %272 = load i32, ptr %33, align 4
  %273 = mul i32 %272, %192
  %274 = add i32 %273, %142
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, ptr %271, i64 %275
  %277 = load float, ptr %276, align 4
  %278 = fmul reassoc ninf nsz float %277, %270
  %279 = fadd reassoc ninf nsz float %257, %278
  %280 = fadd reassoc ninf nsz float %258, %270
  %281 = load ptr, ptr %30, align 8
  %282 = load i32, ptr %31, align 4
  %283 = mul i32 %282, %192
  %284 = add i32 %283, %167
  %285 = sext i32 %284 to i64
  %286 = getelementptr float, ptr %281, i64 %285
  %287 = load float, ptr %286, align 4
  %288 = fsub reassoc ninf nsz float %287, %59
  %289 = fmul reassoc ninf nsz float %288, %288
  %290 = fmul reassoc ninf nsz float %289, %23
  %291 = fsub reassoc ninf nsz float %25, %290
  %292 = tail call noundef float @expf(float noundef %291) #7
  %293 = load ptr, ptr %32, align 8
  %294 = load i32, ptr %33, align 4
  %295 = mul i32 %294, %192
  %296 = add i32 %295, %167
  %297 = sext i32 %296 to i64
  %298 = getelementptr float, ptr %293, i64 %297
  %299 = load float, ptr %298, align 4
  %300 = fmul reassoc ninf nsz float %299, %292
  %301 = fadd reassoc ninf nsz float %279, %300
  %302 = fadd reassoc ninf nsz float %280, %292
  %303 = tail call i32 @llvm.smax.i32(i32 %48, i32 0)
  %304 = tail call i32 @llvm.smin.i32(i32 %63, i32 %303)
  %305 = load ptr, ptr %30, align 8
  %306 = load i32, ptr %31, align 4
  %307 = mul i32 %306, %304
  %308 = add i32 %307, %71
  %309 = sext i32 %308 to i64
  %310 = getelementptr float, ptr %305, i64 %309
  %311 = load float, ptr %310, align 4
  %312 = fsub reassoc ninf nsz float %311, %59
  %313 = fmul reassoc ninf nsz float %312, %312
  %314 = fmul reassoc ninf nsz float %313, %23
  %315 = fsub reassoc ninf nsz float %26, %314
  %316 = tail call noundef float @expf(float noundef %315) #7
  %317 = load ptr, ptr %32, align 8
  %318 = load i32, ptr %33, align 4
  %319 = mul i32 %318, %304
  %320 = add i32 %319, %71
  %321 = sext i32 %320 to i64
  %322 = getelementptr float, ptr %317, i64 %321
  %323 = load float, ptr %322, align 4
  %324 = fmul reassoc ninf nsz float %323, %316
  %325 = fadd reassoc ninf nsz float %301, %324
  %326 = fadd reassoc ninf nsz float %302, %316
  %327 = load ptr, ptr %30, align 8
  %328 = load i32, ptr %31, align 4
  %329 = mul i32 %328, %304
  %330 = add i32 %329, %93
  %331 = sext i32 %330 to i64
  %332 = getelementptr float, ptr %327, i64 %331
  %333 = load float, ptr %332, align 4
  %334 = fsub reassoc ninf nsz float %333, %59
  %335 = fmul reassoc ninf nsz float %334, %334
  %336 = fmul reassoc ninf nsz float %335, %23
  %337 = fsub reassoc ninf nsz float %28, %336
  %338 = tail call noundef float @expf(float noundef %337) #7
  %339 = load ptr, ptr %32, align 8
  %340 = load i32, ptr %33, align 4
  %341 = mul i32 %340, %304
  %342 = add i32 %341, %93
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, ptr %339, i64 %343
  %345 = load float, ptr %344, align 4
  %346 = fmul reassoc ninf nsz float %345, %338
  %347 = fadd reassoc ninf nsz float %325, %346
  %348 = fadd reassoc ninf nsz float %326, %338
  %349 = load ptr, ptr %30, align 8
  %350 = load i32, ptr %31, align 4
  %351 = mul i32 %350, %304
  %352 = add i32 %351, %117
  %353 = sext i32 %352 to i64
  %354 = getelementptr float, ptr %349, i64 %353
  %355 = load float, ptr %354, align 4
  %356 = fsub reassoc ninf nsz float %355, %59
  %357 = fmul reassoc ninf nsz float %356, %356
  %358 = fmul reassoc ninf nsz float %357, %34
  %359 = tail call noundef float @expf(float noundef %358) #7
  %360 = load ptr, ptr %32, align 8
  %361 = load i32, ptr %33, align 4
  %362 = mul i32 %361, %304
  %363 = add i32 %362, %117
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, ptr %360, i64 %364
  %366 = load float, ptr %365, align 4
  %367 = fmul reassoc ninf nsz float %366, %359
  %368 = fadd reassoc ninf nsz float %347, %367
  %369 = fadd reassoc ninf nsz float %348, %359
  %370 = load ptr, ptr %30, align 8
  %371 = load i32, ptr %31, align 4
  %372 = mul i32 %371, %304
  %373 = add i32 %372, %142
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, ptr %370, i64 %374
  %376 = load float, ptr %375, align 4
  %377 = fsub reassoc ninf nsz float %376, %59
  %378 = fmul reassoc ninf nsz float %377, %377
  %379 = fmul reassoc ninf nsz float %378, %23
  %380 = fsub reassoc ninf nsz float %28, %379
  %381 = tail call noundef float @expf(float noundef %380) #7
  %382 = load ptr, ptr %32, align 8
  %383 = load i32, ptr %33, align 4
  %384 = mul i32 %383, %304
  %385 = add i32 %384, %142
  %386 = sext i32 %385 to i64
  %387 = getelementptr float, ptr %382, i64 %386
  %388 = load float, ptr %387, align 4
  %389 = fmul reassoc ninf nsz float %388, %381
  %390 = fadd reassoc ninf nsz float %368, %389
  %391 = fadd reassoc ninf nsz float %369, %381
  %392 = load ptr, ptr %30, align 8
  %393 = load i32, ptr %31, align 4
  %394 = mul i32 %393, %304
  %395 = add i32 %394, %167
  %396 = sext i32 %395 to i64
  %397 = getelementptr float, ptr %392, i64 %396
  %398 = load float, ptr %397, align 4
  %399 = fsub reassoc ninf nsz float %398, %59
  %400 = fmul reassoc ninf nsz float %399, %399
  %401 = fmul reassoc ninf nsz float %400, %23
  %402 = fsub reassoc ninf nsz float %26, %401
  %403 = tail call noundef float @expf(float noundef %402) #7
  %404 = load ptr, ptr %32, align 8
  %405 = load i32, ptr %33, align 4
  %406 = mul i32 %405, %304
  %407 = add i32 %406, %167
  %408 = sext i32 %407 to i64
  %409 = getelementptr float, ptr %404, i64 %408
  %410 = load float, ptr %409, align 4
  %411 = fmul reassoc ninf nsz float %410, %403
  %412 = fadd reassoc ninf nsz float %390, %411
  %413 = fadd reassoc ninf nsz float %391, %403
  %414 = add i32 %48, 1
  %415 = tail call i32 @llvm.smax.i32(i32 %414, i32 0)
  %416 = tail call i32 @llvm.smin.i32(i32 %63, i32 %415)
  %417 = load ptr, ptr %30, align 8
  %418 = load i32, ptr %31, align 4
  %419 = mul i32 %418, %416
  %420 = add i32 %419, %71
  %421 = sext i32 %420 to i64
  %422 = getelementptr float, ptr %417, i64 %421
  %423 = load float, ptr %422, align 4
  %424 = fsub reassoc ninf nsz float %423, %59
  %425 = fmul reassoc ninf nsz float %424, %424
  %426 = fmul reassoc ninf nsz float %425, %23
  %427 = fsub reassoc ninf nsz float %25, %426
  %428 = tail call noundef float @expf(float noundef %427) #7
  %429 = load ptr, ptr %32, align 8
  %430 = load i32, ptr %33, align 4
  %431 = mul i32 %430, %416
  %432 = add i32 %431, %71
  %433 = sext i32 %432 to i64
  %434 = getelementptr float, ptr %429, i64 %433
  %435 = load float, ptr %434, align 4
  %436 = fmul reassoc ninf nsz float %435, %428
  %437 = fadd reassoc ninf nsz float %412, %436
  %438 = fadd reassoc ninf nsz float %413, %428
  %439 = load ptr, ptr %30, align 8
  %440 = load i32, ptr %31, align 4
  %441 = mul i32 %440, %416
  %442 = add i32 %441, %93
  %443 = sext i32 %442 to i64
  %444 = getelementptr float, ptr %439, i64 %443
  %445 = load float, ptr %444, align 4
  %446 = fsub reassoc ninf nsz float %445, %59
  %447 = fmul reassoc ninf nsz float %446, %446
  %448 = fmul reassoc ninf nsz float %447, %23
  %449 = fsub reassoc ninf nsz float %27, %448
  %450 = tail call noundef float @expf(float noundef %449) #7
  %451 = load ptr, ptr %32, align 8
  %452 = load i32, ptr %33, align 4
  %453 = mul i32 %452, %416
  %454 = add i32 %453, %93
  %455 = sext i32 %454 to i64
  %456 = getelementptr float, ptr %451, i64 %455
  %457 = load float, ptr %456, align 4
  %458 = fmul reassoc ninf nsz float %457, %450
  %459 = fadd reassoc ninf nsz float %437, %458
  %460 = fadd reassoc ninf nsz float %438, %450
  %461 = load ptr, ptr %30, align 8
  %462 = load i32, ptr %31, align 4
  %463 = mul i32 %462, %416
  %464 = add i32 %463, %117
  %465 = sext i32 %464 to i64
  %466 = getelementptr float, ptr %461, i64 %465
  %467 = load float, ptr %466, align 4
  %468 = fsub reassoc ninf nsz float %467, %59
  %469 = fmul reassoc ninf nsz float %468, %468
  %470 = fmul reassoc ninf nsz float %469, %23
  %471 = fsub reassoc ninf nsz float %28, %470
  %472 = tail call noundef float @expf(float noundef %471) #7
  %473 = load ptr, ptr %32, align 8
  %474 = load i32, ptr %33, align 4
  %475 = mul i32 %474, %416
  %476 = add i32 %475, %117
  %477 = sext i32 %476 to i64
  %478 = getelementptr float, ptr %473, i64 %477
  %479 = load float, ptr %478, align 4
  %480 = fmul reassoc ninf nsz float %479, %472
  %481 = fadd reassoc ninf nsz float %459, %480
  %482 = fadd reassoc ninf nsz float %460, %472
  %483 = load ptr, ptr %30, align 8
  %484 = load i32, ptr %31, align 4
  %485 = mul i32 %484, %416
  %486 = add i32 %485, %142
  %487 = sext i32 %486 to i64
  %488 = getelementptr float, ptr %483, i64 %487
  %489 = load float, ptr %488, align 4
  %490 = fsub reassoc ninf nsz float %489, %59
  %491 = fmul reassoc ninf nsz float %490, %490
  %492 = fmul reassoc ninf nsz float %491, %23
  %493 = fsub reassoc ninf nsz float %27, %492
  %494 = tail call noundef float @expf(float noundef %493) #7
  %495 = load ptr, ptr %32, align 8
  %496 = load i32, ptr %33, align 4
  %497 = mul i32 %496, %416
  %498 = add i32 %497, %142
  %499 = sext i32 %498 to i64
  %500 = getelementptr float, ptr %495, i64 %499
  %501 = load float, ptr %500, align 4
  %502 = fmul reassoc ninf nsz float %501, %494
  %503 = fadd reassoc ninf nsz float %481, %502
  %504 = fadd reassoc ninf nsz float %482, %494
  %505 = load ptr, ptr %30, align 8
  %506 = load i32, ptr %31, align 4
  %507 = mul i32 %506, %416
  %508 = add i32 %507, %167
  %509 = sext i32 %508 to i64
  %510 = getelementptr float, ptr %505, i64 %509
  %511 = load float, ptr %510, align 4
  %512 = fsub reassoc ninf nsz float %511, %59
  %513 = fmul reassoc ninf nsz float %512, %512
  %514 = fmul reassoc ninf nsz float %513, %23
  %515 = fsub reassoc ninf nsz float %25, %514
  %516 = tail call noundef float @expf(float noundef %515) #7
  %517 = load ptr, ptr %32, align 8
  %518 = load i32, ptr %33, align 4
  %519 = mul i32 %518, %416
  %520 = add i32 %519, %167
  %521 = sext i32 %520 to i64
  %522 = getelementptr float, ptr %517, i64 %521
  %523 = load float, ptr %522, align 4
  %524 = fmul reassoc ninf nsz float %523, %516
  %525 = fadd reassoc ninf nsz float %503, %524
  %526 = fadd reassoc ninf nsz float %504, %516
  %527 = add i32 %48, 2
  %528 = tail call i32 @llvm.smax.i32(i32 %527, i32 0)
  %529 = tail call i32 @llvm.smin.i32(i32 %63, i32 %528)
  %530 = load ptr, ptr %30, align 8
  %531 = load i32, ptr %31, align 4
  %532 = mul i32 %531, %529
  %533 = add i32 %532, %71
  %534 = sext i32 %533 to i64
  %535 = getelementptr float, ptr %530, i64 %534
  %536 = load float, ptr %535, align 4
  %537 = fsub reassoc ninf nsz float %536, %59
  %538 = fmul reassoc ninf nsz float %537, %537
  %539 = fmul reassoc ninf nsz float %538, %23
  %540 = fsub reassoc ninf nsz float %24, %539
  %541 = tail call noundef float @expf(float noundef %540) #7
  %542 = load ptr, ptr %32, align 8
  %543 = load i32, ptr %33, align 4
  %544 = mul i32 %543, %529
  %545 = add i32 %544, %71
  %546 = sext i32 %545 to i64
  %547 = getelementptr float, ptr %542, i64 %546
  %548 = load float, ptr %547, align 4
  %549 = fmul reassoc ninf nsz float %548, %541
  %550 = fadd reassoc ninf nsz float %525, %549
  %551 = fadd reassoc ninf nsz float %526, %541
  %552 = load ptr, ptr %30, align 8
  %553 = load i32, ptr %31, align 4
  %554 = mul i32 %553, %529
  %555 = add i32 %554, %93
  %556 = sext i32 %555 to i64
  %557 = getelementptr float, ptr %552, i64 %556
  %558 = load float, ptr %557, align 4
  %559 = fsub reassoc ninf nsz float %558, %59
  %560 = fmul reassoc ninf nsz float %559, %559
  %561 = fmul reassoc ninf nsz float %560, %23
  %562 = fsub reassoc ninf nsz float %25, %561
  %563 = tail call noundef float @expf(float noundef %562) #7
  %564 = load ptr, ptr %32, align 8
  %565 = load i32, ptr %33, align 4
  %566 = mul i32 %565, %529
  %567 = add i32 %566, %93
  %568 = sext i32 %567 to i64
  %569 = getelementptr float, ptr %564, i64 %568
  %570 = load float, ptr %569, align 4
  %571 = fmul reassoc ninf nsz float %570, %563
  %572 = fadd reassoc ninf nsz float %550, %571
  %573 = fadd reassoc ninf nsz float %551, %563
  %574 = load ptr, ptr %30, align 8
  %575 = load i32, ptr %31, align 4
  %576 = mul i32 %575, %529
  %577 = add i32 %576, %117
  %578 = sext i32 %577 to i64
  %579 = getelementptr float, ptr %574, i64 %578
  %580 = load float, ptr %579, align 4
  %581 = fsub reassoc ninf nsz float %580, %59
  %582 = fmul reassoc ninf nsz float %581, %581
  %583 = fmul reassoc ninf nsz float %582, %23
  %584 = fsub reassoc ninf nsz float %26, %583
  %585 = tail call noundef float @expf(float noundef %584) #7
  %586 = load ptr, ptr %32, align 8
  %587 = load i32, ptr %33, align 4
  %588 = mul i32 %587, %529
  %589 = add i32 %588, %117
  %590 = sext i32 %589 to i64
  %591 = getelementptr float, ptr %586, i64 %590
  %592 = load float, ptr %591, align 4
  %593 = fmul reassoc ninf nsz float %592, %585
  %594 = fadd reassoc ninf nsz float %572, %593
  %595 = fadd reassoc ninf nsz float %573, %585
  %596 = load ptr, ptr %30, align 8
  %597 = load i32, ptr %31, align 4
  %598 = mul i32 %597, %529
  %599 = add i32 %598, %142
  %600 = sext i32 %599 to i64
  %601 = getelementptr float, ptr %596, i64 %600
  %602 = load float, ptr %601, align 4
  %603 = fsub reassoc ninf nsz float %602, %59
  %604 = fmul reassoc ninf nsz float %603, %603
  %605 = fmul reassoc ninf nsz float %604, %23
  %606 = fsub reassoc ninf nsz float %25, %605
  %607 = tail call noundef float @expf(float noundef %606) #7
  %608 = load ptr, ptr %32, align 8
  %609 = load i32, ptr %33, align 4
  %610 = mul i32 %609, %529
  %611 = add i32 %610, %142
  %612 = sext i32 %611 to i64
  %613 = getelementptr float, ptr %608, i64 %612
  %614 = load float, ptr %613, align 4
  %615 = fmul reassoc ninf nsz float %614, %607
  %616 = fadd reassoc ninf nsz float %594, %615
  %617 = fadd reassoc ninf nsz float %595, %607
  %618 = load ptr, ptr %30, align 8
  %619 = load i32, ptr %31, align 4
  %620 = mul i32 %619, %529
  %621 = add i32 %620, %167
  %622 = sext i32 %621 to i64
  %623 = getelementptr float, ptr %618, i64 %622
  %624 = load float, ptr %623, align 4
  %625 = fsub reassoc ninf nsz float %624, %59
  %626 = fmul reassoc ninf nsz float %625, %625
  %627 = fmul reassoc ninf nsz float %626, %23
  %628 = fsub reassoc ninf nsz float %24, %627
  %629 = tail call noundef float @expf(float noundef %628) #7
  %630 = load ptr, ptr %32, align 8
  %631 = load i32, ptr %33, align 4
  %632 = mul i32 %631, %529
  %633 = add i32 %632, %167
  %634 = sext i32 %633 to i64
  %635 = getelementptr float, ptr %630, i64 %634
  %636 = load float, ptr %635, align 4
  %637 = fmul reassoc ninf nsz float %636, %629
  %638 = fadd reassoc ninf nsz float %616, %637
  %639 = fadd reassoc ninf nsz float %617, %629
  %640 = fdiv reassoc ninf nsz float %638, %639
  %641 = load ptr, ptr %35, align 8
  %642 = load i32, ptr %36, align 4
  %643 = sub i32 %642, %41
  %644 = mul i32 %643, %48
  %645 = add i32 %.05, %644
  %646 = sext i32 %645 to i64
  %647 = getelementptr float, ptr %641, i64 %646
  store float %640, ptr %647, align 4
  %648 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %18, %648
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
