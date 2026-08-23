; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { ptr, ptr, i64 }
%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_mlri_admm_srgb_tonemap_c136_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %1, i64 0, i32 3
  %3 = load i32, ptr %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %1, i64 0, i32 4
  %6 = load i32, ptr %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.6, ptr %context, i64 0, i32 1
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %9, i64 0, i32 14
  %11 = load ptr, ptr %10, align 8
  %12 = getelementptr inbounds i8, ptr %11, i64 4
  %13 = bitcast ptr %12 to ptr
  store i32 %7, ptr %13, align 4
  %14 = mul i32 %7, %4
  %15 = load ptr, ptr %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %15, i64 0, i32 14
  %17 = bitcast ptr %16 to ptr
  %18 = load ptr, ptr %17, align 8
  store i32 %14, ptr %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_mlri_admm_srgb_tonemap_c136_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast ptr %0 to ptr
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 0
  store ptr %context, ptr %4, align 8
  store ptr null, ptr %2, align 8
  store i64 1, ptr %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 2
  store ptr @function_body, ptr %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 3
  store ptr null, ptr %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 5
  %8 = bitcast ptr %7 to ptr
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, ptr %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, ptr %context, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %10, i64 0, i32 10
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %10, i64 0, i32 9
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %4, i64 0, i32 14
  %6 = bitcast ptr %5 to ptr
  %7 = load ptr, ptr %6, align 8
  %8 = load i32, ptr %7, align 4
  %9 = add i32 %8, 7
  %10 = sdiv i32 %9, 8
  %11 = icmp slt i32 %9, 0
  %12 = shl nsw i32 %10, 3
  %13 = icmp ne i32 %12, %9
  %14 = and i1 %11, %13
  %.neg = sext i1 %14 to i32
  %15 = add nsw i32 %10, %.neg
  %16 = tail call i32 @llvm.smax.i32(i32 %15, i32 512)
  %17 = mul i32 %16, %2
  %18 = add i32 %17, %16
  %19 = tail call i32 @llvm.smin.i32(i32 %8, i32 %18)
  %20 = bitcast ptr %0 to ptr
  %21 = load ptr, ptr %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 1, i32 1
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 1, i32 0, i32 1
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr float, ptr %23, i64 1
  %27 = getelementptr float, ptr %23, i64 2
  %28 = sext i32 %25 to i64
  %29 = getelementptr float, ptr %23, i64 %28
  %30 = add i32 %25, 1
  %31 = sext i32 %30 to i64
  %32 = getelementptr float, ptr %23, i64 %31
  %33 = add i32 %25, 2
  %34 = sext i32 %33 to i64
  %35 = getelementptr float, ptr %23, i64 %34
  %36 = shl i32 %25, 1
  %37 = sext i32 %36 to i64
  %38 = getelementptr float, ptr %23, i64 %37
  %39 = getelementptr float, ptr %38, i64 1
  %40 = add i32 %36, 2
  %41 = sext i32 %40 to i64
  %42 = getelementptr float, ptr %23, i64 %41
  %43 = icmp slt i32 %17, %19
  br i1 %43, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %44 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 0, i32 1
  %45 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 0, i32 0, i32 2
  %47 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 2, i32 1
  %48 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 2, i32 0, i32 1
  %49 = getelementptr { { { i32, i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32 }, ptr %21, i64 0, i32 2, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %145, %for_loop_body ]
  %50 = load ptr, ptr %3, align 8
  %51 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %50, i64 0, i32 14
  %52 = load ptr, ptr %51, align 8
  %53 = getelementptr inbounds i8, ptr %52, i64 4
  %54 = bitcast ptr %53 to ptr
  %55 = load i32, ptr %54, align 4
  %56 = sdiv i32 %.05, %55
  %57 = mul i32 %56, %55
  %58 = xor i32 %55, %.05
  %59 = icmp slt i32 %58, 0
  %60 = icmp ne i32 %.05, 0
  %61 = icmp ne i32 %.05, %57
  %62 = and i1 %60, %59
  %63 = and i1 %62, %61
  %.neg4 = sext i1 %63 to i32
  %64 = add i32 %56, %.neg4
  %65 = load ptr, ptr %44, align 8
  %66 = load i32, ptr %45, align 4
  %67 = load i32, ptr %46, align 4
  %68 = sub i32 %66, %55
  %69 = mul i32 %68, %64
  %70 = add i32 %.05, %69
  %71 = mul i32 %70, %67
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, ptr %65, i64 %72
  %74 = load float, ptr %73, align 4
  %75 = add i32 %71, 1
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, ptr %65, i64 %76
  %78 = load float, ptr %77, align 4
  %79 = add i32 %71, 2
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, ptr %65, i64 %80
  %82 = load float, ptr %81, align 4
  %83 = load float, ptr %23, align 4
  %84 = fmul reassoc ninf nsz float %83, %74
  %85 = load float, ptr %26, align 4
  %86 = fmul reassoc ninf nsz float %85, %78
  %87 = fadd reassoc ninf nsz float %86, %84
  %88 = load float, ptr %27, align 4
  %89 = fmul reassoc ninf nsz float %88, %82
  %90 = fadd reassoc ninf nsz float %87, %89
  %91 = load float, ptr %29, align 4
  %92 = fmul reassoc ninf nsz float %91, %74
  %93 = load float, ptr %32, align 4
  %94 = fmul reassoc ninf nsz float %93, %78
  %95 = fadd reassoc ninf nsz float %94, %92
  %96 = load float, ptr %35, align 4
  %97 = fmul reassoc ninf nsz float %96, %82
  %98 = fadd reassoc ninf nsz float %95, %97
  %99 = load float, ptr %38, align 4
  %100 = fmul reassoc ninf nsz float %99, %74
  %101 = load float, ptr %39, align 4
  %102 = fmul reassoc ninf nsz float %101, %78
  %103 = fadd reassoc ninf nsz float %102, %100
  %104 = load float, ptr %42, align 4
  %105 = fmul reassoc ninf nsz float %104, %82
  %106 = fadd reassoc ninf nsz float %103, %105
  %107 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %90, float 0.000000e+00)
  %108 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %107, float 1.000000e+00)
  %109 = tail call float @powf(float noundef %108, float noundef 0x3FDCD42E20000000) #1
  %110 = load ptr, ptr %47, align 8
  %111 = load i32, ptr %48, align 4
  %112 = load i32, ptr %49, align 4
  %113 = sub i32 %111, %55
  %114 = mul i32 %113, %64
  %115 = add i32 %.05, %114
  %116 = mul i32 %115, %112
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %110, i64 %117
  store float %109, ptr %118, align 4
  %119 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %98, float 0.000000e+00)
  %120 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %119, float 1.000000e+00)
  %121 = tail call float @powf(float noundef %120, float noundef 0x3FDCD42E20000000) #1
  %122 = load ptr, ptr %47, align 8
  %123 = load i32, ptr %48, align 4
  %124 = load i32, ptr %49, align 4
  %125 = sub i32 %123, %55
  %126 = mul i32 %125, %64
  %127 = add i32 %.05, %126
  %128 = mul i32 %127, %124
  %129 = add i32 %128, 1
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %122, i64 %130
  store float %121, ptr %131, align 4
  %132 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %106, float 0.000000e+00)
  %133 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %132, float 1.000000e+00)
  %134 = tail call float @powf(float noundef %133, float noundef 0x3FDCD42E20000000) #1
  %135 = load ptr, ptr %47, align 8
  %136 = load i32, ptr %48, align 4
  %137 = load i32, ptr %49, align 4
  %138 = sub i32 %136, %55
  %139 = mul i32 %138, %64
  %140 = add i32 %.05, %139
  %141 = mul i32 %140, %137
  %142 = add i32 %141, 2
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %135, i64 %143
  store float %134, ptr %144, align 4
  %145 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %145
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @powf(float noundef, float noundef) local_unnamed_addr #4

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #5 {
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast ptr %0 to ptr
  %.sroa.0.0.copyload = load ptr, ptr %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast ptr %.sroa.4.0..sroa_idx to ptr
  %.sroa.4.0.copyload = load ptr, ptr %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast ptr %.sroa.5.0..sroa_idx to ptr
  %.sroa.5.0.copyload = load ptr, ptr %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast ptr %.sroa.7.0..sroa_idx to ptr
  %.sroa.7.0.copyload = load ptr, ptr %.sroa.7.0..sroa_cast, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 32
  %.sroa.8.0..sroa_cast = bitcast ptr %.sroa.8.0..sroa_idx to ptr
  %.sroa.8.0.copyload = load i64, ptr %.sroa.8.0..sroa_cast, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 40
  %.sroa.9.0..sroa_cast = bitcast ptr %.sroa.9.0..sroa_idx to ptr
  %.sroa.9.0.copyload = load i32, ptr %.sroa.9.0..sroa_cast, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 44
  %.sroa.12.0..sroa_cast = bitcast ptr %.sroa.12.0..sroa_idx to ptr
  %.sroa.12.0.copyload = load i32, ptr %.sroa.12.0..sroa_cast, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 48
  %.sroa.15.0..sroa_cast = bitcast ptr %.sroa.15.0..sroa_idx to ptr
  %.sroa.15.0.copyload = load i32, ptr %.sroa.15.0..sroa_cast, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 52
  %.sroa.17.0..sroa_cast = bitcast ptr %.sroa.17.0..sroa_idx to ptr
  %.sroa.17.0.copyload = load i32, ptr %.sroa.17.0..sroa_cast, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq ptr %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast ptr %.sroa.0.0.copyload to ptr
  %9 = bitcast ptr %4 to ptr
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %9, ptr noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, ptr %4, i64 0, i32 2
  store i32 %1, ptr %10, align 8
  switch i32 %.sroa.17.0.copyload, label %.loopexit [
    i32 1, label %11
    i32 -1, label %19
  ]

11:                                               ; preds = %7
  %12 = mul nsw i32 %.sroa.15.0.copyload, %2
  %13 = add nsw i32 %12, %.sroa.9.0.copyload
  %14 = add nsw i32 %13, %.sroa.15.0.copyload
  %15 = call i32 @llvm.smin.i32(i32 %.sroa.12.0.copyload, i32 %14)
  %16 = icmp slt i32 %13, %15
  br i1 %16, label %.lr.ph.preheader, label %.loopexit

.lr.ph.preheader:                                 ; preds = %11
  br label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %.lr.ph.preheader
  %.02038 = phi i32 [ %17, %.lr.ph ], [ %13, %.lr.ph.preheader ]
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !9

19:                                               ; preds = %7
  %20 = mul nsw i32 %.sroa.15.0.copyload, %2
  %21 = sub nsw i32 %.sroa.12.0.copyload, %20
  %22 = mul nsw i32 %21, %.sroa.15.0.copyload
  %23 = call i32 @llvm.smax.i32(i32 %.sroa.9.0.copyload, i32 %22)
  %.not25.not39 = icmp sgt i32 %21, %23
  br i1 %.not25.not39, label %.lr.ph41.preheader, label %.loopexit

.lr.ph41.preheader:                               ; preds = %19
  br label %.lr.ph41

.lr.ph41:                                         ; preds = %.lr.ph41, %.lr.ph41.preheader
  %.0.in40 = phi i32 [ %.0, %.lr.ph41 ], [ %21, %.lr.ph41.preheader ]
  %.0 = add nsw i32 %.0.in40, -1
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }

!llvm.linker.options = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}
!llvm.module.flags = !{!6, !7, !8}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"clang version 14.0.6"}
!6 = !{i32 1, !"wchar_size", i32 2}
!7 = !{i32 8, !"PIC Level", i32 2}
!8 = !{i32 7, !"uwtable", i32 1}
!9 = distinct !{!9, !10}
!10 = !{!"llvm.loop.mustprogress"}
!11 = distinct !{!11, !10}
