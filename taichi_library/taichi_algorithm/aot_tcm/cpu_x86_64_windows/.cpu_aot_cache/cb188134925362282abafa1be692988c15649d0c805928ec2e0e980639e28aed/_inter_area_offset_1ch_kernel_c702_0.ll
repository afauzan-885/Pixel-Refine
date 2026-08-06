; ModuleID = '<string>'
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
define void @_inter_area_offset_1ch_kernel_c682_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 20
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = sitofp i32 %3 to float
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 5
  %13 = load i32, i32* %12, align 4
  %14 = sitofp i32 %13 to float
  %15 = fdiv reassoc ninf nsz float %10, %14
  %16 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %17 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %16, i64 0, i32 14
  %18 = load i8*, i8** %17, align 8
  %19 = getelementptr inbounds i8, i8* %18, i64 8
  %20 = bitcast i8* %19 to float*
  store float %15, float* %20, align 4
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2
  %23 = load i32, i32* %22, align 4
  %24 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 16
  %28 = bitcast i8* %27 to i32*
  store i32 %23, i32* %28, align 4
  %29 = sitofp i32 %23 to float
  %30 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %30, i64 0, i32 4
  %32 = load i32, i32* %31, align 4
  %33 = sitofp i32 %32 to float
  %34 = fdiv reassoc ninf nsz float %29, %33
  %35 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %35, i64 0, i32 14
  %37 = load i8*, i8** %36, align 8
  %38 = getelementptr inbounds i8, i8* %37, i64 12
  %39 = bitcast i8* %38 to float*
  store float %34, float* %39, align 4
  %40 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %40, i64 0, i32 1, i32 0, i32 0
  %42 = load i32, i32* %41, align 4
  %43 = tail call i32 @llvm.smax.i32(i32 %42, i32 0)
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %40, i64 0, i32 1, i32 0, i32 1
  %45 = load i32, i32* %44, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %47 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  store i32 %46, i32* %51, align 4
  %52 = mul i32 %46, %43
  %53 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %53, i64 0, i32 14
  %55 = bitcast i8** %54 to i32**
  %56 = load i32*, i32** %55, align 8
  store i32 %52, i32* %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_inter_area_offset_1ch_kernel_c682_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %23 = bitcast i32* %22 to <2 x i32>*
  %24 = load <2 x i32>, <2 x i32>* %23, align 4
  %25 = icmp slt i32 %17, %19
  br i1 %25, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01728 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %173, %after_for3 ]
  %30 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %.01728, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.01728
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.01728, 0
  %41 = icmp ne i32 %37, %.01728
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg18 = sext i1 %43 to i32
  %44 = add i32 %36, %.neg18
  %45 = mul i32 %44, %35
  %46 = sub i32 %.01728, %45
  %47 = getelementptr inbounds i8, i8* %32, i64 8
  %48 = getelementptr inbounds i8, i8* %32, i64 16
  %49 = bitcast i8* %48 to i32*
  %50 = load i32, i32* %49, align 4
  %51 = add i32 %50, -1
  %52 = getelementptr inbounds i8, i8* %32, i64 20
  %53 = bitcast i8* %52 to i32*
  %54 = load i32, i32* %53, align 4
  %55 = add i32 %54, -1
  %56 = insertelement <2 x i32> poison, i32 %44, i64 0
  %57 = insertelement <2 x i32> %56, i32 %46, i64 1
  %58 = add <2 x i32> %57, %24
  %shuffle = shufflevector <2 x i32> %58, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %59 = sitofp <2 x i32> %shuffle to <2 x float>
  %60 = bitcast i8* %47 to <2 x float>*
  %61 = load <2 x float>, <2 x float>* %60, align 4
  %62 = fmul reassoc ninf nsz <2 x float> %61, %59
  %63 = add <2 x i32> %shuffle, <i32 1, i32 1>
  %64 = sitofp <2 x i32> %63 to <2 x float>
  %65 = fmul reassoc ninf nsz <2 x float> %61, %64
  %66 = call reassoc ninf nsz <2 x float> @llvm.floor.v2f32(<2 x float> %62)
  %67 = call reassoc ninf nsz <2 x float> @llvm.ceil.v2f32(<2 x float> %65)
  %68 = fptosi <2 x float> %66 to <2 x i32>
  %69 = fptosi <2 x float> %67 to <2 x i32>
  %70 = icmp sgt <2 x i32> %69, %68
  %71 = extractelement <2 x i1> %70, i64 0
  %72 = extractelement <2 x i1> %70, i64 1
  %or.cond = select i1 %72, i1 %71, i1 false
  br i1 %or.cond, label %for_loop_body1.us.preheader, label %after_for3

for_loop_body1.us.preheader:                      ; preds = %for_loop_body
  %.pre = load float*, float** %26, align 8
  %.pre34 = load i32, i32* %27, align 4
  %73 = extractelement <2 x i32> %69, i64 0
  %74 = extractelement <2 x i32> %68, i64 0
  %75 = sub i32 %73, %74
  %76 = extractelement <2 x i32> %68, i64 1
  %77 = add i32 %75, -8
  %78 = lshr i32 %77, 3
  %79 = add nuw nsw i32 %78, 1
  %80 = extractelement <2 x float> %62, i64 1
  %81 = extractelement <2 x float> %65, i64 1
  %min.iters.check = icmp ult i32 %75, 8
  %n.vec = and i32 %75, -8
  %ind.end = add i32 %n.vec, %74
  %.splat = shufflevector <2 x i32> %68, <2 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splat = shufflevector <2 x float> %65, <2 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splat39 = shufflevector <2 x float> %62, <2 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert42 = insertelement <8 x i32> poison, i32 %55, i64 0
  %broadcast.splat43 = shufflevector <8 x i32> %broadcast.splatinsert42, <8 x i32> poison, <8 x i32> zeroinitializer
  %xtraiter = and i32 %79, 1
  %82 = icmp ult i32 %77, 8
  %unroll_iter = and i32 %79, 1073741822
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  %cmp.n = icmp eq i32 %75, %n.vec
  %83 = extractelement <2 x float> %65, i64 0
  %84 = extractelement <2 x float> %62, i64 0
  %85 = extractelement <2 x i32> %69, i64 1
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, %for_loop_body1.us.preheader
  %.01325.us = phi i32 [ %86, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ %76, %for_loop_body1.us.preheader ]
  %.01424.us = phi float [ %.lcssa, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.01523.us = phi float [ %.lcssa36, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %86 = add nsw i32 %.01325.us, 1
  %87 = sitofp i32 %.01325.us to float
  %88 = tail call i32 @llvm.smax.i32(i32 %.01325.us, i32 0)
  %89 = sitofp i32 %86 to float
  %90 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %87, float %80)
  %91 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %89, float %81)
  %92 = tail call i32 @llvm.smin.i32(i32 %51, i32 %88)
  %93 = fsub reassoc ninf nsz float %91, %90
  %94 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %93, float 0.000000e+00)
  %95 = mul i32 %.pre34, %92
  br i1 %min.iters.check, label %for_loop_body5.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body1.us
  %96 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01424.us, i64 0
  %97 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01523.us, i64 0
  %broadcast.splatinsert40 = insertelement <8 x float> poison, float %94, i64 0
  %broadcast.splat41 = shufflevector <8 x float> %broadcast.splatinsert40, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert44 = insertelement <8 x i32> poison, i32 %95, i64 0
  %broadcast.splat45 = shufflevector <8 x i32> %broadcast.splatinsert44, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %82, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv = phi i32 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next, %vector.body ]
  %vec.ind = phi <8 x i32> [ %vec.ind.next.1, %vector.body ], [ %induction, %vector.body.preheader ]
  %vec.phi = phi <8 x float> [ %129, %vector.body ], [ %96, %vector.body.preheader ]
  %vec.phi37 = phi <8 x float> [ %128, %vector.body ], [ %97, %vector.body.preheader ]
  %98 = add nsw <8 x i32> %vec.ind, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %99 = sitofp <8 x i32> %98 to <8 x float>
  %100 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %99, <8 x float> %broadcast.splat)
  %101 = sitofp <8 x i32> %vec.ind to <8 x float>
  %102 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %101, <8 x float> %broadcast.splat39)
  %103 = fsub reassoc ninf nsz <8 x float> %100, %102
  %104 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %103, <8 x float> zeroinitializer)
  %105 = fmul reassoc ninf nsz <8 x float> %104, %broadcast.splat41
  %106 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind, <8 x i32> zeroinitializer)
  %107 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat43, <8 x i32> %106)
  %108 = add <8 x i32> %broadcast.splat45, %107
  %109 = sext <8 x i32> %108 to <8 x i64>
  %110 = getelementptr float, float* %.pre, <8 x i64> %109
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %110, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %111 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather, %105
  %112 = fadd reassoc ninf nsz <8 x float> %111, %vec.phi37
  %113 = fadd reassoc ninf nsz <8 x float> %105, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %114 = add <8 x i32> %vec.ind, <i32 9, i32 9, i32 9, i32 9, i32 9, i32 9, i32 9, i32 9>
  %115 = sitofp <8 x i32> %114 to <8 x float>
  %116 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %115, <8 x float> %broadcast.splat)
  %117 = sitofp <8 x i32> %vec.ind.next to <8 x float>
  %118 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %117, <8 x float> %broadcast.splat39)
  %119 = fsub reassoc ninf nsz <8 x float> %116, %118
  %120 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %119, <8 x float> zeroinitializer)
  %121 = fmul reassoc ninf nsz <8 x float> %120, %broadcast.splat41
  %122 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind.next, <8 x i32> zeroinitializer)
  %123 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat43, <8 x i32> %122)
  %124 = add <8 x i32> %broadcast.splat45, %123
  %125 = sext <8 x i32> %124 to <8 x i64>
  %126 = getelementptr float, float* %.pre, <8 x i64> %125
  %wide.masked.gather.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %126, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %127 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather.1, %121
  %128 = fadd reassoc ninf nsz <8 x float> %127, %112
  %129 = fadd reassoc ninf nsz <8 x float> %121, %113
  %vec.ind.next.1 = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %lsr.iv.next = add i32 %lsr.iv, -2
  %niter.ncmp.1 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa48.ph = phi <8 x float> [ undef, %vector.ph ], [ %128, %middle.block.unr-lcssa.loopexit ]
  %.lcssa47.ph = phi <8 x float> [ undef, %vector.ph ], [ %129, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ %96, %vector.ph ], [ %129, %middle.block.unr-lcssa.loopexit ]
  %vec.phi37.unr = phi <8 x float> [ %97, %vector.ph ], [ %128, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %130 = add nsw <8 x i32> %vec.ind.unr, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %131 = sitofp <8 x i32> %130 to <8 x float>
  %132 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %131, <8 x float> %broadcast.splat)
  %133 = sitofp <8 x i32> %vec.ind.unr to <8 x float>
  %134 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %133, <8 x float> %broadcast.splat39)
  %135 = fsub reassoc ninf nsz <8 x float> %132, %134
  %136 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %135, <8 x float> zeroinitializer)
  %137 = fmul reassoc ninf nsz <8 x float> %136, %broadcast.splat41
  %138 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind.unr, <8 x i32> zeroinitializer)
  %139 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat43, <8 x i32> %138)
  %140 = add <8 x i32> %broadcast.splat45, %139
  %141 = sext <8 x i32> %140 to <8 x i64>
  %142 = getelementptr float, float* %.pre, <8 x i64> %141
  %wide.masked.gather.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %142, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %143 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather.epil, %137
  %144 = fadd reassoc ninf nsz <8 x float> %143, %vec.phi37.unr
  %145 = fadd reassoc ninf nsz <8 x float> %137, %vec.phi.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa48 = phi <8 x float> [ %.lcssa48.ph, %middle.block.unr-lcssa ], [ %144, %vector.body.epil ]
  %.lcssa47 = phi <8 x float> [ %.lcssa47.ph, %middle.block.unr-lcssa ], [ %145, %vector.body.epil ]
  %146 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa48)
  %147 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa47)
  br i1 %cmp.n, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, label %for_loop_body5.us.preheader

for_loop_body5.us.preheader:                      ; preds = %middle.block, %for_loop_body1.us
  %.021.us.ph = phi i32 [ %74, %for_loop_body1.us ], [ %ind.end, %middle.block ]
  %.120.us.ph = phi float [ %.01424.us, %for_loop_body1.us ], [ %147, %middle.block ]
  %.11619.us.ph = phi float [ %.01523.us, %for_loop_body1.us ], [ %146, %middle.block ]
  br label %for_loop_body5.us

for_loop_body5.us:                                ; preds = %for_loop_body5.us, %for_loop_body5.us.preheader
  %.021.us = phi i32 [ %148, %for_loop_body5.us ], [ %.021.us.ph, %for_loop_body5.us.preheader ]
  %.120.us = phi float [ %164, %for_loop_body5.us ], [ %.120.us.ph, %for_loop_body5.us.preheader ]
  %.11619.us = phi float [ %163, %for_loop_body5.us ], [ %.11619.us.ph, %for_loop_body5.us.preheader ]
  %148 = add nsw i32 %.021.us, 1
  %149 = sitofp i32 %148 to float
  %150 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %149, float %83)
  %151 = sitofp i32 %.021.us to float
  %152 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %151, float %84)
  %153 = fsub reassoc ninf nsz float %150, %152
  %154 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %153, float 0.000000e+00)
  %155 = fmul reassoc ninf nsz float %154, %94
  %156 = tail call i32 @llvm.smax.i32(i32 %.021.us, i32 0)
  %157 = tail call i32 @llvm.smin.i32(i32 %55, i32 %156)
  %158 = add i32 %95, %157
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %.pre, i64 %159
  %161 = load float, float* %160, align 4
  %162 = fmul reassoc ninf nsz float %161, %155
  %163 = fadd reassoc ninf nsz float %162, %.11619.us
  %164 = fadd reassoc ninf nsz float %155, %.120.us
  %exitcond.not = icmp eq i32 %73, %148
  br i1 %exitcond.not, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, label %for_loop_body5.us, !llvm.loop !11

for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit: ; preds = %for_loop_body5.us
  br label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us

for_loop_test8.for_loop_test4.loopexit_crit_edge.us: ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, %middle.block
  %.lcssa36 = phi float [ %146, %middle.block ], [ %163, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %147, %middle.block ], [ %164, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %exitcond32.not = icmp eq i32 %86, %85
  br i1 %exitcond32.not, label %after_for3.loopexit, label %for_loop_body1.us

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3.loopexit:                              ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.015.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa36, %after_for3.loopexit ]
  %.014.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa, %after_for3.loopexit ]
  %165 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.014.lcssa, float 0x3E112E0BE0000000)
  %166 = fdiv reassoc ninf nsz float %.015.lcssa, %165
  %167 = load float*, float** %28, align 8
  %168 = load i32, i32* %29, align 4
  %169 = mul i32 %168, %44
  %170 = add i32 %169, %46
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %167, i64 %171
  store float %166, float* %172, align 4
  %173 = add nsw i32 %.01728, 1
  %exitcond33.not = icmp eq i32 %173, %19
  br i1 %exitcond33.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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

; Function Attrs: argmemonly nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.minnum.v8f32(<8 x float>, <8 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.maxnum.v8f32(<8 x float>, <8 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.ceil.v2f32(<2 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.floor.v2f32(<2 x float>) #3

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone willreturn }

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
