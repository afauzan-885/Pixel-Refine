; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.11 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_gaussian_blur_x_3ch_i32_kernel_c192_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_gaussian_blur_x_3ch_i32_kernel_c192_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %.091145 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %645, %after_if45 ]
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
  %52 = getelementptr i32, ptr %42, i64 %51
  %53 = load i32, ptr %52, align 4
  %54 = sitofp i32 %53 to float
  %55 = fmul reassoc ninf nsz float %41, %54
  %56 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %57 = load i32, ptr %56, align 4
  %58 = icmp sgt i32 %57, 0
  br i1 %58, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %59 = load ptr, ptr %20, align 8
  %60 = getelementptr i8, ptr %59, i64 4
  %61 = load float, ptr %60, align 4
  %62 = mul i32 %33, -1
  %63 = mul i32 %62, %40
  %64 = add i32 %.091145, %63
  %65 = add i32 %64, -1
  %66 = tail call i32 @llvm.abs.i32(i32 %65, i1 true)
  %67 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %68 = load i32, ptr %67, align 4
  %69 = add i32 %68, -1
  %70 = sub i32 %66, %69
  %71 = tail call i32 @llvm.smax.i32(i32 %70, i32 0)
  %72 = shl nuw i32 %71, 1
  %73 = sub i32 %66, %72
  %74 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %75 = tail call i32 @llvm.smin.i32(i32 %69, i32 %74)
  %76 = add i32 %64, 1
  %77 = tail call i32 @llvm.abs.i32(i32 %76, i1 true)
  %78 = sub i32 %77, %69
  %79 = tail call i32 @llvm.smax.i32(i32 %78, i32 0)
  %80 = shl nuw i32 %79, 1
  %81 = sub i32 %77, %80
  %82 = tail call i32 @llvm.smax.i32(i32 %81, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %69, i32 %82)
  %84 = add i32 %75, %45
  %85 = mul i32 %84, %44
  %86 = add i32 %83, %45
  %87 = mul i32 %86, %44
  %88 = add i32 %85, 2
  %89 = sext i32 %88 to i64
  %90 = getelementptr i32, ptr %42, i64 %89
  %91 = load i32, ptr %90, align 4
  %92 = add i32 %87, 2
  %93 = sext i32 %92 to i64
  %94 = getelementptr i32, ptr %42, i64 %93
  %95 = load i32, ptr %94, align 4
  %96 = add i32 %95, %91
  %97 = sitofp i32 %96 to float
  %98 = fmul reassoc ninf nsz float %61, %97
  %99 = fadd reassoc ninf nsz float %98, %55
  %factor = fmul reassoc ninf nsz float %61, 2.000000e+00
  %100 = fadd reassoc ninf nsz float %factor, %41
  %.not = icmp eq i32 %57, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %101 = getelementptr i8, ptr %59, i64 8
  %102 = load float, ptr %101, align 4
  %103 = add i32 %64, -2
  %104 = tail call i32 @llvm.abs.i32(i32 %103, i1 true)
  %105 = sub i32 %104, %69
  %106 = tail call i32 @llvm.smax.i32(i32 %105, i32 0)
  %107 = shl nuw i32 %106, 1
  %108 = sub i32 %104, %107
  %109 = tail call i32 @llvm.smax.i32(i32 %108, i32 0)
  %110 = tail call i32 @llvm.smin.i32(i32 %69, i32 %109)
  %111 = add i32 %64, 2
  %112 = tail call i32 @llvm.abs.i32(i32 %111, i1 true)
  %113 = sub i32 %112, %69
  %114 = tail call i32 @llvm.smax.i32(i32 %113, i32 0)
  %115 = shl nuw i32 %114, 1
  %116 = sub i32 %112, %115
  %117 = tail call i32 @llvm.smax.i32(i32 %116, i32 0)
  %118 = tail call i32 @llvm.smin.i32(i32 %69, i32 %117)
  %119 = add i32 %110, %45
  %120 = mul i32 %119, %44
  %121 = add i32 %118, %45
  %122 = mul i32 %121, %44
  %123 = add i32 %120, 2
  %124 = sext i32 %123 to i64
  %125 = getelementptr i32, ptr %42, i64 %124
  %126 = load i32, ptr %125, align 4
  %127 = add i32 %122, 2
  %128 = sext i32 %127 to i64
  %129 = getelementptr i32, ptr %42, i64 %128
  %130 = load i32, ptr %129, align 4
  %131 = add i32 %130, %126
  %132 = sitofp i32 %131 to float
  %133 = fmul reassoc ninf nsz float %102, %132
  %134 = fadd reassoc ninf nsz float %133, %99
  %factor130 = fmul reassoc ninf nsz float %102, 2.000000e+00
  %135 = fadd reassoc ninf nsz float %factor130, %100
  %136 = icmp samesign ugt i32 %57, 2
  br i1 %136, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %137 = getelementptr i8, ptr %59, i64 12
  %138 = load float, ptr %137, align 4
  %139 = add i32 %64, -3
  %140 = tail call i32 @llvm.abs.i32(i32 %139, i1 true)
  %141 = sub i32 %140, %69
  %142 = tail call i32 @llvm.smax.i32(i32 %141, i32 0)
  %143 = shl nuw i32 %142, 1
  %144 = sub i32 %140, %143
  %145 = tail call i32 @llvm.smax.i32(i32 %144, i32 0)
  %146 = tail call i32 @llvm.smin.i32(i32 %69, i32 %145)
  %147 = add i32 %64, 3
  %148 = tail call i32 @llvm.abs.i32(i32 %147, i1 true)
  %149 = sub i32 %148, %69
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = shl nuw i32 %150, 1
  %152 = sub i32 %148, %151
  %153 = tail call i32 @llvm.smax.i32(i32 %152, i32 0)
  %154 = tail call i32 @llvm.smin.i32(i32 %69, i32 %153)
  %155 = add i32 %146, %45
  %156 = mul i32 %155, %44
  %157 = add i32 %154, %45
  %158 = mul i32 %157, %44
  %159 = add i32 %156, 2
  %160 = sext i32 %159 to i64
  %161 = getelementptr i32, ptr %42, i64 %160
  %162 = load i32, ptr %161, align 4
  %163 = add i32 %158, 2
  %164 = sext i32 %163 to i64
  %165 = getelementptr i32, ptr %42, i64 %164
  %166 = load i32, ptr %165, align 4
  %167 = add i32 %166, %162
  %168 = sitofp i32 %167 to float
  %169 = fmul reassoc ninf nsz float %138, %168
  %170 = fadd reassoc ninf nsz float %169, %134
  %factor131 = fmul reassoc ninf nsz float %138, 2.000000e+00
  %171 = fadd reassoc ninf nsz float %factor131, %135
  %.not123 = icmp eq i32 %57, 3
  br i1 %.not123, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %172 = getelementptr i8, ptr %59, i64 16
  %173 = load float, ptr %172, align 4
  %174 = add i32 %64, -4
  %175 = tail call i32 @llvm.abs.i32(i32 %174, i1 true)
  %176 = sub i32 %175, %69
  %177 = tail call i32 @llvm.smax.i32(i32 %176, i32 0)
  %178 = shl nuw i32 %177, 1
  %179 = sub i32 %175, %178
  %180 = tail call i32 @llvm.smax.i32(i32 %179, i32 0)
  %181 = tail call i32 @llvm.smin.i32(i32 %69, i32 %180)
  %182 = add i32 %64, 4
  %183 = tail call i32 @llvm.abs.i32(i32 %182, i1 true)
  %184 = sub i32 %183, %69
  %185 = tail call i32 @llvm.smax.i32(i32 %184, i32 0)
  %186 = shl nuw i32 %185, 1
  %187 = sub i32 %183, %186
  %188 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %189 = tail call i32 @llvm.smin.i32(i32 %69, i32 %188)
  %190 = add i32 %181, %45
  %191 = mul i32 %190, %44
  %192 = add i32 %189, %45
  %193 = mul i32 %192, %44
  %194 = add i32 %191, 2
  %195 = sext i32 %194 to i64
  %196 = getelementptr i32, ptr %42, i64 %195
  %197 = load i32, ptr %196, align 4
  %198 = add i32 %193, 2
  %199 = sext i32 %198 to i64
  %200 = getelementptr i32, ptr %42, i64 %199
  %201 = load i32, ptr %200, align 4
  %202 = add i32 %201, %197
  %203 = sitofp i32 %202 to float
  %204 = fmul reassoc ninf nsz float %173, %203
  %205 = fadd reassoc ninf nsz float %204, %170
  %factor132 = fmul reassoc ninf nsz float %173, 2.000000e+00
  %206 = fadd reassoc ninf nsz float %factor132, %171
  %207 = icmp samesign ugt i32 %57, 4
  br i1 %207, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %208 = getelementptr i8, ptr %59, i64 20
  %209 = load float, ptr %208, align 4
  %210 = add i32 %64, -5
  %211 = tail call i32 @llvm.abs.i32(i32 %210, i1 true)
  %212 = sub i32 %211, %69
  %213 = tail call i32 @llvm.smax.i32(i32 %212, i32 0)
  %214 = shl nuw i32 %213, 1
  %215 = sub i32 %211, %214
  %216 = tail call i32 @llvm.smax.i32(i32 %215, i32 0)
  %217 = tail call i32 @llvm.smin.i32(i32 %69, i32 %216)
  %218 = add i32 %64, 5
  %219 = tail call i32 @llvm.abs.i32(i32 %218, i1 true)
  %220 = sub i32 %219, %69
  %221 = tail call i32 @llvm.smax.i32(i32 %220, i32 0)
  %222 = shl nuw i32 %221, 1
  %223 = sub i32 %219, %222
  %224 = tail call i32 @llvm.smax.i32(i32 %223, i32 0)
  %225 = tail call i32 @llvm.smin.i32(i32 %69, i32 %224)
  %226 = add i32 %217, %45
  %227 = mul i32 %226, %44
  %228 = add i32 %225, %45
  %229 = mul i32 %228, %44
  %230 = add i32 %227, 2
  %231 = sext i32 %230 to i64
  %232 = getelementptr i32, ptr %42, i64 %231
  %233 = load i32, ptr %232, align 4
  %234 = add i32 %229, 2
  %235 = sext i32 %234 to i64
  %236 = getelementptr i32, ptr %42, i64 %235
  %237 = load i32, ptr %236, align 4
  %238 = add i32 %237, %233
  %239 = sitofp i32 %238 to float
  %240 = fmul reassoc ninf nsz float %209, %239
  %241 = fadd reassoc ninf nsz float %240, %205
  %factor133 = fmul reassoc ninf nsz float %209, 2.000000e+00
  %242 = fadd reassoc ninf nsz float %factor133, %206
  %.not124 = icmp eq i32 %57, 5
  br i1 %.not124, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %243 = getelementptr i8, ptr %59, i64 24
  %244 = load float, ptr %243, align 4
  %245 = add i32 %64, -6
  %246 = tail call i32 @llvm.abs.i32(i32 %245, i1 true)
  %247 = sub i32 %246, %69
  %248 = tail call i32 @llvm.smax.i32(i32 %247, i32 0)
  %249 = shl nuw i32 %248, 1
  %250 = sub i32 %246, %249
  %251 = tail call i32 @llvm.smax.i32(i32 %250, i32 0)
  %252 = tail call i32 @llvm.smin.i32(i32 %69, i32 %251)
  %253 = add i32 %64, 6
  %254 = tail call i32 @llvm.abs.i32(i32 %253, i1 true)
  %255 = sub i32 %254, %69
  %256 = tail call i32 @llvm.smax.i32(i32 %255, i32 0)
  %257 = shl nuw i32 %256, 1
  %258 = sub i32 %254, %257
  %259 = tail call i32 @llvm.smax.i32(i32 %258, i32 0)
  %260 = tail call i32 @llvm.smin.i32(i32 %69, i32 %259)
  %261 = add i32 %252, %45
  %262 = mul i32 %261, %44
  %263 = add i32 %260, %45
  %264 = mul i32 %263, %44
  %265 = add i32 %262, 2
  %266 = sext i32 %265 to i64
  %267 = getelementptr i32, ptr %42, i64 %266
  %268 = load i32, ptr %267, align 4
  %269 = add i32 %264, 2
  %270 = sext i32 %269 to i64
  %271 = getelementptr i32, ptr %42, i64 %270
  %272 = load i32, ptr %271, align 4
  %273 = add i32 %272, %268
  %274 = sitofp i32 %273 to float
  %275 = fmul reassoc ninf nsz float %244, %274
  %276 = fadd reassoc ninf nsz float %275, %241
  %factor134 = fmul reassoc ninf nsz float %244, 2.000000e+00
  %277 = fadd reassoc ninf nsz float %factor134, %242
  %278 = icmp samesign ugt i32 %57, 6
  br i1 %278, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %279 = getelementptr i8, ptr %59, i64 28
  %280 = load float, ptr %279, align 4
  %281 = add i32 %64, -7
  %282 = tail call i32 @llvm.abs.i32(i32 %281, i1 true)
  %283 = sub i32 %282, %69
  %284 = tail call i32 @llvm.smax.i32(i32 %283, i32 0)
  %285 = shl nuw i32 %284, 1
  %286 = sub i32 %282, %285
  %287 = tail call i32 @llvm.smax.i32(i32 %286, i32 0)
  %288 = tail call i32 @llvm.smin.i32(i32 %69, i32 %287)
  %289 = add i32 %64, 7
  %290 = tail call i32 @llvm.abs.i32(i32 %289, i1 true)
  %291 = sub i32 %290, %69
  %292 = tail call i32 @llvm.smax.i32(i32 %291, i32 0)
  %293 = shl nuw i32 %292, 1
  %294 = sub i32 %290, %293
  %295 = tail call i32 @llvm.smax.i32(i32 %294, i32 0)
  %296 = tail call i32 @llvm.smin.i32(i32 %69, i32 %295)
  %297 = add i32 %288, %45
  %298 = mul i32 %297, %44
  %299 = add i32 %296, %45
  %300 = mul i32 %299, %44
  %301 = add i32 %298, 2
  %302 = sext i32 %301 to i64
  %303 = getelementptr i32, ptr %42, i64 %302
  %304 = load i32, ptr %303, align 4
  %305 = add i32 %300, 2
  %306 = sext i32 %305 to i64
  %307 = getelementptr i32, ptr %42, i64 %306
  %308 = load i32, ptr %307, align 4
  %309 = add i32 %308, %304
  %310 = sitofp i32 %309 to float
  %311 = fmul reassoc ninf nsz float %280, %310
  %312 = fadd reassoc ninf nsz float %311, %276
  %factor135 = fmul reassoc ninf nsz float %280, 2.000000e+00
  %313 = fadd reassoc ninf nsz float %factor135, %277
  %.not125 = icmp eq i32 %57, 7
  br i1 %.not125, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %314 = getelementptr i8, ptr %59, i64 32
  %315 = load float, ptr %314, align 4
  %316 = add i32 %64, -8
  %317 = tail call i32 @llvm.abs.i32(i32 %316, i1 true)
  %318 = sub i32 %317, %69
  %319 = tail call i32 @llvm.smax.i32(i32 %318, i32 0)
  %320 = shl nuw i32 %319, 1
  %321 = sub i32 %317, %320
  %322 = tail call i32 @llvm.smax.i32(i32 %321, i32 0)
  %323 = tail call i32 @llvm.smin.i32(i32 %69, i32 %322)
  %324 = add i32 %64, 8
  %325 = tail call i32 @llvm.abs.i32(i32 %324, i1 true)
  %326 = sub i32 %325, %69
  %327 = tail call i32 @llvm.smax.i32(i32 %326, i32 0)
  %328 = shl nuw i32 %327, 1
  %329 = sub i32 %325, %328
  %330 = tail call i32 @llvm.smax.i32(i32 %329, i32 0)
  %331 = tail call i32 @llvm.smin.i32(i32 %69, i32 %330)
  %332 = add i32 %323, %45
  %333 = mul i32 %332, %44
  %334 = add i32 %331, %45
  %335 = mul i32 %334, %44
  %336 = add i32 %333, 2
  %337 = sext i32 %336 to i64
  %338 = getelementptr i32, ptr %42, i64 %337
  %339 = load i32, ptr %338, align 4
  %340 = add i32 %335, 2
  %341 = sext i32 %340 to i64
  %342 = getelementptr i32, ptr %42, i64 %341
  %343 = load i32, ptr %342, align 4
  %344 = add i32 %343, %339
  %345 = sitofp i32 %344 to float
  %346 = fmul reassoc ninf nsz float %315, %345
  %347 = fadd reassoc ninf nsz float %346, %312
  %factor136 = fmul reassoc ninf nsz float %315, 2.000000e+00
  %348 = fadd reassoc ninf nsz float %factor136, %313
  %349 = icmp samesign ugt i32 %57, 8
  br i1 %349, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %350 = getelementptr i8, ptr %59, i64 36
  %351 = load float, ptr %350, align 4
  %352 = add i32 %64, -9
  %353 = tail call i32 @llvm.abs.i32(i32 %352, i1 true)
  %354 = sub i32 %353, %69
  %355 = tail call i32 @llvm.smax.i32(i32 %354, i32 0)
  %356 = shl nuw i32 %355, 1
  %357 = sub i32 %353, %356
  %358 = tail call i32 @llvm.smax.i32(i32 %357, i32 0)
  %359 = tail call i32 @llvm.smin.i32(i32 %69, i32 %358)
  %360 = add i32 %64, 9
  %361 = tail call i32 @llvm.abs.i32(i32 %360, i1 true)
  %362 = sub i32 %361, %69
  %363 = tail call i32 @llvm.smax.i32(i32 %362, i32 0)
  %364 = shl nuw i32 %363, 1
  %365 = sub i32 %361, %364
  %366 = tail call i32 @llvm.smax.i32(i32 %365, i32 0)
  %367 = tail call i32 @llvm.smin.i32(i32 %69, i32 %366)
  %368 = add i32 %359, %45
  %369 = mul i32 %368, %44
  %370 = add i32 %367, %45
  %371 = mul i32 %370, %44
  %372 = add i32 %369, 2
  %373 = sext i32 %372 to i64
  %374 = getelementptr i32, ptr %42, i64 %373
  %375 = load i32, ptr %374, align 4
  %376 = add i32 %371, 2
  %377 = sext i32 %376 to i64
  %378 = getelementptr i32, ptr %42, i64 %377
  %379 = load i32, ptr %378, align 4
  %380 = add i32 %379, %375
  %381 = sitofp i32 %380 to float
  %382 = fmul reassoc ninf nsz float %351, %381
  %383 = fadd reassoc ninf nsz float %382, %347
  %factor137 = fmul reassoc ninf nsz float %351, 2.000000e+00
  %384 = fadd reassoc ninf nsz float %factor137, %348
  %.not126 = icmp eq i32 %57, 9
  br i1 %.not126, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %385 = getelementptr i8, ptr %59, i64 40
  %386 = load float, ptr %385, align 4
  %387 = add i32 %64, -10
  %388 = tail call i32 @llvm.abs.i32(i32 %387, i1 true)
  %389 = sub i32 %388, %69
  %390 = tail call i32 @llvm.smax.i32(i32 %389, i32 0)
  %391 = shl nuw i32 %390, 1
  %392 = sub i32 %388, %391
  %393 = tail call i32 @llvm.smax.i32(i32 %392, i32 0)
  %394 = tail call i32 @llvm.smin.i32(i32 %69, i32 %393)
  %395 = add i32 %64, 10
  %396 = tail call i32 @llvm.abs.i32(i32 %395, i1 true)
  %397 = sub i32 %396, %69
  %398 = tail call i32 @llvm.smax.i32(i32 %397, i32 0)
  %399 = shl nuw i32 %398, 1
  %400 = sub i32 %396, %399
  %401 = tail call i32 @llvm.smax.i32(i32 %400, i32 0)
  %402 = tail call i32 @llvm.smin.i32(i32 %69, i32 %401)
  %403 = add i32 %394, %45
  %404 = mul i32 %403, %44
  %405 = add i32 %402, %45
  %406 = mul i32 %405, %44
  %407 = add i32 %404, 2
  %408 = sext i32 %407 to i64
  %409 = getelementptr i32, ptr %42, i64 %408
  %410 = load i32, ptr %409, align 4
  %411 = add i32 %406, 2
  %412 = sext i32 %411 to i64
  %413 = getelementptr i32, ptr %42, i64 %412
  %414 = load i32, ptr %413, align 4
  %415 = add i32 %414, %410
  %416 = sitofp i32 %415 to float
  %417 = fmul reassoc ninf nsz float %386, %416
  %418 = fadd reassoc ninf nsz float %417, %383
  %factor138 = fmul reassoc ninf nsz float %386, 2.000000e+00
  %419 = fadd reassoc ninf nsz float %factor138, %384
  %420 = icmp samesign ugt i32 %57, 10
  br i1 %420, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %421 = getelementptr i8, ptr %59, i64 44
  %422 = load float, ptr %421, align 4
  %423 = add i32 %64, -11
  %424 = tail call i32 @llvm.abs.i32(i32 %423, i1 true)
  %425 = sub i32 %424, %69
  %426 = tail call i32 @llvm.smax.i32(i32 %425, i32 0)
  %427 = shl nuw i32 %426, 1
  %428 = sub i32 %424, %427
  %429 = tail call i32 @llvm.smax.i32(i32 %428, i32 0)
  %430 = tail call i32 @llvm.smin.i32(i32 %69, i32 %429)
  %431 = add i32 %64, 11
  %432 = tail call i32 @llvm.abs.i32(i32 %431, i1 true)
  %433 = sub i32 %432, %69
  %434 = tail call i32 @llvm.smax.i32(i32 %433, i32 0)
  %435 = shl nuw i32 %434, 1
  %436 = sub i32 %432, %435
  %437 = tail call i32 @llvm.smax.i32(i32 %436, i32 0)
  %438 = tail call i32 @llvm.smin.i32(i32 %69, i32 %437)
  %439 = add i32 %430, %45
  %440 = mul i32 %439, %44
  %441 = add i32 %438, %45
  %442 = mul i32 %441, %44
  %443 = add i32 %440, 2
  %444 = sext i32 %443 to i64
  %445 = getelementptr i32, ptr %42, i64 %444
  %446 = load i32, ptr %445, align 4
  %447 = add i32 %442, 2
  %448 = sext i32 %447 to i64
  %449 = getelementptr i32, ptr %42, i64 %448
  %450 = load i32, ptr %449, align 4
  %451 = add i32 %450, %446
  %452 = sitofp i32 %451 to float
  %453 = fmul reassoc ninf nsz float %422, %452
  %454 = fadd reassoc ninf nsz float %453, %418
  %factor139 = fmul reassoc ninf nsz float %422, 2.000000e+00
  %455 = fadd reassoc ninf nsz float %factor139, %419
  %.not127 = icmp eq i32 %57, 11
  br i1 %.not127, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %456 = getelementptr i8, ptr %59, i64 48
  %457 = load float, ptr %456, align 4
  %458 = add i32 %64, -12
  %459 = tail call i32 @llvm.abs.i32(i32 %458, i1 true)
  %460 = sub i32 %459, %69
  %461 = tail call i32 @llvm.smax.i32(i32 %460, i32 0)
  %462 = shl nuw i32 %461, 1
  %463 = sub i32 %459, %462
  %464 = tail call i32 @llvm.smax.i32(i32 %463, i32 0)
  %465 = tail call i32 @llvm.smin.i32(i32 %69, i32 %464)
  %466 = add i32 %64, 12
  %467 = tail call i32 @llvm.abs.i32(i32 %466, i1 true)
  %468 = sub i32 %467, %69
  %469 = tail call i32 @llvm.smax.i32(i32 %468, i32 0)
  %470 = shl nuw i32 %469, 1
  %471 = sub i32 %467, %470
  %472 = tail call i32 @llvm.smax.i32(i32 %471, i32 0)
  %473 = tail call i32 @llvm.smin.i32(i32 %69, i32 %472)
  %474 = add i32 %465, %45
  %475 = mul i32 %474, %44
  %476 = add i32 %475, 2
  %477 = sext i32 %476 to i64
  %478 = getelementptr i32, ptr %42, i64 %477
  %479 = load i32, ptr %478, align 4
  %480 = add i32 %473, %45
  %481 = mul i32 %480, %44
  %482 = add i32 %481, 2
  %483 = sext i32 %482 to i64
  %484 = getelementptr i32, ptr %42, i64 %483
  %485 = load i32, ptr %484, align 4
  %486 = add i32 %485, %479
  %487 = sitofp i32 %486 to float
  %488 = fmul reassoc ninf nsz float %457, %487
  %489 = fadd reassoc ninf nsz float %488, %454
  %factor140 = fmul reassoc ninf nsz float %457, 2.000000e+00
  %490 = fadd reassoc ninf nsz float %factor140, %455
  %491 = icmp samesign ugt i32 %57, 12
  br i1 %491, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %492 = getelementptr i8, ptr %59, i64 52
  %493 = load float, ptr %492, align 4
  %494 = add i32 %64, -13
  %495 = tail call i32 @llvm.abs.i32(i32 %494, i1 true)
  %496 = sub i32 %495, %69
  %497 = tail call i32 @llvm.smax.i32(i32 %496, i32 0)
  %498 = shl nuw i32 %497, 1
  %499 = sub i32 %495, %498
  %500 = tail call i32 @llvm.smax.i32(i32 %499, i32 0)
  %501 = tail call i32 @llvm.smin.i32(i32 %69, i32 %500)
  %502 = add i32 %64, 13
  %503 = tail call i32 @llvm.abs.i32(i32 %502, i1 true)
  %504 = sub i32 %503, %69
  %505 = tail call i32 @llvm.smax.i32(i32 %504, i32 0)
  %506 = shl nuw i32 %505, 1
  %507 = sub i32 %503, %506
  %508 = tail call i32 @llvm.smax.i32(i32 %507, i32 0)
  %509 = tail call i32 @llvm.smin.i32(i32 %69, i32 %508)
  %510 = add i32 %501, %45
  %511 = mul i32 %510, %44
  %512 = add i32 %511, 2
  %513 = sext i32 %512 to i64
  %514 = getelementptr i32, ptr %42, i64 %513
  %515 = load i32, ptr %514, align 4
  %516 = add i32 %509, %45
  %517 = mul i32 %516, %44
  %518 = add i32 %517, 2
  %519 = sext i32 %518 to i64
  %520 = getelementptr i32, ptr %42, i64 %519
  %521 = load i32, ptr %520, align 4
  %522 = add i32 %521, %515
  %523 = sitofp i32 %522 to float
  %524 = fmul reassoc ninf nsz float %493, %523
  %525 = fadd reassoc ninf nsz float %524, %489
  %factor141 = fmul reassoc ninf nsz float %493, 2.000000e+00
  %526 = fadd reassoc ninf nsz float %factor141, %490
  %.not128 = icmp eq i32 %57, 13
  br i1 %.not128, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %527 = getelementptr i8, ptr %59, i64 56
  %528 = load float, ptr %527, align 4
  %529 = add i32 %64, -14
  %530 = tail call i32 @llvm.abs.i32(i32 %529, i1 true)
  %531 = sub i32 %530, %69
  %532 = tail call i32 @llvm.smax.i32(i32 %531, i32 0)
  %533 = shl nuw i32 %532, 1
  %534 = sub i32 %530, %533
  %535 = tail call i32 @llvm.smax.i32(i32 %534, i32 0)
  %536 = tail call i32 @llvm.smin.i32(i32 %69, i32 %535)
  %537 = add i32 %64, 14
  %538 = tail call i32 @llvm.abs.i32(i32 %537, i1 true)
  %539 = sub i32 %538, %69
  %540 = tail call i32 @llvm.smax.i32(i32 %539, i32 0)
  %541 = shl nuw i32 %540, 1
  %542 = sub i32 %538, %541
  %543 = tail call i32 @llvm.smax.i32(i32 %542, i32 0)
  %544 = tail call i32 @llvm.smin.i32(i32 %69, i32 %543)
  %545 = add i32 %536, %45
  %546 = mul i32 %545, %44
  %547 = add i32 %546, 2
  %548 = sext i32 %547 to i64
  %549 = getelementptr i32, ptr %42, i64 %548
  %550 = load i32, ptr %549, align 4
  %551 = add i32 %544, %45
  %552 = mul i32 %551, %44
  %553 = add i32 %552, 2
  %554 = sext i32 %553 to i64
  %555 = getelementptr i32, ptr %42, i64 %554
  %556 = load i32, ptr %555, align 4
  %557 = add i32 %556, %550
  %558 = sitofp i32 %557 to float
  %559 = fmul reassoc ninf nsz float %528, %558
  %560 = fadd reassoc ninf nsz float %559, %525
  %factor142 = fmul reassoc ninf nsz float %528, 2.000000e+00
  %561 = fadd reassoc ninf nsz float %factor142, %526
  %562 = icmp samesign ugt i32 %57, 14
  br i1 %562, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %563 = getelementptr i8, ptr %59, i64 60
  %564 = load float, ptr %563, align 4
  %565 = add i32 %64, -15
  %566 = tail call i32 @llvm.abs.i32(i32 %565, i1 true)
  %567 = sub i32 %566, %69
  %568 = tail call i32 @llvm.smax.i32(i32 %567, i32 0)
  %569 = shl nuw i32 %568, 1
  %570 = sub i32 %566, %569
  %571 = tail call i32 @llvm.smax.i32(i32 %570, i32 0)
  %572 = tail call i32 @llvm.smin.i32(i32 %69, i32 %571)
  %573 = add i32 %64, 15
  %574 = tail call i32 @llvm.abs.i32(i32 %573, i1 true)
  %575 = sub i32 %574, %69
  %576 = tail call i32 @llvm.smax.i32(i32 %575, i32 0)
  %577 = shl nuw i32 %576, 1
  %578 = sub i32 %574, %577
  %579 = tail call i32 @llvm.smax.i32(i32 %578, i32 0)
  %580 = tail call i32 @llvm.smin.i32(i32 %69, i32 %579)
  %581 = add i32 %572, %45
  %582 = mul i32 %581, %44
  %583 = add i32 %582, 2
  %584 = sext i32 %583 to i64
  %585 = getelementptr i32, ptr %42, i64 %584
  %586 = load i32, ptr %585, align 4
  %587 = add i32 %580, %45
  %588 = mul i32 %587, %44
  %589 = add i32 %588, 2
  %590 = sext i32 %589 to i64
  %591 = getelementptr i32, ptr %42, i64 %590
  %592 = load i32, ptr %591, align 4
  %593 = add i32 %592, %586
  %594 = sitofp i32 %593 to float
  %595 = fmul reassoc ninf nsz float %564, %594
  %596 = fadd reassoc ninf nsz float %595, %560
  %factor143 = fmul reassoc ninf nsz float %564, 2.000000e+00
  %597 = fadd reassoc ninf nsz float %factor143, %561
  %.not129 = icmp eq i32 %57, 15
  br i1 %.not129, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %598 = getelementptr i8, ptr %59, i64 64
  %599 = load float, ptr %598, align 4
  %600 = add i32 %64, -16
  %601 = tail call i32 @llvm.abs.i32(i32 %600, i1 true)
  %602 = sub i32 %601, %69
  %603 = tail call i32 @llvm.smax.i32(i32 %602, i32 0)
  %604 = shl nuw i32 %603, 1
  %605 = sub i32 %601, %604
  %606 = tail call i32 @llvm.smax.i32(i32 %605, i32 0)
  %607 = tail call i32 @llvm.smin.i32(i32 %69, i32 %606)
  %608 = add i32 %64, 16
  %609 = tail call i32 @llvm.abs.i32(i32 %608, i1 true)
  %610 = sub i32 %609, %69
  %611 = tail call i32 @llvm.smax.i32(i32 %610, i32 0)
  %612 = shl nuw i32 %611, 1
  %613 = sub i32 %609, %612
  %614 = tail call i32 @llvm.smax.i32(i32 %613, i32 0)
  %615 = tail call i32 @llvm.smin.i32(i32 %69, i32 %614)
  %616 = add i32 %607, %45
  %617 = mul i32 %616, %44
  %618 = add i32 %617, 2
  %619 = sext i32 %618 to i64
  %620 = getelementptr i32, ptr %42, i64 %619
  %621 = load i32, ptr %620, align 4
  %622 = add i32 %615, %45
  %623 = mul i32 %622, %44
  %624 = add i32 %623, 2
  %625 = sext i32 %624 to i64
  %626 = getelementptr i32, ptr %42, i64 %625
  %627 = load i32, ptr %626, align 4
  %628 = add i32 %627, %621
  %629 = sitofp i32 %628 to float
  %630 = fmul reassoc ninf nsz float %599, %629
  %631 = fadd reassoc ninf nsz float %630, %596
  %factor144 = fmul reassoc ninf nsz float %599, 2.000000e+00
  %632 = fadd reassoc ninf nsz float %factor144, %597
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %.1570 = phi float [ %631, %true_block43 ], [ %596, %after_if42 ], [ %560, %after_if39 ], [ %525, %after_if36 ], [ %489, %after_if33 ], [ %454, %after_if30 ], [ %418, %after_if27 ], [ %383, %after_if24 ], [ %347, %after_if21 ], [ %312, %after_if18 ], [ %276, %after_if15 ], [ %241, %after_if12 ], [ %205, %after_if9 ], [ %170, %after_if6 ], [ %134, %after_if3 ], [ %99, %after_if ], [ %55, %for_loop_body ]
  %.15 = phi float [ %632, %true_block43 ], [ %597, %after_if42 ], [ %561, %after_if39 ], [ %526, %after_if36 ], [ %490, %after_if33 ], [ %455, %after_if30 ], [ %419, %after_if27 ], [ %384, %after_if24 ], [ %348, %after_if21 ], [ %313, %after_if18 ], [ %277, %after_if15 ], [ %242, %after_if12 ], [ %206, %after_if9 ], [ %171, %after_if6 ], [ %135, %after_if3 ], [ %100, %after_if ], [ %41, %for_loop_body ]
  %633 = fdiv reassoc ninf nsz float %.1570, %.15
  %634 = load ptr, ptr %26, align 8
  %635 = load i32, ptr %27, align 4
  %636 = load i32, ptr %28, align 4
  %637 = sub i32 %635, %33
  %638 = mul i32 %637, %40
  %639 = add i32 %.091145, %638
  %640 = mul i32 %639, %636
  %641 = add i32 %640, 2
  %642 = sext i32 %641 to i64
  %643 = getelementptr i32, ptr %634, i64 %642
  %644 = fptosi float %633 to i32
  store i32 %644, ptr %643, align 4
  %645 = add nsw i32 %.091145, 1
  %exitcond.not = icmp eq i32 %18, %645
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.11, align 8
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
