; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.17 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jblu_1ch_r2_c716_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 56
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 60
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

define void @_jblu_1ch_r2_c716_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #8
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
  %20 = getelementptr i8, ptr %19, i64 48
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 52
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 64
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 68
  %27 = load float, ptr %26, align 4
  %28 = sitofp i32 %21 to float
  %29 = sitofp i32 %23 to float
  %30 = add i32 %21, -1
  %31 = add i32 %23, -1
  %32 = fmul reassoc ninf nsz float %25, -8.000000e+00
  %33 = fmul reassoc ninf nsz float %25, -5.000000e+00
  %34 = fmul reassoc ninf nsz float %25, -4.000000e+00
  %35 = fmul reassoc ninf nsz float %25, -2.000000e+00
  %36 = fneg reassoc ninf nsz float %25
  %37 = icmp slt i32 %16, %18
  br i1 %37, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %38 = getelementptr i8, ptr %19, i64 24
  %39 = getelementptr i8, ptr %19, i64 20
  %40 = getelementptr i8, ptr %19, i64 8
  %41 = getelementptr i8, ptr %19, i64 4
  %42 = fneg reassoc ninf nsz float %27
  %43 = getelementptr i8, ptr %19, i64 40
  %44 = getelementptr i8, ptr %19, i64 36
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %738, %for_loop_body ]
  %45 = load ptr, ptr %3, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 32872
  %47 = load ptr, ptr %46, align 8
  %48 = getelementptr inbounds nuw i8, ptr %47, i64 4
  %49 = load i32, ptr %48, align 4
  %50 = sdiv i32 %.05, %49
  %51 = mul i32 %50, %49
  %52 = xor i32 %49, %.05
  %53 = icmp slt i32 %52, 0
  %54 = icmp ne i32 %.05, %51
  %55 = and i1 %53, %54
  %.neg4 = sext i1 %55 to i32
  %56 = add i32 %50, %.neg4
  %57 = mul i32 %49, -1
  %58 = mul i32 %57, %56
  %59 = add i32 %.05, %58
  %60 = sitofp i32 %56 to float
  %61 = fmul reassoc ninf nsz float %60, %28
  %62 = getelementptr inbounds nuw i8, ptr %47, i64 8
  %63 = load i32, ptr %62, align 4
  %64 = sitofp i32 %63 to float
  %65 = fdiv reassoc ninf nsz float %61, %64
  %66 = tail call reassoc ninf nsz float @llvm.floor.f32(float %65)
  %67 = fptosi float %66 to i32
  %68 = sitofp i32 %59 to float
  %69 = fmul reassoc ninf nsz float %68, %29
  %70 = getelementptr inbounds nuw i8, ptr %47, i64 12
  %71 = load i32, ptr %70, align 4
  %72 = sitofp i32 %71 to float
  %73 = fdiv reassoc ninf nsz float %69, %72
  %74 = tail call reassoc ninf nsz float @llvm.floor.f32(float %73)
  %75 = fptosi float %74 to i32
  %76 = load ptr, ptr %38, align 8
  %77 = load i32, ptr %39, align 4
  %78 = sub i32 %77, %49
  %79 = mul i32 %78, %56
  %80 = add i32 %.05, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, ptr %76, i64 %81
  %83 = load float, ptr %82, align 4
  %84 = add i32 %67, -2
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %86 = tail call i32 @llvm.smin.i32(i32 %30, i32 %85)
  %87 = add i32 %75, -2
  %88 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %31, i32 %88)
  %90 = sitofp i32 %86 to float
  %91 = fmul reassoc ninf nsz float %90, %64
  %92 = fdiv reassoc ninf nsz float %91, %28
  %93 = fadd reassoc ninf nsz float %92, 5.000000e-01
  %94 = fptosi float %93 to i32
  %95 = add i32 %63, -1
  %96 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %97 = tail call i32 @llvm.smin.i32(i32 %95, i32 %96)
  %98 = sitofp i32 %89 to float
  %99 = fmul reassoc ninf nsz float %98, %72
  %100 = fdiv reassoc ninf nsz float %99, %29
  %101 = fadd reassoc ninf nsz float %100, 5.000000e-01
  %102 = fptosi float %101 to i32
  %103 = add i32 %71, -1
  %104 = tail call i32 @llvm.smax.i32(i32 %102, i32 0)
  %105 = tail call i32 @llvm.smin.i32(i32 %103, i32 %104)
  %106 = mul i32 %97, %77
  %107 = add i32 %105, %106
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %76, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = fsub reassoc ninf nsz float %110, %83
  %112 = fmul reassoc ninf nsz float %111, %111
  %113 = fmul reassoc ninf nsz float %112, %27
  %114 = fsub reassoc ninf nsz float %32, %113
  %115 = tail call noundef float @expf(float noundef %114) #8
  %116 = load ptr, ptr %40, align 8
  %117 = load i32, ptr %41, align 4
  %118 = mul i32 %86, %117
  %119 = add i32 %89, %118
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %116, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = fmul reassoc ninf nsz float %122, %115
  %124 = fadd reassoc ninf nsz float %115, 0x3D71979980000000
  %125 = add i32 %75, -1
  %126 = tail call i32 @llvm.smax.i32(i32 %125, i32 0)
  %127 = tail call i32 @llvm.smin.i32(i32 %31, i32 %126)
  %128 = sitofp i32 %127 to float
  %129 = fmul reassoc ninf nsz float %128, %72
  %130 = fdiv reassoc ninf nsz float %129, %29
  %131 = fadd reassoc ninf nsz float %130, 5.000000e-01
  %132 = fptosi float %131 to i32
  %133 = tail call i32 @llvm.smax.i32(i32 %132, i32 0)
  %134 = tail call i32 @llvm.smin.i32(i32 %103, i32 %133)
  %135 = load ptr, ptr %38, align 8
  %136 = load i32, ptr %39, align 4
  %137 = mul i32 %97, %136
  %138 = add i32 %134, %137
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, ptr %135, i64 %139
  %141 = load float, ptr %140, align 4
  %142 = fsub reassoc ninf nsz float %141, %83
  %143 = fmul reassoc ninf nsz float %142, %142
  %144 = fmul reassoc ninf nsz float %143, %27
  %145 = fsub reassoc ninf nsz float %33, %144
  %146 = tail call noundef float @expf(float noundef %145) #8
  %147 = load ptr, ptr %40, align 8
  %148 = load i32, ptr %41, align 4
  %149 = mul i32 %148, %86
  %150 = add i32 %149, %127
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %147, i64 %151
  %153 = load float, ptr %152, align 4
  %154 = fmul reassoc ninf nsz float %153, %146
  %155 = fadd reassoc ninf nsz float %154, %123
  %156 = fadd reassoc ninf nsz float %124, %146
  %157 = tail call i32 @llvm.smax.i32(i32 %75, i32 0)
  %158 = tail call i32 @llvm.smin.i32(i32 %31, i32 %157)
  %159 = sitofp i32 %158 to float
  %160 = fmul reassoc ninf nsz float %159, %72
  %161 = fdiv reassoc ninf nsz float %160, %29
  %162 = fadd reassoc ninf nsz float %161, 5.000000e-01
  %163 = fptosi float %162 to i32
  %164 = tail call i32 @llvm.smax.i32(i32 %163, i32 0)
  %165 = tail call i32 @llvm.smin.i32(i32 %103, i32 %164)
  %166 = load ptr, ptr %38, align 8
  %167 = load i32, ptr %39, align 4
  %168 = mul i32 %97, %167
  %169 = add i32 %168, %165
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, ptr %166, i64 %170
  %172 = load float, ptr %171, align 4
  %173 = fsub reassoc ninf nsz float %172, %83
  %174 = fmul reassoc ninf nsz float %173, %173
  %175 = fmul reassoc ninf nsz float %174, %27
  %176 = fsub reassoc ninf nsz float %34, %175
  %177 = tail call noundef float @expf(float noundef %176) #8
  %178 = load ptr, ptr %40, align 8
  %179 = load i32, ptr %41, align 4
  %180 = mul i32 %179, %86
  %181 = add i32 %180, %158
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %178, i64 %182
  %184 = load float, ptr %183, align 4
  %185 = fmul reassoc ninf nsz float %184, %177
  %186 = fadd reassoc ninf nsz float %155, %185
  %187 = fadd reassoc ninf nsz float %156, %177
  %188 = add i32 %75, 1
  %189 = tail call i32 @llvm.smax.i32(i32 %188, i32 0)
  %190 = tail call i32 @llvm.smin.i32(i32 %31, i32 %189)
  %191 = sitofp i32 %190 to float
  %192 = fmul reassoc ninf nsz float %191, %72
  %193 = fdiv reassoc ninf nsz float %192, %29
  %194 = fadd reassoc ninf nsz float %193, 5.000000e-01
  %195 = fptosi float %194 to i32
  %196 = tail call i32 @llvm.smax.i32(i32 %195, i32 0)
  %197 = tail call i32 @llvm.smin.i32(i32 %103, i32 %196)
  %198 = load ptr, ptr %38, align 8
  %199 = load i32, ptr %39, align 4
  %200 = mul i32 %199, %97
  %201 = add i32 %200, %197
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %198, i64 %202
  %204 = load float, ptr %203, align 4
  %205 = fsub reassoc ninf nsz float %204, %83
  %206 = fmul reassoc ninf nsz float %205, %205
  %207 = fmul reassoc ninf nsz float %206, %27
  %208 = fsub reassoc ninf nsz float %33, %207
  %209 = tail call noundef float @expf(float noundef %208) #8
  %210 = load ptr, ptr %40, align 8
  %211 = load i32, ptr %41, align 4
  %212 = mul i32 %211, %86
  %213 = add i32 %212, %190
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, ptr %210, i64 %214
  %216 = load float, ptr %215, align 4
  %217 = fmul reassoc ninf nsz float %216, %209
  %218 = fadd reassoc ninf nsz float %186, %217
  %219 = fadd reassoc ninf nsz float %187, %209
  %220 = add i32 %75, 2
  %221 = tail call i32 @llvm.smax.i32(i32 %220, i32 0)
  %222 = tail call i32 @llvm.smin.i32(i32 %31, i32 %221)
  %223 = sitofp i32 %222 to float
  %224 = fmul reassoc ninf nsz float %223, %72
  %225 = fdiv reassoc ninf nsz float %224, %29
  %226 = fadd reassoc ninf nsz float %225, 5.000000e-01
  %227 = fptosi float %226 to i32
  %228 = tail call i32 @llvm.smax.i32(i32 %227, i32 0)
  %229 = tail call i32 @llvm.smin.i32(i32 %103, i32 %228)
  %230 = load ptr, ptr %38, align 8
  %231 = load i32, ptr %39, align 4
  %232 = mul i32 %231, %97
  %233 = add i32 %232, %229
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, ptr %230, i64 %234
  %236 = load float, ptr %235, align 4
  %237 = fsub reassoc ninf nsz float %236, %83
  %238 = fmul reassoc ninf nsz float %237, %237
  %239 = fmul reassoc ninf nsz float %238, %27
  %240 = fsub reassoc ninf nsz float %32, %239
  %241 = tail call noundef float @expf(float noundef %240) #8
  %242 = load ptr, ptr %40, align 8
  %243 = load i32, ptr %41, align 4
  %244 = mul i32 %243, %86
  %245 = add i32 %244, %222
  %246 = sext i32 %245 to i64
  %247 = getelementptr float, ptr %242, i64 %246
  %248 = load float, ptr %247, align 4
  %249 = fmul reassoc ninf nsz float %248, %241
  %250 = fadd reassoc ninf nsz float %218, %249
  %251 = fadd reassoc ninf nsz float %219, %241
  %252 = add i32 %67, -1
  %253 = tail call i32 @llvm.smax.i32(i32 %252, i32 0)
  %254 = tail call i32 @llvm.smin.i32(i32 %30, i32 %253)
  %255 = sitofp i32 %254 to float
  %256 = fmul reassoc ninf nsz float %255, %64
  %257 = fdiv reassoc ninf nsz float %256, %28
  %258 = fadd reassoc ninf nsz float %257, 5.000000e-01
  %259 = fptosi float %258 to i32
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = tail call i32 @llvm.smin.i32(i32 %95, i32 %260)
  %262 = load ptr, ptr %38, align 8
  %263 = load i32, ptr %39, align 4
  %264 = mul i32 %263, %261
  %265 = add i32 %264, %105
  %266 = sext i32 %265 to i64
  %267 = getelementptr float, ptr %262, i64 %266
  %268 = load float, ptr %267, align 4
  %269 = fsub reassoc ninf nsz float %268, %83
  %270 = fmul reassoc ninf nsz float %269, %269
  %271 = fmul reassoc ninf nsz float %270, %27
  %272 = fsub reassoc ninf nsz float %33, %271
  %273 = tail call noundef float @expf(float noundef %272) #8
  %274 = load ptr, ptr %40, align 8
  %275 = load i32, ptr %41, align 4
  %276 = mul i32 %275, %254
  %277 = add i32 %276, %89
  %278 = sext i32 %277 to i64
  %279 = getelementptr float, ptr %274, i64 %278
  %280 = load float, ptr %279, align 4
  %281 = fmul reassoc ninf nsz float %280, %273
  %282 = fadd reassoc ninf nsz float %250, %281
  %283 = fadd reassoc ninf nsz float %251, %273
  %284 = load ptr, ptr %38, align 8
  %285 = load i32, ptr %39, align 4
  %286 = mul i32 %285, %261
  %287 = add i32 %286, %134
  %288 = sext i32 %287 to i64
  %289 = getelementptr float, ptr %284, i64 %288
  %290 = load float, ptr %289, align 4
  %291 = fsub reassoc ninf nsz float %290, %83
  %292 = fmul reassoc ninf nsz float %291, %291
  %293 = fmul reassoc ninf nsz float %292, %27
  %294 = fsub reassoc ninf nsz float %35, %293
  %295 = tail call noundef float @expf(float noundef %294) #8
  %296 = load ptr, ptr %40, align 8
  %297 = load i32, ptr %41, align 4
  %298 = mul i32 %297, %254
  %299 = add i32 %298, %127
  %300 = sext i32 %299 to i64
  %301 = getelementptr float, ptr %296, i64 %300
  %302 = load float, ptr %301, align 4
  %303 = fmul reassoc ninf nsz float %302, %295
  %304 = fadd reassoc ninf nsz float %282, %303
  %305 = fadd reassoc ninf nsz float %283, %295
  %306 = load ptr, ptr %38, align 8
  %307 = load i32, ptr %39, align 4
  %308 = mul i32 %307, %261
  %309 = add i32 %308, %165
  %310 = sext i32 %309 to i64
  %311 = getelementptr float, ptr %306, i64 %310
  %312 = load float, ptr %311, align 4
  %313 = fsub reassoc ninf nsz float %312, %83
  %314 = fmul reassoc ninf nsz float %313, %313
  %315 = fmul reassoc ninf nsz float %314, %27
  %316 = fsub reassoc ninf nsz float %36, %315
  %317 = tail call noundef float @expf(float noundef %316) #8
  %318 = load ptr, ptr %40, align 8
  %319 = load i32, ptr %41, align 4
  %320 = mul i32 %319, %254
  %321 = add i32 %320, %158
  %322 = sext i32 %321 to i64
  %323 = getelementptr float, ptr %318, i64 %322
  %324 = load float, ptr %323, align 4
  %325 = fmul reassoc ninf nsz float %324, %317
  %326 = fadd reassoc ninf nsz float %304, %325
  %327 = fadd reassoc ninf nsz float %305, %317
  %328 = load ptr, ptr %38, align 8
  %329 = load i32, ptr %39, align 4
  %330 = mul i32 %329, %261
  %331 = add i32 %330, %197
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, ptr %328, i64 %332
  %334 = load float, ptr %333, align 4
  %335 = fsub reassoc ninf nsz float %334, %83
  %336 = fmul reassoc ninf nsz float %335, %335
  %337 = fmul reassoc ninf nsz float %336, %27
  %338 = fsub reassoc ninf nsz float %35, %337
  %339 = tail call noundef float @expf(float noundef %338) #8
  %340 = load ptr, ptr %40, align 8
  %341 = load i32, ptr %41, align 4
  %342 = mul i32 %341, %254
  %343 = add i32 %342, %190
  %344 = sext i32 %343 to i64
  %345 = getelementptr float, ptr %340, i64 %344
  %346 = load float, ptr %345, align 4
  %347 = fmul reassoc ninf nsz float %346, %339
  %348 = fadd reassoc ninf nsz float %326, %347
  %349 = fadd reassoc ninf nsz float %327, %339
  %350 = load ptr, ptr %38, align 8
  %351 = load i32, ptr %39, align 4
  %352 = mul i32 %351, %261
  %353 = add i32 %352, %229
  %354 = sext i32 %353 to i64
  %355 = getelementptr float, ptr %350, i64 %354
  %356 = load float, ptr %355, align 4
  %357 = fsub reassoc ninf nsz float %356, %83
  %358 = fmul reassoc ninf nsz float %357, %357
  %359 = fmul reassoc ninf nsz float %358, %27
  %360 = fsub reassoc ninf nsz float %33, %359
  %361 = tail call noundef float @expf(float noundef %360) #8
  %362 = load ptr, ptr %40, align 8
  %363 = load i32, ptr %41, align 4
  %364 = mul i32 %363, %254
  %365 = add i32 %364, %222
  %366 = sext i32 %365 to i64
  %367 = getelementptr float, ptr %362, i64 %366
  %368 = load float, ptr %367, align 4
  %369 = fmul reassoc ninf nsz float %368, %361
  %370 = fadd reassoc ninf nsz float %348, %369
  %371 = fadd reassoc ninf nsz float %349, %361
  %372 = tail call i32 @llvm.smax.i32(i32 %67, i32 0)
  %373 = tail call i32 @llvm.smin.i32(i32 %30, i32 %372)
  %374 = sitofp i32 %373 to float
  %375 = fmul reassoc ninf nsz float %374, %64
  %376 = fdiv reassoc ninf nsz float %375, %28
  %377 = fadd reassoc ninf nsz float %376, 5.000000e-01
  %378 = fptosi float %377 to i32
  %379 = tail call i32 @llvm.smax.i32(i32 %378, i32 0)
  %380 = tail call i32 @llvm.smin.i32(i32 %95, i32 %379)
  %381 = load ptr, ptr %38, align 8
  %382 = load i32, ptr %39, align 4
  %383 = mul i32 %382, %380
  %384 = add i32 %383, %105
  %385 = sext i32 %384 to i64
  %386 = getelementptr float, ptr %381, i64 %385
  %387 = load float, ptr %386, align 4
  %388 = fsub reassoc ninf nsz float %387, %83
  %389 = fmul reassoc ninf nsz float %388, %388
  %390 = fmul reassoc ninf nsz float %389, %27
  %391 = fsub reassoc ninf nsz float %34, %390
  %392 = tail call noundef float @expf(float noundef %391) #8
  %393 = load ptr, ptr %40, align 8
  %394 = load i32, ptr %41, align 4
  %395 = mul i32 %394, %373
  %396 = add i32 %395, %89
  %397 = sext i32 %396 to i64
  %398 = getelementptr float, ptr %393, i64 %397
  %399 = load float, ptr %398, align 4
  %400 = fmul reassoc ninf nsz float %399, %392
  %401 = fadd reassoc ninf nsz float %370, %400
  %402 = fadd reassoc ninf nsz float %371, %392
  %403 = load ptr, ptr %38, align 8
  %404 = load i32, ptr %39, align 4
  %405 = mul i32 %404, %380
  %406 = add i32 %405, %134
  %407 = sext i32 %406 to i64
  %408 = getelementptr float, ptr %403, i64 %407
  %409 = load float, ptr %408, align 4
  %410 = fsub reassoc ninf nsz float %409, %83
  %411 = fmul reassoc ninf nsz float %410, %410
  %412 = fmul reassoc ninf nsz float %411, %27
  %413 = fsub reassoc ninf nsz float %36, %412
  %414 = tail call noundef float @expf(float noundef %413) #8
  %415 = load ptr, ptr %40, align 8
  %416 = load i32, ptr %41, align 4
  %417 = mul i32 %416, %373
  %418 = add i32 %417, %127
  %419 = sext i32 %418 to i64
  %420 = getelementptr float, ptr %415, i64 %419
  %421 = load float, ptr %420, align 4
  %422 = fmul reassoc ninf nsz float %421, %414
  %423 = fadd reassoc ninf nsz float %401, %422
  %424 = fadd reassoc ninf nsz float %402, %414
  %425 = load ptr, ptr %38, align 8
  %426 = load i32, ptr %39, align 4
  %427 = mul i32 %426, %380
  %428 = add i32 %427, %165
  %429 = sext i32 %428 to i64
  %430 = getelementptr float, ptr %425, i64 %429
  %431 = load float, ptr %430, align 4
  %432 = fsub reassoc ninf nsz float %431, %83
  %433 = fmul reassoc ninf nsz float %432, %432
  %434 = fmul reassoc ninf nsz float %433, %42
  %435 = tail call noundef float @expf(float noundef %434) #8
  %436 = load ptr, ptr %40, align 8
  %437 = load i32, ptr %41, align 4
  %438 = mul i32 %437, %373
  %439 = add i32 %438, %158
  %440 = sext i32 %439 to i64
  %441 = getelementptr float, ptr %436, i64 %440
  %442 = load float, ptr %441, align 4
  %443 = fmul reassoc ninf nsz float %442, %435
  %444 = fadd reassoc ninf nsz float %423, %443
  %445 = fadd reassoc ninf nsz float %424, %435
  %446 = load ptr, ptr %38, align 8
  %447 = load i32, ptr %39, align 4
  %448 = mul i32 %447, %380
  %449 = add i32 %448, %197
  %450 = sext i32 %449 to i64
  %451 = getelementptr float, ptr %446, i64 %450
  %452 = load float, ptr %451, align 4
  %453 = fsub reassoc ninf nsz float %452, %83
  %454 = fmul reassoc ninf nsz float %453, %453
  %455 = fmul reassoc ninf nsz float %454, %27
  %456 = fsub reassoc ninf nsz float %36, %455
  %457 = tail call noundef float @expf(float noundef %456) #8
  %458 = load ptr, ptr %40, align 8
  %459 = load i32, ptr %41, align 4
  %460 = mul i32 %459, %373
  %461 = add i32 %460, %190
  %462 = sext i32 %461 to i64
  %463 = getelementptr float, ptr %458, i64 %462
  %464 = load float, ptr %463, align 4
  %465 = fmul reassoc ninf nsz float %464, %457
  %466 = fadd reassoc ninf nsz float %444, %465
  %467 = fadd reassoc ninf nsz float %445, %457
  %468 = load ptr, ptr %38, align 8
  %469 = load i32, ptr %39, align 4
  %470 = mul i32 %469, %380
  %471 = add i32 %470, %229
  %472 = sext i32 %471 to i64
  %473 = getelementptr float, ptr %468, i64 %472
  %474 = load float, ptr %473, align 4
  %475 = fsub reassoc ninf nsz float %474, %83
  %476 = fmul reassoc ninf nsz float %475, %475
  %477 = fmul reassoc ninf nsz float %476, %27
  %478 = fsub reassoc ninf nsz float %34, %477
  %479 = tail call noundef float @expf(float noundef %478) #8
  %480 = load ptr, ptr %40, align 8
  %481 = load i32, ptr %41, align 4
  %482 = mul i32 %481, %373
  %483 = add i32 %482, %222
  %484 = sext i32 %483 to i64
  %485 = getelementptr float, ptr %480, i64 %484
  %486 = load float, ptr %485, align 4
  %487 = fmul reassoc ninf nsz float %486, %479
  %488 = fadd reassoc ninf nsz float %466, %487
  %489 = fadd reassoc ninf nsz float %467, %479
  %490 = add i32 %67, 1
  %491 = tail call i32 @llvm.smax.i32(i32 %490, i32 0)
  %492 = tail call i32 @llvm.smin.i32(i32 %30, i32 %491)
  %493 = sitofp i32 %492 to float
  %494 = fmul reassoc ninf nsz float %493, %64
  %495 = fdiv reassoc ninf nsz float %494, %28
  %496 = fadd reassoc ninf nsz float %495, 5.000000e-01
  %497 = fptosi float %496 to i32
  %498 = tail call i32 @llvm.smax.i32(i32 %497, i32 0)
  %499 = tail call i32 @llvm.smin.i32(i32 %95, i32 %498)
  %500 = load ptr, ptr %38, align 8
  %501 = load i32, ptr %39, align 4
  %502 = mul i32 %501, %499
  %503 = add i32 %502, %105
  %504 = sext i32 %503 to i64
  %505 = getelementptr float, ptr %500, i64 %504
  %506 = load float, ptr %505, align 4
  %507 = fsub reassoc ninf nsz float %506, %83
  %508 = fmul reassoc ninf nsz float %507, %507
  %509 = fmul reassoc ninf nsz float %508, %27
  %510 = fsub reassoc ninf nsz float %33, %509
  %511 = tail call noundef float @expf(float noundef %510) #8
  %512 = load ptr, ptr %40, align 8
  %513 = load i32, ptr %41, align 4
  %514 = mul i32 %513, %492
  %515 = add i32 %514, %89
  %516 = sext i32 %515 to i64
  %517 = getelementptr float, ptr %512, i64 %516
  %518 = load float, ptr %517, align 4
  %519 = fmul reassoc ninf nsz float %518, %511
  %520 = fadd reassoc ninf nsz float %488, %519
  %521 = fadd reassoc ninf nsz float %489, %511
  %522 = load ptr, ptr %38, align 8
  %523 = load i32, ptr %39, align 4
  %524 = mul i32 %523, %499
  %525 = add i32 %524, %134
  %526 = sext i32 %525 to i64
  %527 = getelementptr float, ptr %522, i64 %526
  %528 = load float, ptr %527, align 4
  %529 = fsub reassoc ninf nsz float %528, %83
  %530 = fmul reassoc ninf nsz float %529, %529
  %531 = fmul reassoc ninf nsz float %530, %27
  %532 = fsub reassoc ninf nsz float %35, %531
  %533 = tail call noundef float @expf(float noundef %532) #8
  %534 = load ptr, ptr %40, align 8
  %535 = load i32, ptr %41, align 4
  %536 = mul i32 %535, %492
  %537 = add i32 %536, %127
  %538 = sext i32 %537 to i64
  %539 = getelementptr float, ptr %534, i64 %538
  %540 = load float, ptr %539, align 4
  %541 = fmul reassoc ninf nsz float %540, %533
  %542 = fadd reassoc ninf nsz float %520, %541
  %543 = fadd reassoc ninf nsz float %521, %533
  %544 = load ptr, ptr %38, align 8
  %545 = load i32, ptr %39, align 4
  %546 = mul i32 %545, %499
  %547 = add i32 %546, %165
  %548 = sext i32 %547 to i64
  %549 = getelementptr float, ptr %544, i64 %548
  %550 = load float, ptr %549, align 4
  %551 = fsub reassoc ninf nsz float %550, %83
  %552 = fmul reassoc ninf nsz float %551, %551
  %553 = fmul reassoc ninf nsz float %552, %27
  %554 = fsub reassoc ninf nsz float %36, %553
  %555 = tail call noundef float @expf(float noundef %554) #8
  %556 = load ptr, ptr %40, align 8
  %557 = load i32, ptr %41, align 4
  %558 = mul i32 %557, %492
  %559 = add i32 %558, %158
  %560 = sext i32 %559 to i64
  %561 = getelementptr float, ptr %556, i64 %560
  %562 = load float, ptr %561, align 4
  %563 = fmul reassoc ninf nsz float %562, %555
  %564 = fadd reassoc ninf nsz float %542, %563
  %565 = fadd reassoc ninf nsz float %543, %555
  %566 = load ptr, ptr %38, align 8
  %567 = load i32, ptr %39, align 4
  %568 = mul i32 %567, %499
  %569 = add i32 %568, %197
  %570 = sext i32 %569 to i64
  %571 = getelementptr float, ptr %566, i64 %570
  %572 = load float, ptr %571, align 4
  %573 = fsub reassoc ninf nsz float %572, %83
  %574 = fmul reassoc ninf nsz float %573, %573
  %575 = fmul reassoc ninf nsz float %574, %27
  %576 = fsub reassoc ninf nsz float %35, %575
  %577 = tail call noundef float @expf(float noundef %576) #8
  %578 = load ptr, ptr %40, align 8
  %579 = load i32, ptr %41, align 4
  %580 = mul i32 %579, %492
  %581 = add i32 %580, %190
  %582 = sext i32 %581 to i64
  %583 = getelementptr float, ptr %578, i64 %582
  %584 = load float, ptr %583, align 4
  %585 = fmul reassoc ninf nsz float %584, %577
  %586 = fadd reassoc ninf nsz float %564, %585
  %587 = fadd reassoc ninf nsz float %565, %577
  %588 = load ptr, ptr %38, align 8
  %589 = load i32, ptr %39, align 4
  %590 = mul i32 %589, %499
  %591 = add i32 %590, %229
  %592 = sext i32 %591 to i64
  %593 = getelementptr float, ptr %588, i64 %592
  %594 = load float, ptr %593, align 4
  %595 = fsub reassoc ninf nsz float %594, %83
  %596 = fmul reassoc ninf nsz float %595, %595
  %597 = fmul reassoc ninf nsz float %596, %27
  %598 = fsub reassoc ninf nsz float %33, %597
  %599 = tail call noundef float @expf(float noundef %598) #8
  %600 = load ptr, ptr %40, align 8
  %601 = load i32, ptr %41, align 4
  %602 = mul i32 %601, %492
  %603 = add i32 %602, %222
  %604 = sext i32 %603 to i64
  %605 = getelementptr float, ptr %600, i64 %604
  %606 = load float, ptr %605, align 4
  %607 = fmul reassoc ninf nsz float %606, %599
  %608 = fadd reassoc ninf nsz float %586, %607
  %609 = fadd reassoc ninf nsz float %587, %599
  %610 = add i32 %67, 2
  %611 = tail call i32 @llvm.smax.i32(i32 %610, i32 0)
  %612 = tail call i32 @llvm.smin.i32(i32 %30, i32 %611)
  %613 = sitofp i32 %612 to float
  %614 = fmul reassoc ninf nsz float %613, %64
  %615 = fdiv reassoc ninf nsz float %614, %28
  %616 = fadd reassoc ninf nsz float %615, 5.000000e-01
  %617 = fptosi float %616 to i32
  %618 = tail call i32 @llvm.smax.i32(i32 %617, i32 0)
  %619 = tail call i32 @llvm.smin.i32(i32 %95, i32 %618)
  %620 = load ptr, ptr %38, align 8
  %621 = load i32, ptr %39, align 4
  %622 = mul i32 %621, %619
  %623 = add i32 %622, %105
  %624 = sext i32 %623 to i64
  %625 = getelementptr float, ptr %620, i64 %624
  %626 = load float, ptr %625, align 4
  %627 = fsub reassoc ninf nsz float %626, %83
  %628 = fmul reassoc ninf nsz float %627, %627
  %629 = fmul reassoc ninf nsz float %628, %27
  %630 = fsub reassoc ninf nsz float %32, %629
  %631 = tail call noundef float @expf(float noundef %630) #8
  %632 = load ptr, ptr %40, align 8
  %633 = load i32, ptr %41, align 4
  %634 = mul i32 %633, %612
  %635 = add i32 %634, %89
  %636 = sext i32 %635 to i64
  %637 = getelementptr float, ptr %632, i64 %636
  %638 = load float, ptr %637, align 4
  %639 = fmul reassoc ninf nsz float %638, %631
  %640 = fadd reassoc ninf nsz float %608, %639
  %641 = fadd reassoc ninf nsz float %609, %631
  %642 = load ptr, ptr %38, align 8
  %643 = load i32, ptr %39, align 4
  %644 = mul i32 %643, %619
  %645 = add i32 %644, %134
  %646 = sext i32 %645 to i64
  %647 = getelementptr float, ptr %642, i64 %646
  %648 = load float, ptr %647, align 4
  %649 = fsub reassoc ninf nsz float %648, %83
  %650 = fmul reassoc ninf nsz float %649, %649
  %651 = fmul reassoc ninf nsz float %650, %27
  %652 = fsub reassoc ninf nsz float %33, %651
  %653 = tail call noundef float @expf(float noundef %652) #8
  %654 = load ptr, ptr %40, align 8
  %655 = load i32, ptr %41, align 4
  %656 = mul i32 %655, %612
  %657 = add i32 %656, %127
  %658 = sext i32 %657 to i64
  %659 = getelementptr float, ptr %654, i64 %658
  %660 = load float, ptr %659, align 4
  %661 = fmul reassoc ninf nsz float %660, %653
  %662 = fadd reassoc ninf nsz float %640, %661
  %663 = fadd reassoc ninf nsz float %641, %653
  %664 = load ptr, ptr %38, align 8
  %665 = load i32, ptr %39, align 4
  %666 = mul i32 %665, %619
  %667 = add i32 %666, %165
  %668 = sext i32 %667 to i64
  %669 = getelementptr float, ptr %664, i64 %668
  %670 = load float, ptr %669, align 4
  %671 = fsub reassoc ninf nsz float %670, %83
  %672 = fmul reassoc ninf nsz float %671, %671
  %673 = fmul reassoc ninf nsz float %672, %27
  %674 = fsub reassoc ninf nsz float %34, %673
  %675 = tail call noundef float @expf(float noundef %674) #8
  %676 = load ptr, ptr %40, align 8
  %677 = load i32, ptr %41, align 4
  %678 = mul i32 %677, %612
  %679 = add i32 %678, %158
  %680 = sext i32 %679 to i64
  %681 = getelementptr float, ptr %676, i64 %680
  %682 = load float, ptr %681, align 4
  %683 = fmul reassoc ninf nsz float %682, %675
  %684 = fadd reassoc ninf nsz float %662, %683
  %685 = fadd reassoc ninf nsz float %663, %675
  %686 = load ptr, ptr %38, align 8
  %687 = load i32, ptr %39, align 4
  %688 = mul i32 %687, %619
  %689 = add i32 %688, %197
  %690 = sext i32 %689 to i64
  %691 = getelementptr float, ptr %686, i64 %690
  %692 = load float, ptr %691, align 4
  %693 = fsub reassoc ninf nsz float %692, %83
  %694 = fmul reassoc ninf nsz float %693, %693
  %695 = fmul reassoc ninf nsz float %694, %27
  %696 = fsub reassoc ninf nsz float %33, %695
  %697 = tail call noundef float @expf(float noundef %696) #8
  %698 = load ptr, ptr %40, align 8
  %699 = load i32, ptr %41, align 4
  %700 = mul i32 %699, %612
  %701 = add i32 %700, %190
  %702 = sext i32 %701 to i64
  %703 = getelementptr float, ptr %698, i64 %702
  %704 = load float, ptr %703, align 4
  %705 = fmul reassoc ninf nsz float %704, %697
  %706 = fadd reassoc ninf nsz float %684, %705
  %707 = fadd reassoc ninf nsz float %685, %697
  %708 = load ptr, ptr %38, align 8
  %709 = load i32, ptr %39, align 4
  %710 = mul i32 %709, %619
  %711 = add i32 %710, %229
  %712 = sext i32 %711 to i64
  %713 = getelementptr float, ptr %708, i64 %712
  %714 = load float, ptr %713, align 4
  %715 = fsub reassoc ninf nsz float %714, %83
  %716 = fmul reassoc ninf nsz float %715, %715
  %717 = fmul reassoc ninf nsz float %716, %27
  %718 = fsub reassoc ninf nsz float %32, %717
  %719 = tail call noundef float @expf(float noundef %718) #8
  %720 = load ptr, ptr %40, align 8
  %721 = load i32, ptr %41, align 4
  %722 = mul i32 %721, %612
  %723 = add i32 %722, %222
  %724 = sext i32 %723 to i64
  %725 = getelementptr float, ptr %720, i64 %724
  %726 = load float, ptr %725, align 4
  %727 = fmul reassoc ninf nsz float %726, %719
  %728 = fadd reassoc ninf nsz float %706, %727
  %729 = fadd reassoc ninf nsz float %707, %719
  %730 = fdiv reassoc ninf nsz float %728, %729
  %731 = load ptr, ptr %43, align 8
  %732 = load i32, ptr %44, align 4
  %733 = sub i32 %732, %49
  %734 = mul i32 %733, %56
  %735 = add i32 %.05, %734
  %736 = sext i32 %735 to i64
  %737 = getelementptr float, ptr %731, i64 %736
  store float %730, ptr %737, align 4
  %738 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %18, %738
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.17, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nounwind }

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
