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
define void @_bilinear_demosaice_fused_kernel_c698_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 8
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 32
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 36
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 11
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 8
  %27 = bitcast i8* %26 to i32*
  store i32 %22, i32* %27, align 4
  switch i32 %22, label %false_block5 [
    i32 0, label %true_block
    i32 1, label %true_block1
    i32 2, label %true_block4
  ]

true_block:                                       ; preds = %entry
  %28 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %28, i64 0, i32 3
  br label %after_if

after_if:                                         ; preds = %false_block5, %true_block4, %true_block1, %true_block
  %.022.in = phi float* [ %29, %true_block ], [ %44, %true_block1 ], [ %46, %true_block4 ], [ %48, %false_block5 ]
  %.022 = load float, float* %.022.in, align 4
  %30 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 40
  %34 = bitcast i8* %33 to float*
  store float %.022, float* %34, align 4
  %35 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %35, i64 0, i32 12
  %37 = load i32, i32* %36, align 4
  %38 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 12
  %42 = bitcast i8* %41 to i32*
  store i32 %37, i32* %42, align 4
  switch i32 %37, label %false_block14 [
    i32 0, label %true_block7
    i32 1, label %true_block10
    i32 2, label %true_block13
  ]

true_block1:                                      ; preds = %entry
  %43 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %43, i64 0, i32 4
  br label %after_if

true_block4:                                      ; preds = %entry
  %45 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %45, i64 0, i32 5
  br label %after_if

false_block5:                                     ; preds = %entry
  %47 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %47, i64 0, i32 6
  br label %after_if

true_block7:                                      ; preds = %after_if
  %49 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %50 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %49, i64 0, i32 3
  br label %after_if9

after_if9:                                        ; preds = %false_block14, %true_block13, %true_block10, %true_block7
  %.019.in = phi float* [ %50, %true_block7 ], [ %65, %true_block10 ], [ %67, %true_block13 ], [ %69, %false_block14 ]
  %.019 = load float, float* %.019.in, align 4
  %51 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %51, i64 0, i32 14
  %53 = load i8*, i8** %52, align 8
  %54 = getelementptr inbounds i8, i8* %53, i64 44
  %55 = bitcast i8* %54 to float*
  store float %.019, float* %55, align 4
  %56 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %56, i64 0, i32 13
  %58 = load i32, i32* %57, align 4
  %59 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %60 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %59, i64 0, i32 14
  %61 = load i8*, i8** %60, align 8
  %62 = getelementptr inbounds i8, i8* %61, i64 16
  %63 = bitcast i8* %62 to i32*
  store i32 %58, i32* %63, align 4
  switch i32 %58, label %false_block23 [
    i32 0, label %true_block16
    i32 1, label %true_block19
    i32 2, label %true_block22
  ]

true_block10:                                     ; preds = %after_if
  %64 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %65 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 4
  br label %after_if9

true_block13:                                     ; preds = %after_if
  %66 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %67 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %66, i64 0, i32 5
  br label %after_if9

false_block14:                                    ; preds = %after_if
  %68 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %69 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %68, i64 0, i32 6
  br label %after_if9

true_block16:                                     ; preds = %after_if9
  %70 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %71 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %70, i64 0, i32 3
  br label %after_if18

after_if18:                                       ; preds = %false_block23, %true_block22, %true_block19, %true_block16
  %.016.in = phi float* [ %71, %true_block16 ], [ %86, %true_block19 ], [ %88, %true_block22 ], [ %90, %false_block23 ]
  %.016 = load float, float* %.016.in, align 4
  %72 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %73 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %72, i64 0, i32 14
  %74 = load i8*, i8** %73, align 8
  %75 = getelementptr inbounds i8, i8* %74, i64 48
  %76 = bitcast i8* %75 to float*
  store float %.016, float* %76, align 4
  %77 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %78 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %77, i64 0, i32 14
  %79 = load i32, i32* %78, align 4
  %80 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %81 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %80, i64 0, i32 14
  %82 = load i8*, i8** %81, align 8
  %83 = getelementptr inbounds i8, i8* %82, i64 20
  %84 = bitcast i8* %83 to i32*
  store i32 %79, i32* %84, align 4
  switch i32 %79, label %false_block32 [
    i32 0, label %true_block25
    i32 1, label %true_block28
    i32 2, label %true_block31
  ]

true_block19:                                     ; preds = %after_if9
  %85 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %86 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %85, i64 0, i32 4
  br label %after_if18

true_block22:                                     ; preds = %after_if9
  %87 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %88 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %87, i64 0, i32 5
  br label %after_if18

false_block23:                                    ; preds = %after_if9
  %89 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %90 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %89, i64 0, i32 6
  br label %after_if18

true_block25:                                     ; preds = %after_if18
  %91 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %92 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %91, i64 0, i32 3
  br label %after_if27

after_if27:                                       ; preds = %false_block32, %true_block31, %true_block28, %true_block25
  %.013.in = phi float* [ %92, %true_block25 ], [ %127, %true_block28 ], [ %129, %true_block31 ], [ %131, %false_block32 ]
  %.013 = load float, float* %.013.in, align 4
  %93 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %94 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %93, i64 0, i32 14
  %95 = load i8*, i8** %94, align 8
  %96 = getelementptr inbounds i8, i8* %95, i64 52
  %97 = bitcast i8* %96 to float*
  store float %.013, float* %97, align 4
  %98 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %99 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %98, i64 0, i32 9
  %100 = load i32, i32* %99, align 4
  %101 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %102 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %101, i64 0, i32 14
  %103 = load i8*, i8** %102, align 8
  %104 = getelementptr inbounds i8, i8* %103, i64 24
  %105 = bitcast i8* %104 to i32*
  store i32 %100, i32* %105, align 4
  %106 = tail call i32 @llvm.smax.i32(i32 %100, i32 0)
  %107 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %108 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %107, i64 0, i32 10
  %109 = load i32, i32* %108, align 4
  %110 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %6, align 8
  %111 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %110, i64 0, i32 14
  %112 = load i8*, i8** %111, align 8
  %113 = getelementptr inbounds i8, i8* %112, i64 28
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
  %126 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %127 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %126, i64 0, i32 4
  br label %after_if27

true_block31:                                     ; preds = %after_if18
  %128 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %129 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %128, i64 0, i32 5
  br label %after_if27

false_block32:                                    ; preds = %after_if18
  %130 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %131 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %130, i64 0, i32 6
  br label %after_if27
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_bilinear_demosaice_fused_kernel_c698_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #2 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %23 = load float*, float** %22, align 8
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr float, float* %23, i64 1
  %27 = getelementptr float, float* %23, i64 2
  %28 = sext i32 %25 to i64
  %29 = getelementptr float, float* %23, i64 %28
  %30 = add i32 %25, 1
  %31 = sext i32 %30 to i64
  %32 = getelementptr float, float* %23, i64 %31
  %33 = add i32 %25, 2
  %34 = sext i32 %33 to i64
  %35 = getelementptr float, float* %23, i64 %34
  %36 = shl i32 %25, 1
  %37 = sext i32 %36 to i64
  %38 = getelementptr float, float* %23, i64 %37
  %39 = getelementptr float, float* %38, i64 1
  %40 = add i32 %36, 2
  %41 = sext i32 %40 to i64
  %42 = getelementptr float, float* %23, i64 %41
  %43 = icmp slt i32 %17, %19
  br i1 %43, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %47 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 2
  %49 = sub i32 1, %17
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if21, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %49, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if21 ]
  %.02857 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %316, %after_if21 ]
  %50 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %51 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %50, i64 0, i32 14
  %52 = load i8*, i8** %51, align 8
  %53 = getelementptr inbounds i8, i8* %52, i64 4
  %54 = bitcast i8* %53 to i32*
  %55 = load i32, i32* %54, align 4
  %56 = sdiv i32 %.02857, %55
  %57 = mul i32 %56, %55
  %58 = xor i32 %55, %.02857
  %59 = icmp slt i32 %58, 0
  %60 = icmp ne i32 %.02857, 0
  %61 = icmp ne i32 %.02857, %57
  %62 = and i1 %60, %59
  %63 = and i1 %62, %61
  %.neg29 = sext i1 %63 to i32
  %64 = add i32 %56, %.neg29
  %65 = mul i32 %64, %55
  %66 = mul i32 %55, -1
  %67 = mul i32 %66, %64
  %68 = add i32 %.02857, %67
  %69 = sdiv i32 %64, 2
  %70 = icmp slt i32 %64, 0
  %71 = shl nsw i32 %69, 1
  %72 = icmp ne i32 %71, %64
  %73 = and i1 %70, %72
  %.neg30.neg = zext i1 %73 to i32
  %.neg32 = sub nsw i32 %.neg30.neg, %69
  %.neg31 = shl i32 %.neg32, 1
  %74 = add i32 %.neg31, %64
  %75 = sdiv i32 %68, 2
  %76 = icmp slt i32 %68, 0
  %77 = shl i32 %75, 1
  %78 = icmp ne i32 %68, %77
  %79 = and i1 %76, %78
  %.neg33.neg = zext i1 %79 to i32
  %80 = shl nuw nsw i32 %.neg33.neg, 1
  %81 = sub i32 %80, %65
  %82 = sub i32 %81, %77
  %83 = add i32 %.02857, %82
  %84 = add i32 %65, %77
  %85 = sub i32 %84, %80
  %86 = add i32 %85, 1
  %87 = icmp eq i32 %74, 0
  %.not = icmp eq i32 %85, %.02857
  %spec.select = select i1 %.not, i64 8, i64 12
  %spec.select59 = select i1 %.not, i64 16, i64 20
  %.sink = select i1 %87, i64 %spec.select, i64 %spec.select59
  %88 = getelementptr inbounds i8, i8* %52, i64 %.sink
  %.027.in = bitcast i8* %88 to i32*
  %.027 = load i32, i32* %.027.in, align 4
  %89 = add i32 %64, -1
  %90 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %91 = getelementptr inbounds i8, i8* %52, i64 24
  %92 = bitcast i8* %91 to i32*
  %93 = load i32, i32* %92, align 4
  %94 = add i32 %93, -1
  %95 = add i32 %64, 1
  %96 = tail call i32 @llvm.smin.i32(i32 %94, i32 %95)
  %97 = add i32 %68, -1
  %98 = getelementptr inbounds i8, i8* %52, i64 28
  %99 = bitcast i8* %98 to i32*
  %100 = load i32, i32* %99, align 4
  %101 = add i32 %100, -1
  %102 = add i32 %68, 1
  %103 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %104 = tail call i32 @llvm.smin.i32(i32 %101, i32 %102)
  %.not36 = icmp eq i32 %64, 0
  %105 = sub i32 1, %74
  %.not37 = icmp eq i32 %64, %94
  %.024 = select i1 %.not37, i32 %74, i32 %105
  %.not38 = icmp eq i32 %.02857, %65
  %106 = add i32 %lsr.iv, %85
  %.not39 = icmp eq i32 %68, %101
  %.022 = select i1 %.not39, i32 %83, i32 %106
  %107 = load float*, float** %44, align 8
  %108 = load i32, i32* %45, align 4
  %109 = mul i32 %108, %64
  %110 = sub i32 %108, %55
  %111 = mul i32 %110, %64
  %112 = add i32 %.02857, %111
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %107, i64 %113
  %115 = load float, float* %114, align 4
  %116 = getelementptr inbounds i8, i8* %52, i64 32
  %117 = bitcast i8* %116 to float*
  %118 = load float, float* %117, align 4
  %119 = fsub reassoc ninf nsz float %115, %118
  %120 = getelementptr inbounds i8, i8* %52, i64 36
  %121 = bitcast i8* %120 to float*
  %122 = load float, float* %121, align 4
  %123 = fmul reassoc ninf nsz float %119, %122
  %124 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %123, float 0.000000e+00)
  %125 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %124, float 1.000000e+00)
  %126 = add i32 %109, %103
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, float* %107, i64 %127
  %129 = load float, float* %128, align 4
  %130 = fsub reassoc ninf nsz float %129, %118
  %131 = fmul reassoc ninf nsz float %130, %122
  %132 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %131, float 0.000000e+00)
  %133 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %132, float 1.000000e+00)
  %134 = add i32 %109, %104
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %107, i64 %135
  %137 = load float, float* %136, align 4
  %138 = fsub reassoc ninf nsz float %137, %118
  %139 = fmul reassoc ninf nsz float %138, %122
  %140 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %139, float 0.000000e+00)
  %141 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %140, float 1.000000e+00)
  %142 = getelementptr inbounds i8, i8* %52, i64 40
  %143 = bitcast i8* %142 to float*
  %144 = load float, float* %143, align 4
  %145 = getelementptr inbounds i8, i8* %52, i64 44
  %146 = bitcast i8* %145 to float*
  %147 = load float, float* %146, align 4
  %148 = select reassoc ninf nsz i1 %.not, float %144, float %147
  %149 = getelementptr inbounds i8, i8* %52, i64 48
  %150 = bitcast i8* %149 to float*
  %151 = load float, float* %150, align 4
  %152 = getelementptr inbounds i8, i8* %52, i64 52
  %153 = bitcast i8* %152 to float*
  %154 = load float, float* %153, align 4
  %155 = select reassoc ninf nsz i1 %.not, float %151, float %154
  %156 = select reassoc ninf nsz i1 %87, float %148, float %155
  %157 = fmul reassoc ninf nsz float %156, %125
  %.not4055 = icmp eq i32 %74, 1
  %.not40 = select i1 %.not36, i1 true, i1 %.not4055
  %158 = select reassoc ninf nsz i1 %.not40, float %148, float %155
  %.not41 = icmp eq i32 %.024, 0
  %159 = select reassoc ninf nsz i1 %.not41, float %148, float %155
  %.not4256 = icmp eq i32 %86, %.02857
  %.not42 = select i1 %.not38, i1 true, i1 %.not4256
  %.not43 = icmp eq i32 %.022, 0
  %160 = insertelement <2 x i32> poison, i32 %108, i64 0
  %161 = shufflevector <2 x i32> %160, <2 x i32> poison, <2 x i32> zeroinitializer
  %162 = insertelement <2 x i32> poison, i32 %90, i64 0
  %163 = insertelement <2 x i32> %162, i32 %96, i64 1
  %164 = mul <2 x i32> %161, %163
  %165 = extractelement <2 x i32> %164, i64 0
  %166 = sub i32 %165, %65
  %167 = add i32 %.02857, %166
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, float* %107, i64 %168
  %170 = load float, float* %169, align 4
  %171 = fsub reassoc ninf nsz float %170, %118
  %172 = fmul reassoc ninf nsz float %171, %122
  %173 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %172, float 0.000000e+00)
  %174 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %173, float 1.000000e+00)
  %175 = extractelement <2 x i32> %164, i64 1
  %176 = sub i32 %175, %65
  %177 = add i32 %.02857, %176
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %107, i64 %178
  %180 = load float, float* %179, align 4
  %181 = fsub reassoc ninf nsz float %180, %118
  %182 = fmul reassoc ninf nsz float %181, %122
  %183 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %182, float 0.000000e+00)
  %184 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %183, float 1.000000e+00)
  %185 = fmul reassoc ninf nsz float %158, %174
  %186 = fmul reassoc ninf nsz float %159, %184
  %187 = insertelement <2 x i1> poison, i1 %.not42, i64 0
  %188 = insertelement <2 x i1> %187, i1 %.not43, i64 1
  %189 = insertelement <2 x float> poison, float %144, i64 0
  %190 = shufflevector <2 x float> %189, <2 x float> poison, <2 x i32> zeroinitializer
  %191 = insertelement <2 x float> poison, float %147, i64 0
  %192 = shufflevector <2 x float> %191, <2 x float> poison, <2 x i32> zeroinitializer
  %193 = select <2 x i1> %188, <2 x float> %190, <2 x float> %192
  %194 = insertelement <2 x float> poison, float %151, i64 0
  %195 = shufflevector <2 x float> %194, <2 x float> poison, <2 x i32> zeroinitializer
  %196 = insertelement <2 x float> poison, float %154, i64 0
  %197 = shufflevector <2 x float> %196, <2 x float> poison, <2 x i32> zeroinitializer
  %198 = select <2 x i1> %188, <2 x float> %195, <2 x float> %197
  %199 = extractelement <2 x float> %193, i64 0
  %200 = extractelement <2 x float> %198, i64 0
  %201 = select reassoc ninf nsz i1 %87, float %199, float %200
  %202 = fmul reassoc ninf nsz float %201, %133
  %203 = extractelement <2 x float> %193, i64 1
  %204 = extractelement <2 x float> %198, i64 1
  %205 = select reassoc ninf nsz i1 %87, float %203, float %204
  %206 = fmul reassoc ninf nsz float %205, %141
  switch i32 %.027, label %false_block23 [
    i32 0, label %true_block19
    i32 2, label %true_block22
  ]

after_for.loopexit:                               ; preds = %after_if21
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block19:                                     ; preds = %for_loop_body
  %207 = shufflevector <2 x i32> %164, <2 x i32> undef, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %208 = insertelement <4 x i32> poison, i32 %103, i64 0
  %209 = insertelement <4 x i32> %208, i32 %104, i64 1
  %shuffle68 = shufflevector <4 x i32> %209, <4 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %210 = add <4 x i32> %207, %shuffle68
  %211 = sext <4 x i32> %210 to <4 x i64>
  %212 = insertelement <4 x float*> poison, float* %107, i64 0
  %shuffle67 = shufflevector <4 x float*> %212, <4 x float*> poison, <4 x i32> zeroinitializer
  %213 = getelementptr float, <4 x float*> %shuffle67, <4 x i64> %211
  %214 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %213, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %215 = insertelement <4 x float> poison, float %118, i64 0
  %shuffle69 = shufflevector <4 x float> %215, <4 x float> poison, <4 x i32> zeroinitializer
  %216 = fsub reassoc ninf nsz <4 x float> %214, %shuffle69
  %217 = insertelement <4 x float> poison, float %122, i64 0
  %shuffle70 = shufflevector <4 x float> %217, <4 x float> poison, <4 x i32> zeroinitializer
  %218 = fmul reassoc ninf nsz <4 x float> %216, %shuffle70
  %219 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %218, <4 x float> zeroinitializer)
  %220 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %219, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %221 = insertelement <4 x i1> poison, i1 %.not40, i64 0
  %222 = insertelement <4 x i1> %221, i1 %.not41, i64 1
  %shuffle71 = shufflevector <4 x i1> %222, <4 x i1> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %223 = shufflevector <2 x float> %193, <2 x float> undef, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %224 = shufflevector <2 x float> %198, <2 x float> undef, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %225 = select <4 x i1> %shuffle71, <4 x float> %223, <4 x float> %224
  %226 = fmul reassoc ninf nsz <4 x float> %220, %225
  %227 = fadd reassoc ninf nsz float %186, %185
  %228 = fadd reassoc ninf nsz float %227, %202
  %229 = fadd reassoc ninf nsz float %228, %206
  %230 = fmul reassoc ninf nsz float %229, 2.500000e-01
  %231 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %226)
  %232 = fmul reassoc ninf nsz float %231, 2.500000e-01
  br label %after_if21

after_if21:                                       ; preds = %false_block23, %true_block22, %true_block19
  %.021 = phi float [ %157, %true_block19 ], [ %339, %true_block22 ], [ %., %false_block23 ]
  %.020 = phi float [ %230, %true_block19 ], [ %337, %true_block22 ], [ %157, %false_block23 ]
  %.019 = phi float [ %232, %true_block19 ], [ %157, %true_block22 ], [ %.58, %false_block23 ]
  %233 = load float, float* %23, align 4
  %234 = fmul reassoc ninf nsz float %233, %.021
  %235 = load float, float* %26, align 4
  %236 = fmul reassoc ninf nsz float %235, %.020
  %237 = fadd reassoc ninf nsz float %236, %234
  %238 = load float, float* %27, align 4
  %239 = fmul reassoc ninf nsz float %238, %.019
  %240 = fadd reassoc ninf nsz float %237, %239
  %241 = load float, float* %29, align 4
  %242 = fmul reassoc ninf nsz float %241, %.021
  %243 = load float, float* %32, align 4
  %244 = fmul reassoc ninf nsz float %243, %.020
  %245 = fadd reassoc ninf nsz float %244, %242
  %246 = load float, float* %35, align 4
  %247 = fmul reassoc ninf nsz float %246, %.019
  %248 = fadd reassoc ninf nsz float %245, %247
  %249 = load float, float* %38, align 4
  %250 = fmul reassoc ninf nsz float %249, %.021
  %251 = load float, float* %39, align 4
  %252 = fmul reassoc ninf nsz float %251, %.020
  %253 = fadd reassoc ninf nsz float %252, %250
  %254 = load float, float* %42, align 4
  %255 = fmul reassoc ninf nsz float %254, %.019
  %256 = fadd reassoc ninf nsz float %253, %255
  %257 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %240, float 0.000000e+00)
  %258 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %257, float 1.000000e+00)
  %259 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %258)
  %260 = fmul reassoc ninf nsz float %259, 0x3FD3A00620000000
  %261 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %260
  %262 = fmul reassoc ninf nsz float %261, %259
  %263 = fadd reassoc ninf nsz float %262, 0xBFE9435AA0000000
  %264 = fmul reassoc ninf nsz float %263, %259
  %265 = fadd reassoc ninf nsz float %264, 0x3FF4E33660000000
  %266 = fmul reassoc ninf nsz float %265, %259
  %267 = load float*, float** %46, align 8
  %268 = load i32, i32* %47, align 4
  %269 = load i32, i32* %48, align 4
  %270 = sub i32 %268, %55
  %271 = mul i32 %270, %64
  %272 = add i32 %.02857, %271
  %273 = mul i32 %272, %269
  %274 = sext i32 %273 to i64
  %275 = getelementptr float, float* %267, i64 %274
  store float %266, float* %275, align 4
  %276 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %248, float 0.000000e+00)
  %277 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %276, float 1.000000e+00)
  %278 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %277)
  %279 = fmul reassoc ninf nsz float %278, 0x3FD3A00620000000
  %280 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %279
  %281 = fmul reassoc ninf nsz float %280, %278
  %282 = fadd reassoc ninf nsz float %281, 0xBFE9435AA0000000
  %283 = fmul reassoc ninf nsz float %282, %278
  %284 = fadd reassoc ninf nsz float %283, 0x3FF4E33660000000
  %285 = fmul reassoc ninf nsz float %284, %278
  %286 = load float*, float** %46, align 8
  %287 = load i32, i32* %47, align 4
  %288 = load i32, i32* %48, align 4
  %289 = sub i32 %287, %55
  %290 = mul i32 %289, %64
  %291 = add i32 %.02857, %290
  %292 = mul i32 %291, %288
  %293 = add i32 %292, 1
  %294 = sext i32 %293 to i64
  %295 = getelementptr float, float* %286, i64 %294
  store float %285, float* %295, align 4
  %296 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %256, float 0.000000e+00)
  %297 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %296, float 1.000000e+00)
  %298 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %297)
  %299 = fmul reassoc ninf nsz float %298, 0x3FD3A00620000000
  %300 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %299
  %301 = fmul reassoc ninf nsz float %300, %298
  %302 = fadd reassoc ninf nsz float %301, 0xBFE9435AA0000000
  %303 = fmul reassoc ninf nsz float %302, %298
  %304 = fadd reassoc ninf nsz float %303, 0x3FF4E33660000000
  %305 = fmul reassoc ninf nsz float %304, %298
  %306 = load float*, float** %46, align 8
  %307 = load i32, i32* %47, align 4
  %308 = load i32, i32* %48, align 4
  %309 = sub i32 %307, %55
  %310 = mul i32 %309, %64
  %311 = add i32 %.02857, %310
  %312 = mul i32 %311, %308
  %313 = add i32 %312, 2
  %314 = sext i32 %313 to i64
  %315 = getelementptr float, float* %306, i64 %314
  store float %305, float* %315, align 4
  %316 = add nsw i32 %.02857, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %19, %316
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block22:                                     ; preds = %for_loop_body
  %shuffle66 = shufflevector <2 x float> %198, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %shuffle65 = shufflevector <2 x float> %193, <2 x float> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %shuffle60 = shufflevector <2 x i32> %164, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %317 = insertelement <4 x i32> poison, i32 %103, i64 0
  %318 = insertelement <4 x i32> %317, i32 %104, i64 1
  %shuffle61 = shufflevector <4 x i32> %318, <4 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %319 = add <4 x i32> %shuffle60, %shuffle61
  %320 = insertelement <4 x i1> poison, i1 %.not40, i64 0
  %321 = insertelement <4 x i1> %320, i1 %.not41, i64 1
  %shuffle64 = shufflevector <4 x i1> %321, <4 x i1> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %322 = select <4 x i1> %shuffle64, <4 x float> %shuffle65, <4 x float> %shuffle66
  %323 = sext <4 x i32> %319 to <4 x i64>
  %324 = insertelement <4 x float*> poison, float* %107, i64 0
  %shuffle = shufflevector <4 x float*> %324, <4 x float*> poison, <4 x i32> zeroinitializer
  %325 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %323
  %326 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %325, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %327 = insertelement <4 x float> poison, float %118, i64 0
  %shuffle62 = shufflevector <4 x float> %327, <4 x float> poison, <4 x i32> zeroinitializer
  %328 = fsub reassoc ninf nsz <4 x float> %326, %shuffle62
  %329 = insertelement <4 x float> poison, float %122, i64 0
  %shuffle63 = shufflevector <4 x float> %329, <4 x float> poison, <4 x i32> zeroinitializer
  %330 = fmul reassoc ninf nsz <4 x float> %328, %shuffle63
  %331 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %330, <4 x float> zeroinitializer)
  %332 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %331, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %333 = fmul reassoc ninf nsz <4 x float> %332, %322
  %334 = fadd reassoc ninf nsz float %186, %185
  %335 = fadd reassoc ninf nsz float %334, %202
  %336 = fadd reassoc ninf nsz float %335, %206
  %337 = fmul reassoc ninf nsz float %336, 2.500000e-01
  %338 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %333)
  %339 = fmul reassoc ninf nsz float %338, 2.500000e-01
  br label %after_if21

false_block23:                                    ; preds = %for_loop_body
  %spec.select53.v = select i1 %.not42, i64 8, i64 12
  %spec.select54.v = select i1 %.not42, i64 16, i64 20
  %.017.in.in.v = select i1 %87, i64 %spec.select53.v, i64 %spec.select54.v
  %.017.in.in = getelementptr inbounds i8, i8* %52, i64 %.017.in.in.v
  %.017.in = bitcast i8* %.017.in.in to i32*
  %.017 = load i32, i32* %.017.in, align 4
  %340 = icmp eq i32 %.017, 0
  %341 = fadd reassoc ninf nsz float %202, %206
  %342 = fmul reassoc ninf nsz float %341, 5.000000e-01
  %343 = fadd reassoc ninf nsz float %185, %186
  %344 = fmul reassoc ninf nsz float %343, 5.000000e-01
  %. = select i1 %340, float %342, float %344
  %.58 = select i1 %340, float %344, float %342
  br label %after_if21
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.sqrt.f32(float) #1

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

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.maxnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.minnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone willreturn }

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
