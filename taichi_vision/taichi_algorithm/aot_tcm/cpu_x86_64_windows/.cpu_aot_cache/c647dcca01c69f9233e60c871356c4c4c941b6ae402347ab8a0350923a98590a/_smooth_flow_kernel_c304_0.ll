; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.5 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_smooth_flow_kernel_c304_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 48
  %2 = load i32, ptr %1, align 4
  %3 = tail call i32 @llvm.smax.i32(i32 %2, i32 0)
  %4 = getelementptr i8, ptr %0, i64 52
  %5 = load i32, ptr %4, align 4
  %6 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds nuw i8, ptr %7, i64 32872
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds nuw i8, ptr %9, i64 8
  store i32 %5, ptr %10, align 4
  %11 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %12 = shl nuw i32 %11, 1
  %13 = load ptr, ptr %6, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 32872
  %15 = load ptr, ptr %14, align 8
  %16 = getelementptr inbounds nuw i8, ptr %15, i64 4
  store i32 %12, ptr %16, align 4
  %17 = mul i32 %12, %3
  %18 = load ptr, ptr %6, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  store i32 %17, ptr %20, align 4
  ret void
}

define void @_smooth_flow_kernel_c304_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %15 = tail call i32 @llvm.smax.i32(i32 %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 72
  %21 = load i32, ptr %20, align 4
  %neg = sub i32 0, %21
  %22 = add i32 %21, 1
  %23 = icmp slt i32 %16, %18
  br i1 %23, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %24 = icmp sgt i32 %22, %neg
  %25 = getelementptr i8, ptr %19, i64 64
  %26 = getelementptr i8, ptr %19, i64 16
  %27 = getelementptr i8, ptr %19, i64 4
  %28 = getelementptr i8, ptr %19, i64 8
  %29 = getelementptr i8, ptr %19, i64 40
  %30 = getelementptr i8, ptr %19, i64 28
  %31 = getelementptr i8, ptr %19, i64 32
  br i1 %24, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  br label %for_loop_body

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %32 = sext i32 %neg to i64
  %wide.trip.count = sext i32 %22 to i64
  %33 = sub i64 %wide.trip.count, %32
  %min.iters.check = icmp ugt i64 %33, 7
  %34 = sub nsw i64 %32, %wide.trip.count
  %.not = icmp ugt i64 %34, -2147483649
  %or.cond = select i1 %min.iters.check, i1 %.not, i1 false
  %n.vec = and i64 %33, -8
  %35 = add nsw i64 %n.vec, %32
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %cmp.n = icmp eq i64 %33, %n.vec
  %36 = add nsw i64 %wide.trip.count, -1
  %37 = zext i32 %21 to i64
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %.01219.us = phi i32 [ %147, %for_loop_test4.after_for3_crit_edge.us ], [ %16, %for_loop_body.us.preheader ]
  %38 = load ptr, ptr %3, align 8
  %39 = getelementptr inbounds nuw i8, ptr %38, i64 32872
  %40 = load ptr, ptr %39, align 8
  %41 = getelementptr inbounds nuw i8, ptr %40, i64 4
  %42 = load i32, ptr %41, align 4
  %43 = sdiv i32 %.01219.us, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.01219.us
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %44, %.01219.us
  %48 = and i1 %46, %47
  %.neg13.us = sext i1 %48 to i32
  %49 = add i32 %43, %.neg13.us
  %50 = mul i32 %49, %42
  %51 = sub i32 %.01219.us, %50
  %52 = sdiv i32 %51, 2
  %53 = icmp slt i32 %51, 0
  %54 = shl nsw i32 %52, 1
  %55 = icmp ne i32 %54, %51
  %56 = and i1 %53, %55
  %.neg14.us = sext i1 %56 to i32
  %57 = add i32 %52, %.neg14.us
  %58 = shl i32 %57, 1
  %59 = sub i32 %51, %58
  %60 = getelementptr inbounds nuw i8, ptr %40, i64 8
  %61 = load i32, ptr %60, align 4
  %62 = add i32 %61, -1
  %63 = load ptr, ptr %25, align 8
  %64 = load ptr, ptr %26, align 8
  %65 = load i32, ptr %27, align 4
  %66 = load i32, ptr %28, align 4
  %67 = mul i32 %65, %49
  br i1 %or.cond, label %vector.ph, label %for_loop_body1.us.preheader

vector.ph:                                        ; preds = %for_loop_body.us
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %57, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert30 = insertelement <8 x i32> poison, i32 %62, i64 0
  %broadcast.splat31 = shufflevector <8 x i32> %broadcast.splatinsert30, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert32 = insertelement <8 x i32> poison, i32 %67, i64 0
  %broadcast.splat33 = shufflevector <8 x i32> %broadcast.splatinsert32, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert34 = insertelement <8 x i32> poison, i32 %66, i64 0
  %broadcast.splat35 = shufflevector <8 x i32> %broadcast.splatinsert34, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert36 = insertelement <8 x i32> poison, i32 %59, i64 0
  %broadcast.splat37 = shufflevector <8 x i32> %broadcast.splatinsert36, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv51 = phi i64 [ %lsr.iv.next52, %vector.body ], [ %n.vec, %vector.ph ]
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body ], [ 0, %vector.ph ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %80, %vector.body ]
  %vec.phi29 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %79, %vector.body ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %68 = add <8 x i32> %broadcast.splat, %vec.ind
  %69 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %68, <8 x i32> zeroinitializer)
  %70 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %69, <8 x i32> %broadcast.splat31)
  %71 = ashr exact i64 %lsr.iv, 30
  %72 = getelementptr i8, ptr %63, i64 %71
  %wide.load = load <8 x float>, ptr %72, align 4
  %73 = add <8 x i32> %broadcast.splat33, %70
  %74 = mul <8 x i32> %73, %broadcast.splat35
  %75 = add <8 x i32> %74, %broadcast.splat37
  %76 = sext <8 x i32> %75 to <8 x i64>
  %77 = getelementptr float, ptr %64, <8 x i64> %76
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %77, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %78 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.load
  %79 = fadd reassoc ninf nsz <8 x float> %78, %vec.phi29
  %80 = fadd reassoc ninf nsz <8 x float> %wide.load, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %lsr.iv.next = add i64 %lsr.iv, 34359738368
  %lsr.iv.next52 = add i64 %lsr.iv51, -8
  %81 = icmp eq i64 %lsr.iv.next52, 0
  br i1 %81, label %middle.block, label %vector.body, !llvm.loop !11

middle.block:                                     ; preds = %vector.body
  %82 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %80)
  %83 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %79)
  br i1 %cmp.n, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %middle.block, %for_loop_body.us
  %indvars.iv.ph = phi i64 [ %32, %for_loop_body.us ], [ %35, %middle.block ]
  %.01016.us.ph = phi float [ 0.000000e+00, %for_loop_body.us ], [ %82, %middle.block ]
  %.01115.us.ph = phi float [ 0.000000e+00, %for_loop_body.us ], [ %83, %middle.block ]
  %84 = sub nsw i64 %wide.trip.count, %indvars.iv.ph
  %xtraiter = and i64 %84, 1
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %for_loop_body1.us.prol.loopexit, label %for_loop_body1.us.prol

for_loop_body1.us.prol:                           ; preds = %for_loop_body1.us.preheader
  %85 = trunc nsw i64 %indvars.iv.ph to i32
  %86 = add i32 %57, %85
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = tail call i32 @llvm.smin.i32(i32 %87, i32 %62)
  %89 = add i32 %21, %85
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %63, i64 %90
  %92 = load float, ptr %91, align 4
  %93 = add i32 %67, %88
  %94 = mul i32 %93, %66
  %95 = add i32 %94, %59
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, ptr %64, i64 %96
  %98 = load float, ptr %97, align 4
  %99 = fmul reassoc ninf nsz float %98, %92
  %100 = fadd reassoc ninf nsz float %99, %.01115.us.ph
  %101 = fadd reassoc ninf nsz float %92, %.01016.us.ph
  %indvars.iv.next.prol = add nsw i64 %indvars.iv.ph, 1
  br label %for_loop_body1.us.prol.loopexit

for_loop_body1.us.prol.loopexit:                  ; preds = %for_loop_body1.us.prol, %for_loop_body1.us.preheader
  %.lcssa42.unr = phi float [ poison, %for_loop_body1.us.preheader ], [ %100, %for_loop_body1.us.prol ]
  %.lcssa41.unr = phi float [ poison, %for_loop_body1.us.preheader ], [ %101, %for_loop_body1.us.prol ]
  %indvars.iv.unr = phi i64 [ %indvars.iv.ph, %for_loop_body1.us.preheader ], [ %indvars.iv.next.prol, %for_loop_body1.us.prol ]
  %.01016.us.unr = phi float [ %.01016.us.ph, %for_loop_body1.us.preheader ], [ %101, %for_loop_body1.us.prol ]
  %.01115.us.unr = phi float [ %.01115.us.ph, %for_loop_body1.us.preheader ], [ %100, %for_loop_body1.us.prol ]
  %102 = icmp eq i64 %indvars.iv.ph, %36
  br i1 %102, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us.preheader.new

for_loop_body1.us.preheader.new:                  ; preds = %for_loop_body1.us.prol.loopexit
  %103 = zext i32 %57 to i64
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader.new
  %indvars.iv = phi i64 [ %indvars.iv.unr, %for_loop_body1.us.preheader.new ], [ %indvars.iv.next.1, %for_loop_body1.us ]
  %.01016.us = phi float [ %.01016.us.unr, %for_loop_body1.us.preheader.new ], [ %135, %for_loop_body1.us ]
  %.01115.us = phi float [ %.01115.us.unr, %for_loop_body1.us.preheader.new ], [ %134, %for_loop_body1.us ]
  %104 = add i64 %103, %indvars.iv
  %tmp55 = trunc i64 %104 to i32
  %105 = tail call i32 @llvm.smax.i32(i32 %tmp55, i32 0)
  %106 = tail call i32 @llvm.smin.i32(i32 %105, i32 %62)
  %107 = add i64 %37, %indvars.iv
  %tmp54 = trunc i64 %107 to i32
  %108 = sext i32 %tmp54 to i64
  %109 = getelementptr float, ptr %63, i64 %108
  %110 = load float, ptr %109, align 4
  %111 = add i32 %67, %106
  %112 = mul i32 %111, %66
  %113 = add i32 %112, %59
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, ptr %64, i64 %114
  %116 = load float, ptr %115, align 4
  %117 = fmul reassoc ninf nsz float %116, %110
  %118 = fadd reassoc ninf nsz float %117, %.01115.us
  %119 = fadd reassoc ninf nsz float %110, %.01016.us
  %120 = add i64 %104, 1
  %tmp53 = trunc i64 %120 to i32
  %121 = tail call i32 @llvm.smax.i32(i32 %tmp53, i32 0)
  %122 = tail call i32 @llvm.smin.i32(i32 %121, i32 %62)
  %123 = add i64 %107, 1
  %tmp = trunc i64 %123 to i32
  %124 = sext i32 %tmp to i64
  %125 = getelementptr float, ptr %63, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = add i32 %67, %122
  %128 = mul i32 %127, %66
  %129 = add i32 %128, %59
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, ptr %64, i64 %130
  %132 = load float, ptr %131, align 4
  %133 = fmul reassoc ninf nsz float %132, %126
  %134 = fadd reassoc ninf nsz float %133, %118
  %135 = fadd reassoc ninf nsz float %126, %119
  %indvars.iv.next.1 = add nsw i64 %indvars.iv, 2
  %exitcond23.not.1 = icmp eq i64 %wide.trip.count, %indvars.iv.next.1
  br i1 %exitcond23.not.1, label %for_loop_test4.after_for3_crit_edge.us.loopexit, label %for_loop_body1.us, !llvm.loop !14

for_loop_test4.after_for3_crit_edge.us.loopexit:  ; preds = %for_loop_body1.us
  br label %for_loop_test4.after_for3_crit_edge.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_test4.after_for3_crit_edge.us.loopexit, %for_loop_body1.us.prol.loopexit, %middle.block
  %.lcssa28 = phi float [ %83, %middle.block ], [ %.lcssa42.unr, %for_loop_body1.us.prol.loopexit ], [ %134, %for_loop_test4.after_for3_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %82, %middle.block ], [ %.lcssa41.unr, %for_loop_body1.us.prol.loopexit ], [ %135, %for_loop_test4.after_for3_crit_edge.us.loopexit ]
  %136 = fadd reassoc ninf nsz float %.lcssa, 0x3D71979980000000
  %137 = fdiv reassoc ninf nsz float %.lcssa28, %136
  %138 = load ptr, ptr %29, align 8
  %139 = load i32, ptr %30, align 4
  %140 = load i32, ptr %31, align 4
  %141 = mul i32 %139, %49
  %142 = add i32 %141, %57
  %143 = mul i32 %142, %140
  %144 = add i32 %143, %59
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, ptr %138, i64 %145
  store float %137, ptr %146, align 4
  %147 = add nsw i32 %.01219.us, 1
  %exitcond24.not = icmp eq i32 %147, %18
  br i1 %exitcond24.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.01219 = phi i32 [ %182, %for_loop_body ], [ %16, %for_loop_body.preheader ]
  %148 = load ptr, ptr %3, align 8
  %149 = getelementptr inbounds nuw i8, ptr %148, i64 32872
  %150 = load ptr, ptr %149, align 8
  %151 = getelementptr inbounds nuw i8, ptr %150, i64 4
  %152 = load i32, ptr %151, align 4
  %153 = sdiv i32 %.01219, %152
  %154 = mul i32 %153, %152
  %155 = xor i32 %152, %.01219
  %156 = icmp slt i32 %155, 0
  %157 = icmp ne i32 %.01219, %154
  %158 = and i1 %156, %157
  %.neg13 = sext i1 %158 to i32
  %159 = add i32 %153, %.neg13
  %160 = mul i32 %159, %152
  %161 = mul i32 %152, -1
  %162 = mul i32 %161, %159
  %163 = add i32 %.01219, %162
  %164 = sdiv i32 %163, 2
  %165 = icmp slt i32 %163, 0
  %166 = shl nsw i32 %164, 1
  %167 = icmp ne i32 %163, %166
  %168 = and i1 %165, %167
  %.neg14 = sext i1 %168 to i32
  %169 = add nsw i32 %164, %.neg14
  %170 = shl i32 %169, 1
  %171 = load ptr, ptr %29, align 8
  %172 = load i32, ptr %30, align 4
  %173 = load i32, ptr %31, align 4
  %174 = mul i32 %172, %159
  %175 = add i32 %174, %169
  %176 = mul i32 %175, %173
  %177 = sub i32 %176, %160
  %178 = sub i32 %177, %170
  %179 = add i32 %.01219, %178
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, ptr %171, i64 %180
  store float 0.000000e+00, ptr %181, align 4
  %182 = add nsw i32 %.01219, 1
  %exitcond.not = icmp eq i32 %18, %182
  br i1 %exitcond.not, label %after_for.loopexit50, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit50:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit50, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
  %4 = alloca %struct.RuntimeContext.5, align 8
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #5 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(read) }
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
!11 = distinct !{!11, !12, !13}
!12 = !{!"llvm.loop.isvectorized", i32 1}
!13 = !{!"llvm.loop.unroll.runtime.disable"}
!14 = distinct !{!14, !12}
!15 = distinct !{!15, !16}
!16 = !{!"llvm.loop.mustprogress"}
!17 = distinct !{!17, !16}
