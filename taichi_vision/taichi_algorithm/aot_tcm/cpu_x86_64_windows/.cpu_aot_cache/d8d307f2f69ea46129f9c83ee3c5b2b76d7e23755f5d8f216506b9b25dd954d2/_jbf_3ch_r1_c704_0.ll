; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jbf_3ch_r1_c704_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_jbf_3ch_r1_c704_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %34 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %34, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %418, %for_loop_body ]
  %35 = load ptr, ptr %3, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 32872
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 4
  %39 = load i32, ptr %38, align 4
  %40 = sdiv i32 %.05, %39
  %41 = mul i32 %40, %39
  %42 = xor i32 %39, %.05
  %43 = icmp slt i32 %42, 0
  %44 = icmp ne i32 %.05, %41
  %45 = and i1 %43, %44
  %.neg4 = sext i1 %45 to i32
  %46 = add i32 %40, %.neg4
  %47 = mul i32 %39, -1
  %48 = mul i32 %47, %46
  %49 = add i32 %.05, %48
  %50 = load ptr, ptr %27, align 8
  %51 = load i32, ptr %28, align 4
  %52 = sub i32 %51, %39
  %53 = mul i32 %52, %46
  %54 = add i32 %.05, %53
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, ptr %50, i64 %55
  %57 = load float, ptr %56, align 4
  %58 = add i32 %46, -1
  %59 = getelementptr inbounds nuw i8, ptr %37, i64 8
  %60 = load i32, ptr %59, align 4
  %61 = add i32 %60, -1
  %62 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %63 = tail call i32 @llvm.smin.i32(i32 %61, i32 %62)
  %64 = add i32 %49, -1
  %65 = getelementptr inbounds nuw i8, ptr %37, i64 12
  %66 = load i32, ptr %65, align 4
  %67 = add i32 %66, -1
  %68 = tail call i32 @llvm.smax.i32(i32 %64, i32 0)
  %69 = tail call i32 @llvm.smin.i32(i32 %67, i32 %68)
  %70 = mul i32 %63, %51
  %71 = add i32 %69, %70
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, ptr %50, i64 %72
  %74 = load float, ptr %73, align 4
  %75 = fsub reassoc ninf nsz float %74, %57
  %76 = fmul reassoc ninf nsz float %75, %75
  %77 = fmul reassoc ninf nsz float %76, %23
  %78 = fsub reassoc ninf nsz float %24, %77
  %79 = tail call noundef float @expf(float noundef %78) #7
  %80 = load ptr, ptr %29, align 8
  %81 = load i32, ptr %30, align 4
  %82 = mul i32 %81, %63
  %83 = add i32 %82, %69
  %84 = mul i32 %83, 3
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, ptr %80, i64 %85
  %87 = load float, ptr %86, align 4
  %88 = add i32 %84, 1
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, ptr %80, i64 %89
  %91 = load float, ptr %90, align 4
  %92 = add i32 %84, 2
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %80, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = fmul reassoc ninf nsz float %87, %79
  %97 = fmul reassoc ninf nsz float %91, %79
  %98 = fmul reassoc ninf nsz float %95, %79
  %99 = fadd reassoc ninf nsz float %79, 0x3D71979980000000
  %100 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %101 = tail call i32 @llvm.smin.i32(i32 %67, i32 %100)
  %102 = load ptr, ptr %27, align 8
  %103 = load i32, ptr %28, align 4
  %104 = mul i32 %103, %63
  %105 = add i32 %104, %101
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %102, i64 %106
  %108 = load float, ptr %107, align 4
  %109 = fsub reassoc ninf nsz float %108, %57
  %110 = fmul reassoc ninf nsz float %109, %109
  %111 = fmul reassoc ninf nsz float %110, %23
  %112 = fsub reassoc ninf nsz float %25, %111
  %113 = tail call noundef float @expf(float noundef %112) #7
  %114 = load ptr, ptr %29, align 8
  %115 = load i32, ptr %30, align 4
  %116 = mul i32 %115, %63
  %117 = add i32 %116, %101
  %118 = mul i32 %117, 3
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %114, i64 %119
  %121 = load float, ptr %120, align 4
  %122 = add i32 %118, 1
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, ptr %114, i64 %123
  %125 = load float, ptr %124, align 4
  %126 = add i32 %118, 2
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %114, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = fmul reassoc ninf nsz float %121, %113
  %131 = fmul reassoc ninf nsz float %125, %113
  %132 = fmul reassoc ninf nsz float %129, %113
  %133 = fadd reassoc ninf nsz float %130, %96
  %134 = fadd reassoc ninf nsz float %131, %97
  %135 = fadd reassoc ninf nsz float %132, %98
  %136 = fadd reassoc ninf nsz float %99, %113
  %137 = add i32 %49, 1
  %138 = tail call i32 @llvm.smax.i32(i32 %137, i32 0)
  %139 = tail call i32 @llvm.smin.i32(i32 %67, i32 %138)
  %140 = load ptr, ptr %27, align 8
  %141 = load i32, ptr %28, align 4
  %142 = mul i32 %141, %63
  %143 = add i32 %142, %139
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %140, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = fsub reassoc ninf nsz float %146, %57
  %148 = fmul reassoc ninf nsz float %147, %147
  %149 = fmul reassoc ninf nsz float %148, %23
  %150 = fsub reassoc ninf nsz float %24, %149
  %151 = tail call noundef float @expf(float noundef %150) #7
  %152 = load ptr, ptr %29, align 8
  %153 = load i32, ptr %30, align 4
  %154 = mul i32 %153, %63
  %155 = add i32 %154, %139
  %156 = mul i32 %155, 3
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %152, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = add i32 %156, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %152, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = add i32 %156, 2
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %152, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = fmul reassoc ninf nsz float %159, %151
  %169 = fmul reassoc ninf nsz float %163, %151
  %170 = fmul reassoc ninf nsz float %167, %151
  %171 = fadd reassoc ninf nsz float %133, %168
  %172 = fadd reassoc ninf nsz float %134, %169
  %173 = fadd reassoc ninf nsz float %135, %170
  %174 = fadd reassoc ninf nsz float %136, %151
  %175 = tail call i32 @llvm.smax.i32(i32 %46, i32 0)
  %176 = tail call i32 @llvm.smin.i32(i32 %61, i32 %175)
  %177 = load ptr, ptr %27, align 8
  %178 = load i32, ptr %28, align 4
  %179 = mul i32 %178, %176
  %180 = add i32 %179, %69
  %181 = sext i32 %180 to i64
  %182 = getelementptr float, ptr %177, i64 %181
  %183 = load float, ptr %182, align 4
  %184 = fsub reassoc ninf nsz float %183, %57
  %185 = fmul reassoc ninf nsz float %184, %184
  %186 = fmul reassoc ninf nsz float %185, %23
  %187 = fsub reassoc ninf nsz float %25, %186
  %188 = tail call noundef float @expf(float noundef %187) #7
  %189 = load ptr, ptr %29, align 8
  %190 = load i32, ptr %30, align 4
  %191 = mul i32 %190, %176
  %192 = add i32 %191, %69
  %193 = mul i32 %192, 3
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, ptr %189, i64 %194
  %196 = load float, ptr %195, align 4
  %197 = add i32 %193, 1
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %189, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = add i32 %193, 2
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %189, i64 %202
  %204 = load float, ptr %203, align 4
  %205 = fmul reassoc ninf nsz float %196, %188
  %206 = fmul reassoc ninf nsz float %200, %188
  %207 = fmul reassoc ninf nsz float %204, %188
  %208 = fadd reassoc ninf nsz float %171, %205
  %209 = fadd reassoc ninf nsz float %172, %206
  %210 = fadd reassoc ninf nsz float %173, %207
  %211 = fadd reassoc ninf nsz float %174, %188
  %212 = load ptr, ptr %27, align 8
  %213 = load i32, ptr %28, align 4
  %214 = mul i32 %213, %176
  %215 = add i32 %214, %101
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, ptr %212, i64 %216
  %218 = load float, ptr %217, align 4
  %219 = fsub reassoc ninf nsz float %218, %57
  %220 = fmul reassoc ninf nsz float %219, %219
  %221 = fmul reassoc ninf nsz float %220, %31
  %222 = tail call noundef float @expf(float noundef %221) #7
  %223 = load ptr, ptr %29, align 8
  %224 = load i32, ptr %30, align 4
  %225 = mul i32 %224, %176
  %226 = add i32 %225, %101
  %227 = mul i32 %226, 3
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, ptr %223, i64 %228
  %230 = load float, ptr %229, align 4
  %231 = add i32 %227, 1
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, ptr %223, i64 %232
  %234 = load float, ptr %233, align 4
  %235 = add i32 %227, 2
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, ptr %223, i64 %236
  %238 = load float, ptr %237, align 4
  %239 = fmul reassoc ninf nsz float %230, %222
  %240 = fmul reassoc ninf nsz float %234, %222
  %241 = fmul reassoc ninf nsz float %238, %222
  %242 = fadd reassoc ninf nsz float %208, %239
  %243 = fadd reassoc ninf nsz float %209, %240
  %244 = fadd reassoc ninf nsz float %210, %241
  %245 = fadd reassoc ninf nsz float %211, %222
  %246 = load ptr, ptr %27, align 8
  %247 = load i32, ptr %28, align 4
  %248 = mul i32 %247, %176
  %249 = add i32 %248, %139
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, ptr %246, i64 %250
  %252 = load float, ptr %251, align 4
  %253 = fsub reassoc ninf nsz float %252, %57
  %254 = fmul reassoc ninf nsz float %253, %253
  %255 = fmul reassoc ninf nsz float %254, %23
  %256 = fsub reassoc ninf nsz float %25, %255
  %257 = tail call noundef float @expf(float noundef %256) #7
  %258 = load ptr, ptr %29, align 8
  %259 = load i32, ptr %30, align 4
  %260 = mul i32 %259, %176
  %261 = add i32 %260, %139
  %262 = mul i32 %261, 3
  %263 = sext i32 %262 to i64
  %264 = getelementptr float, ptr %258, i64 %263
  %265 = load float, ptr %264, align 4
  %266 = add i32 %262, 1
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, ptr %258, i64 %267
  %269 = load float, ptr %268, align 4
  %270 = add i32 %262, 2
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %258, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = fmul reassoc ninf nsz float %265, %257
  %275 = fmul reassoc ninf nsz float %269, %257
  %276 = fmul reassoc ninf nsz float %273, %257
  %277 = fadd reassoc ninf nsz float %242, %274
  %278 = fadd reassoc ninf nsz float %243, %275
  %279 = fadd reassoc ninf nsz float %244, %276
  %280 = fadd reassoc ninf nsz float %245, %257
  %281 = add i32 %46, 1
  %282 = tail call i32 @llvm.smax.i32(i32 %281, i32 0)
  %283 = tail call i32 @llvm.smin.i32(i32 %61, i32 %282)
  %284 = load ptr, ptr %27, align 8
  %285 = load i32, ptr %28, align 4
  %286 = mul i32 %285, %283
  %287 = add i32 %286, %69
  %288 = sext i32 %287 to i64
  %289 = getelementptr float, ptr %284, i64 %288
  %290 = load float, ptr %289, align 4
  %291 = fsub reassoc ninf nsz float %290, %57
  %292 = fmul reassoc ninf nsz float %291, %291
  %293 = fmul reassoc ninf nsz float %292, %23
  %294 = fsub reassoc ninf nsz float %24, %293
  %295 = tail call noundef float @expf(float noundef %294) #7
  %296 = load ptr, ptr %29, align 8
  %297 = load i32, ptr %30, align 4
  %298 = mul i32 %297, %283
  %299 = add i32 %298, %69
  %300 = mul i32 %299, 3
  %301 = sext i32 %300 to i64
  %302 = getelementptr float, ptr %296, i64 %301
  %303 = load float, ptr %302, align 4
  %304 = add i32 %300, 1
  %305 = sext i32 %304 to i64
  %306 = getelementptr float, ptr %296, i64 %305
  %307 = load float, ptr %306, align 4
  %308 = add i32 %300, 2
  %309 = sext i32 %308 to i64
  %310 = getelementptr float, ptr %296, i64 %309
  %311 = load float, ptr %310, align 4
  %312 = fmul reassoc ninf nsz float %303, %295
  %313 = fmul reassoc ninf nsz float %307, %295
  %314 = fmul reassoc ninf nsz float %311, %295
  %315 = fadd reassoc ninf nsz float %277, %312
  %316 = fadd reassoc ninf nsz float %278, %313
  %317 = fadd reassoc ninf nsz float %279, %314
  %318 = fadd reassoc ninf nsz float %280, %295
  %319 = load ptr, ptr %27, align 8
  %320 = load i32, ptr %28, align 4
  %321 = mul i32 %320, %283
  %322 = add i32 %321, %101
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, ptr %319, i64 %323
  %325 = load float, ptr %324, align 4
  %326 = fsub reassoc ninf nsz float %325, %57
  %327 = fmul reassoc ninf nsz float %326, %326
  %328 = fmul reassoc ninf nsz float %327, %23
  %329 = fsub reassoc ninf nsz float %25, %328
  %330 = tail call noundef float @expf(float noundef %329) #7
  %331 = load ptr, ptr %29, align 8
  %332 = load i32, ptr %30, align 4
  %333 = mul i32 %332, %283
  %334 = add i32 %333, %101
  %335 = mul i32 %334, 3
  %336 = sext i32 %335 to i64
  %337 = getelementptr float, ptr %331, i64 %336
  %338 = load float, ptr %337, align 4
  %339 = add i32 %335, 1
  %340 = sext i32 %339 to i64
  %341 = getelementptr float, ptr %331, i64 %340
  %342 = load float, ptr %341, align 4
  %343 = add i32 %335, 2
  %344 = sext i32 %343 to i64
  %345 = getelementptr float, ptr %331, i64 %344
  %346 = load float, ptr %345, align 4
  %347 = fmul reassoc ninf nsz float %338, %330
  %348 = fmul reassoc ninf nsz float %342, %330
  %349 = fmul reassoc ninf nsz float %346, %330
  %350 = fadd reassoc ninf nsz float %315, %347
  %351 = fadd reassoc ninf nsz float %316, %348
  %352 = fadd reassoc ninf nsz float %317, %349
  %353 = fadd reassoc ninf nsz float %318, %330
  %354 = load ptr, ptr %27, align 8
  %355 = load i32, ptr %28, align 4
  %356 = mul i32 %355, %283
  %357 = add i32 %356, %139
  %358 = sext i32 %357 to i64
  %359 = getelementptr float, ptr %354, i64 %358
  %360 = load float, ptr %359, align 4
  %361 = fsub reassoc ninf nsz float %360, %57
  %362 = fmul reassoc ninf nsz float %361, %361
  %363 = fmul reassoc ninf nsz float %362, %23
  %364 = fsub reassoc ninf nsz float %24, %363
  %365 = tail call noundef float @expf(float noundef %364) #7
  %366 = load ptr, ptr %29, align 8
  %367 = load i32, ptr %30, align 4
  %368 = mul i32 %367, %283
  %369 = add i32 %368, %139
  %370 = mul i32 %369, 3
  %371 = sext i32 %370 to i64
  %372 = getelementptr float, ptr %366, i64 %371
  %373 = load float, ptr %372, align 4
  %374 = add i32 %370, 1
  %375 = sext i32 %374 to i64
  %376 = getelementptr float, ptr %366, i64 %375
  %377 = load float, ptr %376, align 4
  %378 = add i32 %370, 2
  %379 = sext i32 %378 to i64
  %380 = getelementptr float, ptr %366, i64 %379
  %381 = load float, ptr %380, align 4
  %382 = fmul reassoc ninf nsz float %373, %365
  %383 = fmul reassoc ninf nsz float %377, %365
  %384 = fmul reassoc ninf nsz float %381, %365
  %385 = fadd reassoc ninf nsz float %350, %382
  %386 = fadd reassoc ninf nsz float %351, %383
  %387 = fadd reassoc ninf nsz float %352, %384
  %388 = fadd reassoc ninf nsz float %353, %365
  %389 = fdiv reassoc ninf nsz float %385, %388
  %390 = fdiv reassoc ninf nsz float %386, %388
  %391 = fdiv reassoc ninf nsz float %387, %388
  %392 = load ptr, ptr %32, align 8
  %393 = load i32, ptr %33, align 4
  %394 = sub i32 %393, %39
  %395 = mul i32 %394, 3
  %396 = mul i32 %395, %46
  %397 = add i32 %lsr.iv, %396
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, ptr %392, i64 %398
  store float %389, ptr %399, align 4
  %400 = load ptr, ptr %32, align 8
  %401 = load i32, ptr %33, align 4
  %402 = sub i32 %401, %39
  %403 = mul i32 %402, 3
  %404 = mul i32 %403, %46
  %405 = add i32 %lsr.iv, %404
  %406 = add i32 %405, 1
  %407 = sext i32 %406 to i64
  %408 = getelementptr float, ptr %400, i64 %407
  store float %390, ptr %408, align 4
  %409 = load ptr, ptr %32, align 8
  %410 = load i32, ptr %33, align 4
  %411 = sub i32 %410, %39
  %412 = mul i32 %411, 3
  %413 = mul i32 %412, %46
  %414 = add i32 %lsr.iv, %413
  %415 = add i32 %414, 2
  %416 = sext i32 %415 to i64
  %417 = getelementptr float, ptr %409, i64 %416
  store float %391, ptr %417, align 4
  %418 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %418
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
