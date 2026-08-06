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
define void @_ha_red_blue_diff_kernel_c704_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 4
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 5
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
define void @_ha_red_blue_diff_kernel_c704_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 1, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 2, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 2, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 3, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 3, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.lr.ph
  %.03995 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %104, %after_if9 ]
  %29 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.03995, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.03995
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.03995, 0
  %40 = icmp ne i32 %.03995, %36
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg57 = sext i1 %42 to i32
  %43 = add i32 %35, %.neg57
  %44 = mul i32 %43, %34
  %45 = mul i32 %34, -1
  %46 = mul i32 %45, %43
  %47 = add i32 %.03995, %46
  %48 = sdiv i32 %43, 2
  %49 = icmp slt i32 %43, 0
  %50 = shl nsw i32 %48, 1
  %51 = icmp ne i32 %50, %43
  %52 = and i1 %49, %51
  %.neg58.neg = zext i1 %52 to i32
  %.neg60 = sub nsw i32 %.neg58.neg, %48
  %.neg59 = shl i32 %.neg60, 1
  %53 = sdiv i32 %47, 2
  %54 = icmp slt i32 %47, 0
  %55 = shl i32 %53, 1
  %56 = icmp ne i32 %47, %55
  %57 = and i1 %54, %56
  %.neg61.neg = zext i1 %57 to i32
  %58 = add i32 %44, %55
  %59 = shl nuw nsw i32 %.neg61.neg, 1
  %60 = sub i32 %58, %59
  %61 = add i32 %60, 1
  %62 = sub i32 0, %43
  %63 = icmp eq i32 %.neg59, %62
  %.not = icmp eq i32 %60, %.03995
  %64 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  br i1 %63, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  br i1 %.not, label %true_block1, label %false_block2

false_block:                                      ; preds = %for_loop_body
  br i1 %.not, label %true_block4, label %false_block5

after_if:                                         ; preds = %false_block5, %true_block4, %false_block2, %true_block1
  %.038.in = phi i32* [ %73, %true_block1 ], [ %74, %false_block2 ], [ %75, %true_block4 ], [ %76, %false_block5 ]
  %.038 = load i32, i32* %.038.in, align 4
  %65 = load float*, float** %23, align 8
  %66 = load i32, i32* %24, align 4
  %67 = sub i32 %66, %34
  %68 = mul i32 %67, %43
  %69 = add i32 %.03995, %68
  %70 = sext i32 %69 to i64
  %71 = getelementptr float, float* %65, i64 %70
  %72 = load float, float* %71, align 4
  switch i32 %.038, label %false_block23 [
    i32 0, label %true_block7
    i32 2, label %true_block22
  ]

true_block1:                                      ; preds = %true_block
  %73 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 6
  br label %after_if

false_block2:                                     ; preds = %true_block
  %74 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 7
  br label %after_if

true_block4:                                      ; preds = %false_block
  %75 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 8
  br label %after_if

false_block5:                                     ; preds = %false_block
  %76 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 9
  br label %after_if

true_block7:                                      ; preds = %after_if
  %77 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 1
  %78 = load float*, float** %77, align 8
  %79 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 0, i32 1
  %80 = load i32, i32* %79, align 4
  %81 = sub i32 %80, %34
  %82 = mul i32 %81, %43
  %83 = add i32 %.03995, %82
  %84 = sext i32 %83 to i64
  %85 = getelementptr float, float* %78, i64 %84
  %86 = load float, float* %85, align 4
  %87 = icmp sgt i32 %43, 0
  br i1 %87, label %true_block10, label %after_if9

after_if9:                                        ; preds = %true_block70, %true_block67, %after_if66, %true_block58, %true_block55, %after_if54, %true_block34, %true_block31, %true_block25, %true_block22, %true_block19, %true_block16, %true_block10, %true_block7
  %.034 = phi float [ %86, %true_block19 ], [ %241, %true_block34 ], [ %.135, %true_block58 ], [ %.2, %true_block70 ], [ %86, %true_block10 ], [ %86, %true_block7 ], [ %86, %true_block16 ], [ %72, %true_block25 ], [ %72, %true_block22 ], [ %72, %true_block31 ], [ %.135, %after_if54 ], [ %.135, %true_block55 ], [ %.2, %after_if66 ], [ %.2, %true_block67 ]
  %.033 = phi float [ %167, %true_block19 ], [ %177, %true_block34 ], [ %321, %true_block58 ], [ %395, %true_block70 ], [ %72, %true_block10 ], [ %72, %true_block7 ], [ %72, %true_block16 ], [ %177, %true_block25 ], [ %177, %true_block22 ], [ %177, %true_block31 ], [ %72, %after_if54 ], [ %72, %true_block55 ], [ %72, %after_if66 ], [ %72, %true_block67 ]
  %88 = fsub reassoc ninf nsz float %.034, %72
  %89 = load float*, float** %25, align 8
  %90 = load i32, i32* %26, align 4
  %91 = sub i32 %90, %34
  %92 = mul i32 %91, %43
  %93 = add i32 %.03995, %92
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, float* %89, i64 %94
  store float %88, float* %95, align 4
  %96 = fsub reassoc ninf nsz float %.033, %72
  %97 = load float*, float** %27, align 8
  %98 = load i32, i32* %28, align 4
  %99 = sub i32 %98, %34
  %100 = mul i32 %99, %43
  %101 = add i32 %.03995, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %97, i64 %102
  store float %96, float* %103, align 4
  %104 = add nsw i32 %.03995, 1
  %exitcond.not = icmp eq i32 %19, %104
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %true_block7
  %105 = getelementptr inbounds i8, i8* %31, i64 8
  %106 = bitcast i8* %105 to i32*
  %107 = load i32, i32* %106, align 4
  %108 = add i32 %107, -1
  %109 = icmp slt i32 %43, %108
  %110 = icmp sgt i32 %47, 0
  %or.cond = select i1 %109, i1 %110, i1 false
  br i1 %or.cond, label %true_block16, label %after_if9

true_block16:                                     ; preds = %true_block10
  %111 = getelementptr inbounds i8, i8* %31, i64 12
  %112 = bitcast i8* %111 to i32*
  %113 = load i32, i32* %112, align 4
  %114 = add i32 %113, -1
  %115 = icmp slt i32 %47, %114
  br i1 %115, label %true_block19, label %after_if9

true_block19:                                     ; preds = %true_block16
  %116 = add nsw i32 %43, -1
  %117 = insertelement <2 x i32> poison, i32 %47, i64 0
  %118 = shufflevector <2 x i32> %117, <2 x i32> poison, <2 x i32> zeroinitializer
  %119 = add nsw <2 x i32> %118, <i32 1, i32 -1>
  %120 = mul i32 %66, %116
  %121 = add nuw nsw i32 %43, 1
  %122 = mul i32 %66, %121
  %123 = mul i32 %80, %116
  %124 = mul i32 %80, %121
  %125 = insertelement <2 x i32> poison, i32 %120, i64 0
  %126 = shufflevector <2 x i32> %125, <2 x i32> poison, <2 x i32> zeroinitializer
  %127 = add <2 x i32> %126, %119
  %128 = sext <2 x i32> %127 to <2 x i64>
  %129 = insertelement <2 x float*> poison, float* %65, i64 0
  %130 = shufflevector <2 x float*> %129, <2 x float*> poison, <2 x i32> zeroinitializer
  %131 = getelementptr float, <2 x float*> %130, <2 x i64> %128
  %132 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %131, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %133 = insertelement <2 x i32> poison, i32 %122, i64 0
  %134 = shufflevector <2 x i32> %133, <2 x i32> poison, <2 x i32> zeroinitializer
  %135 = shufflevector <2 x i32> %119, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %136 = add <2 x i32> %134, %135
  %137 = sext <2 x i32> %136 to <2 x i64>
  %138 = getelementptr float, <2 x float*> %130, <2 x i64> %137
  %139 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %138, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %140 = fsub reassoc ninf nsz <2 x float> %132, %139
  %141 = call <2 x float> @llvm.fabs.v2f32(<2 x float> %140)
  %142 = fadd reassoc ninf nsz <2 x float> %141, <float 1.000000e+00, float 1.000000e+00>
  %143 = fdiv reassoc ninf nsz <2 x float> <float 1.000000e+00, float 1.000000e+00>, %142
  %144 = insertelement <2 x i32> poison, i32 %123, i64 0
  %145 = shufflevector <2 x i32> %144, <2 x i32> poison, <2 x i32> zeroinitializer
  %146 = add <2 x i32> %145, %119
  %147 = sext <2 x i32> %146 to <2 x i64>
  %148 = insertelement <2 x float*> poison, float* %78, i64 0
  %149 = shufflevector <2 x float*> %148, <2 x float*> poison, <2 x i32> zeroinitializer
  %150 = getelementptr float, <2 x float*> %149, <2 x i64> %147
  %151 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %150, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %152 = insertelement <2 x i32> poison, i32 %124, i64 0
  %153 = shufflevector <2 x i32> %152, <2 x i32> poison, <2 x i32> zeroinitializer
  %154 = add <2 x i32> %153, %135
  %155 = sext <2 x i32> %154 to <2 x i64>
  %156 = getelementptr float, <2 x float*> %149, <2 x i64> %155
  %157 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %156, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %158 = fadd reassoc ninf nsz <2 x float> %132, %139
  %159 = fsub reassoc ninf nsz <2 x float> %151, %158
  %160 = fadd reassoc ninf nsz <2 x float> %159, %157
  %161 = fmul reassoc ninf nsz <2 x float> %160, %143
  %shift = shufflevector <2 x float> %161, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %162 = fadd reassoc ninf nsz <2 x float> %161, %shift
  %163 = extractelement <2 x float> %162, i64 0
  %shift96 = shufflevector <2 x float> %143, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %164 = fadd reassoc ninf nsz <2 x float> %143, %shift96
  %165 = extractelement <2 x float> %164, i64 0
  %factor82 = fmul reassoc ninf nsz float %165, 2.000000e+00
  %166 = fdiv reassoc ninf nsz float %163, %factor82
  %167 = fadd reassoc ninf nsz float %166, %72
  br label %after_if9

true_block22:                                     ; preds = %after_if
  %168 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 1
  %169 = load float*, float** %168, align 8
  %170 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 0, i32 1
  %171 = load i32, i32* %170, align 4
  %172 = sub i32 %171, %34
  %173 = mul i32 %172, %43
  %174 = add i32 %.03995, %173
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, float* %169, i64 %175
  %177 = load float, float* %176, align 4
  %178 = icmp sgt i32 %43, 0
  br i1 %178, label %true_block25, label %after_if9

false_block23:                                    ; preds = %after_if
  %.not64 = icmp eq i32 %61, %.03995
  br i1 %63, label %true_block37, label %false_block38

true_block25:                                     ; preds = %true_block22
  %179 = getelementptr inbounds i8, i8* %31, i64 8
  %180 = bitcast i8* %179 to i32*
  %181 = load i32, i32* %180, align 4
  %182 = add i32 %181, -1
  %183 = icmp slt i32 %43, %182
  %184 = icmp sgt i32 %47, 0
  %or.cond69 = select i1 %183, i1 %184, i1 false
  br i1 %or.cond69, label %true_block31, label %after_if9

true_block31:                                     ; preds = %true_block25
  %185 = getelementptr inbounds i8, i8* %31, i64 12
  %186 = bitcast i8* %185 to i32*
  %187 = load i32, i32* %186, align 4
  %188 = add i32 %187, -1
  %189 = icmp slt i32 %47, %188
  br i1 %189, label %true_block34, label %after_if9

true_block34:                                     ; preds = %true_block31
  %190 = add nsw i32 %43, -1
  %191 = insertelement <2 x i32> poison, i32 %47, i64 0
  %192 = shufflevector <2 x i32> %191, <2 x i32> poison, <2 x i32> zeroinitializer
  %193 = add nsw <2 x i32> %192, <i32 1, i32 -1>
  %194 = mul i32 %66, %190
  %195 = add nuw nsw i32 %43, 1
  %196 = mul i32 %66, %195
  %197 = mul i32 %171, %190
  %198 = mul i32 %171, %195
  %199 = insertelement <2 x i32> poison, i32 %194, i64 0
  %200 = shufflevector <2 x i32> %199, <2 x i32> poison, <2 x i32> zeroinitializer
  %201 = add <2 x i32> %200, %193
  %202 = sext <2 x i32> %201 to <2 x i64>
  %203 = insertelement <2 x float*> poison, float* %65, i64 0
  %204 = shufflevector <2 x float*> %203, <2 x float*> poison, <2 x i32> zeroinitializer
  %205 = getelementptr float, <2 x float*> %204, <2 x i64> %202
  %206 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %205, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %207 = insertelement <2 x i32> poison, i32 %196, i64 0
  %208 = shufflevector <2 x i32> %207, <2 x i32> poison, <2 x i32> zeroinitializer
  %209 = shufflevector <2 x i32> %193, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %210 = add <2 x i32> %208, %209
  %211 = sext <2 x i32> %210 to <2 x i64>
  %212 = getelementptr float, <2 x float*> %204, <2 x i64> %211
  %213 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %212, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %214 = fsub reassoc ninf nsz <2 x float> %206, %213
  %215 = call <2 x float> @llvm.fabs.v2f32(<2 x float> %214)
  %216 = fadd reassoc ninf nsz <2 x float> %215, <float 1.000000e+00, float 1.000000e+00>
  %217 = fdiv reassoc ninf nsz <2 x float> <float 1.000000e+00, float 1.000000e+00>, %216
  %218 = insertelement <2 x i32> poison, i32 %197, i64 0
  %219 = shufflevector <2 x i32> %218, <2 x i32> poison, <2 x i32> zeroinitializer
  %220 = add <2 x i32> %219, %193
  %221 = sext <2 x i32> %220 to <2 x i64>
  %222 = insertelement <2 x float*> poison, float* %169, i64 0
  %223 = shufflevector <2 x float*> %222, <2 x float*> poison, <2 x i32> zeroinitializer
  %224 = getelementptr float, <2 x float*> %223, <2 x i64> %221
  %225 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %224, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %226 = insertelement <2 x i32> poison, i32 %198, i64 0
  %227 = shufflevector <2 x i32> %226, <2 x i32> poison, <2 x i32> zeroinitializer
  %228 = add <2 x i32> %227, %209
  %229 = sext <2 x i32> %228 to <2 x i64>
  %230 = getelementptr float, <2 x float*> %223, <2 x i64> %229
  %231 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %230, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %232 = fadd reassoc ninf nsz <2 x float> %206, %213
  %233 = fsub reassoc ninf nsz <2 x float> %225, %232
  %234 = fadd reassoc ninf nsz <2 x float> %233, %231
  %235 = fmul reassoc ninf nsz <2 x float> %234, %217
  %shift97 = shufflevector <2 x float> %235, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %236 = fadd reassoc ninf nsz <2 x float> %235, %shift97
  %237 = extractelement <2 x float> %236, i64 0
  %shift98 = shufflevector <2 x float> %217, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %238 = fadd reassoc ninf nsz <2 x float> %217, %shift98
  %239 = extractelement <2 x float> %238, i64 0
  %factor = fmul reassoc ninf nsz float %239, 2.000000e+00
  %240 = fdiv reassoc ninf nsz float %237, %factor
  %241 = fadd reassoc ninf nsz float %240, %72
  br label %after_if9

true_block37:                                     ; preds = %false_block23
  br i1 %.not64, label %true_block40, label %false_block41

false_block38:                                    ; preds = %false_block23
  br i1 %.not64, label %true_block43, label %false_block44

after_if39:                                       ; preds = %false_block44, %true_block43, %false_block41, %true_block40
  %.026.in.in = phi i32* [ %242, %true_block40 ], [ %243, %false_block41 ], [ %244, %true_block43 ], [ %245, %false_block44 ]
  %.026.in = load i32, i32* %.026.in.in, align 4
  %.026 = icmp eq i32 %.026.in, 0
  br i1 %.026, label %true_block46, label %false_block47

true_block40:                                     ; preds = %true_block37
  %242 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 6
  br label %after_if39

false_block41:                                    ; preds = %true_block37
  %243 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 7
  br label %after_if39

true_block43:                                     ; preds = %false_block38
  %244 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 8
  br label %after_if39

false_block44:                                    ; preds = %false_block38
  %245 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 9
  br label %after_if39

true_block46:                                     ; preds = %after_if39
  %246 = icmp sgt i32 %47, 0
  br i1 %246, label %true_block49, label %after_if54

false_block47:                                    ; preds = %after_if39
  %247 = icmp sgt i32 %43, 0
  br i1 %247, label %true_block61, label %after_if66

true_block49:                                     ; preds = %true_block46
  %248 = getelementptr inbounds i8, i8* %31, i64 12
  %249 = bitcast i8* %248 to i32*
  %250 = load i32, i32* %249, align 4
  %251 = add i32 %250, -1
  %252 = icmp slt i32 %47, %251
  br i1 %252, label %true_block52, label %after_if54

true_block52:                                     ; preds = %true_block49
  %253 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 1
  %254 = load float*, float** %253, align 8
  %255 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 0, i32 1
  %256 = load i32, i32* %255, align 4
  %257 = sub i32 %256, %34
  %258 = mul i32 %257, %43
  %259 = add i32 %.03995, %258
  %260 = add i32 %259, -1
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, float* %254, i64 %261
  %263 = load float, float* %262, align 4
  %264 = add i32 %69, -1
  %265 = sext i32 %264 to i64
  %266 = getelementptr float, float* %65, i64 %265
  %267 = load float, float* %266, align 4
  %268 = add i32 %259, 1
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, float* %254, i64 %269
  %271 = load float, float* %270, align 4
  %272 = add i32 %69, 1
  %273 = sext i32 %272 to i64
  %274 = getelementptr float, float* %65, i64 %273
  %275 = load float, float* %274, align 4
  %276 = fadd reassoc ninf nsz float %263, %271
  %277 = fadd reassoc ninf nsz float %267, %275
  %278 = fsub reassoc ninf nsz float %276, %277
  %279 = fmul reassoc ninf nsz float %278, 5.000000e-01
  %280 = fadd reassoc ninf nsz float %279, %72
  br label %after_if54

after_if54:                                       ; preds = %true_block52, %true_block49, %true_block46
  %.135 = phi float [ %280, %true_block52 ], [ %72, %true_block46 ], [ %72, %true_block49 ]
  %281 = icmp sgt i32 %43, 0
  br i1 %281, label %true_block55, label %after_if9

true_block55:                                     ; preds = %after_if54
  %282 = getelementptr inbounds i8, i8* %31, i64 8
  %283 = bitcast i8* %282 to i32*
  %284 = load i32, i32* %283, align 4
  %285 = add i32 %284, -1
  %286 = icmp slt i32 %43, %285
  br i1 %286, label %true_block58, label %after_if9

true_block58:                                     ; preds = %true_block55
  %287 = add nsw i32 %43, -1
  %288 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 1
  %289 = load float*, float** %288, align 8
  %290 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 0, i32 1
  %291 = load i32, i32* %290, align 4
  %292 = mul i32 %291, %287
  %293 = sub i32 %292, %44
  %294 = add i32 %.03995, %293
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, float* %289, i64 %295
  %297 = load float, float* %296, align 4
  %298 = mul i32 %66, %287
  %299 = sub i32 %298, %44
  %300 = add i32 %.03995, %299
  %301 = sext i32 %300 to i64
  %302 = getelementptr float, float* %65, i64 %301
  %303 = load float, float* %302, align 4
  %304 = add nuw nsw i32 %43, 1
  %305 = mul i32 %291, %304
  %306 = sub i32 %305, %44
  %307 = add i32 %.03995, %306
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, float* %289, i64 %308
  %310 = load float, float* %309, align 4
  %311 = mul i32 %66, %304
  %312 = sub i32 %311, %44
  %313 = add i32 %.03995, %312
  %314 = sext i32 %313 to i64
  %315 = getelementptr float, float* %65, i64 %314
  %316 = load float, float* %315, align 4
  %317 = fadd reassoc ninf nsz float %297, %310
  %318 = fadd reassoc ninf nsz float %303, %316
  %319 = fsub reassoc ninf nsz float %317, %318
  %320 = fmul reassoc ninf nsz float %319, 5.000000e-01
  %321 = fadd reassoc ninf nsz float %320, %72
  br label %after_if9

true_block61:                                     ; preds = %false_block47
  %322 = getelementptr inbounds i8, i8* %31, i64 8
  %323 = bitcast i8* %322 to i32*
  %324 = load i32, i32* %323, align 4
  %325 = add i32 %324, -1
  %326 = icmp slt i32 %43, %325
  br i1 %326, label %true_block64, label %after_if66

true_block64:                                     ; preds = %true_block61
  %327 = add nsw i32 %43, -1
  %328 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 1
  %329 = load float*, float** %328, align 8
  %330 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 0, i32 1
  %331 = load i32, i32* %330, align 4
  %332 = mul i32 %331, %327
  %333 = sub i32 %332, %44
  %334 = add i32 %.03995, %333
  %335 = sext i32 %334 to i64
  %336 = getelementptr float, float* %329, i64 %335
  %337 = load float, float* %336, align 4
  %338 = mul i32 %66, %327
  %339 = sub i32 %338, %44
  %340 = add i32 %.03995, %339
  %341 = sext i32 %340 to i64
  %342 = getelementptr float, float* %65, i64 %341
  %343 = load float, float* %342, align 4
  %344 = add nuw nsw i32 %43, 1
  %345 = mul i32 %331, %344
  %346 = sub i32 %345, %44
  %347 = add i32 %.03995, %346
  %348 = sext i32 %347 to i64
  %349 = getelementptr float, float* %329, i64 %348
  %350 = load float, float* %349, align 4
  %351 = mul i32 %66, %344
  %352 = sub i32 %351, %44
  %353 = add i32 %.03995, %352
  %354 = sext i32 %353 to i64
  %355 = getelementptr float, float* %65, i64 %354
  %356 = load float, float* %355, align 4
  %357 = fadd reassoc ninf nsz float %337, %350
  %358 = fadd reassoc ninf nsz float %343, %356
  %359 = fsub reassoc ninf nsz float %357, %358
  %360 = fmul reassoc ninf nsz float %359, 5.000000e-01
  %361 = fadd reassoc ninf nsz float %360, %72
  br label %after_if66

after_if66:                                       ; preds = %true_block64, %true_block61, %false_block47
  %.2 = phi float [ %361, %true_block64 ], [ %72, %false_block47 ], [ %72, %true_block61 ]
  %362 = icmp sgt i32 %47, 0
  br i1 %362, label %true_block67, label %after_if9

true_block67:                                     ; preds = %after_if66
  %363 = getelementptr inbounds i8, i8* %31, i64 12
  %364 = bitcast i8* %363 to i32*
  %365 = load i32, i32* %364, align 4
  %366 = add i32 %365, -1
  %367 = icmp slt i32 %47, %366
  br i1 %367, label %true_block70, label %after_if9

true_block70:                                     ; preds = %true_block67
  %368 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 1
  %369 = load float*, float** %368, align 8
  %370 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 0, i32 1
  %371 = load i32, i32* %370, align 4
  %372 = sub i32 %371, %34
  %373 = mul i32 %372, %43
  %374 = add i32 %.03995, %373
  %375 = add i32 %374, -1
  %376 = sext i32 %375 to i64
  %377 = getelementptr float, float* %369, i64 %376
  %378 = load float, float* %377, align 4
  %379 = add i32 %69, -1
  %380 = sext i32 %379 to i64
  %381 = getelementptr float, float* %65, i64 %380
  %382 = load float, float* %381, align 4
  %383 = add i32 %374, 1
  %384 = sext i32 %383 to i64
  %385 = getelementptr float, float* %369, i64 %384
  %386 = load float, float* %385, align 4
  %387 = add i32 %69, 1
  %388 = sext i32 %387 to i64
  %389 = getelementptr float, float* %65, i64 %388
  %390 = load float, float* %389, align 4
  %391 = fadd reassoc ninf nsz float %378, %386
  %392 = fadd reassoc ninf nsz float %382, %390
  %393 = fsub reassoc ninf nsz float %391, %392
  %394 = fmul reassoc ninf nsz float %393, 5.000000e-01
  %395 = fadd reassoc ninf nsz float %394, %72
  br label %after_if9
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
