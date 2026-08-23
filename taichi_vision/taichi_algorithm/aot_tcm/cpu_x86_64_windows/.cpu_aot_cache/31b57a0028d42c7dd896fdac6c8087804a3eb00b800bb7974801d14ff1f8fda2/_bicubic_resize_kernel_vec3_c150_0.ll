; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bicubic_resize_kernel_vec3_c150_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 40
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 44
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

define void @_bicubic_resize_kernel_vec3_c150_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 32
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 36
  %23 = load i32, ptr %22, align 4
  %24 = sitofp i32 %21 to float
  %25 = sitofp i32 %23 to float
  %26 = add i32 %21, -1
  %27 = add i32 %23, -1
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr i8, ptr %19, i64 8
  %30 = getelementptr i8, ptr %19, i64 4
  %31 = getelementptr i8, ptr %19, i64 24
  %32 = getelementptr i8, ptr %19, i64 20
  %33 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %33, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.011 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %494, %for_loop_body ]
  %34 = load ptr, ptr %3, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 4
  %38 = load i32, ptr %37, align 4
  %39 = sdiv i32 %.011, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.011
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.011, %40
  %44 = and i1 %42, %43
  %.neg4 = sext i1 %44 to i32
  %45 = add i32 %39, %.neg4
  %46 = mul i32 %38, -1
  %47 = mul i32 %46, %45
  %48 = add i32 %.011, %47
  %49 = sitofp i32 %45 to float
  %50 = fadd reassoc ninf nsz float %49, 5.000000e-01
  %51 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %52 = load i32, ptr %51, align 4
  %53 = sitofp i32 %52 to float
  %54 = fmul reassoc ninf nsz float %50, %24
  %55 = fdiv reassoc ninf nsz float %54, %53
  %56 = fadd reassoc ninf nsz float %55, -5.000000e-01
  %57 = sitofp i32 %48 to float
  %58 = fadd reassoc ninf nsz float %57, 5.000000e-01
  %59 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %60 = load i32, ptr %59, align 4
  %61 = sitofp i32 %60 to float
  %62 = fmul reassoc ninf nsz float %58, %25
  %63 = fdiv reassoc ninf nsz float %62, %61
  %64 = fadd reassoc ninf nsz float %63, -5.000000e-01
  %65 = tail call reassoc ninf nsz float @llvm.floor.f32(float %64)
  %66 = fptosi float %65 to i32
  %67 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %68 = fptosi float %67 to i32
  %69 = sitofp i32 %66 to float
  %70 = fsub reassoc ninf nsz float %64, %69
  %71 = sitofp i32 %68 to float
  %72 = fsub reassoc ninf nsz float %56, %71
  %73 = tail call noundef float @llvm.fabs.f32(float %70)
  %74 = fadd reassoc ninf nsz float %73, 1.000000e+00
  %75 = fmul reassoc ninf nsz float %74, %74
  %76 = fmul reassoc ninf nsz float %74, 7.500000e-01
  %77 = fmul reassoc ninf nsz float %74, -6.000000e+00
  %78 = fsub reassoc ninf nsz float 3.750000e+00, %76
  %reass.mul = fmul reassoc ninf nsz float %75, %78
  %79 = fadd reassoc ninf nsz float %77, 3.000000e+00
  %80 = fadd reassoc ninf nsz float %79, %reass.mul
  %81 = fmul reassoc ninf nsz float %70, %70
  %82 = fmul reassoc ninf nsz float %81, 1.250000e+00
  %83 = fmul reassoc ninf nsz float %82, %73
  %84 = fmul reassoc ninf nsz float %81, 2.250000e+00
  %85 = fsub reassoc ninf nsz float %83, %84
  %86 = fadd reassoc ninf nsz float %85, 1.000000e+00
  %87 = fsub reassoc ninf nsz float 1.000000e+00, %73
  %88 = fmul reassoc ninf nsz float %87, %87
  %89 = fmul reassoc ninf nsz float %87, 1.250000e+00
  %90 = fadd reassoc ninf nsz float %89, -2.250000e+00
  %91 = fmul reassoc ninf nsz float %90, %88
  %92 = fadd reassoc ninf nsz float %91, 1.000000e+00
  %93 = fsub reassoc ninf nsz float 2.000000e+00, %73
  %94 = fmul reassoc ninf nsz float %93, %93
  %95 = fmul reassoc ninf nsz float %93, 7.500000e-01
  %96 = fmul reassoc ninf nsz float %93, -6.000000e+00
  %97 = fsub reassoc ninf nsz float 3.750000e+00, %95
  %reass.mul6 = fmul reassoc ninf nsz float %94, %97
  %98 = fadd reassoc ninf nsz float %96, 3.000000e+00
  %99 = fadd reassoc ninf nsz float %98, %reass.mul6
  %100 = tail call noundef float @llvm.fabs.f32(float %72)
  %101 = fadd reassoc ninf nsz float %100, 1.000000e+00
  %102 = fmul reassoc ninf nsz float %101, %101
  %103 = fmul reassoc ninf nsz float %101, 7.500000e-01
  %104 = fmul reassoc ninf nsz float %101, -6.000000e+00
  %105 = fsub reassoc ninf nsz float 3.750000e+00, %103
  %reass.mul8 = fmul reassoc ninf nsz float %102, %105
  %106 = fadd reassoc ninf nsz float %104, 3.000000e+00
  %107 = fadd reassoc ninf nsz float %106, %reass.mul8
  %108 = fmul reassoc ninf nsz float %72, %72
  %109 = fmul reassoc ninf nsz float %108, 1.250000e+00
  %110 = fmul reassoc ninf nsz float %109, %100
  %111 = fmul reassoc ninf nsz float %108, 2.250000e+00
  %112 = fsub reassoc ninf nsz float %110, %111
  %113 = fadd reassoc ninf nsz float %112, 1.000000e+00
  %114 = fsub reassoc ninf nsz float 1.000000e+00, %100
  %115 = fmul reassoc ninf nsz float %114, %114
  %116 = fmul reassoc ninf nsz float %114, 1.250000e+00
  %117 = fadd reassoc ninf nsz float %116, -2.250000e+00
  %118 = fmul reassoc ninf nsz float %117, %115
  %119 = fadd reassoc ninf nsz float %118, 1.000000e+00
  %120 = fsub reassoc ninf nsz float 2.000000e+00, %100
  %121 = fmul reassoc ninf nsz float %120, %120
  %122 = fmul reassoc ninf nsz float %120, 7.500000e-01
  %123 = fmul reassoc ninf nsz float %120, -6.000000e+00
  %124 = fsub reassoc ninf nsz float 3.750000e+00, %122
  %reass.mul10 = fmul reassoc ninf nsz float %121, %124
  %125 = fadd reassoc ninf nsz float %123, 3.000000e+00
  %126 = fadd reassoc ninf nsz float %125, %reass.mul10
  %127 = add i32 %68, -1
  %128 = tail call i32 @llvm.smax.i32(i32 %127, i32 0)
  %129 = tail call i32 @llvm.smin.i32(i32 %26, i32 %128)
  %130 = add i32 %66, -1
  %131 = tail call i32 @llvm.smax.i32(i32 %130, i32 0)
  %132 = tail call i32 @llvm.smin.i32(i32 %27, i32 %131)
  %133 = load ptr, ptr %29, align 8
  %134 = load i32, ptr %30, align 4
  %135 = mul i32 %129, %134
  %136 = add i32 %132, %135
  %137 = mul i32 %136, 3
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %133, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = add i32 %137, 1
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %133, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = add i32 %137, 2
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, ptr %133, i64 %146
  %148 = load float, ptr %147, align 4
  %149 = fmul reassoc ninf nsz float %80, %140
  %150 = fmul reassoc ninf nsz float %80, %144
  %151 = fmul reassoc ninf nsz float %80, %148
  %152 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %153 = tail call i32 @llvm.smin.i32(i32 %27, i32 %152)
  %154 = add i32 %135, %153
  %155 = mul i32 %154, 3
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %133, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = add i32 %155, 1
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %133, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = add i32 %155, 2
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %133, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = fmul reassoc ninf nsz float %86, %158
  %168 = fmul reassoc ninf nsz float %86, %162
  %169 = fmul reassoc ninf nsz float %86, %166
  %170 = add i32 %66, 1
  %171 = tail call i32 @llvm.smax.i32(i32 %170, i32 0)
  %172 = tail call i32 @llvm.smin.i32(i32 %27, i32 %171)
  %173 = add i32 %172, %135
  %174 = mul i32 %173, 3
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %133, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = add i32 %174, 1
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, ptr %133, i64 %179
  %181 = load float, ptr %180, align 4
  %182 = add i32 %174, 2
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %133, i64 %183
  %185 = load float, ptr %184, align 4
  %186 = fmul reassoc ninf nsz float %92, %177
  %187 = fmul reassoc ninf nsz float %92, %181
  %188 = fmul reassoc ninf nsz float %92, %185
  %189 = add i32 %66, 2
  %190 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %191 = tail call i32 @llvm.smin.i32(i32 %27, i32 %190)
  %192 = add i32 %191, %135
  %193 = mul i32 %192, 3
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, ptr %133, i64 %194
  %196 = load float, ptr %195, align 4
  %197 = add i32 %193, 1
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %133, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = add i32 %193, 2
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %133, i64 %202
  %204 = load float, ptr %203, align 4
  %205 = fmul reassoc ninf nsz float %99, %196
  %206 = fmul reassoc ninf nsz float %99, %200
  %207 = fmul reassoc ninf nsz float %99, %204
  %208 = fadd reassoc ninf nsz float %186, %167
  %209 = fadd reassoc ninf nsz float %208, %149
  %210 = fadd reassoc ninf nsz float %209, %205
  %211 = fadd reassoc ninf nsz float %187, %168
  %212 = fadd reassoc ninf nsz float %211, %150
  %213 = fadd reassoc ninf nsz float %212, %206
  %214 = fadd reassoc ninf nsz float %188, %169
  %215 = fadd reassoc ninf nsz float %214, %151
  %216 = fadd reassoc ninf nsz float %215, %207
  %217 = fmul reassoc ninf nsz float %210, %107
  %218 = fmul reassoc ninf nsz float %213, %107
  %219 = fmul reassoc ninf nsz float %216, %107
  %220 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %221 = tail call i32 @llvm.smin.i32(i32 %26, i32 %220)
  %222 = mul i32 %221, %134
  %223 = add i32 %132, %222
  %224 = mul i32 %223, 3
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, ptr %133, i64 %225
  %227 = load float, ptr %226, align 4
  %228 = add i32 %224, 1
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, ptr %133, i64 %229
  %231 = load float, ptr %230, align 4
  %232 = add i32 %224, 2
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %133, i64 %233
  %235 = load float, ptr %234, align 4
  %236 = fmul reassoc ninf nsz float %80, %227
  %237 = fmul reassoc ninf nsz float %80, %231
  %238 = fmul reassoc ninf nsz float %80, %235
  %239 = add i32 %153, %222
  %240 = mul i32 %239, 3
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %133, i64 %241
  %243 = load float, ptr %242, align 4
  %244 = add i32 %240, 1
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, ptr %133, i64 %245
  %247 = load float, ptr %246, align 4
  %248 = add i32 %240, 2
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, ptr %133, i64 %249
  %251 = load float, ptr %250, align 4
  %252 = fmul reassoc ninf nsz float %86, %243
  %253 = fmul reassoc ninf nsz float %247, %86
  %254 = fmul reassoc ninf nsz float %251, %86
  %255 = fadd reassoc ninf nsz float %236, %252
  %256 = fadd reassoc ninf nsz float %237, %253
  %257 = fadd reassoc ninf nsz float %238, %254
  %258 = add i32 %172, %222
  %259 = mul i32 %258, 3
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, ptr %133, i64 %260
  %262 = load float, ptr %261, align 4
  %263 = add i32 %259, 1
  %264 = sext i32 %263 to i64
  %265 = getelementptr float, ptr %133, i64 %264
  %266 = load float, ptr %265, align 4
  %267 = add i32 %259, 2
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, ptr %133, i64 %268
  %270 = load float, ptr %269, align 4
  %271 = fmul reassoc ninf nsz float %262, %92
  %272 = fmul reassoc ninf nsz float %266, %92
  %273 = fmul reassoc ninf nsz float %270, %92
  %274 = fadd reassoc ninf nsz float %255, %271
  %275 = fadd reassoc ninf nsz float %256, %272
  %276 = fadd reassoc ninf nsz float %257, %273
  %277 = add i32 %191, %222
  %278 = mul i32 %277, 3
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, ptr %133, i64 %279
  %281 = load float, ptr %280, align 4
  %282 = add i32 %278, 1
  %283 = sext i32 %282 to i64
  %284 = getelementptr float, ptr %133, i64 %283
  %285 = load float, ptr %284, align 4
  %286 = add i32 %278, 2
  %287 = sext i32 %286 to i64
  %288 = getelementptr float, ptr %133, i64 %287
  %289 = load float, ptr %288, align 4
  %290 = fmul reassoc ninf nsz float %281, %99
  %291 = fmul reassoc ninf nsz float %285, %99
  %292 = fmul reassoc ninf nsz float %289, %99
  %293 = fadd reassoc ninf nsz float %274, %290
  %294 = fadd reassoc ninf nsz float %275, %291
  %295 = fadd reassoc ninf nsz float %276, %292
  %296 = fmul reassoc ninf nsz float %293, %113
  %297 = fmul reassoc ninf nsz float %294, %113
  %298 = fmul reassoc ninf nsz float %295, %113
  %299 = fadd reassoc ninf nsz float %296, %217
  %300 = fadd reassoc ninf nsz float %297, %218
  %301 = fadd reassoc ninf nsz float %298, %219
  %302 = add i32 %68, 1
  %303 = tail call i32 @llvm.smax.i32(i32 %302, i32 0)
  %304 = tail call i32 @llvm.smin.i32(i32 %26, i32 %303)
  %305 = mul i32 %304, %134
  %306 = add i32 %132, %305
  %307 = mul i32 %306, 3
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, ptr %133, i64 %308
  %310 = load float, ptr %309, align 4
  %311 = add i32 %307, 1
  %312 = sext i32 %311 to i64
  %313 = getelementptr float, ptr %133, i64 %312
  %314 = load float, ptr %313, align 4
  %315 = add i32 %307, 2
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, ptr %133, i64 %316
  %318 = load float, ptr %317, align 4
  %319 = fmul reassoc ninf nsz float %310, %80
  %320 = fmul reassoc ninf nsz float %314, %80
  %321 = fmul reassoc ninf nsz float %318, %80
  %322 = add i32 %305, %153
  %323 = mul i32 %322, 3
  %324 = sext i32 %323 to i64
  %325 = getelementptr float, ptr %133, i64 %324
  %326 = load float, ptr %325, align 4
  %327 = add i32 %323, 1
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, ptr %133, i64 %328
  %330 = load float, ptr %329, align 4
  %331 = add i32 %323, 2
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, ptr %133, i64 %332
  %334 = load float, ptr %333, align 4
  %335 = fmul reassoc ninf nsz float %326, %86
  %336 = fmul reassoc ninf nsz float %330, %86
  %337 = fmul reassoc ninf nsz float %334, %86
  %338 = fadd reassoc ninf nsz float %335, %319
  %339 = fadd reassoc ninf nsz float %336, %320
  %340 = fadd reassoc ninf nsz float %337, %321
  %341 = add i32 %172, %305
  %342 = mul i32 %341, 3
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, ptr %133, i64 %343
  %345 = load float, ptr %344, align 4
  %346 = add i32 %342, 1
  %347 = sext i32 %346 to i64
  %348 = getelementptr float, ptr %133, i64 %347
  %349 = load float, ptr %348, align 4
  %350 = add i32 %342, 2
  %351 = sext i32 %350 to i64
  %352 = getelementptr float, ptr %133, i64 %351
  %353 = load float, ptr %352, align 4
  %354 = fmul reassoc ninf nsz float %345, %92
  %355 = fmul reassoc ninf nsz float %349, %92
  %356 = fmul reassoc ninf nsz float %353, %92
  %357 = fadd reassoc ninf nsz float %338, %354
  %358 = fadd reassoc ninf nsz float %339, %355
  %359 = fadd reassoc ninf nsz float %340, %356
  %360 = add i32 %191, %305
  %361 = mul i32 %360, 3
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, ptr %133, i64 %362
  %364 = load float, ptr %363, align 4
  %365 = add i32 %361, 1
  %366 = sext i32 %365 to i64
  %367 = getelementptr float, ptr %133, i64 %366
  %368 = load float, ptr %367, align 4
  %369 = add i32 %361, 2
  %370 = sext i32 %369 to i64
  %371 = getelementptr float, ptr %133, i64 %370
  %372 = load float, ptr %371, align 4
  %373 = fmul reassoc ninf nsz float %364, %99
  %374 = fmul reassoc ninf nsz float %368, %99
  %375 = fmul reassoc ninf nsz float %372, %99
  %376 = fadd reassoc ninf nsz float %357, %373
  %377 = fadd reassoc ninf nsz float %358, %374
  %378 = fadd reassoc ninf nsz float %359, %375
  %379 = fmul reassoc ninf nsz float %376, %119
  %380 = fmul reassoc ninf nsz float %377, %119
  %381 = fmul reassoc ninf nsz float %378, %119
  %382 = fadd reassoc ninf nsz float %299, %379
  %383 = fadd reassoc ninf nsz float %300, %380
  %384 = fadd reassoc ninf nsz float %301, %381
  %385 = add i32 %68, 2
  %386 = tail call i32 @llvm.smax.i32(i32 %385, i32 0)
  %387 = tail call i32 @llvm.smin.i32(i32 %26, i32 %386)
  %388 = mul i32 %387, %134
  %389 = add i32 %132, %388
  %390 = mul i32 %389, 3
  %391 = sext i32 %390 to i64
  %392 = getelementptr float, ptr %133, i64 %391
  %393 = load float, ptr %392, align 4
  %394 = add i32 %390, 1
  %395 = sext i32 %394 to i64
  %396 = getelementptr float, ptr %133, i64 %395
  %397 = load float, ptr %396, align 4
  %398 = add i32 %390, 2
  %399 = sext i32 %398 to i64
  %400 = getelementptr float, ptr %133, i64 %399
  %401 = load float, ptr %400, align 4
  %402 = fmul reassoc ninf nsz float %393, %80
  %403 = fmul reassoc ninf nsz float %397, %80
  %404 = fmul reassoc ninf nsz float %401, %80
  %405 = add i32 %388, %153
  %406 = mul i32 %405, 3
  %407 = sext i32 %406 to i64
  %408 = getelementptr float, ptr %133, i64 %407
  %409 = load float, ptr %408, align 4
  %410 = add i32 %406, 1
  %411 = sext i32 %410 to i64
  %412 = getelementptr float, ptr %133, i64 %411
  %413 = load float, ptr %412, align 4
  %414 = add i32 %406, 2
  %415 = sext i32 %414 to i64
  %416 = getelementptr float, ptr %133, i64 %415
  %417 = load float, ptr %416, align 4
  %418 = fmul reassoc ninf nsz float %409, %86
  %419 = fmul reassoc ninf nsz float %413, %86
  %420 = fmul reassoc ninf nsz float %417, %86
  %421 = fadd reassoc ninf nsz float %418, %402
  %422 = fadd reassoc ninf nsz float %419, %403
  %423 = fadd reassoc ninf nsz float %420, %404
  %424 = add i32 %172, %388
  %425 = mul i32 %424, 3
  %426 = sext i32 %425 to i64
  %427 = getelementptr float, ptr %133, i64 %426
  %428 = load float, ptr %427, align 4
  %429 = add i32 %425, 1
  %430 = sext i32 %429 to i64
  %431 = getelementptr float, ptr %133, i64 %430
  %432 = load float, ptr %431, align 4
  %433 = add i32 %425, 2
  %434 = sext i32 %433 to i64
  %435 = getelementptr float, ptr %133, i64 %434
  %436 = load float, ptr %435, align 4
  %437 = fmul reassoc ninf nsz float %428, %92
  %438 = fmul reassoc ninf nsz float %432, %92
  %439 = fmul reassoc ninf nsz float %436, %92
  %440 = fadd reassoc ninf nsz float %421, %437
  %441 = fadd reassoc ninf nsz float %422, %438
  %442 = fadd reassoc ninf nsz float %423, %439
  %443 = add i32 %191, %388
  %444 = mul i32 %443, 3
  %445 = sext i32 %444 to i64
  %446 = getelementptr float, ptr %133, i64 %445
  %447 = load float, ptr %446, align 4
  %448 = add i32 %444, 1
  %449 = sext i32 %448 to i64
  %450 = getelementptr float, ptr %133, i64 %449
  %451 = load float, ptr %450, align 4
  %452 = add i32 %444, 2
  %453 = sext i32 %452 to i64
  %454 = getelementptr float, ptr %133, i64 %453
  %455 = load float, ptr %454, align 4
  %456 = fmul reassoc ninf nsz float %447, %99
  %457 = fmul reassoc ninf nsz float %451, %99
  %458 = fmul reassoc ninf nsz float %455, %99
  %459 = fadd reassoc ninf nsz float %440, %456
  %460 = fadd reassoc ninf nsz float %441, %457
  %461 = fadd reassoc ninf nsz float %442, %458
  %462 = fmul reassoc ninf nsz float %459, %126
  %463 = fmul reassoc ninf nsz float %460, %126
  %464 = fmul reassoc ninf nsz float %461, %126
  %465 = fadd reassoc ninf nsz float %382, %462
  %466 = fadd reassoc ninf nsz float %383, %463
  %467 = fadd reassoc ninf nsz float %384, %464
  %468 = load ptr, ptr %31, align 8
  %469 = load i32, ptr %32, align 4
  %470 = sub i32 %469, %38
  %471 = mul i32 %470, 3
  %472 = mul i32 %471, %45
  %473 = add i32 %lsr.iv, %472
  %474 = sext i32 %473 to i64
  %475 = getelementptr float, ptr %468, i64 %474
  store float %465, ptr %475, align 4
  %476 = load ptr, ptr %31, align 8
  %477 = load i32, ptr %32, align 4
  %478 = sub i32 %477, %38
  %479 = mul i32 %478, 3
  %480 = mul i32 %479, %45
  %481 = add i32 %lsr.iv, %480
  %482 = add i32 %481, 1
  %483 = sext i32 %482 to i64
  %484 = getelementptr float, ptr %476, i64 %483
  store float %466, ptr %484, align 4
  %485 = load ptr, ptr %31, align 8
  %486 = load i32, ptr %32, align 4
  %487 = sub i32 %486, %38
  %488 = mul i32 %487, 3
  %489 = mul i32 %488, %45
  %490 = add i32 %lsr.iv, %489
  %491 = add i32 %490, 2
  %492 = sext i32 %491 to i64
  %493 = getelementptr float, ptr %485, i64 %492
  store float %467, ptr %493, align 4
  %494 = add nsw i32 %.011, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %494
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
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
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
