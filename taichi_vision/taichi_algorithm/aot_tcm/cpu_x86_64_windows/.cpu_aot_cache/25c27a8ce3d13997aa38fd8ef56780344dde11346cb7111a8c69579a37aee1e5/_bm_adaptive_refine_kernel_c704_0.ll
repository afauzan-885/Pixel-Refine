; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_bm_adaptive_refine_kernel_c704_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 8
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 12
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 32
  %16 = load i32, ptr %15, align 4
  %17 = getelementptr i8, ptr %14, i64 36
  %18 = load i32, ptr %17, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %20 = tail call i32 @llvm.smax.i32(i32 %18, i32 0)
  %21 = load ptr, ptr %2, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 4
  store i32 %20, ptr %24, align 4
  %25 = mul i32 %20, %19
  %26 = load ptr, ptr %2, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  store i32 %25, ptr %28, align 4
  ret void
}

define void @_bm_adaptive_refine_kernel_c704_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 100
  %21 = load i32, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 72
  %24 = getelementptr i8, ptr %19, i64 60
  %25 = getelementptr i8, ptr %19, i64 64
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.065141 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %119, %after_if3 ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.065141, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.065141
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %32, %.065141
  %36 = and i1 %34, %35
  %.neg69 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg69
  %38 = mul i32 %37, %30
  %39 = sub i32 %.065141, %38
  %40 = load ptr, ptr %23, align 8
  %41 = load i32, ptr %24, align 4
  %42 = load i32, ptr %25, align 4
  %43 = mul i32 %37, %41
  %44 = add i32 %39, %43
  %45 = mul i32 %44, %42
  %46 = add i32 %45, 2
  %47 = sext i32 %46 to i64
  %48 = getelementptr float, ptr %40, i64 %47
  %49 = load float, ptr %48, align 4
  %50 = fptosi float %49 to i32
  %.not = icmp sgt i32 %21, %50
  br i1 %.not, label %after_if3, label %true_block

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %51 = load ptr, ptr %0, align 8
  %52 = getelementptr i8, ptr %51, i64 48
  %53 = load ptr, ptr %52, align 8
  %54 = getelementptr i8, ptr %51, i64 36
  %55 = load i32, ptr %54, align 4
  %56 = getelementptr i8, ptr %51, i64 40
  %57 = load i32, ptr %56, align 4
  %58 = mul i32 %55, %37
  %59 = add i32 %58, %39
  %60 = mul i32 %59, %57
  %61 = add i32 %60, 2
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, ptr %53, i64 %62
  %64 = load float, ptr %63, align 4
  %65 = fcmp reassoc ninf nsz ogt float %64, 5.000000e-01
  br i1 %65, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %66 = sext i32 %60 to i64
  %67 = getelementptr float, ptr %53, i64 %66
  %68 = load float, ptr %67, align 4
  %69 = add i32 %60, 1
  %70 = sext i32 %69 to i64
  %71 = getelementptr float, ptr %53, i64 %70
  %72 = load float, ptr %71, align 4
  %73 = tail call reassoc ninf nsz float @llvm.round.f32(float %68)
  %74 = fptosi float %73 to i32
  %75 = tail call reassoc ninf nsz float @llvm.round.f32(float %72)
  %76 = fptosi float %75 to i32
  %77 = getelementptr i8, ptr %51, i64 88
  %78 = load i32, ptr %77, align 4
  %neg = sub i32 0, %78
  %79 = getelementptr i8, ptr %51, i64 84
  %80 = load i32, ptr %79, align 4
  %81 = getelementptr i8, ptr %51, i64 80
  %82 = load i32, ptr %81, align 4
  %83 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %84 = load i32, ptr %83, align 4
  %85 = add i32 %84, -1
  %86 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %87 = load i32, ptr %86, align 4
  %88 = add i32 %87, -1
  %89 = mul i32 %82, %37
  %90 = mul i32 %82, %39
  %91 = add i32 %89, %80
  %92 = add i32 %90, %80
  %invariant.op83 = add i32 %91, %76
  %.not7085 = icmp slt i32 %78, %neg
  br i1 %.not7085, label %false_block52, label %while_loop_body7.preheader.lr.ph

while_loop_body7.preheader.lr.ph:                 ; preds = %true_block1
  %invariant.op = add i32 %92, %74
  %93 = getelementptr i8, ptr %51, i64 24
  %94 = getelementptr i8, ptr %51, i64 20
  %95 = getelementptr i8, ptr %51, i64 8
  %96 = getelementptr i8, ptr %51, i64 4
  %97 = load ptr, ptr %93, align 8
  %98 = load i32, ptr %94, align 4
  %99 = load ptr, ptr %95, align 8
  %100 = load i32, ptr %96, align 4
  %101 = sext i32 %78 to i64
  %102 = add nsw i64 %101, 1
  %103 = sub i32 2, %78
  %104 = sext i32 %103 to i64
  %smax293 = tail call i64 @llvm.smax.i64(i64 %102, i64 %104)
  %105 = add i64 %smax293, 1
  %106 = sub i64 %105, %104
  %107 = lshr i64 %106, 1
  %108 = trunc i64 %107 to i32
  %109 = add i32 %108, 1
  %min.iters.check300 = icmp ult i32 %109, 8
  %mul.result295 = shl i32 %108, 1
  %mul.overflow296 = icmp slt i32 %108, 0
  %110 = add i32 %103, %mul.result295
  %111 = icmp slt i32 %110, %103
  %112 = or i1 %111, %mul.overflow296
  %113 = icmp ugt i64 %106, 8589934591
  %114 = or i1 %112, %113
  %n.vec303 = and i32 %109, -8
  %115 = shl i32 %n.vec303, 1
  %116 = sub i32 %115, %78
  %.splatinsert306 = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat307 = shufflevector <8 x i32> %.splatinsert306, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction308 = add <8 x i32> %.splat307, <i32 0, i32 2, i32 4, i32 6, i32 8, i32 10, i32 12, i32 14>
  %broadcast.splatinsert312 = insertelement <8 x i32> poison, i32 %92, i64 0
  %broadcast.splat313 = shufflevector <8 x i32> %broadcast.splatinsert312, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert314 = insertelement <8 x i32> poison, i32 %invariant.op, i64 0
  %broadcast.splat315 = shufflevector <8 x i32> %broadcast.splatinsert314, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert316 = insertelement <8 x i32> poison, i32 %88, i64 0
  %broadcast.splat317 = shufflevector <8 x i32> %broadcast.splatinsert316, <8 x i32> poison, <8 x i32> zeroinitializer
  %cmp.n325 = icmp eq i32 %109, %n.vec303
  %117 = add i32 %74, %80
  %118 = add i32 %117, %90
  br label %while_loop_body7.preheader

after_if3:                                        ; preds = %after_if66, %true_block, %for_loop_body
  %119 = add nsw i32 %.065141, 1
  %exitcond.not = icmp eq i32 %119, %18
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

while_loop_body19.preheader.lr.ph:                ; preds = %while_loop_body7.false_block10_crit_edge
  %120 = add i32 %74, -1
  %invariant.op93 = add i32 %92, %120
  %broadcast.splatinsert278 = insertelement <8 x i32> poison, i32 %invariant.op93, i64 0
  %broadcast.splat279 = shufflevector <8 x i32> %broadcast.splatinsert278, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body19.preheader

while_loop_body7.preheader:                       ; preds = %while_loop_body7.false_block10_crit_edge, %while_loop_body7.preheader.lr.ph
  %.05387 = phi i32 [ %neg, %while_loop_body7.preheader.lr.ph ], [ %146, %while_loop_body7.false_block10_crit_edge ]
  %.06286 = phi float [ 0.000000e+00, %while_loop_body7.preheader.lr.ph ], [ %.lcssa, %while_loop_body7.false_block10_crit_edge ]
  %121 = add i32 %.05387, %91
  %.reass84 = add i32 %.05387, %invariant.op83
  %122 = tail call i32 @llvm.smin.i32(i32 %.reass84, i32 %85)
  %123 = tail call i32 @llvm.smax.i32(i32 %122, i32 0)
  %124 = tail call i32 @llvm.smin.i32(i32 %121, i32 %85)
  %125 = tail call i32 @llvm.smax.i32(i32 %124, i32 0)
  %126 = mul i32 %98, %123
  %127 = mul i32 %100, %125
  %brmerge = select i1 %min.iters.check300, i1 true, i1 %114
  br i1 %brmerge, label %after_if11.preheader, label %vector.ph301

vector.ph301:                                     ; preds = %while_loop_body7.preheader
  %128 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06286, i64 0
  %broadcast.splatinsert318 = insertelement <8 x i32> poison, i32 %126, i64 0
  %broadcast.splat319 = shufflevector <8 x i32> %broadcast.splatinsert318, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert321 = insertelement <8 x i32> poison, i32 %127, i64 0
  %broadcast.splat322 = shufflevector <8 x i32> %broadcast.splatinsert321, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body304

vector.body304:                                   ; preds = %vector.body304, %vector.ph301
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body304 ], [ %n.vec303, %vector.ph301 ]
  %vec.ind309 = phi <8 x i32> [ %induction308, %vector.ph301 ], [ %vec.ind.next310, %vector.body304 ]
  %vec.phi311 = phi <8 x float> [ %128, %vector.ph301 ], [ %143, %vector.body304 ]
  %129 = add <8 x i32> %vec.ind309, %broadcast.splat313
  %130 = add <8 x i32> %vec.ind309, %broadcast.splat315
  %131 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %130, <8 x i32> %broadcast.splat317)
  %132 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %131, <8 x i32> zeroinitializer)
  %133 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %129, <8 x i32> %broadcast.splat317)
  %134 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %133, <8 x i32> zeroinitializer)
  %135 = add <8 x i32> %broadcast.splat319, %132
  %136 = sext <8 x i32> %135 to <8 x i64>
  %137 = getelementptr float, ptr %97, <8 x i64> %136
  %wide.masked.gather320 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %137, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %138 = add <8 x i32> %broadcast.splat322, %134
  %139 = sext <8 x i32> %138 to <8 x i64>
  %140 = getelementptr float, ptr %99, <8 x i64> %139
  %wide.masked.gather323 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %140, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %141 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather320, %wide.masked.gather323
  %142 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %141)
  %143 = fadd reassoc ninf nsz <8 x float> %142, %vec.phi311
  %vec.ind.next310 = add <8 x i32> %vec.ind309, splat (i32 16)
  %lsr.iv.next = add i32 %lsr.iv, -8
  %144 = icmp eq i32 %lsr.iv.next, 0
  br i1 %144, label %middle.block298, label %vector.body304, !llvm.loop !10

middle.block298:                                  ; preds = %vector.body304
  %145 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %143)
  br i1 %cmp.n325, label %while_loop_body7.false_block10_crit_edge, label %after_if11.preheader

after_if11.preheader:                             ; preds = %middle.block298, %while_loop_body7.preheader
  %.05282.ph = phi i32 [ %neg, %while_loop_body7.preheader ], [ %116, %middle.block298 ]
  %.16381.ph = phi float [ %.06286, %while_loop_body7.preheader ], [ %145, %middle.block298 ]
  br label %after_if11

while_loop_body7.false_block10_crit_edge.loopexit: ; preds = %after_if11
  br label %while_loop_body7.false_block10_crit_edge

while_loop_body7.false_block10_crit_edge:         ; preds = %while_loop_body7.false_block10_crit_edge.loopexit, %middle.block298
  %.lcssa = phi float [ %145, %middle.block298 ], [ %163, %while_loop_body7.false_block10_crit_edge.loopexit ]
  %146 = add i32 %.05387, 2
  %.not70 = icmp sgt i32 %146, %78
  br i1 %.not70, label %while_loop_body19.preheader.lr.ph, label %while_loop_body7.preheader

after_if11:                                       ; preds = %after_if11, %after_if11.preheader
  %.05282 = phi i32 [ %164, %after_if11 ], [ %.05282.ph, %after_if11.preheader ]
  %.16381 = phi float [ %163, %after_if11 ], [ %.16381.ph, %after_if11.preheader ]
  %147 = add i32 %92, %.05282
  %148 = add i32 %118, %.05282
  %149 = tail call i32 @llvm.smin.i32(i32 %148, i32 %88)
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %151 = tail call i32 @llvm.smin.i32(i32 %147, i32 %88)
  %152 = tail call i32 @llvm.smax.i32(i32 %151, i32 0)
  %153 = add i32 %126, %150
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, ptr %97, i64 %154
  %156 = load float, ptr %155, align 4
  %157 = add i32 %127, %152
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, ptr %99, i64 %158
  %160 = load float, ptr %159, align 4
  %161 = fsub reassoc ninf nsz float %156, %160
  %162 = tail call noundef float @llvm.fabs.f32(float %161)
  %163 = fadd reassoc ninf nsz float %162, %.16381
  %164 = add i32 %.05282, 2
  %.not79 = icmp sgt i32 %164, %78
  br i1 %.not79, label %while_loop_body7.false_block10_crit_edge.loopexit, label %after_if11, !llvm.loop !13

while_loop_body31.preheader.lr.ph:                ; preds = %while_loop_body19.false_block22_crit_edge
  %165 = add i32 %74, 1
  %invariant.op106 = add i32 %92, %165
  %broadcast.splatinsert242 = insertelement <8 x i32> poison, i32 %invariant.op106, i64 0
  %broadcast.splat243 = shufflevector <8 x i32> %broadcast.splatinsert242, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %while_loop_body31.preheader

while_loop_body19.preheader:                      ; preds = %while_loop_body19.false_block22_crit_edge, %while_loop_body19.preheader.lr.ph
  %.199 = phi i32 [ %neg, %while_loop_body19.preheader.lr.ph ], [ %192, %while_loop_body19.false_block22_crit_edge ]
  %.06098 = phi float [ 0.000000e+00, %while_loop_body19.preheader.lr.ph ], [ %.lcssa170, %while_loop_body19.false_block22_crit_edge ]
  %166 = add i32 %.199, %91
  %.reass96 = add i32 %.199, %invariant.op83
  %167 = tail call i32 @llvm.smin.i32(i32 %.reass96, i32 %85)
  %168 = tail call i32 @llvm.smax.i32(i32 %167, i32 0)
  %169 = tail call i32 @llvm.smin.i32(i32 %166, i32 %85)
  %170 = tail call i32 @llvm.smax.i32(i32 %169, i32 0)
  %171 = mul i32 %98, %168
  %172 = mul i32 %100, %170
  br i1 %brmerge, label %after_if23.preheader, label %vector.ph265

vector.ph265:                                     ; preds = %while_loop_body19.preheader
  %173 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.06098, i64 0
  %broadcast.splatinsert282 = insertelement <8 x i32> poison, i32 %171, i64 0
  %broadcast.splat283 = shufflevector <8 x i32> %broadcast.splatinsert282, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert285 = insertelement <8 x i32> poison, i32 %172, i64 0
  %broadcast.splat286 = shufflevector <8 x i32> %broadcast.splatinsert285, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body268

vector.body268:                                   ; preds = %vector.body268, %vector.ph265
  %lsr.iv352 = phi i32 [ %lsr.iv.next353, %vector.body268 ], [ %n.vec303, %vector.ph265 ]
  %vec.ind273 = phi <8 x i32> [ %induction308, %vector.ph265 ], [ %vec.ind.next274, %vector.body268 ]
  %vec.phi275 = phi <8 x float> [ %173, %vector.ph265 ], [ %188, %vector.body268 ]
  %174 = add <8 x i32> %vec.ind273, %broadcast.splat313
  %175 = add <8 x i32> %vec.ind273, %broadcast.splat279
  %176 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %175, <8 x i32> %broadcast.splat317)
  %177 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %176, <8 x i32> zeroinitializer)
  %178 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %174, <8 x i32> %broadcast.splat317)
  %179 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %178, <8 x i32> zeroinitializer)
  %180 = add <8 x i32> %broadcast.splat283, %177
  %181 = sext <8 x i32> %180 to <8 x i64>
  %182 = getelementptr float, ptr %97, <8 x i64> %181
  %wide.masked.gather284 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %182, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %183 = add <8 x i32> %broadcast.splat286, %179
  %184 = sext <8 x i32> %183 to <8 x i64>
  %185 = getelementptr float, ptr %99, <8 x i64> %184
  %wide.masked.gather287 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %185, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %186 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather284, %wide.masked.gather287
  %187 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %186)
  %188 = fadd reassoc ninf nsz <8 x float> %187, %vec.phi275
  %vec.ind.next274 = add <8 x i32> %vec.ind273, splat (i32 16)
  %lsr.iv.next353 = add i32 %lsr.iv352, -8
  %189 = icmp eq i32 %lsr.iv.next353, 0
  br i1 %189, label %middle.block262, label %vector.body268, !llvm.loop !14

middle.block262:                                  ; preds = %vector.body268
  %190 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %188)
  br i1 %cmp.n325, label %while_loop_body19.false_block22_crit_edge, label %after_if23.preheader

after_if23.preheader:                             ; preds = %middle.block262, %while_loop_body19.preheader
  %.05191.ph = phi i32 [ %neg, %while_loop_body19.preheader ], [ %116, %middle.block262 ]
  %.16190.ph = phi float [ %.06098, %while_loop_body19.preheader ], [ %190, %middle.block262 ]
  %191 = add i32 %92, %.05191.ph
  br label %after_if23

while_loop_body19.false_block22_crit_edge.loopexit: ; preds = %after_if23
  br label %while_loop_body19.false_block22_crit_edge

while_loop_body19.false_block22_crit_edge:        ; preds = %while_loop_body19.false_block22_crit_edge.loopexit, %middle.block262
  %.lcssa170 = phi float [ %190, %middle.block262 ], [ %208, %while_loop_body19.false_block22_crit_edge.loopexit ]
  %192 = add i32 %.199, 2
  %.not71 = icmp sgt i32 %192, %78
  br i1 %.not71, label %while_loop_body31.preheader.lr.ph, label %while_loop_body19.preheader

after_if23:                                       ; preds = %after_if23, %after_if23.preheader
  %lsr.iv354 = phi i32 [ %191, %after_if23.preheader ], [ %lsr.iv.next355, %after_if23 ]
  %.05191 = phi i32 [ %209, %after_if23 ], [ %.05191.ph, %after_if23.preheader ]
  %.16190 = phi float [ %208, %after_if23 ], [ %.16190.ph, %after_if23.preheader ]
  %193 = add i32 %120, %lsr.iv354
  %194 = tail call i32 @llvm.smin.i32(i32 %193, i32 %88)
  %195 = tail call i32 @llvm.smax.i32(i32 %194, i32 0)
  %196 = tail call i32 @llvm.smin.i32(i32 %lsr.iv354, i32 %88)
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = add i32 %171, %195
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, ptr %97, i64 %199
  %201 = load float, ptr %200, align 4
  %202 = add i32 %172, %197
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %99, i64 %203
  %205 = load float, ptr %204, align 4
  %206 = fsub reassoc ninf nsz float %201, %205
  %207 = tail call noundef float @llvm.fabs.f32(float %206)
  %208 = fadd reassoc ninf nsz float %207, %.16190
  %209 = add i32 %.05191, 2
  %lsr.iv.next355 = add i32 %lsr.iv354, 2
  %.not78 = icmp sgt i32 %209, %78
  br i1 %.not78, label %while_loop_body19.false_block22_crit_edge.loopexit, label %after_if23, !llvm.loop !15

while_loop_body43.preheader.lr.ph:                ; preds = %while_loop_body31.false_block34_crit_edge
  %210 = add i32 %76, -1
  %invariant.op125 = add i32 %91, %210
  br label %while_loop_body43.preheader

while_loop_body31.preheader:                      ; preds = %while_loop_body31.false_block34_crit_edge, %while_loop_body31.preheader.lr.ph
  %.2112 = phi i32 [ %neg, %while_loop_body31.preheader.lr.ph ], [ %237, %while_loop_body31.false_block34_crit_edge ]
  %.058111 = phi float [ 0.000000e+00, %while_loop_body31.preheader.lr.ph ], [ %.lcssa171, %while_loop_body31.false_block34_crit_edge ]
  %211 = add i32 %.2112, %91
  %.reass109 = add i32 %.2112, %invariant.op83
  %212 = tail call i32 @llvm.smin.i32(i32 %.reass109, i32 %85)
  %213 = tail call i32 @llvm.smax.i32(i32 %212, i32 0)
  %214 = tail call i32 @llvm.smin.i32(i32 %211, i32 %85)
  %215 = tail call i32 @llvm.smax.i32(i32 %214, i32 0)
  %216 = mul i32 %98, %213
  %217 = mul i32 %100, %215
  br i1 %brmerge, label %after_if35.preheader, label %vector.ph229

vector.ph229:                                     ; preds = %while_loop_body31.preheader
  %218 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.058111, i64 0
  %broadcast.splatinsert246 = insertelement <8 x i32> poison, i32 %216, i64 0
  %broadcast.splat247 = shufflevector <8 x i32> %broadcast.splatinsert246, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert249 = insertelement <8 x i32> poison, i32 %217, i64 0
  %broadcast.splat250 = shufflevector <8 x i32> %broadcast.splatinsert249, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body232

vector.body232:                                   ; preds = %vector.body232, %vector.ph229
  %lsr.iv356 = phi i32 [ %lsr.iv.next357, %vector.body232 ], [ %n.vec303, %vector.ph229 ]
  %vec.ind237 = phi <8 x i32> [ %induction308, %vector.ph229 ], [ %vec.ind.next238, %vector.body232 ]
  %vec.phi239 = phi <8 x float> [ %218, %vector.ph229 ], [ %233, %vector.body232 ]
  %219 = add <8 x i32> %vec.ind237, %broadcast.splat313
  %220 = add <8 x i32> %vec.ind237, %broadcast.splat243
  %221 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %220, <8 x i32> %broadcast.splat317)
  %222 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %221, <8 x i32> zeroinitializer)
  %223 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %219, <8 x i32> %broadcast.splat317)
  %224 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %223, <8 x i32> zeroinitializer)
  %225 = add <8 x i32> %broadcast.splat247, %222
  %226 = sext <8 x i32> %225 to <8 x i64>
  %227 = getelementptr float, ptr %97, <8 x i64> %226
  %wide.masked.gather248 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %227, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %228 = add <8 x i32> %broadcast.splat250, %224
  %229 = sext <8 x i32> %228 to <8 x i64>
  %230 = getelementptr float, ptr %99, <8 x i64> %229
  %wide.masked.gather251 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %230, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %231 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather248, %wide.masked.gather251
  %232 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %231)
  %233 = fadd reassoc ninf nsz <8 x float> %232, %vec.phi239
  %vec.ind.next238 = add <8 x i32> %vec.ind237, splat (i32 16)
  %lsr.iv.next357 = add i32 %lsr.iv356, -8
  %234 = icmp eq i32 %lsr.iv.next357, 0
  br i1 %234, label %middle.block226, label %vector.body232, !llvm.loop !16

middle.block226:                                  ; preds = %vector.body232
  %235 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %233)
  br i1 %cmp.n325, label %while_loop_body31.false_block34_crit_edge, label %after_if35.preheader

after_if35.preheader:                             ; preds = %middle.block226, %while_loop_body31.preheader
  %.050104.ph = phi i32 [ %neg, %while_loop_body31.preheader ], [ %116, %middle.block226 ]
  %.159103.ph = phi float [ %.058111, %while_loop_body31.preheader ], [ %235, %middle.block226 ]
  %236 = add i32 %92, %.050104.ph
  br label %after_if35

while_loop_body31.false_block34_crit_edge.loopexit: ; preds = %after_if35
  br label %while_loop_body31.false_block34_crit_edge

while_loop_body31.false_block34_crit_edge:        ; preds = %while_loop_body31.false_block34_crit_edge.loopexit, %middle.block226
  %.lcssa171 = phi float [ %235, %middle.block226 ], [ %253, %while_loop_body31.false_block34_crit_edge.loopexit ]
  %237 = add i32 %.2112, 2
  %.not72 = icmp sgt i32 %237, %78
  br i1 %.not72, label %while_loop_body43.preheader.lr.ph, label %while_loop_body31.preheader

after_if35:                                       ; preds = %after_if35, %after_if35.preheader
  %lsr.iv358 = phi i32 [ %236, %after_if35.preheader ], [ %lsr.iv.next359, %after_if35 ]
  %.050104 = phi i32 [ %254, %after_if35 ], [ %.050104.ph, %after_if35.preheader ]
  %.159103 = phi float [ %253, %after_if35 ], [ %.159103.ph, %after_if35.preheader ]
  %238 = add i32 %165, %lsr.iv358
  %239 = tail call i32 @llvm.smin.i32(i32 %238, i32 %88)
  %240 = tail call i32 @llvm.smax.i32(i32 %239, i32 0)
  %241 = tail call i32 @llvm.smin.i32(i32 %lsr.iv358, i32 %88)
  %242 = tail call i32 @llvm.smax.i32(i32 %241, i32 0)
  %243 = add i32 %216, %240
  %244 = sext i32 %243 to i64
  %245 = getelementptr float, ptr %97, i64 %244
  %246 = load float, ptr %245, align 4
  %247 = add i32 %217, %242
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, ptr %99, i64 %248
  %250 = load float, ptr %249, align 4
  %251 = fsub reassoc ninf nsz float %246, %250
  %252 = tail call noundef float @llvm.fabs.f32(float %251)
  %253 = fadd reassoc ninf nsz float %252, %.159103
  %254 = add i32 %.050104, 2
  %lsr.iv.next359 = add i32 %lsr.iv358, 2
  %.not77 = icmp sgt i32 %254, %78
  br i1 %.not77, label %while_loop_body31.false_block34_crit_edge.loopexit, label %after_if35, !llvm.loop !17

while_loop_body55.preheader.lr.ph:                ; preds = %while_loop_body43.false_block46_crit_edge
  %255 = add i32 %76, 1
  %invariant.op138 = add i32 %91, %255
  br label %while_loop_body55.preheader

while_loop_body43.preheader:                      ; preds = %while_loop_body43.false_block46_crit_edge, %while_loop_body43.preheader.lr.ph
  %.3123 = phi i32 [ %neg, %while_loop_body43.preheader.lr.ph ], [ %281, %while_loop_body43.false_block46_crit_edge ]
  %.056122 = phi float [ 0.000000e+00, %while_loop_body43.preheader.lr.ph ], [ %.lcssa172, %while_loop_body43.false_block46_crit_edge ]
  %256 = add i32 %.3123, %91
  %.reass126 = add i32 %.3123, %invariant.op125
  %257 = tail call i32 @llvm.smin.i32(i32 %.reass126, i32 %85)
  %258 = tail call i32 @llvm.smax.i32(i32 %257, i32 0)
  %259 = tail call i32 @llvm.smin.i32(i32 %256, i32 %85)
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = mul i32 %98, %258
  %262 = mul i32 %100, %260
  br i1 %brmerge, label %after_if47.preheader, label %vector.ph193

vector.ph193:                                     ; preds = %while_loop_body43.preheader
  %263 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.056122, i64 0
  %broadcast.splatinsert210 = insertelement <8 x i32> poison, i32 %261, i64 0
  %broadcast.splat211 = shufflevector <8 x i32> %broadcast.splatinsert210, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert213 = insertelement <8 x i32> poison, i32 %262, i64 0
  %broadcast.splat214 = shufflevector <8 x i32> %broadcast.splatinsert213, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body196

vector.body196:                                   ; preds = %vector.body196, %vector.ph193
  %lsr.iv360 = phi i32 [ %lsr.iv.next361, %vector.body196 ], [ %n.vec303, %vector.ph193 ]
  %vec.ind201 = phi <8 x i32> [ %induction308, %vector.ph193 ], [ %vec.ind.next202, %vector.body196 ]
  %vec.phi203 = phi <8 x float> [ %263, %vector.ph193 ], [ %278, %vector.body196 ]
  %264 = add <8 x i32> %vec.ind201, %broadcast.splat313
  %265 = add <8 x i32> %vec.ind201, %broadcast.splat315
  %266 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %265, <8 x i32> %broadcast.splat317)
  %267 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %266, <8 x i32> zeroinitializer)
  %268 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %264, <8 x i32> %broadcast.splat317)
  %269 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %268, <8 x i32> zeroinitializer)
  %270 = add <8 x i32> %broadcast.splat211, %267
  %271 = sext <8 x i32> %270 to <8 x i64>
  %272 = getelementptr float, ptr %97, <8 x i64> %271
  %wide.masked.gather212 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %272, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %273 = add <8 x i32> %broadcast.splat214, %269
  %274 = sext <8 x i32> %273 to <8 x i64>
  %275 = getelementptr float, ptr %99, <8 x i64> %274
  %wide.masked.gather215 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %275, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %276 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather212, %wide.masked.gather215
  %277 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %276)
  %278 = fadd reassoc ninf nsz <8 x float> %277, %vec.phi203
  %vec.ind.next202 = add <8 x i32> %vec.ind201, splat (i32 16)
  %lsr.iv.next361 = add i32 %lsr.iv360, -8
  %279 = icmp eq i32 %lsr.iv.next361, 0
  br i1 %279, label %middle.block190, label %vector.body196, !llvm.loop !18

middle.block190:                                  ; preds = %vector.body196
  %280 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %278)
  br i1 %cmp.n325, label %while_loop_body43.false_block46_crit_edge, label %after_if47.preheader

after_if47.preheader:                             ; preds = %middle.block190, %while_loop_body43.preheader
  %.049119.ph = phi i32 [ %neg, %while_loop_body43.preheader ], [ %116, %middle.block190 ]
  %.157118.ph = phi float [ %.056122, %while_loop_body43.preheader ], [ %280, %middle.block190 ]
  br label %after_if47

while_loop_body43.false_block46_crit_edge.loopexit: ; preds = %after_if47
  br label %while_loop_body43.false_block46_crit_edge

while_loop_body43.false_block46_crit_edge:        ; preds = %while_loop_body43.false_block46_crit_edge.loopexit, %middle.block190
  %.lcssa172 = phi float [ %280, %middle.block190 ], [ %298, %while_loop_body43.false_block46_crit_edge.loopexit ]
  %281 = add i32 %.3123, 2
  %.not73 = icmp sgt i32 %281, %78
  br i1 %.not73, label %while_loop_body55.preheader.lr.ph, label %while_loop_body43.preheader

after_if47:                                       ; preds = %after_if47, %after_if47.preheader
  %.049119 = phi i32 [ %299, %after_if47 ], [ %.049119.ph, %after_if47.preheader ]
  %.157118 = phi float [ %298, %after_if47 ], [ %.157118.ph, %after_if47.preheader ]
  %282 = add i32 %92, %.049119
  %283 = add i32 %118, %.049119
  %284 = tail call i32 @llvm.smin.i32(i32 %283, i32 %88)
  %285 = tail call i32 @llvm.smax.i32(i32 %284, i32 0)
  %286 = tail call i32 @llvm.smin.i32(i32 %282, i32 %88)
  %287 = tail call i32 @llvm.smax.i32(i32 %286, i32 0)
  %288 = add i32 %261, %285
  %289 = sext i32 %288 to i64
  %290 = getelementptr float, ptr %97, i64 %289
  %291 = load float, ptr %290, align 4
  %292 = add i32 %262, %287
  %293 = sext i32 %292 to i64
  %294 = getelementptr float, ptr %99, i64 %293
  %295 = load float, ptr %294, align 4
  %296 = fsub reassoc ninf nsz float %291, %295
  %297 = tail call noundef float @llvm.fabs.f32(float %296)
  %298 = fadd reassoc ninf nsz float %297, %.157118
  %299 = add i32 %.049119, 2
  %.not76 = icmp sgt i32 %299, %78
  br i1 %.not76, label %while_loop_body43.false_block46_crit_edge.loopexit, label %after_if47, !llvm.loop !19

while_loop_body55.preheader:                      ; preds = %while_loop_body55.false_block58_crit_edge, %while_loop_body55.preheader.lr.ph
  %.4136 = phi i32 [ %neg, %while_loop_body55.preheader.lr.ph ], [ %329, %while_loop_body55.false_block58_crit_edge ]
  %.054135 = phi float [ 0.000000e+00, %while_loop_body55.preheader.lr.ph ], [ %.lcssa173, %while_loop_body55.false_block58_crit_edge ]
  %300 = add i32 %.4136, %91
  %.reass139 = add i32 %.4136, %invariant.op138
  %301 = tail call i32 @llvm.smin.i32(i32 %.reass139, i32 %85)
  %302 = tail call i32 @llvm.smax.i32(i32 %301, i32 0)
  %303 = tail call i32 @llvm.smin.i32(i32 %300, i32 %85)
  %304 = tail call i32 @llvm.smax.i32(i32 %303, i32 0)
  %305 = mul i32 %98, %302
  %306 = mul i32 %100, %304
  br i1 %brmerge, label %after_if59.preheader, label %vector.ph

vector.ph:                                        ; preds = %while_loop_body55.preheader
  %307 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.054135, i64 0
  %broadcast.splatinsert179 = insertelement <8 x i32> poison, i32 %305, i64 0
  %broadcast.splat180 = shufflevector <8 x i32> %broadcast.splatinsert179, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert181 = insertelement <8 x i32> poison, i32 %306, i64 0
  %broadcast.splat182 = shufflevector <8 x i32> %broadcast.splatinsert181, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv362 = phi i32 [ %lsr.iv.next363, %vector.body ], [ %n.vec303, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction308, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ %307, %vector.ph ], [ %322, %vector.body ]
  %308 = add <8 x i32> %vec.ind, %broadcast.splat313
  %309 = add <8 x i32> %vec.ind, %broadcast.splat315
  %310 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %309, <8 x i32> %broadcast.splat317)
  %311 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %310, <8 x i32> zeroinitializer)
  %312 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %308, <8 x i32> %broadcast.splat317)
  %313 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %312, <8 x i32> zeroinitializer)
  %314 = add <8 x i32> %broadcast.splat180, %311
  %315 = sext <8 x i32> %314 to <8 x i64>
  %316 = getelementptr float, ptr %97, <8 x i64> %315
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %316, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %317 = add <8 x i32> %broadcast.splat182, %313
  %318 = sext <8 x i32> %317 to <8 x i64>
  %319 = getelementptr float, ptr %99, <8 x i64> %318
  %wide.masked.gather183 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %319, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %320 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather183
  %321 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %320)
  %322 = fadd reassoc ninf nsz <8 x float> %321, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 16)
  %lsr.iv.next363 = add i32 %lsr.iv362, -8
  %323 = icmp eq i32 %lsr.iv.next363, 0
  br i1 %323, label %middle.block, label %vector.body, !llvm.loop !20

middle.block:                                     ; preds = %vector.body
  %324 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %322)
  br i1 %cmp.n325, label %while_loop_body55.false_block58_crit_edge, label %after_if59.preheader

after_if59.preheader:                             ; preds = %middle.block, %while_loop_body55.preheader
  %.048132.ph = phi i32 [ %neg, %while_loop_body55.preheader ], [ %116, %middle.block ]
  %.155131.ph = phi float [ %.054135, %while_loop_body55.preheader ], [ %324, %middle.block ]
  br label %after_if59

false_block52.loopexit:                           ; preds = %while_loop_body55.false_block58_crit_edge
  br label %false_block52

false_block52:                                    ; preds = %false_block52.loopexit, %true_block1
  %.056.lcssa165 = phi float [ 0.000000e+00, %true_block1 ], [ %.lcssa172, %false_block52.loopexit ]
  %.060.lcssa151155164 = phi float [ 0.000000e+00, %true_block1 ], [ %.lcssa170, %false_block52.loopexit ]
  %.062.lcssa147150156163 = phi float [ 0.000000e+00, %true_block1 ], [ %.lcssa, %false_block52.loopexit ]
  %.058.lcssa157162 = phi float [ 0.000000e+00, %true_block1 ], [ %.lcssa171, %false_block52.loopexit ]
  %.054.lcssa = phi float [ 0.000000e+00, %true_block1 ], [ %.lcssa173, %false_block52.loopexit ]
  %factor = fmul reassoc ninf nsz float %.062.lcssa147150156163, 2.000000e+00
  %325 = fsub reassoc ninf nsz float %.058.lcssa157162, %factor
  %326 = fadd reassoc ninf nsz float %325, %.060.lcssa151155164
  %327 = tail call noundef float @llvm.fabs.f32(float %326)
  %328 = fcmp reassoc ninf nsz ogt float %327, 0x3F1A36E2E0000000
  br i1 %328, label %true_block61, label %after_if63

while_loop_body55.false_block58_crit_edge.loopexit: ; preds = %after_if59
  br label %while_loop_body55.false_block58_crit_edge

while_loop_body55.false_block58_crit_edge:        ; preds = %while_loop_body55.false_block58_crit_edge.loopexit, %middle.block
  %.lcssa173 = phi float [ %324, %middle.block ], [ %346, %while_loop_body55.false_block58_crit_edge.loopexit ]
  %329 = add i32 %.4136, 2
  %.not74 = icmp sgt i32 %329, %78
  br i1 %.not74, label %false_block52.loopexit, label %while_loop_body55.preheader

after_if59:                                       ; preds = %after_if59, %after_if59.preheader
  %.048132 = phi i32 [ %347, %after_if59 ], [ %.048132.ph, %after_if59.preheader ]
  %.155131 = phi float [ %346, %after_if59 ], [ %.155131.ph, %after_if59.preheader ]
  %330 = add i32 %92, %.048132
  %331 = add i32 %118, %.048132
  %332 = tail call i32 @llvm.smin.i32(i32 %331, i32 %88)
  %333 = tail call i32 @llvm.smax.i32(i32 %332, i32 0)
  %334 = tail call i32 @llvm.smin.i32(i32 %330, i32 %88)
  %335 = tail call i32 @llvm.smax.i32(i32 %334, i32 0)
  %336 = add i32 %305, %333
  %337 = sext i32 %336 to i64
  %338 = getelementptr float, ptr %97, i64 %337
  %339 = load float, ptr %338, align 4
  %340 = add i32 %306, %335
  %341 = sext i32 %340 to i64
  %342 = getelementptr float, ptr %99, i64 %341
  %343 = load float, ptr %342, align 4
  %344 = fsub reassoc ninf nsz float %339, %343
  %345 = tail call noundef float @llvm.fabs.f32(float %344)
  %346 = fadd reassoc ninf nsz float %345, %.155131
  %347 = add i32 %.048132, 2
  %.not75 = icmp sgt i32 %347, %78
  br i1 %.not75, label %while_loop_body55.false_block58_crit_edge.loopexit, label %after_if59, !llvm.loop !21

true_block61:                                     ; preds = %false_block52
  %348 = fsub reassoc ninf nsz float %.058.lcssa157162, %.060.lcssa151155164
  %349 = fmul reassoc ninf nsz float %348, -5.000000e-01
  %350 = fdiv reassoc ninf nsz float %349, %326
  %351 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %350, float 5.000000e-01)
  %352 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %351, float -5.000000e-01)
  br label %after_if63

after_if63:                                       ; preds = %true_block61, %false_block52
  %.047 = phi float [ %352, %true_block61 ], [ 0.000000e+00, %false_block52 ]
  %353 = fsub reassoc ninf nsz float %.054.lcssa, %factor
  %354 = fadd reassoc ninf nsz float %353, %.056.lcssa165
  %355 = tail call noundef float @llvm.fabs.f32(float %354)
  %356 = fcmp reassoc ninf nsz ogt float %355, 0x3F1A36E2E0000000
  br i1 %356, label %true_block64, label %after_if66

true_block64:                                     ; preds = %after_if63
  %357 = fsub reassoc ninf nsz float %.054.lcssa, %.056.lcssa165
  %358 = fmul reassoc ninf nsz float %357, -5.000000e-01
  %359 = fdiv reassoc ninf nsz float %358, %354
  %360 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %359, float 5.000000e-01)
  %361 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %360, float -5.000000e-01)
  br label %after_if66

after_if66:                                       ; preds = %true_block64, %after_if63
  %.0 = phi float [ %361, %true_block64 ], [ 0.000000e+00, %after_if63 ]
  %362 = sitofp i32 %74 to float
  %363 = fadd reassoc ninf nsz float %.047, %362
  %364 = sitofp i32 %76 to float
  %365 = fadd reassoc ninf nsz float %.0, %364
  %366 = shl i32 %78, 1
  %367 = add i32 %82, %78
  %368 = shl i32 %367, 1
  %369 = sitofp i32 %368 to float
  %neg67 = fneg reassoc ninf nsz float %369
  %370 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %369, float %363)
  %371 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg67, float %370)
  %372 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %369, float %365)
  %373 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg67, float %372)
  %374 = ashr exact i32 %366, 1
  %375 = add nsw i32 %374, 1
  %376 = mul i32 %375, %375
  %377 = sitofp i32 %376 to float
  %378 = fdiv reassoc ninf nsz float %.062.lcssa147150156163, %377
  store float %371, ptr %67, align 4
  store float %373, ptr %71, align 4
  %379 = load ptr, ptr %23, align 8
  %380 = load i32, ptr %24, align 4
  %381 = load i32, ptr %25, align 4
  %382 = mul i32 %380, %37
  %383 = add i32 %382, %39
  %384 = mul i32 %383, %381
  %385 = sext i32 %384 to i64
  %386 = getelementptr float, ptr %379, i64 %385
  store float %378, ptr %386, align 4
  %387 = fmul reassoc ninf nsz float %371, %371
  %388 = fmul reassoc ninf nsz float %373, %373
  %389 = fadd reassoc ninf nsz float %388, %387
  %390 = load ptr, ptr %23, align 8
  %391 = load i32, ptr %24, align 4
  %392 = load i32, ptr %25, align 4
  %393 = mul i32 %391, %37
  %394 = add i32 %393, %39
  %395 = mul i32 %394, %392
  %396 = add i32 %395, 3
  %397 = sext i32 %396 to i64
  %398 = getelementptr float, ptr %390, i64 %397
  store float %389, ptr %398, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.round.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.7, align 8
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !22

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !24

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
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.smax.i64(i64, i64) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(read) }
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
!14 = distinct !{!14, !11, !12}
!15 = distinct !{!15, !11}
!16 = distinct !{!16, !11, !12}
!17 = distinct !{!17, !11}
!18 = distinct !{!18, !11, !12}
!19 = distinct !{!19, !11}
!20 = distinct !{!20, !11, !12}
!21 = distinct !{!21, !11}
!22 = distinct !{!22, !23}
!23 = !{!"llvm.loop.mustprogress"}
!24 = distinct !{!24, !23}
