; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_upsample_flow_kernel_c270_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 16
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 8
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 24
  %16 = load i32, ptr %15, align 4
  %17 = load ptr, ptr %2, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 20
  store i32 %16, ptr %20, align 4
  %21 = load ptr, ptr %context, align 8
  %22 = getelementptr i8, ptr %21, i64 28
  %23 = load i32, ptr %22, align 4
  %24 = load ptr, ptr %2, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 32872
  %26 = load ptr, ptr %25, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 12
  store i32 %23, ptr %27, align 4
  %28 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %29 = tail call i32 @llvm.smax.i32(i32 %23, i32 0)
  %30 = load ptr, ptr %2, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 32872
  %32 = load ptr, ptr %31, align 8
  %33 = getelementptr inbounds nuw i8, ptr %32, i64 4
  store i32 %29, ptr %33, align 4
  %34 = mul i32 %29, %28
  %35 = load ptr, ptr %2, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 32872
  %37 = load ptr, ptr %36, align 8
  store i32 %34, ptr %37, align 4
  ret void
}

define void @_upsample_flow_kernel_c270_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = load float, ptr %20, align 4
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

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %440, %for_loop_body ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.05, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.05
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.05, %35
  %39 = and i1 %37, %38
  %.neg4 = sext i1 %39 to i32
  %40 = add i32 %34, %.neg4
  %41 = mul i32 %33, -1
  %42 = mul i32 %41, %40
  %43 = add i32 %.05, %42
  %44 = sitofp i32 %43 to float
  %45 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %46 = load i32, ptr %45, align 4
  %47 = sitofp i32 %46 to float
  %48 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %49 = load i32, ptr %48, align 4
  %50 = sitofp i32 %49 to float
  %51 = fmul reassoc ninf nsz float %44, %47
  %52 = fdiv reassoc ninf nsz float %51, %50
  %53 = sitofp i32 %40 to float
  %54 = getelementptr inbounds nuw i8, ptr %31, i64 16
  %55 = load i32, ptr %54, align 4
  %56 = sitofp i32 %55 to float
  %57 = getelementptr inbounds nuw i8, ptr %31, i64 20
  %58 = load i32, ptr %57, align 4
  %59 = sitofp i32 %58 to float
  %60 = fmul reassoc ninf nsz float %53, %56
  %61 = fdiv reassoc ninf nsz float %60, %59
  %62 = tail call reassoc ninf nsz float @llvm.floor.f32(float %52)
  %63 = fptosi float %62 to i32
  %64 = tail call reassoc ninf nsz float @llvm.floor.f32(float %61)
  %65 = fptosi float %64 to i32
  %66 = sitofp i32 %63 to float
  %67 = fsub reassoc ninf nsz float %52, %66
  %68 = sitofp i32 %65 to float
  %69 = fsub reassoc ninf nsz float %61, %68
  %70 = fadd reassoc ninf nsz float %67, 1.000000e+00
  %71 = fmul reassoc ninf nsz float %70, 7.500000e-01
  %72 = fsub reassoc ninf nsz float 3.750000e+00, %71
  %73 = fmul reassoc ninf nsz float %72, %70
  %74 = fadd reassoc ninf nsz float %73, -6.000000e+00
  %75 = fmul reassoc ninf nsz float %74, %70
  %76 = fadd reassoc ninf nsz float %75, 3.000000e+00
  %77 = fmul reassoc ninf nsz float %67, 1.250000e+00
  %78 = fadd reassoc ninf nsz float %77, -2.250000e+00
  %79 = fmul reassoc ninf nsz float %67, %67
  %80 = fmul reassoc ninf nsz float %79, %78
  %81 = fadd reassoc ninf nsz float %80, 1.000000e+00
  %82 = fsub reassoc ninf nsz float 1.000000e+00, %67
  %83 = fmul reassoc ninf nsz float %82, 1.250000e+00
  %84 = fadd reassoc ninf nsz float %83, -2.250000e+00
  %85 = fmul reassoc ninf nsz float %82, %82
  %86 = fmul reassoc ninf nsz float %85, %84
  %87 = fadd reassoc ninf nsz float %86, 1.000000e+00
  %88 = fsub reassoc ninf nsz float 2.000000e+00, %67
  %89 = fmul reassoc ninf nsz float %88, 7.500000e-01
  %90 = fsub reassoc ninf nsz float 3.750000e+00, %89
  %91 = fmul reassoc ninf nsz float %90, %88
  %92 = fadd reassoc ninf nsz float %91, -6.000000e+00
  %93 = fmul reassoc ninf nsz float %92, %88
  %94 = fadd reassoc ninf nsz float %93, 3.000000e+00
  %95 = fadd reassoc ninf nsz float %87, %81
  %96 = fadd reassoc ninf nsz float %95, %76
  %97 = fadd reassoc ninf nsz float %96, %94
  %98 = fdiv reassoc ninf nsz float %76, %97
  %99 = fdiv reassoc ninf nsz float %81, %97
  %100 = fdiv reassoc ninf nsz float %87, %97
  %101 = fdiv reassoc ninf nsz float %94, %97
  %102 = fadd reassoc ninf nsz float %69, 1.000000e+00
  %103 = fmul reassoc ninf nsz float %102, 7.500000e-01
  %104 = fsub reassoc ninf nsz float 3.750000e+00, %103
  %105 = fmul reassoc ninf nsz float %104, %102
  %106 = fadd reassoc ninf nsz float %105, -6.000000e+00
  %107 = fmul reassoc ninf nsz float %106, %102
  %108 = fadd reassoc ninf nsz float %107, 3.000000e+00
  %109 = fmul reassoc ninf nsz float %69, 1.250000e+00
  %110 = fadd reassoc ninf nsz float %109, -2.250000e+00
  %111 = fmul reassoc ninf nsz float %69, %69
  %112 = fmul reassoc ninf nsz float %111, %110
  %113 = fadd reassoc ninf nsz float %112, 1.000000e+00
  %114 = fsub reassoc ninf nsz float 1.000000e+00, %69
  %115 = fmul reassoc ninf nsz float %114, 1.250000e+00
  %116 = fadd reassoc ninf nsz float %115, -2.250000e+00
  %117 = fmul reassoc ninf nsz float %114, %114
  %118 = fmul reassoc ninf nsz float %117, %116
  %119 = fadd reassoc ninf nsz float %118, 1.000000e+00
  %120 = fsub reassoc ninf nsz float 2.000000e+00, %69
  %121 = fmul reassoc ninf nsz float %120, 7.500000e-01
  %122 = fsub reassoc ninf nsz float 3.750000e+00, %121
  %123 = fmul reassoc ninf nsz float %122, %120
  %124 = fadd reassoc ninf nsz float %123, -6.000000e+00
  %125 = fmul reassoc ninf nsz float %124, %120
  %126 = fadd reassoc ninf nsz float %125, 3.000000e+00
  %127 = fadd reassoc ninf nsz float %119, %113
  %128 = fadd reassoc ninf nsz float %127, %108
  %129 = fadd reassoc ninf nsz float %128, %126
  %130 = fdiv reassoc ninf nsz float %108, %129
  %131 = fdiv reassoc ninf nsz float %113, %129
  %132 = fdiv reassoc ninf nsz float %119, %129
  %133 = fdiv reassoc ninf nsz float %126, %129
  %134 = add i32 %65, -1
  %135 = tail call i32 @llvm.abs.i32(i32 %134, i1 true)
  %136 = add i32 %55, -1
  %137 = sub i32 %135, %136
  %138 = tail call i32 @llvm.smax.i32(i32 %137, i32 0)
  %139 = shl nuw i32 %138, 1
  %140 = sub i32 %135, %139
  %141 = tail call i32 @llvm.smax.i32(i32 %140, i32 0)
  %142 = tail call i32 @llvm.smin.i32(i32 %136, i32 %141)
  %143 = add i32 %63, -1
  %144 = tail call i32 @llvm.abs.i32(i32 %143, i1 true)
  %145 = add i32 %46, -1
  %146 = sub i32 %144, %145
  %147 = tail call i32 @llvm.smax.i32(i32 %146, i32 0)
  %148 = shl nuw i32 %147, 1
  %149 = sub i32 %144, %148
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = tail call i32 @llvm.smin.i32(i32 %145, i32 %150)
  %152 = load ptr, ptr %23, align 8
  %153 = load i32, ptr %24, align 4
  %154 = load i32, ptr %25, align 4
  %155 = mul i32 %142, %153
  %156 = add i32 %151, %155
  %157 = mul i32 %156, %154
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %152, i64 %158
  %160 = load float, ptr %159, align 4
  %161 = fmul reassoc ninf nsz float %98, %160
  %162 = tail call i32 @llvm.abs.i32(i32 %63, i1 true)
  %163 = sub i32 %162, %145
  %164 = tail call i32 @llvm.smax.i32(i32 %163, i32 0)
  %165 = shl nuw i32 %164, 1
  %166 = sub i32 %162, %165
  %167 = tail call i32 @llvm.smax.i32(i32 %166, i32 0)
  %168 = tail call i32 @llvm.smin.i32(i32 %145, i32 %167)
  %169 = add i32 %155, %168
  %170 = mul i32 %169, %154
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %152, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = fmul reassoc ninf nsz float %99, %173
  %175 = fadd reassoc ninf nsz float %161, %174
  %176 = add i32 %63, 1
  %177 = tail call i32 @llvm.abs.i32(i32 %176, i1 true)
  %178 = sub i32 %177, %145
  %179 = tail call i32 @llvm.smax.i32(i32 %178, i32 0)
  %180 = shl nuw i32 %179, 1
  %181 = sub i32 %177, %180
  %182 = tail call i32 @llvm.smax.i32(i32 %181, i32 0)
  %183 = tail call i32 @llvm.smin.i32(i32 %145, i32 %182)
  %184 = add i32 %183, %155
  %185 = mul i32 %184, %154
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %152, i64 %186
  %188 = load float, ptr %187, align 4
  %189 = fmul reassoc ninf nsz float %100, %188
  %190 = fadd reassoc ninf nsz float %175, %189
  %191 = add i32 %63, 2
  %192 = tail call i32 @llvm.abs.i32(i32 %191, i1 true)
  %193 = sub i32 %192, %145
  %194 = tail call i32 @llvm.smax.i32(i32 %193, i32 0)
  %195 = shl nuw i32 %194, 1
  %196 = sub i32 %192, %195
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = tail call i32 @llvm.smin.i32(i32 %145, i32 %197)
  %199 = add i32 %198, %155
  %200 = mul i32 %199, %154
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, ptr %152, i64 %201
  %203 = load float, ptr %202, align 4
  %204 = fmul reassoc ninf nsz float %101, %203
  %205 = fadd reassoc ninf nsz float %190, %204
  %206 = fmul reassoc ninf nsz float %205, %130
  %207 = tail call i32 @llvm.abs.i32(i32 %65, i1 true)
  %208 = sub i32 %207, %136
  %209 = tail call i32 @llvm.smax.i32(i32 %208, i32 0)
  %210 = shl nuw i32 %209, 1
  %211 = sub i32 %207, %210
  %212 = tail call i32 @llvm.smax.i32(i32 %211, i32 0)
  %213 = tail call i32 @llvm.smin.i32(i32 %136, i32 %212)
  %214 = mul i32 %213, %153
  %215 = add i32 %151, %214
  %216 = mul i32 %215, %154
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, ptr %152, i64 %217
  %219 = load float, ptr %218, align 4
  %220 = fmul reassoc ninf nsz float %98, %219
  %221 = add i32 %168, %214
  %222 = mul i32 %221, %154
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %152, i64 %223
  %225 = load float, ptr %224, align 4
  %226 = fmul reassoc ninf nsz float %99, %225
  %227 = fadd reassoc ninf nsz float %220, %226
  %228 = add i32 %183, %214
  %229 = mul i32 %228, %154
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, ptr %152, i64 %230
  %232 = load float, ptr %231, align 4
  %233 = fmul reassoc ninf nsz float %100, %232
  %234 = fadd reassoc ninf nsz float %227, %233
  %235 = add i32 %198, %214
  %236 = mul i32 %235, %154
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, ptr %152, i64 %237
  %239 = load float, ptr %238, align 4
  %240 = fmul reassoc ninf nsz float %101, %239
  %241 = fadd reassoc ninf nsz float %234, %240
  %242 = fmul reassoc ninf nsz float %241, %131
  %243 = fadd reassoc ninf nsz float %206, %242
  %244 = add i32 %65, 1
  %245 = tail call i32 @llvm.abs.i32(i32 %244, i1 true)
  %246 = sub i32 %245, %136
  %247 = tail call i32 @llvm.smax.i32(i32 %246, i32 0)
  %248 = shl nuw i32 %247, 1
  %249 = sub i32 %245, %248
  %250 = tail call i32 @llvm.smax.i32(i32 %249, i32 0)
  %251 = tail call i32 @llvm.smin.i32(i32 %136, i32 %250)
  %252 = mul i32 %251, %153
  %253 = add i32 %151, %252
  %254 = mul i32 %253, %154
  %255 = sext i32 %254 to i64
  %256 = getelementptr float, ptr %152, i64 %255
  %257 = load float, ptr %256, align 4
  %258 = fmul reassoc ninf nsz float %98, %257
  %259 = add i32 %252, %168
  %260 = mul i32 %259, %154
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, ptr %152, i64 %261
  %263 = load float, ptr %262, align 4
  %264 = fmul reassoc ninf nsz float %99, %263
  %265 = fadd reassoc ninf nsz float %258, %264
  %266 = add i32 %183, %252
  %267 = mul i32 %266, %154
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, ptr %152, i64 %268
  %270 = load float, ptr %269, align 4
  %271 = fmul reassoc ninf nsz float %100, %270
  %272 = fadd reassoc ninf nsz float %265, %271
  %273 = add i32 %198, %252
  %274 = mul i32 %273, %154
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, ptr %152, i64 %275
  %277 = load float, ptr %276, align 4
  %278 = fmul reassoc ninf nsz float %101, %277
  %279 = fadd reassoc ninf nsz float %272, %278
  %280 = fmul reassoc ninf nsz float %279, %132
  %281 = fadd reassoc ninf nsz float %243, %280
  %282 = add i32 %65, 2
  %283 = tail call i32 @llvm.abs.i32(i32 %282, i1 true)
  %284 = sub i32 %283, %136
  %285 = tail call i32 @llvm.smax.i32(i32 %284, i32 0)
  %286 = shl nuw i32 %285, 1
  %287 = sub i32 %283, %286
  %288 = tail call i32 @llvm.smax.i32(i32 %287, i32 0)
  %289 = tail call i32 @llvm.smin.i32(i32 %136, i32 %288)
  %290 = mul i32 %289, %153
  %291 = add i32 %151, %290
  %292 = mul i32 %291, %154
  %293 = sext i32 %292 to i64
  %294 = getelementptr float, ptr %152, i64 %293
  %295 = load float, ptr %294, align 4
  %296 = fmul reassoc ninf nsz float %98, %295
  %297 = add i32 %290, %168
  %298 = mul i32 %297, %154
  %299 = sext i32 %298 to i64
  %300 = getelementptr float, ptr %152, i64 %299
  %301 = load float, ptr %300, align 4
  %302 = fmul reassoc ninf nsz float %99, %301
  %303 = fadd reassoc ninf nsz float %296, %302
  %304 = add i32 %183, %290
  %305 = mul i32 %304, %154
  %306 = sext i32 %305 to i64
  %307 = getelementptr float, ptr %152, i64 %306
  %308 = load float, ptr %307, align 4
  %309 = fmul reassoc ninf nsz float %100, %308
  %310 = fadd reassoc ninf nsz float %303, %309
  %311 = add i32 %198, %290
  %312 = mul i32 %311, %154
  %313 = sext i32 %312 to i64
  %314 = getelementptr float, ptr %152, i64 %313
  %315 = load float, ptr %314, align 4
  %316 = fmul reassoc ninf nsz float %101, %315
  %317 = fadd reassoc ninf nsz float %310, %316
  %318 = fmul reassoc ninf nsz float %317, %133
  %319 = fadd reassoc ninf nsz float %281, %318
  %320 = add i32 %157, 1
  %321 = sext i32 %320 to i64
  %322 = getelementptr float, ptr %152, i64 %321
  %323 = load float, ptr %322, align 4
  %324 = fmul reassoc ninf nsz float %98, %323
  %325 = add i32 %170, 1
  %326 = sext i32 %325 to i64
  %327 = getelementptr float, ptr %152, i64 %326
  %328 = load float, ptr %327, align 4
  %329 = fmul reassoc ninf nsz float %328, %99
  %330 = fadd reassoc ninf nsz float %324, %329
  %331 = add i32 %185, 1
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, ptr %152, i64 %332
  %334 = load float, ptr %333, align 4
  %335 = fmul reassoc ninf nsz float %334, %100
  %336 = fadd reassoc ninf nsz float %330, %335
  %337 = add i32 %200, 1
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, ptr %152, i64 %338
  %340 = load float, ptr %339, align 4
  %341 = fmul reassoc ninf nsz float %340, %101
  %342 = fadd reassoc ninf nsz float %336, %341
  %343 = fmul reassoc ninf nsz float %342, %130
  %344 = add i32 %216, 1
  %345 = sext i32 %344 to i64
  %346 = getelementptr float, ptr %152, i64 %345
  %347 = load float, ptr %346, align 4
  %348 = fmul reassoc ninf nsz float %347, %98
  %349 = add i32 %222, 1
  %350 = sext i32 %349 to i64
  %351 = getelementptr float, ptr %152, i64 %350
  %352 = load float, ptr %351, align 4
  %353 = fmul reassoc ninf nsz float %352, %99
  %354 = fadd reassoc ninf nsz float %353, %348
  %355 = add i32 %229, 1
  %356 = sext i32 %355 to i64
  %357 = getelementptr float, ptr %152, i64 %356
  %358 = load float, ptr %357, align 4
  %359 = fmul reassoc ninf nsz float %358, %100
  %360 = fadd reassoc ninf nsz float %354, %359
  %361 = add i32 %236, 1
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, ptr %152, i64 %362
  %364 = load float, ptr %363, align 4
  %365 = fmul reassoc ninf nsz float %364, %101
  %366 = fadd reassoc ninf nsz float %360, %365
  %367 = fmul reassoc ninf nsz float %366, %131
  %368 = fadd reassoc ninf nsz float %367, %343
  %369 = add i32 %254, 1
  %370 = sext i32 %369 to i64
  %371 = getelementptr float, ptr %152, i64 %370
  %372 = load float, ptr %371, align 4
  %373 = fmul reassoc ninf nsz float %372, %98
  %374 = add i32 %260, 1
  %375 = sext i32 %374 to i64
  %376 = getelementptr float, ptr %152, i64 %375
  %377 = load float, ptr %376, align 4
  %378 = fmul reassoc ninf nsz float %377, %99
  %379 = fadd reassoc ninf nsz float %378, %373
  %380 = add i32 %267, 1
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, ptr %152, i64 %381
  %383 = load float, ptr %382, align 4
  %384 = fmul reassoc ninf nsz float %383, %100
  %385 = fadd reassoc ninf nsz float %379, %384
  %386 = add i32 %274, 1
  %387 = sext i32 %386 to i64
  %388 = getelementptr float, ptr %152, i64 %387
  %389 = load float, ptr %388, align 4
  %390 = fmul reassoc ninf nsz float %389, %101
  %391 = fadd reassoc ninf nsz float %385, %390
  %392 = fmul reassoc ninf nsz float %391, %132
  %393 = fadd reassoc ninf nsz float %368, %392
  %394 = add i32 %292, 1
  %395 = sext i32 %394 to i64
  %396 = getelementptr float, ptr %152, i64 %395
  %397 = load float, ptr %396, align 4
  %398 = fmul reassoc ninf nsz float %397, %98
  %399 = add i32 %298, 1
  %400 = sext i32 %399 to i64
  %401 = getelementptr float, ptr %152, i64 %400
  %402 = load float, ptr %401, align 4
  %403 = fmul reassoc ninf nsz float %402, %99
  %404 = fadd reassoc ninf nsz float %403, %398
  %405 = add i32 %305, 1
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, ptr %152, i64 %406
  %408 = load float, ptr %407, align 4
  %409 = fmul reassoc ninf nsz float %408, %100
  %410 = fadd reassoc ninf nsz float %404, %409
  %411 = add i32 %312, 1
  %412 = sext i32 %411 to i64
  %413 = getelementptr float, ptr %152, i64 %412
  %414 = load float, ptr %413, align 4
  %415 = fmul reassoc ninf nsz float %414, %101
  %416 = fadd reassoc ninf nsz float %410, %415
  %417 = fmul reassoc ninf nsz float %416, %133
  %418 = fadd reassoc ninf nsz float %393, %417
  %419 = fmul reassoc ninf nsz float %319, %21
  %420 = load ptr, ptr %26, align 8
  %421 = load i32, ptr %27, align 4
  %422 = load i32, ptr %28, align 4
  %423 = sub i32 %421, %33
  %424 = mul i32 %423, %40
  %425 = add i32 %.05, %424
  %426 = mul i32 %425, %422
  %427 = sext i32 %426 to i64
  %428 = getelementptr float, ptr %420, i64 %427
  store float %419, ptr %428, align 4
  %429 = fmul reassoc ninf nsz float %418, %21
  %430 = load ptr, ptr %26, align 8
  %431 = load i32, ptr %27, align 4
  %432 = load i32, ptr %28, align 4
  %433 = sub i32 %431, %33
  %434 = mul i32 %433, %40
  %435 = add i32 %.05, %434
  %436 = mul i32 %435, %432
  %437 = add i32 %436, 1
  %438 = sext i32 %437 to i64
  %439 = getelementptr float, ptr %430, i64 %438
  store float %429, ptr %439, align 4
  %440 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %18, %440
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #5

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
