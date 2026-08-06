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
define void @_nlm_1ch_s3_p1_c408_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %1, i64 0, i32 4
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 20
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fmul reassoc ninf nsz float %4, 3.500000e+00
  %13 = fadd reassoc ninf nsz float %12, 0x3F60624DE0000000
  %14 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 16
  %18 = bitcast i8* %17 to float*
  store float %13, float* %18, align 4
  %19 = fmul reassoc ninf nsz float %3, 0x3FE6666660000000
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %20, i64 0, i32 6
  %22 = load float, float* %21, align 4
  %23 = fmul reassoc ninf nsz float %19, %22
  %24 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 24
  %28 = bitcast i8* %27 to float*
  store float %23, float* %28, align 4
  %29 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %29, i64 0, i32 2
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 8
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %39 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %38, i64 0, i32 3
  %40 = load i32, i32* %39, align 4
  %41 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %41, i64 0, i32 14
  %43 = load i8*, i8** %42, align 8
  %44 = getelementptr inbounds i8, i8* %43, i64 12
  %45 = bitcast i8* %44 to i32*
  store i32 %40, i32* %45, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %47 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  store i32 %46, i32* %51, align 4
  %52 = mul i32 %46, %37
  %53 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %53, i64 0, i32 14
  %55 = bitcast i8** %54 to i32**
  %56 = load i32*, i32** %55, align 8
  store i32 %52, i32* %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_nlm_1ch_s3_p1_c408_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 5
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = add i32 %17, -3
  %28 = add i32 %17, -2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv104 = phi i32 [ %28, %for_loop_body.lr.ph ], [ %lsr.iv.next105, %after_if47 ]
  %lsr.iv102 = phi i32 [ %27, %for_loop_body.lr.ph ], [ %lsr.iv.next103, %after_if47 ]
  %.05782 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %288, %after_if47 ]
  %29 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.05782, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.05782
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.05782, 0
  %40 = icmp ne i32 %36, %.05782
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg63 = sext i1 %42 to i32
  %43 = getelementptr inbounds i8, i8* %31, i64 8
  %44 = bitcast i8* %43 to i32*
  %45 = load i32, i32* %44, align 4
  %46 = add i32 %45, -1
  %47 = getelementptr inbounds i8, i8* %31, i64 12
  %48 = bitcast i8* %47 to i32*
  %49 = load i32, i32* %48, align 4
  %50 = add i32 %49, -1
  %51 = load float*, float** %25, align 8
  %52 = load i32, i32* %26, align 4
  %53 = insertelement <2 x i32> poison, i32 %50, i64 0
  %54 = shufflevector <2 x i32> %53, <2 x i32> poison, <2 x i32> zeroinitializer
  %55 = add i32 %35, %.neg63
  %56 = mul i32 %55, %34
  %57 = sub i32 %.05782, %56
  %58 = add i32 %57, -1
  %59 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %60 = tail call i32 @llvm.smin.i32(i32 %50, i32 %59)
  %61 = add i32 %55, -1
  %62 = insertelement <2 x i32> poison, i32 %61, i64 0
  %63 = insertelement <2 x i32> %62, i32 %55, i64 1
  %64 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %63, <2 x i32> zeroinitializer)
  %65 = insertelement <2 x i32> poison, i32 %46, i64 0
  %66 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %67 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %66, <2 x i32> %64)
  %68 = extractelement <2 x i32> %67, i64 0
  %69 = mul i32 %52, %68
  %70 = add i32 %69, %60
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, float* %51, i64 %71
  %73 = load float, float* %72, align 4
  %74 = fmul reassoc ninf nsz float %73, %73
  %75 = add i32 %57, 1
  %76 = insertelement <2 x i32> poison, i32 %57, i64 0
  %77 = insertelement <2 x i32> %76, i32 %75, i64 1
  %78 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %77, <2 x i32> zeroinitializer)
  %79 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %54, <2 x i32> %78)
  %80 = extractelement <2 x i32> %79, i64 0
  %81 = add i32 %69, %80
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, float* %51, i64 %82
  %84 = load float, float* %83, align 4
  %85 = fadd reassoc ninf nsz float %84, %73
  %86 = fmul reassoc ninf nsz float %84, %84
  %87 = fadd reassoc ninf nsz float %86, %74
  %88 = extractelement <2 x i32> %79, i64 1
  %89 = add i32 %69, %88
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, float* %51, i64 %90
  %92 = load float, float* %91, align 4
  %93 = fadd reassoc ninf nsz float %92, %85
  %94 = fmul reassoc ninf nsz float %92, %92
  %95 = fadd reassoc ninf nsz float %94, %87
  %96 = extractelement <2 x i32> %67, i64 1
  %97 = mul i32 %52, %96
  %98 = add i32 %97, %60
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %51, i64 %99
  %101 = load float, float* %100, align 4
  %102 = fadd reassoc ninf nsz float %101, %93
  %103 = fmul reassoc ninf nsz float %101, %101
  %104 = fadd reassoc ninf nsz float %103, %95
  %105 = add i32 %97, %80
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, float* %51, i64 %106
  %108 = load float, float* %107, align 4
  %109 = fadd reassoc ninf nsz float %108, %102
  %110 = fmul reassoc ninf nsz float %108, %108
  %111 = fadd reassoc ninf nsz float %110, %104
  %112 = add i32 %97, %88
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %51, i64 %113
  %115 = load float, float* %114, align 4
  %116 = fadd reassoc ninf nsz float %115, %109
  %117 = fmul reassoc ninf nsz float %115, %115
  %118 = fadd reassoc ninf nsz float %117, %111
  %119 = add i32 %55, 1
  %120 = tail call i32 @llvm.smax.i32(i32 %119, i32 0)
  %121 = tail call i32 @llvm.smin.i32(i32 %46, i32 %120)
  %122 = mul i32 %52, %121
  %123 = add i32 %122, %60
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %51, i64 %124
  %126 = load float, float* %125, align 4
  %127 = fadd reassoc ninf nsz float %126, %116
  %128 = fmul reassoc ninf nsz float %126, %126
  %129 = fadd reassoc ninf nsz float %128, %118
  %130 = add i32 %122, %80
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, float* %51, i64 %131
  %133 = load float, float* %132, align 4
  %134 = fadd reassoc ninf nsz float %133, %127
  %135 = fmul reassoc ninf nsz float %133, %133
  %136 = fadd reassoc ninf nsz float %135, %129
  %137 = add i32 %122, %88
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %51, i64 %138
  %140 = load float, float* %139, align 4
  %141 = fadd reassoc ninf nsz float %140, %134
  %142 = fmul reassoc ninf nsz float %140, %140
  %143 = fadd reassoc ninf nsz float %142, %136
  %144 = fmul reassoc ninf nsz float %141, 0x3FBC71C720000000
  %145 = fmul reassoc ninf nsz float %143, 0x3FBC71C720000000
  %146 = fmul reassoc ninf nsz float %144, %144
  %147 = fsub reassoc ninf nsz float %145, %146
  %148 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %147, float 0.000000e+00)
  %149 = fmul reassoc ninf nsz float %148, -3.500000e+02
  %150 = tail call float @expf(float noundef %149) #1
  %151 = insertelement <8 x i32> poison, i32 %60, i64 0
  %152 = shufflevector <2 x i32> %79, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %153 = shufflevector <8 x i32> %151, <8 x i32> %152, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle98 = shufflevector <8 x i32> %153, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 1, i32 2, i32 0, i32 1>
  %154 = sub i32 %lsr.iv102, %56
  %155 = sub i32 %lsr.iv104, %56
  %156 = add i32 %35, -3
  %157 = add i32 %156, %.neg63
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv106 = phi i32 [ %157, %for_loop_body ], [ %lsr.iv.next107, %for_loop_inc10 ]
  %.04381 = phi i32 [ -3, %for_loop_body ], [ %160, %for_loop_inc10 ]
  %.14580 = phi float [ 0.000000e+00, %for_loop_body ], [ %.044, %for_loop_inc10 ]
  %.14879 = phi float [ 0.000000e+00, %for_loop_body ], [ %.047, %for_loop_inc10 ]
  %158 = add i32 %.04381, %55
  %159 = icmp slt i32 %158, 0
  br i1 %159, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.047 = phi float [ %.14879, %false_block ], [ %.14879, %for_loop_body9 ], [ %.249, %for_loop_inc10.loopexit ]
  %.044 = phi float [ %.14580, %false_block ], [ %.14580, %for_loop_body9 ], [ %.246, %for_loop_inc10.loopexit ]
  %160 = add nsw i32 %.04381, 1
  %lsr.iv.next107 = add i32 %lsr.iv106, 1
  %exitcond85.not = icmp eq i32 %160, 4
  br i1 %exitcond85.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %161 = fsub reassoc ninf nsz float 1.000000e+00, %150
  %162 = fcmp reassoc ninf nsz ogt float %.047, 0x3D71979980000000
  br i1 %162, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %163 = load i32, i32* %44, align 4
  %.not64 = icmp slt i32 %158, %163
  br i1 %.not64, label %after_if15, label %for_loop_inc10

after_if15:                                       ; preds = %false_block
  %.not = icmp ne i32 %.04381, 0
  %164 = add i32 %158, -1
  %165 = tail call i32 @llvm.smax.i32(i32 %164, i32 0)
  %166 = tail call i32 @llvm.smin.i32(i32 %46, i32 %165)
  %167 = add i32 %158, 1
  %168 = insertelement <2 x i32> poison, i32 %158, i64 0
  %169 = insertelement <2 x i32> %168, i32 %167, i64 1
  %170 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %169, <2 x i32> zeroinitializer)
  %171 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %66, <2 x i32> %170)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %after_if15
  %lsr.iv = phi i32 [ 0, %after_if15 ], [ %lsr.iv.next, %for_loop_inc17 ]
  %.377 = phi float [ %.14580, %after_if15 ], [ %.246, %for_loop_inc17 ]
  %.35076 = phi float [ %.14879, %after_if15 ], [ %.249, %for_loop_inc17 ]
  %172 = add i32 %154, %lsr.iv
  %173 = icmp slt i32 %172, 0
  br i1 %173, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.249 = phi float [ %.35076, %false_block21 ], [ %234, %true_block41 ], [ %.35076, %after_if32 ], [ %.35076, %for_loop_body16 ]
  %.246 = phi float [ %.377, %false_block21 ], [ %243, %true_block41 ], [ %.377, %after_if32 ], [ %.377, %for_loop_body16 ]
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 7
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %174 = load i32, i32* %48, align 4
  %.not65 = icmp slt i32 %172, %174
  br i1 %.not65, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %175 = icmp ne i32 %lsr.iv, 3
  %spec.select = select i1 %.not, i1 true, i1 %175
  br i1 %spec.select, label %for_loop_test36.preheader, label %after_if32

for_loop_test36.preheader:                        ; preds = %after_if25
  %176 = load float*, float** %25, align 8
  %177 = load i32, i32* %26, align 4
  %178 = call i32 @llvm.smax.i32(i32 %172, i32 1)
  %179 = add nsw i32 %178, -1
  %180 = mul i32 %177, %166
  %181 = insertelement <2 x i32> poison, i32 %179, i64 0
  %182 = insertelement <2 x i32> %181, i32 %172, i64 1
  %183 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %54, <2 x i32> %182)
  %184 = add i32 %155, %lsr.iv
  %185 = tail call i32 @llvm.smin.i32(i32 %50, i32 %184)
  %186 = insertelement <2 x i32> poison, i32 %177, i64 0
  %187 = shufflevector <2 x i32> %186, <2 x i32> poison, <2 x i32> zeroinitializer
  %188 = mul <2 x i32> %187, %67
  %189 = mul i32 %177, %121
  %190 = mul <2 x i32> %187, %171
  %191 = shufflevector <2 x i32> %188, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %192 = insertelement <8 x i32> %191, i32 %189, i64 2
  %shuffle97 = shufflevector <8 x i32> %192, <8 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 2, i32 2>
  %193 = add <8 x i32> %shuffle97, %shuffle98
  %194 = sext <8 x i32> %193 to <8 x i64>
  %195 = insertelement <8 x float*> poison, float* %176, i64 0
  %shuffle = shufflevector <8 x float*> %195, <8 x float*> poison, <8 x i32> zeroinitializer
  %196 = getelementptr float, <8 x float*> %shuffle, <8 x i64> %194
  %197 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %196, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %198 = insertelement <8 x i32> poison, i32 %180, i64 0
  %199 = shufflevector <2 x i32> %190, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %200 = shufflevector <8 x i32> %198, <8 x i32> %199, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle100 = shufflevector <8 x i32> %200, <8 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 2, i32 2>
  %201 = shufflevector <2 x i32> %183, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %202 = insertelement <8 x i32> %201, i32 %185, i64 2
  %shuffle101 = shufflevector <8 x i32> %202, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 1, i32 2, i32 0, i32 1>
  %203 = add <8 x i32> %shuffle100, %shuffle101
  %204 = sext <8 x i32> %203 to <8 x i64>
  %205 = getelementptr float, <8 x float*> %shuffle, <8 x i64> %204
  %206 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %205, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %207 = fsub reassoc ninf nsz <8 x float> %197, %206
  %208 = fmul reassoc ninf nsz <8 x float> %207, %207
  %209 = add i32 %189, %88
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, float* %176, i64 %210
  %212 = load float, float* %211, align 4
  %213 = extractelement <2 x i32> %190, i64 1
  %214 = add i32 %213, %185
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, float* %176, i64 %215
  %217 = load float, float* %216, align 4
  %218 = fsub reassoc ninf nsz float %212, %217
  %219 = fmul reassoc ninf nsz float %218, %218
  %220 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float %219, <8 x float> %208)
  %221 = fmul reassoc ninf nsz float %220, 0x3FBC71C720000000
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.039 = phi float [ %221, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %222 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %223 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %222, i64 0, i32 14
  %224 = load i8*, i8** %223, align 8
  %225 = getelementptr inbounds i8, i8* %224, i64 16
  %226 = bitcast i8* %225 to float*
  %227 = load float, float* %226, align 4
  %228 = fcmp reassoc ninf nsz ugt float %.039, %227
  br i1 %228, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.039
  %229 = getelementptr inbounds i8, i8* %224, i64 20
  %230 = bitcast i8* %229 to float*
  %231 = load float, float* %230, align 4
  %232 = fmul reassoc ninf nsz float %231, %neg44
  %233 = tail call float @expf(float noundef %232) #1
  %234 = fadd reassoc ninf nsz float %233, %.35076
  %235 = load float*, float** %25, align 8
  %236 = load i32, i32* %26, align 4
  %237 = mul i32 %lsr.iv106, %236
  %238 = add i32 %172, %237
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, float* %235, i64 %239
  %241 = load float, float* %240, align 4
  %242 = fmul reassoc ninf nsz float %241, %233
  %243 = fadd reassoc ninf nsz float %242, %.377
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %244 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %161, float 0x3FE6666660000000)
  %245 = fdiv reassoc ninf nsz float %.044, %.047
  %246 = load float*, float** %25, align 8
  %247 = load i32, i32* %26, align 4
  %248 = mul i32 %247, %55
  %249 = add i32 %248, %57
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, float* %246, i64 %250
  %252 = load float, float* %251, align 4
  %253 = fsub reassoc ninf nsz float %252, %245
  %254 = tail call float @llvm.fabs.f32(float %253)
  %255 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %256 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %255, i64 0, i32 14
  %257 = load i8*, i8** %256, align 8
  %258 = getelementptr inbounds i8, i8* %257, i64 24
  %259 = bitcast i8* %258 to float*
  %260 = load float, float* %259, align 4
  %261 = fsub reassoc ninf nsz float %254, %260
  %262 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %261, float 0.000000e+00)
  %263 = fcmp reassoc ninf nsz oge float %253, 0.000000e+00
  %264 = uitofp i1 %263 to float
  %265 = fcmp reassoc ninf nsz ole float %253, 0.000000e+00
  %266 = uitofp i1 %265 to float
  %267 = fsub reassoc ninf nsz float %264, %266
  %268 = fmul reassoc ninf nsz float %244, %23
  %269 = fmul reassoc ninf nsz float %268, %267
  %270 = fmul reassoc ninf nsz float %269, %262
  %271 = fadd reassoc ninf nsz float %270, %245
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %272 = load float*, float** %25, align 8
  %273 = load i32, i32* %26, align 4
  %274 = mul i32 %273, %55
  %275 = add i32 %274, %57
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, float* %272, i64 %276
  %278 = load float, float* %277, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink = phi float [ %278, %false_block46 ], [ %271, %true_block45 ]
  %279 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %280 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %279, i64 0, i32 1, i32 1
  %281 = load float*, float** %280, align 8
  %282 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %279, i64 0, i32 1, i32 0, i32 1
  %283 = load i32, i32* %282, align 4
  %284 = mul i32 %283, %55
  %285 = add i32 %284, %57
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, float* %281, i64 %286
  store float %.sink, float* %287, align 4
  %288 = add nsw i32 %.05782, 1
  %lsr.iv.next103 = add i32 %lsr.iv102, 1
  %lsr.iv.next105 = add i32 %lsr.iv104, 1
  %exitcond86.not = icmp eq i32 %288, %19
  br i1 %exitcond86.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @expf(float noundef) local_unnamed_addr #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #5 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #10

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #10

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone willreturn }
attributes #10 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
