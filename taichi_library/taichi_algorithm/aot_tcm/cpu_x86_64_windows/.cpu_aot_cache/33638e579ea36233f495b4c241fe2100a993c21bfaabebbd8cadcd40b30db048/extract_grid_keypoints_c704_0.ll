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

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @extract_grid_keypoints_c704_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %10, i64 0, i32 5
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 8
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = sdiv i32 %3, %12
  %19 = mul i32 %18, %12
  %20 = xor i32 %12, %3
  %21 = icmp slt i32 %20, 0
  %22 = icmp ne i32 %3, 0
  %23 = icmp ne i32 %19, %3
  %24 = and i1 %22, %21
  %25 = and i1 %24, %23
  %.neg = sext i1 %25 to i32
  %26 = add i32 %18, %.neg
  %27 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }** %0, align 8
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %27, i64 0, i32 4
  %29 = load i32, i32* %28, align 4
  %30 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 16
  %34 = bitcast i8* %33 to i32*
  store i32 %29, i32* %34, align 4
  %35 = sdiv i32 %29, %12
  %36 = mul i32 %35, %12
  %37 = xor i32 %29, %12
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %29, 0
  %40 = icmp ne i32 %36, %29
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg1 = sext i1 %42 to i32
  %43 = add i32 %35, %.neg1
  %44 = tail call i32 @llvm.smax.i32(i32 %26, i32 0)
  %45 = tail call i32 @llvm.smax.i32(i32 %43, i32 0)
  %46 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %47 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %46, i64 0, i32 14
  %48 = load i8*, i8** %47, align 8
  %49 = getelementptr inbounds i8, i8* %48, i64 4
  %50 = bitcast i8* %49 to i32*
  store i32 %45, i32* %50, align 4
  %51 = mul i32 %45, %44
  %52 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %53 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %52, i64 0, i32 14
  %54 = bitcast i8** %53 to i32**
  %55 = load i32*, i32** %54, align 8
  store i32 %51, i32* %55, align 4
  ret void
}

; Function Attrs: nounwind
define void @extract_grid_keypoints_c704_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %21, i64 0, i32 6
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %21, i64 0, i32 0, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if11, %for_loop_body.lr.ph
  %.04169 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %90, %after_if11 ]
  %27 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 4
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sdiv i32 %.04169, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.04169
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.04169, 0
  %38 = icmp ne i32 %34, %.04169
  %39 = and i1 %37, %36
  %40 = and i1 %39, %38
  %.neg48 = sext i1 %40 to i32
  %41 = add i32 %33, %.neg48
  %42 = mul i32 %41, %32
  %43 = sub i32 %.04169, %42
  %44 = getelementptr inbounds i8, i8* %29, i64 8
  %45 = bitcast i8* %44 to i32*
  %46 = load i32, i32* %45, align 4
  %47 = getelementptr inbounds i8, i8* %29, i64 12
  %48 = bitcast i8* %47 to i32*
  %49 = getelementptr inbounds i8, i8* %29, i64 16
  %50 = bitcast i8* %49 to i32*
  %51 = insertelement <2 x i32> poison, i32 %41, i64 0
  %52 = insertelement <2 x i32> %51, i32 %43, i64 1
  %53 = insertelement <2 x i32> poison, i32 %46, i64 0
  %54 = shufflevector <2 x i32> %53, <2 x i32> poison, <2 x i32> zeroinitializer
  %55 = mul <2 x i32> %52, %54
  %56 = add <2 x i32> %55, %54
  %57 = bitcast i8* %47 to <2 x i32>*
  %58 = load <2 x i32>, <2 x i32>* %57, align 4
  %59 = add <2 x i32> %58, <i32 -3, i32 -3>
  %60 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %56, <2 x i32> %59)
  %61 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %55, <2 x i32> <i32 3, i32 3>)
  %62 = icmp slt <2 x i32> %61, %60
  %63 = extractelement <2 x i1> %62, i64 0
  %64 = extractelement <2 x i1> %62, i64 1
  %or.cond76 = select i1 %63, i1 %64, i1 false
  br i1 %or.cond76, label %for_loop_test8.preheader.us.preheader, label %after_for3

for_loop_test8.preheader.us.preheader:            ; preds = %for_loop_body
  %65 = extractelement <2 x i32> %61, i64 1
  %66 = zext i32 %65 to i64
  %67 = extractelement <2 x i32> %60, i64 1
  %68 = sext i32 %67 to i64
  %.pre = load float*, float** %25, align 8
  %.pre75 = load i32, i32* %26, align 4
  %69 = extractelement <2 x i32> %61, i64 0
  %70 = extractelement <2 x i32> %60, i64 0
  %71 = mul i32 %69, %.pre75
  %72 = zext i32 %71 to i64
  %73 = zext i32 %.pre75 to i64
  br label %for_loop_test8.preheader.us

for_loop_test8.preheader.us:                      ; preds = %for_loop_test8.after_for7_crit_edge.us, %for_loop_test8.preheader.us.preheader
  %lsr.iv = phi i64 [ %72, %for_loop_test8.preheader.us.preheader ], [ %lsr.iv.next, %for_loop_test8.after_for7_crit_edge.us ]
  %.03265.us = phi i32 [ %80, %for_loop_test8.after_for7_crit_edge.us ], [ %69, %for_loop_test8.preheader.us.preheader ]
  %.03364.us = phi i32 [ %.2.us, %for_loop_test8.after_for7_crit_edge.us ], [ -1, %for_loop_test8.preheader.us.preheader ]
  %.03563.us = phi i32 [ %.237.us, %for_loop_test8.after_for7_crit_edge.us ], [ -1, %for_loop_test8.preheader.us.preheader ]
  %.03862.us = phi float [ %.240.us, %for_loop_test8.after_for7_crit_edge.us ], [ 0.000000e+00, %for_loop_test8.preheader.us.preheader ]
  br label %for_loop_body5.us

for_loop_body5.us:                                ; preds = %for_loop_body5.us, %for_loop_test8.preheader.us
  %indvars.iv = phi i64 [ %66, %for_loop_test8.preheader.us ], [ %indvars.iv.next, %for_loop_body5.us ]
  %.13458.us = phi i32 [ %.03364.us, %for_loop_test8.preheader.us ], [ %.2.us, %for_loop_body5.us ]
  %.13657.us = phi i32 [ %.03563.us, %for_loop_test8.preheader.us ], [ %.237.us, %for_loop_body5.us ]
  %.13956.us = phi float [ %.03862.us, %for_loop_test8.preheader.us ], [ %.240.us, %for_loop_body5.us ]
  %74 = add i64 %lsr.iv, %indvars.iv
  %tmp77 = trunc i64 %74 to i32
  %75 = sext i32 %tmp77 to i64
  %76 = getelementptr float, float* %.pre, i64 %75
  %77 = load float, float* %76, align 4
  %78 = fcmp reassoc ninf nsz ogt float %77, %.13956.us
  %.240.us = select i1 %78, float %77, float %.13956.us
  %tmp = trunc i64 %indvars.iv to i32
  %.237.us = select i1 %78, i32 %tmp, i32 %.13657.us
  %.2.us = select i1 %78, i32 %.03265.us, i32 %.13458.us
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %79 = icmp slt i64 %indvars.iv.next, %68
  br i1 %79, label %for_loop_body5.us, label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us:           ; preds = %for_loop_body5.us
  %80 = add nuw nsw i32 %.03265.us, 1
  %lsr.iv.next = add i64 %lsr.iv, %73
  %exitcond.not = icmp eq i32 %80, %70
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_test8.preheader.us

after_for.loopexit:                               ; preds = %after_if11
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3.loopexit:                              ; preds = %for_loop_test8.after_for7_crit_edge.us
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.038.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.240.us, %after_for3.loopexit ]
  %.035.lcssa = phi i32 [ -1, %for_loop_body ], [ %.237.us, %after_for3.loopexit ]
  %.033.lcssa = phi i32 [ -1, %for_loop_body ], [ %.2.us, %after_for3.loopexit ]
  %81 = fcmp reassoc ninf nsz ogt float %.038.lcssa, %23
  br i1 %81, label %true_block9, label %after_if11

true_block9:                                      ; preds = %after_for3
  %82 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }** %20, align 8
  %83 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %82, i64 0, i32 2, i32 1
  %84 = load i32*, i32** %83, align 8
  %85 = atomicrmw add i32* %84, i32 1 seq_cst, align 4
  %86 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }** %20, align 8
  %87 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %86, i64 0, i32 1, i32 0, i32 0
  %88 = load i32, i32* %87, align 4
  %89 = icmp slt i32 %85, %88
  br i1 %89, label %true_block12, label %after_if11

after_if11:                                       ; preds = %after_if26, %true_block9, %after_for3
  %90 = add nsw i32 %.04169, 1
  %exitcond74.not = icmp eq i32 %90, %19
  br i1 %exitcond74.not, label %after_for.loopexit, label %for_loop_body

true_block12:                                     ; preds = %true_block9
  %91 = icmp sgt i32 %.033.lcssa, 0
  br i1 %91, label %true_block15, label %after_if26

true_block15:                                     ; preds = %true_block12
  %92 = load i32, i32* %48, align 4
  %93 = add i32 %92, -1
  %94 = icmp slt i32 %.033.lcssa, %93
  %95 = icmp sgt i32 %.035.lcssa, 0
  %or.cond = select i1 %94, i1 %95, i1 false
  br i1 %or.cond, label %true_block21, label %after_if26

true_block21:                                     ; preds = %true_block15
  %96 = load i32, i32* %50, align 4
  %97 = add i32 %96, -1
  %98 = icmp slt i32 %.035.lcssa, %97
  br i1 %98, label %true_block24, label %after_if26

true_block24:                                     ; preds = %true_block21
  %99 = load float*, float** %25, align 8
  %100 = load i32, i32* %26, align 4
  %101 = mul i32 %100, %.033.lcssa
  %102 = add i32 %101, %.035.lcssa
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %99, i64 %103
  %105 = load float, float* %104, align 4
  %106 = add i32 %102, -1
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, float* %99, i64 %107
  %109 = load float, float* %108, align 4
  %110 = add i32 %102, 1
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, float* %99, i64 %111
  %113 = load float, float* %112, align 4
  %114 = add nsw i32 %.033.lcssa, -1
  %115 = mul i32 %100, %114
  %116 = add i32 %115, %.035.lcssa
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, float* %99, i64 %117
  %119 = load float, float* %118, align 4
  %120 = add nuw nsw i32 %.033.lcssa, 1
  %121 = mul i32 %100, %120
  %122 = add i32 %121, %.035.lcssa
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, float* %99, i64 %123
  %125 = load float, float* %124, align 4
  %factor = fmul reassoc ninf nsz float %105, 2.000000e+00
  %126 = fadd reassoc ninf nsz float %109, %113
  %127 = fsub reassoc ninf nsz float %factor, %126
  %128 = fcmp reassoc ninf nsz ogt float %127, 0x3EE4F8B580000000
  br i1 %128, label %true_block27, label %after_if29

after_if26:                                       ; preds = %after_if32, %true_block21, %true_block15, %true_block12
  %129 = phi <2 x float> [ %161, %after_if32 ], [ zeroinitializer, %true_block21 ], [ zeroinitializer, %true_block12 ], [ zeroinitializer, %true_block15 ]
  %130 = sitofp i32 %.033.lcssa to float
  %131 = extractelement <2 x float> %129, i64 0
  %132 = fadd reassoc ninf nsz float %131, %130
  %133 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %86, i64 0, i32 1, i32 1
  %134 = load float*, float** %133, align 8
  %135 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, float }* %86, i64 0, i32 1, i32 0, i32 1
  %136 = load i32, i32* %135, align 4
  %137 = mul i32 %136, %85
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %134, i64 %138
  store float %132, float* %139, align 4
  %140 = sitofp i32 %.035.lcssa to float
  %141 = extractelement <2 x float> %129, i64 1
  %142 = fadd reassoc ninf nsz float %141, %140
  %143 = load float*, float** %133, align 8
  %144 = load i32, i32* %135, align 4
  %145 = mul i32 %144, %85
  %146 = add i32 %145, 1
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %143, i64 %147
  store float %142, float* %148, align 4
  br label %after_if11

true_block27:                                     ; preds = %true_block24
  %149 = fsub reassoc ninf nsz float %113, %109
  %150 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %151 = fdiv reassoc ninf nsz float %150, %127
  br label %after_if29

after_if29:                                       ; preds = %true_block27, %true_block24
  %.1 = phi float [ %151, %true_block27 ], [ 0.000000e+00, %true_block24 ]
  %152 = fadd reassoc ninf nsz float %119, %125
  %153 = fsub reassoc ninf nsz float %factor, %152
  %154 = fcmp reassoc ninf nsz ogt float %153, 0x3EE4F8B580000000
  br i1 %154, label %true_block30, label %after_if32

true_block30:                                     ; preds = %after_if29
  %155 = fsub reassoc ninf nsz float %125, %119
  %156 = fmul reassoc ninf nsz float %155, 5.000000e-01
  %157 = fdiv reassoc ninf nsz float %156, %153
  br label %after_if32

after_if32:                                       ; preds = %true_block30, %after_if29
  %.130 = phi float [ %157, %true_block30 ], [ 0.000000e+00, %after_if29 ]
  %158 = insertelement <2 x float> poison, float %.130, i64 0
  %159 = insertelement <2 x float> %158, float %.1, i64 1
  %160 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %159, <2 x float> <float 5.000000e-01, float 5.000000e-01>)
  %161 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %160, <2 x float> <float -5.000000e-01, float -5.000000e-01>)
  br label %after_if26
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.minnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.maxnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
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
