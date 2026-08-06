; ModuleID = '<string>'
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
define void @_gbtf_green_interpolation_kernel_c82_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
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
define void @_gbtf_green_interpolation_kernel_c82_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %21 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if12, %for_loop_body.lr.ph
  %.01019 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %174, %after_if12 ]
  %22 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  %27 = load i32, i32* %26, align 4
  %28 = sdiv i32 %.01019, %27
  %29 = mul i32 %28, %27
  %30 = xor i32 %27, %.01019
  %31 = icmp slt i32 %30, 0
  %32 = icmp ne i32 %.01019, 0
  %33 = icmp ne i32 %.01019, %29
  %34 = and i1 %32, %31
  %35 = and i1 %34, %33
  %.neg12 = sext i1 %35 to i32
  %36 = add i32 %28, %.neg12
  %37 = mul i32 %27, -1
  %38 = mul i32 %37, %36
  %39 = add i32 %.01019, %38
  %40 = insertelement <2 x i32> poison, i32 %39, i64 0
  %41 = insertelement <2 x i32> %40, i32 %36, i64 1
  %42 = sdiv <2 x i32> %41, <i32 2, i32 2>
  %43 = icmp slt <2 x i32> %41, zeroinitializer
  %44 = shl nsw <2 x i32> %42, <i32 1, i32 1>
  %45 = icmp ne <2 x i32> %44, %41
  %46 = and <2 x i1> %43, %45
  %47 = zext <2 x i1> %46 to <2 x i32>
  %48 = sub nsw <2 x i32> %47, %42
  %49 = shl <2 x i32> %48, <i32 1, i32 1>
  %50 = sub <2 x i32> zeroinitializer, %41
  %51 = icmp eq <2 x i32> %49, %50
  %52 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %53 = extractelement <2 x i1> %51, i64 1
  br i1 %53, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if12
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %54 = extractelement <2 x i1> %51, i64 0
  br i1 %54, label %true_block1, label %false_block2

false_block:                                      ; preds = %for_loop_body
  %55 = extractelement <2 x i1> %51, i64 0
  br i1 %55, label %true_block4, label %false_block5

after_if:                                         ; preds = %false_block5, %true_block4, %false_block2, %true_block1
  %.09.in = phi i32* [ %56, %true_block1 ], [ %57, %false_block2 ], [ %58, %true_block4 ], [ %59, %false_block5 ]
  %.09 = load i32, i32* %.09.in, align 4
  switch i32 %.09, label %false_block11 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

true_block1:                                      ; preds = %true_block
  %56 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 4
  br label %after_if

false_block2:                                     ; preds = %true_block
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 5
  br label %after_if

true_block4:                                      ; preds = %false_block
  %58 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 6
  br label %after_if

false_block5:                                     ; preds = %false_block
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 7
  br label %after_if

true_block10:                                     ; preds = %after_if, %after_if
  %60 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 0, i32 1
  %61 = load float*, float** %60, align 8
  %62 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 0, i32 0, i32 1
  %63 = load i32, i32* %62, align 4
  %64 = sub i32 %63, %27
  %65 = mul i32 %64, %36
  %66 = add i32 %.01019, %65
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, float* %61, i64 %67
  %69 = load float, float* %68, align 4
  br label %after_if12

false_block11:                                    ; preds = %after_if
  %70 = insertelement <2 x i32> poison, i32 %36, i64 0
  %71 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %72 = add <2 x i32> %71, <i32 -3, i32 3>
  %73 = getelementptr inbounds i8, i8* %24, i64 8
  %74 = bitcast i8* %73 to i32*
  %75 = load i32, i32* %74, align 4
  %76 = add i32 %75, -1
  %77 = add <2 x i32> %71, <i32 -2, i32 2>
  %78 = add <2 x i32> %71, <i32 -1, i32 1>
  %79 = shufflevector <2 x i32> %40, <2 x i32> poison, <2 x i32> zeroinitializer
  %80 = add <2 x i32> %79, <i32 3, i32 -3>
  %81 = getelementptr inbounds i8, i8* %24, i64 12
  %82 = bitcast i8* %81 to i32*
  %83 = load i32, i32* %82, align 4
  %84 = add i32 %83, -1
  %85 = add <2 x i32> %79, <i32 2, i32 -2>
  %86 = add <2 x i32> %79, <i32 1, i32 -1>
  %87 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %86, <2 x i32> zeroinitializer)
  %88 = insertelement <2 x i32> poison, i32 %84, i64 0
  %89 = shufflevector <2 x i32> %88, <2 x i32> poison, <2 x i32> zeroinitializer
  %90 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %87)
  %91 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %85, <2 x i32> zeroinitializer)
  %92 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %91)
  %93 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %80, <2 x i32> zeroinitializer)
  %94 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %93)
  %95 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 0, i32 1
  %96 = load float*, float** %95, align 8
  %97 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 0, i32 0, i32 1
  %98 = load i32, i32* %97, align 4
  %99 = mul i32 %98, %36
  %100 = sub i32 %98, %27
  %101 = mul i32 %100, %36
  %102 = add i32 %.01019, %101
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %96, i64 %103
  %105 = load float, float* %104, align 4
  %106 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %78, <2 x i32> zeroinitializer)
  %107 = insertelement <2 x i32> poison, i32 %76, i64 0
  %108 = shufflevector <2 x i32> %107, <2 x i32> poison, <2 x i32> zeroinitializer
  %109 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %108, <2 x i32> %106)
  %110 = insertelement <2 x i32> poison, i32 %98, i64 0
  %111 = shufflevector <2 x i32> %110, <2 x i32> poison, <2 x i32> zeroinitializer
  %112 = mul <2 x i32> %111, %109
  %113 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %72, <2 x i32> zeroinitializer)
  %114 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %108, <2 x i32> %113)
  %115 = mul <2 x i32> %111, %114
  %116 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %77, <2 x i32> zeroinitializer)
  %117 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %108, <2 x i32> %116)
  %118 = mul <2 x i32> %111, %117
  %119 = insertelement <4 x i32> poison, i32 %99, i64 0
  %120 = shufflevector <4 x i32> %119, <4 x i32> poison, <4 x i32> <i32 0, i32 0, i32 undef, i32 undef>
  %121 = shufflevector <2 x i32> %112, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %122 = shufflevector <4 x i32> %120, <4 x i32> %121, <4 x i32> <i32 0, i32 1, i32 4, i32 5>
  %123 = shufflevector <2 x i32> %90, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %124 = insertelement <4 x i32> %123, i32 %39, i64 2
  %125 = insertelement <4 x i32> %124, i32 %39, i64 3
  %126 = add <4 x i32> %122, %125
  %127 = sext <4 x i32> %126 to <4 x i64>
  %128 = insertelement <4 x float*> poison, float* %96, i64 0
  %shuffle = shufflevector <4 x float*> %128, <4 x float*> poison, <4 x i32> zeroinitializer
  %129 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %127
  %130 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %129, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %131 = shufflevector <2 x i32> %115, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %132 = shufflevector <4 x i32> %120, <4 x i32> %131, <4 x i32> <i32 0, i32 1, i32 4, i32 5>
  %133 = shufflevector <2 x i32> %94, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %134 = insertelement <4 x i32> %133, i32 %39, i64 2
  %135 = insertelement <4 x i32> %134, i32 %39, i64 3
  %136 = add <4 x i32> %132, %135
  %137 = sext <4 x i32> %136 to <4 x i64>
  %138 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %137
  %139 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %138, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %140 = fsub reassoc ninf nsz <4 x float> %130, %139
  %141 = call <4 x float> @llvm.fabs.v4f32(<4 x float> %140)
  %142 = shufflevector <2 x i32> %118, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %143 = shufflevector <4 x i32> %120, <4 x i32> %142, <4 x i32> <i32 0, i32 1, i32 4, i32 5>
  %144 = shufflevector <2 x i32> %92, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 undef, i32 undef>
  %145 = insertelement <4 x i32> %144, i32 %39, i64 2
  %146 = insertelement <4 x i32> %145, i32 %39, i64 3
  %147 = add <4 x i32> %143, %146
  %148 = sext <4 x i32> %147 to <4 x i64>
  %149 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %148
  %150 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %149, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %151 = insertelement <4 x float> poison, float %105, i64 0
  %shuffle29 = shufflevector <4 x float> %151, <4 x float> poison, <4 x i32> zeroinitializer
  %152 = fsub reassoc ninf nsz <4 x float> %shuffle29, %150
  %153 = call <4 x float> @llvm.fabs.v4f32(<4 x float> %152)
  %154 = fadd reassoc ninf nsz <4 x float> %141, <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>
  %155 = fadd reassoc ninf nsz <4 x float> %154, %153
  %156 = fmul reassoc ninf nsz <4 x float> %155, %155
  %157 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %156, <4 x float> <float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000, float 0x3EE4F8B580000000>)
  %158 = fdiv reassoc ninf nsz <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %157
  %159 = fmul reassoc ninf nsz <4 x float> %152, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %160 = fadd reassoc ninf nsz <4 x float> %159, %130
  %161 = fmul reassoc ninf nsz <4 x float> %158, %160
  %162 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %161)
  %163 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %158)
  %164 = fdiv reassoc ninf nsz float %162, %163
  br label %after_if12

after_if12:                                       ; preds = %false_block11, %true_block10
  %.sink = phi float [ %164, %false_block11 ], [ %69, %true_block10 ]
  %165 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 1, i32 1
  %166 = load float*, float** %165, align 8
  %167 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %52, i64 0, i32 1, i32 0, i32 1
  %168 = load i32, i32* %167, align 4
  %169 = sub i32 %168, %27
  %170 = mul i32 %169, %36
  %171 = add i32 %.01019, %170
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %166, i64 %172
  store float %.sink, float* %173, align 4
  %174 = add nsw i32 %.01019, 1
  %exitcond.not = icmp eq i32 %19, %174
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

; Function Attrs: argmemonly nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.fabs.v4f32(<4 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.maxnum.v4f32(<4 x float>, <4 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #5

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly nocallback nofree nounwind willreturn }
attributes #5 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone willreturn }

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
