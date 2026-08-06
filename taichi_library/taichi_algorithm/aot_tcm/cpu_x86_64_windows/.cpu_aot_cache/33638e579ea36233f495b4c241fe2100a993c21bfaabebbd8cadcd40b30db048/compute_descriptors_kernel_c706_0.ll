; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.48*, void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.48 = type { i8*, %struct.LLVMRuntime.47*, i32, i64* }
%struct.LLVMRuntime.47 = type { %struct.PreallocatedMemoryChunk.43, %struct.PreallocatedMemoryChunk.43, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.44*], [1024 x %struct.NodeManager.45*], [1024 x i8*], i8*, %struct.RandState.46*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.43 = type { i8*, i8*, i64 }
%struct.ListManager.44 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.47* }
%struct.NodeManager.45 = type { %struct.LLVMRuntime.47*, i32, i32, i32, i32, %struct.ListManager.44*, %struct.ListManager.44*, %struct.ListManager.44*, i32 }
%struct.RandState.46 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @compute_descriptors_kernel_c706_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %1, i64 0, i32 4, i32 1
  %3 = load i32*, i32** %2, align 8
  %4 = load i32, i32* %3, align 4
  %5 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %6 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %6, i64 0, i32 14
  %8 = load i8*, i8** %7, align 8
  %9 = getelementptr inbounds i8, i8* %8, i64 4
  %10 = bitcast i8* %9 to i32*
  store i32 %4, i32* %10, align 4
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %11, i64 0, i32 1, i32 0, i32 0
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %5, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %14, i64 0, i32 14
  %16 = bitcast i8** %15 to i32**
  %17 = load i32*, i32** %16, align 8
  store i32 %13, i32* %17, align 4
  ret void
}

; Function Attrs: nounwind
define void @compute_descriptors_kernel_c706_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.48* %context, %struct.RuntimeContext.48** %4, align 8
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.48*, i8*, i32)* @function_body, void (%struct.RuntimeContext.48*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.48* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = alloca [16 x i32], align 4
  %4 = alloca [4 x float], align 4
  %5 = alloca [4 x float], align 4
  %6 = alloca [4 x float], align 4
  %7 = alloca [9 x float], align 4
  %8 = alloca [9 x float], align 4
  %9 = alloca [9 x float], align 4
  %10 = alloca [16 x float], align 4
  %11 = alloca [16 x float], align 4
  %12 = alloca [16 x float], align 4
  %13 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %0, i64 0, i32 1
  %14 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %13, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %14, i64 0, i32 14
  %16 = bitcast i8** %15 to i32**
  %17 = load i32*, i32** %16, align 8
  %18 = load i32, i32* %17, align 4
  %19 = add i32 %18, 7
  %20 = sdiv i32 %19, 8
  %21 = icmp slt i32 %19, 0
  %22 = shl nsw i32 %20, 3
  %23 = icmp ne i32 %22, %19
  %24 = and i1 %21, %23
  %.neg = sext i1 %24 to i32
  %25 = add nsw i32 %20, %.neg
  %26 = tail call i32 @llvm.smax.i32(i32 %25, i32 512)
  %27 = mul i32 %26, %2
  %28 = add i32 %27, %26
  %29 = tail call i32 @llvm.smin.i32(i32 %18, i32 %28)
  %30 = icmp slt i32 %27, %29
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**
  %32 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 15
  %33 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 14
  %34 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 13
  %35 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 12
  %36 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 11
  %37 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 10
  %38 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 9
  %39 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 8
  %40 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 7
  %41 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 6
  %42 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 5
  %43 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 4
  %44 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 3
  %45 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 2
  %46 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 1
  %47 = getelementptr inbounds [16 x i32], [16 x i32]* %3, i64 0, i64 0
  %48 = bitcast [16 x i32]* %3 to i8*
  %49 = bitcast [4 x float]* %4 to i8*
  %50 = bitcast [4 x float]* %5 to i8*
  %51 = bitcast [4 x float]* %6 to i8*
  %52 = bitcast [9 x float]* %7 to i8*
  %53 = bitcast [9 x float]* %8 to i8*
  %54 = bitcast [9 x float]* %9 to i8*
  %55 = bitcast [16 x float]* %10 to i8*
  %56 = bitcast [16 x float]* %11 to i8*
  %57 = bitcast [16 x float]* %12 to i8*
  %scevgep570 = getelementptr [9 x float], [9 x float]* %9, i64 0, i64 1
  %scevgep573 = getelementptr [9 x float], [9 x float]* %8, i64 0, i64 1
  %scevgep575 = getelementptr [9 x float], [9 x float]* %7, i64 0, i64 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.0115219 = phi i32 [ %27, %for_loop_body.lr.ph ], [ %130, %after_if ]
  %58 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %13, align 8
  %59 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %58, i64 0, i32 14
  %60 = load i8*, i8** %59, align 8
  %61 = getelementptr inbounds i8, i8* %60, i64 4
  %62 = bitcast i8* %61 to i32*
  %63 = load i32, i32* %62, align 4
  %64 = icmp slt i32 %.0115219, %63
  br i1 %64, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %65 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %31, align 8
  %66 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %65, i64 0, i32 1, i32 1
  %67 = load float*, float** %66, align 8
  %68 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %65, i64 0, i32 1, i32 0, i32 1
  %69 = load i32, i32* %68, align 4
  %70 = mul i32 %69, %.0115219
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, float* %67, i64 %71
  %73 = load float, float* %72, align 4
  %74 = fptosi float %73 to i32
  %75 = add i32 %70, 1
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, float* %67, i64 %76
  %78 = load float, float* %77, align 4
  %79 = fptosi float %78 to i32
  %80 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %65, i64 0, i32 5
  %81 = load i32, i32* %80, align 4
  %82 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %65, i64 0, i32 6
  %83 = load i32, i32* %82, align 4
  %84 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %65, i64 0, i32 0, i32 1
  %85 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %65, i64 0, i32 0, i32 0, i32 1
  %broadcast.splatinsert528 = insertelement <4 x i32*> poison, i32* %85, i64 0
  %broadcast.splat529 = shufflevector <4 x i32*> %broadcast.splatinsert528, <4 x i32*> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert525 = insertelement <4 x float**> poison, float** %84, i64 0
  %broadcast.splat526 = shufflevector <4 x float**> %broadcast.splatinsert525, <4 x float**> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert523 = insertelement <4 x i32> poison, i32 %83, i64 0
  %broadcast.splat524 = shufflevector <4 x i32> %broadcast.splatinsert523, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert521 = insertelement <4 x i32> poison, i32 %79, i64 0
  %broadcast.splat522 = shufflevector <4 x i32> %broadcast.splatinsert521, <4 x i32> poison, <4 x i32> zeroinitializer
  %86 = add <4 x i32> %broadcast.splat522, <i32 -15, i32 -14, i32 -13, i32 -12>
  %87 = icmp sgt <4 x i32> %86, <i32 -1, i32 -1, i32 -1, i32 -1>
  %88 = icmp slt <4 x i32> %86, %broadcast.splat524
  %89 = select <4 x i1> %87, <4 x i1> %88, <4 x i1> zeroinitializer
  %90 = xor <4 x i1> %89, <i1 true, i1 true, i1 true, i1 true>
  %91 = add <4 x i32> %broadcast.splat522, <i32 -11, i32 -10, i32 -9, i32 -8>
  %92 = icmp sgt <4 x i32> %91, <i32 -1, i32 -1, i32 -1, i32 -1>
  %93 = icmp slt <4 x i32> %91, %broadcast.splat524
  %94 = select <4 x i1> %92, <4 x i1> %93, <4 x i1> zeroinitializer
  %95 = xor <4 x i1> %94, <i1 true, i1 true, i1 true, i1 true>
  %96 = add <4 x i32> %broadcast.splat522, <i32 -7, i32 -6, i32 -5, i32 -4>
  %97 = icmp sgt <4 x i32> %96, <i32 -1, i32 -1, i32 -1, i32 -1>
  %98 = icmp slt <4 x i32> %96, %broadcast.splat524
  %99 = select <4 x i1> %97, <4 x i1> %98, <4 x i1> zeroinitializer
  %100 = xor <4 x i1> %99, <i1 true, i1 true, i1 true, i1 true>
  %101 = add <4 x i32> %broadcast.splat522, <i32 -3, i32 -2, i32 -1, i32 0>
  %102 = icmp sgt <4 x i32> %101, <i32 -1, i32 -1, i32 -1, i32 -1>
  %103 = icmp slt <4 x i32> %101, %broadcast.splat524
  %104 = select <4 x i1> %102, <4 x i1> %103, <4 x i1> zeroinitializer
  %105 = xor <4 x i1> %104, <i1 true, i1 true, i1 true, i1 true>
  %106 = add <4 x i32> %broadcast.splat522, <i32 1, i32 2, i32 3, i32 4>
  %107 = icmp sgt <4 x i32> %106, <i32 -1, i32 -1, i32 -1, i32 -1>
  %108 = icmp slt <4 x i32> %106, %broadcast.splat524
  %109 = select <4 x i1> %107, <4 x i1> %108, <4 x i1> zeroinitializer
  %110 = xor <4 x i1> %109, <i1 true, i1 true, i1 true, i1 true>
  %111 = add <4 x i32> %broadcast.splat522, <i32 5, i32 6, i32 7, i32 8>
  %112 = icmp sgt <4 x i32> %111, <i32 -1, i32 -1, i32 -1, i32 -1>
  %113 = icmp slt <4 x i32> %111, %broadcast.splat524
  %114 = select <4 x i1> %112, <4 x i1> %113, <4 x i1> zeroinitializer
  %115 = xor <4 x i1> %114, <i1 true, i1 true, i1 true, i1 true>
  %116 = add <4 x i32> %broadcast.splat522, <i32 9, i32 10, i32 11, i32 12>
  %117 = icmp sgt <4 x i32> %116, <i32 -1, i32 -1, i32 -1, i32 -1>
  %118 = icmp slt <4 x i32> %116, %broadcast.splat524
  %119 = select <4 x i1> %117, <4 x i1> %118, <4 x i1> zeroinitializer
  %120 = xor <4 x i1> %119, <i1 true, i1 true, i1 true, i1 true>
  %121 = add i32 %79, 13
  %122 = icmp sgt i32 %121, -1
  %123 = icmp slt i32 %121, %83
  %spec.select.us = select i1 %122, i1 %123, i1 false
  %124 = add i32 %79, 14
  %125 = icmp sgt i32 %124, -1
  %126 = icmp slt i32 %124, %83
  %spec.select.us.1 = select i1 %125, i1 %126, i1 false
  %127 = add i32 %79, 15
  %128 = icmp sgt i32 %127, -1
  %129 = icmp slt i32 %127, %83
  %spec.select.us.2 = select i1 %128, i1 %129, i1 false
  br label %for_loop_body1

after_if:                                         ; preds = %for_loop_test134.preheader, %for_loop_body
  %130 = add nsw i32 %.0115219, 1
  %exitcond296.not = icmp eq i32 %130, %29
  br i1 %exitcond296.not, label %after_for.loopexit, label %for_loop_body

for_loop_body1:                                   ; preds = %after_for7, %true_block
  %.0108149 = phi i32 [ -15, %true_block ], [ %265, %after_for7 ]
  %.0109148 = phi float [ 0.000000e+00, %true_block ], [ %.us-phi220, %after_for7 ]
  %.0112147 = phi float [ 0.000000e+00, %true_block ], [ %.us-phi, %after_for7 ]
  %131 = mul i32 %.0108149, %.0108149
  %132 = add i32 %74, %.0108149
  %133 = icmp sgt i32 %132, -1
  %134 = icmp slt i32 %132, %81
  %or.cond = select i1 %133, i1 %134, i1 false
  %135 = sitofp i32 %.0108149 to float
  %or.cond.fr = freeze i1 %or.cond
  br i1 %or.cond.fr, label %vector.body513, label %after_for7

vector.body513:                                   ; preds = %for_loop_body1
  %broadcast.splatinsert534 = insertelement <4 x float> poison, float %135, i64 0
  %broadcast.splat535 = shufflevector <4 x float> %broadcast.splatinsert534, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert531 = insertelement <4 x i32> poison, i32 %132, i64 0
  %broadcast.splat532 = shufflevector <4 x i32> %broadcast.splatinsert531, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert519 = insertelement <4 x i32> poison, i32 %131, i64 0
  %broadcast.splat520 = shufflevector <4 x i32> %broadcast.splatinsert519, <4 x i32> poison, <4 x i32> zeroinitializer
  %136 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0112147, i64 0
  %137 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.0109148, i64 0
  %138 = add <4 x i32> %broadcast.splat520, <i32 225, i32 196, i32 169, i32 144>
  %139 = icmp slt <4 x i32> %138, <i32 226, i32 226, i32 226, i32 226>
  %140 = select <4 x i1> %139, <4 x i1> %89, <4 x i1> zeroinitializer
  %wide.masked.gather527 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat526, i32 8, <4 x i1> %140, <4 x float*> undef)
  %wide.masked.gather530 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat529, i32 4, <4 x i1> %140, <4 x i32> undef)
  %141 = mul <4 x i32> %wide.masked.gather530, %broadcast.splat532
  %142 = add <4 x i32> %141, %86
  %143 = sext <4 x i32> %142 to <4 x i64>
  %144 = getelementptr float, <4 x float*> %wide.masked.gather527, <4 x i64> %143
  %wide.masked.gather533 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %144, i32 4, <4 x i1> %140, <4 x float> undef)
  %145 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533, <float -1.500000e+01, float -1.400000e+01, float -1.300000e+01, float -1.200000e+01>
  %146 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533, %broadcast.splat535
  %147 = select <4 x i1> %139, <4 x i1> %90, <4 x i1> zeroinitializer
  %148 = xor <4 x i1> %139, <i1 true, i1 true, i1 true, i1 true>
  %149 = select <4 x i1> %148, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %147
  %predphi = select <4 x i1> %149, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %145
  %predphi536 = fadd reassoc ninf nsz <4 x float> %136, %predphi
  %predphi537 = select <4 x i1> %149, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %146
  %predphi538 = fadd reassoc ninf nsz <4 x float> %137, %predphi537
  %150 = add <4 x i32> %broadcast.splat520, <i32 121, i32 100, i32 81, i32 64>
  %151 = icmp slt <4 x i32> %150, <i32 226, i32 226, i32 226, i32 226>
  %152 = select <4 x i1> %151, <4 x i1> %94, <4 x i1> zeroinitializer
  %wide.masked.gather527.1 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat526, i32 8, <4 x i1> %152, <4 x float*> undef)
  %wide.masked.gather530.1 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat529, i32 4, <4 x i1> %152, <4 x i32> undef)
  %153 = mul <4 x i32> %wide.masked.gather530.1, %broadcast.splat532
  %154 = add <4 x i32> %153, %91
  %155 = sext <4 x i32> %154 to <4 x i64>
  %156 = getelementptr float, <4 x float*> %wide.masked.gather527.1, <4 x i64> %155
  %wide.masked.gather533.1 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %156, i32 4, <4 x i1> %152, <4 x float> undef)
  %157 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.1, <float -1.100000e+01, float -1.000000e+01, float -9.000000e+00, float -8.000000e+00>
  %158 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.1, %broadcast.splat535
  %159 = select <4 x i1> %151, <4 x i1> %95, <4 x i1> zeroinitializer
  %160 = xor <4 x i1> %151, <i1 true, i1 true, i1 true, i1 true>
  %161 = select <4 x i1> %160, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %159
  %predphi.1 = select <4 x i1> %161, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %157
  %predphi536.1 = fadd reassoc ninf nsz <4 x float> %predphi536, %predphi.1
  %predphi537.1 = select <4 x i1> %161, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %158
  %predphi538.1 = fadd reassoc ninf nsz <4 x float> %predphi538, %predphi537.1
  %162 = add <4 x i32> %broadcast.splat520, <i32 49, i32 36, i32 25, i32 16>
  %163 = icmp slt <4 x i32> %162, <i32 226, i32 226, i32 226, i32 226>
  %164 = select <4 x i1> %163, <4 x i1> %99, <4 x i1> zeroinitializer
  %wide.masked.gather527.2 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat526, i32 8, <4 x i1> %164, <4 x float*> undef)
  %wide.masked.gather530.2 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat529, i32 4, <4 x i1> %164, <4 x i32> undef)
  %165 = mul <4 x i32> %wide.masked.gather530.2, %broadcast.splat532
  %166 = add <4 x i32> %165, %96
  %167 = sext <4 x i32> %166 to <4 x i64>
  %168 = getelementptr float, <4 x float*> %wide.masked.gather527.2, <4 x i64> %167
  %wide.masked.gather533.2 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %168, i32 4, <4 x i1> %164, <4 x float> undef)
  %169 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.2, <float -7.000000e+00, float -6.000000e+00, float -5.000000e+00, float -4.000000e+00>
  %170 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.2, %broadcast.splat535
  %171 = select <4 x i1> %163, <4 x i1> %100, <4 x i1> zeroinitializer
  %172 = xor <4 x i1> %163, <i1 true, i1 true, i1 true, i1 true>
  %173 = select <4 x i1> %172, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %171
  %predphi.2 = select <4 x i1> %173, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %169
  %predphi536.2 = fadd reassoc ninf nsz <4 x float> %predphi536.1, %predphi.2
  %predphi537.2 = select <4 x i1> %173, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %170
  %predphi538.2 = fadd reassoc ninf nsz <4 x float> %predphi538.1, %predphi537.2
  %174 = add <4 x i32> %broadcast.splat520, <i32 9, i32 4, i32 1, i32 0>
  %175 = icmp slt <4 x i32> %174, <i32 226, i32 226, i32 226, i32 226>
  %176 = select <4 x i1> %175, <4 x i1> %104, <4 x i1> zeroinitializer
  %wide.masked.gather527.3 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat526, i32 8, <4 x i1> %176, <4 x float*> undef)
  %wide.masked.gather530.3 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat529, i32 4, <4 x i1> %176, <4 x i32> undef)
  %177 = mul <4 x i32> %wide.masked.gather530.3, %broadcast.splat532
  %178 = add <4 x i32> %177, %101
  %179 = sext <4 x i32> %178 to <4 x i64>
  %180 = getelementptr float, <4 x float*> %wide.masked.gather527.3, <4 x i64> %179
  %wide.masked.gather533.3 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %180, i32 4, <4 x i1> %176, <4 x float> undef)
  %181 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.3, <float -3.000000e+00, float -2.000000e+00, float -1.000000e+00, float 0.000000e+00>
  %182 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.3, %broadcast.splat535
  %183 = select <4 x i1> %175, <4 x i1> %105, <4 x i1> zeroinitializer
  %184 = xor <4 x i1> %175, <i1 true, i1 true, i1 true, i1 true>
  %185 = select <4 x i1> %184, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %183
  %predphi.3 = select <4 x i1> %185, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %181
  %predphi536.3 = fadd reassoc ninf nsz <4 x float> %predphi536.2, %predphi.3
  %predphi537.3 = select <4 x i1> %185, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %182
  %predphi538.3 = fadd reassoc ninf nsz <4 x float> %predphi538.2, %predphi537.3
  %186 = add <4 x i32> %broadcast.splat520, <i32 1, i32 4, i32 9, i32 16>
  %187 = icmp slt <4 x i32> %186, <i32 226, i32 226, i32 226, i32 226>
  %188 = select <4 x i1> %187, <4 x i1> %109, <4 x i1> zeroinitializer
  %wide.masked.gather527.4 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat526, i32 8, <4 x i1> %188, <4 x float*> undef)
  %wide.masked.gather530.4 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat529, i32 4, <4 x i1> %188, <4 x i32> undef)
  %189 = mul <4 x i32> %wide.masked.gather530.4, %broadcast.splat532
  %190 = add <4 x i32> %189, %106
  %191 = sext <4 x i32> %190 to <4 x i64>
  %192 = getelementptr float, <4 x float*> %wide.masked.gather527.4, <4 x i64> %191
  %wide.masked.gather533.4 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %192, i32 4, <4 x i1> %188, <4 x float> undef)
  %193 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.4, <float 1.000000e+00, float 2.000000e+00, float 3.000000e+00, float 4.000000e+00>
  %194 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.4, %broadcast.splat535
  %195 = select <4 x i1> %187, <4 x i1> %110, <4 x i1> zeroinitializer
  %196 = xor <4 x i1> %187, <i1 true, i1 true, i1 true, i1 true>
  %197 = select <4 x i1> %196, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %195
  %predphi.4 = select <4 x i1> %197, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %193
  %predphi536.4 = fadd reassoc ninf nsz <4 x float> %predphi536.3, %predphi.4
  %predphi537.4 = select <4 x i1> %197, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %194
  %predphi538.4 = fadd reassoc ninf nsz <4 x float> %predphi538.3, %predphi537.4
  %198 = add <4 x i32> %broadcast.splat520, <i32 25, i32 36, i32 49, i32 64>
  %199 = icmp slt <4 x i32> %198, <i32 226, i32 226, i32 226, i32 226>
  %200 = select <4 x i1> %199, <4 x i1> %114, <4 x i1> zeroinitializer
  %wide.masked.gather527.5 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat526, i32 8, <4 x i1> %200, <4 x float*> undef)
  %wide.masked.gather530.5 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat529, i32 4, <4 x i1> %200, <4 x i32> undef)
  %201 = mul <4 x i32> %wide.masked.gather530.5, %broadcast.splat532
  %202 = add <4 x i32> %201, %111
  %203 = sext <4 x i32> %202 to <4 x i64>
  %204 = getelementptr float, <4 x float*> %wide.masked.gather527.5, <4 x i64> %203
  %wide.masked.gather533.5 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %204, i32 4, <4 x i1> %200, <4 x float> undef)
  %205 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.5, <float 5.000000e+00, float 6.000000e+00, float 7.000000e+00, float 8.000000e+00>
  %206 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.5, %broadcast.splat535
  %207 = select <4 x i1> %199, <4 x i1> %115, <4 x i1> zeroinitializer
  %208 = xor <4 x i1> %199, <i1 true, i1 true, i1 true, i1 true>
  %209 = select <4 x i1> %208, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %207
  %predphi.5 = select <4 x i1> %209, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %205
  %predphi536.5 = fadd reassoc ninf nsz <4 x float> %predphi536.4, %predphi.5
  %predphi537.5 = select <4 x i1> %209, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %206
  %predphi538.5 = fadd reassoc ninf nsz <4 x float> %predphi538.4, %predphi537.5
  %210 = add <4 x i32> %broadcast.splat520, <i32 81, i32 100, i32 121, i32 144>
  %211 = icmp slt <4 x i32> %210, <i32 226, i32 226, i32 226, i32 226>
  %212 = select <4 x i1> %211, <4 x i1> %119, <4 x i1> zeroinitializer
  %wide.masked.gather527.6 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat526, i32 8, <4 x i1> %212, <4 x float*> undef)
  %wide.masked.gather530.6 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat529, i32 4, <4 x i1> %212, <4 x i32> undef)
  %213 = mul <4 x i32> %wide.masked.gather530.6, %broadcast.splat532
  %214 = add <4 x i32> %213, %116
  %215 = sext <4 x i32> %214 to <4 x i64>
  %216 = getelementptr float, <4 x float*> %wide.masked.gather527.6, <4 x i64> %215
  %wide.masked.gather533.6 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %216, i32 4, <4 x i1> %212, <4 x float> undef)
  %217 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.6, <float 9.000000e+00, float 1.000000e+01, float 1.100000e+01, float 1.200000e+01>
  %218 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather533.6, %broadcast.splat535
  %219 = select <4 x i1> %211, <4 x i1> %120, <4 x i1> zeroinitializer
  %220 = xor <4 x i1> %211, <i1 true, i1 true, i1 true, i1 true>
  %221 = select <4 x i1> %220, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %219
  %predphi.6 = select <4 x i1> %221, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %217
  %predphi536.6 = fadd reassoc ninf nsz <4 x float> %predphi536.5, %predphi.6
  %predphi537.6 = select <4 x i1> %221, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %218
  %predphi538.6 = fadd reassoc ninf nsz <4 x float> %predphi538.5, %predphi537.6
  %222 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %predphi536.6)
  %223 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %predphi538.6)
  %224 = add i32 %131, 169
  %225 = icmp slt i32 %224, 226
  %.not = xor i1 %225, true
  %spec.select.us.not = xor i1 %spec.select.us, true
  %brmerge = select i1 %.not, i1 true, i1 %spec.select.us.not
  br i1 %brmerge, label %after_if11.us, label %true_block21.us

true_block21.us:                                  ; preds = %vector.body513
  %226 = load float*, float** %84, align 8
  %227 = load i32, i32* %85, align 4
  %228 = mul i32 %227, %132
  %229 = add i32 %228, %121
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, float* %226, i64 %230
  %232 = load float, float* %231, align 4
  %233 = fmul reassoc ninf nsz float %232, 1.300000e+01
  %234 = fadd reassoc ninf nsz float %233, %222
  %235 = fmul reassoc ninf nsz float %232, %135
  %236 = fadd reassoc ninf nsz float %235, %223
  br label %after_if11.us

after_if11.us:                                    ; preds = %true_block21.us, %vector.body513
  %.2114.us = phi float [ %234, %true_block21.us ], [ %222, %vector.body513 ]
  %.2111.us = phi float [ %236, %true_block21.us ], [ %223, %vector.body513 ]
  %237 = add i32 %131, 196
  %238 = icmp slt i32 %237, 226
  %.not546 = xor i1 %238, true
  %spec.select.us.1.not = xor i1 %spec.select.us.1, true
  %brmerge547 = select i1 %.not546, i1 true, i1 %spec.select.us.1.not
  br i1 %brmerge547, label %after_if11.us.1, label %true_block21.us.1

true_block21.us.1:                                ; preds = %after_if11.us
  %239 = load float*, float** %84, align 8
  %240 = load i32, i32* %85, align 4
  %241 = mul i32 %240, %132
  %242 = add i32 %241, %124
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, float* %239, i64 %243
  %245 = load float, float* %244, align 4
  %246 = fmul reassoc ninf nsz float %245, 1.400000e+01
  %247 = fadd reassoc ninf nsz float %246, %.2114.us
  %248 = fmul reassoc ninf nsz float %245, %135
  %249 = fadd reassoc ninf nsz float %248, %.2111.us
  br label %after_if11.us.1

after_if11.us.1:                                  ; preds = %true_block21.us.1, %after_if11.us
  %.2114.us.1 = phi float [ %247, %true_block21.us.1 ], [ %.2114.us, %after_if11.us ]
  %.2111.us.1 = phi float [ %249, %true_block21.us.1 ], [ %.2111.us, %after_if11.us ]
  %250 = add i32 %131, 225
  %251 = icmp slt i32 %250, 226
  %.not548 = xor i1 %251, true
  %spec.select.us.2.not = xor i1 %spec.select.us.2, true
  %brmerge549 = select i1 %.not548, i1 true, i1 %spec.select.us.2.not
  br i1 %brmerge549, label %after_for7, label %true_block21.us.2

true_block21.us.2:                                ; preds = %after_if11.us.1
  %252 = load float*, float** %84, align 8
  %253 = load i32, i32* %85, align 4
  %254 = mul i32 %253, %132
  %255 = add i32 %254, %127
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, float* %252, i64 %256
  %258 = load float, float* %257, align 4
  %259 = fmul reassoc ninf nsz float %258, 1.500000e+01
  %260 = fadd reassoc ninf nsz float %259, %.2114.us.1
  %261 = fmul reassoc ninf nsz float %258, %135
  %262 = fadd reassoc ninf nsz float %261, %.2111.us.1
  br label %after_for7

after_for3:                                       ; preds = %after_for7
  %263 = fcmp reassoc ninf nsz one float %.us-phi, 0.000000e+00
  %264 = fcmp reassoc ninf nsz one float %.us-phi220, 0.000000e+00
  %.0102 = select i1 %263, i1 true, i1 %264
  br i1 %.0102, label %true_block27, label %after_if29

after_for7:                                       ; preds = %true_block21.us.2, %after_if11.us.1, %for_loop_body1
  %.us-phi = phi float [ %.0112147, %for_loop_body1 ], [ %260, %true_block21.us.2 ], [ %.2114.us.1, %after_if11.us.1 ]
  %.us-phi220 = phi float [ %.0109148, %for_loop_body1 ], [ %262, %true_block21.us.2 ], [ %.2111.us.1, %after_if11.us.1 ]
  %265 = add nsw i32 %.0108149, 1
  %exitcond233.not = icmp eq i32 %265, 16
  br i1 %exitcond233.not, label %after_for3, label %for_loop_body1

true_block27:                                     ; preds = %after_for3
  %266 = tail call float @atan2f(float noundef %.us-phi220, float noundef %.us-phi) #1
  br label %after_if29

after_if29:                                       ; preds = %true_block27, %after_for3
  %.0103 = phi float [ %266, %true_block27 ], [ 0.000000e+00, %after_for3 ]
  %267 = tail call float @cosf(float noundef %.0103) #1
  %268 = tail call float @sinf(float noundef %.0103) #1
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(64) %48, i8 0, i64 64, i1 false)
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(16) %49, i8 0, i64 16, i1 false)
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(16) %50, i8 0, i64 16, i1 false)
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(16) %51, i8 0, i64 16, i1 false)
  %269 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %31, align 8
  %270 = add i32 %81, -1
  %271 = add i32 %83, -1
  %272 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %269, i64 0, i32 0, i32 1
  %273 = load float*, float** %272, align 8
  %274 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %269, i64 0, i32 0, i32 0, i32 1
  %275 = load i32, i32* %274, align 4
  %broadcast.splatinsert454 = insertelement <4 x float> poison, float %268, i64 0
  %broadcast.splat455 = shufflevector <4 x float> %broadcast.splatinsert454, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert456 = insertelement <4 x float> poison, float %267, i64 0
  %broadcast.splat457 = shufflevector <4 x float> %broadcast.splatinsert456, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert464 = insertelement <4 x i32> poison, i32 %74, i64 0
  %broadcast.splat465 = shufflevector <4 x i32> %broadcast.splatinsert464, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert466 = insertelement <4 x i32> poison, i32 %270, i64 0
  %broadcast.splat467 = shufflevector <4 x i32> %broadcast.splatinsert466, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert468 = insertelement <4 x i32> poison, i32 %271, i64 0
  %broadcast.splat469 = shufflevector <4 x i32> %broadcast.splatinsert468, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert470 = insertelement <4 x i32> poison, i32 %275, i64 0
  %broadcast.splat471 = shufflevector <4 x i32> %broadcast.splatinsert470, <4 x i32> poison, <4 x i32> zeroinitializer
  br label %for_loop_body30

for_loop_body30:                                  ; preds = %after_for36, %after_if29
  %lsr.iv554 = phi [4 x float]* [ %6, %after_if29 ], [ %517, %after_for36 ]
  %lsr.iv551 = phi [4 x float]* [ %5, %after_if29 ], [ %516, %after_for36 ]
  %lsr.iv = phi [4 x float]* [ %4, %after_if29 ], [ %515, %after_for36 ]
  %indvars.iv238 = phi i64 [ 0, %after_if29 ], [ %indvars.iv.next239, %after_for36 ]
  %276 = trunc i64 %indvars.iv238 to i32
  %277 = sitofp i32 %276 to float
  %278 = fmul reassoc ninf nsz float %277, 1.000000e+01
  %279 = fadd reassoc ninf nsz float %278, -8.750000e+00
  %broadcast.splatinsert452 = insertelement <4 x float> poison, float %279, i64 0
  %broadcast.splat453 = shufflevector <4 x float> %broadcast.splatinsert452, <4 x float> poison, <4 x i32> zeroinitializer
  %280 = fadd reassoc ninf nsz <4 x float> %broadcast.splat453, <float 0.000000e+00, float 2.500000e+00, float 5.000000e+00, float 7.500000e+00>
  %281 = fmul reassoc ninf nsz <4 x float> %280, %broadcast.splat455
  %282 = fmul reassoc ninf nsz <4 x float> %280, %broadcast.splat457
  br label %for_loop_body34

for_loop_body34:                                  ; preds = %for_loop_body34, %for_loop_body30
  %indvars.iv = phi i64 [ 0, %for_loop_body30 ], [ %indvars.iv.next, %for_loop_body34 ]
  %scevgep550 = getelementptr [4 x float], [4 x float]* %lsr.iv, i64 0, i64 %indvars.iv
  %scevgep553 = getelementptr [4 x float], [4 x float]* %lsr.iv551, i64 0, i64 %indvars.iv
  %scevgep556 = getelementptr [4 x float], [4 x float]* %lsr.iv554, i64 0, i64 %indvars.iv
  %tmp = trunc i64 %indvars.iv to i32
  %283 = sitofp i32 %tmp to float
  %284 = fmul reassoc ninf nsz float %283, 1.000000e+01
  %285 = fadd reassoc ninf nsz float %284, -1.250000e+00
  %286 = fmul reassoc ninf nsz float %285, %268
  %287 = fmul reassoc ninf nsz float %285, %267
  %288 = fadd reassoc ninf nsz float %284, -3.750000e+00
  %289 = fmul reassoc ninf nsz float %288, %268
  %290 = fmul reassoc ninf nsz float %288, %267
  %291 = fadd reassoc ninf nsz float %284, -6.250000e+00
  %292 = fmul reassoc ninf nsz float %291, %268
  %293 = fmul reassoc ninf nsz float %291, %267
  %294 = fadd reassoc ninf nsz float %284, -8.750000e+00
  %295 = fmul reassoc ninf nsz float %294, %268
  %296 = fmul reassoc ninf nsz float %294, %267
  %.promoted158 = load float, float* %scevgep556, align 4
  %.promoted = load float, float* %scevgep553, align 4
  %.promoted155 = load float, float* %scevgep550, align 4
  %297 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted155, i64 0
  %298 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted, i64 0
  %299 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted158, i64 0
  %broadcast.splatinsert458 = insertelement <4 x float> poison, float %296, i64 0
  %broadcast.splat459 = shufflevector <4 x float> %broadcast.splatinsert458, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert460 = insertelement <4 x float> poison, float %295, i64 0
  %broadcast.splat461 = shufflevector <4 x float> %broadcast.splatinsert460, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert477 = insertelement <4 x float> poison, float %293, i64 0
  %broadcast.splat478 = shufflevector <4 x float> %broadcast.splatinsert477, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert479 = insertelement <4 x float> poison, float %292, i64 0
  %broadcast.splat480 = shufflevector <4 x float> %broadcast.splatinsert479, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert486 = insertelement <4 x float> poison, float %290, i64 0
  %broadcast.splat487 = shufflevector <4 x float> %broadcast.splatinsert486, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert488 = insertelement <4 x float> poison, float %289, i64 0
  %broadcast.splat489 = shufflevector <4 x float> %broadcast.splatinsert488, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert495 = insertelement <4 x float> poison, float %287, i64 0
  %broadcast.splat496 = shufflevector <4 x float> %broadcast.splatinsert495, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert497 = insertelement <4 x float> poison, float %286, i64 0
  %broadcast.splat498 = shufflevector <4 x float> %broadcast.splatinsert497, <4 x float> poison, <4 x i32> zeroinitializer
  %300 = fsub reassoc ninf nsz <4 x float> %broadcast.splat459, %281
  %301 = fadd reassoc ninf nsz <4 x float> %broadcast.splat461, %282
  %302 = fptosi <4 x float> %300 to <4 x i32>
  %303 = add <4 x i32> %broadcast.splat522, %302
  %304 = fptosi <4 x float> %301 to <4 x i32>
  %305 = add <4 x i32> %broadcast.splat465, %304
  %306 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %305)
  %307 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %306, <4 x i32> zeroinitializer)
  %308 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %303)
  %309 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %308, <4 x i32> zeroinitializer)
  %310 = mul <4 x i32> %broadcast.splat471, %307
  %311 = add <4 x i32> %310, %309
  %312 = sext <4 x i32> %311 to <4 x i64>
  %313 = getelementptr float, float* %273, <4 x i64> %312
  %wide.masked.gather472 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %313, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %314 = add <4 x i32> %303, <i32 1, i32 1, i32 1, i32 1>
  %315 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %314)
  %316 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %315, <4 x i32> zeroinitializer)
  %317 = add <4 x i32> %303, <i32 -1, i32 -1, i32 -1, i32 -1>
  %318 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %317)
  %319 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %318, <4 x i32> zeroinitializer)
  %320 = add <4 x i32> %310, %316
  %321 = sext <4 x i32> %320 to <4 x i64>
  %322 = getelementptr float, float* %273, <4 x i64> %321
  %wide.masked.gather473 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %322, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %323 = add <4 x i32> %310, %319
  %324 = sext <4 x i32> %323 to <4 x i64>
  %325 = getelementptr float, float* %273, <4 x i64> %324
  %wide.masked.gather474 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %325, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %326 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather473, %wide.masked.gather474
  %327 = fmul reassoc ninf nsz <4 x float> %326, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %328 = add <4 x i32> %305, <i32 1, i32 1, i32 1, i32 1>
  %329 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %328)
  %330 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %329, <4 x i32> zeroinitializer)
  %331 = add <4 x i32> %305, <i32 -1, i32 -1, i32 -1, i32 -1>
  %332 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %331)
  %333 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %332, <4 x i32> zeroinitializer)
  %334 = mul <4 x i32> %broadcast.splat471, %330
  %335 = add <4 x i32> %334, %309
  %336 = sext <4 x i32> %335 to <4 x i64>
  %337 = getelementptr float, float* %273, <4 x i64> %336
  %wide.masked.gather475 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %337, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %338 = mul <4 x i32> %broadcast.splat471, %333
  %339 = add <4 x i32> %338, %309
  %340 = sext <4 x i32> %339 to <4 x i64>
  %341 = getelementptr float, float* %273, <4 x i64> %340
  %wide.masked.gather476 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %341, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %342 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather475, %wide.masked.gather476
  %343 = fmul reassoc ninf nsz <4 x float> %342, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %344 = fmul reassoc ninf nsz <4 x float> %327, %broadcast.splat457
  %345 = fmul reassoc ninf nsz <4 x float> %343, %broadcast.splat455
  %346 = fadd reassoc ninf nsz <4 x float> %345, %344
  %347 = fmul reassoc ninf nsz <4 x float> %343, %broadcast.splat457
  %348 = fmul reassoc ninf nsz <4 x float> %327, %broadcast.splat455
  %349 = fsub reassoc ninf nsz <4 x float> %347, %348
  %350 = fadd reassoc ninf nsz <4 x float> %297, %wide.masked.gather472
  %351 = fadd reassoc ninf nsz <4 x float> %346, %298
  %352 = fadd reassoc ninf nsz <4 x float> %349, %299
  %353 = fsub reassoc ninf nsz <4 x float> %broadcast.splat478, %281
  %354 = fadd reassoc ninf nsz <4 x float> %broadcast.splat480, %282
  %355 = fptosi <4 x float> %353 to <4 x i32>
  %356 = add <4 x i32> %broadcast.splat522, %355
  %357 = fptosi <4 x float> %354 to <4 x i32>
  %358 = add <4 x i32> %broadcast.splat465, %357
  %359 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %358)
  %360 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %359, <4 x i32> zeroinitializer)
  %361 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %356)
  %362 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %361, <4 x i32> zeroinitializer)
  %363 = mul <4 x i32> %broadcast.splat471, %360
  %364 = add <4 x i32> %363, %362
  %365 = sext <4 x i32> %364 to <4 x i64>
  %366 = getelementptr float, float* %273, <4 x i64> %365
  %wide.masked.gather481 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %366, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %367 = add <4 x i32> %356, <i32 1, i32 1, i32 1, i32 1>
  %368 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %367)
  %369 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %368, <4 x i32> zeroinitializer)
  %370 = add <4 x i32> %356, <i32 -1, i32 -1, i32 -1, i32 -1>
  %371 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %370)
  %372 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %371, <4 x i32> zeroinitializer)
  %373 = add <4 x i32> %363, %369
  %374 = sext <4 x i32> %373 to <4 x i64>
  %375 = getelementptr float, float* %273, <4 x i64> %374
  %wide.masked.gather482 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %375, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %376 = add <4 x i32> %363, %372
  %377 = sext <4 x i32> %376 to <4 x i64>
  %378 = getelementptr float, float* %273, <4 x i64> %377
  %wide.masked.gather483 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %378, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %379 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather482, %wide.masked.gather483
  %380 = fmul reassoc ninf nsz <4 x float> %379, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %381 = add <4 x i32> %358, <i32 1, i32 1, i32 1, i32 1>
  %382 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %381)
  %383 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %382, <4 x i32> zeroinitializer)
  %384 = add <4 x i32> %358, <i32 -1, i32 -1, i32 -1, i32 -1>
  %385 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %384)
  %386 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %385, <4 x i32> zeroinitializer)
  %387 = mul <4 x i32> %broadcast.splat471, %383
  %388 = add <4 x i32> %387, %362
  %389 = sext <4 x i32> %388 to <4 x i64>
  %390 = getelementptr float, float* %273, <4 x i64> %389
  %wide.masked.gather484 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %390, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %391 = mul <4 x i32> %broadcast.splat471, %386
  %392 = add <4 x i32> %391, %362
  %393 = sext <4 x i32> %392 to <4 x i64>
  %394 = getelementptr float, float* %273, <4 x i64> %393
  %wide.masked.gather485 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %394, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %395 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather484, %wide.masked.gather485
  %396 = fmul reassoc ninf nsz <4 x float> %395, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %397 = fmul reassoc ninf nsz <4 x float> %380, %broadcast.splat457
  %398 = fmul reassoc ninf nsz <4 x float> %396, %broadcast.splat455
  %399 = fadd reassoc ninf nsz <4 x float> %398, %397
  %400 = fmul reassoc ninf nsz <4 x float> %396, %broadcast.splat457
  %401 = fmul reassoc ninf nsz <4 x float> %380, %broadcast.splat455
  %402 = fsub reassoc ninf nsz <4 x float> %400, %401
  %403 = fadd reassoc ninf nsz <4 x float> %350, %wide.masked.gather481
  %404 = fadd reassoc ninf nsz <4 x float> %399, %351
  %405 = fadd reassoc ninf nsz <4 x float> %402, %352
  %406 = fsub reassoc ninf nsz <4 x float> %broadcast.splat487, %281
  %407 = fadd reassoc ninf nsz <4 x float> %broadcast.splat489, %282
  %408 = fptosi <4 x float> %406 to <4 x i32>
  %409 = add <4 x i32> %broadcast.splat522, %408
  %410 = fptosi <4 x float> %407 to <4 x i32>
  %411 = add <4 x i32> %broadcast.splat465, %410
  %412 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %411)
  %413 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %412, <4 x i32> zeroinitializer)
  %414 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %409)
  %415 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %414, <4 x i32> zeroinitializer)
  %416 = mul <4 x i32> %broadcast.splat471, %413
  %417 = add <4 x i32> %416, %415
  %418 = sext <4 x i32> %417 to <4 x i64>
  %419 = getelementptr float, float* %273, <4 x i64> %418
  %wide.masked.gather490 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %419, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %420 = add <4 x i32> %409, <i32 1, i32 1, i32 1, i32 1>
  %421 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %420)
  %422 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %421, <4 x i32> zeroinitializer)
  %423 = add <4 x i32> %409, <i32 -1, i32 -1, i32 -1, i32 -1>
  %424 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %423)
  %425 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %424, <4 x i32> zeroinitializer)
  %426 = add <4 x i32> %416, %422
  %427 = sext <4 x i32> %426 to <4 x i64>
  %428 = getelementptr float, float* %273, <4 x i64> %427
  %wide.masked.gather491 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %428, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %429 = add <4 x i32> %416, %425
  %430 = sext <4 x i32> %429 to <4 x i64>
  %431 = getelementptr float, float* %273, <4 x i64> %430
  %wide.masked.gather492 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %431, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %432 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather491, %wide.masked.gather492
  %433 = fmul reassoc ninf nsz <4 x float> %432, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %434 = add <4 x i32> %411, <i32 1, i32 1, i32 1, i32 1>
  %435 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %434)
  %436 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %435, <4 x i32> zeroinitializer)
  %437 = add <4 x i32> %411, <i32 -1, i32 -1, i32 -1, i32 -1>
  %438 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %437)
  %439 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %438, <4 x i32> zeroinitializer)
  %440 = mul <4 x i32> %broadcast.splat471, %436
  %441 = add <4 x i32> %440, %415
  %442 = sext <4 x i32> %441 to <4 x i64>
  %443 = getelementptr float, float* %273, <4 x i64> %442
  %wide.masked.gather493 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %443, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %444 = mul <4 x i32> %broadcast.splat471, %439
  %445 = add <4 x i32> %444, %415
  %446 = sext <4 x i32> %445 to <4 x i64>
  %447 = getelementptr float, float* %273, <4 x i64> %446
  %wide.masked.gather494 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %447, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %448 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather493, %wide.masked.gather494
  %449 = fmul reassoc ninf nsz <4 x float> %448, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %450 = fmul reassoc ninf nsz <4 x float> %433, %broadcast.splat457
  %451 = fmul reassoc ninf nsz <4 x float> %449, %broadcast.splat455
  %452 = fadd reassoc ninf nsz <4 x float> %451, %450
  %453 = fmul reassoc ninf nsz <4 x float> %449, %broadcast.splat457
  %454 = fmul reassoc ninf nsz <4 x float> %433, %broadcast.splat455
  %455 = fsub reassoc ninf nsz <4 x float> %453, %454
  %456 = fadd reassoc ninf nsz <4 x float> %403, %wide.masked.gather490
  %457 = fadd reassoc ninf nsz <4 x float> %452, %404
  %458 = fadd reassoc ninf nsz <4 x float> %455, %405
  %459 = fsub reassoc ninf nsz <4 x float> %broadcast.splat496, %281
  %460 = fadd reassoc ninf nsz <4 x float> %broadcast.splat498, %282
  %461 = fptosi <4 x float> %459 to <4 x i32>
  %462 = add <4 x i32> %broadcast.splat522, %461
  %463 = fptosi <4 x float> %460 to <4 x i32>
  %464 = add <4 x i32> %broadcast.splat465, %463
  %465 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %464)
  %466 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %465, <4 x i32> zeroinitializer)
  %467 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %462)
  %468 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %467, <4 x i32> zeroinitializer)
  %469 = mul <4 x i32> %broadcast.splat471, %466
  %470 = add <4 x i32> %469, %468
  %471 = sext <4 x i32> %470 to <4 x i64>
  %472 = getelementptr float, float* %273, <4 x i64> %471
  %wide.masked.gather499 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %472, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %473 = add <4 x i32> %462, <i32 1, i32 1, i32 1, i32 1>
  %474 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %473)
  %475 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %474, <4 x i32> zeroinitializer)
  %476 = add <4 x i32> %462, <i32 -1, i32 -1, i32 -1, i32 -1>
  %477 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %476)
  %478 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %477, <4 x i32> zeroinitializer)
  %479 = add <4 x i32> %469, %475
  %480 = sext <4 x i32> %479 to <4 x i64>
  %481 = getelementptr float, float* %273, <4 x i64> %480
  %wide.masked.gather500 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %481, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %482 = add <4 x i32> %469, %478
  %483 = sext <4 x i32> %482 to <4 x i64>
  %484 = getelementptr float, float* %273, <4 x i64> %483
  %wide.masked.gather501 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %484, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %485 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather500, %wide.masked.gather501
  %486 = fmul reassoc ninf nsz <4 x float> %485, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %487 = add <4 x i32> %464, <i32 1, i32 1, i32 1, i32 1>
  %488 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %487)
  %489 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %488, <4 x i32> zeroinitializer)
  %490 = add <4 x i32> %464, <i32 -1, i32 -1, i32 -1, i32 -1>
  %491 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %490)
  %492 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %491, <4 x i32> zeroinitializer)
  %493 = mul <4 x i32> %broadcast.splat471, %489
  %494 = add <4 x i32> %493, %468
  %495 = sext <4 x i32> %494 to <4 x i64>
  %496 = getelementptr float, float* %273, <4 x i64> %495
  %wide.masked.gather502 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %496, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %497 = mul <4 x i32> %broadcast.splat471, %492
  %498 = add <4 x i32> %497, %468
  %499 = sext <4 x i32> %498 to <4 x i64>
  %500 = getelementptr float, float* %273, <4 x i64> %499
  %wide.masked.gather503 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %500, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %501 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather502, %wide.masked.gather503
  %502 = fmul reassoc ninf nsz <4 x float> %501, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %503 = fmul reassoc ninf nsz <4 x float> %486, %broadcast.splat457
  %504 = fmul reassoc ninf nsz <4 x float> %502, %broadcast.splat455
  %505 = fadd reassoc ninf nsz <4 x float> %504, %503
  %506 = fmul reassoc ninf nsz <4 x float> %502, %broadcast.splat457
  %507 = fmul reassoc ninf nsz <4 x float> %486, %broadcast.splat455
  %508 = fsub reassoc ninf nsz <4 x float> %506, %507
  %509 = fadd reassoc ninf nsz <4 x float> %456, %wide.masked.gather499
  %510 = fadd reassoc ninf nsz <4 x float> %505, %457
  %511 = fadd reassoc ninf nsz <4 x float> %508, %458
  %512 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %511)
  %513 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %510)
  %514 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %509)
  store float %514, float* %scevgep550, align 4
  store float %513, float* %scevgep553, align 4
  store float %512, float* %scevgep556, align 4
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %exitcond237.not = icmp eq i64 %indvars.iv.next, 2
  br i1 %exitcond237.not, label %after_for36, label %for_loop_body34

after_for36:                                      ; preds = %for_loop_body34
  %indvars.iv.next239 = add nuw nsw i64 %indvars.iv238, 1
  %scevgep = getelementptr [4 x float], [4 x float]* %lsr.iv, i64 0, i64 2
  %515 = bitcast float* %scevgep to [4 x float]*
  %scevgep552 = getelementptr [4 x float], [4 x float]* %lsr.iv551, i64 0, i64 2
  %516 = bitcast float* %scevgep552 to [4 x float]*
  %scevgep555 = getelementptr [4 x float], [4 x float]* %lsr.iv554, i64 0, i64 2
  %517 = bitcast float* %scevgep555 to [4 x float]*
  %exitcond241.not = icmp eq i64 %indvars.iv.next239, 2
  br i1 %exitcond241.not, label %for_loop_body46.preheader, label %for_loop_body30

for_loop_body46.preheader:                        ; preds = %after_for36
  br label %for_loop_body46

for_loop_body46:                                  ; preds = %for_loop_test49.loopexit, %for_loop_body46.preheader
  %indvars.iv248 = phi i64 [ %indvars.iv.next249, %for_loop_test49.loopexit ], [ 0, %for_loop_body46.preheader ]
  %indvars.iv242 = phi i64 [ %indvars.iv.next243, %for_loop_test49.loopexit ], [ 1, %for_loop_body46.preheader ]
  %.0101168 = phi i32 [ %.1.lcssa, %for_loop_test49.loopexit ], [ 0, %for_loop_body46.preheader ]
  %indvars.iv.next249 = add nuw nsw i64 %indvars.iv248, 1
  %518 = icmp ult i64 %indvars.iv248, 3
  br i1 %518, label %for_loop_body50.lr.ph, label %for_loop_test49.loopexit

for_loop_body50.lr.ph:                            ; preds = %for_loop_body46
  %519 = getelementptr [4 x float], [4 x float]* %4, i64 0, i64 %indvars.iv248
  %520 = load float, float* %519, align 4
  %521 = getelementptr [4 x float], [4 x float]* %5, i64 0, i64 %indvars.iv248
  %522 = load float, float* %521, align 4
  %523 = getelementptr [4 x float], [4 x float]* %6, i64 0, i64 %indvars.iv248
  %524 = load float, float* %523, align 4
  br label %for_loop_body50

after_for48:                                      ; preds = %for_loop_test49.loopexit
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(36) %52, i8 0, i64 36, i1 false)
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(36) %53, i8 0, i64 36, i1 false)
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(36) %54, i8 0, i64 36, i1 false)
  br label %for_loop_body63

for_loop_test49.loopexit.loopexit:                ; preds = %after_if62
  br label %for_loop_test49.loopexit

for_loop_test49.loopexit:                         ; preds = %for_loop_test49.loopexit.loopexit, %for_loop_body46
  %.1.lcssa = phi i32 [ %.0101168, %for_loop_body46 ], [ %571, %for_loop_test49.loopexit.loopexit ]
  %indvars.iv.next243 = add nuw nsw i64 %indvars.iv242, 1
  %exitcond251.not = icmp eq i64 %indvars.iv.next249, 4
  br i1 %exitcond251.not, label %after_for48, label %for_loop_body46

for_loop_body50:                                  ; preds = %after_if62, %for_loop_body50.lr.ph
  %indvars.iv244 = phi i64 [ %indvars.iv242, %for_loop_body50.lr.ph ], [ %indvars.iv.next245, %after_if62 ]
  %.1166 = phi i32 [ %.0101168, %for_loop_body50.lr.ph ], [ %571, %after_if62 ]
  %scevgep559 = getelementptr [4 x float], [4 x float]* %4, i64 0, i64 %indvars.iv244
  %525 = load float, float* %scevgep559, align 4
  %526 = fcmp reassoc ninf nsz ogt float %520, %525
  br i1 %526, label %true_block54, label %after_if56

true_block54:                                     ; preds = %for_loop_body50
  %527 = sdiv i32 %.1166, 32
  %528 = icmp slt i32 %.1166, 0
  %529 = shl nsw i32 %527, 5
  %530 = icmp ne i32 %.1166, %529
  %531 = and i1 %528, %530
  %.neg138 = sext i1 %531 to i32
  %532 = add nsw i32 %527, %.neg138
  %.neg139 = mul i32 %532, -32
  %533 = add i32 %.1166, %.neg139
  %534 = shl nuw i32 1, %533
  %535 = sext i32 %532 to i64
  %536 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %535
  %537 = load i32, i32* %536, align 4
  %538 = or i32 %537, %534
  store i32 %538, i32* %536, align 4
  br label %after_if56

after_if56:                                       ; preds = %true_block54, %for_loop_body50
  %scevgep558 = getelementptr [4 x float], [4 x float]* %5, i64 0, i64 %indvars.iv244
  %539 = load float, float* %scevgep558, align 4
  %540 = fcmp reassoc ninf nsz ogt float %522, %539
  br i1 %540, label %true_block57, label %after_if59

true_block57:                                     ; preds = %after_if56
  %541 = add i32 %.1166, 1
  %542 = sdiv i32 %541, 32
  %543 = icmp slt i32 %541, 0
  %544 = shl nsw i32 %542, 5
  %545 = icmp ne i32 %541, %544
  %546 = and i1 %543, %545
  %.neg136 = sext i1 %546 to i32
  %547 = add nsw i32 %542, %.neg136
  %.neg137 = mul i32 %547, -32
  %548 = add i32 %.1166, %.neg137
  %549 = add i32 %548, 1
  %550 = shl nuw i32 1, %549
  %551 = sext i32 %547 to i64
  %552 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %551
  %553 = load i32, i32* %552, align 4
  %554 = or i32 %553, %550
  store i32 %554, i32* %552, align 4
  br label %after_if59

after_if59:                                       ; preds = %true_block57, %after_if56
  %scevgep557 = getelementptr [4 x float], [4 x float]* %6, i64 0, i64 %indvars.iv244
  %555 = load float, float* %scevgep557, align 4
  %556 = fcmp reassoc ninf nsz ogt float %524, %555
  br i1 %556, label %true_block60, label %after_if62

true_block60:                                     ; preds = %after_if59
  %557 = add i32 %.1166, 2
  %558 = sdiv i32 %557, 32
  %559 = icmp slt i32 %557, 0
  %560 = shl nsw i32 %558, 5
  %561 = icmp ne i32 %557, %560
  %562 = and i1 %559, %561
  %.neg134 = sext i1 %562 to i32
  %563 = add nsw i32 %558, %.neg134
  %.neg135 = mul i32 %563, -32
  %564 = add i32 %.1166, %.neg135
  %565 = add i32 %564, 2
  %566 = shl nuw i32 1, %565
  %567 = sext i32 %563 to i64
  %568 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %567
  %569 = load i32, i32* %568, align 4
  %570 = or i32 %569, %566
  store i32 %570, i32* %568, align 4
  br label %after_if62

after_if62:                                       ; preds = %true_block60, %after_if59
  %571 = add i32 %.1166, 3
  %indvars.iv.next245 = add nuw nsw i64 %indvars.iv244, 1
  %exitcond247.not = icmp eq i64 %indvars.iv.next245, 4
  br i1 %exitcond247.not, label %for_loop_test49.loopexit.loopexit, label %for_loop_body50

for_loop_body63:                                  ; preds = %after_for69, %after_for48
  %lsr.iv567 = phi [9 x float]* [ %9, %after_for48 ], [ %813, %after_for69 ]
  %lsr.iv564 = phi [9 x float]* [ %8, %after_for48 ], [ %812, %after_for69 ]
  %lsr.iv561 = phi [9 x float]* [ %7, %after_for48 ], [ %811, %after_for69 ]
  %indvars.iv258 = phi i64 [ 0, %after_for48 ], [ %indvars.iv.next259, %after_for69 ]
  %572 = trunc i64 %indvars.iv258 to i32
  %573 = sitofp i32 %572 to float
  %574 = fmul reassoc ninf nsz float %573, 0x401AAAAAA0000000
  %575 = fadd reassoc ninf nsz float %574, 0xC022555560000000
  %broadcast.splatinsert384 = insertelement <4 x float> poison, float %575, i64 0
  %broadcast.splat385 = shufflevector <4 x float> %broadcast.splatinsert384, <4 x float> poison, <4 x i32> zeroinitializer
  %576 = fadd reassoc ninf nsz <4 x float> %broadcast.splat385, <float 0.000000e+00, float 0x3FFAAAAAA0000000, float 0x400AAAAAA0000000, float 5.000000e+00>
  %577 = fmul reassoc ninf nsz <4 x float> %576, %broadcast.splat455
  %578 = fmul reassoc ninf nsz <4 x float> %576, %broadcast.splat457
  br label %for_loop_body67

for_loop_body67:                                  ; preds = %for_loop_body67, %for_loop_body63
  %indvars.iv254 = phi i64 [ 0, %for_loop_body63 ], [ %indvars.iv.next255, %for_loop_body67 ]
  %scevgep563 = getelementptr [9 x float], [9 x float]* %lsr.iv561, i64 0, i64 %indvars.iv254
  %scevgep566 = getelementptr [9 x float], [9 x float]* %lsr.iv564, i64 0, i64 %indvars.iv254
  %scevgep569 = getelementptr [9 x float], [9 x float]* %lsr.iv567, i64 0, i64 %indvars.iv254
  %tmp560 = trunc i64 %indvars.iv254 to i32
  %579 = sitofp i32 %tmp560 to float
  %580 = fmul reassoc ninf nsz float %579, 0x401AAAAAA0000000
  %581 = fadd reassoc ninf nsz float %580, 0xC010AAAAC0000000
  %582 = fmul reassoc ninf nsz float %581, %268
  %583 = fmul reassoc ninf nsz float %581, %267
  %584 = fadd reassoc ninf nsz float %580, 0xC017555580000000
  %585 = fmul reassoc ninf nsz float %584, %268
  %586 = fmul reassoc ninf nsz float %584, %267
  %587 = fadd reassoc ninf nsz float %580, 0xC01E000020000000
  %588 = fmul reassoc ninf nsz float %587, %268
  %589 = fmul reassoc ninf nsz float %587, %267
  %590 = fadd reassoc ninf nsz float %580, 0xC022555560000000
  %591 = fmul reassoc ninf nsz float %590, %268
  %592 = fmul reassoc ninf nsz float %590, %267
  %.promoted181 = load float, float* %scevgep569, align 4
  %.promoted179 = load float, float* %scevgep566, align 4
  %.promoted177 = load float, float* %scevgep563, align 4
  %593 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted177, i64 0
  %594 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted179, i64 0
  %595 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted181, i64 0
  %broadcast.splatinsert390 = insertelement <4 x float> poison, float %592, i64 0
  %broadcast.splat391 = shufflevector <4 x float> %broadcast.splatinsert390, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert392 = insertelement <4 x float> poison, float %591, i64 0
  %broadcast.splat393 = shufflevector <4 x float> %broadcast.splatinsert392, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert409 = insertelement <4 x float> poison, float %589, i64 0
  %broadcast.splat410 = shufflevector <4 x float> %broadcast.splatinsert409, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert411 = insertelement <4 x float> poison, float %588, i64 0
  %broadcast.splat412 = shufflevector <4 x float> %broadcast.splatinsert411, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert418 = insertelement <4 x float> poison, float %586, i64 0
  %broadcast.splat419 = shufflevector <4 x float> %broadcast.splatinsert418, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert420 = insertelement <4 x float> poison, float %585, i64 0
  %broadcast.splat421 = shufflevector <4 x float> %broadcast.splatinsert420, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert427 = insertelement <4 x float> poison, float %583, i64 0
  %broadcast.splat428 = shufflevector <4 x float> %broadcast.splatinsert427, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert429 = insertelement <4 x float> poison, float %582, i64 0
  %broadcast.splat430 = shufflevector <4 x float> %broadcast.splatinsert429, <4 x float> poison, <4 x i32> zeroinitializer
  %596 = fsub reassoc ninf nsz <4 x float> %broadcast.splat391, %577
  %597 = fadd reassoc ninf nsz <4 x float> %broadcast.splat393, %578
  %598 = fptosi <4 x float> %596 to <4 x i32>
  %599 = add <4 x i32> %broadcast.splat522, %598
  %600 = fptosi <4 x float> %597 to <4 x i32>
  %601 = add <4 x i32> %broadcast.splat465, %600
  %602 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %601)
  %603 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %602, <4 x i32> zeroinitializer)
  %604 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %599)
  %605 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %604, <4 x i32> zeroinitializer)
  %606 = mul <4 x i32> %broadcast.splat471, %603
  %607 = add <4 x i32> %606, %605
  %608 = sext <4 x i32> %607 to <4 x i64>
  %609 = getelementptr float, float* %273, <4 x i64> %608
  %wide.masked.gather404 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %609, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %610 = add <4 x i32> %599, <i32 1, i32 1, i32 1, i32 1>
  %611 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %610)
  %612 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %611, <4 x i32> zeroinitializer)
  %613 = add <4 x i32> %599, <i32 -1, i32 -1, i32 -1, i32 -1>
  %614 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %613)
  %615 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %614, <4 x i32> zeroinitializer)
  %616 = add <4 x i32> %606, %612
  %617 = sext <4 x i32> %616 to <4 x i64>
  %618 = getelementptr float, float* %273, <4 x i64> %617
  %wide.masked.gather405 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %618, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %619 = add <4 x i32> %606, %615
  %620 = sext <4 x i32> %619 to <4 x i64>
  %621 = getelementptr float, float* %273, <4 x i64> %620
  %wide.masked.gather406 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %621, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %622 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather405, %wide.masked.gather406
  %623 = fmul reassoc ninf nsz <4 x float> %622, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %624 = add <4 x i32> %601, <i32 1, i32 1, i32 1, i32 1>
  %625 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %624)
  %626 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %625, <4 x i32> zeroinitializer)
  %627 = add <4 x i32> %601, <i32 -1, i32 -1, i32 -1, i32 -1>
  %628 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %627)
  %629 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %628, <4 x i32> zeroinitializer)
  %630 = mul <4 x i32> %broadcast.splat471, %626
  %631 = add <4 x i32> %630, %605
  %632 = sext <4 x i32> %631 to <4 x i64>
  %633 = getelementptr float, float* %273, <4 x i64> %632
  %wide.masked.gather407 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %633, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %634 = mul <4 x i32> %broadcast.splat471, %629
  %635 = add <4 x i32> %634, %605
  %636 = sext <4 x i32> %635 to <4 x i64>
  %637 = getelementptr float, float* %273, <4 x i64> %636
  %wide.masked.gather408 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %637, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %638 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather407, %wide.masked.gather408
  %639 = fmul reassoc ninf nsz <4 x float> %638, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %640 = fmul reassoc ninf nsz <4 x float> %623, %broadcast.splat457
  %641 = fmul reassoc ninf nsz <4 x float> %639, %broadcast.splat455
  %642 = fadd reassoc ninf nsz <4 x float> %641, %640
  %643 = fmul reassoc ninf nsz <4 x float> %639, %broadcast.splat457
  %644 = fmul reassoc ninf nsz <4 x float> %623, %broadcast.splat455
  %645 = fsub reassoc ninf nsz <4 x float> %643, %644
  %646 = fadd reassoc ninf nsz <4 x float> %593, %wide.masked.gather404
  %647 = fadd reassoc ninf nsz <4 x float> %642, %594
  %648 = fadd reassoc ninf nsz <4 x float> %645, %595
  %649 = fsub reassoc ninf nsz <4 x float> %broadcast.splat410, %577
  %650 = fadd reassoc ninf nsz <4 x float> %broadcast.splat412, %578
  %651 = fptosi <4 x float> %649 to <4 x i32>
  %652 = add <4 x i32> %broadcast.splat522, %651
  %653 = fptosi <4 x float> %650 to <4 x i32>
  %654 = add <4 x i32> %broadcast.splat465, %653
  %655 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %654)
  %656 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %655, <4 x i32> zeroinitializer)
  %657 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %652)
  %658 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %657, <4 x i32> zeroinitializer)
  %659 = mul <4 x i32> %broadcast.splat471, %656
  %660 = add <4 x i32> %659, %658
  %661 = sext <4 x i32> %660 to <4 x i64>
  %662 = getelementptr float, float* %273, <4 x i64> %661
  %wide.masked.gather413 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %662, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %663 = add <4 x i32> %652, <i32 1, i32 1, i32 1, i32 1>
  %664 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %663)
  %665 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %664, <4 x i32> zeroinitializer)
  %666 = add <4 x i32> %652, <i32 -1, i32 -1, i32 -1, i32 -1>
  %667 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %666)
  %668 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %667, <4 x i32> zeroinitializer)
  %669 = add <4 x i32> %659, %665
  %670 = sext <4 x i32> %669 to <4 x i64>
  %671 = getelementptr float, float* %273, <4 x i64> %670
  %wide.masked.gather414 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %671, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %672 = add <4 x i32> %659, %668
  %673 = sext <4 x i32> %672 to <4 x i64>
  %674 = getelementptr float, float* %273, <4 x i64> %673
  %wide.masked.gather415 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %674, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %675 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather414, %wide.masked.gather415
  %676 = fmul reassoc ninf nsz <4 x float> %675, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %677 = add <4 x i32> %654, <i32 1, i32 1, i32 1, i32 1>
  %678 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %677)
  %679 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %678, <4 x i32> zeroinitializer)
  %680 = add <4 x i32> %654, <i32 -1, i32 -1, i32 -1, i32 -1>
  %681 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %680)
  %682 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %681, <4 x i32> zeroinitializer)
  %683 = mul <4 x i32> %broadcast.splat471, %679
  %684 = add <4 x i32> %683, %658
  %685 = sext <4 x i32> %684 to <4 x i64>
  %686 = getelementptr float, float* %273, <4 x i64> %685
  %wide.masked.gather416 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %686, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %687 = mul <4 x i32> %broadcast.splat471, %682
  %688 = add <4 x i32> %687, %658
  %689 = sext <4 x i32> %688 to <4 x i64>
  %690 = getelementptr float, float* %273, <4 x i64> %689
  %wide.masked.gather417 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %690, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %691 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather416, %wide.masked.gather417
  %692 = fmul reassoc ninf nsz <4 x float> %691, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %693 = fmul reassoc ninf nsz <4 x float> %676, %broadcast.splat457
  %694 = fmul reassoc ninf nsz <4 x float> %692, %broadcast.splat455
  %695 = fadd reassoc ninf nsz <4 x float> %694, %693
  %696 = fmul reassoc ninf nsz <4 x float> %692, %broadcast.splat457
  %697 = fmul reassoc ninf nsz <4 x float> %676, %broadcast.splat455
  %698 = fsub reassoc ninf nsz <4 x float> %696, %697
  %699 = fadd reassoc ninf nsz <4 x float> %646, %wide.masked.gather413
  %700 = fadd reassoc ninf nsz <4 x float> %695, %647
  %701 = fadd reassoc ninf nsz <4 x float> %698, %648
  %702 = fsub reassoc ninf nsz <4 x float> %broadcast.splat419, %577
  %703 = fadd reassoc ninf nsz <4 x float> %broadcast.splat421, %578
  %704 = fptosi <4 x float> %702 to <4 x i32>
  %705 = add <4 x i32> %broadcast.splat522, %704
  %706 = fptosi <4 x float> %703 to <4 x i32>
  %707 = add <4 x i32> %broadcast.splat465, %706
  %708 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %707)
  %709 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %708, <4 x i32> zeroinitializer)
  %710 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %705)
  %711 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %710, <4 x i32> zeroinitializer)
  %712 = mul <4 x i32> %broadcast.splat471, %709
  %713 = add <4 x i32> %712, %711
  %714 = sext <4 x i32> %713 to <4 x i64>
  %715 = getelementptr float, float* %273, <4 x i64> %714
  %wide.masked.gather422 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %715, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %716 = add <4 x i32> %705, <i32 1, i32 1, i32 1, i32 1>
  %717 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %716)
  %718 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %717, <4 x i32> zeroinitializer)
  %719 = add <4 x i32> %705, <i32 -1, i32 -1, i32 -1, i32 -1>
  %720 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %719)
  %721 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %720, <4 x i32> zeroinitializer)
  %722 = add <4 x i32> %712, %718
  %723 = sext <4 x i32> %722 to <4 x i64>
  %724 = getelementptr float, float* %273, <4 x i64> %723
  %wide.masked.gather423 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %724, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %725 = add <4 x i32> %712, %721
  %726 = sext <4 x i32> %725 to <4 x i64>
  %727 = getelementptr float, float* %273, <4 x i64> %726
  %wide.masked.gather424 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %727, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %728 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather423, %wide.masked.gather424
  %729 = fmul reassoc ninf nsz <4 x float> %728, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %730 = add <4 x i32> %707, <i32 1, i32 1, i32 1, i32 1>
  %731 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %730)
  %732 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %731, <4 x i32> zeroinitializer)
  %733 = add <4 x i32> %707, <i32 -1, i32 -1, i32 -1, i32 -1>
  %734 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %733)
  %735 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %734, <4 x i32> zeroinitializer)
  %736 = mul <4 x i32> %broadcast.splat471, %732
  %737 = add <4 x i32> %736, %711
  %738 = sext <4 x i32> %737 to <4 x i64>
  %739 = getelementptr float, float* %273, <4 x i64> %738
  %wide.masked.gather425 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %739, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %740 = mul <4 x i32> %broadcast.splat471, %735
  %741 = add <4 x i32> %740, %711
  %742 = sext <4 x i32> %741 to <4 x i64>
  %743 = getelementptr float, float* %273, <4 x i64> %742
  %wide.masked.gather426 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %743, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %744 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather425, %wide.masked.gather426
  %745 = fmul reassoc ninf nsz <4 x float> %744, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %746 = fmul reassoc ninf nsz <4 x float> %729, %broadcast.splat457
  %747 = fmul reassoc ninf nsz <4 x float> %745, %broadcast.splat455
  %748 = fadd reassoc ninf nsz <4 x float> %747, %746
  %749 = fmul reassoc ninf nsz <4 x float> %745, %broadcast.splat457
  %750 = fmul reassoc ninf nsz <4 x float> %729, %broadcast.splat455
  %751 = fsub reassoc ninf nsz <4 x float> %749, %750
  %752 = fadd reassoc ninf nsz <4 x float> %699, %wide.masked.gather422
  %753 = fadd reassoc ninf nsz <4 x float> %748, %700
  %754 = fadd reassoc ninf nsz <4 x float> %751, %701
  %755 = fsub reassoc ninf nsz <4 x float> %broadcast.splat428, %577
  %756 = fadd reassoc ninf nsz <4 x float> %broadcast.splat430, %578
  %757 = fptosi <4 x float> %755 to <4 x i32>
  %758 = add <4 x i32> %broadcast.splat522, %757
  %759 = fptosi <4 x float> %756 to <4 x i32>
  %760 = add <4 x i32> %broadcast.splat465, %759
  %761 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %760)
  %762 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %761, <4 x i32> zeroinitializer)
  %763 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %758)
  %764 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %763, <4 x i32> zeroinitializer)
  %765 = mul <4 x i32> %broadcast.splat471, %762
  %766 = add <4 x i32> %765, %764
  %767 = sext <4 x i32> %766 to <4 x i64>
  %768 = getelementptr float, float* %273, <4 x i64> %767
  %wide.masked.gather431 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %768, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %769 = add <4 x i32> %758, <i32 1, i32 1, i32 1, i32 1>
  %770 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %769)
  %771 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %770, <4 x i32> zeroinitializer)
  %772 = add <4 x i32> %758, <i32 -1, i32 -1, i32 -1, i32 -1>
  %773 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %772)
  %774 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %773, <4 x i32> zeroinitializer)
  %775 = add <4 x i32> %765, %771
  %776 = sext <4 x i32> %775 to <4 x i64>
  %777 = getelementptr float, float* %273, <4 x i64> %776
  %wide.masked.gather432 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %777, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %778 = add <4 x i32> %765, %774
  %779 = sext <4 x i32> %778 to <4 x i64>
  %780 = getelementptr float, float* %273, <4 x i64> %779
  %wide.masked.gather433 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %780, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %781 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather432, %wide.masked.gather433
  %782 = fmul reassoc ninf nsz <4 x float> %781, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %783 = add <4 x i32> %760, <i32 1, i32 1, i32 1, i32 1>
  %784 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %783)
  %785 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %784, <4 x i32> zeroinitializer)
  %786 = add <4 x i32> %760, <i32 -1, i32 -1, i32 -1, i32 -1>
  %787 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %786)
  %788 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %787, <4 x i32> zeroinitializer)
  %789 = mul <4 x i32> %broadcast.splat471, %785
  %790 = add <4 x i32> %789, %764
  %791 = sext <4 x i32> %790 to <4 x i64>
  %792 = getelementptr float, float* %273, <4 x i64> %791
  %wide.masked.gather434 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %792, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %793 = mul <4 x i32> %broadcast.splat471, %788
  %794 = add <4 x i32> %793, %764
  %795 = sext <4 x i32> %794 to <4 x i64>
  %796 = getelementptr float, float* %273, <4 x i64> %795
  %wide.masked.gather435 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %796, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %797 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather434, %wide.masked.gather435
  %798 = fmul reassoc ninf nsz <4 x float> %797, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %799 = fmul reassoc ninf nsz <4 x float> %782, %broadcast.splat457
  %800 = fmul reassoc ninf nsz <4 x float> %798, %broadcast.splat455
  %801 = fadd reassoc ninf nsz <4 x float> %800, %799
  %802 = fmul reassoc ninf nsz <4 x float> %798, %broadcast.splat457
  %803 = fmul reassoc ninf nsz <4 x float> %782, %broadcast.splat455
  %804 = fsub reassoc ninf nsz <4 x float> %802, %803
  %805 = fadd reassoc ninf nsz <4 x float> %752, %wide.masked.gather431
  %806 = fadd reassoc ninf nsz <4 x float> %801, %753
  %807 = fadd reassoc ninf nsz <4 x float> %804, %754
  %808 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %807)
  %809 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %806)
  %810 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %805)
  store float %810, float* %scevgep563, align 4
  store float %809, float* %scevgep566, align 4
  store float %808, float* %scevgep569, align 4
  %indvars.iv.next255 = add nuw nsw i64 %indvars.iv254, 1
  %exitcond257.not = icmp eq i64 %indvars.iv.next255, 3
  br i1 %exitcond257.not, label %after_for69, label %for_loop_body67

after_for69:                                      ; preds = %for_loop_body67
  %indvars.iv.next259 = add nuw nsw i64 %indvars.iv258, 1
  %scevgep562 = getelementptr [9 x float], [9 x float]* %lsr.iv561, i64 0, i64 3
  %811 = bitcast float* %scevgep562 to [9 x float]*
  %scevgep565 = getelementptr [9 x float], [9 x float]* %lsr.iv564, i64 0, i64 3
  %812 = bitcast float* %scevgep565 to [9 x float]*
  %scevgep568 = getelementptr [9 x float], [9 x float]* %lsr.iv567, i64 0, i64 3
  %813 = bitcast float* %scevgep568 to [9 x float]*
  %exitcond261.not = icmp eq i64 %indvars.iv.next259, 3
  br i1 %exitcond261.not, label %for_loop_body80.preheader, label %for_loop_body63

for_loop_body80.preheader:                        ; preds = %after_for69
  br label %for_loop_body80

for_loop_body80:                                  ; preds = %for_loop_test83.loopexit, %for_loop_body80.preheader
  %indvars.iv268 = phi i64 [ %indvars.iv.next269, %for_loop_test83.loopexit ], [ 0, %for_loop_body80.preheader ]
  %.2192 = phi i32 [ %.3.lcssa, %for_loop_test83.loopexit ], [ %.1.lcssa, %for_loop_body80.preheader ]
  %indvars.iv.next269 = add nuw nsw i64 %indvars.iv268, 1
  %814 = icmp ult i64 %indvars.iv268, 8
  br i1 %814, label %for_loop_body84.lr.ph, label %for_loop_test83.loopexit

for_loop_body84.lr.ph:                            ; preds = %for_loop_body80
  %815 = getelementptr [9 x float], [9 x float]* %7, i64 0, i64 %indvars.iv268
  %816 = load float, float* %815, align 4
  %817 = getelementptr [9 x float], [9 x float]* %8, i64 0, i64 %indvars.iv268
  %818 = load float, float* %817, align 4
  %819 = getelementptr [9 x float], [9 x float]* %9, i64 0, i64 %indvars.iv268
  %820 = load float, float* %819, align 4
  br label %for_loop_body84

after_for82:                                      ; preds = %for_loop_test83.loopexit
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(64) %55, i8 0, i64 64, i1 false)
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(64) %56, i8 0, i64 64, i1 false)
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(64) %57, i8 0, i64 64, i1 false)
  br label %for_loop_body97

for_loop_test83.loopexit.loopexit:                ; preds = %after_if96
  br label %for_loop_test83.loopexit

for_loop_test83.loopexit:                         ; preds = %for_loop_test83.loopexit.loopexit, %for_loop_body80
  %.3.lcssa = phi i32 [ %.2192, %for_loop_body80 ], [ %867, %for_loop_test83.loopexit.loopexit ]
  %exitcond271.not = icmp eq i64 %indvars.iv.next269, 9
  br i1 %exitcond271.not, label %after_for82, label %for_loop_body80

for_loop_body84:                                  ; preds = %after_if96, %for_loop_body84.lr.ph
  %lsr.iv571 = phi i64 [ %indvars.iv268, %for_loop_body84.lr.ph ], [ %lsr.iv.next, %after_if96 ]
  %.3189 = phi i32 [ %.2192, %for_loop_body84.lr.ph ], [ %867, %after_if96 ]
  %scevgep576 = getelementptr float, float* %scevgep575, i64 %lsr.iv571
  %821 = load float, float* %scevgep576, align 4
  %822 = fcmp reassoc ninf nsz ogt float %816, %821
  br i1 %822, label %true_block88, label %after_if90

true_block88:                                     ; preds = %for_loop_body84
  %823 = sdiv i32 %.3189, 32
  %824 = icmp slt i32 %.3189, 0
  %825 = shl nsw i32 %823, 5
  %826 = icmp ne i32 %.3189, %825
  %827 = and i1 %824, %826
  %.neg132 = sext i1 %827 to i32
  %828 = add nsw i32 %823, %.neg132
  %.neg133 = mul i32 %828, -32
  %829 = add i32 %.3189, %.neg133
  %830 = shl nuw i32 1, %829
  %831 = sext i32 %828 to i64
  %832 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %831
  %833 = load i32, i32* %832, align 4
  %834 = or i32 %833, %830
  store i32 %834, i32* %832, align 4
  br label %after_if90

after_if90:                                       ; preds = %true_block88, %for_loop_body84
  %scevgep574 = getelementptr float, float* %scevgep573, i64 %lsr.iv571
  %835 = load float, float* %scevgep574, align 4
  %836 = fcmp reassoc ninf nsz ogt float %818, %835
  br i1 %836, label %true_block91, label %after_if93

true_block91:                                     ; preds = %after_if90
  %837 = add i32 %.3189, 1
  %838 = sdiv i32 %837, 32
  %839 = icmp slt i32 %837, 0
  %840 = shl nsw i32 %838, 5
  %841 = icmp ne i32 %837, %840
  %842 = and i1 %839, %841
  %.neg130 = sext i1 %842 to i32
  %843 = add nsw i32 %838, %.neg130
  %.neg131 = mul i32 %843, -32
  %844 = add i32 %.3189, %.neg131
  %845 = add i32 %844, 1
  %846 = shl nuw i32 1, %845
  %847 = sext i32 %843 to i64
  %848 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %847
  %849 = load i32, i32* %848, align 4
  %850 = or i32 %849, %846
  store i32 %850, i32* %848, align 4
  br label %after_if93

after_if93:                                       ; preds = %true_block91, %after_if90
  %scevgep572 = getelementptr float, float* %scevgep570, i64 %lsr.iv571
  %851 = load float, float* %scevgep572, align 4
  %852 = fcmp reassoc ninf nsz ogt float %820, %851
  br i1 %852, label %true_block94, label %after_if96

true_block94:                                     ; preds = %after_if93
  %853 = add i32 %.3189, 2
  %854 = sdiv i32 %853, 32
  %855 = icmp slt i32 %853, 0
  %856 = shl nsw i32 %854, 5
  %857 = icmp ne i32 %853, %856
  %858 = and i1 %855, %857
  %.neg128 = sext i1 %858 to i32
  %859 = add nsw i32 %854, %.neg128
  %.neg129 = mul i32 %859, -32
  %860 = add i32 %.3189, %.neg129
  %861 = add i32 %860, 2
  %862 = shl nuw i32 1, %861
  %863 = sext i32 %859 to i64
  %864 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %863
  %865 = load i32, i32* %864, align 4
  %866 = or i32 %865, %862
  store i32 %866, i32* %864, align 4
  br label %after_if96

after_if96:                                       ; preds = %true_block94, %after_if93
  %867 = add i32 %.3189, 3
  %lsr.iv.next = add nuw nsw i64 %lsr.iv571, 1
  %exitcond267.not = icmp eq i64 %lsr.iv.next, 8
  br i1 %exitcond267.not, label %for_loop_test83.loopexit.loopexit, label %for_loop_body84

for_loop_body97:                                  ; preds = %after_for103, %after_for82
  %lsr.iv584 = phi [16 x float]* [ %12, %after_for82 ], [ %1109, %after_for103 ]
  %lsr.iv581 = phi [16 x float]* [ %11, %after_for82 ], [ %1108, %after_for103 ]
  %lsr.iv578 = phi [16 x float]* [ %10, %after_for82 ], [ %1107, %after_for103 ]
  %indvars.iv278 = phi i64 [ 0, %after_for82 ], [ %indvars.iv.next279, %after_for103 ]
  %868 = trunc i64 %indvars.iv278 to i32
  %869 = sitofp i32 %868 to float
  %870 = fmul reassoc ninf nsz float %869, 5.000000e+00
  %871 = fadd reassoc ninf nsz float %870, -9.375000e+00
  %broadcast.splatinsert = insertelement <4 x float> poison, float %871, i64 0
  %broadcast.splat = shufflevector <4 x float> %broadcast.splatinsert, <4 x float> poison, <4 x i32> zeroinitializer
  %872 = fadd reassoc ninf nsz <4 x float> %broadcast.splat, <float 0.000000e+00, float 1.250000e+00, float 2.500000e+00, float 3.750000e+00>
  %873 = fmul reassoc ninf nsz <4 x float> %872, %broadcast.splat455
  %874 = fmul reassoc ninf nsz <4 x float> %872, %broadcast.splat457
  br label %for_loop_body101

for_loop_body101:                                 ; preds = %for_loop_body101, %for_loop_body97
  %indvars.iv274 = phi i64 [ 0, %for_loop_body97 ], [ %indvars.iv.next275, %for_loop_body101 ]
  %scevgep580 = getelementptr [16 x float], [16 x float]* %lsr.iv578, i64 0, i64 %indvars.iv274
  %scevgep583 = getelementptr [16 x float], [16 x float]* %lsr.iv581, i64 0, i64 %indvars.iv274
  %scevgep586 = getelementptr [16 x float], [16 x float]* %lsr.iv584, i64 0, i64 %indvars.iv274
  %tmp577 = trunc i64 %indvars.iv274 to i32
  %875 = sitofp i32 %tmp577 to float
  %876 = fmul reassoc ninf nsz float %875, 5.000000e+00
  %877 = fadd reassoc ninf nsz float %876, -5.625000e+00
  %878 = fmul reassoc ninf nsz float %877, %268
  %879 = fmul reassoc ninf nsz float %877, %267
  %880 = fadd reassoc ninf nsz float %876, -6.875000e+00
  %881 = fmul reassoc ninf nsz float %880, %268
  %882 = fmul reassoc ninf nsz float %880, %267
  %883 = fadd reassoc ninf nsz float %876, -8.125000e+00
  %884 = fmul reassoc ninf nsz float %883, %268
  %885 = fmul reassoc ninf nsz float %883, %267
  %886 = fadd reassoc ninf nsz float %876, -9.375000e+00
  %887 = fmul reassoc ninf nsz float %886, %268
  %888 = fmul reassoc ninf nsz float %886, %267
  %.promoted205 = load float, float* %scevgep586, align 4
  %.promoted203 = load float, float* %scevgep583, align 4
  %.promoted201 = load float, float* %scevgep580, align 4
  %889 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted201, i64 0
  %890 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted203, i64 0
  %891 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.promoted205, i64 0
  %broadcast.splatinsert325 = insertelement <4 x float> poison, float %888, i64 0
  %broadcast.splat326 = shufflevector <4 x float> %broadcast.splatinsert325, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert327 = insertelement <4 x float> poison, float %887, i64 0
  %broadcast.splat328 = shufflevector <4 x float> %broadcast.splatinsert327, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert343 = insertelement <4 x float> poison, float %885, i64 0
  %broadcast.splat344 = shufflevector <4 x float> %broadcast.splatinsert343, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert345 = insertelement <4 x float> poison, float %884, i64 0
  %broadcast.splat346 = shufflevector <4 x float> %broadcast.splatinsert345, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert352 = insertelement <4 x float> poison, float %882, i64 0
  %broadcast.splat353 = shufflevector <4 x float> %broadcast.splatinsert352, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert354 = insertelement <4 x float> poison, float %881, i64 0
  %broadcast.splat355 = shufflevector <4 x float> %broadcast.splatinsert354, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert361 = insertelement <4 x float> poison, float %879, i64 0
  %broadcast.splat362 = shufflevector <4 x float> %broadcast.splatinsert361, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert363 = insertelement <4 x float> poison, float %878, i64 0
  %broadcast.splat364 = shufflevector <4 x float> %broadcast.splatinsert363, <4 x float> poison, <4 x i32> zeroinitializer
  %892 = fsub reassoc ninf nsz <4 x float> %broadcast.splat326, %873
  %893 = fadd reassoc ninf nsz <4 x float> %broadcast.splat328, %874
  %894 = fptosi <4 x float> %892 to <4 x i32>
  %895 = add <4 x i32> %broadcast.splat522, %894
  %896 = fptosi <4 x float> %893 to <4 x i32>
  %897 = add <4 x i32> %broadcast.splat465, %896
  %898 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %897)
  %899 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %898, <4 x i32> zeroinitializer)
  %900 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %895)
  %901 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %900, <4 x i32> zeroinitializer)
  %902 = mul <4 x i32> %broadcast.splat471, %899
  %903 = add <4 x i32> %902, %901
  %904 = sext <4 x i32> %903 to <4 x i64>
  %905 = getelementptr float, float* %273, <4 x i64> %904
  %wide.masked.gather = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %905, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %906 = add <4 x i32> %895, <i32 1, i32 1, i32 1, i32 1>
  %907 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %906)
  %908 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %907, <4 x i32> zeroinitializer)
  %909 = add <4 x i32> %895, <i32 -1, i32 -1, i32 -1, i32 -1>
  %910 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %909)
  %911 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %910, <4 x i32> zeroinitializer)
  %912 = add <4 x i32> %902, %908
  %913 = sext <4 x i32> %912 to <4 x i64>
  %914 = getelementptr float, float* %273, <4 x i64> %913
  %wide.masked.gather339 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %914, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %915 = add <4 x i32> %902, %911
  %916 = sext <4 x i32> %915 to <4 x i64>
  %917 = getelementptr float, float* %273, <4 x i64> %916
  %wide.masked.gather340 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %917, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %918 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather339, %wide.masked.gather340
  %919 = fmul reassoc ninf nsz <4 x float> %918, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %920 = add <4 x i32> %897, <i32 1, i32 1, i32 1, i32 1>
  %921 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %920)
  %922 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %921, <4 x i32> zeroinitializer)
  %923 = add <4 x i32> %897, <i32 -1, i32 -1, i32 -1, i32 -1>
  %924 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %923)
  %925 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %924, <4 x i32> zeroinitializer)
  %926 = mul <4 x i32> %broadcast.splat471, %922
  %927 = add <4 x i32> %926, %901
  %928 = sext <4 x i32> %927 to <4 x i64>
  %929 = getelementptr float, float* %273, <4 x i64> %928
  %wide.masked.gather341 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %929, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %930 = mul <4 x i32> %broadcast.splat471, %925
  %931 = add <4 x i32> %930, %901
  %932 = sext <4 x i32> %931 to <4 x i64>
  %933 = getelementptr float, float* %273, <4 x i64> %932
  %wide.masked.gather342 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %933, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %934 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather341, %wide.masked.gather342
  %935 = fmul reassoc ninf nsz <4 x float> %934, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %936 = fmul reassoc ninf nsz <4 x float> %919, %broadcast.splat457
  %937 = fmul reassoc ninf nsz <4 x float> %935, %broadcast.splat455
  %938 = fadd reassoc ninf nsz <4 x float> %937, %936
  %939 = fmul reassoc ninf nsz <4 x float> %935, %broadcast.splat457
  %940 = fmul reassoc ninf nsz <4 x float> %919, %broadcast.splat455
  %941 = fsub reassoc ninf nsz <4 x float> %939, %940
  %942 = fadd reassoc ninf nsz <4 x float> %889, %wide.masked.gather
  %943 = fadd reassoc ninf nsz <4 x float> %938, %890
  %944 = fadd reassoc ninf nsz <4 x float> %941, %891
  %945 = fsub reassoc ninf nsz <4 x float> %broadcast.splat344, %873
  %946 = fadd reassoc ninf nsz <4 x float> %broadcast.splat346, %874
  %947 = fptosi <4 x float> %945 to <4 x i32>
  %948 = add <4 x i32> %broadcast.splat522, %947
  %949 = fptosi <4 x float> %946 to <4 x i32>
  %950 = add <4 x i32> %broadcast.splat465, %949
  %951 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %950)
  %952 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %951, <4 x i32> zeroinitializer)
  %953 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %948)
  %954 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %953, <4 x i32> zeroinitializer)
  %955 = mul <4 x i32> %broadcast.splat471, %952
  %956 = add <4 x i32> %955, %954
  %957 = sext <4 x i32> %956 to <4 x i64>
  %958 = getelementptr float, float* %273, <4 x i64> %957
  %wide.masked.gather347 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %958, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %959 = add <4 x i32> %948, <i32 1, i32 1, i32 1, i32 1>
  %960 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %959)
  %961 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %960, <4 x i32> zeroinitializer)
  %962 = add <4 x i32> %948, <i32 -1, i32 -1, i32 -1, i32 -1>
  %963 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %962)
  %964 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %963, <4 x i32> zeroinitializer)
  %965 = add <4 x i32> %955, %961
  %966 = sext <4 x i32> %965 to <4 x i64>
  %967 = getelementptr float, float* %273, <4 x i64> %966
  %wide.masked.gather348 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %967, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %968 = add <4 x i32> %955, %964
  %969 = sext <4 x i32> %968 to <4 x i64>
  %970 = getelementptr float, float* %273, <4 x i64> %969
  %wide.masked.gather349 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %970, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %971 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather348, %wide.masked.gather349
  %972 = fmul reassoc ninf nsz <4 x float> %971, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %973 = add <4 x i32> %950, <i32 1, i32 1, i32 1, i32 1>
  %974 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %973)
  %975 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %974, <4 x i32> zeroinitializer)
  %976 = add <4 x i32> %950, <i32 -1, i32 -1, i32 -1, i32 -1>
  %977 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %976)
  %978 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %977, <4 x i32> zeroinitializer)
  %979 = mul <4 x i32> %broadcast.splat471, %975
  %980 = add <4 x i32> %979, %954
  %981 = sext <4 x i32> %980 to <4 x i64>
  %982 = getelementptr float, float* %273, <4 x i64> %981
  %wide.masked.gather350 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %982, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %983 = mul <4 x i32> %broadcast.splat471, %978
  %984 = add <4 x i32> %983, %954
  %985 = sext <4 x i32> %984 to <4 x i64>
  %986 = getelementptr float, float* %273, <4 x i64> %985
  %wide.masked.gather351 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %986, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %987 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather350, %wide.masked.gather351
  %988 = fmul reassoc ninf nsz <4 x float> %987, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %989 = fmul reassoc ninf nsz <4 x float> %972, %broadcast.splat457
  %990 = fmul reassoc ninf nsz <4 x float> %988, %broadcast.splat455
  %991 = fadd reassoc ninf nsz <4 x float> %990, %989
  %992 = fmul reassoc ninf nsz <4 x float> %988, %broadcast.splat457
  %993 = fmul reassoc ninf nsz <4 x float> %972, %broadcast.splat455
  %994 = fsub reassoc ninf nsz <4 x float> %992, %993
  %995 = fadd reassoc ninf nsz <4 x float> %942, %wide.masked.gather347
  %996 = fadd reassoc ninf nsz <4 x float> %991, %943
  %997 = fadd reassoc ninf nsz <4 x float> %994, %944
  %998 = fsub reassoc ninf nsz <4 x float> %broadcast.splat353, %873
  %999 = fadd reassoc ninf nsz <4 x float> %broadcast.splat355, %874
  %1000 = fptosi <4 x float> %998 to <4 x i32>
  %1001 = add <4 x i32> %broadcast.splat522, %1000
  %1002 = fptosi <4 x float> %999 to <4 x i32>
  %1003 = add <4 x i32> %broadcast.splat465, %1002
  %1004 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %1003)
  %1005 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1004, <4 x i32> zeroinitializer)
  %1006 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %1001)
  %1007 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1006, <4 x i32> zeroinitializer)
  %1008 = mul <4 x i32> %broadcast.splat471, %1005
  %1009 = add <4 x i32> %1008, %1007
  %1010 = sext <4 x i32> %1009 to <4 x i64>
  %1011 = getelementptr float, float* %273, <4 x i64> %1010
  %wide.masked.gather356 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1011, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1012 = add <4 x i32> %1001, <i32 1, i32 1, i32 1, i32 1>
  %1013 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %1012)
  %1014 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1013, <4 x i32> zeroinitializer)
  %1015 = add <4 x i32> %1001, <i32 -1, i32 -1, i32 -1, i32 -1>
  %1016 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %1015)
  %1017 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1016, <4 x i32> zeroinitializer)
  %1018 = add <4 x i32> %1008, %1014
  %1019 = sext <4 x i32> %1018 to <4 x i64>
  %1020 = getelementptr float, float* %273, <4 x i64> %1019
  %wide.masked.gather357 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1020, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1021 = add <4 x i32> %1008, %1017
  %1022 = sext <4 x i32> %1021 to <4 x i64>
  %1023 = getelementptr float, float* %273, <4 x i64> %1022
  %wide.masked.gather358 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1023, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1024 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather357, %wide.masked.gather358
  %1025 = fmul reassoc ninf nsz <4 x float> %1024, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %1026 = add <4 x i32> %1003, <i32 1, i32 1, i32 1, i32 1>
  %1027 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %1026)
  %1028 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1027, <4 x i32> zeroinitializer)
  %1029 = add <4 x i32> %1003, <i32 -1, i32 -1, i32 -1, i32 -1>
  %1030 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %1029)
  %1031 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1030, <4 x i32> zeroinitializer)
  %1032 = mul <4 x i32> %broadcast.splat471, %1028
  %1033 = add <4 x i32> %1032, %1007
  %1034 = sext <4 x i32> %1033 to <4 x i64>
  %1035 = getelementptr float, float* %273, <4 x i64> %1034
  %wide.masked.gather359 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1035, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1036 = mul <4 x i32> %broadcast.splat471, %1031
  %1037 = add <4 x i32> %1036, %1007
  %1038 = sext <4 x i32> %1037 to <4 x i64>
  %1039 = getelementptr float, float* %273, <4 x i64> %1038
  %wide.masked.gather360 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1039, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1040 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather359, %wide.masked.gather360
  %1041 = fmul reassoc ninf nsz <4 x float> %1040, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %1042 = fmul reassoc ninf nsz <4 x float> %1025, %broadcast.splat457
  %1043 = fmul reassoc ninf nsz <4 x float> %1041, %broadcast.splat455
  %1044 = fadd reassoc ninf nsz <4 x float> %1043, %1042
  %1045 = fmul reassoc ninf nsz <4 x float> %1041, %broadcast.splat457
  %1046 = fmul reassoc ninf nsz <4 x float> %1025, %broadcast.splat455
  %1047 = fsub reassoc ninf nsz <4 x float> %1045, %1046
  %1048 = fadd reassoc ninf nsz <4 x float> %995, %wide.masked.gather356
  %1049 = fadd reassoc ninf nsz <4 x float> %1044, %996
  %1050 = fadd reassoc ninf nsz <4 x float> %1047, %997
  %1051 = fsub reassoc ninf nsz <4 x float> %broadcast.splat362, %873
  %1052 = fadd reassoc ninf nsz <4 x float> %broadcast.splat364, %874
  %1053 = fptosi <4 x float> %1051 to <4 x i32>
  %1054 = add <4 x i32> %broadcast.splat522, %1053
  %1055 = fptosi <4 x float> %1052 to <4 x i32>
  %1056 = add <4 x i32> %broadcast.splat465, %1055
  %1057 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %1056)
  %1058 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1057, <4 x i32> zeroinitializer)
  %1059 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %1054)
  %1060 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1059, <4 x i32> zeroinitializer)
  %1061 = mul <4 x i32> %broadcast.splat471, %1058
  %1062 = add <4 x i32> %1061, %1060
  %1063 = sext <4 x i32> %1062 to <4 x i64>
  %1064 = getelementptr float, float* %273, <4 x i64> %1063
  %wide.masked.gather365 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1064, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1065 = add <4 x i32> %1054, <i32 1, i32 1, i32 1, i32 1>
  %1066 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %1065)
  %1067 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1066, <4 x i32> zeroinitializer)
  %1068 = add <4 x i32> %1054, <i32 -1, i32 -1, i32 -1, i32 -1>
  %1069 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat469, <4 x i32> %1068)
  %1070 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1069, <4 x i32> zeroinitializer)
  %1071 = add <4 x i32> %1061, %1067
  %1072 = sext <4 x i32> %1071 to <4 x i64>
  %1073 = getelementptr float, float* %273, <4 x i64> %1072
  %wide.masked.gather366 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1073, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1074 = add <4 x i32> %1061, %1070
  %1075 = sext <4 x i32> %1074 to <4 x i64>
  %1076 = getelementptr float, float* %273, <4 x i64> %1075
  %wide.masked.gather367 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1076, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1077 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather366, %wide.masked.gather367
  %1078 = fmul reassoc ninf nsz <4 x float> %1077, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %1079 = add <4 x i32> %1056, <i32 1, i32 1, i32 1, i32 1>
  %1080 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %1079)
  %1081 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1080, <4 x i32> zeroinitializer)
  %1082 = add <4 x i32> %1056, <i32 -1, i32 -1, i32 -1, i32 -1>
  %1083 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat467, <4 x i32> %1082)
  %1084 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %1083, <4 x i32> zeroinitializer)
  %1085 = mul <4 x i32> %broadcast.splat471, %1081
  %1086 = add <4 x i32> %1085, %1060
  %1087 = sext <4 x i32> %1086 to <4 x i64>
  %1088 = getelementptr float, float* %273, <4 x i64> %1087
  %wide.masked.gather368 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1088, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1089 = mul <4 x i32> %broadcast.splat471, %1084
  %1090 = add <4 x i32> %1089, %1060
  %1091 = sext <4 x i32> %1090 to <4 x i64>
  %1092 = getelementptr float, float* %273, <4 x i64> %1091
  %wide.masked.gather369 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %1092, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %1093 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather368, %wide.masked.gather369
  %1094 = fmul reassoc ninf nsz <4 x float> %1093, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %1095 = fmul reassoc ninf nsz <4 x float> %1078, %broadcast.splat457
  %1096 = fmul reassoc ninf nsz <4 x float> %1094, %broadcast.splat455
  %1097 = fadd reassoc ninf nsz <4 x float> %1096, %1095
  %1098 = fmul reassoc ninf nsz <4 x float> %1094, %broadcast.splat457
  %1099 = fmul reassoc ninf nsz <4 x float> %1078, %broadcast.splat455
  %1100 = fsub reassoc ninf nsz <4 x float> %1098, %1099
  %1101 = fadd reassoc ninf nsz <4 x float> %1048, %wide.masked.gather365
  %1102 = fadd reassoc ninf nsz <4 x float> %1097, %1049
  %1103 = fadd reassoc ninf nsz <4 x float> %1100, %1050
  %1104 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %1103)
  %1105 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %1102)
  %1106 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %1101)
  store float %1106, float* %scevgep580, align 4
  store float %1105, float* %scevgep583, align 4
  store float %1104, float* %scevgep586, align 4
  %indvars.iv.next275 = add nuw nsw i64 %indvars.iv274, 1
  %exitcond277.not = icmp eq i64 %indvars.iv.next275, 4
  br i1 %exitcond277.not, label %after_for103, label %for_loop_body101

after_for103:                                     ; preds = %for_loop_body101
  %indvars.iv.next279 = add nuw nsw i64 %indvars.iv278, 1
  %scevgep579 = getelementptr [16 x float], [16 x float]* %lsr.iv578, i64 0, i64 4
  %1107 = bitcast float* %scevgep579 to [16 x float]*
  %scevgep582 = getelementptr [16 x float], [16 x float]* %lsr.iv581, i64 0, i64 4
  %1108 = bitcast float* %scevgep582 to [16 x float]*
  %scevgep585 = getelementptr [16 x float], [16 x float]* %lsr.iv584, i64 0, i64 4
  %1109 = bitcast float* %scevgep585 to [16 x float]*
  %exitcond281.not = icmp eq i64 %indvars.iv.next279, 4
  br i1 %exitcond281.not, label %for_loop_body114.preheader, label %for_loop_body97

for_loop_body114.preheader:                       ; preds = %after_for103
  br label %for_loop_body114

for_loop_body114:                                 ; preds = %for_loop_test117.loopexit, %for_loop_body114.preheader
  %indvars.iv288 = phi i64 [ %indvars.iv.next289, %for_loop_test117.loopexit ], [ 0, %for_loop_body114.preheader ]
  %indvars.iv282 = phi i64 [ %indvars.iv.next283, %for_loop_test117.loopexit ], [ 1, %for_loop_body114.preheader ]
  %.4216 = phi i32 [ %.5.lcssa, %for_loop_test117.loopexit ], [ %.3.lcssa, %for_loop_body114.preheader ]
  %indvars.iv.next289 = add nuw nsw i64 %indvars.iv288, 1
  %1110 = icmp ult i64 %indvars.iv288, 15
  br i1 %1110, label %for_loop_body118.lr.ph, label %for_loop_test117.loopexit

for_loop_body118.lr.ph:                           ; preds = %for_loop_body114
  %1111 = getelementptr [16 x float], [16 x float]* %10, i64 0, i64 %indvars.iv288
  %1112 = load float, float* %1111, align 4
  %1113 = getelementptr [16 x float], [16 x float]* %11, i64 0, i64 %indvars.iv288
  %1114 = load float, float* %1113, align 4
  %1115 = getelementptr [16 x float], [16 x float]* %12, i64 0, i64 %indvars.iv288
  %1116 = load float, float* %1115, align 4
  br label %for_loop_body118

for_loop_test117.loopexit.loopexit:               ; preds = %after_if130
  br label %for_loop_test117.loopexit

for_loop_test117.loopexit:                        ; preds = %for_loop_test117.loopexit.loopexit, %for_loop_body114
  %.5.lcssa = phi i32 [ %.4216, %for_loop_body114 ], [ %1276, %for_loop_test117.loopexit.loopexit ]
  %indvars.iv.next283 = add nuw nsw i64 %indvars.iv282, 1
  %exitcond291.not = icmp eq i64 %indvars.iv.next289, 16
  br i1 %exitcond291.not, label %for_loop_test134.preheader, label %for_loop_body114

for_loop_test134.preheader:                       ; preds = %for_loop_test117.loopexit
  %1117 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %269, i64 0, i32 3, i32 1
  %1118 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %269, i64 0, i32 3, i32 0, i32 1
  %1119 = load i32, i32* %47, align 4
  %1120 = load i32*, i32** %1117, align 8
  %1121 = load i32, i32* %1118, align 4
  %1122 = mul i32 %1121, %.0115219
  %1123 = sext i32 %1122 to i64
  %1124 = getelementptr i32, i32* %1120, i64 %1123
  store i32 %1119, i32* %1124, align 4
  %1125 = load i32, i32* %46, align 4
  %1126 = load i32*, i32** %1117, align 8
  %1127 = load i32, i32* %1118, align 4
  %1128 = mul i32 %1127, %.0115219
  %1129 = add i32 %1128, 1
  %1130 = sext i32 %1129 to i64
  %1131 = getelementptr i32, i32* %1126, i64 %1130
  store i32 %1125, i32* %1131, align 4
  %1132 = load i32, i32* %45, align 4
  %1133 = load i32*, i32** %1117, align 8
  %1134 = load i32, i32* %1118, align 4
  %1135 = mul i32 %1134, %.0115219
  %1136 = add i32 %1135, 2
  %1137 = sext i32 %1136 to i64
  %1138 = getelementptr i32, i32* %1133, i64 %1137
  store i32 %1132, i32* %1138, align 4
  %1139 = load i32, i32* %44, align 4
  %1140 = load i32*, i32** %1117, align 8
  %1141 = load i32, i32* %1118, align 4
  %1142 = mul i32 %1141, %.0115219
  %1143 = add i32 %1142, 3
  %1144 = sext i32 %1143 to i64
  %1145 = getelementptr i32, i32* %1140, i64 %1144
  store i32 %1139, i32* %1145, align 4
  %1146 = load i32, i32* %43, align 4
  %1147 = load i32*, i32** %1117, align 8
  %1148 = load i32, i32* %1118, align 4
  %1149 = mul i32 %1148, %.0115219
  %1150 = add i32 %1149, 4
  %1151 = sext i32 %1150 to i64
  %1152 = getelementptr i32, i32* %1147, i64 %1151
  store i32 %1146, i32* %1152, align 4
  %1153 = load i32, i32* %42, align 4
  %1154 = load i32*, i32** %1117, align 8
  %1155 = load i32, i32* %1118, align 4
  %1156 = mul i32 %1155, %.0115219
  %1157 = add i32 %1156, 5
  %1158 = sext i32 %1157 to i64
  %1159 = getelementptr i32, i32* %1154, i64 %1158
  store i32 %1153, i32* %1159, align 4
  %1160 = load i32, i32* %41, align 4
  %1161 = load i32*, i32** %1117, align 8
  %1162 = load i32, i32* %1118, align 4
  %1163 = mul i32 %1162, %.0115219
  %1164 = add i32 %1163, 6
  %1165 = sext i32 %1164 to i64
  %1166 = getelementptr i32, i32* %1161, i64 %1165
  store i32 %1160, i32* %1166, align 4
  %1167 = load i32, i32* %40, align 4
  %1168 = load i32*, i32** %1117, align 8
  %1169 = load i32, i32* %1118, align 4
  %1170 = mul i32 %1169, %.0115219
  %1171 = add i32 %1170, 7
  %1172 = sext i32 %1171 to i64
  %1173 = getelementptr i32, i32* %1168, i64 %1172
  store i32 %1167, i32* %1173, align 4
  %1174 = load i32, i32* %39, align 4
  %1175 = load i32*, i32** %1117, align 8
  %1176 = load i32, i32* %1118, align 4
  %1177 = mul i32 %1176, %.0115219
  %1178 = add i32 %1177, 8
  %1179 = sext i32 %1178 to i64
  %1180 = getelementptr i32, i32* %1175, i64 %1179
  store i32 %1174, i32* %1180, align 4
  %1181 = load i32, i32* %38, align 4
  %1182 = load i32*, i32** %1117, align 8
  %1183 = load i32, i32* %1118, align 4
  %1184 = mul i32 %1183, %.0115219
  %1185 = add i32 %1184, 9
  %1186 = sext i32 %1185 to i64
  %1187 = getelementptr i32, i32* %1182, i64 %1186
  store i32 %1181, i32* %1187, align 4
  %1188 = load i32, i32* %37, align 4
  %1189 = load i32*, i32** %1117, align 8
  %1190 = load i32, i32* %1118, align 4
  %1191 = mul i32 %1190, %.0115219
  %1192 = add i32 %1191, 10
  %1193 = sext i32 %1192 to i64
  %1194 = getelementptr i32, i32* %1189, i64 %1193
  store i32 %1188, i32* %1194, align 4
  %1195 = load i32, i32* %36, align 4
  %1196 = load i32*, i32** %1117, align 8
  %1197 = load i32, i32* %1118, align 4
  %1198 = mul i32 %1197, %.0115219
  %1199 = add i32 %1198, 11
  %1200 = sext i32 %1199 to i64
  %1201 = getelementptr i32, i32* %1196, i64 %1200
  store i32 %1195, i32* %1201, align 4
  %1202 = load i32, i32* %35, align 4
  %1203 = load i32*, i32** %1117, align 8
  %1204 = load i32, i32* %1118, align 4
  %1205 = mul i32 %1204, %.0115219
  %1206 = add i32 %1205, 12
  %1207 = sext i32 %1206 to i64
  %1208 = getelementptr i32, i32* %1203, i64 %1207
  store i32 %1202, i32* %1208, align 4
  %1209 = load i32, i32* %34, align 4
  %1210 = load i32*, i32** %1117, align 8
  %1211 = load i32, i32* %1118, align 4
  %1212 = mul i32 %1211, %.0115219
  %1213 = add i32 %1212, 13
  %1214 = sext i32 %1213 to i64
  %1215 = getelementptr i32, i32* %1210, i64 %1214
  store i32 %1209, i32* %1215, align 4
  %1216 = load i32, i32* %33, align 4
  %1217 = load i32*, i32** %1117, align 8
  %1218 = load i32, i32* %1118, align 4
  %1219 = mul i32 %1218, %.0115219
  %1220 = add i32 %1219, 14
  %1221 = sext i32 %1220 to i64
  %1222 = getelementptr i32, i32* %1217, i64 %1221
  store i32 %1216, i32* %1222, align 4
  %1223 = load i32, i32* %32, align 4
  %1224 = load i32*, i32** %1117, align 8
  %1225 = load i32, i32* %1118, align 4
  %1226 = mul i32 %1225, %.0115219
  %1227 = add i32 %1226, 15
  %1228 = sext i32 %1227 to i64
  %1229 = getelementptr i32, i32* %1224, i64 %1228
  store i32 %1223, i32* %1229, align 4
  br label %after_if

for_loop_body118:                                 ; preds = %after_if130, %for_loop_body118.lr.ph
  %indvars.iv284 = phi i64 [ %indvars.iv282, %for_loop_body118.lr.ph ], [ %indvars.iv.next285, %after_if130 ]
  %.5213 = phi i32 [ %.4216, %for_loop_body118.lr.ph ], [ %1276, %after_if130 ]
  %scevgep589 = getelementptr [16 x float], [16 x float]* %10, i64 0, i64 %indvars.iv284
  %1230 = load float, float* %scevgep589, align 4
  %1231 = fcmp reassoc ninf nsz ogt float %1112, %1230
  br i1 %1231, label %true_block122, label %after_if124

true_block122:                                    ; preds = %for_loop_body118
  %1232 = sdiv i32 %.5213, 32
  %1233 = icmp slt i32 %.5213, 0
  %1234 = shl nsw i32 %1232, 5
  %1235 = icmp ne i32 %.5213, %1234
  %1236 = and i1 %1233, %1235
  %.neg126 = sext i1 %1236 to i32
  %1237 = add nsw i32 %1232, %.neg126
  %.neg127 = mul i32 %1237, -32
  %1238 = add i32 %.5213, %.neg127
  %1239 = shl nuw i32 1, %1238
  %1240 = sext i32 %1237 to i64
  %1241 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %1240
  %1242 = load i32, i32* %1241, align 4
  %1243 = or i32 %1242, %1239
  store i32 %1243, i32* %1241, align 4
  br label %after_if124

after_if124:                                      ; preds = %true_block122, %for_loop_body118
  %scevgep588 = getelementptr [16 x float], [16 x float]* %11, i64 0, i64 %indvars.iv284
  %1244 = load float, float* %scevgep588, align 4
  %1245 = fcmp reassoc ninf nsz ogt float %1114, %1244
  br i1 %1245, label %true_block125, label %after_if127

true_block125:                                    ; preds = %after_if124
  %1246 = add i32 %.5213, 1
  %1247 = sdiv i32 %1246, 32
  %1248 = icmp slt i32 %1246, 0
  %1249 = shl nsw i32 %1247, 5
  %1250 = icmp ne i32 %1246, %1249
  %1251 = and i1 %1248, %1250
  %.neg124 = sext i1 %1251 to i32
  %1252 = add nsw i32 %1247, %.neg124
  %.neg125 = mul i32 %1252, -32
  %1253 = add i32 %.5213, %.neg125
  %1254 = add i32 %1253, 1
  %1255 = shl nuw i32 1, %1254
  %1256 = sext i32 %1252 to i64
  %1257 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %1256
  %1258 = load i32, i32* %1257, align 4
  %1259 = or i32 %1258, %1255
  store i32 %1259, i32* %1257, align 4
  br label %after_if127

after_if127:                                      ; preds = %true_block125, %after_if124
  %scevgep587 = getelementptr [16 x float], [16 x float]* %12, i64 0, i64 %indvars.iv284
  %1260 = load float, float* %scevgep587, align 4
  %1261 = fcmp reassoc ninf nsz ogt float %1116, %1260
  br i1 %1261, label %true_block128, label %after_if130

true_block128:                                    ; preds = %after_if127
  %1262 = add i32 %.5213, 2
  %1263 = sdiv i32 %1262, 32
  %1264 = icmp slt i32 %1262, 0
  %1265 = shl nsw i32 %1263, 5
  %1266 = icmp ne i32 %1262, %1265
  %1267 = and i1 %1264, %1266
  %.neg122 = sext i1 %1267 to i32
  %1268 = add nsw i32 %1263, %.neg122
  %.neg123 = mul i32 %1268, -32
  %1269 = add i32 %.5213, %.neg123
  %1270 = add i32 %1269, 2
  %1271 = shl nuw i32 1, %1270
  %1272 = sext i32 %1268 to i64
  %1273 = getelementptr [16 x i32], [16 x i32]* %3, i64 0, i64 %1272
  %1274 = load i32, i32* %1273, align 4
  %1275 = or i32 %1274, %1271
  store i32 %1275, i32* %1273, align 4
  br label %after_if130

after_if130:                                      ; preds = %true_block128, %after_if127
  %1276 = add i32 %.5213, 3
  %indvars.iv.next285 = add nuw nsw i64 %indvars.iv284, 1
  %exitcond287.not = icmp eq i64 %indvars.iv.next285, 16
  br i1 %exitcond287.not, label %for_loop_test117.loopexit.loopexit, label %for_loop_body118
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @cosf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @sinf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @atan2f(float noundef, float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.48, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.48**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.48*, %struct.RuntimeContext.48** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.48* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.48* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: argmemonly nocallback nofree nounwind willreturn writeonly
declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i1 immarg) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #8

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #9

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #10

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #11

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**>, i32 immarg, <4 x i1>, <4 x float*>) #10

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*>, i32 immarg, <4 x i1>, <4 x i32>) #10

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #7 = { argmemonly nocallback nofree nounwind willreturn writeonly }
attributes #8 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #10 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #11 = { nocallback nofree nosync nounwind readnone willreturn }

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
