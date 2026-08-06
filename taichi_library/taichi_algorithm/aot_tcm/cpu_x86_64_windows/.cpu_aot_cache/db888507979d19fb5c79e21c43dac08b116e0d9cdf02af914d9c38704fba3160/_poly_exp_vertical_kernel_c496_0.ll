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
define void @_poly_exp_vertical_kernel_c496_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 4
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = mul i32 %14, %10
  %21 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %21, i64 0, i32 14
  %23 = bitcast i8** %22 to i32**
  %24 = load i32*, i32** %23, align 8
  store i32 %20, i32* %24, align 4
  ret void
}

; Function Attrs: nounwind
define void @_poly_exp_vertical_kernel_c496_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %25 = load float*, float** %24, align 8
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 0, i32 1
  %27 = getelementptr float, float* %25, i64 2
  %28 = icmp sgt i32 %23, 0
  %29 = icmp sgt i32 %23, 1
  %30 = icmp sgt i32 %23, 2
  %31 = icmp sgt i32 %23, 3
  %32 = icmp sgt i32 %23, 4
  %33 = icmp sgt i32 %23, 5
  %34 = icmp sgt i32 %23, 6
  %35 = icmp sgt i32 %23, 7
  %36 = icmp sgt i32 %23, 8
  %37 = icmp sgt i32 %23, 9
  %38 = icmp sgt i32 %23, 10
  %39 = icmp slt i32 %17, %19
  br i1 %39, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %42 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if30, %for_loop_body.lr.ph
  %.05860 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %581, %after_if30 ]
  %45 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %46 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %45, i64 0, i32 14
  %47 = load i8*, i8** %46, align 8
  %48 = getelementptr inbounds i8, i8* %47, i64 4
  %49 = bitcast i8* %48 to i32*
  %50 = load i32, i32* %49, align 4
  %51 = sdiv i32 %.05860, %50
  %52 = mul i32 %51, %50
  %53 = xor i32 %50, %.05860
  %54 = icmp slt i32 %53, 0
  %55 = icmp ne i32 %.05860, 0
  %56 = icmp ne i32 %.05860, %52
  %57 = and i1 %55, %54
  %58 = and i1 %57, %56
  %.neg59 = sext i1 %58 to i32
  %59 = load float*, float** %40, align 8
  %60 = load i32, i32* %41, align 4
  %61 = add i32 %51, %.neg59
  %62 = mul i32 %61, %50
  %63 = insertelement <2 x i32> poison, i32 %.05860, i64 0
  %64 = insertelement <2 x i32> poison, i32 %62, i64 0
  %65 = sub <2 x i32> %63, %64
  %66 = extractelement <2 x i32> %65, i64 0
  %67 = mul i32 %60, %61
  %68 = add i32 %66, %67
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, float* %59, i64 %69
  %71 = load float, float* %70, align 4
  %72 = load float, float* %25, align 4
  %73 = fmul reassoc ninf nsz float %72, %71
  %74 = load float, float* %27, align 4
  %75 = fmul reassoc ninf nsz float %74, %71
  br i1 %28, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if30
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %76 = insertelement <2 x i32> poison, i32 %61, i64 0
  %77 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %78 = add <2 x i32> %77, <i32 1, i32 -1>
  %79 = getelementptr inbounds i8, i8* %47, i64 8
  %80 = bitcast i8* %79 to i32*
  %81 = load i32, i32* %80, align 4
  %82 = add i32 %81, -1
  %83 = insertelement <2 x i32> poison, i32 %82, i64 0
  %84 = shufflevector <2 x i32> %83, <2 x i32> poison, <2 x i32> zeroinitializer
  %85 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %78, <2 x i32> %84)
  %86 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %85, <2 x i32> zeroinitializer)
  %87 = insertelement <2 x i32> poison, i32 %60, i64 0
  %88 = shufflevector <2 x i32> %87, <2 x i32> poison, <2 x i32> zeroinitializer
  %89 = mul <2 x i32> %86, %88
  %90 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %91 = add <2 x i32> %89, %90
  %92 = sext <2 x i32> %91 to <2 x i64>
  %93 = insertelement <2 x float*> poison, float* %59, i64 0
  %94 = shufflevector <2 x float*> %93, <2 x float*> poison, <2 x i32> zeroinitializer
  %95 = getelementptr float, <2 x float*> %94, <2 x i64> %92
  %96 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %95, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %97 = load float*, float** %24, align 8
  %98 = load i32, i32* %26, align 4
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %97, i64 %99
  %101 = load float, float* %100, align 4
  %102 = extractelement <2 x float> %96, i64 0
  %103 = extractelement <2 x float> %96, i64 1
  %104 = fadd reassoc ninf nsz float %102, %103
  %105 = fmul reassoc ninf nsz float %101, %104
  %106 = fadd reassoc ninf nsz float %105, %73
  %107 = add i32 %98, 1
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, float* %97, i64 %108
  %110 = load float, float* %109, align 4
  %111 = fsub reassoc ninf nsz float %102, %103
  %112 = fmul reassoc ninf nsz float %110, %111
  %113 = add i32 %98, 2
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, float* %97, i64 %114
  %116 = load float, float* %115, align 4
  %117 = fmul reassoc ninf nsz float %116, %104
  %118 = fadd reassoc ninf nsz float %117, %75
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %.047 = phi float [ %106, %true_block ], [ %73, %for_loop_body ]
  %.036 = phi float [ %112, %true_block ], [ 0.000000e+00, %for_loop_body ]
  %.0 = phi float [ %118, %true_block ], [ %75, %for_loop_body ]
  br i1 %29, label %true_block1, label %after_if3

true_block1:                                      ; preds = %after_if
  %119 = insertelement <2 x i32> poison, i32 %61, i64 0
  %120 = shufflevector <2 x i32> %119, <2 x i32> poison, <2 x i32> zeroinitializer
  %121 = add <2 x i32> %120, <i32 2, i32 -2>
  %122 = getelementptr inbounds i8, i8* %47, i64 8
  %123 = bitcast i8* %122 to i32*
  %124 = load i32, i32* %123, align 4
  %125 = add i32 %124, -1
  %126 = insertelement <2 x i32> poison, i32 %125, i64 0
  %127 = shufflevector <2 x i32> %126, <2 x i32> poison, <2 x i32> zeroinitializer
  %128 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %121, <2 x i32> %127)
  %129 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %128, <2 x i32> zeroinitializer)
  %130 = insertelement <2 x i32> poison, i32 %60, i64 0
  %131 = shufflevector <2 x i32> %130, <2 x i32> poison, <2 x i32> zeroinitializer
  %132 = mul <2 x i32> %129, %131
  %133 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %134 = add <2 x i32> %132, %133
  %135 = sext <2 x i32> %134 to <2 x i64>
  %136 = insertelement <2 x float*> poison, float* %59, i64 0
  %137 = shufflevector <2 x float*> %136, <2 x float*> poison, <2 x i32> zeroinitializer
  %138 = getelementptr float, <2 x float*> %137, <2 x i64> %135
  %139 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %138, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %140 = load float*, float** %24, align 8
  %141 = load i32, i32* %26, align 4
  %142 = shl i32 %141, 1
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %140, i64 %143
  %145 = load float, float* %144, align 4
  %146 = extractelement <2 x float> %139, i64 0
  %147 = extractelement <2 x float> %139, i64 1
  %148 = fadd reassoc ninf nsz float %146, %147
  %149 = fmul reassoc ninf nsz float %145, %148
  %150 = fadd reassoc ninf nsz float %149, %.047
  %151 = getelementptr float, float* %144, i64 1
  %152 = load float, float* %151, align 4
  %153 = fsub reassoc ninf nsz float %146, %147
  %154 = fmul reassoc ninf nsz float %152, %153
  %155 = fadd reassoc ninf nsz float %154, %.036
  %156 = add i32 %142, 2
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %140, i64 %157
  %159 = load float, float* %158, align 4
  %160 = fmul reassoc ninf nsz float %159, %148
  %161 = fadd reassoc ninf nsz float %160, %.0
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %after_if
  %.148 = phi float [ %150, %true_block1 ], [ %.047, %after_if ]
  %.137 = phi float [ %155, %true_block1 ], [ %.036, %after_if ]
  %.1 = phi float [ %161, %true_block1 ], [ %.0, %after_if ]
  br i1 %30, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %162 = insertelement <2 x i32> poison, i32 %61, i64 0
  %163 = shufflevector <2 x i32> %162, <2 x i32> poison, <2 x i32> zeroinitializer
  %164 = add <2 x i32> %163, <i32 3, i32 -3>
  %165 = getelementptr inbounds i8, i8* %47, i64 8
  %166 = bitcast i8* %165 to i32*
  %167 = load i32, i32* %166, align 4
  %168 = add i32 %167, -1
  %169 = insertelement <2 x i32> poison, i32 %168, i64 0
  %170 = shufflevector <2 x i32> %169, <2 x i32> poison, <2 x i32> zeroinitializer
  %171 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %164, <2 x i32> %170)
  %172 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %171, <2 x i32> zeroinitializer)
  %173 = insertelement <2 x i32> poison, i32 %60, i64 0
  %174 = shufflevector <2 x i32> %173, <2 x i32> poison, <2 x i32> zeroinitializer
  %175 = mul <2 x i32> %172, %174
  %176 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %177 = add <2 x i32> %175, %176
  %178 = sext <2 x i32> %177 to <2 x i64>
  %179 = insertelement <2 x float*> poison, float* %59, i64 0
  %180 = shufflevector <2 x float*> %179, <2 x float*> poison, <2 x i32> zeroinitializer
  %181 = getelementptr float, <2 x float*> %180, <2 x i64> %178
  %182 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %181, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %183 = load float*, float** %24, align 8
  %184 = load i32, i32* %26, align 4
  %185 = mul i32 %184, 3
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %183, i64 %186
  %188 = load float, float* %187, align 4
  %189 = extractelement <2 x float> %182, i64 0
  %190 = extractelement <2 x float> %182, i64 1
  %191 = fadd reassoc ninf nsz float %189, %190
  %192 = fmul reassoc ninf nsz float %188, %191
  %193 = fadd reassoc ninf nsz float %192, %.148
  %194 = add i32 %185, 1
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, float* %183, i64 %195
  %197 = load float, float* %196, align 4
  %198 = fsub reassoc ninf nsz float %189, %190
  %199 = fmul reassoc ninf nsz float %197, %198
  %200 = fadd reassoc ninf nsz float %199, %.137
  %201 = add i32 %185, 2
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %183, i64 %202
  %204 = load float, float* %203, align 4
  %205 = fmul reassoc ninf nsz float %204, %191
  %206 = fadd reassoc ninf nsz float %205, %.1
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %.249 = phi float [ %193, %true_block4 ], [ %.148, %after_if3 ]
  %.238 = phi float [ %200, %true_block4 ], [ %.137, %after_if3 ]
  %.2 = phi float [ %206, %true_block4 ], [ %.1, %after_if3 ]
  br i1 %31, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %207 = insertelement <2 x i32> poison, i32 %61, i64 0
  %208 = shufflevector <2 x i32> %207, <2 x i32> poison, <2 x i32> zeroinitializer
  %209 = add <2 x i32> %208, <i32 4, i32 -4>
  %210 = getelementptr inbounds i8, i8* %47, i64 8
  %211 = bitcast i8* %210 to i32*
  %212 = load i32, i32* %211, align 4
  %213 = add i32 %212, -1
  %214 = insertelement <2 x i32> poison, i32 %213, i64 0
  %215 = shufflevector <2 x i32> %214, <2 x i32> poison, <2 x i32> zeroinitializer
  %216 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %209, <2 x i32> %215)
  %217 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %216, <2 x i32> zeroinitializer)
  %218 = insertelement <2 x i32> poison, i32 %60, i64 0
  %219 = shufflevector <2 x i32> %218, <2 x i32> poison, <2 x i32> zeroinitializer
  %220 = mul <2 x i32> %217, %219
  %221 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %222 = add <2 x i32> %220, %221
  %223 = sext <2 x i32> %222 to <2 x i64>
  %224 = insertelement <2 x float*> poison, float* %59, i64 0
  %225 = shufflevector <2 x float*> %224, <2 x float*> poison, <2 x i32> zeroinitializer
  %226 = getelementptr float, <2 x float*> %225, <2 x i64> %223
  %227 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %226, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %228 = load float*, float** %24, align 8
  %229 = load i32, i32* %26, align 4
  %230 = shl i32 %229, 2
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, float* %228, i64 %231
  %233 = load float, float* %232, align 4
  %234 = extractelement <2 x float> %227, i64 0
  %235 = extractelement <2 x float> %227, i64 1
  %236 = fadd reassoc ninf nsz float %234, %235
  %237 = fmul reassoc ninf nsz float %233, %236
  %238 = fadd reassoc ninf nsz float %237, %.249
  %239 = getelementptr float, float* %232, i64 1
  %240 = load float, float* %239, align 4
  %241 = fsub reassoc ninf nsz float %234, %235
  %242 = fmul reassoc ninf nsz float %240, %241
  %243 = fadd reassoc ninf nsz float %242, %.238
  %244 = getelementptr float, float* %232, i64 2
  %245 = load float, float* %244, align 4
  %246 = fmul reassoc ninf nsz float %245, %236
  %247 = fadd reassoc ninf nsz float %246, %.2
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.350 = phi float [ %238, %true_block7 ], [ %.249, %after_if6 ]
  %.339 = phi float [ %243, %true_block7 ], [ %.238, %after_if6 ]
  %.3 = phi float [ %247, %true_block7 ], [ %.2, %after_if6 ]
  br i1 %32, label %true_block10, label %after_if12

true_block10:                                     ; preds = %after_if9
  %248 = insertelement <2 x i32> poison, i32 %61, i64 0
  %249 = shufflevector <2 x i32> %248, <2 x i32> poison, <2 x i32> zeroinitializer
  %250 = add <2 x i32> %249, <i32 5, i32 -5>
  %251 = getelementptr inbounds i8, i8* %47, i64 8
  %252 = bitcast i8* %251 to i32*
  %253 = load i32, i32* %252, align 4
  %254 = add i32 %253, -1
  %255 = insertelement <2 x i32> poison, i32 %254, i64 0
  %256 = shufflevector <2 x i32> %255, <2 x i32> poison, <2 x i32> zeroinitializer
  %257 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %250, <2 x i32> %256)
  %258 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %257, <2 x i32> zeroinitializer)
  %259 = insertelement <2 x i32> poison, i32 %60, i64 0
  %260 = shufflevector <2 x i32> %259, <2 x i32> poison, <2 x i32> zeroinitializer
  %261 = mul <2 x i32> %258, %260
  %262 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %263 = add <2 x i32> %261, %262
  %264 = sext <2 x i32> %263 to <2 x i64>
  %265 = insertelement <2 x float*> poison, float* %59, i64 0
  %266 = shufflevector <2 x float*> %265, <2 x float*> poison, <2 x i32> zeroinitializer
  %267 = getelementptr float, <2 x float*> %266, <2 x i64> %264
  %268 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %267, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %269 = load float*, float** %24, align 8
  %270 = load i32, i32* %26, align 4
  %271 = mul i32 %270, 5
  %272 = sext i32 %271 to i64
  %273 = getelementptr float, float* %269, i64 %272
  %274 = load float, float* %273, align 4
  %275 = extractelement <2 x float> %268, i64 0
  %276 = extractelement <2 x float> %268, i64 1
  %277 = fadd reassoc ninf nsz float %275, %276
  %278 = fmul reassoc ninf nsz float %274, %277
  %279 = fadd reassoc ninf nsz float %278, %.350
  %280 = add i32 %271, 1
  %281 = sext i32 %280 to i64
  %282 = getelementptr float, float* %269, i64 %281
  %283 = load float, float* %282, align 4
  %284 = fsub reassoc ninf nsz float %275, %276
  %285 = fmul reassoc ninf nsz float %283, %284
  %286 = fadd reassoc ninf nsz float %285, %.339
  %287 = add i32 %271, 2
  %288 = sext i32 %287 to i64
  %289 = getelementptr float, float* %269, i64 %288
  %290 = load float, float* %289, align 4
  %291 = fmul reassoc ninf nsz float %290, %277
  %292 = fadd reassoc ninf nsz float %291, %.3
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %.451 = phi float [ %279, %true_block10 ], [ %.350, %after_if9 ]
  %.440 = phi float [ %286, %true_block10 ], [ %.339, %after_if9 ]
  %.4 = phi float [ %292, %true_block10 ], [ %.3, %after_if9 ]
  br i1 %33, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if12
  %293 = insertelement <2 x i32> poison, i32 %61, i64 0
  %294 = shufflevector <2 x i32> %293, <2 x i32> poison, <2 x i32> zeroinitializer
  %295 = add <2 x i32> %294, <i32 6, i32 -6>
  %296 = getelementptr inbounds i8, i8* %47, i64 8
  %297 = bitcast i8* %296 to i32*
  %298 = load i32, i32* %297, align 4
  %299 = add i32 %298, -1
  %300 = insertelement <2 x i32> poison, i32 %299, i64 0
  %301 = shufflevector <2 x i32> %300, <2 x i32> poison, <2 x i32> zeroinitializer
  %302 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %295, <2 x i32> %301)
  %303 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %302, <2 x i32> zeroinitializer)
  %304 = insertelement <2 x i32> poison, i32 %60, i64 0
  %305 = shufflevector <2 x i32> %304, <2 x i32> poison, <2 x i32> zeroinitializer
  %306 = mul <2 x i32> %303, %305
  %307 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %308 = add <2 x i32> %306, %307
  %309 = sext <2 x i32> %308 to <2 x i64>
  %310 = insertelement <2 x float*> poison, float* %59, i64 0
  %311 = shufflevector <2 x float*> %310, <2 x float*> poison, <2 x i32> zeroinitializer
  %312 = getelementptr float, <2 x float*> %311, <2 x i64> %309
  %313 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %312, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %314 = load float*, float** %24, align 8
  %315 = load i32, i32* %26, align 4
  %316 = mul i32 %315, 6
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, float* %314, i64 %317
  %319 = load float, float* %318, align 4
  %320 = extractelement <2 x float> %313, i64 0
  %321 = extractelement <2 x float> %313, i64 1
  %322 = fadd reassoc ninf nsz float %320, %321
  %323 = fmul reassoc ninf nsz float %319, %322
  %324 = fadd reassoc ninf nsz float %323, %.451
  %325 = getelementptr float, float* %318, i64 1
  %326 = load float, float* %325, align 4
  %327 = fsub reassoc ninf nsz float %320, %321
  %328 = fmul reassoc ninf nsz float %326, %327
  %329 = fadd reassoc ninf nsz float %328, %.440
  %330 = add i32 %316, 2
  %331 = sext i32 %330 to i64
  %332 = getelementptr float, float* %314, i64 %331
  %333 = load float, float* %332, align 4
  %334 = fmul reassoc ninf nsz float %333, %322
  %335 = fadd reassoc ninf nsz float %334, %.4
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if12
  %.552 = phi float [ %324, %true_block13 ], [ %.451, %after_if12 ]
  %.541 = phi float [ %329, %true_block13 ], [ %.440, %after_if12 ]
  %.5 = phi float [ %335, %true_block13 ], [ %.4, %after_if12 ]
  br i1 %34, label %true_block16, label %after_if18

true_block16:                                     ; preds = %after_if15
  %336 = insertelement <2 x i32> poison, i32 %61, i64 0
  %337 = shufflevector <2 x i32> %336, <2 x i32> poison, <2 x i32> zeroinitializer
  %338 = add <2 x i32> %337, <i32 7, i32 -7>
  %339 = getelementptr inbounds i8, i8* %47, i64 8
  %340 = bitcast i8* %339 to i32*
  %341 = load i32, i32* %340, align 4
  %342 = add i32 %341, -1
  %343 = insertelement <2 x i32> poison, i32 %342, i64 0
  %344 = shufflevector <2 x i32> %343, <2 x i32> poison, <2 x i32> zeroinitializer
  %345 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %338, <2 x i32> %344)
  %346 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %345, <2 x i32> zeroinitializer)
  %347 = insertelement <2 x i32> poison, i32 %60, i64 0
  %348 = shufflevector <2 x i32> %347, <2 x i32> poison, <2 x i32> zeroinitializer
  %349 = mul <2 x i32> %346, %348
  %350 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %351 = add <2 x i32> %349, %350
  %352 = sext <2 x i32> %351 to <2 x i64>
  %353 = insertelement <2 x float*> poison, float* %59, i64 0
  %354 = shufflevector <2 x float*> %353, <2 x float*> poison, <2 x i32> zeroinitializer
  %355 = getelementptr float, <2 x float*> %354, <2 x i64> %352
  %356 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %355, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %357 = load float*, float** %24, align 8
  %358 = load i32, i32* %26, align 4
  %359 = mul i32 %358, 7
  %360 = sext i32 %359 to i64
  %361 = getelementptr float, float* %357, i64 %360
  %362 = load float, float* %361, align 4
  %363 = extractelement <2 x float> %356, i64 0
  %364 = extractelement <2 x float> %356, i64 1
  %365 = fadd reassoc ninf nsz float %363, %364
  %366 = fmul reassoc ninf nsz float %362, %365
  %367 = fadd reassoc ninf nsz float %366, %.552
  %368 = add i32 %359, 1
  %369 = sext i32 %368 to i64
  %370 = getelementptr float, float* %357, i64 %369
  %371 = load float, float* %370, align 4
  %372 = fsub reassoc ninf nsz float %363, %364
  %373 = fmul reassoc ninf nsz float %371, %372
  %374 = fadd reassoc ninf nsz float %373, %.541
  %375 = add i32 %359, 2
  %376 = sext i32 %375 to i64
  %377 = getelementptr float, float* %357, i64 %376
  %378 = load float, float* %377, align 4
  %379 = fmul reassoc ninf nsz float %378, %365
  %380 = fadd reassoc ninf nsz float %379, %.5
  br label %after_if18

after_if18:                                       ; preds = %true_block16, %after_if15
  %.653 = phi float [ %367, %true_block16 ], [ %.552, %after_if15 ]
  %.642 = phi float [ %374, %true_block16 ], [ %.541, %after_if15 ]
  %.6 = phi float [ %380, %true_block16 ], [ %.5, %after_if15 ]
  br i1 %35, label %true_block19, label %after_if21

true_block19:                                     ; preds = %after_if18
  %381 = insertelement <2 x i32> poison, i32 %61, i64 0
  %382 = shufflevector <2 x i32> %381, <2 x i32> poison, <2 x i32> zeroinitializer
  %383 = add <2 x i32> %382, <i32 8, i32 -8>
  %384 = getelementptr inbounds i8, i8* %47, i64 8
  %385 = bitcast i8* %384 to i32*
  %386 = load i32, i32* %385, align 4
  %387 = add i32 %386, -1
  %388 = insertelement <2 x i32> poison, i32 %387, i64 0
  %389 = shufflevector <2 x i32> %388, <2 x i32> poison, <2 x i32> zeroinitializer
  %390 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %383, <2 x i32> %389)
  %391 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %390, <2 x i32> zeroinitializer)
  %392 = insertelement <2 x i32> poison, i32 %60, i64 0
  %393 = shufflevector <2 x i32> %392, <2 x i32> poison, <2 x i32> zeroinitializer
  %394 = mul <2 x i32> %391, %393
  %395 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %396 = add <2 x i32> %394, %395
  %397 = sext <2 x i32> %396 to <2 x i64>
  %398 = insertelement <2 x float*> poison, float* %59, i64 0
  %399 = shufflevector <2 x float*> %398, <2 x float*> poison, <2 x i32> zeroinitializer
  %400 = getelementptr float, <2 x float*> %399, <2 x i64> %397
  %401 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %400, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %402 = load float*, float** %24, align 8
  %403 = load i32, i32* %26, align 4
  %404 = shl i32 %403, 3
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, float* %402, i64 %405
  %407 = load float, float* %406, align 4
  %408 = extractelement <2 x float> %401, i64 0
  %409 = extractelement <2 x float> %401, i64 1
  %410 = fadd reassoc ninf nsz float %408, %409
  %411 = fmul reassoc ninf nsz float %407, %410
  %412 = fadd reassoc ninf nsz float %411, %.653
  %413 = getelementptr float, float* %406, i64 1
  %414 = load float, float* %413, align 4
  %415 = fsub reassoc ninf nsz float %408, %409
  %416 = fmul reassoc ninf nsz float %414, %415
  %417 = fadd reassoc ninf nsz float %416, %.642
  %418 = getelementptr float, float* %406, i64 2
  %419 = load float, float* %418, align 4
  %420 = fmul reassoc ninf nsz float %419, %410
  %421 = fadd reassoc ninf nsz float %420, %.6
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if18
  %.754 = phi float [ %412, %true_block19 ], [ %.653, %after_if18 ]
  %.743 = phi float [ %417, %true_block19 ], [ %.642, %after_if18 ]
  %.7 = phi float [ %421, %true_block19 ], [ %.6, %after_if18 ]
  br i1 %36, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if21
  %422 = insertelement <2 x i32> poison, i32 %61, i64 0
  %423 = shufflevector <2 x i32> %422, <2 x i32> poison, <2 x i32> zeroinitializer
  %424 = add <2 x i32> %423, <i32 9, i32 -9>
  %425 = getelementptr inbounds i8, i8* %47, i64 8
  %426 = bitcast i8* %425 to i32*
  %427 = load i32, i32* %426, align 4
  %428 = add i32 %427, -1
  %429 = insertelement <2 x i32> poison, i32 %428, i64 0
  %430 = shufflevector <2 x i32> %429, <2 x i32> poison, <2 x i32> zeroinitializer
  %431 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %424, <2 x i32> %430)
  %432 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %431, <2 x i32> zeroinitializer)
  %433 = insertelement <2 x i32> poison, i32 %60, i64 0
  %434 = shufflevector <2 x i32> %433, <2 x i32> poison, <2 x i32> zeroinitializer
  %435 = mul <2 x i32> %432, %434
  %436 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %437 = add <2 x i32> %435, %436
  %438 = sext <2 x i32> %437 to <2 x i64>
  %439 = insertelement <2 x float*> poison, float* %59, i64 0
  %440 = shufflevector <2 x float*> %439, <2 x float*> poison, <2 x i32> zeroinitializer
  %441 = getelementptr float, <2 x float*> %440, <2 x i64> %438
  %442 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %441, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %443 = load float*, float** %24, align 8
  %444 = load i32, i32* %26, align 4
  %445 = mul i32 %444, 9
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, float* %443, i64 %446
  %448 = load float, float* %447, align 4
  %449 = extractelement <2 x float> %442, i64 0
  %450 = extractelement <2 x float> %442, i64 1
  %451 = fadd reassoc ninf nsz float %449, %450
  %452 = fmul reassoc ninf nsz float %448, %451
  %453 = fadd reassoc ninf nsz float %452, %.754
  %454 = add i32 %445, 1
  %455 = sext i32 %454 to i64
  %456 = getelementptr float, float* %443, i64 %455
  %457 = load float, float* %456, align 4
  %458 = fsub reassoc ninf nsz float %449, %450
  %459 = fmul reassoc ninf nsz float %457, %458
  %460 = fadd reassoc ninf nsz float %459, %.743
  %461 = add i32 %445, 2
  %462 = sext i32 %461 to i64
  %463 = getelementptr float, float* %443, i64 %462
  %464 = load float, float* %463, align 4
  %465 = fmul reassoc ninf nsz float %464, %451
  %466 = fadd reassoc ninf nsz float %465, %.7
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if21
  %.855 = phi float [ %453, %true_block22 ], [ %.754, %after_if21 ]
  %.844 = phi float [ %460, %true_block22 ], [ %.743, %after_if21 ]
  %.8 = phi float [ %466, %true_block22 ], [ %.7, %after_if21 ]
  br i1 %37, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if24
  %467 = insertelement <2 x i32> poison, i32 %61, i64 0
  %468 = shufflevector <2 x i32> %467, <2 x i32> poison, <2 x i32> zeroinitializer
  %469 = add <2 x i32> %468, <i32 10, i32 -10>
  %470 = getelementptr inbounds i8, i8* %47, i64 8
  %471 = bitcast i8* %470 to i32*
  %472 = load i32, i32* %471, align 4
  %473 = add i32 %472, -1
  %474 = insertelement <2 x i32> poison, i32 %473, i64 0
  %475 = shufflevector <2 x i32> %474, <2 x i32> poison, <2 x i32> zeroinitializer
  %476 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %469, <2 x i32> %475)
  %477 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %476, <2 x i32> zeroinitializer)
  %478 = insertelement <2 x i32> poison, i32 %60, i64 0
  %479 = shufflevector <2 x i32> %478, <2 x i32> poison, <2 x i32> zeroinitializer
  %480 = mul <2 x i32> %477, %479
  %481 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %482 = add <2 x i32> %480, %481
  %483 = sext <2 x i32> %482 to <2 x i64>
  %484 = insertelement <2 x float*> poison, float* %59, i64 0
  %485 = shufflevector <2 x float*> %484, <2 x float*> poison, <2 x i32> zeroinitializer
  %486 = getelementptr float, <2 x float*> %485, <2 x i64> %483
  %487 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %486, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %488 = load float*, float** %24, align 8
  %489 = load i32, i32* %26, align 4
  %490 = mul i32 %489, 10
  %491 = sext i32 %490 to i64
  %492 = getelementptr float, float* %488, i64 %491
  %493 = load float, float* %492, align 4
  %494 = extractelement <2 x float> %487, i64 0
  %495 = extractelement <2 x float> %487, i64 1
  %496 = fadd reassoc ninf nsz float %494, %495
  %497 = fmul reassoc ninf nsz float %493, %496
  %498 = fadd reassoc ninf nsz float %497, %.855
  %499 = getelementptr float, float* %492, i64 1
  %500 = load float, float* %499, align 4
  %501 = fsub reassoc ninf nsz float %494, %495
  %502 = fmul reassoc ninf nsz float %500, %501
  %503 = fadd reassoc ninf nsz float %502, %.844
  %504 = add i32 %490, 2
  %505 = sext i32 %504 to i64
  %506 = getelementptr float, float* %488, i64 %505
  %507 = load float, float* %506, align 4
  %508 = fmul reassoc ninf nsz float %507, %496
  %509 = fadd reassoc ninf nsz float %508, %.8
  br label %after_if27

after_if27:                                       ; preds = %true_block25, %after_if24
  %.956 = phi float [ %498, %true_block25 ], [ %.855, %after_if24 ]
  %.945 = phi float [ %503, %true_block25 ], [ %.844, %after_if24 ]
  %.9 = phi float [ %509, %true_block25 ], [ %.8, %after_if24 ]
  br i1 %38, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %510 = insertelement <2 x i32> poison, i32 %61, i64 0
  %511 = shufflevector <2 x i32> %510, <2 x i32> poison, <2 x i32> zeroinitializer
  %512 = add <2 x i32> %511, <i32 11, i32 -11>
  %513 = getelementptr inbounds i8, i8* %47, i64 8
  %514 = bitcast i8* %513 to i32*
  %515 = load i32, i32* %514, align 4
  %516 = add i32 %515, -1
  %517 = insertelement <2 x i32> poison, i32 %516, i64 0
  %518 = shufflevector <2 x i32> %517, <2 x i32> poison, <2 x i32> zeroinitializer
  %519 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %512, <2 x i32> %518)
  %520 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %519, <2 x i32> zeroinitializer)
  %521 = insertelement <2 x i32> poison, i32 %60, i64 0
  %522 = shufflevector <2 x i32> %521, <2 x i32> poison, <2 x i32> zeroinitializer
  %523 = mul <2 x i32> %520, %522
  %524 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %525 = add <2 x i32> %523, %524
  %526 = sext <2 x i32> %525 to <2 x i64>
  %527 = insertelement <2 x float*> poison, float* %59, i64 0
  %528 = shufflevector <2 x float*> %527, <2 x float*> poison, <2 x i32> zeroinitializer
  %529 = getelementptr float, <2 x float*> %528, <2 x i64> %526
  %530 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %529, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %531 = load float*, float** %24, align 8
  %532 = load i32, i32* %26, align 4
  %533 = mul i32 %532, 11
  %534 = sext i32 %533 to i64
  %535 = getelementptr float, float* %531, i64 %534
  %536 = load float, float* %535, align 4
  %537 = extractelement <2 x float> %530, i64 0
  %538 = extractelement <2 x float> %530, i64 1
  %539 = fadd reassoc ninf nsz float %537, %538
  %540 = fmul reassoc ninf nsz float %536, %539
  %541 = fadd reassoc ninf nsz float %540, %.956
  %542 = add i32 %533, 1
  %543 = sext i32 %542 to i64
  %544 = getelementptr float, float* %531, i64 %543
  %545 = load float, float* %544, align 4
  %546 = fsub reassoc ninf nsz float %537, %538
  %547 = fmul reassoc ninf nsz float %545, %546
  %548 = fadd reassoc ninf nsz float %547, %.945
  %549 = add i32 %533, 2
  %550 = sext i32 %549 to i64
  %551 = getelementptr float, float* %531, i64 %550
  %552 = load float, float* %551, align 4
  %553 = fmul reassoc ninf nsz float %552, %539
  %554 = fadd reassoc ninf nsz float %553, %.9
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27
  %.1057 = phi float [ %541, %true_block28 ], [ %.956, %after_if27 ]
  %.1046 = phi float [ %548, %true_block28 ], [ %.945, %after_if27 ]
  %.10 = phi float [ %554, %true_block28 ], [ %.9, %after_if27 ]
  %555 = load float*, float** %42, align 8
  %556 = load i32, i32* %43, align 4
  %557 = load i32, i32* %44, align 4
  %558 = mul i32 %556, %61
  %559 = add i32 %558, %66
  %560 = mul i32 %559, %557
  %561 = sext i32 %560 to i64
  %562 = getelementptr float, float* %555, i64 %561
  store float %.1057, float* %562, align 4
  %563 = load float*, float** %42, align 8
  %564 = load i32, i32* %43, align 4
  %565 = load i32, i32* %44, align 4
  %566 = mul i32 %564, %61
  %567 = add i32 %566, %66
  %568 = mul i32 %567, %565
  %569 = add i32 %568, 1
  %570 = sext i32 %569 to i64
  %571 = getelementptr float, float* %563, i64 %570
  store float %.1046, float* %571, align 4
  %572 = load float*, float** %42, align 8
  %573 = load i32, i32* %43, align 4
  %574 = load i32, i32* %44, align 4
  %575 = mul i32 %573, %61
  %576 = add i32 %575, %66
  %577 = mul i32 %576, %574
  %578 = add i32 %577, 2
  %579 = sext i32 %578 to i64
  %580 = getelementptr float, float* %572, i64 %579
  store float %.10, float* %580, align 4
  %581 = add nsw i32 %.05860, 1
  %exitcond.not = icmp eq i32 %19, %581
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
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
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

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
