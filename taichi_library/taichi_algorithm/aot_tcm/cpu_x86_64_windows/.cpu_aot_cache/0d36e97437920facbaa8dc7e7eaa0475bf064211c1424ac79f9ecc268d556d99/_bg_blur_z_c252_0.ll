; ModuleID = '<string>'
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
define void @_bg_blur_z_c250_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load float, float* %2, align 4
  %4 = fmul reassoc ninf nsz float %3, %3
  %5 = fmul reassoc ninf nsz float %4, 2.000000e+00
  %6 = fdiv reassoc ninf nsz float 1.000000e+00, %5
  %7 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %8, i64 0, i32 14
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
  %19 = tail call i32 @llvm.smax.i32(i32 %18, i32 0)
  %20 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }* %13, i64 0, i32 6
  %21 = load i32, i32* %20, align 4
  %22 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %7, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 12
  %26 = bitcast i8* %25 to i32*
  store i32 %21, i32* %26, align 4
  %27 = tail call i32 @llvm.smax.i32(i32 %21, i32 0)
  %28 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %7, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %28, i64 0, i32 14
  %30 = load i8*, i8** %29, align 8
  %31 = getelementptr inbounds i8, i8* %30, i64 8
  %32 = bitcast i8* %31 to i32*
  store i32 %27, i32* %32, align 4
  %33 = mul i32 %27, %19
  %34 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %7, align 8
  %35 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %34, i64 0, i32 14
  %36 = load i8*, i8** %35, align 8
  %37 = getelementptr inbounds i8, i8* %36, i64 4
  %38 = bitcast i8* %37 to i32*
  store i32 %33, i32* %38, align 4
  %39 = mul i32 %33, %16
  %40 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %7, align 8
  %41 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %40, i64 0, i32 14
  %42 = bitcast i8** %41 to i32**
  %43 = load i32*, i32** %42, align 8
  store i32 %39, i32* %43, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bg_blur_z_c250_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, float, i32, i32, i32 }**
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
  %37 = sub i32 %17, %23
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %lsr.iv36 = phi i32 [ %37, %for_loop_body.lr.ph ], [ %lsr.iv.next37, %after_for3 ]
  %.01524 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %134, %after_for3 ]
  %38 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  %43 = load i32, i32* %42, align 4
  %44 = sdiv i32 %.01524, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.01524
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %.01524, 0
  %49 = icmp ne i32 %45, %.01524
  %50 = and i1 %48, %47
  %51 = and i1 %50, %49
  %.neg16 = sext i1 %51 to i32
  %52 = add i32 %44, %.neg16
  %53 = mul i32 %52, %43
  %54 = sub i32 %.01524, %53
  %55 = getelementptr inbounds i8, i8* %40, i64 8
  %56 = bitcast i8* %55 to i32*
  %57 = load i32, i32* %56, align 4
  %58 = sdiv i32 %54, %57
  %59 = mul i32 %58, %57
  %60 = xor i32 %54, %57
  %61 = icmp slt i32 %60, 0
  %62 = icmp ne i32 %.01524, %53
  %63 = icmp ne i32 %59, %54
  %64 = and i1 %62, %61
  %65 = and i1 %63, %64
  %.neg17 = sext i1 %65 to i32
  %66 = add i32 %58, %.neg17
  %67 = mul i32 %66, %57
  %68 = sub i32 %54, %67
  %69 = getelementptr inbounds i8, i8* %40, i64 12
  %70 = bitcast i8* %69 to i32*
  %71 = load i32, i32* %70, align 4
  %72 = add i32 %71, -1
  br i1 %26, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_body
  %73 = sub i32 %lsr.iv36, %53
  %74 = sub i32 %73, %67
  br label %for_loop_body1

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_body1:                                   ; preds = %for_loop_body1, %for_loop_body1.preheader
  %lsr.iv38 = phi i32 [ %74, %for_loop_body1.preheader ], [ %lsr.iv.next39, %for_loop_body1 ]
  %lsr.iv = phi i32 [ %36, %for_loop_body1.preheader ], [ %lsr.iv.next, %for_loop_body1 ]
  %.021 = phi i32 [ %108, %for_loop_body1 ], [ %neg, %for_loop_body1.preheader ]
  %.01220 = phi float [ %107, %for_loop_body1 ], [ 0.000000e+00, %for_loop_body1.preheader ]
  %.01319 = phi float [ %106, %for_loop_body1 ], [ 0.000000e+00, %for_loop_body1.preheader ]
  %.01418 = phi float [ %105, %for_loop_body1 ], [ 0.000000e+00, %for_loop_body1.preheader ]
  %75 = tail call i32 @llvm.smax.i32(i32 %lsr.iv38, i32 0)
  %76 = tail call i32 @llvm.smin.i32(i32 %72, i32 %75)
  %77 = mul i32 %.021, %.021
  %78 = sitofp i32 %77 to float
  %neg5 = fneg reassoc ninf nsz float %78
  %79 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %80 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %79, i64 0, i32 14
  %81 = load i8*, i8** %80, align 8
  %82 = getelementptr inbounds i8, i8* %81, i64 16
  %83 = bitcast i8* %82 to float*
  %84 = load float, float* %83, align 4
  %85 = fmul reassoc ninf nsz float %84, %neg5
  %86 = tail call float @expf(float noundef %85) #1
  %87 = load float*, float** %27, align 8
  %88 = load i32, i32* %28, align 4
  %89 = load i32, i32* %29, align 4
  %90 = load i32, i32* %30, align 4
  %91 = mul i32 %88, %52
  %92 = add i32 %91, %66
  %93 = mul i32 %92, %89
  %94 = add i32 %93, %76
  %95 = mul i32 %94, %90
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, float* %87, i64 %96
  %98 = load float, float* %97, align 4
  %99 = add i32 %95, 1
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %87, i64 %100
  %102 = load float, float* %101, align 4
  %103 = fmul reassoc ninf nsz float %98, %86
  %104 = fmul reassoc ninf nsz float %102, %86
  %105 = fadd reassoc ninf nsz float %103, %.01418
  %106 = fadd reassoc ninf nsz float %104, %.01319
  %107 = fadd reassoc ninf nsz float %86, %.01220
  %108 = add nsw i32 %.021, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %lsr.iv.next39 = add i32 %lsr.iv38, 1
  %exitcond.not = icmp eq i32 %lsr.iv.next, 0
  br i1 %exitcond.not, label %after_for3.loopexit, label %for_loop_body1

after_for3.loopexit:                              ; preds = %for_loop_body1
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.014.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %105, %after_for3.loopexit ]
  %.013.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %106, %after_for3.loopexit ]
  %.012.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %107, %after_for3.loopexit ]
  %109 = fdiv reassoc ninf nsz float %.014.lcssa, %.012.lcssa
  %110 = load float*, float** %31, align 8
  %111 = load i32, i32* %32, align 4
  %112 = load i32, i32* %33, align 4
  %113 = load i32, i32* %34, align 4
  %114 = mul i32 %111, %52
  %115 = add i32 %114, %66
  %116 = mul i32 %115, %112
  %117 = add i32 %116, %68
  %118 = mul i32 %117, %113
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, float* %110, i64 %119
  store float %109, float* %120, align 4
  %121 = fdiv reassoc ninf nsz float %.013.lcssa, %.012.lcssa
  %122 = load float*, float** %31, align 8
  %123 = load i32, i32* %32, align 4
  %124 = load i32, i32* %33, align 4
  %125 = load i32, i32* %34, align 4
  %126 = mul i32 %123, %52
  %127 = add i32 %126, %66
  %128 = mul i32 %127, %124
  %129 = add i32 %128, %68
  %130 = mul i32 %129, %125
  %131 = add i32 %130, 1
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %122, i64 %132
  store float %121, float* %133, align 4
  %134 = add nsw i32 %.01524, 1
  %lsr.iv.next37 = add i32 %lsr.iv36, 1
  %exitcond27.not = icmp eq i32 %134, %19
  br i1 %exitcond27.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @expf(float noundef) local_unnamed_addr #3

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
