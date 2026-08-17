; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bit_reverse_kernel_c272_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = tail call i32 @llvm.smax.i32(i32 %1, i32 0)
  %3 = getelementptr i8, ptr %0, i64 4
  %4 = load i32, ptr %3, align 4
  %5 = tail call i32 @llvm.smax.i32(i32 %4, i32 0)
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 4
  store i32 %5, ptr %10, align 4
  %11 = mul i32 %5, %2
  %12 = load ptr, ptr %6, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  store i32 %11, ptr %14, align 4
  ret void
}

define void @_bit_reverse_kernel_c272_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %21 = getelementptr i8, ptr %20, i64 36
  %22 = load i32, ptr %21, align 4
  %23 = icmp eq i32 %22, 0
  br i1 %23, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  br label %for_loop_body

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %after_for3.us, %for_loop_body.us.preheader
  %.01827.us = phi i32 [ %76, %after_for3.us ], [ %16, %for_loop_body.us.preheader ]
  %24 = load ptr, ptr %3, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 32872
  %26 = load ptr, ptr %25, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 4
  %28 = load i32, ptr %27, align 4
  %29 = sdiv i32 %.01827.us, %28
  %30 = mul i32 %29, %28
  %31 = xor i32 %28, %.01827.us
  %32 = icmp slt i32 %31, 0
  %33 = icmp ne i32 %30, %.01827.us
  %34 = and i1 %32, %33
  %.neg19.us = sext i1 %34 to i32
  %35 = add i32 %29, %.neg19.us
  %36 = mul i32 %35, %28
  %37 = sub i32 %.01827.us, %36
  %38 = load ptr, ptr %0, align 8
  %39 = getelementptr i8, ptr %38, i64 32
  %40 = load i32, ptr %39, align 4
  %41 = icmp sgt i32 %40, 0
  br i1 %41, label %for_loop_body1.us.preheader, label %after_for3.us

for_loop_body1.us.preheader:                      ; preds = %for_loop_body.us
  %xtraiter40 = and i32 %40, 7
  %42 = icmp ult i32 %40, 8
  br i1 %42, label %after_for3.us.loopexit.unr-lcssa, label %for_loop_body1.us.preheader.new

for_loop_body1.us.preheader.new:                  ; preds = %for_loop_body1.us.preheader
  %unroll_iter44 = and i32 %40, 2147483640
  br label %for_loop_body1.us

after_for3.us.loopexit.unr-lcssa.loopexit:        ; preds = %for_loop_body1.us
  br label %after_for3.us.loopexit.unr-lcssa

after_for3.us.loopexit.unr-lcssa:                 ; preds = %after_for3.us.loopexit.unr-lcssa.loopexit, %for_loop_body1.us.preheader
  %.lcssa.ph = phi i32 [ poison, %for_loop_body1.us.preheader ], [ %100, %after_for3.us.loopexit.unr-lcssa.loopexit ]
  %.01624.us.unr = phi i32 [ 0, %for_loop_body1.us.preheader ], [ %100, %after_for3.us.loopexit.unr-lcssa.loopexit ]
  %.01723.us.unr = phi i32 [ %37, %for_loop_body1.us.preheader ], [ %101, %after_for3.us.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod42.not = icmp eq i32 %xtraiter40, 0
  br i1 %lcmp.mod42.not, label %after_for3.us, label %for_loop_body1.us.epil.preheader

for_loop_body1.us.epil.preheader:                 ; preds = %after_for3.us.loopexit.unr-lcssa
  br label %for_loop_body1.us.epil

for_loop_body1.us.epil:                           ; preds = %for_loop_body1.us.epil, %for_loop_body1.us.epil.preheader
  %lsr.iv53 = phi i32 [ %xtraiter40, %for_loop_body1.us.epil.preheader ], [ %lsr.iv.next54, %for_loop_body1.us.epil ]
  %.01624.us.epil = phi i32 [ %45, %for_loop_body1.us.epil ], [ %.01624.us.unr, %for_loop_body1.us.epil.preheader ]
  %.01723.us.epil = phi i32 [ %46, %for_loop_body1.us.epil ], [ %.01723.us.unr, %for_loop_body1.us.epil.preheader ]
  %43 = shl i32 %.01624.us.epil, 1
  %44 = and i32 %.01723.us.epil, 1
  %45 = or disjoint i32 %43, %44
  %46 = ashr i32 %.01723.us.epil, 1
  %lsr.iv.next54 = add nsw i32 %lsr.iv53, -1
  %epil.iter41.cmp.not = icmp eq i32 %lsr.iv.next54, 0
  br i1 %epil.iter41.cmp.not, label %after_for3.us.loopexit, label %for_loop_body1.us.epil, !llvm.loop !10

after_for3.us.loopexit:                           ; preds = %for_loop_body1.us.epil
  br label %after_for3.us

after_for3.us:                                    ; preds = %after_for3.us.loopexit, %after_for3.us.loopexit.unr-lcssa, %for_loop_body.us
  %.016.lcssa.us = phi i32 [ 0, %for_loop_body.us ], [ %.lcssa.ph, %after_for3.us.loopexit.unr-lcssa ], [ %45, %after_for3.us.loopexit ]
  %47 = getelementptr i8, ptr %38, i64 8
  %48 = load ptr, ptr %47, align 8
  %49 = getelementptr i8, ptr %38, i64 4
  %50 = load i32, ptr %49, align 4
  %51 = mul i32 %50, %35
  %52 = add i32 %51, %37
  %53 = shl i32 %52, 1
  %54 = sext i32 %53 to i64
  %55 = getelementptr float, ptr %48, i64 %54
  %56 = load float, ptr %55, align 4
  %57 = getelementptr i8, ptr %55, i64 4
  %58 = load float, ptr %57, align 4
  %59 = getelementptr i8, ptr %38, i64 24
  %60 = load ptr, ptr %59, align 8
  %61 = getelementptr i8, ptr %38, i64 20
  %62 = load i32, ptr %61, align 4
  %63 = mul i32 %62, %35
  %64 = add i32 %63, %.016.lcssa.us
  %65 = shl i32 %64, 1
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, ptr %60, i64 %66
  store float %56, ptr %67, align 4
  %68 = load ptr, ptr %59, align 8
  %69 = load i32, ptr %61, align 4
  %70 = mul i32 %69, %35
  %71 = add i32 %70, %.016.lcssa.us
  %72 = shl i32 %71, 1
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, ptr %68, i64 %73
  %75 = getelementptr i8, ptr %74, i64 4
  store float %58, ptr %75, align 4
  %76 = add nsw i32 %.01827.us, 1
  %exitcond32.not = icmp eq i32 %76, %18
  br i1 %exitcond32.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader.new
  %lsr.iv = phi i32 [ %lsr.iv.next, %for_loop_body1.us ], [ %unroll_iter44, %for_loop_body1.us.preheader.new ]
  %.01624.us = phi i32 [ 0, %for_loop_body1.us.preheader.new ], [ %100, %for_loop_body1.us ]
  %.01723.us = phi i32 [ %37, %for_loop_body1.us.preheader.new ], [ %101, %for_loop_body1.us ]
  %77 = shl i32 %.01624.us, 3
  %78 = shl i32 %.01723.us, 2
  %79 = and i32 %78, 4
  %80 = or disjoint i32 %77, %79
  %81 = and i32 %.01723.us, 2
  %82 = or disjoint i32 %80, %81
  %83 = lshr i32 %.01723.us, 4
  %84 = shl i32 %82, 2
  %.01723.us.mask = and i32 %.01723.us, 4
  %85 = or disjoint i32 %.01723.us.mask, %84
  %86 = lshr i32 %.01723.us, 2
  %87 = and i32 %86, 2
  %88 = or disjoint i32 %85, %87
  %89 = and i32 %83, 1
  %90 = or disjoint i32 %88, %89
  %91 = lshr i32 %.01723.us, 6
  %92 = shl i32 %90, 2
  %93 = and i32 %83, 2
  %94 = or disjoint i32 %92, %93
  %95 = and i32 %91, 1
  %96 = or disjoint i32 %94, %95
  %97 = lshr i32 %.01723.us, 7
  %98 = shl i32 %96, 1
  %99 = and i32 %97, 1
  %100 = or disjoint i32 %98, %99
  %101 = ashr i32 %.01723.us, 8
  %lsr.iv.next = add nsw i32 %lsr.iv, -8
  %niter45.ncmp.7 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter45.ncmp.7, label %after_for3.us.loopexit.unr-lcssa.loopexit, label %for_loop_body1.us

for_loop_body:                                    ; preds = %after_for7, %for_loop_body.preheader
  %.01827 = phi i32 [ %179, %after_for7 ], [ %16, %for_loop_body.preheader ]
  %102 = load ptr, ptr %3, align 8
  %103 = getelementptr inbounds nuw i8, ptr %102, i64 32872
  %104 = load ptr, ptr %103, align 8
  %105 = getelementptr inbounds nuw i8, ptr %104, i64 4
  %106 = load i32, ptr %105, align 4
  %107 = sdiv i32 %.01827, %106
  %108 = mul i32 %107, %106
  %109 = xor i32 %106, %.01827
  %110 = icmp slt i32 %109, 0
  %111 = icmp ne i32 %108, %.01827
  %112 = and i1 %110, %111
  %.neg19 = sext i1 %112 to i32
  %113 = add i32 %107, %.neg19
  %114 = mul i32 %113, %106
  %115 = sub i32 %.01827, %114
  %116 = load ptr, ptr %0, align 8
  %117 = getelementptr i8, ptr %116, i64 32
  %118 = load i32, ptr %117, align 4
  %119 = icmp sgt i32 %118, 0
  br i1 %119, label %for_loop_body5.preheader, label %after_for7

for_loop_body5.preheader:                         ; preds = %for_loop_body
  %xtraiter = and i32 %118, 7
  %120 = icmp ult i32 %118, 8
  br i1 %120, label %after_for7.loopexit.unr-lcssa, label %for_loop_body5.preheader.new

for_loop_body5.preheader.new:                     ; preds = %for_loop_body5.preheader
  %unroll_iter = and i32 %118, 2147483640
  br label %for_loop_body5

after_for.loopexit:                               ; preds = %after_for3.us
  br label %after_for

after_for.loopexit52:                             ; preds = %after_for7
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit52, %after_for.loopexit, %allocs
  ret void

for_loop_body5:                                   ; preds = %for_loop_body5, %for_loop_body5.preheader.new
  %lsr.iv55 = phi i32 [ %lsr.iv.next56, %for_loop_body5 ], [ %unroll_iter, %for_loop_body5.preheader.new ]
  %.01421 = phi i32 [ 0, %for_loop_body5.preheader.new ], [ %144, %for_loop_body5 ]
  %.120 = phi i32 [ %113, %for_loop_body5.preheader.new ], [ %145, %for_loop_body5 ]
  %121 = shl i32 %.01421, 3
  %122 = shl i32 %.120, 2
  %123 = and i32 %122, 4
  %124 = or disjoint i32 %121, %123
  %125 = and i32 %.120, 2
  %126 = or disjoint i32 %124, %125
  %127 = lshr i32 %.120, 4
  %128 = shl i32 %126, 2
  %.120.mask = and i32 %.120, 4
  %129 = or disjoint i32 %.120.mask, %128
  %130 = lshr i32 %.120, 2
  %131 = and i32 %130, 2
  %132 = or disjoint i32 %129, %131
  %133 = and i32 %127, 1
  %134 = or disjoint i32 %132, %133
  %135 = lshr i32 %.120, 6
  %136 = shl i32 %134, 2
  %137 = and i32 %127, 2
  %138 = or disjoint i32 %136, %137
  %139 = and i32 %135, 1
  %140 = or disjoint i32 %138, %139
  %141 = lshr i32 %.120, 7
  %142 = shl i32 %140, 1
  %143 = and i32 %141, 1
  %144 = or disjoint i32 %142, %143
  %145 = ashr i32 %.120, 8
  %lsr.iv.next56 = add nsw i32 %lsr.iv55, -8
  %niter.ncmp.7 = icmp eq i32 %lsr.iv.next56, 0
  br i1 %niter.ncmp.7, label %after_for7.loopexit.unr-lcssa.loopexit, label %for_loop_body5

after_for7.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body5
  br label %after_for7.loopexit.unr-lcssa

after_for7.loopexit.unr-lcssa:                    ; preds = %after_for7.loopexit.unr-lcssa.loopexit, %for_loop_body5.preheader
  %.lcssa38.ph = phi i32 [ poison, %for_loop_body5.preheader ], [ %144, %after_for7.loopexit.unr-lcssa.loopexit ]
  %.01421.unr = phi i32 [ 0, %for_loop_body5.preheader ], [ %144, %after_for7.loopexit.unr-lcssa.loopexit ]
  %.120.unr = phi i32 [ %113, %for_loop_body5.preheader ], [ %145, %after_for7.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_for7, label %for_loop_body5.epil.preheader

for_loop_body5.epil.preheader:                    ; preds = %after_for7.loopexit.unr-lcssa
  br label %for_loop_body5.epil

for_loop_body5.epil:                              ; preds = %for_loop_body5.epil, %for_loop_body5.epil.preheader
  %lsr.iv57 = phi i32 [ %xtraiter, %for_loop_body5.epil.preheader ], [ %lsr.iv.next58, %for_loop_body5.epil ]
  %.01421.epil = phi i32 [ %148, %for_loop_body5.epil ], [ %.01421.unr, %for_loop_body5.epil.preheader ]
  %.120.epil = phi i32 [ %149, %for_loop_body5.epil ], [ %.120.unr, %for_loop_body5.epil.preheader ]
  %146 = shl i32 %.01421.epil, 1
  %147 = and i32 %.120.epil, 1
  %148 = or disjoint i32 %146, %147
  %149 = ashr i32 %.120.epil, 1
  %lsr.iv.next58 = add nsw i32 %lsr.iv57, -1
  %epil.iter.cmp.not = icmp eq i32 %lsr.iv.next58, 0
  br i1 %epil.iter.cmp.not, label %after_for7.loopexit, label %for_loop_body5.epil, !llvm.loop !12

after_for7.loopexit:                              ; preds = %for_loop_body5.epil
  br label %after_for7

after_for7:                                       ; preds = %after_for7.loopexit, %after_for7.loopexit.unr-lcssa, %for_loop_body
  %.014.lcssa = phi i32 [ 0, %for_loop_body ], [ %.lcssa38.ph, %after_for7.loopexit.unr-lcssa ], [ %148, %after_for7.loopexit ]
  %150 = getelementptr i8, ptr %116, i64 8
  %151 = load ptr, ptr %150, align 8
  %152 = getelementptr i8, ptr %116, i64 4
  %153 = load i32, ptr %152, align 4
  %154 = mul i32 %153, %113
  %155 = add i32 %154, %115
  %156 = shl i32 %155, 1
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, ptr %151, i64 %157
  %159 = load float, ptr %158, align 4
  %160 = getelementptr i8, ptr %158, i64 4
  %161 = load float, ptr %160, align 4
  %162 = getelementptr i8, ptr %116, i64 24
  %163 = load ptr, ptr %162, align 8
  %164 = getelementptr i8, ptr %116, i64 20
  %165 = load i32, ptr %164, align 4
  %166 = mul i32 %165, %.014.lcssa
  %167 = add i32 %166, %115
  %168 = shl i32 %167, 1
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %163, i64 %169
  store float %159, ptr %170, align 4
  %171 = load ptr, ptr %162, align 8
  %172 = load i32, ptr %164, align 4
  %173 = mul i32 %172, %.014.lcssa
  %174 = add i32 %173, %115
  %175 = shl i32 %174, 1
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, ptr %171, i64 %176
  %178 = getelementptr i8, ptr %177, i64 4
  store float %161, ptr %178, align 4
  %179 = add nsw i32 %.01827, 1
  %exitcond30.not = icmp eq i32 %179, %18
  br i1 %exitcond30.not, label %after_for.loopexit52, label %for_loop_body
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !13

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !15

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
!11 = !{!"llvm.loop.unroll.disable"}
!12 = distinct !{!12, !11}
!13 = distinct !{!13, !14}
!14 = !{!"llvm.loop.mustprogress"}
!15 = distinct !{!15, !14}
