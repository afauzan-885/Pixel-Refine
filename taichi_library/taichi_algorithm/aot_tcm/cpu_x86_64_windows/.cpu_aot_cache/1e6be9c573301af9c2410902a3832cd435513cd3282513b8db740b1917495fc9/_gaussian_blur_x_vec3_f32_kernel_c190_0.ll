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
define void @_gaussian_blur_x_vec3_f32_kernel_c190_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 3
  %5 = load i32, i32* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 12
  %11 = bitcast i8* %10 to i32*
  store i32 %5, i32* %11, align 4
  %12 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %13 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %12, i64 0, i32 5
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %21 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %22 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  store i32 %21, i32* %26, align 4
  %27 = mul i32 %21, %20
  %28 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %6, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %28, i64 0, i32 14
  %30 = bitcast i8** %29 to i32**
  %31 = load i32*, i32** %30, align 8
  store i32 %27, i32* %31, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_x_vec3_f32_kernel_c190_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %23 = load float*, float** %22, align 8
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.0115231 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %737, %after_if45 ]
  %29 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.0115231, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.0115231
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.0115231, 0
  %40 = icmp ne i32 %.0115231, %36
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg116 = sext i1 %42 to i32
  %43 = load float, float* %23, align 4
  %44 = load float*, float** %25, align 8
  %45 = load i32, i32* %26, align 4
  %46 = add i32 %35, %.neg116
  %47 = mul i32 %46, %34
  %48 = insertelement <2 x i32> poison, i32 %.0115231, i64 0
  %49 = insertelement <2 x i32> %48, i32 %45, i64 1
  %50 = insertelement <2 x i32> poison, i32 %47, i64 0
  %51 = insertelement <2 x i32> %50, i32 %46, i64 1
  %52 = sub <2 x i32> %49, %51
  %53 = mul <2 x i32> %49, %51
  %54 = extractelement <2 x i32> %52, i64 0
  %55 = extractelement <2 x i32> %53, i64 1
  %56 = add i32 %54, %55
  %57 = mul i32 %56, 3
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, float* %44, i64 %58
  %60 = load float, float* %59, align 4
  %61 = add i32 %57, 1
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, float* %44, i64 %62
  %64 = load float, float* %63, align 4
  %65 = add i32 %57, 2
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, float* %44, i64 %66
  %68 = load float, float* %67, align 4
  %69 = fmul reassoc ninf nsz float %60, %43
  %70 = fmul reassoc ninf nsz float %64, %43
  %71 = fmul reassoc ninf nsz float %68, %43
  %72 = getelementptr inbounds i8, i8* %31, i64 8
  %73 = bitcast i8* %72 to i32*
  %74 = load i32, i32* %73, align 4
  %75 = icmp sgt i32 %74, 0
  %76 = insertelement <4 x float> poison, float %69, i64 0
  %77 = insertelement <4 x float> %76, float %70, i64 1
  %78 = insertelement <4 x float> %77, float %71, i64 2
  %79 = insertelement <4 x float> %78, float %43, i64 3
  br i1 %75, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %80 = load float*, float** %22, align 8
  %81 = getelementptr float, float* %80, i64 1
  %82 = load float, float* %81, align 4
  %83 = shufflevector <2 x i32> %52, <2 x i32> poison, <2 x i32> zeroinitializer
  %84 = add <2 x i32> %83, <i32 1, i32 -1>
  %85 = getelementptr inbounds i8, i8* %31, i64 12
  %86 = bitcast i8* %85 to i32*
  %87 = load i32, i32* %86, align 4
  %88 = add i32 %87, -1
  %89 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %84, i1 true)
  %90 = insertelement <2 x i32> poison, i32 %88, i64 0
  %91 = shufflevector <2 x i32> %90, <2 x i32> poison, <2 x i32> zeroinitializer
  %92 = sub <2 x i32> %89, %91
  %93 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %92, <2 x i32> zeroinitializer)
  %94 = mul <2 x i32> %93, <i32 -2, i32 -2>
  %95 = add <2 x i32> %94, %89
  %96 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %95, <2 x i32> zeroinitializer)
  %97 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %96)
  %98 = shufflevector <2 x i32> %53, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %99 = add <2 x i32> %97, %98
  %100 = mul <2 x i32> %99, <i32 3, i32 3>
  %101 = sext <2 x i32> %100 to <2 x i64>
  %102 = extractelement <2 x i64> %101, i64 1
  %103 = getelementptr float, float* %44, i64 %102
  %104 = load float, float* %103, align 4
  %105 = extractelement <2 x i64> %101, i64 0
  %106 = getelementptr float, float* %44, i64 %105
  %107 = load float, float* %106, align 4
  %108 = add <2 x i32> %100, <i32 1, i32 1>
  %109 = sext <2 x i32> %108 to <2 x i64>
  %110 = insertelement <2 x float*> poison, float* %44, i64 0
  %111 = shufflevector <2 x float*> %110, <2 x float*> poison, <2 x i32> zeroinitializer
  %112 = getelementptr float, <2 x float*> %111, <2 x i64> %109
  %113 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %112, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %114 = add <2 x i32> %100, <i32 2, i32 2>
  %115 = sext <2 x i32> %114 to <2 x i64>
  %116 = getelementptr float, <2 x float*> %111, <2 x i64> %115
  %117 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %116, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %118 = fadd reassoc ninf nsz float %107, %104
  %shift = shufflevector <2 x float> %113, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %119 = fadd reassoc ninf nsz <2 x float> %113, %shift
  %120 = shufflevector <2 x float> %119, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift247 = shufflevector <2 x float> %117, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %121 = fadd reassoc ninf nsz <2 x float> %117, %shift247
  %122 = shufflevector <2 x float> %121, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %123 = insertelement <4 x float> poison, float %82, i64 0
  %shuffle245 = shufflevector <4 x float> %123, <4 x float> poison, <4 x i32> zeroinitializer
  %124 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %118, i64 0
  %125 = shufflevector <4 x float> %124, <4 x float> %120, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %126 = shufflevector <4 x float> %125, <4 x float> %122, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %127 = fmul reassoc ninf nsz <4 x float> %shuffle245, %126
  %128 = fadd reassoc ninf nsz <4 x float> %127, %79
  %.not = icmp eq i32 %74, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %129 = getelementptr float, float* %80, i64 2
  %130 = load float, float* %129, align 4
  %131 = add <2 x i32> %83, <i32 2, i32 -2>
  %132 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %131, i1 true)
  %133 = sub <2 x i32> %132, %91
  %134 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %133, <2 x i32> zeroinitializer)
  %135 = mul <2 x i32> %134, <i32 -2, i32 -2>
  %136 = add <2 x i32> %135, %132
  %137 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %136, <2 x i32> zeroinitializer)
  %138 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %137)
  %139 = add <2 x i32> %138, %98
  %140 = mul <2 x i32> %139, <i32 3, i32 3>
  %141 = sext <2 x i32> %140 to <2 x i64>
  %142 = extractelement <2 x i64> %141, i64 1
  %143 = getelementptr float, float* %44, i64 %142
  %144 = load float, float* %143, align 4
  %145 = extractelement <2 x i64> %141, i64 0
  %146 = getelementptr float, float* %44, i64 %145
  %147 = load float, float* %146, align 4
  %148 = add <2 x i32> %140, <i32 1, i32 1>
  %149 = sext <2 x i32> %148 to <2 x i64>
  %150 = getelementptr float, <2 x float*> %111, <2 x i64> %149
  %151 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %150, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %152 = add <2 x i32> %140, <i32 2, i32 2>
  %153 = sext <2 x i32> %152 to <2 x i64>
  %154 = getelementptr float, <2 x float*> %111, <2 x i64> %153
  %155 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %154, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %156 = fadd reassoc ninf nsz float %147, %144
  %shift248 = shufflevector <2 x float> %151, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %157 = fadd reassoc ninf nsz <2 x float> %151, %shift248
  %158 = shufflevector <2 x float> %157, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift249 = shufflevector <2 x float> %155, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %159 = fadd reassoc ninf nsz <2 x float> %155, %shift249
  %160 = shufflevector <2 x float> %159, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %161 = insertelement <4 x float> poison, float %130, i64 0
  %shuffle244 = shufflevector <4 x float> %161, <4 x float> poison, <4 x i32> zeroinitializer
  %162 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %156, i64 0
  %163 = shufflevector <4 x float> %162, <4 x float> %158, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %164 = shufflevector <4 x float> %163, <4 x float> %160, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %165 = fmul reassoc ninf nsz <4 x float> %shuffle244, %164
  %166 = fadd reassoc ninf nsz <4 x float> %165, %128
  %167 = icmp ugt i32 %74, 2
  br i1 %167, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %168 = getelementptr float, float* %80, i64 3
  %169 = load float, float* %168, align 4
  %170 = add <2 x i32> %83, <i32 3, i32 -3>
  %171 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %170, i1 true)
  %172 = sub <2 x i32> %171, %91
  %173 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %172, <2 x i32> zeroinitializer)
  %174 = mul <2 x i32> %173, <i32 -2, i32 -2>
  %175 = add <2 x i32> %174, %171
  %176 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %175, <2 x i32> zeroinitializer)
  %177 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %176)
  %178 = add <2 x i32> %177, %98
  %179 = mul <2 x i32> %178, <i32 3, i32 3>
  %180 = sext <2 x i32> %179 to <2 x i64>
  %181 = extractelement <2 x i64> %180, i64 1
  %182 = getelementptr float, float* %44, i64 %181
  %183 = load float, float* %182, align 4
  %184 = extractelement <2 x i64> %180, i64 0
  %185 = getelementptr float, float* %44, i64 %184
  %186 = load float, float* %185, align 4
  %187 = add <2 x i32> %179, <i32 1, i32 1>
  %188 = sext <2 x i32> %187 to <2 x i64>
  %189 = getelementptr float, <2 x float*> %111, <2 x i64> %188
  %190 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %189, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %191 = add <2 x i32> %179, <i32 2, i32 2>
  %192 = sext <2 x i32> %191 to <2 x i64>
  %193 = getelementptr float, <2 x float*> %111, <2 x i64> %192
  %194 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %193, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %195 = fadd reassoc ninf nsz float %186, %183
  %shift250 = shufflevector <2 x float> %190, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %196 = fadd reassoc ninf nsz <2 x float> %190, %shift250
  %197 = shufflevector <2 x float> %196, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift251 = shufflevector <2 x float> %194, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %198 = fadd reassoc ninf nsz <2 x float> %194, %shift251
  %199 = shufflevector <2 x float> %198, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %200 = insertelement <4 x float> poison, float %169, i64 0
  %shuffle243 = shufflevector <4 x float> %200, <4 x float> poison, <4 x i32> zeroinitializer
  %201 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %195, i64 0
  %202 = shufflevector <4 x float> %201, <4 x float> %197, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %203 = shufflevector <4 x float> %202, <4 x float> %199, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %204 = fmul reassoc ninf nsz <4 x float> %shuffle243, %203
  %205 = fadd reassoc ninf nsz <4 x float> %204, %166
  %.not209 = icmp eq i32 %74, 3
  br i1 %.not209, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %206 = getelementptr float, float* %80, i64 4
  %207 = load float, float* %206, align 4
  %208 = add <2 x i32> %83, <i32 4, i32 -4>
  %209 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %208, i1 true)
  %210 = sub <2 x i32> %209, %91
  %211 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %210, <2 x i32> zeroinitializer)
  %212 = mul <2 x i32> %211, <i32 -2, i32 -2>
  %213 = add <2 x i32> %212, %209
  %214 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %213, <2 x i32> zeroinitializer)
  %215 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %214)
  %216 = add <2 x i32> %215, %98
  %217 = mul <2 x i32> %216, <i32 3, i32 3>
  %218 = sext <2 x i32> %217 to <2 x i64>
  %219 = extractelement <2 x i64> %218, i64 1
  %220 = getelementptr float, float* %44, i64 %219
  %221 = load float, float* %220, align 4
  %222 = extractelement <2 x i64> %218, i64 0
  %223 = getelementptr float, float* %44, i64 %222
  %224 = load float, float* %223, align 4
  %225 = add <2 x i32> %217, <i32 1, i32 1>
  %226 = sext <2 x i32> %225 to <2 x i64>
  %227 = getelementptr float, <2 x float*> %111, <2 x i64> %226
  %228 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %227, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %229 = add <2 x i32> %217, <i32 2, i32 2>
  %230 = sext <2 x i32> %229 to <2 x i64>
  %231 = getelementptr float, <2 x float*> %111, <2 x i64> %230
  %232 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %231, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %233 = fadd reassoc ninf nsz float %224, %221
  %shift252 = shufflevector <2 x float> %228, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %234 = fadd reassoc ninf nsz <2 x float> %228, %shift252
  %235 = shufflevector <2 x float> %234, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift253 = shufflevector <2 x float> %232, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %236 = fadd reassoc ninf nsz <2 x float> %232, %shift253
  %237 = shufflevector <2 x float> %236, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %238 = insertelement <4 x float> poison, float %207, i64 0
  %shuffle242 = shufflevector <4 x float> %238, <4 x float> poison, <4 x i32> zeroinitializer
  %239 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %233, i64 0
  %240 = shufflevector <4 x float> %239, <4 x float> %235, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %241 = shufflevector <4 x float> %240, <4 x float> %237, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %242 = fmul reassoc ninf nsz <4 x float> %shuffle242, %241
  %243 = fadd reassoc ninf nsz <4 x float> %242, %205
  %244 = icmp ugt i32 %74, 4
  br i1 %244, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %245 = getelementptr float, float* %80, i64 5
  %246 = load float, float* %245, align 4
  %247 = add <2 x i32> %83, <i32 5, i32 -5>
  %248 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %247, i1 true)
  %249 = sub <2 x i32> %248, %91
  %250 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %249, <2 x i32> zeroinitializer)
  %251 = mul <2 x i32> %250, <i32 -2, i32 -2>
  %252 = add <2 x i32> %251, %248
  %253 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %252, <2 x i32> zeroinitializer)
  %254 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %253)
  %255 = add <2 x i32> %254, %98
  %256 = mul <2 x i32> %255, <i32 3, i32 3>
  %257 = sext <2 x i32> %256 to <2 x i64>
  %258 = extractelement <2 x i64> %257, i64 1
  %259 = getelementptr float, float* %44, i64 %258
  %260 = load float, float* %259, align 4
  %261 = extractelement <2 x i64> %257, i64 0
  %262 = getelementptr float, float* %44, i64 %261
  %263 = load float, float* %262, align 4
  %264 = add <2 x i32> %256, <i32 1, i32 1>
  %265 = sext <2 x i32> %264 to <2 x i64>
  %266 = getelementptr float, <2 x float*> %111, <2 x i64> %265
  %267 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %266, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %268 = add <2 x i32> %256, <i32 2, i32 2>
  %269 = sext <2 x i32> %268 to <2 x i64>
  %270 = getelementptr float, <2 x float*> %111, <2 x i64> %269
  %271 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %270, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %272 = fadd reassoc ninf nsz float %263, %260
  %shift254 = shufflevector <2 x float> %267, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %273 = fadd reassoc ninf nsz <2 x float> %267, %shift254
  %274 = shufflevector <2 x float> %273, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift255 = shufflevector <2 x float> %271, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %275 = fadd reassoc ninf nsz <2 x float> %271, %shift255
  %276 = shufflevector <2 x float> %275, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %277 = insertelement <4 x float> poison, float %246, i64 0
  %shuffle241 = shufflevector <4 x float> %277, <4 x float> poison, <4 x i32> zeroinitializer
  %278 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %272, i64 0
  %279 = shufflevector <4 x float> %278, <4 x float> %274, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %280 = shufflevector <4 x float> %279, <4 x float> %276, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %281 = fmul reassoc ninf nsz <4 x float> %shuffle241, %280
  %282 = fadd reassoc ninf nsz <4 x float> %281, %243
  %.not210 = icmp eq i32 %74, 5
  br i1 %.not210, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %283 = getelementptr float, float* %80, i64 6
  %284 = load float, float* %283, align 4
  %285 = add <2 x i32> %83, <i32 6, i32 -6>
  %286 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %285, i1 true)
  %287 = sub <2 x i32> %286, %91
  %288 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %287, <2 x i32> zeroinitializer)
  %289 = mul <2 x i32> %288, <i32 -2, i32 -2>
  %290 = add <2 x i32> %289, %286
  %291 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %290, <2 x i32> zeroinitializer)
  %292 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %291)
  %293 = add <2 x i32> %292, %98
  %294 = mul <2 x i32> %293, <i32 3, i32 3>
  %295 = sext <2 x i32> %294 to <2 x i64>
  %296 = extractelement <2 x i64> %295, i64 1
  %297 = getelementptr float, float* %44, i64 %296
  %298 = load float, float* %297, align 4
  %299 = extractelement <2 x i64> %295, i64 0
  %300 = getelementptr float, float* %44, i64 %299
  %301 = load float, float* %300, align 4
  %302 = add <2 x i32> %294, <i32 1, i32 1>
  %303 = sext <2 x i32> %302 to <2 x i64>
  %304 = getelementptr float, <2 x float*> %111, <2 x i64> %303
  %305 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %304, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %306 = add <2 x i32> %294, <i32 2, i32 2>
  %307 = sext <2 x i32> %306 to <2 x i64>
  %308 = getelementptr float, <2 x float*> %111, <2 x i64> %307
  %309 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %308, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %310 = fadd reassoc ninf nsz float %301, %298
  %shift256 = shufflevector <2 x float> %305, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %311 = fadd reassoc ninf nsz <2 x float> %305, %shift256
  %312 = shufflevector <2 x float> %311, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift257 = shufflevector <2 x float> %309, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %313 = fadd reassoc ninf nsz <2 x float> %309, %shift257
  %314 = shufflevector <2 x float> %313, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %315 = insertelement <4 x float> poison, float %284, i64 0
  %shuffle246 = shufflevector <4 x float> %315, <4 x float> poison, <4 x i32> zeroinitializer
  %316 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %310, i64 0
  %317 = shufflevector <4 x float> %316, <4 x float> %312, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %318 = shufflevector <4 x float> %317, <4 x float> %314, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %319 = fmul reassoc ninf nsz <4 x float> %shuffle246, %318
  %320 = fadd reassoc ninf nsz <4 x float> %319, %282
  %321 = icmp ugt i32 %74, 6
  br i1 %321, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %322 = getelementptr float, float* %80, i64 7
  %323 = load float, float* %322, align 4
  %324 = add <2 x i32> %83, <i32 7, i32 -7>
  %325 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %324, i1 true)
  %326 = sub <2 x i32> %325, %91
  %327 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %326, <2 x i32> zeroinitializer)
  %328 = mul <2 x i32> %327, <i32 -2, i32 -2>
  %329 = add <2 x i32> %328, %325
  %330 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %329, <2 x i32> zeroinitializer)
  %331 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %330)
  %332 = add <2 x i32> %331, %98
  %333 = mul <2 x i32> %332, <i32 3, i32 3>
  %334 = sext <2 x i32> %333 to <2 x i64>
  %335 = extractelement <2 x i64> %334, i64 1
  %336 = getelementptr float, float* %44, i64 %335
  %337 = load float, float* %336, align 4
  %338 = extractelement <2 x i64> %334, i64 0
  %339 = getelementptr float, float* %44, i64 %338
  %340 = load float, float* %339, align 4
  %341 = add <2 x i32> %333, <i32 1, i32 1>
  %342 = sext <2 x i32> %341 to <2 x i64>
  %343 = getelementptr float, <2 x float*> %111, <2 x i64> %342
  %344 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %343, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %345 = add <2 x i32> %333, <i32 2, i32 2>
  %346 = sext <2 x i32> %345 to <2 x i64>
  %347 = getelementptr float, <2 x float*> %111, <2 x i64> %346
  %348 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %347, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %349 = fadd reassoc ninf nsz float %340, %337
  %shift258 = shufflevector <2 x float> %344, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %350 = fadd reassoc ninf nsz <2 x float> %344, %shift258
  %351 = shufflevector <2 x float> %350, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift259 = shufflevector <2 x float> %348, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %352 = fadd reassoc ninf nsz <2 x float> %348, %shift259
  %353 = shufflevector <2 x float> %352, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %354 = insertelement <4 x float> poison, float %323, i64 0
  %shuffle240 = shufflevector <4 x float> %354, <4 x float> poison, <4 x i32> zeroinitializer
  %355 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %349, i64 0
  %356 = shufflevector <4 x float> %355, <4 x float> %351, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %357 = shufflevector <4 x float> %356, <4 x float> %353, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %358 = fmul reassoc ninf nsz <4 x float> %shuffle240, %357
  %359 = fadd reassoc ninf nsz <4 x float> %358, %320
  %.not211 = icmp eq i32 %74, 7
  br i1 %.not211, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %360 = getelementptr float, float* %80, i64 8
  %361 = load float, float* %360, align 4
  %362 = add <2 x i32> %83, <i32 8, i32 -8>
  %363 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %362, i1 true)
  %364 = sub <2 x i32> %363, %91
  %365 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %364, <2 x i32> zeroinitializer)
  %366 = mul <2 x i32> %365, <i32 -2, i32 -2>
  %367 = add <2 x i32> %366, %363
  %368 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %367, <2 x i32> zeroinitializer)
  %369 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %368)
  %370 = add <2 x i32> %369, %98
  %371 = mul <2 x i32> %370, <i32 3, i32 3>
  %372 = sext <2 x i32> %371 to <2 x i64>
  %373 = extractelement <2 x i64> %372, i64 1
  %374 = getelementptr float, float* %44, i64 %373
  %375 = load float, float* %374, align 4
  %376 = extractelement <2 x i64> %372, i64 0
  %377 = getelementptr float, float* %44, i64 %376
  %378 = load float, float* %377, align 4
  %379 = add <2 x i32> %371, <i32 1, i32 1>
  %380 = sext <2 x i32> %379 to <2 x i64>
  %381 = getelementptr float, <2 x float*> %111, <2 x i64> %380
  %382 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %381, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %383 = add <2 x i32> %371, <i32 2, i32 2>
  %384 = sext <2 x i32> %383 to <2 x i64>
  %385 = getelementptr float, <2 x float*> %111, <2 x i64> %384
  %386 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %385, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %387 = fadd reassoc ninf nsz float %378, %375
  %shift260 = shufflevector <2 x float> %382, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %388 = fadd reassoc ninf nsz <2 x float> %382, %shift260
  %389 = shufflevector <2 x float> %388, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift261 = shufflevector <2 x float> %386, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %390 = fadd reassoc ninf nsz <2 x float> %386, %shift261
  %391 = shufflevector <2 x float> %390, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %392 = insertelement <4 x float> poison, float %361, i64 0
  %shuffle239 = shufflevector <4 x float> %392, <4 x float> poison, <4 x i32> zeroinitializer
  %393 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %387, i64 0
  %394 = shufflevector <4 x float> %393, <4 x float> %389, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %395 = shufflevector <4 x float> %394, <4 x float> %391, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %396 = fmul reassoc ninf nsz <4 x float> %shuffle239, %395
  %397 = fadd reassoc ninf nsz <4 x float> %396, %359
  %398 = icmp ugt i32 %74, 8
  br i1 %398, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %399 = getelementptr float, float* %80, i64 9
  %400 = load float, float* %399, align 4
  %401 = add <2 x i32> %83, <i32 9, i32 -9>
  %402 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %401, i1 true)
  %403 = sub <2 x i32> %402, %91
  %404 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %403, <2 x i32> zeroinitializer)
  %405 = mul <2 x i32> %404, <i32 -2, i32 -2>
  %406 = add <2 x i32> %405, %402
  %407 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %406, <2 x i32> zeroinitializer)
  %408 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %407)
  %409 = add <2 x i32> %408, %98
  %410 = mul <2 x i32> %409, <i32 3, i32 3>
  %411 = sext <2 x i32> %410 to <2 x i64>
  %412 = extractelement <2 x i64> %411, i64 1
  %413 = getelementptr float, float* %44, i64 %412
  %414 = load float, float* %413, align 4
  %415 = extractelement <2 x i64> %411, i64 0
  %416 = getelementptr float, float* %44, i64 %415
  %417 = load float, float* %416, align 4
  %418 = add <2 x i32> %410, <i32 1, i32 1>
  %419 = sext <2 x i32> %418 to <2 x i64>
  %420 = getelementptr float, <2 x float*> %111, <2 x i64> %419
  %421 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %420, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %422 = add <2 x i32> %410, <i32 2, i32 2>
  %423 = sext <2 x i32> %422 to <2 x i64>
  %424 = getelementptr float, <2 x float*> %111, <2 x i64> %423
  %425 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %424, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %426 = fadd reassoc ninf nsz float %417, %414
  %shift262 = shufflevector <2 x float> %421, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %427 = fadd reassoc ninf nsz <2 x float> %421, %shift262
  %428 = shufflevector <2 x float> %427, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift263 = shufflevector <2 x float> %425, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %429 = fadd reassoc ninf nsz <2 x float> %425, %shift263
  %430 = shufflevector <2 x float> %429, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %431 = insertelement <4 x float> poison, float %400, i64 0
  %shuffle238 = shufflevector <4 x float> %431, <4 x float> poison, <4 x i32> zeroinitializer
  %432 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %426, i64 0
  %433 = shufflevector <4 x float> %432, <4 x float> %428, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %434 = shufflevector <4 x float> %433, <4 x float> %430, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %435 = fmul reassoc ninf nsz <4 x float> %shuffle238, %434
  %436 = fadd reassoc ninf nsz <4 x float> %435, %397
  %.not212 = icmp eq i32 %74, 9
  br i1 %.not212, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %437 = getelementptr float, float* %80, i64 10
  %438 = load float, float* %437, align 4
  %439 = add <2 x i32> %83, <i32 10, i32 -10>
  %440 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %439, i1 true)
  %441 = sub <2 x i32> %440, %91
  %442 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %441, <2 x i32> zeroinitializer)
  %443 = mul <2 x i32> %442, <i32 -2, i32 -2>
  %444 = add <2 x i32> %443, %440
  %445 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %444, <2 x i32> zeroinitializer)
  %446 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %445)
  %447 = add <2 x i32> %446, %98
  %448 = mul <2 x i32> %447, <i32 3, i32 3>
  %449 = sext <2 x i32> %448 to <2 x i64>
  %450 = extractelement <2 x i64> %449, i64 1
  %451 = getelementptr float, float* %44, i64 %450
  %452 = load float, float* %451, align 4
  %453 = extractelement <2 x i64> %449, i64 0
  %454 = getelementptr float, float* %44, i64 %453
  %455 = load float, float* %454, align 4
  %456 = add <2 x i32> %448, <i32 1, i32 1>
  %457 = sext <2 x i32> %456 to <2 x i64>
  %458 = getelementptr float, <2 x float*> %111, <2 x i64> %457
  %459 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %458, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %460 = add <2 x i32> %448, <i32 2, i32 2>
  %461 = sext <2 x i32> %460 to <2 x i64>
  %462 = getelementptr float, <2 x float*> %111, <2 x i64> %461
  %463 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %462, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %464 = fadd reassoc ninf nsz float %455, %452
  %shift264 = shufflevector <2 x float> %459, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %465 = fadd reassoc ninf nsz <2 x float> %459, %shift264
  %466 = shufflevector <2 x float> %465, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift265 = shufflevector <2 x float> %463, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %467 = fadd reassoc ninf nsz <2 x float> %463, %shift265
  %468 = shufflevector <2 x float> %467, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %469 = insertelement <4 x float> poison, float %438, i64 0
  %shuffle237 = shufflevector <4 x float> %469, <4 x float> poison, <4 x i32> zeroinitializer
  %470 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %464, i64 0
  %471 = shufflevector <4 x float> %470, <4 x float> %466, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %472 = shufflevector <4 x float> %471, <4 x float> %468, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %473 = fmul reassoc ninf nsz <4 x float> %shuffle237, %472
  %474 = fadd reassoc ninf nsz <4 x float> %473, %436
  %475 = icmp ugt i32 %74, 10
  br i1 %475, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %476 = getelementptr float, float* %80, i64 11
  %477 = load float, float* %476, align 4
  %478 = add <2 x i32> %83, <i32 11, i32 -11>
  %479 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %478, i1 true)
  %480 = sub <2 x i32> %479, %91
  %481 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %480, <2 x i32> zeroinitializer)
  %482 = mul <2 x i32> %481, <i32 -2, i32 -2>
  %483 = add <2 x i32> %482, %479
  %484 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %483, <2 x i32> zeroinitializer)
  %485 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %484)
  %486 = add <2 x i32> %485, %98
  %487 = mul <2 x i32> %486, <i32 3, i32 3>
  %488 = sext <2 x i32> %487 to <2 x i64>
  %489 = extractelement <2 x i64> %488, i64 1
  %490 = getelementptr float, float* %44, i64 %489
  %491 = load float, float* %490, align 4
  %492 = extractelement <2 x i64> %488, i64 0
  %493 = getelementptr float, float* %44, i64 %492
  %494 = load float, float* %493, align 4
  %495 = add <2 x i32> %487, <i32 1, i32 1>
  %496 = sext <2 x i32> %495 to <2 x i64>
  %497 = getelementptr float, <2 x float*> %111, <2 x i64> %496
  %498 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %497, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %499 = add <2 x i32> %487, <i32 2, i32 2>
  %500 = sext <2 x i32> %499 to <2 x i64>
  %501 = getelementptr float, <2 x float*> %111, <2 x i64> %500
  %502 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %501, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %503 = fadd reassoc ninf nsz float %494, %491
  %shift266 = shufflevector <2 x float> %498, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %504 = fadd reassoc ninf nsz <2 x float> %498, %shift266
  %505 = shufflevector <2 x float> %504, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift267 = shufflevector <2 x float> %502, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %506 = fadd reassoc ninf nsz <2 x float> %502, %shift267
  %507 = shufflevector <2 x float> %506, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %508 = insertelement <4 x float> poison, float %477, i64 0
  %shuffle236 = shufflevector <4 x float> %508, <4 x float> poison, <4 x i32> zeroinitializer
  %509 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %503, i64 0
  %510 = shufflevector <4 x float> %509, <4 x float> %505, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %511 = shufflevector <4 x float> %510, <4 x float> %507, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %512 = fmul reassoc ninf nsz <4 x float> %shuffle236, %511
  %513 = fadd reassoc ninf nsz <4 x float> %512, %474
  %.not213 = icmp eq i32 %74, 11
  br i1 %.not213, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %514 = getelementptr float, float* %80, i64 12
  %515 = load float, float* %514, align 4
  %516 = add <2 x i32> %83, <i32 12, i32 -12>
  %517 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %516, i1 true)
  %518 = sub <2 x i32> %517, %91
  %519 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %518, <2 x i32> zeroinitializer)
  %520 = mul <2 x i32> %519, <i32 -2, i32 -2>
  %521 = add <2 x i32> %520, %517
  %522 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %521, <2 x i32> zeroinitializer)
  %523 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %522)
  %524 = add <2 x i32> %523, %98
  %525 = mul <2 x i32> %524, <i32 3, i32 3>
  %526 = sext <2 x i32> %525 to <2 x i64>
  %527 = extractelement <2 x i64> %526, i64 1
  %528 = getelementptr float, float* %44, i64 %527
  %529 = load float, float* %528, align 4
  %530 = extractelement <2 x i64> %526, i64 0
  %531 = getelementptr float, float* %44, i64 %530
  %532 = load float, float* %531, align 4
  %533 = add <2 x i32> %525, <i32 1, i32 1>
  %534 = sext <2 x i32> %533 to <2 x i64>
  %535 = getelementptr float, <2 x float*> %111, <2 x i64> %534
  %536 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %535, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %537 = add <2 x i32> %525, <i32 2, i32 2>
  %538 = sext <2 x i32> %537 to <2 x i64>
  %539 = getelementptr float, <2 x float*> %111, <2 x i64> %538
  %540 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %539, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %541 = fadd reassoc ninf nsz float %532, %529
  %shift268 = shufflevector <2 x float> %536, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %542 = fadd reassoc ninf nsz <2 x float> %536, %shift268
  %543 = shufflevector <2 x float> %542, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift269 = shufflevector <2 x float> %540, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %544 = fadd reassoc ninf nsz <2 x float> %540, %shift269
  %545 = shufflevector <2 x float> %544, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %546 = insertelement <4 x float> poison, float %515, i64 0
  %shuffle235 = shufflevector <4 x float> %546, <4 x float> poison, <4 x i32> zeroinitializer
  %547 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %541, i64 0
  %548 = shufflevector <4 x float> %547, <4 x float> %543, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %549 = shufflevector <4 x float> %548, <4 x float> %545, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %550 = fmul reassoc ninf nsz <4 x float> %shuffle235, %549
  %551 = fadd reassoc ninf nsz <4 x float> %550, %513
  %552 = icmp ugt i32 %74, 12
  br i1 %552, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %553 = getelementptr float, float* %80, i64 13
  %554 = load float, float* %553, align 4
  %555 = add <2 x i32> %83, <i32 13, i32 -13>
  %556 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %555, i1 true)
  %557 = sub <2 x i32> %556, %91
  %558 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %557, <2 x i32> zeroinitializer)
  %559 = mul <2 x i32> %558, <i32 -2, i32 -2>
  %560 = add <2 x i32> %559, %556
  %561 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %560, <2 x i32> zeroinitializer)
  %562 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %561)
  %563 = add <2 x i32> %562, %98
  %564 = mul <2 x i32> %563, <i32 3, i32 3>
  %565 = sext <2 x i32> %564 to <2 x i64>
  %566 = extractelement <2 x i64> %565, i64 1
  %567 = getelementptr float, float* %44, i64 %566
  %568 = load float, float* %567, align 4
  %569 = extractelement <2 x i64> %565, i64 0
  %570 = getelementptr float, float* %44, i64 %569
  %571 = load float, float* %570, align 4
  %572 = add <2 x i32> %564, <i32 1, i32 1>
  %573 = sext <2 x i32> %572 to <2 x i64>
  %574 = getelementptr float, <2 x float*> %111, <2 x i64> %573
  %575 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %574, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %576 = add <2 x i32> %564, <i32 2, i32 2>
  %577 = sext <2 x i32> %576 to <2 x i64>
  %578 = getelementptr float, <2 x float*> %111, <2 x i64> %577
  %579 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %578, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %580 = fadd reassoc ninf nsz float %571, %568
  %shift270 = shufflevector <2 x float> %575, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %581 = fadd reassoc ninf nsz <2 x float> %575, %shift270
  %582 = shufflevector <2 x float> %581, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift271 = shufflevector <2 x float> %579, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %583 = fadd reassoc ninf nsz <2 x float> %579, %shift271
  %584 = shufflevector <2 x float> %583, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %585 = insertelement <4 x float> poison, float %554, i64 0
  %shuffle234 = shufflevector <4 x float> %585, <4 x float> poison, <4 x i32> zeroinitializer
  %586 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %580, i64 0
  %587 = shufflevector <4 x float> %586, <4 x float> %582, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %588 = shufflevector <4 x float> %587, <4 x float> %584, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %589 = fmul reassoc ninf nsz <4 x float> %shuffle234, %588
  %590 = fadd reassoc ninf nsz <4 x float> %589, %551
  %.not214 = icmp eq i32 %74, 13
  br i1 %.not214, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %591 = getelementptr float, float* %80, i64 14
  %592 = load float, float* %591, align 4
  %593 = add <2 x i32> %83, <i32 14, i32 -14>
  %594 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %593, i1 true)
  %595 = sub <2 x i32> %594, %91
  %596 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %595, <2 x i32> zeroinitializer)
  %597 = mul <2 x i32> %596, <i32 -2, i32 -2>
  %598 = add <2 x i32> %597, %594
  %599 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %598, <2 x i32> zeroinitializer)
  %600 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %599)
  %601 = add <2 x i32> %600, %98
  %602 = mul <2 x i32> %601, <i32 3, i32 3>
  %603 = sext <2 x i32> %602 to <2 x i64>
  %604 = extractelement <2 x i64> %603, i64 1
  %605 = getelementptr float, float* %44, i64 %604
  %606 = load float, float* %605, align 4
  %607 = extractelement <2 x i64> %603, i64 0
  %608 = getelementptr float, float* %44, i64 %607
  %609 = load float, float* %608, align 4
  %610 = add <2 x i32> %602, <i32 1, i32 1>
  %611 = sext <2 x i32> %610 to <2 x i64>
  %612 = getelementptr float, <2 x float*> %111, <2 x i64> %611
  %613 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %612, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %614 = add <2 x i32> %602, <i32 2, i32 2>
  %615 = sext <2 x i32> %614 to <2 x i64>
  %616 = getelementptr float, <2 x float*> %111, <2 x i64> %615
  %617 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %616, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %618 = fadd reassoc ninf nsz float %609, %606
  %shift272 = shufflevector <2 x float> %613, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %619 = fadd reassoc ninf nsz <2 x float> %613, %shift272
  %620 = shufflevector <2 x float> %619, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift273 = shufflevector <2 x float> %617, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %621 = fadd reassoc ninf nsz <2 x float> %617, %shift273
  %622 = shufflevector <2 x float> %621, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %623 = insertelement <4 x float> poison, float %592, i64 0
  %shuffle233 = shufflevector <4 x float> %623, <4 x float> poison, <4 x i32> zeroinitializer
  %624 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %618, i64 0
  %625 = shufflevector <4 x float> %624, <4 x float> %620, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %626 = shufflevector <4 x float> %625, <4 x float> %622, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %627 = fmul reassoc ninf nsz <4 x float> %shuffle233, %626
  %628 = fadd reassoc ninf nsz <4 x float> %627, %590
  %629 = icmp ugt i32 %74, 14
  br i1 %629, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %630 = getelementptr float, float* %80, i64 15
  %631 = load float, float* %630, align 4
  %632 = add <2 x i32> %83, <i32 15, i32 -15>
  %633 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %632, i1 true)
  %634 = sub <2 x i32> %633, %91
  %635 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %634, <2 x i32> zeroinitializer)
  %636 = mul <2 x i32> %635, <i32 -2, i32 -2>
  %637 = add <2 x i32> %636, %633
  %638 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %637, <2 x i32> zeroinitializer)
  %639 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %638)
  %640 = add <2 x i32> %639, %98
  %641 = mul <2 x i32> %640, <i32 3, i32 3>
  %642 = sext <2 x i32> %641 to <2 x i64>
  %643 = extractelement <2 x i64> %642, i64 1
  %644 = getelementptr float, float* %44, i64 %643
  %645 = load float, float* %644, align 4
  %646 = extractelement <2 x i64> %642, i64 0
  %647 = getelementptr float, float* %44, i64 %646
  %648 = load float, float* %647, align 4
  %649 = add <2 x i32> %641, <i32 1, i32 1>
  %650 = sext <2 x i32> %649 to <2 x i64>
  %651 = getelementptr float, <2 x float*> %111, <2 x i64> %650
  %652 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %651, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %653 = add <2 x i32> %641, <i32 2, i32 2>
  %654 = sext <2 x i32> %653 to <2 x i64>
  %655 = getelementptr float, <2 x float*> %111, <2 x i64> %654
  %656 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %655, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %657 = fadd reassoc ninf nsz float %648, %645
  %shift274 = shufflevector <2 x float> %652, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %658 = fadd reassoc ninf nsz <2 x float> %652, %shift274
  %659 = shufflevector <2 x float> %658, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift275 = shufflevector <2 x float> %656, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %660 = fadd reassoc ninf nsz <2 x float> %656, %shift275
  %661 = shufflevector <2 x float> %660, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %662 = insertelement <4 x float> poison, float %631, i64 0
  %shuffle232 = shufflevector <4 x float> %662, <4 x float> poison, <4 x i32> zeroinitializer
  %663 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %657, i64 0
  %664 = shufflevector <4 x float> %663, <4 x float> %659, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %665 = shufflevector <4 x float> %664, <4 x float> %661, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %666 = fmul reassoc ninf nsz <4 x float> %shuffle232, %665
  %667 = fadd reassoc ninf nsz <4 x float> %666, %628
  %.not215 = icmp eq i32 %74, 15
  br i1 %.not215, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %668 = getelementptr float, float* %80, i64 16
  %669 = load float, float* %668, align 4
  %670 = add <2 x i32> %83, <i32 16, i32 -16>
  %671 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %670, i1 true)
  %672 = sub <2 x i32> %671, %91
  %673 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %672, <2 x i32> zeroinitializer)
  %674 = mul <2 x i32> %673, <i32 -2, i32 -2>
  %675 = add <2 x i32> %674, %671
  %676 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %675, <2 x i32> zeroinitializer)
  %677 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %676)
  %678 = add <2 x i32> %677, %98
  %679 = mul <2 x i32> %678, <i32 3, i32 3>
  %680 = sext <2 x i32> %679 to <2 x i64>
  %681 = extractelement <2 x i64> %680, i64 1
  %682 = getelementptr float, float* %44, i64 %681
  %683 = load float, float* %682, align 4
  %684 = extractelement <2 x i64> %680, i64 0
  %685 = getelementptr float, float* %44, i64 %684
  %686 = load float, float* %685, align 4
  %687 = add <2 x i32> %679, <i32 1, i32 1>
  %688 = sext <2 x i32> %687 to <2 x i64>
  %689 = getelementptr float, <2 x float*> %111, <2 x i64> %688
  %690 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %689, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %691 = add <2 x i32> %679, <i32 2, i32 2>
  %692 = sext <2 x i32> %691 to <2 x i64>
  %693 = getelementptr float, <2 x float*> %111, <2 x i64> %692
  %694 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %693, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %695 = fadd reassoc ninf nsz float %686, %683
  %shift276 = shufflevector <2 x float> %690, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %696 = fadd reassoc ninf nsz <2 x float> %690, %shift276
  %697 = shufflevector <2 x float> %696, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift277 = shufflevector <2 x float> %694, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %698 = fadd reassoc ninf nsz <2 x float> %694, %shift277
  %699 = shufflevector <2 x float> %698, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %700 = insertelement <4 x float> poison, float %669, i64 0
  %shuffle = shufflevector <4 x float> %700, <4 x float> poison, <4 x i32> zeroinitializer
  %701 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %695, i64 0
  %702 = shufflevector <4 x float> %701, <4 x float> %697, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %703 = shufflevector <4 x float> %702, <4 x float> %699, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %704 = fmul reassoc ninf nsz <4 x float> %shuffle, %703
  %705 = fadd reassoc ninf nsz <4 x float> %704, %667
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %706 = phi <4 x float> [ %705, %true_block43 ], [ %667, %after_if42 ], [ %628, %after_if39 ], [ %590, %after_if36 ], [ %551, %after_if33 ], [ %513, %after_if30 ], [ %474, %after_if27 ], [ %436, %after_if24 ], [ %397, %after_if21 ], [ %359, %after_if18 ], [ %320, %after_if15 ], [ %282, %after_if12 ], [ %243, %after_if9 ], [ %205, %after_if6 ], [ %166, %after_if3 ], [ %128, %after_if ], [ %79, %for_loop_body ]
  %707 = extractelement <4 x float> %706, i64 0
  %708 = extractelement <4 x float> %706, i64 3
  %709 = fdiv reassoc ninf nsz float %707, %708
  %710 = extractelement <4 x float> %706, i64 1
  %711 = fdiv reassoc ninf nsz float %710, %708
  %712 = extractelement <4 x float> %706, i64 2
  %713 = fdiv reassoc ninf nsz float %712, %708
  %714 = load float*, float** %27, align 8
  %715 = load i32, i32* %28, align 4
  %716 = mul i32 %715, %46
  %717 = add i32 %716, %54
  %718 = mul i32 %717, 3
  %719 = sext i32 %718 to i64
  %720 = getelementptr float, float* %714, i64 %719
  store float %709, float* %720, align 4
  %721 = load float*, float** %27, align 8
  %722 = load i32, i32* %28, align 4
  %723 = mul i32 %722, %46
  %724 = add i32 %723, %54
  %725 = mul i32 %724, 3
  %726 = add i32 %725, 1
  %727 = sext i32 %726 to i64
  %728 = getelementptr float, float* %721, i64 %727
  store float %711, float* %728, align 4
  %729 = load float*, float** %27, align 8
  %730 = load i32, i32* %28, align 4
  %731 = mul i32 %730, %46
  %732 = add i32 %731, %54
  %733 = mul i32 %732, 3
  %734 = add i32 %733, 2
  %735 = sext i32 %734 to i64
  %736 = getelementptr float, float* %729, i64 %735
  store float %713, float* %736, align 4
  %737 = add nsw i32 %.0115231, 1
  %exitcond.not = icmp eq i32 %19, %737
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.abs.v2i32(<2 x i32>, i1 immarg) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

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
