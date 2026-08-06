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

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_hamming_matcher_kernel_c704_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }**
  %1 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %1, i64 0, i32 3, i32 1
  %3 = load i32*, i32** %2, align 8
  %4 = load i32, i32* %3, align 4
  %5 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %6 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %6, i64 0, i32 14
  %8 = load i8*, i8** %7, align 8
  %9 = getelementptr inbounds i8, i8* %8, i64 4
  %10 = bitcast i8* %9 to i32*
  store i32 %4, i32* %10, align 4
  %11 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %11, i64 0, i32 4, i32 1
  %13 = load i32*, i32** %12, align 8
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %5, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %20, i64 0, i32 0, i32 0, i32 0
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %5, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %23, i64 0, i32 14
  %25 = bitcast i8** %24 to i32**
  %26 = load i32*, i32** %25, align 8
  store i32 %22, i32* %26, align 4
  ret void
}

; Function Attrs: nounwind
define void @_hamming_matcher_kernel_c704_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nosync nounwind
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }**
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.03141 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %40, %after_if ]
  %22 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  %27 = load i32, i32* %26, align 4
  %28 = icmp slt i32 %.03141, %27
  br i1 %28, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %29 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }** %21, align 8
  %30 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 1, i32 0, i32 0
  %31 = load i32, i32* %30, align 4
  %32 = icmp sgt i32 %31, 0
  br i1 %32, label %for_loop_body1.lr.ph, label %after_for3

for_loop_body1.lr.ph:                             ; preds = %true_block
  %33 = getelementptr inbounds i8, i8* %24, i64 8
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 0, i32 1
  %37 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 0, i32 0, i32 1
  %38 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 1, i32 1
  %39 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body1

after_if:                                         ; preds = %after_for3, %for_loop_body
  %40 = add nsw i32 %.03141, 1
  %exitcond43.not = icmp eq i32 %40, %19
  br i1 %exitcond43.not, label %after_for.loopexit, label %for_loop_body

for_loop_body1:                                   ; preds = %after_if7, %for_loop_body1.lr.ph
  %.02538 = phi i32 [ 0, %for_loop_body1.lr.ph ], [ %118, %after_if7 ]
  %.02637 = phi i32 [ 256, %for_loop_body1.lr.ph ], [ %.1, %after_if7 ]
  %.02736 = phi i32 [ 256, %for_loop_body1.lr.ph ], [ %.128, %after_if7 ]
  %.02935 = phi i32 [ -1, %for_loop_body1.lr.ph ], [ %.130, %after_if7 ]
  %41 = icmp slt i32 %.02538, %35
  br i1 %41, label %for_loop_test11.preheader, label %after_if7

for_loop_test11.preheader:                        ; preds = %for_loop_body1
  %42 = load i32*, i32** %36, align 8
  %43 = load i32, i32* %37, align 4
  %44 = load i32*, i32** %38, align 8
  %45 = load i32, i32* %39, align 4
  %46 = mul i32 %43, %.03141
  %47 = mul i32 %45, %.02538
  %48 = insertelement <4 x i32> poison, i32 %46, i64 0
  %shuffle56 = shufflevector <4 x i32> %48, <4 x i32> poison, <4 x i32> zeroinitializer
  %49 = add <4 x i32> %shuffle56, <i32 1, i32 2, i32 3, i32 4>
  %50 = insertelement <4 x i32> poison, i32 %47, i64 0
  %shuffle55 = shufflevector <4 x i32> %50, <4 x i32> poison, <4 x i32> zeroinitializer
  %51 = add <4 x i32> %shuffle55, <i32 1, i32 2, i32 3, i32 4>
  %52 = add i32 %46, 5
  %53 = add i32 %47, 5
  %54 = insertelement <2 x i32> poison, i32 %46, i64 0
  %55 = shufflevector <2 x i32> %54, <2 x i32> poison, <2 x i32> zeroinitializer
  %56 = add <2 x i32> %55, <i32 6, i32 7>
  %57 = insertelement <8 x i32> poison, i32 %46, i64 0
  %58 = shufflevector <4 x i32> %49, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %59 = shufflevector <8 x i32> %57, <8 x i32> %58, <8 x i32> <i32 0, i32 8, i32 9, i32 10, i32 11, i32 undef, i32 undef, i32 undef>
  %60 = insertelement <8 x i32> %59, i32 %52, i64 5
  %61 = shufflevector <2 x i32> %56, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %62 = shufflevector <8 x i32> %60, <8 x i32> %61, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 8, i32 9>
  %63 = sext <8 x i32> %62 to <8 x i64>
  %64 = insertelement <8 x i32*> poison, i32* %42, i64 0
  %shuffle54 = shufflevector <8 x i32*> %64, <8 x i32*> poison, <8 x i32> zeroinitializer
  %65 = getelementptr i32, <8 x i32*> %shuffle54, <8 x i64> %63
  %66 = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %65, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x i32> undef)
  %67 = insertelement <2 x i32> poison, i32 %47, i64 0
  %68 = shufflevector <2 x i32> %67, <2 x i32> poison, <2 x i32> zeroinitializer
  %69 = add <2 x i32> %68, <i32 6, i32 7>
  %70 = insertelement <8 x i32> poison, i32 %47, i64 0
  %71 = shufflevector <4 x i32> %51, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %72 = shufflevector <8 x i32> %70, <8 x i32> %71, <8 x i32> <i32 0, i32 8, i32 9, i32 10, i32 11, i32 undef, i32 undef, i32 undef>
  %73 = insertelement <8 x i32> %72, i32 %53, i64 5
  %74 = shufflevector <2 x i32> %69, <2 x i32> poison, <8 x i32> <i32 0, i32 1, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef, i32 undef>
  %75 = shufflevector <8 x i32> %73, <8 x i32> %74, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 8, i32 9>
  %76 = sext <8 x i32> %75 to <8 x i64>
  %77 = insertelement <8 x i32*> poison, i32* %44, i64 0
  %shuffle = shufflevector <8 x i32*> %77, <8 x i32*> poison, <8 x i32> zeroinitializer
  %78 = getelementptr i32, <8 x i32*> %shuffle, <8 x i64> %76
  %79 = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %78, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x i32> undef)
  %80 = xor <8 x i32> %79, %66
  %81 = lshr <8 x i32> %80, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %82 = and <8 x i32> %81, <i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765>
  %83 = sub <8 x i32> %80, %82
  %84 = and <8 x i32> %83, <i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459>
  %85 = lshr <8 x i32> %83, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %86 = and <8 x i32> %85, <i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459>
  %87 = add nuw nsw <8 x i32> %86, %84
  %88 = lshr <8 x i32> %87, <i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4>
  %89 = add nuw nsw <8 x i32> %88, %87
  %90 = and <8 x i32> %89, <i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135>
  %91 = lshr <8 x i32> %90, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %92 = add nuw nsw <8 x i32> %91, %90
  %93 = lshr <8 x i32> %92, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %94 = add nuw nsw <8 x i32> %93, %92
  %95 = and <8 x i32> %94, <i32 63, i32 63, i32 63, i32 63, i32 63, i32 63, i32 63, i32 63>
  %96 = call i32 @llvm.vector.reduce.add.v8i32(<8 x i32> %95)
  %97 = icmp slt i32 %96, %.02736
  br i1 %97, label %for_loop_test11.preheader.after_if7_crit_edge, label %false_block13

for_loop_test11.preheader.after_if7_crit_edge:    ; preds = %for_loop_test11.preheader
  br label %after_if7

after_for3.loopexit:                              ; preds = %after_if7
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %true_block
  %.029.lcssa = phi i32 [ -1, %true_block ], [ %.130, %after_for3.loopexit ]
  %.027.lcssa = phi i32 [ 256, %true_block ], [ %.128, %after_for3.loopexit ]
  %.026.lcssa = phi i32 [ 256, %true_block ], [ %.1, %after_for3.loopexit ]
  %98 = sitofp i32 %.027.lcssa to float
  %99 = sitofp i32 %.026.lcssa to float
  %100 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 5
  %101 = load float, float* %100, align 4
  %102 = fmul reassoc ninf nsz float %101, %99
  %103 = fcmp reassoc ninf nsz oge float %102, %98
  %104 = icmp slt i32 %.027.lcssa, 81
  %.0 = and i1 %104, %103
  %105 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 2, i32 1
  %106 = load i32*, i32** %105, align 8
  %107 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 2, i32 0, i32 1
  %.029.lcssa. = select i1 %.0, i32 %.029.lcssa, i32 -1
  %.027.lcssa. = select i1 %.0, i32 %.027.lcssa, i32 -1
  %108 = load i32, i32* %107, align 4
  %109 = mul i32 %108, %.03141
  %110 = sext i32 %109 to i64
  %111 = getelementptr i32, i32* %106, i64 %110
  store i32 %.029.lcssa., i32* %111, align 4
  %112 = load i32*, i32** %105, align 8
  %113 = load i32, i32* %107, align 4
  %114 = mul i32 %113, %.03141
  %115 = add i32 %114, 1
  %116 = sext i32 %115 to i64
  %117 = getelementptr i32, i32* %112, i64 %116
  store i32 %.027.lcssa., i32* %117, align 4
  br label %after_if

after_if7:                                        ; preds = %false_block13, %for_loop_test11.preheader.after_if7_crit_edge, %for_loop_body1
  %.130 = phi i32 [ %.02935, %for_loop_body1 ], [ %.02538, %for_loop_test11.preheader.after_if7_crit_edge ], [ %.02935, %false_block13 ]
  %.128 = phi i32 [ %.02736, %for_loop_body1 ], [ %96, %for_loop_test11.preheader.after_if7_crit_edge ], [ %.02736, %false_block13 ]
  %.1 = phi i32 [ %.02637, %for_loop_body1 ], [ %.02736, %for_loop_test11.preheader.after_if7_crit_edge ], [ %119, %false_block13 ]
  %118 = add nuw nsw i32 %.02538, 1
  %exitcond.not = icmp eq i32 %31, %118
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1

false_block13:                                    ; preds = %for_loop_test11.preheader
  %119 = tail call i32 @llvm.smin.i32(i32 %96, i32 %.02637)
  br label %after_if7
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare i32 @llvm.vector.reduce.add.v8i32(<8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*>, i32 immarg, <8 x i1>, <8 x i32>) #8

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }

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
