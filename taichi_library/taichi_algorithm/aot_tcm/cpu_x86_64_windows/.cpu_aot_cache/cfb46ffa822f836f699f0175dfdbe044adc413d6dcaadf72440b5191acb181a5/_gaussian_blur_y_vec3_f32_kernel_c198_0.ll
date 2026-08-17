; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.9 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gaussian_blur_y_vec3_f32_kernel_c198_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 12
  store i32 %2, ptr %7, align 4
  %8 = load ptr, ptr %context, align 8
  %9 = getelementptr i8, ptr %8, i64 36
  %10 = load i32, ptr %9, align 4
  %11 = getelementptr i8, ptr %8, i64 56
  %12 = load i32, ptr %11, align 4
  %13 = load ptr, ptr %3, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 8
  store i32 %12, ptr %16, align 4
  %17 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %18 = tail call i32 @llvm.smax.i32(i32 %10, i32 0)
  %19 = load ptr, ptr %3, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 32872
  %21 = load ptr, ptr %20, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 4
  store i32 %18, ptr %22, align 4
  %23 = mul i32 %18, %17
  %24 = load ptr, ptr %3, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 32872
  %26 = load ptr, ptr %25, align 8
  store i32 %23, ptr %26, align 4
  ret void
}

define void @_gaussian_blur_y_vec3_f32_kernel_c198_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = load ptr, ptr %20, align 8
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 8
  %24 = getelementptr i8, ptr %19, i64 4
  %25 = getelementptr i8, ptr %19, i64 24
  %26 = getelementptr i8, ptr %19, i64 20
  %27 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %27, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if45 ]
  %.0115199 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %1033, %after_if45 ]
  %28 = load ptr, ptr %3, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 32872
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 4
  %32 = load i32, ptr %31, align 4
  %33 = sdiv i32 %.0115199, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.0115199
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.0115199, %34
  %38 = and i1 %36, %37
  %.neg116 = sext i1 %38 to i32
  %39 = add i32 %33, %.neg116
  %40 = mul i32 %39, %32
  %41 = load float, ptr %21, align 4
  %42 = load ptr, ptr %23, align 8
  %43 = load i32, ptr %24, align 4
  %44 = sub i32 %43, %32
  %45 = mul i32 %44, 3
  %46 = mul i32 %45, %39
  %47 = add i32 %lsr.iv, %46
  %48 = sext i32 %47 to i64
  %49 = getelementptr float, ptr %42, i64 %48
  %50 = load float, ptr %49, align 4
  %51 = add i32 %47, 1
  %52 = sext i32 %51 to i64
  %53 = getelementptr float, ptr %42, i64 %52
  %54 = load float, ptr %53, align 4
  %55 = add i32 %47, 2
  %56 = sext i32 %55 to i64
  %57 = getelementptr float, ptr %42, i64 %56
  %58 = load float, ptr %57, align 4
  %59 = fmul reassoc ninf nsz float %50, %41
  %60 = fmul reassoc ninf nsz float %54, %41
  %61 = fmul reassoc ninf nsz float %58, %41
  %62 = getelementptr inbounds nuw i8, ptr %30, i64 8
  %63 = load i32, ptr %62, align 4
  %64 = icmp sgt i32 %63, 0
  br i1 %64, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %65 = load ptr, ptr %20, align 8
  %66 = getelementptr i8, ptr %65, i64 4
  %67 = load float, ptr %66, align 4
  %68 = add i32 %39, -1
  %69 = tail call i32 @llvm.abs.i32(i32 %68, i1 true)
  %70 = getelementptr inbounds nuw i8, ptr %30, i64 12
  %71 = load i32, ptr %70, align 4
  %72 = add i32 %71, -1
  %73 = sub i32 %69, %72
  %74 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %75 = shl nuw i32 %74, 1
  %76 = sub i32 %69, %75
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %72, i32 %77)
  %79 = add i32 %39, 1
  %80 = tail call i32 @llvm.abs.i32(i32 %79, i1 true)
  %81 = sub i32 %80, %72
  %82 = tail call i32 @llvm.smax.i32(i32 %81, i32 0)
  %83 = shl nuw i32 %82, 1
  %84 = sub i32 %80, %83
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %86 = tail call i32 @llvm.smin.i32(i32 %72, i32 %85)
  %87 = mul i32 %78, %43
  %88 = sub i32 %87, %40
  %89 = add i32 %.0115199, %88
  %90 = mul i32 %89, 3
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %42, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = add i32 %90, 1
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, ptr %42, i64 %95
  %97 = load float, ptr %96, align 4
  %98 = add i32 %90, 2
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %42, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = mul i32 %86, %43
  %103 = sub i32 %102, %40
  %104 = add i32 %.0115199, %103
  %105 = mul i32 %104, 3
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %42, i64 %106
  %108 = load float, ptr %107, align 4
  %109 = add i32 %105, 1
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %42, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = add i32 %105, 2
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, ptr %42, i64 %114
  %116 = load float, ptr %115, align 4
  %117 = fadd reassoc ninf nsz float %108, %93
  %118 = fadd reassoc ninf nsz float %112, %97
  %119 = fadd reassoc ninf nsz float %116, %101
  %120 = fmul reassoc ninf nsz float %117, %67
  %121 = fmul reassoc ninf nsz float %118, %67
  %122 = fmul reassoc ninf nsz float %119, %67
  %123 = fadd reassoc ninf nsz float %120, %59
  %124 = fadd reassoc ninf nsz float %121, %60
  %125 = fadd reassoc ninf nsz float %122, %61
  %factor = fmul reassoc ninf nsz float %67, 2.000000e+00
  %126 = fadd reassoc ninf nsz float %factor, %41
  %.not = icmp eq i32 %63, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %127 = getelementptr i8, ptr %65, i64 8
  %128 = load float, ptr %127, align 4
  %129 = add i32 %39, -2
  %130 = tail call i32 @llvm.abs.i32(i32 %129, i1 true)
  %131 = sub i32 %130, %72
  %132 = tail call i32 @llvm.smax.i32(i32 %131, i32 0)
  %133 = shl nuw i32 %132, 1
  %134 = sub i32 %130, %133
  %135 = tail call i32 @llvm.smax.i32(i32 %134, i32 0)
  %136 = tail call i32 @llvm.smin.i32(i32 %72, i32 %135)
  %137 = add i32 %39, 2
  %138 = tail call i32 @llvm.abs.i32(i32 %137, i1 true)
  %139 = sub i32 %138, %72
  %140 = tail call i32 @llvm.smax.i32(i32 %139, i32 0)
  %141 = shl nuw i32 %140, 1
  %142 = sub i32 %138, %141
  %143 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %144 = tail call i32 @llvm.smin.i32(i32 %72, i32 %143)
  %145 = mul i32 %136, %43
  %146 = sub i32 %145, %40
  %147 = add i32 %.0115199, %146
  %148 = mul i32 %147, 3
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %42, i64 %149
  %151 = load float, ptr %150, align 4
  %152 = add i32 %148, 1
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %42, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = add i32 %148, 2
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %42, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = mul i32 %144, %43
  %161 = sub i32 %160, %40
  %162 = add i32 %.0115199, %161
  %163 = mul i32 %162, 3
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %42, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = add i32 %163, 1
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, ptr %42, i64 %168
  %170 = load float, ptr %169, align 4
  %171 = add i32 %163, 2
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %42, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = fadd reassoc ninf nsz float %166, %151
  %176 = fadd reassoc ninf nsz float %170, %155
  %177 = fadd reassoc ninf nsz float %174, %159
  %178 = fmul reassoc ninf nsz float %175, %128
  %179 = fmul reassoc ninf nsz float %176, %128
  %180 = fmul reassoc ninf nsz float %177, %128
  %181 = fadd reassoc ninf nsz float %178, %123
  %182 = fadd reassoc ninf nsz float %179, %124
  %183 = fadd reassoc ninf nsz float %180, %125
  %factor184 = fmul reassoc ninf nsz float %128, 2.000000e+00
  %184 = fadd reassoc ninf nsz float %factor184, %126
  %185 = icmp samesign ugt i32 %63, 2
  br i1 %185, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %186 = getelementptr i8, ptr %65, i64 12
  %187 = load float, ptr %186, align 4
  %188 = add i32 %39, -3
  %189 = tail call i32 @llvm.abs.i32(i32 %188, i1 true)
  %190 = sub i32 %189, %72
  %191 = tail call i32 @llvm.smax.i32(i32 %190, i32 0)
  %192 = shl nuw i32 %191, 1
  %193 = sub i32 %189, %192
  %194 = tail call i32 @llvm.smax.i32(i32 %193, i32 0)
  %195 = tail call i32 @llvm.smin.i32(i32 %72, i32 %194)
  %196 = add i32 %39, 3
  %197 = tail call i32 @llvm.abs.i32(i32 %196, i1 true)
  %198 = sub i32 %197, %72
  %199 = tail call i32 @llvm.smax.i32(i32 %198, i32 0)
  %200 = shl nuw i32 %199, 1
  %201 = sub i32 %197, %200
  %202 = tail call i32 @llvm.smax.i32(i32 %201, i32 0)
  %203 = tail call i32 @llvm.smin.i32(i32 %72, i32 %202)
  %204 = mul i32 %195, %43
  %205 = sub i32 %204, %40
  %206 = add i32 %.0115199, %205
  %207 = mul i32 %206, 3
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %42, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = add i32 %207, 1
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %42, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = add i32 %207, 2
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, ptr %42, i64 %216
  %218 = load float, ptr %217, align 4
  %219 = mul i32 %203, %43
  %220 = sub i32 %219, %40
  %221 = add i32 %.0115199, %220
  %222 = mul i32 %221, 3
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %42, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = add i32 %222, 1
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %42, i64 %227
  %229 = load float, ptr %228, align 4
  %230 = add i32 %222, 2
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, ptr %42, i64 %231
  %233 = load float, ptr %232, align 4
  %234 = fadd reassoc ninf nsz float %225, %210
  %235 = fadd reassoc ninf nsz float %229, %214
  %236 = fadd reassoc ninf nsz float %233, %218
  %237 = fmul reassoc ninf nsz float %234, %187
  %238 = fmul reassoc ninf nsz float %235, %187
  %239 = fmul reassoc ninf nsz float %236, %187
  %240 = fadd reassoc ninf nsz float %237, %181
  %241 = fadd reassoc ninf nsz float %238, %182
  %242 = fadd reassoc ninf nsz float %239, %183
  %factor185 = fmul reassoc ninf nsz float %187, 2.000000e+00
  %243 = fadd reassoc ninf nsz float %factor185, %184
  %.not177 = icmp eq i32 %63, 3
  br i1 %.not177, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %244 = getelementptr i8, ptr %65, i64 16
  %245 = load float, ptr %244, align 4
  %246 = add i32 %39, -4
  %247 = tail call i32 @llvm.abs.i32(i32 %246, i1 true)
  %248 = sub i32 %247, %72
  %249 = tail call i32 @llvm.smax.i32(i32 %248, i32 0)
  %250 = shl nuw i32 %249, 1
  %251 = sub i32 %247, %250
  %252 = tail call i32 @llvm.smax.i32(i32 %251, i32 0)
  %253 = tail call i32 @llvm.smin.i32(i32 %72, i32 %252)
  %254 = add i32 %39, 4
  %255 = tail call i32 @llvm.abs.i32(i32 %254, i1 true)
  %256 = sub i32 %255, %72
  %257 = tail call i32 @llvm.smax.i32(i32 %256, i32 0)
  %258 = shl nuw i32 %257, 1
  %259 = sub i32 %255, %258
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = tail call i32 @llvm.smin.i32(i32 %72, i32 %260)
  %262 = mul i32 %253, %43
  %263 = sub i32 %262, %40
  %264 = add i32 %.0115199, %263
  %265 = mul i32 %264, 3
  %266 = sext i32 %265 to i64
  %267 = getelementptr float, ptr %42, i64 %266
  %268 = load float, ptr %267, align 4
  %269 = add i32 %265, 1
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, ptr %42, i64 %270
  %272 = load float, ptr %271, align 4
  %273 = add i32 %265, 2
  %274 = sext i32 %273 to i64
  %275 = getelementptr float, ptr %42, i64 %274
  %276 = load float, ptr %275, align 4
  %277 = mul i32 %261, %43
  %278 = sub i32 %277, %40
  %279 = add i32 %.0115199, %278
  %280 = mul i32 %279, 3
  %281 = sext i32 %280 to i64
  %282 = getelementptr float, ptr %42, i64 %281
  %283 = load float, ptr %282, align 4
  %284 = add i32 %280, 1
  %285 = sext i32 %284 to i64
  %286 = getelementptr float, ptr %42, i64 %285
  %287 = load float, ptr %286, align 4
  %288 = add i32 %280, 2
  %289 = sext i32 %288 to i64
  %290 = getelementptr float, ptr %42, i64 %289
  %291 = load float, ptr %290, align 4
  %292 = fadd reassoc ninf nsz float %283, %268
  %293 = fadd reassoc ninf nsz float %287, %272
  %294 = fadd reassoc ninf nsz float %291, %276
  %295 = fmul reassoc ninf nsz float %292, %245
  %296 = fmul reassoc ninf nsz float %293, %245
  %297 = fmul reassoc ninf nsz float %294, %245
  %298 = fadd reassoc ninf nsz float %295, %240
  %299 = fadd reassoc ninf nsz float %296, %241
  %300 = fadd reassoc ninf nsz float %297, %242
  %factor186 = fmul reassoc ninf nsz float %245, 2.000000e+00
  %301 = fadd reassoc ninf nsz float %factor186, %243
  %302 = icmp samesign ugt i32 %63, 4
  br i1 %302, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %303 = getelementptr i8, ptr %65, i64 20
  %304 = load float, ptr %303, align 4
  %305 = add i32 %39, -5
  %306 = tail call i32 @llvm.abs.i32(i32 %305, i1 true)
  %307 = sub i32 %306, %72
  %308 = tail call i32 @llvm.smax.i32(i32 %307, i32 0)
  %309 = shl nuw i32 %308, 1
  %310 = sub i32 %306, %309
  %311 = tail call i32 @llvm.smax.i32(i32 %310, i32 0)
  %312 = tail call i32 @llvm.smin.i32(i32 %72, i32 %311)
  %313 = add i32 %39, 5
  %314 = tail call i32 @llvm.abs.i32(i32 %313, i1 true)
  %315 = sub i32 %314, %72
  %316 = tail call i32 @llvm.smax.i32(i32 %315, i32 0)
  %317 = shl nuw i32 %316, 1
  %318 = sub i32 %314, %317
  %319 = tail call i32 @llvm.smax.i32(i32 %318, i32 0)
  %320 = tail call i32 @llvm.smin.i32(i32 %72, i32 %319)
  %321 = mul i32 %312, %43
  %322 = sub i32 %321, %40
  %323 = add i32 %.0115199, %322
  %324 = mul i32 %323, 3
  %325 = sext i32 %324 to i64
  %326 = getelementptr float, ptr %42, i64 %325
  %327 = load float, ptr %326, align 4
  %328 = add i32 %324, 1
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, ptr %42, i64 %329
  %331 = load float, ptr %330, align 4
  %332 = add i32 %324, 2
  %333 = sext i32 %332 to i64
  %334 = getelementptr float, ptr %42, i64 %333
  %335 = load float, ptr %334, align 4
  %336 = mul i32 %320, %43
  %337 = sub i32 %336, %40
  %338 = add i32 %.0115199, %337
  %339 = mul i32 %338, 3
  %340 = sext i32 %339 to i64
  %341 = getelementptr float, ptr %42, i64 %340
  %342 = load float, ptr %341, align 4
  %343 = add i32 %339, 1
  %344 = sext i32 %343 to i64
  %345 = getelementptr float, ptr %42, i64 %344
  %346 = load float, ptr %345, align 4
  %347 = add i32 %339, 2
  %348 = sext i32 %347 to i64
  %349 = getelementptr float, ptr %42, i64 %348
  %350 = load float, ptr %349, align 4
  %351 = fadd reassoc ninf nsz float %342, %327
  %352 = fadd reassoc ninf nsz float %346, %331
  %353 = fadd reassoc ninf nsz float %350, %335
  %354 = fmul reassoc ninf nsz float %351, %304
  %355 = fmul reassoc ninf nsz float %352, %304
  %356 = fmul reassoc ninf nsz float %353, %304
  %357 = fadd reassoc ninf nsz float %354, %298
  %358 = fadd reassoc ninf nsz float %355, %299
  %359 = fadd reassoc ninf nsz float %356, %300
  %factor187 = fmul reassoc ninf nsz float %304, 2.000000e+00
  %360 = fadd reassoc ninf nsz float %factor187, %301
  %.not178 = icmp eq i32 %63, 5
  br i1 %.not178, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %361 = getelementptr i8, ptr %65, i64 24
  %362 = load float, ptr %361, align 4
  %363 = add i32 %39, -6
  %364 = tail call i32 @llvm.abs.i32(i32 %363, i1 true)
  %365 = sub i32 %364, %72
  %366 = tail call i32 @llvm.smax.i32(i32 %365, i32 0)
  %367 = shl nuw i32 %366, 1
  %368 = sub i32 %364, %367
  %369 = tail call i32 @llvm.smax.i32(i32 %368, i32 0)
  %370 = tail call i32 @llvm.smin.i32(i32 %72, i32 %369)
  %371 = add i32 %39, 6
  %372 = tail call i32 @llvm.abs.i32(i32 %371, i1 true)
  %373 = sub i32 %372, %72
  %374 = tail call i32 @llvm.smax.i32(i32 %373, i32 0)
  %375 = shl nuw i32 %374, 1
  %376 = sub i32 %372, %375
  %377 = tail call i32 @llvm.smax.i32(i32 %376, i32 0)
  %378 = tail call i32 @llvm.smin.i32(i32 %72, i32 %377)
  %379 = mul i32 %370, %43
  %380 = sub i32 %379, %40
  %381 = add i32 %.0115199, %380
  %382 = mul i32 %381, 3
  %383 = sext i32 %382 to i64
  %384 = getelementptr float, ptr %42, i64 %383
  %385 = load float, ptr %384, align 4
  %386 = add i32 %382, 1
  %387 = sext i32 %386 to i64
  %388 = getelementptr float, ptr %42, i64 %387
  %389 = load float, ptr %388, align 4
  %390 = add i32 %382, 2
  %391 = sext i32 %390 to i64
  %392 = getelementptr float, ptr %42, i64 %391
  %393 = load float, ptr %392, align 4
  %394 = mul i32 %378, %43
  %395 = sub i32 %394, %40
  %396 = add i32 %.0115199, %395
  %397 = mul i32 %396, 3
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, ptr %42, i64 %398
  %400 = load float, ptr %399, align 4
  %401 = add i32 %397, 1
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, ptr %42, i64 %402
  %404 = load float, ptr %403, align 4
  %405 = add i32 %397, 2
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, ptr %42, i64 %406
  %408 = load float, ptr %407, align 4
  %409 = fadd reassoc ninf nsz float %400, %385
  %410 = fadd reassoc ninf nsz float %404, %389
  %411 = fadd reassoc ninf nsz float %408, %393
  %412 = fmul reassoc ninf nsz float %409, %362
  %413 = fmul reassoc ninf nsz float %410, %362
  %414 = fmul reassoc ninf nsz float %411, %362
  %415 = fadd reassoc ninf nsz float %412, %357
  %416 = fadd reassoc ninf nsz float %413, %358
  %417 = fadd reassoc ninf nsz float %414, %359
  %factor188 = fmul reassoc ninf nsz float %362, 2.000000e+00
  %418 = fadd reassoc ninf nsz float %factor188, %360
  %419 = icmp samesign ugt i32 %63, 6
  br i1 %419, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %420 = getelementptr i8, ptr %65, i64 28
  %421 = load float, ptr %420, align 4
  %422 = add i32 %39, -7
  %423 = tail call i32 @llvm.abs.i32(i32 %422, i1 true)
  %424 = sub i32 %423, %72
  %425 = tail call i32 @llvm.smax.i32(i32 %424, i32 0)
  %426 = shl nuw i32 %425, 1
  %427 = sub i32 %423, %426
  %428 = tail call i32 @llvm.smax.i32(i32 %427, i32 0)
  %429 = tail call i32 @llvm.smin.i32(i32 %72, i32 %428)
  %430 = add i32 %39, 7
  %431 = tail call i32 @llvm.abs.i32(i32 %430, i1 true)
  %432 = sub i32 %431, %72
  %433 = tail call i32 @llvm.smax.i32(i32 %432, i32 0)
  %434 = shl nuw i32 %433, 1
  %435 = sub i32 %431, %434
  %436 = tail call i32 @llvm.smax.i32(i32 %435, i32 0)
  %437 = tail call i32 @llvm.smin.i32(i32 %72, i32 %436)
  %438 = mul i32 %429, %43
  %439 = sub i32 %438, %40
  %440 = add i32 %.0115199, %439
  %441 = mul i32 %440, 3
  %442 = sext i32 %441 to i64
  %443 = getelementptr float, ptr %42, i64 %442
  %444 = load float, ptr %443, align 4
  %445 = add i32 %441, 1
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, ptr %42, i64 %446
  %448 = load float, ptr %447, align 4
  %449 = add i32 %441, 2
  %450 = sext i32 %449 to i64
  %451 = getelementptr float, ptr %42, i64 %450
  %452 = load float, ptr %451, align 4
  %453 = mul i32 %437, %43
  %454 = sub i32 %453, %40
  %455 = add i32 %.0115199, %454
  %456 = mul i32 %455, 3
  %457 = sext i32 %456 to i64
  %458 = getelementptr float, ptr %42, i64 %457
  %459 = load float, ptr %458, align 4
  %460 = add i32 %456, 1
  %461 = sext i32 %460 to i64
  %462 = getelementptr float, ptr %42, i64 %461
  %463 = load float, ptr %462, align 4
  %464 = add i32 %456, 2
  %465 = sext i32 %464 to i64
  %466 = getelementptr float, ptr %42, i64 %465
  %467 = load float, ptr %466, align 4
  %468 = fadd reassoc ninf nsz float %459, %444
  %469 = fadd reassoc ninf nsz float %463, %448
  %470 = fadd reassoc ninf nsz float %467, %452
  %471 = fmul reassoc ninf nsz float %468, %421
  %472 = fmul reassoc ninf nsz float %469, %421
  %473 = fmul reassoc ninf nsz float %470, %421
  %474 = fadd reassoc ninf nsz float %471, %415
  %475 = fadd reassoc ninf nsz float %472, %416
  %476 = fadd reassoc ninf nsz float %473, %417
  %factor189 = fmul reassoc ninf nsz float %421, 2.000000e+00
  %477 = fadd reassoc ninf nsz float %factor189, %418
  %.not179 = icmp eq i32 %63, 7
  br i1 %.not179, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %478 = getelementptr i8, ptr %65, i64 32
  %479 = load float, ptr %478, align 4
  %480 = add i32 %39, -8
  %481 = tail call i32 @llvm.abs.i32(i32 %480, i1 true)
  %482 = sub i32 %481, %72
  %483 = tail call i32 @llvm.smax.i32(i32 %482, i32 0)
  %484 = shl nuw i32 %483, 1
  %485 = sub i32 %481, %484
  %486 = tail call i32 @llvm.smax.i32(i32 %485, i32 0)
  %487 = tail call i32 @llvm.smin.i32(i32 %72, i32 %486)
  %488 = add i32 %39, 8
  %489 = tail call i32 @llvm.abs.i32(i32 %488, i1 true)
  %490 = sub i32 %489, %72
  %491 = tail call i32 @llvm.smax.i32(i32 %490, i32 0)
  %492 = shl nuw i32 %491, 1
  %493 = sub i32 %489, %492
  %494 = tail call i32 @llvm.smax.i32(i32 %493, i32 0)
  %495 = tail call i32 @llvm.smin.i32(i32 %72, i32 %494)
  %496 = mul i32 %487, %43
  %497 = sub i32 %496, %40
  %498 = add i32 %.0115199, %497
  %499 = mul i32 %498, 3
  %500 = sext i32 %499 to i64
  %501 = getelementptr float, ptr %42, i64 %500
  %502 = load float, ptr %501, align 4
  %503 = add i32 %499, 1
  %504 = sext i32 %503 to i64
  %505 = getelementptr float, ptr %42, i64 %504
  %506 = load float, ptr %505, align 4
  %507 = add i32 %499, 2
  %508 = sext i32 %507 to i64
  %509 = getelementptr float, ptr %42, i64 %508
  %510 = load float, ptr %509, align 4
  %511 = mul i32 %495, %43
  %512 = sub i32 %511, %40
  %513 = add i32 %.0115199, %512
  %514 = mul i32 %513, 3
  %515 = sext i32 %514 to i64
  %516 = getelementptr float, ptr %42, i64 %515
  %517 = load float, ptr %516, align 4
  %518 = add i32 %514, 1
  %519 = sext i32 %518 to i64
  %520 = getelementptr float, ptr %42, i64 %519
  %521 = load float, ptr %520, align 4
  %522 = add i32 %514, 2
  %523 = sext i32 %522 to i64
  %524 = getelementptr float, ptr %42, i64 %523
  %525 = load float, ptr %524, align 4
  %526 = fadd reassoc ninf nsz float %517, %502
  %527 = fadd reassoc ninf nsz float %521, %506
  %528 = fadd reassoc ninf nsz float %525, %510
  %529 = fmul reassoc ninf nsz float %526, %479
  %530 = fmul reassoc ninf nsz float %527, %479
  %531 = fmul reassoc ninf nsz float %528, %479
  %532 = fadd reassoc ninf nsz float %529, %474
  %533 = fadd reassoc ninf nsz float %530, %475
  %534 = fadd reassoc ninf nsz float %531, %476
  %factor190 = fmul reassoc ninf nsz float %479, 2.000000e+00
  %535 = fadd reassoc ninf nsz float %factor190, %477
  %536 = icmp samesign ugt i32 %63, 8
  br i1 %536, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %537 = getelementptr i8, ptr %65, i64 36
  %538 = load float, ptr %537, align 4
  %539 = add i32 %39, -9
  %540 = tail call i32 @llvm.abs.i32(i32 %539, i1 true)
  %541 = sub i32 %540, %72
  %542 = tail call i32 @llvm.smax.i32(i32 %541, i32 0)
  %543 = shl nuw i32 %542, 1
  %544 = sub i32 %540, %543
  %545 = tail call i32 @llvm.smax.i32(i32 %544, i32 0)
  %546 = tail call i32 @llvm.smin.i32(i32 %72, i32 %545)
  %547 = add i32 %39, 9
  %548 = tail call i32 @llvm.abs.i32(i32 %547, i1 true)
  %549 = sub i32 %548, %72
  %550 = tail call i32 @llvm.smax.i32(i32 %549, i32 0)
  %551 = shl nuw i32 %550, 1
  %552 = sub i32 %548, %551
  %553 = tail call i32 @llvm.smax.i32(i32 %552, i32 0)
  %554 = tail call i32 @llvm.smin.i32(i32 %72, i32 %553)
  %555 = mul i32 %546, %43
  %556 = sub i32 %555, %40
  %557 = add i32 %.0115199, %556
  %558 = mul i32 %557, 3
  %559 = sext i32 %558 to i64
  %560 = getelementptr float, ptr %42, i64 %559
  %561 = load float, ptr %560, align 4
  %562 = add i32 %558, 1
  %563 = sext i32 %562 to i64
  %564 = getelementptr float, ptr %42, i64 %563
  %565 = load float, ptr %564, align 4
  %566 = add i32 %558, 2
  %567 = sext i32 %566 to i64
  %568 = getelementptr float, ptr %42, i64 %567
  %569 = load float, ptr %568, align 4
  %570 = mul i32 %554, %43
  %571 = sub i32 %570, %40
  %572 = add i32 %.0115199, %571
  %573 = mul i32 %572, 3
  %574 = sext i32 %573 to i64
  %575 = getelementptr float, ptr %42, i64 %574
  %576 = load float, ptr %575, align 4
  %577 = add i32 %573, 1
  %578 = sext i32 %577 to i64
  %579 = getelementptr float, ptr %42, i64 %578
  %580 = load float, ptr %579, align 4
  %581 = add i32 %573, 2
  %582 = sext i32 %581 to i64
  %583 = getelementptr float, ptr %42, i64 %582
  %584 = load float, ptr %583, align 4
  %585 = fadd reassoc ninf nsz float %576, %561
  %586 = fadd reassoc ninf nsz float %580, %565
  %587 = fadd reassoc ninf nsz float %584, %569
  %588 = fmul reassoc ninf nsz float %585, %538
  %589 = fmul reassoc ninf nsz float %586, %538
  %590 = fmul reassoc ninf nsz float %587, %538
  %591 = fadd reassoc ninf nsz float %588, %532
  %592 = fadd reassoc ninf nsz float %589, %533
  %593 = fadd reassoc ninf nsz float %590, %534
  %factor191 = fmul reassoc ninf nsz float %538, 2.000000e+00
  %594 = fadd reassoc ninf nsz float %factor191, %535
  %.not180 = icmp eq i32 %63, 9
  br i1 %.not180, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %595 = getelementptr i8, ptr %65, i64 40
  %596 = load float, ptr %595, align 4
  %597 = add i32 %39, -10
  %598 = tail call i32 @llvm.abs.i32(i32 %597, i1 true)
  %599 = sub i32 %598, %72
  %600 = tail call i32 @llvm.smax.i32(i32 %599, i32 0)
  %601 = shl nuw i32 %600, 1
  %602 = sub i32 %598, %601
  %603 = tail call i32 @llvm.smax.i32(i32 %602, i32 0)
  %604 = tail call i32 @llvm.smin.i32(i32 %72, i32 %603)
  %605 = add i32 %39, 10
  %606 = tail call i32 @llvm.abs.i32(i32 %605, i1 true)
  %607 = sub i32 %606, %72
  %608 = tail call i32 @llvm.smax.i32(i32 %607, i32 0)
  %609 = shl nuw i32 %608, 1
  %610 = sub i32 %606, %609
  %611 = tail call i32 @llvm.smax.i32(i32 %610, i32 0)
  %612 = tail call i32 @llvm.smin.i32(i32 %72, i32 %611)
  %613 = mul i32 %604, %43
  %614 = sub i32 %613, %40
  %615 = add i32 %.0115199, %614
  %616 = mul i32 %615, 3
  %617 = sext i32 %616 to i64
  %618 = getelementptr float, ptr %42, i64 %617
  %619 = load float, ptr %618, align 4
  %620 = add i32 %616, 1
  %621 = sext i32 %620 to i64
  %622 = getelementptr float, ptr %42, i64 %621
  %623 = load float, ptr %622, align 4
  %624 = add i32 %616, 2
  %625 = sext i32 %624 to i64
  %626 = getelementptr float, ptr %42, i64 %625
  %627 = load float, ptr %626, align 4
  %628 = mul i32 %612, %43
  %629 = sub i32 %628, %40
  %630 = add i32 %.0115199, %629
  %631 = mul i32 %630, 3
  %632 = sext i32 %631 to i64
  %633 = getelementptr float, ptr %42, i64 %632
  %634 = load float, ptr %633, align 4
  %635 = add i32 %631, 1
  %636 = sext i32 %635 to i64
  %637 = getelementptr float, ptr %42, i64 %636
  %638 = load float, ptr %637, align 4
  %639 = add i32 %631, 2
  %640 = sext i32 %639 to i64
  %641 = getelementptr float, ptr %42, i64 %640
  %642 = load float, ptr %641, align 4
  %643 = fadd reassoc ninf nsz float %634, %619
  %644 = fadd reassoc ninf nsz float %638, %623
  %645 = fadd reassoc ninf nsz float %642, %627
  %646 = fmul reassoc ninf nsz float %643, %596
  %647 = fmul reassoc ninf nsz float %644, %596
  %648 = fmul reassoc ninf nsz float %645, %596
  %649 = fadd reassoc ninf nsz float %646, %591
  %650 = fadd reassoc ninf nsz float %647, %592
  %651 = fadd reassoc ninf nsz float %648, %593
  %factor192 = fmul reassoc ninf nsz float %596, 2.000000e+00
  %652 = fadd reassoc ninf nsz float %factor192, %594
  %653 = icmp samesign ugt i32 %63, 10
  br i1 %653, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %654 = getelementptr i8, ptr %65, i64 44
  %655 = load float, ptr %654, align 4
  %656 = add i32 %39, -11
  %657 = tail call i32 @llvm.abs.i32(i32 %656, i1 true)
  %658 = sub i32 %657, %72
  %659 = tail call i32 @llvm.smax.i32(i32 %658, i32 0)
  %660 = shl nuw i32 %659, 1
  %661 = sub i32 %657, %660
  %662 = tail call i32 @llvm.smax.i32(i32 %661, i32 0)
  %663 = tail call i32 @llvm.smin.i32(i32 %72, i32 %662)
  %664 = add i32 %39, 11
  %665 = tail call i32 @llvm.abs.i32(i32 %664, i1 true)
  %666 = sub i32 %665, %72
  %667 = tail call i32 @llvm.smax.i32(i32 %666, i32 0)
  %668 = shl nuw i32 %667, 1
  %669 = sub i32 %665, %668
  %670 = tail call i32 @llvm.smax.i32(i32 %669, i32 0)
  %671 = tail call i32 @llvm.smin.i32(i32 %72, i32 %670)
  %672 = mul i32 %663, %43
  %673 = sub i32 %672, %40
  %674 = add i32 %.0115199, %673
  %675 = mul i32 %674, 3
  %676 = sext i32 %675 to i64
  %677 = getelementptr float, ptr %42, i64 %676
  %678 = load float, ptr %677, align 4
  %679 = add i32 %675, 1
  %680 = sext i32 %679 to i64
  %681 = getelementptr float, ptr %42, i64 %680
  %682 = load float, ptr %681, align 4
  %683 = add i32 %675, 2
  %684 = sext i32 %683 to i64
  %685 = getelementptr float, ptr %42, i64 %684
  %686 = load float, ptr %685, align 4
  %687 = mul i32 %671, %43
  %688 = sub i32 %687, %40
  %689 = add i32 %.0115199, %688
  %690 = mul i32 %689, 3
  %691 = sext i32 %690 to i64
  %692 = getelementptr float, ptr %42, i64 %691
  %693 = load float, ptr %692, align 4
  %694 = add i32 %690, 1
  %695 = sext i32 %694 to i64
  %696 = getelementptr float, ptr %42, i64 %695
  %697 = load float, ptr %696, align 4
  %698 = add i32 %690, 2
  %699 = sext i32 %698 to i64
  %700 = getelementptr float, ptr %42, i64 %699
  %701 = load float, ptr %700, align 4
  %702 = fadd reassoc ninf nsz float %693, %678
  %703 = fadd reassoc ninf nsz float %697, %682
  %704 = fadd reassoc ninf nsz float %701, %686
  %705 = fmul reassoc ninf nsz float %702, %655
  %706 = fmul reassoc ninf nsz float %703, %655
  %707 = fmul reassoc ninf nsz float %704, %655
  %708 = fadd reassoc ninf nsz float %705, %649
  %709 = fadd reassoc ninf nsz float %706, %650
  %710 = fadd reassoc ninf nsz float %707, %651
  %factor193 = fmul reassoc ninf nsz float %655, 2.000000e+00
  %711 = fadd reassoc ninf nsz float %factor193, %652
  %.not181 = icmp eq i32 %63, 11
  br i1 %.not181, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %712 = getelementptr i8, ptr %65, i64 48
  %713 = load float, ptr %712, align 4
  %714 = add i32 %39, -12
  %715 = tail call i32 @llvm.abs.i32(i32 %714, i1 true)
  %716 = sub i32 %715, %72
  %717 = tail call i32 @llvm.smax.i32(i32 %716, i32 0)
  %718 = shl nuw i32 %717, 1
  %719 = sub i32 %715, %718
  %720 = tail call i32 @llvm.smax.i32(i32 %719, i32 0)
  %721 = tail call i32 @llvm.smin.i32(i32 %72, i32 %720)
  %722 = add i32 %39, 12
  %723 = tail call i32 @llvm.abs.i32(i32 %722, i1 true)
  %724 = sub i32 %723, %72
  %725 = tail call i32 @llvm.smax.i32(i32 %724, i32 0)
  %726 = shl nuw i32 %725, 1
  %727 = sub i32 %723, %726
  %728 = tail call i32 @llvm.smax.i32(i32 %727, i32 0)
  %729 = tail call i32 @llvm.smin.i32(i32 %72, i32 %728)
  %730 = mul i32 %721, %43
  %731 = sub i32 %730, %40
  %732 = add i32 %.0115199, %731
  %733 = mul i32 %732, 3
  %734 = sext i32 %733 to i64
  %735 = getelementptr float, ptr %42, i64 %734
  %736 = load float, ptr %735, align 4
  %737 = add i32 %733, 1
  %738 = sext i32 %737 to i64
  %739 = getelementptr float, ptr %42, i64 %738
  %740 = load float, ptr %739, align 4
  %741 = add i32 %733, 2
  %742 = sext i32 %741 to i64
  %743 = getelementptr float, ptr %42, i64 %742
  %744 = load float, ptr %743, align 4
  %745 = mul i32 %729, %43
  %746 = sub i32 %745, %40
  %747 = add i32 %.0115199, %746
  %748 = mul i32 %747, 3
  %749 = sext i32 %748 to i64
  %750 = getelementptr float, ptr %42, i64 %749
  %751 = load float, ptr %750, align 4
  %752 = add i32 %748, 1
  %753 = sext i32 %752 to i64
  %754 = getelementptr float, ptr %42, i64 %753
  %755 = load float, ptr %754, align 4
  %756 = add i32 %748, 2
  %757 = sext i32 %756 to i64
  %758 = getelementptr float, ptr %42, i64 %757
  %759 = load float, ptr %758, align 4
  %760 = fadd reassoc ninf nsz float %751, %736
  %761 = fadd reassoc ninf nsz float %755, %740
  %762 = fadd reassoc ninf nsz float %759, %744
  %763 = fmul reassoc ninf nsz float %760, %713
  %764 = fmul reassoc ninf nsz float %761, %713
  %765 = fmul reassoc ninf nsz float %762, %713
  %766 = fadd reassoc ninf nsz float %763, %708
  %767 = fadd reassoc ninf nsz float %764, %709
  %768 = fadd reassoc ninf nsz float %765, %710
  %factor194 = fmul reassoc ninf nsz float %713, 2.000000e+00
  %769 = fadd reassoc ninf nsz float %factor194, %711
  %770 = icmp samesign ugt i32 %63, 12
  br i1 %770, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %771 = getelementptr i8, ptr %65, i64 52
  %772 = load float, ptr %771, align 4
  %773 = add i32 %39, -13
  %774 = tail call i32 @llvm.abs.i32(i32 %773, i1 true)
  %775 = sub i32 %774, %72
  %776 = tail call i32 @llvm.smax.i32(i32 %775, i32 0)
  %777 = shl nuw i32 %776, 1
  %778 = sub i32 %774, %777
  %779 = tail call i32 @llvm.smax.i32(i32 %778, i32 0)
  %780 = tail call i32 @llvm.smin.i32(i32 %72, i32 %779)
  %781 = add i32 %39, 13
  %782 = tail call i32 @llvm.abs.i32(i32 %781, i1 true)
  %783 = sub i32 %782, %72
  %784 = tail call i32 @llvm.smax.i32(i32 %783, i32 0)
  %785 = shl nuw i32 %784, 1
  %786 = sub i32 %782, %785
  %787 = tail call i32 @llvm.smax.i32(i32 %786, i32 0)
  %788 = tail call i32 @llvm.smin.i32(i32 %72, i32 %787)
  %789 = mul i32 %780, %43
  %790 = sub i32 %789, %40
  %791 = add i32 %.0115199, %790
  %792 = mul i32 %791, 3
  %793 = sext i32 %792 to i64
  %794 = getelementptr float, ptr %42, i64 %793
  %795 = load float, ptr %794, align 4
  %796 = add i32 %792, 1
  %797 = sext i32 %796 to i64
  %798 = getelementptr float, ptr %42, i64 %797
  %799 = load float, ptr %798, align 4
  %800 = add i32 %792, 2
  %801 = sext i32 %800 to i64
  %802 = getelementptr float, ptr %42, i64 %801
  %803 = load float, ptr %802, align 4
  %804 = mul i32 %788, %43
  %805 = sub i32 %804, %40
  %806 = add i32 %.0115199, %805
  %807 = mul i32 %806, 3
  %808 = sext i32 %807 to i64
  %809 = getelementptr float, ptr %42, i64 %808
  %810 = load float, ptr %809, align 4
  %811 = add i32 %807, 1
  %812 = sext i32 %811 to i64
  %813 = getelementptr float, ptr %42, i64 %812
  %814 = load float, ptr %813, align 4
  %815 = add i32 %807, 2
  %816 = sext i32 %815 to i64
  %817 = getelementptr float, ptr %42, i64 %816
  %818 = load float, ptr %817, align 4
  %819 = fadd reassoc ninf nsz float %810, %795
  %820 = fadd reassoc ninf nsz float %814, %799
  %821 = fadd reassoc ninf nsz float %818, %803
  %822 = fmul reassoc ninf nsz float %819, %772
  %823 = fmul reassoc ninf nsz float %820, %772
  %824 = fmul reassoc ninf nsz float %821, %772
  %825 = fadd reassoc ninf nsz float %822, %766
  %826 = fadd reassoc ninf nsz float %823, %767
  %827 = fadd reassoc ninf nsz float %824, %768
  %factor195 = fmul reassoc ninf nsz float %772, 2.000000e+00
  %828 = fadd reassoc ninf nsz float %factor195, %769
  %.not182 = icmp eq i32 %63, 13
  br i1 %.not182, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %829 = getelementptr i8, ptr %65, i64 56
  %830 = load float, ptr %829, align 4
  %831 = add i32 %39, -14
  %832 = tail call i32 @llvm.abs.i32(i32 %831, i1 true)
  %833 = sub i32 %832, %72
  %834 = tail call i32 @llvm.smax.i32(i32 %833, i32 0)
  %835 = shl nuw i32 %834, 1
  %836 = sub i32 %832, %835
  %837 = tail call i32 @llvm.smax.i32(i32 %836, i32 0)
  %838 = tail call i32 @llvm.smin.i32(i32 %72, i32 %837)
  %839 = add i32 %39, 14
  %840 = tail call i32 @llvm.abs.i32(i32 %839, i1 true)
  %841 = sub i32 %840, %72
  %842 = tail call i32 @llvm.smax.i32(i32 %841, i32 0)
  %843 = shl nuw i32 %842, 1
  %844 = sub i32 %840, %843
  %845 = tail call i32 @llvm.smax.i32(i32 %844, i32 0)
  %846 = tail call i32 @llvm.smin.i32(i32 %72, i32 %845)
  %847 = mul i32 %838, %43
  %848 = sub i32 %847, %40
  %849 = add i32 %.0115199, %848
  %850 = mul i32 %849, 3
  %851 = sext i32 %850 to i64
  %852 = getelementptr float, ptr %42, i64 %851
  %853 = load float, ptr %852, align 4
  %854 = add i32 %850, 1
  %855 = sext i32 %854 to i64
  %856 = getelementptr float, ptr %42, i64 %855
  %857 = load float, ptr %856, align 4
  %858 = add i32 %850, 2
  %859 = sext i32 %858 to i64
  %860 = getelementptr float, ptr %42, i64 %859
  %861 = load float, ptr %860, align 4
  %862 = mul i32 %846, %43
  %863 = sub i32 %862, %40
  %864 = add i32 %.0115199, %863
  %865 = mul i32 %864, 3
  %866 = sext i32 %865 to i64
  %867 = getelementptr float, ptr %42, i64 %866
  %868 = load float, ptr %867, align 4
  %869 = add i32 %865, 1
  %870 = sext i32 %869 to i64
  %871 = getelementptr float, ptr %42, i64 %870
  %872 = load float, ptr %871, align 4
  %873 = add i32 %865, 2
  %874 = sext i32 %873 to i64
  %875 = getelementptr float, ptr %42, i64 %874
  %876 = load float, ptr %875, align 4
  %877 = fadd reassoc ninf nsz float %868, %853
  %878 = fadd reassoc ninf nsz float %872, %857
  %879 = fadd reassoc ninf nsz float %876, %861
  %880 = fmul reassoc ninf nsz float %877, %830
  %881 = fmul reassoc ninf nsz float %878, %830
  %882 = fmul reassoc ninf nsz float %879, %830
  %883 = fadd reassoc ninf nsz float %880, %825
  %884 = fadd reassoc ninf nsz float %881, %826
  %885 = fadd reassoc ninf nsz float %882, %827
  %factor196 = fmul reassoc ninf nsz float %830, 2.000000e+00
  %886 = fadd reassoc ninf nsz float %factor196, %828
  %887 = icmp samesign ugt i32 %63, 14
  br i1 %887, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %888 = getelementptr i8, ptr %65, i64 60
  %889 = load float, ptr %888, align 4
  %890 = add i32 %39, -15
  %891 = tail call i32 @llvm.abs.i32(i32 %890, i1 true)
  %892 = sub i32 %891, %72
  %893 = tail call i32 @llvm.smax.i32(i32 %892, i32 0)
  %894 = shl nuw i32 %893, 1
  %895 = sub i32 %891, %894
  %896 = tail call i32 @llvm.smax.i32(i32 %895, i32 0)
  %897 = tail call i32 @llvm.smin.i32(i32 %72, i32 %896)
  %898 = add i32 %39, 15
  %899 = tail call i32 @llvm.abs.i32(i32 %898, i1 true)
  %900 = sub i32 %899, %72
  %901 = tail call i32 @llvm.smax.i32(i32 %900, i32 0)
  %902 = shl nuw i32 %901, 1
  %903 = sub i32 %899, %902
  %904 = tail call i32 @llvm.smax.i32(i32 %903, i32 0)
  %905 = tail call i32 @llvm.smin.i32(i32 %72, i32 %904)
  %906 = mul i32 %897, %43
  %907 = sub i32 %906, %40
  %908 = add i32 %.0115199, %907
  %909 = mul i32 %908, 3
  %910 = sext i32 %909 to i64
  %911 = getelementptr float, ptr %42, i64 %910
  %912 = load float, ptr %911, align 4
  %913 = add i32 %909, 1
  %914 = sext i32 %913 to i64
  %915 = getelementptr float, ptr %42, i64 %914
  %916 = load float, ptr %915, align 4
  %917 = add i32 %909, 2
  %918 = sext i32 %917 to i64
  %919 = getelementptr float, ptr %42, i64 %918
  %920 = load float, ptr %919, align 4
  %921 = mul i32 %905, %43
  %922 = sub i32 %921, %40
  %923 = add i32 %.0115199, %922
  %924 = mul i32 %923, 3
  %925 = sext i32 %924 to i64
  %926 = getelementptr float, ptr %42, i64 %925
  %927 = load float, ptr %926, align 4
  %928 = add i32 %924, 1
  %929 = sext i32 %928 to i64
  %930 = getelementptr float, ptr %42, i64 %929
  %931 = load float, ptr %930, align 4
  %932 = add i32 %924, 2
  %933 = sext i32 %932 to i64
  %934 = getelementptr float, ptr %42, i64 %933
  %935 = load float, ptr %934, align 4
  %936 = fadd reassoc ninf nsz float %927, %912
  %937 = fadd reassoc ninf nsz float %931, %916
  %938 = fadd reassoc ninf nsz float %935, %920
  %939 = fmul reassoc ninf nsz float %936, %889
  %940 = fmul reassoc ninf nsz float %937, %889
  %941 = fmul reassoc ninf nsz float %938, %889
  %942 = fadd reassoc ninf nsz float %939, %883
  %943 = fadd reassoc ninf nsz float %940, %884
  %944 = fadd reassoc ninf nsz float %941, %885
  %factor197 = fmul reassoc ninf nsz float %889, 2.000000e+00
  %945 = fadd reassoc ninf nsz float %factor197, %886
  %.not183 = icmp eq i32 %63, 15
  br i1 %.not183, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %946 = getelementptr i8, ptr %65, i64 64
  %947 = load float, ptr %946, align 4
  %948 = add i32 %39, -16
  %949 = tail call i32 @llvm.abs.i32(i32 %948, i1 true)
  %950 = sub i32 %949, %72
  %951 = tail call i32 @llvm.smax.i32(i32 %950, i32 0)
  %952 = shl nuw i32 %951, 1
  %953 = sub i32 %949, %952
  %954 = tail call i32 @llvm.smax.i32(i32 %953, i32 0)
  %955 = tail call i32 @llvm.smin.i32(i32 %72, i32 %954)
  %956 = add i32 %39, 16
  %957 = tail call i32 @llvm.abs.i32(i32 %956, i1 true)
  %958 = sub i32 %957, %72
  %959 = tail call i32 @llvm.smax.i32(i32 %958, i32 0)
  %960 = shl nuw i32 %959, 1
  %961 = sub i32 %957, %960
  %962 = tail call i32 @llvm.smax.i32(i32 %961, i32 0)
  %963 = tail call i32 @llvm.smin.i32(i32 %72, i32 %962)
  %964 = mul i32 %955, %43
  %965 = sub i32 %964, %40
  %966 = add i32 %.0115199, %965
  %967 = mul i32 %966, 3
  %968 = sext i32 %967 to i64
  %969 = getelementptr float, ptr %42, i64 %968
  %970 = load float, ptr %969, align 4
  %971 = add i32 %967, 1
  %972 = sext i32 %971 to i64
  %973 = getelementptr float, ptr %42, i64 %972
  %974 = load float, ptr %973, align 4
  %975 = add i32 %967, 2
  %976 = sext i32 %975 to i64
  %977 = getelementptr float, ptr %42, i64 %976
  %978 = load float, ptr %977, align 4
  %979 = mul i32 %963, %43
  %980 = sub i32 %979, %40
  %981 = add i32 %.0115199, %980
  %982 = mul i32 %981, 3
  %983 = sext i32 %982 to i64
  %984 = getelementptr float, ptr %42, i64 %983
  %985 = load float, ptr %984, align 4
  %986 = add i32 %982, 1
  %987 = sext i32 %986 to i64
  %988 = getelementptr float, ptr %42, i64 %987
  %989 = load float, ptr %988, align 4
  %990 = add i32 %982, 2
  %991 = sext i32 %990 to i64
  %992 = getelementptr float, ptr %42, i64 %991
  %993 = load float, ptr %992, align 4
  %994 = fadd reassoc ninf nsz float %985, %970
  %995 = fadd reassoc ninf nsz float %989, %974
  %996 = fadd reassoc ninf nsz float %993, %978
  %997 = fmul reassoc ninf nsz float %994, %947
  %998 = fmul reassoc ninf nsz float %995, %947
  %999 = fmul reassoc ninf nsz float %996, %947
  %1000 = fadd reassoc ninf nsz float %997, %942
  %1001 = fadd reassoc ninf nsz float %998, %943
  %1002 = fadd reassoc ninf nsz float %999, %944
  %factor198 = fmul reassoc ninf nsz float %947, 2.000000e+00
  %1003 = fadd reassoc ninf nsz float %factor198, %945
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.15114 = phi float [ %1000, %true_block43 ], [ %942, %after_if42 ], [ %883, %after_if39 ], [ %825, %after_if36 ], [ %766, %after_if33 ], [ %708, %after_if30 ], [ %649, %after_if27 ], [ %591, %after_if24 ], [ %532, %after_if21 ], [ %474, %after_if18 ], [ %415, %after_if15 ], [ %357, %after_if12 ], [ %298, %after_if9 ], [ %240, %after_if6 ], [ %181, %after_if3 ], [ %123, %after_if ], [ %59, %for_loop_body ]
  %.1598 = phi float [ %1001, %true_block43 ], [ %943, %after_if42 ], [ %884, %after_if39 ], [ %826, %after_if36 ], [ %767, %after_if33 ], [ %709, %after_if30 ], [ %650, %after_if27 ], [ %592, %after_if24 ], [ %533, %after_if21 ], [ %475, %after_if18 ], [ %416, %after_if15 ], [ %358, %after_if12 ], [ %299, %after_if9 ], [ %241, %after_if6 ], [ %182, %after_if3 ], [ %124, %after_if ], [ %60, %for_loop_body ]
  %.1582 = phi float [ %1002, %true_block43 ], [ %944, %after_if42 ], [ %885, %after_if39 ], [ %827, %after_if36 ], [ %768, %after_if33 ], [ %710, %after_if30 ], [ %651, %after_if27 ], [ %593, %after_if24 ], [ %534, %after_if21 ], [ %476, %after_if18 ], [ %417, %after_if15 ], [ %359, %after_if12 ], [ %300, %after_if9 ], [ %242, %after_if6 ], [ %183, %after_if3 ], [ %125, %after_if ], [ %61, %for_loop_body ]
  %.15 = phi float [ %1003, %true_block43 ], [ %945, %after_if42 ], [ %886, %after_if39 ], [ %828, %after_if36 ], [ %769, %after_if33 ], [ %711, %after_if30 ], [ %652, %after_if27 ], [ %594, %after_if24 ], [ %535, %after_if21 ], [ %477, %after_if18 ], [ %418, %after_if15 ], [ %360, %after_if12 ], [ %301, %after_if9 ], [ %243, %after_if6 ], [ %184, %after_if3 ], [ %126, %after_if ], [ %41, %for_loop_body ]
  %1004 = fdiv reassoc ninf nsz float %.15114, %.15
  %1005 = fdiv reassoc ninf nsz float %.1598, %.15
  %1006 = fdiv reassoc ninf nsz float %.1582, %.15
  %1007 = load ptr, ptr %25, align 8
  %1008 = load i32, ptr %26, align 4
  %1009 = sub i32 %1008, %32
  %1010 = mul i32 %1009, 3
  %1011 = mul i32 %1010, %39
  %1012 = add i32 %lsr.iv, %1011
  %1013 = sext i32 %1012 to i64
  %1014 = getelementptr float, ptr %1007, i64 %1013
  store float %1004, ptr %1014, align 4
  %1015 = load ptr, ptr %25, align 8
  %1016 = load i32, ptr %26, align 4
  %1017 = sub i32 %1016, %32
  %1018 = mul i32 %1017, 3
  %1019 = mul i32 %1018, %39
  %1020 = add i32 %lsr.iv, %1019
  %1021 = add i32 %1020, 1
  %1022 = sext i32 %1021 to i64
  %1023 = getelementptr float, ptr %1015, i64 %1022
  store float %1005, ptr %1023, align 4
  %1024 = load ptr, ptr %25, align 8
  %1025 = load i32, ptr %26, align 4
  %1026 = sub i32 %1025, %32
  %1027 = mul i32 %1026, 3
  %1028 = mul i32 %1027, %39
  %1029 = add i32 %lsr.iv, %1028
  %1030 = add i32 %1029, 2
  %1031 = sext i32 %1030 to i64
  %1032 = getelementptr float, ptr %1024, i64 %1031
  store float %1006, ptr %1032, align 4
  %1033 = add nsw i32 %.0115199, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %1033
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
