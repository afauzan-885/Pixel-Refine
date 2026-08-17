; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.21 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_remap_with_flow_batch_kernel_c326_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 72
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 84
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 16
  store i32 %5, ptr %10, align 4
  %11 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %12 = load ptr, ptr %context, align 8
  %13 = getelementptr i8, ptr %12, i64 88
  %14 = load i32, ptr %13, align 4
  %15 = load ptr, ptr %6, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 32872
  %17 = load ptr, ptr %16, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 12
  store i32 %14, ptr %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %14, i32 0)
  %20 = load ptr, ptr %6, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 8
  store i32 %19, ptr %23, align 4
  %24 = mul i32 %19, %11
  %25 = load ptr, ptr %6, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 4
  store i32 %24, ptr %28, align 4
  %29 = mul i32 %24, %3
  %30 = load ptr, ptr %6, align 8
  %31 = getelementptr inbounds nuw i8, ptr %30, i64 32872
  %32 = load ptr, ptr %31, align 8
  store i32 %29, ptr %32, align 4
  ret void
}

define void @_remap_with_flow_batch_kernel_c326_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 96
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 92
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 100
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 104
  %27 = load float, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 80
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 76
  %31 = load i32, ptr %30, align 4
  %32 = add i32 %21, -1
  %33 = add i32 %23, -1
  %34 = add i32 %29, -1
  %35 = add i32 %31, -1
  %36 = sitofp i32 %32 to float
  %37 = sitofp i32 %33 to float
  %38 = icmp slt i32 %16, %18
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr i8, ptr %19, i64 40
  %40 = getelementptr i8, ptr %19, i64 28
  %41 = getelementptr i8, ptr %19, i64 32
  %42 = getelementptr i8, ptr %19, i64 36
  %43 = getelementptr i8, ptr %19, i64 16
  %44 = getelementptr i8, ptr %19, i64 4
  %45 = getelementptr i8, ptr %19, i64 8
  %46 = getelementptr i8, ptr %19, i64 64
  %47 = getelementptr i8, ptr %19, i64 52
  %48 = getelementptr i8, ptr %19, i64 56
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.07 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %235, %for_loop_body ]
  %49 = load ptr, ptr %3, align 8
  %50 = getelementptr inbounds nuw i8, ptr %49, i64 32872
  %51 = load ptr, ptr %50, align 8
  %52 = getelementptr inbounds nuw i8, ptr %51, i64 4
  %53 = load i32, ptr %52, align 4
  %54 = sdiv i32 %.07, %53
  %55 = mul i32 %54, %53
  %56 = xor i32 %53, %.07
  %57 = icmp slt i32 %56, 0
  %58 = icmp ne i32 %.07, %55
  %59 = and i1 %57, %58
  %.neg4 = sext i1 %59 to i32
  %60 = add i32 %54, %.neg4
  %61 = mul i32 %60, %53
  %62 = mul i32 %53, -1
  %63 = mul i32 %62, %60
  %64 = add i32 %.07, %63
  %65 = getelementptr inbounds nuw i8, ptr %51, i64 8
  %66 = load i32, ptr %65, align 4
  %67 = sdiv i32 %64, %66
  %68 = mul i32 %67, %66
  %69 = xor i32 %64, %66
  %70 = icmp slt i32 %69, 0
  %71 = icmp ne i32 %.07, %61
  %72 = icmp ne i32 %64, %68
  %73 = and i1 %71, %70
  %74 = and i1 %72, %73
  %.neg5 = sext i1 %74 to i32
  %75 = add i32 %67, %.neg5
  %76 = mul i32 %75, %66
  %77 = mul i32 %66, -1
  %78 = mul i32 %77, %75
  %79 = add i32 %64, %78
  %80 = sitofp i32 %79 to float
  %81 = fmul reassoc ninf nsz float %80, %36
  %82 = getelementptr inbounds nuw i8, ptr %51, i64 12
  %83 = load i32, ptr %82, align 4
  %84 = add i32 %83, -1
  %85 = sitofp i32 %84 to float
  %86 = fdiv reassoc ninf nsz float %81, %85
  %87 = sitofp i32 %75 to float
  %88 = fmul reassoc ninf nsz float %87, %37
  %89 = getelementptr inbounds nuw i8, ptr %51, i64 16
  %90 = load i32, ptr %89, align 4
  %91 = add i32 %90, -1
  %92 = sitofp i32 %91 to float
  %93 = fdiv reassoc ninf nsz float %88, %92
  %94 = tail call reassoc ninf nsz float @llvm.floor.f32(float %86)
  %95 = fptosi float %94 to i32
  %96 = tail call reassoc ninf nsz float @llvm.floor.f32(float %93)
  %97 = fptosi float %96 to i32
  %98 = add i32 %95, 1
  %99 = tail call i32 @llvm.smin.i32(i32 %98, i32 %32)
  %100 = add i32 %97, 1
  %101 = tail call i32 @llvm.smin.i32(i32 %100, i32 %33)
  %102 = sitofp i32 %95 to float
  %103 = fsub reassoc ninf nsz float %86, %102
  %104 = sitofp i32 %97 to float
  %105 = fsub reassoc ninf nsz float %93, %104
  %106 = load ptr, ptr %39, align 8
  %107 = load i32, ptr %40, align 4
  %108 = load i32, ptr %41, align 4
  %109 = load i32, ptr %42, align 4
  %110 = mul i32 %107, %60
  %111 = add i32 %110, %97
  %112 = mul i32 %111, %108
  %113 = add i32 %112, %95
  %114 = mul i32 %113, %109
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %106, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = add i32 %99, %112
  %119 = mul i32 %118, %109
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %106, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = add i32 %101, %110
  %124 = mul i32 %123, %108
  %125 = add i32 %124, %95
  %126 = mul i32 %125, %109
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %106, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = add i32 %124, %99
  %131 = mul i32 %130, %109
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, ptr %106, i64 %132
  %134 = load float, ptr %133, align 4
  %135 = add i32 %114, 1
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %106, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = add i32 %119, 1
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %106, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = add i32 %126, 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %106, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %131, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %106, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = fsub reassoc ninf nsz float 1.000000e+00, %103
  %152 = fmul reassoc ninf nsz float %151, %117
  %153 = fmul reassoc ninf nsz float %103, %122
  %154 = fadd reassoc ninf nsz float %152, %153
  %155 = fsub reassoc ninf nsz float 1.000000e+00, %105
  %156 = fmul reassoc ninf nsz float %154, %155
  %157 = fmul reassoc ninf nsz float %151, %129
  %158 = fmul reassoc ninf nsz float %103, %134
  %159 = fadd reassoc ninf nsz float %157, %158
  %160 = fmul reassoc ninf nsz float %159, %105
  %161 = fadd reassoc ninf nsz float %156, %160
  %162 = fmul reassoc ninf nsz float %151, %138
  %163 = fmul reassoc ninf nsz float %103, %142
  %164 = fadd reassoc ninf nsz float %162, %163
  %165 = fmul reassoc ninf nsz float %164, %155
  %166 = fmul reassoc ninf nsz float %151, %146
  %167 = fmul reassoc ninf nsz float %103, %150
  %168 = fadd reassoc ninf nsz float %166, %167
  %169 = fmul reassoc ninf nsz float %168, %105
  %170 = fadd reassoc ninf nsz float %165, %169
  %171 = fmul reassoc ninf nsz float %161, %25
  %172 = fadd reassoc ninf nsz float %171, %80
  %173 = fmul reassoc ninf nsz float %170, %27
  %174 = fadd reassoc ninf nsz float %173, %87
  %175 = tail call reassoc ninf nsz float @llvm.floor.f32(float %172)
  %176 = fptosi float %175 to i32
  %177 = tail call reassoc ninf nsz float @llvm.floor.f32(float %174)
  %178 = fptosi float %177 to i32
  %179 = sitofp i32 %176 to float
  %180 = fsub reassoc ninf nsz float %172, %179
  %181 = sitofp i32 %178 to float
  %182 = fsub reassoc ninf nsz float %174, %181
  %183 = tail call i32 @llvm.smax.i32(i32 %176, i32 0)
  %184 = tail call i32 @llvm.smin.i32(i32 %183, i32 %34)
  %185 = tail call i32 @llvm.smax.i32(i32 %178, i32 0)
  %186 = tail call i32 @llvm.smin.i32(i32 %185, i32 %35)
  %187 = add i32 %184, 1
  %188 = tail call i32 @llvm.smin.i32(i32 %187, i32 %34)
  %189 = add i32 %186, 1
  %190 = tail call i32 @llvm.smin.i32(i32 %189, i32 %35)
  %191 = load ptr, ptr %43, align 8
  %192 = load i32, ptr %44, align 4
  %193 = load i32, ptr %45, align 4
  %194 = mul i32 %192, %60
  %195 = add i32 %186, %194
  %196 = mul i32 %195, %193
  %197 = add i32 %196, %184
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %191, i64 %198
  %200 = load float, ptr %199, align 4
  %201 = add i32 %196, %188
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %191, i64 %202
  %204 = load float, ptr %203, align 4
  %205 = add i32 %190, %194
  %206 = mul i32 %205, %193
  %207 = add i32 %206, %184
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, ptr %191, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = add i32 %206, %188
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %191, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = fsub reassoc ninf nsz float 1.000000e+00, %180
  %216 = fmul reassoc ninf nsz float %215, %200
  %217 = fmul reassoc ninf nsz float %180, %204
  %218 = fadd reassoc ninf nsz float %216, %217
  %219 = fmul reassoc ninf nsz float %215, %210
  %220 = fmul reassoc ninf nsz float %180, %214
  %221 = fadd reassoc ninf nsz float %219, %220
  %222 = fsub reassoc ninf nsz float %221, %218
  %223 = fmul reassoc ninf nsz float %222, %182
  %224 = fadd reassoc ninf nsz float %223, %218
  %225 = load ptr, ptr %46, align 8
  %226 = load i32, ptr %47, align 4
  %227 = load i32, ptr %48, align 4
  %228 = mul i32 %226, %60
  %229 = add i32 %228, %75
  %230 = mul i32 %229, %227
  %231 = sub i32 %230, %76
  %232 = add i32 %64, %231
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, ptr %225, i64 %233
  store float %224, ptr %234, align 4
  %235 = add nsw i32 %.07, 1
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
  %4 = alloca %struct.RuntimeContext.21, align 8
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
