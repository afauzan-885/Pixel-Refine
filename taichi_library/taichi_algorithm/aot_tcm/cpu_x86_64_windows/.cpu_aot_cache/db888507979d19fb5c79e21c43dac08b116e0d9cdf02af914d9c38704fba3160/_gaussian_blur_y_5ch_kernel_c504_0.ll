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
define void @_gaussian_blur_y_5ch_kernel_c504_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 4
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = mul i32 %14, %10
  %21 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %21, i64 0, i32 14
  %23 = bitcast i8** %22 to i32**
  %24 = load i32*, i32** %23, align 8
  store i32 %20, i32* %24, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_y_5ch_kernel_c504_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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
  %3 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %25 = load float*, float** %24, align 8
  %26 = icmp sgt i32 %23, 0
  %27 = icmp sgt i32 %23, 1
  %28 = icmp sgt i32 %23, 2
  %29 = icmp sgt i32 %23, 3
  %30 = icmp sgt i32 %23, 4
  %31 = icmp sgt i32 %23, 5
  %32 = icmp sgt i32 %23, 6
  %33 = icmp sgt i32 %23, 7
  %34 = icmp sgt i32 %23, 8
  %35 = icmp sgt i32 %23, 9
  %36 = icmp sgt i32 %23, 10
  %37 = icmp sgt i32 %23, 11
  %38 = icmp sgt i32 %23, 12
  %39 = icmp sgt i32 %23, 13
  %40 = icmp sgt i32 %23, 14
  %41 = icmp sgt i32 %23, 15
  %42 = icmp sgt i32 %23, 16
  %43 = icmp sgt i32 %23, 17
  %44 = icmp sgt i32 %23, 18
  %45 = icmp sgt i32 %23, 19
  %46 = icmp slt i32 %17, %19
  br i1 %46, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %47 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %48 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %49 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %50 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %51 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %52 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if57, %for_loop_body.lr.ph
  %.0223284 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %1377, %after_if57 ]
  %53 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %53, i64 0, i32 14
  %55 = load i8*, i8** %54, align 8
  %56 = getelementptr inbounds i8, i8* %55, i64 4
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = sdiv i32 %.0223284, %58
  %60 = mul i32 %59, %58
  %61 = xor i32 %58, %.0223284
  %62 = icmp slt i32 %61, 0
  %63 = icmp ne i32 %.0223284, 0
  %64 = icmp ne i32 %.0223284, %60
  %65 = and i1 %63, %62
  %66 = and i1 %65, %64
  %.neg224 = sext i1 %66 to i32
  %67 = load float*, float** %47, align 8
  %68 = load i32, i32* %48, align 4
  %69 = load i32, i32* %49, align 4
  %70 = add i32 %59, %.neg224
  %71 = mul i32 %70, %58
  %72 = insertelement <2 x i32> poison, i32 %.0223284, i64 0
  %73 = insertelement <2 x i32> poison, i32 %71, i64 0
  %74 = sub <2 x i32> %72, %73
  %75 = extractelement <2 x i32> %74, i64 0
  %76 = mul i32 %68, %70
  %77 = add i32 %75, %76
  %78 = mul i32 %77, %69
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, float* %67, i64 %79
  %81 = load float, float* %80, align 4
  %82 = load float, float* %25, align 4
  %83 = fmul reassoc ninf nsz float %82, %81
  %84 = insertelement <4 x i32> poison, i32 %78, i64 0
  %shuffle349 = shufflevector <4 x i32> %84, <4 x i32> poison, <4 x i32> zeroinitializer
  %85 = add <4 x i32> %shuffle349, <i32 1, i32 2, i32 3, i32 4>
  %86 = sext <4 x i32> %85 to <4 x i64>
  %87 = insertelement <4 x float*> poison, float* %67, i64 0
  %shuffle348 = shufflevector <4 x float*> %87, <4 x float*> poison, <4 x i32> zeroinitializer
  %88 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %86
  %89 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %88, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %90 = insertelement <4 x float> poison, float %82, i64 0
  %shuffle350 = shufflevector <4 x float> %90, <4 x float> poison, <4 x i32> zeroinitializer
  %91 = fmul reassoc ninf nsz <4 x float> %89, %shuffle350
  %92 = insertelement <2 x float> poison, float %83, i64 0
  %93 = insertelement <2 x float> %92, float %82, i64 1
  br i1 %26, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if57
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %94 = load float*, float** %24, align 8
  %95 = getelementptr float, float* %94, i64 1
  %96 = load float, float* %95, align 4
  %97 = insertelement <2 x i32> poison, i32 %70, i64 0
  %98 = shufflevector <2 x i32> %97, <2 x i32> poison, <2 x i32> zeroinitializer
  %99 = add <2 x i32> %98, <i32 1, i32 -1>
  %100 = getelementptr inbounds i8, i8* %55, i64 8
  %101 = bitcast i8* %100 to i32*
  %102 = load i32, i32* %101, align 4
  %103 = add i32 %102, -1
  %104 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %99, i1 true)
  %105 = insertelement <2 x i32> poison, i32 %103, i64 0
  %106 = shufflevector <2 x i32> %105, <2 x i32> poison, <2 x i32> zeroinitializer
  %107 = sub <2 x i32> %104, %106
  %108 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %107, <2 x i32> zeroinitializer)
  %109 = mul <2 x i32> %108, <i32 -2, i32 -2>
  %110 = add <2 x i32> %109, %104
  %111 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %110, <2 x i32> zeroinitializer)
  %112 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %106, <2 x i32> %111)
  %113 = insertelement <2 x i32> poison, i32 %68, i64 0
  %114 = shufflevector <2 x i32> %113, <2 x i32> poison, <2 x i32> zeroinitializer
  %115 = mul <2 x i32> %112, %114
  %116 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %117 = add <2 x i32> %115, %116
  %118 = insertelement <2 x i32> poison, i32 %69, i64 0
  %119 = shufflevector <2 x i32> %118, <2 x i32> poison, <2 x i32> zeroinitializer
  %120 = mul <2 x i32> %117, %119
  %121 = sext <2 x i32> %120 to <2 x i64>
  %122 = insertelement <2 x float*> poison, float* %67, i64 0
  %123 = shufflevector <2 x float*> %122, <2 x float*> poison, <2 x i32> zeroinitializer
  %124 = getelementptr float, <2 x float*> %123, <2 x i64> %121
  %125 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %124, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift = shufflevector <2 x float> %125, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %126 = fadd reassoc ninf nsz <2 x float> %125, %shift
  %shuffle346 = shufflevector <2 x i32> %120, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %127 = add <4 x i32> %shuffle346, <i32 1, i32 2, i32 3, i32 4>
  %128 = sext <4 x i32> %127 to <4 x i64>
  %129 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %128
  %130 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %129, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle344 = shufflevector <2 x i32> %120, <2 x i32> poison, <4 x i32> zeroinitializer
  %131 = add <4 x i32> %shuffle344, <i32 1, i32 2, i32 3, i32 4>
  %132 = sext <4 x i32> %131 to <4 x i64>
  %133 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %132
  %134 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %133, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %135 = fadd reassoc ninf nsz <4 x float> %134, %130
  %136 = insertelement <4 x float> poison, float %96, i64 0
  %shuffle347 = shufflevector <4 x float> %136, <4 x float> poison, <4 x i32> zeroinitializer
  %137 = fmul reassoc ninf nsz <4 x float> %135, %shuffle347
  %138 = fadd reassoc ninf nsz <4 x float> %137, %91
  %139 = insertelement <2 x float> %126, float 2.000000e+00, i64 1
  %140 = insertelement <2 x float> poison, float %96, i64 0
  %141 = shufflevector <2 x float> %140, <2 x float> poison, <2 x i32> zeroinitializer
  %142 = fmul reassoc ninf nsz <2 x float> %139, %141
  %143 = fadd reassoc ninf nsz <2 x float> %142, %93
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %144 = phi <2 x float> [ %143, %true_block ], [ %93, %for_loop_body ]
  %145 = phi <4 x float> [ %138, %true_block ], [ %91, %for_loop_body ]
  br i1 %27, label %true_block1, label %after_if3

true_block1:                                      ; preds = %after_if
  %146 = load float*, float** %24, align 8
  %147 = getelementptr float, float* %146, i64 2
  %148 = load float, float* %147, align 4
  %149 = insertelement <2 x i32> poison, i32 %70, i64 0
  %150 = shufflevector <2 x i32> %149, <2 x i32> poison, <2 x i32> zeroinitializer
  %151 = add <2 x i32> %150, <i32 2, i32 -2>
  %152 = getelementptr inbounds i8, i8* %55, i64 8
  %153 = bitcast i8* %152 to i32*
  %154 = load i32, i32* %153, align 4
  %155 = add i32 %154, -1
  %156 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %151, i1 true)
  %157 = insertelement <2 x i32> poison, i32 %155, i64 0
  %158 = shufflevector <2 x i32> %157, <2 x i32> poison, <2 x i32> zeroinitializer
  %159 = sub <2 x i32> %156, %158
  %160 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %159, <2 x i32> zeroinitializer)
  %161 = mul <2 x i32> %160, <i32 -2, i32 -2>
  %162 = add <2 x i32> %161, %156
  %163 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %162, <2 x i32> zeroinitializer)
  %164 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %158, <2 x i32> %163)
  %165 = insertelement <2 x i32> poison, i32 %68, i64 0
  %166 = shufflevector <2 x i32> %165, <2 x i32> poison, <2 x i32> zeroinitializer
  %167 = mul <2 x i32> %164, %166
  %168 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %169 = add <2 x i32> %167, %168
  %170 = insertelement <2 x i32> poison, i32 %69, i64 0
  %171 = shufflevector <2 x i32> %170, <2 x i32> poison, <2 x i32> zeroinitializer
  %172 = mul <2 x i32> %169, %171
  %173 = extractelement <2 x i32> %172, i64 1
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, float* %67, i64 %174
  %176 = load float, float* %175, align 4
  %177 = extractelement <2 x i32> %172, i64 0
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %67, i64 %178
  %180 = load float, float* %179, align 4
  %181 = fadd reassoc ninf nsz float %180, %176
  %182 = add <2 x i32> %172, <i32 1, i32 1>
  %183 = extractelement <2 x i32> %182, i64 1
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, float* %67, i64 %184
  %186 = load float, float* %185, align 4
  %187 = extractelement <2 x i32> %182, i64 0
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, float* %67, i64 %188
  %190 = load float, float* %189, align 4
  %191 = shufflevector <2 x i32> %172, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %192 = add <2 x i32> %191, <i32 2, i32 3>
  %193 = sext <2 x i32> %192 to <2 x i64>
  %194 = insertelement <2 x float*> poison, float* %67, i64 0
  %195 = shufflevector <2 x float*> %194, <2 x float*> poison, <2 x i32> zeroinitializer
  %196 = getelementptr float, <2 x float*> %195, <2 x i64> %193
  %197 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %196, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %198 = shufflevector <2 x i32> %172, <2 x i32> undef, <2 x i32> zeroinitializer
  %199 = add <2 x i32> %198, <i32 2, i32 3>
  %200 = sext <2 x i32> %199 to <2 x i64>
  %201 = getelementptr float, <2 x float*> %195, <2 x i64> %200
  %202 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %201, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %203 = add <2 x i32> %172, <i32 4, i32 4>
  %204 = sext <2 x i32> %203 to <2 x i64>
  %205 = getelementptr float, <2 x float*> %195, <2 x i64> %204
  %206 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %205, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %207 = shufflevector <2 x float> %206, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %208 = insertelement <4 x float> poison, float %190, i64 0
  %209 = shufflevector <2 x float> %202, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %210 = shufflevector <4 x float> %208, <4 x float> %209, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %211 = shufflevector <4 x float> %210, <4 x float> %207, <4 x i32> <i32 0, i32 1, i32 2, i32 4>
  %212 = insertelement <4 x float> poison, float %186, i64 0
  %213 = shufflevector <2 x float> %197, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %214 = shufflevector <4 x float> %212, <4 x float> %213, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %215 = shufflevector <4 x float> %214, <4 x float> %207, <4 x i32> <i32 0, i32 1, i32 2, i32 5>
  %216 = fadd reassoc ninf nsz <4 x float> %211, %215
  %217 = insertelement <4 x float> poison, float %148, i64 0
  %shuffle342 = shufflevector <4 x float> %217, <4 x float> poison, <4 x i32> zeroinitializer
  %218 = fmul reassoc ninf nsz <4 x float> %216, %shuffle342
  %219 = fadd reassoc ninf nsz <4 x float> %218, %145
  %220 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %181, i64 0
  %221 = insertelement <2 x float> poison, float %148, i64 0
  %222 = shufflevector <2 x float> %221, <2 x float> poison, <2 x i32> zeroinitializer
  %223 = fmul reassoc ninf nsz <2 x float> %220, %222
  %224 = fadd reassoc ninf nsz <2 x float> %223, %144
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %after_if
  %225 = phi <4 x float> [ %219, %true_block1 ], [ %145, %after_if ]
  %226 = phi <2 x float> [ %224, %true_block1 ], [ %144, %after_if ]
  br i1 %28, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %227 = load float*, float** %24, align 8
  %228 = getelementptr float, float* %227, i64 3
  %229 = load float, float* %228, align 4
  %230 = insertelement <2 x i32> poison, i32 %70, i64 0
  %231 = shufflevector <2 x i32> %230, <2 x i32> poison, <2 x i32> zeroinitializer
  %232 = add <2 x i32> %231, <i32 3, i32 -3>
  %233 = getelementptr inbounds i8, i8* %55, i64 8
  %234 = bitcast i8* %233 to i32*
  %235 = load i32, i32* %234, align 4
  %236 = add i32 %235, -1
  %237 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %232, i1 true)
  %238 = insertelement <2 x i32> poison, i32 %236, i64 0
  %239 = shufflevector <2 x i32> %238, <2 x i32> poison, <2 x i32> zeroinitializer
  %240 = sub <2 x i32> %237, %239
  %241 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %240, <2 x i32> zeroinitializer)
  %242 = mul <2 x i32> %241, <i32 -2, i32 -2>
  %243 = add <2 x i32> %242, %237
  %244 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %243, <2 x i32> zeroinitializer)
  %245 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %239, <2 x i32> %244)
  %246 = insertelement <2 x i32> poison, i32 %68, i64 0
  %247 = shufflevector <2 x i32> %246, <2 x i32> poison, <2 x i32> zeroinitializer
  %248 = mul <2 x i32> %245, %247
  %249 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %250 = add <2 x i32> %248, %249
  %251 = insertelement <2 x i32> poison, i32 %69, i64 0
  %252 = shufflevector <2 x i32> %251, <2 x i32> poison, <2 x i32> zeroinitializer
  %253 = mul <2 x i32> %250, %252
  %254 = sext <2 x i32> %253 to <2 x i64>
  %255 = insertelement <2 x float*> poison, float* %67, i64 0
  %256 = shufflevector <2 x float*> %255, <2 x float*> poison, <2 x i32> zeroinitializer
  %257 = getelementptr float, <2 x float*> %256, <2 x i64> %254
  %258 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %257, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift351 = shufflevector <2 x float> %258, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %259 = fadd reassoc ninf nsz <2 x float> %258, %shift351
  %260 = shufflevector <2 x i32> %253, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %261 = add <4 x i32> %260, <i32 1, i32 2, i32 3, i32 4>
  %262 = sext <4 x i32> %261 to <4 x i64>
  %263 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %262
  %264 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %263, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %265 = shufflevector <2 x i32> %253, <2 x i32> undef, <4 x i32> zeroinitializer
  %266 = add <4 x i32> %265, <i32 1, i32 2, i32 3, i32 4>
  %267 = sext <4 x i32> %266 to <4 x i64>
  %268 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %267
  %269 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %268, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %270 = fadd reassoc ninf nsz <4 x float> %269, %264
  %271 = insertelement <4 x float> poison, float %229, i64 0
  %shuffle341 = shufflevector <4 x float> %271, <4 x float> poison, <4 x i32> zeroinitializer
  %272 = fmul reassoc ninf nsz <4 x float> %270, %shuffle341
  %273 = fadd reassoc ninf nsz <4 x float> %272, %225
  %274 = insertelement <2 x float> %259, float 2.000000e+00, i64 1
  %275 = insertelement <2 x float> poison, float %229, i64 0
  %276 = shufflevector <2 x float> %275, <2 x float> poison, <2 x i32> zeroinitializer
  %277 = fmul reassoc ninf nsz <2 x float> %274, %276
  %278 = fadd reassoc ninf nsz <2 x float> %277, %226
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %279 = phi <4 x float> [ %273, %true_block4 ], [ %225, %after_if3 ]
  %280 = phi <2 x float> [ %278, %true_block4 ], [ %226, %after_if3 ]
  br i1 %29, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %281 = load float*, float** %24, align 8
  %282 = getelementptr float, float* %281, i64 4
  %283 = load float, float* %282, align 4
  %284 = insertelement <2 x i32> poison, i32 %70, i64 0
  %285 = shufflevector <2 x i32> %284, <2 x i32> poison, <2 x i32> zeroinitializer
  %286 = add <2 x i32> %285, <i32 4, i32 -4>
  %287 = getelementptr inbounds i8, i8* %55, i64 8
  %288 = bitcast i8* %287 to i32*
  %289 = load i32, i32* %288, align 4
  %290 = add i32 %289, -1
  %291 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %286, i1 true)
  %292 = insertelement <2 x i32> poison, i32 %290, i64 0
  %293 = shufflevector <2 x i32> %292, <2 x i32> poison, <2 x i32> zeroinitializer
  %294 = sub <2 x i32> %291, %293
  %295 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %294, <2 x i32> zeroinitializer)
  %296 = mul <2 x i32> %295, <i32 -2, i32 -2>
  %297 = add <2 x i32> %296, %291
  %298 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %297, <2 x i32> zeroinitializer)
  %299 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %293, <2 x i32> %298)
  %300 = insertelement <2 x i32> poison, i32 %68, i64 0
  %301 = shufflevector <2 x i32> %300, <2 x i32> poison, <2 x i32> zeroinitializer
  %302 = mul <2 x i32> %299, %301
  %303 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %304 = add <2 x i32> %302, %303
  %305 = insertelement <2 x i32> poison, i32 %69, i64 0
  %306 = shufflevector <2 x i32> %305, <2 x i32> poison, <2 x i32> zeroinitializer
  %307 = mul <2 x i32> %304, %306
  %308 = sext <2 x i32> %307 to <2 x i64>
  %309 = insertelement <2 x float*> poison, float* %67, i64 0
  %310 = shufflevector <2 x float*> %309, <2 x float*> poison, <2 x i32> zeroinitializer
  %311 = getelementptr float, <2 x float*> %310, <2 x i64> %308
  %312 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %311, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift352 = shufflevector <2 x float> %312, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %313 = fadd reassoc ninf nsz <2 x float> %312, %shift352
  %314 = add <2 x i32> %307, <i32 1, i32 1>
  %315 = extractelement <2 x i32> %314, i64 1
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, float* %67, i64 %316
  %318 = extractelement <2 x i32> %314, i64 0
  %319 = sext i32 %318 to i64
  %320 = getelementptr float, float* %67, i64 %319
  %321 = shufflevector <2 x i32> %307, <2 x i32> undef, <4 x i32> <i32 1, i32 0, i32 1, i32 0>
  %322 = add <4 x i32> %321, <i32 2, i32 2, i32 3, i32 3>
  %323 = extractelement <4 x i32> %322, i64 0
  %324 = sext i32 %323 to i64
  %325 = getelementptr float, float* %67, i64 %324
  %326 = extractelement <4 x i32> %322, i64 1
  %327 = sext i32 %326 to i64
  %328 = getelementptr float, float* %67, i64 %327
  %329 = extractelement <4 x i32> %322, i64 2
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, float* %67, i64 %330
  %332 = extractelement <4 x i32> %322, i64 3
  %333 = sext i32 %332 to i64
  %334 = getelementptr float, float* %67, i64 %333
  %335 = add <2 x i32> %307, <i32 4, i32 4>
  %336 = extractelement <2 x i32> %335, i64 1
  %337 = sext i32 %336 to i64
  %338 = getelementptr float, float* %67, i64 %337
  %339 = extractelement <2 x i32> %335, i64 0
  %340 = sext i32 %339 to i64
  %341 = getelementptr float, float* %67, i64 %340
  %342 = insertelement <4 x float*> poison, float* %317, i64 0
  %343 = insertelement <4 x float*> %342, float* %325, i64 1
  %344 = insertelement <4 x float*> %343, float* %331, i64 2
  %345 = insertelement <4 x float*> %344, float* %338, i64 3
  %346 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %345, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %347 = insertelement <4 x float*> poison, float* %320, i64 0
  %348 = insertelement <4 x float*> %347, float* %328, i64 1
  %349 = insertelement <4 x float*> %348, float* %334, i64 2
  %350 = insertelement <4 x float*> %349, float* %341, i64 3
  %351 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %350, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %352 = fadd reassoc ninf nsz <4 x float> %351, %346
  %353 = insertelement <4 x float> poison, float %283, i64 0
  %shuffle338 = shufflevector <4 x float> %353, <4 x float> poison, <4 x i32> zeroinitializer
  %354 = fmul reassoc ninf nsz <4 x float> %352, %shuffle338
  %355 = fadd reassoc ninf nsz <4 x float> %354, %279
  %356 = insertelement <2 x float> %313, float 2.000000e+00, i64 1
  %357 = insertelement <2 x float> poison, float %283, i64 0
  %358 = shufflevector <2 x float> %357, <2 x float> poison, <2 x i32> zeroinitializer
  %359 = fmul reassoc ninf nsz <2 x float> %356, %358
  %360 = fadd reassoc ninf nsz <2 x float> %359, %280
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %361 = phi <4 x float> [ %355, %true_block7 ], [ %279, %after_if6 ]
  %362 = phi <2 x float> [ %360, %true_block7 ], [ %280, %after_if6 ]
  br i1 %30, label %true_block10, label %after_if12

true_block10:                                     ; preds = %after_if9
  %363 = load float*, float** %24, align 8
  %364 = getelementptr float, float* %363, i64 5
  %365 = load float, float* %364, align 4
  %366 = insertelement <2 x i32> poison, i32 %70, i64 0
  %367 = shufflevector <2 x i32> %366, <2 x i32> poison, <2 x i32> zeroinitializer
  %368 = add <2 x i32> %367, <i32 5, i32 -5>
  %369 = getelementptr inbounds i8, i8* %55, i64 8
  %370 = bitcast i8* %369 to i32*
  %371 = load i32, i32* %370, align 4
  %372 = add i32 %371, -1
  %373 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %368, i1 true)
  %374 = insertelement <2 x i32> poison, i32 %372, i64 0
  %375 = shufflevector <2 x i32> %374, <2 x i32> poison, <2 x i32> zeroinitializer
  %376 = sub <2 x i32> %373, %375
  %377 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %376, <2 x i32> zeroinitializer)
  %378 = mul <2 x i32> %377, <i32 -2, i32 -2>
  %379 = add <2 x i32> %378, %373
  %380 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %379, <2 x i32> zeroinitializer)
  %381 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %375, <2 x i32> %380)
  %382 = insertelement <2 x i32> poison, i32 %68, i64 0
  %383 = shufflevector <2 x i32> %382, <2 x i32> poison, <2 x i32> zeroinitializer
  %384 = mul <2 x i32> %381, %383
  %385 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %386 = add <2 x i32> %384, %385
  %387 = insertelement <2 x i32> poison, i32 %69, i64 0
  %388 = shufflevector <2 x i32> %387, <2 x i32> poison, <2 x i32> zeroinitializer
  %389 = mul <2 x i32> %386, %388
  %390 = sext <2 x i32> %389 to <2 x i64>
  %391 = insertelement <2 x float*> poison, float* %67, i64 0
  %392 = shufflevector <2 x float*> %391, <2 x float*> poison, <2 x i32> zeroinitializer
  %393 = getelementptr float, <2 x float*> %392, <2 x i64> %390
  %394 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %393, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift353 = shufflevector <2 x float> %394, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %395 = fadd reassoc ninf nsz <2 x float> %394, %shift353
  %396 = shufflevector <2 x i32> %389, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %397 = add <4 x i32> %396, <i32 1, i32 2, i32 3, i32 4>
  %398 = sext <4 x i32> %397 to <4 x i64>
  %399 = shufflevector <2 x i32> %389, <2 x i32> undef, <4 x i32> zeroinitializer
  %400 = add <4 x i32> %399, <i32 1, i32 2, i32 3, i32 4>
  %401 = sext <4 x i32> %400 to <4 x i64>
  %402 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %398
  %403 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %402, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %404 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %401
  %405 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %404, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %406 = fadd reassoc ninf nsz <4 x float> %405, %403
  %407 = insertelement <4 x float> poison, float %365, i64 0
  %shuffle337 = shufflevector <4 x float> %407, <4 x float> poison, <4 x i32> zeroinitializer
  %408 = fmul reassoc ninf nsz <4 x float> %406, %shuffle337
  %409 = fadd reassoc ninf nsz <4 x float> %408, %361
  %410 = insertelement <2 x float> %395, float 2.000000e+00, i64 1
  %411 = insertelement <2 x float> poison, float %365, i64 0
  %412 = shufflevector <2 x float> %411, <2 x float> poison, <2 x i32> zeroinitializer
  %413 = fmul reassoc ninf nsz <2 x float> %410, %412
  %414 = fadd reassoc ninf nsz <2 x float> %413, %362
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %415 = phi <4 x float> [ %409, %true_block10 ], [ %361, %after_if9 ]
  %416 = phi <2 x float> [ %414, %true_block10 ], [ %362, %after_if9 ]
  br i1 %31, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if12
  %417 = load float*, float** %24, align 8
  %418 = getelementptr float, float* %417, i64 6
  %419 = load float, float* %418, align 4
  %420 = insertelement <2 x i32> poison, i32 %70, i64 0
  %421 = shufflevector <2 x i32> %420, <2 x i32> poison, <2 x i32> zeroinitializer
  %422 = add <2 x i32> %421, <i32 6, i32 -6>
  %423 = getelementptr inbounds i8, i8* %55, i64 8
  %424 = bitcast i8* %423 to i32*
  %425 = load i32, i32* %424, align 4
  %426 = add i32 %425, -1
  %427 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %422, i1 true)
  %428 = insertelement <2 x i32> poison, i32 %426, i64 0
  %429 = shufflevector <2 x i32> %428, <2 x i32> poison, <2 x i32> zeroinitializer
  %430 = sub <2 x i32> %427, %429
  %431 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %430, <2 x i32> zeroinitializer)
  %432 = mul <2 x i32> %431, <i32 -2, i32 -2>
  %433 = add <2 x i32> %432, %427
  %434 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %433, <2 x i32> zeroinitializer)
  %435 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %429, <2 x i32> %434)
  %436 = insertelement <2 x i32> poison, i32 %68, i64 0
  %437 = shufflevector <2 x i32> %436, <2 x i32> poison, <2 x i32> zeroinitializer
  %438 = mul <2 x i32> %435, %437
  %439 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %440 = add <2 x i32> %438, %439
  %441 = insertelement <2 x i32> poison, i32 %69, i64 0
  %442 = shufflevector <2 x i32> %441, <2 x i32> poison, <2 x i32> zeroinitializer
  %443 = mul <2 x i32> %440, %442
  %444 = sext <2 x i32> %443 to <2 x i64>
  %445 = insertelement <2 x float*> poison, float* %67, i64 0
  %446 = shufflevector <2 x float*> %445, <2 x float*> poison, <2 x i32> zeroinitializer
  %447 = getelementptr float, <2 x float*> %446, <2 x i64> %444
  %448 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %447, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift354 = shufflevector <2 x float> %448, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %449 = fadd reassoc ninf nsz <2 x float> %448, %shift354
  %shuffle333 = shufflevector <2 x i32> %443, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %450 = add <4 x i32> %shuffle333, <i32 1, i32 2, i32 3, i32 4>
  %451 = sext <4 x i32> %450 to <4 x i64>
  %452 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %451
  %453 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %452, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle331 = shufflevector <2 x i32> %443, <2 x i32> poison, <4 x i32> zeroinitializer
  %454 = add <4 x i32> %shuffle331, <i32 1, i32 2, i32 3, i32 4>
  %455 = sext <4 x i32> %454 to <4 x i64>
  %456 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %455
  %457 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %456, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %458 = fadd reassoc ninf nsz <4 x float> %457, %453
  %459 = insertelement <4 x float> poison, float %419, i64 0
  %shuffle334 = shufflevector <4 x float> %459, <4 x float> poison, <4 x i32> zeroinitializer
  %460 = fmul reassoc ninf nsz <4 x float> %458, %shuffle334
  %461 = fadd reassoc ninf nsz <4 x float> %460, %415
  %462 = insertelement <2 x float> %449, float 2.000000e+00, i64 1
  %463 = insertelement <2 x float> poison, float %419, i64 0
  %464 = shufflevector <2 x float> %463, <2 x float> poison, <2 x i32> zeroinitializer
  %465 = fmul reassoc ninf nsz <2 x float> %462, %464
  %466 = fadd reassoc ninf nsz <2 x float> %465, %416
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if12
  %467 = phi <4 x float> [ %461, %true_block13 ], [ %415, %after_if12 ]
  %468 = phi <2 x float> [ %466, %true_block13 ], [ %416, %after_if12 ]
  br i1 %32, label %true_block16, label %after_if18

true_block16:                                     ; preds = %after_if15
  %469 = load float*, float** %24, align 8
  %470 = getelementptr float, float* %469, i64 7
  %471 = load float, float* %470, align 4
  %472 = insertelement <2 x i32> poison, i32 %70, i64 0
  %473 = shufflevector <2 x i32> %472, <2 x i32> poison, <2 x i32> zeroinitializer
  %474 = add <2 x i32> %473, <i32 7, i32 -7>
  %475 = getelementptr inbounds i8, i8* %55, i64 8
  %476 = bitcast i8* %475 to i32*
  %477 = load i32, i32* %476, align 4
  %478 = add i32 %477, -1
  %479 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %474, i1 true)
  %480 = insertelement <2 x i32> poison, i32 %478, i64 0
  %481 = shufflevector <2 x i32> %480, <2 x i32> poison, <2 x i32> zeroinitializer
  %482 = sub <2 x i32> %479, %481
  %483 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %482, <2 x i32> zeroinitializer)
  %484 = mul <2 x i32> %483, <i32 -2, i32 -2>
  %485 = add <2 x i32> %484, %479
  %486 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %485, <2 x i32> zeroinitializer)
  %487 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %481, <2 x i32> %486)
  %488 = insertelement <2 x i32> poison, i32 %68, i64 0
  %489 = shufflevector <2 x i32> %488, <2 x i32> poison, <2 x i32> zeroinitializer
  %490 = mul <2 x i32> %487, %489
  %491 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %492 = add <2 x i32> %490, %491
  %493 = insertelement <2 x i32> poison, i32 %69, i64 0
  %494 = shufflevector <2 x i32> %493, <2 x i32> poison, <2 x i32> zeroinitializer
  %495 = mul <2 x i32> %492, %494
  %496 = sext <2 x i32> %495 to <2 x i64>
  %497 = insertelement <2 x float*> poison, float* %67, i64 0
  %498 = shufflevector <2 x float*> %497, <2 x float*> poison, <2 x i32> zeroinitializer
  %499 = getelementptr float, <2 x float*> %498, <2 x i64> %496
  %500 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %499, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift355 = shufflevector <2 x float> %500, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %501 = fadd reassoc ninf nsz <2 x float> %500, %shift355
  %shuffle328 = shufflevector <2 x i32> %495, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %502 = add <4 x i32> %shuffle328, <i32 1, i32 2, i32 3, i32 4>
  %503 = sext <4 x i32> %502 to <4 x i64>
  %504 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %503
  %505 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %504, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle326 = shufflevector <2 x i32> %495, <2 x i32> poison, <4 x i32> zeroinitializer
  %506 = add <4 x i32> %shuffle326, <i32 1, i32 2, i32 3, i32 4>
  %507 = sext <4 x i32> %506 to <4 x i64>
  %508 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %507
  %509 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %508, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %510 = fadd reassoc ninf nsz <4 x float> %509, %505
  %511 = insertelement <4 x float> poison, float %471, i64 0
  %shuffle329 = shufflevector <4 x float> %511, <4 x float> poison, <4 x i32> zeroinitializer
  %512 = fmul reassoc ninf nsz <4 x float> %510, %shuffle329
  %513 = fadd reassoc ninf nsz <4 x float> %512, %467
  %514 = insertelement <2 x float> %501, float 2.000000e+00, i64 1
  %515 = insertelement <2 x float> poison, float %471, i64 0
  %516 = shufflevector <2 x float> %515, <2 x float> poison, <2 x i32> zeroinitializer
  %517 = fmul reassoc ninf nsz <2 x float> %514, %516
  %518 = fadd reassoc ninf nsz <2 x float> %517, %468
  br label %after_if18

after_if18:                                       ; preds = %true_block16, %after_if15
  %519 = phi <2 x float> [ %518, %true_block16 ], [ %468, %after_if15 ]
  %520 = phi <4 x float> [ %513, %true_block16 ], [ %467, %after_if15 ]
  br i1 %33, label %true_block19, label %after_if21

true_block19:                                     ; preds = %after_if18
  %521 = load float*, float** %24, align 8
  %522 = getelementptr float, float* %521, i64 8
  %523 = load float, float* %522, align 4
  %524 = insertelement <2 x i32> poison, i32 %70, i64 0
  %525 = shufflevector <2 x i32> %524, <2 x i32> poison, <2 x i32> zeroinitializer
  %526 = add <2 x i32> %525, <i32 8, i32 -8>
  %527 = getelementptr inbounds i8, i8* %55, i64 8
  %528 = bitcast i8* %527 to i32*
  %529 = load i32, i32* %528, align 4
  %530 = add i32 %529, -1
  %531 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %526, i1 true)
  %532 = insertelement <2 x i32> poison, i32 %530, i64 0
  %533 = shufflevector <2 x i32> %532, <2 x i32> poison, <2 x i32> zeroinitializer
  %534 = sub <2 x i32> %531, %533
  %535 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %534, <2 x i32> zeroinitializer)
  %536 = mul <2 x i32> %535, <i32 -2, i32 -2>
  %537 = add <2 x i32> %536, %531
  %538 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %537, <2 x i32> zeroinitializer)
  %539 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %533, <2 x i32> %538)
  %540 = insertelement <2 x i32> poison, i32 %68, i64 0
  %541 = shufflevector <2 x i32> %540, <2 x i32> poison, <2 x i32> zeroinitializer
  %542 = mul <2 x i32> %539, %541
  %543 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %544 = add <2 x i32> %542, %543
  %545 = insertelement <2 x i32> poison, i32 %69, i64 0
  %546 = shufflevector <2 x i32> %545, <2 x i32> poison, <2 x i32> zeroinitializer
  %547 = mul <2 x i32> %544, %546
  %548 = extractelement <2 x i32> %547, i64 1
  %549 = sext i32 %548 to i64
  %550 = getelementptr float, float* %67, i64 %549
  %551 = load float, float* %550, align 4
  %552 = extractelement <2 x i32> %547, i64 0
  %553 = sext i32 %552 to i64
  %554 = getelementptr float, float* %67, i64 %553
  %555 = load float, float* %554, align 4
  %556 = fadd reassoc ninf nsz float %555, %551
  %557 = add <2 x i32> %547, <i32 1, i32 1>
  %558 = extractelement <2 x i32> %557, i64 1
  %559 = sext i32 %558 to i64
  %560 = getelementptr float, float* %67, i64 %559
  %561 = load float, float* %560, align 4
  %562 = extractelement <2 x i32> %557, i64 0
  %563 = sext i32 %562 to i64
  %564 = getelementptr float, float* %67, i64 %563
  %565 = load float, float* %564, align 4
  %566 = shufflevector <2 x i32> %547, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %567 = add <2 x i32> %566, <i32 2, i32 3>
  %568 = sext <2 x i32> %567 to <2 x i64>
  %569 = insertelement <2 x float*> poison, float* %67, i64 0
  %570 = shufflevector <2 x float*> %569, <2 x float*> poison, <2 x i32> zeroinitializer
  %571 = getelementptr float, <2 x float*> %570, <2 x i64> %568
  %572 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %571, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %573 = shufflevector <2 x i32> %547, <2 x i32> undef, <2 x i32> zeroinitializer
  %574 = add <2 x i32> %573, <i32 2, i32 3>
  %575 = sext <2 x i32> %574 to <2 x i64>
  %576 = getelementptr float, <2 x float*> %570, <2 x i64> %575
  %577 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %576, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %578 = add <2 x i32> %547, <i32 4, i32 4>
  %579 = sext <2 x i32> %578 to <2 x i64>
  %580 = getelementptr float, <2 x float*> %570, <2 x i64> %579
  %581 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %580, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %582 = shufflevector <2 x float> %581, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %583 = insertelement <4 x float> poison, float %565, i64 0
  %584 = shufflevector <2 x float> %577, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %585 = shufflevector <4 x float> %583, <4 x float> %584, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %586 = shufflevector <4 x float> %585, <4 x float> %582, <4 x i32> <i32 0, i32 1, i32 2, i32 4>
  %587 = insertelement <4 x float> poison, float %561, i64 0
  %588 = shufflevector <2 x float> %572, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %589 = shufflevector <4 x float> %587, <4 x float> %588, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %590 = shufflevector <4 x float> %589, <4 x float> %582, <4 x i32> <i32 0, i32 1, i32 2, i32 5>
  %591 = fadd reassoc ninf nsz <4 x float> %586, %590
  %592 = insertelement <4 x float> poison, float %523, i64 0
  %shuffle324 = shufflevector <4 x float> %592, <4 x float> poison, <4 x i32> zeroinitializer
  %593 = fmul reassoc ninf nsz <4 x float> %591, %shuffle324
  %594 = fadd reassoc ninf nsz <4 x float> %593, %520
  %595 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %556, i64 0
  %596 = insertelement <2 x float> poison, float %523, i64 0
  %597 = shufflevector <2 x float> %596, <2 x float> poison, <2 x i32> zeroinitializer
  %598 = fmul reassoc ninf nsz <2 x float> %595, %597
  %599 = fadd reassoc ninf nsz <2 x float> %598, %519
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if18
  %600 = phi <4 x float> [ %594, %true_block19 ], [ %520, %after_if18 ]
  %601 = phi <2 x float> [ %599, %true_block19 ], [ %519, %after_if18 ]
  br i1 %34, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if21
  %602 = load float*, float** %24, align 8
  %603 = getelementptr float, float* %602, i64 9
  %604 = load float, float* %603, align 4
  %605 = insertelement <2 x i32> poison, i32 %70, i64 0
  %606 = shufflevector <2 x i32> %605, <2 x i32> poison, <2 x i32> zeroinitializer
  %607 = add <2 x i32> %606, <i32 9, i32 -9>
  %608 = getelementptr inbounds i8, i8* %55, i64 8
  %609 = bitcast i8* %608 to i32*
  %610 = load i32, i32* %609, align 4
  %611 = add i32 %610, -1
  %612 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %607, i1 true)
  %613 = insertelement <2 x i32> poison, i32 %611, i64 0
  %614 = shufflevector <2 x i32> %613, <2 x i32> poison, <2 x i32> zeroinitializer
  %615 = sub <2 x i32> %612, %614
  %616 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %615, <2 x i32> zeroinitializer)
  %617 = mul <2 x i32> %616, <i32 -2, i32 -2>
  %618 = add <2 x i32> %617, %612
  %619 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %618, <2 x i32> zeroinitializer)
  %620 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %614, <2 x i32> %619)
  %621 = insertelement <2 x i32> poison, i32 %68, i64 0
  %622 = shufflevector <2 x i32> %621, <2 x i32> poison, <2 x i32> zeroinitializer
  %623 = mul <2 x i32> %620, %622
  %624 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %625 = add <2 x i32> %623, %624
  %626 = insertelement <2 x i32> poison, i32 %69, i64 0
  %627 = shufflevector <2 x i32> %626, <2 x i32> poison, <2 x i32> zeroinitializer
  %628 = mul <2 x i32> %625, %627
  %629 = sext <2 x i32> %628 to <2 x i64>
  %630 = insertelement <2 x float*> poison, float* %67, i64 0
  %631 = shufflevector <2 x float*> %630, <2 x float*> poison, <2 x i32> zeroinitializer
  %632 = getelementptr float, <2 x float*> %631, <2 x i64> %629
  %633 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %632, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift356 = shufflevector <2 x float> %633, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %634 = fadd reassoc ninf nsz <2 x float> %633, %shift356
  %635 = shufflevector <2 x i32> %628, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %636 = add <4 x i32> %635, <i32 1, i32 2, i32 3, i32 4>
  %637 = sext <4 x i32> %636 to <4 x i64>
  %638 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %637
  %639 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %638, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %640 = shufflevector <2 x i32> %628, <2 x i32> undef, <4 x i32> zeroinitializer
  %641 = add <4 x i32> %640, <i32 1, i32 2, i32 3, i32 4>
  %642 = sext <4 x i32> %641 to <4 x i64>
  %643 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %642
  %644 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %643, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %645 = fadd reassoc ninf nsz <4 x float> %644, %639
  %646 = insertelement <4 x float> poison, float %604, i64 0
  %shuffle323 = shufflevector <4 x float> %646, <4 x float> poison, <4 x i32> zeroinitializer
  %647 = fmul reassoc ninf nsz <4 x float> %645, %shuffle323
  %648 = fadd reassoc ninf nsz <4 x float> %647, %600
  %649 = insertelement <2 x float> %634, float 2.000000e+00, i64 1
  %650 = insertelement <2 x float> poison, float %604, i64 0
  %651 = shufflevector <2 x float> %650, <2 x float> poison, <2 x i32> zeroinitializer
  %652 = fmul reassoc ninf nsz <2 x float> %649, %651
  %653 = fadd reassoc ninf nsz <2 x float> %652, %601
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if21
  %654 = phi <4 x float> [ %648, %true_block22 ], [ %600, %after_if21 ]
  %655 = phi <2 x float> [ %653, %true_block22 ], [ %601, %after_if21 ]
  br i1 %35, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if24
  %656 = load float*, float** %24, align 8
  %657 = getelementptr float, float* %656, i64 10
  %658 = load float, float* %657, align 4
  %659 = insertelement <2 x i32> poison, i32 %70, i64 0
  %660 = shufflevector <2 x i32> %659, <2 x i32> poison, <2 x i32> zeroinitializer
  %661 = add <2 x i32> %660, <i32 10, i32 -10>
  %662 = getelementptr inbounds i8, i8* %55, i64 8
  %663 = bitcast i8* %662 to i32*
  %664 = load i32, i32* %663, align 4
  %665 = add i32 %664, -1
  %666 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %661, i1 true)
  %667 = insertelement <2 x i32> poison, i32 %665, i64 0
  %668 = shufflevector <2 x i32> %667, <2 x i32> poison, <2 x i32> zeroinitializer
  %669 = sub <2 x i32> %666, %668
  %670 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %669, <2 x i32> zeroinitializer)
  %671 = mul <2 x i32> %670, <i32 -2, i32 -2>
  %672 = add <2 x i32> %671, %666
  %673 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %672, <2 x i32> zeroinitializer)
  %674 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %668, <2 x i32> %673)
  %675 = insertelement <2 x i32> poison, i32 %68, i64 0
  %676 = shufflevector <2 x i32> %675, <2 x i32> poison, <2 x i32> zeroinitializer
  %677 = mul <2 x i32> %674, %676
  %678 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %679 = add <2 x i32> %677, %678
  %680 = insertelement <2 x i32> poison, i32 %69, i64 0
  %681 = shufflevector <2 x i32> %680, <2 x i32> poison, <2 x i32> zeroinitializer
  %682 = mul <2 x i32> %679, %681
  %683 = sext <2 x i32> %682 to <2 x i64>
  %684 = insertelement <2 x float*> poison, float* %67, i64 0
  %685 = shufflevector <2 x float*> %684, <2 x float*> poison, <2 x i32> zeroinitializer
  %686 = getelementptr float, <2 x float*> %685, <2 x i64> %683
  %687 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %686, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift357 = shufflevector <2 x float> %687, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %688 = fadd reassoc ninf nsz <2 x float> %687, %shift357
  %689 = add <2 x i32> %682, <i32 1, i32 1>
  %690 = extractelement <2 x i32> %689, i64 1
  %691 = sext i32 %690 to i64
  %692 = getelementptr float, float* %67, i64 %691
  %693 = extractelement <2 x i32> %689, i64 0
  %694 = sext i32 %693 to i64
  %695 = getelementptr float, float* %67, i64 %694
  %696 = shufflevector <2 x i32> %682, <2 x i32> undef, <4 x i32> <i32 1, i32 0, i32 1, i32 0>
  %697 = add <4 x i32> %696, <i32 2, i32 2, i32 3, i32 3>
  %698 = extractelement <4 x i32> %697, i64 0
  %699 = sext i32 %698 to i64
  %700 = getelementptr float, float* %67, i64 %699
  %701 = extractelement <4 x i32> %697, i64 1
  %702 = sext i32 %701 to i64
  %703 = getelementptr float, float* %67, i64 %702
  %704 = extractelement <4 x i32> %697, i64 2
  %705 = sext i32 %704 to i64
  %706 = getelementptr float, float* %67, i64 %705
  %707 = extractelement <4 x i32> %697, i64 3
  %708 = sext i32 %707 to i64
  %709 = getelementptr float, float* %67, i64 %708
  %710 = add <2 x i32> %682, <i32 4, i32 4>
  %711 = extractelement <2 x i32> %710, i64 1
  %712 = sext i32 %711 to i64
  %713 = getelementptr float, float* %67, i64 %712
  %714 = extractelement <2 x i32> %710, i64 0
  %715 = sext i32 %714 to i64
  %716 = getelementptr float, float* %67, i64 %715
  %717 = insertelement <4 x float*> poison, float* %692, i64 0
  %718 = insertelement <4 x float*> %717, float* %700, i64 1
  %719 = insertelement <4 x float*> %718, float* %706, i64 2
  %720 = insertelement <4 x float*> %719, float* %713, i64 3
  %721 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %720, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %722 = insertelement <4 x float*> poison, float* %695, i64 0
  %723 = insertelement <4 x float*> %722, float* %703, i64 1
  %724 = insertelement <4 x float*> %723, float* %709, i64 2
  %725 = insertelement <4 x float*> %724, float* %716, i64 3
  %726 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %725, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %727 = fadd reassoc ninf nsz <4 x float> %726, %721
  %728 = insertelement <4 x float> poison, float %658, i64 0
  %shuffle320 = shufflevector <4 x float> %728, <4 x float> poison, <4 x i32> zeroinitializer
  %729 = fmul reassoc ninf nsz <4 x float> %727, %shuffle320
  %730 = fadd reassoc ninf nsz <4 x float> %729, %654
  %731 = insertelement <2 x float> %688, float 2.000000e+00, i64 1
  %732 = insertelement <2 x float> poison, float %658, i64 0
  %733 = shufflevector <2 x float> %732, <2 x float> poison, <2 x i32> zeroinitializer
  %734 = fmul reassoc ninf nsz <2 x float> %731, %733
  %735 = fadd reassoc ninf nsz <2 x float> %734, %655
  br label %after_if27

after_if27:                                       ; preds = %true_block25, %after_if24
  %736 = phi <4 x float> [ %730, %true_block25 ], [ %654, %after_if24 ]
  %737 = phi <2 x float> [ %735, %true_block25 ], [ %655, %after_if24 ]
  br i1 %36, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %738 = load float*, float** %24, align 8
  %739 = getelementptr float, float* %738, i64 11
  %740 = load float, float* %739, align 4
  %741 = insertelement <2 x i32> poison, i32 %70, i64 0
  %742 = shufflevector <2 x i32> %741, <2 x i32> poison, <2 x i32> zeroinitializer
  %743 = add <2 x i32> %742, <i32 11, i32 -11>
  %744 = getelementptr inbounds i8, i8* %55, i64 8
  %745 = bitcast i8* %744 to i32*
  %746 = load i32, i32* %745, align 4
  %747 = add i32 %746, -1
  %748 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %743, i1 true)
  %749 = insertelement <2 x i32> poison, i32 %747, i64 0
  %750 = shufflevector <2 x i32> %749, <2 x i32> poison, <2 x i32> zeroinitializer
  %751 = sub <2 x i32> %748, %750
  %752 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %751, <2 x i32> zeroinitializer)
  %753 = mul <2 x i32> %752, <i32 -2, i32 -2>
  %754 = add <2 x i32> %753, %748
  %755 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %754, <2 x i32> zeroinitializer)
  %756 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %750, <2 x i32> %755)
  %757 = insertelement <2 x i32> poison, i32 %68, i64 0
  %758 = shufflevector <2 x i32> %757, <2 x i32> poison, <2 x i32> zeroinitializer
  %759 = mul <2 x i32> %756, %758
  %760 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %761 = add <2 x i32> %759, %760
  %762 = insertelement <2 x i32> poison, i32 %69, i64 0
  %763 = shufflevector <2 x i32> %762, <2 x i32> poison, <2 x i32> zeroinitializer
  %764 = mul <2 x i32> %761, %763
  %765 = sext <2 x i32> %764 to <2 x i64>
  %766 = insertelement <2 x float*> poison, float* %67, i64 0
  %767 = shufflevector <2 x float*> %766, <2 x float*> poison, <2 x i32> zeroinitializer
  %768 = getelementptr float, <2 x float*> %767, <2 x i64> %765
  %769 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %768, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift358 = shufflevector <2 x float> %769, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %770 = fadd reassoc ninf nsz <2 x float> %769, %shift358
  %771 = shufflevector <2 x i32> %764, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %772 = add <4 x i32> %771, <i32 1, i32 2, i32 3, i32 4>
  %773 = sext <4 x i32> %772 to <4 x i64>
  %774 = shufflevector <2 x i32> %764, <2 x i32> undef, <4 x i32> zeroinitializer
  %775 = add <4 x i32> %774, <i32 1, i32 2, i32 3, i32 4>
  %776 = sext <4 x i32> %775 to <4 x i64>
  %777 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %773
  %778 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %777, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %779 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %776
  %780 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %779, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %781 = fadd reassoc ninf nsz <4 x float> %780, %778
  %782 = insertelement <4 x float> poison, float %740, i64 0
  %shuffle319 = shufflevector <4 x float> %782, <4 x float> poison, <4 x i32> zeroinitializer
  %783 = fmul reassoc ninf nsz <4 x float> %781, %shuffle319
  %784 = fadd reassoc ninf nsz <4 x float> %783, %736
  %785 = insertelement <2 x float> %770, float 2.000000e+00, i64 1
  %786 = insertelement <2 x float> poison, float %740, i64 0
  %787 = shufflevector <2 x float> %786, <2 x float> poison, <2 x i32> zeroinitializer
  %788 = fmul reassoc ninf nsz <2 x float> %785, %787
  %789 = fadd reassoc ninf nsz <2 x float> %788, %737
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27
  %790 = phi <4 x float> [ %784, %true_block28 ], [ %736, %after_if27 ]
  %791 = phi <2 x float> [ %789, %true_block28 ], [ %737, %after_if27 ]
  br i1 %37, label %true_block31, label %after_if33

true_block31:                                     ; preds = %after_if30
  %792 = load float*, float** %24, align 8
  %793 = getelementptr float, float* %792, i64 12
  %794 = load float, float* %793, align 4
  %795 = insertelement <2 x i32> poison, i32 %70, i64 0
  %796 = shufflevector <2 x i32> %795, <2 x i32> poison, <2 x i32> zeroinitializer
  %797 = add <2 x i32> %796, <i32 12, i32 -12>
  %798 = getelementptr inbounds i8, i8* %55, i64 8
  %799 = bitcast i8* %798 to i32*
  %800 = load i32, i32* %799, align 4
  %801 = add i32 %800, -1
  %802 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %797, i1 true)
  %803 = insertelement <2 x i32> poison, i32 %801, i64 0
  %804 = shufflevector <2 x i32> %803, <2 x i32> poison, <2 x i32> zeroinitializer
  %805 = sub <2 x i32> %802, %804
  %806 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %805, <2 x i32> zeroinitializer)
  %807 = mul <2 x i32> %806, <i32 -2, i32 -2>
  %808 = add <2 x i32> %807, %802
  %809 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %808, <2 x i32> zeroinitializer)
  %810 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %804, <2 x i32> %809)
  %811 = insertelement <2 x i32> poison, i32 %68, i64 0
  %812 = shufflevector <2 x i32> %811, <2 x i32> poison, <2 x i32> zeroinitializer
  %813 = mul <2 x i32> %810, %812
  %814 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %815 = add <2 x i32> %813, %814
  %816 = insertelement <2 x i32> poison, i32 %69, i64 0
  %817 = shufflevector <2 x i32> %816, <2 x i32> poison, <2 x i32> zeroinitializer
  %818 = mul <2 x i32> %815, %817
  %819 = sext <2 x i32> %818 to <2 x i64>
  %820 = insertelement <2 x float*> poison, float* %67, i64 0
  %821 = shufflevector <2 x float*> %820, <2 x float*> poison, <2 x i32> zeroinitializer
  %822 = getelementptr float, <2 x float*> %821, <2 x i64> %819
  %823 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %822, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift359 = shufflevector <2 x float> %823, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %824 = fadd reassoc ninf nsz <2 x float> %823, %shift359
  %shuffle315 = shufflevector <2 x i32> %818, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %825 = add <4 x i32> %shuffle315, <i32 1, i32 2, i32 3, i32 4>
  %826 = sext <4 x i32> %825 to <4 x i64>
  %827 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %826
  %828 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %827, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle313 = shufflevector <2 x i32> %818, <2 x i32> poison, <4 x i32> zeroinitializer
  %829 = add <4 x i32> %shuffle313, <i32 1, i32 2, i32 3, i32 4>
  %830 = sext <4 x i32> %829 to <4 x i64>
  %831 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %830
  %832 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %831, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %833 = fadd reassoc ninf nsz <4 x float> %832, %828
  %834 = insertelement <4 x float> poison, float %794, i64 0
  %shuffle316 = shufflevector <4 x float> %834, <4 x float> poison, <4 x i32> zeroinitializer
  %835 = fmul reassoc ninf nsz <4 x float> %833, %shuffle316
  %836 = fadd reassoc ninf nsz <4 x float> %835, %790
  %837 = insertelement <2 x float> %824, float 2.000000e+00, i64 1
  %838 = insertelement <2 x float> poison, float %794, i64 0
  %839 = shufflevector <2 x float> %838, <2 x float> poison, <2 x i32> zeroinitializer
  %840 = fmul reassoc ninf nsz <2 x float> %837, %839
  %841 = fadd reassoc ninf nsz <2 x float> %840, %791
  br label %after_if33

after_if33:                                       ; preds = %true_block31, %after_if30
  %842 = phi <4 x float> [ %836, %true_block31 ], [ %790, %after_if30 ]
  %843 = phi <2 x float> [ %841, %true_block31 ], [ %791, %after_if30 ]
  br i1 %38, label %true_block34, label %after_if36

true_block34:                                     ; preds = %after_if33
  %844 = load float*, float** %24, align 8
  %845 = getelementptr float, float* %844, i64 13
  %846 = load float, float* %845, align 4
  %847 = insertelement <2 x i32> poison, i32 %70, i64 0
  %848 = shufflevector <2 x i32> %847, <2 x i32> poison, <2 x i32> zeroinitializer
  %849 = add <2 x i32> %848, <i32 13, i32 -13>
  %850 = getelementptr inbounds i8, i8* %55, i64 8
  %851 = bitcast i8* %850 to i32*
  %852 = load i32, i32* %851, align 4
  %853 = add i32 %852, -1
  %854 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %849, i1 true)
  %855 = insertelement <2 x i32> poison, i32 %853, i64 0
  %856 = shufflevector <2 x i32> %855, <2 x i32> poison, <2 x i32> zeroinitializer
  %857 = sub <2 x i32> %854, %856
  %858 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %857, <2 x i32> zeroinitializer)
  %859 = mul <2 x i32> %858, <i32 -2, i32 -2>
  %860 = add <2 x i32> %859, %854
  %861 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %860, <2 x i32> zeroinitializer)
  %862 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %856, <2 x i32> %861)
  %863 = insertelement <2 x i32> poison, i32 %68, i64 0
  %864 = shufflevector <2 x i32> %863, <2 x i32> poison, <2 x i32> zeroinitializer
  %865 = mul <2 x i32> %862, %864
  %866 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %867 = add <2 x i32> %865, %866
  %868 = insertelement <2 x i32> poison, i32 %69, i64 0
  %869 = shufflevector <2 x i32> %868, <2 x i32> poison, <2 x i32> zeroinitializer
  %870 = mul <2 x i32> %867, %869
  %871 = sext <2 x i32> %870 to <2 x i64>
  %872 = insertelement <2 x float*> poison, float* %67, i64 0
  %873 = shufflevector <2 x float*> %872, <2 x float*> poison, <2 x i32> zeroinitializer
  %874 = getelementptr float, <2 x float*> %873, <2 x i64> %871
  %875 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %874, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift360 = shufflevector <2 x float> %875, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %876 = fadd reassoc ninf nsz <2 x float> %875, %shift360
  %shuffle310 = shufflevector <2 x i32> %870, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %877 = add <4 x i32> %shuffle310, <i32 1, i32 2, i32 3, i32 4>
  %878 = sext <4 x i32> %877 to <4 x i64>
  %879 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %878
  %880 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %879, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle308 = shufflevector <2 x i32> %870, <2 x i32> poison, <4 x i32> zeroinitializer
  %881 = add <4 x i32> %shuffle308, <i32 1, i32 2, i32 3, i32 4>
  %882 = sext <4 x i32> %881 to <4 x i64>
  %883 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %882
  %884 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %883, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %885 = fadd reassoc ninf nsz <4 x float> %884, %880
  %886 = insertelement <4 x float> poison, float %846, i64 0
  %shuffle311 = shufflevector <4 x float> %886, <4 x float> poison, <4 x i32> zeroinitializer
  %887 = fmul reassoc ninf nsz <4 x float> %885, %shuffle311
  %888 = fadd reassoc ninf nsz <4 x float> %887, %842
  %889 = insertelement <2 x float> %876, float 2.000000e+00, i64 1
  %890 = insertelement <2 x float> poison, float %846, i64 0
  %891 = shufflevector <2 x float> %890, <2 x float> poison, <2 x i32> zeroinitializer
  %892 = fmul reassoc ninf nsz <2 x float> %889, %891
  %893 = fadd reassoc ninf nsz <2 x float> %892, %843
  br label %after_if36

after_if36:                                       ; preds = %true_block34, %after_if33
  %894 = phi <2 x float> [ %893, %true_block34 ], [ %843, %after_if33 ]
  %895 = phi <4 x float> [ %888, %true_block34 ], [ %842, %after_if33 ]
  br i1 %39, label %true_block37, label %after_if39

true_block37:                                     ; preds = %after_if36
  %896 = load float*, float** %24, align 8
  %897 = getelementptr float, float* %896, i64 14
  %898 = load float, float* %897, align 4
  %899 = insertelement <2 x i32> poison, i32 %70, i64 0
  %900 = shufflevector <2 x i32> %899, <2 x i32> poison, <2 x i32> zeroinitializer
  %901 = add <2 x i32> %900, <i32 14, i32 -14>
  %902 = getelementptr inbounds i8, i8* %55, i64 8
  %903 = bitcast i8* %902 to i32*
  %904 = load i32, i32* %903, align 4
  %905 = add i32 %904, -1
  %906 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %901, i1 true)
  %907 = insertelement <2 x i32> poison, i32 %905, i64 0
  %908 = shufflevector <2 x i32> %907, <2 x i32> poison, <2 x i32> zeroinitializer
  %909 = sub <2 x i32> %906, %908
  %910 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %909, <2 x i32> zeroinitializer)
  %911 = mul <2 x i32> %910, <i32 -2, i32 -2>
  %912 = add <2 x i32> %911, %906
  %913 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %912, <2 x i32> zeroinitializer)
  %914 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %908, <2 x i32> %913)
  %915 = insertelement <2 x i32> poison, i32 %68, i64 0
  %916 = shufflevector <2 x i32> %915, <2 x i32> poison, <2 x i32> zeroinitializer
  %917 = mul <2 x i32> %914, %916
  %918 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %919 = add <2 x i32> %917, %918
  %920 = insertelement <2 x i32> poison, i32 %69, i64 0
  %921 = shufflevector <2 x i32> %920, <2 x i32> poison, <2 x i32> zeroinitializer
  %922 = mul <2 x i32> %919, %921
  %923 = extractelement <2 x i32> %922, i64 1
  %924 = sext i32 %923 to i64
  %925 = getelementptr float, float* %67, i64 %924
  %926 = load float, float* %925, align 4
  %927 = extractelement <2 x i32> %922, i64 0
  %928 = sext i32 %927 to i64
  %929 = getelementptr float, float* %67, i64 %928
  %930 = load float, float* %929, align 4
  %931 = fadd reassoc ninf nsz float %930, %926
  %932 = add <2 x i32> %922, <i32 1, i32 1>
  %933 = extractelement <2 x i32> %932, i64 1
  %934 = sext i32 %933 to i64
  %935 = getelementptr float, float* %67, i64 %934
  %936 = load float, float* %935, align 4
  %937 = extractelement <2 x i32> %932, i64 0
  %938 = sext i32 %937 to i64
  %939 = getelementptr float, float* %67, i64 %938
  %940 = load float, float* %939, align 4
  %941 = shufflevector <2 x i32> %922, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %942 = add <2 x i32> %941, <i32 2, i32 3>
  %943 = sext <2 x i32> %942 to <2 x i64>
  %944 = insertelement <2 x float*> poison, float* %67, i64 0
  %945 = shufflevector <2 x float*> %944, <2 x float*> poison, <2 x i32> zeroinitializer
  %946 = getelementptr float, <2 x float*> %945, <2 x i64> %943
  %947 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %946, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %948 = shufflevector <2 x i32> %922, <2 x i32> undef, <2 x i32> zeroinitializer
  %949 = add <2 x i32> %948, <i32 2, i32 3>
  %950 = sext <2 x i32> %949 to <2 x i64>
  %951 = getelementptr float, <2 x float*> %945, <2 x i64> %950
  %952 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %951, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %953 = add <2 x i32> %922, <i32 4, i32 4>
  %954 = sext <2 x i32> %953 to <2 x i64>
  %955 = getelementptr float, <2 x float*> %945, <2 x i64> %954
  %956 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %955, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %957 = shufflevector <2 x float> %956, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %958 = insertelement <4 x float> poison, float %940, i64 0
  %959 = shufflevector <2 x float> %952, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %960 = shufflevector <4 x float> %958, <4 x float> %959, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %961 = shufflevector <4 x float> %960, <4 x float> %957, <4 x i32> <i32 0, i32 1, i32 2, i32 4>
  %962 = insertelement <4 x float> poison, float %936, i64 0
  %963 = shufflevector <2 x float> %947, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %964 = shufflevector <4 x float> %962, <4 x float> %963, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %965 = shufflevector <4 x float> %964, <4 x float> %957, <4 x i32> <i32 0, i32 1, i32 2, i32 5>
  %966 = fadd reassoc ninf nsz <4 x float> %961, %965
  %967 = insertelement <4 x float> poison, float %898, i64 0
  %shuffle306 = shufflevector <4 x float> %967, <4 x float> poison, <4 x i32> zeroinitializer
  %968 = fmul reassoc ninf nsz <4 x float> %966, %shuffle306
  %969 = fadd reassoc ninf nsz <4 x float> %968, %895
  %970 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %931, i64 0
  %971 = insertelement <2 x float> poison, float %898, i64 0
  %972 = shufflevector <2 x float> %971, <2 x float> poison, <2 x i32> zeroinitializer
  %973 = fmul reassoc ninf nsz <2 x float> %970, %972
  %974 = fadd reassoc ninf nsz <2 x float> %973, %894
  br label %after_if39

after_if39:                                       ; preds = %true_block37, %after_if36
  %975 = phi <4 x float> [ %969, %true_block37 ], [ %895, %after_if36 ]
  %976 = phi <2 x float> [ %974, %true_block37 ], [ %894, %after_if36 ]
  br i1 %40, label %true_block40, label %after_if42

true_block40:                                     ; preds = %after_if39
  %977 = load float*, float** %24, align 8
  %978 = getelementptr float, float* %977, i64 15
  %979 = load float, float* %978, align 4
  %980 = insertelement <2 x i32> poison, i32 %70, i64 0
  %981 = shufflevector <2 x i32> %980, <2 x i32> poison, <2 x i32> zeroinitializer
  %982 = add <2 x i32> %981, <i32 15, i32 -15>
  %983 = getelementptr inbounds i8, i8* %55, i64 8
  %984 = bitcast i8* %983 to i32*
  %985 = load i32, i32* %984, align 4
  %986 = add i32 %985, -1
  %987 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %982, i1 true)
  %988 = insertelement <2 x i32> poison, i32 %986, i64 0
  %989 = shufflevector <2 x i32> %988, <2 x i32> poison, <2 x i32> zeroinitializer
  %990 = sub <2 x i32> %987, %989
  %991 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %990, <2 x i32> zeroinitializer)
  %992 = mul <2 x i32> %991, <i32 -2, i32 -2>
  %993 = add <2 x i32> %992, %987
  %994 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %993, <2 x i32> zeroinitializer)
  %995 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %989, <2 x i32> %994)
  %996 = insertelement <2 x i32> poison, i32 %68, i64 0
  %997 = shufflevector <2 x i32> %996, <2 x i32> poison, <2 x i32> zeroinitializer
  %998 = mul <2 x i32> %995, %997
  %999 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %1000 = add <2 x i32> %998, %999
  %1001 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1002 = shufflevector <2 x i32> %1001, <2 x i32> poison, <2 x i32> zeroinitializer
  %1003 = mul <2 x i32> %1000, %1002
  %1004 = sext <2 x i32> %1003 to <2 x i64>
  %1005 = insertelement <2 x float*> poison, float* %67, i64 0
  %1006 = shufflevector <2 x float*> %1005, <2 x float*> poison, <2 x i32> zeroinitializer
  %1007 = getelementptr float, <2 x float*> %1006, <2 x i64> %1004
  %1008 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1007, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift361 = shufflevector <2 x float> %1008, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1009 = fadd reassoc ninf nsz <2 x float> %1008, %shift361
  %1010 = shufflevector <2 x i32> %1003, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1011 = add <4 x i32> %1010, <i32 1, i32 2, i32 3, i32 4>
  %1012 = sext <4 x i32> %1011 to <4 x i64>
  %1013 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1012
  %1014 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1013, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1015 = shufflevector <2 x i32> %1003, <2 x i32> undef, <4 x i32> zeroinitializer
  %1016 = add <4 x i32> %1015, <i32 1, i32 2, i32 3, i32 4>
  %1017 = sext <4 x i32> %1016 to <4 x i64>
  %1018 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1017
  %1019 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1018, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1020 = fadd reassoc ninf nsz <4 x float> %1019, %1014
  %1021 = insertelement <4 x float> poison, float %979, i64 0
  %shuffle305 = shufflevector <4 x float> %1021, <4 x float> poison, <4 x i32> zeroinitializer
  %1022 = fmul reassoc ninf nsz <4 x float> %1020, %shuffle305
  %1023 = fadd reassoc ninf nsz <4 x float> %1022, %975
  %1024 = insertelement <2 x float> %1009, float 2.000000e+00, i64 1
  %1025 = insertelement <2 x float> poison, float %979, i64 0
  %1026 = shufflevector <2 x float> %1025, <2 x float> poison, <2 x i32> zeroinitializer
  %1027 = fmul reassoc ninf nsz <2 x float> %1024, %1026
  %1028 = fadd reassoc ninf nsz <2 x float> %1027, %976
  br label %after_if42

after_if42:                                       ; preds = %true_block40, %after_if39
  %1029 = phi <4 x float> [ %1023, %true_block40 ], [ %975, %after_if39 ]
  %1030 = phi <2 x float> [ %1028, %true_block40 ], [ %976, %after_if39 ]
  br i1 %41, label %true_block43, label %after_if45

true_block43:                                     ; preds = %after_if42
  %1031 = load float*, float** %24, align 8
  %1032 = getelementptr float, float* %1031, i64 16
  %1033 = load float, float* %1032, align 4
  %1034 = insertelement <2 x i32> poison, i32 %70, i64 0
  %1035 = shufflevector <2 x i32> %1034, <2 x i32> poison, <2 x i32> zeroinitializer
  %1036 = add <2 x i32> %1035, <i32 16, i32 -16>
  %1037 = getelementptr inbounds i8, i8* %55, i64 8
  %1038 = bitcast i8* %1037 to i32*
  %1039 = load i32, i32* %1038, align 4
  %1040 = add i32 %1039, -1
  %1041 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1036, i1 true)
  %1042 = insertelement <2 x i32> poison, i32 %1040, i64 0
  %1043 = shufflevector <2 x i32> %1042, <2 x i32> poison, <2 x i32> zeroinitializer
  %1044 = sub <2 x i32> %1041, %1043
  %1045 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1044, <2 x i32> zeroinitializer)
  %1046 = mul <2 x i32> %1045, <i32 -2, i32 -2>
  %1047 = add <2 x i32> %1046, %1041
  %1048 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1047, <2 x i32> zeroinitializer)
  %1049 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1043, <2 x i32> %1048)
  %1050 = insertelement <2 x i32> poison, i32 %68, i64 0
  %1051 = shufflevector <2 x i32> %1050, <2 x i32> poison, <2 x i32> zeroinitializer
  %1052 = mul <2 x i32> %1049, %1051
  %1053 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %1054 = add <2 x i32> %1052, %1053
  %1055 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1056 = shufflevector <2 x i32> %1055, <2 x i32> poison, <2 x i32> zeroinitializer
  %1057 = mul <2 x i32> %1054, %1056
  %1058 = sext <2 x i32> %1057 to <2 x i64>
  %1059 = insertelement <2 x float*> poison, float* %67, i64 0
  %1060 = shufflevector <2 x float*> %1059, <2 x float*> poison, <2 x i32> zeroinitializer
  %1061 = getelementptr float, <2 x float*> %1060, <2 x i64> %1058
  %1062 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1061, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift362 = shufflevector <2 x float> %1062, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1063 = fadd reassoc ninf nsz <2 x float> %1062, %shift362
  %1064 = add <2 x i32> %1057, <i32 1, i32 1>
  %1065 = extractelement <2 x i32> %1064, i64 1
  %1066 = sext i32 %1065 to i64
  %1067 = getelementptr float, float* %67, i64 %1066
  %1068 = extractelement <2 x i32> %1064, i64 0
  %1069 = sext i32 %1068 to i64
  %1070 = getelementptr float, float* %67, i64 %1069
  %1071 = shufflevector <2 x i32> %1057, <2 x i32> undef, <4 x i32> <i32 1, i32 0, i32 1, i32 0>
  %1072 = add <4 x i32> %1071, <i32 2, i32 2, i32 3, i32 3>
  %1073 = extractelement <4 x i32> %1072, i64 0
  %1074 = sext i32 %1073 to i64
  %1075 = getelementptr float, float* %67, i64 %1074
  %1076 = extractelement <4 x i32> %1072, i64 1
  %1077 = sext i32 %1076 to i64
  %1078 = getelementptr float, float* %67, i64 %1077
  %1079 = extractelement <4 x i32> %1072, i64 2
  %1080 = sext i32 %1079 to i64
  %1081 = getelementptr float, float* %67, i64 %1080
  %1082 = extractelement <4 x i32> %1072, i64 3
  %1083 = sext i32 %1082 to i64
  %1084 = getelementptr float, float* %67, i64 %1083
  %1085 = add <2 x i32> %1057, <i32 4, i32 4>
  %1086 = extractelement <2 x i32> %1085, i64 1
  %1087 = sext i32 %1086 to i64
  %1088 = getelementptr float, float* %67, i64 %1087
  %1089 = extractelement <2 x i32> %1085, i64 0
  %1090 = sext i32 %1089 to i64
  %1091 = getelementptr float, float* %67, i64 %1090
  %1092 = insertelement <4 x float*> poison, float* %1067, i64 0
  %1093 = insertelement <4 x float*> %1092, float* %1075, i64 1
  %1094 = insertelement <4 x float*> %1093, float* %1081, i64 2
  %1095 = insertelement <4 x float*> %1094, float* %1088, i64 3
  %1096 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1095, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1097 = insertelement <4 x float*> poison, float* %1070, i64 0
  %1098 = insertelement <4 x float*> %1097, float* %1078, i64 1
  %1099 = insertelement <4 x float*> %1098, float* %1084, i64 2
  %1100 = insertelement <4 x float*> %1099, float* %1091, i64 3
  %1101 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1100, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1102 = fadd reassoc ninf nsz <4 x float> %1101, %1096
  %1103 = insertelement <4 x float> poison, float %1033, i64 0
  %shuffle302 = shufflevector <4 x float> %1103, <4 x float> poison, <4 x i32> zeroinitializer
  %1104 = fmul reassoc ninf nsz <4 x float> %1102, %shuffle302
  %1105 = fadd reassoc ninf nsz <4 x float> %1104, %1029
  %1106 = insertelement <2 x float> %1063, float 2.000000e+00, i64 1
  %1107 = insertelement <2 x float> poison, float %1033, i64 0
  %1108 = shufflevector <2 x float> %1107, <2 x float> poison, <2 x i32> zeroinitializer
  %1109 = fmul reassoc ninf nsz <2 x float> %1106, %1108
  %1110 = fadd reassoc ninf nsz <2 x float> %1109, %1030
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42
  %1111 = phi <4 x float> [ %1105, %true_block43 ], [ %1029, %after_if42 ]
  %1112 = phi <2 x float> [ %1110, %true_block43 ], [ %1030, %after_if42 ]
  br i1 %42, label %true_block46, label %after_if48

true_block46:                                     ; preds = %after_if45
  %1113 = load float*, float** %24, align 8
  %1114 = getelementptr float, float* %1113, i64 17
  %1115 = load float, float* %1114, align 4
  %1116 = insertelement <2 x i32> poison, i32 %70, i64 0
  %1117 = shufflevector <2 x i32> %1116, <2 x i32> poison, <2 x i32> zeroinitializer
  %1118 = add <2 x i32> %1117, <i32 17, i32 -17>
  %1119 = getelementptr inbounds i8, i8* %55, i64 8
  %1120 = bitcast i8* %1119 to i32*
  %1121 = load i32, i32* %1120, align 4
  %1122 = add i32 %1121, -1
  %1123 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1118, i1 true)
  %1124 = insertelement <2 x i32> poison, i32 %1122, i64 0
  %1125 = shufflevector <2 x i32> %1124, <2 x i32> poison, <2 x i32> zeroinitializer
  %1126 = sub <2 x i32> %1123, %1125
  %1127 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1126, <2 x i32> zeroinitializer)
  %1128 = mul <2 x i32> %1127, <i32 -2, i32 -2>
  %1129 = add <2 x i32> %1128, %1123
  %1130 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1129, <2 x i32> zeroinitializer)
  %1131 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1125, <2 x i32> %1130)
  %1132 = insertelement <2 x i32> poison, i32 %68, i64 0
  %1133 = shufflevector <2 x i32> %1132, <2 x i32> poison, <2 x i32> zeroinitializer
  %1134 = mul <2 x i32> %1131, %1133
  %1135 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %1136 = add <2 x i32> %1134, %1135
  %1137 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1138 = shufflevector <2 x i32> %1137, <2 x i32> poison, <2 x i32> zeroinitializer
  %1139 = mul <2 x i32> %1136, %1138
  %1140 = sext <2 x i32> %1139 to <2 x i64>
  %1141 = insertelement <2 x float*> poison, float* %67, i64 0
  %1142 = shufflevector <2 x float*> %1141, <2 x float*> poison, <2 x i32> zeroinitializer
  %1143 = getelementptr float, <2 x float*> %1142, <2 x i64> %1140
  %1144 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1143, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift363 = shufflevector <2 x float> %1144, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1145 = fadd reassoc ninf nsz <2 x float> %1144, %shift363
  %1146 = shufflevector <2 x i32> %1139, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1147 = add <4 x i32> %1146, <i32 1, i32 2, i32 3, i32 4>
  %1148 = sext <4 x i32> %1147 to <4 x i64>
  %1149 = shufflevector <2 x i32> %1139, <2 x i32> undef, <4 x i32> zeroinitializer
  %1150 = add <4 x i32> %1149, <i32 1, i32 2, i32 3, i32 4>
  %1151 = sext <4 x i32> %1150 to <4 x i64>
  %1152 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1148
  %1153 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1152, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1154 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1151
  %1155 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1154, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1156 = fadd reassoc ninf nsz <4 x float> %1155, %1153
  %1157 = insertelement <4 x float> poison, float %1115, i64 0
  %shuffle301 = shufflevector <4 x float> %1157, <4 x float> poison, <4 x i32> zeroinitializer
  %1158 = fmul reassoc ninf nsz <4 x float> %1156, %shuffle301
  %1159 = fadd reassoc ninf nsz <4 x float> %1158, %1111
  %1160 = insertelement <2 x float> %1145, float 2.000000e+00, i64 1
  %1161 = insertelement <2 x float> poison, float %1115, i64 0
  %1162 = shufflevector <2 x float> %1161, <2 x float> poison, <2 x i32> zeroinitializer
  %1163 = fmul reassoc ninf nsz <2 x float> %1160, %1162
  %1164 = fadd reassoc ninf nsz <2 x float> %1163, %1112
  br label %after_if48

after_if48:                                       ; preds = %true_block46, %after_if45
  %1165 = phi <4 x float> [ %1159, %true_block46 ], [ %1111, %after_if45 ]
  %1166 = phi <2 x float> [ %1164, %true_block46 ], [ %1112, %after_if45 ]
  br i1 %43, label %true_block49, label %after_if51

true_block49:                                     ; preds = %after_if48
  %1167 = load float*, float** %24, align 8
  %1168 = getelementptr float, float* %1167, i64 18
  %1169 = load float, float* %1168, align 4
  %1170 = insertelement <2 x i32> poison, i32 %70, i64 0
  %1171 = shufflevector <2 x i32> %1170, <2 x i32> poison, <2 x i32> zeroinitializer
  %1172 = add <2 x i32> %1171, <i32 18, i32 -18>
  %1173 = getelementptr inbounds i8, i8* %55, i64 8
  %1174 = bitcast i8* %1173 to i32*
  %1175 = load i32, i32* %1174, align 4
  %1176 = add i32 %1175, -1
  %1177 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1172, i1 true)
  %1178 = insertelement <2 x i32> poison, i32 %1176, i64 0
  %1179 = shufflevector <2 x i32> %1178, <2 x i32> poison, <2 x i32> zeroinitializer
  %1180 = sub <2 x i32> %1177, %1179
  %1181 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1180, <2 x i32> zeroinitializer)
  %1182 = mul <2 x i32> %1181, <i32 -2, i32 -2>
  %1183 = add <2 x i32> %1182, %1177
  %1184 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1183, <2 x i32> zeroinitializer)
  %1185 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1179, <2 x i32> %1184)
  %1186 = insertelement <2 x i32> poison, i32 %68, i64 0
  %1187 = shufflevector <2 x i32> %1186, <2 x i32> poison, <2 x i32> zeroinitializer
  %1188 = mul <2 x i32> %1185, %1187
  %1189 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %1190 = add <2 x i32> %1188, %1189
  %1191 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1192 = shufflevector <2 x i32> %1191, <2 x i32> poison, <2 x i32> zeroinitializer
  %1193 = mul <2 x i32> %1190, %1192
  %1194 = sext <2 x i32> %1193 to <2 x i64>
  %1195 = insertelement <2 x float*> poison, float* %67, i64 0
  %1196 = shufflevector <2 x float*> %1195, <2 x float*> poison, <2 x i32> zeroinitializer
  %1197 = getelementptr float, <2 x float*> %1196, <2 x i64> %1194
  %1198 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1197, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift364 = shufflevector <2 x float> %1198, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1199 = fadd reassoc ninf nsz <2 x float> %1198, %shift364
  %shuffle297 = shufflevector <2 x i32> %1193, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1200 = add <4 x i32> %shuffle297, <i32 1, i32 2, i32 3, i32 4>
  %1201 = sext <4 x i32> %1200 to <4 x i64>
  %1202 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1201
  %1203 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1202, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle295 = shufflevector <2 x i32> %1193, <2 x i32> poison, <4 x i32> zeroinitializer
  %1204 = add <4 x i32> %shuffle295, <i32 1, i32 2, i32 3, i32 4>
  %1205 = sext <4 x i32> %1204 to <4 x i64>
  %1206 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1205
  %1207 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1206, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1208 = fadd reassoc ninf nsz <4 x float> %1207, %1203
  %1209 = insertelement <4 x float> poison, float %1169, i64 0
  %shuffle298 = shufflevector <4 x float> %1209, <4 x float> poison, <4 x i32> zeroinitializer
  %1210 = fmul reassoc ninf nsz <4 x float> %1208, %shuffle298
  %1211 = fadd reassoc ninf nsz <4 x float> %1210, %1165
  %1212 = insertelement <2 x float> %1199, float 2.000000e+00, i64 1
  %1213 = insertelement <2 x float> poison, float %1169, i64 0
  %1214 = shufflevector <2 x float> %1213, <2 x float> poison, <2 x i32> zeroinitializer
  %1215 = fmul reassoc ninf nsz <2 x float> %1212, %1214
  %1216 = fadd reassoc ninf nsz <2 x float> %1215, %1166
  br label %after_if51

after_if51:                                       ; preds = %true_block49, %after_if48
  %1217 = phi <4 x float> [ %1211, %true_block49 ], [ %1165, %after_if48 ]
  %1218 = phi <2 x float> [ %1216, %true_block49 ], [ %1166, %after_if48 ]
  br i1 %44, label %true_block52, label %after_if54

true_block52:                                     ; preds = %after_if51
  %1219 = load float*, float** %24, align 8
  %1220 = getelementptr float, float* %1219, i64 19
  %1221 = load float, float* %1220, align 4
  %1222 = insertelement <2 x i32> poison, i32 %70, i64 0
  %1223 = shufflevector <2 x i32> %1222, <2 x i32> poison, <2 x i32> zeroinitializer
  %1224 = add <2 x i32> %1223, <i32 19, i32 -19>
  %1225 = getelementptr inbounds i8, i8* %55, i64 8
  %1226 = bitcast i8* %1225 to i32*
  %1227 = load i32, i32* %1226, align 4
  %1228 = add i32 %1227, -1
  %1229 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1224, i1 true)
  %1230 = insertelement <2 x i32> poison, i32 %1228, i64 0
  %1231 = shufflevector <2 x i32> %1230, <2 x i32> poison, <2 x i32> zeroinitializer
  %1232 = sub <2 x i32> %1229, %1231
  %1233 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1232, <2 x i32> zeroinitializer)
  %1234 = mul <2 x i32> %1233, <i32 -2, i32 -2>
  %1235 = add <2 x i32> %1234, %1229
  %1236 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1235, <2 x i32> zeroinitializer)
  %1237 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1231, <2 x i32> %1236)
  %1238 = insertelement <2 x i32> poison, i32 %68, i64 0
  %1239 = shufflevector <2 x i32> %1238, <2 x i32> poison, <2 x i32> zeroinitializer
  %1240 = mul <2 x i32> %1237, %1239
  %1241 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %1242 = add <2 x i32> %1240, %1241
  %1243 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1244 = shufflevector <2 x i32> %1243, <2 x i32> poison, <2 x i32> zeroinitializer
  %1245 = mul <2 x i32> %1242, %1244
  %1246 = sext <2 x i32> %1245 to <2 x i64>
  %1247 = insertelement <2 x float*> poison, float* %67, i64 0
  %1248 = shufflevector <2 x float*> %1247, <2 x float*> poison, <2 x i32> zeroinitializer
  %1249 = getelementptr float, <2 x float*> %1248, <2 x i64> %1246
  %1250 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1249, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift365 = shufflevector <2 x float> %1250, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1251 = fadd reassoc ninf nsz <2 x float> %1250, %shift365
  %shuffle292 = shufflevector <2 x i32> %1245, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1252 = add <4 x i32> %shuffle292, <i32 1, i32 2, i32 3, i32 4>
  %1253 = sext <4 x i32> %1252 to <4 x i64>
  %1254 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1253
  %1255 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1254, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle290 = shufflevector <2 x i32> %1245, <2 x i32> poison, <4 x i32> zeroinitializer
  %1256 = add <4 x i32> %shuffle290, <i32 1, i32 2, i32 3, i32 4>
  %1257 = sext <4 x i32> %1256 to <4 x i64>
  %1258 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1257
  %1259 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1258, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1260 = fadd reassoc ninf nsz <4 x float> %1259, %1255
  %1261 = insertelement <4 x float> poison, float %1221, i64 0
  %shuffle293 = shufflevector <4 x float> %1261, <4 x float> poison, <4 x i32> zeroinitializer
  %1262 = fmul reassoc ninf nsz <4 x float> %1260, %shuffle293
  %1263 = fadd reassoc ninf nsz <4 x float> %1262, %1217
  %1264 = insertelement <2 x float> %1251, float 2.000000e+00, i64 1
  %1265 = insertelement <2 x float> poison, float %1221, i64 0
  %1266 = shufflevector <2 x float> %1265, <2 x float> poison, <2 x i32> zeroinitializer
  %1267 = fmul reassoc ninf nsz <2 x float> %1264, %1266
  %1268 = fadd reassoc ninf nsz <2 x float> %1267, %1218
  br label %after_if54

after_if54:                                       ; preds = %true_block52, %after_if51
  %1269 = phi <4 x float> [ %1263, %true_block52 ], [ %1217, %after_if51 ]
  %1270 = phi <2 x float> [ %1268, %true_block52 ], [ %1218, %after_if51 ]
  %1271 = extractelement <2 x float> %1270, i64 0
  %1272 = extractelement <2 x float> %1270, i64 1
  br i1 %45, label %true_block55, label %after_if57

true_block55:                                     ; preds = %after_if54
  %1273 = load float*, float** %24, align 8
  %1274 = getelementptr float, float* %1273, i64 20
  %1275 = load float, float* %1274, align 4
  %1276 = insertelement <2 x i32> poison, i32 %70, i64 0
  %1277 = shufflevector <2 x i32> %1276, <2 x i32> poison, <2 x i32> zeroinitializer
  %1278 = add <2 x i32> %1277, <i32 20, i32 -20>
  %1279 = getelementptr inbounds i8, i8* %55, i64 8
  %1280 = bitcast i8* %1279 to i32*
  %1281 = load i32, i32* %1280, align 4
  %1282 = add i32 %1281, -1
  %1283 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1278, i1 true)
  %1284 = insertelement <2 x i32> poison, i32 %1282, i64 0
  %1285 = shufflevector <2 x i32> %1284, <2 x i32> poison, <2 x i32> zeroinitializer
  %1286 = sub <2 x i32> %1283, %1285
  %1287 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1286, <2 x i32> zeroinitializer)
  %1288 = mul <2 x i32> %1287, <i32 -2, i32 -2>
  %1289 = add <2 x i32> %1288, %1283
  %1290 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1289, <2 x i32> zeroinitializer)
  %1291 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1285, <2 x i32> %1290)
  %1292 = insertelement <2 x i32> poison, i32 %68, i64 0
  %1293 = shufflevector <2 x i32> %1292, <2 x i32> poison, <2 x i32> zeroinitializer
  %1294 = mul <2 x i32> %1291, %1293
  %1295 = shufflevector <2 x i32> %74, <2 x i32> poison, <2 x i32> zeroinitializer
  %1296 = add <2 x i32> %1294, %1295
  %1297 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1298 = shufflevector <2 x i32> %1297, <2 x i32> poison, <2 x i32> zeroinitializer
  %1299 = mul <2 x i32> %1296, %1298
  %1300 = sext <2 x i32> %1299 to <2 x i64>
  %1301 = insertelement <2 x float*> poison, float* %67, i64 0
  %1302 = shufflevector <2 x float*> %1301, <2 x float*> poison, <2 x i32> zeroinitializer
  %1303 = getelementptr float, <2 x float*> %1302, <2 x i64> %1300
  %1304 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1303, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift366 = shufflevector <2 x float> %1304, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1305 = fadd reassoc ninf nsz <2 x float> %1304, %shift366
  %1306 = extractelement <2 x float> %1305, i64 0
  %1307 = fmul reassoc ninf nsz float %1306, %1275
  %1308 = fadd reassoc ninf nsz float %1307, %1271
  %shuffle287 = shufflevector <2 x i32> %1299, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1309 = add <4 x i32> %shuffle287, <i32 1, i32 2, i32 3, i32 4>
  %1310 = sext <4 x i32> %1309 to <4 x i64>
  %1311 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1310
  %1312 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1311, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle285 = shufflevector <2 x i32> %1299, <2 x i32> poison, <4 x i32> zeroinitializer
  %1313 = add <4 x i32> %shuffle285, <i32 1, i32 2, i32 3, i32 4>
  %1314 = sext <4 x i32> %1313 to <4 x i64>
  %1315 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1314
  %1316 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1315, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1317 = fadd reassoc ninf nsz <4 x float> %1316, %1312
  %1318 = insertelement <4 x float> poison, float %1275, i64 0
  %shuffle288 = shufflevector <4 x float> %1318, <4 x float> poison, <4 x i32> zeroinitializer
  %1319 = fmul reassoc ninf nsz <4 x float> %1317, %shuffle288
  %1320 = fadd reassoc ninf nsz <4 x float> %1319, %1269
  %factor283 = fmul reassoc ninf nsz float %1275, 2.000000e+00
  %1321 = fadd reassoc ninf nsz float %factor283, %1272
  br label %after_if57

after_if57:                                       ; preds = %true_block55, %after_if54
  %.19222 = phi float [ %1308, %true_block55 ], [ %1271, %after_if54 ]
  %.19 = phi float [ %1321, %true_block55 ], [ %1272, %after_if54 ]
  %1322 = phi <4 x float> [ %1320, %true_block55 ], [ %1269, %after_if54 ]
  %1323 = fdiv reassoc ninf nsz float 1.000000e+00, %.19
  %1324 = fmul reassoc ninf nsz float %1323, %.19222
  %1325 = load float*, float** %50, align 8
  %1326 = load i32, i32* %51, align 4
  %1327 = load i32, i32* %52, align 4
  %1328 = mul i32 %1326, %70
  %1329 = add i32 %1328, %75
  %1330 = mul i32 %1329, %1327
  %1331 = sext i32 %1330 to i64
  %1332 = getelementptr float, float* %1325, i64 %1331
  store float %1324, float* %1332, align 4
  %1333 = extractelement <4 x float> %1322, i64 0
  %1334 = fmul reassoc ninf nsz float %1323, %1333
  %1335 = load float*, float** %50, align 8
  %1336 = load i32, i32* %51, align 4
  %1337 = load i32, i32* %52, align 4
  %1338 = mul i32 %1336, %70
  %1339 = add i32 %1338, %75
  %1340 = mul i32 %1339, %1337
  %1341 = add i32 %1340, 1
  %1342 = sext i32 %1341 to i64
  %1343 = getelementptr float, float* %1335, i64 %1342
  store float %1334, float* %1343, align 4
  %1344 = extractelement <4 x float> %1322, i64 1
  %1345 = fmul reassoc ninf nsz float %1323, %1344
  %1346 = load float*, float** %50, align 8
  %1347 = load i32, i32* %51, align 4
  %1348 = load i32, i32* %52, align 4
  %1349 = mul i32 %1347, %70
  %1350 = add i32 %1349, %75
  %1351 = mul i32 %1350, %1348
  %1352 = add i32 %1351, 2
  %1353 = sext i32 %1352 to i64
  %1354 = getelementptr float, float* %1346, i64 %1353
  store float %1345, float* %1354, align 4
  %1355 = extractelement <4 x float> %1322, i64 2
  %1356 = fmul reassoc ninf nsz float %1323, %1355
  %1357 = load float*, float** %50, align 8
  %1358 = load i32, i32* %51, align 4
  %1359 = load i32, i32* %52, align 4
  %1360 = mul i32 %1358, %70
  %1361 = add i32 %1360, %75
  %1362 = mul i32 %1361, %1359
  %1363 = add i32 %1362, 3
  %1364 = sext i32 %1363 to i64
  %1365 = getelementptr float, float* %1357, i64 %1364
  store float %1356, float* %1365, align 4
  %1366 = extractelement <4 x float> %1322, i64 3
  %1367 = fmul reassoc ninf nsz float %1323, %1366
  %1368 = load float*, float** %50, align 8
  %1369 = load i32, i32* %51, align 4
  %1370 = load i32, i32* %52, align 4
  %1371 = mul i32 %1369, %70
  %1372 = add i32 %1371, %75
  %1373 = mul i32 %1372, %1370
  %1374 = add i32 %1373, 4
  %1375 = sext i32 %1374 to i64
  %1376 = getelementptr float, float* %1368, i64 %1375
  store float %1367, float* %1376, align 4
  %1377 = add nsw i32 %.0223284, 1
  %exitcond.not = icmp eq i32 %19, %1377
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
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
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.abs.v2i32(<2 x i32>, i1 immarg) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #7

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
