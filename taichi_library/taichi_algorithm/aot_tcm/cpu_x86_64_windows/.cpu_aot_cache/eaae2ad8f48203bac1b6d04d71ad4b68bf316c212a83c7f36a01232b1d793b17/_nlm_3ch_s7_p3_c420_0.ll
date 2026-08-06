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
define void @_nlm_3ch_s7_p3_c420_0_kernel_0_serial(%struct.RuntimeContext.72* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.72* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %1, i64 0, i32 5
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 20
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fmul reassoc ninf nsz float %4, 3.500000e+00
  %13 = fadd reassoc ninf nsz float %12, 0x3F60624DE0000000
  %14 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 16
  %18 = bitcast i8* %17 to float*
  store float %13, float* %18, align 4
  %19 = fmul reassoc ninf nsz float %3, 0x3FE6666660000000
  %20 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %21 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %20, i64 0, i32 7
  %22 = load float, float* %21, align 4
  %23 = fmul reassoc ninf nsz float %19, %22
  %24 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %24, i64 0, i32 14
  %26 = load i8*, i8** %25, align 8
  %27 = getelementptr inbounds i8, i8* %26, i64 24
  %28 = bitcast i8* %27 to float*
  store float %23, float* %28, align 4
  %29 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %29, i64 0, i32 3
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 8
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %0, align 8
  %39 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %38, i64 0, i32 4
  %40 = load i32, i32* %39, align 4
  %41 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %41, i64 0, i32 14
  %43 = load i8*, i8** %42, align 8
  %44 = getelementptr inbounds i8, i8* %43, i64 12
  %45 = bitcast i8* %44 to i32*
  store i32 %40, i32* %45, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %40, i32 0)
  %47 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  store i32 %46, i32* %51, align 4
  %52 = mul i32 %46, %37
  %53 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %6, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %53, i64 0, i32 14
  %55 = bitcast i8** %54 to i32**
  %56 = load i32*, i32** %55, align 8
  store i32 %52, i32* %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_nlm_3ch_s7_p3_c420_0_kernel_1_range_for(%struct.RuntimeContext.72* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext.72* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 6
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if47, %for_loop_body.lr.ph
  %.06998 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %604, %after_if47 ]
  %31 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.06998, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.06998
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.06998, 0
  %42 = icmp ne i32 %38, %.06998
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg75 = sext i1 %44 to i32
  %45 = add i32 %37, %.neg75
  %46 = mul i32 %45, %36
  %47 = sub i32 %.06998, %46
  %48 = getelementptr inbounds i8, i8* %33, i64 8
  %49 = bitcast i8* %48 to i32*
  %50 = load i32, i32* %49, align 4
  %51 = add i32 %50, -1
  %52 = getelementptr inbounds i8, i8* %33, i64 12
  %53 = bitcast i8* %52 to i32*
  %54 = load i32, i32* %53, align 4
  %55 = add i32 %54, -1
  %56 = load float*, float** %25, align 8
  %57 = load i32, i32* %26, align 4
  %58 = load i32, i32* %27, align 4
  %59 = add i32 %47, -1
  %60 = tail call i32 @llvm.smax.i32(i32 %59, i32 0)
  %61 = tail call i32 @llvm.smin.i32(i32 %55, i32 %60)
  %62 = add i32 %45, -1
  %63 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %64 = tail call i32 @llvm.smin.i32(i32 %51, i32 %63)
  %65 = mul i32 %57, %64
  %66 = add i32 %65, %61
  %67 = mul i32 %66, %58
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, float* %56, i64 %68
  %70 = load float, float* %69, align 4
  %71 = add i32 %67, 1
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, float* %56, i64 %72
  %74 = load float, float* %73, align 4
  %75 = fadd reassoc ninf nsz float %74, %70
  %76 = add i32 %67, 2
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, float* %56, i64 %77
  %79 = load float, float* %78, align 4
  %80 = fadd reassoc ninf nsz float %75, %79
  %81 = fmul reassoc ninf nsz float %80, 0x3FD5555560000000
  %82 = fmul reassoc ninf nsz float %81, %81
  %83 = tail call i32 @llvm.smax.i32(i32 %47, i32 0)
  %84 = tail call i32 @llvm.smin.i32(i32 %55, i32 %83)
  %85 = add i32 %65, %84
  %86 = mul i32 %85, %58
  %87 = sext i32 %86 to i64
  %88 = getelementptr float, float* %56, i64 %87
  %89 = load float, float* %88, align 4
  %90 = add i32 %86, 1
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, float* %56, i64 %91
  %93 = load float, float* %92, align 4
  %94 = fadd reassoc ninf nsz float %93, %89
  %95 = add i32 %86, 2
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, float* %56, i64 %96
  %98 = load float, float* %97, align 4
  %99 = fadd reassoc ninf nsz float %94, %98
  %100 = fmul reassoc ninf nsz float %99, 0x3FD5555560000000
  %101 = fadd reassoc ninf nsz float %100, %81
  %102 = fmul reassoc ninf nsz float %100, %100
  %103 = fadd reassoc ninf nsz float %102, %82
  %104 = add i32 %47, 1
  %105 = tail call i32 @llvm.smax.i32(i32 %104, i32 0)
  %106 = tail call i32 @llvm.smin.i32(i32 %55, i32 %105)
  %107 = add i32 %65, %106
  %108 = mul i32 %107, %58
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %56, i64 %109
  %111 = load float, float* %110, align 4
  %112 = add i32 %108, 1
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %56, i64 %113
  %115 = load float, float* %114, align 4
  %116 = fadd reassoc ninf nsz float %115, %111
  %117 = add i32 %108, 2
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, float* %56, i64 %118
  %120 = load float, float* %119, align 4
  %121 = fadd reassoc ninf nsz float %116, %120
  %122 = fmul reassoc ninf nsz float %121, 0x3FD5555560000000
  %123 = fadd reassoc ninf nsz float %122, %101
  %124 = fmul reassoc ninf nsz float %122, %122
  %125 = fadd reassoc ninf nsz float %124, %103
  %126 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %127 = tail call i32 @llvm.smin.i32(i32 %51, i32 %126)
  %128 = mul i32 %57, %127
  %129 = add i32 %128, %61
  %130 = mul i32 %129, %58
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, float* %56, i64 %131
  %133 = load float, float* %132, align 4
  %134 = add i32 %130, 1
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %56, i64 %135
  %137 = load float, float* %136, align 4
  %138 = fadd reassoc ninf nsz float %137, %133
  %139 = add i32 %130, 2
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %56, i64 %140
  %142 = load float, float* %141, align 4
  %143 = fadd reassoc ninf nsz float %138, %142
  %144 = fmul reassoc ninf nsz float %143, 0x3FD5555560000000
  %145 = fadd reassoc ninf nsz float %144, %123
  %146 = fmul reassoc ninf nsz float %144, %144
  %147 = fadd reassoc ninf nsz float %146, %125
  %148 = add i32 %128, %84
  %149 = mul i32 %148, %58
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, float* %56, i64 %150
  %152 = load float, float* %151, align 4
  %153 = add i32 %149, 1
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %56, i64 %154
  %156 = load float, float* %155, align 4
  %157 = fadd reassoc ninf nsz float %156, %152
  %158 = add i32 %149, 2
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %56, i64 %159
  %161 = load float, float* %160, align 4
  %162 = fadd reassoc ninf nsz float %157, %161
  %163 = fmul reassoc ninf nsz float %162, 0x3FD5555560000000
  %164 = fadd reassoc ninf nsz float %163, %145
  %165 = fmul reassoc ninf nsz float %163, %163
  %166 = fadd reassoc ninf nsz float %165, %147
  %167 = add i32 %128, %106
  %168 = mul i32 %167, %58
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, float* %56, i64 %169
  %171 = load float, float* %170, align 4
  %172 = add i32 %168, 1
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, float* %56, i64 %173
  %175 = load float, float* %174, align 4
  %176 = fadd reassoc ninf nsz float %175, %171
  %177 = add i32 %168, 2
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %56, i64 %178
  %180 = load float, float* %179, align 4
  %181 = fadd reassoc ninf nsz float %176, %180
  %182 = fmul reassoc ninf nsz float %181, 0x3FD5555560000000
  %183 = fadd reassoc ninf nsz float %182, %164
  %184 = fmul reassoc ninf nsz float %182, %182
  %185 = fadd reassoc ninf nsz float %184, %166
  %186 = add i32 %45, 1
  %187 = tail call i32 @llvm.smax.i32(i32 %186, i32 0)
  %188 = tail call i32 @llvm.smin.i32(i32 %51, i32 %187)
  %189 = mul i32 %57, %188
  %190 = add i32 %189, %61
  %191 = mul i32 %190, %58
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, float* %56, i64 %192
  %194 = load float, float* %193, align 4
  %195 = add i32 %191, 1
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, float* %56, i64 %196
  %198 = load float, float* %197, align 4
  %199 = fadd reassoc ninf nsz float %198, %194
  %200 = add i32 %191, 2
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, float* %56, i64 %201
  %203 = load float, float* %202, align 4
  %204 = fadd reassoc ninf nsz float %199, %203
  %205 = fmul reassoc ninf nsz float %204, 0x3FD5555560000000
  %206 = fadd reassoc ninf nsz float %205, %183
  %207 = fmul reassoc ninf nsz float %205, %205
  %208 = fadd reassoc ninf nsz float %207, %185
  %209 = add i32 %189, %84
  %210 = mul i32 %209, %58
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %56, i64 %211
  %213 = load float, float* %212, align 4
  %214 = add i32 %210, 1
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, float* %56, i64 %215
  %217 = load float, float* %216, align 4
  %218 = fadd reassoc ninf nsz float %217, %213
  %219 = add i32 %210, 2
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %56, i64 %220
  %222 = load float, float* %221, align 4
  %223 = fadd reassoc ninf nsz float %218, %222
  %224 = fmul reassoc ninf nsz float %223, 0x3FD5555560000000
  %225 = fadd reassoc ninf nsz float %224, %206
  %226 = fmul reassoc ninf nsz float %224, %224
  %227 = fadd reassoc ninf nsz float %226, %208
  %228 = add i32 %189, %106
  %229 = mul i32 %228, %58
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, float* %56, i64 %230
  %232 = load float, float* %231, align 4
  %233 = add i32 %229, 1
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, float* %56, i64 %234
  %236 = load float, float* %235, align 4
  %237 = fadd reassoc ninf nsz float %236, %232
  %238 = add i32 %229, 2
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, float* %56, i64 %239
  %241 = load float, float* %240, align 4
  %242 = fadd reassoc ninf nsz float %237, %241
  %243 = fmul reassoc ninf nsz float %242, 0x3FD5555560000000
  %244 = fadd reassoc ninf nsz float %243, %225
  %245 = fmul reassoc ninf nsz float %243, %243
  %246 = fadd reassoc ninf nsz float %245, %227
  %247 = fmul reassoc ninf nsz float %244, 0x3FBC71C720000000
  %248 = fmul reassoc ninf nsz float %246, 0x3FBC71C720000000
  %249 = fmul reassoc ninf nsz float %247, %247
  %250 = fsub reassoc ninf nsz float %248, %249
  %251 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %250, float 0.000000e+00)
  %252 = fmul reassoc ninf nsz float %251, -3.500000e+02
  %253 = tail call float @expf(float noundef %252) #1
  %254 = fsub reassoc ninf nsz float 1.000000e+00, %253
  %255 = load float*, float** %28, align 8
  %256 = load i32, i32* %29, align 4
  %257 = load i32, i32* %30, align 4
  %258 = mul i32 %256, %45
  %259 = add i32 %258, %47
  %260 = mul i32 %259, %257
  %261 = add i32 %260, 1
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, float* %255, i64 %262
  %264 = load float, float* %263, align 4
  %265 = add i32 %260, 2
  %266 = sext i32 %265 to i64
  %267 = getelementptr float, float* %255, i64 %266
  %268 = load float, float* %267, align 4
  %269 = add i32 %47, -3
  %270 = tail call i32 @llvm.smax.i32(i32 %269, i32 0)
  %271 = tail call i32 @llvm.smin.i32(i32 %55, i32 %270)
  %272 = add i32 %47, -2
  %273 = tail call i32 @llvm.smax.i32(i32 %272, i32 0)
  %274 = tail call i32 @llvm.smin.i32(i32 %55, i32 %273)
  %275 = add i32 %47, 2
  %276 = tail call i32 @llvm.smax.i32(i32 %275, i32 0)
  %277 = tail call i32 @llvm.smin.i32(i32 %55, i32 %276)
  %278 = add i32 %47, 3
  %279 = tail call i32 @llvm.smax.i32(i32 %278, i32 0)
  %280 = tail call i32 @llvm.smin.i32(i32 %55, i32 %279)
  %broadcast.splatinsert116 = insertelement <8 x i32> poison, i32 %45, i64 0
  %broadcast.splat117 = shufflevector <8 x i32> %broadcast.splatinsert116, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert118 = insertelement <8 x i32> poison, i32 %51, i64 0
  %broadcast.splat119 = shufflevector <8 x i32> %broadcast.splatinsert118, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert124 = insertelement <8 x i32> poison, i32 %271, i64 0
  %broadcast.splat125 = shufflevector <8 x i32> %broadcast.splatinsert124, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert131 = insertelement <8 x i32> poison, i32 %274, i64 0
  %broadcast.splat132 = shufflevector <8 x i32> %broadcast.splatinsert131, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert137 = insertelement <8 x i32> poison, i32 %61, i64 0
  %broadcast.splat138 = shufflevector <8 x i32> %broadcast.splatinsert137, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert143 = insertelement <8 x i32> poison, i32 %84, i64 0
  %broadcast.splat144 = shufflevector <8 x i32> %broadcast.splatinsert143, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert149 = insertelement <8 x i32> poison, i32 %106, i64 0
  %broadcast.splat150 = shufflevector <8 x i32> %broadcast.splatinsert149, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert155 = insertelement <8 x i32> poison, i32 %277, i64 0
  %broadcast.splat156 = shufflevector <8 x i32> %broadcast.splatinsert155, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert161 = insertelement <8 x i32> poison, i32 %280, i64 0
  %broadcast.splat162 = shufflevector <8 x i32> %broadcast.splatinsert161, <8 x i32> poison, <8 x i32> zeroinitializer
  %281 = add <8 x i32> %broadcast.splat117, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %282 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %281, <8 x i32> zeroinitializer)
  %283 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat119, <8 x i32> %282)
  %284 = add i32 %47, -6
  %285 = add i32 %37, -7
  %286 = add i32 %285, %.neg75
  br label %for_loop_body9

after_for.loopexit:                               ; preds = %after_if47
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body9:                                   ; preds = %for_loop_inc10, %for_loop_body
  %lsr.iv167 = phi i32 [ %286, %for_loop_body ], [ %lsr.iv.next168, %for_loop_inc10 ]
  %.04797 = phi i32 [ -7, %for_loop_body ], [ %289, %for_loop_inc10 ]
  %.14996 = phi float [ 0.000000e+00, %for_loop_body ], [ %.048, %for_loop_inc10 ]
  %.15295 = phi float [ 0.000000e+00, %for_loop_body ], [ %.051, %for_loop_inc10 ]
  %.15694 = phi float [ 0.000000e+00, %for_loop_body ], [ %.055, %for_loop_inc10 ]
  %.16093 = phi float [ 0.000000e+00, %for_loop_body ], [ %.059, %for_loop_inc10 ]
  %287 = add i32 %.04797, %45
  %288 = icmp slt i32 %287, 0
  br i1 %288, label %for_loop_inc10, label %false_block

for_loop_inc10.loopexit:                          ; preds = %for_loop_inc17
  br label %for_loop_inc10

for_loop_inc10:                                   ; preds = %false_block, %for_loop_inc10.loopexit, %for_loop_body9
  %.059 = phi float [ %.16093, %false_block ], [ %.16093, %for_loop_body9 ], [ %.261, %for_loop_inc10.loopexit ]
  %.055 = phi float [ %.15694, %false_block ], [ %.15694, %for_loop_body9 ], [ %.257, %for_loop_inc10.loopexit ]
  %.051 = phi float [ %.15295, %false_block ], [ %.15295, %for_loop_body9 ], [ %.253, %for_loop_inc10.loopexit ]
  %.048 = phi float [ %.14996, %false_block ], [ %.14996, %for_loop_body9 ], [ %.250, %for_loop_inc10.loopexit ]
  %289 = add nsw i32 %.04797, 1
  %lsr.iv.next168 = add i32 %lsr.iv167, 1
  %exitcond102.not = icmp eq i32 %289, 8
  br i1 %exitcond102.not, label %after_for11, label %for_loop_body9

after_for11:                                      ; preds = %for_loop_inc10
  %290 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %254, float 0x3FE6666660000000)
  %291 = fcmp reassoc ninf nsz ogt float %.059, 0x3D71979980000000
  br i1 %291, label %true_block45, label %false_block46

false_block:                                      ; preds = %for_loop_body9
  %292 = load i32, i32* %49, align 4
  %.not76 = icmp slt i32 %287, %292
  br i1 %.not76, label %after_if15, label %for_loop_inc10

after_if15:                                       ; preds = %false_block
  %.not = icmp ne i32 %.04797, 0
  %broadcast.splatinsert120 = insertelement <8 x i32> poison, i32 %287, i64 0
  %broadcast.splat121 = shufflevector <8 x i32> %broadcast.splatinsert120, <8 x i32> poison, <8 x i32> zeroinitializer
  %293 = add <8 x i32> %broadcast.splat121, <i32 -3, i32 -2, i32 -1, i32 0, i32 1, i32 2, i32 3, i32 4>
  %294 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %293, <8 x i32> zeroinitializer)
  %295 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat119, <8 x i32> %294)
  br label %for_loop_body16

for_loop_body16:                                  ; preds = %for_loop_inc17, %after_if15
  %lsr.iv = phi i32 [ 0, %after_if15 ], [ %lsr.iv.next, %for_loop_inc17 ]
  %.391 = phi float [ %.14996, %after_if15 ], [ %.250, %for_loop_inc17 ]
  %.35490 = phi float [ %.15295, %after_if15 ], [ %.253, %for_loop_inc17 ]
  %.35889 = phi float [ %.15694, %after_if15 ], [ %.257, %for_loop_inc17 ]
  %.36288 = phi float [ %.16093, %after_if15 ], [ %.261, %for_loop_inc17 ]
  %296 = add i32 %284, %lsr.iv
  %297 = add i32 %296, -1
  %298 = icmp slt i32 %297, 0
  br i1 %298, label %for_loop_inc17, label %false_block21

for_loop_inc17:                                   ; preds = %true_block41, %after_if32, %false_block21, %for_loop_body16
  %.261 = phi float [ %.36288, %false_block21 ], [ %435, %true_block41 ], [ %.36288, %after_if32 ], [ %.36288, %for_loop_body16 ]
  %.257 = phi float [ %.35889, %false_block21 ], [ %447, %true_block41 ], [ %.35889, %after_if32 ], [ %.35889, %for_loop_body16 ]
  %.253 = phi float [ %.35490, %false_block21 ], [ %453, %true_block41 ], [ %.35490, %after_if32 ], [ %.35490, %for_loop_body16 ]
  %.250 = phi float [ %.391, %false_block21 ], [ %459, %true_block41 ], [ %.391, %after_if32 ], [ %.391, %for_loop_body16 ]
  %lsr.iv.next = add nuw nsw i32 %lsr.iv, 1
  %exitcond101.not = icmp eq i32 %lsr.iv.next, 15
  br i1 %exitcond101.not, label %for_loop_inc10.loopexit, label %for_loop_body16

false_block21:                                    ; preds = %for_loop_body16
  %299 = load i32, i32* %53, align 4
  %.not77 = icmp slt i32 %297, %299
  br i1 %.not77, label %after_if25, label %for_loop_inc17

after_if25:                                       ; preds = %false_block21
  %300 = icmp ne i32 %lsr.iv, 7
  %spec.select = select i1 %.not, i1 true, i1 %300
  br i1 %spec.select, label %for_loop_test36.preheader, label %after_if32

for_loop_test36.preheader:                        ; preds = %after_if25
  %301 = load float*, float** %28, align 8
  %302 = add i32 %296, 2
  %303 = tail call i32 @llvm.smax.i32(i32 %302, i32 0)
  %304 = tail call i32 @llvm.smin.i32(i32 %55, i32 %303)
  %305 = add i32 %296, 1
  %306 = tail call i32 @llvm.smax.i32(i32 %305, i32 0)
  %307 = tail call i32 @llvm.smin.i32(i32 %55, i32 %306)
  %308 = tail call i32 @llvm.smax.i32(i32 %296, i32 0)
  %309 = tail call i32 @llvm.smin.i32(i32 %55, i32 %308)
  %310 = tail call i32 @llvm.smax.i32(i32 %297, i32 0)
  %311 = tail call i32 @llvm.smin.i32(i32 %55, i32 %310)
  %312 = add i32 %296, -2
  %313 = tail call i32 @llvm.smax.i32(i32 %312, i32 0)
  %314 = tail call i32 @llvm.smin.i32(i32 %55, i32 %313)
  %315 = add i32 %296, -3
  %316 = tail call i32 @llvm.smax.i32(i32 %315, i32 0)
  %317 = tail call i32 @llvm.smin.i32(i32 %55, i32 %316)
  %318 = call i32 @llvm.smax.i32(i32 %297, i32 3)
  %319 = add nsw i32 %318, -3
  %320 = tail call i32 @llvm.smin.i32(i32 %55, i32 %319)
  %321 = load i32, i32* %30, align 4
  %322 = load i32, i32* %29, align 4
  %broadcast.splatinsert122 = insertelement <8 x i32> poison, i32 %322, i64 0
  %broadcast.splat123 = shufflevector <8 x i32> %broadcast.splatinsert122, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert126 = insertelement <8 x i32> poison, i32 %321, i64 0
  %broadcast.splat127 = shufflevector <8 x i32> %broadcast.splatinsert126, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert128 = insertelement <8 x i32> poison, i32 %320, i64 0
  %broadcast.splat129 = shufflevector <8 x i32> %broadcast.splatinsert128, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert134 = insertelement <8 x i32> poison, i32 %317, i64 0
  %broadcast.splat135 = shufflevector <8 x i32> %broadcast.splatinsert134, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert140 = insertelement <8 x i32> poison, i32 %314, i64 0
  %broadcast.splat141 = shufflevector <8 x i32> %broadcast.splatinsert140, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert146 = insertelement <8 x i32> poison, i32 %311, i64 0
  %broadcast.splat147 = shufflevector <8 x i32> %broadcast.splatinsert146, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert152 = insertelement <8 x i32> poison, i32 %309, i64 0
  %broadcast.splat153 = shufflevector <8 x i32> %broadcast.splatinsert152, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert158 = insertelement <8 x i32> poison, i32 %307, i64 0
  %broadcast.splat159 = shufflevector <8 x i32> %broadcast.splatinsert158, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert164 = insertelement <8 x i32> poison, i32 %304, i64 0
  %broadcast.splat165 = shufflevector <8 x i32> %broadcast.splatinsert164, <8 x i32> poison, <8 x i32> zeroinitializer
  %323 = mul <8 x i32> %broadcast.splat123, %283
  %324 = mul <8 x i32> %broadcast.splat123, %295
  %325 = add <8 x i32> %323, %broadcast.splat125
  %326 = mul <8 x i32> %325, %broadcast.splat127
  %327 = sext <8 x i32> %326 to <8 x i64>
  %328 = getelementptr float, float* %301, <8 x i64> %327
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %328, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %329 = add <8 x i32> %324, %broadcast.splat129
  %330 = mul <8 x i32> %329, %broadcast.splat127
  %331 = sext <8 x i32> %330 to <8 x i64>
  %332 = getelementptr float, float* %301, <8 x i64> %331
  %wide.masked.gather130 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %332, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %333 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather130
  %334 = fmul reassoc ninf nsz <8 x float> %333, %333
  %335 = add <8 x i32> %323, %broadcast.splat132
  %336 = mul <8 x i32> %335, %broadcast.splat127
  %337 = sext <8 x i32> %336 to <8 x i64>
  %338 = getelementptr float, float* %301, <8 x i64> %337
  %wide.masked.gather133 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %338, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %339 = add <8 x i32> %324, %broadcast.splat135
  %340 = mul <8 x i32> %339, %broadcast.splat127
  %341 = sext <8 x i32> %340 to <8 x i64>
  %342 = getelementptr float, float* %301, <8 x i64> %341
  %wide.masked.gather136 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %342, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %343 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather133, %wide.masked.gather136
  %344 = fmul reassoc ninf nsz <8 x float> %343, %343
  %345 = fadd reassoc ninf nsz <8 x float> %344, %334
  %346 = add <8 x i32> %323, %broadcast.splat138
  %347 = mul <8 x i32> %346, %broadcast.splat127
  %348 = sext <8 x i32> %347 to <8 x i64>
  %349 = getelementptr float, float* %301, <8 x i64> %348
  %wide.masked.gather139 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %349, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %350 = add <8 x i32> %324, %broadcast.splat141
  %351 = mul <8 x i32> %350, %broadcast.splat127
  %352 = sext <8 x i32> %351 to <8 x i64>
  %353 = getelementptr float, float* %301, <8 x i64> %352
  %wide.masked.gather142 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %353, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %354 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather139, %wide.masked.gather142
  %355 = fmul reassoc ninf nsz <8 x float> %354, %354
  %356 = fadd reassoc ninf nsz <8 x float> %355, %345
  %357 = add <8 x i32> %323, %broadcast.splat144
  %358 = mul <8 x i32> %357, %broadcast.splat127
  %359 = sext <8 x i32> %358 to <8 x i64>
  %360 = getelementptr float, float* %301, <8 x i64> %359
  %wide.masked.gather145 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %360, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %361 = add <8 x i32> %324, %broadcast.splat147
  %362 = mul <8 x i32> %361, %broadcast.splat127
  %363 = sext <8 x i32> %362 to <8 x i64>
  %364 = getelementptr float, float* %301, <8 x i64> %363
  %wide.masked.gather148 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %364, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %365 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather145, %wide.masked.gather148
  %366 = fmul reassoc ninf nsz <8 x float> %365, %365
  %367 = fadd reassoc ninf nsz <8 x float> %366, %356
  %368 = add <8 x i32> %323, %broadcast.splat150
  %369 = mul <8 x i32> %368, %broadcast.splat127
  %370 = sext <8 x i32> %369 to <8 x i64>
  %371 = getelementptr float, float* %301, <8 x i64> %370
  %wide.masked.gather151 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %371, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %372 = add <8 x i32> %324, %broadcast.splat153
  %373 = mul <8 x i32> %372, %broadcast.splat127
  %374 = sext <8 x i32> %373 to <8 x i64>
  %375 = getelementptr float, float* %301, <8 x i64> %374
  %wide.masked.gather154 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %375, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %376 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather151, %wide.masked.gather154
  %377 = fmul reassoc ninf nsz <8 x float> %376, %376
  %378 = fadd reassoc ninf nsz <8 x float> %377, %367
  %379 = add <8 x i32> %323, %broadcast.splat156
  %380 = mul <8 x i32> %379, %broadcast.splat127
  %381 = sext <8 x i32> %380 to <8 x i64>
  %382 = getelementptr float, float* %301, <8 x i64> %381
  %wide.masked.gather157 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %382, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %383 = add <8 x i32> %324, %broadcast.splat159
  %384 = mul <8 x i32> %383, %broadcast.splat127
  %385 = sext <8 x i32> %384 to <8 x i64>
  %386 = getelementptr float, float* %301, <8 x i64> %385
  %wide.masked.gather160 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %386, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %387 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather157, %wide.masked.gather160
  %388 = fmul reassoc ninf nsz <8 x float> %387, %387
  %389 = fadd reassoc ninf nsz <8 x float> %388, %378
  %390 = add <8 x i32> %323, %broadcast.splat162
  %391 = mul <8 x i32> %390, %broadcast.splat127
  %392 = sext <8 x i32> %391 to <8 x i64>
  %393 = getelementptr float, float* %301, <8 x i64> %392
  %wide.masked.gather163 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %393, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %394 = add <8 x i32> %324, %broadcast.splat165
  %395 = mul <8 x i32> %394, %broadcast.splat127
  %396 = sext <8 x i32> %395 to <8 x i64>
  %397 = getelementptr float, float* %301, <8 x i64> %396
  %wide.masked.gather166 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %397, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 false>, <8 x float> undef)
  %398 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather163, %wide.masked.gather166
  %399 = fmul reassoc ninf nsz <8 x float> %398, %398
  %400 = fadd reassoc ninf nsz <8 x float> %399, %389
  %401 = insertelement <8 x float> %400, float 0.000000e+00, i64 7
  %402 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %401)
  %403 = fmul reassoc ninf nsz float %402, 0x3F94E5E0A0000000
  %404 = mul i32 %lsr.iv167, %322
  %405 = add i32 %296, %404
  %406 = add i32 %405, -1
  %407 = mul i32 %406, %321
  %408 = add i32 %407, 1
  %409 = sext i32 %408 to i64
  %410 = getelementptr float, float* %301, i64 %409
  %411 = load float, float* %410, align 4
  %412 = add i32 %407, 2
  %413 = sext i32 %412 to i64
  %414 = getelementptr float, float* %301, i64 %413
  %415 = load float, float* %414, align 4
  %416 = fsub reassoc ninf nsz float %264, %411
  %417 = fsub reassoc ninf nsz float %268, %415
  %418 = fmul reassoc ninf nsz float %416, %416
  %419 = fmul reassoc ninf nsz float %417, %417
  %420 = fadd reassoc ninf nsz float %419, %418
  %421 = fmul reassoc ninf nsz float %420, 2.500000e-01
  %422 = fadd reassoc ninf nsz float %421, %403
  br label %after_if32

after_if32:                                       ; preds = %for_loop_test36.preheader, %after_if25
  %.043 = phi float [ %422, %for_loop_test36.preheader ], [ 0.000000e+00, %after_if25 ]
  %423 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %424 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %423, i64 0, i32 14
  %425 = load i8*, i8** %424, align 8
  %426 = getelementptr inbounds i8, i8* %425, i64 16
  %427 = bitcast i8* %426 to float*
  %428 = load float, float* %427, align 4
  %429 = fcmp reassoc ninf nsz ugt float %.043, %428
  br i1 %429, label %for_loop_inc17, label %true_block41

true_block41:                                     ; preds = %after_if32
  %neg44 = fneg reassoc ninf nsz float %.043
  %430 = getelementptr inbounds i8, i8* %425, i64 20
  %431 = bitcast i8* %430 to float*
  %432 = load float, float* %431, align 4
  %433 = fmul reassoc ninf nsz float %432, %neg44
  %434 = tail call float @expf(float noundef %433) #1
  %435 = fadd reassoc ninf nsz float %434, %.36288
  %436 = load float*, float** %25, align 8
  %437 = load i32, i32* %26, align 4
  %438 = load i32, i32* %27, align 4
  %439 = mul i32 %lsr.iv167, %437
  %440 = add i32 %296, %439
  %441 = add i32 %440, -1
  %442 = mul i32 %441, %438
  %443 = sext i32 %442 to i64
  %444 = getelementptr float, float* %436, i64 %443
  %445 = load float, float* %444, align 4
  %446 = fmul reassoc ninf nsz float %445, %434
  %447 = fadd reassoc ninf nsz float %446, %.35889
  %448 = add i32 %442, 1
  %449 = sext i32 %448 to i64
  %450 = getelementptr float, float* %436, i64 %449
  %451 = load float, float* %450, align 4
  %452 = fmul reassoc ninf nsz float %451, %434
  %453 = fadd reassoc ninf nsz float %452, %.35490
  %454 = add i32 %442, 2
  %455 = sext i32 %454 to i64
  %456 = getelementptr float, float* %436, i64 %455
  %457 = load float, float* %456, align 4
  %458 = fmul reassoc ninf nsz float %457, %434
  %459 = fadd reassoc ninf nsz float %458, %.391
  br label %for_loop_inc17

true_block45:                                     ; preds = %after_for11
  %460 = fmul reassoc ninf nsz float %290, %23
  %461 = fdiv reassoc ninf nsz float 1.000000e+00, %.059
  %462 = fmul reassoc ninf nsz float %.055, %461
  %463 = fmul reassoc ninf nsz float %.051, %461
  %464 = fmul reassoc ninf nsz float %.048, %461
  %465 = load float*, float** %25, align 8
  %466 = load i32, i32* %26, align 4
  %467 = load i32, i32* %27, align 4
  %468 = mul i32 %466, %45
  %469 = add i32 %468, %47
  %470 = mul i32 %469, %467
  %471 = sext i32 %470 to i64
  %472 = getelementptr float, float* %465, i64 %471
  %473 = load float, float* %472, align 4
  %474 = fsub reassoc ninf nsz float %473, %462
  %475 = add i32 %470, 1
  %476 = sext i32 %475 to i64
  %477 = getelementptr float, float* %465, i64 %476
  %478 = load float, float* %477, align 4
  %479 = fsub reassoc ninf nsz float %478, %463
  %480 = add i32 %470, 2
  %481 = sext i32 %480 to i64
  %482 = getelementptr float, float* %465, i64 %481
  %483 = load float, float* %482, align 4
  %484 = fsub reassoc ninf nsz float %483, %464
  %485 = tail call float @llvm.fabs.f32(float %474)
  %486 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %487 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %486, i64 0, i32 14
  %488 = load i8*, i8** %487, align 8
  %489 = getelementptr inbounds i8, i8* %488, i64 24
  %490 = bitcast i8* %489 to float*
  %491 = load float, float* %490, align 4
  %492 = fsub reassoc ninf nsz float %485, %491
  %493 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %492, float 0.000000e+00)
  %494 = fcmp reassoc ninf nsz oge float %474, 0.000000e+00
  %495 = uitofp i1 %494 to float
  %496 = fcmp reassoc ninf nsz ole float %474, 0.000000e+00
  %497 = uitofp i1 %496 to float
  %498 = fsub reassoc ninf nsz float %495, %497
  %499 = tail call float @llvm.fabs.f32(float %479)
  %500 = fsub reassoc ninf nsz float %499, %491
  %501 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %500, float 0.000000e+00)
  %502 = fcmp reassoc ninf nsz oge float %479, 0.000000e+00
  %503 = uitofp i1 %502 to float
  %504 = fcmp reassoc ninf nsz ole float %479, 0.000000e+00
  %505 = uitofp i1 %504 to float
  %506 = fsub reassoc ninf nsz float %503, %505
  %507 = tail call float @llvm.fabs.f32(float %484)
  %508 = fsub reassoc ninf nsz float %507, %491
  %509 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %508, float 0.000000e+00)
  %510 = fcmp reassoc ninf nsz oge float %484, 0.000000e+00
  %511 = uitofp i1 %510 to float
  %512 = fcmp reassoc ninf nsz ole float %484, 0.000000e+00
  %513 = uitofp i1 %512 to float
  %514 = fsub reassoc ninf nsz float %511, %513
  %515 = fmul reassoc ninf nsz float %498, %460
  %516 = fmul reassoc ninf nsz float %515, %493
  %517 = fadd reassoc ninf nsz float %516, %462
  %518 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %519 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %518, i64 0, i32 2, i32 1
  %520 = load float*, float** %519, align 8
  %521 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %518, i64 0, i32 2, i32 0, i32 1
  %522 = load i32, i32* %521, align 4
  %523 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %518, i64 0, i32 2, i32 0, i32 2
  %524 = load i32, i32* %523, align 4
  %525 = mul i32 %522, %45
  %526 = add i32 %525, %47
  %527 = mul i32 %526, %524
  %528 = sext i32 %527 to i64
  %529 = getelementptr float, float* %520, i64 %528
  store float %517, float* %529, align 4
  %530 = fmul reassoc ninf nsz float %506, %460
  %531 = fmul reassoc ninf nsz float %530, %501
  %532 = fadd reassoc ninf nsz float %531, %463
  %533 = load float*, float** %519, align 8
  %534 = load i32, i32* %521, align 4
  %535 = load i32, i32* %523, align 4
  %536 = mul i32 %534, %45
  %537 = add i32 %536, %47
  %538 = mul i32 %537, %535
  %539 = add i32 %538, 1
  %540 = sext i32 %539 to i64
  %541 = getelementptr float, float* %533, i64 %540
  store float %532, float* %541, align 4
  %542 = fmul reassoc ninf nsz float %514, %460
  %543 = fmul reassoc ninf nsz float %542, %509
  %544 = fadd reassoc ninf nsz float %543, %464
  br label %after_if47

false_block46:                                    ; preds = %after_for11
  %545 = load float*, float** %25, align 8
  %546 = load i32, i32* %26, align 4
  %547 = load i32, i32* %27, align 4
  %548 = mul i32 %546, %45
  %549 = add i32 %548, %47
  %550 = mul i32 %549, %547
  %551 = sext i32 %550 to i64
  %552 = getelementptr float, float* %545, i64 %551
  %553 = load float, float* %552, align 4
  %554 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }** %20, align 8
  %555 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %554, i64 0, i32 2, i32 1
  %556 = load float*, float** %555, align 8
  %557 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %554, i64 0, i32 2, i32 0, i32 1
  %558 = load i32, i32* %557, align 4
  %559 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float, float, float }* %554, i64 0, i32 2, i32 0, i32 2
  %560 = load i32, i32* %559, align 4
  %561 = mul i32 %558, %45
  %562 = add i32 %561, %47
  %563 = mul i32 %562, %560
  %564 = sext i32 %563 to i64
  %565 = getelementptr float, float* %556, i64 %564
  store float %553, float* %565, align 4
  %566 = load float*, float** %25, align 8
  %567 = load i32, i32* %26, align 4
  %568 = load i32, i32* %27, align 4
  %569 = mul i32 %567, %45
  %570 = add i32 %569, %47
  %571 = mul i32 %570, %568
  %572 = add i32 %571, 1
  %573 = sext i32 %572 to i64
  %574 = getelementptr float, float* %566, i64 %573
  %575 = load float, float* %574, align 4
  %576 = load float*, float** %555, align 8
  %577 = load i32, i32* %557, align 4
  %578 = load i32, i32* %559, align 4
  %579 = mul i32 %577, %45
  %580 = add i32 %579, %47
  %581 = mul i32 %580, %578
  %582 = add i32 %581, 1
  %583 = sext i32 %582 to i64
  %584 = getelementptr float, float* %576, i64 %583
  store float %575, float* %584, align 4
  %585 = load float*, float** %25, align 8
  %586 = load i32, i32* %26, align 4
  %587 = load i32, i32* %27, align 4
  %588 = mul i32 %586, %45
  %589 = add i32 %588, %47
  %590 = mul i32 %589, %587
  %591 = add i32 %590, 2
  %592 = sext i32 %591 to i64
  %593 = getelementptr float, float* %585, i64 %592
  %594 = load float, float* %593, align 4
  br label %after_if47

after_if47:                                       ; preds = %false_block46, %true_block45
  %.sink115 = phi float** [ %555, %false_block46 ], [ %519, %true_block45 ]
  %.sink114 = phi i32* [ %557, %false_block46 ], [ %521, %true_block45 ]
  %.sink113 = phi i32* [ %559, %false_block46 ], [ %523, %true_block45 ]
  %.sink = phi float [ %594, %false_block46 ], [ %544, %true_block45 ]
  %595 = load float*, float** %.sink115, align 8
  %596 = load i32, i32* %.sink114, align 4
  %597 = load i32, i32* %.sink113, align 4
  %598 = mul i32 %596, %45
  %599 = add i32 %598, %47
  %600 = mul i32 %599, %597
  %601 = add i32 %600, 2
  %602 = sext i32 %601 to i64
  %603 = getelementptr float, float* %595, i64 %602
  store float %.sink, float* %603, align 4
  %604 = add nsw i32 %.06998, 1
  %exitcond103.not = icmp eq i32 %604, %19
  br i1 %exitcond103.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @expf(float noundef) local_unnamed_addr #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #5 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #10

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #9 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #10 = { nocallback nofree nosync nounwind readnone willreturn }

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
