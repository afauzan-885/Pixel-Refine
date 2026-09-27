; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.14 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @accumulate_spatial_merging_kernel_c754_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 88
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 16
  store i32 %2, ptr %7, align 4
  %8 = sitofp i32 %2 to float
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 80
  %11 = load i32, ptr %10, align 4
  %12 = sitofp i32 %11 to float
  %13 = fdiv reassoc ninf nsz float %8, %12
  %14 = load ptr, ptr %3, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 32872
  %16 = load ptr, ptr %15, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 8
  store float %13, ptr %17, align 4
  %18 = load ptr, ptr %context, align 8
  %19 = getelementptr i8, ptr %18, i64 92
  %20 = load i32, ptr %19, align 4
  %21 = load ptr, ptr %3, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 20
  store i32 %20, ptr %24, align 4
  %25 = sitofp i32 %20 to float
  %26 = load ptr, ptr %context, align 8
  %27 = getelementptr i8, ptr %26, i64 84
  %28 = load i32, ptr %27, align 4
  %29 = sitofp i32 %28 to float
  %30 = fdiv reassoc ninf nsz float %25, %29
  %31 = load ptr, ptr %3, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 32872
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 12
  store float %30, ptr %34, align 4
  %35 = tail call i32 @llvm.smax.i32(i32 %11, i32 0)
  %36 = tail call i32 @llvm.smax.i32(i32 %28, i32 0)
  %37 = load ptr, ptr %3, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 32872
  %39 = load ptr, ptr %38, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 4
  store i32 %36, ptr %40, align 4
  %41 = mul i32 %36, %35
  %42 = load ptr, ptr %3, align 8
  %43 = getelementptr inbounds nuw i8, ptr %42, i64 32872
  %44 = load ptr, ptr %43, align 8
  store i32 %41, ptr %44, align 4
  ret void
}

define void @accumulate_spatial_merging_kernel_c754_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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

; Function Attrs: nofree norecurse nounwind memory(readwrite, inaccessiblemem: none)
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
  %20 = getelementptr i8, ptr %19, i64 96
  %21 = load i32, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 32
  %24 = getelementptr i8, ptr %19, i64 28
  %25 = getelementptr i8, ptr %19, i64 72
  %26 = getelementptr i8, ptr %19, i64 68
  %27 = icmp sgt i32 %21, 0
  %28 = getelementptr i8, ptr %19, i64 16
  %29 = getelementptr i8, ptr %19, i64 4
  %30 = getelementptr i8, ptr %19, i64 8
  %31 = getelementptr i8, ptr %19, i64 56
  %32 = getelementptr i8, ptr %19, i64 44
  %33 = getelementptr i8, ptr %19, i64 48
  %xtraiter = and i32 %21, 1
  %34 = icmp eq i32 %21, 1
  %unroll_iter = and i32 %21, 2147483646
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.0712 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %183, %after_for3 ]
  %35 = load ptr, ptr %3, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 32872
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds nuw i8, ptr %37, i64 4
  %39 = load i32, ptr %38, align 4
  %40 = sdiv i32 %.0712, %39
  %41 = mul i32 %40, %39
  %42 = xor i32 %39, %.0712
  %43 = icmp slt i32 %42, 0
  %44 = icmp ne i32 %41, %.0712
  %45 = and i1 %43, %44
  %.neg8 = sext i1 %45 to i32
  %46 = add i32 %40, %.neg8
  %47 = mul i32 %46, %39
  %48 = sub i32 %.0712, %47
  %49 = sitofp i32 %46 to float
  %50 = getelementptr inbounds nuw i8, ptr %37, i64 8
  %51 = load float, ptr %50, align 4
  %52 = fmul reassoc ninf nsz float %51, %49
  %53 = sitofp i32 %48 to float
  %54 = getelementptr inbounds nuw i8, ptr %37, i64 12
  %55 = load float, ptr %54, align 4
  %56 = fmul reassoc ninf nsz float %55, %53
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %52)
  %58 = fptosi float %57 to i32
  %59 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %60 = fptosi float %59 to i32
  %61 = add i32 %58, 1
  %62 = getelementptr inbounds nuw i8, ptr %37, i64 16
  %63 = load i32, ptr %62, align 4
  %64 = add i32 %63, -1
  %65 = tail call i32 @llvm.smin.i32(i32 %61, i32 %64)
  %66 = add i32 %60, 1
  %67 = getelementptr inbounds nuw i8, ptr %37, i64 20
  %68 = load i32, ptr %67, align 4
  %69 = add i32 %68, -1
  %70 = tail call i32 @llvm.smin.i32(i32 %66, i32 %69)
  %71 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %72 = tail call i32 @llvm.smax.i32(i32 %60, i32 0)
  %73 = uitofp nneg i32 %71 to float
  %74 = fsub reassoc ninf nsz float %52, %73
  %75 = uitofp nneg i32 %72 to float
  %76 = fsub reassoc ninf nsz float %56, %75
  %77 = fsub reassoc ninf nsz float 1.000000e+00, %74
  %78 = load ptr, ptr %23, align 8
  %79 = load i32, ptr %24, align 4
  %80 = mul i32 %71, %79
  %81 = add i32 %72, %80
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, ptr %78, i64 %82
  %84 = load float, ptr %83, align 4
  %85 = fmul reassoc ninf nsz float %77, %84
  %86 = add i32 %70, %80
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, ptr %78, i64 %87
  %89 = load float, ptr %88, align 4
  %90 = fmul reassoc ninf nsz float %77, %89
  %91 = mul i32 %65, %79
  %92 = add i32 %91, %72
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %78, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = fmul reassoc ninf nsz float %74, %95
  %97 = add i32 %70, %91
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, ptr %78, i64 %98
  %100 = load float, ptr %99, align 4
  %101 = fmul reassoc ninf nsz float %74, %100
  %reass.add = fadd reassoc ninf nsz float %96, %85
  %reass.add9 = fadd reassoc ninf nsz float %101, %90
  %102 = fsub reassoc ninf nsz float %reass.add9, %reass.add
  %103 = fmul reassoc ninf nsz float %76, %102
  %104 = fadd reassoc ninf nsz float %reass.add, %103
  %105 = load ptr, ptr %25, align 8
  %106 = load i32, ptr %26, align 4
  %107 = mul i32 %106, %46
  %108 = add i32 %107, %48
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %105, i64 %109
  %111 = atomicrmw fadd ptr %110, float %104 seq_cst, align 4
  br i1 %27, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  br i1 %34, label %after_for3.loopexit.unr-lcssa, label %for_loop_body1.preheader14

for_loop_body1.preheader14:                       ; preds = %for_loop_body1.preheader
  %112 = mul i32 %39, -1
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader14
  %.011 = phi i32 [ %161, %for_loop_body1 ], [ 0, %for_loop_body1.preheader14 ]
  %113 = load ptr, ptr %28, align 8
  %114 = load i32, ptr %29, align 4
  %115 = load i32, ptr %30, align 4
  %116 = add i32 %112, %114
  %117 = mul i32 %46, %116
  %118 = add i32 %.0712, %117
  %119 = mul i32 %115, %118
  %120 = add i32 %.011, %119
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, ptr %113, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = fmul reassoc ninf nsz float %123, %104
  %125 = load ptr, ptr %31, align 8
  %126 = load i32, ptr %32, align 4
  %127 = load i32, ptr %33, align 4
  %128 = add i32 %112, %126
  %129 = mul i32 %46, %128
  %130 = add i32 %.0712, %129
  %131 = mul i32 %127, %130
  %132 = add i32 %.011, %131
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %125, i64 %133
  %135 = atomicrmw fadd ptr %134, float %124 seq_cst, align 4
  %136 = load ptr, ptr %28, align 8
  %137 = load i32, ptr %29, align 4
  %138 = load i32, ptr %30, align 4
  %139 = add i32 %112, %137
  %140 = mul i32 %46, %139
  %141 = add i32 %.0712, %140
  %142 = mul i32 %138, %141
  %143 = add i32 %.011, %142
  %144 = add i32 %143, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %136, i64 %145
  %147 = load float, ptr %146, align 4
  %148 = fmul reassoc ninf nsz float %147, %104
  %149 = load ptr, ptr %31, align 8
  %150 = load i32, ptr %32, align 4
  %151 = load i32, ptr %33, align 4
  %152 = add i32 %112, %150
  %153 = mul i32 %46, %152
  %154 = add i32 %.0712, %153
  %155 = mul i32 %151, %154
  %156 = add i32 %.011, %155
  %157 = add i32 %156, 1
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %149, i64 %158
  %160 = atomicrmw fadd ptr %159, float %148 seq_cst, align 4
  %161 = add nuw i32 %.011, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %161
  br i1 %niter.ncmp.1, label %after_for3.loopexit.unr-lcssa.loopexit, label %for_loop_body1

after_for3.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body1
  br label %after_for3.loopexit.unr-lcssa

after_for3.loopexit.unr-lcssa:                    ; preds = %after_for3.loopexit.unr-lcssa.loopexit, %for_loop_body1.preheader
  %.011.unr = phi i32 [ 0, %for_loop_body1.preheader ], [ %161, %after_for3.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for3, label %for_loop_body1.epil

for_loop_body1.epil:                              ; preds = %after_for3.loopexit.unr-lcssa
  %162 = load ptr, ptr %28, align 8
  %163 = load i32, ptr %29, align 4
  %164 = load i32, ptr %30, align 4
  %165 = mul i32 %163, %46
  %166 = add i32 %165, %48
  %167 = mul i32 %166, %164
  %168 = add i32 %167, %.011.unr
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %162, i64 %169
  %171 = load float, ptr %170, align 4
  %172 = fmul reassoc ninf nsz float %171, %104
  %173 = load ptr, ptr %31, align 8
  %174 = load i32, ptr %32, align 4
  %175 = load i32, ptr %33, align 4
  %176 = mul i32 %174, %46
  %177 = add i32 %176, %48
  %178 = mul i32 %177, %175
  %179 = add i32 %178, %.011.unr
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %173, i64 %180
  %182 = atomicrmw fadd ptr %181, float %172 seq_cst, align 4
  br label %after_for3

after_for3:                                       ; preds = %for_loop_body1.epil, %after_for3.loopexit.unr-lcssa, %for_loop_body
  %183 = add nsw i32 %.0712, 1
  %exitcond13.not = icmp eq i32 %183, %18
  br i1 %exitcond13.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.14, align 8
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
attributes #1 = { nofree norecurse nounwind memory(readwrite, inaccessiblemem: none) }
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
