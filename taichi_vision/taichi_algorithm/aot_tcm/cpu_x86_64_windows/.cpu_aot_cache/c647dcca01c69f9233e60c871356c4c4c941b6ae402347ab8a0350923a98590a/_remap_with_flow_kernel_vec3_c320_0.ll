; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.15 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_remap_with_flow_kernel_vec3_c320_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 64
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 12
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 68
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 8
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

define void @_remap_with_flow_kernel_vec3_c320_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %14 = add nsw i32 %9, %.neg
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 76
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 72
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 80
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 84
  %27 = load float, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 56
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 60
  %31 = load i32, ptr %30, align 4
  %32 = add i32 %21, -1
  %33 = add i32 %23, -1
  %34 = add i32 %31, -1
  %35 = add i32 %29, -1
  %36 = sitofp i32 %32 to float
  %37 = sitofp i32 %33 to float
  %38 = icmp slt i32 %16, %18
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr i8, ptr %19, i64 32
  %40 = getelementptr i8, ptr %19, i64 20
  %41 = getelementptr i8, ptr %19, i64 24
  %42 = getelementptr i8, ptr %19, i64 8
  %43 = getelementptr i8, ptr %19, i64 4
  %44 = getelementptr i8, ptr %19, i64 48
  %45 = getelementptr i8, ptr %19, i64 44
  %46 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %46, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %328, %for_loop_body ]
  %47 = load ptr, ptr %3, align 8
  %48 = getelementptr inbounds nuw i8, ptr %47, i64 32872
  %49 = load ptr, ptr %48, align 8
  %50 = getelementptr inbounds nuw i8, ptr %49, i64 4
  %51 = load i32, ptr %50, align 4
  %52 = sdiv i32 %.05, %51
  %53 = mul i32 %52, %51
  %54 = xor i32 %51, %.05
  %55 = icmp slt i32 %54, 0
  %56 = icmp ne i32 %.05, %53
  %57 = and i1 %55, %56
  %.neg4 = sext i1 %57 to i32
  %58 = add i32 %52, %.neg4
  %59 = mul i32 %51, -1
  %60 = mul i32 %59, %58
  %61 = add i32 %.05, %60
  %62 = sitofp i32 %61 to float
  %63 = fmul reassoc ninf nsz float %62, %36
  %64 = getelementptr inbounds nuw i8, ptr %49, i64 8
  %65 = load i32, ptr %64, align 4
  %66 = add i32 %65, -1
  %67 = sitofp i32 %66 to float
  %68 = fdiv reassoc ninf nsz float %63, %67
  %69 = sitofp i32 %58 to float
  %70 = fmul reassoc ninf nsz float %69, %37
  %71 = getelementptr inbounds nuw i8, ptr %49, i64 12
  %72 = load i32, ptr %71, align 4
  %73 = add i32 %72, -1
  %74 = sitofp i32 %73 to float
  %75 = fdiv reassoc ninf nsz float %70, %74
  %76 = tail call reassoc ninf nsz float @llvm.floor.f32(float %68)
  %77 = fptosi float %76 to i32
  %78 = tail call reassoc ninf nsz float @llvm.floor.f32(float %75)
  %79 = fptosi float %78 to i32
  %80 = sitofp i32 %77 to float
  %81 = fsub reassoc ninf nsz float %68, %80
  %82 = sitofp i32 %79 to float
  %83 = fsub reassoc ninf nsz float %75, %82
  %84 = tail call i32 @llvm.abs.i32(i32 %77, i1 true)
  %85 = sub i32 %84, %32
  %86 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %87 = shl nuw i32 %86, 1
  %88 = sub i32 %84, %87
  %89 = tail call i32 @llvm.smax.i32(i32 %88, i32 0)
  %90 = tail call i32 @llvm.smin.i32(i32 %32, i32 %89)
  %91 = tail call i32 @llvm.abs.i32(i32 %79, i1 true)
  %92 = sub i32 %91, %33
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = shl nuw i32 %93, 1
  %95 = sub i32 %91, %94
  %96 = tail call i32 @llvm.smax.i32(i32 %95, i32 0)
  %97 = tail call i32 @llvm.smin.i32(i32 %33, i32 %96)
  %98 = add i32 %77, 1
  %99 = tail call i32 @llvm.abs.i32(i32 %98, i1 true)
  %100 = sub i32 %99, %32
  %101 = tail call i32 @llvm.smax.i32(i32 %100, i32 0)
  %102 = shl nuw i32 %101, 1
  %103 = sub i32 %99, %102
  %104 = tail call i32 @llvm.smax.i32(i32 %103, i32 0)
  %105 = tail call i32 @llvm.smin.i32(i32 %32, i32 %104)
  %106 = add i32 %79, 1
  %107 = tail call i32 @llvm.abs.i32(i32 %106, i1 true)
  %108 = sub i32 %107, %33
  %109 = tail call i32 @llvm.smax.i32(i32 %108, i32 0)
  %110 = shl nuw i32 %109, 1
  %111 = sub i32 %107, %110
  %112 = tail call i32 @llvm.smax.i32(i32 %111, i32 0)
  %113 = tail call i32 @llvm.smin.i32(i32 %33, i32 %112)
  %114 = load ptr, ptr %39, align 8
  %115 = load i32, ptr %40, align 4
  %116 = load i32, ptr %41, align 4
  %117 = mul i32 %97, %115
  %118 = add i32 %90, %117
  %119 = mul i32 %118, %116
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %114, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = add i32 %105, %117
  %124 = mul i32 %123, %116
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %114, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = mul i32 %113, %115
  %129 = add i32 %128, %90
  %130 = mul i32 %129, %116
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, ptr %114, i64 %131
  %133 = load float, ptr %132, align 4
  %134 = add i32 %105, %128
  %135 = mul i32 %134, %116
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %114, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = fsub reassoc ninf nsz float 1.000000e+00, %81
  %140 = fmul reassoc ninf nsz float %139, %122
  %141 = fmul reassoc ninf nsz float %81, %127
  %142 = fadd reassoc ninf nsz float %140, %141
  %143 = fmul reassoc ninf nsz float %139, %133
  %144 = fmul reassoc ninf nsz float %81, %138
  %145 = fadd reassoc ninf nsz float %143, %144
  %146 = fsub reassoc ninf nsz float 1.000000e+00, %83
  %147 = fmul reassoc ninf nsz float %142, %146
  %148 = fmul reassoc ninf nsz float %145, %83
  %149 = fadd reassoc ninf nsz float %147, %148
  %150 = add i32 %119, 1
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %114, i64 %151
  %153 = load float, ptr %152, align 4
  %154 = add i32 %124, 1
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %114, i64 %155
  %157 = load float, ptr %156, align 4
  %158 = add i32 %130, 1
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %114, i64 %159
  %161 = load float, ptr %160, align 4
  %162 = add i32 %135, 1
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %114, i64 %163
  %165 = load float, ptr %164, align 4
  %166 = fmul reassoc ninf nsz float %139, %153
  %167 = fmul reassoc ninf nsz float %81, %157
  %168 = fadd reassoc ninf nsz float %166, %167
  %169 = fmul reassoc ninf nsz float %139, %161
  %170 = fmul reassoc ninf nsz float %81, %165
  %171 = fadd reassoc ninf nsz float %169, %170
  %172 = fmul reassoc ninf nsz float %168, %146
  %173 = fmul reassoc ninf nsz float %171, %83
  %174 = fadd reassoc ninf nsz float %172, %173
  %175 = fmul reassoc ninf nsz float %149, %25
  %176 = fadd reassoc ninf nsz float %175, %62
  %177 = fmul reassoc ninf nsz float %174, %27
  %178 = fadd reassoc ninf nsz float %177, %69
  %179 = tail call reassoc ninf nsz float @llvm.floor.f32(float %176)
  %180 = fptosi float %179 to i32
  %181 = tail call reassoc ninf nsz float @llvm.floor.f32(float %178)
  %182 = fptosi float %181 to i32
  %183 = sitofp i32 %180 to float
  %184 = fsub reassoc ninf nsz float %176, %183
  %185 = sitofp i32 %182 to float
  %186 = fsub reassoc ninf nsz float %178, %185
  %187 = tail call i32 @llvm.abs.i32(i32 %180, i1 true)
  %188 = sub i32 %187, %34
  %189 = tail call i32 @llvm.smax.i32(i32 %188, i32 0)
  %190 = shl nuw i32 %189, 1
  %191 = sub i32 %187, %190
  %192 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %193 = tail call i32 @llvm.smin.i32(i32 %34, i32 %192)
  %194 = tail call i32 @llvm.abs.i32(i32 %182, i1 true)
  %195 = sub i32 %194, %35
  %196 = tail call i32 @llvm.smax.i32(i32 %195, i32 0)
  %197 = shl nuw i32 %196, 1
  %198 = sub i32 %194, %197
  %199 = tail call i32 @llvm.smax.i32(i32 %198, i32 0)
  %200 = tail call i32 @llvm.smin.i32(i32 %35, i32 %199)
  %201 = add i32 %180, 1
  %202 = tail call i32 @llvm.abs.i32(i32 %201, i1 true)
  %203 = sub i32 %202, %34
  %204 = tail call i32 @llvm.smax.i32(i32 %203, i32 0)
  %205 = shl nuw i32 %204, 1
  %206 = sub i32 %202, %205
  %207 = tail call i32 @llvm.smax.i32(i32 %206, i32 0)
  %208 = tail call i32 @llvm.smin.i32(i32 %34, i32 %207)
  %209 = add i32 %182, 1
  %210 = tail call i32 @llvm.abs.i32(i32 %209, i1 true)
  %211 = sub i32 %210, %35
  %212 = tail call i32 @llvm.smax.i32(i32 %211, i32 0)
  %213 = shl nuw i32 %212, 1
  %214 = sub i32 %210, %213
  %215 = tail call i32 @llvm.smax.i32(i32 %214, i32 0)
  %216 = tail call i32 @llvm.smin.i32(i32 %35, i32 %215)
  %217 = load ptr, ptr %42, align 8
  %218 = load i32, ptr %43, align 4
  %219 = mul i32 %200, %218
  %220 = add i32 %219, %193
  %221 = mul i32 %220, 3
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, ptr %217, i64 %222
  %224 = load float, ptr %223, align 4
  %225 = add i32 %221, 1
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %217, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = add i32 %221, 2
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, ptr %217, i64 %230
  %232 = load float, ptr %231, align 4
  %233 = add i32 %219, %208
  %234 = mul i32 %233, 3
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %217, i64 %235
  %237 = load float, ptr %236, align 4
  %238 = add i32 %234, 1
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, ptr %217, i64 %239
  %241 = load float, ptr %240, align 4
  %242 = add i32 %234, 2
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, ptr %217, i64 %243
  %245 = load float, ptr %244, align 4
  %246 = mul i32 %216, %218
  %247 = add i32 %246, %193
  %248 = mul i32 %247, 3
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, ptr %217, i64 %249
  %251 = load float, ptr %250, align 4
  %252 = add i32 %248, 1
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, ptr %217, i64 %253
  %255 = load float, ptr %254, align 4
  %256 = add i32 %248, 2
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, ptr %217, i64 %257
  %259 = load float, ptr %258, align 4
  %260 = add i32 %246, %208
  %261 = mul i32 %260, 3
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, ptr %217, i64 %262
  %264 = load float, ptr %263, align 4
  %265 = add i32 %261, 1
  %266 = sext i32 %265 to i64
  %267 = getelementptr float, ptr %217, i64 %266
  %268 = load float, ptr %267, align 4
  %269 = add i32 %261, 2
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, ptr %217, i64 %270
  %272 = load float, ptr %271, align 4
  %273 = fsub reassoc ninf nsz float 1.000000e+00, %184
  %274 = fmul reassoc ninf nsz float %273, %224
  %275 = fmul reassoc ninf nsz float %273, %228
  %276 = fmul reassoc ninf nsz float %273, %232
  %277 = fmul reassoc ninf nsz float %184, %237
  %278 = fmul reassoc ninf nsz float %184, %241
  %279 = fmul reassoc ninf nsz float %184, %245
  %280 = fadd reassoc ninf nsz float %274, %277
  %281 = fadd reassoc ninf nsz float %275, %278
  %282 = fadd reassoc ninf nsz float %276, %279
  %283 = fmul reassoc ninf nsz float %273, %251
  %284 = fmul reassoc ninf nsz float %273, %255
  %285 = fmul reassoc ninf nsz float %273, %259
  %286 = fmul reassoc ninf nsz float %264, %184
  %287 = fmul reassoc ninf nsz float %268, %184
  %288 = fmul reassoc ninf nsz float %272, %184
  %289 = fadd reassoc ninf nsz float %283, %286
  %290 = fadd reassoc ninf nsz float %284, %287
  %291 = fadd reassoc ninf nsz float %288, %285
  %292 = fsub reassoc ninf nsz float 1.000000e+00, %186
  %293 = fmul reassoc ninf nsz float %280, %292
  %294 = fmul reassoc ninf nsz float %281, %292
  %295 = fmul reassoc ninf nsz float %282, %292
  %296 = fmul reassoc ninf nsz float %289, %186
  %297 = fmul reassoc ninf nsz float %290, %186
  %298 = fmul reassoc ninf nsz float %291, %186
  %299 = fadd reassoc ninf nsz float %293, %296
  %300 = fadd reassoc ninf nsz float %294, %297
  %301 = fadd reassoc ninf nsz float %298, %295
  %302 = load ptr, ptr %44, align 8
  %303 = load i32, ptr %45, align 4
  %304 = sub i32 %303, %51
  %305 = mul i32 %304, 3
  %306 = mul i32 %305, %58
  %307 = add i32 %lsr.iv, %306
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %302, i64 %308
  store float %299, ptr %309, align 4
  %310 = load ptr, ptr %44, align 8
  %311 = load i32, ptr %45, align 4
  %312 = sub i32 %311, %51
  %313 = mul i32 %312, 3
  %314 = mul i32 %313, %58
  %315 = add i32 %lsr.iv, %314
  %316 = add i32 %315, 1
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, ptr %310, i64 %317
  store float %300, ptr %318, align 4
  %319 = load ptr, ptr %44, align 8
  %320 = load i32, ptr %45, align 4
  %321 = sub i32 %320, %51
  %322 = mul i32 %321, 3
  %323 = mul i32 %322, %58
  %324 = add i32 %lsr.iv, %323
  %325 = add i32 %324, 2
  %326 = sext i32 %325 to i64
  %327 = getelementptr float, ptr %319, i64 %326
  store float %301, ptr %327, align 4
  %328 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %328
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
  %4 = alloca %struct.RuntimeContext.15, align 8
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
