; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.48*, void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.48 = type { i8*, %struct.LLVMRuntime.47*, i32, i64* }
%struct.LLVMRuntime.47 = type { %struct.PreallocatedMemoryChunk.43, %struct.PreallocatedMemoryChunk.43, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.44*], [1024 x %struct.NodeManager.45*], [1024 x i8*], i8*, %struct.RandState.46*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.43 = type { i8*, i8*, i64 }
%struct.ListManager.44 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.47* }
%struct.NodeManager.45 = type { %struct.LLVMRuntime.47*, i32, i32, i32, i32, %struct.ListManager.44*, %struct.ListManager.44*, %struct.ListManager.44*, i32 }
%struct.RandState.46 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_hs_jacobi_step_kernel_c700_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 12
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %18, i64 0, i32 5
  %20 = load float, float* %19, align 4
  %21 = fmul reassoc ninf nsz float %20, %20
  %22 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 16
  %26 = bitcast i8* %25 to float*
  store float %21, float* %26, align 4
  %27 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %28 = tail call i32 @llvm.smax.i32(i32 %12, i32 0)
  %29 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  store i32 %28, i32* %33, align 4
  %34 = mul i32 %28, %27
  %35 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %35, i64 0, i32 14
  %37 = bitcast i8** %36 to i32**
  %38 = load i32*, i32** %37, align 8
  store i32 %34, i32* %38, align 4
  ret void
}

; Function Attrs: nounwind
define void @_hs_jacobi_step_kernel_c700_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.48* %context, %struct.RuntimeContext.48** %4, align 8
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.48*, i8*, i32)* @function_body, void (%struct.RuntimeContext.48*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.48* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %4, i64 0, i32 14
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
  %21 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 3, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 3, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 3, i32 0, i32 2
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 2, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 2, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 4, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 4, i32 0, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %22, i64 0, i32 4, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %187, %for_loop_body ]
  %35 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %35, i64 0, i32 14
  %37 = load i8*, i8** %36, align 8
  %38 = getelementptr inbounds i8, i8* %37, i64 4
  %39 = bitcast i8* %38 to i32*
  %40 = load i32, i32* %39, align 4
  %41 = sdiv i32 %.05, %40
  %42 = mul i32 %41, %40
  %43 = xor i32 %40, %.05
  %44 = icmp slt i32 %43, 0
  %45 = icmp ne i32 %.05, 0
  %46 = icmp ne i32 %.05, %42
  %47 = and i1 %45, %44
  %48 = and i1 %47, %46
  %.neg4 = sext i1 %48 to i32
  %49 = add i32 %41, %.neg4
  %50 = mul i32 %40, -1
  %51 = mul i32 %50, %49
  %52 = add i32 %.05, %51
  %53 = add i32 %49, -1
  %54 = getelementptr inbounds i8, i8* %37, i64 8
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = add i32 %56, -1
  %58 = tail call i32 @llvm.smin.i32(i32 %53, i32 %57)
  %59 = tail call i32 @llvm.smax.i32(i32 %58, i32 0)
  %60 = getelementptr inbounds i8, i8* %37, i64 12
  %61 = bitcast i8* %60 to i32*
  %62 = load i32, i32* %61, align 4
  %63 = add i32 %62, -1
  %64 = tail call i32 @llvm.smin.i32(i32 %52, i32 %63)
  %65 = tail call i32 @llvm.smax.i32(i32 %64, i32 0)
  %66 = load float*, float** %23, align 8
  %67 = load i32, i32* %24, align 4
  %68 = load i32, i32* %25, align 4
  %69 = mul i32 %59, %67
  %70 = add i32 %69, %65
  %71 = mul i32 %70, %68
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, float* %66, i64 %72
  %74 = load float, float* %73, align 4
  %75 = add i32 %71, 1
  %76 = sext i32 %75 to i64
  %77 = getelementptr float, float* %66, i64 %76
  %78 = load float, float* %77, align 4
  %79 = add i32 %49, 1
  %80 = tail call i32 @llvm.smin.i32(i32 %79, i32 %57)
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = mul i32 %81, %67
  %83 = add i32 %82, %65
  %84 = mul i32 %83, %68
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, float* %66, i64 %85
  %87 = load float, float* %86, align 4
  %88 = fadd reassoc ninf nsz float %87, %74
  %89 = add i32 %84, 1
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, float* %66, i64 %90
  %92 = load float, float* %91, align 4
  %93 = fadd reassoc ninf nsz float %92, %78
  %94 = tail call i32 @llvm.smin.i32(i32 %49, i32 %57)
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = add i32 %52, -1
  %97 = tail call i32 @llvm.smin.i32(i32 %96, i32 %63)
  %98 = tail call i32 @llvm.smax.i32(i32 %97, i32 0)
  %99 = mul i32 %95, %67
  %100 = add i32 %98, %99
  %101 = mul i32 %100, %68
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %66, i64 %102
  %104 = load float, float* %103, align 4
  %105 = fadd reassoc ninf nsz float %88, %104
  %106 = add i32 %101, 1
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, float* %66, i64 %107
  %109 = load float, float* %108, align 4
  %110 = fadd reassoc ninf nsz float %93, %109
  %111 = add i32 %52, 1
  %112 = tail call i32 @llvm.smin.i32(i32 %111, i32 %63)
  %113 = tail call i32 @llvm.smax.i32(i32 %112, i32 0)
  %114 = add i32 %113, %99
  %115 = mul i32 %114, %68
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %66, i64 %116
  %118 = load float, float* %117, align 4
  %119 = fadd reassoc ninf nsz float %105, %118
  %120 = add i32 %115, 1
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, float* %66, i64 %121
  %123 = load float, float* %122, align 4
  %124 = fadd reassoc ninf nsz float %110, %123
  %125 = fmul reassoc ninf nsz float %119, 2.500000e-01
  %126 = fmul reassoc ninf nsz float %124, 2.500000e-01
  %127 = load float*, float** %26, align 8
  %128 = load i32, i32* %27, align 4
  %129 = sub i32 %128, %40
  %130 = mul i32 %129, %49
  %131 = add i32 %.05, %130
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %127, i64 %132
  %134 = load float, float* %133, align 4
  %135 = load float*, float** %28, align 8
  %136 = load i32, i32* %29, align 4
  %137 = sub i32 %136, %40
  %138 = mul i32 %137, %49
  %139 = add i32 %.05, %138
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %135, i64 %140
  %142 = load float, float* %141, align 4
  %143 = fmul reassoc ninf nsz float %134, %125
  %144 = fmul reassoc ninf nsz float %142, %126
  %145 = fadd reassoc ninf nsz float %144, %143
  %146 = load float*, float** %30, align 8
  %147 = load i32, i32* %31, align 4
  %148 = sub i32 %147, %40
  %149 = mul i32 %148, %49
  %150 = add i32 %.05, %149
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %146, i64 %151
  %153 = load float, float* %152, align 4
  %154 = fadd reassoc ninf nsz float %145, %153
  %155 = fmul reassoc ninf nsz float %134, %134
  %156 = getelementptr inbounds i8, i8* %37, i64 16
  %157 = bitcast i8* %156 to float*
  %158 = load float, float* %157, align 4
  %159 = fmul reassoc ninf nsz float %142, %142
  %160 = fadd reassoc ninf nsz float %159, %155
  %161 = fadd reassoc ninf nsz float %160, %158
  %162 = fmul reassoc ninf nsz float %154, %134
  %163 = fdiv reassoc ninf nsz float %162, %161
  %164 = fsub reassoc ninf nsz float %125, %163
  %165 = load float*, float** %32, align 8
  %166 = load i32, i32* %33, align 4
  %167 = load i32, i32* %34, align 4
  %168 = sub i32 %166, %40
  %169 = mul i32 %168, %49
  %170 = add i32 %.05, %169
  %171 = mul i32 %170, %167
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %165, i64 %172
  store float %164, float* %173, align 4
  %174 = fmul reassoc ninf nsz float %154, %142
  %175 = fdiv reassoc ninf nsz float %174, %161
  %176 = fsub reassoc ninf nsz float %126, %175
  %177 = load float*, float** %32, align 8
  %178 = load i32, i32* %33, align 4
  %179 = load i32, i32* %34, align 4
  %180 = sub i32 %178, %40
  %181 = mul i32 %180, %49
  %182 = add i32 %.05, %181
  %183 = mul i32 %182, %179
  %184 = add i32 %183, 1
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, float* %177, i64 %185
  store float %176, float* %186, align 4
  %187 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %187
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.48, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.48**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.48*, %struct.RuntimeContext.48** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.48* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.48* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
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
