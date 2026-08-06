; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.96*, void (%struct.RuntimeContext.96*, i8*)*, void (%struct.RuntimeContext.96*, i8*, i32)*, void (%struct.RuntimeContext.96*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.96 = type { i8*, %struct.LLVMRuntime.95*, i32, i64* }
%struct.LLVMRuntime.95 = type { %struct.PreallocatedMemoryChunk.91, %struct.PreallocatedMemoryChunk.91, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.92*], [1024 x %struct.NodeManager.93*], [1024 x i8*], i8*, %struct.RandState.94*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.91 = type { i8*, i8*, i64 }
%struct.ListManager.92 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.95* }
%struct.NodeManager.93 = type { %struct.LLVMRuntime.95*, i32, i32, i32, i32, %struct.ListManager.92*, %struct.ListManager.92*, %struct.ListManager.92*, i32 }
%struct.RandState.94 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_box_blur_v_generic_1ch_kernel_c172_0_kernel_0_serial(%struct.RuntimeContext.96* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.96* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 4
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = mul i32 %14, %10
  %21 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %21, i64 0, i32 14
  %23 = bitcast i8** %22 to i32**
  %24 = load i32*, i32** %23, align 8
  store i32 %20, i32* %24, align 4
  ret void
}

; Function Attrs: nounwind
define void @_box_blur_v_generic_1ch_kernel_c172_0_kernel_1_range_for(%struct.RuntimeContext.96* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.96* %context, %struct.RuntimeContext.96** %4, align 8
  store void (%struct.RuntimeContext.96*, i8*)* null, void (%struct.RuntimeContext.96*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.96*, i8*, i32)* @function_body, void (%struct.RuntimeContext.96*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.96*, i8*)* null, void (%struct.RuntimeContext.96*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.96* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.96* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
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
  %.0913.us = phi i32 [ %133, %for_loop_test4.after_for3_crit_edge.us ], [ %17, %for_loop_body.us.preheader ]
  %39 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %3, align 8
  %40 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %39, i64 0, i32 14
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
  br i1 %min.iters.check, label %for_loop_body1.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body.us
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %53, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert23 = insertelement <8 x i32> poison, i32 %59, i64 0
  %broadcast.splat24 = shufflevector <8 x i32> %broadcast.splatinsert23, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert27 = insertelement <8 x i32> poison, i32 %61, i64 0
  %broadcast.splat28 = shufflevector <8 x i32> %broadcast.splatinsert27, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert31 = insertelement <8 x i32> poison, i32 %55, i64 0
  %broadcast.splat32 = shufflevector <8 x i32> %broadcast.splatinsert31, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %37, label %middle.block.unr-lcssa, label %vector.ph.new

vector.ph.new:                                    ; preds = %vector.ph
  %.scalar = add i32 %53, 8
  %62 = insertelement <8 x i32> poison, i32 %.scalar, i64 0
  %63 = shufflevector <8 x i32> %62, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph.new
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %unroll_iter, %vector.ph.new ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph.new ], [ %vec.ind.next.1, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph.new ], [ %94, %vector.body ]
  %vec.phi20 = phi <8 x float> [ zeroinitializer, %vector.ph.new ], [ %95, %vector.body ]
  %64 = add <8 x i32> %vec.ind, %broadcast.splat
  %65 = add <8 x i32> %63, %vec.ind
  %66 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %64, <8 x i32> zeroinitializer)
  %67 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %65, <8 x i32> zeroinitializer)
  %68 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %66)
  %69 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %67)
  %70 = mul <8 x i32> %broadcast.splat28, %68
  %71 = mul <8 x i32> %broadcast.splat28, %69
  %72 = add <8 x i32> %70, %broadcast.splat32
  %73 = add <8 x i32> %71, %broadcast.splat32
  %74 = sext <8 x i32> %72 to <8 x i64>
  %75 = sext <8 x i32> %73 to <8 x i64>
  %76 = getelementptr float, float* %60, <8 x i64> %74
  %77 = getelementptr float, float* %60, <8 x i64> %75
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %76, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather35 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %77, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %78 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi
  %79 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather35, %vec.phi20
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %80 = add <8 x i32> %vec.ind.next, %broadcast.splat
  %81 = add <8 x i32> %63, %vec.ind.next
  %82 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %80, <8 x i32> zeroinitializer)
  %83 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %81, <8 x i32> zeroinitializer)
  %84 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %82)
  %85 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %83)
  %86 = mul <8 x i32> %broadcast.splat28, %84
  %87 = mul <8 x i32> %broadcast.splat28, %85
  %88 = add <8 x i32> %86, %broadcast.splat32
  %89 = add <8 x i32> %87, %broadcast.splat32
  %90 = sext <8 x i32> %88 to <8 x i64>
  %91 = sext <8 x i32> %89 to <8 x i64>
  %92 = getelementptr float, float* %60, <8 x i64> %90
  %93 = getelementptr float, float* %60, <8 x i64> %91
  %wide.masked.gather.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %92, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather35.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %93, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %94 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.1, %78
  %95 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather35.1, %79
  %vec.ind.next.1 = add <8 x i32> %vec.ind, <i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32>
  %lsr.iv.next = add i32 %lsr.iv, -2
  %niter.ncmp.1 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa37.ph = phi <8 x float> [ undef, %vector.ph ], [ %94, %middle.block.unr-lcssa.loopexit ]
  %.lcssa.ph = phi <8 x float> [ undef, %vector.ph ], [ %95, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %94, %middle.block.unr-lcssa.loopexit ]
  %vec.phi20.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %95, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %96 = add <8 x i32> %vec.ind.unr, %broadcast.splat
  %.scalar.epil = add i32 %53, 8
  %97 = insertelement <8 x i32> poison, i32 %.scalar.epil, i64 0
  %98 = shufflevector <8 x i32> %97, <8 x i32> poison, <8 x i32> zeroinitializer
  %99 = add <8 x i32> %98, %vec.ind.unr
  %100 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %96, <8 x i32> zeroinitializer)
  %101 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %99, <8 x i32> zeroinitializer)
  %102 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %100)
  %103 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat24, <8 x i32> %101)
  %104 = mul <8 x i32> %broadcast.splat28, %102
  %105 = mul <8 x i32> %broadcast.splat28, %103
  %106 = add <8 x i32> %104, %broadcast.splat32
  %107 = add <8 x i32> %105, %broadcast.splat32
  %108 = sext <8 x i32> %106 to <8 x i64>
  %109 = sext <8 x i32> %107 to <8 x i64>
  %110 = getelementptr float, float* %60, <8 x i64> %108
  %111 = getelementptr float, float* %60, <8 x i64> %109
  %wide.masked.gather.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %110, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather35.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %111, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %112 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.epil, %vec.phi.unr
  %113 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather35.epil, %vec.phi20.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa37 = phi <8 x float> [ %.lcssa37.ph, %middle.block.unr-lcssa ], [ %112, %vector.body.epil ]
  %.lcssa = phi <8 x float> [ %.lcssa.ph, %middle.block.unr-lcssa ], [ %113, %vector.body.epil ]
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %.lcssa, %.lcssa37
  %114 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx)
  br label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %middle.block, %for_loop_body.us
  %.012.us.ph = phi i32 [ %neg, %for_loop_body.us ], [ %ind.end, %middle.block ]
  %.0811.us.ph = phi float [ 0.000000e+00, %for_loop_body.us ], [ %114, %middle.block ]
  %115 = sub i32 %28, %.012.us.ph
  %116 = add i32 %.012.us.ph, %45
  %117 = add i32 %116, %.neg10.us
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader
  %lsr.iv47 = phi i32 [ %117, %for_loop_body1.us.preheader ], [ %lsr.iv.next48, %for_loop_body1.us ]
  %lsr.iv45 = phi i32 [ %115, %for_loop_body1.us.preheader ], [ %lsr.iv.next46, %for_loop_body1.us ]
  %.0811.us = phi float [ %125, %for_loop_body1.us ], [ %.0811.us.ph, %for_loop_body1.us.preheader ]
  %118 = tail call i32 @llvm.smax.i32(i32 %lsr.iv47, i32 0)
  %119 = tail call i32 @llvm.smin.i32(i32 %59, i32 %118)
  %120 = mul i32 %61, %119
  %121 = add i32 %120, %55
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, float* %60, i64 %122
  %124 = load float, float* %123, align 4
  %125 = fadd reassoc ninf nsz float %124, %.0811.us
  %lsr.iv.next46 = add i32 %lsr.iv45, -1
  %lsr.iv.next48 = add i32 %lsr.iv47, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next46, 0
  br i1 %exitcond.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us, !llvm.loop !11

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us
  %126 = fdiv reassoc ninf nsz float %125, %26
  %127 = load float*, float** %32, align 8
  %128 = load i32, i32* %33, align 4
  %129 = mul i32 %128, %53
  %130 = add i32 %129, %55
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, float* %127, i64 %131
  store float %126, float* %132, align 4
  %133 = add nsw i32 %.0913.us, 1
  %exitcond15.not = icmp eq i32 %133, %19
  br i1 %exitcond15.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.0913 = phi i32 [ %156, %for_loop_body ], [ %17, %for_loop_body.preheader ]
  %134 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %3, align 8
  %135 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %134, i64 0, i32 14
  %136 = load i8*, i8** %135, align 8
  %137 = getelementptr inbounds i8, i8* %136, i64 4
  %138 = bitcast i8* %137 to i32*
  %139 = load i32, i32* %138, align 4
  %140 = sdiv i32 %.0913, %139
  %141 = mul i32 %140, %139
  %142 = xor i32 %139, %.0913
  %143 = icmp slt i32 %142, 0
  %144 = icmp ne i32 %.0913, 0
  %145 = icmp ne i32 %.0913, %141
  %146 = and i1 %144, %143
  %147 = and i1 %146, %145
  %.neg10 = sext i1 %147 to i32
  %148 = add i32 %140, %.neg10
  %149 = load float*, float** %32, align 8
  %150 = load i32, i32* %33, align 4
  %151 = sub i32 %150, %139
  %152 = mul i32 %151, %148
  %153 = add i32 %.0913, %152
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %149, i64 %154
  store float %38, float* %155, align 4
  %156 = add nsw i32 %.0913, 1
  %exitcond16.not = icmp eq i32 %19, %156
  br i1 %exitcond16.not, label %after_for.loopexit44, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit44:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit44, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.96, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.96**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.96*, %struct.RuntimeContext.96** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.96*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.96*, i8*)*, void (%struct.RuntimeContext.96*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.96*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.96*, i8*, i32)*, void (%struct.RuntimeContext.96*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.96*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.96*, i8*)*, void (%struct.RuntimeContext.96*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.96*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.96* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.96* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.96* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.96* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.96* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !15

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.96*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.96* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
