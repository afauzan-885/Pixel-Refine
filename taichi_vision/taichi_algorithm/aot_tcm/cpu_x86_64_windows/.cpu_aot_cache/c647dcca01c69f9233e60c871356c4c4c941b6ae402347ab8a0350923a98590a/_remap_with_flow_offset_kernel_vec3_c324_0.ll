; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.31 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_remap_with_flow_offset_kernel_vec3_c324_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 40
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 44
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 32872
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 4
  store i32 %6, ptr %11, align 4
  %12 = mul i32 %6, %3
  %13 = load ptr, ptr %7, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  store i32 %12, ptr %15, align 4
  ret void
}

define void @_remap_with_flow_offset_kernel_vec3_c324_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %14 = add i32 %9, %.neg
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 88
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 92
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 76
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 68
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 72
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 64
  %31 = load i32, ptr %30, align 4
  %32 = getelementptr i8, ptr %19, i64 80
  %33 = load float, ptr %32, align 4
  %34 = getelementptr i8, ptr %19, i64 84
  %35 = load float, ptr %34, align 4
  %36 = getelementptr i8, ptr %19, i64 56
  %37 = load i32, ptr %36, align 4
  %38 = getelementptr i8, ptr %19, i64 60
  %39 = load i32, ptr %38, align 4
  %40 = add i32 %25, -1
  %41 = add i32 %27, -1
  %42 = add i32 %29, -1
  %43 = add i32 %31, -1
  %44 = add i32 %39, -1
  %45 = add i32 %37, -1
  %46 = sitofp i32 %40 to float
  %47 = sitofp i32 %41 to float
  %48 = sitofp i32 %42 to float
  %49 = sitofp i32 %43 to float
  %50 = icmp slt i32 %16, %18
  br i1 %50, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %51 = getelementptr i8, ptr %19, i64 32
  %52 = getelementptr i8, ptr %19, i64 20
  %53 = getelementptr i8, ptr %19, i64 24
  %54 = getelementptr i8, ptr %19, i64 8
  %55 = getelementptr i8, ptr %19, i64 4
  %56 = getelementptr i8, ptr %19, i64 48
  %57 = getelementptr i8, ptr %19, i64 44
  %58 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %58, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %334, %for_loop_body ]
  %59 = load ptr, ptr %3, align 8
  %60 = getelementptr inbounds nuw i8, ptr %59, i64 32872
  %61 = load ptr, ptr %60, align 8
  %62 = getelementptr inbounds nuw i8, ptr %61, i64 4
  %63 = load i32, ptr %62, align 4
  %64 = sdiv i32 %.05, %63
  %65 = mul i32 %64, %63
  %66 = xor i32 %63, %.05
  %67 = icmp slt i32 %66, 0
  %68 = icmp ne i32 %.05, %65
  %69 = and i1 %67, %68
  %.neg4 = sext i1 %69 to i32
  %70 = add i32 %64, %.neg4
  %71 = add i32 %70, %21
  %72 = mul i32 %63, -1
  %73 = mul i32 %72, %70
  %74 = add i32 %23, %.05
  %75 = add i32 %74, %73
  %76 = sitofp i32 %75 to float
  %77 = fmul reassoc ninf nsz float %76, %46
  %78 = fdiv reassoc ninf nsz float %77, %47
  %79 = sitofp i32 %71 to float
  %80 = fmul reassoc ninf nsz float %79, %48
  %81 = fdiv reassoc ninf nsz float %80, %49
  %82 = tail call reassoc ninf nsz float @llvm.floor.f32(float %78)
  %83 = fptosi float %82 to i32
  %84 = tail call reassoc ninf nsz float @llvm.floor.f32(float %81)
  %85 = fptosi float %84 to i32
  %86 = sitofp i32 %83 to float
  %87 = fsub reassoc ninf nsz float %78, %86
  %88 = sitofp i32 %85 to float
  %89 = fsub reassoc ninf nsz float %81, %88
  %90 = tail call i32 @llvm.abs.i32(i32 %83, i1 true)
  %91 = sub i32 %90, %40
  %92 = tail call i32 @llvm.smax.i32(i32 %91, i32 0)
  %93 = shl nuw i32 %92, 1
  %94 = sub i32 %90, %93
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %40, i32 %95)
  %97 = tail call i32 @llvm.abs.i32(i32 %85, i1 true)
  %98 = sub i32 %97, %42
  %99 = tail call i32 @llvm.smax.i32(i32 %98, i32 0)
  %100 = shl nuw i32 %99, 1
  %101 = sub i32 %97, %100
  %102 = tail call i32 @llvm.smax.i32(i32 %101, i32 0)
  %103 = tail call i32 @llvm.smin.i32(i32 %42, i32 %102)
  %104 = add i32 %83, 1
  %105 = tail call i32 @llvm.abs.i32(i32 %104, i1 true)
  %106 = sub i32 %105, %40
  %107 = tail call i32 @llvm.smax.i32(i32 %106, i32 0)
  %108 = shl nuw i32 %107, 1
  %109 = sub i32 %105, %108
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %111 = tail call i32 @llvm.smin.i32(i32 %40, i32 %110)
  %112 = add i32 %85, 1
  %113 = tail call i32 @llvm.abs.i32(i32 %112, i1 true)
  %114 = sub i32 %113, %42
  %115 = tail call i32 @llvm.smax.i32(i32 %114, i32 0)
  %116 = shl nuw i32 %115, 1
  %117 = sub i32 %113, %116
  %118 = tail call i32 @llvm.smax.i32(i32 %117, i32 0)
  %119 = tail call i32 @llvm.smin.i32(i32 %42, i32 %118)
  %120 = load ptr, ptr %51, align 8
  %121 = load i32, ptr %52, align 4
  %122 = load i32, ptr %53, align 4
  %123 = mul i32 %103, %121
  %124 = add i32 %96, %123
  %125 = mul i32 %124, %122
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %120, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = add i32 %111, %123
  %130 = mul i32 %129, %122
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, ptr %120, i64 %131
  %133 = load float, ptr %132, align 4
  %134 = mul i32 %119, %121
  %135 = add i32 %134, %96
  %136 = mul i32 %135, %122
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %120, i64 %137
  %139 = load float, ptr %138, align 4
  %140 = add i32 %111, %134
  %141 = mul i32 %140, %122
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %120, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = fsub reassoc ninf nsz float 1.000000e+00, %87
  %146 = fmul reassoc ninf nsz float %145, %128
  %147 = fmul reassoc ninf nsz float %87, %133
  %148 = fadd reassoc ninf nsz float %146, %147
  %149 = fmul reassoc ninf nsz float %145, %139
  %150 = fmul reassoc ninf nsz float %87, %144
  %151 = fadd reassoc ninf nsz float %149, %150
  %152 = fsub reassoc ninf nsz float 1.000000e+00, %89
  %153 = fmul reassoc ninf nsz float %148, %152
  %154 = fmul reassoc ninf nsz float %151, %89
  %155 = fadd reassoc ninf nsz float %153, %154
  %156 = add i32 %125, 1
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %120, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = add i32 %130, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %120, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = add i32 %136, 1
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %120, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = add i32 %141, 1
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %120, i64 %169
  %171 = load float, ptr %170, align 4
  %172 = fmul reassoc ninf nsz float %145, %159
  %173 = fmul reassoc ninf nsz float %87, %163
  %174 = fadd reassoc ninf nsz float %172, %173
  %175 = fmul reassoc ninf nsz float %145, %167
  %176 = fmul reassoc ninf nsz float %87, %171
  %177 = fadd reassoc ninf nsz float %175, %176
  %178 = fmul reassoc ninf nsz float %174, %152
  %179 = fmul reassoc ninf nsz float %177, %89
  %180 = fadd reassoc ninf nsz float %178, %179
  %181 = fmul reassoc ninf nsz float %155, %33
  %182 = fadd reassoc ninf nsz float %181, %76
  %183 = fmul reassoc ninf nsz float %180, %35
  %184 = fadd reassoc ninf nsz float %183, %79
  %185 = tail call reassoc ninf nsz float @llvm.floor.f32(float %182)
  %186 = fptosi float %185 to i32
  %187 = tail call reassoc ninf nsz float @llvm.floor.f32(float %184)
  %188 = fptosi float %187 to i32
  %189 = sitofp i32 %186 to float
  %190 = fsub reassoc ninf nsz float %182, %189
  %191 = sitofp i32 %188 to float
  %192 = fsub reassoc ninf nsz float %184, %191
  %193 = tail call i32 @llvm.abs.i32(i32 %186, i1 true)
  %194 = sub i32 %193, %44
  %195 = tail call i32 @llvm.smax.i32(i32 %194, i32 0)
  %196 = shl nuw i32 %195, 1
  %197 = sub i32 %193, %196
  %198 = tail call i32 @llvm.smax.i32(i32 %197, i32 0)
  %199 = tail call i32 @llvm.smin.i32(i32 %44, i32 %198)
  %200 = tail call i32 @llvm.abs.i32(i32 %188, i1 true)
  %201 = sub i32 %200, %45
  %202 = tail call i32 @llvm.smax.i32(i32 %201, i32 0)
  %203 = shl nuw i32 %202, 1
  %204 = sub i32 %200, %203
  %205 = tail call i32 @llvm.smax.i32(i32 %204, i32 0)
  %206 = tail call i32 @llvm.smin.i32(i32 %45, i32 %205)
  %207 = add i32 %186, 1
  %208 = tail call i32 @llvm.abs.i32(i32 %207, i1 true)
  %209 = sub i32 %208, %44
  %210 = tail call i32 @llvm.smax.i32(i32 %209, i32 0)
  %211 = shl nuw i32 %210, 1
  %212 = sub i32 %208, %211
  %213 = tail call i32 @llvm.smax.i32(i32 %212, i32 0)
  %214 = tail call i32 @llvm.smin.i32(i32 %44, i32 %213)
  %215 = add i32 %188, 1
  %216 = tail call i32 @llvm.abs.i32(i32 %215, i1 true)
  %217 = sub i32 %216, %45
  %218 = tail call i32 @llvm.smax.i32(i32 %217, i32 0)
  %219 = shl nuw i32 %218, 1
  %220 = sub i32 %216, %219
  %221 = tail call i32 @llvm.smax.i32(i32 %220, i32 0)
  %222 = tail call i32 @llvm.smin.i32(i32 %45, i32 %221)
  %223 = load ptr, ptr %54, align 8
  %224 = load i32, ptr %55, align 4
  %225 = mul i32 %206, %224
  %226 = add i32 %225, %199
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
  %239 = add i32 %225, %214
  %240 = mul i32 %239, 3
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %223, i64 %241
  %243 = load float, ptr %242, align 4
  %244 = add i32 %240, 1
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, ptr %223, i64 %245
  %247 = load float, ptr %246, align 4
  %248 = add i32 %240, 2
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, ptr %223, i64 %249
  %251 = load float, ptr %250, align 4
  %252 = mul i32 %222, %224
  %253 = add i32 %252, %199
  %254 = mul i32 %253, 3
  %255 = sext i32 %254 to i64
  %256 = getelementptr float, ptr %223, i64 %255
  %257 = load float, ptr %256, align 4
  %258 = add i32 %254, 1
  %259 = sext i32 %258 to i64
  %260 = getelementptr float, ptr %223, i64 %259
  %261 = load float, ptr %260, align 4
  %262 = add i32 %254, 2
  %263 = sext i32 %262 to i64
  %264 = getelementptr float, ptr %223, i64 %263
  %265 = load float, ptr %264, align 4
  %266 = add i32 %252, %214
  %267 = mul i32 %266, 3
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, ptr %223, i64 %268
  %270 = load float, ptr %269, align 4
  %271 = add i32 %267, 1
  %272 = sext i32 %271 to i64
  %273 = getelementptr float, ptr %223, i64 %272
  %274 = load float, ptr %273, align 4
  %275 = add i32 %267, 2
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, ptr %223, i64 %276
  %278 = load float, ptr %277, align 4
  %279 = fsub reassoc ninf nsz float 1.000000e+00, %190
  %280 = fmul reassoc ninf nsz float %279, %230
  %281 = fmul reassoc ninf nsz float %279, %234
  %282 = fmul reassoc ninf nsz float %279, %238
  %283 = fmul reassoc ninf nsz float %190, %243
  %284 = fmul reassoc ninf nsz float %190, %247
  %285 = fmul reassoc ninf nsz float %190, %251
  %286 = fadd reassoc ninf nsz float %280, %283
  %287 = fadd reassoc ninf nsz float %281, %284
  %288 = fadd reassoc ninf nsz float %282, %285
  %289 = fmul reassoc ninf nsz float %279, %257
  %290 = fmul reassoc ninf nsz float %279, %261
  %291 = fmul reassoc ninf nsz float %279, %265
  %292 = fmul reassoc ninf nsz float %190, %270
  %293 = fmul reassoc ninf nsz float %190, %274
  %294 = fmul reassoc ninf nsz float %190, %278
  %295 = fadd reassoc ninf nsz float %289, %292
  %296 = fadd reassoc ninf nsz float %290, %293
  %297 = fadd reassoc ninf nsz float %291, %294
  %298 = fsub reassoc ninf nsz float 1.000000e+00, %192
  %299 = fmul reassoc ninf nsz float %286, %298
  %300 = fmul reassoc ninf nsz float %287, %298
  %301 = fmul reassoc ninf nsz float %288, %298
  %302 = fmul reassoc ninf nsz float %295, %192
  %303 = fmul reassoc ninf nsz float %296, %192
  %304 = fmul reassoc ninf nsz float %297, %192
  %305 = fadd reassoc ninf nsz float %299, %302
  %306 = fadd reassoc ninf nsz float %300, %303
  %307 = fadd reassoc ninf nsz float %301, %304
  %308 = load ptr, ptr %56, align 8
  %309 = load i32, ptr %57, align 4
  %310 = sub i32 %309, %63
  %311 = mul i32 %310, 3
  %312 = mul i32 %311, %70
  %313 = add i32 %lsr.iv, %312
  %314 = sext i32 %313 to i64
  %315 = getelementptr float, ptr %308, i64 %314
  store float %305, ptr %315, align 4
  %316 = load ptr, ptr %56, align 8
  %317 = load i32, ptr %57, align 4
  %318 = sub i32 %317, %63
  %319 = mul i32 %318, 3
  %320 = mul i32 %319, %70
  %321 = add i32 %lsr.iv, %320
  %322 = add i32 %321, 1
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, ptr %316, i64 %323
  store float %306, ptr %324, align 4
  %325 = load ptr, ptr %56, align 8
  %326 = load i32, ptr %57, align 4
  %327 = sub i32 %326, %63
  %328 = mul i32 %327, 3
  %329 = mul i32 %328, %70
  %330 = add i32 %lsr.iv, %329
  %331 = add i32 %330, 2
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, ptr %325, i64 %332
  store float %307, ptr %333, align 4
  %334 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %334
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
  %4 = alloca %struct.RuntimeContext.31, align 8
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #5

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
