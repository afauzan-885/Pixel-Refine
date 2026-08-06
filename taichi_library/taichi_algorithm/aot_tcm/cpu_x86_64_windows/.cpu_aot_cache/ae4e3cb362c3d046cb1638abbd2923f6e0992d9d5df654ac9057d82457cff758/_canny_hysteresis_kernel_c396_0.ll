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
define void @_canny_hysteresis_kernel_c396_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }* %11, i64 0, i32 3
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
define void @_canny_hysteresis_kernel_c396_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.048 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %90, %after_if ]
  %25 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  %30 = load i32, i32* %29, align 4
  %31 = sdiv i32 %.048, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.048
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %.048, 0
  %36 = icmp ne i32 %.048, %32
  %37 = and i1 %35, %34
  %38 = and i1 %37, %36
  %.neg5 = sext i1 %38 to i32
  %39 = add i32 %31, %.neg5
  %40 = mul i32 %30, -1
  %41 = mul i32 %40, %39
  %42 = add i32 %.048, %41
  %43 = load float*, float** %23, align 8
  %44 = load i32, i32* %24, align 4
  %45 = sub i32 %44, %30
  %46 = mul i32 %45, %39
  %47 = add i32 %.048, %46
  %48 = sext i32 %47 to i64
  %49 = getelementptr float, float* %43, i64 %48
  %50 = load float, float* %49, align 4
  %51 = fcmp reassoc ninf nsz oeq float %50, 1.280000e+02
  br i1 %51, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %52 = add i32 %39, -1
  %53 = getelementptr inbounds i8, i8* %27, i64 8
  %54 = bitcast i8* %53 to i32*
  %55 = load i32, i32* %54, align 4
  %56 = add i32 %55, -1
  %57 = tail call i32 @llvm.smax.i32(i32 %52, i32 0)
  %58 = tail call i32 @llvm.smin.i32(i32 %56, i32 %57)
  %59 = insertelement <2 x i32> poison, i32 %42, i64 0
  %60 = shufflevector <2 x i32> %59, <2 x i32> poison, <2 x i32> zeroinitializer
  %61 = add <2 x i32> %60, <i32 1, i32 -1>
  %62 = getelementptr inbounds i8, i8* %27, i64 12
  %63 = bitcast i8* %62 to i32*
  %64 = load i32, i32* %63, align 4
  %65 = add i32 %64, -1
  %66 = mul i32 %58, %44
  %67 = tail call i32 @llvm.smax.i32(i32 %42, i32 0)
  %68 = tail call i32 @llvm.smin.i32(i32 %65, i32 %67)
  %69 = add i32 %66, %68
  %70 = sext i32 %69 to i64
  %71 = getelementptr float, float* %43, i64 %70
  %72 = load float, float* %71, align 4
  %73 = fcmp reassoc ninf nsz oeq float %72, 2.550000e+02
  %74 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %61, <2 x i32> zeroinitializer)
  %75 = insertelement <2 x i32> poison, i32 %65, i64 0
  %76 = shufflevector <2 x i32> %75, <2 x i32> poison, <2 x i32> zeroinitializer
  %77 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %76, <2 x i32> %74)
  %78 = extractelement <2 x i32> %77, i64 1
  %79 = add i32 %66, %78
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, float* %43, i64 %80
  %82 = load float, float* %81, align 4
  %83 = fcmp reassoc ninf nsz oeq float %82, 2.550000e+02
  %.1 = select i1 %73, i1 true, i1 %83
  %84 = extractelement <2 x i32> %77, i64 0
  %85 = add i32 %66, %84
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, float* %43, i64 %86
  %88 = load float, float* %87, align 4
  %89 = fcmp reassoc ninf nsz oeq float %88, 2.550000e+02
  br i1 %89, label %true_block7, label %after_if9

after_if:                                         ; preds = %true_block25, %after_if21, %for_loop_body
  %90 = add nsw i32 %.048, 1
  %exitcond.not = icmp eq i32 %19, %90
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block7:                                      ; preds = %true_block
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %true_block
  %.2 = phi i1 [ true, %true_block7 ], [ %.1, %true_block ]
  %91 = tail call i32 @llvm.smax.i32(i32 %39, i32 0)
  %92 = tail call i32 @llvm.smin.i32(i32 %56, i32 %91)
  %93 = mul i32 %92, %44
  %94 = add i32 %93, %78
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, float* %43, i64 %95
  %97 = load float, float* %96, align 4
  %98 = fcmp reassoc ninf nsz oeq float %97, 2.550000e+02
  %.3 = select i1 %98, i1 true, i1 %.2
  %99 = add i32 %93, %84
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %43, i64 %100
  %102 = load float, float* %101, align 4
  %103 = fcmp reassoc ninf nsz oeq float %102, 2.550000e+02
  br i1 %103, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if9
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if9
  %.4 = phi i1 [ true, %true_block13 ], [ %.3, %after_if9 ]
  %104 = add i32 %39, 1
  %105 = tail call i32 @llvm.smax.i32(i32 %104, i32 0)
  %106 = tail call i32 @llvm.smin.i32(i32 %56, i32 %105)
  %107 = mul i32 %106, %44
  %108 = add i32 %107, %68
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %43, i64 %109
  %111 = load float, float* %110, align 4
  %112 = fcmp reassoc ninf nsz oeq float %111, 2.550000e+02
  br i1 %112, label %true_block25, label %after_if21

after_if21:                                       ; preds = %after_if15
  %113 = insertelement <2 x i32> poison, i32 %107, i64 0
  %114 = shufflevector <2 x i32> %113, <2 x i32> poison, <2 x i32> zeroinitializer
  %115 = add <2 x i32> %114, %77
  %116 = sext <2 x i32> %115 to <2 x i64>
  %117 = insertelement <2 x float*> poison, float* %43, i64 0
  %118 = shufflevector <2 x float*> %117, <2 x float*> poison, <2 x i32> zeroinitializer
  %119 = getelementptr float, <2 x float*> %118, <2 x i64> %116
  %120 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %119, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %121 = fcmp reassoc ninf nsz oeq <2 x float> %120, <float 2.550000e+02, float 2.550000e+02>
  %122 = extractelement <2 x i1> %121, i64 0
  %123 = extractelement <2 x i1> %121, i64 1
  %124 = select i1 %122, i1 true, i1 %123
  %.7 = select i1 %124, i1 true, i1 %.4
  br i1 %.7, label %true_block25, label %after_if

true_block25:                                     ; preds = %after_if21, %after_if15
  store float 2.550000e+02, float* %49, align 4
  %125 = load { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }** %20, align 8
  %126 = getelementptr { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32 }* %125, i64 0, i32 1, i32 1
  %127 = load i32*, i32** %126, align 8
  store i32 1, i32* %127, align 4
  br label %after_if
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #8 = { nocallback nofree nosync nounwind readonly willreturn }

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
