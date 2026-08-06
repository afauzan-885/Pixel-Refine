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
define void @_compute_mtb_error_to_buf_c340_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**
  %1 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 12
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %19 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %18, i64 0, i32 14
  %20 = load i8*, i8** %19, align 8
  %21 = getelementptr inbounds i8, i8* %20, i64 16
  %22 = bitcast i8* %21 to i32*
  store i32 0, i32* %22, align 4
  %23 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %24 = tail call i32 @llvm.smax.i32(i32 %12, i32 0)
  %25 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  store i32 %24, i32* %29, align 4
  %30 = mul i32 %24, %23
  %31 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %31, i64 0, i32 14
  %33 = bitcast i8** %32 to i32**
  %34 = load i32*, i32** %33, align 8
  store i32 %30, i32* %34, align 4
  ret void
}

; Function Attrs: nounwind
define void @_compute_mtb_error_to_buf_c340_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.24* %context, %struct.RuntimeContext.24** %4, align 8
  store void (%struct.RuntimeContext.24*, i8*)* @function_body, void (%struct.RuntimeContext.24*, i8*)** %2, align 8
  store i64 8, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.24*, i8*, i32)* @function_body.1, void (%struct.RuntimeContext.24*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.24*, i8*)* @function_body.2, void (%struct.RuntimeContext.24*, i8*)** %6, align 8
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

; Function Attrs: argmemonly mustprogress nofree norecurse nosync nounwind willreturn writeonly
define internal void @function_body(%struct.RuntimeContext.24* nocapture readnone %0, i8* nocapture writeonly %1) #2 {
allocs:
  %2 = bitcast i8* %1 to <2 x i32>*
  store <2 x i32> zeroinitializer, <2 x i32>* %2, align 4
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body.1(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture %1, i32 %2) #3 {
allocs:
  %3 = getelementptr i8, i8* %1, i64 4
  %4 = bitcast i8* %3 to i32*
  %5 = bitcast i8* %1 to i32*
  %6 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %0, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %7, i64 0, i32 14
  %9 = bitcast i8** %8 to i32**
  %10 = load i32*, i32** %9, align 8
  %11 = load i32, i32* %10, align 4
  %12 = add i32 %11, 7
  %13 = sdiv i32 %12, 8
  %14 = icmp slt i32 %12, 0
  %15 = shl nsw i32 %13, 3
  %16 = icmp ne i32 %15, %12
  %17 = and i1 %14, %16
  %.neg = sext i1 %17 to i32
  %18 = add nsw i32 %13, %.neg
  %19 = tail call i32 @llvm.smax.i32(i32 %18, i32 512)
  %20 = mul i32 %19, %2
  %21 = add i32 %20, %19
  %22 = tail call i32 @llvm.smin.i32(i32 %11, i32 %21)
  %23 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**
  %24 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %23, align 8
  %25 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %24, i64 0, i32 6
  %26 = load i32, i32* %25, align 4
  %27 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %24, i64 0, i32 5
  %28 = load i32, i32* %27, align 4
  %29 = icmp slt i32 %20, %22
  br i1 %29, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.preheader
  %.0815 = phi i32 [ %108, %after_if9 ], [ %20, %for_loop_body.preheader ]
  %30 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %6, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %.0815, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.0815
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.0815, 0
  %41 = icmp ne i32 %.0815, %37
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg13 = sext i1 %43 to i32
  %44 = add i32 %36, %.neg13
  %45 = mul i32 %44, %35
  %46 = add i32 %44, %26
  %47 = mul i32 %35, -1
  %48 = mul i32 %47, %44
  %49 = add i32 %28, %.0815
  %50 = add i32 %49, %48
  %51 = icmp sgt i32 %46, -1
  br i1 %51, label %true_block, label %false_block8

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %52 = getelementptr inbounds i8, i8* %32, i64 8
  %53 = bitcast i8* %52 to i32*
  %54 = load i32, i32* %53, align 4
  %55 = icmp slt i32 %46, %54
  %56 = icmp sgt i32 %50, -1
  %or.cond = select i1 %55, i1 %56, i1 false
  br i1 %or.cond, label %true_block4, label %false_block8

true_block4:                                      ; preds = %true_block
  %57 = getelementptr inbounds i8, i8* %32, i64 12
  %58 = bitcast i8* %57 to i32*
  %59 = load i32, i32* %58, align 4
  %60 = icmp slt i32 %50, %59
  br i1 %60, label %true_block7, label %false_block8

true_block7:                                      ; preds = %true_block4
  %61 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %23, align 8
  %62 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 0, i32 1
  %63 = load i32*, i32** %62, align 8
  %64 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 0, i32 0, i32 1
  %65 = load i32, i32* %64, align 4
  %66 = sub i32 %65, %35
  %67 = mul i32 %66, %44
  %68 = add i32 %.0815, %67
  %69 = sext i32 %68 to i64
  %70 = getelementptr i32, i32* %63, i64 %69
  %71 = load i32, i32* %70, align 4
  %72 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 1, i32 1
  %73 = load i32*, i32** %72, align 8
  %74 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 1, i32 0, i32 1
  %75 = load i32, i32* %74, align 4
  %76 = sub i32 %75, %35
  %77 = mul i32 %76, %44
  %78 = add i32 %.0815, %77
  %79 = sext i32 %78 to i64
  %80 = getelementptr i32, i32* %73, i64 %79
  %81 = load i32, i32* %80, align 4
  %82 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 2, i32 1
  %83 = load i32*, i32** %82, align 8
  %84 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 2, i32 0, i32 1
  %85 = load i32, i32* %84, align 4
  %86 = mul i32 %85, %46
  %87 = sub i32 %86, %45
  %88 = add i32 %49, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr i32, i32* %83, i64 %89
  %91 = load i32, i32* %90, align 4
  %92 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 3, i32 1
  %93 = load i32*, i32** %92, align 8
  %94 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %61, i64 0, i32 3, i32 0, i32 1
  %95 = load i32, i32* %94, align 4
  %96 = mul i32 %95, %46
  %97 = sub i32 %96, %45
  %98 = add i32 %49, %97
  %99 = sext i32 %98 to i64
  %100 = getelementptr i32, i32* %93, i64 %99
  %101 = load i32, i32* %100, align 4
  %102 = xor i32 %91, %71
  %103 = and i32 %101, %81
  %104 = mul i32 %103, %102
  %105 = load i32, i32* %5, align 4
  br label %after_if9

false_block8:                                     ; preds = %true_block4, %true_block, %for_loop_body
  %106 = load i32, i32* %4, align 4
  br label %after_if9

after_if9:                                        ; preds = %false_block8, %true_block7
  %.sink18 = phi i32 [ 1, %false_block8 ], [ %105, %true_block7 ]
  %.sink17 = phi i32 [ %106, %false_block8 ], [ %104, %true_block7 ]
  %.sink16 = phi i32* [ %4, %false_block8 ], [ %5, %true_block7 ]
  %107 = add i32 %.sink17, %.sink18
  store i32 %107, i32* %.sink16, align 4
  %108 = add nsw i32 %.0815, 1
  %exitcond.not = icmp eq i32 %22, %108
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nofree norecurse nounwind willreturn
define internal void @function_body.2(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture readonly %1) #4 {
allocs:
  %2 = bitcast i8* %1 to i32*
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %0, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 16
  %9 = bitcast i8* %8 to i32*
  %10 = atomicrmw add i32* %9, i32 %3 seq_cst, align 4
  %11 = getelementptr i8, i8* %1, i64 4
  %12 = bitcast i8* %11 to i32*
  %13 = load i32, i32* %12, align 4
  %14 = atomicrmw add i32* %9, i32 %13 seq_cst, align 4
  ret void
}

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_compute_mtb_error_to_buf_c340_0_kernel_2_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #5 {
entry:
  %0 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %1 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %0, align 8
  %2 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %1, i64 0, i32 14
  %3 = load i8*, i8** %2, align 8
  %4 = getelementptr inbounds i8, i8* %3, i64 16
  %5 = bitcast i8* %4 to i32*
  %6 = load i32, i32* %5, align 4
  %7 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }**
  %8 = load { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }** %7, align 8
  %9 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32 }, i32* }, i32, i32 }* %8, i64 0, i32 4, i32 1
  %10 = load i32*, i32** %9, align 8
  store i32 %6, i32* %10, align 4
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #6 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #7

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #8

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #8

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #9

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { argmemonly mustprogress nofree norecurse nosync nounwind willreturn writeonly }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { mustprogress nofree norecurse nounwind willreturn }
attributes #5 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #6 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #7 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #8 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #9 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
