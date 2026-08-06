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
define void @_bicubic_resize_kernel_2d_c140_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 4
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %11, i64 0, i32 5
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bicubic_resize_kernel_2d_c140_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %25 = load i32, i32* %24, align 4
  %26 = sitofp i32 %23 to float
  %27 = sitofp i32 %25 to float
  %28 = icmp slt i32 %17, %19
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = add i32 %25, -1
  %30 = add i32 %23, -1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %35 = insertelement <2 x i32> poison, i32 %30, i64 0
  %36 = shufflevector <2 x i32> %35, <2 x i32> poison, <2 x i32> zeroinitializer
  %37 = insertelement <4 x i32> poison, i32 %29, i64 0
  %shuffle18 = shufflevector <4 x i32> %37, <4 x i32> poison, <4 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.017 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %258, %for_loop_body ]
  %38 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  %43 = load i32, i32* %42, align 4
  %44 = sdiv i32 %.017, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.017
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %.017, 0
  %49 = icmp ne i32 %.017, %45
  %50 = and i1 %48, %47
  %51 = and i1 %50, %49
  %.neg4 = sext i1 %51 to i32
  %52 = add i32 %44, %.neg4
  %53 = mul i32 %43, -1
  %54 = mul i32 %53, %52
  %55 = add i32 %.017, %54
  %56 = sitofp i32 %52 to float
  %57 = fadd reassoc ninf nsz float %56, 5.000000e-01
  %58 = getelementptr inbounds i8, i8* %40, i64 8
  %59 = bitcast i8* %58 to i32*
  %60 = load i32, i32* %59, align 4
  %61 = sitofp i32 %60 to float
  %62 = fmul reassoc ninf nsz float %57, %26
  %63 = fdiv reassoc ninf nsz float %62, %61
  %64 = fadd reassoc ninf nsz float %63, -5.000000e-01
  %65 = sitofp i32 %55 to float
  %66 = fadd reassoc ninf nsz float %65, 5.000000e-01
  %67 = getelementptr inbounds i8, i8* %40, i64 12
  %68 = bitcast i8* %67 to i32*
  %69 = load i32, i32* %68, align 4
  %70 = sitofp i32 %69 to float
  %71 = fmul reassoc ninf nsz float %66, %27
  %72 = fdiv reassoc ninf nsz float %71, %70
  %73 = fadd reassoc ninf nsz float %72, -5.000000e-01
  %74 = tail call reassoc ninf nsz float @llvm.floor.f32(float %73)
  %75 = fptosi float %74 to i32
  %76 = tail call reassoc ninf nsz float @llvm.floor.f32(float %64)
  %77 = fptosi float %76 to i32
  %78 = sitofp i32 %75 to float
  %79 = fsub reassoc ninf nsz float %73, %78
  %80 = sitofp i32 %77 to float
  %81 = fsub reassoc ninf nsz float %64, %80
  %82 = tail call float @llvm.fabs.f32(float %79)
  %83 = fadd reassoc ninf nsz float %82, 1.000000e+00
  %84 = fmul reassoc ninf nsz float %83, %83
  %85 = fmul reassoc ninf nsz float %83, 7.500000e-01
  %86 = fmul reassoc ninf nsz float %83, -6.000000e+00
  %87 = fsub reassoc ninf nsz float 3.750000e+00, %85
  %reass.mul = fmul reassoc ninf nsz float %84, %87
  %88 = fadd reassoc ninf nsz float %86, 3.000000e+00
  %89 = fadd reassoc ninf nsz float %88, %reass.mul
  %90 = fmul reassoc ninf nsz float %79, %79
  %91 = fmul reassoc ninf nsz float %90, 1.250000e+00
  %92 = fmul reassoc ninf nsz float %91, %82
  %93 = fmul reassoc ninf nsz float %90, 2.250000e+00
  %94 = fsub reassoc ninf nsz float %92, %93
  %95 = fadd reassoc ninf nsz float %94, 1.000000e+00
  %96 = fsub reassoc ninf nsz float 1.000000e+00, %82
  %97 = fmul reassoc ninf nsz float %96, %96
  %98 = fmul reassoc ninf nsz float %96, 1.250000e+00
  %99 = fadd reassoc ninf nsz float %98, -2.250000e+00
  %100 = fmul reassoc ninf nsz float %99, %97
  %101 = fadd reassoc ninf nsz float %100, 1.000000e+00
  %102 = fsub reassoc ninf nsz float 2.000000e+00, %82
  %103 = fmul reassoc ninf nsz float %102, %102
  %104 = fmul reassoc ninf nsz float %102, 7.500000e-01
  %105 = fmul reassoc ninf nsz float %102, -6.000000e+00
  %106 = fsub reassoc ninf nsz float 3.750000e+00, %104
  %reass.mul8 = fmul reassoc ninf nsz float %103, %106
  %107 = fadd reassoc ninf nsz float %105, 3.000000e+00
  %108 = fadd reassoc ninf nsz float %107, %reass.mul8
  %109 = tail call float @llvm.fabs.f32(float %81)
  %110 = fadd reassoc ninf nsz float %109, 1.000000e+00
  %111 = fmul reassoc ninf nsz float %110, %110
  %112 = fmul reassoc ninf nsz float %110, 7.500000e-01
  %113 = fmul reassoc ninf nsz float %110, -6.000000e+00
  %114 = fsub reassoc ninf nsz float 3.750000e+00, %112
  %reass.mul10 = fmul reassoc ninf nsz float %111, %114
  %115 = fadd reassoc ninf nsz float %113, 3.000000e+00
  %116 = fadd reassoc ninf nsz float %115, %reass.mul10
  %117 = fmul reassoc ninf nsz float %81, %81
  %118 = fmul reassoc ninf nsz float %109, 1.250000e+00
  %reass.add11 = fadd reassoc ninf nsz float %118, -2.250000e+00
  %reass.mul12 = fmul reassoc ninf nsz float %117, %reass.add11
  %119 = fadd reassoc ninf nsz float %reass.mul12, 1.000000e+00
  %120 = fsub reassoc ninf nsz float 1.000000e+00, %109
  %121 = fmul reassoc ninf nsz float %120, %120
  %122 = fmul reassoc ninf nsz float %120, 1.250000e+00
  %reass.add13 = fadd reassoc ninf nsz float %122, -2.250000e+00
  %reass.mul14 = fmul reassoc ninf nsz float %121, %reass.add13
  %123 = fadd reassoc ninf nsz float %reass.mul14, 1.000000e+00
  %124 = fsub reassoc ninf nsz float 2.000000e+00, %109
  %125 = fmul reassoc ninf nsz float %124, %124
  %126 = fmul reassoc ninf nsz float %124, 7.500000e-01
  %127 = fmul reassoc ninf nsz float %124, -6.000000e+00
  %128 = fsub reassoc ninf nsz float 3.750000e+00, %126
  %reass.mul16 = fmul reassoc ninf nsz float %125, %128
  %129 = fadd reassoc ninf nsz float %127, 3.000000e+00
  %130 = fadd reassoc ninf nsz float %129, %reass.mul16
  %131 = add i32 %77, -1
  %132 = add i32 %75, -1
  %133 = load float*, float** %31, align 8
  %134 = load i32, i32* %32, align 4
  %135 = add i32 %75, 1
  %136 = add i32 %75, 2
  %137 = insertelement <4 x i32> poison, i32 %132, i64 0
  %138 = insertelement <4 x i32> %137, i32 %75, i64 1
  %139 = insertelement <4 x i32> %138, i32 %135, i64 2
  %140 = insertelement <4 x i32> %139, i32 %136, i64 3
  %141 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %140, <4 x i32> zeroinitializer)
  %142 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle18, <4 x i32> %141)
  %shuffle19 = shufflevector <4 x i32> %142, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 0, i32 1, i32 2, i32 3>
  %143 = insertelement <2 x i32> poison, i32 %131, i64 0
  %144 = insertelement <2 x i32> %143, i32 %77, i64 1
  %145 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %144, <2 x i32> zeroinitializer)
  %146 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %36, <2 x i32> %145)
  %147 = insertelement <2 x i32> poison, i32 %134, i64 0
  %148 = shufflevector <2 x i32> %147, <2 x i32> poison, <2 x i32> zeroinitializer
  %149 = mul <2 x i32> %146, %148
  %shuffle = shufflevector <2 x i32> %149, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1>
  %150 = add <8 x i32> %shuffle, %shuffle19
  %151 = sext <8 x i32> %150 to <8 x i64>
  %152 = extractelement <8 x i64> %151, i64 0
  %153 = getelementptr float, float* %133, i64 %152
  %154 = load float, float* %153, align 4
  %155 = fmul reassoc ninf nsz float %89, %154
  %156 = extractelement <8 x i64> %151, i64 1
  %157 = getelementptr float, float* %133, i64 %156
  %158 = load float, float* %157, align 4
  %159 = fmul reassoc ninf nsz float %95, %158
  %160 = extractelement <8 x i64> %151, i64 2
  %161 = getelementptr float, float* %133, i64 %160
  %162 = load float, float* %161, align 4
  %163 = fmul reassoc ninf nsz float %101, %162
  %164 = extractelement <8 x i64> %151, i64 3
  %165 = getelementptr float, float* %133, i64 %164
  %166 = load float, float* %165, align 4
  %167 = fmul reassoc ninf nsz float %108, %166
  %168 = fadd reassoc ninf nsz float %163, %159
  %169 = fadd reassoc ninf nsz float %168, %155
  %170 = fadd reassoc ninf nsz float %169, %167
  %171 = fmul reassoc ninf nsz float %170, %116
  %172 = extractelement <8 x i64> %151, i64 4
  %173 = getelementptr float, float* %133, i64 %172
  %174 = load float, float* %173, align 4
  %175 = fmul reassoc ninf nsz float %89, %174
  %176 = extractelement <8 x i64> %151, i64 5
  %177 = getelementptr float, float* %133, i64 %176
  %178 = load float, float* %177, align 4
  %179 = fmul reassoc ninf nsz float %95, %178
  %180 = extractelement <8 x i64> %151, i64 6
  %181 = getelementptr float, float* %133, i64 %180
  %182 = load float, float* %181, align 4
  %183 = fmul reassoc ninf nsz float %101, %182
  %184 = extractelement <8 x i64> %151, i64 7
  %185 = getelementptr float, float* %133, i64 %184
  %186 = load float, float* %185, align 4
  %187 = fmul reassoc ninf nsz float %108, %186
  %188 = fadd reassoc ninf nsz float %183, %179
  %189 = fadd reassoc ninf nsz float %188, %175
  %190 = fadd reassoc ninf nsz float %189, %187
  %191 = fmul reassoc ninf nsz float %190, %119
  %192 = fadd reassoc ninf nsz float %171, %191
  %193 = insertelement <2 x i32> poison, i32 %77, i64 0
  %194 = shufflevector <2 x i32> %193, <2 x i32> poison, <2 x i32> zeroinitializer
  %195 = add <2 x i32> %194, <i32 1, i32 2>
  %196 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %195, <2 x i32> zeroinitializer)
  %197 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %36, <2 x i32> %196)
  %198 = mul <2 x i32> %197, %148
  %shuffle20 = shufflevector <2 x i32> %198, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1>
  %199 = shufflevector <4 x i32> %142, <4 x i32> undef, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 0, i32 1, i32 2, i32 3>
  %200 = add <8 x i32> %shuffle20, %199
  %201 = extractelement <8 x i32> %200, i64 0
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %133, i64 %202
  %204 = load float, float* %203, align 4
  %205 = fmul reassoc ninf nsz float %89, %204
  %206 = extractelement <8 x i32> %200, i64 1
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, float* %133, i64 %207
  %209 = load float, float* %208, align 4
  %210 = fmul reassoc ninf nsz float %95, %209
  %211 = extractelement <8 x i32> %200, i64 2
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, float* %133, i64 %212
  %214 = load float, float* %213, align 4
  %215 = fmul reassoc ninf nsz float %101, %214
  %216 = extractelement <8 x i32> %200, i64 3
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, float* %133, i64 %217
  %219 = load float, float* %218, align 4
  %220 = fmul reassoc ninf nsz float %108, %219
  %221 = fadd reassoc ninf nsz float %215, %210
  %222 = fadd reassoc ninf nsz float %221, %205
  %223 = fadd reassoc ninf nsz float %222, %220
  %224 = fmul reassoc ninf nsz float %223, %123
  %225 = fadd reassoc ninf nsz float %192, %224
  %226 = extractelement <8 x i32> %200, i64 4
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, float* %133, i64 %227
  %229 = load float, float* %228, align 4
  %230 = fmul reassoc ninf nsz float %89, %229
  %231 = extractelement <8 x i32> %200, i64 5
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, float* %133, i64 %232
  %234 = load float, float* %233, align 4
  %235 = fmul reassoc ninf nsz float %95, %234
  %236 = extractelement <8 x i32> %200, i64 6
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, float* %133, i64 %237
  %239 = load float, float* %238, align 4
  %240 = fmul reassoc ninf nsz float %101, %239
  %241 = extractelement <8 x i32> %200, i64 7
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, float* %133, i64 %242
  %244 = load float, float* %243, align 4
  %245 = fmul reassoc ninf nsz float %108, %244
  %246 = fadd reassoc ninf nsz float %240, %235
  %247 = fadd reassoc ninf nsz float %246, %230
  %248 = fadd reassoc ninf nsz float %247, %245
  %249 = fmul reassoc ninf nsz float %248, %130
  %250 = fadd reassoc ninf nsz float %225, %249
  %251 = load float*, float** %33, align 8
  %252 = load i32, i32* %34, align 4
  %253 = sub i32 %252, %43
  %254 = mul i32 %253, %52
  %255 = add i32 %.017, %254
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, float* %251, i64 %256
  store float %250, float* %257, align 4
  %258 = add nsw i32 %.017, 1
  %exitcond.not = icmp eq i32 %19, %258
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

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
