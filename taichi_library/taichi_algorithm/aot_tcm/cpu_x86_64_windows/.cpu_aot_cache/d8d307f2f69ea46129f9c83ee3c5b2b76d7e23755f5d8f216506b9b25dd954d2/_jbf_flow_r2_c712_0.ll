; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.13 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jbf_flow_r2_c712_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_jbf_flow_r2_c712_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %37 = shl i32 %16, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %37, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %784, %for_loop_body ]
  %38 = load ptr, ptr %3, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 32872
  %40 = load ptr, ptr %39, align 8
  %41 = getelementptr inbounds nuw i8, ptr %40, i64 4
  %42 = load i32, ptr %41, align 4
  %43 = sdiv i32 %.05, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.05
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.05, %44
  %48 = and i1 %46, %47
  %.neg4 = sext i1 %48 to i32
  %49 = add i32 %43, %.neg4
  %50 = mul i32 %42, -1
  %51 = mul i32 %50, %49
  %52 = add i32 %.05, %51
  %53 = load ptr, ptr %30, align 8
  %54 = load i32, ptr %31, align 4
  %55 = sub i32 %54, %42
  %56 = mul i32 %55, %49
  %57 = add i32 %.05, %56
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, ptr %53, i64 %58
  %60 = load float, ptr %59, align 4
  %61 = add i32 %49, -2
  %62 = getelementptr inbounds nuw i8, ptr %40, i64 8
  %63 = load i32, ptr %62, align 4
  %64 = add i32 %63, -1
  %65 = tail call i32 @llvm.smax.i32(i32 %61, i32 0)
  %66 = tail call i32 @llvm.smin.i32(i32 %64, i32 %65)
  %67 = add i32 %52, -2
  %68 = getelementptr inbounds nuw i8, ptr %40, i64 12
  %69 = load i32, ptr %68, align 4
  %70 = add i32 %69, -1
  %71 = tail call i32 @llvm.smax.i32(i32 %67, i32 0)
  %72 = tail call i32 @llvm.smin.i32(i32 %70, i32 %71)
  %73 = mul i32 %66, %54
  %74 = add i32 %72, %73
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, ptr %53, i64 %75
  %77 = load float, ptr %76, align 4
  %78 = fsub reassoc ninf nsz float %77, %60
  %79 = fmul reassoc ninf nsz float %78, %78
  %80 = fmul reassoc ninf nsz float %79, %23
  %81 = fsub reassoc ninf nsz float %24, %80
  %82 = tail call noundef float @expf(float noundef %81) #7
  %83 = load ptr, ptr %32, align 8
  %84 = load i32, ptr %33, align 4
  %85 = mul i32 %84, %66
  %86 = add i32 %85, %72
  %87 = shl i32 %86, 1
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %83, i64 %88
  %90 = load float, ptr %89, align 4
  %91 = getelementptr i8, ptr %89, i64 4
  %92 = load float, ptr %91, align 4
  %93 = fmul reassoc ninf nsz float %90, %82
  %94 = fmul reassoc ninf nsz float %92, %82
  %95 = fadd reassoc ninf nsz float %82, 0x3D71979980000000
  %96 = add i32 %52, -1
  %97 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %98 = tail call i32 @llvm.smin.i32(i32 %70, i32 %97)
  %99 = load ptr, ptr %30, align 8
  %100 = load i32, ptr %31, align 4
  %101 = mul i32 %100, %66
  %102 = add i32 %101, %98
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, ptr %99, i64 %103
  %105 = load float, ptr %104, align 4
  %106 = fsub reassoc ninf nsz float %105, %60
  %107 = fmul reassoc ninf nsz float %106, %106
  %108 = fmul reassoc ninf nsz float %107, %23
  %109 = fsub reassoc ninf nsz float %25, %108
  %110 = tail call noundef float @expf(float noundef %109) #7
  %111 = load ptr, ptr %32, align 8
  %112 = load i32, ptr %33, align 4
  %113 = mul i32 %112, %66
  %114 = add i32 %113, %98
  %115 = shl i32 %114, 1
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %111, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = getelementptr i8, ptr %117, i64 4
  %120 = load float, ptr %119, align 4
  %121 = fmul reassoc ninf nsz float %118, %110
  %122 = fmul reassoc ninf nsz float %120, %110
  %123 = fadd reassoc ninf nsz float %121, %93
  %124 = fadd reassoc ninf nsz float %122, %94
  %125 = fadd reassoc ninf nsz float %95, %110
  %126 = tail call i32 @llvm.smax.i32(i32 %52, i32 0)
  %127 = tail call i32 @llvm.smin.i32(i32 %70, i32 %126)
  %128 = load ptr, ptr %30, align 8
  %129 = load i32, ptr %31, align 4
  %130 = mul i32 %129, %66
  %131 = add i32 %130, %127
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, ptr %128, i64 %132
  %134 = load float, ptr %133, align 4
  %135 = fsub reassoc ninf nsz float %134, %60
  %136 = fmul reassoc ninf nsz float %135, %135
  %137 = fmul reassoc ninf nsz float %136, %23
  %138 = fsub reassoc ninf nsz float %26, %137
  %139 = tail call noundef float @expf(float noundef %138) #7
  %140 = load ptr, ptr %32, align 8
  %141 = load i32, ptr %33, align 4
  %142 = mul i32 %141, %66
  %143 = add i32 %142, %127
  %144 = shl i32 %143, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %140, i64 %145
  %147 = load float, ptr %146, align 4
  %148 = getelementptr i8, ptr %146, i64 4
  %149 = load float, ptr %148, align 4
  %150 = fmul reassoc ninf nsz float %147, %139
  %151 = fmul reassoc ninf nsz float %149, %139
  %152 = fadd reassoc ninf nsz float %123, %150
  %153 = fadd reassoc ninf nsz float %124, %151
  %154 = fadd reassoc ninf nsz float %125, %139
  %155 = add i32 %52, 1
  %156 = tail call i32 @llvm.smax.i32(i32 %155, i32 0)
  %157 = tail call i32 @llvm.smin.i32(i32 %70, i32 %156)
  %158 = load ptr, ptr %30, align 8
  %159 = load i32, ptr %31, align 4
  %160 = mul i32 %159, %66
  %161 = add i32 %160, %157
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, ptr %158, i64 %162
  %164 = load float, ptr %163, align 4
  %165 = fsub reassoc ninf nsz float %164, %60
  %166 = fmul reassoc ninf nsz float %165, %165
  %167 = fmul reassoc ninf nsz float %166, %23
  %168 = fsub reassoc ninf nsz float %25, %167
  %169 = tail call noundef float @expf(float noundef %168) #7
  %170 = load ptr, ptr %32, align 8
  %171 = load i32, ptr %33, align 4
  %172 = mul i32 %171, %66
  %173 = add i32 %172, %157
  %174 = shl i32 %173, 1
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %170, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = getelementptr i8, ptr %176, i64 4
  %179 = load float, ptr %178, align 4
  %180 = fmul reassoc ninf nsz float %177, %169
  %181 = fmul reassoc ninf nsz float %179, %169
  %182 = fadd reassoc ninf nsz float %152, %180
  %183 = fadd reassoc ninf nsz float %153, %181
  %184 = fadd reassoc ninf nsz float %154, %169
  %185 = add i32 %52, 2
  %186 = tail call i32 @llvm.smax.i32(i32 %185, i32 0)
  %187 = tail call i32 @llvm.smin.i32(i32 %70, i32 %186)
  %188 = load ptr, ptr %30, align 8
  %189 = load i32, ptr %31, align 4
  %190 = mul i32 %189, %66
  %191 = add i32 %190, %187
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, ptr %188, i64 %192
  %194 = load float, ptr %193, align 4
  %195 = fsub reassoc ninf nsz float %194, %60
  %196 = fmul reassoc ninf nsz float %195, %195
  %197 = fmul reassoc ninf nsz float %196, %23
  %198 = fsub reassoc ninf nsz float %24, %197
  %199 = tail call noundef float @expf(float noundef %198) #7
  %200 = load ptr, ptr %32, align 8
  %201 = load i32, ptr %33, align 4
  %202 = mul i32 %201, %66
  %203 = add i32 %202, %187
  %204 = shl i32 %203, 1
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, ptr %200, i64 %205
  %207 = load float, ptr %206, align 4
  %208 = getelementptr i8, ptr %206, i64 4
  %209 = load float, ptr %208, align 4
  %210 = fmul reassoc ninf nsz float %207, %199
  %211 = fmul reassoc ninf nsz float %209, %199
  %212 = fadd reassoc ninf nsz float %182, %210
  %213 = fadd reassoc ninf nsz float %183, %211
  %214 = fadd reassoc ninf nsz float %184, %199
  %215 = add i32 %49, -1
  %216 = tail call i32 @llvm.smax.i32(i32 %215, i32 0)
  %217 = tail call i32 @llvm.smin.i32(i32 %64, i32 %216)
  %218 = load ptr, ptr %30, align 8
  %219 = load i32, ptr %31, align 4
  %220 = mul i32 %219, %217
  %221 = add i32 %220, %72
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, ptr %218, i64 %222
  %224 = load float, ptr %223, align 4
  %225 = fsub reassoc ninf nsz float %224, %60
  %226 = fmul reassoc ninf nsz float %225, %225
  %227 = fmul reassoc ninf nsz float %226, %23
  %228 = fsub reassoc ninf nsz float %25, %227
  %229 = tail call noundef float @expf(float noundef %228) #7
  %230 = load ptr, ptr %32, align 8
  %231 = load i32, ptr %33, align 4
  %232 = mul i32 %231, %217
  %233 = add i32 %232, %72
  %234 = shl i32 %233, 1
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %230, i64 %235
  %237 = load float, ptr %236, align 4
  %238 = getelementptr i8, ptr %236, i64 4
  %239 = load float, ptr %238, align 4
  %240 = fmul reassoc ninf nsz float %237, %229
  %241 = fmul reassoc ninf nsz float %239, %229
  %242 = fadd reassoc ninf nsz float %212, %240
  %243 = fadd reassoc ninf nsz float %213, %241
  %244 = fadd reassoc ninf nsz float %214, %229
  %245 = load ptr, ptr %30, align 8
  %246 = load i32, ptr %31, align 4
  %247 = mul i32 %246, %217
  %248 = add i32 %247, %98
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, ptr %245, i64 %249
  %251 = load float, ptr %250, align 4
  %252 = fsub reassoc ninf nsz float %251, %60
  %253 = fmul reassoc ninf nsz float %252, %252
  %254 = fmul reassoc ninf nsz float %253, %23
  %255 = fsub reassoc ninf nsz float %27, %254
  %256 = tail call noundef float @expf(float noundef %255) #7
  %257 = load ptr, ptr %32, align 8
  %258 = load i32, ptr %33, align 4
  %259 = mul i32 %258, %217
  %260 = add i32 %259, %98
  %261 = shl i32 %260, 1
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, ptr %257, i64 %262
  %264 = load float, ptr %263, align 4
  %265 = getelementptr i8, ptr %263, i64 4
  %266 = load float, ptr %265, align 4
  %267 = fmul reassoc ninf nsz float %264, %256
  %268 = fmul reassoc ninf nsz float %266, %256
  %269 = fadd reassoc ninf nsz float %242, %267
  %270 = fadd reassoc ninf nsz float %243, %268
  %271 = fadd reassoc ninf nsz float %244, %256
  %272 = load ptr, ptr %30, align 8
  %273 = load i32, ptr %31, align 4
  %274 = mul i32 %273, %217
  %275 = add i32 %274, %127
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, ptr %272, i64 %276
  %278 = load float, ptr %277, align 4
  %279 = fsub reassoc ninf nsz float %278, %60
  %280 = fmul reassoc ninf nsz float %279, %279
  %281 = fmul reassoc ninf nsz float %280, %23
  %282 = fsub reassoc ninf nsz float %28, %281
  %283 = tail call noundef float @expf(float noundef %282) #7
  %284 = load ptr, ptr %32, align 8
  %285 = load i32, ptr %33, align 4
  %286 = mul i32 %285, %217
  %287 = add i32 %286, %127
  %288 = shl i32 %287, 1
  %289 = sext i32 %288 to i64
  %290 = getelementptr float, ptr %284, i64 %289
  %291 = load float, ptr %290, align 4
  %292 = getelementptr i8, ptr %290, i64 4
  %293 = load float, ptr %292, align 4
  %294 = fmul reassoc ninf nsz float %291, %283
  %295 = fmul reassoc ninf nsz float %293, %283
  %296 = fadd reassoc ninf nsz float %269, %294
  %297 = fadd reassoc ninf nsz float %270, %295
  %298 = fadd reassoc ninf nsz float %271, %283
  %299 = load ptr, ptr %30, align 8
  %300 = load i32, ptr %31, align 4
  %301 = mul i32 %300, %217
  %302 = add i32 %301, %157
  %303 = sext i32 %302 to i64
  %304 = getelementptr float, ptr %299, i64 %303
  %305 = load float, ptr %304, align 4
  %306 = fsub reassoc ninf nsz float %305, %60
  %307 = fmul reassoc ninf nsz float %306, %306
  %308 = fmul reassoc ninf nsz float %307, %23
  %309 = fsub reassoc ninf nsz float %27, %308
  %310 = tail call noundef float @expf(float noundef %309) #7
  %311 = load ptr, ptr %32, align 8
  %312 = load i32, ptr %33, align 4
  %313 = mul i32 %312, %217
  %314 = add i32 %313, %157
  %315 = shl i32 %314, 1
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, ptr %311, i64 %316
  %318 = load float, ptr %317, align 4
  %319 = getelementptr i8, ptr %317, i64 4
  %320 = load float, ptr %319, align 4
  %321 = fmul reassoc ninf nsz float %318, %310
  %322 = fmul reassoc ninf nsz float %320, %310
  %323 = fadd reassoc ninf nsz float %296, %321
  %324 = fadd reassoc ninf nsz float %297, %322
  %325 = fadd reassoc ninf nsz float %298, %310
  %326 = load ptr, ptr %30, align 8
  %327 = load i32, ptr %31, align 4
  %328 = mul i32 %327, %217
  %329 = add i32 %328, %187
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, ptr %326, i64 %330
  %332 = load float, ptr %331, align 4
  %333 = fsub reassoc ninf nsz float %332, %60
  %334 = fmul reassoc ninf nsz float %333, %333
  %335 = fmul reassoc ninf nsz float %334, %23
  %336 = fsub reassoc ninf nsz float %25, %335
  %337 = tail call noundef float @expf(float noundef %336) #7
  %338 = load ptr, ptr %32, align 8
  %339 = load i32, ptr %33, align 4
  %340 = mul i32 %339, %217
  %341 = add i32 %340, %187
  %342 = shl i32 %341, 1
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, ptr %338, i64 %343
  %345 = load float, ptr %344, align 4
  %346 = getelementptr i8, ptr %344, i64 4
  %347 = load float, ptr %346, align 4
  %348 = fmul reassoc ninf nsz float %345, %337
  %349 = fmul reassoc ninf nsz float %347, %337
  %350 = fadd reassoc ninf nsz float %323, %348
  %351 = fadd reassoc ninf nsz float %324, %349
  %352 = fadd reassoc ninf nsz float %325, %337
  %353 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %354 = tail call i32 @llvm.smin.i32(i32 %64, i32 %353)
  %355 = load ptr, ptr %30, align 8
  %356 = load i32, ptr %31, align 4
  %357 = mul i32 %356, %354
  %358 = add i32 %357, %72
  %359 = sext i32 %358 to i64
  %360 = getelementptr float, ptr %355, i64 %359
  %361 = load float, ptr %360, align 4
  %362 = fsub reassoc ninf nsz float %361, %60
  %363 = fmul reassoc ninf nsz float %362, %362
  %364 = fmul reassoc ninf nsz float %363, %23
  %365 = fsub reassoc ninf nsz float %26, %364
  %366 = tail call noundef float @expf(float noundef %365) #7
  %367 = load ptr, ptr %32, align 8
  %368 = load i32, ptr %33, align 4
  %369 = mul i32 %368, %354
  %370 = add i32 %369, %72
  %371 = shl i32 %370, 1
  %372 = sext i32 %371 to i64
  %373 = getelementptr float, ptr %367, i64 %372
  %374 = load float, ptr %373, align 4
  %375 = getelementptr i8, ptr %373, i64 4
  %376 = load float, ptr %375, align 4
  %377 = fmul reassoc ninf nsz float %374, %366
  %378 = fmul reassoc ninf nsz float %376, %366
  %379 = fadd reassoc ninf nsz float %350, %377
  %380 = fadd reassoc ninf nsz float %351, %378
  %381 = fadd reassoc ninf nsz float %352, %366
  %382 = load ptr, ptr %30, align 8
  %383 = load i32, ptr %31, align 4
  %384 = mul i32 %383, %354
  %385 = add i32 %384, %98
  %386 = sext i32 %385 to i64
  %387 = getelementptr float, ptr %382, i64 %386
  %388 = load float, ptr %387, align 4
  %389 = fsub reassoc ninf nsz float %388, %60
  %390 = fmul reassoc ninf nsz float %389, %389
  %391 = fmul reassoc ninf nsz float %390, %23
  %392 = fsub reassoc ninf nsz float %28, %391
  %393 = tail call noundef float @expf(float noundef %392) #7
  %394 = load ptr, ptr %32, align 8
  %395 = load i32, ptr %33, align 4
  %396 = mul i32 %395, %354
  %397 = add i32 %396, %98
  %398 = shl i32 %397, 1
  %399 = sext i32 %398 to i64
  %400 = getelementptr float, ptr %394, i64 %399
  %401 = load float, ptr %400, align 4
  %402 = getelementptr i8, ptr %400, i64 4
  %403 = load float, ptr %402, align 4
  %404 = fmul reassoc ninf nsz float %401, %393
  %405 = fmul reassoc ninf nsz float %403, %393
  %406 = fadd reassoc ninf nsz float %379, %404
  %407 = fadd reassoc ninf nsz float %380, %405
  %408 = fadd reassoc ninf nsz float %381, %393
  %409 = load ptr, ptr %30, align 8
  %410 = load i32, ptr %31, align 4
  %411 = mul i32 %410, %354
  %412 = add i32 %411, %127
  %413 = sext i32 %412 to i64
  %414 = getelementptr float, ptr %409, i64 %413
  %415 = load float, ptr %414, align 4
  %416 = fsub reassoc ninf nsz float %415, %60
  %417 = fmul reassoc ninf nsz float %416, %416
  %418 = fmul reassoc ninf nsz float %417, %34
  %419 = tail call noundef float @expf(float noundef %418) #7
  %420 = load ptr, ptr %32, align 8
  %421 = load i32, ptr %33, align 4
  %422 = mul i32 %421, %354
  %423 = add i32 %422, %127
  %424 = shl i32 %423, 1
  %425 = sext i32 %424 to i64
  %426 = getelementptr float, ptr %420, i64 %425
  %427 = load float, ptr %426, align 4
  %428 = getelementptr i8, ptr %426, i64 4
  %429 = load float, ptr %428, align 4
  %430 = fmul reassoc ninf nsz float %427, %419
  %431 = fmul reassoc ninf nsz float %429, %419
  %432 = fadd reassoc ninf nsz float %406, %430
  %433 = fadd reassoc ninf nsz float %407, %431
  %434 = fadd reassoc ninf nsz float %408, %419
  %435 = load ptr, ptr %30, align 8
  %436 = load i32, ptr %31, align 4
  %437 = mul i32 %436, %354
  %438 = add i32 %437, %157
  %439 = sext i32 %438 to i64
  %440 = getelementptr float, ptr %435, i64 %439
  %441 = load float, ptr %440, align 4
  %442 = fsub reassoc ninf nsz float %441, %60
  %443 = fmul reassoc ninf nsz float %442, %442
  %444 = fmul reassoc ninf nsz float %443, %23
  %445 = fsub reassoc ninf nsz float %28, %444
  %446 = tail call noundef float @expf(float noundef %445) #7
  %447 = load ptr, ptr %32, align 8
  %448 = load i32, ptr %33, align 4
  %449 = mul i32 %448, %354
  %450 = add i32 %449, %157
  %451 = shl i32 %450, 1
  %452 = sext i32 %451 to i64
  %453 = getelementptr float, ptr %447, i64 %452
  %454 = load float, ptr %453, align 4
  %455 = getelementptr i8, ptr %453, i64 4
  %456 = load float, ptr %455, align 4
  %457 = fmul reassoc ninf nsz float %454, %446
  %458 = fmul reassoc ninf nsz float %456, %446
  %459 = fadd reassoc ninf nsz float %432, %457
  %460 = fadd reassoc ninf nsz float %433, %458
  %461 = fadd reassoc ninf nsz float %434, %446
  %462 = load ptr, ptr %30, align 8
  %463 = load i32, ptr %31, align 4
  %464 = mul i32 %463, %354
  %465 = add i32 %464, %187
  %466 = sext i32 %465 to i64
  %467 = getelementptr float, ptr %462, i64 %466
  %468 = load float, ptr %467, align 4
  %469 = fsub reassoc ninf nsz float %468, %60
  %470 = fmul reassoc ninf nsz float %469, %469
  %471 = fmul reassoc ninf nsz float %470, %23
  %472 = fsub reassoc ninf nsz float %26, %471
  %473 = tail call noundef float @expf(float noundef %472) #7
  %474 = load ptr, ptr %32, align 8
  %475 = load i32, ptr %33, align 4
  %476 = mul i32 %475, %354
  %477 = add i32 %476, %187
  %478 = shl i32 %477, 1
  %479 = sext i32 %478 to i64
  %480 = getelementptr float, ptr %474, i64 %479
  %481 = load float, ptr %480, align 4
  %482 = getelementptr i8, ptr %480, i64 4
  %483 = load float, ptr %482, align 4
  %484 = fmul reassoc ninf nsz float %481, %473
  %485 = fmul reassoc ninf nsz float %483, %473
  %486 = fadd reassoc ninf nsz float %459, %484
  %487 = fadd reassoc ninf nsz float %460, %485
  %488 = fadd reassoc ninf nsz float %461, %473
  %489 = add i32 %49, 1
  %490 = tail call i32 @llvm.smax.i32(i32 %489, i32 0)
  %491 = tail call i32 @llvm.smin.i32(i32 %64, i32 %490)
  %492 = load ptr, ptr %30, align 8
  %493 = load i32, ptr %31, align 4
  %494 = mul i32 %493, %491
  %495 = add i32 %494, %72
  %496 = sext i32 %495 to i64
  %497 = getelementptr float, ptr %492, i64 %496
  %498 = load float, ptr %497, align 4
  %499 = fsub reassoc ninf nsz float %498, %60
  %500 = fmul reassoc ninf nsz float %499, %499
  %501 = fmul reassoc ninf nsz float %500, %23
  %502 = fsub reassoc ninf nsz float %25, %501
  %503 = tail call noundef float @expf(float noundef %502) #7
  %504 = load ptr, ptr %32, align 8
  %505 = load i32, ptr %33, align 4
  %506 = mul i32 %505, %491
  %507 = add i32 %506, %72
  %508 = shl i32 %507, 1
  %509 = sext i32 %508 to i64
  %510 = getelementptr float, ptr %504, i64 %509
  %511 = load float, ptr %510, align 4
  %512 = getelementptr i8, ptr %510, i64 4
  %513 = load float, ptr %512, align 4
  %514 = fmul reassoc ninf nsz float %511, %503
  %515 = fmul reassoc ninf nsz float %513, %503
  %516 = fadd reassoc ninf nsz float %486, %514
  %517 = fadd reassoc ninf nsz float %487, %515
  %518 = fadd reassoc ninf nsz float %488, %503
  %519 = load ptr, ptr %30, align 8
  %520 = load i32, ptr %31, align 4
  %521 = mul i32 %520, %491
  %522 = add i32 %521, %98
  %523 = sext i32 %522 to i64
  %524 = getelementptr float, ptr %519, i64 %523
  %525 = load float, ptr %524, align 4
  %526 = fsub reassoc ninf nsz float %525, %60
  %527 = fmul reassoc ninf nsz float %526, %526
  %528 = fmul reassoc ninf nsz float %527, %23
  %529 = fsub reassoc ninf nsz float %27, %528
  %530 = tail call noundef float @expf(float noundef %529) #7
  %531 = load ptr, ptr %32, align 8
  %532 = load i32, ptr %33, align 4
  %533 = mul i32 %532, %491
  %534 = add i32 %533, %98
  %535 = shl i32 %534, 1
  %536 = sext i32 %535 to i64
  %537 = getelementptr float, ptr %531, i64 %536
  %538 = load float, ptr %537, align 4
  %539 = getelementptr i8, ptr %537, i64 4
  %540 = load float, ptr %539, align 4
  %541 = fmul reassoc ninf nsz float %538, %530
  %542 = fmul reassoc ninf nsz float %540, %530
  %543 = fadd reassoc ninf nsz float %516, %541
  %544 = fadd reassoc ninf nsz float %517, %542
  %545 = fadd reassoc ninf nsz float %518, %530
  %546 = load ptr, ptr %30, align 8
  %547 = load i32, ptr %31, align 4
  %548 = mul i32 %547, %491
  %549 = add i32 %548, %127
  %550 = sext i32 %549 to i64
  %551 = getelementptr float, ptr %546, i64 %550
  %552 = load float, ptr %551, align 4
  %553 = fsub reassoc ninf nsz float %552, %60
  %554 = fmul reassoc ninf nsz float %553, %553
  %555 = fmul reassoc ninf nsz float %554, %23
  %556 = fsub reassoc ninf nsz float %28, %555
  %557 = tail call noundef float @expf(float noundef %556) #7
  %558 = load ptr, ptr %32, align 8
  %559 = load i32, ptr %33, align 4
  %560 = mul i32 %559, %491
  %561 = add i32 %560, %127
  %562 = shl i32 %561, 1
  %563 = sext i32 %562 to i64
  %564 = getelementptr float, ptr %558, i64 %563
  %565 = load float, ptr %564, align 4
  %566 = getelementptr i8, ptr %564, i64 4
  %567 = load float, ptr %566, align 4
  %568 = fmul reassoc ninf nsz float %565, %557
  %569 = fmul reassoc ninf nsz float %567, %557
  %570 = fadd reassoc ninf nsz float %543, %568
  %571 = fadd reassoc ninf nsz float %544, %569
  %572 = fadd reassoc ninf nsz float %545, %557
  %573 = load ptr, ptr %30, align 8
  %574 = load i32, ptr %31, align 4
  %575 = mul i32 %574, %491
  %576 = add i32 %575, %157
  %577 = sext i32 %576 to i64
  %578 = getelementptr float, ptr %573, i64 %577
  %579 = load float, ptr %578, align 4
  %580 = fsub reassoc ninf nsz float %579, %60
  %581 = fmul reassoc ninf nsz float %580, %580
  %582 = fmul reassoc ninf nsz float %581, %23
  %583 = fsub reassoc ninf nsz float %27, %582
  %584 = tail call noundef float @expf(float noundef %583) #7
  %585 = load ptr, ptr %32, align 8
  %586 = load i32, ptr %33, align 4
  %587 = mul i32 %586, %491
  %588 = add i32 %587, %157
  %589 = shl i32 %588, 1
  %590 = sext i32 %589 to i64
  %591 = getelementptr float, ptr %585, i64 %590
  %592 = load float, ptr %591, align 4
  %593 = getelementptr i8, ptr %591, i64 4
  %594 = load float, ptr %593, align 4
  %595 = fmul reassoc ninf nsz float %592, %584
  %596 = fmul reassoc ninf nsz float %594, %584
  %597 = fadd reassoc ninf nsz float %570, %595
  %598 = fadd reassoc ninf nsz float %571, %596
  %599 = fadd reassoc ninf nsz float %572, %584
  %600 = load ptr, ptr %30, align 8
  %601 = load i32, ptr %31, align 4
  %602 = mul i32 %601, %491
  %603 = add i32 %602, %187
  %604 = sext i32 %603 to i64
  %605 = getelementptr float, ptr %600, i64 %604
  %606 = load float, ptr %605, align 4
  %607 = fsub reassoc ninf nsz float %606, %60
  %608 = fmul reassoc ninf nsz float %607, %607
  %609 = fmul reassoc ninf nsz float %608, %23
  %610 = fsub reassoc ninf nsz float %25, %609
  %611 = tail call noundef float @expf(float noundef %610) #7
  %612 = load ptr, ptr %32, align 8
  %613 = load i32, ptr %33, align 4
  %614 = mul i32 %613, %491
  %615 = add i32 %614, %187
  %616 = shl i32 %615, 1
  %617 = sext i32 %616 to i64
  %618 = getelementptr float, ptr %612, i64 %617
  %619 = load float, ptr %618, align 4
  %620 = getelementptr i8, ptr %618, i64 4
  %621 = load float, ptr %620, align 4
  %622 = fmul reassoc ninf nsz float %619, %611
  %623 = fmul reassoc ninf nsz float %621, %611
  %624 = fadd reassoc ninf nsz float %597, %622
  %625 = fadd reassoc ninf nsz float %598, %623
  %626 = fadd reassoc ninf nsz float %599, %611
  %627 = add i32 %49, 2
  %628 = tail call i32 @llvm.smax.i32(i32 %627, i32 0)
  %629 = tail call i32 @llvm.smin.i32(i32 %64, i32 %628)
  %630 = load ptr, ptr %30, align 8
  %631 = load i32, ptr %31, align 4
  %632 = mul i32 %631, %629
  %633 = add i32 %632, %72
  %634 = sext i32 %633 to i64
  %635 = getelementptr float, ptr %630, i64 %634
  %636 = load float, ptr %635, align 4
  %637 = fsub reassoc ninf nsz float %636, %60
  %638 = fmul reassoc ninf nsz float %637, %637
  %639 = fmul reassoc ninf nsz float %638, %23
  %640 = fsub reassoc ninf nsz float %24, %639
  %641 = tail call noundef float @expf(float noundef %640) #7
  %642 = load ptr, ptr %32, align 8
  %643 = load i32, ptr %33, align 4
  %644 = mul i32 %643, %629
  %645 = add i32 %644, %72
  %646 = shl i32 %645, 1
  %647 = sext i32 %646 to i64
  %648 = getelementptr float, ptr %642, i64 %647
  %649 = load float, ptr %648, align 4
  %650 = getelementptr i8, ptr %648, i64 4
  %651 = load float, ptr %650, align 4
  %652 = fmul reassoc ninf nsz float %649, %641
  %653 = fmul reassoc ninf nsz float %651, %641
  %654 = fadd reassoc ninf nsz float %624, %652
  %655 = fadd reassoc ninf nsz float %625, %653
  %656 = fadd reassoc ninf nsz float %626, %641
  %657 = load ptr, ptr %30, align 8
  %658 = load i32, ptr %31, align 4
  %659 = mul i32 %658, %629
  %660 = add i32 %659, %98
  %661 = sext i32 %660 to i64
  %662 = getelementptr float, ptr %657, i64 %661
  %663 = load float, ptr %662, align 4
  %664 = fsub reassoc ninf nsz float %663, %60
  %665 = fmul reassoc ninf nsz float %664, %664
  %666 = fmul reassoc ninf nsz float %665, %23
  %667 = fsub reassoc ninf nsz float %25, %666
  %668 = tail call noundef float @expf(float noundef %667) #7
  %669 = load ptr, ptr %32, align 8
  %670 = load i32, ptr %33, align 4
  %671 = mul i32 %670, %629
  %672 = add i32 %671, %98
  %673 = shl i32 %672, 1
  %674 = sext i32 %673 to i64
  %675 = getelementptr float, ptr %669, i64 %674
  %676 = load float, ptr %675, align 4
  %677 = getelementptr i8, ptr %675, i64 4
  %678 = load float, ptr %677, align 4
  %679 = fmul reassoc ninf nsz float %676, %668
  %680 = fmul reassoc ninf nsz float %678, %668
  %681 = fadd reassoc ninf nsz float %654, %679
  %682 = fadd reassoc ninf nsz float %655, %680
  %683 = fadd reassoc ninf nsz float %656, %668
  %684 = load ptr, ptr %30, align 8
  %685 = load i32, ptr %31, align 4
  %686 = mul i32 %685, %629
  %687 = add i32 %686, %127
  %688 = sext i32 %687 to i64
  %689 = getelementptr float, ptr %684, i64 %688
  %690 = load float, ptr %689, align 4
  %691 = fsub reassoc ninf nsz float %690, %60
  %692 = fmul reassoc ninf nsz float %691, %691
  %693 = fmul reassoc ninf nsz float %692, %23
  %694 = fsub reassoc ninf nsz float %26, %693
  %695 = tail call noundef float @expf(float noundef %694) #7
  %696 = load ptr, ptr %32, align 8
  %697 = load i32, ptr %33, align 4
  %698 = mul i32 %697, %629
  %699 = add i32 %698, %127
  %700 = shl i32 %699, 1
  %701 = sext i32 %700 to i64
  %702 = getelementptr float, ptr %696, i64 %701
  %703 = load float, ptr %702, align 4
  %704 = getelementptr i8, ptr %702, i64 4
  %705 = load float, ptr %704, align 4
  %706 = fmul reassoc ninf nsz float %703, %695
  %707 = fmul reassoc ninf nsz float %705, %695
  %708 = fadd reassoc ninf nsz float %681, %706
  %709 = fadd reassoc ninf nsz float %682, %707
  %710 = fadd reassoc ninf nsz float %683, %695
  %711 = load ptr, ptr %30, align 8
  %712 = load i32, ptr %31, align 4
  %713 = mul i32 %712, %629
  %714 = add i32 %713, %157
  %715 = sext i32 %714 to i64
  %716 = getelementptr float, ptr %711, i64 %715
  %717 = load float, ptr %716, align 4
  %718 = fsub reassoc ninf nsz float %717, %60
  %719 = fmul reassoc ninf nsz float %718, %718
  %720 = fmul reassoc ninf nsz float %719, %23
  %721 = fsub reassoc ninf nsz float %25, %720
  %722 = tail call noundef float @expf(float noundef %721) #7
  %723 = load ptr, ptr %32, align 8
  %724 = load i32, ptr %33, align 4
  %725 = mul i32 %724, %629
  %726 = add i32 %725, %157
  %727 = shl i32 %726, 1
  %728 = sext i32 %727 to i64
  %729 = getelementptr float, ptr %723, i64 %728
  %730 = load float, ptr %729, align 4
  %731 = getelementptr i8, ptr %729, i64 4
  %732 = load float, ptr %731, align 4
  %733 = fmul reassoc ninf nsz float %730, %722
  %734 = fmul reassoc ninf nsz float %732, %722
  %735 = fadd reassoc ninf nsz float %708, %733
  %736 = fadd reassoc ninf nsz float %709, %734
  %737 = fadd reassoc ninf nsz float %710, %722
  %738 = load ptr, ptr %30, align 8
  %739 = load i32, ptr %31, align 4
  %740 = mul i32 %739, %629
  %741 = add i32 %740, %187
  %742 = sext i32 %741 to i64
  %743 = getelementptr float, ptr %738, i64 %742
  %744 = load float, ptr %743, align 4
  %745 = fsub reassoc ninf nsz float %744, %60
  %746 = fmul reassoc ninf nsz float %745, %745
  %747 = fmul reassoc ninf nsz float %746, %23
  %748 = fsub reassoc ninf nsz float %24, %747
  %749 = tail call noundef float @expf(float noundef %748) #7
  %750 = load ptr, ptr %32, align 8
  %751 = load i32, ptr %33, align 4
  %752 = mul i32 %751, %629
  %753 = add i32 %752, %187
  %754 = shl i32 %753, 1
  %755 = sext i32 %754 to i64
  %756 = getelementptr float, ptr %750, i64 %755
  %757 = load float, ptr %756, align 4
  %758 = getelementptr i8, ptr %756, i64 4
  %759 = load float, ptr %758, align 4
  %760 = fmul reassoc ninf nsz float %757, %749
  %761 = fmul reassoc ninf nsz float %759, %749
  %762 = fadd reassoc ninf nsz float %735, %760
  %763 = fadd reassoc ninf nsz float %736, %761
  %764 = fadd reassoc ninf nsz float %737, %749
  %765 = fdiv reassoc ninf nsz float %762, %764
  %766 = fdiv reassoc ninf nsz float %763, %764
  %767 = load ptr, ptr %35, align 8
  %768 = load i32, ptr %36, align 4
  %769 = sub i32 %768, %42
  %770 = shl i32 %769, 1
  %771 = mul i32 %770, %49
  %772 = add i32 %lsr.iv, %771
  %773 = sext i32 %772 to i64
  %774 = getelementptr float, ptr %767, i64 %773
  store float %765, ptr %774, align 4
  %775 = load ptr, ptr %35, align 8
  %776 = load i32, ptr %36, align 4
  %777 = sub i32 %776, %42
  %778 = shl i32 %777, 1
  %779 = mul i32 %778, %49
  %780 = add i32 %lsr.iv, %779
  %781 = add i32 %780, 1
  %782 = sext i32 %781 to i64
  %783 = getelementptr float, ptr %775, i64 %782
  store float %766, ptr %783, align 4
  %784 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %784
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
  %4 = alloca %struct.RuntimeContext.13, align 8
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
