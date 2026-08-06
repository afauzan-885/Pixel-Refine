; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.84*, void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.84 = type { i8*, %struct.LLVMRuntime.83*, i32, i64* }
%struct.LLVMRuntime.83 = type { %struct.PreallocatedMemoryChunk.79, %struct.PreallocatedMemoryChunk.79, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.80*], [1024 x %struct.NodeManager.81*], [1024 x i8*], i8*, %struct.RandState.82*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.79 = type { i8*, i8*, i64 }
%struct.ListManager.80 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.83* }
%struct.NodeManager.81 = type { %struct.LLVMRuntime.83*, i32, i32, i32, i32, %struct.ListManager.80*, %struct.ListManager.80*, %struct.ListManager.80*, i32 }
%struct.RandState.82 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_box_blur_h_generic_1ch_kernel_c170_0_kernel_0_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 8
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %7, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 4
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = mul i32 %13, %4
  %20 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %7, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %20, i64 0, i32 14
  %22 = bitcast i8** %21 to i32**
  %23 = load i32*, i32** %22, align 8
  store i32 %19, i32* %23, align 4
  ret void
}

; Function Attrs: nounwind
define void @_box_blur_h_generic_1ch_kernel_c170_0_kernel_1_range_for(%struct.RuntimeContext.84* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.84* %context, %struct.RuntimeContext.84** %4, align 8
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.84*, i8*, i32)* @function_body, void (%struct.RuntimeContext.84*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.84* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %4, i64 0, i32 14
  %6 = bitcast i8** %5 to i32**
  %7 = load i32*, i32** %6, align 8
  %8 = load i32, i32* %7, align 4
  %9 = add i32 %8, 7
  %10 = sdiv i32 %9, 8
  %11 = icmp slt i32 %9, 0
  %12 = shl nsw i32 %10, 3
  %13 = icmp ne i32 %12, %9
  %14 = and i1 %11, %13
  %.neg = sext i1 %14 to i32
  %15 = add nsw i32 %10, %.neg
  %16 = tail call i32 @llvm.smax.i32(i32 %15, i32 512)
  %17 = mul i32 %16, %2
  %18 = add i32 %17, %16
  %19 = tail call i32 @llvm.smin.i32(i32 %8, i32 %18)
  %20 = bitcast %struct.RuntimeContext.84* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 4
  %23 = load i32, i32* %22, align 4
  %neg = sub i32 0, %23
  %24 = shl i32 %23, 1
  %25 = or i32 %24, 1
  %26 = sitofp i32 %25 to float
  %27 = icmp slt i32 %17, %19
  br i1 %27, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %28 = add i32 %23, 1
  %29 = icmp sgt i32 %28, %neg
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  br i1 %29, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %34 = add i32 %24, -16
  %35 = lshr i32 %34, 4
  %36 = add nuw nsw i32 %35, 1
  %min.iters.check = icmp ult i32 %24, 16
  %n.vec = and i32 %24, -16
  %ind.end = sub i32 %n.vec, %23
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %xtraiter = and i32 %36, 1
  %37 = icmp ult i32 %34, 16
  %unroll_iter = and i32 %36, 536870910
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br label %for_loop_body.us

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  %38 = fdiv reassoc ninf nsz float 0.000000e+00, %26
  br label %for_loop_body

for_loop_body.us:                                 ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %.0913.us = phi i32 [ %127, %for_loop_test4.after_for3_crit_edge.us ], [ %17, %for_loop_body.us.preheader ]
  %39 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %40 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %39, i64 0, i32 14
  %41 = load i8*, i8** %40, align 8
  %42 = getelementptr inbounds i8, i8* %41, i64 4
  %43 = bitcast i8* %42 to i32*
  %44 = load i32, i32* %43, align 4
  %45 = sdiv i32 %.0913.us, %44
  %46 = mul i32 %45, %44
  %47 = xor i32 %44, %.0913.us
  %48 = icmp slt i32 %47, 0
  %49 = icmp ne i32 %.0913.us, 0
  %50 = icmp ne i32 %46, %.0913.us
  %51 = and i1 %49, %48
  %52 = and i1 %51, %50
  %.neg10.us = sext i1 %52 to i32
  %53 = add i32 %45, %.neg10.us
  %54 = mul i32 %53, %44
  %55 = sub i32 %.0913.us, %54
  %56 = getelementptr inbounds i8, i8* %41, i64 8
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = add i32 %58, -1
  %60 = load float*, float** %30, align 8
  %61 = load i32, i32* %31, align 4
  %62 = mul i32 %61, %53
  br i1 %min.iters.check, label %for_loop_body1.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body.us
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %55, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert23 = insertelement <8 x i32> poison, i32 %59, i64 0
  %broadcast.splat24 = shufflevector <8 x i32> %broadcast.splatinsert23, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert27 = insertelement <8 x i32> poison, i32 %62, i64 0
  %broadcast.splat28 = shufflevector <8 x i32> %broadcast.splatinsert27, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %37, label %middle.block.unr-lcssa, label %vector.ph.new

vector.ph.new:                                    ; preds = %vector.ph
  %.scalar = add i32 %55, 8
  %63 = insertelement <8 x i32> poison, i32 %.scalar, i64 0
  %64 = shufflevector <8 x i32> %63, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph.new
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %unroll_iter, %vector.ph.new ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph.new ], [ %vec.ind.next.1, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph.new ], [ %91, %vector.body ]
  %vec.phi20 = phi <8 x float> [ zeroinitializer, %vector.ph.new ], [ %92, %vector.body ]
  %65 = add <8 x i32> %vec.ind, %broadcast.splat
  %66 = add <8 x i32> %64, %vec.ind
  %67 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %65, <8 x i32> zeroinitializer)
  %68 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %66, <8 x i32> zeroinitializer)
  %69 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %67)
  %70 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %68)
  %71 = add <8 x i32> %broadcast.splat28, %69
  %72 = add <8 x i32> %broadcast.splat28, %70
  %73 = sext <8 x i32> %71 to <8 x i64>
  %74 = sext <8 x i32> %72 to <8 x i64>
  %75 = getelementptr float, float* %60, <8 x i64> %73
  %76 = getelementptr float, float* %60, <8 x i64> %74
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %75, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather31 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %76, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %77 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi
  %78 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather31, %vec.phi20
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %79 = add <8 x i32> %vec.ind.next, %broadcast.splat
  %80 = add <8 x i32> %64, %vec.ind.next
  %81 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %79, <8 x i32> zeroinitializer)
  %82 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %80, <8 x i32> zeroinitializer)
  %83 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %81)
  %84 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %82)
  %85 = add <8 x i32> %broadcast.splat28, %83
  %86 = add <8 x i32> %broadcast.splat28, %84
  %87 = sext <8 x i32> %85 to <8 x i64>
  %88 = sext <8 x i32> %86 to <8 x i64>
  %89 = getelementptr float, float* %60, <8 x i64> %87
  %90 = getelementptr float, float* %60, <8 x i64> %88
  %wide.masked.gather.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %89, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather31.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %90, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %91 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.1, %77
  %92 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather31.1, %78
  %vec.ind.next.1 = add <8 x i32> %vec.ind, <i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32>
  %lsr.iv.next = add i32 %lsr.iv, -2
  %niter.ncmp.1 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa33.ph = phi <8 x float> [ undef, %vector.ph ], [ %91, %middle.block.unr-lcssa.loopexit ]
  %.lcssa.ph = phi <8 x float> [ undef, %vector.ph ], [ %92, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %91, %middle.block.unr-lcssa.loopexit ]
  %vec.phi20.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %92, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %93 = add <8 x i32> %vec.ind.unr, %broadcast.splat
  %.scalar.epil = add i32 %55, 8
  %94 = insertelement <8 x i32> poison, i32 %.scalar.epil, i64 0
  %95 = shufflevector <8 x i32> %94, <8 x i32> poison, <8 x i32> zeroinitializer
  %96 = add <8 x i32> %95, %vec.ind.unr
  %97 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %93, <8 x i32> zeroinitializer)
  %98 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %96, <8 x i32> zeroinitializer)
  %99 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %97)
  %100 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %98)
  %101 = add <8 x i32> %broadcast.splat28, %99
  %102 = add <8 x i32> %broadcast.splat28, %100
  %103 = sext <8 x i32> %101 to <8 x i64>
  %104 = sext <8 x i32> %102 to <8 x i64>
  %105 = getelementptr float, float* %60, <8 x i64> %103
  %106 = getelementptr float, float* %60, <8 x i64> %104
  %wide.masked.gather.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %105, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather31.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %106, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %107 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.epil, %vec.phi.unr
  %108 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather31.epil, %vec.phi20.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa33 = phi <8 x float> [ %.lcssa33.ph, %middle.block.unr-lcssa ], [ %107, %vector.body.epil ]
  %.lcssa = phi <8 x float> [ %.lcssa.ph, %middle.block.unr-lcssa ], [ %108, %vector.body.epil ]
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %.lcssa, %.lcssa33
  %109 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx)
  br label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %middle.block, %for_loop_body.us
  %.012.us.ph = phi i32 [ %neg, %for_loop_body.us ], [ %ind.end, %middle.block ]
  %.0811.us.ph = phi float [ 0.000000e+00, %for_loop_body.us ], [ %109, %middle.block ]
  %110 = sub i32 %28, %.012.us.ph
  %111 = add i32 %.012.us.ph, %.0913.us
  %112 = sub i32 %111, %54
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader
  %lsr.iv43 = phi i32 [ %112, %for_loop_body1.us.preheader ], [ %lsr.iv.next44, %for_loop_body1.us ]
  %lsr.iv41 = phi i32 [ %110, %for_loop_body1.us.preheader ], [ %lsr.iv.next42, %for_loop_body1.us ]
  %.0811.us = phi float [ %119, %for_loop_body1.us ], [ %.0811.us.ph, %for_loop_body1.us.preheader ]
  %113 = tail call i32 @llvm.smax.i32(i32 %lsr.iv43, i32 0)
  %114 = tail call i32 @llvm.smin.i32(i32 %59, i32 %113)
  %115 = add i32 %62, %114
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %60, i64 %116
  %118 = load float, float* %117, align 4
  %119 = fadd reassoc ninf nsz float %118, %.0811.us
  %lsr.iv.next42 = add i32 %lsr.iv41, -1
  %lsr.iv.next44 = add i32 %lsr.iv43, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next42, 0
  br i1 %exitcond.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us, !llvm.loop !11

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us
  %120 = fdiv reassoc ninf nsz float %119, %26
  %121 = load float*, float** %32, align 8
  %122 = load i32, i32* %33, align 4
  %123 = mul i32 %122, %53
  %124 = add i32 %123, %55
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %121, i64 %125
  store float %120, float* %126, align 4
  %127 = add nsw i32 %.0913.us, 1
  %exitcond15.not = icmp eq i32 %127, %19
  br i1 %exitcond15.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.0913 = phi i32 [ %150, %for_loop_body ], [ %17, %for_loop_body.preheader ]
  %128 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %129 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %128, i64 0, i32 14
  %130 = load i8*, i8** %129, align 8
  %131 = getelementptr inbounds i8, i8* %130, i64 4
  %132 = bitcast i8* %131 to i32*
  %133 = load i32, i32* %132, align 4
  %134 = sdiv i32 %.0913, %133
  %135 = mul i32 %134, %133
  %136 = xor i32 %133, %.0913
  %137 = icmp slt i32 %136, 0
  %138 = icmp ne i32 %.0913, 0
  %139 = icmp ne i32 %.0913, %135
  %140 = and i1 %138, %137
  %141 = and i1 %140, %139
  %.neg10 = sext i1 %141 to i32
  %142 = add i32 %134, %.neg10
  %143 = load float*, float** %32, align 8
  %144 = load i32, i32* %33, align 4
  %145 = sub i32 %144, %133
  %146 = mul i32 %145, %142
  %147 = add i32 %.0913, %146
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %143, i64 %148
  store float %38, float* %149, align 4
  %150 = add nsw i32 %.0913, 1
  %exitcond16.not = icmp eq i32 %19, %150
  br i1 %exitcond16.not, label %after_for.loopexit40, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit40:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit40, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.84, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.84**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.84*, %struct.RuntimeContext.84** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.7.0..sroa_cast, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 32
  %.sroa.8.0..sroa_cast = bitcast i8* %.sroa.8.0..sroa_idx to i64*
  %.sroa.8.0.copyload = load i64, i64* %.sroa.8.0..sroa_cast, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 40
  %.sroa.9.0..sroa_cast = bitcast i8* %.sroa.9.0..sroa_idx to i32*
  %.sroa.9.0.copyload = load i32, i32* %.sroa.9.0..sroa_cast, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 44
  %.sroa.12.0..sroa_cast = bitcast i8* %.sroa.12.0..sroa_idx to i32*
  %.sroa.12.0.copyload = load i32, i32* %.sroa.12.0..sroa_cast, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 48
  %.sroa.15.0..sroa_cast = bitcast i8* %.sroa.15.0..sroa_idx to i32*
  %.sroa.15.0.copyload = load i32, i32* %.sroa.15.0..sroa_cast, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 52
  %.sroa.17.0..sroa_cast = bitcast i8* %.sroa.17.0..sroa_idx to i32*
  %.sroa.17.0.copyload = load i32, i32* %.sroa.17.0..sroa_cast, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.84* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.84* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %4, i64 0, i32 2
  store i32 %1, i32* %10, align 8
  switch i32 %.sroa.17.0.copyload, label %.loopexit [
    i32 1, label %11
    i32 -1, label %19
  ]

11:                                               ; preds = %7
  %12 = mul nsw i32 %.sroa.15.0.copyload, %2
  %13 = add nsw i32 %12, %.sroa.9.0.copyload
  %14 = add nsw i32 %13, %.sroa.15.0.copyload
  %15 = call i32 @llvm.smin.i32(i32 %.sroa.12.0.copyload, i32 %14)
  %16 = icmp slt i32 %13, %15
  br i1 %16, label %.lr.ph.preheader, label %.loopexit

.lr.ph.preheader:                                 ; preds = %11
  br label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %.lr.ph.preheader
  %.02038 = phi i32 [ %17, %.lr.ph ], [ %13, %.lr.ph.preheader ]
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !13

19:                                               ; preds = %7
  %20 = mul nsw i32 %.sroa.15.0.copyload, %2
  %21 = sub nsw i32 %.sroa.12.0.copyload, %20
  %22 = mul nsw i32 %21, %.sroa.15.0.copyload
  %23 = call i32 @llvm.smax.i32(i32 %.sroa.9.0.copyload, i32 %22)
  %.not25.not39 = icmp sgt i32 %21, %23
  br i1 %.not25.not39, label %.lr.ph41.preheader, label %.loopexit

.lr.ph41.preheader:                               ; preds = %19
  br label %.lr.ph41

.lr.ph41:                                         ; preds = %.lr.ph41, %.lr.ph41.preheader
  %.0.in40 = phi i32 [ %.0, %.lr.ph41 ], [ %21, %.lr.ph41.preheader ]
  %.0 = add nsw i32 %.0.in40, -1
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !15

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone willreturn }

!llvm.linker.options = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}
!llvm.module.flags = !{!6, !7, !8}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"clang version 14.0.6"}
!6 = !{i32 1, !"wchar_size", i32 2}
!7 = !{i32 7, !"PIC Level", i32 2}
!8 = !{i32 7, !"uwtable", i32 1}
!9 = distinct !{!9, !10}
!10 = !{!"llvm.loop.isvectorized", i32 1}
!11 = distinct !{!11, !12, !10}
!12 = !{!"llvm.loop.unroll.runtime.disable"}
!13 = distinct !{!13, !14}
!14 = !{!"llvm.loop.mustprogress"}
!15 = distinct !{!15, !14}
