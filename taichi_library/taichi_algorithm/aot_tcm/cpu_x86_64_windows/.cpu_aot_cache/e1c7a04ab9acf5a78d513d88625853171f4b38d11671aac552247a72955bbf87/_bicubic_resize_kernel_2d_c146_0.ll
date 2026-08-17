; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bicubic_resize_kernel_2d_c146_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_bicubic_resize_kernel_2d_c146_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.017 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %255, %for_loop_body ]
  %33 = load ptr, ptr %3, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 4
  %37 = load i32, ptr %36, align 4
  %38 = sdiv i32 %.017, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %.017
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %.017, %39
  %43 = and i1 %41, %42
  %.neg4 = sext i1 %43 to i32
  %44 = add i32 %38, %.neg4
  %45 = mul i32 %37, -1
  %46 = mul i32 %45, %44
  %47 = add i32 %.017, %46
  %48 = sitofp i32 %44 to float
  %49 = fadd reassoc ninf nsz float %48, 5.000000e-01
  %50 = getelementptr inbounds nuw i8, ptr %35, i64 8
  %51 = load i32, ptr %50, align 4
  %52 = sitofp i32 %51 to float
  %53 = fmul reassoc ninf nsz float %49, %24
  %54 = fdiv reassoc ninf nsz float %53, %52
  %55 = fadd reassoc ninf nsz float %54, -5.000000e-01
  %56 = sitofp i32 %47 to float
  %57 = fadd reassoc ninf nsz float %56, 5.000000e-01
  %58 = getelementptr inbounds nuw i8, ptr %35, i64 12
  %59 = load i32, ptr %58, align 4
  %60 = sitofp i32 %59 to float
  %61 = fmul reassoc ninf nsz float %57, %25
  %62 = fdiv reassoc ninf nsz float %61, %60
  %63 = fadd reassoc ninf nsz float %62, -5.000000e-01
  %64 = tail call reassoc ninf nsz float @llvm.floor.f32(float %63)
  %65 = fptosi float %64 to i32
  %66 = tail call reassoc ninf nsz float @llvm.floor.f32(float %55)
  %67 = fptosi float %66 to i32
  %68 = sitofp i32 %65 to float
  %69 = fsub reassoc ninf nsz float %63, %68
  %70 = sitofp i32 %67 to float
  %71 = fsub reassoc ninf nsz float %55, %70
  %72 = tail call noundef float @llvm.fabs.f32(float %69)
  %73 = fadd reassoc ninf nsz float %72, 1.000000e+00
  %74 = fmul reassoc ninf nsz float %73, %73
  %75 = fmul reassoc ninf nsz float %73, 7.500000e-01
  %76 = fmul reassoc ninf nsz float %73, -6.000000e+00
  %77 = fsub reassoc ninf nsz float 3.750000e+00, %75
  %reass.mul = fmul reassoc ninf nsz float %74, %77
  %78 = fadd reassoc ninf nsz float %76, 3.000000e+00
  %79 = fadd reassoc ninf nsz float %78, %reass.mul
  %80 = fmul reassoc ninf nsz float %69, %69
  %81 = fmul reassoc ninf nsz float %80, 1.250000e+00
  %82 = fmul reassoc ninf nsz float %81, %72
  %83 = fmul reassoc ninf nsz float %80, 2.250000e+00
  %84 = fsub reassoc ninf nsz float %82, %83
  %85 = fadd reassoc ninf nsz float %84, 1.000000e+00
  %86 = fsub reassoc ninf nsz float 1.000000e+00, %72
  %87 = fmul reassoc ninf nsz float %86, %86
  %88 = fmul reassoc ninf nsz float %86, 1.250000e+00
  %89 = fadd reassoc ninf nsz float %88, -2.250000e+00
  %90 = fmul reassoc ninf nsz float %89, %87
  %91 = fadd reassoc ninf nsz float %90, 1.000000e+00
  %92 = fsub reassoc ninf nsz float 2.000000e+00, %72
  %93 = fmul reassoc ninf nsz float %92, %92
  %94 = fmul reassoc ninf nsz float %92, 7.500000e-01
  %95 = fmul reassoc ninf nsz float %92, -6.000000e+00
  %96 = fsub reassoc ninf nsz float 3.750000e+00, %94
  %reass.mul8 = fmul reassoc ninf nsz float %93, %96
  %97 = fadd reassoc ninf nsz float %95, 3.000000e+00
  %98 = fadd reassoc ninf nsz float %97, %reass.mul8
  %99 = tail call noundef float @llvm.fabs.f32(float %71)
  %100 = fadd reassoc ninf nsz float %99, 1.000000e+00
  %101 = fmul reassoc ninf nsz float %100, %100
  %102 = fmul reassoc ninf nsz float %100, 7.500000e-01
  %103 = fmul reassoc ninf nsz float %100, -6.000000e+00
  %104 = fsub reassoc ninf nsz float 3.750000e+00, %102
  %reass.mul10 = fmul reassoc ninf nsz float %101, %104
  %105 = fadd reassoc ninf nsz float %103, 3.000000e+00
  %106 = fadd reassoc ninf nsz float %105, %reass.mul10
  %107 = fmul reassoc ninf nsz float %71, %71
  %108 = fmul reassoc ninf nsz float %99, 1.250000e+00
  %reass.add11 = fadd reassoc ninf nsz float %108, -2.250000e+00
  %reass.mul12 = fmul reassoc ninf nsz float %107, %reass.add11
  %109 = fadd reassoc ninf nsz float %reass.mul12, 1.000000e+00
  %110 = fsub reassoc ninf nsz float 1.000000e+00, %99
  %111 = fmul reassoc ninf nsz float %110, %110
  %112 = fmul reassoc ninf nsz float %110, 1.250000e+00
  %reass.add13 = fadd reassoc ninf nsz float %112, -2.250000e+00
  %reass.mul14 = fmul reassoc ninf nsz float %111, %reass.add13
  %113 = fadd reassoc ninf nsz float %reass.mul14, 1.000000e+00
  %114 = fsub reassoc ninf nsz float 2.000000e+00, %99
  %115 = fmul reassoc ninf nsz float %114, %114
  %116 = fmul reassoc ninf nsz float %114, 7.500000e-01
  %117 = fmul reassoc ninf nsz float %114, -6.000000e+00
  %118 = fsub reassoc ninf nsz float 3.750000e+00, %116
  %reass.mul16 = fmul reassoc ninf nsz float %115, %118
  %119 = fadd reassoc ninf nsz float %117, 3.000000e+00
  %120 = fadd reassoc ninf nsz float %119, %reass.mul16
  %121 = add i32 %67, -1
  %122 = tail call i32 @llvm.smax.i32(i32 %121, i32 0)
  %123 = tail call i32 @llvm.smin.i32(i32 %26, i32 %122)
  %124 = add i32 %65, -1
  %125 = tail call i32 @llvm.smax.i32(i32 %124, i32 0)
  %126 = tail call i32 @llvm.smin.i32(i32 %27, i32 %125)
  %127 = load ptr, ptr %29, align 8
  %128 = load i32, ptr %30, align 4
  %129 = mul i32 %123, %128
  %130 = add i32 %126, %129
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, ptr %127, i64 %131
  %133 = load float, ptr %132, align 4
  %134 = fmul reassoc ninf nsz float %79, %133
  %135 = tail call i32 @llvm.smax.i32(i32 %65, i32 0)
  %136 = tail call i32 @llvm.smin.i32(i32 %27, i32 %135)
  %137 = add i32 %129, %136
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %127, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = fmul reassoc ninf nsz float %85, %140
  %142 = add i32 %65, 1
  %143 = tail call i32 @llvm.smax.i32(i32 %142, i32 0)
  %144 = tail call i32 @llvm.smin.i32(i32 %27, i32 %143)
  %145 = add i32 %144, %129
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, ptr %127, i64 %146
  %148 = load float, ptr %147, align 4
  %149 = fmul reassoc ninf nsz float %91, %148
  %150 = add i32 %65, 2
  %151 = tail call i32 @llvm.smax.i32(i32 %150, i32 0)
  %152 = tail call i32 @llvm.smin.i32(i32 %27, i32 %151)
  %153 = add i32 %152, %129
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %127, i64 %154
  %156 = load float, ptr %155, align 4
  %157 = fmul reassoc ninf nsz float %98, %156
  %158 = fadd reassoc ninf nsz float %149, %141
  %159 = fadd reassoc ninf nsz float %158, %134
  %160 = fadd reassoc ninf nsz float %159, %157
  %161 = fmul reassoc ninf nsz float %160, %106
  %162 = tail call i32 @llvm.smax.i32(i32 %67, i32 0)
  %163 = tail call i32 @llvm.smin.i32(i32 %26, i32 %162)
  %164 = mul i32 %163, %128
  %165 = add i32 %126, %164
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, ptr %127, i64 %166
  %168 = load float, ptr %167, align 4
  %169 = fmul reassoc ninf nsz float %79, %168
  %170 = add i32 %136, %164
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %127, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = fmul reassoc ninf nsz float %85, %173
  %175 = add i32 %144, %164
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, ptr %127, i64 %176
  %178 = load float, ptr %177, align 4
  %179 = fmul reassoc ninf nsz float %91, %178
  %180 = add i32 %152, %164
  %181 = sext i32 %180 to i64
  %182 = getelementptr float, ptr %127, i64 %181
  %183 = load float, ptr %182, align 4
  %184 = fmul reassoc ninf nsz float %98, %183
  %185 = fadd reassoc ninf nsz float %179, %174
  %186 = fadd reassoc ninf nsz float %185, %169
  %187 = fadd reassoc ninf nsz float %186, %184
  %188 = fmul reassoc ninf nsz float %187, %109
  %189 = fadd reassoc ninf nsz float %161, %188
  %190 = add i32 %67, 1
  %191 = tail call i32 @llvm.smax.i32(i32 %190, i32 0)
  %192 = tail call i32 @llvm.smin.i32(i32 %26, i32 %191)
  %193 = mul i32 %192, %128
  %194 = add i32 %126, %193
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, ptr %127, i64 %195
  %197 = load float, ptr %196, align 4
  %198 = fmul reassoc ninf nsz float %79, %197
  %199 = add i32 %193, %136
  %200 = sext i32 %199 to i64
  %201 = getelementptr float, ptr %127, i64 %200
  %202 = load float, ptr %201, align 4
  %203 = fmul reassoc ninf nsz float %85, %202
  %204 = add i32 %144, %193
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, ptr %127, i64 %205
  %207 = load float, ptr %206, align 4
  %208 = fmul reassoc ninf nsz float %91, %207
  %209 = add i32 %152, %193
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, ptr %127, i64 %210
  %212 = load float, ptr %211, align 4
  %213 = fmul reassoc ninf nsz float %98, %212
  %214 = fadd reassoc ninf nsz float %208, %203
  %215 = fadd reassoc ninf nsz float %214, %198
  %216 = fadd reassoc ninf nsz float %215, %213
  %217 = fmul reassoc ninf nsz float %216, %113
  %218 = fadd reassoc ninf nsz float %189, %217
  %219 = add i32 %67, 2
  %220 = tail call i32 @llvm.smax.i32(i32 %219, i32 0)
  %221 = tail call i32 @llvm.smin.i32(i32 %26, i32 %220)
  %222 = mul i32 %221, %128
  %223 = add i32 %126, %222
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %127, i64 %224
  %226 = load float, ptr %225, align 4
  %227 = fmul reassoc ninf nsz float %79, %226
  %228 = add i32 %222, %136
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, ptr %127, i64 %229
  %231 = load float, ptr %230, align 4
  %232 = fmul reassoc ninf nsz float %85, %231
  %233 = add i32 %144, %222
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, ptr %127, i64 %234
  %236 = load float, ptr %235, align 4
  %237 = fmul reassoc ninf nsz float %91, %236
  %238 = add i32 %152, %222
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, ptr %127, i64 %239
  %241 = load float, ptr %240, align 4
  %242 = fmul reassoc ninf nsz float %98, %241
  %243 = fadd reassoc ninf nsz float %237, %232
  %244 = fadd reassoc ninf nsz float %243, %227
  %245 = fadd reassoc ninf nsz float %244, %242
  %246 = fmul reassoc ninf nsz float %245, %120
  %247 = fadd reassoc ninf nsz float %218, %246
  %248 = load ptr, ptr %31, align 8
  %249 = load i32, ptr %32, align 4
  %250 = sub i32 %249, %37
  %251 = mul i32 %250, %44
  %252 = add i32 %.017, %251
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, ptr %248, i64 %253
  store float %247, ptr %254, align 4
  %255 = add nsw i32 %.017, 1
  %exitcond.not = icmp eq i32 %18, %255
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
