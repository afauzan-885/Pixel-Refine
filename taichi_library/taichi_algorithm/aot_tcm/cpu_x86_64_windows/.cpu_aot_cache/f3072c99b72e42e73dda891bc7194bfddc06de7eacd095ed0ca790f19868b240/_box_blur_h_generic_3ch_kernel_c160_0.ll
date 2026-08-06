; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.24*, void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.24 = type { i8*, %struct.LLVMRuntime.23*, i32, i64* }
%struct.LLVMRuntime.23 = type { %struct.PreallocatedMemoryChunk.19, %struct.PreallocatedMemoryChunk.19, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.20*], [1024 x %struct.NodeManager.21*], [1024 x i8*], i8*, %struct.RandState.22*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.19 = type { i8*, i8*, i64 }
%struct.ListManager.20 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.23* }
%struct.NodeManager.21 = type { %struct.LLVMRuntime.23*, i32, i32, i32, i32, %struct.ListManager.20*, %struct.ListManager.20*, %struct.ListManager.20*, i32 }
%struct.RandState.22 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_box_blur_h_generic_3ch_kernel_c160_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 8
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %7, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 4
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = mul i32 %13, %4
  %20 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %7, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %20, i64 0, i32 14
  %22 = bitcast i8** %21 to i32**
  %23 = load i32*, i32** %22, align 8
  store i32 %19, i32* %23, align 4
  ret void
}

; Function Attrs: nounwind
define void @_box_blur_h_generic_3ch_kernel_c160_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.24* %context, %struct.RuntimeContext.24** %4, align 8
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.24*, i8*, i32)* @function_body, void (%struct.RuntimeContext.24*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 4
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
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %33 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %34 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %35 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %36 = add i32 %24, -8
  %37 = lshr i32 %36, 3
  %38 = add nuw nsw i32 %37, 1
  %min.iters.check = icmp ult i32 %24, 8
  %n.vec = and i32 %24, -8
  %ind.end = sub i32 %n.vec, %23
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %xtraiter = and i32 %38, 1
  %39 = icmp ult i32 %36, 8
  %unroll_iter = and i32 %38, 1073741822
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01523 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %166, %after_for3 ]
  %40 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %41 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %40, i64 0, i32 14
  %42 = load i8*, i8** %41, align 8
  %43 = getelementptr inbounds i8, i8* %42, i64 4
  %44 = bitcast i8* %43 to i32*
  %45 = load i32, i32* %44, align 4
  %46 = sdiv i32 %.01523, %45
  %47 = mul i32 %46, %45
  %48 = xor i32 %45, %.01523
  %49 = icmp slt i32 %48, 0
  %50 = icmp ne i32 %.01523, 0
  %51 = icmp ne i32 %47, %.01523
  %52 = and i1 %50, %49
  %53 = and i1 %52, %51
  %.neg16 = sext i1 %53 to i32
  %54 = add i32 %46, %.neg16
  %55 = mul i32 %54, %45
  %56 = sub i32 %.01523, %55
  %57 = getelementptr inbounds i8, i8* %42, i64 8
  %58 = bitcast i8* %57 to i32*
  %59 = load i32, i32* %58, align 4
  %60 = add i32 %59, -1
  br i1 %29, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %61 = load float*, float** %30, align 8
  %62 = load i32, i32* %31, align 4
  %63 = load i32, i32* %32, align 4
  %64 = mul i32 %62, %54
  br i1 %min.iters.check, label %for_loop_body1.preheader, label %vector.ph

for_loop_body1.preheader:                         ; preds = %middle.block, %for_loop_body1.lr.ph
  %.020.ph = phi i32 [ %neg, %for_loop_body1.lr.ph ], [ %ind.end, %middle.block ]
  %.01219.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %118, %middle.block ]
  %.01318.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %117, %middle.block ]
  %.01417.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %116, %middle.block ]
  %65 = sub i32 %28, %.020.ph
  %66 = add i32 %.020.ph, %.01523
  %67 = sub i32 %66, %55
  br label %for_loop_body1

vector.ph:                                        ; preds = %for_loop_body1.lr.ph
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %56, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert33 = insertelement <8 x i32> poison, i32 %60, i64 0
  %broadcast.splat34 = shufflevector <8 x i32> %broadcast.splatinsert33, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert35 = insertelement <8 x i32> poison, i32 %64, i64 0
  %broadcast.splat36 = shufflevector <8 x i32> %broadcast.splatinsert35, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert37 = insertelement <8 x i32> poison, i32 %63, i64 0
  %broadcast.splat38 = shufflevector <8 x i32> %broadcast.splatinsert37, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %39, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv = phi i32 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next, %vector.body ]
  %vec.ind = phi <8 x i32> [ %vec.ind.next.1, %vector.body ], [ %induction, %vector.body.preheader ]
  %vec.phi = phi <8 x float> [ %99, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi31 = phi <8 x float> [ %95, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi32 = phi <8 x float> [ %91, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %68 = add <8 x i32> %vec.ind, %broadcast.splat
  %69 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %68, <8 x i32> zeroinitializer)
  %70 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat34, <8 x i32> %69)
  %71 = add <8 x i32> %broadcast.splat36, %70
  %72 = mul <8 x i32> %71, %broadcast.splat38
  %73 = sext <8 x i32> %72 to <8 x i64>
  %74 = getelementptr float, float* %61, <8 x i64> %73
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %74, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %75 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi32
  %76 = add <8 x i32> %72, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %77 = sext <8 x i32> %76 to <8 x i64>
  %78 = getelementptr float, float* %61, <8 x i64> %77
  %wide.masked.gather39 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %78, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %79 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather39, %vec.phi31
  %80 = add <8 x i32> %72, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %81 = sext <8 x i32> %80 to <8 x i64>
  %82 = getelementptr float, float* %61, <8 x i64> %81
  %wide.masked.gather40 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %82, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %83 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather40, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %84 = add <8 x i32> %vec.ind.next, %broadcast.splat
  %85 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %84, <8 x i32> zeroinitializer)
  %86 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat34, <8 x i32> %85)
  %87 = add <8 x i32> %broadcast.splat36, %86
  %88 = mul <8 x i32> %87, %broadcast.splat38
  %89 = sext <8 x i32> %88 to <8 x i64>
  %90 = getelementptr float, float* %61, <8 x i64> %89
  %wide.masked.gather.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %90, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %91 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.1, %75
  %92 = add <8 x i32> %88, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %93 = sext <8 x i32> %92 to <8 x i64>
  %94 = getelementptr float, float* %61, <8 x i64> %93
  %wide.masked.gather39.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %94, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %95 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather39.1, %79
  %96 = add <8 x i32> %88, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %97 = sext <8 x i32> %96 to <8 x i64>
  %98 = getelementptr float, float* %61, <8 x i64> %97
  %wide.masked.gather40.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %98, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %99 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather40.1, %83
  %vec.ind.next.1 = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %lsr.iv.next = add i32 %lsr.iv, -2
  %niter.ncmp.1 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa44.ph = phi <8 x float> [ undef, %vector.ph ], [ %91, %middle.block.unr-lcssa.loopexit ]
  %.lcssa43.ph = phi <8 x float> [ undef, %vector.ph ], [ %95, %middle.block.unr-lcssa.loopexit ]
  %.lcssa.ph = phi <8 x float> [ undef, %vector.ph ], [ %99, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %99, %middle.block.unr-lcssa.loopexit ]
  %vec.phi31.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %95, %middle.block.unr-lcssa.loopexit ]
  %vec.phi32.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %91, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %100 = add <8 x i32> %vec.ind.unr, %broadcast.splat
  %101 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %100, <8 x i32> zeroinitializer)
  %102 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat34, <8 x i32> %101)
  %103 = add <8 x i32> %broadcast.splat36, %102
  %104 = mul <8 x i32> %103, %broadcast.splat38
  %105 = sext <8 x i32> %104 to <8 x i64>
  %106 = getelementptr float, float* %61, <8 x i64> %105
  %wide.masked.gather.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %106, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %107 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.epil, %vec.phi32.unr
  %108 = add <8 x i32> %104, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %109 = sext <8 x i32> %108 to <8 x i64>
  %110 = getelementptr float, float* %61, <8 x i64> %109
  %wide.masked.gather39.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %110, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %111 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather39.epil, %vec.phi31.unr
  %112 = add <8 x i32> %104, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %113 = sext <8 x i32> %112 to <8 x i64>
  %114 = getelementptr float, float* %61, <8 x i64> %113
  %wide.masked.gather40.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %114, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %115 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather40.epil, %vec.phi.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa44 = phi <8 x float> [ %.lcssa44.ph, %middle.block.unr-lcssa ], [ %107, %vector.body.epil ]
  %.lcssa43 = phi <8 x float> [ %.lcssa43.ph, %middle.block.unr-lcssa ], [ %111, %vector.body.epil ]
  %.lcssa = phi <8 x float> [ %.lcssa.ph, %middle.block.unr-lcssa ], [ %115, %vector.body.epil ]
  %116 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa44)
  %117 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa43)
  %118 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa)
  br label %for_loop_body1.preheader

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader
  %lsr.iv59 = phi i32 [ %67, %for_loop_body1.preheader ], [ %lsr.iv.next60, %for_loop_body1 ]
  %lsr.iv57 = phi i32 [ %65, %for_loop_body1.preheader ], [ %lsr.iv.next58, %for_loop_body1 ]
  %.01219 = phi float [ %136, %for_loop_body1 ], [ %.01219.ph, %for_loop_body1.preheader ]
  %.01318 = phi float [ %131, %for_loop_body1 ], [ %.01318.ph, %for_loop_body1.preheader ]
  %.01417 = phi float [ %126, %for_loop_body1 ], [ %.01417.ph, %for_loop_body1.preheader ]
  %119 = tail call i32 @llvm.smax.i32(i32 %lsr.iv59, i32 0)
  %120 = tail call i32 @llvm.smin.i32(i32 %60, i32 %119)
  %121 = add i32 %64, %120
  %122 = mul i32 %121, %63
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, float* %61, i64 %123
  %125 = load float, float* %124, align 4
  %126 = fadd reassoc ninf nsz float %125, %.01417
  %127 = add i32 %122, 1
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, float* %61, i64 %128
  %130 = load float, float* %129, align 4
  %131 = fadd reassoc ninf nsz float %130, %.01318
  %132 = add i32 %122, 2
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %61, i64 %133
  %135 = load float, float* %134, align 4
  %136 = fadd reassoc ninf nsz float %135, %.01219
  %lsr.iv.next58 = add i32 %lsr.iv57, -1
  %lsr.iv.next60 = add i32 %lsr.iv59, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next58, 0
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1, !llvm.loop !11

after_for3.loopexit:                              ; preds = %for_loop_body1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.014.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %126, %after_for3.loopexit ]
  %.013.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %131, %after_for3.loopexit ]
  %.012.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %136, %after_for3.loopexit ]
  %137 = fdiv reassoc ninf nsz float %.014.lcssa, %26
  %138 = load float*, float** %33, align 8
  %139 = load i32, i32* %34, align 4
  %140 = load i32, i32* %35, align 4
  %141 = mul i32 %139, %54
  %142 = add i32 %141, %56
  %143 = mul i32 %142, %140
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, float* %138, i64 %144
  store float %137, float* %145, align 4
  %146 = fdiv reassoc ninf nsz float %.013.lcssa, %26
  %147 = load float*, float** %33, align 8
  %148 = load i32, i32* %34, align 4
  %149 = load i32, i32* %35, align 4
  %150 = mul i32 %148, %54
  %151 = add i32 %150, %56
  %152 = mul i32 %151, %149
  %153 = add i32 %152, 1
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %147, i64 %154
  store float %146, float* %155, align 4
  %156 = fdiv reassoc ninf nsz float %.012.lcssa, %26
  %157 = load float*, float** %33, align 8
  %158 = load i32, i32* %34, align 4
  %159 = load i32, i32* %35, align 4
  %160 = mul i32 %158, %54
  %161 = add i32 %160, %56
  %162 = mul i32 %161, %159
  %163 = add i32 %162, 2
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %157, i64 %164
  store float %156, float* %165, align 4
  %166 = add nsw i32 %.01523, 1
  %exitcond26.not = icmp eq i32 %166, %19
  br i1 %exitcond26.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.24, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.24**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.24*, %struct.RuntimeContext.24** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.24* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.24* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !15

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
