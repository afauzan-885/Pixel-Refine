; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_downsample_2x_kernel_3ch_c264_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 8
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 12
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 24
  %16 = load i32, ptr %15, align 4
  %17 = getelementptr i8, ptr %14, i64 28
  %18 = load i32, ptr %17, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %20 = tail call i32 @llvm.smax.i32(i32 %18, i32 0)
  %21 = load ptr, ptr %2, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 4
  store i32 %20, ptr %24, align 4
  %25 = mul i32 %20, %19
  %26 = load ptr, ptr %2, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  store i32 %25, ptr %28, align 4
  ret void
}

define void @_downsample_2x_kernel_3ch_c264_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %20 = load ptr, ptr %0, align 8
  %21 = getelementptr i8, ptr %20, i64 16
  %22 = getelementptr i8, ptr %20, i64 4
  %23 = getelementptr i8, ptr %20, i64 8
  %24 = getelementptr i8, ptr %20, i64 40
  %25 = getelementptr i8, ptr %20, i64 28
  %26 = getelementptr i8, ptr %20, i64 32
  %27 = shl i32 %16, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %27, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.063 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %520, %for_loop_body ]
  %28 = load ptr, ptr %3, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 4
  %32 = load i32, ptr %31, align 4
  %33 = sdiv i32 %.063, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.063
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.063, %34
  %38 = and i1 %36, %37
  %.neg4 = sext i1 %38 to i32
  %39 = add i32 %33, %.neg4
  %40 = shl i32 %39, 1
  %41 = mul i32 %32, -2
  %42 = mul i32 %41, %39
  %43 = add i32 %lsr.iv, %42
  %44 = add i32 %40, -2
  %45 = tail call i32 @llvm.abs.i32(i32 %44, i1 true)
  %46 = getelementptr inbounds nuw i8, ptr %30, i64 8
  %47 = load i32, ptr %46, align 4
  %48 = add i32 %47, -1
  %49 = sub i32 %45, %48
  %50 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %51 = shl nuw i32 %50, 1
  %52 = sub i32 %45, %51
  %53 = tail call i32 @llvm.smax.i32(i32 %52, i32 0)
  %54 = tail call i32 @llvm.smin.i32(i32 %48, i32 %53)
  %55 = add i32 %43, -2
  %56 = tail call i32 @llvm.abs.i32(i32 %55, i1 true)
  %57 = getelementptr inbounds nuw i8, ptr %30, i64 12
  %58 = load i32, ptr %57, align 4
  %59 = add i32 %58, -1
  %60 = sub i32 %56, %59
  %61 = tail call i32 @llvm.smax.i32(i32 %60, i32 0)
  %62 = shl nuw i32 %61, 1
  %63 = sub i32 %56, %62
  %64 = tail call i32 @llvm.smax.i32(i32 %63, i32 0)
  %65 = tail call i32 @llvm.smin.i32(i32 %59, i32 %64)
  %66 = load ptr, ptr %21, align 8
  %67 = load i32, ptr %22, align 4
  %68 = load i32, ptr %23, align 4
  %69 = mul i32 %54, %67
  %70 = add i32 %65, %69
  %71 = mul i32 %70, %68
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, ptr %66, i64 %72
  %74 = load float, ptr %73, align 4
  %75 = add i32 %71, 1
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, ptr %66, i64 %76
  %78 = load float, ptr %77, align 4
  %79 = add i32 %71, 2
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, ptr %66, i64 %80
  %82 = load float, ptr %81, align 4
  %83 = add i32 %43, -1
  %84 = tail call i32 @llvm.abs.i32(i32 %83, i1 true)
  %85 = sub i32 %84, %59
  %86 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %87 = shl nuw i32 %86, 1
  %88 = sub i32 %84, %87
  %89 = tail call i32 @llvm.smax.i32(i32 %88, i32 0)
  %90 = tail call i32 @llvm.smin.i32(i32 %59, i32 %89)
  %91 = add i32 %90, %69
  %92 = mul i32 %91, %68
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %66, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = add i32 %92, 1
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %66, i64 %97
  %99 = load float, ptr %98, align 4
  %100 = add i32 %92, 2
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %66, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = tail call i32 @llvm.abs.i32(i32 %43, i1 true)
  %105 = sub i32 %104, %59
  %106 = tail call i32 @llvm.smax.i32(i32 %105, i32 0)
  %107 = shl nuw i32 %106, 1
  %108 = sub i32 %104, %107
  %109 = tail call i32 @llvm.smax.i32(i32 %108, i32 0)
  %110 = tail call i32 @llvm.smin.i32(i32 %59, i32 %109)
  %111 = add i32 %69, %110
  %112 = mul i32 %111, %68
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %66, i64 %113
  %115 = load float, ptr %114, align 4
  %116 = add i32 %112, 1
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %66, i64 %117
  %119 = load float, ptr %118, align 4
  %120 = add i32 %112, 2
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %66, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = add i32 %43, 1
  %125 = tail call i32 @llvm.abs.i32(i32 %124, i1 true)
  %126 = sub i32 %125, %59
  %127 = tail call i32 @llvm.smax.i32(i32 %126, i32 0)
  %128 = shl nuw i32 %127, 1
  %129 = sub i32 %125, %128
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 0)
  %131 = tail call i32 @llvm.smin.i32(i32 %59, i32 %130)
  %132 = add i32 %131, %69
  %133 = mul i32 %132, %68
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %66, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = add i32 %133, 1
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %66, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = add i32 %133, 2
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %66, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = add i32 %43, 2
  %146 = tail call i32 @llvm.abs.i32(i32 %145, i1 true)
  %147 = sub i32 %146, %59
  %148 = tail call i32 @llvm.smax.i32(i32 %147, i32 0)
  %149 = shl nuw i32 %148, 1
  %150 = sub i32 %146, %149
  %151 = tail call i32 @llvm.smax.i32(i32 %150, i32 0)
  %152 = tail call i32 @llvm.smin.i32(i32 %59, i32 %151)
  %153 = add i32 %152, %69
  %154 = mul i32 %153, %68
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %66, i64 %155
  %157 = load float, ptr %156, align 4
  %158 = add i32 %154, 1
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %66, i64 %159
  %161 = load float, ptr %160, align 4
  %162 = add i32 %154, 2
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %66, i64 %163
  %165 = load float, ptr %164, align 4
  %166 = add i32 %40, -1
  %167 = tail call i32 @llvm.abs.i32(i32 %166, i1 true)
  %168 = sub i32 %167, %48
  %169 = tail call i32 @llvm.smax.i32(i32 %168, i32 0)
  %170 = shl nuw i32 %169, 1
  %171 = sub i32 %167, %170
  %172 = tail call i32 @llvm.smax.i32(i32 %171, i32 0)
  %173 = tail call i32 @llvm.smin.i32(i32 %48, i32 %172)
  %174 = mul i32 %173, %67
  %175 = add i32 %65, %174
  %176 = mul i32 %175, %68
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, ptr %66, i64 %177
  %179 = load float, ptr %178, align 4
  %180 = add i32 %176, 1
  %181 = sext i32 %180 to i64
  %182 = getelementptr float, ptr %66, i64 %181
  %183 = load float, ptr %182, align 4
  %184 = add i32 %176, 2
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, ptr %66, i64 %185
  %187 = load float, ptr %186, align 4
  %188 = add i32 %90, %174
  %189 = mul i32 %188, %68
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, ptr %66, i64 %190
  %192 = load float, ptr %191, align 4
  %193 = add i32 %189, 1
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, ptr %66, i64 %194
  %196 = load float, ptr %195, align 4
  %197 = add i32 %189, 2
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %66, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = add i32 %174, %110
  %202 = mul i32 %201, %68
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %66, i64 %203
  %205 = load float, ptr %204, align 4
  %206 = add i32 %202, 1
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, ptr %66, i64 %207
  %209 = load float, ptr %208, align 4
  %210 = add i32 %202, 2
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %66, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = add i32 %131, %174
  %215 = mul i32 %214, %68
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, ptr %66, i64 %216
  %218 = load float, ptr %217, align 4
  %219 = add i32 %215, 1
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, ptr %66, i64 %220
  %222 = load float, ptr %221, align 4
  %223 = add i32 %215, 2
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %66, i64 %224
  %226 = load float, ptr %225, align 4
  %227 = add i32 %152, %174
  %228 = mul i32 %227, %68
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, ptr %66, i64 %229
  %231 = load float, ptr %230, align 4
  %232 = add i32 %228, 1
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %66, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = add i32 %228, 2
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, ptr %66, i64 %237
  %239 = load float, ptr %238, align 4
  %240 = tail call i32 @llvm.abs.i32(i32 %40, i1 true)
  %241 = sub i32 %240, %48
  %242 = tail call i32 @llvm.smax.i32(i32 %241, i32 0)
  %243 = shl nuw i32 %242, 1
  %244 = sub i32 %240, %243
  %245 = tail call i32 @llvm.smax.i32(i32 %244, i32 0)
  %246 = tail call i32 @llvm.smin.i32(i32 %48, i32 %245)
  %247 = mul i32 %246, %67
  %248 = add i32 %65, %247
  %249 = mul i32 %248, %68
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, ptr %66, i64 %250
  %252 = load float, ptr %251, align 4
  %253 = add i32 %249, 1
  %254 = sext i32 %253 to i64
  %255 = getelementptr float, ptr %66, i64 %254
  %256 = load float, ptr %255, align 4
  %257 = add i32 %249, 2
  %258 = sext i32 %257 to i64
  %259 = getelementptr float, ptr %66, i64 %258
  %260 = load float, ptr %259, align 4
  %261 = add i32 %90, %247
  %262 = mul i32 %261, %68
  %263 = sext i32 %262 to i64
  %264 = getelementptr float, ptr %66, i64 %263
  %265 = load float, ptr %264, align 4
  %266 = add i32 %262, 1
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, ptr %66, i64 %267
  %269 = load float, ptr %268, align 4
  %270 = add i32 %262, 2
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %66, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = add i32 %110, %247
  %275 = mul i32 %274, %68
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, ptr %66, i64 %276
  %278 = load float, ptr %277, align 4
  %279 = add i32 %275, 1
  %280 = sext i32 %279 to i64
  %281 = getelementptr float, ptr %66, i64 %280
  %282 = load float, ptr %281, align 4
  %283 = add i32 %275, 2
  %284 = sext i32 %283 to i64
  %285 = getelementptr float, ptr %66, i64 %284
  %286 = load float, ptr %285, align 4
  %287 = fmul reassoc ninf nsz float %278, 3.600000e+01
  %288 = fmul reassoc ninf nsz float %282, 3.600000e+01
  %289 = fmul reassoc ninf nsz float %286, 3.600000e+01
  %290 = add i32 %131, %247
  %291 = mul i32 %290, %68
  %292 = sext i32 %291 to i64
  %293 = getelementptr float, ptr %66, i64 %292
  %294 = load float, ptr %293, align 4
  %295 = add i32 %291, 1
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, ptr %66, i64 %296
  %298 = load float, ptr %297, align 4
  %299 = add i32 %291, 2
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, ptr %66, i64 %300
  %302 = load float, ptr %301, align 4
  %303 = add i32 %152, %247
  %304 = mul i32 %303, %68
  %305 = sext i32 %304 to i64
  %306 = getelementptr float, ptr %66, i64 %305
  %307 = load float, ptr %306, align 4
  %308 = add i32 %304, 1
  %309 = sext i32 %308 to i64
  %310 = getelementptr float, ptr %66, i64 %309
  %311 = load float, ptr %310, align 4
  %312 = add i32 %304, 2
  %313 = sext i32 %312 to i64
  %314 = getelementptr float, ptr %66, i64 %313
  %315 = load float, ptr %314, align 4
  %316 = or disjoint i32 %40, 1
  %317 = tail call i32 @llvm.abs.i32(i32 %316, i1 true)
  %318 = sub i32 %317, %48
  %319 = tail call i32 @llvm.smax.i32(i32 %318, i32 0)
  %320 = shl nuw i32 %319, 1
  %321 = sub i32 %317, %320
  %322 = tail call i32 @llvm.smax.i32(i32 %321, i32 0)
  %323 = tail call i32 @llvm.smin.i32(i32 %48, i32 %322)
  %324 = mul i32 %323, %67
  %325 = add i32 %65, %324
  %326 = mul i32 %325, %68
  %327 = sext i32 %326 to i64
  %328 = getelementptr float, ptr %66, i64 %327
  %329 = load float, ptr %328, align 4
  %330 = add i32 %326, 1
  %331 = sext i32 %330 to i64
  %332 = getelementptr float, ptr %66, i64 %331
  %333 = load float, ptr %332, align 4
  %334 = add i32 %326, 2
  %335 = sext i32 %334 to i64
  %336 = getelementptr float, ptr %66, i64 %335
  %337 = load float, ptr %336, align 4
  %338 = add i32 %90, %324
  %339 = mul i32 %338, %68
  %340 = sext i32 %339 to i64
  %341 = getelementptr float, ptr %66, i64 %340
  %342 = load float, ptr %341, align 4
  %343 = add i32 %339, 1
  %344 = sext i32 %343 to i64
  %345 = getelementptr float, ptr %66, i64 %344
  %346 = load float, ptr %345, align 4
  %347 = add i32 %339, 2
  %348 = sext i32 %347 to i64
  %349 = getelementptr float, ptr %66, i64 %348
  %350 = load float, ptr %349, align 4
  %351 = add i32 %324, %110
  %352 = mul i32 %351, %68
  %353 = sext i32 %352 to i64
  %354 = getelementptr float, ptr %66, i64 %353
  %355 = load float, ptr %354, align 4
  %356 = add i32 %352, 1
  %357 = sext i32 %356 to i64
  %358 = getelementptr float, ptr %66, i64 %357
  %359 = load float, ptr %358, align 4
  %360 = add i32 %352, 2
  %361 = sext i32 %360 to i64
  %362 = getelementptr float, ptr %66, i64 %361
  %363 = load float, ptr %362, align 4
  %364 = add i32 %131, %324
  %365 = mul i32 %364, %68
  %366 = sext i32 %365 to i64
  %367 = getelementptr float, ptr %66, i64 %366
  %368 = load float, ptr %367, align 4
  %369 = add i32 %365, 1
  %370 = sext i32 %369 to i64
  %371 = getelementptr float, ptr %66, i64 %370
  %372 = load float, ptr %371, align 4
  %373 = add i32 %365, 2
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, ptr %66, i64 %374
  %376 = load float, ptr %375, align 4
  %377 = add i32 %152, %324
  %378 = mul i32 %377, %68
  %379 = sext i32 %378 to i64
  %380 = getelementptr float, ptr %66, i64 %379
  %381 = load float, ptr %380, align 4
  %382 = add i32 %378, 1
  %383 = sext i32 %382 to i64
  %384 = getelementptr float, ptr %66, i64 %383
  %385 = load float, ptr %384, align 4
  %386 = add i32 %378, 2
  %387 = sext i32 %386 to i64
  %388 = getelementptr float, ptr %66, i64 %387
  %389 = load float, ptr %388, align 4
  %390 = add i32 %40, 2
  %391 = tail call i32 @llvm.abs.i32(i32 %390, i1 true)
  %392 = sub i32 %391, %48
  %393 = tail call i32 @llvm.smax.i32(i32 %392, i32 0)
  %394 = shl nuw i32 %393, 1
  %395 = sub i32 %391, %394
  %396 = tail call i32 @llvm.smax.i32(i32 %395, i32 0)
  %397 = tail call i32 @llvm.smin.i32(i32 %48, i32 %396)
  %398 = mul i32 %397, %67
  %399 = add i32 %65, %398
  %400 = mul i32 %399, %68
  %401 = sext i32 %400 to i64
  %402 = getelementptr float, ptr %66, i64 %401
  %403 = load float, ptr %402, align 4
  %404 = add i32 %400, 1
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, ptr %66, i64 %405
  %407 = load float, ptr %406, align 4
  %408 = add i32 %400, 2
  %409 = sext i32 %408 to i64
  %410 = getelementptr float, ptr %66, i64 %409
  %411 = load float, ptr %410, align 4
  %412 = add i32 %90, %398
  %413 = mul i32 %412, %68
  %414 = sext i32 %413 to i64
  %415 = getelementptr float, ptr %66, i64 %414
  %416 = load float, ptr %415, align 4
  %417 = add i32 %413, 1
  %418 = sext i32 %417 to i64
  %419 = getelementptr float, ptr %66, i64 %418
  %420 = load float, ptr %419, align 4
  %421 = add i32 %413, 2
  %422 = sext i32 %421 to i64
  %423 = getelementptr float, ptr %66, i64 %422
  %424 = load float, ptr %423, align 4
  %425 = add i32 %398, %110
  %426 = mul i32 %425, %68
  %427 = sext i32 %426 to i64
  %428 = getelementptr float, ptr %66, i64 %427
  %429 = load float, ptr %428, align 4
  %430 = add i32 %426, 1
  %431 = sext i32 %430 to i64
  %432 = getelementptr float, ptr %66, i64 %431
  %433 = load float, ptr %432, align 4
  %434 = add i32 %426, 2
  %435 = sext i32 %434 to i64
  %436 = getelementptr float, ptr %66, i64 %435
  %437 = load float, ptr %436, align 4
  %438 = add i32 %131, %398
  %439 = mul i32 %438, %68
  %440 = sext i32 %439 to i64
  %441 = getelementptr float, ptr %66, i64 %440
  %442 = load float, ptr %441, align 4
  %443 = add i32 %439, 1
  %444 = sext i32 %443 to i64
  %445 = getelementptr float, ptr %66, i64 %444
  %446 = load float, ptr %445, align 4
  %447 = add i32 %439, 2
  %448 = sext i32 %447 to i64
  %449 = getelementptr float, ptr %66, i64 %448
  %450 = load float, ptr %449, align 4
  %451 = add i32 %152, %398
  %452 = mul i32 %451, %68
  %453 = sext i32 %452 to i64
  %454 = getelementptr float, ptr %66, i64 %453
  %455 = load float, ptr %454, align 4
  %456 = add i32 %452, 1
  %457 = sext i32 %456 to i64
  %458 = getelementptr float, ptr %66, i64 %457
  %459 = load float, ptr %458, align 4
  %460 = add i32 %452, 2
  %461 = sext i32 %460 to i64
  %462 = getelementptr float, ptr %66, i64 %461
  %463 = load float, ptr %462, align 4
  %reass.add = fadd reassoc ninf nsz float %136, %95
  %reass.add5 = fadd reassoc ninf nsz float %reass.add, %179
  %reass.add6 = fadd reassoc ninf nsz float %reass.add5, %231
  %reass.add7 = fadd reassoc ninf nsz float %reass.add6, %329
  %reass.add8 = fadd reassoc ninf nsz float %reass.add7, %381
  %reass.add9 = fadd reassoc ninf nsz float %reass.add8, %416
  %reass.add10 = fadd reassoc ninf nsz float %reass.add9, %442
  %reass.mul = fmul reassoc ninf nsz float %reass.add10, 4.000000e+00
  %reass.add11 = fadd reassoc ninf nsz float %265, %205
  %reass.add12 = fadd reassoc ninf nsz float %reass.add11, %294
  %reass.add13 = fadd reassoc ninf nsz float %reass.add12, %355
  %reass.mul14 = fmul reassoc ninf nsz float %reass.add13, 2.400000e+01
  %reass.add15 = fadd reassoc ninf nsz float %218, %192
  %reass.add16 = fadd reassoc ninf nsz float %reass.add15, %342
  %reass.add17 = fadd reassoc ninf nsz float %reass.add16, %368
  %reass.mul18 = fmul reassoc ninf nsz float %reass.add17, 1.600000e+01
  %reass.add19 = fadd reassoc ninf nsz float %252, %115
  %reass.add20 = fadd reassoc ninf nsz float %reass.add19, %307
  %reass.add21 = fadd reassoc ninf nsz float %reass.add20, %429
  %reass.mul22 = fmul reassoc ninf nsz float %reass.add21, 6.000000e+00
  %464 = fadd reassoc ninf nsz float %157, %74
  %465 = fadd reassoc ninf nsz float %464, %287
  %466 = fadd reassoc ninf nsz float %465, %reass.mul14
  %467 = fadd reassoc ninf nsz float %466, %reass.mul18
  %468 = fadd reassoc ninf nsz float %467, %403
  %469 = fadd reassoc ninf nsz float %468, %reass.mul22
  %470 = fadd reassoc ninf nsz float %469, %455
  %471 = fadd reassoc ninf nsz float %470, %reass.mul
  %reass.add23 = fadd reassoc ninf nsz float %140, %99
  %reass.add24 = fadd reassoc ninf nsz float %reass.add23, %183
  %reass.add25 = fadd reassoc ninf nsz float %reass.add24, %235
  %reass.add26 = fadd reassoc ninf nsz float %reass.add25, %333
  %reass.add27 = fadd reassoc ninf nsz float %reass.add26, %385
  %reass.add28 = fadd reassoc ninf nsz float %reass.add27, %420
  %reass.add29 = fadd reassoc ninf nsz float %reass.add28, %446
  %reass.mul30 = fmul reassoc ninf nsz float %reass.add29, 4.000000e+00
  %reass.add31 = fadd reassoc ninf nsz float %269, %209
  %reass.add32 = fadd reassoc ninf nsz float %reass.add31, %298
  %reass.add33 = fadd reassoc ninf nsz float %reass.add32, %359
  %reass.mul34 = fmul reassoc ninf nsz float %reass.add33, 2.400000e+01
  %reass.add35 = fadd reassoc ninf nsz float %222, %196
  %reass.add36 = fadd reassoc ninf nsz float %reass.add35, %346
  %reass.add37 = fadd reassoc ninf nsz float %reass.add36, %372
  %reass.mul38 = fmul reassoc ninf nsz float %reass.add37, 1.600000e+01
  %reass.add39 = fadd reassoc ninf nsz float %256, %119
  %reass.add40 = fadd reassoc ninf nsz float %reass.add39, %311
  %reass.add41 = fadd reassoc ninf nsz float %reass.add40, %433
  %reass.mul42 = fmul reassoc ninf nsz float %reass.add41, 6.000000e+00
  %472 = fadd reassoc ninf nsz float %161, %78
  %473 = fadd reassoc ninf nsz float %472, %288
  %474 = fadd reassoc ninf nsz float %473, %reass.mul34
  %475 = fadd reassoc ninf nsz float %474, %reass.mul38
  %476 = fadd reassoc ninf nsz float %475, %407
  %477 = fadd reassoc ninf nsz float %476, %reass.mul42
  %478 = fadd reassoc ninf nsz float %477, %459
  %479 = fadd reassoc ninf nsz float %478, %reass.mul30
  %reass.add43 = fadd reassoc ninf nsz float %144, %103
  %reass.add44 = fadd reassoc ninf nsz float %reass.add43, %187
  %reass.add45 = fadd reassoc ninf nsz float %reass.add44, %239
  %reass.add46 = fadd reassoc ninf nsz float %reass.add45, %337
  %reass.add47 = fadd reassoc ninf nsz float %reass.add46, %389
  %reass.add48 = fadd reassoc ninf nsz float %reass.add47, %424
  %reass.add49 = fadd reassoc ninf nsz float %reass.add48, %450
  %reass.mul50 = fmul reassoc ninf nsz float %reass.add49, 4.000000e+00
  %reass.add51 = fadd reassoc ninf nsz float %273, %213
  %reass.add52 = fadd reassoc ninf nsz float %reass.add51, %302
  %reass.add53 = fadd reassoc ninf nsz float %reass.add52, %363
  %reass.mul54 = fmul reassoc ninf nsz float %reass.add53, 2.400000e+01
  %reass.add55 = fadd reassoc ninf nsz float %226, %200
  %reass.add56 = fadd reassoc ninf nsz float %reass.add55, %350
  %reass.add57 = fadd reassoc ninf nsz float %reass.add56, %376
  %reass.mul58 = fmul reassoc ninf nsz float %reass.add57, 1.600000e+01
  %reass.add59 = fadd reassoc ninf nsz float %260, %123
  %reass.add60 = fadd reassoc ninf nsz float %reass.add59, %315
  %reass.add61 = fadd reassoc ninf nsz float %reass.add60, %437
  %reass.mul62 = fmul reassoc ninf nsz float %reass.add61, 6.000000e+00
  %480 = fadd reassoc ninf nsz float %165, %82
  %481 = fadd reassoc ninf nsz float %480, %289
  %482 = fadd reassoc ninf nsz float %481, %reass.mul54
  %483 = fadd reassoc ninf nsz float %482, %reass.mul58
  %484 = fadd reassoc ninf nsz float %483, %411
  %485 = fadd reassoc ninf nsz float %484, %reass.mul62
  %486 = fadd reassoc ninf nsz float %485, %463
  %487 = fadd reassoc ninf nsz float %486, %reass.mul50
  %488 = fmul reassoc ninf nsz float %471, 3.906250e-03
  %489 = fmul reassoc ninf nsz float %479, 3.906250e-03
  %490 = fmul reassoc ninf nsz float %487, 3.906250e-03
  %491 = load ptr, ptr %24, align 8
  %492 = load i32, ptr %25, align 4
  %493 = load i32, ptr %26, align 4
  %494 = sub i32 %492, %32
  %495 = mul i32 %494, %39
  %496 = add i32 %.063, %495
  %497 = mul i32 %496, %493
  %498 = sext i32 %497 to i64
  %499 = getelementptr float, ptr %491, i64 %498
  store float %488, ptr %499, align 4
  %500 = load ptr, ptr %24, align 8
  %501 = load i32, ptr %25, align 4
  %502 = load i32, ptr %26, align 4
  %503 = sub i32 %501, %32
  %504 = mul i32 %503, %39
  %505 = add i32 %.063, %504
  %506 = mul i32 %505, %502
  %507 = add i32 %506, 1
  %508 = sext i32 %507 to i64
  %509 = getelementptr float, ptr %500, i64 %508
  store float %489, ptr %509, align 4
  %510 = load ptr, ptr %24, align 8
  %511 = load i32, ptr %25, align 4
  %512 = load i32, ptr %26, align 4
  %513 = sub i32 %511, %32
  %514 = mul i32 %513, %39
  %515 = add i32 %.063, %514
  %516 = mul i32 %515, %512
  %517 = add i32 %516, 2
  %518 = sext i32 %517 to i64
  %519 = getelementptr float, ptr %510, i64 %518
  store float %490, ptr %519, align 4
  %520 = add nsw i32 %.063, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %520
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
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
