; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.24*, void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.24 = type { i8*, %struct.LLVMRuntime.23*, i32, i64* }
%struct.LLVMRuntime.23 = type { %struct.PreallocatedMemoryChunk.19, %struct.PreallocatedMemoryChunk.19, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.20*], [1024 x %struct.NodeManager.21*], [1024 x i8*], i8*, %struct.RandState.22*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.19 = type { i8*, i8*, i64 }
%struct.ListManager.20 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.23* }
%struct.NodeManager.21 = type { %struct.LLVMRuntime.23*, i32, i32, i32, i32, %struct.ListManager.20*, %struct.ListManager.20*, %struct.ListManager.20*, i32 }
%struct.RandState.22 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_clahe_interpolate_kernel_c388_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %1, i64 0, i32 4
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_clahe_interpolate_kernel_c388_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.24* %context, %struct.RuntimeContext.24** %4, align 8
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.24*, i8*, i32)* @function_body, void (%struct.RuntimeContext.24*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 9
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 10
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 6
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 5
  %29 = load i32, i32* %28, align 4
  %30 = sitofp i32 %25 to float
  %31 = add i32 %25, -1
  %32 = sitofp i32 %27 to float
  %33 = sitofp i32 %29 to float
  %34 = fmul reassoc ninf nsz float %32, 5.000000e-01
  %35 = fmul reassoc ninf nsz float %33, 5.000000e-01
  %36 = sitofp i32 %31 to float
  %37 = icmp slt i32 %17, %19
  br i1 %37, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 8
  %39 = load i32, i32* %38, align 4
  %40 = add i32 %39, -1
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 7
  %42 = load i32, i32* %41, align 4
  %43 = add i32 %42, -1
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 0, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 1, i32 1
  %47 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 2, i32 1
  %49 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %50 = insertelement <2 x i32> poison, i32 %40, i64 0
  %51 = shufflevector <2 x i32> %50, <2 x i32> poison, <2 x i32> zeroinitializer
  %52 = insertelement <2 x i32> poison, i32 %42, i64 0
  %53 = shufflevector <2 x i32> %52, <2 x i32> poison, <2 x i32> zeroinitializer
  %54 = insertelement <2 x i32> poison, i32 %43, i64 0
  %55 = shufflevector <2 x i32> %54, <2 x i32> poison, <2 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.06 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %155, %for_loop_body ]
  %56 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %57 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %56, i64 0, i32 14
  %58 = load i8*, i8** %57, align 8
  %59 = getelementptr inbounds i8, i8* %58, i64 4
  %60 = bitcast i8* %59 to i32*
  %61 = load i32, i32* %60, align 4
  %62 = sdiv i32 %.06, %61
  %63 = mul i32 %62, %61
  %64 = xor i32 %61, %.06
  %65 = icmp slt i32 %64, 0
  %66 = icmp ne i32 %.06, 0
  %67 = icmp ne i32 %.06, %63
  %68 = and i1 %66, %65
  %69 = and i1 %68, %67
  %.neg4 = sext i1 %69 to i32
  %70 = add i32 %62, %.neg4
  %71 = mul i32 %61, -1
  %72 = mul i32 %71, %70
  %73 = add i32 %.06, %72
  %74 = load float*, float** %44, align 8
  %75 = load i32, i32* %45, align 4
  %76 = sub i32 %75, %61
  %77 = mul i32 %76, %70
  %78 = add i32 %.06, %77
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, float* %74, i64 %79
  %81 = load float, float* %80, align 4
  %82 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %81, float 0.000000e+00)
  %83 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %23, float %82)
  %84 = fmul reassoc ninf nsz float %83, %30
  %85 = fdiv reassoc ninf nsz float %84, %23
  %86 = fptosi float %85 to i32
  %87 = tail call i32 @llvm.smin.i32(i32 %86, i32 %31)
  %88 = sitofp i32 %73 to float
  %89 = fsub reassoc ninf nsz float %88, %34
  %90 = fdiv reassoc ninf nsz float %89, %32
  %91 = sitofp i32 %70 to float
  %92 = fsub reassoc ninf nsz float %91, %35
  %93 = fdiv reassoc ninf nsz float %92, %33
  %94 = tail call reassoc ninf nsz float @llvm.floor.f32(float %90)
  %95 = fptosi float %94 to i32
  %96 = tail call reassoc ninf nsz float @llvm.floor.f32(float %93)
  %97 = fptosi float %96 to i32
  %98 = add i32 %95, 1
  %99 = add i32 %97, 1
  %100 = sitofp i32 %95 to float
  %101 = fsub reassoc ninf nsz float %90, %100
  %102 = sitofp i32 %97 to float
  %103 = fsub reassoc ninf nsz float %93, %102
  %104 = load float*, float** %46, align 8
  %105 = load i32, i32* %47, align 4
  %106 = insertelement <2 x i32> poison, i32 %95, i64 0
  %107 = insertelement <2 x i32> %106, i32 %98, i64 1
  %108 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %107, <2 x i32> zeroinitializer)
  %109 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %55, <2 x i32> %108)
  %shuffle7 = shufflevector <2 x i32> %109, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %110 = insertelement <2 x i32> poison, i32 %97, i64 0
  %111 = insertelement <2 x i32> %110, i32 %99, i64 1
  %112 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %111, <2 x i32> zeroinitializer)
  %113 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %51, <2 x i32> %112)
  %114 = mul <2 x i32> %113, %53
  %shuffle = shufflevector <2 x i32> %114, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %115 = add <4 x i32> %shuffle, %shuffle7
  %116 = insertelement <4 x i32> poison, i32 %105, i64 0
  %shuffle8 = shufflevector <4 x i32> %116, <4 x i32> poison, <4 x i32> zeroinitializer
  %117 = mul <4 x i32> %115, %shuffle8
  %118 = insertelement <4 x i32> poison, i32 %87, i64 0
  %shuffle9 = shufflevector <4 x i32> %118, <4 x i32> poison, <4 x i32> zeroinitializer
  %119 = add <4 x i32> %117, %shuffle9
  %120 = extractelement <4 x i32> %119, i64 0
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, float* %104, i64 %121
  %123 = load float, float* %122, align 4
  %124 = extractelement <4 x i32> %119, i64 1
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %104, i64 %125
  %127 = load float, float* %126, align 4
  %128 = extractelement <4 x i32> %119, i64 2
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %104, i64 %129
  %131 = load float, float* %130, align 4
  %132 = extractelement <4 x i32> %119, i64 3
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %104, i64 %133
  %135 = load float, float* %134, align 4
  %136 = fsub reassoc ninf nsz float 1.000000e+00, %101
  %137 = fmul reassoc ninf nsz float %136, %123
  %138 = fmul reassoc ninf nsz float %101, %127
  %139 = fadd reassoc ninf nsz float %137, %138
  %140 = fmul reassoc ninf nsz float %136, %131
  %141 = fmul reassoc ninf nsz float %101, %135
  %142 = fadd reassoc ninf nsz float %140, %141
  %143 = fsub reassoc ninf nsz float %142, %139
  %144 = fmul reassoc ninf nsz float %143, %103
  %145 = fadd reassoc ninf nsz float %144, %139
  %146 = fmul reassoc ninf nsz float %145, %23
  %147 = fdiv reassoc ninf nsz float %146, %36
  %148 = load float*, float** %48, align 8
  %149 = load i32, i32* %49, align 4
  %150 = sub i32 %149, %61
  %151 = mul i32 %150, %70
  %152 = add i32 %.06, %151
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %148, i64 %153
  store float %147, float* %154, align 4
  %155 = add nsw i32 %.06, 1
  %exitcond.not = icmp eq i32 %19, %155
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.24, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.24**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.24*, %struct.RuntimeContext.24** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.24* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.24* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
