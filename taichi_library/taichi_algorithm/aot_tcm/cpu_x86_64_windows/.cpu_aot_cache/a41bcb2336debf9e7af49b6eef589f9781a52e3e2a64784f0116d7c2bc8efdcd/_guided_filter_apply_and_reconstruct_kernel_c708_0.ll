; ModuleID = '<string>'
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
define void @_guided_filter_apply_and_reconstruct_kernel_c88_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 4
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 5
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
define void @_guided_filter_apply_and_reconstruct_kernel_c88_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
define internal void @function_body(%struct.RuntimeContext.24* readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3, i32 0, i32 1
  %27 = sub i32 0, %19
  %28 = add i32 %17, 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if297, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %28, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if297 ]
  %.0278561 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %838, %after_if297 ]
  %29 = add i32 %lsr.iv, -2
  %30 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %29, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %29
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %lsr.iv, 2
  %41 = icmp ne i32 %29, %37
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg379 = sext i1 %43 to i32
  %44 = add i32 %36, %.neg379
  %45 = mul i32 %44, %35
  %46 = sub i32 %.0278561, %45
  %47 = mul i32 %35, -1
  %48 = mul i32 %47, %44
  %49 = add i32 %lsr.iv, %48
  %50 = add i32 %49, -2
  %51 = add i32 %44, -2
  %52 = add i32 %49, -4
  %53 = icmp sgt i32 %51, -1
  br i1 %53, label %true_block, label %after_if45

after_for.loopexit:                               ; preds = %after_if297
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %54 = getelementptr inbounds i8, i8* %32, i64 8
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = icmp slt i32 %51, %56
  %58 = icmp sgt i32 %52, -1
  %or.cond = select i1 %57, i1 %58, i1 false
  br i1 %or.cond, label %true_block4, label %true_block10

true_block4:                                      ; preds = %true_block
  %59 = getelementptr inbounds i8, i8* %32, i64 12
  %60 = bitcast i8* %59 to i32*
  %61 = load i32, i32* %60, align 4
  %62 = icmp slt i32 %52, %61
  br i1 %62, label %true_block7, label %true_block10

true_block7:                                      ; preds = %true_block4
  %63 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %64 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %63, i64 0, i32 1, i32 1
  %65 = load float*, float** %64, align 8
  %66 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %63, i64 0, i32 1, i32 0, i32 1
  %67 = load i32, i32* %66, align 4
  %68 = mul i32 %67, %51
  %69 = sub i32 %68, %45
  %70 = add i32 %lsr.iv, %69
  %71 = add i32 %70, -4
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, float* %65, i64 %72
  %74 = load float, float* %73, align 4
  %75 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %63, i64 0, i32 2, i32 1
  %76 = load float*, float** %75, align 8
  %77 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %63, i64 0, i32 2, i32 0, i32 1
  %78 = load i32, i32* %77, align 4
  %79 = mul i32 %78, %51
  %80 = sub i32 %79, %45
  %81 = add i32 %lsr.iv, %80
  %82 = add i32 %81, -4
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, float* %76, i64 %83
  %85 = load float, float* %84, align 4
  br label %true_block10

true_block10:                                     ; preds = %true_block7, %true_block4, %true_block
  %.0253.ph = phi float [ 0.000000e+00, %true_block ], [ 0.000000e+00, %true_block4 ], [ %74, %true_block7 ]
  %.0228.ph = phi float [ 0.000000e+00, %true_block ], [ 0.000000e+00, %true_block4 ], [ %85, %true_block7 ]
  %.0227.ph = phi float [ 0.000000e+00, %true_block ], [ 0.000000e+00, %true_block4 ], [ 1.000000e+00, %true_block7 ]
  %86 = add i32 %49, -3
  %87 = icmp sgt i32 %86, -1
  %or.cond405 = select i1 %57, i1 %87, i1 false
  br i1 %or.cond405, label %true_block16, label %true_block22

true_block16:                                     ; preds = %true_block10
  %88 = getelementptr inbounds i8, i8* %32, i64 12
  %89 = bitcast i8* %88 to i32*
  %90 = load i32, i32* %89, align 4
  %91 = icmp slt i32 %86, %90
  br i1 %91, label %true_block19, label %true_block22

true_block19:                                     ; preds = %true_block16
  %92 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %93 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %92, i64 0, i32 1, i32 1
  %94 = load float*, float** %93, align 8
  %95 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %92, i64 0, i32 1, i32 0, i32 1
  %96 = load i32, i32* %95, align 4
  %97 = mul i32 %96, %51
  %98 = sub i32 %97, %45
  %99 = add i32 %lsr.iv, %98
  %100 = add i32 %99, -3
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %94, i64 %101
  %103 = load float, float* %102, align 4
  %104 = fadd reassoc ninf nsz float %103, %.0253.ph
  %105 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %92, i64 0, i32 2, i32 1
  %106 = load float*, float** %105, align 8
  %107 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %92, i64 0, i32 2, i32 0, i32 1
  %108 = load i32, i32* %107, align 4
  %109 = mul i32 %108, %51
  %110 = sub i32 %109, %45
  %111 = add i32 %lsr.iv, %110
  %112 = add i32 %111, -3
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %106, i64 %113
  %115 = load float, float* %114, align 4
  %116 = fadd reassoc ninf nsz float %115, %.0228.ph
  %117 = fadd reassoc ninf nsz float %.0227.ph, 1.000000e+00
  br label %true_block22

true_block22:                                     ; preds = %true_block19, %true_block16, %true_block10
  %.1254.ph = phi float [ %.0253.ph, %true_block10 ], [ %.0253.ph, %true_block16 ], [ %104, %true_block19 ]
  %.1229.ph = phi float [ %.0228.ph, %true_block10 ], [ %.0228.ph, %true_block16 ], [ %116, %true_block19 ]
  %.1.ph = phi float [ %.0227.ph, %true_block10 ], [ %.0227.ph, %true_block16 ], [ %117, %true_block19 ]
  %118 = icmp sgt i32 %50, -1
  %or.cond406 = select i1 %57, i1 %118, i1 false
  br i1 %or.cond406, label %true_block28, label %true_block34

true_block28:                                     ; preds = %true_block22
  %119 = getelementptr inbounds i8, i8* %32, i64 12
  %120 = bitcast i8* %119 to i32*
  %121 = load i32, i32* %120, align 4
  %122 = icmp slt i32 %50, %121
  br i1 %122, label %true_block31, label %true_block34

true_block31:                                     ; preds = %true_block28
  %123 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %124 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %123, i64 0, i32 1, i32 1
  %125 = load float*, float** %124, align 8
  %126 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %123, i64 0, i32 1, i32 0, i32 1
  %127 = load i32, i32* %126, align 4
  %128 = mul i32 %127, %51
  %129 = sub i32 %128, %45
  %130 = add i32 %lsr.iv, %129
  %131 = add i32 %130, -2
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %125, i64 %132
  %134 = load float, float* %133, align 4
  %135 = fadd reassoc ninf nsz float %134, %.1254.ph
  %136 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %123, i64 0, i32 2, i32 1
  %137 = load float*, float** %136, align 8
  %138 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %123, i64 0, i32 2, i32 0, i32 1
  %139 = load i32, i32* %138, align 4
  %140 = mul i32 %139, %51
  %141 = sub i32 %140, %45
  %142 = add i32 %lsr.iv, %141
  %143 = add i32 %142, -2
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, float* %137, i64 %144
  %146 = load float, float* %145, align 4
  %147 = fadd reassoc ninf nsz float %146, %.1229.ph
  %148 = fadd reassoc ninf nsz float %.1.ph, 1.000000e+00
  br label %true_block34

true_block34:                                     ; preds = %true_block31, %true_block28, %true_block22
  %.2255.ph = phi float [ %.1254.ph, %true_block22 ], [ %.1254.ph, %true_block28 ], [ %135, %true_block31 ]
  %.2230.ph = phi float [ %.1229.ph, %true_block22 ], [ %.1229.ph, %true_block28 ], [ %147, %true_block31 ]
  %.2.ph = phi float [ %.1.ph, %true_block22 ], [ %.1.ph, %true_block28 ], [ %148, %true_block31 ]
  %149 = add i32 %49, -1
  %150 = icmp sgt i32 %149, -1
  %or.cond407 = select i1 %57, i1 %150, i1 false
  br i1 %or.cond407, label %true_block40, label %true_block46

true_block40:                                     ; preds = %true_block34
  %151 = getelementptr inbounds i8, i8* %32, i64 12
  %152 = bitcast i8* %151 to i32*
  %153 = load i32, i32* %152, align 4
  %154 = icmp slt i32 %149, %153
  br i1 %154, label %true_block43, label %true_block46

true_block43:                                     ; preds = %true_block40
  %155 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %156 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %155, i64 0, i32 1, i32 1
  %157 = load float*, float** %156, align 8
  %158 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %155, i64 0, i32 1, i32 0, i32 1
  %159 = load i32, i32* %158, align 4
  %160 = mul i32 %159, %51
  %161 = sub i32 %160, %45
  %162 = add i32 %lsr.iv, %161
  %163 = add i32 %162, -1
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %157, i64 %164
  %166 = load float, float* %165, align 4
  %167 = fadd reassoc ninf nsz float %166, %.2255.ph
  %168 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %155, i64 0, i32 2, i32 1
  %169 = load float*, float** %168, align 8
  %170 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %155, i64 0, i32 2, i32 0, i32 1
  %171 = load i32, i32* %170, align 4
  %172 = mul i32 %171, %51
  %173 = sub i32 %172, %45
  %174 = add i32 %lsr.iv, %173
  %175 = add i32 %174, -1
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, float* %169, i64 %176
  %178 = load float, float* %177, align 4
  %179 = fadd reassoc ninf nsz float %178, %.2230.ph
  %180 = fadd reassoc ninf nsz float %.2.ph, 1.000000e+00
  br label %true_block46

after_if45:                                       ; preds = %for_loop_body
  %181 = add i32 %46, -1
  %182 = add i32 %46, 1
  %183 = add i32 %46, 2
  br label %after_if57

true_block46:                                     ; preds = %true_block43, %true_block40, %true_block34
  %.3256.ph = phi float [ %.2255.ph, %true_block34 ], [ %.2255.ph, %true_block40 ], [ %167, %true_block43 ]
  %.3231.ph = phi float [ %.2230.ph, %true_block34 ], [ %.2230.ph, %true_block40 ], [ %179, %true_block43 ]
  %.3.ph = phi float [ %.2.ph, %true_block34 ], [ %.2.ph, %true_block40 ], [ %180, %true_block43 ]
  %184 = icmp sgt i32 %49, -1
  %or.cond408 = select i1 %57, i1 %184, i1 false
  br i1 %or.cond408, label %true_block52, label %true_block46.after_if57_crit_edge

true_block46.after_if57_crit_edge:                ; preds = %true_block46
  br label %after_if57

true_block52:                                     ; preds = %true_block46
  %185 = getelementptr inbounds i8, i8* %32, i64 12
  %186 = bitcast i8* %185 to i32*
  %187 = load i32, i32* %186, align 4
  %188 = icmp slt i32 %49, %187
  br i1 %188, label %true_block55, label %after_if57.thread

true_block55:                                     ; preds = %true_block52
  %189 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %190 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %189, i64 0, i32 1, i32 1
  %191 = load float*, float** %190, align 8
  %192 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %189, i64 0, i32 1, i32 0, i32 1
  %193 = load i32, i32* %192, align 4
  %194 = mul i32 %193, %51
  %195 = sub i32 %194, %45
  %196 = add i32 %lsr.iv, %195
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, float* %191, i64 %197
  %199 = load float, float* %198, align 4
  %200 = fadd reassoc ninf nsz float %199, %.3256.ph
  %201 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %189, i64 0, i32 2, i32 1
  %202 = load float*, float** %201, align 8
  %203 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %189, i64 0, i32 2, i32 0, i32 1
  %204 = load i32, i32* %203, align 4
  %205 = mul i32 %204, %51
  %206 = sub i32 %205, %45
  %207 = add i32 %lsr.iv, %206
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, float* %202, i64 %208
  %210 = load float, float* %209, align 4
  %211 = fadd reassoc ninf nsz float %210, %.3231.ph
  %212 = fadd reassoc ninf nsz float %.3.ph, 1.000000e+00
  br label %after_if57.thread

after_if57.thread:                                ; preds = %true_block55, %true_block52
  %.4257.ph = phi float [ %.3256.ph, %true_block52 ], [ %200, %true_block55 ]
  %.4232.ph = phi float [ %.3231.ph, %true_block52 ], [ %211, %true_block55 ]
  %.4.ph = phi float [ %.3.ph, %true_block52 ], [ %212, %true_block55 ]
  %213 = add i32 %44, -1
  br label %true_block58

after_if57:                                       ; preds = %true_block46.after_if57_crit_edge, %after_if45
  %214 = phi i32 [ %183, %after_if45 ], [ %49, %true_block46.after_if57_crit_edge ]
  %215 = phi i32 [ %181, %after_if45 ], [ %86, %true_block46.after_if57_crit_edge ]
  %216 = phi i32 [ %182, %after_if45 ], [ %149, %true_block46.after_if57_crit_edge ]
  %.4257 = phi float [ 0.000000e+00, %after_if45 ], [ %.3256.ph, %true_block46.after_if57_crit_edge ]
  %.4232 = phi float [ 0.000000e+00, %after_if45 ], [ %.3231.ph, %true_block46.after_if57_crit_edge ]
  %.4 = phi float [ 0.000000e+00, %after_if45 ], [ %.3.ph, %true_block46.after_if57_crit_edge ]
  %217 = add i32 %44, -1
  %218 = icmp sgt i32 %217, -1
  br i1 %218, label %after_if57.true_block58_crit_edge, label %after_if117

after_if57.true_block58_crit_edge:                ; preds = %after_if57
  %.phi.trans.insert = getelementptr inbounds i8, i8* %32, i64 8
  %.phi.trans.insert562 = bitcast i8* %.phi.trans.insert to i32*
  %.pre = load i32, i32* %.phi.trans.insert562, align 4
  br label %true_block58

true_block58:                                     ; preds = %after_if57.true_block58_crit_edge, %after_if57.thread
  %219 = phi i32 [ %56, %after_if57.thread ], [ %.pre, %after_if57.true_block58_crit_edge ]
  %220 = phi i32 [ %213, %after_if57.thread ], [ %217, %after_if57.true_block58_crit_edge ]
  %.4458 = phi float [ %.4.ph, %after_if57.thread ], [ %.4, %after_if57.true_block58_crit_edge ]
  %.4232457 = phi float [ %.4232.ph, %after_if57.thread ], [ %.4232, %after_if57.true_block58_crit_edge ]
  %.4257456 = phi float [ %.4257.ph, %after_if57.thread ], [ %.4257, %after_if57.true_block58_crit_edge ]
  %221 = phi i32 [ %149, %after_if57.thread ], [ %216, %after_if57.true_block58_crit_edge ]
  %222 = phi i32 [ %86, %after_if57.thread ], [ %215, %after_if57.true_block58_crit_edge ]
  %223 = phi i32 [ %49, %after_if57.thread ], [ %214, %after_if57.true_block58_crit_edge ]
  %224 = icmp slt i32 %220, %219
  %225 = icmp sgt i32 %52, -1
  %or.cond409 = select i1 %224, i1 %225, i1 false
  br i1 %or.cond409, label %true_block64, label %true_block70

true_block64:                                     ; preds = %true_block58
  %226 = getelementptr inbounds i8, i8* %32, i64 12
  %227 = bitcast i8* %226 to i32*
  %228 = load i32, i32* %227, align 4
  %229 = icmp slt i32 %52, %228
  br i1 %229, label %true_block67, label %true_block70

true_block67:                                     ; preds = %true_block64
  %230 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %231 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %230, i64 0, i32 1, i32 1
  %232 = load float*, float** %231, align 8
  %233 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %230, i64 0, i32 1, i32 0, i32 1
  %234 = load i32, i32* %233, align 4
  %235 = mul i32 %234, %220
  %236 = sub i32 %235, %45
  %237 = add i32 %lsr.iv, %236
  %238 = add i32 %237, -4
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, float* %232, i64 %239
  %241 = load float, float* %240, align 4
  %242 = fadd reassoc ninf nsz float %241, %.4257456
  %243 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %230, i64 0, i32 2, i32 1
  %244 = load float*, float** %243, align 8
  %245 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %230, i64 0, i32 2, i32 0, i32 1
  %246 = load i32, i32* %245, align 4
  %247 = mul i32 %246, %220
  %248 = sub i32 %247, %45
  %249 = add i32 %lsr.iv, %248
  %250 = add i32 %249, -4
  %251 = sext i32 %250 to i64
  %252 = getelementptr float, float* %244, i64 %251
  %253 = load float, float* %252, align 4
  %254 = fadd reassoc ninf nsz float %253, %.4232457
  %255 = fadd reassoc ninf nsz float %.4458, 1.000000e+00
  br label %true_block70

true_block70:                                     ; preds = %true_block67, %true_block64, %true_block58
  %.5464 = phi float [ %255, %true_block67 ], [ %.4458, %true_block58 ], [ %.4458, %true_block64 ]
  %.5233463 = phi float [ %254, %true_block67 ], [ %.4232457, %true_block58 ], [ %.4232457, %true_block64 ]
  %.5258462 = phi float [ %242, %true_block67 ], [ %.4257456, %true_block58 ], [ %.4257456, %true_block64 ]
  %256 = icmp sgt i32 %222, -1
  %or.cond410 = select i1 %224, i1 %256, i1 false
  br i1 %or.cond410, label %true_block76, label %true_block82

true_block76:                                     ; preds = %true_block70
  %257 = getelementptr inbounds i8, i8* %32, i64 12
  %258 = bitcast i8* %257 to i32*
  %259 = load i32, i32* %258, align 4
  %260 = icmp slt i32 %222, %259
  br i1 %260, label %true_block79, label %true_block82

true_block79:                                     ; preds = %true_block76
  %261 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %262 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %261, i64 0, i32 1, i32 1
  %263 = load float*, float** %262, align 8
  %264 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %261, i64 0, i32 1, i32 0, i32 1
  %265 = load i32, i32* %264, align 4
  %266 = mul i32 %265, %220
  %267 = add i32 %266, %222
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, float* %263, i64 %268
  %270 = load float, float* %269, align 4
  %271 = fadd reassoc ninf nsz float %270, %.5258462
  %272 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %261, i64 0, i32 2, i32 1
  %273 = load float*, float** %272, align 8
  %274 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %261, i64 0, i32 2, i32 0, i32 1
  %275 = load i32, i32* %274, align 4
  %276 = mul i32 %275, %220
  %277 = add i32 %276, %222
  %278 = sext i32 %277 to i64
  %279 = getelementptr float, float* %273, i64 %278
  %280 = load float, float* %279, align 4
  %281 = fadd reassoc ninf nsz float %280, %.5233463
  %282 = fadd reassoc ninf nsz float %.5464, 1.000000e+00
  br label %true_block82

true_block82:                                     ; preds = %true_block79, %true_block76, %true_block70
  %.6259.ph = phi float [ %.5258462, %true_block70 ], [ %.5258462, %true_block76 ], [ %271, %true_block79 ]
  %.6234.ph = phi float [ %.5233463, %true_block70 ], [ %.5233463, %true_block76 ], [ %281, %true_block79 ]
  %.6.ph = phi float [ %.5464, %true_block70 ], [ %.5464, %true_block76 ], [ %282, %true_block79 ]
  %283 = icmp sgt i32 %50, -1
  %or.cond411 = select i1 %224, i1 %283, i1 false
  br i1 %or.cond411, label %true_block88, label %true_block94

true_block88:                                     ; preds = %true_block82
  %284 = getelementptr inbounds i8, i8* %32, i64 12
  %285 = bitcast i8* %284 to i32*
  %286 = load i32, i32* %285, align 4
  %287 = icmp slt i32 %50, %286
  br i1 %287, label %true_block91, label %true_block94

true_block91:                                     ; preds = %true_block88
  %288 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %289 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %288, i64 0, i32 1, i32 1
  %290 = load float*, float** %289, align 8
  %291 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %288, i64 0, i32 1, i32 0, i32 1
  %292 = load i32, i32* %291, align 4
  %293 = mul i32 %292, %220
  %294 = sub i32 %293, %45
  %295 = add i32 %lsr.iv, %294
  %296 = add i32 %295, -2
  %297 = sext i32 %296 to i64
  %298 = getelementptr float, float* %290, i64 %297
  %299 = load float, float* %298, align 4
  %300 = fadd reassoc ninf nsz float %299, %.6259.ph
  %301 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %288, i64 0, i32 2, i32 1
  %302 = load float*, float** %301, align 8
  %303 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %288, i64 0, i32 2, i32 0, i32 1
  %304 = load i32, i32* %303, align 4
  %305 = mul i32 %304, %220
  %306 = sub i32 %305, %45
  %307 = add i32 %lsr.iv, %306
  %308 = add i32 %307, -2
  %309 = sext i32 %308 to i64
  %310 = getelementptr float, float* %302, i64 %309
  %311 = load float, float* %310, align 4
  %312 = fadd reassoc ninf nsz float %311, %.6234.ph
  %313 = fadd reassoc ninf nsz float %.6.ph, 1.000000e+00
  br label %true_block94

true_block94:                                     ; preds = %true_block91, %true_block88, %true_block82
  %.7260.ph = phi float [ %.6259.ph, %true_block82 ], [ %.6259.ph, %true_block88 ], [ %300, %true_block91 ]
  %.7235.ph = phi float [ %.6234.ph, %true_block82 ], [ %.6234.ph, %true_block88 ], [ %312, %true_block91 ]
  %.7.ph = phi float [ %.6.ph, %true_block82 ], [ %.6.ph, %true_block88 ], [ %313, %true_block91 ]
  %314 = icmp sgt i32 %221, -1
  %or.cond412 = select i1 %224, i1 %314, i1 false
  br i1 %or.cond412, label %true_block100, label %true_block106

true_block100:                                    ; preds = %true_block94
  %315 = getelementptr inbounds i8, i8* %32, i64 12
  %316 = bitcast i8* %315 to i32*
  %317 = load i32, i32* %316, align 4
  %318 = icmp slt i32 %221, %317
  br i1 %318, label %true_block103, label %true_block106

true_block103:                                    ; preds = %true_block100
  %319 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %320 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %319, i64 0, i32 1, i32 1
  %321 = load float*, float** %320, align 8
  %322 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %319, i64 0, i32 1, i32 0, i32 1
  %323 = load i32, i32* %322, align 4
  %324 = mul i32 %323, %220
  %325 = add i32 %324, %221
  %326 = sext i32 %325 to i64
  %327 = getelementptr float, float* %321, i64 %326
  %328 = load float, float* %327, align 4
  %329 = fadd reassoc ninf nsz float %328, %.7260.ph
  %330 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %319, i64 0, i32 2, i32 1
  %331 = load float*, float** %330, align 8
  %332 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %319, i64 0, i32 2, i32 0, i32 1
  %333 = load i32, i32* %332, align 4
  %334 = mul i32 %333, %220
  %335 = add i32 %334, %221
  %336 = sext i32 %335 to i64
  %337 = getelementptr float, float* %331, i64 %336
  %338 = load float, float* %337, align 4
  %339 = fadd reassoc ninf nsz float %338, %.7235.ph
  %340 = fadd reassoc ninf nsz float %.7.ph, 1.000000e+00
  br label %true_block106

true_block106:                                    ; preds = %true_block103, %true_block100, %true_block94
  %.8261.ph = phi float [ %.7260.ph, %true_block94 ], [ %.7260.ph, %true_block100 ], [ %329, %true_block103 ]
  %.8236.ph = phi float [ %.7235.ph, %true_block94 ], [ %.7235.ph, %true_block100 ], [ %339, %true_block103 ]
  %.8.ph = phi float [ %.7.ph, %true_block94 ], [ %.7.ph, %true_block100 ], [ %340, %true_block103 ]
  %341 = icmp sgt i32 %223, -1
  %or.cond413 = select i1 %224, i1 %341, i1 false
  br i1 %or.cond413, label %true_block112, label %after_if117

true_block112:                                    ; preds = %true_block106
  %342 = getelementptr inbounds i8, i8* %32, i64 12
  %343 = bitcast i8* %342 to i32*
  %344 = load i32, i32* %343, align 4
  %345 = icmp slt i32 %223, %344
  br i1 %345, label %true_block115, label %after_if117

true_block115:                                    ; preds = %true_block112
  %346 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %347 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %346, i64 0, i32 1, i32 1
  %348 = load float*, float** %347, align 8
  %349 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %346, i64 0, i32 1, i32 0, i32 1
  %350 = load i32, i32* %349, align 4
  %351 = mul i32 %350, %220
  %352 = add i32 %351, %223
  %353 = sext i32 %352 to i64
  %354 = getelementptr float, float* %348, i64 %353
  %355 = load float, float* %354, align 4
  %356 = fadd reassoc ninf nsz float %355, %.8261.ph
  %357 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %346, i64 0, i32 2, i32 1
  %358 = load float*, float** %357, align 8
  %359 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %346, i64 0, i32 2, i32 0, i32 1
  %360 = load i32, i32* %359, align 4
  %361 = mul i32 %360, %220
  %362 = add i32 %361, %223
  %363 = sext i32 %362 to i64
  %364 = getelementptr float, float* %358, i64 %363
  %365 = load float, float* %364, align 4
  %366 = fadd reassoc ninf nsz float %365, %.8236.ph
  %367 = fadd reassoc ninf nsz float %.8.ph, 1.000000e+00
  br label %after_if117

after_if117:                                      ; preds = %true_block115, %true_block112, %true_block106, %after_if57
  %368 = phi i32 [ %221, %true_block115 ], [ %221, %true_block112 ], [ %221, %true_block106 ], [ %216, %after_if57 ]
  %369 = phi i32 [ %222, %true_block115 ], [ %222, %true_block112 ], [ %222, %true_block106 ], [ %215, %after_if57 ]
  %370 = phi i32 [ %223, %true_block115 ], [ %223, %true_block112 ], [ %223, %true_block106 ], [ %214, %after_if57 ]
  %.9262 = phi float [ %356, %true_block115 ], [ %.8261.ph, %true_block112 ], [ %.8261.ph, %true_block106 ], [ %.4257, %after_if57 ]
  %.9237 = phi float [ %366, %true_block115 ], [ %.8236.ph, %true_block112 ], [ %.8236.ph, %true_block106 ], [ %.4232, %after_if57 ]
  %.9 = phi float [ %367, %true_block115 ], [ %.8.ph, %true_block112 ], [ %.8.ph, %true_block106 ], [ %.4, %after_if57 ]
  %371 = icmp sgt i32 %44, -1
  br i1 %371, label %true_block118, label %after_if177

true_block118:                                    ; preds = %after_if117
  %372 = getelementptr inbounds i8, i8* %32, i64 8
  %373 = bitcast i8* %372 to i32*
  %374 = load i32, i32* %373, align 4
  %375 = icmp slt i32 %44, %374
  %376 = icmp sgt i32 %52, -1
  %or.cond414 = select i1 %375, i1 %376, i1 false
  br i1 %or.cond414, label %true_block124, label %true_block130

true_block124:                                    ; preds = %true_block118
  %377 = getelementptr inbounds i8, i8* %32, i64 12
  %378 = bitcast i8* %377 to i32*
  %379 = load i32, i32* %378, align 4
  %380 = icmp slt i32 %52, %379
  br i1 %380, label %true_block127, label %true_block130

true_block127:                                    ; preds = %true_block124
  %381 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %382 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %381, i64 0, i32 1, i32 1
  %383 = load float*, float** %382, align 8
  %384 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %381, i64 0, i32 1, i32 0, i32 1
  %385 = load i32, i32* %384, align 4
  %386 = sub i32 %385, %35
  %387 = mul i32 %386, %44
  %388 = add i32 %lsr.iv, %387
  %389 = add i32 %388, -4
  %390 = sext i32 %389 to i64
  %391 = getelementptr float, float* %383, i64 %390
  %392 = load float, float* %391, align 4
  %393 = fadd reassoc ninf nsz float %392, %.9262
  %394 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %381, i64 0, i32 2, i32 1
  %395 = load float*, float** %394, align 8
  %396 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %381, i64 0, i32 2, i32 0, i32 1
  %397 = load i32, i32* %396, align 4
  %398 = sub i32 %397, %35
  %399 = mul i32 %398, %44
  %400 = add i32 %lsr.iv, %399
  %401 = add i32 %400, -4
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, float* %395, i64 %402
  %404 = load float, float* %403, align 4
  %405 = fadd reassoc ninf nsz float %404, %.9237
  %406 = fadd reassoc ninf nsz float %.9, 1.000000e+00
  br label %true_block130

true_block130:                                    ; preds = %true_block127, %true_block124, %true_block118
  %.10263.ph = phi float [ %.9262, %true_block118 ], [ %.9262, %true_block124 ], [ %393, %true_block127 ]
  %.10238.ph = phi float [ %.9237, %true_block118 ], [ %.9237, %true_block124 ], [ %405, %true_block127 ]
  %.10.ph = phi float [ %.9, %true_block118 ], [ %.9, %true_block124 ], [ %406, %true_block127 ]
  %407 = icmp sgt i32 %369, -1
  %or.cond415 = select i1 %375, i1 %407, i1 false
  br i1 %or.cond415, label %true_block136, label %true_block142

true_block136:                                    ; preds = %true_block130
  %408 = getelementptr inbounds i8, i8* %32, i64 12
  %409 = bitcast i8* %408 to i32*
  %410 = load i32, i32* %409, align 4
  %411 = icmp slt i32 %369, %410
  br i1 %411, label %true_block139, label %true_block142

true_block139:                                    ; preds = %true_block136
  %412 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %413 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %412, i64 0, i32 1, i32 1
  %414 = load float*, float** %413, align 8
  %415 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %412, i64 0, i32 1, i32 0, i32 1
  %416 = load i32, i32* %415, align 4
  %417 = mul i32 %416, %44
  %418 = add i32 %417, %369
  %419 = sext i32 %418 to i64
  %420 = getelementptr float, float* %414, i64 %419
  %421 = load float, float* %420, align 4
  %422 = fadd reassoc ninf nsz float %421, %.10263.ph
  %423 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %412, i64 0, i32 2, i32 1
  %424 = load float*, float** %423, align 8
  %425 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %412, i64 0, i32 2, i32 0, i32 1
  %426 = load i32, i32* %425, align 4
  %427 = mul i32 %426, %44
  %428 = add i32 %427, %369
  %429 = sext i32 %428 to i64
  %430 = getelementptr float, float* %424, i64 %429
  %431 = load float, float* %430, align 4
  %432 = fadd reassoc ninf nsz float %431, %.10238.ph
  %433 = fadd reassoc ninf nsz float %.10.ph, 1.000000e+00
  br label %true_block142

true_block142:                                    ; preds = %true_block139, %true_block136, %true_block130
  %.11264.ph = phi float [ %.10263.ph, %true_block130 ], [ %.10263.ph, %true_block136 ], [ %422, %true_block139 ]
  %.11239.ph = phi float [ %.10238.ph, %true_block130 ], [ %.10238.ph, %true_block136 ], [ %432, %true_block139 ]
  %.11.ph = phi float [ %.10.ph, %true_block130 ], [ %.10.ph, %true_block136 ], [ %433, %true_block139 ]
  %434 = icmp sgt i32 %50, -1
  %or.cond416 = select i1 %375, i1 %434, i1 false
  br i1 %or.cond416, label %true_block148, label %true_block154

true_block148:                                    ; preds = %true_block142
  %435 = getelementptr inbounds i8, i8* %32, i64 12
  %436 = bitcast i8* %435 to i32*
  %437 = load i32, i32* %436, align 4
  %438 = icmp slt i32 %50, %437
  br i1 %438, label %true_block151, label %true_block154

true_block151:                                    ; preds = %true_block148
  %439 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %440 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %439, i64 0, i32 1, i32 1
  %441 = load float*, float** %440, align 8
  %442 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %439, i64 0, i32 1, i32 0, i32 1
  %443 = load i32, i32* %442, align 4
  %444 = sub i32 %443, %35
  %445 = mul i32 %444, %44
  %446 = add i32 %lsr.iv, %445
  %447 = add i32 %446, -2
  %448 = sext i32 %447 to i64
  %449 = getelementptr float, float* %441, i64 %448
  %450 = load float, float* %449, align 4
  %451 = fadd reassoc ninf nsz float %450, %.11264.ph
  %452 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %439, i64 0, i32 2, i32 1
  %453 = load float*, float** %452, align 8
  %454 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %439, i64 0, i32 2, i32 0, i32 1
  %455 = load i32, i32* %454, align 4
  %456 = sub i32 %455, %35
  %457 = mul i32 %456, %44
  %458 = add i32 %lsr.iv, %457
  %459 = add i32 %458, -2
  %460 = sext i32 %459 to i64
  %461 = getelementptr float, float* %453, i64 %460
  %462 = load float, float* %461, align 4
  %463 = fadd reassoc ninf nsz float %462, %.11239.ph
  %464 = fadd reassoc ninf nsz float %.11.ph, 1.000000e+00
  br label %true_block154

true_block154:                                    ; preds = %true_block151, %true_block148, %true_block142
  %.12265.ph = phi float [ %.11264.ph, %true_block142 ], [ %.11264.ph, %true_block148 ], [ %451, %true_block151 ]
  %.12240.ph = phi float [ %.11239.ph, %true_block142 ], [ %.11239.ph, %true_block148 ], [ %463, %true_block151 ]
  %.12.ph = phi float [ %.11.ph, %true_block142 ], [ %.11.ph, %true_block148 ], [ %464, %true_block151 ]
  %465 = icmp sgt i32 %368, -1
  %or.cond417 = select i1 %375, i1 %465, i1 false
  br i1 %or.cond417, label %true_block160, label %true_block166

true_block160:                                    ; preds = %true_block154
  %466 = getelementptr inbounds i8, i8* %32, i64 12
  %467 = bitcast i8* %466 to i32*
  %468 = load i32, i32* %467, align 4
  %469 = icmp slt i32 %368, %468
  br i1 %469, label %true_block163, label %true_block166

true_block163:                                    ; preds = %true_block160
  %470 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %471 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %470, i64 0, i32 1, i32 1
  %472 = load float*, float** %471, align 8
  %473 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %470, i64 0, i32 1, i32 0, i32 1
  %474 = load i32, i32* %473, align 4
  %475 = mul i32 %474, %44
  %476 = add i32 %475, %368
  %477 = sext i32 %476 to i64
  %478 = getelementptr float, float* %472, i64 %477
  %479 = load float, float* %478, align 4
  %480 = fadd reassoc ninf nsz float %479, %.12265.ph
  %481 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %470, i64 0, i32 2, i32 1
  %482 = load float*, float** %481, align 8
  %483 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %470, i64 0, i32 2, i32 0, i32 1
  %484 = load i32, i32* %483, align 4
  %485 = mul i32 %484, %44
  %486 = add i32 %485, %368
  %487 = sext i32 %486 to i64
  %488 = getelementptr float, float* %482, i64 %487
  %489 = load float, float* %488, align 4
  %490 = fadd reassoc ninf nsz float %489, %.12240.ph
  %491 = fadd reassoc ninf nsz float %.12.ph, 1.000000e+00
  br label %true_block166

true_block166:                                    ; preds = %true_block163, %true_block160, %true_block154
  %.13266.ph = phi float [ %.12265.ph, %true_block154 ], [ %.12265.ph, %true_block160 ], [ %480, %true_block163 ]
  %.13241.ph = phi float [ %.12240.ph, %true_block154 ], [ %.12240.ph, %true_block160 ], [ %490, %true_block163 ]
  %.13.ph = phi float [ %.12.ph, %true_block154 ], [ %.12.ph, %true_block160 ], [ %491, %true_block163 ]
  %492 = icmp sgt i32 %370, -1
  %or.cond418 = select i1 %375, i1 %492, i1 false
  br i1 %or.cond418, label %true_block172, label %after_if177

true_block172:                                    ; preds = %true_block166
  %493 = getelementptr inbounds i8, i8* %32, i64 12
  %494 = bitcast i8* %493 to i32*
  %495 = load i32, i32* %494, align 4
  %496 = icmp slt i32 %370, %495
  br i1 %496, label %true_block175, label %after_if177.thread

true_block175:                                    ; preds = %true_block172
  %497 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %498 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %497, i64 0, i32 1, i32 1
  %499 = load float*, float** %498, align 8
  %500 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %497, i64 0, i32 1, i32 0, i32 1
  %501 = load i32, i32* %500, align 4
  %502 = mul i32 %501, %44
  %503 = add i32 %502, %370
  %504 = sext i32 %503 to i64
  %505 = getelementptr float, float* %499, i64 %504
  %506 = load float, float* %505, align 4
  %507 = fadd reassoc ninf nsz float %506, %.13266.ph
  %508 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %497, i64 0, i32 2, i32 1
  %509 = load float*, float** %508, align 8
  %510 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %497, i64 0, i32 2, i32 0, i32 1
  %511 = load i32, i32* %510, align 4
  %512 = mul i32 %511, %44
  %513 = add i32 %512, %370
  %514 = sext i32 %513 to i64
  %515 = getelementptr float, float* %509, i64 %514
  %516 = load float, float* %515, align 4
  %517 = fadd reassoc ninf nsz float %516, %.13241.ph
  %518 = fadd reassoc ninf nsz float %.13.ph, 1.000000e+00
  br label %after_if177.thread

after_if177.thread:                               ; preds = %true_block175, %true_block172
  %.14267.ph = phi float [ %.13266.ph, %true_block172 ], [ %507, %true_block175 ]
  %.14242.ph = phi float [ %.13241.ph, %true_block172 ], [ %517, %true_block175 ]
  %.14.ph = phi float [ %.13.ph, %true_block172 ], [ %518, %true_block175 ]
  %519 = add nuw nsw i32 %44, 1
  br label %true_block178

after_if177:                                      ; preds = %true_block166, %after_if117
  %.14267 = phi float [ %.13266.ph, %true_block166 ], [ %.9262, %after_if117 ]
  %.14242 = phi float [ %.13241.ph, %true_block166 ], [ %.9237, %after_if117 ]
  %.14 = phi float [ %.13.ph, %true_block166 ], [ %.9, %after_if117 ]
  %520 = add i32 %44, 1
  %521 = icmp sgt i32 %520, -1
  br i1 %521, label %after_if177.true_block178_crit_edge, label %after_if237

after_if177.true_block178_crit_edge:              ; preds = %after_if177
  %.phi.trans.insert563 = getelementptr inbounds i8, i8* %32, i64 8
  %.phi.trans.insert564 = bitcast i8* %.phi.trans.insert563 to i32*
  %.pre565 = load i32, i32* %.phi.trans.insert564, align 4
  br label %true_block178

true_block178:                                    ; preds = %after_if177.true_block178_crit_edge, %after_if177.thread
  %522 = phi i32 [ %374, %after_if177.thread ], [ %.pre565, %after_if177.true_block178_crit_edge ]
  %523 = phi i32 [ %519, %after_if177.thread ], [ %520, %after_if177.true_block178_crit_edge ]
  %.14512 = phi float [ %.14.ph, %after_if177.thread ], [ %.14, %after_if177.true_block178_crit_edge ]
  %.14242511 = phi float [ %.14242.ph, %after_if177.thread ], [ %.14242, %after_if177.true_block178_crit_edge ]
  %.14267510 = phi float [ %.14267.ph, %after_if177.thread ], [ %.14267, %after_if177.true_block178_crit_edge ]
  %524 = icmp slt i32 %523, %522
  %525 = icmp sgt i32 %52, -1
  %or.cond419 = select i1 %524, i1 %525, i1 false
  br i1 %or.cond419, label %true_block184, label %true_block190

true_block184:                                    ; preds = %true_block178
  %526 = getelementptr inbounds i8, i8* %32, i64 12
  %527 = bitcast i8* %526 to i32*
  %528 = load i32, i32* %527, align 4
  %529 = icmp slt i32 %52, %528
  br i1 %529, label %true_block187, label %true_block190

true_block187:                                    ; preds = %true_block184
  %530 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %531 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %530, i64 0, i32 1, i32 1
  %532 = load float*, float** %531, align 8
  %533 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %530, i64 0, i32 1, i32 0, i32 1
  %534 = load i32, i32* %533, align 4
  %535 = mul i32 %534, %523
  %536 = sub i32 %535, %45
  %537 = add i32 %lsr.iv, %536
  %538 = add i32 %537, -4
  %539 = sext i32 %538 to i64
  %540 = getelementptr float, float* %532, i64 %539
  %541 = load float, float* %540, align 4
  %542 = fadd reassoc ninf nsz float %541, %.14267510
  %543 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %530, i64 0, i32 2, i32 1
  %544 = load float*, float** %543, align 8
  %545 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %530, i64 0, i32 2, i32 0, i32 1
  %546 = load i32, i32* %545, align 4
  %547 = mul i32 %546, %523
  %548 = sub i32 %547, %45
  %549 = add i32 %lsr.iv, %548
  %550 = add i32 %549, -4
  %551 = sext i32 %550 to i64
  %552 = getelementptr float, float* %544, i64 %551
  %553 = load float, float* %552, align 4
  %554 = fadd reassoc ninf nsz float %553, %.14242511
  %555 = fadd reassoc ninf nsz float %.14512, 1.000000e+00
  br label %true_block190

true_block190:                                    ; preds = %true_block187, %true_block184, %true_block178
  %.15518 = phi float [ %555, %true_block187 ], [ %.14512, %true_block178 ], [ %.14512, %true_block184 ]
  %.15243517 = phi float [ %554, %true_block187 ], [ %.14242511, %true_block178 ], [ %.14242511, %true_block184 ]
  %.15268516 = phi float [ %542, %true_block187 ], [ %.14267510, %true_block178 ], [ %.14267510, %true_block184 ]
  %556 = icmp sgt i32 %369, -1
  %or.cond420 = select i1 %524, i1 %556, i1 false
  br i1 %or.cond420, label %true_block196, label %true_block202

true_block196:                                    ; preds = %true_block190
  %557 = getelementptr inbounds i8, i8* %32, i64 12
  %558 = bitcast i8* %557 to i32*
  %559 = load i32, i32* %558, align 4
  %560 = icmp slt i32 %369, %559
  br i1 %560, label %true_block199, label %true_block202

true_block199:                                    ; preds = %true_block196
  %561 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %562 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %561, i64 0, i32 1, i32 1
  %563 = load float*, float** %562, align 8
  %564 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %561, i64 0, i32 1, i32 0, i32 1
  %565 = load i32, i32* %564, align 4
  %566 = mul i32 %565, %523
  %567 = add i32 %566, %369
  %568 = sext i32 %567 to i64
  %569 = getelementptr float, float* %563, i64 %568
  %570 = load float, float* %569, align 4
  %571 = fadd reassoc ninf nsz float %570, %.15268516
  %572 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %561, i64 0, i32 2, i32 1
  %573 = load float*, float** %572, align 8
  %574 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %561, i64 0, i32 2, i32 0, i32 1
  %575 = load i32, i32* %574, align 4
  %576 = mul i32 %575, %523
  %577 = add i32 %576, %369
  %578 = sext i32 %577 to i64
  %579 = getelementptr float, float* %573, i64 %578
  %580 = load float, float* %579, align 4
  %581 = fadd reassoc ninf nsz float %580, %.15243517
  %582 = fadd reassoc ninf nsz float %.15518, 1.000000e+00
  br label %true_block202

true_block202:                                    ; preds = %true_block199, %true_block196, %true_block190
  %.16269.ph = phi float [ %.15268516, %true_block190 ], [ %.15268516, %true_block196 ], [ %571, %true_block199 ]
  %.16244.ph = phi float [ %.15243517, %true_block190 ], [ %.15243517, %true_block196 ], [ %581, %true_block199 ]
  %.16.ph = phi float [ %.15518, %true_block190 ], [ %.15518, %true_block196 ], [ %582, %true_block199 ]
  %583 = icmp sgt i32 %50, -1
  %or.cond421 = select i1 %524, i1 %583, i1 false
  br i1 %or.cond421, label %true_block208, label %true_block214

true_block208:                                    ; preds = %true_block202
  %584 = getelementptr inbounds i8, i8* %32, i64 12
  %585 = bitcast i8* %584 to i32*
  %586 = load i32, i32* %585, align 4
  %587 = icmp slt i32 %50, %586
  br i1 %587, label %true_block211, label %true_block214

true_block211:                                    ; preds = %true_block208
  %588 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %589 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %588, i64 0, i32 1, i32 1
  %590 = load float*, float** %589, align 8
  %591 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %588, i64 0, i32 1, i32 0, i32 1
  %592 = load i32, i32* %591, align 4
  %593 = mul i32 %592, %523
  %594 = sub i32 %593, %45
  %595 = add i32 %lsr.iv, %594
  %596 = add i32 %595, -2
  %597 = sext i32 %596 to i64
  %598 = getelementptr float, float* %590, i64 %597
  %599 = load float, float* %598, align 4
  %600 = fadd reassoc ninf nsz float %599, %.16269.ph
  %601 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %588, i64 0, i32 2, i32 1
  %602 = load float*, float** %601, align 8
  %603 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %588, i64 0, i32 2, i32 0, i32 1
  %604 = load i32, i32* %603, align 4
  %605 = mul i32 %604, %523
  %606 = sub i32 %605, %45
  %607 = add i32 %lsr.iv, %606
  %608 = add i32 %607, -2
  %609 = sext i32 %608 to i64
  %610 = getelementptr float, float* %602, i64 %609
  %611 = load float, float* %610, align 4
  %612 = fadd reassoc ninf nsz float %611, %.16244.ph
  %613 = fadd reassoc ninf nsz float %.16.ph, 1.000000e+00
  br label %true_block214

true_block214:                                    ; preds = %true_block211, %true_block208, %true_block202
  %.17270.ph = phi float [ %.16269.ph, %true_block202 ], [ %.16269.ph, %true_block208 ], [ %600, %true_block211 ]
  %.17245.ph = phi float [ %.16244.ph, %true_block202 ], [ %.16244.ph, %true_block208 ], [ %612, %true_block211 ]
  %.17.ph = phi float [ %.16.ph, %true_block202 ], [ %.16.ph, %true_block208 ], [ %613, %true_block211 ]
  %614 = icmp sgt i32 %368, -1
  %or.cond422 = select i1 %524, i1 %614, i1 false
  br i1 %or.cond422, label %true_block220, label %true_block226

true_block220:                                    ; preds = %true_block214
  %615 = getelementptr inbounds i8, i8* %32, i64 12
  %616 = bitcast i8* %615 to i32*
  %617 = load i32, i32* %616, align 4
  %618 = icmp slt i32 %368, %617
  br i1 %618, label %true_block223, label %true_block226

true_block223:                                    ; preds = %true_block220
  %619 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %620 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %619, i64 0, i32 1, i32 1
  %621 = load float*, float** %620, align 8
  %622 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %619, i64 0, i32 1, i32 0, i32 1
  %623 = load i32, i32* %622, align 4
  %624 = mul i32 %623, %523
  %625 = add i32 %624, %368
  %626 = sext i32 %625 to i64
  %627 = getelementptr float, float* %621, i64 %626
  %628 = load float, float* %627, align 4
  %629 = fadd reassoc ninf nsz float %628, %.17270.ph
  %630 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %619, i64 0, i32 2, i32 1
  %631 = load float*, float** %630, align 8
  %632 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %619, i64 0, i32 2, i32 0, i32 1
  %633 = load i32, i32* %632, align 4
  %634 = mul i32 %633, %523
  %635 = add i32 %634, %368
  %636 = sext i32 %635 to i64
  %637 = getelementptr float, float* %631, i64 %636
  %638 = load float, float* %637, align 4
  %639 = fadd reassoc ninf nsz float %638, %.17245.ph
  %640 = fadd reassoc ninf nsz float %.17.ph, 1.000000e+00
  br label %true_block226

true_block226:                                    ; preds = %true_block223, %true_block220, %true_block214
  %.18271.ph = phi float [ %.17270.ph, %true_block214 ], [ %.17270.ph, %true_block220 ], [ %629, %true_block223 ]
  %.18246.ph = phi float [ %.17245.ph, %true_block214 ], [ %.17245.ph, %true_block220 ], [ %639, %true_block223 ]
  %.18.ph = phi float [ %.17.ph, %true_block214 ], [ %.17.ph, %true_block220 ], [ %640, %true_block223 ]
  %641 = icmp sgt i32 %370, -1
  %or.cond423 = select i1 %524, i1 %641, i1 false
  br i1 %or.cond423, label %true_block232, label %after_if237

true_block232:                                    ; preds = %true_block226
  %642 = getelementptr inbounds i8, i8* %32, i64 12
  %643 = bitcast i8* %642 to i32*
  %644 = load i32, i32* %643, align 4
  %645 = icmp slt i32 %370, %644
  br i1 %645, label %true_block235, label %after_if237

true_block235:                                    ; preds = %true_block232
  %646 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %647 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %646, i64 0, i32 1, i32 1
  %648 = load float*, float** %647, align 8
  %649 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %646, i64 0, i32 1, i32 0, i32 1
  %650 = load i32, i32* %649, align 4
  %651 = mul i32 %650, %523
  %652 = add i32 %651, %370
  %653 = sext i32 %652 to i64
  %654 = getelementptr float, float* %648, i64 %653
  %655 = load float, float* %654, align 4
  %656 = fadd reassoc ninf nsz float %655, %.18271.ph
  %657 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %646, i64 0, i32 2, i32 1
  %658 = load float*, float** %657, align 8
  %659 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %646, i64 0, i32 2, i32 0, i32 1
  %660 = load i32, i32* %659, align 4
  %661 = mul i32 %660, %523
  %662 = add i32 %661, %370
  %663 = sext i32 %662 to i64
  %664 = getelementptr float, float* %658, i64 %663
  %665 = load float, float* %664, align 4
  %666 = fadd reassoc ninf nsz float %665, %.18246.ph
  %667 = fadd reassoc ninf nsz float %.18.ph, 1.000000e+00
  br label %after_if237

after_if237:                                      ; preds = %true_block235, %true_block232, %true_block226, %after_if177
  %.19272 = phi float [ %656, %true_block235 ], [ %.18271.ph, %true_block232 ], [ %.18271.ph, %true_block226 ], [ %.14267, %after_if177 ]
  %.19247 = phi float [ %666, %true_block235 ], [ %.18246.ph, %true_block232 ], [ %.18246.ph, %true_block226 ], [ %.14242, %after_if177 ]
  %.19 = phi float [ %667, %true_block235 ], [ %.18.ph, %true_block232 ], [ %.18.ph, %true_block226 ], [ %.14, %after_if177 ]
  %668 = add i32 %44, 2
  %669 = icmp sgt i32 %668, -1
  br i1 %669, label %true_block238, label %after_if297

true_block238:                                    ; preds = %after_if237
  %670 = getelementptr inbounds i8, i8* %32, i64 8
  %671 = bitcast i8* %670 to i32*
  %672 = load i32, i32* %671, align 4
  %673 = icmp slt i32 %668, %672
  %674 = icmp sgt i32 %52, -1
  %or.cond424 = select i1 %673, i1 %674, i1 false
  br i1 %or.cond424, label %true_block244, label %true_block250

true_block244:                                    ; preds = %true_block238
  %675 = getelementptr inbounds i8, i8* %32, i64 12
  %676 = bitcast i8* %675 to i32*
  %677 = load i32, i32* %676, align 4
  %678 = icmp slt i32 %52, %677
  br i1 %678, label %true_block247, label %true_block250

true_block247:                                    ; preds = %true_block244
  %679 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %680 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %679, i64 0, i32 1, i32 1
  %681 = load float*, float** %680, align 8
  %682 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %679, i64 0, i32 1, i32 0, i32 1
  %683 = load i32, i32* %682, align 4
  %684 = mul i32 %683, %668
  %685 = sub i32 %684, %45
  %686 = add i32 %lsr.iv, %685
  %687 = add i32 %686, -4
  %688 = sext i32 %687 to i64
  %689 = getelementptr float, float* %681, i64 %688
  %690 = load float, float* %689, align 4
  %691 = fadd reassoc ninf nsz float %690, %.19272
  %692 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %679, i64 0, i32 2, i32 1
  %693 = load float*, float** %692, align 8
  %694 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %679, i64 0, i32 2, i32 0, i32 1
  %695 = load i32, i32* %694, align 4
  %696 = mul i32 %695, %668
  %697 = sub i32 %696, %45
  %698 = add i32 %lsr.iv, %697
  %699 = add i32 %698, -4
  %700 = sext i32 %699 to i64
  %701 = getelementptr float, float* %693, i64 %700
  %702 = load float, float* %701, align 4
  %703 = fadd reassoc ninf nsz float %702, %.19247
  %704 = fadd reassoc ninf nsz float %.19, 1.000000e+00
  br label %true_block250

true_block250:                                    ; preds = %true_block247, %true_block244, %true_block238
  %.20273.ph = phi float [ %.19272, %true_block238 ], [ %.19272, %true_block244 ], [ %691, %true_block247 ]
  %.20248.ph = phi float [ %.19247, %true_block238 ], [ %.19247, %true_block244 ], [ %703, %true_block247 ]
  %.20.ph = phi float [ %.19, %true_block238 ], [ %.19, %true_block244 ], [ %704, %true_block247 ]
  %705 = icmp sgt i32 %369, -1
  %or.cond425 = select i1 %673, i1 %705, i1 false
  br i1 %or.cond425, label %true_block256, label %true_block262

true_block256:                                    ; preds = %true_block250
  %706 = getelementptr inbounds i8, i8* %32, i64 12
  %707 = bitcast i8* %706 to i32*
  %708 = load i32, i32* %707, align 4
  %709 = icmp slt i32 %369, %708
  br i1 %709, label %true_block259, label %true_block262

true_block259:                                    ; preds = %true_block256
  %710 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %711 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %710, i64 0, i32 1, i32 1
  %712 = load float*, float** %711, align 8
  %713 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %710, i64 0, i32 1, i32 0, i32 1
  %714 = load i32, i32* %713, align 4
  %715 = mul i32 %714, %668
  %716 = add i32 %715, %369
  %717 = sext i32 %716 to i64
  %718 = getelementptr float, float* %712, i64 %717
  %719 = load float, float* %718, align 4
  %720 = fadd reassoc ninf nsz float %719, %.20273.ph
  %721 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %710, i64 0, i32 2, i32 1
  %722 = load float*, float** %721, align 8
  %723 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %710, i64 0, i32 2, i32 0, i32 1
  %724 = load i32, i32* %723, align 4
  %725 = mul i32 %724, %668
  %726 = add i32 %725, %369
  %727 = sext i32 %726 to i64
  %728 = getelementptr float, float* %722, i64 %727
  %729 = load float, float* %728, align 4
  %730 = fadd reassoc ninf nsz float %729, %.20248.ph
  %731 = fadd reassoc ninf nsz float %.20.ph, 1.000000e+00
  br label %true_block262

true_block262:                                    ; preds = %true_block259, %true_block256, %true_block250
  %.21274.ph = phi float [ %.20273.ph, %true_block250 ], [ %.20273.ph, %true_block256 ], [ %720, %true_block259 ]
  %.21249.ph = phi float [ %.20248.ph, %true_block250 ], [ %.20248.ph, %true_block256 ], [ %730, %true_block259 ]
  %.21.ph = phi float [ %.20.ph, %true_block250 ], [ %.20.ph, %true_block256 ], [ %731, %true_block259 ]
  %732 = icmp sgt i32 %50, -1
  %or.cond426 = select i1 %673, i1 %732, i1 false
  br i1 %or.cond426, label %true_block268, label %true_block274

true_block268:                                    ; preds = %true_block262
  %733 = getelementptr inbounds i8, i8* %32, i64 12
  %734 = bitcast i8* %733 to i32*
  %735 = load i32, i32* %734, align 4
  %736 = icmp slt i32 %50, %735
  br i1 %736, label %true_block271, label %true_block274

true_block271:                                    ; preds = %true_block268
  %737 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %738 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %737, i64 0, i32 1, i32 1
  %739 = load float*, float** %738, align 8
  %740 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %737, i64 0, i32 1, i32 0, i32 1
  %741 = load i32, i32* %740, align 4
  %742 = mul i32 %741, %668
  %743 = sub i32 %742, %45
  %744 = add i32 %lsr.iv, %743
  %745 = add i32 %744, -2
  %746 = sext i32 %745 to i64
  %747 = getelementptr float, float* %739, i64 %746
  %748 = load float, float* %747, align 4
  %749 = fadd reassoc ninf nsz float %748, %.21274.ph
  %750 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %737, i64 0, i32 2, i32 1
  %751 = load float*, float** %750, align 8
  %752 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %737, i64 0, i32 2, i32 0, i32 1
  %753 = load i32, i32* %752, align 4
  %754 = mul i32 %753, %668
  %755 = sub i32 %754, %45
  %756 = add i32 %lsr.iv, %755
  %757 = add i32 %756, -2
  %758 = sext i32 %757 to i64
  %759 = getelementptr float, float* %751, i64 %758
  %760 = load float, float* %759, align 4
  %761 = fadd reassoc ninf nsz float %760, %.21249.ph
  %762 = fadd reassoc ninf nsz float %.21.ph, 1.000000e+00
  br label %true_block274

true_block274:                                    ; preds = %true_block271, %true_block268, %true_block262
  %.22275.ph = phi float [ %.21274.ph, %true_block262 ], [ %.21274.ph, %true_block268 ], [ %749, %true_block271 ]
  %.22250.ph = phi float [ %.21249.ph, %true_block262 ], [ %.21249.ph, %true_block268 ], [ %761, %true_block271 ]
  %.22.ph = phi float [ %.21.ph, %true_block262 ], [ %.21.ph, %true_block268 ], [ %762, %true_block271 ]
  %763 = icmp sgt i32 %368, -1
  %or.cond427 = select i1 %673, i1 %763, i1 false
  br i1 %or.cond427, label %true_block280, label %true_block286

true_block280:                                    ; preds = %true_block274
  %764 = getelementptr inbounds i8, i8* %32, i64 12
  %765 = bitcast i8* %764 to i32*
  %766 = load i32, i32* %765, align 4
  %767 = icmp slt i32 %368, %766
  br i1 %767, label %true_block283, label %true_block286

true_block283:                                    ; preds = %true_block280
  %768 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %769 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %768, i64 0, i32 1, i32 1
  %770 = load float*, float** %769, align 8
  %771 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %768, i64 0, i32 1, i32 0, i32 1
  %772 = load i32, i32* %771, align 4
  %773 = mul i32 %772, %668
  %774 = add i32 %773, %368
  %775 = sext i32 %774 to i64
  %776 = getelementptr float, float* %770, i64 %775
  %777 = load float, float* %776, align 4
  %778 = fadd reassoc ninf nsz float %777, %.22275.ph
  %779 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %768, i64 0, i32 2, i32 1
  %780 = load float*, float** %779, align 8
  %781 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %768, i64 0, i32 2, i32 0, i32 1
  %782 = load i32, i32* %781, align 4
  %783 = mul i32 %782, %668
  %784 = add i32 %783, %368
  %785 = sext i32 %784 to i64
  %786 = getelementptr float, float* %780, i64 %785
  %787 = load float, float* %786, align 4
  %788 = fadd reassoc ninf nsz float %787, %.22250.ph
  %789 = fadd reassoc ninf nsz float %.22.ph, 1.000000e+00
  br label %true_block286

true_block286:                                    ; preds = %true_block283, %true_block280, %true_block274
  %.23276.ph = phi float [ %.22275.ph, %true_block274 ], [ %.22275.ph, %true_block280 ], [ %778, %true_block283 ]
  %.23251.ph = phi float [ %.22250.ph, %true_block274 ], [ %.22250.ph, %true_block280 ], [ %788, %true_block283 ]
  %.23.ph = phi float [ %.22.ph, %true_block274 ], [ %.22.ph, %true_block280 ], [ %789, %true_block283 ]
  %790 = icmp sgt i32 %370, -1
  %or.cond428 = select i1 %673, i1 %790, i1 false
  br i1 %or.cond428, label %true_block292, label %after_if297

true_block292:                                    ; preds = %true_block286
  %791 = getelementptr inbounds i8, i8* %32, i64 12
  %792 = bitcast i8* %791 to i32*
  %793 = load i32, i32* %792, align 4
  %794 = icmp slt i32 %370, %793
  br i1 %794, label %true_block295, label %after_if297

true_block295:                                    ; preds = %true_block292
  %795 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %796 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %795, i64 0, i32 1, i32 1
  %797 = load float*, float** %796, align 8
  %798 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %795, i64 0, i32 1, i32 0, i32 1
  %799 = load i32, i32* %798, align 4
  %800 = mul i32 %799, %668
  %801 = add i32 %800, %370
  %802 = sext i32 %801 to i64
  %803 = getelementptr float, float* %797, i64 %802
  %804 = load float, float* %803, align 4
  %805 = fadd reassoc ninf nsz float %804, %.23276.ph
  %806 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %795, i64 0, i32 2, i32 1
  %807 = load float*, float** %806, align 8
  %808 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %795, i64 0, i32 2, i32 0, i32 1
  %809 = load i32, i32* %808, align 4
  %810 = mul i32 %809, %668
  %811 = add i32 %810, %370
  %812 = sext i32 %811 to i64
  %813 = getelementptr float, float* %807, i64 %812
  %814 = load float, float* %813, align 4
  %815 = fadd reassoc ninf nsz float %814, %.23251.ph
  %816 = fadd reassoc ninf nsz float %.23.ph, 1.000000e+00
  br label %after_if297

after_if297:                                      ; preds = %true_block295, %true_block292, %true_block286, %after_if237
  %.24277 = phi float [ %805, %true_block295 ], [ %.23276.ph, %true_block292 ], [ %.23276.ph, %true_block286 ], [ %.19272, %after_if237 ]
  %.24252 = phi float [ %815, %true_block295 ], [ %.23251.ph, %true_block292 ], [ %.23251.ph, %true_block286 ], [ %.19247, %after_if237 ]
  %.24 = phi float [ %816, %true_block295 ], [ %.23.ph, %true_block292 ], [ %.23.ph, %true_block286 ], [ %.19, %after_if237 ]
  %817 = load float*, float** %23, align 8
  %818 = load i32, i32* %24, align 4
  %819 = sub i32 %818, %35
  %820 = mul i32 %819, %44
  %821 = add i32 %lsr.iv, %820
  %822 = add i32 %821, -2
  %823 = sext i32 %822 to i64
  %824 = getelementptr float, float* %817, i64 %823
  %825 = load float, float* %824, align 4
  %826 = fmul reassoc ninf nsz float %825, %.24277
  %827 = fadd reassoc ninf nsz float %826, %.24252
  %828 = fdiv reassoc ninf nsz float %827, %.24
  %829 = fadd reassoc ninf nsz float %828, %825
  %830 = load float*, float** %25, align 8
  %831 = load i32, i32* %26, align 4
  %832 = sub i32 %831, %35
  %833 = mul i32 %832, %44
  %834 = add i32 %lsr.iv, %833
  %835 = add i32 %834, -2
  %836 = sext i32 %835 to i64
  %837 = getelementptr float, float* %830, i64 %836
  store float %829, float* %837, align 4
  %838 = add nsw i32 %.0278561, 1
  %lsr.iv.next = add i32 %lsr.iv, 1
  %839 = add i32 %27, %lsr.iv.next
  %exitcond.not = icmp eq i32 %839, 2
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
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

; Function Attrs: argmemonly nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly nocallback nofree nounwind willreturn }
attributes #5 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
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
