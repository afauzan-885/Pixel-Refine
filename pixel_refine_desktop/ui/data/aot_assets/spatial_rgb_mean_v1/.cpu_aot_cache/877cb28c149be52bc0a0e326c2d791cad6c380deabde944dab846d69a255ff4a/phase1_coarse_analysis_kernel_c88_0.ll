; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.8 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @phase1_coarse_analysis_kernel_c88_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
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

define void @phase1_coarse_analysis_kernel_c88_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %.044100 = phi i32 [ %1237, %after_if3 ], [ %16, %for_loop_body.preheader ]
  %29 = load ptr, ptr %3, align 8
  %30 = getelementptr inbounds nuw i8, ptr %29, i64 32872
  %31 = load ptr, ptr %30, align 8
  %32 = getelementptr inbounds nuw i8, ptr %31, i64 4
  %33 = load i32, ptr %32, align 4
  %34 = srem i32 %.044100, %33
  %35 = sdiv i32 %.044100, %33
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
  br i1 %spec.select, label %true_block1, label %after_if3

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
  %.not101 = icmp samesign ult i32 %44, 3
  %or.cond = select i1 %.not, i1 true, i1 %.not101
  br i1 %or.cond, label %for_loop_body54.lr.ph.split.us, label %for_loop_body4.lr.ph.split.us

for_loop_body4.lr.ph.split.us:                    ; preds = %true_block1
  %60 = add nsw i32 %44, -1
  %61 = lshr i32 %60, 1
  %62 = getelementptr i8, ptr %59, i64 20
  %63 = getelementptr i8, ptr %59, i64 24
  %64 = getelementptr i8, ptr %59, i64 4
  %65 = getelementptr i8, ptr %59, i64 8
  %66 = load ptr, ptr %65, align 8
  %67 = load i32, ptr %64, align 4
  %68 = load ptr, ptr %63, align 8
  %69 = load i32, ptr %62, align 4
  %wide.trip.count = zext i32 %61 to i64
  %70 = add nsw i64 %wide.trip.count, -1
  %71 = mul i32 %67, %57
  %72 = add i32 %58, %71
  %73 = shl i32 %67, 1
  %74 = mul i32 %69, %57
  %75 = add i32 %58, %74
  %76 = shl i32 %69, 1
  %77 = add i32 %40, 2
  %78 = add i32 %77, %71
  %79 = add i32 %40, %71
  %80 = mul i32 %21, %67
  %81 = mul i32 %80, %38
  %82 = add i32 %81, 2
  %83 = add i32 %82, %40
  %84 = add i32 %81, %40
  %85 = add i32 %39, 2
  %86 = mul i32 %67, %85
  %87 = add i32 %77, %86
  %88 = add i32 %40, %86
  %89 = add i32 %58, %86
  %90 = add i32 %81, 1
  %91 = add i32 %90, %40
  %92 = add i32 %77, %74
  %93 = add i32 %40, %74
  %94 = mul i32 %21, %69
  %95 = mul i32 %94, %38
  %96 = add i32 %95, 2
  %97 = add i32 %96, %40
  %98 = add i32 %95, %40
  %99 = mul i32 %69, %85
  %100 = add i32 %77, %99
  %101 = add i32 %40, %99
  %102 = add i32 %58, %99
  %103 = add i32 %95, 1
  %104 = add i32 %103, %40
  %min.iters.check203 = icmp ult i32 %44, 17
  %105 = trunc nsw i64 %70 to i32
  %mul.result = shl i32 %105, 1
  %invariant.op517 = add i32 %72, %mul.result
  %invariant.op519 = add i32 %75, %mul.result
  %106 = icmp ugt i64 %70, 4294967295
  %invariant.op521 = add i32 %78, %mul.result
  %invariant.op523 = add i32 %79, %mul.result
  %invariant.op525 = add i32 %83, %mul.result
  %invariant.op527 = add i32 %84, %mul.result
  %invariant.op529 = add i32 %87, %mul.result
  %invariant.op531 = add i32 %88, %mul.result
  %invariant.op533 = add i32 %89, %mul.result
  %invariant.op535 = add i32 %91, %mul.result
  %invariant.op537 = add i32 %92, %mul.result
  %invariant.op539 = add i32 %93, %mul.result
  %invariant.op541 = add i32 %97, %mul.result
  %invariant.op543 = add i32 %98, %mul.result
  %invariant.op545 = add i32 %100, %mul.result
  %invariant.op547 = add i32 %101, %mul.result
  %invariant.op549 = add i32 %102, %mul.result
  %invariant.op551 = add i32 %104, %mul.result
  %min.iters.check206 = icmp ult i32 %44, 65
  %n.vec210 = and i64 %wide.trip.count, 2147483616
  %broadcast.splatinsert = insertelement <8 x i1> poison, i1 %54, i64 0
  %broadcast.splat = shufflevector <8 x i1> %broadcast.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %107 = xor <8 x i1> %broadcast.splat, splat (i1 true)
  %broadcast.splatinsert221 = insertelement <8 x i32> poison, i32 %58, i64 0
  %broadcast.splat222 = shufflevector <8 x i32> %broadcast.splatinsert221, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert238 = insertelement <8 x i32> poison, i32 %40, i64 0
  %broadcast.splat239 = shufflevector <8 x i32> %broadcast.splatinsert238, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert308 = insertelement <8 x float> poison, float %50, i64 0
  %broadcast.splat309 = shufflevector <8 x float> %broadcast.splatinsert308, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert310 = insertelement <8 x float> poison, float %53, i64 0
  %broadcast.splat311 = shufflevector <8 x float> %broadcast.splatinsert310, <8 x float> poison, <8 x i32> zeroinitializer
  %invariant.op = add <8 x i32> splat (i32 16), %broadcast.splat222
  %invariant.op507 = add <8 x i32> splat (i32 32), %broadcast.splat222
  %invariant.op509 = add <8 x i32> splat (i32 48), %broadcast.splat222
  %invariant.op511 = add <8 x i32> splat (i32 16), %broadcast.splat239
  %invariant.op513 = add <8 x i32> splat (i32 32), %broadcast.splat239
  %invariant.op515 = add <8 x i32> splat (i32 48), %broadcast.splat239
  %cmp.n374 = icmp eq i64 %n.vec210, %wide.trip.count
  %n.vec.remaining382 = and i64 %wide.trip.count, 24
  %min.epilog.iters.check383 = icmp eq i64 %n.vec.remaining382, 0
  %n.vec385 = and i64 %wide.trip.count, 2147483640
  %cmp.n447 = icmp eq i64 %n.vec385, %wide.trip.count
  %108 = zext i32 %60 to i64
  %109 = lshr i64 %108, 4
  %110 = mul nsw i64 %109, -8
  %111 = mul nsw i64 %wide.trip.count, -1
  br label %iter.check205

iter.check205:                                    ; preds = %for_loop_test11.after_for10_crit_edge.us, %for_loop_body4.lr.ph.split.us
  %lsr.iv585 = phi i32 [ %lsr.iv.next586, %for_loop_test11.after_for10_crit_edge.us ], [ %79, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv581 = phi i32 [ %lsr.iv.next582, %for_loop_test11.after_for10_crit_edge.us ], [ %93, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv577 = phi i32 [ %lsr.iv.next578, %for_loop_test11.after_for10_crit_edge.us ], [ %88, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv573 = phi i32 [ %lsr.iv.next574, %for_loop_test11.after_for10_crit_edge.us ], [ %84, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv569 = phi i32 [ %lsr.iv.next570, %for_loop_test11.after_for10_crit_edge.us ], [ %101, %for_loop_body4.lr.ph.split.us ]
  %lsr.iv565 = phi i32 [ %lsr.iv.next566, %for_loop_test11.after_for10_crit_edge.us ], [ %98, %for_loop_body4.lr.ph.split.us ]
  %.04987.us = phi i32 [ 0, %for_loop_body4.lr.ph.split.us ], [ %1227, %for_loop_test11.after_for10_crit_edge.us ]
  %.05086.us = phi float [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ], [ %.lcssa, %for_loop_test11.after_for10_crit_edge.us ]
  %.05285.us = phi float [ 0.000000e+00, %for_loop_body4.lr.ph.split.us ], [ %.lcssa126, %for_loop_test11.after_for10_crit_edge.us ]
  %112 = shl nuw i32 %.04987.us, 1
  %113 = add i32 %57, %112
  %114 = add i32 %112, %39
  %115 = add i32 %113, 1
  %116 = mul i32 %67, %113
  %117 = mul i32 %69, %113
  %118 = mul i32 %67, %114
  %119 = mul i32 %67, %115
  %120 = mul i32 %69, %114
  %121 = mul i32 %69, %115
  br i1 %min.iters.check203, label %for_loop_body8.us.preheader, label %vector.scevcheck150

vector.scevcheck150:                              ; preds = %iter.check205
  %122 = mul i32 %76, %.04987.us
  %123 = add i32 %104, %122
  %124 = add i32 %102, %122
  %125 = add i32 %101, %122
  %126 = add i32 %100, %122
  %127 = add i32 %98, %122
  %128 = add i32 %97, %122
  %129 = add i32 %93, %122
  %130 = add i32 %92, %122
  %131 = mul i32 %73, %.04987.us
  %132 = add i32 %91, %131
  %133 = add i32 %89, %131
  %134 = add i32 %88, %131
  %135 = add i32 %87, %131
  %136 = add i32 %84, %131
  %137 = add i32 %83, %131
  %138 = add i32 %79, %131
  %139 = add i32 %78, %131
  %140 = add i32 %75, %122
  %141 = add i32 %72, %131
  %.reass518 = add i32 %131, %invariant.op517
  %142 = icmp slt i32 %.reass518, %141
  %.reass520 = add i32 %122, %invariant.op519
  %143 = icmp slt i32 %.reass520, %140
  %144 = or i1 %143, %106
  %.reass522 = add i32 %131, %invariant.op521
  %145 = icmp slt i32 %.reass522, %139
  %.reass524 = add i32 %131, %invariant.op523
  %146 = icmp slt i32 %.reass524, %138
  %.reass526 = add i32 %131, %invariant.op525
  %147 = icmp slt i32 %.reass526, %137
  %.reass528 = add i32 %131, %invariant.op527
  %148 = icmp slt i32 %.reass528, %136
  %.reass530 = add i32 %131, %invariant.op529
  %149 = icmp slt i32 %.reass530, %135
  %.reass532 = add i32 %131, %invariant.op531
  %150 = icmp slt i32 %.reass532, %134
  %.reass534 = add i32 %131, %invariant.op533
  %151 = icmp slt i32 %.reass534, %133
  %.reass536 = add i32 %131, %invariant.op535
  %152 = icmp slt i32 %.reass536, %132
  %153 = or i1 %152, %106
  %.reass538 = add i32 %122, %invariant.op537
  %154 = icmp slt i32 %.reass538, %130
  %.reass540 = add i32 %122, %invariant.op539
  %155 = icmp slt i32 %.reass540, %129
  %.reass542 = add i32 %122, %invariant.op541
  %156 = icmp slt i32 %.reass542, %128
  %.reass544 = add i32 %122, %invariant.op543
  %157 = icmp slt i32 %.reass544, %127
  %.reass546 = add i32 %122, %invariant.op545
  %158 = icmp slt i32 %.reass546, %126
  %.reass548 = add i32 %122, %invariant.op547
  %159 = icmp slt i32 %.reass548, %125
  %.reass550 = add i32 %122, %invariant.op549
  %160 = icmp slt i32 %.reass550, %124
  %.reass552 = add i32 %122, %invariant.op551
  %161 = icmp slt i32 %.reass552, %123
  %162 = or i1 %161, %106
  %163 = or i1 %142, %144
  %164 = or i1 %145, %163
  %165 = or i1 %146, %164
  %166 = or i1 %147, %165
  %167 = or i1 %148, %166
  %168 = or i1 %149, %167
  %169 = or i1 %150, %168
  %170 = or i1 %151, %169
  %171 = or i1 %170, %153
  %172 = or i1 %154, %171
  %173 = or i1 %155, %172
  %174 = or i1 %156, %173
  %175 = or i1 %157, %174
  %176 = or i1 %158, %175
  %177 = or i1 %159, %176
  %178 = or i1 %160, %177
  %179 = or i1 %178, %162
  br i1 %179, label %for_loop_body8.us.preheader, label %vector.main.loop.iter.check207

vector.main.loop.iter.check207:                   ; preds = %vector.scevcheck150
  br i1 %min.iters.check206, label %vec.epilog.ph380, label %vector.ph208

vector.ph208:                                     ; preds = %vector.main.loop.iter.check207
  %180 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05086.us, i64 0
  %181 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05285.us, i64 0
  %broadcast.splatinsert223 = insertelement <8 x i32> poison, i32 %116, i64 0
  %broadcast.splat224 = shufflevector <8 x i32> %broadcast.splatinsert223, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert228 = insertelement <8 x i32> poison, i32 %117, i64 0
  %broadcast.splat229 = shufflevector <8 x i32> %broadcast.splatinsert228, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert244 = insertelement <8 x i32> poison, i32 %118, i64 0
  %broadcast.splat245 = shufflevector <8 x i32> %broadcast.splatinsert244, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert254 = insertelement <8 x i32> poison, i32 %119, i64 0
  %broadcast.splat255 = shufflevector <8 x i32> %broadcast.splatinsert254, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert280 = insertelement <8 x i32> poison, i32 %120, i64 0
  %broadcast.splat281 = shufflevector <8 x i32> %broadcast.splatinsert280, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert290 = insertelement <8 x i32> poison, i32 %121, i64 0
  %broadcast.splat291 = shufflevector <8 x i32> %broadcast.splatinsert290, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body211

vector.body211:                                   ; preds = %vector.body211, %vector.ph208
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body211 ], [ %n.vec210, %vector.ph208 ]
  %vec.phi213 = phi <8 x float> [ %180, %vector.ph208 ], [ %873, %vector.body211 ]
  %vec.phi214 = phi <8 x float> [ zeroinitializer, %vector.ph208 ], [ %874, %vector.body211 ]
  %vec.phi215 = phi <8 x float> [ zeroinitializer, %vector.ph208 ], [ %875, %vector.body211 ]
  %vec.phi216 = phi <8 x float> [ zeroinitializer, %vector.ph208 ], [ %876, %vector.body211 ]
  %vec.phi217 = phi <8 x float> [ %181, %vector.ph208 ], [ %869, %vector.body211 ]
  %vec.phi218 = phi <8 x float> [ zeroinitializer, %vector.ph208 ], [ %870, %vector.body211 ]
  %vec.phi219 = phi <8 x float> [ zeroinitializer, %vector.ph208 ], [ %871, %vector.body211 ]
  %vec.phi220 = phi <8 x float> [ zeroinitializer, %vector.ph208 ], [ %872, %vector.body211 ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph208 ], [ %vec.ind.next, %vector.body211 ]
  %182 = shl <8 x i32> %vec.ind, splat (i32 1)
  %183 = add <8 x i32> %broadcast.splat222, %182
  %.reass = add <8 x i32> %182, %invariant.op
  %.reass508 = add <8 x i32> %182, %invariant.op507
  %.reass510 = add <8 x i32> %182, %invariant.op509
  %184 = add <8 x i32> %broadcast.splat224, %183
  %185 = add <8 x i32> %broadcast.splat224, %.reass
  %186 = add <8 x i32> %broadcast.splat224, %.reass508
  %187 = add <8 x i32> %broadcast.splat224, %.reass510
  %188 = sext <8 x i32> %184 to <8 x i64>
  %189 = sext <8 x i32> %185 to <8 x i64>
  %190 = sext <8 x i32> %186 to <8 x i64>
  %191 = sext <8 x i32> %187 to <8 x i64>
  %192 = getelementptr float, ptr %66, <8 x i64> %188
  %193 = getelementptr float, ptr %66, <8 x i64> %189
  %194 = getelementptr float, ptr %66, <8 x i64> %190
  %195 = getelementptr float, ptr %66, <8 x i64> %191
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %192, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather225 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %193, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather226 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %194, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather227 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %195, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %196 = add <8 x i32> %broadcast.splat229, %183
  %197 = add <8 x i32> %broadcast.splat229, %.reass
  %198 = add <8 x i32> %broadcast.splat229, %.reass508
  %199 = add <8 x i32> %broadcast.splat229, %.reass510
  %200 = sext <8 x i32> %196 to <8 x i64>
  %201 = sext <8 x i32> %197 to <8 x i64>
  %202 = sext <8 x i32> %198 to <8 x i64>
  %203 = sext <8 x i32> %199 to <8 x i64>
  %204 = getelementptr float, ptr %68, <8 x i64> %200
  %205 = getelementptr float, ptr %68, <8 x i64> %201
  %206 = getelementptr float, ptr %68, <8 x i64> %202
  %207 = getelementptr float, ptr %68, <8 x i64> %203
  %wide.masked.gather230 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %204, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather231 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %205, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather232 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %206, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather233 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %207, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %208 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather230
  %209 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather225, %wide.masked.gather231
  %210 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather232
  %211 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather233
  %212 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %208)
  %213 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %209)
  %214 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %210)
  %215 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %211)
  %216 = add <8 x i32> %183, splat (i32 1)
  %217 = add <8 x i32> %.reass, splat (i32 1)
  %218 = add <8 x i32> %.reass508, splat (i32 1)
  %219 = add <8 x i32> %.reass510, splat (i32 1)
  %220 = add <8 x i32> %broadcast.splat224, %216
  %221 = add <8 x i32> %broadcast.splat224, %217
  %222 = add <8 x i32> %broadcast.splat224, %218
  %223 = add <8 x i32> %broadcast.splat224, %219
  %224 = sext <8 x i32> %220 to <8 x i64>
  %225 = sext <8 x i32> %221 to <8 x i64>
  %226 = sext <8 x i32> %222 to <8 x i64>
  %227 = sext <8 x i32> %223 to <8 x i64>
  %228 = getelementptr float, ptr %66, <8 x i64> %224
  %229 = getelementptr float, ptr %66, <8 x i64> %225
  %230 = getelementptr float, ptr %66, <8 x i64> %226
  %231 = getelementptr float, ptr %66, <8 x i64> %227
  %wide.masked.gather234 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %228, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather235 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %229, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather236 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %230, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather237 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %231, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %232 = add <8 x i32> %182, %broadcast.splat239
  %.reass512 = add <8 x i32> %182, %invariant.op511
  %.reass514 = add <8 x i32> %182, %invariant.op513
  %.reass516 = add <8 x i32> %182, %invariant.op515
  %233 = add <8 x i32> %broadcast.splat224, %232
  %234 = add <8 x i32> %broadcast.splat224, %.reass512
  %235 = add <8 x i32> %broadcast.splat224, %.reass514
  %236 = add <8 x i32> %broadcast.splat224, %.reass516
  %237 = sext <8 x i32> %233 to <8 x i64>
  %238 = sext <8 x i32> %234 to <8 x i64>
  %239 = sext <8 x i32> %235 to <8 x i64>
  %240 = sext <8 x i32> %236 to <8 x i64>
  %241 = getelementptr float, ptr %66, <8 x i64> %237
  %242 = getelementptr float, ptr %66, <8 x i64> %238
  %243 = getelementptr float, ptr %66, <8 x i64> %239
  %244 = getelementptr float, ptr %66, <8 x i64> %240
  %wide.masked.gather240 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %241, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather241 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %242, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather242 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %243, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather243 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %244, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %245 = add <8 x i32> %broadcast.splat245, %216
  %246 = add <8 x i32> %broadcast.splat245, %217
  %247 = add <8 x i32> %broadcast.splat245, %218
  %248 = add <8 x i32> %broadcast.splat245, %219
  %249 = sext <8 x i32> %245 to <8 x i64>
  %250 = sext <8 x i32> %246 to <8 x i64>
  %251 = sext <8 x i32> %247 to <8 x i64>
  %252 = sext <8 x i32> %248 to <8 x i64>
  %253 = getelementptr float, ptr %66, <8 x i64> %249
  %254 = getelementptr float, ptr %66, <8 x i64> %250
  %255 = getelementptr float, ptr %66, <8 x i64> %251
  %256 = getelementptr float, ptr %66, <8 x i64> %252
  %wide.masked.gather246 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %253, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather247 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %254, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather248 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %255, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather249 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %256, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %257 = add <8 x i32> %broadcast.splat245, %232
  %258 = add <8 x i32> %broadcast.splat245, %.reass512
  %259 = add <8 x i32> %broadcast.splat245, %.reass514
  %260 = add <8 x i32> %broadcast.splat245, %.reass516
  %261 = sext <8 x i32> %257 to <8 x i64>
  %262 = sext <8 x i32> %258 to <8 x i64>
  %263 = sext <8 x i32> %259 to <8 x i64>
  %264 = sext <8 x i32> %260 to <8 x i64>
  %265 = getelementptr float, ptr %66, <8 x i64> %261
  %266 = getelementptr float, ptr %66, <8 x i64> %262
  %267 = getelementptr float, ptr %66, <8 x i64> %263
  %268 = getelementptr float, ptr %66, <8 x i64> %264
  %wide.masked.gather250 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %265, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather251 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %266, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather252 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %267, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather253 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %268, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %269 = add <8 x i32> %broadcast.splat255, %216
  %270 = add <8 x i32> %broadcast.splat255, %217
  %271 = add <8 x i32> %broadcast.splat255, %218
  %272 = add <8 x i32> %broadcast.splat255, %219
  %273 = sext <8 x i32> %269 to <8 x i64>
  %274 = sext <8 x i32> %270 to <8 x i64>
  %275 = sext <8 x i32> %271 to <8 x i64>
  %276 = sext <8 x i32> %272 to <8 x i64>
  %277 = getelementptr float, ptr %66, <8 x i64> %273
  %278 = getelementptr float, ptr %66, <8 x i64> %274
  %279 = getelementptr float, ptr %66, <8 x i64> %275
  %280 = getelementptr float, ptr %66, <8 x i64> %276
  %wide.masked.gather256 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %277, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather257 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %278, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather258 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %279, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather259 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %280, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %281 = add <8 x i32> %broadcast.splat255, %232
  %282 = add <8 x i32> %broadcast.splat255, %.reass512
  %283 = add <8 x i32> %broadcast.splat255, %.reass514
  %284 = add <8 x i32> %broadcast.splat255, %.reass516
  %285 = sext <8 x i32> %281 to <8 x i64>
  %286 = sext <8 x i32> %282 to <8 x i64>
  %287 = sext <8 x i32> %283 to <8 x i64>
  %288 = sext <8 x i32> %284 to <8 x i64>
  %289 = getelementptr float, ptr %66, <8 x i64> %285
  %290 = getelementptr float, ptr %66, <8 x i64> %286
  %291 = getelementptr float, ptr %66, <8 x i64> %287
  %292 = getelementptr float, ptr %66, <8 x i64> %288
  %wide.masked.gather260 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %289, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather261 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %290, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather262 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %291, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather263 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %292, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %293 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather234, %wide.masked.gather246
  %294 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather235, %wide.masked.gather247
  %295 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather236, %wide.masked.gather248
  %296 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather237, %wide.masked.gather249
  %297 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather240, %wide.masked.gather250
  %298 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather241, %wide.masked.gather251
  %299 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather242, %wide.masked.gather252
  %300 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather243, %wide.masked.gather253
  %301 = fadd reassoc ninf nsz <8 x float> %293, %wide.masked.gather256
  %302 = fadd reassoc ninf nsz <8 x float> %294, %wide.masked.gather257
  %303 = fadd reassoc ninf nsz <8 x float> %295, %wide.masked.gather258
  %304 = fadd reassoc ninf nsz <8 x float> %296, %wide.masked.gather259
  %305 = fadd reassoc ninf nsz <8 x float> %297, %wide.masked.gather260
  %306 = fadd reassoc ninf nsz <8 x float> %298, %wide.masked.gather261
  %307 = fadd reassoc ninf nsz <8 x float> %299, %wide.masked.gather262
  %308 = fadd reassoc ninf nsz <8 x float> %300, %wide.masked.gather263
  %309 = fsub reassoc ninf nsz <8 x float> %301, %305
  %310 = fsub reassoc ninf nsz <8 x float> %302, %306
  %311 = fsub reassoc ninf nsz <8 x float> %303, %307
  %312 = fsub reassoc ninf nsz <8 x float> %304, %308
  %313 = fmul reassoc ninf nsz <8 x float> %309, splat (float 0x3FD5555560000000)
  %314 = fmul reassoc ninf nsz <8 x float> %310, splat (float 0x3FD5555560000000)
  %315 = fmul reassoc ninf nsz <8 x float> %311, splat (float 0x3FD5555560000000)
  %316 = fmul reassoc ninf nsz <8 x float> %312, splat (float 0x3FD5555560000000)
  %317 = add <8 x i32> %broadcast.splat255, %183
  %318 = add <8 x i32> %broadcast.splat255, %.reass
  %319 = add <8 x i32> %broadcast.splat255, %.reass508
  %320 = add <8 x i32> %broadcast.splat255, %.reass510
  %321 = sext <8 x i32> %317 to <8 x i64>
  %322 = sext <8 x i32> %318 to <8 x i64>
  %323 = sext <8 x i32> %319 to <8 x i64>
  %324 = sext <8 x i32> %320 to <8 x i64>
  %325 = getelementptr float, ptr %66, <8 x i64> %321
  %326 = getelementptr float, ptr %66, <8 x i64> %322
  %327 = getelementptr float, ptr %66, <8 x i64> %323
  %328 = getelementptr float, ptr %66, <8 x i64> %324
  %wide.masked.gather264 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %325, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather265 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %326, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather266 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %327, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather267 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %328, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %329 = add <8 x i32> %broadcast.splat245, %183
  %330 = add <8 x i32> %broadcast.splat245, %.reass
  %331 = add <8 x i32> %broadcast.splat245, %.reass508
  %332 = add <8 x i32> %broadcast.splat245, %.reass510
  %333 = sext <8 x i32> %329 to <8 x i64>
  %334 = sext <8 x i32> %330 to <8 x i64>
  %335 = sext <8 x i32> %331 to <8 x i64>
  %336 = sext <8 x i32> %332 to <8 x i64>
  %337 = getelementptr float, ptr %66, <8 x i64> %333
  %338 = getelementptr float, ptr %66, <8 x i64> %334
  %339 = getelementptr float, ptr %66, <8 x i64> %335
  %340 = getelementptr float, ptr %66, <8 x i64> %336
  %wide.masked.gather268 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %337, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather269 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %338, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather270 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %339, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather271 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %340, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %341 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather246, %wide.masked.gather250
  %342 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather247, %wide.masked.gather251
  %343 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather248, %wide.masked.gather252
  %344 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather249, %wide.masked.gather253
  %345 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather256, %341
  %346 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather257, %342
  %347 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather258, %343
  %348 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather259, %344
  %349 = fadd reassoc ninf nsz <8 x float> %345, %wide.masked.gather260
  %350 = fadd reassoc ninf nsz <8 x float> %346, %wide.masked.gather261
  %351 = fadd reassoc ninf nsz <8 x float> %347, %wide.masked.gather262
  %352 = fadd reassoc ninf nsz <8 x float> %348, %wide.masked.gather263
  %353 = fadd reassoc ninf nsz <8 x float> %349, %wide.masked.gather264
  %354 = fadd reassoc ninf nsz <8 x float> %350, %wide.masked.gather265
  %355 = fadd reassoc ninf nsz <8 x float> %351, %wide.masked.gather266
  %356 = fadd reassoc ninf nsz <8 x float> %352, %wide.masked.gather267
  %357 = fsub reassoc ninf nsz <8 x float> %353, %wide.masked.gather268
  %358 = fsub reassoc ninf nsz <8 x float> %354, %wide.masked.gather269
  %359 = fsub reassoc ninf nsz <8 x float> %355, %wide.masked.gather270
  %360 = fsub reassoc ninf nsz <8 x float> %356, %wide.masked.gather271
  %361 = fmul reassoc ninf nsz <8 x float> %357, splat (float 0x3FD5555560000000)
  %362 = fmul reassoc ninf nsz <8 x float> %358, splat (float 0x3FD5555560000000)
  %363 = fmul reassoc ninf nsz <8 x float> %359, splat (float 0x3FD5555560000000)
  %364 = fmul reassoc ninf nsz <8 x float> %360, splat (float 0x3FD5555560000000)
  %365 = add <8 x i32> %broadcast.splat229, %216
  %366 = add <8 x i32> %broadcast.splat229, %217
  %367 = add <8 x i32> %broadcast.splat229, %218
  %368 = add <8 x i32> %broadcast.splat229, %219
  %369 = sext <8 x i32> %365 to <8 x i64>
  %370 = sext <8 x i32> %366 to <8 x i64>
  %371 = sext <8 x i32> %367 to <8 x i64>
  %372 = sext <8 x i32> %368 to <8 x i64>
  %373 = getelementptr float, ptr %68, <8 x i64> %369
  %374 = getelementptr float, ptr %68, <8 x i64> %370
  %375 = getelementptr float, ptr %68, <8 x i64> %371
  %376 = getelementptr float, ptr %68, <8 x i64> %372
  %wide.masked.gather272 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %373, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather273 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %374, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather274 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %375, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather275 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %376, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %377 = add <8 x i32> %broadcast.splat229, %232
  %378 = add <8 x i32> %broadcast.splat229, %.reass512
  %379 = add <8 x i32> %broadcast.splat229, %.reass514
  %380 = add <8 x i32> %broadcast.splat229, %.reass516
  %381 = sext <8 x i32> %377 to <8 x i64>
  %382 = sext <8 x i32> %378 to <8 x i64>
  %383 = sext <8 x i32> %379 to <8 x i64>
  %384 = sext <8 x i32> %380 to <8 x i64>
  %385 = getelementptr float, ptr %68, <8 x i64> %381
  %386 = getelementptr float, ptr %68, <8 x i64> %382
  %387 = getelementptr float, ptr %68, <8 x i64> %383
  %388 = getelementptr float, ptr %68, <8 x i64> %384
  %wide.masked.gather276 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %385, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather277 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %386, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather278 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %387, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather279 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %388, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %389 = add <8 x i32> %broadcast.splat281, %216
  %390 = add <8 x i32> %broadcast.splat281, %217
  %391 = add <8 x i32> %broadcast.splat281, %218
  %392 = add <8 x i32> %broadcast.splat281, %219
  %393 = sext <8 x i32> %389 to <8 x i64>
  %394 = sext <8 x i32> %390 to <8 x i64>
  %395 = sext <8 x i32> %391 to <8 x i64>
  %396 = sext <8 x i32> %392 to <8 x i64>
  %397 = getelementptr float, ptr %68, <8 x i64> %393
  %398 = getelementptr float, ptr %68, <8 x i64> %394
  %399 = getelementptr float, ptr %68, <8 x i64> %395
  %400 = getelementptr float, ptr %68, <8 x i64> %396
  %wide.masked.gather282 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %397, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather283 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %398, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather284 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %399, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather285 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %400, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %401 = add <8 x i32> %broadcast.splat281, %232
  %402 = add <8 x i32> %broadcast.splat281, %.reass512
  %403 = add <8 x i32> %broadcast.splat281, %.reass514
  %404 = add <8 x i32> %broadcast.splat281, %.reass516
  %405 = sext <8 x i32> %401 to <8 x i64>
  %406 = sext <8 x i32> %402 to <8 x i64>
  %407 = sext <8 x i32> %403 to <8 x i64>
  %408 = sext <8 x i32> %404 to <8 x i64>
  %409 = getelementptr float, ptr %68, <8 x i64> %405
  %410 = getelementptr float, ptr %68, <8 x i64> %406
  %411 = getelementptr float, ptr %68, <8 x i64> %407
  %412 = getelementptr float, ptr %68, <8 x i64> %408
  %wide.masked.gather286 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %409, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather287 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %410, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather288 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %411, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather289 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %412, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %413 = add <8 x i32> %broadcast.splat291, %216
  %414 = add <8 x i32> %broadcast.splat291, %217
  %415 = add <8 x i32> %broadcast.splat291, %218
  %416 = add <8 x i32> %broadcast.splat291, %219
  %417 = sext <8 x i32> %413 to <8 x i64>
  %418 = sext <8 x i32> %414 to <8 x i64>
  %419 = sext <8 x i32> %415 to <8 x i64>
  %420 = sext <8 x i32> %416 to <8 x i64>
  %421 = getelementptr float, ptr %68, <8 x i64> %417
  %422 = getelementptr float, ptr %68, <8 x i64> %418
  %423 = getelementptr float, ptr %68, <8 x i64> %419
  %424 = getelementptr float, ptr %68, <8 x i64> %420
  %wide.masked.gather292 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %421, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather293 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %422, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather294 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %423, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather295 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %424, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %425 = add <8 x i32> %broadcast.splat291, %232
  %426 = add <8 x i32> %broadcast.splat291, %.reass512
  %427 = add <8 x i32> %broadcast.splat291, %.reass514
  %428 = add <8 x i32> %broadcast.splat291, %.reass516
  %429 = sext <8 x i32> %425 to <8 x i64>
  %430 = sext <8 x i32> %426 to <8 x i64>
  %431 = sext <8 x i32> %427 to <8 x i64>
  %432 = sext <8 x i32> %428 to <8 x i64>
  %433 = getelementptr float, ptr %68, <8 x i64> %429
  %434 = getelementptr float, ptr %68, <8 x i64> %430
  %435 = getelementptr float, ptr %68, <8 x i64> %431
  %436 = getelementptr float, ptr %68, <8 x i64> %432
  %wide.masked.gather296 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %433, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather297 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %434, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather298 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %435, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather299 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %436, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %437 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather272, %wide.masked.gather282
  %438 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather273, %wide.masked.gather283
  %439 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather274, %wide.masked.gather284
  %440 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather275, %wide.masked.gather285
  %441 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather276, %wide.masked.gather286
  %442 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather277, %wide.masked.gather287
  %443 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather278, %wide.masked.gather288
  %444 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather279, %wide.masked.gather289
  %445 = fadd reassoc ninf nsz <8 x float> %437, %wide.masked.gather292
  %446 = fadd reassoc ninf nsz <8 x float> %438, %wide.masked.gather293
  %447 = fadd reassoc ninf nsz <8 x float> %439, %wide.masked.gather294
  %448 = fadd reassoc ninf nsz <8 x float> %440, %wide.masked.gather295
  %449 = fadd reassoc ninf nsz <8 x float> %441, %wide.masked.gather296
  %450 = fadd reassoc ninf nsz <8 x float> %442, %wide.masked.gather297
  %451 = fadd reassoc ninf nsz <8 x float> %443, %wide.masked.gather298
  %452 = fadd reassoc ninf nsz <8 x float> %444, %wide.masked.gather299
  %453 = fsub reassoc ninf nsz <8 x float> %445, %449
  %454 = fsub reassoc ninf nsz <8 x float> %446, %450
  %455 = fsub reassoc ninf nsz <8 x float> %447, %451
  %456 = fsub reassoc ninf nsz <8 x float> %448, %452
  %457 = fmul reassoc ninf nsz <8 x float> %453, splat (float 0x3FD5555560000000)
  %458 = fmul reassoc ninf nsz <8 x float> %454, splat (float 0x3FD5555560000000)
  %459 = fmul reassoc ninf nsz <8 x float> %455, splat (float 0x3FD5555560000000)
  %460 = fmul reassoc ninf nsz <8 x float> %456, splat (float 0x3FD5555560000000)
  %461 = add <8 x i32> %broadcast.splat291, %183
  %462 = add <8 x i32> %broadcast.splat291, %.reass
  %463 = add <8 x i32> %broadcast.splat291, %.reass508
  %464 = add <8 x i32> %broadcast.splat291, %.reass510
  %465 = sext <8 x i32> %461 to <8 x i64>
  %466 = sext <8 x i32> %462 to <8 x i64>
  %467 = sext <8 x i32> %463 to <8 x i64>
  %468 = sext <8 x i32> %464 to <8 x i64>
  %469 = getelementptr float, ptr %68, <8 x i64> %465
  %470 = getelementptr float, ptr %68, <8 x i64> %466
  %471 = getelementptr float, ptr %68, <8 x i64> %467
  %472 = getelementptr float, ptr %68, <8 x i64> %468
  %wide.masked.gather300 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %469, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather301 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %470, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather302 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %471, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather303 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %472, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %473 = add <8 x i32> %broadcast.splat281, %183
  %474 = add <8 x i32> %broadcast.splat281, %.reass
  %475 = add <8 x i32> %broadcast.splat281, %.reass508
  %476 = add <8 x i32> %broadcast.splat281, %.reass510
  %477 = sext <8 x i32> %473 to <8 x i64>
  %478 = sext <8 x i32> %474 to <8 x i64>
  %479 = sext <8 x i32> %475 to <8 x i64>
  %480 = sext <8 x i32> %476 to <8 x i64>
  %481 = getelementptr float, ptr %68, <8 x i64> %477
  %482 = getelementptr float, ptr %68, <8 x i64> %478
  %483 = getelementptr float, ptr %68, <8 x i64> %479
  %484 = getelementptr float, ptr %68, <8 x i64> %480
  %wide.masked.gather304 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %481, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather305 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %482, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather306 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %483, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %wide.masked.gather307 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %484, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %485 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather282, %wide.masked.gather286
  %486 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather283, %wide.masked.gather287
  %487 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather284, %wide.masked.gather288
  %488 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather285, %wide.masked.gather289
  %489 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather292, %485
  %490 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather293, %486
  %491 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather294, %487
  %492 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather295, %488
  %493 = fadd reassoc ninf nsz <8 x float> %489, %wide.masked.gather296
  %494 = fadd reassoc ninf nsz <8 x float> %490, %wide.masked.gather297
  %495 = fadd reassoc ninf nsz <8 x float> %491, %wide.masked.gather298
  %496 = fadd reassoc ninf nsz <8 x float> %492, %wide.masked.gather299
  %497 = fadd reassoc ninf nsz <8 x float> %493, %wide.masked.gather300
  %498 = fadd reassoc ninf nsz <8 x float> %494, %wide.masked.gather301
  %499 = fadd reassoc ninf nsz <8 x float> %495, %wide.masked.gather302
  %500 = fadd reassoc ninf nsz <8 x float> %496, %wide.masked.gather303
  %501 = fsub reassoc ninf nsz <8 x float> %497, %wide.masked.gather304
  %502 = fsub reassoc ninf nsz <8 x float> %498, %wide.masked.gather305
  %503 = fsub reassoc ninf nsz <8 x float> %499, %wide.masked.gather306
  %504 = fsub reassoc ninf nsz <8 x float> %500, %wide.masked.gather307
  %505 = fmul reassoc ninf nsz <8 x float> %501, splat (float 0x3FD5555560000000)
  %506 = fmul reassoc ninf nsz <8 x float> %502, splat (float 0x3FD5555560000000)
  %507 = fmul reassoc ninf nsz <8 x float> %503, splat (float 0x3FD5555560000000)
  %508 = fmul reassoc ninf nsz <8 x float> %504, splat (float 0x3FD5555560000000)
  %509 = fmul reassoc ninf nsz <8 x float> %313, %313
  %510 = fmul reassoc ninf nsz <8 x float> %314, %314
  %511 = fmul reassoc ninf nsz <8 x float> %315, %315
  %512 = fmul reassoc ninf nsz <8 x float> %316, %316
  %513 = fmul reassoc ninf nsz <8 x float> %361, %361
  %514 = fmul reassoc ninf nsz <8 x float> %362, %362
  %515 = fmul reassoc ninf nsz <8 x float> %363, %363
  %516 = fmul reassoc ninf nsz <8 x float> %364, %364
  %517 = fadd reassoc ninf nsz <8 x float> %513, %509
  %518 = fadd reassoc ninf nsz <8 x float> %514, %510
  %519 = fadd reassoc ninf nsz <8 x float> %515, %511
  %520 = fadd reassoc ninf nsz <8 x float> %516, %512
  %521 = fmul reassoc ninf nsz <8 x float> %457, %457
  %522 = fmul reassoc ninf nsz <8 x float> %458, %458
  %523 = fmul reassoc ninf nsz <8 x float> %459, %459
  %524 = fmul reassoc ninf nsz <8 x float> %460, %460
  %525 = fmul reassoc ninf nsz <8 x float> %505, %505
  %526 = fmul reassoc ninf nsz <8 x float> %506, %506
  %527 = fmul reassoc ninf nsz <8 x float> %507, %507
  %528 = fmul reassoc ninf nsz <8 x float> %508, %508
  %529 = fadd reassoc ninf nsz <8 x float> %525, %521
  %530 = fadd reassoc ninf nsz <8 x float> %526, %522
  %531 = fadd reassoc ninf nsz <8 x float> %527, %523
  %532 = fadd reassoc ninf nsz <8 x float> %528, %524
  %533 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %517, <8 x float> %529)
  %534 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %518, <8 x float> %530)
  %535 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %519, <8 x float> %531)
  %536 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %520, <8 x float> %532)
  %537 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather230, splat (float -2.000000e+00)
  %538 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather231, splat (float -2.000000e+00)
  %539 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather232, splat (float -2.000000e+00)
  %540 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather233, splat (float -2.000000e+00)
  %541 = fadd reassoc ninf nsz <8 x float> %537, splat (float 3.000000e+00)
  %542 = fadd reassoc ninf nsz <8 x float> %538, splat (float 3.000000e+00)
  %543 = fadd reassoc ninf nsz <8 x float> %539, splat (float 3.000000e+00)
  %544 = fadd reassoc ninf nsz <8 x float> %540, splat (float 3.000000e+00)
  %545 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %541, <8 x float> splat (float 3.000000e+00))
  %546 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %542, <8 x float> splat (float 3.000000e+00))
  %547 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %543, <8 x float> splat (float 3.000000e+00))
  %548 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %544, <8 x float> splat (float 3.000000e+00))
  %549 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %545, <8 x float> splat (float 1.000000e+00))
  %550 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %546, <8 x float> splat (float 1.000000e+00))
  %551 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %547, <8 x float> splat (float 1.000000e+00))
  %552 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %548, <8 x float> splat (float 1.000000e+00))
  %553 = fmul reassoc ninf nsz <8 x float> %549, %broadcast.splat309
  %554 = fmul reassoc ninf nsz <8 x float> %550, %broadcast.splat309
  %555 = fmul reassoc ninf nsz <8 x float> %551, %broadcast.splat309
  %556 = fmul reassoc ninf nsz <8 x float> %552, %broadcast.splat309
  %557 = fmul reassoc ninf nsz <8 x float> %549, %549
  %558 = fmul reassoc ninf nsz <8 x float> %550, %550
  %559 = fmul reassoc ninf nsz <8 x float> %551, %551
  %560 = fmul reassoc ninf nsz <8 x float> %552, %552
  %561 = fmul reassoc ninf nsz <8 x float> %557, %broadcast.splat311
  %562 = fmul reassoc ninf nsz <8 x float> %558, %broadcast.splat311
  %563 = fmul reassoc ninf nsz <8 x float> %559, %broadcast.splat311
  %564 = fmul reassoc ninf nsz <8 x float> %560, %broadcast.splat311
  %565 = fcmp reassoc ninf nsz olt <8 x float> %533, %561
  %566 = fcmp reassoc ninf nsz olt <8 x float> %534, %562
  %567 = fcmp reassoc ninf nsz olt <8 x float> %535, %563
  %568 = fcmp reassoc ninf nsz olt <8 x float> %536, %564
  %569 = xor <8 x i1> %565, splat (i1 true)
  %570 = xor <8 x i1> %566, splat (i1 true)
  %571 = xor <8 x i1> %567, splat (i1 true)
  %572 = xor <8 x i1> %568, splat (i1 true)
  %573 = select <8 x i1> %broadcast.splat, <8 x i1> %569, <8 x i1> zeroinitializer
  %574 = select <8 x i1> %broadcast.splat, <8 x i1> %570, <8 x i1> zeroinitializer
  %575 = select <8 x i1> %broadcast.splat, <8 x i1> %571, <8 x i1> zeroinitializer
  %576 = select <8 x i1> %broadcast.splat, <8 x i1> %572, <8 x i1> zeroinitializer
  %577 = fcmp reassoc ninf nsz olt <8 x float> %212, %553
  %578 = fcmp reassoc ninf nsz olt <8 x float> %213, %554
  %579 = fcmp reassoc ninf nsz olt <8 x float> %214, %555
  %580 = fcmp reassoc ninf nsz olt <8 x float> %215, %556
  %581 = xor <8 x i1> %577, splat (i1 true)
  %582 = xor <8 x i1> %578, splat (i1 true)
  %583 = xor <8 x i1> %579, splat (i1 true)
  %584 = xor <8 x i1> %580, splat (i1 true)
  %585 = select <8 x i1> %573, <8 x i1> %581, <8 x i1> zeroinitializer
  %586 = select <8 x i1> %574, <8 x i1> %582, <8 x i1> zeroinitializer
  %587 = select <8 x i1> %575, <8 x i1> %583, <8 x i1> zeroinitializer
  %588 = select <8 x i1> %576, <8 x i1> %584, <8 x i1> zeroinitializer
  %589 = fmul reassoc ninf nsz <8 x float> %553, splat (float 4.000000e+00)
  %590 = fmul reassoc ninf nsz <8 x float> %554, splat (float 4.000000e+00)
  %591 = fmul reassoc ninf nsz <8 x float> %555, splat (float 4.000000e+00)
  %592 = fmul reassoc ninf nsz <8 x float> %556, splat (float 4.000000e+00)
  %593 = fdiv reassoc ninf nsz <8 x float> %212, %589
  %594 = fdiv reassoc ninf nsz <8 x float> %213, %590
  %595 = fdiv reassoc ninf nsz <8 x float> %214, %591
  %596 = fdiv reassoc ninf nsz <8 x float> %215, %592
  %597 = fcmp reassoc ninf nsz ogt <8 x float> %593, splat (float 1.000000e+00)
  %598 = fcmp reassoc ninf nsz ogt <8 x float> %594, splat (float 1.000000e+00)
  %599 = fcmp reassoc ninf nsz ogt <8 x float> %595, splat (float 1.000000e+00)
  %600 = fcmp reassoc ninf nsz ogt <8 x float> %596, splat (float 1.000000e+00)
  %601 = select <8 x i1> %597, <8 x float> splat (float 1.000000e+00), <8 x float> %593
  %602 = select <8 x i1> %598, <8 x float> splat (float 1.000000e+00), <8 x float> %594
  %603 = select <8 x i1> %599, <8 x float> splat (float 1.000000e+00), <8 x float> %595
  %604 = select <8 x i1> %600, <8 x float> splat (float 1.000000e+00), <8 x float> %596
  %605 = fmul reassoc ninf nsz <8 x float> %601, splat (float 0x3FD99999A0000000)
  %606 = fmul reassoc ninf nsz <8 x float> %602, splat (float 0x3FD99999A0000000)
  %607 = fmul reassoc ninf nsz <8 x float> %603, splat (float 0x3FD99999A0000000)
  %608 = fmul reassoc ninf nsz <8 x float> %604, splat (float 0x3FD99999A0000000)
  %609 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %605
  %610 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %606
  %611 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %607
  %612 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %608
  %613 = select <8 x i1> %573, <8 x i1> %577, <8 x i1> zeroinitializer
  %614 = select <8 x i1> %574, <8 x i1> %578, <8 x i1> zeroinitializer
  %615 = select <8 x i1> %575, <8 x i1> %579, <8 x i1> zeroinitializer
  %616 = select <8 x i1> %576, <8 x i1> %580, <8 x i1> zeroinitializer
  %617 = fmul reassoc ninf nsz <8 x float> %212, splat (float 0x3FC3333340000000)
  %618 = fmul reassoc ninf nsz <8 x float> %213, splat (float 0x3FC3333340000000)
  %619 = fmul reassoc ninf nsz <8 x float> %214, splat (float 0x3FC3333340000000)
  %620 = fmul reassoc ninf nsz <8 x float> %215, splat (float 0x3FC3333340000000)
  %621 = fdiv reassoc ninf nsz <8 x float> %617, %553
  %622 = fdiv reassoc ninf nsz <8 x float> %618, %554
  %623 = fdiv reassoc ninf nsz <8 x float> %619, %555
  %624 = fdiv reassoc ninf nsz <8 x float> %620, %556
  %625 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %621
  %626 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %622
  %627 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %623
  %628 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %624
  %629 = select <8 x i1> %broadcast.splat, <8 x i1> %565, <8 x i1> zeroinitializer
  %630 = select <8 x i1> %broadcast.splat, <8 x i1> %566, <8 x i1> zeroinitializer
  %631 = select <8 x i1> %broadcast.splat, <8 x i1> %567, <8 x i1> zeroinitializer
  %632 = select <8 x i1> %broadcast.splat, <8 x i1> %568, <8 x i1> zeroinitializer
  %633 = fmul reassoc ninf nsz <8 x float> %553, splat (float 1.500000e+00)
  %634 = fmul reassoc ninf nsz <8 x float> %554, splat (float 1.500000e+00)
  %635 = fmul reassoc ninf nsz <8 x float> %555, splat (float 1.500000e+00)
  %636 = fmul reassoc ninf nsz <8 x float> %556, splat (float 1.500000e+00)
  %637 = fcmp reassoc ninf nsz uge <8 x float> %212, %633
  %638 = fcmp reassoc ninf nsz uge <8 x float> %213, %634
  %639 = fcmp reassoc ninf nsz uge <8 x float> %214, %635
  %640 = fcmp reassoc ninf nsz uge <8 x float> %215, %636
  %641 = select <8 x i1> %629, <8 x i1> %637, <8 x i1> zeroinitializer
  %642 = select <8 x i1> %630, <8 x i1> %638, <8 x i1> zeroinitializer
  %643 = select <8 x i1> %631, <8 x i1> %639, <8 x i1> zeroinitializer
  %644 = select <8 x i1> %632, <8 x i1> %640, <8 x i1> zeroinitializer
  %645 = fsub reassoc ninf nsz <8 x float> %212, %633
  %646 = fsub reassoc ninf nsz <8 x float> %213, %634
  %647 = fsub reassoc ninf nsz <8 x float> %214, %635
  %648 = fsub reassoc ninf nsz <8 x float> %215, %636
  %649 = fdiv reassoc ninf nsz <8 x float> %645, %633
  %650 = fdiv reassoc ninf nsz <8 x float> %646, %634
  %651 = fdiv reassoc ninf nsz <8 x float> %647, %635
  %652 = fdiv reassoc ninf nsz <8 x float> %648, %636
  %653 = fcmp reassoc ninf nsz ogt <8 x float> %649, splat (float 1.000000e+00)
  %654 = fcmp reassoc ninf nsz ogt <8 x float> %650, splat (float 1.000000e+00)
  %655 = fcmp reassoc ninf nsz ogt <8 x float> %651, splat (float 1.000000e+00)
  %656 = fcmp reassoc ninf nsz ogt <8 x float> %652, splat (float 1.000000e+00)
  %657 = select <8 x i1> %653, <8 x float> splat (float 1.000000e+00), <8 x float> %649
  %658 = select <8 x i1> %654, <8 x float> splat (float 1.000000e+00), <8 x float> %650
  %659 = select <8 x i1> %655, <8 x float> splat (float 1.000000e+00), <8 x float> %651
  %660 = select <8 x i1> %656, <8 x float> splat (float 1.000000e+00), <8 x float> %652
  %661 = fmul reassoc ninf nsz <8 x float> %657, splat (float 0x3FC99999A0000000)
  %662 = fmul reassoc ninf nsz <8 x float> %658, splat (float 0x3FC99999A0000000)
  %663 = fmul reassoc ninf nsz <8 x float> %659, splat (float 0x3FC99999A0000000)
  %664 = fmul reassoc ninf nsz <8 x float> %660, splat (float 0x3FC99999A0000000)
  %665 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %661
  %666 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %662
  %667 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %663
  %668 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %664
  %669 = fmul reassoc ninf nsz <8 x float> %212, splat (float 0x3FEE666660000000)
  %670 = fmul reassoc ninf nsz <8 x float> %213, splat (float 0x3FEE666660000000)
  %671 = fmul reassoc ninf nsz <8 x float> %214, splat (float 0x3FEE666660000000)
  %672 = fmul reassoc ninf nsz <8 x float> %215, splat (float 0x3FEE666660000000)
  %673 = fdiv reassoc ninf nsz <8 x float> %669, %633
  %674 = fdiv reassoc ninf nsz <8 x float> %670, %634
  %675 = fdiv reassoc ninf nsz <8 x float> %671, %635
  %676 = fdiv reassoc ninf nsz <8 x float> %672, %636
  %677 = fadd reassoc ninf nsz <8 x float> %673, splat (float 0x3FA99999A0000000)
  %678 = fadd reassoc ninf nsz <8 x float> %674, splat (float 0x3FA99999A0000000)
  %679 = fadd reassoc ninf nsz <8 x float> %675, splat (float 0x3FA99999A0000000)
  %680 = fadd reassoc ninf nsz <8 x float> %676, splat (float 0x3FA99999A0000000)
  %681 = or <8 x i1> %629, %613
  %682 = or <8 x i1> %630, %614
  %683 = or <8 x i1> %631, %615
  %684 = or <8 x i1> %632, %616
  %685 = or <8 x i1> %681, %585
  %686 = or <8 x i1> %682, %586
  %687 = or <8 x i1> %683, %587
  %688 = or <8 x i1> %684, %588
  %689 = or <8 x i1> %685, %107
  %690 = or <8 x i1> %686, %107
  %691 = or <8 x i1> %687, %107
  %692 = or <8 x i1> %688, %107
  %predphi = select <8 x i1> %641, <8 x float> %665, <8 x float> %677
  %predphi312 = select <8 x i1> %613, <8 x float> %625, <8 x float> %predphi
  %predphi313 = select <8 x i1> %585, <8 x float> %609, <8 x float> %predphi312
  %predphi314 = select <8 x i1> %broadcast.splat, <8 x float> %predphi313, <8 x float> splat (float 1.000000e+00)
  %predphi315 = select <8 x i1> %642, <8 x float> %666, <8 x float> %678
  %predphi316 = select <8 x i1> %614, <8 x float> %626, <8 x float> %predphi315
  %predphi317 = select <8 x i1> %586, <8 x float> %610, <8 x float> %predphi316
  %predphi318 = select <8 x i1> %broadcast.splat, <8 x float> %predphi317, <8 x float> splat (float 1.000000e+00)
  %predphi319 = select <8 x i1> %643, <8 x float> %667, <8 x float> %679
  %predphi320 = select <8 x i1> %615, <8 x float> %627, <8 x float> %predphi319
  %predphi321 = select <8 x i1> %587, <8 x float> %611, <8 x float> %predphi320
  %predphi322 = select <8 x i1> %broadcast.splat, <8 x float> %predphi321, <8 x float> splat (float 1.000000e+00)
  %predphi323 = select <8 x i1> %644, <8 x float> %668, <8 x float> %680
  %predphi324 = select <8 x i1> %616, <8 x float> %628, <8 x float> %predphi323
  %predphi325 = select <8 x i1> %588, <8 x float> %612, <8 x float> %predphi324
  %predphi326 = select <8 x i1> %broadcast.splat, <8 x float> %predphi325, <8 x float> splat (float 1.000000e+00)
  %693 = fcmp reassoc ninf nsz ogt <8 x float> %533, splat (float 0x3EB0C6F7A0000000)
  %694 = fcmp reassoc ninf nsz ogt <8 x float> %534, splat (float 0x3EB0C6F7A0000000)
  %695 = fcmp reassoc ninf nsz ogt <8 x float> %535, splat (float 0x3EB0C6F7A0000000)
  %696 = fcmp reassoc ninf nsz ogt <8 x float> %536, splat (float 0x3EB0C6F7A0000000)
  %697 = select <8 x i1> %689, <8 x i1> %693, <8 x i1> zeroinitializer
  %698 = select <8 x i1> %690, <8 x i1> %694, <8 x i1> zeroinitializer
  %699 = select <8 x i1> %691, <8 x i1> %695, <8 x i1> zeroinitializer
  %700 = select <8 x i1> %692, <8 x i1> %696, <8 x i1> zeroinitializer
  %701 = fcmp reassoc ninf nsz ogt <8 x float> %517, splat (float 0x3EB0C6F7A0000000)
  %702 = fcmp reassoc ninf nsz ogt <8 x float> %518, splat (float 0x3EB0C6F7A0000000)
  %703 = fcmp reassoc ninf nsz ogt <8 x float> %519, splat (float 0x3EB0C6F7A0000000)
  %704 = fcmp reassoc ninf nsz ogt <8 x float> %520, splat (float 0x3EB0C6F7A0000000)
  %705 = fcmp reassoc ninf nsz ogt <8 x float> %529, splat (float 0x3EB0C6F7A0000000)
  %706 = fcmp reassoc ninf nsz ogt <8 x float> %530, splat (float 0x3EB0C6F7A0000000)
  %707 = fcmp reassoc ninf nsz ogt <8 x float> %531, splat (float 0x3EB0C6F7A0000000)
  %708 = fcmp reassoc ninf nsz ogt <8 x float> %532, splat (float 0x3EB0C6F7A0000000)
  %709 = select <8 x i1> %701, <8 x i1> %705, <8 x i1> zeroinitializer
  %710 = select <8 x i1> %702, <8 x i1> %706, <8 x i1> zeroinitializer
  %711 = select <8 x i1> %703, <8 x i1> %707, <8 x i1> zeroinitializer
  %712 = select <8 x i1> %704, <8 x i1> %708, <8 x i1> zeroinitializer
  %713 = select <8 x i1> %697, <8 x i1> %709, <8 x i1> zeroinitializer
  %714 = select <8 x i1> %698, <8 x i1> %710, <8 x i1> zeroinitializer
  %715 = select <8 x i1> %699, <8 x i1> %711, <8 x i1> zeroinitializer
  %716 = select <8 x i1> %700, <8 x i1> %712, <8 x i1> zeroinitializer
  %717 = fmul reassoc ninf nsz <8 x float> %457, %313
  %718 = fmul reassoc ninf nsz <8 x float> %458, %314
  %719 = fmul reassoc ninf nsz <8 x float> %459, %315
  %720 = fmul reassoc ninf nsz <8 x float> %460, %316
  %721 = fmul reassoc ninf nsz <8 x float> %505, %361
  %722 = fmul reassoc ninf nsz <8 x float> %506, %362
  %723 = fmul reassoc ninf nsz <8 x float> %507, %363
  %724 = fmul reassoc ninf nsz <8 x float> %508, %364
  %725 = fadd reassoc ninf nsz <8 x float> %721, %717
  %726 = fadd reassoc ninf nsz <8 x float> %722, %718
  %727 = fadd reassoc ninf nsz <8 x float> %723, %719
  %728 = fadd reassoc ninf nsz <8 x float> %724, %720
  %729 = fmul reassoc ninf nsz <8 x float> %529, %517
  %730 = fmul reassoc ninf nsz <8 x float> %530, %518
  %731 = fmul reassoc ninf nsz <8 x float> %531, %519
  %732 = fmul reassoc ninf nsz <8 x float> %532, %520
  %733 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %729)
  %734 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %730)
  %735 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %731)
  %736 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %732)
  %737 = fdiv reassoc ninf nsz <8 x float> %725, %733
  %738 = fdiv reassoc ninf nsz <8 x float> %726, %734
  %739 = fdiv reassoc ninf nsz <8 x float> %727, %735
  %740 = fdiv reassoc ninf nsz <8 x float> %728, %736
  %741 = fcmp reassoc ninf nsz ule <8 x float> %533, %561
  %742 = fcmp reassoc ninf nsz ule <8 x float> %534, %562
  %743 = fcmp reassoc ninf nsz ule <8 x float> %535, %563
  %744 = fcmp reassoc ninf nsz ule <8 x float> %536, %564
  %745 = fcmp reassoc ninf nsz uge <8 x float> %737, splat (float 0x3FC99999A0000000)
  %746 = fcmp reassoc ninf nsz uge <8 x float> %738, splat (float 0x3FC99999A0000000)
  %747 = fcmp reassoc ninf nsz uge <8 x float> %739, splat (float 0x3FC99999A0000000)
  %748 = fcmp reassoc ninf nsz uge <8 x float> %740, splat (float 0x3FC99999A0000000)
  %.not453 = select <8 x i1> %741, <8 x i1> splat (i1 true), <8 x i1> %745
  %.not456 = select <8 x i1> %742, <8 x i1> splat (i1 true), <8 x i1> %746
  %.not459 = select <8 x i1> %743, <8 x i1> splat (i1 true), <8 x i1> %747
  %.not462 = select <8 x i1> %744, <8 x i1> splat (i1 true), <8 x i1> %748
  %749 = select <8 x i1> %713, <8 x i1> %.not453, <8 x i1> zeroinitializer
  %750 = select <8 x i1> %714, <8 x i1> %.not456, <8 x i1> zeroinitializer
  %751 = select <8 x i1> %715, <8 x i1> %.not459, <8 x i1> zeroinitializer
  %752 = select <8 x i1> %716, <8 x i1> %.not462, <8 x i1> zeroinitializer
  %753 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %737, <8 x float> zeroinitializer)
  %754 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %738, <8 x float> zeroinitializer)
  %755 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %739, <8 x float> zeroinitializer)
  %756 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %740, <8 x float> zeroinitializer)
  %757 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %533)
  %758 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %534)
  %759 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %535)
  %760 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %536)
  %761 = fmul reassoc ninf nsz <8 x float> %757, splat (float 2.025000e+02)
  %762 = fmul reassoc ninf nsz <8 x float> %758, splat (float 2.025000e+02)
  %763 = fmul reassoc ninf nsz <8 x float> %759, splat (float 2.025000e+02)
  %764 = fmul reassoc ninf nsz <8 x float> %760, splat (float 2.025000e+02)
  %765 = fmul reassoc ninf nsz <8 x float> %761, %753
  %.fr = freeze <8 x float> %765
  %766 = fmul reassoc ninf nsz <8 x float> %762, %754
  %.fr463 = freeze <8 x float> %766
  %767 = fmul reassoc ninf nsz <8 x float> %763, %755
  %.fr464 = freeze <8 x float> %767
  %768 = fmul reassoc ninf nsz <8 x float> %764, %756
  %.fr465 = freeze <8 x float> %768
  %769 = fcmp reassoc nsz ogt <8 x float> %.fr, splat (float 3.000000e+00)
  %770 = fcmp reassoc nsz ogt <8 x float> %.fr463, splat (float 3.000000e+00)
  %771 = fcmp reassoc nsz ogt <8 x float> %.fr464, splat (float 3.000000e+00)
  %772 = fcmp reassoc nsz ogt <8 x float> %.fr465, splat (float 3.000000e+00)
  %773 = xor <8 x i1> %769, splat (i1 true)
  %774 = xor <8 x i1> %770, splat (i1 true)
  %775 = xor <8 x i1> %771, splat (i1 true)
  %776 = xor <8 x i1> %772, splat (i1 true)
  %777 = and <8 x i1> %749, %773
  %778 = and <8 x i1> %750, %774
  %779 = and <8 x i1> %751, %775
  %780 = and <8 x i1> %752, %776
  %781 = fcmp reassoc nsz olt <8 x float> %.fr, splat (float -3.000000e+00)
  %782 = fcmp reassoc nsz olt <8 x float> %.fr463, splat (float -3.000000e+00)
  %783 = fcmp reassoc nsz olt <8 x float> %.fr464, splat (float -3.000000e+00)
  %784 = fcmp reassoc nsz olt <8 x float> %.fr465, splat (float -3.000000e+00)
  %785 = xor <8 x i1> %781, splat (i1 true)
  %786 = xor <8 x i1> %782, splat (i1 true)
  %787 = xor <8 x i1> %783, splat (i1 true)
  %788 = xor <8 x i1> %784, splat (i1 true)
  %789 = and <8 x i1> %777, %785
  %790 = and <8 x i1> %778, %786
  %791 = and <8 x i1> %779, %787
  %792 = and <8 x i1> %780, %788
  %793 = fmul reassoc ninf nsz <8 x float> %.fr, %.fr
  %794 = fmul reassoc ninf nsz <8 x float> %.fr463, %.fr463
  %795 = fmul reassoc ninf nsz <8 x float> %.fr464, %.fr464
  %796 = fmul reassoc ninf nsz <8 x float> %.fr465, %.fr465
  %797 = fadd reassoc ninf nsz <8 x float> %793, splat (float 2.700000e+01)
  %798 = fadd reassoc ninf nsz <8 x float> %794, splat (float 2.700000e+01)
  %799 = fadd reassoc ninf nsz <8 x float> %795, splat (float 2.700000e+01)
  %800 = fadd reassoc ninf nsz <8 x float> %796, splat (float 2.700000e+01)
  %801 = fmul reassoc ninf nsz <8 x float> %797, %.fr
  %802 = fmul reassoc ninf nsz <8 x float> %798, %.fr463
  %803 = fmul reassoc ninf nsz <8 x float> %799, %.fr464
  %804 = fmul reassoc ninf nsz <8 x float> %800, %.fr465
  %805 = fmul reassoc ninf nsz <8 x float> %793, splat (float 9.000000e+00)
  %806 = fmul reassoc ninf nsz <8 x float> %794, splat (float 9.000000e+00)
  %807 = fmul reassoc ninf nsz <8 x float> %795, splat (float 9.000000e+00)
  %808 = fmul reassoc ninf nsz <8 x float> %796, splat (float 9.000000e+00)
  %809 = fadd reassoc ninf nsz <8 x float> %805, splat (float 2.700000e+01)
  %810 = fadd reassoc ninf nsz <8 x float> %806, splat (float 2.700000e+01)
  %811 = fadd reassoc ninf nsz <8 x float> %807, splat (float 2.700000e+01)
  %812 = fadd reassoc ninf nsz <8 x float> %808, splat (float 2.700000e+01)
  %813 = fdiv reassoc ninf nsz <8 x float> %801, %809
  %814 = fdiv reassoc ninf nsz <8 x float> %802, %810
  %815 = fdiv reassoc ninf nsz <8 x float> %803, %811
  %816 = fdiv reassoc ninf nsz <8 x float> %804, %812
  %817 = fadd reassoc ninf nsz <8 x float> %813, splat (float 1.000000e+00)
  %818 = fadd reassoc ninf nsz <8 x float> %814, splat (float 1.000000e+00)
  %819 = fadd reassoc ninf nsz <8 x float> %815, splat (float 1.000000e+00)
  %820 = fadd reassoc ninf nsz <8 x float> %816, splat (float 1.000000e+00)
  %821 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %737
  %822 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %738
  %823 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %739
  %824 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %740
  %825 = fmul reassoc ninf nsz <8 x float> %821, %212
  %826 = fmul reassoc ninf nsz <8 x float> %822, %213
  %827 = fmul reassoc ninf nsz <8 x float> %823, %214
  %828 = fmul reassoc ninf nsz <8 x float> %824, %215
  %829 = and <8 x i1> %777, %781
  %830 = and <8 x i1> %778, %782
  %831 = and <8 x i1> %779, %783
  %832 = and <8 x i1> %780, %784
  %833 = and <8 x i1> %749, %769
  %834 = and <8 x i1> %750, %770
  %835 = and <8 x i1> %751, %771
  %836 = and <8 x i1> %752, %772
  %837 = xor <8 x i1> %709, splat (i1 true)
  %838 = xor <8 x i1> %710, splat (i1 true)
  %839 = xor <8 x i1> %711, splat (i1 true)
  %840 = xor <8 x i1> %712, splat (i1 true)
  %841 = select <8 x i1> %697, <8 x i1> %837, <8 x i1> zeroinitializer
  %842 = select <8 x i1> %698, <8 x i1> %838, <8 x i1> zeroinitializer
  %843 = select <8 x i1> %699, <8 x i1> %839, <8 x i1> zeroinitializer
  %844 = select <8 x i1> %700, <8 x i1> %840, <8 x i1> zeroinitializer
  %845 = xor <8 x i1> %693, splat (i1 true)
  %846 = xor <8 x i1> %694, splat (i1 true)
  %847 = xor <8 x i1> %695, splat (i1 true)
  %848 = xor <8 x i1> %696, splat (i1 true)
  %849 = select <8 x i1> %689, <8 x i1> %845, <8 x i1> zeroinitializer
  %850 = select <8 x i1> %690, <8 x i1> %846, <8 x i1> zeroinitializer
  %851 = select <8 x i1> %691, <8 x i1> %847, <8 x i1> zeroinitializer
  %852 = select <8 x i1> %692, <8 x i1> %848, <8 x i1> zeroinitializer
  %853 = select <8 x i1> %749, <8 x i1> splat (i1 true), <8 x i1> %849
  %854 = select <8 x i1> %853, <8 x i1> splat (i1 true), <8 x i1> %841
  %predphi331 = select <8 x i1> %854, <8 x float> %212, <8 x float> %825
  %855 = select <8 x i1> %750, <8 x i1> splat (i1 true), <8 x i1> %850
  %856 = select <8 x i1> %855, <8 x i1> splat (i1 true), <8 x i1> %842
  %predphi336 = select <8 x i1> %856, <8 x float> %213, <8 x float> %826
  %857 = select <8 x i1> %751, <8 x i1> splat (i1 true), <8 x i1> %851
  %858 = select <8 x i1> %857, <8 x i1> splat (i1 true), <8 x i1> %843
  %predphi341 = select <8 x i1> %858, <8 x float> %214, <8 x float> %827
  %859 = select <8 x i1> %752, <8 x i1> splat (i1 true), <8 x i1> %852
  %860 = select <8 x i1> %859, <8 x i1> splat (i1 true), <8 x i1> %844
  %predphi346 = select <8 x i1> %860, <8 x float> %215, <8 x float> %828
  %predphi349 = select <8 x i1> %833, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi350 = select <8 x i1> %789, <8 x float> %817, <8 x float> %predphi349
  %predphi351 = select <8 x i1> %829, <8 x float> zeroinitializer, <8 x float> %predphi350
  %predphi354 = select <8 x i1> %834, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi355 = select <8 x i1> %790, <8 x float> %818, <8 x float> %predphi354
  %predphi356 = select <8 x i1> %830, <8 x float> zeroinitializer, <8 x float> %predphi355
  %predphi359 = select <8 x i1> %835, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi360 = select <8 x i1> %791, <8 x float> %819, <8 x float> %predphi359
  %predphi361 = select <8 x i1> %831, <8 x float> zeroinitializer, <8 x float> %predphi360
  %predphi364 = select <8 x i1> %836, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi365 = select <8 x i1> %792, <8 x float> %820, <8 x float> %predphi364
  %predphi366 = select <8 x i1> %832, <8 x float> zeroinitializer, <8 x float> %predphi365
  %861 = fmul reassoc ninf nsz <8 x float> %predphi351, %predphi314
  %862 = fmul reassoc ninf nsz <8 x float> %predphi356, %predphi318
  %863 = fmul reassoc ninf nsz <8 x float> %predphi361, %predphi322
  %864 = fmul reassoc ninf nsz <8 x float> %predphi366, %predphi326
  %865 = fmul reassoc ninf nsz <8 x float> %861, %predphi331
  %866 = fmul reassoc ninf nsz <8 x float> %862, %predphi336
  %867 = fmul reassoc ninf nsz <8 x float> %863, %predphi341
  %868 = fmul reassoc ninf nsz <8 x float> %864, %predphi346
  %869 = fadd reassoc ninf nsz <8 x float> %865, %vec.phi217
  %870 = fadd reassoc ninf nsz <8 x float> %866, %vec.phi218
  %871 = fadd reassoc ninf nsz <8 x float> %867, %vec.phi219
  %872 = fadd reassoc ninf nsz <8 x float> %868, %vec.phi220
  %873 = fadd reassoc ninf nsz <8 x float> %861, %vec.phi213
  %874 = fadd reassoc ninf nsz <8 x float> %862, %vec.phi214
  %875 = fadd reassoc ninf nsz <8 x float> %863, %vec.phi215
  %876 = fadd reassoc ninf nsz <8 x float> %864, %vec.phi216
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 32)
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %877 = icmp eq i64 %lsr.iv.next, 0
  br i1 %877, label %middle.block202, label %vector.body211, !llvm.loop !11

middle.block202:                                  ; preds = %vector.body211
  %bin.rdx368 = fadd reassoc ninf nsz <8 x float> %874, %873
  %bin.rdx369 = fadd reassoc ninf nsz <8 x float> %875, %bin.rdx368
  %bin.rdx370 = fadd reassoc ninf nsz <8 x float> %876, %bin.rdx369
  %878 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx370)
  %bin.rdx371 = fadd reassoc ninf nsz <8 x float> %870, %869
  %bin.rdx372 = fadd reassoc ninf nsz <8 x float> %871, %bin.rdx371
  %bin.rdx373 = fadd reassoc ninf nsz <8 x float> %872, %bin.rdx372
  %879 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx373)
  br i1 %cmp.n374, label %for_loop_test11.after_for10_crit_edge.us, label %vec.epilog.iter.check381

vec.epilog.iter.check381:                         ; preds = %middle.block202
  br i1 %min.epilog.iters.check383, label %for_loop_body8.us.preheader, label %vec.epilog.ph380

vec.epilog.ph380:                                 ; preds = %vec.epilog.iter.check381, %vector.main.loop.iter.check207
  %bc.resume.val375 = phi i64 [ %n.vec210, %vec.epilog.iter.check381 ], [ 0, %vector.main.loop.iter.check207 ]
  %bc.merge.rdx376 = phi float [ %878, %vec.epilog.iter.check381 ], [ %.05086.us, %vector.main.loop.iter.check207 ]
  %bc.merge.rdx377 = phi float [ %879, %vec.epilog.iter.check381 ], [ %.05285.us, %vector.main.loop.iter.check207 ]
  %880 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx376, i64 0
  %881 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx377, i64 0
  %882 = trunc nuw nsw i64 %bc.resume.val375 to i32
  %.splatinsert = insertelement <8 x i32> poison, i32 %882, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = or disjoint <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert396 = insertelement <8 x i32> poison, i32 %116, i64 0
  %broadcast.splat397 = shufflevector <8 x i32> %broadcast.splatinsert396, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert399 = insertelement <8 x i32> poison, i32 %117, i64 0
  %broadcast.splat400 = shufflevector <8 x i32> %broadcast.splatinsert399, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert406 = insertelement <8 x i32> poison, i32 %118, i64 0
  %broadcast.splat407 = shufflevector <8 x i32> %broadcast.splatinsert406, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert410 = insertelement <8 x i32> poison, i32 %119, i64 0
  %broadcast.splat411 = shufflevector <8 x i32> %broadcast.splatinsert410, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert418 = insertelement <8 x i32> poison, i32 %120, i64 0
  %broadcast.splat419 = shufflevector <8 x i32> %broadcast.splatinsert418, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert422 = insertelement <8 x i32> poison, i32 %121, i64 0
  %broadcast.splat423 = shufflevector <8 x i32> %broadcast.splatinsert422, <8 x i32> poison, <8 x i32> zeroinitializer
  %883 = add i64 %110, %bc.resume.val375
  br label %vec.epilog.vector.body388

vec.epilog.vector.body388:                        ; preds = %vec.epilog.vector.body388, %vec.epilog.ph380
  %lsr.iv563 = phi i64 [ %lsr.iv.next564, %vec.epilog.vector.body388 ], [ %883, %vec.epilog.ph380 ]
  %vec.phi390 = phi <8 x float> [ %880, %vec.epilog.ph380 ], [ %1059, %vec.epilog.vector.body388 ]
  %vec.phi391 = phi <8 x float> [ %881, %vec.epilog.ph380 ], [ %1058, %vec.epilog.vector.body388 ]
  %vec.ind392 = phi <8 x i32> [ %induction, %vec.epilog.ph380 ], [ %vec.ind.next393, %vec.epilog.vector.body388 ]
  %884 = shl <8 x i32> %vec.ind392, splat (i32 1)
  %885 = add <8 x i32> %broadcast.splat222, %884
  %886 = add <8 x i32> %broadcast.splat397, %885
  %887 = sext <8 x i32> %886 to <8 x i64>
  %888 = getelementptr float, ptr %66, <8 x i64> %887
  %wide.masked.gather398 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %888, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %889 = add <8 x i32> %broadcast.splat400, %885
  %890 = sext <8 x i32> %889 to <8 x i64>
  %891 = getelementptr float, ptr %68, <8 x i64> %890
  %wide.masked.gather401 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %891, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %892 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather398, %wide.masked.gather401
  %893 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %892)
  %894 = add <8 x i32> %885, splat (i32 1)
  %895 = add <8 x i32> %broadcast.splat397, %894
  %896 = sext <8 x i32> %895 to <8 x i64>
  %897 = getelementptr float, ptr %66, <8 x i64> %896
  %wide.masked.gather402 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %897, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %898 = add <8 x i32> %884, %broadcast.splat239
  %899 = add <8 x i32> %broadcast.splat397, %898
  %900 = sext <8 x i32> %899 to <8 x i64>
  %901 = getelementptr float, ptr %66, <8 x i64> %900
  %wide.masked.gather405 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %901, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %902 = add <8 x i32> %broadcast.splat407, %894
  %903 = sext <8 x i32> %902 to <8 x i64>
  %904 = getelementptr float, ptr %66, <8 x i64> %903
  %wide.masked.gather408 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %904, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %905 = add <8 x i32> %broadcast.splat407, %898
  %906 = sext <8 x i32> %905 to <8 x i64>
  %907 = getelementptr float, ptr %66, <8 x i64> %906
  %wide.masked.gather409 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %907, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %908 = add <8 x i32> %broadcast.splat411, %894
  %909 = sext <8 x i32> %908 to <8 x i64>
  %910 = getelementptr float, ptr %66, <8 x i64> %909
  %wide.masked.gather412 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %910, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %911 = add <8 x i32> %broadcast.splat411, %898
  %912 = sext <8 x i32> %911 to <8 x i64>
  %913 = getelementptr float, ptr %66, <8 x i64> %912
  %wide.masked.gather413 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %913, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %914 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather402, %wide.masked.gather408
  %915 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather405, %wide.masked.gather409
  %916 = fadd reassoc ninf nsz <8 x float> %914, %wide.masked.gather412
  %917 = fadd reassoc ninf nsz <8 x float> %915, %wide.masked.gather413
  %918 = fsub reassoc ninf nsz <8 x float> %916, %917
  %919 = fmul reassoc ninf nsz <8 x float> %918, splat (float 0x3FD5555560000000)
  %920 = add <8 x i32> %broadcast.splat411, %885
  %921 = sext <8 x i32> %920 to <8 x i64>
  %922 = getelementptr float, ptr %66, <8 x i64> %921
  %wide.masked.gather414 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %922, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %923 = add <8 x i32> %broadcast.splat407, %885
  %924 = sext <8 x i32> %923 to <8 x i64>
  %925 = getelementptr float, ptr %66, <8 x i64> %924
  %wide.masked.gather415 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %925, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %926 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather408, %wide.masked.gather409
  %927 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather412, %926
  %928 = fadd reassoc ninf nsz <8 x float> %927, %wide.masked.gather413
  %929 = fadd reassoc ninf nsz <8 x float> %928, %wide.masked.gather414
  %930 = fsub reassoc ninf nsz <8 x float> %929, %wide.masked.gather415
  %931 = fmul reassoc ninf nsz <8 x float> %930, splat (float 0x3FD5555560000000)
  %932 = add <8 x i32> %broadcast.splat400, %894
  %933 = sext <8 x i32> %932 to <8 x i64>
  %934 = getelementptr float, ptr %68, <8 x i64> %933
  %wide.masked.gather416 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %934, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %935 = add <8 x i32> %broadcast.splat400, %898
  %936 = sext <8 x i32> %935 to <8 x i64>
  %937 = getelementptr float, ptr %68, <8 x i64> %936
  %wide.masked.gather417 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %937, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %938 = add <8 x i32> %broadcast.splat419, %894
  %939 = sext <8 x i32> %938 to <8 x i64>
  %940 = getelementptr float, ptr %68, <8 x i64> %939
  %wide.masked.gather420 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %940, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %941 = add <8 x i32> %broadcast.splat419, %898
  %942 = sext <8 x i32> %941 to <8 x i64>
  %943 = getelementptr float, ptr %68, <8 x i64> %942
  %wide.masked.gather421 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %943, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %944 = add <8 x i32> %broadcast.splat423, %894
  %945 = sext <8 x i32> %944 to <8 x i64>
  %946 = getelementptr float, ptr %68, <8 x i64> %945
  %wide.masked.gather424 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %946, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %947 = add <8 x i32> %broadcast.splat423, %898
  %948 = sext <8 x i32> %947 to <8 x i64>
  %949 = getelementptr float, ptr %68, <8 x i64> %948
  %wide.masked.gather425 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %949, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %950 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather416, %wide.masked.gather420
  %951 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather417, %wide.masked.gather421
  %952 = fadd reassoc ninf nsz <8 x float> %950, %wide.masked.gather424
  %953 = fadd reassoc ninf nsz <8 x float> %951, %wide.masked.gather425
  %954 = fsub reassoc ninf nsz <8 x float> %952, %953
  %955 = fmul reassoc ninf nsz <8 x float> %954, splat (float 0x3FD5555560000000)
  %956 = add <8 x i32> %broadcast.splat423, %885
  %957 = sext <8 x i32> %956 to <8 x i64>
  %958 = getelementptr float, ptr %68, <8 x i64> %957
  %wide.masked.gather426 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %958, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %959 = add <8 x i32> %broadcast.splat419, %885
  %960 = sext <8 x i32> %959 to <8 x i64>
  %961 = getelementptr float, ptr %68, <8 x i64> %960
  %wide.masked.gather427 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %961, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %962 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather420, %wide.masked.gather421
  %963 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather424, %962
  %964 = fadd reassoc ninf nsz <8 x float> %963, %wide.masked.gather425
  %965 = fadd reassoc ninf nsz <8 x float> %964, %wide.masked.gather426
  %966 = fsub reassoc ninf nsz <8 x float> %965, %wide.masked.gather427
  %967 = fmul reassoc ninf nsz <8 x float> %966, splat (float 0x3FD5555560000000)
  %968 = fmul reassoc ninf nsz <8 x float> %919, %919
  %969 = fmul reassoc ninf nsz <8 x float> %931, %931
  %970 = fadd reassoc ninf nsz <8 x float> %969, %968
  %971 = fmul reassoc ninf nsz <8 x float> %955, %955
  %972 = fmul reassoc ninf nsz <8 x float> %967, %967
  %973 = fadd reassoc ninf nsz <8 x float> %972, %971
  %974 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %970, <8 x float> %973)
  %975 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather401, splat (float -2.000000e+00)
  %976 = fadd reassoc ninf nsz <8 x float> %975, splat (float 3.000000e+00)
  %977 = tail call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %976, <8 x float> splat (float 3.000000e+00))
  %978 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %977, <8 x float> splat (float 1.000000e+00))
  %979 = fmul reassoc ninf nsz <8 x float> %978, %broadcast.splat309
  %980 = fmul reassoc ninf nsz <8 x float> %978, %978
  %981 = fmul reassoc ninf nsz <8 x float> %980, %broadcast.splat311
  %982 = fcmp reassoc ninf nsz olt <8 x float> %974, %981
  %983 = xor <8 x i1> %982, splat (i1 true)
  %984 = select <8 x i1> %broadcast.splat, <8 x i1> %983, <8 x i1> zeroinitializer
  %985 = fcmp reassoc ninf nsz olt <8 x float> %893, %979
  %986 = xor <8 x i1> %985, splat (i1 true)
  %987 = select <8 x i1> %984, <8 x i1> %986, <8 x i1> zeroinitializer
  %988 = fmul reassoc ninf nsz <8 x float> %979, splat (float 4.000000e+00)
  %989 = fdiv reassoc ninf nsz <8 x float> %893, %988
  %990 = fcmp reassoc ninf nsz ogt <8 x float> %989, splat (float 1.000000e+00)
  %991 = select <8 x i1> %990, <8 x float> splat (float 1.000000e+00), <8 x float> %989
  %992 = fmul reassoc ninf nsz <8 x float> %991, splat (float 0x3FD99999A0000000)
  %993 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FE6666680000000), %992
  %994 = select <8 x i1> %984, <8 x i1> %985, <8 x i1> zeroinitializer
  %995 = fmul reassoc ninf nsz <8 x float> %893, splat (float 0x3FC3333340000000)
  %996 = fdiv reassoc ninf nsz <8 x float> %995, %979
  %997 = fsub reassoc ninf nsz <8 x float> splat (float 0x3FF4CCCCC0000000), %996
  %998 = select <8 x i1> %broadcast.splat, <8 x i1> %982, <8 x i1> zeroinitializer
  %999 = fmul reassoc ninf nsz <8 x float> %979, splat (float 1.500000e+00)
  %1000 = fcmp reassoc ninf nsz uge <8 x float> %893, %999
  %1001 = select <8 x i1> %998, <8 x i1> %1000, <8 x i1> zeroinitializer
  %1002 = fsub reassoc ninf nsz <8 x float> %893, %999
  %1003 = fdiv reassoc ninf nsz <8 x float> %1002, %999
  %1004 = fcmp reassoc ninf nsz ogt <8 x float> %1003, splat (float 1.000000e+00)
  %1005 = select <8 x i1> %1004, <8 x float> splat (float 1.000000e+00), <8 x float> %1003
  %1006 = fmul reassoc ninf nsz <8 x float> %1005, splat (float 0x3FC99999A0000000)
  %1007 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %1006
  %1008 = fmul reassoc ninf nsz <8 x float> %893, splat (float 0x3FEE666660000000)
  %1009 = fdiv reassoc ninf nsz <8 x float> %1008, %999
  %1010 = fadd reassoc ninf nsz <8 x float> %1009, splat (float 0x3FA99999A0000000)
  %1011 = or <8 x i1> %994, %107
  %1012 = or <8 x i1> %1011, %998
  %1013 = or <8 x i1> %1012, %987
  %predphi432 = select <8 x i1> %1001, <8 x float> %1007, <8 x float> %1010
  %predphi433 = select <8 x i1> %994, <8 x float> %997, <8 x float> %predphi432
  %predphi434 = select <8 x i1> %987, <8 x float> %993, <8 x float> %predphi433
  %predphi435 = select <8 x i1> %broadcast.splat, <8 x float> %predphi434, <8 x float> splat (float 1.000000e+00)
  %1014 = fcmp reassoc ninf nsz ogt <8 x float> %974, splat (float 0x3EB0C6F7A0000000)
  %1015 = select <8 x i1> %1013, <8 x i1> %1014, <8 x i1> zeroinitializer
  %1016 = fcmp reassoc ninf nsz ogt <8 x float> %970, splat (float 0x3EB0C6F7A0000000)
  %1017 = fcmp reassoc ninf nsz ogt <8 x float> %973, splat (float 0x3EB0C6F7A0000000)
  %1018 = select <8 x i1> %1016, <8 x i1> %1017, <8 x i1> zeroinitializer
  %1019 = select <8 x i1> %1015, <8 x i1> %1018, <8 x i1> zeroinitializer
  %1020 = fmul reassoc ninf nsz <8 x float> %955, %919
  %1021 = fmul reassoc ninf nsz <8 x float> %967, %931
  %1022 = fadd reassoc ninf nsz <8 x float> %1021, %1020
  %1023 = fmul reassoc ninf nsz <8 x float> %973, %970
  %1024 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %1023)
  %1025 = fdiv reassoc ninf nsz <8 x float> %1022, %1024
  %1026 = fcmp reassoc ninf nsz ule <8 x float> %974, %981
  %1027 = fcmp reassoc ninf nsz uge <8 x float> %1025, splat (float 0x3FC99999A0000000)
  %.not468 = select <8 x i1> %1026, <8 x i1> splat (i1 true), <8 x i1> %1027
  %1028 = select <8 x i1> %1019, <8 x i1> %.not468, <8 x i1> zeroinitializer
  %1029 = tail call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %1025, <8 x float> zeroinitializer)
  %1030 = tail call reassoc ninf nsz <8 x float> @llvm.sqrt.v8f32(<8 x float> %974)
  %1031 = fmul reassoc ninf nsz <8 x float> %1030, splat (float 2.025000e+02)
  %1032 = fmul reassoc ninf nsz <8 x float> %1031, %1029
  %.fr469 = freeze <8 x float> %1032
  %1033 = fcmp reassoc nsz ogt <8 x float> %.fr469, splat (float 3.000000e+00)
  %1034 = xor <8 x i1> %1033, splat (i1 true)
  %1035 = and <8 x i1> %1028, %1034
  %1036 = fcmp reassoc nsz olt <8 x float> %.fr469, splat (float -3.000000e+00)
  %1037 = xor <8 x i1> %1036, splat (i1 true)
  %1038 = and <8 x i1> %1035, %1037
  %1039 = fmul reassoc ninf nsz <8 x float> %.fr469, %.fr469
  %1040 = fadd reassoc ninf nsz <8 x float> %1039, splat (float 2.700000e+01)
  %1041 = fmul reassoc ninf nsz <8 x float> %1040, %.fr469
  %1042 = fmul reassoc ninf nsz <8 x float> %1039, splat (float 9.000000e+00)
  %1043 = fadd reassoc ninf nsz <8 x float> %1042, splat (float 2.700000e+01)
  %1044 = fdiv reassoc ninf nsz <8 x float> %1041, %1043
  %1045 = fadd reassoc ninf nsz <8 x float> %1044, splat (float 1.000000e+00)
  %1046 = fsub reassoc ninf nsz <8 x float> splat (float 1.500000e+00), %1025
  %1047 = fmul reassoc ninf nsz <8 x float> %1046, %893
  %1048 = and <8 x i1> %1035, %1036
  %1049 = and <8 x i1> %1028, %1033
  %1050 = xor <8 x i1> %1018, splat (i1 true)
  %1051 = select <8 x i1> %1015, <8 x i1> %1050, <8 x i1> zeroinitializer
  %1052 = xor <8 x i1> %1014, splat (i1 true)
  %1053 = select <8 x i1> %1013, <8 x i1> %1052, <8 x i1> zeroinitializer
  %1054 = select <8 x i1> %1028, <8 x i1> splat (i1 true), <8 x i1> %1053
  %1055 = select <8 x i1> %1054, <8 x i1> splat (i1 true), <8 x i1> %1051
  %predphi440 = select <8 x i1> %1055, <8 x float> %893, <8 x float> %1047
  %predphi443 = select <8 x i1> %1049, <8 x float> splat (float 2.000000e+00), <8 x float> splat (float 1.000000e+00)
  %predphi444 = select <8 x i1> %1038, <8 x float> %1045, <8 x float> %predphi443
  %predphi445 = select <8 x i1> %1048, <8 x float> zeroinitializer, <8 x float> %predphi444
  %1056 = fmul reassoc ninf nsz <8 x float> %predphi445, %predphi435
  %1057 = fmul reassoc ninf nsz <8 x float> %1056, %predphi440
  %1058 = fadd reassoc ninf nsz <8 x float> %1057, %vec.phi391
  %1059 = fadd reassoc ninf nsz <8 x float> %1056, %vec.phi390
  %vec.ind.next393 = add <8 x i32> %vec.ind392, splat (i32 8)
  %lsr.iv.next564 = add i64 %lsr.iv563, 8
  %1060 = icmp eq i64 %lsr.iv.next564, 0
  br i1 %1060, label %vec.epilog.middle.block378, label %vec.epilog.vector.body388, !llvm.loop !14

vec.epilog.middle.block378:                       ; preds = %vec.epilog.vector.body388
  %1061 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %1059)
  %1062 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %1058)
  br i1 %cmp.n447, label %for_loop_test11.after_for10_crit_edge.us, label %for_loop_body8.us.preheader

for_loop_body8.us.preheader:                      ; preds = %vec.epilog.middle.block378, %vec.epilog.iter.check381, %vector.scevcheck150, %iter.check205
  %indvars.iv.ph = phi i64 [ %n.vec210, %vec.epilog.iter.check381 ], [ 0, %iter.check205 ], [ 0, %vector.scevcheck150 ], [ %n.vec385, %vec.epilog.middle.block378 ]
  %.15182.us.ph = phi float [ %878, %vec.epilog.iter.check381 ], [ %.05086.us, %iter.check205 ], [ %.05086.us, %vector.scevcheck150 ], [ %1061, %vec.epilog.middle.block378 ]
  %.15381.us.ph = phi float [ %879, %vec.epilog.iter.check381 ], [ %.05285.us, %iter.check205 ], [ %.05285.us, %vector.scevcheck150 ], [ %1062, %vec.epilog.middle.block378 ]
  %1063 = trunc i64 %indvars.iv.ph to i32
  %1064 = shl nuw i32 %1063, 1
  %1065 = add i64 %111, %indvars.iv.ph
  br label %for_loop_body8.us

for_loop_body8.us:                                ; preds = %after_if38.us, %for_loop_body8.us.preheader
  %lsr.iv589 = phi i64 [ %1065, %for_loop_body8.us.preheader ], [ %lsr.iv.next590, %after_if38.us ]
  %lsr.iv587 = phi i32 [ %lsr.iv585, %for_loop_body8.us.preheader ], [ %lsr.iv.next588, %after_if38.us ]
  %lsr.iv583 = phi i32 [ %lsr.iv581, %for_loop_body8.us.preheader ], [ %lsr.iv.next584, %after_if38.us ]
  %lsr.iv579 = phi i32 [ %lsr.iv577, %for_loop_body8.us.preheader ], [ %lsr.iv.next580, %after_if38.us ]
  %lsr.iv575 = phi i32 [ %lsr.iv573, %for_loop_body8.us.preheader ], [ %lsr.iv.next576, %after_if38.us ]
  %lsr.iv571 = phi i32 [ %lsr.iv569, %for_loop_body8.us.preheader ], [ %lsr.iv.next572, %after_if38.us ]
  %lsr.iv567 = phi i32 [ %lsr.iv565, %for_loop_body8.us.preheader ], [ %lsr.iv.next568, %after_if38.us ]
  %.15182.us = phi float [ %1226, %after_if38.us ], [ %.15182.us.ph, %for_loop_body8.us.preheader ]
  %.15381.us = phi float [ %1225, %after_if38.us ], [ %.15381.us.ph, %for_loop_body8.us.preheader ]
  %1066 = add i32 %1064, %lsr.iv587
  %1067 = add i32 %1066, 1
  %1068 = sext i32 %1067 to i64
  %1069 = getelementptr float, ptr %66, i64 %1068
  %1070 = load float, ptr %1069, align 4
  %1071 = add i32 %1064, %lsr.iv583
  %1072 = add i32 %1071, 1
  %1073 = sext i32 %1072 to i64
  %1074 = getelementptr float, ptr %68, i64 %1073
  %1075 = load float, ptr %1074, align 4
  %1076 = fsub reassoc ninf nsz float %1070, %1075
  %1077 = tail call noundef float @llvm.fabs.f32(float %1076)
  %1078 = add i32 %1066, 2
  %1079 = sext i32 %1078 to i64
  %1080 = getelementptr float, ptr %66, i64 %1079
  %1081 = load float, ptr %1080, align 4
  %1082 = sext i32 %1066 to i64
  %1083 = getelementptr float, ptr %66, i64 %1082
  %1084 = load float, ptr %1083, align 4
  %1085 = add i32 %1064, %lsr.iv575
  %1086 = add i32 %1085, 2
  %1087 = sext i32 %1086 to i64
  %1088 = getelementptr float, ptr %66, i64 %1087
  %1089 = load float, ptr %1088, align 4
  %1090 = sext i32 %1085 to i64
  %1091 = getelementptr float, ptr %66, i64 %1090
  %1092 = load float, ptr %1091, align 4
  %1093 = add i32 %1064, %lsr.iv579
  %1094 = add i32 %1093, 2
  %1095 = sext i32 %1094 to i64
  %1096 = getelementptr float, ptr %66, i64 %1095
  %1097 = load float, ptr %1096, align 4
  %1098 = sext i32 %1093 to i64
  %1099 = getelementptr float, ptr %66, i64 %1098
  %1100 = load float, ptr %1099, align 4
  %1101 = fadd reassoc ninf nsz float %1081, %1089
  %1102 = fadd reassoc ninf nsz float %1084, %1092
  %1103 = fadd reassoc ninf nsz float %1101, %1097
  %1104 = fadd reassoc ninf nsz float %1102, %1100
  %1105 = fsub reassoc ninf nsz float %1103, %1104
  %1106 = fmul reassoc ninf nsz float %1105, 0x3FD5555560000000
  %1107 = add i32 %1093, 1
  %1108 = sext i32 %1107 to i64
  %1109 = getelementptr float, ptr %66, i64 %1108
  %1110 = load float, ptr %1109, align 4
  %1111 = add i32 %1085, 1
  %1112 = sext i32 %1111 to i64
  %1113 = getelementptr float, ptr %66, i64 %1112
  %1114 = load float, ptr %1113, align 4
  %1115 = fadd reassoc ninf nsz float %1089, %1092
  %1116 = fsub reassoc ninf nsz float %1097, %1115
  %1117 = fadd reassoc ninf nsz float %1116, %1100
  %1118 = fadd reassoc ninf nsz float %1117, %1110
  %1119 = fsub reassoc ninf nsz float %1118, %1114
  %1120 = fmul reassoc ninf nsz float %1119, 0x3FD5555560000000
  %1121 = add i32 %1071, 2
  %1122 = sext i32 %1121 to i64
  %1123 = getelementptr float, ptr %68, i64 %1122
  %1124 = load float, ptr %1123, align 4
  %1125 = sext i32 %1071 to i64
  %1126 = getelementptr float, ptr %68, i64 %1125
  %1127 = load float, ptr %1126, align 4
  %1128 = add i32 %1064, %lsr.iv567
  %1129 = add i32 %1128, 2
  %1130 = sext i32 %1129 to i64
  %1131 = getelementptr float, ptr %68, i64 %1130
  %1132 = load float, ptr %1131, align 4
  %1133 = sext i32 %1128 to i64
  %1134 = getelementptr float, ptr %68, i64 %1133
  %1135 = load float, ptr %1134, align 4
  %1136 = add i32 %1064, %lsr.iv571
  %1137 = add i32 %1136, 2
  %1138 = sext i32 %1137 to i64
  %1139 = getelementptr float, ptr %68, i64 %1138
  %1140 = load float, ptr %1139, align 4
  %1141 = sext i32 %1136 to i64
  %1142 = getelementptr float, ptr %68, i64 %1141
  %1143 = load float, ptr %1142, align 4
  %1144 = fadd reassoc ninf nsz float %1124, %1132
  %1145 = fadd reassoc ninf nsz float %1127, %1135
  %1146 = fadd reassoc ninf nsz float %1144, %1140
  %1147 = fadd reassoc ninf nsz float %1145, %1143
  %1148 = fsub reassoc ninf nsz float %1146, %1147
  %1149 = fmul reassoc ninf nsz float %1148, 0x3FD5555560000000
  %1150 = add i32 %1136, 1
  %1151 = sext i32 %1150 to i64
  %1152 = getelementptr float, ptr %68, i64 %1151
  %1153 = load float, ptr %1152, align 4
  %1154 = add i32 %1128, 1
  %1155 = sext i32 %1154 to i64
  %1156 = getelementptr float, ptr %68, i64 %1155
  %1157 = load float, ptr %1156, align 4
  %1158 = fadd reassoc ninf nsz float %1132, %1135
  %1159 = fsub reassoc ninf nsz float %1140, %1158
  %1160 = fadd reassoc ninf nsz float %1159, %1143
  %1161 = fadd reassoc ninf nsz float %1160, %1153
  %1162 = fsub reassoc ninf nsz float %1161, %1157
  %1163 = fmul reassoc ninf nsz float %1162, 0x3FD5555560000000
  %1164 = fmul reassoc ninf nsz float %1106, %1106
  %1165 = fmul reassoc ninf nsz float %1120, %1120
  %1166 = fadd reassoc ninf nsz float %1165, %1164
  %1167 = fmul reassoc ninf nsz float %1149, %1149
  %1168 = fmul reassoc ninf nsz float %1163, %1163
  %1169 = fadd reassoc ninf nsz float %1168, %1167
  %1170 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %1166, float %1169)
  %factor.us = fmul reassoc ninf nsz float %1075, -2.000000e+00
  %1171 = fadd reassoc ninf nsz float %factor.us, 3.000000e+00
  %1172 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %1171, float 3.000000e+00)
  %1173 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1172, float 1.000000e+00)
  %1174 = fmul reassoc ninf nsz float %1173, %50
  %1175 = fmul reassoc ninf nsz float %1173, %1173
  %1176 = fmul reassoc ninf nsz float %1175, %53
  br i1 %54, label %true_block12.us, label %after_if14.us

true_block12.us:                                  ; preds = %for_loop_body8.us
  %1177 = fcmp reassoc ninf nsz olt float %1170, %1176
  br i1 %1177, label %true_block15.us, label %false_block16.us

false_block16.us:                                 ; preds = %true_block12.us
  %1178 = fcmp reassoc ninf nsz olt float %1077, %1174
  br i1 %1178, label %true_block24.us, label %false_block25.us

false_block25.us:                                 ; preds = %false_block16.us
  %1179 = fmul reassoc ninf nsz float %1174, 4.000000e+00
  %1180 = fdiv reassoc ninf nsz float %1077, %1179
  %1181 = fcmp reassoc ninf nsz ogt float %1180, 1.000000e+00
  %spec.store.select1.us = select i1 %1181, float 1.000000e+00, float %1180
  %1182 = fmul reassoc ninf nsz float %spec.store.select1.us, 0x3FD99999A0000000
  %1183 = fsub reassoc ninf nsz float 0x3FE6666680000000, %1182
  br label %after_if14.us

true_block24.us:                                  ; preds = %false_block16.us
  %1184 = fmul reassoc ninf nsz float %1077, 0x3FC3333340000000
  %1185 = fdiv reassoc ninf nsz float %1184, %1174
  %1186 = fsub reassoc ninf nsz float 0x3FF4CCCCC0000000, %1185
  br label %after_if14.us

true_block15.us:                                  ; preds = %true_block12.us
  %1187 = fmul reassoc ninf nsz float %1174, 1.500000e+00
  %1188 = fcmp reassoc ninf nsz olt float %1077, %1187
  br i1 %1188, label %true_block18.us, label %false_block19.us

false_block19.us:                                 ; preds = %true_block15.us
  %1189 = fsub reassoc ninf nsz float %1077, %1187
  %1190 = fdiv reassoc ninf nsz float %1189, %1187
  %1191 = fcmp reassoc ninf nsz ogt float %1190, 1.000000e+00
  %spec.store.select.us = select i1 %1191, float 1.000000e+00, float %1190
  %1192 = fmul reassoc ninf nsz float %spec.store.select.us, 0x3FC99999A0000000
  %1193 = fsub reassoc ninf nsz float 1.000000e+00, %1192
  br label %after_if14.us

true_block18.us:                                  ; preds = %true_block15.us
  %1194 = fmul reassoc ninf nsz float %1077, 0x3FEE666660000000
  %1195 = fdiv reassoc ninf nsz float %1194, %1187
  %1196 = fadd reassoc ninf nsz float %1195, 0x3FA99999A0000000
  br label %after_if14.us

after_if14.us:                                    ; preds = %true_block18.us, %false_block19.us, %true_block24.us, %false_block25.us, %for_loop_body8.us
  %.046.us = phi float [ %1196, %true_block18.us ], [ %1193, %false_block19.us ], [ %1186, %true_block24.us ], [ %1183, %false_block25.us ], [ 1.000000e+00, %for_loop_body8.us ]
  %1197 = fcmp reassoc ninf nsz ogt float %1170, 0x3EB0C6F7A0000000
  br i1 %1197, label %true_block30.us, label %after_if38.us

true_block30.us:                                  ; preds = %after_if14.us
  %1198 = fcmp reassoc ninf nsz ogt float %1166, 0x3EB0C6F7A0000000
  %1199 = fcmp reassoc ninf nsz ogt float %1169, 0x3EB0C6F7A0000000
  %.041.us = select i1 %1198, i1 %1199, i1 false
  br i1 %.041.us, label %true_block36.us, label %after_if38.us

true_block36.us:                                  ; preds = %true_block30.us
  %1200 = fmul reassoc ninf nsz float %1149, %1106
  %1201 = fmul reassoc ninf nsz float %1163, %1120
  %1202 = fadd reassoc ninf nsz float %1201, %1200
  %1203 = fmul reassoc ninf nsz float %1169, %1166
  %1204 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %1203)
  %1205 = fdiv reassoc ninf nsz float %1202, %1204
  %1206 = fcmp reassoc ninf nsz ogt float %1170, %1176
  %1207 = fcmp reassoc ninf nsz olt float %1205, 0x3FC99999A0000000
  %.040.us = select i1 %1206, i1 %1207, i1 false
  br i1 %.040.us, label %true_block42.us, label %false_block43.us

false_block43.us:                                 ; preds = %true_block36.us
  %1208 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1205, float 0.000000e+00)
  %1209 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %1170)
  %1210 = fmul reassoc ninf nsz float %1209, 2.025000e+02
  %1211 = fmul reassoc ninf nsz float %1210, %1208
  %1212 = fcmp reassoc ninf nsz ogt float %1211, 3.000000e+00
  br i1 %1212, label %after_if38.us, label %false_block46.us

false_block46.us:                                 ; preds = %false_block43.us
  %1213 = fcmp reassoc ninf nsz olt float %1211, -3.000000e+00
  br i1 %1213, label %after_if38.us, label %false_block49.us

false_block49.us:                                 ; preds = %false_block46.us
  %1214 = fmul reassoc ninf nsz float %1211, %1211
  %1215 = fadd reassoc ninf nsz float %1214, 2.700000e+01
  %1216 = fmul reassoc ninf nsz float %1215, %1211
  %1217 = fmul reassoc ninf nsz float %1214, 9.000000e+00
  %1218 = fadd reassoc ninf nsz float %1217, 2.700000e+01
  %1219 = fdiv reassoc ninf nsz float %1216, %1218
  %1220 = fadd reassoc ninf nsz float %1219, 1.000000e+00
  br label %after_if38.us

true_block42.us:                                  ; preds = %true_block36.us
  %1221 = fsub reassoc ninf nsz float 1.500000e+00, %1205
  %1222 = fmul reassoc ninf nsz float %1221, %1077
  br label %after_if38.us

after_if38.us:                                    ; preds = %true_block42.us, %false_block49.us, %false_block46.us, %false_block43.us, %true_block30.us, %after_if14.us
  %.047.us = phi float [ %1222, %true_block42.us ], [ %1077, %true_block30.us ], [ %1077, %after_if14.us ], [ %1077, %false_block43.us ], [ %1077, %false_block49.us ], [ %1077, %false_block46.us ]
  %.043.us = phi float [ 1.000000e+00, %true_block42.us ], [ 1.000000e+00, %true_block30.us ], [ 1.000000e+00, %after_if14.us ], [ 2.000000e+00, %false_block43.us ], [ %1220, %false_block49.us ], [ 0.000000e+00, %false_block46.us ]
  %1223 = fmul reassoc ninf nsz float %.043.us, %.046.us
  %1224 = fmul reassoc ninf nsz float %1223, %.047.us
  %1225 = fadd reassoc ninf nsz float %1224, %.15381.us
  %1226 = fadd reassoc ninf nsz float %1223, %.15182.us
  %lsr.iv.next568 = add i32 %lsr.iv567, 2
  %lsr.iv.next572 = add i32 %lsr.iv571, 2
  %lsr.iv.next576 = add i32 %lsr.iv575, 2
  %lsr.iv.next580 = add i32 %lsr.iv579, 2
  %lsr.iv.next584 = add i32 %lsr.iv583, 2
  %lsr.iv.next588 = add i32 %lsr.iv587, 2
  %lsr.iv.next590 = add i64 %lsr.iv589, 1
  %exitcond.not = icmp eq i64 %lsr.iv.next590, 0
  br i1 %exitcond.not, label %for_loop_test11.after_for10_crit_edge.us.loopexit, label %for_loop_body8.us, !llvm.loop !15

for_loop_test11.after_for10_crit_edge.us.loopexit: ; preds = %after_if38.us
  br label %for_loop_test11.after_for10_crit_edge.us

for_loop_test11.after_for10_crit_edge.us:         ; preds = %for_loop_test11.after_for10_crit_edge.us.loopexit, %vec.epilog.middle.block378, %middle.block202
  %.lcssa126 = phi float [ %879, %middle.block202 ], [ %1062, %vec.epilog.middle.block378 ], [ %1225, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %878, %middle.block202 ], [ %1061, %vec.epilog.middle.block378 ], [ %1226, %for_loop_test11.after_for10_crit_edge.us.loopexit ]
  %1227 = add nuw nsw i32 %.04987.us, 1
  %lsr.iv.next566 = add i32 %lsr.iv565, %76
  %lsr.iv.next570 = add i32 %lsr.iv569, %76
  %lsr.iv.next574 = add i32 %lsr.iv573, %73
  %lsr.iv.next578 = add i32 %lsr.iv577, %73
  %lsr.iv.next582 = add i32 %lsr.iv581, %76
  %lsr.iv.next586 = add i32 %lsr.iv585, %73
  %exitcond107.not = icmp eq i32 %1227, %56
  br i1 %exitcond107.not, label %after_for6, label %iter.check205

after_if3:                                        ; preds = %true_block62, %after_if53, %for_loop_body
  %.0.sink = phi float [ %1387, %true_block62 ], [ 0.000000e+00, %after_if53 ], [ 0.000000e+00, %for_loop_body ]
  %1228 = load ptr, ptr %0, align 8
  %1229 = getelementptr i8, ptr %1228, i64 104
  %1230 = load ptr, ptr %1229, align 8
  %1231 = getelementptr i8, ptr %1228, i64 100
  %1232 = load i32, ptr %1231, align 4
  %1233 = mul i32 %1232, %38
  %1234 = add i32 %1233, %34
  %1235 = sext i32 %1234 to i64
  %1236 = getelementptr float, ptr %1230, i64 %1235
  store float %.0.sink, ptr %1236, align 4
  %1237 = add nsw i32 %.044100, 1
  %exitcond115.not = icmp eq i32 %1237, %18
  br i1 %exitcond115.not, label %after_for.loopexit, label %for_loop_body

after_for6:                                       ; preds = %for_loop_test11.after_for10_crit_edge.us
  %1238 = fcmp reassoc ninf nsz olt float %.lcssa, 0x3F1A36E2E0000000
  br i1 %1238, label %for_loop_body54.lr.ph.split.us, label %false_block52

for_loop_body54.lr.ph.split.us:                   ; preds = %after_for6, %true_block1
  %1239 = getelementptr i8, ptr %59, i64 20
  %1240 = getelementptr i8, ptr %59, i64 24
  %1241 = getelementptr i8, ptr %59, i64 4
  %1242 = getelementptr i8, ptr %59, i64 8
  %1243 = load ptr, ptr %1242, align 8
  %1244 = load i32, ptr %1241, align 4
  %1245 = load ptr, ptr %1240, align 8
  %1246 = load i32, ptr %1239, align 4
  %smax = tail call i32 @llvm.smax.i32(i32 %44, i32 1)
  %smax113 = tail call i32 @llvm.smax.i32(i32 %42, i32 1)
  %wide.trip.count111 = zext i32 %smax to i64
  %1247 = add nsw i64 %wide.trip.count111, -1
  %1248 = mul i32 %21, %1244
  %1249 = mul i32 %1248, %38
  %1250 = add i32 %1249, %40
  %1251 = mul i32 %21, %1246
  %1252 = mul i32 %1251, %38
  %1253 = add i32 %1252, %40
  %min.iters.check = icmp slt i32 %44, 4
  %1254 = trunc nsw i64 %1247 to i32
  %invariant.op559 = add i32 %1250, %1254
  %invariant.op561 = add i32 %1253, %1254
  %1255 = icmp ugt i64 %1247, 4294967295
  %min.iters.check128 = icmp slt i32 %44, 32
  %n.vec = and i64 %wide.trip.count111, 2147483616
  %cmp.n = icmp eq i64 %n.vec, %wide.trip.count111
  %n.vec.remaining = and i64 %wide.trip.count111, 28
  %min.epilog.iters.check = icmp eq i64 %n.vec.remaining, 0
  %n.vec142 = and i64 %wide.trip.count111, 2147483644
  %cmp.n148 = icmp eq i64 %n.vec142, %wide.trip.count111
  %xtraiter = and i64 %wide.trip.count111, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %1256 = lshr i64 %wide.trip.count111, 2
  %1257 = mul nsw i64 %1256, -4
  %1258 = zext i32 %1253 to i64
  %1259 = zext i32 %1246 to i64
  %1260 = zext i32 %1250 to i64
  %1261 = zext i32 %1244 to i64
  %1262 = mul nsw i64 %xtraiter, -1
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test61.after_for60_crit_edge.us, %for_loop_body54.lr.ph.split.us
  %lsr.iv609 = phi i64 [ %lsr.iv.next610, %for_loop_test61.after_for60_crit_edge.us ], [ %1260, %for_loop_body54.lr.ph.split.us ]
  %lsr.iv607 = phi i64 [ %lsr.iv.next608, %for_loop_test61.after_for60_crit_edge.us ], [ %1258, %for_loop_body54.lr.ph.split.us ]
  %.03696.us = phi i32 [ 0, %for_loop_body54.lr.ph.split.us ], [ %1367, %for_loop_test61.after_for60_crit_edge.us ]
  %.03795.us = phi float [ 0.000000e+00, %for_loop_body54.lr.ph.split.us ], [ %.lcssa127, %for_loop_test61.after_for60_crit_edge.us ]
  %lsr624 = trunc i64 %lsr.iv609 to i32
  %lsr622 = trunc i64 %lsr.iv607 to i32
  br i1 %min.iters.check, label %for_loop_body58.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %1263 = mul i32 %1246, %.03696.us
  %1264 = add i32 %1253, %1263
  %1265 = mul i32 %1244, %.03696.us
  %1266 = add i32 %1250, %1265
  %.reass560 = add i32 %1265, %invariant.op559
  %1267 = icmp slt i32 %.reass560, %1266
  %.reass562 = add i32 %1263, %invariant.op561
  %1268 = icmp slt i32 %.reass562, %1264
  %1269 = or i1 %1268, %1255
  %1270 = or i1 %1267, %1269
  br i1 %1270, label %for_loop_body58.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check128, label %vec.epilog.ph, label %vector.ph

vector.ph:                                        ; preds = %vector.main.loop.iter.check
  %1271 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.03795.us, i64 0
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv599 = phi i32 [ %lsr.iv.next600, %vector.body ], [ %lsr622, %vector.ph ]
  %lsr.iv595 = phi i32 [ %lsr.iv.next596, %vector.body ], [ %lsr624, %vector.ph ]
  %lsr.iv591 = phi i64 [ %lsr.iv.next592, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.phi = phi <8 x float> [ %1271, %vector.ph ], [ %1290, %vector.body ]
  %vec.phi129 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1291, %vector.body ]
  %vec.phi130 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1292, %vector.body ]
  %vec.phi131 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %1293, %vector.body ]
  %1272 = sext i32 %lsr.iv595 to i64
  %1273 = getelementptr float, ptr %1243, i64 %1272
  %1274 = getelementptr i8, ptr %1273, i64 32
  %1275 = getelementptr i8, ptr %1273, i64 64
  %1276 = getelementptr i8, ptr %1273, i64 96
  %wide.load = load <8 x float>, ptr %1273, align 4
  %wide.load132 = load <8 x float>, ptr %1274, align 4
  %wide.load133 = load <8 x float>, ptr %1275, align 4
  %wide.load134 = load <8 x float>, ptr %1276, align 4
  %1277 = sext i32 %lsr.iv599 to i64
  %1278 = getelementptr float, ptr %1245, i64 %1277
  %1279 = getelementptr i8, ptr %1278, i64 32
  %1280 = getelementptr i8, ptr %1278, i64 64
  %1281 = getelementptr i8, ptr %1278, i64 96
  %wide.load135 = load <8 x float>, ptr %1278, align 4
  %wide.load136 = load <8 x float>, ptr %1279, align 4
  %wide.load137 = load <8 x float>, ptr %1280, align 4
  %wide.load138 = load <8 x float>, ptr %1281, align 4
  %1282 = fsub reassoc ninf nsz <8 x float> %wide.load, %wide.load135
  %1283 = fsub reassoc ninf nsz <8 x float> %wide.load132, %wide.load136
  %1284 = fsub reassoc ninf nsz <8 x float> %wide.load133, %wide.load137
  %1285 = fsub reassoc ninf nsz <8 x float> %wide.load134, %wide.load138
  %1286 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1282)
  %1287 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1283)
  %1288 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1284)
  %1289 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %1285)
  %1290 = fadd reassoc ninf nsz <8 x float> %1286, %vec.phi
  %1291 = fadd reassoc ninf nsz <8 x float> %1287, %vec.phi129
  %1292 = fadd reassoc ninf nsz <8 x float> %1288, %vec.phi130
  %1293 = fadd reassoc ninf nsz <8 x float> %1289, %vec.phi131
  %lsr.iv.next592 = add nsw i64 %lsr.iv591, -32
  %lsr.iv.next596 = add i32 %lsr.iv595, 32
  %lsr.iv.next600 = add i32 %lsr.iv599, 32
  %1294 = icmp eq i64 %lsr.iv.next592, 0
  br i1 %1294, label %middle.block, label %vector.body, !llvm.loop !16

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %1291, %1290
  %bin.rdx139 = fadd reassoc ninf nsz <8 x float> %1292, %bin.rdx
  %bin.rdx140 = fadd reassoc ninf nsz <8 x float> %1293, %bin.rdx139
  %1295 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx140)
  br i1 %cmp.n, label %for_loop_test61.after_for60_crit_edge.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check, label %for_loop_body58.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %1295, %vec.epilog.iter.check ], [ %.03795.us, %vector.main.loop.iter.check ]
  %1296 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %1297 = add i64 %1257, %vec.epilog.resume.val
  %1298 = trunc i64 %vec.epilog.resume.val to i32
  %1299 = add i32 %lsr624, %1298
  %1300 = add i32 %lsr622, %1298
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv605 = phi i32 [ %lsr.iv.next606, %vec.epilog.vector.body ], [ %1300, %vec.epilog.ph ]
  %lsr.iv603 = phi i32 [ %lsr.iv.next604, %vec.epilog.vector.body ], [ %1299, %vec.epilog.ph ]
  %lsr.iv601 = phi i64 [ %lsr.iv.next602, %vec.epilog.vector.body ], [ %1297, %vec.epilog.ph ]
  %vec.phi144 = phi <4 x float> [ %1296, %vec.epilog.ph ], [ %1307, %vec.epilog.vector.body ]
  %1301 = sext i32 %lsr.iv603 to i64
  %1302 = getelementptr float, ptr %1243, i64 %1301
  %wide.load145 = load <4 x float>, ptr %1302, align 4
  %1303 = sext i32 %lsr.iv605 to i64
  %1304 = getelementptr float, ptr %1245, i64 %1303
  %wide.load146 = load <4 x float>, ptr %1304, align 4
  %1305 = fsub reassoc ninf nsz <4 x float> %wide.load145, %wide.load146
  %1306 = tail call <4 x float> @llvm.fabs.v4f32(<4 x float> %1305)
  %1307 = fadd reassoc ninf nsz <4 x float> %1306, %vec.phi144
  %lsr.iv.next602 = add i64 %lsr.iv601, 4
  %lsr.iv.next604 = add i32 %lsr.iv603, 4
  %lsr.iv.next606 = add i32 %lsr.iv605, 4
  %1308 = icmp eq i64 %lsr.iv.next602, 0
  br i1 %1308, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !17

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %1309 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %1307)
  br i1 %cmp.n148, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader

for_loop_body58.us.preheader:                     ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv108.ph = phi i64 [ %n.vec, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec142, %vec.epilog.middle.block ]
  %.191.us.ph = phi float [ %1295, %vec.epilog.iter.check ], [ %.03795.us, %iter.check ], [ %.03795.us, %vector.scevcheck ], [ %1309, %vec.epilog.middle.block ]
  br i1 %lcmp.mod.not, label %for_loop_body58.us.prol.loopexit, label %for_loop_body58.us.prol.preheader

for_loop_body58.us.prol.preheader:                ; preds = %for_loop_body58.us.preheader
  br label %for_loop_body58.us.prol

for_loop_body58.us.prol:                          ; preds = %for_loop_body58.us.prol, %for_loop_body58.us.prol.preheader
  %lsr.iv612 = phi i64 [ %1262, %for_loop_body58.us.prol.preheader ], [ %lsr.iv.next613, %for_loop_body58.us.prol ]
  %indvars.iv108.prol = phi i64 [ %indvars.iv.next109.prol, %for_loop_body58.us.prol ], [ %indvars.iv108.ph, %for_loop_body58.us.prol.preheader ]
  %.191.us.prol = phi float [ %1320, %for_loop_body58.us.prol ], [ %.191.us.ph, %for_loop_body58.us.prol.preheader ]
  %1310 = add i64 %lsr.iv609, %indvars.iv108.prol
  %tmp611 = trunc i64 %1310 to i32
  %1311 = sext i32 %tmp611 to i64
  %1312 = getelementptr float, ptr %1243, i64 %1311
  %1313 = load float, ptr %1312, align 4
  %1314 = add i64 %lsr.iv607, %indvars.iv108.prol
  %tmp = trunc i64 %1314 to i32
  %1315 = sext i32 %tmp to i64
  %1316 = getelementptr float, ptr %1245, i64 %1315
  %1317 = load float, ptr %1316, align 4
  %1318 = fsub reassoc ninf nsz float %1313, %1317
  %1319 = tail call noundef float @llvm.fabs.f32(float %1318)
  %1320 = fadd reassoc ninf nsz float %1319, %.191.us.prol
  %indvars.iv.next109.prol = add nuw nsw i64 %indvars.iv108.prol, 1
  %lsr.iv.next613 = add nsw i64 %lsr.iv612, 1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next613, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body58.us.prol.loopexit.loopexit, label %for_loop_body58.us.prol, !llvm.loop !18

for_loop_body58.us.prol.loopexit.loopexit:        ; preds = %for_loop_body58.us.prol
  br label %for_loop_body58.us.prol.loopexit

for_loop_body58.us.prol.loopexit:                 ; preds = %for_loop_body58.us.prol.loopexit.loopexit, %for_loop_body58.us.preheader
  %.lcssa487.unr = phi float [ poison, %for_loop_body58.us.preheader ], [ %1320, %for_loop_body58.us.prol.loopexit.loopexit ]
  %indvars.iv108.unr = phi i64 [ %indvars.iv108.ph, %for_loop_body58.us.preheader ], [ %indvars.iv.next109.prol, %for_loop_body58.us.prol.loopexit.loopexit ]
  %.191.us.unr = phi float [ %.191.us.ph, %for_loop_body58.us.preheader ], [ %1320, %for_loop_body58.us.prol.loopexit.loopexit ]
  %1321 = sub nsw i64 %indvars.iv108.ph, %wide.trip.count111
  %1322 = icmp ugt i64 %1321, -4
  br i1 %1322, label %for_loop_test61.after_for60_crit_edge.us, label %for_loop_body58.us.preheader.new

for_loop_body58.us.preheader.new:                 ; preds = %for_loop_body58.us.prol.loopexit
  br label %for_loop_body58.us

for_loop_body58.us:                               ; preds = %for_loop_body58.us, %for_loop_body58.us.preheader.new
  %indvars.iv108 = phi i64 [ %indvars.iv108.unr, %for_loop_body58.us.preheader.new ], [ %indvars.iv.next109.3, %for_loop_body58.us ]
  %.191.us = phi float [ %.191.us.unr, %for_loop_body58.us.preheader.new ], [ %1366, %for_loop_body58.us ]
  %1323 = add i64 %lsr.iv609, %indvars.iv108
  %tmp621 = trunc i64 %1323 to i32
  %1324 = sext i32 %tmp621 to i64
  %1325 = getelementptr float, ptr %1243, i64 %1324
  %1326 = load float, ptr %1325, align 4
  %1327 = add i64 %lsr.iv607, %indvars.iv108
  %tmp620 = trunc i64 %1327 to i32
  %1328 = sext i32 %tmp620 to i64
  %1329 = getelementptr float, ptr %1245, i64 %1328
  %1330 = load float, ptr %1329, align 4
  %1331 = fsub reassoc ninf nsz float %1326, %1330
  %1332 = tail call noundef float @llvm.fabs.f32(float %1331)
  %1333 = fadd reassoc ninf nsz float %1332, %.191.us
  %1334 = add i64 %1323, 1
  %tmp619 = trunc i64 %1334 to i32
  %1335 = sext i32 %tmp619 to i64
  %1336 = getelementptr float, ptr %1243, i64 %1335
  %1337 = load float, ptr %1336, align 4
  %1338 = add i64 %1327, 1
  %tmp618 = trunc i64 %1338 to i32
  %1339 = sext i32 %tmp618 to i64
  %1340 = getelementptr float, ptr %1245, i64 %1339
  %1341 = load float, ptr %1340, align 4
  %1342 = fsub reassoc ninf nsz float %1337, %1341
  %1343 = tail call noundef float @llvm.fabs.f32(float %1342)
  %1344 = fadd reassoc ninf nsz float %1343, %1333
  %1345 = add i64 %1323, 2
  %tmp617 = trunc i64 %1345 to i32
  %1346 = sext i32 %tmp617 to i64
  %1347 = getelementptr float, ptr %1243, i64 %1346
  %1348 = load float, ptr %1347, align 4
  %1349 = add i64 %1327, 2
  %tmp616 = trunc i64 %1349 to i32
  %1350 = sext i32 %tmp616 to i64
  %1351 = getelementptr float, ptr %1245, i64 %1350
  %1352 = load float, ptr %1351, align 4
  %1353 = fsub reassoc ninf nsz float %1348, %1352
  %1354 = tail call noundef float @llvm.fabs.f32(float %1353)
  %1355 = fadd reassoc ninf nsz float %1354, %1344
  %1356 = add i64 %1323, 3
  %tmp615 = trunc i64 %1356 to i32
  %1357 = sext i32 %tmp615 to i64
  %1358 = getelementptr float, ptr %1243, i64 %1357
  %1359 = load float, ptr %1358, align 4
  %1360 = add i64 %1327, 3
  %tmp614 = trunc i64 %1360 to i32
  %1361 = sext i32 %tmp614 to i64
  %1362 = getelementptr float, ptr %1245, i64 %1361
  %1363 = load float, ptr %1362, align 4
  %1364 = fsub reassoc ninf nsz float %1359, %1363
  %1365 = tail call noundef float @llvm.fabs.f32(float %1364)
  %1366 = fadd reassoc ninf nsz float %1365, %1355
  %indvars.iv.next109.3 = add nuw nsw i64 %indvars.iv108, 4
  %exitcond112.not.3 = icmp eq i64 %wide.trip.count111, %indvars.iv.next109.3
  br i1 %exitcond112.not.3, label %for_loop_test61.after_for60_crit_edge.us.loopexit, label %for_loop_body58.us, !llvm.loop !20

for_loop_test61.after_for60_crit_edge.us.loopexit: ; preds = %for_loop_body58.us
  br label %for_loop_test61.after_for60_crit_edge.us

for_loop_test61.after_for60_crit_edge.us:         ; preds = %for_loop_test61.after_for60_crit_edge.us.loopexit, %for_loop_body58.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa127 = phi float [ %1295, %middle.block ], [ %1309, %vec.epilog.middle.block ], [ %.lcssa487.unr, %for_loop_body58.us.prol.loopexit ], [ %1366, %for_loop_test61.after_for60_crit_edge.us.loopexit ]
  %1367 = add nuw nsw i32 %.03696.us, 1
  %lsr.iv.next610 = add i64 %lsr.iv609, %1261
  %lsr.iv.next608 = add i64 %lsr.iv607, %1259
  %exitcond114.not = icmp eq i32 %1367, %smax113
  br i1 %exitcond114.not, label %after_for56, label %iter.check

false_block52:                                    ; preds = %after_for6
  %1368 = fdiv reassoc ninf nsz float %.lcssa126, %.lcssa
  br label %after_if53

after_if53:                                       ; preds = %after_for56, %false_block52
  %.038 = phi float [ %1383, %after_for56 ], [ %1368, %false_block52 ]
  %1369 = getelementptr inbounds nuw i8, ptr %31, i64 16
  %1370 = load float, ptr %1369, align 4
  %1371 = fmul reassoc ninf nsz float %1370, %.038
  %1372 = getelementptr i8, ptr %59, i64 136
  %1373 = load float, ptr %1372, align 4
  %1374 = fsub reassoc ninf nsz float %1371, %1373
  %1375 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1374, float 0.000000e+00)
  %1376 = getelementptr i8, ptr %59, i64 132
  %1377 = load float, ptr %1376, align 4
  %1378 = fmul reassoc ninf nsz float %1377, 5.000000e-01
  %1379 = fmul reassoc ninf nsz float %1378, %1375
  %1380 = fcmp reassoc ninf nsz ugt float %1379, 2.000000e+01
  br i1 %1380, label %after_if3, label %true_block62

after_for56:                                      ; preds = %for_loop_test61.after_for60_crit_edge.us
  %1381 = mul i32 %42, %44
  %1382 = sitofp i32 %1381 to float
  %1383 = fdiv reassoc ninf nsz float %.lcssa127, %1382
  br label %after_if53

true_block62:                                     ; preds = %after_if53
  %1384 = fadd reassoc ninf nsz float %1379, -2.000000e+00
  %1385 = tail call noundef float @expf(float noundef %1384) #9
  %1386 = fadd reassoc ninf nsz float %1385, 1.000000e+00
  %1387 = fdiv reassoc ninf nsz float 1.000000e+00, %1386
  br label %after_if3
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
  %4 = alloca %struct.RuntimeContext.8, align 8
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
