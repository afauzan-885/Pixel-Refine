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
define void @_nlm_1ch_s7_p3_c412_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %1, i64 0, i32 4
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 20
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fmul reassoc ninf nsz float %4, 3.500000e+00
  %13 = fadd reassoc ninf nsz float %12, 0x3F60624DE0000000
  %14 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 16
  %18 = bitcast i8* %17 to float*
  store float %13, float* %18, align 4
  %19 = fmul reassoc ninf nsz float %3, 0x3FE6666660000000
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %20, i64 0, i32 6
  %22 = load float, float* %21, align 4
  %23 = fmul reassoc ninf nsz float %19, %22
  %24 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 24
  %28 = bitcast i8* %27 to float*
  store float %23, float* %28, align 4
  %29 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %29, i64 0, i32 2
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 8
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %39 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %38, i64 0, i32 3
  %40 = load i32, i32* %39, align 4
  %41 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %41, i64 0, i32 14
  %43 = load i8*, i8** %42, align 8
  %44 = getelementptr inbounds i8, i8* %43, i64 12
  %45 = bitcast i8* %44 to i32*
  store i32 %40, i32* %45, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %47 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  store i32 %46, i32* %51, align 4
  %52 = mul i32 %46, %37
  %53 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %53, i64 0, i32 14
  %55 = bitcast i8** %54 to i32**
  %56 = load i32*, i32** %55, align 8
  store i32 %52, i32* %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_nlm_1ch_s7_p3_c412_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 5
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %.05782 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %334, %after_if47 ]
  %27 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 4
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sdiv i32 %.05782, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.05782
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.05782, 0
  %38 = icmp ne i32 %34, %.05782
  %39 = and i1 %37, %36
  %40 = and i1 %39, %38
  %.neg63 = sext i1 %40 to i32
  %41 = add i32 %33, %.neg63
  %42 = mul i32 %41, %32
  %43 = getelementptr inbounds i8, i8* %29, i64 8
  %44 = bitcast i8* %43 to i32*
  %45 = load i32, i32* %44, align 4
  %46 = add i32 %45, -1
  %47 = getelementptr inbounds i8, i8* %29, i64 12
  %48 = bitcast i8* %47 to i32*
  %49 = load i32, i32* %48, align 4
  %50 = add i32 %49, -1
  %51 = load float*, float** %25, align 8
  %52 = load i32, i32* %26, align 4
  %53 = add i32 %41, -1
  %54 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %55 = tail call i32 @llvm.smin.i32(i32 %46, i32 %54)
  %56 = mul i32 %52, %55
  %57 = sub i32 %.05782, %42
  %58 = add i32 %57, -1
  %59 = insertelement <2 x i32> poison, i32 %58, i64 0
  %60 = insertelement <2 x i32> %59, i32 %57, i64 1
  %61 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %60, <2 x i32> zeroinitializer)
  %62 = insertelement <2 x i32> poison, i32 %50, i64 0
  %63 = shufflevector <2 x i32> %62, <2 x i32> poison, <2 x i32> zeroinitializer
  %64 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %63, <2 x i32> %61)
  %65 = insertelement <2 x i32> poison, i32 %56, i64 0
  %66 = shufflevector <2 x i32> %65, <2 x i32> poison, <2 x i32> zeroinitializer
  %67 = add <2 x i32> %66, %64
  %68 = sext <2 x i32> %67 to <2 x i64>
  %69 = extractelement <2 x i64> %68, i64 0
  %70 = getelementptr float, float* %51, i64 %69
  %71 = load float, float* %70, align 4
  %72 = fmul reassoc ninf nsz float %71, %71
  %73 = extractelement <2 x i64> %68, i64 1
  %74 = getelementptr float, float* %51, i64 %73
  %75 = load float, float* %74, align 4
  %76 = fadd reassoc ninf nsz float %75, %71
  %77 = fmul reassoc ninf nsz float %75, %75
  %78 = fadd reassoc ninf nsz float %77, %72
  %79 = add i32 %57, 1
  %80 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %81 = tail call i32 @llvm.smin.i32(i32 %50, i32 %80)
  %82 = add i32 %56, %81
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, float* %51, i64 %83
  %85 = load float, float* %84, align 4
  %86 = fadd reassoc ninf nsz float %85, %76
  %87 = fmul reassoc ninf nsz float %85, %85
  %88 = fadd reassoc ninf nsz float %87, %78
  %89 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %90 = tail call i32 @llvm.smin.i32(i32 %46, i32 %89)
  %91 = mul i32 %52, %90
  %92 = extractelement <2 x i32> %64, i64 0
  %93 = add i32 %91, %92
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, float* %51, i64 %94
  %96 = load float, float* %95, align 4
  %97 = fadd reassoc ninf nsz float %96, %86
  %98 = fmul reassoc ninf nsz float %96, %96
  %99 = fadd reassoc ninf nsz float %98, %88
  %100 = extractelement <2 x i32> %64, i64 1
  %101 = add i32 %91, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %51, i64 %102
  %104 = load float, float* %103, align 4
  %105 = fadd reassoc ninf nsz float %104, %97
  %106 = fmul reassoc ninf nsz float %104, %104
  %107 = fadd reassoc ninf nsz float %106, %99
  %108 = add i32 %91, %81
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %51, i64 %109
  %111 = load float, float* %110, align 4
  %112 = fadd reassoc ninf nsz float %111, %105
  %113 = fmul reassoc ninf nsz float %111, %111
  %114 = fadd reassoc ninf nsz float %113, %107
  %115 = add i32 %41, 1
  %116 = tail call i32 @llvm.smax.i32(i32 %115, i32 0)
  %117 = tail call i32 @llvm.smin.i32(i32 %46, i32 %116)
  %118 = mul i32 %52, %117
  %119 = add i32 %118, %92
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %51, i64 %120
  %122 = load float, float* %121, align 4
  %123 = fadd reassoc ninf nsz float %122, %112
  %124 = fmul reassoc ninf nsz float %122, %122
  %125 = fadd reassoc ninf nsz float %124, %114
  %126 = add i32 %118, %100
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, float* %51, i64 %127
  %129 = load float, float* %128, align 4
  %130 = fadd reassoc ninf nsz float %129, %123
  %131 = fmul reassoc ninf nsz float %129, %129
  %132 = fadd reassoc ninf nsz float %131, %125
  %133 = add i32 %118, %81
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %51, i64 %134
  %136 = load float, float* %135, align 4
  %137 = fadd reassoc ninf nsz float %136, %130
  %138 = fmul reassoc ninf nsz float %136, %136
  %139 = fadd reassoc ninf nsz float %138, %132
  %140 = fmul reassoc ninf nsz float %137, 0x3FBC71C720000000
  %141 = fmul reassoc ninf nsz float %139, 0x3FBC71C720000000
  %142 = fmul reassoc ninf nsz float %140, %140
  %143 = fsub reassoc ninf nsz float %141, %142
  %144 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %143, float 0.000000e+00)
  %145 = fmul reassoc ninf nsz float %144, -3.500000e+02
  %146 = tail call float @expf(float noundef %145) #1
  %147 = add i32 %57, -3
  %148 = tail call i32 @llvm.smax.i32(i32 %147, i32 0)
  %149 = tail call i32 @llvm.smin.i32(i32 %50, i32 %148)
  %150 = add i32 %57, -2
  %151 = tail call i32 @llvm.smax.i32(i32 %150, i32 0)
  %152 = tail call i32 @llvm.smin.i32(i32 %50, i32 %151)
  %153 = add i32 %57, 2
  %154 = tail call i32 @llvm.smax.i32(i32 %153, i32 0)
  %155 = tail call i32 @llvm.smin.i32(i32 %50, i32 %154)
  %156 = add i32 %57, 3
  %157 = tail call i32 @llvm.smax.i32(i32 %156, i32 0)
  %158 = tail call i32 @llvm.smin.i32(i32 %50, i32 %157)
  %broadcast.splatinsert98 = insertelement <8 x i32> poison, i32 %41, i64 0
  %broadcast.splat99 = shufflevector <8 x i32> %broadcast.splatinsert98, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert100 = insertelement <8 x i32> poison, i32 %46, i64 0
  %broadcast.splat101 = shufflevector <8 x i32> %broadcast.splatinsert100, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert106 = insertelement <8 x i32> poison, i32 %149, i64 0
  %broadcast.splat107 = shufflevector <8 x i32> %broadcast.splatinsert106, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert111 = insertelement <8 x i32> poison, i32 %152, i64 0
  %broadcast.splat112 = shufflevector <8 x i32> %broadcast.splatinsert111, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splat118 = shufflevector <2 x i32> %64, <2 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splat124 = shufflevector <2 x i32> %64, <2 x i32> poison, <8 x i32> <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %broadcast.splatinsert129 = insertelement <8 x i32> poison, i32 %81, i64 0
  %broadcast.splat130 = shufflevector <8 x i32> %broadcast.splatinsert129, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert135 = insertelement <8 x i32> poison, i32 %155, i64 0
  %broadcast.splat136 = shufflevector <8 x i32> %broadcast.splatinsert135, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert141 = insertelement <8 x i32> poison, i32 %158, i64 0
  %broadcast.splat142 = shufflevector <8 x i32> %broadcast.splatinsert141, <8 x i32> poison, <8 x i32> zeroinitializer
  %159 = add <8 x i32> %broadcast.splat99, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %160 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %159, <8 x i32> zeroinitializer)
  %161 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat101, <8 x i32> %160)
  %162 = add i32 %57, -6
  %163 = add i32 %33, -7
  %164 = add i32 %163, %.neg63
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv147 = phi i32 [ %164, %for_loop_body ], [ %lsr.iv.next148, %for_loop_inc10 ]
  %.04381 = phi i32 [ -7, %for_loop_body ], [ %167, %for_loop_inc10 ]
  %.14580 = phi float [ 0.000000e+00, %for_loop_body ], [ %.044, %for_loop_inc10 ]
  %.14879 = phi float [ 0.000000e+00, %for_loop_body ], [ %.047, %for_loop_inc10 ]
  %165 = add i32 %.04381, %41
  %166 = icmp slt i32 %165, 0
  br i1 %166, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.047 = phi float [ %.14879, %false_block ], [ %.14879, %for_loop_body9 ], [ %.249, %for_loop_inc10.loopexit ]
  %.044 = phi float [ %.14580, %false_block ], [ %.14580, %for_loop_body9 ], [ %.246, %for_loop_inc10.loopexit ]
  %167 = add nsw i32 %.04381, 1
  %lsr.iv.next148 = add i32 %lsr.iv147, 1
  %exitcond86.not = icmp eq i32 %167, 8
  br i1 %exitcond86.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %168 = fsub reassoc ninf nsz float 1.000000e+00, %146
  %169 = fcmp reassoc ninf nsz ogt float %.047, 0x3D71979980000000
  br i1 %169, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %170 = load i32, i32* %44, align 4
  %.not64 = icmp slt i32 %165, %170
  br i1 %.not64, label %after_if15, label %for_loop_inc10

after_if15:                                       ; preds = %false_block
  %.not = icmp ne i32 %.04381, 0
  %broadcast.splatinsert102 = insertelement <8 x i32> poison, i32 %165, i64 0
  %broadcast.splat103 = shufflevector <8 x i32> %broadcast.splatinsert102, <8 x i32> poison, <8 x i32> zeroinitializer
  %171 = add <8 x i32> %broadcast.splat103, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %172 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %171, <8 x i32> zeroinitializer)
  %173 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat101, <8 x i32> %172)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %after_if15
  %lsr.iv = phi i32 [ 0, %after_if15 ], [ %lsr.iv.next, %for_loop_inc17 ]
  %.377 = phi float [ %.14580, %after_if15 ], [ %.246, %for_loop_inc17 ]
  %.35076 = phi float [ %.14879, %after_if15 ], [ %.249, %for_loop_inc17 ]
  %174 = add i32 %162, %lsr.iv
  %175 = add i32 %174, -1
  %176 = icmp slt i32 %175, 0
  br i1 %176, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.249 = phi float [ %.35076, %false_block21 ], [ %279, %true_block41 ], [ %.35076, %after_if32 ], [ %.35076, %for_loop_body16 ]
  %.246 = phi float [ %.377, %false_block21 ], [ %289, %true_block41 ], [ %.377, %after_if32 ], [ %.377, %for_loop_body16 ]
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 1
  %exitcond85.not = icmp eq i32 %lsr.iv.next, 15
  br i1 %exitcond85.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %177 = load i32, i32* %48, align 4
  %.not65 = icmp slt i32 %175, %177
  br i1 %.not65, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %178 = icmp ne i32 %lsr.iv, 7
  %spec.select = select i1 %.not, i1 true, i1 %178
  br i1 %spec.select, label %for_loop_test36.preheader, label %after_if32

for_loop_test36.preheader:                        ; preds = %after_if25
  %179 = load float*, float** %25, align 8
  %180 = add i32 %174, 2
  %181 = tail call i32 @llvm.smax.i32(i32 %180, i32 0)
  %182 = tail call i32 @llvm.smin.i32(i32 %50, i32 %181)
  %183 = add i32 %174, 1
  %184 = tail call i32 @llvm.smax.i32(i32 %183, i32 0)
  %185 = tail call i32 @llvm.smin.i32(i32 %50, i32 %184)
  %186 = tail call i32 @llvm.smax.i32(i32 %174, i32 0)
  %187 = tail call i32 @llvm.smin.i32(i32 %50, i32 %186)
  %188 = tail call i32 @llvm.smax.i32(i32 %175, i32 0)
  %189 = tail call i32 @llvm.smin.i32(i32 %50, i32 %188)
  %190 = add i32 %174, -2
  %191 = tail call i32 @llvm.smax.i32(i32 %190, i32 0)
  %192 = tail call i32 @llvm.smin.i32(i32 %50, i32 %191)
  %193 = add i32 %174, -3
  %194 = tail call i32 @llvm.smax.i32(i32 %193, i32 0)
  %195 = tail call i32 @llvm.smin.i32(i32 %50, i32 %194)
  %196 = call i32 @llvm.smax.i32(i32 %175, i32 3)
  %197 = add nsw i32 %196, -3
  %198 = tail call i32 @llvm.smin.i32(i32 %50, i32 %197)
  %199 = load i32, i32* %26, align 4
  %broadcast.splatinsert104 = insertelement <8 x i32> poison, i32 %199, i64 0
  %broadcast.splat105 = shufflevector <8 x i32> %broadcast.splatinsert104, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert108 = insertelement <8 x i32> poison, i32 %198, i64 0
  %broadcast.splat109 = shufflevector <8 x i32> %broadcast.splatinsert108, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert114 = insertelement <8 x i32> poison, i32 %195, i64 0
  %broadcast.splat115 = shufflevector <8 x i32> %broadcast.splatinsert114, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert120 = insertelement <8 x i32> poison, i32 %192, i64 0
  %broadcast.splat121 = shufflevector <8 x i32> %broadcast.splatinsert120, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert126 = insertelement <8 x i32> poison, i32 %189, i64 0
  %broadcast.splat127 = shufflevector <8 x i32> %broadcast.splatinsert126, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert132 = insertelement <8 x i32> poison, i32 %187, i64 0
  %broadcast.splat133 = shufflevector <8 x i32> %broadcast.splatinsert132, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert138 = insertelement <8 x i32> poison, i32 %185, i64 0
  %broadcast.splat139 = shufflevector <8 x i32> %broadcast.splatinsert138, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert144 = insertelement <8 x i32> poison, i32 %182, i64 0
  %broadcast.splat145 = shufflevector <8 x i32> %broadcast.splatinsert144, <8 x i32> poison, <8 x i32> zeroinitializer
  %200 = mul <8 x i32> %broadcast.splat105, %161
  %201 = mul <8 x i32> %broadcast.splat105, %173
  %202 = add <8 x i32> %200, %broadcast.splat107
  %203 = sext <8 x i32> %202 to <8 x i64>
  %204 = getelementptr float, float* %179, <8 x i64> %203
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %204, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %205 = add <8 x i32> %201, %broadcast.splat109
  %206 = sext <8 x i32> %205 to <8 x i64>
  %207 = getelementptr float, float* %179, <8 x i64> %206
  %wide.masked.gather110 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %207, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %208 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather110
  %209 = fmul reassoc ninf nsz <8 x float> %208, %208
  %210 = add <8 x i32> %200, %broadcast.splat112
  %211 = sext <8 x i32> %210 to <8 x i64>
  %212 = getelementptr float, float* %179, <8 x i64> %211
  %wide.masked.gather113 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %212, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %213 = add <8 x i32> %201, %broadcast.splat115
  %214 = sext <8 x i32> %213 to <8 x i64>
  %215 = getelementptr float, float* %179, <8 x i64> %214
  %wide.masked.gather116 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %215, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %216 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather113, %wide.masked.gather116
  %217 = fmul reassoc ninf nsz <8 x float> %216, %216
  %218 = fadd reassoc ninf nsz <8 x float> %217, %209
  %219 = add <8 x i32> %200, %broadcast.splat118
  %220 = sext <8 x i32> %219 to <8 x i64>
  %221 = getelementptr float, float* %179, <8 x i64> %220
  %wide.masked.gather119 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %221, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %222 = add <8 x i32> %201, %broadcast.splat121
  %223 = sext <8 x i32> %222 to <8 x i64>
  %224 = getelementptr float, float* %179, <8 x i64> %223
  %wide.masked.gather122 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %224, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %225 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather119, %wide.masked.gather122
  %226 = fmul reassoc ninf nsz <8 x float> %225, %225
  %227 = fadd reassoc ninf nsz <8 x float> %226, %218
  %228 = add <8 x i32> %200, %broadcast.splat124
  %229 = sext <8 x i32> %228 to <8 x i64>
  %230 = getelementptr float, float* %179, <8 x i64> %229
  %wide.masked.gather125 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %230, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %231 = add <8 x i32> %201, %broadcast.splat127
  %232 = sext <8 x i32> %231 to <8 x i64>
  %233 = getelementptr float, float* %179, <8 x i64> %232
  %wide.masked.gather128 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %233, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %234 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather125, %wide.masked.gather128
  %235 = fmul reassoc ninf nsz <8 x float> %234, %234
  %236 = fadd reassoc ninf nsz <8 x float> %235, %227
  %237 = add <8 x i32> %200, %broadcast.splat130
  %238 = sext <8 x i32> %237 to <8 x i64>
  %239 = getelementptr float, float* %179, <8 x i64> %238
  %wide.masked.gather131 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %239, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %240 = add <8 x i32> %201, %broadcast.splat133
  %241 = sext <8 x i32> %240 to <8 x i64>
  %242 = getelementptr float, float* %179, <8 x i64> %241
  %wide.masked.gather134 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %242, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %243 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather131, %wide.masked.gather134
  %244 = fmul reassoc ninf nsz <8 x float> %243, %243
  %245 = fadd reassoc ninf nsz <8 x float> %244, %236
  %246 = add <8 x i32> %200, %broadcast.splat136
  %247 = sext <8 x i32> %246 to <8 x i64>
  %248 = getelementptr float, float* %179, <8 x i64> %247
  %wide.masked.gather137 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %248, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %249 = add <8 x i32> %201, %broadcast.splat139
  %250 = sext <8 x i32> %249 to <8 x i64>
  %251 = getelementptr float, float* %179, <8 x i64> %250
  %wide.masked.gather140 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %251, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %252 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather137, %wide.masked.gather140
  %253 = fmul reassoc ninf nsz <8 x float> %252, %252
  %254 = fadd reassoc ninf nsz <8 x float> %253, %245
  %255 = add <8 x i32> %200, %broadcast.splat142
  %256 = sext <8 x i32> %255 to <8 x i64>
  %257 = getelementptr float, float* %179, <8 x i64> %256
  %wide.masked.gather143 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %257, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %258 = add <8 x i32> %201, %broadcast.splat145
  %259 = sext <8 x i32> %258 to <8 x i64>
  %260 = getelementptr float, float* %179, <8 x i64> %259
  %wide.masked.gather146 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %260, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %261 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather143, %wide.masked.gather146
  %262 = fmul reassoc ninf nsz <8 x float> %261, %261
  %263 = fadd reassoc ninf nsz <8 x float> %262, %254
  %264 = insertelement <8 x float> %263, float 0.000000e+00, i64 7
  %265 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %264)
  %266 = fmul reassoc ninf nsz float %265, 0x3F94E5E0A0000000
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.039 = phi float [ %266, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %267 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %268 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %267, i64 0, i32 14
  %269 = load i8*, i8** %268, align 8
  %270 = getelementptr inbounds i8, i8* %269, i64 16
  %271 = bitcast i8* %270 to float*
  %272 = load float, float* %271, align 4
  %273 = fcmp reassoc ninf nsz ugt float %.039, %272
  br i1 %273, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.039
  %274 = getelementptr inbounds i8, i8* %269, i64 20
  %275 = bitcast i8* %274 to float*
  %276 = load float, float* %275, align 4
  %277 = fmul reassoc ninf nsz float %276, %neg44
  %278 = tail call float @expf(float noundef %277) #1
  %279 = fadd reassoc ninf nsz float %278, %.35076
  %280 = load float*, float** %25, align 8
  %281 = load i32, i32* %26, align 4
  %282 = mul i32 %lsr.iv147, %281
  %283 = add i32 %174, %282
  %284 = add i32 %283, -1
  %285 = sext i32 %284 to i64
  %286 = getelementptr float, float* %280, i64 %285
  %287 = load float, float* %286, align 4
  %288 = fmul reassoc ninf nsz float %287, %278
  %289 = fadd reassoc ninf nsz float %288, %.377
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %290 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %168, float 0x3FE6666660000000)
  %291 = fdiv reassoc ninf nsz float %.044, %.047
  %292 = load float*, float** %25, align 8
  %293 = load i32, i32* %26, align 4
  %294 = mul i32 %293, %41
  %295 = add i32 %294, %57
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, float* %292, i64 %296
  %298 = load float, float* %297, align 4
  %299 = fsub reassoc ninf nsz float %298, %291
  %300 = tail call float @llvm.fabs.f32(float %299)
  %301 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %302 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %301, i64 0, i32 14
  %303 = load i8*, i8** %302, align 8
  %304 = getelementptr inbounds i8, i8* %303, i64 24
  %305 = bitcast i8* %304 to float*
  %306 = load float, float* %305, align 4
  %307 = fsub reassoc ninf nsz float %300, %306
  %308 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %307, float 0.000000e+00)
  %309 = fcmp reassoc ninf nsz oge float %299, 0.000000e+00
  %310 = uitofp i1 %309 to float
  %311 = fcmp reassoc ninf nsz ole float %299, 0.000000e+00
  %312 = uitofp i1 %311 to float
  %313 = fsub reassoc ninf nsz float %310, %312
  %314 = fmul reassoc ninf nsz float %290, %23
  %315 = fmul reassoc ninf nsz float %314, %313
  %316 = fmul reassoc ninf nsz float %315, %308
  %317 = fadd reassoc ninf nsz float %316, %291
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %318 = load float*, float** %25, align 8
  %319 = load i32, i32* %26, align 4
  %320 = mul i32 %319, %41
  %321 = add i32 %320, %57
  %322 = sext i32 %321 to i64
  %323 = getelementptr float, float* %318, i64 %322
  %324 = load float, float* %323, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink = phi float [ %324, %false_block46 ], [ %317, %true_block45 ]
  %325 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %326 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %325, i64 0, i32 1, i32 1
  %327 = load float*, float** %326, align 8
  %328 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float, float }* %325, i64 0, i32 1, i32 0, i32 1
  %329 = load i32, i32* %328, align 4
  %330 = mul i32 %329, %41
  %331 = add i32 %330, %57
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, float* %327, i64 %332
  store float %.sink, float* %333, align 4
  %334 = add nsw i32 %.05782, 1
  %exitcond87.not = icmp eq i32 %334, %19
  br i1 %exitcond87.not, label %after_for.loopexit, label %for_loop_body
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
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #10

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #8

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
