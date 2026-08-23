; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_hough_peaks_kernel_c408_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %9 = load ptr, ptr %context, align 8
  %10 = getelementptr i8, ptr %9, i64 52
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

define void @_hough_peaks_kernel_c408_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #8
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
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 60
  %23 = load i32, ptr %22, align 4
  %neg = sub i32 0, %23
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = add i32 %23, 1
  %26 = getelementptr i8, ptr %19, i64 8
  %27 = getelementptr i8, ptr %19, i64 4
  %28 = icmp sgt i32 %25, %neg
  %29 = sext i32 %neg to i64
  %wide.trip.count = sext i32 %25 to i64
  %30 = xor i64 %29, -1
  %31 = add nsw i64 %30, %wide.trip.count
  %32 = sub i64 %wide.trip.count, %29
  %min.iters.check = icmp ult i64 %32, 8
  %33 = trunc i64 %31 to i32
  %34 = icmp ugt i64 %31, 4294967295
  %n.vec = and i64 %32, -8
  %35 = add nsw i64 %n.vec, %29
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %cmp.n = icmp eq i64 %32, %n.vec
  %36 = add nsw i64 %wide.trip.count, -1
  %37 = sub i64 0, %wide.trip.count
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %indvar = phi i32 [ 0, %for_loop_body.lr.ph ], [ %indvar.next, %for_loop_inc ]
  %.02045 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %139, %for_loop_inc ]
  %38 = load ptr, ptr %3, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 32872
  %40 = load ptr, ptr %39, align 8
  %41 = getelementptr inbounds nuw i8, ptr %40, i64 4
  %42 = load i32, ptr %41, align 4
  %43 = sdiv i32 %.02045, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.02045
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %44, %.02045
  %48 = and i1 %46, %47
  %.neg28 = sext i1 %48 to i32
  %49 = add i32 %43, %.neg28
  %50 = mul i32 %49, %42
  %51 = sub i32 %.02045, %50
  %52 = load ptr, ptr %26, align 8
  %53 = load i32, ptr %27, align 4
  %54 = mul i32 %49, %53
  %55 = add i32 %51, %54
  %56 = sext i32 %55 to i64
  %57 = getelementptr i32, ptr %52, i64 %56
  %58 = load i32, ptr %57, align 4
  %59 = icmp slt i32 %58, %21
  br i1 %59, label %for_loop_inc, label %for_loop_test4.preheader

for_loop_test4.preheader:                         ; preds = %for_loop_body
  br i1 %28, label %for_loop_body1.lr.ph, label %true_block31

for_loop_body1.lr.ph:                             ; preds = %for_loop_test4.preheader
  %60 = getelementptr inbounds nuw i8, ptr %40, i64 8
  %61 = getelementptr inbounds nuw i8, ptr %40, i64 12
  %62 = add i32 %16, %indvar
  %63 = add i32 %23, %50
  %64 = sub i32 %62, %63
  %invariant.op66 = add i32 %64, %33
  %broadcast.splatinsert49 = insertelement <8 x i32> poison, i32 %51, i64 0
  %broadcast.splat50 = shufflevector <8 x i32> %broadcast.splatinsert49, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert51 = insertelement <8 x ptr> poison, ptr %60, i64 0
  %broadcast.splat52 = shufflevector <8 x ptr> %broadcast.splatinsert51, <8 x ptr> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert55 = insertelement <8 x ptr> poison, ptr %61, i64 0
  %broadcast.splat56 = shufflevector <8 x ptr> %broadcast.splatinsert55, <8 x ptr> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert58 = insertelement <8 x i32> poison, i32 %58, i64 0
  %broadcast.splat59 = shufflevector <8 x i32> %broadcast.splatinsert58, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.after_for7_crit_edge.us, %for_loop_body1.lr.ph
  %.01834.us = phi i32 [ %neg, %for_loop_body1.lr.ph ], [ %109, %for_loop_test8.after_for7_crit_edge.us ]
  %.01933.us = phi i1 [ true, %for_loop_body1.lr.ph ], [ %.us-phi.us, %for_loop_test8.after_for7_crit_edge.us ]
  %65 = add i32 %.01834.us, %49
  %.fr = freeze i32 %65
  %66 = icmp sgt i32 %.fr, -1
  %67 = mul i32 %.fr, %53
  br i1 %66, label %for_loop_body5.us.us.preheader, label %for_loop_test8.after_for7_crit_edge.us

for_loop_body5.us.us.preheader:                   ; preds = %for_loop_body1.us
  br i1 %min.iters.check, label %for_loop_body5.us.us.preheader65, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %for_loop_body5.us.us.preheader
  %68 = add i32 %64, %67
  %.reass67 = add i32 %67, %invariant.op66
  %69 = icmp slt i32 %.reass67, %68
  %70 = or i1 %69, %34
  br i1 %70, label %for_loop_body5.us.us.preheader65, label %vector.ph

vector.ph:                                        ; preds = %vector.scevcheck
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %.01834.us, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert53 = insertelement <8 x i32> poison, i32 %.fr, i64 0
  %broadcast.splat54 = shufflevector <8 x i32> %broadcast.splatinsert53, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x i1> [ zeroinitializer, %vector.ph ], [ %predphi61, %vector.body ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %71 = or <8 x i32> %broadcast.splat, %vec.ind
  %72 = icmp ne <8 x i32> %71, zeroinitializer
  %73 = add <8 x i32> %broadcast.splat50, %vec.ind
  %wide.masked.gather = tail call <8 x i32> @llvm.masked.gather.v8i32.v8p0(<8 x ptr> %broadcast.splat52, i32 4, <8 x i1> %72, <8 x i32> poison)
  %74 = icmp slt <8 x i32> %broadcast.splat54, %wide.masked.gather
  %75 = icmp sgt <8 x i32> %73, splat (i32 -1)
  %76 = and <8 x i1> %75, %74
  %77 = select <8 x i1> %72, <8 x i1> %76, <8 x i1> zeroinitializer
  %wide.masked.gather57 = tail call <8 x i32> @llvm.masked.gather.v8i32.v8p0(<8 x ptr> %broadcast.splat56, i32 4, <8 x i1> %77, <8 x i32> poison)
  %78 = icmp slt <8 x i32> %73, %wide.masked.gather57
  %79 = select <8 x i1> %77, <8 x i1> %78, <8 x i1> zeroinitializer
  %80 = extractelement <8 x i32> %73, i64 0
  %81 = add i32 %80, %67
  %82 = sext i32 %81 to i64
  %83 = getelementptr i32, ptr %52, i64 %82
  %wide.masked.load = tail call <8 x i32> @llvm.masked.load.v8i32.p0(ptr %83, i32 4, <8 x i1> %79, <8 x i32> poison)
  %.not = icmp sgt <8 x i32> %wide.masked.load, %broadcast.splat59
  %not.62 = xor <8 x i1> %72, splat (i1 true)
  %not. = select <8 x i1> %not.62, <8 x i1> splat (i1 true), <8 x i1> %76
  %84 = select <8 x i1> %not., <8 x i1> %79, <8 x i1> zeroinitializer
  %predphi60 = select <8 x i1> %84, <8 x i1> %.not, <8 x i1> zeroinitializer
  %predphi60.fr = freeze <8 x i1> %predphi60
  %predphi61 = or <8 x i1> %vec.phi, %predphi60.fr
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %lsr.iv.next = add i64 %lsr.iv, -8
  %85 = icmp eq i64 %lsr.iv.next, 0
  br i1 %85, label %middle.block, label %vector.body, !llvm.loop !10

middle.block:                                     ; preds = %vector.body
  %86 = bitcast <8 x i1> %predphi61 to i8
  %.not64 = icmp eq i8 %86, 0
  %rdx.select = select i1 %.not64, i1 %.01933.us, i1 false
  br i1 %cmp.n, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us.us.preheader65

for_loop_body5.us.us.preheader65:                 ; preds = %middle.block, %vector.scevcheck, %for_loop_body5.us.us.preheader
  %indvars.iv.ph = phi i64 [ %29, %for_loop_body5.us.us.preheader ], [ %29, %vector.scevcheck ], [ %35, %middle.block ]
  %.231.us.us.ph = phi i1 [ %.01933.us, %for_loop_body5.us.us.preheader ], [ %.01933.us, %vector.scevcheck ], [ %rdx.select, %middle.block ]
  %87 = sub nsw i64 %wide.trip.count, %indvars.iv.ph
  %xtraiter = and i64 %87, 1
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %for_loop_body5.us.us.prol.loopexit, label %for_loop_body5.us.us.prol

for_loop_body5.us.us.prol:                        ; preds = %for_loop_body5.us.us.preheader65
  %88 = trunc nsw i64 %indvars.iv.ph to i32
  %89 = or i32 %.01834.us, %88
  %spec.select.us.us.prol = icmp eq i32 %89, 0
  br i1 %spec.select.us.us.prol, label %for_loop_inc6.us.us.prol, label %after_if14.us.us.prol

after_if14.us.us.prol:                            ; preds = %for_loop_body5.us.us.prol
  %90 = add i32 %51, %88
  %91 = load i32, ptr %60, align 4
  %92 = icmp slt i32 %.fr, %91
  %93 = icmp sgt i32 %90, -1
  %or.cond.us.us.prol = and i1 %93, %92
  br i1 %or.cond.us.us.prol, label %true_block22.us.us.prol, label %for_loop_inc6.us.us.prol

true_block22.us.us.prol:                          ; preds = %after_if14.us.us.prol
  %94 = load i32, ptr %61, align 4
  %95 = icmp slt i32 %90, %94
  br i1 %95, label %true_block25.us.us.prol, label %for_loop_inc6.us.us.prol

true_block25.us.us.prol:                          ; preds = %true_block22.us.us.prol
  %96 = add i32 %90, %67
  %97 = sext i32 %96 to i64
  %98 = getelementptr i32, ptr %52, i64 %97
  %99 = load i32, ptr %98, align 4
  %100 = icmp sle i32 %99, %58
  %spec.select30.us.us.prol = select i1 %100, i1 %.231.us.us.ph, i1 false
  br label %for_loop_inc6.us.us.prol

for_loop_inc6.us.us.prol:                         ; preds = %true_block25.us.us.prol, %true_block22.us.us.prol, %after_if14.us.us.prol, %for_loop_body5.us.us.prol
  %.1.us.us.prol = phi i1 [ %.231.us.us.ph, %for_loop_body5.us.us.prol ], [ %.231.us.us.ph, %true_block22.us.us.prol ], [ %spec.select30.us.us.prol, %true_block25.us.us.prol ], [ %.231.us.us.ph, %after_if14.us.us.prol ]
  %indvars.iv.next.prol = add nsw i64 %indvars.iv.ph, 1
  br label %for_loop_body5.us.us.prol.loopexit

for_loop_body5.us.us.prol.loopexit:               ; preds = %for_loop_inc6.us.us.prol, %for_loop_body5.us.us.preheader65
  %.1.us.us.lcssa.unr = phi i1 [ poison, %for_loop_body5.us.us.preheader65 ], [ %.1.us.us.prol, %for_loop_inc6.us.us.prol ]
  %indvars.iv.unr = phi i64 [ %indvars.iv.ph, %for_loop_body5.us.us.preheader65 ], [ %indvars.iv.next.prol, %for_loop_inc6.us.us.prol ]
  %.231.us.us.unr = phi i1 [ %.231.us.us.ph, %for_loop_body5.us.us.preheader65 ], [ %.1.us.us.prol, %for_loop_inc6.us.us.prol ]
  %101 = icmp eq i64 %indvars.iv.ph, %36
  br i1 %101, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us.us.preheader68

for_loop_body5.us.us.preheader68:                 ; preds = %for_loop_body5.us.us.prol.loopexit
  %102 = trunc i64 %indvars.iv.unr to i32
  %103 = add i32 %51, %102
  %104 = zext i32 %103 to i64
  %105 = add i32 %51, %67
  %106 = add i32 %105, %102
  %107 = zext i32 %106 to i64
  %108 = add i64 %37, %indvars.iv.unr
  br label %for_loop_body5.us.us

for_loop_test8.after_for7_crit_edge.us.loopexit:  ; preds = %for_loop_inc6.us.us.1
  br label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us:           ; preds = %for_loop_test8.after_for7_crit_edge.us.loopexit, %for_loop_body5.us.us.prol.loopexit, %middle.block, %for_loop_body1.us
  %.us-phi.us = phi i1 [ %.01933.us, %for_loop_body1.us ], [ %rdx.select, %middle.block ], [ %.1.us.us.lcssa.unr, %for_loop_body5.us.us.prol.loopexit ], [ %.1.us.us.1, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %109 = add nsw i32 %.01834.us, 1
  %exitcond47.not = icmp eq i32 %.01834.us, %23
  br i1 %exitcond47.not, label %after_for3, label %for_loop_body1.us

for_loop_body5.us.us:                             ; preds = %for_loop_inc6.us.us.1, %for_loop_body5.us.us.preheader68
  %lsr.iv69 = phi i64 [ 0, %for_loop_body5.us.us.preheader68 ], [ %lsr.iv.next70, %for_loop_inc6.us.us.1 ]
  %.231.us.us = phi i1 [ %.1.us.us.1, %for_loop_inc6.us.us.1 ], [ %.231.us.us.unr, %for_loop_body5.us.us.preheader68 ]
  %110 = add i64 %indvars.iv.unr, %lsr.iv69
  %tmp77 = trunc i64 %110 to i32
  %111 = or i32 %.01834.us, %tmp77
  %spec.select.us.us = icmp eq i32 %111, 0
  br i1 %spec.select.us.us, label %for_loop_inc6.us.us, label %after_if14.us.us

after_if14.us.us:                                 ; preds = %for_loop_body5.us.us
  %112 = add i64 %104, %lsr.iv69
  %113 = load i32, ptr %60, align 4
  %114 = icmp slt i32 %.fr, %113
  %tmp76 = trunc i64 %112 to i32
  %115 = icmp sgt i32 %tmp76, -1
  %or.cond.us.us = and i1 %115, %114
  br i1 %or.cond.us.us, label %true_block22.us.us, label %for_loop_inc6.us.us

true_block22.us.us:                               ; preds = %after_if14.us.us
  %116 = load i32, ptr %61, align 4
  %117 = icmp slt i32 %tmp76, %116
  br i1 %117, label %true_block25.us.us, label %for_loop_inc6.us.us

true_block25.us.us:                               ; preds = %true_block22.us.us
  %118 = add i64 %107, %lsr.iv69
  %tmp74 = trunc i64 %118 to i32
  %119 = sext i32 %tmp74 to i64
  %120 = getelementptr i32, ptr %52, i64 %119
  %121 = load i32, ptr %120, align 4
  %122 = icmp sle i32 %121, %58
  %spec.select30.us.us = select i1 %122, i1 %.231.us.us, i1 false
  br label %for_loop_inc6.us.us

for_loop_inc6.us.us:                              ; preds = %true_block25.us.us, %true_block22.us.us, %after_if14.us.us, %for_loop_body5.us.us
  %.1.us.us = phi i1 [ %.231.us.us, %for_loop_body5.us.us ], [ %.231.us.us, %true_block22.us.us ], [ %spec.select30.us.us, %true_block25.us.us ], [ %.231.us.us, %after_if14.us.us ]
  %123 = add i64 %110, 1
  %tmp73 = trunc i64 %123 to i32
  %124 = or i32 %.01834.us, %tmp73
  %spec.select.us.us.1 = icmp eq i32 %124, 0
  br i1 %spec.select.us.us.1, label %for_loop_inc6.us.us.1, label %after_if14.us.us.1

after_if14.us.us.1:                               ; preds = %for_loop_inc6.us.us
  %125 = add i64 %104, %lsr.iv69
  %126 = add i64 %125, 1
  %127 = load i32, ptr %60, align 4
  %128 = icmp slt i32 %.fr, %127
  %tmp = trunc i64 %126 to i32
  %129 = icmp sgt i32 %tmp, -1
  %or.cond.us.us.1 = and i1 %129, %128
  br i1 %or.cond.us.us.1, label %true_block22.us.us.1, label %for_loop_inc6.us.us.1

true_block22.us.us.1:                             ; preds = %after_if14.us.us.1
  %130 = load i32, ptr %61, align 4
  %131 = icmp slt i32 %tmp, %130
  br i1 %131, label %true_block25.us.us.1, label %for_loop_inc6.us.us.1

true_block25.us.us.1:                             ; preds = %true_block22.us.us.1
  %132 = add i64 %107, %lsr.iv69
  %133 = add i64 %132, 1
  %tmp72 = trunc i64 %133 to i32
  %134 = sext i32 %tmp72 to i64
  %135 = getelementptr i32, ptr %52, i64 %134
  %136 = load i32, ptr %135, align 4
  %137 = icmp sle i32 %136, %58
  %spec.select30.us.us.1 = select i1 %137, i1 %.1.us.us, i1 false
  br label %for_loop_inc6.us.us.1

for_loop_inc6.us.us.1:                            ; preds = %true_block25.us.us.1, %true_block22.us.us.1, %after_if14.us.us.1, %for_loop_inc6.us.us
  %.1.us.us.1 = phi i1 [ %.1.us.us, %for_loop_inc6.us.us ], [ %.1.us.us, %true_block22.us.us.1 ], [ %spec.select30.us.us.1, %true_block25.us.us.1 ], [ %.1.us.us, %after_if14.us.us.1 ]
  %lsr.iv.next70 = add i64 %lsr.iv69, 2
  %138 = add i64 %108, %lsr.iv.next70
  %exitcond.not.1 = icmp eq i64 %138, 0
  br i1 %exitcond.not.1, label %for_loop_test8.after_for7_crit_edge.us.loopexit, label %for_loop_body5.us.us, !llvm.loop !13

for_loop_inc:                                     ; preds = %true_block34, %true_block31, %after_for3, %for_loop_body
  %139 = add nsw i32 %.02045, 1
  %indvar.next = add i32 %indvar, 1
  %exitcond48.not = icmp eq i32 %139, %18
  br i1 %exitcond48.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3:                                       ; preds = %for_loop_test8.after_for7_crit_edge.us
  br i1 %.us-phi.us, label %true_block31, label %for_loop_inc

true_block31:                                     ; preds = %after_for3, %for_loop_test4.preheader
  %140 = load ptr, ptr %0, align 8
  %141 = getelementptr i8, ptr %140, i64 40
  %142 = load ptr, ptr %141, align 8
  %143 = atomicrmw add ptr %142, i32 1 seq_cst, align 4
  %144 = load ptr, ptr %0, align 8
  %145 = getelementptr i8, ptr %144, i64 64
  %146 = load i32, ptr %145, align 4
  %147 = icmp slt i32 %143, %146
  br i1 %147, label %true_block34, label %for_loop_inc

true_block34:                                     ; preds = %true_block31
  %148 = sitofp i32 %49 to float
  %149 = getelementptr i8, ptr %144, i64 24
  %150 = load ptr, ptr %149, align 8
  %151 = getelementptr i8, ptr %144, i64 20
  %152 = load i32, ptr %151, align 4
  %153 = mul i32 %152, %143
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %150, i64 %154
  store float %148, ptr %155, align 4
  %156 = sitofp i32 %51 to float
  %157 = load ptr, ptr %149, align 8
  %158 = load i32, ptr %151, align 4
  %159 = mul i32 %158, %143
  %160 = add i32 %159, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %157, i64 %161
  store float %156, ptr %162, align 4
  %163 = load i32, ptr %57, align 4
  %164 = sitofp i32 %163 to float
  %165 = load ptr, ptr %149, align 8
  %166 = load i32, ptr %151, align 4
  %167 = mul i32 %166, %143
  %168 = add i32 %167, 2
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, ptr %165, i64 %169
  store float %164, ptr %170, align 4
  br label %for_loop_inc
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #8
  %14 = add i32 %.02040, 1
  %15 = icmp slt i32 %14, %.sroa.speculated28
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !14

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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
  %.not24.not = icmp sgt i32 %.0, %.sroa.speculated
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !16

.loopexit.loopexit:                               ; preds = %.lr.ph41
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %16, %9, %7
  %.not25 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not25, label %21, label %20

20:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
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

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x i32> @llvm.masked.gather.v8i32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x i32>) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: read)
declare <8 x i32> @llvm.masked.load.v8i32.p0(ptr nocapture, i32 immarg, <8 x i1>, <8 x i32>) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(read) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: read) }
attributes #8 = { nounwind }

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
!10 = distinct !{!10, !11, !12}
!11 = !{!"llvm.loop.isvectorized", i32 1}
!12 = !{!"llvm.loop.unroll.runtime.disable"}
!13 = distinct !{!13, !11}
!14 = distinct !{!14, !15}
!15 = !{!"llvm.loop.mustprogress"}
!16 = distinct !{!16, !15}
