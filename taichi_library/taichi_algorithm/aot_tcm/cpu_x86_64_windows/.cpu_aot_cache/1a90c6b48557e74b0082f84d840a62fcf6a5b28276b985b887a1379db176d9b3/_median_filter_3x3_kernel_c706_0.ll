; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.48*, void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.48 = type { i8*, %struct.LLVMRuntime.47*, i32, i64* }
%struct.LLVMRuntime.47 = type { %struct.PreallocatedMemoryChunk.43, %struct.PreallocatedMemoryChunk.43, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.44*], [1024 x %struct.NodeManager.45*], [1024 x i8*], i8*, %struct.RandState.46*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.43 = type { i8*, i8*, i64 }
%struct.ListManager.44 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.47* }
%struct.NodeManager.45 = type { %struct.LLVMRuntime.47*, i32, i32, i32, i32, %struct.ListManager.44*, %struct.ListManager.44*, %struct.ListManager.44*, i32 }
%struct.RandState.46 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_median_filter_3x3_kernel_c706_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_median_filter_3x3_kernel_c706_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.48* %context, %struct.RuntimeContext.48** %4, align 8
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.48*, i8*, i32)* @function_body, void (%struct.RuntimeContext.48*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.48* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = alloca [9 x float], align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %0, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  %9 = load i32, i32* %8, align 4
  %10 = add i32 %9, 7
  %11 = sdiv i32 %10, 8
  %12 = icmp slt i32 %10, 0
  %13 = shl nsw i32 %11, 3
  %14 = icmp ne i32 %13, %10
  %15 = and i1 %12, %14
  %.neg = sext i1 %15 to i32
  %16 = add nsw i32 %11, %.neg
  %17 = tail call i32 @llvm.smax.i32(i32 %16, i32 512)
  %18 = mul i32 %17, %2
  %19 = add i32 %18, %17
  %20 = tail call i32 @llvm.smin.i32(i32 %9, i32 %19)
  %21 = icmp slt i32 %18, %20
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %23 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %22, align 8
  %24 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 8
  %25 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 7
  %26 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 6
  %27 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 5
  %28 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 4
  %29 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 3
  %30 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 2
  %31 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 1
  %32 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 0
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %23, i64 0, i32 0, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %23, i64 0, i32 0, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %23, i64 0, i32 1, i32 1
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %23, i64 0, i32 1, i32 0, i32 1
  %37 = bitcast [9 x float]* %3 to <8 x float>*
  br label %for_loop_body5.lr.ph

after_for.loopexit:                               ; preds = %for_loop_test4.loopexit.8
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body5.lr.ph:                             ; preds = %for_loop_test4.loopexit.8, %for_loop_body.lr.ph
  %.01117 = phi i32 [ %18, %for_loop_body.lr.ph ], [ %198, %for_loop_test4.loopexit.8 ]
  %38 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  %43 = load i32, i32* %42, align 4
  %44 = sdiv i32 %.01117, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.01117
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %.01117, 0
  %49 = icmp ne i32 %.01117, %45
  %50 = and i1 %48, %47
  %51 = and i1 %50, %49
  %.neg14 = sext i1 %51 to i32
  %52 = getelementptr inbounds i8, i8* %40, i64 8
  %53 = bitcast i8* %52 to i32*
  %54 = load i32, i32* %53, align 4
  %55 = add i32 %54, -1
  %56 = getelementptr inbounds i8, i8* %40, i64 12
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = add i32 %58, -1
  %60 = load float*, float** %33, align 8
  %61 = load i32, i32* %34, align 4
  %62 = insertelement <2 x i32> poison, i32 %59, i64 0
  %63 = shufflevector <2 x i32> %62, <2 x i32> poison, <2 x i32> zeroinitializer
  %64 = add i32 %44, %.neg14
  %65 = mul i32 %43, -1
  %66 = mul i32 %65, %64
  %67 = add i32 %.01117, %66
  %68 = add i32 %64, -1
  %69 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %70 = tail call i32 @llvm.smin.i32(i32 %55, i32 %69)
  %71 = add i32 %67, -1
  %72 = tail call i32 @llvm.smax.i32(i32 %71, i32 0)
  %73 = tail call i32 @llvm.smin.i32(i32 %59, i32 %72)
  %74 = mul i32 %70, %61
  %75 = add i32 %67, 1
  %76 = insertelement <2 x i32> poison, i32 %67, i64 0
  %77 = insertelement <2 x i32> %76, i32 %75, i64 1
  %78 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %77, <2 x i32> zeroinitializer)
  %79 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %63, <2 x i32> %78)
  %80 = add i32 %64, 1
  %81 = insertelement <2 x i32> poison, i32 %64, i64 0
  %82 = insertelement <2 x i32> %81, i32 %80, i64 1
  %83 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %82, <2 x i32> zeroinitializer)
  %84 = insertelement <2 x i32> poison, i32 %55, i64 0
  %85 = shufflevector <2 x i32> %84, <2 x i32> poison, <2 x i32> zeroinitializer
  %86 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %85, <2 x i32> %83)
  %87 = insertelement <2 x i32> poison, i32 %61, i64 0
  %88 = shufflevector <2 x i32> %87, <2 x i32> poison, <2 x i32> zeroinitializer
  %89 = mul <2 x i32> %86, %88
  %90 = insertelement <8 x i32> poison, i32 %74, i64 0
  %91 = shufflevector <2 x i32> %89, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %92 = shufflevector <8 x i32> %90, <8 x i32> %91, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle26 = shufflevector <8 x i32> %92, <8 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 2, i32 2>
  %93 = insertelement <8 x i32> poison, i32 %73, i64 0
  %94 = shufflevector <2 x i32> %79, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %95 = shufflevector <8 x i32> %93, <8 x i32> %94, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle27 = shufflevector <8 x i32> %95, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 1, i32 2, i32 0, i32 1>
  %96 = add <8 x i32> %shuffle26, %shuffle27
  %97 = sext <8 x i32> %96 to <8 x i64>
  %98 = insertelement <8 x float*> poison, float* %60, i64 0
  %shuffle = shufflevector <8 x float*> %98, <8 x float*> poison, <8 x i32> zeroinitializer
  %99 = getelementptr float, <8 x float*> %shuffle, <8 x i64> %97
  %100 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %99, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  store <8 x float> %100, <8 x float>* %37, align 4
  %101 = add <2 x i32> %79, %89
  %102 = extractelement <2 x i32> %101, i64 1
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %60, i64 %103
  %105 = load float, float* %104, align 4
  store float %105, float* %24, align 4
  %106 = load float, float* %31, align 4
  %107 = load float, float* %32, align 4
  %108 = fcmp reassoc ninf nsz olt float %106, %107
  br i1 %108, label %true_block, label %after_if

true_block.1:                                     ; preds = %after_if.7
  store float %219, float* %31, align 4
  store float %220, float* %30, align 4
  br label %after_if.1

after_if.1:                                       ; preds = %after_if.7, %true_block.1
  %109 = load float, float* %29, align 4
  %110 = load float, float* %31, align 4
  %111 = fcmp reassoc ninf nsz olt float %109, %110
  br i1 %111, label %true_block.1.1, label %after_if.1.1

true_block.1.1:                                   ; preds = %after_if.1
  store float %109, float* %31, align 4
  store float %110, float* %29, align 4
  br label %after_if.1.1

after_if.1.1:                                     ; preds = %true_block.1.1, %after_if.1
  %112 = load float, float* %28, align 4
  %113 = load float, float* %31, align 4
  %114 = fcmp reassoc ninf nsz olt float %112, %113
  br i1 %114, label %true_block.1.2, label %after_if.1.2

true_block.1.2:                                   ; preds = %after_if.1.1
  store float %112, float* %31, align 4
  store float %113, float* %28, align 4
  br label %after_if.1.2

after_if.1.2:                                     ; preds = %true_block.1.2, %after_if.1.1
  %115 = load float, float* %27, align 4
  %116 = load float, float* %31, align 4
  %117 = fcmp reassoc ninf nsz olt float %115, %116
  br i1 %117, label %true_block.1.3, label %after_if.1.3

true_block.1.3:                                   ; preds = %after_if.1.2
  store float %115, float* %31, align 4
  store float %116, float* %27, align 4
  br label %after_if.1.3

after_if.1.3:                                     ; preds = %true_block.1.3, %after_if.1.2
  %118 = load float, float* %26, align 4
  %119 = load float, float* %31, align 4
  %120 = fcmp reassoc ninf nsz olt float %118, %119
  br i1 %120, label %true_block.1.4, label %after_if.1.4

true_block.1.4:                                   ; preds = %after_if.1.3
  store float %118, float* %31, align 4
  store float %119, float* %26, align 4
  br label %after_if.1.4

after_if.1.4:                                     ; preds = %true_block.1.4, %after_if.1.3
  %121 = load float, float* %25, align 4
  %122 = load float, float* %31, align 4
  %123 = fcmp reassoc ninf nsz olt float %121, %122
  br i1 %123, label %true_block.1.5, label %after_if.1.5

true_block.1.5:                                   ; preds = %after_if.1.4
  store float %121, float* %31, align 4
  store float %122, float* %25, align 4
  br label %after_if.1.5

after_if.1.5:                                     ; preds = %true_block.1.5, %after_if.1.4
  %124 = load float, float* %24, align 4
  %125 = load float, float* %31, align 4
  %126 = fcmp reassoc ninf nsz olt float %124, %125
  br i1 %126, label %true_block.1.6, label %for_loop_body5.2

true_block.1.6:                                   ; preds = %after_if.1.5
  store float %124, float* %31, align 4
  store float %125, float* %24, align 4
  br label %for_loop_body5.2

for_loop_body5.2:                                 ; preds = %true_block.1.6, %after_if.1.5
  %127 = load float, float* %29, align 4
  %128 = load float, float* %30, align 4
  %129 = fcmp reassoc ninf nsz olt float %127, %128
  br i1 %129, label %true_block.2, label %after_if.2

true_block.2:                                     ; preds = %for_loop_body5.2
  store float %127, float* %30, align 4
  store float %128, float* %29, align 4
  br label %after_if.2

after_if.2:                                       ; preds = %true_block.2, %for_loop_body5.2
  %130 = load float, float* %28, align 4
  %131 = load float, float* %30, align 4
  %132 = fcmp reassoc ninf nsz olt float %130, %131
  br i1 %132, label %true_block.2.1, label %after_if.2.1

true_block.2.1:                                   ; preds = %after_if.2
  store float %130, float* %30, align 4
  store float %131, float* %28, align 4
  br label %after_if.2.1

after_if.2.1:                                     ; preds = %true_block.2.1, %after_if.2
  %133 = load float, float* %27, align 4
  %134 = load float, float* %30, align 4
  %135 = fcmp reassoc ninf nsz olt float %133, %134
  br i1 %135, label %true_block.2.2, label %after_if.2.2

true_block.2.2:                                   ; preds = %after_if.2.1
  store float %133, float* %30, align 4
  store float %134, float* %27, align 4
  br label %after_if.2.2

after_if.2.2:                                     ; preds = %true_block.2.2, %after_if.2.1
  %136 = load float, float* %26, align 4
  %137 = load float, float* %30, align 4
  %138 = fcmp reassoc ninf nsz olt float %136, %137
  br i1 %138, label %true_block.2.3, label %after_if.2.3

true_block.2.3:                                   ; preds = %after_if.2.2
  store float %136, float* %30, align 4
  store float %137, float* %26, align 4
  br label %after_if.2.3

after_if.2.3:                                     ; preds = %true_block.2.3, %after_if.2.2
  %139 = load float, float* %25, align 4
  %140 = load float, float* %30, align 4
  %141 = fcmp reassoc ninf nsz olt float %139, %140
  br i1 %141, label %true_block.2.4, label %after_if.2.4

true_block.2.4:                                   ; preds = %after_if.2.3
  store float %139, float* %30, align 4
  store float %140, float* %25, align 4
  br label %after_if.2.4

after_if.2.4:                                     ; preds = %true_block.2.4, %after_if.2.3
  %142 = load float, float* %24, align 4
  %143 = load float, float* %30, align 4
  %144 = fcmp reassoc ninf nsz olt float %142, %143
  br i1 %144, label %true_block.2.5, label %for_loop_body5.3

true_block.2.5:                                   ; preds = %after_if.2.4
  store float %142, float* %30, align 4
  store float %143, float* %24, align 4
  br label %for_loop_body5.3

for_loop_body5.3:                                 ; preds = %true_block.2.5, %after_if.2.4
  %145 = load float, float* %28, align 4
  %146 = load float, float* %29, align 4
  %147 = fcmp reassoc ninf nsz olt float %145, %146
  br i1 %147, label %true_block.3, label %after_if.3

true_block.3:                                     ; preds = %for_loop_body5.3
  store float %145, float* %29, align 4
  store float %146, float* %28, align 4
  br label %after_if.3

after_if.3:                                       ; preds = %true_block.3, %for_loop_body5.3
  %148 = load float, float* %27, align 4
  %149 = load float, float* %29, align 4
  %150 = fcmp reassoc ninf nsz olt float %148, %149
  br i1 %150, label %true_block.3.1, label %after_if.3.1

true_block.3.1:                                   ; preds = %after_if.3
  store float %148, float* %29, align 4
  store float %149, float* %27, align 4
  br label %after_if.3.1

after_if.3.1:                                     ; preds = %true_block.3.1, %after_if.3
  %151 = load float, float* %26, align 4
  %152 = load float, float* %29, align 4
  %153 = fcmp reassoc ninf nsz olt float %151, %152
  br i1 %153, label %true_block.3.2, label %after_if.3.2

true_block.3.2:                                   ; preds = %after_if.3.1
  store float %151, float* %29, align 4
  store float %152, float* %26, align 4
  br label %after_if.3.2

after_if.3.2:                                     ; preds = %true_block.3.2, %after_if.3.1
  %154 = load float, float* %25, align 4
  %155 = load float, float* %29, align 4
  %156 = fcmp reassoc ninf nsz olt float %154, %155
  br i1 %156, label %true_block.3.3, label %after_if.3.3

true_block.3.3:                                   ; preds = %after_if.3.2
  store float %154, float* %29, align 4
  store float %155, float* %25, align 4
  br label %after_if.3.3

after_if.3.3:                                     ; preds = %true_block.3.3, %after_if.3.2
  %157 = load float, float* %24, align 4
  %158 = load float, float* %29, align 4
  %159 = fcmp reassoc ninf nsz olt float %157, %158
  br i1 %159, label %true_block.3.4, label %for_loop_body5.4

true_block.3.4:                                   ; preds = %after_if.3.3
  store float %157, float* %29, align 4
  store float %158, float* %24, align 4
  br label %for_loop_body5.4

for_loop_body5.4:                                 ; preds = %true_block.3.4, %after_if.3.3
  %160 = load float, float* %27, align 4
  %161 = load float, float* %28, align 4
  %162 = fcmp reassoc ninf nsz olt float %160, %161
  br i1 %162, label %true_block.4, label %after_if.4

true_block.4:                                     ; preds = %for_loop_body5.4
  store float %160, float* %28, align 4
  store float %161, float* %27, align 4
  br label %after_if.4

after_if.4:                                       ; preds = %true_block.4, %for_loop_body5.4
  %163 = load float, float* %26, align 4
  %164 = load float, float* %28, align 4
  %165 = fcmp reassoc ninf nsz olt float %163, %164
  br i1 %165, label %true_block.4.1, label %after_if.4.1

true_block.4.1:                                   ; preds = %after_if.4
  store float %163, float* %28, align 4
  store float %164, float* %26, align 4
  br label %after_if.4.1

after_if.4.1:                                     ; preds = %true_block.4.1, %after_if.4
  %166 = load float, float* %25, align 4
  %167 = load float, float* %28, align 4
  %168 = fcmp reassoc ninf nsz olt float %166, %167
  br i1 %168, label %true_block.4.2, label %after_if.4.2

true_block.4.2:                                   ; preds = %after_if.4.1
  store float %166, float* %28, align 4
  store float %167, float* %25, align 4
  br label %after_if.4.2

after_if.4.2:                                     ; preds = %true_block.4.2, %after_if.4.1
  %169 = load float, float* %24, align 4
  %170 = load float, float* %28, align 4
  %171 = fcmp reassoc ninf nsz olt float %169, %170
  br i1 %171, label %true_block.4.3, label %for_loop_body5.5

true_block.4.3:                                   ; preds = %after_if.4.2
  store float %169, float* %28, align 4
  store float %170, float* %24, align 4
  br label %for_loop_body5.5

for_loop_body5.5:                                 ; preds = %true_block.4.3, %after_if.4.2
  %172 = load float, float* %26, align 4
  %173 = load float, float* %27, align 4
  %174 = fcmp reassoc ninf nsz olt float %172, %173
  br i1 %174, label %true_block.5, label %after_if.5

true_block.5:                                     ; preds = %for_loop_body5.5
  store float %172, float* %27, align 4
  store float %173, float* %26, align 4
  br label %after_if.5

after_if.5:                                       ; preds = %true_block.5, %for_loop_body5.5
  %175 = load float, float* %25, align 4
  %176 = load float, float* %27, align 4
  %177 = fcmp reassoc ninf nsz olt float %175, %176
  br i1 %177, label %true_block.5.1, label %after_if.5.1

true_block.5.1:                                   ; preds = %after_if.5
  store float %175, float* %27, align 4
  store float %176, float* %25, align 4
  br label %after_if.5.1

after_if.5.1:                                     ; preds = %true_block.5.1, %after_if.5
  %178 = load float, float* %24, align 4
  %179 = load float, float* %27, align 4
  %180 = fcmp reassoc ninf nsz olt float %178, %179
  br i1 %180, label %true_block.5.2, label %for_loop_body5.6

true_block.5.2:                                   ; preds = %after_if.5.1
  store float %178, float* %27, align 4
  store float %179, float* %24, align 4
  br label %for_loop_body5.6

for_loop_body5.6:                                 ; preds = %true_block.5.2, %after_if.5.1
  %181 = load float, float* %25, align 4
  %182 = load float, float* %26, align 4
  %183 = fcmp reassoc ninf nsz olt float %181, %182
  br i1 %183, label %true_block.6, label %after_if.6

true_block.6:                                     ; preds = %for_loop_body5.6
  store float %181, float* %26, align 4
  store float %182, float* %25, align 4
  br label %after_if.6

after_if.6:                                       ; preds = %true_block.6, %for_loop_body5.6
  %184 = load float, float* %24, align 4
  %185 = load float, float* %26, align 4
  %186 = fcmp reassoc ninf nsz olt float %184, %185
  br i1 %186, label %true_block.6.1, label %after_if.6.1

true_block.6.1:                                   ; preds = %after_if.6
  store float %184, float* %26, align 4
  store float %185, float* %24, align 4
  br label %after_if.6.1

after_if.6.1:                                     ; preds = %true_block.6.1, %after_if.6
  %187 = load float, float* %24, align 4
  %188 = load float, float* %25, align 4
  %189 = fcmp reassoc ninf nsz olt float %187, %188
  br i1 %189, label %true_block.7, label %for_loop_test4.loopexit.8

true_block.7:                                     ; preds = %after_if.6.1
  store float %187, float* %25, align 4
  store float %188, float* %24, align 4
  br label %for_loop_test4.loopexit.8

for_loop_test4.loopexit.8:                        ; preds = %true_block.7, %after_if.6.1
  %190 = load float, float* %28, align 4
  %191 = load float*, float** %35, align 8
  %192 = load i32, i32* %36, align 4
  %193 = sub i32 %192, %43
  %194 = mul i32 %193, %64
  %195 = add i32 %.01117, %194
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, float* %191, i64 %196
  store float %190, float* %197, align 4
  %198 = add nsw i32 %.01117, 1
  %exitcond25.not = icmp eq i32 %20, %198
  br i1 %exitcond25.not, label %after_for.loopexit, label %for_loop_body5.lr.ph

true_block:                                       ; preds = %for_loop_body5.lr.ph
  store float %106, float* %32, align 4
  store float %107, float* %31, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body5.lr.ph
  %199 = load float, float* %30, align 4
  %200 = load float, float* %32, align 4
  %201 = fcmp reassoc ninf nsz olt float %199, %200
  br i1 %201, label %true_block.130, label %after_if.132

true_block.130:                                   ; preds = %after_if
  store float %199, float* %32, align 4
  store float %200, float* %30, align 4
  br label %after_if.132

after_if.132:                                     ; preds = %true_block.130, %after_if
  %202 = load float, float* %29, align 4
  %203 = load float, float* %32, align 4
  %204 = fcmp reassoc ninf nsz olt float %202, %203
  br i1 %204, label %true_block.235, label %after_if.237

true_block.235:                                   ; preds = %after_if.132
  store float %202, float* %32, align 4
  store float %203, float* %29, align 4
  br label %after_if.237

after_if.237:                                     ; preds = %true_block.235, %after_if.132
  %205 = load float, float* %28, align 4
  %206 = load float, float* %32, align 4
  %207 = fcmp reassoc ninf nsz olt float %205, %206
  br i1 %207, label %true_block.340, label %after_if.342

true_block.340:                                   ; preds = %after_if.237
  store float %205, float* %32, align 4
  store float %206, float* %28, align 4
  br label %after_if.342

after_if.342:                                     ; preds = %true_block.340, %after_if.237
  %208 = load float, float* %27, align 4
  %209 = load float, float* %32, align 4
  %210 = fcmp reassoc ninf nsz olt float %208, %209
  br i1 %210, label %true_block.445, label %after_if.447

true_block.445:                                   ; preds = %after_if.342
  store float %208, float* %32, align 4
  store float %209, float* %27, align 4
  br label %after_if.447

after_if.447:                                     ; preds = %true_block.445, %after_if.342
  %211 = load float, float* %26, align 4
  %212 = load float, float* %32, align 4
  %213 = fcmp reassoc ninf nsz olt float %211, %212
  br i1 %213, label %true_block.550, label %after_if.552

true_block.550:                                   ; preds = %after_if.447
  store float %211, float* %32, align 4
  store float %212, float* %26, align 4
  br label %after_if.552

after_if.552:                                     ; preds = %true_block.550, %after_if.447
  %214 = load float, float* %25, align 4
  %215 = load float, float* %32, align 4
  %216 = fcmp reassoc ninf nsz olt float %214, %215
  br i1 %216, label %true_block.655, label %after_if.657

true_block.655:                                   ; preds = %after_if.552
  store float %214, float* %32, align 4
  store float %215, float* %25, align 4
  br label %after_if.657

after_if.657:                                     ; preds = %true_block.655, %after_if.552
  %217 = load float, float* %32, align 4
  %218 = fcmp reassoc ninf nsz olt float %105, %217
  br i1 %218, label %true_block.759, label %after_if.7

true_block.759:                                   ; preds = %after_if.657
  store float %105, float* %32, align 4
  store float %217, float* %24, align 4
  br label %after_if.7

after_if.7:                                       ; preds = %true_block.759, %after_if.657
  %219 = load float, float* %30, align 4
  %220 = load float, float* %31, align 4
  %221 = fcmp reassoc ninf nsz olt float %219, %220
  br i1 %221, label %true_block.1, label %after_if.1
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.48, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.48**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.48*, %struct.RuntimeContext.48** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.48* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.48* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
