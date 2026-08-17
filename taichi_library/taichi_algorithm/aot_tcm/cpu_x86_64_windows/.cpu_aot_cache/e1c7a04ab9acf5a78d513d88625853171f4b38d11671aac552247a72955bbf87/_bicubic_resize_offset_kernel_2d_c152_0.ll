; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bicubic_resize_offset_kernel_2d_c152_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 16
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 20
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 32872
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 4
  store i32 %6, ptr %11, align 4
  %12 = mul i32 %6, %3
  %13 = load ptr, ptr %7, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  store i32 %12, ptr %15, align 4
  ret void
}

define void @_bicubic_resize_offset_kernel_2d_c152_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 52
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 32
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 40
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 36
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 44
  %31 = load i32, ptr %30, align 4
  %32 = sitofp i32 %25 to float
  %33 = sitofp i32 %27 to float
  %34 = sitofp i32 %29 to float
  %35 = sitofp i32 %31 to float
  %36 = add i32 %25, -1
  %37 = add i32 %29, -1
  %38 = icmp slt i32 %16, %18
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr i8, ptr %19, i64 8
  %40 = getelementptr i8, ptr %19, i64 4
  %41 = getelementptr i8, ptr %19, i64 24
  %42 = getelementptr i8, ptr %19, i64 20
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.017 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %261, %for_loop_body ]
  %43 = load ptr, ptr %3, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 4
  %47 = load i32, ptr %46, align 4
  %48 = sdiv i32 %.017, %47
  %49 = mul i32 %48, %47
  %50 = xor i32 %47, %.017
  %51 = icmp slt i32 %50, 0
  %52 = icmp ne i32 %.017, %49
  %53 = and i1 %51, %52
  %.neg4 = sext i1 %53 to i32
  %54 = add i32 %48, %.neg4
  %55 = add i32 %54, %21
  %56 = mul i32 %47, -1
  %57 = mul i32 %56, %54
  %58 = add i32 %23, %.017
  %59 = add i32 %58, %57
  %60 = sitofp i32 %55 to float
  %61 = fadd reassoc ninf nsz float %60, 5.000000e-01
  %62 = fmul reassoc ninf nsz float %61, %32
  %63 = fdiv reassoc ninf nsz float %62, %33
  %64 = fadd reassoc ninf nsz float %63, -5.000000e-01
  %65 = sitofp i32 %59 to float
  %66 = fadd reassoc ninf nsz float %65, 5.000000e-01
  %67 = fmul reassoc ninf nsz float %66, %34
  %68 = fdiv reassoc ninf nsz float %67, %35
  %69 = fadd reassoc ninf nsz float %68, -5.000000e-01
  %70 = tail call reassoc ninf nsz float @llvm.floor.f32(float %69)
  %71 = fptosi float %70 to i32
  %72 = tail call reassoc ninf nsz float @llvm.floor.f32(float %64)
  %73 = fptosi float %72 to i32
  %74 = sitofp i32 %71 to float
  %75 = fsub reassoc ninf nsz float %69, %74
  %76 = tail call noundef float @llvm.fabs.f32(float %75)
  %77 = fadd reassoc ninf nsz float %76, 1.000000e+00
  %78 = fmul reassoc ninf nsz float %77, %77
  %79 = fmul reassoc ninf nsz float %77, 7.500000e-01
  %80 = fmul reassoc ninf nsz float %77, -6.000000e+00
  %81 = fsub reassoc ninf nsz float 3.750000e+00, %79
  %reass.mul = fmul reassoc ninf nsz float %78, %81
  %82 = fadd reassoc ninf nsz float %80, 3.000000e+00
  %83 = fadd reassoc ninf nsz float %82, %reass.mul
  %84 = fmul reassoc ninf nsz float %75, %75
  %85 = fmul reassoc ninf nsz float %84, 1.250000e+00
  %86 = fmul reassoc ninf nsz float %85, %76
  %87 = fmul reassoc ninf nsz float %84, 2.250000e+00
  %88 = fsub reassoc ninf nsz float %86, %87
  %89 = fadd reassoc ninf nsz float %88, 1.000000e+00
  %90 = fsub reassoc ninf nsz float 1.000000e+00, %76
  %91 = fmul reassoc ninf nsz float %90, %90
  %92 = fmul reassoc ninf nsz float %90, 1.250000e+00
  %93 = fadd reassoc ninf nsz float %92, -2.250000e+00
  %94 = fmul reassoc ninf nsz float %93, %91
  %95 = fadd reassoc ninf nsz float %94, 1.000000e+00
  %96 = fsub reassoc ninf nsz float 2.000000e+00, %76
  %97 = fmul reassoc ninf nsz float %96, %96
  %98 = fmul reassoc ninf nsz float %96, 7.500000e-01
  %99 = fmul reassoc ninf nsz float %96, -6.000000e+00
  %100 = fsub reassoc ninf nsz float 3.750000e+00, %98
  %reass.mul8 = fmul reassoc ninf nsz float %97, %100
  %101 = fadd reassoc ninf nsz float %99, 3.000000e+00
  %102 = fadd reassoc ninf nsz float %101, %reass.mul8
  %103 = sitofp i32 %73 to float
  %104 = fsub reassoc ninf nsz float %64, %103
  %105 = tail call noundef float @llvm.fabs.f32(float %104)
  %106 = fadd reassoc ninf nsz float %105, 1.000000e+00
  %107 = fmul reassoc ninf nsz float %106, %106
  %108 = fmul reassoc ninf nsz float %106, 7.500000e-01
  %109 = fmul reassoc ninf nsz float %106, -6.000000e+00
  %110 = fsub reassoc ninf nsz float 3.750000e+00, %108
  %reass.mul10 = fmul reassoc ninf nsz float %107, %110
  %111 = fadd reassoc ninf nsz float %109, 3.000000e+00
  %112 = fadd reassoc ninf nsz float %111, %reass.mul10
  %113 = fmul reassoc ninf nsz float %104, %104
  %114 = fmul reassoc ninf nsz float %105, 1.250000e+00
  %reass.add11 = fadd reassoc ninf nsz float %114, -2.250000e+00
  %reass.mul12 = fmul reassoc ninf nsz float %113, %reass.add11
  %115 = fadd reassoc ninf nsz float %reass.mul12, 1.000000e+00
  %116 = fsub reassoc ninf nsz float 1.000000e+00, %105
  %117 = fmul reassoc ninf nsz float %116, %116
  %118 = fmul reassoc ninf nsz float %116, 1.250000e+00
  %reass.add13 = fadd reassoc ninf nsz float %118, -2.250000e+00
  %reass.mul14 = fmul reassoc ninf nsz float %117, %reass.add13
  %119 = fadd reassoc ninf nsz float %reass.mul14, 1.000000e+00
  %120 = fsub reassoc ninf nsz float 2.000000e+00, %105
  %121 = fmul reassoc ninf nsz float %120, %120
  %122 = fmul reassoc ninf nsz float %120, 7.500000e-01
  %123 = fmul reassoc ninf nsz float %120, -6.000000e+00
  %124 = fsub reassoc ninf nsz float 3.750000e+00, %122
  %reass.mul16 = fmul reassoc ninf nsz float %121, %124
  %125 = fadd reassoc ninf nsz float %123, 3.000000e+00
  %126 = fadd reassoc ninf nsz float %125, %reass.mul16
  %127 = add i32 %73, -1
  %128 = tail call i32 @llvm.smax.i32(i32 %127, i32 0)
  %129 = tail call i32 @llvm.smin.i32(i32 %36, i32 %128)
  %130 = add i32 %71, -1
  %131 = tail call i32 @llvm.smax.i32(i32 %130, i32 0)
  %132 = tail call i32 @llvm.smin.i32(i32 %37, i32 %131)
  %133 = load ptr, ptr %39, align 8
  %134 = load i32, ptr %40, align 4
  %135 = mul i32 %129, %134
  %136 = add i32 %132, %135
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %133, i64 %137
  %139 = load float, ptr %138, align 4
  %140 = fmul reassoc ninf nsz float %83, %139
  %141 = tail call i32 @llvm.smax.i32(i32 %71, i32 0)
  %142 = tail call i32 @llvm.smin.i32(i32 %37, i32 %141)
  %143 = add i32 %135, %142
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %133, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = fmul reassoc ninf nsz float %89, %146
  %148 = add i32 %71, 1
  %149 = tail call i32 @llvm.smax.i32(i32 %148, i32 0)
  %150 = tail call i32 @llvm.smin.i32(i32 %37, i32 %149)
  %151 = add i32 %150, %135
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %133, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = fmul reassoc ninf nsz float %95, %154
  %156 = add i32 %71, 2
  %157 = tail call i32 @llvm.smax.i32(i32 %156, i32 0)
  %158 = tail call i32 @llvm.smin.i32(i32 %37, i32 %157)
  %159 = add i32 %158, %135
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %133, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = fmul reassoc ninf nsz float %102, %162
  %164 = fadd reassoc ninf nsz float %155, %147
  %165 = fadd reassoc ninf nsz float %164, %140
  %166 = fadd reassoc ninf nsz float %165, %163
  %167 = fmul reassoc ninf nsz float %166, %112
  %168 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %169 = tail call i32 @llvm.smin.i32(i32 %36, i32 %168)
  %170 = mul i32 %169, %134
  %171 = add i32 %132, %170
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %133, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = fmul reassoc ninf nsz float %83, %174
  %176 = add i32 %142, %170
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, ptr %133, i64 %177
  %179 = load float, ptr %178, align 4
  %180 = fmul reassoc ninf nsz float %89, %179
  %181 = add i32 %150, %170
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %133, i64 %182
  %184 = load float, ptr %183, align 4
  %185 = fmul reassoc ninf nsz float %95, %184
  %186 = add i32 %158, %170
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, ptr %133, i64 %187
  %189 = load float, ptr %188, align 4
  %190 = fmul reassoc ninf nsz float %102, %189
  %191 = fadd reassoc ninf nsz float %185, %180
  %192 = fadd reassoc ninf nsz float %191, %175
  %193 = fadd reassoc ninf nsz float %192, %190
  %194 = fmul reassoc ninf nsz float %193, %115
  %195 = fadd reassoc ninf nsz float %167, %194
  %196 = add i32 %73, 1
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = tail call i32 @llvm.smin.i32(i32 %36, i32 %197)
  %199 = mul i32 %198, %134
  %200 = add i32 %132, %199
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, ptr %133, i64 %201
  %203 = load float, ptr %202, align 4
  %204 = fmul reassoc ninf nsz float %83, %203
  %205 = add i32 %199, %142
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %133, i64 %206
  %208 = load float, ptr %207, align 4
  %209 = fmul reassoc ninf nsz float %89, %208
  %210 = add i32 %150, %199
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %133, i64 %211
  %213 = load float, ptr %212, align 4
  %214 = fmul reassoc ninf nsz float %95, %213
  %215 = add i32 %158, %199
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, ptr %133, i64 %216
  %218 = load float, ptr %217, align 4
  %219 = fmul reassoc ninf nsz float %102, %218
  %220 = fadd reassoc ninf nsz float %214, %209
  %221 = fadd reassoc ninf nsz float %220, %204
  %222 = fadd reassoc ninf nsz float %221, %219
  %223 = fmul reassoc ninf nsz float %222, %119
  %224 = fadd reassoc ninf nsz float %195, %223
  %225 = add i32 %73, 2
  %226 = tail call i32 @llvm.smax.i32(i32 %225, i32 0)
  %227 = tail call i32 @llvm.smin.i32(i32 %36, i32 %226)
  %228 = mul i32 %227, %134
  %229 = add i32 %132, %228
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, ptr %133, i64 %230
  %232 = load float, ptr %231, align 4
  %233 = fmul reassoc ninf nsz float %83, %232
  %234 = add i32 %228, %142
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %133, i64 %235
  %237 = load float, ptr %236, align 4
  %238 = fmul reassoc ninf nsz float %89, %237
  %239 = add i32 %150, %228
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, ptr %133, i64 %240
  %242 = load float, ptr %241, align 4
  %243 = fmul reassoc ninf nsz float %95, %242
  %244 = add i32 %158, %228
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, ptr %133, i64 %245
  %247 = load float, ptr %246, align 4
  %248 = fmul reassoc ninf nsz float %102, %247
  %249 = fadd reassoc ninf nsz float %243, %238
  %250 = fadd reassoc ninf nsz float %249, %233
  %251 = fadd reassoc ninf nsz float %250, %248
  %252 = fmul reassoc ninf nsz float %251, %126
  %253 = fadd reassoc ninf nsz float %224, %252
  %254 = load ptr, ptr %41, align 8
  %255 = load i32, ptr %42, align 4
  %256 = sub i32 %255, %47
  %257 = mul i32 %256, %54
  %258 = add i32 %.017, %257
  %259 = sext i32 %258 to i64
  %260 = getelementptr float, ptr %254, i64 %259
  store float %253, ptr %260, align 4
  %261 = add nsw i32 %.017, 1
  %exitcond.not = icmp eq i32 %18, %261
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
