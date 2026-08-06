; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.60*, void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.60 = type { i8*, %struct.LLVMRuntime.59*, i32, i64* }
%struct.LLVMRuntime.59 = type { %struct.PreallocatedMemoryChunk.55, %struct.PreallocatedMemoryChunk.55, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.56*], [1024 x %struct.NodeManager.57*], [1024 x i8*], i8*, %struct.RandState.58*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.55 = type { i8*, i8*, i64 }
%struct.ListManager.56 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.59* }
%struct.NodeManager.57 = type { %struct.LLVMRuntime.59*, i32, i32, i32, i32, %struct.ListManager.56*, %struct.ListManager.56*, %struct.ListManager.56*, i32 }
%struct.RandState.58 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_build_flow_maps_from_2ch_kernel_c302_0_kernel_0_serial(%struct.RuntimeContext.60* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.60* %context to { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %1, i64 0, i32 5
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %11, i64 0, i32 6
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 8
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_build_flow_maps_from_2ch_kernel_c302_0_kernel_1_range_for(%struct.RuntimeContext.60* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.60* %context, %struct.RuntimeContext.60** %4, align 8
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.60*, i8*, i32)* @function_body, void (%struct.RuntimeContext.60*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.60* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.60* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 4
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 3
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 7
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 8
  %29 = load float, float* %28, align 4
  %30 = add i32 %23, -1
  %31 = add i32 %25, -1
  %32 = sitofp i32 %30 to float
  %33 = sitofp i32 %31 to float
  %34 = icmp slt i32 %17, %19
  br i1 %34, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %35 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %36 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %37 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 2
  %38 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %39 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %40 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %41 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %42 = insertelement <2 x i32> poison, i32 %31, i64 0
  %43 = shufflevector <2 x i32> %42, <2 x i32> poison, <2 x i32> zeroinitializer
  %44 = insertelement <2 x i32> poison, i32 %30, i64 0
  %45 = shufflevector <2 x i32> %44, <2 x i32> poison, <2 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.09 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %185, %for_loop_body ]
  %46 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %47 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %46, i64 0, i32 14
  %48 = load i8*, i8** %47, align 8
  %49 = getelementptr inbounds i8, i8* %48, i64 4
  %50 = bitcast i8* %49 to i32*
  %51 = load i32, i32* %50, align 4
  %52 = sdiv i32 %.09, %51
  %53 = mul i32 %52, %51
  %54 = xor i32 %51, %.09
  %55 = icmp slt i32 %54, 0
  %56 = icmp ne i32 %.09, 0
  %57 = icmp ne i32 %.09, %53
  %58 = and i1 %56, %55
  %59 = and i1 %58, %57
  %.neg4 = sext i1 %59 to i32
  %60 = add i32 %52, %.neg4
  %61 = mul i32 %51, -1
  %62 = mul i32 %61, %60
  %63 = add i32 %.09, %62
  %64 = sitofp i32 %63 to float
  %65 = fmul reassoc ninf nsz float %64, %32
  %66 = getelementptr inbounds i8, i8* %48, i64 8
  %67 = bitcast i8* %66 to i32*
  %68 = load i32, i32* %67, align 4
  %69 = add i32 %68, -1
  %70 = sitofp i32 %69 to float
  %71 = fdiv reassoc ninf nsz float %65, %70
  %72 = sitofp i32 %60 to float
  %73 = fmul reassoc ninf nsz float %72, %33
  %74 = getelementptr inbounds i8, i8* %48, i64 12
  %75 = bitcast i8* %74 to i32*
  %76 = load i32, i32* %75, align 4
  %77 = add i32 %76, -1
  %78 = sitofp i32 %77 to float
  %79 = fdiv reassoc ninf nsz float %73, %78
  %80 = tail call reassoc ninf nsz float @llvm.floor.f32(float %71)
  %81 = fptosi float %80 to i32
  %82 = tail call reassoc ninf nsz float @llvm.floor.f32(float %79)
  %83 = fptosi float %82 to i32
  %84 = sitofp i32 %81 to float
  %85 = fsub reassoc ninf nsz float %71, %84
  %86 = sitofp i32 %83 to float
  %87 = fsub reassoc ninf nsz float %79, %86
  %88 = add i32 %81, 1
  %89 = add i32 %83, 1
  %90 = load float*, float** %35, align 8
  %91 = load i32, i32* %36, align 4
  %92 = load i32, i32* %37, align 4
  %93 = insertelement <2 x i32> poison, i32 %81, i64 0
  %94 = insertelement <2 x i32> %93, i32 %88, i64 1
  %95 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %94, i1 true)
  %96 = sub <2 x i32> %95, %45
  %97 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %96, <2 x i32> zeroinitializer)
  %98 = mul <2 x i32> %97, <i32 -2, i32 -2>
  %99 = add <2 x i32> %98, %95
  %100 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %99, <2 x i32> zeroinitializer)
  %101 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %45, <2 x i32> %100)
  %shuffle10 = shufflevector <2 x i32> %101, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %102 = insertelement <2 x i32> poison, i32 %83, i64 0
  %103 = insertelement <2 x i32> %102, i32 %89, i64 1
  %104 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %103, i1 true)
  %105 = sub <2 x i32> %104, %43
  %106 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %105, <2 x i32> zeroinitializer)
  %107 = mul <2 x i32> %106, <i32 -2, i32 -2>
  %108 = add <2 x i32> %107, %104
  %109 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %108, <2 x i32> zeroinitializer)
  %110 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %43, <2 x i32> %109)
  %111 = insertelement <2 x i32> poison, i32 %91, i64 0
  %112 = shufflevector <2 x i32> %111, <2 x i32> poison, <2 x i32> zeroinitializer
  %113 = mul <2 x i32> %110, %112
  %shuffle = shufflevector <2 x i32> %113, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %114 = add <4 x i32> %shuffle, %shuffle10
  %115 = insertelement <4 x i32> poison, i32 %92, i64 0
  %shuffle11 = shufflevector <4 x i32> %115, <4 x i32> poison, <4 x i32> zeroinitializer
  %116 = mul <4 x i32> %114, %shuffle11
  %117 = sext <4 x i32> %116 to <4 x i64>
  %118 = extractelement <4 x i64> %117, i64 0
  %119 = getelementptr float, float* %90, i64 %118
  %120 = load float, float* %119, align 4
  %121 = extractelement <4 x i64> %117, i64 1
  %122 = getelementptr float, float* %90, i64 %121
  %123 = load float, float* %122, align 4
  %124 = extractelement <4 x i64> %117, i64 2
  %125 = getelementptr float, float* %90, i64 %124
  %126 = load float, float* %125, align 4
  %127 = extractelement <4 x i64> %117, i64 3
  %128 = getelementptr float, float* %90, i64 %127
  %129 = load float, float* %128, align 4
  %130 = fsub reassoc ninf nsz float 1.000000e+00, %85
  %131 = fmul reassoc ninf nsz float %130, %120
  %132 = fmul reassoc ninf nsz float %85, %123
  %133 = fadd reassoc ninf nsz float %131, %132
  %134 = fmul reassoc ninf nsz float %130, %126
  %135 = fmul reassoc ninf nsz float %85, %129
  %136 = fadd reassoc ninf nsz float %134, %135
  %137 = fsub reassoc ninf nsz float 1.000000e+00, %87
  %138 = fmul reassoc ninf nsz float %133, %137
  %139 = fmul reassoc ninf nsz float %136, %87
  %140 = fadd reassoc ninf nsz float %138, %139
  %141 = add <4 x i32> %116, <i32 1, i32 1, i32 1, i32 1>
  %142 = extractelement <4 x i32> %141, i64 0
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %90, i64 %143
  %145 = load float, float* %144, align 4
  %146 = extractelement <4 x i32> %141, i64 1
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %90, i64 %147
  %149 = load float, float* %148, align 4
  %150 = extractelement <4 x i32> %141, i64 2
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %90, i64 %151
  %153 = load float, float* %152, align 4
  %154 = extractelement <4 x i32> %141, i64 3
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %90, i64 %155
  %157 = load float, float* %156, align 4
  %158 = fmul reassoc ninf nsz float %130, %145
  %159 = fmul reassoc ninf nsz float %85, %149
  %160 = fadd reassoc ninf nsz float %158, %159
  %161 = fmul reassoc ninf nsz float %130, %153
  %162 = fmul reassoc ninf nsz float %85, %157
  %163 = fadd reassoc ninf nsz float %161, %162
  %164 = fmul reassoc ninf nsz float %160, %137
  %165 = fmul reassoc ninf nsz float %163, %87
  %166 = fadd reassoc ninf nsz float %164, %165
  %167 = fmul reassoc ninf nsz float %140, %27
  %168 = fadd reassoc ninf nsz float %167, %64
  %169 = load float*, float** %38, align 8
  %170 = load i32, i32* %39, align 4
  %171 = sub i32 %170, %51
  %172 = mul i32 %171, %60
  %173 = add i32 %.09, %172
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, float* %169, i64 %174
  store float %168, float* %175, align 4
  %176 = fmul reassoc ninf nsz float %166, %29
  %177 = fadd reassoc ninf nsz float %176, %72
  %178 = load float*, float** %40, align 8
  %179 = load i32, i32* %41, align 4
  %180 = sub i32 %179, %51
  %181 = mul i32 %180, %60
  %182 = add i32 %.09, %181
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, float* %178, i64 %183
  store float %177, float* %184, align 4
  %185 = add nsw i32 %.09, 1
  %exitcond.not = icmp eq i32 %19, %185
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
  %4 = alloca %struct.RuntimeContext.60, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.60**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.60*, %struct.RuntimeContext.60** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.60* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.60* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
