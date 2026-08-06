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
define void @_jacobi_step_c470_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 4
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 5
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
define void @_jacobi_step_c470_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %.049 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %66, %for_loop_inc ]
  %31 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.049, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.049
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.049, 0
  %42 = icmp ne i32 %.049, %38
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg5 = sext i1 %44 to i32
  %45 = add i32 %37, %.neg5
  %46 = mul i32 %45, %36
  %47 = mul i32 %36, -1
  %48 = mul i32 %47, %45
  %49 = add i32 %.049, %48
  %50 = load float*, float** %23, align 8
  %51 = load i32, i32* %24, align 4
  %52 = sub i32 %51, %36
  %53 = mul i32 %52, %45
  %54 = add i32 %.049, %53
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, float* %50, i64 %55
  %57 = load float, float* %56, align 4
  %58 = fcmp reassoc ninf nsz olt float %57, 5.000000e-01
  br i1 %58, label %true_block, label %after_if

for_loop_inc:                                     ; preds = %after_if27, %true_block25, %true_block
  %.sink = phi float [ %191, %after_if27 ], [ %153, %true_block25 ], [ %74, %true_block ]
  %59 = load float*, float** %29, align 8
  %60 = load i32, i32* %30, align 4
  %61 = sub i32 %60, %36
  %62 = mul i32 %61, %45
  %63 = add i32 %.049, %62
  %64 = sext i32 %63 to i64
  %65 = getelementptr float, float* %59, i64 %64
  store float %.sink, float* %65, align 4
  %66 = add nsw i32 %.049, 1
  %exitcond.not = icmp eq i32 %19, %66
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %67 = load float*, float** %25, align 8
  %68 = load i32, i32* %26, align 4
  %69 = sub i32 %68, %36
  %70 = mul i32 %69, %45
  %71 = add i32 %.049, %70
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, float* %67, i64 %72
  %74 = load float, float* %73, align 4
  br label %for_loop_inc

after_if:                                         ; preds = %for_loop_body
  %75 = add i32 %45, -1
  %76 = getelementptr inbounds i8, i8* %33, i64 8
  %77 = bitcast i8* %76 to i32*
  %78 = load i32, i32* %77, align 4
  %79 = add i32 %78, -1
  %80 = tail call i32 @llvm.smax.i32(i32 %75, i32 0)
  %81 = tail call i32 @llvm.smin.i32(i32 %79, i32 %80)
  %82 = insertelement <2 x i32> poison, i32 %49, i64 0
  %83 = shufflevector <2 x i32> %82, <2 x i32> poison, <2 x i32> zeroinitializer
  %84 = add <2 x i32> %83, <i32 -1, i32 1>
  %85 = getelementptr inbounds i8, i8* %33, i64 12
  %86 = bitcast i8* %85 to i32*
  %87 = load i32, i32* %86, align 4
  %88 = add i32 %87, -1
  %89 = mul i32 %81, %51
  %90 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %91 = tail call i32 @llvm.smin.i32(i32 %88, i32 %90)
  %92 = add i32 %89, %91
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, float* %50, i64 %93
  %95 = load float, float* %94, align 4
  %96 = fcmp reassoc ninf nsz olt float %95, 5.000000e-01
  %97 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %84, <2 x i32> zeroinitializer)
  %98 = insertelement <2 x i32> poison, i32 %88, i64 0
  %99 = shufflevector <2 x i32> %98, <2 x i32> poison, <2 x i32> zeroinitializer
  %100 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %99, <2 x i32> %97)
  %101 = extractelement <2 x i32> %100, i64 0
  %102 = add i32 %89, %101
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %50, i64 %103
  %105 = load float, float* %104, align 4
  %106 = fcmp reassoc ninf nsz olt float %105, 5.000000e-01
  %.1 = select i1 %96, i1 true, i1 %106
  %107 = extractelement <2 x i32> %100, i64 1
  %108 = add i32 %89, %107
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %50, i64 %109
  %111 = load float, float* %110, align 4
  %112 = fcmp reassoc ninf nsz olt float %111, 5.000000e-01
  br i1 %112, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if
  %.2 = phi i1 [ true, %true_block7 ], [ %.1, %after_if ]
  %113 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %114 = tail call i32 @llvm.smin.i32(i32 %79, i32 %113)
  %115 = mul i32 %114, %51
  %116 = add i32 %115, %101
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, float* %50, i64 %117
  %119 = load float, float* %118, align 4
  %120 = fcmp reassoc ninf nsz olt float %119, 5.000000e-01
  %.3 = select i1 %120, i1 true, i1 %.2
  %121 = add i32 %115, %107
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, float* %50, i64 %122
  %124 = load float, float* %123, align 4
  %125 = fcmp reassoc ninf nsz olt float %124, 5.000000e-01
  br i1 %125, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if9
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if9
  %.4 = phi i1 [ true, %true_block13 ], [ %.3, %after_if9 ]
  %126 = add i32 %45, 1
  %127 = tail call i32 @llvm.smax.i32(i32 %126, i32 0)
  %128 = tail call i32 @llvm.smin.i32(i32 %79, i32 %127)
  %129 = mul i32 %128, %51
  %130 = add i32 %129, %91
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, float* %50, i64 %131
  %133 = load float, float* %132, align 4
  %134 = fcmp reassoc ninf nsz olt float %133, 5.000000e-01
  br i1 %134, label %true_block25, label %after_if21

after_if21:                                       ; preds = %after_if15
  %135 = add i32 %129, %101
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, float* %50, i64 %136
  %138 = load float, float* %137, align 4
  %139 = fcmp reassoc ninf nsz olt float %138, 5.000000e-01
  %140 = add i32 %129, %107
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %50, i64 %141
  %143 = load float, float* %142, align 4
  %144 = fcmp reassoc ninf nsz olt float %143, 5.000000e-01
  %145 = select i1 %144, i1 true, i1 %139
  %.7 = select i1 %145, i1 true, i1 %.4
  br i1 %.7, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if21, %after_if15
  %146 = load float*, float** %25, align 8
  %147 = load i32, i32* %26, align 4
  %148 = sub i32 %147, %36
  %149 = mul i32 %148, %45
  %150 = add i32 %.049, %149
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %146, i64 %151
  %153 = load float, float* %152, align 4
  br label %for_loop_inc

after_if27:                                       ; preds = %after_if21
  %154 = load float*, float** %25, align 8
  %155 = load i32, i32* %26, align 4
  %156 = mul i32 %155, %81
  %157 = sub i32 %156, %46
  %158 = add i32 %.049, %157
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %154, i64 %159
  %161 = load float, float* %160, align 4
  %162 = mul i32 %155, %128
  %163 = sub i32 %162, %46
  %164 = add i32 %.049, %163
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, float* %154, i64 %165
  %167 = load float, float* %166, align 4
  %168 = mul i32 %155, %45
  %169 = insertelement <2 x i32> poison, i32 %168, i64 0
  %170 = shufflevector <2 x i32> %169, <2 x i32> poison, <2 x i32> zeroinitializer
  %171 = add <2 x i32> %170, %100
  %172 = sext <2 x i32> %171 to <2 x i64>
  %173 = extractelement <2 x i64> %172, i64 0
  %174 = getelementptr float, float* %154, i64 %173
  %175 = load float, float* %174, align 4
  %176 = extractelement <2 x i64> %172, i64 1
  %177 = getelementptr float, float* %154, i64 %176
  %178 = load float, float* %177, align 4
  %179 = fadd reassoc ninf nsz float %167, %161
  %180 = fadd reassoc ninf nsz float %179, %175
  %181 = fadd reassoc ninf nsz float %180, %178
  %182 = load float*, float** %27, align 8
  %183 = load i32, i32* %28, align 4
  %184 = sub i32 %183, %36
  %185 = mul i32 %184, %45
  %186 = add i32 %.049, %185
  %187 = sext i32 %186 to i64
  %188 = getelementptr float, float* %182, i64 %187
  %189 = load float, float* %188, align 4
  %190 = fsub reassoc ninf nsz float %181, %189
  %191 = fmul reassoc ninf nsz float %190, 2.500000e-01
  br label %for_loop_inc
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
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
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
