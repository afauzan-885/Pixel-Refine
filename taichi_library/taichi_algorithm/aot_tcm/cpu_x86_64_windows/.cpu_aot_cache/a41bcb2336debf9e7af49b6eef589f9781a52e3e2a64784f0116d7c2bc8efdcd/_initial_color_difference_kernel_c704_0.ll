; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { i8*, %struct.LLVMRuntime.5*, i32, i64* }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.2*], [1024 x %struct.NodeManager.3*], [1024 x i8*], i8*, %struct.RandState.4*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { i8*, i8*, i64 }
%struct.ListManager.2 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.5* }
%struct.NodeManager.3 = type { %struct.LLVMRuntime.5*, i32, i32, i32, i32, %struct.ListManager.2*, %struct.ListManager.2*, %struct.ListManager.2*, i32 }
%struct.RandState.4 = type { i32, i32, i32, i32, i32 }
%struct.range_task_helper_context = type { %struct.RuntimeContext.6*, void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*)*, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_initial_color_difference_kernel_c84_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %1 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %2 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %1, i64 0, i32 14
  %3 = load i8*, i8** %2, align 8
  %4 = getelementptr inbounds i8, i8* %3, i64 8
  %5 = bitcast i8* %4 to i32*
  store i32 0, i32* %5, align 4
  %6 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %7 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %6, i64 0, i32 14
  %8 = load i8*, i8** %7, align 8
  %9 = getelementptr inbounds i8, i8* %8, i64 12
  %10 = bitcast i8* %9 to i32*
  store i32 0, i32* %10, align 4
  %11 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %12 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %11, i64 0, i32 14
  %13 = load i8*, i8** %12, align 8
  %14 = getelementptr inbounds i8, i8* %13, i64 24
  %15 = bitcast i8* %14 to i32*
  store i32 0, i32* %15, align 4
  %16 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %17 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %16, i64 0, i32 14
  %18 = load i8*, i8** %17, align 8
  %19 = getelementptr inbounds i8, i8* %18, i64 28
  %20 = bitcast i8* %19 to i32*
  store i32 0, i32* %20, align 4
  %21 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 6
  %24 = load i32, i32* %23, align 4
  %cond = icmp eq i32 %24, 0
  br i1 %cond, label %false_block11, label %false_block

false_block:                                      ; preds = %entry
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 7
  %26 = load i32, i32* %25, align 4
  %27 = icmp eq i32 %26, 0
  br i1 %27, label %after_if.sink.split, label %false_block2

after_if.sink.split:                              ; preds = %true_block7, %false_block2, %false_block
  %.sink = phi i32* [ %10, %true_block7 ], [ %10, %false_block ], [ %5, %false_block2 ]
  store i32 1, i32* %.sink, align 4
  br label %after_if

after_if:                                         ; preds = %false_block5, %after_if.sink.split
  %28 = icmp eq i32 %24, 2
  br i1 %28, label %after_if12, label %after_if.false_block11_crit_edge

after_if.false_block11_crit_edge:                 ; preds = %after_if
  %.pre = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %21, align 8
  br label %false_block11

false_block2:                                     ; preds = %false_block
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 8
  %30 = load i32, i32* %29, align 4
  %31 = icmp eq i32 %30, 0
  br i1 %31, label %after_if.sink.split, label %false_block5

false_block5:                                     ; preds = %false_block2
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 9
  %33 = load i32, i32* %32, align 4
  %34 = icmp eq i32 %33, 0
  br i1 %34, label %true_block7, label %after_if

true_block7:                                      ; preds = %false_block5
  store i32 1, i32* %5, align 4
  br label %after_if.sink.split

false_block11:                                    ; preds = %after_if.false_block11_crit_edge, %entry
  %35 = phi { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* [ %.pre, %after_if.false_block11_crit_edge ], [ %22, %entry ]
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %35, i64 0, i32 7
  %37 = load i32, i32* %36, align 4
  %38 = icmp eq i32 %37, 2
  br i1 %38, label %after_if12.sink.split, label %false_block14

after_if12.sink.split:                            ; preds = %true_block19, %false_block14, %false_block11
  %.sink1 = phi i32* [ %20, %true_block19 ], [ %20, %false_block11 ], [ %15, %false_block14 ]
  store i32 1, i32* %.sink1, align 4
  br label %after_if12

after_if12:                                       ; preds = %false_block17, %after_if12.sink.split, %after_if
  %39 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %39, i64 0, i32 4
  %41 = load i32, i32* %40, align 4
  %42 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %43 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %42, i64 0, i32 14
  %44 = load i8*, i8** %43, align 8
  %45 = getelementptr inbounds i8, i8* %44, i64 20
  %46 = bitcast i8* %45 to i32*
  store i32 %41, i32* %46, align 4
  %47 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %48 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %49 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %48, i64 0, i32 5
  %50 = load i32, i32* %49, align 4
  %51 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %51, i64 0, i32 14
  %53 = load i8*, i8** %52, align 8
  %54 = getelementptr inbounds i8, i8* %53, i64 16
  %55 = bitcast i8* %54 to i32*
  store i32 %50, i32* %55, align 4
  %56 = tail call i32 @llvm.smax.i32(i32 %50, i32 0)
  %57 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %58 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %57, i64 0, i32 14
  %59 = load i8*, i8** %58, align 8
  %60 = getelementptr inbounds i8, i8* %59, i64 4
  %61 = bitcast i8* %60 to i32*
  store i32 %56, i32* %61, align 4
  %62 = mul i32 %56, %47
  %63 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %0, align 8
  %64 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %63, i64 0, i32 14
  %65 = bitcast i8** %64 to i32**
  %66 = load i32*, i32** %65, align 8
  store i32 %62, i32* %66, align 4
  ret void

false_block14:                                    ; preds = %false_block11
  %67 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %35, i64 0, i32 8
  %68 = load i32, i32* %67, align 4
  %69 = icmp eq i32 %68, 2
  br i1 %69, label %after_if12.sink.split, label %false_block17

false_block17:                                    ; preds = %false_block14
  %70 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %35, i64 0, i32 9
  %71 = load i32, i32* %70, align 4
  %72 = icmp eq i32 %71, 2
  br i1 %72, label %true_block19, label %after_if12

true_block19:                                     ; preds = %false_block17
  store i32 1, i32* %15, align 4
  br label %after_if12.sink.split
}

; Function Attrs: nounwind
define void @_initial_color_difference_kernel_c84_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast %struct.range_task_helper_context* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 0
  store %struct.RuntimeContext.6* %context, %struct.RuntimeContext.6** %4, align 8
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.6*, i8*, i32)* @function_body, void (%struct.RuntimeContext.6*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 2, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 2, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 3, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 3, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if21, %for_loop_body.lr.ph
  %.01860 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %298, %after_if21 ]
  %27 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 4
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sdiv i32 %.01860, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.01860
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.01860, 0
  %38 = icmp ne i32 %.01860, %34
  %39 = and i1 %37, %36
  %40 = and i1 %39, %38
  %.neg24 = sext i1 %40 to i32
  %41 = add i32 %33, %.neg24
  %42 = mul i32 %41, %32
  %43 = mul i32 %32, -1
  %44 = mul i32 %43, %41
  %45 = add i32 %.01860, %44
  %46 = getelementptr inbounds i8, i8* %29, i64 8
  %47 = bitcast i8* %46 to i32*
  %48 = load i32, i32* %47, align 4
  %49 = sub i32 %41, %48
  %50 = sdiv i32 %49, 2
  %51 = icmp slt i32 %49, 0
  %52 = shl nsw i32 %50, 1
  %53 = icmp ne i32 %52, %49
  %54 = and i1 %51, %53
  %.neg25.neg = zext i1 %54 to i32
  %.neg27 = sub nsw i32 %.neg25.neg, %50
  %.neg26 = shl i32 %.neg27, 1
  %55 = getelementptr inbounds i8, i8* %29, i64 12
  %56 = bitcast i8* %55 to i32*
  %57 = load i32, i32* %56, align 4
  %58 = sub i32 %44, %57
  %59 = add i32 %.01860, %58
  %60 = sdiv i32 %59, 2
  %61 = icmp slt i32 %59, 0
  %62 = shl i32 %60, 1
  %63 = icmp ne i32 %59, %62
  %64 = and i1 %61, %63
  %.neg28.neg = zext i1 %64 to i32
  %65 = add i32 %57, %62
  %66 = shl nuw nsw i32 %.neg28.neg, 1
  %67 = sub i32 %65, %66
  %68 = mul i32 %67, -1
  %69 = add i32 %45, %68
  %70 = sub i32 0, %49
  %71 = icmp eq i32 %.neg26, %70
  %72 = icmp eq i32 %69, 0
  %spec.select = select i1 %71, i1 %72, i1 false
  br i1 %spec.select, label %true_block1, label %false_block2

after_for.loopexit:                               ; preds = %after_if21
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body
  %73 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %74 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 0, i32 1
  %75 = load float*, float** %74, align 8
  %76 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 0, i32 0, i32 1
  %77 = load i32, i32* %76, align 4
  %78 = sub i32 %77, %32
  %79 = mul i32 %78, %41
  %80 = add i32 %.01860, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %75, i64 %81
  %83 = load float, float* %82, align 4
  %84 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 1, i32 1
  %85 = load float*, float** %84, align 8
  %86 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %73, i64 0, i32 1, i32 0, i32 1
  %87 = load i32, i32* %86, align 4
  %88 = sub i32 %87, %32
  %89 = mul i32 %88, %41
  %90 = add i32 %.01860, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, float* %85, i64 %91
  %93 = load float, float* %92, align 4
  %94 = fsub reassoc ninf nsz float %83, %93
  br label %after_if3

false_block2:                                     ; preds = %for_loop_body
  %95 = icmp ne i32 %69, 0
  %spec.select38 = select i1 %71, i1 %95, i1 false
  br i1 %spec.select38, label %true_block7, label %false_block8

after_if3:                                        ; preds = %false_block14, %true_block13, %true_block7, %true_block1
  %.017 = phi float [ %94, %true_block1 ], [ %177, %true_block7 ], [ %227, %true_block13 ], [ %267, %false_block14 ]
  %96 = load float*, float** %23, align 8
  %97 = load i32, i32* %24, align 4
  %98 = sub i32 %97, %32
  %99 = mul i32 %98, %41
  %100 = add i32 %.01860, %99
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %96, i64 %101
  store float %.017, float* %102, align 4
  %103 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %104 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %103, i64 0, i32 14
  %105 = load i8*, i8** %104, align 8
  %106 = getelementptr inbounds i8, i8* %105, i64 24
  %107 = bitcast i8* %106 to i32*
  %108 = load i32, i32* %107, align 4
  %109 = sub i32 %41, %108
  %110 = sdiv i32 %109, 2
  %111 = icmp slt i32 %109, 0
  %112 = shl nsw i32 %110, 1
  %113 = icmp ne i32 %112, %109
  %114 = and i1 %111, %113
  %.neg31.neg = zext i1 %114 to i32
  %.neg33 = sub nsw i32 %.neg31.neg, %110
  %.neg32 = shl i32 %.neg33, 1
  %115 = getelementptr inbounds i8, i8* %105, i64 28
  %116 = bitcast i8* %115 to i32*
  %117 = load i32, i32* %116, align 4
  %118 = sub i32 %44, %117
  %119 = add i32 %.01860, %118
  %120 = sdiv i32 %119, 2
  %121 = icmp slt i32 %119, 0
  %122 = shl i32 %120, 1
  %123 = icmp ne i32 %119, %122
  %124 = and i1 %121, %123
  %.neg34.neg = zext i1 %124 to i32
  %125 = add i32 %117, %122
  %126 = shl nuw nsw i32 %.neg34.neg, 1
  %127 = sub i32 %125, %126
  %128 = mul i32 %127, -1
  %129 = add i32 %45, %128
  %130 = sub i32 0, %109
  %131 = icmp eq i32 %.neg32, %130
  %132 = icmp eq i32 %129, 0
  %spec.select39 = select i1 %131, i1 %132, i1 false
  br i1 %spec.select39, label %true_block19, label %false_block20

true_block7:                                      ; preds = %false_block2
  %133 = insertelement <2 x i32> poison, i32 %45, i64 0
  %134 = shufflevector <2 x i32> %133, <2 x i32> poison, <2 x i32> zeroinitializer
  %135 = add <2 x i32> %134, <i32 -1, i32 1>
  %136 = getelementptr inbounds i8, i8* %29, i64 16
  %137 = bitcast i8* %136 to i32*
  %138 = load i32, i32* %137, align 4
  %139 = add i32 %138, -1
  %140 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %141 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %140, i64 0, i32 0, i32 1
  %142 = load float*, float** %141, align 8
  %143 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %140, i64 0, i32 0, i32 0, i32 1
  %144 = load i32, i32* %143, align 4
  %145 = mul i32 %144, %41
  %146 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %140, i64 0, i32 1, i32 1
  %147 = load float*, float** %146, align 8
  %148 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %140, i64 0, i32 1, i32 0, i32 1
  %149 = load i32, i32* %148, align 4
  %150 = mul i32 %149, %41
  %151 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %135, <2 x i32> zeroinitializer)
  %152 = insertelement <2 x i32> poison, i32 %139, i64 0
  %153 = shufflevector <2 x i32> %152, <2 x i32> poison, <2 x i32> zeroinitializer
  %154 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %153, <2 x i32> %151)
  %155 = extractelement <2 x i32> %154, i64 0
  %156 = add i32 %150, %155
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %147, i64 %157
  %159 = load float, float* %158, align 4
  %160 = insertelement <2 x i32> poison, i32 %145, i64 0
  %161 = shufflevector <2 x i32> %160, <2 x i32> poison, <2 x i32> zeroinitializer
  %162 = add <2 x i32> %161, %154
  %163 = sext <2 x i32> %162 to <2 x i64>
  %164 = insertelement <2 x float*> poison, float* %142, i64 0
  %165 = shufflevector <2 x float*> %164, <2 x float*> poison, <2 x i32> zeroinitializer
  %166 = getelementptr float, <2 x float*> %165, <2 x i64> %163
  %167 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %166, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %168 = extractelement <2 x i32> %154, i64 1
  %169 = add i32 %150, %168
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, float* %147, i64 %170
  %172 = load float, float* %171, align 4
  %shift = shufflevector <2 x float> %167, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %173 = fadd reassoc ninf nsz <2 x float> %167, %shift
  %174 = extractelement <2 x float> %173, i64 0
  %175 = fadd reassoc ninf nsz float %159, %172
  %176 = fsub reassoc ninf nsz float %174, %175
  %177 = fmul reassoc ninf nsz float %176, 5.000000e-01
  br label %after_if3

false_block8:                                     ; preds = %false_block2
  %not. = xor i1 %71, true
  %spec.select40 = select i1 %not., i1 %72, i1 false
  %178 = insertelement <2 x i32> poison, i32 %41, i64 0
  %179 = shufflevector <2 x i32> %178, <2 x i32> poison, <2 x i32> zeroinitializer
  %180 = add <2 x i32> %179, <i32 1, i32 -1>
  %181 = getelementptr inbounds i8, i8* %29, i64 20
  %182 = bitcast i8* %181 to i32*
  %183 = load i32, i32* %182, align 4
  %184 = add i32 %183, -1
  %185 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %180, <2 x i32> zeroinitializer)
  %186 = insertelement <2 x i32> poison, i32 %184, i64 0
  %187 = shufflevector <2 x i32> %186, <2 x i32> poison, <2 x i32> zeroinitializer
  %188 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %187, <2 x i32> %185)
  br i1 %spec.select40, label %true_block13, label %false_block14

true_block13:                                     ; preds = %false_block8
  %189 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %190 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %189, i64 0, i32 0, i32 1
  %191 = load float*, float** %190, align 8
  %192 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %189, i64 0, i32 0, i32 0, i32 1
  %193 = load i32, i32* %192, align 4
  %194 = extractelement <2 x i32> %188, i64 1
  %195 = mul i32 %193, %194
  %196 = sub i32 %195, %42
  %197 = add i32 %.01860, %196
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, float* %191, i64 %198
  %200 = load float, float* %199, align 4
  %201 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %189, i64 0, i32 1, i32 1
  %202 = load float*, float** %201, align 8
  %203 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %189, i64 0, i32 1, i32 0, i32 1
  %204 = load i32, i32* %203, align 4
  %205 = mul i32 %204, %194
  %206 = sub i32 %205, %42
  %207 = add i32 %.01860, %206
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, float* %202, i64 %208
  %210 = load float, float* %209, align 4
  %211 = extractelement <2 x i32> %188, i64 0
  %212 = mul i32 %193, %211
  %213 = sub i32 %212, %42
  %214 = add i32 %.01860, %213
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, float* %191, i64 %215
  %217 = load float, float* %216, align 4
  %218 = mul i32 %204, %211
  %219 = sub i32 %218, %42
  %220 = add i32 %.01860, %219
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %202, i64 %221
  %223 = load float, float* %222, align 4
  %224 = fadd reassoc ninf nsz float %200, %217
  %225 = fadd reassoc ninf nsz float %210, %223
  %226 = fsub reassoc ninf nsz float %224, %225
  %227 = fmul reassoc ninf nsz float %226, 5.000000e-01
  br label %after_if3

false_block14:                                    ; preds = %false_block8
  %228 = insertelement <2 x i32> poison, i32 %45, i64 0
  %229 = shufflevector <2 x i32> %228, <2 x i32> poison, <2 x i32> zeroinitializer
  %230 = add <2 x i32> %229, <i32 1, i32 -1>
  %231 = getelementptr inbounds i8, i8* %29, i64 16
  %232 = bitcast i8* %231 to i32*
  %233 = load i32, i32* %232, align 4
  %234 = add i32 %233, -1
  %235 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %236 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %235, i64 0, i32 0, i32 1
  %237 = load float*, float** %236, align 8
  %238 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %235, i64 0, i32 0, i32 0, i32 1
  %239 = load i32, i32* %238, align 4
  %240 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %235, i64 0, i32 1, i32 1
  %241 = load float*, float** %240, align 8
  %242 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %235, i64 0, i32 1, i32 0, i32 1
  %243 = load i32, i32* %242, align 4
  %244 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %230, <2 x i32> zeroinitializer)
  %245 = insertelement <2 x i32> poison, i32 %234, i64 0
  %246 = shufflevector <2 x i32> %245, <2 x i32> poison, <2 x i32> zeroinitializer
  %247 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %246, <2 x i32> %244)
  %shuffle67 = shufflevector <2 x i32> %247, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 1, i32 0>
  %248 = insertelement <2 x i32> poison, i32 %239, i64 0
  %249 = shufflevector <2 x i32> %248, <2 x i32> poison, <2 x i32> zeroinitializer
  %250 = mul <2 x i32> %249, %188
  %shuffle66 = shufflevector <2 x i32> %250, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %251 = add <4 x i32> %shuffle66, %shuffle67
  %252 = sext <4 x i32> %251 to <4 x i64>
  %253 = insertelement <4 x float*> poison, float* %237, i64 0
  %shuffle65 = shufflevector <4 x float*> %253, <4 x float*> poison, <4 x i32> zeroinitializer
  %254 = getelementptr float, <4 x float*> %shuffle65, <4 x i64> %252
  %255 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %254, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %256 = insertelement <2 x i32> poison, i32 %243, i64 0
  %257 = shufflevector <2 x i32> %256, <2 x i32> poison, <2 x i32> zeroinitializer
  %258 = mul <2 x i32> %257, %188
  %shuffle69 = shufflevector <2 x i32> %258, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %259 = shufflevector <2 x i32> %247, <2 x i32> undef, <4 x i32> <i32 0, i32 1, i32 1, i32 0>
  %260 = add <4 x i32> %shuffle69, %259
  %261 = sext <4 x i32> %260 to <4 x i64>
  %262 = insertelement <4 x float*> poison, float* %241, i64 0
  %shuffle68 = shufflevector <4 x float*> %262, <4 x float*> poison, <4 x i32> zeroinitializer
  %263 = getelementptr float, <4 x float*> %shuffle68, <4 x i64> %261
  %264 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %263, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %265 = fsub reassoc ninf nsz <4 x float> %255, %264
  %266 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %265)
  %267 = fmul reassoc ninf nsz float %266, 2.500000e-01
  br label %after_if3

true_block19:                                     ; preds = %after_if3
  %268 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %269 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %268, i64 0, i32 0, i32 1
  %270 = load float*, float** %269, align 8
  %271 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %268, i64 0, i32 0, i32 0, i32 1
  %272 = load i32, i32* %271, align 4
  %273 = sub i32 %272, %32
  %274 = mul i32 %273, %41
  %275 = add i32 %.01860, %274
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, float* %270, i64 %276
  %278 = load float, float* %277, align 4
  %279 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %268, i64 0, i32 1, i32 1
  %280 = load float*, float** %279, align 8
  %281 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %268, i64 0, i32 1, i32 0, i32 1
  %282 = load i32, i32* %281, align 4
  %283 = sub i32 %282, %32
  %284 = mul i32 %283, %41
  %285 = add i32 %.01860, %284
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, float* %280, i64 %286
  %288 = load float, float* %287, align 4
  %289 = fsub reassoc ninf nsz float %278, %288
  br label %after_if21

false_block20:                                    ; preds = %after_if3
  %290 = icmp ne i32 %129, 0
  %spec.select41 = select i1 %131, i1 %290, i1 false
  br i1 %spec.select41, label %true_block25, label %false_block26

after_if21:                                       ; preds = %false_block32, %true_block31, %true_block25, %true_block19
  %.013 = phi float [ %289, %true_block19 ], [ %343, %true_block25 ], [ %393, %true_block31 ], [ %433, %false_block32 ]
  %291 = load float*, float** %25, align 8
  %292 = load i32, i32* %26, align 4
  %293 = sub i32 %292, %32
  %294 = mul i32 %293, %41
  %295 = add i32 %.01860, %294
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, float* %291, i64 %296
  store float %.013, float* %297, align 4
  %298 = add nsw i32 %.01860, 1
  %exitcond.not = icmp eq i32 %19, %298
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block25:                                     ; preds = %false_block20
  %299 = insertelement <2 x i32> poison, i32 %45, i64 0
  %300 = shufflevector <2 x i32> %299, <2 x i32> poison, <2 x i32> zeroinitializer
  %301 = add <2 x i32> %300, <i32 -1, i32 1>
  %302 = getelementptr inbounds i8, i8* %105, i64 16
  %303 = bitcast i8* %302 to i32*
  %304 = load i32, i32* %303, align 4
  %305 = add i32 %304, -1
  %306 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %307 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %306, i64 0, i32 0, i32 1
  %308 = load float*, float** %307, align 8
  %309 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %306, i64 0, i32 0, i32 0, i32 1
  %310 = load i32, i32* %309, align 4
  %311 = mul i32 %310, %41
  %312 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %306, i64 0, i32 1, i32 1
  %313 = load float*, float** %312, align 8
  %314 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %306, i64 0, i32 1, i32 0, i32 1
  %315 = load i32, i32* %314, align 4
  %316 = mul i32 %315, %41
  %317 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %301, <2 x i32> zeroinitializer)
  %318 = insertelement <2 x i32> poison, i32 %305, i64 0
  %319 = shufflevector <2 x i32> %318, <2 x i32> poison, <2 x i32> zeroinitializer
  %320 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %319, <2 x i32> %317)
  %321 = extractelement <2 x i32> %320, i64 0
  %322 = add i32 %316, %321
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, float* %313, i64 %323
  %325 = load float, float* %324, align 4
  %326 = insertelement <2 x i32> poison, i32 %311, i64 0
  %327 = shufflevector <2 x i32> %326, <2 x i32> poison, <2 x i32> zeroinitializer
  %328 = add <2 x i32> %327, %320
  %329 = sext <2 x i32> %328 to <2 x i64>
  %330 = insertelement <2 x float*> poison, float* %308, i64 0
  %331 = shufflevector <2 x float*> %330, <2 x float*> poison, <2 x i32> zeroinitializer
  %332 = getelementptr float, <2 x float*> %331, <2 x i64> %329
  %333 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %332, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %334 = extractelement <2 x i32> %320, i64 1
  %335 = add i32 %316, %334
  %336 = sext i32 %335 to i64
  %337 = getelementptr float, float* %313, i64 %336
  %338 = load float, float* %337, align 4
  %shift70 = shufflevector <2 x float> %333, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %339 = fadd reassoc ninf nsz <2 x float> %333, %shift70
  %340 = extractelement <2 x float> %339, i64 0
  %341 = fadd reassoc ninf nsz float %325, %338
  %342 = fsub reassoc ninf nsz float %340, %341
  %343 = fmul reassoc ninf nsz float %342, 5.000000e-01
  br label %after_if21

false_block26:                                    ; preds = %false_block20
  %not.43 = xor i1 %131, true
  %spec.select42 = select i1 %not.43, i1 %132, i1 false
  %344 = insertelement <2 x i32> poison, i32 %41, i64 0
  %345 = shufflevector <2 x i32> %344, <2 x i32> poison, <2 x i32> zeroinitializer
  %346 = add <2 x i32> %345, <i32 1, i32 -1>
  %347 = getelementptr inbounds i8, i8* %105, i64 20
  %348 = bitcast i8* %347 to i32*
  %349 = load i32, i32* %348, align 4
  %350 = add i32 %349, -1
  %351 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %346, <2 x i32> zeroinitializer)
  %352 = insertelement <2 x i32> poison, i32 %350, i64 0
  %353 = shufflevector <2 x i32> %352, <2 x i32> poison, <2 x i32> zeroinitializer
  %354 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %353, <2 x i32> %351)
  br i1 %spec.select42, label %true_block31, label %false_block32

true_block31:                                     ; preds = %false_block26
  %355 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %356 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %355, i64 0, i32 0, i32 1
  %357 = load float*, float** %356, align 8
  %358 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %355, i64 0, i32 0, i32 0, i32 1
  %359 = load i32, i32* %358, align 4
  %360 = extractelement <2 x i32> %354, i64 1
  %361 = mul i32 %359, %360
  %362 = sub i32 %361, %42
  %363 = add i32 %.01860, %362
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, float* %357, i64 %364
  %366 = load float, float* %365, align 4
  %367 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %355, i64 0, i32 1, i32 1
  %368 = load float*, float** %367, align 8
  %369 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %355, i64 0, i32 1, i32 0, i32 1
  %370 = load i32, i32* %369, align 4
  %371 = mul i32 %370, %360
  %372 = sub i32 %371, %42
  %373 = add i32 %.01860, %372
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, float* %368, i64 %374
  %376 = load float, float* %375, align 4
  %377 = extractelement <2 x i32> %354, i64 0
  %378 = mul i32 %359, %377
  %379 = sub i32 %378, %42
  %380 = add i32 %.01860, %379
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, float* %357, i64 %381
  %383 = load float, float* %382, align 4
  %384 = mul i32 %370, %377
  %385 = sub i32 %384, %42
  %386 = add i32 %.01860, %385
  %387 = sext i32 %386 to i64
  %388 = getelementptr float, float* %368, i64 %387
  %389 = load float, float* %388, align 4
  %390 = fadd reassoc ninf nsz float %366, %383
  %391 = fadd reassoc ninf nsz float %376, %389
  %392 = fsub reassoc ninf nsz float %390, %391
  %393 = fmul reassoc ninf nsz float %392, 5.000000e-01
  br label %after_if21

false_block32:                                    ; preds = %false_block26
  %394 = insertelement <2 x i32> poison, i32 %45, i64 0
  %395 = shufflevector <2 x i32> %394, <2 x i32> poison, <2 x i32> zeroinitializer
  %396 = add <2 x i32> %395, <i32 1, i32 -1>
  %397 = getelementptr inbounds i8, i8* %105, i64 16
  %398 = bitcast i8* %397 to i32*
  %399 = load i32, i32* %398, align 4
  %400 = add i32 %399, -1
  %401 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %402 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %401, i64 0, i32 0, i32 1
  %403 = load float*, float** %402, align 8
  %404 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %401, i64 0, i32 0, i32 0, i32 1
  %405 = load i32, i32* %404, align 4
  %406 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %401, i64 0, i32 1, i32 1
  %407 = load float*, float** %406, align 8
  %408 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %401, i64 0, i32 1, i32 0, i32 1
  %409 = load i32, i32* %408, align 4
  %410 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %396, <2 x i32> zeroinitializer)
  %411 = insertelement <2 x i32> poison, i32 %400, i64 0
  %412 = shufflevector <2 x i32> %411, <2 x i32> poison, <2 x i32> zeroinitializer
  %413 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %412, <2 x i32> %410)
  %shuffle62 = shufflevector <2 x i32> %413, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 1, i32 0>
  %414 = insertelement <2 x i32> poison, i32 %405, i64 0
  %415 = shufflevector <2 x i32> %414, <2 x i32> poison, <2 x i32> zeroinitializer
  %416 = mul <2 x i32> %415, %354
  %shuffle61 = shufflevector <2 x i32> %416, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %417 = add <4 x i32> %shuffle61, %shuffle62
  %418 = sext <4 x i32> %417 to <4 x i64>
  %419 = insertelement <4 x float*> poison, float* %403, i64 0
  %shuffle = shufflevector <4 x float*> %419, <4 x float*> poison, <4 x i32> zeroinitializer
  %420 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %418
  %421 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %420, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %422 = insertelement <2 x i32> poison, i32 %409, i64 0
  %423 = shufflevector <2 x i32> %422, <2 x i32> poison, <2 x i32> zeroinitializer
  %424 = mul <2 x i32> %423, %354
  %shuffle64 = shufflevector <2 x i32> %424, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %425 = shufflevector <2 x i32> %413, <2 x i32> undef, <4 x i32> <i32 0, i32 1, i32 1, i32 0>
  %426 = add <4 x i32> %shuffle64, %425
  %427 = sext <4 x i32> %426 to <4 x i64>
  %428 = insertelement <4 x float*> poison, float* %407, i64 0
  %shuffle63 = shufflevector <4 x float*> %428, <4 x float*> poison, <4 x i32> zeroinitializer
  %429 = getelementptr float, <4 x float*> %shuffle63, <4 x i64> %427
  %430 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %429, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %431 = fsub reassoc ninf nsz <4 x float> %421, %430
  %432 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %431)
  %433 = fmul reassoc ninf nsz float %432, 2.500000e-01
  br label %after_if21
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.6**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.6*, %struct.RuntimeContext.6** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.6* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.6* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #8

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
