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
define void @_lk_grid_track_kernel_c484_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 8
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %18, i64 0, i32 3, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %18, i64 0, i32 3, i32 0, i32 1
  %22 = load i32, i32* %21, align 4
  %23 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %24 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %25 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  store i32 %24, i32* %29, align 4
  %30 = mul i32 %24, %23
  %31 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %31, i64 0, i32 14
  %33 = bitcast i8** %32 to i32**
  %34 = load i32*, i32** %33, align 8
  store i32 %30, i32* %34, align 4
  ret void
}

; Function Attrs: nounwind
define void @_lk_grid_track_kernel_c484_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 6
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 5
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 7
  %27 = load i32, i32* %26, align 4
  %28 = tail call i32 @llvm.smax.i32(i32 %25, i32 2)
  %29 = add i32 %27, %25
  %30 = shl i32 %29, 1
  %31 = sitofp i32 %28 to float
  %32 = sitofp i32 %30 to float
  %33 = icmp slt i32 %17, %19
  br i1 %33, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %neg = sub i32 0, %27
  %34 = shl i32 %27, 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 3, i32 1
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 3, i32 0, i32 1
  %37 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 3, i32 0, i32 2
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 4, i32 1
  %39 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 4, i32 0, i32 1
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %21, i64 0, i32 4, i32 0, i32 2
  %41 = add i32 %27, 1
  %42 = tail call i32 @llvm.smax.i32(i32 %neg, i32 %41)
  %43 = add i32 %42, %27
  %44 = mul i32 %43, %43
  %45 = insertelement <2 x i32> <i32 poison, i32 0>, i32 %43, i64 0
  %46 = insertelement <2 x i32> <i32 0, i32 poison>, i32 %44, i64 1
  %47 = icmp slt <2 x i32> %45, %46
  %48 = or i32 %34, 1
  %49 = mul i32 %48, %48
  %50 = sitofp i32 %49 to float
  %neg19 = fneg reassoc ninf nsz float %31
  %neg20 = fneg reassoc ninf nsz float %32
  %51 = mul i32 %25, %25
  %52 = sitofp i32 %51 to float
  %53 = fmul reassoc ninf nsz float %52, 0x3FC99999A0000000
  %54 = fmul reassoc ninf nsz float %52, 0x3FA47AE140000000
  %55 = insertelement <2 x i32> poison, i32 %25, i64 0
  %56 = shufflevector <2 x i32> %55, <2 x i32> poison, <2 x i32> zeroinitializer
  %57 = insertelement <2 x i32> poison, i32 %23, i64 0
  %58 = shufflevector <2 x i32> %57, <2 x i32> poison, <2 x i32> zeroinitializer
  %59 = insertelement <2 x float> poison, float %neg20, i64 0
  %60 = shufflevector <2 x float> %59, <2 x float> poison, <2 x i32> zeroinitializer
  %61 = insertelement <2 x float> poison, float %32, i64 0
  %62 = shufflevector <2 x float> %61, <2 x float> poison, <2 x i32> zeroinitializer
  %63 = insertelement <2 x float> poison, float %neg19, i64 0
  %64 = shufflevector <2 x float> %63, <2 x float> poison, <2 x i32> zeroinitializer
  %65 = insertelement <2 x float> poison, float %31, i64 0
  %66 = shufflevector <2 x float> %65, <2 x float> poison, <2 x i32> zeroinitializer
  %67 = extractelement <2 x i1> %47, i64 1
  %min.iters.check = icmp ult i32 %44, 32
  %n.vec = and i32 %44, -32
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %43, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splat166 = shufflevector <2 x i1> %47, <2 x i1> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert173 = insertelement <8 x i32> poison, i32 %27, i64 0
  %broadcast.splat174 = shufflevector <8 x i32> %broadcast.splatinsert173, <8 x i32> poison, <8 x i32> zeroinitializer
  %cmp.n = icmp eq i32 %44, %n.vec
  %68 = extractelement <2 x i1> %47, i64 0
  %69 = sub i32 0, %43
  %70 = sub i32 -1, %27
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.065104 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %271, %after_if3 ]
  %71 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %72 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %71, i64 0, i32 14
  %73 = load i8*, i8** %72, align 8
  %74 = getelementptr inbounds i8, i8* %73, i64 4
  %75 = bitcast i8* %74 to i32*
  %76 = load i32, i32* %75, align 4
  %77 = sdiv i32 %.065104, %76
  %78 = mul i32 %77, %76
  %79 = xor i32 %76, %.065104
  %80 = icmp slt i32 %79, 0
  %81 = icmp ne i32 %.065104, 0
  %82 = icmp ne i32 %78, %.065104
  %83 = and i1 %81, %80
  %84 = and i1 %83, %82
  %.neg72 = sext i1 %84 to i32
  %85 = add i32 %77, %.neg72
  %86 = mul i32 %85, %76
  %87 = sub i32 %.065104, %86
  %88 = insertelement <2 x i32> poison, i32 %87, i64 0
  %89 = insertelement <2 x i32> %88, i32 %85, i64 1
  %90 = mul <2 x i32> %89, %56
  %91 = add <2 x i32> %90, %58
  %92 = sitofp <2 x i32> %91 to <2 x float>
  %93 = load float*, float** %35, align 8
  %94 = load i32, i32* %36, align 4
  %95 = load i32, i32* %37, align 4
  %96 = mul i32 %85, %94
  %97 = add i32 %87, %96
  %98 = mul i32 %97, %95
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %93, i64 %99
  store float 0.000000e+00, float* %100, align 4
  %101 = load float*, float** %35, align 8
  %102 = load i32, i32* %36, align 4
  %103 = load i32, i32* %37, align 4
  %104 = mul i32 %102, %85
  %105 = add i32 %104, %87
  %106 = mul i32 %105, %103
  %107 = add i32 %106, 1
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, float* %101, i64 %108
  store float 0.000000e+00, float* %109, align 4
  %110 = load float*, float** %35, align 8
  %111 = load i32, i32* %36, align 4
  %112 = load i32, i32* %37, align 4
  %113 = mul i32 %111, %85
  %114 = add i32 %113, %87
  %115 = mul i32 %114, %112
  %116 = add i32 %115, 2
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, float* %110, i64 %117
  store float 0.000000e+00, float* %118, align 4
  %119 = load float*, float** %38, align 8
  %120 = load i32, i32* %39, align 4
  %121 = load i32, i32* %40, align 4
  %122 = mul i32 %120, %85
  %123 = add i32 %122, %87
  %124 = mul i32 %123, %121
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %119, i64 %125
  store float 0.000000e+00, float* %126, align 4
  %127 = load float*, float** %38, align 8
  %128 = load i32, i32* %39, align 4
  %129 = load i32, i32* %40, align 4
  %130 = mul i32 %128, %85
  %131 = add i32 %130, %87
  %132 = mul i32 %131, %129
  %133 = add i32 %132, 1
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %127, i64 %134
  store float 0.000000e+00, float* %135, align 4
  %136 = load float*, float** %38, align 8
  %137 = load i32, i32* %39, align 4
  %138 = load i32, i32* %40, align 4
  %139 = mul i32 %137, %85
  %140 = add i32 %139, %87
  %141 = mul i32 %140, %138
  %142 = add i32 %141, 2
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %136, i64 %143
  store float 2.000000e+00, float* %144, align 4
  %145 = load float*, float** %38, align 8
  %146 = load i32, i32* %39, align 4
  %147 = load i32, i32* %40, align 4
  %148 = mul i32 %146, %85
  %149 = add i32 %148, %87
  %150 = mul i32 %149, %147
  %151 = add i32 %150, 3
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, float* %145, i64 %152
  store float 0.000000e+00, float* %153, align 4
  %154 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %155 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %154, i64 0, i32 14
  %156 = load i8*, i8** %155, align 8
  %157 = getelementptr inbounds i8, i8* %156, i64 8
  %158 = bitcast i8* %157 to i32*
  %159 = load i32, i32* %158, align 4
  %160 = sub i32 %159, %23
  %161 = sitofp i32 %160 to float
  %162 = extractelement <2 x float> %92, i64 0
  %163 = fcmp reassoc ninf nsz olt float %162, %161
  br i1 %163, label %true_block, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %164 = getelementptr inbounds i8, i8* %156, i64 12
  %165 = bitcast i8* %164 to i32*
  %166 = load i32, i32* %165, align 4
  %167 = sub i32 %166, %23
  %168 = sitofp i32 %167 to float
  %169 = extractelement <2 x float> %92, i64 1
  %170 = fcmp reassoc ninf nsz olt float %169, %168
  br i1 %170, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %171 = fptosi <2 x float> %92 to <2 x i32>
  %172 = insertelement <2 x i32> poison, i32 %159, i64 0
  %173 = insertelement <2 x i32> %172, i32 %166, i64 1
  %174 = add <2 x i32> %173, <i32 -1, i32 -1>
  %175 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %20, align 8
  %176 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 2, i32 1
  %177 = load float*, float** %176, align 8
  %178 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 2, i32 0, i32 1
  %179 = load i32, i32* %178, align 4
  %180 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 2, i32 0, i32 2
  %181 = load i32, i32* %180, align 4
  %182 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %171, <2 x i32> %174)
  %183 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %182, <2 x i32> zeroinitializer)
  %184 = extractelement <2 x i32> %183, i64 0
  %185 = add nuw i32 %184, 1
  %186 = extractelement <2 x i32> %174, i64 0
  %187 = tail call i32 @llvm.smin.i32(i32 %185, i32 %186)
  %188 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %189 = extractelement <2 x i32> %183, i64 1
  %190 = add nuw i32 %189, 1
  %191 = extractelement <2 x i32> %174, i64 1
  %192 = tail call i32 @llvm.smin.i32(i32 %190, i32 %191)
  %193 = tail call i32 @llvm.smax.i32(i32 %192, i32 0)
  %194 = sitofp <2 x i32> %183 to <2 x float>
  %195 = fsub reassoc ninf nsz <2 x float> %92, %194
  %196 = mul i32 %179, %189
  %197 = add i32 %196, %184
  %198 = mul i32 %197, %181
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, float* %177, i64 %199
  %201 = add i32 %196, %188
  %202 = mul i32 %201, %181
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, float* %177, i64 %203
  %205 = load float, float* %204, align 4
  %206 = mul i32 %179, %193
  %207 = add i32 %206, %184
  %208 = mul i32 %207, %181
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %177, i64 %209
  %211 = add i32 %206, %188
  %212 = mul i32 %211, %181
  %213 = sext i32 %212 to i64
  %214 = getelementptr float, float* %177, i64 %213
  %215 = extractelement <2 x float> %195, i64 0
  %216 = fsub reassoc ninf nsz float 1.000000e+00, %215
  %217 = fmul reassoc ninf nsz float %205, %215
  %218 = add i32 %202, 1
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, float* %177, i64 %219
  %221 = load float, float* %220, align 4
  %222 = fsub reassoc ninf nsz <2 x float> <float poison, float 1.000000e+00>, %195
  %223 = add i32 %198, 1
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %177, i64 %224
  %226 = add i32 %208, 1
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, float* %177, i64 %227
  %229 = add i32 %212, 1
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, float* %177, i64 %230
  %232 = fmul reassoc ninf nsz float %221, %215
  %233 = insertelement <2 x float*> poison, float* %225, i64 0
  %234 = insertelement <2 x float*> %233, float* %200, i64 1
  %235 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %234, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %236 = insertelement <2 x float*> poison, float* %228, i64 0
  %237 = insertelement <2 x float*> %236, float* %210, i64 1
  %238 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %237, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %239 = insertelement <2 x float*> poison, float* %231, i64 0
  %240 = insertelement <2 x float*> %239, float* %214, i64 1
  %241 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %240, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %242 = insertelement <2 x float> poison, float %216, i64 0
  %243 = shufflevector <2 x float> %242, <2 x float> poison, <2 x i32> zeroinitializer
  %244 = fmul reassoc ninf nsz <2 x float> %235, %243
  %245 = insertelement <2 x float> poison, float %232, i64 0
  %246 = insertelement <2 x float> %245, float %217, i64 1
  %247 = fadd reassoc ninf nsz <2 x float> %246, %244
  %248 = shufflevector <2 x float> %222, <2 x float> undef, <2 x i32> <i32 1, i32 1>
  %249 = fmul reassoc ninf nsz <2 x float> %247, %248
  %250 = fmul reassoc ninf nsz <2 x float> %238, %243
  %251 = shufflevector <2 x float> %195, <2 x float> undef, <2 x i32> zeroinitializer
  %252 = fmul reassoc ninf nsz <2 x float> %241, %251
  %253 = fadd reassoc ninf nsz <2 x float> %252, %250
  %254 = shufflevector <2 x float> %195, <2 x float> undef, <2 x i32> <i32 1, i32 1>
  %255 = fmul reassoc ninf nsz <2 x float> %253, %254
  %256 = fadd reassoc ninf nsz <2 x float> %255, %249
  %257 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 8
  %258 = load i32, i32* %257, align 4
  %259 = icmp sgt i32 %258, 0
  br i1 %259, label %for_loop_body4.lr.ph, label %true_block24

for_loop_body4.lr.ph:                             ; preds = %true_block1
  %260 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 0, i32 1
  %261 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 0, i32 0, i32 1
  %262 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 1, i32 1
  %263 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 1, i32 0, i32 1
  %264 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %175, i64 0, i32 9
  %broadcast.splat182 = shufflevector <2 x i32> %91, <2 x i32> poison, <8 x i32> <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %broadcast.splat190 = shufflevector <2 x i32> %91, <2 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splat214 = shufflevector <2 x i32> %174, <2 x i32> poison, <8 x i32> <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %broadcast.splat222 = shufflevector <2 x i32> %174, <2 x i32> poison, <8 x i32> zeroinitializer
  %265 = extractelement <2 x i32> %91, i64 1
  %266 = extractelement <2 x i32> %91, i64 0
  %267 = shufflevector <2 x i32> %174, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %268 = shufflevector <2 x i32> %174, <2 x i32> undef, <2 x i32> zeroinitializer
  %269 = add i32 %neg, %266
  %270 = add i32 %70, %266
  br label %for_loop_body4

after_if3:                                        ; preds = %903, %after_for6, %true_block, %for_loop_body
  %271 = add nsw i32 %.065104, 1
  %exitcond111.not = icmp eq i32 %271, %19
  br i1 %exitcond111.not, label %after_for.loopexit, label %for_loop_body

for_loop_body4:                                   ; preds = %after_if10, %for_loop_body4.lr.ph
  %.05198 = phi i32 [ 0, %for_loop_body4.lr.ph ], [ %745, %after_if10 ]
  %.05297 = phi float [ 0.000000e+00, %for_loop_body4.lr.ph ], [ %.153, %after_if10 ]
  %.05496 = phi float [ 0.000000e+00, %for_loop_body4.lr.ph ], [ %.155, %after_if10 ]
  %.05695 = phi i32 [ 1, %for_loop_body4.lr.ph ], [ %.157, %after_if10 ]
  %.05894 = phi i32 [ 1, %for_loop_body4.lr.ph ], [ %.159, %after_if10 ]
  %272 = phi <2 x float> [ %256, %for_loop_body4.lr.ph ], [ %744, %after_if10 ]
  %273 = icmp eq i32 %.05695, 1
  br i1 %273, label %true_block8, label %after_if10

after_for6:                                       ; preds = %after_if10
  %274 = icmp eq i32 %.159, 1
  br i1 %274, label %true_block24, label %after_if3

true_block8:                                      ; preds = %for_loop_body4
  br i1 %67, label %for_loop_body11.lr.ph, label %after_for13

for_loop_body11.lr.ph:                            ; preds = %true_block8
  %275 = load float*, float** %260, align 8
  %276 = load i32, i32* %261, align 4
  %277 = load float*, float** %262, align 8
  %278 = load i32, i32* %263, align 4
  br i1 %min.iters.check, label %for_loop_body11.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body11.lr.ph
  %broadcast.splat198 = shufflevector <2 x float> %272, <2 x float> poison, <8 x i32> <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %broadcast.splat206 = shufflevector <2 x float> %272, <2 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert229 = insertelement <8 x i32> poison, i32 %276, i64 0
  %broadcast.splat230 = shufflevector <8 x i32> %broadcast.splatinsert229, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert252 = insertelement <8 x i32> poison, i32 %278, i64 0
  %broadcast.splat253 = shufflevector <8 x i32> %broadcast.splatinsert252, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %719, %vector.body ]
  %vec.phi136 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %720, %vector.body ]
  %vec.phi137 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %721, %vector.body ]
  %vec.phi138 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %722, %vector.body ]
  %vec.phi139 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %711, %vector.body ]
  %vec.phi140 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %712, %vector.body ]
  %vec.phi141 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %713, %vector.body ]
  %vec.phi142 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %714, %vector.body ]
  %vec.phi143 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %703, %vector.body ]
  %vec.phi144 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %704, %vector.body ]
  %vec.phi145 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %705, %vector.body ]
  %vec.phi146 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %706, %vector.body ]
  %vec.phi147 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %695, %vector.body ]
  %vec.phi148 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %696, %vector.body ]
  %vec.phi149 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %697, %vector.body ]
  %vec.phi150 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %698, %vector.body ]
  %vec.phi151 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %687, %vector.body ]
  %vec.phi152 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %688, %vector.body ]
  %vec.phi153 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %689, %vector.body ]
  %vec.phi154 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %690, %vector.body ]
  %vec.phi155 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %679, %vector.body ]
  %vec.phi156 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %680, %vector.body ]
  %vec.phi157 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %681, %vector.body ]
  %vec.phi158 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %682, %vector.body ]
  %step.add = add <8 x i32> %vec.ind, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %step.add133 = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %step.add134 = add <8 x i32> %vec.ind, <i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24>
  %279 = sdiv <8 x i32> %vec.ind, %broadcast.splat
  %280 = sdiv <8 x i32> %step.add, %broadcast.splat
  %281 = sdiv <8 x i32> %step.add133, %broadcast.splat
  %282 = sdiv <8 x i32> %step.add134, %broadcast.splat
  %283 = mul <8 x i32> %279, %broadcast.splat
  %284 = mul <8 x i32> %280, %broadcast.splat
  %285 = mul <8 x i32> %281, %broadcast.splat
  %286 = mul <8 x i32> %282, %broadcast.splat
  %287 = icmp ne <8 x i32> %vec.ind, zeroinitializer
  %288 = icmp ne <8 x i32> %step.add, zeroinitializer
  %289 = icmp ne <8 x i32> %step.add133, zeroinitializer
  %290 = icmp ne <8 x i32> %step.add134, zeroinitializer
  %291 = icmp ne <8 x i32> %283, %vec.ind
  %292 = icmp ne <8 x i32> %284, %step.add
  %293 = icmp ne <8 x i32> %285, %step.add133
  %294 = icmp ne <8 x i32> %286, %step.add134
  %295 = and <8 x i1> %broadcast.splat166, %287
  %296 = and <8 x i1> %broadcast.splat166, %288
  %297 = and <8 x i1> %broadcast.splat166, %289
  %298 = and <8 x i1> %broadcast.splat166, %290
  %299 = and <8 x i1> %295, %291
  %300 = and <8 x i1> %296, %292
  %301 = and <8 x i1> %297, %293
  %302 = and <8 x i1> %298, %294
  %303 = sext <8 x i1> %299 to <8 x i32>
  %304 = sext <8 x i1> %300 to <8 x i32>
  %305 = sext <8 x i1> %301 to <8 x i32>
  %306 = sext <8 x i1> %302 to <8 x i32>
  %307 = add <8 x i32> %279, %303
  %308 = add <8 x i32> %280, %304
  %309 = add <8 x i32> %281, %305
  %310 = add <8 x i32> %282, %306
  %311 = sub <8 x i32> %307, %broadcast.splat174
  %312 = sub <8 x i32> %308, %broadcast.splat174
  %313 = sub <8 x i32> %309, %broadcast.splat174
  %314 = sub <8 x i32> %310, %broadcast.splat174
  %315 = mul <8 x i32> %307, %broadcast.splat
  %316 = mul <8 x i32> %308, %broadcast.splat
  %317 = mul <8 x i32> %309, %broadcast.splat
  %318 = mul <8 x i32> %310, %broadcast.splat
  %319 = add <8 x i32> %311, %broadcast.splat182
  %320 = add <8 x i32> %312, %broadcast.splat182
  %321 = add <8 x i32> %313, %broadcast.splat182
  %322 = add <8 x i32> %314, %broadcast.splat182
  %323 = add <8 x i32> %broadcast.splat190, %vec.ind
  %324 = add <8 x i32> %broadcast.splat190, %step.add
  %325 = add <8 x i32> %broadcast.splat190, %step.add133
  %326 = add <8 x i32> %broadcast.splat190, %step.add134
  %327 = add <8 x i32> %broadcast.splat174, %315
  %328 = add <8 x i32> %broadcast.splat174, %316
  %329 = add <8 x i32> %broadcast.splat174, %317
  %330 = add <8 x i32> %broadcast.splat174, %318
  %331 = sub <8 x i32> %323, %327
  %332 = sub <8 x i32> %324, %328
  %333 = sub <8 x i32> %325, %329
  %334 = sub <8 x i32> %326, %330
  %335 = sitofp <8 x i32> %319 to <8 x float>
  %336 = sitofp <8 x i32> %320 to <8 x float>
  %337 = sitofp <8 x i32> %321 to <8 x float>
  %338 = sitofp <8 x i32> %322 to <8 x float>
  %339 = sitofp <8 x i32> %331 to <8 x float>
  %340 = sitofp <8 x i32> %332 to <8 x float>
  %341 = sitofp <8 x i32> %333 to <8 x float>
  %342 = sitofp <8 x i32> %334 to <8 x float>
  %343 = fadd reassoc ninf nsz <8 x float> %broadcast.splat198, %339
  %344 = fadd reassoc ninf nsz <8 x float> %broadcast.splat198, %340
  %345 = fadd reassoc ninf nsz <8 x float> %broadcast.splat198, %341
  %346 = fadd reassoc ninf nsz <8 x float> %broadcast.splat198, %342
  %347 = fadd reassoc ninf nsz <8 x float> %broadcast.splat206, %335
  %348 = fadd reassoc ninf nsz <8 x float> %broadcast.splat206, %336
  %349 = fadd reassoc ninf nsz <8 x float> %broadcast.splat206, %337
  %350 = fadd reassoc ninf nsz <8 x float> %broadcast.splat206, %338
  %351 = add <8 x i32> %331, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %352 = add <8 x i32> %332, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %353 = add <8 x i32> %333, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %354 = add <8 x i32> %334, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %355 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %319, <8 x i32> %broadcast.splat214)
  %356 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %320, <8 x i32> %broadcast.splat214)
  %357 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %321, <8 x i32> %broadcast.splat214)
  %358 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %322, <8 x i32> %broadcast.splat214)
  %359 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %355, <8 x i32> zeroinitializer)
  %360 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %356, <8 x i32> zeroinitializer)
  %361 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %357, <8 x i32> zeroinitializer)
  %362 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %358, <8 x i32> zeroinitializer)
  %363 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %351, <8 x i32> %broadcast.splat222)
  %364 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %352, <8 x i32> %broadcast.splat222)
  %365 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %353, <8 x i32> %broadcast.splat222)
  %366 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %354, <8 x i32> %broadcast.splat222)
  %367 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %363, <8 x i32> zeroinitializer)
  %368 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %364, <8 x i32> zeroinitializer)
  %369 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %365, <8 x i32> zeroinitializer)
  %370 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %366, <8 x i32> zeroinitializer)
  %371 = add <8 x i32> %331, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %372 = add <8 x i32> %332, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %373 = add <8 x i32> %333, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %374 = add <8 x i32> %334, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %375 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %371, <8 x i32> %broadcast.splat222)
  %376 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %372, <8 x i32> %broadcast.splat222)
  %377 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %373, <8 x i32> %broadcast.splat222)
  %378 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %374, <8 x i32> %broadcast.splat222)
  %379 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %375, <8 x i32> zeroinitializer)
  %380 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %376, <8 x i32> zeroinitializer)
  %381 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %377, <8 x i32> zeroinitializer)
  %382 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %378, <8 x i32> zeroinitializer)
  %383 = mul <8 x i32> %359, %broadcast.splat230
  %384 = mul <8 x i32> %360, %broadcast.splat230
  %385 = mul <8 x i32> %361, %broadcast.splat230
  %386 = mul <8 x i32> %362, %broadcast.splat230
  %387 = add <8 x i32> %367, %383
  %388 = add <8 x i32> %368, %384
  %389 = add <8 x i32> %369, %385
  %390 = add <8 x i32> %370, %386
  %391 = sext <8 x i32> %387 to <8 x i64>
  %392 = sext <8 x i32> %388 to <8 x i64>
  %393 = sext <8 x i32> %389 to <8 x i64>
  %394 = sext <8 x i32> %390 to <8 x i64>
  %395 = getelementptr float, float* %275, <8 x i64> %391
  %396 = getelementptr float, float* %275, <8 x i64> %392
  %397 = getelementptr float, float* %275, <8 x i64> %393
  %398 = getelementptr float, float* %275, <8 x i64> %394
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %395, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather237 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %396, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather238 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %397, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather239 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %398, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %399 = add <8 x i32> %379, %383
  %400 = add <8 x i32> %380, %384
  %401 = add <8 x i32> %381, %385
  %402 = add <8 x i32> %382, %386
  %403 = sext <8 x i32> %399 to <8 x i64>
  %404 = sext <8 x i32> %400 to <8 x i64>
  %405 = sext <8 x i32> %401 to <8 x i64>
  %406 = sext <8 x i32> %402 to <8 x i64>
  %407 = getelementptr float, float* %275, <8 x i64> %403
  %408 = getelementptr float, float* %275, <8 x i64> %404
  %409 = getelementptr float, float* %275, <8 x i64> %405
  %410 = getelementptr float, float* %275, <8 x i64> %406
  %wide.masked.gather240 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %407, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather241 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %408, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather242 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %409, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather243 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %410, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %411 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather240
  %412 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather237, %wide.masked.gather241
  %413 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather238, %wide.masked.gather242
  %414 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather239, %wide.masked.gather243
  %415 = fmul reassoc ninf nsz <8 x float> %411, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %416 = fmul reassoc ninf nsz <8 x float> %412, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %417 = fmul reassoc ninf nsz <8 x float> %413, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %418 = fmul reassoc ninf nsz <8 x float> %414, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %419 = add <8 x i32> %319, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %420 = add <8 x i32> %320, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %421 = add <8 x i32> %321, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %422 = add <8 x i32> %322, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %423 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %419, <8 x i32> %broadcast.splat214)
  %424 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %420, <8 x i32> %broadcast.splat214)
  %425 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %421, <8 x i32> %broadcast.splat214)
  %426 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %422, <8 x i32> %broadcast.splat214)
  %427 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %423, <8 x i32> zeroinitializer)
  %428 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %424, <8 x i32> zeroinitializer)
  %429 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %425, <8 x i32> zeroinitializer)
  %430 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %426, <8 x i32> zeroinitializer)
  %431 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %331, <8 x i32> %broadcast.splat222)
  %432 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %332, <8 x i32> %broadcast.splat222)
  %433 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %333, <8 x i32> %broadcast.splat222)
  %434 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %334, <8 x i32> %broadcast.splat222)
  %435 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %431, <8 x i32> zeroinitializer)
  %436 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %432, <8 x i32> zeroinitializer)
  %437 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %433, <8 x i32> zeroinitializer)
  %438 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %434, <8 x i32> zeroinitializer)
  %439 = add <8 x i32> %319, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %440 = add <8 x i32> %320, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %441 = add <8 x i32> %321, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %442 = add <8 x i32> %322, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %443 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %439, <8 x i32> %broadcast.splat214)
  %444 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %440, <8 x i32> %broadcast.splat214)
  %445 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %441, <8 x i32> %broadcast.splat214)
  %446 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %442, <8 x i32> %broadcast.splat214)
  %447 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %443, <8 x i32> zeroinitializer)
  %448 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %444, <8 x i32> zeroinitializer)
  %449 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %445, <8 x i32> zeroinitializer)
  %450 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %446, <8 x i32> zeroinitializer)
  %451 = mul <8 x i32> %427, %broadcast.splat230
  %452 = mul <8 x i32> %428, %broadcast.splat230
  %453 = mul <8 x i32> %429, %broadcast.splat230
  %454 = mul <8 x i32> %430, %broadcast.splat230
  %455 = add <8 x i32> %451, %435
  %456 = add <8 x i32> %452, %436
  %457 = add <8 x i32> %453, %437
  %458 = add <8 x i32> %454, %438
  %459 = sext <8 x i32> %455 to <8 x i64>
  %460 = sext <8 x i32> %456 to <8 x i64>
  %461 = sext <8 x i32> %457 to <8 x i64>
  %462 = sext <8 x i32> %458 to <8 x i64>
  %463 = getelementptr float, float* %275, <8 x i64> %459
  %464 = getelementptr float, float* %275, <8 x i64> %460
  %465 = getelementptr float, float* %275, <8 x i64> %461
  %466 = getelementptr float, float* %275, <8 x i64> %462
  %wide.masked.gather244 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %463, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather245 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %464, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather246 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %465, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather247 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %466, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %467 = mul <8 x i32> %447, %broadcast.splat230
  %468 = mul <8 x i32> %448, %broadcast.splat230
  %469 = mul <8 x i32> %449, %broadcast.splat230
  %470 = mul <8 x i32> %450, %broadcast.splat230
  %471 = add <8 x i32> %467, %435
  %472 = add <8 x i32> %468, %436
  %473 = add <8 x i32> %469, %437
  %474 = add <8 x i32> %470, %438
  %475 = sext <8 x i32> %471 to <8 x i64>
  %476 = sext <8 x i32> %472 to <8 x i64>
  %477 = sext <8 x i32> %473 to <8 x i64>
  %478 = sext <8 x i32> %474 to <8 x i64>
  %479 = getelementptr float, float* %275, <8 x i64> %475
  %480 = getelementptr float, float* %275, <8 x i64> %476
  %481 = getelementptr float, float* %275, <8 x i64> %477
  %482 = getelementptr float, float* %275, <8 x i64> %478
  %wide.masked.gather248 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %479, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather249 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %480, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather250 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %481, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather251 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %482, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %483 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather244, %wide.masked.gather248
  %484 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather245, %wide.masked.gather249
  %485 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather246, %wide.masked.gather250
  %486 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather247, %wide.masked.gather251
  %487 = fmul reassoc ninf nsz <8 x float> %483, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %488 = fmul reassoc ninf nsz <8 x float> %484, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %489 = fmul reassoc ninf nsz <8 x float> %485, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %490 = fmul reassoc ninf nsz <8 x float> %486, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %491 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %343)
  %492 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %344)
  %493 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %345)
  %494 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %346)
  %495 = fptosi <8 x float> %491 to <8 x i32>
  %496 = fptosi <8 x float> %492 to <8 x i32>
  %497 = fptosi <8 x float> %493 to <8 x i32>
  %498 = fptosi <8 x float> %494 to <8 x i32>
  %499 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %495, <8 x i32> %broadcast.splat222)
  %500 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %496, <8 x i32> %broadcast.splat222)
  %501 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %497, <8 x i32> %broadcast.splat222)
  %502 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %498, <8 x i32> %broadcast.splat222)
  %503 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %499, <8 x i32> zeroinitializer)
  %504 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %500, <8 x i32> zeroinitializer)
  %505 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %501, <8 x i32> zeroinitializer)
  %506 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %502, <8 x i32> zeroinitializer)
  %507 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %347)
  %508 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %348)
  %509 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %349)
  %510 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %350)
  %511 = fptosi <8 x float> %507 to <8 x i32>
  %512 = fptosi <8 x float> %508 to <8 x i32>
  %513 = fptosi <8 x float> %509 to <8 x i32>
  %514 = fptosi <8 x float> %510 to <8 x i32>
  %515 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %511, <8 x i32> %broadcast.splat214)
  %516 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %512, <8 x i32> %broadcast.splat214)
  %517 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %513, <8 x i32> %broadcast.splat214)
  %518 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %514, <8 x i32> %broadcast.splat214)
  %519 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %515, <8 x i32> zeroinitializer)
  %520 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %516, <8 x i32> zeroinitializer)
  %521 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %517, <8 x i32> zeroinitializer)
  %522 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %518, <8 x i32> zeroinitializer)
  %523 = add nuw <8 x i32> %503, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %524 = add nuw <8 x i32> %504, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %525 = add nuw <8 x i32> %505, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %526 = add nuw <8 x i32> %506, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %527 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %523, <8 x i32> %broadcast.splat222)
  %528 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %524, <8 x i32> %broadcast.splat222)
  %529 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %525, <8 x i32> %broadcast.splat222)
  %530 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %526, <8 x i32> %broadcast.splat222)
  %531 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %527, <8 x i32> zeroinitializer)
  %532 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %528, <8 x i32> zeroinitializer)
  %533 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %529, <8 x i32> zeroinitializer)
  %534 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %530, <8 x i32> zeroinitializer)
  %535 = add nuw <8 x i32> %519, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %536 = add nuw <8 x i32> %520, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %537 = add nuw <8 x i32> %521, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %538 = add nuw <8 x i32> %522, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %539 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %535, <8 x i32> %broadcast.splat214)
  %540 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %536, <8 x i32> %broadcast.splat214)
  %541 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %537, <8 x i32> %broadcast.splat214)
  %542 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %538, <8 x i32> %broadcast.splat214)
  %543 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %539, <8 x i32> zeroinitializer)
  %544 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %540, <8 x i32> zeroinitializer)
  %545 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %541, <8 x i32> zeroinitializer)
  %546 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %542, <8 x i32> zeroinitializer)
  %547 = sitofp <8 x i32> %503 to <8 x float>
  %548 = sitofp <8 x i32> %504 to <8 x float>
  %549 = sitofp <8 x i32> %505 to <8 x float>
  %550 = sitofp <8 x i32> %506 to <8 x float>
  %551 = fsub reassoc ninf nsz <8 x float> %343, %547
  %552 = fsub reassoc ninf nsz <8 x float> %344, %548
  %553 = fsub reassoc ninf nsz <8 x float> %345, %549
  %554 = fsub reassoc ninf nsz <8 x float> %346, %550
  %555 = sitofp <8 x i32> %519 to <8 x float>
  %556 = sitofp <8 x i32> %520 to <8 x float>
  %557 = sitofp <8 x i32> %521 to <8 x float>
  %558 = sitofp <8 x i32> %522 to <8 x float>
  %559 = fsub reassoc ninf nsz <8 x float> %347, %555
  %560 = fsub reassoc ninf nsz <8 x float> %348, %556
  %561 = fsub reassoc ninf nsz <8 x float> %349, %557
  %562 = fsub reassoc ninf nsz <8 x float> %350, %558
  %563 = mul <8 x i32> %519, %broadcast.splat253
  %564 = mul <8 x i32> %520, %broadcast.splat253
  %565 = mul <8 x i32> %521, %broadcast.splat253
  %566 = mul <8 x i32> %522, %broadcast.splat253
  %567 = add <8 x i32> %503, %563
  %568 = add <8 x i32> %504, %564
  %569 = add <8 x i32> %505, %565
  %570 = add <8 x i32> %506, %566
  %571 = sext <8 x i32> %567 to <8 x i64>
  %572 = sext <8 x i32> %568 to <8 x i64>
  %573 = sext <8 x i32> %569 to <8 x i64>
  %574 = sext <8 x i32> %570 to <8 x i64>
  %575 = getelementptr float, float* %277, <8 x i64> %571
  %576 = getelementptr float, float* %277, <8 x i64> %572
  %577 = getelementptr float, float* %277, <8 x i64> %573
  %578 = getelementptr float, float* %277, <8 x i64> %574
  %wide.masked.gather260 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %575, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather261 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %576, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather262 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %577, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather263 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %578, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %579 = add <8 x i32> %531, %563
  %580 = add <8 x i32> %532, %564
  %581 = add <8 x i32> %533, %565
  %582 = add <8 x i32> %534, %566
  %583 = sext <8 x i32> %579 to <8 x i64>
  %584 = sext <8 x i32> %580 to <8 x i64>
  %585 = sext <8 x i32> %581 to <8 x i64>
  %586 = sext <8 x i32> %582 to <8 x i64>
  %587 = getelementptr float, float* %277, <8 x i64> %583
  %588 = getelementptr float, float* %277, <8 x i64> %584
  %589 = getelementptr float, float* %277, <8 x i64> %585
  %590 = getelementptr float, float* %277, <8 x i64> %586
  %wide.masked.gather264 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %587, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather265 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %588, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather266 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %589, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather267 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %590, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %591 = mul <8 x i32> %543, %broadcast.splat253
  %592 = mul <8 x i32> %544, %broadcast.splat253
  %593 = mul <8 x i32> %545, %broadcast.splat253
  %594 = mul <8 x i32> %546, %broadcast.splat253
  %595 = add <8 x i32> %591, %503
  %596 = add <8 x i32> %592, %504
  %597 = add <8 x i32> %593, %505
  %598 = add <8 x i32> %594, %506
  %599 = sext <8 x i32> %595 to <8 x i64>
  %600 = sext <8 x i32> %596 to <8 x i64>
  %601 = sext <8 x i32> %597 to <8 x i64>
  %602 = sext <8 x i32> %598 to <8 x i64>
  %603 = getelementptr float, float* %277, <8 x i64> %599
  %604 = getelementptr float, float* %277, <8 x i64> %600
  %605 = getelementptr float, float* %277, <8 x i64> %601
  %606 = getelementptr float, float* %277, <8 x i64> %602
  %wide.masked.gather268 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %603, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather269 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %604, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather270 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %605, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather271 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %606, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %607 = add <8 x i32> %531, %591
  %608 = add <8 x i32> %532, %592
  %609 = add <8 x i32> %533, %593
  %610 = add <8 x i32> %534, %594
  %611 = sext <8 x i32> %607 to <8 x i64>
  %612 = sext <8 x i32> %608 to <8 x i64>
  %613 = sext <8 x i32> %609 to <8 x i64>
  %614 = sext <8 x i32> %610 to <8 x i64>
  %615 = getelementptr float, float* %277, <8 x i64> %611
  %616 = getelementptr float, float* %277, <8 x i64> %612
  %617 = getelementptr float, float* %277, <8 x i64> %613
  %618 = getelementptr float, float* %277, <8 x i64> %614
  %wide.masked.gather272 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %615, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather273 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %616, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather274 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %617, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather275 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %618, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %619 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %551
  %620 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %552
  %621 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %553
  %622 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %554
  %623 = fmul reassoc ninf nsz <8 x float> %619, %wide.masked.gather260
  %624 = fmul reassoc ninf nsz <8 x float> %620, %wide.masked.gather261
  %625 = fmul reassoc ninf nsz <8 x float> %621, %wide.masked.gather262
  %626 = fmul reassoc ninf nsz <8 x float> %622, %wide.masked.gather263
  %627 = fmul reassoc ninf nsz <8 x float> %551, %wide.masked.gather264
  %628 = fmul reassoc ninf nsz <8 x float> %552, %wide.masked.gather265
  %629 = fmul reassoc ninf nsz <8 x float> %553, %wide.masked.gather266
  %630 = fmul reassoc ninf nsz <8 x float> %554, %wide.masked.gather267
  %631 = fadd reassoc ninf nsz <8 x float> %623, %627
  %632 = fadd reassoc ninf nsz <8 x float> %624, %628
  %633 = fadd reassoc ninf nsz <8 x float> %625, %629
  %634 = fadd reassoc ninf nsz <8 x float> %626, %630
  %635 = fmul reassoc ninf nsz <8 x float> %619, %wide.masked.gather268
  %636 = fmul reassoc ninf nsz <8 x float> %620, %wide.masked.gather269
  %637 = fmul reassoc ninf nsz <8 x float> %621, %wide.masked.gather270
  %638 = fmul reassoc ninf nsz <8 x float> %622, %wide.masked.gather271
  %639 = fmul reassoc ninf nsz <8 x float> %551, %wide.masked.gather272
  %640 = fmul reassoc ninf nsz <8 x float> %552, %wide.masked.gather273
  %641 = fmul reassoc ninf nsz <8 x float> %553, %wide.masked.gather274
  %642 = fmul reassoc ninf nsz <8 x float> %554, %wide.masked.gather275
  %643 = fadd reassoc ninf nsz <8 x float> %635, %639
  %644 = fadd reassoc ninf nsz <8 x float> %636, %640
  %645 = fadd reassoc ninf nsz <8 x float> %637, %641
  %646 = fadd reassoc ninf nsz <8 x float> %638, %642
  %647 = fsub reassoc ninf nsz <8 x float> %643, %631
  %648 = fsub reassoc ninf nsz <8 x float> %644, %632
  %649 = fsub reassoc ninf nsz <8 x float> %645, %633
  %650 = fsub reassoc ninf nsz <8 x float> %646, %634
  %651 = fmul reassoc ninf nsz <8 x float> %647, %559
  %652 = fmul reassoc ninf nsz <8 x float> %648, %560
  %653 = fmul reassoc ninf nsz <8 x float> %649, %561
  %654 = fmul reassoc ninf nsz <8 x float> %650, %562
  %655 = add <8 x i32> %435, %383
  %656 = add <8 x i32> %436, %384
  %657 = add <8 x i32> %437, %385
  %658 = add <8 x i32> %438, %386
  %659 = sext <8 x i32> %655 to <8 x i64>
  %660 = sext <8 x i32> %656 to <8 x i64>
  %661 = sext <8 x i32> %657 to <8 x i64>
  %662 = sext <8 x i32> %658 to <8 x i64>
  %663 = getelementptr float, float* %275, <8 x i64> %659
  %664 = getelementptr float, float* %275, <8 x i64> %660
  %665 = getelementptr float, float* %275, <8 x i64> %661
  %666 = getelementptr float, float* %275, <8 x i64> %662
  %wide.masked.gather276 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %663, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather277 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %664, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather278 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %665, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather279 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %666, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %667 = fsub reassoc ninf nsz <8 x float> %631, %wide.masked.gather276
  %668 = fsub reassoc ninf nsz <8 x float> %632, %wide.masked.gather277
  %669 = fsub reassoc ninf nsz <8 x float> %633, %wide.masked.gather278
  %670 = fsub reassoc ninf nsz <8 x float> %634, %wide.masked.gather279
  %671 = fadd reassoc ninf nsz <8 x float> %667, %651
  %672 = fadd reassoc ninf nsz <8 x float> %668, %652
  %673 = fadd reassoc ninf nsz <8 x float> %669, %653
  %674 = fadd reassoc ninf nsz <8 x float> %670, %654
  %675 = fmul reassoc ninf nsz <8 x float> %415, %415
  %676 = fmul reassoc ninf nsz <8 x float> %416, %416
  %677 = fmul reassoc ninf nsz <8 x float> %417, %417
  %678 = fmul reassoc ninf nsz <8 x float> %418, %418
  %679 = fadd reassoc ninf nsz <8 x float> %675, %vec.phi155
  %680 = fadd reassoc ninf nsz <8 x float> %676, %vec.phi156
  %681 = fadd reassoc ninf nsz <8 x float> %677, %vec.phi157
  %682 = fadd reassoc ninf nsz <8 x float> %678, %vec.phi158
  %683 = fmul reassoc ninf nsz <8 x float> %487, %415
  %684 = fmul reassoc ninf nsz <8 x float> %488, %416
  %685 = fmul reassoc ninf nsz <8 x float> %489, %417
  %686 = fmul reassoc ninf nsz <8 x float> %490, %418
  %687 = fadd reassoc ninf nsz <8 x float> %683, %vec.phi151
  %688 = fadd reassoc ninf nsz <8 x float> %684, %vec.phi152
  %689 = fadd reassoc ninf nsz <8 x float> %685, %vec.phi153
  %690 = fadd reassoc ninf nsz <8 x float> %686, %vec.phi154
  %691 = fmul reassoc ninf nsz <8 x float> %487, %487
  %692 = fmul reassoc ninf nsz <8 x float> %488, %488
  %693 = fmul reassoc ninf nsz <8 x float> %489, %489
  %694 = fmul reassoc ninf nsz <8 x float> %490, %490
  %695 = fadd reassoc ninf nsz <8 x float> %691, %vec.phi147
  %696 = fadd reassoc ninf nsz <8 x float> %692, %vec.phi148
  %697 = fadd reassoc ninf nsz <8 x float> %693, %vec.phi149
  %698 = fadd reassoc ninf nsz <8 x float> %694, %vec.phi150
  %699 = fmul reassoc ninf nsz <8 x float> %671, %415
  %700 = fmul reassoc ninf nsz <8 x float> %672, %416
  %701 = fmul reassoc ninf nsz <8 x float> %673, %417
  %702 = fmul reassoc ninf nsz <8 x float> %674, %418
  %703 = fadd reassoc ninf nsz <8 x float> %699, %vec.phi143
  %704 = fadd reassoc ninf nsz <8 x float> %700, %vec.phi144
  %705 = fadd reassoc ninf nsz <8 x float> %701, %vec.phi145
  %706 = fadd reassoc ninf nsz <8 x float> %702, %vec.phi146
  %707 = fmul reassoc ninf nsz <8 x float> %671, %487
  %708 = fmul reassoc ninf nsz <8 x float> %672, %488
  %709 = fmul reassoc ninf nsz <8 x float> %673, %489
  %710 = fmul reassoc ninf nsz <8 x float> %674, %490
  %711 = fadd reassoc ninf nsz <8 x float> %707, %vec.phi139
  %712 = fadd reassoc ninf nsz <8 x float> %708, %vec.phi140
  %713 = fadd reassoc ninf nsz <8 x float> %709, %vec.phi141
  %714 = fadd reassoc ninf nsz <8 x float> %710, %vec.phi142
  %715 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %671)
  %716 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %672)
  %717 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %673)
  %718 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %674)
  %719 = fadd reassoc ninf nsz <8 x float> %715, %vec.phi
  %720 = fadd reassoc ninf nsz <8 x float> %716, %vec.phi136
  %721 = fadd reassoc ninf nsz <8 x float> %717, %vec.phi137
  %722 = fadd reassoc ninf nsz <8 x float> %718, %vec.phi138
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32>
  %lsr.iv.next = add i32 %lsr.iv, -32
  %723 = icmp eq i32 %lsr.iv.next, 0
  br i1 %723, label %middle.block, label %vector.body, !llvm.loop !9

middle.block:                                     ; preds = %vector.body
  %bin.rdx298 = fadd reassoc ninf nsz <8 x float> %680, %679
  %bin.rdx299 = fadd reassoc ninf nsz <8 x float> %681, %bin.rdx298
  %bin.rdx300 = fadd reassoc ninf nsz <8 x float> %682, %bin.rdx299
  %bin.rdx294 = fadd reassoc ninf nsz <8 x float> %688, %687
  %bin.rdx295 = fadd reassoc ninf nsz <8 x float> %689, %bin.rdx294
  %bin.rdx296 = fadd reassoc ninf nsz <8 x float> %690, %bin.rdx295
  %bin.rdx290 = fadd reassoc ninf nsz <8 x float> %696, %695
  %bin.rdx291 = fadd reassoc ninf nsz <8 x float> %697, %bin.rdx290
  %bin.rdx292 = fadd reassoc ninf nsz <8 x float> %698, %bin.rdx291
  %bin.rdx286 = fadd reassoc ninf nsz <8 x float> %704, %703
  %bin.rdx287 = fadd reassoc ninf nsz <8 x float> %705, %bin.rdx286
  %bin.rdx288 = fadd reassoc ninf nsz <8 x float> %706, %bin.rdx287
  %724 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx300)
  %725 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx296)
  %726 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx292)
  %727 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx288)
  %bin.rdx282 = fadd reassoc ninf nsz <8 x float> %712, %711
  %bin.rdx283 = fadd reassoc ninf nsz <8 x float> %713, %bin.rdx282
  %bin.rdx284 = fadd reassoc ninf nsz <8 x float> %714, %bin.rdx283
  %728 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx284)
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %720, %719
  %bin.rdx280 = fadd reassoc ninf nsz <8 x float> %721, %bin.rdx
  %bin.rdx281 = fadd reassoc ninf nsz <8 x float> %722, %bin.rdx280
  %729 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx281)
  %730 = insertelement <2 x float> poison, float %727, i64 0
  %731 = insertelement <2 x float> %730, float %728, i64 1
  %732 = insertelement <2 x float> poison, float %724, i64 0
  %733 = insertelement <2 x float> %732, float %726, i64 1
  %734 = insertelement <4 x float> poison, float %727, i64 0
  %735 = insertelement <4 x float> %734, float %726, i64 1
  %736 = insertelement <4 x float> %735, float %725, i64 2
  %737 = insertelement <4 x float> %736, float %724, i64 3
  br i1 %cmp.n, label %after_for13, label %for_loop_body11.preheader

for_loop_body11.preheader:                        ; preds = %middle.block, %for_loop_body11.lr.ph
  %.04486.ph = phi i32 [ 0, %for_loop_body11.lr.ph ], [ %n.vec, %middle.block ]
  %.04585.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %729, %middle.block ]
  %.04684.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %728, %middle.block ]
  %.ph = phi <4 x float> [ zeroinitializer, %for_loop_body11.lr.ph ], [ %737, %middle.block ]
  %738 = extractelement <2 x float> %272, i64 1
  %739 = extractelement <2 x float> %272, i64 0
  %740 = insertelement <2 x i32> poison, i32 %276, i64 0
  %741 = shufflevector <2 x i32> %740, <2 x i32> poison, <2 x i32> zeroinitializer
  %742 = insertelement <2 x float*> poison, float* %275, i64 0
  %743 = shufflevector <2 x float*> %742, <2 x float*> poison, <2 x i32> zeroinitializer
  br label %for_loop_body11

after_if10:                                       ; preds = %true_block21, %false_block16, %after_for13, %for_loop_body4
  %.159 = phi i32 [ %.05894, %true_block21 ], [ %.05894, %false_block16 ], [ %.05894, %for_loop_body4 ], [ 0, %after_for13 ]
  %.157 = phi i32 [ 0, %true_block21 ], [ 1, %false_block16 ], [ 0, %for_loop_body4 ], [ 0, %after_for13 ]
  %.155 = phi float [ %869, %true_block21 ], [ %869, %false_block16 ], [ %.05496, %for_loop_body4 ], [ %869, %after_for13 ]
  %.153 = phi float [ %868, %true_block21 ], [ %868, %false_block16 ], [ %.05297, %for_loop_body4 ], [ %868, %after_for13 ]
  %744 = phi <2 x float> [ %885, %true_block21 ], [ %885, %false_block16 ], [ %272, %for_loop_body4 ], [ %272, %after_for13 ]
  %745 = add nuw nsw i32 %.05198, 1
  %exitcond110.not = icmp eq i32 %745, %258
  br i1 %exitcond110.not, label %after_for6, label %for_loop_body4

for_loop_body11:                                  ; preds = %for_loop_body11, %for_loop_body11.preheader
  %.04486 = phi i32 [ %857, %for_loop_body11 ], [ %.04486.ph, %for_loop_body11.preheader ]
  %.04585 = phi float [ %856, %for_loop_body11 ], [ %.04585.ph, %for_loop_body11.preheader ]
  %.04684 = phi float [ %854, %for_loop_body11 ], [ %.04684.ph, %for_loop_body11.preheader ]
  %746 = phi <4 x float> [ %852, %for_loop_body11 ], [ %.ph, %for_loop_body11.preheader ]
  %747 = sdiv i32 %.04486, %43
  %748 = mul i32 %747, %43
  %749 = icmp ne i32 %.04486, 0
  %750 = icmp ne i32 %.04486, %748
  %751 = and i1 %68, %749
  %752 = and i1 %751, %750
  %.neg73 = sext i1 %752 to i32
  %753 = add i32 %747, %.neg73
  %754 = sub i32 %753, %27
  %755 = add i32 %754, %265
  %756 = mul i32 %69, %753
  %757 = add i32 %269, %.04486
  %758 = add i32 %757, %756
  %759 = sitofp i32 %755 to float
  %760 = sitofp i32 %758 to float
  %761 = fadd reassoc ninf nsz float %738, %760
  %762 = fadd reassoc ninf nsz float %739, %759
  %763 = add i32 %758, 1
  %764 = add i32 %270, %.04486
  %765 = add i32 %764, %756
  %766 = tail call i32 @llvm.smin.i32(i32 %765, i32 %186)
  %767 = tail call i32 @llvm.smax.i32(i32 %766, i32 0)
  %768 = add i32 %755, 1
  %769 = insertelement <2 x i32> poison, i32 %768, i64 0
  %770 = insertelement <2 x i32> %769, i32 %755, i64 1
  %771 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %770, <2 x i32> %267)
  %772 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %771, <2 x i32> zeroinitializer)
  %773 = insertelement <2 x i32> poison, i32 %758, i64 0
  %774 = insertelement <2 x i32> %773, i32 %763, i64 1
  %775 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %774, <2 x i32> %268)
  %776 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %775, <2 x i32> zeroinitializer)
  %777 = add i32 %755, -1
  %778 = tail call i32 @llvm.smin.i32(i32 %777, i32 %191)
  %779 = tail call i32 @llvm.smax.i32(i32 %778, i32 0)
  %780 = mul <2 x i32> %772, %741
  %781 = add <2 x i32> %780, %776
  %782 = sext <2 x i32> %781 to <2 x i64>
  %783 = getelementptr float, <2 x float*> %743, <2 x i64> %782
  %784 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %783, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %785 = mul i32 %779, %276
  %786 = insertelement <2 x i32> %780, i32 %785, i64 0
  %787 = insertelement <2 x i32> %776, i32 %767, i64 1
  %788 = add <2 x i32> %786, %787
  %789 = sext <2 x i32> %788 to <2 x i64>
  %790 = getelementptr float, <2 x float*> %743, <2 x i64> %789
  %791 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %790, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %792 = fsub reassoc ninf nsz <2 x float> %784, %791
  %793 = fmul reassoc ninf nsz <2 x float> %792, <float 5.000000e-01, float 5.000000e-01>
  %794 = shufflevector <2 x float> %793, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %795 = tail call reassoc ninf nsz float @llvm.floor.f32(float %761)
  %796 = fptosi float %795 to i32
  %797 = tail call i32 @llvm.smin.i32(i32 %796, i32 %186)
  %798 = tail call i32 @llvm.smax.i32(i32 %797, i32 0)
  %799 = tail call reassoc ninf nsz float @llvm.floor.f32(float %762)
  %800 = fptosi float %799 to i32
  %801 = tail call i32 @llvm.smin.i32(i32 %800, i32 %191)
  %802 = tail call i32 @llvm.smax.i32(i32 %801, i32 0)
  %803 = add nuw i32 %798, 1
  %804 = tail call i32 @llvm.smin.i32(i32 %803, i32 %186)
  %805 = tail call i32 @llvm.smax.i32(i32 %804, i32 0)
  %806 = add nuw i32 %802, 1
  %807 = tail call i32 @llvm.smin.i32(i32 %806, i32 %191)
  %808 = tail call i32 @llvm.smax.i32(i32 %807, i32 0)
  %809 = sitofp i32 %798 to float
  %810 = fsub reassoc ninf nsz float %761, %809
  %811 = sitofp i32 %802 to float
  %812 = fsub reassoc ninf nsz float %762, %811
  %813 = mul i32 %802, %278
  %814 = add i32 %798, %813
  %815 = sext i32 %814 to i64
  %816 = getelementptr float, float* %277, i64 %815
  %817 = load float, float* %816, align 4
  %818 = add i32 %805, %813
  %819 = sext i32 %818 to i64
  %820 = getelementptr float, float* %277, i64 %819
  %821 = load float, float* %820, align 4
  %822 = mul i32 %808, %278
  %823 = add i32 %822, %798
  %824 = sext i32 %823 to i64
  %825 = getelementptr float, float* %277, i64 %824
  %826 = load float, float* %825, align 4
  %827 = add i32 %805, %822
  %828 = sext i32 %827 to i64
  %829 = getelementptr float, float* %277, i64 %828
  %830 = load float, float* %829, align 4
  %831 = fsub reassoc ninf nsz float 1.000000e+00, %810
  %832 = fmul reassoc ninf nsz float %831, %817
  %833 = fmul reassoc ninf nsz float %810, %821
  %834 = fadd reassoc ninf nsz float %832, %833
  %835 = fmul reassoc ninf nsz float %831, %826
  %836 = fmul reassoc ninf nsz float %810, %830
  %837 = fadd reassoc ninf nsz float %835, %836
  %838 = fsub reassoc ninf nsz float %837, %834
  %839 = fmul reassoc ninf nsz float %838, %812
  %shift = shufflevector <2 x i32> %780, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %840 = add <2 x i32> %776, %shift
  %841 = extractelement <2 x i32> %840, i64 0
  %842 = sext i32 %841 to i64
  %843 = getelementptr float, float* %275, i64 %842
  %844 = load float, float* %843, align 4
  %845 = fsub reassoc ninf nsz float %834, %844
  %846 = fadd reassoc ninf nsz float %845, %839
  %847 = extractelement <2 x float> %793, i64 0
  %848 = insertelement <4 x float> poison, float %846, i64 0
  %849 = shufflevector <4 x float> %848, <4 x float> %794, <4 x i32> <i32 0, i32 4, i32 4, i32 5>
  %850 = shufflevector <2 x float> %793, <2 x float> undef, <4 x i32> <i32 1, i32 0, i32 1, i32 1>
  %851 = fmul reassoc ninf nsz <4 x float> %849, %850
  %852 = fadd reassoc ninf nsz <4 x float> %851, %746
  %853 = fmul reassoc ninf nsz float %846, %847
  %854 = fadd reassoc ninf nsz float %853, %.04684
  %855 = tail call float @llvm.fabs.f32(float %846)
  %856 = fadd reassoc ninf nsz float %855, %.04585
  %857 = add nuw nsw i32 %.04486, 1
  %exitcond.not = icmp eq i32 %44, %857
  br i1 %exitcond.not, label %after_for13.loopexit, label %for_loop_body11, !llvm.loop !11

after_for13.loopexit:                             ; preds = %for_loop_body11
  %858 = extractelement <4 x float> %852, i64 2
  %859 = shufflevector <4 x float> %852, <4 x float> poison, <2 x i32> <i32 3, i32 1>
  %860 = shufflevector <4 x float> %852, <4 x float> poison, <2 x i32> <i32 0, i32 undef>
  %861 = insertelement <2 x float> %860, float %854, i64 1
  br label %after_for13

after_for13:                                      ; preds = %after_for13.loopexit, %middle.block, %true_block8
  %.049.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %725, %middle.block ], [ %858, %after_for13.loopexit ]
  %.045.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %729, %middle.block ], [ %856, %after_for13.loopexit ]
  %862 = phi <2 x float> [ zeroinitializer, %true_block8 ], [ %731, %middle.block ], [ %861, %after_for13.loopexit ]
  %863 = phi <2 x float> [ zeroinitializer, %true_block8 ], [ %733, %middle.block ], [ %859, %after_for13.loopexit ]
  %shift302 = shufflevector <2 x float> %863, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %864 = fmul reassoc ninf nsz <2 x float> %shift302, %863
  %865 = extractelement <2 x float> %864, i64 0
  %866 = fmul reassoc ninf nsz float %.049.lcssa, %.049.lcssa
  %867 = fsub reassoc ninf nsz float %865, %866
  %868 = tail call float @llvm.fabs.f32(float %867)
  %869 = fdiv reassoc ninf nsz float %.045.lcssa, %50
  %870 = fcmp reassoc ninf nsz olt float %868, 0x3F1A36E2E0000000
  br i1 %870, label %after_if10, label %false_block16

false_block16:                                    ; preds = %after_for13
  %871 = fdiv reassoc ninf nsz float 1.000000e+00, %867
  %872 = insertelement <2 x float> poison, float %.049.lcssa, i64 0
  %873 = shufflevector <2 x float> %872, <2 x float> poison, <2 x i32> zeroinitializer
  %874 = fmul reassoc ninf nsz <2 x float> %862, %873
  %875 = shufflevector <2 x float> %862, <2 x float> poison, <2 x i32> <i32 1, i32 0>
  %876 = fmul reassoc ninf nsz <2 x float> %875, %863
  %877 = fsub reassoc ninf nsz <2 x float> %874, %876
  %878 = insertelement <2 x float> poison, float %871, i64 0
  %879 = shufflevector <2 x float> %878, <2 x float> poison, <2 x i32> zeroinitializer
  %880 = fmul reassoc ninf nsz <2 x float> %877, %879
  %881 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %66, <2 x float> %880)
  %882 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %64, <2 x float> %881)
  %883 = fadd reassoc ninf nsz <2 x float> %882, %272
  %884 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %62, <2 x float> %883)
  %885 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %60, <2 x float> %884)
  %886 = fmul reassoc ninf nsz <2 x float> %882, %882
  %shift303 = shufflevector <2 x float> %886, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %887 = fadd reassoc ninf nsz <2 x float> %shift303, %886
  %888 = extractelement <2 x float> %887, i64 0
  %889 = load float, float* %264, align 4
  %890 = fmul reassoc ninf nsz float %889, %889
  %891 = fcmp reassoc ninf nsz olt float %888, %890
  br i1 %891, label %true_block21, label %after_if10

true_block21:                                     ; preds = %false_block16
  br label %after_if10

true_block24:                                     ; preds = %after_for6, %true_block1
  %.052.lcssa121 = phi float [ %.153, %after_for6 ], [ 0.000000e+00, %true_block1 ]
  %.054.lcssa119 = phi float [ %.155, %after_for6 ], [ 0.000000e+00, %true_block1 ]
  %892 = phi <2 x float> [ %744, %after_for6 ], [ %256, %true_block1 ]
  %893 = extractelement <2 x float> %892, i64 1
  store float %893, float* %100, align 4
  %894 = extractelement <2 x float> %892, i64 0
  store float %894, float* %109, align 4
  store float 1.000000e+00, float* %118, align 4
  %895 = fmul reassoc ninf nsz <2 x float> %892, %892
  %shift304 = shufflevector <2 x float> %895, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %896 = fadd reassoc ninf nsz <2 x float> %895, %shift304
  %897 = extractelement <2 x float> %896, i64 0
  %898 = fcmp reassoc ninf nsz ogt float %897, %53
  br i1 %898, label %after_if35.thread, label %after_if35

after_if35:                                       ; preds = %true_block24
  %899 = fcmp reassoc ninf nsz ogt float %897, %54
  %900 = fcmp reassoc ninf nsz ogt float %.054.lcssa119, 1.000000e+01
  %.042 = select i1 %899, i1 true, i1 %900
  %.043 = select i1 %.042, float 1.000000e+00, float 0.000000e+00
  %901 = fcmp reassoc ninf nsz ogt float %.054.lcssa119, 2.200000e+01
  %902 = fcmp reassoc ninf nsz olt float %.052.lcssa121, 0x3F50624DE0000000
  %.0 = select i1 %901, i1 true, i1 %902
  %cond.fr = freeze i1 %.0
  br i1 %cond.fr, label %after_if35.thread, label %903

after_if35.thread:                                ; preds = %after_if35, %true_block24
  br label %903

903:                                              ; preds = %after_if35.thread, %after_if35
  %904 = phi float [ 2.000000e+00, %after_if35.thread ], [ %.043, %after_if35 ]
  store float %.054.lcssa119, float* %126, align 4
  store float %.052.lcssa121, float* %135, align 4
  store float %904, float* %144, align 4
  store float %897, float* %153, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

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

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.floor.v8f32(<8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.minnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.maxnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
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
