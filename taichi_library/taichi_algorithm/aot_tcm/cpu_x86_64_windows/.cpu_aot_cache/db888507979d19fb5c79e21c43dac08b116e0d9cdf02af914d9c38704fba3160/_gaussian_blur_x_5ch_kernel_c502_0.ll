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
define void @_gaussian_blur_x_5ch_kernel_c502_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 8
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 4
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = mul i32 %13, %4
  %20 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %20, i64 0, i32 14
  %22 = bitcast i8** %21 to i32**
  %23 = load i32*, i32** %22, align 8
  store i32 %19, i32* %23, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_x_5ch_kernel_c502_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
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
  %.0223284 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %1300, %after_if57 ]
  %53 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %53, i64 0, i32 14
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
  %73 = insertelement <2 x i32> %72, i32 %68, i64 1
  %74 = insertelement <2 x i32> poison, i32 %71, i64 0
  %75 = insertelement <2 x i32> %74, i32 %70, i64 1
  %76 = sub <2 x i32> %73, %75
  %77 = mul <2 x i32> %73, %75
  %78 = extractelement <2 x i32> %76, i64 0
  %79 = extractelement <2 x i32> %77, i64 1
  %80 = add i32 %78, %79
  %81 = mul i32 %80, %69
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, float* %67, i64 %82
  %84 = load float, float* %83, align 4
  %85 = load float, float* %25, align 4
  %86 = fmul reassoc ninf nsz float %85, %84
  %87 = insertelement <4 x i32> poison, i32 %81, i64 0
  %shuffle349 = shufflevector <4 x i32> %87, <4 x i32> poison, <4 x i32> zeroinitializer
  %88 = add <4 x i32> %shuffle349, <i32 1, i32 2, i32 3, i32 4>
  %89 = sext <4 x i32> %88 to <4 x i64>
  %90 = insertelement <4 x float*> poison, float* %67, i64 0
  %shuffle348 = shufflevector <4 x float*> %90, <4 x float*> poison, <4 x i32> zeroinitializer
  %91 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %89
  %92 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %91, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %93 = insertelement <4 x float> poison, float %85, i64 0
  %shuffle350 = shufflevector <4 x float> %93, <4 x float> poison, <4 x i32> zeroinitializer
  %94 = fmul reassoc ninf nsz <4 x float> %92, %shuffle350
  %95 = insertelement <2 x float> poison, float %86, i64 0
  %96 = insertelement <2 x float> %95, float %85, i64 1
  br i1 %26, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if57
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %97 = load float*, float** %24, align 8
  %98 = getelementptr float, float* %97, i64 1
  %99 = load float, float* %98, align 4
  %100 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %101 = add <2 x i32> %100, <i32 1, i32 -1>
  %102 = getelementptr inbounds i8, i8* %55, i64 8
  %103 = bitcast i8* %102 to i32*
  %104 = load i32, i32* %103, align 4
  %105 = add i32 %104, -1
  %106 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %101, i1 true)
  %107 = insertelement <2 x i32> poison, i32 %105, i64 0
  %108 = shufflevector <2 x i32> %107, <2 x i32> poison, <2 x i32> zeroinitializer
  %109 = sub <2 x i32> %106, %108
  %110 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %109, <2 x i32> zeroinitializer)
  %111 = mul <2 x i32> %110, <i32 -2, i32 -2>
  %112 = add <2 x i32> %111, %106
  %113 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %112, <2 x i32> zeroinitializer)
  %114 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %108, <2 x i32> %113)
  %115 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %116 = add <2 x i32> %114, %115
  %117 = insertelement <2 x i32> poison, i32 %69, i64 0
  %118 = shufflevector <2 x i32> %117, <2 x i32> poison, <2 x i32> zeroinitializer
  %119 = mul <2 x i32> %116, %118
  %120 = sext <2 x i32> %119 to <2 x i64>
  %121 = insertelement <2 x float*> poison, float* %67, i64 0
  %122 = shufflevector <2 x float*> %121, <2 x float*> poison, <2 x i32> zeroinitializer
  %123 = getelementptr float, <2 x float*> %122, <2 x i64> %120
  %124 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %123, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift = shufflevector <2 x float> %124, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %125 = fadd reassoc ninf nsz <2 x float> %124, %shift
  %shuffle346 = shufflevector <2 x i32> %119, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %126 = add <4 x i32> %shuffle346, <i32 1, i32 2, i32 3, i32 4>
  %127 = sext <4 x i32> %126 to <4 x i64>
  %128 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %127
  %129 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %128, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle344 = shufflevector <2 x i32> %119, <2 x i32> poison, <4 x i32> zeroinitializer
  %130 = add <4 x i32> %shuffle344, <i32 1, i32 2, i32 3, i32 4>
  %131 = sext <4 x i32> %130 to <4 x i64>
  %132 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %131
  %133 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %132, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %134 = fadd reassoc ninf nsz <4 x float> %133, %129
  %135 = insertelement <4 x float> poison, float %99, i64 0
  %shuffle347 = shufflevector <4 x float> %135, <4 x float> poison, <4 x i32> zeroinitializer
  %136 = fmul reassoc ninf nsz <4 x float> %134, %shuffle347
  %137 = fadd reassoc ninf nsz <4 x float> %136, %94
  %138 = insertelement <2 x float> %125, float 2.000000e+00, i64 1
  %139 = insertelement <2 x float> poison, float %99, i64 0
  %140 = shufflevector <2 x float> %139, <2 x float> poison, <2 x i32> zeroinitializer
  %141 = fmul reassoc ninf nsz <2 x float> %138, %140
  %142 = fadd reassoc ninf nsz <2 x float> %141, %96
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %143 = phi <2 x float> [ %142, %true_block ], [ %96, %for_loop_body ]
  %144 = phi <4 x float> [ %137, %true_block ], [ %94, %for_loop_body ]
  br i1 %27, label %true_block1, label %after_if3

true_block1:                                      ; preds = %after_if
  %145 = load float*, float** %24, align 8
  %146 = getelementptr float, float* %145, i64 2
  %147 = load float, float* %146, align 4
  %148 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %149 = add <2 x i32> %148, <i32 2, i32 -2>
  %150 = getelementptr inbounds i8, i8* %55, i64 8
  %151 = bitcast i8* %150 to i32*
  %152 = load i32, i32* %151, align 4
  %153 = add i32 %152, -1
  %154 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %149, i1 true)
  %155 = insertelement <2 x i32> poison, i32 %153, i64 0
  %156 = shufflevector <2 x i32> %155, <2 x i32> poison, <2 x i32> zeroinitializer
  %157 = sub <2 x i32> %154, %156
  %158 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %157, <2 x i32> zeroinitializer)
  %159 = mul <2 x i32> %158, <i32 -2, i32 -2>
  %160 = add <2 x i32> %159, %154
  %161 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %160, <2 x i32> zeroinitializer)
  %162 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %156, <2 x i32> %161)
  %163 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %164 = add <2 x i32> %162, %163
  %165 = insertelement <2 x i32> poison, i32 %69, i64 0
  %166 = shufflevector <2 x i32> %165, <2 x i32> poison, <2 x i32> zeroinitializer
  %167 = mul <2 x i32> %164, %166
  %168 = extractelement <2 x i32> %167, i64 1
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, float* %67, i64 %169
  %171 = load float, float* %170, align 4
  %172 = extractelement <2 x i32> %167, i64 0
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, float* %67, i64 %173
  %175 = load float, float* %174, align 4
  %176 = fadd reassoc ninf nsz float %175, %171
  %177 = add <2 x i32> %167, <i32 1, i32 1>
  %178 = extractelement <2 x i32> %177, i64 1
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, float* %67, i64 %179
  %181 = load float, float* %180, align 4
  %182 = extractelement <2 x i32> %177, i64 0
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, float* %67, i64 %183
  %185 = load float, float* %184, align 4
  %186 = shufflevector <2 x i32> %167, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %187 = add <2 x i32> %186, <i32 2, i32 3>
  %188 = sext <2 x i32> %187 to <2 x i64>
  %189 = insertelement <2 x float*> poison, float* %67, i64 0
  %190 = shufflevector <2 x float*> %189, <2 x float*> poison, <2 x i32> zeroinitializer
  %191 = getelementptr float, <2 x float*> %190, <2 x i64> %188
  %192 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %191, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %193 = shufflevector <2 x i32> %167, <2 x i32> undef, <2 x i32> zeroinitializer
  %194 = add <2 x i32> %193, <i32 2, i32 3>
  %195 = sext <2 x i32> %194 to <2 x i64>
  %196 = getelementptr float, <2 x float*> %190, <2 x i64> %195
  %197 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %196, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %198 = add <2 x i32> %167, <i32 4, i32 4>
  %199 = sext <2 x i32> %198 to <2 x i64>
  %200 = getelementptr float, <2 x float*> %190, <2 x i64> %199
  %201 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %200, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %202 = shufflevector <2 x float> %201, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %203 = insertelement <4 x float> poison, float %185, i64 0
  %204 = shufflevector <2 x float> %197, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %205 = shufflevector <4 x float> %203, <4 x float> %204, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %206 = shufflevector <4 x float> %205, <4 x float> %202, <4 x i32> <i32 0, i32 1, i32 2, i32 4>
  %207 = insertelement <4 x float> poison, float %181, i64 0
  %208 = shufflevector <2 x float> %192, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %209 = shufflevector <4 x float> %207, <4 x float> %208, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %210 = shufflevector <4 x float> %209, <4 x float> %202, <4 x i32> <i32 0, i32 1, i32 2, i32 5>
  %211 = fadd reassoc ninf nsz <4 x float> %206, %210
  %212 = insertelement <4 x float> poison, float %147, i64 0
  %shuffle342 = shufflevector <4 x float> %212, <4 x float> poison, <4 x i32> zeroinitializer
  %213 = fmul reassoc ninf nsz <4 x float> %211, %shuffle342
  %214 = fadd reassoc ninf nsz <4 x float> %213, %144
  %215 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %176, i64 0
  %216 = insertelement <2 x float> poison, float %147, i64 0
  %217 = shufflevector <2 x float> %216, <2 x float> poison, <2 x i32> zeroinitializer
  %218 = fmul reassoc ninf nsz <2 x float> %215, %217
  %219 = fadd reassoc ninf nsz <2 x float> %218, %143
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %after_if
  %220 = phi <4 x float> [ %214, %true_block1 ], [ %144, %after_if ]
  %221 = phi <2 x float> [ %219, %true_block1 ], [ %143, %after_if ]
  br i1 %28, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %222 = load float*, float** %24, align 8
  %223 = getelementptr float, float* %222, i64 3
  %224 = load float, float* %223, align 4
  %225 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %226 = add <2 x i32> %225, <i32 3, i32 -3>
  %227 = getelementptr inbounds i8, i8* %55, i64 8
  %228 = bitcast i8* %227 to i32*
  %229 = load i32, i32* %228, align 4
  %230 = add i32 %229, -1
  %231 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %226, i1 true)
  %232 = insertelement <2 x i32> poison, i32 %230, i64 0
  %233 = shufflevector <2 x i32> %232, <2 x i32> poison, <2 x i32> zeroinitializer
  %234 = sub <2 x i32> %231, %233
  %235 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %234, <2 x i32> zeroinitializer)
  %236 = mul <2 x i32> %235, <i32 -2, i32 -2>
  %237 = add <2 x i32> %236, %231
  %238 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %237, <2 x i32> zeroinitializer)
  %239 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %233, <2 x i32> %238)
  %240 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %241 = add <2 x i32> %239, %240
  %242 = insertelement <2 x i32> poison, i32 %69, i64 0
  %243 = shufflevector <2 x i32> %242, <2 x i32> poison, <2 x i32> zeroinitializer
  %244 = mul <2 x i32> %241, %243
  %245 = sext <2 x i32> %244 to <2 x i64>
  %246 = insertelement <2 x float*> poison, float* %67, i64 0
  %247 = shufflevector <2 x float*> %246, <2 x float*> poison, <2 x i32> zeroinitializer
  %248 = getelementptr float, <2 x float*> %247, <2 x i64> %245
  %249 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %248, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift351 = shufflevector <2 x float> %249, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %250 = fadd reassoc ninf nsz <2 x float> %249, %shift351
  %251 = shufflevector <2 x i32> %244, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %252 = add <4 x i32> %251, <i32 1, i32 2, i32 3, i32 4>
  %253 = sext <4 x i32> %252 to <4 x i64>
  %254 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %253
  %255 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %254, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %256 = shufflevector <2 x i32> %244, <2 x i32> undef, <4 x i32> zeroinitializer
  %257 = add <4 x i32> %256, <i32 1, i32 2, i32 3, i32 4>
  %258 = sext <4 x i32> %257 to <4 x i64>
  %259 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %258
  %260 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %259, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %261 = fadd reassoc ninf nsz <4 x float> %260, %255
  %262 = insertelement <4 x float> poison, float %224, i64 0
  %shuffle341 = shufflevector <4 x float> %262, <4 x float> poison, <4 x i32> zeroinitializer
  %263 = fmul reassoc ninf nsz <4 x float> %261, %shuffle341
  %264 = fadd reassoc ninf nsz <4 x float> %263, %220
  %265 = insertelement <2 x float> %250, float 2.000000e+00, i64 1
  %266 = insertelement <2 x float> poison, float %224, i64 0
  %267 = shufflevector <2 x float> %266, <2 x float> poison, <2 x i32> zeroinitializer
  %268 = fmul reassoc ninf nsz <2 x float> %265, %267
  %269 = fadd reassoc ninf nsz <2 x float> %268, %221
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %270 = phi <4 x float> [ %264, %true_block4 ], [ %220, %after_if3 ]
  %271 = phi <2 x float> [ %269, %true_block4 ], [ %221, %after_if3 ]
  br i1 %29, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %272 = load float*, float** %24, align 8
  %273 = getelementptr float, float* %272, i64 4
  %274 = load float, float* %273, align 4
  %275 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %276 = add <2 x i32> %275, <i32 4, i32 -4>
  %277 = getelementptr inbounds i8, i8* %55, i64 8
  %278 = bitcast i8* %277 to i32*
  %279 = load i32, i32* %278, align 4
  %280 = add i32 %279, -1
  %281 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %276, i1 true)
  %282 = insertelement <2 x i32> poison, i32 %280, i64 0
  %283 = shufflevector <2 x i32> %282, <2 x i32> poison, <2 x i32> zeroinitializer
  %284 = sub <2 x i32> %281, %283
  %285 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %284, <2 x i32> zeroinitializer)
  %286 = mul <2 x i32> %285, <i32 -2, i32 -2>
  %287 = add <2 x i32> %286, %281
  %288 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %287, <2 x i32> zeroinitializer)
  %289 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %283, <2 x i32> %288)
  %290 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %291 = add <2 x i32> %289, %290
  %292 = insertelement <2 x i32> poison, i32 %69, i64 0
  %293 = shufflevector <2 x i32> %292, <2 x i32> poison, <2 x i32> zeroinitializer
  %294 = mul <2 x i32> %291, %293
  %295 = sext <2 x i32> %294 to <2 x i64>
  %296 = insertelement <2 x float*> poison, float* %67, i64 0
  %297 = shufflevector <2 x float*> %296, <2 x float*> poison, <2 x i32> zeroinitializer
  %298 = getelementptr float, <2 x float*> %297, <2 x i64> %295
  %299 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %298, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift352 = shufflevector <2 x float> %299, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %300 = fadd reassoc ninf nsz <2 x float> %299, %shift352
  %301 = add <2 x i32> %294, <i32 1, i32 1>
  %302 = extractelement <2 x i32> %301, i64 1
  %303 = sext i32 %302 to i64
  %304 = getelementptr float, float* %67, i64 %303
  %305 = extractelement <2 x i32> %301, i64 0
  %306 = sext i32 %305 to i64
  %307 = getelementptr float, float* %67, i64 %306
  %308 = shufflevector <2 x i32> %294, <2 x i32> undef, <4 x i32> <i32 1, i32 0, i32 1, i32 0>
  %309 = add <4 x i32> %308, <i32 2, i32 2, i32 3, i32 3>
  %310 = extractelement <4 x i32> %309, i64 0
  %311 = sext i32 %310 to i64
  %312 = getelementptr float, float* %67, i64 %311
  %313 = extractelement <4 x i32> %309, i64 1
  %314 = sext i32 %313 to i64
  %315 = getelementptr float, float* %67, i64 %314
  %316 = extractelement <4 x i32> %309, i64 2
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, float* %67, i64 %317
  %319 = extractelement <4 x i32> %309, i64 3
  %320 = sext i32 %319 to i64
  %321 = getelementptr float, float* %67, i64 %320
  %322 = add <2 x i32> %294, <i32 4, i32 4>
  %323 = extractelement <2 x i32> %322, i64 1
  %324 = sext i32 %323 to i64
  %325 = getelementptr float, float* %67, i64 %324
  %326 = extractelement <2 x i32> %322, i64 0
  %327 = sext i32 %326 to i64
  %328 = getelementptr float, float* %67, i64 %327
  %329 = insertelement <4 x float*> poison, float* %304, i64 0
  %330 = insertelement <4 x float*> %329, float* %312, i64 1
  %331 = insertelement <4 x float*> %330, float* %318, i64 2
  %332 = insertelement <4 x float*> %331, float* %325, i64 3
  %333 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %332, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %334 = insertelement <4 x float*> poison, float* %307, i64 0
  %335 = insertelement <4 x float*> %334, float* %315, i64 1
  %336 = insertelement <4 x float*> %335, float* %321, i64 2
  %337 = insertelement <4 x float*> %336, float* %328, i64 3
  %338 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %337, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %339 = fadd reassoc ninf nsz <4 x float> %338, %333
  %340 = insertelement <4 x float> poison, float %274, i64 0
  %shuffle338 = shufflevector <4 x float> %340, <4 x float> poison, <4 x i32> zeroinitializer
  %341 = fmul reassoc ninf nsz <4 x float> %339, %shuffle338
  %342 = fadd reassoc ninf nsz <4 x float> %341, %270
  %343 = insertelement <2 x float> %300, float 2.000000e+00, i64 1
  %344 = insertelement <2 x float> poison, float %274, i64 0
  %345 = shufflevector <2 x float> %344, <2 x float> poison, <2 x i32> zeroinitializer
  %346 = fmul reassoc ninf nsz <2 x float> %343, %345
  %347 = fadd reassoc ninf nsz <2 x float> %346, %271
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %348 = phi <4 x float> [ %342, %true_block7 ], [ %270, %after_if6 ]
  %349 = phi <2 x float> [ %347, %true_block7 ], [ %271, %after_if6 ]
  br i1 %30, label %true_block10, label %after_if12

true_block10:                                     ; preds = %after_if9
  %350 = load float*, float** %24, align 8
  %351 = getelementptr float, float* %350, i64 5
  %352 = load float, float* %351, align 4
  %353 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %354 = add <2 x i32> %353, <i32 5, i32 -5>
  %355 = getelementptr inbounds i8, i8* %55, i64 8
  %356 = bitcast i8* %355 to i32*
  %357 = load i32, i32* %356, align 4
  %358 = add i32 %357, -1
  %359 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %354, i1 true)
  %360 = insertelement <2 x i32> poison, i32 %358, i64 0
  %361 = shufflevector <2 x i32> %360, <2 x i32> poison, <2 x i32> zeroinitializer
  %362 = sub <2 x i32> %359, %361
  %363 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %362, <2 x i32> zeroinitializer)
  %364 = mul <2 x i32> %363, <i32 -2, i32 -2>
  %365 = add <2 x i32> %364, %359
  %366 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %365, <2 x i32> zeroinitializer)
  %367 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %361, <2 x i32> %366)
  %368 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %369 = add <2 x i32> %367, %368
  %370 = insertelement <2 x i32> poison, i32 %69, i64 0
  %371 = shufflevector <2 x i32> %370, <2 x i32> poison, <2 x i32> zeroinitializer
  %372 = mul <2 x i32> %369, %371
  %373 = sext <2 x i32> %372 to <2 x i64>
  %374 = insertelement <2 x float*> poison, float* %67, i64 0
  %375 = shufflevector <2 x float*> %374, <2 x float*> poison, <2 x i32> zeroinitializer
  %376 = getelementptr float, <2 x float*> %375, <2 x i64> %373
  %377 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %376, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift353 = shufflevector <2 x float> %377, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %378 = fadd reassoc ninf nsz <2 x float> %377, %shift353
  %379 = shufflevector <2 x i32> %372, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %380 = add <4 x i32> %379, <i32 1, i32 2, i32 3, i32 4>
  %381 = sext <4 x i32> %380 to <4 x i64>
  %382 = shufflevector <2 x i32> %372, <2 x i32> undef, <4 x i32> zeroinitializer
  %383 = add <4 x i32> %382, <i32 1, i32 2, i32 3, i32 4>
  %384 = sext <4 x i32> %383 to <4 x i64>
  %385 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %381
  %386 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %385, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %387 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %384
  %388 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %387, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %389 = fadd reassoc ninf nsz <4 x float> %388, %386
  %390 = insertelement <4 x float> poison, float %352, i64 0
  %shuffle337 = shufflevector <4 x float> %390, <4 x float> poison, <4 x i32> zeroinitializer
  %391 = fmul reassoc ninf nsz <4 x float> %389, %shuffle337
  %392 = fadd reassoc ninf nsz <4 x float> %391, %348
  %393 = insertelement <2 x float> %378, float 2.000000e+00, i64 1
  %394 = insertelement <2 x float> poison, float %352, i64 0
  %395 = shufflevector <2 x float> %394, <2 x float> poison, <2 x i32> zeroinitializer
  %396 = fmul reassoc ninf nsz <2 x float> %393, %395
  %397 = fadd reassoc ninf nsz <2 x float> %396, %349
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %398 = phi <4 x float> [ %392, %true_block10 ], [ %348, %after_if9 ]
  %399 = phi <2 x float> [ %397, %true_block10 ], [ %349, %after_if9 ]
  br i1 %31, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if12
  %400 = load float*, float** %24, align 8
  %401 = getelementptr float, float* %400, i64 6
  %402 = load float, float* %401, align 4
  %403 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %404 = add <2 x i32> %403, <i32 6, i32 -6>
  %405 = getelementptr inbounds i8, i8* %55, i64 8
  %406 = bitcast i8* %405 to i32*
  %407 = load i32, i32* %406, align 4
  %408 = add i32 %407, -1
  %409 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %404, i1 true)
  %410 = insertelement <2 x i32> poison, i32 %408, i64 0
  %411 = shufflevector <2 x i32> %410, <2 x i32> poison, <2 x i32> zeroinitializer
  %412 = sub <2 x i32> %409, %411
  %413 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %412, <2 x i32> zeroinitializer)
  %414 = mul <2 x i32> %413, <i32 -2, i32 -2>
  %415 = add <2 x i32> %414, %409
  %416 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %415, <2 x i32> zeroinitializer)
  %417 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %411, <2 x i32> %416)
  %418 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %419 = add <2 x i32> %417, %418
  %420 = insertelement <2 x i32> poison, i32 %69, i64 0
  %421 = shufflevector <2 x i32> %420, <2 x i32> poison, <2 x i32> zeroinitializer
  %422 = mul <2 x i32> %419, %421
  %423 = sext <2 x i32> %422 to <2 x i64>
  %424 = insertelement <2 x float*> poison, float* %67, i64 0
  %425 = shufflevector <2 x float*> %424, <2 x float*> poison, <2 x i32> zeroinitializer
  %426 = getelementptr float, <2 x float*> %425, <2 x i64> %423
  %427 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %426, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift354 = shufflevector <2 x float> %427, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %428 = fadd reassoc ninf nsz <2 x float> %427, %shift354
  %shuffle333 = shufflevector <2 x i32> %422, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %429 = add <4 x i32> %shuffle333, <i32 1, i32 2, i32 3, i32 4>
  %430 = sext <4 x i32> %429 to <4 x i64>
  %431 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %430
  %432 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %431, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle331 = shufflevector <2 x i32> %422, <2 x i32> poison, <4 x i32> zeroinitializer
  %433 = add <4 x i32> %shuffle331, <i32 1, i32 2, i32 3, i32 4>
  %434 = sext <4 x i32> %433 to <4 x i64>
  %435 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %434
  %436 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %435, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %437 = fadd reassoc ninf nsz <4 x float> %436, %432
  %438 = insertelement <4 x float> poison, float %402, i64 0
  %shuffle334 = shufflevector <4 x float> %438, <4 x float> poison, <4 x i32> zeroinitializer
  %439 = fmul reassoc ninf nsz <4 x float> %437, %shuffle334
  %440 = fadd reassoc ninf nsz <4 x float> %439, %398
  %441 = insertelement <2 x float> %428, float 2.000000e+00, i64 1
  %442 = insertelement <2 x float> poison, float %402, i64 0
  %443 = shufflevector <2 x float> %442, <2 x float> poison, <2 x i32> zeroinitializer
  %444 = fmul reassoc ninf nsz <2 x float> %441, %443
  %445 = fadd reassoc ninf nsz <2 x float> %444, %399
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if12
  %446 = phi <4 x float> [ %440, %true_block13 ], [ %398, %after_if12 ]
  %447 = phi <2 x float> [ %445, %true_block13 ], [ %399, %after_if12 ]
  br i1 %32, label %true_block16, label %after_if18

true_block16:                                     ; preds = %after_if15
  %448 = load float*, float** %24, align 8
  %449 = getelementptr float, float* %448, i64 7
  %450 = load float, float* %449, align 4
  %451 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %452 = add <2 x i32> %451, <i32 7, i32 -7>
  %453 = getelementptr inbounds i8, i8* %55, i64 8
  %454 = bitcast i8* %453 to i32*
  %455 = load i32, i32* %454, align 4
  %456 = add i32 %455, -1
  %457 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %452, i1 true)
  %458 = insertelement <2 x i32> poison, i32 %456, i64 0
  %459 = shufflevector <2 x i32> %458, <2 x i32> poison, <2 x i32> zeroinitializer
  %460 = sub <2 x i32> %457, %459
  %461 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %460, <2 x i32> zeroinitializer)
  %462 = mul <2 x i32> %461, <i32 -2, i32 -2>
  %463 = add <2 x i32> %462, %457
  %464 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %463, <2 x i32> zeroinitializer)
  %465 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %459, <2 x i32> %464)
  %466 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %467 = add <2 x i32> %465, %466
  %468 = insertelement <2 x i32> poison, i32 %69, i64 0
  %469 = shufflevector <2 x i32> %468, <2 x i32> poison, <2 x i32> zeroinitializer
  %470 = mul <2 x i32> %467, %469
  %471 = sext <2 x i32> %470 to <2 x i64>
  %472 = insertelement <2 x float*> poison, float* %67, i64 0
  %473 = shufflevector <2 x float*> %472, <2 x float*> poison, <2 x i32> zeroinitializer
  %474 = getelementptr float, <2 x float*> %473, <2 x i64> %471
  %475 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %474, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift355 = shufflevector <2 x float> %475, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %476 = fadd reassoc ninf nsz <2 x float> %475, %shift355
  %shuffle328 = shufflevector <2 x i32> %470, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %477 = add <4 x i32> %shuffle328, <i32 1, i32 2, i32 3, i32 4>
  %478 = sext <4 x i32> %477 to <4 x i64>
  %479 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %478
  %480 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %479, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle326 = shufflevector <2 x i32> %470, <2 x i32> poison, <4 x i32> zeroinitializer
  %481 = add <4 x i32> %shuffle326, <i32 1, i32 2, i32 3, i32 4>
  %482 = sext <4 x i32> %481 to <4 x i64>
  %483 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %482
  %484 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %483, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %485 = fadd reassoc ninf nsz <4 x float> %484, %480
  %486 = insertelement <4 x float> poison, float %450, i64 0
  %shuffle329 = shufflevector <4 x float> %486, <4 x float> poison, <4 x i32> zeroinitializer
  %487 = fmul reassoc ninf nsz <4 x float> %485, %shuffle329
  %488 = fadd reassoc ninf nsz <4 x float> %487, %446
  %489 = insertelement <2 x float> %476, float 2.000000e+00, i64 1
  %490 = insertelement <2 x float> poison, float %450, i64 0
  %491 = shufflevector <2 x float> %490, <2 x float> poison, <2 x i32> zeroinitializer
  %492 = fmul reassoc ninf nsz <2 x float> %489, %491
  %493 = fadd reassoc ninf nsz <2 x float> %492, %447
  br label %after_if18

after_if18:                                       ; preds = %true_block16, %after_if15
  %494 = phi <2 x float> [ %493, %true_block16 ], [ %447, %after_if15 ]
  %495 = phi <4 x float> [ %488, %true_block16 ], [ %446, %after_if15 ]
  br i1 %33, label %true_block19, label %after_if21

true_block19:                                     ; preds = %after_if18
  %496 = load float*, float** %24, align 8
  %497 = getelementptr float, float* %496, i64 8
  %498 = load float, float* %497, align 4
  %499 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %500 = add <2 x i32> %499, <i32 8, i32 -8>
  %501 = getelementptr inbounds i8, i8* %55, i64 8
  %502 = bitcast i8* %501 to i32*
  %503 = load i32, i32* %502, align 4
  %504 = add i32 %503, -1
  %505 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %500, i1 true)
  %506 = insertelement <2 x i32> poison, i32 %504, i64 0
  %507 = shufflevector <2 x i32> %506, <2 x i32> poison, <2 x i32> zeroinitializer
  %508 = sub <2 x i32> %505, %507
  %509 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %508, <2 x i32> zeroinitializer)
  %510 = mul <2 x i32> %509, <i32 -2, i32 -2>
  %511 = add <2 x i32> %510, %505
  %512 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %511, <2 x i32> zeroinitializer)
  %513 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %507, <2 x i32> %512)
  %514 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %515 = add <2 x i32> %513, %514
  %516 = insertelement <2 x i32> poison, i32 %69, i64 0
  %517 = shufflevector <2 x i32> %516, <2 x i32> poison, <2 x i32> zeroinitializer
  %518 = mul <2 x i32> %515, %517
  %519 = extractelement <2 x i32> %518, i64 1
  %520 = sext i32 %519 to i64
  %521 = getelementptr float, float* %67, i64 %520
  %522 = load float, float* %521, align 4
  %523 = extractelement <2 x i32> %518, i64 0
  %524 = sext i32 %523 to i64
  %525 = getelementptr float, float* %67, i64 %524
  %526 = load float, float* %525, align 4
  %527 = fadd reassoc ninf nsz float %526, %522
  %528 = add <2 x i32> %518, <i32 1, i32 1>
  %529 = extractelement <2 x i32> %528, i64 1
  %530 = sext i32 %529 to i64
  %531 = getelementptr float, float* %67, i64 %530
  %532 = load float, float* %531, align 4
  %533 = extractelement <2 x i32> %528, i64 0
  %534 = sext i32 %533 to i64
  %535 = getelementptr float, float* %67, i64 %534
  %536 = load float, float* %535, align 4
  %537 = shufflevector <2 x i32> %518, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %538 = add <2 x i32> %537, <i32 2, i32 3>
  %539 = sext <2 x i32> %538 to <2 x i64>
  %540 = insertelement <2 x float*> poison, float* %67, i64 0
  %541 = shufflevector <2 x float*> %540, <2 x float*> poison, <2 x i32> zeroinitializer
  %542 = getelementptr float, <2 x float*> %541, <2 x i64> %539
  %543 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %542, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %544 = shufflevector <2 x i32> %518, <2 x i32> undef, <2 x i32> zeroinitializer
  %545 = add <2 x i32> %544, <i32 2, i32 3>
  %546 = sext <2 x i32> %545 to <2 x i64>
  %547 = getelementptr float, <2 x float*> %541, <2 x i64> %546
  %548 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %547, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %549 = add <2 x i32> %518, <i32 4, i32 4>
  %550 = sext <2 x i32> %549 to <2 x i64>
  %551 = getelementptr float, <2 x float*> %541, <2 x i64> %550
  %552 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %551, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %553 = shufflevector <2 x float> %552, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %554 = insertelement <4 x float> poison, float %536, i64 0
  %555 = shufflevector <2 x float> %548, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %556 = shufflevector <4 x float> %554, <4 x float> %555, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %557 = shufflevector <4 x float> %556, <4 x float> %553, <4 x i32> <i32 0, i32 1, i32 2, i32 4>
  %558 = insertelement <4 x float> poison, float %532, i64 0
  %559 = shufflevector <2 x float> %543, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %560 = shufflevector <4 x float> %558, <4 x float> %559, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %561 = shufflevector <4 x float> %560, <4 x float> %553, <4 x i32> <i32 0, i32 1, i32 2, i32 5>
  %562 = fadd reassoc ninf nsz <4 x float> %557, %561
  %563 = insertelement <4 x float> poison, float %498, i64 0
  %shuffle324 = shufflevector <4 x float> %563, <4 x float> poison, <4 x i32> zeroinitializer
  %564 = fmul reassoc ninf nsz <4 x float> %562, %shuffle324
  %565 = fadd reassoc ninf nsz <4 x float> %564, %495
  %566 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %527, i64 0
  %567 = insertelement <2 x float> poison, float %498, i64 0
  %568 = shufflevector <2 x float> %567, <2 x float> poison, <2 x i32> zeroinitializer
  %569 = fmul reassoc ninf nsz <2 x float> %566, %568
  %570 = fadd reassoc ninf nsz <2 x float> %569, %494
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if18
  %571 = phi <4 x float> [ %565, %true_block19 ], [ %495, %after_if18 ]
  %572 = phi <2 x float> [ %570, %true_block19 ], [ %494, %after_if18 ]
  br i1 %34, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if21
  %573 = load float*, float** %24, align 8
  %574 = getelementptr float, float* %573, i64 9
  %575 = load float, float* %574, align 4
  %576 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %577 = add <2 x i32> %576, <i32 9, i32 -9>
  %578 = getelementptr inbounds i8, i8* %55, i64 8
  %579 = bitcast i8* %578 to i32*
  %580 = load i32, i32* %579, align 4
  %581 = add i32 %580, -1
  %582 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %577, i1 true)
  %583 = insertelement <2 x i32> poison, i32 %581, i64 0
  %584 = shufflevector <2 x i32> %583, <2 x i32> poison, <2 x i32> zeroinitializer
  %585 = sub <2 x i32> %582, %584
  %586 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %585, <2 x i32> zeroinitializer)
  %587 = mul <2 x i32> %586, <i32 -2, i32 -2>
  %588 = add <2 x i32> %587, %582
  %589 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %588, <2 x i32> zeroinitializer)
  %590 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %584, <2 x i32> %589)
  %591 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %592 = add <2 x i32> %590, %591
  %593 = insertelement <2 x i32> poison, i32 %69, i64 0
  %594 = shufflevector <2 x i32> %593, <2 x i32> poison, <2 x i32> zeroinitializer
  %595 = mul <2 x i32> %592, %594
  %596 = sext <2 x i32> %595 to <2 x i64>
  %597 = insertelement <2 x float*> poison, float* %67, i64 0
  %598 = shufflevector <2 x float*> %597, <2 x float*> poison, <2 x i32> zeroinitializer
  %599 = getelementptr float, <2 x float*> %598, <2 x i64> %596
  %600 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %599, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift356 = shufflevector <2 x float> %600, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %601 = fadd reassoc ninf nsz <2 x float> %600, %shift356
  %602 = shufflevector <2 x i32> %595, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %603 = add <4 x i32> %602, <i32 1, i32 2, i32 3, i32 4>
  %604 = sext <4 x i32> %603 to <4 x i64>
  %605 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %604
  %606 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %605, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %607 = shufflevector <2 x i32> %595, <2 x i32> undef, <4 x i32> zeroinitializer
  %608 = add <4 x i32> %607, <i32 1, i32 2, i32 3, i32 4>
  %609 = sext <4 x i32> %608 to <4 x i64>
  %610 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %609
  %611 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %610, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %612 = fadd reassoc ninf nsz <4 x float> %611, %606
  %613 = insertelement <4 x float> poison, float %575, i64 0
  %shuffle323 = shufflevector <4 x float> %613, <4 x float> poison, <4 x i32> zeroinitializer
  %614 = fmul reassoc ninf nsz <4 x float> %612, %shuffle323
  %615 = fadd reassoc ninf nsz <4 x float> %614, %571
  %616 = insertelement <2 x float> %601, float 2.000000e+00, i64 1
  %617 = insertelement <2 x float> poison, float %575, i64 0
  %618 = shufflevector <2 x float> %617, <2 x float> poison, <2 x i32> zeroinitializer
  %619 = fmul reassoc ninf nsz <2 x float> %616, %618
  %620 = fadd reassoc ninf nsz <2 x float> %619, %572
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if21
  %621 = phi <4 x float> [ %615, %true_block22 ], [ %571, %after_if21 ]
  %622 = phi <2 x float> [ %620, %true_block22 ], [ %572, %after_if21 ]
  br i1 %35, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if24
  %623 = load float*, float** %24, align 8
  %624 = getelementptr float, float* %623, i64 10
  %625 = load float, float* %624, align 4
  %626 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %627 = add <2 x i32> %626, <i32 10, i32 -10>
  %628 = getelementptr inbounds i8, i8* %55, i64 8
  %629 = bitcast i8* %628 to i32*
  %630 = load i32, i32* %629, align 4
  %631 = add i32 %630, -1
  %632 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %627, i1 true)
  %633 = insertelement <2 x i32> poison, i32 %631, i64 0
  %634 = shufflevector <2 x i32> %633, <2 x i32> poison, <2 x i32> zeroinitializer
  %635 = sub <2 x i32> %632, %634
  %636 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %635, <2 x i32> zeroinitializer)
  %637 = mul <2 x i32> %636, <i32 -2, i32 -2>
  %638 = add <2 x i32> %637, %632
  %639 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %638, <2 x i32> zeroinitializer)
  %640 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %634, <2 x i32> %639)
  %641 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %642 = add <2 x i32> %640, %641
  %643 = insertelement <2 x i32> poison, i32 %69, i64 0
  %644 = shufflevector <2 x i32> %643, <2 x i32> poison, <2 x i32> zeroinitializer
  %645 = mul <2 x i32> %642, %644
  %646 = sext <2 x i32> %645 to <2 x i64>
  %647 = insertelement <2 x float*> poison, float* %67, i64 0
  %648 = shufflevector <2 x float*> %647, <2 x float*> poison, <2 x i32> zeroinitializer
  %649 = getelementptr float, <2 x float*> %648, <2 x i64> %646
  %650 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %649, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift357 = shufflevector <2 x float> %650, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %651 = fadd reassoc ninf nsz <2 x float> %650, %shift357
  %652 = add <2 x i32> %645, <i32 1, i32 1>
  %653 = extractelement <2 x i32> %652, i64 1
  %654 = sext i32 %653 to i64
  %655 = getelementptr float, float* %67, i64 %654
  %656 = extractelement <2 x i32> %652, i64 0
  %657 = sext i32 %656 to i64
  %658 = getelementptr float, float* %67, i64 %657
  %659 = shufflevector <2 x i32> %645, <2 x i32> undef, <4 x i32> <i32 1, i32 0, i32 1, i32 0>
  %660 = add <4 x i32> %659, <i32 2, i32 2, i32 3, i32 3>
  %661 = extractelement <4 x i32> %660, i64 0
  %662 = sext i32 %661 to i64
  %663 = getelementptr float, float* %67, i64 %662
  %664 = extractelement <4 x i32> %660, i64 1
  %665 = sext i32 %664 to i64
  %666 = getelementptr float, float* %67, i64 %665
  %667 = extractelement <4 x i32> %660, i64 2
  %668 = sext i32 %667 to i64
  %669 = getelementptr float, float* %67, i64 %668
  %670 = extractelement <4 x i32> %660, i64 3
  %671 = sext i32 %670 to i64
  %672 = getelementptr float, float* %67, i64 %671
  %673 = add <2 x i32> %645, <i32 4, i32 4>
  %674 = extractelement <2 x i32> %673, i64 1
  %675 = sext i32 %674 to i64
  %676 = getelementptr float, float* %67, i64 %675
  %677 = extractelement <2 x i32> %673, i64 0
  %678 = sext i32 %677 to i64
  %679 = getelementptr float, float* %67, i64 %678
  %680 = insertelement <4 x float*> poison, float* %655, i64 0
  %681 = insertelement <4 x float*> %680, float* %663, i64 1
  %682 = insertelement <4 x float*> %681, float* %669, i64 2
  %683 = insertelement <4 x float*> %682, float* %676, i64 3
  %684 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %683, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %685 = insertelement <4 x float*> poison, float* %658, i64 0
  %686 = insertelement <4 x float*> %685, float* %666, i64 1
  %687 = insertelement <4 x float*> %686, float* %672, i64 2
  %688 = insertelement <4 x float*> %687, float* %679, i64 3
  %689 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %688, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %690 = fadd reassoc ninf nsz <4 x float> %689, %684
  %691 = insertelement <4 x float> poison, float %625, i64 0
  %shuffle320 = shufflevector <4 x float> %691, <4 x float> poison, <4 x i32> zeroinitializer
  %692 = fmul reassoc ninf nsz <4 x float> %690, %shuffle320
  %693 = fadd reassoc ninf nsz <4 x float> %692, %621
  %694 = insertelement <2 x float> %651, float 2.000000e+00, i64 1
  %695 = insertelement <2 x float> poison, float %625, i64 0
  %696 = shufflevector <2 x float> %695, <2 x float> poison, <2 x i32> zeroinitializer
  %697 = fmul reassoc ninf nsz <2 x float> %694, %696
  %698 = fadd reassoc ninf nsz <2 x float> %697, %622
  br label %after_if27

after_if27:                                       ; preds = %true_block25, %after_if24
  %699 = phi <4 x float> [ %693, %true_block25 ], [ %621, %after_if24 ]
  %700 = phi <2 x float> [ %698, %true_block25 ], [ %622, %after_if24 ]
  br i1 %36, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %701 = load float*, float** %24, align 8
  %702 = getelementptr float, float* %701, i64 11
  %703 = load float, float* %702, align 4
  %704 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %705 = add <2 x i32> %704, <i32 11, i32 -11>
  %706 = getelementptr inbounds i8, i8* %55, i64 8
  %707 = bitcast i8* %706 to i32*
  %708 = load i32, i32* %707, align 4
  %709 = add i32 %708, -1
  %710 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %705, i1 true)
  %711 = insertelement <2 x i32> poison, i32 %709, i64 0
  %712 = shufflevector <2 x i32> %711, <2 x i32> poison, <2 x i32> zeroinitializer
  %713 = sub <2 x i32> %710, %712
  %714 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %713, <2 x i32> zeroinitializer)
  %715 = mul <2 x i32> %714, <i32 -2, i32 -2>
  %716 = add <2 x i32> %715, %710
  %717 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %716, <2 x i32> zeroinitializer)
  %718 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %712, <2 x i32> %717)
  %719 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %720 = add <2 x i32> %718, %719
  %721 = insertelement <2 x i32> poison, i32 %69, i64 0
  %722 = shufflevector <2 x i32> %721, <2 x i32> poison, <2 x i32> zeroinitializer
  %723 = mul <2 x i32> %720, %722
  %724 = sext <2 x i32> %723 to <2 x i64>
  %725 = insertelement <2 x float*> poison, float* %67, i64 0
  %726 = shufflevector <2 x float*> %725, <2 x float*> poison, <2 x i32> zeroinitializer
  %727 = getelementptr float, <2 x float*> %726, <2 x i64> %724
  %728 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %727, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift358 = shufflevector <2 x float> %728, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %729 = fadd reassoc ninf nsz <2 x float> %728, %shift358
  %730 = shufflevector <2 x i32> %723, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %731 = add <4 x i32> %730, <i32 1, i32 2, i32 3, i32 4>
  %732 = sext <4 x i32> %731 to <4 x i64>
  %733 = shufflevector <2 x i32> %723, <2 x i32> undef, <4 x i32> zeroinitializer
  %734 = add <4 x i32> %733, <i32 1, i32 2, i32 3, i32 4>
  %735 = sext <4 x i32> %734 to <4 x i64>
  %736 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %732
  %737 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %736, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %738 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %735
  %739 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %738, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %740 = fadd reassoc ninf nsz <4 x float> %739, %737
  %741 = insertelement <4 x float> poison, float %703, i64 0
  %shuffle319 = shufflevector <4 x float> %741, <4 x float> poison, <4 x i32> zeroinitializer
  %742 = fmul reassoc ninf nsz <4 x float> %740, %shuffle319
  %743 = fadd reassoc ninf nsz <4 x float> %742, %699
  %744 = insertelement <2 x float> %729, float 2.000000e+00, i64 1
  %745 = insertelement <2 x float> poison, float %703, i64 0
  %746 = shufflevector <2 x float> %745, <2 x float> poison, <2 x i32> zeroinitializer
  %747 = fmul reassoc ninf nsz <2 x float> %744, %746
  %748 = fadd reassoc ninf nsz <2 x float> %747, %700
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27
  %749 = phi <4 x float> [ %743, %true_block28 ], [ %699, %after_if27 ]
  %750 = phi <2 x float> [ %748, %true_block28 ], [ %700, %after_if27 ]
  br i1 %37, label %true_block31, label %after_if33

true_block31:                                     ; preds = %after_if30
  %751 = load float*, float** %24, align 8
  %752 = getelementptr float, float* %751, i64 12
  %753 = load float, float* %752, align 4
  %754 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %755 = add <2 x i32> %754, <i32 12, i32 -12>
  %756 = getelementptr inbounds i8, i8* %55, i64 8
  %757 = bitcast i8* %756 to i32*
  %758 = load i32, i32* %757, align 4
  %759 = add i32 %758, -1
  %760 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %755, i1 true)
  %761 = insertelement <2 x i32> poison, i32 %759, i64 0
  %762 = shufflevector <2 x i32> %761, <2 x i32> poison, <2 x i32> zeroinitializer
  %763 = sub <2 x i32> %760, %762
  %764 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %763, <2 x i32> zeroinitializer)
  %765 = mul <2 x i32> %764, <i32 -2, i32 -2>
  %766 = add <2 x i32> %765, %760
  %767 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %766, <2 x i32> zeroinitializer)
  %768 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %762, <2 x i32> %767)
  %769 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %770 = add <2 x i32> %768, %769
  %771 = insertelement <2 x i32> poison, i32 %69, i64 0
  %772 = shufflevector <2 x i32> %771, <2 x i32> poison, <2 x i32> zeroinitializer
  %773 = mul <2 x i32> %770, %772
  %774 = sext <2 x i32> %773 to <2 x i64>
  %775 = insertelement <2 x float*> poison, float* %67, i64 0
  %776 = shufflevector <2 x float*> %775, <2 x float*> poison, <2 x i32> zeroinitializer
  %777 = getelementptr float, <2 x float*> %776, <2 x i64> %774
  %778 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %777, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift359 = shufflevector <2 x float> %778, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %779 = fadd reassoc ninf nsz <2 x float> %778, %shift359
  %shuffle315 = shufflevector <2 x i32> %773, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %780 = add <4 x i32> %shuffle315, <i32 1, i32 2, i32 3, i32 4>
  %781 = sext <4 x i32> %780 to <4 x i64>
  %782 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %781
  %783 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %782, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle313 = shufflevector <2 x i32> %773, <2 x i32> poison, <4 x i32> zeroinitializer
  %784 = add <4 x i32> %shuffle313, <i32 1, i32 2, i32 3, i32 4>
  %785 = sext <4 x i32> %784 to <4 x i64>
  %786 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %785
  %787 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %786, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %788 = fadd reassoc ninf nsz <4 x float> %787, %783
  %789 = insertelement <4 x float> poison, float %753, i64 0
  %shuffle316 = shufflevector <4 x float> %789, <4 x float> poison, <4 x i32> zeroinitializer
  %790 = fmul reassoc ninf nsz <4 x float> %788, %shuffle316
  %791 = fadd reassoc ninf nsz <4 x float> %790, %749
  %792 = insertelement <2 x float> %779, float 2.000000e+00, i64 1
  %793 = insertelement <2 x float> poison, float %753, i64 0
  %794 = shufflevector <2 x float> %793, <2 x float> poison, <2 x i32> zeroinitializer
  %795 = fmul reassoc ninf nsz <2 x float> %792, %794
  %796 = fadd reassoc ninf nsz <2 x float> %795, %750
  br label %after_if33

after_if33:                                       ; preds = %true_block31, %after_if30
  %797 = phi <4 x float> [ %791, %true_block31 ], [ %749, %after_if30 ]
  %798 = phi <2 x float> [ %796, %true_block31 ], [ %750, %after_if30 ]
  br i1 %38, label %true_block34, label %after_if36

true_block34:                                     ; preds = %after_if33
  %799 = load float*, float** %24, align 8
  %800 = getelementptr float, float* %799, i64 13
  %801 = load float, float* %800, align 4
  %802 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %803 = add <2 x i32> %802, <i32 13, i32 -13>
  %804 = getelementptr inbounds i8, i8* %55, i64 8
  %805 = bitcast i8* %804 to i32*
  %806 = load i32, i32* %805, align 4
  %807 = add i32 %806, -1
  %808 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %803, i1 true)
  %809 = insertelement <2 x i32> poison, i32 %807, i64 0
  %810 = shufflevector <2 x i32> %809, <2 x i32> poison, <2 x i32> zeroinitializer
  %811 = sub <2 x i32> %808, %810
  %812 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %811, <2 x i32> zeroinitializer)
  %813 = mul <2 x i32> %812, <i32 -2, i32 -2>
  %814 = add <2 x i32> %813, %808
  %815 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %814, <2 x i32> zeroinitializer)
  %816 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %810, <2 x i32> %815)
  %817 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %818 = add <2 x i32> %816, %817
  %819 = insertelement <2 x i32> poison, i32 %69, i64 0
  %820 = shufflevector <2 x i32> %819, <2 x i32> poison, <2 x i32> zeroinitializer
  %821 = mul <2 x i32> %818, %820
  %822 = sext <2 x i32> %821 to <2 x i64>
  %823 = insertelement <2 x float*> poison, float* %67, i64 0
  %824 = shufflevector <2 x float*> %823, <2 x float*> poison, <2 x i32> zeroinitializer
  %825 = getelementptr float, <2 x float*> %824, <2 x i64> %822
  %826 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %825, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift360 = shufflevector <2 x float> %826, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %827 = fadd reassoc ninf nsz <2 x float> %826, %shift360
  %shuffle310 = shufflevector <2 x i32> %821, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %828 = add <4 x i32> %shuffle310, <i32 1, i32 2, i32 3, i32 4>
  %829 = sext <4 x i32> %828 to <4 x i64>
  %830 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %829
  %831 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %830, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle308 = shufflevector <2 x i32> %821, <2 x i32> poison, <4 x i32> zeroinitializer
  %832 = add <4 x i32> %shuffle308, <i32 1, i32 2, i32 3, i32 4>
  %833 = sext <4 x i32> %832 to <4 x i64>
  %834 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %833
  %835 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %834, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %836 = fadd reassoc ninf nsz <4 x float> %835, %831
  %837 = insertelement <4 x float> poison, float %801, i64 0
  %shuffle311 = shufflevector <4 x float> %837, <4 x float> poison, <4 x i32> zeroinitializer
  %838 = fmul reassoc ninf nsz <4 x float> %836, %shuffle311
  %839 = fadd reassoc ninf nsz <4 x float> %838, %797
  %840 = insertelement <2 x float> %827, float 2.000000e+00, i64 1
  %841 = insertelement <2 x float> poison, float %801, i64 0
  %842 = shufflevector <2 x float> %841, <2 x float> poison, <2 x i32> zeroinitializer
  %843 = fmul reassoc ninf nsz <2 x float> %840, %842
  %844 = fadd reassoc ninf nsz <2 x float> %843, %798
  br label %after_if36

after_if36:                                       ; preds = %true_block34, %after_if33
  %845 = phi <2 x float> [ %844, %true_block34 ], [ %798, %after_if33 ]
  %846 = phi <4 x float> [ %839, %true_block34 ], [ %797, %after_if33 ]
  br i1 %39, label %true_block37, label %after_if39

true_block37:                                     ; preds = %after_if36
  %847 = load float*, float** %24, align 8
  %848 = getelementptr float, float* %847, i64 14
  %849 = load float, float* %848, align 4
  %850 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %851 = add <2 x i32> %850, <i32 14, i32 -14>
  %852 = getelementptr inbounds i8, i8* %55, i64 8
  %853 = bitcast i8* %852 to i32*
  %854 = load i32, i32* %853, align 4
  %855 = add i32 %854, -1
  %856 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %851, i1 true)
  %857 = insertelement <2 x i32> poison, i32 %855, i64 0
  %858 = shufflevector <2 x i32> %857, <2 x i32> poison, <2 x i32> zeroinitializer
  %859 = sub <2 x i32> %856, %858
  %860 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %859, <2 x i32> zeroinitializer)
  %861 = mul <2 x i32> %860, <i32 -2, i32 -2>
  %862 = add <2 x i32> %861, %856
  %863 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %862, <2 x i32> zeroinitializer)
  %864 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %858, <2 x i32> %863)
  %865 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %866 = add <2 x i32> %864, %865
  %867 = insertelement <2 x i32> poison, i32 %69, i64 0
  %868 = shufflevector <2 x i32> %867, <2 x i32> poison, <2 x i32> zeroinitializer
  %869 = mul <2 x i32> %866, %868
  %870 = extractelement <2 x i32> %869, i64 1
  %871 = sext i32 %870 to i64
  %872 = getelementptr float, float* %67, i64 %871
  %873 = load float, float* %872, align 4
  %874 = extractelement <2 x i32> %869, i64 0
  %875 = sext i32 %874 to i64
  %876 = getelementptr float, float* %67, i64 %875
  %877 = load float, float* %876, align 4
  %878 = fadd reassoc ninf nsz float %877, %873
  %879 = add <2 x i32> %869, <i32 1, i32 1>
  %880 = extractelement <2 x i32> %879, i64 1
  %881 = sext i32 %880 to i64
  %882 = getelementptr float, float* %67, i64 %881
  %883 = load float, float* %882, align 4
  %884 = extractelement <2 x i32> %879, i64 0
  %885 = sext i32 %884 to i64
  %886 = getelementptr float, float* %67, i64 %885
  %887 = load float, float* %886, align 4
  %888 = shufflevector <2 x i32> %869, <2 x i32> undef, <2 x i32> <i32 1, i32 1>
  %889 = add <2 x i32> %888, <i32 2, i32 3>
  %890 = sext <2 x i32> %889 to <2 x i64>
  %891 = insertelement <2 x float*> poison, float* %67, i64 0
  %892 = shufflevector <2 x float*> %891, <2 x float*> poison, <2 x i32> zeroinitializer
  %893 = getelementptr float, <2 x float*> %892, <2 x i64> %890
  %894 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %893, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %895 = shufflevector <2 x i32> %869, <2 x i32> undef, <2 x i32> zeroinitializer
  %896 = add <2 x i32> %895, <i32 2, i32 3>
  %897 = sext <2 x i32> %896 to <2 x i64>
  %898 = getelementptr float, <2 x float*> %892, <2 x i64> %897
  %899 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %898, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %900 = add <2 x i32> %869, <i32 4, i32 4>
  %901 = sext <2 x i32> %900 to <2 x i64>
  %902 = getelementptr float, <2 x float*> %892, <2 x i64> %901
  %903 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %902, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %904 = shufflevector <2 x float> %903, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %905 = insertelement <4 x float> poison, float %887, i64 0
  %906 = shufflevector <2 x float> %899, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %907 = shufflevector <4 x float> %905, <4 x float> %906, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %908 = shufflevector <4 x float> %907, <4 x float> %904, <4 x i32> <i32 0, i32 1, i32 2, i32 4>
  %909 = insertelement <4 x float> poison, float %883, i64 0
  %910 = shufflevector <2 x float> %894, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %911 = shufflevector <4 x float> %909, <4 x float> %910, <4 x i32> <i32 0, i32 4, i32 5, i32 undef>
  %912 = shufflevector <4 x float> %911, <4 x float> %904, <4 x i32> <i32 0, i32 1, i32 2, i32 5>
  %913 = fadd reassoc ninf nsz <4 x float> %908, %912
  %914 = insertelement <4 x float> poison, float %849, i64 0
  %shuffle306 = shufflevector <4 x float> %914, <4 x float> poison, <4 x i32> zeroinitializer
  %915 = fmul reassoc ninf nsz <4 x float> %913, %shuffle306
  %916 = fadd reassoc ninf nsz <4 x float> %915, %846
  %917 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %878, i64 0
  %918 = insertelement <2 x float> poison, float %849, i64 0
  %919 = shufflevector <2 x float> %918, <2 x float> poison, <2 x i32> zeroinitializer
  %920 = fmul reassoc ninf nsz <2 x float> %917, %919
  %921 = fadd reassoc ninf nsz <2 x float> %920, %845
  br label %after_if39

after_if39:                                       ; preds = %true_block37, %after_if36
  %922 = phi <4 x float> [ %916, %true_block37 ], [ %846, %after_if36 ]
  %923 = phi <2 x float> [ %921, %true_block37 ], [ %845, %after_if36 ]
  br i1 %40, label %true_block40, label %after_if42

true_block40:                                     ; preds = %after_if39
  %924 = load float*, float** %24, align 8
  %925 = getelementptr float, float* %924, i64 15
  %926 = load float, float* %925, align 4
  %927 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %928 = add <2 x i32> %927, <i32 15, i32 -15>
  %929 = getelementptr inbounds i8, i8* %55, i64 8
  %930 = bitcast i8* %929 to i32*
  %931 = load i32, i32* %930, align 4
  %932 = add i32 %931, -1
  %933 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %928, i1 true)
  %934 = insertelement <2 x i32> poison, i32 %932, i64 0
  %935 = shufflevector <2 x i32> %934, <2 x i32> poison, <2 x i32> zeroinitializer
  %936 = sub <2 x i32> %933, %935
  %937 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %936, <2 x i32> zeroinitializer)
  %938 = mul <2 x i32> %937, <i32 -2, i32 -2>
  %939 = add <2 x i32> %938, %933
  %940 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %939, <2 x i32> zeroinitializer)
  %941 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %935, <2 x i32> %940)
  %942 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %943 = add <2 x i32> %941, %942
  %944 = insertelement <2 x i32> poison, i32 %69, i64 0
  %945 = shufflevector <2 x i32> %944, <2 x i32> poison, <2 x i32> zeroinitializer
  %946 = mul <2 x i32> %943, %945
  %947 = sext <2 x i32> %946 to <2 x i64>
  %948 = insertelement <2 x float*> poison, float* %67, i64 0
  %949 = shufflevector <2 x float*> %948, <2 x float*> poison, <2 x i32> zeroinitializer
  %950 = getelementptr float, <2 x float*> %949, <2 x i64> %947
  %951 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %950, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift361 = shufflevector <2 x float> %951, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %952 = fadd reassoc ninf nsz <2 x float> %951, %shift361
  %953 = shufflevector <2 x i32> %946, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %954 = add <4 x i32> %953, <i32 1, i32 2, i32 3, i32 4>
  %955 = sext <4 x i32> %954 to <4 x i64>
  %956 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %955
  %957 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %956, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %958 = shufflevector <2 x i32> %946, <2 x i32> undef, <4 x i32> zeroinitializer
  %959 = add <4 x i32> %958, <i32 1, i32 2, i32 3, i32 4>
  %960 = sext <4 x i32> %959 to <4 x i64>
  %961 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %960
  %962 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %961, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %963 = fadd reassoc ninf nsz <4 x float> %962, %957
  %964 = insertelement <4 x float> poison, float %926, i64 0
  %shuffle305 = shufflevector <4 x float> %964, <4 x float> poison, <4 x i32> zeroinitializer
  %965 = fmul reassoc ninf nsz <4 x float> %963, %shuffle305
  %966 = fadd reassoc ninf nsz <4 x float> %965, %922
  %967 = insertelement <2 x float> %952, float 2.000000e+00, i64 1
  %968 = insertelement <2 x float> poison, float %926, i64 0
  %969 = shufflevector <2 x float> %968, <2 x float> poison, <2 x i32> zeroinitializer
  %970 = fmul reassoc ninf nsz <2 x float> %967, %969
  %971 = fadd reassoc ninf nsz <2 x float> %970, %923
  br label %after_if42

after_if42:                                       ; preds = %true_block40, %after_if39
  %972 = phi <4 x float> [ %966, %true_block40 ], [ %922, %after_if39 ]
  %973 = phi <2 x float> [ %971, %true_block40 ], [ %923, %after_if39 ]
  br i1 %41, label %true_block43, label %after_if45

true_block43:                                     ; preds = %after_if42
  %974 = load float*, float** %24, align 8
  %975 = getelementptr float, float* %974, i64 16
  %976 = load float, float* %975, align 4
  %977 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %978 = add <2 x i32> %977, <i32 16, i32 -16>
  %979 = getelementptr inbounds i8, i8* %55, i64 8
  %980 = bitcast i8* %979 to i32*
  %981 = load i32, i32* %980, align 4
  %982 = add i32 %981, -1
  %983 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %978, i1 true)
  %984 = insertelement <2 x i32> poison, i32 %982, i64 0
  %985 = shufflevector <2 x i32> %984, <2 x i32> poison, <2 x i32> zeroinitializer
  %986 = sub <2 x i32> %983, %985
  %987 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %986, <2 x i32> zeroinitializer)
  %988 = mul <2 x i32> %987, <i32 -2, i32 -2>
  %989 = add <2 x i32> %988, %983
  %990 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %989, <2 x i32> zeroinitializer)
  %991 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %985, <2 x i32> %990)
  %992 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %993 = add <2 x i32> %991, %992
  %994 = insertelement <2 x i32> poison, i32 %69, i64 0
  %995 = shufflevector <2 x i32> %994, <2 x i32> poison, <2 x i32> zeroinitializer
  %996 = mul <2 x i32> %993, %995
  %997 = sext <2 x i32> %996 to <2 x i64>
  %998 = insertelement <2 x float*> poison, float* %67, i64 0
  %999 = shufflevector <2 x float*> %998, <2 x float*> poison, <2 x i32> zeroinitializer
  %1000 = getelementptr float, <2 x float*> %999, <2 x i64> %997
  %1001 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1000, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift362 = shufflevector <2 x float> %1001, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1002 = fadd reassoc ninf nsz <2 x float> %1001, %shift362
  %1003 = add <2 x i32> %996, <i32 1, i32 1>
  %1004 = extractelement <2 x i32> %1003, i64 1
  %1005 = sext i32 %1004 to i64
  %1006 = getelementptr float, float* %67, i64 %1005
  %1007 = extractelement <2 x i32> %1003, i64 0
  %1008 = sext i32 %1007 to i64
  %1009 = getelementptr float, float* %67, i64 %1008
  %1010 = shufflevector <2 x i32> %996, <2 x i32> undef, <4 x i32> <i32 1, i32 0, i32 1, i32 0>
  %1011 = add <4 x i32> %1010, <i32 2, i32 2, i32 3, i32 3>
  %1012 = extractelement <4 x i32> %1011, i64 0
  %1013 = sext i32 %1012 to i64
  %1014 = getelementptr float, float* %67, i64 %1013
  %1015 = extractelement <4 x i32> %1011, i64 1
  %1016 = sext i32 %1015 to i64
  %1017 = getelementptr float, float* %67, i64 %1016
  %1018 = extractelement <4 x i32> %1011, i64 2
  %1019 = sext i32 %1018 to i64
  %1020 = getelementptr float, float* %67, i64 %1019
  %1021 = extractelement <4 x i32> %1011, i64 3
  %1022 = sext i32 %1021 to i64
  %1023 = getelementptr float, float* %67, i64 %1022
  %1024 = add <2 x i32> %996, <i32 4, i32 4>
  %1025 = extractelement <2 x i32> %1024, i64 1
  %1026 = sext i32 %1025 to i64
  %1027 = getelementptr float, float* %67, i64 %1026
  %1028 = extractelement <2 x i32> %1024, i64 0
  %1029 = sext i32 %1028 to i64
  %1030 = getelementptr float, float* %67, i64 %1029
  %1031 = insertelement <4 x float*> poison, float* %1006, i64 0
  %1032 = insertelement <4 x float*> %1031, float* %1014, i64 1
  %1033 = insertelement <4 x float*> %1032, float* %1020, i64 2
  %1034 = insertelement <4 x float*> %1033, float* %1027, i64 3
  %1035 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1034, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1036 = insertelement <4 x float*> poison, float* %1009, i64 0
  %1037 = insertelement <4 x float*> %1036, float* %1017, i64 1
  %1038 = insertelement <4 x float*> %1037, float* %1023, i64 2
  %1039 = insertelement <4 x float*> %1038, float* %1030, i64 3
  %1040 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1039, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1041 = fadd reassoc ninf nsz <4 x float> %1040, %1035
  %1042 = insertelement <4 x float> poison, float %976, i64 0
  %shuffle302 = shufflevector <4 x float> %1042, <4 x float> poison, <4 x i32> zeroinitializer
  %1043 = fmul reassoc ninf nsz <4 x float> %1041, %shuffle302
  %1044 = fadd reassoc ninf nsz <4 x float> %1043, %972
  %1045 = insertelement <2 x float> %1002, float 2.000000e+00, i64 1
  %1046 = insertelement <2 x float> poison, float %976, i64 0
  %1047 = shufflevector <2 x float> %1046, <2 x float> poison, <2 x i32> zeroinitializer
  %1048 = fmul reassoc ninf nsz <2 x float> %1045, %1047
  %1049 = fadd reassoc ninf nsz <2 x float> %1048, %973
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42
  %1050 = phi <4 x float> [ %1044, %true_block43 ], [ %972, %after_if42 ]
  %1051 = phi <2 x float> [ %1049, %true_block43 ], [ %973, %after_if42 ]
  br i1 %42, label %true_block46, label %after_if48

true_block46:                                     ; preds = %after_if45
  %1052 = load float*, float** %24, align 8
  %1053 = getelementptr float, float* %1052, i64 17
  %1054 = load float, float* %1053, align 4
  %1055 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %1056 = add <2 x i32> %1055, <i32 17, i32 -17>
  %1057 = getelementptr inbounds i8, i8* %55, i64 8
  %1058 = bitcast i8* %1057 to i32*
  %1059 = load i32, i32* %1058, align 4
  %1060 = add i32 %1059, -1
  %1061 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1056, i1 true)
  %1062 = insertelement <2 x i32> poison, i32 %1060, i64 0
  %1063 = shufflevector <2 x i32> %1062, <2 x i32> poison, <2 x i32> zeroinitializer
  %1064 = sub <2 x i32> %1061, %1063
  %1065 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1064, <2 x i32> zeroinitializer)
  %1066 = mul <2 x i32> %1065, <i32 -2, i32 -2>
  %1067 = add <2 x i32> %1066, %1061
  %1068 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1067, <2 x i32> zeroinitializer)
  %1069 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1063, <2 x i32> %1068)
  %1070 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %1071 = add <2 x i32> %1069, %1070
  %1072 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1073 = shufflevector <2 x i32> %1072, <2 x i32> poison, <2 x i32> zeroinitializer
  %1074 = mul <2 x i32> %1071, %1073
  %1075 = sext <2 x i32> %1074 to <2 x i64>
  %1076 = insertelement <2 x float*> poison, float* %67, i64 0
  %1077 = shufflevector <2 x float*> %1076, <2 x float*> poison, <2 x i32> zeroinitializer
  %1078 = getelementptr float, <2 x float*> %1077, <2 x i64> %1075
  %1079 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1078, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift363 = shufflevector <2 x float> %1079, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1080 = fadd reassoc ninf nsz <2 x float> %1079, %shift363
  %1081 = shufflevector <2 x i32> %1074, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1082 = add <4 x i32> %1081, <i32 1, i32 2, i32 3, i32 4>
  %1083 = sext <4 x i32> %1082 to <4 x i64>
  %1084 = shufflevector <2 x i32> %1074, <2 x i32> undef, <4 x i32> zeroinitializer
  %1085 = add <4 x i32> %1084, <i32 1, i32 2, i32 3, i32 4>
  %1086 = sext <4 x i32> %1085 to <4 x i64>
  %1087 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1083
  %1088 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1087, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1089 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1086
  %1090 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1089, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1091 = fadd reassoc ninf nsz <4 x float> %1090, %1088
  %1092 = insertelement <4 x float> poison, float %1054, i64 0
  %shuffle301 = shufflevector <4 x float> %1092, <4 x float> poison, <4 x i32> zeroinitializer
  %1093 = fmul reassoc ninf nsz <4 x float> %1091, %shuffle301
  %1094 = fadd reassoc ninf nsz <4 x float> %1093, %1050
  %1095 = insertelement <2 x float> %1080, float 2.000000e+00, i64 1
  %1096 = insertelement <2 x float> poison, float %1054, i64 0
  %1097 = shufflevector <2 x float> %1096, <2 x float> poison, <2 x i32> zeroinitializer
  %1098 = fmul reassoc ninf nsz <2 x float> %1095, %1097
  %1099 = fadd reassoc ninf nsz <2 x float> %1098, %1051
  br label %after_if48

after_if48:                                       ; preds = %true_block46, %after_if45
  %1100 = phi <4 x float> [ %1094, %true_block46 ], [ %1050, %after_if45 ]
  %1101 = phi <2 x float> [ %1099, %true_block46 ], [ %1051, %after_if45 ]
  br i1 %43, label %true_block49, label %after_if51

true_block49:                                     ; preds = %after_if48
  %1102 = load float*, float** %24, align 8
  %1103 = getelementptr float, float* %1102, i64 18
  %1104 = load float, float* %1103, align 4
  %1105 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %1106 = add <2 x i32> %1105, <i32 18, i32 -18>
  %1107 = getelementptr inbounds i8, i8* %55, i64 8
  %1108 = bitcast i8* %1107 to i32*
  %1109 = load i32, i32* %1108, align 4
  %1110 = add i32 %1109, -1
  %1111 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1106, i1 true)
  %1112 = insertelement <2 x i32> poison, i32 %1110, i64 0
  %1113 = shufflevector <2 x i32> %1112, <2 x i32> poison, <2 x i32> zeroinitializer
  %1114 = sub <2 x i32> %1111, %1113
  %1115 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1114, <2 x i32> zeroinitializer)
  %1116 = mul <2 x i32> %1115, <i32 -2, i32 -2>
  %1117 = add <2 x i32> %1116, %1111
  %1118 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1117, <2 x i32> zeroinitializer)
  %1119 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1113, <2 x i32> %1118)
  %1120 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %1121 = add <2 x i32> %1119, %1120
  %1122 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1123 = shufflevector <2 x i32> %1122, <2 x i32> poison, <2 x i32> zeroinitializer
  %1124 = mul <2 x i32> %1121, %1123
  %1125 = sext <2 x i32> %1124 to <2 x i64>
  %1126 = insertelement <2 x float*> poison, float* %67, i64 0
  %1127 = shufflevector <2 x float*> %1126, <2 x float*> poison, <2 x i32> zeroinitializer
  %1128 = getelementptr float, <2 x float*> %1127, <2 x i64> %1125
  %1129 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1128, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift364 = shufflevector <2 x float> %1129, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1130 = fadd reassoc ninf nsz <2 x float> %1129, %shift364
  %shuffle297 = shufflevector <2 x i32> %1124, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1131 = add <4 x i32> %shuffle297, <i32 1, i32 2, i32 3, i32 4>
  %1132 = sext <4 x i32> %1131 to <4 x i64>
  %1133 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1132
  %1134 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1133, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle295 = shufflevector <2 x i32> %1124, <2 x i32> poison, <4 x i32> zeroinitializer
  %1135 = add <4 x i32> %shuffle295, <i32 1, i32 2, i32 3, i32 4>
  %1136 = sext <4 x i32> %1135 to <4 x i64>
  %1137 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1136
  %1138 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1137, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1139 = fadd reassoc ninf nsz <4 x float> %1138, %1134
  %1140 = insertelement <4 x float> poison, float %1104, i64 0
  %shuffle298 = shufflevector <4 x float> %1140, <4 x float> poison, <4 x i32> zeroinitializer
  %1141 = fmul reassoc ninf nsz <4 x float> %1139, %shuffle298
  %1142 = fadd reassoc ninf nsz <4 x float> %1141, %1100
  %1143 = insertelement <2 x float> %1130, float 2.000000e+00, i64 1
  %1144 = insertelement <2 x float> poison, float %1104, i64 0
  %1145 = shufflevector <2 x float> %1144, <2 x float> poison, <2 x i32> zeroinitializer
  %1146 = fmul reassoc ninf nsz <2 x float> %1143, %1145
  %1147 = fadd reassoc ninf nsz <2 x float> %1146, %1101
  br label %after_if51

after_if51:                                       ; preds = %true_block49, %after_if48
  %1148 = phi <4 x float> [ %1142, %true_block49 ], [ %1100, %after_if48 ]
  %1149 = phi <2 x float> [ %1147, %true_block49 ], [ %1101, %after_if48 ]
  br i1 %44, label %true_block52, label %after_if54

true_block52:                                     ; preds = %after_if51
  %1150 = load float*, float** %24, align 8
  %1151 = getelementptr float, float* %1150, i64 19
  %1152 = load float, float* %1151, align 4
  %1153 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %1154 = add <2 x i32> %1153, <i32 19, i32 -19>
  %1155 = getelementptr inbounds i8, i8* %55, i64 8
  %1156 = bitcast i8* %1155 to i32*
  %1157 = load i32, i32* %1156, align 4
  %1158 = add i32 %1157, -1
  %1159 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1154, i1 true)
  %1160 = insertelement <2 x i32> poison, i32 %1158, i64 0
  %1161 = shufflevector <2 x i32> %1160, <2 x i32> poison, <2 x i32> zeroinitializer
  %1162 = sub <2 x i32> %1159, %1161
  %1163 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1162, <2 x i32> zeroinitializer)
  %1164 = mul <2 x i32> %1163, <i32 -2, i32 -2>
  %1165 = add <2 x i32> %1164, %1159
  %1166 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1165, <2 x i32> zeroinitializer)
  %1167 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1161, <2 x i32> %1166)
  %1168 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %1169 = add <2 x i32> %1167, %1168
  %1170 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1171 = shufflevector <2 x i32> %1170, <2 x i32> poison, <2 x i32> zeroinitializer
  %1172 = mul <2 x i32> %1169, %1171
  %1173 = sext <2 x i32> %1172 to <2 x i64>
  %1174 = insertelement <2 x float*> poison, float* %67, i64 0
  %1175 = shufflevector <2 x float*> %1174, <2 x float*> poison, <2 x i32> zeroinitializer
  %1176 = getelementptr float, <2 x float*> %1175, <2 x i64> %1173
  %1177 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1176, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift365 = shufflevector <2 x float> %1177, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1178 = fadd reassoc ninf nsz <2 x float> %1177, %shift365
  %shuffle292 = shufflevector <2 x i32> %1172, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1179 = add <4 x i32> %shuffle292, <i32 1, i32 2, i32 3, i32 4>
  %1180 = sext <4 x i32> %1179 to <4 x i64>
  %1181 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1180
  %1182 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1181, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle290 = shufflevector <2 x i32> %1172, <2 x i32> poison, <4 x i32> zeroinitializer
  %1183 = add <4 x i32> %shuffle290, <i32 1, i32 2, i32 3, i32 4>
  %1184 = sext <4 x i32> %1183 to <4 x i64>
  %1185 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1184
  %1186 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1185, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1187 = fadd reassoc ninf nsz <4 x float> %1186, %1182
  %1188 = insertelement <4 x float> poison, float %1152, i64 0
  %shuffle293 = shufflevector <4 x float> %1188, <4 x float> poison, <4 x i32> zeroinitializer
  %1189 = fmul reassoc ninf nsz <4 x float> %1187, %shuffle293
  %1190 = fadd reassoc ninf nsz <4 x float> %1189, %1148
  %1191 = insertelement <2 x float> %1178, float 2.000000e+00, i64 1
  %1192 = insertelement <2 x float> poison, float %1152, i64 0
  %1193 = shufflevector <2 x float> %1192, <2 x float> poison, <2 x i32> zeroinitializer
  %1194 = fmul reassoc ninf nsz <2 x float> %1191, %1193
  %1195 = fadd reassoc ninf nsz <2 x float> %1194, %1149
  br label %after_if54

after_if54:                                       ; preds = %true_block52, %after_if51
  %1196 = phi <4 x float> [ %1190, %true_block52 ], [ %1148, %after_if51 ]
  %1197 = phi <2 x float> [ %1195, %true_block52 ], [ %1149, %after_if51 ]
  %1198 = extractelement <2 x float> %1197, i64 0
  %1199 = extractelement <2 x float> %1197, i64 1
  br i1 %45, label %true_block55, label %after_if57

true_block55:                                     ; preds = %after_if54
  %1200 = load float*, float** %24, align 8
  %1201 = getelementptr float, float* %1200, i64 20
  %1202 = load float, float* %1201, align 4
  %1203 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %1204 = add <2 x i32> %1203, <i32 20, i32 -20>
  %1205 = getelementptr inbounds i8, i8* %55, i64 8
  %1206 = bitcast i8* %1205 to i32*
  %1207 = load i32, i32* %1206, align 4
  %1208 = add i32 %1207, -1
  %1209 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %1204, i1 true)
  %1210 = insertelement <2 x i32> poison, i32 %1208, i64 0
  %1211 = shufflevector <2 x i32> %1210, <2 x i32> poison, <2 x i32> zeroinitializer
  %1212 = sub <2 x i32> %1209, %1211
  %1213 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1212, <2 x i32> zeroinitializer)
  %1214 = mul <2 x i32> %1213, <i32 -2, i32 -2>
  %1215 = add <2 x i32> %1214, %1209
  %1216 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %1215, <2 x i32> zeroinitializer)
  %1217 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %1211, <2 x i32> %1216)
  %1218 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %1219 = add <2 x i32> %1217, %1218
  %1220 = insertelement <2 x i32> poison, i32 %69, i64 0
  %1221 = shufflevector <2 x i32> %1220, <2 x i32> poison, <2 x i32> zeroinitializer
  %1222 = mul <2 x i32> %1219, %1221
  %1223 = sext <2 x i32> %1222 to <2 x i64>
  %1224 = insertelement <2 x float*> poison, float* %67, i64 0
  %1225 = shufflevector <2 x float*> %1224, <2 x float*> poison, <2 x i32> zeroinitializer
  %1226 = getelementptr float, <2 x float*> %1225, <2 x i64> %1223
  %1227 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1226, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift366 = shufflevector <2 x float> %1227, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %1228 = fadd reassoc ninf nsz <2 x float> %1227, %shift366
  %1229 = extractelement <2 x float> %1228, i64 0
  %1230 = fmul reassoc ninf nsz float %1229, %1202
  %1231 = fadd reassoc ninf nsz float %1230, %1198
  %shuffle287 = shufflevector <2 x i32> %1222, <2 x i32> poison, <4 x i32> <i32 1, i32 1, i32 1, i32 1>
  %1232 = add <4 x i32> %shuffle287, <i32 1, i32 2, i32 3, i32 4>
  %1233 = sext <4 x i32> %1232 to <4 x i64>
  %1234 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1233
  %1235 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1234, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %shuffle285 = shufflevector <2 x i32> %1222, <2 x i32> poison, <4 x i32> zeroinitializer
  %1236 = add <4 x i32> %shuffle285, <i32 1, i32 2, i32 3, i32 4>
  %1237 = sext <4 x i32> %1236 to <4 x i64>
  %1238 = getelementptr float, <4 x float*> %shuffle348, <4 x i64> %1237
  %1239 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1238, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1240 = fadd reassoc ninf nsz <4 x float> %1239, %1235
  %1241 = insertelement <4 x float> poison, float %1202, i64 0
  %shuffle288 = shufflevector <4 x float> %1241, <4 x float> poison, <4 x i32> zeroinitializer
  %1242 = fmul reassoc ninf nsz <4 x float> %1240, %shuffle288
  %1243 = fadd reassoc ninf nsz <4 x float> %1242, %1196
  %factor283 = fmul reassoc ninf nsz float %1202, 2.000000e+00
  %1244 = fadd reassoc ninf nsz float %factor283, %1199
  br label %after_if57

after_if57:                                       ; preds = %true_block55, %after_if54
  %.19222 = phi float [ %1231, %true_block55 ], [ %1198, %after_if54 ]
  %.19 = phi float [ %1244, %true_block55 ], [ %1199, %after_if54 ]
  %1245 = phi <4 x float> [ %1243, %true_block55 ], [ %1196, %after_if54 ]
  %1246 = fdiv reassoc ninf nsz float 1.000000e+00, %.19
  %1247 = fmul reassoc ninf nsz float %1246, %.19222
  %1248 = load float*, float** %50, align 8
  %1249 = load i32, i32* %51, align 4
  %1250 = load i32, i32* %52, align 4
  %1251 = mul i32 %1249, %70
  %1252 = add i32 %1251, %78
  %1253 = mul i32 %1252, %1250
  %1254 = sext i32 %1253 to i64
  %1255 = getelementptr float, float* %1248, i64 %1254
  store float %1247, float* %1255, align 4
  %1256 = extractelement <4 x float> %1245, i64 0
  %1257 = fmul reassoc ninf nsz float %1246, %1256
  %1258 = load float*, float** %50, align 8
  %1259 = load i32, i32* %51, align 4
  %1260 = load i32, i32* %52, align 4
  %1261 = mul i32 %1259, %70
  %1262 = add i32 %1261, %78
  %1263 = mul i32 %1262, %1260
  %1264 = add i32 %1263, 1
  %1265 = sext i32 %1264 to i64
  %1266 = getelementptr float, float* %1258, i64 %1265
  store float %1257, float* %1266, align 4
  %1267 = extractelement <4 x float> %1245, i64 1
  %1268 = fmul reassoc ninf nsz float %1246, %1267
  %1269 = load float*, float** %50, align 8
  %1270 = load i32, i32* %51, align 4
  %1271 = load i32, i32* %52, align 4
  %1272 = mul i32 %1270, %70
  %1273 = add i32 %1272, %78
  %1274 = mul i32 %1273, %1271
  %1275 = add i32 %1274, 2
  %1276 = sext i32 %1275 to i64
  %1277 = getelementptr float, float* %1269, i64 %1276
  store float %1268, float* %1277, align 4
  %1278 = extractelement <4 x float> %1245, i64 2
  %1279 = fmul reassoc ninf nsz float %1246, %1278
  %1280 = load float*, float** %50, align 8
  %1281 = load i32, i32* %51, align 4
  %1282 = load i32, i32* %52, align 4
  %1283 = mul i32 %1281, %70
  %1284 = add i32 %1283, %78
  %1285 = mul i32 %1284, %1282
  %1286 = add i32 %1285, 3
  %1287 = sext i32 %1286 to i64
  %1288 = getelementptr float, float* %1280, i64 %1287
  store float %1279, float* %1288, align 4
  %1289 = extractelement <4 x float> %1245, i64 3
  %1290 = fmul reassoc ninf nsz float %1246, %1289
  %1291 = load float*, float** %50, align 8
  %1292 = load i32, i32* %51, align 4
  %1293 = load i32, i32* %52, align 4
  %1294 = mul i32 %1292, %70
  %1295 = add i32 %1294, %78
  %1296 = mul i32 %1295, %1293
  %1297 = add i32 %1296, 4
  %1298 = sext i32 %1297 to i64
  %1299 = getelementptr float, float* %1291, i64 %1298
  store float %1290, float* %1299, align 4
  %1300 = add nsw i32 %.0223284, 1
  %exitcond.not = icmp eq i32 %19, %1300
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
