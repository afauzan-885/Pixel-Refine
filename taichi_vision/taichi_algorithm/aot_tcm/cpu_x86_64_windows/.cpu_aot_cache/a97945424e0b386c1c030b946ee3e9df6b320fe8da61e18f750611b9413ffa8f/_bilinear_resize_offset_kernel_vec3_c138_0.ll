; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bilinear_resize_offset_kernel_vec3_c138_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 16
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 20
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

define void @_bilinear_resize_offset_kernel_vec3_c138_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 48
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 52
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 32
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 40
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr i8, ptr %19, i64 36
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr i8, ptr %19, i64 44
  %31 = load i32, ptr %30, align 4
  %32 = sitofp i32 %25 to float
  %33 = sitofp i32 %27 to float
  %34 = sitofp i32 %29 to float
  %35 = sitofp i32 %31 to float
  %36 = add i32 %25, -1
  %37 = add i32 %29, -1
  %38 = icmp slt i32 %16, %18
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr i8, ptr %19, i64 8
  %40 = getelementptr i8, ptr %19, i64 4
  %41 = getelementptr i8, ptr %19, i64 24
  %42 = getelementptr i8, ptr %19, i64 20
  %43 = mul i32 %16, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %43, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %200, %for_loop_body ]
  %44 = load ptr, ptr %3, align 8
  %45 = getelementptr inbounds nuw i8, ptr %44, i64 32872
  %46 = load ptr, ptr %45, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 4
  %48 = load i32, ptr %47, align 4
  %49 = sdiv i32 %.05, %48
  %50 = mul i32 %49, %48
  %51 = xor i32 %48, %.05
  %52 = icmp slt i32 %51, 0
  %53 = icmp ne i32 %.05, %50
  %54 = and i1 %52, %53
  %.neg4 = sext i1 %54 to i32
  %55 = add i32 %49, %.neg4
  %56 = add i32 %55, %21
  %57 = mul i32 %48, -1
  %58 = mul i32 %57, %55
  %59 = add i32 %23, %.05
  %60 = add i32 %59, %58
  %61 = sitofp i32 %56 to float
  %62 = fadd reassoc ninf nsz float %61, 5.000000e-01
  %63 = fmul reassoc ninf nsz float %62, %32
  %64 = fdiv reassoc ninf nsz float %63, %33
  %65 = fadd reassoc ninf nsz float %64, -5.000000e-01
  %66 = sitofp i32 %60 to float
  %67 = fadd reassoc ninf nsz float %66, 5.000000e-01
  %68 = fmul reassoc ninf nsz float %67, %34
  %69 = fdiv reassoc ninf nsz float %68, %35
  %70 = fadd reassoc ninf nsz float %69, -5.000000e-01
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %65)
  %72 = fptosi float %71 to i32
  %73 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %74 = fptosi float %73 to i32
  %75 = sitofp i32 %72 to float
  %76 = fsub reassoc ninf nsz float %65, %75
  %77 = sitofp i32 %74 to float
  %78 = fsub reassoc ninf nsz float %70, %77
  %79 = add i32 %72, 1
  %80 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %81 = tail call i32 @llvm.smin.i32(i32 %36, i32 %80)
  %82 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %36, i32 %82)
  %84 = add i32 %74, 1
  %85 = tail call i32 @llvm.smax.i32(i32 %74, i32 0)
  %86 = tail call i32 @llvm.smin.i32(i32 %37, i32 %85)
  %87 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %88 = tail call i32 @llvm.smin.i32(i32 %37, i32 %87)
  %89 = load ptr, ptr %39, align 8
  %90 = load i32, ptr %40, align 4
  %91 = mul i32 %81, %90
  %92 = add i32 %86, %91
  %93 = mul i32 %92, 3
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %89, i64 %94
  %96 = load float, ptr %95, align 4
  %97 = add i32 %93, 1
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %89, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = add i32 %93, 2
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, ptr %89, i64 %102
  %104 = load float, ptr %103, align 4
  %105 = add i32 %88, %91
  %106 = mul i32 %105, 3
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, ptr %89, i64 %107
  %109 = load float, ptr %108, align 4
  %110 = add i32 %106, 1
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, ptr %89, i64 %111
  %113 = load float, ptr %112, align 4
  %114 = add i32 %106, 2
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %89, i64 %115
  %117 = load float, ptr %116, align 4
  %118 = mul i32 %83, %90
  %119 = add i32 %118, %86
  %120 = mul i32 %119, 3
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %89, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = add i32 %120, 1
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %89, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = add i32 %120, 2
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, ptr %89, i64 %129
  %131 = load float, ptr %130, align 4
  %132 = add i32 %88, %118
  %133 = mul i32 %132, 3
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, ptr %89, i64 %134
  %136 = load float, ptr %135, align 4
  %137 = add i32 %133, 1
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %89, i64 %138
  %140 = load float, ptr %139, align 4
  %141 = add i32 %133, 2
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, ptr %89, i64 %142
  %144 = load float, ptr %143, align 4
  %145 = fsub reassoc ninf nsz float 1.000000e+00, %78
  %146 = fmul reassoc ninf nsz float %145, %96
  %147 = fmul reassoc ninf nsz float %145, %100
  %148 = fmul reassoc ninf nsz float %145, %104
  %149 = fmul reassoc ninf nsz float %78, %109
  %150 = fmul reassoc ninf nsz float %78, %113
  %151 = fmul reassoc ninf nsz float %78, %117
  %152 = fadd reassoc ninf nsz float %146, %149
  %153 = fadd reassoc ninf nsz float %147, %150
  %154 = fadd reassoc ninf nsz float %148, %151
  %155 = fmul reassoc ninf nsz float %145, %123
  %156 = fmul reassoc ninf nsz float %145, %127
  %157 = fmul reassoc ninf nsz float %145, %131
  %158 = fmul reassoc ninf nsz float %78, %136
  %159 = fmul reassoc ninf nsz float %78, %140
  %160 = fmul reassoc ninf nsz float %78, %144
  %161 = fadd reassoc ninf nsz float %155, %158
  %162 = fadd reassoc ninf nsz float %156, %159
  %163 = fadd reassoc ninf nsz float %157, %160
  %164 = fsub reassoc ninf nsz float 1.000000e+00, %76
  %165 = fmul reassoc ninf nsz float %152, %164
  %166 = fmul reassoc ninf nsz float %153, %164
  %167 = fmul reassoc ninf nsz float %154, %164
  %168 = fmul reassoc ninf nsz float %161, %76
  %169 = fmul reassoc ninf nsz float %162, %76
  %170 = fmul reassoc ninf nsz float %163, %76
  %171 = fadd reassoc ninf nsz float %165, %168
  %172 = fadd reassoc ninf nsz float %166, %169
  %173 = fadd reassoc ninf nsz float %167, %170
  %174 = load ptr, ptr %41, align 8
  %175 = load i32, ptr %42, align 4
  %176 = sub i32 %175, %48
  %177 = mul i32 %176, 3
  %178 = mul i32 %177, %55
  %179 = add i32 %lsr.iv, %178
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %174, i64 %180
  store float %171, ptr %181, align 4
  %182 = load ptr, ptr %41, align 8
  %183 = load i32, ptr %42, align 4
  %184 = sub i32 %183, %48
  %185 = mul i32 %184, 3
  %186 = mul i32 %185, %55
  %187 = add i32 %lsr.iv, %186
  %188 = add i32 %187, 1
  %189 = sext i32 %188 to i64
  %190 = getelementptr float, ptr %182, i64 %189
  store float %172, ptr %190, align 4
  %191 = load ptr, ptr %41, align 8
  %192 = load i32, ptr %42, align 4
  %193 = sub i32 %192, %48
  %194 = mul i32 %193, 3
  %195 = mul i32 %194, %55
  %196 = add i32 %lsr.iv, %195
  %197 = add i32 %196, 2
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, ptr %191, i64 %198
  store float %173, ptr %199, align 4
  %200 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %18, %200
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #7
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
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nounwind }

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
