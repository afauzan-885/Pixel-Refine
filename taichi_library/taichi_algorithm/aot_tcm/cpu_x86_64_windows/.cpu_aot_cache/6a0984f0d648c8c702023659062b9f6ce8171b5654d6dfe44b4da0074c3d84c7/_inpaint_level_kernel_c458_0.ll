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
define void @_inpaint_level_kernel_c458_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %11, i64 0, i32 4
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
define void @_inpaint_level_kernel_c458_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 5
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 6
  %25 = load float, float* %24, align 4
  %26 = fptosi float %25 to i32
  %27 = fmul reassoc ninf nsz float %25, %25
  %28 = add i32 %26, 2
  %neg = xor i32 %26, -1
  %29 = icmp slt i32 %17, %19
  br i1 %29, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %32 = icmp sle i32 %28, %neg
  %33 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %34 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %35 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %36 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %37 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 2
  %38 = shl i32 %26, 1
  %39 = add i32 %38, 3
  %40 = sub i32 -1, %26
  %41 = add i32 %17, -1
  %42 = sub i32 %41, %26
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %lsr.iv100 = phi i32 [ %42, %for_loop_body.lr.ph ], [ %lsr.iv.next101, %for_loop_inc ]
  %.03666 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %123, %for_loop_inc ]
  %43 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %44 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %43, i64 0, i32 14
  %45 = load i8*, i8** %44, align 8
  %46 = getelementptr inbounds i8, i8* %45, i64 4
  %47 = bitcast i8* %46 to i32*
  %48 = load i32, i32* %47, align 4
  %49 = sdiv i32 %.03666, %48
  %50 = mul i32 %49, %48
  %51 = xor i32 %48, %.03666
  %52 = icmp slt i32 %51, 0
  %53 = icmp ne i32 %.03666, 0
  %54 = icmp ne i32 %50, %.03666
  %55 = and i1 %53, %52
  %56 = and i1 %55, %54
  %.neg44 = sext i1 %56 to i32
  %57 = add i32 %49, %.neg44
  %58 = mul i32 %57, %48
  %59 = sub i32 %.03666, %58
  %60 = load float*, float** %30, align 8
  %61 = load i32, i32* %31, align 4
  %62 = mul i32 %57, %61
  %63 = add i32 %59, %62
  %64 = sext i32 %63 to i64
  %65 = getelementptr float, float* %60, i64 %64
  %66 = load float, float* %65, align 4
  %67 = fsub reassoc ninf nsz float %66, %23
  %68 = tail call float @llvm.fabs.f32(float %67)
  %69 = fcmp reassoc ninf nsz ogt float %68, 5.000000e-01
  %brmerge = select i1 %69, i1 true, i1 %32
  br i1 %brmerge, label %for_loop_inc, label %for_loop_body1.lr.ph

for_loop_body1.lr.ph:                             ; preds = %for_loop_body
  %70 = getelementptr inbounds i8, i8* %45, i64 8
  %71 = bitcast i8* %70 to i32*
  %72 = getelementptr inbounds i8, i8* %45, i64 12
  %73 = bitcast i8* %72 to i32*
  %74 = add i32 %40, %49
  %75 = add i32 %74, %.neg44
  %76 = sub i32 %lsr.iv100, %58
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.after_for7_crit_edge.us, %for_loop_body1.lr.ph
  %lsr.iv98 = phi i32 [ %lsr.iv.next99, %for_loop_test8.after_for7_crit_edge.us ], [ %75, %for_loop_body1.lr.ph ]
  %.02561.us = phi i32 [ %neg, %for_loop_body1.lr.ph ], [ %122, %for_loop_test8.after_for7_crit_edge.us ]
  %.02660.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi69.us, %for_loop_test8.after_for7_crit_edge.us ]
  %.02759.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi68.us, %for_loop_test8.after_for7_crit_edge.us ]
  %.03058.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi67.us, %for_loop_test8.after_for7_crit_edge.us ]
  %.03357.us = phi float [ 0.000000e+00, %for_loop_body1.lr.ph ], [ %.us-phi.us, %for_loop_test8.after_for7_crit_edge.us ]
  %77 = add i32 %.02561.us, %57
  %78 = mul i32 %.02561.us, %.02561.us
  %79 = icmp slt i32 %77, 0
  br i1 %79, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us70.preheader

for_loop_body5.us70.preheader:                    ; preds = %for_loop_body1.us
  %.pre = load i32, i32* %71, align 4
  %.not.us = icmp sge i32 %77, %.pre
  br label %for_loop_body5.us70

for_loop_body5.us70:                              ; preds = %for_loop_inc6.us76, %for_loop_body5.us70.preheader
  %lsr.iv = phi i32 [ 0, %for_loop_body5.us70.preheader ], [ %lsr.iv.next, %for_loop_inc6.us76 ]
  %.252.us72 = phi float [ %.1.us80, %for_loop_inc6.us76 ], [ %.02660.us, %for_loop_body5.us70.preheader ]
  %.22951.us73 = phi float [ %.128.us79, %for_loop_inc6.us76 ], [ %.02759.us, %for_loop_body5.us70.preheader ]
  %.23250.us74 = phi float [ %.131.us78, %for_loop_inc6.us76 ], [ %.03058.us, %for_loop_body5.us70.preheader ]
  %.23549.us75 = phi float [ %.134.us77, %for_loop_inc6.us76 ], [ %.03357.us, %for_loop_body5.us70.preheader ]
  %80 = add i32 %neg, %lsr.iv
  %81 = add i32 %76, %lsr.iv
  %82 = icmp slt i32 %81, 0
  %or.cond47.us = select i1 %.not.us, i1 true, i1 %82
  br i1 %or.cond47.us, label %for_loop_inc6.us76, label %false_block16.us

false_block16.us:                                 ; preds = %for_loop_body5.us70
  %83 = load i32, i32* %73, align 4
  %.not48.us = icmp slt i32 %81, %83
  br i1 %.not48.us, label %after_if20.us, label %for_loop_inc6.us76

after_if20.us:                                    ; preds = %false_block16.us
  %84 = load float*, float** %33, align 8
  %85 = load i32, i32* %34, align 4
  %86 = mul i32 %lsr.iv98, %85
  %87 = add i32 %81, %86
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, float* %84, i64 %88
  %90 = load float, float* %89, align 4
  %91 = fcmp reassoc ninf nsz olt float %90, 5.000000e-01
  br i1 %91, label %for_loop_inc6.us76, label %after_if24.us

after_if24.us:                                    ; preds = %after_if20.us
  %92 = mul i32 %80, %80
  %93 = add i32 %92, %78
  %94 = sitofp i32 %93 to float
  %95 = fcmp reassoc ninf nsz olt float %27, %94
  %96 = icmp slt i32 %93, 1
  %or.cond.us = or i1 %96, %95
  br i1 %or.cond.us, label %for_loop_inc6.us76, label %after_if32.us

after_if32.us:                                    ; preds = %after_if24.us
  %97 = fdiv reassoc ninf nsz float 1.000000e+00, %94
  %98 = fadd reassoc ninf nsz float %97, %.23549.us75
  %99 = load float*, float** %35, align 8
  %100 = load i32, i32* %36, align 4
  %101 = load i32, i32* %37, align 4
  %102 = mul i32 %lsr.iv98, %100
  %103 = add i32 %81, %102
  %104 = mul i32 %103, %101
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, float* %99, i64 %105
  %107 = load float, float* %106, align 4
  %108 = fmul reassoc ninf nsz float %107, %97
  %109 = fadd reassoc ninf nsz float %108, %.23250.us74
  %110 = add i32 %104, 1
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, float* %99, i64 %111
  %113 = load float, float* %112, align 4
  %114 = fmul reassoc ninf nsz float %113, %97
  %115 = fadd reassoc ninf nsz float %114, %.22951.us73
  %116 = add i32 %104, 2
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, float* %99, i64 %117
  %119 = load float, float* %118, align 4
  %120 = fmul reassoc ninf nsz float %119, %97
  %121 = fadd reassoc ninf nsz float %120, %.252.us72
  br label %for_loop_inc6.us76

for_loop_inc6.us76:                               ; preds = %after_if32.us, %after_if24.us, %after_if20.us, %false_block16.us, %for_loop_body5.us70
  %.134.us77 = phi float [ %.23549.us75, %false_block16.us ], [ %.23549.us75, %after_if20.us ], [ %.23549.us75, %after_if24.us ], [ %98, %after_if32.us ], [ %.23549.us75, %for_loop_body5.us70 ]
  %.131.us78 = phi float [ %.23250.us74, %false_block16.us ], [ %.23250.us74, %after_if20.us ], [ %.23250.us74, %after_if24.us ], [ %109, %after_if32.us ], [ %.23250.us74, %for_loop_body5.us70 ]
  %.128.us79 = phi float [ %.22951.us73, %false_block16.us ], [ %.22951.us73, %after_if20.us ], [ %.22951.us73, %after_if24.us ], [ %115, %after_if32.us ], [ %.22951.us73, %for_loop_body5.us70 ]
  %.1.us80 = phi float [ %.252.us72, %false_block16.us ], [ %.252.us72, %after_if20.us ], [ %.252.us72, %after_if24.us ], [ %121, %after_if32.us ], [ %.252.us72, %for_loop_body5.us70 ]
  %lsr.iv.next = add nuw i32 %lsr.iv, 1
  %exitcond.not = icmp eq i32 %39, %lsr.iv.next
  br i1 %exitcond.not, label %for_loop_test8.after_for7_crit_edge.us.loopexit, label %for_loop_body5.us70

for_loop_test8.after_for7_crit_edge.us.loopexit:  ; preds = %for_loop_inc6.us76
  br label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us:           ; preds = %for_loop_test8.after_for7_crit_edge.us.loopexit, %for_loop_body1.us
  %.us-phi.us = phi float [ %.03357.us, %for_loop_body1.us ], [ %.134.us77, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %.us-phi67.us = phi float [ %.03058.us, %for_loop_body1.us ], [ %.131.us78, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %.us-phi68.us = phi float [ %.02759.us, %for_loop_body1.us ], [ %.128.us79, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %.us-phi69.us = phi float [ %.02660.us, %for_loop_body1.us ], [ %.1.us80, %for_loop_test8.after_for7_crit_edge.us.loopexit ]
  %122 = add i32 %.02561.us, 1
  %lsr.iv.next99 = add i32 %lsr.iv98, 1
  %exitcond92.not = icmp eq i32 %122, %28
  br i1 %exitcond92.not, label %after_for3, label %for_loop_body1.us

for_loop_inc:                                     ; preds = %true_block34, %after_for3, %for_loop_body
  %123 = add nsw i32 %.03666, 1
  %lsr.iv.next101 = add i32 %lsr.iv100, 1
  %exitcond93.not = icmp eq i32 %123, %19
  br i1 %exitcond93.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3:                                       ; preds = %for_loop_test8.after_for7_crit_edge.us
  %124 = fcmp reassoc ninf nsz ogt float %.us-phi.us, 0x3D71979980000000
  br i1 %124, label %true_block34, label %for_loop_inc

true_block34:                                     ; preds = %after_for3
  %125 = fdiv reassoc ninf nsz float 1.000000e+00, %.us-phi.us
  %126 = fmul reassoc ninf nsz float %.us-phi67.us, %125
  %127 = load float*, float** %35, align 8
  %128 = load i32, i32* %36, align 4
  %129 = load i32, i32* %37, align 4
  %130 = mul i32 %128, %57
  %131 = add i32 %130, %59
  %132 = mul i32 %131, %129
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %127, i64 %133
  store float %126, float* %134, align 4
  %135 = fmul reassoc ninf nsz float %.us-phi68.us, %125
  %136 = load float*, float** %35, align 8
  %137 = load i32, i32* %36, align 4
  %138 = load i32, i32* %37, align 4
  %139 = mul i32 %137, %57
  %140 = add i32 %139, %59
  %141 = mul i32 %140, %138
  %142 = add i32 %141, 1
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %136, i64 %143
  store float %135, float* %144, align 4
  %145 = fmul reassoc ninf nsz float %.us-phi69.us, %125
  %146 = load float*, float** %35, align 8
  %147 = load i32, i32* %36, align 4
  %148 = load i32, i32* %37, align 4
  %149 = mul i32 %147, %57
  %150 = add i32 %149, %59
  %151 = mul i32 %150, %148
  %152 = add i32 %151, 2
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %146, i64 %153
  store float %145, float* %154, align 4
  %155 = load float*, float** %33, align 8
  %156 = load i32, i32* %34, align 4
  %157 = mul i32 %156, %57
  %158 = add i32 %157, %59
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %155, i64 %159
  store float 1.000000e+00, float* %160, align 4
  br label %for_loop_inc
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

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
