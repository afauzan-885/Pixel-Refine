; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.4 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @phase1_coarse_analysis_kernel_c84_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 96
  %2 = load i32, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 8
  store i32 %2, ptr %7, align 4
  %8 = load ptr, ptr %context, align 8
  %9 = getelementptr i8, ptr %8, i64 100
  %10 = load i32, ptr %9, align 4
  %11 = load ptr, ptr %3, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 32872
  %13 = load ptr, ptr %12, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 4
  store i32 %10, ptr %14, align 4
  %15 = mul i32 %10, %2
  %16 = load ptr, ptr %3, align 8
  %17 = getelementptr inbounds nuw i8, ptr %16, i64 32872
  %18 = load ptr, ptr %17, align 8
  store i32 %15, ptr %18, align 4
  ret void
}

define void @phase1_coarse_analysis_kernel_c84_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #9
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %0)
  ret void
}

; Function Attrs: nofree nounwind memory(readwrite, inaccessiblemem: write)
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
  %15 = tail call range(i32 -268435457, 268435456) i32 @llvm.smax.i32(i32 range(i32 -268435457, 268435456) %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 112
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 116
  %23 = load i32, ptr %22, align 4
  %24 = getelementptr i8, ptr %19, i64 120
  %25 = load i32, ptr %24, align 4
  %26 = getelementptr i8, ptr %19, i64 124
  %27 = load i32, ptr %26, align 4
  %28 = icmp slt i32 %16, %18
  br i1 %28, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.preheader
  %.04488 = phi i32 [ %716, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = srem i32 %.04488, %33
  %35 = sdiv i32 %.04488, %33
  %36 = getelementptr inbounds nuw i8, ptr %31, i64 8
  %37 = load i32, ptr %36, align 4
  %38 = srem i32 %35, %37
  %39 = mul i32 %38, %21
  %40 = mul i32 %34, %23
  %41 = sub i32 %25, %39
  %42 = tail call i32 @llvm.smin.i32(i32 %21, i32 %41)
  %43 = sub i32 %27, %40
  %44 = tail call i32 @llvm.smin.i32(i32 %23, i32 %43)
  %45 = icmp sgt i32 %42, 0
  %46 = icmp sgt i32 %44, 0
  %spec.select = select i1 %45, i1 %46, i1 false
  %47 = load ptr, ptr %0, align 8
  br i1 %spec.select, label %true_block1, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body
  %48 = getelementptr i8, ptr %47, i64 128
  %49 = load float, ptr %48, align 4
  %50 = fmul reassoc ninf nsz float %49, 0x3FC99999A0000000
  %51 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %50, float 0x3F747AE140000000)
  %52 = fcmp reassoc ninf nsz ogt float %49, 0x3EB0C6F7A0000000
  %53 = add i32 %39, 1
  %54 = add i32 %40, 1
  %.not = icmp samesign ult i32 %42, 3
  %.not89 = icmp samesign ult i32 %44, 3
  %or.cond = select i1 %.not, i1 true, i1 %.not89
  br i1 %or.cond, label %for_loop_body54.lr.ph.split.us, label %for_loop_body4.lr.ph.split.us

for_loop_body4.lr.ph.split.us:                    ; preds = %true_block1
  %55 = add nsw i32 %44, -1
  %56 = lshr i32 %55, 1
  %57 = add nsw i32 %42, -1
  %58 = lshr i32 %57, 1
  %59 = getelementptr i8, ptr %47, i64 84
  %60 = getelementptr i8, ptr %47, i64 88
  %61 = getelementptr i8, ptr %47, i64 68
  %62 = getelementptr i8, ptr %47, i64 72
  %63 = getelementptr i8, ptr %47, i64 52
  %64 = getelementptr i8, ptr %47, i64 56
  %65 = getelementptr i8, ptr %47, i64 36
  %66 = getelementptr i8, ptr %47, i64 40
  %67 = getelementptr i8, ptr %47, i64 20
  %68 = getelementptr i8, ptr %47, i64 24
  %69 = getelementptr i8, ptr %47, i64 4
  %70 = getelementptr i8, ptr %47, i64 8
  %71 = load ptr, ptr %70, align 8
  %72 = load i32, ptr %69, align 4
  %73 = sext i32 %72 to i64
  %74 = load ptr, ptr %68, align 8
  %75 = load i32, ptr %67, align 4
  %76 = sext i32 %75 to i64
  %77 = load ptr, ptr %66, align 8
  %78 = load i32, ptr %65, align 4
  %79 = sext i32 %78 to i64
  %80 = load ptr, ptr %64, align 8
  %81 = load i32, ptr %63, align 4
  %82 = sext i32 %81 to i64
  %83 = load ptr, ptr %62, align 8
  %84 = load i32, ptr %61, align 4
  %85 = sext i32 %84 to i64
  %86 = load ptr, ptr %60, align 8
  %87 = load i32, ptr %59, align 4
  %88 = sext i32 %87 to i64
  %wide.trip.count98 = zext nneg i32 %58 to i64
  %wide.trip.count = zext i32 %56 to i64
  %89 = add nsw i64 %wide.trip.count, -1
  %min.iters.check151 = icmp ult i32 %44, 17
  %90 = trunc nsw i64 %89 to i32
  %mul.result = shl i32 %90, 1
  %91 = add i32 %54, %mul.result
  %92 = icmp slt i32 %91, %54
  %93 = icmp ugt i64 %89, 4294967295
  %94 = or i1 %92, %93
  %min.iters.check154 = icmp ult i32 %44, 65
  %n.vec158 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %52, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %95 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert169 = insertelement <8 x i32> poison, i32 %54, i64 0
  %broadcast.splat170 = shufflevector <8 x i32> %broadcast.splatinsert169, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert194 = insertelement <8 x float> poison, float %51, i64 0
  %broadcast.splat195 = shufflevector <8 x float> %broadcast.splatinsert194, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat170
  %invariant.op363 = add <8 x i32> splat (i32 32), %broadcast.splat170
  %invariant.op365 = add <8 x i32> splat (i32 48), %broadcast.splat170
  %cmp.n258 = icmp eq i64 %n.vec158, %wide.trip.count
  %n.vec.remaining266 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check267 = icmp eq i64 %n.vec.remaining266, 0
  %n.vec269 = and i64 %wide.trip.count, 2147483640
  %cmp.n303 = icmp eq i64 %n.vec269, %wide.trip.count
  %96 = zext i32 %55 to i64
  %97 = lshr i64 %96, 4
  %98 = mul nsw i64 %97, -8
  %99 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check153

iter.check153:                                    ; preds = %for_loop_test11.after_for10_crit_edge.us, %for_loop_body4.lr.ph.split.us
  %indvars.iv95 = phi i64 [ %indvars.iv.next96, %for_loop_test11.after_for10_crit_edge.us ], [ 0, %for_loop_body4.lr.ph.split.us ]
  %.05076.us = phi float [ %.lcssa, %for_loop_test11.after_for10_crit_edge.us ], [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ]
  %.05275.us = phi float [ %.lcssa125, %for_loop_test11.after_for10_crit_edge.us ], [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ]
  %indvars.iv95.tr = trunc i64 %indvars.iv95 to i32
  %100 = shl i32 %indvars.iv95.tr, 1
  %101 = add i32 %53, %100
  %102 = sext i32 %101 to i64
  %103 = mul nsw i64 %73, %102
  %104 = getelementptr float, ptr %71, i64 %103
  %105 = mul nsw i64 %76, %102
  %106 = getelementptr float, ptr %74, i64 %105
  %107 = mul nsw i64 %79, %102
  %108 = getelementptr float, ptr %77, i64 %107
  %109 = mul nsw i64 %82, %102
  %110 = getelementptr float, ptr %80, i64 %109
  %111 = mul nsw i64 %85, %102
  %112 = getelementptr float, ptr %83, i64 %111
  %113 = mul nsw i64 %88, %102
  %114 = getelementptr float, ptr %86, i64 %113
  %brmerge = select i1 %min.iters.check151, i1 true, i1 %94
  br i1 %brmerge, label %for_loop_body8.us.preheader, label %vector.main.loop.iter.check155

vector.main.loop.iter.check155:                   ; preds = %iter.check153
  br i1 %min.iters.check154, label %vec.epilog.ph264, label %vector.ph156

vector.ph156:                                     ; preds = %vector.main.loop.iter.check155
  %115 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05076.us, i64 0
  %116 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05275.us, i64 0
  br label %vector.body159

vector.body159:                                   ; preds = %vector.body159, %vector.ph156
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body159 ], [ %n.vec158, %vector.ph156 ]
  %vec.phi161 = phi <8 x float> [ %115, %vector.ph156 ], [ %511, %vector.body159 ]
  %vec.phi162 = phi <8 x float> [ zeroinitializer, %vector.ph156 ], [ %512, %vector.body159 ]
  %vec.phi163 = phi <8 x float> [ zeroinitializer, %vector.ph156 ], [ %513, %vector.body159 ]
  %vec.phi164 = phi <8 x float> [ zeroinitializer, %vector.ph156 ], [ %514, %vector.body159 ]
  %vec.phi165 = phi <8 x float> [ %116, %vector.ph156 ], [ %507, %vector.body159 ]
  %vec.phi166 = phi <8 x float> [ zeroinitializer, %vector.ph156 ], [ %508, %vector.body159 ]
  %vec.phi167 = phi <8 x float> [ zeroinitializer, %vector.ph156 ], [ %509, %vector.body159 ]
  %vec.phi168 = phi <8 x float> [ zeroinitializer, %vector.ph156 ], [ %510, %vector.body159 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph156 ], [ %vec.ind.next, %vector.body159 ]
  %117 = shl <8 x i32> %vec.ind, splat (i32 1)
  %118 = add <8 x i32> %broadcast.splat170, %117
  %.reass = add <8 x i32> %117, %invariant.op
  %.reass364 = add <8 x i32> %117, %invariant.op363
  %.reass366 = add <8 x i32> %117, %invariant.op365
  %119 = sext <8 x i32> %118 to <8 x i64>
  %120 = sext <8 x i32> %.reass to <8 x i64>
  %121 = sext <8 x i32> %.reass364 to <8 x i64>
  %122 = sext <8 x i32> %.reass366 to <8 x i64>
  %123 = getelementptr float, ptr %104, <8 x i64> %119
  %124 = getelementptr float, ptr %104, <8 x i64> %120
  %125 = getelementptr float, ptr %104, <8 x i64> %121
  %126 = getelementptr float, ptr %104, <8 x i64> %122
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %123, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather171 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %124, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather172 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %125, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather173 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %126, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %127 = getelementptr float, ptr %106, <8 x i64> %119
  %128 = getelementptr float, ptr %106, <8 x i64> %120
  %129 = getelementptr float, ptr %106, <8 x i64> %121
  %130 = getelementptr float, ptr %106, <8 x i64> %122
  %wide.masked.gather174 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %127, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather175 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %128, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather176 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %129, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather177 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %130, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %131 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather174
  %132 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather171, %wide.masked.gather175
  %133 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather172, %wide.masked.gather176
  %134 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather173, %wide.masked.gather177
  %135 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %131)
  %136 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %132)
  %137 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %133)
  %138 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %134)
  %139 = getelementptr float, ptr %108, <8 x i64> %119
  %140 = getelementptr float, ptr %108, <8 x i64> %120
  %141 = getelementptr float, ptr %108, <8 x i64> %121
  %142 = getelementptr float, ptr %108, <8 x i64> %122
  %wide.masked.gather178 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %139, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather179 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %140, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather180 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %141, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather181 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %142, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %143 = getelementptr float, ptr %110, <8 x i64> %119
  %144 = getelementptr float, ptr %110, <8 x i64> %120
  %145 = getelementptr float, ptr %110, <8 x i64> %121
  %146 = getelementptr float, ptr %110, <8 x i64> %122
  %wide.masked.gather182 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %143, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather183 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %144, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather184 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %145, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather185 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %146, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %147 = getelementptr float, ptr %112, <8 x i64> %119
  %148 = getelementptr float, ptr %112, <8 x i64> %120
  %149 = getelementptr float, ptr %112, <8 x i64> %121
  %150 = getelementptr float, ptr %112, <8 x i64> %122
  %wide.masked.gather186 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %147, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather187 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %148, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather188 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %149, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather189 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %150, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %151 = getelementptr float, ptr %114, <8 x i64> %119
  %152 = getelementptr float, ptr %114, <8 x i64> %120
  %153 = getelementptr float, ptr %114, <8 x i64> %121
  %154 = getelementptr float, ptr %114, <8 x i64> %122
  %wide.masked.gather190 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %151, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather191 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %152, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather192 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %153, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather193 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %154, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %155 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather178, %wide.masked.gather178
  %156 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather179, %wide.masked.gather179
  %157 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather180, %wide.masked.gather180
  %158 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather181, %wide.masked.gather181
  %159 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather182, %wide.masked.gather182
  %160 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather183, %wide.masked.gather183
  %161 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather184, %wide.masked.gather184
  %162 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather185, %wide.masked.gather185
  %163 = fadd reassoc ninf nsz <8 x float> %159, %155
  %164 = fadd reassoc ninf nsz <8 x float> %160, %156
  %165 = fadd reassoc ninf nsz <8 x float> %161, %157
  %166 = fadd reassoc ninf nsz <8 x float> %162, %158
  %167 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather186, %wide.masked.gather186
  %168 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather187, %wide.masked.gather187
  %169 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather188, %wide.masked.gather188
  %170 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather189, %wide.masked.gather189
  %171 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather190, %wide.masked.gather190
  %172 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather191, %wide.masked.gather191
  %173 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather192, %wide.masked.gather192
  %174 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather193, %wide.masked.gather193
  %175 = fadd reassoc ninf nsz <8 x float> %171, %167
  %176 = fadd reassoc ninf nsz <8 x float> %172, %168
  %177 = fadd reassoc ninf nsz <8 x float> %173, %169
  %178 = fadd reassoc ninf nsz <8 x float> %174, %170
  %179 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %163, <8 x float> %175)
  %180 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %164, <8 x float> %176)
  %181 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %165, <8 x float> %177)
  %182 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %166, <8 x float> %178)
  %183 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather174, splat (float -2.000000e+00)
  %184 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather175, splat (float -2.000000e+00)
  %185 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather176, splat (float -2.000000e+00)
  %186 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather177, splat (float -2.000000e+00)
  %187 = fadd reassoc ninf nsz <8 x float> %183, splat (float 3.000000e+00)
  %188 = fadd reassoc ninf nsz <8 x float> %184, splat (float 3.000000e+00)
  %189 = fadd reassoc ninf nsz <8 x float> %185, splat (float 3.000000e+00)
  %190 = fadd reassoc ninf nsz <8 x float> %186, splat (float 3.000000e+00)
  %191 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %187, <8 x float> splat (float 3.000000e+00))
  %192 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %188, <8 x float> splat (float 3.000000e+00))
  %193 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %189, <8 x float> splat (float 3.000000e+00))
  %194 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %190, <8 x float> splat (float 3.000000e+00))
  %195 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %191, <8 x float> splat (float 1.000000e+00))
  %196 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %192, <8 x float> splat (float 1.000000e+00))
  %197 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %193, <8 x float> splat (float 1.000000e+00))
  %198 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %194, <8 x float> splat (float 1.000000e+00))
  %199 = fmul reassoc ninf nsz <8 x float> %195, %broadcast.splat195
  %200 = fmul reassoc ninf nsz <8 x float> %196, %broadcast.splat195
  %201 = fmul reassoc ninf nsz <8 x float> %197, %broadcast.splat195
  %202 = fmul reassoc ninf nsz <8 x float> %198, %broadcast.splat195
  %203 = fcmp reassoc ninf nsz olt <8 x float> %179, splat (float 1.500000e+02)
  %204 = fcmp reassoc ninf nsz olt <8 x float> %180, splat (float 1.500000e+02)
  %205 = fcmp reassoc ninf nsz olt <8 x float> %181, splat (float 1.500000e+02)
  %206 = fcmp reassoc ninf nsz olt <8 x float> %182, splat (float 1.500000e+02)
  %207 = xor <8 x i1> %203, splat (i1 true)
  %208 = xor <8 x i1> %204, splat (i1 true)
  %209 = xor <8 x i1> %205, splat (i1 true)
  %210 = xor <8 x i1> %206, splat (i1 true)
  %211 = select <8 x i1> %broadcast.splat, <8 x i1> %207, <8 x i1> zeroinitializer
  %212 = select <8 x i1> %broadcast.splat, <8 x i1> %208, <8 x i1> zeroinitializer
  %213 = select <8 x i1> %broadcast.splat, <8 x i1> %209, <8 x i1> zeroinitializer
  %214 = select <8 x i1> %broadcast.splat, <8 x i1> %210, <8 x i1> zeroinitializer
  %215 = fcmp reassoc ninf nsz olt <8 x float> %135, %199
  %216 = fcmp reassoc ninf nsz olt <8 x float> %136, %200
  %217 = fcmp reassoc ninf nsz olt <8 x float> %137, %201
  %218 = fcmp reassoc ninf nsz olt <8 x float> %138, %202
  %219 = xor <8 x i1> %215, splat (i1 true)
  %220 = xor <8 x i1> %216, splat (i1 true)
  %221 = xor <8 x i1> %217, splat (i1 true)
  %222 = xor <8 x i1> %218, splat (i1 true)
  %223 = select <8 x i1> %211, <8 x i1> %219, <8 x i1> zeroinitializer
  %224 = select <8 x i1> %212, <8 x i1> %220, <8 x i1> zeroinitializer
  %225 = select <8 x i1> %213, <8 x i1> %221, <8 x i1> zeroinitializer
  %226 = select <8 x i1> %214, <8 x i1> %222, <8 x i1> zeroinitializer
  %227 = fmul reassoc ninf nsz <8 x float> %199, splat (float 4.000000e+00)
  %228 = fmul reassoc ninf nsz <8 x float> %200, splat (float 4.000000e+00)
  %229 = fmul reassoc ninf nsz <8 x float> %201, splat (float 4.000000e+00)
  %230 = fmul reassoc ninf nsz <8 x float> %202, splat (float 4.000000e+00)
  %231 = fdiv reassoc ninf nsz <8 x float> %135, %227
  %232 = fdiv reassoc ninf nsz <8 x float> %136, %228
  %233 = fdiv reassoc ninf nsz <8 x float> %137, %229
  %234 = fdiv reassoc ninf nsz <8 x float> %138, %230
  %235 = fcmp reassoc ninf nsz ogt <8 x float> %231, splat (float 1.000000e+00)
  %236 = fcmp reassoc ninf nsz ogt <8 x float> %232, splat (float 1.000000e+00)
  %237 = fcmp reassoc ninf nsz ogt <8 x float> %233, splat (float 1.000000e+00)
  %238 = fcmp reassoc ninf nsz ogt <8 x float> %234, splat (float 1.000000e+00)
  %239 = select <8 x i1> %235, <8 x float> splat (float 1.000000e+00), <8 x float> %231
  %240 = select <8 x i1> %236, <8 x float> splat (float 1.000000e+00), <8 x float> %232
  %241 = select <8 x i1> %237, <8 x float> splat (float 1.000000e+00), <8 x float> %233
  %242 = select <8 x i1> %238, <8 x float> splat (float 1.000000e+00), <8 x float> %234
  %243 = fmul reassoc ninf nsz <8 x float> %239, splat (float 0x3FD99999A0000000)
  %244 = fmul reassoc ninf nsz <8 x float> %240, splat (float 0x3FD99999A0000000)
  %245 = fmul reassoc ninf nsz <8 x float> %241, splat (float 0x3FD99999A0000000)
  %246 = fmul reassoc ninf nsz <8 x float> %242, splat (float 0x3FD99999A0000000)
  %247 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %243
  %248 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %244
  %249 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %245
  %250 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %246
  %251 = select <8 x i1> %211, <8 x i1> %215, <8 x i1> zeroinitializer
  %252 = select <8 x i1> %212, <8 x i1> %216, <8 x i1> zeroinitializer
  %253 = select <8 x i1> %213, <8 x i1> %217, <8 x i1> zeroinitializer
  %254 = select <8 x i1> %214, <8 x i1> %218, <8 x i1> zeroinitializer
  %255 = fmul reassoc ninf nsz <8 x float> %135, splat (float 0x3FC3333340000000)
  %256 = fmul reassoc ninf nsz <8 x float> %136, splat (float 0x3FC3333340000000)
  %257 = fmul reassoc ninf nsz <8 x float> %137, splat (float 0x3FC3333340000000)
  %258 = fmul reassoc ninf nsz <8 x float> %138, splat (float 0x3FC3333340000000)
  %259 = fdiv reassoc ninf nsz <8 x float> %255, %199
  %260 = fdiv reassoc ninf nsz <8 x float> %256, %200
  %261 = fdiv reassoc ninf nsz <8 x float> %257, %201
  %262 = fdiv reassoc ninf nsz <8 x float> %258, %202
  %263 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %259
  %264 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %260
  %265 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %261
  %266 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %262
  %267 = select <8 x i1> %broadcast.splat, <8 x i1> %203, <8 x i1> zeroinitializer
  %268 = select <8 x i1> %broadcast.splat, <8 x i1> %204, <8 x i1> zeroinitializer
  %269 = select <8 x i1> %broadcast.splat, <8 x i1> %205, <8 x i1> zeroinitializer
  %270 = select <8 x i1> %broadcast.splat, <8 x i1> %206, <8 x i1> zeroinitializer
  %271 = fmul reassoc ninf nsz <8 x float> %199, splat (float 1.500000e+00)
  %272 = fmul reassoc ninf nsz <8 x float> %200, splat (float 1.500000e+00)
  %273 = fmul reassoc ninf nsz <8 x float> %201, splat (float 1.500000e+00)
  %274 = fmul reassoc ninf nsz <8 x float> %202, splat (float 1.500000e+00)
  %275 = fcmp reassoc ninf nsz uge <8 x float> %135, %271
  %276 = fcmp reassoc ninf nsz uge <8 x float> %136, %272
  %277 = fcmp reassoc ninf nsz uge <8 x float> %137, %273
  %278 = fcmp reassoc ninf nsz uge <8 x float> %138, %274
  %279 = select <8 x i1> %267, <8 x i1> %275, <8 x i1> zeroinitializer
  %280 = select <8 x i1> %268, <8 x i1> %276, <8 x i1> zeroinitializer
  %281 = select <8 x i1> %269, <8 x i1> %277, <8 x i1> zeroinitializer
  %282 = select <8 x i1> %270, <8 x i1> %278, <8 x i1> zeroinitializer
  %283 = fsub reassoc ninf nsz <8 x float> %135, %271
  %284 = fsub reassoc ninf nsz <8 x float> %136, %272
  %285 = fsub reassoc ninf nsz <8 x float> %137, %273
  %286 = fsub reassoc ninf nsz <8 x float> %138, %274
  %287 = fdiv reassoc ninf nsz <8 x float> %283, %271
  %288 = fdiv reassoc ninf nsz <8 x float> %284, %272
  %289 = fdiv reassoc ninf nsz <8 x float> %285, %273
  %290 = fdiv reassoc ninf nsz <8 x float> %286, %274
  %291 = fcmp reassoc ninf nsz ogt <8 x float> %287, splat (float 1.000000e+00)
  %292 = fcmp reassoc ninf nsz ogt <8 x float> %288, splat (float 1.000000e+00)
  %293 = fcmp reassoc ninf nsz ogt <8 x float> %289, splat (float 1.000000e+00)
  %294 = fcmp reassoc ninf nsz ogt <8 x float> %290, splat (float 1.000000e+00)
  %295 = select <8 x i1> %291, <8 x float> splat (float 1.000000e+00), <8 x float> %287
  %296 = select <8 x i1> %292, <8 x float> splat (float 1.000000e+00), <8 x float> %288
  %297 = select <8 x i1> %293, <8 x float> splat (float 1.000000e+00), <8 x float> %289
  %298 = select <8 x i1> %294, <8 x float> splat (float 1.000000e+00), <8 x float> %290
  %299 = fmul reassoc ninf nsz <8 x float> %295, splat (float 0x3FC99999A0000000)
  %300 = fmul reassoc ninf nsz <8 x float> %296, splat (float 0x3FC99999A0000000)
  %301 = fmul reassoc ninf nsz <8 x float> %297, splat (float 0x3FC99999A0000000)
  %302 = fmul reassoc ninf nsz <8 x float> %298, splat (float 0x3FC99999A0000000)
  %303 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %299
  %304 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %300
  %305 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %301
  %306 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %302
  %307 = fmul reassoc ninf nsz <8 x float> %135, splat (float 0x3FEE666660000000)
  %308 = fmul reassoc ninf nsz <8 x float> %136, splat (float 0x3FEE666660000000)
  %309 = fmul reassoc ninf nsz <8 x float> %137, splat (float 0x3FEE666660000000)
  %310 = fmul reassoc ninf nsz <8 x float> %138, splat (float 0x3FEE666660000000)
  %311 = fdiv reassoc ninf nsz <8 x float> %307, %271
  %312 = fdiv reassoc ninf nsz <8 x float> %308, %272
  %313 = fdiv reassoc ninf nsz <8 x float> %309, %273
  %314 = fdiv reassoc ninf nsz <8 x float> %310, %274
  %315 = fadd reassoc ninf nsz <8 x float> %311, splat (float 0x3FA99999A0000000)
  %316 = fadd reassoc ninf nsz <8 x float> %312, splat (float 0x3FA99999A0000000)
  %317 = fadd reassoc ninf nsz <8 x float> %313, splat (float 0x3FA99999A0000000)
  %318 = fadd reassoc ninf nsz <8 x float> %314, splat (float 0x3FA99999A0000000)
  %319 = or <8 x i1> %267, %251
  %320 = or <8 x i1> %268, %252
  %321 = or <8 x i1> %269, %253
  %322 = or <8 x i1> %270, %254
  %323 = or <8 x i1> %319, %223
  %324 = or <8 x i1> %320, %224
  %325 = or <8 x i1> %321, %225
  %326 = or <8 x i1> %322, %226
  %327 = or <8 x i1> %323, %95
  %328 = or <8 x i1> %324, %95
  %329 = or <8 x i1> %325, %95
  %330 = or <8 x i1> %326, %95
  %predphi = select <8 x i1> %279, <8 x float> %303, <8 x float> %315
  %predphi196 = select <8 x i1> %251, <8 x float> %263, <8 x float> %predphi
  %predphi197 = select <8 x i1> %223, <8 x float> %247, <8 x float> %predphi196
  %predphi198 = select <8 x i1> %broadcast.splat, <8 x float> %predphi197, <8 x float> splat (float 1.000000e+00)
  %predphi199 = select <8 x i1> %280, <8 x float> %304, <8 x float> %316
  %predphi200 = select <8 x i1> %252, <8 x float> %264, <8 x float> %predphi199
  %predphi201 = select <8 x i1> %224, <8 x float> %248, <8 x float> %predphi200
  %predphi202 = select <8 x i1> %broadcast.splat, <8 x float> %predphi201, <8 x float> splat (float 1.000000e+00)
  %predphi203 = select <8 x i1> %281, <8 x float> %305, <8 x float> %317
  %predphi204 = select <8 x i1> %253, <8 x float> %265, <8 x float> %predphi203
  %predphi205 = select <8 x i1> %225, <8 x float> %249, <8 x float> %predphi204
  %predphi206 = select <8 x i1> %broadcast.splat, <8 x float> %predphi205, <8 x float> splat (float 1.000000e+00)
  %predphi207 = select <8 x i1> %282, <8 x float> %306, <8 x float> %318
  %predphi208 = select <8 x i1> %254, <8 x float> %266, <8 x float> %predphi207
  %predphi209 = select <8 x i1> %226, <8 x float> %250, <8 x float> %predphi208
  %predphi210 = select <8 x i1> %broadcast.splat, <8 x float> %predphi209, <8 x float> splat (float 1.000000e+00)
  %331 = fcmp reassoc ninf nsz ogt <8 x float> %179, splat (float 0x3EB0C6F7A0000000)
  %332 = fcmp reassoc ninf nsz ogt <8 x float> %180, splat (float 0x3EB0C6F7A0000000)
  %333 = fcmp reassoc ninf nsz ogt <8 x float> %181, splat (float 0x3EB0C6F7A0000000)
  %334 = fcmp reassoc ninf nsz ogt <8 x float> %182, splat (float 0x3EB0C6F7A0000000)
  %335 = select <8 x i1> %327, <8 x i1> %331, <8 x i1> zeroinitializer
  %336 = select <8 x i1> %328, <8 x i1> %332, <8 x i1> zeroinitializer
  %337 = select <8 x i1> %329, <8 x i1> %333, <8 x i1> zeroinitializer
  %338 = select <8 x i1> %330, <8 x i1> %334, <8 x i1> zeroinitializer
  %339 = fcmp reassoc ninf nsz ogt <8 x float> %163, splat (float 0x3EB0C6F7A0000000)
  %340 = fcmp reassoc ninf nsz ogt <8 x float> %164, splat (float 0x3EB0C6F7A0000000)
  %341 = fcmp reassoc ninf nsz ogt <8 x float> %165, splat (float 0x3EB0C6F7A0000000)
  %342 = fcmp reassoc ninf nsz ogt <8 x float> %166, splat (float 0x3EB0C6F7A0000000)
  %343 = fcmp reassoc ninf nsz ogt <8 x float> %175, splat (float 0x3EB0C6F7A0000000)
  %344 = fcmp reassoc ninf nsz ogt <8 x float> %176, splat (float 0x3EB0C6F7A0000000)
  %345 = fcmp reassoc ninf nsz ogt <8 x float> %177, splat (float 0x3EB0C6F7A0000000)
  %346 = fcmp reassoc ninf nsz ogt <8 x float> %178, splat (float 0x3EB0C6F7A0000000)
  %347 = select <8 x i1> %339, <8 x i1> %343, <8 x i1> zeroinitializer
  %348 = select <8 x i1> %340, <8 x i1> %344, <8 x i1> zeroinitializer
  %349 = select <8 x i1> %341, <8 x i1> %345, <8 x i1> zeroinitializer
  %350 = select <8 x i1> %342, <8 x i1> %346, <8 x i1> zeroinitializer
  %351 = select <8 x i1> %335, <8 x i1> %347, <8 x i1> zeroinitializer
  %352 = select <8 x i1> %336, <8 x i1> %348, <8 x i1> zeroinitializer
  %353 = select <8 x i1> %337, <8 x i1> %349, <8 x i1> zeroinitializer
  %354 = select <8 x i1> %338, <8 x i1> %350, <8 x i1> zeroinitializer
  %355 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather186, %wide.masked.gather178
  %356 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather187, %wide.masked.gather179
  %357 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather188, %wide.masked.gather180
  %358 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather189, %wide.masked.gather181
  %359 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather190, %wide.masked.gather182
  %360 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather191, %wide.masked.gather183
  %361 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather192, %wide.masked.gather184
  %362 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather193, %wide.masked.gather185
  %363 = fadd reassoc ninf nsz <8 x float> %359, %355
  %364 = fadd reassoc ninf nsz <8 x float> %360, %356
  %365 = fadd reassoc ninf nsz <8 x float> %361, %357
  %366 = fadd reassoc ninf nsz <8 x float> %362, %358
  %367 = fmul reassoc ninf nsz <8 x float> %175, %163
  %368 = fmul reassoc ninf nsz <8 x float> %176, %164
  %369 = fmul reassoc ninf nsz <8 x float> %177, %165
  %370 = fmul reassoc ninf nsz <8 x float> %178, %166
  %371 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %367)
  %372 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %368)
  %373 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %369)
  %374 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %370)
  %375 = fdiv reassoc ninf nsz <8 x float> %363, %371
  %376 = fdiv reassoc ninf nsz <8 x float> %364, %372
  %377 = fdiv reassoc ninf nsz <8 x float> %365, %373
  %378 = fdiv reassoc ninf nsz <8 x float> %366, %374
  %379 = fcmp reassoc ninf nsz ule <8 x float> %179, splat (float 1.500000e+02)
  %380 = fcmp reassoc ninf nsz ule <8 x float> %180, splat (float 1.500000e+02)
  %381 = fcmp reassoc ninf nsz ule <8 x float> %181, splat (float 1.500000e+02)
  %382 = fcmp reassoc ninf nsz ule <8 x float> %182, splat (float 1.500000e+02)
  %383 = fcmp reassoc ninf nsz uge <8 x float> %375, splat (float 0x3FC99999A0000000)
  %384 = fcmp reassoc ninf nsz uge <8 x float> %376, splat (float 0x3FC99999A0000000)
  %385 = fcmp reassoc ninf nsz uge <8 x float> %377, splat (float 0x3FC99999A0000000)
  %386 = fcmp reassoc ninf nsz uge <8 x float> %378, splat (float 0x3FC99999A0000000)
  %.not309 = select <8 x i1> %379, <8 x i1> splat (i1 true), <8 x i1> %383
  %.not312 = select <8 x i1> %380, <8 x i1> splat (i1 true), <8 x i1> %384
  %.not315 = select <8 x i1> %381, <8 x i1> splat (i1 true), <8 x i1> %385
  %.not318 = select <8 x i1> %382, <8 x i1> splat (i1 true), <8 x i1> %386
  %387 = select <8 x i1> %351, <8 x i1> %.not309, <8 x i1> zeroinitializer
  %388 = select <8 x i1> %352, <8 x i1> %.not312, <8 x i1> zeroinitializer
  %389 = select <8 x i1> %353, <8 x i1> %.not315, <8 x i1> zeroinitializer
  %390 = select <8 x i1> %354, <8 x i1> %.not318, <8 x i1> zeroinitializer
  %391 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %375, <8 x float> zeroinitializer)
  %392 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %376, <8 x float> zeroinitializer)
  %393 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %377, <8 x float> zeroinitializer)
  %394 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %378, <8 x float> zeroinitializer)
  %395 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %179)
  %396 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %180)
  %397 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %181)
  %398 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %182)
  %399 = fmul reassoc ninf nsz <8 x float> %395, splat (float 2.025000e+02)
  %400 = fmul reassoc ninf nsz <8 x float> %396, splat (float 2.025000e+02)
  %401 = fmul reassoc ninf nsz <8 x float> %397, splat (float 2.025000e+02)
  %402 = fmul reassoc ninf nsz <8 x float> %398, splat (float 2.025000e+02)
  %403 = fmul reassoc ninf nsz <8 x float> %399, %391
  %.fr = freeze <8 x float> %403
  %404 = fmul reassoc ninf nsz <8 x float> %400, %392
  %.fr319 = freeze <8 x float> %404
  %405 = fmul reassoc ninf nsz <8 x float> %401, %393
  %.fr320 = freeze <8 x float> %405
  %406 = fmul reassoc ninf nsz <8 x float> %402, %394
  %.fr321 = freeze <8 x float> %406
  %407 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %408 = fcmp reassoc nsz ogt <8 x float> %.fr319, splat (float 3.000000e+00)
  %409 = fcmp reassoc nsz ogt <8 x float> %.fr320, splat (float 3.000000e+00)
  %410 = fcmp reassoc nsz ogt <8 x float> %.fr321, splat (float 3.000000e+00)
  %411 = xor <8 x i1> %407, splat (i1 true)
  %412 = xor <8 x i1> %408, splat (i1 true)
  %413 = xor <8 x i1> %409, splat (i1 true)
  %414 = xor <8 x i1> %410, splat (i1 true)
  %415 = and <8 x i1> %387, %411
  %416 = and <8 x i1> %388, %412
  %417 = and <8 x i1> %389, %413
  %418 = and <8 x i1> %390, %414
  %419 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %420 = fcmp reassoc nsz olt <8 x float> %.fr319, splat (float -3.000000e+00)
  %421 = fcmp reassoc nsz olt <8 x float> %.fr320, splat (float -3.000000e+00)
  %422 = fcmp reassoc nsz olt <8 x float> %.fr321, splat (float -3.000000e+00)
  %423 = xor <8 x i1> %419, splat (i1 true)
  %424 = xor <8 x i1> %420, splat (i1 true)
  %425 = xor <8 x i1> %421, splat (i1 true)
  %426 = xor <8 x i1> %422, splat (i1 true)
  %427 = and <8 x i1> %415, %423
  %428 = and <8 x i1> %416, %424
  %429 = and <8 x i1> %417, %425
  %430 = and <8 x i1> %418, %426
  %431 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %432 = fmul reassoc ninf nsz <8 x float> %.fr319, %.fr319
  %433 = fmul reassoc ninf nsz <8 x float> %.fr320, %.fr320
  %434 = fmul reassoc ninf nsz <8 x float> %.fr321, %.fr321
  %435 = fadd reassoc ninf nsz <8 x float> %431, splat (float 2.700000e+01)
  %436 = fadd reassoc ninf nsz <8 x float> %432, splat (float 2.700000e+01)
  %437 = fadd reassoc ninf nsz <8 x float> %433, splat (float 2.700000e+01)
  %438 = fadd reassoc ninf nsz <8 x float> %434, splat (float 2.700000e+01)
  %439 = fmul reassoc ninf nsz <8 x float> %435, %.fr
  %440 = fmul reassoc ninf nsz <8 x float> %436, %.fr319
  %441 = fmul reassoc ninf nsz <8 x float> %437, %.fr320
  %442 = fmul reassoc ninf nsz <8 x float> %438, %.fr321
  %443 = fmul reassoc ninf nsz <8 x float> %431, splat (float 9.000000e+00)
  %444 = fmul reassoc ninf nsz <8 x float> %432, splat (float 9.000000e+00)
  %445 = fmul reassoc ninf nsz <8 x float> %433, splat (float 9.000000e+00)
  %446 = fmul reassoc ninf nsz <8 x float> %434, splat (float 9.000000e+00)
  %447 = fadd reassoc ninf nsz <8 x float> %443, splat (float 2.700000e+01)
  %448 = fadd reassoc ninf nsz <8 x float> %444, splat (float 2.700000e+01)
  %449 = fadd reassoc ninf nsz <8 x float> %445, splat (float 2.700000e+01)
  %450 = fadd reassoc ninf nsz <8 x float> %446, splat (float 2.700000e+01)
  %451 = fdiv reassoc ninf nsz <8 x float> %439, %447
  %452 = fdiv reassoc ninf nsz <8 x float> %440, %448
  %453 = fdiv reassoc ninf nsz <8 x float> %441, %449
  %454 = fdiv reassoc ninf nsz <8 x float> %442, %450
  %455 = fadd reassoc ninf nsz <8 x float> %451, splat (float 1.000000e+00)
  %456 = fadd reassoc ninf nsz <8 x float> %452, splat (float 1.000000e+00)
  %457 = fadd reassoc ninf nsz <8 x float> %453, splat (float 1.000000e+00)
  %458 = fadd reassoc ninf nsz <8 x float> %454, splat (float 1.000000e+00)
  %459 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %375
  %460 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %376
  %461 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %377
  %462 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %378
  %463 = fmul reassoc ninf nsz <8 x float> %459, %135
  %464 = fmul reassoc ninf nsz <8 x float> %460, %136
  %465 = fmul reassoc ninf nsz <8 x float> %461, %137
  %466 = fmul reassoc ninf nsz <8 x float> %462, %138
  %467 = and <8 x i1> %415, %419
  %468 = and <8 x i1> %416, %420
  %469 = and <8 x i1> %417, %421
  %470 = and <8 x i1> %418, %422
  %471 = and <8 x i1> %387, %407
  %472 = and <8 x i1> %388, %408
  %473 = and <8 x i1> %389, %409
  %474 = and <8 x i1> %390, %410
  %475 = xor <8 x i1> %347, splat (i1 true)
  %476 = xor <8 x i1> %348, splat (i1 true)
  %477 = xor <8 x i1> %349, splat (i1 true)
  %478 = xor <8 x i1> %350, splat (i1 true)
  %479 = select <8 x i1> %335, <8 x i1> %475, <8 x i1> zeroinitializer
  %480 = select <8 x i1> %336, <8 x i1> %476, <8 x i1> zeroinitializer
  %481 = select <8 x i1> %337, <8 x i1> %477, <8 x i1> zeroinitializer
  %482 = select <8 x i1> %338, <8 x i1> %478, <8 x i1> zeroinitializer
  %483 = xor <8 x i1> %331, splat (i1 true)
  %484 = xor <8 x i1> %332, splat (i1 true)
  %485 = xor <8 x i1> %333, splat (i1 true)
  %486 = xor <8 x i1> %334, splat (i1 true)
  %487 = select <8 x i1> %327, <8 x i1> %483, <8 x i1> zeroinitializer
  %488 = select <8 x i1> %328, <8 x i1> %484, <8 x i1> zeroinitializer
  %489 = select <8 x i1> %329, <8 x i1> %485, <8 x i1> zeroinitializer
  %490 = select <8 x i1> %330, <8 x i1> %486, <8 x i1> zeroinitializer
  %491 = select <8 x i1> %387, <8 x i1> splat (i1 true), <8 x i1> %487
  %492 = select <8 x i1> %491, <8 x i1> splat (i1 true), <8 x i1> %479
  %predphi215 = select <8 x i1> %492, <8 x float> %135, <8 x float> %463
  %493 = select <8 x i1> %388, <8 x i1> splat (i1 true), <8 x i1> %488
  %494 = select <8 x i1> %493, <8 x i1> splat (i1 true), <8 x i1> %480
  %predphi220 = select <8 x i1> %494, <8 x float> %136, <8 x float> %464
  %495 = select <8 x i1> %389, <8 x i1> splat (i1 true), <8 x i1> %489
  %496 = select <8 x i1> %495, <8 x i1> splat (i1 true), <8 x i1> %481
  %predphi225 = select <8 x i1> %496, <8 x float> %137, <8 x float> %465
  %497 = select <8 x i1> %390, <8 x i1> splat (i1 true), <8 x i1> %490
  %498 = select <8 x i1> %497, <8 x i1> splat (i1 true), <8 x i1> %482
  %predphi230 = select <8 x i1> %498, <8 x float> %138, <8 x float> %466
  %predphi233 = select <8 x i1> %471, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi234 = select <8 x i1> %427, <8 x float> %455, <8 x float> %predphi233
  %predphi235 = select <8 x i1> %467, <8 x float> zeroinitializer, <8 x float> %predphi234
  %predphi238 = select <8 x i1> %472, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi239 = select <8 x i1> %428, <8 x float> %456, <8 x float> %predphi238
  %predphi240 = select <8 x i1> %468, <8 x float> zeroinitializer, <8 x float> %predphi239
  %predphi243 = select <8 x i1> %473, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi244 = select <8 x i1> %429, <8 x float> %457, <8 x float> %predphi243
  %predphi245 = select <8 x i1> %469, <8 x float> zeroinitializer, <8 x float> %predphi244
  %predphi248 = select <8 x i1> %474, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi249 = select <8 x i1> %430, <8 x float> %458, <8 x float> %predphi248
  %predphi250 = select <8 x i1> %470, <8 x float> zeroinitializer, <8 x float> %predphi249
  %499 = fmul reassoc ninf nsz <8 x float> %predphi235, %predphi198
  %500 = fmul reassoc ninf nsz <8 x float> %predphi240, %predphi202
  %501 = fmul reassoc ninf nsz <8 x float> %predphi245, %predphi206
  %502 = fmul reassoc ninf nsz <8 x float> %predphi250, %predphi210
  %503 = fmul reassoc ninf nsz <8 x float> %499, %predphi215
  %504 = fmul reassoc ninf nsz <8 x float> %500, %predphi220
  %505 = fmul reassoc ninf nsz <8 x float> %501, %predphi225
  %506 = fmul reassoc ninf nsz <8 x float> %502, %predphi230
  %507 = fadd reassoc ninf nsz <8 x float> %503, %vec.phi165
  %508 = fadd reassoc ninf nsz <8 x float> %504, %vec.phi166
  %509 = fadd reassoc ninf nsz <8 x float> %505, %vec.phi167
  %510 = fadd reassoc ninf nsz <8 x float> %506, %vec.phi168
  %511 = fadd reassoc ninf nsz <8 x float> %499, %vec.phi161
  %512 = fadd reassoc ninf nsz <8 x float> %500, %vec.phi162
  %513 = fadd reassoc ninf nsz <8 x float> %501, %vec.phi163
  %514 = fadd reassoc ninf nsz <8 x float> %502, %vec.phi164
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %515 = icmp eq i64 %lsr.iv.next, 0
  br i1 %515, label %middle.block150, label %vector.body159, !llvm.loop !11

middle.block150:                                  ; preds = %vector.body159
  %bin.rdx252 = fadd reassoc ninf nsz <8 x float> %512, %511
  %bin.rdx253 = fadd reassoc ninf nsz <8 x float> %513, %bin.rdx252
  %bin.rdx254 = fadd reassoc ninf nsz <8 x float> %514, %bin.rdx253
  %516 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx254)
  %bin.rdx255 = fadd reassoc ninf nsz <8 x float> %508, %507
  %bin.rdx256 = fadd reassoc ninf nsz <8 x float> %509, %bin.rdx255
  %bin.rdx257 = fadd reassoc ninf nsz <8 x float> %510, %bin.rdx256
  %517 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx257)
  br i1 %cmp.n258, label %for_loop_test11.after_for10_crit_edge.us, label %vec.epilog.iter.check265

vec.epilog.iter.check265:                         ; preds = %middle.block150
  br i1 %min.epilog.iters.check267, label %for_loop_body8.us.preheader, label %vec.epilog.ph264

vec.epilog.ph264:                                 ; preds = %vec.epilog.iter.check265, %vector.main.loop.iter.check155
  %bc.resume.val259 = phi i64 [ %n.vec158, %vec.epilog.iter.check265 ], [ 0, %vector.main.loop.iter.check155 ]
  %bc.merge.rdx260 = phi float [ %516, %vec.epilog.iter.check265 ], [ %.05076.us, %vector.main.loop.iter.check155 ]
  %bc.merge.rdx261 = phi float [ %517, %vec.epilog.iter.check265 ], [ %.05275.us, %vector.main.loop.iter.check155 ]
  %518 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx260, i64 0
  %519 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx261, i64 0
  %520 = trunc nuw nsw i64 %bc.resume.val259 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %520, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %521 = add i64 %98, %bc.resume.val259
  br label %vec.epilog.vector.body272

vec.epilog.vector.body272:                        ; preds = %vec.epilog.vector.body272, %vec.epilog.ph264
  %lsr.iv375 = phi i64 [ %lsr.iv.next376, %vec.epilog.vector.body272 ], [ %521, %vec.epilog.ph264 ]
  %vec.phi274 = phi <8 x float> [ %518, %vec.epilog.ph264 ], [ %622, %vec.epilog.vector.body272 ]
  %vec.phi275 = phi <8 x float> [ %519, %vec.epilog.ph264 ], [ %621, %vec.epilog.vector.body272 ]
  %vec.ind276 = phi <8 x i32> [ %induction, %vec.epilog.ph264 ], [ %vec.ind.next277, %vec.epilog.vector.body272 ]
  %522 = shl <8 x i32> %vec.ind276, splat (i32 1)
  %523 = add <8 x i32> %broadcast.splat170, %522
  %524 = sext <8 x i32> %523 to <8 x i64>
  %525 = getelementptr float, ptr %104, <8 x i64> %524
  %wide.masked.gather280 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %525, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %526 = getelementptr float, ptr %106, <8 x i64> %524
  %wide.masked.gather281 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %526, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %527 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather280, %wide.masked.gather281
  %528 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %527)
  %529 = getelementptr float, ptr %108, <8 x i64> %524
  %wide.masked.gather282 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %529, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %530 = getelementptr float, ptr %110, <8 x i64> %524
  %wide.masked.gather283 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %530, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %531 = getelementptr float, ptr %112, <8 x i64> %524
  %wide.masked.gather284 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %531, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %532 = getelementptr float, ptr %114, <8 x i64> %524
  %wide.masked.gather285 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %532, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %533 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather282, %wide.masked.gather282
  %534 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather283, %wide.masked.gather283
  %535 = fadd reassoc ninf nsz <8 x float> %534, %533
  %536 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather284, %wide.masked.gather284
  %537 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather285, %wide.masked.gather285
  %538 = fadd reassoc ninf nsz <8 x float> %537, %536
  %539 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %535, <8 x float> %538)
  %540 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather281, splat (float -2.000000e+00)
  %541 = fadd reassoc ninf nsz <8 x float> %540, splat (float 3.000000e+00)
  %542 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %541, <8 x float> splat (float 3.000000e+00))
  %543 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %542, <8 x float> splat (float 1.000000e+00))
  %544 = fmul reassoc ninf nsz <8 x float> %543, %broadcast.splat195
  %545 = fcmp reassoc ninf nsz olt <8 x float> %539, splat (float 1.500000e+02)
  %546 = xor <8 x i1> %545, splat (i1 true)
  %547 = select <8 x i1> %broadcast.splat, <8 x i1> %546, <8 x i1> zeroinitializer
  %548 = fcmp reassoc ninf nsz olt <8 x float> %528, %544
  %549 = xor <8 x i1> %548, splat (i1 true)
  %550 = select <8 x i1> %547, <8 x i1> %549, <8 x i1> zeroinitializer
  %551 = fmul reassoc ninf nsz <8 x float> %544, splat (float 4.000000e+00)
  %552 = fdiv reassoc ninf nsz <8 x float> %528, %551
  %553 = fcmp reassoc ninf nsz ogt <8 x float> %552, splat (float 1.000000e+00)
  %554 = select <8 x i1> %553, <8 x float> splat (float 1.000000e+00), <8 x float> %552
  %555 = fmul reassoc ninf nsz <8 x float> %554, splat (float 0x3FD99999A0000000)
  %556 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %555
  %557 = select <8 x i1> %547, <8 x i1> %548, <8 x i1> zeroinitializer
  %558 = fmul reassoc ninf nsz <8 x float> %528, splat (float 0x3FC3333340000000)
  %559 = fdiv reassoc ninf nsz <8 x float> %558, %544
  %560 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %559
  %561 = select <8 x i1> %broadcast.splat, <8 x i1> %545, <8 x i1> zeroinitializer
  %562 = fmul reassoc ninf nsz <8 x float> %544, splat (float 1.500000e+00)
  %563 = fcmp reassoc ninf nsz uge <8 x float> %528, %562
  %564 = select <8 x i1> %561, <8 x i1> %563, <8 x i1> zeroinitializer
  %565 = fsub reassoc ninf nsz <8 x float> %528, %562
  %566 = fdiv reassoc ninf nsz <8 x float> %565, %562
  %567 = fcmp reassoc ninf nsz ogt <8 x float> %566, splat (float 1.000000e+00)
  %568 = select <8 x i1> %567, <8 x float> splat (float 1.000000e+00), <8 x float> %566
  %569 = fmul reassoc ninf nsz <8 x float> %568, splat (float 0x3FC99999A0000000)
  %570 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %569
  %571 = fmul reassoc ninf nsz <8 x float> %528, splat (float 0x3FEE666660000000)
  %572 = fdiv reassoc ninf nsz <8 x float> %571, %562
  %573 = fadd reassoc ninf nsz <8 x float> %572, splat (float 0x3FA99999A0000000)
  %574 = or <8 x i1> %557, %95
  %575 = or <8 x i1> %574, %561
  %576 = or <8 x i1> %575, %550
  %predphi288 = select <8 x i1> %564, <8 x float> %570, <8 x float> %573
  %predphi289 = select <8 x i1> %557, <8 x float> %560, <8 x float> %predphi288
  %predphi290 = select <8 x i1> %550, <8 x float> %556, <8 x float> %predphi289
  %predphi291 = select <8 x i1> %broadcast.splat, <8 x float> %predphi290, <8 x float> splat (float 1.000000e+00)
  %577 = fcmp reassoc ninf nsz ogt <8 x float> %539, splat (float 0x3EB0C6F7A0000000)
  %578 = select <8 x i1> %576, <8 x i1> %577, <8 x i1> zeroinitializer
  %579 = fcmp reassoc ninf nsz ogt <8 x float> %535, splat (float 0x3EB0C6F7A0000000)
  %580 = fcmp reassoc ninf nsz ogt <8 x float> %538, splat (float 0x3EB0C6F7A0000000)
  %581 = select <8 x i1> %579, <8 x i1> %580, <8 x i1> zeroinitializer
  %582 = select <8 x i1> %578, <8 x i1> %581, <8 x i1> zeroinitializer
  %583 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather284, %wide.masked.gather282
  %584 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather285, %wide.masked.gather283
  %585 = fadd reassoc ninf nsz <8 x float> %584, %583
  %586 = fmul reassoc ninf nsz <8 x float> %538, %535
  %587 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %586)
  %588 = fdiv reassoc ninf nsz <8 x float> %585, %587
  %589 = fcmp reassoc ninf nsz ule <8 x float> %539, splat (float 1.500000e+02)
  %590 = fcmp reassoc ninf nsz uge <8 x float> %588, splat (float 0x3FC99999A0000000)
  %.not324 = select <8 x i1> %589, <8 x i1> splat (i1 true), <8 x i1> %590
  %591 = select <8 x i1> %582, <8 x i1> %.not324, <8 x i1> zeroinitializer
  %592 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %588, <8 x float> zeroinitializer)
  %593 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %539)
  %594 = fmul reassoc ninf nsz <8 x float> %593, splat (float 2.025000e+02)
  %595 = fmul reassoc ninf nsz <8 x float> %594, %592
  %.fr325 = freeze <8 x float> %595
  %596 = fcmp reassoc nsz ogt <8 x float> %.fr325, splat (float 3.000000e+00)
  %597 = xor <8 x i1> %596, splat (i1 true)
  %598 = and <8 x i1> %591, %597
  %599 = fcmp reassoc nsz olt <8 x float> %.fr325, splat (float -3.000000e+00)
  %600 = xor <8 x i1> %599, splat (i1 true)
  %601 = and <8 x i1> %598, %600
  %602 = fmul reassoc ninf nsz <8 x float> %.fr325, %.fr325
  %603 = fadd reassoc ninf nsz <8 x float> %602, splat (float 2.700000e+01)
  %604 = fmul reassoc ninf nsz <8 x float> %603, %.fr325
  %605 = fmul reassoc ninf nsz <8 x float> %602, splat (float 9.000000e+00)
  %606 = fadd reassoc ninf nsz <8 x float> %605, splat (float 2.700000e+01)
  %607 = fdiv reassoc ninf nsz <8 x float> %604, %606
  %608 = fadd reassoc ninf nsz <8 x float> %607, splat (float 1.000000e+00)
  %609 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %588
  %610 = fmul reassoc ninf nsz <8 x float> %609, %528
  %611 = and <8 x i1> %598, %599
  %612 = and <8 x i1> %591, %596
  %613 = xor <8 x i1> %581, splat (i1 true)
  %614 = select <8 x i1> %578, <8 x i1> %613, <8 x i1> zeroinitializer
  %615 = xor <8 x i1> %577, splat (i1 true)
  %616 = select <8 x i1> %576, <8 x i1> %615, <8 x i1> zeroinitializer
  %617 = select <8 x i1> %591, <8 x i1> splat (i1 true), <8 x i1> %616
  %618 = select <8 x i1> %617, <8 x i1> splat (i1 true), <8 x i1> %614
  %predphi296 = select <8 x i1> %618, <8 x float> %528, <8 x float> %610
  %predphi299 = select <8 x i1> %612, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi300 = select <8 x i1> %601, <8 x float> %608, <8 x float> %predphi299
  %predphi301 = select <8 x i1> %611, <8 x float> zeroinitializer, <8 x float> %predphi300
  %619 = fmul reassoc ninf nsz <8 x float> %predphi301, %predphi291
  %620 = fmul reassoc ninf nsz <8 x float> %619, %predphi296
  %621 = fadd reassoc ninf nsz <8 x float> %620, %vec.phi275
  %622 = fadd reassoc ninf nsz <8 x float> %619, %vec.phi274
  %vec.ind.next277 = add <8 x i32> %vec.ind276, splat (i32 8)
  %lsr.iv.next376 = add i64 %lsr.iv375, 8
  %623 = icmp eq i64 %lsr.iv.next376, 0
  br i1 %623, label %vec.epilog.middle.block262, label %vec.epilog.vector.body272, !llvm.loop !14

vec.epilog.middle.block262:                       ; preds = %vec.epilog.vector.body272
  %624 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %622)
  %625 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %621)
  br i1 %cmp.n303, label %for_loop_test11.after_for10_crit_edge.us, label %for_loop_body8.us.preheader

for_loop_body8.us.preheader:                      ; preds = %vec.epilog.middle.block262, %vec.epilog.iter.check265, %iter.check153
  %indvars.iv.ph = phi i64 [ %n.vec158, %vec.epilog.iter.check265 ], [ 0, %iter.check153 ], [ %n.vec269, %vec.epilog.middle.block262 ]
  %.15172.us.ph = phi float [ %516, %vec.epilog.iter.check265 ], [ %.05076.us, %iter.check153 ], [ %624, %vec.epilog.middle.block262 ]
  %.15371.us.ph = phi float [ %517, %vec.epilog.iter.check265 ], [ %.05275.us, %iter.check153 ], [ %625, %vec.epilog.middle.block262 ]
  %626 = trunc i64 %indvars.iv.ph to i32
  %627 = shl nuw i32 %626, 1
  %628 = add i32 %54, %627
  %629 = add i64 %99, %indvars.iv.ph
  br label %for_loop_body8.us

for_loop_body8.us:                                ; preds = %after_if38.us, %for_loop_body8.us.preheader
  %lsr.iv379 = phi i64 [ %629, %for_loop_body8.us.preheader ], [ %lsr.iv.next380, %after_if38.us ]
  %lsr.iv377 = phi i32 [ %628, %for_loop_body8.us.preheader ], [ %lsr.iv.next378, %after_if38.us ]
  %.15172.us = phi float [ %705, %after_if38.us ], [ %.15172.us.ph, %for_loop_body8.us.preheader ]
  %.15371.us = phi float [ %704, %after_if38.us ], [ %.15371.us.ph, %for_loop_body8.us.preheader ]
  %630 = sext i32 %lsr.iv377 to i64
  %631 = getelementptr float, ptr %104, i64 %630
  %632 = load float, ptr %631, align 4
  %633 = getelementptr float, ptr %106, i64 %630
  %634 = load float, ptr %633, align 4
  %635 = fsub reassoc ninf nsz float %632, %634
  %636 = tail call noundef float @llvm.fabs.f32(float %635)
  %637 = getelementptr float, ptr %108, i64 %630
  %638 = load float, ptr %637, align 4
  %639 = getelementptr float, ptr %110, i64 %630
  %640 = load float, ptr %639, align 4
  %641 = getelementptr float, ptr %112, i64 %630
  %642 = load float, ptr %641, align 4
  %643 = getelementptr float, ptr %114, i64 %630
  %644 = load float, ptr %643, align 4
  %645 = fmul reassoc ninf nsz float %638, %638
  %646 = fmul reassoc ninf nsz float %640, %640
  %647 = fadd reassoc ninf nsz float %646, %645
  %648 = fmul reassoc ninf nsz float %642, %642
  %649 = fmul reassoc ninf nsz float %644, %644
  %650 = fadd reassoc ninf nsz float %649, %648
  %651 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %647, float %650)
  %factor.us = fmul reassoc ninf nsz float %634, -2.000000e+00
  %652 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %653 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %652, float 3.000000e+00)
  %654 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %653, float 1.000000e+00)
  %655 = fmul reassoc ninf nsz float %654, %51
  br i1 %52, label %true_block12.us, label %after_if14.us

true_block12.us:                                  ; preds = %for_loop_body8.us
  %656 = fcmp reassoc ninf nsz olt float %651, 1.500000e+02
  br i1 %656, label %true_block15.us, label %false_block16.us

false_block16.us:                                 ; preds = %true_block12.us
  %657 = fcmp reassoc ninf nsz olt float %636, %655
  br i1 %657, label %true_block24.us, label %false_block25.us

false_block25.us:                                 ; preds = %false_block16.us
  %658 = fmul reassoc ninf nsz float %655, 4.000000e+00
  %659 = fdiv reassoc ninf nsz float %636, %658
  %660 = fcmp reassoc ninf nsz ogt float %659, 1.000000e+00
  %spec.store.select1.us = select i1 %660, float 1.000000e+00, float %659
  %661 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %662 = fsub reassoc ninf nsz float 0x3FE6666680000000, %661
  br label %after_if14.us

true_block24.us:                                  ; preds = %false_block16.us
  %663 = fmul reassoc ninf nsz float %636, 0x3FC3333340000000
  %664 = fdiv reassoc ninf nsz float %663, %655
  %665 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %664
  br label %after_if14.us

true_block15.us:                                  ; preds = %true_block12.us
  %666 = fmul reassoc ninf nsz float %655, 1.500000e+00
  %667 = fcmp reassoc ninf nsz olt float %636, %666
  br i1 %667, label %true_block18.us, label %false_block19.us

false_block19.us:                                 ; preds = %true_block15.us
  %668 = fsub reassoc ninf nsz float %636, %666
  %669 = fdiv reassoc ninf nsz float %668, %666
  %670 = fcmp reassoc ninf nsz ogt float %669, 1.000000e+00
  %spec.store.select.us = select i1 %670, float 1.000000e+00, float %669
  %671 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %672 = fsub reassoc ninf nsz float 1.000000e+00, %671
  br label %after_if14.us

true_block18.us:                                  ; preds = %true_block15.us
  %673 = fmul reassoc ninf nsz float %636, 0x3FEE666660000000
  %674 = fdiv reassoc ninf nsz float %673, %666
  %675 = fadd reassoc ninf nsz float %674, 0x3FA99999A0000000
  br label %after_if14.us

after_if14.us:                                    ; preds = %true_block18.us, %false_block19.us, %true_block24.us, %false_block25.us, %for_loop_body8.us
  %.046.us = phi float [ %675, %true_block18.us ], [ %672, %false_block19.us ], [ %665, %true_block24.us ], [ %662, %false_block25.us ], [ 1.000000e+00, %for_loop_body8.us ]
  %676 = fcmp reassoc ninf nsz ogt float %651, 0x3EB0C6F7A0000000
  br i1 %676, label %true_block30.us, label %after_if38.us

true_block30.us:                                  ; preds = %after_if14.us
  %677 = fcmp reassoc ninf nsz ogt float %647, 0x3EB0C6F7A0000000
  %678 = fcmp reassoc ninf nsz ogt float %650, 0x3EB0C6F7A0000000
  %.041.us = select i1 %677, i1 %678, i1 false
  br i1 %.041.us, label %true_block36.us, label %after_if38.us

true_block36.us:                                  ; preds = %true_block30.us
  %679 = fmul reassoc ninf nsz float %642, %638
  %680 = fmul reassoc ninf nsz float %644, %640
  %681 = fadd reassoc ninf nsz float %680, %679
  %682 = fmul reassoc ninf nsz float %650, %647
  %683 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %682)
  %684 = fdiv reassoc ninf nsz float %681, %683
  %685 = fcmp reassoc ninf nsz ogt float %651, 1.500000e+02
  %686 = fcmp reassoc ninf nsz olt float %684, 0x3FC99999A0000000
  %.040.us = select i1 %685, i1 %686, i1 false
  br i1 %.040.us, label %true_block42.us, label %false_block43.us

false_block43.us:                                 ; preds = %true_block36.us
  %687 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %684, float 0.000000e+00)
  %688 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %651)
  %689 = fmul reassoc ninf nsz float %688, 2.025000e+02
  %690 = fmul reassoc ninf nsz float %689, %687
  %691 = fcmp reassoc ninf nsz ogt float %690, 3.000000e+00
  br i1 %691, label %after_if38.us, label %false_block46.us

false_block46.us:                                 ; preds = %false_block43.us
  %692 = fcmp reassoc ninf nsz olt float %690, -3.000000e+00
  br i1 %692, label %after_if38.us, label %false_block49.us

false_block49.us:                                 ; preds = %false_block46.us
  %693 = fmul reassoc ninf nsz float %690, %690
  %694 = fadd reassoc ninf nsz float %693, 2.700000e+01
  %695 = fmul reassoc ninf nsz float %694, %690
  %696 = fmul reassoc ninf nsz float %693, 9.000000e+00
  %697 = fadd reassoc ninf nsz float %696, 2.700000e+01
  %698 = fdiv reassoc ninf nsz float %695, %697
  %699 = fadd reassoc ninf nsz float %698, 1.000000e+00
  br label %after_if38.us

true_block42.us:                                  ; preds = %true_block36.us
  %700 = fsub reassoc ninf nsz float 1.500000e+00, %684
  %701 = fmul reassoc ninf nsz float %700, %636
  br label %after_if38.us

after_if38.us:                                    ; preds = %true_block42.us, %false_block49.us, %false_block46.us, %false_block43.us, %true_block30.us, %after_if14.us
  %.047.us = phi float [ %701, %true_block42.us ], [ %636, %true_block30.us ], [ %636, %after_if14.us ], [ %636, %false_block43.us ], [ %636, %false_block49.us ], [ %636, %false_block46.us ]
  %.043.us = phi float [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %true_block30.us ], [ 1.000000e+00, %after_if14.us ], [ 2.000000e+00, %false_block43.us ], [ %699, %false_block49.us ], [ 0.000000e+00, %false_block46.us ]
  %702 = fmul reassoc ninf nsz float %.043.us, %.046.us
  %703 = fmul reassoc ninf nsz float %702, %.047.us
  %704 = fadd reassoc ninf nsz float %703, %.15371.us
  %705 = fadd reassoc ninf nsz float %702, %.15172.us
  %lsr.iv.next378 = add i32 %lsr.iv377, 2
  %lsr.iv.next380 = add i64 %lsr.iv379, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next380, 0
  br i1 %exitcond.not, label %for_loop_test11.after_for10_crit_edge.us.loopexit, label %for_loop_body8.us, !llvm.loop !15

for_loop_test11.after_for10_crit_edge.us.loopexit: ; preds = %after_if38.us
  br label %for_loop_test11.after_for10_crit_edge.us

for_loop_test11.after_for10_crit_edge.us:         ; preds = %for_loop_test11.after_for10_crit_edge.us.loopexit, %vec.epilog.middle.block262, %middle.block150
  %.lcssa125 = phi float [ %517, %middle.block150 ], [ %625, %vec.epilog.middle.block262 ], [ %704, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %516, %middle.block150 ], [ %624, %vec.epilog.middle.block262 ], [ %705, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %indvars.iv.next96 = add nuw nsw i64 %indvars.iv95, 1
  %exitcond99.not = icmp eq i64 %indvars.iv.next96, %wide.trip.count98
  br i1 %exitcond99.not, label %after_for6, label %iter.check153

after_if3:                                        ; preds = %true_block62, %after_if53, %for_loop_body
  %.sink = phi ptr [ %.pre, %true_block62 ], [ %47, %after_if53 ], [ %47, %for_loop_body ]
  %.0.sink = phi float [ %846, %true_block62 ], [ 0.000000e+00, %after_if53 ], [ 0.000000e+00, %for_loop_body ]
  %706 = getelementptr i8, ptr %.sink, i64 104
  %707 = load ptr, ptr %706, align 8
  %708 = getelementptr i8, ptr %.sink, i64 100
  %709 = load i32, ptr %708, align 4
  %710 = sext i32 %709 to i64
  %711 = sext i32 %38 to i64
  %712 = mul nsw i64 %710, %711
  %713 = sext i32 %34 to i64
  %714 = getelementptr float, ptr %707, i64 %712
  %715 = getelementptr float, ptr %714, i64 %713
  store float %.0.sink, ptr %715, align 4
  %716 = add nsw i32 %.04488, 1
  %exitcond111.not = icmp eq i32 %716, %18
  br i1 %exitcond111.not, label %after_for.loopexit, label %for_loop_body

after_for6:                                       ; preds = %for_loop_test11.after_for10_crit_edge.us
  %717 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %717, label %for_loop_body54.lr.ph.split.us, label %false_block52

for_loop_body54.lr.ph.split.us:                   ; preds = %after_for6, %true_block1
  %718 = getelementptr i8, ptr %47, i64 20
  %719 = getelementptr i8, ptr %47, i64 24
  %720 = getelementptr i8, ptr %47, i64 4
  %721 = getelementptr i8, ptr %47, i64 8
  %722 = load ptr, ptr %721, align 8
  %723 = load i32, ptr %720, align 4
  %724 = sext i32 %723 to i64
  %725 = load ptr, ptr %719, align 8
  %726 = load i32, ptr %718, align 4
  %727 = sext i32 %726 to i64
  %smax = tail call i32 @llvm.smax.i32(i32 %44, i32 1)
  %smax108 = tail call i32 @llvm.smax.i32(i32 %42, i32 1)
  %wide.trip.count109 = zext nneg i32 %smax108 to i64
  %wide.trip.count103 = zext i32 %smax to i64
  %728 = add nsw i64 %wide.trip.count103, -1
  %min.iters.check = icmp slt i32 %44, 4
  %729 = trunc nsw i64 %728 to i32
  %730 = add i32 %40, %729
  %731 = icmp slt i32 %730, %40
  %732 = icmp ugt i64 %728, 4294967295
  %733 = or i1 %731, %732
  %min.iters.check127 = icmp slt i32 %44, 32
  %n.vec = and i64 %wide.trip.count103, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count103
  %n.vec.remaining = and i64 %wide.trip.count103, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec141 = and i64 %wide.trip.count103, 2147483644
  %cmp.n147 = icmp eq i64 %n.vec141, %wide.trip.count103
  %xtraiter = and i64 %wide.trip.count103, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %734 = lshr i64 %wide.trip.count103, 2
  %735 = mul nsw i64 %734, -4
  %736 = zext i32 %40 to i64
  %737 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test61.after_for60_crit_edge.us, %for_loop_body54.lr.ph.split.us
  %indvars.iv105 = phi i64 [ %indvars.iv.next106, %for_loop_test61.after_for60_crit_edge.us ], [ 0, %for_loop_body54.lr.ph.split.us ]
  %.03783.us = phi float [ %.lcssa126, %for_loop_test61.after_for60_crit_edge.us ], [ 0.000000e+00, %for_loop_body54.lr.ph.split.us ]
  %738 = trunc nuw nsw i64 %indvars.iv105 to i32
  %739 = add i32 %39, %738
  %740 = sext i32 %739 to i64
  %741 = mul nsw i64 %724, %740
  %742 = getelementptr float, ptr %722, i64 %741
  %743 = mul nsw i64 %727, %740
  %744 = getelementptr float, ptr %725, i64 %743
  %brmerge373 = select i1 %min.iters.check, i1 true, i1 %733
  br i1 %brmerge373, label %for_loop_body58.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %iter.check
  br i1 %min.iters.check127, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %745 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.03783.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv383 = phi i32 [ %lsr.iv.next384, %vector.body ], [ %40, %vector.ph ]
  %lsr.iv381 = phi i64 [ %lsr.iv.next382, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %745, %vector.ph ], [ %763, %vector.body ]
  %vec.phi128 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %764, %vector.body ]
  %vec.phi129 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %765, %vector.body ]
  %vec.phi130 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %766, %vector.body ]
  %746 = sext i32 %lsr.iv383 to i64
  %747 = getelementptr float, ptr %742, i64 %746
  %748 = getelementptr i8, ptr %747, i64 32
  %749 = getelementptr i8, ptr %747, i64 64
  %750 = getelementptr i8, ptr %747, i64 96
  %wide.load = load <8 x float>, ptr %747, align 4
  %wide.load131 = load <8 x float>, ptr %748, align 4
  %wide.load132 = load <8 x float>, ptr %749, align 4
  %wide.load133 = load <8 x float>, ptr %750, align 4
  %751 = getelementptr float, ptr %744, i64 %746
  %752 = getelementptr i8, ptr %751, i64 32
  %753 = getelementptr i8, ptr %751, i64 64
  %754 = getelementptr i8, ptr %751, i64 96
  %wide.load134 = load <8 x float>, ptr %751, align 4
  %wide.load135 = load <8 x float>, ptr %752, align 4
  %wide.load136 = load <8 x float>, ptr %753, align 4
  %wide.load137 = load <8 x float>, ptr %754, align 4
  %755 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load134
  %756 = fsub reassoc ninf nsz <8 x float> %wide.load131, %wide.load135
  %757 = fsub reassoc ninf nsz <8 x float> %wide.load132, %wide.load136
  %758 = fsub reassoc ninf nsz <8 x float> %wide.load133, %wide.load137
  %759 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %755)
  %760 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %756)
  %761 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %757)
  %762 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %758)
  %763 = fadd reassoc ninf nsz <8 x float> %759, %vec.phi
  %764 = fadd reassoc ninf nsz <8 x float> %760, %vec.phi128
  %765 = fadd reassoc ninf nsz <8 x float> %761, %vec.phi129
  %766 = fadd reassoc ninf nsz <8 x float> %762, %vec.phi130
  %lsr.iv.next382 = add nsw i64 %lsr.iv381, -32
  %lsr.iv.next384 = add i32 %lsr.iv383, 32
  %767 = icmp eq i64 %lsr.iv.next382, 0
  br i1 %767, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %764, %763
  %bin.rdx138 = fadd reassoc ninf nsz <8 x float> %765, %bin.rdx
  %bin.rdx139 = fadd reassoc ninf nsz <8 x float> %766, %bin.rdx138
  %768 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx139)
  br i1 %cmp.n, label %for_loop_test61.after_for60_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body58.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %768, %vec.epilog.iter.check ], [ %.03783.us, %vector.main.loop.iter.check ]
  %769 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %770 = add i64 %735, %vec.epilog.resume.val
  %771 = trunc i64 %vec.epilog.resume.val to i32
  %772 = add i32 %40, %771
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv387 = phi i32 [ %lsr.iv.next388, %vec.epilog.vector.body ], [ %772, %vec.epilog.ph ]
  %lsr.iv385 = phi i64 [ %lsr.iv.next386, %vec.epilog.vector.body ], [ %770, %vec.epilog.ph ]
  %vec.phi143 = phi <4 x float> [ %769, %vec.epilog.ph ], [ %778, %vec.epilog.vector.body ]
  %773 = sext i32 %lsr.iv387 to i64
  %774 = getelementptr float, ptr %742, i64 %773
  %wide.load144 = load <4 x float>, ptr %774, align 4
  %775 = getelementptr float, ptr %744, i64 %773
  %wide.load145 = load <4 x float>, ptr %775, align 4
  %776 = fsub reassoc ninf nsz <4 x float> %wide.load144, %wide.load145
  %777 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %776)
  %778 = fadd reassoc ninf nsz <4 x float> %777, %vec.phi143
  %lsr.iv.next386 = add i64 %lsr.iv385, 4
  %lsr.iv.next388 = add i32 %lsr.iv387, 4
  %779 = icmp eq i64 %lsr.iv.next386, 0
  br i1 %779, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %780 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %778)
  br i1 %cmp.n147, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader

for_loop_body58.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %iter.check
  %indvars.iv100.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ %n.vec141, %vec.epilog.middle.block ]
  %.181.us.ph = phi float [ %768, %vec.epilog.iter.check ], [ %.03783.us, %iter.check ], [ %780, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body58.us.prol.loopexit, label %for_loop_body58.us.prol.preheader

for_loop_body58.us.prol.preheader:                ; preds = %for_loop_body58.us.preheader
  br label %for_loop_body58.us.prol

for_loop_body58.us.prol:                          ; preds = %for_loop_body58.us.prol, %for_loop_body58.us.prol.preheader
  %lsr.iv389 = phi i64 [ %737, %for_loop_body58.us.prol.preheader ], [ %lsr.iv.next390, %for_loop_body58.us.prol ]
  %indvars.iv100.prol = phi i64 [ %indvars.iv.next101.prol, %for_loop_body58.us.prol ], [ %indvars.iv100.ph, %for_loop_body58.us.prol.preheader ]
  %.181.us.prol = phi float [ %789, %for_loop_body58.us.prol ], [ %.181.us.ph, %for_loop_body58.us.prol.preheader ]
  %781 = add i64 %736, %indvars.iv100.prol
  %tmp = trunc i64 %781 to i32
  %782 = sext i32 %tmp to i64
  %783 = getelementptr float, ptr %742, i64 %782
  %784 = load float, ptr %783, align 4
  %785 = getelementptr float, ptr %744, i64 %782
  %786 = load float, ptr %785, align 4
  %787 = fsub reassoc ninf nsz float %784, %786
  %788 = tail call noundef float @llvm.fabs.f32(float %787)
  %789 = fadd reassoc ninf nsz float %788, %.181.us.prol
  %indvars.iv.next101.prol = add nuw nsw i64 %indvars.iv100.prol, 1
  %lsr.iv.next390 = add nsw i64 %lsr.iv389, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next390, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body58.us.prol.loopexit.loopexit, label %for_loop_body58.us.prol, !llvm.loop !18

for_loop_body58.us.prol.loopexit.loopexit:        ; preds = %for_loop_body58.us.prol
  br label %for_loop_body58.us.prol.loopexit

for_loop_body58.us.prol.loopexit:                 ; preds = %for_loop_body58.us.prol.loopexit.loopexit, %for_loop_body58.us.preheader
  %.lcssa343.unr = phi float [ poison, %for_loop_body58.us.preheader ], [ %789, %for_loop_body58.us.prol.loopexit.loopexit ]
  %indvars.iv100.unr = phi i64 [ %indvars.iv100.ph, %for_loop_body58.us.preheader ], [ %indvars.iv.next101.prol, %for_loop_body58.us.prol.loopexit.loopexit ]
  %.181.us.unr = phi float [ %.181.us.ph, %for_loop_body58.us.preheader ], [ %789, %for_loop_body58.us.prol.loopexit.loopexit ]
  %790 = sub nsw i64 %indvars.iv100.ph, %wide.trip.count103
  %791 = icmp ugt i64 %790, -4
  br i1 %791, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader374

for_loop_body58.us.preheader374:                  ; preds = %for_loop_body58.us.prol.loopexit
  br label %for_loop_body58.us

for_loop_body58.us:                               ; preds = %for_loop_body58.us, %for_loop_body58.us.preheader374
  %indvars.iv100 = phi i64 [ %indvars.iv.next101.3, %for_loop_body58.us ], [ %indvars.iv100.unr, %for_loop_body58.us.preheader374 ]
  %.181.us = phi float [ %827, %for_loop_body58.us ], [ %.181.us.unr, %for_loop_body58.us.preheader374 ]
  %792 = add i64 %736, %indvars.iv100
  %tmp394 = trunc i64 %792 to i32
  %793 = sext i32 %tmp394 to i64
  %794 = getelementptr float, ptr %742, i64 %793
  %795 = load float, ptr %794, align 4
  %796 = getelementptr float, ptr %744, i64 %793
  %797 = load float, ptr %796, align 4
  %798 = fsub reassoc ninf nsz float %795, %797
  %799 = tail call noundef float @llvm.fabs.f32(float %798)
  %800 = fadd reassoc ninf nsz float %799, %.181.us
  %801 = add i64 %792, 1
  %tmp393 = trunc i64 %801 to i32
  %802 = sext i32 %tmp393 to i64
  %803 = getelementptr float, ptr %742, i64 %802
  %804 = load float, ptr %803, align 4
  %805 = getelementptr float, ptr %744, i64 %802
  %806 = load float, ptr %805, align 4
  %807 = fsub reassoc ninf nsz float %804, %806
  %808 = tail call noundef float @llvm.fabs.f32(float %807)
  %809 = fadd reassoc ninf nsz float %808, %800
  %810 = add i64 %792, 2
  %tmp392 = trunc i64 %810 to i32
  %811 = sext i32 %tmp392 to i64
  %812 = getelementptr float, ptr %742, i64 %811
  %813 = load float, ptr %812, align 4
  %814 = getelementptr float, ptr %744, i64 %811
  %815 = load float, ptr %814, align 4
  %816 = fsub reassoc ninf nsz float %813, %815
  %817 = tail call noundef float @llvm.fabs.f32(float %816)
  %818 = fadd reassoc ninf nsz float %817, %809
  %819 = add i64 %792, 3
  %tmp391 = trunc i64 %819 to i32
  %820 = sext i32 %tmp391 to i64
  %821 = getelementptr float, ptr %742, i64 %820
  %822 = load float, ptr %821, align 4
  %823 = getelementptr float, ptr %744, i64 %820
  %824 = load float, ptr %823, align 4
  %825 = fsub reassoc ninf nsz float %822, %824
  %826 = tail call noundef float @llvm.fabs.f32(float %825)
  %827 = fadd reassoc ninf nsz float %826, %818
  %indvars.iv.next101.3 = add nuw nsw i64 %indvars.iv100, 4
  %exitcond104.not.3 = icmp eq i64 %wide.trip.count103, %indvars.iv.next101.3
  br i1 %exitcond104.not.3, label %for_loop_test61.after_for60_crit_edge.us.loopexit, label %for_loop_body58.us, !llvm.loop !20

for_loop_test61.after_for60_crit_edge.us.loopexit: ; preds = %for_loop_body58.us
  br label %for_loop_test61.after_for60_crit_edge.us

for_loop_test61.after_for60_crit_edge.us:         ; preds = %for_loop_test61.after_for60_crit_edge.us.loopexit, %for_loop_body58.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa126 = phi float [ %768, %middle.block ], [ %780, %vec.epilog.middle.block ], [ %.lcssa343.unr, %for_loop_body58.us.prol.loopexit ], [ %827, %for_loop_test61.after_for60_crit_edge.us.loopexit ]
  %indvars.iv.next106 = add nuw nsw i64 %indvars.iv105, 1
  %exitcond110.not = icmp eq i64 %indvars.iv.next106, %wide.trip.count109
  br i1 %exitcond110.not, label %after_for56, label %iter.check

false_block52:                                    ; preds = %after_for6
  %828 = fdiv reassoc ninf nsz float %.lcssa125, %.lcssa
  br label %after_if53

after_if53:                                       ; preds = %after_for56, %false_block52
  %.038 = phi float [ %842, %after_for56 ], [ %828, %false_block52 ]
  %829 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %49, float 0x3EB0C6F7A0000000)
  %830 = fdiv reassoc ninf nsz float %.038, %829
  %831 = getelementptr i8, ptr %47, i64 136
  %832 = load float, ptr %831, align 4
  %833 = fsub reassoc ninf nsz float %830, %832
  %834 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %833, float 0.000000e+00)
  %835 = getelementptr i8, ptr %47, i64 132
  %836 = load float, ptr %835, align 4
  %837 = fmul reassoc ninf nsz float %836, 5.000000e-01
  %838 = fmul reassoc ninf nsz float %837, %834
  %839 = fcmp reassoc ninf nsz ugt float %838, 2.000000e+01
  br i1 %839, label %after_if3, label %true_block62

after_for56:                                      ; preds = %for_loop_test61.after_for60_crit_edge.us
  %840 = mul i32 %42, %44
  %841 = sitofp i32 %840 to float
  %842 = fdiv reassoc ninf nsz float %.lcssa126, %841
  br label %after_if53

true_block62:                                     ; preds = %after_if53
  %843 = fadd reassoc ninf nsz float %838, -2.000000e+00
  %844 = tail call noundef float @expf(float noundef %843) #9
  %845 = fadd reassoc ninf nsz float %844, 1.000000e+00
  %846 = fdiv reassoc ninf nsz float 1.000000e+00, %845
  %.pre = load ptr, ptr %0, align 8
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #2

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.4, align 8
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #9
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #9
  %14 = add i32 %.02040, 1
  %15 = icmp slt i32 %14, %.sroa.speculated28
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !21

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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #9
  %.not24.not = icmp sgt i32 %.0, %.sroa.speculated
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !23

.loopexit.loopexit:                               ; preds = %.lr.ph41
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %16, %9, %7
  %.not25 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not25, label %21, label %20

20:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #9
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <4 x float> @llvm.fabs.v4f32(<4 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.minnum.v8f32(<8 x float>, <8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.maxnum.v8f32(<8 x float>, <8 x float>) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.sqrt.v8f32(<8 x float>) #6

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #8 = { nocallback nofree nosync nounwind willreturn memory(read) }
attributes #9 = { nounwind }

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
!14 = distinct !{!14, !12, !13}
!15 = distinct !{!15, !12}
!16 = distinct !{!16, !12, !13}
!17 = distinct !{!17, !12, !13}
!18 = distinct !{!18, !19}
!19 = !{!"llvm.loop.unroll.disable"}
!20 = distinct !{!20, !12}
!21 = distinct !{!21, !22}
!22 = !{!"llvm.loop.mustprogress"}
!23 = distinct !{!23, !22}
