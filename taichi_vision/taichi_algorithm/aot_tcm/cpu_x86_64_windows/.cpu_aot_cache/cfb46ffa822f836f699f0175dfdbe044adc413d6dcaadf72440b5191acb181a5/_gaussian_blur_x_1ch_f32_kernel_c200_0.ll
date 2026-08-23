; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gaussian_blur_x_1ch_f32_kernel_c200_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 36
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 8
  store i32 %5, ptr %10, align 4
  %11 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %12 = load ptr, ptr %6, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 4
  store i32 %11, ptr %15, align 4
  %16 = mul i32 %11, %3
  %17 = load ptr, ptr %6, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  store i32 %16, ptr %19, align 4
  ret void
}

define void @_gaussian_blur_x_1ch_f32_kernel_c200_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %.05198 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %563, %after_if45 ]
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
  %57 = load float, ptr %23, align 4
  %58 = load ptr, ptr %41, align 8
  %59 = load i32, ptr %42, align 4
  %60 = mul i32 %56, %59
  %61 = sub i32 %59, %49
  %62 = mul i32 %61, %56
  %63 = add i32 %.05198, %62
  %64 = sext i32 %63 to i64
  %65 = getelementptr float, ptr %58, i64 %64
  %66 = load float, ptr %65, align 4
  %67 = fmul reassoc ninf nsz float %66, %57
  br i1 %24, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %68 = load ptr, ptr %22, align 8
  %69 = getelementptr i8, ptr %68, i64 4
  %70 = load float, ptr %69, align 4
  %71 = mul i32 %49, -1
  %72 = mul i32 %71, %56
  %73 = add i32 %.05198, %72
  %74 = add i32 %73, -1
  %75 = tail call i32 @llvm.abs.i32(i32 %74, i1 true)
  %76 = getelementptr inbounds nuw i8, ptr %47, i64 8
  %77 = load i32, ptr %76, align 4
  %78 = add i32 %77, -1
  %79 = sub i32 %75, %78
  %80 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %81 = shl nuw i32 %80, 1
  %82 = sub i32 %75, %81
  %83 = add i32 %73, 1
  %84 = tail call i32 @llvm.abs.i32(i32 %83, i1 true)
  %85 = sub i32 %84, %78
  %86 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %87 = shl nuw i32 %86, 1
  %88 = sub i32 %84, %87
  %89 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %90 = tail call i32 @llvm.smin.i32(i32 %78, i32 %89)
  %91 = add i32 %90, %60
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %58, i64 %92
  %94 = load float, ptr %93, align 4
  %95 = tail call i32 @llvm.smax.i32(i32 %88, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %78, i32 %95)
  %97 = add i32 %96, %60
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %58, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = fadd reassoc ninf nsz float %100, %94
  %102 = fmul reassoc ninf nsz float %101, %70
  %103 = fadd reassoc ninf nsz float %102, %67
  %factor = fmul reassoc ninf nsz float %70, 2.000000e+00
  %104 = fadd reassoc ninf nsz float %factor, %57
  br i1 %25, label %after_if3, label %after_if45

after_if3:                                        ; preds = %after_if
  %105 = getelementptr i8, ptr %68, i64 8
  %106 = load float, ptr %105, align 4
  %107 = add i32 %73, -2
  %108 = tail call i32 @llvm.abs.i32(i32 %107, i1 true)
  %109 = sub i32 %108, %78
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %111 = shl nuw i32 %110, 1
  %112 = sub i32 %108, %111
  %113 = add i32 %73, 2
  %114 = tail call i32 @llvm.abs.i32(i32 %113, i1 true)
  %115 = sub i32 %114, %78
  %116 = tail call i32 @llvm.smax.i32(i32 %115, i32 0)
  %117 = shl nuw i32 %116, 1
  %118 = sub i32 %114, %117
  %119 = tail call i32 @llvm.smax.i32(i32 %112, i32 0)
  %120 = tail call i32 @llvm.smin.i32(i32 %78, i32 %119)
  %121 = add i32 %120, %60
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %58, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = tail call i32 @llvm.smax.i32(i32 %118, i32 0)
  %126 = tail call i32 @llvm.smin.i32(i32 %78, i32 %125)
  %127 = add i32 %126, %60
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %58, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = fadd reassoc ninf nsz float %130, %124
  %132 = fmul reassoc ninf nsz float %131, %106
  %133 = fadd reassoc ninf nsz float %132, %103
  %factor83 = fmul reassoc ninf nsz float %106, 2.000000e+00
  %134 = fadd reassoc ninf nsz float %factor83, %104
  br i1 %26, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %135 = getelementptr i8, ptr %68, i64 12
  %136 = load float, ptr %135, align 4
  %137 = add i32 %73, -3
  %138 = tail call i32 @llvm.abs.i32(i32 %137, i1 true)
  %139 = sub i32 %138, %78
  %140 = tail call i32 @llvm.smax.i32(i32 %139, i32 0)
  %141 = shl nuw i32 %140, 1
  %142 = sub i32 %138, %141
  %143 = add i32 %73, 3
  %144 = tail call i32 @llvm.abs.i32(i32 %143, i1 true)
  %145 = sub i32 %144, %78
  %146 = tail call i32 @llvm.smax.i32(i32 %145, i32 0)
  %147 = shl nuw i32 %146, 1
  %148 = sub i32 %144, %147
  %149 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %150 = tail call i32 @llvm.smin.i32(i32 %78, i32 %149)
  %151 = add i32 %150, %60
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %58, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = tail call i32 @llvm.smax.i32(i32 %148, i32 0)
  %156 = tail call i32 @llvm.smin.i32(i32 %78, i32 %155)
  %157 = add i32 %156, %60
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %58, i64 %158
  %160 = load float, ptr %159, align 4
  %161 = fadd reassoc ninf nsz float %160, %154
  %162 = fmul reassoc ninf nsz float %161, %136
  %163 = fadd reassoc ninf nsz float %162, %133
  %factor84 = fmul reassoc ninf nsz float %136, 2.000000e+00
  %164 = fadd reassoc ninf nsz float %factor84, %134
  br i1 %27, label %after_if9, label %after_if45

after_if9:                                        ; preds = %after_if6
  %165 = getelementptr i8, ptr %68, i64 16
  %166 = load float, ptr %165, align 4
  %167 = add i32 %73, -4
  %168 = tail call i32 @llvm.abs.i32(i32 %167, i1 true)
  %169 = sub i32 %168, %78
  %170 = tail call i32 @llvm.smax.i32(i32 %169, i32 0)
  %171 = shl nuw i32 %170, 1
  %172 = sub i32 %168, %171
  %173 = add i32 %73, 4
  %174 = tail call i32 @llvm.abs.i32(i32 %173, i1 true)
  %175 = sub i32 %174, %78
  %176 = tail call i32 @llvm.smax.i32(i32 %175, i32 0)
  %177 = shl nuw i32 %176, 1
  %178 = sub i32 %174, %177
  %179 = tail call i32 @llvm.smax.i32(i32 %172, i32 0)
  %180 = tail call i32 @llvm.smin.i32(i32 %78, i32 %179)
  %181 = add i32 %180, %60
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %58, i64 %182
  %184 = load float, ptr %183, align 4
  %185 = tail call i32 @llvm.smax.i32(i32 %178, i32 0)
  %186 = tail call i32 @llvm.smin.i32(i32 %78, i32 %185)
  %187 = add i32 %186, %60
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, ptr %58, i64 %188
  %190 = load float, ptr %189, align 4
  %191 = fadd reassoc ninf nsz float %190, %184
  %192 = fmul reassoc ninf nsz float %191, %166
  %193 = fadd reassoc ninf nsz float %192, %163
  %factor85 = fmul reassoc ninf nsz float %166, 2.000000e+00
  %194 = fadd reassoc ninf nsz float %factor85, %164
  br i1 %28, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %195 = getelementptr i8, ptr %68, i64 20
  %196 = load float, ptr %195, align 4
  %197 = add i32 %73, -5
  %198 = tail call i32 @llvm.abs.i32(i32 %197, i1 true)
  %199 = sub i32 %198, %78
  %200 = tail call i32 @llvm.smax.i32(i32 %199, i32 0)
  %201 = shl nuw i32 %200, 1
  %202 = sub i32 %198, %201
  %203 = add i32 %73, 5
  %204 = tail call i32 @llvm.abs.i32(i32 %203, i1 true)
  %205 = sub i32 %204, %78
  %206 = tail call i32 @llvm.smax.i32(i32 %205, i32 0)
  %207 = shl nuw i32 %206, 1
  %208 = sub i32 %204, %207
  %209 = tail call i32 @llvm.smax.i32(i32 %202, i32 0)
  %210 = tail call i32 @llvm.smin.i32(i32 %78, i32 %209)
  %211 = add i32 %210, %60
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %58, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = tail call i32 @llvm.smax.i32(i32 %208, i32 0)
  %216 = tail call i32 @llvm.smin.i32(i32 %78, i32 %215)
  %217 = add i32 %216, %60
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, ptr %58, i64 %218
  %220 = load float, ptr %219, align 4
  %221 = fadd reassoc ninf nsz float %220, %214
  %222 = fmul reassoc ninf nsz float %221, %196
  %223 = fadd reassoc ninf nsz float %222, %193
  %factor86 = fmul reassoc ninf nsz float %196, 2.000000e+00
  %224 = fadd reassoc ninf nsz float %factor86, %194
  br i1 %29, label %after_if15, label %after_if45

after_if15:                                       ; preds = %after_if12
  %225 = getelementptr i8, ptr %68, i64 24
  %226 = load float, ptr %225, align 4
  %227 = add i32 %73, -6
  %228 = tail call i32 @llvm.abs.i32(i32 %227, i1 true)
  %229 = sub i32 %228, %78
  %230 = tail call i32 @llvm.smax.i32(i32 %229, i32 0)
  %231 = shl nuw i32 %230, 1
  %232 = sub i32 %228, %231
  %233 = add i32 %73, 6
  %234 = tail call i32 @llvm.abs.i32(i32 %233, i1 true)
  %235 = sub i32 %234, %78
  %236 = tail call i32 @llvm.smax.i32(i32 %235, i32 0)
  %237 = shl nuw i32 %236, 1
  %238 = sub i32 %234, %237
  %239 = tail call i32 @llvm.smax.i32(i32 %232, i32 0)
  %240 = tail call i32 @llvm.smin.i32(i32 %78, i32 %239)
  %241 = add i32 %240, %60
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, ptr %58, i64 %242
  %244 = load float, ptr %243, align 4
  %245 = tail call i32 @llvm.smax.i32(i32 %238, i32 0)
  %246 = tail call i32 @llvm.smin.i32(i32 %78, i32 %245)
  %247 = add i32 %246, %60
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, ptr %58, i64 %248
  %250 = load float, ptr %249, align 4
  %251 = fadd reassoc ninf nsz float %250, %244
  %252 = fmul reassoc ninf nsz float %251, %226
  %253 = fadd reassoc ninf nsz float %252, %223
  %factor87 = fmul reassoc ninf nsz float %226, 2.000000e+00
  %254 = fadd reassoc ninf nsz float %factor87, %224
  br i1 %30, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %255 = getelementptr i8, ptr %68, i64 28
  %256 = load float, ptr %255, align 4
  %257 = add i32 %73, -7
  %258 = tail call i32 @llvm.abs.i32(i32 %257, i1 true)
  %259 = sub i32 %258, %78
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = shl nuw i32 %260, 1
  %262 = sub i32 %258, %261
  %263 = add i32 %73, 7
  %264 = tail call i32 @llvm.abs.i32(i32 %263, i1 true)
  %265 = sub i32 %264, %78
  %266 = tail call i32 @llvm.smax.i32(i32 %265, i32 0)
  %267 = shl nuw i32 %266, 1
  %268 = sub i32 %264, %267
  %269 = tail call i32 @llvm.smax.i32(i32 %262, i32 0)
  %270 = tail call i32 @llvm.smin.i32(i32 %78, i32 %269)
  %271 = add i32 %270, %60
  %272 = sext i32 %271 to i64
  %273 = getelementptr float, ptr %58, i64 %272
  %274 = load float, ptr %273, align 4
  %275 = tail call i32 @llvm.smax.i32(i32 %268, i32 0)
  %276 = tail call i32 @llvm.smin.i32(i32 %78, i32 %275)
  %277 = add i32 %276, %60
  %278 = sext i32 %277 to i64
  %279 = getelementptr float, ptr %58, i64 %278
  %280 = load float, ptr %279, align 4
  %281 = fadd reassoc ninf nsz float %280, %274
  %282 = fmul reassoc ninf nsz float %281, %256
  %283 = fadd reassoc ninf nsz float %282, %253
  %factor88 = fmul reassoc ninf nsz float %256, 2.000000e+00
  %284 = fadd reassoc ninf nsz float %factor88, %254
  br i1 %31, label %after_if21, label %after_if45

after_if21:                                       ; preds = %after_if18
  %285 = getelementptr i8, ptr %68, i64 32
  %286 = load float, ptr %285, align 4
  %287 = add i32 %73, -8
  %288 = tail call i32 @llvm.abs.i32(i32 %287, i1 true)
  %289 = sub i32 %288, %78
  %290 = tail call i32 @llvm.smax.i32(i32 %289, i32 0)
  %291 = shl nuw i32 %290, 1
  %292 = sub i32 %288, %291
  %293 = add i32 %73, 8
  %294 = tail call i32 @llvm.abs.i32(i32 %293, i1 true)
  %295 = sub i32 %294, %78
  %296 = tail call i32 @llvm.smax.i32(i32 %295, i32 0)
  %297 = shl nuw i32 %296, 1
  %298 = sub i32 %294, %297
  %299 = tail call i32 @llvm.smax.i32(i32 %292, i32 0)
  %300 = tail call i32 @llvm.smin.i32(i32 %78, i32 %299)
  %301 = add i32 %300, %60
  %302 = sext i32 %301 to i64
  %303 = getelementptr float, ptr %58, i64 %302
  %304 = load float, ptr %303, align 4
  %305 = tail call i32 @llvm.smax.i32(i32 %298, i32 0)
  %306 = tail call i32 @llvm.smin.i32(i32 %78, i32 %305)
  %307 = add i32 %306, %60
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %58, i64 %308
  %310 = load float, ptr %309, align 4
  %311 = fadd reassoc ninf nsz float %310, %304
  %312 = fmul reassoc ninf nsz float %311, %286
  %313 = fadd reassoc ninf nsz float %312, %283
  %factor89 = fmul reassoc ninf nsz float %286, 2.000000e+00
  %314 = fadd reassoc ninf nsz float %factor89, %284
  br i1 %32, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %315 = getelementptr i8, ptr %68, i64 36
  %316 = load float, ptr %315, align 4
  %317 = add i32 %73, -9
  %318 = tail call i32 @llvm.abs.i32(i32 %317, i1 true)
  %319 = sub i32 %318, %78
  %320 = tail call i32 @llvm.smax.i32(i32 %319, i32 0)
  %321 = shl nuw i32 %320, 1
  %322 = sub i32 %318, %321
  %323 = add i32 %73, 9
  %324 = tail call i32 @llvm.abs.i32(i32 %323, i1 true)
  %325 = sub i32 %324, %78
  %326 = tail call i32 @llvm.smax.i32(i32 %325, i32 0)
  %327 = shl nuw i32 %326, 1
  %328 = sub i32 %324, %327
  %329 = tail call i32 @llvm.smax.i32(i32 %322, i32 0)
  %330 = tail call i32 @llvm.smin.i32(i32 %78, i32 %329)
  %331 = add i32 %330, %60
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, ptr %58, i64 %332
  %334 = load float, ptr %333, align 4
  %335 = tail call i32 @llvm.smax.i32(i32 %328, i32 0)
  %336 = tail call i32 @llvm.smin.i32(i32 %78, i32 %335)
  %337 = add i32 %336, %60
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, ptr %58, i64 %338
  %340 = load float, ptr %339, align 4
  %341 = fadd reassoc ninf nsz float %340, %334
  %342 = fmul reassoc ninf nsz float %341, %316
  %343 = fadd reassoc ninf nsz float %342, %313
  %factor90 = fmul reassoc ninf nsz float %316, 2.000000e+00
  %344 = fadd reassoc ninf nsz float %factor90, %314
  br i1 %33, label %after_if27, label %after_if45

after_if27:                                       ; preds = %after_if24
  %345 = getelementptr i8, ptr %68, i64 40
  %346 = load float, ptr %345, align 4
  %347 = add i32 %73, -10
  %348 = tail call i32 @llvm.abs.i32(i32 %347, i1 true)
  %349 = sub i32 %348, %78
  %350 = tail call i32 @llvm.smax.i32(i32 %349, i32 0)
  %351 = shl nuw i32 %350, 1
  %352 = sub i32 %348, %351
  %353 = add i32 %73, 10
  %354 = tail call i32 @llvm.abs.i32(i32 %353, i1 true)
  %355 = sub i32 %354, %78
  %356 = tail call i32 @llvm.smax.i32(i32 %355, i32 0)
  %357 = shl nuw i32 %356, 1
  %358 = sub i32 %354, %357
  %359 = tail call i32 @llvm.smax.i32(i32 %352, i32 0)
  %360 = tail call i32 @llvm.smin.i32(i32 %78, i32 %359)
  %361 = add i32 %360, %60
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, ptr %58, i64 %362
  %364 = load float, ptr %363, align 4
  %365 = tail call i32 @llvm.smax.i32(i32 %358, i32 0)
  %366 = tail call i32 @llvm.smin.i32(i32 %78, i32 %365)
  %367 = add i32 %366, %60
  %368 = sext i32 %367 to i64
  %369 = getelementptr float, ptr %58, i64 %368
  %370 = load float, ptr %369, align 4
  %371 = fadd reassoc ninf nsz float %370, %364
  %372 = fmul reassoc ninf nsz float %371, %346
  %373 = fadd reassoc ninf nsz float %372, %343
  %factor91 = fmul reassoc ninf nsz float %346, 2.000000e+00
  %374 = fadd reassoc ninf nsz float %factor91, %344
  br i1 %34, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %375 = getelementptr i8, ptr %68, i64 44
  %376 = load float, ptr %375, align 4
  %377 = add i32 %73, -11
  %378 = tail call i32 @llvm.abs.i32(i32 %377, i1 true)
  %379 = sub i32 %378, %78
  %380 = tail call i32 @llvm.smax.i32(i32 %379, i32 0)
  %381 = shl nuw i32 %380, 1
  %382 = sub i32 %378, %381
  %383 = add i32 %73, 11
  %384 = tail call i32 @llvm.abs.i32(i32 %383, i1 true)
  %385 = sub i32 %384, %78
  %386 = tail call i32 @llvm.smax.i32(i32 %385, i32 0)
  %387 = shl nuw i32 %386, 1
  %388 = sub i32 %384, %387
  %389 = tail call i32 @llvm.smax.i32(i32 %382, i32 0)
  %390 = tail call i32 @llvm.smin.i32(i32 %78, i32 %389)
  %391 = add i32 %390, %60
  %392 = sext i32 %391 to i64
  %393 = getelementptr float, ptr %58, i64 %392
  %394 = load float, ptr %393, align 4
  %395 = tail call i32 @llvm.smax.i32(i32 %388, i32 0)
  %396 = tail call i32 @llvm.smin.i32(i32 %78, i32 %395)
  %397 = add i32 %396, %60
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, ptr %58, i64 %398
  %400 = load float, ptr %399, align 4
  %401 = fadd reassoc ninf nsz float %400, %394
  %402 = fmul reassoc ninf nsz float %401, %376
  %403 = fadd reassoc ninf nsz float %402, %373
  %factor92 = fmul reassoc ninf nsz float %376, 2.000000e+00
  %404 = fadd reassoc ninf nsz float %factor92, %374
  br i1 %35, label %after_if33, label %after_if45

after_if33:                                       ; preds = %after_if30
  %405 = getelementptr i8, ptr %68, i64 48
  %406 = load float, ptr %405, align 4
  %407 = add i32 %73, -12
  %408 = tail call i32 @llvm.abs.i32(i32 %407, i1 true)
  %409 = sub i32 %408, %78
  %410 = tail call i32 @llvm.smax.i32(i32 %409, i32 0)
  %411 = shl nuw i32 %410, 1
  %412 = sub i32 %408, %411
  %413 = add i32 %73, 12
  %414 = tail call i32 @llvm.abs.i32(i32 %413, i1 true)
  %415 = sub i32 %414, %78
  %416 = tail call i32 @llvm.smax.i32(i32 %415, i32 0)
  %417 = shl nuw i32 %416, 1
  %418 = sub i32 %414, %417
  %419 = tail call i32 @llvm.smax.i32(i32 %412, i32 0)
  %420 = tail call i32 @llvm.smin.i32(i32 %78, i32 %419)
  %421 = add i32 %420, %60
  %422 = sext i32 %421 to i64
  %423 = getelementptr float, ptr %58, i64 %422
  %424 = load float, ptr %423, align 4
  %425 = tail call i32 @llvm.smax.i32(i32 %418, i32 0)
  %426 = tail call i32 @llvm.smin.i32(i32 %78, i32 %425)
  %427 = add i32 %426, %60
  %428 = sext i32 %427 to i64
  %429 = getelementptr float, ptr %58, i64 %428
  %430 = load float, ptr %429, align 4
  %431 = fadd reassoc ninf nsz float %430, %424
  %432 = fmul reassoc ninf nsz float %431, %406
  %433 = fadd reassoc ninf nsz float %432, %403
  %factor93 = fmul reassoc ninf nsz float %406, 2.000000e+00
  %434 = fadd reassoc ninf nsz float %factor93, %404
  br i1 %36, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %435 = getelementptr i8, ptr %68, i64 52
  %436 = load float, ptr %435, align 4
  %437 = add i32 %73, -13
  %438 = tail call i32 @llvm.abs.i32(i32 %437, i1 true)
  %439 = sub i32 %438, %78
  %440 = tail call i32 @llvm.smax.i32(i32 %439, i32 0)
  %441 = shl nuw i32 %440, 1
  %442 = sub i32 %438, %441
  %443 = add i32 %73, 13
  %444 = tail call i32 @llvm.abs.i32(i32 %443, i1 true)
  %445 = sub i32 %444, %78
  %446 = tail call i32 @llvm.smax.i32(i32 %445, i32 0)
  %447 = shl nuw i32 %446, 1
  %448 = sub i32 %444, %447
  %449 = tail call i32 @llvm.smax.i32(i32 %442, i32 0)
  %450 = tail call i32 @llvm.smin.i32(i32 %78, i32 %449)
  %451 = add i32 %450, %60
  %452 = sext i32 %451 to i64
  %453 = getelementptr float, ptr %58, i64 %452
  %454 = load float, ptr %453, align 4
  %455 = tail call i32 @llvm.smax.i32(i32 %448, i32 0)
  %456 = tail call i32 @llvm.smin.i32(i32 %78, i32 %455)
  %457 = add i32 %456, %60
  %458 = sext i32 %457 to i64
  %459 = getelementptr float, ptr %58, i64 %458
  %460 = load float, ptr %459, align 4
  %461 = fadd reassoc ninf nsz float %460, %454
  %462 = fmul reassoc ninf nsz float %461, %436
  %463 = fadd reassoc ninf nsz float %462, %433
  %factor94 = fmul reassoc ninf nsz float %436, 2.000000e+00
  %464 = fadd reassoc ninf nsz float %factor94, %434
  br i1 %37, label %after_if39, label %after_if45

after_if39:                                       ; preds = %after_if36
  %465 = getelementptr i8, ptr %68, i64 56
  %466 = load float, ptr %465, align 4
  %467 = add i32 %73, -14
  %468 = tail call i32 @llvm.abs.i32(i32 %467, i1 true)
  %469 = sub i32 %468, %78
  %470 = tail call i32 @llvm.smax.i32(i32 %469, i32 0)
  %471 = shl nuw i32 %470, 1
  %472 = sub i32 %468, %471
  %473 = add i32 %73, 14
  %474 = tail call i32 @llvm.abs.i32(i32 %473, i1 true)
  %475 = sub i32 %474, %78
  %476 = tail call i32 @llvm.smax.i32(i32 %475, i32 0)
  %477 = shl nuw i32 %476, 1
  %478 = sub i32 %474, %477
  %479 = tail call i32 @llvm.smax.i32(i32 %472, i32 0)
  %480 = tail call i32 @llvm.smin.i32(i32 %78, i32 %479)
  %481 = add i32 %480, %60
  %482 = sext i32 %481 to i64
  %483 = getelementptr float, ptr %58, i64 %482
  %484 = load float, ptr %483, align 4
  %485 = tail call i32 @llvm.smax.i32(i32 %478, i32 0)
  %486 = tail call i32 @llvm.smin.i32(i32 %78, i32 %485)
  %487 = add i32 %486, %60
  %488 = sext i32 %487 to i64
  %489 = getelementptr float, ptr %58, i64 %488
  %490 = load float, ptr %489, align 4
  %491 = fadd reassoc ninf nsz float %490, %484
  %492 = fmul reassoc ninf nsz float %491, %466
  %493 = fadd reassoc ninf nsz float %492, %463
  %factor95 = fmul reassoc ninf nsz float %466, 2.000000e+00
  %494 = fadd reassoc ninf nsz float %factor95, %464
  br i1 %38, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %495 = getelementptr i8, ptr %68, i64 60
  %496 = load float, ptr %495, align 4
  %497 = add i32 %73, -15
  %498 = tail call i32 @llvm.abs.i32(i32 %497, i1 true)
  %499 = sub i32 %498, %78
  %500 = tail call i32 @llvm.smax.i32(i32 %499, i32 0)
  %501 = shl nuw i32 %500, 1
  %502 = sub i32 %498, %501
  %503 = add i32 %73, 15
  %504 = tail call i32 @llvm.abs.i32(i32 %503, i1 true)
  %505 = sub i32 %504, %78
  %506 = tail call i32 @llvm.smax.i32(i32 %505, i32 0)
  %507 = shl nuw i32 %506, 1
  %508 = sub i32 %504, %507
  %509 = tail call i32 @llvm.smax.i32(i32 %502, i32 0)
  %510 = tail call i32 @llvm.smin.i32(i32 %78, i32 %509)
  %511 = add i32 %510, %60
  %512 = sext i32 %511 to i64
  %513 = getelementptr float, ptr %58, i64 %512
  %514 = load float, ptr %513, align 4
  %515 = tail call i32 @llvm.smax.i32(i32 %508, i32 0)
  %516 = tail call i32 @llvm.smin.i32(i32 %78, i32 %515)
  %517 = add i32 %516, %60
  %518 = sext i32 %517 to i64
  %519 = getelementptr float, ptr %58, i64 %518
  %520 = load float, ptr %519, align 4
  %521 = fadd reassoc ninf nsz float %520, %514
  %522 = fmul reassoc ninf nsz float %521, %496
  %523 = fadd reassoc ninf nsz float %522, %493
  %factor96 = fmul reassoc ninf nsz float %496, 2.000000e+00
  %524 = fadd reassoc ninf nsz float %factor96, %494
  br i1 %39, label %true_block43, label %after_if45

true_block43:                                     ; preds = %after_if42
  %525 = getelementptr i8, ptr %68, i64 64
  %526 = load float, ptr %525, align 4
  %527 = add i32 %73, -16
  %528 = tail call i32 @llvm.abs.i32(i32 %527, i1 true)
  %529 = sub i32 %528, %78
  %530 = tail call i32 @llvm.smax.i32(i32 %529, i32 0)
  %531 = shl nuw i32 %530, 1
  %532 = sub i32 %528, %531
  %533 = add i32 %73, 16
  %534 = tail call i32 @llvm.abs.i32(i32 %533, i1 true)
  %535 = sub i32 %534, %78
  %536 = tail call i32 @llvm.smax.i32(i32 %535, i32 0)
  %537 = shl nuw i32 %536, 1
  %538 = sub i32 %534, %537
  %539 = tail call i32 @llvm.smax.i32(i32 %532, i32 0)
  %540 = tail call i32 @llvm.smin.i32(i32 %78, i32 %539)
  %541 = add i32 %540, %60
  %542 = sext i32 %541 to i64
  %543 = getelementptr float, ptr %58, i64 %542
  %544 = load float, ptr %543, align 4
  %545 = tail call i32 @llvm.smax.i32(i32 %538, i32 0)
  %546 = tail call i32 @llvm.smin.i32(i32 %78, i32 %545)
  %547 = add i32 %546, %60
  %548 = sext i32 %547 to i64
  %549 = getelementptr float, ptr %58, i64 %548
  %550 = load float, ptr %549, align 4
  %551 = fadd reassoc ninf nsz float %550, %544
  %552 = fmul reassoc ninf nsz float %551, %526
  %553 = fadd reassoc ninf nsz float %552, %523
  %factor97 = fmul reassoc ninf nsz float %526, 2.000000e+00
  %554 = fadd reassoc ninf nsz float %factor97, %524
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.1550 = phi float [ %553, %true_block43 ], [ %523, %after_if42 ], [ %493, %after_if39 ], [ %463, %after_if36 ], [ %433, %after_if33 ], [ %403, %after_if30 ], [ %373, %after_if27 ], [ %343, %after_if24 ], [ %313, %after_if21 ], [ %283, %after_if18 ], [ %253, %after_if15 ], [ %223, %after_if12 ], [ %193, %after_if9 ], [ %163, %after_if6 ], [ %133, %after_if3 ], [ %103, %after_if ], [ %67, %for_loop_body ]
  %.15 = phi float [ %554, %true_block43 ], [ %524, %after_if42 ], [ %494, %after_if39 ], [ %464, %after_if36 ], [ %434, %after_if33 ], [ %404, %after_if30 ], [ %374, %after_if27 ], [ %344, %after_if24 ], [ %314, %after_if21 ], [ %284, %after_if18 ], [ %254, %after_if15 ], [ %224, %after_if12 ], [ %194, %after_if9 ], [ %164, %after_if6 ], [ %134, %after_if3 ], [ %104, %after_if ], [ %57, %for_loop_body ]
  %555 = fdiv reassoc ninf nsz float %.1550, %.15
  %556 = load ptr, ptr %43, align 8
  %557 = load i32, ptr %44, align 4
  %558 = sub i32 %557, %49
  %559 = mul i32 %558, %56
  %560 = add i32 %.05198, %559
  %561 = sext i32 %560 to i64
  %562 = getelementptr float, ptr %556, i64 %561
  store float %555, ptr %562, align 4
  %563 = add nsw i32 %.05198, 1
  %exitcond.not = icmp eq i32 %18, %563
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.3, align 8
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
