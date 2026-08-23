; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.9 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bicubic_resize_offset_kernel_vec3_c154_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 16
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 20
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

define void @_bicubic_resize_offset_kernel_vec3_c154_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 48
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 52
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 32
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 40
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 36
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 44
  %31 = load i32, ptr %30, align 4
  %32 = sitofp i32 %25 to float
  %33 = sitofp i32 %27 to float
  %34 = sitofp i32 %29 to float
  %35 = sitofp i32 %31 to float
  %36 = add i32 %25, -1
  %37 = add i32 %29, -1
  %38 = icmp slt i32 %16, %18
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr i8, ptr %19, i64 8
  %40 = getelementptr i8, ptr %19, i64 4
  %41 = getelementptr i8, ptr %19, i64 24
  %42 = getelementptr i8, ptr %19, i64 20
  %43 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %43, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.011 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %500, %for_loop_body ]
  %44 = load ptr, ptr %3, align 8
  %45 = getelementptr inbounds nuw i8, ptr %44, i64 32872
  %46 = load ptr, ptr %45, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 4
  %48 = load i32, ptr %47, align 4
  %49 = sdiv i32 %.011, %48
  %50 = mul i32 %49, %48
  %51 = xor i32 %48, %.011
  %52 = icmp slt i32 %51, 0
  %53 = icmp ne i32 %.011, %50
  %54 = and i1 %52, %53
  %.neg4 = sext i1 %54 to i32
  %55 = add i32 %49, %.neg4
  %56 = add i32 %55, %21
  %57 = mul i32 %48, -1
  %58 = mul i32 %57, %55
  %59 = add i32 %23, %.011
  %60 = add i32 %59, %58
  %61 = sitofp i32 %56 to float
  %62 = fadd reassoc ninf nsz float %61, 5.000000e-01
  %63 = fmul reassoc ninf nsz float %62, %32
  %64 = fdiv reassoc ninf nsz float %63, %33
  %65 = fadd reassoc ninf nsz float %64, -5.000000e-01
  %66 = sitofp i32 %60 to float
  %67 = fadd reassoc ninf nsz float %66, 5.000000e-01
  %68 = fmul reassoc ninf nsz float %67, %34
  %69 = fdiv reassoc ninf nsz float %68, %35
  %70 = fadd reassoc ninf nsz float %69, -5.000000e-01
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %72 = fptosi float %71 to i32
  %73 = tail call reassoc ninf nsz float @llvm.floor.f32(float %65)
  %74 = fptosi float %73 to i32
  %75 = sitofp i32 %72 to float
  %76 = fsub reassoc ninf nsz float %70, %75
  %77 = tail call noundef float @llvm.fabs.f32(float %76)
  %78 = fadd reassoc ninf nsz float %77, 1.000000e+00
  %79 = fmul reassoc ninf nsz float %78, %78
  %80 = fmul reassoc ninf nsz float %78, 7.500000e-01
  %81 = fmul reassoc ninf nsz float %78, -6.000000e+00
  %82 = fsub reassoc ninf nsz float 3.750000e+00, %80
  %reass.mul = fmul reassoc ninf nsz float %79, %82
  %83 = fadd reassoc ninf nsz float %81, 3.000000e+00
  %84 = fadd reassoc ninf nsz float %83, %reass.mul
  %85 = fmul reassoc ninf nsz float %76, %76
  %86 = fmul reassoc ninf nsz float %85, 1.250000e+00
  %87 = fmul reassoc ninf nsz float %86, %77
  %88 = fmul reassoc ninf nsz float %85, 2.250000e+00
  %89 = fsub reassoc ninf nsz float %87, %88
  %90 = fadd reassoc ninf nsz float %89, 1.000000e+00
  %91 = fsub reassoc ninf nsz float 1.000000e+00, %77
  %92 = fmul reassoc ninf nsz float %91, %91
  %93 = fmul reassoc ninf nsz float %91, 1.250000e+00
  %94 = fadd reassoc ninf nsz float %93, -2.250000e+00
  %95 = fmul reassoc ninf nsz float %94, %92
  %96 = fadd reassoc ninf nsz float %95, 1.000000e+00
  %97 = fsub reassoc ninf nsz float 2.000000e+00, %77
  %98 = fmul reassoc ninf nsz float %97, %97
  %99 = fmul reassoc ninf nsz float %97, 7.500000e-01
  %100 = fmul reassoc ninf nsz float %97, -6.000000e+00
  %101 = fsub reassoc ninf nsz float 3.750000e+00, %99
  %reass.mul6 = fmul reassoc ninf nsz float %98, %101
  %102 = fadd reassoc ninf nsz float %100, 3.000000e+00
  %103 = fadd reassoc ninf nsz float %102, %reass.mul6
  %104 = sitofp i32 %74 to float
  %105 = fsub reassoc ninf nsz float %65, %104
  %106 = tail call noundef float @llvm.fabs.f32(float %105)
  %107 = fadd reassoc ninf nsz float %106, 1.000000e+00
  %108 = fmul reassoc ninf nsz float %107, %107
  %109 = fmul reassoc ninf nsz float %107, 7.500000e-01
  %110 = fmul reassoc ninf nsz float %107, -6.000000e+00
  %111 = fsub reassoc ninf nsz float 3.750000e+00, %109
  %reass.mul8 = fmul reassoc ninf nsz float %108, %111
  %112 = fadd reassoc ninf nsz float %110, 3.000000e+00
  %113 = fadd reassoc ninf nsz float %112, %reass.mul8
  %114 = fmul reassoc ninf nsz float %105, %105
  %115 = fmul reassoc ninf nsz float %114, 1.250000e+00
  %116 = fmul reassoc ninf nsz float %115, %106
  %117 = fmul reassoc ninf nsz float %114, 2.250000e+00
  %118 = fsub reassoc ninf nsz float %116, %117
  %119 = fadd reassoc ninf nsz float %118, 1.000000e+00
  %120 = fsub reassoc ninf nsz float 1.000000e+00, %106
  %121 = fmul reassoc ninf nsz float %120, %120
  %122 = fmul reassoc ninf nsz float %120, 1.250000e+00
  %123 = fadd reassoc ninf nsz float %122, -2.250000e+00
  %124 = fmul reassoc ninf nsz float %123, %121
  %125 = fadd reassoc ninf nsz float %124, 1.000000e+00
  %126 = fsub reassoc ninf nsz float 2.000000e+00, %106
  %127 = fmul reassoc ninf nsz float %126, %126
  %128 = fmul reassoc ninf nsz float %126, 7.500000e-01
  %129 = fmul reassoc ninf nsz float %126, -6.000000e+00
  %130 = fsub reassoc ninf nsz float 3.750000e+00, %128
  %reass.mul10 = fmul reassoc ninf nsz float %127, %130
  %131 = fadd reassoc ninf nsz float %129, 3.000000e+00
  %132 = fadd reassoc ninf nsz float %131, %reass.mul10
  %133 = add i32 %74, -1
  %134 = tail call i32 @llvm.smax.i32(i32 %133, i32 0)
  %135 = tail call i32 @llvm.smin.i32(i32 %36, i32 %134)
  %136 = add i32 %72, -1
  %137 = tail call i32 @llvm.smax.i32(i32 %136, i32 0)
  %138 = tail call i32 @llvm.smin.i32(i32 %37, i32 %137)
  %139 = load ptr, ptr %39, align 8
  %140 = load i32, ptr %40, align 4
  %141 = mul i32 %135, %140
  %142 = add i32 %138, %141
  %143 = mul i32 %142, 3
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %139, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %143, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %139, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = add i32 %143, 2
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %139, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = fmul reassoc ninf nsz float %84, %146
  %156 = fmul reassoc ninf nsz float %84, %150
  %157 = fmul reassoc ninf nsz float %84, %154
  %158 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %159 = tail call i32 @llvm.smin.i32(i32 %37, i32 %158)
  %160 = add i32 %141, %159
  %161 = mul i32 %160, 3
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, ptr %139, i64 %162
  %164 = load float, ptr %163, align 4
  %165 = add i32 %161, 1
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %139, i64 %166
  %168 = load float, ptr %167, align 4
  %169 = add i32 %161, 2
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, ptr %139, i64 %170
  %172 = load float, ptr %171, align 4
  %173 = fmul reassoc ninf nsz float %90, %164
  %174 = fmul reassoc ninf nsz float %90, %168
  %175 = fmul reassoc ninf nsz float %90, %172
  %176 = add i32 %72, 1
  %177 = tail call i32 @llvm.smax.i32(i32 %176, i32 0)
  %178 = tail call i32 @llvm.smin.i32(i32 %37, i32 %177)
  %179 = add i32 %178, %141
  %180 = mul i32 %179, 3
  %181 = sext i32 %180 to i64
  %182 = getelementptr float, ptr %139, i64 %181
  %183 = load float, ptr %182, align 4
  %184 = add i32 %180, 1
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, ptr %139, i64 %185
  %187 = load float, ptr %186, align 4
  %188 = add i32 %180, 2
  %189 = sext i32 %188 to i64
  %190 = getelementptr float, ptr %139, i64 %189
  %191 = load float, ptr %190, align 4
  %192 = fmul reassoc ninf nsz float %96, %183
  %193 = fmul reassoc ninf nsz float %96, %187
  %194 = fmul reassoc ninf nsz float %96, %191
  %195 = add i32 %72, 2
  %196 = tail call i32 @llvm.smax.i32(i32 %195, i32 0)
  %197 = tail call i32 @llvm.smin.i32(i32 %37, i32 %196)
  %198 = add i32 %197, %141
  %199 = mul i32 %198, 3
  %200 = sext i32 %199 to i64
  %201 = getelementptr float, ptr %139, i64 %200
  %202 = load float, ptr %201, align 4
  %203 = add i32 %199, 1
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, ptr %139, i64 %204
  %206 = load float, ptr %205, align 4
  %207 = add i32 %199, 2
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %139, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = fmul reassoc ninf nsz float %103, %202
  %212 = fmul reassoc ninf nsz float %103, %206
  %213 = fmul reassoc ninf nsz float %103, %210
  %214 = fadd reassoc ninf nsz float %192, %173
  %215 = fadd reassoc ninf nsz float %214, %155
  %216 = fadd reassoc ninf nsz float %215, %211
  %217 = fadd reassoc ninf nsz float %193, %174
  %218 = fadd reassoc ninf nsz float %217, %156
  %219 = fadd reassoc ninf nsz float %218, %212
  %220 = fadd reassoc ninf nsz float %194, %175
  %221 = fadd reassoc ninf nsz float %220, %157
  %222 = fadd reassoc ninf nsz float %221, %213
  %223 = fmul reassoc ninf nsz float %216, %113
  %224 = fmul reassoc ninf nsz float %219, %113
  %225 = fmul reassoc ninf nsz float %222, %113
  %226 = tail call i32 @llvm.smax.i32(i32 %74, i32 0)
  %227 = tail call i32 @llvm.smin.i32(i32 %36, i32 %226)
  %228 = mul i32 %227, %140
  %229 = add i32 %138, %228
  %230 = mul i32 %229, 3
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, ptr %139, i64 %231
  %233 = load float, ptr %232, align 4
  %234 = add i32 %230, 1
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %139, i64 %235
  %237 = load float, ptr %236, align 4
  %238 = add i32 %230, 2
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, ptr %139, i64 %239
  %241 = load float, ptr %240, align 4
  %242 = fmul reassoc ninf nsz float %84, %233
  %243 = fmul reassoc ninf nsz float %84, %237
  %244 = fmul reassoc ninf nsz float %84, %241
  %245 = add i32 %159, %228
  %246 = mul i32 %245, 3
  %247 = sext i32 %246 to i64
  %248 = getelementptr float, ptr %139, i64 %247
  %249 = load float, ptr %248, align 4
  %250 = add i32 %246, 1
  %251 = sext i32 %250 to i64
  %252 = getelementptr float, ptr %139, i64 %251
  %253 = load float, ptr %252, align 4
  %254 = add i32 %246, 2
  %255 = sext i32 %254 to i64
  %256 = getelementptr float, ptr %139, i64 %255
  %257 = load float, ptr %256, align 4
  %258 = fmul reassoc ninf nsz float %90, %249
  %259 = fmul reassoc ninf nsz float %90, %253
  %260 = fmul reassoc ninf nsz float %90, %257
  %261 = add i32 %178, %228
  %262 = mul i32 %261, 3
  %263 = sext i32 %262 to i64
  %264 = getelementptr float, ptr %139, i64 %263
  %265 = load float, ptr %264, align 4
  %266 = add i32 %262, 1
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, ptr %139, i64 %267
  %269 = load float, ptr %268, align 4
  %270 = add i32 %262, 2
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %139, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = fmul reassoc ninf nsz float %96, %265
  %275 = fmul reassoc ninf nsz float %96, %269
  %276 = fmul reassoc ninf nsz float %273, %96
  %277 = add i32 %197, %228
  %278 = mul i32 %277, 3
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, ptr %139, i64 %279
  %281 = load float, ptr %280, align 4
  %282 = add i32 %278, 1
  %283 = sext i32 %282 to i64
  %284 = getelementptr float, ptr %139, i64 %283
  %285 = load float, ptr %284, align 4
  %286 = add i32 %278, 2
  %287 = sext i32 %286 to i64
  %288 = getelementptr float, ptr %139, i64 %287
  %289 = load float, ptr %288, align 4
  %290 = fmul reassoc ninf nsz float %281, %103
  %291 = fmul reassoc ninf nsz float %285, %103
  %292 = fmul reassoc ninf nsz float %289, %103
  %293 = fadd reassoc ninf nsz float %274, %258
  %294 = fadd reassoc ninf nsz float %293, %242
  %295 = fadd reassoc ninf nsz float %294, %290
  %296 = fadd reassoc ninf nsz float %275, %259
  %297 = fadd reassoc ninf nsz float %296, %243
  %298 = fadd reassoc ninf nsz float %297, %291
  %299 = fadd reassoc ninf nsz float %276, %260
  %300 = fadd reassoc ninf nsz float %299, %244
  %301 = fadd reassoc ninf nsz float %300, %292
  %302 = fmul reassoc ninf nsz float %295, %119
  %303 = fmul reassoc ninf nsz float %298, %119
  %304 = fmul reassoc ninf nsz float %301, %119
  %305 = fadd reassoc ninf nsz float %223, %302
  %306 = fadd reassoc ninf nsz float %224, %303
  %307 = fadd reassoc ninf nsz float %225, %304
  %308 = add i32 %74, 1
  %309 = tail call i32 @llvm.smax.i32(i32 %308, i32 0)
  %310 = tail call i32 @llvm.smin.i32(i32 %36, i32 %309)
  %311 = mul i32 %310, %140
  %312 = add i32 %138, %311
  %313 = mul i32 %312, 3
  %314 = sext i32 %313 to i64
  %315 = getelementptr float, ptr %139, i64 %314
  %316 = load float, ptr %315, align 4
  %317 = add i32 %313, 1
  %318 = sext i32 %317 to i64
  %319 = getelementptr float, ptr %139, i64 %318
  %320 = load float, ptr %319, align 4
  %321 = add i32 %313, 2
  %322 = sext i32 %321 to i64
  %323 = getelementptr float, ptr %139, i64 %322
  %324 = load float, ptr %323, align 4
  %325 = fmul reassoc ninf nsz float %316, %84
  %326 = fmul reassoc ninf nsz float %320, %84
  %327 = fmul reassoc ninf nsz float %324, %84
  %328 = add i32 %311, %159
  %329 = mul i32 %328, 3
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, ptr %139, i64 %330
  %332 = load float, ptr %331, align 4
  %333 = add i32 %329, 1
  %334 = sext i32 %333 to i64
  %335 = getelementptr float, ptr %139, i64 %334
  %336 = load float, ptr %335, align 4
  %337 = add i32 %329, 2
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, ptr %139, i64 %338
  %340 = load float, ptr %339, align 4
  %341 = fmul reassoc ninf nsz float %332, %90
  %342 = fmul reassoc ninf nsz float %336, %90
  %343 = fmul reassoc ninf nsz float %340, %90
  %344 = fadd reassoc ninf nsz float %341, %325
  %345 = fadd reassoc ninf nsz float %342, %326
  %346 = fadd reassoc ninf nsz float %343, %327
  %347 = add i32 %178, %311
  %348 = mul i32 %347, 3
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, ptr %139, i64 %349
  %351 = load float, ptr %350, align 4
  %352 = add i32 %348, 1
  %353 = sext i32 %352 to i64
  %354 = getelementptr float, ptr %139, i64 %353
  %355 = load float, ptr %354, align 4
  %356 = add i32 %348, 2
  %357 = sext i32 %356 to i64
  %358 = getelementptr float, ptr %139, i64 %357
  %359 = load float, ptr %358, align 4
  %360 = fmul reassoc ninf nsz float %351, %96
  %361 = fmul reassoc ninf nsz float %355, %96
  %362 = fmul reassoc ninf nsz float %359, %96
  %363 = fadd reassoc ninf nsz float %344, %360
  %364 = fadd reassoc ninf nsz float %345, %361
  %365 = fadd reassoc ninf nsz float %346, %362
  %366 = add i32 %197, %311
  %367 = mul i32 %366, 3
  %368 = sext i32 %367 to i64
  %369 = getelementptr float, ptr %139, i64 %368
  %370 = load float, ptr %369, align 4
  %371 = add i32 %367, 1
  %372 = sext i32 %371 to i64
  %373 = getelementptr float, ptr %139, i64 %372
  %374 = load float, ptr %373, align 4
  %375 = add i32 %367, 2
  %376 = sext i32 %375 to i64
  %377 = getelementptr float, ptr %139, i64 %376
  %378 = load float, ptr %377, align 4
  %379 = fmul reassoc ninf nsz float %370, %103
  %380 = fmul reassoc ninf nsz float %374, %103
  %381 = fmul reassoc ninf nsz float %378, %103
  %382 = fadd reassoc ninf nsz float %363, %379
  %383 = fadd reassoc ninf nsz float %364, %380
  %384 = fadd reassoc ninf nsz float %365, %381
  %385 = fmul reassoc ninf nsz float %382, %125
  %386 = fmul reassoc ninf nsz float %383, %125
  %387 = fmul reassoc ninf nsz float %384, %125
  %388 = fadd reassoc ninf nsz float %305, %385
  %389 = fadd reassoc ninf nsz float %306, %386
  %390 = fadd reassoc ninf nsz float %307, %387
  %391 = add i32 %74, 2
  %392 = tail call i32 @llvm.smax.i32(i32 %391, i32 0)
  %393 = tail call i32 @llvm.smin.i32(i32 %36, i32 %392)
  %394 = mul i32 %393, %140
  %395 = add i32 %138, %394
  %396 = mul i32 %395, 3
  %397 = sext i32 %396 to i64
  %398 = getelementptr float, ptr %139, i64 %397
  %399 = load float, ptr %398, align 4
  %400 = add i32 %396, 1
  %401 = sext i32 %400 to i64
  %402 = getelementptr float, ptr %139, i64 %401
  %403 = load float, ptr %402, align 4
  %404 = add i32 %396, 2
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, ptr %139, i64 %405
  %407 = load float, ptr %406, align 4
  %408 = fmul reassoc ninf nsz float %399, %84
  %409 = fmul reassoc ninf nsz float %403, %84
  %410 = fmul reassoc ninf nsz float %407, %84
  %411 = add i32 %394, %159
  %412 = mul i32 %411, 3
  %413 = sext i32 %412 to i64
  %414 = getelementptr float, ptr %139, i64 %413
  %415 = load float, ptr %414, align 4
  %416 = add i32 %412, 1
  %417 = sext i32 %416 to i64
  %418 = getelementptr float, ptr %139, i64 %417
  %419 = load float, ptr %418, align 4
  %420 = add i32 %412, 2
  %421 = sext i32 %420 to i64
  %422 = getelementptr float, ptr %139, i64 %421
  %423 = load float, ptr %422, align 4
  %424 = fmul reassoc ninf nsz float %415, %90
  %425 = fmul reassoc ninf nsz float %419, %90
  %426 = fmul reassoc ninf nsz float %423, %90
  %427 = fadd reassoc ninf nsz float %424, %408
  %428 = fadd reassoc ninf nsz float %425, %409
  %429 = fadd reassoc ninf nsz float %426, %410
  %430 = add i32 %178, %394
  %431 = mul i32 %430, 3
  %432 = sext i32 %431 to i64
  %433 = getelementptr float, ptr %139, i64 %432
  %434 = load float, ptr %433, align 4
  %435 = add i32 %431, 1
  %436 = sext i32 %435 to i64
  %437 = getelementptr float, ptr %139, i64 %436
  %438 = load float, ptr %437, align 4
  %439 = add i32 %431, 2
  %440 = sext i32 %439 to i64
  %441 = getelementptr float, ptr %139, i64 %440
  %442 = load float, ptr %441, align 4
  %443 = fmul reassoc ninf nsz float %434, %96
  %444 = fmul reassoc ninf nsz float %438, %96
  %445 = fmul reassoc ninf nsz float %442, %96
  %446 = fadd reassoc ninf nsz float %427, %443
  %447 = fadd reassoc ninf nsz float %428, %444
  %448 = fadd reassoc ninf nsz float %429, %445
  %449 = add i32 %197, %394
  %450 = mul i32 %449, 3
  %451 = sext i32 %450 to i64
  %452 = getelementptr float, ptr %139, i64 %451
  %453 = load float, ptr %452, align 4
  %454 = add i32 %450, 1
  %455 = sext i32 %454 to i64
  %456 = getelementptr float, ptr %139, i64 %455
  %457 = load float, ptr %456, align 4
  %458 = add i32 %450, 2
  %459 = sext i32 %458 to i64
  %460 = getelementptr float, ptr %139, i64 %459
  %461 = load float, ptr %460, align 4
  %462 = fmul reassoc ninf nsz float %453, %103
  %463 = fmul reassoc ninf nsz float %457, %103
  %464 = fmul reassoc ninf nsz float %461, %103
  %465 = fadd reassoc ninf nsz float %446, %462
  %466 = fadd reassoc ninf nsz float %447, %463
  %467 = fadd reassoc ninf nsz float %448, %464
  %468 = fmul reassoc ninf nsz float %465, %132
  %469 = fmul reassoc ninf nsz float %466, %132
  %470 = fmul reassoc ninf nsz float %467, %132
  %471 = fadd reassoc ninf nsz float %388, %468
  %472 = fadd reassoc ninf nsz float %389, %469
  %473 = fadd reassoc ninf nsz float %390, %470
  %474 = load ptr, ptr %41, align 8
  %475 = load i32, ptr %42, align 4
  %476 = sub i32 %475, %48
  %477 = mul i32 %476, 3
  %478 = mul i32 %477, %55
  %479 = add i32 %lsr.iv, %478
  %480 = sext i32 %479 to i64
  %481 = getelementptr float, ptr %474, i64 %480
  store float %471, ptr %481, align 4
  %482 = load ptr, ptr %41, align 8
  %483 = load i32, ptr %42, align 4
  %484 = sub i32 %483, %48
  %485 = mul i32 %484, 3
  %486 = mul i32 %485, %55
  %487 = add i32 %lsr.iv, %486
  %488 = add i32 %487, 1
  %489 = sext i32 %488 to i64
  %490 = getelementptr float, ptr %482, i64 %489
  store float %472, ptr %490, align 4
  %491 = load ptr, ptr %41, align 8
  %492 = load i32, ptr %42, align 4
  %493 = sub i32 %492, %48
  %494 = mul i32 %493, 3
  %495 = mul i32 %494, %55
  %496 = add i32 %lsr.iv, %495
  %497 = add i32 %496, 2
  %498 = sext i32 %497 to i64
  %499 = getelementptr float, ptr %491, i64 %498
  store float %473, ptr %499, align 4
  %500 = add nsw i32 %.011, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %500
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.9, align 8
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
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
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
