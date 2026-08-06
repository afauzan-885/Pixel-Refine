; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.60*, void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.60 = type { i8*, %struct.LLVMRuntime.59*, i32, i64* }
%struct.LLVMRuntime.59 = type { %struct.PreallocatedMemoryChunk.55, %struct.PreallocatedMemoryChunk.55, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.56*], [1024 x %struct.NodeManager.57*], [1024 x i8*], i8*, %struct.RandState.58*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.55 = type { i8*, i8*, i64 }
%struct.ListManager.56 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.59* }
%struct.NodeManager.57 = type { %struct.LLVMRuntime.59*, i32, i32, i32, i32, %struct.ListManager.56*, %struct.ListManager.56*, %struct.ListManager.56*, i32 }
%struct.RandState.58 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_nlm_3ch_s5_p2_c418_0_kernel_0_serial(%struct.RuntimeContext.60* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.60* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %1, i64 0, i32 5
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 20
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fmul reassoc ninf nsz float %4, 3.500000e+00
  %13 = fadd reassoc ninf nsz float %12, 0x3F60624DE0000000
  %14 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %6, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 16
  %18 = bitcast i8* %17 to float*
  store float %13, float* %18, align 4
  %19 = fmul reassoc ninf nsz float %3, 0x3FE6666660000000
  %20 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %21 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %20, i64 0, i32 7
  %22 = load float, float* %21, align 4
  %23 = fmul reassoc ninf nsz float %19, %22
  %24 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %6, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 24
  %28 = bitcast i8* %27 to float*
  store float %23, float* %28, align 4
  %29 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %29, i64 0, i32 3
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 8
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %39 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %38, i64 0, i32 4
  %40 = load i32, i32* %39, align 4
  %41 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %6, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %41, i64 0, i32 14
  %43 = load i8*, i8** %42, align 8
  %44 = getelementptr inbounds i8, i8* %43, i64 12
  %45 = bitcast i8* %44 to i32*
  store i32 %40, i32* %45, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %47 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %6, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  store i32 %46, i32* %51, align 4
  %52 = mul i32 %46, %37
  %53 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %6, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %53, i64 0, i32 14
  %55 = bitcast i8** %54 to i32**
  %56 = load i32*, i32** %55, align 8
  store i32 %52, i32* %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_nlm_3ch_s5_p2_c418_0_kernel_1_range_for(%struct.RuntimeContext.60* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.60* %context, %struct.RuntimeContext.60** %4, align 8
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.60*, i8*, i32)* @function_body, void (%struct.RuntimeContext.60*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.60* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.60* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }**
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
  %31 = add i32 %17, -5
  %32 = add i32 %17, -3
  %33 = add i32 %17, -4
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %lsr.iv141 = phi i32 [ %33, %for_loop_body.lr.ph ], [ %lsr.iv.next142, %after_if47 ]
  %lsr.iv139 = phi i32 [ %32, %for_loop_body.lr.ph ], [ %lsr.iv.next140, %after_if47 ]
  %lsr.iv137 = phi i32 [ %31, %for_loop_body.lr.ph ], [ %lsr.iv.next138, %after_if47 ]
  %.06998 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %601, %after_if47 ]
  %34 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %35 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %34, i64 0, i32 14
  %36 = load i8*, i8** %35, align 8
  %37 = getelementptr inbounds i8, i8* %36, i64 4
  %38 = bitcast i8* %37 to i32*
  %39 = load i32, i32* %38, align 4
  %40 = sdiv i32 %.06998, %39
  %41 = mul i32 %40, %39
  %42 = xor i32 %39, %.06998
  %43 = icmp slt i32 %42, 0
  %44 = icmp ne i32 %.06998, 0
  %45 = icmp ne i32 %41, %.06998
  %46 = and i1 %44, %43
  %47 = and i1 %46, %45
  %.neg75 = sext i1 %47 to i32
  %48 = getelementptr inbounds i8, i8* %36, i64 8
  %49 = bitcast i8* %48 to i32*
  %50 = load i32, i32* %49, align 4
  %51 = add i32 %50, -1
  %52 = getelementptr inbounds i8, i8* %36, i64 12
  %53 = bitcast i8* %52 to i32*
  %54 = load i32, i32* %53, align 4
  %55 = add i32 %54, -1
  %56 = load float*, float** %25, align 8
  %57 = load i32, i32* %26, align 4
  %58 = load i32, i32* %27, align 4
  %59 = add i32 %40, %.neg75
  %60 = mul i32 %59, %39
  %61 = add i32 %59, 1
  %62 = insertelement <2 x i32> poison, i32 %59, i64 0
  %63 = shufflevector <2 x i32> %62, <2 x i32> poison, <2 x i32> zeroinitializer
  %64 = add <2 x i32> %63, <i32 -2, i32 -1>
  %65 = shufflevector <2 x i32> %64, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %66 = insertelement <4 x i32> %65, i32 %59, i64 2
  %67 = insertelement <4 x i32> %66, i32 %61, i64 3
  %68 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %67, <4 x i32> zeroinitializer)
  %69 = insertelement <4 x i32> poison, i32 %51, i64 0
  %shuffle116 = shufflevector <4 x i32> %69, <4 x i32> poison, <4 x i32> zeroinitializer
  %70 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle116, <4 x i32> %68)
  %71 = extractelement <4 x i32> %70, i64 1
  %72 = mul i32 %57, %71
  %73 = extractelement <4 x i32> %70, i64 2
  %74 = mul i32 %57, %73
  %75 = extractelement <4 x i32> %70, i64 3
  %76 = mul i32 %57, %75
  %77 = sub i32 %.06998, %60
  %78 = add i32 %77, -1
  %79 = add i32 %77, 1
  %80 = add i32 %77, 2
  %81 = insertelement <4 x i32> poison, i32 %78, i64 0
  %82 = insertelement <4 x i32> %81, i32 %77, i64 1
  %83 = insertelement <4 x i32> %82, i32 %79, i64 2
  %84 = insertelement <4 x i32> %83, i32 %80, i64 3
  %85 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %84, <4 x i32> zeroinitializer)
  %86 = insertelement <4 x i32> poison, i32 %55, i64 0
  %shuffle136 = shufflevector <4 x i32> %86, <4 x i32> poison, <4 x i32> zeroinitializer
  %87 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle136, <4 x i32> %85)
  %88 = extractelement <4 x i32> %87, i64 0
  %89 = add i32 %72, %88
  %90 = mul i32 %89, %58
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, float* %56, i64 %91
  %93 = load float, float* %92, align 4
  %94 = add i32 %90, 1
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, float* %56, i64 %95
  %97 = load float, float* %96, align 4
  %98 = fadd reassoc ninf nsz float %97, %93
  %99 = add i32 %90, 2
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %56, i64 %100
  %102 = load float, float* %101, align 4
  %103 = fadd reassoc ninf nsz float %98, %102
  %104 = fmul reassoc ninf nsz float %103, 0x3FD5555560000000
  %105 = fmul reassoc ninf nsz float %104, %104
  %106 = extractelement <4 x i32> %87, i64 1
  %107 = add i32 %72, %106
  %108 = mul i32 %107, %58
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %56, i64 %109
  %111 = load float, float* %110, align 4
  %112 = add i32 %108, 1
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %56, i64 %113
  %115 = load float, float* %114, align 4
  %116 = fadd reassoc ninf nsz float %115, %111
  %117 = add i32 %108, 2
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, float* %56, i64 %118
  %120 = load float, float* %119, align 4
  %121 = fadd reassoc ninf nsz float %116, %120
  %122 = fmul reassoc ninf nsz float %121, 0x3FD5555560000000
  %123 = fadd reassoc ninf nsz float %122, %104
  %124 = fmul reassoc ninf nsz float %122, %122
  %125 = fadd reassoc ninf nsz float %124, %105
  %126 = extractelement <4 x i32> %87, i64 2
  %127 = add i32 %72, %126
  %128 = mul i32 %127, %58
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %56, i64 %129
  %131 = load float, float* %130, align 4
  %132 = add i32 %128, 1
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %56, i64 %133
  %135 = load float, float* %134, align 4
  %136 = fadd reassoc ninf nsz float %135, %131
  %137 = add i32 %128, 2
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %56, i64 %138
  %140 = load float, float* %139, align 4
  %141 = fadd reassoc ninf nsz float %136, %140
  %142 = fmul reassoc ninf nsz float %141, 0x3FD5555560000000
  %143 = fadd reassoc ninf nsz float %142, %123
  %144 = fmul reassoc ninf nsz float %142, %142
  %145 = fadd reassoc ninf nsz float %144, %125
  %146 = add i32 %74, %88
  %147 = mul i32 %146, %58
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %56, i64 %148
  %150 = load float, float* %149, align 4
  %151 = add i32 %147, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, float* %56, i64 %152
  %154 = load float, float* %153, align 4
  %155 = fadd reassoc ninf nsz float %154, %150
  %156 = add i32 %147, 2
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %56, i64 %157
  %159 = load float, float* %158, align 4
  %160 = fadd reassoc ninf nsz float %155, %159
  %161 = fmul reassoc ninf nsz float %160, 0x3FD5555560000000
  %162 = fadd reassoc ninf nsz float %161, %143
  %163 = fmul reassoc ninf nsz float %161, %161
  %164 = fadd reassoc ninf nsz float %163, %145
  %165 = add i32 %74, %106
  %166 = mul i32 %165, %58
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, float* %56, i64 %167
  %169 = load float, float* %168, align 4
  %170 = add i32 %166, 1
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %56, i64 %171
  %173 = load float, float* %172, align 4
  %174 = fadd reassoc ninf nsz float %173, %169
  %175 = add i32 %166, 2
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, float* %56, i64 %176
  %178 = load float, float* %177, align 4
  %179 = fadd reassoc ninf nsz float %174, %178
  %180 = fmul reassoc ninf nsz float %179, 0x3FD5555560000000
  %181 = fadd reassoc ninf nsz float %180, %162
  %182 = fmul reassoc ninf nsz float %180, %180
  %183 = fadd reassoc ninf nsz float %182, %164
  %184 = add i32 %74, %126
  %185 = mul i32 %184, %58
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %56, i64 %186
  %188 = load float, float* %187, align 4
  %189 = add i32 %185, 1
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %56, i64 %190
  %192 = load float, float* %191, align 4
  %193 = fadd reassoc ninf nsz float %192, %188
  %194 = add i32 %185, 2
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, float* %56, i64 %195
  %197 = load float, float* %196, align 4
  %198 = fadd reassoc ninf nsz float %193, %197
  %199 = fmul reassoc ninf nsz float %198, 0x3FD5555560000000
  %200 = fadd reassoc ninf nsz float %199, %181
  %201 = fmul reassoc ninf nsz float %199, %199
  %202 = fadd reassoc ninf nsz float %201, %183
  %203 = add i32 %76, %88
  %204 = mul i32 %203, %58
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %56, i64 %205
  %207 = load float, float* %206, align 4
  %208 = add i32 %204, 1
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %56, i64 %209
  %211 = load float, float* %210, align 4
  %212 = fadd reassoc ninf nsz float %211, %207
  %213 = add i32 %204, 2
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, float* %56, i64 %214
  %216 = load float, float* %215, align 4
  %217 = fadd reassoc ninf nsz float %212, %216
  %218 = fmul reassoc ninf nsz float %217, 0x3FD5555560000000
  %219 = fadd reassoc ninf nsz float %218, %200
  %220 = fmul reassoc ninf nsz float %218, %218
  %221 = fadd reassoc ninf nsz float %220, %202
  %222 = add i32 %76, %106
  %223 = mul i32 %222, %58
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %56, i64 %224
  %226 = load float, float* %225, align 4
  %227 = add i32 %223, 1
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, float* %56, i64 %228
  %230 = load float, float* %229, align 4
  %231 = fadd reassoc ninf nsz float %230, %226
  %232 = add i32 %223, 2
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, float* %56, i64 %233
  %235 = load float, float* %234, align 4
  %236 = fadd reassoc ninf nsz float %231, %235
  %237 = fmul reassoc ninf nsz float %236, 0x3FD5555560000000
  %238 = fadd reassoc ninf nsz float %237, %219
  %239 = fmul reassoc ninf nsz float %237, %237
  %240 = fadd reassoc ninf nsz float %239, %221
  %241 = add i32 %76, %126
  %242 = mul i32 %241, %58
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, float* %56, i64 %243
  %245 = load float, float* %244, align 4
  %246 = add i32 %242, 1
  %247 = sext i32 %246 to i64
  %248 = getelementptr float, float* %56, i64 %247
  %249 = load float, float* %248, align 4
  %250 = fadd reassoc ninf nsz float %249, %245
  %251 = add i32 %242, 2
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, float* %56, i64 %252
  %254 = load float, float* %253, align 4
  %255 = fadd reassoc ninf nsz float %250, %254
  %256 = fmul reassoc ninf nsz float %255, 0x3FD5555560000000
  %257 = fadd reassoc ninf nsz float %256, %238
  %258 = fmul reassoc ninf nsz float %256, %256
  %259 = fadd reassoc ninf nsz float %258, %240
  %260 = fmul reassoc ninf nsz float %257, 0x3FBC71C720000000
  %261 = fmul reassoc ninf nsz float %259, 0x3FBC71C720000000
  %262 = fmul reassoc ninf nsz float %260, %260
  %263 = fsub reassoc ninf nsz float %261, %262
  %264 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %263, float 0.000000e+00)
  %265 = fmul reassoc ninf nsz float %264, -3.500000e+02
  %266 = tail call float @expf(float noundef %265) #1
  %267 = fsub reassoc ninf nsz float 1.000000e+00, %266
  %268 = load float*, float** %28, align 8
  %269 = load i32, i32* %29, align 4
  %270 = load i32, i32* %30, align 4
  %271 = mul i32 %269, %59
  %272 = add i32 %271, %77
  %273 = mul i32 %272, %270
  %274 = add i32 %273, 1
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, float* %268, i64 %275
  %277 = load float, float* %276, align 4
  %278 = add i32 %273, 2
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, float* %268, i64 %279
  %281 = load float, float* %280, align 4
  %282 = add i32 %77, -2
  %283 = tail call i32 @llvm.smax.i32(i32 %282, i32 0)
  %284 = tail call i32 @llvm.smin.i32(i32 %55, i32 %283)
  %285 = add i32 %59, 2
  %286 = tail call i32 @llvm.smax.i32(i32 %285, i32 0)
  %287 = tail call i32 @llvm.smin.i32(i32 %51, i32 %286)
  %288 = insertelement <16 x i32> poison, i32 %284, i64 0
  %289 = shufflevector <4 x i32> %87, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %290 = shufflevector <4 x i32> %87, <4 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %291 = shufflevector <16 x i32> %288, <16 x i32> %290, <16 x i32> <i32 0, i32 16, i32 17, i32 18, i32 19, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle118 = shufflevector <16 x i32> %291, <16 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0>
  %292 = insertelement <8 x i32> %289, i32 %284, i64 4
  %shuffle128 = shufflevector <8 x i32> %292, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2>
  %293 = extractelement <4 x i32> %87, i64 3
  %294 = sub i32 %lsr.iv137, %60
  %295 = sub i32 %lsr.iv139, %60
  %296 = sub i32 %lsr.iv141, %60
  %297 = add i32 %40, -5
  %298 = add i32 %297, %.neg75
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv143 = phi i32 [ %298, %for_loop_body ], [ %lsr.iv.next144, %for_loop_inc10 ]
  %.04797 = phi i32 [ -5, %for_loop_body ], [ %301, %for_loop_inc10 ]
  %.14996 = phi float [ 0.000000e+00, %for_loop_body ], [ %.048, %for_loop_inc10 ]
  %.15295 = phi float [ 0.000000e+00, %for_loop_body ], [ %.051, %for_loop_inc10 ]
  %.15694 = phi float [ 0.000000e+00, %for_loop_body ], [ %.055, %for_loop_inc10 ]
  %.16093 = phi float [ 0.000000e+00, %for_loop_body ], [ %.059, %for_loop_inc10 ]
  %299 = add i32 %.04797, %59
  %300 = icmp slt i32 %299, 0
  br i1 %300, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.059 = phi float [ %.16093, %false_block ], [ %.16093, %for_loop_body9 ], [ %.261, %for_loop_inc10.loopexit ]
  %.055 = phi float [ %.15694, %false_block ], [ %.15694, %for_loop_body9 ], [ %.257, %for_loop_inc10.loopexit ]
  %.051 = phi float [ %.15295, %false_block ], [ %.15295, %for_loop_body9 ], [ %.253, %for_loop_inc10.loopexit ]
  %.048 = phi float [ %.14996, %false_block ], [ %.14996, %for_loop_body9 ], [ %.250, %for_loop_inc10.loopexit ]
  %301 = add nsw i32 %.04797, 1
  %lsr.iv.next144 = add i32 %lsr.iv143, 1
  %exitcond101.not = icmp eq i32 %301, 6
  br i1 %exitcond101.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %302 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %267, float 0x3FE6666660000000)
  %303 = fcmp reassoc ninf nsz ogt float %.059, 0x3D71979980000000
  br i1 %303, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %304 = load i32, i32* %49, align 4
  %.not76 = icmp slt i32 %299, %304
  br i1 %.not76, label %after_if15, label %for_loop_inc10

after_if15:                                       ; preds = %false_block
  %.not = icmp ne i32 %.04797, 0
  %305 = insertelement <2 x i32> poison, i32 %299, i64 0
  %306 = shufflevector <2 x i32> %305, <2 x i32> poison, <2 x i32> zeroinitializer
  %307 = add <2 x i32> %306, <i32 -2, i32 -1>
  %308 = add i32 %299, 1
  %309 = shufflevector <2 x i32> %307, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %310 = insertelement <4 x i32> %309, i32 %299, i64 2
  %311 = insertelement <4 x i32> %310, i32 %308, i64 3
  %312 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %311, <4 x i32> zeroinitializer)
  %313 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle116, <4 x i32> %312)
  %314 = add i32 %299, 2
  %315 = tail call i32 @llvm.smax.i32(i32 %314, i32 0)
  %316 = tail call i32 @llvm.smin.i32(i32 %51, i32 %315)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %after_if15
  %lsr.iv = phi i32 [ 0, %after_if15 ], [ %lsr.iv.next, %for_loop_inc17 ]
  %.391 = phi float [ %.14996, %after_if15 ], [ %.250, %for_loop_inc17 ]
  %.35490 = phi float [ %.15295, %after_if15 ], [ %.253, %for_loop_inc17 ]
  %.35889 = phi float [ %.15694, %after_if15 ], [ %.257, %for_loop_inc17 ]
  %.36288 = phi float [ %.16093, %after_if15 ], [ %.261, %for_loop_inc17 ]
  %317 = add i32 %294, %lsr.iv
  %318 = icmp slt i32 %317, 0
  br i1 %318, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.261 = phi float [ %.36288, %false_block21 ], [ %433, %true_block41 ], [ %.36288, %after_if32 ], [ %.36288, %for_loop_body16 ]
  %.257 = phi float [ %.35889, %false_block21 ], [ %444, %true_block41 ], [ %.35889, %after_if32 ], [ %.35889, %for_loop_body16 ]
  %.253 = phi float [ %.35490, %false_block21 ], [ %450, %true_block41 ], [ %.35490, %after_if32 ], [ %.35490, %for_loop_body16 ]
  %.250 = phi float [ %.391, %false_block21 ], [ %456, %true_block41 ], [ %.391, %after_if32 ], [ %.391, %for_loop_body16 ]
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 11
  br i1 %exitcond.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %319 = load i32, i32* %53, align 4
  %.not77 = icmp slt i32 %317, %319
  br i1 %.not77, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %320 = icmp ne i32 %lsr.iv, 5
  %spec.select = select i1 %.not, i1 true, i1 %320
  br i1 %spec.select, label %for_loop_test36.preheader, label %after_if32

for_loop_test36.preheader:                        ; preds = %after_if25
  %321 = load float*, float** %28, align 8
  %322 = load i32, i32* %29, align 4
  %323 = load i32, i32* %30, align 4
  %324 = call i32 @llvm.smax.i32(i32 %317, i32 2)
  %325 = add nsw i32 %324, -2
  %326 = tail call i32 @llvm.smin.i32(i32 %55, i32 %325)
  %327 = call i32 @llvm.smax.i32(i32 %317, i32 1)
  %328 = add nsw i32 %327, -1
  %329 = add i32 %296, %lsr.iv
  %330 = add i32 %295, %lsr.iv
  %331 = tail call i32 @llvm.smax.i32(i32 %330, i32 0)
  %332 = insertelement <4 x i32> poison, i32 %328, i64 0
  %333 = insertelement <4 x i32> %332, i32 %317, i64 1
  %334 = insertelement <4 x i32> %333, i32 %329, i64 2
  %335 = insertelement <4 x i32> %334, i32 %331, i64 3
  %336 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle136, <4 x i32> %335)
  %337 = insertelement <4 x i32> poison, i32 %322, i64 0
  %shuffle115 = shufflevector <4 x i32> %337, <4 x i32> poison, <4 x i32> zeroinitializer
  %338 = mul <4 x i32> %shuffle115, %70
  %shuffle117 = shufflevector <4 x i32> %338, <4 x i32> poison, <16 x i32> <i32 0, i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1, i32 1, i32 2, i32 2, i32 2, i32 2, i32 2, i32 3>
  %339 = mul <4 x i32> %shuffle115, %313
  %shuffle123 = shufflevector <4 x i32> %339, <4 x i32> poison, <16 x i32> <i32 0, i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1, i32 1, i32 2, i32 2, i32 2, i32 2, i32 2, i32 3>
  %340 = add <16 x i32> %shuffle117, %shuffle118
  %341 = insertelement <16 x i32> poison, i32 %323, i64 0
  %shuffle119 = shufflevector <16 x i32> %341, <16 x i32> poison, <16 x i32> zeroinitializer
  %342 = mul <16 x i32> %340, %shuffle119
  %343 = sext <16 x i32> %342 to <16 x i64>
  %344 = insertelement <16 x float*> poison, float* %321, i64 0
  %shuffle = shufflevector <16 x float*> %344, <16 x float*> poison, <16 x i32> zeroinitializer
  %345 = getelementptr float, <16 x float*> %shuffle, <16 x i64> %343
  %346 = call <16 x float> @llvm.masked.gather.v16f32.v16p0f32(<16 x float*> %345, i32 4, <16 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <16 x float> undef)
  %347 = insertelement <16 x i32> poison, i32 %326, i64 0
  %348 = shufflevector <4 x i32> %336, <4 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %349 = shufflevector <16 x i32> %347, <16 x i32> %348, <16 x i32> <i32 0, i32 16, i32 17, i32 18, i32 19, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %shuffle124 = shufflevector <16 x i32> %349, <16 x i32> poison, <16 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2, i32 3, i32 4, i32 0>
  %350 = add <16 x i32> %shuffle123, %shuffle124
  %351 = mul <16 x i32> %350, %shuffle119
  %352 = sext <16 x i32> %351 to <16 x i64>
  %353 = getelementptr float, <16 x float*> %shuffle, <16 x i64> %352
  %354 = call <16 x float> @llvm.masked.gather.v16f32.v16p0f32(<16 x float*> %353, i32 4, <16 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <16 x float> undef)
  %355 = fsub reassoc ninf nsz <16 x float> %346, %354
  %356 = fmul reassoc ninf nsz <16 x float> %355, %355
  %357 = extractelement <4 x i32> %338, i64 3
  %358 = extractelement <4 x i32> %339, i64 3
  %359 = mul i32 %322, %287
  %360 = mul i32 %322, %316
  %361 = insertelement <8 x i32> poison, i32 %357, i64 0
  %362 = insertelement <8 x i32> %361, i32 %357, i64 1
  %363 = insertelement <8 x i32> %362, i32 %357, i64 2
  %364 = insertelement <8 x i32> %363, i32 %357, i64 3
  %365 = insertelement <8 x i32> %364, i32 %359, i64 4
  %shuffle127 = shufflevector <8 x i32> %365, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 4, i32 4, i32 4>
  %366 = add <8 x i32> %shuffle127, %shuffle128
  %367 = insertelement <8 x i32> poison, i32 %323, i64 0
  %shuffle129 = shufflevector <8 x i32> %367, <8 x i32> poison, <8 x i32> zeroinitializer
  %368 = mul <8 x i32> %366, %shuffle129
  %369 = sext <8 x i32> %368 to <8 x i64>
  %370 = insertelement <8 x float*> poison, float* %321, i64 0
  %shuffle126 = shufflevector <8 x float*> %370, <8 x float*> poison, <8 x i32> zeroinitializer
  %371 = getelementptr float, <8 x float*> %shuffle126, <8 x i64> %369
  %372 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %371, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %373 = insertelement <8 x i32> poison, i32 %358, i64 0
  %374 = insertelement <8 x i32> %373, i32 %358, i64 1
  %375 = insertelement <8 x i32> %374, i32 %358, i64 2
  %376 = insertelement <8 x i32> %375, i32 %358, i64 3
  %377 = insertelement <8 x i32> %376, i32 %360, i64 4
  %shuffle131 = shufflevector <8 x i32> %377, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 4, i32 4, i32 4>
  %378 = shufflevector <4 x i32> %336, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %379 = insertelement <8 x i32> %378, i32 %326, i64 4
  %shuffle132 = shufflevector <8 x i32> %379, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2>
  %380 = add <8 x i32> %shuffle131, %shuffle132
  %381 = mul <8 x i32> %380, %shuffle129
  %382 = sext <8 x i32> %381 to <8 x i64>
  %383 = getelementptr float, <8 x float*> %shuffle126, <8 x i64> %382
  %384 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %383, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %385 = fsub reassoc ninf nsz <8 x float> %372, %384
  %386 = fmul reassoc ninf nsz <8 x float> %385, %385
  %387 = add i32 %359, %293
  %388 = mul i32 %387, %323
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, float* %321, i64 %389
  %391 = load float, float* %390, align 4
  %392 = extractelement <4 x i32> %336, i64 3
  %393 = add i32 %360, %392
  %394 = mul i32 %393, %323
  %395 = sext i32 %394 to i64
  %396 = getelementptr float, float* %321, i64 %395
  %397 = load float, float* %396, align 4
  %398 = fsub reassoc ninf nsz float %391, %397
  %399 = fmul reassoc ninf nsz float %398, %398
  %400 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %386)
  %401 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v16f32(float %400, <16 x float> %356)
  %op.rdx134 = fadd reassoc ninf nsz float %401, %399
  %402 = fmul reassoc ninf nsz float %op.rdx134, 0x3FA47AE140000000
  %403 = mul i32 %lsr.iv143, %322
  %404 = add i32 %317, %403
  %405 = mul i32 %404, %323
  %406 = add i32 %405, 1
  %407 = sext i32 %406 to i64
  %408 = getelementptr float, float* %321, i64 %407
  %409 = load float, float* %408, align 4
  %410 = add i32 %405, 2
  %411 = sext i32 %410 to i64
  %412 = getelementptr float, float* %321, i64 %411
  %413 = load float, float* %412, align 4
  %414 = fsub reassoc ninf nsz float %277, %409
  %415 = fsub reassoc ninf nsz float %281, %413
  %416 = fmul reassoc ninf nsz float %414, %414
  %417 = fmul reassoc ninf nsz float %415, %415
  %418 = fadd reassoc ninf nsz float %417, %416
  %419 = fmul reassoc ninf nsz float %418, 2.500000e-01
  %420 = fadd reassoc ninf nsz float %419, %402
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.043 = phi float [ %420, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %421 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %422 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %421, i64 0, i32 14
  %423 = load i8*, i8** %422, align 8
  %424 = getelementptr inbounds i8, i8* %423, i64 16
  %425 = bitcast i8* %424 to float*
  %426 = load float, float* %425, align 4
  %427 = fcmp reassoc ninf nsz ugt float %.043, %426
  br i1 %427, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.043
  %428 = getelementptr inbounds i8, i8* %423, i64 20
  %429 = bitcast i8* %428 to float*
  %430 = load float, float* %429, align 4
  %431 = fmul reassoc ninf nsz float %430, %neg44
  %432 = tail call float @expf(float noundef %431) #1
  %433 = fadd reassoc ninf nsz float %432, %.36288
  %434 = load float*, float** %25, align 8
  %435 = load i32, i32* %26, align 4
  %436 = load i32, i32* %27, align 4
  %437 = mul i32 %lsr.iv143, %435
  %438 = add i32 %317, %437
  %439 = mul i32 %438, %436
  %440 = sext i32 %439 to i64
  %441 = getelementptr float, float* %434, i64 %440
  %442 = load float, float* %441, align 4
  %443 = fmul reassoc ninf nsz float %442, %432
  %444 = fadd reassoc ninf nsz float %443, %.35889
  %445 = add i32 %439, 1
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, float* %434, i64 %446
  %448 = load float, float* %447, align 4
  %449 = fmul reassoc ninf nsz float %448, %432
  %450 = fadd reassoc ninf nsz float %449, %.35490
  %451 = add i32 %439, 2
  %452 = sext i32 %451 to i64
  %453 = getelementptr float, float* %434, i64 %452
  %454 = load float, float* %453, align 4
  %455 = fmul reassoc ninf nsz float %454, %432
  %456 = fadd reassoc ninf nsz float %455, %.391
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %457 = fmul reassoc ninf nsz float %302, %23
  %458 = fdiv reassoc ninf nsz float 1.000000e+00, %.059
  %459 = fmul reassoc ninf nsz float %.055, %458
  %460 = fmul reassoc ninf nsz float %.051, %458
  %461 = fmul reassoc ninf nsz float %.048, %458
  %462 = load float*, float** %25, align 8
  %463 = load i32, i32* %26, align 4
  %464 = load i32, i32* %27, align 4
  %465 = mul i32 %463, %59
  %466 = add i32 %465, %77
  %467 = mul i32 %466, %464
  %468 = sext i32 %467 to i64
  %469 = getelementptr float, float* %462, i64 %468
  %470 = load float, float* %469, align 4
  %471 = fsub reassoc ninf nsz float %470, %459
  %472 = add i32 %467, 1
  %473 = sext i32 %472 to i64
  %474 = getelementptr float, float* %462, i64 %473
  %475 = load float, float* %474, align 4
  %476 = fsub reassoc ninf nsz float %475, %460
  %477 = add i32 %467, 2
  %478 = sext i32 %477 to i64
  %479 = getelementptr float, float* %462, i64 %478
  %480 = load float, float* %479, align 4
  %481 = fsub reassoc ninf nsz float %480, %461
  %482 = tail call float @llvm.fabs.f32(float %471)
  %483 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %484 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %483, i64 0, i32 14
  %485 = load i8*, i8** %484, align 8
  %486 = getelementptr inbounds i8, i8* %485, i64 24
  %487 = bitcast i8* %486 to float*
  %488 = load float, float* %487, align 4
  %489 = fsub reassoc ninf nsz float %482, %488
  %490 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %489, float 0.000000e+00)
  %491 = fcmp reassoc ninf nsz oge float %471, 0.000000e+00
  %492 = uitofp i1 %491 to float
  %493 = fcmp reassoc ninf nsz ole float %471, 0.000000e+00
  %494 = uitofp i1 %493 to float
  %495 = fsub reassoc ninf nsz float %492, %494
  %496 = tail call float @llvm.fabs.f32(float %476)
  %497 = fsub reassoc ninf nsz float %496, %488
  %498 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %497, float 0.000000e+00)
  %499 = fcmp reassoc ninf nsz oge float %476, 0.000000e+00
  %500 = uitofp i1 %499 to float
  %501 = fcmp reassoc ninf nsz ole float %476, 0.000000e+00
  %502 = uitofp i1 %501 to float
  %503 = fsub reassoc ninf nsz float %500, %502
  %504 = tail call float @llvm.fabs.f32(float %481)
  %505 = fsub reassoc ninf nsz float %504, %488
  %506 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %505, float 0.000000e+00)
  %507 = fcmp reassoc ninf nsz oge float %481, 0.000000e+00
  %508 = uitofp i1 %507 to float
  %509 = fcmp reassoc ninf nsz ole float %481, 0.000000e+00
  %510 = uitofp i1 %509 to float
  %511 = fsub reassoc ninf nsz float %508, %510
  %512 = fmul reassoc ninf nsz float %495, %457
  %513 = fmul reassoc ninf nsz float %512, %490
  %514 = fadd reassoc ninf nsz float %513, %459
  %515 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %516 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %515, i64 0, i32 2, i32 1
  %517 = load float*, float** %516, align 8
  %518 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %515, i64 0, i32 2, i32 0, i32 1
  %519 = load i32, i32* %518, align 4
  %520 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %515, i64 0, i32 2, i32 0, i32 2
  %521 = load i32, i32* %520, align 4
  %522 = mul i32 %519, %59
  %523 = add i32 %522, %77
  %524 = mul i32 %523, %521
  %525 = sext i32 %524 to i64
  %526 = getelementptr float, float* %517, i64 %525
  store float %514, float* %526, align 4
  %527 = fmul reassoc ninf nsz float %503, %457
  %528 = fmul reassoc ninf nsz float %527, %498
  %529 = fadd reassoc ninf nsz float %528, %460
  %530 = load float*, float** %516, align 8
  %531 = load i32, i32* %518, align 4
  %532 = load i32, i32* %520, align 4
  %533 = mul i32 %531, %59
  %534 = add i32 %533, %77
  %535 = mul i32 %534, %532
  %536 = add i32 %535, 1
  %537 = sext i32 %536 to i64
  %538 = getelementptr float, float* %530, i64 %537
  store float %529, float* %538, align 4
  %539 = fmul reassoc ninf nsz float %511, %457
  %540 = fmul reassoc ninf nsz float %539, %506
  %541 = fadd reassoc ninf nsz float %540, %461
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %542 = load float*, float** %25, align 8
  %543 = load i32, i32* %26, align 4
  %544 = load i32, i32* %27, align 4
  %545 = mul i32 %543, %59
  %546 = add i32 %545, %77
  %547 = mul i32 %546, %544
  %548 = sext i32 %547 to i64
  %549 = getelementptr float, float* %542, i64 %548
  %550 = load float, float* %549, align 4
  %551 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %552 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %551, i64 0, i32 2, i32 1
  %553 = load float*, float** %552, align 8
  %554 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %551, i64 0, i32 2, i32 0, i32 1
  %555 = load i32, i32* %554, align 4
  %556 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %551, i64 0, i32 2, i32 0, i32 2
  %557 = load i32, i32* %556, align 4
  %558 = mul i32 %555, %59
  %559 = add i32 %558, %77
  %560 = mul i32 %559, %557
  %561 = sext i32 %560 to i64
  %562 = getelementptr float, float* %553, i64 %561
  store float %550, float* %562, align 4
  %563 = load float*, float** %25, align 8
  %564 = load i32, i32* %26, align 4
  %565 = load i32, i32* %27, align 4
  %566 = mul i32 %564, %59
  %567 = add i32 %566, %77
  %568 = mul i32 %567, %565
  %569 = add i32 %568, 1
  %570 = sext i32 %569 to i64
  %571 = getelementptr float, float* %563, i64 %570
  %572 = load float, float* %571, align 4
  %573 = load float*, float** %552, align 8
  %574 = load i32, i32* %554, align 4
  %575 = load i32, i32* %556, align 4
  %576 = mul i32 %574, %59
  %577 = add i32 %576, %77
  %578 = mul i32 %577, %575
  %579 = add i32 %578, 1
  %580 = sext i32 %579 to i64
  %581 = getelementptr float, float* %573, i64 %580
  store float %572, float* %581, align 4
  %582 = load float*, float** %25, align 8
  %583 = load i32, i32* %26, align 4
  %584 = load i32, i32* %27, align 4
  %585 = mul i32 %583, %59
  %586 = add i32 %585, %77
  %587 = mul i32 %586, %584
  %588 = add i32 %587, 2
  %589 = sext i32 %588 to i64
  %590 = getelementptr float, float* %582, i64 %589
  %591 = load float, float* %590, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink114 = phi float** [ %552, %false_block46 ], [ %516, %true_block45 ]
  %.sink113 = phi i32* [ %554, %false_block46 ], [ %518, %true_block45 ]
  %.sink112 = phi i32* [ %556, %false_block46 ], [ %520, %true_block45 ]
  %.sink = phi float [ %591, %false_block46 ], [ %541, %true_block45 ]
  %592 = load float*, float** %.sink114, align 8
  %593 = load i32, i32* %.sink113, align 4
  %594 = load i32, i32* %.sink112, align 4
  %595 = mul i32 %593, %59
  %596 = add i32 %595, %77
  %597 = mul i32 %596, %594
  %598 = add i32 %597, 2
  %599 = sext i32 %598 to i64
  %600 = getelementptr float, float* %592, i64 %599
  store float %.sink, float* %600, align 4
  %601 = add nsw i32 %.06998, 1
  %lsr.iv.next138 = add i32 %lsr.iv137, 1
  %lsr.iv.next140 = add i32 %lsr.iv139, 1
  %lsr.iv.next142 = add i32 %lsr.iv141, 1
  %exitcond102.not = icmp eq i32 %601, %19
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
  %4 = alloca %struct.RuntimeContext.60, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.60**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.60*, %struct.RuntimeContext.60** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.60* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.60* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
