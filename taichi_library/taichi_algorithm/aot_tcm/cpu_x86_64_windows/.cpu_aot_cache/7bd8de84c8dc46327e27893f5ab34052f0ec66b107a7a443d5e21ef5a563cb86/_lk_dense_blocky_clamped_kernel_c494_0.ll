; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.84*, void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.84 = type { i8*, %struct.LLVMRuntime.83*, i32, i64* }
%struct.LLVMRuntime.83 = type { %struct.PreallocatedMemoryChunk.79, %struct.PreallocatedMemoryChunk.79, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.80*], [1024 x %struct.NodeManager.81*], [1024 x i8*], i8*, %struct.RandState.82*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.79 = type { i8*, i8*, i64 }
%struct.ListManager.80 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.83* }
%struct.NodeManager.81 = type { %struct.LLVMRuntime.83*, i32, i32, i32, i32, %struct.ListManager.80*, %struct.ListManager.80*, %struct.ListManager.80*, i32 }
%struct.RandState.82 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_lk_dense_blocky_clamped_kernel_c494_0_kernel_0_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %1, i64 0, i32 1, i32 0, i32 1
  %5 = load i32, i32* %4, align 4
  %6 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %1, i64 0, i32 0, i32 0, i32 0
  %7 = load i32, i32* %6, align 4
  %8 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 16
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %0, align 8
  %15 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %14, i64 0, i32 0, i32 0, i32 1
  %16 = load i32, i32* %15, align 4
  %17 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %8, align 8
  %18 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %17, i64 0, i32 14
  %19 = load i8*, i8** %18, align 8
  %20 = getelementptr inbounds i8, i8* %19, i64 12
  %21 = bitcast i8* %20 to i32*
  store i32 %16, i32* %21, align 4
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %0, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %22, i64 0, i32 2
  %24 = load i32, i32* %23, align 4
  %25 = sitofp i32 %24 to float
  %26 = fdiv reassoc ninf nsz float 1.000000e+00, %25
  %27 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %8, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 8
  %31 = bitcast i8* %30 to float*
  store float %26, float* %31, align 4
  %32 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %33 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %34 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %8, align 8
  %35 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %34, i64 0, i32 14
  %36 = load i8*, i8** %35, align 8
  %37 = getelementptr inbounds i8, i8* %36, i64 4
  %38 = bitcast i8* %37 to i32*
  store i32 %33, i32* %38, align 4
  %39 = mul i32 %33, %32
  %40 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %8, align 8
  %41 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %40, i64 0, i32 14
  %42 = bitcast i8** %41 to i32**
  %43 = load i32*, i32** %42, align 8
  store i32 %39, i32* %43, align 4
  ret void
}

; Function Attrs: nounwind
define void @_lk_dense_blocky_clamped_kernel_c494_0_kernel_1_range_for(%struct.RuntimeContext.84* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.84* %context, %struct.RuntimeContext.84** %4, align 8
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.84*, i8*, i32)* @function_body, void (%struct.RuntimeContext.84*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.84* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.84* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 3
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 4
  %25 = load float, float* %24, align 4
  %26 = fcmp reassoc ninf nsz ogt float %25, 0.000000e+00
  %27 = icmp slt i32 %17, %19
  br i1 %27, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 0, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 0, i32 0, i32 2
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 1, i32 1
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 1, i32 0, i32 1
  %33 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %21, i64 0, i32 1, i32 0, i32 2
  %34 = sub i32 0, %23
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if78, %for_loop_body.lr.ph
  %.06785 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %274, %after_if78 ]
  %35 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %35, i64 0, i32 14
  %37 = load i8*, i8** %36, align 8
  %38 = getelementptr inbounds i8, i8* %37, i64 4
  %39 = bitcast i8* %38 to i32*
  %40 = load i32, i32* %39, align 4
  %41 = sdiv i32 %.06785, %40
  %42 = mul i32 %41, %40
  %43 = xor i32 %40, %.06785
  %44 = icmp slt i32 %43, 0
  %45 = icmp ne i32 %.06785, 0
  %46 = icmp ne i32 %.06785, %42
  %47 = and i1 %45, %44
  %48 = and i1 %47, %46
  %.neg78 = sext i1 %48 to i32
  %49 = add i32 %41, %.neg78
  %50 = mul i32 %40, -1
  %51 = mul i32 %50, %49
  %52 = add i32 %34, %.06785
  %53 = add i32 %52, %51
  %54 = sitofp i32 %53 to float
  %55 = getelementptr inbounds i8, i8* %37, i64 8
  %56 = bitcast i8* %55 to float*
  %57 = load float, float* %56, align 4
  %58 = fmul reassoc ninf nsz float %57, %54
  %59 = sub i32 %49, %23
  %60 = sitofp i32 %59 to float
  %61 = fmul reassoc ninf nsz float %57, %60
  %62 = fadd reassoc ninf nsz float %58, 5.000000e-01
  %63 = tail call reassoc ninf nsz float @llvm.floor.f32(float %62)
  %64 = fptosi float %63 to i32
  %65 = getelementptr inbounds i8, i8* %37, i64 12
  %66 = bitcast i8* %65 to i32*
  %67 = load i32, i32* %66, align 4
  %68 = add i32 %67, -1
  %69 = tail call i32 @llvm.smin.i32(i32 %64, i32 %68)
  %70 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %71 = fadd reassoc ninf nsz float %61, 5.000000e-01
  %72 = tail call reassoc ninf nsz float @llvm.floor.f32(float %71)
  %73 = fptosi float %72 to i32
  %74 = getelementptr inbounds i8, i8* %37, i64 16
  %75 = bitcast i8* %74 to i32*
  %76 = load i32, i32* %75, align 4
  %77 = add i32 %76, -1
  %78 = tail call i32 @llvm.smin.i32(i32 %73, i32 %77)
  %79 = tail call i32 @llvm.smax.i32(i32 %78, i32 0)
  %80 = load float*, float** %28, align 8
  %81 = load i32, i32* %29, align 4
  %82 = load i32, i32* %30, align 4
  %83 = mul i32 %79, %81
  %84 = add i32 %70, %83
  %85 = mul i32 %84, %82
  %86 = add i32 %85, 2
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, float* %80, i64 %87
  %89 = load float, float* %88, align 4
  %90 = fcmp reassoc ninf nsz ogt float %89, 5.000000e-01
  br i1 %90, label %after_if.sink.split, label %false_block

after_for.loopexit:                               ; preds = %after_if78
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

false_block:                                      ; preds = %for_loop_body
  %91 = add nsw i32 %79, -1
  %92 = tail call i32 @llvm.smin.i32(i32 %91, i32 %77)
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = add nsw i32 %70, -1
  %95 = tail call i32 @llvm.smin.i32(i32 %94, i32 %68)
  %96 = tail call i32 @llvm.smax.i32(i32 %95, i32 0)
  %97 = mul i32 %93, %81
  %98 = add i32 %96, %97
  %99 = mul i32 %98, %82
  %100 = add i32 %99, 2
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %80, i64 %101
  %103 = load float, float* %102, align 4
  %104 = fcmp reassoc ninf nsz ogt float %103, 5.000000e-01
  br i1 %104, label %true_block1, label %after_if3

after_if.sink.split:                              ; preds = %true_block67, %for_loop_body
  %.sink = phi i32 [ %235, %true_block67 ], [ %85, %for_loop_body ]
  %105 = sext i32 %.sink to i64
  %106 = getelementptr float, float* %80, i64 %105
  %107 = load float, float* %106, align 4
  %108 = add i32 %.sink, 1
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %80, i64 %109
  %111 = load float, float* %110, align 4
  br label %after_if

after_if:                                         ; preds = %true_block67, %after_if60, %after_if.sink.split
  %.057 = phi float [ %.865, %true_block67 ], [ %.865, %after_if60 ], [ %107, %after_if.sink.split ]
  %.049 = phi float [ %.8, %true_block67 ], [ %.8, %after_if60 ], [ %111, %after_if.sink.split ]
  br i1 %26, label %true_block76, label %after_if78

true_block1:                                      ; preds = %false_block
  %112 = sext i32 %99 to i64
  %113 = getelementptr float, float* %80, i64 %112
  %114 = load float, float* %113, align 4
  %115 = add i32 %99, 1
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %80, i64 %116
  %118 = load float, float* %117, align 4
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %false_block
  %.158 = phi float [ %114, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.150 = phi float [ %118, %true_block1 ], [ 0.000000e+00, %false_block ]
  %.041 = phi i32 [ 1, %true_block1 ], [ 0, %false_block ]
  %.040 = phi float [ 2.000000e+00, %true_block1 ], [ 9.999990e+05, %false_block ]
  %119 = tail call i32 @llvm.smin.i32(i32 %70, i32 %68)
  %120 = tail call i32 @llvm.smax.i32(i32 %119, i32 0)
  %121 = add i32 %97, %120
  %122 = mul i32 %121, %82
  %123 = add i32 %122, 2
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %80, i64 %124
  %126 = load float, float* %125, align 4
  %127 = fcmp reassoc ninf nsz ogt float %126, 5.000000e-01
  br i1 %127, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %128 = sext i32 %122 to i64
  %129 = getelementptr float, float* %80, i64 %128
  %130 = load float, float* %129, align 4
  %131 = add i32 %122, 1
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %80, i64 %132
  %134 = load float, float* %133, align 4
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %.259 = phi float [ %130, %true_block4 ], [ %.158, %after_if3 ]
  %.251 = phi float [ %134, %true_block4 ], [ %.150, %after_if3 ]
  %.142 = phi i32 [ 1, %true_block4 ], [ %.041, %after_if3 ]
  %.1 = phi float [ 1.000000e+00, %true_block4 ], [ %.040, %after_if3 ]
  %135 = add nuw i32 %70, 1
  %136 = tail call i32 @llvm.smin.i32(i32 %135, i32 %68)
  %137 = tail call i32 @llvm.smax.i32(i32 %136, i32 0)
  %138 = add i32 %137, %97
  %139 = mul i32 %138, %82
  %140 = add i32 %139, 2
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %80, i64 %141
  %143 = load float, float* %142, align 4
  %144 = fcmp reassoc ninf nsz ogt float %143, 5.000000e-01
  br i1 %144, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if6
  %145 = icmp eq i32 %.142, 0
  %146 = fcmp reassoc ninf nsz ogt float %.1, 2.000000e+00
  %spec.select = select i1 %145, i1 true, i1 %146
  br i1 %spec.select, label %true_block19, label %after_if15

after_if15:                                       ; preds = %true_block19, %true_block13, %after_if6
  %.360 = phi float [ %159, %true_block19 ], [ %.259, %true_block13 ], [ %.259, %after_if6 ]
  %.352 = phi float [ %163, %true_block19 ], [ %.251, %true_block13 ], [ %.251, %after_if6 ]
  %.243 = phi i32 [ 1, %true_block19 ], [ 1, %true_block13 ], [ %.142, %after_if6 ]
  %.2 = phi float [ 2.000000e+00, %true_block19 ], [ %.1, %true_block13 ], [ %.1, %after_if6 ]
  %147 = tail call i32 @llvm.smin.i32(i32 %79, i32 %77)
  %148 = tail call i32 @llvm.smax.i32(i32 %147, i32 0)
  %149 = mul i32 %148, %81
  %150 = add i32 %96, %149
  %151 = mul i32 %150, %82
  %152 = add i32 %151, 2
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %80, i64 %153
  %155 = load float, float* %154, align 4
  %156 = fcmp reassoc ninf nsz ogt float %155, 5.000000e-01
  br i1 %156, label %true_block22, label %after_if24

true_block19:                                     ; preds = %true_block13
  %157 = sext i32 %139 to i64
  %158 = getelementptr float, float* %80, i64 %157
  %159 = load float, float* %158, align 4
  %160 = add i32 %139, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %80, i64 %161
  %163 = load float, float* %162, align 4
  br label %after_if15

true_block22:                                     ; preds = %after_if15
  %164 = icmp eq i32 %.243, 0
  %165 = fcmp reassoc ninf nsz ogt float %.2, 1.000000e+00
  %spec.select79 = select i1 %164, i1 true, i1 %165
  br i1 %spec.select79, label %true_block28, label %after_if24

after_if24:                                       ; preds = %true_block28, %true_block22, %after_if15
  %.461 = phi float [ %175, %true_block28 ], [ %.360, %true_block22 ], [ %.360, %after_if15 ]
  %.453 = phi float [ %179, %true_block28 ], [ %.352, %true_block22 ], [ %.352, %after_if15 ]
  %.344 = phi i32 [ 1, %true_block28 ], [ 1, %true_block22 ], [ %.243, %after_if15 ]
  %.3 = phi float [ 1.000000e+00, %true_block28 ], [ %.2, %true_block22 ], [ %.2, %after_if15 ]
  %166 = add i32 %120, %149
  %167 = mul i32 %166, %82
  %168 = add i32 %167, 2
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, float* %80, i64 %169
  %171 = load float, float* %170, align 4
  %172 = fcmp reassoc ninf nsz ogt float %171, 5.000000e-01
  br i1 %172, label %true_block31, label %after_if33

true_block28:                                     ; preds = %true_block22
  %173 = sext i32 %151 to i64
  %174 = getelementptr float, float* %80, i64 %173
  %175 = load float, float* %174, align 4
  %176 = add i32 %151, 1
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, float* %80, i64 %177
  %179 = load float, float* %178, align 4
  br label %after_if24

true_block31:                                     ; preds = %after_if24
  %180 = icmp eq i32 %.344, 0
  %181 = fcmp reassoc ninf nsz ogt float %.3, 0.000000e+00
  %spec.select80 = select i1 %180, i1 true, i1 %181
  br i1 %spec.select80, label %true_block37, label %after_if33

after_if33:                                       ; preds = %true_block37, %true_block31, %after_if24
  %.562 = phi float [ %191, %true_block37 ], [ %.461, %true_block31 ], [ %.461, %after_if24 ]
  %.554 = phi float [ %195, %true_block37 ], [ %.453, %true_block31 ], [ %.453, %after_if24 ]
  %.445 = phi i32 [ 1, %true_block37 ], [ 1, %true_block31 ], [ %.344, %after_if24 ]
  %.4 = phi float [ 0.000000e+00, %true_block37 ], [ %.3, %true_block31 ], [ %.3, %after_if24 ]
  %182 = add i32 %137, %149
  %183 = mul i32 %182, %82
  %184 = add i32 %183, 2
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, float* %80, i64 %185
  %187 = load float, float* %186, align 4
  %188 = fcmp reassoc ninf nsz ogt float %187, 5.000000e-01
  br i1 %188, label %true_block40, label %after_if42

true_block37:                                     ; preds = %true_block31
  %189 = sext i32 %167 to i64
  %190 = getelementptr float, float* %80, i64 %189
  %191 = load float, float* %190, align 4
  %192 = add i32 %167, 1
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, float* %80, i64 %193
  %195 = load float, float* %194, align 4
  br label %after_if33

true_block40:                                     ; preds = %after_if33
  %196 = icmp eq i32 %.445, 0
  %197 = fcmp reassoc ninf nsz ogt float %.4, 1.000000e+00
  %spec.select81 = select i1 %196, i1 true, i1 %197
  br i1 %spec.select81, label %true_block46, label %after_if42

after_if42:                                       ; preds = %true_block46, %true_block40, %after_if33
  %.663 = phi float [ %211, %true_block46 ], [ %.562, %true_block40 ], [ %.562, %after_if33 ]
  %.655 = phi float [ %215, %true_block46 ], [ %.554, %true_block40 ], [ %.554, %after_if33 ]
  %.546 = phi i32 [ 1, %true_block46 ], [ 1, %true_block40 ], [ %.445, %after_if33 ]
  %.5 = phi float [ 1.000000e+00, %true_block46 ], [ %.4, %true_block40 ], [ %.4, %after_if33 ]
  %198 = add nuw i32 %79, 1
  %199 = tail call i32 @llvm.smin.i32(i32 %198, i32 %77)
  %200 = tail call i32 @llvm.smax.i32(i32 %199, i32 0)
  %201 = mul i32 %200, %81
  %202 = add i32 %96, %201
  %203 = mul i32 %202, %82
  %204 = add i32 %203, 2
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %80, i64 %205
  %207 = load float, float* %206, align 4
  %208 = fcmp reassoc ninf nsz ogt float %207, 5.000000e-01
  br i1 %208, label %true_block49, label %after_if51

true_block46:                                     ; preds = %true_block40
  %209 = sext i32 %183 to i64
  %210 = getelementptr float, float* %80, i64 %209
  %211 = load float, float* %210, align 4
  %212 = add i32 %183, 1
  %213 = sext i32 %212 to i64
  %214 = getelementptr float, float* %80, i64 %213
  %215 = load float, float* %214, align 4
  br label %after_if42

true_block49:                                     ; preds = %after_if42
  %216 = icmp eq i32 %.546, 0
  %217 = fcmp reassoc ninf nsz ogt float %.5, 2.000000e+00
  %spec.select82 = select i1 %216, i1 true, i1 %217
  br i1 %spec.select82, label %true_block55, label %after_if51

after_if51:                                       ; preds = %true_block55, %true_block49, %after_if42
  %.764 = phi float [ %227, %true_block55 ], [ %.663, %true_block49 ], [ %.663, %after_if42 ]
  %.756 = phi float [ %231, %true_block55 ], [ %.655, %true_block49 ], [ %.655, %after_if42 ]
  %.647 = phi i32 [ 1, %true_block55 ], [ 1, %true_block49 ], [ %.546, %after_if42 ]
  %.6 = phi float [ 2.000000e+00, %true_block55 ], [ %.5, %true_block49 ], [ %.5, %after_if42 ]
  %218 = add i32 %201, %120
  %219 = mul i32 %218, %82
  %220 = add i32 %219, 2
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %80, i64 %221
  %223 = load float, float* %222, align 4
  %224 = fcmp reassoc ninf nsz ogt float %223, 5.000000e-01
  br i1 %224, label %true_block58, label %after_if60

true_block55:                                     ; preds = %true_block49
  %225 = sext i32 %203 to i64
  %226 = getelementptr float, float* %80, i64 %225
  %227 = load float, float* %226, align 4
  %228 = add i32 %203, 1
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %80, i64 %229
  %231 = load float, float* %230, align 4
  br label %after_if51

true_block58:                                     ; preds = %after_if51
  %232 = icmp eq i32 %.647, 0
  %233 = fcmp reassoc ninf nsz ogt float %.6, 1.000000e+00
  %spec.select83 = select i1 %232, i1 true, i1 %233
  br i1 %spec.select83, label %true_block64, label %after_if60

after_if60:                                       ; preds = %true_block64, %true_block58, %after_if51
  %.865 = phi float [ %243, %true_block64 ], [ %.764, %true_block58 ], [ %.764, %after_if51 ]
  %.8 = phi float [ %247, %true_block64 ], [ %.756, %true_block58 ], [ %.756, %after_if51 ]
  %.748 = phi i32 [ 1, %true_block64 ], [ 1, %true_block58 ], [ %.647, %after_if51 ]
  %.7 = phi float [ 1.000000e+00, %true_block64 ], [ %.6, %true_block58 ], [ %.6, %after_if51 ]
  %234 = add i32 %137, %201
  %235 = mul i32 %234, %82
  %236 = add i32 %235, 2
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, float* %80, i64 %237
  %239 = load float, float* %238, align 4
  %240 = fcmp reassoc ninf nsz ogt float %239, 5.000000e-01
  br i1 %240, label %true_block67, label %after_if

true_block64:                                     ; preds = %true_block58
  %241 = sext i32 %219 to i64
  %242 = getelementptr float, float* %80, i64 %241
  %243 = load float, float* %242, align 4
  %244 = add i32 %219, 1
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, float* %80, i64 %245
  %247 = load float, float* %246, align 4
  br label %after_if60

true_block67:                                     ; preds = %after_if60
  %248 = icmp eq i32 %.748, 0
  %249 = fcmp reassoc ninf nsz ogt float %.7, 2.000000e+00
  %spec.select84 = select i1 %248, i1 true, i1 %249
  br i1 %spec.select84, label %after_if.sink.split, label %after_if

true_block76:                                     ; preds = %after_if
  %250 = fmul reassoc ninf nsz float %.057, %.057
  %251 = fmul reassoc ninf nsz float %.049, %.049
  %252 = fadd reassoc ninf nsz float %251, %250
  %253 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %252)
  %254 = fcmp reassoc ninf nsz ogt float %253, %25
  br i1 %254, label %true_block79, label %after_if78

after_if78:                                       ; preds = %true_block79, %true_block76, %after_if
  %.966 = phi float [ %277, %true_block79 ], [ %.057, %true_block76 ], [ %.057, %after_if ]
  %.9 = phi float [ %278, %true_block79 ], [ %.049, %true_block76 ], [ %.049, %after_if ]
  %255 = load float*, float** %31, align 8
  %256 = load i32, i32* %32, align 4
  %257 = load i32, i32* %33, align 4
  %258 = sub i32 %256, %40
  %259 = mul i32 %258, %49
  %260 = add i32 %.06785, %259
  %261 = mul i32 %260, %257
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, float* %255, i64 %262
  store float %.966, float* %263, align 4
  %264 = load float*, float** %31, align 8
  %265 = load i32, i32* %32, align 4
  %266 = load i32, i32* %33, align 4
  %267 = sub i32 %265, %40
  %268 = mul i32 %267, %49
  %269 = add i32 %.06785, %268
  %270 = mul i32 %269, %266
  %271 = add i32 %270, 1
  %272 = sext i32 %271 to i64
  %273 = getelementptr float, float* %264, i64 %272
  store float %.9, float* %273, align 4
  %274 = add nsw i32 %.06785, 1
  %exitcond.not = icmp eq i32 %19, %274
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block79:                                     ; preds = %true_block76
  %275 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %253, float 0x3EB0C6F7A0000000)
  %276 = fdiv reassoc ninf nsz float %25, %275
  %277 = fmul reassoc ninf nsz float %276, %.057
  %278 = fmul reassoc ninf nsz float %276, %.049
  br label %after_if78
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.sqrt.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.84, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.84**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.84*, %struct.RuntimeContext.84** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.84* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.84* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
