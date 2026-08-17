; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { ptr, ptr, i64 }
%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_bg_splat_c244_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %1, i64 0, i32 4
  %3 = load i32, ptr %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %1, i64 0, i32 5
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
define void @_bg_splat_c244_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
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
  %22 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 2
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 3
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 6
  %27 = load i32, ptr %26, align 4
  %28 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 7
  %29 = load i32, ptr %28, align 4
  %30 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 8
  %31 = load i32, ptr %30, align 4
  %32 = sitofp i32 %23 to float
  %33 = sitofp i32 %25 to float
  %34 = add i32 %27, -1
  %35 = add i32 %29, -1
  %36 = add i32 %31, -1
  %37 = icmp slt i32 %17, %19
  br i1 %37, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %38 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 0, i32 1
  %39 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 0, i32 0, i32 1
  %40 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 1, i32 1
  %41 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 1, i32 0, i32 1
  %42 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %109, %for_loop_body ]
  %43 = load ptr, ptr %3, align 8
  %44 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %43, i64 0, i32 14
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds i8, ptr %45, i64 4
  %47 = bitcast ptr %46 to ptr
  %48 = load i32, ptr %47, align 4
  %49 = sdiv i32 %.05, %48
  %50 = mul i32 %49, %48
  %51 = xor i32 %48, %.05
  %52 = icmp slt i32 %51, 0
  %53 = icmp ne i32 %.05, 0
  %54 = icmp ne i32 %.05, %50
  %55 = and i1 %53, %52
  %56 = and i1 %55, %54
  %.neg4 = sext i1 %56 to i32
  %57 = add i32 %49, %.neg4
  %58 = mul i32 %48, -1
  %59 = mul i32 %58, %57
  %60 = add i32 %.05, %59
  %61 = load ptr, ptr %38, align 8
  %62 = load i32, ptr %39, align 4
  %63 = sub i32 %62, %48
  %64 = mul i32 %63, %57
  %65 = add i32 %.05, %64
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %61, i64 %66
  %68 = load float, ptr %67, align 4
  %69 = sitofp i32 %57 to float
  %70 = fdiv reassoc ninf nsz float %69, %32
  %71 = tail call reassoc ninf nsz float @llvm.round.f32(float %70)
  %72 = fptosi float %71 to i32
  %73 = sitofp i32 %60 to float
  %74 = fdiv reassoc ninf nsz float %73, %32
  %75 = tail call reassoc ninf nsz float @llvm.round.f32(float %74)
  %76 = fptosi float %75 to i32
  %77 = fdiv reassoc ninf nsz float %68, %33
  %78 = tail call reassoc ninf nsz float @llvm.round.f32(float %77)
  %79 = fptosi float %78 to i32
  %80 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %81 = tail call i32 @llvm.smin.i32(i32 %34, i32 %80)
  %82 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %35, i32 %82)
  %84 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %85 = tail call i32 @llvm.smin.i32(i32 %36, i32 %84)
  %86 = load ptr, ptr %40, align 8
  %87 = load i32, ptr %41, align 4
  %88 = load i32, ptr %42, align 4
  %89 = mul i32 %81, %87
  %90 = add i32 %83, %89
  %91 = mul i32 %90, %88
  %92 = add i32 %91, %85
  %93 = shl i32 %92, 1
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %86, i64 %94
  %96 = atomicrmw fadd ptr %95, float %68 seq_cst, align 4
  %97 = load ptr, ptr %40, align 8
  %98 = load i32, ptr %41, align 4
  %99 = load i32, ptr %42, align 4
  %100 = mul i32 %81, %98
  %101 = add i32 %83, %100
  %102 = mul i32 %101, %99
  %103 = add i32 %102, %85
  %104 = shl i32 %103, 1
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, ptr %97, i64 %105
  %107 = getelementptr float, ptr %106, i64 1
  %108 = atomicrmw fadd ptr %107, float 1.000000e+00 seq_cst, align 4
  %109 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %109
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.round.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }

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
