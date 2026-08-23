; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.15 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_box_blur_h_generic_1ch_kernel_c176_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 32
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 36
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 8
  store i32 %5, ptr %10, align 4
  %11 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %12 = load ptr, ptr %6, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 32872
  %14 = load ptr, ptr %13, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 4
  store i32 %11, ptr %15, align 4
  %16 = mul i32 %11, %3
  %17 = load ptr, ptr %6, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  store i32 %16, ptr %19, align 4
  ret void
}

define void @_box_blur_h_generic_1ch_kernel_c176_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %n.vec27 = and i32 %22, -4
  %34 = sub i32 %n.vec27, %21
  %35 = lshr i32 %21, 1
  %36 = trunc i32 %35 to i30
  %37 = zext i30 %36 to i32
  %38 = mul i32 %37, -4
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %.0913.us = phi i32 [ %102, %for_loop_test4.after_for3_crit_edge.us ], [ %16, %for_loop_body.us.preheader ]
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
  %58 = mul i32 %57, %50
  br i1 %min.iters.check, label %for_loop_body1.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %iter.check
  br i1 %min.iters.check19, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %52, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert21 = insertelement <8 x i32> poison, i32 %55, i64 0
  %broadcast.splat22 = shufflevector <8 x i32> %broadcast.splatinsert21, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert23 = insertelement <8 x i32> poison, i32 %58, i64 0
  %broadcast.splat24 = shufflevector <8 x i32> %broadcast.splatinsert23, <8 x i32> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 8), %broadcast.splat
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %70, %vector.body ]
  %vec.phi20 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %71, %vector.body ]
  %59 = add <8 x i32> %vec.ind, %broadcast.splat
  %.reass = add <8 x i32> %vec.ind, %invariant.op
  %60 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %59, <8 x i32> zeroinitializer)
  %61 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %.reass, <8 x i32> zeroinitializer)
  %62 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat22, <8 x i32> %60)
  %63 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat22, <8 x i32> %61)
  %64 = add <8 x i32> %broadcast.splat24, %62
  %65 = add <8 x i32> %broadcast.splat24, %63
  %66 = sext <8 x i32> %64 to <8 x i64>
  %67 = sext <8 x i32> %65 to <8 x i64>
  %68 = getelementptr float, ptr %56, <8 x i64> %66
  %69 = getelementptr float, ptr %56, <8 x i64> %67
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %68, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather25 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %69, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %70 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi
  %71 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather25, %vec.phi20
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 16)
  %lsr.iv.next = add i32 %lsr.iv, -16
  %72 = icmp eq i32 %lsr.iv.next, 0
  br i1 %72, label %vec.epilog.iter.check, label %vector.body, !llvm.loop !10

vec.epilog.iter.check:                            ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %71, %70
  %73 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx)
  br i1 %min.epilog.iters.check, label %for_loop_body1.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i32 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.resume.val = phi i32 [ %32, %vec.epilog.iter.check ], [ %neg, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %73, %vec.epilog.iter.check ], [ 0.000000e+00, %vector.main.loop.iter.check ]
  %.splatinsert29 = insertelement <4 x i32> poison, i32 %bc.resume.val, i64 0
  %.splat30 = shufflevector <4 x i32> %.splatinsert29, <4 x i32> poison, <4 x i32> zeroinitializer
  %induction31 = add <4 x i32> %.splat30, <i32 0, i32 1, i32 2, i32 3>
  %74 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %broadcast.splatinsert35 = insertelement <4 x i32> poison, i32 %52, i64 0
  %broadcast.splat36 = shufflevector <4 x i32> %broadcast.splatinsert35, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert37 = insertelement <4 x i32> poison, i32 %55, i64 0
  %broadcast.splat38 = shufflevector <4 x i32> %broadcast.splatinsert37, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert39 = insertelement <4 x i32> poison, i32 %58, i64 0
  %broadcast.splat40 = shufflevector <4 x i32> %broadcast.splatinsert39, <4 x i32> poison, <4 x i32> zeroinitializer
  %75 = add i32 %38, %vec.epilog.resume.val
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv55 = phi i32 [ %lsr.iv.next56, %vec.epilog.vector.body ], [ %75, %vec.epilog.ph ]
  %vec.ind32 = phi <4 x i32> [ %induction31, %vec.epilog.ph ], [ %vec.ind.next33, %vec.epilog.vector.body ]
  %vec.phi34 = phi <4 x float> [ %74, %vec.epilog.ph ], [ %82, %vec.epilog.vector.body ]
  %76 = add <4 x i32> %vec.ind32, %broadcast.splat36
  %77 = tail call <4 x i32> @llvm.smax.v4i32(<4 x i32> %76, <4 x i32> zeroinitializer)
  %78 = tail call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat38, <4 x i32> %77)
  %79 = add <4 x i32> %broadcast.splat40, %78
  %80 = sext <4 x i32> %79 to <4 x i64>
  %81 = getelementptr float, ptr %56, <4 x i64> %80
  %wide.masked.gather41 = tail call <4 x float> @llvm.masked.gather.v4f32.v4p0(<4 x ptr> %81, i32 4, <4 x i1> splat (i1 true), <4 x float> poison)
  %82 = fadd reassoc ninf nsz <4 x float> %wide.masked.gather41, %vec.phi34
  %vec.ind.next33 = add <4 x i32> %vec.ind32, splat (i32 4)
  %lsr.iv.next56 = add i32 %lsr.iv55, 4
  %83 = icmp eq i32 %lsr.iv.next56, 0
  br i1 %83, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !13

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %84 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %82)
  br label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %iter.check
  %.012.us.ph = phi i32 [ %32, %vec.epilog.iter.check ], [ %neg, %iter.check ], [ %34, %vec.epilog.middle.block ]
  %.0811.us.ph = phi float [ %73, %vec.epilog.iter.check ], [ 0.000000e+00, %iter.check ], [ %84, %vec.epilog.middle.block ]
  %85 = sub i32 %26, %.012.us.ph
  %86 = add i32 %.012.us.ph, %.0913.us
  %87 = sub i32 %86, %51
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader
  %lsr.iv59 = phi i32 [ %87, %for_loop_body1.us.preheader ], [ %lsr.iv.next60, %for_loop_body1.us ]
  %lsr.iv57 = phi i32 [ %85, %for_loop_body1.us.preheader ], [ %lsr.iv.next58, %for_loop_body1.us ]
  %.0811.us = phi float [ %94, %for_loop_body1.us ], [ %.0811.us.ph, %for_loop_body1.us.preheader ]
  %88 = tail call i32 @llvm.smax.i32(i32 %lsr.iv59, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %55, i32 %88)
  %90 = add i32 %58, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %56, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = fadd reassoc ninf nsz float %93, %.0811.us
  %lsr.iv.next58 = add i32 %lsr.iv57, -1
  %lsr.iv.next60 = add i32 %lsr.iv59, 1
  %exitcond15.not = icmp eq i32 %lsr.iv.next58, 0
  br i1 %exitcond15.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us, !llvm.loop !14

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us
  %95 = fdiv reassoc ninf nsz float %94, %24
  %96 = load ptr, ptr %30, align 8
  %97 = load i32, ptr %31, align 4
  %98 = mul i32 %97, %50
  %99 = add i32 %98, %52
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, ptr %96, i64 %100
  store float %95, ptr %101, align 4
  %102 = add nsw i32 %.0913.us, 1
  %exitcond16.not = icmp eq i32 %102, %18
  br i1 %exitcond16.not, label %after_for.loopexit, label %iter.check

for_loop_body.lr.ph.split:                        ; preds = %for_loop_body.lr.ph
  %103 = fdiv reassoc ninf nsz float 0.000000e+00, %24
  %104 = sub i32 %18, %16
  %.neg50 = add i32 %16, 1
  %xtraiter = and i32 %104, 1
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %for_loop_body.prol.loopexit, label %for_loop_body.prol

for_loop_body.prol:                               ; preds = %for_loop_body.lr.ph.split
  %105 = getelementptr inbounds nuw i8, ptr %6, i64 4
  %106 = load i32, ptr %105, align 4
  %107 = sdiv i32 %16, %106
  %108 = mul i32 %107, %106
  %109 = xor i32 %106, %16
  %110 = icmp slt i32 %109, 0
  %111 = icmp ne i32 %108, %16
  %112 = and i1 %110, %111
  %.neg10.prol = sext i1 %112 to i32
  %113 = add i32 %107, %.neg10.prol
  %114 = mul i32 %113, %106
  %115 = sub i32 %16, %114
  %116 = load ptr, ptr %30, align 8
  %117 = load i32, ptr %31, align 4
  %118 = mul i32 %117, %113
  %119 = add i32 %118, %115
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, ptr %116, i64 %120
  store float %103, ptr %121, align 4
  br label %for_loop_body.prol.loopexit

for_loop_body.prol.loopexit:                      ; preds = %for_loop_body.prol, %for_loop_body.lr.ph.split
  %.0913.unr = phi i32 [ %16, %for_loop_body.lr.ph.split ], [ %.neg50, %for_loop_body.prol ]
  %122 = icmp eq i32 %18, %.neg50
  br i1 %122, label %after_for, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.prol.loopexit
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.0913 = phi i32 [ %163, %for_loop_body ], [ %.0913.unr, %for_loop_body.preheader ]
  %123 = load ptr, ptr %3, align 8
  %124 = getelementptr inbounds nuw i8, ptr %123, i64 32872
  %125 = load ptr, ptr %124, align 8
  %126 = getelementptr inbounds nuw i8, ptr %125, i64 4
  %127 = load i32, ptr %126, align 4
  %128 = sdiv i32 %.0913, %127
  %129 = mul i32 %128, %127
  %130 = xor i32 %127, %.0913
  %131 = icmp slt i32 %130, 0
  %132 = icmp ne i32 %129, %.0913
  %133 = and i1 %131, %132
  %.neg10 = sext i1 %133 to i32
  %134 = add i32 %128, %.neg10
  %135 = load ptr, ptr %30, align 8
  %136 = load i32, ptr %31, align 4
  %137 = sub i32 %136, %127
  %138 = mul i32 %137, %134
  %139 = add i32 %.0913, %138
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %135, i64 %140
  store float %103, ptr %141, align 4
  %142 = load ptr, ptr %3, align 8
  %143 = getelementptr inbounds nuw i8, ptr %142, i64 32872
  %144 = load ptr, ptr %143, align 8
  %145 = getelementptr inbounds nuw i8, ptr %144, i64 4
  %146 = load i32, ptr %145, align 4
  %147 = add i32 %.0913, 1
  %148 = sdiv i32 %147, %146
  %149 = mul i32 %148, %146
  %150 = xor i32 %146, %147
  %151 = icmp slt i32 %150, 0
  %152 = icmp ne i32 %149, %147
  %153 = and i1 %151, %152
  %.neg10.1 = sext i1 %153 to i32
  %154 = add i32 %148, %.neg10.1
  %155 = load ptr, ptr %30, align 8
  %156 = load i32, ptr %31, align 4
  %157 = sub i32 %156, %146
  %158 = mul i32 %157, %154
  %159 = add i32 %.0913, %158
  %160 = add i32 %159, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, ptr %155, i64 %161
  store float %103, ptr %162, align 4
  %163 = add i32 %147, 1
  %exitcond.not.1 = icmp eq i32 %163, %18
  br i1 %exitcond.not.1, label %after_for.loopexit54, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit54:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit54, %after_for.loopexit, %for_loop_body.prol.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.15, align 8
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
