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
define void @_bm_adaptive_refine_kernel_c704_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 12
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }** %0, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %18, i64 0, i32 2, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %18, i64 0, i32 2, i32 0, i32 1
  %22 = load i32, i32* %21, align 4
  %23 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %24 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %25 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  store i32 %24, i32* %29, align 4
  %30 = mul i32 %24, %23
  %31 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %4, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %31, i64 0, i32 14
  %33 = bitcast i8** %32 to i32**
  %34 = load i32*, i32** %33, align 8
  store i32 %30, i32* %34, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bm_adaptive_refine_kernel_c704_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 9
  %23 = load i32, i32* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 3, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %21, i64 0, i32 3, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.065120 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %106, %after_if3 ]
  %28 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %28, i64 0, i32 14
  %30 = load i8*, i8** %29, align 8
  %31 = getelementptr inbounds i8, i8* %30, i64 4
  %32 = bitcast i8* %31 to i32*
  %33 = load i32, i32* %32, align 4
  %34 = sdiv i32 %.065120, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.065120
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.065120, 0
  %39 = icmp ne i32 %35, %.065120
  %40 = and i1 %38, %37
  %41 = and i1 %40, %39
  %.neg69 = sext i1 %41 to i32
  %42 = add i32 %34, %.neg69
  %43 = mul i32 %42, %33
  %44 = sub i32 %.065120, %43
  %45 = load float*, float** %25, align 8
  %46 = load i32, i32* %26, align 4
  %47 = load i32, i32* %27, align 4
  %48 = mul i32 %42, %46
  %49 = add i32 %44, %48
  %50 = mul i32 %49, %47
  %51 = add i32 %50, 2
  %52 = sext i32 %51 to i64
  %53 = getelementptr float, float* %45, i64 %52
  %54 = load float, float* %53, align 4
  %55 = fptosi float %54 to i32
  %.not = icmp sgt i32 %23, %55
  br i1 %.not, label %after_if3, label %true_block

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %56 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }** %20, align 8
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 2, i32 1
  %58 = load float*, float** %57, align 8
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 2, i32 0, i32 1
  %60 = load i32, i32* %59, align 4
  %61 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 2, i32 0, i32 2
  %62 = load i32, i32* %61, align 4
  %63 = mul i32 %60, %42
  %64 = add i32 %63, %44
  %65 = mul i32 %64, %62
  %66 = add i32 %65, 2
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, float* %58, i64 %67
  %69 = load float, float* %68, align 4
  %70 = fcmp reassoc ninf nsz ogt float %69, 5.000000e-01
  br i1 %70, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %71 = sext i32 %65 to i64
  %72 = getelementptr float, float* %58, i64 %71
  %73 = load float, float* %72, align 4
  %74 = add i32 %65, 1
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, float* %58, i64 %75
  %77 = load float, float* %76, align 4
  %78 = tail call reassoc ninf nsz float @llvm.round.f32(float %73)
  %79 = fptosi float %78 to i32
  %80 = tail call reassoc ninf nsz float @llvm.round.f32(float %77)
  %81 = fptosi float %80 to i32
  %82 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 6
  %83 = load i32, i32* %82, align 4
  %neg = sub i32 0, %83
  %84 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 5
  %85 = load i32, i32* %84, align 4
  %86 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 4
  %87 = load i32, i32* %86, align 4
  %88 = getelementptr inbounds i8, i8* %30, i64 8
  %89 = bitcast i8* %88 to i32*
  %90 = load i32, i32* %89, align 4
  %91 = add i32 %90, -1
  %92 = getelementptr inbounds i8, i8* %30, i64 12
  %93 = bitcast i8* %92 to i32*
  %94 = load i32, i32* %93, align 4
  %95 = add i32 %94, -1
  %96 = mul i32 %87, %42
  %97 = add i32 %96, %85
  %.not7084 = icmp slt i32 %83, %neg
  br i1 %.not7084, label %false_block52, label %while_loop_body7.preheader.lr.ph

while_loop_body7.preheader.lr.ph:                 ; preds = %true_block1
  %98 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 1, i32 1
  %99 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 1, i32 0, i32 1
  %100 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 0, i32 1
  %101 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 0, i32 0, i32 1
  %.pre = load float*, float** %98, align 8
  %.pre129 = load i32, i32* %99, align 4
  %.pre130 = load float*, float** %100, align 8
  %.pre131 = load i32, i32* %101, align 4
  %102 = mul i32 %87, %44
  %103 = add i32 %85, %102
  %104 = add i32 %79, %85
  %105 = add i32 %104, %102
  br label %while_loop_body7.preheader

after_if3:                                        ; preds = %after_if66, %true_block, %for_loop_body
  %106 = add nsw i32 %.065120, 1
  %exitcond.not = icmp eq i32 %106, %19
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

while_loop_body13.preheader:                      ; preds = %false_block10
  br i1 false, label %false_block52, label %while_loop_body19.preheader.lr.ph

while_loop_body19.preheader.lr.ph:                ; preds = %while_loop_body13.preheader
  br label %while_loop_body19.preheader

while_loop_body7.preheader:                       ; preds = %false_block10, %while_loop_body7.preheader.lr.ph
  %.05386 = phi i32 [ %neg, %while_loop_body7.preheader.lr.ph ], [ %115, %false_block10 ]
  %.06285 = phi float [ 0.000000e+00, %while_loop_body7.preheader.lr.ph ], [ %132, %false_block10 ]
  %107 = add i32 %.05386, %97
  %108 = add i32 %107, %81
  %109 = tail call i32 @llvm.smin.i32(i32 %108, i32 %91)
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %111 = tail call i32 @llvm.smin.i32(i32 %107, i32 %91)
  %112 = tail call i32 @llvm.smax.i32(i32 %111, i32 0)
  %113 = mul i32 %.pre129, %110
  %114 = mul i32 %.pre131, %112
  br label %after_if11

false_block10:                                    ; preds = %after_if11
  %115 = add i32 %.05386, 2
  %.not70 = icmp sgt i32 %115, %83
  br i1 %.not70, label %while_loop_body13.preheader, label %while_loop_body7.preheader

after_if11:                                       ; preds = %after_if11, %while_loop_body7.preheader
  %.05283 = phi i32 [ %neg, %while_loop_body7.preheader ], [ %133, %after_if11 ]
  %.16382 = phi float [ %.06285, %while_loop_body7.preheader ], [ %132, %after_if11 ]
  %116 = add i32 %103, %.05283
  %117 = add i32 %105, %.05283
  %118 = tail call i32 @llvm.smin.i32(i32 %117, i32 %95)
  %119 = tail call i32 @llvm.smax.i32(i32 %118, i32 0)
  %120 = tail call i32 @llvm.smin.i32(i32 %116, i32 %95)
  %121 = tail call i32 @llvm.smax.i32(i32 %120, i32 0)
  %122 = add i32 %113, %119
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, float* %.pre, i64 %123
  %125 = load float, float* %124, align 4
  %126 = add i32 %114, %121
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, float* %.pre130, i64 %127
  %129 = load float, float* %128, align 4
  %130 = fsub reassoc ninf nsz float %125, %129
  %131 = tail call float @llvm.fabs.f32(float %130)
  %132 = fadd reassoc ninf nsz float %131, %.16382
  %133 = add i32 %.05283, 2
  %.not80 = icmp sgt i32 %133, %83
  br i1 %.not80, label %false_block10, label %after_if11

while_loop_body25.preheader:                      ; preds = %false_block22
  br i1 false, label %false_block52, label %while_loop_body31.preheader.lr.ph

while_loop_body31.preheader.lr.ph:                ; preds = %while_loop_body25.preheader
  br label %while_loop_body31.preheader

while_loop_body19.preheader:                      ; preds = %false_block22, %while_loop_body19.preheader.lr.ph
  %.194 = phi i32 [ %neg, %while_loop_body19.preheader.lr.ph ], [ %142, %false_block22 ]
  %.06093 = phi float [ 0.000000e+00, %while_loop_body19.preheader.lr.ph ], [ %160, %false_block22 ]
  %134 = add i32 %.194, %97
  %135 = add i32 %134, %81
  %136 = tail call i32 @llvm.smin.i32(i32 %135, i32 %91)
  %137 = tail call i32 @llvm.smax.i32(i32 %136, i32 0)
  %138 = tail call i32 @llvm.smin.i32(i32 %134, i32 %91)
  %139 = tail call i32 @llvm.smax.i32(i32 %138, i32 0)
  %140 = mul i32 %.pre129, %137
  %141 = mul i32 %.pre131, %139
  br label %after_if23

false_block22:                                    ; preds = %after_if23
  %142 = add i32 %.194, 2
  %.not71 = icmp sgt i32 %142, %83
  br i1 %.not71, label %while_loop_body25.preheader, label %while_loop_body19.preheader

after_if23:                                       ; preds = %after_if23, %while_loop_body19.preheader
  %.05190 = phi i32 [ %neg, %while_loop_body19.preheader ], [ %161, %after_if23 ]
  %.16189 = phi float [ %.06093, %while_loop_body19.preheader ], [ %160, %after_if23 ]
  %143 = add i32 %103, %.05190
  %144 = add i32 %105, %.05190
  %145 = add i32 %144, -1
  %146 = tail call i32 @llvm.smin.i32(i32 %145, i32 %95)
  %147 = tail call i32 @llvm.smax.i32(i32 %146, i32 0)
  %148 = tail call i32 @llvm.smin.i32(i32 %143, i32 %95)
  %149 = tail call i32 @llvm.smax.i32(i32 %148, i32 0)
  %150 = add i32 %140, %147
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %.pre, i64 %151
  %153 = load float, float* %152, align 4
  %154 = add i32 %141, %149
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %.pre130, i64 %155
  %157 = load float, float* %156, align 4
  %158 = fsub reassoc ninf nsz float %153, %157
  %159 = tail call float @llvm.fabs.f32(float %158)
  %160 = fadd reassoc ninf nsz float %159, %.16189
  %161 = add i32 %.05190, 2
  %.not79 = icmp sgt i32 %161, %83
  br i1 %.not79, label %false_block22, label %after_if23

while_loop_body37.preheader:                      ; preds = %false_block34
  br i1 false, label %false_block52, label %while_loop_body43.preheader.lr.ph

while_loop_body43.preheader.lr.ph:                ; preds = %while_loop_body37.preheader
  %162 = add i32 %81, -1
  br label %while_loop_body43.preheader

while_loop_body31.preheader:                      ; preds = %false_block34, %while_loop_body31.preheader.lr.ph
  %.2102 = phi i32 [ %neg, %while_loop_body31.preheader.lr.ph ], [ %171, %false_block34 ]
  %.058101 = phi float [ 0.000000e+00, %while_loop_body31.preheader.lr.ph ], [ %189, %false_block34 ]
  %163 = add i32 %.2102, %97
  %164 = add i32 %163, %81
  %165 = tail call i32 @llvm.smin.i32(i32 %164, i32 %91)
  %166 = tail call i32 @llvm.smax.i32(i32 %165, i32 0)
  %167 = tail call i32 @llvm.smin.i32(i32 %163, i32 %91)
  %168 = tail call i32 @llvm.smax.i32(i32 %167, i32 0)
  %169 = mul i32 %.pre129, %166
  %170 = mul i32 %.pre131, %168
  br label %after_if35

false_block34:                                    ; preds = %after_if35
  %171 = add i32 %.2102, 2
  %.not72 = icmp sgt i32 %171, %83
  br i1 %.not72, label %while_loop_body37.preheader, label %while_loop_body31.preheader

after_if35:                                       ; preds = %after_if35, %while_loop_body31.preheader
  %.05098 = phi i32 [ %neg, %while_loop_body31.preheader ], [ %190, %after_if35 ]
  %.15997 = phi float [ %.058101, %while_loop_body31.preheader ], [ %189, %after_if35 ]
  %172 = add i32 %103, %.05098
  %173 = add i32 %105, %.05098
  %174 = add i32 %173, 1
  %175 = tail call i32 @llvm.smin.i32(i32 %174, i32 %95)
  %176 = tail call i32 @llvm.smax.i32(i32 %175, i32 0)
  %177 = tail call i32 @llvm.smin.i32(i32 %172, i32 %95)
  %178 = tail call i32 @llvm.smax.i32(i32 %177, i32 0)
  %179 = add i32 %169, %176
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, float* %.pre, i64 %180
  %182 = load float, float* %181, align 4
  %183 = add i32 %170, %178
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, float* %.pre130, i64 %184
  %186 = load float, float* %185, align 4
  %187 = fsub reassoc ninf nsz float %182, %186
  %188 = tail call float @llvm.fabs.f32(float %187)
  %189 = fadd reassoc ninf nsz float %188, %.15997
  %190 = add i32 %.05098, 2
  %.not78 = icmp sgt i32 %190, %83
  br i1 %.not78, label %false_block34, label %after_if35

while_loop_body49.preheader:                      ; preds = %false_block46
  br i1 false, label %false_block52, label %while_loop_body55.preheader.lr.ph

while_loop_body55.preheader.lr.ph:                ; preds = %while_loop_body49.preheader
  %191 = add i32 %81, 1
  br label %while_loop_body55.preheader

while_loop_body43.preheader:                      ; preds = %false_block46, %while_loop_body43.preheader.lr.ph
  %.3110 = phi i32 [ %neg, %while_loop_body43.preheader.lr.ph ], [ %200, %false_block46 ]
  %.056109 = phi float [ 0.000000e+00, %while_loop_body43.preheader.lr.ph ], [ %217, %false_block46 ]
  %192 = add i32 %.3110, %97
  %193 = add i32 %162, %192
  %194 = tail call i32 @llvm.smin.i32(i32 %193, i32 %91)
  %195 = tail call i32 @llvm.smax.i32(i32 %194, i32 0)
  %196 = tail call i32 @llvm.smin.i32(i32 %192, i32 %91)
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = mul i32 %.pre129, %195
  %199 = mul i32 %.pre131, %197
  br label %after_if47

false_block46:                                    ; preds = %after_if47
  %200 = add i32 %.3110, 2
  %.not73 = icmp sgt i32 %200, %83
  br i1 %.not73, label %while_loop_body49.preheader, label %while_loop_body43.preheader

after_if47:                                       ; preds = %after_if47, %while_loop_body43.preheader
  %.049106 = phi i32 [ %neg, %while_loop_body43.preheader ], [ %218, %after_if47 ]
  %.157105 = phi float [ %.056109, %while_loop_body43.preheader ], [ %217, %after_if47 ]
  %201 = add i32 %103, %.049106
  %202 = add i32 %105, %.049106
  %203 = tail call i32 @llvm.smin.i32(i32 %202, i32 %95)
  %204 = tail call i32 @llvm.smax.i32(i32 %203, i32 0)
  %205 = tail call i32 @llvm.smin.i32(i32 %201, i32 %95)
  %206 = tail call i32 @llvm.smax.i32(i32 %205, i32 0)
  %207 = add i32 %198, %204
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, float* %.pre, i64 %208
  %210 = load float, float* %209, align 4
  %211 = add i32 %199, %206
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, float* %.pre130, i64 %212
  %214 = load float, float* %213, align 4
  %215 = fsub reassoc ninf nsz float %210, %214
  %216 = tail call float @llvm.fabs.f32(float %215)
  %217 = fadd reassoc ninf nsz float %216, %.157105
  %218 = add i32 %.049106, 2
  %.not77 = icmp sgt i32 %218, %83
  br i1 %.not77, label %false_block46, label %after_if47

while_loop_body55.preheader:                      ; preds = %false_block58, %while_loop_body55.preheader.lr.ph
  %.4118 = phi i32 [ %neg, %while_loop_body55.preheader.lr.ph ], [ %231, %false_block58 ]
  %.054117 = phi float [ 0.000000e+00, %while_loop_body55.preheader.lr.ph ], [ %248, %false_block58 ]
  %219 = add i32 %.4118, %97
  %220 = add i32 %191, %219
  %221 = tail call i32 @llvm.smin.i32(i32 %220, i32 %91)
  %222 = tail call i32 @llvm.smax.i32(i32 %221, i32 0)
  %223 = tail call i32 @llvm.smin.i32(i32 %219, i32 %91)
  %224 = tail call i32 @llvm.smax.i32(i32 %223, i32 0)
  %225 = mul i32 %.pre129, %222
  %226 = mul i32 %.pre131, %224
  br label %after_if59

false_block52.loopexit:                           ; preds = %false_block58
  br label %false_block52

false_block52:                                    ; preds = %false_block52.loopexit, %while_loop_body49.preheader, %while_loop_body37.preheader, %while_loop_body25.preheader, %while_loop_body13.preheader, %true_block1
  %.056.lcssa167 = phi float [ %217, %while_loop_body49.preheader ], [ 0.000000e+00, %while_loop_body37.preheader ], [ 0.000000e+00, %while_loop_body25.preheader ], [ 0.000000e+00, %while_loop_body13.preheader ], [ 0.000000e+00, %true_block1 ], [ %217, %false_block52.loopexit ]
  %.060.lcssa153157166 = phi float [ %160, %while_loop_body49.preheader ], [ %160, %while_loop_body37.preheader ], [ %160, %while_loop_body25.preheader ], [ 0.000000e+00, %while_loop_body13.preheader ], [ 0.000000e+00, %true_block1 ], [ %160, %false_block52.loopexit ]
  %.062.lcssa149152158165 = phi float [ %132, %while_loop_body49.preheader ], [ %132, %while_loop_body37.preheader ], [ %132, %while_loop_body25.preheader ], [ %132, %while_loop_body13.preheader ], [ 0.000000e+00, %true_block1 ], [ %132, %false_block52.loopexit ]
  %.058.lcssa159164 = phi float [ %189, %while_loop_body49.preheader ], [ %189, %while_loop_body37.preheader ], [ 0.000000e+00, %while_loop_body25.preheader ], [ 0.000000e+00, %while_loop_body13.preheader ], [ 0.000000e+00, %true_block1 ], [ %189, %false_block52.loopexit ]
  %.054.lcssa = phi float [ 0.000000e+00, %while_loop_body49.preheader ], [ 0.000000e+00, %while_loop_body37.preheader ], [ 0.000000e+00, %while_loop_body25.preheader ], [ 0.000000e+00, %while_loop_body13.preheader ], [ 0.000000e+00, %true_block1 ], [ %248, %false_block52.loopexit ]
  %factor = fmul reassoc ninf nsz float %.062.lcssa149152158165, 2.000000e+00
  %227 = fsub reassoc ninf nsz float %.058.lcssa159164, %factor
  %228 = fadd reassoc ninf nsz float %227, %.060.lcssa153157166
  %229 = tail call float @llvm.fabs.f32(float %228)
  %230 = fcmp reassoc ninf nsz ogt float %229, 0x3F1A36E2E0000000
  br i1 %230, label %true_block61, label %after_if63

false_block58:                                    ; preds = %after_if59
  %231 = add i32 %.4118, 2
  %.not74 = icmp sgt i32 %231, %83
  br i1 %.not74, label %false_block52.loopexit, label %while_loop_body55.preheader

after_if59:                                       ; preds = %after_if59, %while_loop_body55.preheader
  %.048114 = phi i32 [ %neg, %while_loop_body55.preheader ], [ %249, %after_if59 ]
  %.155113 = phi float [ %.054117, %while_loop_body55.preheader ], [ %248, %after_if59 ]
  %232 = add i32 %103, %.048114
  %233 = add i32 %105, %.048114
  %234 = tail call i32 @llvm.smin.i32(i32 %233, i32 %95)
  %235 = tail call i32 @llvm.smax.i32(i32 %234, i32 0)
  %236 = tail call i32 @llvm.smin.i32(i32 %232, i32 %95)
  %237 = tail call i32 @llvm.smax.i32(i32 %236, i32 0)
  %238 = add i32 %225, %235
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, float* %.pre, i64 %239
  %241 = load float, float* %240, align 4
  %242 = add i32 %226, %237
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, float* %.pre130, i64 %243
  %245 = load float, float* %244, align 4
  %246 = fsub reassoc ninf nsz float %241, %245
  %247 = tail call float @llvm.fabs.f32(float %246)
  %248 = fadd reassoc ninf nsz float %247, %.155113
  %249 = add i32 %.048114, 2
  %.not76 = icmp sgt i32 %249, %83
  br i1 %.not76, label %false_block58, label %after_if59

true_block61:                                     ; preds = %false_block52
  %250 = fsub reassoc ninf nsz float %.058.lcssa159164, %.060.lcssa153157166
  %251 = fmul reassoc ninf nsz float %250, -5.000000e-01
  %252 = fdiv reassoc ninf nsz float %251, %228
  %253 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %252, float 5.000000e-01)
  %254 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %253, float -5.000000e-01)
  br label %after_if63

after_if63:                                       ; preds = %true_block61, %false_block52
  %.047 = phi float [ %254, %true_block61 ], [ 0.000000e+00, %false_block52 ]
  %255 = fsub reassoc ninf nsz float %.054.lcssa, %factor
  %256 = fadd reassoc ninf nsz float %255, %.056.lcssa167
  %257 = tail call float @llvm.fabs.f32(float %256)
  %258 = fcmp reassoc ninf nsz ogt float %257, 0x3F1A36E2E0000000
  br i1 %258, label %true_block64, label %after_if66

true_block64:                                     ; preds = %after_if63
  %259 = fsub reassoc ninf nsz float %.054.lcssa, %.056.lcssa167
  %260 = fmul reassoc ninf nsz float %259, -5.000000e-01
  %261 = fdiv reassoc ninf nsz float %260, %256
  %262 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %261, float 5.000000e-01)
  %263 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %262, float -5.000000e-01)
  br label %after_if66

after_if66:                                       ; preds = %true_block64, %after_if63
  %.0 = phi float [ %263, %true_block64 ], [ 0.000000e+00, %after_if63 ]
  %264 = sitofp i32 %79 to float
  %265 = fadd reassoc ninf nsz float %.047, %264
  %266 = sitofp i32 %81 to float
  %267 = fadd reassoc ninf nsz float %.0, %266
  %268 = shl i32 %83, 1
  %269 = add i32 %87, %83
  %270 = shl i32 %269, 1
  %271 = sitofp i32 %270 to float
  %neg67 = fneg reassoc ninf nsz float %271
  %272 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %271, float %265)
  %273 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg67, float %272)
  %274 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %271, float %267)
  %275 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg67, float %274)
  %276 = sdiv i32 %268, 2
  %277 = icmp slt i32 %268, 0
  %278 = shl nsw i32 %276, 1
  %279 = icmp ne i32 %278, %268
  %280 = and i1 %277, %279
  %.neg75 = sext i1 %280 to i32
  %281 = add nsw i32 %276, 1
  %282 = add nsw i32 %281, %.neg75
  %283 = mul i32 %282, %282
  %284 = sitofp i32 %283 to float
  %285 = fdiv reassoc ninf nsz float %.062.lcssa149152158165, %284
  store float %273, float* %72, align 4
  store float %275, float* %76, align 4
  %286 = load float*, float** %25, align 8
  %287 = load i32, i32* %26, align 4
  %288 = load i32, i32* %27, align 4
  %289 = mul i32 %287, %42
  %290 = add i32 %289, %44
  %291 = mul i32 %290, %288
  %292 = sext i32 %291 to i64
  %293 = getelementptr float, float* %286, i64 %292
  store float %285, float* %293, align 4
  %294 = fmul reassoc ninf nsz float %273, %273
  %295 = fmul reassoc ninf nsz float %275, %275
  %296 = fadd reassoc ninf nsz float %295, %294
  %297 = load float*, float** %25, align 8
  %298 = load i32, i32* %26, align 4
  %299 = load i32, i32* %27, align 4
  %300 = mul i32 %298, %42
  %301 = add i32 %300, %44
  %302 = mul i32 %301, %299
  %303 = add i32 %302, 3
  %304 = sext i32 %303 to i64
  %305 = getelementptr float, float* %297, i64 %304
  store float %296, float* %305, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.round.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
