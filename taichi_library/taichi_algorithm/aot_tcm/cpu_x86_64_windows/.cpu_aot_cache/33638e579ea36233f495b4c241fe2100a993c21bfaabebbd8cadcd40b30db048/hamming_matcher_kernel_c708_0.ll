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

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @hamming_matcher_kernel_c708_0_kernel_0_serial(%struct.RuntimeContext.60* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.60* %context to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }**
  %1 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %1, i64 0, i32 3, i32 1
  %3 = load i32*, i32** %2, align 8
  %4 = load i32, i32* %3, align 4
  %5 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %6 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %5, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %6, i64 0, i32 14
  %8 = load i8*, i8** %7, align 8
  %9 = getelementptr inbounds i8, i8* %8, i64 4
  %10 = bitcast i8* %9 to i32*
  store i32 %4, i32* %10, align 4
  %11 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %11, i64 0, i32 4, i32 1
  %13 = load i32*, i32** %12, align 8
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %5, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %20, i64 0, i32 0, i32 0, i32 0
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %5, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %23, i64 0, i32 14
  %25 = bitcast i8** %24 to i32**
  %26 = load i32*, i32** %25, align 8
  store i32 %22, i32* %26, align 4
  ret void
}

; Function Attrs: nounwind
define void @hamming_matcher_kernel_c708_0_kernel_1_range_for(%struct.RuntimeContext.60* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nosync nounwind
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.60* %0 to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }**
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.03141 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %40, %after_if ]
  %22 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %22, i64 0, i32 14
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
  %exitcond44.not = icmp eq i32 %40, %19
  br i1 %exitcond44.not, label %after_for.loopexit, label %for_loop_body

for_loop_body1:                                   ; preds = %after_if7, %for_loop_body1.lr.ph
  %.02538 = phi i32 [ 0, %for_loop_body1.lr.ph ], [ %119, %after_if7 ]
  %.02637 = phi i32 [ 512, %for_loop_body1.lr.ph ], [ %.1, %after_if7 ]
  %.02736 = phi i32 [ 512, %for_loop_body1.lr.ph ], [ %.128, %after_if7 ]
  %.02935 = phi i32 [ -1, %for_loop_body1.lr.ph ], [ %.130, %after_if7 ]
  %41 = icmp slt i32 %.02538, %35
  br i1 %41, label %for_loop_test11.preheader, label %after_if7

for_loop_test11.preheader:                        ; preds = %for_loop_body1
  %42 = load i32*, i32** %36, align 8
  %43 = load i32, i32* %37, align 4
  %44 = mul i32 %43, %.03141
  %45 = load i32*, i32** %38, align 8
  %46 = load i32, i32* %39, align 4
  %47 = mul i32 %46, %.02538
  %48 = icmp sgt i32 %44, 2147483632
  %49 = icmp sgt i32 %47, 2147483632
  %50 = or i1 %48, %49
  br i1 %50, label %for_loop_body8.preheader, label %vector.body

for_loop_body8.preheader:                         ; preds = %for_loop_test11.preheader
  br label %for_loop_body8

vector.body:                                      ; preds = %for_loop_test11.preheader
  %51 = sext i32 %44 to i64
  %52 = getelementptr i32, i32* %42, i64 %51
  %53 = bitcast i32* %52 to <8 x i32>*
  %wide.load = load <8 x i32>, <8 x i32>* %53, align 4
  %54 = sext i32 %47 to i64
  %55 = getelementptr i32, i32* %45, i64 %54
  %56 = bitcast i32* %55 to <8 x i32>*
  %wide.load55 = load <8 x i32>, <8 x i32>* %56, align 4
  %57 = xor <8 x i32> %wide.load55, %wide.load
  %58 = lshr <8 x i32> %57, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %59 = and <8 x i32> %58, <i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765>
  %60 = sub <8 x i32> %57, %59
  %61 = and <8 x i32> %60, <i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459>
  %62 = lshr <8 x i32> %60, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %63 = and <8 x i32> %62, <i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459>
  %64 = add nuw nsw <8 x i32> %63, %61
  %65 = lshr <8 x i32> %64, <i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4>
  %66 = add nuw nsw <8 x i32> %65, %64
  %67 = and <8 x i32> %66, <i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135>
  %68 = lshr <8 x i32> %67, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %69 = add nuw nsw <8 x i32> %68, %67
  %70 = lshr <8 x i32> %69, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %71 = add nuw nsw <8 x i32> %70, %69
  %72 = and <8 x i32> %71, <i32 63, i32 63, i32 63, i32 63, i32 63, i32 63, i32 63, i32 63>
  %73 = add i32 %44, 8
  %74 = sext i32 %73 to i64
  %75 = getelementptr i32, i32* %42, i64 %74
  %76 = bitcast i32* %75 to <8 x i32>*
  %wide.load.1 = load <8 x i32>, <8 x i32>* %76, align 4
  %77 = add i32 %47, 8
  %78 = sext i32 %77 to i64
  %79 = getelementptr i32, i32* %45, i64 %78
  %80 = bitcast i32* %79 to <8 x i32>*
  %wide.load55.1 = load <8 x i32>, <8 x i32>* %80, align 4
  %81 = xor <8 x i32> %wide.load55.1, %wide.load.1
  %82 = lshr <8 x i32> %81, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %83 = and <8 x i32> %82, <i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765, i32 1431655765>
  %84 = sub <8 x i32> %81, %83
  %85 = and <8 x i32> %84, <i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459>
  %86 = lshr <8 x i32> %84, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
  %87 = and <8 x i32> %86, <i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459, i32 858993459>
  %88 = add nuw nsw <8 x i32> %87, %85
  %89 = lshr <8 x i32> %88, <i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4>
  %90 = add nuw nsw <8 x i32> %89, %88
  %91 = and <8 x i32> %90, <i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135, i32 252645135>
  %92 = lshr <8 x i32> %91, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %93 = add nuw nsw <8 x i32> %92, %91
  %94 = lshr <8 x i32> %93, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %95 = add nuw nsw <8 x i32> %94, %93
  %96 = and <8 x i32> %95, <i32 63, i32 63, i32 63, i32 63, i32 63, i32 63, i32 63, i32 63>
  %97 = add nuw nsw <8 x i32> %96, %72
  %98 = call i32 @llvm.vector.reduce.add.v8i32(<8 x i32> %97)
  br label %after_for10

after_for3.loopexit:                              ; preds = %after_if7
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %true_block
  %.029.lcssa = phi i32 [ -1, %true_block ], [ %.130, %after_for3.loopexit ]
  %.027.lcssa = phi i32 [ 512, %true_block ], [ %.128, %after_for3.loopexit ]
  %.026.lcssa = phi i32 [ 512, %true_block ], [ %.1, %after_for3.loopexit ]
  %99 = sitofp i32 %.027.lcssa to float
  %100 = sitofp i32 %.026.lcssa to float
  %101 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 5
  %102 = load float, float* %101, align 4
  %103 = fmul reassoc ninf nsz float %102, %100
  %104 = fcmp reassoc ninf nsz oge float %103, %99
  %105 = icmp slt i32 %.027.lcssa, 161
  %.0 = and i1 %105, %104
  %106 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 2, i32 1
  %107 = load i32*, i32** %106, align 8
  %108 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, { { i32 }, i32* }, float }* %29, i64 0, i32 2, i32 0, i32 1
  %.029.lcssa. = select i1 %.0, i32 %.029.lcssa, i32 -1
  %.027.lcssa. = select i1 %.0, i32 %.027.lcssa, i32 -1
  %109 = load i32, i32* %108, align 4
  %110 = mul i32 %109, %.03141
  %111 = sext i32 %110 to i64
  %112 = getelementptr i32, i32* %107, i64 %111
  store i32 %.029.lcssa., i32* %112, align 4
  %113 = load i32*, i32** %106, align 8
  %114 = load i32, i32* %108, align 4
  %115 = mul i32 %114, %.03141
  %116 = add i32 %115, 1
  %117 = sext i32 %116 to i64
  %118 = getelementptr i32, i32* %113, i64 %117
  store i32 %.027.lcssa., i32* %118, align 4
  br label %after_if

after_if7:                                        ; preds = %false_block13, %after_for10, %for_loop_body1
  %.130 = phi i32 [ %.02935, %for_loop_body1 ], [ %.02538, %after_for10 ], [ %.02935, %false_block13 ]
  %.128 = phi i32 [ %.02736, %for_loop_body1 ], [ %.lcssa, %after_for10 ], [ %.02736, %false_block13 ]
  %.1 = phi i32 [ %.02637, %for_loop_body1 ], [ %.02736, %after_for10 ], [ %169, %false_block13 ]
  %119 = add nuw nsw i32 %.02538, 1
  %exitcond43.not = icmp eq i32 %119, %31
  br i1 %exitcond43.not, label %after_for3.loopexit, label %for_loop_body1

for_loop_body8:                                   ; preds = %for_loop_body8, %for_loop_body8.preheader
  %lsr.iv61 = phi i64 [ 16, %for_loop_body8.preheader ], [ %lsr.iv.next62, %for_loop_body8 ]
  %lsr.iv59 = phi i32 [ %47, %for_loop_body8.preheader ], [ %lsr.iv.next60, %for_loop_body8 ]
  %lsr.iv = phi i32 [ %44, %for_loop_body8.preheader ], [ %lsr.iv.next, %for_loop_body8 ]
  %.02433 = phi i32 [ %167, %for_loop_body8 ], [ 0, %for_loop_body8.preheader ]
  %120 = sext i32 %lsr.iv to i64
  %121 = getelementptr i32, i32* %42, i64 %120
  %122 = load i32, i32* %121, align 4
  %123 = sext i32 %lsr.iv59 to i64
  %124 = getelementptr i32, i32* %45, i64 %123
  %125 = load i32, i32* %124, align 4
  %126 = xor i32 %125, %122
  %127 = lshr i32 %126, 1
  %128 = and i32 %127, 1431655765
  %129 = sub i32 %126, %128
  %130 = and i32 %129, 858993459
  %131 = lshr i32 %129, 2
  %132 = and i32 %131, 858993459
  %133 = add nuw nsw i32 %132, %130
  %134 = lshr i32 %133, 4
  %135 = add nuw nsw i32 %134, %133
  %136 = and i32 %135, 252645135
  %137 = lshr i32 %136, 8
  %138 = add nuw nsw i32 %137, %136
  %139 = lshr i32 %138, 16
  %140 = add nuw nsw i32 %139, %138
  %141 = and i32 %140, 63
  %142 = add i32 %141, %.02433
  %143 = add i32 %lsr.iv, 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr i32, i32* %42, i64 %144
  %146 = load i32, i32* %145, align 4
  %147 = add i32 %lsr.iv59, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr i32, i32* %45, i64 %148
  %150 = load i32, i32* %149, align 4
  %151 = xor i32 %150, %146
  %152 = lshr i32 %151, 1
  %153 = and i32 %152, 1431655765
  %154 = sub i32 %151, %153
  %155 = and i32 %154, 858993459
  %156 = lshr i32 %154, 2
  %157 = and i32 %156, 858993459
  %158 = add nuw nsw i32 %157, %155
  %159 = lshr i32 %158, 4
  %160 = add nuw nsw i32 %159, %158
  %161 = and i32 %160, 252645135
  %162 = lshr i32 %161, 8
  %163 = add nuw nsw i32 %162, %161
  %164 = lshr i32 %163, 16
  %165 = add nuw nsw i32 %164, %163
  %166 = and i32 %165, 63
  %167 = add i32 %166, %142
  %lsr.iv.next = add i32 %lsr.iv, 2
  %lsr.iv.next60 = add i32 %lsr.iv59, 2
  %lsr.iv.next62 = add nsw i64 %lsr.iv61, -2
  %exitcond.not.1 = icmp eq i64 %lsr.iv.next62, 0
  br i1 %exitcond.not.1, label %after_for10.loopexit, label %for_loop_body8, !llvm.loop !9

after_for10.loopexit:                             ; preds = %for_loop_body8
  br label %after_for10

after_for10:                                      ; preds = %after_for10.loopexit, %vector.body
  %.lcssa = phi i32 [ %98, %vector.body ], [ %167, %after_for10.loopexit ]
  %168 = icmp slt i32 %.lcssa, %.02736
  br i1 %168, label %after_if7, label %false_block13

false_block13:                                    ; preds = %after_for10
  %169 = tail call i32 @llvm.smin.i32(i32 %.lcssa, i32 %.02637)
  br label %after_if7
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !11

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !13

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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone willreturn }

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
!11 = distinct !{!11, !12}
!12 = !{!"llvm.loop.mustprogress"}
!13 = distinct !{!13, !12}
