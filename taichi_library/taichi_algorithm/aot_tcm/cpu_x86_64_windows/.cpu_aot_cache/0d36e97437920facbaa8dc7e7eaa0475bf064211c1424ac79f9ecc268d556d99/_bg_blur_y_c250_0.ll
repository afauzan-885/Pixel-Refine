; ModuleID = '<string>'
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
define void @_bg_blur_y_c248_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fmul reassoc ninf nsz float %4, 2.000000e+00
  %6 = fdiv reassoc ninf nsz float 1.000000e+00, %5
  %7 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 16
  %12 = bitcast i8* %11 to float*
  store float %6, float* %12, align 4
  %13 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }** %0, align 8
  %14 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %13, i64 0, i32 4
  %15 = load i32, i32* %14, align 4
  %16 = tail call i32 @llvm.smax.i32(i32 %15, i32 0)
  %17 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %13, i64 0, i32 5
  %18 = load i32, i32* %17, align 4
  %19 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %20 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %19, i64 0, i32 14
  %21 = load i8*, i8** %20, align 8
  %22 = getelementptr inbounds i8, i8* %21, i64 12
  %23 = bitcast i8* %22 to i32*
  store i32 %18, i32* %23, align 4
  %24 = tail call i32 @llvm.smax.i32(i32 %18, i32 0)
  %25 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }** %0, align 8
  %26 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %25, i64 0, i32 6
  %27 = load i32, i32* %26, align 4
  %28 = tail call i32 @llvm.smax.i32(i32 %27, i32 0)
  %29 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 8
  %33 = bitcast i8* %32 to i32*
  store i32 %28, i32* %33, align 4
  %34 = mul i32 %28, %24
  %35 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %35, i64 0, i32 14
  %37 = load i8*, i8** %36, align 8
  %38 = getelementptr inbounds i8, i8* %37, i64 4
  %39 = bitcast i8* %38 to i32*
  store i32 %34, i32* %39, align 4
  %40 = mul i32 %34, %16
  %41 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %7, align 8
  %42 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %41, i64 0, i32 14
  %43 = bitcast i8** %42 to i32**
  %44 = load i32*, i32** %43, align 8
  store i32 %40, i32* %44, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bg_blur_y_c248_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }**
  %21 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 2
  %23 = load i32, i32* %22, align 4
  %neg = sub i32 0, %23
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = add i32 %23, 1
  %26 = icmp sgt i32 %25, %neg
  %27 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %30 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 3
  %31 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %32 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %33 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %34 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 3
  %35 = shl i32 %23, 1
  %36 = add nuw nsw i32 %35, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01524 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %132, %after_for3 ]
  %37 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.01524, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.01524
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.01524, 0
  %48 = icmp ne i32 %44, %.01524
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg16 = sext i1 %50 to i32
  %51 = add i32 %43, %.neg16
  %52 = mul i32 %51, %42
  %53 = sub i32 %.01524, %52
  %54 = getelementptr inbounds i8, i8* %39, i64 8
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = sdiv i32 %53, %56
  %58 = mul i32 %57, %56
  %59 = xor i32 %53, %56
  %60 = icmp slt i32 %59, 0
  %61 = icmp ne i32 %.01524, %52
  %62 = icmp ne i32 %58, %53
  %63 = and i1 %61, %60
  %64 = and i1 %62, %63
  %.neg17 = sext i1 %64 to i32
  %65 = add i32 %57, %.neg17
  %66 = mul i32 %65, %56
  %67 = sub i32 %53, %66
  %68 = getelementptr inbounds i8, i8* %39, i64 12
  %69 = bitcast i8* %68 to i32*
  %70 = load i32, i32* %69, align 4
  %71 = add i32 %70, -1
  br i1 %26, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader
  %lsr.iv = phi i32 [ %36, %for_loop_body1.preheader ], [ %lsr.iv.next, %for_loop_body1 ]
  %.021 = phi i32 [ %106, %for_loop_body1 ], [ %neg, %for_loop_body1.preheader ]
  %.01220 = phi float [ %105, %for_loop_body1 ], [ 0.000000e+00, %for_loop_body1.preheader ]
  %.01319 = phi float [ %104, %for_loop_body1 ], [ 0.000000e+00, %for_loop_body1.preheader ]
  %.01418 = phi float [ %103, %for_loop_body1 ], [ 0.000000e+00, %for_loop_body1.preheader ]
  %72 = add i32 %65, %.021
  %73 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %74 = tail call i32 @llvm.smin.i32(i32 %71, i32 %73)
  %75 = mul i32 %.021, %.021
  %76 = sitofp i32 %75 to float
  %neg5 = fneg reassoc ninf nsz float %76
  %77 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %78 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %77, i64 0, i32 14
  %79 = load i8*, i8** %78, align 8
  %80 = getelementptr inbounds i8, i8* %79, i64 16
  %81 = bitcast i8* %80 to float*
  %82 = load float, float* %81, align 4
  %83 = fmul reassoc ninf nsz float %82, %neg5
  %84 = tail call float @expf(float noundef %83) #1
  %85 = load float*, float** %27, align 8
  %86 = load i32, i32* %28, align 4
  %87 = load i32, i32* %29, align 4
  %88 = load i32, i32* %30, align 4
  %89 = mul i32 %86, %51
  %90 = add i32 %89, %74
  %91 = mul i32 %90, %87
  %92 = add i32 %91, %67
  %93 = mul i32 %92, %88
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, float* %85, i64 %94
  %96 = load float, float* %95, align 4
  %97 = add i32 %93, 1
  %98 = sext i32 %97 to i64
  %99 = getelementptr float, float* %85, i64 %98
  %100 = load float, float* %99, align 4
  %101 = fmul reassoc ninf nsz float %96, %84
  %102 = fmul reassoc ninf nsz float %100, %84
  %103 = fadd reassoc ninf nsz float %101, %.01418
  %104 = fadd reassoc ninf nsz float %102, %.01319
  %105 = fadd reassoc ninf nsz float %84, %.01220
  %106 = add nsw i32 %.021, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 0
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1

after_for3.loopexit:                              ; preds = %for_loop_body1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.014.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %103, %after_for3.loopexit ]
  %.013.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %104, %after_for3.loopexit ]
  %.012.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %105, %after_for3.loopexit ]
  %107 = fdiv reassoc ninf nsz float %.014.lcssa, %.012.lcssa
  %108 = load float*, float** %31, align 8
  %109 = load i32, i32* %32, align 4
  %110 = load i32, i32* %33, align 4
  %111 = load i32, i32* %34, align 4
  %112 = mul i32 %109, %51
  %113 = add i32 %112, %65
  %114 = mul i32 %113, %110
  %115 = add i32 %114, %67
  %116 = mul i32 %115, %111
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, float* %108, i64 %117
  store float %107, float* %118, align 4
  %119 = fdiv reassoc ninf nsz float %.013.lcssa, %.012.lcssa
  %120 = load float*, float** %31, align 8
  %121 = load i32, i32* %32, align 4
  %122 = load i32, i32* %33, align 4
  %123 = load i32, i32* %34, align 4
  %124 = mul i32 %121, %51
  %125 = add i32 %124, %65
  %126 = mul i32 %125, %122
  %127 = add i32 %126, %67
  %128 = mul i32 %127, %123
  %129 = add i32 %128, 1
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, float* %120, i64 %130
  store float %119, float* %131, align 4
  %132 = add nsw i32 %.01524, 1
  %exitcond27.not = icmp eq i32 %132, %19
  br i1 %exitcond27.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @expf(float noundef) local_unnamed_addr #3

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

; Function Attrs: argmemonly nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly nocallback nofree nounwind willreturn }
attributes #6 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
