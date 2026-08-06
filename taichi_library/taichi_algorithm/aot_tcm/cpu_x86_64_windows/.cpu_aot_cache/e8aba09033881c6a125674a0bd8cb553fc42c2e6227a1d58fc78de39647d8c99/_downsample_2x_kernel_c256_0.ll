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
define void @_downsample_2x_kernel_c256_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* } }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 12
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %18, i64 0, i32 1, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %18, i64 0, i32 1, i32 0, i32 1
  %22 = load i32, i32* %21, align 4
  %23 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %24 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %25 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  store i32 %24, i32* %29, align 4
  %30 = mul i32 %24, %23
  %31 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %31, i64 0, i32 14
  %33 = bitcast i8** %32 to i32**
  %34 = load i32*, i32** %33, align 8
  store i32 %30, i32* %34, align 4
  ret void
}

; Function Attrs: nounwind
define void @_downsample_2x_kernel_c256_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* } }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %22, i64 0, i32 1, i32 0, i32 1
  %27 = shl i32 %17, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %27, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.033 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %226, %for_loop_body ]
  %28 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %28, i64 0, i32 14
  %30 = load i8*, i8** %29, align 8
  %31 = getelementptr inbounds i8, i8* %30, i64 4
  %32 = bitcast i8* %31 to i32*
  %33 = load i32, i32* %32, align 4
  %34 = sdiv i32 %.033, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.033
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.033, 0
  %39 = icmp ne i32 %.033, %35
  %40 = and i1 %38, %37
  %41 = and i1 %40, %39
  %.neg4 = sext i1 %41 to i32
  %42 = add i32 %34, %.neg4
  %43 = shl i32 %42, 1
  %44 = mul i32 %33, -2
  %45 = mul i32 %44, %42
  %46 = add i32 %lsr.iv, %45
  %47 = getelementptr inbounds i8, i8* %30, i64 8
  %48 = bitcast i8* %47 to i32*
  %49 = load i32, i32* %48, align 4
  %50 = add i32 %49, -1
  %51 = getelementptr inbounds i8, i8* %30, i64 12
  %52 = bitcast i8* %51 to i32*
  %53 = load i32, i32* %52, align 4
  %54 = add i32 %53, -1
  %55 = load float*, float** %23, align 8
  %56 = load i32, i32* %24, align 4
  %57 = tail call i32 @llvm.abs.i32(i32 %46, i1 true)
  %58 = sub i32 %57, %54
  %59 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %.neg8 = mul i32 %59, -2
  %60 = add i32 %.neg8, %57
  %61 = tail call i32 @llvm.smax.i32(i32 %60, i32 0)
  %62 = tail call i32 @llvm.smin.i32(i32 %54, i32 %61)
  %63 = insertelement <2 x i32> poison, i32 %43, i64 0
  %64 = shufflevector <2 x i32> %63, <2 x i32> poison, <2 x i32> zeroinitializer
  %65 = add <2 x i32> %64, <i32 -2, i32 -1>
  %66 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %65, i1 true)
  %67 = insertelement <2 x i32> poison, i32 %50, i64 0
  %68 = shufflevector <2 x i32> %67, <2 x i32> poison, <2 x i32> zeroinitializer
  %69 = sub <2 x i32> %66, %68
  %70 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %69, <2 x i32> zeroinitializer)
  %71 = mul <2 x i32> %70, <i32 -2, i32 -2>
  %72 = add <2 x i32> %71, %66
  %73 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %72, <2 x i32> zeroinitializer)
  %74 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %68, <2 x i32> %73)
  %75 = insertelement <2 x i32> poison, i32 %56, i64 0
  %76 = shufflevector <2 x i32> %75, <2 x i32> poison, <2 x i32> zeroinitializer
  %77 = mul <2 x i32> %74, %76
  %shuffle = shufflevector <2 x i32> %77, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1>
  %78 = insertelement <4 x i32> poison, i32 %46, i64 0
  %shuffle36 = shufflevector <4 x i32> %78, <4 x i32> poison, <4 x i32> zeroinitializer
  %79 = or <4 x i32> %shuffle36, <i32 1, i32 poison, i32 poison, i32 poison>
  %80 = add <4 x i32> %shuffle36, <i32 poison, i32 2, i32 -2, i32 -1>
  %81 = shufflevector <4 x i32> %79, <4 x i32> %80, <4 x i32> <i32 0, i32 5, i32 6, i32 7>
  %82 = call <4 x i32> @llvm.abs.v4i32(<4 x i32> %81, i1 true)
  %83 = insertelement <4 x i32> poison, i32 %54, i64 0
  %shuffle37 = shufflevector <4 x i32> %83, <4 x i32> poison, <4 x i32> zeroinitializer
  %84 = sub <4 x i32> %82, %shuffle37
  %85 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %84, <4 x i32> zeroinitializer)
  %86 = mul <4 x i32> %85, <i32 -2, i32 -2, i32 -2, i32 -2>
  %87 = add <4 x i32> %86, %82
  %88 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %87, <4 x i32> zeroinitializer)
  %89 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle37, <4 x i32> %88)
  %90 = shufflevector <4 x i32> %89, <4 x i32> poison, <8 x i32> <i32 2, i32 3, i32 undef, i32 0, i32 1, i32 undef, i32 undef, i32 undef>
  %91 = insertelement <8 x i32> %90, i32 %62, i64 2
  %shuffle34 = shufflevector <8 x i32> %91, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2>
  %92 = add <8 x i32> %shuffle, %shuffle34
  %93 = sext <8 x i32> %92 to <8 x i64>
  %94 = extractelement <8 x i64> %93, i64 0
  %95 = getelementptr float, float* %55, i64 %94
  %96 = load float, float* %95, align 4
  %97 = extractelement <8 x i64> %93, i64 1
  %98 = getelementptr float, float* %55, i64 %97
  %99 = load float, float* %98, align 4
  %100 = extractelement <8 x i64> %93, i64 2
  %101 = getelementptr float, float* %55, i64 %100
  %102 = load float, float* %101, align 4
  %103 = extractelement <8 x i64> %93, i64 3
  %104 = getelementptr float, float* %55, i64 %103
  %105 = load float, float* %104, align 4
  %106 = extractelement <8 x i64> %93, i64 4
  %107 = getelementptr float, float* %55, i64 %106
  %108 = load float, float* %107, align 4
  %109 = extractelement <8 x i64> %93, i64 5
  %110 = getelementptr float, float* %55, i64 %109
  %111 = load float, float* %110, align 4
  %112 = extractelement <8 x i64> %93, i64 6
  %113 = getelementptr float, float* %55, i64 %112
  %114 = load float, float* %113, align 4
  %115 = extractelement <8 x i64> %93, i64 7
  %116 = getelementptr float, float* %55, i64 %115
  %117 = load float, float* %116, align 4
  %118 = shufflevector <2 x i32> %77, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 undef, i32 undef>
  %119 = extractelement <4 x i32> %89, i64 0
  %120 = extractelement <4 x i32> %89, i64 1
  %121 = or i32 %43, 1
  %122 = extractelement <4 x i32> %89, i64 2
  %123 = insertelement <2 x i32> %63, i32 %121, i64 1
  %124 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %123, i1 true)
  %125 = sub <2 x i32> %124, %68
  %126 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %125, <2 x i32> zeroinitializer)
  %127 = mul <2 x i32> %126, <i32 -2, i32 -2>
  %128 = add <2 x i32> %127, %124
  %129 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %128, <2 x i32> zeroinitializer)
  %130 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %68, <2 x i32> %129)
  %131 = mul <2 x i32> %130, %76
  %shuffle38 = shufflevector <2 x i32> %131, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 0, i32 1>
  %132 = shufflevector <4 x i32> %118, <4 x i32> %shuffle38, <4 x i32> <i32 0, i32 1, i32 4, i32 4>
  %133 = add <4 x i32> %89, %132
  %134 = sext <4 x i32> %133 to <4 x i64>
  %135 = extractelement <4 x i64> %134, i64 0
  %136 = getelementptr float, float* %55, i64 %135
  %137 = load float, float* %136, align 4
  %138 = extractelement <4 x i64> %134, i64 1
  %139 = getelementptr float, float* %55, i64 %138
  %140 = load float, float* %139, align 4
  %141 = extractelement <4 x i64> %134, i64 2
  %142 = getelementptr float, float* %55, i64 %141
  %143 = load float, float* %142, align 4
  %144 = extractelement <4 x i64> %134, i64 3
  %145 = getelementptr float, float* %55, i64 %144
  %146 = load float, float* %145, align 4
  %147 = insertelement <4 x i32> poison, i32 %62, i64 0
  %148 = shufflevector <4 x i32> %147, <4 x i32> %89, <4 x i32> <i32 0, i32 4, i32 5, i32 6>
  %149 = add <4 x i32> %148, %shuffle38
  %150 = sext <4 x i32> %149 to <4 x i64>
  %151 = extractelement <4 x i64> %150, i64 0
  %152 = getelementptr float, float* %55, i64 %151
  %153 = load float, float* %152, align 4
  %154 = fmul reassoc ninf nsz float %153, 3.600000e+01
  %155 = extractelement <4 x i64> %150, i64 1
  %156 = getelementptr float, float* %55, i64 %155
  %157 = load float, float* %156, align 4
  %158 = extractelement <4 x i64> %150, i64 2
  %159 = getelementptr float, float* %55, i64 %158
  %160 = load float, float* %159, align 4
  %161 = extractelement <4 x i64> %150, i64 3
  %162 = getelementptr float, float* %55, i64 %161
  %163 = load float, float* %162, align 4
  %164 = extractelement <4 x i32> %89, i64 3
  %165 = extractelement <2 x i32> %131, i64 1
  %166 = add i32 %164, %165
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, float* %55, i64 %167
  %169 = load float, float* %168, align 4
  %170 = add i32 %165, %62
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %55, i64 %171
  %173 = load float, float* %172, align 4
  %174 = add i32 %119, %165
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, float* %55, i64 %175
  %177 = load float, float* %176, align 4
  %178 = add i32 %120, %165
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, float* %55, i64 %179
  %181 = load float, float* %180, align 4
  %182 = add i32 %43, 2
  %183 = tail call i32 @llvm.abs.i32(i32 %182, i1 true)
  %184 = sub i32 %183, %50
  %185 = tail call i32 @llvm.smax.i32(i32 %184, i32 0)
  %.neg14 = mul i32 %185, -2
  %186 = add i32 %.neg14, %183
  %187 = tail call i32 @llvm.smax.i32(i32 %186, i32 0)
  %188 = tail call i32 @llvm.smin.i32(i32 %50, i32 %187)
  %189 = mul i32 %188, %56
  %190 = add i32 %122, %189
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, float* %55, i64 %191
  %193 = load float, float* %192, align 4
  %194 = add i32 %164, %189
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, float* %55, i64 %195
  %197 = load float, float* %196, align 4
  %198 = add i32 %189, %62
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, float* %55, i64 %199
  %201 = load float, float* %200, align 4
  %202 = add i32 %119, %189
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, float* %55, i64 %203
  %205 = load float, float* %204, align 4
  %206 = add i32 %120, %189
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, float* %55, i64 %207
  %209 = load float, float* %208, align 4
  %reass.add = fadd reassoc ninf nsz float %105, %99
  %reass.add15 = fadd reassoc ninf nsz float %reass.add, %111
  %reass.add16 = fadd reassoc ninf nsz float %reass.add15, %140
  %reass.add17 = fadd reassoc ninf nsz float %reass.add16, %163
  %reass.add18 = fadd reassoc ninf nsz float %reass.add17, %181
  %reass.add19 = fadd reassoc ninf nsz float %reass.add18, %197
  %reass.add20 = fadd reassoc ninf nsz float %reass.add19, %205
  %reass.mul = fmul reassoc ninf nsz float %reass.add20, 4.000000e+00
  %reass.add21 = fadd reassoc ninf nsz float %146, %117
  %reass.add22 = fadd reassoc ninf nsz float %reass.add21, %157
  %reass.add23 = fadd reassoc ninf nsz float %reass.add22, %173
  %reass.mul24 = fmul reassoc ninf nsz float %reass.add23, 2.400000e+01
  %reass.add25 = fadd reassoc ninf nsz float %137, %114
  %reass.add26 = fadd reassoc ninf nsz float %reass.add25, %169
  %reass.add27 = fadd reassoc ninf nsz float %reass.add26, %177
  %reass.mul28 = fmul reassoc ninf nsz float %reass.add27, 1.600000e+01
  %reass.add29 = fadd reassoc ninf nsz float %143, %102
  %reass.add30 = fadd reassoc ninf nsz float %reass.add29, %160
  %reass.add31 = fadd reassoc ninf nsz float %reass.add30, %201
  %reass.mul32 = fmul reassoc ninf nsz float %reass.add31, 6.000000e+00
  %210 = fadd reassoc ninf nsz float %108, %96
  %211 = fadd reassoc ninf nsz float %210, %154
  %212 = fadd reassoc ninf nsz float %211, %193
  %213 = fadd reassoc ninf nsz float %212, %reass.mul24
  %214 = fadd reassoc ninf nsz float %213, %reass.mul28
  %215 = fadd reassoc ninf nsz float %214, %209
  %216 = fadd reassoc ninf nsz float %215, %reass.mul32
  %217 = fadd reassoc ninf nsz float %216, %reass.mul
  %218 = fmul reassoc ninf nsz float %217, 3.906250e-03
  %219 = load float*, float** %25, align 8
  %220 = load i32, i32* %26, align 4
  %221 = sub i32 %220, %33
  %222 = mul i32 %221, %42
  %223 = add i32 %.033, %222
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %219, i64 %224
  store float %218, float* %225, align 4
  %226 = add nsw i32 %.033, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %226
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #5

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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.abs.v4i32(<4 x i32>, i1 immarg) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
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
