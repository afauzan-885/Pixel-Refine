; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.192*, void (%struct.RuntimeContext.192*, i8*)*, void (%struct.RuntimeContext.192*, i8*, i32)*, void (%struct.RuntimeContext.192*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.192 = type { i8*, %struct.LLVMRuntime.191*, i32, i64* }
%struct.LLVMRuntime.191 = type { %struct.PreallocatedMemoryChunk.187, %struct.PreallocatedMemoryChunk.187, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.188*], [1024 x %struct.NodeManager.189*], [1024 x i8*], i8*, %struct.RandState.190*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.187 = type { i8*, i8*, i64 }
%struct.ListManager.188 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.191* }
%struct.NodeManager.189 = type { %struct.LLVMRuntime.191*, i32, i32, i32, i32, %struct.ListManager.188*, %struct.ListManager.188*, %struct.ListManager.188*, i32 }
%struct.RandState.190 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_remap_with_flow_offset_kernel_vec3_c318_0_kernel_0_serial(%struct.RuntimeContext.192* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.192* %context to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.192, %struct.RuntimeContext.192* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.191*, %struct.LLVMRuntime.191** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.191, %struct.LLVMRuntime.191* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.191*, %struct.LLVMRuntime.191** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.191, %struct.LLVMRuntime.191* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_remap_with_flow_offset_kernel_vec3_c318_0_kernel_1_range_for(%struct.RuntimeContext.192* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.192* %context, %struct.RuntimeContext.192** %4, align 8
  store void (%struct.RuntimeContext.192*, i8*)* null, void (%struct.RuntimeContext.192*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.192*, i8*, i32)* @function_body, void (%struct.RuntimeContext.192*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.192*, i8*)* null, void (%struct.RuntimeContext.192*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.192, %struct.RuntimeContext.192* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.191*, %struct.LLVMRuntime.191** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.191, %struct.LLVMRuntime.191* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.191, %struct.LLVMRuntime.191* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.192* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.192, %struct.RuntimeContext.192* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.191*, %struct.LLVMRuntime.191** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.191, %struct.LLVMRuntime.191* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.192* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }**
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
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 3
  %39 = load i32, i32* %38, align 4
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 4
  %41 = load i32, i32* %40, align 4
  %42 = add i32 %27, -1
  %43 = add i32 %29, -1
  %44 = add i32 %31, -1
  %45 = add i32 %33, -1
  %46 = add i32 %41, -1
  %47 = add i32 %39, -1
  %48 = sitofp i32 %42 to float
  %49 = sitofp i32 %43 to float
  %50 = sitofp i32 %44 to float
  %51 = sitofp i32 %45 to float
  %52 = icmp slt i32 %17, %19
  br i1 %52, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %53 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 1, i32 1
  %54 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %55 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %56 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 0, i32 1
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %58 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 2, i32 1
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, float, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %60 = insertelement <2 x i32> poison, i32 %44, i64 0
  %61 = shufflevector <2 x i32> %60, <2 x i32> poison, <2 x i32> zeroinitializer
  %62 = insertelement <2 x i32> poison, i32 %42, i64 0
  %63 = shufflevector <2 x i32> %62, <2 x i32> poison, <2 x i32> zeroinitializer
  %64 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %64, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.013 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %327, %for_loop_body ]
  %65 = load %struct.LLVMRuntime.191*, %struct.LLVMRuntime.191** %3, align 8
  %66 = getelementptr inbounds %struct.LLVMRuntime.191, %struct.LLVMRuntime.191* %65, i64 0, i32 14
  %67 = load i8*, i8** %66, align 8
  %68 = getelementptr inbounds i8, i8* %67, i64 4
  %69 = bitcast i8* %68 to i32*
  %70 = load i32, i32* %69, align 4
  %71 = sdiv i32 %.013, %70
  %72 = mul i32 %71, %70
  %73 = xor i32 %70, %.013
  %74 = icmp slt i32 %73, 0
  %75 = icmp ne i32 %.013, 0
  %76 = icmp ne i32 %.013, %72
  %77 = and i1 %75, %74
  %78 = and i1 %77, %76
  %.neg4 = sext i1 %78 to i32
  %79 = add i32 %71, %.neg4
  %80 = add i32 %79, %23
  %81 = mul i32 %70, -1
  %82 = mul i32 %81, %79
  %83 = add i32 %25, %.013
  %84 = add i32 %83, %82
  %85 = sitofp i32 %84 to float
  %86 = fmul reassoc ninf nsz float %85, %48
  %87 = fdiv reassoc ninf nsz float %86, %49
  %88 = sitofp i32 %80 to float
  %89 = fmul reassoc ninf nsz float %88, %50
  %90 = fdiv reassoc ninf nsz float %89, %51
  %91 = tail call reassoc ninf nsz float @llvm.floor.f32(float %87)
  %92 = fptosi float %91 to i32
  %93 = tail call reassoc ninf nsz float @llvm.floor.f32(float %90)
  %94 = fptosi float %93 to i32
  %95 = sitofp i32 %92 to float
  %96 = fsub reassoc ninf nsz float %87, %95
  %97 = sitofp i32 %94 to float
  %98 = fsub reassoc ninf nsz float %90, %97
  %99 = add i32 %92, 1
  %100 = add i32 %94, 1
  %101 = load float*, float** %53, align 8
  %102 = load i32, i32* %54, align 4
  %103 = load i32, i32* %55, align 4
  %104 = insertelement <2 x i32> poison, i32 %92, i64 0
  %105 = insertelement <2 x i32> %104, i32 %99, i64 1
  %106 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %105, i1 true)
  %107 = sub <2 x i32> %106, %63
  %108 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %107, <2 x i32> zeroinitializer)
  %109 = mul <2 x i32> %108, <i32 -2, i32 -2>
  %110 = add <2 x i32> %109, %106
  %111 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %110, <2 x i32> zeroinitializer)
  %112 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %63, <2 x i32> %111)
  %shuffle14 = shufflevector <2 x i32> %112, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %113 = insertelement <2 x i32> poison, i32 %94, i64 0
  %114 = insertelement <2 x i32> %113, i32 %100, i64 1
  %115 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %114, i1 true)
  %116 = sub <2 x i32> %115, %61
  %117 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %116, <2 x i32> zeroinitializer)
  %118 = mul <2 x i32> %117, <i32 -2, i32 -2>
  %119 = add <2 x i32> %118, %115
  %120 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %119, <2 x i32> zeroinitializer)
  %121 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %61, <2 x i32> %120)
  %122 = insertelement <2 x i32> poison, i32 %102, i64 0
  %123 = shufflevector <2 x i32> %122, <2 x i32> poison, <2 x i32> zeroinitializer
  %124 = mul <2 x i32> %121, %123
  %shuffle = shufflevector <2 x i32> %124, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %125 = add <4 x i32> %shuffle, %shuffle14
  %126 = insertelement <4 x i32> poison, i32 %103, i64 0
  %shuffle15 = shufflevector <4 x i32> %126, <4 x i32> poison, <4 x i32> zeroinitializer
  %127 = mul <4 x i32> %125, %shuffle15
  %128 = sext <4 x i32> %127 to <4 x i64>
  %129 = extractelement <4 x i64> %128, i64 0
  %130 = getelementptr float, float* %101, i64 %129
  %131 = load float, float* %130, align 4
  %132 = extractelement <4 x i64> %128, i64 1
  %133 = getelementptr float, float* %101, i64 %132
  %134 = load float, float* %133, align 4
  %135 = extractelement <4 x i64> %128, i64 2
  %136 = getelementptr float, float* %101, i64 %135
  %137 = load float, float* %136, align 4
  %138 = extractelement <4 x i64> %128, i64 3
  %139 = getelementptr float, float* %101, i64 %138
  %140 = load float, float* %139, align 4
  %141 = fsub reassoc ninf nsz float 1.000000e+00, %96
  %142 = fmul reassoc ninf nsz float %141, %131
  %143 = fmul reassoc ninf nsz float %96, %134
  %144 = fadd reassoc ninf nsz float %142, %143
  %145 = fmul reassoc ninf nsz float %141, %137
  %146 = fmul reassoc ninf nsz float %96, %140
  %147 = fadd reassoc ninf nsz float %145, %146
  %148 = fsub reassoc ninf nsz float 1.000000e+00, %98
  %149 = fmul reassoc ninf nsz float %144, %148
  %150 = fmul reassoc ninf nsz float %147, %98
  %151 = fadd reassoc ninf nsz float %149, %150
  %152 = add <4 x i32> %127, <i32 1, i32 1, i32 1, i32 1>
  %153 = extractelement <4 x i32> %152, i64 0
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %101, i64 %154
  %156 = load float, float* %155, align 4
  %157 = extractelement <4 x i32> %152, i64 1
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, float* %101, i64 %158
  %160 = load float, float* %159, align 4
  %161 = extractelement <4 x i32> %152, i64 2
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, float* %101, i64 %162
  %164 = load float, float* %163, align 4
  %165 = extractelement <4 x i32> %152, i64 3
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, float* %101, i64 %166
  %168 = load float, float* %167, align 4
  %169 = fmul reassoc ninf nsz float %141, %156
  %170 = fmul reassoc ninf nsz float %96, %160
  %171 = fadd reassoc ninf nsz float %169, %170
  %172 = fmul reassoc ninf nsz float %141, %164
  %173 = fmul reassoc ninf nsz float %96, %168
  %174 = fadd reassoc ninf nsz float %172, %173
  %175 = fmul reassoc ninf nsz float %171, %148
  %176 = fmul reassoc ninf nsz float %174, %98
  %177 = fadd reassoc ninf nsz float %175, %176
  %178 = fmul reassoc ninf nsz float %151, %35
  %179 = fadd reassoc ninf nsz float %178, %85
  %180 = fmul reassoc ninf nsz float %177, %37
  %181 = fadd reassoc ninf nsz float %180, %88
  %182 = tail call reassoc ninf nsz float @llvm.floor.f32(float %179)
  %183 = fptosi float %182 to i32
  %184 = tail call reassoc ninf nsz float @llvm.floor.f32(float %181)
  %185 = fptosi float %184 to i32
  %186 = sitofp i32 %183 to float
  %187 = fsub reassoc ninf nsz float %179, %186
  %188 = sitofp i32 %185 to float
  %189 = fsub reassoc ninf nsz float %181, %188
  %190 = tail call i32 @llvm.abs.i32(i32 %183, i1 true)
  %191 = sub i32 %190, %46
  %192 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %.neg9 = mul i32 %192, -2
  %193 = add i32 %.neg9, %190
  %194 = tail call i32 @llvm.smax.i32(i32 %193, i32 0)
  %195 = tail call i32 @llvm.smin.i32(i32 %46, i32 %194)
  %196 = tail call i32 @llvm.abs.i32(i32 %185, i1 true)
  %197 = sub i32 %196, %47
  %198 = tail call i32 @llvm.smax.i32(i32 %197, i32 0)
  %.neg10 = mul i32 %198, -2
  %199 = add i32 %.neg10, %196
  %200 = tail call i32 @llvm.smax.i32(i32 %199, i32 0)
  %201 = tail call i32 @llvm.smin.i32(i32 %47, i32 %200)
  %202 = add i32 %183, 1
  %203 = tail call i32 @llvm.abs.i32(i32 %202, i1 true)
  %204 = sub i32 %203, %46
  %205 = tail call i32 @llvm.smax.i32(i32 %204, i32 0)
  %.neg11 = mul i32 %205, -2
  %206 = add i32 %.neg11, %203
  %207 = tail call i32 @llvm.smax.i32(i32 %206, i32 0)
  %208 = tail call i32 @llvm.smin.i32(i32 %46, i32 %207)
  %209 = add i32 %185, 1
  %210 = tail call i32 @llvm.abs.i32(i32 %209, i1 true)
  %211 = sub i32 %210, %47
  %212 = tail call i32 @llvm.smax.i32(i32 %211, i32 0)
  %.neg12 = mul i32 %212, -2
  %213 = add i32 %.neg12, %210
  %214 = tail call i32 @llvm.smax.i32(i32 %213, i32 0)
  %215 = tail call i32 @llvm.smin.i32(i32 %47, i32 %214)
  %216 = load float*, float** %56, align 8
  %217 = load i32, i32* %57, align 4
  %218 = mul i32 %201, %217
  %219 = add i32 %218, %195
  %220 = mul i32 %219, 3
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %216, i64 %221
  %223 = load float, float* %222, align 4
  %224 = add i32 %220, 1
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, float* %216, i64 %225
  %227 = load float, float* %226, align 4
  %228 = add i32 %220, 2
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %216, i64 %229
  %231 = load float, float* %230, align 4
  %232 = add i32 %218, %208
  %233 = mul i32 %232, 3
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, float* %216, i64 %234
  %236 = load float, float* %235, align 4
  %237 = add i32 %233, 1
  %238 = sext i32 %237 to i64
  %239 = getelementptr float, float* %216, i64 %238
  %240 = load float, float* %239, align 4
  %241 = add i32 %233, 2
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, float* %216, i64 %242
  %244 = load float, float* %243, align 4
  %245 = mul i32 %215, %217
  %246 = add i32 %245, %195
  %247 = mul i32 %246, 3
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, float* %216, i64 %248
  %250 = load float, float* %249, align 4
  %251 = add i32 %247, 1
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, float* %216, i64 %252
  %254 = load float, float* %253, align 4
  %255 = add i32 %247, 2
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, float* %216, i64 %256
  %258 = load float, float* %257, align 4
  %259 = add i32 %245, %208
  %260 = mul i32 %259, 3
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, float* %216, i64 %261
  %263 = load float, float* %262, align 4
  %264 = add i32 %260, 1
  %265 = sext i32 %264 to i64
  %266 = getelementptr float, float* %216, i64 %265
  %267 = load float, float* %266, align 4
  %268 = add i32 %260, 2
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, float* %216, i64 %269
  %271 = load float, float* %270, align 4
  %272 = fsub reassoc ninf nsz float 1.000000e+00, %187
  %273 = fmul reassoc ninf nsz float %272, %223
  %274 = fmul reassoc ninf nsz float %272, %227
  %275 = fmul reassoc ninf nsz float %272, %231
  %276 = fmul reassoc ninf nsz float %187, %236
  %277 = fmul reassoc ninf nsz float %187, %240
  %278 = fmul reassoc ninf nsz float %187, %244
  %279 = fadd reassoc ninf nsz float %273, %276
  %280 = fadd reassoc ninf nsz float %274, %277
  %281 = fadd reassoc ninf nsz float %275, %278
  %282 = fmul reassoc ninf nsz float %272, %250
  %283 = fmul reassoc ninf nsz float %272, %254
  %284 = fmul reassoc ninf nsz float %272, %258
  %285 = fmul reassoc ninf nsz float %187, %263
  %286 = fmul reassoc ninf nsz float %187, %267
  %287 = fmul reassoc ninf nsz float %187, %271
  %288 = fadd reassoc ninf nsz float %282, %285
  %289 = fadd reassoc ninf nsz float %283, %286
  %290 = fadd reassoc ninf nsz float %284, %287
  %291 = fsub reassoc ninf nsz float 1.000000e+00, %189
  %292 = fmul reassoc ninf nsz float %279, %291
  %293 = fmul reassoc ninf nsz float %280, %291
  %294 = fmul reassoc ninf nsz float %281, %291
  %295 = fmul reassoc ninf nsz float %288, %189
  %296 = fmul reassoc ninf nsz float %289, %189
  %297 = fmul reassoc ninf nsz float %290, %189
  %298 = fadd reassoc ninf nsz float %292, %295
  %299 = fadd reassoc ninf nsz float %293, %296
  %300 = fadd reassoc ninf nsz float %294, %297
  %301 = load float*, float** %58, align 8
  %302 = load i32, i32* %59, align 4
  %303 = sub i32 %302, %70
  %304 = mul i32 %303, 3
  %305 = mul i32 %304, %79
  %306 = add i32 %lsr.iv, %305
  %307 = sext i32 %306 to i64
  %308 = getelementptr float, float* %301, i64 %307
  store float %298, float* %308, align 4
  %309 = load float*, float** %58, align 8
  %310 = load i32, i32* %59, align 4
  %311 = sub i32 %310, %70
  %312 = mul i32 %311, 3
  %313 = mul i32 %312, %79
  %314 = add i32 %lsr.iv, %313
  %315 = add i32 %314, 1
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, float* %309, i64 %316
  store float %299, float* %317, align 4
  %318 = load float*, float** %58, align 8
  %319 = load i32, i32* %59, align 4
  %320 = sub i32 %319, %70
  %321 = mul i32 %320, 3
  %322 = mul i32 %321, %79
  %323 = add i32 %lsr.iv, %322
  %324 = add i32 %323, 2
  %325 = sext i32 %324 to i64
  %326 = getelementptr float, float* %318, i64 %325
  store float %300, float* %326, align 4
  %327 = add nsw i32 %.013, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %327
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
  %4 = alloca %struct.RuntimeContext.192, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.192**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.192*, %struct.RuntimeContext.192** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.192*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.192*, i8*)*, void (%struct.RuntimeContext.192*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.192*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.192*, i8*, i32)*, void (%struct.RuntimeContext.192*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.192*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.192*, i8*)*, void (%struct.RuntimeContext.192*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.192*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.192* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.192* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.192* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.192, %struct.RuntimeContext.192* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.192* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.192* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.192*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.192* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
