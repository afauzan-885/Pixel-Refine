; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bilinear_resize_kernel_vec3_c134_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_bilinear_resize_kernel_vec3_c134_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %33 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %33, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %194, %for_loop_body ]
  %34 = load ptr, ptr %3, align 8
  %35 = getelementptr inbounds nuw i8, ptr %34, i64 32872
  %36 = load ptr, ptr %35, align 8
  %37 = getelementptr inbounds nuw i8, ptr %36, i64 4
  %38 = load i32, ptr %37, align 4
  %39 = sdiv i32 %.05, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.05
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.05, %40
  %44 = and i1 %42, %43
  %.neg4 = sext i1 %44 to i32
  %45 = add i32 %39, %.neg4
  %46 = mul i32 %38, -1
  %47 = mul i32 %46, %45
  %48 = add i32 %.05, %47
  %49 = sitofp i32 %45 to float
  %50 = fadd reassoc ninf nsz float %49, 5.000000e-01
  %51 = getelementptr inbounds nuw i8, ptr %36, i64 8
  %52 = load i32, ptr %51, align 4
  %53 = sitofp i32 %52 to float
  %54 = fmul reassoc ninf nsz float %50, %24
  %55 = fdiv reassoc ninf nsz float %54, %53
  %56 = fadd reassoc ninf nsz float %55, -5.000000e-01
  %57 = sitofp i32 %48 to float
  %58 = fadd reassoc ninf nsz float %57, 5.000000e-01
  %59 = getelementptr inbounds nuw i8, ptr %36, i64 12
  %60 = load i32, ptr %59, align 4
  %61 = sitofp i32 %60 to float
  %62 = fmul reassoc ninf nsz float %58, %25
  %63 = fdiv reassoc ninf nsz float %62, %61
  %64 = fadd reassoc ninf nsz float %63, -5.000000e-01
  %65 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %66 = fptosi float %65 to i32
  %67 = tail call reassoc ninf nsz float @llvm.floor.f32(float %64)
  %68 = fptosi float %67 to i32
  %69 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %70 = tail call i32 @llvm.smin.i32(i32 %26, i32 %69)
  %71 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %72 = tail call i32 @llvm.smin.i32(i32 %27, i32 %71)
  %73 = add i32 %66, 1
  %74 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %75 = tail call i32 @llvm.smin.i32(i32 %26, i32 %74)
  %76 = add i32 %68, 1
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %27, i32 %77)
  %79 = sitofp i32 %66 to float
  %80 = fsub reassoc ninf nsz float %56, %79
  %81 = sitofp i32 %68 to float
  %82 = fsub reassoc ninf nsz float %64, %81
  %83 = load ptr, ptr %29, align 8
  %84 = load i32, ptr %30, align 4
  %85 = mul i32 %70, %84
  %86 = add i32 %72, %85
  %87 = mul i32 %86, 3
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %83, i64 %88
  %90 = load float, ptr %89, align 4
  %91 = add i32 %87, 1
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %83, i64 %92
  %94 = load float, ptr %93, align 4
  %95 = add i32 %87, 2
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %83, i64 %96
  %98 = load float, ptr %97, align 4
  %99 = add i32 %78, %85
  %100 = mul i32 %99, 3
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %83, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = add i32 %100, 1
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, ptr %83, i64 %105
  %107 = load float, ptr %106, align 4
  %108 = add i32 %100, 2
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %83, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = mul i32 %75, %84
  %113 = add i32 %112, %72
  %114 = mul i32 %113, 3
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %83, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = add i32 %114, 1
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, ptr %83, i64 %119
  %121 = load float, ptr %120, align 4
  %122 = add i32 %114, 2
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, ptr %83, i64 %123
  %125 = load float, ptr %124, align 4
  %126 = add i32 %78, %112
  %127 = mul i32 %126, 3
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, ptr %83, i64 %128
  %130 = load float, ptr %129, align 4
  %131 = add i32 %127, 1
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, ptr %83, i64 %132
  %134 = load float, ptr %133, align 4
  %135 = add i32 %127, 2
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %83, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = fsub reassoc ninf nsz float 1.000000e+00, %82
  %140 = fmul reassoc ninf nsz float %139, %90
  %141 = fmul reassoc ninf nsz float %139, %94
  %142 = fmul reassoc ninf nsz float %139, %98
  %143 = fmul reassoc ninf nsz float %82, %103
  %144 = fmul reassoc ninf nsz float %82, %107
  %145 = fmul reassoc ninf nsz float %82, %111
  %146 = fadd reassoc ninf nsz float %140, %143
  %147 = fadd reassoc ninf nsz float %141, %144
  %148 = fadd reassoc ninf nsz float %142, %145
  %149 = fmul reassoc ninf nsz float %139, %117
  %150 = fmul reassoc ninf nsz float %139, %121
  %151 = fmul reassoc ninf nsz float %139, %125
  %152 = fmul reassoc ninf nsz float %82, %130
  %153 = fmul reassoc ninf nsz float %82, %134
  %154 = fmul reassoc ninf nsz float %138, %82
  %155 = fadd reassoc ninf nsz float %149, %152
  %156 = fadd reassoc ninf nsz float %150, %153
  %157 = fadd reassoc ninf nsz float %151, %154
  %158 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %159 = fmul reassoc ninf nsz float %146, %158
  %160 = fmul reassoc ninf nsz float %147, %158
  %161 = fmul reassoc ninf nsz float %148, %158
  %162 = fmul reassoc ninf nsz float %155, %80
  %163 = fmul reassoc ninf nsz float %156, %80
  %164 = fmul reassoc ninf nsz float %157, %80
  %165 = fadd reassoc ninf nsz float %159, %162
  %166 = fadd reassoc ninf nsz float %160, %163
  %167 = fadd reassoc ninf nsz float %161, %164
  %168 = load ptr, ptr %31, align 8
  %169 = load i32, ptr %32, align 4
  %170 = sub i32 %169, %38
  %171 = mul i32 %170, 3
  %172 = mul i32 %171, %45
  %173 = add i32 %lsr.iv, %172
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, ptr %168, i64 %174
  store float %165, ptr %175, align 4
  %176 = load ptr, ptr %31, align 8
  %177 = load i32, ptr %32, align 4
  %178 = sub i32 %177, %38
  %179 = mul i32 %178, 3
  %180 = mul i32 %179, %45
  %181 = add i32 %lsr.iv, %180
  %182 = add i32 %181, 1
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %176, i64 %183
  store float %166, ptr %184, align 4
  %185 = load ptr, ptr %31, align 8
  %186 = load i32, ptr %32, align 4
  %187 = sub i32 %186, %38
  %188 = mul i32 %187, 3
  %189 = mul i32 %188, %45
  %190 = add i32 %lsr.iv, %189
  %191 = add i32 %190, 2
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, ptr %185, i64 %192
  store float %167, ptr %193, align 4
  %194 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %194
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
