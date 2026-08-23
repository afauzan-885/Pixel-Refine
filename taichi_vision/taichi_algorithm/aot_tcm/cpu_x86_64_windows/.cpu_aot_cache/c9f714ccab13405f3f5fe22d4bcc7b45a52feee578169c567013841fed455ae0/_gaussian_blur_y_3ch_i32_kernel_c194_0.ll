; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.13 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gaussian_blur_y_3ch_i32_kernel_c194_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 12
  store i32 %2, ptr %7, align 4
  %8 = load ptr, ptr %context, align 8
  %9 = getelementptr i8, ptr %8, i64 52
  %10 = load i32, ptr %9, align 4
  %11 = getelementptr i8, ptr %8, i64 72
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

define void @_gaussian_blur_y_3ch_i32_kernel_c194_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = load ptr, ptr %20, align 8
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 16
  %24 = getelementptr i8, ptr %19, i64 4
  %25 = getelementptr i8, ptr %19, i64 8
  %26 = getelementptr i8, ptr %19, i64 40
  %27 = getelementptr i8, ptr %19, i64 28
  %28 = getelementptr i8, ptr %19, i64 32
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.0115199 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %1092, %after_if45 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.0115199, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.0115199
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.0115199, %35
  %39 = and i1 %37, %38
  %.neg116 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg116
  %41 = mul i32 %40, %33
  %42 = load float, ptr %21, align 4
  %43 = load ptr, ptr %23, align 8
  %44 = load i32, ptr %24, align 4
  %45 = load i32, ptr %25, align 4
  %46 = sub i32 %44, %33
  %47 = mul i32 %46, %40
  %48 = add i32 %.0115199, %47
  %49 = mul i32 %48, %45
  %50 = sext i32 %49 to i64
  %51 = getelementptr i32, ptr %43, i64 %50
  %52 = load i32, ptr %51, align 4
  %53 = sitofp i32 %52 to float
  %54 = fmul reassoc ninf nsz float %42, %53
  %55 = add i32 %49, 1
  %56 = sext i32 %55 to i64
  %57 = getelementptr i32, ptr %43, i64 %56
  %58 = load i32, ptr %57, align 4
  %59 = sitofp i32 %58 to float
  %60 = fmul reassoc ninf nsz float %42, %59
  %61 = add i32 %49, 2
  %62 = sext i32 %61 to i64
  %63 = getelementptr i32, ptr %43, i64 %62
  %64 = load i32, ptr %63, align 4
  %65 = sitofp i32 %64 to float
  %66 = fmul reassoc ninf nsz float %42, %65
  %67 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %68 = load i32, ptr %67, align 4
  %69 = icmp sgt i32 %68, 0
  br i1 %69, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %70 = load ptr, ptr %20, align 8
  %71 = getelementptr i8, ptr %70, i64 4
  %72 = load float, ptr %71, align 4
  %73 = add i32 %40, -1
  %74 = tail call i32 @llvm.abs.i32(i32 %73, i1 true)
  %75 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %76 = load i32, ptr %75, align 4
  %77 = add i32 %76, -1
  %78 = sub i32 %74, %77
  %79 = tail call i32 @llvm.smax.i32(i32 %78, i32 0)
  %80 = shl nuw i32 %79, 1
  %81 = sub i32 %74, %80
  %82 = tail call i32 @llvm.smax.i32(i32 %81, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %77, i32 %82)
  %84 = add i32 %40, 1
  %85 = tail call i32 @llvm.abs.i32(i32 %84, i1 true)
  %86 = sub i32 %85, %77
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = shl nuw i32 %87, 1
  %89 = sub i32 %85, %88
  %90 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %91 = tail call i32 @llvm.smin.i32(i32 %77, i32 %90)
  %92 = mul i32 %83, %44
  %93 = sub i32 %92, %41
  %94 = add i32 %.0115199, %93
  %95 = mul i32 %94, %45
  %96 = sext i32 %95 to i64
  %97 = getelementptr i32, ptr %43, i64 %96
  %98 = load i32, ptr %97, align 4
  %99 = mul i32 %91, %44
  %100 = sub i32 %99, %41
  %101 = add i32 %.0115199, %100
  %102 = mul i32 %101, %45
  %103 = sext i32 %102 to i64
  %104 = getelementptr i32, ptr %43, i64 %103
  %105 = load i32, ptr %104, align 4
  %106 = add i32 %105, %98
  %107 = sitofp i32 %106 to float
  %108 = fmul reassoc ninf nsz float %72, %107
  %109 = fadd reassoc ninf nsz float %108, %54
  %110 = add i32 %95, 1
  %111 = sext i32 %110 to i64
  %112 = getelementptr i32, ptr %43, i64 %111
  %113 = load i32, ptr %112, align 4
  %114 = add i32 %102, 1
  %115 = sext i32 %114 to i64
  %116 = getelementptr i32, ptr %43, i64 %115
  %117 = load i32, ptr %116, align 4
  %118 = add i32 %117, %113
  %119 = sitofp i32 %118 to float
  %120 = fmul reassoc ninf nsz float %72, %119
  %121 = fadd reassoc ninf nsz float %120, %60
  %122 = add i32 %95, 2
  %123 = sext i32 %122 to i64
  %124 = getelementptr i32, ptr %43, i64 %123
  %125 = load i32, ptr %124, align 4
  %126 = add i32 %102, 2
  %127 = sext i32 %126 to i64
  %128 = getelementptr i32, ptr %43, i64 %127
  %129 = load i32, ptr %128, align 4
  %130 = add i32 %129, %125
  %131 = sitofp i32 %130 to float
  %132 = fmul reassoc ninf nsz float %72, %131
  %133 = fadd reassoc ninf nsz float %132, %66
  %factor = fmul reassoc ninf nsz float %72, 2.000000e+00
  %134 = fadd reassoc ninf nsz float %factor, %42
  %.not = icmp eq i32 %68, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %135 = getelementptr i8, ptr %70, i64 8
  %136 = load float, ptr %135, align 4
  %137 = add i32 %40, -2
  %138 = tail call i32 @llvm.abs.i32(i32 %137, i1 true)
  %139 = sub i32 %138, %77
  %140 = tail call i32 @llvm.smax.i32(i32 %139, i32 0)
  %141 = shl nuw i32 %140, 1
  %142 = sub i32 %138, %141
  %143 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %144 = tail call i32 @llvm.smin.i32(i32 %77, i32 %143)
  %145 = add i32 %40, 2
  %146 = tail call i32 @llvm.abs.i32(i32 %145, i1 true)
  %147 = sub i32 %146, %77
  %148 = tail call i32 @llvm.smax.i32(i32 %147, i32 0)
  %149 = shl nuw i32 %148, 1
  %150 = sub i32 %146, %149
  %151 = tail call i32 @llvm.smax.i32(i32 %150, i32 0)
  %152 = tail call i32 @llvm.smin.i32(i32 %77, i32 %151)
  %153 = mul i32 %144, %44
  %154 = sub i32 %153, %41
  %155 = add i32 %.0115199, %154
  %156 = mul i32 %155, %45
  %157 = sext i32 %156 to i64
  %158 = getelementptr i32, ptr %43, i64 %157
  %159 = load i32, ptr %158, align 4
  %160 = mul i32 %152, %44
  %161 = sub i32 %160, %41
  %162 = add i32 %.0115199, %161
  %163 = mul i32 %162, %45
  %164 = sext i32 %163 to i64
  %165 = getelementptr i32, ptr %43, i64 %164
  %166 = load i32, ptr %165, align 4
  %167 = add i32 %166, %159
  %168 = sitofp i32 %167 to float
  %169 = fmul reassoc ninf nsz float %136, %168
  %170 = fadd reassoc ninf nsz float %169, %109
  %171 = add i32 %156, 1
  %172 = sext i32 %171 to i64
  %173 = getelementptr i32, ptr %43, i64 %172
  %174 = load i32, ptr %173, align 4
  %175 = add i32 %163, 1
  %176 = sext i32 %175 to i64
  %177 = getelementptr i32, ptr %43, i64 %176
  %178 = load i32, ptr %177, align 4
  %179 = add i32 %178, %174
  %180 = sitofp i32 %179 to float
  %181 = fmul reassoc ninf nsz float %136, %180
  %182 = fadd reassoc ninf nsz float %181, %121
  %183 = add i32 %156, 2
  %184 = sext i32 %183 to i64
  %185 = getelementptr i32, ptr %43, i64 %184
  %186 = load i32, ptr %185, align 4
  %187 = add i32 %163, 2
  %188 = sext i32 %187 to i64
  %189 = getelementptr i32, ptr %43, i64 %188
  %190 = load i32, ptr %189, align 4
  %191 = add i32 %190, %186
  %192 = sitofp i32 %191 to float
  %193 = fmul reassoc ninf nsz float %136, %192
  %194 = fadd reassoc ninf nsz float %193, %133
  %factor184 = fmul reassoc ninf nsz float %136, 2.000000e+00
  %195 = fadd reassoc ninf nsz float %factor184, %134
  %196 = icmp samesign ugt i32 %68, 2
  br i1 %196, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %197 = getelementptr i8, ptr %70, i64 12
  %198 = load float, ptr %197, align 4
  %199 = add i32 %40, -3
  %200 = tail call i32 @llvm.abs.i32(i32 %199, i1 true)
  %201 = sub i32 %200, %77
  %202 = tail call i32 @llvm.smax.i32(i32 %201, i32 0)
  %203 = shl nuw i32 %202, 1
  %204 = sub i32 %200, %203
  %205 = tail call i32 @llvm.smax.i32(i32 %204, i32 0)
  %206 = tail call i32 @llvm.smin.i32(i32 %77, i32 %205)
  %207 = add i32 %40, 3
  %208 = tail call i32 @llvm.abs.i32(i32 %207, i1 true)
  %209 = sub i32 %208, %77
  %210 = tail call i32 @llvm.smax.i32(i32 %209, i32 0)
  %211 = shl nuw i32 %210, 1
  %212 = sub i32 %208, %211
  %213 = tail call i32 @llvm.smax.i32(i32 %212, i32 0)
  %214 = tail call i32 @llvm.smin.i32(i32 %77, i32 %213)
  %215 = mul i32 %206, %44
  %216 = sub i32 %215, %41
  %217 = add i32 %.0115199, %216
  %218 = mul i32 %217, %45
  %219 = sext i32 %218 to i64
  %220 = getelementptr i32, ptr %43, i64 %219
  %221 = load i32, ptr %220, align 4
  %222 = mul i32 %214, %44
  %223 = sub i32 %222, %41
  %224 = add i32 %.0115199, %223
  %225 = mul i32 %224, %45
  %226 = sext i32 %225 to i64
  %227 = getelementptr i32, ptr %43, i64 %226
  %228 = load i32, ptr %227, align 4
  %229 = add i32 %228, %221
  %230 = sitofp i32 %229 to float
  %231 = fmul reassoc ninf nsz float %198, %230
  %232 = fadd reassoc ninf nsz float %231, %170
  %233 = add i32 %218, 1
  %234 = sext i32 %233 to i64
  %235 = getelementptr i32, ptr %43, i64 %234
  %236 = load i32, ptr %235, align 4
  %237 = add i32 %225, 1
  %238 = sext i32 %237 to i64
  %239 = getelementptr i32, ptr %43, i64 %238
  %240 = load i32, ptr %239, align 4
  %241 = add i32 %240, %236
  %242 = sitofp i32 %241 to float
  %243 = fmul reassoc ninf nsz float %198, %242
  %244 = fadd reassoc ninf nsz float %243, %182
  %245 = add i32 %218, 2
  %246 = sext i32 %245 to i64
  %247 = getelementptr i32, ptr %43, i64 %246
  %248 = load i32, ptr %247, align 4
  %249 = add i32 %225, 2
  %250 = sext i32 %249 to i64
  %251 = getelementptr i32, ptr %43, i64 %250
  %252 = load i32, ptr %251, align 4
  %253 = add i32 %252, %248
  %254 = sitofp i32 %253 to float
  %255 = fmul reassoc ninf nsz float %198, %254
  %256 = fadd reassoc ninf nsz float %255, %194
  %factor185 = fmul reassoc ninf nsz float %198, 2.000000e+00
  %257 = fadd reassoc ninf nsz float %factor185, %195
  %.not177 = icmp eq i32 %68, 3
  br i1 %.not177, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %258 = getelementptr i8, ptr %70, i64 16
  %259 = load float, ptr %258, align 4
  %260 = add i32 %40, -4
  %261 = tail call i32 @llvm.abs.i32(i32 %260, i1 true)
  %262 = sub i32 %261, %77
  %263 = tail call i32 @llvm.smax.i32(i32 %262, i32 0)
  %264 = shl nuw i32 %263, 1
  %265 = sub i32 %261, %264
  %266 = tail call i32 @llvm.smax.i32(i32 %265, i32 0)
  %267 = tail call i32 @llvm.smin.i32(i32 %77, i32 %266)
  %268 = add i32 %40, 4
  %269 = tail call i32 @llvm.abs.i32(i32 %268, i1 true)
  %270 = sub i32 %269, %77
  %271 = tail call i32 @llvm.smax.i32(i32 %270, i32 0)
  %272 = shl nuw i32 %271, 1
  %273 = sub i32 %269, %272
  %274 = tail call i32 @llvm.smax.i32(i32 %273, i32 0)
  %275 = tail call i32 @llvm.smin.i32(i32 %77, i32 %274)
  %276 = mul i32 %267, %44
  %277 = sub i32 %276, %41
  %278 = add i32 %.0115199, %277
  %279 = mul i32 %278, %45
  %280 = sext i32 %279 to i64
  %281 = getelementptr i32, ptr %43, i64 %280
  %282 = load i32, ptr %281, align 4
  %283 = mul i32 %275, %44
  %284 = sub i32 %283, %41
  %285 = add i32 %.0115199, %284
  %286 = mul i32 %285, %45
  %287 = sext i32 %286 to i64
  %288 = getelementptr i32, ptr %43, i64 %287
  %289 = load i32, ptr %288, align 4
  %290 = add i32 %289, %282
  %291 = sitofp i32 %290 to float
  %292 = fmul reassoc ninf nsz float %259, %291
  %293 = fadd reassoc ninf nsz float %292, %232
  %294 = add i32 %279, 1
  %295 = sext i32 %294 to i64
  %296 = getelementptr i32, ptr %43, i64 %295
  %297 = load i32, ptr %296, align 4
  %298 = add i32 %286, 1
  %299 = sext i32 %298 to i64
  %300 = getelementptr i32, ptr %43, i64 %299
  %301 = load i32, ptr %300, align 4
  %302 = add i32 %301, %297
  %303 = sitofp i32 %302 to float
  %304 = fmul reassoc ninf nsz float %259, %303
  %305 = fadd reassoc ninf nsz float %304, %244
  %306 = add i32 %279, 2
  %307 = sext i32 %306 to i64
  %308 = getelementptr i32, ptr %43, i64 %307
  %309 = load i32, ptr %308, align 4
  %310 = add i32 %286, 2
  %311 = sext i32 %310 to i64
  %312 = getelementptr i32, ptr %43, i64 %311
  %313 = load i32, ptr %312, align 4
  %314 = add i32 %313, %309
  %315 = sitofp i32 %314 to float
  %316 = fmul reassoc ninf nsz float %259, %315
  %317 = fadd reassoc ninf nsz float %316, %256
  %factor186 = fmul reassoc ninf nsz float %259, 2.000000e+00
  %318 = fadd reassoc ninf nsz float %factor186, %257
  %319 = icmp samesign ugt i32 %68, 4
  br i1 %319, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %320 = getelementptr i8, ptr %70, i64 20
  %321 = load float, ptr %320, align 4
  %322 = add i32 %40, -5
  %323 = tail call i32 @llvm.abs.i32(i32 %322, i1 true)
  %324 = sub i32 %323, %77
  %325 = tail call i32 @llvm.smax.i32(i32 %324, i32 0)
  %326 = shl nuw i32 %325, 1
  %327 = sub i32 %323, %326
  %328 = tail call i32 @llvm.smax.i32(i32 %327, i32 0)
  %329 = tail call i32 @llvm.smin.i32(i32 %77, i32 %328)
  %330 = add i32 %40, 5
  %331 = tail call i32 @llvm.abs.i32(i32 %330, i1 true)
  %332 = sub i32 %331, %77
  %333 = tail call i32 @llvm.smax.i32(i32 %332, i32 0)
  %334 = shl nuw i32 %333, 1
  %335 = sub i32 %331, %334
  %336 = tail call i32 @llvm.smax.i32(i32 %335, i32 0)
  %337 = tail call i32 @llvm.smin.i32(i32 %77, i32 %336)
  %338 = mul i32 %329, %44
  %339 = sub i32 %338, %41
  %340 = add i32 %.0115199, %339
  %341 = mul i32 %340, %45
  %342 = sext i32 %341 to i64
  %343 = getelementptr i32, ptr %43, i64 %342
  %344 = load i32, ptr %343, align 4
  %345 = mul i32 %337, %44
  %346 = sub i32 %345, %41
  %347 = add i32 %.0115199, %346
  %348 = mul i32 %347, %45
  %349 = sext i32 %348 to i64
  %350 = getelementptr i32, ptr %43, i64 %349
  %351 = load i32, ptr %350, align 4
  %352 = add i32 %351, %344
  %353 = sitofp i32 %352 to float
  %354 = fmul reassoc ninf nsz float %321, %353
  %355 = fadd reassoc ninf nsz float %354, %293
  %356 = add i32 %341, 1
  %357 = sext i32 %356 to i64
  %358 = getelementptr i32, ptr %43, i64 %357
  %359 = load i32, ptr %358, align 4
  %360 = add i32 %348, 1
  %361 = sext i32 %360 to i64
  %362 = getelementptr i32, ptr %43, i64 %361
  %363 = load i32, ptr %362, align 4
  %364 = add i32 %363, %359
  %365 = sitofp i32 %364 to float
  %366 = fmul reassoc ninf nsz float %321, %365
  %367 = fadd reassoc ninf nsz float %366, %305
  %368 = add i32 %341, 2
  %369 = sext i32 %368 to i64
  %370 = getelementptr i32, ptr %43, i64 %369
  %371 = load i32, ptr %370, align 4
  %372 = add i32 %348, 2
  %373 = sext i32 %372 to i64
  %374 = getelementptr i32, ptr %43, i64 %373
  %375 = load i32, ptr %374, align 4
  %376 = add i32 %375, %371
  %377 = sitofp i32 %376 to float
  %378 = fmul reassoc ninf nsz float %321, %377
  %379 = fadd reassoc ninf nsz float %378, %317
  %factor187 = fmul reassoc ninf nsz float %321, 2.000000e+00
  %380 = fadd reassoc ninf nsz float %factor187, %318
  %.not178 = icmp eq i32 %68, 5
  br i1 %.not178, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %381 = getelementptr i8, ptr %70, i64 24
  %382 = load float, ptr %381, align 4
  %383 = add i32 %40, -6
  %384 = tail call i32 @llvm.abs.i32(i32 %383, i1 true)
  %385 = sub i32 %384, %77
  %386 = tail call i32 @llvm.smax.i32(i32 %385, i32 0)
  %387 = shl nuw i32 %386, 1
  %388 = sub i32 %384, %387
  %389 = tail call i32 @llvm.smax.i32(i32 %388, i32 0)
  %390 = tail call i32 @llvm.smin.i32(i32 %77, i32 %389)
  %391 = add i32 %40, 6
  %392 = tail call i32 @llvm.abs.i32(i32 %391, i1 true)
  %393 = sub i32 %392, %77
  %394 = tail call i32 @llvm.smax.i32(i32 %393, i32 0)
  %395 = shl nuw i32 %394, 1
  %396 = sub i32 %392, %395
  %397 = tail call i32 @llvm.smax.i32(i32 %396, i32 0)
  %398 = tail call i32 @llvm.smin.i32(i32 %77, i32 %397)
  %399 = mul i32 %390, %44
  %400 = sub i32 %399, %41
  %401 = add i32 %.0115199, %400
  %402 = mul i32 %401, %45
  %403 = sext i32 %402 to i64
  %404 = getelementptr i32, ptr %43, i64 %403
  %405 = load i32, ptr %404, align 4
  %406 = mul i32 %398, %44
  %407 = sub i32 %406, %41
  %408 = add i32 %.0115199, %407
  %409 = mul i32 %408, %45
  %410 = sext i32 %409 to i64
  %411 = getelementptr i32, ptr %43, i64 %410
  %412 = load i32, ptr %411, align 4
  %413 = add i32 %412, %405
  %414 = sitofp i32 %413 to float
  %415 = fmul reassoc ninf nsz float %382, %414
  %416 = fadd reassoc ninf nsz float %415, %355
  %417 = add i32 %402, 1
  %418 = sext i32 %417 to i64
  %419 = getelementptr i32, ptr %43, i64 %418
  %420 = load i32, ptr %419, align 4
  %421 = add i32 %409, 1
  %422 = sext i32 %421 to i64
  %423 = getelementptr i32, ptr %43, i64 %422
  %424 = load i32, ptr %423, align 4
  %425 = add i32 %424, %420
  %426 = sitofp i32 %425 to float
  %427 = fmul reassoc ninf nsz float %382, %426
  %428 = fadd reassoc ninf nsz float %427, %367
  %429 = add i32 %402, 2
  %430 = sext i32 %429 to i64
  %431 = getelementptr i32, ptr %43, i64 %430
  %432 = load i32, ptr %431, align 4
  %433 = add i32 %409, 2
  %434 = sext i32 %433 to i64
  %435 = getelementptr i32, ptr %43, i64 %434
  %436 = load i32, ptr %435, align 4
  %437 = add i32 %436, %432
  %438 = sitofp i32 %437 to float
  %439 = fmul reassoc ninf nsz float %382, %438
  %440 = fadd reassoc ninf nsz float %439, %379
  %factor188 = fmul reassoc ninf nsz float %382, 2.000000e+00
  %441 = fadd reassoc ninf nsz float %factor188, %380
  %442 = icmp samesign ugt i32 %68, 6
  br i1 %442, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %443 = getelementptr i8, ptr %70, i64 28
  %444 = load float, ptr %443, align 4
  %445 = add i32 %40, -7
  %446 = tail call i32 @llvm.abs.i32(i32 %445, i1 true)
  %447 = sub i32 %446, %77
  %448 = tail call i32 @llvm.smax.i32(i32 %447, i32 0)
  %449 = shl nuw i32 %448, 1
  %450 = sub i32 %446, %449
  %451 = tail call i32 @llvm.smax.i32(i32 %450, i32 0)
  %452 = tail call i32 @llvm.smin.i32(i32 %77, i32 %451)
  %453 = add i32 %40, 7
  %454 = tail call i32 @llvm.abs.i32(i32 %453, i1 true)
  %455 = sub i32 %454, %77
  %456 = tail call i32 @llvm.smax.i32(i32 %455, i32 0)
  %457 = shl nuw i32 %456, 1
  %458 = sub i32 %454, %457
  %459 = tail call i32 @llvm.smax.i32(i32 %458, i32 0)
  %460 = tail call i32 @llvm.smin.i32(i32 %77, i32 %459)
  %461 = mul i32 %452, %44
  %462 = sub i32 %461, %41
  %463 = add i32 %.0115199, %462
  %464 = mul i32 %463, %45
  %465 = sext i32 %464 to i64
  %466 = getelementptr i32, ptr %43, i64 %465
  %467 = load i32, ptr %466, align 4
  %468 = mul i32 %460, %44
  %469 = sub i32 %468, %41
  %470 = add i32 %.0115199, %469
  %471 = mul i32 %470, %45
  %472 = sext i32 %471 to i64
  %473 = getelementptr i32, ptr %43, i64 %472
  %474 = load i32, ptr %473, align 4
  %475 = add i32 %474, %467
  %476 = sitofp i32 %475 to float
  %477 = fmul reassoc ninf nsz float %444, %476
  %478 = fadd reassoc ninf nsz float %477, %416
  %479 = add i32 %464, 1
  %480 = sext i32 %479 to i64
  %481 = getelementptr i32, ptr %43, i64 %480
  %482 = load i32, ptr %481, align 4
  %483 = add i32 %471, 1
  %484 = sext i32 %483 to i64
  %485 = getelementptr i32, ptr %43, i64 %484
  %486 = load i32, ptr %485, align 4
  %487 = add i32 %486, %482
  %488 = sitofp i32 %487 to float
  %489 = fmul reassoc ninf nsz float %444, %488
  %490 = fadd reassoc ninf nsz float %489, %428
  %491 = add i32 %464, 2
  %492 = sext i32 %491 to i64
  %493 = getelementptr i32, ptr %43, i64 %492
  %494 = load i32, ptr %493, align 4
  %495 = add i32 %471, 2
  %496 = sext i32 %495 to i64
  %497 = getelementptr i32, ptr %43, i64 %496
  %498 = load i32, ptr %497, align 4
  %499 = add i32 %498, %494
  %500 = sitofp i32 %499 to float
  %501 = fmul reassoc ninf nsz float %444, %500
  %502 = fadd reassoc ninf nsz float %501, %440
  %factor189 = fmul reassoc ninf nsz float %444, 2.000000e+00
  %503 = fadd reassoc ninf nsz float %factor189, %441
  %.not179 = icmp eq i32 %68, 7
  br i1 %.not179, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %504 = getelementptr i8, ptr %70, i64 32
  %505 = load float, ptr %504, align 4
  %506 = add i32 %40, -8
  %507 = tail call i32 @llvm.abs.i32(i32 %506, i1 true)
  %508 = sub i32 %507, %77
  %509 = tail call i32 @llvm.smax.i32(i32 %508, i32 0)
  %510 = shl nuw i32 %509, 1
  %511 = sub i32 %507, %510
  %512 = tail call i32 @llvm.smax.i32(i32 %511, i32 0)
  %513 = tail call i32 @llvm.smin.i32(i32 %77, i32 %512)
  %514 = add i32 %40, 8
  %515 = tail call i32 @llvm.abs.i32(i32 %514, i1 true)
  %516 = sub i32 %515, %77
  %517 = tail call i32 @llvm.smax.i32(i32 %516, i32 0)
  %518 = shl nuw i32 %517, 1
  %519 = sub i32 %515, %518
  %520 = tail call i32 @llvm.smax.i32(i32 %519, i32 0)
  %521 = tail call i32 @llvm.smin.i32(i32 %77, i32 %520)
  %522 = mul i32 %513, %44
  %523 = sub i32 %522, %41
  %524 = add i32 %.0115199, %523
  %525 = mul i32 %524, %45
  %526 = sext i32 %525 to i64
  %527 = getelementptr i32, ptr %43, i64 %526
  %528 = load i32, ptr %527, align 4
  %529 = mul i32 %521, %44
  %530 = sub i32 %529, %41
  %531 = add i32 %.0115199, %530
  %532 = mul i32 %531, %45
  %533 = sext i32 %532 to i64
  %534 = getelementptr i32, ptr %43, i64 %533
  %535 = load i32, ptr %534, align 4
  %536 = add i32 %535, %528
  %537 = sitofp i32 %536 to float
  %538 = fmul reassoc ninf nsz float %505, %537
  %539 = fadd reassoc ninf nsz float %538, %478
  %540 = add i32 %525, 1
  %541 = sext i32 %540 to i64
  %542 = getelementptr i32, ptr %43, i64 %541
  %543 = load i32, ptr %542, align 4
  %544 = add i32 %532, 1
  %545 = sext i32 %544 to i64
  %546 = getelementptr i32, ptr %43, i64 %545
  %547 = load i32, ptr %546, align 4
  %548 = add i32 %547, %543
  %549 = sitofp i32 %548 to float
  %550 = fmul reassoc ninf nsz float %505, %549
  %551 = fadd reassoc ninf nsz float %550, %490
  %552 = add i32 %525, 2
  %553 = sext i32 %552 to i64
  %554 = getelementptr i32, ptr %43, i64 %553
  %555 = load i32, ptr %554, align 4
  %556 = add i32 %532, 2
  %557 = sext i32 %556 to i64
  %558 = getelementptr i32, ptr %43, i64 %557
  %559 = load i32, ptr %558, align 4
  %560 = add i32 %559, %555
  %561 = sitofp i32 %560 to float
  %562 = fmul reassoc ninf nsz float %505, %561
  %563 = fadd reassoc ninf nsz float %562, %502
  %factor190 = fmul reassoc ninf nsz float %505, 2.000000e+00
  %564 = fadd reassoc ninf nsz float %factor190, %503
  %565 = icmp samesign ugt i32 %68, 8
  br i1 %565, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %566 = getelementptr i8, ptr %70, i64 36
  %567 = load float, ptr %566, align 4
  %568 = add i32 %40, -9
  %569 = tail call i32 @llvm.abs.i32(i32 %568, i1 true)
  %570 = sub i32 %569, %77
  %571 = tail call i32 @llvm.smax.i32(i32 %570, i32 0)
  %572 = shl nuw i32 %571, 1
  %573 = sub i32 %569, %572
  %574 = tail call i32 @llvm.smax.i32(i32 %573, i32 0)
  %575 = tail call i32 @llvm.smin.i32(i32 %77, i32 %574)
  %576 = add i32 %40, 9
  %577 = tail call i32 @llvm.abs.i32(i32 %576, i1 true)
  %578 = sub i32 %577, %77
  %579 = tail call i32 @llvm.smax.i32(i32 %578, i32 0)
  %580 = shl nuw i32 %579, 1
  %581 = sub i32 %577, %580
  %582 = tail call i32 @llvm.smax.i32(i32 %581, i32 0)
  %583 = tail call i32 @llvm.smin.i32(i32 %77, i32 %582)
  %584 = mul i32 %575, %44
  %585 = sub i32 %584, %41
  %586 = add i32 %.0115199, %585
  %587 = mul i32 %586, %45
  %588 = sext i32 %587 to i64
  %589 = getelementptr i32, ptr %43, i64 %588
  %590 = load i32, ptr %589, align 4
  %591 = mul i32 %583, %44
  %592 = sub i32 %591, %41
  %593 = add i32 %.0115199, %592
  %594 = mul i32 %593, %45
  %595 = sext i32 %594 to i64
  %596 = getelementptr i32, ptr %43, i64 %595
  %597 = load i32, ptr %596, align 4
  %598 = add i32 %597, %590
  %599 = sitofp i32 %598 to float
  %600 = fmul reassoc ninf nsz float %567, %599
  %601 = fadd reassoc ninf nsz float %600, %539
  %602 = add i32 %587, 1
  %603 = sext i32 %602 to i64
  %604 = getelementptr i32, ptr %43, i64 %603
  %605 = load i32, ptr %604, align 4
  %606 = add i32 %594, 1
  %607 = sext i32 %606 to i64
  %608 = getelementptr i32, ptr %43, i64 %607
  %609 = load i32, ptr %608, align 4
  %610 = add i32 %609, %605
  %611 = sitofp i32 %610 to float
  %612 = fmul reassoc ninf nsz float %567, %611
  %613 = fadd reassoc ninf nsz float %612, %551
  %614 = add i32 %587, 2
  %615 = sext i32 %614 to i64
  %616 = getelementptr i32, ptr %43, i64 %615
  %617 = load i32, ptr %616, align 4
  %618 = add i32 %594, 2
  %619 = sext i32 %618 to i64
  %620 = getelementptr i32, ptr %43, i64 %619
  %621 = load i32, ptr %620, align 4
  %622 = add i32 %621, %617
  %623 = sitofp i32 %622 to float
  %624 = fmul reassoc ninf nsz float %567, %623
  %625 = fadd reassoc ninf nsz float %624, %563
  %factor191 = fmul reassoc ninf nsz float %567, 2.000000e+00
  %626 = fadd reassoc ninf nsz float %factor191, %564
  %.not180 = icmp eq i32 %68, 9
  br i1 %.not180, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %627 = getelementptr i8, ptr %70, i64 40
  %628 = load float, ptr %627, align 4
  %629 = add i32 %40, -10
  %630 = tail call i32 @llvm.abs.i32(i32 %629, i1 true)
  %631 = sub i32 %630, %77
  %632 = tail call i32 @llvm.smax.i32(i32 %631, i32 0)
  %633 = shl nuw i32 %632, 1
  %634 = sub i32 %630, %633
  %635 = tail call i32 @llvm.smax.i32(i32 %634, i32 0)
  %636 = tail call i32 @llvm.smin.i32(i32 %77, i32 %635)
  %637 = add i32 %40, 10
  %638 = tail call i32 @llvm.abs.i32(i32 %637, i1 true)
  %639 = sub i32 %638, %77
  %640 = tail call i32 @llvm.smax.i32(i32 %639, i32 0)
  %641 = shl nuw i32 %640, 1
  %642 = sub i32 %638, %641
  %643 = tail call i32 @llvm.smax.i32(i32 %642, i32 0)
  %644 = tail call i32 @llvm.smin.i32(i32 %77, i32 %643)
  %645 = mul i32 %636, %44
  %646 = sub i32 %645, %41
  %647 = add i32 %.0115199, %646
  %648 = mul i32 %647, %45
  %649 = sext i32 %648 to i64
  %650 = getelementptr i32, ptr %43, i64 %649
  %651 = load i32, ptr %650, align 4
  %652 = mul i32 %644, %44
  %653 = sub i32 %652, %41
  %654 = add i32 %.0115199, %653
  %655 = mul i32 %654, %45
  %656 = sext i32 %655 to i64
  %657 = getelementptr i32, ptr %43, i64 %656
  %658 = load i32, ptr %657, align 4
  %659 = add i32 %658, %651
  %660 = sitofp i32 %659 to float
  %661 = fmul reassoc ninf nsz float %628, %660
  %662 = fadd reassoc ninf nsz float %661, %601
  %663 = add i32 %648, 1
  %664 = sext i32 %663 to i64
  %665 = getelementptr i32, ptr %43, i64 %664
  %666 = load i32, ptr %665, align 4
  %667 = add i32 %655, 1
  %668 = sext i32 %667 to i64
  %669 = getelementptr i32, ptr %43, i64 %668
  %670 = load i32, ptr %669, align 4
  %671 = add i32 %670, %666
  %672 = sitofp i32 %671 to float
  %673 = fmul reassoc ninf nsz float %628, %672
  %674 = fadd reassoc ninf nsz float %673, %613
  %675 = add i32 %648, 2
  %676 = sext i32 %675 to i64
  %677 = getelementptr i32, ptr %43, i64 %676
  %678 = load i32, ptr %677, align 4
  %679 = add i32 %655, 2
  %680 = sext i32 %679 to i64
  %681 = getelementptr i32, ptr %43, i64 %680
  %682 = load i32, ptr %681, align 4
  %683 = add i32 %682, %678
  %684 = sitofp i32 %683 to float
  %685 = fmul reassoc ninf nsz float %628, %684
  %686 = fadd reassoc ninf nsz float %685, %625
  %factor192 = fmul reassoc ninf nsz float %628, 2.000000e+00
  %687 = fadd reassoc ninf nsz float %factor192, %626
  %688 = icmp samesign ugt i32 %68, 10
  br i1 %688, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %689 = getelementptr i8, ptr %70, i64 44
  %690 = load float, ptr %689, align 4
  %691 = add i32 %40, -11
  %692 = tail call i32 @llvm.abs.i32(i32 %691, i1 true)
  %693 = sub i32 %692, %77
  %694 = tail call i32 @llvm.smax.i32(i32 %693, i32 0)
  %695 = shl nuw i32 %694, 1
  %696 = sub i32 %692, %695
  %697 = tail call i32 @llvm.smax.i32(i32 %696, i32 0)
  %698 = tail call i32 @llvm.smin.i32(i32 %77, i32 %697)
  %699 = add i32 %40, 11
  %700 = tail call i32 @llvm.abs.i32(i32 %699, i1 true)
  %701 = sub i32 %700, %77
  %702 = tail call i32 @llvm.smax.i32(i32 %701, i32 0)
  %703 = shl nuw i32 %702, 1
  %704 = sub i32 %700, %703
  %705 = tail call i32 @llvm.smax.i32(i32 %704, i32 0)
  %706 = tail call i32 @llvm.smin.i32(i32 %77, i32 %705)
  %707 = mul i32 %698, %44
  %708 = sub i32 %707, %41
  %709 = add i32 %.0115199, %708
  %710 = mul i32 %709, %45
  %711 = sext i32 %710 to i64
  %712 = getelementptr i32, ptr %43, i64 %711
  %713 = load i32, ptr %712, align 4
  %714 = mul i32 %706, %44
  %715 = sub i32 %714, %41
  %716 = add i32 %.0115199, %715
  %717 = mul i32 %716, %45
  %718 = sext i32 %717 to i64
  %719 = getelementptr i32, ptr %43, i64 %718
  %720 = load i32, ptr %719, align 4
  %721 = add i32 %720, %713
  %722 = sitofp i32 %721 to float
  %723 = fmul reassoc ninf nsz float %690, %722
  %724 = fadd reassoc ninf nsz float %723, %662
  %725 = add i32 %710, 1
  %726 = sext i32 %725 to i64
  %727 = getelementptr i32, ptr %43, i64 %726
  %728 = load i32, ptr %727, align 4
  %729 = add i32 %717, 1
  %730 = sext i32 %729 to i64
  %731 = getelementptr i32, ptr %43, i64 %730
  %732 = load i32, ptr %731, align 4
  %733 = add i32 %732, %728
  %734 = sitofp i32 %733 to float
  %735 = fmul reassoc ninf nsz float %690, %734
  %736 = fadd reassoc ninf nsz float %735, %674
  %737 = add i32 %710, 2
  %738 = sext i32 %737 to i64
  %739 = getelementptr i32, ptr %43, i64 %738
  %740 = load i32, ptr %739, align 4
  %741 = add i32 %717, 2
  %742 = sext i32 %741 to i64
  %743 = getelementptr i32, ptr %43, i64 %742
  %744 = load i32, ptr %743, align 4
  %745 = add i32 %744, %740
  %746 = sitofp i32 %745 to float
  %747 = fmul reassoc ninf nsz float %690, %746
  %748 = fadd reassoc ninf nsz float %747, %686
  %factor193 = fmul reassoc ninf nsz float %690, 2.000000e+00
  %749 = fadd reassoc ninf nsz float %factor193, %687
  %.not181 = icmp eq i32 %68, 11
  br i1 %.not181, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %750 = getelementptr i8, ptr %70, i64 48
  %751 = load float, ptr %750, align 4
  %752 = add i32 %40, -12
  %753 = tail call i32 @llvm.abs.i32(i32 %752, i1 true)
  %754 = sub i32 %753, %77
  %755 = tail call i32 @llvm.smax.i32(i32 %754, i32 0)
  %756 = shl nuw i32 %755, 1
  %757 = sub i32 %753, %756
  %758 = tail call i32 @llvm.smax.i32(i32 %757, i32 0)
  %759 = tail call i32 @llvm.smin.i32(i32 %77, i32 %758)
  %760 = add i32 %40, 12
  %761 = tail call i32 @llvm.abs.i32(i32 %760, i1 true)
  %762 = sub i32 %761, %77
  %763 = tail call i32 @llvm.smax.i32(i32 %762, i32 0)
  %764 = shl nuw i32 %763, 1
  %765 = sub i32 %761, %764
  %766 = tail call i32 @llvm.smax.i32(i32 %765, i32 0)
  %767 = tail call i32 @llvm.smin.i32(i32 %77, i32 %766)
  %768 = mul i32 %759, %44
  %769 = sub i32 %768, %41
  %770 = add i32 %.0115199, %769
  %771 = mul i32 %770, %45
  %772 = sext i32 %771 to i64
  %773 = getelementptr i32, ptr %43, i64 %772
  %774 = load i32, ptr %773, align 4
  %775 = mul i32 %767, %44
  %776 = sub i32 %775, %41
  %777 = add i32 %.0115199, %776
  %778 = mul i32 %777, %45
  %779 = sext i32 %778 to i64
  %780 = getelementptr i32, ptr %43, i64 %779
  %781 = load i32, ptr %780, align 4
  %782 = add i32 %781, %774
  %783 = sitofp i32 %782 to float
  %784 = fmul reassoc ninf nsz float %751, %783
  %785 = fadd reassoc ninf nsz float %784, %724
  %786 = add i32 %771, 1
  %787 = sext i32 %786 to i64
  %788 = getelementptr i32, ptr %43, i64 %787
  %789 = load i32, ptr %788, align 4
  %790 = add i32 %778, 1
  %791 = sext i32 %790 to i64
  %792 = getelementptr i32, ptr %43, i64 %791
  %793 = load i32, ptr %792, align 4
  %794 = add i32 %793, %789
  %795 = sitofp i32 %794 to float
  %796 = fmul reassoc ninf nsz float %751, %795
  %797 = fadd reassoc ninf nsz float %796, %736
  %798 = add i32 %771, 2
  %799 = sext i32 %798 to i64
  %800 = getelementptr i32, ptr %43, i64 %799
  %801 = load i32, ptr %800, align 4
  %802 = add i32 %778, 2
  %803 = sext i32 %802 to i64
  %804 = getelementptr i32, ptr %43, i64 %803
  %805 = load i32, ptr %804, align 4
  %806 = add i32 %805, %801
  %807 = sitofp i32 %806 to float
  %808 = fmul reassoc ninf nsz float %751, %807
  %809 = fadd reassoc ninf nsz float %808, %748
  %factor194 = fmul reassoc ninf nsz float %751, 2.000000e+00
  %810 = fadd reassoc ninf nsz float %factor194, %749
  %811 = icmp samesign ugt i32 %68, 12
  br i1 %811, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %812 = getelementptr i8, ptr %70, i64 52
  %813 = load float, ptr %812, align 4
  %814 = add i32 %40, -13
  %815 = tail call i32 @llvm.abs.i32(i32 %814, i1 true)
  %816 = sub i32 %815, %77
  %817 = tail call i32 @llvm.smax.i32(i32 %816, i32 0)
  %818 = shl nuw i32 %817, 1
  %819 = sub i32 %815, %818
  %820 = tail call i32 @llvm.smax.i32(i32 %819, i32 0)
  %821 = tail call i32 @llvm.smin.i32(i32 %77, i32 %820)
  %822 = add i32 %40, 13
  %823 = tail call i32 @llvm.abs.i32(i32 %822, i1 true)
  %824 = sub i32 %823, %77
  %825 = tail call i32 @llvm.smax.i32(i32 %824, i32 0)
  %826 = shl nuw i32 %825, 1
  %827 = sub i32 %823, %826
  %828 = tail call i32 @llvm.smax.i32(i32 %827, i32 0)
  %829 = tail call i32 @llvm.smin.i32(i32 %77, i32 %828)
  %830 = mul i32 %821, %44
  %831 = sub i32 %830, %41
  %832 = add i32 %.0115199, %831
  %833 = mul i32 %832, %45
  %834 = sext i32 %833 to i64
  %835 = getelementptr i32, ptr %43, i64 %834
  %836 = load i32, ptr %835, align 4
  %837 = mul i32 %829, %44
  %838 = sub i32 %837, %41
  %839 = add i32 %.0115199, %838
  %840 = mul i32 %839, %45
  %841 = sext i32 %840 to i64
  %842 = getelementptr i32, ptr %43, i64 %841
  %843 = load i32, ptr %842, align 4
  %844 = add i32 %843, %836
  %845 = sitofp i32 %844 to float
  %846 = fmul reassoc ninf nsz float %813, %845
  %847 = fadd reassoc ninf nsz float %846, %785
  %848 = add i32 %833, 1
  %849 = sext i32 %848 to i64
  %850 = getelementptr i32, ptr %43, i64 %849
  %851 = load i32, ptr %850, align 4
  %852 = add i32 %840, 1
  %853 = sext i32 %852 to i64
  %854 = getelementptr i32, ptr %43, i64 %853
  %855 = load i32, ptr %854, align 4
  %856 = add i32 %855, %851
  %857 = sitofp i32 %856 to float
  %858 = fmul reassoc ninf nsz float %813, %857
  %859 = fadd reassoc ninf nsz float %858, %797
  %860 = add i32 %833, 2
  %861 = sext i32 %860 to i64
  %862 = getelementptr i32, ptr %43, i64 %861
  %863 = load i32, ptr %862, align 4
  %864 = add i32 %840, 2
  %865 = sext i32 %864 to i64
  %866 = getelementptr i32, ptr %43, i64 %865
  %867 = load i32, ptr %866, align 4
  %868 = add i32 %867, %863
  %869 = sitofp i32 %868 to float
  %870 = fmul reassoc ninf nsz float %813, %869
  %871 = fadd reassoc ninf nsz float %870, %809
  %factor195 = fmul reassoc ninf nsz float %813, 2.000000e+00
  %872 = fadd reassoc ninf nsz float %factor195, %810
  %.not182 = icmp eq i32 %68, 13
  br i1 %.not182, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %873 = getelementptr i8, ptr %70, i64 56
  %874 = load float, ptr %873, align 4
  %875 = add i32 %40, -14
  %876 = tail call i32 @llvm.abs.i32(i32 %875, i1 true)
  %877 = sub i32 %876, %77
  %878 = tail call i32 @llvm.smax.i32(i32 %877, i32 0)
  %879 = shl nuw i32 %878, 1
  %880 = sub i32 %876, %879
  %881 = tail call i32 @llvm.smax.i32(i32 %880, i32 0)
  %882 = tail call i32 @llvm.smin.i32(i32 %77, i32 %881)
  %883 = add i32 %40, 14
  %884 = tail call i32 @llvm.abs.i32(i32 %883, i1 true)
  %885 = sub i32 %884, %77
  %886 = tail call i32 @llvm.smax.i32(i32 %885, i32 0)
  %887 = shl nuw i32 %886, 1
  %888 = sub i32 %884, %887
  %889 = tail call i32 @llvm.smax.i32(i32 %888, i32 0)
  %890 = tail call i32 @llvm.smin.i32(i32 %77, i32 %889)
  %891 = mul i32 %882, %44
  %892 = sub i32 %891, %41
  %893 = add i32 %.0115199, %892
  %894 = mul i32 %893, %45
  %895 = sext i32 %894 to i64
  %896 = getelementptr i32, ptr %43, i64 %895
  %897 = load i32, ptr %896, align 4
  %898 = mul i32 %890, %44
  %899 = sub i32 %898, %41
  %900 = add i32 %.0115199, %899
  %901 = mul i32 %900, %45
  %902 = sext i32 %901 to i64
  %903 = getelementptr i32, ptr %43, i64 %902
  %904 = load i32, ptr %903, align 4
  %905 = add i32 %904, %897
  %906 = sitofp i32 %905 to float
  %907 = fmul reassoc ninf nsz float %874, %906
  %908 = fadd reassoc ninf nsz float %907, %847
  %909 = add i32 %894, 1
  %910 = sext i32 %909 to i64
  %911 = getelementptr i32, ptr %43, i64 %910
  %912 = load i32, ptr %911, align 4
  %913 = add i32 %901, 1
  %914 = sext i32 %913 to i64
  %915 = getelementptr i32, ptr %43, i64 %914
  %916 = load i32, ptr %915, align 4
  %917 = add i32 %916, %912
  %918 = sitofp i32 %917 to float
  %919 = fmul reassoc ninf nsz float %874, %918
  %920 = fadd reassoc ninf nsz float %919, %859
  %921 = add i32 %894, 2
  %922 = sext i32 %921 to i64
  %923 = getelementptr i32, ptr %43, i64 %922
  %924 = load i32, ptr %923, align 4
  %925 = add i32 %901, 2
  %926 = sext i32 %925 to i64
  %927 = getelementptr i32, ptr %43, i64 %926
  %928 = load i32, ptr %927, align 4
  %929 = add i32 %928, %924
  %930 = sitofp i32 %929 to float
  %931 = fmul reassoc ninf nsz float %874, %930
  %932 = fadd reassoc ninf nsz float %931, %871
  %factor196 = fmul reassoc ninf nsz float %874, 2.000000e+00
  %933 = fadd reassoc ninf nsz float %factor196, %872
  %934 = icmp samesign ugt i32 %68, 14
  br i1 %934, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %935 = getelementptr i8, ptr %70, i64 60
  %936 = load float, ptr %935, align 4
  %937 = add i32 %40, -15
  %938 = tail call i32 @llvm.abs.i32(i32 %937, i1 true)
  %939 = sub i32 %938, %77
  %940 = tail call i32 @llvm.smax.i32(i32 %939, i32 0)
  %941 = shl nuw i32 %940, 1
  %942 = sub i32 %938, %941
  %943 = tail call i32 @llvm.smax.i32(i32 %942, i32 0)
  %944 = tail call i32 @llvm.smin.i32(i32 %77, i32 %943)
  %945 = add i32 %40, 15
  %946 = tail call i32 @llvm.abs.i32(i32 %945, i1 true)
  %947 = sub i32 %946, %77
  %948 = tail call i32 @llvm.smax.i32(i32 %947, i32 0)
  %949 = shl nuw i32 %948, 1
  %950 = sub i32 %946, %949
  %951 = tail call i32 @llvm.smax.i32(i32 %950, i32 0)
  %952 = tail call i32 @llvm.smin.i32(i32 %77, i32 %951)
  %953 = mul i32 %944, %44
  %954 = sub i32 %953, %41
  %955 = add i32 %.0115199, %954
  %956 = mul i32 %955, %45
  %957 = sext i32 %956 to i64
  %958 = getelementptr i32, ptr %43, i64 %957
  %959 = load i32, ptr %958, align 4
  %960 = mul i32 %952, %44
  %961 = sub i32 %960, %41
  %962 = add i32 %.0115199, %961
  %963 = mul i32 %962, %45
  %964 = sext i32 %963 to i64
  %965 = getelementptr i32, ptr %43, i64 %964
  %966 = load i32, ptr %965, align 4
  %967 = add i32 %966, %959
  %968 = sitofp i32 %967 to float
  %969 = fmul reassoc ninf nsz float %936, %968
  %970 = fadd reassoc ninf nsz float %969, %908
  %971 = add i32 %956, 1
  %972 = sext i32 %971 to i64
  %973 = getelementptr i32, ptr %43, i64 %972
  %974 = load i32, ptr %973, align 4
  %975 = add i32 %963, 1
  %976 = sext i32 %975 to i64
  %977 = getelementptr i32, ptr %43, i64 %976
  %978 = load i32, ptr %977, align 4
  %979 = add i32 %978, %974
  %980 = sitofp i32 %979 to float
  %981 = fmul reassoc ninf nsz float %936, %980
  %982 = fadd reassoc ninf nsz float %981, %920
  %983 = add i32 %956, 2
  %984 = sext i32 %983 to i64
  %985 = getelementptr i32, ptr %43, i64 %984
  %986 = load i32, ptr %985, align 4
  %987 = add i32 %963, 2
  %988 = sext i32 %987 to i64
  %989 = getelementptr i32, ptr %43, i64 %988
  %990 = load i32, ptr %989, align 4
  %991 = add i32 %990, %986
  %992 = sitofp i32 %991 to float
  %993 = fmul reassoc ninf nsz float %936, %992
  %994 = fadd reassoc ninf nsz float %993, %932
  %factor197 = fmul reassoc ninf nsz float %936, 2.000000e+00
  %995 = fadd reassoc ninf nsz float %factor197, %933
  %.not183 = icmp eq i32 %68, 15
  br i1 %.not183, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %996 = getelementptr i8, ptr %70, i64 64
  %997 = load float, ptr %996, align 4
  %998 = add i32 %40, -16
  %999 = tail call i32 @llvm.abs.i32(i32 %998, i1 true)
  %1000 = sub i32 %999, %77
  %1001 = tail call i32 @llvm.smax.i32(i32 %1000, i32 0)
  %1002 = shl nuw i32 %1001, 1
  %1003 = sub i32 %999, %1002
  %1004 = tail call i32 @llvm.smax.i32(i32 %1003, i32 0)
  %1005 = tail call i32 @llvm.smin.i32(i32 %77, i32 %1004)
  %1006 = add i32 %40, 16
  %1007 = tail call i32 @llvm.abs.i32(i32 %1006, i1 true)
  %1008 = sub i32 %1007, %77
  %1009 = tail call i32 @llvm.smax.i32(i32 %1008, i32 0)
  %1010 = shl nuw i32 %1009, 1
  %1011 = sub i32 %1007, %1010
  %1012 = tail call i32 @llvm.smax.i32(i32 %1011, i32 0)
  %1013 = tail call i32 @llvm.smin.i32(i32 %77, i32 %1012)
  %1014 = mul i32 %1005, %44
  %1015 = sub i32 %1014, %41
  %1016 = add i32 %.0115199, %1015
  %1017 = mul i32 %1016, %45
  %1018 = sext i32 %1017 to i64
  %1019 = getelementptr i32, ptr %43, i64 %1018
  %1020 = load i32, ptr %1019, align 4
  %1021 = mul i32 %1013, %44
  %1022 = sub i32 %1021, %41
  %1023 = add i32 %.0115199, %1022
  %1024 = mul i32 %1023, %45
  %1025 = sext i32 %1024 to i64
  %1026 = getelementptr i32, ptr %43, i64 %1025
  %1027 = load i32, ptr %1026, align 4
  %1028 = add i32 %1027, %1020
  %1029 = sitofp i32 %1028 to float
  %1030 = fmul reassoc ninf nsz float %997, %1029
  %1031 = fadd reassoc ninf nsz float %1030, %970
  %1032 = add i32 %1017, 1
  %1033 = sext i32 %1032 to i64
  %1034 = getelementptr i32, ptr %43, i64 %1033
  %1035 = load i32, ptr %1034, align 4
  %1036 = add i32 %1024, 1
  %1037 = sext i32 %1036 to i64
  %1038 = getelementptr i32, ptr %43, i64 %1037
  %1039 = load i32, ptr %1038, align 4
  %1040 = add i32 %1039, %1035
  %1041 = sitofp i32 %1040 to float
  %1042 = fmul reassoc ninf nsz float %997, %1041
  %1043 = fadd reassoc ninf nsz float %1042, %982
  %1044 = add i32 %1017, 2
  %1045 = sext i32 %1044 to i64
  %1046 = getelementptr i32, ptr %43, i64 %1045
  %1047 = load i32, ptr %1046, align 4
  %1048 = add i32 %1024, 2
  %1049 = sext i32 %1048 to i64
  %1050 = getelementptr i32, ptr %43, i64 %1049
  %1051 = load i32, ptr %1050, align 4
  %1052 = add i32 %1051, %1047
  %1053 = sitofp i32 %1052 to float
  %1054 = fmul reassoc ninf nsz float %997, %1053
  %1055 = fadd reassoc ninf nsz float %1054, %994
  %factor198 = fmul reassoc ninf nsz float %997, 2.000000e+00
  %1056 = fadd reassoc ninf nsz float %factor198, %995
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.15114 = phi float [ %1031, %true_block43 ], [ %970, %after_if42 ], [ %908, %after_if39 ], [ %847, %after_if36 ], [ %785, %after_if33 ], [ %724, %after_if30 ], [ %662, %after_if27 ], [ %601, %after_if24 ], [ %539, %after_if21 ], [ %478, %after_if18 ], [ %416, %after_if15 ], [ %355, %after_if12 ], [ %293, %after_if9 ], [ %232, %after_if6 ], [ %170, %after_if3 ], [ %109, %after_if ], [ %54, %for_loop_body ]
  %.1598 = phi float [ %1043, %true_block43 ], [ %982, %after_if42 ], [ %920, %after_if39 ], [ %859, %after_if36 ], [ %797, %after_if33 ], [ %736, %after_if30 ], [ %674, %after_if27 ], [ %613, %after_if24 ], [ %551, %after_if21 ], [ %490, %after_if18 ], [ %428, %after_if15 ], [ %367, %after_if12 ], [ %305, %after_if9 ], [ %244, %after_if6 ], [ %182, %after_if3 ], [ %121, %after_if ], [ %60, %for_loop_body ]
  %.1582 = phi float [ %1055, %true_block43 ], [ %994, %after_if42 ], [ %932, %after_if39 ], [ %871, %after_if36 ], [ %809, %after_if33 ], [ %748, %after_if30 ], [ %686, %after_if27 ], [ %625, %after_if24 ], [ %563, %after_if21 ], [ %502, %after_if18 ], [ %440, %after_if15 ], [ %379, %after_if12 ], [ %317, %after_if9 ], [ %256, %after_if6 ], [ %194, %after_if3 ], [ %133, %after_if ], [ %66, %for_loop_body ]
  %.15 = phi float [ %1056, %true_block43 ], [ %995, %after_if42 ], [ %933, %after_if39 ], [ %872, %after_if36 ], [ %810, %after_if33 ], [ %749, %after_if30 ], [ %687, %after_if27 ], [ %626, %after_if24 ], [ %564, %after_if21 ], [ %503, %after_if18 ], [ %441, %after_if15 ], [ %380, %after_if12 ], [ %318, %after_if9 ], [ %257, %after_if6 ], [ %195, %after_if3 ], [ %134, %after_if ], [ %42, %for_loop_body ]
  %1057 = fdiv reassoc ninf nsz float %.15114, %.15
  %1058 = load ptr, ptr %26, align 8
  %1059 = load i32, ptr %27, align 4
  %1060 = load i32, ptr %28, align 4
  %1061 = sub i32 %1059, %33
  %1062 = mul i32 %1061, %40
  %1063 = add i32 %.0115199, %1062
  %1064 = mul i32 %1063, %1060
  %1065 = sext i32 %1064 to i64
  %1066 = getelementptr i32, ptr %1058, i64 %1065
  %1067 = fptosi float %1057 to i32
  store i32 %1067, ptr %1066, align 4
  %1068 = fdiv reassoc ninf nsz float %.1598, %.15
  %1069 = load ptr, ptr %26, align 8
  %1070 = load i32, ptr %27, align 4
  %1071 = load i32, ptr %28, align 4
  %1072 = sub i32 %1070, %33
  %1073 = mul i32 %1072, %40
  %1074 = add i32 %.0115199, %1073
  %1075 = mul i32 %1074, %1071
  %1076 = add i32 %1075, 1
  %1077 = sext i32 %1076 to i64
  %1078 = getelementptr i32, ptr %1069, i64 %1077
  %1079 = fptosi float %1068 to i32
  store i32 %1079, ptr %1078, align 4
  %1080 = fdiv reassoc ninf nsz float %.1582, %.15
  %1081 = load ptr, ptr %26, align 8
  %1082 = load i32, ptr %27, align 4
  %1083 = load i32, ptr %28, align 4
  %1084 = sub i32 %1082, %33
  %1085 = mul i32 %1084, %40
  %1086 = add i32 %.0115199, %1085
  %1087 = mul i32 %1086, %1083
  %1088 = add i32 %1087, 2
  %1089 = sext i32 %1088 to i64
  %1090 = getelementptr i32, ptr %1081, i64 %1089
  %1091 = fptosi float %1080 to i32
  store i32 %1091, ptr %1090, align 4
  %1092 = add nsw i32 %.0115199, 1
  %exitcond.not = icmp eq i32 %18, %1092
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.13, align 8
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
