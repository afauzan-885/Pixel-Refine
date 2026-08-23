; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_remap_kernel_vec3_c316_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 72
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 76
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

define void @_remap_kernel_vec3_c316_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 64
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 68
  %23 = load i32, ptr %22, align 4
  %24 = add i32 %23, -1
  %25 = add i32 %21, -1
  %26 = icmp slt i32 %16, %18
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr i8, ptr %19, i64 24
  %28 = getelementptr i8, ptr %19, i64 20
  %29 = getelementptr i8, ptr %19, i64 40
  %30 = getelementptr i8, ptr %19, i64 36
  %31 = getelementptr i8, ptr %19, i64 8
  %32 = getelementptr i8, ptr %19, i64 4
  %33 = getelementptr i8, ptr %19, i64 56
  %34 = getelementptr i8, ptr %19, i64 52
  %35 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %35, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %213, %for_loop_body ]
  %36 = load ptr, ptr %3, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 32872
  %38 = load ptr, ptr %37, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 4
  %40 = load i32, ptr %39, align 4
  %41 = sdiv i32 %.05, %40
  %42 = mul i32 %41, %40
  %43 = xor i32 %40, %.05
  %44 = icmp slt i32 %43, 0
  %45 = icmp ne i32 %.05, %42
  %46 = and i1 %44, %45
  %.neg4 = sext i1 %46 to i32
  %47 = add i32 %41, %.neg4
  %48 = load ptr, ptr %27, align 8
  %49 = load i32, ptr %28, align 4
  %50 = sub i32 %49, %40
  %51 = mul i32 %50, %47
  %52 = add i32 %.05, %51
  %53 = sext i32 %52 to i64
  %54 = getelementptr float, ptr %48, i64 %53
  %55 = load float, ptr %54, align 4
  %56 = load ptr, ptr %29, align 8
  %57 = load i32, ptr %30, align 4
  %58 = sub i32 %57, %40
  %59 = mul i32 %58, %47
  %60 = add i32 %.05, %59
  %61 = sext i32 %60 to i64
  %62 = getelementptr float, ptr %56, i64 %61
  %63 = load float, ptr %62, align 4
  %64 = tail call reassoc ninf nsz float @llvm.floor.f32(float %55)
  %65 = fptosi float %64 to i32
  %66 = tail call reassoc ninf nsz float @llvm.floor.f32(float %63)
  %67 = fptosi float %66 to i32
  %68 = sitofp i32 %65 to float
  %69 = fsub reassoc ninf nsz float %55, %68
  %70 = sitofp i32 %67 to float
  %71 = fsub reassoc ninf nsz float %63, %70
  %72 = tail call i32 @llvm.abs.i32(i32 %65, i1 true)
  %73 = sub i32 %72, %24
  %74 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %75 = shl nuw i32 %74, 1
  %76 = sub i32 %72, %75
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %24, i32 %77)
  %79 = tail call i32 @llvm.abs.i32(i32 %67, i1 true)
  %80 = sub i32 %79, %25
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = shl nuw i32 %81, 1
  %83 = sub i32 %79, %82
  %84 = tail call i32 @llvm.smax.i32(i32 %83, i32 0)
  %85 = tail call i32 @llvm.smin.i32(i32 %25, i32 %84)
  %86 = add i32 %65, 1
  %87 = tail call i32 @llvm.abs.i32(i32 %86, i1 true)
  %88 = sub i32 %87, %24
  %89 = tail call i32 @llvm.smax.i32(i32 %88, i32 0)
  %90 = shl nuw i32 %89, 1
  %91 = sub i32 %87, %90
  %92 = tail call i32 @llvm.smax.i32(i32 %91, i32 0)
  %93 = tail call i32 @llvm.smin.i32(i32 %24, i32 %92)
  %94 = add i32 %67, 1
  %95 = tail call i32 @llvm.abs.i32(i32 %94, i1 true)
  %96 = sub i32 %95, %25
  %97 = tail call i32 @llvm.smax.i32(i32 %96, i32 0)
  %98 = shl nuw i32 %97, 1
  %99 = sub i32 %95, %98
  %100 = tail call i32 @llvm.smax.i32(i32 %99, i32 0)
  %101 = tail call i32 @llvm.smin.i32(i32 %25, i32 %100)
  %102 = load ptr, ptr %31, align 8
  %103 = load i32, ptr %32, align 4
  %104 = mul i32 %85, %103
  %105 = add i32 %104, %78
  %106 = mul i32 %105, 3
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, ptr %102, i64 %107
  %109 = load float, ptr %108, align 4
  %110 = add i32 %106, 1
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, ptr %102, i64 %111
  %113 = load float, ptr %112, align 4
  %114 = add i32 %106, 2
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %102, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = add i32 %104, %93
  %119 = mul i32 %118, 3
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %102, i64 %120
  %122 = load float, ptr %121, align 4
  %123 = add i32 %119, 1
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %102, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = add i32 %119, 2
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %102, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = mul i32 %101, %103
  %132 = add i32 %131, %78
  %133 = mul i32 %132, 3
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %102, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = add i32 %133, 1
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %102, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = add i32 %133, 2
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %102, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = add i32 %131, %93
  %146 = mul i32 %145, 3
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %102, i64 %147
  %149 = load float, ptr %148, align 4
  %150 = add i32 %146, 1
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %102, i64 %151
  %153 = load float, ptr %152, align 4
  %154 = add i32 %146, 2
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %102, i64 %155
  %157 = load float, ptr %156, align 4
  %158 = fsub reassoc ninf nsz float 1.000000e+00, %69
  %159 = fmul reassoc ninf nsz float %109, %158
  %160 = fmul reassoc ninf nsz float %113, %158
  %161 = fmul reassoc ninf nsz float %117, %158
  %162 = fmul reassoc ninf nsz float %122, %69
  %163 = fmul reassoc ninf nsz float %126, %69
  %164 = fmul reassoc ninf nsz float %130, %69
  %165 = fadd reassoc ninf nsz float %162, %159
  %166 = fadd reassoc ninf nsz float %163, %160
  %167 = fadd reassoc ninf nsz float %164, %161
  %168 = fmul reassoc ninf nsz float %136, %158
  %169 = fmul reassoc ninf nsz float %140, %158
  %170 = fmul reassoc ninf nsz float %144, %158
  %171 = fmul reassoc ninf nsz float %149, %69
  %172 = fmul reassoc ninf nsz float %153, %69
  %173 = fmul reassoc ninf nsz float %157, %69
  %174 = fadd reassoc ninf nsz float %171, %168
  %175 = fadd reassoc ninf nsz float %172, %169
  %176 = fadd reassoc ninf nsz float %173, %170
  %177 = fsub reassoc ninf nsz float 1.000000e+00, %71
  %178 = fmul reassoc ninf nsz float %165, %177
  %179 = fmul reassoc ninf nsz float %166, %177
  %180 = fmul reassoc ninf nsz float %167, %177
  %181 = fmul reassoc ninf nsz float %174, %71
  %182 = fmul reassoc ninf nsz float %175, %71
  %183 = fmul reassoc ninf nsz float %176, %71
  %184 = fadd reassoc ninf nsz float %181, %178
  %185 = fadd reassoc ninf nsz float %182, %179
  %186 = fadd reassoc ninf nsz float %183, %180
  %187 = load ptr, ptr %33, align 8
  %188 = load i32, ptr %34, align 4
  %189 = sub i32 %188, %40
  %190 = mul i32 %189, 3
  %191 = mul i32 %190, %47
  %192 = add i32 %lsr.iv, %191
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, ptr %187, i64 %193
  store float %184, ptr %194, align 4
  %195 = load ptr, ptr %33, align 8
  %196 = load i32, ptr %34, align 4
  %197 = sub i32 %196, %40
  %198 = mul i32 %197, 3
  %199 = mul i32 %198, %47
  %200 = add i32 %lsr.iv, %199
  %201 = add i32 %200, 1
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %195, i64 %202
  store float %185, ptr %203, align 4
  %204 = load ptr, ptr %33, align 8
  %205 = load i32, ptr %34, align 4
  %206 = sub i32 %205, %40
  %207 = mul i32 %206, 3
  %208 = mul i32 %207, %47
  %209 = add i32 %lsr.iv, %208
  %210 = add i32 %209, 2
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, ptr %204, i64 %211
  store float %186, ptr %212, align 4
  %213 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %213
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
