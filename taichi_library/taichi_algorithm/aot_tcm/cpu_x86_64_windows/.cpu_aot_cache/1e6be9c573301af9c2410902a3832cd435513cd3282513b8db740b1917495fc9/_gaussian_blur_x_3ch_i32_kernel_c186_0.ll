; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.72*, void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*, i32)*, void (%struct.RuntimeContext.72*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.72 = type { i8*, %struct.LLVMRuntime.71*, i32, i64* }
%struct.LLVMRuntime.71 = type { %struct.PreallocatedMemoryChunk.67, %struct.PreallocatedMemoryChunk.67, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.68*], [1024 x %struct.NodeManager.69*], [1024 x i8*], i8*, %struct.RandState.70*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.67 = type { i8*, i8*, i64 }
%struct.ListManager.68 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.71* }
%struct.NodeManager.69 = type { %struct.LLVMRuntime.71*, i32, i32, i32, i32, %struct.ListManager.68*, %struct.ListManager.68*, %struct.ListManager.68*, i32 }
%struct.RandState.70 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_gaussian_blur_x_3ch_i32_kernel_c186_0_kernel_0_serial(%struct.RuntimeContext.72* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.72* %context to { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 3
  %5 = load i32, i32* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 12
  %11 = bitcast i8* %10 to i32*
  store i32 %5, i32* %11, align 4
  %12 = load { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %13 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %12, i64 0, i32 5
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %21 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %22 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  store i32 %21, i32* %26, align 4
  %27 = mul i32 %21, %20
  %28 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %28, i64 0, i32 14
  %30 = bitcast i8** %29 to i32**
  %31 = load i32*, i32** %30, align 8
  store i32 %27, i32* %31, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_x_3ch_i32_kernel_c186_0_kernel_1_range_for(%struct.RuntimeContext.72* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.72* %context, %struct.RuntimeContext.72** %4, align 8
  store void (%struct.RuntimeContext.72*, i8*)* null, void (%struct.RuntimeContext.72*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.72*, i8*, i32)* @function_body, void (%struct.RuntimeContext.72*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.72*, i8*)* null, void (%struct.RuntimeContext.72*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.72* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.72* %0 to { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %23 = load float*, float** %22, align 8
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.091177 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %490, %after_if45 ]
  %31 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.091177, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.091177
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.091177, 0
  %42 = icmp ne i32 %.091177, %38
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg92 = sext i1 %44 to i32
  %45 = load float, float* %23, align 4
  %46 = load i32*, i32** %25, align 8
  %47 = load i32, i32* %26, align 4
  %48 = load i32, i32* %27, align 4
  %49 = add i32 %37, %.neg92
  %50 = mul i32 %49, %36
  %51 = insertelement <2 x i32> poison, i32 %.091177, i64 0
  %52 = insertelement <2 x i32> %51, i32 %47, i64 1
  %53 = insertelement <2 x i32> poison, i32 %50, i64 0
  %54 = insertelement <2 x i32> %53, i32 %49, i64 1
  %55 = sub <2 x i32> %52, %54
  %56 = mul <2 x i32> %52, %54
  %57 = extractelement <2 x i32> %55, i64 0
  %58 = extractelement <2 x i32> %56, i64 1
  %59 = add i32 %57, %58
  %60 = mul i32 %59, %48
  %61 = add i32 %60, 2
  %62 = sext i32 %61 to i64
  %63 = getelementptr i32, i32* %46, i64 %62
  %64 = load i32, i32* %63, align 4
  %65 = sitofp i32 %64 to float
  %66 = fmul reassoc ninf nsz float %45, %65
  %67 = getelementptr inbounds i8, i8* %33, i64 8
  %68 = bitcast i8* %67 to i32*
  %69 = load i32, i32* %68, align 4
  %70 = icmp sgt i32 %69, 0
  %71 = insertelement <2 x float> poison, float %66, i64 0
  %72 = insertelement <2 x float> %71, float %45, i64 1
  br i1 %70, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %73 = load float*, float** %22, align 8
  %74 = getelementptr float, float* %73, i64 1
  %75 = load float, float* %74, align 4
  %76 = shufflevector <2 x i32> %55, <2 x i32> poison, <2 x i32> zeroinitializer
  %77 = add <2 x i32> %76, <i32 1, i32 -1>
  %78 = getelementptr inbounds i8, i8* %33, i64 12
  %79 = bitcast i8* %78 to i32*
  %80 = load i32, i32* %79, align 4
  %81 = add i32 %80, -1
  %82 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %77, i1 true)
  %83 = insertelement <2 x i32> poison, i32 %81, i64 0
  %84 = shufflevector <2 x i32> %83, <2 x i32> poison, <2 x i32> zeroinitializer
  %85 = sub <2 x i32> %82, %84
  %86 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %85, <2 x i32> zeroinitializer)
  %87 = mul <2 x i32> %86, <i32 -2, i32 -2>
  %88 = add <2 x i32> %87, %82
  %89 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %88, <2 x i32> zeroinitializer)
  %90 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %89)
  %91 = shufflevector <2 x i32> %56, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %92 = add <2 x i32> %90, %91
  %93 = insertelement <2 x i32> poison, i32 %48, i64 0
  %94 = shufflevector <2 x i32> %93, <2 x i32> poison, <2 x i32> zeroinitializer
  %95 = mul <2 x i32> %92, %94
  %96 = add <2 x i32> %95, <i32 2, i32 2>
  %97 = sext <2 x i32> %96 to <2 x i64>
  %98 = insertelement <2 x i32*> poison, i32* %46, i64 0
  %99 = shufflevector <2 x i32*> %98, <2 x i32*> poison, <2 x i32> zeroinitializer
  %100 = getelementptr i32, <2 x i32*> %99, <2 x i64> %97
  %101 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %100, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift = shufflevector <2 x i32> %101, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %102 = add <2 x i32> %101, %shift
  %103 = extractelement <2 x i32> %102, i64 0
  %104 = sitofp i32 %103 to float
  %105 = insertelement <2 x float> poison, float %75, i64 0
  %106 = shufflevector <2 x float> %105, <2 x float> poison, <2 x i32> zeroinitializer
  %107 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %104, i64 0
  %108 = fmul reassoc ninf nsz <2 x float> %106, %107
  %109 = fadd reassoc ninf nsz <2 x float> %108, %72
  %.not = icmp eq i32 %69, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %110 = getelementptr float, float* %73, i64 2
  %111 = load float, float* %110, align 4
  %112 = add <2 x i32> %76, <i32 2, i32 -2>
  %113 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %112, i1 true)
  %114 = sub <2 x i32> %113, %84
  %115 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %114, <2 x i32> zeroinitializer)
  %116 = mul <2 x i32> %115, <i32 -2, i32 -2>
  %117 = add <2 x i32> %116, %113
  %118 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %117, <2 x i32> zeroinitializer)
  %119 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %118)
  %120 = add <2 x i32> %119, %91
  %121 = mul <2 x i32> %120, %94
  %122 = add <2 x i32> %121, <i32 2, i32 2>
  %123 = sext <2 x i32> %122 to <2 x i64>
  %124 = getelementptr i32, <2 x i32*> %99, <2 x i64> %123
  %125 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %124, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift178 = shufflevector <2 x i32> %125, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %126 = add <2 x i32> %125, %shift178
  %127 = extractelement <2 x i32> %126, i64 0
  %128 = sitofp i32 %127 to float
  %129 = insertelement <2 x float> poison, float %111, i64 0
  %130 = shufflevector <2 x float> %129, <2 x float> poison, <2 x i32> zeroinitializer
  %131 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %128, i64 0
  %132 = fmul reassoc ninf nsz <2 x float> %130, %131
  %133 = fadd reassoc ninf nsz <2 x float> %132, %109
  %134 = icmp ugt i32 %69, 2
  br i1 %134, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %135 = getelementptr float, float* %73, i64 3
  %136 = load float, float* %135, align 4
  %137 = add <2 x i32> %76, <i32 3, i32 -3>
  %138 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %137, i1 true)
  %139 = sub <2 x i32> %138, %84
  %140 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %139, <2 x i32> zeroinitializer)
  %141 = mul <2 x i32> %140, <i32 -2, i32 -2>
  %142 = add <2 x i32> %141, %138
  %143 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %142, <2 x i32> zeroinitializer)
  %144 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %143)
  %145 = add <2 x i32> %144, %91
  %146 = mul <2 x i32> %145, %94
  %147 = add <2 x i32> %146, <i32 2, i32 2>
  %148 = sext <2 x i32> %147 to <2 x i64>
  %149 = getelementptr i32, <2 x i32*> %99, <2 x i64> %148
  %150 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %149, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift179 = shufflevector <2 x i32> %150, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %151 = add <2 x i32> %150, %shift179
  %152 = extractelement <2 x i32> %151, i64 0
  %153 = sitofp i32 %152 to float
  %154 = insertelement <2 x float> poison, float %136, i64 0
  %155 = shufflevector <2 x float> %154, <2 x float> poison, <2 x i32> zeroinitializer
  %156 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %153, i64 0
  %157 = fmul reassoc ninf nsz <2 x float> %155, %156
  %158 = fadd reassoc ninf nsz <2 x float> %157, %133
  %.not155 = icmp eq i32 %69, 3
  br i1 %.not155, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %159 = getelementptr float, float* %73, i64 4
  %160 = load float, float* %159, align 4
  %161 = add <2 x i32> %76, <i32 4, i32 -4>
  %162 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %161, i1 true)
  %163 = sub <2 x i32> %162, %84
  %164 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %163, <2 x i32> zeroinitializer)
  %165 = mul <2 x i32> %164, <i32 -2, i32 -2>
  %166 = add <2 x i32> %165, %162
  %167 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %166, <2 x i32> zeroinitializer)
  %168 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %167)
  %169 = add <2 x i32> %168, %91
  %170 = mul <2 x i32> %169, %94
  %171 = add <2 x i32> %170, <i32 2, i32 2>
  %172 = sext <2 x i32> %171 to <2 x i64>
  %173 = getelementptr i32, <2 x i32*> %99, <2 x i64> %172
  %174 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %173, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift180 = shufflevector <2 x i32> %174, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %175 = add <2 x i32> %174, %shift180
  %176 = extractelement <2 x i32> %175, i64 0
  %177 = sitofp i32 %176 to float
  %178 = insertelement <2 x float> poison, float %160, i64 0
  %179 = shufflevector <2 x float> %178, <2 x float> poison, <2 x i32> zeroinitializer
  %180 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %177, i64 0
  %181 = fmul reassoc ninf nsz <2 x float> %179, %180
  %182 = fadd reassoc ninf nsz <2 x float> %181, %158
  %183 = icmp ugt i32 %69, 4
  br i1 %183, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %184 = getelementptr float, float* %73, i64 5
  %185 = load float, float* %184, align 4
  %186 = add <2 x i32> %76, <i32 5, i32 -5>
  %187 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %186, i1 true)
  %188 = sub <2 x i32> %187, %84
  %189 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %188, <2 x i32> zeroinitializer)
  %190 = mul <2 x i32> %189, <i32 -2, i32 -2>
  %191 = add <2 x i32> %190, %187
  %192 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %191, <2 x i32> zeroinitializer)
  %193 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %192)
  %194 = add <2 x i32> %193, %91
  %195 = mul <2 x i32> %194, %94
  %196 = add <2 x i32> %195, <i32 2, i32 2>
  %197 = sext <2 x i32> %196 to <2 x i64>
  %198 = getelementptr i32, <2 x i32*> %99, <2 x i64> %197
  %199 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %198, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift181 = shufflevector <2 x i32> %199, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %200 = add <2 x i32> %199, %shift181
  %201 = extractelement <2 x i32> %200, i64 0
  %202 = sitofp i32 %201 to float
  %203 = insertelement <2 x float> poison, float %185, i64 0
  %204 = shufflevector <2 x float> %203, <2 x float> poison, <2 x i32> zeroinitializer
  %205 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %202, i64 0
  %206 = fmul reassoc ninf nsz <2 x float> %204, %205
  %207 = fadd reassoc ninf nsz <2 x float> %206, %182
  %.not156 = icmp eq i32 %69, 5
  br i1 %.not156, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %208 = getelementptr float, float* %73, i64 6
  %209 = load float, float* %208, align 4
  %210 = add <2 x i32> %76, <i32 6, i32 -6>
  %211 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %210, i1 true)
  %212 = sub <2 x i32> %211, %84
  %213 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %212, <2 x i32> zeroinitializer)
  %214 = mul <2 x i32> %213, <i32 -2, i32 -2>
  %215 = add <2 x i32> %214, %211
  %216 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %215, <2 x i32> zeroinitializer)
  %217 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %216)
  %218 = add <2 x i32> %217, %91
  %219 = mul <2 x i32> %218, %94
  %220 = add <2 x i32> %219, <i32 2, i32 2>
  %221 = sext <2 x i32> %220 to <2 x i64>
  %222 = getelementptr i32, <2 x i32*> %99, <2 x i64> %221
  %223 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %222, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift182 = shufflevector <2 x i32> %223, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %224 = add <2 x i32> %223, %shift182
  %225 = extractelement <2 x i32> %224, i64 0
  %226 = sitofp i32 %225 to float
  %227 = insertelement <2 x float> poison, float %209, i64 0
  %228 = shufflevector <2 x float> %227, <2 x float> poison, <2 x i32> zeroinitializer
  %229 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %226, i64 0
  %230 = fmul reassoc ninf nsz <2 x float> %228, %229
  %231 = fadd reassoc ninf nsz <2 x float> %230, %207
  %232 = icmp ugt i32 %69, 6
  br i1 %232, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %233 = getelementptr float, float* %73, i64 7
  %234 = load float, float* %233, align 4
  %235 = add <2 x i32> %76, <i32 7, i32 -7>
  %236 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %235, i1 true)
  %237 = sub <2 x i32> %236, %84
  %238 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %237, <2 x i32> zeroinitializer)
  %239 = mul <2 x i32> %238, <i32 -2, i32 -2>
  %240 = add <2 x i32> %239, %236
  %241 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %240, <2 x i32> zeroinitializer)
  %242 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %241)
  %243 = add <2 x i32> %242, %91
  %244 = mul <2 x i32> %243, %94
  %245 = add <2 x i32> %244, <i32 2, i32 2>
  %246 = sext <2 x i32> %245 to <2 x i64>
  %247 = getelementptr i32, <2 x i32*> %99, <2 x i64> %246
  %248 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %247, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift183 = shufflevector <2 x i32> %248, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %249 = add <2 x i32> %248, %shift183
  %250 = extractelement <2 x i32> %249, i64 0
  %251 = sitofp i32 %250 to float
  %252 = insertelement <2 x float> poison, float %234, i64 0
  %253 = shufflevector <2 x float> %252, <2 x float> poison, <2 x i32> zeroinitializer
  %254 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %251, i64 0
  %255 = fmul reassoc ninf nsz <2 x float> %253, %254
  %256 = fadd reassoc ninf nsz <2 x float> %255, %231
  %.not157 = icmp eq i32 %69, 7
  br i1 %.not157, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %257 = getelementptr float, float* %73, i64 8
  %258 = load float, float* %257, align 4
  %259 = add <2 x i32> %76, <i32 8, i32 -8>
  %260 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %259, i1 true)
  %261 = sub <2 x i32> %260, %84
  %262 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %261, <2 x i32> zeroinitializer)
  %263 = mul <2 x i32> %262, <i32 -2, i32 -2>
  %264 = add <2 x i32> %263, %260
  %265 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %264, <2 x i32> zeroinitializer)
  %266 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %265)
  %267 = add <2 x i32> %266, %91
  %268 = mul <2 x i32> %267, %94
  %269 = add <2 x i32> %268, <i32 2, i32 2>
  %270 = sext <2 x i32> %269 to <2 x i64>
  %271 = getelementptr i32, <2 x i32*> %99, <2 x i64> %270
  %272 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %271, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift184 = shufflevector <2 x i32> %272, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %273 = add <2 x i32> %272, %shift184
  %274 = extractelement <2 x i32> %273, i64 0
  %275 = sitofp i32 %274 to float
  %276 = insertelement <2 x float> poison, float %258, i64 0
  %277 = shufflevector <2 x float> %276, <2 x float> poison, <2 x i32> zeroinitializer
  %278 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %275, i64 0
  %279 = fmul reassoc ninf nsz <2 x float> %277, %278
  %280 = fadd reassoc ninf nsz <2 x float> %279, %256
  %281 = icmp ugt i32 %69, 8
  br i1 %281, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %282 = getelementptr float, float* %73, i64 9
  %283 = load float, float* %282, align 4
  %284 = add <2 x i32> %76, <i32 9, i32 -9>
  %285 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %284, i1 true)
  %286 = sub <2 x i32> %285, %84
  %287 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %286, <2 x i32> zeroinitializer)
  %288 = mul <2 x i32> %287, <i32 -2, i32 -2>
  %289 = add <2 x i32> %288, %285
  %290 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %289, <2 x i32> zeroinitializer)
  %291 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %290)
  %292 = add <2 x i32> %291, %91
  %293 = mul <2 x i32> %292, %94
  %294 = add <2 x i32> %293, <i32 2, i32 2>
  %295 = sext <2 x i32> %294 to <2 x i64>
  %296 = getelementptr i32, <2 x i32*> %99, <2 x i64> %295
  %297 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %296, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift185 = shufflevector <2 x i32> %297, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %298 = add <2 x i32> %297, %shift185
  %299 = extractelement <2 x i32> %298, i64 0
  %300 = sitofp i32 %299 to float
  %301 = insertelement <2 x float> poison, float %283, i64 0
  %302 = shufflevector <2 x float> %301, <2 x float> poison, <2 x i32> zeroinitializer
  %303 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %300, i64 0
  %304 = fmul reassoc ninf nsz <2 x float> %302, %303
  %305 = fadd reassoc ninf nsz <2 x float> %304, %280
  %.not158 = icmp eq i32 %69, 9
  br i1 %.not158, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %306 = getelementptr float, float* %73, i64 10
  %307 = load float, float* %306, align 4
  %308 = add <2 x i32> %76, <i32 10, i32 -10>
  %309 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %308, i1 true)
  %310 = sub <2 x i32> %309, %84
  %311 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %310, <2 x i32> zeroinitializer)
  %312 = mul <2 x i32> %311, <i32 -2, i32 -2>
  %313 = add <2 x i32> %312, %309
  %314 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %313, <2 x i32> zeroinitializer)
  %315 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %314)
  %316 = add <2 x i32> %315, %91
  %317 = mul <2 x i32> %316, %94
  %318 = add <2 x i32> %317, <i32 2, i32 2>
  %319 = sext <2 x i32> %318 to <2 x i64>
  %320 = getelementptr i32, <2 x i32*> %99, <2 x i64> %319
  %321 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %320, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift186 = shufflevector <2 x i32> %321, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %322 = add <2 x i32> %321, %shift186
  %323 = extractelement <2 x i32> %322, i64 0
  %324 = sitofp i32 %323 to float
  %325 = insertelement <2 x float> poison, float %307, i64 0
  %326 = shufflevector <2 x float> %325, <2 x float> poison, <2 x i32> zeroinitializer
  %327 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %324, i64 0
  %328 = fmul reassoc ninf nsz <2 x float> %326, %327
  %329 = fadd reassoc ninf nsz <2 x float> %328, %305
  %330 = icmp ugt i32 %69, 10
  br i1 %330, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %331 = getelementptr float, float* %73, i64 11
  %332 = load float, float* %331, align 4
  %333 = add <2 x i32> %76, <i32 11, i32 -11>
  %334 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %333, i1 true)
  %335 = sub <2 x i32> %334, %84
  %336 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %335, <2 x i32> zeroinitializer)
  %337 = mul <2 x i32> %336, <i32 -2, i32 -2>
  %338 = add <2 x i32> %337, %334
  %339 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %338, <2 x i32> zeroinitializer)
  %340 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %339)
  %341 = add <2 x i32> %340, %91
  %342 = mul <2 x i32> %341, %94
  %343 = add <2 x i32> %342, <i32 2, i32 2>
  %344 = sext <2 x i32> %343 to <2 x i64>
  %345 = getelementptr i32, <2 x i32*> %99, <2 x i64> %344
  %346 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %345, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift187 = shufflevector <2 x i32> %346, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %347 = add <2 x i32> %346, %shift187
  %348 = extractelement <2 x i32> %347, i64 0
  %349 = sitofp i32 %348 to float
  %350 = insertelement <2 x float> poison, float %332, i64 0
  %351 = shufflevector <2 x float> %350, <2 x float> poison, <2 x i32> zeroinitializer
  %352 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %349, i64 0
  %353 = fmul reassoc ninf nsz <2 x float> %351, %352
  %354 = fadd reassoc ninf nsz <2 x float> %353, %329
  %.not159 = icmp eq i32 %69, 11
  br i1 %.not159, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %355 = getelementptr float, float* %73, i64 12
  %356 = load float, float* %355, align 4
  %357 = add <2 x i32> %76, <i32 12, i32 -12>
  %358 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %357, i1 true)
  %359 = sub <2 x i32> %358, %84
  %360 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %359, <2 x i32> zeroinitializer)
  %361 = mul <2 x i32> %360, <i32 -2, i32 -2>
  %362 = add <2 x i32> %361, %358
  %363 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %362, <2 x i32> zeroinitializer)
  %364 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %363)
  %365 = add <2 x i32> %364, %91
  %366 = mul <2 x i32> %365, %94
  %367 = add <2 x i32> %366, <i32 2, i32 2>
  %368 = sext <2 x i32> %367 to <2 x i64>
  %369 = getelementptr i32, <2 x i32*> %99, <2 x i64> %368
  %370 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %369, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift188 = shufflevector <2 x i32> %370, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %371 = add <2 x i32> %370, %shift188
  %372 = extractelement <2 x i32> %371, i64 0
  %373 = sitofp i32 %372 to float
  %374 = insertelement <2 x float> poison, float %356, i64 0
  %375 = shufflevector <2 x float> %374, <2 x float> poison, <2 x i32> zeroinitializer
  %376 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %373, i64 0
  %377 = fmul reassoc ninf nsz <2 x float> %375, %376
  %378 = fadd reassoc ninf nsz <2 x float> %377, %354
  %379 = icmp ugt i32 %69, 12
  br i1 %379, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %380 = getelementptr float, float* %73, i64 13
  %381 = load float, float* %380, align 4
  %382 = add <2 x i32> %76, <i32 13, i32 -13>
  %383 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %382, i1 true)
  %384 = sub <2 x i32> %383, %84
  %385 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %384, <2 x i32> zeroinitializer)
  %386 = mul <2 x i32> %385, <i32 -2, i32 -2>
  %387 = add <2 x i32> %386, %383
  %388 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %387, <2 x i32> zeroinitializer)
  %389 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %388)
  %390 = add <2 x i32> %389, %91
  %391 = mul <2 x i32> %390, %94
  %392 = add <2 x i32> %391, <i32 2, i32 2>
  %393 = sext <2 x i32> %392 to <2 x i64>
  %394 = getelementptr i32, <2 x i32*> %99, <2 x i64> %393
  %395 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %394, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift189 = shufflevector <2 x i32> %395, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %396 = add <2 x i32> %395, %shift189
  %397 = extractelement <2 x i32> %396, i64 0
  %398 = sitofp i32 %397 to float
  %399 = insertelement <2 x float> poison, float %381, i64 0
  %400 = shufflevector <2 x float> %399, <2 x float> poison, <2 x i32> zeroinitializer
  %401 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %398, i64 0
  %402 = fmul reassoc ninf nsz <2 x float> %400, %401
  %403 = fadd reassoc ninf nsz <2 x float> %402, %378
  %.not160 = icmp eq i32 %69, 13
  br i1 %.not160, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %404 = getelementptr float, float* %73, i64 14
  %405 = load float, float* %404, align 4
  %406 = add <2 x i32> %76, <i32 14, i32 -14>
  %407 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %406, i1 true)
  %408 = sub <2 x i32> %407, %84
  %409 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %408, <2 x i32> zeroinitializer)
  %410 = mul <2 x i32> %409, <i32 -2, i32 -2>
  %411 = add <2 x i32> %410, %407
  %412 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %411, <2 x i32> zeroinitializer)
  %413 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %412)
  %414 = add <2 x i32> %413, %91
  %415 = mul <2 x i32> %414, %94
  %416 = add <2 x i32> %415, <i32 2, i32 2>
  %417 = sext <2 x i32> %416 to <2 x i64>
  %418 = getelementptr i32, <2 x i32*> %99, <2 x i64> %417
  %419 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %418, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift190 = shufflevector <2 x i32> %419, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %420 = add <2 x i32> %419, %shift190
  %421 = extractelement <2 x i32> %420, i64 0
  %422 = sitofp i32 %421 to float
  %423 = insertelement <2 x float> poison, float %405, i64 0
  %424 = shufflevector <2 x float> %423, <2 x float> poison, <2 x i32> zeroinitializer
  %425 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %422, i64 0
  %426 = fmul reassoc ninf nsz <2 x float> %424, %425
  %427 = fadd reassoc ninf nsz <2 x float> %426, %403
  %428 = icmp ugt i32 %69, 14
  br i1 %428, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %429 = getelementptr float, float* %73, i64 15
  %430 = load float, float* %429, align 4
  %431 = add <2 x i32> %76, <i32 15, i32 -15>
  %432 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %431, i1 true)
  %433 = sub <2 x i32> %432, %84
  %434 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %433, <2 x i32> zeroinitializer)
  %435 = mul <2 x i32> %434, <i32 -2, i32 -2>
  %436 = add <2 x i32> %435, %432
  %437 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %436, <2 x i32> zeroinitializer)
  %438 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %437)
  %439 = add <2 x i32> %438, %91
  %440 = mul <2 x i32> %439, %94
  %441 = add <2 x i32> %440, <i32 2, i32 2>
  %442 = sext <2 x i32> %441 to <2 x i64>
  %443 = getelementptr i32, <2 x i32*> %99, <2 x i64> %442
  %444 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %443, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift191 = shufflevector <2 x i32> %444, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %445 = add <2 x i32> %444, %shift191
  %446 = extractelement <2 x i32> %445, i64 0
  %447 = sitofp i32 %446 to float
  %448 = insertelement <2 x float> poison, float %430, i64 0
  %449 = shufflevector <2 x float> %448, <2 x float> poison, <2 x i32> zeroinitializer
  %450 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %447, i64 0
  %451 = fmul reassoc ninf nsz <2 x float> %449, %450
  %452 = fadd reassoc ninf nsz <2 x float> %451, %427
  %.not161 = icmp eq i32 %69, 15
  br i1 %.not161, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %453 = getelementptr float, float* %73, i64 16
  %454 = load float, float* %453, align 4
  %455 = add <2 x i32> %76, <i32 16, i32 -16>
  %456 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %455, i1 true)
  %457 = sub <2 x i32> %456, %84
  %458 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %457, <2 x i32> zeroinitializer)
  %459 = mul <2 x i32> %458, <i32 -2, i32 -2>
  %460 = add <2 x i32> %459, %456
  %461 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %460, <2 x i32> zeroinitializer)
  %462 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %84, <2 x i32> %461)
  %463 = add <2 x i32> %462, %91
  %464 = mul <2 x i32> %463, %94
  %465 = add <2 x i32> %464, <i32 2, i32 2>
  %466 = sext <2 x i32> %465 to <2 x i64>
  %467 = getelementptr i32, <2 x i32*> %99, <2 x i64> %466
  %468 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %467, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift192 = shufflevector <2 x i32> %468, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %469 = add <2 x i32> %468, %shift192
  %470 = extractelement <2 x i32> %469, i64 0
  %471 = sitofp i32 %470 to float
  %472 = insertelement <2 x float> poison, float %454, i64 0
  %473 = shufflevector <2 x float> %472, <2 x float> poison, <2 x i32> zeroinitializer
  %474 = insertelement <2 x float> <float poison, float 2.000000e+00>, float %471, i64 0
  %475 = fmul reassoc ninf nsz <2 x float> %473, %474
  %476 = fadd reassoc ninf nsz <2 x float> %475, %452
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %477 = phi <2 x float> [ %476, %true_block43 ], [ %452, %after_if42 ], [ %427, %after_if39 ], [ %403, %after_if36 ], [ %378, %after_if33 ], [ %354, %after_if30 ], [ %329, %after_if27 ], [ %305, %after_if24 ], [ %280, %after_if21 ], [ %256, %after_if18 ], [ %231, %after_if15 ], [ %207, %after_if12 ], [ %182, %after_if9 ], [ %158, %after_if6 ], [ %133, %after_if3 ], [ %109, %after_if ], [ %72, %for_loop_body ]
  %shift193 = shufflevector <2 x float> %477, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %478 = fdiv reassoc ninf nsz <2 x float> %477, %shift193
  %479 = extractelement <2 x float> %478, i64 0
  %480 = load i32*, i32** %28, align 8
  %481 = load i32, i32* %29, align 4
  %482 = load i32, i32* %30, align 4
  %483 = mul i32 %481, %49
  %484 = add i32 %483, %57
  %485 = mul i32 %484, %482
  %486 = add i32 %485, 2
  %487 = sext i32 %486 to i64
  %488 = getelementptr i32, i32* %480, i64 %487
  %489 = fptosi float %479 to i32
  store i32 %489, i32* %488, align 4
  %490 = add nsw i32 %.091177, 1
  %exitcond.not = icmp eq i32 %19, %490
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.72, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.72**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.72*, %struct.RuntimeContext.72** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.72*, i8*, i32)*, void (%struct.RuntimeContext.72*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.72*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.72* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.72* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.72* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.72* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.72* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.72*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.72* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
declare <2 x i32> @llvm.abs.v2i32(<2 x i32>, i1 immarg) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*>, i32 immarg, <2 x i1>, <2 x i32>) #8

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
