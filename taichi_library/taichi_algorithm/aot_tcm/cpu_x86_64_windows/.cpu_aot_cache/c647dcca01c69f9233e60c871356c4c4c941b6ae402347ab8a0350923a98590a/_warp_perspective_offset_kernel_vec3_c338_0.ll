; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.35 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_warp_perspective_offset_kernel_vec3_c338_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 36
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

define void @_warp_perspective_offset_kernel_vec3_c338_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 60
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 48
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 52
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 24
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr i8, ptr %19, i64 20
  %31 = load i32, ptr %30, align 4
  %32 = getelementptr i8, ptr %29, i64 4
  %33 = getelementptr i8, ptr %29, i64 8
  %34 = sext i32 %31 to i64
  %35 = getelementptr float, ptr %29, i64 %34
  %36 = add i32 %31, 1
  %37 = sext i32 %36 to i64
  %38 = getelementptr float, ptr %29, i64 %37
  %39 = add i32 %31, 2
  %40 = sext i32 %39 to i64
  %41 = getelementptr float, ptr %29, i64 %40
  %42 = shl i32 %31, 1
  %43 = sext i32 %42 to i64
  %44 = getelementptr float, ptr %29, i64 %43
  %45 = getelementptr i8, ptr %44, i64 4
  %46 = add i32 %42, 2
  %47 = sext i32 %46 to i64
  %48 = getelementptr float, ptr %29, i64 %47
  %49 = add i32 %27, -1
  %50 = add i32 %25, -1
  %51 = icmp slt i32 %16, %18
  br i1 %51, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %52 = getelementptr i8, ptr %19, i64 8
  %53 = getelementptr i8, ptr %19, i64 4
  %54 = getelementptr i8, ptr %19, i64 40
  %55 = getelementptr i8, ptr %19, i64 36
  %56 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %56, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %249, %for_loop_body ]
  %57 = load ptr, ptr %3, align 8
  %58 = getelementptr inbounds nuw i8, ptr %57, i64 32872
  %59 = load ptr, ptr %58, align 8
  %60 = getelementptr inbounds nuw i8, ptr %59, i64 4
  %61 = load i32, ptr %60, align 4
  %62 = sdiv i32 %.05, %61
  %63 = mul i32 %62, %61
  %64 = xor i32 %61, %.05
  %65 = icmp slt i32 %64, 0
  %66 = icmp ne i32 %.05, %63
  %67 = and i1 %65, %66
  %.neg4 = sext i1 %67 to i32
  %68 = add i32 %62, %.neg4
  %69 = add i32 %68, %21
  %70 = mul i32 %61, -1
  %71 = mul i32 %70, %68
  %72 = add i32 %23, %.05
  %73 = add i32 %72, %71
  %74 = load float, ptr %29, align 4
  %75 = sitofp i32 %73 to float
  %76 = fmul reassoc ninf nsz float %74, %75
  %77 = load float, ptr %32, align 4
  %78 = sitofp i32 %69 to float
  %79 = fmul reassoc ninf nsz float %77, %78
  %80 = load float, ptr %33, align 4
  %81 = fadd reassoc ninf nsz float %79, %80
  %82 = fadd reassoc ninf nsz float %81, %76
  %83 = load float, ptr %35, align 4
  %84 = fmul reassoc ninf nsz float %83, %75
  %85 = load float, ptr %38, align 4
  %86 = fmul reassoc ninf nsz float %85, %78
  %87 = load float, ptr %41, align 4
  %88 = fadd reassoc ninf nsz float %86, %87
  %89 = fadd reassoc ninf nsz float %88, %84
  %90 = load float, ptr %44, align 4
  %91 = fmul reassoc ninf nsz float %90, %75
  %92 = load float, ptr %45, align 4
  %93 = fmul reassoc ninf nsz float %92, %78
  %94 = load float, ptr %48, align 4
  %95 = fadd reassoc ninf nsz float %93, 0x3E112E0BE0000000
  %96 = fadd reassoc ninf nsz float %95, %94
  %97 = fadd reassoc ninf nsz float %96, %91
  %98 = fdiv reassoc ninf nsz float %82, %97
  %99 = fdiv reassoc ninf nsz float %89, %97
  %100 = tail call reassoc ninf nsz float @llvm.floor.f32(float %98)
  %101 = fptosi float %100 to i32
  %102 = tail call reassoc ninf nsz float @llvm.floor.f32(float %99)
  %103 = fptosi float %102 to i32
  %104 = sitofp i32 %101 to float
  %105 = fsub reassoc ninf nsz float %98, %104
  %106 = sitofp i32 %103 to float
  %107 = fsub reassoc ninf nsz float %99, %106
  %108 = tail call i32 @llvm.abs.i32(i32 %101, i1 true)
  %109 = sub i32 %108, %49
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %111 = shl nuw i32 %110, 1
  %112 = sub i32 %108, %111
  %113 = tail call i32 @llvm.smax.i32(i32 %112, i32 0)
  %114 = tail call i32 @llvm.smin.i32(i32 %49, i32 %113)
  %115 = tail call i32 @llvm.abs.i32(i32 %103, i1 true)
  %116 = sub i32 %115, %50
  %117 = tail call i32 @llvm.smax.i32(i32 %116, i32 0)
  %118 = shl nuw i32 %117, 1
  %119 = sub i32 %115, %118
  %120 = tail call i32 @llvm.smax.i32(i32 %119, i32 0)
  %121 = tail call i32 @llvm.smin.i32(i32 %50, i32 %120)
  %122 = add i32 %101, 1
  %123 = tail call i32 @llvm.abs.i32(i32 %122, i1 true)
  %124 = sub i32 %123, %49
  %125 = tail call i32 @llvm.smax.i32(i32 %124, i32 0)
  %126 = shl nuw i32 %125, 1
  %127 = sub i32 %123, %126
  %128 = tail call i32 @llvm.smax.i32(i32 %127, i32 0)
  %129 = tail call i32 @llvm.smin.i32(i32 %49, i32 %128)
  %130 = add i32 %103, 1
  %131 = tail call i32 @llvm.abs.i32(i32 %130, i1 true)
  %132 = sub i32 %131, %50
  %133 = tail call i32 @llvm.smax.i32(i32 %132, i32 0)
  %134 = shl nuw i32 %133, 1
  %135 = sub i32 %131, %134
  %136 = tail call i32 @llvm.smax.i32(i32 %135, i32 0)
  %137 = tail call i32 @llvm.smin.i32(i32 %50, i32 %136)
  %138 = load ptr, ptr %52, align 8
  %139 = load i32, ptr %53, align 4
  %140 = mul i32 %121, %139
  %141 = add i32 %140, %114
  %142 = mul i32 %141, 3
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %138, i64 %143
  %145 = load float, ptr %144, align 4
  %146 = add i32 %142, 1
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %138, i64 %147
  %149 = load float, ptr %148, align 4
  %150 = add i32 %142, 2
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %138, i64 %151
  %153 = load float, ptr %152, align 4
  %154 = add i32 %140, %129
  %155 = mul i32 %154, 3
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %138, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = add i32 %155, 1
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, ptr %138, i64 %160
  %162 = load float, ptr %161, align 4
  %163 = add i32 %155, 2
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %138, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = mul i32 %137, %139
  %168 = add i32 %167, %114
  %169 = mul i32 %168, 3
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, ptr %138, i64 %170
  %172 = load float, ptr %171, align 4
  %173 = add i32 %169, 1
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, ptr %138, i64 %174
  %176 = load float, ptr %175, align 4
  %177 = add i32 %169, 2
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, ptr %138, i64 %178
  %180 = load float, ptr %179, align 4
  %181 = add i32 %167, %129
  %182 = mul i32 %181, 3
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %138, i64 %183
  %185 = load float, ptr %184, align 4
  %186 = add i32 %182, 1
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, ptr %138, i64 %187
  %189 = load float, ptr %188, align 4
  %190 = add i32 %182, 2
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, ptr %138, i64 %191
  %193 = load float, ptr %192, align 4
  %194 = fsub reassoc ninf nsz float 1.000000e+00, %105
  %195 = fmul reassoc ninf nsz float %194, %145
  %196 = fmul reassoc ninf nsz float %194, %149
  %197 = fmul reassoc ninf nsz float %194, %153
  %198 = fmul reassoc ninf nsz float %105, %158
  %199 = fmul reassoc ninf nsz float %105, %162
  %200 = fmul reassoc ninf nsz float %105, %166
  %201 = fadd reassoc ninf nsz float %195, %198
  %202 = fadd reassoc ninf nsz float %196, %199
  %203 = fadd reassoc ninf nsz float %197, %200
  %204 = fmul reassoc ninf nsz float %194, %172
  %205 = fmul reassoc ninf nsz float %176, %194
  %206 = fmul reassoc ninf nsz float %180, %194
  %207 = fmul reassoc ninf nsz float %185, %105
  %208 = fmul reassoc ninf nsz float %189, %105
  %209 = fmul reassoc ninf nsz float %193, %105
  %210 = fadd reassoc ninf nsz float %207, %204
  %211 = fadd reassoc ninf nsz float %208, %205
  %212 = fadd reassoc ninf nsz float %209, %206
  %213 = fsub reassoc ninf nsz float 1.000000e+00, %107
  %214 = fmul reassoc ninf nsz float %201, %213
  %215 = fmul reassoc ninf nsz float %202, %213
  %216 = fmul reassoc ninf nsz float %203, %213
  %217 = fmul reassoc ninf nsz float %210, %107
  %218 = fmul reassoc ninf nsz float %211, %107
  %219 = fmul reassoc ninf nsz float %212, %107
  %220 = fadd reassoc ninf nsz float %217, %214
  %221 = fadd reassoc ninf nsz float %218, %215
  %222 = fadd reassoc ninf nsz float %219, %216
  %223 = load ptr, ptr %54, align 8
  %224 = load i32, ptr %55, align 4
  %225 = sub i32 %224, %61
  %226 = mul i32 %225, 3
  %227 = mul i32 %226, %68
  %228 = add i32 %lsr.iv, %227
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, ptr %223, i64 %229
  store float %220, ptr %230, align 4
  %231 = load ptr, ptr %54, align 8
  %232 = load i32, ptr %55, align 4
  %233 = sub i32 %232, %61
  %234 = mul i32 %233, 3
  %235 = mul i32 %234, %68
  %236 = add i32 %lsr.iv, %235
  %237 = add i32 %236, 1
  %238 = sext i32 %237 to i64
  %239 = getelementptr float, ptr %231, i64 %238
  store float %221, ptr %239, align 4
  %240 = load ptr, ptr %54, align 8
  %241 = load i32, ptr %55, align 4
  %242 = sub i32 %241, %61
  %243 = mul i32 %242, 3
  %244 = mul i32 %243, %68
  %245 = add i32 %lsr.iv, %244
  %246 = add i32 %245, 2
  %247 = sext i32 %246 to i64
  %248 = getelementptr float, ptr %240, i64 %247
  store float %222, ptr %248, align 4
  %249 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %249
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
  %4 = alloca %struct.RuntimeContext.35, align 8
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
