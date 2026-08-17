; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gaussian_blur_y_1ch_f32_kernel_c202_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 36
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

define void @_gaussian_blur_y_1ch_f32_kernel_c202_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 48
  %23 = load ptr, ptr %22, align 8
  %24 = icmp sgt i32 %21, 0
  %25 = icmp sgt i32 %21, 1
  %26 = icmp sgt i32 %21, 2
  %27 = icmp sgt i32 %21, 3
  %28 = icmp sgt i32 %21, 4
  %29 = icmp sgt i32 %21, 5
  %30 = icmp sgt i32 %21, 6
  %31 = icmp sgt i32 %21, 7
  %32 = icmp sgt i32 %21, 8
  %33 = icmp sgt i32 %21, 9
  %34 = icmp sgt i32 %21, 10
  %35 = icmp sgt i32 %21, 11
  %36 = icmp sgt i32 %21, 12
  %37 = icmp sgt i32 %21, 13
  %38 = icmp sgt i32 %21, 14
  %39 = icmp sgt i32 %21, 15
  %40 = icmp slt i32 %16, %18
  br i1 %40, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %41 = getelementptr i8, ptr %19, i64 8
  %42 = getelementptr i8, ptr %19, i64 4
  %43 = getelementptr i8, ptr %19, i64 24
  %44 = getelementptr i8, ptr %19, i64 20
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.05198 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %624, %after_if45 ]
  %45 = load ptr, ptr %3, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 32872
  %47 = load ptr, ptr %46, align 8
  %48 = getelementptr inbounds nuw i8, ptr %47, i64 4
  %49 = load i32, ptr %48, align 4
  %50 = sdiv i32 %.05198, %49
  %51 = mul i32 %50, %49
  %52 = xor i32 %49, %.05198
  %53 = icmp slt i32 %52, 0
  %54 = icmp ne i32 %.05198, %51
  %55 = and i1 %53, %54
  %.neg52 = sext i1 %55 to i32
  %56 = add i32 %50, %.neg52
  %57 = mul i32 %56, %49
  %58 = load float, ptr %23, align 4
  %59 = load ptr, ptr %41, align 8
  %60 = load i32, ptr %42, align 4
  %61 = sub i32 %60, %49
  %62 = mul i32 %61, %56
  %63 = add i32 %.05198, %62
  %64 = sext i32 %63 to i64
  %65 = getelementptr float, ptr %59, i64 %64
  %66 = load float, ptr %65, align 4
  %67 = fmul reassoc ninf nsz float %66, %58
  br i1 %24, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %68 = load ptr, ptr %22, align 8
  %69 = getelementptr i8, ptr %68, i64 4
  %70 = load float, ptr %69, align 4
  %71 = add i32 %56, -1
  %72 = tail call i32 @llvm.abs.i32(i32 %71, i1 true)
  %73 = getelementptr inbounds nuw i8, ptr %47, i64 8
  %74 = load i32, ptr %73, align 4
  %75 = add i32 %74, -1
  %76 = sub i32 %72, %75
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = shl nuw i32 %77, 1
  %79 = sub i32 %72, %78
  %80 = add i32 %56, 1
  %81 = tail call i32 @llvm.abs.i32(i32 %80, i1 true)
  %82 = sub i32 %81, %75
  %83 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %84 = shl nuw i32 %83, 1
  %85 = sub i32 %81, %84
  %86 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %87 = tail call i32 @llvm.smin.i32(i32 %75, i32 %86)
  %88 = mul i32 %87, %60
  %89 = sub i32 %88, %57
  %90 = add i32 %.05198, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %59, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %75, i32 %94)
  %96 = mul i32 %95, %60
  %97 = sub i32 %96, %57
  %98 = add i32 %.05198, %97
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %59, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = fadd reassoc ninf nsz float %101, %93
  %103 = fmul reassoc ninf nsz float %102, %70
  %104 = fadd reassoc ninf nsz float %103, %67
  %factor = fmul reassoc ninf nsz float %70, 2.000000e+00
  %105 = fadd reassoc ninf nsz float %factor, %58
  br i1 %25, label %after_if3, label %after_if45

after_if3:                                        ; preds = %after_if
  %106 = getelementptr i8, ptr %68, i64 8
  %107 = load float, ptr %106, align 4
  %108 = add i32 %56, -2
  %109 = tail call i32 @llvm.abs.i32(i32 %108, i1 true)
  %110 = sub i32 %109, %75
  %111 = tail call i32 @llvm.smax.i32(i32 %110, i32 0)
  %112 = shl nuw i32 %111, 1
  %113 = sub i32 %109, %112
  %114 = add i32 %56, 2
  %115 = tail call i32 @llvm.abs.i32(i32 %114, i1 true)
  %116 = sub i32 %115, %75
  %117 = tail call i32 @llvm.smax.i32(i32 %116, i32 0)
  %118 = shl nuw i32 %117, 1
  %119 = sub i32 %115, %118
  %120 = tail call i32 @llvm.smax.i32(i32 %113, i32 0)
  %121 = tail call i32 @llvm.smin.i32(i32 %75, i32 %120)
  %122 = mul i32 %121, %60
  %123 = sub i32 %122, %57
  %124 = add i32 %.05198, %123
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %59, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = tail call i32 @llvm.smax.i32(i32 %119, i32 0)
  %129 = tail call i32 @llvm.smin.i32(i32 %75, i32 %128)
  %130 = mul i32 %129, %60
  %131 = sub i32 %130, %57
  %132 = add i32 %.05198, %131
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %59, i64 %133
  %135 = load float, ptr %134, align 4
  %136 = fadd reassoc ninf nsz float %135, %127
  %137 = fmul reassoc ninf nsz float %136, %107
  %138 = fadd reassoc ninf nsz float %137, %104
  %factor83 = fmul reassoc ninf nsz float %107, 2.000000e+00
  %139 = fadd reassoc ninf nsz float %factor83, %105
  br i1 %26, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %140 = getelementptr i8, ptr %68, i64 12
  %141 = load float, ptr %140, align 4
  %142 = add i32 %56, -3
  %143 = tail call i32 @llvm.abs.i32(i32 %142, i1 true)
  %144 = sub i32 %143, %75
  %145 = tail call i32 @llvm.smax.i32(i32 %144, i32 0)
  %146 = shl nuw i32 %145, 1
  %147 = sub i32 %143, %146
  %148 = add i32 %56, 3
  %149 = tail call i32 @llvm.abs.i32(i32 %148, i1 true)
  %150 = sub i32 %149, %75
  %151 = tail call i32 @llvm.smax.i32(i32 %150, i32 0)
  %152 = shl nuw i32 %151, 1
  %153 = sub i32 %149, %152
  %154 = tail call i32 @llvm.smax.i32(i32 %147, i32 0)
  %155 = tail call i32 @llvm.smin.i32(i32 %75, i32 %154)
  %156 = mul i32 %155, %60
  %157 = sub i32 %156, %57
  %158 = add i32 %.05198, %157
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %59, i64 %159
  %161 = load float, ptr %160, align 4
  %162 = tail call i32 @llvm.smax.i32(i32 %153, i32 0)
  %163 = tail call i32 @llvm.smin.i32(i32 %75, i32 %162)
  %164 = mul i32 %163, %60
  %165 = sub i32 %164, %57
  %166 = add i32 %.05198, %165
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, ptr %59, i64 %167
  %169 = load float, ptr %168, align 4
  %170 = fadd reassoc ninf nsz float %169, %161
  %171 = fmul reassoc ninf nsz float %170, %141
  %172 = fadd reassoc ninf nsz float %171, %138
  %factor84 = fmul reassoc ninf nsz float %141, 2.000000e+00
  %173 = fadd reassoc ninf nsz float %factor84, %139
  br i1 %27, label %after_if9, label %after_if45

after_if9:                                        ; preds = %after_if6
  %174 = getelementptr i8, ptr %68, i64 16
  %175 = load float, ptr %174, align 4
  %176 = add i32 %56, -4
  %177 = tail call i32 @llvm.abs.i32(i32 %176, i1 true)
  %178 = sub i32 %177, %75
  %179 = tail call i32 @llvm.smax.i32(i32 %178, i32 0)
  %180 = shl nuw i32 %179, 1
  %181 = sub i32 %177, %180
  %182 = add i32 %56, 4
  %183 = tail call i32 @llvm.abs.i32(i32 %182, i1 true)
  %184 = sub i32 %183, %75
  %185 = tail call i32 @llvm.smax.i32(i32 %184, i32 0)
  %186 = shl nuw i32 %185, 1
  %187 = sub i32 %183, %186
  %188 = tail call i32 @llvm.smax.i32(i32 %181, i32 0)
  %189 = tail call i32 @llvm.smin.i32(i32 %75, i32 %188)
  %190 = mul i32 %189, %60
  %191 = sub i32 %190, %57
  %192 = add i32 %.05198, %191
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, ptr %59, i64 %193
  %195 = load float, ptr %194, align 4
  %196 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %197 = tail call i32 @llvm.smin.i32(i32 %75, i32 %196)
  %198 = mul i32 %197, %60
  %199 = sub i32 %198, %57
  %200 = add i32 %.05198, %199
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, ptr %59, i64 %201
  %203 = load float, ptr %202, align 4
  %204 = fadd reassoc ninf nsz float %203, %195
  %205 = fmul reassoc ninf nsz float %204, %175
  %206 = fadd reassoc ninf nsz float %205, %172
  %factor85 = fmul reassoc ninf nsz float %175, 2.000000e+00
  %207 = fadd reassoc ninf nsz float %factor85, %173
  br i1 %28, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %208 = getelementptr i8, ptr %68, i64 20
  %209 = load float, ptr %208, align 4
  %210 = add i32 %56, -5
  %211 = tail call i32 @llvm.abs.i32(i32 %210, i1 true)
  %212 = sub i32 %211, %75
  %213 = tail call i32 @llvm.smax.i32(i32 %212, i32 0)
  %214 = shl nuw i32 %213, 1
  %215 = sub i32 %211, %214
  %216 = add i32 %56, 5
  %217 = tail call i32 @llvm.abs.i32(i32 %216, i1 true)
  %218 = sub i32 %217, %75
  %219 = tail call i32 @llvm.smax.i32(i32 %218, i32 0)
  %220 = shl nuw i32 %219, 1
  %221 = sub i32 %217, %220
  %222 = tail call i32 @llvm.smax.i32(i32 %215, i32 0)
  %223 = tail call i32 @llvm.smin.i32(i32 %75, i32 %222)
  %224 = mul i32 %223, %60
  %225 = sub i32 %224, %57
  %226 = add i32 %.05198, %225
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %59, i64 %227
  %229 = load float, ptr %228, align 4
  %230 = tail call i32 @llvm.smax.i32(i32 %221, i32 0)
  %231 = tail call i32 @llvm.smin.i32(i32 %75, i32 %230)
  %232 = mul i32 %231, %60
  %233 = sub i32 %232, %57
  %234 = add i32 %.05198, %233
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %59, i64 %235
  %237 = load float, ptr %236, align 4
  %238 = fadd reassoc ninf nsz float %237, %229
  %239 = fmul reassoc ninf nsz float %238, %209
  %240 = fadd reassoc ninf nsz float %239, %206
  %factor86 = fmul reassoc ninf nsz float %209, 2.000000e+00
  %241 = fadd reassoc ninf nsz float %factor86, %207
  br i1 %29, label %after_if15, label %after_if45

after_if15:                                       ; preds = %after_if12
  %242 = getelementptr i8, ptr %68, i64 24
  %243 = load float, ptr %242, align 4
  %244 = add i32 %56, -6
  %245 = tail call i32 @llvm.abs.i32(i32 %244, i1 true)
  %246 = sub i32 %245, %75
  %247 = tail call i32 @llvm.smax.i32(i32 %246, i32 0)
  %248 = shl nuw i32 %247, 1
  %249 = sub i32 %245, %248
  %250 = add i32 %56, 6
  %251 = tail call i32 @llvm.abs.i32(i32 %250, i1 true)
  %252 = sub i32 %251, %75
  %253 = tail call i32 @llvm.smax.i32(i32 %252, i32 0)
  %254 = shl nuw i32 %253, 1
  %255 = sub i32 %251, %254
  %256 = tail call i32 @llvm.smax.i32(i32 %249, i32 0)
  %257 = tail call i32 @llvm.smin.i32(i32 %75, i32 %256)
  %258 = mul i32 %257, %60
  %259 = sub i32 %258, %57
  %260 = add i32 %.05198, %259
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, ptr %59, i64 %261
  %263 = load float, ptr %262, align 4
  %264 = tail call i32 @llvm.smax.i32(i32 %255, i32 0)
  %265 = tail call i32 @llvm.smin.i32(i32 %75, i32 %264)
  %266 = mul i32 %265, %60
  %267 = sub i32 %266, %57
  %268 = add i32 %.05198, %267
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, ptr %59, i64 %269
  %271 = load float, ptr %270, align 4
  %272 = fadd reassoc ninf nsz float %271, %263
  %273 = fmul reassoc ninf nsz float %272, %243
  %274 = fadd reassoc ninf nsz float %273, %240
  %factor87 = fmul reassoc ninf nsz float %243, 2.000000e+00
  %275 = fadd reassoc ninf nsz float %factor87, %241
  br i1 %30, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %276 = getelementptr i8, ptr %68, i64 28
  %277 = load float, ptr %276, align 4
  %278 = add i32 %56, -7
  %279 = tail call i32 @llvm.abs.i32(i32 %278, i1 true)
  %280 = sub i32 %279, %75
  %281 = tail call i32 @llvm.smax.i32(i32 %280, i32 0)
  %282 = shl nuw i32 %281, 1
  %283 = sub i32 %279, %282
  %284 = add i32 %56, 7
  %285 = tail call i32 @llvm.abs.i32(i32 %284, i1 true)
  %286 = sub i32 %285, %75
  %287 = tail call i32 @llvm.smax.i32(i32 %286, i32 0)
  %288 = shl nuw i32 %287, 1
  %289 = sub i32 %285, %288
  %290 = tail call i32 @llvm.smax.i32(i32 %283, i32 0)
  %291 = tail call i32 @llvm.smin.i32(i32 %75, i32 %290)
  %292 = mul i32 %291, %60
  %293 = sub i32 %292, %57
  %294 = add i32 %.05198, %293
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, ptr %59, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = tail call i32 @llvm.smax.i32(i32 %289, i32 0)
  %299 = tail call i32 @llvm.smin.i32(i32 %75, i32 %298)
  %300 = mul i32 %299, %60
  %301 = sub i32 %300, %57
  %302 = add i32 %.05198, %301
  %303 = sext i32 %302 to i64
  %304 = getelementptr float, ptr %59, i64 %303
  %305 = load float, ptr %304, align 4
  %306 = fadd reassoc ninf nsz float %305, %297
  %307 = fmul reassoc ninf nsz float %306, %277
  %308 = fadd reassoc ninf nsz float %307, %274
  %factor88 = fmul reassoc ninf nsz float %277, 2.000000e+00
  %309 = fadd reassoc ninf nsz float %factor88, %275
  br i1 %31, label %after_if21, label %after_if45

after_if21:                                       ; preds = %after_if18
  %310 = getelementptr i8, ptr %68, i64 32
  %311 = load float, ptr %310, align 4
  %312 = add i32 %56, -8
  %313 = tail call i32 @llvm.abs.i32(i32 %312, i1 true)
  %314 = sub i32 %313, %75
  %315 = tail call i32 @llvm.smax.i32(i32 %314, i32 0)
  %316 = shl nuw i32 %315, 1
  %317 = sub i32 %313, %316
  %318 = add i32 %56, 8
  %319 = tail call i32 @llvm.abs.i32(i32 %318, i1 true)
  %320 = sub i32 %319, %75
  %321 = tail call i32 @llvm.smax.i32(i32 %320, i32 0)
  %322 = shl nuw i32 %321, 1
  %323 = sub i32 %319, %322
  %324 = tail call i32 @llvm.smax.i32(i32 %317, i32 0)
  %325 = tail call i32 @llvm.smin.i32(i32 %75, i32 %324)
  %326 = mul i32 %325, %60
  %327 = sub i32 %326, %57
  %328 = add i32 %.05198, %327
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, ptr %59, i64 %329
  %331 = load float, ptr %330, align 4
  %332 = tail call i32 @llvm.smax.i32(i32 %323, i32 0)
  %333 = tail call i32 @llvm.smin.i32(i32 %75, i32 %332)
  %334 = mul i32 %333, %60
  %335 = sub i32 %334, %57
  %336 = add i32 %.05198, %335
  %337 = sext i32 %336 to i64
  %338 = getelementptr float, ptr %59, i64 %337
  %339 = load float, ptr %338, align 4
  %340 = fadd reassoc ninf nsz float %339, %331
  %341 = fmul reassoc ninf nsz float %340, %311
  %342 = fadd reassoc ninf nsz float %341, %308
  %factor89 = fmul reassoc ninf nsz float %311, 2.000000e+00
  %343 = fadd reassoc ninf nsz float %factor89, %309
  br i1 %32, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %344 = getelementptr i8, ptr %68, i64 36
  %345 = load float, ptr %344, align 4
  %346 = add i32 %56, -9
  %347 = tail call i32 @llvm.abs.i32(i32 %346, i1 true)
  %348 = sub i32 %347, %75
  %349 = tail call i32 @llvm.smax.i32(i32 %348, i32 0)
  %350 = shl nuw i32 %349, 1
  %351 = sub i32 %347, %350
  %352 = add i32 %56, 9
  %353 = tail call i32 @llvm.abs.i32(i32 %352, i1 true)
  %354 = sub i32 %353, %75
  %355 = tail call i32 @llvm.smax.i32(i32 %354, i32 0)
  %356 = shl nuw i32 %355, 1
  %357 = sub i32 %353, %356
  %358 = tail call i32 @llvm.smax.i32(i32 %351, i32 0)
  %359 = tail call i32 @llvm.smin.i32(i32 %75, i32 %358)
  %360 = mul i32 %359, %60
  %361 = sub i32 %360, %57
  %362 = add i32 %.05198, %361
  %363 = sext i32 %362 to i64
  %364 = getelementptr float, ptr %59, i64 %363
  %365 = load float, ptr %364, align 4
  %366 = tail call i32 @llvm.smax.i32(i32 %357, i32 0)
  %367 = tail call i32 @llvm.smin.i32(i32 %75, i32 %366)
  %368 = mul i32 %367, %60
  %369 = sub i32 %368, %57
  %370 = add i32 %.05198, %369
  %371 = sext i32 %370 to i64
  %372 = getelementptr float, ptr %59, i64 %371
  %373 = load float, ptr %372, align 4
  %374 = fadd reassoc ninf nsz float %373, %365
  %375 = fmul reassoc ninf nsz float %374, %345
  %376 = fadd reassoc ninf nsz float %375, %342
  %factor90 = fmul reassoc ninf nsz float %345, 2.000000e+00
  %377 = fadd reassoc ninf nsz float %factor90, %343
  br i1 %33, label %after_if27, label %after_if45

after_if27:                                       ; preds = %after_if24
  %378 = getelementptr i8, ptr %68, i64 40
  %379 = load float, ptr %378, align 4
  %380 = add i32 %56, -10
  %381 = tail call i32 @llvm.abs.i32(i32 %380, i1 true)
  %382 = sub i32 %381, %75
  %383 = tail call i32 @llvm.smax.i32(i32 %382, i32 0)
  %384 = shl nuw i32 %383, 1
  %385 = sub i32 %381, %384
  %386 = add i32 %56, 10
  %387 = tail call i32 @llvm.abs.i32(i32 %386, i1 true)
  %388 = sub i32 %387, %75
  %389 = tail call i32 @llvm.smax.i32(i32 %388, i32 0)
  %390 = shl nuw i32 %389, 1
  %391 = sub i32 %387, %390
  %392 = tail call i32 @llvm.smax.i32(i32 %385, i32 0)
  %393 = tail call i32 @llvm.smin.i32(i32 %75, i32 %392)
  %394 = mul i32 %393, %60
  %395 = sub i32 %394, %57
  %396 = add i32 %.05198, %395
  %397 = sext i32 %396 to i64
  %398 = getelementptr float, ptr %59, i64 %397
  %399 = load float, ptr %398, align 4
  %400 = tail call i32 @llvm.smax.i32(i32 %391, i32 0)
  %401 = tail call i32 @llvm.smin.i32(i32 %75, i32 %400)
  %402 = mul i32 %401, %60
  %403 = sub i32 %402, %57
  %404 = add i32 %.05198, %403
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, ptr %59, i64 %405
  %407 = load float, ptr %406, align 4
  %408 = fadd reassoc ninf nsz float %407, %399
  %409 = fmul reassoc ninf nsz float %408, %379
  %410 = fadd reassoc ninf nsz float %409, %376
  %factor91 = fmul reassoc ninf nsz float %379, 2.000000e+00
  %411 = fadd reassoc ninf nsz float %factor91, %377
  br i1 %34, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %412 = getelementptr i8, ptr %68, i64 44
  %413 = load float, ptr %412, align 4
  %414 = add i32 %56, -11
  %415 = tail call i32 @llvm.abs.i32(i32 %414, i1 true)
  %416 = sub i32 %415, %75
  %417 = tail call i32 @llvm.smax.i32(i32 %416, i32 0)
  %418 = shl nuw i32 %417, 1
  %419 = sub i32 %415, %418
  %420 = add i32 %56, 11
  %421 = tail call i32 @llvm.abs.i32(i32 %420, i1 true)
  %422 = sub i32 %421, %75
  %423 = tail call i32 @llvm.smax.i32(i32 %422, i32 0)
  %424 = shl nuw i32 %423, 1
  %425 = sub i32 %421, %424
  %426 = tail call i32 @llvm.smax.i32(i32 %419, i32 0)
  %427 = tail call i32 @llvm.smin.i32(i32 %75, i32 %426)
  %428 = mul i32 %427, %60
  %429 = sub i32 %428, %57
  %430 = add i32 %.05198, %429
  %431 = sext i32 %430 to i64
  %432 = getelementptr float, ptr %59, i64 %431
  %433 = load float, ptr %432, align 4
  %434 = tail call i32 @llvm.smax.i32(i32 %425, i32 0)
  %435 = tail call i32 @llvm.smin.i32(i32 %75, i32 %434)
  %436 = mul i32 %435, %60
  %437 = sub i32 %436, %57
  %438 = add i32 %.05198, %437
  %439 = sext i32 %438 to i64
  %440 = getelementptr float, ptr %59, i64 %439
  %441 = load float, ptr %440, align 4
  %442 = fadd reassoc ninf nsz float %441, %433
  %443 = fmul reassoc ninf nsz float %442, %413
  %444 = fadd reassoc ninf nsz float %443, %410
  %factor92 = fmul reassoc ninf nsz float %413, 2.000000e+00
  %445 = fadd reassoc ninf nsz float %factor92, %411
  br i1 %35, label %after_if33, label %after_if45

after_if33:                                       ; preds = %after_if30
  %446 = getelementptr i8, ptr %68, i64 48
  %447 = load float, ptr %446, align 4
  %448 = add i32 %56, -12
  %449 = tail call i32 @llvm.abs.i32(i32 %448, i1 true)
  %450 = sub i32 %449, %75
  %451 = tail call i32 @llvm.smax.i32(i32 %450, i32 0)
  %452 = shl nuw i32 %451, 1
  %453 = sub i32 %449, %452
  %454 = add i32 %56, 12
  %455 = tail call i32 @llvm.abs.i32(i32 %454, i1 true)
  %456 = sub i32 %455, %75
  %457 = tail call i32 @llvm.smax.i32(i32 %456, i32 0)
  %458 = shl nuw i32 %457, 1
  %459 = sub i32 %455, %458
  %460 = tail call i32 @llvm.smax.i32(i32 %453, i32 0)
  %461 = tail call i32 @llvm.smin.i32(i32 %75, i32 %460)
  %462 = mul i32 %461, %60
  %463 = sub i32 %462, %57
  %464 = add i32 %.05198, %463
  %465 = sext i32 %464 to i64
  %466 = getelementptr float, ptr %59, i64 %465
  %467 = load float, ptr %466, align 4
  %468 = tail call i32 @llvm.smax.i32(i32 %459, i32 0)
  %469 = tail call i32 @llvm.smin.i32(i32 %75, i32 %468)
  %470 = mul i32 %469, %60
  %471 = sub i32 %470, %57
  %472 = add i32 %.05198, %471
  %473 = sext i32 %472 to i64
  %474 = getelementptr float, ptr %59, i64 %473
  %475 = load float, ptr %474, align 4
  %476 = fadd reassoc ninf nsz float %475, %467
  %477 = fmul reassoc ninf nsz float %476, %447
  %478 = fadd reassoc ninf nsz float %477, %444
  %factor93 = fmul reassoc ninf nsz float %447, 2.000000e+00
  %479 = fadd reassoc ninf nsz float %factor93, %445
  br i1 %36, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %480 = getelementptr i8, ptr %68, i64 52
  %481 = load float, ptr %480, align 4
  %482 = add i32 %56, -13
  %483 = tail call i32 @llvm.abs.i32(i32 %482, i1 true)
  %484 = sub i32 %483, %75
  %485 = tail call i32 @llvm.smax.i32(i32 %484, i32 0)
  %486 = shl nuw i32 %485, 1
  %487 = sub i32 %483, %486
  %488 = add i32 %56, 13
  %489 = tail call i32 @llvm.abs.i32(i32 %488, i1 true)
  %490 = sub i32 %489, %75
  %491 = tail call i32 @llvm.smax.i32(i32 %490, i32 0)
  %492 = shl nuw i32 %491, 1
  %493 = sub i32 %489, %492
  %494 = tail call i32 @llvm.smax.i32(i32 %487, i32 0)
  %495 = tail call i32 @llvm.smin.i32(i32 %75, i32 %494)
  %496 = mul i32 %495, %60
  %497 = sub i32 %496, %57
  %498 = add i32 %.05198, %497
  %499 = sext i32 %498 to i64
  %500 = getelementptr float, ptr %59, i64 %499
  %501 = load float, ptr %500, align 4
  %502 = tail call i32 @llvm.smax.i32(i32 %493, i32 0)
  %503 = tail call i32 @llvm.smin.i32(i32 %75, i32 %502)
  %504 = mul i32 %503, %60
  %505 = sub i32 %504, %57
  %506 = add i32 %.05198, %505
  %507 = sext i32 %506 to i64
  %508 = getelementptr float, ptr %59, i64 %507
  %509 = load float, ptr %508, align 4
  %510 = fadd reassoc ninf nsz float %509, %501
  %511 = fmul reassoc ninf nsz float %510, %481
  %512 = fadd reassoc ninf nsz float %511, %478
  %factor94 = fmul reassoc ninf nsz float %481, 2.000000e+00
  %513 = fadd reassoc ninf nsz float %factor94, %479
  br i1 %37, label %after_if39, label %after_if45

after_if39:                                       ; preds = %after_if36
  %514 = getelementptr i8, ptr %68, i64 56
  %515 = load float, ptr %514, align 4
  %516 = add i32 %56, -14
  %517 = tail call i32 @llvm.abs.i32(i32 %516, i1 true)
  %518 = sub i32 %517, %75
  %519 = tail call i32 @llvm.smax.i32(i32 %518, i32 0)
  %520 = shl nuw i32 %519, 1
  %521 = sub i32 %517, %520
  %522 = add i32 %56, 14
  %523 = tail call i32 @llvm.abs.i32(i32 %522, i1 true)
  %524 = sub i32 %523, %75
  %525 = tail call i32 @llvm.smax.i32(i32 %524, i32 0)
  %526 = shl nuw i32 %525, 1
  %527 = sub i32 %523, %526
  %528 = tail call i32 @llvm.smax.i32(i32 %521, i32 0)
  %529 = tail call i32 @llvm.smin.i32(i32 %75, i32 %528)
  %530 = mul i32 %529, %60
  %531 = sub i32 %530, %57
  %532 = add i32 %.05198, %531
  %533 = sext i32 %532 to i64
  %534 = getelementptr float, ptr %59, i64 %533
  %535 = load float, ptr %534, align 4
  %536 = tail call i32 @llvm.smax.i32(i32 %527, i32 0)
  %537 = tail call i32 @llvm.smin.i32(i32 %75, i32 %536)
  %538 = mul i32 %537, %60
  %539 = sub i32 %538, %57
  %540 = add i32 %.05198, %539
  %541 = sext i32 %540 to i64
  %542 = getelementptr float, ptr %59, i64 %541
  %543 = load float, ptr %542, align 4
  %544 = fadd reassoc ninf nsz float %543, %535
  %545 = fmul reassoc ninf nsz float %544, %515
  %546 = fadd reassoc ninf nsz float %545, %512
  %factor95 = fmul reassoc ninf nsz float %515, 2.000000e+00
  %547 = fadd reassoc ninf nsz float %factor95, %513
  br i1 %38, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %548 = getelementptr i8, ptr %68, i64 60
  %549 = load float, ptr %548, align 4
  %550 = add i32 %56, -15
  %551 = tail call i32 @llvm.abs.i32(i32 %550, i1 true)
  %552 = sub i32 %551, %75
  %553 = tail call i32 @llvm.smax.i32(i32 %552, i32 0)
  %554 = shl nuw i32 %553, 1
  %555 = sub i32 %551, %554
  %556 = add i32 %56, 15
  %557 = tail call i32 @llvm.abs.i32(i32 %556, i1 true)
  %558 = sub i32 %557, %75
  %559 = tail call i32 @llvm.smax.i32(i32 %558, i32 0)
  %560 = shl nuw i32 %559, 1
  %561 = sub i32 %557, %560
  %562 = tail call i32 @llvm.smax.i32(i32 %555, i32 0)
  %563 = tail call i32 @llvm.smin.i32(i32 %75, i32 %562)
  %564 = mul i32 %563, %60
  %565 = sub i32 %564, %57
  %566 = add i32 %.05198, %565
  %567 = sext i32 %566 to i64
  %568 = getelementptr float, ptr %59, i64 %567
  %569 = load float, ptr %568, align 4
  %570 = tail call i32 @llvm.smax.i32(i32 %561, i32 0)
  %571 = tail call i32 @llvm.smin.i32(i32 %75, i32 %570)
  %572 = mul i32 %571, %60
  %573 = sub i32 %572, %57
  %574 = add i32 %.05198, %573
  %575 = sext i32 %574 to i64
  %576 = getelementptr float, ptr %59, i64 %575
  %577 = load float, ptr %576, align 4
  %578 = fadd reassoc ninf nsz float %577, %569
  %579 = fmul reassoc ninf nsz float %578, %549
  %580 = fadd reassoc ninf nsz float %579, %546
  %factor96 = fmul reassoc ninf nsz float %549, 2.000000e+00
  %581 = fadd reassoc ninf nsz float %factor96, %547
  br i1 %39, label %true_block43, label %after_if45

true_block43:                                     ; preds = %after_if42
  %582 = getelementptr i8, ptr %68, i64 64
  %583 = load float, ptr %582, align 4
  %584 = add i32 %56, -16
  %585 = tail call i32 @llvm.abs.i32(i32 %584, i1 true)
  %586 = sub i32 %585, %75
  %587 = tail call i32 @llvm.smax.i32(i32 %586, i32 0)
  %588 = shl nuw i32 %587, 1
  %589 = sub i32 %585, %588
  %590 = add i32 %56, 16
  %591 = tail call i32 @llvm.abs.i32(i32 %590, i1 true)
  %592 = sub i32 %591, %75
  %593 = tail call i32 @llvm.smax.i32(i32 %592, i32 0)
  %594 = shl nuw i32 %593, 1
  %595 = sub i32 %591, %594
  %596 = tail call i32 @llvm.smax.i32(i32 %589, i32 0)
  %597 = tail call i32 @llvm.smin.i32(i32 %75, i32 %596)
  %598 = mul i32 %597, %60
  %599 = sub i32 %598, %57
  %600 = add i32 %.05198, %599
  %601 = sext i32 %600 to i64
  %602 = getelementptr float, ptr %59, i64 %601
  %603 = load float, ptr %602, align 4
  %604 = tail call i32 @llvm.smax.i32(i32 %595, i32 0)
  %605 = tail call i32 @llvm.smin.i32(i32 %75, i32 %604)
  %606 = mul i32 %605, %60
  %607 = sub i32 %606, %57
  %608 = add i32 %.05198, %607
  %609 = sext i32 %608 to i64
  %610 = getelementptr float, ptr %59, i64 %609
  %611 = load float, ptr %610, align 4
  %612 = fadd reassoc ninf nsz float %611, %603
  %613 = fmul reassoc ninf nsz float %612, %583
  %614 = fadd reassoc ninf nsz float %613, %580
  %factor97 = fmul reassoc ninf nsz float %583, 2.000000e+00
  %615 = fadd reassoc ninf nsz float %factor97, %581
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.1550 = phi float [ %614, %true_block43 ], [ %580, %after_if42 ], [ %546, %after_if39 ], [ %512, %after_if36 ], [ %478, %after_if33 ], [ %444, %after_if30 ], [ %410, %after_if27 ], [ %376, %after_if24 ], [ %342, %after_if21 ], [ %308, %after_if18 ], [ %274, %after_if15 ], [ %240, %after_if12 ], [ %206, %after_if9 ], [ %172, %after_if6 ], [ %138, %after_if3 ], [ %104, %after_if ], [ %67, %for_loop_body ]
  %.15 = phi float [ %615, %true_block43 ], [ %581, %after_if42 ], [ %547, %after_if39 ], [ %513, %after_if36 ], [ %479, %after_if33 ], [ %445, %after_if30 ], [ %411, %after_if27 ], [ %377, %after_if24 ], [ %343, %after_if21 ], [ %309, %after_if18 ], [ %275, %after_if15 ], [ %241, %after_if12 ], [ %207, %after_if9 ], [ %173, %after_if6 ], [ %139, %after_if3 ], [ %105, %after_if ], [ %58, %for_loop_body ]
  %616 = fdiv reassoc ninf nsz float %.1550, %.15
  %617 = load ptr, ptr %43, align 8
  %618 = load i32, ptr %44, align 4
  %619 = sub i32 %618, %49
  %620 = mul i32 %619, %56
  %621 = add i32 %.05198, %620
  %622 = sext i32 %621 to i64
  %623 = getelementptr float, ptr %617, i64 %622
  store float %616, ptr %623, align 4
  %624 = add nsw i32 %.05198, 1
  %exitcond.not = icmp eq i32 %18, %624
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.5, align 8
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
