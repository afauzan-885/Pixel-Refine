; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_poly_exp_horizontal_kernel_c504_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 52
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 8
  store i32 %5, ptr %10, align 4
  %11 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %12 = load ptr, ptr %6, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 4
  store i32 %11, ptr %15, align 4
  %16 = mul i32 %11, %3
  %17 = load ptr, ptr %6, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  store i32 %16, ptr %19, align 4
  ret void
}

define void @_poly_exp_horizontal_kernel_c504_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 88
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 72
  %23 = load float, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 76
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 80
  %27 = load float, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 84
  %29 = load float, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 64
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr i8, ptr %19, i64 60
  %33 = icmp sgt i32 %21, 0
  %34 = icmp sgt i32 %21, 1
  %35 = icmp sgt i32 %21, 2
  %36 = icmp sgt i32 %21, 3
  %37 = icmp sgt i32 %21, 4
  %38 = icmp sgt i32 %21, 5
  %39 = icmp sgt i32 %21, 6
  %40 = icmp sgt i32 %21, 7
  %41 = icmp sgt i32 %21, 8
  %42 = icmp sgt i32 %21, 9
  %43 = icmp sgt i32 %21, 10
  %44 = icmp slt i32 %16, %18
  br i1 %44, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %45 = getelementptr i8, ptr %19, i64 16
  %46 = getelementptr i8, ptr %19, i64 4
  %47 = getelementptr i8, ptr %19, i64 8
  %48 = getelementptr i8, ptr %19, i64 40
  %49 = getelementptr i8, ptr %19, i64 28
  %50 = getelementptr i8, ptr %19, i64 32
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if30, %for_loop_body.lr.ph
  %.0124186 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %804, %after_if30 ]
  %51 = load ptr, ptr %3, align 8
  %52 = getelementptr inbounds nuw i8, ptr %51, i64 32872
  %53 = load ptr, ptr %52, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 4
  %55 = load i32, ptr %54, align 4
  %56 = sdiv i32 %.0124186, %55
  %57 = mul i32 %56, %55
  %58 = xor i32 %55, %.0124186
  %59 = icmp slt i32 %58, 0
  %60 = icmp ne i32 %.0124186, %57
  %61 = and i1 %59, %60
  %.neg125 = sext i1 %61 to i32
  %62 = add i32 %56, %.neg125
  %63 = load ptr, ptr %45, align 8
  %64 = load i32, ptr %46, align 4
  %65 = load i32, ptr %47, align 4
  %66 = mul i32 %62, %64
  %67 = sub i32 %64, %55
  %68 = mul i32 %67, %62
  %69 = add i32 %.0124186, %68
  %70 = mul i32 %69, %65
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, ptr %63, i64 %71
  %73 = load float, ptr %72, align 4
  %74 = load float, ptr %31, align 4
  %75 = fmul reassoc ninf nsz float %74, %73
  %76 = add i32 %70, 1
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, ptr %63, i64 %77
  %79 = load float, ptr %78, align 4
  %80 = fmul reassoc ninf nsz float %79, %74
  %81 = add i32 %70, 2
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, ptr %63, i64 %82
  %84 = load float, ptr %83, align 4
  %85 = fmul reassoc ninf nsz float %84, %74
  br i1 %33, label %after_if, label %after_if30

after_for.loopexit:                               ; preds = %after_if30
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %86 = mul i32 %55, -1
  %87 = mul i32 %86, %62
  %88 = add i32 %.0124186, %87
  %89 = add i32 %88, -1
  %90 = getelementptr inbounds nuw i8, ptr %53, i64 8
  %91 = load i32, ptr %90, align 4
  %92 = add i32 %91, -1
  %93 = tail call i32 @llvm.smin.i32(i32 %89, i32 %92)
  %94 = tail call i32 @llvm.smax.i32(i32 %93, i32 0)
  %95 = add i32 %88, 1
  %96 = tail call i32 @llvm.smin.i32(i32 %95, i32 %92)
  %97 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %98 = add i32 %94, %66
  %99 = mul i32 %98, %65
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %63, i64 %100
  %102 = load float, ptr %101, align 4
  %103 = add i32 %97, %66
  %104 = mul i32 %103, %65
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, ptr %63, i64 %105
  %107 = load float, ptr %106, align 4
  %108 = add i32 %99, 1
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %63, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = add i32 %104, 1
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %63, i64 %113
  %115 = load float, ptr %114, align 4
  %116 = add i32 %99, 2
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %63, i64 %117
  %119 = load float, ptr %118, align 4
  %120 = add i32 %104, 2
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %63, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = fadd reassoc ninf nsz float %107, %102
  %125 = load ptr, ptr %30, align 8
  %126 = load i32, ptr %32, align 4
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %125, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = fmul reassoc ninf nsz float %129, %124
  %131 = fadd reassoc ninf nsz float %130, %75
  %132 = add i32 %126, 2
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %125, i64 %133
  %135 = load float, ptr %134, align 4
  %136 = fmul reassoc ninf nsz float %135, %124
  %137 = fsub reassoc ninf nsz float %107, %102
  %138 = add i32 %126, 1
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, ptr %125, i64 %139
  %141 = load float, ptr %140, align 4
  %142 = fmul reassoc ninf nsz float %141, %137
  %143 = fadd reassoc ninf nsz float %115, %111
  %144 = fmul reassoc ninf nsz float %129, %143
  %145 = fadd reassoc ninf nsz float %144, %80
  %146 = fsub reassoc ninf nsz float %115, %111
  %147 = fmul reassoc ninf nsz float %141, %146
  %148 = fadd reassoc ninf nsz float %123, %119
  %149 = fmul reassoc ninf nsz float %129, %148
  %150 = fadd reassoc ninf nsz float %149, %85
  br i1 %34, label %after_if3, label %after_if30

after_if3:                                        ; preds = %after_if
  %151 = add i32 %88, -2
  %152 = tail call i32 @llvm.smin.i32(i32 %151, i32 %92)
  %153 = tail call i32 @llvm.smax.i32(i32 %152, i32 0)
  %154 = add i32 %88, 2
  %155 = tail call i32 @llvm.smin.i32(i32 %154, i32 %92)
  %156 = tail call i32 @llvm.smax.i32(i32 %155, i32 0)
  %157 = add i32 %153, %66
  %158 = mul i32 %157, %65
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %63, i64 %159
  %161 = load float, ptr %160, align 4
  %162 = add i32 %156, %66
  %163 = mul i32 %162, %65
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %63, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = add i32 %158, 1
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, ptr %63, i64 %168
  %170 = load float, ptr %169, align 4
  %171 = add i32 %163, 1
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %63, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = add i32 %158, 2
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, ptr %63, i64 %176
  %178 = load float, ptr %177, align 4
  %179 = add i32 %163, 2
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %63, i64 %180
  %182 = load float, ptr %181, align 4
  %183 = fadd reassoc ninf nsz float %166, %161
  %184 = shl i32 %126, 1
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, ptr %125, i64 %185
  %187 = load float, ptr %186, align 4
  %188 = fmul reassoc ninf nsz float %187, %183
  %189 = fadd reassoc ninf nsz float %188, %131
  %190 = add i32 %184, 2
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, ptr %125, i64 %191
  %193 = load float, ptr %192, align 4
  %194 = fmul reassoc ninf nsz float %193, %183
  %195 = fadd reassoc ninf nsz float %194, %136
  %196 = fsub reassoc ninf nsz float %166, %161
  %197 = getelementptr i8, ptr %186, i64 4
  %198 = load float, ptr %197, align 4
  %199 = fmul reassoc ninf nsz float %198, %196
  %200 = fadd reassoc ninf nsz float %199, %142
  %201 = fadd reassoc ninf nsz float %174, %170
  %202 = fmul reassoc ninf nsz float %187, %201
  %203 = fadd reassoc ninf nsz float %202, %145
  %204 = fsub reassoc ninf nsz float %174, %170
  %205 = fmul reassoc ninf nsz float %198, %204
  %206 = fadd reassoc ninf nsz float %205, %147
  %207 = fadd reassoc ninf nsz float %182, %178
  %208 = fmul reassoc ninf nsz float %187, %207
  %209 = fadd reassoc ninf nsz float %208, %150
  br i1 %35, label %after_if6, label %after_if30

after_if6:                                        ; preds = %after_if3
  %210 = add i32 %88, -3
  %211 = tail call i32 @llvm.smin.i32(i32 %210, i32 %92)
  %212 = tail call i32 @llvm.smax.i32(i32 %211, i32 0)
  %213 = add i32 %88, 3
  %214 = tail call i32 @llvm.smin.i32(i32 %213, i32 %92)
  %215 = tail call i32 @llvm.smax.i32(i32 %214, i32 0)
  %216 = add i32 %212, %66
  %217 = mul i32 %216, %65
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, ptr %63, i64 %218
  %220 = load float, ptr %219, align 4
  %221 = add i32 %215, %66
  %222 = mul i32 %221, %65
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %63, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = add i32 %217, 1
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %63, i64 %227
  %229 = load float, ptr %228, align 4
  %230 = add i32 %222, 1
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, ptr %63, i64 %231
  %233 = load float, ptr %232, align 4
  %234 = add i32 %217, 2
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %63, i64 %235
  %237 = load float, ptr %236, align 4
  %238 = add i32 %222, 2
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, ptr %63, i64 %239
  %241 = load float, ptr %240, align 4
  %242 = fadd reassoc ninf nsz float %225, %220
  %243 = mul i32 %126, 3
  %244 = sext i32 %243 to i64
  %245 = getelementptr float, ptr %125, i64 %244
  %246 = load float, ptr %245, align 4
  %247 = fmul reassoc ninf nsz float %246, %242
  %248 = fadd reassoc ninf nsz float %247, %189
  %249 = add i32 %243, 2
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, ptr %125, i64 %250
  %252 = load float, ptr %251, align 4
  %253 = fmul reassoc ninf nsz float %252, %242
  %254 = fadd reassoc ninf nsz float %253, %195
  %255 = fsub reassoc ninf nsz float %225, %220
  %256 = add i32 %243, 1
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, ptr %125, i64 %257
  %259 = load float, ptr %258, align 4
  %260 = fmul reassoc ninf nsz float %259, %255
  %261 = fadd reassoc ninf nsz float %260, %200
  %262 = fadd reassoc ninf nsz float %233, %229
  %263 = fmul reassoc ninf nsz float %246, %262
  %264 = fadd reassoc ninf nsz float %263, %203
  %265 = fsub reassoc ninf nsz float %233, %229
  %266 = fmul reassoc ninf nsz float %259, %265
  %267 = fadd reassoc ninf nsz float %266, %206
  %268 = fadd reassoc ninf nsz float %241, %237
  %269 = fmul reassoc ninf nsz float %246, %268
  %270 = fadd reassoc ninf nsz float %269, %209
  br i1 %36, label %after_if9, label %after_if30

after_if9:                                        ; preds = %after_if6
  %271 = add i32 %88, -4
  %272 = tail call i32 @llvm.smin.i32(i32 %271, i32 %92)
  %273 = tail call i32 @llvm.smax.i32(i32 %272, i32 0)
  %274 = add i32 %88, 4
  %275 = tail call i32 @llvm.smin.i32(i32 %274, i32 %92)
  %276 = tail call i32 @llvm.smax.i32(i32 %275, i32 0)
  %277 = add i32 %273, %66
  %278 = mul i32 %277, %65
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, ptr %63, i64 %279
  %281 = load float, ptr %280, align 4
  %282 = add i32 %276, %66
  %283 = mul i32 %282, %65
  %284 = sext i32 %283 to i64
  %285 = getelementptr float, ptr %63, i64 %284
  %286 = load float, ptr %285, align 4
  %287 = add i32 %278, 1
  %288 = sext i32 %287 to i64
  %289 = getelementptr float, ptr %63, i64 %288
  %290 = load float, ptr %289, align 4
  %291 = add i32 %283, 1
  %292 = sext i32 %291 to i64
  %293 = getelementptr float, ptr %63, i64 %292
  %294 = load float, ptr %293, align 4
  %295 = add i32 %278, 2
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, ptr %63, i64 %296
  %298 = load float, ptr %297, align 4
  %299 = add i32 %283, 2
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, ptr %63, i64 %300
  %302 = load float, ptr %301, align 4
  %303 = fadd reassoc ninf nsz float %286, %281
  %304 = shl i32 %126, 2
  %305 = sext i32 %304 to i64
  %306 = getelementptr float, ptr %125, i64 %305
  %307 = load float, ptr %306, align 4
  %308 = fmul reassoc ninf nsz float %307, %303
  %309 = fadd reassoc ninf nsz float %308, %248
  %310 = getelementptr i8, ptr %306, i64 8
  %311 = load float, ptr %310, align 4
  %312 = fmul reassoc ninf nsz float %311, %303
  %313 = fadd reassoc ninf nsz float %312, %254
  %314 = fsub reassoc ninf nsz float %286, %281
  %315 = getelementptr i8, ptr %306, i64 4
  %316 = load float, ptr %315, align 4
  %317 = fmul reassoc ninf nsz float %316, %314
  %318 = fadd reassoc ninf nsz float %317, %261
  %319 = fadd reassoc ninf nsz float %294, %290
  %320 = fmul reassoc ninf nsz float %307, %319
  %321 = fadd reassoc ninf nsz float %320, %264
  %322 = fsub reassoc ninf nsz float %294, %290
  %323 = fmul reassoc ninf nsz float %316, %322
  %324 = fadd reassoc ninf nsz float %323, %267
  %325 = fadd reassoc ninf nsz float %302, %298
  %326 = fmul reassoc ninf nsz float %307, %325
  %327 = fadd reassoc ninf nsz float %326, %270
  br i1 %37, label %after_if12, label %after_if30

after_if12:                                       ; preds = %after_if9
  %328 = add i32 %88, -5
  %329 = tail call i32 @llvm.smin.i32(i32 %328, i32 %92)
  %330 = tail call i32 @llvm.smax.i32(i32 %329, i32 0)
  %331 = add i32 %88, 5
  %332 = tail call i32 @llvm.smin.i32(i32 %331, i32 %92)
  %333 = tail call i32 @llvm.smax.i32(i32 %332, i32 0)
  %334 = add i32 %330, %66
  %335 = mul i32 %334, %65
  %336 = sext i32 %335 to i64
  %337 = getelementptr float, ptr %63, i64 %336
  %338 = load float, ptr %337, align 4
  %339 = add i32 %333, %66
  %340 = mul i32 %339, %65
  %341 = sext i32 %340 to i64
  %342 = getelementptr float, ptr %63, i64 %341
  %343 = load float, ptr %342, align 4
  %344 = add i32 %335, 1
  %345 = sext i32 %344 to i64
  %346 = getelementptr float, ptr %63, i64 %345
  %347 = load float, ptr %346, align 4
  %348 = add i32 %340, 1
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, ptr %63, i64 %349
  %351 = load float, ptr %350, align 4
  %352 = add i32 %335, 2
  %353 = sext i32 %352 to i64
  %354 = getelementptr float, ptr %63, i64 %353
  %355 = load float, ptr %354, align 4
  %356 = add i32 %340, 2
  %357 = sext i32 %356 to i64
  %358 = getelementptr float, ptr %63, i64 %357
  %359 = load float, ptr %358, align 4
  %360 = fadd reassoc ninf nsz float %343, %338
  %361 = mul i32 %126, 5
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, ptr %125, i64 %362
  %364 = load float, ptr %363, align 4
  %365 = fmul reassoc ninf nsz float %364, %360
  %366 = fadd reassoc ninf nsz float %365, %309
  %367 = add i32 %361, 2
  %368 = sext i32 %367 to i64
  %369 = getelementptr float, ptr %125, i64 %368
  %370 = load float, ptr %369, align 4
  %371 = fmul reassoc ninf nsz float %370, %360
  %372 = fadd reassoc ninf nsz float %371, %313
  %373 = fsub reassoc ninf nsz float %343, %338
  %374 = add i32 %361, 1
  %375 = sext i32 %374 to i64
  %376 = getelementptr float, ptr %125, i64 %375
  %377 = load float, ptr %376, align 4
  %378 = fmul reassoc ninf nsz float %377, %373
  %379 = fadd reassoc ninf nsz float %378, %318
  %380 = fadd reassoc ninf nsz float %351, %347
  %381 = fmul reassoc ninf nsz float %364, %380
  %382 = fadd reassoc ninf nsz float %381, %321
  %383 = fsub reassoc ninf nsz float %351, %347
  %384 = fmul reassoc ninf nsz float %377, %383
  %385 = fadd reassoc ninf nsz float %384, %324
  %386 = fadd reassoc ninf nsz float %359, %355
  %387 = fmul reassoc ninf nsz float %364, %386
  %388 = fadd reassoc ninf nsz float %387, %327
  br i1 %38, label %after_if15, label %after_if30

after_if15:                                       ; preds = %after_if12
  %389 = add i32 %88, -6
  %390 = tail call i32 @llvm.smin.i32(i32 %389, i32 %92)
  %391 = tail call i32 @llvm.smax.i32(i32 %390, i32 0)
  %392 = add i32 %88, 6
  %393 = tail call i32 @llvm.smin.i32(i32 %392, i32 %92)
  %394 = tail call i32 @llvm.smax.i32(i32 %393, i32 0)
  %395 = add i32 %391, %66
  %396 = mul i32 %395, %65
  %397 = sext i32 %396 to i64
  %398 = getelementptr float, ptr %63, i64 %397
  %399 = load float, ptr %398, align 4
  %400 = add i32 %394, %66
  %401 = mul i32 %400, %65
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, ptr %63, i64 %402
  %404 = load float, ptr %403, align 4
  %405 = add i32 %396, 1
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, ptr %63, i64 %406
  %408 = load float, ptr %407, align 4
  %409 = add i32 %401, 1
  %410 = sext i32 %409 to i64
  %411 = getelementptr float, ptr %63, i64 %410
  %412 = load float, ptr %411, align 4
  %413 = add i32 %396, 2
  %414 = sext i32 %413 to i64
  %415 = getelementptr float, ptr %63, i64 %414
  %416 = load float, ptr %415, align 4
  %417 = add i32 %401, 2
  %418 = sext i32 %417 to i64
  %419 = getelementptr float, ptr %63, i64 %418
  %420 = load float, ptr %419, align 4
  %421 = fadd reassoc ninf nsz float %404, %399
  %422 = mul i32 %126, 6
  %423 = sext i32 %422 to i64
  %424 = getelementptr float, ptr %125, i64 %423
  %425 = load float, ptr %424, align 4
  %426 = fmul reassoc ninf nsz float %425, %421
  %427 = fadd reassoc ninf nsz float %426, %366
  %428 = add i32 %422, 2
  %429 = sext i32 %428 to i64
  %430 = getelementptr float, ptr %125, i64 %429
  %431 = load float, ptr %430, align 4
  %432 = fmul reassoc ninf nsz float %431, %421
  %433 = fadd reassoc ninf nsz float %432, %372
  %434 = fsub reassoc ninf nsz float %404, %399
  %435 = getelementptr i8, ptr %424, i64 4
  %436 = load float, ptr %435, align 4
  %437 = fmul reassoc ninf nsz float %436, %434
  %438 = fadd reassoc ninf nsz float %437, %379
  %439 = fadd reassoc ninf nsz float %412, %408
  %440 = fmul reassoc ninf nsz float %425, %439
  %441 = fadd reassoc ninf nsz float %440, %382
  %442 = fsub reassoc ninf nsz float %412, %408
  %443 = fmul reassoc ninf nsz float %436, %442
  %444 = fadd reassoc ninf nsz float %443, %385
  %445 = fadd reassoc ninf nsz float %420, %416
  %446 = fmul reassoc ninf nsz float %425, %445
  %447 = fadd reassoc ninf nsz float %446, %388
  br i1 %39, label %after_if18, label %after_if30

after_if18:                                       ; preds = %after_if15
  %448 = add i32 %88, -7
  %449 = tail call i32 @llvm.smin.i32(i32 %448, i32 %92)
  %450 = tail call i32 @llvm.smax.i32(i32 %449, i32 0)
  %451 = add i32 %88, 7
  %452 = tail call i32 @llvm.smin.i32(i32 %451, i32 %92)
  %453 = tail call i32 @llvm.smax.i32(i32 %452, i32 0)
  %454 = add i32 %450, %66
  %455 = mul i32 %454, %65
  %456 = sext i32 %455 to i64
  %457 = getelementptr float, ptr %63, i64 %456
  %458 = load float, ptr %457, align 4
  %459 = add i32 %453, %66
  %460 = mul i32 %459, %65
  %461 = sext i32 %460 to i64
  %462 = getelementptr float, ptr %63, i64 %461
  %463 = load float, ptr %462, align 4
  %464 = add i32 %455, 1
  %465 = sext i32 %464 to i64
  %466 = getelementptr float, ptr %63, i64 %465
  %467 = load float, ptr %466, align 4
  %468 = add i32 %460, 1
  %469 = sext i32 %468 to i64
  %470 = getelementptr float, ptr %63, i64 %469
  %471 = load float, ptr %470, align 4
  %472 = add i32 %455, 2
  %473 = sext i32 %472 to i64
  %474 = getelementptr float, ptr %63, i64 %473
  %475 = load float, ptr %474, align 4
  %476 = add i32 %460, 2
  %477 = sext i32 %476 to i64
  %478 = getelementptr float, ptr %63, i64 %477
  %479 = load float, ptr %478, align 4
  %480 = fadd reassoc ninf nsz float %463, %458
  %481 = mul i32 %126, 7
  %482 = sext i32 %481 to i64
  %483 = getelementptr float, ptr %125, i64 %482
  %484 = load float, ptr %483, align 4
  %485 = fmul reassoc ninf nsz float %484, %480
  %486 = fadd reassoc ninf nsz float %485, %427
  %487 = add i32 %481, 2
  %488 = sext i32 %487 to i64
  %489 = getelementptr float, ptr %125, i64 %488
  %490 = load float, ptr %489, align 4
  %491 = fmul reassoc ninf nsz float %490, %480
  %492 = fadd reassoc ninf nsz float %491, %433
  %493 = fsub reassoc ninf nsz float %463, %458
  %494 = add i32 %481, 1
  %495 = sext i32 %494 to i64
  %496 = getelementptr float, ptr %125, i64 %495
  %497 = load float, ptr %496, align 4
  %498 = fmul reassoc ninf nsz float %497, %493
  %499 = fadd reassoc ninf nsz float %498, %438
  %500 = fadd reassoc ninf nsz float %471, %467
  %501 = fmul reassoc ninf nsz float %484, %500
  %502 = fadd reassoc ninf nsz float %501, %441
  %503 = fsub reassoc ninf nsz float %471, %467
  %504 = fmul reassoc ninf nsz float %497, %503
  %505 = fadd reassoc ninf nsz float %504, %444
  %506 = fadd reassoc ninf nsz float %479, %475
  %507 = fmul reassoc ninf nsz float %484, %506
  %508 = fadd reassoc ninf nsz float %507, %447
  br i1 %40, label %after_if21, label %after_if30

after_if21:                                       ; preds = %after_if18
  %509 = add i32 %88, -8
  %510 = tail call i32 @llvm.smin.i32(i32 %509, i32 %92)
  %511 = tail call i32 @llvm.smax.i32(i32 %510, i32 0)
  %512 = add i32 %88, 8
  %513 = tail call i32 @llvm.smin.i32(i32 %512, i32 %92)
  %514 = tail call i32 @llvm.smax.i32(i32 %513, i32 0)
  %515 = add i32 %511, %66
  %516 = mul i32 %515, %65
  %517 = sext i32 %516 to i64
  %518 = getelementptr float, ptr %63, i64 %517
  %519 = load float, ptr %518, align 4
  %520 = add i32 %514, %66
  %521 = mul i32 %520, %65
  %522 = sext i32 %521 to i64
  %523 = getelementptr float, ptr %63, i64 %522
  %524 = load float, ptr %523, align 4
  %525 = add i32 %516, 1
  %526 = sext i32 %525 to i64
  %527 = getelementptr float, ptr %63, i64 %526
  %528 = load float, ptr %527, align 4
  %529 = add i32 %521, 1
  %530 = sext i32 %529 to i64
  %531 = getelementptr float, ptr %63, i64 %530
  %532 = load float, ptr %531, align 4
  %533 = add i32 %516, 2
  %534 = sext i32 %533 to i64
  %535 = getelementptr float, ptr %63, i64 %534
  %536 = load float, ptr %535, align 4
  %537 = add i32 %521, 2
  %538 = sext i32 %537 to i64
  %539 = getelementptr float, ptr %63, i64 %538
  %540 = load float, ptr %539, align 4
  %541 = fadd reassoc ninf nsz float %524, %519
  %542 = shl i32 %126, 3
  %543 = sext i32 %542 to i64
  %544 = getelementptr float, ptr %125, i64 %543
  %545 = load float, ptr %544, align 4
  %546 = fmul reassoc ninf nsz float %545, %541
  %547 = fadd reassoc ninf nsz float %546, %486
  %548 = getelementptr i8, ptr %544, i64 8
  %549 = load float, ptr %548, align 4
  %550 = fmul reassoc ninf nsz float %549, %541
  %551 = fadd reassoc ninf nsz float %550, %492
  %552 = fsub reassoc ninf nsz float %524, %519
  %553 = getelementptr i8, ptr %544, i64 4
  %554 = load float, ptr %553, align 4
  %555 = fmul reassoc ninf nsz float %554, %552
  %556 = fadd reassoc ninf nsz float %555, %499
  %557 = fadd reassoc ninf nsz float %532, %528
  %558 = fmul reassoc ninf nsz float %545, %557
  %559 = fadd reassoc ninf nsz float %558, %502
  %560 = fsub reassoc ninf nsz float %532, %528
  %561 = fmul reassoc ninf nsz float %554, %560
  %562 = fadd reassoc ninf nsz float %561, %505
  %563 = fadd reassoc ninf nsz float %540, %536
  %564 = fmul reassoc ninf nsz float %545, %563
  %565 = fadd reassoc ninf nsz float %564, %508
  br i1 %41, label %after_if24, label %after_if30

after_if24:                                       ; preds = %after_if21
  %566 = add i32 %88, -9
  %567 = tail call i32 @llvm.smin.i32(i32 %566, i32 %92)
  %568 = tail call i32 @llvm.smax.i32(i32 %567, i32 0)
  %569 = add i32 %88, 9
  %570 = tail call i32 @llvm.smin.i32(i32 %569, i32 %92)
  %571 = tail call i32 @llvm.smax.i32(i32 %570, i32 0)
  %572 = add i32 %568, %66
  %573 = mul i32 %572, %65
  %574 = sext i32 %573 to i64
  %575 = getelementptr float, ptr %63, i64 %574
  %576 = load float, ptr %575, align 4
  %577 = add i32 %571, %66
  %578 = mul i32 %577, %65
  %579 = sext i32 %578 to i64
  %580 = getelementptr float, ptr %63, i64 %579
  %581 = load float, ptr %580, align 4
  %582 = add i32 %573, 1
  %583 = sext i32 %582 to i64
  %584 = getelementptr float, ptr %63, i64 %583
  %585 = load float, ptr %584, align 4
  %586 = add i32 %578, 1
  %587 = sext i32 %586 to i64
  %588 = getelementptr float, ptr %63, i64 %587
  %589 = load float, ptr %588, align 4
  %590 = add i32 %573, 2
  %591 = sext i32 %590 to i64
  %592 = getelementptr float, ptr %63, i64 %591
  %593 = load float, ptr %592, align 4
  %594 = add i32 %578, 2
  %595 = sext i32 %594 to i64
  %596 = getelementptr float, ptr %63, i64 %595
  %597 = load float, ptr %596, align 4
  %598 = fadd reassoc ninf nsz float %581, %576
  %599 = mul i32 %126, 9
  %600 = sext i32 %599 to i64
  %601 = getelementptr float, ptr %125, i64 %600
  %602 = load float, ptr %601, align 4
  %603 = fmul reassoc ninf nsz float %602, %598
  %604 = fadd reassoc ninf nsz float %603, %547
  %605 = add i32 %599, 2
  %606 = sext i32 %605 to i64
  %607 = getelementptr float, ptr %125, i64 %606
  %608 = load float, ptr %607, align 4
  %609 = fmul reassoc ninf nsz float %608, %598
  %610 = fadd reassoc ninf nsz float %609, %551
  %611 = fsub reassoc ninf nsz float %581, %576
  %612 = add i32 %599, 1
  %613 = sext i32 %612 to i64
  %614 = getelementptr float, ptr %125, i64 %613
  %615 = load float, ptr %614, align 4
  %616 = fmul reassoc ninf nsz float %615, %611
  %617 = fadd reassoc ninf nsz float %616, %556
  %618 = fadd reassoc ninf nsz float %589, %585
  %619 = fmul reassoc ninf nsz float %602, %618
  %620 = fadd reassoc ninf nsz float %619, %559
  %621 = fsub reassoc ninf nsz float %589, %585
  %622 = fmul reassoc ninf nsz float %615, %621
  %623 = fadd reassoc ninf nsz float %622, %562
  %624 = fadd reassoc ninf nsz float %597, %593
  %625 = fmul reassoc ninf nsz float %602, %624
  %626 = fadd reassoc ninf nsz float %625, %565
  br i1 %42, label %after_if27, label %after_if30

after_if27:                                       ; preds = %after_if24
  %627 = add i32 %88, -10
  %628 = tail call i32 @llvm.smin.i32(i32 %627, i32 %92)
  %629 = tail call i32 @llvm.smax.i32(i32 %628, i32 0)
  %630 = add i32 %88, 10
  %631 = tail call i32 @llvm.smin.i32(i32 %630, i32 %92)
  %632 = tail call i32 @llvm.smax.i32(i32 %631, i32 0)
  %633 = add i32 %629, %66
  %634 = mul i32 %633, %65
  %635 = sext i32 %634 to i64
  %636 = getelementptr float, ptr %63, i64 %635
  %637 = load float, ptr %636, align 4
  %638 = add i32 %632, %66
  %639 = mul i32 %638, %65
  %640 = sext i32 %639 to i64
  %641 = getelementptr float, ptr %63, i64 %640
  %642 = load float, ptr %641, align 4
  %643 = add i32 %634, 1
  %644 = sext i32 %643 to i64
  %645 = getelementptr float, ptr %63, i64 %644
  %646 = load float, ptr %645, align 4
  %647 = add i32 %639, 1
  %648 = sext i32 %647 to i64
  %649 = getelementptr float, ptr %63, i64 %648
  %650 = load float, ptr %649, align 4
  %651 = add i32 %634, 2
  %652 = sext i32 %651 to i64
  %653 = getelementptr float, ptr %63, i64 %652
  %654 = load float, ptr %653, align 4
  %655 = add i32 %639, 2
  %656 = sext i32 %655 to i64
  %657 = getelementptr float, ptr %63, i64 %656
  %658 = load float, ptr %657, align 4
  %659 = fadd reassoc ninf nsz float %642, %637
  %660 = mul i32 %126, 10
  %661 = sext i32 %660 to i64
  %662 = getelementptr float, ptr %125, i64 %661
  %663 = load float, ptr %662, align 4
  %664 = fmul reassoc ninf nsz float %663, %659
  %665 = fadd reassoc ninf nsz float %664, %604
  %666 = add i32 %660, 2
  %667 = sext i32 %666 to i64
  %668 = getelementptr float, ptr %125, i64 %667
  %669 = load float, ptr %668, align 4
  %670 = fmul reassoc ninf nsz float %669, %659
  %671 = fadd reassoc ninf nsz float %670, %610
  %672 = fsub reassoc ninf nsz float %642, %637
  %673 = getelementptr i8, ptr %662, i64 4
  %674 = load float, ptr %673, align 4
  %675 = fmul reassoc ninf nsz float %674, %672
  %676 = fadd reassoc ninf nsz float %675, %617
  %677 = fadd reassoc ninf nsz float %650, %646
  %678 = fmul reassoc ninf nsz float %663, %677
  %679 = fadd reassoc ninf nsz float %678, %620
  %680 = fsub reassoc ninf nsz float %650, %646
  %681 = fmul reassoc ninf nsz float %674, %680
  %682 = fadd reassoc ninf nsz float %681, %623
  %683 = fadd reassoc ninf nsz float %658, %654
  %684 = fmul reassoc ninf nsz float %663, %683
  %685 = fadd reassoc ninf nsz float %684, %626
  br i1 %43, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %686 = add i32 %88, -11
  %687 = tail call i32 @llvm.smin.i32(i32 %686, i32 %92)
  %688 = tail call i32 @llvm.smax.i32(i32 %687, i32 0)
  %689 = add i32 %88, 11
  %690 = tail call i32 @llvm.smin.i32(i32 %689, i32 %92)
  %691 = tail call i32 @llvm.smax.i32(i32 %690, i32 0)
  %692 = add i32 %688, %66
  %693 = mul i32 %692, %65
  %694 = sext i32 %693 to i64
  %695 = getelementptr float, ptr %63, i64 %694
  %696 = load float, ptr %695, align 4
  %697 = add i32 %691, %66
  %698 = mul i32 %697, %65
  %699 = sext i32 %698 to i64
  %700 = getelementptr float, ptr %63, i64 %699
  %701 = load float, ptr %700, align 4
  %702 = add i32 %693, 1
  %703 = sext i32 %702 to i64
  %704 = getelementptr float, ptr %63, i64 %703
  %705 = load float, ptr %704, align 4
  %706 = add i32 %698, 1
  %707 = sext i32 %706 to i64
  %708 = getelementptr float, ptr %63, i64 %707
  %709 = load float, ptr %708, align 4
  %710 = add i32 %693, 2
  %711 = sext i32 %710 to i64
  %712 = getelementptr float, ptr %63, i64 %711
  %713 = load float, ptr %712, align 4
  %714 = add i32 %698, 2
  %715 = sext i32 %714 to i64
  %716 = getelementptr float, ptr %63, i64 %715
  %717 = load float, ptr %716, align 4
  %718 = fadd reassoc ninf nsz float %701, %696
  %719 = mul i32 %126, 11
  %720 = sext i32 %719 to i64
  %721 = getelementptr float, ptr %125, i64 %720
  %722 = load float, ptr %721, align 4
  %723 = fmul reassoc ninf nsz float %722, %718
  %724 = fadd reassoc ninf nsz float %723, %665
  %725 = add i32 %719, 2
  %726 = sext i32 %725 to i64
  %727 = getelementptr float, ptr %125, i64 %726
  %728 = load float, ptr %727, align 4
  %729 = fmul reassoc ninf nsz float %728, %718
  %730 = fadd reassoc ninf nsz float %729, %671
  %731 = fsub reassoc ninf nsz float %701, %696
  %732 = add i32 %719, 1
  %733 = sext i32 %732 to i64
  %734 = getelementptr float, ptr %125, i64 %733
  %735 = load float, ptr %734, align 4
  %736 = fmul reassoc ninf nsz float %735, %731
  %737 = fadd reassoc ninf nsz float %736, %676
  %738 = fadd reassoc ninf nsz float %709, %705
  %739 = fmul reassoc ninf nsz float %722, %738
  %740 = fadd reassoc ninf nsz float %739, %679
  %741 = fsub reassoc ninf nsz float %709, %705
  %742 = fmul reassoc ninf nsz float %735, %741
  %743 = fadd reassoc ninf nsz float %742, %682
  %744 = fadd reassoc ninf nsz float %717, %713
  %745 = fmul reassoc ninf nsz float %722, %744
  %746 = fadd reassoc ninf nsz float %745, %685
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.10123 = phi float [ %724, %true_block28 ], [ %665, %after_if27 ], [ %604, %after_if24 ], [ %547, %after_if21 ], [ %486, %after_if18 ], [ %427, %after_if15 ], [ %366, %after_if12 ], [ %309, %after_if9 ], [ %248, %after_if6 ], [ %189, %after_if3 ], [ %131, %after_if ], [ %75, %for_loop_body ]
  %.10112 = phi float [ %737, %true_block28 ], [ %676, %after_if27 ], [ %617, %after_if24 ], [ %556, %after_if21 ], [ %499, %after_if18 ], [ %438, %after_if15 ], [ %379, %after_if12 ], [ %318, %after_if9 ], [ %261, %after_if6 ], [ %200, %after_if3 ], [ %142, %after_if ], [ 0.000000e+00, %for_loop_body ]
  %.10101 = phi float [ %740, %true_block28 ], [ %679, %after_if27 ], [ %620, %after_if24 ], [ %559, %after_if21 ], [ %502, %after_if18 ], [ %441, %after_if15 ], [ %382, %after_if12 ], [ %321, %after_if9 ], [ %264, %after_if6 ], [ %203, %after_if3 ], [ %145, %after_if ], [ %80, %for_loop_body ]
  %.1090 = phi float [ %730, %true_block28 ], [ %671, %after_if27 ], [ %610, %after_if24 ], [ %551, %after_if21 ], [ %492, %after_if18 ], [ %433, %after_if15 ], [ %372, %after_if12 ], [ %313, %after_if9 ], [ %254, %after_if6 ], [ %195, %after_if3 ], [ %136, %after_if ], [ 0.000000e+00, %for_loop_body ]
  %.1079 = phi float [ %746, %true_block28 ], [ %685, %after_if27 ], [ %626, %after_if24 ], [ %565, %after_if21 ], [ %508, %after_if18 ], [ %447, %after_if15 ], [ %388, %after_if12 ], [ %327, %after_if9 ], [ %270, %after_if6 ], [ %209, %after_if3 ], [ %150, %after_if ], [ %85, %for_loop_body ]
  %.10 = phi float [ %743, %true_block28 ], [ %682, %after_if27 ], [ %623, %after_if24 ], [ %562, %after_if21 ], [ %505, %after_if18 ], [ %444, %after_if15 ], [ %385, %after_if12 ], [ %324, %after_if9 ], [ %267, %after_if6 ], [ %206, %after_if3 ], [ %147, %after_if ], [ 0.000000e+00, %for_loop_body ]
  %747 = fmul reassoc ninf nsz float %.10101, %23
  %748 = load ptr, ptr %48, align 8
  %749 = load i32, ptr %49, align 4
  %750 = load i32, ptr %50, align 4
  %751 = sub i32 %749, %55
  %752 = mul i32 %751, %62
  %753 = add i32 %.0124186, %752
  %754 = mul i32 %753, %750
  %755 = sext i32 %754 to i64
  %756 = getelementptr float, ptr %748, i64 %755
  store float %747, ptr %756, align 4
  %757 = fmul reassoc ninf nsz float %.10112, %23
  %758 = load ptr, ptr %48, align 8
  %759 = load i32, ptr %49, align 4
  %760 = load i32, ptr %50, align 4
  %761 = sub i32 %759, %55
  %762 = mul i32 %761, %62
  %763 = add i32 %.0124186, %762
  %764 = mul i32 %763, %760
  %765 = add i32 %764, 1
  %766 = sext i32 %765 to i64
  %767 = getelementptr float, ptr %758, i64 %766
  store float %757, ptr %767, align 4
  %768 = fmul reassoc ninf nsz float %.10123, %25
  %769 = fmul reassoc ninf nsz float %.1079, %27
  %770 = fadd reassoc ninf nsz float %769, %768
  %771 = load ptr, ptr %48, align 8
  %772 = load i32, ptr %49, align 4
  %773 = load i32, ptr %50, align 4
  %774 = sub i32 %772, %55
  %775 = mul i32 %774, %62
  %776 = add i32 %.0124186, %775
  %777 = mul i32 %776, %773
  %778 = add i32 %777, 2
  %779 = sext i32 %778 to i64
  %780 = getelementptr float, ptr %771, i64 %779
  store float %770, ptr %780, align 4
  %781 = fmul reassoc ninf nsz float %.1090, %27
  %782 = fadd reassoc ninf nsz float %781, %768
  %783 = load ptr, ptr %48, align 8
  %784 = load i32, ptr %49, align 4
  %785 = load i32, ptr %50, align 4
  %786 = sub i32 %784, %55
  %787 = mul i32 %786, %62
  %788 = add i32 %.0124186, %787
  %789 = mul i32 %788, %785
  %790 = add i32 %789, 3
  %791 = sext i32 %790 to i64
  %792 = getelementptr float, ptr %783, i64 %791
  store float %782, ptr %792, align 4
  %793 = fmul reassoc ninf nsz float %.10, %29
  %794 = load ptr, ptr %48, align 8
  %795 = load i32, ptr %49, align 4
  %796 = load i32, ptr %50, align 4
  %797 = sub i32 %795, %55
  %798 = mul i32 %797, %62
  %799 = add i32 %.0124186, %798
  %800 = mul i32 %799, %796
  %801 = add i32 %800, 4
  %802 = sext i32 %801 to i64
  %803 = getelementptr float, ptr %794, i64 %802
  store float %793, ptr %803, align 4
  %804 = add nsw i32 %.0124186, 1
  %exitcond.not = icmp eq i32 %18, %804
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

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
attributes #2 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
