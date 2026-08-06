; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.36*, void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.36 = type { i8*, %struct.LLVMRuntime.35*, i32, i64* }
%struct.LLVMRuntime.35 = type { %struct.PreallocatedMemoryChunk.31, %struct.PreallocatedMemoryChunk.31, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.32*], [1024 x %struct.NodeManager.33*], [1024 x i8*], i8*, %struct.RandState.34*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.31 = type { i8*, i8*, i64 }
%struct.ListManager.32 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.35* }
%struct.NodeManager.33 = type { %struct.LLVMRuntime.35*, i32, i32, i32, i32, %struct.ListManager.32*, %struct.ListManager.32*, %struct.ListManager.32*, i32 }
%struct.RandState.34 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_nlm_3ch_s3_p1_c416_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %1, i64 0, i32 5
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 20
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fmul reassoc ninf nsz float %4, 3.500000e+00
  %13 = fadd reassoc ninf nsz float %12, 0x3F60624DE0000000
  %14 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 16
  %18 = bitcast i8* %17 to float*
  store float %13, float* %18, align 4
  %19 = fmul reassoc ninf nsz float %3, 0x3FE6666660000000
  %20 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %21 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %20, i64 0, i32 7
  %22 = load float, float* %21, align 4
  %23 = fmul reassoc ninf nsz float %19, %22
  %24 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 24
  %28 = bitcast i8* %27 to float*
  store float %23, float* %28, align 4
  %29 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %29, i64 0, i32 3
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 8
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %39 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %38, i64 0, i32 4
  %40 = load i32, i32* %39, align 4
  %41 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %41, i64 0, i32 14
  %43 = load i8*, i8** %42, align 8
  %44 = getelementptr inbounds i8, i8* %43, i64 12
  %45 = bitcast i8* %44 to i32*
  store i32 %40, i32* %45, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %47 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  store i32 %46, i32* %51, align 4
  %52 = mul i32 %46, %37
  %53 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %6, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %53, i64 0, i32 14
  %55 = bitcast i8** %54 to i32**
  %56 = load i32*, i32** %55, align 8
  store i32 %52, i32* %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_nlm_3ch_s3_p1_c416_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.36* %context, %struct.RuntimeContext.36** %4, align 8
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.36*, i8*, i32)* @function_body, void (%struct.RuntimeContext.36*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.36* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 6
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 1, i32 0, i32 2
  %31 = add i32 %17, -3
  %32 = add i32 %17, -2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv124 = phi i32 [ %32, %for_loop_body.lr.ph ], [ %lsr.iv.next125, %after_if47 ]
  %lsr.iv122 = phi i32 [ %31, %for_loop_body.lr.ph ], [ %lsr.iv.next123, %after_if47 ]
  %.06998 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %554, %after_if47 ]
  %33 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %34 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %33, i64 0, i32 14
  %35 = load i8*, i8** %34, align 8
  %36 = getelementptr inbounds i8, i8* %35, i64 4
  %37 = bitcast i8* %36 to i32*
  %38 = load i32, i32* %37, align 4
  %39 = sdiv i32 %.06998, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.06998
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.06998, 0
  %44 = icmp ne i32 %40, %.06998
  %45 = and i1 %43, %42
  %46 = and i1 %45, %44
  %.neg75 = sext i1 %46 to i32
  %47 = getelementptr inbounds i8, i8* %35, i64 8
  %48 = bitcast i8* %47 to i32*
  %49 = load i32, i32* %48, align 4
  %50 = add i32 %49, -1
  %51 = getelementptr inbounds i8, i8* %35, i64 12
  %52 = bitcast i8* %51 to i32*
  %53 = load i32, i32* %52, align 4
  %54 = add i32 %53, -1
  %55 = load float*, float** %25, align 8
  %56 = load i32, i32* %26, align 4
  %57 = load i32, i32* %27, align 4
  %58 = insertelement <2 x i32> poison, i32 %54, i64 0
  %59 = shufflevector <2 x i32> %58, <2 x i32> poison, <2 x i32> zeroinitializer
  %60 = add i32 %39, %.neg75
  %61 = mul i32 %60, %38
  %62 = sub i32 %.06998, %61
  %63 = add i32 %62, -1
  %64 = tail call i32 @llvm.smax.i32(i32 %63, i32 0)
  %65 = tail call i32 @llvm.smin.i32(i32 %54, i32 %64)
  %66 = add i32 %60, -1
  %67 = insertelement <2 x i32> poison, i32 %66, i64 0
  %68 = insertelement <2 x i32> %67, i32 %60, i64 1
  %69 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %68, <2 x i32> zeroinitializer)
  %70 = insertelement <2 x i32> poison, i32 %50, i64 0
  %71 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %72 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %71, <2 x i32> %69)
  %73 = extractelement <2 x i32> %72, i64 0
  %74 = mul i32 %56, %73
  %75 = add i32 %74, %65
  %76 = mul i32 %75, %57
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, float* %55, i64 %77
  %79 = load float, float* %78, align 4
  %80 = add i32 %76, 1
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %55, i64 %81
  %83 = load float, float* %82, align 4
  %84 = fadd reassoc ninf nsz float %83, %79
  %85 = add i32 %76, 2
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, float* %55, i64 %86
  %88 = load float, float* %87, align 4
  %89 = fadd reassoc ninf nsz float %84, %88
  %90 = fmul reassoc ninf nsz float %89, 0x3FD5555560000000
  %91 = fmul reassoc ninf nsz float %90, %90
  %92 = add i32 %62, 1
  %93 = insertelement <2 x i32> poison, i32 %62, i64 0
  %94 = insertelement <2 x i32> %93, i32 %92, i64 1
  %95 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %94, <2 x i32> zeroinitializer)
  %96 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %59, <2 x i32> %95)
  %97 = extractelement <2 x i32> %96, i64 0
  %98 = add i32 %74, %97
  %99 = mul i32 %98, %57
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %55, i64 %100
  %102 = load float, float* %101, align 4
  %103 = add i32 %99, 1
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, float* %55, i64 %104
  %106 = load float, float* %105, align 4
  %107 = fadd reassoc ninf nsz float %106, %102
  %108 = add i32 %99, 2
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %55, i64 %109
  %111 = load float, float* %110, align 4
  %112 = fadd reassoc ninf nsz float %107, %111
  %113 = fmul reassoc ninf nsz float %112, 0x3FD5555560000000
  %114 = fadd reassoc ninf nsz float %113, %90
  %115 = fmul reassoc ninf nsz float %113, %113
  %116 = fadd reassoc ninf nsz float %115, %91
  %117 = extractelement <2 x i32> %96, i64 1
  %118 = add i32 %74, %117
  %119 = mul i32 %118, %57
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %55, i64 %120
  %122 = load float, float* %121, align 4
  %123 = add i32 %119, 1
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %55, i64 %124
  %126 = load float, float* %125, align 4
  %127 = fadd reassoc ninf nsz float %126, %122
  %128 = add i32 %119, 2
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %55, i64 %129
  %131 = load float, float* %130, align 4
  %132 = fadd reassoc ninf nsz float %127, %131
  %133 = fmul reassoc ninf nsz float %132, 0x3FD5555560000000
  %134 = fadd reassoc ninf nsz float %133, %114
  %135 = fmul reassoc ninf nsz float %133, %133
  %136 = fadd reassoc ninf nsz float %135, %116
  %137 = extractelement <2 x i32> %72, i64 1
  %138 = mul i32 %56, %137
  %139 = add i32 %138, %65
  %140 = mul i32 %139, %57
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %55, i64 %141
  %143 = load float, float* %142, align 4
  %144 = add i32 %140, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %55, i64 %145
  %147 = load float, float* %146, align 4
  %148 = fadd reassoc ninf nsz float %147, %143
  %149 = add i32 %140, 2
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, float* %55, i64 %150
  %152 = load float, float* %151, align 4
  %153 = fadd reassoc ninf nsz float %148, %152
  %154 = fmul reassoc ninf nsz float %153, 0x3FD5555560000000
  %155 = fadd reassoc ninf nsz float %154, %134
  %156 = fmul reassoc ninf nsz float %154, %154
  %157 = fadd reassoc ninf nsz float %156, %136
  %158 = add i32 %138, %97
  %159 = mul i32 %158, %57
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, float* %55, i64 %160
  %162 = load float, float* %161, align 4
  %163 = add i32 %159, 1
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %55, i64 %164
  %166 = load float, float* %165, align 4
  %167 = fadd reassoc ninf nsz float %166, %162
  %168 = add i32 %159, 2
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, float* %55, i64 %169
  %171 = load float, float* %170, align 4
  %172 = fadd reassoc ninf nsz float %167, %171
  %173 = fmul reassoc ninf nsz float %172, 0x3FD5555560000000
  %174 = fadd reassoc ninf nsz float %173, %155
  %175 = fmul reassoc ninf nsz float %173, %173
  %176 = fadd reassoc ninf nsz float %175, %157
  %177 = add i32 %138, %117
  %178 = mul i32 %177, %57
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, float* %55, i64 %179
  %181 = load float, float* %180, align 4
  %182 = add i32 %178, 1
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, float* %55, i64 %183
  %185 = load float, float* %184, align 4
  %186 = fadd reassoc ninf nsz float %185, %181
  %187 = add i32 %178, 2
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, float* %55, i64 %188
  %190 = load float, float* %189, align 4
  %191 = fadd reassoc ninf nsz float %186, %190
  %192 = fmul reassoc ninf nsz float %191, 0x3FD5555560000000
  %193 = fadd reassoc ninf nsz float %192, %174
  %194 = fmul reassoc ninf nsz float %192, %192
  %195 = fadd reassoc ninf nsz float %194, %176
  %196 = add i32 %60, 1
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = tail call i32 @llvm.smin.i32(i32 %50, i32 %197)
  %199 = mul i32 %56, %198
  %200 = add i32 %199, %65
  %201 = mul i32 %200, %57
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %55, i64 %202
  %204 = load float, float* %203, align 4
  %205 = add i32 %201, 1
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, float* %55, i64 %206
  %208 = load float, float* %207, align 4
  %209 = fadd reassoc ninf nsz float %208, %204
  %210 = add i32 %201, 2
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %55, i64 %211
  %213 = load float, float* %212, align 4
  %214 = fadd reassoc ninf nsz float %209, %213
  %215 = fmul reassoc ninf nsz float %214, 0x3FD5555560000000
  %216 = fadd reassoc ninf nsz float %215, %193
  %217 = fmul reassoc ninf nsz float %215, %215
  %218 = fadd reassoc ninf nsz float %217, %195
  %219 = add i32 %199, %97
  %220 = mul i32 %219, %57
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %55, i64 %221
  %223 = load float, float* %222, align 4
  %224 = add i32 %220, 1
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, float* %55, i64 %225
  %227 = load float, float* %226, align 4
  %228 = fadd reassoc ninf nsz float %227, %223
  %229 = add i32 %220, 2
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, float* %55, i64 %230
  %232 = load float, float* %231, align 4
  %233 = fadd reassoc ninf nsz float %228, %232
  %234 = fmul reassoc ninf nsz float %233, 0x3FD5555560000000
  %235 = fadd reassoc ninf nsz float %234, %216
  %236 = fmul reassoc ninf nsz float %234, %234
  %237 = fadd reassoc ninf nsz float %236, %218
  %238 = add i32 %199, %117
  %239 = mul i32 %238, %57
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %55, i64 %240
  %242 = load float, float* %241, align 4
  %243 = add i32 %239, 1
  %244 = sext i32 %243 to i64
  %245 = getelementptr float, float* %55, i64 %244
  %246 = load float, float* %245, align 4
  %247 = fadd reassoc ninf nsz float %246, %242
  %248 = add i32 %239, 2
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, float* %55, i64 %249
  %251 = load float, float* %250, align 4
  %252 = fadd reassoc ninf nsz float %247, %251
  %253 = fmul reassoc ninf nsz float %252, 0x3FD5555560000000
  %254 = fadd reassoc ninf nsz float %253, %235
  %255 = fmul reassoc ninf nsz float %253, %253
  %256 = fadd reassoc ninf nsz float %255, %237
  %257 = fmul reassoc ninf nsz float %254, 0x3FBC71C720000000
  %258 = fmul reassoc ninf nsz float %256, 0x3FBC71C720000000
  %259 = fmul reassoc ninf nsz float %257, %257
  %260 = fsub reassoc ninf nsz float %258, %259
  %261 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %260, float 0.000000e+00)
  %262 = fmul reassoc ninf nsz float %261, -3.500000e+02
  %263 = tail call float @expf(float noundef %262) #1
  %264 = fsub reassoc ninf nsz float 1.000000e+00, %263
  %265 = load float*, float** %28, align 8
  %266 = load i32, i32* %29, align 4
  %267 = load i32, i32* %30, align 4
  %268 = mul i32 %266, %60
  %269 = add i32 %268, %62
  %270 = mul i32 %269, %267
  %271 = add i32 %270, 1
  %272 = sext i32 %271 to i64
  %273 = getelementptr float, float* %265, i64 %272
  %274 = load float, float* %273, align 4
  %275 = add i32 %270, 2
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, float* %265, i64 %276
  %278 = load float, float* %277, align 4
  %279 = insertelement <8 x i32> poison, i32 %65, i64 0
  %280 = shufflevector <2 x i32> %96, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %281 = shufflevector <8 x i32> %279, <8 x i32> %280, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle116 = shufflevector <8 x i32> %281, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 1, i32 2, i32 0, i32 1>
  %282 = sub i32 %lsr.iv122, %61
  %283 = sub i32 %lsr.iv124, %61
  %284 = add i32 %39, -3
  %285 = add i32 %284, %.neg75
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv126 = phi i32 [ %285, %for_loop_body ], [ %lsr.iv.next127, %for_loop_inc10 ]
  %.04797 = phi i32 [ -3, %for_loop_body ], [ %288, %for_loop_inc10 ]
  %.14996 = phi float [ 0.000000e+00, %for_loop_body ], [ %.048, %for_loop_inc10 ]
  %.15295 = phi float [ 0.000000e+00, %for_loop_body ], [ %.051, %for_loop_inc10 ]
  %.15694 = phi float [ 0.000000e+00, %for_loop_body ], [ %.055, %for_loop_inc10 ]
  %.16093 = phi float [ 0.000000e+00, %for_loop_body ], [ %.059, %for_loop_inc10 ]
  %286 = add i32 %.04797, %60
  %287 = icmp slt i32 %286, 0
  br i1 %287, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.059 = phi float [ %.16093, %false_block ], [ %.16093, %for_loop_body9 ], [ %.261, %for_loop_inc10.loopexit ]
  %.055 = phi float [ %.15694, %false_block ], [ %.15694, %for_loop_body9 ], [ %.257, %for_loop_inc10.loopexit ]
  %.051 = phi float [ %.15295, %false_block ], [ %.15295, %for_loop_body9 ], [ %.253, %for_loop_inc10.loopexit ]
  %.048 = phi float [ %.14996, %false_block ], [ %.14996, %for_loop_body9 ], [ %.250, %for_loop_inc10.loopexit ]
  %288 = add nsw i32 %.04797, 1
  %lsr.iv.next127 = add i32 %lsr.iv126, 1
  %exitcond101.not = icmp eq i32 %288, 4
  br i1 %exitcond101.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %289 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %264, float 0x3FE6666660000000)
  %290 = fcmp reassoc ninf nsz ogt float %.059, 0x3D71979980000000
  br i1 %290, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %291 = load i32, i32* %48, align 4
  %.not76 = icmp slt i32 %286, %291
  br i1 %.not76, label %after_if15, label %for_loop_inc10

after_if15:                                       ; preds = %false_block
  %.not = icmp ne i32 %.04797, 0
  %292 = add i32 %286, -1
  %293 = tail call i32 @llvm.smax.i32(i32 %292, i32 0)
  %294 = tail call i32 @llvm.smin.i32(i32 %50, i32 %293)
  %295 = add i32 %286, 1
  %296 = insertelement <2 x i32> poison, i32 %286, i64 0
  %297 = insertelement <2 x i32> %296, i32 %295, i64 1
  %298 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %297, <2 x i32> zeroinitializer)
  %299 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %71, <2 x i32> %298)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %after_if15
  %lsr.iv = phi i32 [ 0, %after_if15 ], [ %lsr.iv.next, %for_loop_inc17 ]
  %.391 = phi float [ %.14996, %after_if15 ], [ %.250, %for_loop_inc17 ]
  %.35490 = phi float [ %.15295, %after_if15 ], [ %.253, %for_loop_inc17 ]
  %.35889 = phi float [ %.15694, %after_if15 ], [ %.257, %for_loop_inc17 ]
  %.36288 = phi float [ %.16093, %after_if15 ], [ %.261, %for_loop_inc17 ]
  %300 = add i32 %282, %lsr.iv
  %301 = icmp slt i32 %300, 0
  br i1 %301, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.261 = phi float [ %.36288, %false_block21 ], [ %386, %true_block41 ], [ %.36288, %after_if32 ], [ %.36288, %for_loop_body16 ]
  %.257 = phi float [ %.35889, %false_block21 ], [ %397, %true_block41 ], [ %.35889, %after_if32 ], [ %.35889, %for_loop_body16 ]
  %.253 = phi float [ %.35490, %false_block21 ], [ %403, %true_block41 ], [ %.35490, %after_if32 ], [ %.35490, %for_loop_body16 ]
  %.250 = phi float [ %.391, %false_block21 ], [ %409, %true_block41 ], [ %.391, %after_if32 ], [ %.391, %for_loop_body16 ]
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 7
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %302 = load i32, i32* %52, align 4
  %.not77 = icmp slt i32 %300, %302
  br i1 %.not77, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %303 = icmp ne i32 %lsr.iv, 3
  %spec.select = select i1 %.not, i1 true, i1 %303
  br i1 %spec.select, label %for_loop_test36.preheader, label %after_if32

for_loop_test36.preheader:                        ; preds = %after_if25
  %304 = load float*, float** %28, align 8
  %305 = load i32, i32* %29, align 4
  %306 = load i32, i32* %30, align 4
  %307 = call i32 @llvm.smax.i32(i32 %300, i32 1)
  %308 = add nsw i32 %307, -1
  %309 = mul i32 %305, %294
  %310 = insertelement <2 x i32> poison, i32 %308, i64 0
  %311 = insertelement <2 x i32> %310, i32 %300, i64 1
  %312 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %59, <2 x i32> %311)
  %313 = add i32 %283, %lsr.iv
  %314 = tail call i32 @llvm.smin.i32(i32 %54, i32 %313)
  %315 = insertelement <2 x i32> poison, i32 %305, i64 0
  %316 = shufflevector <2 x i32> %315, <2 x i32> poison, <2 x i32> zeroinitializer
  %317 = mul <2 x i32> %316, %72
  %318 = mul i32 %305, %198
  %319 = mul <2 x i32> %316, %299
  %320 = shufflevector <2 x i32> %317, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %321 = insertelement <8 x i32> %320, i32 %318, i64 2
  %shuffle115 = shufflevector <8 x i32> %321, <8 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 2, i32 2>
  %322 = add <8 x i32> %shuffle115, %shuffle116
  %323 = insertelement <8 x i32> poison, i32 %306, i64 0
  %shuffle117 = shufflevector <8 x i32> %323, <8 x i32> poison, <8 x i32> zeroinitializer
  %324 = mul <8 x i32> %322, %shuffle117
  %325 = sext <8 x i32> %324 to <8 x i64>
  %326 = insertelement <8 x float*> poison, float* %304, i64 0
  %shuffle = shufflevector <8 x float*> %326, <8 x float*> poison, <8 x i32> zeroinitializer
  %327 = getelementptr float, <8 x float*> %shuffle, <8 x i64> %325
  %328 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %327, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %329 = insertelement <8 x i32> poison, i32 %309, i64 0
  %330 = shufflevector <2 x i32> %319, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %331 = shufflevector <8 x i32> %329, <8 x i32> %330, <8 x i32> <i32 0, i32 8, i32 9, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle119 = shufflevector <8 x i32> %331, <8 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 2, i32 2>
  %332 = shufflevector <2 x i32> %312, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %333 = insertelement <8 x i32> %332, i32 %314, i64 2
  %shuffle120 = shufflevector <8 x i32> %333, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 0, i32 1, i32 2, i32 0, i32 1>
  %334 = add <8 x i32> %shuffle119, %shuffle120
  %335 = mul <8 x i32> %334, %shuffle117
  %336 = sext <8 x i32> %335 to <8 x i64>
  %337 = getelementptr float, <8 x float*> %shuffle, <8 x i64> %336
  %338 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %337, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %339 = fsub reassoc ninf nsz <8 x float> %328, %338
  %340 = fmul reassoc ninf nsz <8 x float> %339, %339
  %341 = add i32 %318, %117
  %342 = mul i32 %341, %306
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, float* %304, i64 %343
  %345 = load float, float* %344, align 4
  %346 = extractelement <2 x i32> %319, i64 1
  %347 = add i32 %346, %314
  %348 = mul i32 %347, %306
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, float* %304, i64 %349
  %351 = load float, float* %350, align 4
  %352 = fsub reassoc ninf nsz float %345, %351
  %353 = fmul reassoc ninf nsz float %352, %352
  %354 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float %353, <8 x float> %340)
  %355 = fmul reassoc ninf nsz float %354, 0x3FBC71C720000000
  %356 = mul i32 %lsr.iv126, %305
  %357 = add i32 %300, %356
  %358 = mul i32 %357, %306
  %359 = add i32 %358, 1
  %360 = sext i32 %359 to i64
  %361 = getelementptr float, float* %304, i64 %360
  %362 = load float, float* %361, align 4
  %363 = add i32 %358, 2
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, float* %304, i64 %364
  %366 = load float, float* %365, align 4
  %367 = fsub reassoc ninf nsz float %274, %362
  %368 = fsub reassoc ninf nsz float %278, %366
  %369 = fmul reassoc ninf nsz float %367, %367
  %370 = fmul reassoc ninf nsz float %368, %368
  %371 = fadd reassoc ninf nsz float %370, %369
  %372 = fmul reassoc ninf nsz float %371, 2.500000e-01
  %373 = fadd reassoc ninf nsz float %372, %355
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.043 = phi float [ %373, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %374 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %375 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %374, i64 0, i32 14
  %376 = load i8*, i8** %375, align 8
  %377 = getelementptr inbounds i8, i8* %376, i64 16
  %378 = bitcast i8* %377 to float*
  %379 = load float, float* %378, align 4
  %380 = fcmp reassoc ninf nsz ugt float %.043, %379
  br i1 %380, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.043
  %381 = getelementptr inbounds i8, i8* %376, i64 20
  %382 = bitcast i8* %381 to float*
  %383 = load float, float* %382, align 4
  %384 = fmul reassoc ninf nsz float %383, %neg44
  %385 = tail call float @expf(float noundef %384) #1
  %386 = fadd reassoc ninf nsz float %385, %.36288
  %387 = load float*, float** %25, align 8
  %388 = load i32, i32* %26, align 4
  %389 = load i32, i32* %27, align 4
  %390 = mul i32 %lsr.iv126, %388
  %391 = add i32 %300, %390
  %392 = mul i32 %391, %389
  %393 = sext i32 %392 to i64
  %394 = getelementptr float, float* %387, i64 %393
  %395 = load float, float* %394, align 4
  %396 = fmul reassoc ninf nsz float %395, %385
  %397 = fadd reassoc ninf nsz float %396, %.35889
  %398 = add i32 %392, 1
  %399 = sext i32 %398 to i64
  %400 = getelementptr float, float* %387, i64 %399
  %401 = load float, float* %400, align 4
  %402 = fmul reassoc ninf nsz float %401, %385
  %403 = fadd reassoc ninf nsz float %402, %.35490
  %404 = add i32 %392, 2
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, float* %387, i64 %405
  %407 = load float, float* %406, align 4
  %408 = fmul reassoc ninf nsz float %407, %385
  %409 = fadd reassoc ninf nsz float %408, %.391
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %410 = fmul reassoc ninf nsz float %289, %23
  %411 = fdiv reassoc ninf nsz float 1.000000e+00, %.059
  %412 = fmul reassoc ninf nsz float %.055, %411
  %413 = fmul reassoc ninf nsz float %.051, %411
  %414 = fmul reassoc ninf nsz float %.048, %411
  %415 = load float*, float** %25, align 8
  %416 = load i32, i32* %26, align 4
  %417 = load i32, i32* %27, align 4
  %418 = mul i32 %416, %60
  %419 = add i32 %418, %62
  %420 = mul i32 %419, %417
  %421 = sext i32 %420 to i64
  %422 = getelementptr float, float* %415, i64 %421
  %423 = load float, float* %422, align 4
  %424 = fsub reassoc ninf nsz float %423, %412
  %425 = add i32 %420, 1
  %426 = sext i32 %425 to i64
  %427 = getelementptr float, float* %415, i64 %426
  %428 = load float, float* %427, align 4
  %429 = fsub reassoc ninf nsz float %428, %413
  %430 = add i32 %420, 2
  %431 = sext i32 %430 to i64
  %432 = getelementptr float, float* %415, i64 %431
  %433 = load float, float* %432, align 4
  %434 = fsub reassoc ninf nsz float %433, %414
  %435 = tail call float @llvm.fabs.f32(float %424)
  %436 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %437 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %436, i64 0, i32 14
  %438 = load i8*, i8** %437, align 8
  %439 = getelementptr inbounds i8, i8* %438, i64 24
  %440 = bitcast i8* %439 to float*
  %441 = load float, float* %440, align 4
  %442 = fsub reassoc ninf nsz float %435, %441
  %443 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %442, float 0.000000e+00)
  %444 = fcmp reassoc ninf nsz oge float %424, 0.000000e+00
  %445 = uitofp i1 %444 to float
  %446 = fcmp reassoc ninf nsz ole float %424, 0.000000e+00
  %447 = uitofp i1 %446 to float
  %448 = fsub reassoc ninf nsz float %445, %447
  %449 = tail call float @llvm.fabs.f32(float %429)
  %450 = fsub reassoc ninf nsz float %449, %441
  %451 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %450, float 0.000000e+00)
  %452 = fcmp reassoc ninf nsz oge float %429, 0.000000e+00
  %453 = uitofp i1 %452 to float
  %454 = fcmp reassoc ninf nsz ole float %429, 0.000000e+00
  %455 = uitofp i1 %454 to float
  %456 = fsub reassoc ninf nsz float %453, %455
  %457 = tail call float @llvm.fabs.f32(float %434)
  %458 = fsub reassoc ninf nsz float %457, %441
  %459 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %458, float 0.000000e+00)
  %460 = fcmp reassoc ninf nsz oge float %434, 0.000000e+00
  %461 = uitofp i1 %460 to float
  %462 = fcmp reassoc ninf nsz ole float %434, 0.000000e+00
  %463 = uitofp i1 %462 to float
  %464 = fsub reassoc ninf nsz float %461, %463
  %465 = fmul reassoc ninf nsz float %448, %410
  %466 = fmul reassoc ninf nsz float %465, %443
  %467 = fadd reassoc ninf nsz float %466, %412
  %468 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %469 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %468, i64 0, i32 2, i32 1
  %470 = load float*, float** %469, align 8
  %471 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %468, i64 0, i32 2, i32 0, i32 1
  %472 = load i32, i32* %471, align 4
  %473 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %468, i64 0, i32 2, i32 0, i32 2
  %474 = load i32, i32* %473, align 4
  %475 = mul i32 %472, %60
  %476 = add i32 %475, %62
  %477 = mul i32 %476, %474
  %478 = sext i32 %477 to i64
  %479 = getelementptr float, float* %470, i64 %478
  store float %467, float* %479, align 4
  %480 = fmul reassoc ninf nsz float %456, %410
  %481 = fmul reassoc ninf nsz float %480, %451
  %482 = fadd reassoc ninf nsz float %481, %413
  %483 = load float*, float** %469, align 8
  %484 = load i32, i32* %471, align 4
  %485 = load i32, i32* %473, align 4
  %486 = mul i32 %484, %60
  %487 = add i32 %486, %62
  %488 = mul i32 %487, %485
  %489 = add i32 %488, 1
  %490 = sext i32 %489 to i64
  %491 = getelementptr float, float* %483, i64 %490
  store float %482, float* %491, align 4
  %492 = fmul reassoc ninf nsz float %464, %410
  %493 = fmul reassoc ninf nsz float %492, %459
  %494 = fadd reassoc ninf nsz float %493, %414
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %495 = load float*, float** %25, align 8
  %496 = load i32, i32* %26, align 4
  %497 = load i32, i32* %27, align 4
  %498 = mul i32 %496, %60
  %499 = add i32 %498, %62
  %500 = mul i32 %499, %497
  %501 = sext i32 %500 to i64
  %502 = getelementptr float, float* %495, i64 %501
  %503 = load float, float* %502, align 4
  %504 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %505 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %504, i64 0, i32 2, i32 1
  %506 = load float*, float** %505, align 8
  %507 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %504, i64 0, i32 2, i32 0, i32 1
  %508 = load i32, i32* %507, align 4
  %509 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %504, i64 0, i32 2, i32 0, i32 2
  %510 = load i32, i32* %509, align 4
  %511 = mul i32 %508, %60
  %512 = add i32 %511, %62
  %513 = mul i32 %512, %510
  %514 = sext i32 %513 to i64
  %515 = getelementptr float, float* %506, i64 %514
  store float %503, float* %515, align 4
  %516 = load float*, float** %25, align 8
  %517 = load i32, i32* %26, align 4
  %518 = load i32, i32* %27, align 4
  %519 = mul i32 %517, %60
  %520 = add i32 %519, %62
  %521 = mul i32 %520, %518
  %522 = add i32 %521, 1
  %523 = sext i32 %522 to i64
  %524 = getelementptr float, float* %516, i64 %523
  %525 = load float, float* %524, align 4
  %526 = load float*, float** %505, align 8
  %527 = load i32, i32* %507, align 4
  %528 = load i32, i32* %509, align 4
  %529 = mul i32 %527, %60
  %530 = add i32 %529, %62
  %531 = mul i32 %530, %528
  %532 = add i32 %531, 1
  %533 = sext i32 %532 to i64
  %534 = getelementptr float, float* %526, i64 %533
  store float %525, float* %534, align 4
  %535 = load float*, float** %25, align 8
  %536 = load i32, i32* %26, align 4
  %537 = load i32, i32* %27, align 4
  %538 = mul i32 %536, %60
  %539 = add i32 %538, %62
  %540 = mul i32 %539, %537
  %541 = add i32 %540, 2
  %542 = sext i32 %541 to i64
  %543 = getelementptr float, float* %535, i64 %542
  %544 = load float, float* %543, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink114 = phi float** [ %505, %false_block46 ], [ %469, %true_block45 ]
  %.sink113 = phi i32* [ %507, %false_block46 ], [ %471, %true_block45 ]
  %.sink112 = phi i32* [ %509, %false_block46 ], [ %473, %true_block45 ]
  %.sink = phi float [ %544, %false_block46 ], [ %494, %true_block45 ]
  %545 = load float*, float** %.sink114, align 8
  %546 = load i32, i32* %.sink113, align 4
  %547 = load i32, i32* %.sink112, align 4
  %548 = mul i32 %546, %60
  %549 = add i32 %548, %62
  %550 = mul i32 %549, %547
  %551 = add i32 %550, 2
  %552 = sext i32 %551 to i64
  %553 = getelementptr float, float* %545, i64 %552
  store float %.sink, float* %553, align 4
  %554 = add nsw i32 %.06998, 1
  %lsr.iv.next123 = add i32 %lsr.iv122, 1
  %lsr.iv.next125 = add i32 %lsr.iv124, 1
  %exitcond102.not = icmp eq i32 %554, %19
  br i1 %exitcond102.not, label %after_for.loopexit, label %for_loop_body
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
  %4 = alloca %struct.RuntimeContext.36, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.36**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.36*, %struct.RuntimeContext.36** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.36* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.36* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
