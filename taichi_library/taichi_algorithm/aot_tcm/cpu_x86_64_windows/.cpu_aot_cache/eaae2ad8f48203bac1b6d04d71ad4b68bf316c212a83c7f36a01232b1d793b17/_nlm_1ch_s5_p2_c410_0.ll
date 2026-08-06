; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext*, void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { i8*, %struct.LLVMRuntime*, i32, i64* }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager*], [1024 x %struct.NodeManager*], [1024 x i8*], i8*, %struct.RandState*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { i8*, i8*, i64 }
%struct.ListManager = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime* }
%struct.NodeManager = type { %struct.LLVMRuntime*, i32, i32, i32, i32, %struct.ListManager*, %struct.ListManager*, %struct.ListManager*, i32 }
%struct.RandState = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_nlm_1ch_s5_p2_c410_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %1, i64 0, i32 4
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 20
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fmul reassoc ninf nsz float %4, 3.500000e+00
  %13 = fadd reassoc ninf nsz float %12, 0x3F60624DE0000000
  %14 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 16
  %18 = bitcast i8* %17 to float*
  store float %13, float* %18, align 4
  %19 = fmul reassoc ninf nsz float %3, 0x3FE6666660000000
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %20, i64 0, i32 6
  %22 = load float, float* %21, align 4
  %23 = fmul reassoc ninf nsz float %19, %22
  %24 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 24
  %28 = bitcast i8* %27 to float*
  store float %23, float* %28, align 4
  %29 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %29, i64 0, i32 2
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 8
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %39 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %38, i64 0, i32 3
  %40 = load i32, i32* %39, align 4
  %41 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %41, i64 0, i32 14
  %43 = load i8*, i8** %42, align 8
  %44 = getelementptr inbounds i8, i8* %43, i64 12
  %45 = bitcast i8* %44 to i32*
  store i32 %40, i32* %45, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %47 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  store i32 %46, i32* %51, align 4
  %52 = mul i32 %46, %37
  %53 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %53, i64 0, i32 14
  %55 = bitcast i8** %54 to i32**
  %56 = load i32*, i32** %55, align 8
  store i32 %52, i32* %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_nlm_1ch_s5_p2_c410_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext* %context, %struct.RuntimeContext** %4, align 8
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext*, i8*, i32)* @function_body, void (%struct.RuntimeContext*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 5
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = add i32 %17, -5
  %28 = add i32 %17, -3
  %29 = add i32 %17, -4
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv120 = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next121, %after_if47 ]
  %lsr.iv118 = phi i32 [ %28, %for_loop_body.lr.ph ], [ %lsr.iv.next119, %after_if47 ]
  %lsr.iv116 = phi i32 [ %27, %for_loop_body.lr.ph ], [ %lsr.iv.next117, %after_if47 ]
  %.05782 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %332, %after_if47 ]
  %30 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %.05782, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.05782
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.05782, 0
  %41 = icmp ne i32 %37, %.05782
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg63 = sext i1 %43 to i32
  %44 = getelementptr inbounds i8, i8* %32, i64 8
  %45 = bitcast i8* %44 to i32*
  %46 = load i32, i32* %45, align 4
  %47 = add i32 %46, -1
  %48 = getelementptr inbounds i8, i8* %32, i64 12
  %49 = bitcast i8* %48 to i32*
  %50 = load i32, i32* %49, align 4
  %51 = add i32 %50, -1
  %52 = load float*, float** %25, align 8
  %53 = load i32, i32* %26, align 4
  %54 = add i32 %36, %.neg63
  %55 = mul i32 %54, %35
  %56 = add i32 %54, 1
  %57 = insertelement <2 x i32> poison, i32 %54, i64 0
  %58 = shufflevector <2 x i32> %57, <2 x i32> poison, <2 x i32> zeroinitializer
  %59 = add <2 x i32> %58, <i32 -2, i32 -1>
  %60 = shufflevector <2 x i32> %59, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %61 = insertelement <4 x i32> %60, i32 %54, i64 2
  %62 = insertelement <4 x i32> %61, i32 %56, i64 3
  %63 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %62, <4 x i32> zeroinitializer)
  %64 = insertelement <4 x i32> poison, i32 %47, i64 0
  %shuffle98 = shufflevector <4 x i32> %64, <4 x i32> poison, <4 x i32> zeroinitializer
  %65 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle98, <4 x i32> %63)
  %66 = extractelement <4 x i32> %65, i64 3
  %67 = mul i32 %53, %66
  %68 = sub i32 %.05782, %55
  %69 = add i32 %68, -1
  %70 = add i32 %68, 1
  %71 = add i32 %68, 2
  %72 = insertelement <4 x i32> poison, i32 %69, i64 0
  %73 = insertelement <4 x i32> %72, i32 %68, i64 1
  %74 = insertelement <4 x i32> %73, i32 %70, i64 2
  %75 = insertelement <4 x i32> %74, i32 %71, i64 3
  %76 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %75, <4 x i32> zeroinitializer)
  %77 = insertelement <4 x i32> poison, i32 %51, i64 0
  %shuffle114 = shufflevector <4 x i32> %77, <4 x i32> poison, <4 x i32> zeroinitializer
  %78 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle114, <4 x i32> %76)
  %79 = extractelement <4 x i32> %78, i64 0
  %80 = extractelement <4 x i32> %78, i64 1
  %81 = extractelement <4 x i32> %78, i64 2
  %82 = insertelement <2 x i32> poison, i32 %53, i64 0
  %83 = shufflevector <2 x i32> %82, <2 x i32> poison, <2 x i32> zeroinitializer
  %84 = shufflevector <4 x i32> %65, <4 x i32> undef, <2 x i32> <i32 1, i32 2>
  %85 = mul <2 x i32> %83, %84
  %shuffle115 = shufflevector <2 x i32> %85, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 0, i32 1>
  %86 = shufflevector <4 x i32> %78, <4 x i32> undef, <4 x i32> <i32 0, i32 1, i32 2, i32 0>
  %87 = add <4 x i32> %shuffle115, %86
  %88 = sext <4 x i32> %87 to <4 x i64>
  %89 = extractelement <4 x i64> %88, i64 0
  %90 = getelementptr float, float* %52, i64 %89
  %91 = load float, float* %90, align 4
  %92 = fmul reassoc ninf nsz float %91, %91
  %93 = extractelement <4 x i64> %88, i64 1
  %94 = getelementptr float, float* %52, i64 %93
  %95 = load float, float* %94, align 4
  %96 = fadd reassoc ninf nsz float %95, %91
  %97 = fmul reassoc ninf nsz float %95, %95
  %98 = fadd reassoc ninf nsz float %97, %92
  %99 = extractelement <4 x i64> %88, i64 2
  %100 = getelementptr float, float* %52, i64 %99
  %101 = load float, float* %100, align 4
  %102 = fadd reassoc ninf nsz float %101, %96
  %103 = fmul reassoc ninf nsz float %101, %101
  %104 = fadd reassoc ninf nsz float %103, %98
  %105 = extractelement <4 x i64> %88, i64 3
  %106 = getelementptr float, float* %52, i64 %105
  %107 = load float, float* %106, align 4
  %108 = fadd reassoc ninf nsz float %107, %102
  %109 = fmul reassoc ninf nsz float %107, %107
  %110 = fadd reassoc ninf nsz float %109, %104
  %111 = extractelement <2 x i32> %85, i64 1
  %112 = add i32 %111, %80
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %52, i64 %113
  %115 = load float, float* %114, align 4
  %116 = fadd reassoc ninf nsz float %115, %108
  %117 = fmul reassoc ninf nsz float %115, %115
  %118 = fadd reassoc ninf nsz float %117, %110
  %119 = add i32 %111, %81
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %52, i64 %120
  %122 = load float, float* %121, align 4
  %123 = fadd reassoc ninf nsz float %122, %116
  %124 = fmul reassoc ninf nsz float %122, %122
  %125 = fadd reassoc ninf nsz float %124, %118
  %126 = add i32 %67, %79
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, float* %52, i64 %127
  %129 = load float, float* %128, align 4
  %130 = fadd reassoc ninf nsz float %129, %123
  %131 = fmul reassoc ninf nsz float %129, %129
  %132 = fadd reassoc ninf nsz float %131, %125
  %133 = add i32 %67, %80
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %52, i64 %134
  %136 = load float, float* %135, align 4
  %137 = fadd reassoc ninf nsz float %136, %130
  %138 = fmul reassoc ninf nsz float %136, %136
  %139 = fadd reassoc ninf nsz float %138, %132
  %140 = add i32 %67, %81
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %52, i64 %141
  %143 = load float, float* %142, align 4
  %144 = fadd reassoc ninf nsz float %143, %137
  %145 = fmul reassoc ninf nsz float %143, %143
  %146 = fadd reassoc ninf nsz float %145, %139
  %147 = fmul reassoc ninf nsz float %144, 0x3FBC71C720000000
  %148 = fmul reassoc ninf nsz float %146, 0x3FBC71C720000000
  %149 = fmul reassoc ninf nsz float %147, %147
  %150 = fsub reassoc ninf nsz float %148, %149
  %151 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %150, float 0.000000e+00)
  %152 = fmul reassoc ninf nsz float %151, -3.500000e+02
  %153 = tail call float @expf(float noundef %152) #1
  %154 = add i32 %68, -2
  %155 = tail call i32 @llvm.smax.i32(i32 %154, i32 0)
  %156 = tail call i32 @llvm.smin.i32(i32 %51, i32 %155)
  %157 = add i32 %54, 2
  %158 = tail call i32 @llvm.smax.i32(i32 %157, i32 0)
  %159 = tail call i32 @llvm.smin.i32(i32 %47, i32 %158)
  %160 = insertelement <16 x i32> poison, i32 %156, i64 0
  %161 = shufflevector <4 x i32> %78, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %162 = shufflevector <4 x i32> %78, <4 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %163 = shufflevector <16 x i32> %160, <16 x i32> %162, <16 x i32> <i32 0, i32 16, i32 17, i32 18, i32 19, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle100 = shufflevector <16 x i32> %163, <16 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0>
  %164 = insertelement <8 x i32> %161, i32 %156, i64 4
  %shuffle108 = shufflevector <8 x i32> %164, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2>
  %165 = extractelement <4 x i32> %78, i64 3
  %166 = sub i32 %lsr.iv116, %55
  %167 = sub i32 %lsr.iv118, %55
  %168 = sub i32 %lsr.iv120, %55
  %169 = add i32 %36, -5
  %170 = add i32 %169, %.neg63
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv122 = phi i32 [ %170, %for_loop_body ], [ %lsr.iv.next123, %for_loop_inc10 ]
  %.04381 = phi i32 [ -5, %for_loop_body ], [ %173, %for_loop_inc10 ]
  %.14580 = phi float [ 0.000000e+00, %for_loop_body ], [ %.044, %for_loop_inc10 ]
  %.14879 = phi float [ 0.000000e+00, %for_loop_body ], [ %.047, %for_loop_inc10 ]
  %171 = add i32 %.04381, %54
  %172 = icmp slt i32 %171, 0
  br i1 %172, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.047 = phi float [ %.14879, %false_block ], [ %.14879, %for_loop_body9 ], [ %.249, %for_loop_inc10.loopexit ]
  %.044 = phi float [ %.14580, %false_block ], [ %.14580, %for_loop_body9 ], [ %.246, %for_loop_inc10.loopexit ]
  %173 = add nsw i32 %.04381, 1
  %lsr.iv.next123 = add i32 %lsr.iv122, 1
  %exitcond85.not = icmp eq i32 %173, 6
  br i1 %exitcond85.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %174 = fsub reassoc ninf nsz float 1.000000e+00, %153
  %175 = fcmp reassoc ninf nsz ogt float %.047, 0x3D71979980000000
  br i1 %175, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %176 = load i32, i32* %45, align 4
  %.not64 = icmp slt i32 %171, %176
  br i1 %.not64, label %after_if15, label %for_loop_inc10

after_if15:                                       ; preds = %false_block
  %.not = icmp ne i32 %.04381, 0
  %177 = insertelement <2 x i32> poison, i32 %171, i64 0
  %178 = shufflevector <2 x i32> %177, <2 x i32> poison, <2 x i32> zeroinitializer
  %179 = add <2 x i32> %178, <i32 -2, i32 -1>
  %180 = add i32 %171, 1
  %181 = shufflevector <2 x i32> %179, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %182 = insertelement <4 x i32> %181, i32 %171, i64 2
  %183 = insertelement <4 x i32> %182, i32 %180, i64 3
  %184 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %183, <4 x i32> zeroinitializer)
  %185 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle98, <4 x i32> %184)
  %186 = add i32 %171, 2
  %187 = tail call i32 @llvm.smax.i32(i32 %186, i32 0)
  %188 = tail call i32 @llvm.smin.i32(i32 %47, i32 %187)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %after_if15
  %lsr.iv = phi i32 [ 0, %after_if15 ], [ %lsr.iv.next, %for_loop_inc17 ]
  %.377 = phi float [ %.14580, %after_if15 ], [ %.246, %for_loop_inc17 ]
  %.35076 = phi float [ %.14879, %after_if15 ], [ %.249, %for_loop_inc17 ]
  %189 = add i32 %166, %lsr.iv
  %190 = icmp slt i32 %189, 0
  br i1 %190, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.249 = phi float [ %.35076, %false_block21 ], [ %278, %true_block41 ], [ %.35076, %after_if32 ], [ %.35076, %for_loop_body16 ]
  %.246 = phi float [ %.377, %false_block21 ], [ %287, %true_block41 ], [ %.377, %after_if32 ], [ %.377, %for_loop_body16 ]
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 11
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %191 = load i32, i32* %49, align 4
  %.not65 = icmp slt i32 %189, %191
  br i1 %.not65, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %192 = icmp ne i32 %lsr.iv, 5
  %spec.select = select i1 %.not, i1 true, i1 %192
  br i1 %spec.select, label %for_loop_test36.preheader, label %after_if32

for_loop_test36.preheader:                        ; preds = %after_if25
  %193 = load float*, float** %25, align 8
  %194 = load i32, i32* %26, align 4
  %195 = call i32 @llvm.smax.i32(i32 %189, i32 2)
  %196 = add nsw i32 %195, -2
  %197 = tail call i32 @llvm.smin.i32(i32 %51, i32 %196)
  %198 = call i32 @llvm.smax.i32(i32 %189, i32 1)
  %199 = add nsw i32 %198, -1
  %200 = add i32 %168, %lsr.iv
  %201 = add i32 %167, %lsr.iv
  %202 = tail call i32 @llvm.smax.i32(i32 %201, i32 0)
  %203 = insertelement <4 x i32> poison, i32 %199, i64 0
  %204 = insertelement <4 x i32> %203, i32 %189, i64 1
  %205 = insertelement <4 x i32> %204, i32 %200, i64 2
  %206 = insertelement <4 x i32> %205, i32 %202, i64 3
  %207 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle114, <4 x i32> %206)
  %208 = insertelement <4 x i32> poison, i32 %194, i64 0
  %shuffle97 = shufflevector <4 x i32> %208, <4 x i32> poison, <4 x i32> zeroinitializer
  %209 = mul <4 x i32> %shuffle97, %65
  %shuffle99 = shufflevector <4 x i32> %209, <4 x i32> poison, <16 x i32> <i32 0, i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1, i32 1, i32 2, i32 2, i32 2, i32 2, i32 2, i32 3>
  %210 = mul <4 x i32> %shuffle97, %185
  %shuffle104 = shufflevector <4 x i32> %210, <4 x i32> poison, <16 x i32> <i32 0, i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1, i32 1, i32 2, i32 2, i32 2, i32 2, i32 2, i32 3>
  %211 = add <16 x i32> %shuffle99, %shuffle100
  %212 = sext <16 x i32> %211 to <16 x i64>
  %213 = insertelement <16 x float*> poison, float* %193, i64 0
  %shuffle = shufflevector <16 x float*> %213, <16 x float*> poison, <16 x i32> zeroinitializer
  %214 = getelementptr float, <16 x float*> %shuffle, <16 x i64> %212
  %215 = call <16 x float> @llvm.masked.gather.v16f32.v16p0f32(<16 x float*> %214, i32 4, <16 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <16 x float> undef)
  %216 = insertelement <16 x i32> poison, i32 %197, i64 0
  %217 = shufflevector <4 x i32> %207, <4 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %218 = shufflevector <16 x i32> %216, <16 x i32> %217, <16 x i32> <i32 0, i32 16, i32 17, i32 18, i32 19, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle105 = shufflevector <16 x i32> %218, <16 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0>
  %219 = add <16 x i32> %shuffle104, %shuffle105
  %220 = sext <16 x i32> %219 to <16 x i64>
  %221 = getelementptr float, <16 x float*> %shuffle, <16 x i64> %220
  %222 = call <16 x float> @llvm.masked.gather.v16f32.v16p0f32(<16 x float*> %221, i32 4, <16 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <16 x float> undef)
  %223 = fsub reassoc ninf nsz <16 x float> %215, %222
  %224 = fmul reassoc ninf nsz <16 x float> %223, %223
  %225 = extractelement <4 x i32> %209, i64 3
  %226 = extractelement <4 x i32> %210, i64 3
  %227 = mul i32 %194, %159
  %228 = mul i32 %194, %188
  %229 = insertelement <8 x i32> poison, i32 %225, i64 0
  %230 = insertelement <8 x i32> %229, i32 %225, i64 1
  %231 = insertelement <8 x i32> %230, i32 %225, i64 2
  %232 = insertelement <8 x i32> %231, i32 %225, i64 3
  %233 = insertelement <8 x i32> %232, i32 %227, i64 4
  %shuffle107 = shufflevector <8 x i32> %233, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 4, i32 4, i32 4>
  %234 = add <8 x i32> %shuffle107, %shuffle108
  %235 = sext <8 x i32> %234 to <8 x i64>
  %236 = insertelement <8 x float*> poison, float* %193, i64 0
  %shuffle106 = shufflevector <8 x float*> %236, <8 x float*> poison, <8 x i32> zeroinitializer
  %237 = getelementptr float, <8 x float*> %shuffle106, <8 x i64> %235
  %238 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %237, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %239 = insertelement <8 x i32> poison, i32 %226, i64 0
  %240 = insertelement <8 x i32> %239, i32 %226, i64 1
  %241 = insertelement <8 x i32> %240, i32 %226, i64 2
  %242 = insertelement <8 x i32> %241, i32 %226, i64 3
  %243 = insertelement <8 x i32> %242, i32 %228, i64 4
  %shuffle110 = shufflevector <8 x i32> %243, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 4, i32 4, i32 4>
  %244 = shufflevector <4 x i32> %207, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %245 = insertelement <8 x i32> %244, i32 %197, i64 4
  %shuffle111 = shufflevector <8 x i32> %245, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2>
  %246 = add <8 x i32> %shuffle110, %shuffle111
  %247 = sext <8 x i32> %246 to <8 x i64>
  %248 = getelementptr float, <8 x float*> %shuffle106, <8 x i64> %247
  %249 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %248, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %250 = fsub reassoc ninf nsz <8 x float> %238, %249
  %251 = fmul reassoc ninf nsz <8 x float> %250, %250
  %252 = add i32 %227, %165
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, float* %193, i64 %253
  %255 = load float, float* %254, align 4
  %256 = extractelement <4 x i32> %207, i64 3
  %257 = add i32 %228, %256
  %258 = sext i32 %257 to i64
  %259 = getelementptr float, float* %193, i64 %258
  %260 = load float, float* %259, align 4
  %261 = fsub reassoc ninf nsz float %255, %260
  %262 = fmul reassoc ninf nsz float %261, %261
  %263 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %251)
  %264 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v16f32(float %263, <16 x float> %224)
  %op.rdx112 = fadd reassoc ninf nsz float %264, %262
  %265 = fmul reassoc ninf nsz float %op.rdx112, 0x3FA47AE140000000
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.039 = phi float [ %265, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %266 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %267 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %266, i64 0, i32 14
  %268 = load i8*, i8** %267, align 8
  %269 = getelementptr inbounds i8, i8* %268, i64 16
  %270 = bitcast i8* %269 to float*
  %271 = load float, float* %270, align 4
  %272 = fcmp reassoc ninf nsz ugt float %.039, %271
  br i1 %272, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.039
  %273 = getelementptr inbounds i8, i8* %268, i64 20
  %274 = bitcast i8* %273 to float*
  %275 = load float, float* %274, align 4
  %276 = fmul reassoc ninf nsz float %275, %neg44
  %277 = tail call float @expf(float noundef %276) #1
  %278 = fadd reassoc ninf nsz float %277, %.35076
  %279 = load float*, float** %25, align 8
  %280 = load i32, i32* %26, align 4
  %281 = mul i32 %lsr.iv122, %280
  %282 = add i32 %189, %281
  %283 = sext i32 %282 to i64
  %284 = getelementptr float, float* %279, i64 %283
  %285 = load float, float* %284, align 4
  %286 = fmul reassoc ninf nsz float %285, %277
  %287 = fadd reassoc ninf nsz float %286, %.377
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %288 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %174, float 0x3FE6666660000000)
  %289 = fdiv reassoc ninf nsz float %.044, %.047
  %290 = load float*, float** %25, align 8
  %291 = load i32, i32* %26, align 4
  %292 = mul i32 %291, %54
  %293 = add i32 %292, %68
  %294 = sext i32 %293 to i64
  %295 = getelementptr float, float* %290, i64 %294
  %296 = load float, float* %295, align 4
  %297 = fsub reassoc ninf nsz float %296, %289
  %298 = tail call float @llvm.fabs.f32(float %297)
  %299 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %300 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %299, i64 0, i32 14
  %301 = load i8*, i8** %300, align 8
  %302 = getelementptr inbounds i8, i8* %301, i64 24
  %303 = bitcast i8* %302 to float*
  %304 = load float, float* %303, align 4
  %305 = fsub reassoc ninf nsz float %298, %304
  %306 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %305, float 0.000000e+00)
  %307 = fcmp reassoc ninf nsz oge float %297, 0.000000e+00
  %308 = uitofp i1 %307 to float
  %309 = fcmp reassoc ninf nsz ole float %297, 0.000000e+00
  %310 = uitofp i1 %309 to float
  %311 = fsub reassoc ninf nsz float %308, %310
  %312 = fmul reassoc ninf nsz float %288, %23
  %313 = fmul reassoc ninf nsz float %312, %311
  %314 = fmul reassoc ninf nsz float %313, %306
  %315 = fadd reassoc ninf nsz float %314, %289
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %316 = load float*, float** %25, align 8
  %317 = load i32, i32* %26, align 4
  %318 = mul i32 %317, %54
  %319 = add i32 %318, %68
  %320 = sext i32 %319 to i64
  %321 = getelementptr float, float* %316, i64 %320
  %322 = load float, float* %321, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink = phi float [ %322, %false_block46 ], [ %315, %true_block45 ]
  %323 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %324 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %323, i64 0, i32 1, i32 1
  %325 = load float*, float** %324, align 8
  %326 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %323, i64 0, i32 1, i32 0, i32 1
  %327 = load i32, i32* %326, align 4
  %328 = mul i32 %327, %54
  %329 = add i32 %328, %68
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, float* %325, i64 %330
  store float %.sink, float* %331, align 4
  %332 = add nsw i32 %.05782, 1
  %lsr.iv.next117 = add i32 %lsr.iv116, 1
  %lsr.iv.next119 = add i32 %lsr.iv118, 1
  %lsr.iv.next121 = add i32 %lsr.iv120, 1
  %exitcond86.not = icmp eq i32 %332, %19
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
  %4 = alloca %struct.RuntimeContext, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext**
  %.sroa.0.0.copyload = load %struct.RuntimeContext*, %struct.RuntimeContext** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <16 x float> @llvm.masked.gather.v16f32.v16p0f32(<16 x float*>, i32 immarg, <16 x i1>, <16 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v16f32(float, <16 x float>) #10

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #10

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #9 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #10 = { nocallback nofree nosync nounwind readnone willreturn }

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
