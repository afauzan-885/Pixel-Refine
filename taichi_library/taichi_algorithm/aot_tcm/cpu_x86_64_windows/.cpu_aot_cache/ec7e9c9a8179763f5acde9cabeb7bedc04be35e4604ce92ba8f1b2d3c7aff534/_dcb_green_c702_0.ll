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
define void @_dcb_green_c702_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
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
define void @_dcb_green_c702_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %29 = load i32, i32* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if12, %for_loop_body.preheader
  %.0919 = phi i32 [ %133, %after_if12 ], [ %17, %for_loop_body.preheader ]
  %31 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.0919, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.0919
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.0919, 0
  %42 = icmp ne i32 %.0919, %38
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg11 = sext i1 %44 to i32
  %45 = add i32 %37, %.neg11
  %46 = mul i32 %36, -1
  %47 = mul i32 %46, %45
  %48 = add i32 %.0919, %47
  %49 = insertelement <2 x i32> poison, i32 %48, i64 0
  %50 = insertelement <2 x i32> %49, i32 %45, i64 1
  %51 = sdiv <2 x i32> %50, <i32 2, i32 2>
  %52 = icmp slt <2 x i32> %50, zeroinitializer
  %53 = shl nsw <2 x i32> %51, <i32 1, i32 1>
  %54 = icmp ne <2 x i32> %53, %50
  %55 = and <2 x i1> %52, %54
  %56 = zext <2 x i1> %55 to <2 x i32>
  %57 = sub nsw <2 x i32> %56, %51
  %58 = shl <2 x i32> %57, <i32 1, i32 1>
  %59 = sub <2 x i32> zeroinitializer, %50
  %60 = icmp eq <2 x i32> %58, %59
  %61 = extractelement <2 x i1> %60, i64 0
  %. = select i1 %61, i32 %23, i32 %25
  %.18 = select i1 %61, i32 %27, i32 %29
  %62 = extractelement <2 x i1> %60, i64 1
  %.08 = select i1 %62, i32 %., i32 %.18
  switch i32 %.08, label %false_block11 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

after_for.loopexit:                               ; preds = %after_if12
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block10:                                     ; preds = %for_loop_body, %for_loop_body
  %63 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %64 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %63, i64 0, i32 0, i32 1
  %65 = load float*, float** %64, align 8
  %66 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %63, i64 0, i32 0, i32 0, i32 1
  %67 = load i32, i32* %66, align 4
  %68 = sub i32 %67, %36
  %69 = mul i32 %68, %45
  %70 = add i32 %.0919, %69
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, float* %65, i64 %71
  %73 = load float, float* %72, align 4
  br label %after_if12

false_block11:                                    ; preds = %for_loop_body
  %74 = add i32 %45, -1
  %75 = tail call i32 @llvm.smax.i32(i32 %74, i32 0)
  %76 = getelementptr inbounds i8, i8* %33, i64 8
  %77 = bitcast i8* %76 to i32*
  %78 = load i32, i32* %77, align 4
  %79 = add i32 %78, -1
  %80 = add i32 %45, 1
  %81 = tail call i32 @llvm.smin.i32(i32 %79, i32 %80)
  %82 = add i32 %48, -1
  %83 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %84 = getelementptr inbounds i8, i8* %33, i64 12
  %85 = bitcast i8* %84 to i32*
  %86 = load i32, i32* %85, align 4
  %87 = add i32 %86, -1
  %88 = add i32 %48, 1
  %89 = tail call i32 @llvm.smin.i32(i32 %87, i32 %88)
  %90 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %91 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %90, i64 0, i32 0, i32 1
  %92 = load float*, float** %91, align 8
  %93 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %90, i64 0, i32 0, i32 0, i32 1
  %94 = load i32, i32* %93, align 4
  %95 = mul i32 %94, %81
  %96 = insertelement <2 x i32> poison, i32 %94, i64 0
  %97 = shufflevector <2 x i32> %96, <2 x i32> poison, <2 x i32> zeroinitializer
  %98 = insertelement <2 x i32> poison, i32 %75, i64 0
  %99 = insertelement <2 x i32> %98, i32 %45, i64 1
  %100 = mul <2 x i32> %97, %99
  %101 = insertelement <2 x i32> %49, i32 %83, i64 1
  %102 = add <2 x i32> %100, %101
  %103 = sext <2 x i32> %102 to <2 x i64>
  %104 = insertelement <2 x float*> poison, float* %92, i64 0
  %105 = shufflevector <2 x float*> %104, <2 x float*> poison, <2 x i32> zeroinitializer
  %106 = getelementptr float, <2 x float*> %105, <2 x i64> %103
  %107 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %106, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %108 = insertelement <2 x i32> %100, i32 %95, i64 0
  %109 = insertelement <2 x i32> %49, i32 %89, i64 1
  %110 = add <2 x i32> %108, %109
  %111 = sext <2 x i32> %110 to <2 x i64>
  %112 = getelementptr float, <2 x float*> %105, <2 x i64> %111
  %113 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %112, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %114 = fadd reassoc ninf nsz <2 x float> %113, %107
  %115 = fsub reassoc ninf nsz <2 x float> %107, %113
  %116 = call <2 x float> @llvm.fabs.v2f32(<2 x float> %115)
  %117 = fadd reassoc ninf nsz <2 x float> %116, <float 0x3F1A36E2E0000000, float 0x3F1A36E2E0000000>
  %118 = fdiv reassoc ninf nsz <2 x float> <float 1.000000e+00, float 1.000000e+00>, %117
  %119 = fmul reassoc ninf nsz <2 x float> %118, %114
  %shift = shufflevector <2 x float> %119, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %120 = fadd reassoc ninf nsz <2 x float> %119, %shift
  %reass.add = extractelement <2 x float> %120, i64 0
  %reass.mul = fmul reassoc ninf nsz float %reass.add, 5.000000e-01
  %shift30 = shufflevector <2 x float> %118, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %121 = fadd reassoc ninf nsz <2 x float> %118, %shift30
  %122 = extractelement <2 x float> %121, i64 0
  %123 = fdiv reassoc ninf nsz float %reass.mul, %122
  br label %after_if12

after_if12:                                       ; preds = %false_block11, %true_block10
  %.sink29 = phi { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* [ %90, %false_block11 ], [ %63, %true_block10 ]
  %.sink = phi float [ %123, %false_block11 ], [ %73, %true_block10 ]
  %124 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %.sink29, i64 0, i32 1, i32 1
  %125 = load float*, float** %124, align 8
  %126 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %.sink29, i64 0, i32 1, i32 0, i32 1
  %127 = load i32, i32* %126, align 4
  %128 = sub i32 %127, %36
  %129 = mul i32 %128, %45
  %130 = add i32 %.0919, %129
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, float* %125, i64 %131
  store float %.sink, float* %132, align 4
  %133 = add nsw i32 %.0919, 1
  %exitcond.not = icmp eq i32 %19, %133
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.fabs.v2f32(<2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
