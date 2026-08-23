; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.13 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_box_blur_v_generic_1ch_kernel_c178_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @_box_blur_v_generic_1ch_kernel_c178_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 40
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
  %28 = getelementptr i8, ptr %19, i64 8
  %29 = getelementptr i8, ptr %19, i64 4
  %30 = getelementptr i8, ptr %19, i64 24
  %31 = getelementptr i8, ptr %19, i64 20
  br i1 %27, label %for_loop_body.us.preheader, label %for_loop_body.lr.ph.split

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %min.iters.check = icmp ult i32 %22, 4
  %min.iters.check19 = icmp ult i32 %22, 16
  %n.vec = and i32 %22, -16
  %32 = sub i32 %n.vec, %21
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %33 = and i32 %21, 6
  %min.epilog.iters.check = icmp eq i32 %33, 0
  %n.vec29 = and i32 %22, -4
  %34 = sub i32 %n.vec29, %21
  %35 = lshr i32 %21, 1
  %36 = trunc i32 %35 to i30
  %37 = zext i30 %36 to i32
  %38 = mul i32 %37, -4
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %.0913.us = phi i32 [ %105, %for_loop_test4.after_for3_crit_edge.us ], [ %16, %for_loop_body.us.preheader ]
  %39 = load ptr, ptr %3, align 8
  %40 = getelementptr inbounds nuw i8, ptr %39, i64 32872
  %41 = load ptr, ptr %40, align 8
  %42 = getelementptr inbounds nuw i8, ptr %41, i64 4
  %43 = load i32, ptr %42, align 4
  %44 = sdiv i32 %.0913.us, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.0913.us
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %45, %.0913.us
  %49 = and i1 %47, %48
  %.neg10.us = sext i1 %49 to i32
  %50 = add i32 %44, %.neg10.us
  %51 = mul i32 %50, %43
  %52 = sub i32 %.0913.us, %51
  %53 = getelementptr inbounds nuw i8, ptr %41, i64 8
  %54 = load i32, ptr %53, align 4
  %55 = add i32 %54, -1
  %56 = load ptr, ptr %28, align 8
  %57 = load i32, ptr %29, align 4
  br i1 %min.iters.check, label %for_loop_body1.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %iter.check
  br i1 %min.iters.check19, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %50, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert21 = insertelement <8 x i32> poison, i32 %55, i64 0
  %broadcast.splat22 = shufflevector <8 x i32> %broadcast.splatinsert21, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert23 = insertelement <8 x i32> poison, i32 %57, i64 0
  %broadcast.splat24 = shufflevector <8 x i32> %broadcast.splatinsert23, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert25 = insertelement <8 x i32> poison, i32 %52, i64 0
  %broadcast.splat26 = shufflevector <8 x i32> %broadcast.splatinsert25, <8 x i32> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 8), %broadcast.splat
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %71, %vector.body ]
  %vec.phi20 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %72, %vector.body ]
  %58 = add <8 x i32> %vec.ind, %broadcast.splat
  %.reass = add <8 x i32> %vec.ind, %invariant.op
  %59 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %58, <8 x i32> zeroinitializer)
  %60 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %.reass, <8 x i32> zeroinitializer)
  %61 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat22, <8 x i32> %59)
  %62 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat22, <8 x i32> %60)
  %63 = mul <8 x i32> %broadcast.splat24, %61
  %64 = mul <8 x i32> %broadcast.splat24, %62
  %65 = add <8 x i32> %63, %broadcast.splat26
  %66 = add <8 x i32> %64, %broadcast.splat26
  %67 = sext <8 x i32> %65 to <8 x i64>
  %68 = sext <8 x i32> %66 to <8 x i64>
  %69 = getelementptr float, ptr %56, <8 x i64> %67
  %70 = getelementptr float, ptr %56, <8 x i64> %68
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %69, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather27 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %70, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %71 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi
  %72 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather27, %vec.phi20
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 16)
  %lsr.iv.next = add i32 %lsr.iv, -16
  %73 = icmp eq i32 %lsr.iv.next, 0
  br i1 %73, label %vec.epilog.iter.check, label %vector.body, !llvm.loop !10

vec.epilog.iter.check:                            ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %72, %71
  %74 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx)
  br i1 %min.epilog.iters.check, label %for_loop_body1.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i32 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.resume.val = phi i32 [ %32, %vec.epilog.iter.check ], [ %neg, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %74, %vec.epilog.iter.check ], [ 0.000000e+00, %vector.main.loop.iter.check ]
  %.splatinsert31 = insertelement <4 x i32> poison, i32 %bc.resume.val, i64 0
  %.splat32 = shufflevector <4 x i32> %.splatinsert31, <4 x i32> poison, <4 x i32> zeroinitializer
  %induction33 = add <4 x i32> %.splat32, <i32 0, i32 1, i32 2, i32 3>
  %75 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %broadcast.splatinsert37 = insertelement <4 x i32> poison, i32 %50, i64 0
  %broadcast.splat38 = shufflevector <4 x i32> %broadcast.splatinsert37, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert39 = insertelement <4 x i32> poison, i32 %55, i64 0
  %broadcast.splat40 = shufflevector <4 x i32> %broadcast.splatinsert39, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert41 = insertelement <4 x i32> poison, i32 %57, i64 0
  %broadcast.splat42 = shufflevector <4 x i32> %broadcast.splatinsert41, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert43 = insertelement <4 x i32> poison, i32 %52, i64 0
  %broadcast.splat44 = shufflevector <4 x i32> %broadcast.splatinsert43, <4 x i32> poison, <4 x i32> zeroinitializer
  %76 = add i32 %38, %vec.epilog.resume.val
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv59 = phi i32 [ %lsr.iv.next60, %vec.epilog.vector.body ], [ %76, %vec.epilog.ph ]
  %vec.ind34 = phi <4 x i32> [ %induction33, %vec.epilog.ph ], [ %vec.ind.next35, %vec.epilog.vector.body ]
  %vec.phi36 = phi <4 x float> [ %75, %vec.epilog.ph ], [ %84, %vec.epilog.vector.body ]
  %77 = add <4 x i32> %vec.ind34, %broadcast.splat38
  %78 = tail call <4 x i32> @llvm.smax.v4i32(<4 x i32> %77, <4 x i32> zeroinitializer)
  %79 = tail call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat40, <4 x i32> %78)
  %80 = mul <4 x i32> %broadcast.splat42, %79
  %81 = add <4 x i32> %80, %broadcast.splat44
  %82 = sext <4 x i32> %81 to <4 x i64>
  %83 = getelementptr float, ptr %56, <4 x i64> %82
  %wide.masked.gather45 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %83, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %84 = fadd reassoc ninf nsz <4 x float> %wide.masked.gather45, %vec.phi36
  %vec.ind.next35 = add <4 x i32> %vec.ind34, splat (i32 4)
  %lsr.iv.next60 = add i32 %lsr.iv59, 4
  %85 = icmp eq i32 %lsr.iv.next60, 0
  br i1 %85, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !13

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %86 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %84)
  br label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %iter.check
  %.012.us.ph = phi i32 [ %32, %vec.epilog.iter.check ], [ %neg, %iter.check ], [ %34, %vec.epilog.middle.block ]
  %.0811.us.ph = phi float [ %74, %vec.epilog.iter.check ], [ 0.000000e+00, %iter.check ], [ %86, %vec.epilog.middle.block ]
  %87 = sub i32 %26, %.012.us.ph
  %88 = add i32 %.012.us.ph, %44
  %89 = add i32 %88, %.neg10.us
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader
  %lsr.iv63 = phi i32 [ %89, %for_loop_body1.us.preheader ], [ %lsr.iv.next64, %for_loop_body1.us ]
  %lsr.iv61 = phi i32 [ %87, %for_loop_body1.us.preheader ], [ %lsr.iv.next62, %for_loop_body1.us ]
  %.0811.us = phi float [ %97, %for_loop_body1.us ], [ %.0811.us.ph, %for_loop_body1.us.preheader ]
  %90 = tail call i32 @llvm.smax.i32(i32 %lsr.iv63, i32 0)
  %91 = tail call i32 @llvm.smin.i32(i32 %55, i32 %90)
  %92 = mul i32 %57, %91
  %93 = add i32 %92, %52
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, ptr %56, i64 %94
  %96 = load float, ptr %95, align 4
  %97 = fadd reassoc ninf nsz float %96, %.0811.us
  %lsr.iv.next62 = add i32 %lsr.iv61, -1
  %lsr.iv.next64 = add i32 %lsr.iv63, 1
  %exitcond15.not = icmp eq i32 %lsr.iv.next62, 0
  br i1 %exitcond15.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us, !llvm.loop !14

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us
  %98 = fdiv reassoc ninf nsz float %97, %24
  %99 = load ptr, ptr %30, align 8
  %100 = load i32, ptr %31, align 4
  %101 = mul i32 %100, %50
  %102 = add i32 %101, %52
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, ptr %99, i64 %103
  store float %98, ptr %104, align 4
  %105 = add nsw i32 %.0913.us, 1
  %exitcond16.not = icmp eq i32 %105, %18
  br i1 %exitcond16.not, label %after_for.loopexit, label %iter.check

for_loop_body.lr.ph.split:                        ; preds = %for_loop_body.lr.ph
  %106 = fdiv reassoc ninf nsz float 0.000000e+00, %24
  %107 = sub i32 %18, %16
  %.neg54 = add i32 %16, 1
  %xtraiter = and i32 %107, 1
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %for_loop_body.prol.loopexit, label %for_loop_body.prol

for_loop_body.prol:                               ; preds = %for_loop_body.lr.ph.split
  %108 = getelementptr inbounds nuw i8, ptr %6, i64 4
  %109 = load i32, ptr %108, align 4
  %110 = sdiv i32 %16, %109
  %111 = mul i32 %110, %109
  %112 = xor i32 %109, %16
  %113 = icmp slt i32 %112, 0
  %114 = icmp ne i32 %111, %16
  %115 = and i1 %113, %114
  %.neg10.prol = sext i1 %115 to i32
  %116 = add i32 %110, %.neg10.prol
  %117 = mul i32 %116, %109
  %118 = sub i32 %16, %117
  %119 = load ptr, ptr %30, align 8
  %120 = load i32, ptr %31, align 4
  %121 = mul i32 %120, %116
  %122 = add i32 %121, %118
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, ptr %119, i64 %123
  store float %106, ptr %124, align 4
  br label %for_loop_body.prol.loopexit

for_loop_body.prol.loopexit:                      ; preds = %for_loop_body.prol, %for_loop_body.lr.ph.split
  %.0913.unr = phi i32 [ %16, %for_loop_body.lr.ph.split ], [ %.neg54, %for_loop_body.prol ]
  %125 = icmp eq i32 %18, %.neg54
  br i1 %125, label %after_for, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.prol.loopexit
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.0913 = phi i32 [ %166, %for_loop_body ], [ %.0913.unr, %for_loop_body.preheader ]
  %126 = load ptr, ptr %3, align 8
  %127 = getelementptr inbounds nuw i8, ptr %126, i64 32872
  %128 = load ptr, ptr %127, align 8
  %129 = getelementptr inbounds nuw i8, ptr %128, i64 4
  %130 = load i32, ptr %129, align 4
  %131 = sdiv i32 %.0913, %130
  %132 = mul i32 %131, %130
  %133 = xor i32 %130, %.0913
  %134 = icmp slt i32 %133, 0
  %135 = icmp ne i32 %132, %.0913
  %136 = and i1 %134, %135
  %.neg10 = sext i1 %136 to i32
  %137 = add i32 %131, %.neg10
  %138 = load ptr, ptr %30, align 8
  %139 = load i32, ptr %31, align 4
  %140 = sub i32 %139, %130
  %141 = mul i32 %140, %137
  %142 = add i32 %.0913, %141
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, ptr %138, i64 %143
  store float %106, ptr %144, align 4
  %145 = load ptr, ptr %3, align 8
  %146 = getelementptr inbounds nuw i8, ptr %145, i64 32872
  %147 = load ptr, ptr %146, align 8
  %148 = getelementptr inbounds nuw i8, ptr %147, i64 4
  %149 = load i32, ptr %148, align 4
  %150 = add i32 %.0913, 1
  %151 = sdiv i32 %150, %149
  %152 = mul i32 %151, %149
  %153 = xor i32 %149, %150
  %154 = icmp slt i32 %153, 0
  %155 = icmp ne i32 %152, %150
  %156 = and i1 %154, %155
  %.neg10.1 = sext i1 %156 to i32
  %157 = add i32 %151, %.neg10.1
  %158 = load ptr, ptr %30, align 8
  %159 = load i32, ptr %31, align 4
  %160 = sub i32 %159, %149
  %161 = mul i32 %160, %157
  %162 = add i32 %.0913, %161
  %163 = add i32 %162, 1
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, ptr %158, i64 %164
  store float %106, ptr %165, align 4
  %166 = add i32 %150, 1
  %exitcond.not.1 = icmp eq i32 %166, %18
  br i1 %exitcond.not.1, label %after_for.loopexit58, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit58:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit58, %after_for.loopexit, %for_loop_body.prol.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.13, align 8
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
