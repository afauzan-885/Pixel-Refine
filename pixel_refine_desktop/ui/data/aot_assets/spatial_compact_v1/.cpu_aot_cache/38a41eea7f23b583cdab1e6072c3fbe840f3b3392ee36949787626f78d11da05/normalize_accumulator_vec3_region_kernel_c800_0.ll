; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.56 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @normalize_accumulator_vec3_region_kernel_c800_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @normalize_accumulator_vec3_region_kernel_c800_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %24 = getelementptr i8, ptr %19, i64 48
  %25 = load i32, ptr %24, align 4
  %26 = icmp slt i32 %16, %18
  br i1 %26, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.047 = phi i32 [ %126, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 32872
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 4
  %31 = load i32, ptr %30, align 4
  %32 = sdiv i32 %.047, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.047
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.047, %33
  %37 = and i1 %35, %36
  %.neg6 = sext i1 %37 to i32
  %38 = add i32 %32, %.neg6
  %39 = mul i32 %38, %31
  %40 = add i32 %38, %21
  %41 = mul i32 %31, -1
  %42 = mul i32 %41, %38
  %43 = add i32 %23, %.047
  %44 = add i32 %43, %42
  %45 = icmp slt i32 %40, %25
  br i1 %45, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %46 = load ptr, ptr %0, align 8
  %47 = getelementptr i8, ptr %46, i64 52
  %48 = load i32, ptr %47, align 4
  %49 = icmp slt i32 %44, %48
  br i1 %49, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %50 = getelementptr i8, ptr %46, i64 40
  %51 = load ptr, ptr %50, align 8
  %52 = getelementptr i8, ptr %46, i64 28
  %53 = load i32, ptr %52, align 4
  %54 = getelementptr i8, ptr %46, i64 32
  %55 = load i32, ptr %54, align 4
  %56 = mul i32 %53, %40
  %57 = sub i32 %56, %39
  %58 = add i32 %43, %57
  %59 = mul i32 %58, %55
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %51, i64 %60
  %62 = load float, ptr %61, align 4
  %63 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %62, float 0x3E45798EE0000000)
  %64 = getelementptr i8, ptr %46, i64 16
  %65 = load ptr, ptr %64, align 8
  %66 = getelementptr i8, ptr %46, i64 4
  %67 = load i32, ptr %66, align 4
  %68 = getelementptr i8, ptr %46, i64 8
  %69 = load i32, ptr %68, align 4
  %70 = mul i32 %67, %40
  %71 = sub i32 %70, %39
  %72 = add i32 %43, %71
  %73 = mul i32 %72, %69
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, ptr %65, i64 %74
  %76 = load float, ptr %75, align 4
  %77 = fdiv reassoc ninf nsz float %76, %63
  store float %77, ptr %75, align 4
  %78 = load ptr, ptr %50, align 8
  %79 = load i32, ptr %52, align 4
  %80 = load i32, ptr %54, align 4
  %81 = mul i32 %79, %40
  %82 = sub i32 %81, %39
  %83 = add i32 %43, %82
  %84 = mul i32 %83, %80
  %85 = add i32 %84, 1
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %78, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %88, float 0x3E45798EE0000000)
  %90 = load ptr, ptr %64, align 8
  %91 = load i32, ptr %66, align 4
  %92 = load i32, ptr %68, align 4
  %93 = mul i32 %91, %40
  %94 = sub i32 %93, %39
  %95 = add i32 %43, %94
  %96 = mul i32 %95, %92
  %97 = add i32 %96, 1
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %90, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = fdiv reassoc ninf nsz float %100, %89
  store float %101, ptr %99, align 4
  %102 = load ptr, ptr %50, align 8
  %103 = load i32, ptr %52, align 4
  %104 = load i32, ptr %54, align 4
  %105 = mul i32 %103, %40
  %106 = sub i32 %105, %39
  %107 = add i32 %43, %106
  %108 = mul i32 %107, %104
  %109 = add i32 %108, 2
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, ptr %102, i64 %110
  %112 = load float, ptr %111, align 4
  %113 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %112, float 0x3E45798EE0000000)
  %114 = load ptr, ptr %64, align 8
  %115 = load i32, ptr %66, align 4
  %116 = load i32, ptr %68, align 4
  %117 = mul i32 %115, %40
  %118 = sub i32 %117, %39
  %119 = add i32 %43, %118
  %120 = mul i32 %119, %116
  %121 = add i32 %120, 2
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, ptr %114, i64 %122
  %124 = load float, ptr %123, align 4
  %125 = fdiv reassoc ninf nsz float %124, %113
  store float %125, ptr %123, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %true_block, %for_loop_body
  %126 = add nsw i32 %.047, 1
  %exitcond.not = icmp eq i32 %18, %126
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.56, align 8
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
