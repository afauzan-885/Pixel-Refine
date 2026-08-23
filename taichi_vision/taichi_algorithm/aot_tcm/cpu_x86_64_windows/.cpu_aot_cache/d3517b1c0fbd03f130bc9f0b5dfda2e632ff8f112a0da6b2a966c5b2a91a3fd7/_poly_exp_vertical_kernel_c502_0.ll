; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_poly_exp_vertical_kernel_c502_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 40
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 44
  %11 = load i32, ptr %10, align 4
  %12 = tail call i32 @llvm.smax.i32(i32 %11, i32 0)
  %13 = load ptr, ptr %3, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 4
  store i32 %12, ptr %16, align 4
  %17 = mul i32 %12, %8
  %18 = load ptr, ptr %3, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  store i32 %17, ptr %20, align 4
  ret void
}

define void @_poly_exp_vertical_kernel_c502_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 64
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 56
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr i8, ptr %19, i64 52
  %25 = getelementptr i8, ptr %23, i64 8
  %26 = icmp sgt i32 %21, 0
  %27 = icmp sgt i32 %21, 1
  %28 = icmp sgt i32 %21, 2
  %29 = icmp sgt i32 %21, 3
  %30 = icmp sgt i32 %21, 4
  %31 = icmp sgt i32 %21, 5
  %32 = icmp sgt i32 %21, 6
  %33 = icmp sgt i32 %21, 7
  %34 = icmp sgt i32 %21, 8
  %35 = icmp sgt i32 %21, 9
  %36 = icmp sgt i32 %21, 10
  %37 = icmp slt i32 %16, %18
  br i1 %37, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %38 = getelementptr i8, ptr %19, i64 8
  %39 = getelementptr i8, ptr %19, i64 4
  %40 = getelementptr i8, ptr %19, i64 32
  %41 = getelementptr i8, ptr %19, i64 20
  %42 = getelementptr i8, ptr %19, i64 24
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if30, %for_loop_body.lr.ph
  %.05890 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %504, %after_if30 ]
  %43 = load ptr, ptr %3, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 4
  %47 = load i32, ptr %46, align 4
  %48 = sdiv i32 %.05890, %47
  %49 = mul i32 %48, %47
  %50 = xor i32 %47, %.05890
  %51 = icmp slt i32 %50, 0
  %52 = icmp ne i32 %.05890, %49
  %53 = and i1 %51, %52
  %.neg59 = sext i1 %53 to i32
  %54 = add i32 %48, %.neg59
  %55 = mul i32 %54, %47
  %56 = load ptr, ptr %38, align 8
  %57 = load i32, ptr %39, align 4
  %58 = sub i32 %57, %47
  %59 = mul i32 %58, %54
  %60 = add i32 %.05890, %59
  %61 = sext i32 %60 to i64
  %62 = getelementptr float, ptr %56, i64 %61
  %63 = load float, ptr %62, align 4
  %64 = load float, ptr %23, align 4
  %65 = fmul reassoc ninf nsz float %64, %63
  %66 = load float, ptr %25, align 4
  %67 = fmul reassoc ninf nsz float %66, %63
  br i1 %26, label %after_if, label %after_if30

after_for.loopexit:                               ; preds = %after_if30
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %68 = add i32 %54, -1
  %69 = getelementptr inbounds nuw i8, ptr %45, i64 8
  %70 = load i32, ptr %69, align 4
  %71 = add i32 %70, -1
  %72 = tail call i32 @llvm.smin.i32(i32 %68, i32 %71)
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = add i32 %54, 1
  %75 = tail call i32 @llvm.smin.i32(i32 %74, i32 %71)
  %76 = tail call i32 @llvm.smax.i32(i32 %75, i32 0)
  %77 = mul i32 %73, %57
  %78 = sub i32 %77, %55
  %79 = add i32 %.05890, %78
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, ptr %56, i64 %80
  %82 = load float, ptr %81, align 4
  %83 = mul i32 %76, %57
  %84 = sub i32 %83, %55
  %85 = add i32 %.05890, %84
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %56, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = load ptr, ptr %22, align 8
  %90 = load i32, ptr %24, align 4
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %89, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = fadd reassoc ninf nsz float %88, %82
  %95 = fmul reassoc ninf nsz float %93, %94
  %96 = fadd reassoc ninf nsz float %95, %65
  %97 = add i32 %90, 1
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %89, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = fsub reassoc ninf nsz float %88, %82
  %102 = fmul reassoc ninf nsz float %100, %101
  %103 = add i32 %90, 2
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %89, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = fmul reassoc ninf nsz float %106, %94
  %108 = fadd reassoc ninf nsz float %107, %67
  br i1 %27, label %after_if3, label %after_if30

after_if3:                                        ; preds = %after_if
  %109 = add i32 %54, -2
  %110 = tail call i32 @llvm.smin.i32(i32 %109, i32 %71)
  %111 = tail call i32 @llvm.smax.i32(i32 %110, i32 0)
  %112 = add i32 %54, 2
  %113 = tail call i32 @llvm.smin.i32(i32 %112, i32 %71)
  %114 = tail call i32 @llvm.smax.i32(i32 %113, i32 0)
  %115 = mul i32 %111, %57
  %116 = sub i32 %115, %55
  %117 = add i32 %.05890, %116
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, ptr %56, i64 %118
  %120 = load float, ptr %119, align 4
  %121 = mul i32 %114, %57
  %122 = sub i32 %121, %55
  %123 = add i32 %.05890, %122
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %56, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = shl i32 %90, 1
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %89, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = fadd reassoc ninf nsz float %126, %120
  %132 = fmul reassoc ninf nsz float %130, %131
  %133 = fadd reassoc ninf nsz float %132, %96
  %134 = getelementptr i8, ptr %129, i64 4
  %135 = load float, ptr %134, align 4
  %136 = fsub reassoc ninf nsz float %126, %120
  %137 = fmul reassoc ninf nsz float %135, %136
  %138 = fadd reassoc ninf nsz float %137, %102
  %139 = add i32 %127, 2
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %89, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = fmul reassoc ninf nsz float %142, %131
  %144 = fadd reassoc ninf nsz float %143, %108
  br i1 %28, label %after_if6, label %after_if30

after_if6:                                        ; preds = %after_if3
  %145 = add i32 %54, -3
  %146 = tail call i32 @llvm.smin.i32(i32 %145, i32 %71)
  %147 = tail call i32 @llvm.smax.i32(i32 %146, i32 0)
  %148 = add i32 %54, 3
  %149 = tail call i32 @llvm.smin.i32(i32 %148, i32 %71)
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = mul i32 %147, %57
  %152 = sub i32 %151, %55
  %153 = add i32 %.05890, %152
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %56, i64 %154
  %156 = load float, ptr %155, align 4
  %157 = mul i32 %150, %57
  %158 = sub i32 %157, %55
  %159 = add i32 %.05890, %158
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %56, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = mul i32 %90, 3
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %89, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = fadd reassoc ninf nsz float %162, %156
  %168 = fmul reassoc ninf nsz float %166, %167
  %169 = fadd reassoc ninf nsz float %168, %133
  %170 = add i32 %163, 1
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %89, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = fsub reassoc ninf nsz float %162, %156
  %175 = fmul reassoc ninf nsz float %173, %174
  %176 = fadd reassoc ninf nsz float %175, %138
  %177 = add i32 %163, 2
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, ptr %89, i64 %178
  %180 = load float, ptr %179, align 4
  %181 = fmul reassoc ninf nsz float %180, %167
  %182 = fadd reassoc ninf nsz float %181, %144
  br i1 %29, label %after_if9, label %after_if30

after_if9:                                        ; preds = %after_if6
  %183 = add i32 %54, -4
  %184 = tail call i32 @llvm.smin.i32(i32 %183, i32 %71)
  %185 = tail call i32 @llvm.smax.i32(i32 %184, i32 0)
  %186 = add i32 %54, 4
  %187 = tail call i32 @llvm.smin.i32(i32 %186, i32 %71)
  %188 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %189 = mul i32 %185, %57
  %190 = sub i32 %189, %55
  %191 = add i32 %.05890, %190
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, ptr %56, i64 %192
  %194 = load float, ptr %193, align 4
  %195 = mul i32 %188, %57
  %196 = sub i32 %195, %55
  %197 = add i32 %.05890, %196
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %56, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = shl i32 %90, 2
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %89, i64 %202
  %204 = load float, ptr %203, align 4
  %205 = fadd reassoc ninf nsz float %200, %194
  %206 = fmul reassoc ninf nsz float %204, %205
  %207 = fadd reassoc ninf nsz float %206, %169
  %208 = getelementptr i8, ptr %203, i64 4
  %209 = load float, ptr %208, align 4
  %210 = fsub reassoc ninf nsz float %200, %194
  %211 = fmul reassoc ninf nsz float %209, %210
  %212 = fadd reassoc ninf nsz float %211, %176
  %213 = getelementptr i8, ptr %203, i64 8
  %214 = load float, ptr %213, align 4
  %215 = fmul reassoc ninf nsz float %214, %205
  %216 = fadd reassoc ninf nsz float %215, %182
  br i1 %30, label %after_if12, label %after_if30

after_if12:                                       ; preds = %after_if9
  %217 = add i32 %54, -5
  %218 = tail call i32 @llvm.smin.i32(i32 %217, i32 %71)
  %219 = tail call i32 @llvm.smax.i32(i32 %218, i32 0)
  %220 = add i32 %54, 5
  %221 = tail call i32 @llvm.smin.i32(i32 %220, i32 %71)
  %222 = tail call i32 @llvm.smax.i32(i32 %221, i32 0)
  %223 = mul i32 %219, %57
  %224 = sub i32 %223, %55
  %225 = add i32 %.05890, %224
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %56, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = mul i32 %222, %57
  %230 = sub i32 %229, %55
  %231 = add i32 %.05890, %230
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, ptr %56, i64 %232
  %234 = load float, ptr %233, align 4
  %235 = mul i32 %90, 5
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, ptr %89, i64 %236
  %238 = load float, ptr %237, align 4
  %239 = fadd reassoc ninf nsz float %234, %228
  %240 = fmul reassoc ninf nsz float %238, %239
  %241 = fadd reassoc ninf nsz float %240, %207
  %242 = add i32 %235, 1
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, ptr %89, i64 %243
  %245 = load float, ptr %244, align 4
  %246 = fsub reassoc ninf nsz float %234, %228
  %247 = fmul reassoc ninf nsz float %245, %246
  %248 = fadd reassoc ninf nsz float %247, %212
  %249 = add i32 %235, 2
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, ptr %89, i64 %250
  %252 = load float, ptr %251, align 4
  %253 = fmul reassoc ninf nsz float %252, %239
  %254 = fadd reassoc ninf nsz float %253, %216
  br i1 %31, label %after_if15, label %after_if30

after_if15:                                       ; preds = %after_if12
  %255 = add i32 %54, -6
  %256 = tail call i32 @llvm.smin.i32(i32 %255, i32 %71)
  %257 = tail call i32 @llvm.smax.i32(i32 %256, i32 0)
  %258 = add i32 %54, 6
  %259 = tail call i32 @llvm.smin.i32(i32 %258, i32 %71)
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = mul i32 %257, %57
  %262 = sub i32 %261, %55
  %263 = add i32 %.05890, %262
  %264 = sext i32 %263 to i64
  %265 = getelementptr float, ptr %56, i64 %264
  %266 = load float, ptr %265, align 4
  %267 = mul i32 %260, %57
  %268 = sub i32 %267, %55
  %269 = add i32 %.05890, %268
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, ptr %56, i64 %270
  %272 = load float, ptr %271, align 4
  %273 = mul i32 %90, 6
  %274 = sext i32 %273 to i64
  %275 = getelementptr float, ptr %89, i64 %274
  %276 = load float, ptr %275, align 4
  %277 = fadd reassoc ninf nsz float %272, %266
  %278 = fmul reassoc ninf nsz float %276, %277
  %279 = fadd reassoc ninf nsz float %278, %241
  %280 = getelementptr i8, ptr %275, i64 4
  %281 = load float, ptr %280, align 4
  %282 = fsub reassoc ninf nsz float %272, %266
  %283 = fmul reassoc ninf nsz float %281, %282
  %284 = fadd reassoc ninf nsz float %283, %248
  %285 = add i32 %273, 2
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, ptr %89, i64 %286
  %288 = load float, ptr %287, align 4
  %289 = fmul reassoc ninf nsz float %288, %277
  %290 = fadd reassoc ninf nsz float %289, %254
  br i1 %32, label %after_if18, label %after_if30

after_if18:                                       ; preds = %after_if15
  %291 = add i32 %54, -7
  %292 = tail call i32 @llvm.smin.i32(i32 %291, i32 %71)
  %293 = tail call i32 @llvm.smax.i32(i32 %292, i32 0)
  %294 = add i32 %54, 7
  %295 = tail call i32 @llvm.smin.i32(i32 %294, i32 %71)
  %296 = tail call i32 @llvm.smax.i32(i32 %295, i32 0)
  %297 = mul i32 %293, %57
  %298 = sub i32 %297, %55
  %299 = add i32 %.05890, %298
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, ptr %56, i64 %300
  %302 = load float, ptr %301, align 4
  %303 = mul i32 %296, %57
  %304 = sub i32 %303, %55
  %305 = add i32 %.05890, %304
  %306 = sext i32 %305 to i64
  %307 = getelementptr float, ptr %56, i64 %306
  %308 = load float, ptr %307, align 4
  %309 = mul i32 %90, 7
  %310 = sext i32 %309 to i64
  %311 = getelementptr float, ptr %89, i64 %310
  %312 = load float, ptr %311, align 4
  %313 = fadd reassoc ninf nsz float %308, %302
  %314 = fmul reassoc ninf nsz float %312, %313
  %315 = fadd reassoc ninf nsz float %314, %279
  %316 = add i32 %309, 1
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, ptr %89, i64 %317
  %319 = load float, ptr %318, align 4
  %320 = fsub reassoc ninf nsz float %308, %302
  %321 = fmul reassoc ninf nsz float %319, %320
  %322 = fadd reassoc ninf nsz float %321, %284
  %323 = add i32 %309, 2
  %324 = sext i32 %323 to i64
  %325 = getelementptr float, ptr %89, i64 %324
  %326 = load float, ptr %325, align 4
  %327 = fmul reassoc ninf nsz float %326, %313
  %328 = fadd reassoc ninf nsz float %327, %290
  br i1 %33, label %after_if21, label %after_if30

after_if21:                                       ; preds = %after_if18
  %329 = add i32 %54, -8
  %330 = tail call i32 @llvm.smin.i32(i32 %329, i32 %71)
  %331 = tail call i32 @llvm.smax.i32(i32 %330, i32 0)
  %332 = add i32 %54, 8
  %333 = tail call i32 @llvm.smin.i32(i32 %332, i32 %71)
  %334 = tail call i32 @llvm.smax.i32(i32 %333, i32 0)
  %335 = mul i32 %331, %57
  %336 = sub i32 %335, %55
  %337 = add i32 %.05890, %336
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, ptr %56, i64 %338
  %340 = load float, ptr %339, align 4
  %341 = mul i32 %334, %57
  %342 = sub i32 %341, %55
  %343 = add i32 %.05890, %342
  %344 = sext i32 %343 to i64
  %345 = getelementptr float, ptr %56, i64 %344
  %346 = load float, ptr %345, align 4
  %347 = shl i32 %90, 3
  %348 = sext i32 %347 to i64
  %349 = getelementptr float, ptr %89, i64 %348
  %350 = load float, ptr %349, align 4
  %351 = fadd reassoc ninf nsz float %346, %340
  %352 = fmul reassoc ninf nsz float %350, %351
  %353 = fadd reassoc ninf nsz float %352, %315
  %354 = getelementptr i8, ptr %349, i64 4
  %355 = load float, ptr %354, align 4
  %356 = fsub reassoc ninf nsz float %346, %340
  %357 = fmul reassoc ninf nsz float %355, %356
  %358 = fadd reassoc ninf nsz float %357, %322
  %359 = getelementptr i8, ptr %349, i64 8
  %360 = load float, ptr %359, align 4
  %361 = fmul reassoc ninf nsz float %360, %351
  %362 = fadd reassoc ninf nsz float %361, %328
  br i1 %34, label %after_if24, label %after_if30

after_if24:                                       ; preds = %after_if21
  %363 = add i32 %54, -9
  %364 = tail call i32 @llvm.smin.i32(i32 %363, i32 %71)
  %365 = tail call i32 @llvm.smax.i32(i32 %364, i32 0)
  %366 = add i32 %54, 9
  %367 = tail call i32 @llvm.smin.i32(i32 %366, i32 %71)
  %368 = tail call i32 @llvm.smax.i32(i32 %367, i32 0)
  %369 = mul i32 %365, %57
  %370 = sub i32 %369, %55
  %371 = add i32 %.05890, %370
  %372 = sext i32 %371 to i64
  %373 = getelementptr float, ptr %56, i64 %372
  %374 = load float, ptr %373, align 4
  %375 = mul i32 %368, %57
  %376 = sub i32 %375, %55
  %377 = add i32 %.05890, %376
  %378 = sext i32 %377 to i64
  %379 = getelementptr float, ptr %56, i64 %378
  %380 = load float, ptr %379, align 4
  %381 = mul i32 %90, 9
  %382 = sext i32 %381 to i64
  %383 = getelementptr float, ptr %89, i64 %382
  %384 = load float, ptr %383, align 4
  %385 = fadd reassoc ninf nsz float %380, %374
  %386 = fmul reassoc ninf nsz float %384, %385
  %387 = fadd reassoc ninf nsz float %386, %353
  %388 = add i32 %381, 1
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, ptr %89, i64 %389
  %391 = load float, ptr %390, align 4
  %392 = fsub reassoc ninf nsz float %380, %374
  %393 = fmul reassoc ninf nsz float %391, %392
  %394 = fadd reassoc ninf nsz float %393, %358
  %395 = add i32 %381, 2
  %396 = sext i32 %395 to i64
  %397 = getelementptr float, ptr %89, i64 %396
  %398 = load float, ptr %397, align 4
  %399 = fmul reassoc ninf nsz float %398, %385
  %400 = fadd reassoc ninf nsz float %399, %362
  br i1 %35, label %after_if27, label %after_if30

after_if27:                                       ; preds = %after_if24
  %401 = add i32 %54, -10
  %402 = tail call i32 @llvm.smin.i32(i32 %401, i32 %71)
  %403 = tail call i32 @llvm.smax.i32(i32 %402, i32 0)
  %404 = add i32 %54, 10
  %405 = tail call i32 @llvm.smin.i32(i32 %404, i32 %71)
  %406 = tail call i32 @llvm.smax.i32(i32 %405, i32 0)
  %407 = mul i32 %403, %57
  %408 = sub i32 %407, %55
  %409 = add i32 %.05890, %408
  %410 = sext i32 %409 to i64
  %411 = getelementptr float, ptr %56, i64 %410
  %412 = load float, ptr %411, align 4
  %413 = mul i32 %406, %57
  %414 = sub i32 %413, %55
  %415 = add i32 %.05890, %414
  %416 = sext i32 %415 to i64
  %417 = getelementptr float, ptr %56, i64 %416
  %418 = load float, ptr %417, align 4
  %419 = mul i32 %90, 10
  %420 = sext i32 %419 to i64
  %421 = getelementptr float, ptr %89, i64 %420
  %422 = load float, ptr %421, align 4
  %423 = fadd reassoc ninf nsz float %418, %412
  %424 = fmul reassoc ninf nsz float %422, %423
  %425 = fadd reassoc ninf nsz float %424, %387
  %426 = getelementptr i8, ptr %421, i64 4
  %427 = load float, ptr %426, align 4
  %428 = fsub reassoc ninf nsz float %418, %412
  %429 = fmul reassoc ninf nsz float %427, %428
  %430 = fadd reassoc ninf nsz float %429, %394
  %431 = add i32 %419, 2
  %432 = sext i32 %431 to i64
  %433 = getelementptr float, ptr %89, i64 %432
  %434 = load float, ptr %433, align 4
  %435 = fmul reassoc ninf nsz float %434, %423
  %436 = fadd reassoc ninf nsz float %435, %400
  br i1 %36, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %437 = add i32 %54, -11
  %438 = tail call i32 @llvm.smin.i32(i32 %437, i32 %71)
  %439 = tail call i32 @llvm.smax.i32(i32 %438, i32 0)
  %440 = add i32 %54, 11
  %441 = tail call i32 @llvm.smin.i32(i32 %440, i32 %71)
  %442 = tail call i32 @llvm.smax.i32(i32 %441, i32 0)
  %443 = mul i32 %439, %57
  %444 = sub i32 %443, %55
  %445 = add i32 %.05890, %444
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, ptr %56, i64 %446
  %448 = load float, ptr %447, align 4
  %449 = mul i32 %442, %57
  %450 = sub i32 %449, %55
  %451 = add i32 %.05890, %450
  %452 = sext i32 %451 to i64
  %453 = getelementptr float, ptr %56, i64 %452
  %454 = load float, ptr %453, align 4
  %455 = mul i32 %90, 11
  %456 = sext i32 %455 to i64
  %457 = getelementptr float, ptr %89, i64 %456
  %458 = load float, ptr %457, align 4
  %459 = fadd reassoc ninf nsz float %454, %448
  %460 = fmul reassoc ninf nsz float %458, %459
  %461 = fadd reassoc ninf nsz float %460, %425
  %462 = add i32 %455, 1
  %463 = sext i32 %462 to i64
  %464 = getelementptr float, ptr %89, i64 %463
  %465 = load float, ptr %464, align 4
  %466 = fsub reassoc ninf nsz float %454, %448
  %467 = fmul reassoc ninf nsz float %465, %466
  %468 = fadd reassoc ninf nsz float %467, %430
  %469 = add i32 %455, 2
  %470 = sext i32 %469 to i64
  %471 = getelementptr float, ptr %89, i64 %470
  %472 = load float, ptr %471, align 4
  %473 = fmul reassoc ninf nsz float %472, %459
  %474 = fadd reassoc ninf nsz float %473, %436
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.1057 = phi float [ %461, %true_block28 ], [ %425, %after_if27 ], [ %387, %after_if24 ], [ %353, %after_if21 ], [ %315, %after_if18 ], [ %279, %after_if15 ], [ %241, %after_if12 ], [ %207, %after_if9 ], [ %169, %after_if6 ], [ %133, %after_if3 ], [ %96, %after_if ], [ %65, %for_loop_body ]
  %.1046 = phi float [ %468, %true_block28 ], [ %430, %after_if27 ], [ %394, %after_if24 ], [ %358, %after_if21 ], [ %322, %after_if18 ], [ %284, %after_if15 ], [ %248, %after_if12 ], [ %212, %after_if9 ], [ %176, %after_if6 ], [ %138, %after_if3 ], [ %102, %after_if ], [ 0.000000e+00, %for_loop_body ]
  %.10 = phi float [ %474, %true_block28 ], [ %436, %after_if27 ], [ %400, %after_if24 ], [ %362, %after_if21 ], [ %328, %after_if18 ], [ %290, %after_if15 ], [ %254, %after_if12 ], [ %216, %after_if9 ], [ %182, %after_if6 ], [ %144, %after_if3 ], [ %108, %after_if ], [ %67, %for_loop_body ]
  %475 = load ptr, ptr %40, align 8
  %476 = load i32, ptr %41, align 4
  %477 = load i32, ptr %42, align 4
  %478 = sub i32 %476, %47
  %479 = mul i32 %478, %54
  %480 = add i32 %.05890, %479
  %481 = mul i32 %480, %477
  %482 = sext i32 %481 to i64
  %483 = getelementptr float, ptr %475, i64 %482
  store float %.1057, ptr %483, align 4
  %484 = load ptr, ptr %40, align 8
  %485 = load i32, ptr %41, align 4
  %486 = load i32, ptr %42, align 4
  %487 = sub i32 %485, %47
  %488 = mul i32 %487, %54
  %489 = add i32 %.05890, %488
  %490 = mul i32 %489, %486
  %491 = add i32 %490, 1
  %492 = sext i32 %491 to i64
  %493 = getelementptr float, ptr %484, i64 %492
  store float %.1046, ptr %493, align 4
  %494 = load ptr, ptr %40, align 8
  %495 = load i32, ptr %41, align 4
  %496 = load i32, ptr %42, align 4
  %497 = sub i32 %495, %47
  %498 = mul i32 %497, %54
  %499 = add i32 %.05890, %498
  %500 = mul i32 %499, %496
  %501 = add i32 %500, 2
  %502 = sext i32 %501 to i64
  %503 = getelementptr float, ptr %494, i64 %502
  store float %.10, ptr %503, align 4
  %504 = add nsw i32 %.05890, 1
  %exitcond.not = icmp eq i32 %18, %504
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
