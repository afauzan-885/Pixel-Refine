; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.0 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_block_match_and_extract_kernel_c428_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 104
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  store i32 %2, ptr %6, align 4
  ret void
}

define void @_block_match_and_extract_kernel_c428_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %3 = alloca [32 x float], align 4
  %4 = alloca [32 x i32], align 4
  %5 = alloca [32 x i32], align 4
  %6 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = load i32, ptr %9, align 4
  %11 = add i32 %10, 7
  %12 = sdiv i32 %11, 8
  %13 = icmp slt i32 %11, 0
  %14 = shl nsw i32 %12, 3
  %15 = icmp ne i32 %14, %11
  %16 = and i1 %13, %15
  %.neg = sext i1 %16 to i32
  %17 = add nsw i32 %12, %.neg
  %18 = tail call range(i32 -268435457, 268435456) i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %17, i32 512)
  %19 = mul i32 %18, %2
  %20 = add i32 %19, %18
  %21 = tail call i32 @llvm.smin.i32(i32 %10, i32 %20)
  %22 = load ptr, ptr %0, align 8
  %23 = getelementptr i8, ptr %22, i64 116
  %24 = load i32, ptr %23, align 4
  %25 = getelementptr i8, ptr %22, i64 112
  %26 = load i32, ptr %25, align 4
  %.fr130 = freeze i32 %26
  %27 = getelementptr i8, ptr %22, i64 108
  %28 = load i32, ptr %27, align 4
  %neg = sub i32 0, %24
  %29 = icmp slt i32 %19, %21
  br i1 %29, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %30 = add i32 %24, 1
  %31 = getelementptr i8, ptr %22, i64 96
  %32 = getelementptr i8, ptr %22, i64 92
  %33 = getelementptr inbounds nuw i8, ptr %3, i64 124
  %34 = getelementptr inbounds nuw i8, ptr %3, i64 120
  %35 = getelementptr inbounds nuw i8, ptr %3, i64 116
  %36 = getelementptr inbounds nuw i8, ptr %3, i64 112
  %37 = getelementptr inbounds nuw i8, ptr %3, i64 108
  %38 = getelementptr inbounds nuw i8, ptr %3, i64 104
  %39 = getelementptr inbounds nuw i8, ptr %3, i64 100
  %40 = getelementptr inbounds nuw i8, ptr %3, i64 96
  %41 = getelementptr inbounds nuw i8, ptr %3, i64 92
  %42 = getelementptr inbounds nuw i8, ptr %3, i64 88
  %43 = getelementptr inbounds nuw i8, ptr %3, i64 84
  %44 = getelementptr inbounds nuw i8, ptr %3, i64 80
  %45 = getelementptr inbounds nuw i8, ptr %3, i64 76
  %46 = getelementptr inbounds nuw i8, ptr %3, i64 72
  %47 = getelementptr inbounds nuw i8, ptr %3, i64 68
  %48 = getelementptr inbounds nuw i8, ptr %3, i64 64
  %49 = getelementptr inbounds nuw i8, ptr %3, i64 60
  %50 = getelementptr inbounds nuw i8, ptr %3, i64 56
  %51 = getelementptr inbounds nuw i8, ptr %3, i64 52
  %52 = getelementptr inbounds nuw i8, ptr %3, i64 48
  %53 = getelementptr inbounds nuw i8, ptr %3, i64 44
  %54 = getelementptr inbounds nuw i8, ptr %3, i64 40
  %55 = getelementptr inbounds nuw i8, ptr %3, i64 36
  %56 = getelementptr inbounds nuw i8, ptr %3, i64 32
  %57 = getelementptr inbounds nuw i8, ptr %3, i64 28
  %58 = getelementptr inbounds nuw i8, ptr %3, i64 24
  %59 = getelementptr inbounds nuw i8, ptr %3, i64 20
  %60 = getelementptr inbounds nuw i8, ptr %3, i64 16
  %61 = getelementptr inbounds nuw i8, ptr %3, i64 12
  %62 = getelementptr inbounds nuw i8, ptr %3, i64 8
  %63 = getelementptr inbounds nuw i8, ptr %3, i64 4
  %64 = icmp sgt i32 %30, %neg
  %65 = sub i32 1, %.fr130
  %66 = icmp sgt i32 %.fr130, 0
  %67 = getelementptr i8, ptr %22, i64 8
  %68 = getelementptr i8, ptr %22, i64 4
  %69 = icmp sgt i32 %28, 1
  %70 = icmp sgt i32 %28, 0
  %wide.trip.count = zext i32 %28 to i64
  %wide.trip.count139 = zext i32 %.fr130 to i64
  %71 = add nsw i64 %wide.trip.count139, -1
  %72 = add nsw i64 %wide.trip.count, -1
  %73 = add nsw i64 %wide.trip.count, -2
  %74 = add i32 %.fr130, -1
  %xtraiter = and i64 %72, 7
  %75 = icmp ult i64 %73, 7
  %unroll_iter = and i64 %72, -8
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %min.iters.check = icmp ult i32 %.fr130, 4
  %76 = trunc i64 %71 to i32
  %77 = icmp ugt i64 %71, 4294967295
  %min.iters.check165 = icmp ult i32 %.fr130, 32
  %n.vec = and i64 %wide.trip.count139, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count139
  %n.vec.remaining = and i64 %wide.trip.count139, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec179 = and i64 %wide.trip.count139, 2147483644
  %cmp.n185 = icmp eq i64 %n.vec179, %wide.trip.count139
  %xtraiter197 = and i64 %wide.trip.count139, 3
  %lcmp.mod198.not = icmp eq i64 %xtraiter197, 0
  %xtraiter206 = and i32 %.fr130, 1
  %78 = icmp eq i32 %74, 0
  %unroll_iter209 = and i32 %.fr130, 2147483646
  %lcmp.mod208.not = icmp eq i32 %xtraiter206, 0
  %79 = lshr i64 %wide.trip.count139, 2
  %80 = trunc i64 %79 to i29
  %81 = zext i29 %80 to i64
  %82 = mul nsw i64 %81, -4
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for42, %for_loop_body.lr.ph
  %.063129 = phi i32 [ %19, %for_loop_body.lr.ph ], [ %320, %after_for42 ]
  %83 = load ptr, ptr %31, align 8
  %84 = load i32, ptr %32, align 4
  %85 = mul i32 %84, %.063129
  %86 = sext i32 %85 to i64
  %87 = getelementptr i32, ptr %83, i64 %86
  %88 = load i32, ptr %87, align 4
  %89 = add i32 %85, 1
  %90 = sext i32 %89 to i64
  %91 = getelementptr i32, ptr %83, i64 %90
  %92 = load i32, ptr %91, align 4
  store float 0x46293E5940000000, ptr %3, align 4
  store float 0x46293E5940000000, ptr %63, align 4
  store float 0x46293E5940000000, ptr %62, align 4
  store float 0x46293E5940000000, ptr %61, align 4
  store float 0x46293E5940000000, ptr %60, align 4
  store float 0x46293E5940000000, ptr %59, align 4
  store float 0x46293E5940000000, ptr %58, align 4
  store float 0x46293E5940000000, ptr %57, align 4
  store float 0x46293E5940000000, ptr %56, align 4
  store float 0x46293E5940000000, ptr %55, align 4
  store float 0x46293E5940000000, ptr %54, align 4
  store float 0x46293E5940000000, ptr %53, align 4
  store float 0x46293E5940000000, ptr %52, align 4
  store float 0x46293E5940000000, ptr %51, align 4
  store float 0x46293E5940000000, ptr %50, align 4
  store float 0x46293E5940000000, ptr %49, align 4
  store float 0x46293E5940000000, ptr %48, align 4
  store float 0x46293E5940000000, ptr %47, align 4
  store float 0x46293E5940000000, ptr %46, align 4
  store float 0x46293E5940000000, ptr %45, align 4
  store float 0x46293E5940000000, ptr %44, align 4
  store float 0x46293E5940000000, ptr %43, align 4
  store float 0x46293E5940000000, ptr %42, align 4
  store float 0x46293E5940000000, ptr %41, align 4
  store float 0x46293E5940000000, ptr %40, align 4
  store float 0x46293E5940000000, ptr %39, align 4
  store float 0x46293E5940000000, ptr %38, align 4
  store float 0x46293E5940000000, ptr %37, align 4
  store float 0x46293E5940000000, ptr %36, align 4
  store float 0x46293E5940000000, ptr %35, align 4
  store float 0x46293E5940000000, ptr %34, align 4
  store float 0x46293E5940000000, ptr %33, align 4
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 4 dereferenceable(128) %4, i8 0, i64 128, i1 false)
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 4 dereferenceable(128) %5, i8 0, i64 128, i1 false)
  br i1 %64, label %for_loop_body1.lr.ph, label %for_loop_test43.preheader

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  br i1 %66, label %for_loop_body1.us.us.preheader, label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %for_loop_body1.lr.ph
  br label %for_loop_body1.us

for_loop_body1.us.us.preheader:                   ; preds = %for_loop_body1.lr.ph
  %93 = sub i32 %92, %24
  %94 = sub i32 %88, %24
  %invariant.op233 = add i32 %92, %76
  %95 = add i32 %neg, %92
  %96 = add i32 %neg, %88
  br label %for_loop_body1.us.us

for_loop_body1.us.us:                             ; preds = %for_loop_inc2.us.us, %for_loop_body1.us.us.preheader
  %lsr.iv262 = phi i32 [ %96, %for_loop_body1.us.us.preheader ], [ %lsr.iv.next263, %for_loop_inc2.us.us ]
  %indvar163 = phi i32 [ 0, %for_loop_body1.us.us.preheader ], [ %indvar.next164, %for_loop_inc2.us.us ]
  %.06093.us.us = phi i32 [ %neg, %for_loop_body1.us.us.preheader ], [ %104, %for_loop_inc2.us.us ]
  %.16292.us.us = phi i32 [ 0, %for_loop_body1.us.us.preheader ], [ %.061.us.us, %for_loop_inc2.us.us ]
  %97 = add i32 %94, %indvar163
  %98 = add i32 %.06093.us.us, %88
  %99 = icmp slt i32 %98, 0
  br i1 %99, label %for_loop_inc2.us.us, label %false_block.us.us

false_block.us.us:                                ; preds = %for_loop_body1.us.us
  %100 = load ptr, ptr %0, align 8
  %101 = getelementptr i8, ptr %100, i64 120
  %102 = load i32, ptr %101, align 4
  %103 = add i32 %65, %102
  %.not.us.us = icmp slt i32 %98, %103
  br i1 %.not.us.us, label %for_loop_test11.preheader.us.us, label %for_loop_inc2.us.us

for_loop_inc2.us.us.loopexit:                     ; preds = %for_loop_inc9.us.us.us
  br label %for_loop_inc2.us.us

for_loop_inc2.us.us:                              ; preds = %for_loop_inc2.us.us.loopexit, %false_block.us.us, %for_loop_body1.us.us
  %.061.us.us = phi i32 [ %.16292.us.us, %false_block.us.us ], [ %.16292.us.us, %for_loop_body1.us.us ], [ %.2.us.us.us, %for_loop_inc2.us.us.loopexit ]
  %104 = add nsw i32 %.06093.us.us, 1
  %indvar.next164 = add i32 %indvar163, 1
  %lsr.iv.next263 = add i32 %lsr.iv262, 1
  %exitcond148.not = icmp eq i32 %.06093.us.us, %24
  br i1 %exitcond148.not, label %for_loop_test43.preheader.loopexit, label %for_loop_body1.us.us

for_loop_test11.preheader.us.us:                  ; preds = %false_block.us.us
  %105 = getelementptr i8, ptr %100, i64 124
  br label %for_loop_body8.us.us.us

for_loop_body8.us.us.us:                          ; preds = %for_loop_inc9.us.us.us, %for_loop_test11.preheader.us.us
  %lsr.iv260 = phi i32 [ %lsr.iv.next261, %for_loop_inc9.us.us.us ], [ %95, %for_loop_test11.preheader.us.us ]
  %indvar = phi i32 [ %indvar.next, %for_loop_inc9.us.us.us ], [ 0, %for_loop_test11.preheader.us.us ]
  %.05889.us.us.us = phi i32 [ %149, %for_loop_inc9.us.us.us ], [ %neg, %for_loop_test11.preheader.us.us ]
  %.388.us.us.us = phi i32 [ %.2.us.us.us, %for_loop_inc9.us.us.us ], [ %.16292.us.us, %for_loop_test11.preheader.us.us ]
  %106 = add i32 %93, %indvar
  %107 = add i32 %.05889.us.us.us, %92
  %108 = icmp slt i32 %107, 0
  br i1 %108, label %for_loop_inc9.us.us.us, label %false_block13.us.us.us

false_block13.us.us.us:                           ; preds = %for_loop_body8.us.us.us
  %109 = load i32, ptr %105, align 4
  %110 = add i32 %65, %109
  %.not74.us.us.us = icmp slt i32 %107, %110
  br i1 %.not74.us.us.us, label %for_loop_test22.preheader.us.us.us, label %for_loop_inc9.us.us.us

false_block28.us.us.us:                           ; preds = %for_loop_test22.after_for21_crit_edge.split.us.us.us.us
  %111 = load float, ptr %3, align 4
  br i1 %69, label %for_loop_body30.us.us.us.preheader, label %after_for32.us.us.us

for_loop_body30.us.us.us.preheader:               ; preds = %false_block28.us.us.us
  br i1 %75, label %after_for32.us.us.us.loopexit.unr-lcssa, label %for_loop_body30.us.us.us.preheader234

for_loop_body30.us.us.us.preheader234:            ; preds = %for_loop_body30.us.us.us.preheader
  br label %for_loop_body30.us.us.us

after_for32.us.us.us.loopexit.unr-lcssa.loopexit: ; preds = %for_loop_body30.us.us.us
  br label %after_for32.us.us.us.loopexit.unr-lcssa

after_for32.us.us.us.loopexit.unr-lcssa:          ; preds = %after_for32.us.us.us.loopexit.unr-lcssa.loopexit, %for_loop_body30.us.us.us.preheader
  %.152.us.us.us.lcssa.ph = phi i32 [ poison, %for_loop_body30.us.us.us.preheader ], [ %.152.us.us.us.7, %after_for32.us.us.us.loopexit.unr-lcssa.loopexit ]
  %.1.us.us.us.lcssa.ph = phi float [ poison, %for_loop_body30.us.us.us.preheader ], [ %.1.us.us.us.7, %after_for32.us.us.us.loopexit.unr-lcssa.loopexit ]
  %indvars.iv142.unr = phi i64 [ 1, %for_loop_body30.us.us.us.preheader ], [ %indvars.iv.next143.7, %after_for32.us.us.us.loopexit.unr-lcssa.loopexit ]
  %.05085.us.us.us.unr = phi float [ %111, %for_loop_body30.us.us.us.preheader ], [ %.1.us.us.us.7, %after_for32.us.us.us.loopexit.unr-lcssa.loopexit ]
  %.05184.us.us.us.unr = phi i32 [ 0, %for_loop_body30.us.us.us.preheader ], [ %.152.us.us.us.7, %after_for32.us.us.us.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for32.us.us.us.loopexit, label %for_loop_body30.us.us.us.epil.preheader

for_loop_body30.us.us.us.epil.preheader:          ; preds = %after_for32.us.us.us.loopexit.unr-lcssa
  br label %for_loop_body30.us.us.us.epil

for_loop_body30.us.us.us.epil:                    ; preds = %for_loop_body30.us.us.us.epil, %for_loop_body30.us.us.us.epil.preheader
  %lsr.iv313 = phi i64 [ %xtraiter, %for_loop_body30.us.us.us.epil.preheader ], [ %lsr.iv.next314, %for_loop_body30.us.us.us.epil ]
  %indvars.iv142.epil = phi i64 [ %indvars.iv.next143.epil, %for_loop_body30.us.us.us.epil ], [ %indvars.iv142.unr, %for_loop_body30.us.us.us.epil.preheader ]
  %.05085.us.us.us.epil = phi float [ %.1.us.us.us.epil, %for_loop_body30.us.us.us.epil ], [ %.05085.us.us.us.unr, %for_loop_body30.us.us.us.epil.preheader ]
  %.05184.us.us.us.epil = phi i32 [ %.152.us.us.us.epil, %for_loop_body30.us.us.us.epil ], [ %.05184.us.us.us.unr, %for_loop_body30.us.us.us.epil.preheader ]
  %112 = shl i64 %indvars.iv142.epil, 2
  %scevgep312 = getelementptr i8, ptr %3, i64 %112
  %113 = load float, ptr %scevgep312, align 4
  %114 = fcmp reassoc ninf nsz ogt float %113, %.05085.us.us.us.epil
  %tmp311 = trunc i64 %indvars.iv142.epil to i32
  %.152.us.us.us.epil = select i1 %114, i32 %tmp311, i32 %.05184.us.us.us.epil
  %.1.us.us.us.epil = select i1 %114, float %113, float %.05085.us.us.us.epil
  %indvars.iv.next143.epil = add nuw nsw i64 %indvars.iv142.epil, 1
  %lsr.iv.next314 = add nsw i64 %lsr.iv313, -1
  %epil.iter200.cmp.not = icmp eq i64 %lsr.iv.next314, 0
  br i1 %epil.iter200.cmp.not, label %after_for32.us.us.us.loopexit.loopexit, label %for_loop_body30.us.us.us.epil, !llvm.loop !10

after_for32.us.us.us.loopexit.loopexit:           ; preds = %for_loop_body30.us.us.us.epil
  br label %after_for32.us.us.us.loopexit

after_for32.us.us.us.loopexit:                    ; preds = %after_for32.us.us.us.loopexit.loopexit, %after_for32.us.us.us.loopexit.unr-lcssa
  %.152.us.us.us.lcssa = phi i32 [ %.152.us.us.us.lcssa.ph, %after_for32.us.us.us.loopexit.unr-lcssa ], [ %.152.us.us.us.epil, %after_for32.us.us.us.loopexit.loopexit ]
  %.1.us.us.us.lcssa = phi float [ %.1.us.us.us.lcssa.ph, %after_for32.us.us.us.loopexit.unr-lcssa ], [ %.1.us.us.us.epil, %after_for32.us.us.us.loopexit.loopexit ]
  %115 = zext nneg i32 %.152.us.us.us.lcssa to i64
  br label %after_for32.us.us.us

after_for32.us.us.us:                             ; preds = %after_for32.us.us.us.loopexit, %false_block28.us.us.us
  %.051.lcssa.us.us.us = phi i64 [ 0, %false_block28.us.us.us ], [ %115, %after_for32.us.us.us.loopexit ]
  %.050.lcssa.us.us.us = phi float [ %111, %false_block28.us.us.us ], [ %.1.us.us.us.lcssa, %after_for32.us.us.us.loopexit ]
  %116 = fcmp reassoc ninf nsz olt float %.lcssa, %.050.lcssa.us.us.us
  br i1 %116, label %true_block37.us.us.us, label %for_loop_inc9.us.us.us

true_block37.us.us.us:                            ; preds = %after_for32.us.us.us
  %117 = getelementptr [32 x float], ptr %3, i64 0, i64 %.051.lcssa.us.us.us
  store float %.lcssa, ptr %117, align 4
  %118 = getelementptr [32 x i32], ptr %4, i64 0, i64 %.051.lcssa.us.us.us
  store i32 %98, ptr %118, align 4
  %119 = getelementptr [32 x i32], ptr %5, i64 0, i64 %.051.lcssa.us.us.us
  store i32 %107, ptr %119, align 4
  br label %for_loop_inc9.us.us.us

for_loop_body30.us.us.us:                         ; preds = %for_loop_body30.us.us.us, %for_loop_body30.us.us.us.preheader234
  %indvars.iv142 = phi i64 [ %indvars.iv.next143.7, %for_loop_body30.us.us.us ], [ 1, %for_loop_body30.us.us.us.preheader234 ]
  %.05085.us.us.us = phi float [ %.1.us.us.us.7, %for_loop_body30.us.us.us ], [ %111, %for_loop_body30.us.us.us.preheader234 ]
  %.05184.us.us.us = phi i32 [ %.152.us.us.us.7, %for_loop_body30.us.us.us ], [ 0, %for_loop_body30.us.us.us.preheader234 ]
  %niter205 = phi i64 [ %niter205.next.7, %for_loop_body30.us.us.us ], [ 0, %for_loop_body30.us.us.us.preheader234 ]
  %lsr310 = trunc i64 %indvars.iv142 to i32
  %120 = shl i64 %indvars.iv142, 2
  %scevgep305 = getelementptr i8, ptr %3, i64 %120
  %121 = load float, ptr %scevgep305, align 4
  %122 = fcmp reassoc ninf nsz ogt float %121, %.05085.us.us.us
  %.152.us.us.us = select i1 %122, i32 %lsr310, i32 %.05184.us.us.us
  %.1.us.us.us = select i1 %122, float %121, float %.05085.us.us.us
  %indvars.iv.next143 = add nuw nsw i64 %indvars.iv142, 1
  %scevgep307 = getelementptr i8, ptr %scevgep305, i64 4
  %123 = load float, ptr %scevgep307, align 4
  %124 = fcmp reassoc ninf nsz ogt float %123, %.1.us.us.us
  %125 = trunc nuw nsw i64 %indvars.iv.next143 to i32
  %.152.us.us.us.1 = select i1 %124, i32 %125, i32 %.152.us.us.us
  %.1.us.us.us.1 = select i1 %124, float %123, float %.1.us.us.us
  %indvars.iv.next143.1 = add nuw nsw i64 %indvars.iv142, 2
  %scevgep304 = getelementptr i8, ptr %scevgep305, i64 8
  %126 = load float, ptr %scevgep304, align 4
  %127 = fcmp reassoc ninf nsz ogt float %126, %.1.us.us.us.1
  %128 = trunc nuw nsw i64 %indvars.iv.next143.1 to i32
  %.152.us.us.us.2 = select i1 %127, i32 %128, i32 %.152.us.us.us.1
  %.1.us.us.us.2 = select i1 %127, float %126, float %.1.us.us.us.1
  %indvars.iv.next143.2 = add nuw nsw i64 %indvars.iv142, 3
  %scevgep302 = getelementptr i8, ptr %scevgep305, i64 12
  %129 = load float, ptr %scevgep302, align 4
  %130 = fcmp reassoc ninf nsz ogt float %129, %.1.us.us.us.2
  %131 = trunc nuw nsw i64 %indvars.iv.next143.2 to i32
  %.152.us.us.us.3 = select i1 %130, i32 %131, i32 %.152.us.us.us.2
  %.1.us.us.us.3 = select i1 %130, float %129, float %.1.us.us.us.2
  %indvars.iv.next143.3 = add nuw nsw i64 %indvars.iv142, 4
  %scevgep300 = getelementptr i8, ptr %scevgep305, i64 16
  %132 = load float, ptr %scevgep300, align 4
  %133 = fcmp reassoc ninf nsz ogt float %132, %.1.us.us.us.3
  %134 = trunc nuw nsw i64 %indvars.iv.next143.3 to i32
  %.152.us.us.us.4 = select i1 %133, i32 %134, i32 %.152.us.us.us.3
  %.1.us.us.us.4 = select i1 %133, float %132, float %.1.us.us.us.3
  %indvars.iv.next143.4 = add nuw nsw i64 %indvars.iv142, 5
  %scevgep298 = getelementptr i8, ptr %scevgep305, i64 20
  %135 = load float, ptr %scevgep298, align 4
  %136 = fcmp reassoc ninf nsz ogt float %135, %.1.us.us.us.4
  %137 = trunc nuw nsw i64 %indvars.iv.next143.4 to i32
  %.152.us.us.us.5 = select i1 %136, i32 %137, i32 %.152.us.us.us.4
  %.1.us.us.us.5 = select i1 %136, float %135, float %.1.us.us.us.4
  %indvars.iv.next143.5 = add nuw nsw i64 %indvars.iv142, 6
  %scevgep296 = getelementptr i8, ptr %scevgep305, i64 24
  %138 = load float, ptr %scevgep296, align 4
  %139 = fcmp reassoc ninf nsz ogt float %138, %.1.us.us.us.5
  %140 = trunc nuw nsw i64 %indvars.iv.next143.5 to i32
  %.152.us.us.us.6 = select i1 %139, i32 %140, i32 %.152.us.us.us.5
  %.1.us.us.us.6 = select i1 %139, float %138, float %.1.us.us.us.5
  %indvars.iv.next143.6 = add nuw nsw i64 %indvars.iv142, 7
  %scevgep294 = getelementptr i8, ptr %scevgep305, i64 28
  %141 = load float, ptr %scevgep294, align 4
  %142 = fcmp reassoc ninf nsz ogt float %141, %.1.us.us.us.6
  %143 = trunc nuw nsw i64 %indvars.iv.next143.6 to i32
  %.152.us.us.us.7 = select i1 %142, i32 %143, i32 %.152.us.us.us.6
  %.1.us.us.us.7 = select i1 %142, float %141, float %.1.us.us.us.6
  %indvars.iv.next143.7 = add nuw i64 %indvars.iv142, 8
  %niter205.next.7 = add i64 %niter205, 8
  %niter205.ncmp.7 = icmp eq i64 %niter205.next.7, %unroll_iter
  br i1 %niter205.ncmp.7, label %after_for32.us.us.us.loopexit.unr-lcssa.loopexit, label %for_loop_body30.us.us.us

true_block27.us.us.us:                            ; preds = %for_loop_test22.after_for21_crit_edge.split.us.us.us.us
  %144 = sext i32 %.388.us.us.us to i64
  %145 = getelementptr [32 x float], ptr %3, i64 0, i64 %144
  store float %.lcssa, ptr %145, align 4
  %146 = getelementptr [32 x i32], ptr %4, i64 0, i64 %144
  store i32 %98, ptr %146, align 4
  %147 = getelementptr [32 x i32], ptr %5, i64 0, i64 %144
  store i32 %107, ptr %147, align 4
  %148 = add nsw i32 %.388.us.us.us, 1
  br label %for_loop_inc9.us.us.us

for_loop_inc9.us.us.us:                           ; preds = %true_block27.us.us.us, %true_block37.us.us.us, %after_for32.us.us.us, %false_block13.us.us.us, %for_loop_body8.us.us.us
  %.2.us.us.us = phi i32 [ %.388.us.us.us, %false_block13.us.us.us ], [ %148, %true_block27.us.us.us ], [ %.388.us.us.us, %true_block37.us.us.us ], [ %.388.us.us.us, %after_for32.us.us.us ], [ %.388.us.us.us, %for_loop_body8.us.us.us ]
  %149 = add nsw i32 %.05889.us.us.us, 1
  %indvar.next = add i32 %indvar, 1
  %lsr.iv.next261 = add i32 %lsr.iv260, 1
  %exitcond147.not = icmp eq i32 %.05889.us.us.us, %24
  br i1 %exitcond147.not, label %for_loop_inc2.us.us.loopexit, label %for_loop_body8.us.us.us

for_loop_test22.preheader.us.us.us:               ; preds = %false_block13.us.us.us
  %150 = load ptr, ptr %67, align 8
  %151 = load i32, ptr %68, align 4
  %152 = mul i32 %88, %151
  %153 = add i32 %92, %152
  %154 = mul i32 %97, %151
  %155 = add i32 %106, %154
  %invariant.op230.reass = add i32 %152, %invariant.op233
  %invariant.op231 = add i32 %155, %76
  %156 = mul i32 %lsr.iv262, %151
  %157 = add i32 %lsr.iv260, %156
  %158 = zext i32 %157 to i64
  %159 = zext i32 %151 to i64
  %160 = zext i32 %153 to i64
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test26.after_for25_crit_edge.us.us.us.us, %for_loop_test22.preheader.us.us.us
  %lsr.iv277 = phi i64 [ %lsr.iv.next278, %for_loop_test26.after_for25_crit_edge.us.us.us.us ], [ %160, %for_loop_test22.preheader.us.us.us ]
  %lsr.iv274 = phi i64 [ %lsr.iv.next275, %for_loop_test26.after_for25_crit_edge.us.us.us.us ], [ %158, %for_loop_test22.preheader.us.us.us ]
  %.05482.us.us.us.us = phi i32 [ 0, %for_loop_test22.preheader.us.us.us ], [ %264, %for_loop_test26.after_for25_crit_edge.us.us.us.us ]
  %.05581.us.us.us.us = phi float [ 0.000000e+00, %for_loop_test22.preheader.us.us.us ], [ %.lcssa, %for_loop_test26.after_for25_crit_edge.us.us.us.us ]
  %lsr292 = trunc i64 %lsr.iv277 to i32
  %lsr290 = trunc i64 %lsr.iv274 to i32
  br i1 %min.iters.check, label %for_loop_body23.us.us.us.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %161 = mul i32 %151, %.05482.us.us.us.us
  %162 = add i32 %155, %161
  %163 = add i32 %153, %161
  %.reass = add i32 %161, %invariant.op230.reass
  %164 = icmp slt i32 %.reass, %163
  %.reass232 = add i32 %161, %invariant.op231
  %165 = icmp slt i32 %.reass232, %162
  %166 = or i1 %165, %77
  %167 = or i1 %164, %166
  br i1 %167, label %for_loop_body23.us.us.us.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check165, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %168 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05581.us.us.us.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv266 = phi i32 [ %lsr.iv.next267, %vector.body ], [ %lsr290, %vector.ph ]
  %lsr.iv258 = phi i32 [ %lsr.iv.next259, %vector.body ], [ %lsr292, %vector.ph ]
  %lsr.iv254 = phi i64 [ %lsr.iv.next255, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %168, %vector.ph ], [ %187, %vector.body ]
  %vec.phi166 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %188, %vector.body ]
  %vec.phi167 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %189, %vector.body ]
  %vec.phi168 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %190, %vector.body ]
  %169 = sext i32 %lsr.iv258 to i64
  %170 = getelementptr float, ptr %150, i64 %169
  %171 = getelementptr i8, ptr %170, i64 32
  %172 = getelementptr i8, ptr %170, i64 64
  %173 = getelementptr i8, ptr %170, i64 96
  %wide.load = load <8 x float>, ptr %170, align 4
  %wide.load169 = load <8 x float>, ptr %171, align 4
  %wide.load170 = load <8 x float>, ptr %172, align 4
  %wide.load171 = load <8 x float>, ptr %173, align 4
  %174 = sext i32 %lsr.iv266 to i64
  %175 = getelementptr float, ptr %150, i64 %174
  %176 = getelementptr i8, ptr %175, i64 32
  %177 = getelementptr i8, ptr %175, i64 64
  %178 = getelementptr i8, ptr %175, i64 96
  %wide.load172 = load <8 x float>, ptr %175, align 4
  %wide.load173 = load <8 x float>, ptr %176, align 4
  %wide.load174 = load <8 x float>, ptr %177, align 4
  %wide.load175 = load <8 x float>, ptr %178, align 4
  %179 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load172
  %180 = fsub reassoc ninf nsz <8 x float> %wide.load169, %wide.load173
  %181 = fsub reassoc ninf nsz <8 x float> %wide.load170, %wide.load174
  %182 = fsub reassoc ninf nsz <8 x float> %wide.load171, %wide.load175
  %183 = fmul reassoc ninf nsz <8 x float> %179, %179
  %184 = fmul reassoc ninf nsz <8 x float> %180, %180
  %185 = fmul reassoc ninf nsz <8 x float> %181, %181
  %186 = fmul reassoc ninf nsz <8 x float> %182, %182
  %187 = fadd reassoc ninf nsz <8 x float> %183, %vec.phi
  %188 = fadd reassoc ninf nsz <8 x float> %184, %vec.phi166
  %189 = fadd reassoc ninf nsz <8 x float> %185, %vec.phi167
  %190 = fadd reassoc ninf nsz <8 x float> %186, %vec.phi168
  %lsr.iv.next255 = add nsw i64 %lsr.iv254, -32
  %lsr.iv.next259 = add i32 %lsr.iv258, 32
  %lsr.iv.next267 = add i32 %lsr.iv266, 32
  %191 = icmp eq i64 %lsr.iv.next255, 0
  br i1 %191, label %middle.block, label %vector.body, !llvm.loop !12

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %188, %187
  %bin.rdx176 = fadd reassoc ninf nsz <8 x float> %189, %bin.rdx
  %bin.rdx177 = fadd reassoc ninf nsz <8 x float> %190, %bin.rdx176
  %192 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx177)
  br i1 %cmp.n, label %for_loop_test26.after_for25_crit_edge.us.us.us.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body23.us.us.us.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %192, %vec.epilog.iter.check ], [ %.05581.us.us.us.us, %vector.main.loop.iter.check ]
  %193 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %194 = add i64 %82, %vec.epilog.resume.val
  %195 = trunc i64 %vec.epilog.resume.val to i32
  %196 = add i32 %lsr292, %195
  %197 = add i32 %lsr290, %195
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv272 = phi i32 [ %lsr.iv.next273, %vec.epilog.vector.body ], [ %197, %vec.epilog.ph ]
  %lsr.iv270 = phi i32 [ %lsr.iv.next271, %vec.epilog.vector.body ], [ %196, %vec.epilog.ph ]
  %lsr.iv268 = phi i64 [ %lsr.iv.next269, %vec.epilog.vector.body ], [ %194, %vec.epilog.ph ]
  %vec.phi181 = phi <4 x float> [ %193, %vec.epilog.ph ], [ %204, %vec.epilog.vector.body ]
  %198 = sext i32 %lsr.iv270 to i64
  %199 = getelementptr float, ptr %150, i64 %198
  %wide.load182 = load <4 x float>, ptr %199, align 4
  %200 = sext i32 %lsr.iv272 to i64
  %201 = getelementptr float, ptr %150, i64 %200
  %wide.load183 = load <4 x float>, ptr %201, align 4
  %202 = fsub reassoc ninf nsz <4 x float> %wide.load182, %wide.load183
  %203 = fmul reassoc ninf nsz <4 x float> %202, %202
  %204 = fadd reassoc ninf nsz <4 x float> %203, %vec.phi181
  %lsr.iv.next269 = add i64 %lsr.iv268, 4
  %lsr.iv.next271 = add i32 %lsr.iv270, 4
  %lsr.iv.next273 = add i32 %lsr.iv272, 4
  %205 = icmp eq i64 %lsr.iv.next269, 0
  br i1 %205, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !15

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %206 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %204)
  br i1 %cmp.n185, label %for_loop_test26.after_for25_crit_edge.us.us.us.us, label %for_loop_body23.us.us.us.us.preheader

for_loop_body23.us.us.us.us.preheader:            ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv136.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec179, %vec.epilog.middle.block ]
  %.15677.us.us.us.us.ph = phi float [ %192, %vec.epilog.iter.check ], [ %.05581.us.us.us.us, %iter.check ], [ %.05581.us.us.us.us, %vector.scevcheck ], [ %206, %vec.epilog.middle.block ]
  br i1 %lcmp.mod198.not, label %for_loop_body23.us.us.us.us.prol.loopexit, label %for_loop_body23.us.us.us.us.prol.preheader

for_loop_body23.us.us.us.us.prol.preheader:       ; preds = %for_loop_body23.us.us.us.us.preheader
  br label %for_loop_body23.us.us.us.us.prol

for_loop_body23.us.us.us.us.prol:                 ; preds = %for_loop_body23.us.us.us.us.prol, %for_loop_body23.us.us.us.us.prol.preheader
  %lsr.iv280 = phi i64 [ %xtraiter197, %for_loop_body23.us.us.us.us.prol.preheader ], [ %lsr.iv.next281, %for_loop_body23.us.us.us.us.prol ]
  %indvars.iv136.prol = phi i64 [ %indvars.iv.next137.prol, %for_loop_body23.us.us.us.us.prol ], [ %indvars.iv136.ph, %for_loop_body23.us.us.us.us.prol.preheader ]
  %.15677.us.us.us.us.prol = phi float [ %217, %for_loop_body23.us.us.us.us.prol ], [ %.15677.us.us.us.us.ph, %for_loop_body23.us.us.us.us.prol.preheader ]
  %207 = add i64 %lsr.iv277, %indvars.iv136.prol
  %tmp279 = trunc i64 %207 to i32
  %208 = sext i32 %tmp279 to i64
  %209 = getelementptr float, ptr %150, i64 %208
  %210 = load float, ptr %209, align 4
  %211 = add i64 %lsr.iv274, %indvars.iv136.prol
  %tmp276 = trunc i64 %211 to i32
  %212 = sext i32 %tmp276 to i64
  %213 = getelementptr float, ptr %150, i64 %212
  %214 = load float, ptr %213, align 4
  %215 = fsub reassoc ninf nsz float %210, %214
  %216 = fmul reassoc ninf nsz float %215, %215
  %217 = fadd reassoc ninf nsz float %216, %.15677.us.us.us.us.prol
  %indvars.iv.next137.prol = add nuw nsw i64 %indvars.iv136.prol, 1
  %lsr.iv.next281 = add nsw i64 %lsr.iv280, -1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next281, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body23.us.us.us.us.prol.loopexit.loopexit, label %for_loop_body23.us.us.us.us.prol, !llvm.loop !16

for_loop_body23.us.us.us.us.prol.loopexit.loopexit: ; preds = %for_loop_body23.us.us.us.us.prol
  br label %for_loop_body23.us.us.us.us.prol.loopexit

for_loop_body23.us.us.us.us.prol.loopexit:        ; preds = %for_loop_body23.us.us.us.us.prol.loopexit.loopexit, %for_loop_body23.us.us.us.us.preheader
  %.lcssa194.unr = phi float [ poison, %for_loop_body23.us.us.us.us.preheader ], [ %217, %for_loop_body23.us.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv136.unr = phi i64 [ %indvars.iv136.ph, %for_loop_body23.us.us.us.us.preheader ], [ %indvars.iv.next137.prol, %for_loop_body23.us.us.us.us.prol.loopexit.loopexit ]
  %.15677.us.us.us.us.unr = phi float [ %.15677.us.us.us.us.ph, %for_loop_body23.us.us.us.us.preheader ], [ %217, %for_loop_body23.us.us.us.us.prol.loopexit.loopexit ]
  %218 = sub nsw i64 %indvars.iv136.ph, %wide.trip.count139
  %219 = icmp ugt i64 %218, -4
  br i1 %219, label %for_loop_test26.after_for25_crit_edge.us.us.us.us, label %for_loop_body23.us.us.us.us.preheader.new

for_loop_body23.us.us.us.us.preheader.new:        ; preds = %for_loop_body23.us.us.us.us.prol.loopexit
  br label %for_loop_body23.us.us.us.us

for_loop_body23.us.us.us.us:                      ; preds = %for_loop_body23.us.us.us.us, %for_loop_body23.us.us.us.us.preheader.new
  %indvars.iv136 = phi i64 [ %indvars.iv136.unr, %for_loop_body23.us.us.us.us.preheader.new ], [ %indvars.iv.next137.3, %for_loop_body23.us.us.us.us ]
  %.15677.us.us.us.us = phi float [ %.15677.us.us.us.us.unr, %for_loop_body23.us.us.us.us.preheader.new ], [ %263, %for_loop_body23.us.us.us.us ]
  %220 = add i64 %lsr.iv277, %indvars.iv136
  %tmp289 = trunc i64 %220 to i32
  %221 = sext i32 %tmp289 to i64
  %222 = getelementptr float, ptr %150, i64 %221
  %223 = load float, ptr %222, align 4
  %224 = add i64 %lsr.iv274, %indvars.iv136
  %tmp288 = trunc i64 %224 to i32
  %225 = sext i32 %tmp288 to i64
  %226 = getelementptr float, ptr %150, i64 %225
  %227 = load float, ptr %226, align 4
  %228 = fsub reassoc ninf nsz float %223, %227
  %229 = fmul reassoc ninf nsz float %228, %228
  %230 = fadd reassoc ninf nsz float %229, %.15677.us.us.us.us
  %231 = add i64 %220, 1
  %tmp287 = trunc i64 %231 to i32
  %232 = sext i32 %tmp287 to i64
  %233 = getelementptr float, ptr %150, i64 %232
  %234 = load float, ptr %233, align 4
  %235 = add i64 %224, 1
  %tmp286 = trunc i64 %235 to i32
  %236 = sext i32 %tmp286 to i64
  %237 = getelementptr float, ptr %150, i64 %236
  %238 = load float, ptr %237, align 4
  %239 = fsub reassoc ninf nsz float %234, %238
  %240 = fmul reassoc ninf nsz float %239, %239
  %241 = fadd reassoc ninf nsz float %240, %230
  %242 = add i64 %220, 2
  %tmp285 = trunc i64 %242 to i32
  %243 = sext i32 %tmp285 to i64
  %244 = getelementptr float, ptr %150, i64 %243
  %245 = load float, ptr %244, align 4
  %246 = add i64 %224, 2
  %tmp284 = trunc i64 %246 to i32
  %247 = sext i32 %tmp284 to i64
  %248 = getelementptr float, ptr %150, i64 %247
  %249 = load float, ptr %248, align 4
  %250 = fsub reassoc ninf nsz float %245, %249
  %251 = fmul reassoc ninf nsz float %250, %250
  %252 = fadd reassoc ninf nsz float %251, %241
  %253 = add i64 %220, 3
  %tmp283 = trunc i64 %253 to i32
  %254 = sext i32 %tmp283 to i64
  %255 = getelementptr float, ptr %150, i64 %254
  %256 = load float, ptr %255, align 4
  %257 = add i64 %224, 3
  %tmp282 = trunc i64 %257 to i32
  %258 = sext i32 %tmp282 to i64
  %259 = getelementptr float, ptr %150, i64 %258
  %260 = load float, ptr %259, align 4
  %261 = fsub reassoc ninf nsz float %256, %260
  %262 = fmul reassoc ninf nsz float %261, %261
  %263 = fadd reassoc ninf nsz float %262, %252
  %indvars.iv.next137.3 = add nuw nsw i64 %indvars.iv136, 4
  %exitcond140.not.3 = icmp eq i64 %wide.trip.count139, %indvars.iv.next137.3
  br i1 %exitcond140.not.3, label %for_loop_test26.after_for25_crit_edge.us.us.us.us.loopexit, label %for_loop_body23.us.us.us.us, !llvm.loop !17

for_loop_test26.after_for25_crit_edge.us.us.us.us.loopexit: ; preds = %for_loop_body23.us.us.us.us
  br label %for_loop_test26.after_for25_crit_edge.us.us.us.us

for_loop_test26.after_for25_crit_edge.us.us.us.us: ; preds = %for_loop_test26.after_for25_crit_edge.us.us.us.us.loopexit, %for_loop_body23.us.us.us.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa = phi float [ %192, %middle.block ], [ %206, %vec.epilog.middle.block ], [ %.lcssa194.unr, %for_loop_body23.us.us.us.us.prol.loopexit ], [ %263, %for_loop_test26.after_for25_crit_edge.us.us.us.us.loopexit ]
  %264 = add nuw nsw i32 %.05482.us.us.us.us, 1
  %lsr.iv.next278 = add i64 %lsr.iv277, %159
  %lsr.iv.next275 = add i64 %lsr.iv274, %159
  %exitcond141.not = icmp eq i32 %264, %.fr130
  br i1 %exitcond141.not, label %for_loop_test22.after_for21_crit_edge.split.us.us.us.us, label %iter.check

for_loop_test22.after_for21_crit_edge.split.us.us.us.us: ; preds = %for_loop_test26.after_for25_crit_edge.us.us.us.us
  %265 = icmp slt i32 %.388.us.us.us, %28
  br i1 %265, label %true_block27.us.us.us, label %false_block28.us.us.us

for_loop_body1.us:                                ; preds = %for_loop_inc2.us, %for_loop_body1.us.preheader
  %.06093.us = phi i32 [ %315, %for_loop_inc2.us ], [ %neg, %for_loop_body1.us.preheader ]
  %.16292.us = phi i32 [ %.061.us, %for_loop_inc2.us ], [ 0, %for_loop_body1.us.preheader ]
  %266 = add i32 %.06093.us, %88
  %267 = icmp slt i32 %266, 0
  br i1 %267, label %for_loop_inc2.us, label %false_block.us

false_block.us:                                   ; preds = %for_loop_body1.us
  %268 = load ptr, ptr %0, align 8
  %269 = getelementptr i8, ptr %268, i64 120
  %270 = load i32, ptr %269, align 4
  %271 = add i32 %65, %270
  %.not.us = icmp slt i32 %266, %271
  br i1 %.not.us, label %for_loop_test11.preheader.us, label %for_loop_inc2.us

for_loop_body8.us95:                              ; preds = %for_loop_test11.preheader.us, %for_loop_inc9.us112
  %.05889.us96 = phi i32 [ %neg, %for_loop_test11.preheader.us ], [ %314, %for_loop_inc9.us112 ]
  %.388.us97 = phi i32 [ %.16292.us, %for_loop_test11.preheader.us ], [ %.2.us113, %for_loop_inc9.us112 ]
  %272 = add i32 %.05889.us96, %92
  %273 = icmp slt i32 %272, 0
  br i1 %273, label %for_loop_inc9.us112, label %false_block13.us98

false_block13.us98:                               ; preds = %for_loop_body8.us95
  %274 = load i32, ptr %317, align 4
  %275 = add i32 %65, %274
  %.not74.us99 = icmp slt i32 %272, %275
  br i1 %.not74.us99, label %for_loop_test22.preheader.us114, label %for_loop_inc9.us112

false_block28.us100:                              ; preds = %for_loop_test22.preheader.us114
  %276 = load float, ptr %3, align 4
  br i1 %69, label %for_loop_body30.us105.preheader, label %after_for32.us101

for_loop_body30.us105.preheader:                  ; preds = %false_block28.us100
  br i1 %75, label %after_for32.us101.loopexit.unr-lcssa, label %for_loop_body30.us105.preheader235

for_loop_body30.us105.preheader235:               ; preds = %for_loop_body30.us105.preheader
  br label %for_loop_body30.us105

after_for32.us101.loopexit.unr-lcssa.loopexit:    ; preds = %for_loop_body30.us105
  br label %after_for32.us101.loopexit.unr-lcssa

after_for32.us101.loopexit.unr-lcssa:             ; preds = %after_for32.us101.loopexit.unr-lcssa.loopexit, %for_loop_body30.us105.preheader
  %.152.us109.lcssa.ph = phi i32 [ poison, %for_loop_body30.us105.preheader ], [ %.152.us109.7, %after_for32.us101.loopexit.unr-lcssa.loopexit ]
  %.1.us110.lcssa.ph = phi float [ poison, %for_loop_body30.us105.preheader ], [ %.1.us110.7, %after_for32.us101.loopexit.unr-lcssa.loopexit ]
  %indvars.iv.unr = phi i64 [ 1, %for_loop_body30.us105.preheader ], [ %indvars.iv.next.7, %after_for32.us101.loopexit.unr-lcssa.loopexit ]
  %.05085.us107.unr = phi float [ %276, %for_loop_body30.us105.preheader ], [ %.1.us110.7, %after_for32.us101.loopexit.unr-lcssa.loopexit ]
  %.05184.us108.unr = phi i32 [ 0, %for_loop_body30.us105.preheader ], [ %.152.us109.7, %after_for32.us101.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for32.us101.loopexit, label %for_loop_body30.us105.epil.preheader

for_loop_body30.us105.epil.preheader:             ; preds = %after_for32.us101.loopexit.unr-lcssa
  br label %for_loop_body30.us105.epil

for_loop_body30.us105.epil:                       ; preds = %for_loop_body30.us105.epil, %for_loop_body30.us105.epil.preheader
  %lsr.iv = phi i64 [ %xtraiter, %for_loop_body30.us105.epil.preheader ], [ %lsr.iv.next, %for_loop_body30.us105.epil ]
  %indvars.iv.epil = phi i64 [ %indvars.iv.next.epil, %for_loop_body30.us105.epil ], [ %indvars.iv.unr, %for_loop_body30.us105.epil.preheader ]
  %.05085.us107.epil = phi float [ %.1.us110.epil, %for_loop_body30.us105.epil ], [ %.05085.us107.unr, %for_loop_body30.us105.epil.preheader ]
  %.05184.us108.epil = phi i32 [ %.152.us109.epil, %for_loop_body30.us105.epil ], [ %.05184.us108.unr, %for_loop_body30.us105.epil.preheader ]
  %277 = shl i64 %indvars.iv.epil, 2
  %scevgep253 = getelementptr i8, ptr %3, i64 %277
  %278 = load float, ptr %scevgep253, align 4
  %279 = fcmp reassoc ninf nsz ogt float %278, %.05085.us107.epil
  %tmp = trunc i64 %indvars.iv.epil to i32
  %.152.us109.epil = select i1 %279, i32 %tmp, i32 %.05184.us108.epil
  %.1.us110.epil = select i1 %279, float %278, float %.05085.us107.epil
  %indvars.iv.next.epil = add nuw nsw i64 %indvars.iv.epil, 1
  %lsr.iv.next = add nsw i64 %lsr.iv, -1
  %epil.iter.cmp.not = icmp eq i64 %lsr.iv.next, 0
  br i1 %epil.iter.cmp.not, label %after_for32.us101.loopexit.loopexit, label %for_loop_body30.us105.epil, !llvm.loop !18

after_for32.us101.loopexit.loopexit:              ; preds = %for_loop_body30.us105.epil
  br label %after_for32.us101.loopexit

after_for32.us101.loopexit:                       ; preds = %after_for32.us101.loopexit.loopexit, %after_for32.us101.loopexit.unr-lcssa
  %.152.us109.lcssa = phi i32 [ %.152.us109.lcssa.ph, %after_for32.us101.loopexit.unr-lcssa ], [ %.152.us109.epil, %after_for32.us101.loopexit.loopexit ]
  %.1.us110.lcssa = phi float [ %.1.us110.lcssa.ph, %after_for32.us101.loopexit.unr-lcssa ], [ %.1.us110.epil, %after_for32.us101.loopexit.loopexit ]
  %280 = zext nneg i32 %.152.us109.lcssa to i64
  br label %after_for32.us101

after_for32.us101:                                ; preds = %after_for32.us101.loopexit, %false_block28.us100
  %.051.lcssa.us102 = phi i64 [ 0, %false_block28.us100 ], [ %280, %after_for32.us101.loopexit ]
  %.050.lcssa.us103 = phi float [ %276, %false_block28.us100 ], [ %.1.us110.lcssa, %after_for32.us101.loopexit ]
  %281 = fcmp reassoc ninf nsz ogt float %.050.lcssa.us103, 0.000000e+00
  br i1 %281, label %true_block37.us104, label %for_loop_inc9.us112

true_block37.us104:                               ; preds = %after_for32.us101
  %282 = getelementptr [32 x float], ptr %3, i64 0, i64 %.051.lcssa.us102
  store float 0.000000e+00, ptr %282, align 4
  %283 = getelementptr [32 x i32], ptr %4, i64 0, i64 %.051.lcssa.us102
  store i32 %266, ptr %283, align 4
  %284 = getelementptr [32 x i32], ptr %5, i64 0, i64 %.051.lcssa.us102
  store i32 %272, ptr %284, align 4
  br label %for_loop_inc9.us112

for_loop_body30.us105:                            ; preds = %for_loop_body30.us105, %for_loop_body30.us105.preheader235
  %indvars.iv = phi i64 [ %indvars.iv.next.7, %for_loop_body30.us105 ], [ 1, %for_loop_body30.us105.preheader235 ]
  %.05085.us107 = phi float [ %.1.us110.7, %for_loop_body30.us105 ], [ %276, %for_loop_body30.us105.preheader235 ]
  %.05184.us108 = phi i32 [ %.152.us109.7, %for_loop_body30.us105 ], [ 0, %for_loop_body30.us105.preheader235 ]
  %niter = phi i64 [ %niter.next.7, %for_loop_body30.us105 ], [ 0, %for_loop_body30.us105.preheader235 ]
  %lsr252 = trunc i64 %indvars.iv to i32
  %285 = shl i64 %indvars.iv, 2
  %scevgep249 = getelementptr i8, ptr %3, i64 %285
  %286 = load float, ptr %scevgep249, align 4
  %287 = fcmp reassoc ninf nsz ogt float %286, %.05085.us107
  %.152.us109 = select i1 %287, i32 %lsr252, i32 %.05184.us108
  %.1.us110 = select i1 %287, float %286, float %.05085.us107
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %scevgep251 = getelementptr i8, ptr %scevgep249, i64 4
  %288 = load float, ptr %scevgep251, align 4
  %289 = fcmp reassoc ninf nsz ogt float %288, %.1.us110
  %290 = trunc nuw nsw i64 %indvars.iv.next to i32
  %.152.us109.1 = select i1 %289, i32 %290, i32 %.152.us109
  %.1.us110.1 = select i1 %289, float %288, float %.1.us110
  %indvars.iv.next.1 = add nuw nsw i64 %indvars.iv, 2
  %scevgep248 = getelementptr i8, ptr %scevgep249, i64 8
  %291 = load float, ptr %scevgep248, align 4
  %292 = fcmp reassoc ninf nsz ogt float %291, %.1.us110.1
  %293 = trunc nuw nsw i64 %indvars.iv.next.1 to i32
  %.152.us109.2 = select i1 %292, i32 %293, i32 %.152.us109.1
  %.1.us110.2 = select i1 %292, float %291, float %.1.us110.1
  %indvars.iv.next.2 = add nuw nsw i64 %indvars.iv, 3
  %scevgep246 = getelementptr i8, ptr %scevgep249, i64 12
  %294 = load float, ptr %scevgep246, align 4
  %295 = fcmp reassoc ninf nsz ogt float %294, %.1.us110.2
  %296 = trunc nuw nsw i64 %indvars.iv.next.2 to i32
  %.152.us109.3 = select i1 %295, i32 %296, i32 %.152.us109.2
  %.1.us110.3 = select i1 %295, float %294, float %.1.us110.2
  %indvars.iv.next.3 = add nuw nsw i64 %indvars.iv, 4
  %scevgep244 = getelementptr i8, ptr %scevgep249, i64 16
  %297 = load float, ptr %scevgep244, align 4
  %298 = fcmp reassoc ninf nsz ogt float %297, %.1.us110.3
  %299 = trunc nuw nsw i64 %indvars.iv.next.3 to i32
  %.152.us109.4 = select i1 %298, i32 %299, i32 %.152.us109.3
  %.1.us110.4 = select i1 %298, float %297, float %.1.us110.3
  %indvars.iv.next.4 = add nuw nsw i64 %indvars.iv, 5
  %scevgep242 = getelementptr i8, ptr %scevgep249, i64 20
  %300 = load float, ptr %scevgep242, align 4
  %301 = fcmp reassoc ninf nsz ogt float %300, %.1.us110.4
  %302 = trunc nuw nsw i64 %indvars.iv.next.4 to i32
  %.152.us109.5 = select i1 %301, i32 %302, i32 %.152.us109.4
  %.1.us110.5 = select i1 %301, float %300, float %.1.us110.4
  %indvars.iv.next.5 = add nuw nsw i64 %indvars.iv, 6
  %scevgep240 = getelementptr i8, ptr %scevgep249, i64 24
  %303 = load float, ptr %scevgep240, align 4
  %304 = fcmp reassoc ninf nsz ogt float %303, %.1.us110.5
  %305 = trunc nuw nsw i64 %indvars.iv.next.5 to i32
  %.152.us109.6 = select i1 %304, i32 %305, i32 %.152.us109.5
  %.1.us110.6 = select i1 %304, float %303, float %.1.us110.5
  %indvars.iv.next.6 = add nuw nsw i64 %indvars.iv, 7
  %scevgep238 = getelementptr i8, ptr %scevgep249, i64 28
  %306 = load float, ptr %scevgep238, align 4
  %307 = fcmp reassoc ninf nsz ogt float %306, %.1.us110.6
  %308 = trunc nuw nsw i64 %indvars.iv.next.6 to i32
  %.152.us109.7 = select i1 %307, i32 %308, i32 %.152.us109.6
  %.1.us110.7 = select i1 %307, float %306, float %.1.us110.6
  %indvars.iv.next.7 = add nuw i64 %indvars.iv, 8
  %niter.next.7 = add i64 %niter, 8
  %niter.ncmp.7 = icmp eq i64 %niter.next.7, %unroll_iter
  br i1 %niter.ncmp.7, label %after_for32.us101.loopexit.unr-lcssa.loopexit, label %for_loop_body30.us105

true_block27.us111:                               ; preds = %for_loop_test22.preheader.us114
  %309 = sext i32 %.388.us97 to i64
  %310 = getelementptr [32 x float], ptr %3, i64 0, i64 %309
  store float 0.000000e+00, ptr %310, align 4
  %311 = getelementptr [32 x i32], ptr %4, i64 0, i64 %309
  store i32 %266, ptr %311, align 4
  %312 = getelementptr [32 x i32], ptr %5, i64 0, i64 %309
  store i32 %272, ptr %312, align 4
  %313 = add nsw i32 %.388.us97, 1
  br label %for_loop_inc9.us112

for_loop_inc9.us112:                              ; preds = %true_block27.us111, %true_block37.us104, %after_for32.us101, %false_block13.us98, %for_loop_body8.us95
  %.2.us113 = phi i32 [ %.388.us97, %false_block13.us98 ], [ %313, %true_block27.us111 ], [ %.388.us97, %true_block37.us104 ], [ %.388.us97, %after_for32.us101 ], [ %.388.us97, %for_loop_body8.us95 ]
  %314 = add nsw i32 %.05889.us96, 1
  %exitcond134.not = icmp eq i32 %.05889.us96, %24
  br i1 %exitcond134.not, label %for_loop_inc2.us.loopexit, label %for_loop_body8.us95

for_loop_inc2.us.loopexit:                        ; preds = %for_loop_inc9.us112
  br label %for_loop_inc2.us

for_loop_inc2.us:                                 ; preds = %for_loop_inc2.us.loopexit, %false_block.us, %for_loop_body1.us
  %.061.us = phi i32 [ %.16292.us, %false_block.us ], [ %.16292.us, %for_loop_body1.us ], [ %.2.us113, %for_loop_inc2.us.loopexit ]
  %315 = add nsw i32 %.06093.us, 1
  %exitcond135.not = icmp eq i32 %.06093.us, %24
  br i1 %exitcond135.not, label %for_loop_test43.preheader.loopexit237, label %for_loop_body1.us

for_loop_test22.preheader.us114:                  ; preds = %false_block13.us98
  %316 = icmp slt i32 %.388.us97, %28
  br i1 %316, label %true_block27.us111, label %false_block28.us100

for_loop_test11.preheader.us:                     ; preds = %false_block.us
  %317 = getelementptr i8, ptr %268, i64 124
  br label %for_loop_body8.us95

after_for.loopexit:                               ; preds = %after_for42
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_test43.preheader.loopexit:               ; preds = %for_loop_inc2.us.us
  br label %for_loop_test43.preheader

for_loop_test43.preheader.loopexit237:            ; preds = %for_loop_inc2.us
  br label %for_loop_test43.preheader

for_loop_test43.preheader:                        ; preds = %for_loop_test43.preheader.loopexit237, %for_loop_test43.preheader.loopexit, %for_loop_body
  %.162.lcssa = phi i32 [ 0, %for_loop_body ], [ %.061.us.us, %for_loop_test43.preheader.loopexit ], [ %.061.us, %for_loop_test43.preheader.loopexit237 ]
  br i1 %70, label %for_loop_body40.preheader, label %after_for42

for_loop_body40.preheader:                        ; preds = %for_loop_test43.preheader
  %318 = sext i32 %.162.lcssa to i64
  br label %for_loop_body40

for_loop_body40:                                  ; preds = %after_if46, %for_loop_body40.preheader
  %indvars.iv153 = phi i64 [ 0, %for_loop_body40.preheader ], [ %indvars.iv.next154, %after_if46 ]
  %lsr321 = trunc i64 %indvars.iv153 to i32
  %319 = icmp slt i64 %indvars.iv153, %318
  br i1 %319, label %true_block44, label %false_block45

after_for42.loopexit:                             ; preds = %after_if46
  br label %after_for42

after_for42:                                      ; preds = %after_for42.loopexit, %for_loop_test43.preheader
  %320 = add nsw i32 %.063129, 1
  %exitcond158.not = icmp eq i32 %320, %21
  br i1 %exitcond158.not, label %after_for.loopexit, label %for_loop_body

true_block44:                                     ; preds = %for_loop_body40
  %321 = getelementptr [32 x i32], ptr %4, i64 0, i64 %indvars.iv153
  %322 = load i32, ptr %321, align 4
  %323 = getelementptr [32 x i32], ptr %5, i64 0, i64 %indvars.iv153
  %324 = load i32, ptr %323, align 4
  %325 = load ptr, ptr %0, align 8
  %326 = getelementptr i8, ptr %325, i64 48
  %327 = load ptr, ptr %326, align 8
  %328 = getelementptr i8, ptr %325, i64 44
  %329 = load i32, ptr %328, align 4
  %330 = mul i32 %329, %.063129
  %331 = add i32 %330, %lsr321
  %332 = sext i32 %331 to i64
  %333 = getelementptr i32, ptr %327, i64 %332
  store i32 %322, ptr %333, align 4
  %334 = load ptr, ptr %0, align 8
  %335 = getelementptr i8, ptr %334, i64 64
  %336 = load ptr, ptr %335, align 8
  %337 = getelementptr i8, ptr %334, i64 60
  %338 = load i32, ptr %337, align 4
  %339 = mul i32 %338, %.063129
  %340 = add i32 %339, %lsr321
  %341 = sext i32 %340 to i64
  %342 = getelementptr i32, ptr %336, i64 %341
  store i32 %324, ptr %342, align 4
  %343 = load ptr, ptr %0, align 8
  %344 = getelementptr i8, ptr %343, i64 80
  %345 = load ptr, ptr %344, align 8
  %346 = getelementptr i8, ptr %343, i64 76
  %347 = load i32, ptr %346, align 4
  %348 = mul i32 %347, %.063129
  %349 = add i32 %348, %lsr321
  %350 = sext i32 %349 to i64
  %351 = getelementptr i32, ptr %345, i64 %350
  store i32 1, ptr %351, align 4
  br i1 %66, label %for_loop_body47.lr.ph, label %after_if46

for_loop_body47.lr.ph:                            ; preds = %true_block44
  %352 = load ptr, ptr %0, align 8
  %353 = getelementptr i8, ptr %352, i64 32
  %354 = getelementptr i8, ptr %352, i64 20
  %355 = getelementptr i8, ptr %352, i64 24
  %356 = getelementptr i8, ptr %352, i64 28
  %357 = add i32 %324, 1
  br label %for_loop_body47.us

for_loop_body47.us:                               ; preds = %for_loop_test54.after_for53_crit_edge.us, %for_loop_body47.lr.ph
  %lsr.iv318 = phi i32 [ %lsr.iv.next319, %for_loop_test54.after_for53_crit_edge.us ], [ %322, %for_loop_body47.lr.ph ]
  %.047126.us = phi i32 [ 0, %for_loop_body47.lr.ph ], [ %421, %for_loop_test54.after_for53_crit_edge.us ]
  %358 = add i32 %.047126.us, %322
  br i1 %78, label %for_loop_test54.after_for53_crit_edge.us.unr-lcssa, label %for_loop_body51.us.preheader

for_loop_body51.us.preheader:                     ; preds = %for_loop_body47.us
  br label %for_loop_body51.us

for_loop_body51.us:                               ; preds = %for_loop_body51.us, %for_loop_body51.us.preheader
  %.046125.us = phi i32 [ %400, %for_loop_body51.us ], [ 0, %for_loop_body51.us.preheader ]
  %359 = load ptr, ptr %67, align 8
  %360 = load i32, ptr %68, align 4
  %361 = mul i32 %lsr.iv318, %360
  %362 = add i32 %324, %.046125.us
  %363 = add i32 %362, %361
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, ptr %359, i64 %364
  %366 = load float, ptr %365, align 4
  %367 = load ptr, ptr %353, align 8
  %368 = load i32, ptr %354, align 4
  %369 = load i32, ptr %355, align 4
  %370 = load i32, ptr %356, align 4
  %371 = mul i32 %.063129, %368
  %372 = add i32 %lsr321, %371
  %373 = mul i32 %369, %372
  %374 = add i32 %.047126.us, %373
  %375 = mul i32 %370, %374
  %376 = add i32 %.046125.us, %375
  %377 = sext i32 %376 to i64
  %378 = getelementptr float, ptr %367, i64 %377
  store float %366, ptr %378, align 4
  %379 = load ptr, ptr %67, align 8
  %380 = load i32, ptr %68, align 4
  %381 = mul i32 %lsr.iv318, %380
  %382 = add i32 %357, %.046125.us
  %383 = add i32 %382, %381
  %384 = sext i32 %383 to i64
  %385 = getelementptr float, ptr %379, i64 %384
  %386 = load float, ptr %385, align 4
  %387 = load ptr, ptr %353, align 8
  %388 = load i32, ptr %354, align 4
  %389 = load i32, ptr %355, align 4
  %390 = load i32, ptr %356, align 4
  %391 = mul i32 %.063129, %388
  %392 = add i32 %lsr321, %391
  %393 = mul i32 %389, %392
  %394 = add i32 %.047126.us, %393
  %395 = mul i32 %390, %394
  %396 = add i32 %.046125.us, %395
  %397 = add i32 %396, 1
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, ptr %387, i64 %398
  store float %386, ptr %399, align 4
  %400 = add nuw i32 %.046125.us, 2
  %niter215.ncmp.1 = icmp eq i32 %unroll_iter209, %400
  br i1 %niter215.ncmp.1, label %for_loop_test54.after_for53_crit_edge.us.unr-lcssa.loopexit, label %for_loop_body51.us

for_loop_test54.after_for53_crit_edge.us.unr-lcssa.loopexit: ; preds = %for_loop_body51.us
  br label %for_loop_test54.after_for53_crit_edge.us.unr-lcssa

for_loop_test54.after_for53_crit_edge.us.unr-lcssa: ; preds = %for_loop_test54.after_for53_crit_edge.us.unr-lcssa.loopexit, %for_loop_body47.us
  %.046125.us.unr = phi i32 [ 0, %for_loop_body47.us ], [ %400, %for_loop_test54.after_for53_crit_edge.us.unr-lcssa.loopexit ]
  br i1 %lcmp.mod208.not, label %for_loop_test54.after_for53_crit_edge.us, label %for_loop_body51.us.epil

for_loop_body51.us.epil:                          ; preds = %for_loop_test54.after_for53_crit_edge.us.unr-lcssa
  %401 = add i32 %.046125.us.unr, %324
  %402 = load ptr, ptr %67, align 8
  %403 = load i32, ptr %68, align 4
  %404 = mul i32 %403, %358
  %405 = add i32 %401, %404
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, ptr %402, i64 %406
  %408 = load float, ptr %407, align 4
  %409 = load ptr, ptr %353, align 8
  %410 = load i32, ptr %354, align 4
  %411 = load i32, ptr %355, align 4
  %412 = load i32, ptr %356, align 4
  %413 = mul i32 %410, %.063129
  %414 = add i32 %413, %lsr321
  %415 = mul i32 %414, %411
  %416 = add i32 %415, %.047126.us
  %417 = mul i32 %416, %412
  %418 = add i32 %417, %.046125.us.unr
  %419 = sext i32 %418 to i64
  %420 = getelementptr float, ptr %409, i64 %419
  store float %408, ptr %420, align 4
  br label %for_loop_test54.after_for53_crit_edge.us

for_loop_test54.after_for53_crit_edge.us:         ; preds = %for_loop_body51.us.epil, %for_loop_test54.after_for53_crit_edge.us.unr-lcssa
  %421 = add nuw nsw i32 %.047126.us, 1
  %lsr.iv.next319 = add i32 %lsr.iv318, 1
  %exitcond152.not = icmp eq i32 %421, %.fr130
  br i1 %exitcond152.not, label %after_if46.loopexit, label %for_loop_body47.us

false_block45:                                    ; preds = %for_loop_body40
  %422 = load ptr, ptr %0, align 8
  %423 = getelementptr i8, ptr %422, i64 48
  %424 = load ptr, ptr %423, align 8
  %425 = getelementptr i8, ptr %422, i64 44
  %426 = load i32, ptr %425, align 4
  %427 = mul i32 %426, %.063129
  %428 = add i32 %427, %lsr321
  %429 = sext i32 %428 to i64
  %430 = getelementptr i32, ptr %424, i64 %429
  store i32 0, ptr %430, align 4
  %431 = load ptr, ptr %0, align 8
  %432 = getelementptr i8, ptr %431, i64 64
  %433 = load ptr, ptr %432, align 8
  %434 = getelementptr i8, ptr %431, i64 60
  %435 = load i32, ptr %434, align 4
  %436 = mul i32 %435, %.063129
  %437 = add i32 %436, %lsr321
  %438 = sext i32 %437 to i64
  %439 = getelementptr i32, ptr %433, i64 %438
  store i32 0, ptr %439, align 4
  %440 = load ptr, ptr %0, align 8
  %441 = getelementptr i8, ptr %440, i64 80
  %442 = load ptr, ptr %441, align 8
  %443 = getelementptr i8, ptr %440, i64 76
  %444 = load i32, ptr %443, align 4
  %445 = mul i32 %444, %.063129
  %446 = add i32 %445, %lsr321
  %447 = sext i32 %446 to i64
  %448 = getelementptr i32, ptr %442, i64 %447
  store i32 0, ptr %448, align 4
  br i1 %66, label %for_loop_test62.preheader.lr.ph, label %after_if46

for_loop_test62.preheader.lr.ph:                  ; preds = %false_block45
  %449 = load ptr, ptr %0, align 8
  %450 = getelementptr i8, ptr %449, i64 32
  %451 = getelementptr i8, ptr %449, i64 20
  %452 = getelementptr i8, ptr %449, i64 24
  %453 = getelementptr i8, ptr %449, i64 28
  br label %for_loop_test62.preheader.us

for_loop_test62.preheader.us:                     ; preds = %for_loop_test62.after_for61_crit_edge.us, %for_loop_test62.preheader.lr.ph
  %.045124.us = phi i32 [ 0, %for_loop_test62.preheader.lr.ph ], [ %492, %for_loop_test62.after_for61_crit_edge.us ]
  br i1 %78, label %for_loop_test62.after_for61_crit_edge.us.unr-lcssa, label %for_loop_body59.us.preheader

for_loop_body59.us.preheader:                     ; preds = %for_loop_test62.preheader.us
  br label %for_loop_body59.us

for_loop_body59.us:                               ; preds = %for_loop_body59.us, %for_loop_body59.us.preheader
  %.0123.us = phi i32 [ %479, %for_loop_body59.us ], [ 0, %for_loop_body59.us.preheader ]
  %454 = load ptr, ptr %450, align 8
  %455 = load i32, ptr %451, align 4
  %456 = load i32, ptr %452, align 4
  %457 = load i32, ptr %453, align 4
  %458 = mul i32 %.063129, %455
  %459 = add i32 %lsr321, %458
  %460 = mul i32 %456, %459
  %461 = add i32 %.045124.us, %460
  %462 = mul i32 %457, %461
  %463 = add i32 %.0123.us, %462
  %464 = sext i32 %463 to i64
  %465 = getelementptr float, ptr %454, i64 %464
  store float 0.000000e+00, ptr %465, align 4
  %466 = load ptr, ptr %450, align 8
  %467 = load i32, ptr %451, align 4
  %468 = load i32, ptr %452, align 4
  %469 = load i32, ptr %453, align 4
  %470 = mul i32 %.063129, %467
  %471 = add i32 %lsr321, %470
  %472 = mul i32 %468, %471
  %473 = add i32 %.045124.us, %472
  %474 = mul i32 %469, %473
  %475 = add i32 %.0123.us, %474
  %476 = add i32 %475, 1
  %477 = sext i32 %476 to i64
  %478 = getelementptr float, ptr %466, i64 %477
  store float 0.000000e+00, ptr %478, align 4
  %479 = add nuw i32 %.0123.us, 2
  %niter210.ncmp.1 = icmp eq i32 %unroll_iter209, %479
  br i1 %niter210.ncmp.1, label %for_loop_test62.after_for61_crit_edge.us.unr-lcssa.loopexit, label %for_loop_body59.us

for_loop_test62.after_for61_crit_edge.us.unr-lcssa.loopexit: ; preds = %for_loop_body59.us
  br label %for_loop_test62.after_for61_crit_edge.us.unr-lcssa

for_loop_test62.after_for61_crit_edge.us.unr-lcssa: ; preds = %for_loop_test62.after_for61_crit_edge.us.unr-lcssa.loopexit, %for_loop_test62.preheader.us
  %.0123.us.unr = phi i32 [ 0, %for_loop_test62.preheader.us ], [ %479, %for_loop_test62.after_for61_crit_edge.us.unr-lcssa.loopexit ]
  br i1 %lcmp.mod208.not, label %for_loop_test62.after_for61_crit_edge.us, label %for_loop_body59.us.epil

for_loop_body59.us.epil:                          ; preds = %for_loop_test62.after_for61_crit_edge.us.unr-lcssa
  %480 = load ptr, ptr %450, align 8
  %481 = load i32, ptr %451, align 4
  %482 = load i32, ptr %452, align 4
  %483 = load i32, ptr %453, align 4
  %484 = mul i32 %481, %.063129
  %485 = add i32 %484, %lsr321
  %486 = mul i32 %485, %482
  %487 = add i32 %486, %.045124.us
  %488 = mul i32 %487, %483
  %489 = add i32 %488, %.0123.us.unr
  %490 = sext i32 %489 to i64
  %491 = getelementptr float, ptr %480, i64 %490
  store float 0.000000e+00, ptr %491, align 4
  br label %for_loop_test62.after_for61_crit_edge.us

for_loop_test62.after_for61_crit_edge.us:         ; preds = %for_loop_body59.us.epil, %for_loop_test62.after_for61_crit_edge.us.unr-lcssa
  %492 = add nuw nsw i32 %.045124.us, 1
  %exitcond150.not = icmp eq i32 %492, %.fr130
  br i1 %exitcond150.not, label %after_if46.loopexit236, label %for_loop_test62.preheader.us

after_if46.loopexit:                              ; preds = %for_loop_test54.after_for53_crit_edge.us
  br label %after_if46

after_if46.loopexit236:                           ; preds = %for_loop_test62.after_for61_crit_edge.us
  br label %after_if46

after_if46:                                       ; preds = %after_if46.loopexit236, %after_if46.loopexit, %false_block45, %true_block44
  %indvars.iv.next154 = add nuw nsw i64 %indvars.iv153, 1
  %exitcond157.not = icmp eq i64 %indvars.iv.next154, %wide.trip.count
  br i1 %exitcond157.not, label %after_for42.loopexit, label %for_loop_body40
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !19

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !21

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
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #5

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #4

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #7 = { nounwind }

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
!12 = distinct !{!12, !13, !14}
!13 = !{!"llvm.loop.isvectorized", i32 1}
!14 = !{!"llvm.loop.unroll.runtime.disable"}
!15 = distinct !{!15, !13, !14}
!16 = distinct !{!16, !11}
!17 = distinct !{!17, !13}
!18 = distinct !{!18, !11}
!19 = distinct !{!19, !20}
!20 = !{!"llvm.loop.mustprogress"}
!21 = distinct !{!21, !20}
