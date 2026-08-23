; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.11 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jbf_flow_r1_c710_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_jbf_flow_r1_c710_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %34 = shl i32 %16, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %34, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %337, %for_loop_body ]
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
  %84 = shl i32 %83, 1
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, ptr %80, i64 %85
  %87 = load float, ptr %86, align 4
  %88 = getelementptr i8, ptr %86, i64 4
  %89 = load float, ptr %88, align 4
  %90 = fmul reassoc ninf nsz float %87, %79
  %91 = fmul reassoc ninf nsz float %89, %79
  %92 = fadd reassoc ninf nsz float %79, 0x3D71979980000000
  %93 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %94 = tail call i32 @llvm.smin.i32(i32 %67, i32 %93)
  %95 = load ptr, ptr %27, align 8
  %96 = load i32, ptr %28, align 4
  %97 = mul i32 %96, %63
  %98 = add i32 %97, %94
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %95, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = fsub reassoc ninf nsz float %101, %57
  %103 = fmul reassoc ninf nsz float %102, %102
  %104 = fmul reassoc ninf nsz float %103, %23
  %105 = fsub reassoc ninf nsz float %25, %104
  %106 = tail call noundef float @expf(float noundef %105) #7
  %107 = load ptr, ptr %29, align 8
  %108 = load i32, ptr %30, align 4
  %109 = mul i32 %108, %63
  %110 = add i32 %109, %94
  %111 = shl i32 %110, 1
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %107, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = getelementptr i8, ptr %113, i64 4
  %116 = load float, ptr %115, align 4
  %117 = fmul reassoc ninf nsz float %114, %106
  %118 = fmul reassoc ninf nsz float %116, %106
  %119 = fadd reassoc ninf nsz float %117, %90
  %120 = fadd reassoc ninf nsz float %118, %91
  %121 = fadd reassoc ninf nsz float %92, %106
  %122 = add i32 %49, 1
  %123 = tail call i32 @llvm.smax.i32(i32 %122, i32 0)
  %124 = tail call i32 @llvm.smin.i32(i32 %67, i32 %123)
  %125 = load ptr, ptr %27, align 8
  %126 = load i32, ptr %28, align 4
  %127 = mul i32 %126, %63
  %128 = add i32 %127, %124
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %125, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = fsub reassoc ninf nsz float %131, %57
  %133 = fmul reassoc ninf nsz float %132, %132
  %134 = fmul reassoc ninf nsz float %133, %23
  %135 = fsub reassoc ninf nsz float %24, %134
  %136 = tail call noundef float @expf(float noundef %135) #7
  %137 = load ptr, ptr %29, align 8
  %138 = load i32, ptr %30, align 4
  %139 = mul i32 %138, %63
  %140 = add i32 %139, %124
  %141 = shl i32 %140, 1
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %137, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = getelementptr i8, ptr %143, i64 4
  %146 = load float, ptr %145, align 4
  %147 = fmul reassoc ninf nsz float %144, %136
  %148 = fmul reassoc ninf nsz float %146, %136
  %149 = fadd reassoc ninf nsz float %119, %147
  %150 = fadd reassoc ninf nsz float %120, %148
  %151 = fadd reassoc ninf nsz float %121, %136
  %152 = tail call i32 @llvm.smax.i32(i32 %46, i32 0)
  %153 = tail call i32 @llvm.smin.i32(i32 %61, i32 %152)
  %154 = load ptr, ptr %27, align 8
  %155 = load i32, ptr %28, align 4
  %156 = mul i32 %155, %153
  %157 = add i32 %156, %69
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %154, i64 %158
  %160 = load float, ptr %159, align 4
  %161 = fsub reassoc ninf nsz float %160, %57
  %162 = fmul reassoc ninf nsz float %161, %161
  %163 = fmul reassoc ninf nsz float %162, %23
  %164 = fsub reassoc ninf nsz float %25, %163
  %165 = tail call noundef float @expf(float noundef %164) #7
  %166 = load ptr, ptr %29, align 8
  %167 = load i32, ptr %30, align 4
  %168 = mul i32 %167, %153
  %169 = add i32 %168, %69
  %170 = shl i32 %169, 1
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %166, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = getelementptr i8, ptr %172, i64 4
  %175 = load float, ptr %174, align 4
  %176 = fmul reassoc ninf nsz float %173, %165
  %177 = fmul reassoc ninf nsz float %175, %165
  %178 = fadd reassoc ninf nsz float %149, %176
  %179 = fadd reassoc ninf nsz float %150, %177
  %180 = fadd reassoc ninf nsz float %151, %165
  %181 = load ptr, ptr %27, align 8
  %182 = load i32, ptr %28, align 4
  %183 = mul i32 %182, %153
  %184 = add i32 %183, %94
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, ptr %181, i64 %185
  %187 = load float, ptr %186, align 4
  %188 = fsub reassoc ninf nsz float %187, %57
  %189 = fmul reassoc ninf nsz float %188, %188
  %190 = fmul reassoc ninf nsz float %189, %31
  %191 = tail call noundef float @expf(float noundef %190) #7
  %192 = load ptr, ptr %29, align 8
  %193 = load i32, ptr %30, align 4
  %194 = mul i32 %193, %153
  %195 = add i32 %194, %94
  %196 = shl i32 %195, 1
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %192, i64 %197
  %199 = load float, ptr %198, align 4
  %200 = getelementptr i8, ptr %198, i64 4
  %201 = load float, ptr %200, align 4
  %202 = fmul reassoc ninf nsz float %199, %191
  %203 = fmul reassoc ninf nsz float %201, %191
  %204 = fadd reassoc ninf nsz float %178, %202
  %205 = fadd reassoc ninf nsz float %179, %203
  %206 = fadd reassoc ninf nsz float %180, %191
  %207 = load ptr, ptr %27, align 8
  %208 = load i32, ptr %28, align 4
  %209 = mul i32 %208, %153
  %210 = add i32 %209, %124
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %207, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = fsub reassoc ninf nsz float %213, %57
  %215 = fmul reassoc ninf nsz float %214, %214
  %216 = fmul reassoc ninf nsz float %215, %23
  %217 = fsub reassoc ninf nsz float %25, %216
  %218 = tail call noundef float @expf(float noundef %217) #7
  %219 = load ptr, ptr %29, align 8
  %220 = load i32, ptr %30, align 4
  %221 = mul i32 %220, %153
  %222 = add i32 %221, %124
  %223 = shl i32 %222, 1
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %219, i64 %224
  %226 = load float, ptr %225, align 4
  %227 = getelementptr i8, ptr %225, i64 4
  %228 = load float, ptr %227, align 4
  %229 = fmul reassoc ninf nsz float %226, %218
  %230 = fmul reassoc ninf nsz float %228, %218
  %231 = fadd reassoc ninf nsz float %204, %229
  %232 = fadd reassoc ninf nsz float %205, %230
  %233 = fadd reassoc ninf nsz float %206, %218
  %234 = add i32 %46, 1
  %235 = tail call i32 @llvm.smax.i32(i32 %234, i32 0)
  %236 = tail call i32 @llvm.smin.i32(i32 %61, i32 %235)
  %237 = load ptr, ptr %27, align 8
  %238 = load i32, ptr %28, align 4
  %239 = mul i32 %238, %236
  %240 = add i32 %239, %69
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %237, i64 %241
  %243 = load float, ptr %242, align 4
  %244 = fsub reassoc ninf nsz float %243, %57
  %245 = fmul reassoc ninf nsz float %244, %244
  %246 = fmul reassoc ninf nsz float %245, %23
  %247 = fsub reassoc ninf nsz float %24, %246
  %248 = tail call noundef float @expf(float noundef %247) #7
  %249 = load ptr, ptr %29, align 8
  %250 = load i32, ptr %30, align 4
  %251 = mul i32 %250, %236
  %252 = add i32 %251, %69
  %253 = shl i32 %252, 1
  %254 = sext i32 %253 to i64
  %255 = getelementptr float, ptr %249, i64 %254
  %256 = load float, ptr %255, align 4
  %257 = getelementptr i8, ptr %255, i64 4
  %258 = load float, ptr %257, align 4
  %259 = fmul reassoc ninf nsz float %256, %248
  %260 = fmul reassoc ninf nsz float %258, %248
  %261 = fadd reassoc ninf nsz float %231, %259
  %262 = fadd reassoc ninf nsz float %232, %260
  %263 = fadd reassoc ninf nsz float %233, %248
  %264 = load ptr, ptr %27, align 8
  %265 = load i32, ptr %28, align 4
  %266 = mul i32 %265, %236
  %267 = add i32 %266, %94
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, ptr %264, i64 %268
  %270 = load float, ptr %269, align 4
  %271 = fsub reassoc ninf nsz float %270, %57
  %272 = fmul reassoc ninf nsz float %271, %271
  %273 = fmul reassoc ninf nsz float %272, %23
  %274 = fsub reassoc ninf nsz float %25, %273
  %275 = tail call noundef float @expf(float noundef %274) #7
  %276 = load ptr, ptr %29, align 8
  %277 = load i32, ptr %30, align 4
  %278 = mul i32 %277, %236
  %279 = add i32 %278, %94
  %280 = shl i32 %279, 1
  %281 = sext i32 %280 to i64
  %282 = getelementptr float, ptr %276, i64 %281
  %283 = load float, ptr %282, align 4
  %284 = getelementptr i8, ptr %282, i64 4
  %285 = load float, ptr %284, align 4
  %286 = fmul reassoc ninf nsz float %283, %275
  %287 = fmul reassoc ninf nsz float %285, %275
  %288 = fadd reassoc ninf nsz float %261, %286
  %289 = fadd reassoc ninf nsz float %262, %287
  %290 = fadd reassoc ninf nsz float %263, %275
  %291 = load ptr, ptr %27, align 8
  %292 = load i32, ptr %28, align 4
  %293 = mul i32 %292, %236
  %294 = add i32 %293, %124
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, ptr %291, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = fsub reassoc ninf nsz float %297, %57
  %299 = fmul reassoc ninf nsz float %298, %298
  %300 = fmul reassoc ninf nsz float %299, %23
  %301 = fsub reassoc ninf nsz float %24, %300
  %302 = tail call noundef float @expf(float noundef %301) #7
  %303 = load ptr, ptr %29, align 8
  %304 = load i32, ptr %30, align 4
  %305 = mul i32 %304, %236
  %306 = add i32 %305, %124
  %307 = shl i32 %306, 1
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %303, i64 %308
  %310 = load float, ptr %309, align 4
  %311 = getelementptr i8, ptr %309, i64 4
  %312 = load float, ptr %311, align 4
  %313 = fmul reassoc ninf nsz float %310, %302
  %314 = fmul reassoc ninf nsz float %312, %302
  %315 = fadd reassoc ninf nsz float %288, %313
  %316 = fadd reassoc ninf nsz float %289, %314
  %317 = fadd reassoc ninf nsz float %290, %302
  %318 = fdiv reassoc ninf nsz float %315, %317
  %319 = fdiv reassoc ninf nsz float %316, %317
  %320 = load ptr, ptr %32, align 8
  %321 = load i32, ptr %33, align 4
  %322 = sub i32 %321, %39
  %323 = shl i32 %322, 1
  %324 = mul i32 %323, %46
  %325 = add i32 %lsr.iv, %324
  %326 = sext i32 %325 to i64
  %327 = getelementptr float, ptr %320, i64 %326
  store float %318, ptr %327, align 4
  %328 = load ptr, ptr %32, align 8
  %329 = load i32, ptr %33, align 4
  %330 = sub i32 %329, %39
  %331 = shl i32 %330, 1
  %332 = mul i32 %331, %46
  %333 = add i32 %lsr.iv, %332
  %334 = add i32 %333, 1
  %335 = sext i32 %334 to i64
  %336 = getelementptr float, ptr %328, i64 %335
  store float %319, ptr %336, align 4
  %337 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %337
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
  %4 = alloca %struct.RuntimeContext.11, align 8
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
