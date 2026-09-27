; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @precompute_gradients_pair_kernel_c736_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 96
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 100
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

define void @precompute_gradients_pair_kernel_c736_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #6
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
  %19 = icmp slt i32 %16, %18
  br i1 %19, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.preheader
  %.0821 = phi i32 [ %234, %after_if9 ], [ %16, %for_loop_body.preheader ]
  %20 = load ptr, ptr %3, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 32872
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds nuw i8, ptr %22, i64 4
  %24 = load i32, ptr %23, align 4
  %25 = sdiv i32 %.0821, %24
  %26 = mul i32 %25, %24
  %27 = xor i32 %24, %.0821
  %28 = icmp slt i32 %27, 0
  %29 = icmp ne i32 %.0821, %26
  %30 = and i1 %28, %29
  %.neg13 = sext i1 %30 to i32
  %31 = add i32 %25, %.neg13
  %32 = mul i32 %31, %24
  %33 = mul i32 %24, -1
  %34 = mul i32 %33, %31
  %35 = add i32 %.0821, %34
  %36 = icmp sgt i32 %31, 0
  br i1 %36, label %true_block, label %false_block8

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %37 = getelementptr inbounds nuw i8, ptr %22, i64 8
  %38 = load i32, ptr %37, align 4
  %39 = add i32 %38, -1
  %40 = icmp slt i32 %31, %39
  %41 = icmp sgt i32 %35, 0
  %or.cond = and i1 %41, %40
  br i1 %or.cond, label %true_block4, label %false_block8

true_block4:                                      ; preds = %true_block
  %42 = getelementptr inbounds nuw i8, ptr %22, i64 12
  %43 = load i32, ptr %42, align 4
  %44 = add i32 %43, -1
  %45 = icmp slt i32 %35, %44
  br i1 %45, label %true_block7, label %false_block8

true_block7:                                      ; preds = %true_block4
  %46 = load ptr, ptr %0, align 8
  %47 = getelementptr i8, ptr %46, i64 8
  %48 = load ptr, ptr %47, align 8
  %49 = getelementptr i8, ptr %46, i64 4
  %50 = load i32, ptr %49, align 4
  %51 = sub i32 %50, %24
  %52 = mul i32 %51, %31
  %53 = add i32 %.0821, %52
  %54 = add i32 %53, 1
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, ptr %48, i64 %55
  %57 = load float, ptr %56, align 4
  %58 = add i32 %53, -1
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, ptr %48, i64 %59
  %61 = load float, ptr %60, align 4
  %62 = add nsw i32 %31, -1
  %63 = mul i32 %50, %62
  %64 = sub i32 %63, %32
  %65 = add i32 %.0821, %64
  %66 = add i32 %65, 1
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, ptr %48, i64 %67
  %69 = load float, ptr %68, align 4
  %70 = add i32 %65, -1
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, ptr %48, i64 %71
  %73 = load float, ptr %72, align 4
  %74 = add nuw nsw i32 %31, 1
  %75 = mul i32 %50, %74
  %76 = sub i32 %75, %32
  %77 = add i32 %.0821, %76
  %78 = add i32 %77, 1
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, ptr %48, i64 %79
  %81 = load float, ptr %80, align 4
  %82 = add i32 %77, -1
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, ptr %48, i64 %83
  %85 = load float, ptr %84, align 4
  %86 = fadd reassoc ninf nsz float %57, %69
  %87 = fadd reassoc ninf nsz float %61, %73
  %88 = fadd reassoc ninf nsz float %86, %81
  %89 = fadd reassoc ninf nsz float %87, %85
  %90 = fsub reassoc ninf nsz float %88, %89
  %91 = fmul reassoc ninf nsz float %90, 0x3FD54FDF40000000
  %92 = getelementptr i8, ptr %46, i64 40
  %93 = load ptr, ptr %92, align 8
  %94 = getelementptr i8, ptr %46, i64 36
  %95 = load i32, ptr %94, align 4
  %96 = sub i32 %95, %24
  %97 = mul i32 %96, %31
  %98 = add i32 %.0821, %97
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %93, i64 %99
  store float %91, ptr %100, align 4
  %101 = load ptr, ptr %47, align 8
  %102 = load i32, ptr %49, align 4
  %103 = mul i32 %102, %74
  %104 = sub i32 %103, %32
  %105 = add i32 %.0821, %104
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, ptr %101, i64 %106
  %108 = load float, ptr %107, align 4
  %109 = mul i32 %102, %62
  %110 = sub i32 %109, %32
  %111 = add i32 %.0821, %110
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %101, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = fsub reassoc ninf nsz float %108, %114
  %116 = load ptr, ptr %0, align 8
  %117 = getelementptr i8, ptr %116, i64 56
  %118 = load ptr, ptr %117, align 8
  %119 = getelementptr i8, ptr %116, i64 52
  %120 = load i32, ptr %119, align 4
  %121 = sub i32 %120, %24
  %122 = mul i32 %121, %31
  %123 = add i32 %.0821, %122
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %118, i64 %124
  store float %115, ptr %125, align 4
  %126 = load ptr, ptr %0, align 8
  %127 = getelementptr i8, ptr %126, i64 24
  %128 = load ptr, ptr %127, align 8
  %129 = getelementptr i8, ptr %126, i64 20
  %130 = load i32, ptr %129, align 4
  %131 = sub i32 %130, %24
  %132 = mul i32 %131, %31
  %133 = add i32 %.0821, %132
  %134 = add i32 %133, 1
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, ptr %128, i64 %135
  %137 = load float, ptr %136, align 4
  %138 = add i32 %133, -1
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, ptr %128, i64 %139
  %141 = load float, ptr %140, align 4
  %142 = mul i32 %130, %62
  %143 = sub i32 %142, %32
  %144 = add i32 %.0821, %143
  %145 = add i32 %144, 1
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, ptr %128, i64 %146
  %148 = load float, ptr %147, align 4
  %149 = add i32 %144, -1
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, ptr %128, i64 %150
  %152 = load float, ptr %151, align 4
  %153 = mul i32 %130, %74
  %154 = sub i32 %153, %32
  %155 = add i32 %.0821, %154
  %156 = add i32 %155, 1
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %128, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = add i32 %155, -1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %128, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = fadd reassoc ninf nsz float %137, %148
  %165 = fadd reassoc ninf nsz float %141, %152
  %166 = fadd reassoc ninf nsz float %164, %159
  %167 = fadd reassoc ninf nsz float %165, %163
  %168 = fsub reassoc ninf nsz float %166, %167
  %169 = fmul reassoc ninf nsz float %168, 0x3FD54FDF40000000
  %170 = getelementptr i8, ptr %126, i64 72
  %171 = load ptr, ptr %170, align 8
  %172 = getelementptr i8, ptr %126, i64 68
  %173 = load i32, ptr %172, align 4
  %174 = sub i32 %173, %24
  %175 = mul i32 %174, %31
  %176 = add i32 %.0821, %175
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, ptr %171, i64 %177
  store float %169, ptr %178, align 4
  %179 = load ptr, ptr %127, align 8
  %180 = load i32, ptr %129, align 4
  %181 = mul i32 %180, %74
  %182 = sub i32 %181, %32
  %183 = add i32 %.0821, %182
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, ptr %179, i64 %184
  %186 = load float, ptr %185, align 4
  %187 = mul i32 %180, %62
  %188 = sub i32 %187, %32
  %189 = add i32 %.0821, %188
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, ptr %179, i64 %190
  %192 = load float, ptr %191, align 4
  %193 = fsub reassoc ninf nsz float %186, %192
  br label %after_if9

false_block8:                                     ; preds = %true_block4, %true_block, %for_loop_body
  %194 = load ptr, ptr %0, align 8
  %195 = getelementptr i8, ptr %194, i64 40
  %196 = load ptr, ptr %195, align 8
  %197 = getelementptr i8, ptr %194, i64 36
  %198 = load i32, ptr %197, align 4
  %199 = sub i32 %198, %24
  %200 = mul i32 %199, %31
  %201 = add i32 %.0821, %200
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %196, i64 %202
  store float 0.000000e+00, ptr %203, align 4
  %204 = load ptr, ptr %0, align 8
  %205 = getelementptr i8, ptr %204, i64 56
  %206 = load ptr, ptr %205, align 8
  %207 = getelementptr i8, ptr %204, i64 52
  %208 = load i32, ptr %207, align 4
  %209 = sub i32 %208, %24
  %210 = mul i32 %209, %31
  %211 = add i32 %.0821, %210
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, ptr %206, i64 %212
  store float 0.000000e+00, ptr %213, align 4
  %214 = load ptr, ptr %0, align 8
  %215 = getelementptr i8, ptr %214, i64 72
  %216 = load ptr, ptr %215, align 8
  %217 = getelementptr i8, ptr %214, i64 68
  %218 = load i32, ptr %217, align 4
  %219 = sub i32 %218, %24
  %220 = mul i32 %219, %31
  %221 = add i32 %.0821, %220
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, ptr %216, i64 %222
  store float 0.000000e+00, ptr %223, align 4
  br label %after_if9

after_if9:                                        ; preds = %false_block8, %true_block7
  %.sink = phi float [ 0.000000e+00, %false_block8 ], [ %193, %true_block7 ]
  %224 = load ptr, ptr %0, align 8
  %225 = getelementptr i8, ptr %224, i64 88
  %226 = load ptr, ptr %225, align 8
  %227 = getelementptr i8, ptr %224, i64 84
  %228 = load i32, ptr %227, align 4
  %229 = sub i32 %228, %24
  %230 = mul i32 %229, %31
  %231 = add i32 %.0821, %230
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, ptr %226, i64 %232
  store float %.sink, ptr %233, align 4
  %234 = add nsw i32 %.0821, 1
  %exitcond.not = icmp eq i32 %18, %234
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #6
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #6
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
