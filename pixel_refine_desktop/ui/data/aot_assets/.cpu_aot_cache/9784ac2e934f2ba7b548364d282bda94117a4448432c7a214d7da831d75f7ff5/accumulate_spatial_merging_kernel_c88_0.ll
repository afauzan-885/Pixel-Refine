; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.8 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @accumulate_spatial_merging_kernel_c88_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 80
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 84
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

define void @accumulate_spatial_merging_kernel_c88_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 88
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 92
  %23 = load i32, ptr %22, align 4
  %24 = sitofp i32 %21 to float
  %25 = sitofp i32 %23 to float
  %26 = add i32 %21, -1
  %27 = add i32 %23, -1
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr i8, ptr %19, i64 96
  %30 = load i32, ptr %29, align 4
  %31 = getelementptr i8, ptr %19, i64 32
  %32 = getelementptr i8, ptr %19, i64 28
  %33 = getelementptr i8, ptr %19, i64 72
  %34 = getelementptr i8, ptr %19, i64 68
  %35 = icmp sgt i32 %30, 0
  %36 = getelementptr i8, ptr %19, i64 16
  %37 = getelementptr i8, ptr %19, i64 4
  %38 = getelementptr i8, ptr %19, i64 8
  %39 = getelementptr i8, ptr %19, i64 56
  %40 = getelementptr i8, ptr %19, i64 44
  %41 = getelementptr i8, ptr %19, i64 48
  %wide.trip.count = zext i32 %30 to i64
  %xtraiter = and i64 %wide.trip.count, 1
  %42 = icmp eq i32 %30, 1
  %unroll_iter = and i64 %wide.trip.count, 2147483646
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.0712 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %185, %after_for3 ]
  %43 = load ptr, ptr %3, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 32872
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds nuw i8, ptr %45, i64 4
  %47 = load i32, ptr %46, align 4
  %48 = sdiv i32 %.0712, %47
  %49 = mul i32 %48, %47
  %50 = xor i32 %47, %.0712
  %51 = icmp slt i32 %50, 0
  %52 = icmp ne i32 %49, %.0712
  %53 = and i1 %51, %52
  %.neg8 = sext i1 %53 to i32
  %54 = add i32 %48, %.neg8
  %55 = mul i32 %54, %47
  %56 = sub i32 %.0712, %55
  %57 = sitofp i32 %54 to float
  %58 = fmul reassoc ninf nsz float %57, %24
  %59 = getelementptr inbounds nuw i8, ptr %45, i64 8
  %60 = load i32, ptr %59, align 4
  %61 = sitofp i32 %60 to float
  %62 = fdiv reassoc ninf nsz float %58, %61
  %63 = sitofp i32 %56 to float
  %64 = fmul reassoc ninf nsz float %63, %25
  %65 = getelementptr inbounds nuw i8, ptr %45, i64 12
  %66 = load i32, ptr %65, align 4
  %67 = sitofp i32 %66 to float
  %68 = fdiv reassoc ninf nsz float %64, %67
  %69 = tail call reassoc ninf nsz float @llvm.floor.f32(float %62)
  %70 = fptosi float %69 to i32
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %68)
  %72 = fptosi float %71 to i32
  %73 = add i32 %70, 1
  %74 = tail call i32 @llvm.smin.i32(i32 %73, i32 %26)
  %75 = add i32 %72, 1
  %76 = tail call i32 @llvm.smin.i32(i32 %75, i32 %27)
  %77 = tail call i32 @llvm.smax.i32(i32 %70, i32 0)
  %78 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %79 = uitofp nneg i32 %77 to float
  %80 = fsub reassoc ninf nsz float %62, %79
  %81 = uitofp nneg i32 %78 to float
  %82 = fsub reassoc ninf nsz float %68, %81
  %83 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %84 = load ptr, ptr %31, align 8
  %85 = load i32, ptr %32, align 4
  %86 = sext i32 %85 to i64
  %87 = zext nneg i32 %77 to i64
  %88 = mul nsw i64 %87, %86
  %89 = zext nneg i32 %78 to i64
  %90 = getelementptr float, ptr %84, i64 %88
  %91 = getelementptr float, ptr %90, i64 %89
  %92 = load float, ptr %91, align 4
  %93 = fmul reassoc ninf nsz float %83, %92
  %94 = sext i32 %76 to i64
  %95 = getelementptr float, ptr %90, i64 %94
  %96 = load float, ptr %95, align 4
  %97 = fmul reassoc ninf nsz float %83, %96
  %98 = sext i32 %74 to i64
  %99 = mul nsw i64 %98, %86
  %100 = getelementptr float, ptr %84, i64 %99
  %101 = getelementptr float, ptr %100, i64 %89
  %102 = load float, ptr %101, align 4
  %103 = fmul reassoc ninf nsz float %80, %102
  %104 = getelementptr float, ptr %100, i64 %94
  %105 = load float, ptr %104, align 4
  %106 = fmul reassoc ninf nsz float %80, %105
  %reass.add = fadd reassoc ninf nsz float %103, %93
  %reass.add9 = fadd reassoc ninf nsz float %106, %97
  %107 = fsub reassoc ninf nsz float %reass.add9, %reass.add
  %108 = fmul reassoc ninf nsz float %82, %107
  %109 = fadd reassoc ninf nsz float %reass.add, %108
  %110 = load ptr, ptr %33, align 8
  %111 = load i32, ptr %34, align 4
  %112 = sext i32 %111 to i64
  %113 = sext i32 %54 to i64
  %114 = mul nsw i64 %112, %113
  %115 = sext i32 %56 to i64
  %116 = getelementptr float, ptr %110, i64 %114
  %117 = getelementptr float, ptr %116, i64 %115
  %118 = atomicrmw fadd ptr %117, float %109 seq_cst, align 4
  br i1 %35, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  br i1 %42, label %after_for3.loopexit.unr-lcssa, label %for_loop_body1.preheader15

for_loop_body1.preheader15:                       ; preds = %for_loop_body1.preheader
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader15
  %indvars.iv = phi i64 [ %indvars.iv.next.1, %for_loop_body1 ], [ 0, %for_loop_body1.preheader15 ]
  %119 = load ptr, ptr %36, align 8
  %120 = load i32, ptr %37, align 4
  %121 = sext i32 %120 to i64
  %122 = load i32, ptr %38, align 4
  %123 = sext i32 %122 to i64
  %124 = mul nsw i64 %121, %113
  %125 = add nsw i64 %115, %124
  %126 = shl i64 %125, 2
  %127 = mul i64 %126, %123
  %scevgep23 = getelementptr i8, ptr %119, i64 %127
  %128 = shl i64 %indvars.iv, 2
  %scevgep24 = getelementptr i8, ptr %scevgep23, i64 %128
  %129 = load float, ptr %scevgep24, align 4
  %130 = fmul reassoc ninf nsz float %129, %109
  %131 = load ptr, ptr %39, align 8
  %132 = load i32, ptr %40, align 4
  %133 = sext i32 %132 to i64
  %134 = load i32, ptr %41, align 4
  %135 = sext i32 %134 to i64
  %136 = mul nsw i64 %133, %113
  %137 = add nsw i64 %115, %136
  %138 = shl i64 %137, 2
  %139 = mul i64 %138, %135
  %scevgep21 = getelementptr i8, ptr %131, i64 %139
  %scevgep22 = getelementptr i8, ptr %scevgep21, i64 %128
  %140 = atomicrmw fadd ptr %scevgep22, float %130 seq_cst, align 4
  %141 = load ptr, ptr %36, align 8
  %142 = load i32, ptr %37, align 4
  %143 = sext i32 %142 to i64
  %144 = load i32, ptr %38, align 4
  %145 = sext i32 %144 to i64
  %146 = mul nsw i64 %143, %113
  %147 = add nsw i64 %115, %146
  %148 = shl i64 %147, 2
  %149 = mul i64 %148, %145
  %scevgep = getelementptr i8, ptr %141, i64 %149
  %scevgep16 = getelementptr i8, ptr %scevgep, i64 %128
  %scevgep17 = getelementptr i8, ptr %scevgep16, i64 4
  %150 = load float, ptr %scevgep17, align 4
  %151 = fmul reassoc ninf nsz float %150, %109
  %152 = load ptr, ptr %39, align 8
  %153 = load i32, ptr %40, align 4
  %154 = sext i32 %153 to i64
  %155 = load i32, ptr %41, align 4
  %156 = sext i32 %155 to i64
  %157 = mul nsw i64 %154, %113
  %158 = add nsw i64 %115, %157
  %159 = shl i64 %158, 2
  %160 = mul i64 %159, %156
  %scevgep18 = getelementptr i8, ptr %152, i64 %160
  %scevgep19 = getelementptr i8, ptr %scevgep18, i64 %128
  %scevgep20 = getelementptr i8, ptr %scevgep19, i64 4
  %161 = atomicrmw fadd ptr %scevgep20, float %151 seq_cst, align 4
  %indvars.iv.next.1 = add nuw i64 %indvars.iv, 2
  %niter.ncmp.1 = icmp eq i64 %unroll_iter, %indvars.iv.next.1
  br i1 %niter.ncmp.1, label %after_for3.loopexit.unr-lcssa.loopexit, label %for_loop_body1

after_for3.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body1
  br label %after_for3.loopexit.unr-lcssa

after_for3.loopexit.unr-lcssa:                    ; preds = %after_for3.loopexit.unr-lcssa.loopexit, %for_loop_body1.preheader
  %indvars.iv.unr = phi i64 [ 0, %for_loop_body1.preheader ], [ %indvars.iv.next.1, %after_for3.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for3, label %for_loop_body1.epil

for_loop_body1.epil:                              ; preds = %after_for3.loopexit.unr-lcssa
  %162 = load ptr, ptr %36, align 8
  %163 = load i32, ptr %37, align 4
  %164 = sext i32 %163 to i64
  %165 = load i32, ptr %38, align 4
  %166 = sext i32 %165 to i64
  %167 = mul nsw i64 %164, %113
  %168 = add nsw i64 %167, %115
  %169 = mul i64 %168, %166
  %170 = getelementptr float, ptr %162, i64 %169
  %171 = getelementptr float, ptr %170, i64 %indvars.iv.unr
  %172 = load float, ptr %171, align 4
  %173 = fmul reassoc ninf nsz float %172, %109
  %174 = load ptr, ptr %39, align 8
  %175 = load i32, ptr %40, align 4
  %176 = sext i32 %175 to i64
  %177 = load i32, ptr %41, align 4
  %178 = sext i32 %177 to i64
  %179 = mul nsw i64 %176, %113
  %180 = add nsw i64 %179, %115
  %181 = mul i64 %180, %178
  %182 = getelementptr float, ptr %174, i64 %181
  %183 = getelementptr float, ptr %182, i64 %indvars.iv.unr
  %184 = atomicrmw fadd ptr %183, float %173 seq_cst, align 4
  br label %after_for3

after_for3:                                       ; preds = %for_loop_body1.epil, %after_for3.loopexit.unr-lcssa, %for_loop_body
  %185 = add nsw i32 %.0712, 1
  %exitcond14.not = icmp eq i32 %185, %18
  br i1 %exitcond14.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.8, align 8
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
