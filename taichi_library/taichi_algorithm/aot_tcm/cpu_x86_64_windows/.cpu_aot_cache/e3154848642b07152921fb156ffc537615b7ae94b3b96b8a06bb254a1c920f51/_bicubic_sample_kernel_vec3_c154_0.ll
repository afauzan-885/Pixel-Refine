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

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_bicubic_sample_kernel_vec3_c154_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  store i32 %3, i32* %8, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bicubic_sample_kernel_vec3_c154_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %3 = alloca [12 x float], align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %0, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  %9 = load i32, i32* %8, align 4
  %10 = add i32 %9, 7
  %11 = sdiv i32 %10, 8
  %12 = icmp slt i32 %10, 0
  %13 = shl nsw i32 %11, 3
  %14 = icmp ne i32 %13, %10
  %15 = and i1 %12, %14
  %.neg = sext i1 %15 to i32
  %16 = add nsw i32 %11, %.neg
  %17 = tail call i32 @llvm.smax.i32(i32 %16, i32 512)
  %18 = mul i32 %17, %2
  %19 = add i32 %18, %17
  %20 = tail call i32 @llvm.smin.i32(i32 %9, i32 %19)
  %21 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %22, i64 0, i32 4
  %24 = load i32, i32* %23, align 4
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %22, i64 0, i32 5
  %26 = load i32, i32* %25, align 4
  %27 = add i32 %24, -1
  %28 = add i32 %26, -1
  %29 = icmp slt i32 %18, %20
  br i1 %29, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %22, i64 0, i32 1, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %32 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 11
  %33 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 10
  %34 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 9
  %35 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 8
  %36 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 7
  %37 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 6
  %38 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 5
  %39 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 4
  %40 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 3
  %41 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 2
  %42 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 1
  %43 = getelementptr inbounds [12 x float], [12 x float]* %3, i64 0, i64 0
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %22, i64 0, i32 0, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %22, i64 0, i32 2, i32 1
  %47 = sext i32 %18 to i64
  %wide.trip.count = sext i32 %20 to i64
  %48 = bitcast [12 x float]* %3 to i8*
  %broadcast.splatinsert77 = insertelement <4 x i32> poison, i32 %27, i64 0
  %broadcast.splat78 = shufflevector <4 x i32> %broadcast.splatinsert77, <4 x i32> poison, <4 x i32> zeroinitializer
  %49 = bitcast [12 x float]* %3 to <12 x float>*
  %50 = mul i32 %18, 3
  %51 = sub i64 %47, %wide.trip.count
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv106 = phi i64 [ %51, %for_loop_body.lr.ph ], [ %lsr.iv.next107, %for_loop_body ]
  %lsr.iv104 = phi i32 [ %18, %for_loop_body.lr.ph ], [ %lsr.iv.next105, %for_loop_body ]
  %lsr.iv = phi i32 [ %50, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %52 = load float*, float** %30, align 8
  %53 = load i32, i32* %31, align 4
  %54 = mul i32 %53, %lsr.iv104
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, float* %52, i64 %55
  %57 = load float, float* %56, align 4
  %58 = add i32 %54, 1
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, float* %52, i64 %59
  %61 = load float, float* %60, align 4
  %62 = tail call reassoc ninf nsz float @llvm.floor.f32(float %61)
  %63 = fptosi float %62 to i32
  %64 = sitofp i32 %63 to float
  call void @llvm.memset.p0i8.i64(i8* noundef nonnull align 4 dereferenceable(48) %48, i8 0, i64 48, i1 false)
  %65 = load float*, float** %44, align 8
  %66 = tail call reassoc ninf nsz float @llvm.floor.f32(float %57)
  %67 = fptosi float %66 to i32
  %68 = add i32 %67, 2
  %69 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %70 = tail call i32 @llvm.smin.i32(i32 %28, i32 %69)
  %71 = add i32 %67, 1
  %72 = tail call i32 @llvm.smax.i32(i32 %71, i32 0)
  %73 = tail call i32 @llvm.smin.i32(i32 %28, i32 %72)
  %74 = tail call i32 @llvm.smax.i32(i32 %67, i32 0)
  %75 = tail call i32 @llvm.smin.i32(i32 %28, i32 %74)
  %76 = add i32 %67, -1
  %77 = tail call i32 @llvm.smax.i32(i32 %76, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %28, i32 %77)
  %79 = sitofp i32 %67 to float
  %80 = fsub reassoc ninf nsz float %57, %79
  %81 = fmul reassoc ninf nsz float %80, %80
  %82 = load i32, i32* %45, align 4
  %83 = add i32 %63, -1
  %broadcast.splatinsert = insertelement <4 x i32> poison, i32 %83, i64 0
  %broadcast.splat = shufflevector <4 x i32> %broadcast.splatinsert, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert79 = insertelement <4 x i32> poison, i32 %82, i64 0
  %broadcast.splat80 = shufflevector <4 x i32> %broadcast.splatinsert79, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert81 = insertelement <4 x i32> poison, i32 %78, i64 0
  %broadcast.splat82 = shufflevector <4 x i32> %broadcast.splatinsert81, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert85 = insertelement <4 x i32> poison, i32 %75, i64 0
  %broadcast.splat86 = shufflevector <4 x i32> %broadcast.splatinsert85, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert90 = insertelement <4 x i32> poison, i32 %73, i64 0
  %broadcast.splat91 = shufflevector <4 x i32> %broadcast.splatinsert90, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert95 = insertelement <4 x i32> poison, i32 %70, i64 0
  %broadcast.splat96 = shufflevector <4 x i32> %broadcast.splatinsert95, <4 x i32> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert100 = insertelement <4 x float> poison, float %80, i64 0
  %broadcast.splat101 = shufflevector <4 x float> %broadcast.splatinsert100, <4 x float> poison, <4 x i32> zeroinitializer
  %broadcast.splatinsert102 = insertelement <4 x float> poison, float %81, i64 0
  %broadcast.splat103 = shufflevector <4 x float> %broadcast.splatinsert102, <4 x float> poison, <4 x i32> zeroinitializer
  %84 = add <4 x i32> %broadcast.splat, <i32 0, i32 1, i32 2, i32 3>
  %85 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %84, <4 x i32> zeroinitializer)
  %86 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %broadcast.splat78, <4 x i32> %85)
  %87 = mul <4 x i32> %broadcast.splat80, %86
  %88 = add <4 x i32> %87, %broadcast.splat82
  %89 = mul <4 x i32> %88, <i32 3, i32 3, i32 3, i32 3>
  %90 = sext <4 x i32> %89 to <4 x i64>
  %91 = getelementptr float, float* %65, <4 x i64> %90
  %wide.masked.gather = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %91, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %92 = add <4 x i32> %89, <i32 1, i32 1, i32 1, i32 1>
  %93 = sext <4 x i32> %92 to <4 x i64>
  %94 = getelementptr float, float* %65, <4 x i64> %93
  %wide.masked.gather83 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %94, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %95 = add <4 x i32> %89, <i32 2, i32 2, i32 2, i32 2>
  %96 = sext <4 x i32> %95 to <4 x i64>
  %97 = getelementptr float, float* %65, <4 x i64> %96
  %wide.masked.gather84 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %97, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %98 = add <4 x i32> %87, %broadcast.splat86
  %99 = mul <4 x i32> %98, <i32 3, i32 3, i32 3, i32 3>
  %100 = sext <4 x i32> %99 to <4 x i64>
  %101 = getelementptr float, float* %65, <4 x i64> %100
  %wide.masked.gather87 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %101, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %102 = add <4 x i32> %99, <i32 1, i32 1, i32 1, i32 1>
  %103 = sext <4 x i32> %102 to <4 x i64>
  %104 = getelementptr float, float* %65, <4 x i64> %103
  %wide.masked.gather88 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %104, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %105 = add <4 x i32> %99, <i32 2, i32 2, i32 2, i32 2>
  %106 = sext <4 x i32> %105 to <4 x i64>
  %107 = getelementptr float, float* %65, <4 x i64> %106
  %wide.masked.gather89 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %107, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %108 = add <4 x i32> %87, %broadcast.splat91
  %109 = mul <4 x i32> %108, <i32 3, i32 3, i32 3, i32 3>
  %110 = sext <4 x i32> %109 to <4 x i64>
  %111 = getelementptr float, float* %65, <4 x i64> %110
  %wide.masked.gather92 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %111, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %112 = add <4 x i32> %109, <i32 1, i32 1, i32 1, i32 1>
  %113 = sext <4 x i32> %112 to <4 x i64>
  %114 = getelementptr float, float* %65, <4 x i64> %113
  %wide.masked.gather93 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %114, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %115 = add <4 x i32> %109, <i32 2, i32 2, i32 2, i32 2>
  %116 = sext <4 x i32> %115 to <4 x i64>
  %117 = getelementptr float, float* %65, <4 x i64> %116
  %wide.masked.gather94 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %117, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %118 = add <4 x i32> %87, %broadcast.splat96
  %119 = mul <4 x i32> %118, <i32 3, i32 3, i32 3, i32 3>
  %120 = sext <4 x i32> %119 to <4 x i64>
  %121 = getelementptr float, float* %65, <4 x i64> %120
  %wide.masked.gather97 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %121, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %122 = add <4 x i32> %119, <i32 1, i32 1, i32 1, i32 1>
  %123 = sext <4 x i32> %122 to <4 x i64>
  %124 = getelementptr float, float* %65, <4 x i64> %123
  %wide.masked.gather98 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %124, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %125 = add <4 x i32> %119, <i32 2, i32 2, i32 2, i32 2>
  %126 = sext <4 x i32> %125 to <4 x i64>
  %127 = getelementptr float, float* %65, <4 x i64> %126
  %wide.masked.gather99 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %127, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %128 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather, <float -5.000000e-01, float -5.000000e-01, float -5.000000e-01, float -5.000000e-01>
  %129 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather83, <float -5.000000e-01, float -5.000000e-01, float -5.000000e-01, float -5.000000e-01>
  %130 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather84, <float -5.000000e-01, float -5.000000e-01, float -5.000000e-01, float -5.000000e-01>
  %131 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather97, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %132 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather98, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %133 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather99, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %134 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather87, %wide.masked.gather92
  %135 = fmul reassoc ninf nsz <4 x float> %134, <float 1.500000e+00, float 1.500000e+00, float 1.500000e+00, float 1.500000e+00>
  %136 = fadd reassoc ninf nsz <4 x float> %135, %128
  %137 = fadd reassoc ninf nsz <4 x float> %136, %131
  %138 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather88, %wide.masked.gather93
  %139 = fmul reassoc ninf nsz <4 x float> %138, <float 1.500000e+00, float 1.500000e+00, float 1.500000e+00, float 1.500000e+00>
  %140 = fadd reassoc ninf nsz <4 x float> %139, %129
  %141 = fadd reassoc ninf nsz <4 x float> %140, %132
  %142 = fsub reassoc ninf nsz <4 x float> %wide.masked.gather89, %wide.masked.gather94
  %143 = fmul reassoc ninf nsz <4 x float> %142, <float 1.500000e+00, float 1.500000e+00, float 1.500000e+00, float 1.500000e+00>
  %144 = fadd reassoc ninf nsz <4 x float> %143, %130
  %145 = fadd reassoc ninf nsz <4 x float> %144, %133
  %146 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather87, <float -2.500000e+00, float -2.500000e+00, float -2.500000e+00, float -2.500000e+00>
  %147 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather92, <float 2.000000e+00, float 2.000000e+00, float 2.000000e+00, float 2.000000e+00>
  %148 = fadd reassoc ninf nsz <4 x float> %146, %wide.masked.gather
  %149 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather88, <float -2.500000e+00, float -2.500000e+00, float -2.500000e+00, float -2.500000e+00>
  %150 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather93, <float 2.000000e+00, float 2.000000e+00, float 2.000000e+00, float 2.000000e+00>
  %151 = fadd reassoc ninf nsz <4 x float> %149, %wide.masked.gather83
  %152 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather89, <float -2.500000e+00, float -2.500000e+00, float -2.500000e+00, float -2.500000e+00>
  %153 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather94, <float 2.000000e+00, float 2.000000e+00, float 2.000000e+00, float 2.000000e+00>
  %154 = fadd reassoc ninf nsz <4 x float> %152, %wide.masked.gather84
  %155 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather92, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %156 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather93, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %157 = fmul reassoc ninf nsz <4 x float> %wide.masked.gather94, <float 5.000000e-01, float 5.000000e-01, float 5.000000e-01, float 5.000000e-01>
  %158 = fadd reassoc ninf nsz <4 x float> %155, %128
  %159 = fadd reassoc ninf nsz <4 x float> %156, %129
  %160 = fadd reassoc ninf nsz <4 x float> %157, %130
  %161 = fmul reassoc ninf nsz <4 x float> %137, %broadcast.splat101
  %162 = fmul reassoc ninf nsz <4 x float> %141, %broadcast.splat101
  %163 = fmul reassoc ninf nsz <4 x float> %145, %broadcast.splat101
  %164 = fmul reassoc ninf nsz <4 x float> %158, %broadcast.splat101
  %165 = fmul reassoc ninf nsz <4 x float> %159, %broadcast.splat101
  %166 = fmul reassoc ninf nsz <4 x float> %160, %broadcast.splat101
  %167 = fadd reassoc ninf nsz <4 x float> %148, %147
  %168 = fsub reassoc ninf nsz <4 x float> %167, %131
  %169 = fadd reassoc ninf nsz <4 x float> %168, %161
  %170 = fmul reassoc ninf nsz <4 x float> %169, %broadcast.splat103
  %171 = fadd reassoc ninf nsz <4 x float> %164, %wide.masked.gather87
  %172 = fadd reassoc ninf nsz <4 x float> %171, %170
  %173 = fadd reassoc ninf nsz <4 x float> %151, %150
  %174 = fsub reassoc ninf nsz <4 x float> %173, %132
  %175 = fadd reassoc ninf nsz <4 x float> %174, %162
  %176 = fmul reassoc ninf nsz <4 x float> %175, %broadcast.splat103
  %177 = fadd reassoc ninf nsz <4 x float> %165, %wide.masked.gather88
  %178 = fadd reassoc ninf nsz <4 x float> %177, %176
  %179 = fadd reassoc ninf nsz <4 x float> %154, %153
  %180 = fsub reassoc ninf nsz <4 x float> %179, %133
  %181 = fadd reassoc ninf nsz <4 x float> %180, %163
  %182 = fmul reassoc ninf nsz <4 x float> %181, %broadcast.splat103
  %183 = fadd reassoc ninf nsz <4 x float> %166, %wide.masked.gather89
  %184 = fadd reassoc ninf nsz <4 x float> %183, %182
  %185 = shufflevector <4 x float> %172, <4 x float> %178, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %186 = shufflevector <4 x float> %184, <4 x float> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 undef, i32 undef, i32 undef, i32 undef>
  %interleaved.vec = shufflevector <8 x float> %185, <8 x float> %186, <12 x i32> <i32 0, i32 4, i32 8, i32 1, i32 5, i32 9, i32 2, i32 6, i32 10, i32 3, i32 7, i32 11>
  store <12 x float> %interleaved.vec, <12 x float>* %49, align 4
  %187 = fsub reassoc ninf nsz float %61, %64
  %188 = load float, float* %43, align 4
  %189 = load float, float* %42, align 4
  %190 = load float, float* %41, align 4
  %191 = load float, float* %40, align 4
  %192 = load float, float* %39, align 4
  %193 = load float, float* %38, align 4
  %194 = load float, float* %37, align 4
  %195 = load float, float* %36, align 4
  %196 = load float, float* %35, align 4
  %197 = load float, float* %34, align 4
  %198 = load float, float* %33, align 4
  %199 = load float, float* %32, align 4
  %200 = fmul reassoc ninf nsz float %188, -5.000000e-01
  %201 = fmul reassoc ninf nsz float %189, -5.000000e-01
  %202 = fmul reassoc ninf nsz float %190, -5.000000e-01
  %203 = fmul reassoc ninf nsz float %197, 5.000000e-01
  %204 = fmul reassoc ninf nsz float %198, 5.000000e-01
  %205 = fmul reassoc ninf nsz float %199, 5.000000e-01
  %reass.add30 = fsub reassoc ninf nsz float %191, %194
  %reass.mul31 = fmul reassoc ninf nsz float %reass.add30, 1.500000e+00
  %206 = fadd reassoc ninf nsz float %reass.mul31, %200
  %207 = fadd reassoc ninf nsz float %206, %203
  %reass.add33 = fsub reassoc ninf nsz float %192, %195
  %reass.mul34 = fmul reassoc ninf nsz float %reass.add33, 1.500000e+00
  %208 = fadd reassoc ninf nsz float %reass.mul34, %201
  %209 = fadd reassoc ninf nsz float %208, %204
  %reass.add36 = fsub reassoc ninf nsz float %193, %196
  %reass.mul37 = fmul reassoc ninf nsz float %reass.add36, 1.500000e+00
  %210 = fadd reassoc ninf nsz float %reass.mul37, %202
  %211 = fadd reassoc ninf nsz float %210, %205
  %.neg15 = fmul reassoc ninf nsz float %191, -2.500000e+00
  %factor = fmul reassoc ninf nsz float %194, 2.000000e+00
  %212 = fadd reassoc ninf nsz float %.neg15, %188
  %.neg18 = fmul reassoc ninf nsz float %192, -2.500000e+00
  %factor21 = fmul reassoc ninf nsz float %195, 2.000000e+00
  %213 = fadd reassoc ninf nsz float %.neg18, %189
  %.neg22 = fmul reassoc ninf nsz float %193, -2.500000e+00
  %factor25 = fmul reassoc ninf nsz float %196, 2.000000e+00
  %214 = fadd reassoc ninf nsz float %.neg22, %190
  %215 = fmul reassoc ninf nsz float %194, 5.000000e-01
  %216 = fmul reassoc ninf nsz float %195, 5.000000e-01
  %217 = fmul reassoc ninf nsz float %196, 5.000000e-01
  %218 = fadd reassoc ninf nsz float %215, %200
  %219 = fadd reassoc ninf nsz float %216, %201
  %220 = fadd reassoc ninf nsz float %217, %202
  %221 = fmul reassoc ninf nsz float %187, %187
  %222 = fmul reassoc ninf nsz float %207, %187
  %223 = fmul reassoc ninf nsz float %209, %187
  %224 = fmul reassoc ninf nsz float %211, %187
  %225 = fmul reassoc ninf nsz float %218, %187
  %226 = fmul reassoc ninf nsz float %219, %187
  %227 = fmul reassoc ninf nsz float %220, %187
  %228 = fadd reassoc ninf nsz float %212, %factor
  %229 = fsub reassoc ninf nsz float %228, %203
  %reass.add = fadd reassoc ninf nsz float %229, %222
  %reass.mul = fmul reassoc ninf nsz float %reass.add, %221
  %230 = fadd reassoc ninf nsz float %225, %191
  %231 = fadd reassoc ninf nsz float %230, %reass.mul
  %232 = fadd reassoc ninf nsz float %213, %factor21
  %233 = fsub reassoc ninf nsz float %232, %204
  %reass.add26 = fadd reassoc ninf nsz float %233, %223
  %reass.mul27 = fmul reassoc ninf nsz float %reass.add26, %221
  %234 = fadd reassoc ninf nsz float %226, %192
  %235 = fadd reassoc ninf nsz float %234, %reass.mul27
  %236 = fadd reassoc ninf nsz float %214, %factor25
  %237 = fsub reassoc ninf nsz float %236, %205
  %reass.add28 = fadd reassoc ninf nsz float %237, %224
  %reass.mul29 = fmul reassoc ninf nsz float %reass.add28, %221
  %238 = fadd reassoc ninf nsz float %227, %193
  %239 = fadd reassoc ninf nsz float %238, %reass.mul29
  %240 = load float*, float** %46, align 8
  %241 = sext i32 %lsr.iv to i64
  %242 = getelementptr float, float* %240, i64 %241
  store float %231, float* %242, align 4
  %243 = load float*, float** %46, align 8
  %244 = add i32 %lsr.iv, 1
  %245 = sext i32 %244 to i64
  %246 = getelementptr float, float* %243, i64 %245
  store float %235, float* %246, align 4
  %247 = load float*, float** %46, align 8
  %248 = add i32 %lsr.iv, 2
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, float* %247, i64 %249
  store float %239, float* %250, align 4
  %lsr.iv.next = add i32 %lsr.iv, 3
  %lsr.iv.next105 = add i32 %lsr.iv104, 1
  %lsr.iv.next107 = add i64 %lsr.iv106, 1
  %exitcond76.not = icmp eq i64 %lsr.iv.next107, 0
  br i1 %exitcond76.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nounwind willreturn writeonly
declare void @llvm.memset.p0i8.i64(i8* nocapture writeonly, i8, i64, i1 immarg) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #8

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #9

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nounwind willreturn writeonly }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #9 = { nocallback nofree nosync nounwind readonly willreturn }

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
