; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_box_filter_3x3_vec3_f32_kernel_c164_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 36
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

define void @_box_filter_3x3_vec3_f32_kernel_c164_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %25 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %25, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %238, %for_loop_body ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.05, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.05
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %.05, %32
  %36 = and i1 %34, %35
  %.neg4 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg4
  %38 = mul i32 %30, -1
  %39 = mul i32 %38, %37
  %40 = add i32 %.05, %39
  %41 = add i32 %37, -1
  %42 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %43 = load i32, ptr %42, align 4
  %44 = add i32 %43, -1
  %45 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %46 = tail call i32 @llvm.smin.i32(i32 %44, i32 %45)
  %47 = add i32 %40, -1
  %48 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %49 = load i32, ptr %48, align 4
  %50 = add i32 %49, -1
  %51 = tail call i32 @llvm.smax.i32(i32 %47, i32 0)
  %52 = tail call i32 @llvm.smin.i32(i32 %50, i32 %51)
  %53 = load ptr, ptr %21, align 8
  %54 = load i32, ptr %22, align 4
  %55 = mul i32 %46, %54
  %56 = add i32 %52, %55
  %57 = mul i32 %56, 3
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, ptr %53, i64 %58
  %60 = load float, ptr %59, align 4
  %61 = add i32 %57, 1
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, ptr %53, i64 %62
  %64 = load float, ptr %63, align 4
  %65 = add i32 %57, 2
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %53, i64 %66
  %68 = load float, ptr %67, align 4
  %69 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %70 = tail call i32 @llvm.smin.i32(i32 %50, i32 %69)
  %71 = add i32 %55, %70
  %72 = mul i32 %71, 3
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, ptr %53, i64 %73
  %75 = load float, ptr %74, align 4
  %76 = add i32 %72, 1
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, ptr %53, i64 %77
  %79 = load float, ptr %78, align 4
  %80 = add i32 %72, 2
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, ptr %53, i64 %81
  %83 = load float, ptr %82, align 4
  %84 = fadd reassoc ninf nsz float %75, %60
  %85 = fadd reassoc ninf nsz float %79, %64
  %86 = fadd reassoc ninf nsz float %83, %68
  %87 = add i32 %40, 1
  %88 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %50, i32 %88)
  %90 = add i32 %89, %55
  %91 = mul i32 %90, 3
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %53, i64 %92
  %94 = load float, ptr %93, align 4
  %95 = add i32 %91, 1
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %53, i64 %96
  %98 = load float, ptr %97, align 4
  %99 = add i32 %91, 2
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %53, i64 %100
  %102 = load float, ptr %101, align 4
  %103 = fadd reassoc ninf nsz float %84, %94
  %104 = fadd reassoc ninf nsz float %85, %98
  %105 = fadd reassoc ninf nsz float %86, %102
  %106 = tail call i32 @llvm.smax.i32(i32 %37, i32 0)
  %107 = tail call i32 @llvm.smin.i32(i32 %44, i32 %106)
  %108 = mul i32 %107, %54
  %109 = add i32 %52, %108
  %110 = mul i32 %109, 3
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, ptr %53, i64 %111
  %113 = load float, ptr %112, align 4
  %114 = add i32 %110, 1
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %53, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = add i32 %110, 2
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %53, i64 %119
  %121 = load float, ptr %120, align 4
  %122 = fadd reassoc ninf nsz float %103, %113
  %123 = fadd reassoc ninf nsz float %104, %117
  %124 = fadd reassoc ninf nsz float %105, %121
  %125 = add i32 %70, %108
  %126 = mul i32 %125, 3
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %53, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = add i32 %126, 1
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, ptr %53, i64 %131
  %133 = load float, ptr %132, align 4
  %134 = add i32 %126, 2
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, ptr %53, i64 %135
  %137 = load float, ptr %136, align 4
  %138 = fadd reassoc ninf nsz float %122, %129
  %139 = fadd reassoc ninf nsz float %123, %133
  %140 = fadd reassoc ninf nsz float %124, %137
  %141 = add i32 %89, %108
  %142 = mul i32 %141, 3
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %53, i64 %143
  %145 = load float, ptr %144, align 4
  %146 = add i32 %142, 1
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %53, i64 %147
  %149 = load float, ptr %148, align 4
  %150 = add i32 %142, 2
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %53, i64 %151
  %153 = load float, ptr %152, align 4
  %154 = fadd reassoc ninf nsz float %138, %145
  %155 = fadd reassoc ninf nsz float %139, %149
  %156 = fadd reassoc ninf nsz float %140, %153
  %157 = add i32 %37, 1
  %158 = tail call i32 @llvm.smax.i32(i32 %157, i32 0)
  %159 = tail call i32 @llvm.smin.i32(i32 %44, i32 %158)
  %160 = mul i32 %159, %54
  %161 = add i32 %52, %160
  %162 = mul i32 %161, 3
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %53, i64 %163
  %165 = load float, ptr %164, align 4
  %166 = add i32 %162, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, ptr %53, i64 %167
  %169 = load float, ptr %168, align 4
  %170 = add i32 %162, 2
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, ptr %53, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = fadd reassoc ninf nsz float %154, %165
  %175 = fadd reassoc ninf nsz float %155, %169
  %176 = fadd reassoc ninf nsz float %156, %173
  %177 = add i32 %160, %70
  %178 = mul i32 %177, 3
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, ptr %53, i64 %179
  %181 = load float, ptr %180, align 4
  %182 = add i32 %178, 1
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %53, i64 %183
  %185 = load float, ptr %184, align 4
  %186 = add i32 %178, 2
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, ptr %53, i64 %187
  %189 = load float, ptr %188, align 4
  %190 = fadd reassoc ninf nsz float %174, %181
  %191 = fadd reassoc ninf nsz float %175, %185
  %192 = fadd reassoc ninf nsz float %176, %189
  %193 = add i32 %89, %160
  %194 = mul i32 %193, 3
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, ptr %53, i64 %195
  %197 = load float, ptr %196, align 4
  %198 = add i32 %194, 1
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, ptr %53, i64 %199
  %201 = load float, ptr %200, align 4
  %202 = add i32 %194, 2
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %53, i64 %203
  %205 = load float, ptr %204, align 4
  %206 = fadd reassoc ninf nsz float %190, %197
  %207 = fadd reassoc ninf nsz float %191, %201
  %208 = fadd reassoc ninf nsz float %192, %205
  %209 = fmul reassoc ninf nsz float %206, 0x3FBC71C720000000
  %210 = fmul reassoc ninf nsz float %207, 0x3FBC71C720000000
  %211 = fmul reassoc ninf nsz float %208, 0x3FBC71C720000000
  %212 = load ptr, ptr %23, align 8
  %213 = load i32, ptr %24, align 4
  %214 = sub i32 %213, %30
  %215 = mul i32 %214, 3
  %216 = mul i32 %215, %37
  %217 = add i32 %lsr.iv, %216
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, ptr %212, i64 %218
  store float %209, ptr %219, align 4
  %220 = load ptr, ptr %23, align 8
  %221 = load i32, ptr %24, align 4
  %222 = sub i32 %221, %30
  %223 = mul i32 %222, 3
  %224 = mul i32 %223, %37
  %225 = add i32 %lsr.iv, %224
  %226 = add i32 %225, 1
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, ptr %220, i64 %227
  store float %210, ptr %228, align 4
  %229 = load ptr, ptr %23, align 8
  %230 = load i32, ptr %24, align 4
  %231 = sub i32 %230, %30
  %232 = mul i32 %231, 3
  %233 = mul i32 %232, %37
  %234 = add i32 %lsr.iv, %233
  %235 = add i32 %234, 2
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, ptr %229, i64 %236
  store float %211, ptr %237, align 4
  %238 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %238
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.5, align 8
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
