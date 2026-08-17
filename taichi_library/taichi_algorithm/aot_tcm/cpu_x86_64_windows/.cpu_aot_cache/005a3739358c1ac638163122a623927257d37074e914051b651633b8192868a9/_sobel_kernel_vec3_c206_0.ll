; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_sobel_kernel_vec3_c206_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 52
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

define void @_sobel_kernel_vec3_c206_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  br i1 %19, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %20 = load ptr, ptr %0, align 8
  %21 = getelementptr i8, ptr %20, i64 8
  %22 = getelementptr i8, ptr %20, i64 4
  %23 = getelementptr i8, ptr %20, i64 24
  %24 = getelementptr i8, ptr %20, i64 20
  %25 = getelementptr i8, ptr %20, i64 40
  %26 = getelementptr i8, ptr %20, i64 36
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.064 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %220, %for_loop_body ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.064, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.064
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.064, %33
  %37 = and i1 %35, %36
  %.neg4 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg4
  %39 = mul i32 %38, %31
  %40 = add i32 %38, -1
  %41 = getelementptr inbounds nuw i8, ptr %29, i64 8
  %42 = load i32, ptr %41, align 4
  %43 = add i32 %42, -1
  %44 = mul i32 %31, -1
  %45 = mul i32 %44, %38
  %46 = add i32 %.064, %45
  %47 = add i32 %46, -1
  %48 = getelementptr inbounds nuw i8, ptr %29, i64 12
  %49 = load i32, ptr %48, align 4
  %50 = add i32 %49, -1
  %51 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %52 = tail call i32 @llvm.smin.i32(i32 %43, i32 %51)
  %53 = tail call i32 @llvm.smax.i32(i32 %47, i32 0)
  %54 = tail call i32 @llvm.smin.i32(i32 %50, i32 %53)
  %55 = load ptr, ptr %21, align 8
  %56 = load i32, ptr %22, align 4
  %57 = mul i32 %52, %56
  %58 = add i32 %54, %57
  %59 = mul i32 %58, 3
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %55, i64 %60
  %62 = load float, ptr %61, align 4
  %63 = add i32 %59, 1
  %64 = sext i32 %63 to i64
  %65 = getelementptr float, ptr %55, i64 %64
  %66 = load float, ptr %65, align 4
  %67 = add i32 %59, 2
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %55, i64 %68
  %70 = load float, ptr %69, align 4
  %71 = sub i32 %57, %39
  %72 = add i32 %.064, %71
  %73 = mul i32 %72, 3
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, ptr %55, i64 %74
  %76 = load float, ptr %75, align 4
  %77 = add i32 %73, 1
  %78 = sext i32 %77 to i64
  %79 = getelementptr float, ptr %55, i64 %78
  %80 = load float, ptr %79, align 4
  %81 = add i32 %73, 2
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, ptr %55, i64 %82
  %84 = load float, ptr %83, align 4
  %85 = add i32 %46, 1
  %86 = tail call i32 @llvm.smax.i32(i32 %85, i32 0)
  %87 = tail call i32 @llvm.smin.i32(i32 %50, i32 %86)
  %88 = add i32 %87, %57
  %89 = mul i32 %88, 3
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %55, i64 %90
  %92 = load float, ptr %91, align 4
  %93 = add i32 %89, 1
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %55, i64 %94
  %96 = load float, ptr %95, align 4
  %97 = add i32 %89, 2
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %55, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = mul i32 %38, %56
  %102 = add i32 %54, %101
  %103 = mul i32 %102, 3
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %55, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = add i32 %103, 1
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, ptr %55, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = add i32 %103, 2
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %55, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = add i32 %87, %101
  %116 = mul i32 %115, 3
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %55, i64 %117
  %119 = load float, ptr %118, align 4
  %120 = add i32 %116, 1
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %55, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = add i32 %116, 2
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %55, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = add i32 %38, 1
  %129 = tail call i32 @llvm.smax.i32(i32 %128, i32 0)
  %130 = tail call i32 @llvm.smin.i32(i32 %43, i32 %129)
  %131 = mul i32 %130, %56
  %132 = add i32 %54, %131
  %133 = mul i32 %132, 3
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %55, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = add i32 %133, 1
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %55, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = add i32 %133, 2
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %55, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = sub i32 %131, %39
  %146 = add i32 %.064, %145
  %147 = mul i32 %146, 3
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %55, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = add i32 %147, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %55, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = add i32 %147, 2
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %55, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = add i32 %87, %131
  %160 = mul i32 %159, 3
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %55, i64 %161
  %163 = load float, ptr %162, align 4
  %164 = add i32 %160, 1
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, ptr %55, i64 %165
  %167 = load float, ptr %166, align 4
  %168 = add i32 %160, 2
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %55, i64 %169
  %171 = load float, ptr %170, align 4
  %reass.add = fsub reassoc ninf nsz float %119, %106
  %reass.mul = fmul reassoc ninf nsz float %reass.add, 2.000000e+00
  %172 = fadd reassoc ninf nsz float %92, %reass.mul
  %173 = fadd reassoc ninf nsz float %62, %136
  %174 = fsub reassoc ninf nsz float %172, %173
  %175 = fadd reassoc ninf nsz float %174, %163
  %reass.add50 = fsub reassoc ninf nsz float %123, %110
  %reass.mul51 = fmul reassoc ninf nsz float %reass.add50, 2.000000e+00
  %176 = fadd reassoc ninf nsz float %96, %reass.mul51
  %177 = fadd reassoc ninf nsz float %66, %140
  %178 = fsub reassoc ninf nsz float %176, %177
  %179 = fadd reassoc ninf nsz float %178, %167
  %reass.add53 = fsub reassoc ninf nsz float %127, %114
  %reass.mul54 = fmul reassoc ninf nsz float %reass.add53, 2.000000e+00
  %180 = fadd reassoc ninf nsz float %100, %reass.mul54
  %181 = fadd reassoc ninf nsz float %70, %144
  %182 = fsub reassoc ninf nsz float %180, %181
  %183 = fadd reassoc ninf nsz float %182, %171
  %reass.add56 = fsub reassoc ninf nsz float %150, %76
  %reass.mul57 = fmul reassoc ninf nsz float %reass.add56, 2.000000e+00
  %184 = fadd reassoc ninf nsz float %62, %92
  %185 = fsub reassoc ninf nsz float %136, %184
  %186 = fadd reassoc ninf nsz float %185, %reass.mul57
  %187 = fadd reassoc ninf nsz float %186, %163
  %reass.add59 = fsub reassoc ninf nsz float %154, %80
  %reass.mul60 = fmul reassoc ninf nsz float %reass.add59, 2.000000e+00
  %188 = fadd reassoc ninf nsz float %66, %96
  %189 = fsub reassoc ninf nsz float %140, %188
  %190 = fadd reassoc ninf nsz float %189, %reass.mul60
  %191 = fadd reassoc ninf nsz float %190, %167
  %reass.add62 = fsub reassoc ninf nsz float %158, %84
  %reass.mul63 = fmul reassoc ninf nsz float %reass.add62, 2.000000e+00
  %192 = fadd reassoc ninf nsz float %70, %100
  %193 = fsub reassoc ninf nsz float %144, %192
  %194 = fadd reassoc ninf nsz float %193, %reass.mul63
  %195 = fadd reassoc ninf nsz float %194, %171
  %196 = fmul reassoc ninf nsz float %175, 0x3FD322D0E0000000
  %197 = fmul reassoc ninf nsz float %179, 0x3FE2C8B440000000
  %198 = fmul reassoc ninf nsz float %183, 0x3FBD2F1AA0000000
  %199 = fadd reassoc ninf nsz float %197, %196
  %200 = fadd reassoc ninf nsz float %199, %198
  %201 = load ptr, ptr %23, align 8
  %202 = load i32, ptr %24, align 4
  %203 = sub i32 %202, %31
  %204 = mul i32 %203, %38
  %205 = add i32 %.064, %204
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, ptr %201, i64 %206
  store float %200, ptr %207, align 4
  %208 = fmul reassoc ninf nsz float %187, 0x3FD322D0E0000000
  %209 = fmul reassoc ninf nsz float %191, 0x3FE2C8B440000000
  %210 = fmul reassoc ninf nsz float %195, 0x3FBD2F1AA0000000
  %211 = fadd reassoc ninf nsz float %209, %208
  %212 = fadd reassoc ninf nsz float %211, %210
  %213 = load ptr, ptr %25, align 8
  %214 = load i32, ptr %26, align 4
  %215 = sub i32 %214, %31
  %216 = mul i32 %215, %38
  %217 = add i32 %.064, %216
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, ptr %213, i64 %218
  store float %212, ptr %219, align 4
  %220 = add nsw i32 %.064, 1
  %exitcond.not = icmp eq i32 %18, %220
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #6
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
attributes #2 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nounwind }

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
