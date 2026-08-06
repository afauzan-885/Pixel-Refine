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
define void @_init_distance_kernel_c448_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 4
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
define void @_init_distance_kernel_c448_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.046 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %105, %after_if3 ]
  %27 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 4
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sdiv i32 %.046, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.046
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.046, 0
  %38 = icmp ne i32 %.046, %34
  %39 = and i1 %37, %36
  %40 = and i1 %39, %38
  %.neg5 = sext i1 %40 to i32
  %41 = add i32 %33, %.neg5
  %42 = mul i32 %32, -1
  %43 = mul i32 %42, %41
  %44 = add i32 %.046, %43
  %45 = load float*, float** %23, align 8
  %46 = load i32, i32* %24, align 4
  %47 = sub i32 %46, %32
  %48 = mul i32 %47, %41
  %49 = add i32 %.046, %48
  %50 = sext i32 %49 to i64
  %51 = getelementptr float, float* %45, i64 %50
  %52 = load float, float* %51, align 4
  %53 = fcmp reassoc ninf nsz ogt float %52, 5.000000e-01
  %54 = load float*, float** %25, align 8
  %55 = load i32, i32* %26, align 4
  %56 = sub i32 %55, %32
  %57 = mul i32 %56, %41
  %58 = add i32 %.046, %57
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, float* %54, i64 %59
  %. = select i1 %53, float -1.000000e+00, float 0.000000e+00
  store float %., float* %60, align 4
  %61 = fcmp reassoc ninf nsz olt float %52, 5.000000e-01
  br i1 %61, label %true_block1, label %after_if3

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body
  %62 = add i32 %41, -1
  %63 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %64 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %63, i64 0, i32 14
  %65 = load i8*, i8** %64, align 8
  %66 = getelementptr inbounds i8, i8* %65, i64 8
  %67 = bitcast i8* %66 to i32*
  %68 = load i32, i32* %67, align 4
  %69 = add i32 %68, -1
  %70 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %71 = tail call i32 @llvm.smin.i32(i32 %69, i32 %70)
  %72 = insertelement <2 x i32> poison, i32 %44, i64 0
  %73 = shufflevector <2 x i32> %72, <2 x i32> poison, <2 x i32> zeroinitializer
  %74 = add <2 x i32> %73, <i32 1, i32 -1>
  %75 = getelementptr inbounds i8, i8* %65, i64 12
  %76 = bitcast i8* %75 to i32*
  %77 = load i32, i32* %76, align 4
  %78 = add i32 %77, -1
  %79 = load float*, float** %23, align 8
  %80 = load i32, i32* %24, align 4
  %81 = mul i32 %80, %71
  %82 = tail call i32 @llvm.smax.i32(i32 %44, i32 0)
  %83 = tail call i32 @llvm.smin.i32(i32 %78, i32 %82)
  %84 = add i32 %81, %83
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, float* %79, i64 %85
  %87 = load float, float* %86, align 4
  %88 = fcmp reassoc ninf nsz ogt float %87, 5.000000e-01
  %89 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %74, <2 x i32> zeroinitializer)
  %90 = insertelement <2 x i32> poison, i32 %78, i64 0
  %91 = shufflevector <2 x i32> %90, <2 x i32> poison, <2 x i32> zeroinitializer
  %92 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %91, <2 x i32> %89)
  %93 = extractelement <2 x i32> %92, i64 1
  %94 = add i32 %81, %93
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, float* %79, i64 %95
  %97 = load float, float* %96, align 4
  %98 = fcmp reassoc ninf nsz ogt float %97, 5.000000e-01
  %.1 = select i1 %88, i1 true, i1 %98
  %99 = extractelement <2 x i32> %92, i64 0
  %100 = add i32 %81, %99
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %79, i64 %101
  %103 = load float, float* %102, align 4
  %104 = fcmp reassoc ninf nsz ogt float %103, 5.000000e-01
  br i1 %104, label %true_block10, label %after_if12

after_if3.sink.split:                             ; preds = %true_block28, %after_if24
  %.sink = phi float* [ %60, %true_block28 ], [ %148, %after_if24 ]
  store float 0.000000e+00, float* %.sink, align 4
  br label %after_if3

after_if3:                                        ; preds = %after_if3.sink.split, %for_loop_body
  %105 = add nsw i32 %.046, 1
  %exitcond.not = icmp eq i32 %19, %105
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %true_block1
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %true_block1
  %.2 = phi i1 [ true, %true_block10 ], [ %.1, %true_block1 ]
  %106 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %107 = tail call i32 @llvm.smin.i32(i32 %69, i32 %106)
  %108 = mul i32 %80, %107
  %109 = insertelement <2 x i32> poison, i32 %108, i64 0
  %110 = shufflevector <2 x i32> %109, <2 x i32> poison, <2 x i32> zeroinitializer
  %111 = add <2 x i32> %110, %92
  %112 = sext <2 x i32> %111 to <2 x i64>
  %113 = insertelement <2 x float*> poison, float* %79, i64 0
  %114 = shufflevector <2 x float*> %113, <2 x float*> poison, <2 x i32> zeroinitializer
  %115 = getelementptr float, <2 x float*> %114, <2 x i64> %112
  %116 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %115, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %117 = fcmp reassoc ninf nsz ogt <2 x float> %116, <float 5.000000e-01, float 5.000000e-01>
  %118 = extractelement <2 x i1> %117, i64 1
  %.3 = select i1 %118, i1 true, i1 %.2
  %119 = extractelement <2 x i1> %117, i64 0
  %spec.select = select i1 %119, i1 true, i1 %.3
  %120 = add i32 %41, 1
  %121 = tail call i32 @llvm.smax.i32(i32 %120, i32 0)
  %122 = tail call i32 @llvm.smin.i32(i32 %69, i32 %121)
  %123 = mul i32 %80, %122
  %124 = add i32 %123, %93
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %79, i64 %125
  %127 = load float, float* %126, align 4
  %128 = fcmp reassoc ninf nsz ogt float %127, 5.000000e-01
  %.5 = select i1 %128, i1 true, i1 %spec.select
  %129 = add i32 %123, %83
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, float* %79, i64 %130
  %132 = load float, float* %131, align 4
  %133 = fcmp reassoc ninf nsz ogt float %132, 5.000000e-01
  br i1 %133, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if12
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if12
  %.6 = phi i1 [ true, %true_block22 ], [ %.5, %after_if12 ]
  %134 = add i32 %123, %99
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %79, i64 %135
  %137 = load float, float* %136, align 4
  %138 = fcmp reassoc ninf nsz ogt float %137, 5.000000e-01
  %.7 = select i1 %138, i1 true, i1 %.6
  %139 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %140 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %139, i64 0, i32 2, i32 1
  %141 = load float*, float** %140, align 8
  %142 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %139, i64 0, i32 2, i32 0, i32 1
  %143 = load i32, i32* %142, align 4
  %144 = sub i32 %143, %32
  %145 = mul i32 %144, %41
  %146 = add i32 %.046, %145
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %141, i64 %147
  br i1 %.7, label %true_block28, label %after_if3.sink.split

true_block28:                                     ; preds = %after_if24
  store float 1.000000e+00, float* %148, align 4
  br label %after_if3.sink.split
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
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }

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
