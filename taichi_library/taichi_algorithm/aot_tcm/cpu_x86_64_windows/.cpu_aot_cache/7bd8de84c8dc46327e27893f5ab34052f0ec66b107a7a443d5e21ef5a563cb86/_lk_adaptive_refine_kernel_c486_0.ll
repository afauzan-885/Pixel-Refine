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
define void @_lk_adaptive_refine_kernel_c486_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
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
define void @_lk_adaptive_refine_kernel_c486_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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
  %.05387 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %134, %after_if3 ]
  %28 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %28, i64 0, i32 14
  %30 = load i8*, i8** %29, align 8
  %31 = getelementptr inbounds i8, i8* %30, i64 4
  %32 = bitcast i8* %31 to i32*
  %33 = load i32, i32* %32, align 4
  %34 = sdiv i32 %.05387, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.05387
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.05387, 0
  %39 = icmp ne i32 %35, %.05387
  %40 = and i1 %38, %37
  %41 = and i1 %40, %39
  %.neg57 = sext i1 %41 to i32
  %42 = add i32 %34, %.neg57
  %43 = mul i32 %42, %33
  %44 = sub i32 %.05387, %43
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
  %71 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 6
  %72 = load i32, i32* %71, align 4
  %73 = add i32 %65, 1
  %74 = insertelement <2 x i32> poison, i32 %65, i64 0
  %75 = insertelement <2 x i32> %74, i32 %73, i64 1
  %76 = sext <2 x i32> %75 to <2 x i64>
  %77 = insertelement <2 x float*> poison, float* %58, i64 0
  %78 = shufflevector <2 x float*> %77, <2 x float*> poison, <2 x i32> zeroinitializer
  %79 = getelementptr float, <2 x float*> %78, <2 x i64> %76
  %80 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %79, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %81 = sext i32 %50 to i64
  %82 = getelementptr float, float* %45, i64 %81
  %83 = load float, float* %82, align 4
  %84 = add i32 %50, 1
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, float* %45, i64 %85
  %87 = load float, float* %86, align 4
  %88 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 7
  %89 = load i32, i32* %88, align 4
  %90 = icmp sgt i32 %89, 0
  %91 = extractelement <2 x float> %80, i64 0
  %92 = extractelement <2 x float> %80, i64 1
  br i1 %90, label %for_loop_body4.lr.ph, label %true_block24

for_loop_body4.lr.ph:                             ; preds = %true_block1
  %93 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 4
  %94 = load i32, i32* %93, align 4
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 2)
  %96 = sitofp i32 %95 to float
  %97 = add i32 %72, %94
  %98 = shl i32 %97, 1
  %99 = sitofp i32 %98 to float
  %100 = shl i32 %72, 1
  %neg = sub i32 0, %72
  %101 = add i32 %72, 1
  %102 = tail call i32 @llvm.smax.i32(i32 %neg, i32 %101)
  %103 = add i32 %102, %72
  %104 = mul i32 %103, %103
  %105 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 5
  %106 = getelementptr inbounds i8, i8* %30, i64 8
  %107 = bitcast i8* %106 to i32*
  %108 = getelementptr inbounds i8, i8* %30, i64 12
  %109 = bitcast i8* %108 to i32*
  %110 = mul i32 %94, %42
  %111 = mul i32 %94, %44
  %112 = insertelement <2 x i32> <i32 poison, i32 0>, i32 %103, i64 0
  %113 = insertelement <2 x i32> <i32 0, i32 poison>, i32 %104, i64 1
  %114 = icmp slt <2 x i32> %112, %113
  %.neg60 = sub i32 %111, %72
  %115 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 0, i32 1
  %116 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 0, i32 0, i32 1
  %117 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 1, i32 1
  %118 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 1, i32 0, i32 1
  %119 = or i32 %100, 1
  %120 = mul i32 %119, %119
  %121 = sitofp i32 %120 to float
  %neg19 = fneg reassoc ninf nsz float %96
  %neg20 = fneg reassoc ninf nsz float %99
  %122 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float, i32 }* %56, i64 0, i32 8
  %123 = insertelement <2 x float> poison, float %neg20, i64 0
  %124 = shufflevector <2 x float> %123, <2 x float> poison, <2 x i32> zeroinitializer
  %125 = insertelement <2 x float> poison, float %99, i64 0
  %126 = shufflevector <2 x float> %125, <2 x float> poison, <2 x i32> zeroinitializer
  %127 = insertelement <2 x float> poison, float %neg19, i64 0
  %128 = shufflevector <2 x float> %127, <2 x float> poison, <2 x i32> zeroinitializer
  %129 = insertelement <2 x float> poison, float %96, i64 0
  %130 = shufflevector <2 x float> %129, <2 x float> poison, <2 x i32> zeroinitializer
  %131 = extractelement <2 x i1> %114, i64 1
  %min.iters.check = icmp ult i32 %104, 32
  %n.vec = and i32 %104, -32
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %103, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splat147 = shufflevector <2 x i1> %114, <2 x i1> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert154 = insertelement <8 x i32> poison, i32 %72, i64 0
  %broadcast.splat155 = shufflevector <8 x i32> %broadcast.splatinsert154, <8 x i32> poison, <8 x i32> zeroinitializer
  %cmp.n = icmp eq i32 %104, %n.vec
  %132 = extractelement <2 x i1> %114, i64 0
  %133 = mul i32 %103, -1
  br label %for_loop_body4

after_if3:                                        ; preds = %true_block24, %after_for6, %true_block, %for_loop_body
  %134 = add nsw i32 %.05387, 1
  %exitcond94.not = icmp eq i32 %134, %19
  br i1 %exitcond94.not, label %after_for.loopexit, label %for_loop_body

for_loop_body4:                                   ; preds = %after_if10, %for_loop_body4.lr.ph
  %.04081 = phi i32 [ 0, %for_loop_body4.lr.ph ], [ %613, %after_if10 ]
  %.04180 = phi float [ %87, %for_loop_body4.lr.ph ], [ %.1, %after_if10 ]
  %.04279 = phi float [ %83, %for_loop_body4.lr.ph ], [ %.143, %after_if10 ]
  %.04478 = phi i32 [ 1, %for_loop_body4.lr.ph ], [ %.145, %after_if10 ]
  %.04677 = phi i32 [ 1, %for_loop_body4.lr.ph ], [ %.147, %after_if10 ]
  %135 = phi <2 x float> [ %80, %for_loop_body4.lr.ph ], [ %612, %after_if10 ]
  %136 = icmp eq i32 %.04677, 1
  br i1 %136, label %true_block8, label %after_if10

after_for6:                                       ; preds = %after_if10
  %137 = icmp eq i32 %.145, 1
  %138 = extractelement <2 x float> %612, i64 0
  %139 = extractelement <2 x float> %612, i64 1
  br i1 %137, label %true_block24, label %after_if3

true_block8:                                      ; preds = %for_loop_body4
  %140 = load i32, i32* %105, align 4
  %141 = load i32, i32* %107, align 4
  %142 = add i32 %141, -1
  %143 = load i32, i32* %109, align 4
  %144 = add i32 %143, -1
  %145 = add i32 %140, %110
  br i1 %131, label %for_loop_body11.lr.ph, label %after_for13

for_loop_body11.lr.ph:                            ; preds = %true_block8
  %146 = add i32 %.neg60, %140
  %147 = load float*, float** %115, align 8
  %148 = load i32, i32* %116, align 4
  %149 = load float*, float** %117, align 8
  %150 = load i32, i32* %118, align 4
  br i1 %min.iters.check, label %for_loop_body11.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body11.lr.ph
  %broadcast.splatinsert162 = insertelement <8 x i32> poison, i32 %145, i64 0
  %broadcast.splat163 = shufflevector <8 x i32> %broadcast.splatinsert162, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert170 = insertelement <8 x i32> poison, i32 %146, i64 0
  %broadcast.splat171 = shufflevector <8 x i32> %broadcast.splatinsert170, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splat179 = shufflevector <2 x float> %135, <2 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splat187 = shufflevector <2 x float> %135, <2 x float> poison, <8 x i32> <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %broadcast.splatinsert194 = insertelement <8 x i32> poison, i32 %142, i64 0
  %broadcast.splat195 = shufflevector <8 x i32> %broadcast.splatinsert194, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert202 = insertelement <8 x i32> poison, i32 %144, i64 0
  %broadcast.splat203 = shufflevector <8 x i32> %broadcast.splatinsert202, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert210 = insertelement <8 x i32> poison, i32 %148, i64 0
  %broadcast.splat211 = shufflevector <8 x i32> %broadcast.splatinsert210, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert233 = insertelement <8 x i32> poison, i32 %150, i64 0
  %broadcast.splat234 = shufflevector <8 x i32> %broadcast.splatinsert233, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %587, %vector.body ]
  %vec.phi117 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %588, %vector.body ]
  %vec.phi118 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %589, %vector.body ]
  %vec.phi119 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %590, %vector.body ]
  %vec.phi120 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %579, %vector.body ]
  %vec.phi121 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %580, %vector.body ]
  %vec.phi122 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %581, %vector.body ]
  %vec.phi123 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %582, %vector.body ]
  %vec.phi124 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %571, %vector.body ]
  %vec.phi125 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %572, %vector.body ]
  %vec.phi126 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %573, %vector.body ]
  %vec.phi127 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %574, %vector.body ]
  %vec.phi128 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %563, %vector.body ]
  %vec.phi129 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %564, %vector.body ]
  %vec.phi130 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %565, %vector.body ]
  %vec.phi131 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %566, %vector.body ]
  %vec.phi132 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %555, %vector.body ]
  %vec.phi133 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %556, %vector.body ]
  %vec.phi134 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %557, %vector.body ]
  %vec.phi135 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %558, %vector.body ]
  %vec.phi136 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %547, %vector.body ]
  %vec.phi137 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %548, %vector.body ]
  %vec.phi138 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %549, %vector.body ]
  %vec.phi139 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %550, %vector.body ]
  %step.add = add <8 x i32> %vec.ind, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %step.add114 = add <8 x i32> %vec.ind, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %step.add115 = add <8 x i32> %vec.ind, <i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24>
  %151 = sdiv <8 x i32> %vec.ind, %broadcast.splat
  %152 = sdiv <8 x i32> %step.add, %broadcast.splat
  %153 = sdiv <8 x i32> %step.add114, %broadcast.splat
  %154 = sdiv <8 x i32> %step.add115, %broadcast.splat
  %155 = mul <8 x i32> %151, %broadcast.splat
  %156 = mul <8 x i32> %152, %broadcast.splat
  %157 = mul <8 x i32> %153, %broadcast.splat
  %158 = mul <8 x i32> %154, %broadcast.splat
  %159 = icmp ne <8 x i32> %vec.ind, zeroinitializer
  %160 = icmp ne <8 x i32> %step.add, zeroinitializer
  %161 = icmp ne <8 x i32> %step.add114, zeroinitializer
  %162 = icmp ne <8 x i32> %step.add115, zeroinitializer
  %163 = icmp ne <8 x i32> %155, %vec.ind
  %164 = icmp ne <8 x i32> %156, %step.add
  %165 = icmp ne <8 x i32> %157, %step.add114
  %166 = icmp ne <8 x i32> %158, %step.add115
  %167 = and <8 x i1> %broadcast.splat147, %159
  %168 = and <8 x i1> %broadcast.splat147, %160
  %169 = and <8 x i1> %broadcast.splat147, %161
  %170 = and <8 x i1> %broadcast.splat147, %162
  %171 = and <8 x i1> %167, %163
  %172 = and <8 x i1> %168, %164
  %173 = and <8 x i1> %169, %165
  %174 = and <8 x i1> %170, %166
  %175 = sext <8 x i1> %171 to <8 x i32>
  %176 = sext <8 x i1> %172 to <8 x i32>
  %177 = sext <8 x i1> %173 to <8 x i32>
  %178 = sext <8 x i1> %174 to <8 x i32>
  %179 = add <8 x i32> %151, %175
  %180 = add <8 x i32> %152, %176
  %181 = add <8 x i32> %153, %177
  %182 = add <8 x i32> %154, %178
  %183 = sub <8 x i32> %179, %broadcast.splat155
  %184 = sub <8 x i32> %180, %broadcast.splat155
  %185 = sub <8 x i32> %181, %broadcast.splat155
  %186 = sub <8 x i32> %182, %broadcast.splat155
  %187 = mul <8 x i32> %179, %broadcast.splat
  %188 = mul <8 x i32> %180, %broadcast.splat
  %189 = mul <8 x i32> %181, %broadcast.splat
  %190 = mul <8 x i32> %182, %broadcast.splat
  %191 = add <8 x i32> %broadcast.splat163, %183
  %192 = add <8 x i32> %broadcast.splat163, %184
  %193 = add <8 x i32> %broadcast.splat163, %185
  %194 = add <8 x i32> %broadcast.splat163, %186
  %195 = add <8 x i32> %broadcast.splat171, %vec.ind
  %196 = add <8 x i32> %broadcast.splat171, %step.add
  %197 = add <8 x i32> %broadcast.splat171, %step.add114
  %198 = add <8 x i32> %broadcast.splat171, %step.add115
  %199 = sub <8 x i32> %195, %187
  %200 = sub <8 x i32> %196, %188
  %201 = sub <8 x i32> %197, %189
  %202 = sub <8 x i32> %198, %190
  %203 = sitofp <8 x i32> %191 to <8 x float>
  %204 = sitofp <8 x i32> %192 to <8 x float>
  %205 = sitofp <8 x i32> %193 to <8 x float>
  %206 = sitofp <8 x i32> %194 to <8 x float>
  %207 = sitofp <8 x i32> %199 to <8 x float>
  %208 = sitofp <8 x i32> %200 to <8 x float>
  %209 = sitofp <8 x i32> %201 to <8 x float>
  %210 = sitofp <8 x i32> %202 to <8 x float>
  %211 = fadd reassoc ninf nsz <8 x float> %broadcast.splat179, %207
  %212 = fadd reassoc ninf nsz <8 x float> %broadcast.splat179, %208
  %213 = fadd reassoc ninf nsz <8 x float> %broadcast.splat179, %209
  %214 = fadd reassoc ninf nsz <8 x float> %broadcast.splat179, %210
  %215 = fadd reassoc ninf nsz <8 x float> %broadcast.splat187, %203
  %216 = fadd reassoc ninf nsz <8 x float> %broadcast.splat187, %204
  %217 = fadd reassoc ninf nsz <8 x float> %broadcast.splat187, %205
  %218 = fadd reassoc ninf nsz <8 x float> %broadcast.splat187, %206
  %219 = add <8 x i32> %199, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %220 = add <8 x i32> %200, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %221 = add <8 x i32> %201, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %222 = add <8 x i32> %202, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %223 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %191, <8 x i32> %broadcast.splat195)
  %224 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %192, <8 x i32> %broadcast.splat195)
  %225 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %193, <8 x i32> %broadcast.splat195)
  %226 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %194, <8 x i32> %broadcast.splat195)
  %227 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %223, <8 x i32> zeroinitializer)
  %228 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %224, <8 x i32> zeroinitializer)
  %229 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %225, <8 x i32> zeroinitializer)
  %230 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %226, <8 x i32> zeroinitializer)
  %231 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %219, <8 x i32> %broadcast.splat203)
  %232 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %220, <8 x i32> %broadcast.splat203)
  %233 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %221, <8 x i32> %broadcast.splat203)
  %234 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %222, <8 x i32> %broadcast.splat203)
  %235 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %231, <8 x i32> zeroinitializer)
  %236 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %232, <8 x i32> zeroinitializer)
  %237 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %233, <8 x i32> zeroinitializer)
  %238 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %234, <8 x i32> zeroinitializer)
  %239 = add <8 x i32> %199, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %240 = add <8 x i32> %200, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %241 = add <8 x i32> %201, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %242 = add <8 x i32> %202, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %243 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %239, <8 x i32> %broadcast.splat203)
  %244 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %240, <8 x i32> %broadcast.splat203)
  %245 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %241, <8 x i32> %broadcast.splat203)
  %246 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %242, <8 x i32> %broadcast.splat203)
  %247 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %243, <8 x i32> zeroinitializer)
  %248 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %244, <8 x i32> zeroinitializer)
  %249 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %245, <8 x i32> zeroinitializer)
  %250 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %246, <8 x i32> zeroinitializer)
  %251 = mul <8 x i32> %227, %broadcast.splat211
  %252 = mul <8 x i32> %228, %broadcast.splat211
  %253 = mul <8 x i32> %229, %broadcast.splat211
  %254 = mul <8 x i32> %230, %broadcast.splat211
  %255 = add <8 x i32> %251, %235
  %256 = add <8 x i32> %252, %236
  %257 = add <8 x i32> %253, %237
  %258 = add <8 x i32> %254, %238
  %259 = sext <8 x i32> %255 to <8 x i64>
  %260 = sext <8 x i32> %256 to <8 x i64>
  %261 = sext <8 x i32> %257 to <8 x i64>
  %262 = sext <8 x i32> %258 to <8 x i64>
  %263 = getelementptr float, float* %147, <8 x i64> %259
  %264 = getelementptr float, float* %147, <8 x i64> %260
  %265 = getelementptr float, float* %147, <8 x i64> %261
  %266 = getelementptr float, float* %147, <8 x i64> %262
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %263, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather218 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %264, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather219 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %265, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather220 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %266, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %267 = add <8 x i32> %251, %247
  %268 = add <8 x i32> %252, %248
  %269 = add <8 x i32> %253, %249
  %270 = add <8 x i32> %254, %250
  %271 = sext <8 x i32> %267 to <8 x i64>
  %272 = sext <8 x i32> %268 to <8 x i64>
  %273 = sext <8 x i32> %269 to <8 x i64>
  %274 = sext <8 x i32> %270 to <8 x i64>
  %275 = getelementptr float, float* %147, <8 x i64> %271
  %276 = getelementptr float, float* %147, <8 x i64> %272
  %277 = getelementptr float, float* %147, <8 x i64> %273
  %278 = getelementptr float, float* %147, <8 x i64> %274
  %wide.masked.gather221 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %275, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather222 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %276, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather223 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %277, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather224 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %278, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %279 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather221
  %280 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather218, %wide.masked.gather222
  %281 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather219, %wide.masked.gather223
  %282 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather220, %wide.masked.gather224
  %283 = fmul reassoc ninf nsz <8 x float> %279, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %284 = fmul reassoc ninf nsz <8 x float> %280, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %285 = fmul reassoc ninf nsz <8 x float> %281, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %286 = fmul reassoc ninf nsz <8 x float> %282, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %287 = add <8 x i32> %191, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %288 = add <8 x i32> %192, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %289 = add <8 x i32> %193, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %290 = add <8 x i32> %194, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %291 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %287, <8 x i32> %broadcast.splat195)
  %292 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %288, <8 x i32> %broadcast.splat195)
  %293 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %289, <8 x i32> %broadcast.splat195)
  %294 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %290, <8 x i32> %broadcast.splat195)
  %295 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %291, <8 x i32> zeroinitializer)
  %296 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %292, <8 x i32> zeroinitializer)
  %297 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %293, <8 x i32> zeroinitializer)
  %298 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %294, <8 x i32> zeroinitializer)
  %299 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %199, <8 x i32> %broadcast.splat203)
  %300 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %200, <8 x i32> %broadcast.splat203)
  %301 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %201, <8 x i32> %broadcast.splat203)
  %302 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %202, <8 x i32> %broadcast.splat203)
  %303 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %299, <8 x i32> zeroinitializer)
  %304 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %300, <8 x i32> zeroinitializer)
  %305 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %301, <8 x i32> zeroinitializer)
  %306 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %302, <8 x i32> zeroinitializer)
  %307 = add <8 x i32> %191, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %308 = add <8 x i32> %192, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %309 = add <8 x i32> %193, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %310 = add <8 x i32> %194, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %311 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %307, <8 x i32> %broadcast.splat195)
  %312 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %308, <8 x i32> %broadcast.splat195)
  %313 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %309, <8 x i32> %broadcast.splat195)
  %314 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %310, <8 x i32> %broadcast.splat195)
  %315 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %311, <8 x i32> zeroinitializer)
  %316 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %312, <8 x i32> zeroinitializer)
  %317 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %313, <8 x i32> zeroinitializer)
  %318 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %314, <8 x i32> zeroinitializer)
  %319 = mul <8 x i32> %295, %broadcast.splat211
  %320 = mul <8 x i32> %296, %broadcast.splat211
  %321 = mul <8 x i32> %297, %broadcast.splat211
  %322 = mul <8 x i32> %298, %broadcast.splat211
  %323 = add <8 x i32> %319, %303
  %324 = add <8 x i32> %320, %304
  %325 = add <8 x i32> %321, %305
  %326 = add <8 x i32> %322, %306
  %327 = sext <8 x i32> %323 to <8 x i64>
  %328 = sext <8 x i32> %324 to <8 x i64>
  %329 = sext <8 x i32> %325 to <8 x i64>
  %330 = sext <8 x i32> %326 to <8 x i64>
  %331 = getelementptr float, float* %147, <8 x i64> %327
  %332 = getelementptr float, float* %147, <8 x i64> %328
  %333 = getelementptr float, float* %147, <8 x i64> %329
  %334 = getelementptr float, float* %147, <8 x i64> %330
  %wide.masked.gather225 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %331, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather226 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %332, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather227 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %333, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather228 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %334, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %335 = mul <8 x i32> %315, %broadcast.splat211
  %336 = mul <8 x i32> %316, %broadcast.splat211
  %337 = mul <8 x i32> %317, %broadcast.splat211
  %338 = mul <8 x i32> %318, %broadcast.splat211
  %339 = add <8 x i32> %335, %303
  %340 = add <8 x i32> %336, %304
  %341 = add <8 x i32> %337, %305
  %342 = add <8 x i32> %338, %306
  %343 = sext <8 x i32> %339 to <8 x i64>
  %344 = sext <8 x i32> %340 to <8 x i64>
  %345 = sext <8 x i32> %341 to <8 x i64>
  %346 = sext <8 x i32> %342 to <8 x i64>
  %347 = getelementptr float, float* %147, <8 x i64> %343
  %348 = getelementptr float, float* %147, <8 x i64> %344
  %349 = getelementptr float, float* %147, <8 x i64> %345
  %350 = getelementptr float, float* %147, <8 x i64> %346
  %wide.masked.gather229 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %347, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather230 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %348, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather231 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %349, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather232 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %350, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %351 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather225, %wide.masked.gather229
  %352 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather226, %wide.masked.gather230
  %353 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather227, %wide.masked.gather231
  %354 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather228, %wide.masked.gather232
  %355 = fmul reassoc ninf nsz <8 x float> %351, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %356 = fmul reassoc ninf nsz <8 x float> %352, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %357 = fmul reassoc ninf nsz <8 x float> %353, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %358 = fmul reassoc ninf nsz <8 x float> %354, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %359 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %211)
  %360 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %212)
  %361 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %213)
  %362 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %214)
  %363 = fptosi <8 x float> %359 to <8 x i32>
  %364 = fptosi <8 x float> %360 to <8 x i32>
  %365 = fptosi <8 x float> %361 to <8 x i32>
  %366 = fptosi <8 x float> %362 to <8 x i32>
  %367 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %363, <8 x i32> %broadcast.splat203)
  %368 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %364, <8 x i32> %broadcast.splat203)
  %369 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %365, <8 x i32> %broadcast.splat203)
  %370 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %366, <8 x i32> %broadcast.splat203)
  %371 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %367, <8 x i32> zeroinitializer)
  %372 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %368, <8 x i32> zeroinitializer)
  %373 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %369, <8 x i32> zeroinitializer)
  %374 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %370, <8 x i32> zeroinitializer)
  %375 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %215)
  %376 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %216)
  %377 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %217)
  %378 = call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %218)
  %379 = fptosi <8 x float> %375 to <8 x i32>
  %380 = fptosi <8 x float> %376 to <8 x i32>
  %381 = fptosi <8 x float> %377 to <8 x i32>
  %382 = fptosi <8 x float> %378 to <8 x i32>
  %383 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %379, <8 x i32> %broadcast.splat195)
  %384 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %380, <8 x i32> %broadcast.splat195)
  %385 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %381, <8 x i32> %broadcast.splat195)
  %386 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %382, <8 x i32> %broadcast.splat195)
  %387 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %383, <8 x i32> zeroinitializer)
  %388 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %384, <8 x i32> zeroinitializer)
  %389 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %385, <8 x i32> zeroinitializer)
  %390 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %386, <8 x i32> zeroinitializer)
  %391 = add nuw <8 x i32> %371, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %392 = add nuw <8 x i32> %372, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %393 = add nuw <8 x i32> %373, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %394 = add nuw <8 x i32> %374, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %395 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %391, <8 x i32> %broadcast.splat203)
  %396 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %392, <8 x i32> %broadcast.splat203)
  %397 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %393, <8 x i32> %broadcast.splat203)
  %398 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %394, <8 x i32> %broadcast.splat203)
  %399 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %395, <8 x i32> zeroinitializer)
  %400 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %396, <8 x i32> zeroinitializer)
  %401 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %397, <8 x i32> zeroinitializer)
  %402 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %398, <8 x i32> zeroinitializer)
  %403 = add nuw <8 x i32> %387, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %404 = add nuw <8 x i32> %388, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %405 = add nuw <8 x i32> %389, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %406 = add nuw <8 x i32> %390, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
  %407 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %403, <8 x i32> %broadcast.splat195)
  %408 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %404, <8 x i32> %broadcast.splat195)
  %409 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %405, <8 x i32> %broadcast.splat195)
  %410 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %406, <8 x i32> %broadcast.splat195)
  %411 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %407, <8 x i32> zeroinitializer)
  %412 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %408, <8 x i32> zeroinitializer)
  %413 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %409, <8 x i32> zeroinitializer)
  %414 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %410, <8 x i32> zeroinitializer)
  %415 = sitofp <8 x i32> %371 to <8 x float>
  %416 = sitofp <8 x i32> %372 to <8 x float>
  %417 = sitofp <8 x i32> %373 to <8 x float>
  %418 = sitofp <8 x i32> %374 to <8 x float>
  %419 = fsub reassoc ninf nsz <8 x float> %211, %415
  %420 = fsub reassoc ninf nsz <8 x float> %212, %416
  %421 = fsub reassoc ninf nsz <8 x float> %213, %417
  %422 = fsub reassoc ninf nsz <8 x float> %214, %418
  %423 = sitofp <8 x i32> %387 to <8 x float>
  %424 = sitofp <8 x i32> %388 to <8 x float>
  %425 = sitofp <8 x i32> %389 to <8 x float>
  %426 = sitofp <8 x i32> %390 to <8 x float>
  %427 = fsub reassoc ninf nsz <8 x float> %215, %423
  %428 = fsub reassoc ninf nsz <8 x float> %216, %424
  %429 = fsub reassoc ninf nsz <8 x float> %217, %425
  %430 = fsub reassoc ninf nsz <8 x float> %218, %426
  %431 = mul <8 x i32> %387, %broadcast.splat234
  %432 = mul <8 x i32> %388, %broadcast.splat234
  %433 = mul <8 x i32> %389, %broadcast.splat234
  %434 = mul <8 x i32> %390, %broadcast.splat234
  %435 = add <8 x i32> %431, %371
  %436 = add <8 x i32> %432, %372
  %437 = add <8 x i32> %433, %373
  %438 = add <8 x i32> %434, %374
  %439 = sext <8 x i32> %435 to <8 x i64>
  %440 = sext <8 x i32> %436 to <8 x i64>
  %441 = sext <8 x i32> %437 to <8 x i64>
  %442 = sext <8 x i32> %438 to <8 x i64>
  %443 = getelementptr float, float* %149, <8 x i64> %439
  %444 = getelementptr float, float* %149, <8 x i64> %440
  %445 = getelementptr float, float* %149, <8 x i64> %441
  %446 = getelementptr float, float* %149, <8 x i64> %442
  %wide.masked.gather241 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %443, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather242 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %444, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather243 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %445, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather244 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %446, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %447 = add <8 x i32> %399, %431
  %448 = add <8 x i32> %400, %432
  %449 = add <8 x i32> %401, %433
  %450 = add <8 x i32> %402, %434
  %451 = sext <8 x i32> %447 to <8 x i64>
  %452 = sext <8 x i32> %448 to <8 x i64>
  %453 = sext <8 x i32> %449 to <8 x i64>
  %454 = sext <8 x i32> %450 to <8 x i64>
  %455 = getelementptr float, float* %149, <8 x i64> %451
  %456 = getelementptr float, float* %149, <8 x i64> %452
  %457 = getelementptr float, float* %149, <8 x i64> %453
  %458 = getelementptr float, float* %149, <8 x i64> %454
  %wide.masked.gather245 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %455, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather246 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %456, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather247 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %457, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather248 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %458, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %459 = mul <8 x i32> %411, %broadcast.splat234
  %460 = mul <8 x i32> %412, %broadcast.splat234
  %461 = mul <8 x i32> %413, %broadcast.splat234
  %462 = mul <8 x i32> %414, %broadcast.splat234
  %463 = add <8 x i32> %459, %371
  %464 = add <8 x i32> %460, %372
  %465 = add <8 x i32> %461, %373
  %466 = add <8 x i32> %462, %374
  %467 = sext <8 x i32> %463 to <8 x i64>
  %468 = sext <8 x i32> %464 to <8 x i64>
  %469 = sext <8 x i32> %465 to <8 x i64>
  %470 = sext <8 x i32> %466 to <8 x i64>
  %471 = getelementptr float, float* %149, <8 x i64> %467
  %472 = getelementptr float, float* %149, <8 x i64> %468
  %473 = getelementptr float, float* %149, <8 x i64> %469
  %474 = getelementptr float, float* %149, <8 x i64> %470
  %wide.masked.gather249 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %471, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather250 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %472, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather251 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %473, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather252 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %474, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %475 = add <8 x i32> %459, %399
  %476 = add <8 x i32> %460, %400
  %477 = add <8 x i32> %461, %401
  %478 = add <8 x i32> %462, %402
  %479 = sext <8 x i32> %475 to <8 x i64>
  %480 = sext <8 x i32> %476 to <8 x i64>
  %481 = sext <8 x i32> %477 to <8 x i64>
  %482 = sext <8 x i32> %478 to <8 x i64>
  %483 = getelementptr float, float* %149, <8 x i64> %479
  %484 = getelementptr float, float* %149, <8 x i64> %480
  %485 = getelementptr float, float* %149, <8 x i64> %481
  %486 = getelementptr float, float* %149, <8 x i64> %482
  %wide.masked.gather253 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %483, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather254 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %484, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather255 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %485, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather256 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %486, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %487 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %419
  %488 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %420
  %489 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %421
  %490 = fsub reassoc ninf nsz <8 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>, %422
  %491 = fmul reassoc ninf nsz <8 x float> %487, %wide.masked.gather241
  %492 = fmul reassoc ninf nsz <8 x float> %488, %wide.masked.gather242
  %493 = fmul reassoc ninf nsz <8 x float> %489, %wide.masked.gather243
  %494 = fmul reassoc ninf nsz <8 x float> %490, %wide.masked.gather244
  %495 = fmul reassoc ninf nsz <8 x float> %419, %wide.masked.gather245
  %496 = fmul reassoc ninf nsz <8 x float> %420, %wide.masked.gather246
  %497 = fmul reassoc ninf nsz <8 x float> %421, %wide.masked.gather247
  %498 = fmul reassoc ninf nsz <8 x float> %422, %wide.masked.gather248
  %499 = fadd reassoc ninf nsz <8 x float> %491, %495
  %500 = fadd reassoc ninf nsz <8 x float> %492, %496
  %501 = fadd reassoc ninf nsz <8 x float> %493, %497
  %502 = fadd reassoc ninf nsz <8 x float> %494, %498
  %503 = fmul reassoc ninf nsz <8 x float> %487, %wide.masked.gather249
  %504 = fmul reassoc ninf nsz <8 x float> %488, %wide.masked.gather250
  %505 = fmul reassoc ninf nsz <8 x float> %489, %wide.masked.gather251
  %506 = fmul reassoc ninf nsz <8 x float> %490, %wide.masked.gather252
  %507 = fmul reassoc ninf nsz <8 x float> %419, %wide.masked.gather253
  %508 = fmul reassoc ninf nsz <8 x float> %420, %wide.masked.gather254
  %509 = fmul reassoc ninf nsz <8 x float> %421, %wide.masked.gather255
  %510 = fmul reassoc ninf nsz <8 x float> %422, %wide.masked.gather256
  %511 = fadd reassoc ninf nsz <8 x float> %503, %507
  %512 = fadd reassoc ninf nsz <8 x float> %504, %508
  %513 = fadd reassoc ninf nsz <8 x float> %505, %509
  %514 = fadd reassoc ninf nsz <8 x float> %506, %510
  %515 = fsub reassoc ninf nsz <8 x float> %511, %499
  %516 = fsub reassoc ninf nsz <8 x float> %512, %500
  %517 = fsub reassoc ninf nsz <8 x float> %513, %501
  %518 = fsub reassoc ninf nsz <8 x float> %514, %502
  %519 = fmul reassoc ninf nsz <8 x float> %515, %427
  %520 = fmul reassoc ninf nsz <8 x float> %516, %428
  %521 = fmul reassoc ninf nsz <8 x float> %517, %429
  %522 = fmul reassoc ninf nsz <8 x float> %518, %430
  %523 = add <8 x i32> %251, %303
  %524 = add <8 x i32> %252, %304
  %525 = add <8 x i32> %253, %305
  %526 = add <8 x i32> %254, %306
  %527 = sext <8 x i32> %523 to <8 x i64>
  %528 = sext <8 x i32> %524 to <8 x i64>
  %529 = sext <8 x i32> %525 to <8 x i64>
  %530 = sext <8 x i32> %526 to <8 x i64>
  %531 = getelementptr float, float* %147, <8 x i64> %527
  %532 = getelementptr float, float* %147, <8 x i64> %528
  %533 = getelementptr float, float* %147, <8 x i64> %529
  %534 = getelementptr float, float* %147, <8 x i64> %530
  %wide.masked.gather257 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %531, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather258 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %532, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather259 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %533, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %wide.masked.gather260 = call <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*> %534, i32 4, <8 x i1> <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>, <8 x float> undef)
  %535 = fsub reassoc ninf nsz <8 x float> %499, %wide.masked.gather257
  %536 = fsub reassoc ninf nsz <8 x float> %500, %wide.masked.gather258
  %537 = fsub reassoc ninf nsz <8 x float> %501, %wide.masked.gather259
  %538 = fsub reassoc ninf nsz <8 x float> %502, %wide.masked.gather260
  %539 = fadd reassoc ninf nsz <8 x float> %535, %519
  %540 = fadd reassoc ninf nsz <8 x float> %536, %520
  %541 = fadd reassoc ninf nsz <8 x float> %537, %521
  %542 = fadd reassoc ninf nsz <8 x float> %538, %522
  %543 = fmul reassoc ninf nsz <8 x float> %283, %283
  %544 = fmul reassoc ninf nsz <8 x float> %284, %284
  %545 = fmul reassoc ninf nsz <8 x float> %285, %285
  %546 = fmul reassoc ninf nsz <8 x float> %286, %286
  %547 = fadd reassoc ninf nsz <8 x float> %543, %vec.phi136
  %548 = fadd reassoc ninf nsz <8 x float> %544, %vec.phi137
  %549 = fadd reassoc ninf nsz <8 x float> %545, %vec.phi138
  %550 = fadd reassoc ninf nsz <8 x float> %546, %vec.phi139
  %551 = fmul reassoc ninf nsz <8 x float> %355, %283
  %552 = fmul reassoc ninf nsz <8 x float> %356, %284
  %553 = fmul reassoc ninf nsz <8 x float> %357, %285
  %554 = fmul reassoc ninf nsz <8 x float> %358, %286
  %555 = fadd reassoc ninf nsz <8 x float> %551, %vec.phi132
  %556 = fadd reassoc ninf nsz <8 x float> %552, %vec.phi133
  %557 = fadd reassoc ninf nsz <8 x float> %553, %vec.phi134
  %558 = fadd reassoc ninf nsz <8 x float> %554, %vec.phi135
  %559 = fmul reassoc ninf nsz <8 x float> %355, %355
  %560 = fmul reassoc ninf nsz <8 x float> %356, %356
  %561 = fmul reassoc ninf nsz <8 x float> %357, %357
  %562 = fmul reassoc ninf nsz <8 x float> %358, %358
  %563 = fadd reassoc ninf nsz <8 x float> %559, %vec.phi128
  %564 = fadd reassoc ninf nsz <8 x float> %560, %vec.phi129
  %565 = fadd reassoc ninf nsz <8 x float> %561, %vec.phi130
  %566 = fadd reassoc ninf nsz <8 x float> %562, %vec.phi131
  %567 = fmul reassoc ninf nsz <8 x float> %539, %283
  %568 = fmul reassoc ninf nsz <8 x float> %540, %284
  %569 = fmul reassoc ninf nsz <8 x float> %541, %285
  %570 = fmul reassoc ninf nsz <8 x float> %542, %286
  %571 = fadd reassoc ninf nsz <8 x float> %567, %vec.phi124
  %572 = fadd reassoc ninf nsz <8 x float> %568, %vec.phi125
  %573 = fadd reassoc ninf nsz <8 x float> %569, %vec.phi126
  %574 = fadd reassoc ninf nsz <8 x float> %570, %vec.phi127
  %575 = fmul reassoc ninf nsz <8 x float> %539, %355
  %576 = fmul reassoc ninf nsz <8 x float> %540, %356
  %577 = fmul reassoc ninf nsz <8 x float> %541, %357
  %578 = fmul reassoc ninf nsz <8 x float> %542, %358
  %579 = fadd reassoc ninf nsz <8 x float> %575, %vec.phi120
  %580 = fadd reassoc ninf nsz <8 x float> %576, %vec.phi121
  %581 = fadd reassoc ninf nsz <8 x float> %577, %vec.phi122
  %582 = fadd reassoc ninf nsz <8 x float> %578, %vec.phi123
  %583 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %539)
  %584 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %540)
  %585 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %541)
  %586 = call <8 x float> @llvm.fabs.v8f32(<8 x float> %542)
  %587 = fadd reassoc ninf nsz <8 x float> %583, %vec.phi
  %588 = fadd reassoc ninf nsz <8 x float> %584, %vec.phi117
  %589 = fadd reassoc ninf nsz <8 x float> %585, %vec.phi118
  %590 = fadd reassoc ninf nsz <8 x float> %586, %vec.phi119
  %vec.ind.next = add <8 x i32> %vec.ind, <i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32, i32 32>
  %lsr.iv.next = add i32 %lsr.iv, -32
  %591 = icmp eq i32 %lsr.iv.next, 0
  br i1 %591, label %middle.block, label %vector.body, !llvm.loop !9

middle.block:                                     ; preds = %vector.body
  %bin.rdx279 = fadd reassoc ninf nsz <8 x float> %548, %547
  %bin.rdx280 = fadd reassoc ninf nsz <8 x float> %549, %bin.rdx279
  %bin.rdx281 = fadd reassoc ninf nsz <8 x float> %550, %bin.rdx280
  %592 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx281)
  %bin.rdx275 = fadd reassoc ninf nsz <8 x float> %556, %555
  %bin.rdx276 = fadd reassoc ninf nsz <8 x float> %557, %bin.rdx275
  %bin.rdx277 = fadd reassoc ninf nsz <8 x float> %558, %bin.rdx276
  %593 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx277)
  %bin.rdx271 = fadd reassoc ninf nsz <8 x float> %564, %563
  %bin.rdx272 = fadd reassoc ninf nsz <8 x float> %565, %bin.rdx271
  %bin.rdx273 = fadd reassoc ninf nsz <8 x float> %566, %bin.rdx272
  %594 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx273)
  %bin.rdx267 = fadd reassoc ninf nsz <8 x float> %572, %571
  %bin.rdx268 = fadd reassoc ninf nsz <8 x float> %573, %bin.rdx267
  %bin.rdx269 = fadd reassoc ninf nsz <8 x float> %574, %bin.rdx268
  %595 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx269)
  %bin.rdx263 = fadd reassoc ninf nsz <8 x float> %580, %579
  %bin.rdx264 = fadd reassoc ninf nsz <8 x float> %581, %bin.rdx263
  %bin.rdx265 = fadd reassoc ninf nsz <8 x float> %582, %bin.rdx264
  %596 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx265)
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %588, %587
  %bin.rdx261 = fadd reassoc ninf nsz <8 x float> %589, %bin.rdx
  %bin.rdx262 = fadd reassoc ninf nsz <8 x float> %590, %bin.rdx261
  %597 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx262)
  %598 = insertelement <2 x float> poison, float %596, i64 0
  %599 = insertelement <2 x float> %598, float %595, i64 1
  %600 = insertelement <2 x float> poison, float %594, i64 0
  %601 = insertelement <2 x float> %600, float %592, i64 1
  br i1 %cmp.n, label %after_for13, label %for_loop_body11.preheader

for_loop_body11.preheader:                        ; preds = %middle.block, %for_loop_body11.lr.ph
  %.069.ph = phi i32 [ 0, %for_loop_body11.lr.ph ], [ %n.vec, %middle.block ]
  %.03468.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %597, %middle.block ]
  %.03864.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %593, %middle.block ]
  %.ph = phi <2 x float> [ zeroinitializer, %for_loop_body11.lr.ph ], [ %599, %middle.block ]
  %.ph286 = phi <2 x float> [ zeroinitializer, %for_loop_body11.lr.ph ], [ %601, %middle.block ]
  %602 = extractelement <2 x float> %135, i64 0
  %603 = extractelement <2 x float> %135, i64 1
  %604 = insertelement <2 x i32> poison, i32 %142, i64 0
  %605 = shufflevector <2 x i32> %604, <2 x i32> poison, <2 x i32> zeroinitializer
  %606 = insertelement <2 x i32> poison, i32 %144, i64 0
  %607 = shufflevector <2 x i32> %606, <2 x i32> poison, <2 x i32> zeroinitializer
  %608 = insertelement <2 x i32> poison, i32 %148, i64 0
  %609 = shufflevector <2 x i32> %608, <2 x i32> poison, <2 x i32> zeroinitializer
  %610 = insertelement <2 x float*> poison, float* %147, i64 0
  %611 = shufflevector <2 x float*> %610, <2 x float*> poison, <2 x i32> zeroinitializer
  br label %for_loop_body11

after_if10:                                       ; preds = %true_block21, %false_block16, %after_for13, %for_loop_body4
  %.147 = phi i32 [ 0, %true_block21 ], [ 1, %false_block16 ], [ 0, %for_loop_body4 ], [ 0, %after_for13 ]
  %.145 = phi i32 [ %.04478, %true_block21 ], [ %.04478, %false_block16 ], [ %.04478, %for_loop_body4 ], [ 0, %after_for13 ]
  %.143 = phi float [ %733, %true_block21 ], [ %733, %false_block16 ], [ %.04279, %for_loop_body4 ], [ %733, %after_for13 ]
  %.1 = phi float [ %732, %true_block21 ], [ %732, %false_block16 ], [ %.04180, %for_loop_body4 ], [ %732, %after_for13 ]
  %612 = phi <2 x float> [ %749, %true_block21 ], [ %749, %false_block16 ], [ %135, %for_loop_body4 ], [ %135, %after_for13 ]
  %613 = add nuw nsw i32 %.04081, 1
  %exitcond93.not = icmp eq i32 %613, %89
  br i1 %exitcond93.not, label %after_for6, label %for_loop_body4

for_loop_body11:                                  ; preds = %for_loop_body11, %for_loop_body11.preheader
  %.069 = phi i32 [ %725, %for_loop_body11 ], [ %.069.ph, %for_loop_body11.preheader ]
  %.03468 = phi float [ %724, %for_loop_body11 ], [ %.03468.ph, %for_loop_body11.preheader ]
  %.03864 = phi float [ %716, %for_loop_body11 ], [ %.03864.ph, %for_loop_body11.preheader ]
  %614 = phi <2 x float> [ %722, %for_loop_body11 ], [ %.ph, %for_loop_body11.preheader ]
  %615 = phi <2 x float> [ %718, %for_loop_body11 ], [ %.ph286, %for_loop_body11.preheader ]
  %616 = sdiv i32 %.069, %103
  %617 = mul i32 %616, %103
  %618 = icmp ne i32 %.069, 0
  %619 = icmp ne i32 %.069, %617
  %620 = and i1 %132, %618
  %621 = and i1 %620, %619
  %.neg58 = sext i1 %621 to i32
  %622 = add i32 %616, %.neg58
  %623 = sub i32 %622, %72
  %624 = add i32 %145, %623
  %625 = mul i32 %133, %622
  %626 = add i32 %146, %.069
  %627 = add i32 %626, %625
  %628 = sitofp i32 %624 to float
  %629 = sitofp i32 %627 to float
  %630 = fadd reassoc ninf nsz float %602, %629
  %631 = fadd reassoc ninf nsz float %603, %628
  %632 = add i32 %627, 1
  %633 = add i32 %627, -1
  %634 = tail call i32 @llvm.smin.i32(i32 %633, i32 %144)
  %635 = tail call i32 @llvm.smax.i32(i32 %634, i32 0)
  %636 = add i32 %624, 1
  %637 = insertelement <2 x i32> poison, i32 %636, i64 0
  %638 = insertelement <2 x i32> %637, i32 %624, i64 1
  %639 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %638, <2 x i32> %605)
  %640 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %639, <2 x i32> zeroinitializer)
  %641 = insertelement <2 x i32> poison, i32 %627, i64 0
  %642 = insertelement <2 x i32> %641, i32 %632, i64 1
  %643 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %642, <2 x i32> %607)
  %644 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %643, <2 x i32> zeroinitializer)
  %645 = add i32 %624, -1
  %646 = tail call i32 @llvm.smin.i32(i32 %645, i32 %142)
  %647 = tail call i32 @llvm.smax.i32(i32 %646, i32 0)
  %648 = mul <2 x i32> %640, %609
  %649 = add <2 x i32> %648, %644
  %650 = sext <2 x i32> %649 to <2 x i64>
  %651 = getelementptr float, <2 x float*> %611, <2 x i64> %650
  %652 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %651, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %653 = mul i32 %647, %148
  %654 = insertelement <2 x i32> %648, i32 %653, i64 0
  %655 = insertelement <2 x i32> %644, i32 %635, i64 1
  %656 = add <2 x i32> %654, %655
  %657 = sext <2 x i32> %656 to <2 x i64>
  %658 = getelementptr float, <2 x float*> %611, <2 x i64> %657
  %659 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %658, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %660 = fsub reassoc ninf nsz <2 x float> %652, %659
  %661 = fmul reassoc ninf nsz <2 x float> %660, <float 5.000000e-01, float 5.000000e-01>
  %662 = tail call reassoc ninf nsz float @llvm.floor.f32(float %630)
  %663 = fptosi float %662 to i32
  %664 = tail call i32 @llvm.smin.i32(i32 %663, i32 %144)
  %665 = tail call i32 @llvm.smax.i32(i32 %664, i32 0)
  %666 = tail call reassoc ninf nsz float @llvm.floor.f32(float %631)
  %667 = fptosi float %666 to i32
  %668 = tail call i32 @llvm.smin.i32(i32 %667, i32 %142)
  %669 = tail call i32 @llvm.smax.i32(i32 %668, i32 0)
  %670 = add nuw i32 %665, 1
  %671 = tail call i32 @llvm.smin.i32(i32 %670, i32 %144)
  %672 = tail call i32 @llvm.smax.i32(i32 %671, i32 0)
  %673 = add nuw i32 %669, 1
  %674 = tail call i32 @llvm.smin.i32(i32 %673, i32 %142)
  %675 = tail call i32 @llvm.smax.i32(i32 %674, i32 0)
  %676 = sitofp i32 %665 to float
  %677 = fsub reassoc ninf nsz float %630, %676
  %678 = sitofp i32 %669 to float
  %679 = fsub reassoc ninf nsz float %631, %678
  %680 = mul i32 %669, %150
  %681 = add i32 %680, %665
  %682 = sext i32 %681 to i64
  %683 = getelementptr float, float* %149, i64 %682
  %684 = load float, float* %683, align 4
  %685 = add i32 %672, %680
  %686 = sext i32 %685 to i64
  %687 = getelementptr float, float* %149, i64 %686
  %688 = load float, float* %687, align 4
  %689 = mul i32 %675, %150
  %690 = add i32 %689, %665
  %691 = sext i32 %690 to i64
  %692 = getelementptr float, float* %149, i64 %691
  %693 = load float, float* %692, align 4
  %694 = add i32 %689, %672
  %695 = sext i32 %694 to i64
  %696 = getelementptr float, float* %149, i64 %695
  %697 = load float, float* %696, align 4
  %698 = fsub reassoc ninf nsz float 1.000000e+00, %677
  %699 = fmul reassoc ninf nsz float %698, %684
  %700 = fmul reassoc ninf nsz float %677, %688
  %701 = fadd reassoc ninf nsz float %699, %700
  %702 = fmul reassoc ninf nsz float %698, %693
  %703 = fmul reassoc ninf nsz float %677, %697
  %704 = fadd reassoc ninf nsz float %702, %703
  %705 = fsub reassoc ninf nsz float %704, %701
  %706 = fmul reassoc ninf nsz float %705, %679
  %shift = shufflevector <2 x i32> %648, <2 x i32> poison, <2 x i32> <i32 1, i32 undef>
  %707 = add <2 x i32> %shift, %644
  %708 = extractelement <2 x i32> %707, i64 0
  %709 = sext i32 %708 to i64
  %710 = getelementptr float, float* %147, i64 %709
  %711 = load float, float* %710, align 4
  %712 = fsub reassoc ninf nsz float %701, %711
  %713 = fadd reassoc ninf nsz float %712, %706
  %shift283 = shufflevector <2 x float> %661, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %714 = fmul reassoc ninf nsz <2 x float> %661, %shift283
  %715 = extractelement <2 x float> %714, i64 0
  %716 = fadd reassoc ninf nsz float %715, %.03864
  %717 = fmul reassoc ninf nsz <2 x float> %661, %661
  %718 = fadd reassoc ninf nsz <2 x float> %717, %615
  %719 = insertelement <2 x float> poison, float %713, i64 0
  %720 = shufflevector <2 x float> %719, <2 x float> poison, <2 x i32> zeroinitializer
  %721 = fmul reassoc ninf nsz <2 x float> %720, %661
  %722 = fadd reassoc ninf nsz <2 x float> %721, %614
  %723 = tail call float @llvm.fabs.f32(float %713)
  %724 = fadd reassoc ninf nsz float %723, %.03468
  %725 = add nuw nsw i32 %.069, 1
  %exitcond.not = icmp eq i32 %104, %725
  br i1 %exitcond.not, label %after_for13.loopexit, label %for_loop_body11, !llvm.loop !11

after_for13.loopexit:                             ; preds = %for_loop_body11
  br label %after_for13

after_for13:                                      ; preds = %after_for13.loopexit, %middle.block, %true_block8
  %.038.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %593, %middle.block ], [ %716, %after_for13.loopexit ]
  %.034.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %597, %middle.block ], [ %724, %after_for13.loopexit ]
  %726 = phi <2 x float> [ zeroinitializer, %true_block8 ], [ %599, %middle.block ], [ %722, %after_for13.loopexit ]
  %727 = phi <2 x float> [ zeroinitializer, %true_block8 ], [ %601, %middle.block ], [ %718, %after_for13.loopexit ]
  %shift284 = shufflevector <2 x float> %727, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %728 = fmul reassoc ninf nsz <2 x float> %727, %shift284
  %729 = extractelement <2 x float> %728, i64 0
  %730 = fmul reassoc ninf nsz float %.038.lcssa, %.038.lcssa
  %731 = fsub reassoc ninf nsz float %729, %730
  %732 = tail call float @llvm.fabs.f32(float %731)
  %733 = fdiv reassoc ninf nsz float %.034.lcssa, %121
  %734 = fcmp reassoc ninf nsz olt float %732, 0x3F1A36E2E0000000
  br i1 %734, label %after_if10, label %false_block16

false_block16:                                    ; preds = %after_for13
  %735 = fdiv reassoc ninf nsz float 1.000000e+00, %731
  %736 = insertelement <2 x float> poison, float %.038.lcssa, i64 0
  %737 = shufflevector <2 x float> %736, <2 x float> poison, <2 x i32> zeroinitializer
  %738 = fmul reassoc ninf nsz <2 x float> %726, %737
  %739 = shufflevector <2 x float> %726, <2 x float> poison, <2 x i32> <i32 1, i32 0>
  %740 = fmul reassoc ninf nsz <2 x float> %739, %727
  %741 = fsub reassoc ninf nsz <2 x float> %738, %740
  %742 = insertelement <2 x float> poison, float %735, i64 0
  %743 = shufflevector <2 x float> %742, <2 x float> poison, <2 x i32> zeroinitializer
  %744 = fmul reassoc ninf nsz <2 x float> %741, %743
  %745 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %130, <2 x float> %744)
  %746 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %128, <2 x float> %745)
  %747 = fadd reassoc ninf nsz <2 x float> %746, %135
  %748 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %126, <2 x float> %747)
  %749 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %124, <2 x float> %748)
  %750 = fmul reassoc ninf nsz <2 x float> %746, %746
  %shift285 = shufflevector <2 x float> %750, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %751 = fadd reassoc ninf nsz <2 x float> %750, %shift285
  %752 = extractelement <2 x float> %751, i64 0
  %753 = load float, float* %122, align 4
  %754 = fmul reassoc ninf nsz float %753, %753
  %755 = fcmp reassoc ninf nsz olt float %752, %754
  br i1 %755, label %true_block21, label %after_if10

true_block21:                                     ; preds = %false_block16
  br label %after_if10

true_block24:                                     ; preds = %after_for6, %true_block1
  %.041.lcssa103 = phi float [ %.1, %after_for6 ], [ %87, %true_block1 ]
  %.042.lcssa102 = phi float [ %.143, %after_for6 ], [ %83, %true_block1 ]
  %.048.lcssa101 = phi float [ %139, %after_for6 ], [ %92, %true_block1 ]
  %.050.lcssa100 = phi float [ %138, %after_for6 ], [ %91, %true_block1 ]
  %756 = extractelement <2 x float*> %79, i64 0
  store float %.050.lcssa100, float* %756, align 4
  %757 = extractelement <2 x float*> %79, i64 1
  store float %.048.lcssa101, float* %757, align 4
  store float %.042.lcssa102, float* %82, align 4
  store float %.041.lcssa103, float* %86, align 4
  %758 = fmul reassoc ninf nsz float %.050.lcssa100, %.050.lcssa100
  %759 = fmul reassoc ninf nsz float %.048.lcssa101, %.048.lcssa101
  %760 = fadd reassoc ninf nsz float %759, %758
  %761 = load float*, float** %25, align 8
  %762 = load i32, i32* %26, align 4
  %763 = load i32, i32* %27, align 4
  %764 = mul i32 %762, %42
  %765 = add i32 %764, %44
  %766 = mul i32 %765, %763
  %767 = add i32 %766, 3
  %768 = sext i32 %767 to i64
  %769 = getelementptr float, float* %761, i64 %768
  store float %760, float* %769, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !13

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !15

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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x float> @llvm.masked.gather.v8f32.v8p0f32(<8 x float*>, i32 immarg, <8 x i1>, <8 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.floor.v8f32(<8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #9

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.minnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.maxnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }
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
!10 = !{!"llvm.loop.isvectorized", i32 1}
!11 = distinct !{!11, !12, !10}
!12 = !{!"llvm.loop.unroll.runtime.disable"}
!13 = distinct !{!13, !14}
!14 = !{!"llvm.loop.mustprogress"}
!15 = distinct !{!15, !14}
