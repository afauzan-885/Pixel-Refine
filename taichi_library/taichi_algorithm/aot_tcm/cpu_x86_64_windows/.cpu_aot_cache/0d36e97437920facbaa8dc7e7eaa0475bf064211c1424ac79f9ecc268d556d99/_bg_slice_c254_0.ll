; ModuleID = '<string>'
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
define void @_bg_slice_c252_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 5
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 6
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bg_slice_c252_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 9
  %25 = load i32, i32* %24, align 4
  %26 = sitofp i32 %23 to float
  %27 = add i32 %25, -1
  %28 = icmp slt i32 %17, %19
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 8
  %30 = load i32, i32* %29, align 4
  %31 = add i32 %30, -1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %33 = load i32, i32* %32, align 4
  %34 = add i32 %33, -1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %36 = load i32, i32* %35, align 4
  %37 = sitofp i32 %36 to float
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %39 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %42 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 3
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %46 = insertelement <2 x i32> poison, i32 %34, i64 0
  %47 = shufflevector <2 x i32> %46, <2 x i32> poison, <2 x i32> zeroinitializer
  %48 = insertelement <2 x i32> poison, i32 %31, i64 0
  %49 = shufflevector <2 x i32> %48, <2 x i32> poison, <2 x i32> zeroinitializer
  %50 = insertelement <2 x float> poison, float %37, i64 0
  %51 = shufflevector <2 x float> %50, <2 x float> poison, <2 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.047 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %237, %after_if ]
  %52 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %53 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %52, i64 0, i32 14
  %54 = load i8*, i8** %53, align 8
  %55 = getelementptr inbounds i8, i8* %54, i64 4
  %56 = bitcast i8* %55 to i32*
  %57 = load i32, i32* %56, align 4
  %58 = sdiv i32 %.047, %57
  %59 = mul i32 %58, %57
  %60 = xor i32 %57, %.047
  %61 = icmp slt i32 %60, 0
  %62 = icmp ne i32 %.047, 0
  %63 = icmp ne i32 %.047, %59
  %64 = and i1 %62, %61
  %65 = and i1 %64, %63
  %.neg6 = sext i1 %65 to i32
  %66 = add i32 %58, %.neg6
  %67 = mul i32 %57, -1
  %68 = mul i32 %67, %66
  %69 = add i32 %.047, %68
  %70 = load float*, float** %38, align 8
  %71 = load i32, i32* %39, align 4
  %72 = sub i32 %71, %57
  %73 = mul i32 %72, %66
  %74 = add i32 %.047, %73
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, float* %70, i64 %75
  %77 = load float, float* %76, align 4
  %78 = fdiv reassoc ninf nsz float %77, %26
  %79 = tail call reassoc ninf nsz float @llvm.floor.f32(float %78)
  %80 = fptosi float %79 to i32
  %81 = sitofp i32 %80 to float
  %82 = fsub reassoc ninf nsz float %78, %81
  %83 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %27, i32 %83)
  %85 = load float*, float** %40, align 8
  %86 = load i32, i32* %41, align 4
  %87 = load i32, i32* %42, align 4
  %88 = load i32, i32* %43, align 4
  %89 = insertelement <2 x i32> poison, i32 %86, i64 0
  %90 = shufflevector <2 x i32> %89, <2 x i32> poison, <2 x i32> zeroinitializer
  %91 = insertelement <4 x i32> poison, i32 %87, i64 0
  %shuffle9 = shufflevector <4 x i32> %91, <4 x i32> poison, <4 x i32> zeroinitializer
  %92 = insertelement <4 x i32> poison, i32 %84, i64 0
  %shuffle10 = shufflevector <4 x i32> %92, <4 x i32> poison, <4 x i32> zeroinitializer
  %93 = insertelement <4 x i32> poison, i32 %88, i64 0
  %shuffle11 = shufflevector <4 x i32> %93, <4 x i32> poison, <4 x i32> zeroinitializer
  %94 = add i32 %80, 1
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %27, i32 %95)
  %97 = insertelement <2 x float*> poison, float* %85, i64 0
  %98 = shufflevector <2 x float*> %97, <2 x float*> poison, <2 x i32> zeroinitializer
  %99 = insertelement <2 x i32> poison, i32 %66, i64 0
  %100 = insertelement <2 x i32> %99, i32 %69, i64 1
  %101 = sitofp <2 x i32> %100 to <2 x float>
  %102 = fdiv reassoc ninf nsz <2 x float> %101, %51
  %103 = call reassoc ninf nsz <2 x float> @llvm.floor.v2f32(<2 x float> %102)
  %104 = fptosi <2 x float> %103 to <2 x i32>
  %105 = sitofp <2 x i32> %104 to <2 x float>
  %106 = extractelement <2 x i32> %104, i64 0
  %107 = add i32 %106, 1
  %108 = extractelement <2 x i32> %104, i64 1
  %109 = add i32 %108, 1
  %110 = insertelement <2 x i32> poison, i32 %107, i64 0
  %111 = shufflevector <2 x i32> %110, <2 x i32> %104, <2 x i32> <i32 0, i32 2>
  %112 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %111, <2 x i32> zeroinitializer)
  %113 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %47, <2 x i32> %112)
  %114 = mul <2 x i32> %113, %90
  %shuffle = shufflevector <2 x i32> %114, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %115 = insertelement <2 x i32> %104, i32 %109, i64 0
  %116 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %115, <2 x i32> zeroinitializer)
  %117 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %49, <2 x i32> %116)
  %shuffle8 = shufflevector <2 x i32> %117, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %118 = add <4 x i32> %shuffle, %shuffle8
  %119 = mul <4 x i32> %118, %shuffle9
  %120 = add <4 x i32> %119, %shuffle10
  %121 = mul <4 x i32> %120, %shuffle11
  %122 = insertelement <4 x i32> poison, i32 %96, i64 0
  %shuffle12 = shufflevector <4 x i32> %122, <4 x i32> poison, <4 x i32> zeroinitializer
  %123 = add <4 x i32> %119, %shuffle12
  %124 = mul <4 x i32> %123, %shuffle11
  %125 = add <4 x i32> %124, <i32 1, i32 1, i32 1, i32 1>
  %126 = sext <4 x i32> %125 to <4 x i64>
  %127 = extractelement <4 x i64> %126, i64 3
  %128 = getelementptr float, float* %85, i64 %127
  %129 = load float, float* %128, align 4
  %130 = extractelement <4 x i64> %126, i64 2
  %131 = getelementptr float, float* %85, i64 %130
  %132 = load float, float* %131, align 4
  %133 = extractelement <4 x i64> %126, i64 1
  %134 = getelementptr float, float* %85, i64 %133
  %135 = load float, float* %134, align 4
  %136 = extractelement <4 x i64> %126, i64 0
  %137 = getelementptr float, float* %85, i64 %136
  %138 = load float, float* %137, align 4
  %139 = fsub reassoc ninf nsz <2 x float> %102, %105
  %140 = shufflevector <4 x i32> %121, <4 x i32> undef, <2 x i32> <i32 2, i32 1>
  %141 = add <2 x i32> %140, <i32 1, i32 1>
  %142 = sext <2 x i32> %141 to <2 x i64>
  %143 = getelementptr float, <2 x float*> %98, <2 x i64> %142
  %144 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %143, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %145 = shufflevector <4 x i32> %121, <4 x i32> undef, <2 x i32> <i32 3, i32 0>
  %146 = add <2 x i32> %145, <i32 1, i32 1>
  %147 = sext <2 x i32> %146 to <2 x i64>
  %148 = getelementptr float, <2 x float*> %98, <2 x i64> %147
  %149 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %148, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %150 = extractelement <2 x float> %139, i64 0
  %151 = fsub reassoc ninf nsz float 1.000000e+00, %150
  %152 = insertelement <2 x float> %139, float %151, i64 1
  %153 = fmul reassoc ninf nsz <2 x float> %152, %144
  %154 = insertelement <2 x float> poison, float %151, i64 0
  %155 = shufflevector <2 x float> %154, <2 x float> %139, <2 x i32> <i32 0, i32 2>
  %156 = fmul reassoc ninf nsz <2 x float> %155, %149
  %157 = fadd reassoc ninf nsz <2 x float> %153, %156
  %158 = fmul reassoc ninf nsz float %129, %151
  %159 = fsub reassoc ninf nsz <2 x float> <float poison, float 1.000000e+00>, %139
  %160 = fmul reassoc ninf nsz float %132, %150
  %161 = fadd reassoc ninf nsz float %160, %158
  %162 = fmul reassoc ninf nsz float %135, %151
  %163 = fmul reassoc ninf nsz float %138, %150
  %164 = fadd reassoc ninf nsz float %163, %162
  %165 = shufflevector <2 x float> %159, <2 x float> %139, <2 x i32> <i32 1, i32 3>
  %166 = fmul reassoc ninf nsz <2 x float> %157, %165
  %shift = shufflevector <2 x float> %166, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %167 = fadd reassoc ninf nsz <2 x float> %166, %shift
  %168 = extractelement <2 x float> %167, i64 0
  %169 = extractelement <2 x float> %159, i64 1
  %170 = fmul reassoc ninf nsz float %161, %169
  %171 = extractelement <2 x float> %139, i64 1
  %172 = fmul reassoc ninf nsz float %164, %171
  %173 = fadd reassoc ninf nsz float %172, %170
  %174 = fsub reassoc ninf nsz float 1.000000e+00, %82
  %175 = fmul reassoc ninf nsz float %168, %174
  %176 = fmul reassoc ninf nsz float %173, %82
  %177 = fadd reassoc ninf nsz float %176, %175
  %178 = fcmp reassoc ninf nsz ogt float %177, 0x3EB0C6F7A0000000
  br i1 %178, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %179 = sext <4 x i32> %121 to <4 x i64>
  %180 = extractelement <4 x i64> %179, i64 0
  %181 = getelementptr float, float* %85, i64 %180
  %182 = load float, float* %181, align 4
  %183 = extractelement <4 x i64> %179, i64 1
  %184 = getelementptr float, float* %85, i64 %183
  %185 = load float, float* %184, align 4
  %186 = extractelement <4 x i64> %179, i64 2
  %187 = getelementptr float, float* %85, i64 %186
  %188 = load float, float* %187, align 4
  %189 = extractelement <4 x i64> %179, i64 3
  %190 = getelementptr float, float* %85, i64 %189
  %191 = load float, float* %190, align 4
  %192 = fmul reassoc ninf nsz float %191, %151
  %193 = fmul reassoc ninf nsz float %188, %150
  %194 = fadd reassoc ninf nsz float %192, %193
  %195 = fmul reassoc ninf nsz float %194, %169
  %196 = fmul reassoc ninf nsz float %185, %151
  %197 = fmul reassoc ninf nsz float %182, %150
  %198 = fadd reassoc ninf nsz float %196, %197
  %199 = fmul reassoc ninf nsz float %198, %171
  %200 = fadd reassoc ninf nsz float %195, %199
  %201 = fmul reassoc ninf nsz float %200, %174
  %202 = extractelement <4 x i32> %124, i64 3
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, float* %85, i64 %203
  %205 = load float, float* %204, align 4
  %206 = fmul reassoc ninf nsz float %205, %151
  %207 = extractelement <4 x i32> %124, i64 2
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, float* %85, i64 %208
  %210 = load float, float* %209, align 4
  %211 = fmul reassoc ninf nsz float %210, %150
  %212 = fadd reassoc ninf nsz float %211, %206
  %213 = fmul reassoc ninf nsz float %212, %169
  %214 = extractelement <4 x i32> %124, i64 1
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, float* %85, i64 %215
  %217 = load float, float* %216, align 4
  %218 = fmul reassoc ninf nsz float %217, %151
  %219 = extractelement <4 x i32> %124, i64 0
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %85, i64 %220
  %222 = load float, float* %221, align 4
  %223 = fmul reassoc ninf nsz float %222, %150
  %224 = fadd reassoc ninf nsz float %223, %218
  %225 = fmul reassoc ninf nsz float %224, %171
  %226 = fadd reassoc ninf nsz float %225, %213
  %227 = fmul reassoc ninf nsz float %226, %82
  %228 = fadd reassoc ninf nsz float %227, %201
  %229 = fdiv reassoc ninf nsz float %228, %177
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %.0 = phi float [ %229, %true_block ], [ %77, %for_loop_body ]
  %230 = load float*, float** %44, align 8
  %231 = load i32, i32* %45, align 4
  %232 = sub i32 %231, %57
  %233 = mul i32 %232, %66
  %234 = add i32 %.047, %233
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, float* %230, i64 %235
  store float %.0, float* %236, align 4
  %237 = add nsw i32 %.047, 1
  %exitcond.not = icmp eq i32 %19, %237
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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

; Function Attrs: argmemonly nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.floor.v2f32(<2 x float>) #3

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly nocallback nofree nounwind willreturn }
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
