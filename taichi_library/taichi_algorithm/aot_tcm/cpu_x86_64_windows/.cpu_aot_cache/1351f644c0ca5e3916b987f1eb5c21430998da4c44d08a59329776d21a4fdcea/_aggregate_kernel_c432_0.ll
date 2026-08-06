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
define void @_aggregate_kernel_c432_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  store i32 %3, i32* %8, align 4
  ret void
}

; Function Attrs: nounwind
define void @_aggregate_kernel_c432_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 8
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 9
  %25 = load i32, i32* %24, align 4
  %.fr = freeze i32 %25
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %28 = icmp sgt i32 %23, 0
  %29 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4, i32 1
  %30 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4, i32 0, i32 1
  %31 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %32 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %33 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 1
  %34 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  %35 = icmp sgt i32 %.fr, 0
  br i1 %28, label %for_loop_body.us.preheader, label %after_for

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %36 = sext i32 %17 to i64
  %wide.trip.count = sext i32 %19 to i64
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %indvars.iv = phi i64 [ %36, %for_loop_body.us.preheader ], [ %indvars.iv.next, %for_loop_test4.after_for3_crit_edge.us ]
  %lsr58 = trunc i64 %indvars.iv to i32
  %37 = load float*, float** %27, align 8
  %38 = getelementptr float, float* %37, i64 %indvars.iv
  %39 = load float, float* %38, align 4
  br i1 %35, label %for_loop_body1.us.us.preheader, label %for_loop_test4.after_for3_crit_edge.us

for_loop_body1.us.us.preheader:                   ; preds = %for_loop_body.us
  br label %for_loop_body1.us.us

for_loop_test4.after_for3_crit_edge.us.loopexit:  ; preds = %for_loop_inc2.us.us
  br label %for_loop_test4.after_for3_crit_edge.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_test4.after_for3_crit_edge.us.loopexit, %for_loop_body.us
  %indvars.iv.next = add nsw i64 %indvars.iv, 1
  %exitcond55.not = icmp eq i64 %indvars.iv.next, %wide.trip.count
  br i1 %exitcond55.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body1.us.us:                             ; preds = %for_loop_inc2.us.us, %for_loop_body1.us.us.preheader
  %.01929.us.us = phi i32 [ %62, %for_loop_inc2.us.us ], [ 0, %for_loop_body1.us.us.preheader ]
  %40 = load i32*, i32** %29, align 8
  %41 = load i32, i32* %30, align 4
  %42 = mul i32 %41, %lsr58
  %43 = add i32 %42, %.01929.us.us
  %44 = sext i32 %43 to i64
  %45 = getelementptr i32, i32* %40, i64 %44
  %46 = load i32, i32* %45, align 4
  %47 = icmp eq i32 %46, 0
  br i1 %47, label %for_loop_inc2.us.us, label %for_loop_body5.us.us.us.preheader

for_loop_body5.us.us.us.preheader:                ; preds = %for_loop_body1.us.us
  %48 = load i32*, i32** %31, align 8
  %49 = load i32, i32* %32, align 4
  %50 = mul i32 %49, %lsr58
  %51 = add i32 %50, %.01929.us.us
  %52 = sext i32 %51 to i64
  %53 = getelementptr i32, i32* %48, i64 %52
  %54 = load i32, i32* %53, align 4
  %55 = load i32*, i32** %33, align 8
  %56 = load i32, i32* %34, align 4
  %57 = mul i32 %56, %lsr58
  %58 = add i32 %57, %.01929.us.us
  %59 = sext i32 %58 to i64
  %60 = getelementptr i32, i32* %55, i64 %59
  %61 = load i32, i32* %60, align 4
  br label %for_loop_body5.us.us.us

for_loop_inc2.us.us.loopexit:                     ; preds = %for_loop_test12.after_for11_crit_edge.us.us.us
  br label %for_loop_inc2.us.us

for_loop_inc2.us.us:                              ; preds = %for_loop_inc2.us.us.loopexit, %for_loop_body1.us.us
  %62 = add nuw nsw i32 %.01929.us.us, 1
  %exitcond53.not = icmp eq i32 %62, %23
  br i1 %exitcond53.not, label %for_loop_test4.after_for3_crit_edge.us.loopexit, label %for_loop_body1.us.us

for_loop_body5.us.us.us:                          ; preds = %for_loop_test12.after_for11_crit_edge.us.us.us, %for_loop_body5.us.us.us.preheader
  %lsr.iv56 = phi i32 [ %54, %for_loop_body5.us.us.us.preheader ], [ %lsr.iv.next57, %for_loop_test12.after_for11_crit_edge.us.us.us ]
  %.01828.us.us.us = phi i32 [ %65, %for_loop_test12.after_for11_crit_edge.us.us.us ], [ 0, %for_loop_body5.us.us.us.preheader ]
  %63 = add i32 %.01828.us.us.us, %54
  %64 = icmp sgt i32 %63, -1
  br i1 %64, label %for_loop_body9.us.us.us.us.preheader, label %for_loop_test12.after_for11_crit_edge.us.us.us

for_loop_body9.us.us.us.us.preheader:             ; preds = %for_loop_body5.us.us.us
  br label %for_loop_body9.us.us.us.us

for_loop_test12.after_for11_crit_edge.us.us.us.loopexit: ; preds = %after_if24.us.us.us.us
  br label %for_loop_test12.after_for11_crit_edge.us.us.us

for_loop_test12.after_for11_crit_edge.us.us.us:   ; preds = %for_loop_test12.after_for11_crit_edge.us.us.us.loopexit, %for_loop_body5.us.us.us
  %65 = add nuw nsw i32 %.01828.us.us.us, 1
  %lsr.iv.next57 = add i32 %lsr.iv56, 1
  %exitcond52.not = icmp eq i32 %65, %.fr
  br i1 %exitcond52.not, label %for_loop_inc2.us.us.loopexit, label %for_loop_body5.us.us.us

for_loop_body9.us.us.us.us:                       ; preds = %after_if24.us.us.us.us, %for_loop_body9.us.us.us.us.preheader
  %.01727.us.us.us.us = phi i32 [ %112, %after_if24.us.us.us.us ], [ 0, %for_loop_body9.us.us.us.us.preheader ]
  %66 = add i32 %61, %.01727.us.us.us.us
  %67 = load { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }** %20, align 8
  %68 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 10
  %69 = load i32, i32* %68, align 4
  %70 = icmp slt i32 %63, %69
  %71 = icmp sgt i32 %66, -1
  %or.cond.us.us.us.us = select i1 %70, i1 %71, i1 false
  br i1 %or.cond.us.us.us.us, label %true_block19.us.us.us.us, label %after_if24.us.us.us.us

true_block19.us.us.us.us:                         ; preds = %for_loop_body9.us.us.us.us
  %72 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 11
  %73 = load i32, i32* %72, align 4
  %74 = icmp slt i32 %66, %73
  br i1 %74, label %true_block22.us.us.us.us, label %after_if24.us.us.us.us

true_block22.us.us.us.us:                         ; preds = %true_block19.us.us.us.us
  %75 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 0, i32 1
  %76 = load float*, float** %75, align 8
  %77 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 0, i32 0, i32 1
  %78 = load i32, i32* %77, align 4
  %79 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 0, i32 0, i32 2
  %80 = load i32, i32* %79, align 4
  %81 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 0, i32 0, i32 3
  %82 = load i32, i32* %81, align 4
  %83 = mul i32 %lsr58, %78
  %84 = add i32 %.01929.us.us, %83
  %85 = mul i32 %80, %84
  %86 = add i32 %.01828.us.us.us, %85
  %87 = mul i32 %82, %86
  %88 = add i32 %.01727.us.us.us.us, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, float* %76, i64 %89
  %91 = load float, float* %90, align 4
  %92 = fmul reassoc ninf nsz float %91, %39
  %93 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 5, i32 1
  %94 = load float*, float** %93, align 8
  %95 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %67, i64 0, i32 5, i32 0, i32 1
  %96 = load i32, i32* %95, align 4
  %97 = mul i32 %lsr.iv56, %96
  %98 = add i32 %66, %97
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %94, i64 %99
  %101 = atomicrmw fadd float* %100, float %92 seq_cst, align 4
  %102 = load { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }** %20, align 8
  %103 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %102, i64 0, i32 6, i32 1
  %104 = load float*, float** %103, align 8
  %105 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32 }* %102, i64 0, i32 6, i32 0, i32 1
  %106 = load i32, i32* %105, align 4
  %107 = mul i32 %lsr.iv56, %106
  %108 = add i32 %66, %107
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %104, i64 %109
  %111 = atomicrmw fadd float* %110, float %39 seq_cst, align 4
  br label %after_if24.us.us.us.us

after_if24.us.us.us.us:                           ; preds = %true_block22.us.us.us.us, %true_block19.us.us.us.us, %for_loop_body9.us.us.us.us
  %112 = add nuw nsw i32 %.01727.us.us.us.us, 1
  %exitcond.not = icmp eq i32 %.fr, %112
  br i1 %exitcond.not, label %for_loop_test12.after_for11_crit_edge.us.us.us.loopexit, label %for_loop_body9.us.us.us.us

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %for_loop_body.lr.ph, %allocs
  ret void
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
