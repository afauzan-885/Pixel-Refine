; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { i8*, %struct.LLVMRuntime.5*, i32, i64* }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.2*], [1024 x %struct.NodeManager.3*], [1024 x i8*], i8*, %struct.RandState.4*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { i8*, i8*, i64 }
%struct.ListManager.2 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.5* }
%struct.NodeManager.3 = type { %struct.LLVMRuntime.5*, i32, i32, i32, i32, %struct.ListManager.2*, %struct.ListManager.2*, %struct.ListManager.2*, i32 }
%struct.RandState.4 = type { i32, i32, i32, i32, i32 }
%struct.range_task_helper_context = type { %struct.RuntimeContext.6*, void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*)*, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_gaussian_blur_x_3ch_f32_kernel_c182_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 3
  %5 = load i32, i32* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 12
  %11 = bitcast i8* %10 to i32*
  store i32 %5, i32* %11, align 4
  %12 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %13 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %12, i64 0, i32 5
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %21 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %22 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  store i32 %21, i32* %26, align 4
  %27 = mul i32 %21, %20
  %28 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %28, i64 0, i32 14
  %30 = bitcast i8** %29 to i32**
  %31 = load i32*, i32** %30, align 8
  store i32 %27, i32* %31, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_x_3ch_f32_kernel_c182_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast %struct.range_task_helper_context* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 0
  store %struct.RuntimeContext.6* %context, %struct.RuntimeContext.6** %4, align 8
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.6*, i8*, i32)* @function_body, void (%struct.RuntimeContext.6*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %23 = load float*, float** %22, align 8
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.091177 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %456, %after_if45 ]
  %31 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %31, i64 0, i32 14
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
  %46 = load float*, float** %25, align 8
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
  %63 = getelementptr float, float* %46, i64 %62
  %64 = load float, float* %63, align 4
  %65 = fmul reassoc ninf nsz float %64, %45
  %66 = getelementptr inbounds i8, i8* %33, i64 8
  %67 = bitcast i8* %66 to i32*
  %68 = load i32, i32* %67, align 4
  %69 = icmp sgt i32 %68, 0
  %70 = insertelement <2 x float> poison, float %65, i64 0
  %71 = insertelement <2 x float> %70, float %45, i64 1
  br i1 %69, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %72 = load float*, float** %22, align 8
  %73 = getelementptr float, float* %72, i64 1
  %74 = load float, float* %73, align 4
  %75 = shufflevector <2 x i32> %55, <2 x i32> poison, <2 x i32> zeroinitializer
  %76 = add <2 x i32> %75, <i32 1, i32 -1>
  %77 = getelementptr inbounds i8, i8* %33, i64 12
  %78 = bitcast i8* %77 to i32*
  %79 = load i32, i32* %78, align 4
  %80 = add i32 %79, -1
  %81 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %76, i1 true)
  %82 = insertelement <2 x i32> poison, i32 %80, i64 0
  %83 = shufflevector <2 x i32> %82, <2 x i32> poison, <2 x i32> zeroinitializer
  %84 = sub <2 x i32> %81, %83
  %85 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %84, <2 x i32> zeroinitializer)
  %86 = mul <2 x i32> %85, <i32 -2, i32 -2>
  %87 = add <2 x i32> %86, %81
  %88 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %87, <2 x i32> zeroinitializer)
  %89 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %88)
  %90 = shufflevector <2 x i32> %56, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %91 = add <2 x i32> %89, %90
  %92 = insertelement <2 x i32> poison, i32 %48, i64 0
  %93 = shufflevector <2 x i32> %92, <2 x i32> poison, <2 x i32> zeroinitializer
  %94 = mul <2 x i32> %91, %93
  %95 = add <2 x i32> %94, <i32 2, i32 2>
  %96 = sext <2 x i32> %95 to <2 x i64>
  %97 = insertelement <2 x float*> poison, float* %46, i64 0
  %98 = shufflevector <2 x float*> %97, <2 x float*> poison, <2 x i32> zeroinitializer
  %99 = getelementptr float, <2 x float*> %98, <2 x i64> %96
  %100 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %99, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift = shufflevector <2 x float> %100, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %101 = fadd reassoc ninf nsz <2 x float> %100, %shift
  %102 = insertelement <2 x float> %101, float 2.000000e+00, i64 1
  %103 = insertelement <2 x float> poison, float %74, i64 0
  %104 = shufflevector <2 x float> %103, <2 x float> poison, <2 x i32> zeroinitializer
  %105 = fmul reassoc ninf nsz <2 x float> %102, %104
  %106 = fadd reassoc ninf nsz <2 x float> %105, %71
  %.not = icmp eq i32 %68, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %107 = getelementptr float, float* %72, i64 2
  %108 = load float, float* %107, align 4
  %109 = add <2 x i32> %75, <i32 2, i32 -2>
  %110 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %109, i1 true)
  %111 = sub <2 x i32> %110, %83
  %112 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %111, <2 x i32> zeroinitializer)
  %113 = mul <2 x i32> %112, <i32 -2, i32 -2>
  %114 = add <2 x i32> %113, %110
  %115 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %114, <2 x i32> zeroinitializer)
  %116 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %115)
  %117 = add <2 x i32> %116, %90
  %118 = mul <2 x i32> %117, %93
  %119 = add <2 x i32> %118, <i32 2, i32 2>
  %120 = sext <2 x i32> %119 to <2 x i64>
  %121 = getelementptr float, <2 x float*> %98, <2 x i64> %120
  %122 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %121, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift178 = shufflevector <2 x float> %122, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %123 = fadd reassoc ninf nsz <2 x float> %122, %shift178
  %124 = insertelement <2 x float> %123, float 2.000000e+00, i64 1
  %125 = insertelement <2 x float> poison, float %108, i64 0
  %126 = shufflevector <2 x float> %125, <2 x float> poison, <2 x i32> zeroinitializer
  %127 = fmul reassoc ninf nsz <2 x float> %124, %126
  %128 = fadd reassoc ninf nsz <2 x float> %127, %106
  %129 = icmp ugt i32 %68, 2
  br i1 %129, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %130 = getelementptr float, float* %72, i64 3
  %131 = load float, float* %130, align 4
  %132 = add <2 x i32> %75, <i32 3, i32 -3>
  %133 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %132, i1 true)
  %134 = sub <2 x i32> %133, %83
  %135 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %134, <2 x i32> zeroinitializer)
  %136 = mul <2 x i32> %135, <i32 -2, i32 -2>
  %137 = add <2 x i32> %136, %133
  %138 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %137, <2 x i32> zeroinitializer)
  %139 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %138)
  %140 = add <2 x i32> %139, %90
  %141 = mul <2 x i32> %140, %93
  %142 = add <2 x i32> %141, <i32 2, i32 2>
  %143 = sext <2 x i32> %142 to <2 x i64>
  %144 = getelementptr float, <2 x float*> %98, <2 x i64> %143
  %145 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %144, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift179 = shufflevector <2 x float> %145, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %146 = fadd reassoc ninf nsz <2 x float> %145, %shift179
  %147 = insertelement <2 x float> %146, float 2.000000e+00, i64 1
  %148 = insertelement <2 x float> poison, float %131, i64 0
  %149 = shufflevector <2 x float> %148, <2 x float> poison, <2 x i32> zeroinitializer
  %150 = fmul reassoc ninf nsz <2 x float> %147, %149
  %151 = fadd reassoc ninf nsz <2 x float> %150, %128
  %.not155 = icmp eq i32 %68, 3
  br i1 %.not155, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %152 = getelementptr float, float* %72, i64 4
  %153 = load float, float* %152, align 4
  %154 = add <2 x i32> %75, <i32 4, i32 -4>
  %155 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %154, i1 true)
  %156 = sub <2 x i32> %155, %83
  %157 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %156, <2 x i32> zeroinitializer)
  %158 = mul <2 x i32> %157, <i32 -2, i32 -2>
  %159 = add <2 x i32> %158, %155
  %160 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %159, <2 x i32> zeroinitializer)
  %161 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %160)
  %162 = add <2 x i32> %161, %90
  %163 = mul <2 x i32> %162, %93
  %164 = add <2 x i32> %163, <i32 2, i32 2>
  %165 = sext <2 x i32> %164 to <2 x i64>
  %166 = getelementptr float, <2 x float*> %98, <2 x i64> %165
  %167 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %166, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift180 = shufflevector <2 x float> %167, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %168 = fadd reassoc ninf nsz <2 x float> %167, %shift180
  %169 = insertelement <2 x float> %168, float 2.000000e+00, i64 1
  %170 = insertelement <2 x float> poison, float %153, i64 0
  %171 = shufflevector <2 x float> %170, <2 x float> poison, <2 x i32> zeroinitializer
  %172 = fmul reassoc ninf nsz <2 x float> %169, %171
  %173 = fadd reassoc ninf nsz <2 x float> %172, %151
  %174 = icmp ugt i32 %68, 4
  br i1 %174, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %175 = getelementptr float, float* %72, i64 5
  %176 = load float, float* %175, align 4
  %177 = add <2 x i32> %75, <i32 5, i32 -5>
  %178 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %177, i1 true)
  %179 = sub <2 x i32> %178, %83
  %180 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %179, <2 x i32> zeroinitializer)
  %181 = mul <2 x i32> %180, <i32 -2, i32 -2>
  %182 = add <2 x i32> %181, %178
  %183 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %182, <2 x i32> zeroinitializer)
  %184 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %183)
  %185 = add <2 x i32> %184, %90
  %186 = mul <2 x i32> %185, %93
  %187 = add <2 x i32> %186, <i32 2, i32 2>
  %188 = sext <2 x i32> %187 to <2 x i64>
  %189 = getelementptr float, <2 x float*> %98, <2 x i64> %188
  %190 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %189, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift181 = shufflevector <2 x float> %190, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %191 = fadd reassoc ninf nsz <2 x float> %190, %shift181
  %192 = insertelement <2 x float> %191, float 2.000000e+00, i64 1
  %193 = insertelement <2 x float> poison, float %176, i64 0
  %194 = shufflevector <2 x float> %193, <2 x float> poison, <2 x i32> zeroinitializer
  %195 = fmul reassoc ninf nsz <2 x float> %192, %194
  %196 = fadd reassoc ninf nsz <2 x float> %195, %173
  %.not156 = icmp eq i32 %68, 5
  br i1 %.not156, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %197 = getelementptr float, float* %72, i64 6
  %198 = load float, float* %197, align 4
  %199 = add <2 x i32> %75, <i32 6, i32 -6>
  %200 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %199, i1 true)
  %201 = sub <2 x i32> %200, %83
  %202 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %201, <2 x i32> zeroinitializer)
  %203 = mul <2 x i32> %202, <i32 -2, i32 -2>
  %204 = add <2 x i32> %203, %200
  %205 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %204, <2 x i32> zeroinitializer)
  %206 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %205)
  %207 = add <2 x i32> %206, %90
  %208 = mul <2 x i32> %207, %93
  %209 = add <2 x i32> %208, <i32 2, i32 2>
  %210 = sext <2 x i32> %209 to <2 x i64>
  %211 = getelementptr float, <2 x float*> %98, <2 x i64> %210
  %212 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %211, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift182 = shufflevector <2 x float> %212, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %213 = fadd reassoc ninf nsz <2 x float> %212, %shift182
  %214 = insertelement <2 x float> %213, float 2.000000e+00, i64 1
  %215 = insertelement <2 x float> poison, float %198, i64 0
  %216 = shufflevector <2 x float> %215, <2 x float> poison, <2 x i32> zeroinitializer
  %217 = fmul reassoc ninf nsz <2 x float> %214, %216
  %218 = fadd reassoc ninf nsz <2 x float> %217, %196
  %219 = icmp ugt i32 %68, 6
  br i1 %219, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %220 = getelementptr float, float* %72, i64 7
  %221 = load float, float* %220, align 4
  %222 = add <2 x i32> %75, <i32 7, i32 -7>
  %223 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %222, i1 true)
  %224 = sub <2 x i32> %223, %83
  %225 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %224, <2 x i32> zeroinitializer)
  %226 = mul <2 x i32> %225, <i32 -2, i32 -2>
  %227 = add <2 x i32> %226, %223
  %228 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %227, <2 x i32> zeroinitializer)
  %229 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %228)
  %230 = add <2 x i32> %229, %90
  %231 = mul <2 x i32> %230, %93
  %232 = add <2 x i32> %231, <i32 2, i32 2>
  %233 = sext <2 x i32> %232 to <2 x i64>
  %234 = getelementptr float, <2 x float*> %98, <2 x i64> %233
  %235 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %234, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift183 = shufflevector <2 x float> %235, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %236 = fadd reassoc ninf nsz <2 x float> %235, %shift183
  %237 = insertelement <2 x float> %236, float 2.000000e+00, i64 1
  %238 = insertelement <2 x float> poison, float %221, i64 0
  %239 = shufflevector <2 x float> %238, <2 x float> poison, <2 x i32> zeroinitializer
  %240 = fmul reassoc ninf nsz <2 x float> %237, %239
  %241 = fadd reassoc ninf nsz <2 x float> %240, %218
  %.not157 = icmp eq i32 %68, 7
  br i1 %.not157, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %242 = getelementptr float, float* %72, i64 8
  %243 = load float, float* %242, align 4
  %244 = add <2 x i32> %75, <i32 8, i32 -8>
  %245 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %244, i1 true)
  %246 = sub <2 x i32> %245, %83
  %247 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %246, <2 x i32> zeroinitializer)
  %248 = mul <2 x i32> %247, <i32 -2, i32 -2>
  %249 = add <2 x i32> %248, %245
  %250 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %249, <2 x i32> zeroinitializer)
  %251 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %250)
  %252 = add <2 x i32> %251, %90
  %253 = mul <2 x i32> %252, %93
  %254 = add <2 x i32> %253, <i32 2, i32 2>
  %255 = sext <2 x i32> %254 to <2 x i64>
  %256 = getelementptr float, <2 x float*> %98, <2 x i64> %255
  %257 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %256, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift184 = shufflevector <2 x float> %257, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %258 = fadd reassoc ninf nsz <2 x float> %257, %shift184
  %259 = insertelement <2 x float> %258, float 2.000000e+00, i64 1
  %260 = insertelement <2 x float> poison, float %243, i64 0
  %261 = shufflevector <2 x float> %260, <2 x float> poison, <2 x i32> zeroinitializer
  %262 = fmul reassoc ninf nsz <2 x float> %259, %261
  %263 = fadd reassoc ninf nsz <2 x float> %262, %241
  %264 = icmp ugt i32 %68, 8
  br i1 %264, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %265 = getelementptr float, float* %72, i64 9
  %266 = load float, float* %265, align 4
  %267 = add <2 x i32> %75, <i32 9, i32 -9>
  %268 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %267, i1 true)
  %269 = sub <2 x i32> %268, %83
  %270 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %269, <2 x i32> zeroinitializer)
  %271 = mul <2 x i32> %270, <i32 -2, i32 -2>
  %272 = add <2 x i32> %271, %268
  %273 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %272, <2 x i32> zeroinitializer)
  %274 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %273)
  %275 = add <2 x i32> %274, %90
  %276 = mul <2 x i32> %275, %93
  %277 = add <2 x i32> %276, <i32 2, i32 2>
  %278 = sext <2 x i32> %277 to <2 x i64>
  %279 = getelementptr float, <2 x float*> %98, <2 x i64> %278
  %280 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %279, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift185 = shufflevector <2 x float> %280, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %281 = fadd reassoc ninf nsz <2 x float> %280, %shift185
  %282 = insertelement <2 x float> %281, float 2.000000e+00, i64 1
  %283 = insertelement <2 x float> poison, float %266, i64 0
  %284 = shufflevector <2 x float> %283, <2 x float> poison, <2 x i32> zeroinitializer
  %285 = fmul reassoc ninf nsz <2 x float> %282, %284
  %286 = fadd reassoc ninf nsz <2 x float> %285, %263
  %.not158 = icmp eq i32 %68, 9
  br i1 %.not158, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %287 = getelementptr float, float* %72, i64 10
  %288 = load float, float* %287, align 4
  %289 = add <2 x i32> %75, <i32 10, i32 -10>
  %290 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %289, i1 true)
  %291 = sub <2 x i32> %290, %83
  %292 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %291, <2 x i32> zeroinitializer)
  %293 = mul <2 x i32> %292, <i32 -2, i32 -2>
  %294 = add <2 x i32> %293, %290
  %295 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %294, <2 x i32> zeroinitializer)
  %296 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %295)
  %297 = add <2 x i32> %296, %90
  %298 = mul <2 x i32> %297, %93
  %299 = add <2 x i32> %298, <i32 2, i32 2>
  %300 = sext <2 x i32> %299 to <2 x i64>
  %301 = getelementptr float, <2 x float*> %98, <2 x i64> %300
  %302 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %301, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift186 = shufflevector <2 x float> %302, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %303 = fadd reassoc ninf nsz <2 x float> %302, %shift186
  %304 = insertelement <2 x float> %303, float 2.000000e+00, i64 1
  %305 = insertelement <2 x float> poison, float %288, i64 0
  %306 = shufflevector <2 x float> %305, <2 x float> poison, <2 x i32> zeroinitializer
  %307 = fmul reassoc ninf nsz <2 x float> %304, %306
  %308 = fadd reassoc ninf nsz <2 x float> %307, %286
  %309 = icmp ugt i32 %68, 10
  br i1 %309, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %310 = getelementptr float, float* %72, i64 11
  %311 = load float, float* %310, align 4
  %312 = add <2 x i32> %75, <i32 11, i32 -11>
  %313 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %312, i1 true)
  %314 = sub <2 x i32> %313, %83
  %315 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %314, <2 x i32> zeroinitializer)
  %316 = mul <2 x i32> %315, <i32 -2, i32 -2>
  %317 = add <2 x i32> %316, %313
  %318 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %317, <2 x i32> zeroinitializer)
  %319 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %318)
  %320 = add <2 x i32> %319, %90
  %321 = mul <2 x i32> %320, %93
  %322 = add <2 x i32> %321, <i32 2, i32 2>
  %323 = sext <2 x i32> %322 to <2 x i64>
  %324 = getelementptr float, <2 x float*> %98, <2 x i64> %323
  %325 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %324, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift187 = shufflevector <2 x float> %325, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %326 = fadd reassoc ninf nsz <2 x float> %325, %shift187
  %327 = insertelement <2 x float> %326, float 2.000000e+00, i64 1
  %328 = insertelement <2 x float> poison, float %311, i64 0
  %329 = shufflevector <2 x float> %328, <2 x float> poison, <2 x i32> zeroinitializer
  %330 = fmul reassoc ninf nsz <2 x float> %327, %329
  %331 = fadd reassoc ninf nsz <2 x float> %330, %308
  %.not159 = icmp eq i32 %68, 11
  br i1 %.not159, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %332 = getelementptr float, float* %72, i64 12
  %333 = load float, float* %332, align 4
  %334 = add <2 x i32> %75, <i32 12, i32 -12>
  %335 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %334, i1 true)
  %336 = sub <2 x i32> %335, %83
  %337 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %336, <2 x i32> zeroinitializer)
  %338 = mul <2 x i32> %337, <i32 -2, i32 -2>
  %339 = add <2 x i32> %338, %335
  %340 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %339, <2 x i32> zeroinitializer)
  %341 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %340)
  %342 = add <2 x i32> %341, %90
  %343 = mul <2 x i32> %342, %93
  %344 = add <2 x i32> %343, <i32 2, i32 2>
  %345 = sext <2 x i32> %344 to <2 x i64>
  %346 = getelementptr float, <2 x float*> %98, <2 x i64> %345
  %347 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %346, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift188 = shufflevector <2 x float> %347, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %348 = fadd reassoc ninf nsz <2 x float> %347, %shift188
  %349 = insertelement <2 x float> %348, float 2.000000e+00, i64 1
  %350 = insertelement <2 x float> poison, float %333, i64 0
  %351 = shufflevector <2 x float> %350, <2 x float> poison, <2 x i32> zeroinitializer
  %352 = fmul reassoc ninf nsz <2 x float> %349, %351
  %353 = fadd reassoc ninf nsz <2 x float> %352, %331
  %354 = icmp ugt i32 %68, 12
  br i1 %354, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %355 = getelementptr float, float* %72, i64 13
  %356 = load float, float* %355, align 4
  %357 = add <2 x i32> %75, <i32 13, i32 -13>
  %358 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %357, i1 true)
  %359 = sub <2 x i32> %358, %83
  %360 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %359, <2 x i32> zeroinitializer)
  %361 = mul <2 x i32> %360, <i32 -2, i32 -2>
  %362 = add <2 x i32> %361, %358
  %363 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %362, <2 x i32> zeroinitializer)
  %364 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %363)
  %365 = add <2 x i32> %364, %90
  %366 = mul <2 x i32> %365, %93
  %367 = add <2 x i32> %366, <i32 2, i32 2>
  %368 = sext <2 x i32> %367 to <2 x i64>
  %369 = getelementptr float, <2 x float*> %98, <2 x i64> %368
  %370 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %369, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift189 = shufflevector <2 x float> %370, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %371 = fadd reassoc ninf nsz <2 x float> %370, %shift189
  %372 = insertelement <2 x float> %371, float 2.000000e+00, i64 1
  %373 = insertelement <2 x float> poison, float %356, i64 0
  %374 = shufflevector <2 x float> %373, <2 x float> poison, <2 x i32> zeroinitializer
  %375 = fmul reassoc ninf nsz <2 x float> %372, %374
  %376 = fadd reassoc ninf nsz <2 x float> %375, %353
  %.not160 = icmp eq i32 %68, 13
  br i1 %.not160, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %377 = getelementptr float, float* %72, i64 14
  %378 = load float, float* %377, align 4
  %379 = add <2 x i32> %75, <i32 14, i32 -14>
  %380 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %379, i1 true)
  %381 = sub <2 x i32> %380, %83
  %382 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %381, <2 x i32> zeroinitializer)
  %383 = mul <2 x i32> %382, <i32 -2, i32 -2>
  %384 = add <2 x i32> %383, %380
  %385 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %384, <2 x i32> zeroinitializer)
  %386 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %385)
  %387 = add <2 x i32> %386, %90
  %388 = mul <2 x i32> %387, %93
  %389 = add <2 x i32> %388, <i32 2, i32 2>
  %390 = sext <2 x i32> %389 to <2 x i64>
  %391 = getelementptr float, <2 x float*> %98, <2 x i64> %390
  %392 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %391, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift190 = shufflevector <2 x float> %392, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %393 = fadd reassoc ninf nsz <2 x float> %392, %shift190
  %394 = insertelement <2 x float> %393, float 2.000000e+00, i64 1
  %395 = insertelement <2 x float> poison, float %378, i64 0
  %396 = shufflevector <2 x float> %395, <2 x float> poison, <2 x i32> zeroinitializer
  %397 = fmul reassoc ninf nsz <2 x float> %394, %396
  %398 = fadd reassoc ninf nsz <2 x float> %397, %376
  %399 = icmp ugt i32 %68, 14
  br i1 %399, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %400 = getelementptr float, float* %72, i64 15
  %401 = load float, float* %400, align 4
  %402 = add <2 x i32> %75, <i32 15, i32 -15>
  %403 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %402, i1 true)
  %404 = sub <2 x i32> %403, %83
  %405 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %404, <2 x i32> zeroinitializer)
  %406 = mul <2 x i32> %405, <i32 -2, i32 -2>
  %407 = add <2 x i32> %406, %403
  %408 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %407, <2 x i32> zeroinitializer)
  %409 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %408)
  %410 = add <2 x i32> %409, %90
  %411 = mul <2 x i32> %410, %93
  %412 = add <2 x i32> %411, <i32 2, i32 2>
  %413 = sext <2 x i32> %412 to <2 x i64>
  %414 = getelementptr float, <2 x float*> %98, <2 x i64> %413
  %415 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %414, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift191 = shufflevector <2 x float> %415, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %416 = fadd reassoc ninf nsz <2 x float> %415, %shift191
  %417 = insertelement <2 x float> %416, float 2.000000e+00, i64 1
  %418 = insertelement <2 x float> poison, float %401, i64 0
  %419 = shufflevector <2 x float> %418, <2 x float> poison, <2 x i32> zeroinitializer
  %420 = fmul reassoc ninf nsz <2 x float> %417, %419
  %421 = fadd reassoc ninf nsz <2 x float> %420, %398
  %.not161 = icmp eq i32 %68, 15
  br i1 %.not161, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %422 = getelementptr float, float* %72, i64 16
  %423 = load float, float* %422, align 4
  %424 = add <2 x i32> %75, <i32 16, i32 -16>
  %425 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %424, i1 true)
  %426 = sub <2 x i32> %425, %83
  %427 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %426, <2 x i32> zeroinitializer)
  %428 = mul <2 x i32> %427, <i32 -2, i32 -2>
  %429 = add <2 x i32> %428, %425
  %430 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %429, <2 x i32> zeroinitializer)
  %431 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %83, <2 x i32> %430)
  %432 = add <2 x i32> %431, %90
  %433 = mul <2 x i32> %432, %93
  %434 = add <2 x i32> %433, <i32 2, i32 2>
  %435 = sext <2 x i32> %434 to <2 x i64>
  %436 = getelementptr float, <2 x float*> %98, <2 x i64> %435
  %437 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %436, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift192 = shufflevector <2 x float> %437, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %438 = fadd reassoc ninf nsz <2 x float> %437, %shift192
  %439 = insertelement <2 x float> %438, float 2.000000e+00, i64 1
  %440 = insertelement <2 x float> poison, float %423, i64 0
  %441 = shufflevector <2 x float> %440, <2 x float> poison, <2 x i32> zeroinitializer
  %442 = fmul reassoc ninf nsz <2 x float> %439, %441
  %443 = fadd reassoc ninf nsz <2 x float> %442, %421
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %444 = phi <2 x float> [ %443, %true_block43 ], [ %421, %after_if42 ], [ %398, %after_if39 ], [ %376, %after_if36 ], [ %353, %after_if33 ], [ %331, %after_if30 ], [ %308, %after_if27 ], [ %286, %after_if24 ], [ %263, %after_if21 ], [ %241, %after_if18 ], [ %218, %after_if15 ], [ %196, %after_if12 ], [ %173, %after_if9 ], [ %151, %after_if6 ], [ %128, %after_if3 ], [ %106, %after_if ], [ %71, %for_loop_body ]
  %shift193 = shufflevector <2 x float> %444, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %445 = fdiv reassoc ninf nsz <2 x float> %444, %shift193
  %446 = extractelement <2 x float> %445, i64 0
  %447 = load float*, float** %28, align 8
  %448 = load i32, i32* %29, align 4
  %449 = load i32, i32* %30, align 4
  %450 = mul i32 %448, %49
  %451 = add i32 %450, %57
  %452 = mul i32 %451, %449
  %453 = add i32 %452, 2
  %454 = sext i32 %453 to i64
  %455 = getelementptr float, float* %447, i64 %454
  store float %446, float* %455, align 4
  %456 = add nsw i32 %.091177, 1
  %exitcond.not = icmp eq i32 %19, %456
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.6**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.6*, %struct.RuntimeContext.6** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.6* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.6* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
