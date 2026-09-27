; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.20 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @accumulate_spatial_merging_vec3_region_kernel_c768_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 104
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 24
  store i32 %2, ptr %7, align 4
  %8 = sitofp i32 %2 to float
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 96
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 8
  store i32 %11, ptr %15, align 4
  %16 = sitofp i32 %11 to float
  %17 = fdiv reassoc ninf nsz float %8, %16
  %18 = load ptr, ptr %3, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 16
  store float %17, ptr %21, align 4
  %22 = load ptr, ptr %context, align 8
  %23 = getelementptr i8, ptr %22, i64 108
  %24 = load i32, ptr %23, align 4
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 28
  store i32 %24, ptr %28, align 4
  %29 = sitofp i32 %24 to float
  %30 = load ptr, ptr %context, align 8
  %31 = getelementptr i8, ptr %30, i64 100
  %32 = load i32, ptr %31, align 4
  %33 = load ptr, ptr %3, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 12
  store i32 %32, ptr %36, align 4
  %37 = sitofp i32 %32 to float
  %38 = fdiv reassoc ninf nsz float %29, %37
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 20
  store float %38, ptr %42, align 4
  %43 = load ptr, ptr %context, align 8
  %44 = getelementptr i8, ptr %43, i64 112
  %45 = load i32, ptr %44, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %47 = getelementptr i8, ptr %43, i64 116
  %48 = load i32, ptr %47, align 4
  %49 = tail call i32 @llvm.smax.i32(i32 %48, i32 0)
  %50 = load ptr, ptr %3, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 32872
  %52 = load ptr, ptr %51, align 8
  %53 = getelementptr inbounds nuw i8, ptr %52, i64 4
  store i32 %49, ptr %53, align 4
  %54 = mul i32 %49, %46
  %55 = load ptr, ptr %3, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 32872
  %57 = load ptr, ptr %56, align 8
  store i32 %54, ptr %57, align 4
  ret void
}

define void @accumulate_spatial_merging_vec3_region_kernel_c768_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 120
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 124
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.01013 = phi i32 [ %163, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 4
  %29 = load i32, ptr %28, align 4
  %30 = sdiv i32 %.01013, %29
  %31 = mul i32 %30, %29
  %32 = xor i32 %29, %.01013
  %33 = icmp slt i32 %32, 0
  %34 = icmp ne i32 %.01013, %31
  %35 = and i1 %33, %34
  %.neg12 = sext i1 %35 to i32
  %36 = add i32 %30, %.neg12
  %37 = mul i32 %36, %29
  %38 = add i32 %36, %21
  %39 = mul i32 %29, -1
  %40 = mul i32 %39, %36
  %41 = add i32 %23, %.01013
  %42 = add i32 %41, %40
  %43 = getelementptr inbounds nuw i8, ptr %27, i64 8
  %44 = load i32, ptr %43, align 4
  %45 = icmp slt i32 %38, %44
  br i1 %45, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %46 = getelementptr inbounds nuw i8, ptr %27, i64 12
  %47 = load i32, ptr %46, align 4
  %48 = icmp slt i32 %42, %47
  br i1 %48, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %49 = sitofp i32 %38 to float
  %50 = getelementptr inbounds nuw i8, ptr %27, i64 16
  %51 = load float, ptr %50, align 4
  %52 = fmul reassoc ninf nsz float %51, %49
  %53 = sitofp i32 %42 to float
  %54 = getelementptr inbounds nuw i8, ptr %27, i64 20
  %55 = load float, ptr %54, align 4
  %56 = fmul reassoc ninf nsz float %55, %53
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %52)
  %58 = fptosi float %57 to i32
  %59 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %60 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %61 = fptosi float %60 to i32
  %62 = tail call i32 @llvm.smax.i32(i32 %61, i32 0)
  %63 = add nuw i32 %59, 1
  %64 = getelementptr inbounds nuw i8, ptr %27, i64 24
  %65 = load i32, ptr %64, align 4
  %66 = add i32 %65, -1
  %67 = tail call i32 @llvm.smin.i32(i32 %63, i32 %66)
  %68 = add nuw i32 %62, 1
  %69 = getelementptr inbounds nuw i8, ptr %27, i64 28
  %70 = load i32, ptr %69, align 4
  %71 = add i32 %70, -1
  %72 = tail call i32 @llvm.smin.i32(i32 %68, i32 %71)
  %73 = uitofp nneg i32 %59 to float
  %74 = fsub reassoc ninf nsz float %52, %73
  %75 = uitofp nneg i32 %62 to float
  %76 = fsub reassoc ninf nsz float %56, %75
  %77 = fsub reassoc ninf nsz float 1.000000e+00, %74
  %78 = fsub reassoc ninf nsz float 1.000000e+00, %76
  %79 = fmul reassoc ninf nsz float %78, %77
  %80 = load ptr, ptr %0, align 8
  %81 = getelementptr i8, ptr %80, i64 40
  %82 = load ptr, ptr %81, align 8
  %83 = getelementptr i8, ptr %80, i64 28
  %84 = load i32, ptr %83, align 4
  %85 = getelementptr i8, ptr %80, i64 32
  %86 = load i32, ptr %85, align 4
  %87 = mul i32 %84, %59
  %88 = add i32 %87, %62
  %89 = mul i32 %88, %86
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %82, i64 %90
  %92 = load float, ptr %91, align 4
  %93 = fmul reassoc ninf nsz float %79, %92
  %94 = fmul reassoc ninf nsz float %77, %76
  %95 = add i32 %87, %72
  %96 = mul i32 %95, %86
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %82, i64 %97
  %99 = load float, ptr %98, align 4
  %100 = fmul reassoc ninf nsz float %99, %94
  %101 = fadd reassoc ninf nsz float %93, %100
  %102 = fmul reassoc ninf nsz float %78, %74
  %103 = mul i32 %67, %84
  %104 = add i32 %103, %62
  %105 = mul i32 %104, %86
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %82, i64 %106
  %108 = load float, ptr %107, align 4
  %109 = fmul reassoc ninf nsz float %108, %102
  %110 = fadd reassoc ninf nsz float %101, %109
  %111 = fmul reassoc ninf nsz float %76, %74
  %112 = add i32 %103, %72
  %113 = mul i32 %112, %86
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, ptr %82, i64 %114
  %116 = load float, ptr %115, align 4
  %117 = fmul reassoc ninf nsz float %116, %111
  %118 = fadd reassoc ninf nsz float %110, %117
  %119 = getelementptr i8, ptr %80, i64 88
  %120 = load ptr, ptr %119, align 8
  %121 = getelementptr i8, ptr %80, i64 76
  %122 = load i32, ptr %121, align 4
  %123 = getelementptr i8, ptr %80, i64 80
  %124 = load i32, ptr %123, align 4
  %125 = mul i32 %122, %38
  %126 = sub i32 %125, %37
  %127 = add i32 %41, %126
  %128 = mul i32 %127, %124
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %120, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = fadd reassoc ninf nsz float %131, %118
  %133 = getelementptr i8, ptr %80, i64 64
  %134 = load ptr, ptr %133, align 8
  %135 = getelementptr i8, ptr %80, i64 52
  %136 = load i32, ptr %135, align 4
  %137 = getelementptr i8, ptr %80, i64 56
  %138 = load i32, ptr %137, align 4
  %139 = mul i32 %136, %38
  %140 = sub i32 %139, %37
  %141 = add i32 %41, %140
  %142 = mul i32 %141, %138
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %134, i64 %143
  %145 = load float, ptr %144, align 4
  %146 = getelementptr i8, ptr %80, i64 16
  %147 = load ptr, ptr %146, align 8
  %148 = getelementptr i8, ptr %80, i64 4
  %149 = load i32, ptr %148, align 4
  %150 = getelementptr i8, ptr %80, i64 8
  %151 = load i32, ptr %150, align 4
  %152 = mul i32 %149, %38
  %153 = sub i32 %152, %37
  %154 = add i32 %41, %153
  %155 = mul i32 %154, %151
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %147, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = fmul reassoc ninf nsz float %158, %118
  %160 = fadd reassoc ninf nsz float %159, %145
  %161 = getelementptr i8, ptr %80, i64 128
  %162 = load i32, ptr %161, align 4
  %.not = icmp eq i32 %162, 0
  br i1 %.not, label %after_if6, label %true_block4

after_if3:                                        ; preds = %after_if12, %true_block, %for_loop_body
  %163 = add nsw i32 %.01013, 1
  %exitcond.not = icmp eq i32 %18, %163
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %true_block1
  %164 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %132, float 0x3E45798EE0000000)
  %165 = fdiv reassoc ninf nsz float %160, %164
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %true_block1
  %.08 = phi float [ %165, %true_block4 ], [ %160, %true_block1 ]
  store float %132, ptr %130, align 4
  store float %.08, ptr %144, align 4
  %166 = load ptr, ptr %81, align 8
  %167 = load i32, ptr %83, align 4
  %168 = load i32, ptr %85, align 4
  %169 = mul i32 %167, %59
  %170 = add i32 %169, %62
  %171 = mul i32 %170, %168
  %172 = add i32 %171, 1
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, ptr %166, i64 %173
  %175 = load float, ptr %174, align 4
  %176 = fmul reassoc ninf nsz float %175, %79
  %177 = add i32 %169, %72
  %178 = mul i32 %177, %168
  %179 = add i32 %178, 1
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %166, i64 %180
  %182 = load float, ptr %181, align 4
  %183 = fmul reassoc ninf nsz float %182, %94
  %184 = fadd reassoc ninf nsz float %183, %176
  %185 = mul i32 %167, %67
  %186 = add i32 %185, %62
  %187 = mul i32 %186, %168
  %188 = add i32 %187, 1
  %189 = sext i32 %188 to i64
  %190 = getelementptr float, ptr %166, i64 %189
  %191 = load float, ptr %190, align 4
  %192 = fmul reassoc ninf nsz float %191, %102
  %193 = fadd reassoc ninf nsz float %184, %192
  %194 = add i32 %185, %72
  %195 = mul i32 %194, %168
  %196 = add i32 %195, 1
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %166, i64 %197
  %199 = load float, ptr %198, align 4
  %200 = fmul reassoc ninf nsz float %199, %111
  %201 = fadd reassoc ninf nsz float %193, %200
  %202 = load ptr, ptr %119, align 8
  %203 = load i32, ptr %121, align 4
  %204 = load i32, ptr %123, align 4
  %205 = mul i32 %203, %38
  %206 = sub i32 %205, %37
  %207 = add i32 %41, %206
  %208 = mul i32 %207, %204
  %209 = add i32 %208, 1
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, ptr %202, i64 %210
  %212 = load float, ptr %211, align 4
  %213 = fadd reassoc ninf nsz float %212, %201
  %214 = load ptr, ptr %133, align 8
  %215 = load i32, ptr %135, align 4
  %216 = load i32, ptr %137, align 4
  %217 = mul i32 %215, %38
  %218 = sub i32 %217, %37
  %219 = add i32 %41, %218
  %220 = mul i32 %219, %216
  %221 = add i32 %220, 1
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, ptr %214, i64 %222
  %224 = load float, ptr %223, align 4
  %225 = load ptr, ptr %146, align 8
  %226 = load i32, ptr %148, align 4
  %227 = load i32, ptr %150, align 4
  %228 = mul i32 %226, %38
  %229 = sub i32 %228, %37
  %230 = add i32 %41, %229
  %231 = mul i32 %230, %227
  %232 = add i32 %231, 1
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %225, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = fmul reassoc ninf nsz float %235, %201
  %237 = fadd reassoc ninf nsz float %236, %224
  br i1 %.not, label %after_if9, label %true_block7

true_block7:                                      ; preds = %after_if6
  %238 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %213, float 0x3E45798EE0000000)
  %239 = fdiv reassoc ninf nsz float %237, %238
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.07 = phi float [ %239, %true_block7 ], [ %237, %after_if6 ]
  store float %213, ptr %211, align 4
  store float %.07, ptr %223, align 4
  %240 = load ptr, ptr %81, align 8
  %241 = load i32, ptr %83, align 4
  %242 = load i32, ptr %85, align 4
  %243 = mul i32 %241, %59
  %244 = add i32 %243, %62
  %245 = mul i32 %244, %242
  %246 = add i32 %245, 2
  %247 = sext i32 %246 to i64
  %248 = getelementptr float, ptr %240, i64 %247
  %249 = load float, ptr %248, align 4
  %250 = fmul reassoc ninf nsz float %249, %79
  %251 = add i32 %243, %72
  %252 = mul i32 %251, %242
  %253 = add i32 %252, 2
  %254 = sext i32 %253 to i64
  %255 = getelementptr float, ptr %240, i64 %254
  %256 = load float, ptr %255, align 4
  %257 = fmul reassoc ninf nsz float %256, %94
  %258 = fadd reassoc ninf nsz float %257, %250
  %259 = mul i32 %241, %67
  %260 = add i32 %259, %62
  %261 = mul i32 %260, %242
  %262 = add i32 %261, 2
  %263 = sext i32 %262 to i64
  %264 = getelementptr float, ptr %240, i64 %263
  %265 = load float, ptr %264, align 4
  %266 = fmul reassoc ninf nsz float %265, %102
  %267 = fadd reassoc ninf nsz float %258, %266
  %268 = add i32 %259, %72
  %269 = mul i32 %268, %242
  %270 = add i32 %269, 2
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %240, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = fmul reassoc ninf nsz float %273, %111
  %275 = fadd reassoc ninf nsz float %267, %274
  %276 = load ptr, ptr %119, align 8
  %277 = load i32, ptr %121, align 4
  %278 = load i32, ptr %123, align 4
  %279 = mul i32 %277, %38
  %280 = sub i32 %279, %37
  %281 = add i32 %41, %280
  %282 = mul i32 %281, %278
  %283 = add i32 %282, 2
  %284 = sext i32 %283 to i64
  %285 = getelementptr float, ptr %276, i64 %284
  %286 = load float, ptr %285, align 4
  %287 = fadd reassoc ninf nsz float %286, %275
  %288 = load ptr, ptr %133, align 8
  %289 = load i32, ptr %135, align 4
  %290 = load i32, ptr %137, align 4
  %291 = mul i32 %289, %38
  %292 = sub i32 %291, %37
  %293 = add i32 %41, %292
  %294 = mul i32 %293, %290
  %295 = add i32 %294, 2
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, ptr %288, i64 %296
  %298 = load float, ptr %297, align 4
  %299 = load ptr, ptr %146, align 8
  %300 = load i32, ptr %148, align 4
  %301 = load i32, ptr %150, align 4
  %302 = mul i32 %300, %38
  %303 = sub i32 %302, %37
  %304 = add i32 %41, %303
  %305 = mul i32 %304, %301
  %306 = add i32 %305, 2
  %307 = sext i32 %306 to i64
  %308 = getelementptr float, ptr %299, i64 %307
  %309 = load float, ptr %308, align 4
  %310 = fmul reassoc ninf nsz float %309, %275
  %311 = fadd reassoc ninf nsz float %310, %298
  br i1 %.not, label %after_if12, label %true_block10

true_block10:                                     ; preds = %after_if9
  %312 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %287, float 0x3E45798EE0000000)
  %313 = fdiv reassoc ninf nsz float %311, %312
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %.0 = phi float [ %313, %true_block10 ], [ %311, %after_if9 ]
  store float %287, ptr %285, align 4
  store float %.0, ptr %297, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.20, align 8
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
