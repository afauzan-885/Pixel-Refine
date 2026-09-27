; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.10 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @phase1_coarse_analysis_kernel_c744_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 128
  %2 = load float, ptr %1, align 4
  %3 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 12
  store float %2, ptr %7, align 4
  %8 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2, float 0x3EB0C6F7A0000000)
  %9 = fdiv reassoc ninf nsz float 1.000000e+00, %8
  %10 = load ptr, ptr %3, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 16
  store float %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 96
  %16 = load i32, ptr %15, align 4
  %17 = load ptr, ptr %3, align 8
  %18 = getelementptr inbounds nuw i8, ptr %17, i64 32872
  %19 = load ptr, ptr %18, align 8
  %20 = getelementptr inbounds nuw i8, ptr %19, i64 8
  store i32 %16, ptr %20, align 4
  %21 = load ptr, ptr %context, align 8
  %22 = getelementptr i8, ptr %21, i64 100
  %23 = load i32, ptr %22, align 4
  %24 = load ptr, ptr %3, align 8
  %25 = getelementptr inbounds nuw i8, ptr %24, i64 32872
  %26 = load ptr, ptr %25, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 4
  store i32 %23, ptr %27, align 4
  %28 = mul i32 %23, %16
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  store i32 %28, ptr %31, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

define void @phase1_coarse_analysis_kernel_c744_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
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
  %.04490 = phi i32 [ %821, %after_if3 ], [ %16, %for_loop_body.preheader ]
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
  br i1 %spec.select, label %true_block1, label %after_if3.sink.split

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body
  %47 = getelementptr inbounds nuw i8, ptr %31, i64 12
  %48 = load float, ptr %47, align 4
  %49 = fmul reassoc ninf nsz float %48, 0x3FC99999A0000000
  %50 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %49, float 0x3F747AE140000000)
  %51 = fmul reassoc ninf nsz float %48, %48
  %52 = fmul reassoc ninf nsz float %51, 4.000000e+00
  %53 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %52, float 0x3F62E62140000000)
  %54 = fcmp reassoc ninf nsz ogt float %48, 0x3EB0C6F7A0000000
  %55 = add nsw i32 %42, -1
  %56 = lshr i32 %55, 1
  %57 = add i32 %39, 1
  %58 = add i32 %40, 1
  %59 = load ptr, ptr %0, align 8
  %.not = icmp samesign ult i32 %42, 3
  %.not91 = icmp samesign ult i32 %44, 3
  %or.cond = select i1 %.not, i1 true, i1 %.not91
  br i1 %or.cond, label %for_loop_body54.lr.ph.split.us, label %for_loop_body4.lr.ph.split.us

for_loop_body4.lr.ph.split.us:                    ; preds = %true_block1
  %60 = add nsw i32 %44, -1
  %61 = lshr i32 %60, 1
  %62 = getelementptr i8, ptr %59, i64 84
  %63 = getelementptr i8, ptr %59, i64 88
  %64 = getelementptr i8, ptr %59, i64 68
  %65 = getelementptr i8, ptr %59, i64 72
  %66 = getelementptr i8, ptr %59, i64 52
  %67 = getelementptr i8, ptr %59, i64 56
  %68 = getelementptr i8, ptr %59, i64 36
  %69 = getelementptr i8, ptr %59, i64 40
  %70 = getelementptr i8, ptr %59, i64 20
  %71 = getelementptr i8, ptr %59, i64 24
  %72 = getelementptr i8, ptr %59, i64 4
  %73 = getelementptr i8, ptr %59, i64 8
  %74 = load ptr, ptr %73, align 8
  %75 = load i32, ptr %72, align 4
  %76 = load ptr, ptr %71, align 8
  %77 = load i32, ptr %70, align 4
  %78 = load ptr, ptr %69, align 8
  %79 = load i32, ptr %68, align 4
  %80 = load ptr, ptr %67, align 8
  %81 = load i32, ptr %66, align 4
  %82 = load ptr, ptr %65, align 8
  %83 = load i32, ptr %64, align 4
  %84 = load ptr, ptr %63, align 8
  %85 = load i32, ptr %62, align 4
  %wide.trip.count = zext i32 %61 to i64
  %86 = add nsw i64 %wide.trip.count, -1
  %87 = mul i32 %75, %57
  %88 = add i32 %58, %87
  %89 = shl i32 %75, 1
  %90 = mul i32 %77, %57
  %91 = add i32 %58, %90
  %92 = shl i32 %77, 1
  %93 = mul i32 %79, %57
  %94 = add i32 %58, %93
  %95 = shl i32 %79, 1
  %96 = mul i32 %81, %57
  %97 = add i32 %58, %96
  %98 = shl i32 %81, 1
  %99 = mul i32 %83, %57
  %100 = add i32 %58, %99
  %101 = shl i32 %83, 1
  %102 = mul i32 %85, %57
  %103 = add i32 %58, %102
  %104 = shl i32 %85, 1
  %min.iters.check157 = icmp ult i32 %44, 17
  %105 = trunc nsw i64 %86 to i32
  %mul.result = shl i32 %105, 1
  %invariant.op401 = add i32 %88, %mul.result
  %invariant.op403 = add i32 %91, %mul.result
  %106 = icmp ugt i64 %86, 4294967295
  %invariant.op405 = add i32 %94, %mul.result
  %invariant.op407 = add i32 %97, %mul.result
  %invariant.op409 = add i32 %100, %mul.result
  %invariant.op411 = add i32 %103, %mul.result
  %min.iters.check160 = icmp ult i32 %44, 65
  %n.vec164 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %54, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %107 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert175 = insertelement <8 x i32> poison, i32 %58, i64 0
  %broadcast.splat176 = shufflevector <8 x i32> %broadcast.splatinsert175, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert212 = insertelement <8 x float> poison, float %50, i64 0
  %broadcast.splat213 = shufflevector <8 x float> %broadcast.splatinsert212, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert214 = insertelement <8 x float> poison, float %53, i64 0
  %broadcast.splat215 = shufflevector <8 x float> %broadcast.splatinsert214, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat176
  %invariant.op397 = add <8 x i32> splat (i32 32), %broadcast.splat176
  %invariant.op399 = add <8 x i32> splat (i32 48), %broadcast.splat176
  %cmp.n278 = icmp eq i64 %n.vec164, %wide.trip.count
  %n.vec.remaining286 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check287 = icmp eq i64 %n.vec.remaining286, 0
  %n.vec289 = and i64 %wide.trip.count, 2147483640
  %cmp.n337 = icmp eq i64 %n.vec289, %wide.trip.count
  %108 = zext i32 %60 to i64
  %109 = lshr i64 %108, 4
  %110 = mul nsw i64 %109, -8
  %111 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check159

iter.check159:                                    ; preds = %for_loop_test11.after_for10_crit_edge.us, %for_loop_body4.lr.ph.split.us
  %lsr.iv445 = phi i32 [ %lsr.iv.next446, %for_loop_test11.after_for10_crit_edge.us ], [ %88, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv441 = phi i32 [ %lsr.iv.next442, %for_loop_test11.after_for10_crit_edge.us ], [ %91, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv437 = phi i32 [ %lsr.iv.next438, %for_loop_test11.after_for10_crit_edge.us ], [ %94, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv433 = phi i32 [ %lsr.iv.next434, %for_loop_test11.after_for10_crit_edge.us ], [ %97, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv429 = phi i32 [ %lsr.iv.next430, %for_loop_test11.after_for10_crit_edge.us ], [ %100, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv425 = phi i32 [ %lsr.iv.next426, %for_loop_test11.after_for10_crit_edge.us ], [ %103, %for_loop_body4.lr.ph.split.us ]
  %.04977.us = phi i32 [ 0, %for_loop_body4.lr.ph.split.us ], [ %812, %for_loop_test11.after_for10_crit_edge.us ]
  %.05076.us = phi float [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ], [ %.lcssa, %for_loop_test11.after_for10_crit_edge.us ]
  %.05275.us = phi float [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ], [ %.lcssa116, %for_loop_test11.after_for10_crit_edge.us ]
  %112 = shl nuw i32 %.04977.us, 1
  %113 = add i32 %57, %112
  %114 = mul i32 %75, %113
  %115 = mul i32 %77, %113
  %116 = mul i32 %79, %113
  %117 = mul i32 %81, %113
  %118 = mul i32 %83, %113
  %119 = mul i32 %85, %113
  br i1 %min.iters.check157, label %for_loop_body8.us.preheader, label %vector.scevcheck140

vector.scevcheck140:                              ; preds = %iter.check159
  %120 = mul i32 %104, %.04977.us
  %121 = add i32 %103, %120
  %122 = mul i32 %101, %.04977.us
  %123 = add i32 %100, %122
  %124 = mul i32 %98, %.04977.us
  %125 = add i32 %97, %124
  %126 = mul i32 %95, %.04977.us
  %127 = add i32 %94, %126
  %128 = mul i32 %92, %.04977.us
  %129 = add i32 %91, %128
  %130 = mul i32 %89, %.04977.us
  %131 = add i32 %88, %130
  %.reass402 = add i32 %130, %invariant.op401
  %132 = icmp slt i32 %.reass402, %131
  %.reass404 = add i32 %128, %invariant.op403
  %133 = icmp slt i32 %.reass404, %129
  %134 = or i1 %133, %106
  %.reass406 = add i32 %126, %invariant.op405
  %135 = icmp slt i32 %.reass406, %127
  %.reass408 = add i32 %124, %invariant.op407
  %136 = icmp slt i32 %.reass408, %125
  %.reass410 = add i32 %122, %invariant.op409
  %137 = icmp slt i32 %.reass410, %123
  %.reass412 = add i32 %120, %invariant.op411
  %138 = icmp slt i32 %.reass412, %121
  %139 = or i1 %132, %134
  %140 = or i1 %135, %139
  %141 = or i1 %136, %140
  %142 = or i1 %137, %141
  %143 = or i1 %138, %142
  br i1 %143, label %for_loop_body8.us.preheader, label %vector.main.loop.iter.check161

vector.main.loop.iter.check161:                   ; preds = %vector.scevcheck140
  br i1 %min.iters.check160, label %vec.epilog.ph284, label %vector.ph162

vector.ph162:                                     ; preds = %vector.main.loop.iter.check161
  %144 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05076.us, i64 0
  %145 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05275.us, i64 0
  %broadcast.splatinsert177 = insertelement <8 x i32> poison, i32 %114, i64 0
  %broadcast.splat178 = shufflevector <8 x i32> %broadcast.splatinsert177, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert182 = insertelement <8 x i32> poison, i32 %115, i64 0
  %broadcast.splat183 = shufflevector <8 x i32> %broadcast.splatinsert182, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert188 = insertelement <8 x i32> poison, i32 %116, i64 0
  %broadcast.splat189 = shufflevector <8 x i32> %broadcast.splatinsert188, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert194 = insertelement <8 x i32> poison, i32 %117, i64 0
  %broadcast.splat195 = shufflevector <8 x i32> %broadcast.splatinsert194, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert200 = insertelement <8 x i32> poison, i32 %118, i64 0
  %broadcast.splat201 = shufflevector <8 x i32> %broadcast.splatinsert200, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert206 = insertelement <8 x i32> poison, i32 %119, i64 0
  %broadcast.splat207 = shufflevector <8 x i32> %broadcast.splatinsert206, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body165

vector.body165:                                   ; preds = %vector.body165, %vector.ph162
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body165 ], [ %n.vec164, %vector.ph162 ]
  %vec.phi167 = phi <8 x float> [ %144, %vector.ph162 ], [ %592, %vector.body165 ]
  %vec.phi168 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %593, %vector.body165 ]
  %vec.phi169 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %594, %vector.body165 ]
  %vec.phi170 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %595, %vector.body165 ]
  %vec.phi171 = phi <8 x float> [ %145, %vector.ph162 ], [ %588, %vector.body165 ]
  %vec.phi172 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %589, %vector.body165 ]
  %vec.phi173 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %590, %vector.body165 ]
  %vec.phi174 = phi <8 x float> [ zeroinitializer, %vector.ph162 ], [ %591, %vector.body165 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph162 ], [ %vec.ind.next, %vector.body165 ]
  %146 = shl <8 x i32> %vec.ind, splat (i32 1)
  %147 = add <8 x i32> %broadcast.splat176, %146
  %.reass = add <8 x i32> %146, %invariant.op
  %.reass398 = add <8 x i32> %146, %invariant.op397
  %.reass400 = add <8 x i32> %146, %invariant.op399
  %148 = add <8 x i32> %broadcast.splat178, %147
  %149 = add <8 x i32> %broadcast.splat178, %.reass
  %150 = add <8 x i32> %broadcast.splat178, %.reass398
  %151 = add <8 x i32> %broadcast.splat178, %.reass400
  %152 = sext <8 x i32> %148 to <8 x i64>
  %153 = sext <8 x i32> %149 to <8 x i64>
  %154 = sext <8 x i32> %150 to <8 x i64>
  %155 = sext <8 x i32> %151 to <8 x i64>
  %156 = getelementptr float, ptr %74, <8 x i64> %152
  %157 = getelementptr float, ptr %74, <8 x i64> %153
  %158 = getelementptr float, ptr %74, <8 x i64> %154
  %159 = getelementptr float, ptr %74, <8 x i64> %155
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %156, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather179 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %157, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather180 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %158, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather181 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %159, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %160 = add <8 x i32> %broadcast.splat183, %147
  %161 = add <8 x i32> %broadcast.splat183, %.reass
  %162 = add <8 x i32> %broadcast.splat183, %.reass398
  %163 = add <8 x i32> %broadcast.splat183, %.reass400
  %164 = sext <8 x i32> %160 to <8 x i64>
  %165 = sext <8 x i32> %161 to <8 x i64>
  %166 = sext <8 x i32> %162 to <8 x i64>
  %167 = sext <8 x i32> %163 to <8 x i64>
  %168 = getelementptr float, ptr %76, <8 x i64> %164
  %169 = getelementptr float, ptr %76, <8 x i64> %165
  %170 = getelementptr float, ptr %76, <8 x i64> %166
  %171 = getelementptr float, ptr %76, <8 x i64> %167
  %wide.masked.gather184 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %168, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather185 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %169, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather186 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %170, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather187 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %171, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %172 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather184
  %173 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather179, %wide.masked.gather185
  %174 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather180, %wide.masked.gather186
  %175 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather181, %wide.masked.gather187
  %176 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %172)
  %177 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %173)
  %178 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %174)
  %179 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %175)
  %180 = add <8 x i32> %broadcast.splat189, %147
  %181 = add <8 x i32> %broadcast.splat189, %.reass
  %182 = add <8 x i32> %broadcast.splat189, %.reass398
  %183 = add <8 x i32> %broadcast.splat189, %.reass400
  %184 = sext <8 x i32> %180 to <8 x i64>
  %185 = sext <8 x i32> %181 to <8 x i64>
  %186 = sext <8 x i32> %182 to <8 x i64>
  %187 = sext <8 x i32> %183 to <8 x i64>
  %188 = getelementptr float, ptr %78, <8 x i64> %184
  %189 = getelementptr float, ptr %78, <8 x i64> %185
  %190 = getelementptr float, ptr %78, <8 x i64> %186
  %191 = getelementptr float, ptr %78, <8 x i64> %187
  %wide.masked.gather190 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %188, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather191 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %189, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather192 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %190, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather193 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %191, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %192 = add <8 x i32> %broadcast.splat195, %147
  %193 = add <8 x i32> %broadcast.splat195, %.reass
  %194 = add <8 x i32> %broadcast.splat195, %.reass398
  %195 = add <8 x i32> %broadcast.splat195, %.reass400
  %196 = sext <8 x i32> %192 to <8 x i64>
  %197 = sext <8 x i32> %193 to <8 x i64>
  %198 = sext <8 x i32> %194 to <8 x i64>
  %199 = sext <8 x i32> %195 to <8 x i64>
  %200 = getelementptr float, ptr %80, <8 x i64> %196
  %201 = getelementptr float, ptr %80, <8 x i64> %197
  %202 = getelementptr float, ptr %80, <8 x i64> %198
  %203 = getelementptr float, ptr %80, <8 x i64> %199
  %wide.masked.gather196 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %200, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather197 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %201, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather198 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %202, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather199 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %203, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %204 = add <8 x i32> %broadcast.splat201, %147
  %205 = add <8 x i32> %broadcast.splat201, %.reass
  %206 = add <8 x i32> %broadcast.splat201, %.reass398
  %207 = add <8 x i32> %broadcast.splat201, %.reass400
  %208 = sext <8 x i32> %204 to <8 x i64>
  %209 = sext <8 x i32> %205 to <8 x i64>
  %210 = sext <8 x i32> %206 to <8 x i64>
  %211 = sext <8 x i32> %207 to <8 x i64>
  %212 = getelementptr float, ptr %82, <8 x i64> %208
  %213 = getelementptr float, ptr %82, <8 x i64> %209
  %214 = getelementptr float, ptr %82, <8 x i64> %210
  %215 = getelementptr float, ptr %82, <8 x i64> %211
  %wide.masked.gather202 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %212, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather203 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %213, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather204 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %214, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather205 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %215, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %216 = add <8 x i32> %broadcast.splat207, %147
  %217 = add <8 x i32> %broadcast.splat207, %.reass
  %218 = add <8 x i32> %broadcast.splat207, %.reass398
  %219 = add <8 x i32> %broadcast.splat207, %.reass400
  %220 = sext <8 x i32> %216 to <8 x i64>
  %221 = sext <8 x i32> %217 to <8 x i64>
  %222 = sext <8 x i32> %218 to <8 x i64>
  %223 = sext <8 x i32> %219 to <8 x i64>
  %224 = getelementptr float, ptr %84, <8 x i64> %220
  %225 = getelementptr float, ptr %84, <8 x i64> %221
  %226 = getelementptr float, ptr %84, <8 x i64> %222
  %227 = getelementptr float, ptr %84, <8 x i64> %223
  %wide.masked.gather208 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %224, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather209 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %225, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather210 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %226, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather211 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %227, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %228 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather190, %wide.masked.gather190
  %229 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather191, %wide.masked.gather191
  %230 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather192, %wide.masked.gather192
  %231 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather193, %wide.masked.gather193
  %232 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather196, %wide.masked.gather196
  %233 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather197, %wide.masked.gather197
  %234 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather198, %wide.masked.gather198
  %235 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather199, %wide.masked.gather199
  %236 = fadd reassoc ninf nsz <8 x float> %232, %228
  %237 = fadd reassoc ninf nsz <8 x float> %233, %229
  %238 = fadd reassoc ninf nsz <8 x float> %234, %230
  %239 = fadd reassoc ninf nsz <8 x float> %235, %231
  %240 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, %wide.masked.gather202
  %241 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, %wide.masked.gather203
  %242 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, %wide.masked.gather204
  %243 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather205, %wide.masked.gather205
  %244 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather208, %wide.masked.gather208
  %245 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather209, %wide.masked.gather209
  %246 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather210, %wide.masked.gather210
  %247 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather211, %wide.masked.gather211
  %248 = fadd reassoc ninf nsz <8 x float> %244, %240
  %249 = fadd reassoc ninf nsz <8 x float> %245, %241
  %250 = fadd reassoc ninf nsz <8 x float> %246, %242
  %251 = fadd reassoc ninf nsz <8 x float> %247, %243
  %252 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %236, <8 x float> %248)
  %253 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %237, <8 x float> %249)
  %254 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %238, <8 x float> %250)
  %255 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %239, <8 x float> %251)
  %256 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather184, splat (float -2.000000e+00)
  %257 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather185, splat (float -2.000000e+00)
  %258 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather186, splat (float -2.000000e+00)
  %259 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather187, splat (float -2.000000e+00)
  %260 = fadd reassoc ninf nsz <8 x float> %256, splat (float 3.000000e+00)
  %261 = fadd reassoc ninf nsz <8 x float> %257, splat (float 3.000000e+00)
  %262 = fadd reassoc ninf nsz <8 x float> %258, splat (float 3.000000e+00)
  %263 = fadd reassoc ninf nsz <8 x float> %259, splat (float 3.000000e+00)
  %264 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %260, <8 x float> splat (float 3.000000e+00))
  %265 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %261, <8 x float> splat (float 3.000000e+00))
  %266 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %262, <8 x float> splat (float 3.000000e+00))
  %267 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %263, <8 x float> splat (float 3.000000e+00))
  %268 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %264, <8 x float> splat (float 1.000000e+00))
  %269 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %265, <8 x float> splat (float 1.000000e+00))
  %270 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %266, <8 x float> splat (float 1.000000e+00))
  %271 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %267, <8 x float> splat (float 1.000000e+00))
  %272 = fmul reassoc ninf nsz <8 x float> %268, %broadcast.splat213
  %273 = fmul reassoc ninf nsz <8 x float> %269, %broadcast.splat213
  %274 = fmul reassoc ninf nsz <8 x float> %270, %broadcast.splat213
  %275 = fmul reassoc ninf nsz <8 x float> %271, %broadcast.splat213
  %276 = fmul reassoc ninf nsz <8 x float> %268, %268
  %277 = fmul reassoc ninf nsz <8 x float> %269, %269
  %278 = fmul reassoc ninf nsz <8 x float> %270, %270
  %279 = fmul reassoc ninf nsz <8 x float> %271, %271
  %280 = fmul reassoc ninf nsz <8 x float> %276, %broadcast.splat215
  %281 = fmul reassoc ninf nsz <8 x float> %277, %broadcast.splat215
  %282 = fmul reassoc ninf nsz <8 x float> %278, %broadcast.splat215
  %283 = fmul reassoc ninf nsz <8 x float> %279, %broadcast.splat215
  %284 = fcmp reassoc ninf nsz olt <8 x float> %252, %280
  %285 = fcmp reassoc ninf nsz olt <8 x float> %253, %281
  %286 = fcmp reassoc ninf nsz olt <8 x float> %254, %282
  %287 = fcmp reassoc ninf nsz olt <8 x float> %255, %283
  %288 = xor <8 x i1> %284, splat (i1 true)
  %289 = xor <8 x i1> %285, splat (i1 true)
  %290 = xor <8 x i1> %286, splat (i1 true)
  %291 = xor <8 x i1> %287, splat (i1 true)
  %292 = select <8 x i1> %broadcast.splat, <8 x i1> %288, <8 x i1> zeroinitializer
  %293 = select <8 x i1> %broadcast.splat, <8 x i1> %289, <8 x i1> zeroinitializer
  %294 = select <8 x i1> %broadcast.splat, <8 x i1> %290, <8 x i1> zeroinitializer
  %295 = select <8 x i1> %broadcast.splat, <8 x i1> %291, <8 x i1> zeroinitializer
  %296 = fcmp reassoc ninf nsz olt <8 x float> %176, %272
  %297 = fcmp reassoc ninf nsz olt <8 x float> %177, %273
  %298 = fcmp reassoc ninf nsz olt <8 x float> %178, %274
  %299 = fcmp reassoc ninf nsz olt <8 x float> %179, %275
  %300 = xor <8 x i1> %296, splat (i1 true)
  %301 = xor <8 x i1> %297, splat (i1 true)
  %302 = xor <8 x i1> %298, splat (i1 true)
  %303 = xor <8 x i1> %299, splat (i1 true)
  %304 = select <8 x i1> %292, <8 x i1> %300, <8 x i1> zeroinitializer
  %305 = select <8 x i1> %293, <8 x i1> %301, <8 x i1> zeroinitializer
  %306 = select <8 x i1> %294, <8 x i1> %302, <8 x i1> zeroinitializer
  %307 = select <8 x i1> %295, <8 x i1> %303, <8 x i1> zeroinitializer
  %308 = fmul reassoc ninf nsz <8 x float> %272, splat (float 4.000000e+00)
  %309 = fmul reassoc ninf nsz <8 x float> %273, splat (float 4.000000e+00)
  %310 = fmul reassoc ninf nsz <8 x float> %274, splat (float 4.000000e+00)
  %311 = fmul reassoc ninf nsz <8 x float> %275, splat (float 4.000000e+00)
  %312 = fdiv reassoc ninf nsz <8 x float> %176, %308
  %313 = fdiv reassoc ninf nsz <8 x float> %177, %309
  %314 = fdiv reassoc ninf nsz <8 x float> %178, %310
  %315 = fdiv reassoc ninf nsz <8 x float> %179, %311
  %316 = fcmp reassoc ninf nsz ogt <8 x float> %312, splat (float 1.000000e+00)
  %317 = fcmp reassoc ninf nsz ogt <8 x float> %313, splat (float 1.000000e+00)
  %318 = fcmp reassoc ninf nsz ogt <8 x float> %314, splat (float 1.000000e+00)
  %319 = fcmp reassoc ninf nsz ogt <8 x float> %315, splat (float 1.000000e+00)
  %320 = select <8 x i1> %316, <8 x float> splat (float 1.000000e+00), <8 x float> %312
  %321 = select <8 x i1> %317, <8 x float> splat (float 1.000000e+00), <8 x float> %313
  %322 = select <8 x i1> %318, <8 x float> splat (float 1.000000e+00), <8 x float> %314
  %323 = select <8 x i1> %319, <8 x float> splat (float 1.000000e+00), <8 x float> %315
  %324 = fmul reassoc ninf nsz <8 x float> %320, splat (float 0x3FD99999A0000000)
  %325 = fmul reassoc ninf nsz <8 x float> %321, splat (float 0x3FD99999A0000000)
  %326 = fmul reassoc ninf nsz <8 x float> %322, splat (float 0x3FD99999A0000000)
  %327 = fmul reassoc ninf nsz <8 x float> %323, splat (float 0x3FD99999A0000000)
  %328 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %324
  %329 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %325
  %330 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %326
  %331 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %327
  %332 = select <8 x i1> %292, <8 x i1> %296, <8 x i1> zeroinitializer
  %333 = select <8 x i1> %293, <8 x i1> %297, <8 x i1> zeroinitializer
  %334 = select <8 x i1> %294, <8 x i1> %298, <8 x i1> zeroinitializer
  %335 = select <8 x i1> %295, <8 x i1> %299, <8 x i1> zeroinitializer
  %336 = fmul reassoc ninf nsz <8 x float> %176, splat (float 0x3FC3333340000000)
  %337 = fmul reassoc ninf nsz <8 x float> %177, splat (float 0x3FC3333340000000)
  %338 = fmul reassoc ninf nsz <8 x float> %178, splat (float 0x3FC3333340000000)
  %339 = fmul reassoc ninf nsz <8 x float> %179, splat (float 0x3FC3333340000000)
  %340 = fdiv reassoc ninf nsz <8 x float> %336, %272
  %341 = fdiv reassoc ninf nsz <8 x float> %337, %273
  %342 = fdiv reassoc ninf nsz <8 x float> %338, %274
  %343 = fdiv reassoc ninf nsz <8 x float> %339, %275
  %344 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %340
  %345 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %341
  %346 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %342
  %347 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %343
  %348 = select <8 x i1> %broadcast.splat, <8 x i1> %284, <8 x i1> zeroinitializer
  %349 = select <8 x i1> %broadcast.splat, <8 x i1> %285, <8 x i1> zeroinitializer
  %350 = select <8 x i1> %broadcast.splat, <8 x i1> %286, <8 x i1> zeroinitializer
  %351 = select <8 x i1> %broadcast.splat, <8 x i1> %287, <8 x i1> zeroinitializer
  %352 = fmul reassoc ninf nsz <8 x float> %272, splat (float 1.500000e+00)
  %353 = fmul reassoc ninf nsz <8 x float> %273, splat (float 1.500000e+00)
  %354 = fmul reassoc ninf nsz <8 x float> %274, splat (float 1.500000e+00)
  %355 = fmul reassoc ninf nsz <8 x float> %275, splat (float 1.500000e+00)
  %356 = fcmp reassoc ninf nsz uge <8 x float> %176, %352
  %357 = fcmp reassoc ninf nsz uge <8 x float> %177, %353
  %358 = fcmp reassoc ninf nsz uge <8 x float> %178, %354
  %359 = fcmp reassoc ninf nsz uge <8 x float> %179, %355
  %360 = select <8 x i1> %348, <8 x i1> %356, <8 x i1> zeroinitializer
  %361 = select <8 x i1> %349, <8 x i1> %357, <8 x i1> zeroinitializer
  %362 = select <8 x i1> %350, <8 x i1> %358, <8 x i1> zeroinitializer
  %363 = select <8 x i1> %351, <8 x i1> %359, <8 x i1> zeroinitializer
  %364 = fsub reassoc ninf nsz <8 x float> %176, %352
  %365 = fsub reassoc ninf nsz <8 x float> %177, %353
  %366 = fsub reassoc ninf nsz <8 x float> %178, %354
  %367 = fsub reassoc ninf nsz <8 x float> %179, %355
  %368 = fdiv reassoc ninf nsz <8 x float> %364, %352
  %369 = fdiv reassoc ninf nsz <8 x float> %365, %353
  %370 = fdiv reassoc ninf nsz <8 x float> %366, %354
  %371 = fdiv reassoc ninf nsz <8 x float> %367, %355
  %372 = fcmp reassoc ninf nsz ogt <8 x float> %368, splat (float 1.000000e+00)
  %373 = fcmp reassoc ninf nsz ogt <8 x float> %369, splat (float 1.000000e+00)
  %374 = fcmp reassoc ninf nsz ogt <8 x float> %370, splat (float 1.000000e+00)
  %375 = fcmp reassoc ninf nsz ogt <8 x float> %371, splat (float 1.000000e+00)
  %376 = select <8 x i1> %372, <8 x float> splat (float 1.000000e+00), <8 x float> %368
  %377 = select <8 x i1> %373, <8 x float> splat (float 1.000000e+00), <8 x float> %369
  %378 = select <8 x i1> %374, <8 x float> splat (float 1.000000e+00), <8 x float> %370
  %379 = select <8 x i1> %375, <8 x float> splat (float 1.000000e+00), <8 x float> %371
  %380 = fmul reassoc ninf nsz <8 x float> %376, splat (float 0x3FC99999A0000000)
  %381 = fmul reassoc ninf nsz <8 x float> %377, splat (float 0x3FC99999A0000000)
  %382 = fmul reassoc ninf nsz <8 x float> %378, splat (float 0x3FC99999A0000000)
  %383 = fmul reassoc ninf nsz <8 x float> %379, splat (float 0x3FC99999A0000000)
  %384 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %380
  %385 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %381
  %386 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %382
  %387 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %383
  %388 = fmul reassoc ninf nsz <8 x float> %176, splat (float 0x3FEE666660000000)
  %389 = fmul reassoc ninf nsz <8 x float> %177, splat (float 0x3FEE666660000000)
  %390 = fmul reassoc ninf nsz <8 x float> %178, splat (float 0x3FEE666660000000)
  %391 = fmul reassoc ninf nsz <8 x float> %179, splat (float 0x3FEE666660000000)
  %392 = fdiv reassoc ninf nsz <8 x float> %388, %352
  %393 = fdiv reassoc ninf nsz <8 x float> %389, %353
  %394 = fdiv reassoc ninf nsz <8 x float> %390, %354
  %395 = fdiv reassoc ninf nsz <8 x float> %391, %355
  %396 = fadd reassoc ninf nsz <8 x float> %392, splat (float 0x3FA99999A0000000)
  %397 = fadd reassoc ninf nsz <8 x float> %393, splat (float 0x3FA99999A0000000)
  %398 = fadd reassoc ninf nsz <8 x float> %394, splat (float 0x3FA99999A0000000)
  %399 = fadd reassoc ninf nsz <8 x float> %395, splat (float 0x3FA99999A0000000)
  %400 = or <8 x i1> %348, %332
  %401 = or <8 x i1> %349, %333
  %402 = or <8 x i1> %350, %334
  %403 = or <8 x i1> %351, %335
  %404 = or <8 x i1> %400, %304
  %405 = or <8 x i1> %401, %305
  %406 = or <8 x i1> %402, %306
  %407 = or <8 x i1> %403, %307
  %408 = or <8 x i1> %404, %107
  %409 = or <8 x i1> %405, %107
  %410 = or <8 x i1> %406, %107
  %411 = or <8 x i1> %407, %107
  %predphi = select <8 x i1> %360, <8 x float> %384, <8 x float> %396
  %predphi216 = select <8 x i1> %332, <8 x float> %344, <8 x float> %predphi
  %predphi217 = select <8 x i1> %304, <8 x float> %328, <8 x float> %predphi216
  %predphi218 = select <8 x i1> %broadcast.splat, <8 x float> %predphi217, <8 x float> splat (float 1.000000e+00)
  %predphi219 = select <8 x i1> %361, <8 x float> %385, <8 x float> %397
  %predphi220 = select <8 x i1> %333, <8 x float> %345, <8 x float> %predphi219
  %predphi221 = select <8 x i1> %305, <8 x float> %329, <8 x float> %predphi220
  %predphi222 = select <8 x i1> %broadcast.splat, <8 x float> %predphi221, <8 x float> splat (float 1.000000e+00)
  %predphi223 = select <8 x i1> %362, <8 x float> %386, <8 x float> %398
  %predphi224 = select <8 x i1> %334, <8 x float> %346, <8 x float> %predphi223
  %predphi225 = select <8 x i1> %306, <8 x float> %330, <8 x float> %predphi224
  %predphi226 = select <8 x i1> %broadcast.splat, <8 x float> %predphi225, <8 x float> splat (float 1.000000e+00)
  %predphi227 = select <8 x i1> %363, <8 x float> %387, <8 x float> %399
  %predphi228 = select <8 x i1> %335, <8 x float> %347, <8 x float> %predphi227
  %predphi229 = select <8 x i1> %307, <8 x float> %331, <8 x float> %predphi228
  %predphi230 = select <8 x i1> %broadcast.splat, <8 x float> %predphi229, <8 x float> splat (float 1.000000e+00)
  %412 = fcmp reassoc ninf nsz ogt <8 x float> %252, splat (float 0x3EB0C6F7A0000000)
  %413 = fcmp reassoc ninf nsz ogt <8 x float> %253, splat (float 0x3EB0C6F7A0000000)
  %414 = fcmp reassoc ninf nsz ogt <8 x float> %254, splat (float 0x3EB0C6F7A0000000)
  %415 = fcmp reassoc ninf nsz ogt <8 x float> %255, splat (float 0x3EB0C6F7A0000000)
  %416 = select <8 x i1> %408, <8 x i1> %412, <8 x i1> zeroinitializer
  %417 = select <8 x i1> %409, <8 x i1> %413, <8 x i1> zeroinitializer
  %418 = select <8 x i1> %410, <8 x i1> %414, <8 x i1> zeroinitializer
  %419 = select <8 x i1> %411, <8 x i1> %415, <8 x i1> zeroinitializer
  %420 = fcmp reassoc ninf nsz ogt <8 x float> %236, splat (float 0x3EB0C6F7A0000000)
  %421 = fcmp reassoc ninf nsz ogt <8 x float> %237, splat (float 0x3EB0C6F7A0000000)
  %422 = fcmp reassoc ninf nsz ogt <8 x float> %238, splat (float 0x3EB0C6F7A0000000)
  %423 = fcmp reassoc ninf nsz ogt <8 x float> %239, splat (float 0x3EB0C6F7A0000000)
  %424 = fcmp reassoc ninf nsz ogt <8 x float> %248, splat (float 0x3EB0C6F7A0000000)
  %425 = fcmp reassoc ninf nsz ogt <8 x float> %249, splat (float 0x3EB0C6F7A0000000)
  %426 = fcmp reassoc ninf nsz ogt <8 x float> %250, splat (float 0x3EB0C6F7A0000000)
  %427 = fcmp reassoc ninf nsz ogt <8 x float> %251, splat (float 0x3EB0C6F7A0000000)
  %428 = select <8 x i1> %420, <8 x i1> %424, <8 x i1> zeroinitializer
  %429 = select <8 x i1> %421, <8 x i1> %425, <8 x i1> zeroinitializer
  %430 = select <8 x i1> %422, <8 x i1> %426, <8 x i1> zeroinitializer
  %431 = select <8 x i1> %423, <8 x i1> %427, <8 x i1> zeroinitializer
  %432 = select <8 x i1> %416, <8 x i1> %428, <8 x i1> zeroinitializer
  %433 = select <8 x i1> %417, <8 x i1> %429, <8 x i1> zeroinitializer
  %434 = select <8 x i1> %418, <8 x i1> %430, <8 x i1> zeroinitializer
  %435 = select <8 x i1> %419, <8 x i1> %431, <8 x i1> zeroinitializer
  %436 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather202, %wide.masked.gather190
  %437 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather203, %wide.masked.gather191
  %438 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather204, %wide.masked.gather192
  %439 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather205, %wide.masked.gather193
  %440 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather208, %wide.masked.gather196
  %441 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather209, %wide.masked.gather197
  %442 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather210, %wide.masked.gather198
  %443 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather211, %wide.masked.gather199
  %444 = fadd reassoc ninf nsz <8 x float> %440, %436
  %445 = fadd reassoc ninf nsz <8 x float> %441, %437
  %446 = fadd reassoc ninf nsz <8 x float> %442, %438
  %447 = fadd reassoc ninf nsz <8 x float> %443, %439
  %448 = fmul reassoc ninf nsz <8 x float> %248, %236
  %449 = fmul reassoc ninf nsz <8 x float> %249, %237
  %450 = fmul reassoc ninf nsz <8 x float> %250, %238
  %451 = fmul reassoc ninf nsz <8 x float> %251, %239
  %452 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %448)
  %453 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %449)
  %454 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %450)
  %455 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %451)
  %456 = fdiv reassoc ninf nsz <8 x float> %444, %452
  %457 = fdiv reassoc ninf nsz <8 x float> %445, %453
  %458 = fdiv reassoc ninf nsz <8 x float> %446, %454
  %459 = fdiv reassoc ninf nsz <8 x float> %447, %455
  %460 = fcmp reassoc ninf nsz ule <8 x float> %252, %280
  %461 = fcmp reassoc ninf nsz ule <8 x float> %253, %281
  %462 = fcmp reassoc ninf nsz ule <8 x float> %254, %282
  %463 = fcmp reassoc ninf nsz ule <8 x float> %255, %283
  %464 = fcmp reassoc ninf nsz uge <8 x float> %456, splat (float 0x3FC99999A0000000)
  %465 = fcmp reassoc ninf nsz uge <8 x float> %457, splat (float 0x3FC99999A0000000)
  %466 = fcmp reassoc ninf nsz uge <8 x float> %458, splat (float 0x3FC99999A0000000)
  %467 = fcmp reassoc ninf nsz uge <8 x float> %459, splat (float 0x3FC99999A0000000)
  %.not343 = select <8 x i1> %460, <8 x i1> splat (i1 true), <8 x i1> %464
  %.not346 = select <8 x i1> %461, <8 x i1> splat (i1 true), <8 x i1> %465
  %.not349 = select <8 x i1> %462, <8 x i1> splat (i1 true), <8 x i1> %466
  %.not352 = select <8 x i1> %463, <8 x i1> splat (i1 true), <8 x i1> %467
  %468 = select <8 x i1> %432, <8 x i1> %.not343, <8 x i1> zeroinitializer
  %469 = select <8 x i1> %433, <8 x i1> %.not346, <8 x i1> zeroinitializer
  %470 = select <8 x i1> %434, <8 x i1> %.not349, <8 x i1> zeroinitializer
  %471 = select <8 x i1> %435, <8 x i1> %.not352, <8 x i1> zeroinitializer
  %472 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %456, <8 x float> zeroinitializer)
  %473 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %457, <8 x float> zeroinitializer)
  %474 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %458, <8 x float> zeroinitializer)
  %475 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %459, <8 x float> zeroinitializer)
  %476 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %252)
  %477 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %253)
  %478 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %254)
  %479 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %255)
  %480 = fmul reassoc ninf nsz <8 x float> %476, splat (float 2.025000e+02)
  %481 = fmul reassoc ninf nsz <8 x float> %477, splat (float 2.025000e+02)
  %482 = fmul reassoc ninf nsz <8 x float> %478, splat (float 2.025000e+02)
  %483 = fmul reassoc ninf nsz <8 x float> %479, splat (float 2.025000e+02)
  %484 = fmul reassoc ninf nsz <8 x float> %480, %472
  %.fr = freeze <8 x float> %484
  %485 = fmul reassoc ninf nsz <8 x float> %481, %473
  %.fr353 = freeze <8 x float> %485
  %486 = fmul reassoc ninf nsz <8 x float> %482, %474
  %.fr354 = freeze <8 x float> %486
  %487 = fmul reassoc ninf nsz <8 x float> %483, %475
  %.fr355 = freeze <8 x float> %487
  %488 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %489 = fcmp reassoc nsz ogt <8 x float> %.fr353, splat (float 3.000000e+00)
  %490 = fcmp reassoc nsz ogt <8 x float> %.fr354, splat (float 3.000000e+00)
  %491 = fcmp reassoc nsz ogt <8 x float> %.fr355, splat (float 3.000000e+00)
  %492 = xor <8 x i1> %488, splat (i1 true)
  %493 = xor <8 x i1> %489, splat (i1 true)
  %494 = xor <8 x i1> %490, splat (i1 true)
  %495 = xor <8 x i1> %491, splat (i1 true)
  %496 = and <8 x i1> %468, %492
  %497 = and <8 x i1> %469, %493
  %498 = and <8 x i1> %470, %494
  %499 = and <8 x i1> %471, %495
  %500 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %501 = fcmp reassoc nsz olt <8 x float> %.fr353, splat (float -3.000000e+00)
  %502 = fcmp reassoc nsz olt <8 x float> %.fr354, splat (float -3.000000e+00)
  %503 = fcmp reassoc nsz olt <8 x float> %.fr355, splat (float -3.000000e+00)
  %504 = xor <8 x i1> %500, splat (i1 true)
  %505 = xor <8 x i1> %501, splat (i1 true)
  %506 = xor <8 x i1> %502, splat (i1 true)
  %507 = xor <8 x i1> %503, splat (i1 true)
  %508 = and <8 x i1> %496, %504
  %509 = and <8 x i1> %497, %505
  %510 = and <8 x i1> %498, %506
  %511 = and <8 x i1> %499, %507
  %512 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %513 = fmul reassoc ninf nsz <8 x float> %.fr353, %.fr353
  %514 = fmul reassoc ninf nsz <8 x float> %.fr354, %.fr354
  %515 = fmul reassoc ninf nsz <8 x float> %.fr355, %.fr355
  %516 = fadd reassoc ninf nsz <8 x float> %512, splat (float 2.700000e+01)
  %517 = fadd reassoc ninf nsz <8 x float> %513, splat (float 2.700000e+01)
  %518 = fadd reassoc ninf nsz <8 x float> %514, splat (float 2.700000e+01)
  %519 = fadd reassoc ninf nsz <8 x float> %515, splat (float 2.700000e+01)
  %520 = fmul reassoc ninf nsz <8 x float> %516, %.fr
  %521 = fmul reassoc ninf nsz <8 x float> %517, %.fr353
  %522 = fmul reassoc ninf nsz <8 x float> %518, %.fr354
  %523 = fmul reassoc ninf nsz <8 x float> %519, %.fr355
  %524 = fmul reassoc ninf nsz <8 x float> %512, splat (float 9.000000e+00)
  %525 = fmul reassoc ninf nsz <8 x float> %513, splat (float 9.000000e+00)
  %526 = fmul reassoc ninf nsz <8 x float> %514, splat (float 9.000000e+00)
  %527 = fmul reassoc ninf nsz <8 x float> %515, splat (float 9.000000e+00)
  %528 = fadd reassoc ninf nsz <8 x float> %524, splat (float 2.700000e+01)
  %529 = fadd reassoc ninf nsz <8 x float> %525, splat (float 2.700000e+01)
  %530 = fadd reassoc ninf nsz <8 x float> %526, splat (float 2.700000e+01)
  %531 = fadd reassoc ninf nsz <8 x float> %527, splat (float 2.700000e+01)
  %532 = fdiv reassoc ninf nsz <8 x float> %520, %528
  %533 = fdiv reassoc ninf nsz <8 x float> %521, %529
  %534 = fdiv reassoc ninf nsz <8 x float> %522, %530
  %535 = fdiv reassoc ninf nsz <8 x float> %523, %531
  %536 = fadd reassoc ninf nsz <8 x float> %532, splat (float 1.000000e+00)
  %537 = fadd reassoc ninf nsz <8 x float> %533, splat (float 1.000000e+00)
  %538 = fadd reassoc ninf nsz <8 x float> %534, splat (float 1.000000e+00)
  %539 = fadd reassoc ninf nsz <8 x float> %535, splat (float 1.000000e+00)
  %540 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %456
  %541 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %457
  %542 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %458
  %543 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %459
  %544 = fmul reassoc ninf nsz <8 x float> %540, %176
  %545 = fmul reassoc ninf nsz <8 x float> %541, %177
  %546 = fmul reassoc ninf nsz <8 x float> %542, %178
  %547 = fmul reassoc ninf nsz <8 x float> %543, %179
  %548 = and <8 x i1> %496, %500
  %549 = and <8 x i1> %497, %501
  %550 = and <8 x i1> %498, %502
  %551 = and <8 x i1> %499, %503
  %552 = and <8 x i1> %468, %488
  %553 = and <8 x i1> %469, %489
  %554 = and <8 x i1> %470, %490
  %555 = and <8 x i1> %471, %491
  %556 = xor <8 x i1> %428, splat (i1 true)
  %557 = xor <8 x i1> %429, splat (i1 true)
  %558 = xor <8 x i1> %430, splat (i1 true)
  %559 = xor <8 x i1> %431, splat (i1 true)
  %560 = select <8 x i1> %416, <8 x i1> %556, <8 x i1> zeroinitializer
  %561 = select <8 x i1> %417, <8 x i1> %557, <8 x i1> zeroinitializer
  %562 = select <8 x i1> %418, <8 x i1> %558, <8 x i1> zeroinitializer
  %563 = select <8 x i1> %419, <8 x i1> %559, <8 x i1> zeroinitializer
  %564 = xor <8 x i1> %412, splat (i1 true)
  %565 = xor <8 x i1> %413, splat (i1 true)
  %566 = xor <8 x i1> %414, splat (i1 true)
  %567 = xor <8 x i1> %415, splat (i1 true)
  %568 = select <8 x i1> %408, <8 x i1> %564, <8 x i1> zeroinitializer
  %569 = select <8 x i1> %409, <8 x i1> %565, <8 x i1> zeroinitializer
  %570 = select <8 x i1> %410, <8 x i1> %566, <8 x i1> zeroinitializer
  %571 = select <8 x i1> %411, <8 x i1> %567, <8 x i1> zeroinitializer
  %572 = select <8 x i1> %468, <8 x i1> splat (i1 true), <8 x i1> %568
  %573 = select <8 x i1> %572, <8 x i1> splat (i1 true), <8 x i1> %560
  %predphi235 = select <8 x i1> %573, <8 x float> %176, <8 x float> %544
  %574 = select <8 x i1> %469, <8 x i1> splat (i1 true), <8 x i1> %569
  %575 = select <8 x i1> %574, <8 x i1> splat (i1 true), <8 x i1> %561
  %predphi240 = select <8 x i1> %575, <8 x float> %177, <8 x float> %545
  %576 = select <8 x i1> %470, <8 x i1> splat (i1 true), <8 x i1> %570
  %577 = select <8 x i1> %576, <8 x i1> splat (i1 true), <8 x i1> %562
  %predphi245 = select <8 x i1> %577, <8 x float> %178, <8 x float> %546
  %578 = select <8 x i1> %471, <8 x i1> splat (i1 true), <8 x i1> %571
  %579 = select <8 x i1> %578, <8 x i1> splat (i1 true), <8 x i1> %563
  %predphi250 = select <8 x i1> %579, <8 x float> %179, <8 x float> %547
  %predphi253 = select <8 x i1> %552, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi254 = select <8 x i1> %508, <8 x float> %536, <8 x float> %predphi253
  %predphi255 = select <8 x i1> %548, <8 x float> zeroinitializer, <8 x float> %predphi254
  %predphi258 = select <8 x i1> %553, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi259 = select <8 x i1> %509, <8 x float> %537, <8 x float> %predphi258
  %predphi260 = select <8 x i1> %549, <8 x float> zeroinitializer, <8 x float> %predphi259
  %predphi263 = select <8 x i1> %554, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi264 = select <8 x i1> %510, <8 x float> %538, <8 x float> %predphi263
  %predphi265 = select <8 x i1> %550, <8 x float> zeroinitializer, <8 x float> %predphi264
  %predphi268 = select <8 x i1> %555, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi269 = select <8 x i1> %511, <8 x float> %539, <8 x float> %predphi268
  %predphi270 = select <8 x i1> %551, <8 x float> zeroinitializer, <8 x float> %predphi269
  %580 = fmul reassoc ninf nsz <8 x float> %predphi255, %predphi218
  %581 = fmul reassoc ninf nsz <8 x float> %predphi260, %predphi222
  %582 = fmul reassoc ninf nsz <8 x float> %predphi265, %predphi226
  %583 = fmul reassoc ninf nsz <8 x float> %predphi270, %predphi230
  %584 = fmul reassoc ninf nsz <8 x float> %580, %predphi235
  %585 = fmul reassoc ninf nsz <8 x float> %581, %predphi240
  %586 = fmul reassoc ninf nsz <8 x float> %582, %predphi245
  %587 = fmul reassoc ninf nsz <8 x float> %583, %predphi250
  %588 = fadd reassoc ninf nsz <8 x float> %584, %vec.phi171
  %589 = fadd reassoc ninf nsz <8 x float> %585, %vec.phi172
  %590 = fadd reassoc ninf nsz <8 x float> %586, %vec.phi173
  %591 = fadd reassoc ninf nsz <8 x float> %587, %vec.phi174
  %592 = fadd reassoc ninf nsz <8 x float> %580, %vec.phi167
  %593 = fadd reassoc ninf nsz <8 x float> %581, %vec.phi168
  %594 = fadd reassoc ninf nsz <8 x float> %582, %vec.phi169
  %595 = fadd reassoc ninf nsz <8 x float> %583, %vec.phi170
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %596 = icmp eq i64 %lsr.iv.next, 0
  br i1 %596, label %middle.block156, label %vector.body165, !llvm.loop !11

middle.block156:                                  ; preds = %vector.body165
  %bin.rdx272 = fadd reassoc ninf nsz <8 x float> %593, %592
  %bin.rdx273 = fadd reassoc ninf nsz <8 x float> %594, %bin.rdx272
  %bin.rdx274 = fadd reassoc ninf nsz <8 x float> %595, %bin.rdx273
  %597 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx274)
  %bin.rdx275 = fadd reassoc ninf nsz <8 x float> %589, %588
  %bin.rdx276 = fadd reassoc ninf nsz <8 x float> %590, %bin.rdx275
  %bin.rdx277 = fadd reassoc ninf nsz <8 x float> %591, %bin.rdx276
  %598 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx277)
  br i1 %cmp.n278, label %for_loop_test11.after_for10_crit_edge.us, label %vec.epilog.iter.check285

vec.epilog.iter.check285:                         ; preds = %middle.block156
  br i1 %min.epilog.iters.check287, label %for_loop_body8.us.preheader, label %vec.epilog.ph284

vec.epilog.ph284:                                 ; preds = %vec.epilog.iter.check285, %vector.main.loop.iter.check161
  %bc.resume.val279 = phi i64 [ %n.vec164, %vec.epilog.iter.check285 ], [ 0, %vector.main.loop.iter.check161 ]
  %bc.merge.rdx280 = phi float [ %597, %vec.epilog.iter.check285 ], [ %.05076.us, %vector.main.loop.iter.check161 ]
  %bc.merge.rdx281 = phi float [ %598, %vec.epilog.iter.check285 ], [ %.05275.us, %vector.main.loop.iter.check161 ]
  %599 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx280, i64 0
  %600 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx281, i64 0
  %601 = trunc nuw nsw i64 %bc.resume.val279 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %601, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert300 = insertelement <8 x i32> poison, i32 %114, i64 0
  %broadcast.splat301 = shufflevector <8 x i32> %broadcast.splatinsert300, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert303 = insertelement <8 x i32> poison, i32 %115, i64 0
  %broadcast.splat304 = shufflevector <8 x i32> %broadcast.splatinsert303, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert306 = insertelement <8 x i32> poison, i32 %116, i64 0
  %broadcast.splat307 = shufflevector <8 x i32> %broadcast.splatinsert306, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert309 = insertelement <8 x i32> poison, i32 %117, i64 0
  %broadcast.splat310 = shufflevector <8 x i32> %broadcast.splatinsert309, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert312 = insertelement <8 x i32> poison, i32 %118, i64 0
  %broadcast.splat313 = shufflevector <8 x i32> %broadcast.splatinsert312, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert315 = insertelement <8 x i32> poison, i32 %119, i64 0
  %broadcast.splat316 = shufflevector <8 x i32> %broadcast.splatinsert315, <8 x i32> poison, <8 x i32> zeroinitializer
  %602 = add i64 %110, %bc.resume.val279
  br label %vec.epilog.vector.body292

vec.epilog.vector.body292:                        ; preds = %vec.epilog.vector.body292, %vec.epilog.ph284
  %lsr.iv423 = phi i64 [ %lsr.iv.next424, %vec.epilog.vector.body292 ], [ %602, %vec.epilog.ph284 ]
  %vec.phi294 = phi <8 x float> [ %599, %vec.epilog.ph284 ], [ %716, %vec.epilog.vector.body292 ]
  %vec.phi295 = phi <8 x float> [ %600, %vec.epilog.ph284 ], [ %715, %vec.epilog.vector.body292 ]
  %vec.ind296 = phi <8 x i32> [ %induction, %vec.epilog.ph284 ], [ %vec.ind.next297, %vec.epilog.vector.body292 ]
  %603 = shl <8 x i32> %vec.ind296, splat (i32 1)
  %604 = add <8 x i32> %broadcast.splat176, %603
  %605 = add <8 x i32> %broadcast.splat301, %604
  %606 = sext <8 x i32> %605 to <8 x i64>
  %607 = getelementptr float, ptr %74, <8 x i64> %606
  %wide.masked.gather302 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %607, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %608 = add <8 x i32> %broadcast.splat304, %604
  %609 = sext <8 x i32> %608 to <8 x i64>
  %610 = getelementptr float, ptr %76, <8 x i64> %609
  %wide.masked.gather305 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %610, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %611 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather302, %wide.masked.gather305
  %612 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %611)
  %613 = add <8 x i32> %broadcast.splat307, %604
  %614 = sext <8 x i32> %613 to <8 x i64>
  %615 = getelementptr float, ptr %78, <8 x i64> %614
  %wide.masked.gather308 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %615, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %616 = add <8 x i32> %broadcast.splat310, %604
  %617 = sext <8 x i32> %616 to <8 x i64>
  %618 = getelementptr float, ptr %80, <8 x i64> %617
  %wide.masked.gather311 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %618, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %619 = add <8 x i32> %broadcast.splat313, %604
  %620 = sext <8 x i32> %619 to <8 x i64>
  %621 = getelementptr float, ptr %82, <8 x i64> %620
  %wide.masked.gather314 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %621, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %622 = add <8 x i32> %broadcast.splat316, %604
  %623 = sext <8 x i32> %622 to <8 x i64>
  %624 = getelementptr float, ptr %84, <8 x i64> %623
  %wide.masked.gather317 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %624, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %625 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather308, %wide.masked.gather308
  %626 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather311, %wide.masked.gather311
  %627 = fadd reassoc ninf nsz <8 x float> %626, %625
  %628 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather314, %wide.masked.gather314
  %629 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather317, %wide.masked.gather317
  %630 = fadd reassoc ninf nsz <8 x float> %629, %628
  %631 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %627, <8 x float> %630)
  %632 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather305, splat (float -2.000000e+00)
  %633 = fadd reassoc ninf nsz <8 x float> %632, splat (float 3.000000e+00)
  %634 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %633, <8 x float> splat (float 3.000000e+00))
  %635 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %634, <8 x float> splat (float 1.000000e+00))
  %636 = fmul reassoc ninf nsz <8 x float> %635, %broadcast.splat213
  %637 = fmul reassoc ninf nsz <8 x float> %635, %635
  %638 = fmul reassoc ninf nsz <8 x float> %637, %broadcast.splat215
  %639 = fcmp reassoc ninf nsz olt <8 x float> %631, %638
  %640 = xor <8 x i1> %639, splat (i1 true)
  %641 = select <8 x i1> %broadcast.splat, <8 x i1> %640, <8 x i1> zeroinitializer
  %642 = fcmp reassoc ninf nsz olt <8 x float> %612, %636
  %643 = xor <8 x i1> %642, splat (i1 true)
  %644 = select <8 x i1> %641, <8 x i1> %643, <8 x i1> zeroinitializer
  %645 = fmul reassoc ninf nsz <8 x float> %636, splat (float 4.000000e+00)
  %646 = fdiv reassoc ninf nsz <8 x float> %612, %645
  %647 = fcmp reassoc ninf nsz ogt <8 x float> %646, splat (float 1.000000e+00)
  %648 = select <8 x i1> %647, <8 x float> splat (float 1.000000e+00), <8 x float> %646
  %649 = fmul reassoc ninf nsz <8 x float> %648, splat (float 0x3FD99999A0000000)
  %650 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %649
  %651 = select <8 x i1> %641, <8 x i1> %642, <8 x i1> zeroinitializer
  %652 = fmul reassoc ninf nsz <8 x float> %612, splat (float 0x3FC3333340000000)
  %653 = fdiv reassoc ninf nsz <8 x float> %652, %636
  %654 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %653
  %655 = select <8 x i1> %broadcast.splat, <8 x i1> %639, <8 x i1> zeroinitializer
  %656 = fmul reassoc ninf nsz <8 x float> %636, splat (float 1.500000e+00)
  %657 = fcmp reassoc ninf nsz uge <8 x float> %612, %656
  %658 = select <8 x i1> %655, <8 x i1> %657, <8 x i1> zeroinitializer
  %659 = fsub reassoc ninf nsz <8 x float> %612, %656
  %660 = fdiv reassoc ninf nsz <8 x float> %659, %656
  %661 = fcmp reassoc ninf nsz ogt <8 x float> %660, splat (float 1.000000e+00)
  %662 = select <8 x i1> %661, <8 x float> splat (float 1.000000e+00), <8 x float> %660
  %663 = fmul reassoc ninf nsz <8 x float> %662, splat (float 0x3FC99999A0000000)
  %664 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %663
  %665 = fmul reassoc ninf nsz <8 x float> %612, splat (float 0x3FEE666660000000)
  %666 = fdiv reassoc ninf nsz <8 x float> %665, %656
  %667 = fadd reassoc ninf nsz <8 x float> %666, splat (float 0x3FA99999A0000000)
  %668 = or <8 x i1> %651, %107
  %669 = or <8 x i1> %668, %655
  %670 = or <8 x i1> %669, %644
  %predphi322 = select <8 x i1> %658, <8 x float> %664, <8 x float> %667
  %predphi323 = select <8 x i1> %651, <8 x float> %654, <8 x float> %predphi322
  %predphi324 = select <8 x i1> %644, <8 x float> %650, <8 x float> %predphi323
  %predphi325 = select <8 x i1> %broadcast.splat, <8 x float> %predphi324, <8 x float> splat (float 1.000000e+00)
  %671 = fcmp reassoc ninf nsz ogt <8 x float> %631, splat (float 0x3EB0C6F7A0000000)
  %672 = select <8 x i1> %670, <8 x i1> %671, <8 x i1> zeroinitializer
  %673 = fcmp reassoc ninf nsz ogt <8 x float> %627, splat (float 0x3EB0C6F7A0000000)
  %674 = fcmp reassoc ninf nsz ogt <8 x float> %630, splat (float 0x3EB0C6F7A0000000)
  %675 = select <8 x i1> %673, <8 x i1> %674, <8 x i1> zeroinitializer
  %676 = select <8 x i1> %672, <8 x i1> %675, <8 x i1> zeroinitializer
  %677 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather314, %wide.masked.gather308
  %678 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather317, %wide.masked.gather311
  %679 = fadd reassoc ninf nsz <8 x float> %678, %677
  %680 = fmul reassoc ninf nsz <8 x float> %630, %627
  %681 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %680)
  %682 = fdiv reassoc ninf nsz <8 x float> %679, %681
  %683 = fcmp reassoc ninf nsz ule <8 x float> %631, %638
  %684 = fcmp reassoc ninf nsz uge <8 x float> %682, splat (float 0x3FC99999A0000000)
  %.not358 = select <8 x i1> %683, <8 x i1> splat (i1 true), <8 x i1> %684
  %685 = select <8 x i1> %676, <8 x i1> %.not358, <8 x i1> zeroinitializer
  %686 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %682, <8 x float> zeroinitializer)
  %687 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %631)
  %688 = fmul reassoc ninf nsz <8 x float> %687, splat (float 2.025000e+02)
  %689 = fmul reassoc ninf nsz <8 x float> %688, %686
  %.fr359 = freeze <8 x float> %689
  %690 = fcmp reassoc nsz ogt <8 x float> %.fr359, splat (float 3.000000e+00)
  %691 = xor <8 x i1> %690, splat (i1 true)
  %692 = and <8 x i1> %685, %691
  %693 = fcmp reassoc nsz olt <8 x float> %.fr359, splat (float -3.000000e+00)
  %694 = xor <8 x i1> %693, splat (i1 true)
  %695 = and <8 x i1> %692, %694
  %696 = fmul reassoc ninf nsz <8 x float> %.fr359, %.fr359
  %697 = fadd reassoc ninf nsz <8 x float> %696, splat (float 2.700000e+01)
  %698 = fmul reassoc ninf nsz <8 x float> %697, %.fr359
  %699 = fmul reassoc ninf nsz <8 x float> %696, splat (float 9.000000e+00)
  %700 = fadd reassoc ninf nsz <8 x float> %699, splat (float 2.700000e+01)
  %701 = fdiv reassoc ninf nsz <8 x float> %698, %700
  %702 = fadd reassoc ninf nsz <8 x float> %701, splat (float 1.000000e+00)
  %703 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %682
  %704 = fmul reassoc ninf nsz <8 x float> %703, %612
  %705 = and <8 x i1> %692, %693
  %706 = and <8 x i1> %685, %690
  %707 = xor <8 x i1> %675, splat (i1 true)
  %708 = select <8 x i1> %672, <8 x i1> %707, <8 x i1> zeroinitializer
  %709 = xor <8 x i1> %671, splat (i1 true)
  %710 = select <8 x i1> %670, <8 x i1> %709, <8 x i1> zeroinitializer
  %711 = select <8 x i1> %685, <8 x i1> splat (i1 true), <8 x i1> %710
  %712 = select <8 x i1> %711, <8 x i1> splat (i1 true), <8 x i1> %708
  %predphi330 = select <8 x i1> %712, <8 x float> %612, <8 x float> %704
  %predphi333 = select <8 x i1> %706, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi334 = select <8 x i1> %695, <8 x float> %702, <8 x float> %predphi333
  %predphi335 = select <8 x i1> %705, <8 x float> zeroinitializer, <8 x float> %predphi334
  %713 = fmul reassoc ninf nsz <8 x float> %predphi335, %predphi325
  %714 = fmul reassoc ninf nsz <8 x float> %713, %predphi330
  %715 = fadd reassoc ninf nsz <8 x float> %714, %vec.phi295
  %716 = fadd reassoc ninf nsz <8 x float> %713, %vec.phi294
  %vec.ind.next297 = add <8 x i32> %vec.ind296, splat (i32 8)
  %lsr.iv.next424 = add i64 %lsr.iv423, 8
  %717 = icmp eq i64 %lsr.iv.next424, 0
  br i1 %717, label %vec.epilog.middle.block282, label %vec.epilog.vector.body292, !llvm.loop !14

vec.epilog.middle.block282:                       ; preds = %vec.epilog.vector.body292
  %718 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %716)
  %719 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %715)
  br i1 %cmp.n337, label %for_loop_test11.after_for10_crit_edge.us, label %for_loop_body8.us.preheader

for_loop_body8.us.preheader:                      ; preds = %vec.epilog.middle.block282, %vec.epilog.iter.check285, %vector.scevcheck140, %iter.check159
  %indvars.iv.ph = phi i64 [ %n.vec164, %vec.epilog.iter.check285 ], [ 0, %iter.check159 ], [ 0, %vector.scevcheck140 ], [ %n.vec289, %vec.epilog.middle.block282 ]
  %.15172.us.ph = phi float [ %597, %vec.epilog.iter.check285 ], [ %.05076.us, %iter.check159 ], [ %.05076.us, %vector.scevcheck140 ], [ %718, %vec.epilog.middle.block282 ]
  %.15371.us.ph = phi float [ %598, %vec.epilog.iter.check285 ], [ %.05275.us, %iter.check159 ], [ %.05275.us, %vector.scevcheck140 ], [ %719, %vec.epilog.middle.block282 ]
  %720 = trunc i64 %indvars.iv.ph to i32
  %721 = shl nuw i32 %720, 1
  %722 = add i64 %111, %indvars.iv.ph
  br label %for_loop_body8.us

for_loop_body8.us:                                ; preds = %after_if38.us, %for_loop_body8.us.preheader
  %lsr.iv449 = phi i64 [ %722, %for_loop_body8.us.preheader ], [ %lsr.iv.next450, %after_if38.us ]
  %lsr.iv447 = phi i32 [ %lsr.iv445, %for_loop_body8.us.preheader ], [ %lsr.iv.next448, %after_if38.us ]
  %lsr.iv443 = phi i32 [ %lsr.iv441, %for_loop_body8.us.preheader ], [ %lsr.iv.next444, %after_if38.us ]
  %lsr.iv439 = phi i32 [ %lsr.iv437, %for_loop_body8.us.preheader ], [ %lsr.iv.next440, %after_if38.us ]
  %lsr.iv435 = phi i32 [ %lsr.iv433, %for_loop_body8.us.preheader ], [ %lsr.iv.next436, %after_if38.us ]
  %lsr.iv431 = phi i32 [ %lsr.iv429, %for_loop_body8.us.preheader ], [ %lsr.iv.next432, %after_if38.us ]
  %lsr.iv427 = phi i32 [ %lsr.iv425, %for_loop_body8.us.preheader ], [ %lsr.iv.next428, %after_if38.us ]
  %.15172.us = phi float [ %811, %after_if38.us ], [ %.15172.us.ph, %for_loop_body8.us.preheader ]
  %.15371.us = phi float [ %810, %after_if38.us ], [ %.15371.us.ph, %for_loop_body8.us.preheader ]
  %723 = add i32 %721, %lsr.iv447
  %724 = sext i32 %723 to i64
  %725 = getelementptr float, ptr %74, i64 %724
  %726 = load float, ptr %725, align 4
  %727 = add i32 %721, %lsr.iv443
  %728 = sext i32 %727 to i64
  %729 = getelementptr float, ptr %76, i64 %728
  %730 = load float, ptr %729, align 4
  %731 = fsub reassoc ninf nsz float %726, %730
  %732 = tail call noundef float @llvm.fabs.f32(float %731)
  %733 = add i32 %721, %lsr.iv439
  %734 = sext i32 %733 to i64
  %735 = getelementptr float, ptr %78, i64 %734
  %736 = load float, ptr %735, align 4
  %737 = add i32 %721, %lsr.iv435
  %738 = sext i32 %737 to i64
  %739 = getelementptr float, ptr %80, i64 %738
  %740 = load float, ptr %739, align 4
  %741 = add i32 %721, %lsr.iv431
  %742 = sext i32 %741 to i64
  %743 = getelementptr float, ptr %82, i64 %742
  %744 = load float, ptr %743, align 4
  %745 = add i32 %721, %lsr.iv427
  %746 = sext i32 %745 to i64
  %747 = getelementptr float, ptr %84, i64 %746
  %748 = load float, ptr %747, align 4
  %749 = fmul reassoc ninf nsz float %736, %736
  %750 = fmul reassoc ninf nsz float %740, %740
  %751 = fadd reassoc ninf nsz float %750, %749
  %752 = fmul reassoc ninf nsz float %744, %744
  %753 = fmul reassoc ninf nsz float %748, %748
  %754 = fadd reassoc ninf nsz float %753, %752
  %755 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %751, float %754)
  %factor.us = fmul reassoc ninf nsz float %730, -2.000000e+00
  %756 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %757 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %756, float 3.000000e+00)
  %758 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %757, float 1.000000e+00)
  %759 = fmul reassoc ninf nsz float %758, %50
  %760 = fmul reassoc ninf nsz float %758, %758
  %761 = fmul reassoc ninf nsz float %760, %53
  br i1 %54, label %true_block12.us, label %after_if14.us

true_block12.us:                                  ; preds = %for_loop_body8.us
  %762 = fcmp reassoc ninf nsz olt float %755, %761
  br i1 %762, label %true_block15.us, label %false_block16.us

false_block16.us:                                 ; preds = %true_block12.us
  %763 = fcmp reassoc ninf nsz olt float %732, %759
  br i1 %763, label %true_block24.us, label %false_block25.us

false_block25.us:                                 ; preds = %false_block16.us
  %764 = fmul reassoc ninf nsz float %759, 4.000000e+00
  %765 = fdiv reassoc ninf nsz float %732, %764
  %766 = fcmp reassoc ninf nsz ogt float %765, 1.000000e+00
  %spec.store.select1.us = select i1 %766, float 1.000000e+00, float %765
  %767 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %768 = fsub reassoc ninf nsz float 0x3FE6666680000000, %767
  br label %after_if14.us

true_block24.us:                                  ; preds = %false_block16.us
  %769 = fmul reassoc ninf nsz float %732, 0x3FC3333340000000
  %770 = fdiv reassoc ninf nsz float %769, %759
  %771 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %770
  br label %after_if14.us

true_block15.us:                                  ; preds = %true_block12.us
  %772 = fmul reassoc ninf nsz float %759, 1.500000e+00
  %773 = fcmp reassoc ninf nsz olt float %732, %772
  br i1 %773, label %true_block18.us, label %false_block19.us

false_block19.us:                                 ; preds = %true_block15.us
  %774 = fsub reassoc ninf nsz float %732, %772
  %775 = fdiv reassoc ninf nsz float %774, %772
  %776 = fcmp reassoc ninf nsz ogt float %775, 1.000000e+00
  %spec.store.select.us = select i1 %776, float 1.000000e+00, float %775
  %777 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %778 = fsub reassoc ninf nsz float 1.000000e+00, %777
  br label %after_if14.us

true_block18.us:                                  ; preds = %true_block15.us
  %779 = fmul reassoc ninf nsz float %732, 0x3FEE666660000000
  %780 = fdiv reassoc ninf nsz float %779, %772
  %781 = fadd reassoc ninf nsz float %780, 0x3FA99999A0000000
  br label %after_if14.us

after_if14.us:                                    ; preds = %true_block18.us, %false_block19.us, %true_block24.us, %false_block25.us, %for_loop_body8.us
  %.046.us = phi float [ %781, %true_block18.us ], [ %778, %false_block19.us ], [ %771, %true_block24.us ], [ %768, %false_block25.us ], [ 1.000000e+00, %for_loop_body8.us ]
  %782 = fcmp reassoc ninf nsz ogt float %755, 0x3EB0C6F7A0000000
  br i1 %782, label %true_block30.us, label %after_if38.us

true_block30.us:                                  ; preds = %after_if14.us
  %783 = fcmp reassoc ninf nsz ogt float %751, 0x3EB0C6F7A0000000
  %784 = fcmp reassoc ninf nsz ogt float %754, 0x3EB0C6F7A0000000
  %.041.us = select i1 %783, i1 %784, i1 false
  br i1 %.041.us, label %true_block36.us, label %after_if38.us

true_block36.us:                                  ; preds = %true_block30.us
  %785 = fmul reassoc ninf nsz float %744, %736
  %786 = fmul reassoc ninf nsz float %748, %740
  %787 = fadd reassoc ninf nsz float %786, %785
  %788 = fmul reassoc ninf nsz float %754, %751
  %789 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %788)
  %790 = fdiv reassoc ninf nsz float %787, %789
  %791 = fcmp reassoc ninf nsz ogt float %755, %761
  %792 = fcmp reassoc ninf nsz olt float %790, 0x3FC99999A0000000
  %.040.us = select i1 %791, i1 %792, i1 false
  br i1 %.040.us, label %true_block42.us, label %false_block43.us

false_block43.us:                                 ; preds = %true_block36.us
  %793 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %790, float 0.000000e+00)
  %794 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %755)
  %795 = fmul reassoc ninf nsz float %794, 2.025000e+02
  %796 = fmul reassoc ninf nsz float %795, %793
  %797 = fcmp reassoc ninf nsz ogt float %796, 3.000000e+00
  br i1 %797, label %after_if38.us, label %false_block46.us

false_block46.us:                                 ; preds = %false_block43.us
  %798 = fcmp reassoc ninf nsz olt float %796, -3.000000e+00
  br i1 %798, label %after_if38.us, label %false_block49.us

false_block49.us:                                 ; preds = %false_block46.us
  %799 = fmul reassoc ninf nsz float %796, %796
  %800 = fadd reassoc ninf nsz float %799, 2.700000e+01
  %801 = fmul reassoc ninf nsz float %800, %796
  %802 = fmul reassoc ninf nsz float %799, 9.000000e+00
  %803 = fadd reassoc ninf nsz float %802, 2.700000e+01
  %804 = fdiv reassoc ninf nsz float %801, %803
  %805 = fadd reassoc ninf nsz float %804, 1.000000e+00
  br label %after_if38.us

true_block42.us:                                  ; preds = %true_block36.us
  %806 = fsub reassoc ninf nsz float 1.500000e+00, %790
  %807 = fmul reassoc ninf nsz float %806, %732
  br label %after_if38.us

after_if38.us:                                    ; preds = %true_block42.us, %false_block49.us, %false_block46.us, %false_block43.us, %true_block30.us, %after_if14.us
  %.047.us = phi float [ %807, %true_block42.us ], [ %732, %true_block30.us ], [ %732, %after_if14.us ], [ %732, %false_block43.us ], [ %732, %false_block49.us ], [ %732, %false_block46.us ]
  %.043.us = phi float [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %true_block30.us ], [ 1.000000e+00, %after_if14.us ], [ 2.000000e+00, %false_block43.us ], [ %805, %false_block49.us ], [ 0.000000e+00, %false_block46.us ]
  %808 = fmul reassoc ninf nsz float %.043.us, %.046.us
  %809 = fmul reassoc ninf nsz float %808, %.047.us
  %810 = fadd reassoc ninf nsz float %809, %.15371.us
  %811 = fadd reassoc ninf nsz float %808, %.15172.us
  %lsr.iv.next428 = add i32 %lsr.iv427, 2
  %lsr.iv.next432 = add i32 %lsr.iv431, 2
  %lsr.iv.next436 = add i32 %lsr.iv435, 2
  %lsr.iv.next440 = add i32 %lsr.iv439, 2
  %lsr.iv.next444 = add i32 %lsr.iv443, 2
  %lsr.iv.next448 = add i32 %lsr.iv447, 2
  %lsr.iv.next450 = add i64 %lsr.iv449, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next450, 0
  br i1 %exitcond.not, label %for_loop_test11.after_for10_crit_edge.us.loopexit, label %for_loop_body8.us, !llvm.loop !15

for_loop_test11.after_for10_crit_edge.us.loopexit: ; preds = %after_if38.us
  br label %for_loop_test11.after_for10_crit_edge.us

for_loop_test11.after_for10_crit_edge.us:         ; preds = %for_loop_test11.after_for10_crit_edge.us.loopexit, %vec.epilog.middle.block282, %middle.block156
  %.lcssa116 = phi float [ %598, %middle.block156 ], [ %719, %vec.epilog.middle.block282 ], [ %810, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %597, %middle.block156 ], [ %718, %vec.epilog.middle.block282 ], [ %811, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %812 = add nuw nsw i32 %.04977.us, 1
  %lsr.iv.next426 = add i32 %lsr.iv425, %104
  %lsr.iv.next430 = add i32 %lsr.iv429, %101
  %lsr.iv.next434 = add i32 %lsr.iv433, %98
  %lsr.iv.next438 = add i32 %lsr.iv437, %95
  %lsr.iv.next442 = add i32 %lsr.iv441, %92
  %lsr.iv.next446 = add i32 %lsr.iv445, %89
  %exitcond97.not = icmp eq i32 %812, %56
  br i1 %exitcond97.not, label %after_for6, label %iter.check159

after_if3.sink.split:                             ; preds = %true_block62, %for_loop_body
  %.0.sink.ph = phi float [ %971, %true_block62 ], [ 0.000000e+00, %for_loop_body ]
  %.pre = load ptr, ptr %0, align 8
  br label %after_if3

after_if3:                                        ; preds = %after_if53, %after_if3.sink.split
  %.sink115 = phi ptr [ %59, %after_if53 ], [ %.pre, %after_if3.sink.split ]
  %.0.sink = phi float [ 0.000000e+00, %after_if53 ], [ %.0.sink.ph, %after_if3.sink.split ]
  %813 = getelementptr i8, ptr %.sink115, i64 104
  %814 = load ptr, ptr %813, align 8
  %815 = getelementptr i8, ptr %.sink115, i64 100
  %816 = load i32, ptr %815, align 4
  %817 = mul i32 %816, %38
  %818 = add i32 %817, %34
  %819 = sext i32 %818 to i64
  %820 = getelementptr float, ptr %814, i64 %819
  store float %.0.sink, ptr %820, align 4
  %821 = add nsw i32 %.04490, 1
  %exitcond105.not = icmp eq i32 %821, %18
  br i1 %exitcond105.not, label %after_for.loopexit, label %for_loop_body

after_for6:                                       ; preds = %for_loop_test11.after_for10_crit_edge.us
  %822 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %822, label %for_loop_body54.lr.ph.split.us, label %false_block52

for_loop_body54.lr.ph.split.us:                   ; preds = %after_for6, %true_block1
  %823 = getelementptr i8, ptr %59, i64 20
  %824 = getelementptr i8, ptr %59, i64 24
  %825 = getelementptr i8, ptr %59, i64 4
  %826 = getelementptr i8, ptr %59, i64 8
  %827 = load ptr, ptr %826, align 8
  %828 = load i32, ptr %825, align 4
  %829 = load ptr, ptr %824, align 8
  %830 = load i32, ptr %823, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %44, i32 1)
  %smax103 = tail call i32 @llvm.smax.i32(i32 %42, i32 1)
  %wide.trip.count101 = zext i32 %smax to i64
  %831 = add nsw i64 %wide.trip.count101, -1
  %832 = mul i32 %21, %828
  %833 = mul i32 %832, %38
  %834 = add i32 %833, %40
  %835 = mul i32 %21, %830
  %836 = mul i32 %835, %38
  %837 = add i32 %836, %40
  %min.iters.check = icmp slt i32 %44, 4
  %838 = trunc nsw i64 %831 to i32
  %invariant.op419 = add i32 %834, %838
  %invariant.op421 = add i32 %837, %838
  %839 = icmp ugt i64 %831, 4294967295
  %min.iters.check118 = icmp slt i32 %44, 32
  %n.vec = and i64 %wide.trip.count101, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count101
  %n.vec.remaining = and i64 %wide.trip.count101, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec132 = and i64 %wide.trip.count101, 2147483644
  %cmp.n138 = icmp eq i64 %n.vec132, %wide.trip.count101
  %xtraiter = and i64 %wide.trip.count101, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %840 = lshr i64 %wide.trip.count101, 2
  %841 = mul nsw i64 %840, -4
  %842 = zext i32 %837 to i64
  %843 = zext i32 %830 to i64
  %844 = zext i32 %834 to i64
  %845 = zext i32 %828 to i64
  %846 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test61.after_for60_crit_edge.us, %for_loop_body54.lr.ph.split.us
  %lsr.iv469 = phi i64 [ %lsr.iv.next470, %for_loop_test61.after_for60_crit_edge.us ], [ %844, %for_loop_body54.lr.ph.split.us ]
  %lsr.iv467 = phi i64 [ %lsr.iv.next468, %for_loop_test61.after_for60_crit_edge.us ], [ %842, %for_loop_body54.lr.ph.split.us ]
  %.03686.us = phi i32 [ 0, %for_loop_body54.lr.ph.split.us ], [ %951, %for_loop_test61.after_for60_crit_edge.us ]
  %.03785.us = phi float [ 0.000000e+00, %for_loop_body54.lr.ph.split.us ], [ %.lcssa117, %for_loop_test61.after_for60_crit_edge.us ]
  %lsr484 = trunc i64 %lsr.iv469 to i32
  %lsr482 = trunc i64 %lsr.iv467 to i32
  br i1 %min.iters.check, label %for_loop_body58.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %847 = mul i32 %830, %.03686.us
  %848 = add i32 %837, %847
  %849 = mul i32 %828, %.03686.us
  %850 = add i32 %834, %849
  %.reass420 = add i32 %849, %invariant.op419
  %851 = icmp slt i32 %.reass420, %850
  %.reass422 = add i32 %847, %invariant.op421
  %852 = icmp slt i32 %.reass422, %848
  %853 = or i1 %852, %839
  %854 = or i1 %851, %853
  br i1 %854, label %for_loop_body58.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check118, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %855 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.03785.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv459 = phi i32 [ %lsr.iv.next460, %vector.body ], [ %lsr482, %vector.ph ]
  %lsr.iv455 = phi i32 [ %lsr.iv.next456, %vector.body ], [ %lsr484, %vector.ph ]
  %lsr.iv451 = phi i64 [ %lsr.iv.next452, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %855, %vector.ph ], [ %874, %vector.body ]
  %vec.phi119 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %875, %vector.body ]
  %vec.phi120 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %876, %vector.body ]
  %vec.phi121 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %877, %vector.body ]
  %856 = sext i32 %lsr.iv455 to i64
  %857 = getelementptr float, ptr %827, i64 %856
  %858 = getelementptr i8, ptr %857, i64 32
  %859 = getelementptr i8, ptr %857, i64 64
  %860 = getelementptr i8, ptr %857, i64 96
  %wide.load = load <8 x float>, ptr %857, align 4
  %wide.load122 = load <8 x float>, ptr %858, align 4
  %wide.load123 = load <8 x float>, ptr %859, align 4
  %wide.load124 = load <8 x float>, ptr %860, align 4
  %861 = sext i32 %lsr.iv459 to i64
  %862 = getelementptr float, ptr %829, i64 %861
  %863 = getelementptr i8, ptr %862, i64 32
  %864 = getelementptr i8, ptr %862, i64 64
  %865 = getelementptr i8, ptr %862, i64 96
  %wide.load125 = load <8 x float>, ptr %862, align 4
  %wide.load126 = load <8 x float>, ptr %863, align 4
  %wide.load127 = load <8 x float>, ptr %864, align 4
  %wide.load128 = load <8 x float>, ptr %865, align 4
  %866 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load125
  %867 = fsub reassoc ninf nsz <8 x float> %wide.load122, %wide.load126
  %868 = fsub reassoc ninf nsz <8 x float> %wide.load123, %wide.load127
  %869 = fsub reassoc ninf nsz <8 x float> %wide.load124, %wide.load128
  %870 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %866)
  %871 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %867)
  %872 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %868)
  %873 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %869)
  %874 = fadd reassoc ninf nsz <8 x float> %870, %vec.phi
  %875 = fadd reassoc ninf nsz <8 x float> %871, %vec.phi119
  %876 = fadd reassoc ninf nsz <8 x float> %872, %vec.phi120
  %877 = fadd reassoc ninf nsz <8 x float> %873, %vec.phi121
  %lsr.iv.next452 = add nsw i64 %lsr.iv451, -32
  %lsr.iv.next456 = add i32 %lsr.iv455, 32
  %lsr.iv.next460 = add i32 %lsr.iv459, 32
  %878 = icmp eq i64 %lsr.iv.next452, 0
  br i1 %878, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %875, %874
  %bin.rdx129 = fadd reassoc ninf nsz <8 x float> %876, %bin.rdx
  %bin.rdx130 = fadd reassoc ninf nsz <8 x float> %877, %bin.rdx129
  %879 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx130)
  br i1 %cmp.n, label %for_loop_test61.after_for60_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body58.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %879, %vec.epilog.iter.check ], [ %.03785.us, %vector.main.loop.iter.check ]
  %880 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %881 = add i64 %841, %vec.epilog.resume.val
  %882 = trunc i64 %vec.epilog.resume.val to i32
  %883 = add i32 %lsr484, %882
  %884 = add i32 %lsr482, %882
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv465 = phi i32 [ %lsr.iv.next466, %vec.epilog.vector.body ], [ %884, %vec.epilog.ph ]
  %lsr.iv463 = phi i32 [ %lsr.iv.next464, %vec.epilog.vector.body ], [ %883, %vec.epilog.ph ]
  %lsr.iv461 = phi i64 [ %lsr.iv.next462, %vec.epilog.vector.body ], [ %881, %vec.epilog.ph ]
  %vec.phi134 = phi <4 x float> [ %880, %vec.epilog.ph ], [ %891, %vec.epilog.vector.body ]
  %885 = sext i32 %lsr.iv463 to i64
  %886 = getelementptr float, ptr %827, i64 %885
  %wide.load135 = load <4 x float>, ptr %886, align 4
  %887 = sext i32 %lsr.iv465 to i64
  %888 = getelementptr float, ptr %829, i64 %887
  %wide.load136 = load <4 x float>, ptr %888, align 4
  %889 = fsub reassoc ninf nsz <4 x float> %wide.load135, %wide.load136
  %890 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %889)
  %891 = fadd reassoc ninf nsz <4 x float> %890, %vec.phi134
  %lsr.iv.next462 = add i64 %lsr.iv461, 4
  %lsr.iv.next464 = add i32 %lsr.iv463, 4
  %lsr.iv.next466 = add i32 %lsr.iv465, 4
  %892 = icmp eq i64 %lsr.iv.next462, 0
  br i1 %892, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %893 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %891)
  br i1 %cmp.n138, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader

for_loop_body58.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv98.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec132, %vec.epilog.middle.block ]
  %.181.us.ph = phi float [ %879, %vec.epilog.iter.check ], [ %.03785.us, %iter.check ], [ %.03785.us, %vector.scevcheck ], [ %893, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body58.us.prol.loopexit, label %for_loop_body58.us.prol.preheader

for_loop_body58.us.prol.preheader:                ; preds = %for_loop_body58.us.preheader
  br label %for_loop_body58.us.prol

for_loop_body58.us.prol:                          ; preds = %for_loop_body58.us.prol, %for_loop_body58.us.prol.preheader
  %lsr.iv472 = phi i64 [ %846, %for_loop_body58.us.prol.preheader ], [ %lsr.iv.next473, %for_loop_body58.us.prol ]
  %indvars.iv98.prol = phi i64 [ %indvars.iv.next99.prol, %for_loop_body58.us.prol ], [ %indvars.iv98.ph, %for_loop_body58.us.prol.preheader ]
  %.181.us.prol = phi float [ %904, %for_loop_body58.us.prol ], [ %.181.us.ph, %for_loop_body58.us.prol.preheader ]
  %894 = add i64 %lsr.iv469, %indvars.iv98.prol
  %tmp471 = trunc i64 %894 to i32
  %895 = sext i32 %tmp471 to i64
  %896 = getelementptr float, ptr %827, i64 %895
  %897 = load float, ptr %896, align 4
  %898 = add i64 %lsr.iv467, %indvars.iv98.prol
  %tmp = trunc i64 %898 to i32
  %899 = sext i32 %tmp to i64
  %900 = getelementptr float, ptr %829, i64 %899
  %901 = load float, ptr %900, align 4
  %902 = fsub reassoc ninf nsz float %897, %901
  %903 = tail call noundef float @llvm.fabs.f32(float %902)
  %904 = fadd reassoc ninf nsz float %903, %.181.us.prol
  %indvars.iv.next99.prol = add nuw nsw i64 %indvars.iv98.prol, 1
  %lsr.iv.next473 = add nsw i64 %lsr.iv472, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next473, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body58.us.prol.loopexit.loopexit, label %for_loop_body58.us.prol, !llvm.loop !18

for_loop_body58.us.prol.loopexit.loopexit:        ; preds = %for_loop_body58.us.prol
  br label %for_loop_body58.us.prol.loopexit

for_loop_body58.us.prol.loopexit:                 ; preds = %for_loop_body58.us.prol.loopexit.loopexit, %for_loop_body58.us.preheader
  %.lcssa377.unr = phi float [ poison, %for_loop_body58.us.preheader ], [ %904, %for_loop_body58.us.prol.loopexit.loopexit ]
  %indvars.iv98.unr = phi i64 [ %indvars.iv98.ph, %for_loop_body58.us.preheader ], [ %indvars.iv.next99.prol, %for_loop_body58.us.prol.loopexit.loopexit ]
  %.181.us.unr = phi float [ %.181.us.ph, %for_loop_body58.us.preheader ], [ %904, %for_loop_body58.us.prol.loopexit.loopexit ]
  %905 = sub nsw i64 %indvars.iv98.ph, %wide.trip.count101
  %906 = icmp ugt i64 %905, -4
  br i1 %906, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader.new

for_loop_body58.us.preheader.new:                 ; preds = %for_loop_body58.us.prol.loopexit
  br label %for_loop_body58.us

for_loop_body58.us:                               ; preds = %for_loop_body58.us, %for_loop_body58.us.preheader.new
  %indvars.iv98 = phi i64 [ %indvars.iv98.unr, %for_loop_body58.us.preheader.new ], [ %indvars.iv.next99.3, %for_loop_body58.us ]
  %.181.us = phi float [ %.181.us.unr, %for_loop_body58.us.preheader.new ], [ %950, %for_loop_body58.us ]
  %907 = add i64 %lsr.iv469, %indvars.iv98
  %tmp481 = trunc i64 %907 to i32
  %908 = sext i32 %tmp481 to i64
  %909 = getelementptr float, ptr %827, i64 %908
  %910 = load float, ptr %909, align 4
  %911 = add i64 %lsr.iv467, %indvars.iv98
  %tmp480 = trunc i64 %911 to i32
  %912 = sext i32 %tmp480 to i64
  %913 = getelementptr float, ptr %829, i64 %912
  %914 = load float, ptr %913, align 4
  %915 = fsub reassoc ninf nsz float %910, %914
  %916 = tail call noundef float @llvm.fabs.f32(float %915)
  %917 = fadd reassoc ninf nsz float %916, %.181.us
  %918 = add i64 %907, 1
  %tmp479 = trunc i64 %918 to i32
  %919 = sext i32 %tmp479 to i64
  %920 = getelementptr float, ptr %827, i64 %919
  %921 = load float, ptr %920, align 4
  %922 = add i64 %911, 1
  %tmp478 = trunc i64 %922 to i32
  %923 = sext i32 %tmp478 to i64
  %924 = getelementptr float, ptr %829, i64 %923
  %925 = load float, ptr %924, align 4
  %926 = fsub reassoc ninf nsz float %921, %925
  %927 = tail call noundef float @llvm.fabs.f32(float %926)
  %928 = fadd reassoc ninf nsz float %927, %917
  %929 = add i64 %907, 2
  %tmp477 = trunc i64 %929 to i32
  %930 = sext i32 %tmp477 to i64
  %931 = getelementptr float, ptr %827, i64 %930
  %932 = load float, ptr %931, align 4
  %933 = add i64 %911, 2
  %tmp476 = trunc i64 %933 to i32
  %934 = sext i32 %tmp476 to i64
  %935 = getelementptr float, ptr %829, i64 %934
  %936 = load float, ptr %935, align 4
  %937 = fsub reassoc ninf nsz float %932, %936
  %938 = tail call noundef float @llvm.fabs.f32(float %937)
  %939 = fadd reassoc ninf nsz float %938, %928
  %940 = add i64 %907, 3
  %tmp475 = trunc i64 %940 to i32
  %941 = sext i32 %tmp475 to i64
  %942 = getelementptr float, ptr %827, i64 %941
  %943 = load float, ptr %942, align 4
  %944 = add i64 %911, 3
  %tmp474 = trunc i64 %944 to i32
  %945 = sext i32 %tmp474 to i64
  %946 = getelementptr float, ptr %829, i64 %945
  %947 = load float, ptr %946, align 4
  %948 = fsub reassoc ninf nsz float %943, %947
  %949 = tail call noundef float @llvm.fabs.f32(float %948)
  %950 = fadd reassoc ninf nsz float %949, %939
  %indvars.iv.next99.3 = add nuw nsw i64 %indvars.iv98, 4
  %exitcond102.not.3 = icmp eq i64 %wide.trip.count101, %indvars.iv.next99.3
  br i1 %exitcond102.not.3, label %for_loop_test61.after_for60_crit_edge.us.loopexit, label %for_loop_body58.us, !llvm.loop !20

for_loop_test61.after_for60_crit_edge.us.loopexit: ; preds = %for_loop_body58.us
  br label %for_loop_test61.after_for60_crit_edge.us

for_loop_test61.after_for60_crit_edge.us:         ; preds = %for_loop_test61.after_for60_crit_edge.us.loopexit, %for_loop_body58.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa117 = phi float [ %879, %middle.block ], [ %893, %vec.epilog.middle.block ], [ %.lcssa377.unr, %for_loop_body58.us.prol.loopexit ], [ %950, %for_loop_test61.after_for60_crit_edge.us.loopexit ]
  %951 = add nuw nsw i32 %.03686.us, 1
  %lsr.iv.next470 = add i64 %lsr.iv469, %845
  %lsr.iv.next468 = add i64 %lsr.iv467, %843
  %exitcond104.not = icmp eq i32 %951, %smax103
  br i1 %exitcond104.not, label %after_for56, label %iter.check

false_block52:                                    ; preds = %after_for6
  %952 = fdiv reassoc ninf nsz float %.lcssa116, %.lcssa
  br label %after_if53

after_if53:                                       ; preds = %after_for56, %false_block52
  %.038 = phi float [ %967, %after_for56 ], [ %952, %false_block52 ]
  %953 = getelementptr inbounds nuw i8, ptr %31, i64 16
  %954 = load float, ptr %953, align 4
  %955 = fmul reassoc ninf nsz float %954, %.038
  %956 = getelementptr i8, ptr %59, i64 136
  %957 = load float, ptr %956, align 4
  %958 = fsub reassoc ninf nsz float %955, %957
  %959 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %958, float 0.000000e+00)
  %960 = getelementptr i8, ptr %59, i64 132
  %961 = load float, ptr %960, align 4
  %962 = fmul reassoc ninf nsz float %961, 5.000000e-01
  %963 = fmul reassoc ninf nsz float %962, %959
  %964 = fcmp reassoc ninf nsz ugt float %963, 2.000000e+01
  br i1 %964, label %after_if3, label %true_block62

after_for56:                                      ; preds = %for_loop_test61.after_for60_crit_edge.us
  %965 = mul i32 %42, %44
  %966 = sitofp i32 %965 to float
  %967 = fdiv reassoc ninf nsz float %.lcssa117, %966
  br label %after_if53

true_block62:                                     ; preds = %after_if53
  %968 = fadd reassoc ninf nsz float %963, -2.000000e+00
  %969 = tail call noundef float @expf(float noundef %968) #9
  %970 = fadd reassoc ninf nsz float %969, 1.000000e+00
  %971 = fdiv reassoc ninf nsz float 1.000000e+00, %970
  br label %after_if3.sink.split
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #1

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.10, align 8
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
attributes #1 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nofree nounwind memory(readwrite, inaccessiblemem: write) }
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
