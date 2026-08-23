; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_smooth_flow_y_kernel_c306_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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
  %13 = shl nuw i32 %12, 1
  %14 = load ptr, ptr %3, align 8
  %15 = getelementptr inbounds nuw i8, ptr %14, i64 32872
  %16 = load ptr, ptr %15, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 4
  store i32 %13, ptr %17, align 4
  %18 = mul i32 %13, %8
  %19 = load ptr, ptr %3, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 32872
  %21 = load ptr, ptr %20, align 8
  store i32 %18, ptr %21, align 4
  ret void
}

define void @_smooth_flow_y_kernel_c306_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %.01219.us = phi i32 [ %150, %for_loop_test4.after_for3_crit_edge.us ], [ %16, %for_loop_body.us.preheader ]
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
  %57 = add nsw i32 %52, %.neg14.us
  %58 = shl i32 %57, 1
  %59 = sub i32 %51, %58
  %60 = getelementptr inbounds nuw i8, ptr %40, i64 8
  %61 = load i32, ptr %60, align 4
  %62 = add i32 %61, -1
  %63 = load ptr, ptr %25, align 8
  %64 = load ptr, ptr %26, align 8
  %65 = load i32, ptr %27, align 4
  %66 = load i32, ptr %28, align 4
  br i1 %or.cond, label %vector.ph, label %for_loop_body1.us.preheader

vector.ph:                                        ; preds = %for_loop_body.us
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %49, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert30 = insertelement <8 x i32> poison, i32 %62, i64 0
  %broadcast.splat31 = shufflevector <8 x i32> %broadcast.splatinsert30, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert32 = insertelement <8 x i32> poison, i32 %65, i64 0
  %broadcast.splat33 = shufflevector <8 x i32> %broadcast.splatinsert32, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert34 = insertelement <8 x i32> poison, i32 %57, i64 0
  %broadcast.splat35 = shufflevector <8 x i32> %broadcast.splatinsert34, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert36 = insertelement <8 x i32> poison, i32 %66, i64 0
  %broadcast.splat37 = shufflevector <8 x i32> %broadcast.splatinsert36, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert38 = insertelement <8 x i32> poison, i32 %59, i64 0
  %broadcast.splat39 = shufflevector <8 x i32> %broadcast.splatinsert38, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv53 = phi i64 [ %lsr.iv.next54, %vector.body ], [ %n.vec, %vector.ph ]
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body ], [ 0, %vector.ph ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %80, %vector.body ]
  %vec.phi29 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %79, %vector.body ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %67 = add <8 x i32> %broadcast.splat, %vec.ind
  %68 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %67, <8 x i32> zeroinitializer)
  %69 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %68, <8 x i32> %broadcast.splat31)
  %70 = ashr exact i64 %lsr.iv, 30
  %71 = getelementptr i8, ptr %63, i64 %70
  %wide.load = load <8 x float>, ptr %71, align 4
  %72 = mul <8 x i32> %broadcast.splat33, %69
  %73 = add <8 x i32> %72, %broadcast.splat35
  %74 = mul <8 x i32> %73, %broadcast.splat37
  %75 = add <8 x i32> %74, %broadcast.splat39
  %76 = sext <8 x i32> %75 to <8 x i64>
  %77 = getelementptr float, ptr %64, <8 x i64> %76
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %77, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %78 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.load
  %79 = fadd reassoc ninf nsz <8 x float> %78, %vec.phi29
  %80 = fadd reassoc ninf nsz <8 x float> %wide.load, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %lsr.iv.next = add i64 %lsr.iv, 34359738368
  %lsr.iv.next54 = add i64 %lsr.iv53, -8
  %81 = icmp eq i64 %lsr.iv.next54, 0
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
  %86 = add i32 %49, %85
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = tail call i32 @llvm.smin.i32(i32 %87, i32 %62)
  %89 = add i32 %21, %85
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, ptr %63, i64 %90
  %92 = load float, ptr %91, align 4
  %93 = mul i32 %65, %88
  %94 = add i32 %93, %57
  %95 = mul i32 %94, %66
  %96 = add i32 %95, %59
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, ptr %64, i64 %97
  %99 = load float, ptr %98, align 4
  %100 = fmul reassoc ninf nsz float %99, %92
  %101 = fadd reassoc ninf nsz float %100, %.01115.us.ph
  %102 = fadd reassoc ninf nsz float %92, %.01016.us.ph
  %indvars.iv.next.prol = add nsw i64 %indvars.iv.ph, 1
  br label %for_loop_body1.us.prol.loopexit

for_loop_body1.us.prol.loopexit:                  ; preds = %for_loop_body1.us.prol, %for_loop_body1.us.preheader
  %.lcssa44.unr = phi float [ poison, %for_loop_body1.us.preheader ], [ %101, %for_loop_body1.us.prol ]
  %.lcssa43.unr = phi float [ poison, %for_loop_body1.us.preheader ], [ %102, %for_loop_body1.us.prol ]
  %indvars.iv.unr = phi i64 [ %indvars.iv.ph, %for_loop_body1.us.preheader ], [ %indvars.iv.next.prol, %for_loop_body1.us.prol ]
  %.01016.us.unr = phi float [ %.01016.us.ph, %for_loop_body1.us.preheader ], [ %102, %for_loop_body1.us.prol ]
  %.01115.us.unr = phi float [ %.01115.us.ph, %for_loop_body1.us.preheader ], [ %101, %for_loop_body1.us.prol ]
  %103 = icmp eq i64 %indvars.iv.ph, %36
  br i1 %103, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us.preheader.new

for_loop_body1.us.preheader.new:                  ; preds = %for_loop_body1.us.prol.loopexit
  %104 = zext i32 %49 to i64
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader.new
  %indvars.iv = phi i64 [ %indvars.iv.unr, %for_loop_body1.us.preheader.new ], [ %indvars.iv.next.1, %for_loop_body1.us ]
  %.01016.us = phi float [ %.01016.us.unr, %for_loop_body1.us.preheader.new ], [ %138, %for_loop_body1.us ]
  %.01115.us = phi float [ %.01115.us.unr, %for_loop_body1.us.preheader.new ], [ %137, %for_loop_body1.us ]
  %105 = add i64 %104, %indvars.iv
  %tmp57 = trunc i64 %105 to i32
  %106 = tail call i32 @llvm.smax.i32(i32 %tmp57, i32 0)
  %107 = tail call i32 @llvm.smin.i32(i32 %106, i32 %62)
  %108 = add i64 %37, %indvars.iv
  %tmp56 = trunc i64 %108 to i32
  %109 = sext i32 %tmp56 to i64
  %110 = getelementptr float, ptr %63, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = mul i32 %65, %107
  %113 = add i32 %112, %57
  %114 = mul i32 %113, %66
  %115 = add i32 %114, %59
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, ptr %64, i64 %116
  %118 = load float, ptr %117, align 4
  %119 = fmul reassoc ninf nsz float %118, %111
  %120 = fadd reassoc ninf nsz float %119, %.01115.us
  %121 = fadd reassoc ninf nsz float %111, %.01016.us
  %122 = add i64 %105, 1
  %tmp55 = trunc i64 %122 to i32
  %123 = tail call i32 @llvm.smax.i32(i32 %tmp55, i32 0)
  %124 = tail call i32 @llvm.smin.i32(i32 %123, i32 %62)
  %125 = add i64 %108, 1
  %tmp = trunc i64 %125 to i32
  %126 = sext i32 %tmp to i64
  %127 = getelementptr float, ptr %63, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = mul i32 %65, %124
  %130 = add i32 %129, %57
  %131 = mul i32 %130, %66
  %132 = add i32 %131, %59
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, ptr %64, i64 %133
  %135 = load float, ptr %134, align 4
  %136 = fmul reassoc ninf nsz float %135, %128
  %137 = fadd reassoc ninf nsz float %136, %120
  %138 = fadd reassoc ninf nsz float %128, %121
  %indvars.iv.next.1 = add nsw i64 %indvars.iv, 2
  %exitcond23.not.1 = icmp eq i64 %wide.trip.count, %indvars.iv.next.1
  br i1 %exitcond23.not.1, label %for_loop_test4.after_for3_crit_edge.us.loopexit, label %for_loop_body1.us, !llvm.loop !14

for_loop_test4.after_for3_crit_edge.us.loopexit:  ; preds = %for_loop_body1.us
  br label %for_loop_test4.after_for3_crit_edge.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_test4.after_for3_crit_edge.us.loopexit, %for_loop_body1.us.prol.loopexit, %middle.block
  %.lcssa28 = phi float [ %83, %middle.block ], [ %.lcssa44.unr, %for_loop_body1.us.prol.loopexit ], [ %137, %for_loop_test4.after_for3_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %82, %middle.block ], [ %.lcssa43.unr, %for_loop_body1.us.prol.loopexit ], [ %138, %for_loop_test4.after_for3_crit_edge.us.loopexit ]
  %139 = fadd reassoc ninf nsz float %.lcssa, 0x3D71979980000000
  %140 = fdiv reassoc ninf nsz float %.lcssa28, %139
  %141 = load ptr, ptr %29, align 8
  %142 = load i32, ptr %30, align 4
  %143 = load i32, ptr %31, align 4
  %144 = mul i32 %142, %49
  %145 = add i32 %144, %57
  %146 = mul i32 %145, %143
  %147 = add i32 %146, %59
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %141, i64 %148
  store float %140, ptr %149, align 4
  %150 = add nsw i32 %.01219.us, 1
  %exitcond24.not = icmp eq i32 %150, %18
  br i1 %exitcond24.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.01219 = phi i32 [ %185, %for_loop_body ], [ %16, %for_loop_body.preheader ]
  %151 = load ptr, ptr %3, align 8
  %152 = getelementptr inbounds nuw i8, ptr %151, i64 32872
  %153 = load ptr, ptr %152, align 8
  %154 = getelementptr inbounds nuw i8, ptr %153, i64 4
  %155 = load i32, ptr %154, align 4
  %156 = sdiv i32 %.01219, %155
  %157 = mul i32 %156, %155
  %158 = xor i32 %155, %.01219
  %159 = icmp slt i32 %158, 0
  %160 = icmp ne i32 %.01219, %157
  %161 = and i1 %159, %160
  %.neg13 = sext i1 %161 to i32
  %162 = add i32 %156, %.neg13
  %163 = mul i32 %162, %155
  %164 = mul i32 %155, -1
  %165 = mul i32 %164, %162
  %166 = add i32 %.01219, %165
  %167 = sdiv i32 %166, 2
  %168 = icmp slt i32 %166, 0
  %169 = shl nsw i32 %167, 1
  %170 = icmp ne i32 %166, %169
  %171 = and i1 %168, %170
  %.neg14 = sext i1 %171 to i32
  %172 = add nsw i32 %167, %.neg14
  %173 = shl i32 %172, 1
  %174 = load ptr, ptr %29, align 8
  %175 = load i32, ptr %30, align 4
  %176 = load i32, ptr %31, align 4
  %177 = mul i32 %175, %162
  %178 = add i32 %177, %172
  %179 = mul i32 %178, %176
  %180 = sub i32 %179, %163
  %181 = sub i32 %180, %173
  %182 = add i32 %.01219, %181
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %174, i64 %183
  store float 0.000000e+00, ptr %184, align 4
  %185 = add nsw i32 %.01219, 1
  %exitcond.not = icmp eq i32 %18, %185
  br i1 %exitcond.not, label %after_for.loopexit52, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit52:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit52, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #2 {
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
