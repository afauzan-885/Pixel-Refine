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
define void @_arm_preprocess_and_green_interpolation_kernel_c698_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 8
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 8
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 12
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 11
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 32
  %27 = bitcast i8* %26 to i32*
  store i32 %22, i32* %27, align 4
  switch i32 %22, label %false_block5 [
    i32 0, label %true_block
    i32 1, label %true_block1
    i32 2, label %true_block4
  ]

true_block:                                       ; preds = %entry
  %28 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %28, i64 0, i32 3
  br label %after_if

after_if:                                         ; preds = %false_block5, %true_block4, %true_block1, %true_block
  %.022.in = phi float* [ %29, %true_block ], [ %44, %true_block1 ], [ %46, %true_block4 ], [ %48, %false_block5 ]
  %.022 = load float, float* %.022.in, align 4
  %30 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 16
  %34 = bitcast i8* %33 to float*
  store float %.022, float* %34, align 4
  %35 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %35, i64 0, i32 12
  %37 = load i32, i32* %36, align 4
  %38 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 36
  %42 = bitcast i8* %41 to i32*
  store i32 %37, i32* %42, align 4
  switch i32 %37, label %false_block14 [
    i32 0, label %true_block7
    i32 1, label %true_block10
    i32 2, label %true_block13
  ]

true_block1:                                      ; preds = %entry
  %43 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %43, i64 0, i32 4
  br label %after_if

true_block4:                                      ; preds = %entry
  %45 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %45, i64 0, i32 5
  br label %after_if

false_block5:                                     ; preds = %entry
  %47 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %47, i64 0, i32 6
  br label %after_if

true_block7:                                      ; preds = %after_if
  %49 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %50 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %49, i64 0, i32 3
  br label %after_if9

after_if9:                                        ; preds = %false_block14, %true_block13, %true_block10, %true_block7
  %.019.in = phi float* [ %50, %true_block7 ], [ %65, %true_block10 ], [ %67, %true_block13 ], [ %69, %false_block14 ]
  %.019 = load float, float* %.019.in, align 4
  %51 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %51, i64 0, i32 14
  %53 = load i8*, i8** %52, align 8
  %54 = getelementptr inbounds i8, i8* %53, i64 20
  %55 = bitcast i8* %54 to float*
  store float %.019, float* %55, align 4
  %56 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %56, i64 0, i32 13
  %58 = load i32, i32* %57, align 4
  %59 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %60 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %59, i64 0, i32 14
  %61 = load i8*, i8** %60, align 8
  %62 = getelementptr inbounds i8, i8* %61, i64 40
  %63 = bitcast i8* %62 to i32*
  store i32 %58, i32* %63, align 4
  switch i32 %58, label %false_block23 [
    i32 0, label %true_block16
    i32 1, label %true_block19
    i32 2, label %true_block22
  ]

true_block10:                                     ; preds = %after_if
  %64 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %65 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 4
  br label %after_if9

true_block13:                                     ; preds = %after_if
  %66 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %67 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %66, i64 0, i32 5
  br label %after_if9

false_block14:                                    ; preds = %after_if
  %68 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %69 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %68, i64 0, i32 6
  br label %after_if9

true_block16:                                     ; preds = %after_if9
  %70 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %71 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %70, i64 0, i32 3
  br label %after_if18

after_if18:                                       ; preds = %false_block23, %true_block22, %true_block19, %true_block16
  %.016.in = phi float* [ %71, %true_block16 ], [ %86, %true_block19 ], [ %88, %true_block22 ], [ %90, %false_block23 ]
  %.016 = load float, float* %.016.in, align 4
  %72 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %73 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %72, i64 0, i32 14
  %74 = load i8*, i8** %73, align 8
  %75 = getelementptr inbounds i8, i8* %74, i64 24
  %76 = bitcast i8* %75 to float*
  store float %.016, float* %76, align 4
  %77 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %78 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %77, i64 0, i32 14
  %79 = load i32, i32* %78, align 4
  %80 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %81 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %80, i64 0, i32 14
  %82 = load i8*, i8** %81, align 8
  %83 = getelementptr inbounds i8, i8* %82, i64 44
  %84 = bitcast i8* %83 to i32*
  store i32 %79, i32* %84, align 4
  switch i32 %79, label %false_block32 [
    i32 0, label %true_block25
    i32 1, label %true_block28
    i32 2, label %true_block31
  ]

true_block19:                                     ; preds = %after_if9
  %85 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %86 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %85, i64 0, i32 4
  br label %after_if18

true_block22:                                     ; preds = %after_if9
  %87 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %88 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %87, i64 0, i32 5
  br label %after_if18

false_block23:                                    ; preds = %after_if9
  %89 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %90 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %89, i64 0, i32 6
  br label %after_if18

true_block25:                                     ; preds = %after_if18
  %91 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %92 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %91, i64 0, i32 3
  br label %after_if27

after_if27:                                       ; preds = %false_block32, %true_block31, %true_block28, %true_block25
  %.013.in = phi float* [ %92, %true_block25 ], [ %127, %true_block28 ], [ %129, %true_block31 ], [ %131, %false_block32 ]
  %.013 = load float, float* %.013.in, align 4
  %93 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %94 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %93, i64 0, i32 14
  %95 = load i8*, i8** %94, align 8
  %96 = getelementptr inbounds i8, i8* %95, i64 28
  %97 = bitcast i8* %96 to float*
  store float %.013, float* %97, align 4
  %98 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %99 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %98, i64 0, i32 9
  %100 = load i32, i32* %99, align 4
  %101 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %102 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %101, i64 0, i32 14
  %103 = load i8*, i8** %102, align 8
  %104 = getelementptr inbounds i8, i8* %103, i64 48
  %105 = bitcast i8* %104 to i32*
  store i32 %100, i32* %105, align 4
  %106 = tail call i32 @llvm.smax.i32(i32 %100, i32 0)
  %107 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %108 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %107, i64 0, i32 10
  %109 = load i32, i32* %108, align 4
  %110 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %111 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %110, i64 0, i32 14
  %112 = load i8*, i8** %111, align 8
  %113 = getelementptr inbounds i8, i8* %112, i64 52
  %114 = bitcast i8* %113 to i32*
  store i32 %109, i32* %114, align 4
  %115 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %116 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %117 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %116, i64 0, i32 14
  %118 = load i8*, i8** %117, align 8
  %119 = getelementptr inbounds i8, i8* %118, i64 4
  %120 = bitcast i8* %119 to i32*
  store i32 %115, i32* %120, align 4
  %121 = mul i32 %115, %106
  %122 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %123 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %122, i64 0, i32 14
  %124 = bitcast i8** %123 to i32**
  %125 = load i32*, i32** %124, align 8
  store i32 %121, i32* %125, align 4
  ret void

true_block28:                                     ; preds = %after_if18
  %126 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %127 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %126, i64 0, i32 4
  br label %after_if27

true_block31:                                     ; preds = %after_if18
  %128 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %129 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %128, i64 0, i32 5
  br label %after_if27

false_block32:                                    ; preds = %after_if18
  %130 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %131 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %130, i64 0, i32 6
  br label %after_if27
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_arm_preprocess_and_green_interpolation_kernel_c698_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #2 {
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
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.012 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %100, %for_loop_body ]
  %27 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 4
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sdiv i32 %.012, %32
  %34 = mul i32 %33, %32
  %35 = xor i32 %32, %.012
  %36 = icmp slt i32 %35, 0
  %37 = icmp ne i32 %.012, 0
  %38 = icmp ne i32 %.012, %34
  %39 = and i1 %37, %36
  %40 = and i1 %39, %38
  %.neg4 = sext i1 %40 to i32
  %41 = add i32 %33, %.neg4
  %42 = mul i32 %32, -1
  %43 = mul i32 %42, %41
  %44 = add i32 %.012, %43
  %45 = load float*, float** %23, align 8
  %46 = load i32, i32* %24, align 4
  %47 = sub i32 %46, %32
  %48 = mul i32 %47, %41
  %49 = add i32 %.012, %48
  %50 = sext i32 %49 to i64
  %51 = getelementptr float, float* %45, i64 %50
  %52 = load float, float* %51, align 4
  %53 = getelementptr inbounds i8, i8* %29, i64 8
  %54 = bitcast i8* %53 to float*
  %55 = load float, float* %54, align 4
  %56 = fsub reassoc ninf nsz float %52, %55
  %57 = getelementptr inbounds i8, i8* %29, i64 12
  %58 = bitcast i8* %57 to float*
  %59 = load float, float* %58, align 4
  %60 = fmul reassoc ninf nsz float %56, %59
  %61 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %60, float 0.000000e+00)
  %62 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %61, float 1.000000e+00)
  %63 = insertelement <2 x i32> poison, i32 %44, i64 0
  %64 = insertelement <2 x i32> %63, i32 %41, i64 1
  %65 = sdiv <2 x i32> %64, <i32 2, i32 2>
  %66 = icmp slt <2 x i32> %64, zeroinitializer
  %67 = shl nsw <2 x i32> %65, <i32 1, i32 1>
  %68 = icmp ne <2 x i32> %67, %64
  %69 = and <2 x i1> %66, %68
  %70 = zext <2 x i1> %69 to <2 x i32>
  %71 = sub nsw <2 x i32> %70, %65
  %72 = shl <2 x i32> %71, <i32 1, i32 1>
  %73 = sub <2 x i32> zeroinitializer, %64
  %74 = icmp eq <2 x i32> %72, %73
  %75 = getelementptr inbounds i8, i8* %29, i64 16
  %76 = bitcast i8* %75 to float*
  %77 = load float, float* %76, align 4
  %78 = getelementptr inbounds i8, i8* %29, i64 20
  %79 = bitcast i8* %78 to float*
  %80 = load float, float* %79, align 4
  %81 = extractelement <2 x i1> %74, i64 0
  %82 = select reassoc ninf nsz i1 %81, float %77, float %80
  %83 = getelementptr inbounds i8, i8* %29, i64 24
  %84 = bitcast i8* %83 to float*
  %85 = load float, float* %84, align 4
  %86 = getelementptr inbounds i8, i8* %29, i64 28
  %87 = bitcast i8* %86 to float*
  %88 = load float, float* %87, align 4
  %89 = select reassoc ninf nsz i1 %81, float %85, float %88
  %90 = extractelement <2 x i1> %74, i64 1
  %91 = select reassoc ninf nsz i1 %90, float %82, float %89
  %92 = fmul reassoc ninf nsz float %91, %62
  %93 = load float*, float** %25, align 8
  %94 = load i32, i32* %26, align 4
  %95 = sub i32 %94, %32
  %96 = mul i32 %95, %41
  %97 = add i32 %.012, %96
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, float* %93, i64 %98
  store float %92, float* %99, align 4
  %100 = add nsw i32 %.012, 1
  %exitcond.not = icmp eq i32 %19, %100
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_arm_preprocess_and_green_interpolation_kernel_c698_0_kernel_2_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #2 {
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
  store void (%struct.RuntimeContext.6*, i8*, i32)* @function_body.1, void (%struct.RuntimeContext.6*, i8*, i32)** %5, align 8
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
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body.1(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.047108 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %91, %after_if3 ]
  %22 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  %27 = load i32, i32* %26, align 4
  %28 = sdiv i32 %.047108, %27
  %29 = mul i32 %28, %27
  %30 = xor i32 %27, %.047108
  %31 = icmp slt i32 %30, 0
  %32 = icmp ne i32 %.047108, 0
  %33 = icmp ne i32 %.047108, %29
  %34 = and i1 %32, %31
  %35 = and i1 %34, %33
  %.neg75 = sext i1 %35 to i32
  %36 = add i32 %28, %.neg75
  %37 = mul i32 %36, %27
  %38 = mul i32 %27, -1
  %39 = mul i32 %38, %36
  %40 = add i32 %.047108, %39
  %41 = insertelement <2 x i32> poison, i32 %40, i64 0
  %42 = insertelement <2 x i32> %41, i32 %36, i64 1
  %43 = sdiv <2 x i32> %42, <i32 2, i32 2>
  %44 = icmp slt <2 x i32> %42, zeroinitializer
  %45 = shl nsw <2 x i32> %43, <i32 1, i32 1>
  %46 = icmp ne <2 x i32> %45, %42
  %47 = and <2 x i1> %44, %46
  %48 = zext <2 x i1> %47 to <2 x i32>
  %49 = sub nsw <2 x i32> %48, %43
  %50 = shl <2 x i32> %49, <i32 1, i32 1>
  %51 = sub <2 x i32> zeroinitializer, %42
  %52 = icmp eq <2 x i32> %50, %51
  %53 = getelementptr inbounds i8, i8* %24, i64 32
  %54 = bitcast i8* %53 to i32*
  %55 = load i32, i32* %54, align 4
  %56 = getelementptr inbounds i8, i8* %24, i64 36
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = extractelement <2 x i1> %52, i64 0
  %60 = select i1 %59, i32 %55, i32 %58
  %61 = getelementptr inbounds i8, i8* %24, i64 40
  %62 = bitcast i8* %61 to i32*
  %63 = load i32, i32* %62, align 4
  %64 = getelementptr inbounds i8, i8* %24, i64 44
  %65 = bitcast i8* %64 to i32*
  %66 = load i32, i32* %65, align 4
  %67 = select i1 %59, i32 %63, i32 %66
  %68 = extractelement <2 x i1> %52, i64 1
  %69 = select i1 %68, i32 %60, i32 %67
  switch i32 %69, label %false_block2 [
    i32 3, label %true_block1
    i32 1, label %true_block1
  ]

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block1:                                      ; preds = %for_loop_body, %for_loop_body
  %70 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %71 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %70, i64 0, i32 1, i32 1
  %72 = load float*, float** %71, align 8
  %73 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %70, i64 0, i32 1, i32 0, i32 1
  %74 = load i32, i32* %73, align 4
  %75 = sub i32 %74, %27
  %76 = mul i32 %75, %36
  %77 = add i32 %.047108, %76
  %78 = sext i32 %77 to i64
  %79 = getelementptr float, float* %72, i64 %78
  %80 = load float, float* %79, align 4
  br label %after_if3

false_block2:                                     ; preds = %for_loop_body
  %81 = icmp sgt i32 %36, 1
  br i1 %81, label %true_block4, label %false_block14

after_if3:                                        ; preds = %after_if63, %true_block13, %true_block1
  %.sink119 = phi { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* [ %103, %true_block13 ], [ %284, %after_if63 ], [ %70, %true_block1 ]
  %.sink = phi float [ %185, %true_block13 ], [ %283, %after_if63 ], [ %80, %true_block1 ]
  %82 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink119, i64 0, i32 2, i32 1
  %83 = load float*, float** %82, align 8
  %84 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink119, i64 0, i32 2, i32 0, i32 1
  %85 = load i32, i32* %84, align 4
  %86 = sub i32 %85, %27
  %87 = mul i32 %86, %36
  %88 = add i32 %.047108, %87
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, float* %83, i64 %89
  store float %.sink, float* %90, align 4
  %91 = add nsw i32 %.047108, 1
  %exitcond.not = icmp eq i32 %19, %91
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block4:                                      ; preds = %false_block2
  %92 = getelementptr inbounds i8, i8* %24, i64 48
  %93 = bitcast i8* %92 to i32*
  %94 = load i32, i32* %93, align 4
  %95 = add i32 %94, -2
  %96 = icmp slt i32 %36, %95
  %97 = icmp sgt i32 %40, 1
  %or.cond = select i1 %96, i1 %97, i1 false
  br i1 %or.cond, label %true_block10, label %false_block14.thread

true_block10:                                     ; preds = %true_block4
  %98 = getelementptr inbounds i8, i8* %24, i64 52
  %99 = bitcast i8* %98 to i32*
  %100 = load i32, i32* %99, align 4
  %101 = add i32 %100, -2
  %102 = icmp slt i32 %40, %101
  br i1 %102, label %true_block13, label %false_block14.thread

true_block13:                                     ; preds = %true_block10
  %103 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %104 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %103, i64 0, i32 1, i32 1
  %105 = load float*, float** %104, align 8
  %106 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %103, i64 0, i32 1, i32 0, i32 1
  %107 = load i32, i32* %106, align 4
  %108 = sub i32 %107, %27
  %109 = mul i32 %108, %36
  %110 = add i32 %.047108, %109
  %111 = add i32 %110, -1
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, float* %105, i64 %112
  %114 = load float, float* %113, align 4
  %115 = add i32 %110, 1
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %105, i64 %116
  %118 = load float, float* %117, align 4
  %119 = fsub reassoc ninf nsz float %114, %118
  %120 = tail call float @llvm.fabs.f32(float %119)
  %121 = sext i32 %110 to i64
  %122 = getelementptr float, float* %105, i64 %121
  %123 = load float, float* %122, align 4
  %factor = fmul reassoc ninf nsz float %123, 2.000000e+00
  %124 = add i32 %110, -2
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %105, i64 %125
  %127 = load float, float* %126, align 4
  %128 = add i32 %110, 2
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %105, i64 %129
  %131 = load float, float* %130, align 4
  %132 = fadd reassoc ninf nsz float %127, %131
  %133 = fsub reassoc ninf nsz float %factor, %132
  %134 = tail call float @llvm.fabs.f32(float %133)
  %135 = fadd reassoc ninf nsz float %134, %120
  %136 = add nsw i32 %36, -1
  %137 = mul i32 %107, %136
  %138 = sub i32 %137, %37
  %139 = add i32 %.047108, %138
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %105, i64 %140
  %142 = load float, float* %141, align 4
  %143 = add nuw nsw i32 %36, 1
  %144 = mul i32 %107, %143
  %145 = sub i32 %144, %37
  %146 = add i32 %.047108, %145
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %105, i64 %147
  %149 = load float, float* %148, align 4
  %150 = fsub reassoc ninf nsz float %142, %149
  %151 = tail call float @llvm.fabs.f32(float %150)
  %152 = add nsw i32 %36, -2
  %153 = mul i32 %107, %152
  %154 = sub i32 %153, %37
  %155 = add i32 %.047108, %154
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, float* %105, i64 %156
  %158 = load float, float* %157, align 4
  %159 = add nuw i32 %36, 2
  %160 = mul i32 %107, %159
  %161 = sub i32 %160, %37
  %162 = add i32 %.047108, %161
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %105, i64 %163
  %165 = load float, float* %164, align 4
  %166 = fadd reassoc ninf nsz float %158, %165
  %167 = fsub reassoc ninf nsz float %factor, %166
  %168 = tail call float @llvm.fabs.f32(float %167)
  %169 = fadd reassoc ninf nsz float %168, %151
  %170 = fmul reassoc ninf nsz float %135, %135
  %171 = fmul reassoc ninf nsz float %169, %169
  %172 = fadd reassoc ninf nsz float %170, 0x3EB0C6F7A0000000
  %173 = fadd reassoc ninf nsz float %172, %171
  %174 = fadd reassoc ninf nsz float %118, %114
  %175 = fmul reassoc ninf nsz float %174, 5.000000e-01
  %176 = fmul reassoc ninf nsz float %133, 2.500000e-01
  %177 = fadd reassoc ninf nsz float %176, %175
  %178 = fadd reassoc ninf nsz float %149, %142
  %179 = fmul reassoc ninf nsz float %178, 5.000000e-01
  %180 = fmul reassoc ninf nsz float %167, 2.500000e-01
  %181 = fadd reassoc ninf nsz float %180, %179
  %182 = fsub reassoc ninf nsz float %177, %181
  %183 = fmul reassoc ninf nsz float %171, %182
  %184 = fdiv reassoc ninf nsz float %183, %173
  %185 = fadd reassoc ninf nsz float %184, %181
  br label %after_if3

false_block14.thread:                             ; preds = %true_block10, %true_block4
  %186 = add nsw i32 %36, -1
  br label %true_block16

false_block14:                                    ; preds = %false_block2
  %187 = add i32 %36, -1
  %188 = icmp sgt i32 %187, -1
  br i1 %188, label %false_block14.true_block16_crit_edge, label %after_if27

false_block14.true_block16_crit_edge:             ; preds = %false_block14
  %.phi.trans.insert = getelementptr inbounds i8, i8* %24, i64 48
  %.phi.trans.insert109 = bitcast i8* %.phi.trans.insert to i32*
  %.pre = load i32, i32* %.phi.trans.insert109, align 4
  br label %true_block16

true_block16:                                     ; preds = %false_block14.true_block16_crit_edge, %false_block14.thread
  %189 = phi i32 [ %94, %false_block14.thread ], [ %.pre, %false_block14.true_block16_crit_edge ]
  %190 = phi i32 [ %186, %false_block14.thread ], [ %187, %false_block14.true_block16_crit_edge ]
  %191 = icmp slt i32 %190, %189
  %192 = icmp sgt i32 %40, -1
  %or.cond93 = select i1 %191, i1 %192, i1 false
  br i1 %or.cond93, label %true_block22, label %after_if27

true_block22:                                     ; preds = %true_block16
  %193 = getelementptr inbounds i8, i8* %24, i64 52
  %194 = bitcast i8* %193 to i32*
  %195 = load i32, i32* %194, align 4
  %196 = icmp slt i32 %40, %195
  br i1 %196, label %true_block25, label %after_if27

true_block25:                                     ; preds = %true_block22
  %197 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %198 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %197, i64 0, i32 1, i32 1
  %199 = load float*, float** %198, align 8
  %200 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %197, i64 0, i32 1, i32 0, i32 1
  %201 = load i32, i32* %200, align 4
  %202 = mul i32 %201, %190
  %203 = sub i32 %202, %37
  %204 = add i32 %.047108, %203
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %199, i64 %205
  %207 = load float, float* %206, align 4
  %208 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %207, i64 0
  br label %after_if27

after_if27:                                       ; preds = %true_block25, %true_block22, %true_block16, %false_block14
  %209 = phi <2 x float> [ %208, %true_block25 ], [ zeroinitializer, %true_block22 ], [ zeroinitializer, %false_block14 ], [ zeroinitializer, %true_block16 ]
  %210 = add i32 %36, 1
  %211 = icmp sgt i32 %210, -1
  br i1 %211, label %true_block28, label %after_if39

true_block28:                                     ; preds = %after_if27
  %212 = getelementptr inbounds i8, i8* %24, i64 48
  %213 = bitcast i8* %212 to i32*
  %214 = load i32, i32* %213, align 4
  %215 = icmp slt i32 %210, %214
  %216 = icmp sgt i32 %40, -1
  %or.cond94 = select i1 %215, i1 %216, i1 false
  br i1 %or.cond94, label %true_block34, label %after_if39

true_block34:                                     ; preds = %true_block28
  %217 = getelementptr inbounds i8, i8* %24, i64 52
  %218 = bitcast i8* %217 to i32*
  %219 = load i32, i32* %218, align 4
  %220 = icmp slt i32 %40, %219
  br i1 %220, label %true_block37, label %after_if39

true_block37:                                     ; preds = %true_block34
  %221 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %222 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %221, i64 0, i32 1, i32 1
  %223 = load float*, float** %222, align 8
  %224 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %221, i64 0, i32 1, i32 0, i32 1
  %225 = load i32, i32* %224, align 4
  %226 = mul i32 %225, %210
  %227 = sub i32 %226, %37
  %228 = add i32 %.047108, %227
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %223, i64 %229
  %231 = load float, float* %230, align 4
  %232 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %231, i64 0
  %233 = fadd reassoc ninf nsz <2 x float> %232, %209
  br label %after_if39

after_if39:                                       ; preds = %true_block37, %true_block34, %true_block28, %after_if27
  %234 = phi <2 x float> [ %233, %true_block37 ], [ %209, %true_block34 ], [ %209, %after_if27 ], [ %209, %true_block28 ]
  %235 = add i32 %40, -1
  %236 = icmp sgt i32 %36, -1
  br i1 %236, label %true_block40, label %after_if63

true_block40:                                     ; preds = %after_if39
  %237 = getelementptr inbounds i8, i8* %24, i64 48
  %238 = bitcast i8* %237 to i32*
  %239 = load i32, i32* %238, align 4
  %240 = icmp slt i32 %36, %239
  %241 = icmp sgt i32 %235, -1
  %or.cond95 = select i1 %240, i1 %241, i1 false
  br i1 %or.cond95, label %true_block46, label %true_block52

true_block46:                                     ; preds = %true_block40
  %242 = getelementptr inbounds i8, i8* %24, i64 52
  %243 = bitcast i8* %242 to i32*
  %244 = load i32, i32* %243, align 4
  %245 = icmp slt i32 %235, %244
  br i1 %245, label %true_block49, label %true_block52

true_block49:                                     ; preds = %true_block46
  %246 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %247 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %246, i64 0, i32 1, i32 1
  %248 = load float*, float** %247, align 8
  %249 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %246, i64 0, i32 1, i32 0, i32 1
  %250 = load i32, i32* %249, align 4
  %251 = sub i32 %250, %27
  %252 = mul i32 %251, %36
  %253 = add i32 %.047108, %252
  %254 = add i32 %253, -1
  %255 = sext i32 %254 to i64
  %256 = getelementptr float, float* %248, i64 %255
  %257 = load float, float* %256, align 4
  %258 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %257, i64 0
  %259 = fadd reassoc ninf nsz <2 x float> %258, %234
  br label %true_block52

true_block52:                                     ; preds = %true_block49, %true_block46, %true_block40
  %260 = phi <2 x float> [ %234, %true_block40 ], [ %234, %true_block46 ], [ %259, %true_block49 ]
  %261 = add i32 %40, 1
  %262 = icmp sgt i32 %261, -1
  %or.cond96 = select i1 %240, i1 %262, i1 false
  br i1 %or.cond96, label %true_block58, label %after_if63

true_block58:                                     ; preds = %true_block52
  %263 = getelementptr inbounds i8, i8* %24, i64 52
  %264 = bitcast i8* %263 to i32*
  %265 = load i32, i32* %264, align 4
  %266 = icmp slt i32 %261, %265
  br i1 %266, label %true_block61, label %after_if63

true_block61:                                     ; preds = %true_block58
  %267 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %268 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %267, i64 0, i32 1, i32 1
  %269 = load float*, float** %268, align 8
  %270 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %267, i64 0, i32 1, i32 0, i32 1
  %271 = load i32, i32* %270, align 4
  %272 = sub i32 %271, %27
  %273 = mul i32 %272, %36
  %274 = add i32 %.047108, %273
  %275 = add i32 %274, 1
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, float* %269, i64 %276
  %278 = load float, float* %277, align 4
  %279 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %278, i64 0
  %280 = fadd reassoc ninf nsz <2 x float> %279, %260
  br label %after_if63

after_if63:                                       ; preds = %true_block61, %true_block58, %true_block52, %after_if39
  %281 = phi <2 x float> [ %280, %true_block61 ], [ %260, %true_block58 ], [ %260, %true_block52 ], [ %234, %after_if39 ]
  %shift = shufflevector <2 x float> %281, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %282 = fdiv reassoc ninf nsz <2 x float> %281, %shift
  %283 = extractelement <2 x float> %282, i64 0
  %284 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %21, align 8
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
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
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #1

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
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
