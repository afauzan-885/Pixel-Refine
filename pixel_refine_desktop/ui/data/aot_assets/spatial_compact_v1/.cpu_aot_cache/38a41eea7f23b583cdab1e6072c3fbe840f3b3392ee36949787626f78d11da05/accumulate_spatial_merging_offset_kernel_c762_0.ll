; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.22 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @accumulate_spatial_merging_offset_kernel_c762_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 88
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 24
  store i32 %2, ptr %7, align 4
  %8 = sitofp i32 %2 to float
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 80
  %11 = load i32, ptr %10, align 4
  %12 = load ptr, ptr %3, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 8
  store i32 %11, ptr %15, align 4
  %16 = sitofp i32 %11 to float
  %17 = fdiv reassoc ninf nsz float %8, %16
  %18 = load ptr, ptr %3, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  %21 = getelementptr inbounds nuw i8, ptr %20, i64 16
  store float %17, ptr %21, align 4
  %22 = load ptr, ptr %context, align 8
  %23 = getelementptr i8, ptr %22, i64 92
  %24 = load i32, ptr %23, align 4
  %25 = load ptr, ptr %3, align 8
  %26 = getelementptr inbounds nuw i8, ptr %25, i64 32872
  %27 = load ptr, ptr %26, align 8
  %28 = getelementptr inbounds nuw i8, ptr %27, i64 28
  store i32 %24, ptr %28, align 4
  %29 = sitofp i32 %24 to float
  %30 = load ptr, ptr %context, align 8
  %31 = getelementptr i8, ptr %30, i64 84
  %32 = load i32, ptr %31, align 4
  %33 = load ptr, ptr %3, align 8
  %34 = getelementptr inbounds nuw i8, ptr %33, i64 32872
  %35 = load ptr, ptr %34, align 8
  %36 = getelementptr inbounds nuw i8, ptr %35, i64 12
  store i32 %32, ptr %36, align 4
  %37 = sitofp i32 %32 to float
  %38 = fdiv reassoc ninf nsz float %29, %37
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 20
  store float %38, ptr %42, align 4
  %43 = load ptr, ptr %context, align 8
  %44 = getelementptr i8, ptr %43, i64 100
  %45 = load i32, ptr %44, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %47 = getelementptr i8, ptr %43, i64 104
  %48 = load i32, ptr %47, align 4
  %49 = tail call i32 @llvm.smax.i32(i32 %48, i32 0)
  %50 = load ptr, ptr %3, align 8
  %51 = getelementptr inbounds nuw i8, ptr %50, i64 32872
  %52 = load ptr, ptr %51, align 8
  %53 = getelementptr inbounds nuw i8, ptr %52, i64 4
  store i32 %49, ptr %53, align 4
  %54 = mul i32 %49, %46
  %55 = load ptr, ptr %3, align 8
  %56 = getelementptr inbounds nuw i8, ptr %55, i64 32872
  %57 = load ptr, ptr %56, align 8
  store i32 %54, ptr %57, align 4
  ret void
}

define void @accumulate_spatial_merging_offset_kernel_c762_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 108
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 112
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  %25 = add i32 %23, %16
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %lsr.iv = phi i32 [ %25, %for_loop_body.preheader ], [ %lsr.iv.next, %after_if3 ]
  %.0814 = phi i32 [ %150, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.0814, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.0814
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %32, %.0814
  %36 = and i1 %34, %35
  %.neg10 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg10
  %38 = mul i32 %37, %30
  %39 = sub i32 %.0814, %38
  %40 = add i32 %37, %21
  %41 = add i32 %39, %23
  %42 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %43 = load i32, ptr %42, align 4
  %44 = icmp slt i32 %40, %43
  br i1 %44, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %45 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %46 = load i32, ptr %45, align 4
  %47 = icmp slt i32 %41, %46
  br i1 %47, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %48 = sitofp i32 %40 to float
  %49 = getelementptr inbounds nuw i8, ptr %28, i64 16
  %50 = load float, ptr %49, align 4
  %51 = fmul reassoc ninf nsz float %50, %48
  %52 = sitofp i32 %41 to float
  %53 = getelementptr inbounds nuw i8, ptr %28, i64 20
  %54 = load float, ptr %53, align 4
  %55 = fmul reassoc ninf nsz float %54, %52
  %56 = tail call reassoc ninf nsz float @llvm.floor.f32(float %51)
  %57 = fptosi float %56 to i32
  %58 = tail call reassoc ninf nsz float @llvm.floor.f32(float %55)
  %59 = fptosi float %58 to i32
  %60 = add i32 %57, 1
  %61 = getelementptr inbounds nuw i8, ptr %28, i64 24
  %62 = load i32, ptr %61, align 4
  %63 = add i32 %62, -1
  %64 = tail call i32 @llvm.smin.i32(i32 %60, i32 %63)
  %65 = add i32 %59, 1
  %66 = getelementptr inbounds nuw i8, ptr %28, i64 28
  %67 = load i32, ptr %66, align 4
  %68 = add i32 %67, -1
  %69 = tail call i32 @llvm.smin.i32(i32 %65, i32 %68)
  %70 = tail call i32 @llvm.smax.i32(i32 %57, i32 0)
  %71 = tail call i32 @llvm.smax.i32(i32 %59, i32 0)
  %72 = uitofp nneg i32 %70 to float
  %73 = fsub reassoc ninf nsz float %51, %72
  %74 = uitofp nneg i32 %71 to float
  %75 = fsub reassoc ninf nsz float %55, %74
  %76 = fsub reassoc ninf nsz float 1.000000e+00, %75
  %77 = load ptr, ptr %0, align 8
  %78 = getelementptr i8, ptr %77, i64 32
  %79 = load ptr, ptr %78, align 8
  %80 = getelementptr i8, ptr %77, i64 28
  %81 = load i32, ptr %80, align 4
  %82 = mul i32 %81, %70
  %83 = add i32 %82, %71
  %84 = sext i32 %83 to i64
  %85 = getelementptr float, ptr %79, i64 %84
  %86 = load float, ptr %85, align 4
  %87 = fmul reassoc ninf nsz float %76, %86
  %88 = add i32 %82, %69
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, ptr %79, i64 %89
  %91 = load float, ptr %90, align 4
  %92 = fmul reassoc ninf nsz float %91, %75
  %93 = mul i32 %81, %64
  %94 = add i32 %93, %71
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, ptr %79, i64 %95
  %97 = load float, ptr %96, align 4
  %98 = fmul reassoc ninf nsz float %97, %76
  %99 = add i32 %93, %69
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %79, i64 %100
  %102 = load float, ptr %101, align 4
  %103 = fmul reassoc ninf nsz float %102, %75
  %reass.add = fadd reassoc ninf nsz float %103, %98
  %reass.add11 = fadd reassoc ninf nsz float %87, %92
  %104 = fsub reassoc ninf nsz float %reass.add, %reass.add11
  %105 = fmul reassoc ninf nsz float %73, %104
  %106 = fadd reassoc ninf nsz float %reass.add11, %105
  %107 = getelementptr i8, ptr %77, i64 72
  %108 = load ptr, ptr %107, align 8
  %109 = getelementptr i8, ptr %77, i64 68
  %110 = load i32, ptr %109, align 4
  %111 = mul i32 %110, %40
  %112 = add i32 %111, %41
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, ptr %108, i64 %113
  %115 = atomicrmw fadd ptr %114, float %106 seq_cst, align 4
  %116 = load ptr, ptr %0, align 8
  %117 = getelementptr i8, ptr %116, i64 96
  %118 = load i32, ptr %117, align 4
  %119 = icmp sgt i32 %118, 0
  br i1 %119, label %for_loop_body4.lr.ph, label %after_if3

for_loop_body4.lr.ph:                             ; preds = %true_block1
  %120 = getelementptr i8, ptr %116, i64 16
  %121 = getelementptr i8, ptr %116, i64 4
  %122 = getelementptr i8, ptr %116, i64 8
  %123 = getelementptr i8, ptr %116, i64 56
  %124 = getelementptr i8, ptr %116, i64 44
  %125 = getelementptr i8, ptr %116, i64 48
  %xtraiter = and i32 %118, 1
  %126 = icmp eq i32 %118, 1
  br i1 %126, label %after_if3.loopexit.unr-lcssa, label %for_loop_body4.lr.ph.new

for_loop_body4.lr.ph.new:                         ; preds = %for_loop_body4.lr.ph
  %unroll_iter = and i32 %118, 2147483646
  %127 = mul i32 %30, -1
  %128 = sub i32 %lsr.iv, %38
  br label %for_loop_body4

after_if3.loopexit.unr-lcssa.loopexit:            ; preds = %for_loop_body4
  br label %after_if3.loopexit.unr-lcssa

after_if3.loopexit.unr-lcssa:                     ; preds = %after_if3.loopexit.unr-lcssa.loopexit, %for_loop_body4.lr.ph
  %.013.unr = phi i32 [ 0, %for_loop_body4.lr.ph ], [ %197, %after_if3.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_if3, label %for_loop_body4.epil

for_loop_body4.epil:                              ; preds = %after_if3.loopexit.unr-lcssa
  %129 = load ptr, ptr %120, align 8
  %130 = load i32, ptr %121, align 4
  %131 = load i32, ptr %122, align 4
  %132 = mul i32 %130, %37
  %133 = add i32 %132, %39
  %134 = mul i32 %133, %131
  %135 = add i32 %134, %.013.unr
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %129, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = fmul reassoc ninf nsz float %138, %106
  %140 = load ptr, ptr %123, align 8
  %141 = load i32, ptr %124, align 4
  %142 = load i32, ptr %125, align 4
  %143 = mul i32 %141, %40
  %144 = add i32 %143, %41
  %145 = mul i32 %144, %142
  %146 = add i32 %145, %.013.unr
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, ptr %140, i64 %147
  %149 = atomicrmw fadd ptr %148, float %139 seq_cst, align 4
  br label %after_if3

after_if3:                                        ; preds = %for_loop_body4.epil, %after_if3.loopexit.unr-lcssa, %true_block1, %true_block, %for_loop_body
  %150 = add nsw i32 %.0814, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %exitcond15.not = icmp eq i32 %150, %18
  br i1 %exitcond15.not, label %after_for.loopexit, label %for_loop_body

for_loop_body4:                                   ; preds = %for_loop_body4, %for_loop_body4.lr.ph.new
  %.013 = phi i32 [ 0, %for_loop_body4.lr.ph.new ], [ %197, %for_loop_body4 ]
  %151 = load ptr, ptr %120, align 8
  %152 = load i32, ptr %121, align 4
  %153 = load i32, ptr %122, align 4
  %154 = add i32 %127, %152
  %155 = mul i32 %37, %154
  %156 = add i32 %.0814, %155
  %157 = mul i32 %153, %156
  %158 = add i32 %.013, %157
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %151, i64 %159
  %161 = load float, ptr %160, align 4
  %162 = fmul reassoc ninf nsz float %161, %106
  %163 = load ptr, ptr %123, align 8
  %164 = load i32, ptr %124, align 4
  %165 = load i32, ptr %125, align 4
  %166 = mul i32 %164, %40
  %167 = add i32 %128, %166
  %168 = mul i32 %165, %167
  %169 = add i32 %.013, %168
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, ptr %163, i64 %170
  %172 = atomicrmw fadd ptr %171, float %162 seq_cst, align 4
  %173 = load ptr, ptr %120, align 8
  %174 = load i32, ptr %121, align 4
  %175 = load i32, ptr %122, align 4
  %176 = add i32 %127, %174
  %177 = mul i32 %37, %176
  %178 = add i32 %.0814, %177
  %179 = mul i32 %175, %178
  %180 = add i32 %.013, %179
  %181 = add i32 %180, 1
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, ptr %173, i64 %182
  %184 = load float, ptr %183, align 4
  %185 = fmul reassoc ninf nsz float %184, %106
  %186 = load ptr, ptr %123, align 8
  %187 = load i32, ptr %124, align 4
  %188 = load i32, ptr %125, align 4
  %189 = mul i32 %187, %40
  %190 = add i32 %128, %189
  %191 = mul i32 %188, %190
  %192 = add i32 %.013, %191
  %193 = add i32 %192, 1
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, ptr %186, i64 %194
  %196 = atomicrmw fadd ptr %195, float %185 seq_cst, align 4
  %197 = add nuw i32 %.013, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %197
  br i1 %niter.ncmp.1, label %after_if3.loopexit.unr-lcssa.loopexit, label %for_loop_body4
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.22, align 8
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
