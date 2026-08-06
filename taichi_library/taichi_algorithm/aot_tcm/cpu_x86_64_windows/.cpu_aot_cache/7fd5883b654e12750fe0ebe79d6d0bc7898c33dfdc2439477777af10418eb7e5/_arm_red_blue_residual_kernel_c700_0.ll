; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext*, void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { i8*, %struct.LLVMRuntime*, i32, i64* }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager*], [1024 x %struct.NodeManager*], [1024 x i8*], i8*, %struct.RandState*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { i8*, i8*, i64 }
%struct.ListManager = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime* }
%struct.NodeManager = type { %struct.LLVMRuntime*, i32, i32, i32, i32, %struct.ListManager*, %struct.ListManager*, %struct.ListManager*, i32 }
%struct.RandState = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_arm_red_blue_residual_kernel_c700_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 4
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 5
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_arm_red_blue_residual_kernel_c700_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext* %context, %struct.RuntimeContext** %4, align 8
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext*, i8*, i32)* @function_body, void (%struct.RuntimeContext*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 8
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 9
  %29 = load i32, i32* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 1
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.02371 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %112, %after_if ]
  %37 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.02371, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.02371
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.02371, 0
  %48 = icmp ne i32 %.02371, %44
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg35 = sext i1 %50 to i32
  %51 = add i32 %43, %.neg35
  %52 = mul i32 %51, %42
  %53 = mul i32 %42, -1
  %54 = mul i32 %53, %51
  %55 = add i32 %.02371, %54
  %56 = sdiv i32 %51, 2
  %57 = icmp slt i32 %51, 0
  %58 = shl nsw i32 %56, 1
  %59 = icmp ne i32 %58, %51
  %60 = and i1 %57, %59
  %.neg36.neg = zext i1 %60 to i32
  %.neg38 = sub nsw i32 %.neg36.neg, %56
  %.neg37 = shl i32 %.neg38, 1
  %61 = sdiv i32 %55, 2
  %62 = icmp slt i32 %55, 0
  %63 = shl i32 %61, 1
  %64 = icmp ne i32 %55, %63
  %65 = and i1 %62, %64
  %.neg39.neg = zext i1 %65 to i32
  %66 = add i32 %52, %63
  %67 = shl nuw nsw i32 %.neg39.neg, 1
  %68 = sub i32 %66, %67
  %69 = add i32 %68, 1
  %70 = sub i32 0, %51
  %71 = icmp eq i32 %.neg37, %70
  %.not = icmp eq i32 %68, %.02371
  %72 = select i1 %.not, i32 %23, i32 %25
  %73 = select i1 %.not, i32 %27, i32 %29
  %74 = select i1 %71, i32 %72, i32 %73
  %75 = load float*, float** %31, align 8
  %76 = load i32, i32* %32, align 4
  %77 = mul i32 %51, %76
  %78 = sub i32 %76, %42
  %79 = mul i32 %78, %51
  %80 = add i32 %.02371, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %75, i64 %81
  %83 = load float, float* %82, align 4
  switch i32 %74, label %false_block14 [
    i32 0, label %true_block
    i32 2, label %true_block13
  ]

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %84 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %85 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %84, i64 0, i32 0, i32 1
  %86 = load float*, float** %85, align 8
  %87 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %84, i64 0, i32 0, i32 0, i32 1
  %88 = load i32, i32* %87, align 4
  %89 = sub i32 %88, %42
  %90 = mul i32 %89, %51
  %91 = add i32 %.02371, %90
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, float* %86, i64 %92
  %94 = load float, float* %93, align 4
  %95 = icmp sgt i32 %51, 0
  br i1 %95, label %true_block1, label %after_if

after_if:                                         ; preds = %true_block25, %true_block22, %true_block16, %false_block14, %true_block13, %true_block10, %true_block7, %true_block1, %true_block
  %.022 = phi float [ %94, %true_block10 ], [ %322, %true_block25 ], [ %94, %true_block1 ], [ %94, %true_block ], [ %94, %true_block7 ], [ %83, %true_block16 ], [ %83, %true_block13 ], [ %83, %true_block22 ], [ %.72, %false_block14 ]
  %.021 = phi float [ %175, %true_block10 ], [ %186, %true_block25 ], [ %83, %true_block1 ], [ %83, %true_block ], [ %83, %true_block7 ], [ %186, %true_block16 ], [ %186, %true_block13 ], [ %186, %true_block22 ], [ %.73, %false_block14 ]
  %96 = fsub reassoc ninf nsz float %.022, %83
  %97 = load float*, float** %33, align 8
  %98 = load i32, i32* %34, align 4
  %99 = sub i32 %98, %42
  %100 = mul i32 %99, %51
  %101 = add i32 %.02371, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %97, i64 %102
  store float %96, float* %103, align 4
  %104 = fsub reassoc ninf nsz float %.021, %83
  %105 = load float*, float** %35, align 8
  %106 = load i32, i32* %36, align 4
  %107 = sub i32 %106, %42
  %108 = mul i32 %107, %51
  %109 = add i32 %.02371, %108
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, float* %105, i64 %110
  store float %104, float* %111, align 4
  %112 = add nsw i32 %.02371, 1
  %exitcond.not = icmp eq i32 %19, %112
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block1:                                      ; preds = %true_block
  %113 = getelementptr inbounds i8, i8* %39, i64 8
  %114 = bitcast i8* %113 to i32*
  %115 = load i32, i32* %114, align 4
  %116 = add i32 %115, -1
  %117 = icmp slt i32 %51, %116
  %118 = icmp sgt i32 %55, 0
  %or.cond = select i1 %117, i1 %118, i1 false
  br i1 %or.cond, label %true_block7, label %after_if

true_block7:                                      ; preds = %true_block1
  %119 = getelementptr inbounds i8, i8* %39, i64 12
  %120 = bitcast i8* %119 to i32*
  %121 = load i32, i32* %120, align 4
  %122 = add i32 %121, -1
  %123 = icmp slt i32 %55, %122
  br i1 %123, label %true_block10, label %after_if

true_block10:                                     ; preds = %true_block7
  %124 = add nsw i32 %51, -1
  %125 = insertelement <2 x i32> poison, i32 %55, i64 0
  %126 = shufflevector <2 x i32> %125, <2 x i32> poison, <2 x i32> zeroinitializer
  %127 = add nsw <2 x i32> %126, <i32 1, i32 -1>
  %128 = mul i32 %124, %76
  %129 = add nuw nsw i32 %51, 1
  %130 = mul i32 %129, %76
  %131 = mul i32 %88, %124
  %132 = mul i32 %88, %129
  %133 = insertelement <2 x i32> poison, i32 %128, i64 0
  %134 = shufflevector <2 x i32> %133, <2 x i32> poison, <2 x i32> zeroinitializer
  %135 = add <2 x i32> %127, %134
  %136 = sext <2 x i32> %135 to <2 x i64>
  %137 = insertelement <2 x float*> poison, float* %75, i64 0
  %138 = shufflevector <2 x float*> %137, <2 x float*> poison, <2 x i32> zeroinitializer
  %139 = getelementptr float, <2 x float*> %138, <2 x i64> %136
  %140 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %139, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %141 = shufflevector <2 x i32> %127, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %142 = insertelement <2 x i32> poison, i32 %130, i64 0
  %143 = shufflevector <2 x i32> %142, <2 x i32> poison, <2 x i32> zeroinitializer
  %144 = add <2 x i32> %141, %143
  %145 = sext <2 x i32> %144 to <2 x i64>
  %146 = getelementptr float, <2 x float*> %138, <2 x i64> %145
  %147 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %146, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %148 = fsub reassoc ninf nsz <2 x float> %140, %147
  %149 = call <2 x float> @llvm.fabs.v2f32(<2 x float> %148)
  %150 = fadd reassoc ninf nsz <2 x float> %149, <float 1.000000e+00, float 1.000000e+00>
  %151 = fdiv reassoc ninf nsz <2 x float> <float 1.000000e+00, float 1.000000e+00>, %150
  %152 = insertelement <2 x i32> poison, i32 %131, i64 0
  %153 = shufflevector <2 x i32> %152, <2 x i32> poison, <2 x i32> zeroinitializer
  %154 = add <2 x i32> %153, %127
  %155 = sext <2 x i32> %154 to <2 x i64>
  %156 = insertelement <2 x float*> poison, float* %86, i64 0
  %157 = shufflevector <2 x float*> %156, <2 x float*> poison, <2 x i32> zeroinitializer
  %158 = getelementptr float, <2 x float*> %157, <2 x i64> %155
  %159 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %158, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %160 = insertelement <2 x i32> poison, i32 %132, i64 0
  %161 = shufflevector <2 x i32> %160, <2 x i32> poison, <2 x i32> zeroinitializer
  %162 = add <2 x i32> %161, %141
  %163 = sext <2 x i32> %162 to <2 x i64>
  %164 = getelementptr float, <2 x float*> %157, <2 x i64> %163
  %165 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %164, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %166 = fadd reassoc ninf nsz <2 x float> %140, %147
  %167 = fsub reassoc ninf nsz <2 x float> %159, %166
  %168 = fadd reassoc ninf nsz <2 x float> %167, %165
  %169 = fmul reassoc ninf nsz <2 x float> %168, %151
  %shift = shufflevector <2 x float> %169, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %170 = fadd reassoc ninf nsz <2 x float> %169, %shift
  %171 = extractelement <2 x float> %170, i64 0
  %shift74 = shufflevector <2 x float> %151, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %172 = fadd reassoc ninf nsz <2 x float> %151, %shift74
  %173 = extractelement <2 x float> %172, i64 0
  %factor61 = fmul reassoc ninf nsz float %173, 2.000000e+00
  %174 = fdiv reassoc ninf nsz float %171, %factor61
  %175 = fadd reassoc ninf nsz float %174, %83
  br label %after_if

true_block13:                                     ; preds = %for_loop_body
  %176 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %177 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %176, i64 0, i32 0, i32 1
  %178 = load float*, float** %177, align 8
  %179 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %176, i64 0, i32 0, i32 0, i32 1
  %180 = load i32, i32* %179, align 4
  %181 = sub i32 %180, %42
  %182 = mul i32 %181, %51
  %183 = add i32 %.02371, %182
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, float* %178, i64 %184
  %186 = load float, float* %185, align 4
  %187 = icmp sgt i32 %51, 0
  br i1 %187, label %true_block16, label %after_if

false_block14:                                    ; preds = %for_loop_body
  %.not42 = icmp eq i32 %69, %.02371
  %. = select i1 %.not42, i32 %23, i32 %25
  %.47 = select i1 %.not42, i32 %27, i32 %29
  %.014.in = select i1 %71, i32 %., i32 %.47
  %.014 = icmp eq i32 %.014.in, 0
  %188 = add i32 %55, -1
  %189 = tail call i32 @llvm.smax.i32(i32 %188, i32 0)
  %190 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %191 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %190, i64 0, i32 0, i32 1
  %192 = load float*, float** %191, align 8
  %193 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %190, i64 0, i32 0, i32 0, i32 1
  %194 = load i32, i32* %193, align 4
  %195 = mul i32 %194, %51
  %196 = add i32 %195, %189
  %197 = sext i32 %196 to i64
  %198 = getelementptr float, float* %192, i64 %197
  %199 = load float, float* %198, align 4
  %200 = add i32 %189, %77
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, float* %75, i64 %201
  %203 = load float, float* %202, align 4
  %204 = getelementptr inbounds i8, i8* %39, i64 12
  %205 = bitcast i8* %204 to i32*
  %206 = load i32, i32* %205, align 4
  %207 = add i32 %206, -1
  %208 = add i32 %55, 1
  %209 = tail call i32 @llvm.smin.i32(i32 %207, i32 %208)
  %210 = add i32 %209, %195
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %192, i64 %211
  %213 = load float, float* %212, align 4
  %214 = add i32 %209, %77
  %215 = sext i32 %214 to i64
  %216 = getelementptr float, float* %75, i64 %215
  %217 = load float, float* %216, align 4
  %218 = fadd reassoc ninf nsz float %199, %213
  %219 = fadd reassoc ninf nsz float %203, %217
  %220 = fsub reassoc ninf nsz float %218, %219
  %221 = fmul reassoc ninf nsz float %220, 5.000000e-01
  %222 = fadd reassoc ninf nsz float %221, %83
  %223 = add i32 %51, -1
  %224 = tail call i32 @llvm.smax.i32(i32 %223, i32 0)
  %225 = mul i32 %194, %224
  %226 = sub i32 %225, %52
  %227 = add i32 %.02371, %226
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, float* %192, i64 %228
  %230 = load float, float* %229, align 4
  %231 = mul i32 %224, %76
  %232 = sub i32 %231, %52
  %233 = add i32 %.02371, %232
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, float* %75, i64 %234
  %236 = load float, float* %235, align 4
  %237 = getelementptr inbounds i8, i8* %39, i64 8
  %238 = bitcast i8* %237 to i32*
  %239 = load i32, i32* %238, align 4
  %240 = add i32 %239, -1
  %241 = add i32 %51, 1
  %242 = tail call i32 @llvm.smin.i32(i32 %240, i32 %241)
  %243 = mul i32 %242, %194
  %244 = sub i32 %243, %52
  %245 = add i32 %.02371, %244
  %246 = sext i32 %245 to i64
  %247 = getelementptr float, float* %192, i64 %246
  %248 = load float, float* %247, align 4
  %249 = mul i32 %242, %76
  %250 = sub i32 %249, %52
  %251 = add i32 %.02371, %250
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, float* %75, i64 %252
  %254 = load float, float* %253, align 4
  %255 = fadd reassoc ninf nsz float %230, %248
  %256 = fadd reassoc ninf nsz float %236, %254
  %257 = fsub reassoc ninf nsz float %255, %256
  %258 = fmul reassoc ninf nsz float %257, 5.000000e-01
  %259 = fadd reassoc ninf nsz float %258, %83
  %.72 = select i1 %.014, float %222, float %259
  %.73 = select i1 %.014, float %259, float %222
  br label %after_if

true_block16:                                     ; preds = %true_block13
  %260 = getelementptr inbounds i8, i8* %39, i64 8
  %261 = bitcast i8* %260 to i32*
  %262 = load i32, i32* %261, align 4
  %263 = add i32 %262, -1
  %264 = icmp slt i32 %51, %263
  %265 = icmp sgt i32 %55, 0
  %or.cond48 = select i1 %264, i1 %265, i1 false
  br i1 %or.cond48, label %true_block22, label %after_if

true_block22:                                     ; preds = %true_block16
  %266 = getelementptr inbounds i8, i8* %39, i64 12
  %267 = bitcast i8* %266 to i32*
  %268 = load i32, i32* %267, align 4
  %269 = add i32 %268, -1
  %270 = icmp slt i32 %55, %269
  br i1 %270, label %true_block25, label %after_if

true_block25:                                     ; preds = %true_block22
  %271 = add nsw i32 %51, -1
  %272 = insertelement <2 x i32> poison, i32 %55, i64 0
  %273 = shufflevector <2 x i32> %272, <2 x i32> poison, <2 x i32> zeroinitializer
  %274 = add nsw <2 x i32> %273, <i32 1, i32 -1>
  %275 = mul i32 %271, %76
  %276 = add nuw nsw i32 %51, 1
  %277 = mul i32 %276, %76
  %278 = mul i32 %180, %271
  %279 = mul i32 %180, %276
  %280 = insertelement <2 x i32> poison, i32 %275, i64 0
  %281 = shufflevector <2 x i32> %280, <2 x i32> poison, <2 x i32> zeroinitializer
  %282 = add <2 x i32> %274, %281
  %283 = sext <2 x i32> %282 to <2 x i64>
  %284 = insertelement <2 x float*> poison, float* %75, i64 0
  %285 = shufflevector <2 x float*> %284, <2 x float*> poison, <2 x i32> zeroinitializer
  %286 = getelementptr float, <2 x float*> %285, <2 x i64> %283
  %287 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %286, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %288 = shufflevector <2 x i32> %274, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %289 = insertelement <2 x i32> poison, i32 %277, i64 0
  %290 = shufflevector <2 x i32> %289, <2 x i32> poison, <2 x i32> zeroinitializer
  %291 = add <2 x i32> %288, %290
  %292 = sext <2 x i32> %291 to <2 x i64>
  %293 = getelementptr float, <2 x float*> %285, <2 x i64> %292
  %294 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %293, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %295 = fsub reassoc ninf nsz <2 x float> %287, %294
  %296 = call <2 x float> @llvm.fabs.v2f32(<2 x float> %295)
  %297 = fadd reassoc ninf nsz <2 x float> %296, <float 1.000000e+00, float 1.000000e+00>
  %298 = fdiv reassoc ninf nsz <2 x float> <float 1.000000e+00, float 1.000000e+00>, %297
  %299 = insertelement <2 x i32> poison, i32 %278, i64 0
  %300 = shufflevector <2 x i32> %299, <2 x i32> poison, <2 x i32> zeroinitializer
  %301 = add <2 x i32> %300, %274
  %302 = sext <2 x i32> %301 to <2 x i64>
  %303 = insertelement <2 x float*> poison, float* %178, i64 0
  %304 = shufflevector <2 x float*> %303, <2 x float*> poison, <2 x i32> zeroinitializer
  %305 = getelementptr float, <2 x float*> %304, <2 x i64> %302
  %306 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %305, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %307 = insertelement <2 x i32> poison, i32 %279, i64 0
  %308 = shufflevector <2 x i32> %307, <2 x i32> poison, <2 x i32> zeroinitializer
  %309 = add <2 x i32> %308, %288
  %310 = sext <2 x i32> %309 to <2 x i64>
  %311 = getelementptr float, <2 x float*> %304, <2 x i64> %310
  %312 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %311, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %313 = fadd reassoc ninf nsz <2 x float> %287, %294
  %314 = fsub reassoc ninf nsz <2 x float> %306, %313
  %315 = fadd reassoc ninf nsz <2 x float> %314, %312
  %316 = fmul reassoc ninf nsz <2 x float> %315, %298
  %shift75 = shufflevector <2 x float> %316, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %317 = fadd reassoc ninf nsz <2 x float> %316, %shift75
  %318 = extractelement <2 x float> %317, i64 0
  %shift76 = shufflevector <2 x float> %298, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %319 = fadd reassoc ninf nsz <2 x float> %298, %shift76
  %320 = extractelement <2 x float> %319, i64 0
  %factor = fmul reassoc ninf nsz float %320, 2.000000e+00
  %321 = fdiv reassoc ninf nsz float %318, %factor
  %322 = fadd reassoc ninf nsz float %321, %83
  br label %after_if
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext**
  %.sroa.0.0.copyload = load %struct.RuntimeContext*, %struct.RuntimeContext** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.fabs.v2f32(<2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
