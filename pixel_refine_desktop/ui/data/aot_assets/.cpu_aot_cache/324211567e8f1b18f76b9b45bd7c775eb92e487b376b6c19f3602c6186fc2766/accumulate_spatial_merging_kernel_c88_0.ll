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
  %24 = getelementptr i8, ptr %19, i64 96
  %25 = load i32, ptr %24, align 4
  %26 = sitofp i32 %21 to float
  %27 = sitofp i32 %23 to float
  %28 = add i32 %21, -1
  %29 = add i32 %23, -1
  %30 = icmp slt i32 %16, %18
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = getelementptr i8, ptr %19, i64 32
  %32 = getelementptr i8, ptr %19, i64 28
  %33 = getelementptr i8, ptr %19, i64 72
  %34 = getelementptr i8, ptr %19, i64 68
  %35 = icmp sgt i32 %25, 0
  %36 = getelementptr i8, ptr %19, i64 16
  %37 = getelementptr i8, ptr %19, i64 4
  %38 = getelementptr i8, ptr %19, i64 8
  %39 = getelementptr i8, ptr %19, i64 56
  %40 = getelementptr i8, ptr %19, i64 44
  %41 = getelementptr i8, ptr %19, i64 48
  %xtraiter = and i32 %25, 1
  %42 = icmp eq i32 %25, 1
  %unroll_iter = and i32 %25, 2147483646
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.0712 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %189, %after_for3 ]
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
  %58 = fmul reassoc ninf nsz float %57, %26
  %59 = getelementptr inbounds nuw i8, ptr %45, i64 8
  %60 = load i32, ptr %59, align 4
  %61 = sitofp i32 %60 to float
  %62 = fdiv reassoc ninf nsz float %58, %61
  %63 = sitofp i32 %56 to float
  %64 = fmul reassoc ninf nsz float %63, %27
  %65 = getelementptr inbounds nuw i8, ptr %45, i64 12
  %66 = load i32, ptr %65, align 4
  %67 = sitofp i32 %66 to float
  %68 = fdiv reassoc ninf nsz float %64, %67
  %69 = tail call reassoc ninf nsz float @llvm.floor.f32(float %62)
  %70 = fptosi float %69 to i32
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %68)
  %72 = fptosi float %71 to i32
  %73 = add i32 %70, 1
  %74 = tail call i32 @llvm.smin.i32(i32 %73, i32 %28)
  %75 = add i32 %72, 1
  %76 = tail call i32 @llvm.smin.i32(i32 %75, i32 %29)
  %77 = tail call i32 @llvm.smax.i32(i32 %70, i32 0)
  %78 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %79 = uitofp nneg i32 %77 to float
  %80 = fsub reassoc ninf nsz float %62, %79
  %81 = uitofp nneg i32 %78 to float
  %82 = fsub reassoc ninf nsz float %68, %81
  %83 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %84 = load ptr, ptr %31, align 8
  %85 = load i32, ptr %32, align 4
  %86 = mul i32 %77, %85
  %87 = add i32 %78, %86
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, ptr %84, i64 %88
  %90 = load float, ptr %89, align 4
  %91 = fmul reassoc ninf nsz float %83, %90
  %92 = add i32 %76, %86
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %84, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = fmul reassoc ninf nsz float %83, %95
  %97 = mul i32 %74, %85
  %98 = add i32 %97, %78
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, ptr %84, i64 %99
  %101 = load float, ptr %100, align 4
  %102 = fmul reassoc ninf nsz float %80, %101
  %103 = add i32 %76, %97
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, ptr %84, i64 %104
  %106 = load float, ptr %105, align 4
  %107 = fmul reassoc ninf nsz float %80, %106
  %reass.add = fadd reassoc ninf nsz float %102, %91
  %reass.add9 = fadd reassoc ninf nsz float %107, %96
  %108 = fsub reassoc ninf nsz float %reass.add9, %reass.add
  %109 = fmul reassoc ninf nsz float %82, %108
  %110 = fadd reassoc ninf nsz float %reass.add, %109
  %111 = load ptr, ptr %33, align 8
  %112 = load i32, ptr %34, align 4
  %113 = mul i32 %112, %54
  %114 = add i32 %113, %56
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, ptr %111, i64 %115
  %117 = atomicrmw fadd ptr %116, float %110 seq_cst, align 4
  br i1 %35, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  br i1 %42, label %after_for3.loopexit.unr-lcssa, label %for_loop_body1.preheader14

for_loop_body1.preheader14:                       ; preds = %for_loop_body1.preheader
  %118 = mul i32 %47, -1
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader14
  %.011 = phi i32 [ %167, %for_loop_body1 ], [ 0, %for_loop_body1.preheader14 ]
  %119 = load ptr, ptr %36, align 8
  %120 = load i32, ptr %37, align 4
  %121 = load i32, ptr %38, align 4
  %122 = add i32 %118, %120
  %123 = mul i32 %54, %122
  %124 = add i32 %.0712, %123
  %125 = mul i32 %121, %124
  %126 = add i32 %.011, %125
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, ptr %119, i64 %127
  %129 = load float, ptr %128, align 4
  %130 = fmul reassoc ninf nsz float %129, %110
  %131 = load ptr, ptr %39, align 8
  %132 = load i32, ptr %40, align 4
  %133 = load i32, ptr %41, align 4
  %134 = add i32 %118, %132
  %135 = mul i32 %54, %134
  %136 = add i32 %.0712, %135
  %137 = mul i32 %133, %136
  %138 = add i32 %.011, %137
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, ptr %131, i64 %139
  %141 = atomicrmw fadd ptr %140, float %130 seq_cst, align 4
  %142 = load ptr, ptr %36, align 8
  %143 = load i32, ptr %37, align 4
  %144 = load i32, ptr %38, align 4
  %145 = add i32 %118, %143
  %146 = mul i32 %54, %145
  %147 = add i32 %.0712, %146
  %148 = mul i32 %144, %147
  %149 = add i32 %.011, %148
  %150 = add i32 %149, 1
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %142, i64 %151
  %153 = load float, ptr %152, align 4
  %154 = fmul reassoc ninf nsz float %153, %110
  %155 = load ptr, ptr %39, align 8
  %156 = load i32, ptr %40, align 4
  %157 = load i32, ptr %41, align 4
  %158 = add i32 %118, %156
  %159 = mul i32 %54, %158
  %160 = add i32 %.0712, %159
  %161 = mul i32 %157, %160
  %162 = add i32 %.011, %161
  %163 = add i32 %162, 1
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %155, i64 %164
  %166 = atomicrmw fadd ptr %165, float %154 seq_cst, align 4
  %167 = add nuw i32 %.011, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %167
  br i1 %niter.ncmp.1, label %after_for3.loopexit.unr-lcssa.loopexit, label %for_loop_body1

after_for3.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body1
  br label %after_for3.loopexit.unr-lcssa

after_for3.loopexit.unr-lcssa:                    ; preds = %after_for3.loopexit.unr-lcssa.loopexit, %for_loop_body1.preheader
  %.011.unr = phi i32 [ 0, %for_loop_body1.preheader ], [ %167, %after_for3.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for3, label %for_loop_body1.epil

for_loop_body1.epil:                              ; preds = %after_for3.loopexit.unr-lcssa
  %168 = load ptr, ptr %36, align 8
  %169 = load i32, ptr %37, align 4
  %170 = load i32, ptr %38, align 4
  %171 = mul i32 %169, %54
  %172 = add i32 %171, %56
  %173 = mul i32 %172, %170
  %174 = add i32 %173, %.011.unr
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %168, i64 %175
  %177 = load float, ptr %176, align 4
  %178 = fmul reassoc ninf nsz float %177, %110
  %179 = load ptr, ptr %39, align 8
  %180 = load i32, ptr %40, align 4
  %181 = load i32, ptr %41, align 4
  %182 = mul i32 %180, %54
  %183 = add i32 %182, %56
  %184 = mul i32 %183, %181
  %185 = add i32 %184, %.011.unr
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, ptr %179, i64 %186
  %188 = atomicrmw fadd ptr %187, float %178 seq_cst, align 4
  br label %after_for3

after_for3:                                       ; preds = %for_loop_body1.epil, %after_for3.loopexit.unr-lcssa, %for_loop_body
  %189 = add nsw i32 %.0712, 1
  %exitcond13.not = icmp eq i32 %189, %18
  br i1 %exitcond13.not, label %after_for.loopexit, label %for_loop_body
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
