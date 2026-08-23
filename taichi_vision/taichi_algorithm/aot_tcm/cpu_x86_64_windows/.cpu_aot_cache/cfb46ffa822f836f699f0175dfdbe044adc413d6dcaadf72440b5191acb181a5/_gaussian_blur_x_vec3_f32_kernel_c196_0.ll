; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gaussian_blur_x_vec3_f32_kernel_c196_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 36
  %4 = load i32, ptr %3, align 4
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 12
  store i32 %4, ptr %9, align 4
  %10 = load ptr, ptr %context, align 8
  %11 = getelementptr i8, ptr %10, i64 56
  %12 = load i32, ptr %11, align 4
  %13 = load ptr, ptr %5, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 8
  store i32 %12, ptr %16, align 4
  %17 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %18 = tail call i32 @llvm.smax.i32(i32 %4, i32 0)
  %19 = load ptr, ptr %5, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 32872
  %21 = load ptr, ptr %20, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 4
  store i32 %18, ptr %22, align 4
  %23 = mul i32 %18, %17
  %24 = load ptr, ptr %5, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 32872
  %26 = load ptr, ptr %25, align 8
  store i32 %23, ptr %26, align 4
  ret void
}

define void @_gaussian_blur_x_vec3_f32_kernel_c196_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %27 = sub i32 0, %18
  %28 = add i32 %16, 16
  %29 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %lsr.iv200 = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next201, %after_if45 ]
  %lsr.iv = phi i32 [ %28, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if45 ]
  %30 = add i32 %lsr.iv, -16
  %31 = load ptr, ptr %3, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 4
  %35 = load i32, ptr %34, align 4
  %36 = sdiv i32 %30, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %30
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %30, %37
  %41 = and i1 %39, %40
  %.neg116 = sext i1 %41 to i32
  %42 = add i32 %36, %.neg116
  %43 = load float, ptr %21, align 4
  %44 = load ptr, ptr %23, align 8
  %45 = load i32, ptr %24, align 4
  %46 = mul i32 %42, %45
  %47 = sub i32 %45, %35
  %48 = mul i32 %47, 3
  %49 = mul i32 %48, %42
  %50 = add i32 %lsr.iv200, %49
  %51 = sext i32 %50 to i64
  %52 = getelementptr float, ptr %44, i64 %51
  %53 = load float, ptr %52, align 4
  %54 = add i32 %50, 1
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, ptr %44, i64 %55
  %57 = load float, ptr %56, align 4
  %58 = add i32 %50, 2
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, ptr %44, i64 %59
  %61 = load float, ptr %60, align 4
  %62 = fmul reassoc ninf nsz float %53, %43
  %63 = fmul reassoc ninf nsz float %57, %43
  %64 = fmul reassoc ninf nsz float %61, %43
  %65 = getelementptr inbounds nuw i8, ptr %33, i64 8
  %66 = load i32, ptr %65, align 4
  %67 = icmp sgt i32 %66, 0
  br i1 %67, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %68 = load ptr, ptr %20, align 8
  %69 = getelementptr i8, ptr %68, i64 4
  %70 = load float, ptr %69, align 4
  %71 = mul i32 %35, -1
  %72 = mul i32 %71, %42
  %73 = add i32 %lsr.iv, %72
  %74 = add i32 %73, -17
  %75 = tail call i32 @llvm.abs.i32(i32 %74, i1 true)
  %76 = getelementptr inbounds nuw i8, ptr %33, i64 12
  %77 = load i32, ptr %76, align 4
  %78 = add i32 %77, -1
  %79 = sub i32 %75, %78
  %80 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %81 = shl nuw i32 %80, 1
  %82 = sub i32 %75, %81
  %83 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %78, i32 %83)
  %85 = add i32 %73, -15
  %86 = tail call i32 @llvm.abs.i32(i32 %85, i1 true)
  %87 = sub i32 %86, %78
  %88 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %89 = shl nuw i32 %88, 1
  %90 = sub i32 %86, %89
  %91 = tail call i32 @llvm.smax.i32(i32 %90, i32 0)
  %92 = tail call i32 @llvm.smin.i32(i32 %78, i32 %91)
  %93 = add i32 %84, %46
  %94 = mul i32 %93, 3
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, ptr %44, i64 %95
  %97 = load float, ptr %96, align 4
  %98 = add i32 %94, 1
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %44, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = add i32 %94, 2
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, ptr %44, i64 %103
  %105 = load float, ptr %104, align 4
  %106 = add i32 %92, %46
  %107 = mul i32 %106, 3
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %44, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = add i32 %107, 1
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %44, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = add i32 %107, 2
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %44, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = fadd reassoc ninf nsz float %110, %97
  %120 = fadd reassoc ninf nsz float %114, %101
  %121 = fadd reassoc ninf nsz float %118, %105
  %122 = fmul reassoc ninf nsz float %119, %70
  %123 = fmul reassoc ninf nsz float %120, %70
  %124 = fmul reassoc ninf nsz float %121, %70
  %125 = fadd reassoc ninf nsz float %122, %62
  %126 = fadd reassoc ninf nsz float %123, %63
  %127 = fadd reassoc ninf nsz float %124, %64
  %factor = fmul reassoc ninf nsz float %70, 2.000000e+00
  %128 = fadd reassoc ninf nsz float %factor, %43
  %.not = icmp eq i32 %66, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %129 = getelementptr i8, ptr %68, i64 8
  %130 = load float, ptr %129, align 4
  %131 = add i32 %73, -18
  %132 = tail call i32 @llvm.abs.i32(i32 %131, i1 true)
  %133 = sub i32 %132, %78
  %134 = tail call i32 @llvm.smax.i32(i32 %133, i32 0)
  %135 = shl nuw i32 %134, 1
  %136 = sub i32 %132, %135
  %137 = tail call i32 @llvm.smax.i32(i32 %136, i32 0)
  %138 = tail call i32 @llvm.smin.i32(i32 %78, i32 %137)
  %139 = add i32 %73, -14
  %140 = tail call i32 @llvm.abs.i32(i32 %139, i1 true)
  %141 = sub i32 %140, %78
  %142 = tail call i32 @llvm.smax.i32(i32 %141, i32 0)
  %143 = shl nuw i32 %142, 1
  %144 = sub i32 %140, %143
  %145 = tail call i32 @llvm.smax.i32(i32 %144, i32 0)
  %146 = tail call i32 @llvm.smin.i32(i32 %78, i32 %145)
  %147 = add i32 %138, %46
  %148 = mul i32 %147, 3
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, ptr %44, i64 %149
  %151 = load float, ptr %150, align 4
  %152 = add i32 %148, 1
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, ptr %44, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = add i32 %148, 2
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %44, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = add i32 %146, %46
  %161 = mul i32 %160, 3
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, ptr %44, i64 %162
  %164 = load float, ptr %163, align 4
  %165 = add i32 %161, 1
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %44, i64 %166
  %168 = load float, ptr %167, align 4
  %169 = add i32 %161, 2
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, ptr %44, i64 %170
  %172 = load float, ptr %171, align 4
  %173 = fadd reassoc ninf nsz float %164, %151
  %174 = fadd reassoc ninf nsz float %168, %155
  %175 = fadd reassoc ninf nsz float %172, %159
  %176 = fmul reassoc ninf nsz float %173, %130
  %177 = fmul reassoc ninf nsz float %174, %130
  %178 = fmul reassoc ninf nsz float %175, %130
  %179 = fadd reassoc ninf nsz float %176, %125
  %180 = fadd reassoc ninf nsz float %177, %126
  %181 = fadd reassoc ninf nsz float %178, %127
  %factor184 = fmul reassoc ninf nsz float %130, 2.000000e+00
  %182 = fadd reassoc ninf nsz float %factor184, %128
  %183 = icmp samesign ugt i32 %66, 2
  br i1 %183, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %184 = getelementptr i8, ptr %68, i64 12
  %185 = load float, ptr %184, align 4
  %186 = add i32 %73, -19
  %187 = tail call i32 @llvm.abs.i32(i32 %186, i1 true)
  %188 = sub i32 %187, %78
  %189 = tail call i32 @llvm.smax.i32(i32 %188, i32 0)
  %190 = shl nuw i32 %189, 1
  %191 = sub i32 %187, %190
  %192 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %193 = tail call i32 @llvm.smin.i32(i32 %78, i32 %192)
  %194 = add i32 %73, -13
  %195 = tail call i32 @llvm.abs.i32(i32 %194, i1 true)
  %196 = sub i32 %195, %78
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = shl nuw i32 %197, 1
  %199 = sub i32 %195, %198
  %200 = tail call i32 @llvm.smax.i32(i32 %199, i32 0)
  %201 = tail call i32 @llvm.smin.i32(i32 %78, i32 %200)
  %202 = add i32 %193, %46
  %203 = mul i32 %202, 3
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, ptr %44, i64 %204
  %206 = load float, ptr %205, align 4
  %207 = add i32 %203, 1
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %44, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = add i32 %203, 2
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %44, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = add i32 %201, %46
  %216 = mul i32 %215, 3
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %44, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = add i32 %216, 1
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, ptr %44, i64 %221
  %223 = load float, ptr %222, align 4
  %224 = add i32 %216, 2
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, ptr %44, i64 %225
  %227 = load float, ptr %226, align 4
  %228 = fadd reassoc ninf nsz float %219, %206
  %229 = fadd reassoc ninf nsz float %223, %210
  %230 = fadd reassoc ninf nsz float %227, %214
  %231 = fmul reassoc ninf nsz float %228, %185
  %232 = fmul reassoc ninf nsz float %229, %185
  %233 = fmul reassoc ninf nsz float %230, %185
  %234 = fadd reassoc ninf nsz float %231, %179
  %235 = fadd reassoc ninf nsz float %232, %180
  %236 = fadd reassoc ninf nsz float %233, %181
  %factor185 = fmul reassoc ninf nsz float %185, 2.000000e+00
  %237 = fadd reassoc ninf nsz float %factor185, %182
  %.not177 = icmp eq i32 %66, 3
  br i1 %.not177, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %238 = getelementptr i8, ptr %68, i64 16
  %239 = load float, ptr %238, align 4
  %240 = add i32 %73, -20
  %241 = tail call i32 @llvm.abs.i32(i32 %240, i1 true)
  %242 = sub i32 %241, %78
  %243 = tail call i32 @llvm.smax.i32(i32 %242, i32 0)
  %244 = shl nuw i32 %243, 1
  %245 = sub i32 %241, %244
  %246 = tail call i32 @llvm.smax.i32(i32 %245, i32 0)
  %247 = tail call i32 @llvm.smin.i32(i32 %78, i32 %246)
  %248 = add i32 %73, -12
  %249 = tail call i32 @llvm.abs.i32(i32 %248, i1 true)
  %250 = sub i32 %249, %78
  %251 = tail call i32 @llvm.smax.i32(i32 %250, i32 0)
  %252 = shl nuw i32 %251, 1
  %253 = sub i32 %249, %252
  %254 = tail call i32 @llvm.smax.i32(i32 %253, i32 0)
  %255 = tail call i32 @llvm.smin.i32(i32 %78, i32 %254)
  %256 = add i32 %247, %46
  %257 = mul i32 %256, 3
  %258 = sext i32 %257 to i64
  %259 = getelementptr float, ptr %44, i64 %258
  %260 = load float, ptr %259, align 4
  %261 = add i32 %257, 1
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, ptr %44, i64 %262
  %264 = load float, ptr %263, align 4
  %265 = add i32 %257, 2
  %266 = sext i32 %265 to i64
  %267 = getelementptr float, ptr %44, i64 %266
  %268 = load float, ptr %267, align 4
  %269 = add i32 %255, %46
  %270 = mul i32 %269, 3
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %44, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = add i32 %270, 1
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, ptr %44, i64 %275
  %277 = load float, ptr %276, align 4
  %278 = add i32 %270, 2
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, ptr %44, i64 %279
  %281 = load float, ptr %280, align 4
  %282 = fadd reassoc ninf nsz float %273, %260
  %283 = fadd reassoc ninf nsz float %277, %264
  %284 = fadd reassoc ninf nsz float %281, %268
  %285 = fmul reassoc ninf nsz float %282, %239
  %286 = fmul reassoc ninf nsz float %283, %239
  %287 = fmul reassoc ninf nsz float %284, %239
  %288 = fadd reassoc ninf nsz float %285, %234
  %289 = fadd reassoc ninf nsz float %286, %235
  %290 = fadd reassoc ninf nsz float %287, %236
  %factor186 = fmul reassoc ninf nsz float %239, 2.000000e+00
  %291 = fadd reassoc ninf nsz float %factor186, %237
  %292 = icmp samesign ugt i32 %66, 4
  br i1 %292, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %293 = getelementptr i8, ptr %68, i64 20
  %294 = load float, ptr %293, align 4
  %295 = add i32 %73, -21
  %296 = tail call i32 @llvm.abs.i32(i32 %295, i1 true)
  %297 = sub i32 %296, %78
  %298 = tail call i32 @llvm.smax.i32(i32 %297, i32 0)
  %299 = shl nuw i32 %298, 1
  %300 = sub i32 %296, %299
  %301 = tail call i32 @llvm.smax.i32(i32 %300, i32 0)
  %302 = tail call i32 @llvm.smin.i32(i32 %78, i32 %301)
  %303 = add i32 %73, -11
  %304 = tail call i32 @llvm.abs.i32(i32 %303, i1 true)
  %305 = sub i32 %304, %78
  %306 = tail call i32 @llvm.smax.i32(i32 %305, i32 0)
  %307 = shl nuw i32 %306, 1
  %308 = sub i32 %304, %307
  %309 = tail call i32 @llvm.smax.i32(i32 %308, i32 0)
  %310 = tail call i32 @llvm.smin.i32(i32 %78, i32 %309)
  %311 = add i32 %302, %46
  %312 = mul i32 %311, 3
  %313 = sext i32 %312 to i64
  %314 = getelementptr float, ptr %44, i64 %313
  %315 = load float, ptr %314, align 4
  %316 = add i32 %312, 1
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, ptr %44, i64 %317
  %319 = load float, ptr %318, align 4
  %320 = add i32 %312, 2
  %321 = sext i32 %320 to i64
  %322 = getelementptr float, ptr %44, i64 %321
  %323 = load float, ptr %322, align 4
  %324 = add i32 %310, %46
  %325 = mul i32 %324, 3
  %326 = sext i32 %325 to i64
  %327 = getelementptr float, ptr %44, i64 %326
  %328 = load float, ptr %327, align 4
  %329 = add i32 %325, 1
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, ptr %44, i64 %330
  %332 = load float, ptr %331, align 4
  %333 = add i32 %325, 2
  %334 = sext i32 %333 to i64
  %335 = getelementptr float, ptr %44, i64 %334
  %336 = load float, ptr %335, align 4
  %337 = fadd reassoc ninf nsz float %328, %315
  %338 = fadd reassoc ninf nsz float %332, %319
  %339 = fadd reassoc ninf nsz float %336, %323
  %340 = fmul reassoc ninf nsz float %337, %294
  %341 = fmul reassoc ninf nsz float %338, %294
  %342 = fmul reassoc ninf nsz float %339, %294
  %343 = fadd reassoc ninf nsz float %340, %288
  %344 = fadd reassoc ninf nsz float %341, %289
  %345 = fadd reassoc ninf nsz float %342, %290
  %factor187 = fmul reassoc ninf nsz float %294, 2.000000e+00
  %346 = fadd reassoc ninf nsz float %factor187, %291
  %.not178 = icmp eq i32 %66, 5
  br i1 %.not178, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %347 = getelementptr i8, ptr %68, i64 24
  %348 = load float, ptr %347, align 4
  %349 = add i32 %73, -22
  %350 = tail call i32 @llvm.abs.i32(i32 %349, i1 true)
  %351 = sub i32 %350, %78
  %352 = tail call i32 @llvm.smax.i32(i32 %351, i32 0)
  %353 = shl nuw i32 %352, 1
  %354 = sub i32 %350, %353
  %355 = tail call i32 @llvm.smax.i32(i32 %354, i32 0)
  %356 = tail call i32 @llvm.smin.i32(i32 %78, i32 %355)
  %357 = add i32 %73, -10
  %358 = tail call i32 @llvm.abs.i32(i32 %357, i1 true)
  %359 = sub i32 %358, %78
  %360 = tail call i32 @llvm.smax.i32(i32 %359, i32 0)
  %361 = shl nuw i32 %360, 1
  %362 = sub i32 %358, %361
  %363 = tail call i32 @llvm.smax.i32(i32 %362, i32 0)
  %364 = tail call i32 @llvm.smin.i32(i32 %78, i32 %363)
  %365 = add i32 %356, %46
  %366 = mul i32 %365, 3
  %367 = sext i32 %366 to i64
  %368 = getelementptr float, ptr %44, i64 %367
  %369 = load float, ptr %368, align 4
  %370 = add i32 %366, 1
  %371 = sext i32 %370 to i64
  %372 = getelementptr float, ptr %44, i64 %371
  %373 = load float, ptr %372, align 4
  %374 = add i32 %366, 2
  %375 = sext i32 %374 to i64
  %376 = getelementptr float, ptr %44, i64 %375
  %377 = load float, ptr %376, align 4
  %378 = add i32 %364, %46
  %379 = mul i32 %378, 3
  %380 = sext i32 %379 to i64
  %381 = getelementptr float, ptr %44, i64 %380
  %382 = load float, ptr %381, align 4
  %383 = add i32 %379, 1
  %384 = sext i32 %383 to i64
  %385 = getelementptr float, ptr %44, i64 %384
  %386 = load float, ptr %385, align 4
  %387 = add i32 %379, 2
  %388 = sext i32 %387 to i64
  %389 = getelementptr float, ptr %44, i64 %388
  %390 = load float, ptr %389, align 4
  %391 = fadd reassoc ninf nsz float %382, %369
  %392 = fadd reassoc ninf nsz float %386, %373
  %393 = fadd reassoc ninf nsz float %390, %377
  %394 = fmul reassoc ninf nsz float %391, %348
  %395 = fmul reassoc ninf nsz float %392, %348
  %396 = fmul reassoc ninf nsz float %393, %348
  %397 = fadd reassoc ninf nsz float %394, %343
  %398 = fadd reassoc ninf nsz float %395, %344
  %399 = fadd reassoc ninf nsz float %396, %345
  %factor188 = fmul reassoc ninf nsz float %348, 2.000000e+00
  %400 = fadd reassoc ninf nsz float %factor188, %346
  %401 = icmp samesign ugt i32 %66, 6
  br i1 %401, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %402 = getelementptr i8, ptr %68, i64 28
  %403 = load float, ptr %402, align 4
  %404 = add i32 %73, -23
  %405 = tail call i32 @llvm.abs.i32(i32 %404, i1 true)
  %406 = sub i32 %405, %78
  %407 = tail call i32 @llvm.smax.i32(i32 %406, i32 0)
  %408 = shl nuw i32 %407, 1
  %409 = sub i32 %405, %408
  %410 = tail call i32 @llvm.smax.i32(i32 %409, i32 0)
  %411 = tail call i32 @llvm.smin.i32(i32 %78, i32 %410)
  %412 = add i32 %73, -9
  %413 = tail call i32 @llvm.abs.i32(i32 %412, i1 true)
  %414 = sub i32 %413, %78
  %415 = tail call i32 @llvm.smax.i32(i32 %414, i32 0)
  %416 = shl nuw i32 %415, 1
  %417 = sub i32 %413, %416
  %418 = tail call i32 @llvm.smax.i32(i32 %417, i32 0)
  %419 = tail call i32 @llvm.smin.i32(i32 %78, i32 %418)
  %420 = add i32 %411, %46
  %421 = mul i32 %420, 3
  %422 = sext i32 %421 to i64
  %423 = getelementptr float, ptr %44, i64 %422
  %424 = load float, ptr %423, align 4
  %425 = add i32 %421, 1
  %426 = sext i32 %425 to i64
  %427 = getelementptr float, ptr %44, i64 %426
  %428 = load float, ptr %427, align 4
  %429 = add i32 %421, 2
  %430 = sext i32 %429 to i64
  %431 = getelementptr float, ptr %44, i64 %430
  %432 = load float, ptr %431, align 4
  %433 = add i32 %419, %46
  %434 = mul i32 %433, 3
  %435 = sext i32 %434 to i64
  %436 = getelementptr float, ptr %44, i64 %435
  %437 = load float, ptr %436, align 4
  %438 = add i32 %434, 1
  %439 = sext i32 %438 to i64
  %440 = getelementptr float, ptr %44, i64 %439
  %441 = load float, ptr %440, align 4
  %442 = add i32 %434, 2
  %443 = sext i32 %442 to i64
  %444 = getelementptr float, ptr %44, i64 %443
  %445 = load float, ptr %444, align 4
  %446 = fadd reassoc ninf nsz float %437, %424
  %447 = fadd reassoc ninf nsz float %441, %428
  %448 = fadd reassoc ninf nsz float %445, %432
  %449 = fmul reassoc ninf nsz float %446, %403
  %450 = fmul reassoc ninf nsz float %447, %403
  %451 = fmul reassoc ninf nsz float %448, %403
  %452 = fadd reassoc ninf nsz float %449, %397
  %453 = fadd reassoc ninf nsz float %450, %398
  %454 = fadd reassoc ninf nsz float %451, %399
  %factor189 = fmul reassoc ninf nsz float %403, 2.000000e+00
  %455 = fadd reassoc ninf nsz float %factor189, %400
  %.not179 = icmp eq i32 %66, 7
  br i1 %.not179, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %456 = getelementptr i8, ptr %68, i64 32
  %457 = load float, ptr %456, align 4
  %458 = add i32 %73, -24
  %459 = tail call i32 @llvm.abs.i32(i32 %458, i1 true)
  %460 = sub i32 %459, %78
  %461 = tail call i32 @llvm.smax.i32(i32 %460, i32 0)
  %462 = shl nuw i32 %461, 1
  %463 = sub i32 %459, %462
  %464 = tail call i32 @llvm.smax.i32(i32 %463, i32 0)
  %465 = tail call i32 @llvm.smin.i32(i32 %78, i32 %464)
  %466 = add i32 %73, -8
  %467 = tail call i32 @llvm.abs.i32(i32 %466, i1 true)
  %468 = sub i32 %467, %78
  %469 = tail call i32 @llvm.smax.i32(i32 %468, i32 0)
  %470 = shl nuw i32 %469, 1
  %471 = sub i32 %467, %470
  %472 = tail call i32 @llvm.smax.i32(i32 %471, i32 0)
  %473 = tail call i32 @llvm.smin.i32(i32 %78, i32 %472)
  %474 = add i32 %465, %46
  %475 = mul i32 %474, 3
  %476 = sext i32 %475 to i64
  %477 = getelementptr float, ptr %44, i64 %476
  %478 = load float, ptr %477, align 4
  %479 = add i32 %475, 1
  %480 = sext i32 %479 to i64
  %481 = getelementptr float, ptr %44, i64 %480
  %482 = load float, ptr %481, align 4
  %483 = add i32 %475, 2
  %484 = sext i32 %483 to i64
  %485 = getelementptr float, ptr %44, i64 %484
  %486 = load float, ptr %485, align 4
  %487 = add i32 %473, %46
  %488 = mul i32 %487, 3
  %489 = sext i32 %488 to i64
  %490 = getelementptr float, ptr %44, i64 %489
  %491 = load float, ptr %490, align 4
  %492 = add i32 %488, 1
  %493 = sext i32 %492 to i64
  %494 = getelementptr float, ptr %44, i64 %493
  %495 = load float, ptr %494, align 4
  %496 = add i32 %488, 2
  %497 = sext i32 %496 to i64
  %498 = getelementptr float, ptr %44, i64 %497
  %499 = load float, ptr %498, align 4
  %500 = fadd reassoc ninf nsz float %491, %478
  %501 = fadd reassoc ninf nsz float %495, %482
  %502 = fadd reassoc ninf nsz float %499, %486
  %503 = fmul reassoc ninf nsz float %500, %457
  %504 = fmul reassoc ninf nsz float %501, %457
  %505 = fmul reassoc ninf nsz float %502, %457
  %506 = fadd reassoc ninf nsz float %503, %452
  %507 = fadd reassoc ninf nsz float %504, %453
  %508 = fadd reassoc ninf nsz float %505, %454
  %factor190 = fmul reassoc ninf nsz float %457, 2.000000e+00
  %509 = fadd reassoc ninf nsz float %factor190, %455
  %510 = icmp samesign ugt i32 %66, 8
  br i1 %510, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %511 = getelementptr i8, ptr %68, i64 36
  %512 = load float, ptr %511, align 4
  %513 = add i32 %73, -25
  %514 = tail call i32 @llvm.abs.i32(i32 %513, i1 true)
  %515 = sub i32 %514, %78
  %516 = tail call i32 @llvm.smax.i32(i32 %515, i32 0)
  %517 = shl nuw i32 %516, 1
  %518 = sub i32 %514, %517
  %519 = tail call i32 @llvm.smax.i32(i32 %518, i32 0)
  %520 = tail call i32 @llvm.smin.i32(i32 %78, i32 %519)
  %521 = add i32 %73, -7
  %522 = tail call i32 @llvm.abs.i32(i32 %521, i1 true)
  %523 = sub i32 %522, %78
  %524 = tail call i32 @llvm.smax.i32(i32 %523, i32 0)
  %525 = shl nuw i32 %524, 1
  %526 = sub i32 %522, %525
  %527 = tail call i32 @llvm.smax.i32(i32 %526, i32 0)
  %528 = tail call i32 @llvm.smin.i32(i32 %78, i32 %527)
  %529 = add i32 %520, %46
  %530 = mul i32 %529, 3
  %531 = sext i32 %530 to i64
  %532 = getelementptr float, ptr %44, i64 %531
  %533 = load float, ptr %532, align 4
  %534 = add i32 %530, 1
  %535 = sext i32 %534 to i64
  %536 = getelementptr float, ptr %44, i64 %535
  %537 = load float, ptr %536, align 4
  %538 = add i32 %530, 2
  %539 = sext i32 %538 to i64
  %540 = getelementptr float, ptr %44, i64 %539
  %541 = load float, ptr %540, align 4
  %542 = add i32 %528, %46
  %543 = mul i32 %542, 3
  %544 = sext i32 %543 to i64
  %545 = getelementptr float, ptr %44, i64 %544
  %546 = load float, ptr %545, align 4
  %547 = add i32 %543, 1
  %548 = sext i32 %547 to i64
  %549 = getelementptr float, ptr %44, i64 %548
  %550 = load float, ptr %549, align 4
  %551 = add i32 %543, 2
  %552 = sext i32 %551 to i64
  %553 = getelementptr float, ptr %44, i64 %552
  %554 = load float, ptr %553, align 4
  %555 = fadd reassoc ninf nsz float %546, %533
  %556 = fadd reassoc ninf nsz float %550, %537
  %557 = fadd reassoc ninf nsz float %554, %541
  %558 = fmul reassoc ninf nsz float %555, %512
  %559 = fmul reassoc ninf nsz float %556, %512
  %560 = fmul reassoc ninf nsz float %557, %512
  %561 = fadd reassoc ninf nsz float %558, %506
  %562 = fadd reassoc ninf nsz float %559, %507
  %563 = fadd reassoc ninf nsz float %560, %508
  %factor191 = fmul reassoc ninf nsz float %512, 2.000000e+00
  %564 = fadd reassoc ninf nsz float %factor191, %509
  %.not180 = icmp eq i32 %66, 9
  br i1 %.not180, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %565 = getelementptr i8, ptr %68, i64 40
  %566 = load float, ptr %565, align 4
  %567 = add i32 %73, -26
  %568 = tail call i32 @llvm.abs.i32(i32 %567, i1 true)
  %569 = sub i32 %568, %78
  %570 = tail call i32 @llvm.smax.i32(i32 %569, i32 0)
  %571 = shl nuw i32 %570, 1
  %572 = sub i32 %568, %571
  %573 = tail call i32 @llvm.smax.i32(i32 %572, i32 0)
  %574 = tail call i32 @llvm.smin.i32(i32 %78, i32 %573)
  %575 = add i32 %73, -6
  %576 = tail call i32 @llvm.abs.i32(i32 %575, i1 true)
  %577 = sub i32 %576, %78
  %578 = tail call i32 @llvm.smax.i32(i32 %577, i32 0)
  %579 = shl nuw i32 %578, 1
  %580 = sub i32 %576, %579
  %581 = tail call i32 @llvm.smax.i32(i32 %580, i32 0)
  %582 = tail call i32 @llvm.smin.i32(i32 %78, i32 %581)
  %583 = add i32 %574, %46
  %584 = mul i32 %583, 3
  %585 = sext i32 %584 to i64
  %586 = getelementptr float, ptr %44, i64 %585
  %587 = load float, ptr %586, align 4
  %588 = add i32 %584, 1
  %589 = sext i32 %588 to i64
  %590 = getelementptr float, ptr %44, i64 %589
  %591 = load float, ptr %590, align 4
  %592 = add i32 %584, 2
  %593 = sext i32 %592 to i64
  %594 = getelementptr float, ptr %44, i64 %593
  %595 = load float, ptr %594, align 4
  %596 = add i32 %582, %46
  %597 = mul i32 %596, 3
  %598 = sext i32 %597 to i64
  %599 = getelementptr float, ptr %44, i64 %598
  %600 = load float, ptr %599, align 4
  %601 = add i32 %597, 1
  %602 = sext i32 %601 to i64
  %603 = getelementptr float, ptr %44, i64 %602
  %604 = load float, ptr %603, align 4
  %605 = add i32 %597, 2
  %606 = sext i32 %605 to i64
  %607 = getelementptr float, ptr %44, i64 %606
  %608 = load float, ptr %607, align 4
  %609 = fadd reassoc ninf nsz float %600, %587
  %610 = fadd reassoc ninf nsz float %604, %591
  %611 = fadd reassoc ninf nsz float %608, %595
  %612 = fmul reassoc ninf nsz float %609, %566
  %613 = fmul reassoc ninf nsz float %610, %566
  %614 = fmul reassoc ninf nsz float %611, %566
  %615 = fadd reassoc ninf nsz float %612, %561
  %616 = fadd reassoc ninf nsz float %613, %562
  %617 = fadd reassoc ninf nsz float %614, %563
  %factor192 = fmul reassoc ninf nsz float %566, 2.000000e+00
  %618 = fadd reassoc ninf nsz float %factor192, %564
  %619 = icmp samesign ugt i32 %66, 10
  br i1 %619, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %620 = getelementptr i8, ptr %68, i64 44
  %621 = load float, ptr %620, align 4
  %622 = add i32 %73, -27
  %623 = tail call i32 @llvm.abs.i32(i32 %622, i1 true)
  %624 = sub i32 %623, %78
  %625 = tail call i32 @llvm.smax.i32(i32 %624, i32 0)
  %626 = shl nuw i32 %625, 1
  %627 = sub i32 %623, %626
  %628 = tail call i32 @llvm.smax.i32(i32 %627, i32 0)
  %629 = tail call i32 @llvm.smin.i32(i32 %78, i32 %628)
  %630 = add i32 %73, -5
  %631 = tail call i32 @llvm.abs.i32(i32 %630, i1 true)
  %632 = sub i32 %631, %78
  %633 = tail call i32 @llvm.smax.i32(i32 %632, i32 0)
  %634 = shl nuw i32 %633, 1
  %635 = sub i32 %631, %634
  %636 = tail call i32 @llvm.smax.i32(i32 %635, i32 0)
  %637 = tail call i32 @llvm.smin.i32(i32 %78, i32 %636)
  %638 = add i32 %629, %46
  %639 = mul i32 %638, 3
  %640 = sext i32 %639 to i64
  %641 = getelementptr float, ptr %44, i64 %640
  %642 = load float, ptr %641, align 4
  %643 = add i32 %639, 1
  %644 = sext i32 %643 to i64
  %645 = getelementptr float, ptr %44, i64 %644
  %646 = load float, ptr %645, align 4
  %647 = add i32 %639, 2
  %648 = sext i32 %647 to i64
  %649 = getelementptr float, ptr %44, i64 %648
  %650 = load float, ptr %649, align 4
  %651 = add i32 %637, %46
  %652 = mul i32 %651, 3
  %653 = sext i32 %652 to i64
  %654 = getelementptr float, ptr %44, i64 %653
  %655 = load float, ptr %654, align 4
  %656 = add i32 %652, 1
  %657 = sext i32 %656 to i64
  %658 = getelementptr float, ptr %44, i64 %657
  %659 = load float, ptr %658, align 4
  %660 = add i32 %652, 2
  %661 = sext i32 %660 to i64
  %662 = getelementptr float, ptr %44, i64 %661
  %663 = load float, ptr %662, align 4
  %664 = fadd reassoc ninf nsz float %655, %642
  %665 = fadd reassoc ninf nsz float %659, %646
  %666 = fadd reassoc ninf nsz float %663, %650
  %667 = fmul reassoc ninf nsz float %664, %621
  %668 = fmul reassoc ninf nsz float %665, %621
  %669 = fmul reassoc ninf nsz float %666, %621
  %670 = fadd reassoc ninf nsz float %667, %615
  %671 = fadd reassoc ninf nsz float %668, %616
  %672 = fadd reassoc ninf nsz float %669, %617
  %factor193 = fmul reassoc ninf nsz float %621, 2.000000e+00
  %673 = fadd reassoc ninf nsz float %factor193, %618
  %.not181 = icmp eq i32 %66, 11
  br i1 %.not181, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %674 = getelementptr i8, ptr %68, i64 48
  %675 = load float, ptr %674, align 4
  %676 = add i32 %73, -28
  %677 = tail call i32 @llvm.abs.i32(i32 %676, i1 true)
  %678 = sub i32 %677, %78
  %679 = tail call i32 @llvm.smax.i32(i32 %678, i32 0)
  %680 = shl nuw i32 %679, 1
  %681 = sub i32 %677, %680
  %682 = tail call i32 @llvm.smax.i32(i32 %681, i32 0)
  %683 = tail call i32 @llvm.smin.i32(i32 %78, i32 %682)
  %684 = add i32 %73, -4
  %685 = tail call i32 @llvm.abs.i32(i32 %684, i1 true)
  %686 = sub i32 %685, %78
  %687 = tail call i32 @llvm.smax.i32(i32 %686, i32 0)
  %688 = shl nuw i32 %687, 1
  %689 = sub i32 %685, %688
  %690 = tail call i32 @llvm.smax.i32(i32 %689, i32 0)
  %691 = tail call i32 @llvm.smin.i32(i32 %78, i32 %690)
  %692 = add i32 %683, %46
  %693 = mul i32 %692, 3
  %694 = sext i32 %693 to i64
  %695 = getelementptr float, ptr %44, i64 %694
  %696 = load float, ptr %695, align 4
  %697 = add i32 %693, 1
  %698 = sext i32 %697 to i64
  %699 = getelementptr float, ptr %44, i64 %698
  %700 = load float, ptr %699, align 4
  %701 = add i32 %693, 2
  %702 = sext i32 %701 to i64
  %703 = getelementptr float, ptr %44, i64 %702
  %704 = load float, ptr %703, align 4
  %705 = add i32 %691, %46
  %706 = mul i32 %705, 3
  %707 = sext i32 %706 to i64
  %708 = getelementptr float, ptr %44, i64 %707
  %709 = load float, ptr %708, align 4
  %710 = add i32 %706, 1
  %711 = sext i32 %710 to i64
  %712 = getelementptr float, ptr %44, i64 %711
  %713 = load float, ptr %712, align 4
  %714 = add i32 %706, 2
  %715 = sext i32 %714 to i64
  %716 = getelementptr float, ptr %44, i64 %715
  %717 = load float, ptr %716, align 4
  %718 = fadd reassoc ninf nsz float %709, %696
  %719 = fadd reassoc ninf nsz float %713, %700
  %720 = fadd reassoc ninf nsz float %717, %704
  %721 = fmul reassoc ninf nsz float %718, %675
  %722 = fmul reassoc ninf nsz float %719, %675
  %723 = fmul reassoc ninf nsz float %720, %675
  %724 = fadd reassoc ninf nsz float %721, %670
  %725 = fadd reassoc ninf nsz float %722, %671
  %726 = fadd reassoc ninf nsz float %723, %672
  %factor194 = fmul reassoc ninf nsz float %675, 2.000000e+00
  %727 = fadd reassoc ninf nsz float %factor194, %673
  %728 = icmp samesign ugt i32 %66, 12
  br i1 %728, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %729 = getelementptr i8, ptr %68, i64 52
  %730 = load float, ptr %729, align 4
  %731 = add i32 %73, -29
  %732 = tail call i32 @llvm.abs.i32(i32 %731, i1 true)
  %733 = sub i32 %732, %78
  %734 = tail call i32 @llvm.smax.i32(i32 %733, i32 0)
  %735 = shl nuw i32 %734, 1
  %736 = sub i32 %732, %735
  %737 = tail call i32 @llvm.smax.i32(i32 %736, i32 0)
  %738 = tail call i32 @llvm.smin.i32(i32 %78, i32 %737)
  %739 = add i32 %73, -3
  %740 = tail call i32 @llvm.abs.i32(i32 %739, i1 true)
  %741 = sub i32 %740, %78
  %742 = tail call i32 @llvm.smax.i32(i32 %741, i32 0)
  %743 = shl nuw i32 %742, 1
  %744 = sub i32 %740, %743
  %745 = tail call i32 @llvm.smax.i32(i32 %744, i32 0)
  %746 = tail call i32 @llvm.smin.i32(i32 %78, i32 %745)
  %747 = add i32 %738, %46
  %748 = mul i32 %747, 3
  %749 = sext i32 %748 to i64
  %750 = getelementptr float, ptr %44, i64 %749
  %751 = load float, ptr %750, align 4
  %752 = add i32 %748, 1
  %753 = sext i32 %752 to i64
  %754 = getelementptr float, ptr %44, i64 %753
  %755 = load float, ptr %754, align 4
  %756 = add i32 %748, 2
  %757 = sext i32 %756 to i64
  %758 = getelementptr float, ptr %44, i64 %757
  %759 = load float, ptr %758, align 4
  %760 = add i32 %746, %46
  %761 = mul i32 %760, 3
  %762 = sext i32 %761 to i64
  %763 = getelementptr float, ptr %44, i64 %762
  %764 = load float, ptr %763, align 4
  %765 = add i32 %761, 1
  %766 = sext i32 %765 to i64
  %767 = getelementptr float, ptr %44, i64 %766
  %768 = load float, ptr %767, align 4
  %769 = add i32 %761, 2
  %770 = sext i32 %769 to i64
  %771 = getelementptr float, ptr %44, i64 %770
  %772 = load float, ptr %771, align 4
  %773 = fadd reassoc ninf nsz float %764, %751
  %774 = fadd reassoc ninf nsz float %768, %755
  %775 = fadd reassoc ninf nsz float %772, %759
  %776 = fmul reassoc ninf nsz float %773, %730
  %777 = fmul reassoc ninf nsz float %774, %730
  %778 = fmul reassoc ninf nsz float %775, %730
  %779 = fadd reassoc ninf nsz float %776, %724
  %780 = fadd reassoc ninf nsz float %777, %725
  %781 = fadd reassoc ninf nsz float %778, %726
  %factor195 = fmul reassoc ninf nsz float %730, 2.000000e+00
  %782 = fadd reassoc ninf nsz float %factor195, %727
  %.not182 = icmp eq i32 %66, 13
  br i1 %.not182, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %783 = getelementptr i8, ptr %68, i64 56
  %784 = load float, ptr %783, align 4
  %785 = add i32 %73, -30
  %786 = tail call i32 @llvm.abs.i32(i32 %785, i1 true)
  %787 = sub i32 %786, %78
  %788 = tail call i32 @llvm.smax.i32(i32 %787, i32 0)
  %789 = shl nuw i32 %788, 1
  %790 = sub i32 %786, %789
  %791 = tail call i32 @llvm.smax.i32(i32 %790, i32 0)
  %792 = tail call i32 @llvm.smin.i32(i32 %78, i32 %791)
  %793 = add i32 %73, -2
  %794 = tail call i32 @llvm.abs.i32(i32 %793, i1 true)
  %795 = sub i32 %794, %78
  %796 = tail call i32 @llvm.smax.i32(i32 %795, i32 0)
  %797 = shl nuw i32 %796, 1
  %798 = sub i32 %794, %797
  %799 = tail call i32 @llvm.smax.i32(i32 %798, i32 0)
  %800 = tail call i32 @llvm.smin.i32(i32 %78, i32 %799)
  %801 = add i32 %792, %46
  %802 = mul i32 %801, 3
  %803 = sext i32 %802 to i64
  %804 = getelementptr float, ptr %44, i64 %803
  %805 = load float, ptr %804, align 4
  %806 = add i32 %802, 1
  %807 = sext i32 %806 to i64
  %808 = getelementptr float, ptr %44, i64 %807
  %809 = load float, ptr %808, align 4
  %810 = add i32 %802, 2
  %811 = sext i32 %810 to i64
  %812 = getelementptr float, ptr %44, i64 %811
  %813 = load float, ptr %812, align 4
  %814 = add i32 %800, %46
  %815 = mul i32 %814, 3
  %816 = sext i32 %815 to i64
  %817 = getelementptr float, ptr %44, i64 %816
  %818 = load float, ptr %817, align 4
  %819 = add i32 %815, 1
  %820 = sext i32 %819 to i64
  %821 = getelementptr float, ptr %44, i64 %820
  %822 = load float, ptr %821, align 4
  %823 = add i32 %815, 2
  %824 = sext i32 %823 to i64
  %825 = getelementptr float, ptr %44, i64 %824
  %826 = load float, ptr %825, align 4
  %827 = fadd reassoc ninf nsz float %818, %805
  %828 = fadd reassoc ninf nsz float %822, %809
  %829 = fadd reassoc ninf nsz float %826, %813
  %830 = fmul reassoc ninf nsz float %827, %784
  %831 = fmul reassoc ninf nsz float %828, %784
  %832 = fmul reassoc ninf nsz float %829, %784
  %833 = fadd reassoc ninf nsz float %830, %779
  %834 = fadd reassoc ninf nsz float %831, %780
  %835 = fadd reassoc ninf nsz float %832, %781
  %factor196 = fmul reassoc ninf nsz float %784, 2.000000e+00
  %836 = fadd reassoc ninf nsz float %factor196, %782
  %837 = icmp samesign ugt i32 %66, 14
  br i1 %837, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %838 = getelementptr i8, ptr %68, i64 60
  %839 = load float, ptr %838, align 4
  %840 = add i32 %73, -31
  %841 = tail call i32 @llvm.abs.i32(i32 %840, i1 true)
  %842 = sub i32 %841, %78
  %843 = tail call i32 @llvm.smax.i32(i32 %842, i32 0)
  %844 = shl nuw i32 %843, 1
  %845 = sub i32 %841, %844
  %846 = tail call i32 @llvm.smax.i32(i32 %845, i32 0)
  %847 = tail call i32 @llvm.smin.i32(i32 %78, i32 %846)
  %848 = add i32 %73, -1
  %849 = tail call i32 @llvm.abs.i32(i32 %848, i1 true)
  %850 = sub i32 %849, %78
  %851 = tail call i32 @llvm.smax.i32(i32 %850, i32 0)
  %852 = shl nuw i32 %851, 1
  %853 = sub i32 %849, %852
  %854 = tail call i32 @llvm.smax.i32(i32 %853, i32 0)
  %855 = tail call i32 @llvm.smin.i32(i32 %78, i32 %854)
  %856 = add i32 %847, %46
  %857 = mul i32 %856, 3
  %858 = sext i32 %857 to i64
  %859 = getelementptr float, ptr %44, i64 %858
  %860 = load float, ptr %859, align 4
  %861 = add i32 %857, 1
  %862 = sext i32 %861 to i64
  %863 = getelementptr float, ptr %44, i64 %862
  %864 = load float, ptr %863, align 4
  %865 = add i32 %857, 2
  %866 = sext i32 %865 to i64
  %867 = getelementptr float, ptr %44, i64 %866
  %868 = load float, ptr %867, align 4
  %869 = add i32 %855, %46
  %870 = mul i32 %869, 3
  %871 = sext i32 %870 to i64
  %872 = getelementptr float, ptr %44, i64 %871
  %873 = load float, ptr %872, align 4
  %874 = add i32 %870, 1
  %875 = sext i32 %874 to i64
  %876 = getelementptr float, ptr %44, i64 %875
  %877 = load float, ptr %876, align 4
  %878 = add i32 %870, 2
  %879 = sext i32 %878 to i64
  %880 = getelementptr float, ptr %44, i64 %879
  %881 = load float, ptr %880, align 4
  %882 = fadd reassoc ninf nsz float %873, %860
  %883 = fadd reassoc ninf nsz float %877, %864
  %884 = fadd reassoc ninf nsz float %881, %868
  %885 = fmul reassoc ninf nsz float %882, %839
  %886 = fmul reassoc ninf nsz float %883, %839
  %887 = fmul reassoc ninf nsz float %884, %839
  %888 = fadd reassoc ninf nsz float %885, %833
  %889 = fadd reassoc ninf nsz float %886, %834
  %890 = fadd reassoc ninf nsz float %887, %835
  %factor197 = fmul reassoc ninf nsz float %839, 2.000000e+00
  %891 = fadd reassoc ninf nsz float %factor197, %836
  %.not183 = icmp eq i32 %66, 15
  br i1 %.not183, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %892 = getelementptr i8, ptr %68, i64 64
  %893 = load float, ptr %892, align 4
  %894 = add i32 %73, -32
  %895 = tail call i32 @llvm.abs.i32(i32 %894, i1 true)
  %896 = sub i32 %895, %78
  %897 = tail call i32 @llvm.smax.i32(i32 %896, i32 0)
  %898 = shl nuw i32 %897, 1
  %899 = sub i32 %895, %898
  %900 = tail call i32 @llvm.smax.i32(i32 %899, i32 0)
  %901 = tail call i32 @llvm.smin.i32(i32 %78, i32 %900)
  %902 = tail call i32 @llvm.abs.i32(i32 %73, i1 true)
  %903 = sub i32 %902, %78
  %904 = tail call i32 @llvm.smax.i32(i32 %903, i32 0)
  %905 = shl nuw i32 %904, 1
  %906 = sub i32 %902, %905
  %907 = tail call i32 @llvm.smax.i32(i32 %906, i32 0)
  %908 = tail call i32 @llvm.smin.i32(i32 %78, i32 %907)
  %909 = add i32 %901, %46
  %910 = mul i32 %909, 3
  %911 = sext i32 %910 to i64
  %912 = getelementptr float, ptr %44, i64 %911
  %913 = load float, ptr %912, align 4
  %914 = add i32 %910, 1
  %915 = sext i32 %914 to i64
  %916 = getelementptr float, ptr %44, i64 %915
  %917 = load float, ptr %916, align 4
  %918 = add i32 %910, 2
  %919 = sext i32 %918 to i64
  %920 = getelementptr float, ptr %44, i64 %919
  %921 = load float, ptr %920, align 4
  %922 = add i32 %908, %46
  %923 = mul i32 %922, 3
  %924 = sext i32 %923 to i64
  %925 = getelementptr float, ptr %44, i64 %924
  %926 = load float, ptr %925, align 4
  %927 = add i32 %923, 1
  %928 = sext i32 %927 to i64
  %929 = getelementptr float, ptr %44, i64 %928
  %930 = load float, ptr %929, align 4
  %931 = add i32 %923, 2
  %932 = sext i32 %931 to i64
  %933 = getelementptr float, ptr %44, i64 %932
  %934 = load float, ptr %933, align 4
  %935 = fadd reassoc ninf nsz float %926, %913
  %936 = fadd reassoc ninf nsz float %930, %917
  %937 = fadd reassoc ninf nsz float %934, %921
  %938 = fmul reassoc ninf nsz float %935, %893
  %939 = fmul reassoc ninf nsz float %936, %893
  %940 = fmul reassoc ninf nsz float %937, %893
  %941 = fadd reassoc ninf nsz float %938, %888
  %942 = fadd reassoc ninf nsz float %939, %889
  %943 = fadd reassoc ninf nsz float %940, %890
  %factor198 = fmul reassoc ninf nsz float %893, 2.000000e+00
  %944 = fadd reassoc ninf nsz float %factor198, %891
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.15114 = phi float [ %941, %true_block43 ], [ %888, %after_if42 ], [ %833, %after_if39 ], [ %779, %after_if36 ], [ %724, %after_if33 ], [ %670, %after_if30 ], [ %615, %after_if27 ], [ %561, %after_if24 ], [ %506, %after_if21 ], [ %452, %after_if18 ], [ %397, %after_if15 ], [ %343, %after_if12 ], [ %288, %after_if9 ], [ %234, %after_if6 ], [ %179, %after_if3 ], [ %125, %after_if ], [ %62, %for_loop_body ]
  %.1598 = phi float [ %942, %true_block43 ], [ %889, %after_if42 ], [ %834, %after_if39 ], [ %780, %after_if36 ], [ %725, %after_if33 ], [ %671, %after_if30 ], [ %616, %after_if27 ], [ %562, %after_if24 ], [ %507, %after_if21 ], [ %453, %after_if18 ], [ %398, %after_if15 ], [ %344, %after_if12 ], [ %289, %after_if9 ], [ %235, %after_if6 ], [ %180, %after_if3 ], [ %126, %after_if ], [ %63, %for_loop_body ]
  %.1582 = phi float [ %943, %true_block43 ], [ %890, %after_if42 ], [ %835, %after_if39 ], [ %781, %after_if36 ], [ %726, %after_if33 ], [ %672, %after_if30 ], [ %617, %after_if27 ], [ %563, %after_if24 ], [ %508, %after_if21 ], [ %454, %after_if18 ], [ %399, %after_if15 ], [ %345, %after_if12 ], [ %290, %after_if9 ], [ %236, %after_if6 ], [ %181, %after_if3 ], [ %127, %after_if ], [ %64, %for_loop_body ]
  %.15 = phi float [ %944, %true_block43 ], [ %891, %after_if42 ], [ %836, %after_if39 ], [ %782, %after_if36 ], [ %727, %after_if33 ], [ %673, %after_if30 ], [ %618, %after_if27 ], [ %564, %after_if24 ], [ %509, %after_if21 ], [ %455, %after_if18 ], [ %400, %after_if15 ], [ %346, %after_if12 ], [ %291, %after_if9 ], [ %237, %after_if6 ], [ %182, %after_if3 ], [ %128, %after_if ], [ %43, %for_loop_body ]
  %945 = fdiv reassoc ninf nsz float %.15114, %.15
  %946 = fdiv reassoc ninf nsz float %.1598, %.15
  %947 = fdiv reassoc ninf nsz float %.1582, %.15
  %948 = load ptr, ptr %25, align 8
  %949 = load i32, ptr %26, align 4
  %950 = sub i32 %949, %35
  %951 = mul i32 %950, 3
  %952 = mul i32 %951, %42
  %953 = add i32 %lsr.iv200, %952
  %954 = sext i32 %953 to i64
  %955 = getelementptr float, ptr %948, i64 %954
  store float %945, ptr %955, align 4
  %956 = load ptr, ptr %25, align 8
  %957 = load i32, ptr %26, align 4
  %958 = sub i32 %957, %35
  %959 = mul i32 %958, 3
  %960 = mul i32 %959, %42
  %961 = add i32 %lsr.iv200, %960
  %962 = add i32 %961, 1
  %963 = sext i32 %962 to i64
  %964 = getelementptr float, ptr %956, i64 %963
  store float %946, ptr %964, align 4
  %965 = load ptr, ptr %25, align 8
  %966 = load i32, ptr %26, align 4
  %967 = sub i32 %966, %35
  %968 = mul i32 %967, 3
  %969 = mul i32 %968, %42
  %970 = add i32 %lsr.iv200, %969
  %971 = add i32 %970, 2
  %972 = sext i32 %971 to i64
  %973 = getelementptr float, ptr %965, i64 %972
  store float %947, ptr %973, align 4
  %lsr.iv.next = add i32 %lsr.iv, 1
  %974 = add i32 %27, %lsr.iv.next
  %lsr.iv.next201 = add i32 %lsr.iv200, 3
  %exitcond.not = icmp eq i32 %974, 16
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.7, align 8
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
