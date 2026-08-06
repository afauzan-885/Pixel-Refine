; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.84*, void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.84 = type { i8*, %struct.LLVMRuntime.83*, i32, i64* }
%struct.LLVMRuntime.83 = type { %struct.PreallocatedMemoryChunk.79, %struct.PreallocatedMemoryChunk.79, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.80*], [1024 x %struct.NodeManager.81*], [1024 x i8*], i8*, %struct.RandState.82*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.79 = type { i8*, i8*, i64 }
%struct.ListManager.80 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.83* }
%struct.NodeManager.81 = type { %struct.LLVMRuntime.83*, i32, i32, i32, i32, %struct.ListManager.80*, %struct.ListManager.80*, %struct.ListManager.80*, i32 }
%struct.RandState.82 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_gaussian_blur_y_3ch_i32_kernel_c188_0_kernel_0_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %10, i64 0, i32 3
  %12 = load i32, i32* %11, align 4
  %13 = getelementptr { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }* %10, i64 0, i32 5
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %21 = tail call i32 @llvm.smax.i32(i32 %12, i32 0)
  %22 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  store i32 %21, i32* %26, align 4
  %27 = mul i32 %21, %20
  %28 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %28, i64 0, i32 14
  %30 = bitcast i8** %29 to i32**
  %31 = load i32*, i32** %30, align 8
  store i32 %27, i32* %31, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_y_3ch_i32_kernel_c188_0_kernel_1_range_for(%struct.RuntimeContext.84* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.84* %context, %struct.RuntimeContext.84** %4, align 8
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.84*, i8*, i32)* @function_body, void (%struct.RuntimeContext.84*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.84* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.84* %0 to { { { i32, i32, i32 }, i32* }, { { i32, i32, i32 }, i32* }, i32, i32, { { i32 }, float* }, i32 }**
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
  %.0115231 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %735, %after_if45 ]
  %31 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.0115231, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.0115231
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.0115231, 0
  %42 = icmp ne i32 %.0115231, %38
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg116 = sext i1 %44 to i32
  %45 = load float, float* %23, align 4
  %46 = load i32*, i32** %25, align 8
  %47 = load i32, i32* %26, align 4
  %48 = load i32, i32* %27, align 4
  %49 = add i32 %37, %.neg116
  %50 = mul i32 %49, %36
  %51 = insertelement <2 x i32> poison, i32 %.0115231, i64 0
  %52 = insertelement <2 x i32> poison, i32 %50, i64 0
  %53 = sub <2 x i32> %51, %52
  %54 = extractelement <2 x i32> %53, i64 0
  %55 = mul i32 %47, %49
  %56 = add i32 %54, %55
  %57 = mul i32 %56, %48
  %58 = sext i32 %57 to i64
  %59 = getelementptr i32, i32* %46, i64 %58
  %60 = load i32, i32* %59, align 4
  %61 = sitofp i32 %60 to float
  %62 = fmul reassoc ninf nsz float %45, %61
  %63 = add i32 %57, 1
  %64 = sext i32 %63 to i64
  %65 = getelementptr i32, i32* %46, i64 %64
  %66 = load i32, i32* %65, align 4
  %67 = sitofp i32 %66 to float
  %68 = fmul reassoc ninf nsz float %45, %67
  %69 = add i32 %57, 2
  %70 = sext i32 %69 to i64
  %71 = getelementptr i32, i32* %46, i64 %70
  %72 = load i32, i32* %71, align 4
  %73 = sitofp i32 %72 to float
  %74 = fmul reassoc ninf nsz float %45, %73
  %75 = getelementptr inbounds i8, i8* %33, i64 8
  %76 = bitcast i8* %75 to i32*
  %77 = load i32, i32* %76, align 4
  %78 = icmp sgt i32 %77, 0
  %79 = insertelement <4 x float> poison, float %62, i64 0
  %80 = insertelement <4 x float> %79, float %68, i64 1
  %81 = insertelement <4 x float> %80, float %74, i64 2
  %82 = insertelement <4 x float> %81, float %45, i64 3
  br i1 %78, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %83 = load float*, float** %22, align 8
  %84 = getelementptr float, float* %83, i64 1
  %85 = load float, float* %84, align 4
  %86 = insertelement <2 x i32> poison, i32 %49, i64 0
  %87 = shufflevector <2 x i32> %86, <2 x i32> poison, <2 x i32> zeroinitializer
  %88 = add <2 x i32> %87, <i32 1, i32 -1>
  %89 = getelementptr inbounds i8, i8* %33, i64 12
  %90 = bitcast i8* %89 to i32*
  %91 = load i32, i32* %90, align 4
  %92 = add i32 %91, -1
  %93 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %88, i1 true)
  %94 = insertelement <2 x i32> poison, i32 %92, i64 0
  %95 = shufflevector <2 x i32> %94, <2 x i32> poison, <2 x i32> zeroinitializer
  %96 = sub <2 x i32> %93, %95
  %97 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %96, <2 x i32> zeroinitializer)
  %98 = mul <2 x i32> %97, <i32 -2, i32 -2>
  %99 = add <2 x i32> %98, %93
  %100 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %99, <2 x i32> zeroinitializer)
  %101 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %100)
  %102 = insertelement <2 x i32> poison, i32 %47, i64 0
  %103 = shufflevector <2 x i32> %102, <2 x i32> poison, <2 x i32> zeroinitializer
  %104 = mul <2 x i32> %101, %103
  %105 = shufflevector <2 x i32> %53, <2 x i32> poison, <2 x i32> zeroinitializer
  %106 = add <2 x i32> %104, %105
  %107 = insertelement <2 x i32> poison, i32 %48, i64 0
  %108 = shufflevector <2 x i32> %107, <2 x i32> poison, <2 x i32> zeroinitializer
  %109 = mul <2 x i32> %106, %108
  %110 = sext <2 x i32> %109 to <2 x i64>
  %111 = insertelement <2 x i32*> poison, i32* %46, i64 0
  %112 = shufflevector <2 x i32*> %111, <2 x i32*> poison, <2 x i32> zeroinitializer
  %113 = getelementptr i32, <2 x i32*> %112, <2 x i64> %110
  %114 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %113, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift = shufflevector <2 x i32> %114, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %115 = add <2 x i32> %114, %shift
  %116 = extractelement <2 x i32> %115, i64 0
  %117 = sitofp i32 %116 to float
  %118 = shufflevector <2 x i32> %109, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %119 = add <2 x i32> %118, <i32 1, i32 2>
  %120 = sext <2 x i32> %119 to <2 x i64>
  %121 = getelementptr i32, <2 x i32*> %112, <2 x i64> %120
  %122 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %121, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %123 = shufflevector <2 x i32> %109, <2 x i32> poison, <2 x i32> zeroinitializer
  %124 = add <2 x i32> %123, <i32 1, i32 2>
  %125 = sext <2 x i32> %124 to <2 x i64>
  %126 = getelementptr i32, <2 x i32*> %112, <2 x i64> %125
  %127 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %126, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %128 = add <2 x i32> %127, %122
  %129 = sitofp <2 x i32> %128 to <2 x float>
  %130 = insertelement <4 x float> poison, float %85, i64 0
  %shuffle245 = shufflevector <4 x float> %130, <4 x float> poison, <4 x i32> zeroinitializer
  %131 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %117, i64 0
  %132 = shufflevector <2 x float> %129, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %133 = shufflevector <4 x float> %131, <4 x float> %132, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %134 = fmul reassoc ninf nsz <4 x float> %shuffle245, %133
  %135 = fadd reassoc ninf nsz <4 x float> %134, %82
  %.not = icmp eq i32 %77, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %136 = getelementptr float, float* %83, i64 2
  %137 = load float, float* %136, align 4
  %138 = add <2 x i32> %87, <i32 2, i32 -2>
  %139 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %138, i1 true)
  %140 = sub <2 x i32> %139, %95
  %141 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %140, <2 x i32> zeroinitializer)
  %142 = mul <2 x i32> %141, <i32 -2, i32 -2>
  %143 = add <2 x i32> %142, %139
  %144 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %143, <2 x i32> zeroinitializer)
  %145 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %144)
  %146 = mul <2 x i32> %145, %103
  %147 = add <2 x i32> %146, %105
  %148 = mul <2 x i32> %147, %108
  %149 = sext <2 x i32> %148 to <2 x i64>
  %150 = getelementptr i32, <2 x i32*> %112, <2 x i64> %149
  %151 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %150, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift247 = shufflevector <2 x i32> %151, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %152 = add <2 x i32> %151, %shift247
  %153 = extractelement <2 x i32> %152, i64 0
  %154 = sitofp i32 %153 to float
  %155 = shufflevector <2 x i32> %148, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %156 = add <2 x i32> %155, <i32 1, i32 2>
  %157 = sext <2 x i32> %156 to <2 x i64>
  %158 = getelementptr i32, <2 x i32*> %112, <2 x i64> %157
  %159 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %158, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %160 = shufflevector <2 x i32> %148, <2 x i32> poison, <2 x i32> zeroinitializer
  %161 = add <2 x i32> %160, <i32 1, i32 2>
  %162 = sext <2 x i32> %161 to <2 x i64>
  %163 = getelementptr i32, <2 x i32*> %112, <2 x i64> %162
  %164 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %163, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %165 = add <2 x i32> %164, %159
  %166 = sitofp <2 x i32> %165 to <2 x float>
  %167 = insertelement <4 x float> poison, float %137, i64 0
  %shuffle244 = shufflevector <4 x float> %167, <4 x float> poison, <4 x i32> zeroinitializer
  %168 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %154, i64 0
  %169 = shufflevector <2 x float> %166, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %170 = shufflevector <4 x float> %168, <4 x float> %169, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %171 = fmul reassoc ninf nsz <4 x float> %shuffle244, %170
  %172 = fadd reassoc ninf nsz <4 x float> %171, %135
  %173 = icmp ugt i32 %77, 2
  br i1 %173, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %174 = getelementptr float, float* %83, i64 3
  %175 = load float, float* %174, align 4
  %176 = add <2 x i32> %87, <i32 3, i32 -3>
  %177 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %176, i1 true)
  %178 = sub <2 x i32> %177, %95
  %179 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %178, <2 x i32> zeroinitializer)
  %180 = mul <2 x i32> %179, <i32 -2, i32 -2>
  %181 = add <2 x i32> %180, %177
  %182 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %181, <2 x i32> zeroinitializer)
  %183 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %182)
  %184 = mul <2 x i32> %183, %103
  %185 = add <2 x i32> %184, %105
  %186 = mul <2 x i32> %185, %108
  %187 = sext <2 x i32> %186 to <2 x i64>
  %188 = getelementptr i32, <2 x i32*> %112, <2 x i64> %187
  %189 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %188, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift248 = shufflevector <2 x i32> %189, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %190 = add <2 x i32> %189, %shift248
  %191 = extractelement <2 x i32> %190, i64 0
  %192 = sitofp i32 %191 to float
  %193 = shufflevector <2 x i32> %186, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %194 = add <2 x i32> %193, <i32 1, i32 2>
  %195 = sext <2 x i32> %194 to <2 x i64>
  %196 = getelementptr i32, <2 x i32*> %112, <2 x i64> %195
  %197 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %196, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %198 = shufflevector <2 x i32> %186, <2 x i32> poison, <2 x i32> zeroinitializer
  %199 = add <2 x i32> %198, <i32 1, i32 2>
  %200 = sext <2 x i32> %199 to <2 x i64>
  %201 = getelementptr i32, <2 x i32*> %112, <2 x i64> %200
  %202 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %201, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %203 = add <2 x i32> %202, %197
  %204 = sitofp <2 x i32> %203 to <2 x float>
  %205 = insertelement <4 x float> poison, float %175, i64 0
  %shuffle243 = shufflevector <4 x float> %205, <4 x float> poison, <4 x i32> zeroinitializer
  %206 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %192, i64 0
  %207 = shufflevector <2 x float> %204, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %208 = shufflevector <4 x float> %206, <4 x float> %207, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %209 = fmul reassoc ninf nsz <4 x float> %shuffle243, %208
  %210 = fadd reassoc ninf nsz <4 x float> %209, %172
  %.not209 = icmp eq i32 %77, 3
  br i1 %.not209, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %211 = getelementptr float, float* %83, i64 4
  %212 = load float, float* %211, align 4
  %213 = add <2 x i32> %87, <i32 4, i32 -4>
  %214 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %213, i1 true)
  %215 = sub <2 x i32> %214, %95
  %216 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %215, <2 x i32> zeroinitializer)
  %217 = mul <2 x i32> %216, <i32 -2, i32 -2>
  %218 = add <2 x i32> %217, %214
  %219 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %218, <2 x i32> zeroinitializer)
  %220 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %219)
  %221 = mul <2 x i32> %220, %103
  %222 = add <2 x i32> %221, %105
  %223 = mul <2 x i32> %222, %108
  %224 = sext <2 x i32> %223 to <2 x i64>
  %225 = getelementptr i32, <2 x i32*> %112, <2 x i64> %224
  %226 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %225, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift249 = shufflevector <2 x i32> %226, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %227 = add <2 x i32> %226, %shift249
  %228 = extractelement <2 x i32> %227, i64 0
  %229 = sitofp i32 %228 to float
  %230 = shufflevector <2 x i32> %223, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %231 = add <2 x i32> %230, <i32 1, i32 2>
  %232 = sext <2 x i32> %231 to <2 x i64>
  %233 = getelementptr i32, <2 x i32*> %112, <2 x i64> %232
  %234 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %233, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %235 = shufflevector <2 x i32> %223, <2 x i32> poison, <2 x i32> zeroinitializer
  %236 = add <2 x i32> %235, <i32 1, i32 2>
  %237 = sext <2 x i32> %236 to <2 x i64>
  %238 = getelementptr i32, <2 x i32*> %112, <2 x i64> %237
  %239 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %238, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %240 = add <2 x i32> %239, %234
  %241 = sitofp <2 x i32> %240 to <2 x float>
  %242 = insertelement <4 x float> poison, float %212, i64 0
  %shuffle242 = shufflevector <4 x float> %242, <4 x float> poison, <4 x i32> zeroinitializer
  %243 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %229, i64 0
  %244 = shufflevector <2 x float> %241, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %245 = shufflevector <4 x float> %243, <4 x float> %244, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %246 = fmul reassoc ninf nsz <4 x float> %shuffle242, %245
  %247 = fadd reassoc ninf nsz <4 x float> %246, %210
  %248 = icmp ugt i32 %77, 4
  br i1 %248, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %249 = getelementptr float, float* %83, i64 5
  %250 = load float, float* %249, align 4
  %251 = add <2 x i32> %87, <i32 5, i32 -5>
  %252 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %251, i1 true)
  %253 = sub <2 x i32> %252, %95
  %254 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %253, <2 x i32> zeroinitializer)
  %255 = mul <2 x i32> %254, <i32 -2, i32 -2>
  %256 = add <2 x i32> %255, %252
  %257 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %256, <2 x i32> zeroinitializer)
  %258 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %257)
  %259 = mul <2 x i32> %258, %103
  %260 = add <2 x i32> %259, %105
  %261 = mul <2 x i32> %260, %108
  %262 = sext <2 x i32> %261 to <2 x i64>
  %263 = getelementptr i32, <2 x i32*> %112, <2 x i64> %262
  %264 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %263, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift250 = shufflevector <2 x i32> %264, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %265 = add <2 x i32> %264, %shift250
  %266 = extractelement <2 x i32> %265, i64 0
  %267 = sitofp i32 %266 to float
  %268 = shufflevector <2 x i32> %261, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %269 = add <2 x i32> %268, <i32 1, i32 2>
  %270 = sext <2 x i32> %269 to <2 x i64>
  %271 = getelementptr i32, <2 x i32*> %112, <2 x i64> %270
  %272 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %271, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %273 = shufflevector <2 x i32> %261, <2 x i32> poison, <2 x i32> zeroinitializer
  %274 = add <2 x i32> %273, <i32 1, i32 2>
  %275 = sext <2 x i32> %274 to <2 x i64>
  %276 = getelementptr i32, <2 x i32*> %112, <2 x i64> %275
  %277 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %276, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %278 = add <2 x i32> %277, %272
  %279 = sitofp <2 x i32> %278 to <2 x float>
  %280 = insertelement <4 x float> poison, float %250, i64 0
  %shuffle241 = shufflevector <4 x float> %280, <4 x float> poison, <4 x i32> zeroinitializer
  %281 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %267, i64 0
  %282 = shufflevector <2 x float> %279, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %283 = shufflevector <4 x float> %281, <4 x float> %282, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %284 = fmul reassoc ninf nsz <4 x float> %shuffle241, %283
  %285 = fadd reassoc ninf nsz <4 x float> %284, %247
  %.not210 = icmp eq i32 %77, 5
  br i1 %.not210, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %286 = getelementptr float, float* %83, i64 6
  %287 = load float, float* %286, align 4
  %288 = add <2 x i32> %87, <i32 6, i32 -6>
  %289 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %288, i1 true)
  %290 = sub <2 x i32> %289, %95
  %291 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %290, <2 x i32> zeroinitializer)
  %292 = mul <2 x i32> %291, <i32 -2, i32 -2>
  %293 = add <2 x i32> %292, %289
  %294 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %293, <2 x i32> zeroinitializer)
  %295 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %294)
  %296 = mul <2 x i32> %295, %103
  %297 = add <2 x i32> %296, %105
  %298 = mul <2 x i32> %297, %108
  %299 = sext <2 x i32> %298 to <2 x i64>
  %300 = getelementptr i32, <2 x i32*> %112, <2 x i64> %299
  %301 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %300, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift251 = shufflevector <2 x i32> %301, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %302 = add <2 x i32> %301, %shift251
  %303 = extractelement <2 x i32> %302, i64 0
  %304 = sitofp i32 %303 to float
  %305 = shufflevector <2 x i32> %298, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %306 = add <2 x i32> %305, <i32 1, i32 2>
  %307 = sext <2 x i32> %306 to <2 x i64>
  %308 = getelementptr i32, <2 x i32*> %112, <2 x i64> %307
  %309 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %308, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %310 = shufflevector <2 x i32> %298, <2 x i32> poison, <2 x i32> zeroinitializer
  %311 = add <2 x i32> %310, <i32 1, i32 2>
  %312 = sext <2 x i32> %311 to <2 x i64>
  %313 = getelementptr i32, <2 x i32*> %112, <2 x i64> %312
  %314 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %313, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %315 = add <2 x i32> %314, %309
  %316 = sitofp <2 x i32> %315 to <2 x float>
  %317 = insertelement <4 x float> poison, float %287, i64 0
  %shuffle246 = shufflevector <4 x float> %317, <4 x float> poison, <4 x i32> zeroinitializer
  %318 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %304, i64 0
  %319 = shufflevector <2 x float> %316, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %320 = shufflevector <4 x float> %318, <4 x float> %319, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %321 = fmul reassoc ninf nsz <4 x float> %shuffle246, %320
  %322 = fadd reassoc ninf nsz <4 x float> %321, %285
  %323 = icmp ugt i32 %77, 6
  br i1 %323, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %324 = getelementptr float, float* %83, i64 7
  %325 = load float, float* %324, align 4
  %326 = add <2 x i32> %87, <i32 7, i32 -7>
  %327 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %326, i1 true)
  %328 = sub <2 x i32> %327, %95
  %329 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %328, <2 x i32> zeroinitializer)
  %330 = mul <2 x i32> %329, <i32 -2, i32 -2>
  %331 = add <2 x i32> %330, %327
  %332 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %331, <2 x i32> zeroinitializer)
  %333 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %332)
  %334 = mul <2 x i32> %333, %103
  %335 = add <2 x i32> %334, %105
  %336 = mul <2 x i32> %335, %108
  %337 = sext <2 x i32> %336 to <2 x i64>
  %338 = getelementptr i32, <2 x i32*> %112, <2 x i64> %337
  %339 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %338, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift252 = shufflevector <2 x i32> %339, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %340 = add <2 x i32> %339, %shift252
  %341 = extractelement <2 x i32> %340, i64 0
  %342 = sitofp i32 %341 to float
  %343 = shufflevector <2 x i32> %336, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %344 = add <2 x i32> %343, <i32 1, i32 2>
  %345 = sext <2 x i32> %344 to <2 x i64>
  %346 = getelementptr i32, <2 x i32*> %112, <2 x i64> %345
  %347 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %346, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %348 = shufflevector <2 x i32> %336, <2 x i32> poison, <2 x i32> zeroinitializer
  %349 = add <2 x i32> %348, <i32 1, i32 2>
  %350 = sext <2 x i32> %349 to <2 x i64>
  %351 = getelementptr i32, <2 x i32*> %112, <2 x i64> %350
  %352 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %351, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %353 = add <2 x i32> %352, %347
  %354 = sitofp <2 x i32> %353 to <2 x float>
  %355 = insertelement <4 x float> poison, float %325, i64 0
  %shuffle240 = shufflevector <4 x float> %355, <4 x float> poison, <4 x i32> zeroinitializer
  %356 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %342, i64 0
  %357 = shufflevector <2 x float> %354, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %358 = shufflevector <4 x float> %356, <4 x float> %357, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %359 = fmul reassoc ninf nsz <4 x float> %shuffle240, %358
  %360 = fadd reassoc ninf nsz <4 x float> %359, %322
  %.not211 = icmp eq i32 %77, 7
  br i1 %.not211, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %361 = getelementptr float, float* %83, i64 8
  %362 = load float, float* %361, align 4
  %363 = add <2 x i32> %87, <i32 8, i32 -8>
  %364 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %363, i1 true)
  %365 = sub <2 x i32> %364, %95
  %366 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %365, <2 x i32> zeroinitializer)
  %367 = mul <2 x i32> %366, <i32 -2, i32 -2>
  %368 = add <2 x i32> %367, %364
  %369 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %368, <2 x i32> zeroinitializer)
  %370 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %369)
  %371 = mul <2 x i32> %370, %103
  %372 = add <2 x i32> %371, %105
  %373 = mul <2 x i32> %372, %108
  %374 = sext <2 x i32> %373 to <2 x i64>
  %375 = getelementptr i32, <2 x i32*> %112, <2 x i64> %374
  %376 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %375, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift253 = shufflevector <2 x i32> %376, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %377 = add <2 x i32> %376, %shift253
  %378 = extractelement <2 x i32> %377, i64 0
  %379 = sitofp i32 %378 to float
  %380 = shufflevector <2 x i32> %373, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %381 = add <2 x i32> %380, <i32 1, i32 2>
  %382 = sext <2 x i32> %381 to <2 x i64>
  %383 = getelementptr i32, <2 x i32*> %112, <2 x i64> %382
  %384 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %383, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %385 = shufflevector <2 x i32> %373, <2 x i32> poison, <2 x i32> zeroinitializer
  %386 = add <2 x i32> %385, <i32 1, i32 2>
  %387 = sext <2 x i32> %386 to <2 x i64>
  %388 = getelementptr i32, <2 x i32*> %112, <2 x i64> %387
  %389 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %388, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %390 = add <2 x i32> %389, %384
  %391 = sitofp <2 x i32> %390 to <2 x float>
  %392 = insertelement <4 x float> poison, float %362, i64 0
  %shuffle239 = shufflevector <4 x float> %392, <4 x float> poison, <4 x i32> zeroinitializer
  %393 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %379, i64 0
  %394 = shufflevector <2 x float> %391, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %395 = shufflevector <4 x float> %393, <4 x float> %394, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %396 = fmul reassoc ninf nsz <4 x float> %shuffle239, %395
  %397 = fadd reassoc ninf nsz <4 x float> %396, %360
  %398 = icmp ugt i32 %77, 8
  br i1 %398, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %399 = getelementptr float, float* %83, i64 9
  %400 = load float, float* %399, align 4
  %401 = add <2 x i32> %87, <i32 9, i32 -9>
  %402 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %401, i1 true)
  %403 = sub <2 x i32> %402, %95
  %404 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %403, <2 x i32> zeroinitializer)
  %405 = mul <2 x i32> %404, <i32 -2, i32 -2>
  %406 = add <2 x i32> %405, %402
  %407 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %406, <2 x i32> zeroinitializer)
  %408 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %407)
  %409 = mul <2 x i32> %408, %103
  %410 = add <2 x i32> %409, %105
  %411 = mul <2 x i32> %410, %108
  %412 = sext <2 x i32> %411 to <2 x i64>
  %413 = getelementptr i32, <2 x i32*> %112, <2 x i64> %412
  %414 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %413, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift254 = shufflevector <2 x i32> %414, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %415 = add <2 x i32> %414, %shift254
  %416 = extractelement <2 x i32> %415, i64 0
  %417 = sitofp i32 %416 to float
  %418 = shufflevector <2 x i32> %411, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %419 = add <2 x i32> %418, <i32 1, i32 2>
  %420 = sext <2 x i32> %419 to <2 x i64>
  %421 = getelementptr i32, <2 x i32*> %112, <2 x i64> %420
  %422 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %421, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %423 = shufflevector <2 x i32> %411, <2 x i32> poison, <2 x i32> zeroinitializer
  %424 = add <2 x i32> %423, <i32 1, i32 2>
  %425 = sext <2 x i32> %424 to <2 x i64>
  %426 = getelementptr i32, <2 x i32*> %112, <2 x i64> %425
  %427 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %426, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %428 = add <2 x i32> %427, %422
  %429 = sitofp <2 x i32> %428 to <2 x float>
  %430 = insertelement <4 x float> poison, float %400, i64 0
  %shuffle238 = shufflevector <4 x float> %430, <4 x float> poison, <4 x i32> zeroinitializer
  %431 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %417, i64 0
  %432 = shufflevector <2 x float> %429, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %433 = shufflevector <4 x float> %431, <4 x float> %432, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %434 = fmul reassoc ninf nsz <4 x float> %shuffle238, %433
  %435 = fadd reassoc ninf nsz <4 x float> %434, %397
  %.not212 = icmp eq i32 %77, 9
  br i1 %.not212, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %436 = getelementptr float, float* %83, i64 10
  %437 = load float, float* %436, align 4
  %438 = add <2 x i32> %87, <i32 10, i32 -10>
  %439 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %438, i1 true)
  %440 = sub <2 x i32> %439, %95
  %441 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %440, <2 x i32> zeroinitializer)
  %442 = mul <2 x i32> %441, <i32 -2, i32 -2>
  %443 = add <2 x i32> %442, %439
  %444 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %443, <2 x i32> zeroinitializer)
  %445 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %444)
  %446 = mul <2 x i32> %445, %103
  %447 = add <2 x i32> %446, %105
  %448 = mul <2 x i32> %447, %108
  %449 = sext <2 x i32> %448 to <2 x i64>
  %450 = getelementptr i32, <2 x i32*> %112, <2 x i64> %449
  %451 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %450, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift255 = shufflevector <2 x i32> %451, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %452 = add <2 x i32> %451, %shift255
  %453 = extractelement <2 x i32> %452, i64 0
  %454 = sitofp i32 %453 to float
  %455 = shufflevector <2 x i32> %448, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %456 = add <2 x i32> %455, <i32 1, i32 2>
  %457 = sext <2 x i32> %456 to <2 x i64>
  %458 = getelementptr i32, <2 x i32*> %112, <2 x i64> %457
  %459 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %458, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %460 = shufflevector <2 x i32> %448, <2 x i32> poison, <2 x i32> zeroinitializer
  %461 = add <2 x i32> %460, <i32 1, i32 2>
  %462 = sext <2 x i32> %461 to <2 x i64>
  %463 = getelementptr i32, <2 x i32*> %112, <2 x i64> %462
  %464 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %463, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %465 = add <2 x i32> %464, %459
  %466 = sitofp <2 x i32> %465 to <2 x float>
  %467 = insertelement <4 x float> poison, float %437, i64 0
  %shuffle237 = shufflevector <4 x float> %467, <4 x float> poison, <4 x i32> zeroinitializer
  %468 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %454, i64 0
  %469 = shufflevector <2 x float> %466, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %470 = shufflevector <4 x float> %468, <4 x float> %469, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %471 = fmul reassoc ninf nsz <4 x float> %shuffle237, %470
  %472 = fadd reassoc ninf nsz <4 x float> %471, %435
  %473 = icmp ugt i32 %77, 10
  br i1 %473, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %474 = getelementptr float, float* %83, i64 11
  %475 = load float, float* %474, align 4
  %476 = add <2 x i32> %87, <i32 11, i32 -11>
  %477 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %476, i1 true)
  %478 = sub <2 x i32> %477, %95
  %479 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %478, <2 x i32> zeroinitializer)
  %480 = mul <2 x i32> %479, <i32 -2, i32 -2>
  %481 = add <2 x i32> %480, %477
  %482 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %481, <2 x i32> zeroinitializer)
  %483 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %482)
  %484 = mul <2 x i32> %483, %103
  %485 = add <2 x i32> %484, %105
  %486 = mul <2 x i32> %485, %108
  %487 = sext <2 x i32> %486 to <2 x i64>
  %488 = getelementptr i32, <2 x i32*> %112, <2 x i64> %487
  %489 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %488, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift256 = shufflevector <2 x i32> %489, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %490 = add <2 x i32> %489, %shift256
  %491 = extractelement <2 x i32> %490, i64 0
  %492 = sitofp i32 %491 to float
  %493 = shufflevector <2 x i32> %486, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %494 = add <2 x i32> %493, <i32 1, i32 2>
  %495 = sext <2 x i32> %494 to <2 x i64>
  %496 = getelementptr i32, <2 x i32*> %112, <2 x i64> %495
  %497 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %496, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %498 = shufflevector <2 x i32> %486, <2 x i32> poison, <2 x i32> zeroinitializer
  %499 = add <2 x i32> %498, <i32 1, i32 2>
  %500 = sext <2 x i32> %499 to <2 x i64>
  %501 = getelementptr i32, <2 x i32*> %112, <2 x i64> %500
  %502 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %501, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %503 = add <2 x i32> %502, %497
  %504 = sitofp <2 x i32> %503 to <2 x float>
  %505 = insertelement <4 x float> poison, float %475, i64 0
  %shuffle236 = shufflevector <4 x float> %505, <4 x float> poison, <4 x i32> zeroinitializer
  %506 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %492, i64 0
  %507 = shufflevector <2 x float> %504, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %508 = shufflevector <4 x float> %506, <4 x float> %507, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %509 = fmul reassoc ninf nsz <4 x float> %shuffle236, %508
  %510 = fadd reassoc ninf nsz <4 x float> %509, %472
  %.not213 = icmp eq i32 %77, 11
  br i1 %.not213, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %511 = getelementptr float, float* %83, i64 12
  %512 = load float, float* %511, align 4
  %513 = add <2 x i32> %87, <i32 12, i32 -12>
  %514 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %513, i1 true)
  %515 = sub <2 x i32> %514, %95
  %516 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %515, <2 x i32> zeroinitializer)
  %517 = mul <2 x i32> %516, <i32 -2, i32 -2>
  %518 = add <2 x i32> %517, %514
  %519 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %518, <2 x i32> zeroinitializer)
  %520 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %519)
  %521 = mul <2 x i32> %520, %103
  %522 = add <2 x i32> %521, %105
  %523 = mul <2 x i32> %522, %108
  %524 = sext <2 x i32> %523 to <2 x i64>
  %525 = getelementptr i32, <2 x i32*> %112, <2 x i64> %524
  %526 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %525, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift257 = shufflevector <2 x i32> %526, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %527 = add <2 x i32> %526, %shift257
  %528 = extractelement <2 x i32> %527, i64 0
  %529 = sitofp i32 %528 to float
  %530 = shufflevector <2 x i32> %523, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %531 = add <2 x i32> %530, <i32 1, i32 2>
  %532 = sext <2 x i32> %531 to <2 x i64>
  %533 = getelementptr i32, <2 x i32*> %112, <2 x i64> %532
  %534 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %533, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %535 = shufflevector <2 x i32> %523, <2 x i32> poison, <2 x i32> zeroinitializer
  %536 = add <2 x i32> %535, <i32 1, i32 2>
  %537 = sext <2 x i32> %536 to <2 x i64>
  %538 = getelementptr i32, <2 x i32*> %112, <2 x i64> %537
  %539 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %538, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %540 = add <2 x i32> %539, %534
  %541 = sitofp <2 x i32> %540 to <2 x float>
  %542 = insertelement <4 x float> poison, float %512, i64 0
  %shuffle235 = shufflevector <4 x float> %542, <4 x float> poison, <4 x i32> zeroinitializer
  %543 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %529, i64 0
  %544 = shufflevector <2 x float> %541, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %545 = shufflevector <4 x float> %543, <4 x float> %544, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %546 = fmul reassoc ninf nsz <4 x float> %shuffle235, %545
  %547 = fadd reassoc ninf nsz <4 x float> %546, %510
  %548 = icmp ugt i32 %77, 12
  br i1 %548, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %549 = getelementptr float, float* %83, i64 13
  %550 = load float, float* %549, align 4
  %551 = add <2 x i32> %87, <i32 13, i32 -13>
  %552 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %551, i1 true)
  %553 = sub <2 x i32> %552, %95
  %554 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %553, <2 x i32> zeroinitializer)
  %555 = mul <2 x i32> %554, <i32 -2, i32 -2>
  %556 = add <2 x i32> %555, %552
  %557 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %556, <2 x i32> zeroinitializer)
  %558 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %557)
  %559 = mul <2 x i32> %558, %103
  %560 = add <2 x i32> %559, %105
  %561 = mul <2 x i32> %560, %108
  %562 = sext <2 x i32> %561 to <2 x i64>
  %563 = getelementptr i32, <2 x i32*> %112, <2 x i64> %562
  %564 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %563, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift258 = shufflevector <2 x i32> %564, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %565 = add <2 x i32> %564, %shift258
  %566 = extractelement <2 x i32> %565, i64 0
  %567 = sitofp i32 %566 to float
  %568 = shufflevector <2 x i32> %561, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %569 = add <2 x i32> %568, <i32 1, i32 2>
  %570 = sext <2 x i32> %569 to <2 x i64>
  %571 = getelementptr i32, <2 x i32*> %112, <2 x i64> %570
  %572 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %571, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %573 = shufflevector <2 x i32> %561, <2 x i32> poison, <2 x i32> zeroinitializer
  %574 = add <2 x i32> %573, <i32 1, i32 2>
  %575 = sext <2 x i32> %574 to <2 x i64>
  %576 = getelementptr i32, <2 x i32*> %112, <2 x i64> %575
  %577 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %576, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %578 = add <2 x i32> %577, %572
  %579 = sitofp <2 x i32> %578 to <2 x float>
  %580 = insertelement <4 x float> poison, float %550, i64 0
  %shuffle234 = shufflevector <4 x float> %580, <4 x float> poison, <4 x i32> zeroinitializer
  %581 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %567, i64 0
  %582 = shufflevector <2 x float> %579, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %583 = shufflevector <4 x float> %581, <4 x float> %582, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %584 = fmul reassoc ninf nsz <4 x float> %shuffle234, %583
  %585 = fadd reassoc ninf nsz <4 x float> %584, %547
  %.not214 = icmp eq i32 %77, 13
  br i1 %.not214, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %586 = getelementptr float, float* %83, i64 14
  %587 = load float, float* %586, align 4
  %588 = add <2 x i32> %87, <i32 14, i32 -14>
  %589 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %588, i1 true)
  %590 = sub <2 x i32> %589, %95
  %591 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %590, <2 x i32> zeroinitializer)
  %592 = mul <2 x i32> %591, <i32 -2, i32 -2>
  %593 = add <2 x i32> %592, %589
  %594 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %593, <2 x i32> zeroinitializer)
  %595 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %594)
  %596 = mul <2 x i32> %595, %103
  %597 = add <2 x i32> %596, %105
  %598 = mul <2 x i32> %597, %108
  %599 = sext <2 x i32> %598 to <2 x i64>
  %600 = getelementptr i32, <2 x i32*> %112, <2 x i64> %599
  %601 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %600, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift259 = shufflevector <2 x i32> %601, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %602 = add <2 x i32> %601, %shift259
  %603 = extractelement <2 x i32> %602, i64 0
  %604 = sitofp i32 %603 to float
  %605 = shufflevector <2 x i32> %598, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %606 = add <2 x i32> %605, <i32 1, i32 2>
  %607 = sext <2 x i32> %606 to <2 x i64>
  %608 = getelementptr i32, <2 x i32*> %112, <2 x i64> %607
  %609 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %608, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %610 = shufflevector <2 x i32> %598, <2 x i32> poison, <2 x i32> zeroinitializer
  %611 = add <2 x i32> %610, <i32 1, i32 2>
  %612 = sext <2 x i32> %611 to <2 x i64>
  %613 = getelementptr i32, <2 x i32*> %112, <2 x i64> %612
  %614 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %613, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %615 = add <2 x i32> %614, %609
  %616 = sitofp <2 x i32> %615 to <2 x float>
  %617 = insertelement <4 x float> poison, float %587, i64 0
  %shuffle233 = shufflevector <4 x float> %617, <4 x float> poison, <4 x i32> zeroinitializer
  %618 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %604, i64 0
  %619 = shufflevector <2 x float> %616, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %620 = shufflevector <4 x float> %618, <4 x float> %619, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %621 = fmul reassoc ninf nsz <4 x float> %shuffle233, %620
  %622 = fadd reassoc ninf nsz <4 x float> %621, %585
  %623 = icmp ugt i32 %77, 14
  br i1 %623, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %624 = getelementptr float, float* %83, i64 15
  %625 = load float, float* %624, align 4
  %626 = add <2 x i32> %87, <i32 15, i32 -15>
  %627 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %626, i1 true)
  %628 = sub <2 x i32> %627, %95
  %629 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %628, <2 x i32> zeroinitializer)
  %630 = mul <2 x i32> %629, <i32 -2, i32 -2>
  %631 = add <2 x i32> %630, %627
  %632 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %631, <2 x i32> zeroinitializer)
  %633 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %632)
  %634 = mul <2 x i32> %633, %103
  %635 = add <2 x i32> %634, %105
  %636 = mul <2 x i32> %635, %108
  %637 = sext <2 x i32> %636 to <2 x i64>
  %638 = getelementptr i32, <2 x i32*> %112, <2 x i64> %637
  %639 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %638, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift260 = shufflevector <2 x i32> %639, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %640 = add <2 x i32> %639, %shift260
  %641 = extractelement <2 x i32> %640, i64 0
  %642 = sitofp i32 %641 to float
  %643 = shufflevector <2 x i32> %636, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %644 = add <2 x i32> %643, <i32 1, i32 2>
  %645 = sext <2 x i32> %644 to <2 x i64>
  %646 = getelementptr i32, <2 x i32*> %112, <2 x i64> %645
  %647 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %646, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %648 = shufflevector <2 x i32> %636, <2 x i32> poison, <2 x i32> zeroinitializer
  %649 = add <2 x i32> %648, <i32 1, i32 2>
  %650 = sext <2 x i32> %649 to <2 x i64>
  %651 = getelementptr i32, <2 x i32*> %112, <2 x i64> %650
  %652 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %651, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %653 = add <2 x i32> %652, %647
  %654 = sitofp <2 x i32> %653 to <2 x float>
  %655 = insertelement <4 x float> poison, float %625, i64 0
  %shuffle232 = shufflevector <4 x float> %655, <4 x float> poison, <4 x i32> zeroinitializer
  %656 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %642, i64 0
  %657 = shufflevector <2 x float> %654, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %658 = shufflevector <4 x float> %656, <4 x float> %657, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %659 = fmul reassoc ninf nsz <4 x float> %shuffle232, %658
  %660 = fadd reassoc ninf nsz <4 x float> %659, %622
  %.not215 = icmp eq i32 %77, 15
  br i1 %.not215, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %661 = getelementptr float, float* %83, i64 16
  %662 = load float, float* %661, align 4
  %663 = add <2 x i32> %87, <i32 16, i32 -16>
  %664 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %663, i1 true)
  %665 = sub <2 x i32> %664, %95
  %666 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %665, <2 x i32> zeroinitializer)
  %667 = mul <2 x i32> %666, <i32 -2, i32 -2>
  %668 = add <2 x i32> %667, %664
  %669 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %668, <2 x i32> zeroinitializer)
  %670 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %95, <2 x i32> %669)
  %671 = mul <2 x i32> %670, %103
  %672 = add <2 x i32> %671, %105
  %673 = mul <2 x i32> %672, %108
  %674 = sext <2 x i32> %673 to <2 x i64>
  %675 = getelementptr i32, <2 x i32*> %112, <2 x i64> %674
  %676 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %675, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %shift261 = shufflevector <2 x i32> %676, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %677 = add <2 x i32> %676, %shift261
  %678 = extractelement <2 x i32> %677, i64 0
  %679 = sitofp i32 %678 to float
  %680 = shufflevector <2 x i32> %673, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %681 = add <2 x i32> %680, <i32 1, i32 2>
  %682 = sext <2 x i32> %681 to <2 x i64>
  %683 = getelementptr i32, <2 x i32*> %112, <2 x i64> %682
  %684 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %683, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %685 = shufflevector <2 x i32> %673, <2 x i32> poison, <2 x i32> zeroinitializer
  %686 = add <2 x i32> %685, <i32 1, i32 2>
  %687 = sext <2 x i32> %686 to <2 x i64>
  %688 = getelementptr i32, <2 x i32*> %112, <2 x i64> %687
  %689 = call <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*> %688, i32 4, <2 x i1> <i1 true, i1 true>, <2 x i32> undef)
  %690 = add <2 x i32> %689, %684
  %691 = sitofp <2 x i32> %690 to <2 x float>
  %692 = insertelement <4 x float> poison, float %662, i64 0
  %shuffle = shufflevector <4 x float> %692, <4 x float> poison, <4 x i32> zeroinitializer
  %693 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %679, i64 0
  %694 = shufflevector <2 x float> %691, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %695 = shufflevector <4 x float> %693, <4 x float> %694, <4 x i32> <i32 0, i32 4, i32 5, i32 3>
  %696 = fmul reassoc ninf nsz <4 x float> %shuffle, %695
  %697 = fadd reassoc ninf nsz <4 x float> %696, %660
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %698 = phi <4 x float> [ %697, %true_block43 ], [ %660, %after_if42 ], [ %622, %after_if39 ], [ %585, %after_if36 ], [ %547, %after_if33 ], [ %510, %after_if30 ], [ %472, %after_if27 ], [ %435, %after_if24 ], [ %397, %after_if21 ], [ %360, %after_if18 ], [ %322, %after_if15 ], [ %285, %after_if12 ], [ %247, %after_if9 ], [ %210, %after_if6 ], [ %172, %after_if3 ], [ %135, %after_if ], [ %82, %for_loop_body ]
  %699 = extractelement <4 x float> %698, i64 0
  %700 = extractelement <4 x float> %698, i64 3
  %701 = fdiv reassoc ninf nsz float %699, %700
  %702 = load i32*, i32** %28, align 8
  %703 = load i32, i32* %29, align 4
  %704 = load i32, i32* %30, align 4
  %705 = mul i32 %703, %49
  %706 = add i32 %705, %54
  %707 = mul i32 %706, %704
  %708 = sext i32 %707 to i64
  %709 = getelementptr i32, i32* %702, i64 %708
  %710 = fptosi float %701 to i32
  store i32 %710, i32* %709, align 4
  %711 = extractelement <4 x float> %698, i64 1
  %712 = fdiv reassoc ninf nsz float %711, %700
  %713 = load i32*, i32** %28, align 8
  %714 = load i32, i32* %29, align 4
  %715 = load i32, i32* %30, align 4
  %716 = mul i32 %714, %49
  %717 = add i32 %716, %54
  %718 = mul i32 %717, %715
  %719 = add i32 %718, 1
  %720 = sext i32 %719 to i64
  %721 = getelementptr i32, i32* %713, i64 %720
  %722 = fptosi float %712 to i32
  store i32 %722, i32* %721, align 4
  %723 = extractelement <4 x float> %698, i64 2
  %724 = fdiv reassoc ninf nsz float %723, %700
  %725 = load i32*, i32** %28, align 8
  %726 = load i32, i32* %29, align 4
  %727 = load i32, i32* %30, align 4
  %728 = mul i32 %726, %49
  %729 = add i32 %728, %54
  %730 = mul i32 %729, %727
  %731 = add i32 %730, 2
  %732 = sext i32 %731 to i64
  %733 = getelementptr i32, i32* %725, i64 %732
  %734 = fptosi float %724 to i32
  store i32 %734, i32* %733, align 4
  %735 = add nsw i32 %.0115231, 1
  %exitcond.not = icmp eq i32 %19, %735
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.84, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.84**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.84*, %struct.RuntimeContext.84** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.84* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.84* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
declare <2 x i32> @llvm.masked.gather.v2i32.v2p0i32(<2 x i32*>, i32 immarg, <2 x i1>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.abs.v2i32(<2 x i32>, i1 immarg) #8

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
