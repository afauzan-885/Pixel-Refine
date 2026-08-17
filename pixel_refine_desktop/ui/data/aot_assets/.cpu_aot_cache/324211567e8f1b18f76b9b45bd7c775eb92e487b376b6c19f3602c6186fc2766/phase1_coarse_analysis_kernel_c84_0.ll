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
  %.04490 = phi i32 [ %806, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = srem i32 %.04490, %33
  %35 = sdiv i32 %.04490, %33
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
  %50 = add nsw i32 %42, -1
  %51 = lshr i32 %50, 1
  %52 = add i32 %39, 1
  %53 = add i32 %40, 1
  %54 = fmul reassoc ninf nsz float %49, 0x3FC99999A0000000
  %55 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %54, float 0x3F747AE140000000)
  %56 = fcmp reassoc ninf nsz ogt float %49, 0x3EB0C6F7A0000000
  %.not = icmp samesign ult i32 %42, 3
  %.not91 = icmp samesign ult i32 %44, 3
  %or.cond = select i1 %.not, i1 true, i1 %.not91
  br i1 %or.cond, label %for_loop_body54.lr.ph.split.us, label %for_loop_body4.lr.ph.split.us

for_loop_body4.lr.ph.split.us:                    ; preds = %true_block1
  %57 = add nsw i32 %44, -1
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
  %73 = load ptr, ptr %68, align 8
  %74 = load i32, ptr %67, align 4
  %75 = load ptr, ptr %66, align 8
  %76 = load i32, ptr %65, align 4
  %77 = load ptr, ptr %64, align 8
  %78 = load i32, ptr %63, align 4
  %79 = load ptr, ptr %62, align 8
  %80 = load i32, ptr %61, align 4
  %81 = load ptr, ptr %60, align 8
  %82 = load i32, ptr %59, align 4
  %wide.trip.count = zext i32 %58 to i64
  %83 = add nsw i64 %wide.trip.count, -1
  %84 = mul i32 %72, %52
  %85 = add i32 %53, %84
  %86 = shl i32 %72, 1
  %87 = mul i32 %74, %52
  %88 = add i32 %53, %87
  %89 = shl i32 %74, 1
  %90 = mul i32 %76, %52
  %91 = add i32 %53, %90
  %92 = shl i32 %76, 1
  %93 = mul i32 %78, %52
  %94 = add i32 %53, %93
  %95 = shl i32 %78, 1
  %96 = mul i32 %80, %52
  %97 = add i32 %53, %96
  %98 = shl i32 %80, 1
  %99 = mul i32 %82, %52
  %100 = add i32 %53, %99
  %101 = shl i32 %82, 1
  %min.iters.check157 = icmp ult i32 %44, 17
  %102 = trunc nsw i64 %83 to i32
  %mul.result = shl i32 %102, 1
  %invariant.op397 = add i32 %85, %mul.result
  %invariant.op399 = add i32 %88, %mul.result
  %103 = icmp ugt i64 %83, 4294967295
  %invariant.op401 = add i32 %91, %mul.result
  %invariant.op403 = add i32 %94, %mul.result
  %invariant.op405 = add i32 %97, %mul.result
  %invariant.op407 = add i32 %100, %mul.result
  %min.iters.check160 = icmp ult i32 %44, 65
  %n.vec164 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %56, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %104 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert175 = insertelement <8 x i32> poison, i32 %53, i64 0
  %broadcast.splat176 = shufflevector <8 x i32> %broadcast.splatinsert175, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert212 = insertelement <8 x float> poison, float %55, i64 0
  %broadcast.splat213 = shufflevector <8 x float> %broadcast.splatinsert212, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat176
  %invariant.op393 = add <8 x i32> splat (i32 32), %broadcast.splat176
  %invariant.op395 = add <8 x i32> splat (i32 48), %broadcast.splat176
  %cmp.n276 = icmp eq i64 %n.vec164, %wide.trip.count
  %n.vec.remaining284 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check285 = icmp eq i64 %n.vec.remaining284, 0
  %n.vec287 = and i64 %wide.trip.count, 2147483640
  %cmp.n333 = icmp eq i64 %n.vec287, %wide.trip.count
  %105 = zext i32 %57 to i64
  %106 = lshr i64 %105, 4
  %107 = mul nsw i64 %106, -8
  %108 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check159

iter.check159:                                    ; preds = %for_loop_test11.after_for10_crit_edge.us, %for_loop_body4.lr.ph.split.us
  %lsr.iv441 = phi i32 [ %lsr.iv.next442, %for_loop_test11.after_for10_crit_edge.us ], [ %85, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv437 = phi i32 [ %lsr.iv.next438, %for_loop_test11.after_for10_crit_edge.us ], [ %88, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv433 = phi i32 [ %lsr.iv.next434, %for_loop_test11.after_for10_crit_edge.us ], [ %91, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv429 = phi i32 [ %lsr.iv.next430, %for_loop_test11.after_for10_crit_edge.us ], [ %94, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv425 = phi i32 [ %lsr.iv.next426, %for_loop_test11.after_for10_crit_edge.us ], [ %97, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv421 = phi i32 [ %lsr.iv.next422, %for_loop_test11.after_for10_crit_edge.us ], [ %100, %for_loop_body4.lr.ph.split.us ]
  %.04977.us = phi i32 [ 0, %for_loop_body4.lr.ph.split.us ], [ %797, %for_loop_test11.after_for10_crit_edge.us ]
  %.05076.us = phi float [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ], [ %.lcssa, %for_loop_test11.after_for10_crit_edge.us ]
  %.05275.us = phi float [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ], [ %.lcssa116, %for_loop_test11.after_for10_crit_edge.us ]
  %109 = shl nuw i32 %.04977.us, 1
  %110 = add i32 %52, %109
  %111 = mul i32 %72, %110
  %112 = mul i32 %74, %110
  %113 = mul i32 %76, %110
  %114 = mul i32 %78, %110
  %115 = mul i32 %80, %110
  %116 = mul i32 %82, %110
  br i1 %min.iters.check157, label %for_loop_body8.us.preheader, label %vector.scevcheck140

vector.scevcheck140:                              ; preds = %iter.check159
  %117 = mul i32 %101, %.04977.us
  %118 = add i32 %100, %117
  %119 = mul i32 %98, %.04977.us
  %120 = add i32 %97, %119
  %121 = mul i32 %95, %.04977.us
  %122 = add i32 %94, %121
  %123 = mul i32 %92, %.04977.us
  %124 = add i32 %91, %123
  %125 = mul i32 %89, %.04977.us
  %126 = add i32 %88, %125
  %127 = mul i32 %86, %.04977.us
  %128 = add i32 %85, %127
  %.reass398 = add i32 %127, %invariant.op397
  %129 = icmp slt i32 %.reass398, %128
  %.reass400 = add i32 %125, %invariant.op399
  %130 = icmp slt i32 %.reass400, %126
  %131 = or i1 %130, %103
  %.reass402 = add i32 %123, %invariant.op401
  %132 = icmp slt i32 %.reass402, %124
  %.reass404 = add i32 %121, %invariant.op403
  %133 = icmp slt i32 %.reass404, %122
  %.reass406 = add i32 %119, %invariant.op405
  %134 = icmp slt i32 %.reass406, %120
  %.reass408 = add i32 %117, %invariant.op407
  %135 = icmp slt i32 %.reass408, %118
  %136 = or i1 %129, %131
  %137 = or i1 %132, %136
  %138 = or i1 %133, %137
  %139 = or i1 %134, %138
  %140 = or i1 %135, %139
  br i1 %140, label %for_loop_body8.us.preheader, label %vector.main.loop.iter.check161

vector.main.loop.iter.check161:                   ; preds = %vector.scevcheck140
  br i1 %min.iters.check160, label %vec.epilog.ph282, label %vector.ph162

vector.ph162:                                     ; preds = %vector.main.loop.iter.check161
  %141 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05076.us, i64 0
  %142 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05275.us, i64 0
  %broadcast.splatinsert177 = insertelement <8 x i32> poison, i32 %111, i64 0
  %broadcast.splat178 = shufflevector <8 x i32> %broadcast.splatinsert177, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert182 = insertelement <8 x i32> poison, i32 %112, i64 0
  %broadcast.splat183 = shufflevector <8 x i32> %broadcast.splatinsert182, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert188 = insertelement <8 x i32> poison, i32 %113, i64 0
  %broadcast.splat189 = shufflevector <8 x i32> %broadcast.splatinsert188, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert194 = insertelement <8 x i32> poison, i32 %114, i64 0
  %broadcast.splat195 = shufflevector <8 x i32> %broadcast.splatinsert194, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert200 = insertelement <8 x i32> poison, i32 %115, i64 0
  %broadcast.splat201 = shufflevector <8 x i32> %broadcast.splatinsert200, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert206 = insertelement <8 x i32> poison, i32 %116, i64 0
  %broadcast.splat207 = shufflevector <8 x i32> %broadcast.splatinsert206, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body165

vector.body165:                                   ; preds = %vector.body165, %vector.ph162
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body165 ], [ %n.vec164, %vector.ph162 ]
  %vec.phi167 = phi <8 x float> [ %141, %vector.ph162 ], [ %581, %vector.body165 ]
  %vec.phi168 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %582, %vector.body165 ]
  %vec.phi169 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %583, %vector.body165 ]
  %vec.phi170 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %584, %vector.body165 ]
  %vec.phi171 = phi <8 x float> [ %142, %vector.ph162 ], [ %577, %vector.body165 ]
  %vec.phi172 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %578, %vector.body165 ]
  %vec.phi173 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %579, %vector.body165 ]
  %vec.phi174 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %580, %vector.body165 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph162 ], [ %vec.ind.next, %vector.body165 ]
  %143 = shl <8 x i32> %vec.ind, splat (i32 1)
  %144 = add <8 x i32> %broadcast.splat176, %143
  %.reass = add <8 x i32> %143, %invariant.op
  %.reass394 = add <8 x i32> %143, %invariant.op393
  %.reass396 = add <8 x i32> %143, %invariant.op395
  %145 = add <8 x i32> %broadcast.splat178, %144
  %146 = add <8 x i32> %broadcast.splat178, %.reass
  %147 = add <8 x i32> %broadcast.splat178, %.reass394
  %148 = add <8 x i32> %broadcast.splat178, %.reass396
  %149 = sext <8 x i32> %145 to <8 x i64>
  %150 = sext <8 x i32> %146 to <8 x i64>
  %151 = sext <8 x i32> %147 to <8 x i64>
  %152 = sext <8 x i32> %148 to <8 x i64>
  %153 = getelementptr float, ptr %71, <8 x i64> %149
  %154 = getelementptr float, ptr %71, <8 x i64> %150
  %155 = getelementptr float, ptr %71, <8 x i64> %151
  %156 = getelementptr float, ptr %71, <8 x i64> %152
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %153, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather179 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %154, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather180 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %155, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather181 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %156, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %157 = add <8 x i32> %broadcast.splat183, %144
  %158 = add <8 x i32> %broadcast.splat183, %.reass
  %159 = add <8 x i32> %broadcast.splat183, %.reass394
  %160 = add <8 x i32> %broadcast.splat183, %.reass396
  %161 = sext <8 x i32> %157 to <8 x i64>
  %162 = sext <8 x i32> %158 to <8 x i64>
  %163 = sext <8 x i32> %159 to <8 x i64>
  %164 = sext <8 x i32> %160 to <8 x i64>
  %165 = getelementptr float, ptr %73, <8 x i64> %161
  %166 = getelementptr float, ptr %73, <8 x i64> %162
  %167 = getelementptr float, ptr %73, <8 x i64> %163
  %168 = getelementptr float, ptr %73, <8 x i64> %164
  %wide.masked.gather184 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %165, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather185 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %166, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather186 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %167, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather187 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %168, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %169 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather184
  %170 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather179, %wide.masked.gather185
  %171 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather180, %wide.masked.gather186
  %172 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather181, %wide.masked.gather187
  %173 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %169)
  %174 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %170)
  %175 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %171)
  %176 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %172)
  %177 = add <8 x i32> %broadcast.splat189, %144
  %178 = add <8 x i32> %broadcast.splat189, %.reass
  %179 = add <8 x i32> %broadcast.splat189, %.reass394
  %180 = add <8 x i32> %broadcast.splat189, %.reass396
  %181 = sext <8 x i32> %177 to <8 x i64>
  %182 = sext <8 x i32> %178 to <8 x i64>
  %183 = sext <8 x i32> %179 to <8 x i64>
  %184 = sext <8 x i32> %180 to <8 x i64>
  %185 = getelementptr float, ptr %75, <8 x i64> %181
  %186 = getelementptr float, ptr %75, <8 x i64> %182
  %187 = getelementptr float, ptr %75, <8 x i64> %183
  %188 = getelementptr float, ptr %75, <8 x i64> %184
  %wide.masked.gather190 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %185, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather191 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %186, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather192 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %187, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather193 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %188, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %189 = add <8 x i32> %broadcast.splat195, %144
  %190 = add <8 x i32> %broadcast.splat195, %.reass
  %191 = add <8 x i32> %broadcast.splat195, %.reass394
  %192 = add <8 x i32> %broadcast.splat195, %.reass396
  %193 = sext <8 x i32> %189 to <8 x i64>
  %194 = sext <8 x i32> %190 to <8 x i64>
  %195 = sext <8 x i32> %191 to <8 x i64>
  %196 = sext <8 x i32> %192 to <8 x i64>
  %197 = getelementptr float, ptr %77, <8 x i64> %193
  %198 = getelementptr float, ptr %77, <8 x i64> %194
  %199 = getelementptr float, ptr %77, <8 x i64> %195
  %200 = getelementptr float, ptr %77, <8 x i64> %196
  %wide.masked.gather196 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %197, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather197 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %198, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather198 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %199, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather199 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %200, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %201 = add <8 x i32> %broadcast.splat201, %144
  %202 = add <8 x i32> %broadcast.splat201, %.reass
  %203 = add <8 x i32> %broadcast.splat201, %.reass394
  %204 = add <8 x i32> %broadcast.splat201, %.reass396
  %205 = sext <8 x i32> %201 to <8 x i64>
  %206 = sext <8 x i32> %202 to <8 x i64>
  %207 = sext <8 x i32> %203 to <8 x i64>
  %208 = sext <8 x i32> %204 to <8 x i64>
  %209 = getelementptr float, ptr %79, <8 x i64> %205
  %210 = getelementptr float, ptr %79, <8 x i64> %206
  %211 = getelementptr float, ptr %79, <8 x i64> %207
  %212 = getelementptr float, ptr %79, <8 x i64> %208
  %wide.masked.gather202 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %209, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather203 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %210, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather204 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %211, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather205 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %212, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %213 = add <8 x i32> %broadcast.splat207, %144
  %214 = add <8 x i32> %broadcast.splat207, %.reass
  %215 = add <8 x i32> %broadcast.splat207, %.reass394
  %216 = add <8 x i32> %broadcast.splat207, %.reass396
  %217 = sext <8 x i32> %213 to <8 x i64>
  %218 = sext <8 x i32> %214 to <8 x i64>
  %219 = sext <8 x i32> %215 to <8 x i64>
  %220 = sext <8 x i32> %216 to <8 x i64>
  %221 = getelementptr float, ptr %81, <8 x i64> %217
  %222 = getelementptr float, ptr %81, <8 x i64> %218
  %223 = getelementptr float, ptr %81, <8 x i64> %219
  %224 = getelementptr float, ptr %81, <8 x i64> %220
  %wide.masked.gather208 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %221, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather209 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %222, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather210 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %223, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather211 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %224, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %225 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather190, %wide.masked.gather190
  %226 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather191, %wide.masked.gather191
  %227 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather192, %wide.masked.gather192
  %228 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather193, %wide.masked.gather193
  %229 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather196, %wide.masked.gather196
  %230 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather197, %wide.masked.gather197
  %231 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather198, %wide.masked.gather198
  %232 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather199, %wide.masked.gather199
  %233 = fadd reassoc ninf nsz <8 x float> %229, %225
  %234 = fadd reassoc ninf nsz <8 x float> %230, %226
  %235 = fadd reassoc ninf nsz <8 x float> %231, %227
  %236 = fadd reassoc ninf nsz <8 x float> %232, %228
  %237 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, %wide.masked.gather202
  %238 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, %wide.masked.gather203
  %239 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, %wide.masked.gather204
  %240 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather205, %wide.masked.gather205
  %241 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather208, %wide.masked.gather208
  %242 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather209, %wide.masked.gather209
  %243 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather210, %wide.masked.gather210
  %244 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather211, %wide.masked.gather211
  %245 = fadd reassoc ninf nsz <8 x float> %241, %237
  %246 = fadd reassoc ninf nsz <8 x float> %242, %238
  %247 = fadd reassoc ninf nsz <8 x float> %243, %239
  %248 = fadd reassoc ninf nsz <8 x float> %244, %240
  %249 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %233, <8 x float> %245)
  %250 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %234, <8 x float> %246)
  %251 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %235, <8 x float> %247)
  %252 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %236, <8 x float> %248)
  %253 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather184, splat (float -2.000000e+00)
  %254 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather185, splat (float -2.000000e+00)
  %255 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather186, splat (float -2.000000e+00)
  %256 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather187, splat (float -2.000000e+00)
  %257 = fadd reassoc ninf nsz <8 x float> %253, splat (float 3.000000e+00)
  %258 = fadd reassoc ninf nsz <8 x float> %254, splat (float 3.000000e+00)
  %259 = fadd reassoc ninf nsz <8 x float> %255, splat (float 3.000000e+00)
  %260 = fadd reassoc ninf nsz <8 x float> %256, splat (float 3.000000e+00)
  %261 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %257, <8 x float> splat (float 3.000000e+00))
  %262 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %258, <8 x float> splat (float 3.000000e+00))
  %263 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %259, <8 x float> splat (float 3.000000e+00))
  %264 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %260, <8 x float> splat (float 3.000000e+00))
  %265 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %261, <8 x float> splat (float 1.000000e+00))
  %266 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %262, <8 x float> splat (float 1.000000e+00))
  %267 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %263, <8 x float> splat (float 1.000000e+00))
  %268 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %264, <8 x float> splat (float 1.000000e+00))
  %269 = fmul reassoc ninf nsz <8 x float> %265, %broadcast.splat213
  %270 = fmul reassoc ninf nsz <8 x float> %266, %broadcast.splat213
  %271 = fmul reassoc ninf nsz <8 x float> %267, %broadcast.splat213
  %272 = fmul reassoc ninf nsz <8 x float> %268, %broadcast.splat213
  %273 = fcmp reassoc ninf nsz olt <8 x float> %249, splat (float 1.500000e+02)
  %274 = fcmp reassoc ninf nsz olt <8 x float> %250, splat (float 1.500000e+02)
  %275 = fcmp reassoc ninf nsz olt <8 x float> %251, splat (float 1.500000e+02)
  %276 = fcmp reassoc ninf nsz olt <8 x float> %252, splat (float 1.500000e+02)
  %277 = xor <8 x i1> %273, splat (i1 true)
  %278 = xor <8 x i1> %274, splat (i1 true)
  %279 = xor <8 x i1> %275, splat (i1 true)
  %280 = xor <8 x i1> %276, splat (i1 true)
  %281 = select <8 x i1> %broadcast.splat, <8 x i1> %277, <8 x i1> zeroinitializer
  %282 = select <8 x i1> %broadcast.splat, <8 x i1> %278, <8 x i1> zeroinitializer
  %283 = select <8 x i1> %broadcast.splat, <8 x i1> %279, <8 x i1> zeroinitializer
  %284 = select <8 x i1> %broadcast.splat, <8 x i1> %280, <8 x i1> zeroinitializer
  %285 = fcmp reassoc ninf nsz olt <8 x float> %173, %269
  %286 = fcmp reassoc ninf nsz olt <8 x float> %174, %270
  %287 = fcmp reassoc ninf nsz olt <8 x float> %175, %271
  %288 = fcmp reassoc ninf nsz olt <8 x float> %176, %272
  %289 = xor <8 x i1> %285, splat (i1 true)
  %290 = xor <8 x i1> %286, splat (i1 true)
  %291 = xor <8 x i1> %287, splat (i1 true)
  %292 = xor <8 x i1> %288, splat (i1 true)
  %293 = select <8 x i1> %281, <8 x i1> %289, <8 x i1> zeroinitializer
  %294 = select <8 x i1> %282, <8 x i1> %290, <8 x i1> zeroinitializer
  %295 = select <8 x i1> %283, <8 x i1> %291, <8 x i1> zeroinitializer
  %296 = select <8 x i1> %284, <8 x i1> %292, <8 x i1> zeroinitializer
  %297 = fmul reassoc ninf nsz <8 x float> %269, splat (float 4.000000e+00)
  %298 = fmul reassoc ninf nsz <8 x float> %270, splat (float 4.000000e+00)
  %299 = fmul reassoc ninf nsz <8 x float> %271, splat (float 4.000000e+00)
  %300 = fmul reassoc ninf nsz <8 x float> %272, splat (float 4.000000e+00)
  %301 = fdiv reassoc ninf nsz <8 x float> %173, %297
  %302 = fdiv reassoc ninf nsz <8 x float> %174, %298
  %303 = fdiv reassoc ninf nsz <8 x float> %175, %299
  %304 = fdiv reassoc ninf nsz <8 x float> %176, %300
  %305 = fcmp reassoc ninf nsz ogt <8 x float> %301, splat (float 1.000000e+00)
  %306 = fcmp reassoc ninf nsz ogt <8 x float> %302, splat (float 1.000000e+00)
  %307 = fcmp reassoc ninf nsz ogt <8 x float> %303, splat (float 1.000000e+00)
  %308 = fcmp reassoc ninf nsz ogt <8 x float> %304, splat (float 1.000000e+00)
  %309 = select <8 x i1> %305, <8 x float> splat (float 1.000000e+00), <8 x float> %301
  %310 = select <8 x i1> %306, <8 x float> splat (float 1.000000e+00), <8 x float> %302
  %311 = select <8 x i1> %307, <8 x float> splat (float 1.000000e+00), <8 x float> %303
  %312 = select <8 x i1> %308, <8 x float> splat (float 1.000000e+00), <8 x float> %304
  %313 = fmul reassoc ninf nsz <8 x float> %309, splat (float 0x3FD99999A0000000)
  %314 = fmul reassoc ninf nsz <8 x float> %310, splat (float 0x3FD99999A0000000)
  %315 = fmul reassoc ninf nsz <8 x float> %311, splat (float 0x3FD99999A0000000)
  %316 = fmul reassoc ninf nsz <8 x float> %312, splat (float 0x3FD99999A0000000)
  %317 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %313
  %318 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %314
  %319 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %315
  %320 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %316
  %321 = select <8 x i1> %281, <8 x i1> %285, <8 x i1> zeroinitializer
  %322 = select <8 x i1> %282, <8 x i1> %286, <8 x i1> zeroinitializer
  %323 = select <8 x i1> %283, <8 x i1> %287, <8 x i1> zeroinitializer
  %324 = select <8 x i1> %284, <8 x i1> %288, <8 x i1> zeroinitializer
  %325 = fmul reassoc ninf nsz <8 x float> %173, splat (float 0x3FC3333340000000)
  %326 = fmul reassoc ninf nsz <8 x float> %174, splat (float 0x3FC3333340000000)
  %327 = fmul reassoc ninf nsz <8 x float> %175, splat (float 0x3FC3333340000000)
  %328 = fmul reassoc ninf nsz <8 x float> %176, splat (float 0x3FC3333340000000)
  %329 = fdiv reassoc ninf nsz <8 x float> %325, %269
  %330 = fdiv reassoc ninf nsz <8 x float> %326, %270
  %331 = fdiv reassoc ninf nsz <8 x float> %327, %271
  %332 = fdiv reassoc ninf nsz <8 x float> %328, %272
  %333 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %329
  %334 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %330
  %335 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %331
  %336 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %332
  %337 = select <8 x i1> %broadcast.splat, <8 x i1> %273, <8 x i1> zeroinitializer
  %338 = select <8 x i1> %broadcast.splat, <8 x i1> %274, <8 x i1> zeroinitializer
  %339 = select <8 x i1> %broadcast.splat, <8 x i1> %275, <8 x i1> zeroinitializer
  %340 = select <8 x i1> %broadcast.splat, <8 x i1> %276, <8 x i1> zeroinitializer
  %341 = fmul reassoc ninf nsz <8 x float> %269, splat (float 1.500000e+00)
  %342 = fmul reassoc ninf nsz <8 x float> %270, splat (float 1.500000e+00)
  %343 = fmul reassoc ninf nsz <8 x float> %271, splat (float 1.500000e+00)
  %344 = fmul reassoc ninf nsz <8 x float> %272, splat (float 1.500000e+00)
  %345 = fcmp reassoc ninf nsz uge <8 x float> %173, %341
  %346 = fcmp reassoc ninf nsz uge <8 x float> %174, %342
  %347 = fcmp reassoc ninf nsz uge <8 x float> %175, %343
  %348 = fcmp reassoc ninf nsz uge <8 x float> %176, %344
  %349 = select <8 x i1> %337, <8 x i1> %345, <8 x i1> zeroinitializer
  %350 = select <8 x i1> %338, <8 x i1> %346, <8 x i1> zeroinitializer
  %351 = select <8 x i1> %339, <8 x i1> %347, <8 x i1> zeroinitializer
  %352 = select <8 x i1> %340, <8 x i1> %348, <8 x i1> zeroinitializer
  %353 = fsub reassoc ninf nsz <8 x float> %173, %341
  %354 = fsub reassoc ninf nsz <8 x float> %174, %342
  %355 = fsub reassoc ninf nsz <8 x float> %175, %343
  %356 = fsub reassoc ninf nsz <8 x float> %176, %344
  %357 = fdiv reassoc ninf nsz <8 x float> %353, %341
  %358 = fdiv reassoc ninf nsz <8 x float> %354, %342
  %359 = fdiv reassoc ninf nsz <8 x float> %355, %343
  %360 = fdiv reassoc ninf nsz <8 x float> %356, %344
  %361 = fcmp reassoc ninf nsz ogt <8 x float> %357, splat (float 1.000000e+00)
  %362 = fcmp reassoc ninf nsz ogt <8 x float> %358, splat (float 1.000000e+00)
  %363 = fcmp reassoc ninf nsz ogt <8 x float> %359, splat (float 1.000000e+00)
  %364 = fcmp reassoc ninf nsz ogt <8 x float> %360, splat (float 1.000000e+00)
  %365 = select <8 x i1> %361, <8 x float> splat (float 1.000000e+00), <8 x float> %357
  %366 = select <8 x i1> %362, <8 x float> splat (float 1.000000e+00), <8 x float> %358
  %367 = select <8 x i1> %363, <8 x float> splat (float 1.000000e+00), <8 x float> %359
  %368 = select <8 x i1> %364, <8 x float> splat (float 1.000000e+00), <8 x float> %360
  %369 = fmul reassoc ninf nsz <8 x float> %365, splat (float 0x3FC99999A0000000)
  %370 = fmul reassoc ninf nsz <8 x float> %366, splat (float 0x3FC99999A0000000)
  %371 = fmul reassoc ninf nsz <8 x float> %367, splat (float 0x3FC99999A0000000)
  %372 = fmul reassoc ninf nsz <8 x float> %368, splat (float 0x3FC99999A0000000)
  %373 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %369
  %374 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %370
  %375 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %371
  %376 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %372
  %377 = fmul reassoc ninf nsz <8 x float> %173, splat (float 0x3FEE666660000000)
  %378 = fmul reassoc ninf nsz <8 x float> %174, splat (float 0x3FEE666660000000)
  %379 = fmul reassoc ninf nsz <8 x float> %175, splat (float 0x3FEE666660000000)
  %380 = fmul reassoc ninf nsz <8 x float> %176, splat (float 0x3FEE666660000000)
  %381 = fdiv reassoc ninf nsz <8 x float> %377, %341
  %382 = fdiv reassoc ninf nsz <8 x float> %378, %342
  %383 = fdiv reassoc ninf nsz <8 x float> %379, %343
  %384 = fdiv reassoc ninf nsz <8 x float> %380, %344
  %385 = fadd reassoc ninf nsz <8 x float> %381, splat (float 0x3FA99999A0000000)
  %386 = fadd reassoc ninf nsz <8 x float> %382, splat (float 0x3FA99999A0000000)
  %387 = fadd reassoc ninf nsz <8 x float> %383, splat (float 0x3FA99999A0000000)
  %388 = fadd reassoc ninf nsz <8 x float> %384, splat (float 0x3FA99999A0000000)
  %389 = or <8 x i1> %337, %321
  %390 = or <8 x i1> %338, %322
  %391 = or <8 x i1> %339, %323
  %392 = or <8 x i1> %340, %324
  %393 = or <8 x i1> %389, %293
  %394 = or <8 x i1> %390, %294
  %395 = or <8 x i1> %391, %295
  %396 = or <8 x i1> %392, %296
  %397 = or <8 x i1> %393, %104
  %398 = or <8 x i1> %394, %104
  %399 = or <8 x i1> %395, %104
  %400 = or <8 x i1> %396, %104
  %predphi = select <8 x i1> %349, <8 x float> %373, <8 x float> %385
  %predphi214 = select <8 x i1> %321, <8 x float> %333, <8 x float> %predphi
  %predphi215 = select <8 x i1> %293, <8 x float> %317, <8 x float> %predphi214
  %predphi216 = select <8 x i1> %broadcast.splat, <8 x float> %predphi215, <8 x float> splat (float 1.000000e+00)
  %predphi217 = select <8 x i1> %350, <8 x float> %374, <8 x float> %386
  %predphi218 = select <8 x i1> %322, <8 x float> %334, <8 x float> %predphi217
  %predphi219 = select <8 x i1> %294, <8 x float> %318, <8 x float> %predphi218
  %predphi220 = select <8 x i1> %broadcast.splat, <8 x float> %predphi219, <8 x float> splat (float 1.000000e+00)
  %predphi221 = select <8 x i1> %351, <8 x float> %375, <8 x float> %387
  %predphi222 = select <8 x i1> %323, <8 x float> %335, <8 x float> %predphi221
  %predphi223 = select <8 x i1> %295, <8 x float> %319, <8 x float> %predphi222
  %predphi224 = select <8 x i1> %broadcast.splat, <8 x float> %predphi223, <8 x float> splat (float 1.000000e+00)
  %predphi225 = select <8 x i1> %352, <8 x float> %376, <8 x float> %388
  %predphi226 = select <8 x i1> %324, <8 x float> %336, <8 x float> %predphi225
  %predphi227 = select <8 x i1> %296, <8 x float> %320, <8 x float> %predphi226
  %predphi228 = select <8 x i1> %broadcast.splat, <8 x float> %predphi227, <8 x float> splat (float 1.000000e+00)
  %401 = fcmp reassoc ninf nsz ogt <8 x float> %249, splat (float 0x3EB0C6F7A0000000)
  %402 = fcmp reassoc ninf nsz ogt <8 x float> %250, splat (float 0x3EB0C6F7A0000000)
  %403 = fcmp reassoc ninf nsz ogt <8 x float> %251, splat (float 0x3EB0C6F7A0000000)
  %404 = fcmp reassoc ninf nsz ogt <8 x float> %252, splat (float 0x3EB0C6F7A0000000)
  %405 = select <8 x i1> %397, <8 x i1> %401, <8 x i1> zeroinitializer
  %406 = select <8 x i1> %398, <8 x i1> %402, <8 x i1> zeroinitializer
  %407 = select <8 x i1> %399, <8 x i1> %403, <8 x i1> zeroinitializer
  %408 = select <8 x i1> %400, <8 x i1> %404, <8 x i1> zeroinitializer
  %409 = fcmp reassoc ninf nsz ogt <8 x float> %233, splat (float 0x3EB0C6F7A0000000)
  %410 = fcmp reassoc ninf nsz ogt <8 x float> %234, splat (float 0x3EB0C6F7A0000000)
  %411 = fcmp reassoc ninf nsz ogt <8 x float> %235, splat (float 0x3EB0C6F7A0000000)
  %412 = fcmp reassoc ninf nsz ogt <8 x float> %236, splat (float 0x3EB0C6F7A0000000)
  %413 = fcmp reassoc ninf nsz ogt <8 x float> %245, splat (float 0x3EB0C6F7A0000000)
  %414 = fcmp reassoc ninf nsz ogt <8 x float> %246, splat (float 0x3EB0C6F7A0000000)
  %415 = fcmp reassoc ninf nsz ogt <8 x float> %247, splat (float 0x3EB0C6F7A0000000)
  %416 = fcmp reassoc ninf nsz ogt <8 x float> %248, splat (float 0x3EB0C6F7A0000000)
  %417 = select <8 x i1> %409, <8 x i1> %413, <8 x i1> zeroinitializer
  %418 = select <8 x i1> %410, <8 x i1> %414, <8 x i1> zeroinitializer
  %419 = select <8 x i1> %411, <8 x i1> %415, <8 x i1> zeroinitializer
  %420 = select <8 x i1> %412, <8 x i1> %416, <8 x i1> zeroinitializer
  %421 = select <8 x i1> %405, <8 x i1> %417, <8 x i1> zeroinitializer
  %422 = select <8 x i1> %406, <8 x i1> %418, <8 x i1> zeroinitializer
  %423 = select <8 x i1> %407, <8 x i1> %419, <8 x i1> zeroinitializer
  %424 = select <8 x i1> %408, <8 x i1> %420, <8 x i1> zeroinitializer
  %425 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, %wide.masked.gather190
  %426 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, %wide.masked.gather191
  %427 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, %wide.masked.gather192
  %428 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather205, %wide.masked.gather193
  %429 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather208, %wide.masked.gather196
  %430 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather209, %wide.masked.gather197
  %431 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather210, %wide.masked.gather198
  %432 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather211, %wide.masked.gather199
  %433 = fadd reassoc ninf nsz <8 x float> %429, %425
  %434 = fadd reassoc ninf nsz <8 x float> %430, %426
  %435 = fadd reassoc ninf nsz <8 x float> %431, %427
  %436 = fadd reassoc ninf nsz <8 x float> %432, %428
  %437 = fmul reassoc ninf nsz <8 x float> %245, %233
  %438 = fmul reassoc ninf nsz <8 x float> %246, %234
  %439 = fmul reassoc ninf nsz <8 x float> %247, %235
  %440 = fmul reassoc ninf nsz <8 x float> %248, %236
  %441 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %437)
  %442 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %438)
  %443 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %439)
  %444 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %440)
  %445 = fdiv reassoc ninf nsz <8 x float> %433, %441
  %446 = fdiv reassoc ninf nsz <8 x float> %434, %442
  %447 = fdiv reassoc ninf nsz <8 x float> %435, %443
  %448 = fdiv reassoc ninf nsz <8 x float> %436, %444
  %449 = fcmp reassoc ninf nsz ule <8 x float> %249, splat (float 1.500000e+02)
  %450 = fcmp reassoc ninf nsz ule <8 x float> %250, splat (float 1.500000e+02)
  %451 = fcmp reassoc ninf nsz ule <8 x float> %251, splat (float 1.500000e+02)
  %452 = fcmp reassoc ninf nsz ule <8 x float> %252, splat (float 1.500000e+02)
  %453 = fcmp reassoc ninf nsz uge <8 x float> %445, splat (float 0x3FC99999A0000000)
  %454 = fcmp reassoc ninf nsz uge <8 x float> %446, splat (float 0x3FC99999A0000000)
  %455 = fcmp reassoc ninf nsz uge <8 x float> %447, splat (float 0x3FC99999A0000000)
  %456 = fcmp reassoc ninf nsz uge <8 x float> %448, splat (float 0x3FC99999A0000000)
  %.not339 = select <8 x i1> %449, <8 x i1> splat (i1 true), <8 x i1> %453
  %.not342 = select <8 x i1> %450, <8 x i1> splat (i1 true), <8 x i1> %454
  %.not345 = select <8 x i1> %451, <8 x i1> splat (i1 true), <8 x i1> %455
  %.not348 = select <8 x i1> %452, <8 x i1> splat (i1 true), <8 x i1> %456
  %457 = select <8 x i1> %421, <8 x i1> %.not339, <8 x i1> zeroinitializer
  %458 = select <8 x i1> %422, <8 x i1> %.not342, <8 x i1> zeroinitializer
  %459 = select <8 x i1> %423, <8 x i1> %.not345, <8 x i1> zeroinitializer
  %460 = select <8 x i1> %424, <8 x i1> %.not348, <8 x i1> zeroinitializer
  %461 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %445, <8 x float> zeroinitializer)
  %462 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %446, <8 x float> zeroinitializer)
  %463 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %447, <8 x float> zeroinitializer)
  %464 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %448, <8 x float> zeroinitializer)
  %465 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %249)
  %466 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %250)
  %467 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %251)
  %468 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %252)
  %469 = fmul reassoc ninf nsz <8 x float> %465, splat (float 2.025000e+02)
  %470 = fmul reassoc ninf nsz <8 x float> %466, splat (float 2.025000e+02)
  %471 = fmul reassoc ninf nsz <8 x float> %467, splat (float 2.025000e+02)
  %472 = fmul reassoc ninf nsz <8 x float> %468, splat (float 2.025000e+02)
  %473 = fmul reassoc ninf nsz <8 x float> %469, %461
  %.fr = freeze <8 x float> %473
  %474 = fmul reassoc ninf nsz <8 x float> %470, %462
  %.fr349 = freeze <8 x float> %474
  %475 = fmul reassoc ninf nsz <8 x float> %471, %463
  %.fr350 = freeze <8 x float> %475
  %476 = fmul reassoc ninf nsz <8 x float> %472, %464
  %.fr351 = freeze <8 x float> %476
  %477 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %478 = fcmp reassoc nsz ogt <8 x float> %.fr349, splat (float 3.000000e+00)
  %479 = fcmp reassoc nsz ogt <8 x float> %.fr350, splat (float 3.000000e+00)
  %480 = fcmp reassoc nsz ogt <8 x float> %.fr351, splat (float 3.000000e+00)
  %481 = xor <8 x i1> %477, splat (i1 true)
  %482 = xor <8 x i1> %478, splat (i1 true)
  %483 = xor <8 x i1> %479, splat (i1 true)
  %484 = xor <8 x i1> %480, splat (i1 true)
  %485 = and <8 x i1> %457, %481
  %486 = and <8 x i1> %458, %482
  %487 = and <8 x i1> %459, %483
  %488 = and <8 x i1> %460, %484
  %489 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %490 = fcmp reassoc nsz olt <8 x float> %.fr349, splat (float -3.000000e+00)
  %491 = fcmp reassoc nsz olt <8 x float> %.fr350, splat (float -3.000000e+00)
  %492 = fcmp reassoc nsz olt <8 x float> %.fr351, splat (float -3.000000e+00)
  %493 = xor <8 x i1> %489, splat (i1 true)
  %494 = xor <8 x i1> %490, splat (i1 true)
  %495 = xor <8 x i1> %491, splat (i1 true)
  %496 = xor <8 x i1> %492, splat (i1 true)
  %497 = and <8 x i1> %485, %493
  %498 = and <8 x i1> %486, %494
  %499 = and <8 x i1> %487, %495
  %500 = and <8 x i1> %488, %496
  %501 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %502 = fmul reassoc ninf nsz <8 x float> %.fr349, %.fr349
  %503 = fmul reassoc ninf nsz <8 x float> %.fr350, %.fr350
  %504 = fmul reassoc ninf nsz <8 x float> %.fr351, %.fr351
  %505 = fadd reassoc ninf nsz <8 x float> %501, splat (float 2.700000e+01)
  %506 = fadd reassoc ninf nsz <8 x float> %502, splat (float 2.700000e+01)
  %507 = fadd reassoc ninf nsz <8 x float> %503, splat (float 2.700000e+01)
  %508 = fadd reassoc ninf nsz <8 x float> %504, splat (float 2.700000e+01)
  %509 = fmul reassoc ninf nsz <8 x float> %505, %.fr
  %510 = fmul reassoc ninf nsz <8 x float> %506, %.fr349
  %511 = fmul reassoc ninf nsz <8 x float> %507, %.fr350
  %512 = fmul reassoc ninf nsz <8 x float> %508, %.fr351
  %513 = fmul reassoc ninf nsz <8 x float> %501, splat (float 9.000000e+00)
  %514 = fmul reassoc ninf nsz <8 x float> %502, splat (float 9.000000e+00)
  %515 = fmul reassoc ninf nsz <8 x float> %503, splat (float 9.000000e+00)
  %516 = fmul reassoc ninf nsz <8 x float> %504, splat (float 9.000000e+00)
  %517 = fadd reassoc ninf nsz <8 x float> %513, splat (float 2.700000e+01)
  %518 = fadd reassoc ninf nsz <8 x float> %514, splat (float 2.700000e+01)
  %519 = fadd reassoc ninf nsz <8 x float> %515, splat (float 2.700000e+01)
  %520 = fadd reassoc ninf nsz <8 x float> %516, splat (float 2.700000e+01)
  %521 = fdiv reassoc ninf nsz <8 x float> %509, %517
  %522 = fdiv reassoc ninf nsz <8 x float> %510, %518
  %523 = fdiv reassoc ninf nsz <8 x float> %511, %519
  %524 = fdiv reassoc ninf nsz <8 x float> %512, %520
  %525 = fadd reassoc ninf nsz <8 x float> %521, splat (float 1.000000e+00)
  %526 = fadd reassoc ninf nsz <8 x float> %522, splat (float 1.000000e+00)
  %527 = fadd reassoc ninf nsz <8 x float> %523, splat (float 1.000000e+00)
  %528 = fadd reassoc ninf nsz <8 x float> %524, splat (float 1.000000e+00)
  %529 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %445
  %530 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %446
  %531 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %447
  %532 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %448
  %533 = fmul reassoc ninf nsz <8 x float> %529, %173
  %534 = fmul reassoc ninf nsz <8 x float> %530, %174
  %535 = fmul reassoc ninf nsz <8 x float> %531, %175
  %536 = fmul reassoc ninf nsz <8 x float> %532, %176
  %537 = and <8 x i1> %485, %489
  %538 = and <8 x i1> %486, %490
  %539 = and <8 x i1> %487, %491
  %540 = and <8 x i1> %488, %492
  %541 = and <8 x i1> %457, %477
  %542 = and <8 x i1> %458, %478
  %543 = and <8 x i1> %459, %479
  %544 = and <8 x i1> %460, %480
  %545 = xor <8 x i1> %417, splat (i1 true)
  %546 = xor <8 x i1> %418, splat (i1 true)
  %547 = xor <8 x i1> %419, splat (i1 true)
  %548 = xor <8 x i1> %420, splat (i1 true)
  %549 = select <8 x i1> %405, <8 x i1> %545, <8 x i1> zeroinitializer
  %550 = select <8 x i1> %406, <8 x i1> %546, <8 x i1> zeroinitializer
  %551 = select <8 x i1> %407, <8 x i1> %547, <8 x i1> zeroinitializer
  %552 = select <8 x i1> %408, <8 x i1> %548, <8 x i1> zeroinitializer
  %553 = xor <8 x i1> %401, splat (i1 true)
  %554 = xor <8 x i1> %402, splat (i1 true)
  %555 = xor <8 x i1> %403, splat (i1 true)
  %556 = xor <8 x i1> %404, splat (i1 true)
  %557 = select <8 x i1> %397, <8 x i1> %553, <8 x i1> zeroinitializer
  %558 = select <8 x i1> %398, <8 x i1> %554, <8 x i1> zeroinitializer
  %559 = select <8 x i1> %399, <8 x i1> %555, <8 x i1> zeroinitializer
  %560 = select <8 x i1> %400, <8 x i1> %556, <8 x i1> zeroinitializer
  %561 = select <8 x i1> %457, <8 x i1> splat (i1 true), <8 x i1> %557
  %562 = select <8 x i1> %561, <8 x i1> splat (i1 true), <8 x i1> %549
  %predphi233 = select <8 x i1> %562, <8 x float> %173, <8 x float> %533
  %563 = select <8 x i1> %458, <8 x i1> splat (i1 true), <8 x i1> %558
  %564 = select <8 x i1> %563, <8 x i1> splat (i1 true), <8 x i1> %550
  %predphi238 = select <8 x i1> %564, <8 x float> %174, <8 x float> %534
  %565 = select <8 x i1> %459, <8 x i1> splat (i1 true), <8 x i1> %559
  %566 = select <8 x i1> %565, <8 x i1> splat (i1 true), <8 x i1> %551
  %predphi243 = select <8 x i1> %566, <8 x float> %175, <8 x float> %535
  %567 = select <8 x i1> %460, <8 x i1> splat (i1 true), <8 x i1> %560
  %568 = select <8 x i1> %567, <8 x i1> splat (i1 true), <8 x i1> %552
  %predphi248 = select <8 x i1> %568, <8 x float> %176, <8 x float> %536
  %predphi251 = select <8 x i1> %541, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi252 = select <8 x i1> %497, <8 x float> %525, <8 x float> %predphi251
  %predphi253 = select <8 x i1> %537, <8 x float> zeroinitializer, <8 x float> %predphi252
  %predphi256 = select <8 x i1> %542, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi257 = select <8 x i1> %498, <8 x float> %526, <8 x float> %predphi256
  %predphi258 = select <8 x i1> %538, <8 x float> zeroinitializer, <8 x float> %predphi257
  %predphi261 = select <8 x i1> %543, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi262 = select <8 x i1> %499, <8 x float> %527, <8 x float> %predphi261
  %predphi263 = select <8 x i1> %539, <8 x float> zeroinitializer, <8 x float> %predphi262
  %predphi266 = select <8 x i1> %544, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi267 = select <8 x i1> %500, <8 x float> %528, <8 x float> %predphi266
  %predphi268 = select <8 x i1> %540, <8 x float> zeroinitializer, <8 x float> %predphi267
  %569 = fmul reassoc ninf nsz <8 x float> %predphi253, %predphi216
  %570 = fmul reassoc ninf nsz <8 x float> %predphi258, %predphi220
  %571 = fmul reassoc ninf nsz <8 x float> %predphi263, %predphi224
  %572 = fmul reassoc ninf nsz <8 x float> %predphi268, %predphi228
  %573 = fmul reassoc ninf nsz <8 x float> %569, %predphi233
  %574 = fmul reassoc ninf nsz <8 x float> %570, %predphi238
  %575 = fmul reassoc ninf nsz <8 x float> %571, %predphi243
  %576 = fmul reassoc ninf nsz <8 x float> %572, %predphi248
  %577 = fadd reassoc ninf nsz <8 x float> %573, %vec.phi171
  %578 = fadd reassoc ninf nsz <8 x float> %574, %vec.phi172
  %579 = fadd reassoc ninf nsz <8 x float> %575, %vec.phi173
  %580 = fadd reassoc ninf nsz <8 x float> %576, %vec.phi174
  %581 = fadd reassoc ninf nsz <8 x float> %569, %vec.phi167
  %582 = fadd reassoc ninf nsz <8 x float> %570, %vec.phi168
  %583 = fadd reassoc ninf nsz <8 x float> %571, %vec.phi169
  %584 = fadd reassoc ninf nsz <8 x float> %572, %vec.phi170
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %585 = icmp eq i64 %lsr.iv.next, 0
  br i1 %585, label %middle.block156, label %vector.body165, !llvm.loop !11

middle.block156:                                  ; preds = %vector.body165
  %bin.rdx270 = fadd reassoc ninf nsz <8 x float> %582, %581
  %bin.rdx271 = fadd reassoc ninf nsz <8 x float> %583, %bin.rdx270
  %bin.rdx272 = fadd reassoc ninf nsz <8 x float> %584, %bin.rdx271
  %586 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx272)
  %bin.rdx273 = fadd reassoc ninf nsz <8 x float> %578, %577
  %bin.rdx274 = fadd reassoc ninf nsz <8 x float> %579, %bin.rdx273
  %bin.rdx275 = fadd reassoc ninf nsz <8 x float> %580, %bin.rdx274
  %587 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx275)
  br i1 %cmp.n276, label %for_loop_test11.after_for10_crit_edge.us, label %vec.epilog.iter.check283

vec.epilog.iter.check283:                         ; preds = %middle.block156
  br i1 %min.epilog.iters.check285, label %for_loop_body8.us.preheader, label %vec.epilog.ph282

vec.epilog.ph282:                                 ; preds = %vec.epilog.iter.check283, %vector.main.loop.iter.check161
  %bc.resume.val277 = phi i64 [ %n.vec164, %vec.epilog.iter.check283 ], [ 0, %vector.main.loop.iter.check161 ]
  %bc.merge.rdx278 = phi float [ %586, %vec.epilog.iter.check283 ], [ %.05076.us, %vector.main.loop.iter.check161 ]
  %bc.merge.rdx279 = phi float [ %587, %vec.epilog.iter.check283 ], [ %.05275.us, %vector.main.loop.iter.check161 ]
  %588 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx278, i64 0
  %589 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx279, i64 0
  %590 = trunc nuw nsw i64 %bc.resume.val277 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %590, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert298 = insertelement <8 x i32> poison, i32 %111, i64 0
  %broadcast.splat299 = shufflevector <8 x i32> %broadcast.splatinsert298, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert301 = insertelement <8 x i32> poison, i32 %112, i64 0
  %broadcast.splat302 = shufflevector <8 x i32> %broadcast.splatinsert301, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert304 = insertelement <8 x i32> poison, i32 %113, i64 0
  %broadcast.splat305 = shufflevector <8 x i32> %broadcast.splatinsert304, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert307 = insertelement <8 x i32> poison, i32 %114, i64 0
  %broadcast.splat308 = shufflevector <8 x i32> %broadcast.splatinsert307, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert310 = insertelement <8 x i32> poison, i32 %115, i64 0
  %broadcast.splat311 = shufflevector <8 x i32> %broadcast.splatinsert310, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert313 = insertelement <8 x i32> poison, i32 %116, i64 0
  %broadcast.splat314 = shufflevector <8 x i32> %broadcast.splatinsert313, <8 x i32> poison, <8 x i32> zeroinitializer
  %591 = add i64 %107, %bc.resume.val277
  br label %vec.epilog.vector.body290

vec.epilog.vector.body290:                        ; preds = %vec.epilog.vector.body290, %vec.epilog.ph282
  %lsr.iv419 = phi i64 [ %lsr.iv.next420, %vec.epilog.vector.body290 ], [ %591, %vec.epilog.ph282 ]
  %vec.phi292 = phi <8 x float> [ %588, %vec.epilog.ph282 ], [ %703, %vec.epilog.vector.body290 ]
  %vec.phi293 = phi <8 x float> [ %589, %vec.epilog.ph282 ], [ %702, %vec.epilog.vector.body290 ]
  %vec.ind294 = phi <8 x i32> [ %induction, %vec.epilog.ph282 ], [ %vec.ind.next295, %vec.epilog.vector.body290 ]
  %592 = shl <8 x i32> %vec.ind294, splat (i32 1)
  %593 = add <8 x i32> %broadcast.splat176, %592
  %594 = add <8 x i32> %broadcast.splat299, %593
  %595 = sext <8 x i32> %594 to <8 x i64>
  %596 = getelementptr float, ptr %71, <8 x i64> %595
  %wide.masked.gather300 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %596, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %597 = add <8 x i32> %broadcast.splat302, %593
  %598 = sext <8 x i32> %597 to <8 x i64>
  %599 = getelementptr float, ptr %73, <8 x i64> %598
  %wide.masked.gather303 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %599, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %600 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather300, %wide.masked.gather303
  %601 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %600)
  %602 = add <8 x i32> %broadcast.splat305, %593
  %603 = sext <8 x i32> %602 to <8 x i64>
  %604 = getelementptr float, ptr %75, <8 x i64> %603
  %wide.masked.gather306 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %604, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %605 = add <8 x i32> %broadcast.splat308, %593
  %606 = sext <8 x i32> %605 to <8 x i64>
  %607 = getelementptr float, ptr %77, <8 x i64> %606
  %wide.masked.gather309 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %607, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %608 = add <8 x i32> %broadcast.splat311, %593
  %609 = sext <8 x i32> %608 to <8 x i64>
  %610 = getelementptr float, ptr %79, <8 x i64> %609
  %wide.masked.gather312 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %610, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %611 = add <8 x i32> %broadcast.splat314, %593
  %612 = sext <8 x i32> %611 to <8 x i64>
  %613 = getelementptr float, ptr %81, <8 x i64> %612
  %wide.masked.gather315 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %613, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %614 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather306, %wide.masked.gather306
  %615 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather309, %wide.masked.gather309
  %616 = fadd reassoc ninf nsz <8 x float> %615, %614
  %617 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather312, %wide.masked.gather312
  %618 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather315, %wide.masked.gather315
  %619 = fadd reassoc ninf nsz <8 x float> %618, %617
  %620 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %616, <8 x float> %619)
  %621 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather303, splat (float -2.000000e+00)
  %622 = fadd reassoc ninf nsz <8 x float> %621, splat (float 3.000000e+00)
  %623 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %622, <8 x float> splat (float 3.000000e+00))
  %624 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %623, <8 x float> splat (float 1.000000e+00))
  %625 = fmul reassoc ninf nsz <8 x float> %624, %broadcast.splat213
  %626 = fcmp reassoc ninf nsz olt <8 x float> %620, splat (float 1.500000e+02)
  %627 = xor <8 x i1> %626, splat (i1 true)
  %628 = select <8 x i1> %broadcast.splat, <8 x i1> %627, <8 x i1> zeroinitializer
  %629 = fcmp reassoc ninf nsz olt <8 x float> %601, %625
  %630 = xor <8 x i1> %629, splat (i1 true)
  %631 = select <8 x i1> %628, <8 x i1> %630, <8 x i1> zeroinitializer
  %632 = fmul reassoc ninf nsz <8 x float> %625, splat (float 4.000000e+00)
  %633 = fdiv reassoc ninf nsz <8 x float> %601, %632
  %634 = fcmp reassoc ninf nsz ogt <8 x float> %633, splat (float 1.000000e+00)
  %635 = select <8 x i1> %634, <8 x float> splat (float 1.000000e+00), <8 x float> %633
  %636 = fmul reassoc ninf nsz <8 x float> %635, splat (float 0x3FD99999A0000000)
  %637 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %636
  %638 = select <8 x i1> %628, <8 x i1> %629, <8 x i1> zeroinitializer
  %639 = fmul reassoc ninf nsz <8 x float> %601, splat (float 0x3FC3333340000000)
  %640 = fdiv reassoc ninf nsz <8 x float> %639, %625
  %641 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %640
  %642 = select <8 x i1> %broadcast.splat, <8 x i1> %626, <8 x i1> zeroinitializer
  %643 = fmul reassoc ninf nsz <8 x float> %625, splat (float 1.500000e+00)
  %644 = fcmp reassoc ninf nsz uge <8 x float> %601, %643
  %645 = select <8 x i1> %642, <8 x i1> %644, <8 x i1> zeroinitializer
  %646 = fsub reassoc ninf nsz <8 x float> %601, %643
  %647 = fdiv reassoc ninf nsz <8 x float> %646, %643
  %648 = fcmp reassoc ninf nsz ogt <8 x float> %647, splat (float 1.000000e+00)
  %649 = select <8 x i1> %648, <8 x float> splat (float 1.000000e+00), <8 x float> %647
  %650 = fmul reassoc ninf nsz <8 x float> %649, splat (float 0x3FC99999A0000000)
  %651 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %650
  %652 = fmul reassoc ninf nsz <8 x float> %601, splat (float 0x3FEE666660000000)
  %653 = fdiv reassoc ninf nsz <8 x float> %652, %643
  %654 = fadd reassoc ninf nsz <8 x float> %653, splat (float 0x3FA99999A0000000)
  %655 = or <8 x i1> %638, %104
  %656 = or <8 x i1> %655, %642
  %657 = or <8 x i1> %656, %631
  %predphi318 = select <8 x i1> %645, <8 x float> %651, <8 x float> %654
  %predphi319 = select <8 x i1> %638, <8 x float> %641, <8 x float> %predphi318
  %predphi320 = select <8 x i1> %631, <8 x float> %637, <8 x float> %predphi319
  %predphi321 = select <8 x i1> %broadcast.splat, <8 x float> %predphi320, <8 x float> splat (float 1.000000e+00)
  %658 = fcmp reassoc ninf nsz ogt <8 x float> %620, splat (float 0x3EB0C6F7A0000000)
  %659 = select <8 x i1> %657, <8 x i1> %658, <8 x i1> zeroinitializer
  %660 = fcmp reassoc ninf nsz ogt <8 x float> %616, splat (float 0x3EB0C6F7A0000000)
  %661 = fcmp reassoc ninf nsz ogt <8 x float> %619, splat (float 0x3EB0C6F7A0000000)
  %662 = select <8 x i1> %660, <8 x i1> %661, <8 x i1> zeroinitializer
  %663 = select <8 x i1> %659, <8 x i1> %662, <8 x i1> zeroinitializer
  %664 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather312, %wide.masked.gather306
  %665 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather315, %wide.masked.gather309
  %666 = fadd reassoc ninf nsz <8 x float> %665, %664
  %667 = fmul reassoc ninf nsz <8 x float> %619, %616
  %668 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %667)
  %669 = fdiv reassoc ninf nsz <8 x float> %666, %668
  %670 = fcmp reassoc ninf nsz ule <8 x float> %620, splat (float 1.500000e+02)
  %671 = fcmp reassoc ninf nsz uge <8 x float> %669, splat (float 0x3FC99999A0000000)
  %.not354 = select <8 x i1> %670, <8 x i1> splat (i1 true), <8 x i1> %671
  %672 = select <8 x i1> %663, <8 x i1> %.not354, <8 x i1> zeroinitializer
  %673 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %669, <8 x float> zeroinitializer)
  %674 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %620)
  %675 = fmul reassoc ninf nsz <8 x float> %674, splat (float 2.025000e+02)
  %676 = fmul reassoc ninf nsz <8 x float> %675, %673
  %.fr355 = freeze <8 x float> %676
  %677 = fcmp reassoc nsz ogt <8 x float> %.fr355, splat (float 3.000000e+00)
  %678 = xor <8 x i1> %677, splat (i1 true)
  %679 = and <8 x i1> %672, %678
  %680 = fcmp reassoc nsz olt <8 x float> %.fr355, splat (float -3.000000e+00)
  %681 = xor <8 x i1> %680, splat (i1 true)
  %682 = and <8 x i1> %679, %681
  %683 = fmul reassoc ninf nsz <8 x float> %.fr355, %.fr355
  %684 = fadd reassoc ninf nsz <8 x float> %683, splat (float 2.700000e+01)
  %685 = fmul reassoc ninf nsz <8 x float> %684, %.fr355
  %686 = fmul reassoc ninf nsz <8 x float> %683, splat (float 9.000000e+00)
  %687 = fadd reassoc ninf nsz <8 x float> %686, splat (float 2.700000e+01)
  %688 = fdiv reassoc ninf nsz <8 x float> %685, %687
  %689 = fadd reassoc ninf nsz <8 x float> %688, splat (float 1.000000e+00)
  %690 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %669
  %691 = fmul reassoc ninf nsz <8 x float> %690, %601
  %692 = and <8 x i1> %679, %680
  %693 = and <8 x i1> %672, %677
  %694 = xor <8 x i1> %662, splat (i1 true)
  %695 = select <8 x i1> %659, <8 x i1> %694, <8 x i1> zeroinitializer
  %696 = xor <8 x i1> %658, splat (i1 true)
  %697 = select <8 x i1> %657, <8 x i1> %696, <8 x i1> zeroinitializer
  %698 = select <8 x i1> %672, <8 x i1> splat (i1 true), <8 x i1> %697
  %699 = select <8 x i1> %698, <8 x i1> splat (i1 true), <8 x i1> %695
  %predphi326 = select <8 x i1> %699, <8 x float> %601, <8 x float> %691
  %predphi329 = select <8 x i1> %693, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi330 = select <8 x i1> %682, <8 x float> %689, <8 x float> %predphi329
  %predphi331 = select <8 x i1> %692, <8 x float> zeroinitializer, <8 x float> %predphi330
  %700 = fmul reassoc ninf nsz <8 x float> %predphi331, %predphi321
  %701 = fmul reassoc ninf nsz <8 x float> %700, %predphi326
  %702 = fadd reassoc ninf nsz <8 x float> %701, %vec.phi293
  %703 = fadd reassoc ninf nsz <8 x float> %700, %vec.phi292
  %vec.ind.next295 = add <8 x i32> %vec.ind294, splat (i32 8)
  %lsr.iv.next420 = add i64 %lsr.iv419, 8
  %704 = icmp eq i64 %lsr.iv.next420, 0
  br i1 %704, label %vec.epilog.middle.block280, label %vec.epilog.vector.body290, !llvm.loop !14

vec.epilog.middle.block280:                       ; preds = %vec.epilog.vector.body290
  %705 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %703)
  %706 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %702)
  br i1 %cmp.n333, label %for_loop_test11.after_for10_crit_edge.us, label %for_loop_body8.us.preheader

for_loop_body8.us.preheader:                      ; preds = %vec.epilog.middle.block280, %vec.epilog.iter.check283, %vector.scevcheck140, %iter.check159
  %indvars.iv.ph = phi i64 [ %n.vec164, %vec.epilog.iter.check283 ], [ 0, %iter.check159 ], [ 0, %vector.scevcheck140 ], [ %n.vec287, %vec.epilog.middle.block280 ]
  %.15172.us.ph = phi float [ %586, %vec.epilog.iter.check283 ], [ %.05076.us, %iter.check159 ], [ %.05076.us, %vector.scevcheck140 ], [ %705, %vec.epilog.middle.block280 ]
  %.15371.us.ph = phi float [ %587, %vec.epilog.iter.check283 ], [ %.05275.us, %iter.check159 ], [ %.05275.us, %vector.scevcheck140 ], [ %706, %vec.epilog.middle.block280 ]
  %707 = trunc i64 %indvars.iv.ph to i32
  %708 = shl nuw i32 %707, 1
  %709 = add i64 %108, %indvars.iv.ph
  br label %for_loop_body8.us

for_loop_body8.us:                                ; preds = %after_if38.us, %for_loop_body8.us.preheader
  %lsr.iv445 = phi i64 [ %709, %for_loop_body8.us.preheader ], [ %lsr.iv.next446, %after_if38.us ]
  %lsr.iv443 = phi i32 [ %lsr.iv441, %for_loop_body8.us.preheader ], [ %lsr.iv.next444, %after_if38.us ]
  %lsr.iv439 = phi i32 [ %lsr.iv437, %for_loop_body8.us.preheader ], [ %lsr.iv.next440, %after_if38.us ]
  %lsr.iv435 = phi i32 [ %lsr.iv433, %for_loop_body8.us.preheader ], [ %lsr.iv.next436, %after_if38.us ]
  %lsr.iv431 = phi i32 [ %lsr.iv429, %for_loop_body8.us.preheader ], [ %lsr.iv.next432, %after_if38.us ]
  %lsr.iv427 = phi i32 [ %lsr.iv425, %for_loop_body8.us.preheader ], [ %lsr.iv.next428, %after_if38.us ]
  %lsr.iv423 = phi i32 [ %lsr.iv421, %for_loop_body8.us.preheader ], [ %lsr.iv.next424, %after_if38.us ]
  %.15172.us = phi float [ %796, %after_if38.us ], [ %.15172.us.ph, %for_loop_body8.us.preheader ]
  %.15371.us = phi float [ %795, %after_if38.us ], [ %.15371.us.ph, %for_loop_body8.us.preheader ]
  %710 = add i32 %708, %lsr.iv443
  %711 = sext i32 %710 to i64
  %712 = getelementptr float, ptr %71, i64 %711
  %713 = load float, ptr %712, align 4
  %714 = add i32 %708, %lsr.iv439
  %715 = sext i32 %714 to i64
  %716 = getelementptr float, ptr %73, i64 %715
  %717 = load float, ptr %716, align 4
  %718 = fsub reassoc ninf nsz float %713, %717
  %719 = tail call noundef float @llvm.fabs.f32(float %718)
  %720 = add i32 %708, %lsr.iv435
  %721 = sext i32 %720 to i64
  %722 = getelementptr float, ptr %75, i64 %721
  %723 = load float, ptr %722, align 4
  %724 = add i32 %708, %lsr.iv431
  %725 = sext i32 %724 to i64
  %726 = getelementptr float, ptr %77, i64 %725
  %727 = load float, ptr %726, align 4
  %728 = add i32 %708, %lsr.iv427
  %729 = sext i32 %728 to i64
  %730 = getelementptr float, ptr %79, i64 %729
  %731 = load float, ptr %730, align 4
  %732 = add i32 %708, %lsr.iv423
  %733 = sext i32 %732 to i64
  %734 = getelementptr float, ptr %81, i64 %733
  %735 = load float, ptr %734, align 4
  %736 = fmul reassoc ninf nsz float %723, %723
  %737 = fmul reassoc ninf nsz float %727, %727
  %738 = fadd reassoc ninf nsz float %737, %736
  %739 = fmul reassoc ninf nsz float %731, %731
  %740 = fmul reassoc ninf nsz float %735, %735
  %741 = fadd reassoc ninf nsz float %740, %739
  %742 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %738, float %741)
  %factor.us = fmul reassoc ninf nsz float %717, -2.000000e+00
  %743 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %744 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %743, float 3.000000e+00)
  %745 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %744, float 1.000000e+00)
  %746 = fmul reassoc ninf nsz float %745, %55
  br i1 %56, label %true_block12.us, label %after_if14.us

true_block12.us:                                  ; preds = %for_loop_body8.us
  %747 = fcmp reassoc ninf nsz olt float %742, 1.500000e+02
  br i1 %747, label %true_block15.us, label %false_block16.us

false_block16.us:                                 ; preds = %true_block12.us
  %748 = fcmp reassoc ninf nsz olt float %719, %746
  br i1 %748, label %true_block24.us, label %false_block25.us

false_block25.us:                                 ; preds = %false_block16.us
  %749 = fmul reassoc ninf nsz float %746, 4.000000e+00
  %750 = fdiv reassoc ninf nsz float %719, %749
  %751 = fcmp reassoc ninf nsz ogt float %750, 1.000000e+00
  %spec.store.select1.us = select i1 %751, float 1.000000e+00, float %750
  %752 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %753 = fsub reassoc ninf nsz float 0x3FE6666680000000, %752
  br label %after_if14.us

true_block24.us:                                  ; preds = %false_block16.us
  %754 = fmul reassoc ninf nsz float %719, 0x3FC3333340000000
  %755 = fdiv reassoc ninf nsz float %754, %746
  %756 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %755
  br label %after_if14.us

true_block15.us:                                  ; preds = %true_block12.us
  %757 = fmul reassoc ninf nsz float %746, 1.500000e+00
  %758 = fcmp reassoc ninf nsz olt float %719, %757
  br i1 %758, label %true_block18.us, label %false_block19.us

false_block19.us:                                 ; preds = %true_block15.us
  %759 = fsub reassoc ninf nsz float %719, %757
  %760 = fdiv reassoc ninf nsz float %759, %757
  %761 = fcmp reassoc ninf nsz ogt float %760, 1.000000e+00
  %spec.store.select.us = select i1 %761, float 1.000000e+00, float %760
  %762 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %763 = fsub reassoc ninf nsz float 1.000000e+00, %762
  br label %after_if14.us

true_block18.us:                                  ; preds = %true_block15.us
  %764 = fmul reassoc ninf nsz float %719, 0x3FEE666660000000
  %765 = fdiv reassoc ninf nsz float %764, %757
  %766 = fadd reassoc ninf nsz float %765, 0x3FA99999A0000000
  br label %after_if14.us

after_if14.us:                                    ; preds = %true_block18.us, %false_block19.us, %true_block24.us, %false_block25.us, %for_loop_body8.us
  %.046.us = phi float [ %766, %true_block18.us ], [ %763, %false_block19.us ], [ %756, %true_block24.us ], [ %753, %false_block25.us ], [ 1.000000e+00, %for_loop_body8.us ]
  %767 = fcmp reassoc ninf nsz ogt float %742, 0x3EB0C6F7A0000000
  br i1 %767, label %true_block30.us, label %after_if38.us

true_block30.us:                                  ; preds = %after_if14.us
  %768 = fcmp reassoc ninf nsz ogt float %738, 0x3EB0C6F7A0000000
  %769 = fcmp reassoc ninf nsz ogt float %741, 0x3EB0C6F7A0000000
  %.041.us = select i1 %768, i1 %769, i1 false
  br i1 %.041.us, label %true_block36.us, label %after_if38.us

true_block36.us:                                  ; preds = %true_block30.us
  %770 = fmul reassoc ninf nsz float %731, %723
  %771 = fmul reassoc ninf nsz float %735, %727
  %772 = fadd reassoc ninf nsz float %771, %770
  %773 = fmul reassoc ninf nsz float %741, %738
  %774 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %773)
  %775 = fdiv reassoc ninf nsz float %772, %774
  %776 = fcmp reassoc ninf nsz ogt float %742, 1.500000e+02
  %777 = fcmp reassoc ninf nsz olt float %775, 0x3FC99999A0000000
  %.040.us = select i1 %776, i1 %777, i1 false
  br i1 %.040.us, label %true_block42.us, label %false_block43.us

false_block43.us:                                 ; preds = %true_block36.us
  %778 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %775, float 0.000000e+00)
  %779 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %742)
  %780 = fmul reassoc ninf nsz float %779, 2.025000e+02
  %781 = fmul reassoc ninf nsz float %780, %778
  %782 = fcmp reassoc ninf nsz ogt float %781, 3.000000e+00
  br i1 %782, label %after_if38.us, label %false_block46.us

false_block46.us:                                 ; preds = %false_block43.us
  %783 = fcmp reassoc ninf nsz olt float %781, -3.000000e+00
  br i1 %783, label %after_if38.us, label %false_block49.us

false_block49.us:                                 ; preds = %false_block46.us
  %784 = fmul reassoc ninf nsz float %781, %781
  %785 = fadd reassoc ninf nsz float %784, 2.700000e+01
  %786 = fmul reassoc ninf nsz float %785, %781
  %787 = fmul reassoc ninf nsz float %784, 9.000000e+00
  %788 = fadd reassoc ninf nsz float %787, 2.700000e+01
  %789 = fdiv reassoc ninf nsz float %786, %788
  %790 = fadd reassoc ninf nsz float %789, 1.000000e+00
  br label %after_if38.us

true_block42.us:                                  ; preds = %true_block36.us
  %791 = fsub reassoc ninf nsz float 1.500000e+00, %775
  %792 = fmul reassoc ninf nsz float %791, %719
  br label %after_if38.us

after_if38.us:                                    ; preds = %true_block42.us, %false_block49.us, %false_block46.us, %false_block43.us, %true_block30.us, %after_if14.us
  %.047.us = phi float [ %792, %true_block42.us ], [ %719, %true_block30.us ], [ %719, %after_if14.us ], [ %719, %false_block43.us ], [ %719, %false_block49.us ], [ %719, %false_block46.us ]
  %.043.us = phi float [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %true_block30.us ], [ 1.000000e+00, %after_if14.us ], [ 2.000000e+00, %false_block43.us ], [ %790, %false_block49.us ], [ 0.000000e+00, %false_block46.us ]
  %793 = fmul reassoc ninf nsz float %.043.us, %.046.us
  %794 = fmul reassoc ninf nsz float %793, %.047.us
  %795 = fadd reassoc ninf nsz float %794, %.15371.us
  %796 = fadd reassoc ninf nsz float %793, %.15172.us
  %lsr.iv.next424 = add i32 %lsr.iv423, 2
  %lsr.iv.next428 = add i32 %lsr.iv427, 2
  %lsr.iv.next432 = add i32 %lsr.iv431, 2
  %lsr.iv.next436 = add i32 %lsr.iv435, 2
  %lsr.iv.next440 = add i32 %lsr.iv439, 2
  %lsr.iv.next444 = add i32 %lsr.iv443, 2
  %lsr.iv.next446 = add i64 %lsr.iv445, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next446, 0
  br i1 %exitcond.not, label %for_loop_test11.after_for10_crit_edge.us.loopexit, label %for_loop_body8.us, !llvm.loop !15

for_loop_test11.after_for10_crit_edge.us.loopexit: ; preds = %after_if38.us
  br label %for_loop_test11.after_for10_crit_edge.us

for_loop_test11.after_for10_crit_edge.us:         ; preds = %for_loop_test11.after_for10_crit_edge.us.loopexit, %vec.epilog.middle.block280, %middle.block156
  %.lcssa116 = phi float [ %587, %middle.block156 ], [ %706, %vec.epilog.middle.block280 ], [ %795, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %586, %middle.block156 ], [ %705, %vec.epilog.middle.block280 ], [ %796, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %797 = add nuw nsw i32 %.04977.us, 1
  %lsr.iv.next422 = add i32 %lsr.iv421, %101
  %lsr.iv.next426 = add i32 %lsr.iv425, %98
  %lsr.iv.next430 = add i32 %lsr.iv429, %95
  %lsr.iv.next434 = add i32 %lsr.iv433, %92
  %lsr.iv.next438 = add i32 %lsr.iv437, %89
  %lsr.iv.next442 = add i32 %lsr.iv441, %86
  %exitcond97.not = icmp eq i32 %797, %51
  br i1 %exitcond97.not, label %after_for6, label %iter.check159

after_if3:                                        ; preds = %true_block62, %after_if53, %for_loop_body
  %.sink115 = phi ptr [ %.pre, %true_block62 ], [ %47, %after_if53 ], [ %47, %for_loop_body ]
  %.0.sink = phi float [ %955, %true_block62 ], [ 0.000000e+00, %after_if53 ], [ 0.000000e+00, %for_loop_body ]
  %798 = getelementptr i8, ptr %.sink115, i64 104
  %799 = load ptr, ptr %798, align 8
  %800 = getelementptr i8, ptr %.sink115, i64 100
  %801 = load i32, ptr %800, align 4
  %802 = mul i32 %801, %38
  %803 = add i32 %802, %34
  %804 = sext i32 %803 to i64
  %805 = getelementptr float, ptr %799, i64 %804
  store float %.0.sink, ptr %805, align 4
  %806 = add nsw i32 %.04490, 1
  %exitcond105.not = icmp eq i32 %806, %18
  br i1 %exitcond105.not, label %after_for.loopexit, label %for_loop_body

after_for6:                                       ; preds = %for_loop_test11.after_for10_crit_edge.us
  %807 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %807, label %for_loop_body54.lr.ph.split.us, label %false_block52

for_loop_body54.lr.ph.split.us:                   ; preds = %after_for6, %true_block1
  %808 = getelementptr i8, ptr %47, i64 20
  %809 = getelementptr i8, ptr %47, i64 24
  %810 = getelementptr i8, ptr %47, i64 4
  %811 = getelementptr i8, ptr %47, i64 8
  %812 = load ptr, ptr %811, align 8
  %813 = load i32, ptr %810, align 4
  %814 = load ptr, ptr %809, align 8
  %815 = load i32, ptr %808, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %44, i32 1)
  %smax103 = tail call i32 @llvm.smax.i32(i32 %42, i32 1)
  %wide.trip.count101 = zext i32 %smax to i64
  %816 = add nsw i64 %wide.trip.count101, -1
  %817 = mul i32 %21, %813
  %818 = mul i32 %817, %38
  %819 = add i32 %818, %40
  %820 = mul i32 %21, %815
  %821 = mul i32 %820, %38
  %822 = add i32 %821, %40
  %min.iters.check = icmp slt i32 %44, 4
  %823 = trunc nsw i64 %816 to i32
  %invariant.op415 = add i32 %819, %823
  %invariant.op417 = add i32 %822, %823
  %824 = icmp ugt i64 %816, 4294967295
  %min.iters.check118 = icmp slt i32 %44, 32
  %n.vec = and i64 %wide.trip.count101, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count101
  %n.vec.remaining = and i64 %wide.trip.count101, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec132 = and i64 %wide.trip.count101, 2147483644
  %cmp.n138 = icmp eq i64 %n.vec132, %wide.trip.count101
  %xtraiter = and i64 %wide.trip.count101, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %825 = lshr i64 %wide.trip.count101, 2
  %826 = mul nsw i64 %825, -4
  %827 = zext i32 %822 to i64
  %828 = zext i32 %815 to i64
  %829 = zext i32 %819 to i64
  %830 = zext i32 %813 to i64
  %831 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test61.after_for60_crit_edge.us, %for_loop_body54.lr.ph.split.us
  %lsr.iv465 = phi i64 [ %lsr.iv.next466, %for_loop_test61.after_for60_crit_edge.us ], [ %829, %for_loop_body54.lr.ph.split.us ]
  %lsr.iv463 = phi i64 [ %lsr.iv.next464, %for_loop_test61.after_for60_crit_edge.us ], [ %827, %for_loop_body54.lr.ph.split.us ]
  %.03686.us = phi i32 [ 0, %for_loop_body54.lr.ph.split.us ], [ %936, %for_loop_test61.after_for60_crit_edge.us ]
  %.03785.us = phi float [ 0.000000e+00, %for_loop_body54.lr.ph.split.us ], [ %.lcssa117, %for_loop_test61.after_for60_crit_edge.us ]
  %lsr480 = trunc i64 %lsr.iv465 to i32
  %lsr478 = trunc i64 %lsr.iv463 to i32
  br i1 %min.iters.check, label %for_loop_body58.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %832 = mul i32 %815, %.03686.us
  %833 = add i32 %822, %832
  %834 = mul i32 %813, %.03686.us
  %835 = add i32 %819, %834
  %.reass416 = add i32 %834, %invariant.op415
  %836 = icmp slt i32 %.reass416, %835
  %.reass418 = add i32 %832, %invariant.op417
  %837 = icmp slt i32 %.reass418, %833
  %838 = or i1 %837, %824
  %839 = or i1 %836, %838
  br i1 %839, label %for_loop_body58.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check118, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %840 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.03785.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv455 = phi i32 [ %lsr.iv.next456, %vector.body ], [ %lsr478, %vector.ph ]
  %lsr.iv451 = phi i32 [ %lsr.iv.next452, %vector.body ], [ %lsr480, %vector.ph ]
  %lsr.iv447 = phi i64 [ %lsr.iv.next448, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %840, %vector.ph ], [ %859, %vector.body ]
  %vec.phi119 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %860, %vector.body ]
  %vec.phi120 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %861, %vector.body ]
  %vec.phi121 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %862, %vector.body ]
  %841 = sext i32 %lsr.iv451 to i64
  %842 = getelementptr float, ptr %812, i64 %841
  %843 = getelementptr i8, ptr %842, i64 32
  %844 = getelementptr i8, ptr %842, i64 64
  %845 = getelementptr i8, ptr %842, i64 96
  %wide.load = load <8 x float>, ptr %842, align 4
  %wide.load122 = load <8 x float>, ptr %843, align 4
  %wide.load123 = load <8 x float>, ptr %844, align 4
  %wide.load124 = load <8 x float>, ptr %845, align 4
  %846 = sext i32 %lsr.iv455 to i64
  %847 = getelementptr float, ptr %814, i64 %846
  %848 = getelementptr i8, ptr %847, i64 32
  %849 = getelementptr i8, ptr %847, i64 64
  %850 = getelementptr i8, ptr %847, i64 96
  %wide.load125 = load <8 x float>, ptr %847, align 4
  %wide.load126 = load <8 x float>, ptr %848, align 4
  %wide.load127 = load <8 x float>, ptr %849, align 4
  %wide.load128 = load <8 x float>, ptr %850, align 4
  %851 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load125
  %852 = fsub reassoc ninf nsz <8 x float> %wide.load122, %wide.load126
  %853 = fsub reassoc ninf nsz <8 x float> %wide.load123, %wide.load127
  %854 = fsub reassoc ninf nsz <8 x float> %wide.load124, %wide.load128
  %855 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %851)
  %856 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %852)
  %857 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %853)
  %858 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %854)
  %859 = fadd reassoc ninf nsz <8 x float> %855, %vec.phi
  %860 = fadd reassoc ninf nsz <8 x float> %856, %vec.phi119
  %861 = fadd reassoc ninf nsz <8 x float> %857, %vec.phi120
  %862 = fadd reassoc ninf nsz <8 x float> %858, %vec.phi121
  %lsr.iv.next448 = add nsw i64 %lsr.iv447, -32
  %lsr.iv.next452 = add i32 %lsr.iv451, 32
  %lsr.iv.next456 = add i32 %lsr.iv455, 32
  %863 = icmp eq i64 %lsr.iv.next448, 0
  br i1 %863, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %860, %859
  %bin.rdx129 = fadd reassoc ninf nsz <8 x float> %861, %bin.rdx
  %bin.rdx130 = fadd reassoc ninf nsz <8 x float> %862, %bin.rdx129
  %864 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx130)
  br i1 %cmp.n, label %for_loop_test61.after_for60_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body58.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %864, %vec.epilog.iter.check ], [ %.03785.us, %vector.main.loop.iter.check ]
  %865 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %866 = add i64 %826, %vec.epilog.resume.val
  %867 = trunc i64 %vec.epilog.resume.val to i32
  %868 = add i32 %lsr480, %867
  %869 = add i32 %lsr478, %867
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv461 = phi i32 [ %lsr.iv.next462, %vec.epilog.vector.body ], [ %869, %vec.epilog.ph ]
  %lsr.iv459 = phi i32 [ %lsr.iv.next460, %vec.epilog.vector.body ], [ %868, %vec.epilog.ph ]
  %lsr.iv457 = phi i64 [ %lsr.iv.next458, %vec.epilog.vector.body ], [ %866, %vec.epilog.ph ]
  %vec.phi134 = phi <4 x float> [ %865, %vec.epilog.ph ], [ %876, %vec.epilog.vector.body ]
  %870 = sext i32 %lsr.iv459 to i64
  %871 = getelementptr float, ptr %812, i64 %870
  %wide.load135 = load <4 x float>, ptr %871, align 4
  %872 = sext i32 %lsr.iv461 to i64
  %873 = getelementptr float, ptr %814, i64 %872
  %wide.load136 = load <4 x float>, ptr %873, align 4
  %874 = fsub reassoc ninf nsz <4 x float> %wide.load135, %wide.load136
  %875 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %874)
  %876 = fadd reassoc ninf nsz <4 x float> %875, %vec.phi134
  %lsr.iv.next458 = add i64 %lsr.iv457, 4
  %lsr.iv.next460 = add i32 %lsr.iv459, 4
  %lsr.iv.next462 = add i32 %lsr.iv461, 4
  %877 = icmp eq i64 %lsr.iv.next458, 0
  br i1 %877, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %878 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %876)
  br i1 %cmp.n138, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader

for_loop_body58.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv98.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec132, %vec.epilog.middle.block ]
  %.181.us.ph = phi float [ %864, %vec.epilog.iter.check ], [ %.03785.us, %iter.check ], [ %.03785.us, %vector.scevcheck ], [ %878, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body58.us.prol.loopexit, label %for_loop_body58.us.prol.preheader

for_loop_body58.us.prol.preheader:                ; preds = %for_loop_body58.us.preheader
  br label %for_loop_body58.us.prol

for_loop_body58.us.prol:                          ; preds = %for_loop_body58.us.prol, %for_loop_body58.us.prol.preheader
  %lsr.iv468 = phi i64 [ %831, %for_loop_body58.us.prol.preheader ], [ %lsr.iv.next469, %for_loop_body58.us.prol ]
  %indvars.iv98.prol = phi i64 [ %indvars.iv.next99.prol, %for_loop_body58.us.prol ], [ %indvars.iv98.ph, %for_loop_body58.us.prol.preheader ]
  %.181.us.prol = phi float [ %889, %for_loop_body58.us.prol ], [ %.181.us.ph, %for_loop_body58.us.prol.preheader ]
  %879 = add i64 %lsr.iv465, %indvars.iv98.prol
  %tmp467 = trunc i64 %879 to i32
  %880 = sext i32 %tmp467 to i64
  %881 = getelementptr float, ptr %812, i64 %880
  %882 = load float, ptr %881, align 4
  %883 = add i64 %lsr.iv463, %indvars.iv98.prol
  %tmp = trunc i64 %883 to i32
  %884 = sext i32 %tmp to i64
  %885 = getelementptr float, ptr %814, i64 %884
  %886 = load float, ptr %885, align 4
  %887 = fsub reassoc ninf nsz float %882, %886
  %888 = tail call noundef float @llvm.fabs.f32(float %887)
  %889 = fadd reassoc ninf nsz float %888, %.181.us.prol
  %indvars.iv.next99.prol = add nuw nsw i64 %indvars.iv98.prol, 1
  %lsr.iv.next469 = add nsw i64 %lsr.iv468, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next469, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body58.us.prol.loopexit.loopexit, label %for_loop_body58.us.prol, !llvm.loop !18

for_loop_body58.us.prol.loopexit.loopexit:        ; preds = %for_loop_body58.us.prol
  br label %for_loop_body58.us.prol.loopexit

for_loop_body58.us.prol.loopexit:                 ; preds = %for_loop_body58.us.prol.loopexit.loopexit, %for_loop_body58.us.preheader
  %.lcssa373.unr = phi float [ poison, %for_loop_body58.us.preheader ], [ %889, %for_loop_body58.us.prol.loopexit.loopexit ]
  %indvars.iv98.unr = phi i64 [ %indvars.iv98.ph, %for_loop_body58.us.preheader ], [ %indvars.iv.next99.prol, %for_loop_body58.us.prol.loopexit.loopexit ]
  %.181.us.unr = phi float [ %.181.us.ph, %for_loop_body58.us.preheader ], [ %889, %for_loop_body58.us.prol.loopexit.loopexit ]
  %890 = sub nsw i64 %indvars.iv98.ph, %wide.trip.count101
  %891 = icmp ugt i64 %890, -4
  br i1 %891, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader.new

for_loop_body58.us.preheader.new:                 ; preds = %for_loop_body58.us.prol.loopexit
  br label %for_loop_body58.us

for_loop_body58.us:                               ; preds = %for_loop_body58.us, %for_loop_body58.us.preheader.new
  %indvars.iv98 = phi i64 [ %indvars.iv98.unr, %for_loop_body58.us.preheader.new ], [ %indvars.iv.next99.3, %for_loop_body58.us ]
  %.181.us = phi float [ %.181.us.unr, %for_loop_body58.us.preheader.new ], [ %935, %for_loop_body58.us ]
  %892 = add i64 %lsr.iv465, %indvars.iv98
  %tmp477 = trunc i64 %892 to i32
  %893 = sext i32 %tmp477 to i64
  %894 = getelementptr float, ptr %812, i64 %893
  %895 = load float, ptr %894, align 4
  %896 = add i64 %lsr.iv463, %indvars.iv98
  %tmp476 = trunc i64 %896 to i32
  %897 = sext i32 %tmp476 to i64
  %898 = getelementptr float, ptr %814, i64 %897
  %899 = load float, ptr %898, align 4
  %900 = fsub reassoc ninf nsz float %895, %899
  %901 = tail call noundef float @llvm.fabs.f32(float %900)
  %902 = fadd reassoc ninf nsz float %901, %.181.us
  %903 = add i64 %892, 1
  %tmp475 = trunc i64 %903 to i32
  %904 = sext i32 %tmp475 to i64
  %905 = getelementptr float, ptr %812, i64 %904
  %906 = load float, ptr %905, align 4
  %907 = add i64 %896, 1
  %tmp474 = trunc i64 %907 to i32
  %908 = sext i32 %tmp474 to i64
  %909 = getelementptr float, ptr %814, i64 %908
  %910 = load float, ptr %909, align 4
  %911 = fsub reassoc ninf nsz float %906, %910
  %912 = tail call noundef float @llvm.fabs.f32(float %911)
  %913 = fadd reassoc ninf nsz float %912, %902
  %914 = add i64 %892, 2
  %tmp473 = trunc i64 %914 to i32
  %915 = sext i32 %tmp473 to i64
  %916 = getelementptr float, ptr %812, i64 %915
  %917 = load float, ptr %916, align 4
  %918 = add i64 %896, 2
  %tmp472 = trunc i64 %918 to i32
  %919 = sext i32 %tmp472 to i64
  %920 = getelementptr float, ptr %814, i64 %919
  %921 = load float, ptr %920, align 4
  %922 = fsub reassoc ninf nsz float %917, %921
  %923 = tail call noundef float @llvm.fabs.f32(float %922)
  %924 = fadd reassoc ninf nsz float %923, %913
  %925 = add i64 %892, 3
  %tmp471 = trunc i64 %925 to i32
  %926 = sext i32 %tmp471 to i64
  %927 = getelementptr float, ptr %812, i64 %926
  %928 = load float, ptr %927, align 4
  %929 = add i64 %896, 3
  %tmp470 = trunc i64 %929 to i32
  %930 = sext i32 %tmp470 to i64
  %931 = getelementptr float, ptr %814, i64 %930
  %932 = load float, ptr %931, align 4
  %933 = fsub reassoc ninf nsz float %928, %932
  %934 = tail call noundef float @llvm.fabs.f32(float %933)
  %935 = fadd reassoc ninf nsz float %934, %924
  %indvars.iv.next99.3 = add nuw nsw i64 %indvars.iv98, 4
  %exitcond102.not.3 = icmp eq i64 %wide.trip.count101, %indvars.iv.next99.3
  br i1 %exitcond102.not.3, label %for_loop_test61.after_for60_crit_edge.us.loopexit, label %for_loop_body58.us, !llvm.loop !20

for_loop_test61.after_for60_crit_edge.us.loopexit: ; preds = %for_loop_body58.us
  br label %for_loop_test61.after_for60_crit_edge.us

for_loop_test61.after_for60_crit_edge.us:         ; preds = %for_loop_test61.after_for60_crit_edge.us.loopexit, %for_loop_body58.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa117 = phi float [ %864, %middle.block ], [ %878, %vec.epilog.middle.block ], [ %.lcssa373.unr, %for_loop_body58.us.prol.loopexit ], [ %935, %for_loop_test61.after_for60_crit_edge.us.loopexit ]
  %936 = add nuw nsw i32 %.03686.us, 1
  %lsr.iv.next466 = add i64 %lsr.iv465, %830
  %lsr.iv.next464 = add i64 %lsr.iv463, %828
  %exitcond104.not = icmp eq i32 %936, %smax103
  br i1 %exitcond104.not, label %after_for56, label %iter.check

false_block52:                                    ; preds = %after_for6
  %937 = fdiv reassoc ninf nsz float %.lcssa116, %.lcssa
  br label %after_if53

after_if53:                                       ; preds = %after_for56, %false_block52
  %.038 = phi float [ %951, %after_for56 ], [ %937, %false_block52 ]
  %938 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %49, float 0x3EB0C6F7A0000000)
  %939 = fdiv reassoc ninf nsz float %.038, %938
  %940 = getelementptr i8, ptr %47, i64 136
  %941 = load float, ptr %940, align 4
  %942 = fsub reassoc ninf nsz float %939, %941
  %943 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %942, float 0.000000e+00)
  %944 = getelementptr i8, ptr %47, i64 132
  %945 = load float, ptr %944, align 4
  %946 = fmul reassoc ninf nsz float %945, 5.000000e-01
  %947 = fmul reassoc ninf nsz float %946, %943
  %948 = fcmp reassoc ninf nsz ugt float %947, 2.000000e+01
  br i1 %948, label %after_if3, label %true_block62

after_for56:                                      ; preds = %for_loop_test61.after_for60_crit_edge.us
  %949 = mul i32 %42, %44
  %950 = sitofp i32 %949 to float
  %951 = fdiv reassoc ninf nsz float %.lcssa117, %950
  br label %after_if53

true_block62:                                     ; preds = %after_if53
  %952 = fadd reassoc ninf nsz float %947, -2.000000e+00
  %953 = tail call noundef float @expf(float noundef %952) #9
  %954 = fadd reassoc ninf nsz float %953, 1.000000e+00
  %955 = fdiv reassoc ninf nsz float 1.000000e+00, %954
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
