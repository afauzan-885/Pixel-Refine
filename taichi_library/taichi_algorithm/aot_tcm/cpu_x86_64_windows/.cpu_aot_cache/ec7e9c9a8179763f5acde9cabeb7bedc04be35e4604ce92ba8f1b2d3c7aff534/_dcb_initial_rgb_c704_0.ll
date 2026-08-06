; ModuleID = 'kernel'
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
define void @_dcb_initial_rgb_c704_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_initial_rgb_c704_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 8
  %29 = load i32, i32* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 2
  %36 = sub i32 0, %17
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %36, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if9 ]
  %.01746 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %179, %after_if9 ]
  %37 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.01746, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.01746
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.01746, 0
  %48 = icmp ne i32 %.01746, %44
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg18 = sext i1 %50 to i32
  %51 = add i32 %43, %.neg18
  %52 = mul i32 %51, %42
  %53 = mul i32 %42, -1
  %54 = mul i32 %53, %51
  %55 = add i32 %.01746, %54
  %56 = sdiv i32 %51, 2
  %57 = icmp slt i32 %51, 0
  %58 = shl nsw i32 %56, 1
  %59 = icmp ne i32 %58, %51
  %60 = and i1 %57, %59
  %.neg19.neg = zext i1 %60 to i32
  %.neg21 = sub nsw i32 %.neg19.neg, %56
  %.neg20 = shl i32 %.neg21, 1
  %61 = sub i32 0, %51
  %62 = icmp eq i32 %.neg20, %61
  %63 = sdiv i32 %55, 2
  %64 = icmp slt i32 %55, 0
  %65 = shl nsw i32 %63, 1
  %66 = icmp ne i32 %55, %65
  %67 = and i1 %64, %66
  %.neg22.neg = zext i1 %67 to i32
  %.neg24 = sub nsw i32 %.neg22.neg, %63
  %.neg23 = shl i32 %.neg24, 1
  %68 = add i32 %lsr.iv, %52
  %.not = icmp eq i32 %68, %.neg23
  %. = select i1 %.not, i32 %23, i32 %25
  %.29 = select i1 %.not, i32 %27, i32 %29
  %.016 = select i1 %62, i32 %., i32 %.29
  %69 = add i32 %51, -1
  %70 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %71 = getelementptr inbounds i8, i8* %39, i64 8
  %72 = bitcast i8* %71 to i32*
  %73 = load i32, i32* %72, align 4
  %74 = add i32 %73, -1
  %75 = add i32 %51, 1
  %76 = tail call i32 @llvm.smin.i32(i32 %74, i32 %75)
  %77 = add i32 %55, -1
  %78 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %79 = getelementptr inbounds i8, i8* %39, i64 12
  %80 = bitcast i8* %79 to i32*
  %81 = load i32, i32* %80, align 4
  %82 = add i32 %81, -1
  %83 = add i32 %55, 1
  %84 = tail call i32 @llvm.smin.i32(i32 %82, i32 %83)
  %85 = load float*, float** %31, align 8
  %86 = load i32, i32* %32, align 4
  %87 = mul i32 %51, %86
  %88 = sub i32 %86, %42
  %89 = mul i32 %88, %51
  %90 = add i32 %.01746, %89
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, float* %85, i64 %91
  %93 = load float, float* %92, align 4
  switch i32 %.016, label %false_block11 [
    i32 0, label %true_block7
    i32 2, label %true_block10
  ]

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block7:                                      ; preds = %for_loop_body
  %94 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %95 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %94, i64 0, i32 0, i32 1
  %96 = load float*, float** %95, align 8
  %97 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %94, i64 0, i32 0, i32 0, i32 1
  %98 = load i32, i32* %97, align 4
  %99 = sub i32 %98, %42
  %100 = mul i32 %99, %51
  %101 = add i32 %.01746, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %96, i64 %102
  %104 = load float, float* %103, align 4
  %105 = mul i32 %98, %70
  %106 = add i32 %105, %78
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, float* %96, i64 %107
  %109 = load float, float* %108, align 4
  %110 = mul i32 %70, %86
  %111 = add i32 %78, %110
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, float* %85, i64 %112
  %114 = load float, float* %113, align 4
  %115 = add i32 %105, %84
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %96, i64 %116
  %118 = load float, float* %117, align 4
  %119 = add i32 %84, %110
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %85, i64 %120
  %122 = load float, float* %121, align 4
  %123 = mul i32 %98, %76
  %124 = add i32 %123, %78
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %96, i64 %125
  %127 = load float, float* %126, align 4
  %128 = mul i32 %76, %86
  %129 = add i32 %78, %128
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, float* %85, i64 %130
  %132 = load float, float* %131, align 4
  %133 = add i32 %123, %84
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %96, i64 %134
  %136 = load float, float* %135, align 4
  %137 = add i32 %84, %128
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %85, i64 %138
  %140 = load float, float* %139, align 4
  %141 = fadd reassoc ninf nsz float %109, %118
  %142 = fadd reassoc ninf nsz float %114, %122
  %143 = fadd reassoc ninf nsz float %141, %127
  %144 = fadd reassoc ninf nsz float %142, %132
  %145 = fadd reassoc ninf nsz float %143, %136
  %146 = fadd reassoc ninf nsz float %144, %140
  %147 = fsub reassoc ninf nsz float %145, %146
  %148 = fmul reassoc ninf nsz float %147, 2.500000e-01
  %149 = fadd reassoc ninf nsz float %148, %93
  br label %after_if9

after_if9:                                        ; preds = %false_block11, %true_block10, %true_block7
  %.013 = phi float [ %104, %true_block7 ], [ %235, %true_block10 ], [ %.47, %false_block11 ]
  %.012 = phi float [ %149, %true_block7 ], [ %190, %true_block10 ], [ %.48, %false_block11 ]
  %150 = load float*, float** %33, align 8
  %151 = load i32, i32* %34, align 4
  %152 = load i32, i32* %35, align 4
  %153 = sub i32 %151, %42
  %154 = mul i32 %153, %51
  %155 = add i32 %.01746, %154
  %156 = mul i32 %155, %152
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %150, i64 %157
  store float %.013, float* %158, align 4
  %159 = load float*, float** %33, align 8
  %160 = load i32, i32* %34, align 4
  %161 = load i32, i32* %35, align 4
  %162 = sub i32 %160, %42
  %163 = mul i32 %162, %51
  %164 = add i32 %.01746, %163
  %165 = mul i32 %164, %161
  %166 = add i32 %165, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, float* %159, i64 %167
  store float %93, float* %168, align 4
  %169 = load float*, float** %33, align 8
  %170 = load i32, i32* %34, align 4
  %171 = load i32, i32* %35, align 4
  %172 = sub i32 %170, %42
  %173 = mul i32 %172, %51
  %174 = add i32 %.01746, %173
  %175 = mul i32 %174, %171
  %176 = add i32 %175, 2
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, float* %169, i64 %177
  store float %.012, float* %178, align 4
  %179 = add nsw i32 %.01746, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %19, %179
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %for_loop_body
  %180 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %181 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %180, i64 0, i32 0, i32 1
  %182 = load float*, float** %181, align 8
  %183 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %180, i64 0, i32 0, i32 0, i32 1
  %184 = load i32, i32* %183, align 4
  %185 = sub i32 %184, %42
  %186 = mul i32 %185, %51
  %187 = add i32 %.01746, %186
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, float* %182, i64 %188
  %190 = load float, float* %189, align 4
  %191 = mul i32 %184, %70
  %192 = add i32 %191, %78
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, float* %182, i64 %193
  %195 = load float, float* %194, align 4
  %196 = mul i32 %70, %86
  %197 = add i32 %78, %196
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, float* %85, i64 %198
  %200 = load float, float* %199, align 4
  %201 = add i32 %191, %84
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %182, i64 %202
  %204 = load float, float* %203, align 4
  %205 = add i32 %84, %196
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, float* %85, i64 %206
  %208 = load float, float* %207, align 4
  %209 = mul i32 %184, %76
  %210 = add i32 %209, %78
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %182, i64 %211
  %213 = load float, float* %212, align 4
  %214 = mul i32 %76, %86
  %215 = add i32 %78, %214
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, float* %85, i64 %216
  %218 = load float, float* %217, align 4
  %219 = add i32 %209, %84
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %182, i64 %220
  %222 = load float, float* %221, align 4
  %223 = add i32 %84, %214
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %85, i64 %224
  %226 = load float, float* %225, align 4
  %227 = fadd reassoc ninf nsz float %195, %204
  %228 = fadd reassoc ninf nsz float %200, %208
  %229 = fadd reassoc ninf nsz float %227, %213
  %230 = fadd reassoc ninf nsz float %228, %218
  %231 = fadd reassoc ninf nsz float %229, %222
  %232 = fadd reassoc ninf nsz float %230, %226
  %233 = fsub reassoc ninf nsz float %231, %232
  %234 = fmul reassoc ninf nsz float %233, 2.500000e-01
  %235 = fadd reassoc ninf nsz float %234, %93
  br label %after_if9

false_block11:                                    ; preds = %for_loop_body
  %236 = and i32 %78, 2147483646
  %.not28 = icmp eq i32 %78, %236
  %.30 = select i1 %.not28, i32 %23, i32 %25
  %.31 = select i1 %.not28, i32 %27, i32 %29
  %.011 = select i1 %62, i32 %.30, i32 %.31
  %237 = icmp eq i32 %.011, 0
  %238 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %239 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %238, i64 0, i32 0, i32 1
  %240 = load float*, float** %239, align 8
  %241 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %238, i64 0, i32 0, i32 0, i32 1
  %242 = load i32, i32* %241, align 4
  %243 = mul i32 %242, %51
  %244 = add i32 %243, %78
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, float* %240, i64 %245
  %247 = load float, float* %246, align 4
  %248 = add i32 %78, %87
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, float* %85, i64 %249
  %251 = load float, float* %250, align 4
  %252 = add i32 %243, %84
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, float* %240, i64 %253
  %255 = load float, float* %254, align 4
  %256 = add i32 %84, %87
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, float* %85, i64 %257
  %259 = load float, float* %258, align 4
  %260 = fadd reassoc ninf nsz float %247, %255
  %261 = fadd reassoc ninf nsz float %251, %259
  %262 = fsub reassoc ninf nsz float %260, %261
  %263 = fmul reassoc ninf nsz float %262, 5.000000e-01
  %264 = fadd reassoc ninf nsz float %263, %93
  %265 = mul i32 %242, %70
  %266 = sub i32 %265, %52
  %267 = add i32 %.01746, %266
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, float* %240, i64 %268
  %270 = load float, float* %269, align 4
  %271 = mul i32 %70, %86
  %272 = sub i32 %271, %52
  %273 = add i32 %.01746, %272
  %274 = sext i32 %273 to i64
  %275 = getelementptr float, float* %85, i64 %274
  %276 = load float, float* %275, align 4
  %277 = mul i32 %242, %76
  %278 = sub i32 %277, %52
  %279 = add i32 %.01746, %278
  %280 = sext i32 %279 to i64
  %281 = getelementptr float, float* %240, i64 %280
  %282 = load float, float* %281, align 4
  %283 = mul i32 %76, %86
  %284 = sub i32 %283, %52
  %285 = add i32 %.01746, %284
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, float* %85, i64 %286
  %288 = load float, float* %287, align 4
  %289 = fadd reassoc ninf nsz float %270, %282
  %290 = fadd reassoc ninf nsz float %276, %288
  %291 = fsub reassoc ninf nsz float %289, %290
  %292 = fmul reassoc ninf nsz float %291, 5.000000e-01
  %293 = fadd reassoc ninf nsz float %292, %93
  %.47 = select i1 %237, float %264, float %293
  %.48 = select i1 %237, float %293, float %264
  br label %after_if9
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

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
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
