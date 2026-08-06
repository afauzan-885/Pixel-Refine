; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.210*, void (%struct.RuntimeContext.210*, i8*)*, void (%struct.RuntimeContext.210*, i8*, i32)*, void (%struct.RuntimeContext.210*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.210 = type { i8*, %struct.LLVMRuntime.209*, i32, i64* }
%struct.LLVMRuntime.209 = type { %struct.PreallocatedMemoryChunk.205, %struct.PreallocatedMemoryChunk.205, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.206*], [1024 x %struct.NodeManager.207*], [1024 x i8*], i8*, %struct.RandState.208*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.205 = type { i8*, i8*, i64 }
%struct.ListManager.206 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.209* }
%struct.NodeManager.207 = type { %struct.LLVMRuntime.209*, i32, i32, i32, i32, %struct.ListManager.206*, %struct.ListManager.206*, %struct.ListManager.206*, i32 }
%struct.RandState.208 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @math_matmul_kernel_c730_0_kernel_0_serial(%struct.RuntimeContext.210* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.210* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 4
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.210, %struct.RuntimeContext.210* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.209*, %struct.LLVMRuntime.209** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.209, %struct.LLVMRuntime.209* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.209*, %struct.LLVMRuntime.209** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.209, %struct.LLVMRuntime.209* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @math_matmul_kernel_c730_0_kernel_1_range_for(%struct.RuntimeContext.210* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.210* %context, %struct.RuntimeContext.210** %4, align 8
  store void (%struct.RuntimeContext.210*, i8*)* null, void (%struct.RuntimeContext.210*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.210*, i8*, i32)* @function_body, void (%struct.RuntimeContext.210*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.210*, i8*)* null, void (%struct.RuntimeContext.210*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.210, %struct.RuntimeContext.210* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.209*, %struct.LLVMRuntime.209** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.209, %struct.LLVMRuntime.209* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.209, %struct.LLVMRuntime.209* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.210* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.210, %struct.RuntimeContext.210* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.209*, %struct.LLVMRuntime.209** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.209, %struct.LLVMRuntime.209* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.210* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = icmp sgt i32 %23, 0
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  br i1 %25, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  br label %for_loop_body

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %wide.trip.count = zext i32 %23 to i64
  %32 = add nsw i64 %wide.trip.count, -1
  %33 = and i64 %wide.trip.count, 4294967280
  %34 = add nsw i64 %33, -16
  %35 = lshr exact i64 %34, 4
  %36 = add nuw nsw i64 %35, 1
  %min.iters.check = icmp ult i32 %23, 16
  %37 = trunc i64 %32 to i32
  %38 = icmp ugt i64 %32, 4294967295
  %xtraiter = and i64 %36, 1
  %39 = icmp eq i64 %34, 0
  %unroll_iter = and i64 %36, 2305843009213693950
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %cmp.n = icmp eq i64 %33, %wide.trip.count
  %xtraiter30 = and i64 %wide.trip.count, 3
  %lcmp.mod31.not = icmp eq i64 %xtraiter30, 0
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %.0913.us = phi i32 [ %194, %for_loop_test4.after_for3_crit_edge.us ], [ %17, %for_loop_body.us.preheader ]
  %40 = load %struct.LLVMRuntime.209*, %struct.LLVMRuntime.209** %3, align 8
  %41 = getelementptr inbounds %struct.LLVMRuntime.209, %struct.LLVMRuntime.209* %40, i64 0, i32 14
  %42 = load i8*, i8** %41, align 8
  %43 = getelementptr inbounds i8, i8* %42, i64 4
  %44 = bitcast i8* %43 to i32*
  %45 = load i32, i32* %44, align 4
  %46 = sdiv i32 %.0913.us, %45
  %47 = mul i32 %46, %45
  %48 = xor i32 %45, %.0913.us
  %49 = icmp slt i32 %48, 0
  %50 = icmp ne i32 %.0913.us, 0
  %51 = icmp ne i32 %47, %.0913.us
  %52 = and i1 %50, %49
  %53 = and i1 %52, %51
  %.neg10.us = sext i1 %53 to i32
  %54 = add i32 %46, %.neg10.us
  %55 = mul i32 %54, %45
  %56 = sub i32 %.0913.us, %55
  %57 = load float*, float** %26, align 8
  %58 = load i32, i32* %27, align 4
  %59 = mul i32 %58, %54
  %60 = load float*, float** %28, align 8
  %61 = load i32, i32* %29, align 4
  br i1 %min.iters.check, label %for_loop_body1.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %for_loop_body.us
  %62 = add i32 %59, %37
  %63 = icmp slt i32 %62, %59
  %64 = or i1 %63, %38
  %ident.check = icmp ne i32 %61, 1
  %65 = add i32 %56, %37
  %66 = icmp slt i32 %65, %56
  %67 = or i1 %64, %ident.check
  %68 = or i1 %66, %67
  br i1 %68, label %for_loop_body1.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %vector.scevcheck
  br i1 %39, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  %69 = shl i32 %61, 4
  %70 = shl i32 %61, 5
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv40 = phi i64 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next41, %vector.body ]
  %lsr.iv38 = phi i32 [ %56, %vector.body.preheader ], [ %lsr.iv.next39, %vector.body ]
  %lsr.iv = phi i32 [ %59, %vector.body.preheader ], [ %lsr.iv.next, %vector.body ]
  %index = phi i64 [ %index.next.1, %vector.body ], [ 0, %vector.body.preheader ]
  %vec.phi = phi <8 x float> [ %99, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi20 = phi <8 x float> [ %100, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %71 = sext i32 %lsr.iv to i64
  %72 = getelementptr float, float* %57, i64 %71
  %73 = bitcast float* %72 to <8 x float>*
  %wide.load = load <8 x float>, <8 x float>* %73, align 4
  %74 = getelementptr float, float* %72, i64 8
  %75 = bitcast float* %74 to <8 x float>*
  %wide.load21 = load <8 x float>, <8 x float>* %75, align 4
  %76 = sext i32 %lsr.iv38 to i64
  %77 = getelementptr float, float* %60, i64 %76
  %78 = bitcast float* %77 to <8 x float>*
  %wide.load22 = load <8 x float>, <8 x float>* %78, align 4
  %79 = getelementptr float, float* %77, i64 8
  %80 = bitcast float* %79 to <8 x float>*
  %wide.load23 = load <8 x float>, <8 x float>* %80, align 4
  %81 = fmul reassoc ninf nsz <8 x float> %wide.load22, %wide.load
  %82 = fmul reassoc ninf nsz <8 x float> %wide.load23, %wide.load21
  %83 = fadd reassoc ninf nsz <8 x float> %81, %vec.phi
  %84 = fadd reassoc ninf nsz <8 x float> %82, %vec.phi20
  %85 = add i32 %lsr.iv, 16
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, float* %57, i64 %86
  %88 = bitcast float* %87 to <8 x float>*
  %wide.load.1 = load <8 x float>, <8 x float>* %88, align 4
  %89 = getelementptr float, float* %87, i64 8
  %90 = bitcast float* %89 to <8 x float>*
  %wide.load21.1 = load <8 x float>, <8 x float>* %90, align 4
  %91 = add i32 %69, %lsr.iv38
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, float* %60, i64 %92
  %94 = bitcast float* %93 to <8 x float>*
  %wide.load22.1 = load <8 x float>, <8 x float>* %94, align 4
  %95 = getelementptr float, float* %93, i64 8
  %96 = bitcast float* %95 to <8 x float>*
  %wide.load23.1 = load <8 x float>, <8 x float>* %96, align 4
  %97 = fmul reassoc ninf nsz <8 x float> %wide.load22.1, %wide.load.1
  %98 = fmul reassoc ninf nsz <8 x float> %wide.load23.1, %wide.load21.1
  %99 = fadd reassoc ninf nsz <8 x float> %97, %83
  %100 = fadd reassoc ninf nsz <8 x float> %98, %84
  %index.next.1 = add i64 %index, 32
  %lsr.iv.next = add i32 %lsr.iv, 32
  %lsr.iv.next39 = add i32 %lsr.iv38, %70
  %lsr.iv.next41 = add i64 %lsr.iv40, -2
  %niter.ncmp.1 = icmp eq i64 %lsr.iv.next41, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa26.ph = phi <8 x float> [ undef, %vector.ph ], [ %99, %middle.block.unr-lcssa.loopexit ]
  %.lcssa25.ph = phi <8 x float> [ undef, %vector.ph ], [ %100, %middle.block.unr-lcssa.loopexit ]
  %index.unr = phi i64 [ 0, %vector.ph ], [ %index.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %99, %middle.block.unr-lcssa.loopexit ]
  %vec.phi20.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %100, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %101 = trunc i64 %index.unr to i32
  %102 = add i32 %59, %101
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %57, i64 %103
  %105 = bitcast float* %104 to <8 x float>*
  %wide.load.epil = load <8 x float>, <8 x float>* %105, align 4
  %106 = getelementptr float, float* %104, i64 8
  %107 = bitcast float* %106 to <8 x float>*
  %wide.load21.epil = load <8 x float>, <8 x float>* %107, align 4
  %108 = mul i32 %61, %101
  %109 = add i32 %108, %56
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, float* %60, i64 %110
  %112 = bitcast float* %111 to <8 x float>*
  %wide.load22.epil = load <8 x float>, <8 x float>* %112, align 4
  %113 = getelementptr float, float* %111, i64 8
  %114 = bitcast float* %113 to <8 x float>*
  %wide.load23.epil = load <8 x float>, <8 x float>* %114, align 4
  %115 = fmul reassoc ninf nsz <8 x float> %wide.load22.epil, %wide.load.epil
  %116 = fmul reassoc ninf nsz <8 x float> %wide.load23.epil, %wide.load21.epil
  %117 = fadd reassoc ninf nsz <8 x float> %115, %vec.phi.unr
  %118 = fadd reassoc ninf nsz <8 x float> %116, %vec.phi20.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa26 = phi <8 x float> [ %.lcssa26.ph, %middle.block.unr-lcssa ], [ %117, %vector.body.epil ]
  %.lcssa25 = phi <8 x float> [ %.lcssa25.ph, %middle.block.unr-lcssa ], [ %118, %vector.body.epil ]
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %.lcssa25, %.lcssa26
  %119 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx)
  br i1 %cmp.n, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %middle.block, %vector.scevcheck, %for_loop_body.us
  %indvars.iv.ph = phi i64 [ 0, %vector.scevcheck ], [ 0, %for_loop_body.us ], [ %33, %middle.block ]
  %.0811.us.ph = phi float [ 0.000000e+00, %vector.scevcheck ], [ 0.000000e+00, %for_loop_body.us ], [ %119, %middle.block ]
  %120 = xor i64 %indvars.iv.ph, -1
  %121 = add nsw i64 %120, %wide.trip.count
  br i1 %lcmp.mod31.not, label %for_loop_body1.us.prol.loopexit, label %for_loop_body1.us.prol.preheader

for_loop_body1.us.prol.preheader:                 ; preds = %for_loop_body1.us.preheader
  %122 = trunc i64 %indvars.iv.ph to i32
  %123 = mul i32 %61, %122
  %124 = add i32 %.0913.us, %123
  %125 = sub i32 %124, %55
  %126 = zext i32 %59 to i64
  br label %for_loop_body1.us.prol

for_loop_body1.us.prol:                           ; preds = %for_loop_body1.us.prol, %for_loop_body1.us.prol.preheader
  %lsr.iv44 = phi i64 [ %xtraiter30, %for_loop_body1.us.prol.preheader ], [ %lsr.iv.next45, %for_loop_body1.us.prol ]
  %lsr.iv42 = phi i32 [ %125, %for_loop_body1.us.prol.preheader ], [ %lsr.iv.next43, %for_loop_body1.us.prol ]
  %indvars.iv.prol = phi i64 [ %indvars.iv.next.prol, %for_loop_body1.us.prol ], [ %indvars.iv.ph, %for_loop_body1.us.prol.preheader ]
  %.0811.us.prol = phi float [ %135, %for_loop_body1.us.prol ], [ %.0811.us.ph, %for_loop_body1.us.prol.preheader ]
  %127 = add i64 %126, %indvars.iv.prol
  %tmp = trunc i64 %127 to i32
  %128 = sext i32 %tmp to i64
  %129 = getelementptr float, float* %57, i64 %128
  %130 = load float, float* %129, align 4
  %131 = sext i32 %lsr.iv42 to i64
  %132 = getelementptr float, float* %60, i64 %131
  %133 = load float, float* %132, align 4
  %134 = fmul reassoc ninf nsz float %133, %130
  %135 = fadd reassoc ninf nsz float %134, %.0811.us.prol
  %indvars.iv.next.prol = add nuw nsw i64 %indvars.iv.prol, 1
  %lsr.iv.next43 = add i32 %lsr.iv42, %61
  %lsr.iv.next45 = add nsw i64 %lsr.iv44, -1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next45, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body1.us.prol.loopexit.loopexit, label %for_loop_body1.us.prol, !llvm.loop !11

for_loop_body1.us.prol.loopexit.loopexit:         ; preds = %for_loop_body1.us.prol
  %136 = add i64 %xtraiter30, %indvars.iv.ph
  br label %for_loop_body1.us.prol.loopexit

for_loop_body1.us.prol.loopexit:                  ; preds = %for_loop_body1.us.prol.loopexit.loopexit, %for_loop_body1.us.preheader
  %.lcssa27.unr = phi float [ undef, %for_loop_body1.us.preheader ], [ %135, %for_loop_body1.us.prol.loopexit.loopexit ]
  %indvars.iv.unr = phi i64 [ %indvars.iv.ph, %for_loop_body1.us.preheader ], [ %136, %for_loop_body1.us.prol.loopexit.loopexit ]
  %.0811.us.unr = phi float [ %.0811.us.ph, %for_loop_body1.us.preheader ], [ %135, %for_loop_body1.us.prol.loopexit.loopexit ]
  %137 = icmp ult i64 %121, 3
  br i1 %137, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us.preheader36

for_loop_body1.us.preheader36:                    ; preds = %for_loop_body1.us.prol.loopexit
  %138 = zext i32 %59 to i64
  %139 = trunc i64 %indvars.iv.unr to i32
  %140 = add nuw i32 %139, 3
  %141 = mul i32 %61, %140
  %142 = shl i32 %61, 2
  %143 = add nuw i32 %139, 2
  %144 = mul i32 %61, %143
  %145 = add nuw i32 %139, 1
  %146 = mul i32 %61, %145
  %147 = mul i32 %61, %139
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader36
  %lsr.iv47 = phi i32 [ %56, %for_loop_body1.us.preheader36 ], [ %lsr.iv.next48, %for_loop_body1.us ]
  %indvars.iv = phi i64 [ %indvars.iv.next.3, %for_loop_body1.us ], [ %indvars.iv.unr, %for_loop_body1.us.preheader36 ]
  %.0811.us = phi float [ %187, %for_loop_body1.us ], [ %.0811.us.unr, %for_loop_body1.us.preheader36 ]
  %148 = add i64 %138, %indvars.iv
  %tmp51 = trunc i64 %148 to i32
  %149 = sext i32 %tmp51 to i64
  %150 = getelementptr float, float* %57, i64 %149
  %151 = load float, float* %150, align 4
  %152 = add i32 %147, %lsr.iv47
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %60, i64 %153
  %155 = load float, float* %154, align 4
  %156 = fmul reassoc ninf nsz float %155, %151
  %157 = fadd reassoc ninf nsz float %156, %.0811.us
  %158 = add i64 %148, 1
  %tmp50 = trunc i64 %158 to i32
  %159 = sext i32 %tmp50 to i64
  %160 = getelementptr float, float* %57, i64 %159
  %161 = load float, float* %160, align 4
  %162 = add i32 %146, %lsr.iv47
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %60, i64 %163
  %165 = load float, float* %164, align 4
  %166 = fmul reassoc ninf nsz float %165, %161
  %167 = fadd reassoc ninf nsz float %166, %157
  %168 = add i64 %148, 2
  %tmp49 = trunc i64 %168 to i32
  %169 = sext i32 %tmp49 to i64
  %170 = getelementptr float, float* %57, i64 %169
  %171 = load float, float* %170, align 4
  %172 = add i32 %144, %lsr.iv47
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, float* %60, i64 %173
  %175 = load float, float* %174, align 4
  %176 = fmul reassoc ninf nsz float %175, %171
  %177 = fadd reassoc ninf nsz float %176, %167
  %178 = add i64 %148, 3
  %tmp46 = trunc i64 %178 to i32
  %179 = sext i32 %tmp46 to i64
  %180 = getelementptr float, float* %57, i64 %179
  %181 = load float, float* %180, align 4
  %182 = add i32 %141, %lsr.iv47
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, float* %60, i64 %183
  %185 = load float, float* %184, align 4
  %186 = fmul reassoc ninf nsz float %185, %181
  %187 = fadd reassoc ninf nsz float %186, %177
  %indvars.iv.next.3 = add nuw nsw i64 %indvars.iv, 4
  %lsr.iv.next48 = add i32 %lsr.iv47, %142
  %exitcond.not.3 = icmp eq i64 %wide.trip.count, %indvars.iv.next.3
  br i1 %exitcond.not.3, label %for_loop_test4.after_for3_crit_edge.us.loopexit, label %for_loop_body1.us, !llvm.loop !13

for_loop_test4.after_for3_crit_edge.us.loopexit:  ; preds = %for_loop_body1.us
  br label %for_loop_test4.after_for3_crit_edge.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_test4.after_for3_crit_edge.us.loopexit, %for_loop_body1.us.prol.loopexit, %middle.block
  %.lcssa = phi float [ %119, %middle.block ], [ %.lcssa27.unr, %for_loop_body1.us.prol.loopexit ], [ %187, %for_loop_test4.after_for3_crit_edge.us.loopexit ]
  %188 = load float*, float** %30, align 8
  %189 = load i32, i32* %31, align 4
  %190 = mul i32 %189, %54
  %191 = add i32 %190, %56
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, float* %188, i64 %192
  store float %.lcssa, float* %193, align 4
  %194 = add nsw i32 %.0913.us, 1
  %exitcond16.not = icmp eq i32 %194, %19
  br i1 %exitcond16.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.0913 = phi i32 [ %217, %for_loop_body ], [ %17, %for_loop_body.preheader ]
  %195 = load %struct.LLVMRuntime.209*, %struct.LLVMRuntime.209** %3, align 8
  %196 = getelementptr inbounds %struct.LLVMRuntime.209, %struct.LLVMRuntime.209* %195, i64 0, i32 14
  %197 = load i8*, i8** %196, align 8
  %198 = getelementptr inbounds i8, i8* %197, i64 4
  %199 = bitcast i8* %198 to i32*
  %200 = load i32, i32* %199, align 4
  %201 = sdiv i32 %.0913, %200
  %202 = mul i32 %201, %200
  %203 = xor i32 %200, %.0913
  %204 = icmp slt i32 %203, 0
  %205 = icmp ne i32 %.0913, 0
  %206 = icmp ne i32 %.0913, %202
  %207 = and i1 %205, %204
  %208 = and i1 %207, %206
  %.neg10 = sext i1 %208 to i32
  %209 = add i32 %201, %.neg10
  %210 = load float*, float** %30, align 8
  %211 = load i32, i32* %31, align 4
  %212 = sub i32 %211, %200
  %213 = mul i32 %212, %209
  %214 = add i32 %.0913, %213
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, float* %210, i64 %215
  store float 0.000000e+00, float* %216, align 4
  %217 = add nsw i32 %.0913, 1
  %exitcond17.not = icmp eq i32 %19, %217
  br i1 %exitcond17.not, label %after_for.loopexit37, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit37:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit37, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.210, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.210**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.210*, %struct.RuntimeContext.210** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.210*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.210*, i8*)*, void (%struct.RuntimeContext.210*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.210*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.210*, i8*, i32)*, void (%struct.RuntimeContext.210*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.210*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.210*, i8*)*, void (%struct.RuntimeContext.210*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.210*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.210* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.210* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.210* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.210, %struct.RuntimeContext.210* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.210* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !14

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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.210* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !16

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.210*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.210* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone willreturn }

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
!11 = distinct !{!11, !12}
!12 = !{!"llvm.loop.unroll.disable"}
!13 = distinct !{!13, !10}
!14 = distinct !{!14, !15}
!15 = !{!"llvm.loop.mustprogress"}
!16 = distinct !{!16, !15}
