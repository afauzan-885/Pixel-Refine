; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_collaborative_dct_filter_kernel_c432_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = getelementptr i8, ptr %0, i64 120
  %2 = load float, ptr %1, align 4
  %3 = getelementptr i8, ptr %0, i64 116
  %4 = load float, ptr %3, align 4
  %5 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %6 = load ptr, ptr %5, align 8
  %7 = getelementptr inbounds nuw i8, ptr %6, i64 32872
  %8 = load ptr, ptr %7, align 8
  %9 = getelementptr inbounds nuw i8, ptr %8, i64 8
  store float %4, ptr %9, align 4
  %10 = fmul reassoc ninf nsz float %4, %2
  %11 = load ptr, ptr %5, align 8
  %12 = getelementptr inbounds nuw i8, ptr %11, i64 32872
  %13 = load ptr, ptr %12, align 8
  %14 = getelementptr inbounds nuw i8, ptr %13, i64 4
  store float %10, ptr %14, align 4
  %15 = load ptr, ptr %context, align 8
  %16 = getelementptr i8, ptr %15, i64 104
  %17 = load i32, ptr %16, align 4
  %18 = load ptr, ptr %5, align 8
  %19 = getelementptr inbounds nuw i8, ptr %18, i64 32872
  %20 = load ptr, ptr %19, align 8
  store i32 %17, ptr %20, align 4
  ret void
}

define void @_collaborative_dct_filter_kernel_c432_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
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
  %20 = getelementptr i8, ptr %19, i64 108
  %21 = load i32, ptr %20, align 4
  %22 = getelementptr i8, ptr %19, i64 112
  %23 = load i32, ptr %22, align 4
  %24 = icmp slt i32 %16, %18
  br i1 %24, label %for_loop_test4.preheader.lr.ph, label %after_for

for_loop_test4.preheader.lr.ph:                   ; preds = %allocs
  %25 = icmp sgt i32 %21, 0
  %26 = icmp sgt i32 %23, 0
  %27 = getelementptr i8, ptr %19, i64 72
  %28 = getelementptr i8, ptr %19, i64 68
  %29 = getelementptr i8, ptr %19, i64 16
  %30 = getelementptr i8, ptr %19, i64 4
  %31 = getelementptr i8, ptr %19, i64 8
  %32 = getelementptr i8, ptr %19, i64 12
  %33 = getelementptr i8, ptr %19, i64 96
  %34 = getelementptr i8, ptr %19, i64 84
  %35 = getelementptr i8, ptr %19, i64 88
  %36 = getelementptr i8, ptr %19, i64 92
  %37 = getelementptr i8, ptr %19, i64 40
  %38 = getelementptr i8, ptr %19, i64 28
  %39 = getelementptr i8, ptr %19, i64 32
  %40 = getelementptr i8, ptr %19, i64 36
  %41 = getelementptr i8, ptr %19, i64 56
  %42 = sext i32 %16 to i64
  %wide.trip.count136 = sext i32 %18 to i64
  br i1 %25, label %for_loop_test4.preheader.us.preheader, label %for_loop_test4.preheader.preheader

for_loop_test4.preheader.preheader:               ; preds = %for_loop_test4.preheader.lr.ph
  %43 = sub nsw i64 %wide.trip.count136, %42
  %xtraiter = and i64 %43, 3
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %for_loop_test4.preheader.prol.loopexit, label %for_loop_test4.preheader.prol.preheader

for_loop_test4.preheader.prol.preheader:          ; preds = %for_loop_test4.preheader.preheader
  br label %for_loop_test4.preheader.prol

for_loop_test4.preheader.prol:                    ; preds = %for_loop_test4.preheader.prol, %for_loop_test4.preheader.prol.preheader
  %lsr.iv534 = phi i64 [ %xtraiter, %for_loop_test4.preheader.prol.preheader ], [ %lsr.iv.next535, %for_loop_test4.preheader.prol ]
  %indvars.iv.prol = phi i64 [ %indvars.iv.next.prol, %for_loop_test4.preheader.prol ], [ %42, %for_loop_test4.preheader.prol.preheader ]
  %44 = load ptr, ptr %3, align 8
  %45 = getelementptr inbounds nuw i8, ptr %44, i64 32872
  %46 = load ptr, ptr %45, align 8
  %47 = getelementptr inbounds nuw i8, ptr %46, i64 8
  %48 = load float, ptr %47, align 4
  %49 = fmul reassoc ninf nsz float %48, %48
  %50 = fdiv reassoc ninf nsz float 1.000000e+00, %49
  %51 = load ptr, ptr %41, align 8
  %52 = shl nsw i64 %indvars.iv.prol, 2
  %scevgep533 = getelementptr i8, ptr %51, i64 %52
  store float %50, ptr %scevgep533, align 4
  %indvars.iv.next.prol = add nsw i64 %indvars.iv.prol, 1
  %lsr.iv.next535 = add nsw i64 %lsr.iv534, -1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next535, 0
  br i1 %prol.iter.cmp.not, label %for_loop_test4.preheader.prol.loopexit.loopexit, label %for_loop_test4.preheader.prol, !llvm.loop !10

for_loop_test4.preheader.prol.loopexit.loopexit:  ; preds = %for_loop_test4.preheader.prol
  br label %for_loop_test4.preheader.prol.loopexit

for_loop_test4.preheader.prol.loopexit:           ; preds = %for_loop_test4.preheader.prol.loopexit.loopexit, %for_loop_test4.preheader.preheader
  %indvars.iv.unr = phi i64 [ %42, %for_loop_test4.preheader.preheader ], [ %indvars.iv.next.prol, %for_loop_test4.preheader.prol.loopexit.loopexit ]
  %53 = sub nsw i64 %42, %wide.trip.count136
  %54 = icmp ugt i64 %53, -4
  br i1 %54, label %after_for, label %for_loop_test4.preheader.preheader413

for_loop_test4.preheader.preheader413:            ; preds = %for_loop_test4.preheader.prol.loopexit
  br label %for_loop_test4.preheader

for_loop_test4.preheader.us.preheader:            ; preds = %for_loop_test4.preheader.lr.ph
  %wide.trip.count107 = zext i32 %23 to i64
  %55 = add nsw i64 %wide.trip.count107, -1
  %min.iters.check264 = icmp ult i32 %23, 4
  %56 = trunc i64 %55 to i32
  %57 = icmp ugt i64 %55, 4294967295
  %min.iters.check267 = icmp ult i32 %23, 32
  %n.vec271 = and i64 %wide.trip.count107, 2147483616
  %cmp.n290 = icmp eq i64 %n.vec271, %wide.trip.count107
  %n.vec.remaining297 = and i64 %wide.trip.count107, 28
  %min.epilog.iters.check298 = icmp eq i64 %n.vec.remaining297, 0
  %n.vec300 = and i64 %wide.trip.count107, 2147483644
  %cmp.n307 = icmp eq i64 %n.vec300, %wide.trip.count107
  %xtraiter333 = and i64 %wide.trip.count107, 3
  %lcmp.mod334.not = icmp eq i64 %xtraiter333, 0
  %min.iters.check178 = icmp ult i32 %23, 16
  %n.vec182 = and i64 %wide.trip.count107, 2147483632
  %cmp.n193 = icmp eq i64 %n.vec182, %wide.trip.count107
  %n.vec.remaining200 = and i64 %wide.trip.count107, 12
  %min.epilog.iters.check201 = icmp eq i64 %n.vec.remaining200, 0
  %58 = lshr i64 %wide.trip.count107, 2
  %59 = trunc i64 %58 to i29
  %60 = zext i29 %59 to i64
  %61 = mul i64 %60, -4
  %62 = sub i64 0, %xtraiter333
  br label %for_loop_test4.preheader.us

for_loop_test4.preheader.us:                      ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_test4.preheader.us.preheader
  %indvars.iv133 = phi i64 [ %42, %for_loop_test4.preheader.us.preheader ], [ %indvars.iv.next134, %for_loop_test4.after_for3_crit_edge.us ]
  %lsr526 = trunc i64 %indvars.iv133 to i32
  br label %for_loop_test8.preheader.us

after_for43.us.loopexit:                          ; preds = %for_loop_test48.after_for47_crit_edge.split.us.us.us
  br label %after_for43.us

after_for43.us:                                   ; preds = %for_loop_test8.preheader.us, %after_for43.us.loopexit
  %.1.lcssa.us139 = phi i32 [ %.06996.us, %for_loop_test8.preheader.us ], [ %.3.us.us.us, %after_for43.us.loopexit ]
  %63 = add nuw nsw i32 %.06897.us, 1
  %exitcond132.not = icmp eq i32 %63, %21
  br i1 %exitcond132.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_test8.preheader.us

for_loop_test8.preheader.us:                      ; preds = %after_for43.us, %for_loop_test4.preheader.us
  %.06897.us = phi i32 [ 0, %for_loop_test4.preheader.us ], [ %63, %after_for43.us ]
  %.06996.us = phi i32 [ 0, %for_loop_test4.preheader.us ], [ %.1.lcssa.us139, %after_for43.us ]
  br i1 %26, label %for_loop_test12.preheader.us.us.preheader, label %after_for43.us

for_loop_test12.preheader.us.us.preheader:        ; preds = %for_loop_test8.preheader.us
  br label %for_loop_test12.preheader.us.us

for_loop_test12.preheader.us.us:                  ; preds = %for_loop_test12.after_for11_crit_edge.split.us.us.us, %for_loop_test12.preheader.us.us.preheader
  %.06776.us.us = phi i32 [ %198, %for_loop_test12.after_for11_crit_edge.split.us.us.us ], [ 0, %for_loop_test12.preheader.us.us.preheader ]
  br label %iter.check266

iter.check266:                                    ; preds = %for_loop_test16.after_for15_crit_edge.us.us.us, %for_loop_test12.preheader.us.us
  %.06675.us.us.us = phi i32 [ 0, %for_loop_test12.preheader.us.us ], [ %197, %for_loop_test16.after_for15_crit_edge.us.us.us ]
  %64 = load ptr, ptr %27, align 8
  %65 = load i32, ptr %28, align 4
  %66 = mul i32 %65, %.06776.us.us
  %67 = load ptr, ptr %29, align 8
  %68 = load i32, ptr %30, align 4
  %69 = load i32, ptr %31, align 4
  %70 = load i32, ptr %32, align 4
  %71 = mul i32 %68, %lsr526
  %72 = add i32 %71, %.06897.us
  %73 = mul i32 %72, %69
  br i1 %min.iters.check264, label %for_loop_body13.us.us.us.preheader, label %vector.scevcheck261

vector.scevcheck261:                              ; preds = %iter.check266
  %74 = add i32 %66, %56
  %75 = icmp slt i32 %74, %66
  %76 = or i1 %75, %57
  %ident.check262 = icmp ne i32 %70, 1
  %77 = add i32 %.06675.us.us.us, %73
  %78 = add i32 %77, %56
  %79 = icmp slt i32 %78, %77
  %80 = or i1 %76, %ident.check262
  %81 = or i1 %79, %80
  br i1 %81, label %for_loop_body13.us.us.us.preheader, label %vector.main.loop.iter.check268

vector.main.loop.iter.check268:                   ; preds = %vector.scevcheck261
  br i1 %min.iters.check267, label %vec.epilog.ph295, label %vector.ph269

vector.ph269:                                     ; preds = %vector.main.loop.iter.check268
  br label %vector.body272

vector.body272:                                   ; preds = %vector.body272, %vector.ph269
  %lsr.iv419 = phi i32 [ %lsr.iv.next420, %vector.body272 ], [ %66, %vector.ph269 ]
  %lsr.iv417 = phi i32 [ %lsr.iv.next418, %vector.body272 ], [ %77, %vector.ph269 ]
  %lsr.iv = phi i64 [ %lsr.iv.next, %vector.body272 ], [ %n.vec271, %vector.ph269 ]
  %vec.phi274 = phi <8 x float> [ zeroinitializer, %vector.ph269 ], [ %96, %vector.body272 ]
  %vec.phi275 = phi <8 x float> [ zeroinitializer, %vector.ph269 ], [ %97, %vector.body272 ]
  %vec.phi276 = phi <8 x float> [ zeroinitializer, %vector.ph269 ], [ %98, %vector.body272 ]
  %vec.phi277 = phi <8 x float> [ zeroinitializer, %vector.ph269 ], [ %99, %vector.body272 ]
  %82 = sext i32 %lsr.iv419 to i64
  %83 = getelementptr float, ptr %64, i64 %82
  %84 = getelementptr i8, ptr %83, i64 32
  %85 = getelementptr i8, ptr %83, i64 64
  %86 = getelementptr i8, ptr %83, i64 96
  %wide.load278 = load <8 x float>, ptr %83, align 4
  %wide.load279 = load <8 x float>, ptr %84, align 4
  %wide.load280 = load <8 x float>, ptr %85, align 4
  %wide.load281 = load <8 x float>, ptr %86, align 4
  %87 = sext i32 %lsr.iv417 to i64
  %88 = getelementptr float, ptr %67, i64 %87
  %89 = getelementptr i8, ptr %88, i64 32
  %90 = getelementptr i8, ptr %88, i64 64
  %91 = getelementptr i8, ptr %88, i64 96
  %wide.load282 = load <8 x float>, ptr %88, align 4
  %wide.load283 = load <8 x float>, ptr %89, align 4
  %wide.load284 = load <8 x float>, ptr %90, align 4
  %wide.load285 = load <8 x float>, ptr %91, align 4
  %92 = fmul reassoc ninf nsz <8 x float> %wide.load282, %wide.load278
  %93 = fmul reassoc ninf nsz <8 x float> %wide.load283, %wide.load279
  %94 = fmul reassoc ninf nsz <8 x float> %wide.load284, %wide.load280
  %95 = fmul reassoc ninf nsz <8 x float> %wide.load285, %wide.load281
  %96 = fadd reassoc ninf nsz <8 x float> %92, %vec.phi274
  %97 = fadd reassoc ninf nsz <8 x float> %93, %vec.phi275
  %98 = fadd reassoc ninf nsz <8 x float> %94, %vec.phi276
  %99 = fadd reassoc ninf nsz <8 x float> %95, %vec.phi277
  %lsr.iv.next = add nsw i64 %lsr.iv, -32
  %lsr.iv.next418 = add i32 %lsr.iv417, 32
  %lsr.iv.next420 = add i32 %lsr.iv419, 32
  %100 = icmp eq i64 %lsr.iv.next, 0
  br i1 %100, label %middle.block263, label %vector.body272, !llvm.loop !12

middle.block263:                                  ; preds = %vector.body272
  %bin.rdx287 = fadd reassoc ninf nsz <8 x float> %97, %96
  %bin.rdx288 = fadd reassoc ninf nsz <8 x float> %98, %bin.rdx287
  %bin.rdx289 = fadd reassoc ninf nsz <8 x float> %99, %bin.rdx288
  %101 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx289)
  br i1 %cmp.n290, label %for_loop_test16.after_for15_crit_edge.us.us.us, label %vec.epilog.iter.check296

vec.epilog.iter.check296:                         ; preds = %middle.block263
  br i1 %min.epilog.iters.check298, label %for_loop_body13.us.us.us.preheader, label %vec.epilog.ph295

vec.epilog.ph295:                                 ; preds = %vec.epilog.iter.check296, %vector.main.loop.iter.check268
  %vec.epilog.resume.val291 = phi i64 [ %n.vec271, %vec.epilog.iter.check296 ], [ 0, %vector.main.loop.iter.check268 ]
  %bc.merge.rdx292 = phi float [ %101, %vec.epilog.iter.check296 ], [ 0.000000e+00, %vector.main.loop.iter.check268 ]
  %102 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx292, i64 0
  %103 = add i64 %61, %vec.epilog.resume.val291
  %104 = trunc i64 %vec.epilog.resume.val291 to i32
  %105 = add i32 %77, %104
  %106 = add i32 %66, %104
  br label %vec.epilog.vector.body301

vec.epilog.vector.body301:                        ; preds = %vec.epilog.vector.body301, %vec.epilog.ph295
  %lsr.iv425 = phi i32 [ %lsr.iv.next426, %vec.epilog.vector.body301 ], [ %106, %vec.epilog.ph295 ]
  %lsr.iv423 = phi i32 [ %lsr.iv.next424, %vec.epilog.vector.body301 ], [ %105, %vec.epilog.ph295 ]
  %lsr.iv421 = phi i64 [ %lsr.iv.next422, %vec.epilog.vector.body301 ], [ %103, %vec.epilog.ph295 ]
  %vec.phi303 = phi <4 x float> [ %102, %vec.epilog.ph295 ], [ %112, %vec.epilog.vector.body301 ]
  %107 = sext i32 %lsr.iv425 to i64
  %108 = getelementptr float, ptr %64, i64 %107
  %wide.load304 = load <4 x float>, ptr %108, align 4
  %109 = sext i32 %lsr.iv423 to i64
  %110 = getelementptr float, ptr %67, i64 %109
  %wide.load305 = load <4 x float>, ptr %110, align 4
  %111 = fmul reassoc ninf nsz <4 x float> %wide.load305, %wide.load304
  %112 = fadd reassoc ninf nsz <4 x float> %111, %vec.phi303
  %lsr.iv.next422 = add i64 %lsr.iv421, 4
  %lsr.iv.next424 = add i32 %lsr.iv423, 4
  %lsr.iv.next426 = add i32 %lsr.iv425, 4
  %113 = icmp eq i64 %lsr.iv.next422, 0
  br i1 %113, label %vec.epilog.middle.block293, label %vec.epilog.vector.body301, !llvm.loop !15

vec.epilog.middle.block293:                       ; preds = %vec.epilog.vector.body301
  %114 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %112)
  br i1 %cmp.n307, label %for_loop_test16.after_for15_crit_edge.us.us.us, label %for_loop_body13.us.us.us.preheader

for_loop_body13.us.us.us.preheader:               ; preds = %vec.epilog.middle.block293, %vec.epilog.iter.check296, %vector.scevcheck261, %iter.check266
  %indvars.iv104.ph = phi i64 [ %n.vec271, %vec.epilog.iter.check296 ], [ 0, %iter.check266 ], [ 0, %vector.scevcheck261 ], [ %n.vec300, %vec.epilog.middle.block293 ]
  %.06573.us.us.us.ph = phi float [ %101, %vec.epilog.iter.check296 ], [ 0.000000e+00, %iter.check266 ], [ 0.000000e+00, %vector.scevcheck261 ], [ %114, %vec.epilog.middle.block293 ]
  br i1 %lcmp.mod334.not, label %for_loop_body13.us.us.us.prol.loopexit, label %for_loop_body13.us.us.us.prol.preheader

for_loop_body13.us.us.us.prol.preheader:          ; preds = %for_loop_body13.us.us.us.preheader
  %115 = trunc i64 %indvars.iv104.ph to i32
  %116 = add i32 %73, %115
  %117 = mul i32 %70, %116
  %118 = add i32 %.06675.us.us.us, %117
  %119 = zext i32 %66 to i64
  br label %for_loop_body13.us.us.us.prol

for_loop_body13.us.us.us.prol:                    ; preds = %for_loop_body13.us.us.us.prol, %for_loop_body13.us.us.us.prol.preheader
  %lsr.iv429 = phi i64 [ %xtraiter333, %for_loop_body13.us.us.us.prol.preheader ], [ %lsr.iv.next430, %for_loop_body13.us.us.us.prol ]
  %lsr.iv427 = phi i32 [ %118, %for_loop_body13.us.us.us.prol.preheader ], [ %lsr.iv.next428, %for_loop_body13.us.us.us.prol ]
  %indvars.iv104.prol = phi i64 [ %indvars.iv.next105.prol, %for_loop_body13.us.us.us.prol ], [ %indvars.iv104.ph, %for_loop_body13.us.us.us.prol.preheader ]
  %.06573.us.us.us.prol = phi float [ %128, %for_loop_body13.us.us.us.prol ], [ %.06573.us.us.us.ph, %for_loop_body13.us.us.us.prol.preheader ]
  %120 = add i64 %119, %indvars.iv104.prol
  %tmp = trunc i64 %120 to i32
  %121 = sext i32 %tmp to i64
  %122 = getelementptr float, ptr %64, i64 %121
  %123 = load float, ptr %122, align 4
  %124 = sext i32 %lsr.iv427 to i64
  %125 = getelementptr float, ptr %67, i64 %124
  %126 = load float, ptr %125, align 4
  %127 = fmul reassoc ninf nsz float %126, %123
  %128 = fadd reassoc ninf nsz float %127, %.06573.us.us.us.prol
  %indvars.iv.next105.prol = add nuw nsw i64 %indvars.iv104.prol, 1
  %lsr.iv.next428 = add i32 %lsr.iv427, %70
  %lsr.iv.next430 = add nsw i64 %lsr.iv429, -1
  %prol.iter335.cmp.not = icmp eq i64 %lsr.iv.next430, 0
  br i1 %prol.iter335.cmp.not, label %for_loop_body13.us.us.us.prol.loopexit.loopexit, label %for_loop_body13.us.us.us.prol, !llvm.loop !16

for_loop_body13.us.us.us.prol.loopexit.loopexit:  ; preds = %for_loop_body13.us.us.us.prol
  br label %for_loop_body13.us.us.us.prol.loopexit

for_loop_body13.us.us.us.prol.loopexit:           ; preds = %for_loop_body13.us.us.us.prol.loopexit.loopexit, %for_loop_body13.us.us.us.preheader
  %.lcssa315.unr = phi float [ poison, %for_loop_body13.us.us.us.preheader ], [ %128, %for_loop_body13.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv104.unr = phi i64 [ %indvars.iv104.ph, %for_loop_body13.us.us.us.preheader ], [ %indvars.iv.next105.prol, %for_loop_body13.us.us.us.prol.loopexit.loopexit ]
  %.06573.us.us.us.unr = phi float [ %.06573.us.us.us.ph, %for_loop_body13.us.us.us.preheader ], [ %128, %for_loop_body13.us.us.us.prol.loopexit.loopexit ]
  %129 = sub nsw i64 %indvars.iv104.ph, %wide.trip.count107
  %130 = icmp ugt i64 %129, -4
  br i1 %130, label %for_loop_test16.after_for15_crit_edge.us.us.us, label %for_loop_body13.us.us.us.preheader.new

for_loop_body13.us.us.us.preheader.new:           ; preds = %for_loop_body13.us.us.us.prol.loopexit
  %131 = add i32 %73, 3
  %132 = trunc i64 %indvars.iv104.unr to i32
  %133 = add i32 %131, %132
  %134 = mul i32 %70, %133
  %135 = add i32 %.06675.us.us.us, %134
  %136 = shl i32 %70, 2
  %137 = zext i32 %66 to i64
  %138 = add i32 %73, 2
  %139 = add i32 %138, %132
  %140 = mul i32 %70, %139
  %141 = add i32 %.06675.us.us.us, %140
  %142 = add i32 %73, 1
  %143 = add i32 %142, %132
  %144 = mul i32 %70, %143
  %145 = add i32 %.06675.us.us.us, %144
  %146 = add i32 %73, %132
  %147 = mul i32 %70, %146
  %148 = add i32 %.06675.us.us.us, %147
  br label %for_loop_body13.us.us.us

for_loop_body13.us.us.us:                         ; preds = %for_loop_body13.us.us.us, %for_loop_body13.us.us.us.preheader.new
  %lsr.iv440 = phi i32 [ %lsr.iv.next441, %for_loop_body13.us.us.us ], [ %148, %for_loop_body13.us.us.us.preheader.new ]
  %lsr.iv437 = phi i32 [ %lsr.iv.next438, %for_loop_body13.us.us.us ], [ %145, %for_loop_body13.us.us.us.preheader.new ]
  %lsr.iv434 = phi i32 [ %lsr.iv.next435, %for_loop_body13.us.us.us ], [ %141, %for_loop_body13.us.us.us.preheader.new ]
  %lsr.iv431 = phi i32 [ %lsr.iv.next432, %for_loop_body13.us.us.us ], [ %135, %for_loop_body13.us.us.us.preheader.new ]
  %indvars.iv104 = phi i64 [ %indvars.iv104.unr, %for_loop_body13.us.us.us.preheader.new ], [ %indvars.iv.next105.3, %for_loop_body13.us.us.us ]
  %.06573.us.us.us = phi float [ %.06573.us.us.us.unr, %for_loop_body13.us.us.us.preheader.new ], [ %184, %for_loop_body13.us.us.us ]
  %149 = add i64 %137, %indvars.iv104
  %tmp442 = trunc i64 %149 to i32
  %150 = sext i32 %tmp442 to i64
  %151 = getelementptr float, ptr %64, i64 %150
  %152 = load float, ptr %151, align 4
  %153 = sext i32 %lsr.iv440 to i64
  %154 = getelementptr float, ptr %67, i64 %153
  %155 = load float, ptr %154, align 4
  %156 = fmul reassoc ninf nsz float %155, %152
  %157 = fadd reassoc ninf nsz float %156, %.06573.us.us.us
  %158 = add i64 %149, 1
  %tmp439 = trunc i64 %158 to i32
  %159 = sext i32 %tmp439 to i64
  %160 = getelementptr float, ptr %64, i64 %159
  %161 = load float, ptr %160, align 4
  %162 = sext i32 %lsr.iv437 to i64
  %163 = getelementptr float, ptr %67, i64 %162
  %164 = load float, ptr %163, align 4
  %165 = fmul reassoc ninf nsz float %164, %161
  %166 = fadd reassoc ninf nsz float %165, %157
  %167 = add i64 %149, 2
  %tmp436 = trunc i64 %167 to i32
  %168 = sext i32 %tmp436 to i64
  %169 = getelementptr float, ptr %64, i64 %168
  %170 = load float, ptr %169, align 4
  %171 = sext i32 %lsr.iv434 to i64
  %172 = getelementptr float, ptr %67, i64 %171
  %173 = load float, ptr %172, align 4
  %174 = fmul reassoc ninf nsz float %173, %170
  %175 = fadd reassoc ninf nsz float %174, %166
  %176 = add i64 %149, 3
  %tmp433 = trunc i64 %176 to i32
  %177 = sext i32 %tmp433 to i64
  %178 = getelementptr float, ptr %64, i64 %177
  %179 = load float, ptr %178, align 4
  %180 = sext i32 %lsr.iv431 to i64
  %181 = getelementptr float, ptr %67, i64 %180
  %182 = load float, ptr %181, align 4
  %183 = fmul reassoc ninf nsz float %182, %179
  %184 = fadd reassoc ninf nsz float %183, %175
  %indvars.iv.next105.3 = add nuw nsw i64 %indvars.iv104, 4
  %lsr.iv.next432 = add i32 %lsr.iv431, %136
  %lsr.iv.next435 = add i32 %lsr.iv434, %136
  %lsr.iv.next438 = add i32 %lsr.iv437, %136
  %lsr.iv.next441 = add i32 %lsr.iv440, %136
  %exitcond108.not.3 = icmp eq i64 %wide.trip.count107, %indvars.iv.next105.3
  br i1 %exitcond108.not.3, label %for_loop_test16.after_for15_crit_edge.us.us.us.loopexit, label %for_loop_body13.us.us.us, !llvm.loop !17

for_loop_test16.after_for15_crit_edge.us.us.us.loopexit: ; preds = %for_loop_body13.us.us.us
  br label %for_loop_test16.after_for15_crit_edge.us.us.us

for_loop_test16.after_for15_crit_edge.us.us.us:   ; preds = %for_loop_test16.after_for15_crit_edge.us.us.us.loopexit, %for_loop_body13.us.us.us.prol.loopexit, %vec.epilog.middle.block293, %middle.block263
  %.lcssa = phi float [ %101, %middle.block263 ], [ %114, %vec.epilog.middle.block293 ], [ %.lcssa315.unr, %for_loop_body13.us.us.us.prol.loopexit ], [ %184, %for_loop_test16.after_for15_crit_edge.us.us.us.loopexit ]
  %185 = load ptr, ptr %33, align 8
  %186 = load i32, ptr %34, align 4
  %187 = load i32, ptr %35, align 4
  %188 = load i32, ptr %36, align 4
  %189 = mul i32 %186, %lsr526
  %190 = add i32 %189, %.06897.us
  %191 = mul i32 %190, %187
  %192 = add i32 %191, %.06776.us.us
  %193 = mul i32 %192, %188
  %194 = add i32 %193, %.06675.us.us.us
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, ptr %185, i64 %195
  store float %.lcssa, ptr %196, align 4
  %197 = add nuw nsw i32 %.06675.us.us.us, 1
  %exitcond109.not = icmp eq i32 %197, %23
  br i1 %exitcond109.not, label %for_loop_test12.after_for11_crit_edge.split.us.us.us, label %iter.check266

for_loop_test12.after_for11_crit_edge.split.us.us.us: ; preds = %for_loop_test16.after_for15_crit_edge.us.us.us
  %198 = add nuw nsw i32 %.06776.us.us, 1
  %exitcond110.not = icmp eq i32 %198, %23
  br i1 %exitcond110.not, label %for_loop_test24.preheader.us.us.preheader, label %for_loop_test12.preheader.us.us

for_loop_test24.preheader.us.us.preheader:        ; preds = %for_loop_test12.after_for11_crit_edge.split.us.us.us
  br label %for_loop_test24.preheader.us.us

for_loop_test24.preheader.us.us:                  ; preds = %for_loop_test24.after_for23_crit_edge.split.us.us.us, %for_loop_test24.preheader.us.us.preheader
  %.06383.us.us = phi i32 [ %327, %for_loop_test24.after_for23_crit_edge.split.us.us.us ], [ 0, %for_loop_test24.preheader.us.us.preheader ]
  %.182.us.us = phi i32 [ %.3.us.us.us, %for_loop_test24.after_for23_crit_edge.split.us.us.us ], [ %.06996.us, %for_loop_test24.preheader.us.us.preheader ]
  br label %iter.check217

iter.check217:                                    ; preds = %after_if.us.us.us, %for_loop_test24.preheader.us.us
  %.06280.us.us.us = phi i32 [ 0, %for_loop_test24.preheader.us.us ], [ %267, %after_if.us.us.us ]
  %.279.us.us.us = phi i32 [ %.182.us.us, %for_loop_test24.preheader.us.us ], [ %.3.us.us.us, %after_if.us.us.us ]
  %199 = load ptr, ptr %33, align 8
  %200 = load i32, ptr %34, align 4
  %201 = load i32, ptr %35, align 4
  %202 = load i32, ptr %36, align 4
  %203 = mul i32 %200, %lsr526
  %204 = add i32 %203, %.06897.us
  %205 = mul i32 %204, %201
  %206 = add i32 %205, %.06383.us.us
  %207 = mul i32 %206, %202
  %208 = load ptr, ptr %27, align 8
  %209 = load i32, ptr %28, align 4
  %210 = mul i32 %209, %.06280.us.us.us
  br i1 %min.iters.check264, label %for_loop_body25.us.us.us.preheader, label %vector.scevcheck213

for_loop_body25.us.us.us.preheader:               ; preds = %vec.epilog.middle.block244, %vec.epilog.iter.check247, %vector.scevcheck213, %iter.check217
  %indvars.iv111.ph = phi i64 [ %n.vec271, %vec.epilog.iter.check247 ], [ 0, %iter.check217 ], [ 0, %vector.scevcheck213 ], [ %n.vec300, %vec.epilog.middle.block244 ]
  %.06177.us.us.us.ph = phi float [ %252, %vec.epilog.iter.check247 ], [ 0.000000e+00, %iter.check217 ], [ 0.000000e+00, %vector.scevcheck213 ], [ %265, %vec.epilog.middle.block244 ]
  br i1 %lcmp.mod334.not, label %for_loop_body25.us.us.us.prol.loopexit, label %for_loop_body25.us.us.us.prol.preheader

for_loop_body25.us.us.us.prol.preheader:          ; preds = %for_loop_body25.us.us.us.preheader
  %211 = zext i32 %210 to i64
  %212 = zext i32 %207 to i64
  br label %for_loop_body25.us.us.us.prol

for_loop_body25.us.us.us.prol:                    ; preds = %for_loop_body25.us.us.us.prol, %for_loop_body25.us.us.us.prol.preheader
  %lsr.iv457 = phi i64 [ %xtraiter333, %for_loop_body25.us.us.us.prol.preheader ], [ %lsr.iv.next458, %for_loop_body25.us.us.us.prol ]
  %indvars.iv111.prol = phi i64 [ %indvars.iv.next112.prol, %for_loop_body25.us.us.us.prol ], [ %indvars.iv111.ph, %for_loop_body25.us.us.us.prol.preheader ]
  %.06177.us.us.us.prol = phi float [ %222, %for_loop_body25.us.us.us.prol ], [ %.06177.us.us.us.ph, %for_loop_body25.us.us.us.prol.preheader ]
  %213 = add i64 %212, %indvars.iv111.prol
  %tmp456 = trunc i64 %213 to i32
  %214 = sext i32 %tmp456 to i64
  %215 = getelementptr float, ptr %199, i64 %214
  %216 = load float, ptr %215, align 4
  %217 = add i64 %211, %indvars.iv111.prol
  %tmp455 = trunc i64 %217 to i32
  %218 = sext i32 %tmp455 to i64
  %219 = getelementptr float, ptr %208, i64 %218
  %220 = load float, ptr %219, align 4
  %221 = fmul reassoc ninf nsz float %220, %216
  %222 = fadd reassoc ninf nsz float %221, %.06177.us.us.us.prol
  %indvars.iv.next112.prol = add nuw nsw i64 %indvars.iv111.prol, 1
  %lsr.iv.next458 = add nsw i64 %lsr.iv457, -1
  %prol.iter338.cmp.not = icmp eq i64 %lsr.iv.next458, 0
  br i1 %prol.iter338.cmp.not, label %for_loop_body25.us.us.us.prol.loopexit.loopexit, label %for_loop_body25.us.us.us.prol, !llvm.loop !18

for_loop_body25.us.us.us.prol.loopexit.loopexit:  ; preds = %for_loop_body25.us.us.us.prol
  br label %for_loop_body25.us.us.us.prol.loopexit

for_loop_body25.us.us.us.prol.loopexit:           ; preds = %for_loop_body25.us.us.us.prol.loopexit.loopexit, %for_loop_body25.us.us.us.preheader
  %.lcssa321.unr = phi float [ poison, %for_loop_body25.us.us.us.preheader ], [ %222, %for_loop_body25.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv111.unr = phi i64 [ %indvars.iv111.ph, %for_loop_body25.us.us.us.preheader ], [ %indvars.iv.next112.prol, %for_loop_body25.us.us.us.prol.loopexit.loopexit ]
  %.06177.us.us.us.unr = phi float [ %.06177.us.us.us.ph, %for_loop_body25.us.us.us.preheader ], [ %222, %for_loop_body25.us.us.us.prol.loopexit.loopexit ]
  %223 = sub nsw i64 %indvars.iv111.ph, %wide.trip.count107
  %224 = icmp ugt i64 %223, -4
  br i1 %224, label %for_loop_test28.after_for27_crit_edge.us.us.us, label %for_loop_body25.us.us.us.preheader.new

for_loop_body25.us.us.us.preheader.new:           ; preds = %for_loop_body25.us.us.us.prol.loopexit
  %225 = zext i32 %210 to i64
  %226 = zext i32 %207 to i64
  br label %for_loop_body25.us.us.us

vector.scevcheck213:                              ; preds = %iter.check217
  %227 = add i32 %207, %56
  %228 = icmp slt i32 %227, %207
  %229 = add i32 %210, %56
  %230 = icmp slt i32 %229, %210
  %231 = or i1 %230, %57
  %232 = or i1 %228, %231
  br i1 %232, label %for_loop_body25.us.us.us.preheader, label %vector.main.loop.iter.check219

vector.main.loop.iter.check219:                   ; preds = %vector.scevcheck213
  br i1 %min.iters.check267, label %vec.epilog.ph246, label %vector.body223.preheader

vector.body223.preheader:                         ; preds = %vector.main.loop.iter.check219
  br label %vector.body223

vector.body223:                                   ; preds = %vector.body223, %vector.body223.preheader
  %lsr.iv447 = phi i32 [ %210, %vector.body223.preheader ], [ %lsr.iv.next448, %vector.body223 ]
  %lsr.iv445 = phi i32 [ %207, %vector.body223.preheader ], [ %lsr.iv.next446, %vector.body223 ]
  %lsr.iv443 = phi i64 [ %n.vec271, %vector.body223.preheader ], [ %lsr.iv.next444, %vector.body223 ]
  %vec.phi225 = phi <8 x float> [ %247, %vector.body223 ], [ zeroinitializer, %vector.body223.preheader ]
  %vec.phi226 = phi <8 x float> [ %248, %vector.body223 ], [ zeroinitializer, %vector.body223.preheader ]
  %vec.phi227 = phi <8 x float> [ %249, %vector.body223 ], [ zeroinitializer, %vector.body223.preheader ]
  %vec.phi228 = phi <8 x float> [ %250, %vector.body223 ], [ zeroinitializer, %vector.body223.preheader ]
  %233 = sext i32 %lsr.iv445 to i64
  %234 = getelementptr float, ptr %199, i64 %233
  %235 = getelementptr i8, ptr %234, i64 32
  %236 = getelementptr i8, ptr %234, i64 64
  %237 = getelementptr i8, ptr %234, i64 96
  %wide.load229 = load <8 x float>, ptr %234, align 4
  %wide.load230 = load <8 x float>, ptr %235, align 4
  %wide.load231 = load <8 x float>, ptr %236, align 4
  %wide.load232 = load <8 x float>, ptr %237, align 4
  %238 = sext i32 %lsr.iv447 to i64
  %239 = getelementptr float, ptr %208, i64 %238
  %240 = getelementptr i8, ptr %239, i64 32
  %241 = getelementptr i8, ptr %239, i64 64
  %242 = getelementptr i8, ptr %239, i64 96
  %wide.load233 = load <8 x float>, ptr %239, align 4
  %wide.load234 = load <8 x float>, ptr %240, align 4
  %wide.load235 = load <8 x float>, ptr %241, align 4
  %wide.load236 = load <8 x float>, ptr %242, align 4
  %243 = fmul reassoc ninf nsz <8 x float> %wide.load233, %wide.load229
  %244 = fmul reassoc ninf nsz <8 x float> %wide.load234, %wide.load230
  %245 = fmul reassoc ninf nsz <8 x float> %wide.load235, %wide.load231
  %246 = fmul reassoc ninf nsz <8 x float> %wide.load236, %wide.load232
  %247 = fadd reassoc ninf nsz <8 x float> %243, %vec.phi225
  %248 = fadd reassoc ninf nsz <8 x float> %244, %vec.phi226
  %249 = fadd reassoc ninf nsz <8 x float> %245, %vec.phi227
  %250 = fadd reassoc ninf nsz <8 x float> %246, %vec.phi228
  %lsr.iv.next444 = add nsw i64 %lsr.iv443, -32
  %lsr.iv.next446 = add i32 %lsr.iv445, 32
  %lsr.iv.next448 = add i32 %lsr.iv447, 32
  %251 = icmp eq i64 %lsr.iv.next444, 0
  br i1 %251, label %middle.block214, label %vector.body223, !llvm.loop !19

middle.block214:                                  ; preds = %vector.body223
  %bin.rdx238 = fadd reassoc ninf nsz <8 x float> %248, %247
  %bin.rdx239 = fadd reassoc ninf nsz <8 x float> %249, %bin.rdx238
  %bin.rdx240 = fadd reassoc ninf nsz <8 x float> %250, %bin.rdx239
  %252 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx240)
  br i1 %cmp.n290, label %for_loop_test28.after_for27_crit_edge.us.us.us, label %vec.epilog.iter.check247

vec.epilog.iter.check247:                         ; preds = %middle.block214
  br i1 %min.epilog.iters.check298, label %for_loop_body25.us.us.us.preheader, label %vec.epilog.ph246

vec.epilog.ph246:                                 ; preds = %vec.epilog.iter.check247, %vector.main.loop.iter.check219
  %vec.epilog.resume.val242 = phi i64 [ %n.vec271, %vec.epilog.iter.check247 ], [ 0, %vector.main.loop.iter.check219 ]
  %bc.merge.rdx243 = phi float [ %252, %vec.epilog.iter.check247 ], [ 0.000000e+00, %vector.main.loop.iter.check219 ]
  %253 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx243, i64 0
  %254 = add i64 %61, %vec.epilog.resume.val242
  %255 = trunc i64 %vec.epilog.resume.val242 to i32
  %256 = add i32 %207, %255
  %257 = add i32 %210, %255
  br label %vec.epilog.vector.body252

vec.epilog.vector.body252:                        ; preds = %vec.epilog.vector.body252, %vec.epilog.ph246
  %lsr.iv453 = phi i32 [ %lsr.iv.next454, %vec.epilog.vector.body252 ], [ %257, %vec.epilog.ph246 ]
  %lsr.iv451 = phi i32 [ %lsr.iv.next452, %vec.epilog.vector.body252 ], [ %256, %vec.epilog.ph246 ]
  %lsr.iv449 = phi i64 [ %lsr.iv.next450, %vec.epilog.vector.body252 ], [ %254, %vec.epilog.ph246 ]
  %vec.phi254 = phi <4 x float> [ %253, %vec.epilog.ph246 ], [ %263, %vec.epilog.vector.body252 ]
  %258 = sext i32 %lsr.iv451 to i64
  %259 = getelementptr float, ptr %199, i64 %258
  %wide.load255 = load <4 x float>, ptr %259, align 4
  %260 = sext i32 %lsr.iv453 to i64
  %261 = getelementptr float, ptr %208, i64 %260
  %wide.load256 = load <4 x float>, ptr %261, align 4
  %262 = fmul reassoc ninf nsz <4 x float> %wide.load256, %wide.load255
  %263 = fadd reassoc ninf nsz <4 x float> %262, %vec.phi254
  %lsr.iv.next450 = add i64 %lsr.iv449, 4
  %lsr.iv.next452 = add i32 %lsr.iv451, 4
  %lsr.iv.next454 = add i32 %lsr.iv453, 4
  %264 = icmp eq i64 %lsr.iv.next450, 0
  br i1 %264, label %vec.epilog.middle.block244, label %vec.epilog.vector.body252, !llvm.loop !20

vec.epilog.middle.block244:                       ; preds = %vec.epilog.vector.body252
  %265 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %263)
  br i1 %cmp.n307, label %for_loop_test28.after_for27_crit_edge.us.us.us, label %for_loop_body25.us.us.us.preheader

false_block.us.us.us:                             ; preds = %for_loop_test28.after_for27_crit_edge.us.us.us
  store float 0.000000e+00, ptr %326, align 4
  br label %after_if.us.us.us

true_block.us.us.us:                              ; preds = %for_loop_test28.after_for27_crit_edge.us.us.us
  store float %.lcssa146, ptr %326, align 4
  %266 = add i32 %.279.us.us.us, 1
  br label %after_if.us.us.us

after_if.us.us.us:                                ; preds = %true_block.us.us.us, %false_block.us.us.us
  %.3.us.us.us = phi i32 [ %266, %true_block.us.us.us ], [ %.279.us.us.us, %false_block.us.us.us ]
  %267 = add nuw nsw i32 %.06280.us.us.us, 1
  %exitcond116.not = icmp eq i32 %267, %23
  br i1 %exitcond116.not, label %for_loop_test24.after_for23_crit_edge.split.us.us.us, label %iter.check217

for_loop_body25.us.us.us:                         ; preds = %for_loop_body25.us.us.us, %for_loop_body25.us.us.us.preheader.new
  %indvars.iv111 = phi i64 [ %indvars.iv111.unr, %for_loop_body25.us.us.us.preheader.new ], [ %indvars.iv.next112.3, %for_loop_body25.us.us.us ]
  %.06177.us.us.us = phi float [ %.06177.us.us.us.unr, %for_loop_body25.us.us.us.preheader.new ], [ %307, %for_loop_body25.us.us.us ]
  %268 = add i64 %226, %indvars.iv111
  %tmp466 = trunc i64 %268 to i32
  %269 = sext i32 %tmp466 to i64
  %270 = getelementptr float, ptr %199, i64 %269
  %271 = load float, ptr %270, align 4
  %272 = add i64 %225, %indvars.iv111
  %tmp465 = trunc i64 %272 to i32
  %273 = sext i32 %tmp465 to i64
  %274 = getelementptr float, ptr %208, i64 %273
  %275 = load float, ptr %274, align 4
  %276 = fmul reassoc ninf nsz float %275, %271
  %277 = fadd reassoc ninf nsz float %276, %.06177.us.us.us
  %278 = add i64 %268, 1
  %tmp464 = trunc i64 %278 to i32
  %279 = sext i32 %tmp464 to i64
  %280 = getelementptr float, ptr %199, i64 %279
  %281 = load float, ptr %280, align 4
  %282 = add i64 %272, 1
  %tmp463 = trunc i64 %282 to i32
  %283 = sext i32 %tmp463 to i64
  %284 = getelementptr float, ptr %208, i64 %283
  %285 = load float, ptr %284, align 4
  %286 = fmul reassoc ninf nsz float %285, %281
  %287 = fadd reassoc ninf nsz float %286, %277
  %288 = add i64 %268, 2
  %tmp462 = trunc i64 %288 to i32
  %289 = sext i32 %tmp462 to i64
  %290 = getelementptr float, ptr %199, i64 %289
  %291 = load float, ptr %290, align 4
  %292 = add i64 %272, 2
  %tmp461 = trunc i64 %292 to i32
  %293 = sext i32 %tmp461 to i64
  %294 = getelementptr float, ptr %208, i64 %293
  %295 = load float, ptr %294, align 4
  %296 = fmul reassoc ninf nsz float %295, %291
  %297 = fadd reassoc ninf nsz float %296, %287
  %298 = add i64 %268, 3
  %tmp460 = trunc i64 %298 to i32
  %299 = sext i32 %tmp460 to i64
  %300 = getelementptr float, ptr %199, i64 %299
  %301 = load float, ptr %300, align 4
  %302 = add i64 %272, 3
  %tmp459 = trunc i64 %302 to i32
  %303 = sext i32 %tmp459 to i64
  %304 = getelementptr float, ptr %208, i64 %303
  %305 = load float, ptr %304, align 4
  %306 = fmul reassoc ninf nsz float %305, %301
  %307 = fadd reassoc ninf nsz float %306, %297
  %indvars.iv.next112.3 = add nuw nsw i64 %indvars.iv111, 4
  %exitcond115.not.3 = icmp eq i64 %wide.trip.count107, %indvars.iv.next112.3
  br i1 %exitcond115.not.3, label %for_loop_test28.after_for27_crit_edge.us.us.us.loopexit, label %for_loop_body25.us.us.us, !llvm.loop !21

for_loop_test28.after_for27_crit_edge.us.us.us.loopexit: ; preds = %for_loop_body25.us.us.us
  br label %for_loop_test28.after_for27_crit_edge.us.us.us

for_loop_test28.after_for27_crit_edge.us.us.us:   ; preds = %for_loop_test28.after_for27_crit_edge.us.us.us.loopexit, %vec.epilog.middle.block244, %middle.block214, %for_loop_body25.us.us.us.prol.loopexit
  %.lcssa146 = phi float [ %252, %middle.block214 ], [ %265, %vec.epilog.middle.block244 ], [ %.lcssa321.unr, %for_loop_body25.us.us.us.prol.loopexit ], [ %307, %for_loop_test28.after_for27_crit_edge.us.us.us.loopexit ]
  %308 = tail call noundef float @llvm.fabs.f32(float %.lcssa146)
  %309 = load ptr, ptr %3, align 8
  %310 = getelementptr inbounds nuw i8, ptr %309, i64 32872
  %311 = load ptr, ptr %310, align 8
  %312 = getelementptr inbounds nuw i8, ptr %311, i64 4
  %313 = load float, ptr %312, align 4
  %314 = fcmp reassoc ninf nsz ogt float %308, %313
  %315 = load ptr, ptr %29, align 8
  %316 = load i32, ptr %30, align 4
  %317 = load i32, ptr %31, align 4
  %318 = load i32, ptr %32, align 4
  %319 = mul i32 %316, %lsr526
  %320 = add i32 %319, %.06897.us
  %321 = mul i32 %320, %317
  %322 = add i32 %321, %.06383.us.us
  %323 = mul i32 %322, %318
  %324 = add i32 %323, %.06280.us.us.us
  %325 = sext i32 %324 to i64
  %326 = getelementptr float, ptr %315, i64 %325
  br i1 %314, label %true_block.us.us.us, label %false_block.us.us.us

for_loop_test24.after_for23_crit_edge.split.us.us.us: ; preds = %after_if.us.us.us
  %327 = add nuw nsw i32 %.06383.us.us, 1
  %exitcond117.not = icmp eq i32 %327, %23
  br i1 %exitcond117.not, label %for_loop_test36.preheader.us.us.preheader, label %for_loop_test24.preheader.us.us

for_loop_test36.preheader.us.us.preheader:        ; preds = %for_loop_test24.after_for23_crit_edge.split.us.us.us
  br label %for_loop_test36.preheader.us.us

for_loop_test36.preheader.us.us:                  ; preds = %for_loop_test36.after_for35_crit_edge.split.us.us.us, %for_loop_test36.preheader.us.us.preheader
  %.05990.us.us = phi i32 [ %463, %for_loop_test36.after_for35_crit_edge.split.us.us.us ], [ 0, %for_loop_test36.preheader.us.us.preheader ]
  %328 = add i32 %.05990.us.us, %56
  %329 = icmp slt i32 %328, %.05990.us.us
  %330 = or i1 %329, %57
  br label %iter.check177

iter.check177:                                    ; preds = %for_loop_test40.after_for39_crit_edge.us.us.us, %for_loop_test36.preheader.us.us
  %.05889.us.us.us = phi i32 [ 0, %for_loop_test36.preheader.us.us ], [ %462, %for_loop_test40.after_for39_crit_edge.us.us.us ]
  %331 = load ptr, ptr %27, align 8
  %332 = load i32, ptr %28, align 4
  %333 = load ptr, ptr %29, align 8
  %334 = load i32, ptr %30, align 4
  %335 = load i32, ptr %31, align 4
  %336 = load i32, ptr %32, align 4
  %337 = mul i32 %334, %lsr526
  %338 = add i32 %337, %.06897.us
  %339 = mul i32 %338, %335
  br i1 %min.iters.check264, label %for_loop_body37.us.us.us.preheader, label %vector.scevcheck171

vector.scevcheck171:                              ; preds = %iter.check177
  %ident.check172 = icmp ne i32 %332, 1
  %ident.check173 = icmp ne i32 %336, 1
  %340 = add i32 %.05889.us.us.us, %339
  %341 = add i32 %340, %56
  %342 = icmp slt i32 %341, %340
  %343 = or i1 %ident.check172, %330
  %344 = or i1 %343, %ident.check173
  %345 = or i1 %342, %344
  br i1 %345, label %for_loop_body37.us.us.us.preheader, label %vector.main.loop.iter.check179

vector.main.loop.iter.check179:                   ; preds = %vector.scevcheck171
  br i1 %min.iters.check178, label %vec.epilog.ph198, label %vector.ph180

vector.ph180:                                     ; preds = %vector.main.loop.iter.check179
  br label %vector.body183

vector.body183:                                   ; preds = %vector.body183, %vector.ph180
  %lsr.iv471 = phi i32 [ %lsr.iv.next472, %vector.body183 ], [ %.05990.us.us, %vector.ph180 ]
  %lsr.iv469 = phi i32 [ %lsr.iv.next470, %vector.body183 ], [ %340, %vector.ph180 ]
  %lsr.iv467 = phi i64 [ %lsr.iv.next468, %vector.body183 ], [ %n.vec182, %vector.ph180 ]
  %vec.phi185 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %354, %vector.body183 ]
  %vec.phi186 = phi <8 x float> [ zeroinitializer, %vector.ph180 ], [ %355, %vector.body183 ]
  %346 = sext i32 %lsr.iv471 to i64
  %347 = getelementptr float, ptr %331, i64 %346
  %348 = getelementptr i8, ptr %347, i64 32
  %wide.load187 = load <8 x float>, ptr %347, align 4
  %wide.load188 = load <8 x float>, ptr %348, align 4
  %349 = sext i32 %lsr.iv469 to i64
  %350 = getelementptr float, ptr %333, i64 %349
  %351 = getelementptr i8, ptr %350, i64 32
  %wide.load189 = load <8 x float>, ptr %350, align 4
  %wide.load190 = load <8 x float>, ptr %351, align 4
  %352 = fmul reassoc ninf nsz <8 x float> %wide.load189, %wide.load187
  %353 = fmul reassoc ninf nsz <8 x float> %wide.load190, %wide.load188
  %354 = fadd reassoc ninf nsz <8 x float> %352, %vec.phi185
  %355 = fadd reassoc ninf nsz <8 x float> %353, %vec.phi186
  %lsr.iv.next468 = add nsw i64 %lsr.iv467, -16
  %lsr.iv.next470 = add i32 %lsr.iv469, 16
  %lsr.iv.next472 = add nuw i32 %lsr.iv471, 16
  %356 = icmp eq i64 %lsr.iv.next468, 0
  br i1 %356, label %middle.block174, label %vector.body183, !llvm.loop !22

middle.block174:                                  ; preds = %vector.body183
  %bin.rdx192 = fadd reassoc ninf nsz <8 x float> %355, %354
  %357 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx192)
  br i1 %cmp.n193, label %for_loop_test40.after_for39_crit_edge.us.us.us, label %vec.epilog.iter.check199

vec.epilog.iter.check199:                         ; preds = %middle.block174
  br i1 %min.epilog.iters.check201, label %for_loop_body37.us.us.us.preheader, label %vec.epilog.ph198

vec.epilog.ph198:                                 ; preds = %vec.epilog.iter.check199, %vector.main.loop.iter.check179
  %vec.epilog.resume.val194 = phi i64 [ %n.vec182, %vec.epilog.iter.check199 ], [ 0, %vector.main.loop.iter.check179 ]
  %bc.merge.rdx195 = phi float [ %357, %vec.epilog.iter.check199 ], [ 0.000000e+00, %vector.main.loop.iter.check179 ]
  %358 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx195, i64 0
  %359 = add i64 %61, %vec.epilog.resume.val194
  %360 = trunc i64 %vec.epilog.resume.val194 to i32
  %361 = add i32 %340, %360
  %362 = add i32 %.05990.us.us, %360
  br label %vec.epilog.vector.body204

vec.epilog.vector.body204:                        ; preds = %vec.epilog.vector.body204, %vec.epilog.ph198
  %lsr.iv477 = phi i32 [ %lsr.iv.next478, %vec.epilog.vector.body204 ], [ %362, %vec.epilog.ph198 ]
  %lsr.iv475 = phi i32 [ %lsr.iv.next476, %vec.epilog.vector.body204 ], [ %361, %vec.epilog.ph198 ]
  %lsr.iv473 = phi i64 [ %lsr.iv.next474, %vec.epilog.vector.body204 ], [ %359, %vec.epilog.ph198 ]
  %vec.phi206 = phi <4 x float> [ %358, %vec.epilog.ph198 ], [ %368, %vec.epilog.vector.body204 ]
  %363 = sext i32 %lsr.iv477 to i64
  %364 = getelementptr float, ptr %331, i64 %363
  %wide.load207 = load <4 x float>, ptr %364, align 4
  %365 = sext i32 %lsr.iv475 to i64
  %366 = getelementptr float, ptr %333, i64 %365
  %wide.load208 = load <4 x float>, ptr %366, align 4
  %367 = fmul reassoc ninf nsz <4 x float> %wide.load208, %wide.load207
  %368 = fadd reassoc ninf nsz <4 x float> %367, %vec.phi206
  %lsr.iv.next474 = add i64 %lsr.iv473, 4
  %lsr.iv.next476 = add i32 %lsr.iv475, 4
  %lsr.iv.next478 = add i32 %lsr.iv477, 4
  %369 = icmp eq i64 %lsr.iv.next474, 0
  br i1 %369, label %vec.epilog.middle.block196, label %vec.epilog.vector.body204, !llvm.loop !23

vec.epilog.middle.block196:                       ; preds = %vec.epilog.vector.body204
  %370 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %368)
  br i1 %cmp.n307, label %for_loop_test40.after_for39_crit_edge.us.us.us, label %for_loop_body37.us.us.us.preheader

for_loop_body37.us.us.us.preheader:               ; preds = %vec.epilog.middle.block196, %vec.epilog.iter.check199, %vector.scevcheck171, %iter.check177
  %indvars.iv118.ph = phi i64 [ %n.vec182, %vec.epilog.iter.check199 ], [ 0, %iter.check177 ], [ 0, %vector.scevcheck171 ], [ %n.vec300, %vec.epilog.middle.block196 ]
  %.05786.us.us.us.ph = phi float [ %357, %vec.epilog.iter.check199 ], [ 0.000000e+00, %iter.check177 ], [ 0.000000e+00, %vector.scevcheck171 ], [ %370, %vec.epilog.middle.block196 ]
  br i1 %lcmp.mod334.not, label %for_loop_body37.us.us.us.prol.loopexit, label %for_loop_body37.us.us.us.prol.preheader

for_loop_body37.us.us.us.prol.preheader:          ; preds = %for_loop_body37.us.us.us.preheader
  %371 = trunc i64 %indvars.iv118.ph to i32
  %372 = add i32 %339, %371
  %373 = mul i32 %336, %372
  %374 = add i32 %.05889.us.us.us, %373
  %375 = mul i32 %332, %371
  %376 = add i32 %.05990.us.us, %375
  br label %for_loop_body37.us.us.us.prol

for_loop_body37.us.us.us.prol:                    ; preds = %for_loop_body37.us.us.us.prol, %for_loop_body37.us.us.us.prol.preheader
  %lsr.iv483 = phi i32 [ %376, %for_loop_body37.us.us.us.prol.preheader ], [ %lsr.iv.next484, %for_loop_body37.us.us.us.prol ]
  %lsr.iv481 = phi i32 [ %374, %for_loop_body37.us.us.us.prol.preheader ], [ %lsr.iv.next482, %for_loop_body37.us.us.us.prol ]
  %lsr.iv479 = phi i64 [ 0, %for_loop_body37.us.us.us.prol.preheader ], [ %lsr.iv.next480, %for_loop_body37.us.us.us.prol ]
  %.05786.us.us.us.prol = phi float [ %384, %for_loop_body37.us.us.us.prol ], [ %.05786.us.us.us.ph, %for_loop_body37.us.us.us.prol.preheader ]
  %377 = sext i32 %lsr.iv483 to i64
  %378 = getelementptr float, ptr %331, i64 %377
  %379 = load float, ptr %378, align 4
  %380 = sext i32 %lsr.iv481 to i64
  %381 = getelementptr float, ptr %333, i64 %380
  %382 = load float, ptr %381, align 4
  %383 = fmul reassoc ninf nsz float %382, %379
  %384 = fadd reassoc ninf nsz float %383, %.05786.us.us.us.prol
  %lsr.iv.next480 = add nsw i64 %lsr.iv479, -1
  %lsr.iv.next482 = add i32 %lsr.iv481, %336
  %lsr.iv.next484 = add i32 %lsr.iv483, %332
  %prol.iter341.cmp.not = icmp eq i64 %62, %lsr.iv.next480
  br i1 %prol.iter341.cmp.not, label %for_loop_body37.us.us.us.prol.loopexit.loopexit, label %for_loop_body37.us.us.us.prol, !llvm.loop !24

for_loop_body37.us.us.us.prol.loopexit.loopexit:  ; preds = %for_loop_body37.us.us.us.prol
  %385 = sub i64 %indvars.iv118.ph, %lsr.iv.next480
  br label %for_loop_body37.us.us.us.prol.loopexit

for_loop_body37.us.us.us.prol.loopexit:           ; preds = %for_loop_body37.us.us.us.prol.loopexit.loopexit, %for_loop_body37.us.us.us.preheader
  %.lcssa325.unr = phi float [ poison, %for_loop_body37.us.us.us.preheader ], [ %384, %for_loop_body37.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv118.unr = phi i64 [ %indvars.iv118.ph, %for_loop_body37.us.us.us.preheader ], [ %385, %for_loop_body37.us.us.us.prol.loopexit.loopexit ]
  %.05786.us.us.us.unr = phi float [ %.05786.us.us.us.ph, %for_loop_body37.us.us.us.preheader ], [ %384, %for_loop_body37.us.us.us.prol.loopexit.loopexit ]
  %386 = sub nsw i64 %indvars.iv118.ph, %wide.trip.count107
  %387 = icmp ugt i64 %386, -4
  br i1 %387, label %for_loop_test40.after_for39_crit_edge.us.us.us, label %for_loop_body37.us.us.us.preheader.new

for_loop_body37.us.us.us.preheader.new:           ; preds = %for_loop_body37.us.us.us.prol.loopexit
  %388 = add i32 %339, 3
  %389 = trunc i64 %indvars.iv118.unr to i32
  %390 = add i32 %388, %389
  %391 = mul i32 %336, %390
  %392 = shl i32 %336, 2
  %393 = add nuw i32 %389, 3
  %394 = mul i32 %332, %393
  %395 = add i32 %.05990.us.us, %394
  %396 = shl i32 %332, 2
  %397 = add i32 %339, 2
  %398 = add i32 %397, %389
  %399 = mul i32 %336, %398
  %400 = add nuw i32 %389, 2
  %401 = mul i32 %332, %400
  %402 = add i32 %.05990.us.us, %401
  %403 = add i32 %339, 1
  %404 = add i32 %403, %389
  %405 = mul i32 %336, %404
  %406 = add nuw i32 %389, 1
  %407 = mul i32 %332, %406
  %408 = add i32 %.05990.us.us, %407
  %409 = sub i64 %wide.trip.count107, %indvars.iv118.unr
  %410 = add i32 %339, %389
  %411 = mul i32 %336, %410
  %412 = mul i32 %332, %389
  %413 = add i32 %.05990.us.us, %412
  br label %for_loop_body37.us.us.us

for_loop_body37.us.us.us:                         ; preds = %for_loop_body37.us.us.us, %for_loop_body37.us.us.us.preheader.new
  %lsr.iv495 = phi i32 [ %lsr.iv.next496, %for_loop_body37.us.us.us ], [ %413, %for_loop_body37.us.us.us.preheader.new ]
  %lsr.iv493 = phi i64 [ %lsr.iv.next494, %for_loop_body37.us.us.us ], [ %409, %for_loop_body37.us.us.us.preheader.new ]
  %lsr.iv491 = phi i32 [ %lsr.iv.next492, %for_loop_body37.us.us.us ], [ %408, %for_loop_body37.us.us.us.preheader.new ]
  %lsr.iv489 = phi i32 [ %lsr.iv.next490, %for_loop_body37.us.us.us ], [ %402, %for_loop_body37.us.us.us.preheader.new ]
  %lsr.iv487 = phi i32 [ %lsr.iv.next488, %for_loop_body37.us.us.us ], [ %395, %for_loop_body37.us.us.us.preheader.new ]
  %lsr.iv485 = phi i32 [ %lsr.iv.next486, %for_loop_body37.us.us.us ], [ %.05889.us.us.us, %for_loop_body37.us.us.us.preheader.new ]
  %.05786.us.us.us = phi float [ %.05786.us.us.us.unr, %for_loop_body37.us.us.us.preheader.new ], [ %449, %for_loop_body37.us.us.us ]
  %414 = sext i32 %lsr.iv495 to i64
  %415 = getelementptr float, ptr %331, i64 %414
  %416 = load float, ptr %415, align 4
  %417 = add i32 %411, %lsr.iv485
  %418 = sext i32 %417 to i64
  %419 = getelementptr float, ptr %333, i64 %418
  %420 = load float, ptr %419, align 4
  %421 = fmul reassoc ninf nsz float %420, %416
  %422 = fadd reassoc ninf nsz float %421, %.05786.us.us.us
  %423 = sext i32 %lsr.iv491 to i64
  %424 = getelementptr float, ptr %331, i64 %423
  %425 = load float, ptr %424, align 4
  %426 = add i32 %405, %lsr.iv485
  %427 = sext i32 %426 to i64
  %428 = getelementptr float, ptr %333, i64 %427
  %429 = load float, ptr %428, align 4
  %430 = fmul reassoc ninf nsz float %429, %425
  %431 = fadd reassoc ninf nsz float %430, %422
  %432 = sext i32 %lsr.iv489 to i64
  %433 = getelementptr float, ptr %331, i64 %432
  %434 = load float, ptr %433, align 4
  %435 = add i32 %399, %lsr.iv485
  %436 = sext i32 %435 to i64
  %437 = getelementptr float, ptr %333, i64 %436
  %438 = load float, ptr %437, align 4
  %439 = fmul reassoc ninf nsz float %438, %434
  %440 = fadd reassoc ninf nsz float %439, %431
  %441 = sext i32 %lsr.iv487 to i64
  %442 = getelementptr float, ptr %331, i64 %441
  %443 = load float, ptr %442, align 4
  %444 = add i32 %391, %lsr.iv485
  %445 = sext i32 %444 to i64
  %446 = getelementptr float, ptr %333, i64 %445
  %447 = load float, ptr %446, align 4
  %448 = fmul reassoc ninf nsz float %447, %443
  %449 = fadd reassoc ninf nsz float %448, %440
  %lsr.iv.next486 = add i32 %lsr.iv485, %392
  %lsr.iv.next488 = add i32 %lsr.iv487, %396
  %lsr.iv.next490 = add i32 %lsr.iv489, %396
  %lsr.iv.next492 = add i32 %lsr.iv491, %396
  %lsr.iv.next494 = add i64 %lsr.iv493, -4
  %lsr.iv.next496 = add i32 %lsr.iv495, %396
  %exitcond122.not.3 = icmp eq i64 %lsr.iv.next494, 0
  br i1 %exitcond122.not.3, label %for_loop_test40.after_for39_crit_edge.us.us.us.loopexit, label %for_loop_body37.us.us.us, !llvm.loop !25

for_loop_test40.after_for39_crit_edge.us.us.us.loopexit: ; preds = %for_loop_body37.us.us.us
  br label %for_loop_test40.after_for39_crit_edge.us.us.us

for_loop_test40.after_for39_crit_edge.us.us.us:   ; preds = %for_loop_test40.after_for39_crit_edge.us.us.us.loopexit, %for_loop_body37.us.us.us.prol.loopexit, %vec.epilog.middle.block196, %middle.block174
  %.lcssa147 = phi float [ %357, %middle.block174 ], [ %370, %vec.epilog.middle.block196 ], [ %.lcssa325.unr, %for_loop_body37.us.us.us.prol.loopexit ], [ %449, %for_loop_test40.after_for39_crit_edge.us.us.us.loopexit ]
  %450 = load ptr, ptr %33, align 8
  %451 = load i32, ptr %34, align 4
  %452 = load i32, ptr %35, align 4
  %453 = load i32, ptr %36, align 4
  %454 = mul i32 %451, %lsr526
  %455 = add i32 %454, %.06897.us
  %456 = mul i32 %455, %452
  %457 = add i32 %456, %.05990.us.us
  %458 = mul i32 %457, %453
  %459 = add i32 %458, %.05889.us.us.us
  %460 = sext i32 %459 to i64
  %461 = getelementptr float, ptr %450, i64 %460
  store float %.lcssa147, ptr %461, align 4
  %462 = add nuw nsw i32 %.05889.us.us.us, 1
  %exitcond123.not = icmp eq i32 %462, %23
  br i1 %exitcond123.not, label %for_loop_test36.after_for35_crit_edge.split.us.us.us, label %iter.check177

for_loop_test36.after_for35_crit_edge.split.us.us.us: ; preds = %for_loop_test40.after_for39_crit_edge.us.us.us
  %463 = add nuw nsw i32 %.05990.us.us, 1
  %exitcond124.not = icmp eq i32 %463, %23
  br i1 %exitcond124.not, label %for_loop_test48.preheader.us.us.preheader, label %for_loop_test36.preheader.us.us

for_loop_test48.preheader.us.us.preheader:        ; preds = %for_loop_test36.after_for35_crit_edge.split.us.us.us
  br label %for_loop_test48.preheader.us.us

for_loop_test48.preheader.us.us:                  ; preds = %for_loop_test48.after_for47_crit_edge.split.us.us.us, %for_loop_test48.preheader.us.us.preheader
  %.05595.us.us = phi i32 [ %593, %for_loop_test48.after_for47_crit_edge.split.us.us.us ], [ 0, %for_loop_test48.preheader.us.us.preheader ]
  br label %iter.check

iter.check:                                       ; preds = %for_loop_test52.after_for51_crit_edge.us.us.us, %for_loop_test48.preheader.us.us
  %.05494.us.us.us = phi i32 [ 0, %for_loop_test48.preheader.us.us ], [ %592, %for_loop_test52.after_for51_crit_edge.us.us.us ]
  %464 = load ptr, ptr %33, align 8
  %465 = load i32, ptr %34, align 4
  %466 = load i32, ptr %35, align 4
  %467 = load i32, ptr %36, align 4
  %468 = mul i32 %465, %lsr526
  %469 = add i32 %468, %.06897.us
  %470 = mul i32 %469, %466
  %471 = add i32 %470, %.05595.us.us
  %472 = mul i32 %471, %467
  %473 = load ptr, ptr %27, align 8
  %474 = load i32, ptr %28, align 4
  br i1 %min.iters.check264, label %for_loop_body49.us.us.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %iter.check
  %475 = add i32 %472, %56
  %476 = icmp slt i32 %475, %472
  %477 = or i1 %476, %57
  %ident.check = icmp ne i32 %474, 1
  %478 = add i32 %.05494.us.us.us, %56
  %479 = icmp slt i32 %478, %.05494.us.us.us
  %480 = or i1 %477, %ident.check
  %481 = or i1 %479, %480
  br i1 %481, label %for_loop_body49.us.us.us.preheader, label %vector.main.loop.iter.check

vector.main.loop.iter.check:                      ; preds = %vector.scevcheck
  br i1 %min.iters.check267, label %vec.epilog.ph, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.main.loop.iter.check
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv501 = phi i32 [ %.05494.us.us.us, %vector.body.preheader ], [ %lsr.iv.next502, %vector.body ]
  %lsr.iv499 = phi i32 [ %472, %vector.body.preheader ], [ %lsr.iv.next500, %vector.body ]
  %lsr.iv497 = phi i64 [ %n.vec271, %vector.body.preheader ], [ %lsr.iv.next498, %vector.body ]
  %vec.phi = phi <8 x float> [ %496, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi150 = phi <8 x float> [ %497, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi151 = phi <8 x float> [ %498, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi152 = phi <8 x float> [ %499, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %482 = sext i32 %lsr.iv499 to i64
  %483 = getelementptr float, ptr %464, i64 %482
  %484 = getelementptr i8, ptr %483, i64 32
  %485 = getelementptr i8, ptr %483, i64 64
  %486 = getelementptr i8, ptr %483, i64 96
  %wide.load = load <8 x float>, ptr %483, align 4
  %wide.load153 = load <8 x float>, ptr %484, align 4
  %wide.load154 = load <8 x float>, ptr %485, align 4
  %wide.load155 = load <8 x float>, ptr %486, align 4
  %487 = sext i32 %lsr.iv501 to i64
  %488 = getelementptr float, ptr %473, i64 %487
  %489 = getelementptr i8, ptr %488, i64 32
  %490 = getelementptr i8, ptr %488, i64 64
  %491 = getelementptr i8, ptr %488, i64 96
  %wide.load156 = load <8 x float>, ptr %488, align 4
  %wide.load157 = load <8 x float>, ptr %489, align 4
  %wide.load158 = load <8 x float>, ptr %490, align 4
  %wide.load159 = load <8 x float>, ptr %491, align 4
  %492 = fmul reassoc ninf nsz <8 x float> %wide.load156, %wide.load
  %493 = fmul reassoc ninf nsz <8 x float> %wide.load157, %wide.load153
  %494 = fmul reassoc ninf nsz <8 x float> %wide.load158, %wide.load154
  %495 = fmul reassoc ninf nsz <8 x float> %wide.load159, %wide.load155
  %496 = fadd reassoc ninf nsz <8 x float> %492, %vec.phi
  %497 = fadd reassoc ninf nsz <8 x float> %493, %vec.phi150
  %498 = fadd reassoc ninf nsz <8 x float> %494, %vec.phi151
  %499 = fadd reassoc ninf nsz <8 x float> %495, %vec.phi152
  %lsr.iv.next498 = add nsw i64 %lsr.iv497, -32
  %lsr.iv.next500 = add i32 %lsr.iv499, 32
  %lsr.iv.next502 = add nuw i32 %lsr.iv501, 32
  %500 = icmp eq i64 %lsr.iv.next498, 0
  br i1 %500, label %middle.block, label %vector.body, !llvm.loop !26

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %497, %496
  %bin.rdx160 = fadd reassoc ninf nsz <8 x float> %498, %bin.rdx
  %bin.rdx161 = fadd reassoc ninf nsz <8 x float> %499, %bin.rdx160
  %501 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %bin.rdx161)
  br i1 %cmp.n290, label %for_loop_test52.after_for51_crit_edge.us.us.us, label %vec.epilog.iter.check

vec.epilog.iter.check:                            ; preds = %middle.block
  br i1 %min.epilog.iters.check298, label %for_loop_body49.us.us.us.preheader, label %vec.epilog.ph

vec.epilog.ph:                                    ; preds = %vec.epilog.iter.check, %vector.main.loop.iter.check
  %vec.epilog.resume.val = phi i64 [ %n.vec271, %vec.epilog.iter.check ], [ 0, %vector.main.loop.iter.check ]
  %bc.merge.rdx = phi float [ %501, %vec.epilog.iter.check ], [ 0.000000e+00, %vector.main.loop.iter.check ]
  %502 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %bc.merge.rdx, i64 0
  %503 = add i64 %61, %vec.epilog.resume.val
  %504 = trunc i64 %vec.epilog.resume.val to i32
  %505 = add i32 %472, %504
  %506 = add i32 %.05494.us.us.us, %504
  br label %vec.epilog.vector.body

vec.epilog.vector.body:                           ; preds = %vec.epilog.vector.body, %vec.epilog.ph
  %lsr.iv507 = phi i32 [ %lsr.iv.next508, %vec.epilog.vector.body ], [ %506, %vec.epilog.ph ]
  %lsr.iv505 = phi i32 [ %lsr.iv.next506, %vec.epilog.vector.body ], [ %505, %vec.epilog.ph ]
  %lsr.iv503 = phi i64 [ %lsr.iv.next504, %vec.epilog.vector.body ], [ %503, %vec.epilog.ph ]
  %vec.phi165 = phi <4 x float> [ %502, %vec.epilog.ph ], [ %512, %vec.epilog.vector.body ]
  %507 = sext i32 %lsr.iv505 to i64
  %508 = getelementptr float, ptr %464, i64 %507
  %wide.load166 = load <4 x float>, ptr %508, align 4
  %509 = sext i32 %lsr.iv507 to i64
  %510 = getelementptr float, ptr %473, i64 %509
  %wide.load167 = load <4 x float>, ptr %510, align 4
  %511 = fmul reassoc ninf nsz <4 x float> %wide.load167, %wide.load166
  %512 = fadd reassoc ninf nsz <4 x float> %511, %vec.phi165
  %lsr.iv.next504 = add i64 %lsr.iv503, 4
  %lsr.iv.next506 = add i32 %lsr.iv505, 4
  %lsr.iv.next508 = add i32 %lsr.iv507, 4
  %513 = icmp eq i64 %lsr.iv.next504, 0
  br i1 %513, label %vec.epilog.middle.block, label %vec.epilog.vector.body, !llvm.loop !27

vec.epilog.middle.block:                          ; preds = %vec.epilog.vector.body
  %514 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float 0.000000e+00, <4 x float> %512)
  br i1 %cmp.n307, label %for_loop_test52.after_for51_crit_edge.us.us.us, label %for_loop_body49.us.us.us.preheader

for_loop_body49.us.us.us.preheader:               ; preds = %vec.epilog.middle.block, %vec.epilog.iter.check, %vector.scevcheck, %iter.check
  %indvars.iv125.ph = phi i64 [ %n.vec271, %vec.epilog.iter.check ], [ 0, %iter.check ], [ 0, %vector.scevcheck ], [ %n.vec300, %vec.epilog.middle.block ]
  %.05391.us.us.us.ph = phi float [ %501, %vec.epilog.iter.check ], [ 0.000000e+00, %iter.check ], [ 0.000000e+00, %vector.scevcheck ], [ %514, %vec.epilog.middle.block ]
  br i1 %lcmp.mod334.not, label %for_loop_body49.us.us.us.prol.loopexit, label %for_loop_body49.us.us.us.prol.preheader

for_loop_body49.us.us.us.prol.preheader:          ; preds = %for_loop_body49.us.us.us.preheader
  %515 = trunc i64 %indvars.iv125.ph to i32
  %516 = mul i32 %474, %515
  %517 = add i32 %.05494.us.us.us, %516
  %518 = zext i32 %472 to i64
  br label %for_loop_body49.us.us.us.prol

for_loop_body49.us.us.us.prol:                    ; preds = %for_loop_body49.us.us.us.prol, %for_loop_body49.us.us.us.prol.preheader
  %lsr.iv512 = phi i64 [ %xtraiter333, %for_loop_body49.us.us.us.prol.preheader ], [ %lsr.iv.next513, %for_loop_body49.us.us.us.prol ]
  %lsr.iv509 = phi i32 [ %517, %for_loop_body49.us.us.us.prol.preheader ], [ %lsr.iv.next510, %for_loop_body49.us.us.us.prol ]
  %indvars.iv125.prol = phi i64 [ %indvars.iv.next126.prol, %for_loop_body49.us.us.us.prol ], [ %indvars.iv125.ph, %for_loop_body49.us.us.us.prol.preheader ]
  %.05391.us.us.us.prol = phi float [ %527, %for_loop_body49.us.us.us.prol ], [ %.05391.us.us.us.ph, %for_loop_body49.us.us.us.prol.preheader ]
  %519 = add i64 %518, %indvars.iv125.prol
  %tmp511 = trunc i64 %519 to i32
  %520 = sext i32 %tmp511 to i64
  %521 = getelementptr float, ptr %464, i64 %520
  %522 = load float, ptr %521, align 4
  %523 = sext i32 %lsr.iv509 to i64
  %524 = getelementptr float, ptr %473, i64 %523
  %525 = load float, ptr %524, align 4
  %526 = fmul reassoc ninf nsz float %525, %522
  %527 = fadd reassoc ninf nsz float %526, %.05391.us.us.us.prol
  %indvars.iv.next126.prol = add nuw nsw i64 %indvars.iv125.prol, 1
  %lsr.iv.next510 = add i32 %lsr.iv509, %474
  %lsr.iv.next513 = add nsw i64 %lsr.iv512, -1
  %prol.iter344.cmp.not = icmp eq i64 %lsr.iv.next513, 0
  br i1 %prol.iter344.cmp.not, label %for_loop_body49.us.us.us.prol.loopexit.loopexit, label %for_loop_body49.us.us.us.prol, !llvm.loop !28

for_loop_body49.us.us.us.prol.loopexit.loopexit:  ; preds = %for_loop_body49.us.us.us.prol
  br label %for_loop_body49.us.us.us.prol.loopexit

for_loop_body49.us.us.us.prol.loopexit:           ; preds = %for_loop_body49.us.us.us.prol.loopexit.loopexit, %for_loop_body49.us.us.us.preheader
  %.lcssa331.unr = phi float [ poison, %for_loop_body49.us.us.us.preheader ], [ %527, %for_loop_body49.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv125.unr = phi i64 [ %indvars.iv125.ph, %for_loop_body49.us.us.us.preheader ], [ %indvars.iv.next126.prol, %for_loop_body49.us.us.us.prol.loopexit.loopexit ]
  %.05391.us.us.us.unr = phi float [ %.05391.us.us.us.ph, %for_loop_body49.us.us.us.preheader ], [ %527, %for_loop_body49.us.us.us.prol.loopexit.loopexit ]
  %528 = sub nsw i64 %indvars.iv125.ph, %wide.trip.count107
  %529 = icmp ugt i64 %528, -4
  br i1 %529, label %for_loop_test52.after_for51_crit_edge.us.us.us, label %for_loop_body49.us.us.us.preheader.new

for_loop_body49.us.us.us.preheader.new:           ; preds = %for_loop_body49.us.us.us.prol.loopexit
  %530 = zext i32 %472 to i64
  %531 = trunc i64 %indvars.iv125.unr to i32
  %532 = add nuw i32 %531, 3
  %533 = mul i32 %474, %532
  %534 = add i32 %.05494.us.us.us, %533
  %535 = shl i32 %474, 2
  %536 = add nuw i32 %531, 2
  %537 = mul i32 %474, %536
  %538 = add i32 %.05494.us.us.us, %537
  %539 = add nuw i32 %531, 1
  %540 = mul i32 %474, %539
  %541 = add i32 %.05494.us.us.us, %540
  %542 = mul i32 %474, %531
  %543 = add i32 %.05494.us.us.us, %542
  br label %for_loop_body49.us.us.us

for_loop_body49.us.us.us:                         ; preds = %for_loop_body49.us.us.us, %for_loop_body49.us.us.us.preheader.new
  %lsr.iv523 = phi i32 [ %lsr.iv.next524, %for_loop_body49.us.us.us ], [ %543, %for_loop_body49.us.us.us.preheader.new ]
  %lsr.iv521 = phi i32 [ %lsr.iv.next522, %for_loop_body49.us.us.us ], [ %541, %for_loop_body49.us.us.us.preheader.new ]
  %lsr.iv518 = phi i32 [ %lsr.iv.next519, %for_loop_body49.us.us.us ], [ %538, %for_loop_body49.us.us.us.preheader.new ]
  %lsr.iv515 = phi i32 [ %lsr.iv.next516, %for_loop_body49.us.us.us ], [ %534, %for_loop_body49.us.us.us.preheader.new ]
  %indvars.iv125 = phi i64 [ %indvars.iv125.unr, %for_loop_body49.us.us.us.preheader.new ], [ %indvars.iv.next126.3, %for_loop_body49.us.us.us ]
  %.05391.us.us.us = phi float [ %.05391.us.us.us.unr, %for_loop_body49.us.us.us.preheader.new ], [ %579, %for_loop_body49.us.us.us ]
  %544 = add i64 %530, %indvars.iv125
  %tmp525 = trunc i64 %544 to i32
  %545 = sext i32 %tmp525 to i64
  %546 = getelementptr float, ptr %464, i64 %545
  %547 = load float, ptr %546, align 4
  %548 = sext i32 %lsr.iv523 to i64
  %549 = getelementptr float, ptr %473, i64 %548
  %550 = load float, ptr %549, align 4
  %551 = fmul reassoc ninf nsz float %550, %547
  %552 = fadd reassoc ninf nsz float %551, %.05391.us.us.us
  %553 = add i64 %544, 1
  %tmp520 = trunc i64 %553 to i32
  %554 = sext i32 %tmp520 to i64
  %555 = getelementptr float, ptr %464, i64 %554
  %556 = load float, ptr %555, align 4
  %557 = sext i32 %lsr.iv521 to i64
  %558 = getelementptr float, ptr %473, i64 %557
  %559 = load float, ptr %558, align 4
  %560 = fmul reassoc ninf nsz float %559, %556
  %561 = fadd reassoc ninf nsz float %560, %552
  %562 = add i64 %544, 2
  %tmp517 = trunc i64 %562 to i32
  %563 = sext i32 %tmp517 to i64
  %564 = getelementptr float, ptr %464, i64 %563
  %565 = load float, ptr %564, align 4
  %566 = sext i32 %lsr.iv518 to i64
  %567 = getelementptr float, ptr %473, i64 %566
  %568 = load float, ptr %567, align 4
  %569 = fmul reassoc ninf nsz float %568, %565
  %570 = fadd reassoc ninf nsz float %569, %561
  %571 = add i64 %544, 3
  %tmp514 = trunc i64 %571 to i32
  %572 = sext i32 %tmp514 to i64
  %573 = getelementptr float, ptr %464, i64 %572
  %574 = load float, ptr %573, align 4
  %575 = sext i32 %lsr.iv515 to i64
  %576 = getelementptr float, ptr %473, i64 %575
  %577 = load float, ptr %576, align 4
  %578 = fmul reassoc ninf nsz float %577, %574
  %579 = fadd reassoc ninf nsz float %578, %570
  %indvars.iv.next126.3 = add nuw nsw i64 %indvars.iv125, 4
  %lsr.iv.next516 = add i32 %lsr.iv515, %535
  %lsr.iv.next519 = add i32 %lsr.iv518, %535
  %lsr.iv.next522 = add i32 %lsr.iv521, %535
  %lsr.iv.next524 = add i32 %lsr.iv523, %535
  %exitcond129.not.3 = icmp eq i64 %wide.trip.count107, %indvars.iv.next126.3
  br i1 %exitcond129.not.3, label %for_loop_test52.after_for51_crit_edge.us.us.us.loopexit, label %for_loop_body49.us.us.us, !llvm.loop !29

for_loop_test52.after_for51_crit_edge.us.us.us.loopexit: ; preds = %for_loop_body49.us.us.us
  br label %for_loop_test52.after_for51_crit_edge.us.us.us

for_loop_test52.after_for51_crit_edge.us.us.us:   ; preds = %for_loop_test52.after_for51_crit_edge.us.us.us.loopexit, %for_loop_body49.us.us.us.prol.loopexit, %vec.epilog.middle.block, %middle.block
  %.lcssa148 = phi float [ %501, %middle.block ], [ %514, %vec.epilog.middle.block ], [ %.lcssa331.unr, %for_loop_body49.us.us.us.prol.loopexit ], [ %579, %for_loop_test52.after_for51_crit_edge.us.us.us.loopexit ]
  %580 = load ptr, ptr %37, align 8
  %581 = load i32, ptr %38, align 4
  %582 = load i32, ptr %39, align 4
  %583 = load i32, ptr %40, align 4
  %584 = mul i32 %581, %lsr526
  %585 = add i32 %584, %.06897.us
  %586 = mul i32 %585, %582
  %587 = add i32 %586, %.05595.us.us
  %588 = mul i32 %587, %583
  %589 = add i32 %588, %.05494.us.us.us
  %590 = sext i32 %589 to i64
  %591 = getelementptr float, ptr %580, i64 %590
  store float %.lcssa148, ptr %591, align 4
  %592 = add nuw nsw i32 %.05494.us.us.us, 1
  %exitcond130.not = icmp eq i32 %592, %23
  br i1 %exitcond130.not, label %for_loop_test48.after_for47_crit_edge.split.us.us.us, label %iter.check

for_loop_test48.after_for47_crit_edge.split.us.us.us: ; preds = %for_loop_test52.after_for51_crit_edge.us.us.us
  %593 = add nuw nsw i32 %.05595.us.us, 1
  %exitcond131.not = icmp eq i32 %593, %23
  br i1 %exitcond131.not, label %after_for43.us.loopexit, label %for_loop_test48.preheader.us.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %after_for43.us
  %594 = load ptr, ptr %3, align 8
  %595 = getelementptr inbounds nuw i8, ptr %594, i64 32872
  %596 = load ptr, ptr %595, align 8
  %597 = getelementptr inbounds nuw i8, ptr %596, i64 8
  %598 = load float, ptr %597, align 4
  %599 = tail call i32 @llvm.smax.i32(i32 %.1.lcssa.us139, i32 1)
  %600 = uitofp nneg i32 %599 to float
  %601 = fmul reassoc ninf nsz float %598, %598
  %602 = fmul reassoc ninf nsz float %601, %600
  %603 = fdiv reassoc ninf nsz float 1.000000e+00, %602
  %604 = load ptr, ptr %41, align 8
  %605 = getelementptr float, ptr %604, i64 %indvars.iv133
  store float %603, ptr %605, align 4
  %indvars.iv.next134 = add nsw i64 %indvars.iv133, 1
  %exitcond137.not = icmp eq i64 %indvars.iv.next134, %wide.trip.count136
  br i1 %exitcond137.not, label %after_for.loopexit, label %for_loop_test4.preheader.us

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit414:                            ; preds = %for_loop_test4.preheader
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit414, %after_for.loopexit, %for_loop_test4.preheader.prol.loopexit, %allocs
  ret void

for_loop_test4.preheader:                         ; preds = %for_loop_test4.preheader, %for_loop_test4.preheader.preheader413
  %indvars.iv = phi i64 [ %indvars.iv.next.3, %for_loop_test4.preheader ], [ %indvars.iv.unr, %for_loop_test4.preheader.preheader413 ]
  %606 = load ptr, ptr %3, align 8
  %607 = getelementptr inbounds nuw i8, ptr %606, i64 32872
  %608 = load ptr, ptr %607, align 8
  %609 = getelementptr inbounds nuw i8, ptr %608, i64 8
  %610 = load float, ptr %609, align 4
  %611 = fmul reassoc ninf nsz float %610, %610
  %612 = fdiv reassoc ninf nsz float 1.000000e+00, %611
  %613 = load ptr, ptr %41, align 8
  %614 = shl i64 %indvars.iv, 2
  %scevgep532 = getelementptr i8, ptr %613, i64 %614
  store float %612, ptr %scevgep532, align 4
  %615 = load ptr, ptr %3, align 8
  %616 = getelementptr inbounds nuw i8, ptr %615, i64 32872
  %617 = load ptr, ptr %616, align 8
  %618 = getelementptr inbounds nuw i8, ptr %617, i64 8
  %619 = load float, ptr %618, align 4
  %620 = fmul reassoc ninf nsz float %619, %619
  %621 = fdiv reassoc ninf nsz float 1.000000e+00, %620
  %622 = load ptr, ptr %41, align 8
  %623 = getelementptr i8, ptr %622, i64 %614
  %624 = getelementptr i8, ptr %623, i64 4
  store float %621, ptr %624, align 4
  %625 = load ptr, ptr %3, align 8
  %626 = getelementptr inbounds nuw i8, ptr %625, i64 32872
  %627 = load ptr, ptr %626, align 8
  %628 = getelementptr inbounds nuw i8, ptr %627, i64 8
  %629 = load float, ptr %628, align 4
  %630 = fmul reassoc ninf nsz float %629, %629
  %631 = fdiv reassoc ninf nsz float 1.000000e+00, %630
  %632 = load ptr, ptr %41, align 8
  %633 = getelementptr i8, ptr %632, i64 %614
  %634 = getelementptr i8, ptr %633, i64 8
  store float %631, ptr %634, align 4
  %635 = load ptr, ptr %3, align 8
  %636 = getelementptr inbounds nuw i8, ptr %635, i64 32872
  %637 = load ptr, ptr %636, align 8
  %638 = getelementptr inbounds nuw i8, ptr %637, i64 8
  %639 = load float, ptr %638, align 4
  %640 = fmul reassoc ninf nsz float %639, %639
  %641 = fdiv reassoc ninf nsz float 1.000000e+00, %640
  %642 = load ptr, ptr %41, align 8
  %643 = getelementptr i8, ptr %642, i64 %614
  %644 = getelementptr i8, ptr %643, i64 12
  store float %641, ptr %644, align 4
  %indvars.iv.next.3 = add nsw i64 %indvars.iv, 4
  %exitcond.not.3 = icmp eq i64 %wide.trip.count136, %indvars.iv.next.3
  br i1 %exitcond.not.3, label %after_for.loopexit414, label %for_loop_test4.preheader
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext, align 8
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
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !30

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
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !32

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
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
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
!10 = distinct !{!10, !11}
!11 = !{!"llvm.loop.unroll.disable"}
!12 = distinct !{!12, !13, !14}
!13 = !{!"llvm.loop.isvectorized", i32 1}
!14 = !{!"llvm.loop.unroll.runtime.disable"}
!15 = distinct !{!15, !13, !14}
!16 = distinct !{!16, !11}
!17 = distinct !{!17, !13}
!18 = distinct !{!18, !11}
!19 = distinct !{!19, !13, !14}
!20 = distinct !{!20, !13, !14}
!21 = distinct !{!21, !13}
!22 = distinct !{!22, !13, !14}
!23 = distinct !{!23, !13, !14}
!24 = distinct !{!24, !11}
!25 = distinct !{!25, !13}
!26 = distinct !{!26, !13, !14}
!27 = distinct !{!27, !13, !14}
!28 = distinct !{!28, !11}
!29 = distinct !{!29, !13}
!30 = distinct !{!30, !31}
!31 = !{!"llvm.loop.mustprogress"}
!32 = distinct !{!32, !31}
