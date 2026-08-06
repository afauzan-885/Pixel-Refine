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
define void @_remap_with_flow_kernel_c312_0_kernel_0_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %1, i64 0, i32 5
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %11, i64 0, i32 6
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 8
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_remap_with_flow_kernel_c312_0_kernel_1_range_for(%struct.RuntimeContext.84* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.84* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 8
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 7
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 9
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 10
  %29 = load float, float* %28, align 4
  %30 = add i32 %23, -1
  %31 = add i32 %25, -1
  %32 = sitofp i32 %30 to float
  %33 = sitofp i32 %31 to float
  %34 = icmp slt i32 %17, %19
  br i1 %34, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 3
  %36 = load i32, i32* %35, align 4
  %37 = add i32 %36, -1
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 4
  %39 = load i32, i32* %38, align 4
  %40 = add i32 %39, -1
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %42 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 2
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %47 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %48 = insertelement <2 x i32> poison, i32 %31, i64 0
  %49 = shufflevector <2 x i32> %48, <2 x i32> poison, <2 x i32> zeroinitializer
  %50 = insertelement <2 x i32> poison, i32 %30, i64 0
  %51 = shufflevector <2 x i32> %50, <2 x i32> poison, <2 x i32> zeroinitializer
  %52 = insertelement <2 x i32> poison, i32 %37, i64 0
  %53 = shufflevector <2 x i32> %52, <2 x i32> poison, <2 x i32> zeroinitializer
  %54 = insertelement <2 x i32> poison, i32 %40, i64 0
  %55 = shufflevector <2 x i32> %54, <2 x i32> poison, <2 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.014 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %248, %for_loop_body ]
  %56 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %57 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %56, i64 0, i32 14
  %58 = load i8*, i8** %57, align 8
  %59 = getelementptr inbounds i8, i8* %58, i64 4
  %60 = bitcast i8* %59 to i32*
  %61 = load i32, i32* %60, align 4
  %62 = sdiv i32 %.014, %61
  %63 = mul i32 %62, %61
  %64 = xor i32 %61, %.014
  %65 = icmp slt i32 %64, 0
  %66 = icmp ne i32 %.014, 0
  %67 = icmp ne i32 %.014, %63
  %68 = and i1 %66, %65
  %69 = and i1 %68, %67
  %.neg4 = sext i1 %69 to i32
  %70 = add i32 %62, %.neg4
  %71 = mul i32 %61, -1
  %72 = mul i32 %71, %70
  %73 = add i32 %.014, %72
  %74 = sitofp i32 %73 to float
  %75 = fmul reassoc ninf nsz float %74, %32
  %76 = getelementptr inbounds i8, i8* %58, i64 8
  %77 = bitcast i8* %76 to i32*
  %78 = load i32, i32* %77, align 4
  %79 = add i32 %78, -1
  %80 = sitofp i32 %79 to float
  %81 = fdiv reassoc ninf nsz float %75, %80
  %82 = sitofp i32 %70 to float
  %83 = fmul reassoc ninf nsz float %82, %33
  %84 = getelementptr inbounds i8, i8* %58, i64 12
  %85 = bitcast i8* %84 to i32*
  %86 = load i32, i32* %85, align 4
  %87 = add i32 %86, -1
  %88 = sitofp i32 %87 to float
  %89 = fdiv reassoc ninf nsz float %83, %88
  %90 = tail call reassoc ninf nsz float @llvm.floor.f32(float %81)
  %91 = fptosi float %90 to i32
  %92 = tail call reassoc ninf nsz float @llvm.floor.f32(float %89)
  %93 = fptosi float %92 to i32
  %94 = sitofp i32 %91 to float
  %95 = fsub reassoc ninf nsz float %81, %94
  %96 = sitofp i32 %93 to float
  %97 = fsub reassoc ninf nsz float %89, %96
  %98 = add i32 %91, 1
  %99 = add i32 %93, 1
  %100 = load float*, float** %41, align 8
  %101 = load i32, i32* %42, align 4
  %102 = load i32, i32* %43, align 4
  %103 = insertelement <2 x i32> poison, i32 %91, i64 0
  %104 = insertelement <2 x i32> %103, i32 %98, i64 1
  %105 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %104, i1 true)
  %106 = sub <2 x i32> %105, %51
  %107 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %106, <2 x i32> zeroinitializer)
  %108 = mul <2 x i32> %107, <i32 -2, i32 -2>
  %109 = add <2 x i32> %108, %105
  %110 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %109, <2 x i32> zeroinitializer)
  %111 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %51, <2 x i32> %110)
  %shuffle15 = shufflevector <2 x i32> %111, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %112 = insertelement <2 x i32> poison, i32 %93, i64 0
  %113 = insertelement <2 x i32> %112, i32 %99, i64 1
  %114 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %113, i1 true)
  %115 = sub <2 x i32> %114, %49
  %116 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %115, <2 x i32> zeroinitializer)
  %117 = mul <2 x i32> %116, <i32 -2, i32 -2>
  %118 = add <2 x i32> %117, %114
  %119 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %118, <2 x i32> zeroinitializer)
  %120 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %49, <2 x i32> %119)
  %121 = insertelement <2 x i32> poison, i32 %101, i64 0
  %122 = shufflevector <2 x i32> %121, <2 x i32> poison, <2 x i32> zeroinitializer
  %123 = mul <2 x i32> %120, %122
  %shuffle = shufflevector <2 x i32> %123, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %124 = add <4 x i32> %shuffle, %shuffle15
  %125 = insertelement <4 x i32> poison, i32 %102, i64 0
  %shuffle16 = shufflevector <4 x i32> %125, <4 x i32> poison, <4 x i32> zeroinitializer
  %126 = mul <4 x i32> %124, %shuffle16
  %127 = sext <4 x i32> %126 to <4 x i64>
  %128 = extractelement <4 x i64> %127, i64 0
  %129 = getelementptr float, float* %100, i64 %128
  %130 = load float, float* %129, align 4
  %131 = extractelement <4 x i64> %127, i64 1
  %132 = getelementptr float, float* %100, i64 %131
  %133 = load float, float* %132, align 4
  %134 = extractelement <4 x i64> %127, i64 2
  %135 = getelementptr float, float* %100, i64 %134
  %136 = load float, float* %135, align 4
  %137 = extractelement <4 x i64> %127, i64 3
  %138 = getelementptr float, float* %100, i64 %137
  %139 = load float, float* %138, align 4
  %140 = fsub reassoc ninf nsz float 1.000000e+00, %95
  %141 = fmul reassoc ninf nsz float %140, %130
  %142 = fmul reassoc ninf nsz float %95, %133
  %143 = fadd reassoc ninf nsz float %141, %142
  %144 = fmul reassoc ninf nsz float %140, %136
  %145 = fmul reassoc ninf nsz float %95, %139
  %146 = fadd reassoc ninf nsz float %144, %145
  %147 = fsub reassoc ninf nsz float 1.000000e+00, %97
  %148 = fmul reassoc ninf nsz float %143, %147
  %149 = fmul reassoc ninf nsz float %146, %97
  %150 = fadd reassoc ninf nsz float %148, %149
  %151 = add <4 x i32> %126, <i32 1, i32 1, i32 1, i32 1>
  %152 = extractelement <4 x i32> %151, i64 0
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %100, i64 %153
  %155 = load float, float* %154, align 4
  %156 = extractelement <4 x i32> %151, i64 1
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %100, i64 %157
  %159 = load float, float* %158, align 4
  %160 = extractelement <4 x i32> %151, i64 2
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %100, i64 %161
  %163 = load float, float* %162, align 4
  %164 = extractelement <4 x i32> %151, i64 3
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, float* %100, i64 %165
  %167 = load float, float* %166, align 4
  %168 = fmul reassoc ninf nsz float %140, %155
  %169 = fmul reassoc ninf nsz float %95, %159
  %170 = fadd reassoc ninf nsz float %168, %169
  %171 = fmul reassoc ninf nsz float %140, %163
  %172 = fmul reassoc ninf nsz float %95, %167
  %173 = fadd reassoc ninf nsz float %171, %172
  %174 = fmul reassoc ninf nsz float %170, %147
  %175 = fmul reassoc ninf nsz float %173, %97
  %176 = fadd reassoc ninf nsz float %174, %175
  %177 = fmul reassoc ninf nsz float %150, %27
  %178 = fadd reassoc ninf nsz float %177, %74
  %179 = fmul reassoc ninf nsz float %176, %29
  %180 = fadd reassoc ninf nsz float %179, %82
  %181 = tail call reassoc ninf nsz float @llvm.floor.f32(float %178)
  %182 = fptosi float %181 to i32
  %183 = tail call reassoc ninf nsz float @llvm.floor.f32(float %180)
  %184 = fptosi float %183 to i32
  %185 = sitofp i32 %182 to float
  %186 = fsub reassoc ninf nsz float %178, %185
  %187 = sitofp i32 %184 to float
  %188 = fsub reassoc ninf nsz float %180, %187
  %189 = add i32 %182, 1
  %190 = add i32 %184, 1
  %191 = load float*, float** %44, align 8
  %192 = load i32, i32* %45, align 4
  %193 = insertelement <2 x i32> poison, i32 %182, i64 0
  %194 = insertelement <2 x i32> %193, i32 %189, i64 1
  %195 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %194, i1 true)
  %196 = sub <2 x i32> %195, %55
  %197 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %196, <2 x i32> zeroinitializer)
  %198 = mul <2 x i32> %197, <i32 -2, i32 -2>
  %199 = add <2 x i32> %198, %195
  %200 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %199, <2 x i32> zeroinitializer)
  %201 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %55, <2 x i32> %200)
  %shuffle18 = shufflevector <2 x i32> %201, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %202 = insertelement <2 x i32> poison, i32 %184, i64 0
  %203 = insertelement <2 x i32> %202, i32 %190, i64 1
  %204 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %203, i1 true)
  %205 = sub <2 x i32> %204, %53
  %206 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %205, <2 x i32> zeroinitializer)
  %207 = mul <2 x i32> %206, <i32 -2, i32 -2>
  %208 = add <2 x i32> %207, %204
  %209 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %208, <2 x i32> zeroinitializer)
  %210 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %53, <2 x i32> %209)
  %211 = insertelement <2 x i32> poison, i32 %192, i64 0
  %212 = shufflevector <2 x i32> %211, <2 x i32> poison, <2 x i32> zeroinitializer
  %213 = mul <2 x i32> %210, %212
  %shuffle17 = shufflevector <2 x i32> %213, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %214 = add <4 x i32> %shuffle17, %shuffle18
  %215 = extractelement <4 x i32> %214, i64 0
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, float* %191, i64 %216
  %218 = load float, float* %217, align 4
  %219 = extractelement <4 x i32> %214, i64 1
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %191, i64 %220
  %222 = load float, float* %221, align 4
  %223 = extractelement <4 x i32> %214, i64 2
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %191, i64 %224
  %226 = load float, float* %225, align 4
  %227 = extractelement <4 x i32> %214, i64 3
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, float* %191, i64 %228
  %230 = load float, float* %229, align 4
  %231 = fsub reassoc ninf nsz float 1.000000e+00, %186
  %232 = fmul reassoc ninf nsz float %231, %218
  %233 = fmul reassoc ninf nsz float %186, %222
  %234 = fadd reassoc ninf nsz float %232, %233
  %235 = fmul reassoc ninf nsz float %231, %226
  %236 = fmul reassoc ninf nsz float %186, %230
  %237 = fadd reassoc ninf nsz float %235, %236
  %238 = fsub reassoc ninf nsz float %237, %234
  %239 = fmul reassoc ninf nsz float %238, %188
  %240 = fadd reassoc ninf nsz float %239, %234
  %241 = load float*, float** %46, align 8
  %242 = load i32, i32* %47, align 4
  %243 = sub i32 %242, %61
  %244 = mul i32 %243, %70
  %245 = add i32 %.014, %244
  %246 = sext i32 %245 to i64
  %247 = getelementptr float, float* %241, i64 %246
  store float %240, float* %247, align 4
  %248 = add nsw i32 %.014, 1
  %exitcond.not = icmp eq i32 %19, %248
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

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

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
