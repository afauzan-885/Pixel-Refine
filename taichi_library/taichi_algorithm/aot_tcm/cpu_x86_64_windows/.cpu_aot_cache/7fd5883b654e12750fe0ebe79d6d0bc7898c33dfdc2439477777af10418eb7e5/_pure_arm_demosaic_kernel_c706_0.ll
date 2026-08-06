; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.54*, void (%struct.RuntimeContext.54*, i8*)*, void (%struct.RuntimeContext.54*, i8*, i32)*, void (%struct.RuntimeContext.54*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.54 = type { i8*, %struct.LLVMRuntime.53*, i32, i64* }
%struct.LLVMRuntime.53 = type { %struct.PreallocatedMemoryChunk.49, %struct.PreallocatedMemoryChunk.49, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.50*], [1024 x %struct.NodeManager.51*], [1024 x i8*], i8*, %struct.RandState.52*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.49 = type { i8*, i8*, i64 }
%struct.ListManager.50 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.53* }
%struct.NodeManager.51 = type { %struct.LLVMRuntime.53*, i32, i32, i32, i32, %struct.ListManager.50*, %struct.ListManager.50*, %struct.ListManager.50*, i32 }
%struct.RandState.52 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_pure_arm_demosaic_kernel_c706_0_kernel_0_serial(%struct.RuntimeContext.54* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.54* %context to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 2
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.54, %struct.RuntimeContext.54* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 16
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 20
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 4
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %6, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 8
  %27 = bitcast i8* %26 to i32*
  store i32 %22, i32* %27, align 4
  %28 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %29 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %29, i64 0, i32 5
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 12
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %6, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  store i32 %37, i32* %42, align 4
  %43 = mul i32 %37, %28
  %44 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %6, align 8
  %45 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %44, i64 0, i32 14
  %46 = bitcast i8** %45 to i32**
  %47 = load i32*, i32** %46, align 8
  store i32 %43, i32* %47, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_pure_arm_demosaic_kernel_c706_0_kernel_1_range_for(%struct.RuntimeContext.54* %context) local_unnamed_addr #2 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.54* %context, %struct.RuntimeContext.54** %4, align 8
  store void (%struct.RuntimeContext.54*, i8*)* null, void (%struct.RuntimeContext.54*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.54*, i8*, i32)* @function_body, void (%struct.RuntimeContext.54*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.54*, i8*)* null, void (%struct.RuntimeContext.54*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.54, %struct.RuntimeContext.54* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.54* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.54, %struct.RuntimeContext.54* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.54* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 8
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 9
  %29 = load i32, i32* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %36 = sub i32 0, %17
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %36, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if ]
  %.01429 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %196, %after_if ]
  %37 = load %struct.LLVMRuntime.53*, %struct.LLVMRuntime.53** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime.53, %struct.LLVMRuntime.53* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.01429, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.01429
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.01429, 0
  %48 = icmp ne i32 %.01429, %44
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg16 = sext i1 %50 to i32
  %51 = add i32 %43, %.neg16
  %52 = mul i32 %51, %42
  %53 = mul i32 %42, -1
  %54 = mul i32 %53, %51
  %55 = add i32 %.01429, %54
  %56 = sdiv i32 %51, 2
  %57 = icmp slt i32 %51, 0
  %58 = shl nsw i32 %56, 1
  %59 = icmp ne i32 %58, %51
  %60 = and i1 %57, %59
  %.neg17.neg = zext i1 %60 to i32
  %.neg19 = sub nsw i32 %.neg17.neg, %56
  %.neg18 = shl i32 %.neg19, 1
  %61 = sdiv i32 %55, 2
  %62 = icmp slt i32 %55, 0
  %63 = shl nsw i32 %61, 1
  %64 = icmp ne i32 %55, %63
  %65 = and i1 %62, %64
  %.neg20.neg = zext i1 %65 to i32
  %.neg22 = sub nsw i32 %.neg20.neg, %61
  %.neg21 = shl i32 %.neg22, 1
  %66 = sub i32 0, %51
  %.not = icmp eq i32 %.neg18, %66
  %67 = add i32 %lsr.iv, %52
  %.not23 = icmp eq i32 %67, %.neg21
  %68 = select i1 %.not23, i32 %23, i32 %25
  %69 = select i1 %.not23, i32 %27, i32 %29
  %70 = select i1 %.not, i32 %68, i32 %69
  %71 = add i32 %51, -1
  %72 = getelementptr inbounds i8, i8* %39, i64 8
  %73 = bitcast i8* %72 to i32*
  %74 = load i32, i32* %73, align 4
  %75 = add i32 %74, -1
  %76 = add i32 %51, 1
  %77 = add i32 %55, -1
  %78 = getelementptr inbounds i8, i8* %39, i64 12
  %79 = bitcast i8* %78 to i32*
  %80 = load i32, i32* %79, align 4
  %81 = add i32 %80, -1
  %82 = add i32 %55, 1
  %83 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %81, i32 %82)
  %85 = load float*, float** %31, align 8
  %86 = load i32, i32* %32, align 4
  %87 = mul i32 %51, %86
  %88 = sub i32 %86, %42
  %89 = mul i32 %88, %51
  %90 = add i32 %.01429, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, float* %85, i64 %91
  %93 = load float, float* %92, align 4
  %94 = getelementptr inbounds i8, i8* %39, i64 16
  %95 = bitcast i8* %94 to float*
  %96 = load float, float* %95, align 4
  %97 = fsub reassoc ninf nsz float %93, %96
  %98 = getelementptr inbounds i8, i8* %39, i64 20
  %99 = bitcast i8* %98 to float*
  %100 = load float, float* %99, align 4
  %101 = fmul reassoc ninf nsz float %97, %100
  %102 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %101, float 0.000000e+00)
  %103 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %102, float 1.000000e+00)
  %104 = tail call i32 @llvm.smax.i32(i32 %71, i32 0)
  %105 = tail call i32 @llvm.smin.i32(i32 %75, i32 %76)
  %106 = insertelement <2 x i32> poison, i32 %104, i64 0
  %107 = insertelement <2 x i32> %106, i32 %105, i64 1
  %108 = insertelement <2 x i32> poison, i32 %86, i64 0
  %109 = shufflevector <2 x i32> %108, <2 x i32> poison, <2 x i32> zeroinitializer
  %110 = mul <2 x i32> %107, %109
  %111 = extractelement <2 x i32> %110, i64 0
  %112 = sub i32 %111, %52
  %113 = add i32 %.01429, %112
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, float* %85, i64 %114
  %116 = load float, float* %115, align 4
  %117 = fsub reassoc ninf nsz float %116, %96
  %118 = fmul reassoc ninf nsz float %117, %100
  %119 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %118, float 0.000000e+00)
  %120 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %119, float 1.000000e+00)
  %121 = extractelement <2 x i32> %110, i64 1
  %122 = sub i32 %121, %52
  %123 = add i32 %.01429, %122
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %85, i64 %124
  %126 = load float, float* %125, align 4
  %127 = fsub reassoc ninf nsz float %126, %96
  %128 = fmul reassoc ninf nsz float %127, %100
  %129 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %128, float 0.000000e+00)
  %130 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %129, float 1.000000e+00)
  %131 = add i32 %83, %87
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %85, i64 %132
  %134 = load float, float* %133, align 4
  %135 = fsub reassoc ninf nsz float %134, %96
  %136 = fmul reassoc ninf nsz float %135, %100
  %137 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %136, float 0.000000e+00)
  %138 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %137, float 1.000000e+00)
  %139 = add i32 %84, %87
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %85, i64 %140
  %142 = load float, float* %141, align 4
  %143 = fsub reassoc ninf nsz float %142, %96
  %144 = fmul reassoc ninf nsz float %143, %100
  %145 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %144, float 0.000000e+00)
  %146 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %145, float 1.000000e+00)
  switch i32 %70, label %false_block2 [
    i32 0, label %true_block
    i32 2, label %true_block1
  ]

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %147 = insertelement <4 x i32> poison, i32 %83, i64 0
  %148 = insertelement <4 x i32> %147, i32 %84, i64 1
  %shuffle37 = shufflevector <4 x i32> %148, <4 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %149 = shufflevector <2 x i32> %110, <2 x i32> undef, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %150 = add <4 x i32> %shuffle37, %149
  %151 = sext <4 x i32> %150 to <4 x i64>
  %152 = insertelement <4 x float*> poison, float* %85, i64 0
  %shuffle36 = shufflevector <4 x float*> %152, <4 x float*> poison, <4 x i32> zeroinitializer
  %153 = getelementptr float, <4 x float*> %shuffle36, <4 x i64> %151
  %154 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %153, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %155 = insertelement <4 x float> poison, float %96, i64 0
  %shuffle38 = shufflevector <4 x float> %155, <4 x float> poison, <4 x i32> zeroinitializer
  %156 = fsub reassoc ninf nsz <4 x float> %154, %shuffle38
  %157 = insertelement <4 x float> poison, float %100, i64 0
  %shuffle39 = shufflevector <4 x float> %157, <4 x float> poison, <4 x i32> zeroinitializer
  %158 = fmul reassoc ninf nsz <4 x float> %156, %shuffle39
  %159 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %158, <4 x float> zeroinitializer)
  %160 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %159, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %161 = fadd reassoc ninf nsz float %130, %120
  %162 = fadd reassoc ninf nsz float %161, %138
  %163 = fadd reassoc ninf nsz float %162, %146
  %164 = fmul reassoc ninf nsz float %163, 2.500000e-01
  %165 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %160)
  %166 = fmul reassoc ninf nsz float %165, 2.500000e-01
  br label %after_if

after_if:                                         ; preds = %false_block2, %true_block1, %true_block
  %.013 = phi float [ %103, %true_block ], [ %215, %true_block1 ], [ %.30, %false_block2 ]
  %.012 = phi float [ %164, %true_block ], [ %213, %true_block1 ], [ %103, %false_block2 ]
  %.011 = phi float [ %166, %true_block ], [ %103, %true_block1 ], [ %.31, %false_block2 ]
  %167 = load float*, float** %33, align 8
  %168 = load i32, i32* %34, align 4
  %169 = load i32, i32* %35, align 4
  %170 = sub i32 %168, %42
  %171 = mul i32 %170, %51
  %172 = add i32 %.01429, %171
  %173 = mul i32 %172, %169
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, float* %167, i64 %174
  store float %.013, float* %175, align 4
  %176 = load float*, float** %33, align 8
  %177 = load i32, i32* %34, align 4
  %178 = load i32, i32* %35, align 4
  %179 = sub i32 %177, %42
  %180 = mul i32 %179, %51
  %181 = add i32 %.01429, %180
  %182 = mul i32 %181, %178
  %183 = add i32 %182, 1
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, float* %176, i64 %184
  store float %.012, float* %185, align 4
  %186 = load float*, float** %33, align 8
  %187 = load i32, i32* %34, align 4
  %188 = load i32, i32* %35, align 4
  %189 = sub i32 %187, %42
  %190 = mul i32 %189, %51
  %191 = add i32 %.01429, %190
  %192 = mul i32 %191, %188
  %193 = add i32 %192, 2
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %186, i64 %194
  store float %.011, float* %195, align 4
  %196 = add nsw i32 %.01429, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %19, %196
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block1:                                      ; preds = %for_loop_body
  %shuffle33 = shufflevector <2 x i32> %110, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %197 = insertelement <4 x i32> poison, i32 %83, i64 0
  %198 = insertelement <4 x i32> %197, i32 %84, i64 1
  %shuffle32 = shufflevector <4 x i32> %198, <4 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %199 = add <4 x i32> %shuffle32, %shuffle33
  %200 = sext <4 x i32> %199 to <4 x i64>
  %201 = insertelement <4 x float*> poison, float* %85, i64 0
  %shuffle = shufflevector <4 x float*> %201, <4 x float*> poison, <4 x i32> zeroinitializer
  %202 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %200
  %203 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %202, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %204 = insertelement <4 x float> poison, float %96, i64 0
  %shuffle34 = shufflevector <4 x float> %204, <4 x float> poison, <4 x i32> zeroinitializer
  %205 = fsub reassoc ninf nsz <4 x float> %203, %shuffle34
  %206 = insertelement <4 x float> poison, float %100, i64 0
  %shuffle35 = shufflevector <4 x float> %206, <4 x float> poison, <4 x i32> zeroinitializer
  %207 = fmul reassoc ninf nsz <4 x float> %205, %shuffle35
  %208 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %207, <4 x float> zeroinitializer)
  %209 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %208, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %210 = fadd reassoc ninf nsz float %130, %120
  %211 = fadd reassoc ninf nsz float %210, %138
  %212 = fadd reassoc ninf nsz float %211, %146
  %213 = fmul reassoc ninf nsz float %212, 2.500000e-01
  %214 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %209)
  %215 = fmul reassoc ninf nsz float %214, 2.500000e-01
  br label %after_if

false_block2:                                     ; preds = %for_loop_body
  %. = select i1 %.not, i32 %23, i32 %27
  %216 = and i32 %83, 2147483646
  %.not27 = icmp eq i32 %83, %216
  %.28 = select i1 %.not, i32 %25, i32 %29
  %spec.select = select i1 %.not27, i32 %., i32 %.28
  %217 = icmp eq i32 %spec.select, 0
  %218 = fadd reassoc ninf nsz float %146, %138
  %219 = fmul reassoc ninf nsz float %218, 5.000000e-01
  %220 = fadd reassoc ninf nsz float %130, %120
  %221 = fmul reassoc ninf nsz float %220, 5.000000e-01
  %.30 = select i1 %217, float %219, float %221
  %.31 = select i1 %217, float %221, float %219
  br label %after_if
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.54, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.54**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.54*, %struct.RuntimeContext.54** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.54*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.54*, i8*)*, void (%struct.RuntimeContext.54*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.54*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.54*, i8*, i32)*, void (%struct.RuntimeContext.54*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.54*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.54*, i8*)*, void (%struct.RuntimeContext.54*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.54*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.54* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.54* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.54* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.54, %struct.RuntimeContext.54* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.54* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !9

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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.54* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.54*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.54* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #1

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.maxnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.minnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
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
!10 = !{!"llvm.loop.mustprogress"}
!11 = distinct !{!11, !10}
