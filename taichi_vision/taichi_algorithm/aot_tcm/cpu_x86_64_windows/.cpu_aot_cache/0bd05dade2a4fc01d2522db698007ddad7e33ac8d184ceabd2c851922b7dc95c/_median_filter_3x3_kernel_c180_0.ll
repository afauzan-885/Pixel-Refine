; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_median_filter_3x3_kernel_c180_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_median_filter_3x3_kernel_c180_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  br label %for_loop_body5.lr.ph

after_for.loopexit:                               ; preds = %for_loop_body5.lr.ph
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body5.lr.ph:                             ; preds = %for_loop_body5.lr.ph, %for_loop_body.lr.ph
  %.01117 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %140, %for_loop_body5.lr.ph ]
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 4
  %29 = load i32, ptr %28, align 4
  %30 = sdiv i32 %.01117, %29
  %31 = mul i32 %30, %29
  %32 = xor i32 %29, %.01117
  %33 = icmp slt i32 %32, 0
  %34 = icmp ne i32 %.01117, %31
  %35 = and i1 %33, %34
  %.neg14 = sext i1 %35 to i32
  %36 = add i32 %30, %.neg14
  %37 = mul i32 %29, -1
  %38 = mul i32 %37, %36
  %39 = add i32 %.01117, %38
  %40 = add i32 %36, -1
  %41 = getelementptr inbounds nuw i8, ptr %27, i64 8
  %42 = load i32, ptr %41, align 4
  %43 = add i32 %42, -1
  %44 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %45 = tail call i32 @llvm.smin.i32(i32 %43, i32 %44)
  %46 = add i32 %39, -1
  %47 = getelementptr inbounds nuw i8, ptr %27, i64 12
  %48 = load i32, ptr %47, align 4
  %49 = add i32 %48, -1
  %50 = tail call i32 @llvm.smax.i32(i32 %46, i32 0)
  %51 = tail call i32 @llvm.smin.i32(i32 %49, i32 %50)
  %52 = load ptr, ptr %21, align 8
  %53 = load i32, ptr %22, align 4
  %54 = mul i32 %45, %53
  %55 = add i32 %51, %54
  %56 = sext i32 %55 to i64
  %57 = getelementptr float, ptr %52, i64 %56
  %58 = load float, ptr %57, align 4
  %59 = tail call i32 @llvm.smax.i32(i32 %39, i32 0)
  %60 = tail call i32 @llvm.smin.i32(i32 %49, i32 %59)
  %61 = add i32 %54, %60
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, ptr %52, i64 %62
  %64 = load float, ptr %63, align 4
  %65 = add i32 %39, 1
  %66 = tail call i32 @llvm.smax.i32(i32 %65, i32 0)
  %67 = tail call i32 @llvm.smin.i32(i32 %49, i32 %66)
  %68 = add i32 %67, %54
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, ptr %52, i64 %69
  %71 = load float, ptr %70, align 4
  %72 = tail call i32 @llvm.smax.i32(i32 %36, i32 0)
  %73 = tail call i32 @llvm.smin.i32(i32 %43, i32 %72)
  %74 = mul i32 %73, %53
  %75 = add i32 %51, %74
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, ptr %52, i64 %76
  %78 = load float, ptr %77, align 4
  %79 = add i32 %60, %74
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, ptr %52, i64 %80
  %82 = load float, ptr %81, align 4
  %83 = add i32 %67, %74
  %84 = sext i32 %83 to i64
  %85 = getelementptr float, ptr %52, i64 %84
  %86 = load float, ptr %85, align 4
  %87 = add i32 %36, 1
  %88 = tail call i32 @llvm.smax.i32(i32 %87, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %43, i32 %88)
  %90 = mul i32 %89, %53
  %91 = add i32 %51, %90
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, ptr %52, i64 %92
  %94 = load float, ptr %93, align 4
  %95 = add i32 %90, %60
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %52, i64 %96
  %98 = load float, ptr %97, align 4
  %99 = add i32 %67, %90
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %52, i64 %100
  %102 = load float, ptr %101, align 4
  %103 = fcmp reassoc ninf nsz olt float %64, %58
  %.sroa.17.0 = select i1 %103, float %58, float %64
  %.sroa.0.0 = select i1 %103, float %64, float %58
  %104 = fcmp reassoc ninf nsz olt float %71, %.sroa.0.0
  %.sroa.34.8 = select i1 %104, float %.sroa.0.0, float %71
  %.sroa.0.1 = select i1 %104, float %71, float %.sroa.0.0
  %105 = fcmp reassoc ninf nsz olt float %78, %.sroa.0.1
  %.sroa.51.9 = select i1 %105, float %.sroa.0.1, float %78
  %.sroa.0.2 = select i1 %105, float %78, float %.sroa.0.1
  %106 = fcmp reassoc ninf nsz olt float %82, %.sroa.0.2
  %.sroa.68.12 = select i1 %106, float %.sroa.0.2, float %82
  %.sroa.0.3 = select i1 %106, float %82, float %.sroa.0.2
  %107 = fcmp reassoc ninf nsz olt float %86, %.sroa.0.3
  %.sroa.86.11 = select i1 %107, float %.sroa.0.3, float %86
  %.sroa.0.4 = select i1 %107, float %86, float %.sroa.0.3
  %108 = fcmp reassoc ninf nsz olt float %94, %.sroa.0.4
  %.sroa.103.12 = select i1 %108, float %.sroa.0.4, float %94
  %.sroa.0.5 = select i1 %108, float %94, float %.sroa.0.4
  %109 = fcmp reassoc ninf nsz olt float %98, %.sroa.0.5
  %.sroa.120.13 = select i1 %109, float %.sroa.0.5, float %98
  %.sroa.0.6 = select i1 %109, float %98, float %.sroa.0.5
  %110 = fcmp reassoc ninf nsz olt float %102, %.sroa.0.6
  %.sroa.137.13 = select i1 %110, float %.sroa.0.6, float %102
  %111 = fcmp reassoc ninf nsz olt float %.sroa.34.8, %.sroa.17.0
  %.sroa.34.1 = select i1 %111, float %.sroa.17.0, float %.sroa.34.8
  %.sroa.17.2 = select i1 %111, float %.sroa.34.8, float %.sroa.17.0
  %112 = fcmp reassoc ninf nsz olt float %.sroa.51.9, %.sroa.17.2
  %.sroa.51.8 = select i1 %112, float %.sroa.17.2, float %.sroa.51.9
  %.sroa.17.3 = select i1 %112, float %.sroa.51.9, float %.sroa.17.2
  %113 = fcmp reassoc ninf nsz olt float %.sroa.68.12, %.sroa.17.3
  %.sroa.68.11 = select i1 %113, float %.sroa.17.3, float %.sroa.68.12
  %.sroa.17.4 = select i1 %113, float %.sroa.68.12, float %.sroa.17.3
  %114 = fcmp reassoc ninf nsz olt float %.sroa.86.11, %.sroa.17.4
  %.sroa.86.10 = select i1 %114, float %.sroa.17.4, float %.sroa.86.11
  %.sroa.17.5 = select i1 %114, float %.sroa.86.11, float %.sroa.17.4
  %115 = fcmp reassoc ninf nsz olt float %.sroa.103.12, %.sroa.17.5
  %.sroa.103.11 = select i1 %115, float %.sroa.17.5, float %.sroa.103.12
  %.sroa.17.6 = select i1 %115, float %.sroa.103.12, float %.sroa.17.5
  %116 = fcmp reassoc ninf nsz olt float %.sroa.120.13, %.sroa.17.6
  %.sroa.120.12 = select i1 %116, float %.sroa.17.6, float %.sroa.120.13
  %.sroa.17.7 = select i1 %116, float %.sroa.120.13, float %.sroa.17.6
  %117 = fcmp reassoc ninf nsz olt float %.sroa.137.13, %.sroa.17.7
  %.sroa.137.12 = select i1 %117, float %.sroa.17.7, float %.sroa.137.13
  %118 = fcmp reassoc ninf nsz olt float %.sroa.51.8, %.sroa.34.1
  %.sroa.51.2 = select i1 %118, float %.sroa.34.1, float %.sroa.51.8
  %.sroa.34.3 = select i1 %118, float %.sroa.51.8, float %.sroa.34.1
  %119 = fcmp reassoc ninf nsz olt float %.sroa.68.11, %.sroa.34.3
  %.sroa.68.10 = select i1 %119, float %.sroa.34.3, float %.sroa.68.11
  %.sroa.34.4 = select i1 %119, float %.sroa.68.11, float %.sroa.34.3
  %120 = fcmp reassoc ninf nsz olt float %.sroa.86.10, %.sroa.34.4
  %.sroa.86.9 = select i1 %120, float %.sroa.34.4, float %.sroa.86.10
  %.sroa.34.5 = select i1 %120, float %.sroa.86.10, float %.sroa.34.4
  %121 = fcmp reassoc ninf nsz olt float %.sroa.103.11, %.sroa.34.5
  %.sroa.103.10 = select i1 %121, float %.sroa.34.5, float %.sroa.103.11
  %.sroa.34.6 = select i1 %121, float %.sroa.103.11, float %.sroa.34.5
  %122 = fcmp reassoc ninf nsz olt float %.sroa.120.12, %.sroa.34.6
  %.sroa.120.11 = select i1 %122, float %.sroa.34.6, float %.sroa.120.12
  %.sroa.34.7 = select i1 %122, float %.sroa.120.12, float %.sroa.34.6
  %123 = fcmp reassoc ninf nsz olt float %.sroa.137.12, %.sroa.34.7
  %.sroa.137.11 = select i1 %123, float %.sroa.34.7, float %.sroa.137.12
  %124 = fcmp reassoc ninf nsz olt float %.sroa.68.10, %.sroa.51.2
  %.sroa.68.3 = select i1 %124, float %.sroa.51.2, float %.sroa.68.10
  %.sroa.51.4 = select i1 %124, float %.sroa.68.10, float %.sroa.51.2
  %125 = fcmp reassoc ninf nsz olt float %.sroa.86.9, %.sroa.51.4
  %.sroa.86.8 = select i1 %125, float %.sroa.51.4, float %.sroa.86.9
  %.sroa.51.5 = select i1 %125, float %.sroa.86.9, float %.sroa.51.4
  %126 = fcmp reassoc ninf nsz olt float %.sroa.103.10, %.sroa.51.5
  %.sroa.103.9 = select i1 %126, float %.sroa.51.5, float %.sroa.103.10
  %.sroa.51.6 = select i1 %126, float %.sroa.103.10, float %.sroa.51.5
  %127 = fcmp reassoc ninf nsz olt float %.sroa.120.11, %.sroa.51.6
  %.sroa.120.10 = select i1 %127, float %.sroa.51.6, float %.sroa.120.11
  %.sroa.51.7 = select i1 %127, float %.sroa.120.11, float %.sroa.51.6
  %128 = fcmp reassoc ninf nsz olt float %.sroa.137.11, %.sroa.51.7
  %.sroa.137.10 = select i1 %128, float %.sroa.51.7, float %.sroa.137.11
  %129 = fcmp reassoc ninf nsz olt float %.sroa.86.8, %.sroa.68.3
  %.sroa.68.5 = select i1 %129, float %.sroa.86.8, float %.sroa.68.3
  %130 = fcmp reassoc ninf nsz olt float %.sroa.103.9, %.sroa.68.5
  %.sroa.68.7 = select i1 %130, float %.sroa.103.9, float %.sroa.68.5
  %131 = fcmp reassoc ninf nsz olt float %.sroa.120.10, %.sroa.68.7
  %.sroa.68.8 = select i1 %131, float %.sroa.120.10, float %.sroa.68.7
  %132 = fcmp reassoc ninf nsz olt float %.sroa.137.10, %.sroa.68.8
  %.sroa.68.9 = select i1 %132, float %.sroa.137.10, float %.sroa.68.8
  %133 = load ptr, ptr %23, align 8
  %134 = load i32, ptr %24, align 4
  %135 = sub i32 %134, %29
  %136 = mul i32 %135, %36
  %137 = add i32 %.01117, %136
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %133, i64 %138
  store float %.sroa.68.9, ptr %139, align 4
  %140 = add nsw i32 %.01117, 1
  %exitcond.not = icmp eq i32 %18, %140
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body5.lr.ph
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.0, align 8
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
