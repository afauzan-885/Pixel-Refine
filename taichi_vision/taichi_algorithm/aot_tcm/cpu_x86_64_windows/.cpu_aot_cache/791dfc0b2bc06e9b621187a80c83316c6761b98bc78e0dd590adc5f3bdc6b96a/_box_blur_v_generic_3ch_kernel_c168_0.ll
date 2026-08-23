; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.3 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_box_blur_v_generic_3ch_kernel_c168_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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
  %12 = tail call i32 @llvm.smax.i32(i32 %11, i32 0)
  %13 = load ptr, ptr %3, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 4
  store i32 %12, ptr %16, align 4
  %17 = mul i32 %12, %8
  %18 = load ptr, ptr %3, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  store i32 %17, ptr %20, align 4
  ret void
}

define void @_box_blur_v_generic_3ch_kernel_c168_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 56
  %21 = load i32, ptr %20, align 4
  %neg = sub i32 0, %21
  %22 = shl i32 %21, 1
  %23 = or disjoint i32 %22, 1
  %24 = sitofp i32 %23 to float
  %25 = icmp slt i32 %16, %18
  br i1 %25, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %26 = add i32 %21, 1
  %27 = icmp sgt i32 %26, %neg
  %28 = getelementptr i8, ptr %19, i64 16
  %29 = getelementptr i8, ptr %19, i64 4
  %30 = getelementptr i8, ptr %19, i64 8
  %31 = getelementptr i8, ptr %19, i64 40
  %32 = getelementptr i8, ptr %19, i64 28
  %33 = getelementptr i8, ptr %19, i64 32
  br i1 %27, label %for_loop_body.us.preheader, label %for_loop_body.lr.ph.split

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %min.iters.check = icmp ult i32 %22, 4
  %min.iters.check23 = icmp ult i32 %22, 16
  %n.vec = and i32 %22, -16
  %34 = sub i32 %n.vec, %21
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %35 = and i32 %21, 6
  %min.epilog.iters.check = icmp eq i32 %35, 0
  %n.vec35 = and i32 %22, -4
  %36 = sub i32 %n.vec35, %21
  %37 = lshr i32 %21, 1
  %38 = trunc i32 %37 to i30
  %39 = zext i30 %38 to i32
  %40 = mul i32 %39, -4
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %.01317.us = phi i32 [ %119, %for_loop_test4.after_for3_crit_edge.us ], [ %16, %for_loop_body.us.preheader ]
  %41 = load ptr, ptr %3, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 32872
  %43 = load ptr, ptr %42, align 8
  %44 = getelementptr inbounds nuw i8, ptr %43, i64 4
  %45 = load i32, ptr %44, align 4
  %46 = sdiv i32 %.01317.us, %45
  %47 = mul i32 %46, %45
  %48 = xor i32 %45, %.01317.us
  %49 = icmp slt i32 %48, 0
  %50 = icmp ne i32 %47, %.01317.us
  %51 = and i1 %49, %50
  %.neg14.us = sext i1 %51 to i32
  %52 = add i32 %46, %.neg14.us
  %53 = mul i32 %52, %45
  %54 = sub i32 %.01317.us, %53
  %55 = getelementptr inbounds nuw i8, ptr %43, i64 8
  %56 = load i32, ptr %55, align 4
  %57 = add i32 %56, -1
  %58 = load ptr, ptr %28, align 8
  %59 = load i32, ptr %29, align 4
  %60 = load i32, ptr %30, align 4
  br i1 %min.iters.check, label %for_loop_body1.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %iter.check
  br i1 %min.iters.check23, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %52, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert25 = insertelement <8 x i32> poison, i32 %57, i64 0
  %broadcast.splat26 = shufflevector <8 x i32> %broadcast.splatinsert25, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert27 = insertelement <8 x i32> poison, i32 %59, i64 0
  %broadcast.splat28 = shufflevector <8 x i32> %broadcast.splatinsert27, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert29 = insertelement <8 x i32> poison, i32 %54, i64 0
  %broadcast.splat30 = shufflevector <8 x i32> %broadcast.splatinsert29, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert31 = insertelement <8 x i32> poison, i32 %60, i64 0
  %broadcast.splat32 = shufflevector <8 x i32> %broadcast.splatinsert31, <8 x i32> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 8), %broadcast.splat
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %78, %vector.body ]
  %vec.phi24 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %79, %vector.body ]
  %61 = add <8 x i32> %vec.ind, %broadcast.splat
  %.reass = add <8 x i32> %vec.ind, %invariant.op
  %62 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %61, <8 x i32> zeroinitializer)
  %63 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %.reass, <8 x i32> zeroinitializer)
  %64 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat26, <8 x i32> %62)
  %65 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat26, <8 x i32> %63)
  %66 = mul <8 x i32> %broadcast.splat28, %64
  %67 = mul <8 x i32> %broadcast.splat28, %65
  %68 = add <8 x i32> %66, %broadcast.splat30
  %69 = add <8 x i32> %67, %broadcast.splat30
  %70 = mul <8 x i32> %68, %broadcast.splat32
  %71 = mul <8 x i32> %69, %broadcast.splat32
  %72 = add <8 x i32> %70, splat (i32 2)
  %73 = add <8 x i32> %71, splat (i32 2)
  %74 = sext <8 x i32> %72 to <8 x i64>
  %75 = sext <8 x i32> %73 to <8 x i64>
  %76 = getelementptr float, ptr %58, <8 x i64> %74
  %77 = getelementptr float, ptr %58, <8 x i64> %75
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %76, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather33 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %77, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %78 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi
  %79 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather33, %vec.phi24
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 16)
  %lsr.iv.next = add i32 %lsr.iv, -16
  %80 = icmp eq i32 %lsr.iv.next, 0
  br i1 %80, label %vec.epilog.iter.check, label %vector.body, !llvm.loop !10

vec.epilog.iter.check:                            ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %79, %78
  %81 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx)
  br i1 %min.epilog.iters.check, label %for_loop_body1.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i32 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.resume.val = phi i32 [ %34, %vec.epilog.iter.check ], [ %neg, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %81, %vec.epilog.iter.check ], [ 0.000000e+00, %vector.main.loop.iter.check ]
  %.splatinsert37 = insertelement <4 x i32> poison, i32 %bc.resume.val, i64 0
  %.splat38 = shufflevector <4 x i32> %.splatinsert37, <4 x i32> poison, <4 x i32> zeroinitializer
  %induction39 = add <4 x i32> %.splat38, <i32 0, i32 1, i32 2, i32 3>
  %82 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %broadcast.splatinsert43 = insertelement <4 x i32> poison, i32 %52, i64 0
  %broadcast.splat44 = shufflevector <4 x i32> %broadcast.splatinsert43, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert45 = insertelement <4 x i32> poison, i32 %57, i64 0
  %broadcast.splat46 = shufflevector <4 x i32> %broadcast.splatinsert45, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert47 = insertelement <4 x i32> poison, i32 %59, i64 0
  %broadcast.splat48 = shufflevector <4 x i32> %broadcast.splatinsert47, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert49 = insertelement <4 x i32> poison, i32 %54, i64 0
  %broadcast.splat50 = shufflevector <4 x i32> %broadcast.splatinsert49, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert51 = insertelement <4 x i32> poison, i32 %60, i64 0
  %broadcast.splat52 = shufflevector <4 x i32> %broadcast.splatinsert51, <4 x i32> poison, <4 x i32> zeroinitializer
  %83 = add i32 %40, %vec.epilog.resume.val
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv66 = phi i32 [ %lsr.iv.next67, %vec.epilog.vector.body ], [ %83, %vec.epilog.ph ]
  %vec.ind40 = phi <4 x i32> [ %induction39, %vec.epilog.ph ], [ %vec.ind.next41, %vec.epilog.vector.body ]
  %vec.phi42 = phi <4 x float> [ %82, %vec.epilog.ph ], [ %93, %vec.epilog.vector.body ]
  %84 = add <4 x i32> %vec.ind40, %broadcast.splat44
  %85 = tail call <4 x i32> @llvm.smax.v4i32(<4 x i32> %84, <4 x i32> zeroinitializer)
  %86 = tail call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat46, <4 x i32> %85)
  %87 = mul <4 x i32> %broadcast.splat48, %86
  %88 = add <4 x i32> %87, %broadcast.splat50
  %89 = mul <4 x i32> %88, %broadcast.splat52
  %90 = add <4 x i32> %89, splat (i32 2)
  %91 = sext <4 x i32> %90 to <4 x i64>
  %92 = getelementptr float, ptr %58, <4 x i64> %91
  %wide.masked.gather53 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %92, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %93 = fadd reassoc ninf nsz <4 x float> %wide.masked.gather53, %vec.phi42
  %vec.ind.next41 = add <4 x i32> %vec.ind40, splat (i32 4)
  %lsr.iv.next67 = add i32 %lsr.iv66, 4
  %94 = icmp eq i32 %lsr.iv.next67, 0
  br i1 %94, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !13

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %95 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %93)
  br label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %iter.check
  %.016.us.ph = phi i32 [ %34, %vec.epilog.iter.check ], [ %neg, %iter.check ], [ %36, %vec.epilog.middle.block ]
  %.01015.us.ph = phi float [ %81, %vec.epilog.iter.check ], [ 0.000000e+00, %iter.check ], [ %95, %vec.epilog.middle.block ]
  %96 = sub i32 %26, %.016.us.ph
  %97 = add i32 %.016.us.ph, %46
  %98 = add i32 %97, %.neg14.us
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader
  %lsr.iv70 = phi i32 [ %98, %for_loop_body1.us.preheader ], [ %lsr.iv.next71, %for_loop_body1.us ]
  %lsr.iv68 = phi i32 [ %96, %for_loop_body1.us.preheader ], [ %lsr.iv.next69, %for_loop_body1.us ]
  %.01015.us = phi float [ %108, %for_loop_body1.us ], [ %.01015.us.ph, %for_loop_body1.us.preheader ]
  %99 = tail call i32 @llvm.smax.i32(i32 %lsr.iv70, i32 0)
  %100 = tail call i32 @llvm.smin.i32(i32 %57, i32 %99)
  %101 = mul i32 %59, %100
  %102 = add i32 %101, %54
  %103 = mul i32 %102, %60
  %104 = add i32 %103, 2
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, ptr %58, i64 %105
  %107 = load float, ptr %106, align 4
  %108 = fadd reassoc ninf nsz float %107, %.01015.us
  %lsr.iv.next69 = add i32 %lsr.iv68, -1
  %lsr.iv.next71 = add i32 %lsr.iv70, 1
  %exitcond19.not = icmp eq i32 %lsr.iv.next69, 0
  br i1 %exitcond19.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us, !llvm.loop !14

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us
  %109 = fdiv reassoc ninf nsz float %108, %24
  %110 = load ptr, ptr %31, align 8
  %111 = load i32, ptr %32, align 4
  %112 = load i32, ptr %33, align 4
  %113 = mul i32 %111, %52
  %114 = add i32 %113, %54
  %115 = mul i32 %114, %112
  %116 = add i32 %115, 2
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, ptr %110, i64 %117
  store float %109, ptr %118, align 4
  %119 = add nsw i32 %.01317.us, 1
  %exitcond20.not = icmp eq i32 %119, %18
  br i1 %exitcond20.not, label %after_for.loopexit, label %iter.check

for_loop_body.lr.ph.split:                        ; preds = %for_loop_body.lr.ph
  %120 = fdiv reassoc ninf nsz float 0.000000e+00, %24
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph.split
  %.01317 = phi i32 [ %16, %for_loop_body.lr.ph.split ], [ %143, %for_loop_body ]
  %121 = load ptr, ptr %3, align 8
  %122 = getelementptr inbounds nuw i8, ptr %121, i64 32872
  %123 = load ptr, ptr %122, align 8
  %124 = getelementptr inbounds nuw i8, ptr %123, i64 4
  %125 = load i32, ptr %124, align 4
  %126 = sdiv i32 %.01317, %125
  %127 = mul i32 %126, %125
  %128 = xor i32 %125, %.01317
  %129 = icmp slt i32 %128, 0
  %130 = icmp ne i32 %.01317, %127
  %131 = and i1 %129, %130
  %.neg14 = sext i1 %131 to i32
  %132 = add i32 %126, %.neg14
  %133 = load ptr, ptr %31, align 8
  %134 = load i32, ptr %32, align 4
  %135 = load i32, ptr %33, align 4
  %136 = sub i32 %134, %125
  %137 = mul i32 %136, %132
  %138 = add i32 %.01317, %137
  %139 = mul i32 %138, %135
  %140 = add i32 %139, 2
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %133, i64 %141
  store float %120, ptr %142, align 4
  %143 = add nsw i32 %.01317, 1
  %exitcond.not = icmp eq i32 %18, %143
  br i1 %exitcond.not, label %after_for.loopexit65, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit65:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit65, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.3, align 8
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !15

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !17

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

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #4

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr>, i32 immarg, <4 x i1>, <4 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #4

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(read) }
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
!10 = distinct !{!10, !11, !12}
!11 = !{!"llvm.loop.isvectorized", i32 1}
!12 = !{!"llvm.loop.unroll.runtime.disable"}
!13 = distinct !{!13, !11, !12}
!14 = distinct !{!14, !12, !11}
!15 = distinct !{!15, !16}
!16 = !{!"llvm.loop.mustprogress"}
!17 = distinct !{!17, !16}
