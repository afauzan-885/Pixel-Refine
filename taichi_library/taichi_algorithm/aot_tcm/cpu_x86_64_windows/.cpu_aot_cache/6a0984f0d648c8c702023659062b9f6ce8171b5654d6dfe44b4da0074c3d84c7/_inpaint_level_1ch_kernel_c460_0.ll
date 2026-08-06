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
define void @_inpaint_level_1ch_kernel_c460_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_inpaint_level_1ch_kernel_c460_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 5
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 6
  %25 = load float, float* %24, align 4
  %26 = fptosi float %25 to i32
  %27 = fmul reassoc ninf nsz float %25, %25
  %28 = add i32 %26, 2
  %neg = xor i32 %26, -1
  %29 = icmp slt i32 %17, %19
  br i1 %29, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %32 = icmp sle i32 %28, %neg
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %37 = shl i32 %26, 1
  %38 = add i32 %37, 3
  %39 = sub i32 -1, %26
  %40 = add i32 %17, -1
  %41 = sub i32 %40, %26
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %lsr.iv71 = phi i32 [ %41, %for_loop_body.lr.ph ], [ %lsr.iv.next72, %for_loop_inc ]
  %.02749 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %108, %for_loop_inc ]
  %42 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %43 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %42, i64 0, i32 14
  %44 = load i8*, i8** %43, align 8
  %45 = getelementptr inbounds i8, i8* %44, i64 4
  %46 = bitcast i8* %45 to i32*
  %47 = load i32, i32* %46, align 4
  %48 = sdiv i32 %.02749, %47
  %49 = mul i32 %48, %47
  %50 = xor i32 %47, %.02749
  %51 = icmp slt i32 %50, 0
  %52 = icmp ne i32 %.02749, 0
  %53 = icmp ne i32 %49, %.02749
  %54 = and i1 %52, %51
  %55 = and i1 %54, %53
  %.neg36 = sext i1 %55 to i32
  %56 = add i32 %48, %.neg36
  %57 = mul i32 %56, %47
  %58 = sub i32 %.02749, %57
  %59 = load float*, float** %30, align 8
  %60 = load i32, i32* %31, align 4
  %61 = mul i32 %56, %60
  %62 = add i32 %58, %61
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, float* %59, i64 %63
  %65 = load float, float* %64, align 4
  %66 = fsub reassoc ninf nsz float %65, %23
  %67 = tail call float @llvm.fabs.f32(float %66)
  %68 = fcmp reassoc ninf nsz ogt float %67, 5.000000e-01
  %brmerge = select i1 %68, i1 true, i1 %32
  br i1 %brmerge, label %for_loop_inc, label %for_loop_body1.lr.ph

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %69 = getelementptr inbounds i8, i8* %44, i64 8
  %70 = bitcast i8* %69 to i32*
  %71 = getelementptr inbounds i8, i8* %44, i64 12
  %72 = bitcast i8* %71 to i32*
  %73 = add i32 %39, %48
  %74 = add i32 %73, %.neg36
  %75 = sub i32 %lsr.iv71, %57
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.after_for7_crit_edge.us, %for_loop_body1.lr.ph
  %lsr.iv69 = phi i32 [ %lsr.iv.next70, %for_loop_test8.after_for7_crit_edge.us ], [ %74, %for_loop_body1.lr.ph ]
  %.02246.us = phi i32 [ %neg, %for_loop_body1.lr.ph ], [ %107, %for_loop_test8.after_for7_crit_edge.us ]
  %.02345.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi50.us, %for_loop_test8.after_for7_crit_edge.us ]
  %.02444.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi.us, %for_loop_test8.after_for7_crit_edge.us ]
  %76 = add i32 %.02246.us, %56
  %77 = mul i32 %.02246.us, %.02246.us
  %78 = icmp slt i32 %76, 0
  br i1 %78, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us51.preheader

for_loop_body5.us51.preheader:                    ; preds = %for_loop_body1.us
  %.pre = load i32, i32* %70, align 4
  %.not.us = icmp sge i32 %76, %.pre
  br label %for_loop_body5.us51

for_loop_body5.us51:                              ; preds = %for_loop_inc6.us55, %for_loop_body5.us51.preheader
  %lsr.iv = phi i32 [ 0, %for_loop_body5.us51.preheader ], [ %lsr.iv.next, %for_loop_inc6.us55 ]
  %.241.us53 = phi float [ %.1.us57, %for_loop_inc6.us55 ], [ %.02345.us, %for_loop_body5.us51.preheader ]
  %.22640.us54 = phi float [ %.125.us56, %for_loop_inc6.us55 ], [ %.02444.us, %for_loop_body5.us51.preheader ]
  %79 = add i32 %neg, %lsr.iv
  %80 = add i32 %75, %lsr.iv
  %81 = icmp slt i32 %80, 0
  %or.cond.us = select i1 %.not.us, i1 true, i1 %81
  br i1 %or.cond.us, label %for_loop_inc6.us55, label %false_block16.us

false_block16.us:                                 ; preds = %for_loop_body5.us51
  %82 = load i32, i32* %72, align 4
  %.not39.us = icmp slt i32 %80, %82
  br i1 %.not39.us, label %after_if20.us, label %for_loop_inc6.us55

after_if20.us:                                    ; preds = %false_block16.us
  %83 = load float*, float** %33, align 8
  %84 = load i32, i32* %34, align 4
  %85 = mul i32 %lsr.iv69, %84
  %86 = add i32 %80, %85
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, float* %83, i64 %87
  %89 = load float, float* %88, align 4
  %90 = fcmp reassoc ninf nsz olt float %89, 5.000000e-01
  br i1 %90, label %for_loop_inc6.us55, label %after_if24.us

after_if24.us:                                    ; preds = %after_if20.us
  %91 = mul i32 %79, %79
  %92 = add i32 %91, %77
  %93 = sitofp i32 %92 to float
  %94 = fcmp reassoc ninf nsz olt float %27, %93
  %95 = icmp slt i32 %92, 1
  %.0.us = or i1 %95, %94
  br i1 %.0.us, label %for_loop_inc6.us55, label %after_if31.us

after_if31.us:                                    ; preds = %after_if24.us
  %96 = fdiv reassoc ninf nsz float 1.000000e+00, %93
  %97 = fadd reassoc ninf nsz float %96, %.22640.us54
  %98 = load float*, float** %35, align 8
  %99 = load i32, i32* %36, align 4
  %100 = mul i32 %lsr.iv69, %99
  %101 = add i32 %80, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %98, i64 %102
  %104 = load float, float* %103, align 4
  %105 = fmul reassoc ninf nsz float %104, %96
  %106 = fadd reassoc ninf nsz float %105, %.241.us53
  br label %for_loop_inc6.us55

for_loop_inc6.us55:                               ; preds = %after_if31.us, %after_if24.us, %after_if20.us, %false_block16.us, %for_loop_body5.us51
  %.125.us56 = phi float [ %.22640.us54, %false_block16.us ], [ %.22640.us54, %after_if20.us ], [ %.22640.us54, %after_if24.us ], [ %97, %after_if31.us ], [ %.22640.us54, %for_loop_body5.us51 ]
  %.1.us57 = phi float [ %.241.us53, %false_block16.us ], [ %.241.us53, %after_if20.us ], [ %.241.us53, %after_if24.us ], [ %106, %after_if31.us ], [ %.241.us53, %for_loop_body5.us51 ]
  %lsr.iv.next = add nuw i32 %lsr.iv, 1
  %exitcond.not = icmp eq i32 %38, %lsr.iv.next
  br i1 %exitcond.not, label %for_loop_test8.after_for7_crit_edge.us.loopexit, label %for_loop_body5.us51

for_loop_test8.after_for7_crit_edge.us.loopexit:  ; preds = %for_loop_inc6.us55
  br label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us:           ; preds = %for_loop_test8.after_for7_crit_edge.us.loopexit, %for_loop_body1.us
  %.us-phi.us = phi float [ %.02444.us, %for_loop_body1.us ], [ %.125.us56, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %.us-phi50.us = phi float [ %.02345.us, %for_loop_body1.us ], [ %.1.us57, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %107 = add i32 %.02246.us, 1
  %lsr.iv.next70 = add i32 %lsr.iv69, 1
  %exitcond65.not = icmp eq i32 %107, %28
  br i1 %exitcond65.not, label %after_for3, label %for_loop_body1.us

for_loop_inc:                                     ; preds = %true_block33, %after_for3, %for_loop_body
  %108 = add nsw i32 %.02749, 1
  %lsr.iv.next72 = add i32 %lsr.iv71, 1
  %exitcond66.not = icmp eq i32 %108, %19
  br i1 %exitcond66.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3:                                       ; preds = %for_loop_test8.after_for7_crit_edge.us
  %109 = fcmp reassoc ninf nsz ogt float %.us-phi.us, 0x3D71979980000000
  br i1 %109, label %true_block33, label %for_loop_inc

true_block33:                                     ; preds = %after_for3
  %110 = fdiv reassoc ninf nsz float %.us-phi50.us, %.us-phi.us
  %111 = load float*, float** %35, align 8
  %112 = load i32, i32* %36, align 4
  %113 = mul i32 %112, %56
  %114 = add i32 %113, %58
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, float* %111, i64 %115
  store float %110, float* %116, align 4
  %117 = load float*, float** %33, align 8
  %118 = load i32, i32* %34, align 4
  %119 = mul i32 %118, %56
  %120 = add i32 %119, %58
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, float* %117, i64 %121
  store float 1.000000e+00, float* %122, align 4
  br label %for_loop_inc
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
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
