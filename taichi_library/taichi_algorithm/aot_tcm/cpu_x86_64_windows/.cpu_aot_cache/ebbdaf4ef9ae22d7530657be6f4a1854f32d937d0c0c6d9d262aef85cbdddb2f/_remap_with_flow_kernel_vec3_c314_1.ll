; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.120*, void (%struct.RuntimeContext.120*, i8*)*, void (%struct.RuntimeContext.120*, i8*, i32)*, void (%struct.RuntimeContext.120*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.120 = type { i8*, %struct.LLVMRuntime.119*, i32, i64* }
%struct.LLVMRuntime.119 = type { %struct.PreallocatedMemoryChunk.115, %struct.PreallocatedMemoryChunk.115, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.116*], [1024 x %struct.NodeManager.117*], [1024 x i8*], i8*, %struct.RandState.118*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.115 = type { i8*, i8*, i64 }
%struct.ListManager.116 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.119* }
%struct.NodeManager.117 = type { %struct.LLVMRuntime.119*, i32, i32, i32, i32, %struct.ListManager.116*, %struct.ListManager.116*, %struct.ListManager.116*, i32 }
%struct.RandState.118 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_remap_with_flow_kernel_vec3_c314_1_kernel_0_serial(%struct.RuntimeContext.120* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.120* %context to { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %1, i64 0, i32 5
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %11, i64 0, i32 6
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 8
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_remap_with_flow_kernel_vec3_c314_1_kernel_1_range_for(%struct.RuntimeContext.120* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.120* %context, %struct.RuntimeContext.120** %4, align 8
  store void (%struct.RuntimeContext.120*, i8*)* null, void (%struct.RuntimeContext.120*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.120*, i8*, i32)* @function_body, void (%struct.RuntimeContext.120*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.120*, i8*)* null, void (%struct.RuntimeContext.120*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.120* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.120* %0 to { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }**
  %21 = load { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 8
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 7
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 9
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 10
  %29 = load float, float* %28, align 4
  %30 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 3
  %31 = load i32, i32* %30, align 4
  %32 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 4
  %33 = load i32, i32* %32, align 4
  %34 = add i32 %23, -1
  %35 = add i32 %25, -1
  %36 = add i32 %33, -1
  %37 = add i32 %31, -1
  %38 = sitofp i32 %34 to float
  %39 = sitofp i32 %35 to float
  %40 = icmp slt i32 %17, %19
  br i1 %40, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %41 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %42 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %43 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 2
  %44 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %45 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %47 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }, { { { i32, i32 }, i32* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, i32* }, i32, i32, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %48 = insertelement <2 x i32> poison, i32 %35, i64 0
  %49 = shufflevector <2 x i32> %48, <2 x i32> poison, <2 x i32> zeroinitializer
  %50 = insertelement <2 x i32> poison, i32 %34, i64 0
  %51 = shufflevector <2 x i32> %50, <2 x i32> poison, <2 x i32> zeroinitializer
  %52 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %52, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.013 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %338, %for_loop_body ]
  %53 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %3, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %53, i64 0, i32 14
  %55 = load i8*, i8** %54, align 8
  %56 = getelementptr inbounds i8, i8* %55, i64 4
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = sdiv i32 %.013, %58
  %60 = mul i32 %59, %58
  %61 = xor i32 %58, %.013
  %62 = icmp slt i32 %61, 0
  %63 = icmp ne i32 %.013, 0
  %64 = icmp ne i32 %.013, %60
  %65 = and i1 %63, %62
  %66 = and i1 %65, %64
  %.neg4 = sext i1 %66 to i32
  %67 = add i32 %59, %.neg4
  %68 = mul i32 %58, -1
  %69 = mul i32 %68, %67
  %70 = add i32 %.013, %69
  %71 = sitofp i32 %70 to float
  %72 = fmul reassoc ninf nsz float %71, %38
  %73 = getelementptr inbounds i8, i8* %55, i64 8
  %74 = bitcast i8* %73 to i32*
  %75 = load i32, i32* %74, align 4
  %76 = add i32 %75, -1
  %77 = sitofp i32 %76 to float
  %78 = fdiv reassoc ninf nsz float %72, %77
  %79 = sitofp i32 %67 to float
  %80 = fmul reassoc ninf nsz float %79, %39
  %81 = getelementptr inbounds i8, i8* %55, i64 12
  %82 = bitcast i8* %81 to i32*
  %83 = load i32, i32* %82, align 4
  %84 = add i32 %83, -1
  %85 = sitofp i32 %84 to float
  %86 = fdiv reassoc ninf nsz float %80, %85
  %87 = tail call reassoc ninf nsz float @llvm.floor.f32(float %78)
  %88 = fptosi float %87 to i32
  %89 = tail call reassoc ninf nsz float @llvm.floor.f32(float %86)
  %90 = fptosi float %89 to i32
  %91 = sitofp i32 %88 to float
  %92 = fsub reassoc ninf nsz float %78, %91
  %93 = sitofp i32 %90 to float
  %94 = fsub reassoc ninf nsz float %86, %93
  %95 = add i32 %88, 1
  %96 = add i32 %90, 1
  %97 = load float*, float** %41, align 8
  %98 = load i32, i32* %42, align 4
  %99 = load i32, i32* %43, align 4
  %100 = insertelement <2 x i32> poison, i32 %88, i64 0
  %101 = insertelement <2 x i32> %100, i32 %95, i64 1
  %102 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %101, i1 true)
  %103 = sub <2 x i32> %102, %51
  %104 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %103, <2 x i32> zeroinitializer)
  %105 = mul <2 x i32> %104, <i32 -2, i32 -2>
  %106 = add <2 x i32> %105, %102
  %107 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %106, <2 x i32> zeroinitializer)
  %108 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %51, <2 x i32> %107)
  %shuffle14 = shufflevector <2 x i32> %108, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %109 = insertelement <2 x i32> poison, i32 %90, i64 0
  %110 = insertelement <2 x i32> %109, i32 %96, i64 1
  %111 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %110, i1 true)
  %112 = sub <2 x i32> %111, %49
  %113 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %112, <2 x i32> zeroinitializer)
  %114 = mul <2 x i32> %113, <i32 -2, i32 -2>
  %115 = add <2 x i32> %114, %111
  %116 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %115, <2 x i32> zeroinitializer)
  %117 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %49, <2 x i32> %116)
  %118 = insertelement <2 x i32> poison, i32 %98, i64 0
  %119 = shufflevector <2 x i32> %118, <2 x i32> poison, <2 x i32> zeroinitializer
  %120 = mul <2 x i32> %117, %119
  %shuffle = shufflevector <2 x i32> %120, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %121 = add <4 x i32> %shuffle, %shuffle14
  %122 = insertelement <4 x i32> poison, i32 %99, i64 0
  %shuffle15 = shufflevector <4 x i32> %122, <4 x i32> poison, <4 x i32> zeroinitializer
  %123 = mul <4 x i32> %121, %shuffle15
  %124 = sext <4 x i32> %123 to <4 x i64>
  %125 = extractelement <4 x i64> %124, i64 0
  %126 = getelementptr float, float* %97, i64 %125
  %127 = load float, float* %126, align 4
  %128 = extractelement <4 x i64> %124, i64 1
  %129 = getelementptr float, float* %97, i64 %128
  %130 = load float, float* %129, align 4
  %131 = extractelement <4 x i64> %124, i64 2
  %132 = getelementptr float, float* %97, i64 %131
  %133 = load float, float* %132, align 4
  %134 = extractelement <4 x i64> %124, i64 3
  %135 = getelementptr float, float* %97, i64 %134
  %136 = load float, float* %135, align 4
  %137 = fsub reassoc ninf nsz float 1.000000e+00, %92
  %138 = fmul reassoc ninf nsz float %137, %127
  %139 = fmul reassoc ninf nsz float %92, %130
  %140 = fadd reassoc ninf nsz float %138, %139
  %141 = fmul reassoc ninf nsz float %137, %133
  %142 = fmul reassoc ninf nsz float %92, %136
  %143 = fadd reassoc ninf nsz float %141, %142
  %144 = fsub reassoc ninf nsz float 1.000000e+00, %94
  %145 = fmul reassoc ninf nsz float %140, %144
  %146 = fmul reassoc ninf nsz float %143, %94
  %147 = fadd reassoc ninf nsz float %145, %146
  %148 = add <4 x i32> %123, <i32 1, i32 1, i32 1, i32 1>
  %149 = extractelement <4 x i32> %148, i64 0
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, float* %97, i64 %150
  %152 = load float, float* %151, align 4
  %153 = extractelement <4 x i32> %148, i64 1
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %97, i64 %154
  %156 = load float, float* %155, align 4
  %157 = extractelement <4 x i32> %148, i64 2
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, float* %97, i64 %158
  %160 = load float, float* %159, align 4
  %161 = extractelement <4 x i32> %148, i64 3
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, float* %97, i64 %162
  %164 = load float, float* %163, align 4
  %165 = fmul reassoc ninf nsz float %137, %152
  %166 = fmul reassoc ninf nsz float %92, %156
  %167 = fadd reassoc ninf nsz float %165, %166
  %168 = fmul reassoc ninf nsz float %137, %160
  %169 = fmul reassoc ninf nsz float %92, %164
  %170 = fadd reassoc ninf nsz float %168, %169
  %171 = fmul reassoc ninf nsz float %167, %144
  %172 = fmul reassoc ninf nsz float %170, %94
  %173 = fadd reassoc ninf nsz float %171, %172
  %174 = fmul reassoc ninf nsz float %147, %27
  %175 = fadd reassoc ninf nsz float %174, %71
  %176 = fmul reassoc ninf nsz float %173, %29
  %177 = fadd reassoc ninf nsz float %176, %79
  %178 = tail call reassoc ninf nsz float @llvm.floor.f32(float %175)
  %179 = fptosi float %178 to i32
  %180 = tail call reassoc ninf nsz float @llvm.floor.f32(float %177)
  %181 = fptosi float %180 to i32
  %182 = sitofp i32 %179 to float
  %183 = fsub reassoc ninf nsz float %175, %182
  %184 = sitofp i32 %181 to float
  %185 = fsub reassoc ninf nsz float %177, %184
  %186 = tail call i32 @llvm.abs.i32(i32 %179, i1 true)
  %187 = sub i32 %186, %36
  %188 = tail call i32 @llvm.smax.i32(i32 %187, i32 0)
  %.neg9 = mul i32 %188, -2
  %189 = add i32 %.neg9, %186
  %190 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %191 = tail call i32 @llvm.smin.i32(i32 %36, i32 %190)
  %192 = tail call i32 @llvm.abs.i32(i32 %181, i1 true)
  %193 = sub i32 %192, %37
  %194 = tail call i32 @llvm.smax.i32(i32 %193, i32 0)
  %.neg10 = mul i32 %194, -2
  %195 = add i32 %.neg10, %192
  %196 = tail call i32 @llvm.smax.i32(i32 %195, i32 0)
  %197 = tail call i32 @llvm.smin.i32(i32 %37, i32 %196)
  %198 = add i32 %179, 1
  %199 = tail call i32 @llvm.abs.i32(i32 %198, i1 true)
  %200 = sub i32 %199, %36
  %201 = tail call i32 @llvm.smax.i32(i32 %200, i32 0)
  %.neg11 = mul i32 %201, -2
  %202 = add i32 %.neg11, %199
  %203 = tail call i32 @llvm.smax.i32(i32 %202, i32 0)
  %204 = tail call i32 @llvm.smin.i32(i32 %36, i32 %203)
  %205 = add i32 %181, 1
  %206 = tail call i32 @llvm.abs.i32(i32 %205, i1 true)
  %207 = sub i32 %206, %37
  %208 = tail call i32 @llvm.smax.i32(i32 %207, i32 0)
  %.neg12 = mul i32 %208, -2
  %209 = add i32 %.neg12, %206
  %210 = tail call i32 @llvm.smax.i32(i32 %209, i32 0)
  %211 = tail call i32 @llvm.smin.i32(i32 %37, i32 %210)
  %212 = load i32*, i32** %44, align 8
  %213 = load i32, i32* %45, align 4
  %214 = mul i32 %197, %213
  %215 = add i32 %214, %191
  %216 = mul i32 %215, 3
  %217 = sext i32 %216 to i64
  %218 = getelementptr i32, i32* %212, i64 %217
  %219 = load i32, i32* %218, align 4
  %220 = add i32 %216, 1
  %221 = sext i32 %220 to i64
  %222 = getelementptr i32, i32* %212, i64 %221
  %223 = load i32, i32* %222, align 4
  %224 = add i32 %216, 2
  %225 = sext i32 %224 to i64
  %226 = getelementptr i32, i32* %212, i64 %225
  %227 = load i32, i32* %226, align 4
  %228 = add i32 %214, %204
  %229 = mul i32 %228, 3
  %230 = sext i32 %229 to i64
  %231 = getelementptr i32, i32* %212, i64 %230
  %232 = load i32, i32* %231, align 4
  %233 = add i32 %229, 1
  %234 = sext i32 %233 to i64
  %235 = getelementptr i32, i32* %212, i64 %234
  %236 = load i32, i32* %235, align 4
  %237 = add i32 %229, 2
  %238 = sext i32 %237 to i64
  %239 = getelementptr i32, i32* %212, i64 %238
  %240 = load i32, i32* %239, align 4
  %241 = mul i32 %211, %213
  %242 = add i32 %241, %191
  %243 = mul i32 %242, 3
  %244 = sext i32 %243 to i64
  %245 = getelementptr i32, i32* %212, i64 %244
  %246 = load i32, i32* %245, align 4
  %247 = add i32 %243, 1
  %248 = sext i32 %247 to i64
  %249 = getelementptr i32, i32* %212, i64 %248
  %250 = load i32, i32* %249, align 4
  %251 = add i32 %243, 2
  %252 = sext i32 %251 to i64
  %253 = getelementptr i32, i32* %212, i64 %252
  %254 = load i32, i32* %253, align 4
  %255 = add i32 %241, %204
  %256 = mul i32 %255, 3
  %257 = sext i32 %256 to i64
  %258 = getelementptr i32, i32* %212, i64 %257
  %259 = load i32, i32* %258, align 4
  %260 = add i32 %256, 1
  %261 = sext i32 %260 to i64
  %262 = getelementptr i32, i32* %212, i64 %261
  %263 = load i32, i32* %262, align 4
  %264 = add i32 %256, 2
  %265 = sext i32 %264 to i64
  %266 = getelementptr i32, i32* %212, i64 %265
  %267 = load i32, i32* %266, align 4
  %268 = fsub reassoc ninf nsz float 1.000000e+00, %183
  %269 = sitofp i32 %219 to float
  %270 = sitofp i32 %223 to float
  %271 = sitofp i32 %227 to float
  %272 = fmul reassoc ninf nsz float %268, %269
  %273 = fmul reassoc ninf nsz float %268, %270
  %274 = fmul reassoc ninf nsz float %268, %271
  %275 = sitofp i32 %232 to float
  %276 = sitofp i32 %236 to float
  %277 = sitofp i32 %240 to float
  %278 = fmul reassoc ninf nsz float %183, %275
  %279 = fmul reassoc ninf nsz float %183, %276
  %280 = fmul reassoc ninf nsz float %183, %277
  %281 = fadd reassoc ninf nsz float %272, %278
  %282 = fadd reassoc ninf nsz float %273, %279
  %283 = fadd reassoc ninf nsz float %274, %280
  %284 = sitofp i32 %246 to float
  %285 = sitofp i32 %250 to float
  %286 = sitofp i32 %254 to float
  %287 = fmul reassoc ninf nsz float %268, %284
  %288 = fmul reassoc ninf nsz float %268, %285
  %289 = fmul reassoc ninf nsz float %268, %286
  %290 = sitofp i32 %259 to float
  %291 = sitofp i32 %263 to float
  %292 = sitofp i32 %267 to float
  %293 = fmul reassoc ninf nsz float %183, %290
  %294 = fmul reassoc ninf nsz float %183, %291
  %295 = fmul reassoc ninf nsz float %183, %292
  %296 = fadd reassoc ninf nsz float %287, %293
  %297 = fadd reassoc ninf nsz float %294, %288
  %298 = fadd reassoc ninf nsz float %295, %289
  %299 = fsub reassoc ninf nsz float 1.000000e+00, %185
  %300 = fmul reassoc ninf nsz float %281, %299
  %301 = fmul reassoc ninf nsz float %282, %299
  %302 = fmul reassoc ninf nsz float %283, %299
  %303 = fmul reassoc ninf nsz float %296, %185
  %304 = fmul reassoc ninf nsz float %297, %185
  %305 = fmul reassoc ninf nsz float %298, %185
  %306 = fadd reassoc ninf nsz float %300, %303
  %307 = fadd reassoc ninf nsz float %304, %301
  %308 = fadd reassoc ninf nsz float %305, %302
  %309 = fptosi float %306 to i32
  %310 = fptosi float %307 to i32
  %311 = fptosi float %308 to i32
  %312 = load i32*, i32** %46, align 8
  %313 = load i32, i32* %47, align 4
  %314 = sub i32 %313, %58
  %315 = mul i32 %314, 3
  %316 = mul i32 %315, %67
  %317 = add i32 %lsr.iv, %316
  %318 = sext i32 %317 to i64
  %319 = getelementptr i32, i32* %312, i64 %318
  store i32 %309, i32* %319, align 4
  %320 = load i32*, i32** %46, align 8
  %321 = load i32, i32* %47, align 4
  %322 = sub i32 %321, %58
  %323 = mul i32 %322, 3
  %324 = mul i32 %323, %67
  %325 = add i32 %lsr.iv, %324
  %326 = add i32 %325, 1
  %327 = sext i32 %326 to i64
  %328 = getelementptr i32, i32* %320, i64 %327
  store i32 %310, i32* %328, align 4
  %329 = load i32*, i32** %46, align 8
  %330 = load i32, i32* %47, align 4
  %331 = sub i32 %330, %58
  %332 = mul i32 %331, 3
  %333 = mul i32 %332, %67
  %334 = add i32 %lsr.iv, %333
  %335 = add i32 %334, 2
  %336 = sext i32 %335 to i64
  %337 = getelementptr i32, i32* %329, i64 %336
  store i32 %311, i32* %337, align 4
  %338 = add nsw i32 %.013, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %338
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
  %4 = alloca %struct.RuntimeContext.120, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.120**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.120*, %struct.RuntimeContext.120** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.120*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.120*, i8*)*, void (%struct.RuntimeContext.120*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.120*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.120*, i8*, i32)*, void (%struct.RuntimeContext.120*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.120*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.120*, i8*)*, void (%struct.RuntimeContext.120*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.120*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.120* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.120* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.120* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.120* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.120* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.120*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.120* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.abs.i32(i32, i1 immarg) #3

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
