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
define void @_upsample_flow_kernel_c264_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 16
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %11 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 8
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %19 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %18, i64 0, i32 1, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %21, i64 0, i32 14
  %23 = load i8*, i8** %22, align 8
  %24 = getelementptr inbounds i8, i8* %23, i64 20
  %25 = bitcast i8* %24 to i32*
  store i32 %20, i32* %25, align 4
  %26 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %26, i64 0, i32 1, i32 0, i32 1
  %28 = load i32, i32* %27, align 4
  %29 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 12
  %33 = bitcast i8* %32 to i32*
  store i32 %28, i32* %33, align 4
  %34 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %35 = tail call i32 @llvm.smax.i32(i32 %28, i32 0)
  %36 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %37 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %36, i64 0, i32 14
  %38 = load i8*, i8** %37, align 8
  %39 = getelementptr inbounds i8, i8* %38, i64 4
  %40 = bitcast i8* %39 to i32*
  store i32 %35, i32* %40, align 4
  %41 = mul i32 %35, %34
  %42 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %43 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %42, i64 0, i32 14
  %44 = bitcast i8** %43 to i32**
  %45 = load i32*, i32** %44, align 8
  store i32 %41, i32* %45, align 4
  ret void
}

; Function Attrs: nounwind
define void @_upsample_flow_kernel_c264_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 2
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.013 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %402, %for_loop_body ]
  %31 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.013, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.013
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.013, 0
  %42 = icmp ne i32 %.013, %38
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg4 = sext i1 %44 to i32
  %45 = add i32 %37, %.neg4
  %46 = mul i32 %36, -1
  %47 = mul i32 %46, %45
  %48 = add i32 %.013, %47
  %49 = sitofp i32 %48 to float
  %50 = getelementptr inbounds i8, i8* %33, i64 8
  %51 = bitcast i8* %50 to i32*
  %52 = load i32, i32* %51, align 4
  %53 = sitofp i32 %52 to float
  %54 = getelementptr inbounds i8, i8* %33, i64 12
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = sitofp i32 %56 to float
  %58 = fmul reassoc ninf nsz float %49, %53
  %59 = fdiv reassoc ninf nsz float %58, %57
  %60 = sitofp i32 %45 to float
  %61 = getelementptr inbounds i8, i8* %33, i64 16
  %62 = bitcast i8* %61 to i32*
  %63 = load i32, i32* %62, align 4
  %64 = sitofp i32 %63 to float
  %65 = getelementptr inbounds i8, i8* %33, i64 20
  %66 = bitcast i8* %65 to i32*
  %67 = load i32, i32* %66, align 4
  %68 = sitofp i32 %67 to float
  %69 = fmul reassoc ninf nsz float %60, %64
  %70 = fdiv reassoc ninf nsz float %69, %68
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %59)
  %72 = fptosi float %71 to i32
  %73 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %74 = fptosi float %73 to i32
  %75 = sitofp i32 %72 to float
  %76 = fsub reassoc ninf nsz float %59, %75
  %77 = sitofp i32 %74 to float
  %78 = fsub reassoc ninf nsz float %70, %77
  %79 = fadd reassoc ninf nsz float %76, 1.000000e+00
  %80 = fmul reassoc ninf nsz float %79, 7.500000e-01
  %81 = fsub reassoc ninf nsz float 3.750000e+00, %80
  %82 = fmul reassoc ninf nsz float %81, %79
  %83 = fadd reassoc ninf nsz float %82, -6.000000e+00
  %84 = fmul reassoc ninf nsz float %83, %79
  %85 = fadd reassoc ninf nsz float %84, 3.000000e+00
  %86 = fmul reassoc ninf nsz float %76, 1.250000e+00
  %87 = fadd reassoc ninf nsz float %86, -2.250000e+00
  %88 = fmul reassoc ninf nsz float %76, %76
  %89 = fmul reassoc ninf nsz float %88, %87
  %90 = fadd reassoc ninf nsz float %89, 1.000000e+00
  %91 = fsub reassoc ninf nsz float 1.000000e+00, %76
  %92 = fmul reassoc ninf nsz float %91, 1.250000e+00
  %93 = fadd reassoc ninf nsz float %92, -2.250000e+00
  %94 = fmul reassoc ninf nsz float %91, %91
  %95 = fmul reassoc ninf nsz float %94, %93
  %96 = fadd reassoc ninf nsz float %95, 1.000000e+00
  %97 = fsub reassoc ninf nsz float 2.000000e+00, %76
  %98 = fmul reassoc ninf nsz float %97, 7.500000e-01
  %99 = fsub reassoc ninf nsz float 3.750000e+00, %98
  %100 = fmul reassoc ninf nsz float %99, %97
  %101 = fadd reassoc ninf nsz float %100, -6.000000e+00
  %102 = fmul reassoc ninf nsz float %101, %97
  %103 = fadd reassoc ninf nsz float %102, 3.000000e+00
  %104 = fadd reassoc ninf nsz float %96, %90
  %105 = fadd reassoc ninf nsz float %104, %85
  %106 = fadd reassoc ninf nsz float %105, %103
  %107 = fdiv reassoc ninf nsz float %85, %106
  %108 = fdiv reassoc ninf nsz float %90, %106
  %109 = fdiv reassoc ninf nsz float %96, %106
  %110 = fdiv reassoc ninf nsz float %103, %106
  %111 = fadd reassoc ninf nsz float %78, 1.000000e+00
  %112 = fmul reassoc ninf nsz float %111, 7.500000e-01
  %113 = fsub reassoc ninf nsz float 3.750000e+00, %112
  %114 = fmul reassoc ninf nsz float %113, %111
  %115 = fadd reassoc ninf nsz float %114, -6.000000e+00
  %116 = fmul reassoc ninf nsz float %115, %111
  %117 = fadd reassoc ninf nsz float %116, 3.000000e+00
  %118 = fmul reassoc ninf nsz float %78, 1.250000e+00
  %119 = fadd reassoc ninf nsz float %118, -2.250000e+00
  %120 = fmul reassoc ninf nsz float %78, %78
  %121 = fmul reassoc ninf nsz float %120, %119
  %122 = fadd reassoc ninf nsz float %121, 1.000000e+00
  %123 = fsub reassoc ninf nsz float 1.000000e+00, %78
  %124 = fmul reassoc ninf nsz float %123, 1.250000e+00
  %125 = fadd reassoc ninf nsz float %124, -2.250000e+00
  %126 = fmul reassoc ninf nsz float %123, %123
  %127 = fmul reassoc ninf nsz float %126, %125
  %128 = fadd reassoc ninf nsz float %127, 1.000000e+00
  %129 = fsub reassoc ninf nsz float 2.000000e+00, %78
  %130 = fmul reassoc ninf nsz float %129, 7.500000e-01
  %131 = fsub reassoc ninf nsz float 3.750000e+00, %130
  %132 = fmul reassoc ninf nsz float %131, %129
  %133 = fadd reassoc ninf nsz float %132, -6.000000e+00
  %134 = fmul reassoc ninf nsz float %133, %129
  %135 = fadd reassoc ninf nsz float %134, 3.000000e+00
  %136 = fadd reassoc ninf nsz float %128, %122
  %137 = fadd reassoc ninf nsz float %136, %117
  %138 = fadd reassoc ninf nsz float %137, %135
  %139 = fdiv reassoc ninf nsz float %117, %138
  %140 = fdiv reassoc ninf nsz float %122, %138
  %141 = fdiv reassoc ninf nsz float %128, %138
  %142 = fdiv reassoc ninf nsz float %135, %138
  %143 = add i32 %74, -1
  %144 = add i32 %63, -1
  %145 = add i32 %72, -1
  %146 = add i32 %52, -1
  %147 = load float*, float** %25, align 8
  %148 = load i32, i32* %26, align 4
  %149 = load i32, i32* %27, align 4
  %150 = add i32 %72, 1
  %151 = add i32 %72, 2
  %152 = insertelement <4 x i32> poison, i32 %145, i64 0
  %153 = insertelement <4 x i32> %152, i32 %72, i64 1
  %154 = insertelement <4 x i32> %153, i32 %150, i64 2
  %155 = insertelement <4 x i32> %154, i32 %151, i64 3
  %156 = call <4 x i32> @llvm.abs.v4i32(<4 x i32> %155, i1 true)
  %157 = insertelement <4 x i32> poison, i32 %146, i64 0
  %shuffle15 = shufflevector <4 x i32> %157, <4 x i32> poison, <4 x i32> zeroinitializer
  %158 = sub <4 x i32> %156, %shuffle15
  %159 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %158, <4 x i32> zeroinitializer)
  %160 = mul <4 x i32> %159, <i32 -2, i32 -2, i32 -2, i32 -2>
  %161 = add <4 x i32> %160, %156
  %162 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %161, <4 x i32> zeroinitializer)
  %163 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle15, <4 x i32> %162)
  %shuffle16 = shufflevector <4 x i32> %163, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 0, i32 1, i32 2, i32 3>
  %164 = insertelement <2 x i32> poison, i32 %143, i64 0
  %165 = insertelement <2 x i32> %164, i32 %74, i64 1
  %166 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %165, i1 true)
  %167 = insertelement <2 x i32> poison, i32 %144, i64 0
  %168 = shufflevector <2 x i32> %167, <2 x i32> poison, <2 x i32> zeroinitializer
  %169 = sub <2 x i32> %166, %168
  %170 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %169, <2 x i32> zeroinitializer)
  %171 = mul <2 x i32> %170, <i32 -2, i32 -2>
  %172 = add <2 x i32> %171, %166
  %173 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %172, <2 x i32> zeroinitializer)
  %174 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %168, <2 x i32> %173)
  %175 = insertelement <2 x i32> poison, i32 %148, i64 0
  %176 = shufflevector <2 x i32> %175, <2 x i32> poison, <2 x i32> zeroinitializer
  %177 = mul <2 x i32> %174, %176
  %shuffle = shufflevector <2 x i32> %177, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1>
  %178 = add <8 x i32> %shuffle, %shuffle16
  %179 = insertelement <8 x i32> poison, i32 %149, i64 0
  %shuffle17 = shufflevector <8 x i32> %179, <8 x i32> poison, <8 x i32> zeroinitializer
  %180 = mul <8 x i32> %178, %shuffle17
  %181 = sext <8 x i32> %180 to <8 x i64>
  %182 = extractelement <8 x i64> %181, i64 0
  %183 = getelementptr float, float* %147, i64 %182
  %184 = load float, float* %183, align 4
  %185 = fmul reassoc ninf nsz float %107, %184
  %186 = extractelement <8 x i64> %181, i64 1
  %187 = getelementptr float, float* %147, i64 %186
  %188 = load float, float* %187, align 4
  %189 = fmul reassoc ninf nsz float %108, %188
  %190 = fadd reassoc ninf nsz float %185, %189
  %191 = extractelement <8 x i64> %181, i64 2
  %192 = getelementptr float, float* %147, i64 %191
  %193 = load float, float* %192, align 4
  %194 = fmul reassoc ninf nsz float %109, %193
  %195 = fadd reassoc ninf nsz float %190, %194
  %196 = extractelement <8 x i64> %181, i64 3
  %197 = getelementptr float, float* %147, i64 %196
  %198 = load float, float* %197, align 4
  %199 = fmul reassoc ninf nsz float %110, %198
  %200 = fadd reassoc ninf nsz float %195, %199
  %201 = fmul reassoc ninf nsz float %200, %139
  %202 = extractelement <8 x i64> %181, i64 4
  %203 = getelementptr float, float* %147, i64 %202
  %204 = load float, float* %203, align 4
  %205 = fmul reassoc ninf nsz float %107, %204
  %206 = extractelement <8 x i64> %181, i64 5
  %207 = getelementptr float, float* %147, i64 %206
  %208 = load float, float* %207, align 4
  %209 = fmul reassoc ninf nsz float %108, %208
  %210 = fadd reassoc ninf nsz float %205, %209
  %211 = extractelement <8 x i64> %181, i64 6
  %212 = getelementptr float, float* %147, i64 %211
  %213 = load float, float* %212, align 4
  %214 = fmul reassoc ninf nsz float %109, %213
  %215 = fadd reassoc ninf nsz float %210, %214
  %216 = extractelement <8 x i64> %181, i64 7
  %217 = getelementptr float, float* %147, i64 %216
  %218 = load float, float* %217, align 4
  %219 = fmul reassoc ninf nsz float %110, %218
  %220 = fadd reassoc ninf nsz float %215, %219
  %221 = fmul reassoc ninf nsz float %220, %140
  %222 = fadd reassoc ninf nsz float %201, %221
  %223 = insertelement <2 x i32> poison, i32 %74, i64 0
  %224 = shufflevector <2 x i32> %223, <2 x i32> poison, <2 x i32> zeroinitializer
  %225 = add <2 x i32> %224, <i32 1, i32 2>
  %226 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %225, i1 true)
  %227 = sub <2 x i32> %226, %168
  %228 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %227, <2 x i32> zeroinitializer)
  %229 = mul <2 x i32> %228, <i32 -2, i32 -2>
  %230 = add <2 x i32> %229, %226
  %231 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %230, <2 x i32> zeroinitializer)
  %232 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %168, <2 x i32> %231)
  %233 = mul <2 x i32> %232, %176
  %shuffle18 = shufflevector <2 x i32> %233, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1>
  %234 = shufflevector <4 x i32> %163, <4 x i32> undef, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 0, i32 1, i32 2, i32 3>
  %235 = add <8 x i32> %shuffle18, %234
  %236 = mul <8 x i32> %235, %shuffle17
  %237 = sext <8 x i32> %236 to <8 x i64>
  %238 = extractelement <8 x i64> %237, i64 0
  %239 = getelementptr float, float* %147, i64 %238
  %240 = load float, float* %239, align 4
  %241 = fmul reassoc ninf nsz float %107, %240
  %242 = extractelement <8 x i64> %237, i64 1
  %243 = getelementptr float, float* %147, i64 %242
  %244 = load float, float* %243, align 4
  %245 = fmul reassoc ninf nsz float %108, %244
  %246 = fadd reassoc ninf nsz float %241, %245
  %247 = extractelement <8 x i64> %237, i64 2
  %248 = getelementptr float, float* %147, i64 %247
  %249 = load float, float* %248, align 4
  %250 = fmul reassoc ninf nsz float %109, %249
  %251 = fadd reassoc ninf nsz float %246, %250
  %252 = extractelement <8 x i64> %237, i64 3
  %253 = getelementptr float, float* %147, i64 %252
  %254 = load float, float* %253, align 4
  %255 = fmul reassoc ninf nsz float %110, %254
  %256 = fadd reassoc ninf nsz float %251, %255
  %257 = fmul reassoc ninf nsz float %256, %141
  %258 = fadd reassoc ninf nsz float %222, %257
  %259 = extractelement <8 x i64> %237, i64 4
  %260 = getelementptr float, float* %147, i64 %259
  %261 = load float, float* %260, align 4
  %262 = fmul reassoc ninf nsz float %107, %261
  %263 = extractelement <8 x i64> %237, i64 5
  %264 = getelementptr float, float* %147, i64 %263
  %265 = load float, float* %264, align 4
  %266 = fmul reassoc ninf nsz float %108, %265
  %267 = fadd reassoc ninf nsz float %262, %266
  %268 = extractelement <8 x i64> %237, i64 6
  %269 = getelementptr float, float* %147, i64 %268
  %270 = load float, float* %269, align 4
  %271 = fmul reassoc ninf nsz float %109, %270
  %272 = fadd reassoc ninf nsz float %267, %271
  %273 = extractelement <8 x i64> %237, i64 7
  %274 = getelementptr float, float* %147, i64 %273
  %275 = load float, float* %274, align 4
  %276 = fmul reassoc ninf nsz float %110, %275
  %277 = fadd reassoc ninf nsz float %272, %276
  %278 = fmul reassoc ninf nsz float %277, %142
  %279 = fadd reassoc ninf nsz float %258, %278
  %280 = add <8 x i32> %180, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %281 = extractelement <8 x i32> %280, i64 0
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, float* %147, i64 %282
  %284 = load float, float* %283, align 4
  %285 = fmul reassoc ninf nsz float %107, %284
  %286 = extractelement <8 x i32> %280, i64 1
  %287 = sext i32 %286 to i64
  %288 = getelementptr float, float* %147, i64 %287
  %289 = load float, float* %288, align 4
  %290 = fmul reassoc ninf nsz float %289, %108
  %291 = fadd reassoc ninf nsz float %285, %290
  %292 = extractelement <8 x i32> %280, i64 2
  %293 = sext i32 %292 to i64
  %294 = getelementptr float, float* %147, i64 %293
  %295 = load float, float* %294, align 4
  %296 = fmul reassoc ninf nsz float %295, %109
  %297 = fadd reassoc ninf nsz float %291, %296
  %298 = extractelement <8 x i32> %280, i64 3
  %299 = sext i32 %298 to i64
  %300 = getelementptr float, float* %147, i64 %299
  %301 = load float, float* %300, align 4
  %302 = fmul reassoc ninf nsz float %301, %110
  %303 = fadd reassoc ninf nsz float %297, %302
  %304 = fmul reassoc ninf nsz float %303, %139
  %305 = extractelement <8 x i32> %280, i64 4
  %306 = sext i32 %305 to i64
  %307 = getelementptr float, float* %147, i64 %306
  %308 = load float, float* %307, align 4
  %309 = fmul reassoc ninf nsz float %308, %107
  %310 = extractelement <8 x i32> %280, i64 5
  %311 = sext i32 %310 to i64
  %312 = getelementptr float, float* %147, i64 %311
  %313 = load float, float* %312, align 4
  %314 = fmul reassoc ninf nsz float %313, %108
  %315 = fadd reassoc ninf nsz float %314, %309
  %316 = extractelement <8 x i32> %280, i64 6
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, float* %147, i64 %317
  %319 = load float, float* %318, align 4
  %320 = fmul reassoc ninf nsz float %319, %109
  %321 = fadd reassoc ninf nsz float %315, %320
  %322 = extractelement <8 x i32> %280, i64 7
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, float* %147, i64 %323
  %325 = load float, float* %324, align 4
  %326 = fmul reassoc ninf nsz float %325, %110
  %327 = fadd reassoc ninf nsz float %321, %326
  %328 = fmul reassoc ninf nsz float %327, %140
  %329 = fadd reassoc ninf nsz float %328, %304
  %330 = add <8 x i32> %236, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %331 = extractelement <8 x i32> %330, i64 0
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, float* %147, i64 %332
  %334 = load float, float* %333, align 4
  %335 = fmul reassoc ninf nsz float %334, %107
  %336 = extractelement <8 x i32> %330, i64 1
  %337 = sext i32 %336 to i64
  %338 = getelementptr float, float* %147, i64 %337
  %339 = load float, float* %338, align 4
  %340 = fmul reassoc ninf nsz float %339, %108
  %341 = fadd reassoc ninf nsz float %340, %335
  %342 = extractelement <8 x i32> %330, i64 2
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, float* %147, i64 %343
  %345 = load float, float* %344, align 4
  %346 = fmul reassoc ninf nsz float %345, %109
  %347 = fadd reassoc ninf nsz float %341, %346
  %348 = extractelement <8 x i32> %330, i64 3
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, float* %147, i64 %349
  %351 = load float, float* %350, align 4
  %352 = fmul reassoc ninf nsz float %351, %110
  %353 = fadd reassoc ninf nsz float %347, %352
  %354 = fmul reassoc ninf nsz float %353, %141
  %355 = fadd reassoc ninf nsz float %329, %354
  %356 = extractelement <8 x i32> %330, i64 4
  %357 = sext i32 %356 to i64
  %358 = getelementptr float, float* %147, i64 %357
  %359 = load float, float* %358, align 4
  %360 = fmul reassoc ninf nsz float %359, %107
  %361 = extractelement <8 x i32> %330, i64 5
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, float* %147, i64 %362
  %364 = load float, float* %363, align 4
  %365 = fmul reassoc ninf nsz float %364, %108
  %366 = fadd reassoc ninf nsz float %365, %360
  %367 = extractelement <8 x i32> %330, i64 6
  %368 = sext i32 %367 to i64
  %369 = getelementptr float, float* %147, i64 %368
  %370 = load float, float* %369, align 4
  %371 = fmul reassoc ninf nsz float %370, %109
  %372 = fadd reassoc ninf nsz float %366, %371
  %373 = extractelement <8 x i32> %330, i64 7
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, float* %147, i64 %374
  %376 = load float, float* %375, align 4
  %377 = fmul reassoc ninf nsz float %376, %110
  %378 = fadd reassoc ninf nsz float %372, %377
  %379 = fmul reassoc ninf nsz float %378, %142
  %380 = fadd reassoc ninf nsz float %355, %379
  %381 = fmul reassoc ninf nsz float %279, %23
  %382 = load float*, float** %28, align 8
  %383 = load i32, i32* %29, align 4
  %384 = load i32, i32* %30, align 4
  %385 = sub i32 %383, %36
  %386 = mul i32 %385, %45
  %387 = add i32 %.013, %386
  %388 = mul i32 %387, %384
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, float* %382, i64 %389
  store float %381, float* %390, align 4
  %391 = fmul reassoc ninf nsz float %380, %23
  %392 = load float*, float** %28, align 8
  %393 = load i32, i32* %29, align 4
  %394 = load i32, i32* %30, align 4
  %395 = sub i32 %393, %36
  %396 = mul i32 %395, %45
  %397 = add i32 %.013, %396
  %398 = mul i32 %397, %394
  %399 = add i32 %398, 1
  %400 = sext i32 %399 to i64
  %401 = getelementptr float, float* %392, i64 %400
  store float %391, float* %401, align 4
  %402 = add nsw i32 %.013, 1
  %exitcond.not = icmp eq i32 %19, %402
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.abs.v4i32(<4 x i32>, i1 immarg) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #7

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
