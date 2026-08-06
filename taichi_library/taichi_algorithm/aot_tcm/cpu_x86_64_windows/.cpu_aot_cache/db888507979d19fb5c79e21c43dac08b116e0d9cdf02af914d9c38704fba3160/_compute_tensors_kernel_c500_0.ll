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

@switch.table.function_body.13 = private unnamed_addr constant [5 x float] [float 0x3FC1EB8520000000, float 0x3FC1EB8520000000, float 0x3FDC9EECC0000000, float 0x3FDC9EECC0000000, float 0x3FDC9EECC0000000], align 4

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_compute_tensors_kernel_c500_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 4
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 5
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 8
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_compute_tensors_kernel_c500_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nosync nounwind
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2, i32 1
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2, i32 0, i32 1
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2, i32 0, i32 2
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 2
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 2
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3, i32 1
  %33 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3, i32 0, i32 1
  %34 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3, i32 0, i32 2
  %35 = sub i32 -1, %17
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if18, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %35, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if18 ]
  %.01038 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %351, %after_if18 ]
  %36 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %37 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %36, i64 0, i32 14
  %38 = load i8*, i8** %37, align 8
  %39 = getelementptr inbounds i8, i8* %38, i64 4
  %40 = bitcast i8* %39 to i32*
  %41 = load i32, i32* %40, align 4
  %42 = sdiv i32 %.01038, %41
  %43 = mul i32 %42, %41
  %44 = xor i32 %41, %.01038
  %45 = icmp slt i32 %44, 0
  %46 = icmp ne i32 %.01038, 0
  %47 = icmp ne i32 %.01038, %43
  %48 = and i1 %46, %45
  %49 = and i1 %48, %47
  %.neg13 = sext i1 %49 to i32
  %50 = add i32 %42, %.neg13
  %51 = mul i32 %50, %41
  %52 = mul i32 %41, -1
  %53 = mul i32 %52, %50
  %54 = add i32 %.01038, %53
  %55 = load float*, float** %23, align 8
  %56 = load i32, i32* %24, align 4
  %57 = load i32, i32* %25, align 4
  %58 = sub i32 %56, %41
  %59 = mul i32 %58, %50
  %60 = add i32 %.01038, %59
  %61 = mul i32 %60, %57
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, float* %55, i64 %62
  %64 = load float, float* %63, align 4
  %65 = add i32 %61, 1
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, float* %55, i64 %66
  %68 = load float, float* %67, align 4
  %69 = sitofp i32 %54 to float
  %70 = fadd reassoc ninf nsz float %64, %69
  %71 = sitofp i32 %50 to float
  %72 = fadd reassoc ninf nsz float %68, %71
  %73 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %74 = fptosi float %73 to i32
  %75 = tail call reassoc ninf nsz float @llvm.floor.f32(float %72)
  %76 = fptosi float %75 to i32
  %77 = sitofp i32 %74 to float
  %78 = fsub reassoc ninf nsz float %70, %77
  %79 = sitofp i32 %76 to float
  %80 = fsub reassoc ninf nsz float %72, %79
  %81 = getelementptr inbounds i8, i8* %38, i64 8
  %82 = bitcast i8* %81 to i32*
  %83 = load i32, i32* %82, align 4
  %84 = add i32 %83, -1
  %85 = getelementptr inbounds i8, i8* %38, i64 12
  %86 = bitcast i8* %85 to i32*
  %87 = load i32, i32* %86, align 4
  %88 = add i32 %87, -1
  %89 = add i32 %74, 1
  %90 = add i32 %76, 1
  %91 = fsub reassoc ninf nsz float 1.000000e+00, %78
  %92 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %93 = fmul reassoc ninf nsz float %91, %92
  %94 = fmul reassoc ninf nsz float %78, %92
  %95 = fmul reassoc ninf nsz float %91, %80
  %96 = fmul reassoc ninf nsz float %78, %80
  %97 = load float*, float** %26, align 8
  %98 = load i32, i32* %27, align 4
  %99 = load i32, i32* %28, align 4
  %100 = insertelement <2 x i32> poison, i32 %74, i64 0
  %101 = insertelement <2 x i32> %100, i32 %89, i64 1
  %102 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %101, i1 true)
  %103 = insertelement <2 x i32> poison, i32 %84, i64 0
  %104 = shufflevector <2 x i32> %103, <2 x i32> poison, <2 x i32> zeroinitializer
  %105 = sub <2 x i32> %102, %104
  %106 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %105, <2 x i32> zeroinitializer)
  %107 = mul <2 x i32> %106, <i32 -2, i32 -2>
  %108 = add <2 x i32> %107, %102
  %109 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %108, <2 x i32> zeroinitializer)
  %110 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %104, <2 x i32> %109)
  %shuffle43 = shufflevector <2 x i32> %110, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %111 = insertelement <2 x i32> poison, i32 %76, i64 0
  %112 = insertelement <2 x i32> %111, i32 %90, i64 1
  %113 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %112, i1 true)
  %114 = insertelement <2 x i32> poison, i32 %88, i64 0
  %115 = shufflevector <2 x i32> %114, <2 x i32> poison, <2 x i32> zeroinitializer
  %116 = sub <2 x i32> %113, %115
  %117 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %116, <2 x i32> zeroinitializer)
  %118 = mul <2 x i32> %117, <i32 -2, i32 -2>
  %119 = add <2 x i32> %118, %113
  %120 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %119, <2 x i32> zeroinitializer)
  %121 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %115, <2 x i32> %120)
  %122 = insertelement <2 x i32> poison, i32 %98, i64 0
  %123 = shufflevector <2 x i32> %122, <2 x i32> poison, <2 x i32> zeroinitializer
  %124 = mul <2 x i32> %121, %123
  %shuffle = shufflevector <2 x i32> %124, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %125 = add <4 x i32> %shuffle, %shuffle43
  %126 = insertelement <4 x i32> poison, i32 %99, i64 0
  %shuffle44 = shufflevector <4 x i32> %126, <4 x i32> poison, <4 x i32> zeroinitializer
  %127 = mul <4 x i32> %125, %shuffle44
  %128 = sext <4 x i32> %127 to <4 x i64>
  %129 = extractelement <4 x i64> %128, i64 0
  %130 = getelementptr float, float* %97, i64 %129
  %131 = load float, float* %130, align 4
  %132 = extractelement <4 x i64> %128, i64 1
  %133 = getelementptr float, float* %97, i64 %132
  %134 = load float, float* %133, align 4
  %135 = extractelement <4 x i64> %128, i64 2
  %136 = getelementptr float, float* %97, i64 %135
  %137 = load float, float* %136, align 4
  %138 = extractelement <4 x i64> %128, i64 3
  %139 = getelementptr float, float* %97, i64 %138
  %140 = load float, float* %139, align 4
  %141 = add <4 x i32> %127, <i32 1, i32 1, i32 1, i32 1>
  %142 = extractelement <4 x i32> %141, i64 0
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %97, i64 %143
  %145 = load float, float* %144, align 4
  %146 = extractelement <4 x i32> %141, i64 1
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %97, i64 %147
  %149 = load float, float* %148, align 4
  %150 = extractelement <4 x i32> %141, i64 2
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %97, i64 %151
  %153 = load float, float* %152, align 4
  %154 = extractelement <4 x i32> %141, i64 3
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %97, i64 %155
  %157 = load float, float* %156, align 4
  %158 = shufflevector <4 x i32> %127, <4 x i32> undef, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 0, i32 1, i32 2, i32 3>
  %159 = add <8 x i32> %158, <i32 2, i32 2, i32 2, i32 2, i32 3, i32 3, i32 3, i32 3>
  %160 = extractelement <8 x i32> %159, i64 0
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %97, i64 %161
  %163 = load float, float* %162, align 4
  %164 = fmul reassoc ninf nsz float %163, %93
  %165 = extractelement <8 x i32> %159, i64 1
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, float* %97, i64 %166
  %168 = load float, float* %167, align 4
  %169 = fmul reassoc ninf nsz float %168, %94
  %170 = fadd reassoc ninf nsz float %169, %164
  %171 = extractelement <8 x i32> %159, i64 2
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %97, i64 %172
  %174 = load float, float* %173, align 4
  %175 = fmul reassoc ninf nsz float %174, %95
  %176 = fadd reassoc ninf nsz float %170, %175
  %177 = extractelement <8 x i32> %159, i64 3
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %97, i64 %178
  %180 = load float, float* %179, align 4
  %181 = fmul reassoc ninf nsz float %180, %96
  %182 = fadd reassoc ninf nsz float %176, %181
  %183 = extractelement <8 x i32> %159, i64 4
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, float* %97, i64 %184
  %186 = load float, float* %185, align 4
  %187 = fmul reassoc ninf nsz float %186, %93
  %188 = extractelement <8 x i32> %159, i64 5
  %189 = sext i32 %188 to i64
  %190 = getelementptr float, float* %97, i64 %189
  %191 = load float, float* %190, align 4
  %192 = fmul reassoc ninf nsz float %191, %94
  %193 = fadd reassoc ninf nsz float %192, %187
  %194 = extractelement <8 x i32> %159, i64 6
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, float* %97, i64 %195
  %197 = load float, float* %196, align 4
  %198 = fmul reassoc ninf nsz float %197, %95
  %199 = fadd reassoc ninf nsz float %193, %198
  %200 = extractelement <8 x i32> %159, i64 7
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, float* %97, i64 %201
  %203 = load float, float* %202, align 4
  %204 = fmul reassoc ninf nsz float %203, %96
  %205 = fadd reassoc ninf nsz float %199, %204
  %206 = add <4 x i32> %127, <i32 4, i32 4, i32 4, i32 4>
  %207 = extractelement <4 x i32> %206, i64 0
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, float* %97, i64 %208
  %210 = load float, float* %209, align 4
  %211 = fmul reassoc ninf nsz float %210, %93
  %212 = extractelement <4 x i32> %206, i64 1
  %213 = sext i32 %212 to i64
  %214 = getelementptr float, float* %97, i64 %213
  %215 = load float, float* %214, align 4
  %216 = fmul reassoc ninf nsz float %215, %94
  %217 = fadd reassoc ninf nsz float %216, %211
  %218 = extractelement <4 x i32> %206, i64 2
  %219 = sext i32 %218 to i64
  %220 = getelementptr float, float* %97, i64 %219
  %221 = load float, float* %220, align 4
  %222 = fmul reassoc ninf nsz float %221, %95
  %223 = fadd reassoc ninf nsz float %217, %222
  %224 = extractelement <4 x i32> %206, i64 3
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, float* %97, i64 %225
  %227 = load float, float* %226, align 4
  %228 = fmul reassoc ninf nsz float %227, %96
  %229 = fadd reassoc ninf nsz float %223, %228
  %230 = load float*, float** %29, align 8
  %231 = load i32, i32* %30, align 4
  %232 = load i32, i32* %31, align 4
  %233 = sub i32 %231, %41
  %234 = mul i32 %233, %50
  %235 = add i32 %.01038, %234
  %236 = mul i32 %235, %232
  %237 = add i32 %236, 2
  %238 = sext i32 %237 to i64
  %239 = getelementptr float, float* %230, i64 %238
  %240 = load float, float* %239, align 4
  %241 = fadd reassoc ninf nsz float %182, %240
  %242 = fmul reassoc ninf nsz float %241, 5.000000e-01
  %243 = add i32 %236, 3
  %244 = sext i32 %243 to i64
  %245 = getelementptr float, float* %230, i64 %244
  %246 = load float, float* %245, align 4
  %247 = fadd reassoc ninf nsz float %205, %246
  %248 = fmul reassoc ninf nsz float %247, 5.000000e-01
  %249 = add i32 %236, 4
  %250 = sext i32 %249 to i64
  %251 = getelementptr float, float* %230, i64 %250
  %252 = load float, float* %251, align 4
  %253 = fadd reassoc ninf nsz float %229, %252
  %254 = fmul reassoc ninf nsz float %253, 2.500000e-01
  %255 = sext i32 %236 to i64
  %256 = getelementptr float, float* %230, i64 %255
  %257 = load float, float* %256, align 4
  %.neg18 = fmul reassoc ninf nsz float %140, %96
  %.neg19 = fmul reassoc ninf nsz float %95, %137
  %.neg20 = fmul reassoc ninf nsz float %94, %134
  %.neg21 = fmul reassoc ninf nsz float %93, %131
  %reass.add = fadd reassoc ninf nsz float %.neg20, %.neg18
  %reass.add32 = fadd reassoc ninf nsz float %reass.add, %.neg21
  %reass.add33 = fadd reassoc ninf nsz float %reass.add32, %.neg19
  %258 = fsub reassoc ninf nsz float %257, %reass.add33
  %259 = fmul reassoc ninf nsz float %258, 5.000000e-01
  %260 = add i32 %236, 1
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, float* %230, i64 %261
  %263 = load float, float* %262, align 4
  %.neg25 = fmul reassoc ninf nsz float %145, %93
  %.neg26 = fmul reassoc ninf nsz float %149, %94
  %.neg28 = fmul reassoc ninf nsz float %153, %95
  %.neg30 = fmul reassoc ninf nsz float %157, %96
  %reass.add34 = fadd reassoc ninf nsz float %.neg26, %.neg25
  %reass.add35 = fadd reassoc ninf nsz float %reass.add34, %.neg28
  %reass.add36 = fadd reassoc ninf nsz float %reass.add35, %.neg30
  %264 = fsub reassoc ninf nsz float %263, %reass.add36
  %265 = fmul reassoc ninf nsz float %264, 5.000000e-01
  %266 = fmul reassoc ninf nsz float %242, %68
  %267 = fmul reassoc ninf nsz float %254, %64
  %268 = fadd reassoc ninf nsz float %267, %266
  %269 = fadd reassoc ninf nsz float %268, %259
  %270 = fmul reassoc ninf nsz float %254, %68
  %271 = fmul reassoc ninf nsz float %248, %64
  %272 = fadd reassoc ninf nsz float %270, %271
  %273 = fadd reassoc ninf nsz float %272, %265
  %274 = sub i32 %88, %50
  %275 = tail call i32 @llvm.smin.i32(i32 %50, i32 %274)
  %276 = add i32 %83, %51
  %277 = add i32 %lsr.iv, %276
  %278 = tail call i32 @llvm.smin.i32(i32 %54, i32 %277)
  %279 = icmp ult i32 %275, 5
  br i1 %279, label %switch.lookup, label %after_if

after_for.loopexit:                               ; preds = %after_if18
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

switch.lookup:                                    ; preds = %for_loop_body
  %280 = sext i32 %275 to i64
  %switch.gep = getelementptr inbounds [5 x float], [5 x float]* @switch.table.function_body.13, i64 0, i64 %280
  %switch.load = load float, float* %switch.gep, align 4
  br label %after_if

after_if:                                         ; preds = %switch.lookup, %for_loop_body
  %.09 = phi float [ 1.000000e+00, %for_loop_body ], [ %switch.load, %switch.lookup ]
  %281 = icmp ult i32 %278, 5
  br i1 %281, label %switch.lookup39, label %after_if18

switch.lookup39:                                  ; preds = %after_if
  %282 = sext i32 %278 to i64
  %switch.gep40 = getelementptr inbounds [5 x float], [5 x float]* @switch.table.function_body.13, i64 0, i64 %282
  %switch.load41 = load float, float* %switch.gep40, align 4
  br label %after_if18

after_if18:                                       ; preds = %switch.lookup39, %after_if
  %.08 = phi float [ 1.000000e+00, %after_if ], [ %switch.load41, %switch.lookup39 ]
  %283 = fmul reassoc ninf nsz float %.08, %.09
  %284 = fmul reassoc ninf nsz float %283, %269
  %285 = fmul reassoc ninf nsz float %283, %273
  %286 = fmul reassoc ninf nsz float %283, %242
  %287 = fmul reassoc ninf nsz float %283, %248
  %288 = fmul reassoc ninf nsz float %283, %254
  %289 = fmul reassoc ninf nsz float %286, %286
  %290 = fmul reassoc ninf nsz float %288, %288
  %291 = fadd reassoc ninf nsz float %289, %290
  %292 = load float*, float** %32, align 8
  %293 = load i32, i32* %33, align 4
  %294 = load i32, i32* %34, align 4
  %295 = sub i32 %293, %41
  %296 = mul i32 %295, %50
  %297 = add i32 %.01038, %296
  %298 = mul i32 %297, %294
  %299 = sext i32 %298 to i64
  %300 = getelementptr float, float* %292, i64 %299
  store float %291, float* %300, align 4
  %301 = fadd reassoc ninf nsz float %286, %287
  %302 = fmul reassoc ninf nsz float %301, %288
  %303 = load float*, float** %32, align 8
  %304 = load i32, i32* %33, align 4
  %305 = load i32, i32* %34, align 4
  %306 = sub i32 %304, %41
  %307 = mul i32 %306, %50
  %308 = add i32 %.01038, %307
  %309 = mul i32 %308, %305
  %310 = add i32 %309, 1
  %311 = sext i32 %310 to i64
  %312 = getelementptr float, float* %303, i64 %311
  store float %302, float* %312, align 4
  %313 = fmul reassoc ninf nsz float %287, %287
  %314 = fadd reassoc ninf nsz float %313, %290
  %315 = load float*, float** %32, align 8
  %316 = load i32, i32* %33, align 4
  %317 = load i32, i32* %34, align 4
  %318 = sub i32 %316, %41
  %319 = mul i32 %318, %50
  %320 = add i32 %.01038, %319
  %321 = mul i32 %320, %317
  %322 = add i32 %321, 2
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, float* %315, i64 %323
  store float %314, float* %324, align 4
  %325 = fmul reassoc ninf nsz float %286, %284
  %326 = fmul reassoc ninf nsz float %288, %285
  %327 = fadd reassoc ninf nsz float %325, %326
  %328 = load float*, float** %32, align 8
  %329 = load i32, i32* %33, align 4
  %330 = load i32, i32* %34, align 4
  %331 = sub i32 %329, %41
  %332 = mul i32 %331, %50
  %333 = add i32 %.01038, %332
  %334 = mul i32 %333, %330
  %335 = add i32 %334, 3
  %336 = sext i32 %335 to i64
  %337 = getelementptr float, float* %328, i64 %336
  store float %327, float* %337, align 4
  %338 = fmul reassoc ninf nsz float %288, %284
  %339 = fmul reassoc ninf nsz float %287, %285
  %340 = fadd reassoc ninf nsz float %338, %339
  %341 = load float*, float** %32, align 8
  %342 = load i32, i32* %33, align 4
  %343 = load i32, i32* %34, align 4
  %344 = sub i32 %342, %41
  %345 = mul i32 %344, %50
  %346 = add i32 %.01038, %345
  %347 = mul i32 %346, %343
  %348 = add i32 %347, 4
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, float* %341, i64 %349
  store float %340, float* %350, align 4
  %351 = add nsw i32 %.01038, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %19, %351
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
