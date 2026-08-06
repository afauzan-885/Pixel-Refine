; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.72*, void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*, i32)*, void (%struct.RuntimeContext.72*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.72 = type { i8*, %struct.LLVMRuntime.71*, i32, i64* }
%struct.LLVMRuntime.71 = type { %struct.PreallocatedMemoryChunk.67, %struct.PreallocatedMemoryChunk.67, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.68*], [1024 x %struct.NodeManager.69*], [1024 x i8*], i8*, %struct.RandState.70*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.67 = type { i8*, i8*, i64 }
%struct.ListManager.68 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.71* }
%struct.NodeManager.69 = type { %struct.LLVMRuntime.71*, i32, i32, i32, i32, %struct.ListManager.68*, %struct.ListManager.68*, %struct.ListManager.68*, i32 }
%struct.RandState.70 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_lk_dense_blocky_kernel_c492_0_kernel_0_serial(%struct.RuntimeContext.72* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.72* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 1
  %5 = load i32, i32* %4, align 4
  %6 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 0, i32 0, i32 0
  %7 = load i32, i32* %6, align 4
  %8 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 16
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %15 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %14, i64 0, i32 0, i32 0, i32 1
  %16 = load i32, i32* %15, align 4
  %17 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %8, align 8
  %18 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %17, i64 0, i32 14
  %19 = load i8*, i8** %18, align 8
  %20 = getelementptr inbounds i8, i8* %19, i64 12
  %21 = bitcast i8* %20 to i32*
  store i32 %16, i32* %21, align 4
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2
  %24 = load i32, i32* %23, align 4
  %25 = sitofp i32 %24 to float
  %26 = fdiv reassoc ninf nsz float 1.000000e+00, %25
  %27 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %8, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 8
  %31 = bitcast i8* %30 to float*
  store float %26, float* %31, align 4
  %32 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %33 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %34 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %8, align 8
  %35 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %34, i64 0, i32 14
  %36 = load i8*, i8** %35, align 8
  %37 = getelementptr inbounds i8, i8* %36, i64 4
  %38 = bitcast i8* %37 to i32*
  store i32 %33, i32* %38, align 4
  %39 = mul i32 %33, %32
  %40 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %8, align 8
  %41 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %40, i64 0, i32 14
  %42 = bitcast i8** %41 to i32**
  %43 = load i32*, i32** %42, align 8
  store i32 %39, i32* %43, align 4
  ret void
}

; Function Attrs: nounwind
define void @_lk_dense_blocky_kernel_c492_0_kernel_1_range_for(%struct.RuntimeContext.72* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.72* %context, %struct.RuntimeContext.72** %4, align 8
  store void (%struct.RuntimeContext.72*, i8*)* null, void (%struct.RuntimeContext.72*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.72*, i8*, i32)* @function_body, void (%struct.RuntimeContext.72*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.72*, i8*)* null, void (%struct.RuntimeContext.72*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.72* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.72* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 3
  %23 = load i32, i32* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = sub i32 0, %23
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.06278 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %135, %after_if ]
  %29 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.06278, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.06278
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.06278, 0
  %40 = icmp ne i32 %.06278, %36
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg71 = sext i1 %42 to i32
  %43 = add i32 %35, %.neg71
  %44 = mul i32 %34, -1
  %45 = mul i32 %44, %43
  %46 = add i32 %28, %.06278
  %47 = add i32 %46, %45
  %48 = sitofp i32 %47 to float
  %49 = getelementptr inbounds i8, i8* %31, i64 8
  %50 = bitcast i8* %49 to float*
  %51 = load float, float* %50, align 4
  %52 = fmul reassoc ninf nsz float %51, %48
  %53 = sub i32 %43, %23
  %54 = sitofp i32 %53 to float
  %55 = fmul reassoc ninf nsz float %51, %54
  %56 = fadd reassoc ninf nsz float %52, 5.000000e-01
  %57 = tail call reassoc ninf nsz float @llvm.floor.f32(float %56)
  %58 = fptosi float %57 to i32
  %59 = getelementptr inbounds i8, i8* %31, i64 12
  %60 = bitcast i8* %59 to i32*
  %61 = load i32, i32* %60, align 4
  %62 = add i32 %61, -1
  %63 = tail call i32 @llvm.smin.i32(i32 %58, i32 %62)
  %64 = tail call i32 @llvm.smax.i32(i32 %63, i32 0)
  %65 = fadd reassoc ninf nsz float %55, 5.000000e-01
  %66 = tail call reassoc ninf nsz float @llvm.floor.f32(float %65)
  %67 = fptosi float %66 to i32
  %68 = getelementptr inbounds i8, i8* %31, i64 16
  %69 = bitcast i8* %68 to i32*
  %70 = load i32, i32* %69, align 4
  %71 = add i32 %70, -1
  %72 = tail call i32 @llvm.smin.i32(i32 %67, i32 %71)
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = load float*, float** %25, align 8
  %75 = load i32, i32* %26, align 4
  %76 = load i32, i32* %27, align 4
  %77 = mul i32 %73, %75
  %78 = add i32 %64, %77
  %79 = mul i32 %78, %76
  %80 = add i32 %79, 2
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %74, i64 %81
  %83 = load float, float* %82, align 4
  %84 = fcmp reassoc ninf nsz ogt float %83, 5.000000e-01
  br i1 %84, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %85 = sext i32 %79 to i64
  %86 = getelementptr float, float* %74, i64 %85
  %87 = load float, float* %86, align 4
  %88 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %89 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %88, i64 0, i32 1, i32 1
  %90 = load float*, float** %89, align 8
  %91 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %88, i64 0, i32 1, i32 0, i32 1
  %92 = load i32, i32* %91, align 4
  %93 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %88, i64 0, i32 1, i32 0, i32 2
  %94 = load i32, i32* %93, align 4
  %95 = sub i32 %92, %34
  %96 = mul i32 %95, %43
  %97 = add i32 %.06278, %96
  %98 = mul i32 %97, %94
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %90, i64 %99
  store float %87, float* %100, align 4
  %101 = load float*, float** %25, align 8
  %102 = load i32, i32* %26, align 4
  %103 = load i32, i32* %27, align 4
  %104 = mul i32 %102, %73
  %105 = add i32 %104, %64
  %106 = mul i32 %105, %103
  %107 = add i32 %106, 1
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, float* %101, i64 %108
  %110 = load float, float* %109, align 4
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %111 = add nsw i32 %73, -1
  %112 = tail call i32 @llvm.smin.i32(i32 %111, i32 %71)
  %113 = tail call i32 @llvm.smax.i32(i32 %112, i32 0)
  %114 = add nsw i32 %64, -1
  %115 = tail call i32 @llvm.smin.i32(i32 %114, i32 %62)
  %116 = tail call i32 @llvm.smax.i32(i32 %115, i32 0)
  %117 = mul i32 %113, %75
  %118 = add i32 %116, %117
  %119 = mul i32 %118, %76
  %120 = add i32 %119, 2
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, float* %74, i64 %121
  %123 = load float, float* %122, align 4
  %124 = fcmp reassoc ninf nsz ogt float %123, 5.000000e-01
  br i1 %124, label %true_block1, label %after_if3

after_if:                                         ; preds = %after_if69, %true_block
  %.sink = phi float** [ %275, %after_if69 ], [ %89, %true_block ]
  %.sink85 = phi i32* [ %277, %after_if69 ], [ %91, %true_block ]
  %.sink84 = phi i32* [ %279, %after_if69 ], [ %93, %true_block ]
  %.8.sink = phi float [ %.8, %after_if69 ], [ %110, %true_block ]
  %125 = load float*, float** %.sink, align 8
  %126 = load i32, i32* %.sink85, align 4
  %127 = load i32, i32* %.sink84, align 4
  %128 = sub i32 %126, %34
  %129 = mul i32 %128, %43
  %130 = add i32 %.06278, %129
  %131 = mul i32 %130, %127
  %132 = add i32 %131, 1
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %125, i64 %133
  store float %.8.sink, float* %134, align 4
  %135 = add nsw i32 %.06278, 1
  %exitcond.not = icmp eq i32 %19, %135
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block1:                                      ; preds = %false_block
  %136 = sext i32 %119 to i64
  %137 = getelementptr float, float* %74, i64 %136
  %138 = load float, float* %137, align 4
  %139 = add i32 %119, 1
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %74, i64 %140
  %142 = load float, float* %141, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %false_block
  %.053 = phi float [ %138, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.045 = phi float [ %142, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.037 = phi i32 [ 1, %true_block1 ], [ 0, %false_block ]
  %.036 = phi float [ 2.000000e+00, %true_block1 ], [ 9.999990e+05, %false_block ]
  %143 = tail call i32 @llvm.smin.i32(i32 %64, i32 %62)
  %144 = tail call i32 @llvm.smax.i32(i32 %143, i32 0)
  %145 = add i32 %117, %144
  %146 = mul i32 %145, %76
  %147 = add i32 %146, 2
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %74, i64 %148
  %150 = load float, float* %149, align 4
  %151 = fcmp reassoc ninf nsz ogt float %150, 5.000000e-01
  br i1 %151, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %152 = sext i32 %146 to i64
  %153 = getelementptr float, float* %74, i64 %152
  %154 = load float, float* %153, align 4
  %155 = add i32 %146, 1
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, float* %74, i64 %156
  %158 = load float, float* %157, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %.154 = phi float [ %154, %true_block4 ], [ %.053, %after_if3 ]
  %.146 = phi float [ %158, %true_block4 ], [ %.045, %after_if3 ]
  %.138 = phi i32 [ 1, %true_block4 ], [ %.037, %after_if3 ]
  %.1 = phi float [ 1.000000e+00, %true_block4 ], [ %.036, %after_if3 ]
  %159 = add nuw i32 %64, 1
  %160 = tail call i32 @llvm.smin.i32(i32 %159, i32 %62)
  %161 = tail call i32 @llvm.smax.i32(i32 %160, i32 0)
  %162 = add i32 %161, %117
  %163 = mul i32 %162, %76
  %164 = add i32 %163, 2
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, float* %74, i64 %165
  %167 = load float, float* %166, align 4
  %168 = fcmp reassoc ninf nsz ogt float %167, 5.000000e-01
  br i1 %168, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if6
  %169 = icmp eq i32 %.138, 0
  %170 = fcmp reassoc ninf nsz ogt float %.1, 2.000000e+00
  %spec.select = select i1 %169, i1 true, i1 %170
  br i1 %spec.select, label %true_block19, label %after_if15

after_if15:                                       ; preds = %true_block19, %true_block13, %after_if6
  %.255 = phi float [ %183, %true_block19 ], [ %.154, %true_block13 ], [ %.154, %after_if6 ]
  %.247 = phi float [ %187, %true_block19 ], [ %.146, %true_block13 ], [ %.146, %after_if6 ]
  %.239 = phi i32 [ 1, %true_block19 ], [ 1, %true_block13 ], [ %.138, %after_if6 ]
  %.2 = phi float [ 2.000000e+00, %true_block19 ], [ %.1, %true_block13 ], [ %.1, %after_if6 ]
  %171 = tail call i32 @llvm.smin.i32(i32 %73, i32 %71)
  %172 = tail call i32 @llvm.smax.i32(i32 %171, i32 0)
  %173 = mul i32 %172, %75
  %174 = add i32 %116, %173
  %175 = mul i32 %174, %76
  %176 = add i32 %175, 2
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, float* %74, i64 %177
  %179 = load float, float* %178, align 4
  %180 = fcmp reassoc ninf nsz ogt float %179, 5.000000e-01
  br i1 %180, label %true_block22, label %after_if24

true_block19:                                     ; preds = %true_block13
  %181 = sext i32 %163 to i64
  %182 = getelementptr float, float* %74, i64 %181
  %183 = load float, float* %182, align 4
  %184 = add i32 %163, 1
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, float* %74, i64 %185
  %187 = load float, float* %186, align 4
  br label %after_if15

true_block22:                                     ; preds = %after_if15
  %188 = icmp eq i32 %.239, 0
  %189 = fcmp reassoc ninf nsz ogt float %.2, 1.000000e+00
  %spec.select72 = select i1 %188, i1 true, i1 %189
  br i1 %spec.select72, label %true_block28, label %after_if24

after_if24:                                       ; preds = %true_block28, %true_block22, %after_if15
  %.356 = phi float [ %199, %true_block28 ], [ %.255, %true_block22 ], [ %.255, %after_if15 ]
  %.348 = phi float [ %203, %true_block28 ], [ %.247, %true_block22 ], [ %.247, %after_if15 ]
  %.340 = phi i32 [ 1, %true_block28 ], [ 1, %true_block22 ], [ %.239, %after_if15 ]
  %.3 = phi float [ 1.000000e+00, %true_block28 ], [ %.2, %true_block22 ], [ %.2, %after_if15 ]
  %190 = add i32 %144, %173
  %191 = mul i32 %190, %76
  %192 = add i32 %191, 2
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, float* %74, i64 %193
  %195 = load float, float* %194, align 4
  %196 = fcmp reassoc ninf nsz ogt float %195, 5.000000e-01
  br i1 %196, label %true_block31, label %after_if33

true_block28:                                     ; preds = %true_block22
  %197 = sext i32 %175 to i64
  %198 = getelementptr float, float* %74, i64 %197
  %199 = load float, float* %198, align 4
  %200 = add i32 %175, 1
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, float* %74, i64 %201
  %203 = load float, float* %202, align 4
  br label %after_if24

true_block31:                                     ; preds = %after_if24
  %204 = icmp eq i32 %.340, 0
  %205 = fcmp reassoc ninf nsz ogt float %.3, 0.000000e+00
  %spec.select73 = select i1 %204, i1 true, i1 %205
  br i1 %spec.select73, label %true_block37, label %after_if33

after_if33:                                       ; preds = %true_block37, %true_block31, %after_if24
  %.457 = phi float [ %215, %true_block37 ], [ %.356, %true_block31 ], [ %.356, %after_if24 ]
  %.449 = phi float [ %219, %true_block37 ], [ %.348, %true_block31 ], [ %.348, %after_if24 ]
  %.441 = phi i32 [ 1, %true_block37 ], [ 1, %true_block31 ], [ %.340, %after_if24 ]
  %.4 = phi float [ 0.000000e+00, %true_block37 ], [ %.3, %true_block31 ], [ %.3, %after_if24 ]
  %206 = add i32 %161, %173
  %207 = mul i32 %206, %76
  %208 = add i32 %207, 2
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %74, i64 %209
  %211 = load float, float* %210, align 4
  %212 = fcmp reassoc ninf nsz ogt float %211, 5.000000e-01
  br i1 %212, label %true_block40, label %after_if42

true_block37:                                     ; preds = %true_block31
  %213 = sext i32 %191 to i64
  %214 = getelementptr float, float* %74, i64 %213
  %215 = load float, float* %214, align 4
  %216 = add i32 %191, 1
  %217 = sext i32 %216 to i64
  %218 = getelementptr float, float* %74, i64 %217
  %219 = load float, float* %218, align 4
  br label %after_if33

true_block40:                                     ; preds = %after_if33
  %220 = icmp eq i32 %.441, 0
  %221 = fcmp reassoc ninf nsz ogt float %.4, 1.000000e+00
  %spec.select74 = select i1 %220, i1 true, i1 %221
  br i1 %spec.select74, label %true_block46, label %after_if42

after_if42:                                       ; preds = %true_block46, %true_block40, %after_if33
  %.558 = phi float [ %235, %true_block46 ], [ %.457, %true_block40 ], [ %.457, %after_if33 ]
  %.550 = phi float [ %239, %true_block46 ], [ %.449, %true_block40 ], [ %.449, %after_if33 ]
  %.542 = phi i32 [ 1, %true_block46 ], [ 1, %true_block40 ], [ %.441, %after_if33 ]
  %.5 = phi float [ 1.000000e+00, %true_block46 ], [ %.4, %true_block40 ], [ %.4, %after_if33 ]
  %222 = add nuw i32 %73, 1
  %223 = tail call i32 @llvm.smin.i32(i32 %222, i32 %71)
  %224 = tail call i32 @llvm.smax.i32(i32 %223, i32 0)
  %225 = mul i32 %224, %75
  %226 = add i32 %116, %225
  %227 = mul i32 %226, %76
  %228 = add i32 %227, 2
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %74, i64 %229
  %231 = load float, float* %230, align 4
  %232 = fcmp reassoc ninf nsz ogt float %231, 5.000000e-01
  br i1 %232, label %true_block49, label %after_if51

true_block46:                                     ; preds = %true_block40
  %233 = sext i32 %207 to i64
  %234 = getelementptr float, float* %74, i64 %233
  %235 = load float, float* %234, align 4
  %236 = add i32 %207, 1
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, float* %74, i64 %237
  %239 = load float, float* %238, align 4
  br label %after_if42

true_block49:                                     ; preds = %after_if42
  %240 = icmp eq i32 %.542, 0
  %241 = fcmp reassoc ninf nsz ogt float %.5, 2.000000e+00
  %spec.select75 = select i1 %240, i1 true, i1 %241
  br i1 %spec.select75, label %true_block55, label %after_if51

after_if51:                                       ; preds = %true_block55, %true_block49, %after_if42
  %.659 = phi float [ %251, %true_block55 ], [ %.558, %true_block49 ], [ %.558, %after_if42 ]
  %.651 = phi float [ %255, %true_block55 ], [ %.550, %true_block49 ], [ %.550, %after_if42 ]
  %.643 = phi i32 [ 1, %true_block55 ], [ 1, %true_block49 ], [ %.542, %after_if42 ]
  %.6 = phi float [ 2.000000e+00, %true_block55 ], [ %.5, %true_block49 ], [ %.5, %after_if42 ]
  %242 = add i32 %225, %144
  %243 = mul i32 %242, %76
  %244 = add i32 %243, 2
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, float* %74, i64 %245
  %247 = load float, float* %246, align 4
  %248 = fcmp reassoc ninf nsz ogt float %247, 5.000000e-01
  br i1 %248, label %true_block58, label %after_if60

true_block55:                                     ; preds = %true_block49
  %249 = sext i32 %227 to i64
  %250 = getelementptr float, float* %74, i64 %249
  %251 = load float, float* %250, align 4
  %252 = add i32 %227, 1
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, float* %74, i64 %253
  %255 = load float, float* %254, align 4
  br label %after_if51

true_block58:                                     ; preds = %after_if51
  %256 = icmp eq i32 %.643, 0
  %257 = fcmp reassoc ninf nsz ogt float %.6, 1.000000e+00
  %spec.select76 = select i1 %256, i1 true, i1 %257
  br i1 %spec.select76, label %true_block64, label %after_if60

after_if60:                                       ; preds = %true_block64, %true_block58, %after_if51
  %.760 = phi float [ %267, %true_block64 ], [ %.659, %true_block58 ], [ %.659, %after_if51 ]
  %.752 = phi float [ %271, %true_block64 ], [ %.651, %true_block58 ], [ %.651, %after_if51 ]
  %.744 = phi i32 [ 1, %true_block64 ], [ 1, %true_block58 ], [ %.643, %after_if51 ]
  %.7 = phi float [ 1.000000e+00, %true_block64 ], [ %.6, %true_block58 ], [ %.6, %after_if51 ]
  %258 = add i32 %161, %225
  %259 = mul i32 %258, %76
  %260 = add i32 %259, 2
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, float* %74, i64 %261
  %263 = load float, float* %262, align 4
  %264 = fcmp reassoc ninf nsz ogt float %263, 5.000000e-01
  br i1 %264, label %true_block67, label %after_if69

true_block64:                                     ; preds = %true_block58
  %265 = sext i32 %243 to i64
  %266 = getelementptr float, float* %74, i64 %265
  %267 = load float, float* %266, align 4
  %268 = add i32 %243, 1
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, float* %74, i64 %269
  %271 = load float, float* %270, align 4
  br label %after_if60

true_block67:                                     ; preds = %after_if60
  %272 = icmp eq i32 %.744, 0
  %273 = fcmp reassoc ninf nsz ogt float %.7, 2.000000e+00
  %spec.select77 = select i1 %272, i1 true, i1 %273
  br i1 %spec.select77, label %true_block73, label %after_if69

after_if69:                                       ; preds = %true_block73, %true_block67, %after_if60
  %.861 = phi float [ %289, %true_block73 ], [ %.760, %true_block67 ], [ %.760, %after_if60 ]
  %.8 = phi float [ %293, %true_block73 ], [ %.752, %true_block67 ], [ %.752, %after_if60 ]
  %274 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %275 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %274, i64 0, i32 1, i32 1
  %276 = load float*, float** %275, align 8
  %277 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %274, i64 0, i32 1, i32 0, i32 1
  %278 = load i32, i32* %277, align 4
  %279 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %274, i64 0, i32 1, i32 0, i32 2
  %280 = load i32, i32* %279, align 4
  %281 = sub i32 %278, %34
  %282 = mul i32 %281, %43
  %283 = add i32 %.06278, %282
  %284 = mul i32 %283, %280
  %285 = sext i32 %284 to i64
  %286 = getelementptr float, float* %276, i64 %285
  store float %.861, float* %286, align 4
  br label %after_if

true_block73:                                     ; preds = %true_block67
  %287 = sext i32 %259 to i64
  %288 = getelementptr float, float* %74, i64 %287
  %289 = load float, float* %288, align 4
  %290 = add i32 %259, 1
  %291 = sext i32 %290 to i64
  %292 = getelementptr float, float* %74, i64 %291
  %293 = load float, float* %292, align 4
  br label %after_if69
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.72, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.72**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.72*, %struct.RuntimeContext.72** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.72*, i8*, i32)*, void (%struct.RuntimeContext.72*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.72*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.72* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.72* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.72* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.72* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.72* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.72*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.72* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
