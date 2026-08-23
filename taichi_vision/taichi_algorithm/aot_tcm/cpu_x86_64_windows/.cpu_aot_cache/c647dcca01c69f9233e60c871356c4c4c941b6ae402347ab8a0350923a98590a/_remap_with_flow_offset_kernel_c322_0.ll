; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.29 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_remap_with_flow_offset_kernel_c322_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 40
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 44
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

define void @_remap_with_flow_offset_kernel_c322_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %14 = add i32 %9, %.neg
  %15 = tail call i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 88
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 92
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 76
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 68
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 72
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 64
  %31 = load i32, ptr %30, align 4
  %32 = getelementptr i8, ptr %19, i64 80
  %33 = load float, ptr %32, align 4
  %34 = getelementptr i8, ptr %19, i64 84
  %35 = load float, ptr %34, align 4
  %36 = getelementptr i8, ptr %19, i64 56
  %37 = load i32, ptr %36, align 4
  %38 = getelementptr i8, ptr %19, i64 60
  %39 = load i32, ptr %38, align 4
  %40 = add i32 %25, -1
  %41 = add i32 %27, -1
  %42 = add i32 %29, -1
  %43 = add i32 %31, -1
  %44 = add i32 %39, -1
  %45 = add i32 %37, -1
  %46 = sitofp i32 %40 to float
  %47 = sitofp i32 %41 to float
  %48 = sitofp i32 %42 to float
  %49 = sitofp i32 %43 to float
  %50 = icmp slt i32 %16, %18
  br i1 %50, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %51 = getelementptr i8, ptr %19, i64 32
  %52 = getelementptr i8, ptr %19, i64 20
  %53 = getelementptr i8, ptr %19, i64 24
  %54 = getelementptr i8, ptr %19, i64 8
  %55 = getelementptr i8, ptr %19, i64 4
  %56 = getelementptr i8, ptr %19, i64 48
  %57 = getelementptr i8, ptr %19, i64 44
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.06 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %259, %for_loop_body ]
  %58 = load ptr, ptr %3, align 8
  %59 = getelementptr inbounds nuw i8, ptr %58, i64 32872
  %60 = load ptr, ptr %59, align 8
  %61 = getelementptr inbounds nuw i8, ptr %60, i64 4
  %62 = load i32, ptr %61, align 4
  %63 = sdiv i32 %.06, %62
  %64 = mul i32 %63, %62
  %65 = xor i32 %62, %.06
  %66 = icmp slt i32 %65, 0
  %67 = icmp ne i32 %.06, %64
  %68 = and i1 %66, %67
  %.neg4 = sext i1 %68 to i32
  %69 = add i32 %63, %.neg4
  %70 = add i32 %69, %21
  %71 = mul i32 %62, -1
  %72 = mul i32 %71, %69
  %73 = add i32 %23, %.06
  %74 = add i32 %73, %72
  %75 = sitofp i32 %74 to float
  %76 = fmul reassoc ninf nsz float %75, %46
  %77 = fdiv reassoc ninf nsz float %76, %47
  %78 = sitofp i32 %70 to float
  %79 = fmul reassoc ninf nsz float %78, %48
  %80 = fdiv reassoc ninf nsz float %79, %49
  %81 = tail call reassoc ninf nsz float @llvm.floor.f32(float %77)
  %82 = fptosi float %81 to i32
  %83 = tail call reassoc ninf nsz float @llvm.floor.f32(float %80)
  %84 = fptosi float %83 to i32
  %85 = sitofp i32 %82 to float
  %86 = fsub reassoc ninf nsz float %77, %85
  %87 = sitofp i32 %84 to float
  %88 = fsub reassoc ninf nsz float %80, %87
  %89 = tail call i32 @llvm.abs.i32(i32 %82, i1 true)
  %90 = sub i32 %89, %40
  %91 = tail call i32 @llvm.smax.i32(i32 %90, i32 0)
  %92 = shl nuw i32 %91, 1
  %93 = sub i32 %89, %92
  %94 = tail call i32 @llvm.smax.i32(i32 %93, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %40, i32 %94)
  %96 = tail call i32 @llvm.abs.i32(i32 %84, i1 true)
  %97 = sub i32 %96, %42
  %98 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %99 = shl nuw i32 %98, 1
  %100 = sub i32 %96, %99
  %101 = tail call i32 @llvm.smax.i32(i32 %100, i32 0)
  %102 = tail call i32 @llvm.smin.i32(i32 %42, i32 %101)
  %103 = add i32 %82, 1
  %104 = tail call i32 @llvm.abs.i32(i32 %103, i1 true)
  %105 = sub i32 %104, %40
  %106 = tail call i32 @llvm.smax.i32(i32 %105, i32 0)
  %107 = shl nuw i32 %106, 1
  %108 = sub i32 %104, %107
  %109 = tail call i32 @llvm.smax.i32(i32 %108, i32 0)
  %110 = tail call i32 @llvm.smin.i32(i32 %40, i32 %109)
  %111 = add i32 %84, 1
  %112 = tail call i32 @llvm.abs.i32(i32 %111, i1 true)
  %113 = sub i32 %112, %42
  %114 = tail call i32 @llvm.smax.i32(i32 %113, i32 0)
  %115 = shl nuw i32 %114, 1
  %116 = sub i32 %112, %115
  %117 = tail call i32 @llvm.smax.i32(i32 %116, i32 0)
  %118 = tail call i32 @llvm.smin.i32(i32 %42, i32 %117)
  %119 = load ptr, ptr %51, align 8
  %120 = load i32, ptr %52, align 4
  %121 = load i32, ptr %53, align 4
  %122 = mul i32 %102, %120
  %123 = add i32 %95, %122
  %124 = mul i32 %123, %121
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %119, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = add i32 %110, %122
  %129 = mul i32 %128, %121
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %119, i64 %130
  %132 = load float, ptr %131, align 4
  %133 = mul i32 %118, %120
  %134 = add i32 %133, %95
  %135 = mul i32 %134, %121
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %119, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = add i32 %110, %133
  %140 = mul i32 %139, %121
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %119, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = fsub reassoc ninf nsz float 1.000000e+00, %86
  %145 = fmul reassoc ninf nsz float %144, %127
  %146 = fmul reassoc ninf nsz float %86, %132
  %147 = fadd reassoc ninf nsz float %145, %146
  %148 = fmul reassoc ninf nsz float %144, %138
  %149 = fmul reassoc ninf nsz float %86, %143
  %150 = fadd reassoc ninf nsz float %148, %149
  %151 = fsub reassoc ninf nsz float 1.000000e+00, %88
  %152 = fmul reassoc ninf nsz float %147, %151
  %153 = fmul reassoc ninf nsz float %150, %88
  %154 = fadd reassoc ninf nsz float %152, %153
  %155 = add i32 %124, 1
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %119, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = add i32 %129, 1
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %119, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = add i32 %135, 1
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %119, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = add i32 %140, 1
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, ptr %119, i64 %168
  %170 = load float, ptr %169, align 4
  %171 = fmul reassoc ninf nsz float %144, %158
  %172 = fmul reassoc ninf nsz float %86, %162
  %173 = fadd reassoc ninf nsz float %171, %172
  %174 = fmul reassoc ninf nsz float %144, %166
  %175 = fmul reassoc ninf nsz float %86, %170
  %176 = fadd reassoc ninf nsz float %174, %175
  %177 = fmul reassoc ninf nsz float %173, %151
  %178 = fmul reassoc ninf nsz float %176, %88
  %179 = fadd reassoc ninf nsz float %177, %178
  %180 = fmul reassoc ninf nsz float %154, %33
  %181 = fadd reassoc ninf nsz float %180, %75
  %182 = fmul reassoc ninf nsz float %179, %35
  %183 = fadd reassoc ninf nsz float %182, %78
  %184 = tail call reassoc ninf nsz float @llvm.floor.f32(float %181)
  %185 = fptosi float %184 to i32
  %186 = tail call reassoc ninf nsz float @llvm.floor.f32(float %183)
  %187 = fptosi float %186 to i32
  %188 = sitofp i32 %185 to float
  %189 = fsub reassoc ninf nsz float %181, %188
  %190 = sitofp i32 %187 to float
  %191 = fsub reassoc ninf nsz float %183, %190
  %192 = tail call i32 @llvm.abs.i32(i32 %185, i1 true)
  %193 = sub i32 %192, %44
  %194 = tail call i32 @llvm.smax.i32(i32 %193, i32 0)
  %195 = shl nuw i32 %194, 1
  %196 = sub i32 %192, %195
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = tail call i32 @llvm.smin.i32(i32 %44, i32 %197)
  %199 = tail call i32 @llvm.abs.i32(i32 %187, i1 true)
  %200 = sub i32 %199, %45
  %201 = tail call i32 @llvm.smax.i32(i32 %200, i32 0)
  %202 = shl nuw i32 %201, 1
  %203 = sub i32 %199, %202
  %204 = tail call i32 @llvm.smax.i32(i32 %203, i32 0)
  %205 = tail call i32 @llvm.smin.i32(i32 %45, i32 %204)
  %206 = add i32 %185, 1
  %207 = tail call i32 @llvm.abs.i32(i32 %206, i1 true)
  %208 = sub i32 %207, %44
  %209 = tail call i32 @llvm.smax.i32(i32 %208, i32 0)
  %210 = shl nuw i32 %209, 1
  %211 = sub i32 %207, %210
  %212 = tail call i32 @llvm.smax.i32(i32 %211, i32 0)
  %213 = tail call i32 @llvm.smin.i32(i32 %44, i32 %212)
  %214 = add i32 %187, 1
  %215 = tail call i32 @llvm.abs.i32(i32 %214, i1 true)
  %216 = sub i32 %215, %45
  %217 = tail call i32 @llvm.smax.i32(i32 %216, i32 0)
  %218 = shl nuw i32 %217, 1
  %219 = sub i32 %215, %218
  %220 = tail call i32 @llvm.smax.i32(i32 %219, i32 0)
  %221 = tail call i32 @llvm.smin.i32(i32 %45, i32 %220)
  %222 = load ptr, ptr %54, align 8
  %223 = load i32, ptr %55, align 4
  %224 = mul i32 %205, %223
  %225 = add i32 %224, %198
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, ptr %222, i64 %226
  %228 = load float, ptr %227, align 4
  %229 = add i32 %224, %213
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, ptr %222, i64 %230
  %232 = load float, ptr %231, align 4
  %233 = mul i32 %221, %223
  %234 = add i32 %233, %198
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, ptr %222, i64 %235
  %237 = load float, ptr %236, align 4
  %238 = add i32 %233, %213
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, ptr %222, i64 %239
  %241 = load float, ptr %240, align 4
  %242 = fsub reassoc ninf nsz float 1.000000e+00, %189
  %243 = fmul reassoc ninf nsz float %242, %228
  %244 = fmul reassoc ninf nsz float %189, %232
  %245 = fadd reassoc ninf nsz float %243, %244
  %246 = fmul reassoc ninf nsz float %242, %237
  %247 = fmul reassoc ninf nsz float %189, %241
  %248 = fadd reassoc ninf nsz float %246, %247
  %249 = fsub reassoc ninf nsz float %248, %245
  %250 = fmul reassoc ninf nsz float %249, %191
  %251 = fadd reassoc ninf nsz float %250, %245
  %252 = load ptr, ptr %56, align 8
  %253 = load i32, ptr %57, align 4
  %254 = sub i32 %253, %62
  %255 = mul i32 %254, %69
  %256 = add i32 %.06, %255
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, ptr %252, i64 %257
  store float %251, ptr %258, align 4
  %259 = add nsw i32 %.06, 1
  %exitcond.not = icmp eq i32 %18, %259
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
  %4 = alloca %struct.RuntimeContext.29, align 8
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
