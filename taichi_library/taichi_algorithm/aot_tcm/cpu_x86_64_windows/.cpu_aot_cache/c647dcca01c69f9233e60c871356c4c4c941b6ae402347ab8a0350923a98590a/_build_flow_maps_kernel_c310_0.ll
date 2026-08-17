; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_build_flow_maps_kernel_c310_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 72
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 12
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 76
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 8
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

define void @_build_flow_maps_kernel_c310_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 68
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 64
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 80
  %25 = load float, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 84
  %27 = load float, ptr %26, align 4
  %28 = add i32 %21, -1
  %29 = add i32 %23, -1
  %30 = sitofp i32 %28 to float
  %31 = sitofp i32 %29 to float
  %32 = icmp slt i32 %16, %18
  br i1 %32, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %33 = getelementptr i8, ptr %19, i64 8
  %34 = getelementptr i8, ptr %19, i64 4
  %35 = getelementptr i8, ptr %19, i64 24
  %36 = getelementptr i8, ptr %19, i64 20
  %37 = getelementptr i8, ptr %19, i64 40
  %38 = getelementptr i8, ptr %19, i64 36
  %39 = getelementptr i8, ptr %19, i64 56
  %40 = getelementptr i8, ptr %19, i64 52
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %186, %for_loop_body ]
  %41 = load ptr, ptr %3, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 4
  %45 = load i32, ptr %44, align 4
  %46 = sdiv i32 %.05, %45
  %47 = mul i32 %46, %45
  %48 = xor i32 %45, %.05
  %49 = icmp slt i32 %48, 0
  %50 = icmp ne i32 %.05, %47
  %51 = and i1 %49, %50
  %.neg4 = sext i1 %51 to i32
  %52 = add i32 %46, %.neg4
  %53 = mul i32 %45, -1
  %54 = mul i32 %53, %52
  %55 = add i32 %.05, %54
  %56 = sitofp i32 %55 to float
  %57 = fmul reassoc ninf nsz float %56, %30
  %58 = getelementptr inbounds nuw i8, ptr %43, i64 8
  %59 = load i32, ptr %58, align 4
  %60 = add i32 %59, -1
  %61 = sitofp i32 %60 to float
  %62 = fdiv reassoc ninf nsz float %57, %61
  %63 = sitofp i32 %52 to float
  %64 = fmul reassoc ninf nsz float %63, %31
  %65 = getelementptr inbounds nuw i8, ptr %43, i64 12
  %66 = load i32, ptr %65, align 4
  %67 = add i32 %66, -1
  %68 = sitofp i32 %67 to float
  %69 = fdiv reassoc ninf nsz float %64, %68
  %70 = tail call reassoc ninf nsz float @llvm.floor.f32(float %62)
  %71 = fptosi float %70 to i32
  %72 = tail call reassoc ninf nsz float @llvm.floor.f32(float %69)
  %73 = fptosi float %72 to i32
  %74 = sitofp i32 %71 to float
  %75 = fsub reassoc ninf nsz float %62, %74
  %76 = sitofp i32 %73 to float
  %77 = fsub reassoc ninf nsz float %69, %76
  %78 = tail call i32 @llvm.abs.i32(i32 %71, i1 true)
  %79 = sub i32 %78, %28
  %80 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %81 = shl nuw i32 %80, 1
  %82 = sub i32 %78, %81
  %83 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %28, i32 %83)
  %85 = tail call i32 @llvm.abs.i32(i32 %73, i1 true)
  %86 = sub i32 %85, %29
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = shl nuw i32 %87, 1
  %89 = sub i32 %85, %88
  %90 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %91 = tail call i32 @llvm.smin.i32(i32 %29, i32 %90)
  %92 = add i32 %71, 1
  %93 = tail call i32 @llvm.abs.i32(i32 %92, i1 true)
  %94 = sub i32 %93, %28
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = shl nuw i32 %95, 1
  %97 = sub i32 %93, %96
  %98 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %99 = tail call i32 @llvm.smin.i32(i32 %28, i32 %98)
  %100 = add i32 %73, 1
  %101 = tail call i32 @llvm.abs.i32(i32 %100, i1 true)
  %102 = sub i32 %101, %29
  %103 = tail call i32 @llvm.smax.i32(i32 %102, i32 0)
  %104 = shl nuw i32 %103, 1
  %105 = sub i32 %101, %104
  %106 = tail call i32 @llvm.smax.i32(i32 %105, i32 0)
  %107 = tail call i32 @llvm.smin.i32(i32 %29, i32 %106)
  %108 = load ptr, ptr %33, align 8
  %109 = load i32, ptr %34, align 4
  %110 = mul i32 %91, %109
  %111 = add i32 %84, %110
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, ptr %108, i64 %112
  %114 = load float, ptr %113, align 4
  %115 = add i32 %99, %110
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %108, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = mul i32 %107, %109
  %120 = add i32 %119, %84
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %108, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = add i32 %99, %119
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, ptr %108, i64 %125
  %127 = load float, ptr %126, align 4
  %128 = fsub reassoc ninf nsz float 1.000000e+00, %75
  %129 = fmul reassoc ninf nsz float %128, %114
  %130 = fmul reassoc ninf nsz float %75, %118
  %131 = fadd reassoc ninf nsz float %129, %130
  %132 = fmul reassoc ninf nsz float %128, %123
  %133 = fmul reassoc ninf nsz float %75, %127
  %134 = fadd reassoc ninf nsz float %132, %133
  %135 = fsub reassoc ninf nsz float 1.000000e+00, %77
  %136 = fmul reassoc ninf nsz float %131, %135
  %137 = fmul reassoc ninf nsz float %134, %77
  %138 = fadd reassoc ninf nsz float %136, %137
  %139 = load ptr, ptr %35, align 8
  %140 = load i32, ptr %36, align 4
  %141 = mul i32 %91, %140
  %142 = add i32 %84, %141
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %139, i64 %143
  %145 = load float, ptr %144, align 4
  %146 = add i32 %99, %141
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %139, i64 %147
  %149 = load float, ptr %148, align 4
  %150 = mul i32 %107, %140
  %151 = add i32 %150, %84
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %139, i64 %152
  %154 = load float, ptr %153, align 4
  %155 = add i32 %99, %150
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, ptr %139, i64 %156
  %158 = load float, ptr %157, align 4
  %159 = fmul reassoc ninf nsz float %128, %145
  %160 = fmul reassoc ninf nsz float %75, %149
  %161 = fadd reassoc ninf nsz float %159, %160
  %162 = fmul reassoc ninf nsz float %128, %154
  %163 = fmul reassoc ninf nsz float %158, %75
  %164 = fadd reassoc ninf nsz float %162, %163
  %165 = fmul reassoc ninf nsz float %161, %135
  %166 = fmul reassoc ninf nsz float %164, %77
  %167 = fadd reassoc ninf nsz float %165, %166
  %168 = fmul reassoc ninf nsz float %138, %25
  %169 = fadd reassoc ninf nsz float %168, %56
  %170 = load ptr, ptr %37, align 8
  %171 = load i32, ptr %38, align 4
  %172 = sub i32 %171, %45
  %173 = mul i32 %172, %52
  %174 = add i32 %.05, %173
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %170, i64 %175
  store float %169, ptr %176, align 4
  %177 = fmul reassoc ninf nsz float %167, %27
  %178 = fadd reassoc ninf nsz float %177, %63
  %179 = load ptr, ptr %39, align 8
  %180 = load i32, ptr %40, align 4
  %181 = sub i32 %180, %45
  %182 = mul i32 %181, %52
  %183 = add i32 %.05, %182
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, ptr %179, i64 %184
  store float %178, ptr %185, align 4
  %186 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %18, %186
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
  %4 = alloca %struct.RuntimeContext.3, align 8
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
