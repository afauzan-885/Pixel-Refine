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
define void @_dcb_refine_chroma_c706_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_refine_chroma_c706_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 8
  %29 = load i32, i32* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %33 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %34 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %35 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %36 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.lr.ph
  %.01129 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %245, %after_if9 ]
  %37 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.01129, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.01129
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.01129, 0
  %48 = icmp ne i32 %.01129, %44
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg12 = sext i1 %50 to i32
  %51 = load float*, float** %31, align 8
  %52 = load i32, i32* %32, align 4
  %53 = load i32, i32* %33, align 4
  %54 = getelementptr inbounds i8, i8* %39, i64 8
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = add i32 %56, -1
  %58 = getelementptr inbounds i8, i8* %39, i64 12
  %59 = bitcast i8* %58 to i32*
  %60 = load i32, i32* %59, align 4
  %61 = add i32 %60, -1
  %62 = insertelement <2 x i32> poison, i32 %61, i64 0
  %63 = shufflevector <2 x i32> %62, <2 x i32> poison, <2 x i32> zeroinitializer
  %64 = add i32 %43, %.neg12
  %65 = mul i32 %42, -1
  %66 = mul i32 %65, %64
  %67 = add i32 %.01129, %66
  %68 = sub i32 %52, %42
  %69 = mul i32 %68, %64
  %70 = add i32 %.01129, %69
  %71 = mul i32 %70, %53
  %72 = add i32 %71, 1
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, float* %51, i64 %73
  %75 = load float, float* %74, align 4
  %76 = add i32 %64, -1
  %77 = add i32 %67, -1
  %78 = insertelement <2 x i32> poison, i32 %67, i64 0
  %79 = insertelement <2 x i32> %78, i32 %77, i64 1
  %80 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %79, <2 x i32> zeroinitializer)
  %81 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %63, <2 x i32> %80)
  %82 = insertelement <2 x i32> poison, i32 %64, i64 0
  %83 = insertelement <2 x i32> %82, i32 %76, i64 1
  %84 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %83, <2 x i32> zeroinitializer)
  %85 = insertelement <2 x i32> poison, i32 %57, i64 0
  %86 = shufflevector <2 x i32> %85, <2 x i32> poison, <2 x i32> zeroinitializer
  %87 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %86, <2 x i32> %84)
  %88 = insertelement <2 x i32> poison, i32 %52, i64 0
  %89 = shufflevector <2 x i32> %88, <2 x i32> poison, <2 x i32> zeroinitializer
  %90 = mul <2 x i32> %87, %89
  %shift = shufflevector <2 x i32> %90, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %91 = add <2 x i32> %shift, %81
  %92 = extractelement <2 x i32> %91, i64 0
  %93 = mul i32 %92, %53
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, float* %51, i64 %94
  %96 = load float, float* %95, align 4
  %97 = add i32 %93, 1
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, float* %51, i64 %98
  %100 = load float, float* %99, align 4
  %101 = add i32 %67, 1
  %102 = tail call i32 @llvm.smax.i32(i32 %101, i32 0)
  %103 = tail call i32 @llvm.smin.i32(i32 %61, i32 %102)
  %104 = add i32 %64, 1
  %105 = tail call i32 @llvm.smax.i32(i32 %104, i32 0)
  %106 = tail call i32 @llvm.smin.i32(i32 %57, i32 %105)
  %107 = mul i32 %106, %52
  %108 = insertelement <8 x i32> poison, i32 %107, i64 0
  %109 = shufflevector <2 x i32> %90, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %110 = shufflevector <8 x i32> %108, <8 x i32> %109, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle30 = shufflevector <8 x i32> %110, <8 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 2, i32 2>
  %111 = insertelement <8 x i32> poison, i32 %103, i64 0
  %112 = shufflevector <2 x i32> %81, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %113 = shufflevector <8 x i32> %111, <8 x i32> %112, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle31 = shufflevector <8 x i32> %113, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 1, i32 2, i32 0, i32 2>
  %114 = add <8 x i32> %shuffle30, %shuffle31
  %115 = insertelement <8 x i32> poison, i32 %53, i64 0
  %shuffle32 = shufflevector <8 x i32> %115, <8 x i32> poison, <8 x i32> zeroinitializer
  %116 = mul <8 x i32> %114, %shuffle32
  %117 = extractelement <8 x i32> %116, i64 7
  %118 = extractelement <8 x i32> %116, i64 6
  %119 = extractelement <8 x i32> %116, i64 5
  %120 = extractelement <8 x i32> %116, i64 4
  %121 = shufflevector <8 x i32> %116, <8 x i32> undef, <4 x i32> <i32 7, i32 6, i32 5, i32 4>
  %122 = sext <4 x i32> %121 to <4 x i64>
  %123 = extractelement <4 x i64> %122, i64 0
  %124 = getelementptr float, float* %51, i64 %123
  %125 = load float, float* %124, align 4
  %126 = extractelement <4 x i64> %122, i64 1
  %127 = getelementptr float, float* %51, i64 %126
  %128 = load float, float* %127, align 4
  %129 = extractelement <4 x i64> %122, i64 2
  %130 = getelementptr float, float* %51, i64 %129
  %131 = load float, float* %130, align 4
  %132 = extractelement <4 x i64> %122, i64 3
  %133 = getelementptr float, float* %51, i64 %132
  %134 = load float, float* %133, align 4
  %135 = extractelement <8 x i32> %116, i64 3
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, float* %51, i64 %136
  %138 = load float, float* %137, align 4
  %139 = extractelement <8 x i32> %116, i64 2
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %51, i64 %140
  %142 = load float, float* %141, align 4
  %143 = extractelement <8 x i32> %116, i64 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, float* %51, i64 %144
  %146 = load float, float* %145, align 4
  %147 = insertelement <8 x i32> poison, i32 %143, i64 0
  %148 = insertelement <8 x i32> %147, i32 %139, i64 1
  %149 = insertelement <8 x i32> %148, i32 %135, i64 2
  %150 = insertelement <8 x i32> %149, i32 %120, i64 3
  %151 = insertelement <8 x i32> %150, i32 %119, i64 4
  %152 = insertelement <8 x i32> %151, i32 %118, i64 5
  %153 = insertelement <8 x i32> %152, i32 %117, i64 6
  %154 = insertelement <8 x i32> %153, i32 %93, i64 7
  %155 = add <8 x i32> %154, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %156 = sext <8 x i32> %155 to <8 x i64>
  %157 = insertelement <8 x float*> poison, float* %51, i64 0
  %shuffle33 = shufflevector <8 x float*> %157, <8 x float*> poison, <8 x i32> zeroinitializer
  %158 = getelementptr float, <8 x float*> %shuffle33, <8 x i64> %156
  %159 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %158, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %160 = extractelement <8 x i32> %116, i64 0
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %51, i64 %161
  %163 = load float, float* %162, align 4
  %164 = add <8 x i32> %116, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %165 = sext <8 x i32> %164 to <8 x i64>
  %166 = getelementptr float, <8 x float*> %shuffle33, <8 x i64> %165
  %167 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %166, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %168 = fadd reassoc ninf nsz float %125, %96
  %169 = fadd reassoc ninf nsz float %168, %128
  %170 = fadd reassoc ninf nsz float %169, %131
  %171 = fadd reassoc ninf nsz float %170, %134
  %172 = fadd reassoc ninf nsz float %171, %138
  %173 = fadd reassoc ninf nsz float %172, %142
  %174 = fadd reassoc ninf nsz float %173, %146
  %175 = fadd reassoc ninf nsz float %174, %163
  %176 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float %100, <8 x float> %167)
  %177 = fsub reassoc ninf nsz float %175, %176
  %178 = add i32 %160, 2
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, float* %51, i64 %179
  %181 = load float, float* %180, align 4
  %182 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %159)
  %183 = fsub reassoc ninf nsz float %182, %176
  %184 = fadd reassoc ninf nsz float %183, %181
  %185 = fmul reassoc ninf nsz float %177, 0x3FBC71C720000000
  %186 = fadd reassoc ninf nsz float %185, %75
  %187 = fmul reassoc ninf nsz float %184, 0x3FBC71C720000000
  %188 = fadd reassoc ninf nsz float %187, %75
  %189 = insertelement <2 x i32> %78, i32 %64, i64 1
  %190 = sdiv <2 x i32> %189, <i32 2, i32 2>
  %191 = icmp slt <2 x i32> %189, zeroinitializer
  %192 = shl nsw <2 x i32> %190, <i32 1, i32 1>
  %193 = icmp ne <2 x i32> %192, %189
  %194 = and <2 x i1> %191, %193
  %195 = zext <2 x i1> %194 to <2 x i32>
  %196 = sub nsw <2 x i32> %195, %190
  %197 = shl <2 x i32> %196, <i32 1, i32 1>
  %198 = sub <2 x i32> zeroinitializer, %189
  %199 = icmp eq <2 x i32> %197, %198
  %200 = extractelement <2 x i1> %199, i64 0
  %. = select i1 %200, i32 %23, i32 %25
  %.19 = select i1 %200, i32 %27, i32 %29
  %201 = extractelement <2 x i1> %199, i64 1
  %.08 = select i1 %201, i32 %., i32 %.19
  switch i32 %.08, label %after_if9 [
    i32 0, label %true_block7
    i32 2, label %true_block10
  ]

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block7:                                      ; preds = %for_loop_body
  %202 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %203 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %202, i64 0, i32 1, i32 1
  %204 = load float*, float** %203, align 8
  %205 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %202, i64 0, i32 1, i32 0, i32 1
  %206 = load i32, i32* %205, align 4
  %207 = sub i32 %206, %42
  %208 = mul i32 %207, %64
  %209 = add i32 %.01129, %208
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, float* %204, i64 %210
  %212 = load float, float* %211, align 4
  br label %after_if9

after_if9:                                        ; preds = %true_block10, %true_block7, %for_loop_body
  %.010 = phi float [ %212, %true_block7 ], [ %186, %true_block10 ], [ %186, %for_loop_body ]
  %.09 = phi float [ %188, %true_block7 ], [ %256, %true_block10 ], [ %188, %for_loop_body ]
  %213 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.010, float 0.000000e+00)
  %214 = load float*, float** %34, align 8
  %215 = load i32, i32* %35, align 4
  %216 = load i32, i32* %36, align 4
  %217 = sub i32 %215, %42
  %218 = mul i32 %217, %64
  %219 = add i32 %.01129, %218
  %220 = mul i32 %219, %216
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %214, i64 %221
  store float %213, float* %222, align 4
  %223 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %75, float 0.000000e+00)
  %224 = load float*, float** %34, align 8
  %225 = load i32, i32* %35, align 4
  %226 = load i32, i32* %36, align 4
  %227 = sub i32 %225, %42
  %228 = mul i32 %227, %64
  %229 = add i32 %.01129, %228
  %230 = mul i32 %229, %226
  %231 = add i32 %230, 1
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, float* %224, i64 %232
  store float %223, float* %233, align 4
  %234 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.09, float 0.000000e+00)
  %235 = load float*, float** %34, align 8
  %236 = load i32, i32* %35, align 4
  %237 = load i32, i32* %36, align 4
  %238 = sub i32 %236, %42
  %239 = mul i32 %238, %64
  %240 = add i32 %.01129, %239
  %241 = mul i32 %240, %237
  %242 = add i32 %241, 2
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, float* %235, i64 %243
  store float %234, float* %244, align 4
  %245 = add nsw i32 %.01129, 1
  %exitcond.not = icmp eq i32 %19, %245
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %for_loop_body
  %246 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %247 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %246, i64 0, i32 1, i32 1
  %248 = load float*, float** %247, align 8
  %249 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %246, i64 0, i32 1, i32 0, i32 1
  %250 = load i32, i32* %249, align 4
  %251 = sub i32 %250, %42
  %252 = mul i32 %251, %64
  %253 = add i32 %.01129, %252
  %254 = sext i32 %253 to i64
  %255 = getelementptr float, float* %248, i64 %254
  %256 = load float, float* %255, align 4
  br label %after_if9
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
