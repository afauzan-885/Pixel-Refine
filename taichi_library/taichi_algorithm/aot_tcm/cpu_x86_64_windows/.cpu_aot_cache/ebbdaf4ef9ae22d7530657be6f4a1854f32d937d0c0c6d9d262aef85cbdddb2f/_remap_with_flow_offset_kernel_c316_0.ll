; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.180*, void (%struct.RuntimeContext.180*, i8*)*, void (%struct.RuntimeContext.180*, i8*, i32)*, void (%struct.RuntimeContext.180*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.180 = type { i8*, %struct.LLVMRuntime.179*, i32, i64* }
%struct.LLVMRuntime.179 = type { %struct.PreallocatedMemoryChunk.175, %struct.PreallocatedMemoryChunk.175, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.176*], [1024 x %struct.NodeManager.177*], [1024 x i8*], i8*, %struct.RandState.178*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.175 = type { i8*, i8*, i64 }
%struct.ListManager.176 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.179* }
%struct.NodeManager.177 = type { %struct.LLVMRuntime.179*, i32, i32, i32, i32, %struct.ListManager.176*, %struct.ListManager.176*, %struct.ListManager.176*, i32 }
%struct.RandState.178 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_remap_with_flow_offset_kernel_c316_0_kernel_0_serial(%struct.RuntimeContext.180* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.180* %context to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.180, %struct.RuntimeContext.180* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.179*, %struct.LLVMRuntime.179** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.179, %struct.LLVMRuntime.179* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.179*, %struct.LLVMRuntime.179** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.179, %struct.LLVMRuntime.179* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_remap_with_flow_offset_kernel_c316_0_kernel_1_range_for(%struct.RuntimeContext.180* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.180* %context, %struct.RuntimeContext.180** %4, align 8
  store void (%struct.RuntimeContext.180*, i8*)* null, void (%struct.RuntimeContext.180*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.180*, i8*, i32)* @function_body, void (%struct.RuntimeContext.180*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.180*, i8*)* null, void (%struct.RuntimeContext.180*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.180, %struct.RuntimeContext.180* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.179*, %struct.LLVMRuntime.179** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.179, %struct.LLVMRuntime.179* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.179, %struct.LLVMRuntime.179* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.180* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.180, %struct.RuntimeContext.180* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.179*, %struct.LLVMRuntime.179** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.179, %struct.LLVMRuntime.179* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.180* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 11
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 12
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 8
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 6
  %29 = load i32, i32* %28, align 4
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 7
  %31 = load i32, i32* %30, align 4
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 5
  %33 = load i32, i32* %32, align 4
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 9
  %35 = load float, float* %34, align 4
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 10
  %37 = load float, float* %36, align 4
  %38 = add i32 %27, -1
  %39 = add i32 %29, -1
  %40 = add i32 %31, -1
  %41 = add i32 %33, -1
  %42 = sitofp i32 %38 to float
  %43 = sitofp i32 %39 to float
  %44 = sitofp i32 %40 to float
  %45 = sitofp i32 %41 to float
  %46 = icmp slt i32 %17, %19
  br i1 %46, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %47 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 3
  %48 = load i32, i32* %47, align 4
  %49 = add i32 %48, -1
  %50 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 4
  %51 = load i32, i32* %50, align 4
  %52 = add i32 %51, -1
  %53 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 1, i32 1
  %54 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %55 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %56 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 0, i32 1
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %58 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 2, i32 1
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %60 = insertelement <2 x i32> poison, i32 %40, i64 0
  %61 = shufflevector <2 x i32> %60, <2 x i32> poison, <2 x i32> zeroinitializer
  %62 = insertelement <2 x i32> poison, i32 %38, i64 0
  %63 = shufflevector <2 x i32> %62, <2 x i32> poison, <2 x i32> zeroinitializer
  %64 = insertelement <2 x i32> poison, i32 %49, i64 0
  %65 = shufflevector <2 x i32> %64, <2 x i32> poison, <2 x i32> zeroinitializer
  %66 = insertelement <2 x i32> poison, i32 %52, i64 0
  %67 = shufflevector <2 x i32> %66, <2 x i32> poison, <2 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.014 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %252, %for_loop_body ]
  %68 = load %struct.LLVMRuntime.179*, %struct.LLVMRuntime.179** %3, align 8
  %69 = getelementptr inbounds %struct.LLVMRuntime.179, %struct.LLVMRuntime.179* %68, i64 0, i32 14
  %70 = load i8*, i8** %69, align 8
  %71 = getelementptr inbounds i8, i8* %70, i64 4
  %72 = bitcast i8* %71 to i32*
  %73 = load i32, i32* %72, align 4
  %74 = sdiv i32 %.014, %73
  %75 = mul i32 %74, %73
  %76 = xor i32 %73, %.014
  %77 = icmp slt i32 %76, 0
  %78 = icmp ne i32 %.014, 0
  %79 = icmp ne i32 %.014, %75
  %80 = and i1 %78, %77
  %81 = and i1 %80, %79
  %.neg4 = sext i1 %81 to i32
  %82 = add i32 %74, %.neg4
  %83 = add i32 %82, %23
  %84 = mul i32 %73, -1
  %85 = mul i32 %84, %82
  %86 = add i32 %25, %.014
  %87 = add i32 %86, %85
  %88 = sitofp i32 %87 to float
  %89 = fmul reassoc ninf nsz float %88, %42
  %90 = fdiv reassoc ninf nsz float %89, %43
  %91 = sitofp i32 %83 to float
  %92 = fmul reassoc ninf nsz float %91, %44
  %93 = fdiv reassoc ninf nsz float %92, %45
  %94 = tail call reassoc ninf nsz float @llvm.floor.f32(float %90)
  %95 = fptosi float %94 to i32
  %96 = tail call reassoc ninf nsz float @llvm.floor.f32(float %93)
  %97 = fptosi float %96 to i32
  %98 = sitofp i32 %95 to float
  %99 = fsub reassoc ninf nsz float %90, %98
  %100 = sitofp i32 %97 to float
  %101 = fsub reassoc ninf nsz float %93, %100
  %102 = add i32 %95, 1
  %103 = add i32 %97, 1
  %104 = load float*, float** %53, align 8
  %105 = load i32, i32* %54, align 4
  %106 = load i32, i32* %55, align 4
  %107 = insertelement <2 x i32> poison, i32 %95, i64 0
  %108 = insertelement <2 x i32> %107, i32 %102, i64 1
  %109 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %108, i1 true)
  %110 = sub <2 x i32> %109, %63
  %111 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %110, <2 x i32> zeroinitializer)
  %112 = mul <2 x i32> %111, <i32 -2, i32 -2>
  %113 = add <2 x i32> %112, %109
  %114 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %113, <2 x i32> zeroinitializer)
  %115 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %63, <2 x i32> %114)
  %shuffle15 = shufflevector <2 x i32> %115, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %116 = insertelement <2 x i32> poison, i32 %97, i64 0
  %117 = insertelement <2 x i32> %116, i32 %103, i64 1
  %118 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %117, i1 true)
  %119 = sub <2 x i32> %118, %61
  %120 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %119, <2 x i32> zeroinitializer)
  %121 = mul <2 x i32> %120, <i32 -2, i32 -2>
  %122 = add <2 x i32> %121, %118
  %123 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %122, <2 x i32> zeroinitializer)
  %124 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %61, <2 x i32> %123)
  %125 = insertelement <2 x i32> poison, i32 %105, i64 0
  %126 = shufflevector <2 x i32> %125, <2 x i32> poison, <2 x i32> zeroinitializer
  %127 = mul <2 x i32> %124, %126
  %shuffle = shufflevector <2 x i32> %127, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %128 = add <4 x i32> %shuffle, %shuffle15
  %129 = insertelement <4 x i32> poison, i32 %106, i64 0
  %shuffle16 = shufflevector <4 x i32> %129, <4 x i32> poison, <4 x i32> zeroinitializer
  %130 = mul <4 x i32> %128, %shuffle16
  %131 = sext <4 x i32> %130 to <4 x i64>
  %132 = extractelement <4 x i64> %131, i64 0
  %133 = getelementptr float, float* %104, i64 %132
  %134 = load float, float* %133, align 4
  %135 = extractelement <4 x i64> %131, i64 1
  %136 = getelementptr float, float* %104, i64 %135
  %137 = load float, float* %136, align 4
  %138 = extractelement <4 x i64> %131, i64 2
  %139 = getelementptr float, float* %104, i64 %138
  %140 = load float, float* %139, align 4
  %141 = extractelement <4 x i64> %131, i64 3
  %142 = getelementptr float, float* %104, i64 %141
  %143 = load float, float* %142, align 4
  %144 = fsub reassoc ninf nsz float 1.000000e+00, %99
  %145 = fmul reassoc ninf nsz float %144, %134
  %146 = fmul reassoc ninf nsz float %99, %137
  %147 = fadd reassoc ninf nsz float %145, %146
  %148 = fmul reassoc ninf nsz float %144, %140
  %149 = fmul reassoc ninf nsz float %99, %143
  %150 = fadd reassoc ninf nsz float %148, %149
  %151 = fsub reassoc ninf nsz float 1.000000e+00, %101
  %152 = fmul reassoc ninf nsz float %147, %151
  %153 = fmul reassoc ninf nsz float %150, %101
  %154 = fadd reassoc ninf nsz float %152, %153
  %155 = add <4 x i32> %130, <i32 1, i32 1, i32 1, i32 1>
  %156 = extractelement <4 x i32> %155, i64 0
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %104, i64 %157
  %159 = load float, float* %158, align 4
  %160 = extractelement <4 x i32> %155, i64 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %104, i64 %161
  %163 = load float, float* %162, align 4
  %164 = extractelement <4 x i32> %155, i64 2
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, float* %104, i64 %165
  %167 = load float, float* %166, align 4
  %168 = extractelement <4 x i32> %155, i64 3
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, float* %104, i64 %169
  %171 = load float, float* %170, align 4
  %172 = fmul reassoc ninf nsz float %144, %159
  %173 = fmul reassoc ninf nsz float %99, %163
  %174 = fadd reassoc ninf nsz float %172, %173
  %175 = fmul reassoc ninf nsz float %144, %167
  %176 = fmul reassoc ninf nsz float %99, %171
  %177 = fadd reassoc ninf nsz float %175, %176
  %178 = fmul reassoc ninf nsz float %174, %151
  %179 = fmul reassoc ninf nsz float %177, %101
  %180 = fadd reassoc ninf nsz float %178, %179
  %181 = fmul reassoc ninf nsz float %154, %35
  %182 = fadd reassoc ninf nsz float %181, %88
  %183 = fmul reassoc ninf nsz float %180, %37
  %184 = fadd reassoc ninf nsz float %183, %91
  %185 = tail call reassoc ninf nsz float @llvm.floor.f32(float %182)
  %186 = fptosi float %185 to i32
  %187 = tail call reassoc ninf nsz float @llvm.floor.f32(float %184)
  %188 = fptosi float %187 to i32
  %189 = sitofp i32 %186 to float
  %190 = fsub reassoc ninf nsz float %182, %189
  %191 = sitofp i32 %188 to float
  %192 = fsub reassoc ninf nsz float %184, %191
  %193 = add i32 %186, 1
  %194 = add i32 %188, 1
  %195 = load float*, float** %56, align 8
  %196 = load i32, i32* %57, align 4
  %197 = insertelement <2 x i32> poison, i32 %186, i64 0
  %198 = insertelement <2 x i32> %197, i32 %193, i64 1
  %199 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %198, i1 true)
  %200 = sub <2 x i32> %199, %67
  %201 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %200, <2 x i32> zeroinitializer)
  %202 = mul <2 x i32> %201, <i32 -2, i32 -2>
  %203 = add <2 x i32> %202, %199
  %204 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %203, <2 x i32> zeroinitializer)
  %205 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %67, <2 x i32> %204)
  %shuffle18 = shufflevector <2 x i32> %205, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %206 = insertelement <2 x i32> poison, i32 %188, i64 0
  %207 = insertelement <2 x i32> %206, i32 %194, i64 1
  %208 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %207, i1 true)
  %209 = sub <2 x i32> %208, %65
  %210 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %209, <2 x i32> zeroinitializer)
  %211 = mul <2 x i32> %210, <i32 -2, i32 -2>
  %212 = add <2 x i32> %211, %208
  %213 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %212, <2 x i32> zeroinitializer)
  %214 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %65, <2 x i32> %213)
  %215 = insertelement <2 x i32> poison, i32 %196, i64 0
  %216 = shufflevector <2 x i32> %215, <2 x i32> poison, <2 x i32> zeroinitializer
  %217 = mul <2 x i32> %214, %216
  %shuffle17 = shufflevector <2 x i32> %217, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %218 = add <4 x i32> %shuffle17, %shuffle18
  %219 = extractelement <4 x i32> %218, i64 0
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %195, i64 %220
  %222 = load float, float* %221, align 4
  %223 = extractelement <4 x i32> %218, i64 1
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %195, i64 %224
  %226 = load float, float* %225, align 4
  %227 = extractelement <4 x i32> %218, i64 2
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, float* %195, i64 %228
  %230 = load float, float* %229, align 4
  %231 = extractelement <4 x i32> %218, i64 3
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, float* %195, i64 %232
  %234 = load float, float* %233, align 4
  %235 = fsub reassoc ninf nsz float 1.000000e+00, %190
  %236 = fmul reassoc ninf nsz float %235, %222
  %237 = fmul reassoc ninf nsz float %190, %226
  %238 = fadd reassoc ninf nsz float %236, %237
  %239 = fmul reassoc ninf nsz float %235, %230
  %240 = fmul reassoc ninf nsz float %190, %234
  %241 = fadd reassoc ninf nsz float %239, %240
  %242 = fsub reassoc ninf nsz float %241, %238
  %243 = fmul reassoc ninf nsz float %242, %192
  %244 = fadd reassoc ninf nsz float %243, %238
  %245 = load float*, float** %58, align 8
  %246 = load i32, i32* %59, align 4
  %247 = sub i32 %246, %73
  %248 = mul i32 %247, %82
  %249 = add i32 %.014, %248
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, float* %245, i64 %250
  store float %244, float* %251, align 4
  %252 = add nsw i32 %.014, 1
  %exitcond.not = icmp eq i32 %19, %252
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
  %4 = alloca %struct.RuntimeContext.180, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.180**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.180*, %struct.RuntimeContext.180** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.180*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.180*, i8*)*, void (%struct.RuntimeContext.180*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.180*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.180*, i8*, i32)*, void (%struct.RuntimeContext.180*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.180*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.180*, i8*)*, void (%struct.RuntimeContext.180*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.180*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.180* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.180* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.180* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.180, %struct.RuntimeContext.180* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.180* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.180* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.180*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.180* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
