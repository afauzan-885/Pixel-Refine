; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_downsample_2x_offset_kernel_3ch_c268_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 24
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 28
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = mul i32 %6, 3
  %8 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 32872
  %11 = load ptr, ptr %10, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 4
  store i32 %7, ptr %12, align 4
  %13 = mul i32 %7, %3
  %14 = load ptr, ptr %8, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 32872
  %16 = load ptr, ptr %15, align 8
  store i32 %13, ptr %16, align 4
  ret void
}

define void @_downsample_2x_offset_kernel_3ch_c268_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #6
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
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 48
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 52
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr i8, ptr %19, i64 16
  %26 = getelementptr i8, ptr %19, i64 4
  %27 = getelementptr i8, ptr %19, i64 8
  %28 = getelementptr i8, ptr %19, i64 40
  %29 = getelementptr i8, ptr %19, i64 28
  %30 = getelementptr i8, ptr %19, i64 32
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.025 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %371, %for_loop_body ]
  %31 = load ptr, ptr %3, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 4
  %35 = load i32, ptr %34, align 4
  %36 = sdiv i32 %.025, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.025
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.025, %37
  %41 = and i1 %39, %40
  %.neg4 = sext i1 %41 to i32
  %42 = add i32 %36, %.neg4
  %43 = mul i32 %42, %35
  %44 = mul i32 %35, -1
  %45 = mul i32 %44, %42
  %46 = add i32 %.025, %45
  %47 = sdiv i32 %46, 3
  %48 = icmp slt i32 %46, 0
  %49 = mul nsw i32 %47, 3
  %50 = icmp ne i32 %46, %49
  %51 = and i1 %48, %50
  %.neg5 = sext i1 %51 to i32
  %52 = add i32 %47, %.neg5
  %53 = add i32 %42, %21
  %54 = shl i32 %53, 1
  %55 = add i32 %52, %23
  %56 = shl i32 %55, 1
  %57 = add i32 %54, -2
  %58 = load ptr, ptr %0, align 8
  %59 = load i32, ptr %58, align 4
  %60 = tail call i32 @llvm.abs.i32(i32 %57, i1 true)
  %61 = add i32 %59, -1
  %62 = sub i32 %60, %61
  %63 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %64 = shl nuw i32 %63, 1
  %65 = sub i32 %60, %64
  %66 = tail call i32 @llvm.smax.i32(i32 %65, i32 0)
  %67 = tail call i32 @llvm.smin.i32(i32 %61, i32 %66)
  %68 = add i32 %56, -2
  %69 = getelementptr i8, ptr %58, i64 4
  %70 = load i32, ptr %69, align 4
  %71 = tail call i32 @llvm.abs.i32(i32 %68, i1 true)
  %72 = add i32 %70, -1
  %73 = sub i32 %71, %72
  %74 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %75 = shl nuw i32 %74, 1
  %76 = sub i32 %71, %75
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %72, i32 %77)
  %79 = load ptr, ptr %25, align 8
  %80 = load i32, ptr %26, align 4
  %81 = load i32, ptr %27, align 4
  %82 = mul i32 %67, %80
  %83 = add i32 %78, %82
  %84 = mul i32 %83, %81
  %85 = sub i32 %84, %43
  %86 = mul i32 %52, 3
  %87 = sub i32 %85, %86
  %88 = add i32 %.025, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, ptr %79, i64 %89
  %91 = load float, ptr %90, align 4
  %92 = add i32 %56, -1
  %93 = tail call i32 @llvm.abs.i32(i32 %92, i1 true)
  %94 = sub i32 %93, %72
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = shl nuw i32 %95, 1
  %97 = sub i32 %93, %96
  %98 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %99 = tail call i32 @llvm.smin.i32(i32 %72, i32 %98)
  %100 = add i32 %99, %82
  %101 = mul i32 %100, %81
  %102 = sub i32 %101, %43
  %103 = sub i32 %102, %86
  %104 = add i32 %.025, %103
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, ptr %79, i64 %105
  %107 = load float, ptr %106, align 4
  %108 = tail call i32 @llvm.abs.i32(i32 %56, i1 true)
  %109 = sub i32 %108, %72
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %111 = shl nuw i32 %110, 1
  %112 = sub i32 %108, %111
  %113 = tail call i32 @llvm.smax.i32(i32 %112, i32 0)
  %114 = tail call i32 @llvm.smin.i32(i32 %72, i32 %113)
  %115 = add i32 %114, %82
  %116 = mul i32 %115, %81
  %117 = sub i32 %116, %43
  %118 = sub i32 %117, %86
  %119 = add i32 %.025, %118
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %79, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = or disjoint i32 %56, 1
  %124 = tail call i32 @llvm.abs.i32(i32 %123, i1 true)
  %125 = sub i32 %124, %72
  %126 = tail call i32 @llvm.smax.i32(i32 %125, i32 0)
  %127 = shl nuw i32 %126, 1
  %128 = sub i32 %124, %127
  %129 = tail call i32 @llvm.smax.i32(i32 %128, i32 0)
  %130 = tail call i32 @llvm.smin.i32(i32 %72, i32 %129)
  %131 = add i32 %130, %82
  %132 = mul i32 %131, %81
  %133 = sub i32 %132, %43
  %134 = sub i32 %133, %86
  %135 = add i32 %.025, %134
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %79, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = add i32 %56, 2
  %140 = tail call i32 @llvm.abs.i32(i32 %139, i1 true)
  %141 = sub i32 %140, %72
  %142 = tail call i32 @llvm.smax.i32(i32 %141, i32 0)
  %143 = shl nuw i32 %142, 1
  %144 = sub i32 %140, %143
  %145 = tail call i32 @llvm.smax.i32(i32 %144, i32 0)
  %146 = tail call i32 @llvm.smin.i32(i32 %72, i32 %145)
  %147 = add i32 %146, %82
  %148 = mul i32 %147, %81
  %149 = sub i32 %148, %43
  %150 = sub i32 %149, %86
  %151 = add i32 %.025, %150
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %79, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = add i32 %54, -1
  %156 = tail call i32 @llvm.abs.i32(i32 %155, i1 true)
  %157 = sub i32 %156, %61
  %158 = tail call i32 @llvm.smax.i32(i32 %157, i32 0)
  %159 = shl nuw i32 %158, 1
  %160 = sub i32 %156, %159
  %161 = tail call i32 @llvm.smax.i32(i32 %160, i32 0)
  %162 = tail call i32 @llvm.smin.i32(i32 %61, i32 %161)
  %163 = mul i32 %162, %80
  %164 = add i32 %78, %163
  %165 = mul i32 %164, %81
  %166 = sub i32 %165, %43
  %167 = sub i32 %166, %86
  %168 = add i32 %.025, %167
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %79, i64 %169
  %171 = load float, ptr %170, align 4
  %172 = add i32 %99, %163
  %173 = mul i32 %172, %81
  %174 = sub i32 %173, %43
  %175 = sub i32 %174, %86
  %176 = add i32 %.025, %175
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, ptr %79, i64 %177
  %179 = load float, ptr %178, align 4
  %180 = add i32 %114, %163
  %181 = mul i32 %180, %81
  %182 = sub i32 %181, %43
  %183 = sub i32 %182, %86
  %184 = add i32 %.025, %183
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, ptr %79, i64 %185
  %187 = load float, ptr %186, align 4
  %188 = add i32 %130, %163
  %189 = mul i32 %188, %81
  %190 = sub i32 %189, %43
  %191 = sub i32 %190, %86
  %192 = add i32 %.025, %191
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, ptr %79, i64 %193
  %195 = load float, ptr %194, align 4
  %196 = add i32 %146, %163
  %197 = mul i32 %196, %81
  %198 = sub i32 %197, %43
  %199 = sub i32 %198, %86
  %200 = add i32 %.025, %199
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, ptr %79, i64 %201
  %203 = load float, ptr %202, align 4
  %204 = tail call i32 @llvm.abs.i32(i32 %54, i1 true)
  %205 = sub i32 %204, %61
  %206 = tail call i32 @llvm.smax.i32(i32 %205, i32 0)
  %207 = shl nuw i32 %206, 1
  %208 = sub i32 %204, %207
  %209 = tail call i32 @llvm.smax.i32(i32 %208, i32 0)
  %210 = tail call i32 @llvm.smin.i32(i32 %61, i32 %209)
  %211 = mul i32 %210, %80
  %212 = add i32 %78, %211
  %213 = mul i32 %212, %81
  %214 = sub i32 %213, %43
  %215 = sub i32 %214, %86
  %216 = add i32 %.025, %215
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %79, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = add i32 %99, %211
  %221 = mul i32 %220, %81
  %222 = sub i32 %221, %43
  %223 = sub i32 %222, %86
  %224 = add i32 %.025, %223
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, ptr %79, i64 %225
  %227 = load float, ptr %226, align 4
  %228 = add i32 %114, %211
  %229 = mul i32 %228, %81
  %230 = sub i32 %229, %43
  %231 = sub i32 %230, %86
  %232 = add i32 %.025, %231
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %79, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = fmul reassoc ninf nsz float %235, 3.600000e+01
  %237 = add i32 %130, %211
  %238 = mul i32 %237, %81
  %239 = sub i32 %238, %43
  %240 = sub i32 %239, %86
  %241 = add i32 %.025, %240
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, ptr %79, i64 %242
  %244 = load float, ptr %243, align 4
  %245 = add i32 %146, %211
  %246 = mul i32 %245, %81
  %247 = sub i32 %246, %43
  %248 = sub i32 %247, %86
  %249 = add i32 %.025, %248
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, ptr %79, i64 %250
  %252 = load float, ptr %251, align 4
  %253 = or disjoint i32 %54, 1
  %254 = tail call i32 @llvm.abs.i32(i32 %253, i1 true)
  %255 = sub i32 %254, %61
  %256 = tail call i32 @llvm.smax.i32(i32 %255, i32 0)
  %257 = shl nuw i32 %256, 1
  %258 = sub i32 %254, %257
  %259 = tail call i32 @llvm.smax.i32(i32 %258, i32 0)
  %260 = tail call i32 @llvm.smin.i32(i32 %61, i32 %259)
  %261 = mul i32 %260, %80
  %262 = add i32 %78, %261
  %263 = mul i32 %262, %81
  %264 = sub i32 %263, %43
  %265 = sub i32 %264, %86
  %266 = add i32 %.025, %265
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, ptr %79, i64 %267
  %269 = load float, ptr %268, align 4
  %270 = add i32 %99, %261
  %271 = mul i32 %270, %81
  %272 = sub i32 %271, %43
  %273 = sub i32 %272, %86
  %274 = add i32 %.025, %273
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, ptr %79, i64 %275
  %277 = load float, ptr %276, align 4
  %278 = add i32 %114, %261
  %279 = mul i32 %278, %81
  %280 = sub i32 %279, %43
  %281 = sub i32 %280, %86
  %282 = add i32 %.025, %281
  %283 = sext i32 %282 to i64
  %284 = getelementptr float, ptr %79, i64 %283
  %285 = load float, ptr %284, align 4
  %286 = add i32 %130, %261
  %287 = mul i32 %286, %81
  %288 = sub i32 %287, %43
  %289 = sub i32 %288, %86
  %290 = add i32 %.025, %289
  %291 = sext i32 %290 to i64
  %292 = getelementptr float, ptr %79, i64 %291
  %293 = load float, ptr %292, align 4
  %294 = add i32 %146, %261
  %295 = mul i32 %294, %81
  %296 = sub i32 %295, %43
  %297 = sub i32 %296, %86
  %298 = add i32 %.025, %297
  %299 = sext i32 %298 to i64
  %300 = getelementptr float, ptr %79, i64 %299
  %301 = load float, ptr %300, align 4
  %302 = add i32 %54, 2
  %303 = tail call i32 @llvm.abs.i32(i32 %302, i1 true)
  %304 = sub i32 %303, %61
  %305 = tail call i32 @llvm.smax.i32(i32 %304, i32 0)
  %306 = shl nuw i32 %305, 1
  %307 = sub i32 %303, %306
  %308 = tail call i32 @llvm.smax.i32(i32 %307, i32 0)
  %309 = tail call i32 @llvm.smin.i32(i32 %61, i32 %308)
  %310 = mul i32 %309, %80
  %311 = add i32 %78, %310
  %312 = mul i32 %311, %81
  %313 = sub i32 %312, %43
  %314 = sub i32 %313, %86
  %315 = add i32 %.025, %314
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, ptr %79, i64 %316
  %318 = load float, ptr %317, align 4
  %319 = add i32 %99, %310
  %320 = mul i32 %319, %81
  %321 = sub i32 %320, %43
  %322 = sub i32 %321, %86
  %323 = add i32 %.025, %322
  %324 = sext i32 %323 to i64
  %325 = getelementptr float, ptr %79, i64 %324
  %326 = load float, ptr %325, align 4
  %327 = add i32 %114, %310
  %328 = mul i32 %327, %81
  %329 = sub i32 %328, %43
  %330 = sub i32 %329, %86
  %331 = add i32 %.025, %330
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, ptr %79, i64 %332
  %334 = load float, ptr %333, align 4
  %335 = add i32 %130, %310
  %336 = mul i32 %335, %81
  %337 = sub i32 %336, %43
  %338 = sub i32 %337, %86
  %339 = add i32 %.025, %338
  %340 = sext i32 %339 to i64
  %341 = getelementptr float, ptr %79, i64 %340
  %342 = load float, ptr %341, align 4
  %343 = add i32 %146, %310
  %344 = mul i32 %343, %81
  %345 = sub i32 %344, %43
  %346 = sub i32 %345, %86
  %347 = add i32 %.025, %346
  %348 = sext i32 %347 to i64
  %349 = getelementptr float, ptr %79, i64 %348
  %350 = load float, ptr %349, align 4
  %reass.add = fadd reassoc ninf nsz float %138, %107
  %reass.add7 = fadd reassoc ninf nsz float %reass.add, %171
  %reass.add8 = fadd reassoc ninf nsz float %reass.add7, %203
  %reass.add9 = fadd reassoc ninf nsz float %reass.add8, %269
  %reass.add10 = fadd reassoc ninf nsz float %reass.add9, %301
  %reass.add11 = fadd reassoc ninf nsz float %reass.add10, %326
  %reass.add12 = fadd reassoc ninf nsz float %reass.add11, %342
  %reass.mul = fmul reassoc ninf nsz float %reass.add12, 4.000000e+00
  %reass.add13 = fadd reassoc ninf nsz float %227, %187
  %reass.add14 = fadd reassoc ninf nsz float %reass.add13, %244
  %reass.add15 = fadd reassoc ninf nsz float %reass.add14, %285
  %reass.mul16 = fmul reassoc ninf nsz float %reass.add15, 2.400000e+01
  %reass.add17 = fadd reassoc ninf nsz float %195, %179
  %reass.add18 = fadd reassoc ninf nsz float %reass.add17, %277
  %reass.add19 = fadd reassoc ninf nsz float %reass.add18, %293
  %reass.mul20 = fmul reassoc ninf nsz float %reass.add19, 1.600000e+01
  %reass.add21 = fadd reassoc ninf nsz float %219, %122
  %reass.add22 = fadd reassoc ninf nsz float %reass.add21, %252
  %reass.add23 = fadd reassoc ninf nsz float %reass.add22, %334
  %reass.mul24 = fmul reassoc ninf nsz float %reass.add23, 6.000000e+00
  %351 = fadd reassoc ninf nsz float %154, %91
  %352 = fadd reassoc ninf nsz float %351, %236
  %353 = fadd reassoc ninf nsz float %352, %318
  %354 = fadd reassoc ninf nsz float %353, %reass.mul16
  %355 = fadd reassoc ninf nsz float %354, %reass.mul20
  %356 = fadd reassoc ninf nsz float %355, %350
  %357 = fadd reassoc ninf nsz float %356, %reass.mul24
  %358 = fadd reassoc ninf nsz float %357, %reass.mul
  %359 = fmul reassoc ninf nsz float %358, 3.906250e-03
  %360 = load ptr, ptr %28, align 8
  %361 = load i32, ptr %29, align 4
  %362 = load i32, ptr %30, align 4
  %363 = mul i32 %361, %42
  %364 = add i32 %363, %52
  %365 = mul i32 %364, %362
  %366 = sub i32 %365, %43
  %367 = sub i32 %366, %86
  %368 = add i32 %.025, %367
  %369 = sext i32 %368 to i64
  %370 = getelementptr float, ptr %360, i64 %369
  store float %359, ptr %370, align 4
  %371 = add nsw i32 %.025, 1
  %exitcond.not = icmp eq i32 %18, %371
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.abs.i32(i32, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
