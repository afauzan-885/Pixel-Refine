; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gaussian_blur_x_3ch_f32_kernel_c188_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 52
  %4 = load i32, ptr %3, align 4
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 12
  store i32 %4, ptr %9, align 4
  %10 = load ptr, ptr %context, align 8
  %11 = getelementptr i8, ptr %10, i64 72
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

define void @_gaussian_blur_x_3ch_f32_kernel_c188_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %.091145 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %627, %after_if45 ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.091145, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.091145
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.091145, %35
  %39 = and i1 %37, %38
  %.neg92 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg92
  %41 = load float, ptr %21, align 4
  %42 = load ptr, ptr %23, align 8
  %43 = load i32, ptr %24, align 4
  %44 = load i32, ptr %25, align 4
  %45 = mul i32 %40, %43
  %46 = sub i32 %43, %33
  %47 = mul i32 %46, %40
  %48 = add i32 %.091145, %47
  %49 = mul i32 %48, %44
  %50 = add i32 %49, 2
  %51 = sext i32 %50 to i64
  %52 = getelementptr float, ptr %42, i64 %51
  %53 = load float, ptr %52, align 4
  %54 = fmul reassoc ninf nsz float %53, %41
  %55 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %56 = load i32, ptr %55, align 4
  %57 = icmp sgt i32 %56, 0
  br i1 %57, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %58 = load ptr, ptr %20, align 8
  %59 = getelementptr i8, ptr %58, i64 4
  %60 = load float, ptr %59, align 4
  %61 = mul i32 %33, -1
  %62 = mul i32 %61, %40
  %63 = add i32 %.091145, %62
  %64 = add i32 %63, -1
  %65 = tail call i32 @llvm.abs.i32(i32 %64, i1 true)
  %66 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %67 = load i32, ptr %66, align 4
  %68 = add i32 %67, -1
  %69 = sub i32 %65, %68
  %70 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %71 = shl nuw i32 %70, 1
  %72 = sub i32 %65, %71
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = tail call i32 @llvm.smin.i32(i32 %68, i32 %73)
  %75 = add i32 %63, 1
  %76 = tail call i32 @llvm.abs.i32(i32 %75, i1 true)
  %77 = sub i32 %76, %68
  %78 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %79 = shl nuw i32 %78, 1
  %80 = sub i32 %76, %79
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = tail call i32 @llvm.smin.i32(i32 %68, i32 %81)
  %83 = add i32 %74, %45
  %84 = mul i32 %83, %44
  %85 = add i32 %82, %45
  %86 = mul i32 %85, %44
  %87 = add i32 %84, 2
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %42, i64 %88
  %90 = load float, ptr %89, align 4
  %91 = add i32 %86, 2
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %42, i64 %92
  %94 = load float, ptr %93, align 4
  %95 = fadd reassoc ninf nsz float %94, %90
  %96 = fmul reassoc ninf nsz float %95, %60
  %97 = fadd reassoc ninf nsz float %96, %54
  %factor = fmul reassoc ninf nsz float %60, 2.000000e+00
  %98 = fadd reassoc ninf nsz float %factor, %41
  %.not = icmp eq i32 %56, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %99 = getelementptr i8, ptr %58, i64 8
  %100 = load float, ptr %99, align 4
  %101 = add i32 %63, -2
  %102 = tail call i32 @llvm.abs.i32(i32 %101, i1 true)
  %103 = sub i32 %102, %68
  %104 = tail call i32 @llvm.smax.i32(i32 %103, i32 0)
  %105 = shl nuw i32 %104, 1
  %106 = sub i32 %102, %105
  %107 = tail call i32 @llvm.smax.i32(i32 %106, i32 0)
  %108 = tail call i32 @llvm.smin.i32(i32 %68, i32 %107)
  %109 = add i32 %63, 2
  %110 = tail call i32 @llvm.abs.i32(i32 %109, i1 true)
  %111 = sub i32 %110, %68
  %112 = tail call i32 @llvm.smax.i32(i32 %111, i32 0)
  %113 = shl nuw i32 %112, 1
  %114 = sub i32 %110, %113
  %115 = tail call i32 @llvm.smax.i32(i32 %114, i32 0)
  %116 = tail call i32 @llvm.smin.i32(i32 %68, i32 %115)
  %117 = add i32 %108, %45
  %118 = mul i32 %117, %44
  %119 = add i32 %116, %45
  %120 = mul i32 %119, %44
  %121 = add i32 %118, 2
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %42, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = add i32 %120, 2
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %42, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = fadd reassoc ninf nsz float %128, %124
  %130 = fmul reassoc ninf nsz float %129, %100
  %131 = fadd reassoc ninf nsz float %130, %97
  %factor130 = fmul reassoc ninf nsz float %100, 2.000000e+00
  %132 = fadd reassoc ninf nsz float %factor130, %98
  %133 = icmp samesign ugt i32 %56, 2
  br i1 %133, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %134 = getelementptr i8, ptr %58, i64 12
  %135 = load float, ptr %134, align 4
  %136 = add i32 %63, -3
  %137 = tail call i32 @llvm.abs.i32(i32 %136, i1 true)
  %138 = sub i32 %137, %68
  %139 = tail call i32 @llvm.smax.i32(i32 %138, i32 0)
  %140 = shl nuw i32 %139, 1
  %141 = sub i32 %137, %140
  %142 = tail call i32 @llvm.smax.i32(i32 %141, i32 0)
  %143 = tail call i32 @llvm.smin.i32(i32 %68, i32 %142)
  %144 = add i32 %63, 3
  %145 = tail call i32 @llvm.abs.i32(i32 %144, i1 true)
  %146 = sub i32 %145, %68
  %147 = tail call i32 @llvm.smax.i32(i32 %146, i32 0)
  %148 = shl nuw i32 %147, 1
  %149 = sub i32 %145, %148
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = tail call i32 @llvm.smin.i32(i32 %68, i32 %150)
  %152 = add i32 %143, %45
  %153 = mul i32 %152, %44
  %154 = add i32 %151, %45
  %155 = mul i32 %154, %44
  %156 = add i32 %153, 2
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %42, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = add i32 %155, 2
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %42, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = fadd reassoc ninf nsz float %163, %159
  %165 = fmul reassoc ninf nsz float %164, %135
  %166 = fadd reassoc ninf nsz float %165, %131
  %factor131 = fmul reassoc ninf nsz float %135, 2.000000e+00
  %167 = fadd reassoc ninf nsz float %factor131, %132
  %.not123 = icmp eq i32 %56, 3
  br i1 %.not123, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %168 = getelementptr i8, ptr %58, i64 16
  %169 = load float, ptr %168, align 4
  %170 = add i32 %63, -4
  %171 = tail call i32 @llvm.abs.i32(i32 %170, i1 true)
  %172 = sub i32 %171, %68
  %173 = tail call i32 @llvm.smax.i32(i32 %172, i32 0)
  %174 = shl nuw i32 %173, 1
  %175 = sub i32 %171, %174
  %176 = tail call i32 @llvm.smax.i32(i32 %175, i32 0)
  %177 = tail call i32 @llvm.smin.i32(i32 %68, i32 %176)
  %178 = add i32 %63, 4
  %179 = tail call i32 @llvm.abs.i32(i32 %178, i1 true)
  %180 = sub i32 %179, %68
  %181 = tail call i32 @llvm.smax.i32(i32 %180, i32 0)
  %182 = shl nuw i32 %181, 1
  %183 = sub i32 %179, %182
  %184 = tail call i32 @llvm.smax.i32(i32 %183, i32 0)
  %185 = tail call i32 @llvm.smin.i32(i32 %68, i32 %184)
  %186 = add i32 %177, %45
  %187 = mul i32 %186, %44
  %188 = add i32 %185, %45
  %189 = mul i32 %188, %44
  %190 = add i32 %187, 2
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, ptr %42, i64 %191
  %193 = load float, ptr %192, align 4
  %194 = add i32 %189, 2
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, ptr %42, i64 %195
  %197 = load float, ptr %196, align 4
  %198 = fadd reassoc ninf nsz float %197, %193
  %199 = fmul reassoc ninf nsz float %198, %169
  %200 = fadd reassoc ninf nsz float %199, %166
  %factor132 = fmul reassoc ninf nsz float %169, 2.000000e+00
  %201 = fadd reassoc ninf nsz float %factor132, %167
  %202 = icmp samesign ugt i32 %56, 4
  br i1 %202, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %203 = getelementptr i8, ptr %58, i64 20
  %204 = load float, ptr %203, align 4
  %205 = add i32 %63, -5
  %206 = tail call i32 @llvm.abs.i32(i32 %205, i1 true)
  %207 = sub i32 %206, %68
  %208 = tail call i32 @llvm.smax.i32(i32 %207, i32 0)
  %209 = shl nuw i32 %208, 1
  %210 = sub i32 %206, %209
  %211 = tail call i32 @llvm.smax.i32(i32 %210, i32 0)
  %212 = tail call i32 @llvm.smin.i32(i32 %68, i32 %211)
  %213 = add i32 %63, 5
  %214 = tail call i32 @llvm.abs.i32(i32 %213, i1 true)
  %215 = sub i32 %214, %68
  %216 = tail call i32 @llvm.smax.i32(i32 %215, i32 0)
  %217 = shl nuw i32 %216, 1
  %218 = sub i32 %214, %217
  %219 = tail call i32 @llvm.smax.i32(i32 %218, i32 0)
  %220 = tail call i32 @llvm.smin.i32(i32 %68, i32 %219)
  %221 = add i32 %212, %45
  %222 = mul i32 %221, %44
  %223 = add i32 %220, %45
  %224 = mul i32 %223, %44
  %225 = add i32 %222, 2
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %42, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = add i32 %224, 2
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, ptr %42, i64 %230
  %232 = load float, ptr %231, align 4
  %233 = fadd reassoc ninf nsz float %232, %228
  %234 = fmul reassoc ninf nsz float %233, %204
  %235 = fadd reassoc ninf nsz float %234, %200
  %factor133 = fmul reassoc ninf nsz float %204, 2.000000e+00
  %236 = fadd reassoc ninf nsz float %factor133, %201
  %.not124 = icmp eq i32 %56, 5
  br i1 %.not124, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %237 = getelementptr i8, ptr %58, i64 24
  %238 = load float, ptr %237, align 4
  %239 = add i32 %63, -6
  %240 = tail call i32 @llvm.abs.i32(i32 %239, i1 true)
  %241 = sub i32 %240, %68
  %242 = tail call i32 @llvm.smax.i32(i32 %241, i32 0)
  %243 = shl nuw i32 %242, 1
  %244 = sub i32 %240, %243
  %245 = tail call i32 @llvm.smax.i32(i32 %244, i32 0)
  %246 = tail call i32 @llvm.smin.i32(i32 %68, i32 %245)
  %247 = add i32 %63, 6
  %248 = tail call i32 @llvm.abs.i32(i32 %247, i1 true)
  %249 = sub i32 %248, %68
  %250 = tail call i32 @llvm.smax.i32(i32 %249, i32 0)
  %251 = shl nuw i32 %250, 1
  %252 = sub i32 %248, %251
  %253 = tail call i32 @llvm.smax.i32(i32 %252, i32 0)
  %254 = tail call i32 @llvm.smin.i32(i32 %68, i32 %253)
  %255 = add i32 %246, %45
  %256 = mul i32 %255, %44
  %257 = add i32 %254, %45
  %258 = mul i32 %257, %44
  %259 = add i32 %256, 2
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, ptr %42, i64 %260
  %262 = load float, ptr %261, align 4
  %263 = add i32 %258, 2
  %264 = sext i32 %263 to i64
  %265 = getelementptr float, ptr %42, i64 %264
  %266 = load float, ptr %265, align 4
  %267 = fadd reassoc ninf nsz float %266, %262
  %268 = fmul reassoc ninf nsz float %267, %238
  %269 = fadd reassoc ninf nsz float %268, %235
  %factor134 = fmul reassoc ninf nsz float %238, 2.000000e+00
  %270 = fadd reassoc ninf nsz float %factor134, %236
  %271 = icmp samesign ugt i32 %56, 6
  br i1 %271, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %272 = getelementptr i8, ptr %58, i64 28
  %273 = load float, ptr %272, align 4
  %274 = add i32 %63, -7
  %275 = tail call i32 @llvm.abs.i32(i32 %274, i1 true)
  %276 = sub i32 %275, %68
  %277 = tail call i32 @llvm.smax.i32(i32 %276, i32 0)
  %278 = shl nuw i32 %277, 1
  %279 = sub i32 %275, %278
  %280 = tail call i32 @llvm.smax.i32(i32 %279, i32 0)
  %281 = tail call i32 @llvm.smin.i32(i32 %68, i32 %280)
  %282 = add i32 %63, 7
  %283 = tail call i32 @llvm.abs.i32(i32 %282, i1 true)
  %284 = sub i32 %283, %68
  %285 = tail call i32 @llvm.smax.i32(i32 %284, i32 0)
  %286 = shl nuw i32 %285, 1
  %287 = sub i32 %283, %286
  %288 = tail call i32 @llvm.smax.i32(i32 %287, i32 0)
  %289 = tail call i32 @llvm.smin.i32(i32 %68, i32 %288)
  %290 = add i32 %281, %45
  %291 = mul i32 %290, %44
  %292 = add i32 %289, %45
  %293 = mul i32 %292, %44
  %294 = add i32 %291, 2
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, ptr %42, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = add i32 %293, 2
  %299 = sext i32 %298 to i64
  %300 = getelementptr float, ptr %42, i64 %299
  %301 = load float, ptr %300, align 4
  %302 = fadd reassoc ninf nsz float %301, %297
  %303 = fmul reassoc ninf nsz float %302, %273
  %304 = fadd reassoc ninf nsz float %303, %269
  %factor135 = fmul reassoc ninf nsz float %273, 2.000000e+00
  %305 = fadd reassoc ninf nsz float %factor135, %270
  %.not125 = icmp eq i32 %56, 7
  br i1 %.not125, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %306 = getelementptr i8, ptr %58, i64 32
  %307 = load float, ptr %306, align 4
  %308 = add i32 %63, -8
  %309 = tail call i32 @llvm.abs.i32(i32 %308, i1 true)
  %310 = sub i32 %309, %68
  %311 = tail call i32 @llvm.smax.i32(i32 %310, i32 0)
  %312 = shl nuw i32 %311, 1
  %313 = sub i32 %309, %312
  %314 = tail call i32 @llvm.smax.i32(i32 %313, i32 0)
  %315 = tail call i32 @llvm.smin.i32(i32 %68, i32 %314)
  %316 = add i32 %63, 8
  %317 = tail call i32 @llvm.abs.i32(i32 %316, i1 true)
  %318 = sub i32 %317, %68
  %319 = tail call i32 @llvm.smax.i32(i32 %318, i32 0)
  %320 = shl nuw i32 %319, 1
  %321 = sub i32 %317, %320
  %322 = tail call i32 @llvm.smax.i32(i32 %321, i32 0)
  %323 = tail call i32 @llvm.smin.i32(i32 %68, i32 %322)
  %324 = add i32 %315, %45
  %325 = mul i32 %324, %44
  %326 = add i32 %323, %45
  %327 = mul i32 %326, %44
  %328 = add i32 %325, 2
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, ptr %42, i64 %329
  %331 = load float, ptr %330, align 4
  %332 = add i32 %327, 2
  %333 = sext i32 %332 to i64
  %334 = getelementptr float, ptr %42, i64 %333
  %335 = load float, ptr %334, align 4
  %336 = fadd reassoc ninf nsz float %335, %331
  %337 = fmul reassoc ninf nsz float %336, %307
  %338 = fadd reassoc ninf nsz float %337, %304
  %factor136 = fmul reassoc ninf nsz float %307, 2.000000e+00
  %339 = fadd reassoc ninf nsz float %factor136, %305
  %340 = icmp samesign ugt i32 %56, 8
  br i1 %340, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %341 = getelementptr i8, ptr %58, i64 36
  %342 = load float, ptr %341, align 4
  %343 = add i32 %63, -9
  %344 = tail call i32 @llvm.abs.i32(i32 %343, i1 true)
  %345 = sub i32 %344, %68
  %346 = tail call i32 @llvm.smax.i32(i32 %345, i32 0)
  %347 = shl nuw i32 %346, 1
  %348 = sub i32 %344, %347
  %349 = tail call i32 @llvm.smax.i32(i32 %348, i32 0)
  %350 = tail call i32 @llvm.smin.i32(i32 %68, i32 %349)
  %351 = add i32 %63, 9
  %352 = tail call i32 @llvm.abs.i32(i32 %351, i1 true)
  %353 = sub i32 %352, %68
  %354 = tail call i32 @llvm.smax.i32(i32 %353, i32 0)
  %355 = shl nuw i32 %354, 1
  %356 = sub i32 %352, %355
  %357 = tail call i32 @llvm.smax.i32(i32 %356, i32 0)
  %358 = tail call i32 @llvm.smin.i32(i32 %68, i32 %357)
  %359 = add i32 %350, %45
  %360 = mul i32 %359, %44
  %361 = add i32 %358, %45
  %362 = mul i32 %361, %44
  %363 = add i32 %360, 2
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, ptr %42, i64 %364
  %366 = load float, ptr %365, align 4
  %367 = add i32 %362, 2
  %368 = sext i32 %367 to i64
  %369 = getelementptr float, ptr %42, i64 %368
  %370 = load float, ptr %369, align 4
  %371 = fadd reassoc ninf nsz float %370, %366
  %372 = fmul reassoc ninf nsz float %371, %342
  %373 = fadd reassoc ninf nsz float %372, %338
  %factor137 = fmul reassoc ninf nsz float %342, 2.000000e+00
  %374 = fadd reassoc ninf nsz float %factor137, %339
  %.not126 = icmp eq i32 %56, 9
  br i1 %.not126, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %375 = getelementptr i8, ptr %58, i64 40
  %376 = load float, ptr %375, align 4
  %377 = add i32 %63, -10
  %378 = tail call i32 @llvm.abs.i32(i32 %377, i1 true)
  %379 = sub i32 %378, %68
  %380 = tail call i32 @llvm.smax.i32(i32 %379, i32 0)
  %381 = shl nuw i32 %380, 1
  %382 = sub i32 %378, %381
  %383 = tail call i32 @llvm.smax.i32(i32 %382, i32 0)
  %384 = tail call i32 @llvm.smin.i32(i32 %68, i32 %383)
  %385 = add i32 %63, 10
  %386 = tail call i32 @llvm.abs.i32(i32 %385, i1 true)
  %387 = sub i32 %386, %68
  %388 = tail call i32 @llvm.smax.i32(i32 %387, i32 0)
  %389 = shl nuw i32 %388, 1
  %390 = sub i32 %386, %389
  %391 = tail call i32 @llvm.smax.i32(i32 %390, i32 0)
  %392 = tail call i32 @llvm.smin.i32(i32 %68, i32 %391)
  %393 = add i32 %384, %45
  %394 = mul i32 %393, %44
  %395 = add i32 %392, %45
  %396 = mul i32 %395, %44
  %397 = add i32 %394, 2
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, ptr %42, i64 %398
  %400 = load float, ptr %399, align 4
  %401 = add i32 %396, 2
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, ptr %42, i64 %402
  %404 = load float, ptr %403, align 4
  %405 = fadd reassoc ninf nsz float %404, %400
  %406 = fmul reassoc ninf nsz float %405, %376
  %407 = fadd reassoc ninf nsz float %406, %373
  %factor138 = fmul reassoc ninf nsz float %376, 2.000000e+00
  %408 = fadd reassoc ninf nsz float %factor138, %374
  %409 = icmp samesign ugt i32 %56, 10
  br i1 %409, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %410 = getelementptr i8, ptr %58, i64 44
  %411 = load float, ptr %410, align 4
  %412 = add i32 %63, -11
  %413 = tail call i32 @llvm.abs.i32(i32 %412, i1 true)
  %414 = sub i32 %413, %68
  %415 = tail call i32 @llvm.smax.i32(i32 %414, i32 0)
  %416 = shl nuw i32 %415, 1
  %417 = sub i32 %413, %416
  %418 = tail call i32 @llvm.smax.i32(i32 %417, i32 0)
  %419 = tail call i32 @llvm.smin.i32(i32 %68, i32 %418)
  %420 = add i32 %63, 11
  %421 = tail call i32 @llvm.abs.i32(i32 %420, i1 true)
  %422 = sub i32 %421, %68
  %423 = tail call i32 @llvm.smax.i32(i32 %422, i32 0)
  %424 = shl nuw i32 %423, 1
  %425 = sub i32 %421, %424
  %426 = tail call i32 @llvm.smax.i32(i32 %425, i32 0)
  %427 = tail call i32 @llvm.smin.i32(i32 %68, i32 %426)
  %428 = add i32 %419, %45
  %429 = mul i32 %428, %44
  %430 = add i32 %427, %45
  %431 = mul i32 %430, %44
  %432 = add i32 %429, 2
  %433 = sext i32 %432 to i64
  %434 = getelementptr float, ptr %42, i64 %433
  %435 = load float, ptr %434, align 4
  %436 = add i32 %431, 2
  %437 = sext i32 %436 to i64
  %438 = getelementptr float, ptr %42, i64 %437
  %439 = load float, ptr %438, align 4
  %440 = fadd reassoc ninf nsz float %439, %435
  %441 = fmul reassoc ninf nsz float %440, %411
  %442 = fadd reassoc ninf nsz float %441, %407
  %factor139 = fmul reassoc ninf nsz float %411, 2.000000e+00
  %443 = fadd reassoc ninf nsz float %factor139, %408
  %.not127 = icmp eq i32 %56, 11
  br i1 %.not127, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %444 = getelementptr i8, ptr %58, i64 48
  %445 = load float, ptr %444, align 4
  %446 = add i32 %63, -12
  %447 = tail call i32 @llvm.abs.i32(i32 %446, i1 true)
  %448 = sub i32 %447, %68
  %449 = tail call i32 @llvm.smax.i32(i32 %448, i32 0)
  %450 = shl nuw i32 %449, 1
  %451 = sub i32 %447, %450
  %452 = tail call i32 @llvm.smax.i32(i32 %451, i32 0)
  %453 = tail call i32 @llvm.smin.i32(i32 %68, i32 %452)
  %454 = add i32 %63, 12
  %455 = tail call i32 @llvm.abs.i32(i32 %454, i1 true)
  %456 = sub i32 %455, %68
  %457 = tail call i32 @llvm.smax.i32(i32 %456, i32 0)
  %458 = shl nuw i32 %457, 1
  %459 = sub i32 %455, %458
  %460 = tail call i32 @llvm.smax.i32(i32 %459, i32 0)
  %461 = tail call i32 @llvm.smin.i32(i32 %68, i32 %460)
  %462 = add i32 %453, %45
  %463 = mul i32 %462, %44
  %464 = add i32 %463, 2
  %465 = sext i32 %464 to i64
  %466 = getelementptr float, ptr %42, i64 %465
  %467 = load float, ptr %466, align 4
  %468 = add i32 %461, %45
  %469 = mul i32 %468, %44
  %470 = add i32 %469, 2
  %471 = sext i32 %470 to i64
  %472 = getelementptr float, ptr %42, i64 %471
  %473 = load float, ptr %472, align 4
  %474 = fadd reassoc ninf nsz float %473, %467
  %475 = fmul reassoc ninf nsz float %474, %445
  %476 = fadd reassoc ninf nsz float %475, %442
  %factor140 = fmul reassoc ninf nsz float %445, 2.000000e+00
  %477 = fadd reassoc ninf nsz float %factor140, %443
  %478 = icmp samesign ugt i32 %56, 12
  br i1 %478, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %479 = getelementptr i8, ptr %58, i64 52
  %480 = load float, ptr %479, align 4
  %481 = add i32 %63, -13
  %482 = tail call i32 @llvm.abs.i32(i32 %481, i1 true)
  %483 = sub i32 %482, %68
  %484 = tail call i32 @llvm.smax.i32(i32 %483, i32 0)
  %485 = shl nuw i32 %484, 1
  %486 = sub i32 %482, %485
  %487 = tail call i32 @llvm.smax.i32(i32 %486, i32 0)
  %488 = tail call i32 @llvm.smin.i32(i32 %68, i32 %487)
  %489 = add i32 %63, 13
  %490 = tail call i32 @llvm.abs.i32(i32 %489, i1 true)
  %491 = sub i32 %490, %68
  %492 = tail call i32 @llvm.smax.i32(i32 %491, i32 0)
  %493 = shl nuw i32 %492, 1
  %494 = sub i32 %490, %493
  %495 = tail call i32 @llvm.smax.i32(i32 %494, i32 0)
  %496 = tail call i32 @llvm.smin.i32(i32 %68, i32 %495)
  %497 = add i32 %488, %45
  %498 = mul i32 %497, %44
  %499 = add i32 %498, 2
  %500 = sext i32 %499 to i64
  %501 = getelementptr float, ptr %42, i64 %500
  %502 = load float, ptr %501, align 4
  %503 = add i32 %496, %45
  %504 = mul i32 %503, %44
  %505 = add i32 %504, 2
  %506 = sext i32 %505 to i64
  %507 = getelementptr float, ptr %42, i64 %506
  %508 = load float, ptr %507, align 4
  %509 = fadd reassoc ninf nsz float %508, %502
  %510 = fmul reassoc ninf nsz float %509, %480
  %511 = fadd reassoc ninf nsz float %510, %476
  %factor141 = fmul reassoc ninf nsz float %480, 2.000000e+00
  %512 = fadd reassoc ninf nsz float %factor141, %477
  %.not128 = icmp eq i32 %56, 13
  br i1 %.not128, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %513 = getelementptr i8, ptr %58, i64 56
  %514 = load float, ptr %513, align 4
  %515 = add i32 %63, -14
  %516 = tail call i32 @llvm.abs.i32(i32 %515, i1 true)
  %517 = sub i32 %516, %68
  %518 = tail call i32 @llvm.smax.i32(i32 %517, i32 0)
  %519 = shl nuw i32 %518, 1
  %520 = sub i32 %516, %519
  %521 = tail call i32 @llvm.smax.i32(i32 %520, i32 0)
  %522 = tail call i32 @llvm.smin.i32(i32 %68, i32 %521)
  %523 = add i32 %63, 14
  %524 = tail call i32 @llvm.abs.i32(i32 %523, i1 true)
  %525 = sub i32 %524, %68
  %526 = tail call i32 @llvm.smax.i32(i32 %525, i32 0)
  %527 = shl nuw i32 %526, 1
  %528 = sub i32 %524, %527
  %529 = tail call i32 @llvm.smax.i32(i32 %528, i32 0)
  %530 = tail call i32 @llvm.smin.i32(i32 %68, i32 %529)
  %531 = add i32 %522, %45
  %532 = mul i32 %531, %44
  %533 = add i32 %532, 2
  %534 = sext i32 %533 to i64
  %535 = getelementptr float, ptr %42, i64 %534
  %536 = load float, ptr %535, align 4
  %537 = add i32 %530, %45
  %538 = mul i32 %537, %44
  %539 = add i32 %538, 2
  %540 = sext i32 %539 to i64
  %541 = getelementptr float, ptr %42, i64 %540
  %542 = load float, ptr %541, align 4
  %543 = fadd reassoc ninf nsz float %542, %536
  %544 = fmul reassoc ninf nsz float %543, %514
  %545 = fadd reassoc ninf nsz float %544, %511
  %factor142 = fmul reassoc ninf nsz float %514, 2.000000e+00
  %546 = fadd reassoc ninf nsz float %factor142, %512
  %547 = icmp samesign ugt i32 %56, 14
  br i1 %547, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %548 = getelementptr i8, ptr %58, i64 60
  %549 = load float, ptr %548, align 4
  %550 = add i32 %63, -15
  %551 = tail call i32 @llvm.abs.i32(i32 %550, i1 true)
  %552 = sub i32 %551, %68
  %553 = tail call i32 @llvm.smax.i32(i32 %552, i32 0)
  %554 = shl nuw i32 %553, 1
  %555 = sub i32 %551, %554
  %556 = tail call i32 @llvm.smax.i32(i32 %555, i32 0)
  %557 = tail call i32 @llvm.smin.i32(i32 %68, i32 %556)
  %558 = add i32 %63, 15
  %559 = tail call i32 @llvm.abs.i32(i32 %558, i1 true)
  %560 = sub i32 %559, %68
  %561 = tail call i32 @llvm.smax.i32(i32 %560, i32 0)
  %562 = shl nuw i32 %561, 1
  %563 = sub i32 %559, %562
  %564 = tail call i32 @llvm.smax.i32(i32 %563, i32 0)
  %565 = tail call i32 @llvm.smin.i32(i32 %68, i32 %564)
  %566 = add i32 %557, %45
  %567 = mul i32 %566, %44
  %568 = add i32 %567, 2
  %569 = sext i32 %568 to i64
  %570 = getelementptr float, ptr %42, i64 %569
  %571 = load float, ptr %570, align 4
  %572 = add i32 %565, %45
  %573 = mul i32 %572, %44
  %574 = add i32 %573, 2
  %575 = sext i32 %574 to i64
  %576 = getelementptr float, ptr %42, i64 %575
  %577 = load float, ptr %576, align 4
  %578 = fadd reassoc ninf nsz float %577, %571
  %579 = fmul reassoc ninf nsz float %578, %549
  %580 = fadd reassoc ninf nsz float %579, %545
  %factor143 = fmul reassoc ninf nsz float %549, 2.000000e+00
  %581 = fadd reassoc ninf nsz float %factor143, %546
  %.not129 = icmp eq i32 %56, 15
  br i1 %.not129, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %582 = getelementptr i8, ptr %58, i64 64
  %583 = load float, ptr %582, align 4
  %584 = add i32 %63, -16
  %585 = tail call i32 @llvm.abs.i32(i32 %584, i1 true)
  %586 = sub i32 %585, %68
  %587 = tail call i32 @llvm.smax.i32(i32 %586, i32 0)
  %588 = shl nuw i32 %587, 1
  %589 = sub i32 %585, %588
  %590 = tail call i32 @llvm.smax.i32(i32 %589, i32 0)
  %591 = tail call i32 @llvm.smin.i32(i32 %68, i32 %590)
  %592 = add i32 %63, 16
  %593 = tail call i32 @llvm.abs.i32(i32 %592, i1 true)
  %594 = sub i32 %593, %68
  %595 = tail call i32 @llvm.smax.i32(i32 %594, i32 0)
  %596 = shl nuw i32 %595, 1
  %597 = sub i32 %593, %596
  %598 = tail call i32 @llvm.smax.i32(i32 %597, i32 0)
  %599 = tail call i32 @llvm.smin.i32(i32 %68, i32 %598)
  %600 = add i32 %591, %45
  %601 = mul i32 %600, %44
  %602 = add i32 %601, 2
  %603 = sext i32 %602 to i64
  %604 = getelementptr float, ptr %42, i64 %603
  %605 = load float, ptr %604, align 4
  %606 = add i32 %599, %45
  %607 = mul i32 %606, %44
  %608 = add i32 %607, 2
  %609 = sext i32 %608 to i64
  %610 = getelementptr float, ptr %42, i64 %609
  %611 = load float, ptr %610, align 4
  %612 = fadd reassoc ninf nsz float %611, %605
  %613 = fmul reassoc ninf nsz float %612, %583
  %614 = fadd reassoc ninf nsz float %613, %580
  %factor144 = fmul reassoc ninf nsz float %583, 2.000000e+00
  %615 = fadd reassoc ninf nsz float %factor144, %581
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.1570 = phi float [ %614, %true_block43 ], [ %580, %after_if42 ], [ %545, %after_if39 ], [ %511, %after_if36 ], [ %476, %after_if33 ], [ %442, %after_if30 ], [ %407, %after_if27 ], [ %373, %after_if24 ], [ %338, %after_if21 ], [ %304, %after_if18 ], [ %269, %after_if15 ], [ %235, %after_if12 ], [ %200, %after_if9 ], [ %166, %after_if6 ], [ %131, %after_if3 ], [ %97, %after_if ], [ %54, %for_loop_body ]
  %.15 = phi float [ %615, %true_block43 ], [ %581, %after_if42 ], [ %546, %after_if39 ], [ %512, %after_if36 ], [ %477, %after_if33 ], [ %443, %after_if30 ], [ %408, %after_if27 ], [ %374, %after_if24 ], [ %339, %after_if21 ], [ %305, %after_if18 ], [ %270, %after_if15 ], [ %236, %after_if12 ], [ %201, %after_if9 ], [ %167, %after_if6 ], [ %132, %after_if3 ], [ %98, %after_if ], [ %41, %for_loop_body ]
  %616 = fdiv reassoc ninf nsz float %.1570, %.15
  %617 = load ptr, ptr %26, align 8
  %618 = load i32, ptr %27, align 4
  %619 = load i32, ptr %28, align 4
  %620 = sub i32 %618, %33
  %621 = mul i32 %620, %40
  %622 = add i32 %.091145, %621
  %623 = mul i32 %622, %619
  %624 = add i32 %623, 2
  %625 = sext i32 %624 to i64
  %626 = getelementptr float, ptr %617, i64 %625
  store float %616, ptr %626, align 4
  %627 = add nsw i32 %.091145, 1
  %exitcond.not = icmp eq i32 %18, %627
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.0, align 8
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
