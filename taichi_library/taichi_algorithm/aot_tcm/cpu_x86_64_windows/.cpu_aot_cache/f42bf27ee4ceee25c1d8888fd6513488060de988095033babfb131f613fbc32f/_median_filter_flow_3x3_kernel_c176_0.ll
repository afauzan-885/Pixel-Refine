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
define void @_median_filter_flow_3x3_kernel_c176_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_median_filter_flow_3x3_kernel_c176_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %3 = alloca [9 x float], align 16
  %4 = alloca [9 x float], align 4
  %5 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %0, i64 0, i32 1
  %6 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %6, i64 0, i32 14
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
  %23 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %24 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %23, align 8
  %25 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 7
  %26 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 6
  %27 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 5
  %28 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 4
  %29 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 3
  %30 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 2
  %31 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 1
  %32 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 0
  %33 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 8
  %34 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 7
  %35 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 6
  %36 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 5
  %37 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 4
  %38 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 3
  %39 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 2
  %40 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 1
  %41 = getelementptr inbounds [9 x float], [9 x float]* %4, i64 0, i64 0
  %42 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 0, i32 1
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 0, i32 0, i32 1
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 1, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %24, i64 0, i32 1, i32 0, i32 1
  %46 = getelementptr inbounds [9 x float], [9 x float]* %3, i64 0, i64 8
  %47 = bitcast [9 x float]* %3 to <4 x float>*
  %48 = bitcast float* %28 to <2 x float>*
  %49 = bitcast [9 x float]* %4 to <8 x float>*
  %50 = bitcast float* %25 to <2 x float>*
  %51 = shl i32 %19, 1
  br label %for_loop_body5.lr.ph

after_for.loopexit:                               ; preds = %for_loop_test12.loopexit.8
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body5.lr.ph:                             ; preds = %for_loop_test12.loopexit.8, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %for_loop_test12.loopexit.8 ], [ %51, %for_loop_body.lr.ph ]
  %.01929 = phi i32 [ %19, %for_loop_body.lr.ph ], [ %359, %for_loop_test12.loopexit.8 ]
  %52 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %5, align 8
  %53 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %52, i64 0, i32 14
  %54 = load i8*, i8** %53, align 8
  %55 = getelementptr inbounds i8, i8* %54, i64 4
  %56 = bitcast i8* %55 to i32*
  %57 = load i32, i32* %56, align 4
  %58 = sdiv i32 %.01929, %57
  %59 = mul i32 %58, %57
  %60 = xor i32 %57, %.01929
  %61 = icmp slt i32 %60, 0
  %62 = icmp ne i32 %.01929, 0
  %63 = icmp ne i32 %.01929, %59
  %64 = and i1 %62, %61
  %65 = and i1 %64, %63
  %.neg24 = sext i1 %65 to i32
  %66 = getelementptr inbounds i8, i8* %54, i64 8
  %67 = bitcast i8* %66 to i32*
  %68 = load i32, i32* %67, align 4
  %69 = add i32 %68, -1
  %70 = getelementptr inbounds i8, i8* %54, i64 12
  %71 = bitcast i8* %70 to i32*
  %72 = load i32, i32* %71, align 4
  %73 = add i32 %72, -1
  %74 = load float*, float** %42, align 8
  %75 = load i32, i32* %43, align 4
  %76 = add i32 %58, %.neg24
  %77 = mul i32 %57, -1
  %78 = mul i32 %77, %76
  %79 = add i32 %.01929, %78
  %80 = add i32 %76, -1
  %81 = add i32 %79, -1
  %82 = tail call i32 @llvm.smax.i32(i32 %81, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %73, i32 %82)
  %84 = add i32 %79, 1
  %85 = insertelement <2 x i32> poison, i32 %80, i64 0
  %86 = insertelement <2 x i32> %85, i32 %76, i64 1
  %87 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %86, <2 x i32> zeroinitializer)
  %88 = insertelement <2 x i32> poison, i32 %69, i64 0
  %89 = shufflevector <2 x i32> %88, <2 x i32> poison, <2 x i32> zeroinitializer
  %90 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %87)
  %91 = insertelement <2 x i32> poison, i32 %75, i64 0
  %92 = shufflevector <2 x i32> %91, <2 x i32> poison, <2 x i32> zeroinitializer
  %93 = mul <2 x i32> %90, %92
  %shuffle46 = shufflevector <2 x i32> %93, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 0, i32 1>
  %94 = insertelement <4 x i32> poison, i32 %83, i64 0
  %95 = insertelement <4 x float*> poison, float* %74, i64 0
  %shuffle = shufflevector <4 x float*> %95, <4 x float*> poison, <4 x i32> zeroinitializer
  %96 = insertelement <2 x i32> poison, i32 %79, i64 0
  %97 = insertelement <2 x i32> %96, i32 %84, i64 1
  %98 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %97, <2 x i32> zeroinitializer)
  %99 = insertelement <2 x i32> poison, i32 %73, i64 0
  %100 = shufflevector <2 x i32> %99, <2 x i32> poison, <2 x i32> zeroinitializer
  %101 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %100, <2 x i32> %98)
  %102 = shufflevector <2 x i32> %101, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %103 = shufflevector <4 x i32> %94, <4 x i32> %102, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %104 = insertelement <4 x i32> %103, i32 %83, i64 3
  %105 = add <4 x i32> %shuffle46, %104
  %106 = shl <4 x i32> %105, <i32 1, i32 1, i32 1, i32 1>
  %107 = sext <4 x i32> %106 to <4 x i64>
  %108 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %107
  %109 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %108, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  store <4 x float> %109, <4 x float>* %47, align 16
  %110 = shufflevector <2 x i32> %93, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %111 = add <2 x i32> %101, %110
  %112 = shl <2 x i32> %111, <i32 1, i32 1>
  %113 = extractelement <2 x i32> %112, i64 0
  %114 = sext <2 x i32> %112 to <2 x i64>
  %115 = insertelement <2 x float*> poison, float* %74, i64 0
  %116 = shufflevector <2 x float*> %115, <2 x float*> poison, <2 x i32> zeroinitializer
  %117 = getelementptr float, <2 x float*> %116, <2 x i64> %114
  %118 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %117, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  store <2 x float> %118, <2 x float>* %48, align 16
  %119 = extractelement <2 x i32> %112, i64 1
  %120 = add i32 %76, 1
  %121 = tail call i32 @llvm.smax.i32(i32 %120, i32 0)
  %122 = tail call i32 @llvm.smin.i32(i32 %69, i32 %121)
  %123 = mul i32 %122, %75
  %124 = add i32 %83, %123
  %125 = shl i32 %124, 1
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, float* %74, i64 %126
  %128 = load float, float* %127, align 4
  store float %128, float* %26, align 8
  %129 = insertelement <2 x i32> poison, i32 %123, i64 0
  %130 = shufflevector <2 x i32> %129, <2 x i32> poison, <2 x i32> zeroinitializer
  %131 = add <2 x i32> %130, %101
  %132 = shl <2 x i32> %131, <i32 1, i32 1>
  %133 = shufflevector <2 x i32> %132, <2 x i32> poison, <8 x i32> <i32 0, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %134 = shufflevector <4 x i32> %106, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %135 = insertelement <8 x i32> %134, i32 %113, i64 4
  %136 = insertelement <8 x i32> %135, i32 %119, i64 5
  %137 = insertelement <8 x i32> %136, i32 %125, i64 6
  %138 = shufflevector <8 x i32> %137, <8 x i32> %133, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 8>
  %139 = or <8 x i32> %138, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %140 = sext <8 x i32> %139 to <8 x i64>
  %141 = insertelement <8 x float*> poison, float* %74, i64 0
  %shuffle47 = shufflevector <8 x float*> %141, <8 x float*> poison, <8 x i32> zeroinitializer
  %142 = getelementptr float, <8 x float*> %shuffle47, <8 x i64> %140
  %143 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %142, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  store <8 x float> %143, <8 x float>* %49, align 4
  %144 = sext <2 x i32> %132 to <2 x i64>
  %145 = getelementptr float, <2 x float*> %116, <2 x i64> %144
  %146 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %145, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  store <2 x float> %146, <2 x float>* %50, align 4
  %147 = extractelement <2 x i32> %132, i64 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %74, i64 %148
  %150 = getelementptr float, float* %149, i64 1
  %151 = load float, float* %150, align 4
  store float %151, float* %33, align 4
  %152 = load float, float* %31, align 4
  %153 = load float, float* %32, align 16
  %154 = fcmp reassoc ninf nsz olt float %152, %153
  br i1 %154, label %true_block, label %after_if

true_block.1:                                     ; preds = %after_if.7
  store float %256, float* %31, align 4
  store float %257, float* %30, align 8
  br label %after_if.1

after_if.1:                                       ; preds = %after_if.7, %true_block.1
  %155 = load float, float* %29, align 4
  %156 = load float, float* %31, align 4
  %157 = fcmp reassoc ninf nsz olt float %155, %156
  br i1 %157, label %true_block.1.1, label %after_if.1.1

true_block.1.1:                                   ; preds = %after_if.1
  store float %155, float* %31, align 4
  store float %156, float* %29, align 4
  br label %after_if.1.1

after_if.1.1:                                     ; preds = %true_block.1.1, %after_if.1
  %158 = load float, float* %28, align 16
  %159 = load float, float* %31, align 4
  %160 = fcmp reassoc ninf nsz olt float %158, %159
  br i1 %160, label %true_block.1.2, label %after_if.1.2

true_block.1.2:                                   ; preds = %after_if.1.1
  store float %158, float* %31, align 4
  store float %159, float* %28, align 16
  br label %after_if.1.2

after_if.1.2:                                     ; preds = %true_block.1.2, %after_if.1.1
  %161 = load float, float* %27, align 4
  %162 = load float, float* %31, align 4
  %163 = fcmp reassoc ninf nsz olt float %161, %162
  br i1 %163, label %true_block.1.3, label %after_if.1.3

true_block.1.3:                                   ; preds = %after_if.1.2
  store float %161, float* %31, align 4
  store float %162, float* %27, align 4
  br label %after_if.1.3

after_if.1.3:                                     ; preds = %true_block.1.3, %after_if.1.2
  %164 = load float, float* %26, align 8
  %165 = load float, float* %31, align 4
  %166 = fcmp reassoc ninf nsz olt float %164, %165
  br i1 %166, label %true_block.1.4, label %after_if.1.4

true_block.1.4:                                   ; preds = %after_if.1.3
  store float %164, float* %31, align 4
  store float %165, float* %26, align 8
  br label %after_if.1.4

after_if.1.4:                                     ; preds = %true_block.1.4, %after_if.1.3
  %167 = load float, float* %25, align 4
  %168 = load float, float* %31, align 4
  %169 = fcmp reassoc ninf nsz olt float %167, %168
  br i1 %169, label %true_block.1.5, label %after_if.1.5

true_block.1.5:                                   ; preds = %after_if.1.4
  store float %167, float* %31, align 4
  store float %168, float* %25, align 4
  br label %after_if.1.5

after_if.1.5:                                     ; preds = %true_block.1.5, %after_if.1.4
  %170 = load float, float* %46, align 16
  %171 = load float, float* %31, align 4
  %172 = fcmp reassoc ninf nsz olt float %170, %171
  br i1 %172, label %true_block.1.6, label %for_loop_body5.2

true_block.1.6:                                   ; preds = %after_if.1.5
  store float %170, float* %31, align 4
  store float %171, float* %46, align 16
  br label %for_loop_body5.2

for_loop_body5.2:                                 ; preds = %true_block.1.6, %after_if.1.5
  %173 = load float, float* %29, align 4
  %174 = load float, float* %30, align 8
  %175 = fcmp reassoc ninf nsz olt float %173, %174
  br i1 %175, label %true_block.2, label %after_if.2

true_block.2:                                     ; preds = %for_loop_body5.2
  store float %173, float* %30, align 8
  store float %174, float* %29, align 4
  br label %after_if.2

after_if.2:                                       ; preds = %true_block.2, %for_loop_body5.2
  %176 = load float, float* %28, align 16
  %177 = load float, float* %30, align 8
  %178 = fcmp reassoc ninf nsz olt float %176, %177
  br i1 %178, label %true_block.2.1, label %after_if.2.1

true_block.2.1:                                   ; preds = %after_if.2
  store float %176, float* %30, align 8
  store float %177, float* %28, align 16
  br label %after_if.2.1

after_if.2.1:                                     ; preds = %true_block.2.1, %after_if.2
  %179 = load float, float* %27, align 4
  %180 = load float, float* %30, align 8
  %181 = fcmp reassoc ninf nsz olt float %179, %180
  br i1 %181, label %true_block.2.2, label %after_if.2.2

true_block.2.2:                                   ; preds = %after_if.2.1
  store float %179, float* %30, align 8
  store float %180, float* %27, align 4
  br label %after_if.2.2

after_if.2.2:                                     ; preds = %true_block.2.2, %after_if.2.1
  %182 = load float, float* %26, align 8
  %183 = load float, float* %30, align 8
  %184 = fcmp reassoc ninf nsz olt float %182, %183
  br i1 %184, label %true_block.2.3, label %after_if.2.3

true_block.2.3:                                   ; preds = %after_if.2.2
  store float %182, float* %30, align 8
  store float %183, float* %26, align 8
  br label %after_if.2.3

after_if.2.3:                                     ; preds = %true_block.2.3, %after_if.2.2
  %185 = load float, float* %25, align 4
  %186 = load float, float* %30, align 8
  %187 = fcmp reassoc ninf nsz olt float %185, %186
  br i1 %187, label %true_block.2.4, label %after_if.2.4

true_block.2.4:                                   ; preds = %after_if.2.3
  store float %185, float* %30, align 8
  store float %186, float* %25, align 4
  br label %after_if.2.4

after_if.2.4:                                     ; preds = %true_block.2.4, %after_if.2.3
  %188 = load float, float* %46, align 16
  %189 = load float, float* %30, align 8
  %190 = fcmp reassoc ninf nsz olt float %188, %189
  br i1 %190, label %true_block.2.5, label %for_loop_body5.3

true_block.2.5:                                   ; preds = %after_if.2.4
  store float %188, float* %30, align 8
  store float %189, float* %46, align 16
  br label %for_loop_body5.3

for_loop_body5.3:                                 ; preds = %true_block.2.5, %after_if.2.4
  %191 = load float, float* %28, align 16
  %192 = load float, float* %29, align 4
  %193 = fcmp reassoc ninf nsz olt float %191, %192
  br i1 %193, label %true_block.3, label %after_if.3

true_block.3:                                     ; preds = %for_loop_body5.3
  store float %191, float* %29, align 4
  store float %192, float* %28, align 16
  br label %after_if.3

after_if.3:                                       ; preds = %true_block.3, %for_loop_body5.3
  %194 = load float, float* %27, align 4
  %195 = load float, float* %29, align 4
  %196 = fcmp reassoc ninf nsz olt float %194, %195
  br i1 %196, label %true_block.3.1, label %after_if.3.1

true_block.3.1:                                   ; preds = %after_if.3
  store float %194, float* %29, align 4
  store float %195, float* %27, align 4
  br label %after_if.3.1

after_if.3.1:                                     ; preds = %true_block.3.1, %after_if.3
  %197 = load float, float* %26, align 8
  %198 = load float, float* %29, align 4
  %199 = fcmp reassoc ninf nsz olt float %197, %198
  br i1 %199, label %true_block.3.2, label %after_if.3.2

true_block.3.2:                                   ; preds = %after_if.3.1
  store float %197, float* %29, align 4
  store float %198, float* %26, align 8
  br label %after_if.3.2

after_if.3.2:                                     ; preds = %true_block.3.2, %after_if.3.1
  %200 = load float, float* %25, align 4
  %201 = load float, float* %29, align 4
  %202 = fcmp reassoc ninf nsz olt float %200, %201
  br i1 %202, label %true_block.3.3, label %after_if.3.3

true_block.3.3:                                   ; preds = %after_if.3.2
  store float %200, float* %29, align 4
  store float %201, float* %25, align 4
  br label %after_if.3.3

after_if.3.3:                                     ; preds = %true_block.3.3, %after_if.3.2
  %203 = load float, float* %46, align 16
  %204 = load float, float* %29, align 4
  %205 = fcmp reassoc ninf nsz olt float %203, %204
  br i1 %205, label %true_block.3.4, label %for_loop_body5.4

true_block.3.4:                                   ; preds = %after_if.3.3
  store float %203, float* %29, align 4
  store float %204, float* %46, align 16
  br label %for_loop_body5.4

for_loop_body5.4:                                 ; preds = %true_block.3.4, %after_if.3.3
  %206 = load float, float* %27, align 4
  %207 = load float, float* %28, align 16
  %208 = fcmp reassoc ninf nsz olt float %206, %207
  br i1 %208, label %true_block.4, label %after_if.4

true_block.4:                                     ; preds = %for_loop_body5.4
  store float %206, float* %28, align 16
  store float %207, float* %27, align 4
  br label %after_if.4

after_if.4:                                       ; preds = %true_block.4, %for_loop_body5.4
  %209 = load float, float* %26, align 8
  %210 = load float, float* %28, align 16
  %211 = fcmp reassoc ninf nsz olt float %209, %210
  br i1 %211, label %true_block.4.1, label %after_if.4.1

true_block.4.1:                                   ; preds = %after_if.4
  store float %209, float* %28, align 16
  store float %210, float* %26, align 8
  br label %after_if.4.1

after_if.4.1:                                     ; preds = %true_block.4.1, %after_if.4
  %212 = load float, float* %25, align 4
  %213 = load float, float* %28, align 16
  %214 = fcmp reassoc ninf nsz olt float %212, %213
  br i1 %214, label %true_block.4.2, label %after_if.4.2

true_block.4.2:                                   ; preds = %after_if.4.1
  store float %212, float* %28, align 16
  store float %213, float* %25, align 4
  br label %after_if.4.2

after_if.4.2:                                     ; preds = %true_block.4.2, %after_if.4.1
  %215 = load float, float* %46, align 16
  %216 = load float, float* %28, align 16
  %217 = fcmp reassoc ninf nsz olt float %215, %216
  br i1 %217, label %true_block.4.3, label %for_loop_body5.5

true_block.4.3:                                   ; preds = %after_if.4.2
  store float %215, float* %28, align 16
  store float %216, float* %46, align 16
  br label %for_loop_body5.5

for_loop_body5.5:                                 ; preds = %true_block.4.3, %after_if.4.2
  %218 = load float, float* %26, align 8
  %219 = load float, float* %27, align 4
  %220 = fcmp reassoc ninf nsz olt float %218, %219
  br i1 %220, label %true_block.5, label %after_if.5

true_block.5:                                     ; preds = %for_loop_body5.5
  store float %218, float* %27, align 4
  store float %219, float* %26, align 8
  br label %after_if.5

after_if.5:                                       ; preds = %true_block.5, %for_loop_body5.5
  %221 = load float, float* %25, align 4
  %222 = load float, float* %27, align 4
  %223 = fcmp reassoc ninf nsz olt float %221, %222
  br i1 %223, label %true_block.5.1, label %after_if.5.1

true_block.5.1:                                   ; preds = %after_if.5
  store float %221, float* %27, align 4
  store float %222, float* %25, align 4
  br label %after_if.5.1

after_if.5.1:                                     ; preds = %true_block.5.1, %after_if.5
  %224 = load float, float* %46, align 16
  %225 = load float, float* %27, align 4
  %226 = fcmp reassoc ninf nsz olt float %224, %225
  br i1 %226, label %true_block.5.2, label %for_loop_body5.6

true_block.5.2:                                   ; preds = %after_if.5.1
  store float %224, float* %27, align 4
  store float %225, float* %46, align 16
  br label %for_loop_body5.6

for_loop_body5.6:                                 ; preds = %true_block.5.2, %after_if.5.1
  %227 = load float, float* %25, align 4
  %228 = load float, float* %26, align 8
  %229 = fcmp reassoc ninf nsz olt float %227, %228
  br i1 %229, label %true_block.6, label %after_if.6

true_block.6:                                     ; preds = %for_loop_body5.6
  store float %227, float* %26, align 8
  store float %228, float* %25, align 4
  br label %after_if.6

after_if.6:                                       ; preds = %true_block.6, %for_loop_body5.6
  %230 = load float, float* %46, align 16
  %231 = load float, float* %26, align 8
  %232 = fcmp reassoc ninf nsz olt float %230, %231
  br i1 %232, label %true_block.6.1, label %after_if.6.1

true_block.6.1:                                   ; preds = %after_if.6
  store float %230, float* %26, align 8
  store float %231, float* %46, align 16
  br label %after_if.6.1

after_if.6.1:                                     ; preds = %true_block.6.1, %after_if.6
  %233 = load float, float* %46, align 16
  %234 = load float, float* %25, align 4
  %235 = fcmp reassoc ninf nsz olt float %233, %234
  br i1 %235, label %true_block.7, label %for_loop_body13

true_block.7:                                     ; preds = %after_if.6.1
  store float %233, float* %25, align 4
  store float %234, float* %46, align 16
  br label %for_loop_body13

true_block:                                       ; preds = %for_loop_body5.lr.ph
  store float %152, float* %32, align 16
  store float %153, float* %31, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body5.lr.ph
  %236 = load float, float* %30, align 8
  %237 = load float, float* %32, align 16
  %238 = fcmp reassoc ninf nsz olt float %236, %237
  br i1 %238, label %true_block.150, label %after_if.152

true_block.150:                                   ; preds = %after_if
  store float %236, float* %32, align 16
  store float %237, float* %30, align 8
  br label %after_if.152

after_if.152:                                     ; preds = %true_block.150, %after_if
  %239 = load float, float* %29, align 4
  %240 = load float, float* %32, align 16
  %241 = fcmp reassoc ninf nsz olt float %239, %240
  br i1 %241, label %true_block.255, label %after_if.257

true_block.255:                                   ; preds = %after_if.152
  store float %239, float* %32, align 16
  store float %240, float* %29, align 4
  br label %after_if.257

after_if.257:                                     ; preds = %true_block.255, %after_if.152
  %242 = load float, float* %28, align 16
  %243 = load float, float* %32, align 16
  %244 = fcmp reassoc ninf nsz olt float %242, %243
  br i1 %244, label %true_block.360, label %after_if.362

true_block.360:                                   ; preds = %after_if.257
  store float %242, float* %32, align 16
  store float %243, float* %28, align 16
  br label %after_if.362

after_if.362:                                     ; preds = %true_block.360, %after_if.257
  %245 = load float, float* %27, align 4
  %246 = load float, float* %32, align 16
  %247 = fcmp reassoc ninf nsz olt float %245, %246
  br i1 %247, label %true_block.465, label %after_if.467

true_block.465:                                   ; preds = %after_if.362
  store float %245, float* %32, align 16
  store float %246, float* %27, align 4
  br label %after_if.467

after_if.467:                                     ; preds = %true_block.465, %after_if.362
  %248 = load float, float* %32, align 16
  %249 = fcmp reassoc ninf nsz olt float %128, %248
  br i1 %249, label %true_block.570, label %after_if.572

true_block.570:                                   ; preds = %after_if.467
  store float %128, float* %32, align 16
  store float %248, float* %26, align 8
  br label %after_if.572

after_if.572:                                     ; preds = %true_block.570, %after_if.467
  %250 = load float, float* %25, align 4
  %251 = load float, float* %32, align 16
  %252 = fcmp reassoc ninf nsz olt float %250, %251
  br i1 %252, label %true_block.675, label %after_if.677

true_block.675:                                   ; preds = %after_if.572
  store float %250, float* %32, align 16
  store float %251, float* %25, align 4
  br label %after_if.677

after_if.677:                                     ; preds = %true_block.675, %after_if.572
  %253 = load float, float* %46, align 16
  %254 = load float, float* %32, align 16
  %255 = fcmp reassoc ninf nsz olt float %253, %254
  br i1 %255, label %true_block.779, label %after_if.7

true_block.779:                                   ; preds = %after_if.677
  store float %253, float* %32, align 16
  store float %254, float* %46, align 16
  br label %after_if.7

after_if.7:                                       ; preds = %true_block.779, %after_if.677
  %256 = load float, float* %30, align 8
  %257 = load float, float* %31, align 4
  %258 = fcmp reassoc ninf nsz olt float %256, %257
  br i1 %258, label %true_block.1, label %after_if.1

true_block17.1:                                   ; preds = %after_if19.7
  store float %383, float* %40, align 4
  store float %384, float* %39, align 4
  br label %after_if19.1

after_if19.1:                                     ; preds = %after_if19.7, %true_block17.1
  %259 = load float, float* %38, align 4
  %260 = load float, float* %40, align 4
  %261 = fcmp reassoc ninf nsz olt float %259, %260
  br i1 %261, label %true_block17.1.1, label %after_if19.1.1

true_block17.1.1:                                 ; preds = %after_if19.1
  store float %259, float* %40, align 4
  store float %260, float* %38, align 4
  br label %after_if19.1.1

after_if19.1.1:                                   ; preds = %true_block17.1.1, %after_if19.1
  %262 = load float, float* %37, align 4
  %263 = load float, float* %40, align 4
  %264 = fcmp reassoc ninf nsz olt float %262, %263
  br i1 %264, label %true_block17.1.2, label %after_if19.1.2

true_block17.1.2:                                 ; preds = %after_if19.1.1
  store float %262, float* %40, align 4
  store float %263, float* %37, align 4
  br label %after_if19.1.2

after_if19.1.2:                                   ; preds = %true_block17.1.2, %after_if19.1.1
  %265 = load float, float* %36, align 4
  %266 = load float, float* %40, align 4
  %267 = fcmp reassoc ninf nsz olt float %265, %266
  br i1 %267, label %true_block17.1.3, label %after_if19.1.3

true_block17.1.3:                                 ; preds = %after_if19.1.2
  store float %265, float* %40, align 4
  store float %266, float* %36, align 4
  br label %after_if19.1.3

after_if19.1.3:                                   ; preds = %true_block17.1.3, %after_if19.1.2
  %268 = load float, float* %35, align 4
  %269 = load float, float* %40, align 4
  %270 = fcmp reassoc ninf nsz olt float %268, %269
  br i1 %270, label %true_block17.1.4, label %after_if19.1.4

true_block17.1.4:                                 ; preds = %after_if19.1.3
  store float %268, float* %40, align 4
  store float %269, float* %35, align 4
  br label %after_if19.1.4

after_if19.1.4:                                   ; preds = %true_block17.1.4, %after_if19.1.3
  %271 = load float, float* %34, align 4
  %272 = load float, float* %40, align 4
  %273 = fcmp reassoc ninf nsz olt float %271, %272
  br i1 %273, label %true_block17.1.5, label %after_if19.1.5

true_block17.1.5:                                 ; preds = %after_if19.1.4
  store float %271, float* %40, align 4
  store float %272, float* %34, align 4
  br label %after_if19.1.5

after_if19.1.5:                                   ; preds = %true_block17.1.5, %after_if19.1.4
  %274 = load float, float* %33, align 4
  %275 = load float, float* %40, align 4
  %276 = fcmp reassoc ninf nsz olt float %274, %275
  br i1 %276, label %true_block17.1.6, label %for_loop_body13.2

true_block17.1.6:                                 ; preds = %after_if19.1.5
  store float %274, float* %40, align 4
  store float %275, float* %33, align 4
  br label %for_loop_body13.2

for_loop_body13.2:                                ; preds = %true_block17.1.6, %after_if19.1.5
  %277 = load float, float* %38, align 4
  %278 = load float, float* %39, align 4
  %279 = fcmp reassoc ninf nsz olt float %277, %278
  br i1 %279, label %true_block17.2, label %after_if19.2

true_block17.2:                                   ; preds = %for_loop_body13.2
  store float %277, float* %39, align 4
  store float %278, float* %38, align 4
  br label %after_if19.2

after_if19.2:                                     ; preds = %true_block17.2, %for_loop_body13.2
  %280 = load float, float* %37, align 4
  %281 = load float, float* %39, align 4
  %282 = fcmp reassoc ninf nsz olt float %280, %281
  br i1 %282, label %true_block17.2.1, label %after_if19.2.1

true_block17.2.1:                                 ; preds = %after_if19.2
  store float %280, float* %39, align 4
  store float %281, float* %37, align 4
  br label %after_if19.2.1

after_if19.2.1:                                   ; preds = %true_block17.2.1, %after_if19.2
  %283 = load float, float* %36, align 4
  %284 = load float, float* %39, align 4
  %285 = fcmp reassoc ninf nsz olt float %283, %284
  br i1 %285, label %true_block17.2.2, label %after_if19.2.2

true_block17.2.2:                                 ; preds = %after_if19.2.1
  store float %283, float* %39, align 4
  store float %284, float* %36, align 4
  br label %after_if19.2.2

after_if19.2.2:                                   ; preds = %true_block17.2.2, %after_if19.2.1
  %286 = load float, float* %35, align 4
  %287 = load float, float* %39, align 4
  %288 = fcmp reassoc ninf nsz olt float %286, %287
  br i1 %288, label %true_block17.2.3, label %after_if19.2.3

true_block17.2.3:                                 ; preds = %after_if19.2.2
  store float %286, float* %39, align 4
  store float %287, float* %35, align 4
  br label %after_if19.2.3

after_if19.2.3:                                   ; preds = %true_block17.2.3, %after_if19.2.2
  %289 = load float, float* %34, align 4
  %290 = load float, float* %39, align 4
  %291 = fcmp reassoc ninf nsz olt float %289, %290
  br i1 %291, label %true_block17.2.4, label %after_if19.2.4

true_block17.2.4:                                 ; preds = %after_if19.2.3
  store float %289, float* %39, align 4
  store float %290, float* %34, align 4
  br label %after_if19.2.4

after_if19.2.4:                                   ; preds = %true_block17.2.4, %after_if19.2.3
  %292 = load float, float* %33, align 4
  %293 = load float, float* %39, align 4
  %294 = fcmp reassoc ninf nsz olt float %292, %293
  br i1 %294, label %true_block17.2.5, label %for_loop_body13.3

true_block17.2.5:                                 ; preds = %after_if19.2.4
  store float %292, float* %39, align 4
  store float %293, float* %33, align 4
  br label %for_loop_body13.3

for_loop_body13.3:                                ; preds = %true_block17.2.5, %after_if19.2.4
  %295 = load float, float* %37, align 4
  %296 = load float, float* %38, align 4
  %297 = fcmp reassoc ninf nsz olt float %295, %296
  br i1 %297, label %true_block17.3, label %after_if19.3

true_block17.3:                                   ; preds = %for_loop_body13.3
  store float %295, float* %38, align 4
  store float %296, float* %37, align 4
  br label %after_if19.3

after_if19.3:                                     ; preds = %true_block17.3, %for_loop_body13.3
  %298 = load float, float* %36, align 4
  %299 = load float, float* %38, align 4
  %300 = fcmp reassoc ninf nsz olt float %298, %299
  br i1 %300, label %true_block17.3.1, label %after_if19.3.1

true_block17.3.1:                                 ; preds = %after_if19.3
  store float %298, float* %38, align 4
  store float %299, float* %36, align 4
  br label %after_if19.3.1

after_if19.3.1:                                   ; preds = %true_block17.3.1, %after_if19.3
  %301 = load float, float* %35, align 4
  %302 = load float, float* %38, align 4
  %303 = fcmp reassoc ninf nsz olt float %301, %302
  br i1 %303, label %true_block17.3.2, label %after_if19.3.2

true_block17.3.2:                                 ; preds = %after_if19.3.1
  store float %301, float* %38, align 4
  store float %302, float* %35, align 4
  br label %after_if19.3.2

after_if19.3.2:                                   ; preds = %true_block17.3.2, %after_if19.3.1
  %304 = load float, float* %34, align 4
  %305 = load float, float* %38, align 4
  %306 = fcmp reassoc ninf nsz olt float %304, %305
  br i1 %306, label %true_block17.3.3, label %after_if19.3.3

true_block17.3.3:                                 ; preds = %after_if19.3.2
  store float %304, float* %38, align 4
  store float %305, float* %34, align 4
  br label %after_if19.3.3

after_if19.3.3:                                   ; preds = %true_block17.3.3, %after_if19.3.2
  %307 = load float, float* %33, align 4
  %308 = load float, float* %38, align 4
  %309 = fcmp reassoc ninf nsz olt float %307, %308
  br i1 %309, label %true_block17.3.4, label %for_loop_body13.4

true_block17.3.4:                                 ; preds = %after_if19.3.3
  store float %307, float* %38, align 4
  store float %308, float* %33, align 4
  br label %for_loop_body13.4

for_loop_body13.4:                                ; preds = %true_block17.3.4, %after_if19.3.3
  %310 = load float, float* %36, align 4
  %311 = load float, float* %37, align 4
  %312 = fcmp reassoc ninf nsz olt float %310, %311
  br i1 %312, label %true_block17.4, label %after_if19.4

true_block17.4:                                   ; preds = %for_loop_body13.4
  store float %310, float* %37, align 4
  store float %311, float* %36, align 4
  br label %after_if19.4

after_if19.4:                                     ; preds = %true_block17.4, %for_loop_body13.4
  %313 = load float, float* %35, align 4
  %314 = load float, float* %37, align 4
  %315 = fcmp reassoc ninf nsz olt float %313, %314
  br i1 %315, label %true_block17.4.1, label %after_if19.4.1

true_block17.4.1:                                 ; preds = %after_if19.4
  store float %313, float* %37, align 4
  store float %314, float* %35, align 4
  br label %after_if19.4.1

after_if19.4.1:                                   ; preds = %true_block17.4.1, %after_if19.4
  %316 = load float, float* %34, align 4
  %317 = load float, float* %37, align 4
  %318 = fcmp reassoc ninf nsz olt float %316, %317
  br i1 %318, label %true_block17.4.2, label %after_if19.4.2

true_block17.4.2:                                 ; preds = %after_if19.4.1
  store float %316, float* %37, align 4
  store float %317, float* %34, align 4
  br label %after_if19.4.2

after_if19.4.2:                                   ; preds = %true_block17.4.2, %after_if19.4.1
  %319 = load float, float* %33, align 4
  %320 = load float, float* %37, align 4
  %321 = fcmp reassoc ninf nsz olt float %319, %320
  br i1 %321, label %true_block17.4.3, label %for_loop_body13.5

true_block17.4.3:                                 ; preds = %after_if19.4.2
  store float %319, float* %37, align 4
  store float %320, float* %33, align 4
  br label %for_loop_body13.5

for_loop_body13.5:                                ; preds = %true_block17.4.3, %after_if19.4.2
  %322 = load float, float* %35, align 4
  %323 = load float, float* %36, align 4
  %324 = fcmp reassoc ninf nsz olt float %322, %323
  br i1 %324, label %true_block17.5, label %after_if19.5

true_block17.5:                                   ; preds = %for_loop_body13.5
  store float %322, float* %36, align 4
  store float %323, float* %35, align 4
  br label %after_if19.5

after_if19.5:                                     ; preds = %true_block17.5, %for_loop_body13.5
  %325 = load float, float* %34, align 4
  %326 = load float, float* %36, align 4
  %327 = fcmp reassoc ninf nsz olt float %325, %326
  br i1 %327, label %true_block17.5.1, label %after_if19.5.1

true_block17.5.1:                                 ; preds = %after_if19.5
  store float %325, float* %36, align 4
  store float %326, float* %34, align 4
  br label %after_if19.5.1

after_if19.5.1:                                   ; preds = %true_block17.5.1, %after_if19.5
  %328 = load float, float* %33, align 4
  %329 = load float, float* %36, align 4
  %330 = fcmp reassoc ninf nsz olt float %328, %329
  br i1 %330, label %true_block17.5.2, label %for_loop_body13.6

true_block17.5.2:                                 ; preds = %after_if19.5.1
  store float %328, float* %36, align 4
  store float %329, float* %33, align 4
  br label %for_loop_body13.6

for_loop_body13.6:                                ; preds = %true_block17.5.2, %after_if19.5.1
  %331 = load float, float* %34, align 4
  %332 = load float, float* %35, align 4
  %333 = fcmp reassoc ninf nsz olt float %331, %332
  br i1 %333, label %true_block17.6, label %after_if19.6

true_block17.6:                                   ; preds = %for_loop_body13.6
  store float %331, float* %35, align 4
  store float %332, float* %34, align 4
  br label %after_if19.6

after_if19.6:                                     ; preds = %true_block17.6, %for_loop_body13.6
  %334 = load float, float* %33, align 4
  %335 = load float, float* %35, align 4
  %336 = fcmp reassoc ninf nsz olt float %334, %335
  br i1 %336, label %true_block17.6.1, label %after_if19.6.1

true_block17.6.1:                                 ; preds = %after_if19.6
  store float %334, float* %35, align 4
  store float %335, float* %33, align 4
  br label %after_if19.6.1

after_if19.6.1:                                   ; preds = %true_block17.6.1, %after_if19.6
  %337 = load float, float* %33, align 4
  %338 = load float, float* %34, align 4
  %339 = fcmp reassoc ninf nsz olt float %337, %338
  br i1 %339, label %true_block17.7, label %for_loop_test12.loopexit.8

true_block17.7:                                   ; preds = %after_if19.6.1
  store float %337, float* %34, align 4
  store float %338, float* %33, align 4
  br label %for_loop_test12.loopexit.8

for_loop_test12.loopexit.8:                       ; preds = %true_block17.7, %after_if19.6.1
  %340 = load float, float* %28, align 16
  %341 = load float*, float** %44, align 8
  %342 = load i32, i32* %45, align 4
  %343 = sub i32 %342, %57
  %344 = shl i32 %343, 1
  %345 = mul i32 %344, %76
  %346 = add i32 %lsr.iv, %345
  %347 = sext i32 %346 to i64
  %348 = getelementptr float, float* %341, i64 %347
  store float %340, float* %348, align 4
  %349 = load float, float* %37, align 4
  %350 = load float*, float** %44, align 8
  %351 = load i32, i32* %45, align 4
  %352 = sub i32 %351, %57
  %353 = shl i32 %352, 1
  %354 = mul i32 %353, %76
  %355 = add i32 %lsr.iv, %354
  %356 = add i32 %355, 1
  %357 = sext i32 %356 to i64
  %358 = getelementptr float, float* %350, i64 %357
  store float %349, float* %358, align 4
  %359 = add nsw i32 %.01929, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond45.not = icmp eq i32 %21, %359
  br i1 %exitcond45.not, label %after_for.loopexit, label %for_loop_body5.lr.ph

for_loop_body13:                                  ; preds = %true_block.7, %after_if.6.1
  %360 = load float, float* %40, align 4
  %361 = load float, float* %41, align 4
  %362 = fcmp reassoc ninf nsz olt float %360, %361
  br i1 %362, label %true_block17, label %after_if19

true_block17:                                     ; preds = %for_loop_body13
  store float %360, float* %41, align 4
  store float %361, float* %40, align 4
  br label %after_if19

after_if19:                                       ; preds = %true_block17, %for_loop_body13
  %363 = load float, float* %39, align 4
  %364 = load float, float* %41, align 4
  %365 = fcmp reassoc ninf nsz olt float %363, %364
  br i1 %365, label %true_block17.182, label %after_if19.184

true_block17.182:                                 ; preds = %after_if19
  store float %363, float* %41, align 4
  store float %364, float* %39, align 4
  br label %after_if19.184

after_if19.184:                                   ; preds = %true_block17.182, %after_if19
  %366 = load float, float* %38, align 4
  %367 = load float, float* %41, align 4
  %368 = fcmp reassoc ninf nsz olt float %366, %367
  br i1 %368, label %true_block17.287, label %after_if19.289

true_block17.287:                                 ; preds = %after_if19.184
  store float %366, float* %41, align 4
  store float %367, float* %38, align 4
  br label %after_if19.289

after_if19.289:                                   ; preds = %true_block17.287, %after_if19.184
  %369 = load float, float* %37, align 4
  %370 = load float, float* %41, align 4
  %371 = fcmp reassoc ninf nsz olt float %369, %370
  br i1 %371, label %true_block17.392, label %after_if19.394

true_block17.392:                                 ; preds = %after_if19.289
  store float %369, float* %41, align 4
  store float %370, float* %37, align 4
  br label %after_if19.394

after_if19.394:                                   ; preds = %true_block17.392, %after_if19.289
  %372 = load float, float* %36, align 4
  %373 = load float, float* %41, align 4
  %374 = fcmp reassoc ninf nsz olt float %372, %373
  br i1 %374, label %true_block17.497, label %after_if19.499

true_block17.497:                                 ; preds = %after_if19.394
  store float %372, float* %41, align 4
  store float %373, float* %36, align 4
  br label %after_if19.499

after_if19.499:                                   ; preds = %true_block17.497, %after_if19.394
  %375 = load float, float* %35, align 4
  %376 = load float, float* %41, align 4
  %377 = fcmp reassoc ninf nsz olt float %375, %376
  br i1 %377, label %true_block17.5102, label %after_if19.5104

true_block17.5102:                                ; preds = %after_if19.499
  store float %375, float* %41, align 4
  store float %376, float* %35, align 4
  br label %after_if19.5104

after_if19.5104:                                  ; preds = %true_block17.5102, %after_if19.499
  %378 = load float, float* %34, align 4
  %379 = load float, float* %41, align 4
  %380 = fcmp reassoc ninf nsz olt float %378, %379
  br i1 %380, label %true_block17.6107, label %after_if19.6109

true_block17.6107:                                ; preds = %after_if19.5104
  store float %378, float* %41, align 4
  store float %379, float* %34, align 4
  br label %after_if19.6109

after_if19.6109:                                  ; preds = %true_block17.6107, %after_if19.5104
  %381 = load float, float* %41, align 4
  %382 = fcmp reassoc ninf nsz olt float %151, %381
  br i1 %382, label %true_block17.7111, label %after_if19.7

true_block17.7111:                                ; preds = %after_if19.6109
  store float %151, float* %41, align 4
  store float %381, float* %33, align 4
  br label %after_if19.7

after_if19.7:                                     ; preds = %true_block17.7111, %after_if19.6109
  %383 = load float, float* %39, align 4
  %384 = load float, float* %40, align 4
  %385 = fcmp reassoc ninf nsz olt float %383, %384
  br i1 %385, label %true_block17.1, label %after_if19.1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

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
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }

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
