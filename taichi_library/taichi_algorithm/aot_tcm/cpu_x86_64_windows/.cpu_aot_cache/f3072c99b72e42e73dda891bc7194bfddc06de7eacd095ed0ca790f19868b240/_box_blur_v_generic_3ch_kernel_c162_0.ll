; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext*, void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { i8*, %struct.LLVMRuntime*, i32, i64* }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager*], [1024 x %struct.NodeManager*], [1024 x i8*], i8*, %struct.RandState*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { i8*, i8*, i64 }
%struct.ListManager = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime* }
%struct.NodeManager = type { %struct.LLVMRuntime*, i32, i32, i32, i32, %struct.ListManager*, %struct.ListManager*, %struct.ListManager*, i32 }
%struct.RandState = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_box_blur_v_generic_3ch_kernel_c162_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 4
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = mul i32 %14, %10
  %21 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %21, i64 0, i32 14
  %23 = bitcast i8** %22 to i32**
  %24 = load i32*, i32** %23, align 8
  store i32 %20, i32* %24, align 4
  ret void
}

; Function Attrs: nounwind
define void @_box_blur_v_generic_3ch_kernel_c162_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext* %context, %struct.RuntimeContext** %4, align 8
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext*, i8*, i32)* @function_body, void (%struct.RuntimeContext*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32 }**
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
  br i1 %29, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %min.iters.check = icmp ult i32 %24, 16
  %n.vec = and i32 %24, -16
  %ind.end = sub i32 %n.vec, %23
  %.splatinsert = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  br label %for_loop_body.us

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  %36 = fdiv reassoc ninf nsz float 0.000000e+00, %26
  br label %for_loop_body

for_loop_body.us:                                 ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %.01317.us = phi i32 [ %108, %for_loop_test4.after_for3_crit_edge.us ], [ %17, %for_loop_body.us.preheader ]
  %37 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.01317.us, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.01317.us
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.01317.us, 0
  %48 = icmp ne i32 %44, %.01317.us
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg14.us = sext i1 %50 to i32
  %51 = add i32 %43, %.neg14.us
  %52 = mul i32 %51, %42
  %53 = sub i32 %.01317.us, %52
  %54 = getelementptr inbounds i8, i8* %39, i64 8
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = add i32 %56, -1
  %58 = load float*, float** %30, align 8
  %59 = load i32, i32* %31, align 4
  %60 = load i32, i32* %32, align 4
  br i1 %min.iters.check, label %for_loop_body1.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body.us
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %51, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert27 = insertelement <8 x i32> poison, i32 %57, i64 0
  %broadcast.splat28 = shufflevector <8 x i32> %broadcast.splatinsert27, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert31 = insertelement <8 x i32> poison, i32 %59, i64 0
  %broadcast.splat32 = shufflevector <8 x i32> %broadcast.splatinsert31, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert35 = insertelement <8 x i32> poison, i32 %53, i64 0
  %broadcast.splat36 = shufflevector <8 x i32> %broadcast.splatinsert35, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert39 = insertelement <8 x i32> poison, i32 %60, i64 0
  %broadcast.splat40 = shufflevector <8 x i32> %broadcast.splatinsert39, <8 x i32> poison, <8 x i32> zeroinitializer
  %.scalar = add i32 %51, 8
  %61 = insertelement <8 x i32> poison, i32 %.scalar, i64 0
  %62 = shufflevector <8 x i32> %61, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %81, %vector.body ]
  %vec.phi24 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %82, %vector.body ]
  %63 = add <8 x i32> %vec.ind, %broadcast.splat
  %64 = add <8 x i32> %62, %vec.ind
  %65 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %63, <8 x i32> zeroinitializer)
  %66 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %64, <8 x i32> zeroinitializer)
  %67 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat28, <8 x i32> %65)
  %68 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat28, <8 x i32> %66)
  %69 = mul <8 x i32> %broadcast.splat32, %67
  %70 = mul <8 x i32> %broadcast.splat32, %68
  %71 = add <8 x i32> %69, %broadcast.splat36
  %72 = add <8 x i32> %70, %broadcast.splat36
  %73 = mul <8 x i32> %71, %broadcast.splat40
  %74 = mul <8 x i32> %72, %broadcast.splat40
  %75 = add <8 x i32> %73, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %76 = add <8 x i32> %74, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %77 = sext <8 x i32> %75 to <8 x i64>
  %78 = sext <8 x i32> %76 to <8 x i64>
  %79 = getelementptr float, float* %58, <8 x i64> %77
  %80 = getelementptr float, float* %58, <8 x i64> %78
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %79, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather43 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %80, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %81 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather, %vec.phi
  %82 = fadd reassoc ninf nsz <8 x float> %wide.masked.gather43, %vec.phi24
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %lsr.iv.next = add i32 %lsr.iv, -16
  %83 = icmp eq i32 %lsr.iv.next, 0
  br i1 %83, label %middle.block, label %vector.body, !llvm.loop !9

middle.block:                                     ; preds = %vector.body
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %82, %81
  %84 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx)
  br label %for_loop_body1.us.preheader

for_loop_body1.us.preheader:                      ; preds = %middle.block, %for_loop_body.us
  %.016.us.ph = phi i32 [ %neg, %for_loop_body.us ], [ %ind.end, %middle.block ]
  %.01015.us.ph = phi float [ 0.000000e+00, %for_loop_body.us ], [ %84, %middle.block ]
  %85 = sub i32 %28, %.016.us.ph
  %86 = add i32 %.016.us.ph, %43
  %87 = add i32 %86, %.neg14.us
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader
  %lsr.iv52 = phi i32 [ %87, %for_loop_body1.us.preheader ], [ %lsr.iv.next53, %for_loop_body1.us ]
  %lsr.iv50 = phi i32 [ %85, %for_loop_body1.us.preheader ], [ %lsr.iv.next51, %for_loop_body1.us ]
  %.01015.us = phi float [ %97, %for_loop_body1.us ], [ %.01015.us.ph, %for_loop_body1.us.preheader ]
  %88 = tail call i32 @llvm.smax.i32(i32 %lsr.iv52, i32 0)
  %89 = tail call i32 @llvm.smin.i32(i32 %57, i32 %88)
  %90 = mul i32 %59, %89
  %91 = add i32 %90, %53
  %92 = mul i32 %91, %60
  %93 = add i32 %92, 2
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, float* %58, i64 %94
  %96 = load float, float* %95, align 4
  %97 = fadd reassoc ninf nsz float %96, %.01015.us
  %lsr.iv.next51 = add i32 %lsr.iv50, -1
  %lsr.iv.next53 = add i32 %lsr.iv52, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next51, 0
  br i1 %exitcond.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us, !llvm.loop !11

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us
  %98 = fdiv reassoc ninf nsz float %97, %26
  %99 = load float*, float** %33, align 8
  %100 = load i32, i32* %34, align 4
  %101 = load i32, i32* %35, align 4
  %102 = mul i32 %100, %51
  %103 = add i32 %102, %53
  %104 = mul i32 %103, %101
  %105 = add i32 %104, 2
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, float* %99, i64 %106
  store float %98, float* %107, align 4
  %108 = add nsw i32 %.01317.us, 1
  %exitcond19.not = icmp eq i32 %108, %19
  br i1 %exitcond19.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.01317 = phi i32 [ %134, %for_loop_body ], [ %17, %for_loop_body.preheader ]
  %109 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %110 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %109, i64 0, i32 14
  %111 = load i8*, i8** %110, align 8
  %112 = getelementptr inbounds i8, i8* %111, i64 4
  %113 = bitcast i8* %112 to i32*
  %114 = load i32, i32* %113, align 4
  %115 = sdiv i32 %.01317, %114
  %116 = mul i32 %115, %114
  %117 = xor i32 %114, %.01317
  %118 = icmp slt i32 %117, 0
  %119 = icmp ne i32 %.01317, 0
  %120 = icmp ne i32 %.01317, %116
  %121 = and i1 %119, %118
  %122 = and i1 %121, %120
  %.neg14 = sext i1 %122 to i32
  %123 = add i32 %115, %.neg14
  %124 = load float*, float** %33, align 8
  %125 = load i32, i32* %34, align 4
  %126 = load i32, i32* %35, align 4
  %127 = sub i32 %125, %114
  %128 = mul i32 %127, %123
  %129 = add i32 %.01317, %128
  %130 = mul i32 %129, %126
  %131 = add i32 %130, 2
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %124, i64 %132
  store float %36, float* %133, align 4
  %134 = add nsw i32 %.01317, 1
  %exitcond20.not = icmp eq i32 %19, %134
  br i1 %exitcond20.not, label %after_for.loopexit49, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit49:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit49, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext**
  %.sroa.0.0.copyload = load %struct.RuntimeContext*, %struct.RuntimeContext** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !15

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
