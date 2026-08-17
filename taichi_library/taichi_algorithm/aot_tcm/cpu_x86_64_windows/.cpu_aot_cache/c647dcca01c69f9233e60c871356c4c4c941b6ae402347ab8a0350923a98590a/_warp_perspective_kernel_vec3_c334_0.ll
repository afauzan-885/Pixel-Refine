; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.27 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_warp_perspective_kernel_vec3_c334_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 56
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 60
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

define void @_warp_perspective_kernel_vec3_c334_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 48
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 52
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 24
  %25 = load ptr, ptr %24, align 8
  %26 = getelementptr i8, ptr %19, i64 20
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %25, i64 4
  %29 = getelementptr i8, ptr %25, i64 8
  %30 = sext i32 %27 to i64
  %31 = getelementptr float, ptr %25, i64 %30
  %32 = add i32 %27, 1
  %33 = sext i32 %32 to i64
  %34 = getelementptr float, ptr %25, i64 %33
  %35 = add i32 %27, 2
  %36 = sext i32 %35 to i64
  %37 = getelementptr float, ptr %25, i64 %36
  %38 = shl i32 %27, 1
  %39 = sext i32 %38 to i64
  %40 = getelementptr float, ptr %25, i64 %39
  %41 = getelementptr i8, ptr %40, i64 4
  %42 = add i32 %38, 2
  %43 = sext i32 %42 to i64
  %44 = getelementptr float, ptr %25, i64 %43
  %45 = add i32 %23, -1
  %46 = add i32 %21, -1
  %47 = icmp slt i32 %16, %18
  br i1 %47, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %48 = getelementptr i8, ptr %19, i64 8
  %49 = getelementptr i8, ptr %19, i64 4
  %50 = getelementptr i8, ptr %19, i64 40
  %51 = getelementptr i8, ptr %19, i64 36
  %52 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %52, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %243, %for_loop_body ]
  %53 = load ptr, ptr %3, align 8
  %54 = getelementptr inbounds nuw i8, ptr %53, i64 32872
  %55 = load ptr, ptr %54, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 4
  %57 = load i32, ptr %56, align 4
  %58 = sdiv i32 %.05, %57
  %59 = mul i32 %58, %57
  %60 = xor i32 %57, %.05
  %61 = icmp slt i32 %60, 0
  %62 = icmp ne i32 %.05, %59
  %63 = and i1 %61, %62
  %.neg4 = sext i1 %63 to i32
  %64 = add i32 %58, %.neg4
  %65 = mul i32 %57, -1
  %66 = mul i32 %65, %64
  %67 = add i32 %.05, %66
  %68 = load float, ptr %25, align 4
  %69 = sitofp i32 %67 to float
  %70 = fmul reassoc ninf nsz float %68, %69
  %71 = load float, ptr %28, align 4
  %72 = sitofp i32 %64 to float
  %73 = fmul reassoc ninf nsz float %71, %72
  %74 = load float, ptr %29, align 4
  %75 = fadd reassoc ninf nsz float %73, %74
  %76 = fadd reassoc ninf nsz float %75, %70
  %77 = load float, ptr %31, align 4
  %78 = fmul reassoc ninf nsz float %77, %69
  %79 = load float, ptr %34, align 4
  %80 = fmul reassoc ninf nsz float %79, %72
  %81 = load float, ptr %37, align 4
  %82 = fadd reassoc ninf nsz float %80, %81
  %83 = fadd reassoc ninf nsz float %82, %78
  %84 = load float, ptr %40, align 4
  %85 = fmul reassoc ninf nsz float %84, %69
  %86 = load float, ptr %41, align 4
  %87 = fmul reassoc ninf nsz float %86, %72
  %88 = load float, ptr %44, align 4
  %89 = fadd reassoc ninf nsz float %87, 0x3E112E0BE0000000
  %90 = fadd reassoc ninf nsz float %89, %85
  %91 = fadd reassoc ninf nsz float %90, %88
  %92 = fdiv reassoc ninf nsz float %76, %91
  %93 = fdiv reassoc ninf nsz float %83, %91
  %94 = tail call reassoc ninf nsz float @llvm.floor.f32(float %92)
  %95 = fptosi float %94 to i32
  %96 = tail call reassoc ninf nsz float @llvm.floor.f32(float %93)
  %97 = fptosi float %96 to i32
  %98 = sitofp i32 %95 to float
  %99 = fsub reassoc ninf nsz float %92, %98
  %100 = sitofp i32 %97 to float
  %101 = fsub reassoc ninf nsz float %93, %100
  %102 = tail call i32 @llvm.abs.i32(i32 %95, i1 true)
  %103 = sub i32 %102, %45
  %104 = tail call i32 @llvm.smax.i32(i32 %103, i32 0)
  %105 = shl nuw i32 %104, 1
  %106 = sub i32 %102, %105
  %107 = tail call i32 @llvm.smax.i32(i32 %106, i32 0)
  %108 = tail call i32 @llvm.smin.i32(i32 %45, i32 %107)
  %109 = tail call i32 @llvm.abs.i32(i32 %97, i1 true)
  %110 = sub i32 %109, %46
  %111 = tail call i32 @llvm.smax.i32(i32 %110, i32 0)
  %112 = shl nuw i32 %111, 1
  %113 = sub i32 %109, %112
  %114 = tail call i32 @llvm.smax.i32(i32 %113, i32 0)
  %115 = tail call i32 @llvm.smin.i32(i32 %46, i32 %114)
  %116 = add i32 %95, 1
  %117 = tail call i32 @llvm.abs.i32(i32 %116, i1 true)
  %118 = sub i32 %117, %45
  %119 = tail call i32 @llvm.smax.i32(i32 %118, i32 0)
  %120 = shl nuw i32 %119, 1
  %121 = sub i32 %117, %120
  %122 = tail call i32 @llvm.smax.i32(i32 %121, i32 0)
  %123 = tail call i32 @llvm.smin.i32(i32 %45, i32 %122)
  %124 = add i32 %97, 1
  %125 = tail call i32 @llvm.abs.i32(i32 %124, i1 true)
  %126 = sub i32 %125, %46
  %127 = tail call i32 @llvm.smax.i32(i32 %126, i32 0)
  %128 = shl nuw i32 %127, 1
  %129 = sub i32 %125, %128
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 0)
  %131 = tail call i32 @llvm.smin.i32(i32 %46, i32 %130)
  %132 = load ptr, ptr %48, align 8
  %133 = load i32, ptr %49, align 4
  %134 = mul i32 %115, %133
  %135 = add i32 %134, %108
  %136 = mul i32 %135, 3
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, ptr %132, i64 %137
  %139 = load float, ptr %138, align 4
  %140 = add i32 %136, 1
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %132, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = add i32 %136, 2
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %132, i64 %145
  %147 = load float, ptr %146, align 4
  %148 = add i32 %134, %123
  %149 = mul i32 %148, 3
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, ptr %132, i64 %150
  %152 = load float, ptr %151, align 4
  %153 = add i32 %149, 1
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %132, i64 %154
  %156 = load float, ptr %155, align 4
  %157 = add i32 %149, 2
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %132, i64 %158
  %160 = load float, ptr %159, align 4
  %161 = mul i32 %131, %133
  %162 = add i32 %161, %108
  %163 = mul i32 %162, 3
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %132, i64 %164
  %166 = load float, ptr %165, align 4
  %167 = add i32 %163, 1
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, ptr %132, i64 %168
  %170 = load float, ptr %169, align 4
  %171 = add i32 %163, 2
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, ptr %132, i64 %172
  %174 = load float, ptr %173, align 4
  %175 = add i32 %161, %123
  %176 = mul i32 %175, 3
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, ptr %132, i64 %177
  %179 = load float, ptr %178, align 4
  %180 = add i32 %176, 1
  %181 = sext i32 %180 to i64
  %182 = getelementptr float, ptr %132, i64 %181
  %183 = load float, ptr %182, align 4
  %184 = add i32 %176, 2
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, ptr %132, i64 %185
  %187 = load float, ptr %186, align 4
  %188 = fsub reassoc ninf nsz float 1.000000e+00, %99
  %189 = fmul reassoc ninf nsz float %188, %139
  %190 = fmul reassoc ninf nsz float %188, %143
  %191 = fmul reassoc ninf nsz float %188, %147
  %192 = fmul reassoc ninf nsz float %99, %152
  %193 = fmul reassoc ninf nsz float %99, %156
  %194 = fmul reassoc ninf nsz float %160, %99
  %195 = fadd reassoc ninf nsz float %189, %192
  %196 = fadd reassoc ninf nsz float %190, %193
  %197 = fadd reassoc ninf nsz float %191, %194
  %198 = fmul reassoc ninf nsz float %166, %188
  %199 = fmul reassoc ninf nsz float %170, %188
  %200 = fmul reassoc ninf nsz float %174, %188
  %201 = fmul reassoc ninf nsz float %179, %99
  %202 = fmul reassoc ninf nsz float %183, %99
  %203 = fmul reassoc ninf nsz float %187, %99
  %204 = fadd reassoc ninf nsz float %201, %198
  %205 = fadd reassoc ninf nsz float %202, %199
  %206 = fadd reassoc ninf nsz float %203, %200
  %207 = fsub reassoc ninf nsz float 1.000000e+00, %101
  %208 = fmul reassoc ninf nsz float %195, %207
  %209 = fmul reassoc ninf nsz float %196, %207
  %210 = fmul reassoc ninf nsz float %197, %207
  %211 = fmul reassoc ninf nsz float %204, %101
  %212 = fmul reassoc ninf nsz float %205, %101
  %213 = fmul reassoc ninf nsz float %206, %101
  %214 = fadd reassoc ninf nsz float %211, %208
  %215 = fadd reassoc ninf nsz float %212, %209
  %216 = fadd reassoc ninf nsz float %213, %210
  %217 = load ptr, ptr %50, align 8
  %218 = load i32, ptr %51, align 4
  %219 = sub i32 %218, %57
  %220 = mul i32 %219, 3
  %221 = mul i32 %220, %64
  %222 = add i32 %lsr.iv, %221
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, ptr %217, i64 %223
  store float %214, ptr %224, align 4
  %225 = load ptr, ptr %50, align 8
  %226 = load i32, ptr %51, align 4
  %227 = sub i32 %226, %57
  %228 = mul i32 %227, 3
  %229 = mul i32 %228, %64
  %230 = add i32 %lsr.iv, %229
  %231 = add i32 %230, 1
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, ptr %225, i64 %232
  store float %215, ptr %233, align 4
  %234 = load ptr, ptr %50, align 8
  %235 = load i32, ptr %51, align 4
  %236 = sub i32 %235, %57
  %237 = mul i32 %236, 3
  %238 = mul i32 %237, %64
  %239 = add i32 %lsr.iv, %238
  %240 = add i32 %239, 2
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, ptr %234, i64 %241
  store float %216, ptr %242, align 4
  %243 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %243
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
  %4 = alloca %struct.RuntimeContext.27, align 8
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
