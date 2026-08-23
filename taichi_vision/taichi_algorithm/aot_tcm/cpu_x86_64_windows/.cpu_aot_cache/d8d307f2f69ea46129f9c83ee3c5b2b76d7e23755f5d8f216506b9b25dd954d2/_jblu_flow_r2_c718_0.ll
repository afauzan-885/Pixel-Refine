; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.19 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_jblu_flow_r2_c718_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_jblu_flow_r2_c718_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %28 = getelementptr i8, ptr %19, i64 76
  %29 = load float, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 72
  %31 = load float, ptr %30, align 4
  %32 = sitofp i32 %21 to float
  %33 = sitofp i32 %23 to float
  %34 = add i32 %21, -1
  %35 = add i32 %23, -1
  %36 = fmul reassoc ninf nsz float %25, -8.000000e+00
  %37 = fmul reassoc ninf nsz float %25, -5.000000e+00
  %38 = fmul reassoc ninf nsz float %25, -4.000000e+00
  %39 = fmul reassoc ninf nsz float %25, -2.000000e+00
  %40 = fneg reassoc ninf nsz float %25
  %41 = icmp slt i32 %16, %18
  br i1 %41, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %42 = getelementptr i8, ptr %19, i64 24
  %43 = getelementptr i8, ptr %19, i64 20
  %44 = getelementptr i8, ptr %19, i64 8
  %45 = getelementptr i8, ptr %19, i64 4
  %46 = fneg reassoc ninf nsz float %27
  %47 = getelementptr i8, ptr %19, i64 40
  %48 = getelementptr i8, ptr %19, i64 36
  %49 = shl i32 %16, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %49, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %880, %for_loop_body ]
  %50 = load ptr, ptr %3, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 32872
  %52 = load ptr, ptr %51, align 8
  %53 = getelementptr inbounds nuw i8, ptr %52, i64 4
  %54 = load i32, ptr %53, align 4
  %55 = sdiv i32 %.05, %54
  %56 = mul i32 %55, %54
  %57 = xor i32 %54, %.05
  %58 = icmp slt i32 %57, 0
  %59 = icmp ne i32 %.05, %56
  %60 = and i1 %58, %59
  %.neg4 = sext i1 %60 to i32
  %61 = add i32 %55, %.neg4
  %62 = mul i32 %54, -1
  %63 = mul i32 %62, %61
  %64 = add i32 %.05, %63
  %65 = sitofp i32 %61 to float
  %66 = fmul reassoc ninf nsz float %65, %32
  %67 = getelementptr inbounds nuw i8, ptr %52, i64 8
  %68 = load i32, ptr %67, align 4
  %69 = sitofp i32 %68 to float
  %70 = fdiv reassoc ninf nsz float %66, %69
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %72 = fptosi float %71 to i32
  %73 = sitofp i32 %64 to float
  %74 = fmul reassoc ninf nsz float %73, %33
  %75 = getelementptr inbounds nuw i8, ptr %52, i64 12
  %76 = load i32, ptr %75, align 4
  %77 = sitofp i32 %76 to float
  %78 = fdiv reassoc ninf nsz float %74, %77
  %79 = tail call reassoc ninf nsz float @llvm.floor.f32(float %78)
  %80 = fptosi float %79 to i32
  %81 = load ptr, ptr %42, align 8
  %82 = load i32, ptr %43, align 4
  %83 = sub i32 %82, %54
  %84 = mul i32 %83, %61
  %85 = add i32 %.05, %84
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %81, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = add i32 %72, -2
  %90 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %91 = tail call i32 @llvm.smin.i32(i32 %34, i32 %90)
  %92 = add i32 %80, -2
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = tail call i32 @llvm.smin.i32(i32 %35, i32 %93)
  %95 = sitofp i32 %91 to float
  %96 = fmul reassoc ninf nsz float %95, %69
  %97 = fdiv reassoc ninf nsz float %96, %32
  %98 = fadd reassoc ninf nsz float %97, 5.000000e-01
  %99 = fptosi float %98 to i32
  %100 = add i32 %68, -1
  %101 = tail call i32 @llvm.smax.i32(i32 %99, i32 0)
  %102 = tail call i32 @llvm.smin.i32(i32 %100, i32 %101)
  %103 = sitofp i32 %94 to float
  %104 = fmul reassoc ninf nsz float %103, %77
  %105 = fdiv reassoc ninf nsz float %104, %33
  %106 = fadd reassoc ninf nsz float %105, 5.000000e-01
  %107 = fptosi float %106 to i32
  %108 = add i32 %76, -1
  %109 = tail call i32 @llvm.smax.i32(i32 %107, i32 0)
  %110 = tail call i32 @llvm.smin.i32(i32 %108, i32 %109)
  %111 = mul i32 %102, %82
  %112 = add i32 %110, %111
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %81, i64 %113
  %115 = load float, ptr %114, align 4
  %116 = fsub reassoc ninf nsz float %115, %88
  %117 = fmul reassoc ninf nsz float %116, %116
  %118 = fmul reassoc ninf nsz float %117, %27
  %119 = fsub reassoc ninf nsz float %36, %118
  %120 = tail call noundef float @expf(float noundef %119) #8
  %121 = load ptr, ptr %44, align 8
  %122 = load i32, ptr %45, align 4
  %123 = mul i32 %91, %122
  %124 = add i32 %94, %123
  %125 = shl i32 %124, 1
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %121, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = getelementptr i8, ptr %127, i64 4
  %130 = load float, ptr %129, align 4
  %131 = fmul reassoc ninf nsz float %128, %120
  %132 = fmul reassoc ninf nsz float %130, %120
  %133 = fadd reassoc ninf nsz float %120, 0x3D71979980000000
  %134 = add i32 %80, -1
  %135 = tail call i32 @llvm.smax.i32(i32 %134, i32 0)
  %136 = tail call i32 @llvm.smin.i32(i32 %35, i32 %135)
  %137 = sitofp i32 %136 to float
  %138 = fmul reassoc ninf nsz float %137, %77
  %139 = fdiv reassoc ninf nsz float %138, %33
  %140 = fadd reassoc ninf nsz float %139, 5.000000e-01
  %141 = fptosi float %140 to i32
  %142 = tail call i32 @llvm.smax.i32(i32 %141, i32 0)
  %143 = tail call i32 @llvm.smin.i32(i32 %108, i32 %142)
  %144 = load ptr, ptr %42, align 8
  %145 = load i32, ptr %43, align 4
  %146 = mul i32 %102, %145
  %147 = add i32 %143, %146
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %144, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = fsub reassoc ninf nsz float %150, %88
  %152 = fmul reassoc ninf nsz float %151, %151
  %153 = fmul reassoc ninf nsz float %152, %27
  %154 = fsub reassoc ninf nsz float %37, %153
  %155 = tail call noundef float @expf(float noundef %154) #8
  %156 = load ptr, ptr %44, align 8
  %157 = load i32, ptr %45, align 4
  %158 = mul i32 %157, %91
  %159 = add i32 %158, %136
  %160 = shl i32 %159, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %156, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = getelementptr i8, ptr %162, i64 4
  %165 = load float, ptr %164, align 4
  %166 = fmul reassoc ninf nsz float %163, %155
  %167 = fmul reassoc ninf nsz float %165, %155
  %168 = fadd reassoc ninf nsz float %166, %131
  %169 = fadd reassoc ninf nsz float %167, %132
  %170 = fadd reassoc ninf nsz float %133, %155
  %171 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %172 = tail call i32 @llvm.smin.i32(i32 %35, i32 %171)
  %173 = sitofp i32 %172 to float
  %174 = fmul reassoc ninf nsz float %173, %77
  %175 = fdiv reassoc ninf nsz float %174, %33
  %176 = fadd reassoc ninf nsz float %175, 5.000000e-01
  %177 = fptosi float %176 to i32
  %178 = tail call i32 @llvm.smax.i32(i32 %177, i32 0)
  %179 = tail call i32 @llvm.smin.i32(i32 %108, i32 %178)
  %180 = load ptr, ptr %42, align 8
  %181 = load i32, ptr %43, align 4
  %182 = mul i32 %181, %102
  %183 = add i32 %182, %179
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, ptr %180, i64 %184
  %186 = load float, ptr %185, align 4
  %187 = fsub reassoc ninf nsz float %186, %88
  %188 = fmul reassoc ninf nsz float %187, %187
  %189 = fmul reassoc ninf nsz float %188, %27
  %190 = fsub reassoc ninf nsz float %38, %189
  %191 = tail call noundef float @expf(float noundef %190) #8
  %192 = load ptr, ptr %44, align 8
  %193 = load i32, ptr %45, align 4
  %194 = mul i32 %193, %91
  %195 = add i32 %194, %172
  %196 = shl i32 %195, 1
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, ptr %192, i64 %197
  %199 = load float, ptr %198, align 4
  %200 = getelementptr i8, ptr %198, i64 4
  %201 = load float, ptr %200, align 4
  %202 = fmul reassoc ninf nsz float %199, %191
  %203 = fmul reassoc ninf nsz float %201, %191
  %204 = fadd reassoc ninf nsz float %168, %202
  %205 = fadd reassoc ninf nsz float %169, %203
  %206 = fadd reassoc ninf nsz float %170, %191
  %207 = add i32 %80, 1
  %208 = tail call i32 @llvm.smax.i32(i32 %207, i32 0)
  %209 = tail call i32 @llvm.smin.i32(i32 %35, i32 %208)
  %210 = sitofp i32 %209 to float
  %211 = fmul reassoc ninf nsz float %210, %77
  %212 = fdiv reassoc ninf nsz float %211, %33
  %213 = fadd reassoc ninf nsz float %212, 5.000000e-01
  %214 = fptosi float %213 to i32
  %215 = tail call i32 @llvm.smax.i32(i32 %214, i32 0)
  %216 = tail call i32 @llvm.smin.i32(i32 %108, i32 %215)
  %217 = load ptr, ptr %42, align 8
  %218 = load i32, ptr %43, align 4
  %219 = mul i32 %218, %102
  %220 = add i32 %219, %216
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, ptr %217, i64 %221
  %223 = load float, ptr %222, align 4
  %224 = fsub reassoc ninf nsz float %223, %88
  %225 = fmul reassoc ninf nsz float %224, %224
  %226 = fmul reassoc ninf nsz float %225, %27
  %227 = fsub reassoc ninf nsz float %37, %226
  %228 = tail call noundef float @expf(float noundef %227) #8
  %229 = load ptr, ptr %44, align 8
  %230 = load i32, ptr %45, align 4
  %231 = mul i32 %230, %91
  %232 = add i32 %231, %209
  %233 = shl i32 %232, 1
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, ptr %229, i64 %234
  %236 = load float, ptr %235, align 4
  %237 = getelementptr i8, ptr %235, i64 4
  %238 = load float, ptr %237, align 4
  %239 = fmul reassoc ninf nsz float %236, %228
  %240 = fmul reassoc ninf nsz float %238, %228
  %241 = fadd reassoc ninf nsz float %204, %239
  %242 = fadd reassoc ninf nsz float %205, %240
  %243 = fadd reassoc ninf nsz float %206, %228
  %244 = add i32 %80, 2
  %245 = tail call i32 @llvm.smax.i32(i32 %244, i32 0)
  %246 = tail call i32 @llvm.smin.i32(i32 %35, i32 %245)
  %247 = sitofp i32 %246 to float
  %248 = fmul reassoc ninf nsz float %247, %77
  %249 = fdiv reassoc ninf nsz float %248, %33
  %250 = fadd reassoc ninf nsz float %249, 5.000000e-01
  %251 = fptosi float %250 to i32
  %252 = tail call i32 @llvm.smax.i32(i32 %251, i32 0)
  %253 = tail call i32 @llvm.smin.i32(i32 %108, i32 %252)
  %254 = load ptr, ptr %42, align 8
  %255 = load i32, ptr %43, align 4
  %256 = mul i32 %255, %102
  %257 = add i32 %256, %253
  %258 = sext i32 %257 to i64
  %259 = getelementptr float, ptr %254, i64 %258
  %260 = load float, ptr %259, align 4
  %261 = fsub reassoc ninf nsz float %260, %88
  %262 = fmul reassoc ninf nsz float %261, %261
  %263 = fmul reassoc ninf nsz float %262, %27
  %264 = fsub reassoc ninf nsz float %36, %263
  %265 = tail call noundef float @expf(float noundef %264) #8
  %266 = load ptr, ptr %44, align 8
  %267 = load i32, ptr %45, align 4
  %268 = mul i32 %267, %91
  %269 = add i32 %268, %246
  %270 = shl i32 %269, 1
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %266, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = getelementptr i8, ptr %272, i64 4
  %275 = load float, ptr %274, align 4
  %276 = fmul reassoc ninf nsz float %273, %265
  %277 = fmul reassoc ninf nsz float %275, %265
  %278 = fadd reassoc ninf nsz float %241, %276
  %279 = fadd reassoc ninf nsz float %242, %277
  %280 = fadd reassoc ninf nsz float %243, %265
  %281 = add i32 %72, -1
  %282 = tail call i32 @llvm.smax.i32(i32 %281, i32 0)
  %283 = tail call i32 @llvm.smin.i32(i32 %34, i32 %282)
  %284 = sitofp i32 %283 to float
  %285 = fmul reassoc ninf nsz float %284, %69
  %286 = fdiv reassoc ninf nsz float %285, %32
  %287 = fadd reassoc ninf nsz float %286, 5.000000e-01
  %288 = fptosi float %287 to i32
  %289 = tail call i32 @llvm.smax.i32(i32 %288, i32 0)
  %290 = tail call i32 @llvm.smin.i32(i32 %100, i32 %289)
  %291 = load ptr, ptr %42, align 8
  %292 = load i32, ptr %43, align 4
  %293 = mul i32 %292, %290
  %294 = add i32 %293, %110
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, ptr %291, i64 %295
  %297 = load float, ptr %296, align 4
  %298 = fsub reassoc ninf nsz float %297, %88
  %299 = fmul reassoc ninf nsz float %298, %298
  %300 = fmul reassoc ninf nsz float %299, %27
  %301 = fsub reassoc ninf nsz float %37, %300
  %302 = tail call noundef float @expf(float noundef %301) #8
  %303 = load ptr, ptr %44, align 8
  %304 = load i32, ptr %45, align 4
  %305 = mul i32 %304, %283
  %306 = add i32 %305, %94
  %307 = shl i32 %306, 1
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %303, i64 %308
  %310 = load float, ptr %309, align 4
  %311 = getelementptr i8, ptr %309, i64 4
  %312 = load float, ptr %311, align 4
  %313 = fmul reassoc ninf nsz float %310, %302
  %314 = fmul reassoc ninf nsz float %312, %302
  %315 = fadd reassoc ninf nsz float %278, %313
  %316 = fadd reassoc ninf nsz float %279, %314
  %317 = fadd reassoc ninf nsz float %280, %302
  %318 = load ptr, ptr %42, align 8
  %319 = load i32, ptr %43, align 4
  %320 = mul i32 %319, %290
  %321 = add i32 %320, %143
  %322 = sext i32 %321 to i64
  %323 = getelementptr float, ptr %318, i64 %322
  %324 = load float, ptr %323, align 4
  %325 = fsub reassoc ninf nsz float %324, %88
  %326 = fmul reassoc ninf nsz float %325, %325
  %327 = fmul reassoc ninf nsz float %326, %27
  %328 = fsub reassoc ninf nsz float %39, %327
  %329 = tail call noundef float @expf(float noundef %328) #8
  %330 = load ptr, ptr %44, align 8
  %331 = load i32, ptr %45, align 4
  %332 = mul i32 %331, %283
  %333 = add i32 %332, %136
  %334 = shl i32 %333, 1
  %335 = sext i32 %334 to i64
  %336 = getelementptr float, ptr %330, i64 %335
  %337 = load float, ptr %336, align 4
  %338 = getelementptr i8, ptr %336, i64 4
  %339 = load float, ptr %338, align 4
  %340 = fmul reassoc ninf nsz float %337, %329
  %341 = fmul reassoc ninf nsz float %339, %329
  %342 = fadd reassoc ninf nsz float %315, %340
  %343 = fadd reassoc ninf nsz float %316, %341
  %344 = fadd reassoc ninf nsz float %317, %329
  %345 = load ptr, ptr %42, align 8
  %346 = load i32, ptr %43, align 4
  %347 = mul i32 %346, %290
  %348 = add i32 %347, %179
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, ptr %345, i64 %349
  %351 = load float, ptr %350, align 4
  %352 = fsub reassoc ninf nsz float %351, %88
  %353 = fmul reassoc ninf nsz float %352, %352
  %354 = fmul reassoc ninf nsz float %353, %27
  %355 = fsub reassoc ninf nsz float %40, %354
  %356 = tail call noundef float @expf(float noundef %355) #8
  %357 = load ptr, ptr %44, align 8
  %358 = load i32, ptr %45, align 4
  %359 = mul i32 %358, %283
  %360 = add i32 %359, %172
  %361 = shl i32 %360, 1
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, ptr %357, i64 %362
  %364 = load float, ptr %363, align 4
  %365 = getelementptr i8, ptr %363, i64 4
  %366 = load float, ptr %365, align 4
  %367 = fmul reassoc ninf nsz float %364, %356
  %368 = fmul reassoc ninf nsz float %366, %356
  %369 = fadd reassoc ninf nsz float %342, %367
  %370 = fadd reassoc ninf nsz float %343, %368
  %371 = fadd reassoc ninf nsz float %344, %356
  %372 = load ptr, ptr %42, align 8
  %373 = load i32, ptr %43, align 4
  %374 = mul i32 %373, %290
  %375 = add i32 %374, %216
  %376 = sext i32 %375 to i64
  %377 = getelementptr float, ptr %372, i64 %376
  %378 = load float, ptr %377, align 4
  %379 = fsub reassoc ninf nsz float %378, %88
  %380 = fmul reassoc ninf nsz float %379, %379
  %381 = fmul reassoc ninf nsz float %380, %27
  %382 = fsub reassoc ninf nsz float %39, %381
  %383 = tail call noundef float @expf(float noundef %382) #8
  %384 = load ptr, ptr %44, align 8
  %385 = load i32, ptr %45, align 4
  %386 = mul i32 %385, %283
  %387 = add i32 %386, %209
  %388 = shl i32 %387, 1
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, ptr %384, i64 %389
  %391 = load float, ptr %390, align 4
  %392 = getelementptr i8, ptr %390, i64 4
  %393 = load float, ptr %392, align 4
  %394 = fmul reassoc ninf nsz float %391, %383
  %395 = fmul reassoc ninf nsz float %393, %383
  %396 = fadd reassoc ninf nsz float %369, %394
  %397 = fadd reassoc ninf nsz float %370, %395
  %398 = fadd reassoc ninf nsz float %371, %383
  %399 = load ptr, ptr %42, align 8
  %400 = load i32, ptr %43, align 4
  %401 = mul i32 %400, %290
  %402 = add i32 %401, %253
  %403 = sext i32 %402 to i64
  %404 = getelementptr float, ptr %399, i64 %403
  %405 = load float, ptr %404, align 4
  %406 = fsub reassoc ninf nsz float %405, %88
  %407 = fmul reassoc ninf nsz float %406, %406
  %408 = fmul reassoc ninf nsz float %407, %27
  %409 = fsub reassoc ninf nsz float %37, %408
  %410 = tail call noundef float @expf(float noundef %409) #8
  %411 = load ptr, ptr %44, align 8
  %412 = load i32, ptr %45, align 4
  %413 = mul i32 %412, %283
  %414 = add i32 %413, %246
  %415 = shl i32 %414, 1
  %416 = sext i32 %415 to i64
  %417 = getelementptr float, ptr %411, i64 %416
  %418 = load float, ptr %417, align 4
  %419 = getelementptr i8, ptr %417, i64 4
  %420 = load float, ptr %419, align 4
  %421 = fmul reassoc ninf nsz float %418, %410
  %422 = fmul reassoc ninf nsz float %420, %410
  %423 = fadd reassoc ninf nsz float %396, %421
  %424 = fadd reassoc ninf nsz float %397, %422
  %425 = fadd reassoc ninf nsz float %398, %410
  %426 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %427 = tail call i32 @llvm.smin.i32(i32 %34, i32 %426)
  %428 = sitofp i32 %427 to float
  %429 = fmul reassoc ninf nsz float %428, %69
  %430 = fdiv reassoc ninf nsz float %429, %32
  %431 = fadd reassoc ninf nsz float %430, 5.000000e-01
  %432 = fptosi float %431 to i32
  %433 = tail call i32 @llvm.smax.i32(i32 %432, i32 0)
  %434 = tail call i32 @llvm.smin.i32(i32 %100, i32 %433)
  %435 = load ptr, ptr %42, align 8
  %436 = load i32, ptr %43, align 4
  %437 = mul i32 %436, %434
  %438 = add i32 %437, %110
  %439 = sext i32 %438 to i64
  %440 = getelementptr float, ptr %435, i64 %439
  %441 = load float, ptr %440, align 4
  %442 = fsub reassoc ninf nsz float %441, %88
  %443 = fmul reassoc ninf nsz float %442, %442
  %444 = fmul reassoc ninf nsz float %443, %27
  %445 = fsub reassoc ninf nsz float %38, %444
  %446 = tail call noundef float @expf(float noundef %445) #8
  %447 = load ptr, ptr %44, align 8
  %448 = load i32, ptr %45, align 4
  %449 = mul i32 %448, %427
  %450 = add i32 %449, %94
  %451 = shl i32 %450, 1
  %452 = sext i32 %451 to i64
  %453 = getelementptr float, ptr %447, i64 %452
  %454 = load float, ptr %453, align 4
  %455 = getelementptr i8, ptr %453, i64 4
  %456 = load float, ptr %455, align 4
  %457 = fmul reassoc ninf nsz float %454, %446
  %458 = fmul reassoc ninf nsz float %456, %446
  %459 = fadd reassoc ninf nsz float %423, %457
  %460 = fadd reassoc ninf nsz float %424, %458
  %461 = fadd reassoc ninf nsz float %425, %446
  %462 = load ptr, ptr %42, align 8
  %463 = load i32, ptr %43, align 4
  %464 = mul i32 %463, %434
  %465 = add i32 %464, %143
  %466 = sext i32 %465 to i64
  %467 = getelementptr float, ptr %462, i64 %466
  %468 = load float, ptr %467, align 4
  %469 = fsub reassoc ninf nsz float %468, %88
  %470 = fmul reassoc ninf nsz float %469, %469
  %471 = fmul reassoc ninf nsz float %470, %27
  %472 = fsub reassoc ninf nsz float %40, %471
  %473 = tail call noundef float @expf(float noundef %472) #8
  %474 = load ptr, ptr %44, align 8
  %475 = load i32, ptr %45, align 4
  %476 = mul i32 %475, %427
  %477 = add i32 %476, %136
  %478 = shl i32 %477, 1
  %479 = sext i32 %478 to i64
  %480 = getelementptr float, ptr %474, i64 %479
  %481 = load float, ptr %480, align 4
  %482 = getelementptr i8, ptr %480, i64 4
  %483 = load float, ptr %482, align 4
  %484 = fmul reassoc ninf nsz float %481, %473
  %485 = fmul reassoc ninf nsz float %483, %473
  %486 = fadd reassoc ninf nsz float %459, %484
  %487 = fadd reassoc ninf nsz float %460, %485
  %488 = fadd reassoc ninf nsz float %461, %473
  %489 = load ptr, ptr %42, align 8
  %490 = load i32, ptr %43, align 4
  %491 = mul i32 %490, %434
  %492 = add i32 %491, %179
  %493 = sext i32 %492 to i64
  %494 = getelementptr float, ptr %489, i64 %493
  %495 = load float, ptr %494, align 4
  %496 = fsub reassoc ninf nsz float %495, %88
  %497 = fmul reassoc ninf nsz float %496, %496
  %498 = fmul reassoc ninf nsz float %497, %46
  %499 = tail call noundef float @expf(float noundef %498) #8
  %500 = load ptr, ptr %44, align 8
  %501 = load i32, ptr %45, align 4
  %502 = mul i32 %501, %427
  %503 = add i32 %502, %172
  %504 = shl i32 %503, 1
  %505 = sext i32 %504 to i64
  %506 = getelementptr float, ptr %500, i64 %505
  %507 = load float, ptr %506, align 4
  %508 = getelementptr i8, ptr %506, i64 4
  %509 = load float, ptr %508, align 4
  %510 = fmul reassoc ninf nsz float %507, %499
  %511 = fmul reassoc ninf nsz float %509, %499
  %512 = fadd reassoc ninf nsz float %486, %510
  %513 = fadd reassoc ninf nsz float %487, %511
  %514 = fadd reassoc ninf nsz float %488, %499
  %515 = load ptr, ptr %42, align 8
  %516 = load i32, ptr %43, align 4
  %517 = mul i32 %516, %434
  %518 = add i32 %517, %216
  %519 = sext i32 %518 to i64
  %520 = getelementptr float, ptr %515, i64 %519
  %521 = load float, ptr %520, align 4
  %522 = fsub reassoc ninf nsz float %521, %88
  %523 = fmul reassoc ninf nsz float %522, %522
  %524 = fmul reassoc ninf nsz float %523, %27
  %525 = fsub reassoc ninf nsz float %40, %524
  %526 = tail call noundef float @expf(float noundef %525) #8
  %527 = load ptr, ptr %44, align 8
  %528 = load i32, ptr %45, align 4
  %529 = mul i32 %528, %427
  %530 = add i32 %529, %209
  %531 = shl i32 %530, 1
  %532 = sext i32 %531 to i64
  %533 = getelementptr float, ptr %527, i64 %532
  %534 = load float, ptr %533, align 4
  %535 = getelementptr i8, ptr %533, i64 4
  %536 = load float, ptr %535, align 4
  %537 = fmul reassoc ninf nsz float %534, %526
  %538 = fmul reassoc ninf nsz float %536, %526
  %539 = fadd reassoc ninf nsz float %512, %537
  %540 = fadd reassoc ninf nsz float %513, %538
  %541 = fadd reassoc ninf nsz float %514, %526
  %542 = load ptr, ptr %42, align 8
  %543 = load i32, ptr %43, align 4
  %544 = mul i32 %543, %434
  %545 = add i32 %544, %253
  %546 = sext i32 %545 to i64
  %547 = getelementptr float, ptr %542, i64 %546
  %548 = load float, ptr %547, align 4
  %549 = fsub reassoc ninf nsz float %548, %88
  %550 = fmul reassoc ninf nsz float %549, %549
  %551 = fmul reassoc ninf nsz float %550, %27
  %552 = fsub reassoc ninf nsz float %38, %551
  %553 = tail call noundef float @expf(float noundef %552) #8
  %554 = load ptr, ptr %44, align 8
  %555 = load i32, ptr %45, align 4
  %556 = mul i32 %555, %427
  %557 = add i32 %556, %246
  %558 = shl i32 %557, 1
  %559 = sext i32 %558 to i64
  %560 = getelementptr float, ptr %554, i64 %559
  %561 = load float, ptr %560, align 4
  %562 = getelementptr i8, ptr %560, i64 4
  %563 = load float, ptr %562, align 4
  %564 = fmul reassoc ninf nsz float %561, %553
  %565 = fmul reassoc ninf nsz float %563, %553
  %566 = fadd reassoc ninf nsz float %539, %564
  %567 = fadd reassoc ninf nsz float %540, %565
  %568 = fadd reassoc ninf nsz float %541, %553
  %569 = add i32 %72, 1
  %570 = tail call i32 @llvm.smax.i32(i32 %569, i32 0)
  %571 = tail call i32 @llvm.smin.i32(i32 %34, i32 %570)
  %572 = sitofp i32 %571 to float
  %573 = fmul reassoc ninf nsz float %572, %69
  %574 = fdiv reassoc ninf nsz float %573, %32
  %575 = fadd reassoc ninf nsz float %574, 5.000000e-01
  %576 = fptosi float %575 to i32
  %577 = tail call i32 @llvm.smax.i32(i32 %576, i32 0)
  %578 = tail call i32 @llvm.smin.i32(i32 %100, i32 %577)
  %579 = load ptr, ptr %42, align 8
  %580 = load i32, ptr %43, align 4
  %581 = mul i32 %580, %578
  %582 = add i32 %581, %110
  %583 = sext i32 %582 to i64
  %584 = getelementptr float, ptr %579, i64 %583
  %585 = load float, ptr %584, align 4
  %586 = fsub reassoc ninf nsz float %585, %88
  %587 = fmul reassoc ninf nsz float %586, %586
  %588 = fmul reassoc ninf nsz float %587, %27
  %589 = fsub reassoc ninf nsz float %37, %588
  %590 = tail call noundef float @expf(float noundef %589) #8
  %591 = load ptr, ptr %44, align 8
  %592 = load i32, ptr %45, align 4
  %593 = mul i32 %592, %571
  %594 = add i32 %593, %94
  %595 = shl i32 %594, 1
  %596 = sext i32 %595 to i64
  %597 = getelementptr float, ptr %591, i64 %596
  %598 = load float, ptr %597, align 4
  %599 = getelementptr i8, ptr %597, i64 4
  %600 = load float, ptr %599, align 4
  %601 = fmul reassoc ninf nsz float %598, %590
  %602 = fmul reassoc ninf nsz float %600, %590
  %603 = fadd reassoc ninf nsz float %566, %601
  %604 = fadd reassoc ninf nsz float %567, %602
  %605 = fadd reassoc ninf nsz float %568, %590
  %606 = load ptr, ptr %42, align 8
  %607 = load i32, ptr %43, align 4
  %608 = mul i32 %607, %578
  %609 = add i32 %608, %143
  %610 = sext i32 %609 to i64
  %611 = getelementptr float, ptr %606, i64 %610
  %612 = load float, ptr %611, align 4
  %613 = fsub reassoc ninf nsz float %612, %88
  %614 = fmul reassoc ninf nsz float %613, %613
  %615 = fmul reassoc ninf nsz float %614, %27
  %616 = fsub reassoc ninf nsz float %39, %615
  %617 = tail call noundef float @expf(float noundef %616) #8
  %618 = load ptr, ptr %44, align 8
  %619 = load i32, ptr %45, align 4
  %620 = mul i32 %619, %571
  %621 = add i32 %620, %136
  %622 = shl i32 %621, 1
  %623 = sext i32 %622 to i64
  %624 = getelementptr float, ptr %618, i64 %623
  %625 = load float, ptr %624, align 4
  %626 = getelementptr i8, ptr %624, i64 4
  %627 = load float, ptr %626, align 4
  %628 = fmul reassoc ninf nsz float %625, %617
  %629 = fmul reassoc ninf nsz float %627, %617
  %630 = fadd reassoc ninf nsz float %603, %628
  %631 = fadd reassoc ninf nsz float %604, %629
  %632 = fadd reassoc ninf nsz float %605, %617
  %633 = load ptr, ptr %42, align 8
  %634 = load i32, ptr %43, align 4
  %635 = mul i32 %634, %578
  %636 = add i32 %635, %179
  %637 = sext i32 %636 to i64
  %638 = getelementptr float, ptr %633, i64 %637
  %639 = load float, ptr %638, align 4
  %640 = fsub reassoc ninf nsz float %639, %88
  %641 = fmul reassoc ninf nsz float %640, %640
  %642 = fmul reassoc ninf nsz float %641, %27
  %643 = fsub reassoc ninf nsz float %40, %642
  %644 = tail call noundef float @expf(float noundef %643) #8
  %645 = load ptr, ptr %44, align 8
  %646 = load i32, ptr %45, align 4
  %647 = mul i32 %646, %571
  %648 = add i32 %647, %172
  %649 = shl i32 %648, 1
  %650 = sext i32 %649 to i64
  %651 = getelementptr float, ptr %645, i64 %650
  %652 = load float, ptr %651, align 4
  %653 = getelementptr i8, ptr %651, i64 4
  %654 = load float, ptr %653, align 4
  %655 = fmul reassoc ninf nsz float %652, %644
  %656 = fmul reassoc ninf nsz float %654, %644
  %657 = fadd reassoc ninf nsz float %630, %655
  %658 = fadd reassoc ninf nsz float %631, %656
  %659 = fadd reassoc ninf nsz float %632, %644
  %660 = load ptr, ptr %42, align 8
  %661 = load i32, ptr %43, align 4
  %662 = mul i32 %661, %578
  %663 = add i32 %662, %216
  %664 = sext i32 %663 to i64
  %665 = getelementptr float, ptr %660, i64 %664
  %666 = load float, ptr %665, align 4
  %667 = fsub reassoc ninf nsz float %666, %88
  %668 = fmul reassoc ninf nsz float %667, %667
  %669 = fmul reassoc ninf nsz float %668, %27
  %670 = fsub reassoc ninf nsz float %39, %669
  %671 = tail call noundef float @expf(float noundef %670) #8
  %672 = load ptr, ptr %44, align 8
  %673 = load i32, ptr %45, align 4
  %674 = mul i32 %673, %571
  %675 = add i32 %674, %209
  %676 = shl i32 %675, 1
  %677 = sext i32 %676 to i64
  %678 = getelementptr float, ptr %672, i64 %677
  %679 = load float, ptr %678, align 4
  %680 = getelementptr i8, ptr %678, i64 4
  %681 = load float, ptr %680, align 4
  %682 = fmul reassoc ninf nsz float %679, %671
  %683 = fmul reassoc ninf nsz float %681, %671
  %684 = fadd reassoc ninf nsz float %657, %682
  %685 = fadd reassoc ninf nsz float %658, %683
  %686 = fadd reassoc ninf nsz float %659, %671
  %687 = load ptr, ptr %42, align 8
  %688 = load i32, ptr %43, align 4
  %689 = mul i32 %688, %578
  %690 = add i32 %689, %253
  %691 = sext i32 %690 to i64
  %692 = getelementptr float, ptr %687, i64 %691
  %693 = load float, ptr %692, align 4
  %694 = fsub reassoc ninf nsz float %693, %88
  %695 = fmul reassoc ninf nsz float %694, %694
  %696 = fmul reassoc ninf nsz float %695, %27
  %697 = fsub reassoc ninf nsz float %37, %696
  %698 = tail call noundef float @expf(float noundef %697) #8
  %699 = load ptr, ptr %44, align 8
  %700 = load i32, ptr %45, align 4
  %701 = mul i32 %700, %571
  %702 = add i32 %701, %246
  %703 = shl i32 %702, 1
  %704 = sext i32 %703 to i64
  %705 = getelementptr float, ptr %699, i64 %704
  %706 = load float, ptr %705, align 4
  %707 = getelementptr i8, ptr %705, i64 4
  %708 = load float, ptr %707, align 4
  %709 = fmul reassoc ninf nsz float %706, %698
  %710 = fmul reassoc ninf nsz float %708, %698
  %711 = fadd reassoc ninf nsz float %684, %709
  %712 = fadd reassoc ninf nsz float %685, %710
  %713 = fadd reassoc ninf nsz float %686, %698
  %714 = add i32 %72, 2
  %715 = tail call i32 @llvm.smax.i32(i32 %714, i32 0)
  %716 = tail call i32 @llvm.smin.i32(i32 %34, i32 %715)
  %717 = sitofp i32 %716 to float
  %718 = fmul reassoc ninf nsz float %717, %69
  %719 = fdiv reassoc ninf nsz float %718, %32
  %720 = fadd reassoc ninf nsz float %719, 5.000000e-01
  %721 = fptosi float %720 to i32
  %722 = tail call i32 @llvm.smax.i32(i32 %721, i32 0)
  %723 = tail call i32 @llvm.smin.i32(i32 %100, i32 %722)
  %724 = load ptr, ptr %42, align 8
  %725 = load i32, ptr %43, align 4
  %726 = mul i32 %725, %723
  %727 = add i32 %726, %110
  %728 = sext i32 %727 to i64
  %729 = getelementptr float, ptr %724, i64 %728
  %730 = load float, ptr %729, align 4
  %731 = fsub reassoc ninf nsz float %730, %88
  %732 = fmul reassoc ninf nsz float %731, %731
  %733 = fmul reassoc ninf nsz float %732, %27
  %734 = fsub reassoc ninf nsz float %36, %733
  %735 = tail call noundef float @expf(float noundef %734) #8
  %736 = load ptr, ptr %44, align 8
  %737 = load i32, ptr %45, align 4
  %738 = mul i32 %737, %716
  %739 = add i32 %738, %94
  %740 = shl i32 %739, 1
  %741 = sext i32 %740 to i64
  %742 = getelementptr float, ptr %736, i64 %741
  %743 = load float, ptr %742, align 4
  %744 = getelementptr i8, ptr %742, i64 4
  %745 = load float, ptr %744, align 4
  %746 = fmul reassoc ninf nsz float %743, %735
  %747 = fmul reassoc ninf nsz float %745, %735
  %748 = fadd reassoc ninf nsz float %711, %746
  %749 = fadd reassoc ninf nsz float %712, %747
  %750 = fadd reassoc ninf nsz float %713, %735
  %751 = load ptr, ptr %42, align 8
  %752 = load i32, ptr %43, align 4
  %753 = mul i32 %752, %723
  %754 = add i32 %753, %143
  %755 = sext i32 %754 to i64
  %756 = getelementptr float, ptr %751, i64 %755
  %757 = load float, ptr %756, align 4
  %758 = fsub reassoc ninf nsz float %757, %88
  %759 = fmul reassoc ninf nsz float %758, %758
  %760 = fmul reassoc ninf nsz float %759, %27
  %761 = fsub reassoc ninf nsz float %37, %760
  %762 = tail call noundef float @expf(float noundef %761) #8
  %763 = load ptr, ptr %44, align 8
  %764 = load i32, ptr %45, align 4
  %765 = mul i32 %764, %716
  %766 = add i32 %765, %136
  %767 = shl i32 %766, 1
  %768 = sext i32 %767 to i64
  %769 = getelementptr float, ptr %763, i64 %768
  %770 = load float, ptr %769, align 4
  %771 = getelementptr i8, ptr %769, i64 4
  %772 = load float, ptr %771, align 4
  %773 = fmul reassoc ninf nsz float %770, %762
  %774 = fmul reassoc ninf nsz float %772, %762
  %775 = fadd reassoc ninf nsz float %748, %773
  %776 = fadd reassoc ninf nsz float %749, %774
  %777 = fadd reassoc ninf nsz float %750, %762
  %778 = load ptr, ptr %42, align 8
  %779 = load i32, ptr %43, align 4
  %780 = mul i32 %779, %723
  %781 = add i32 %780, %179
  %782 = sext i32 %781 to i64
  %783 = getelementptr float, ptr %778, i64 %782
  %784 = load float, ptr %783, align 4
  %785 = fsub reassoc ninf nsz float %784, %88
  %786 = fmul reassoc ninf nsz float %785, %785
  %787 = fmul reassoc ninf nsz float %786, %27
  %788 = fsub reassoc ninf nsz float %38, %787
  %789 = tail call noundef float @expf(float noundef %788) #8
  %790 = load ptr, ptr %44, align 8
  %791 = load i32, ptr %45, align 4
  %792 = mul i32 %791, %716
  %793 = add i32 %792, %172
  %794 = shl i32 %793, 1
  %795 = sext i32 %794 to i64
  %796 = getelementptr float, ptr %790, i64 %795
  %797 = load float, ptr %796, align 4
  %798 = getelementptr i8, ptr %796, i64 4
  %799 = load float, ptr %798, align 4
  %800 = fmul reassoc ninf nsz float %797, %789
  %801 = fmul reassoc ninf nsz float %799, %789
  %802 = fadd reassoc ninf nsz float %775, %800
  %803 = fadd reassoc ninf nsz float %776, %801
  %804 = fadd reassoc ninf nsz float %777, %789
  %805 = load ptr, ptr %42, align 8
  %806 = load i32, ptr %43, align 4
  %807 = mul i32 %806, %723
  %808 = add i32 %807, %216
  %809 = sext i32 %808 to i64
  %810 = getelementptr float, ptr %805, i64 %809
  %811 = load float, ptr %810, align 4
  %812 = fsub reassoc ninf nsz float %811, %88
  %813 = fmul reassoc ninf nsz float %812, %812
  %814 = fmul reassoc ninf nsz float %813, %27
  %815 = fsub reassoc ninf nsz float %37, %814
  %816 = tail call noundef float @expf(float noundef %815) #8
  %817 = load ptr, ptr %44, align 8
  %818 = load i32, ptr %45, align 4
  %819 = mul i32 %818, %716
  %820 = add i32 %819, %209
  %821 = shl i32 %820, 1
  %822 = sext i32 %821 to i64
  %823 = getelementptr float, ptr %817, i64 %822
  %824 = load float, ptr %823, align 4
  %825 = getelementptr i8, ptr %823, i64 4
  %826 = load float, ptr %825, align 4
  %827 = fmul reassoc ninf nsz float %824, %816
  %828 = fmul reassoc ninf nsz float %826, %816
  %829 = fadd reassoc ninf nsz float %802, %827
  %830 = fadd reassoc ninf nsz float %803, %828
  %831 = fadd reassoc ninf nsz float %804, %816
  %832 = load ptr, ptr %42, align 8
  %833 = load i32, ptr %43, align 4
  %834 = mul i32 %833, %723
  %835 = add i32 %834, %253
  %836 = sext i32 %835 to i64
  %837 = getelementptr float, ptr %832, i64 %836
  %838 = load float, ptr %837, align 4
  %839 = fsub reassoc ninf nsz float %838, %88
  %840 = fmul reassoc ninf nsz float %839, %839
  %841 = fmul reassoc ninf nsz float %840, %27
  %842 = fsub reassoc ninf nsz float %36, %841
  %843 = tail call noundef float @expf(float noundef %842) #8
  %844 = load ptr, ptr %44, align 8
  %845 = load i32, ptr %45, align 4
  %846 = mul i32 %845, %716
  %847 = add i32 %846, %246
  %848 = shl i32 %847, 1
  %849 = sext i32 %848 to i64
  %850 = getelementptr float, ptr %844, i64 %849
  %851 = load float, ptr %850, align 4
  %852 = getelementptr i8, ptr %850, i64 4
  %853 = load float, ptr %852, align 4
  %854 = fmul reassoc ninf nsz float %851, %843
  %855 = fmul reassoc ninf nsz float %853, %843
  %856 = fadd reassoc ninf nsz float %829, %854
  %857 = fadd reassoc ninf nsz float %830, %855
  %858 = fadd reassoc ninf nsz float %831, %843
  %859 = fmul reassoc ninf nsz float %856, %29
  %860 = fdiv reassoc ninf nsz float %859, %858
  %861 = fmul reassoc ninf nsz float %857, %31
  %862 = fdiv reassoc ninf nsz float %861, %858
  %863 = load ptr, ptr %47, align 8
  %864 = load i32, ptr %48, align 4
  %865 = sub i32 %864, %54
  %866 = shl i32 %865, 1
  %867 = mul i32 %866, %61
  %868 = add i32 %lsr.iv, %867
  %869 = sext i32 %868 to i64
  %870 = getelementptr float, ptr %863, i64 %869
  store float %860, ptr %870, align 4
  %871 = load ptr, ptr %47, align 8
  %872 = load i32, ptr %48, align 4
  %873 = sub i32 %872, %54
  %874 = shl i32 %873, 1
  %875 = mul i32 %874, %61
  %876 = add i32 %lsr.iv, %875
  %877 = add i32 %876, 1
  %878 = sext i32 %877 to i64
  %879 = getelementptr float, ptr %871, i64 %878
  store float %862, ptr %879, align 4
  %880 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %18, %880
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
  %4 = alloca %struct.RuntimeContext.19, align 8
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
