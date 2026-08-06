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

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_compute_descriptors_kernel_c702_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %1, i64 0, i32 4, i32 1
  %3 = load i32*, i32** %2, align 8
  %4 = load i32, i32* %3, align 4
  %5 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %6 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %6, i64 0, i32 14
  %8 = load i8*, i8** %7, align 8
  %9 = getelementptr inbounds i8, i8* %8, i64 4
  %10 = bitcast i8* %9 to i32*
  store i32 %4, i32* %10, align 4
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %11, i64 0, i32 1, i32 0, i32 0
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %5, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %14, i64 0, i32 14
  %16 = bitcast i8** %15 to i32**
  %17 = load i32*, i32** %16, align 8
  store i32 %13, i32* %17, align 4
  ret void
}

; Function Attrs: nounwind
define void @_compute_descriptors_kernel_c702_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**
  %broadcast.splatinsert117 = insertelement <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**> poison, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %21, i64 0
  %broadcast.splat118 = shufflevector <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**> %broadcast.splatinsert117, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**> poison, <4 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.05893 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %94, %after_if ]
  %22 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  %27 = load i32, i32* %26, align 4
  %28 = icmp slt i32 %.05893, %27
  br i1 %28, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %29 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %21, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %29, i64 0, i32 1, i32 1
  %31 = load float*, float** %30, align 8
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %29, i64 0, i32 1, i32 0, i32 1
  %33 = load i32, i32* %32, align 4
  %34 = mul i32 %33, %.05893
  %35 = sext i32 %34 to i64
  %36 = getelementptr float, float* %31, i64 %35
  %37 = load float, float* %36, align 4
  %38 = fptosi float %37 to i32
  %39 = add i32 %34, 1
  %40 = sext i32 %39 to i64
  %41 = getelementptr float, float* %31, i64 %40
  %42 = load float, float* %41, align 4
  %43 = fptosi float %42 to i32
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %29, i64 0, i32 5
  %45 = load i32, i32* %44, align 4
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %29, i64 0, i32 6
  %47 = load i32, i32* %46, align 4
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %29, i64 0, i32 0, i32 1
  %49 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %29, i64 0, i32 0, i32 0, i32 1
  %broadcast.splatinsert149 = insertelement <4 x i32*> poison, i32* %49, i64 0
  %broadcast.splat150 = shufflevector <4 x i32*> %broadcast.splatinsert149, <4 x i32*> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert146 = insertelement <4 x float**> poison, float** %48, i64 0
  %broadcast.splat147 = shufflevector <4 x float**> %broadcast.splatinsert146, <4 x float**> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert144 = insertelement <4 x i32> poison, i32 %47, i64 0
  %broadcast.splat145 = shufflevector <4 x i32> %broadcast.splatinsert144, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert142 = insertelement <4 x i32> poison, i32 %43, i64 0
  %broadcast.splat143 = shufflevector <4 x i32> %broadcast.splatinsert142, <4 x i32> poison, <4 x i32> zeroinitializer
  %50 = add <4 x i32> %broadcast.splat143, <i32 -15, i32 -14, i32 -13, i32 -12>
  %51 = icmp sgt <4 x i32> %50, <i32 -1, i32 -1, i32 -1, i32 -1>
  %52 = icmp slt <4 x i32> %50, %broadcast.splat145
  %53 = select <4 x i1> %51, <4 x i1> %52, <4 x i1> zeroinitializer
  %54 = xor <4 x i1> %53, <i1 true, i1 true, i1 true, i1 true>
  %55 = add <4 x i32> %broadcast.splat143, <i32 -11, i32 -10, i32 -9, i32 -8>
  %56 = icmp sgt <4 x i32> %55, <i32 -1, i32 -1, i32 -1, i32 -1>
  %57 = icmp slt <4 x i32> %55, %broadcast.splat145
  %58 = select <4 x i1> %56, <4 x i1> %57, <4 x i1> zeroinitializer
  %59 = xor <4 x i1> %58, <i1 true, i1 true, i1 true, i1 true>
  %60 = add <4 x i32> %broadcast.splat143, <i32 -7, i32 -6, i32 -5, i32 -4>
  %61 = icmp sgt <4 x i32> %60, <i32 -1, i32 -1, i32 -1, i32 -1>
  %62 = icmp slt <4 x i32> %60, %broadcast.splat145
  %63 = select <4 x i1> %61, <4 x i1> %62, <4 x i1> zeroinitializer
  %64 = xor <4 x i1> %63, <i1 true, i1 true, i1 true, i1 true>
  %65 = add <4 x i32> %broadcast.splat143, <i32 -3, i32 -2, i32 -1, i32 0>
  %66 = icmp sgt <4 x i32> %65, <i32 -1, i32 -1, i32 -1, i32 -1>
  %67 = icmp slt <4 x i32> %65, %broadcast.splat145
  %68 = select <4 x i1> %66, <4 x i1> %67, <4 x i1> zeroinitializer
  %69 = xor <4 x i1> %68, <i1 true, i1 true, i1 true, i1 true>
  %70 = add <4 x i32> %broadcast.splat143, <i32 1, i32 2, i32 3, i32 4>
  %71 = icmp sgt <4 x i32> %70, <i32 -1, i32 -1, i32 -1, i32 -1>
  %72 = icmp slt <4 x i32> %70, %broadcast.splat145
  %73 = select <4 x i1> %71, <4 x i1> %72, <4 x i1> zeroinitializer
  %74 = xor <4 x i1> %73, <i1 true, i1 true, i1 true, i1 true>
  %75 = add <4 x i32> %broadcast.splat143, <i32 5, i32 6, i32 7, i32 8>
  %76 = icmp sgt <4 x i32> %75, <i32 -1, i32 -1, i32 -1, i32 -1>
  %77 = icmp slt <4 x i32> %75, %broadcast.splat145
  %78 = select <4 x i1> %76, <4 x i1> %77, <4 x i1> zeroinitializer
  %79 = xor <4 x i1> %78, <i1 true, i1 true, i1 true, i1 true>
  %80 = add <4 x i32> %broadcast.splat143, <i32 9, i32 10, i32 11, i32 12>
  %81 = icmp sgt <4 x i32> %80, <i32 -1, i32 -1, i32 -1, i32 -1>
  %82 = icmp slt <4 x i32> %80, %broadcast.splat145
  %83 = select <4 x i1> %81, <4 x i1> %82, <4 x i1> zeroinitializer
  %84 = xor <4 x i1> %83, <i1 true, i1 true, i1 true, i1 true>
  %85 = add i32 %43, 13
  %86 = icmp sgt i32 %85, -1
  %87 = icmp slt i32 %85, %47
  %spec.select.us = select i1 %86, i1 %87, i1 false
  %88 = add i32 %43, 14
  %89 = icmp sgt i32 %88, -1
  %90 = icmp slt i32 %88, %47
  %spec.select.us.1 = select i1 %89, i1 %90, i1 false
  %91 = add i32 %43, 15
  %92 = icmp sgt i32 %91, -1
  %93 = icmp slt i32 %91, %47
  %spec.select.us.2 = select i1 %92, i1 %93, i1 false
  br label %for_loop_body1

after_if.loopexit:                                ; preds = %after_for36
  br label %after_if

after_if:                                         ; preds = %after_if.loopexit, %for_loop_body
  %94 = add nsw i32 %.05893, 1
  %exitcond103.not = icmp eq i32 %94, %19
  br i1 %exitcond103.not, label %after_for.loopexit, label %for_loop_body

for_loop_body1:                                   ; preds = %after_for7, %true_block
  %.05289 = phi i32 [ -15, %true_block ], [ %229, %after_for7 ]
  %.05388 = phi float [ 0.000000e+00, %true_block ], [ %.us-phi94, %after_for7 ]
  %.05587 = phi float [ 0.000000e+00, %true_block ], [ %.us-phi, %after_for7 ]
  %95 = mul i32 %.05289, %.05289
  %96 = add i32 %38, %.05289
  %97 = icmp sgt i32 %96, -1
  %98 = icmp slt i32 %96, %45
  %or.cond = select i1 %97, i1 %98, i1 false
  %99 = sitofp i32 %.05289 to float
  %or.cond.fr = freeze i1 %or.cond
  br i1 %or.cond.fr, label %vector.body134, label %after_for7

vector.body134:                                   ; preds = %for_loop_body1
  %broadcast.splatinsert155 = insertelement <4 x float> poison, float %99, i64 0
  %broadcast.splat156 = shufflevector <4 x float> %broadcast.splatinsert155, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert152 = insertelement <4 x i32> poison, i32 %96, i64 0
  %broadcast.splat153 = shufflevector <4 x i32> %broadcast.splatinsert152, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert140 = insertelement <4 x i32> poison, i32 %95, i64 0
  %broadcast.splat141 = shufflevector <4 x i32> %broadcast.splatinsert140, <4 x i32> poison, <4 x i32> zeroinitializer
  %100 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05587, i64 0
  %101 = insertelement <4 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.05388, i64 0
  %102 = add <4 x i32> %broadcast.splat141, <i32 225, i32 196, i32 169, i32 144>
  %103 = icmp slt <4 x i32> %102, <i32 226, i32 226, i32 226, i32 226>
  %104 = select <4 x i1> %103, <4 x i1> %53, <4 x i1> zeroinitializer
  %wide.masked.gather148 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat147, i32 8, <4 x i1> %104, <4 x float*> undef)
  %wide.masked.gather151 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat150, i32 4, <4 x i1> %104, <4 x i32> undef)
  %105 = mul <4 x i32> %wide.masked.gather151, %broadcast.splat153
  %106 = add <4 x i32> %105, %50
  %107 = sext <4 x i32> %106 to <4 x i64>
  %108 = getelementptr float, <4 x float*> %wide.masked.gather148, <4 x i64> %107
  %wide.masked.gather154 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %108, i32 4, <4 x i1> %104, <4 x float> undef)
  %109 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154, <float -1.500000e+01, float -1.400000e+01, float -1.300000e+01, float -1.200000e+01>
  %110 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154, %broadcast.splat156
  %111 = select <4 x i1> %103, <4 x i1> %54, <4 x i1> zeroinitializer
  %112 = xor <4 x i1> %103, <i1 true, i1 true, i1 true, i1 true>
  %113 = select <4 x i1> %112, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %111
  %predphi157 = select <4 x i1> %113, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %109
  %predphi158 = fadd reassoc ninf nsz <4 x float> %100, %predphi157
  %predphi159 = select <4 x i1> %113, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %110
  %predphi160 = fadd reassoc ninf nsz <4 x float> %101, %predphi159
  %114 = add <4 x i32> %broadcast.splat141, <i32 121, i32 100, i32 81, i32 64>
  %115 = icmp slt <4 x i32> %114, <i32 226, i32 226, i32 226, i32 226>
  %116 = select <4 x i1> %115, <4 x i1> %58, <4 x i1> zeroinitializer
  %wide.masked.gather148.1 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat147, i32 8, <4 x i1> %116, <4 x float*> undef)
  %wide.masked.gather151.1 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat150, i32 4, <4 x i1> %116, <4 x i32> undef)
  %117 = mul <4 x i32> %wide.masked.gather151.1, %broadcast.splat153
  %118 = add <4 x i32> %117, %55
  %119 = sext <4 x i32> %118 to <4 x i64>
  %120 = getelementptr float, <4 x float*> %wide.masked.gather148.1, <4 x i64> %119
  %wide.masked.gather154.1 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %120, i32 4, <4 x i1> %116, <4 x float> undef)
  %121 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.1, <float -1.100000e+01, float -1.000000e+01, float -9.000000e+00, float -8.000000e+00>
  %122 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.1, %broadcast.splat156
  %123 = select <4 x i1> %115, <4 x i1> %59, <4 x i1> zeroinitializer
  %124 = xor <4 x i1> %115, <i1 true, i1 true, i1 true, i1 true>
  %125 = select <4 x i1> %124, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %123
  %predphi157.1 = select <4 x i1> %125, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %121
  %predphi158.1 = fadd reassoc ninf nsz <4 x float> %predphi158, %predphi157.1
  %predphi159.1 = select <4 x i1> %125, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %122
  %predphi160.1 = fadd reassoc ninf nsz <4 x float> %predphi160, %predphi159.1
  %126 = add <4 x i32> %broadcast.splat141, <i32 49, i32 36, i32 25, i32 16>
  %127 = icmp slt <4 x i32> %126, <i32 226, i32 226, i32 226, i32 226>
  %128 = select <4 x i1> %127, <4 x i1> %63, <4 x i1> zeroinitializer
  %wide.masked.gather148.2 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat147, i32 8, <4 x i1> %128, <4 x float*> undef)
  %wide.masked.gather151.2 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat150, i32 4, <4 x i1> %128, <4 x i32> undef)
  %129 = mul <4 x i32> %wide.masked.gather151.2, %broadcast.splat153
  %130 = add <4 x i32> %129, %60
  %131 = sext <4 x i32> %130 to <4 x i64>
  %132 = getelementptr float, <4 x float*> %wide.masked.gather148.2, <4 x i64> %131
  %wide.masked.gather154.2 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %132, i32 4, <4 x i1> %128, <4 x float> undef)
  %133 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.2, <float -7.000000e+00, float -6.000000e+00, float -5.000000e+00, float -4.000000e+00>
  %134 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.2, %broadcast.splat156
  %135 = select <4 x i1> %127, <4 x i1> %64, <4 x i1> zeroinitializer
  %136 = xor <4 x i1> %127, <i1 true, i1 true, i1 true, i1 true>
  %137 = select <4 x i1> %136, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %135
  %predphi157.2 = select <4 x i1> %137, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %133
  %predphi158.2 = fadd reassoc ninf nsz <4 x float> %predphi158.1, %predphi157.2
  %predphi159.2 = select <4 x i1> %137, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %134
  %predphi160.2 = fadd reassoc ninf nsz <4 x float> %predphi160.1, %predphi159.2
  %138 = add <4 x i32> %broadcast.splat141, <i32 9, i32 4, i32 1, i32 0>
  %139 = icmp slt <4 x i32> %138, <i32 226, i32 226, i32 226, i32 226>
  %140 = select <4 x i1> %139, <4 x i1> %68, <4 x i1> zeroinitializer
  %wide.masked.gather148.3 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat147, i32 8, <4 x i1> %140, <4 x float*> undef)
  %wide.masked.gather151.3 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat150, i32 4, <4 x i1> %140, <4 x i32> undef)
  %141 = mul <4 x i32> %wide.masked.gather151.3, %broadcast.splat153
  %142 = add <4 x i32> %141, %65
  %143 = sext <4 x i32> %142 to <4 x i64>
  %144 = getelementptr float, <4 x float*> %wide.masked.gather148.3, <4 x i64> %143
  %wide.masked.gather154.3 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %144, i32 4, <4 x i1> %140, <4 x float> undef)
  %145 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.3, <float -3.000000e+00, float -2.000000e+00, float -1.000000e+00, float 0.000000e+00>
  %146 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.3, %broadcast.splat156
  %147 = select <4 x i1> %139, <4 x i1> %69, <4 x i1> zeroinitializer
  %148 = xor <4 x i1> %139, <i1 true, i1 true, i1 true, i1 true>
  %149 = select <4 x i1> %148, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %147
  %predphi157.3 = select <4 x i1> %149, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %145
  %predphi158.3 = fadd reassoc ninf nsz <4 x float> %predphi158.2, %predphi157.3
  %predphi159.3 = select <4 x i1> %149, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %146
  %predphi160.3 = fadd reassoc ninf nsz <4 x float> %predphi160.2, %predphi159.3
  %150 = add <4 x i32> %broadcast.splat141, <i32 1, i32 4, i32 9, i32 16>
  %151 = icmp slt <4 x i32> %150, <i32 226, i32 226, i32 226, i32 226>
  %152 = select <4 x i1> %151, <4 x i1> %73, <4 x i1> zeroinitializer
  %wide.masked.gather148.4 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat147, i32 8, <4 x i1> %152, <4 x float*> undef)
  %wide.masked.gather151.4 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat150, i32 4, <4 x i1> %152, <4 x i32> undef)
  %153 = mul <4 x i32> %wide.masked.gather151.4, %broadcast.splat153
  %154 = add <4 x i32> %153, %70
  %155 = sext <4 x i32> %154 to <4 x i64>
  %156 = getelementptr float, <4 x float*> %wide.masked.gather148.4, <4 x i64> %155
  %wide.masked.gather154.4 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %156, i32 4, <4 x i1> %152, <4 x float> undef)
  %157 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.4, <float 1.000000e+00, float 2.000000e+00, float 3.000000e+00, float 4.000000e+00>
  %158 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.4, %broadcast.splat156
  %159 = select <4 x i1> %151, <4 x i1> %74, <4 x i1> zeroinitializer
  %160 = xor <4 x i1> %151, <i1 true, i1 true, i1 true, i1 true>
  %161 = select <4 x i1> %160, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %159
  %predphi157.4 = select <4 x i1> %161, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %157
  %predphi158.4 = fadd reassoc ninf nsz <4 x float> %predphi158.3, %predphi157.4
  %predphi159.4 = select <4 x i1> %161, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %158
  %predphi160.4 = fadd reassoc ninf nsz <4 x float> %predphi160.3, %predphi159.4
  %162 = add <4 x i32> %broadcast.splat141, <i32 25, i32 36, i32 49, i32 64>
  %163 = icmp slt <4 x i32> %162, <i32 226, i32 226, i32 226, i32 226>
  %164 = select <4 x i1> %163, <4 x i1> %78, <4 x i1> zeroinitializer
  %wide.masked.gather148.5 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat147, i32 8, <4 x i1> %164, <4 x float*> undef)
  %wide.masked.gather151.5 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat150, i32 4, <4 x i1> %164, <4 x i32> undef)
  %165 = mul <4 x i32> %wide.masked.gather151.5, %broadcast.splat153
  %166 = add <4 x i32> %165, %75
  %167 = sext <4 x i32> %166 to <4 x i64>
  %168 = getelementptr float, <4 x float*> %wide.masked.gather148.5, <4 x i64> %167
  %wide.masked.gather154.5 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %168, i32 4, <4 x i1> %164, <4 x float> undef)
  %169 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.5, <float 5.000000e+00, float 6.000000e+00, float 7.000000e+00, float 8.000000e+00>
  %170 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.5, %broadcast.splat156
  %171 = select <4 x i1> %163, <4 x i1> %79, <4 x i1> zeroinitializer
  %172 = xor <4 x i1> %163, <i1 true, i1 true, i1 true, i1 true>
  %173 = select <4 x i1> %172, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %171
  %predphi157.5 = select <4 x i1> %173, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %169
  %predphi158.5 = fadd reassoc ninf nsz <4 x float> %predphi158.4, %predphi157.5
  %predphi159.5 = select <4 x i1> %173, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %170
  %predphi160.5 = fadd reassoc ninf nsz <4 x float> %predphi160.4, %predphi159.5
  %174 = add <4 x i32> %broadcast.splat141, <i32 81, i32 100, i32 121, i32 144>
  %175 = icmp slt <4 x i32> %174, <i32 226, i32 226, i32 226, i32 226>
  %176 = select <4 x i1> %175, <4 x i1> %83, <4 x i1> zeroinitializer
  %wide.masked.gather148.6 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %broadcast.splat147, i32 8, <4 x i1> %176, <4 x float*> undef)
  %wide.masked.gather151.6 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %broadcast.splat150, i32 4, <4 x i1> %176, <4 x i32> undef)
  %177 = mul <4 x i32> %wide.masked.gather151.6, %broadcast.splat153
  %178 = add <4 x i32> %177, %80
  %179 = sext <4 x i32> %178 to <4 x i64>
  %180 = getelementptr float, <4 x float*> %wide.masked.gather148.6, <4 x i64> %179
  %wide.masked.gather154.6 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %180, i32 4, <4 x i1> %176, <4 x float> undef)
  %181 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.6, <float 9.000000e+00, float 1.000000e+01, float 1.100000e+01, float 1.200000e+01>
  %182 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather154.6, %broadcast.splat156
  %183 = select <4 x i1> %175, <4 x i1> %84, <4 x i1> zeroinitializer
  %184 = xor <4 x i1> %175, <i1 true, i1 true, i1 true, i1 true>
  %185 = select <4 x i1> %184, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x i1> %183
  %predphi157.6 = select <4 x i1> %185, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %181
  %predphi158.6 = fadd reassoc ninf nsz <4 x float> %predphi158.5, %predphi157.6
  %predphi159.6 = select <4 x i1> %185, <4 x float> <float -0.000000e+00, float -0.000000e+00, float -0.000000e+00, float -0.000000e+00>, <4 x float> %182
  %predphi160.6 = fadd reassoc ninf nsz <4 x float> %predphi160.5, %predphi159.6
  %186 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %predphi158.6)
  %187 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %predphi160.6)
  %188 = add i32 %95, 169
  %189 = icmp slt i32 %188, 226
  %.not = xor i1 %189, true
  %spec.select.us.not = xor i1 %spec.select.us, true
  %brmerge = select i1 %.not, i1 true, i1 %spec.select.us.not
  br i1 %brmerge, label %after_if11.us, label %true_block21.us

true_block21.us:                                  ; preds = %vector.body134
  %190 = load float*, float** %48, align 8
  %191 = load i32, i32* %49, align 4
  %192 = mul i32 %191, %96
  %193 = add i32 %192, %85
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %190, i64 %194
  %196 = load float, float* %195, align 4
  %197 = fmul reassoc ninf nsz float %196, 1.300000e+01
  %198 = fadd reassoc ninf nsz float %197, %186
  %199 = fmul reassoc ninf nsz float %196, %99
  %200 = fadd reassoc ninf nsz float %199, %187
  br label %after_if11.us

after_if11.us:                                    ; preds = %true_block21.us, %vector.body134
  %.257.us = phi float [ %198, %true_block21.us ], [ %186, %vector.body134 ]
  %.2.us = phi float [ %200, %true_block21.us ], [ %187, %vector.body134 ]
  %201 = add i32 %95, 196
  %202 = icmp slt i32 %201, 226
  %.not166 = xor i1 %202, true
  %spec.select.us.1.not = xor i1 %spec.select.us.1, true
  %brmerge167 = select i1 %.not166, i1 true, i1 %spec.select.us.1.not
  br i1 %brmerge167, label %after_if11.us.1, label %true_block21.us.1

true_block21.us.1:                                ; preds = %after_if11.us
  %203 = load float*, float** %48, align 8
  %204 = load i32, i32* %49, align 4
  %205 = mul i32 %204, %96
  %206 = add i32 %205, %88
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, float* %203, i64 %207
  %209 = load float, float* %208, align 4
  %210 = fmul reassoc ninf nsz float %209, 1.400000e+01
  %211 = fadd reassoc ninf nsz float %210, %.257.us
  %212 = fmul reassoc ninf nsz float %209, %99
  %213 = fadd reassoc ninf nsz float %212, %.2.us
  br label %after_if11.us.1

after_if11.us.1:                                  ; preds = %true_block21.us.1, %after_if11.us
  %.257.us.1 = phi float [ %211, %true_block21.us.1 ], [ %.257.us, %after_if11.us ]
  %.2.us.1 = phi float [ %213, %true_block21.us.1 ], [ %.2.us, %after_if11.us ]
  %214 = add i32 %95, 225
  %215 = icmp slt i32 %214, 226
  %.not168 = xor i1 %215, true
  %spec.select.us.2.not = xor i1 %spec.select.us.2, true
  %brmerge169 = select i1 %.not168, i1 true, i1 %spec.select.us.2.not
  br i1 %brmerge169, label %after_for7, label %true_block21.us.2

true_block21.us.2:                                ; preds = %after_if11.us.1
  %216 = load float*, float** %48, align 8
  %217 = load i32, i32* %49, align 4
  %218 = mul i32 %217, %96
  %219 = add i32 %218, %91
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %216, i64 %220
  %222 = load float, float* %221, align 4
  %223 = fmul reassoc ninf nsz float %222, 1.500000e+01
  %224 = fadd reassoc ninf nsz float %223, %.257.us.1
  %225 = fmul reassoc ninf nsz float %222, %99
  %226 = fadd reassoc ninf nsz float %225, %.2.us.1
  br label %after_for7

after_for3:                                       ; preds = %after_for7
  %227 = fcmp reassoc ninf nsz one float %.us-phi, 0.000000e+00
  %228 = fcmp reassoc ninf nsz one float %.us-phi94, 0.000000e+00
  %.046 = select i1 %227, i1 true, i1 %228
  br i1 %.046, label %true_block27, label %after_if29

after_for7:                                       ; preds = %true_block21.us.2, %after_if11.us.1, %for_loop_body1
  %.us-phi = phi float [ %.05587, %for_loop_body1 ], [ %224, %true_block21.us.2 ], [ %.257.us.1, %after_if11.us.1 ]
  %.us-phi94 = phi float [ %.05388, %for_loop_body1 ], [ %226, %true_block21.us.2 ], [ %.2.us.1, %after_if11.us.1 ]
  %229 = add nsw i32 %.05289, 1
  %exitcond96.not = icmp eq i32 %229, 16
  br i1 %exitcond96.not, label %after_for3, label %for_loop_body1

true_block27:                                     ; preds = %after_for3
  %230 = tail call float @atan2f(float noundef %.us-phi94, float noundef %.us-phi) #1
  br label %after_if29

after_if29:                                       ; preds = %true_block27, %after_for3
  %.047 = phi float [ %230, %true_block27 ], [ 0.000000e+00, %after_for3 ]
  %231 = tail call float @cosf(float noundef %.047) #1
  %232 = tail call float @sinf(float noundef %.047) #1
  %233 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %21, align 8
  %234 = sitofp i32 %38 to float
  %235 = sitofp i32 %43 to float
  %236 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %233, i64 0, i32 2, i32 1
  %237 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %233, i64 0, i32 2, i32 0, i32 1
  %238 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %233, i64 0, i32 3, i32 1
  %239 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %233, i64 0, i32 3, i32 0, i32 1
  %broadcast.splatinsert = insertelement <4 x float> poison, float %231, i64 0
  %broadcast.splat = shufflevector <4 x float> %broadcast.splatinsert, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert107 = insertelement <4 x float> poison, float %232, i64 0
  %broadcast.splat108 = shufflevector <4 x float> %broadcast.splatinsert107, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert109 = insertelement <4 x float> poison, float %234, i64 0
  %broadcast.splat110 = shufflevector <4 x float> %broadcast.splatinsert109, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert111 = insertelement <4 x float> poison, float %235, i64 0
  %broadcast.splat112 = shufflevector <4 x float> %broadcast.splatinsert111, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert113 = insertelement <4 x i32> poison, i32 %45, i64 0
  %broadcast.splat114 = shufflevector <4 x i32> %broadcast.splatinsert113, <4 x i32> poison, <4 x i32> zeroinitializer
  br label %for_loop_body30

for_loop_body30:                                  ; preds = %after_for36, %after_if29
  %lsr.iv = phi i32 [ 0, %after_if29 ], [ %lsr.iv.next, %after_for36 ]
  %indvars.iv99 = phi i64 [ 0, %after_if29 ], [ %indvars.iv.next100, %after_for36 ]
  %240 = load float*, float** %236, align 8
  %241 = load i32, i32* %237, align 4
  %ident.check.not = icmp eq i32 %241, 1
  br i1 %ident.check.not, label %vector.body.preheader, label %for_loop_body34.preheader

for_loop_body34.preheader:                        ; preds = %for_loop_body30
  %242 = mul i32 %241, %lsr.iv
  br label %for_loop_body34

vector.body.preheader:                            ; preds = %for_loop_body30
  %243 = mul i32 %241, %lsr.iv
  %244 = shl i32 %241, 2
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv174 = phi i64 [ 32, %vector.body.preheader ], [ %lsr.iv.next175, %vector.body ]
  %lsr.iv172 = phi i32 [ %243, %vector.body.preheader ], [ %lsr.iv.next173, %vector.body ]
  %vec.phi = phi <4 x i32> [ %317, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.ind = phi <4 x i32> [ %vec.ind.next, %vector.body ], [ <i32 0, i32 1, i32 2, i32 3>, %vector.body.preheader ]
  %245 = sext i32 %lsr.iv172 to i64
  %246 = getelementptr float, float* %240, i64 %245
  %247 = bitcast float* %246 to <4 x float>*
  %wide.load = load <4 x float>, <4 x float>* %247, align 4
  %248 = add i32 %lsr.iv172, 1
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, float* %240, i64 %249
  %251 = bitcast float* %250 to <4 x float>*
  %wide.load104 = load <4 x float>, <4 x float>* %251, align 4
  %252 = add i32 %lsr.iv172, 2
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, float* %240, i64 %253
  %255 = bitcast float* %254 to <4 x float>*
  %wide.load105 = load <4 x float>, <4 x float>* %255, align 4
  %256 = add i32 %lsr.iv172, 3
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, float* %240, i64 %257
  %259 = bitcast float* %258 to <4 x float>*
  %wide.load106 = load <4 x float>, <4 x float>* %259, align 4
  %260 = fmul reassoc ninf nsz <4 x float> %wide.load, %broadcast.splat
  %261 = fmul reassoc ninf nsz <4 x float> %wide.load, %broadcast.splat108
  %262 = fmul reassoc ninf nsz <4 x float> %wide.load104, %broadcast.splat
  %263 = fmul reassoc ninf nsz <4 x float> %wide.load105, %broadcast.splat
  %264 = fmul reassoc ninf nsz <4 x float> %wide.load105, %broadcast.splat108
  %265 = fmul reassoc ninf nsz <4 x float> %wide.load106, %broadcast.splat
  %266 = fadd reassoc ninf nsz <4 x float> %261, %broadcast.splat110
  %267 = fadd reassoc ninf nsz <4 x float> %266, %262
  %268 = fadd reassoc ninf nsz <4 x float> %260, %broadcast.splat112
  %269 = fmul reassoc ninf nsz <4 x float> %wide.load104, %broadcast.splat108
  %270 = fsub reassoc ninf nsz <4 x float> %268, %269
  %271 = fptosi <4 x float> %267 to <4 x i32>
  %272 = fptosi <4 x float> %270 to <4 x i32>
  %273 = icmp sgt <4 x i32> %271, <i32 -1, i32 -1, i32 -1, i32 -1>
  %274 = icmp sgt <4 x i32> %broadcast.splat114, %271
  %275 = select <4 x i1> %273, <4 x i1> %274, <4 x i1> zeroinitializer
  %276 = icmp sgt <4 x i32> %272, <i32 -1, i32 -1, i32 -1, i32 -1>
  %277 = icmp sgt <4 x i32> %broadcast.splat145, %272
  %278 = select <4 x i1> %276, <4 x i1> %277, <4 x i1> zeroinitializer
  %279 = select <4 x i1> %275, <4 x i1> %278, <4 x i1> zeroinitializer
  %wide.masked.gather = call <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> @llvm.masked.gather.v4p0sl_sl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0i32ssl_sl_i32sp0i32si32i32s.v4p0p0sl_sl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0i32ssl_sl_i32sp0i32si32i32s(<4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**> %broadcast.splat118, i32 8, <4 x i1> %279, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> undef)
  %280 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> %wide.masked.gather, i64 0, i32 0, i32 1
  %wide.masked.gather119 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %280, i32 8, <4 x i1> %279, <4 x float*> undef)
  %281 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> %wide.masked.gather, i64 0, i32 0, i32 0, i32 1
  %wide.masked.gather120 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %281, i32 4, <4 x i1> %279, <4 x i32> undef)
  %282 = mul <4 x i32> %wide.masked.gather120, %271
  %283 = add <4 x i32> %282, %272
  %284 = sext <4 x i32> %283 to <4 x i64>
  %285 = getelementptr float, <4 x float*> %wide.masked.gather119, <4 x i64> %284
  %wide.masked.gather121 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %285, i32 4, <4 x i1> %279, <4 x float> zeroinitializer)
  %286 = xor <4 x i1> %278, <i1 true, i1 true, i1 true, i1 true>
  %287 = select <4 x i1> %275, <4 x i1> %286, <4 x i1> zeroinitializer
  %288 = xor <4 x i1> %275, <i1 true, i1 true, i1 true, i1 true>
  %predphi122 = select <4 x i1> %275, <4 x float> %wide.masked.gather121, <4 x float> zeroinitializer
  %289 = fadd reassoc ninf nsz <4 x float> %264, %broadcast.splat110
  %290 = fadd reassoc ninf nsz <4 x float> %289, %265
  %291 = fadd reassoc ninf nsz <4 x float> %263, %broadcast.splat112
  %292 = fmul reassoc ninf nsz <4 x float> %wide.load106, %broadcast.splat108
  %293 = fsub reassoc ninf nsz <4 x float> %291, %292
  %294 = fptosi <4 x float> %290 to <4 x i32>
  %295 = fptosi <4 x float> %293 to <4 x i32>
  %296 = icmp sgt <4 x i32> %294, <i32 -1, i32 -1, i32 -1, i32 -1>
  %297 = icmp sgt <4 x i32> %broadcast.splat114, %294
  %298 = select <4 x i1> %296, <4 x i1> %297, <4 x i1> zeroinitializer
  %299 = icmp sgt <4 x i32> %295, <i32 -1, i32 -1, i32 -1, i32 -1>
  %300 = icmp sgt <4 x i32> %broadcast.splat145, %295
  %301 = or <4 x i1> %287, %288
  %302 = or <4 x i1> %301, %279
  %303 = select <4 x i1> %302, <4 x i1> %298, <4 x i1> zeroinitializer
  %304 = select <4 x i1> %303, <4 x i1> %299, <4 x i1> zeroinitializer
  %305 = select <4 x i1> %304, <4 x i1> %300, <4 x i1> zeroinitializer
  %wide.masked.gather123 = call <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> @llvm.masked.gather.v4p0sl_sl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0i32ssl_sl_i32sp0i32si32i32s.v4p0p0sl_sl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0i32ssl_sl_i32sp0i32si32i32s(<4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**> %broadcast.splat118, i32 8, <4 x i1> %305, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> undef)
  %306 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> %wide.masked.gather123, i64 0, i32 0, i32 1
  %wide.masked.gather124 = call <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**> %306, i32 8, <4 x i1> %305, <4 x float*> undef)
  %307 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> %wide.masked.gather123, i64 0, i32 0, i32 0, i32 1
  %wide.masked.gather125 = call <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*> %307, i32 4, <4 x i1> %305, <4 x i32> undef)
  %308 = mul <4 x i32> %wide.masked.gather125, %294
  %309 = add <4 x i32> %308, %295
  %310 = sext <4 x i32> %309 to <4 x i64>
  %311 = getelementptr float, <4 x float*> %wide.masked.gather124, <4 x i64> %310
  %wide.masked.gather126 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %311, i32 4, <4 x i1> %305, <4 x float> zeroinitializer)
  %312 = xor <4 x i1> %298, <i1 true, i1 true, i1 true, i1 true>
  %313 = select <4 x i1> %302, <4 x i1> %312, <4 x i1> zeroinitializer
  %predphi128 = select <4 x i1> %313, <4 x float> zeroinitializer, <4 x float> %wide.masked.gather126
  %314 = fcmp reassoc ninf nsz olt <4 x float> %predphi122, %predphi128
  %315 = shl nuw <4 x i32> <i32 1, i32 1, i32 1, i32 1>, %vec.ind
  %316 = select <4 x i1> %314, <4 x i32> %315, <4 x i32> zeroinitializer
  %317 = or <4 x i32> %316, %vec.phi
  %vec.ind.next = add <4 x i32> %vec.ind, <i32 4, i32 4, i32 4, i32 4>
  %lsr.iv.next173 = add i32 %lsr.iv172, %244
  %lsr.iv.next175 = add nsw i64 %lsr.iv174, -4
  %318 = icmp eq i64 %lsr.iv.next175, 0
  br i1 %318, label %middle.block, label %vector.body, !llvm.loop !9

middle.block:                                     ; preds = %vector.body
  %319 = call i32 @llvm.vector.reduce.or.v4i32(<4 x i32> %317)
  br label %after_for36

for_loop_body34:                                  ; preds = %after_if61, %for_loop_body34.preheader
  %lsr.iv170 = phi i32 [ %242, %for_loop_body34.preheader ], [ %lsr.iv.next171, %after_if61 ]
  %indvars.iv = phi i64 [ %indvars.iv.next, %after_if61 ], [ 0, %for_loop_body34.preheader ]
  %.04490 = phi i32 [ %.1, %after_if61 ], [ 0, %for_loop_body34.preheader ]
  %320 = sext i32 %lsr.iv170 to i64
  %321 = getelementptr float, float* %240, i64 %320
  %322 = load float, float* %321, align 4
  %323 = add i32 %lsr.iv170, 1
  %324 = sext i32 %323 to i64
  %325 = getelementptr float, float* %240, i64 %324
  %326 = load float, float* %325, align 4
  %327 = add i32 %lsr.iv170, 2
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, float* %240, i64 %328
  %330 = load float, float* %329, align 4
  %331 = add i32 %lsr.iv170, 3
  %332 = sext i32 %331 to i64
  %333 = getelementptr float, float* %240, i64 %332
  %334 = load float, float* %333, align 4
  %335 = fmul reassoc ninf nsz float %322, %231
  %336 = fmul reassoc ninf nsz float %322, %232
  %337 = fmul reassoc ninf nsz float %326, %231
  %338 = fmul reassoc ninf nsz float %330, %231
  %339 = fmul reassoc ninf nsz float %330, %232
  %340 = fmul reassoc ninf nsz float %334, %231
  %341 = fadd reassoc ninf nsz float %336, %234
  %342 = fadd reassoc ninf nsz float %341, %337
  %343 = fadd reassoc ninf nsz float %335, %235
  %344 = fmul reassoc ninf nsz float %326, %232
  %345 = fsub reassoc ninf nsz float %343, %344
  %346 = fptosi float %342 to i32
  %347 = fptosi float %345 to i32
  %348 = icmp sgt i32 %346, -1
  %349 = icmp sgt i32 %45, %346
  %or.cond80 = select i1 %348, i1 %349, i1 false
  br i1 %or.cond80, label %true_block41, label %after_if49

after_for36.loopexit:                             ; preds = %after_if61
  br label %after_for36

after_for36:                                      ; preds = %after_for36.loopexit, %middle.block
  %.1.lcssa = phi i32 [ %319, %middle.block ], [ %.1, %after_for36.loopexit ]
  %350 = load i32*, i32** %238, align 8
  %351 = load i32, i32* %239, align 4
  %352 = mul i32 %351, %.05893
  %353 = trunc i64 %indvars.iv99 to i32
  %354 = add i32 %352, %353
  %355 = sext i32 %354 to i64
  %356 = getelementptr i32, i32* %350, i64 %355
  store i32 %.1.lcssa, i32* %356, align 4
  %indvars.iv.next100 = add nuw nsw i64 %indvars.iv99, 1
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 32
  %exitcond102.not = icmp eq i64 %indvars.iv.next100, 8
  br i1 %exitcond102.not, label %after_if.loopexit, label %for_loop_body30

true_block41:                                     ; preds = %for_loop_body34
  %357 = icmp sgt i32 %347, -1
  %358 = icmp sgt i32 %47, %347
  %spec.select76 = select i1 %357, i1 %358, i1 false
  br i1 %spec.select76, label %true_block47, label %after_if49

true_block47:                                     ; preds = %true_block41
  %359 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %21, align 8
  %360 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %359, i64 0, i32 0, i32 1
  %361 = load float*, float** %360, align 8
  %362 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %359, i64 0, i32 0, i32 0, i32 1
  %363 = load i32, i32* %362, align 4
  %364 = mul i32 %363, %346
  %365 = add i32 %364, %347
  %366 = sext i32 %365 to i64
  %367 = getelementptr float, float* %361, i64 %366
  %368 = load float, float* %367, align 4
  br label %after_if49

after_if49:                                       ; preds = %true_block47, %true_block41, %for_loop_body34
  %.042 = phi float [ %368, %true_block47 ], [ 0.000000e+00, %true_block41 ], [ 0.000000e+00, %for_loop_body34 ]
  %369 = fadd reassoc ninf nsz float %339, %234
  %370 = fadd reassoc ninf nsz float %369, %340
  %371 = fadd reassoc ninf nsz float %338, %235
  %372 = fmul reassoc ninf nsz float %334, %232
  %373 = fsub reassoc ninf nsz float %371, %372
  %374 = fptosi float %370 to i32
  %375 = fptosi float %373 to i32
  %376 = icmp sgt i32 %374, -1
  %377 = icmp sgt i32 %45, %374
  %or.cond81 = select i1 %376, i1 %377, i1 false
  br i1 %or.cond81, label %true_block53, label %after_if61

true_block53:                                     ; preds = %after_if49
  %378 = icmp sgt i32 %375, -1
  %379 = icmp sgt i32 %47, %375
  %spec.select78 = select i1 %378, i1 %379, i1 false
  br i1 %spec.select78, label %true_block59, label %after_if61

true_block59:                                     ; preds = %true_block53
  %380 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %21, align 8
  %381 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %380, i64 0, i32 0, i32 1
  %382 = load float*, float** %381, align 8
  %383 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %380, i64 0, i32 0, i32 0, i32 1
  %384 = load i32, i32* %383, align 4
  %385 = mul i32 %384, %374
  %386 = add i32 %385, %375
  %387 = sext i32 %386 to i64
  %388 = getelementptr float, float* %382, i64 %387
  %389 = load float, float* %388, align 4
  br label %after_if61

after_if61:                                       ; preds = %true_block59, %true_block53, %after_if49
  %.038 = phi float [ %389, %true_block59 ], [ 0.000000e+00, %true_block53 ], [ 0.000000e+00, %after_if49 ]
  %390 = fcmp reassoc ninf nsz olt float %.042, %.038
  %tmp = trunc i64 %indvars.iv to i32
  %391 = shl nuw i32 1, %tmp
  %392 = select i1 %390, i32 %391, i32 0
  %.1 = or i32 %392, %.04490
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %lsr.iv.next171 = add i32 %lsr.iv170, %241
  %exitcond98.not = icmp eq i64 %indvars.iv.next, 32
  br i1 %exitcond98.not, label %after_for36.loopexit, label %for_loop_body34, !llvm.loop !11
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @cosf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @sinf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @atan2f(float noundef, float noundef) local_unnamed_addr #3

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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !12

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !14

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
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*> @llvm.masked.gather.v4p0sl_sl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0i32ssl_sl_i32sp0i32si32i32s.v4p0p0sl_sl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0f32ssl_sl_i32i32sp0i32ssl_sl_i32sp0i32si32i32s(<4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**>, i32 immarg, <4 x i1>, <4 x { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float*> @llvm.masked.gather.v4p0f32.v4p0p0f32(<4 x float**>, i32 immarg, <4 x i1>, <4 x float*>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x i32> @llvm.masked.gather.v4i32.v4p0i32(<4 x i32*>, i32 immarg, <4 x i1>, <4 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare i32 @llvm.vector.reduce.or.v4i32(<4 x i32>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #9

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone willreturn }

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
!10 = !{!"llvm.loop.isvectorized", i32 1}
!11 = distinct !{!11, !10}
!12 = distinct !{!12, !13}
!13 = !{!"llvm.loop.mustprogress"}
!14 = distinct !{!14, !13}
