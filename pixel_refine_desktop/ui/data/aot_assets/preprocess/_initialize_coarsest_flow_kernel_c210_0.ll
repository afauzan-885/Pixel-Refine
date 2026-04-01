; ModuleID = 'kernel'
source_filename = "kernel"
target triple = "nvptx64-nvidia-cuda"

%struct.RuntimeContext.37 = type { i8*, %struct.LLVMRuntime.36*, i32, i64* }
%struct.LLVMRuntime.36 = type { %struct.PreallocatedMemoryChunk.32, %struct.PreallocatedMemoryChunk.32, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.33*], [1024 x %struct.NodeManager.34*], [1024 x i8*], i8*, %struct.RandState.35*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.32 = type { i8*, i8*, i64 }
%struct.ListManager.33 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.36* }
%struct.NodeManager.34 = type { %struct.LLVMRuntime.36*, i32, i32, i32, i32, %struct.ListManager.33*, %struct.ListManager.33*, %struct.ListManager.33*, i32 }
%struct.RandState.35 = type { i32, i32, i32, i32, i32 }

define void @_initialize_coarsest_flow_kernel_c210_0_kernel_0_serial(%struct.RuntimeContext.37* byval(%struct.RuntimeContext.37) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = getelementptr %struct.RuntimeContext.37, %struct.RuntimeContext.37* %context, i32 0, i32 0
  %1 = bitcast i8** %0 to { { { i32, i32, i32 }, float* }, i32, i32, float, float }**
  %2 = load { { { i32, i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, i32, i32, float, float }** %1, align 8
  %3 = getelementptr { { { i32, i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, i32, i32, float, float }* %2, i32 0, i32 1
  %4 = load i32, i32* %3, align 4
  %5 = call i32 @max_i32(i32 0, i32 %4)
  %6 = getelementptr %struct.RuntimeContext.37, %struct.RuntimeContext.37* %context, i32 0, i32 0
  %7 = bitcast i8** %6 to { { { i32, i32, i32 }, float* }, i32, i32, float, float }**
  %8 = load { { { i32, i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, i32, i32, float, float }** %7, align 8
  %9 = getelementptr { { { i32, i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, i32, i32, float, float }* %8, i32 0, i32 2
  %10 = load i32, i32* %9, align 4
  %11 = call i32 @max_i32(i32 0, i32 %10)
  %12 = call %struct.LLVMRuntime.36* @RuntimeContext_get_runtime(%struct.RuntimeContext.37* %context)
  %13 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.36* %12, i64 4)
  %14 = bitcast i8* %13 to i32*
  store i32 %11, i32* %14, align 4
  %15 = mul i32 %5, %11
  %16 = call %struct.LLVMRuntime.36* @RuntimeContext_get_runtime(%struct.RuntimeContext.37* %context)
  %17 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.36* %16, i64 0)
  %18 = bitcast i8* %17 to i32*
  store i32 %15, i32* %18, align 4
  br label %final
}

define void @_initialize_coarsest_flow_kernel_c210_0_kernel_1_range_for(%struct.RuntimeContext.37* byval(%struct.RuntimeContext.37) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = call %struct.LLVMRuntime.36* @RuntimeContext_get_runtime(%struct.RuntimeContext.37* %context)
  %1 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.36* %0, i64 0)
  %2 = bitcast i8* %1 to i32*
  %3 = load i32, i32* %2, align 4
  call void @gpu_parallel_range_for(%struct.RuntimeContext.37* %context, i32 0, i32 %3, void (%struct.RuntimeContext.37*, i8*)* null, void (%struct.RuntimeContext.37*, i8*, i32)* @function_body, void (%struct.RuntimeContext.37*, i8*)* null, i64 1)
  br label %final
}

define internal void @function_body(%struct.RuntimeContext.37* %0, i8* %1, i32 %2) {
allocs:
  %3 = alloca i32, align 4
  br label %entry

final:                                            ; preds = %function_body
  ret void

entry:                                            ; preds = %allocs
  br label %function_body

function_body:                                    ; preds = %entry
  store i32 %2, i32* %3, align 4
  %4 = load i32, i32* %3, align 4
  %5 = call %struct.LLVMRuntime.36* @RuntimeContext_get_runtime(%struct.RuntimeContext.37* %0)
  %6 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.36* %5, i64 4)
  %7 = bitcast i8* %6 to i32*
  %8 = load i32, i32* %7, align 4
  %9 = sdiv i32 %4, %8
  %10 = icmp slt i32 %4, 0
  %11 = icmp slt i32 %8, 0
  %12 = mul i32 %8, %9
  %13 = icmp ne i1 %10, %11
  %14 = icmp ne i32 %4, 0
  %15 = icmp ne i32 %12, %4
  %16 = icmp ne i1 %13, false
  %17 = icmp ne i1 %14, false
  %18 = and i1 %16, %17
  %19 = icmp ne i1 %18, false
  %20 = icmp ne i1 %15, false
  %21 = and i1 %19, %20
  %22 = zext i1 %21 to i32
  %23 = sub i32 %9, %22
  %24 = mul i32 %23, %8
  %25 = sub i32 %4, %24
  %26 = getelementptr %struct.RuntimeContext.37, %struct.RuntimeContext.37* %0, i32 0, i32 0
  %27 = bitcast i8** %26 to { { { i32, i32, i32 }, float* }, i32, i32, float, float }**
  %28 = load { { { i32, i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, i32, i32, float, float }** %27, align 8
  %29 = getelementptr { { { i32, i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, i32, i32, float, float }* %28, i32 0, i32 3
  %30 = load float, float* %29, align 4
  %31 = getelementptr %struct.RuntimeContext.37, %struct.RuntimeContext.37* %0, i32 0, i32 0
  %32 = bitcast i8** %31 to { { { i32, i32, i32 }, float* }, i32, i32, float, float }**
  %33 = load { { { i32, i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, i32, i32, float, float }** %32, align 8
  %34 = getelementptr { { { i32, i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, i32, i32, float, float }* %33, i32 0, i32 0
  %35 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 1
  %36 = load float*, float** %35, align 8
  %37 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 0, i32 0
  %38 = load i32, i32* %37, align 4
  %39 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 0, i32 1
  %40 = load i32, i32* %39, align 4
  %41 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 0, i32 2
  %42 = load i32, i32* %41, align 4
  %43 = mul i32 0, %38
  %44 = add i32 %43, %23
  %45 = mul i32 %44, %40
  %46 = add i32 %45, %25
  %47 = mul i32 %46, %42
  %48 = add i32 %47, 0
  %49 = getelementptr float, float* %36, i32 %48
  store float %30, float* %49, align 4
  %50 = getelementptr %struct.RuntimeContext.37, %struct.RuntimeContext.37* %0, i32 0, i32 0
  %51 = bitcast i8** %50 to { { { i32, i32, i32 }, float* }, i32, i32, float, float }**
  %52 = load { { { i32, i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32, i32 }, float* }, i32, i32, float, float }** %51, align 8
  %53 = getelementptr { { { i32, i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32, i32 }, float* }, i32, i32, float, float }* %52, i32 0, i32 4
  %54 = load float, float* %53, align 4
  %55 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 1
  %56 = load float*, float** %55, align 8
  %57 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 0, i32 0
  %58 = load i32, i32* %57, align 4
  %59 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 0, i32 1
  %60 = load i32, i32* %59, align 4
  %61 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %34, i32 0, i32 0, i32 2
  %62 = load i32, i32* %61, align 4
  %63 = mul i32 0, %58
  %64 = add i32 %63, %23
  %65 = mul i32 %64, %60
  %66 = add i32 %65, %25
  %67 = mul i32 %66, %62
  %68 = add i32 %67, 1
  %69 = getelementptr float, float* %56, i32 %68
  store float %54, float* %69, align 4
  br label %final
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @max_i32(i32 noundef %0, i32 noundef %1) #0 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 %1, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  %5 = load i32, i32* %4, align 4
  %6 = load i32, i32* %3, align 4
  %7 = icmp sgt i32 %5, %6
  br i1 %7, label %8, label %10

8:                                                ; preds = %2
  %9 = load i32, i32* %4, align 4
  br label %12

10:                                               ; preds = %2
  %11 = load i32, i32* %3, align 4
  br label %12

12:                                               ; preds = %10, %8
  %13 = phi i32 [ %9, %8 ], [ %11, %10 ]
  ret i32 %13
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal %struct.LLVMRuntime.36* @RuntimeContext_get_runtime(%struct.RuntimeContext.37* noundef %0) #0 {
  %2 = alloca %struct.RuntimeContext.37*, align 8
  store %struct.RuntimeContext.37* %0, %struct.RuntimeContext.37** %2, align 8
  %3 = load %struct.RuntimeContext.37*, %struct.RuntimeContext.37** %2, align 8
  %4 = getelementptr inbounds %struct.RuntimeContext.37, %struct.RuntimeContext.37* %3, i32 0, i32 1
  %5 = load %struct.LLVMRuntime.36*, %struct.LLVMRuntime.36** %4, align 8
  ret %struct.LLVMRuntime.36* %5
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i8* @get_temporary_pointer(%struct.LLVMRuntime.36* noundef %0, i64 noundef %1) #0 {
  %3 = alloca i64, align 8
  %4 = alloca %struct.LLVMRuntime.36*, align 8
  store i64 %1, i64* %3, align 8
  store %struct.LLVMRuntime.36* %0, %struct.LLVMRuntime.36** %4, align 8
  %5 = load %struct.LLVMRuntime.36*, %struct.LLVMRuntime.36** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.36, %struct.LLVMRuntime.36* %5, i32 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = load i64, i64* %3, align 8
  %9 = getelementptr inbounds i8, i8* %7, i64 %8
  ret i8* %9
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @gpu_parallel_range_for(%struct.RuntimeContext.37* noundef %0, i32 noundef %1, i32 noundef %2, void (%struct.RuntimeContext.37*, i8*)* noundef %3, void (%struct.RuntimeContext.37*, i8*, i32)* noundef %4, void (%struct.RuntimeContext.37*, i8*)* noundef %5, i64 noundef %6) #0 {
  %8 = alloca i64, align 8
  %9 = alloca void (%struct.RuntimeContext.37*, i8*)*, align 8
  %10 = alloca void (%struct.RuntimeContext.37*, i8*, i32)*, align 8
  %11 = alloca void (%struct.RuntimeContext.37*, i8*)*, align 8
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca %struct.RuntimeContext.37*, align 8
  %15 = alloca i32, align 4
  %16 = alloca i8*, align 8
  %17 = alloca i64, align 8
  %18 = alloca i8*, align 8
  store i64 %6, i64* %8, align 8
  store void (%struct.RuntimeContext.37*, i8*)* %5, void (%struct.RuntimeContext.37*, i8*)** %9, align 8
  store void (%struct.RuntimeContext.37*, i8*, i32)* %4, void (%struct.RuntimeContext.37*, i8*, i32)** %10, align 8
  store void (%struct.RuntimeContext.37*, i8*)* %3, void (%struct.RuntimeContext.37*, i8*)** %11, align 8
  store i32 %2, i32* %12, align 4
  store i32 %1, i32* %13, align 4
  store %struct.RuntimeContext.37* %0, %struct.RuntimeContext.37** %14, align 8
  %19 = call i32 @thread_idx()
  %20 = call i32 @block_dim()
  %21 = call i32 @block_idx()
  %22 = mul nsw i32 %20, %21
  %23 = add nsw i32 %19, %22
  %24 = load i32, i32* %13, align 4
  %25 = add nsw i32 %23, %24
  store i32 %25, i32* %15, align 4
  %26 = load i64, i64* %8, align 8
  %27 = call i8* @llvm.stacksave()
  store i8* %27, i8** %16, align 8
  %28 = alloca i8, i64 %26, align 8
  store i64 %26, i64* %17, align 8
  %29 = getelementptr inbounds i8, i8* %28, i64 0
  store i8* %29, i8** %18, align 8
  %30 = load void (%struct.RuntimeContext.37*, i8*)*, void (%struct.RuntimeContext.37*, i8*)** %11, align 8
  %31 = icmp ne void (%struct.RuntimeContext.37*, i8*)* %30, null
  br i1 %31, label %32, label %36

32:                                               ; preds = %7
  %33 = load void (%struct.RuntimeContext.37*, i8*)*, void (%struct.RuntimeContext.37*, i8*)** %11, align 8
  %34 = load i8*, i8** %18, align 8
  %35 = load %struct.RuntimeContext.37*, %struct.RuntimeContext.37** %14, align 8
  call void %33(%struct.RuntimeContext.37* noundef %35, i8* noundef %34)
  br label %36

36:                                               ; preds = %32, %7
  br label %37

37:                                               ; preds = %41, %36
  %38 = load i32, i32* %15, align 4
  %39 = load i32, i32* %12, align 4
  %40 = icmp slt i32 %38, %39
  br i1 %40, label %41, label %51

41:                                               ; preds = %37
  %42 = load void (%struct.RuntimeContext.37*, i8*, i32)*, void (%struct.RuntimeContext.37*, i8*, i32)** %10, align 8
  %43 = load i32, i32* %15, align 4
  %44 = load i8*, i8** %18, align 8
  %45 = load %struct.RuntimeContext.37*, %struct.RuntimeContext.37** %14, align 8
  call void %42(%struct.RuntimeContext.37* noundef %45, i8* noundef %44, i32 noundef %43)
  %46 = call i32 @block_dim()
  %47 = call i32 @grid_dim()
  %48 = mul nsw i32 %46, %47
  %49 = load i32, i32* %15, align 4
  %50 = add nsw i32 %49, %48
  store i32 %50, i32* %15, align 4
  br label %37, !llvm.loop !20

51:                                               ; preds = %37
  %52 = load void (%struct.RuntimeContext.37*, i8*)*, void (%struct.RuntimeContext.37*, i8*)** %9, align 8
  %53 = icmp ne void (%struct.RuntimeContext.37*, i8*)* %52, null
  br i1 %53, label %54, label %58

54:                                               ; preds = %51
  %55 = load void (%struct.RuntimeContext.37*, i8*)*, void (%struct.RuntimeContext.37*, i8*)** %9, align 8
  %56 = load i8*, i8** %18, align 8
  %57 = load %struct.RuntimeContext.37*, %struct.RuntimeContext.37** %14, align 8
  call void %55(%struct.RuntimeContext.37* noundef %57, i8* noundef %56)
  br label %58

58:                                               ; preds = %54, %51
  %59 = load i8*, i8** %16, align 8
  call void @llvm.stackrestore(i8* %59)
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @thread_idx() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.tid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_dim() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ntid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_idx() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare i8* @llvm.stacksave() #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @grid_dim() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.nctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare void @llvm.stackrestore(i8*) #1

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.nctaid.x() #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ctaid.x() #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ntid.x() #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.tid.x() #2

attributes #0 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind willreturn }
attributes #2 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

!nvvm.annotations = !{!0, !1, !2, !3, !4, !5, !6, !7, !6, !8, !8, !8, !8, !9, !9, !8}
!llvm.linker.options = !{!10, !11, !12, !13, !14}
!llvm.ident = !{!15}
!nvvmir.version = !{!16}
!llvm.module.flags = !{!17, !18, !19}

!0 = !{void (%struct.RuntimeContext.37*)* @_initialize_coarsest_flow_kernel_c210_0_kernel_0_serial, !"kernel", i32 1}
!1 = !{void (%struct.RuntimeContext.37*)* @_initialize_coarsest_flow_kernel_c210_0_kernel_0_serial, !"maxntidx", i32 1}
!2 = !{void (%struct.RuntimeContext.37*)* @_initialize_coarsest_flow_kernel_c210_0_kernel_0_serial, !"minctasm", i32 2}
!3 = !{void (%struct.RuntimeContext.37*)* @_initialize_coarsest_flow_kernel_c210_0_kernel_1_range_for, !"kernel", i32 1}
!4 = !{void (%struct.RuntimeContext.37*)* @_initialize_coarsest_flow_kernel_c210_0_kernel_1_range_for, !"maxntidx", i32 128}
!5 = !{void (%struct.RuntimeContext.37*)* @_initialize_coarsest_flow_kernel_c210_0_kernel_1_range_for, !"minctasm", i32 2}
!6 = !{null, !"align", i32 8}
!7 = !{null, !"align", i32 8, !"align", i32 65544, !"align", i32 131080}
!8 = !{null, !"align", i32 16}
!9 = !{null, !"align", i32 16, !"align", i32 65552, !"align", i32 131088}
!10 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!11 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!12 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!13 = !{!"/DEFAULTLIB:libcpmt.lib"}
!14 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!15 = !{!"clang version 14.0.6"}
!16 = !{i32 1, i32 4}
!17 = !{i32 1, !"wchar_size", i32 2}
!18 = !{i32 7, !"PIC Level", i32 2}
!19 = !{i32 7, !"uwtable", i32 1}
!20 = distinct !{!20, !21}
!21 = !{!"llvm.loop.mustprogress"}
