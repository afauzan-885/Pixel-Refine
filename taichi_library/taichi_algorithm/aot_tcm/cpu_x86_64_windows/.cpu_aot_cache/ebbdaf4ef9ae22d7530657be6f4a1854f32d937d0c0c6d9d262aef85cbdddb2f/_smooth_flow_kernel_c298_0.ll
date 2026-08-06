; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.36*, void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.36 = type { i8*, %struct.LLVMRuntime.35*, i32, i64* }
%struct.LLVMRuntime.35 = type { %struct.PreallocatedMemoryChunk.31, %struct.PreallocatedMemoryChunk.31, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.32*], [1024 x %struct.NodeManager.33*], [1024 x i8*], i8*, %struct.RandState.34*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.31 = type { i8*, i8*, i64 }
%struct.ListManager.32 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.35* }
%struct.NodeManager.33 = type { %struct.LLVMRuntime.35*, i32, i32, i32, i32, %struct.ListManager.32*, %struct.ListManager.32*, %struct.ListManager.32*, i32 }
%struct.RandState.34 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_smooth_flow_kernel_c298_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 8
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = shl nuw i32 %13, 1
  %15 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 4
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = mul i32 %14, %4
  %21 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %21, i64 0, i32 14
  %23 = bitcast i8** %22 to i32**
  %24 = load i32*, i32** %23, align 8
  store i32 %20, i32* %24, align 4
  ret void
}

; Function Attrs: nounwind
define void @_smooth_flow_kernel_c298_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.36* %context, %struct.RuntimeContext.36** %4, align 8
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.36*, i8*, i32)* @function_body, void (%struct.RuntimeContext.36*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.36* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = add i32 %23, 1
  %neg = sub i32 0, %23
  %26 = icmp sgt i32 %25, %neg
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %33 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %34 = sext i32 %neg to i64
  %wide.trip.count = sext i32 %25 to i64
  %35 = xor i64 %34, -1
  %36 = add nsw i64 %35, %wide.trip.count
  %37 = sub nsw i64 %wide.trip.count, %34
  %38 = add nsw i64 %37, -8
  %39 = lshr i64 %38, 3
  %40 = add nuw nsw i64 %39, 1
  %min.iters.check = icmp ugt i64 %37, 7
  %.not = icmp ult i64 %36, 2147483648
  %or.cond = select i1 %min.iters.check, i1 %.not, i1 false
  %n.vec = and i64 %37, -8
  %ind.end = add nsw i64 %n.vec, %34
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %xtraiter = and i64 %40, 1
  %41 = icmp ult i64 %38, 8
  %unroll_iter = and i64 %40, 4611686018427387902
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %cmp.n = icmp eq i64 %37, %n.vec
  %42 = sub nsw i64 0, %wide.trip.count
  %43 = zext i32 %23 to i64
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01220 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %184, %after_for3 ]
  %44 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %45 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %44, i64 0, i32 14
  %46 = load i8*, i8** %45, align 8
  %47 = getelementptr inbounds i8, i8* %46, i64 4
  %48 = bitcast i8* %47 to i32*
  %49 = load i32, i32* %48, align 4
  %50 = sdiv i32 %.01220, %49
  %51 = mul i32 %50, %49
  %52 = xor i32 %49, %.01220
  %53 = icmp slt i32 %52, 0
  %54 = icmp ne i32 %.01220, 0
  %55 = icmp ne i32 %51, %.01220
  %56 = and i1 %54, %53
  %57 = and i1 %56, %55
  %.neg13 = sext i1 %57 to i32
  %58 = add i32 %50, %.neg13
  %59 = mul i32 %58, %49
  %60 = sub i32 %.01220, %59
  %61 = sdiv i32 %60, 2
  %62 = icmp slt i32 %60, 0
  %63 = shl nsw i32 %61, 1
  %64 = icmp ne i32 %63, %60
  %65 = and i1 %62, %64
  %.neg14 = sext i1 %65 to i32
  %66 = add i32 %61, %.neg14
  %.neg15 = mul i32 %66, -2
  %67 = add i32 %.neg15, %60
  %68 = getelementptr inbounds i8, i8* %46, i64 8
  %69 = bitcast i8* %68 to i32*
  %70 = load i32, i32* %69, align 4
  %71 = add i32 %70, -1
  br i1 %26, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %72 = load float*, float** %27, align 8
  %73 = load float*, float** %28, align 8
  %74 = load i32, i32* %29, align 4
  %75 = load i32, i32* %30, align 4
  %76 = mul i32 %74, %58
  br i1 %or.cond, label %vector.ph, label %for_loop_body1.preheader

vector.ph:                                        ; preds = %for_loop_body1.lr.ph
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %66, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert27 = insertelement <8 x i32> poison, i32 %71, i64 0
  %broadcast.splat28 = shufflevector <8 x i32> %broadcast.splatinsert27, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert29 = insertelement <8 x i32> poison, i32 %76, i64 0
  %broadcast.splat30 = shufflevector <8 x i32> %broadcast.splatinsert29, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert31 = insertelement <8 x i32> poison, i32 %75, i64 0
  %broadcast.splat32 = shufflevector <8 x i32> %broadcast.splatinsert31, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert33 = insertelement <8 x i32> poison, i32 %67, i64 0
  %broadcast.splat34 = shufflevector <8 x i32> %broadcast.splatinsert33, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %41, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv48 = phi i64 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next49, %vector.body ]
  %lsr.iv = phi i64 [ 0, %vector.body.preheader ], [ %lsr.iv.next, %vector.body ]
  %index = phi i64 [ %index.next.1, %vector.body ], [ 0, %vector.body.preheader ]
  %vec.phi = phi <8 x float> [ %103, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi26 = phi <8 x float> [ %102, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.ind = phi <8 x i32> [ %vec.ind.next.1, %vector.body ], [ %induction, %vector.body.preheader ]
  %77 = add <8 x i32> %broadcast.splat, %vec.ind
  %78 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %77, <8 x i32> zeroinitializer)
  %79 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %78, <8 x i32> %broadcast.splat28)
  %80 = ashr exact i64 %lsr.iv, 32
  %81 = getelementptr float, float* %72, i64 %80
  %82 = bitcast float* %81 to <8 x float>*
  %wide.load = load <8 x float>, <8 x float>* %82, align 4
  %83 = add <8 x i32> %broadcast.splat30, %79
  %84 = mul <8 x i32> %83, %broadcast.splat32
  %85 = add <8 x i32> %84, %broadcast.splat34
  %86 = sext <8 x i32> %85 to <8 x i64>
  %87 = getelementptr float, float* %73, <8 x i64> %86
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %87, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %88 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.load
  %89 = fadd reassoc ninf nsz <8 x float> %88, %vec.phi26
  %90 = fadd reassoc ninf nsz <8 x float> %wide.load, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %91 = add <8 x i32> %broadcast.splat, %vec.ind.next
  %92 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %91, <8 x i32> zeroinitializer)
  %93 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %92, <8 x i32> %broadcast.splat28)
  %94 = getelementptr float, float* %81, i64 8
  %95 = bitcast float* %94 to <8 x float>*
  %wide.load.1 = load <8 x float>, <8 x float>* %95, align 4
  %96 = add <8 x i32> %broadcast.splat30, %93
  %97 = mul <8 x i32> %96, %broadcast.splat32
  %98 = add <8 x i32> %97, %broadcast.splat34
  %99 = sext <8 x i32> %98 to <8 x i64>
  %100 = getelementptr float, float* %73, <8 x i64> %99
  %wide.masked.gather.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %100, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %101 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather.1, %wide.load.1
  %102 = fadd reassoc ninf nsz <8 x float> %101, %89
  %103 = fadd reassoc ninf nsz <8 x float> %wide.load.1, %90
  %index.next.1 = add i64 %index, 16
  %vec.ind.next.1 = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %lsr.iv.next = add i64 %lsr.iv, 68719476736
  %lsr.iv.next49 = add i64 %lsr.iv48, -2
  %niter.ncmp.1 = icmp eq i64 %lsr.iv.next49, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa36.ph = phi <8 x float> [ undef, %vector.ph ], [ %102, %middle.block.unr-lcssa.loopexit ]
  %.lcssa.ph = phi <8 x float> [ undef, %vector.ph ], [ %103, %middle.block.unr-lcssa.loopexit ]
  %index.unr = phi i64 [ 0, %vector.ph ], [ %index.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %103, %middle.block.unr-lcssa.loopexit ]
  %vec.phi26.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %102, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %104 = add <8 x i32> %broadcast.splat, %vec.ind.unr
  %105 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %104, <8 x i32> zeroinitializer)
  %106 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %105, <8 x i32> %broadcast.splat28)
  %sext.epil = shl i64 %index.unr, 32
  %107 = ashr exact i64 %sext.epil, 32
  %108 = getelementptr float, float* %72, i64 %107
  %109 = bitcast float* %108 to <8 x float>*
  %wide.load.epil = load <8 x float>, <8 x float>* %109, align 4
  %110 = add <8 x i32> %broadcast.splat30, %106
  %111 = mul <8 x i32> %110, %broadcast.splat32
  %112 = add <8 x i32> %111, %broadcast.splat34
  %113 = sext <8 x i32> %112 to <8 x i64>
  %114 = getelementptr float, float* %73, <8 x i64> %113
  %wide.masked.gather.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %114, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %115 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather.epil, %wide.load.epil
  %116 = fadd reassoc ninf nsz <8 x float> %115, %vec.phi26.unr
  %117 = fadd reassoc ninf nsz <8 x float> %wide.load.epil, %vec.phi.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa36 = phi <8 x float> [ %.lcssa36.ph, %middle.block.unr-lcssa ], [ %116, %vector.body.epil ]
  %.lcssa = phi <8 x float> [ %.lcssa.ph, %middle.block.unr-lcssa ], [ %117, %vector.body.epil ]
  %118 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa36)
  %119 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa)
  br i1 %cmp.n, label %after_for3, label %for_loop_body1.preheader

for_loop_body1.preheader:                         ; preds = %middle.block, %for_loop_body1.lr.ph
  %indvars.iv.ph = phi i64 [ %34, %for_loop_body1.lr.ph ], [ %ind.end, %middle.block ]
  %.01017.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %119, %middle.block ]
  %.01116.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %118, %middle.block ]
  %120 = sub nsw i64 %wide.trip.count, %indvars.iv.ph
  %121 = xor i64 %indvars.iv.ph, -1
  %xtraiter41 = and i64 %120, 1
  %lcmp.mod42.not = icmp eq i64 %xtraiter41, 0
  br i1 %lcmp.mod42.not, label %for_loop_body1.prol.loopexit, label %for_loop_body1.prol

for_loop_body1.prol:                              ; preds = %for_loop_body1.preheader
  %122 = trunc i64 %indvars.iv.ph to i32
  %123 = add i32 %66, %122
  %124 = tail call i32 @llvm.smax.i32(i32 %123, i32 0)
  %125 = tail call i32 @llvm.smin.i32(i32 %124, i32 %71)
  %126 = add i32 %23, %122
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, float* %72, i64 %127
  %129 = load float, float* %128, align 4
  %130 = add i32 %76, %125
  %131 = mul i32 %130, %75
  %132 = add i32 %131, %67
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %73, i64 %133
  %135 = load float, float* %134, align 4
  %136 = fmul reassoc ninf nsz float %135, %129
  %137 = fadd reassoc ninf nsz float %136, %.01116.ph
  %138 = fadd reassoc ninf nsz float %129, %.01017.ph
  %indvars.iv.next.prol = add nsw i64 %indvars.iv.ph, 1
  br label %for_loop_body1.prol.loopexit

for_loop_body1.prol.loopexit:                     ; preds = %for_loop_body1.prol, %for_loop_body1.preheader
  %.lcssa38.unr = phi float [ undef, %for_loop_body1.preheader ], [ %137, %for_loop_body1.prol ]
  %.lcssa37.unr = phi float [ undef, %for_loop_body1.preheader ], [ %138, %for_loop_body1.prol ]
  %indvars.iv.unr = phi i64 [ %indvars.iv.ph, %for_loop_body1.preheader ], [ %indvars.iv.next.prol, %for_loop_body1.prol ]
  %.01017.unr = phi float [ %.01017.ph, %for_loop_body1.preheader ], [ %138, %for_loop_body1.prol ]
  %.01116.unr = phi float [ %.01116.ph, %for_loop_body1.preheader ], [ %137, %for_loop_body1.prol ]
  %139 = icmp eq i64 %121, %42
  br i1 %139, label %after_for3, label %for_loop_body1.preheader47

for_loop_body1.preheader47:                       ; preds = %for_loop_body1.prol.loopexit
  %140 = zext i32 %66 to i64
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader47
  %indvars.iv = phi i64 [ %indvars.iv.next.1, %for_loop_body1 ], [ %indvars.iv.unr, %for_loop_body1.preheader47 ]
  %.01017 = phi float [ %172, %for_loop_body1 ], [ %.01017.unr, %for_loop_body1.preheader47 ]
  %.01116 = phi float [ %171, %for_loop_body1 ], [ %.01116.unr, %for_loop_body1.preheader47 ]
  %141 = add i64 %140, %indvars.iv
  %tmp52 = trunc i64 %141 to i32
  %142 = tail call i32 @llvm.smax.i32(i32 %tmp52, i32 0)
  %143 = tail call i32 @llvm.smin.i32(i32 %142, i32 %71)
  %144 = add i64 %43, %indvars.iv
  %tmp51 = trunc i64 %144 to i32
  %145 = sext i32 %tmp51 to i64
  %146 = getelementptr float, float* %72, i64 %145
  %147 = load float, float* %146, align 4
  %148 = add i32 %76, %143
  %149 = mul i32 %148, %75
  %150 = add i32 %149, %67
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %73, i64 %151
  %153 = load float, float* %152, align 4
  %154 = fmul reassoc ninf nsz float %153, %147
  %155 = fadd reassoc ninf nsz float %154, %.01116
  %156 = fadd reassoc ninf nsz float %147, %.01017
  %157 = add i64 %141, 1
  %tmp = trunc i64 %157 to i32
  %158 = tail call i32 @llvm.smax.i32(i32 %tmp, i32 0)
  %159 = tail call i32 @llvm.smin.i32(i32 %158, i32 %71)
  %160 = add i64 %144, 1
  %tmp50 = trunc i64 %160 to i32
  %161 = sext i32 %tmp50 to i64
  %162 = getelementptr float, float* %72, i64 %161
  %163 = load float, float* %162, align 4
  %164 = add i32 %76, %159
  %165 = mul i32 %164, %75
  %166 = add i32 %165, %67
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, float* %73, i64 %167
  %169 = load float, float* %168, align 4
  %170 = fmul reassoc ninf nsz float %169, %163
  %171 = fadd reassoc ninf nsz float %170, %155
  %172 = fadd reassoc ninf nsz float %163, %156
  %indvars.iv.next.1 = add nsw i64 %indvars.iv, 2
  %exitcond.not.1 = icmp eq i64 %wide.trip.count, %indvars.iv.next.1
  br i1 %exitcond.not.1, label %after_for3.loopexit, label %for_loop_body1, !llvm.loop !11

after_for3.loopexit:                              ; preds = %for_loop_body1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body1.prol.loopexit, %middle.block, %for_loop_body
  %.011.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %118, %middle.block ], [ %.lcssa38.unr, %for_loop_body1.prol.loopexit ], [ %171, %after_for3.loopexit ]
  %.010.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %119, %middle.block ], [ %.lcssa37.unr, %for_loop_body1.prol.loopexit ], [ %172, %after_for3.loopexit ]
  %173 = fadd reassoc ninf nsz float %.010.lcssa, 0x3D71979980000000
  %174 = fdiv reassoc ninf nsz float %.011.lcssa, %173
  %175 = load float*, float** %31, align 8
  %176 = load i32, i32* %32, align 4
  %177 = load i32, i32* %33, align 4
  %178 = mul i32 %176, %58
  %179 = add i32 %178, %66
  %180 = mul i32 %179, %177
  %181 = add i32 %180, %67
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, float* %175, i64 %182
  store float %174, float* %183, align 4
  %184 = add nsw i32 %.01220, 1
  %exitcond23.not = icmp eq i32 %184, %19
  br i1 %exitcond23.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.36, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.36**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.36*, %struct.RuntimeContext.36** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.36* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.36* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !12

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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !14

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
!11 = distinct !{!11, !10}
!12 = distinct !{!12, !13}
!13 = !{!"llvm.loop.mustprogress"}
!14 = distinct !{!14, !13}
