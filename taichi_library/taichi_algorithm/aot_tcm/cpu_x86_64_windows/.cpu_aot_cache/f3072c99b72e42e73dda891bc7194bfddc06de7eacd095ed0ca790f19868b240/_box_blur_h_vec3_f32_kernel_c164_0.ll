; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.60*, void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.60 = type { i8*, %struct.LLVMRuntime.59*, i32, i64* }
%struct.LLVMRuntime.59 = type { %struct.PreallocatedMemoryChunk.55, %struct.PreallocatedMemoryChunk.55, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.56*], [1024 x %struct.NodeManager.57*], [1024 x i8*], i8*, %struct.RandState.58*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.55 = type { i8*, i8*, i64 }
%struct.ListManager.56 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.59* }
%struct.NodeManager.57 = type { %struct.LLVMRuntime.59*, i32, i32, i32, i32, %struct.ListManager.56*, %struct.ListManager.56*, %struct.ListManager.56*, i32 }
%struct.RandState.58 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_box_blur_h_vec3_f32_kernel_c164_0_kernel_0_serial(%struct.RuntimeContext.60* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.60* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 8
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %7, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 4
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = mul i32 %13, %4
  %20 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %7, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %20, i64 0, i32 14
  %22 = bitcast i8** %21 to i32**
  %23 = load i32*, i32** %22, align 8
  store i32 %19, i32* %23, align 4
  ret void
}

; Function Attrs: nounwind
define void @_box_blur_h_vec3_f32_kernel_c164_0_kernel_1_range_for(%struct.RuntimeContext.60* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.60* %context, %struct.RuntimeContext.60** %4, align 8
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.60*, i8*, i32)* @function_body, void (%struct.RuntimeContext.60*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.60* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.60* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
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
  %34 = add i32 %24, -8
  %35 = lshr i32 %34, 3
  %36 = add nuw nsw i32 %35, 1
  %min.iters.check = icmp ult i32 %24, 8
  %n.vec = and i32 %24, -8
  %ind.end = sub i32 %n.vec, %23
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %xtraiter = and i32 %36, 1
  %37 = icmp ult i32 %34, 8
  %unroll_iter = and i32 %36, 1073741822
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01523 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %160, %after_for3 ]
  %38 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  %43 = load i32, i32* %42, align 4
  %44 = sdiv i32 %.01523, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.01523
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %.01523, 0
  %49 = icmp ne i32 %45, %.01523
  %50 = and i1 %48, %47
  %51 = and i1 %50, %49
  %.neg16 = sext i1 %51 to i32
  %52 = add i32 %44, %.neg16
  %53 = mul i32 %52, %43
  %54 = sub i32 %.01523, %53
  %55 = getelementptr inbounds i8, i8* %40, i64 8
  %56 = bitcast i8* %55 to i32*
  %57 = load i32, i32* %56, align 4
  %58 = add i32 %57, -1
  br i1 %29, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %59 = load float*, float** %30, align 8
  %60 = load i32, i32* %31, align 4
  %61 = mul i32 %60, %52
  br i1 %min.iters.check, label %for_loop_body1.preheader, label %vector.ph

for_loop_body1.preheader:                         ; preds = %middle.block, %for_loop_body1.lr.ph
  %.020.ph = phi i32 [ %neg, %for_loop_body1.lr.ph ], [ %ind.end, %middle.block ]
  %.01219.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %115, %middle.block ]
  %.01318.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %114, %middle.block ]
  %.01417.ph = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %113, %middle.block ]
  %62 = sub i32 %28, %.020.ph
  %63 = add i32 %.020.ph, %.01523
  %64 = sub i32 %63, %53
  br label %for_loop_body1

vector.ph:                                        ; preds = %for_loop_body1.lr.ph
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %54, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert33 = insertelement <8 x i32> poison, i32 %58, i64 0
  %broadcast.splat34 = shufflevector <8 x i32> %broadcast.splatinsert33, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert35 = insertelement <8 x i32> poison, i32 %61, i64 0
  %broadcast.splat36 = shufflevector <8 x i32> %broadcast.splatinsert35, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %37, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv = phi i32 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next, %vector.body ]
  %vec.ind = phi <8 x i32> [ %vec.ind.next.1, %vector.body ], [ %induction, %vector.body.preheader ]
  %vec.phi = phi <8 x float> [ %96, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi31 = phi <8 x float> [ %95, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi32 = phi <8 x float> [ %94, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %65 = add <8 x i32> %vec.ind, %broadcast.splat
  %66 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %65, <8 x i32> zeroinitializer)
  %67 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat34, <8 x i32> %66)
  %68 = add <8 x i32> %broadcast.splat36, %67
  %69 = mul <8 x i32> %68, <i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3>
  %70 = sext <8 x i32> %69 to <8 x i64>
  %71 = getelementptr float, float* %59, <8 x i64> %70
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %71, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %72 = add <8 x i32> %69, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %73 = sext <8 x i32> %72 to <8 x i64>
  %74 = getelementptr float, float* %59, <8 x i64> %73
  %wide.masked.gather37 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %74, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %75 = add <8 x i32> %69, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %76 = sext <8 x i32> %75 to <8 x i64>
  %77 = getelementptr float, float* %59, <8 x i64> %76
  %wide.masked.gather38 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %77, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %78 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi32
  %79 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather37, %vec.phi31
  %80 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather38, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %81 = add <8 x i32> %vec.ind.next, %broadcast.splat
  %82 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %81, <8 x i32> zeroinitializer)
  %83 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat34, <8 x i32> %82)
  %84 = add <8 x i32> %broadcast.splat36, %83
  %85 = mul <8 x i32> %84, <i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3>
  %86 = sext <8 x i32> %85 to <8 x i64>
  %87 = getelementptr float, float* %59, <8 x i64> %86
  %wide.masked.gather.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %87, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %88 = add <8 x i32> %85, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %89 = sext <8 x i32> %88 to <8 x i64>
  %90 = getelementptr float, float* %59, <8 x i64> %89
  %wide.masked.gather37.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %90, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %91 = add <8 x i32> %85, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %92 = sext <8 x i32> %91 to <8 x i64>
  %93 = getelementptr float, float* %59, <8 x i64> %92
  %wide.masked.gather38.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %93, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %94 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.1, %78
  %95 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather37.1, %79
  %96 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather38.1, %80
  %vec.ind.next.1 = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %lsr.iv.next = add i32 %lsr.iv, -2
  %niter.ncmp.1 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa42.ph = phi <8 x float> [ undef, %vector.ph ], [ %94, %middle.block.unr-lcssa.loopexit ]
  %.lcssa41.ph = phi <8 x float> [ undef, %vector.ph ], [ %95, %middle.block.unr-lcssa.loopexit ]
  %.lcssa.ph = phi <8 x float> [ undef, %vector.ph ], [ %96, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %96, %middle.block.unr-lcssa.loopexit ]
  %vec.phi31.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %95, %middle.block.unr-lcssa.loopexit ]
  %vec.phi32.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %94, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %97 = add <8 x i32> %vec.ind.unr, %broadcast.splat
  %98 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %97, <8 x i32> zeroinitializer)
  %99 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat34, <8 x i32> %98)
  %100 = add <8 x i32> %broadcast.splat36, %99
  %101 = mul <8 x i32> %100, <i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3>
  %102 = sext <8 x i32> %101 to <8 x i64>
  %103 = getelementptr float, float* %59, <8 x i64> %102
  %wide.masked.gather.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %103, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %104 = add <8 x i32> %101, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %105 = sext <8 x i32> %104 to <8 x i64>
  %106 = getelementptr float, float* %59, <8 x i64> %105
  %wide.masked.gather37.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %106, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %107 = add <8 x i32> %101, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %108 = sext <8 x i32> %107 to <8 x i64>
  %109 = getelementptr float, float* %59, <8 x i64> %108
  %wide.masked.gather38.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %109, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %110 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather.epil, %vec.phi32.unr
  %111 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather37.epil, %vec.phi31.unr
  %112 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather38.epil, %vec.phi.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa42 = phi <8 x float> [ %.lcssa42.ph, %middle.block.unr-lcssa ], [ %110, %vector.body.epil ]
  %.lcssa41 = phi <8 x float> [ %.lcssa41.ph, %middle.block.unr-lcssa ], [ %111, %vector.body.epil ]
  %.lcssa = phi <8 x float> [ %.lcssa.ph, %middle.block.unr-lcssa ], [ %112, %vector.body.epil ]
  %113 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa42)
  %114 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa41)
  %115 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa)
  br label %for_loop_body1.preheader

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader
  %lsr.iv57 = phi i32 [ %64, %for_loop_body1.preheader ], [ %lsr.iv.next58, %for_loop_body1 ]
  %lsr.iv55 = phi i32 [ %62, %for_loop_body1.preheader ], [ %lsr.iv.next56, %for_loop_body1 ]
  %.01219 = phi float [ %133, %for_loop_body1 ], [ %.01219.ph, %for_loop_body1.preheader ]
  %.01318 = phi float [ %132, %for_loop_body1 ], [ %.01318.ph, %for_loop_body1.preheader ]
  %.01417 = phi float [ %131, %for_loop_body1 ], [ %.01417.ph, %for_loop_body1.preheader ]
  %116 = tail call i32 @llvm.smax.i32(i32 %lsr.iv57, i32 0)
  %117 = tail call i32 @llvm.smin.i32(i32 %58, i32 %116)
  %118 = add i32 %61, %117
  %119 = mul i32 %118, 3
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %59, i64 %120
  %122 = load float, float* %121, align 4
  %123 = add i32 %119, 1
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %59, i64 %124
  %126 = load float, float* %125, align 4
  %127 = add i32 %119, 2
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, float* %59, i64 %128
  %130 = load float, float* %129, align 4
  %131 = fadd reassoc ninf nsz float %122, %.01417
  %132 = fadd reassoc ninf nsz float %126, %.01318
  %133 = fadd reassoc ninf nsz float %130, %.01219
  %lsr.iv.next56 = add i32 %lsr.iv55, -1
  %lsr.iv.next58 = add i32 %lsr.iv57, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next56, 0
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1, !llvm.loop !11

after_for3.loopexit:                              ; preds = %for_loop_body1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.014.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %131, %after_for3.loopexit ]
  %.013.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %132, %after_for3.loopexit ]
  %.012.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %133, %after_for3.loopexit ]
  %134 = fdiv reassoc ninf nsz float %.014.lcssa, %26
  %135 = fdiv reassoc ninf nsz float %.013.lcssa, %26
  %136 = fdiv reassoc ninf nsz float %.012.lcssa, %26
  %137 = load float*, float** %32, align 8
  %138 = load i32, i32* %33, align 4
  %139 = mul i32 %138, %52
  %140 = add i32 %139, %54
  %141 = mul i32 %140, 3
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, float* %137, i64 %142
  store float %134, float* %143, align 4
  %144 = load float*, float** %32, align 8
  %145 = load i32, i32* %33, align 4
  %146 = mul i32 %145, %52
  %147 = add i32 %146, %54
  %148 = mul i32 %147, 3
  %149 = add i32 %148, 1
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, float* %144, i64 %150
  store float %135, float* %151, align 4
  %152 = load float*, float** %32, align 8
  %153 = load i32, i32* %33, align 4
  %154 = mul i32 %153, %52
  %155 = add i32 %154, %54
  %156 = mul i32 %155, 3
  %157 = add i32 %156, 2
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, float* %152, i64 %158
  store float %136, float* %159, align 4
  %160 = add nsw i32 %.01523, 1
  %exitcond26.not = icmp eq i32 %160, %19
  br i1 %exitcond26.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.60, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.60**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.60*, %struct.RuntimeContext.60** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.60* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.60* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !15

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
