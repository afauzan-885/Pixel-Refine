; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.9 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bilinear_resize_batch_offset_kernel_vec3_c142_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 16
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 20
  %5 = load i32, ptr %4, align 4
  %6 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %7 = getelementptr i8, ptr %0, i64 24
  %8 = load i32, ptr %7, align 4
  %9 = tail call i32 @llvm.smax.i32(i32 %8, i32 0)
  %10 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %11 = load ptr, ptr %10, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 32872
  %13 = load ptr, ptr %12, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 8
  store i32 %9, ptr %14, align 4
  %15 = mul i32 %9, %6
  %16 = load ptr, ptr %10, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 32872
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 4
  store i32 %15, ptr %19, align 4
  %20 = mul i32 %15, %3
  %21 = load ptr, ptr %10, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  store i32 %20, ptr %23, align 4
  ret void
}

define void @_bilinear_resize_batch_offset_kernel_vec3_c142_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 64
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 60
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 68
  %27 = load i32, ptr %26, align 4
  %28 = sitofp i32 %21 to float
  %29 = sitofp i32 %23 to float
  %30 = sitofp i32 %25 to float
  %31 = sitofp i32 %27 to float
  %32 = add i32 %21, -1
  %33 = add i32 %25, -1
  %34 = icmp slt i32 %16, %18
  br i1 %34, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %35 = getelementptr i8, ptr %19, i64 48
  %36 = getelementptr i8, ptr %19, i64 44
  %37 = getelementptr i8, ptr %19, i64 8
  %38 = getelementptr i8, ptr %19, i64 4
  %39 = getelementptr i8, ptr %19, i64 32
  %40 = getelementptr i8, ptr %19, i64 20
  %41 = getelementptr i8, ptr %19, i64 24
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.06 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %235, %for_loop_body ]
  %42 = load ptr, ptr %3, align 8
  %43 = getelementptr inbounds nuw i8, ptr %42, i64 32872
  %44 = load ptr, ptr %43, align 8
  %45 = getelementptr inbounds nuw i8, ptr %44, i64 4
  %46 = load i32, ptr %45, align 4
  %47 = sdiv i32 %.06, %46
  %48 = mul i32 %47, %46
  %49 = xor i32 %46, %.06
  %50 = icmp slt i32 %49, 0
  %51 = icmp ne i32 %.06, %48
  %52 = and i1 %50, %51
  %.neg4 = sext i1 %52 to i32
  %53 = add i32 %47, %.neg4
  %54 = mul i32 %53, %46
  %55 = mul i32 %46, -1
  %56 = mul i32 %55, %53
  %57 = add i32 %.06, %56
  %58 = getelementptr inbounds nuw i8, ptr %44, i64 8
  %59 = load i32, ptr %58, align 4
  %60 = sdiv i32 %57, %59
  %61 = mul i32 %60, %59
  %62 = xor i32 %57, %59
  %63 = icmp slt i32 %62, 0
  %64 = icmp ne i32 %.06, %54
  %65 = icmp ne i32 %57, %61
  %66 = and i1 %64, %63
  %67 = and i1 %65, %66
  %.neg5 = sext i1 %67 to i32
  %68 = add i32 %60, %.neg5
  %69 = mul i32 %68, %59
  %70 = load ptr, ptr %35, align 8
  %71 = load i32, ptr %36, align 4
  %72 = mul i32 %53, %71
  %73 = sext i32 %72 to i64
  %74 = getelementptr i32, ptr %70, i64 %73
  %75 = load i32, ptr %74, align 4
  %76 = add i32 %68, %75
  %77 = add i32 %72, 1
  %78 = sext i32 %77 to i64
  %79 = getelementptr i32, ptr %70, i64 %78
  %80 = load i32, ptr %79, align 4
  %81 = sub i32 %80, %69
  %82 = sub i32 %81, %54
  %83 = add i32 %.06, %82
  %84 = sitofp i32 %76 to float
  %85 = fadd reassoc ninf nsz float %84, 5.000000e-01
  %86 = fmul reassoc ninf nsz float %85, %28
  %87 = fdiv reassoc ninf nsz float %86, %29
  %88 = fadd reassoc ninf nsz float %87, -5.000000e-01
  %89 = sitofp i32 %83 to float
  %90 = fadd reassoc ninf nsz float %89, 5.000000e-01
  %91 = fmul reassoc ninf nsz float %90, %30
  %92 = fdiv reassoc ninf nsz float %91, %31
  %93 = fadd reassoc ninf nsz float %92, -5.000000e-01
  %94 = tail call reassoc ninf nsz float @llvm.floor.f32(float %88)
  %95 = fptosi float %94 to i32
  %96 = tail call reassoc ninf nsz float @llvm.floor.f32(float %93)
  %97 = fptosi float %96 to i32
  %98 = sitofp i32 %95 to float
  %99 = fsub reassoc ninf nsz float %88, %98
  %100 = sitofp i32 %97 to float
  %101 = fsub reassoc ninf nsz float %93, %100
  %102 = add i32 %95, 1
  %103 = tail call i32 @llvm.smax.i32(i32 %95, i32 0)
  %104 = tail call i32 @llvm.smin.i32(i32 %32, i32 %103)
  %105 = tail call i32 @llvm.smax.i32(i32 %102, i32 0)
  %106 = tail call i32 @llvm.smin.i32(i32 %32, i32 %105)
  %107 = add i32 %97, 1
  %108 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %109 = tail call i32 @llvm.smin.i32(i32 %33, i32 %108)
  %110 = tail call i32 @llvm.smax.i32(i32 %107, i32 0)
  %111 = tail call i32 @llvm.smin.i32(i32 %33, i32 %110)
  %112 = load ptr, ptr %37, align 8
  %113 = load i32, ptr %38, align 4
  %114 = mul i32 %104, %113
  %115 = add i32 %109, %114
  %116 = mul i32 %115, 3
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %112, i64 %117
  %119 = load float, ptr %118, align 4
  %120 = add i32 %116, 1
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %112, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = add i32 %116, 2
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %112, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = add i32 %111, %114
  %129 = mul i32 %128, 3
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %112, i64 %130
  %132 = load float, ptr %131, align 4
  %133 = add i32 %129, 1
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %112, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = add i32 %129, 2
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %112, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = mul i32 %106, %113
  %142 = add i32 %141, %109
  %143 = mul i32 %142, 3
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %112, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %143, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %112, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = add i32 %143, 2
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %112, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = add i32 %111, %141
  %156 = mul i32 %155, 3
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %112, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = add i32 %156, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %112, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = add i32 %156, 2
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %112, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = fsub reassoc ninf nsz float 1.000000e+00, %101
  %169 = fmul reassoc ninf nsz float %168, %119
  %170 = fmul reassoc ninf nsz float %168, %123
  %171 = fmul reassoc ninf nsz float %168, %127
  %172 = fmul reassoc ninf nsz float %101, %132
  %173 = fmul reassoc ninf nsz float %101, %136
  %174 = fmul reassoc ninf nsz float %101, %140
  %175 = fadd reassoc ninf nsz float %169, %172
  %176 = fadd reassoc ninf nsz float %170, %173
  %177 = fadd reassoc ninf nsz float %171, %174
  %178 = fmul reassoc ninf nsz float %168, %146
  %179 = fmul reassoc ninf nsz float %168, %150
  %180 = fmul reassoc ninf nsz float %168, %154
  %181 = fmul reassoc ninf nsz float %101, %159
  %182 = fmul reassoc ninf nsz float %101, %163
  %183 = fmul reassoc ninf nsz float %101, %167
  %184 = fadd reassoc ninf nsz float %178, %181
  %185 = fadd reassoc ninf nsz float %179, %182
  %186 = fadd reassoc ninf nsz float %180, %183
  %187 = fsub reassoc ninf nsz float 1.000000e+00, %99
  %188 = fmul reassoc ninf nsz float %175, %187
  %189 = fmul reassoc ninf nsz float %176, %187
  %190 = fmul reassoc ninf nsz float %177, %187
  %191 = fmul reassoc ninf nsz float %184, %99
  %192 = fmul reassoc ninf nsz float %185, %99
  %193 = fmul reassoc ninf nsz float %186, %99
  %194 = fadd reassoc ninf nsz float %188, %191
  %195 = fadd reassoc ninf nsz float %189, %192
  %196 = fadd reassoc ninf nsz float %190, %193
  %197 = load ptr, ptr %39, align 8
  %198 = load i32, ptr %40, align 4
  %199 = load i32, ptr %41, align 4
  %200 = mul i32 %198, %53
  %201 = add i32 %200, %68
  %202 = mul i32 %201, %199
  %203 = sub i32 %202, %69
  %204 = sub i32 %203, %54
  %205 = add i32 %.06, %204
  %206 = mul i32 %205, 3
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, ptr %197, i64 %207
  store float %194, ptr %208, align 4
  %209 = load ptr, ptr %39, align 8
  %210 = load i32, ptr %40, align 4
  %211 = load i32, ptr %41, align 4
  %212 = mul i32 %210, %53
  %213 = add i32 %212, %68
  %214 = mul i32 %213, %211
  %215 = sub i32 %214, %69
  %216 = sub i32 %215, %54
  %217 = add i32 %.06, %216
  %218 = mul i32 %217, 3
  %219 = add i32 %218, 1
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, ptr %209, i64 %220
  store float %195, ptr %221, align 4
  %222 = load ptr, ptr %39, align 8
  %223 = load i32, ptr %40, align 4
  %224 = load i32, ptr %41, align 4
  %225 = mul i32 %223, %53
  %226 = add i32 %225, %68
  %227 = mul i32 %226, %224
  %228 = sub i32 %227, %69
  %229 = sub i32 %228, %54
  %230 = add i32 %.06, %229
  %231 = mul i32 %230, 3
  %232 = add i32 %231, 2
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %222, i64 %233
  store float %196, ptr %234, align 4
  %235 = add nsw i32 %.06, 1
  %exitcond.not = icmp eq i32 %18, %235
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
  %4 = alloca %struct.RuntimeContext.9, align 8
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
