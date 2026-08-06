; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.300*, void (%struct.RuntimeContext.300*, i8*)*, void (%struct.RuntimeContext.300*, i8*, i32)*, void (%struct.RuntimeContext.300*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.300 = type { i8*, %struct.LLVMRuntime.299*, i32, i64* }
%struct.LLVMRuntime.299 = type { %struct.PreallocatedMemoryChunk.295, %struct.PreallocatedMemoryChunk.295, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.296*], [1024 x %struct.NodeManager.297*], [1024 x i8*], i8*, %struct.RandState.298*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.295 = type { i8*, i8*, i64 }
%struct.ListManager.296 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.299* }
%struct.NodeManager.297 = type { %struct.LLVMRuntime.299*, i32, i32, i32, i32, %struct.ListManager.296*, %struct.ListManager.296*, %struct.ListManager.296*, i32 }
%struct.RandState.298 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_mean_division_kernel_c724_1_kernel_0_serial(%struct.RuntimeContext.300* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.300* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.300, %struct.RuntimeContext.300* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.299*, %struct.LLVMRuntime.299** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.299, %struct.LLVMRuntime.299* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %10, i64 0, i32 1, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime.299*, %struct.LLVMRuntime.299** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime.299, %struct.LLVMRuntime.299* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 4
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = mul i32 %12, %3
  %19 = load %struct.LLVMRuntime.299*, %struct.LLVMRuntime.299** %4, align 8
  %20 = getelementptr inbounds %struct.LLVMRuntime.299, %struct.LLVMRuntime.299* %19, i64 0, i32 14
  %21 = bitcast i8** %20 to i32**
  %22 = load i32*, i32** %21, align 8
  store i32 %18, i32* %22, align 4
  ret void
}

; Function Attrs: nounwind
define void @_mean_division_kernel_c724_1_kernel_1_range_for(%struct.RuntimeContext.300* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.300* %context, %struct.RuntimeContext.300** %4, align 8
  store void (%struct.RuntimeContext.300*, i8*)* null, void (%struct.RuntimeContext.300*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.300*, i8*, i32)* @function_body, void (%struct.RuntimeContext.300*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.300*, i8*)* null, void (%struct.RuntimeContext.300*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.300, %struct.RuntimeContext.300* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.299*, %struct.LLVMRuntime.299** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.299, %struct.LLVMRuntime.299* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.299, %struct.LLVMRuntime.299* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.300* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.300, %struct.RuntimeContext.300* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.299*, %struct.LLVMRuntime.299** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.299, %struct.LLVMRuntime.299* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.300* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %22, i64 0, i32 1, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %22, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %114, %after_if ]
  %25 = load %struct.LLVMRuntime.299*, %struct.LLVMRuntime.299** %3, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.299, %struct.LLVMRuntime.299* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  %30 = load i32, i32* %29, align 4
  %31 = srem i32 %.05, %30
  %32 = sdiv i32 %.05, %30
  %33 = getelementptr inbounds i8, i8* %27, i64 8
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = srem i32 %32, %35
  %37 = load float*, float** %23, align 8
  %38 = load i32, i32* %24, align 4
  %39 = mul i32 %38, %36
  %40 = add i32 %39, %31
  %41 = sext i32 %40 to i64
  %42 = getelementptr float, float* %37, i64 %41
  %43 = load float, float* %42, align 4
  %44 = fcmp reassoc ninf nsz ogt float %43, 0x3EB0C6F7A0000000
  %45 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }** %20, align 8
  br i1 %44, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %45, i64 0, i32 0, i32 1
  %47 = load float*, float** %46, align 8
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %45, i64 0, i32 0, i32 0, i32 1
  %49 = load i32, i32* %48, align 4
  %50 = mul i32 %49, %36
  %51 = add i32 %50, %31
  %52 = mul i32 %51, 3
  %53 = sext i32 %52 to i64
  %54 = getelementptr float, float* %47, i64 %53
  %55 = load float, float* %54, align 4
  %56 = insertelement <2 x i32> poison, i32 %52, i64 0
  %57 = shufflevector <2 x i32> %56, <2 x i32> poison, <2 x i32> zeroinitializer
  %58 = add <2 x i32> %57, <i32 1, i32 2>
  %59 = sext <2 x i32> %58 to <2 x i64>
  %60 = insertelement <2 x float*> poison, float* %47, i64 0
  %61 = shufflevector <2 x float*> %60, <2 x float*> poison, <2 x i32> zeroinitializer
  %62 = getelementptr float, <2 x float*> %61, <2 x i64> %59
  %63 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %62, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %64 = fdiv reassoc ninf nsz float %55, %43
  %65 = insertelement <2 x float> poison, float %43, i64 0
  %66 = shufflevector <2 x float> %65, <2 x float> poison, <2 x i32> zeroinitializer
  %67 = fdiv reassoc ninf nsz <2 x float> %63, %66
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %68 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %45, i64 0, i32 2, i32 1
  %69 = load float*, float** %68, align 8
  %70 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %45, i64 0, i32 2, i32 0, i32 1
  %71 = load i32, i32* %70, align 4
  %72 = mul i32 %71, %36
  %73 = add i32 %72, %31
  %74 = mul i32 %73, 3
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, float* %69, i64 %75
  %77 = load float, float* %76, align 4
  %78 = insertelement <2 x i32> poison, i32 %74, i64 0
  %79 = shufflevector <2 x i32> %78, <2 x i32> poison, <2 x i32> zeroinitializer
  %80 = add <2 x i32> %79, <i32 1, i32 2>
  %81 = sext <2 x i32> %80 to <2 x i64>
  %82 = insertelement <2 x float*> poison, float* %69, i64 0
  %83 = shufflevector <2 x float*> %82, <2 x float*> poison, <2 x i32> zeroinitializer
  %84 = getelementptr float, <2 x float*> %83, <2 x i64> %81
  %85 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %84, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  br label %after_if

after_if:                                         ; preds = %false_block, %true_block
  %.sink27 = phi float [ %77, %false_block ], [ %64, %true_block ]
  %86 = phi <2 x float> [ %85, %false_block ], [ %67, %true_block ]
  %87 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %45, i64 0, i32 3, i32 1
  %88 = load float*, float** %87, align 8
  %89 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* } }* %45, i64 0, i32 3, i32 0, i32 1
  %90 = load i32, i32* %89, align 4
  %91 = mul i32 %90, %36
  %92 = add i32 %91, %31
  %93 = mul i32 %92, 3
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, float* %88, i64 %94
  store float %.sink27, float* %95, align 4
  %96 = load float*, float** %87, align 8
  %97 = load i32, i32* %89, align 4
  %98 = mul i32 %97, %36
  %99 = add i32 %98, %31
  %100 = mul i32 %99, 3
  %101 = add i32 %100, 1
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %96, i64 %102
  %104 = extractelement <2 x float> %86, i64 0
  store float %104, float* %103, align 4
  %105 = load float*, float** %87, align 8
  %106 = load i32, i32* %89, align 4
  %107 = mul i32 %106, %36
  %108 = add i32 %107, %31
  %109 = mul i32 %108, 3
  %110 = add i32 %109, 2
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, float* %105, i64 %111
  %113 = extractelement <2 x float> %86, i64 1
  store float %113, float* %112, align 4
  %114 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %114
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.300, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.300**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.300*, %struct.RuntimeContext.300** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.300*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.300*, i8*)*, void (%struct.RuntimeContext.300*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.300*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.300*, i8*, i32)*, void (%struct.RuntimeContext.300*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.300*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.300*, i8*)*, void (%struct.RuntimeContext.300*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.300*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.300* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.300* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.300* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.300, %struct.RuntimeContext.300* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.300* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.300* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.300*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.300* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }

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
