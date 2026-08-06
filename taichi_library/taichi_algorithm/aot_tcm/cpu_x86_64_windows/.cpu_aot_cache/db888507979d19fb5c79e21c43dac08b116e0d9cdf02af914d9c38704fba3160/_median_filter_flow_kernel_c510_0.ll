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
define void @_median_filter_flow_kernel_c510_0_kernel_0_serial(%struct.RuntimeContext.96* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.96* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_median_filter_flow_kernel_c510_0_kernel_1_range_for(%struct.RuntimeContext.96* %context) local_unnamed_addr #1 {
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
  %3 = alloca [9 x float], align 4
  %4 = alloca [9 x float], align 4
  %5 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %0, i64 0, i32 1
  %6 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %6, i64 0, i32 14
  %8 = bitcast i8** %7 to i32**
  %9 = load i32*, i32** %8, align 8
  %10 = load i32, i32* %9, align 4
  %11 = add i32 %10, 7
  %12 = sdiv i32 %11, 8
  %13 = icmp slt i32 %11, 0
  %14 = shl nsw i32 %12, 3
  %15 = icmp ne i32 %14, %11
  %16 = and i1 %13, %15
  %.neg = sext i1 %16 to i32
  %17 = add nsw i32 %12, %.neg
  %18 = tail call i32 @llvm.smax.i32(i32 %17, i32 512)
  %19 = mul i32 %18, %2
  %20 = add i32 %19, %18
  %21 = tail call i32 @llvm.smin.i32(i32 %10, i32 %20)
  %22 = icmp slt i32 %19, %21
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = bitcast %struct.RuntimeContext.96* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %24 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %23, align 8
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 8
  %29 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 4
  %30 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 0
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 1, i32 1
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 1, i32 0, i32 1
  %33 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 1, i32 0, i32 2
  %34 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 8
  %35 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 4
  %36 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 0
  %37 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 1
  %38 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 1
  %39 = bitcast [9 x float]* %3 to <8 x float>*
  %40 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 2
  %41 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 3
  %42 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 5
  %43 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 6
  %44 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 7
  %45 = bitcast [9 x float]* %4 to <8 x float>*
  %46 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 2
  %47 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 3
  %48 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 5
  %49 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 6
  %50 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 7
  br label %for_loop_body5.preheader

after_for.loopexit:                               ; preds = %after_for15.7
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body5.preheader:                         ; preds = %after_for15.7, %for_loop_body.lr.ph
  %.01929 = phi i32 [ %19, %for_loop_body.lr.ph ], [ %338, %after_for15.7 ]
  %51 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %5, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %51, i64 0, i32 14
  %53 = load i8*, i8** %52, align 8
  %54 = getelementptr inbounds i8, i8* %53, i64 4
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = sdiv i32 %.01929, %56
  %58 = mul i32 %57, %56
  %59 = xor i32 %56, %.01929
  %60 = icmp slt i32 %59, 0
  %61 = icmp ne i32 %.01929, 0
  %62 = icmp ne i32 %.01929, %58
  %63 = and i1 %61, %60
  %64 = and i1 %63, %62
  %.neg24 = sext i1 %64 to i32
  %65 = add i32 %57, %.neg24
  %66 = mul i32 %65, %56
  %67 = add i32 %65, -1
  %68 = getelementptr inbounds i8, i8* %53, i64 8
  %69 = bitcast i8* %68 to i32*
  %70 = load i32, i32* %69, align 4
  %71 = add i32 %70, -1
  %72 = tail call i32 @llvm.smin.i32(i32 %67, i32 %71)
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = getelementptr inbounds i8, i8* %53, i64 12
  %75 = bitcast i8* %74 to i32*
  %76 = load i32, i32* %75, align 4
  %77 = add i32 %76, -1
  %78 = load float*, float** %25, align 8
  %79 = load i32, i32* %26, align 4
  %80 = load i32, i32* %27, align 4
  %81 = add i32 %65, 1
  %82 = tail call i32 @llvm.smin.i32(i32 %81, i32 %71)
  %83 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %84 = insertelement <4 x i32> poison, i32 %73, i64 0
  %85 = insertelement <4 x i32> %84, i32 %65, i64 1
  %86 = insertelement <4 x i32> %85, i32 %.01929, i64 2
  %87 = insertelement <4 x i32> %86, i32 %83, i64 3
  %88 = insertelement <4 x i32> poison, i32 %79, i64 0
  %89 = insertelement <4 x i32> %88, i32 %66, i64 1
  %shuffle65 = shufflevector <4 x i32> %89, <4 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 0>
  %90 = mul <4 x i32> %87, %shuffle65
  %91 = sub <4 x i32> %87, %shuffle65
  %92 = shufflevector <4 x i32> %90, <4 x i32> %91, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 6, i32 1, i32 3, i32 3>
  %93 = extractelement <4 x i32> %91, i64 2
  %94 = add i32 %93, -1
  %95 = tail call i32 @llvm.smin.i32(i32 %94, i32 %77)
  %96 = tail call i32 @llvm.smax.i32(i32 %95, i32 0)
  %97 = add i32 %93, 1
  %98 = tail call i32 @llvm.smin.i32(i32 %97, i32 %77)
  %99 = tail call i32 @llvm.smax.i32(i32 %98, i32 0)
  %100 = insertelement <8 x i32> poison, i32 %96, i64 0
  %101 = shufflevector <8 x i32> %100, <8 x i32> %92, <8 x i32> <i32 0, i32 12, i32 undef, i32 11, i32 undef, i32 undef, i32 undef, i32 undef>
  %102 = insertelement <8 x i32> %101, i32 %99, i64 2
  %shuffle66 = shufflevector <8 x i32> %102, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 3, i32 2, i32 0, i32 1>
  %103 = add <8 x i32> %92, %shuffle66
  %104 = insertelement <8 x i32> poison, i32 %80, i64 0
  %shuffle67 = shufflevector <8 x i32> %104, <8 x i32> poison, <8 x i32> zeroinitializer
  %105 = mul <8 x i32> %103, %shuffle67
  %106 = sext <8 x i32> %105 to <8 x i64>
  %107 = insertelement <8 x float*> poison, float* %78, i64 0
  %shuffle64 = shufflevector <8 x float*> %107, <8 x float*> poison, <8 x i32> zeroinitializer
  %108 = getelementptr float, <8 x float*> %shuffle64, <8 x i64> %106
  %109 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %108, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %110 = extractelement <4 x i32> %90, i64 3
  %111 = add i32 %99, %110
  %112 = mul i32 %111, %80
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %78, i64 %113
  %115 = load float, float* %114, align 4
  store <8 x float> %109, <8 x float>* %39, align 4
  store float %115, float* %28, align 4
  %116 = extractelement <8 x float> %109, i64 0
  %117 = load float, float* %37, align 4
  %118 = fcmp reassoc ninf nsz ogt float %116, %117
  br i1 %118, label %true_block, label %after_if

true_block.1:                                     ; preds = %after_if.7
  store float %214, float* %30, align 4
  store float %.pre, float* %37, align 4
  br label %after_if.1

after_if.1:                                       ; preds = %after_if.7, %true_block.1
  %119 = phi float [ %.pre, %true_block.1 ], [ %214, %after_if.7 ]
  %120 = load float, float* %40, align 4
  %121 = fcmp reassoc ninf nsz ogt float %119, %120
  br i1 %121, label %true_block.1.1, label %after_if.1.1

true_block.1.1:                                   ; preds = %after_if.1
  store float %120, float* %37, align 4
  store float %119, float* %40, align 4
  br label %after_if.1.1

after_if.1.1:                                     ; preds = %true_block.1.1, %after_if.1
  %122 = phi float [ %119, %true_block.1.1 ], [ %120, %after_if.1 ]
  %123 = load float, float* %41, align 4
  %124 = fcmp reassoc ninf nsz ogt float %122, %123
  br i1 %124, label %true_block.1.2, label %after_if.1.2

true_block.1.2:                                   ; preds = %after_if.1.1
  store float %123, float* %40, align 4
  store float %122, float* %41, align 4
  br label %after_if.1.2

after_if.1.2:                                     ; preds = %true_block.1.2, %after_if.1.1
  %125 = phi float [ %122, %true_block.1.2 ], [ %123, %after_if.1.1 ]
  %126 = load float, float* %29, align 4
  %127 = fcmp reassoc ninf nsz ogt float %125, %126
  br i1 %127, label %true_block.1.3, label %after_if.1.3

true_block.1.3:                                   ; preds = %after_if.1.2
  store float %126, float* %41, align 4
  store float %125, float* %29, align 4
  br label %after_if.1.3

after_if.1.3:                                     ; preds = %true_block.1.3, %after_if.1.2
  %128 = phi float [ %125, %true_block.1.3 ], [ %126, %after_if.1.2 ]
  %129 = load float, float* %42, align 4
  %130 = fcmp reassoc ninf nsz ogt float %128, %129
  br i1 %130, label %true_block.1.4, label %after_if.1.4

true_block.1.4:                                   ; preds = %after_if.1.3
  store float %129, float* %29, align 4
  store float %128, float* %42, align 4
  br label %after_if.1.4

after_if.1.4:                                     ; preds = %true_block.1.4, %after_if.1.3
  %131 = phi float [ %128, %true_block.1.4 ], [ %129, %after_if.1.3 ]
  %132 = load float, float* %43, align 4
  %133 = fcmp reassoc ninf nsz ogt float %131, %132
  br i1 %133, label %true_block.1.5, label %after_if.1.5

true_block.1.5:                                   ; preds = %after_if.1.4
  store float %132, float* %42, align 4
  store float %131, float* %43, align 4
  br label %after_if.1.5

after_if.1.5:                                     ; preds = %true_block.1.5, %after_if.1.4
  %134 = phi float [ %131, %true_block.1.5 ], [ %132, %after_if.1.4 ]
  %135 = load float, float* %44, align 4
  %136 = fcmp reassoc ninf nsz ogt float %134, %135
  br i1 %136, label %true_block.1.6, label %after_if.1.6

true_block.1.6:                                   ; preds = %after_if.1.5
  store float %135, float* %43, align 4
  store float %134, float* %44, align 4
  br label %after_if.1.6

after_if.1.6:                                     ; preds = %true_block.1.6, %after_if.1.5
  %.pre48 = load float, float* %30, align 4
  %137 = load float, float* %37, align 4
  %138 = fcmp reassoc ninf nsz ogt float %.pre48, %137
  br i1 %138, label %true_block.2, label %after_if.2

true_block.2:                                     ; preds = %after_if.1.6
  store float %137, float* %30, align 4
  store float %.pre48, float* %37, align 4
  br label %after_if.2

after_if.2:                                       ; preds = %true_block.2, %after_if.1.6
  %139 = phi float [ %.pre48, %true_block.2 ], [ %137, %after_if.1.6 ]
  %140 = load float, float* %40, align 4
  %141 = fcmp reassoc ninf nsz ogt float %139, %140
  br i1 %141, label %true_block.2.1, label %after_if.2.1

true_block.2.1:                                   ; preds = %after_if.2
  store float %140, float* %37, align 4
  store float %139, float* %40, align 4
  br label %after_if.2.1

after_if.2.1:                                     ; preds = %true_block.2.1, %after_if.2
  %142 = phi float [ %139, %true_block.2.1 ], [ %140, %after_if.2 ]
  %143 = load float, float* %41, align 4
  %144 = fcmp reassoc ninf nsz ogt float %142, %143
  br i1 %144, label %true_block.2.2, label %after_if.2.2

true_block.2.2:                                   ; preds = %after_if.2.1
  store float %143, float* %40, align 4
  store float %142, float* %41, align 4
  br label %after_if.2.2

after_if.2.2:                                     ; preds = %true_block.2.2, %after_if.2.1
  %145 = phi float [ %142, %true_block.2.2 ], [ %143, %after_if.2.1 ]
  %146 = load float, float* %29, align 4
  %147 = fcmp reassoc ninf nsz ogt float %145, %146
  br i1 %147, label %true_block.2.3, label %after_if.2.3

true_block.2.3:                                   ; preds = %after_if.2.2
  store float %146, float* %41, align 4
  store float %145, float* %29, align 4
  br label %after_if.2.3

after_if.2.3:                                     ; preds = %true_block.2.3, %after_if.2.2
  %148 = phi float [ %145, %true_block.2.3 ], [ %146, %after_if.2.2 ]
  %149 = load float, float* %42, align 4
  %150 = fcmp reassoc ninf nsz ogt float %148, %149
  br i1 %150, label %true_block.2.4, label %after_if.2.4

true_block.2.4:                                   ; preds = %after_if.2.3
  store float %149, float* %29, align 4
  store float %148, float* %42, align 4
  br label %after_if.2.4

after_if.2.4:                                     ; preds = %true_block.2.4, %after_if.2.3
  %151 = phi float [ %148, %true_block.2.4 ], [ %149, %after_if.2.3 ]
  %152 = load float, float* %43, align 4
  %153 = fcmp reassoc ninf nsz ogt float %151, %152
  br i1 %153, label %true_block.2.5, label %after_if.2.5

true_block.2.5:                                   ; preds = %after_if.2.4
  store float %152, float* %42, align 4
  store float %151, float* %43, align 4
  br label %after_if.2.5

after_if.2.5:                                     ; preds = %true_block.2.5, %after_if.2.4
  %.pre49 = load float, float* %30, align 4
  %154 = load float, float* %37, align 4
  %155 = fcmp reassoc ninf nsz ogt float %.pre49, %154
  br i1 %155, label %true_block.3, label %after_if.3

true_block.3:                                     ; preds = %after_if.2.5
  store float %154, float* %30, align 4
  store float %.pre49, float* %37, align 4
  br label %after_if.3

after_if.3:                                       ; preds = %true_block.3, %after_if.2.5
  %156 = phi float [ %.pre49, %true_block.3 ], [ %154, %after_if.2.5 ]
  %157 = load float, float* %40, align 4
  %158 = fcmp reassoc ninf nsz ogt float %156, %157
  br i1 %158, label %true_block.3.1, label %after_if.3.1

true_block.3.1:                                   ; preds = %after_if.3
  store float %157, float* %37, align 4
  store float %156, float* %40, align 4
  br label %after_if.3.1

after_if.3.1:                                     ; preds = %true_block.3.1, %after_if.3
  %159 = phi float [ %156, %true_block.3.1 ], [ %157, %after_if.3 ]
  %160 = load float, float* %41, align 4
  %161 = fcmp reassoc ninf nsz ogt float %159, %160
  br i1 %161, label %true_block.3.2, label %after_if.3.2

true_block.3.2:                                   ; preds = %after_if.3.1
  store float %160, float* %40, align 4
  store float %159, float* %41, align 4
  br label %after_if.3.2

after_if.3.2:                                     ; preds = %true_block.3.2, %after_if.3.1
  %162 = phi float [ %159, %true_block.3.2 ], [ %160, %after_if.3.1 ]
  %163 = load float, float* %29, align 4
  %164 = fcmp reassoc ninf nsz ogt float %162, %163
  br i1 %164, label %true_block.3.3, label %after_if.3.3

true_block.3.3:                                   ; preds = %after_if.3.2
  store float %163, float* %41, align 4
  store float %162, float* %29, align 4
  br label %after_if.3.3

after_if.3.3:                                     ; preds = %true_block.3.3, %after_if.3.2
  %165 = phi float [ %162, %true_block.3.3 ], [ %163, %after_if.3.2 ]
  %166 = load float, float* %42, align 4
  %167 = fcmp reassoc ninf nsz ogt float %165, %166
  br i1 %167, label %true_block.3.4, label %after_if.3.4

true_block.3.4:                                   ; preds = %after_if.3.3
  store float %166, float* %29, align 4
  store float %165, float* %42, align 4
  br label %after_if.3.4

after_if.3.4:                                     ; preds = %true_block.3.4, %after_if.3.3
  %.pre50 = load float, float* %30, align 4
  %168 = load float, float* %37, align 4
  %169 = fcmp reassoc ninf nsz ogt float %.pre50, %168
  br i1 %169, label %true_block.4, label %after_if.4

true_block.4:                                     ; preds = %after_if.3.4
  store float %168, float* %30, align 4
  store float %.pre50, float* %37, align 4
  br label %after_if.4

after_if.4:                                       ; preds = %true_block.4, %after_if.3.4
  %170 = phi float [ %.pre50, %true_block.4 ], [ %168, %after_if.3.4 ]
  %171 = load float, float* %40, align 4
  %172 = fcmp reassoc ninf nsz ogt float %170, %171
  br i1 %172, label %true_block.4.1, label %after_if.4.1

true_block.4.1:                                   ; preds = %after_if.4
  store float %171, float* %37, align 4
  store float %170, float* %40, align 4
  br label %after_if.4.1

after_if.4.1:                                     ; preds = %true_block.4.1, %after_if.4
  %173 = phi float [ %170, %true_block.4.1 ], [ %171, %after_if.4 ]
  %174 = load float, float* %41, align 4
  %175 = fcmp reassoc ninf nsz ogt float %173, %174
  br i1 %175, label %true_block.4.2, label %after_if.4.2

true_block.4.2:                                   ; preds = %after_if.4.1
  store float %174, float* %40, align 4
  store float %173, float* %41, align 4
  br label %after_if.4.2

after_if.4.2:                                     ; preds = %true_block.4.2, %after_if.4.1
  %176 = phi float [ %173, %true_block.4.2 ], [ %174, %after_if.4.1 ]
  %177 = load float, float* %29, align 4
  %178 = fcmp reassoc ninf nsz ogt float %176, %177
  br i1 %178, label %true_block.4.3, label %after_if.4.3

true_block.4.3:                                   ; preds = %after_if.4.2
  store float %177, float* %41, align 4
  store float %176, float* %29, align 4
  br label %after_if.4.3

after_if.4.3:                                     ; preds = %true_block.4.3, %after_if.4.2
  %.pre51 = load float, float* %30, align 4
  %179 = load float, float* %37, align 4
  %180 = fcmp reassoc ninf nsz ogt float %.pre51, %179
  br i1 %180, label %true_block.5, label %after_if.5

true_block.5:                                     ; preds = %after_if.4.3
  store float %179, float* %30, align 4
  store float %.pre51, float* %37, align 4
  br label %after_if.5

after_if.5:                                       ; preds = %true_block.5, %after_if.4.3
  %181 = phi float [ %.pre51, %true_block.5 ], [ %179, %after_if.4.3 ]
  %182 = load float, float* %40, align 4
  %183 = fcmp reassoc ninf nsz ogt float %181, %182
  br i1 %183, label %true_block.5.1, label %after_if.5.1

true_block.5.1:                                   ; preds = %after_if.5
  store float %182, float* %37, align 4
  store float %181, float* %40, align 4
  br label %after_if.5.1

after_if.5.1:                                     ; preds = %true_block.5.1, %after_if.5
  %184 = phi float [ %181, %true_block.5.1 ], [ %182, %after_if.5 ]
  %185 = load float, float* %41, align 4
  %186 = fcmp reassoc ninf nsz ogt float %184, %185
  br i1 %186, label %true_block.5.2, label %after_if.5.2

true_block.5.2:                                   ; preds = %after_if.5.1
  store float %185, float* %40, align 4
  store float %184, float* %41, align 4
  br label %after_if.5.2

after_if.5.2:                                     ; preds = %true_block.5.2, %after_if.5.1
  %.pre52 = load float, float* %30, align 4
  %187 = load float, float* %37, align 4
  %188 = fcmp reassoc ninf nsz ogt float %.pre52, %187
  br i1 %188, label %true_block.6, label %after_if.6

true_block.6:                                     ; preds = %after_if.5.2
  store float %187, float* %30, align 4
  store float %.pre52, float* %37, align 4
  br label %after_if.6

after_if.6:                                       ; preds = %true_block.6, %after_if.5.2
  %189 = phi float [ %.pre52, %true_block.6 ], [ %187, %after_if.5.2 ]
  %190 = load float, float* %40, align 4
  %191 = fcmp reassoc ninf nsz ogt float %189, %190
  br i1 %191, label %true_block.6.1, label %after_if.6.1

true_block.6.1:                                   ; preds = %after_if.6
  store float %190, float* %37, align 4
  store float %189, float* %40, align 4
  br label %after_if.6.1

after_if.6.1:                                     ; preds = %true_block.6.1, %after_if.6
  %.pre53 = load float, float* %30, align 4
  %192 = load float, float* %37, align 4
  %193 = fcmp reassoc ninf nsz ogt float %.pre53, %192
  br i1 %193, label %true_block.7, label %for_loop_body13.preheader

true_block.7:                                     ; preds = %after_if.6.1
  store float %192, float* %30, align 4
  store float %.pre53, float* %37, align 4
  br label %for_loop_body13.preheader

true_block:                                       ; preds = %for_loop_body5.preheader
  store float %117, float* %30, align 4
  store float %116, float* %37, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body5.preheader
  %194 = phi float [ %117, %for_loop_body5.preheader ], [ %116, %true_block ]
  %195 = load float, float* %40, align 4
  %196 = fcmp reassoc ninf nsz ogt float %194, %195
  br i1 %196, label %true_block.171, label %after_if.172

true_block.171:                                   ; preds = %after_if
  store float %195, float* %37, align 4
  store float %194, float* %40, align 4
  br label %after_if.172

after_if.172:                                     ; preds = %true_block.171, %after_if
  %197 = phi float [ %195, %after_if ], [ %194, %true_block.171 ]
  %198 = load float, float* %41, align 4
  %199 = fcmp reassoc ninf nsz ogt float %197, %198
  br i1 %199, label %true_block.276, label %after_if.277

true_block.276:                                   ; preds = %after_if.172
  store float %198, float* %40, align 4
  store float %197, float* %41, align 4
  br label %after_if.277

after_if.277:                                     ; preds = %true_block.276, %after_if.172
  %200 = phi float [ %198, %after_if.172 ], [ %197, %true_block.276 ]
  %201 = load float, float* %29, align 4
  %202 = fcmp reassoc ninf nsz ogt float %200, %201
  br i1 %202, label %true_block.381, label %after_if.382

true_block.381:                                   ; preds = %after_if.277
  store float %201, float* %41, align 4
  store float %200, float* %29, align 4
  br label %after_if.382

after_if.382:                                     ; preds = %true_block.381, %after_if.277
  %203 = phi float [ %201, %after_if.277 ], [ %200, %true_block.381 ]
  %204 = load float, float* %42, align 4
  %205 = fcmp reassoc ninf nsz ogt float %203, %204
  br i1 %205, label %true_block.486, label %after_if.487

true_block.486:                                   ; preds = %after_if.382
  store float %204, float* %29, align 4
  store float %203, float* %42, align 4
  br label %after_if.487

after_if.487:                                     ; preds = %true_block.486, %after_if.382
  %206 = phi float [ %204, %after_if.382 ], [ %203, %true_block.486 ]
  %207 = load float, float* %43, align 4
  %208 = fcmp reassoc ninf nsz ogt float %206, %207
  br i1 %208, label %true_block.591, label %after_if.592

true_block.591:                                   ; preds = %after_if.487
  store float %207, float* %42, align 4
  store float %206, float* %43, align 4
  br label %after_if.592

after_if.592:                                     ; preds = %true_block.591, %after_if.487
  %209 = phi float [ %207, %after_if.487 ], [ %206, %true_block.591 ]
  %210 = load float, float* %44, align 4
  %211 = fcmp reassoc ninf nsz ogt float %209, %210
  br i1 %211, label %true_block.696, label %after_if.697

true_block.696:                                   ; preds = %after_if.592
  store float %210, float* %43, align 4
  store float %209, float* %44, align 4
  br label %after_if.697

after_if.697:                                     ; preds = %true_block.696, %after_if.592
  %212 = phi float [ %210, %after_if.592 ], [ %209, %true_block.696 ]
  %213 = fcmp reassoc ninf nsz ogt float %212, %115
  br i1 %213, label %true_block.799, label %after_if.7

true_block.799:                                   ; preds = %after_if.697
  store float %115, float* %44, align 4
  store float %212, float* %28, align 4
  br label %after_if.7

after_if.7:                                       ; preds = %true_block.799, %after_if.697
  %.pre = load float, float* %30, align 4
  %214 = load float, float* %37, align 4
  %215 = fcmp reassoc ninf nsz ogt float %.pre, %214
  br i1 %215, label %true_block.1, label %after_if.1

for_loop_body13.preheader:                        ; preds = %true_block.7, %after_if.6.1
  %216 = load float, float* %29, align 4
  %217 = load float*, float** %31, align 8
  %218 = load i32, i32* %32, align 4
  %219 = load i32, i32* %33, align 4
  %220 = mul i32 %218, %65
  %221 = add i32 %220, %93
  %222 = mul i32 %221, %219
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, float* %217, i64 %223
  store float %216, float* %224, align 4
  %225 = load float*, float** %25, align 8
  %226 = load i32, i32* %26, align 4
  %227 = load i32, i32* %27, align 4
  %228 = mul i32 %226, %73
  %229 = mul i32 %226, %65
  %230 = mul i32 %226, %83
  %231 = add i32 %230, %99
  %232 = mul i32 %231, %227
  %233 = add i32 %232, 1
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, float* %225, i64 %234
  %236 = load float, float* %235, align 4
  %237 = insertelement <8 x i32> poison, i32 %228, i64 0
  %238 = insertelement <8 x i32> %237, i32 %229, i64 1
  %239 = insertelement <8 x i32> %238, i32 %230, i64 2
  %shuffle61 = shufflevector <8 x i32> %239, <8 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 2, i32 2>
  %240 = shufflevector <8 x i32> %100, <8 x i32> %92, <8 x i32> <i32 0, i32 12, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %241 = insertelement <8 x i32> %240, i32 %99, i64 2
  %shuffle62 = shufflevector <8 x i32> %241, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 1, i32 2, i32 0, i32 1>
  %242 = add <8 x i32> %shuffle61, %shuffle62
  %243 = insertelement <8 x i32> poison, i32 %227, i64 0
  %shuffle63 = shufflevector <8 x i32> %243, <8 x i32> poison, <8 x i32> zeroinitializer
  %244 = mul <8 x i32> %242, %shuffle63
  %245 = add <8 x i32> %244, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %246 = sext <8 x i32> %245 to <8 x i64>
  %247 = insertelement <8 x float*> poison, float* %225, i64 0
  %shuffle = shufflevector <8 x float*> %247, <8 x float*> poison, <8 x i32> zeroinitializer
  %248 = getelementptr float, <8 x float*> %shuffle, <8 x i64> %246
  %249 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %248, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  store <8 x float> %249, <8 x float>* %45, align 4
  store float %236, float* %34, align 4
  %250 = extractelement <8 x float> %249, i64 0
  %251 = load float, float* %38, align 4
  %252 = fcmp reassoc ninf nsz ogt float %250, %251
  br i1 %252, label %true_block17, label %after_if19

true_block17.1:                                   ; preds = %after_if19.7
  store float %359, float* %36, align 4
  store float %.pre54, float* %38, align 4
  br label %after_if19.1

after_if19.1:                                     ; preds = %after_if19.7, %true_block17.1
  %253 = phi float [ %.pre54, %true_block17.1 ], [ %359, %after_if19.7 ]
  %254 = load float, float* %46, align 4
  %255 = fcmp reassoc ninf nsz ogt float %253, %254
  br i1 %255, label %true_block17.1.1, label %after_if19.1.1

true_block17.1.1:                                 ; preds = %after_if19.1
  store float %254, float* %38, align 4
  store float %253, float* %46, align 4
  br label %after_if19.1.1

after_if19.1.1:                                   ; preds = %true_block17.1.1, %after_if19.1
  %256 = phi float [ %253, %true_block17.1.1 ], [ %254, %after_if19.1 ]
  %257 = load float, float* %47, align 4
  %258 = fcmp reassoc ninf nsz ogt float %256, %257
  br i1 %258, label %true_block17.1.2, label %after_if19.1.2

true_block17.1.2:                                 ; preds = %after_if19.1.1
  store float %257, float* %46, align 4
  store float %256, float* %47, align 4
  br label %after_if19.1.2

after_if19.1.2:                                   ; preds = %true_block17.1.2, %after_if19.1.1
  %259 = phi float [ %256, %true_block17.1.2 ], [ %257, %after_if19.1.1 ]
  %260 = load float, float* %35, align 4
  %261 = fcmp reassoc ninf nsz ogt float %259, %260
  br i1 %261, label %true_block17.1.3, label %after_if19.1.3

true_block17.1.3:                                 ; preds = %after_if19.1.2
  store float %260, float* %47, align 4
  store float %259, float* %35, align 4
  br label %after_if19.1.3

after_if19.1.3:                                   ; preds = %true_block17.1.3, %after_if19.1.2
  %262 = phi float [ %259, %true_block17.1.3 ], [ %260, %after_if19.1.2 ]
  %263 = load float, float* %48, align 4
  %264 = fcmp reassoc ninf nsz ogt float %262, %263
  br i1 %264, label %true_block17.1.4, label %after_if19.1.4

true_block17.1.4:                                 ; preds = %after_if19.1.3
  store float %263, float* %35, align 4
  store float %262, float* %48, align 4
  br label %after_if19.1.4

after_if19.1.4:                                   ; preds = %true_block17.1.4, %after_if19.1.3
  %265 = phi float [ %262, %true_block17.1.4 ], [ %263, %after_if19.1.3 ]
  %266 = load float, float* %49, align 4
  %267 = fcmp reassoc ninf nsz ogt float %265, %266
  br i1 %267, label %true_block17.1.5, label %after_if19.1.5

true_block17.1.5:                                 ; preds = %after_if19.1.4
  store float %266, float* %48, align 4
  store float %265, float* %49, align 4
  br label %after_if19.1.5

after_if19.1.5:                                   ; preds = %true_block17.1.5, %after_if19.1.4
  %268 = phi float [ %265, %true_block17.1.5 ], [ %266, %after_if19.1.4 ]
  %269 = load float, float* %50, align 4
  %270 = fcmp reassoc ninf nsz ogt float %268, %269
  br i1 %270, label %true_block17.1.6, label %after_if19.1.6

true_block17.1.6:                                 ; preds = %after_if19.1.5
  store float %269, float* %49, align 4
  store float %268, float* %50, align 4
  br label %after_if19.1.6

after_if19.1.6:                                   ; preds = %true_block17.1.6, %after_if19.1.5
  %.pre55 = load float, float* %36, align 4
  %271 = load float, float* %38, align 4
  %272 = fcmp reassoc ninf nsz ogt float %.pre55, %271
  br i1 %272, label %true_block17.2, label %after_if19.2

true_block17.2:                                   ; preds = %after_if19.1.6
  store float %271, float* %36, align 4
  store float %.pre55, float* %38, align 4
  br label %after_if19.2

after_if19.2:                                     ; preds = %true_block17.2, %after_if19.1.6
  %273 = phi float [ %.pre55, %true_block17.2 ], [ %271, %after_if19.1.6 ]
  %274 = load float, float* %46, align 4
  %275 = fcmp reassoc ninf nsz ogt float %273, %274
  br i1 %275, label %true_block17.2.1, label %after_if19.2.1

true_block17.2.1:                                 ; preds = %after_if19.2
  store float %274, float* %38, align 4
  store float %273, float* %46, align 4
  br label %after_if19.2.1

after_if19.2.1:                                   ; preds = %true_block17.2.1, %after_if19.2
  %276 = phi float [ %273, %true_block17.2.1 ], [ %274, %after_if19.2 ]
  %277 = load float, float* %47, align 4
  %278 = fcmp reassoc ninf nsz ogt float %276, %277
  br i1 %278, label %true_block17.2.2, label %after_if19.2.2

true_block17.2.2:                                 ; preds = %after_if19.2.1
  store float %277, float* %46, align 4
  store float %276, float* %47, align 4
  br label %after_if19.2.2

after_if19.2.2:                                   ; preds = %true_block17.2.2, %after_if19.2.1
  %279 = phi float [ %276, %true_block17.2.2 ], [ %277, %after_if19.2.1 ]
  %280 = load float, float* %35, align 4
  %281 = fcmp reassoc ninf nsz ogt float %279, %280
  br i1 %281, label %true_block17.2.3, label %after_if19.2.3

true_block17.2.3:                                 ; preds = %after_if19.2.2
  store float %280, float* %47, align 4
  store float %279, float* %35, align 4
  br label %after_if19.2.3

after_if19.2.3:                                   ; preds = %true_block17.2.3, %after_if19.2.2
  %282 = phi float [ %279, %true_block17.2.3 ], [ %280, %after_if19.2.2 ]
  %283 = load float, float* %48, align 4
  %284 = fcmp reassoc ninf nsz ogt float %282, %283
  br i1 %284, label %true_block17.2.4, label %after_if19.2.4

true_block17.2.4:                                 ; preds = %after_if19.2.3
  store float %283, float* %35, align 4
  store float %282, float* %48, align 4
  br label %after_if19.2.4

after_if19.2.4:                                   ; preds = %true_block17.2.4, %after_if19.2.3
  %285 = phi float [ %282, %true_block17.2.4 ], [ %283, %after_if19.2.3 ]
  %286 = load float, float* %49, align 4
  %287 = fcmp reassoc ninf nsz ogt float %285, %286
  br i1 %287, label %true_block17.2.5, label %after_if19.2.5

true_block17.2.5:                                 ; preds = %after_if19.2.4
  store float %286, float* %48, align 4
  store float %285, float* %49, align 4
  br label %after_if19.2.5

after_if19.2.5:                                   ; preds = %true_block17.2.5, %after_if19.2.4
  %.pre56 = load float, float* %36, align 4
  %288 = load float, float* %38, align 4
  %289 = fcmp reassoc ninf nsz ogt float %.pre56, %288
  br i1 %289, label %true_block17.3, label %after_if19.3

true_block17.3:                                   ; preds = %after_if19.2.5
  store float %288, float* %36, align 4
  store float %.pre56, float* %38, align 4
  br label %after_if19.3

after_if19.3:                                     ; preds = %true_block17.3, %after_if19.2.5
  %290 = phi float [ %.pre56, %true_block17.3 ], [ %288, %after_if19.2.5 ]
  %291 = load float, float* %46, align 4
  %292 = fcmp reassoc ninf nsz ogt float %290, %291
  br i1 %292, label %true_block17.3.1, label %after_if19.3.1

true_block17.3.1:                                 ; preds = %after_if19.3
  store float %291, float* %38, align 4
  store float %290, float* %46, align 4
  br label %after_if19.3.1

after_if19.3.1:                                   ; preds = %true_block17.3.1, %after_if19.3
  %293 = phi float [ %290, %true_block17.3.1 ], [ %291, %after_if19.3 ]
  %294 = load float, float* %47, align 4
  %295 = fcmp reassoc ninf nsz ogt float %293, %294
  br i1 %295, label %true_block17.3.2, label %after_if19.3.2

true_block17.3.2:                                 ; preds = %after_if19.3.1
  store float %294, float* %46, align 4
  store float %293, float* %47, align 4
  br label %after_if19.3.2

after_if19.3.2:                                   ; preds = %true_block17.3.2, %after_if19.3.1
  %296 = phi float [ %293, %true_block17.3.2 ], [ %294, %after_if19.3.1 ]
  %297 = load float, float* %35, align 4
  %298 = fcmp reassoc ninf nsz ogt float %296, %297
  br i1 %298, label %true_block17.3.3, label %after_if19.3.3

true_block17.3.3:                                 ; preds = %after_if19.3.2
  store float %297, float* %47, align 4
  store float %296, float* %35, align 4
  br label %after_if19.3.3

after_if19.3.3:                                   ; preds = %true_block17.3.3, %after_if19.3.2
  %299 = phi float [ %296, %true_block17.3.3 ], [ %297, %after_if19.3.2 ]
  %300 = load float, float* %48, align 4
  %301 = fcmp reassoc ninf nsz ogt float %299, %300
  br i1 %301, label %true_block17.3.4, label %after_if19.3.4

true_block17.3.4:                                 ; preds = %after_if19.3.3
  store float %300, float* %35, align 4
  store float %299, float* %48, align 4
  br label %after_if19.3.4

after_if19.3.4:                                   ; preds = %true_block17.3.4, %after_if19.3.3
  %.pre57 = load float, float* %36, align 4
  %302 = load float, float* %38, align 4
  %303 = fcmp reassoc ninf nsz ogt float %.pre57, %302
  br i1 %303, label %true_block17.4, label %after_if19.4

true_block17.4:                                   ; preds = %after_if19.3.4
  store float %302, float* %36, align 4
  store float %.pre57, float* %38, align 4
  br label %after_if19.4

after_if19.4:                                     ; preds = %true_block17.4, %after_if19.3.4
  %304 = phi float [ %.pre57, %true_block17.4 ], [ %302, %after_if19.3.4 ]
  %305 = load float, float* %46, align 4
  %306 = fcmp reassoc ninf nsz ogt float %304, %305
  br i1 %306, label %true_block17.4.1, label %after_if19.4.1

true_block17.4.1:                                 ; preds = %after_if19.4
  store float %305, float* %38, align 4
  store float %304, float* %46, align 4
  br label %after_if19.4.1

after_if19.4.1:                                   ; preds = %true_block17.4.1, %after_if19.4
  %307 = phi float [ %304, %true_block17.4.1 ], [ %305, %after_if19.4 ]
  %308 = load float, float* %47, align 4
  %309 = fcmp reassoc ninf nsz ogt float %307, %308
  br i1 %309, label %true_block17.4.2, label %after_if19.4.2

true_block17.4.2:                                 ; preds = %after_if19.4.1
  store float %308, float* %46, align 4
  store float %307, float* %47, align 4
  br label %after_if19.4.2

after_if19.4.2:                                   ; preds = %true_block17.4.2, %after_if19.4.1
  %310 = phi float [ %307, %true_block17.4.2 ], [ %308, %after_if19.4.1 ]
  %311 = load float, float* %35, align 4
  %312 = fcmp reassoc ninf nsz ogt float %310, %311
  br i1 %312, label %true_block17.4.3, label %after_if19.4.3

true_block17.4.3:                                 ; preds = %after_if19.4.2
  store float %311, float* %47, align 4
  store float %310, float* %35, align 4
  br label %after_if19.4.3

after_if19.4.3:                                   ; preds = %true_block17.4.3, %after_if19.4.2
  %.pre58 = load float, float* %36, align 4
  %313 = load float, float* %38, align 4
  %314 = fcmp reassoc ninf nsz ogt float %.pre58, %313
  br i1 %314, label %true_block17.5, label %after_if19.5

true_block17.5:                                   ; preds = %after_if19.4.3
  store float %313, float* %36, align 4
  store float %.pre58, float* %38, align 4
  br label %after_if19.5

after_if19.5:                                     ; preds = %true_block17.5, %after_if19.4.3
  %315 = phi float [ %.pre58, %true_block17.5 ], [ %313, %after_if19.4.3 ]
  %316 = load float, float* %46, align 4
  %317 = fcmp reassoc ninf nsz ogt float %315, %316
  br i1 %317, label %true_block17.5.1, label %after_if19.5.1

true_block17.5.1:                                 ; preds = %after_if19.5
  store float %316, float* %38, align 4
  store float %315, float* %46, align 4
  br label %after_if19.5.1

after_if19.5.1:                                   ; preds = %true_block17.5.1, %after_if19.5
  %318 = phi float [ %315, %true_block17.5.1 ], [ %316, %after_if19.5 ]
  %319 = load float, float* %47, align 4
  %320 = fcmp reassoc ninf nsz ogt float %318, %319
  br i1 %320, label %true_block17.5.2, label %after_if19.5.2

true_block17.5.2:                                 ; preds = %after_if19.5.1
  store float %319, float* %46, align 4
  store float %318, float* %47, align 4
  br label %after_if19.5.2

after_if19.5.2:                                   ; preds = %true_block17.5.2, %after_if19.5.1
  %.pre59 = load float, float* %36, align 4
  %321 = load float, float* %38, align 4
  %322 = fcmp reassoc ninf nsz ogt float %.pre59, %321
  br i1 %322, label %true_block17.6, label %after_if19.6

true_block17.6:                                   ; preds = %after_if19.5.2
  store float %321, float* %36, align 4
  store float %.pre59, float* %38, align 4
  br label %after_if19.6

after_if19.6:                                     ; preds = %true_block17.6, %after_if19.5.2
  %323 = phi float [ %.pre59, %true_block17.6 ], [ %321, %after_if19.5.2 ]
  %324 = load float, float* %46, align 4
  %325 = fcmp reassoc ninf nsz ogt float %323, %324
  br i1 %325, label %true_block17.6.1, label %after_if19.6.1

true_block17.6.1:                                 ; preds = %after_if19.6
  store float %324, float* %38, align 4
  store float %323, float* %46, align 4
  br label %after_if19.6.1

after_if19.6.1:                                   ; preds = %true_block17.6.1, %after_if19.6
  %.pre60 = load float, float* %36, align 4
  %326 = load float, float* %38, align 4
  %327 = fcmp reassoc ninf nsz ogt float %.pre60, %326
  br i1 %327, label %true_block17.7, label %after_for15.7

true_block17.7:                                   ; preds = %after_if19.6.1
  store float %326, float* %36, align 4
  store float %.pre60, float* %38, align 4
  br label %after_for15.7

after_for15.7:                                    ; preds = %true_block17.7, %after_if19.6.1
  %328 = load float, float* %35, align 4
  %329 = load float*, float** %31, align 8
  %330 = load i32, i32* %32, align 4
  %331 = load i32, i32* %33, align 4
  %332 = mul i32 %330, %65
  %333 = add i32 %332, %93
  %334 = mul i32 %333, %331
  %335 = add i32 %334, 1
  %336 = sext i32 %335 to i64
  %337 = getelementptr float, float* %329, i64 %336
  store float %328, float* %337, align 4
  %338 = add nsw i32 %.01929, 1
  %exitcond47.not = icmp eq i32 %21, %338
  br i1 %exitcond47.not, label %after_for.loopexit, label %for_loop_body5.preheader

true_block17:                                     ; preds = %for_loop_body13.preheader
  store float %251, float* %36, align 4
  store float %250, float* %38, align 4
  br label %after_if19

after_if19:                                       ; preds = %true_block17, %for_loop_body13.preheader
  %339 = phi float [ %251, %for_loop_body13.preheader ], [ %250, %true_block17 ]
  %340 = load float, float* %46, align 4
  %341 = fcmp reassoc ninf nsz ogt float %339, %340
  br i1 %341, label %true_block17.1103, label %after_if19.1104

true_block17.1103:                                ; preds = %after_if19
  store float %340, float* %38, align 4
  store float %339, float* %46, align 4
  br label %after_if19.1104

after_if19.1104:                                  ; preds = %true_block17.1103, %after_if19
  %342 = phi float [ %340, %after_if19 ], [ %339, %true_block17.1103 ]
  %343 = load float, float* %47, align 4
  %344 = fcmp reassoc ninf nsz ogt float %342, %343
  br i1 %344, label %true_block17.2108, label %after_if19.2109

true_block17.2108:                                ; preds = %after_if19.1104
  store float %343, float* %46, align 4
  store float %342, float* %47, align 4
  br label %after_if19.2109

after_if19.2109:                                  ; preds = %true_block17.2108, %after_if19.1104
  %345 = phi float [ %343, %after_if19.1104 ], [ %342, %true_block17.2108 ]
  %346 = load float, float* %35, align 4
  %347 = fcmp reassoc ninf nsz ogt float %345, %346
  br i1 %347, label %true_block17.3113, label %after_if19.3114

true_block17.3113:                                ; preds = %after_if19.2109
  store float %346, float* %47, align 4
  store float %345, float* %35, align 4
  br label %after_if19.3114

after_if19.3114:                                  ; preds = %true_block17.3113, %after_if19.2109
  %348 = phi float [ %346, %after_if19.2109 ], [ %345, %true_block17.3113 ]
  %349 = load float, float* %48, align 4
  %350 = fcmp reassoc ninf nsz ogt float %348, %349
  br i1 %350, label %true_block17.4118, label %after_if19.4119

true_block17.4118:                                ; preds = %after_if19.3114
  store float %349, float* %35, align 4
  store float %348, float* %48, align 4
  br label %after_if19.4119

after_if19.4119:                                  ; preds = %true_block17.4118, %after_if19.3114
  %351 = phi float [ %349, %after_if19.3114 ], [ %348, %true_block17.4118 ]
  %352 = load float, float* %49, align 4
  %353 = fcmp reassoc ninf nsz ogt float %351, %352
  br i1 %353, label %true_block17.5123, label %after_if19.5124

true_block17.5123:                                ; preds = %after_if19.4119
  store float %352, float* %48, align 4
  store float %351, float* %49, align 4
  br label %after_if19.5124

after_if19.5124:                                  ; preds = %true_block17.5123, %after_if19.4119
  %354 = phi float [ %352, %after_if19.4119 ], [ %351, %true_block17.5123 ]
  %355 = load float, float* %50, align 4
  %356 = fcmp reassoc ninf nsz ogt float %354, %355
  br i1 %356, label %true_block17.6128, label %after_if19.6129

true_block17.6128:                                ; preds = %after_if19.5124
  store float %355, float* %49, align 4
  store float %354, float* %50, align 4
  br label %after_if19.6129

after_if19.6129:                                  ; preds = %true_block17.6128, %after_if19.5124
  %357 = phi float [ %355, %after_if19.5124 ], [ %354, %true_block17.6128 ]
  %358 = fcmp reassoc ninf nsz ogt float %357, %236
  br i1 %358, label %true_block17.7131, label %after_if19.7

true_block17.7131:                                ; preds = %after_if19.6129
  store float %236, float* %50, align 4
  store float %357, float* %34, align 4
  br label %after_if19.7

after_if19.7:                                     ; preds = %true_block17.7131, %after_if19.6129
  %.pre54 = load float, float* %36, align 4
  %359 = load float, float* %38, align 4
  %360 = fcmp reassoc ninf nsz ogt float %.pre54, %359
  br i1 %360, label %true_block17.1, label %after_if19.1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.96* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

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

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }

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
