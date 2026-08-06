; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.84*, void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.84 = type { i8*, %struct.LLVMRuntime.83*, i32, i64* }
%struct.LLVMRuntime.83 = type { %struct.PreallocatedMemoryChunk.79, %struct.PreallocatedMemoryChunk.79, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.80*], [1024 x %struct.NodeManager.81*], [1024 x i8*], i8*, %struct.RandState.82*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.79 = type { i8*, i8*, i64 }
%struct.ListManager.80 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.83* }
%struct.NodeManager.81 = type { %struct.LLVMRuntime.83*, i32, i32, i32, i32, %struct.ListManager.80*, %struct.ListManager.80*, %struct.ListManager.80*, i32 }
%struct.RandState.82 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_dcb_highlight_ratio_seed_c720_0_kernel_0_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1, i64 0, i32 8
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_highlight_ratio_seed_c720_0_kernel_1_range_for(%struct.RuntimeContext.84* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.84* %context, %struct.RuntimeContext.84** %4, align 8
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.84*, i8*, i32)* @function_body, void (%struct.RuntimeContext.84*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.84* readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.84* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %28 = shl i32 %17, 3
  %29 = add nuw nsw i32 %28, 7
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if759, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next, %after_if759 ]
  %.05791045 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %3265, %after_if759 ]
  %30 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %.05791045, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.05791045
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.05791045, 0
  %41 = icmp ne i32 %.05791045, %37
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg708 = sext i1 %43 to i32
  %44 = add i32 %36, %.neg708
  %45 = mul i32 %44, %35
  %46 = sub i32 %.05791045, %45
  %47 = shl i32 %44, 3
  %48 = shl i32 %46, 3
  %49 = mul i32 %35, -8
  %50 = mul i32 %49, %44
  %51 = add i32 %lsr.iv, %50
  %52 = add i32 %51, -7
  %53 = icmp slt i32 %47, %23
  br i1 %53, label %true_block, label %after_if75

after_for.loopexit:                               ; preds = %after_if759
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %54 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %55 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 6
  %56 = load i32, i32* %55, align 4
  %57 = icmp slt i32 %52, %56
  br i1 %57, label %true_block1, label %true_block10

true_block1:                                      ; preds = %true_block
  %58 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %59 = load float*, float** %58, align 8
  %60 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %61 = load i32, i32* %60, align 4
  %62 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %63 = load i32, i32* %62, align 4
  %64 = shl i32 %61, 3
  %65 = shl i32 %35, 3
  %66 = sub i32 %64, %65
  %67 = mul i32 %66, %44
  %68 = add i32 %lsr.iv, %67
  %69 = add i32 %68, -7
  %70 = mul i32 %69, %63
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, float* %59, i64 %71
  %73 = or i32 %70, 1
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, float* %59, i64 %74
  %76 = load float, float* %75, align 4
  %77 = or i32 %70, 2
  %78 = sext i32 %77 to i64
  %79 = getelementptr float, float* %59, i64 %78
  %80 = insertelement <2 x float*> poison, float* %72, i64 0
  %81 = insertelement <2 x float*> %80, float* %79, i64 1
  %82 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %81, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %83 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %84 = load float, float* %83, align 4
  %85 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %84, float 0x3F1A36E2E0000000)
  %86 = extractelement <2 x float> %82, i64 0
  %87 = fdiv reassoc ninf nsz float %86, %85
  %88 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %89 = load float, float* %88, align 4
  %90 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %89, float 0x3F1A36E2E0000000)
  %91 = fdiv reassoc ninf nsz float %76, %90
  %92 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %93 = load float, float* %92, align 4
  %94 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %93, float 0x3F1A36E2E0000000)
  %95 = extractelement <2 x float> %82, i64 1
  %96 = fdiv reassoc ninf nsz float %95, %94
  %97 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %91, float %96)
  %98 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %87, float %97)
  %99 = fcmp reassoc ninf nsz olt float %98, 0x3FED70A3E0000000
  %100 = fcmp reassoc ninf nsz ogt float %76, 0x3EE4F8B580000000
  %.0448 = select i1 %99, i1 %100, i1 false
  br i1 %.0448, label %true_block7, label %true_block10

true_block7:                                      ; preds = %true_block1
  %101 = insertelement <2 x float> poison, float %76, i64 0
  %102 = shufflevector <2 x float> %101, <2 x float> poison, <2 x i32> zeroinitializer
  %103 = fdiv reassoc ninf nsz <2 x float> %82, %102
  %104 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %103, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %105 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %104, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  br label %true_block10

true_block10:                                     ; preds = %true_block7, %true_block1, %true_block
  %.0450.ph = phi float [ 0.000000e+00, %true_block ], [ 0.000000e+00, %true_block1 ], [ 1.000000e+00, %true_block7 ]
  %106 = phi <2 x float> [ zeroinitializer, %true_block ], [ zeroinitializer, %true_block1 ], [ %105, %true_block7 ]
  %107 = add i32 %51, -6
  %108 = icmp slt i32 %107, %56
  br i1 %108, label %true_block13, label %true_block22

true_block13:                                     ; preds = %true_block10
  %109 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %110 = load float*, float** %109, align 8
  %111 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %112 = load i32, i32* %111, align 4
  %113 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %114 = load i32, i32* %113, align 4
  %115 = shl i32 %112, 3
  %116 = shl i32 %35, 3
  %117 = sub i32 %115, %116
  %118 = mul i32 %117, %44
  %119 = add i32 %lsr.iv, %118
  %120 = add i32 %119, -6
  %121 = mul i32 %120, %114
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, float* %110, i64 %122
  %124 = add i32 %121, 1
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %110, i64 %125
  %127 = load float, float* %126, align 4
  %128 = add i32 %121, 2
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %110, i64 %129
  %131 = insertelement <2 x float*> poison, float* %123, i64 0
  %132 = insertelement <2 x float*> %131, float* %130, i64 1
  %133 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %132, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %134 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %135 = load float, float* %134, align 4
  %136 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %135, float 0x3F1A36E2E0000000)
  %137 = extractelement <2 x float> %133, i64 0
  %138 = fdiv reassoc ninf nsz float %137, %136
  %139 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %140 = load float, float* %139, align 4
  %141 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %140, float 0x3F1A36E2E0000000)
  %142 = fdiv reassoc ninf nsz float %127, %141
  %143 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %144 = load float, float* %143, align 4
  %145 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %144, float 0x3F1A36E2E0000000)
  %146 = extractelement <2 x float> %133, i64 1
  %147 = fdiv reassoc ninf nsz float %146, %145
  %148 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %142, float %147)
  %149 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %138, float %148)
  %150 = fcmp reassoc ninf nsz olt float %149, 0x3FED70A3E0000000
  %151 = fcmp reassoc ninf nsz ogt float %127, 0x3EE4F8B580000000
  %.0446 = select i1 %150, i1 %151, i1 false
  br i1 %.0446, label %true_block19, label %true_block22

true_block19:                                     ; preds = %true_block13
  %152 = insertelement <2 x float> poison, float %127, i64 0
  %153 = shufflevector <2 x float> %152, <2 x float> poison, <2 x i32> zeroinitializer
  %154 = fdiv reassoc ninf nsz <2 x float> %133, %153
  %155 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %154, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %156 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %155, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %157 = fadd reassoc ninf nsz <2 x float> %156, %106
  %158 = fadd reassoc ninf nsz float %.0450.ph, 1.000000e+00
  br label %true_block22

true_block22:                                     ; preds = %true_block19, %true_block13, %true_block10
  %.1.ph = phi float [ %.0450.ph, %true_block10 ], [ %.0450.ph, %true_block13 ], [ %158, %true_block19 ]
  %159 = phi <2 x float> [ %106, %true_block10 ], [ %106, %true_block13 ], [ %157, %true_block19 ]
  %160 = add i32 %51, -5
  %161 = icmp slt i32 %160, %56
  br i1 %161, label %true_block25, label %true_block34

true_block25:                                     ; preds = %true_block22
  %162 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %163 = load float*, float** %162, align 8
  %164 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %165 = load i32, i32* %164, align 4
  %166 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %167 = load i32, i32* %166, align 4
  %168 = shl i32 %165, 3
  %169 = shl i32 %35, 3
  %170 = sub i32 %168, %169
  %171 = mul i32 %170, %44
  %172 = add i32 %lsr.iv, %171
  %173 = add i32 %172, -5
  %174 = mul i32 %173, %167
  %175 = or i32 %174, 1
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, float* %163, i64 %176
  %178 = load float, float* %177, align 4
  %179 = add i32 %174, 2
  %180 = insertelement <2 x i32> poison, i32 %174, i64 0
  %181 = insertelement <2 x i32> %180, i32 %179, i64 1
  %182 = sext <2 x i32> %181 to <2 x i64>
  %183 = insertelement <2 x float*> poison, float* %163, i64 0
  %184 = shufflevector <2 x float*> %183, <2 x float*> poison, <2 x i32> zeroinitializer
  %185 = getelementptr float, <2 x float*> %184, <2 x i64> %182
  %186 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %185, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %187 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %188 = load float, float* %187, align 4
  %189 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %188, float 0x3F1A36E2E0000000)
  %190 = extractelement <2 x float> %186, i64 0
  %191 = fdiv reassoc ninf nsz float %190, %189
  %192 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %193 = load float, float* %192, align 4
  %194 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %193, float 0x3F1A36E2E0000000)
  %195 = fdiv reassoc ninf nsz float %178, %194
  %196 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %197 = load float, float* %196, align 4
  %198 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %197, float 0x3F1A36E2E0000000)
  %199 = extractelement <2 x float> %186, i64 1
  %200 = fdiv reassoc ninf nsz float %199, %198
  %201 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %195, float %200)
  %202 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %191, float %201)
  %203 = fcmp reassoc ninf nsz olt float %202, 0x3FED70A3E0000000
  %204 = fcmp reassoc ninf nsz ogt float %178, 0x3EE4F8B580000000
  %.0444 = select i1 %203, i1 %204, i1 false
  br i1 %.0444, label %true_block31, label %true_block34

true_block31:                                     ; preds = %true_block25
  %205 = insertelement <2 x float> poison, float %178, i64 0
  %206 = shufflevector <2 x float> %205, <2 x float> poison, <2 x i32> zeroinitializer
  %207 = fdiv reassoc ninf nsz <2 x float> %186, %206
  %208 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %207, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %209 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %208, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %210 = fadd reassoc ninf nsz <2 x float> %209, %159
  %211 = fadd reassoc ninf nsz float %.1.ph, 1.000000e+00
  br label %true_block34

true_block34:                                     ; preds = %true_block31, %true_block25, %true_block22
  %.2.ph = phi float [ %.1.ph, %true_block22 ], [ %.1.ph, %true_block25 ], [ %211, %true_block31 ]
  %212 = phi <2 x float> [ %159, %true_block22 ], [ %159, %true_block25 ], [ %210, %true_block31 ]
  %213 = add i32 %51, -4
  %214 = icmp slt i32 %213, %56
  br i1 %214, label %true_block37, label %true_block46

true_block37:                                     ; preds = %true_block34
  %215 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %216 = load float*, float** %215, align 8
  %217 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %218 = load i32, i32* %217, align 4
  %219 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %220 = load i32, i32* %219, align 4
  %221 = shl i32 %218, 3
  %222 = shl i32 %35, 3
  %223 = sub i32 %221, %222
  %224 = mul i32 %223, %44
  %225 = add i32 %lsr.iv, %224
  %226 = add i32 %225, -4
  %227 = mul i32 %226, %220
  %228 = add i32 %227, 1
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %216, i64 %229
  %231 = load float, float* %230, align 4
  %232 = add i32 %227, 2
  %233 = insertelement <2 x i32> poison, i32 %227, i64 0
  %234 = insertelement <2 x i32> %233, i32 %232, i64 1
  %235 = sext <2 x i32> %234 to <2 x i64>
  %236 = insertelement <2 x float*> poison, float* %216, i64 0
  %237 = shufflevector <2 x float*> %236, <2 x float*> poison, <2 x i32> zeroinitializer
  %238 = getelementptr float, <2 x float*> %237, <2 x i64> %235
  %239 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %238, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %240 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %241 = load float, float* %240, align 4
  %242 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %241, float 0x3F1A36E2E0000000)
  %243 = extractelement <2 x float> %239, i64 0
  %244 = fdiv reassoc ninf nsz float %243, %242
  %245 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %246 = load float, float* %245, align 4
  %247 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %246, float 0x3F1A36E2E0000000)
  %248 = fdiv reassoc ninf nsz float %231, %247
  %249 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %250 = load float, float* %249, align 4
  %251 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %250, float 0x3F1A36E2E0000000)
  %252 = extractelement <2 x float> %239, i64 1
  %253 = fdiv reassoc ninf nsz float %252, %251
  %254 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %248, float %253)
  %255 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %244, float %254)
  %256 = fcmp reassoc ninf nsz olt float %255, 0x3FED70A3E0000000
  %257 = fcmp reassoc ninf nsz ogt float %231, 0x3EE4F8B580000000
  %.0442 = select i1 %256, i1 %257, i1 false
  br i1 %.0442, label %true_block43, label %true_block46

true_block43:                                     ; preds = %true_block37
  %258 = insertelement <2 x float> poison, float %231, i64 0
  %259 = shufflevector <2 x float> %258, <2 x float> poison, <2 x i32> zeroinitializer
  %260 = fdiv reassoc ninf nsz <2 x float> %239, %259
  %261 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %260, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %262 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %261, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %263 = fadd reassoc ninf nsz <2 x float> %262, %212
  %264 = fadd reassoc ninf nsz float %.2.ph, 1.000000e+00
  br label %true_block46

true_block46:                                     ; preds = %true_block43, %true_block37, %true_block34
  %.3.ph = phi float [ %.2.ph, %true_block34 ], [ %.2.ph, %true_block37 ], [ %264, %true_block43 ]
  %265 = phi <2 x float> [ %212, %true_block34 ], [ %212, %true_block37 ], [ %263, %true_block43 ]
  %266 = add i32 %51, -3
  %267 = icmp slt i32 %266, %56
  br i1 %267, label %true_block49, label %true_block58

true_block49:                                     ; preds = %true_block46
  %268 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %269 = load float*, float** %268, align 8
  %270 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %271 = load i32, i32* %270, align 4
  %272 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %273 = load i32, i32* %272, align 4
  %274 = shl i32 %271, 3
  %275 = shl i32 %35, 3
  %276 = sub i32 %274, %275
  %277 = mul i32 %276, %44
  %278 = add i32 %lsr.iv, %277
  %279 = add i32 %278, -3
  %280 = mul i32 %279, %273
  %281 = or i32 %280, 1
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, float* %269, i64 %282
  %284 = load float, float* %283, align 4
  %285 = or i32 %280, 2
  %286 = insertelement <2 x i32> poison, i32 %280, i64 0
  %287 = insertelement <2 x i32> %286, i32 %285, i64 1
  %288 = sext <2 x i32> %287 to <2 x i64>
  %289 = insertelement <2 x float*> poison, float* %269, i64 0
  %290 = shufflevector <2 x float*> %289, <2 x float*> poison, <2 x i32> zeroinitializer
  %291 = getelementptr float, <2 x float*> %290, <2 x i64> %288
  %292 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %291, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %293 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %294 = load float, float* %293, align 4
  %295 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %294, float 0x3F1A36E2E0000000)
  %296 = extractelement <2 x float> %292, i64 0
  %297 = fdiv reassoc ninf nsz float %296, %295
  %298 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %299 = load float, float* %298, align 4
  %300 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %299, float 0x3F1A36E2E0000000)
  %301 = fdiv reassoc ninf nsz float %284, %300
  %302 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %303 = load float, float* %302, align 4
  %304 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %303, float 0x3F1A36E2E0000000)
  %305 = extractelement <2 x float> %292, i64 1
  %306 = fdiv reassoc ninf nsz float %305, %304
  %307 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %301, float %306)
  %308 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %297, float %307)
  %309 = fcmp reassoc ninf nsz olt float %308, 0x3FED70A3E0000000
  %310 = fcmp reassoc ninf nsz ogt float %284, 0x3EE4F8B580000000
  %.0440 = select i1 %309, i1 %310, i1 false
  br i1 %.0440, label %true_block55, label %true_block58

true_block55:                                     ; preds = %true_block49
  %311 = insertelement <2 x float> poison, float %284, i64 0
  %312 = shufflevector <2 x float> %311, <2 x float> poison, <2 x i32> zeroinitializer
  %313 = fdiv reassoc ninf nsz <2 x float> %292, %312
  %314 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %313, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %315 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %314, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %316 = fadd reassoc ninf nsz <2 x float> %315, %265
  %317 = fadd reassoc ninf nsz float %.3.ph, 1.000000e+00
  br label %true_block58

true_block58:                                     ; preds = %true_block55, %true_block49, %true_block46
  %.4.ph = phi float [ %.3.ph, %true_block46 ], [ %.3.ph, %true_block49 ], [ %317, %true_block55 ]
  %318 = phi <2 x float> [ %265, %true_block46 ], [ %265, %true_block49 ], [ %316, %true_block55 ]
  %319 = add i32 %51, -2
  %320 = icmp slt i32 %319, %56
  br i1 %320, label %true_block61, label %true_block70

true_block61:                                     ; preds = %true_block58
  %321 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %322 = load float*, float** %321, align 8
  %323 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %324 = load i32, i32* %323, align 4
  %325 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %326 = load i32, i32* %325, align 4
  %327 = shl i32 %324, 3
  %328 = shl i32 %35, 3
  %329 = sub i32 %327, %328
  %330 = mul i32 %329, %44
  %331 = add i32 %lsr.iv, %330
  %332 = add i32 %331, -2
  %333 = mul i32 %332, %326
  %334 = add i32 %333, 1
  %335 = sext i32 %334 to i64
  %336 = getelementptr float, float* %322, i64 %335
  %337 = load float, float* %336, align 4
  %338 = add i32 %333, 2
  %339 = insertelement <2 x i32> poison, i32 %333, i64 0
  %340 = insertelement <2 x i32> %339, i32 %338, i64 1
  %341 = sext <2 x i32> %340 to <2 x i64>
  %342 = insertelement <2 x float*> poison, float* %322, i64 0
  %343 = shufflevector <2 x float*> %342, <2 x float*> poison, <2 x i32> zeroinitializer
  %344 = getelementptr float, <2 x float*> %343, <2 x i64> %341
  %345 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %344, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %346 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %347 = load float, float* %346, align 4
  %348 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %347, float 0x3F1A36E2E0000000)
  %349 = extractelement <2 x float> %345, i64 0
  %350 = fdiv reassoc ninf nsz float %349, %348
  %351 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %352 = load float, float* %351, align 4
  %353 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %352, float 0x3F1A36E2E0000000)
  %354 = fdiv reassoc ninf nsz float %337, %353
  %355 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %356 = load float, float* %355, align 4
  %357 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %356, float 0x3F1A36E2E0000000)
  %358 = extractelement <2 x float> %345, i64 1
  %359 = fdiv reassoc ninf nsz float %358, %357
  %360 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %354, float %359)
  %361 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %350, float %360)
  %362 = fcmp reassoc ninf nsz olt float %361, 0x3FED70A3E0000000
  %363 = fcmp reassoc ninf nsz ogt float %337, 0x3EE4F8B580000000
  %.0438 = select i1 %362, i1 %363, i1 false
  br i1 %.0438, label %true_block67, label %true_block70

true_block67:                                     ; preds = %true_block61
  %364 = insertelement <2 x float> poison, float %337, i64 0
  %365 = shufflevector <2 x float> %364, <2 x float> poison, <2 x i32> zeroinitializer
  %366 = fdiv reassoc ninf nsz <2 x float> %345, %365
  %367 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %366, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %368 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %367, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %369 = fadd reassoc ninf nsz <2 x float> %368, %318
  %370 = fadd reassoc ninf nsz float %.4.ph, 1.000000e+00
  br label %true_block70

true_block70:                                     ; preds = %true_block67, %true_block61, %true_block58
  %.5.ph = phi float [ %.4.ph, %true_block58 ], [ %.4.ph, %true_block61 ], [ %370, %true_block67 ]
  %371 = phi <2 x float> [ %318, %true_block58 ], [ %318, %true_block61 ], [ %369, %true_block67 ]
  %372 = add i32 %51, -1
  %373 = icmp slt i32 %372, %56
  br i1 %373, label %true_block73, label %true_block82

true_block73:                                     ; preds = %true_block70
  %374 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %375 = load float*, float** %374, align 8
  %376 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %377 = load i32, i32* %376, align 4
  %378 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %379 = load i32, i32* %378, align 4
  %380 = shl i32 %377, 3
  %381 = shl i32 %35, 3
  %382 = sub i32 %380, %381
  %383 = mul i32 %382, %44
  %384 = add i32 %lsr.iv, %383
  %385 = add i32 %384, -1
  %386 = mul i32 %385, %379
  %387 = or i32 %386, 1
  %388 = sext i32 %387 to i64
  %389 = getelementptr float, float* %375, i64 %388
  %390 = load float, float* %389, align 4
  %391 = add i32 %386, 2
  %392 = insertelement <2 x i32> poison, i32 %386, i64 0
  %393 = insertelement <2 x i32> %392, i32 %391, i64 1
  %394 = sext <2 x i32> %393 to <2 x i64>
  %395 = insertelement <2 x float*> poison, float* %375, i64 0
  %396 = shufflevector <2 x float*> %395, <2 x float*> poison, <2 x i32> zeroinitializer
  %397 = getelementptr float, <2 x float*> %396, <2 x i64> %394
  %398 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %397, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %399 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %400 = load float, float* %399, align 4
  %401 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %400, float 0x3F1A36E2E0000000)
  %402 = extractelement <2 x float> %398, i64 0
  %403 = fdiv reassoc ninf nsz float %402, %401
  %404 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %405 = load float, float* %404, align 4
  %406 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %405, float 0x3F1A36E2E0000000)
  %407 = fdiv reassoc ninf nsz float %390, %406
  %408 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %409 = load float, float* %408, align 4
  %410 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %409, float 0x3F1A36E2E0000000)
  %411 = extractelement <2 x float> %398, i64 1
  %412 = fdiv reassoc ninf nsz float %411, %410
  %413 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %407, float %412)
  %414 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %403, float %413)
  %415 = fcmp reassoc ninf nsz olt float %414, 0x3FED70A3E0000000
  %416 = fcmp reassoc ninf nsz ogt float %390, 0x3EE4F8B580000000
  %.0436 = select i1 %415, i1 %416, i1 false
  br i1 %.0436, label %true_block79, label %true_block82

after_if75:                                       ; preds = %for_loop_body
  %417 = or i32 %48, 1
  %418 = or i32 %48, 2
  %419 = or i32 %48, 3
  %420 = or i32 %48, 4
  %421 = or i32 %48, 5
  %422 = or i32 %48, 6
  %423 = or i32 %48, 7
  br label %after_if87

true_block79:                                     ; preds = %true_block73
  %424 = insertelement <2 x float> poison, float %390, i64 0
  %425 = shufflevector <2 x float> %424, <2 x float> poison, <2 x i32> zeroinitializer
  %426 = fdiv reassoc ninf nsz <2 x float> %398, %425
  %427 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %426, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %428 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %427, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %429 = fadd reassoc ninf nsz <2 x float> %428, %371
  %430 = fadd reassoc ninf nsz float %.5.ph, 1.000000e+00
  br label %true_block82

true_block82:                                     ; preds = %true_block79, %true_block73, %true_block70
  %.6.ph = phi float [ %.5.ph, %true_block70 ], [ %.5.ph, %true_block73 ], [ %430, %true_block79 ]
  %431 = phi <2 x float> [ %371, %true_block70 ], [ %371, %true_block73 ], [ %429, %true_block79 ]
  %432 = icmp slt i32 %51, %56
  br i1 %432, label %true_block85, label %true_block82.after_if87_crit_edge

true_block82.after_if87_crit_edge:                ; preds = %true_block82
  br label %after_if87

true_block85:                                     ; preds = %true_block82
  %433 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %434 = load float*, float** %433, align 8
  %435 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %436 = load i32, i32* %435, align 4
  %437 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 2
  %438 = load i32, i32* %437, align 4
  %439 = shl i32 %436, 3
  %440 = shl i32 %35, 3
  %441 = sub i32 %439, %440
  %442 = mul i32 %441, %44
  %443 = add i32 %lsr.iv, %442
  %444 = mul i32 %443, %438
  %445 = add i32 %444, 1
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, float* %434, i64 %446
  %448 = load float, float* %447, align 4
  %449 = add i32 %444, 2
  %450 = insertelement <2 x i32> poison, i32 %444, i64 0
  %451 = insertelement <2 x i32> %450, i32 %449, i64 1
  %452 = sext <2 x i32> %451 to <2 x i64>
  %453 = insertelement <2 x float*> poison, float* %434, i64 0
  %454 = shufflevector <2 x float*> %453, <2 x float*> poison, <2 x i32> zeroinitializer
  %455 = getelementptr float, <2 x float*> %454, <2 x i64> %452
  %456 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %455, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %457 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 2
  %458 = load float, float* %457, align 4
  %459 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %458, float 0x3F1A36E2E0000000)
  %460 = extractelement <2 x float> %456, i64 0
  %461 = fdiv reassoc ninf nsz float %460, %459
  %462 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 3
  %463 = load float, float* %462, align 4
  %464 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %463, float 0x3F1A36E2E0000000)
  %465 = fdiv reassoc ninf nsz float %448, %464
  %466 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %54, i64 0, i32 4
  %467 = load float, float* %466, align 4
  %468 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %467, float 0x3F1A36E2E0000000)
  %469 = extractelement <2 x float> %456, i64 1
  %470 = fdiv reassoc ninf nsz float %469, %468
  %471 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %465, float %470)
  %472 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %461, float %471)
  %473 = fcmp reassoc ninf nsz olt float %472, 0x3FED70A3E0000000
  %474 = fcmp reassoc ninf nsz ogt float %448, 0x3EE4F8B580000000
  %.0434 = select i1 %473, i1 %474, i1 false
  br i1 %.0434, label %true_block91, label %true_block85.after_if87_crit_edge

true_block85.after_if87_crit_edge:                ; preds = %true_block85
  br label %after_if87

after_if87:                                       ; preds = %true_block91, %true_block85.after_if87_crit_edge, %true_block82.after_if87_crit_edge, %after_if75
  %475 = phi i32 [ %51, %true_block91 ], [ %51, %true_block85.after_if87_crit_edge ], [ %51, %true_block82.after_if87_crit_edge ], [ %423, %after_if75 ]
  %476 = phi i32 [ %319, %true_block91 ], [ %319, %true_block85.after_if87_crit_edge ], [ %319, %true_block82.after_if87_crit_edge ], [ %421, %after_if75 ]
  %477 = phi i32 [ %213, %true_block91 ], [ %213, %true_block85.after_if87_crit_edge ], [ %213, %true_block82.after_if87_crit_edge ], [ %419, %after_if75 ]
  %478 = phi i32 [ %107, %true_block91 ], [ %107, %true_block85.after_if87_crit_edge ], [ %107, %true_block82.after_if87_crit_edge ], [ %417, %after_if75 ]
  %479 = phi i32 [ %160, %true_block91 ], [ %160, %true_block85.after_if87_crit_edge ], [ %160, %true_block82.after_if87_crit_edge ], [ %418, %after_if75 ]
  %480 = phi i32 [ %266, %true_block91 ], [ %266, %true_block85.after_if87_crit_edge ], [ %266, %true_block82.after_if87_crit_edge ], [ %420, %after_if75 ]
  %481 = phi i32 [ %372, %true_block91 ], [ %372, %true_block85.after_if87_crit_edge ], [ %372, %true_block82.after_if87_crit_edge ], [ %422, %after_if75 ]
  %.7 = phi float [ %491, %true_block91 ], [ %.6.ph, %true_block85.after_if87_crit_edge ], [ %.6.ph, %true_block82.after_if87_crit_edge ], [ 0.000000e+00, %after_if75 ]
  %482 = phi <2 x float> [ %490, %true_block91 ], [ %431, %true_block85.after_if87_crit_edge ], [ %431, %true_block82.after_if87_crit_edge ], [ zeroinitializer, %after_if75 ]
  %483 = or i32 %47, 1
  %484 = icmp slt i32 %483, %23
  br i1 %484, label %true_block94, label %after_if183

true_block91:                                     ; preds = %true_block85
  %485 = insertelement <2 x float> poison, float %448, i64 0
  %486 = shufflevector <2 x float> %485, <2 x float> poison, <2 x i32> zeroinitializer
  %487 = fdiv reassoc ninf nsz <2 x float> %456, %486
  %488 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %487, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %489 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %488, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %490 = fadd reassoc ninf nsz <2 x float> %489, %431
  %491 = fadd reassoc ninf nsz float %.6.ph, 1.000000e+00
  br label %after_if87

true_block94:                                     ; preds = %after_if87
  %492 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %493 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 6
  %494 = load i32, i32* %493, align 4
  %495 = icmp slt i32 %52, %494
  br i1 %495, label %true_block97, label %true_block106

true_block97:                                     ; preds = %true_block94
  %496 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %497 = load float*, float** %496, align 8
  %498 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %499 = load i32, i32* %498, align 4
  %500 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %501 = load i32, i32* %500, align 4
  %502 = mul i32 %499, %483
  %503 = shl i32 %35, 3
  %504 = mul i32 %503, %44
  %505 = sub i32 %502, %504
  %506 = add i32 %lsr.iv, %505
  %507 = add i32 %506, -7
  %508 = mul i32 %507, %501
  %509 = add i32 %508, 1
  %510 = sext i32 %509 to i64
  %511 = getelementptr float, float* %497, i64 %510
  %512 = load float, float* %511, align 4
  %513 = add i32 %508, 2
  %514 = insertelement <2 x i32> poison, i32 %508, i64 0
  %515 = insertelement <2 x i32> %514, i32 %513, i64 1
  %516 = sext <2 x i32> %515 to <2 x i64>
  %517 = insertelement <2 x float*> poison, float* %497, i64 0
  %518 = shufflevector <2 x float*> %517, <2 x float*> poison, <2 x i32> zeroinitializer
  %519 = getelementptr float, <2 x float*> %518, <2 x i64> %516
  %520 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %519, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %521 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %522 = load float, float* %521, align 4
  %523 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %522, float 0x3F1A36E2E0000000)
  %524 = extractelement <2 x float> %520, i64 0
  %525 = fdiv reassoc ninf nsz float %524, %523
  %526 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %527 = load float, float* %526, align 4
  %528 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %527, float 0x3F1A36E2E0000000)
  %529 = fdiv reassoc ninf nsz float %512, %528
  %530 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %531 = load float, float* %530, align 4
  %532 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %531, float 0x3F1A36E2E0000000)
  %533 = extractelement <2 x float> %520, i64 1
  %534 = fdiv reassoc ninf nsz float %533, %532
  %535 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %529, float %534)
  %536 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %525, float %535)
  %537 = fcmp reassoc ninf nsz olt float %536, 0x3FED70A3E0000000
  %538 = fcmp reassoc ninf nsz ogt float %512, 0x3EE4F8B580000000
  %.0432 = select i1 %537, i1 %538, i1 false
  br i1 %.0432, label %true_block103, label %true_block106

true_block103:                                    ; preds = %true_block97
  %539 = insertelement <2 x float> poison, float %512, i64 0
  %540 = shufflevector <2 x float> %539, <2 x float> poison, <2 x i32> zeroinitializer
  %541 = fdiv reassoc ninf nsz <2 x float> %520, %540
  %542 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %541, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %543 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %542, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %544 = fadd reassoc ninf nsz <2 x float> %543, %482
  %545 = fadd reassoc ninf nsz float %.7, 1.000000e+00
  br label %true_block106

true_block106:                                    ; preds = %true_block103, %true_block97, %true_block94
  %.8.ph = phi float [ %.7, %true_block94 ], [ %.7, %true_block97 ], [ %545, %true_block103 ]
  %546 = phi <2 x float> [ %482, %true_block94 ], [ %482, %true_block97 ], [ %544, %true_block103 ]
  %547 = icmp slt i32 %478, %494
  br i1 %547, label %true_block109, label %true_block118

true_block109:                                    ; preds = %true_block106
  %548 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %549 = load float*, float** %548, align 8
  %550 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %551 = load i32, i32* %550, align 4
  %552 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %553 = load i32, i32* %552, align 4
  %554 = mul i32 %551, %483
  %555 = add i32 %554, %478
  %556 = mul i32 %555, %553
  %557 = sext i32 %556 to i64
  %558 = getelementptr float, float* %549, i64 %557
  %559 = load float, float* %558, align 4
  %560 = add i32 %556, 1
  %561 = sext i32 %560 to i64
  %562 = getelementptr float, float* %549, i64 %561
  %563 = load float, float* %562, align 4
  %564 = add i32 %556, 2
  %565 = sext i32 %564 to i64
  %566 = getelementptr float, float* %549, i64 %565
  %567 = load float, float* %566, align 4
  %568 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %569 = load float, float* %568, align 4
  %570 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %569, float 0x3F1A36E2E0000000)
  %571 = fdiv reassoc ninf nsz float %559, %570
  %572 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %573 = load float, float* %572, align 4
  %574 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %573, float 0x3F1A36E2E0000000)
  %575 = fdiv reassoc ninf nsz float %563, %574
  %576 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %577 = load float, float* %576, align 4
  %578 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %577, float 0x3F1A36E2E0000000)
  %579 = fdiv reassoc ninf nsz float %567, %578
  %580 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %575, float %579)
  %581 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %571, float %580)
  %582 = fcmp reassoc ninf nsz olt float %581, 0x3FED70A3E0000000
  %583 = fcmp reassoc ninf nsz ogt float %563, 0x3EE4F8B580000000
  %.0430 = select i1 %582, i1 %583, i1 false
  br i1 %.0430, label %true_block115, label %true_block118

true_block115:                                    ; preds = %true_block109
  %584 = insertelement <2 x float> poison, float %559, i64 0
  %585 = insertelement <2 x float> %584, float %567, i64 1
  %586 = insertelement <2 x float> poison, float %563, i64 0
  %587 = shufflevector <2 x float> %586, <2 x float> poison, <2 x i32> zeroinitializer
  %588 = fdiv reassoc ninf nsz <2 x float> %585, %587
  %589 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %588, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %590 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %589, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %591 = fadd reassoc ninf nsz <2 x float> %590, %546
  %592 = fadd reassoc ninf nsz float %.8.ph, 1.000000e+00
  br label %true_block118

true_block118:                                    ; preds = %true_block115, %true_block109, %true_block106
  %.9.ph = phi float [ %.8.ph, %true_block106 ], [ %.8.ph, %true_block109 ], [ %592, %true_block115 ]
  %593 = phi <2 x float> [ %546, %true_block106 ], [ %546, %true_block109 ], [ %591, %true_block115 ]
  %594 = icmp slt i32 %479, %494
  br i1 %594, label %true_block121, label %true_block130

true_block121:                                    ; preds = %true_block118
  %595 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %596 = load float*, float** %595, align 8
  %597 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %598 = load i32, i32* %597, align 4
  %599 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %600 = load i32, i32* %599, align 4
  %601 = mul i32 %598, %483
  %602 = add i32 %601, %479
  %603 = mul i32 %602, %600
  %604 = sext i32 %603 to i64
  %605 = getelementptr float, float* %596, i64 %604
  %606 = add i32 %603, 1
  %607 = sext i32 %606 to i64
  %608 = getelementptr float, float* %596, i64 %607
  %609 = load float, float* %608, align 4
  %610 = add i32 %603, 2
  %611 = sext i32 %610 to i64
  %612 = getelementptr float, float* %596, i64 %611
  %613 = insertelement <2 x float*> poison, float* %605, i64 0
  %614 = insertelement <2 x float*> %613, float* %612, i64 1
  %615 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %614, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %616 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %617 = load float, float* %616, align 4
  %618 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %617, float 0x3F1A36E2E0000000)
  %619 = extractelement <2 x float> %615, i64 0
  %620 = fdiv reassoc ninf nsz float %619, %618
  %621 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %622 = load float, float* %621, align 4
  %623 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %622, float 0x3F1A36E2E0000000)
  %624 = fdiv reassoc ninf nsz float %609, %623
  %625 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %626 = load float, float* %625, align 4
  %627 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %626, float 0x3F1A36E2E0000000)
  %628 = extractelement <2 x float> %615, i64 1
  %629 = fdiv reassoc ninf nsz float %628, %627
  %630 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %624, float %629)
  %631 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %620, float %630)
  %632 = fcmp reassoc ninf nsz olt float %631, 0x3FED70A3E0000000
  %633 = fcmp reassoc ninf nsz ogt float %609, 0x3EE4F8B580000000
  %.0428 = select i1 %632, i1 %633, i1 false
  br i1 %.0428, label %true_block127, label %true_block130

true_block127:                                    ; preds = %true_block121
  %634 = insertelement <2 x float> poison, float %609, i64 0
  %635 = shufflevector <2 x float> %634, <2 x float> poison, <2 x i32> zeroinitializer
  %636 = fdiv reassoc ninf nsz <2 x float> %615, %635
  %637 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %636, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %638 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %637, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %639 = fadd reassoc ninf nsz <2 x float> %638, %593
  %640 = fadd reassoc ninf nsz float %.9.ph, 1.000000e+00
  br label %true_block130

true_block130:                                    ; preds = %true_block127, %true_block121, %true_block118
  %.10.ph = phi float [ %.9.ph, %true_block118 ], [ %.9.ph, %true_block121 ], [ %640, %true_block127 ]
  %641 = phi <2 x float> [ %593, %true_block118 ], [ %593, %true_block121 ], [ %639, %true_block127 ]
  %642 = icmp slt i32 %477, %494
  br i1 %642, label %true_block133, label %true_block142

true_block133:                                    ; preds = %true_block130
  %643 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %644 = load float*, float** %643, align 8
  %645 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %646 = load i32, i32* %645, align 4
  %647 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %648 = load i32, i32* %647, align 4
  %649 = mul i32 %646, %483
  %650 = add i32 %649, %477
  %651 = mul i32 %650, %648
  %652 = add i32 %651, 1
  %653 = sext i32 %652 to i64
  %654 = getelementptr float, float* %644, i64 %653
  %655 = load float, float* %654, align 4
  %656 = add i32 %651, 2
  %657 = insertelement <2 x i32> poison, i32 %651, i64 0
  %658 = insertelement <2 x i32> %657, i32 %656, i64 1
  %659 = sext <2 x i32> %658 to <2 x i64>
  %660 = insertelement <2 x float*> poison, float* %644, i64 0
  %661 = shufflevector <2 x float*> %660, <2 x float*> poison, <2 x i32> zeroinitializer
  %662 = getelementptr float, <2 x float*> %661, <2 x i64> %659
  %663 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %662, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %664 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %665 = load float, float* %664, align 4
  %666 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %665, float 0x3F1A36E2E0000000)
  %667 = extractelement <2 x float> %663, i64 0
  %668 = fdiv reassoc ninf nsz float %667, %666
  %669 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %670 = load float, float* %669, align 4
  %671 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %670, float 0x3F1A36E2E0000000)
  %672 = fdiv reassoc ninf nsz float %655, %671
  %673 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %674 = load float, float* %673, align 4
  %675 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %674, float 0x3F1A36E2E0000000)
  %676 = extractelement <2 x float> %663, i64 1
  %677 = fdiv reassoc ninf nsz float %676, %675
  %678 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %672, float %677)
  %679 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %668, float %678)
  %680 = fcmp reassoc ninf nsz olt float %679, 0x3FED70A3E0000000
  %681 = fcmp reassoc ninf nsz ogt float %655, 0x3EE4F8B580000000
  %.0426 = select i1 %680, i1 %681, i1 false
  br i1 %.0426, label %true_block139, label %true_block142

true_block139:                                    ; preds = %true_block133
  %682 = insertelement <2 x float> poison, float %655, i64 0
  %683 = shufflevector <2 x float> %682, <2 x float> poison, <2 x i32> zeroinitializer
  %684 = fdiv reassoc ninf nsz <2 x float> %663, %683
  %685 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %684, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %686 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %685, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %687 = fadd reassoc ninf nsz <2 x float> %686, %641
  %688 = fadd reassoc ninf nsz float %.10.ph, 1.000000e+00
  br label %true_block142

true_block142:                                    ; preds = %true_block139, %true_block133, %true_block130
  %.11.ph = phi float [ %.10.ph, %true_block130 ], [ %.10.ph, %true_block133 ], [ %688, %true_block139 ]
  %689 = phi <2 x float> [ %641, %true_block130 ], [ %641, %true_block133 ], [ %687, %true_block139 ]
  %690 = icmp slt i32 %480, %494
  br i1 %690, label %true_block145, label %true_block154

true_block145:                                    ; preds = %true_block142
  %691 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %692 = load float*, float** %691, align 8
  %693 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %694 = load i32, i32* %693, align 4
  %695 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %696 = load i32, i32* %695, align 4
  %697 = mul i32 %694, %483
  %698 = add i32 %697, %480
  %699 = mul i32 %698, %696
  %700 = add i32 %699, 1
  %701 = sext i32 %700 to i64
  %702 = getelementptr float, float* %692, i64 %701
  %703 = load float, float* %702, align 4
  %704 = add i32 %699, 2
  %705 = insertelement <2 x i32> poison, i32 %699, i64 0
  %706 = insertelement <2 x i32> %705, i32 %704, i64 1
  %707 = sext <2 x i32> %706 to <2 x i64>
  %708 = insertelement <2 x float*> poison, float* %692, i64 0
  %709 = shufflevector <2 x float*> %708, <2 x float*> poison, <2 x i32> zeroinitializer
  %710 = getelementptr float, <2 x float*> %709, <2 x i64> %707
  %711 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %710, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %712 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %713 = load float, float* %712, align 4
  %714 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %713, float 0x3F1A36E2E0000000)
  %715 = extractelement <2 x float> %711, i64 0
  %716 = fdiv reassoc ninf nsz float %715, %714
  %717 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %718 = load float, float* %717, align 4
  %719 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %718, float 0x3F1A36E2E0000000)
  %720 = fdiv reassoc ninf nsz float %703, %719
  %721 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %722 = load float, float* %721, align 4
  %723 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %722, float 0x3F1A36E2E0000000)
  %724 = extractelement <2 x float> %711, i64 1
  %725 = fdiv reassoc ninf nsz float %724, %723
  %726 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %720, float %725)
  %727 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %716, float %726)
  %728 = fcmp reassoc ninf nsz olt float %727, 0x3FED70A3E0000000
  %729 = fcmp reassoc ninf nsz ogt float %703, 0x3EE4F8B580000000
  %.0424 = select i1 %728, i1 %729, i1 false
  br i1 %.0424, label %true_block151, label %true_block154

true_block151:                                    ; preds = %true_block145
  %730 = insertelement <2 x float> poison, float %703, i64 0
  %731 = shufflevector <2 x float> %730, <2 x float> poison, <2 x i32> zeroinitializer
  %732 = fdiv reassoc ninf nsz <2 x float> %711, %731
  %733 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %732, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %734 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %733, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %735 = fadd reassoc ninf nsz <2 x float> %734, %689
  %736 = fadd reassoc ninf nsz float %.11.ph, 1.000000e+00
  br label %true_block154

true_block154:                                    ; preds = %true_block151, %true_block145, %true_block142
  %.12.ph = phi float [ %.11.ph, %true_block142 ], [ %.11.ph, %true_block145 ], [ %736, %true_block151 ]
  %737 = phi <2 x float> [ %689, %true_block142 ], [ %689, %true_block145 ], [ %735, %true_block151 ]
  %738 = icmp slt i32 %476, %494
  br i1 %738, label %true_block157, label %true_block166

true_block157:                                    ; preds = %true_block154
  %739 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %740 = load float*, float** %739, align 8
  %741 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %742 = load i32, i32* %741, align 4
  %743 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %744 = load i32, i32* %743, align 4
  %745 = mul i32 %742, %483
  %746 = add i32 %745, %476
  %747 = mul i32 %746, %744
  %748 = add i32 %747, 1
  %749 = sext i32 %748 to i64
  %750 = getelementptr float, float* %740, i64 %749
  %751 = load float, float* %750, align 4
  %752 = add i32 %747, 2
  %753 = insertelement <2 x i32> poison, i32 %747, i64 0
  %754 = insertelement <2 x i32> %753, i32 %752, i64 1
  %755 = sext <2 x i32> %754 to <2 x i64>
  %756 = insertelement <2 x float*> poison, float* %740, i64 0
  %757 = shufflevector <2 x float*> %756, <2 x float*> poison, <2 x i32> zeroinitializer
  %758 = getelementptr float, <2 x float*> %757, <2 x i64> %755
  %759 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %758, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %760 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %761 = load float, float* %760, align 4
  %762 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %761, float 0x3F1A36E2E0000000)
  %763 = extractelement <2 x float> %759, i64 0
  %764 = fdiv reassoc ninf nsz float %763, %762
  %765 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %766 = load float, float* %765, align 4
  %767 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %766, float 0x3F1A36E2E0000000)
  %768 = fdiv reassoc ninf nsz float %751, %767
  %769 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %770 = load float, float* %769, align 4
  %771 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %770, float 0x3F1A36E2E0000000)
  %772 = extractelement <2 x float> %759, i64 1
  %773 = fdiv reassoc ninf nsz float %772, %771
  %774 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %768, float %773)
  %775 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %764, float %774)
  %776 = fcmp reassoc ninf nsz olt float %775, 0x3FED70A3E0000000
  %777 = fcmp reassoc ninf nsz ogt float %751, 0x3EE4F8B580000000
  %.0422 = select i1 %776, i1 %777, i1 false
  br i1 %.0422, label %true_block163, label %true_block166

true_block163:                                    ; preds = %true_block157
  %778 = insertelement <2 x float> poison, float %751, i64 0
  %779 = shufflevector <2 x float> %778, <2 x float> poison, <2 x i32> zeroinitializer
  %780 = fdiv reassoc ninf nsz <2 x float> %759, %779
  %781 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %780, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %782 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %781, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %783 = fadd reassoc ninf nsz <2 x float> %782, %737
  %784 = fadd reassoc ninf nsz float %.12.ph, 1.000000e+00
  br label %true_block166

true_block166:                                    ; preds = %true_block163, %true_block157, %true_block154
  %.13.ph = phi float [ %.12.ph, %true_block154 ], [ %.12.ph, %true_block157 ], [ %784, %true_block163 ]
  %785 = phi <2 x float> [ %737, %true_block154 ], [ %737, %true_block157 ], [ %783, %true_block163 ]
  %786 = icmp slt i32 %481, %494
  br i1 %786, label %true_block169, label %true_block178

true_block169:                                    ; preds = %true_block166
  %787 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %788 = load float*, float** %787, align 8
  %789 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %790 = load i32, i32* %789, align 4
  %791 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %792 = load i32, i32* %791, align 4
  %793 = mul i32 %790, %483
  %794 = add i32 %793, %481
  %795 = mul i32 %794, %792
  %796 = add i32 %795, 1
  %797 = sext i32 %796 to i64
  %798 = getelementptr float, float* %788, i64 %797
  %799 = load float, float* %798, align 4
  %800 = add i32 %795, 2
  %801 = insertelement <2 x i32> poison, i32 %795, i64 0
  %802 = insertelement <2 x i32> %801, i32 %800, i64 1
  %803 = sext <2 x i32> %802 to <2 x i64>
  %804 = insertelement <2 x float*> poison, float* %788, i64 0
  %805 = shufflevector <2 x float*> %804, <2 x float*> poison, <2 x i32> zeroinitializer
  %806 = getelementptr float, <2 x float*> %805, <2 x i64> %803
  %807 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %806, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %808 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %809 = load float, float* %808, align 4
  %810 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %809, float 0x3F1A36E2E0000000)
  %811 = extractelement <2 x float> %807, i64 0
  %812 = fdiv reassoc ninf nsz float %811, %810
  %813 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %814 = load float, float* %813, align 4
  %815 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %814, float 0x3F1A36E2E0000000)
  %816 = fdiv reassoc ninf nsz float %799, %815
  %817 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %818 = load float, float* %817, align 4
  %819 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %818, float 0x3F1A36E2E0000000)
  %820 = extractelement <2 x float> %807, i64 1
  %821 = fdiv reassoc ninf nsz float %820, %819
  %822 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %816, float %821)
  %823 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %812, float %822)
  %824 = fcmp reassoc ninf nsz olt float %823, 0x3FED70A3E0000000
  %825 = fcmp reassoc ninf nsz ogt float %799, 0x3EE4F8B580000000
  %.0420 = select i1 %824, i1 %825, i1 false
  br i1 %.0420, label %true_block175, label %true_block178

true_block175:                                    ; preds = %true_block169
  %826 = insertelement <2 x float> poison, float %799, i64 0
  %827 = shufflevector <2 x float> %826, <2 x float> poison, <2 x i32> zeroinitializer
  %828 = fdiv reassoc ninf nsz <2 x float> %807, %827
  %829 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %828, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %830 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %829, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %831 = fadd reassoc ninf nsz <2 x float> %830, %785
  %832 = fadd reassoc ninf nsz float %.13.ph, 1.000000e+00
  br label %true_block178

true_block178:                                    ; preds = %true_block175, %true_block169, %true_block166
  %.14.ph = phi float [ %.13.ph, %true_block166 ], [ %.13.ph, %true_block169 ], [ %832, %true_block175 ]
  %833 = phi <2 x float> [ %785, %true_block166 ], [ %785, %true_block169 ], [ %831, %true_block175 ]
  %834 = icmp slt i32 %475, %494
  br i1 %834, label %true_block181, label %after_if183

true_block181:                                    ; preds = %true_block178
  %835 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 1
  %836 = load float*, float** %835, align 8
  %837 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 1
  %838 = load i32, i32* %837, align 4
  %839 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 0, i32 0, i32 2
  %840 = load i32, i32* %839, align 4
  %841 = mul i32 %838, %483
  %842 = add i32 %841, %475
  %843 = mul i32 %842, %840
  %844 = add i32 %843, 1
  %845 = sext i32 %844 to i64
  %846 = getelementptr float, float* %836, i64 %845
  %847 = load float, float* %846, align 4
  %848 = add i32 %843, 2
  %849 = insertelement <2 x i32> poison, i32 %843, i64 0
  %850 = insertelement <2 x i32> %849, i32 %848, i64 1
  %851 = sext <2 x i32> %850 to <2 x i64>
  %852 = insertelement <2 x float*> poison, float* %836, i64 0
  %853 = shufflevector <2 x float*> %852, <2 x float*> poison, <2 x i32> zeroinitializer
  %854 = getelementptr float, <2 x float*> %853, <2 x i64> %851
  %855 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %854, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %856 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 2
  %857 = load float, float* %856, align 4
  %858 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %857, float 0x3F1A36E2E0000000)
  %859 = extractelement <2 x float> %855, i64 0
  %860 = fdiv reassoc ninf nsz float %859, %858
  %861 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 3
  %862 = load float, float* %861, align 4
  %863 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %862, float 0x3F1A36E2E0000000)
  %864 = fdiv reassoc ninf nsz float %847, %863
  %865 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %492, i64 0, i32 4
  %866 = load float, float* %865, align 4
  %867 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %866, float 0x3F1A36E2E0000000)
  %868 = extractelement <2 x float> %855, i64 1
  %869 = fdiv reassoc ninf nsz float %868, %867
  %870 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %864, float %869)
  %871 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %860, float %870)
  %872 = fcmp reassoc ninf nsz olt float %871, 0x3FED70A3E0000000
  %873 = fcmp reassoc ninf nsz ogt float %847, 0x3EE4F8B580000000
  %.0418 = select i1 %872, i1 %873, i1 false
  br i1 %.0418, label %true_block187, label %after_if183

after_if183:                                      ; preds = %true_block187, %true_block181, %true_block178, %after_if87
  %.15 = phi float [ %883, %true_block187 ], [ %.14.ph, %true_block181 ], [ %.14.ph, %true_block178 ], [ %.7, %after_if87 ]
  %874 = phi <2 x float> [ %882, %true_block187 ], [ %833, %true_block181 ], [ %833, %true_block178 ], [ %482, %after_if87 ]
  %875 = or i32 %47, 2
  %876 = icmp slt i32 %875, %23
  br i1 %876, label %true_block190, label %after_if279

true_block187:                                    ; preds = %true_block181
  %877 = insertelement <2 x float> poison, float %847, i64 0
  %878 = shufflevector <2 x float> %877, <2 x float> poison, <2 x i32> zeroinitializer
  %879 = fdiv reassoc ninf nsz <2 x float> %855, %878
  %880 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %879, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %881 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %880, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %882 = fadd reassoc ninf nsz <2 x float> %881, %833
  %883 = fadd reassoc ninf nsz float %.14.ph, 1.000000e+00
  br label %after_if183

true_block190:                                    ; preds = %after_if183
  %884 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %885 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 6
  %886 = load i32, i32* %885, align 4
  %887 = icmp slt i32 %52, %886
  br i1 %887, label %true_block193, label %true_block202

true_block193:                                    ; preds = %true_block190
  %888 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %889 = load float*, float** %888, align 8
  %890 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %891 = load i32, i32* %890, align 4
  %892 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %893 = load i32, i32* %892, align 4
  %894 = mul i32 %891, %875
  %895 = shl i32 %35, 3
  %896 = mul i32 %895, %44
  %897 = sub i32 %894, %896
  %898 = add i32 %lsr.iv, %897
  %899 = add i32 %898, -7
  %900 = mul i32 %899, %893
  %901 = sext i32 %900 to i64
  %902 = getelementptr float, float* %889, i64 %901
  %903 = load float, float* %902, align 4
  %904 = or i32 %900, 1
  %905 = sext i32 %904 to i64
  %906 = getelementptr float, float* %889, i64 %905
  %907 = load float, float* %906, align 4
  %908 = add i32 %900, 2
  %909 = sext i32 %908 to i64
  %910 = getelementptr float, float* %889, i64 %909
  %911 = load float, float* %910, align 4
  %912 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %913 = load float, float* %912, align 4
  %914 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %913, float 0x3F1A36E2E0000000)
  %915 = fdiv reassoc ninf nsz float %903, %914
  %916 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %917 = load float, float* %916, align 4
  %918 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %917, float 0x3F1A36E2E0000000)
  %919 = fdiv reassoc ninf nsz float %907, %918
  %920 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %921 = load float, float* %920, align 4
  %922 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %921, float 0x3F1A36E2E0000000)
  %923 = fdiv reassoc ninf nsz float %911, %922
  %924 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %919, float %923)
  %925 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %915, float %924)
  %926 = fcmp reassoc ninf nsz olt float %925, 0x3FED70A3E0000000
  %927 = fcmp reassoc ninf nsz ogt float %907, 0x3EE4F8B580000000
  %.0416 = select i1 %926, i1 %927, i1 false
  br i1 %.0416, label %true_block199, label %true_block202

true_block199:                                    ; preds = %true_block193
  %928 = insertelement <2 x float> poison, float %903, i64 0
  %929 = insertelement <2 x float> %928, float %911, i64 1
  %930 = insertelement <2 x float> poison, float %907, i64 0
  %931 = shufflevector <2 x float> %930, <2 x float> poison, <2 x i32> zeroinitializer
  %932 = fdiv reassoc ninf nsz <2 x float> %929, %931
  %933 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %932, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %934 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %933, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %935 = fadd reassoc ninf nsz <2 x float> %934, %874
  %936 = fadd reassoc ninf nsz float %.15, 1.000000e+00
  br label %true_block202

true_block202:                                    ; preds = %true_block199, %true_block193, %true_block190
  %.16.ph = phi float [ %.15, %true_block190 ], [ %.15, %true_block193 ], [ %936, %true_block199 ]
  %937 = phi <2 x float> [ %874, %true_block190 ], [ %874, %true_block193 ], [ %935, %true_block199 ]
  %938 = icmp slt i32 %478, %886
  br i1 %938, label %true_block205, label %true_block214

true_block205:                                    ; preds = %true_block202
  %939 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %940 = load float*, float** %939, align 8
  %941 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %942 = load i32, i32* %941, align 4
  %943 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %944 = load i32, i32* %943, align 4
  %945 = mul i32 %942, %875
  %946 = add i32 %945, %478
  %947 = mul i32 %946, %944
  %948 = sext i32 %947 to i64
  %949 = getelementptr float, float* %940, i64 %948
  %950 = add i32 %947, 1
  %951 = sext i32 %950 to i64
  %952 = getelementptr float, float* %940, i64 %951
  %953 = load float, float* %952, align 4
  %954 = add i32 %947, 2
  %955 = sext i32 %954 to i64
  %956 = getelementptr float, float* %940, i64 %955
  %957 = insertelement <2 x float*> poison, float* %949, i64 0
  %958 = insertelement <2 x float*> %957, float* %956, i64 1
  %959 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %958, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %960 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %961 = load float, float* %960, align 4
  %962 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %961, float 0x3F1A36E2E0000000)
  %963 = extractelement <2 x float> %959, i64 0
  %964 = fdiv reassoc ninf nsz float %963, %962
  %965 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %966 = load float, float* %965, align 4
  %967 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %966, float 0x3F1A36E2E0000000)
  %968 = fdiv reassoc ninf nsz float %953, %967
  %969 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %970 = load float, float* %969, align 4
  %971 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %970, float 0x3F1A36E2E0000000)
  %972 = extractelement <2 x float> %959, i64 1
  %973 = fdiv reassoc ninf nsz float %972, %971
  %974 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %968, float %973)
  %975 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %964, float %974)
  %976 = fcmp reassoc ninf nsz olt float %975, 0x3FED70A3E0000000
  %977 = fcmp reassoc ninf nsz ogt float %953, 0x3EE4F8B580000000
  %.0414 = select i1 %976, i1 %977, i1 false
  br i1 %.0414, label %true_block211, label %true_block214

true_block211:                                    ; preds = %true_block205
  %978 = insertelement <2 x float> poison, float %953, i64 0
  %979 = shufflevector <2 x float> %978, <2 x float> poison, <2 x i32> zeroinitializer
  %980 = fdiv reassoc ninf nsz <2 x float> %959, %979
  %981 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %980, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %982 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %981, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %983 = fadd reassoc ninf nsz <2 x float> %982, %937
  %984 = fadd reassoc ninf nsz float %.16.ph, 1.000000e+00
  br label %true_block214

true_block214:                                    ; preds = %true_block211, %true_block205, %true_block202
  %.17.ph = phi float [ %.16.ph, %true_block202 ], [ %.16.ph, %true_block205 ], [ %984, %true_block211 ]
  %985 = phi <2 x float> [ %937, %true_block202 ], [ %937, %true_block205 ], [ %983, %true_block211 ]
  %986 = icmp slt i32 %479, %886
  br i1 %986, label %true_block217, label %true_block226

true_block217:                                    ; preds = %true_block214
  %987 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %988 = load float*, float** %987, align 8
  %989 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %990 = load i32, i32* %989, align 4
  %991 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %992 = load i32, i32* %991, align 4
  %993 = mul i32 %990, %875
  %994 = add i32 %993, %479
  %995 = mul i32 %994, %992
  %996 = or i32 %995, 1
  %997 = sext i32 %996 to i64
  %998 = getelementptr float, float* %988, i64 %997
  %999 = load float, float* %998, align 4
  %1000 = add i32 %995, 2
  %1001 = insertelement <2 x i32> poison, i32 %995, i64 0
  %1002 = insertelement <2 x i32> %1001, i32 %1000, i64 1
  %1003 = sext <2 x i32> %1002 to <2 x i64>
  %1004 = insertelement <2 x float*> poison, float* %988, i64 0
  %1005 = shufflevector <2 x float*> %1004, <2 x float*> poison, <2 x i32> zeroinitializer
  %1006 = getelementptr float, <2 x float*> %1005, <2 x i64> %1003
  %1007 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1006, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1008 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %1009 = load float, float* %1008, align 4
  %1010 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1009, float 0x3F1A36E2E0000000)
  %1011 = extractelement <2 x float> %1007, i64 0
  %1012 = fdiv reassoc ninf nsz float %1011, %1010
  %1013 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %1014 = load float, float* %1013, align 4
  %1015 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1014, float 0x3F1A36E2E0000000)
  %1016 = fdiv reassoc ninf nsz float %999, %1015
  %1017 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %1018 = load float, float* %1017, align 4
  %1019 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1018, float 0x3F1A36E2E0000000)
  %1020 = extractelement <2 x float> %1007, i64 1
  %1021 = fdiv reassoc ninf nsz float %1020, %1019
  %1022 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1016, float %1021)
  %1023 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1012, float %1022)
  %1024 = fcmp reassoc ninf nsz olt float %1023, 0x3FED70A3E0000000
  %1025 = fcmp reassoc ninf nsz ogt float %999, 0x3EE4F8B580000000
  %.0412 = select i1 %1024, i1 %1025, i1 false
  br i1 %.0412, label %true_block223, label %true_block226

true_block223:                                    ; preds = %true_block217
  %1026 = insertelement <2 x float> poison, float %999, i64 0
  %1027 = shufflevector <2 x float> %1026, <2 x float> poison, <2 x i32> zeroinitializer
  %1028 = fdiv reassoc ninf nsz <2 x float> %1007, %1027
  %1029 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1028, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1030 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1029, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1031 = fadd reassoc ninf nsz <2 x float> %1030, %985
  %1032 = fadd reassoc ninf nsz float %.17.ph, 1.000000e+00
  br label %true_block226

true_block226:                                    ; preds = %true_block223, %true_block217, %true_block214
  %.18.ph = phi float [ %.17.ph, %true_block214 ], [ %.17.ph, %true_block217 ], [ %1032, %true_block223 ]
  %1033 = phi <2 x float> [ %985, %true_block214 ], [ %985, %true_block217 ], [ %1031, %true_block223 ]
  %1034 = icmp slt i32 %477, %886
  br i1 %1034, label %true_block229, label %true_block238

true_block229:                                    ; preds = %true_block226
  %1035 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %1036 = load float*, float** %1035, align 8
  %1037 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %1038 = load i32, i32* %1037, align 4
  %1039 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %1040 = load i32, i32* %1039, align 4
  %1041 = mul i32 %1038, %875
  %1042 = add i32 %1041, %477
  %1043 = mul i32 %1042, %1040
  %1044 = add i32 %1043, 1
  %1045 = sext i32 %1044 to i64
  %1046 = getelementptr float, float* %1036, i64 %1045
  %1047 = load float, float* %1046, align 4
  %1048 = add i32 %1043, 2
  %1049 = insertelement <2 x i32> poison, i32 %1043, i64 0
  %1050 = insertelement <2 x i32> %1049, i32 %1048, i64 1
  %1051 = sext <2 x i32> %1050 to <2 x i64>
  %1052 = insertelement <2 x float*> poison, float* %1036, i64 0
  %1053 = shufflevector <2 x float*> %1052, <2 x float*> poison, <2 x i32> zeroinitializer
  %1054 = getelementptr float, <2 x float*> %1053, <2 x i64> %1051
  %1055 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1054, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1056 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %1057 = load float, float* %1056, align 4
  %1058 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1057, float 0x3F1A36E2E0000000)
  %1059 = extractelement <2 x float> %1055, i64 0
  %1060 = fdiv reassoc ninf nsz float %1059, %1058
  %1061 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %1062 = load float, float* %1061, align 4
  %1063 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1062, float 0x3F1A36E2E0000000)
  %1064 = fdiv reassoc ninf nsz float %1047, %1063
  %1065 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %1066 = load float, float* %1065, align 4
  %1067 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1066, float 0x3F1A36E2E0000000)
  %1068 = extractelement <2 x float> %1055, i64 1
  %1069 = fdiv reassoc ninf nsz float %1068, %1067
  %1070 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1064, float %1069)
  %1071 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1060, float %1070)
  %1072 = fcmp reassoc ninf nsz olt float %1071, 0x3FED70A3E0000000
  %1073 = fcmp reassoc ninf nsz ogt float %1047, 0x3EE4F8B580000000
  %.0410 = select i1 %1072, i1 %1073, i1 false
  br i1 %.0410, label %true_block235, label %true_block238

true_block235:                                    ; preds = %true_block229
  %1074 = insertelement <2 x float> poison, float %1047, i64 0
  %1075 = shufflevector <2 x float> %1074, <2 x float> poison, <2 x i32> zeroinitializer
  %1076 = fdiv reassoc ninf nsz <2 x float> %1055, %1075
  %1077 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1076, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1078 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1077, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1079 = fadd reassoc ninf nsz <2 x float> %1078, %1033
  %1080 = fadd reassoc ninf nsz float %.18.ph, 1.000000e+00
  br label %true_block238

true_block238:                                    ; preds = %true_block235, %true_block229, %true_block226
  %.19.ph = phi float [ %.18.ph, %true_block226 ], [ %.18.ph, %true_block229 ], [ %1080, %true_block235 ]
  %1081 = phi <2 x float> [ %1033, %true_block226 ], [ %1033, %true_block229 ], [ %1079, %true_block235 ]
  %1082 = icmp slt i32 %480, %886
  br i1 %1082, label %true_block241, label %true_block250

true_block241:                                    ; preds = %true_block238
  %1083 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %1084 = load float*, float** %1083, align 8
  %1085 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %1086 = load i32, i32* %1085, align 4
  %1087 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %1088 = load i32, i32* %1087, align 4
  %1089 = mul i32 %1086, %875
  %1090 = add i32 %1089, %480
  %1091 = mul i32 %1090, %1088
  %1092 = or i32 %1091, 1
  %1093 = sext i32 %1092 to i64
  %1094 = getelementptr float, float* %1084, i64 %1093
  %1095 = load float, float* %1094, align 4
  %1096 = add i32 %1091, 2
  %1097 = insertelement <2 x i32> poison, i32 %1091, i64 0
  %1098 = insertelement <2 x i32> %1097, i32 %1096, i64 1
  %1099 = sext <2 x i32> %1098 to <2 x i64>
  %1100 = insertelement <2 x float*> poison, float* %1084, i64 0
  %1101 = shufflevector <2 x float*> %1100, <2 x float*> poison, <2 x i32> zeroinitializer
  %1102 = getelementptr float, <2 x float*> %1101, <2 x i64> %1099
  %1103 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1102, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1104 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %1105 = load float, float* %1104, align 4
  %1106 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1105, float 0x3F1A36E2E0000000)
  %1107 = extractelement <2 x float> %1103, i64 0
  %1108 = fdiv reassoc ninf nsz float %1107, %1106
  %1109 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %1110 = load float, float* %1109, align 4
  %1111 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1110, float 0x3F1A36E2E0000000)
  %1112 = fdiv reassoc ninf nsz float %1095, %1111
  %1113 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %1114 = load float, float* %1113, align 4
  %1115 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1114, float 0x3F1A36E2E0000000)
  %1116 = extractelement <2 x float> %1103, i64 1
  %1117 = fdiv reassoc ninf nsz float %1116, %1115
  %1118 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1112, float %1117)
  %1119 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1108, float %1118)
  %1120 = fcmp reassoc ninf nsz olt float %1119, 0x3FED70A3E0000000
  %1121 = fcmp reassoc ninf nsz ogt float %1095, 0x3EE4F8B580000000
  %.0408 = select i1 %1120, i1 %1121, i1 false
  br i1 %.0408, label %true_block247, label %true_block250

true_block247:                                    ; preds = %true_block241
  %1122 = insertelement <2 x float> poison, float %1095, i64 0
  %1123 = shufflevector <2 x float> %1122, <2 x float> poison, <2 x i32> zeroinitializer
  %1124 = fdiv reassoc ninf nsz <2 x float> %1103, %1123
  %1125 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1124, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1126 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1125, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1127 = fadd reassoc ninf nsz <2 x float> %1126, %1081
  %1128 = fadd reassoc ninf nsz float %.19.ph, 1.000000e+00
  br label %true_block250

true_block250:                                    ; preds = %true_block247, %true_block241, %true_block238
  %.20.ph = phi float [ %.19.ph, %true_block238 ], [ %.19.ph, %true_block241 ], [ %1128, %true_block247 ]
  %1129 = phi <2 x float> [ %1081, %true_block238 ], [ %1081, %true_block241 ], [ %1127, %true_block247 ]
  %1130 = icmp slt i32 %476, %886
  br i1 %1130, label %true_block253, label %true_block262

true_block253:                                    ; preds = %true_block250
  %1131 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %1132 = load float*, float** %1131, align 8
  %1133 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %1134 = load i32, i32* %1133, align 4
  %1135 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %1136 = load i32, i32* %1135, align 4
  %1137 = mul i32 %1134, %875
  %1138 = add i32 %1137, %476
  %1139 = mul i32 %1138, %1136
  %1140 = add i32 %1139, 1
  %1141 = sext i32 %1140 to i64
  %1142 = getelementptr float, float* %1132, i64 %1141
  %1143 = load float, float* %1142, align 4
  %1144 = add i32 %1139, 2
  %1145 = insertelement <2 x i32> poison, i32 %1139, i64 0
  %1146 = insertelement <2 x i32> %1145, i32 %1144, i64 1
  %1147 = sext <2 x i32> %1146 to <2 x i64>
  %1148 = insertelement <2 x float*> poison, float* %1132, i64 0
  %1149 = shufflevector <2 x float*> %1148, <2 x float*> poison, <2 x i32> zeroinitializer
  %1150 = getelementptr float, <2 x float*> %1149, <2 x i64> %1147
  %1151 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1150, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1152 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %1153 = load float, float* %1152, align 4
  %1154 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1153, float 0x3F1A36E2E0000000)
  %1155 = extractelement <2 x float> %1151, i64 0
  %1156 = fdiv reassoc ninf nsz float %1155, %1154
  %1157 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %1158 = load float, float* %1157, align 4
  %1159 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1158, float 0x3F1A36E2E0000000)
  %1160 = fdiv reassoc ninf nsz float %1143, %1159
  %1161 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %1162 = load float, float* %1161, align 4
  %1163 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1162, float 0x3F1A36E2E0000000)
  %1164 = extractelement <2 x float> %1151, i64 1
  %1165 = fdiv reassoc ninf nsz float %1164, %1163
  %1166 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1160, float %1165)
  %1167 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1156, float %1166)
  %1168 = fcmp reassoc ninf nsz olt float %1167, 0x3FED70A3E0000000
  %1169 = fcmp reassoc ninf nsz ogt float %1143, 0x3EE4F8B580000000
  %.0406 = select i1 %1168, i1 %1169, i1 false
  br i1 %.0406, label %true_block259, label %true_block262

true_block259:                                    ; preds = %true_block253
  %1170 = insertelement <2 x float> poison, float %1143, i64 0
  %1171 = shufflevector <2 x float> %1170, <2 x float> poison, <2 x i32> zeroinitializer
  %1172 = fdiv reassoc ninf nsz <2 x float> %1151, %1171
  %1173 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1172, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1174 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1173, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1175 = fadd reassoc ninf nsz <2 x float> %1174, %1129
  %1176 = fadd reassoc ninf nsz float %.20.ph, 1.000000e+00
  br label %true_block262

true_block262:                                    ; preds = %true_block259, %true_block253, %true_block250
  %.21.ph = phi float [ %.20.ph, %true_block250 ], [ %.20.ph, %true_block253 ], [ %1176, %true_block259 ]
  %1177 = phi <2 x float> [ %1129, %true_block250 ], [ %1129, %true_block253 ], [ %1175, %true_block259 ]
  %1178 = icmp slt i32 %481, %886
  br i1 %1178, label %true_block265, label %true_block274

true_block265:                                    ; preds = %true_block262
  %1179 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %1180 = load float*, float** %1179, align 8
  %1181 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %1182 = load i32, i32* %1181, align 4
  %1183 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %1184 = load i32, i32* %1183, align 4
  %1185 = mul i32 %1182, %875
  %1186 = add i32 %1185, %481
  %1187 = mul i32 %1186, %1184
  %1188 = or i32 %1187, 1
  %1189 = sext i32 %1188 to i64
  %1190 = getelementptr float, float* %1180, i64 %1189
  %1191 = load float, float* %1190, align 4
  %1192 = add i32 %1187, 2
  %1193 = insertelement <2 x i32> poison, i32 %1187, i64 0
  %1194 = insertelement <2 x i32> %1193, i32 %1192, i64 1
  %1195 = sext <2 x i32> %1194 to <2 x i64>
  %1196 = insertelement <2 x float*> poison, float* %1180, i64 0
  %1197 = shufflevector <2 x float*> %1196, <2 x float*> poison, <2 x i32> zeroinitializer
  %1198 = getelementptr float, <2 x float*> %1197, <2 x i64> %1195
  %1199 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1198, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1200 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %1201 = load float, float* %1200, align 4
  %1202 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1201, float 0x3F1A36E2E0000000)
  %1203 = extractelement <2 x float> %1199, i64 0
  %1204 = fdiv reassoc ninf nsz float %1203, %1202
  %1205 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %1206 = load float, float* %1205, align 4
  %1207 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1206, float 0x3F1A36E2E0000000)
  %1208 = fdiv reassoc ninf nsz float %1191, %1207
  %1209 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %1210 = load float, float* %1209, align 4
  %1211 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1210, float 0x3F1A36E2E0000000)
  %1212 = extractelement <2 x float> %1199, i64 1
  %1213 = fdiv reassoc ninf nsz float %1212, %1211
  %1214 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1208, float %1213)
  %1215 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1204, float %1214)
  %1216 = fcmp reassoc ninf nsz olt float %1215, 0x3FED70A3E0000000
  %1217 = fcmp reassoc ninf nsz ogt float %1191, 0x3EE4F8B580000000
  %.0404 = select i1 %1216, i1 %1217, i1 false
  br i1 %.0404, label %true_block271, label %true_block274

true_block271:                                    ; preds = %true_block265
  %1218 = insertelement <2 x float> poison, float %1191, i64 0
  %1219 = shufflevector <2 x float> %1218, <2 x float> poison, <2 x i32> zeroinitializer
  %1220 = fdiv reassoc ninf nsz <2 x float> %1199, %1219
  %1221 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1220, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1222 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1221, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1223 = fadd reassoc ninf nsz <2 x float> %1222, %1177
  %1224 = fadd reassoc ninf nsz float %.21.ph, 1.000000e+00
  br label %true_block274

true_block274:                                    ; preds = %true_block271, %true_block265, %true_block262
  %.22.ph = phi float [ %.21.ph, %true_block262 ], [ %.21.ph, %true_block265 ], [ %1224, %true_block271 ]
  %1225 = phi <2 x float> [ %1177, %true_block262 ], [ %1177, %true_block265 ], [ %1223, %true_block271 ]
  %1226 = icmp slt i32 %475, %886
  br i1 %1226, label %true_block277, label %after_if279

true_block277:                                    ; preds = %true_block274
  %1227 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 1
  %1228 = load float*, float** %1227, align 8
  %1229 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 1
  %1230 = load i32, i32* %1229, align 4
  %1231 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 0, i32 0, i32 2
  %1232 = load i32, i32* %1231, align 4
  %1233 = mul i32 %1230, %875
  %1234 = add i32 %1233, %475
  %1235 = mul i32 %1234, %1232
  %1236 = add i32 %1235, 1
  %1237 = sext i32 %1236 to i64
  %1238 = getelementptr float, float* %1228, i64 %1237
  %1239 = load float, float* %1238, align 4
  %1240 = add i32 %1235, 2
  %1241 = insertelement <2 x i32> poison, i32 %1235, i64 0
  %1242 = insertelement <2 x i32> %1241, i32 %1240, i64 1
  %1243 = sext <2 x i32> %1242 to <2 x i64>
  %1244 = insertelement <2 x float*> poison, float* %1228, i64 0
  %1245 = shufflevector <2 x float*> %1244, <2 x float*> poison, <2 x i32> zeroinitializer
  %1246 = getelementptr float, <2 x float*> %1245, <2 x i64> %1243
  %1247 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1246, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1248 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 2
  %1249 = load float, float* %1248, align 4
  %1250 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1249, float 0x3F1A36E2E0000000)
  %1251 = extractelement <2 x float> %1247, i64 0
  %1252 = fdiv reassoc ninf nsz float %1251, %1250
  %1253 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 3
  %1254 = load float, float* %1253, align 4
  %1255 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1254, float 0x3F1A36E2E0000000)
  %1256 = fdiv reassoc ninf nsz float %1239, %1255
  %1257 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %884, i64 0, i32 4
  %1258 = load float, float* %1257, align 4
  %1259 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1258, float 0x3F1A36E2E0000000)
  %1260 = extractelement <2 x float> %1247, i64 1
  %1261 = fdiv reassoc ninf nsz float %1260, %1259
  %1262 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1256, float %1261)
  %1263 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1252, float %1262)
  %1264 = fcmp reassoc ninf nsz olt float %1263, 0x3FED70A3E0000000
  %1265 = fcmp reassoc ninf nsz ogt float %1239, 0x3EE4F8B580000000
  %.0402 = select i1 %1264, i1 %1265, i1 false
  br i1 %.0402, label %true_block283, label %after_if279

after_if279:                                      ; preds = %true_block283, %true_block277, %true_block274, %after_if183
  %.23 = phi float [ %1275, %true_block283 ], [ %.22.ph, %true_block277 ], [ %.22.ph, %true_block274 ], [ %.15, %after_if183 ]
  %1266 = phi <2 x float> [ %1274, %true_block283 ], [ %1225, %true_block277 ], [ %1225, %true_block274 ], [ %874, %after_if183 ]
  %1267 = or i32 %47, 3
  %1268 = icmp slt i32 %1267, %23
  br i1 %1268, label %true_block286, label %after_if375

true_block283:                                    ; preds = %true_block277
  %1269 = insertelement <2 x float> poison, float %1239, i64 0
  %1270 = shufflevector <2 x float> %1269, <2 x float> poison, <2 x i32> zeroinitializer
  %1271 = fdiv reassoc ninf nsz <2 x float> %1247, %1270
  %1272 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1271, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1273 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1272, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1274 = fadd reassoc ninf nsz <2 x float> %1273, %1225
  %1275 = fadd reassoc ninf nsz float %.22.ph, 1.000000e+00
  br label %after_if279

true_block286:                                    ; preds = %after_if279
  %1276 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %1277 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 6
  %1278 = load i32, i32* %1277, align 4
  %1279 = icmp slt i32 %52, %1278
  br i1 %1279, label %true_block289, label %true_block298

true_block289:                                    ; preds = %true_block286
  %1280 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1281 = load float*, float** %1280, align 8
  %1282 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1283 = load i32, i32* %1282, align 4
  %1284 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1285 = load i32, i32* %1284, align 4
  %1286 = mul i32 %1283, %1267
  %1287 = shl i32 %35, 3
  %1288 = mul i32 %1287, %44
  %1289 = sub i32 %1286, %1288
  %1290 = add i32 %lsr.iv, %1289
  %1291 = add i32 %1290, -7
  %1292 = mul i32 %1291, %1285
  %1293 = sext i32 %1292 to i64
  %1294 = getelementptr float, float* %1281, i64 %1293
  %1295 = load float, float* %1294, align 4
  %1296 = add i32 %1292, 1
  %1297 = sext i32 %1296 to i64
  %1298 = getelementptr float, float* %1281, i64 %1297
  %1299 = load float, float* %1298, align 4
  %1300 = add i32 %1292, 2
  %1301 = sext i32 %1300 to i64
  %1302 = getelementptr float, float* %1281, i64 %1301
  %1303 = load float, float* %1302, align 4
  %1304 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1305 = load float, float* %1304, align 4
  %1306 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1305, float 0x3F1A36E2E0000000)
  %1307 = fdiv reassoc ninf nsz float %1295, %1306
  %1308 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1309 = load float, float* %1308, align 4
  %1310 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1309, float 0x3F1A36E2E0000000)
  %1311 = fdiv reassoc ninf nsz float %1299, %1310
  %1312 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1313 = load float, float* %1312, align 4
  %1314 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1313, float 0x3F1A36E2E0000000)
  %1315 = fdiv reassoc ninf nsz float %1303, %1314
  %1316 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1311, float %1315)
  %1317 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1307, float %1316)
  %1318 = fcmp reassoc ninf nsz olt float %1317, 0x3FED70A3E0000000
  %1319 = fcmp reassoc ninf nsz ogt float %1299, 0x3EE4F8B580000000
  %.0400 = select i1 %1318, i1 %1319, i1 false
  br i1 %.0400, label %true_block295, label %true_block298

true_block295:                                    ; preds = %true_block289
  %1320 = insertelement <2 x float> poison, float %1295, i64 0
  %1321 = insertelement <2 x float> %1320, float %1303, i64 1
  %1322 = insertelement <2 x float> poison, float %1299, i64 0
  %1323 = shufflevector <2 x float> %1322, <2 x float> poison, <2 x i32> zeroinitializer
  %1324 = fdiv reassoc ninf nsz <2 x float> %1321, %1323
  %1325 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1324, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1326 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1325, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1327 = fadd reassoc ninf nsz <2 x float> %1326, %1266
  %1328 = fadd reassoc ninf nsz float %.23, 1.000000e+00
  br label %true_block298

true_block298:                                    ; preds = %true_block295, %true_block289, %true_block286
  %.24.ph = phi float [ %.23, %true_block286 ], [ %.23, %true_block289 ], [ %1328, %true_block295 ]
  %1329 = phi <2 x float> [ %1266, %true_block286 ], [ %1266, %true_block289 ], [ %1327, %true_block295 ]
  %1330 = icmp slt i32 %478, %1278
  br i1 %1330, label %true_block301, label %true_block310

true_block301:                                    ; preds = %true_block298
  %1331 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1332 = load float*, float** %1331, align 8
  %1333 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1334 = load i32, i32* %1333, align 4
  %1335 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1336 = load i32, i32* %1335, align 4
  %1337 = mul i32 %1334, %1267
  %1338 = add i32 %1337, %478
  %1339 = mul i32 %1338, %1336
  %1340 = sext i32 %1339 to i64
  %1341 = getelementptr float, float* %1332, i64 %1340
  %1342 = add i32 %1339, 1
  %1343 = sext i32 %1342 to i64
  %1344 = getelementptr float, float* %1332, i64 %1343
  %1345 = load float, float* %1344, align 4
  %1346 = add i32 %1339, 2
  %1347 = sext i32 %1346 to i64
  %1348 = getelementptr float, float* %1332, i64 %1347
  %1349 = insertelement <2 x float*> poison, float* %1341, i64 0
  %1350 = insertelement <2 x float*> %1349, float* %1348, i64 1
  %1351 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1350, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1352 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1353 = load float, float* %1352, align 4
  %1354 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1353, float 0x3F1A36E2E0000000)
  %1355 = extractelement <2 x float> %1351, i64 0
  %1356 = fdiv reassoc ninf nsz float %1355, %1354
  %1357 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1358 = load float, float* %1357, align 4
  %1359 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1358, float 0x3F1A36E2E0000000)
  %1360 = fdiv reassoc ninf nsz float %1345, %1359
  %1361 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1362 = load float, float* %1361, align 4
  %1363 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1362, float 0x3F1A36E2E0000000)
  %1364 = extractelement <2 x float> %1351, i64 1
  %1365 = fdiv reassoc ninf nsz float %1364, %1363
  %1366 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1360, float %1365)
  %1367 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1356, float %1366)
  %1368 = fcmp reassoc ninf nsz olt float %1367, 0x3FED70A3E0000000
  %1369 = fcmp reassoc ninf nsz ogt float %1345, 0x3EE4F8B580000000
  %.0398 = select i1 %1368, i1 %1369, i1 false
  br i1 %.0398, label %true_block307, label %true_block310

true_block307:                                    ; preds = %true_block301
  %1370 = insertelement <2 x float> poison, float %1345, i64 0
  %1371 = shufflevector <2 x float> %1370, <2 x float> poison, <2 x i32> zeroinitializer
  %1372 = fdiv reassoc ninf nsz <2 x float> %1351, %1371
  %1373 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1372, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1374 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1373, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1375 = fadd reassoc ninf nsz <2 x float> %1374, %1329
  %1376 = fadd reassoc ninf nsz float %.24.ph, 1.000000e+00
  br label %true_block310

true_block310:                                    ; preds = %true_block307, %true_block301, %true_block298
  %.25.ph = phi float [ %.24.ph, %true_block298 ], [ %.24.ph, %true_block301 ], [ %1376, %true_block307 ]
  %1377 = phi <2 x float> [ %1329, %true_block298 ], [ %1329, %true_block301 ], [ %1375, %true_block307 ]
  %1378 = icmp slt i32 %479, %1278
  br i1 %1378, label %true_block313, label %true_block322

true_block313:                                    ; preds = %true_block310
  %1379 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1380 = load float*, float** %1379, align 8
  %1381 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1382 = load i32, i32* %1381, align 4
  %1383 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1384 = load i32, i32* %1383, align 4
  %1385 = mul i32 %1382, %1267
  %1386 = add i32 %1385, %479
  %1387 = mul i32 %1386, %1384
  %1388 = add i32 %1387, 1
  %1389 = sext i32 %1388 to i64
  %1390 = getelementptr float, float* %1380, i64 %1389
  %1391 = load float, float* %1390, align 4
  %1392 = add i32 %1387, 2
  %1393 = insertelement <2 x i32> poison, i32 %1387, i64 0
  %1394 = insertelement <2 x i32> %1393, i32 %1392, i64 1
  %1395 = sext <2 x i32> %1394 to <2 x i64>
  %1396 = insertelement <2 x float*> poison, float* %1380, i64 0
  %1397 = shufflevector <2 x float*> %1396, <2 x float*> poison, <2 x i32> zeroinitializer
  %1398 = getelementptr float, <2 x float*> %1397, <2 x i64> %1395
  %1399 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1398, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1400 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1401 = load float, float* %1400, align 4
  %1402 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1401, float 0x3F1A36E2E0000000)
  %1403 = extractelement <2 x float> %1399, i64 0
  %1404 = fdiv reassoc ninf nsz float %1403, %1402
  %1405 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1406 = load float, float* %1405, align 4
  %1407 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1406, float 0x3F1A36E2E0000000)
  %1408 = fdiv reassoc ninf nsz float %1391, %1407
  %1409 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1410 = load float, float* %1409, align 4
  %1411 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1410, float 0x3F1A36E2E0000000)
  %1412 = extractelement <2 x float> %1399, i64 1
  %1413 = fdiv reassoc ninf nsz float %1412, %1411
  %1414 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1408, float %1413)
  %1415 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1404, float %1414)
  %1416 = fcmp reassoc ninf nsz olt float %1415, 0x3FED70A3E0000000
  %1417 = fcmp reassoc ninf nsz ogt float %1391, 0x3EE4F8B580000000
  %.0396 = select i1 %1416, i1 %1417, i1 false
  br i1 %.0396, label %true_block319, label %true_block322

true_block319:                                    ; preds = %true_block313
  %1418 = insertelement <2 x float> poison, float %1391, i64 0
  %1419 = shufflevector <2 x float> %1418, <2 x float> poison, <2 x i32> zeroinitializer
  %1420 = fdiv reassoc ninf nsz <2 x float> %1399, %1419
  %1421 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1420, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1422 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1421, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1423 = fadd reassoc ninf nsz <2 x float> %1422, %1377
  %1424 = fadd reassoc ninf nsz float %.25.ph, 1.000000e+00
  br label %true_block322

true_block322:                                    ; preds = %true_block319, %true_block313, %true_block310
  %.26.ph = phi float [ %.25.ph, %true_block310 ], [ %.25.ph, %true_block313 ], [ %1424, %true_block319 ]
  %1425 = phi <2 x float> [ %1377, %true_block310 ], [ %1377, %true_block313 ], [ %1423, %true_block319 ]
  %1426 = icmp slt i32 %477, %1278
  br i1 %1426, label %true_block325, label %true_block334

true_block325:                                    ; preds = %true_block322
  %1427 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1428 = load float*, float** %1427, align 8
  %1429 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1430 = load i32, i32* %1429, align 4
  %1431 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1432 = load i32, i32* %1431, align 4
  %1433 = mul i32 %1430, %1267
  %1434 = add i32 %1433, %477
  %1435 = mul i32 %1434, %1432
  %1436 = add i32 %1435, 1
  %1437 = sext i32 %1436 to i64
  %1438 = getelementptr float, float* %1428, i64 %1437
  %1439 = load float, float* %1438, align 4
  %1440 = add i32 %1435, 2
  %1441 = insertelement <2 x i32> poison, i32 %1435, i64 0
  %1442 = insertelement <2 x i32> %1441, i32 %1440, i64 1
  %1443 = sext <2 x i32> %1442 to <2 x i64>
  %1444 = insertelement <2 x float*> poison, float* %1428, i64 0
  %1445 = shufflevector <2 x float*> %1444, <2 x float*> poison, <2 x i32> zeroinitializer
  %1446 = getelementptr float, <2 x float*> %1445, <2 x i64> %1443
  %1447 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1446, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1448 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1449 = load float, float* %1448, align 4
  %1450 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1449, float 0x3F1A36E2E0000000)
  %1451 = extractelement <2 x float> %1447, i64 0
  %1452 = fdiv reassoc ninf nsz float %1451, %1450
  %1453 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1454 = load float, float* %1453, align 4
  %1455 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1454, float 0x3F1A36E2E0000000)
  %1456 = fdiv reassoc ninf nsz float %1439, %1455
  %1457 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1458 = load float, float* %1457, align 4
  %1459 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1458, float 0x3F1A36E2E0000000)
  %1460 = extractelement <2 x float> %1447, i64 1
  %1461 = fdiv reassoc ninf nsz float %1460, %1459
  %1462 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1456, float %1461)
  %1463 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1452, float %1462)
  %1464 = fcmp reassoc ninf nsz olt float %1463, 0x3FED70A3E0000000
  %1465 = fcmp reassoc ninf nsz ogt float %1439, 0x3EE4F8B580000000
  %.0394 = select i1 %1464, i1 %1465, i1 false
  br i1 %.0394, label %true_block331, label %true_block334

true_block331:                                    ; preds = %true_block325
  %1466 = insertelement <2 x float> poison, float %1439, i64 0
  %1467 = shufflevector <2 x float> %1466, <2 x float> poison, <2 x i32> zeroinitializer
  %1468 = fdiv reassoc ninf nsz <2 x float> %1447, %1467
  %1469 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1468, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1470 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1469, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1471 = fadd reassoc ninf nsz <2 x float> %1470, %1425
  %1472 = fadd reassoc ninf nsz float %.26.ph, 1.000000e+00
  br label %true_block334

true_block334:                                    ; preds = %true_block331, %true_block325, %true_block322
  %.27.ph = phi float [ %.26.ph, %true_block322 ], [ %.26.ph, %true_block325 ], [ %1472, %true_block331 ]
  %1473 = phi <2 x float> [ %1425, %true_block322 ], [ %1425, %true_block325 ], [ %1471, %true_block331 ]
  %1474 = icmp slt i32 %480, %1278
  br i1 %1474, label %true_block337, label %true_block346

true_block337:                                    ; preds = %true_block334
  %1475 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1476 = load float*, float** %1475, align 8
  %1477 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1478 = load i32, i32* %1477, align 4
  %1479 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1480 = load i32, i32* %1479, align 4
  %1481 = mul i32 %1478, %1267
  %1482 = add i32 %1481, %480
  %1483 = mul i32 %1482, %1480
  %1484 = add i32 %1483, 1
  %1485 = sext i32 %1484 to i64
  %1486 = getelementptr float, float* %1476, i64 %1485
  %1487 = load float, float* %1486, align 4
  %1488 = add i32 %1483, 2
  %1489 = insertelement <2 x i32> poison, i32 %1483, i64 0
  %1490 = insertelement <2 x i32> %1489, i32 %1488, i64 1
  %1491 = sext <2 x i32> %1490 to <2 x i64>
  %1492 = insertelement <2 x float*> poison, float* %1476, i64 0
  %1493 = shufflevector <2 x float*> %1492, <2 x float*> poison, <2 x i32> zeroinitializer
  %1494 = getelementptr float, <2 x float*> %1493, <2 x i64> %1491
  %1495 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1494, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1496 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1497 = load float, float* %1496, align 4
  %1498 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1497, float 0x3F1A36E2E0000000)
  %1499 = extractelement <2 x float> %1495, i64 0
  %1500 = fdiv reassoc ninf nsz float %1499, %1498
  %1501 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1502 = load float, float* %1501, align 4
  %1503 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1502, float 0x3F1A36E2E0000000)
  %1504 = fdiv reassoc ninf nsz float %1487, %1503
  %1505 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1506 = load float, float* %1505, align 4
  %1507 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1506, float 0x3F1A36E2E0000000)
  %1508 = extractelement <2 x float> %1495, i64 1
  %1509 = fdiv reassoc ninf nsz float %1508, %1507
  %1510 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1504, float %1509)
  %1511 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1500, float %1510)
  %1512 = fcmp reassoc ninf nsz olt float %1511, 0x3FED70A3E0000000
  %1513 = fcmp reassoc ninf nsz ogt float %1487, 0x3EE4F8B580000000
  %.0392 = select i1 %1512, i1 %1513, i1 false
  br i1 %.0392, label %true_block343, label %true_block346

true_block343:                                    ; preds = %true_block337
  %1514 = insertelement <2 x float> poison, float %1487, i64 0
  %1515 = shufflevector <2 x float> %1514, <2 x float> poison, <2 x i32> zeroinitializer
  %1516 = fdiv reassoc ninf nsz <2 x float> %1495, %1515
  %1517 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1516, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1518 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1517, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1519 = fadd reassoc ninf nsz <2 x float> %1518, %1473
  %1520 = fadd reassoc ninf nsz float %.27.ph, 1.000000e+00
  br label %true_block346

true_block346:                                    ; preds = %true_block343, %true_block337, %true_block334
  %.28.ph = phi float [ %.27.ph, %true_block334 ], [ %.27.ph, %true_block337 ], [ %1520, %true_block343 ]
  %1521 = phi <2 x float> [ %1473, %true_block334 ], [ %1473, %true_block337 ], [ %1519, %true_block343 ]
  %1522 = icmp slt i32 %476, %1278
  br i1 %1522, label %true_block349, label %true_block358

true_block349:                                    ; preds = %true_block346
  %1523 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1524 = load float*, float** %1523, align 8
  %1525 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1526 = load i32, i32* %1525, align 4
  %1527 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1528 = load i32, i32* %1527, align 4
  %1529 = mul i32 %1526, %1267
  %1530 = add i32 %1529, %476
  %1531 = mul i32 %1530, %1528
  %1532 = add i32 %1531, 1
  %1533 = sext i32 %1532 to i64
  %1534 = getelementptr float, float* %1524, i64 %1533
  %1535 = load float, float* %1534, align 4
  %1536 = add i32 %1531, 2
  %1537 = insertelement <2 x i32> poison, i32 %1531, i64 0
  %1538 = insertelement <2 x i32> %1537, i32 %1536, i64 1
  %1539 = sext <2 x i32> %1538 to <2 x i64>
  %1540 = insertelement <2 x float*> poison, float* %1524, i64 0
  %1541 = shufflevector <2 x float*> %1540, <2 x float*> poison, <2 x i32> zeroinitializer
  %1542 = getelementptr float, <2 x float*> %1541, <2 x i64> %1539
  %1543 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1542, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1544 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1545 = load float, float* %1544, align 4
  %1546 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1545, float 0x3F1A36E2E0000000)
  %1547 = extractelement <2 x float> %1543, i64 0
  %1548 = fdiv reassoc ninf nsz float %1547, %1546
  %1549 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1550 = load float, float* %1549, align 4
  %1551 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1550, float 0x3F1A36E2E0000000)
  %1552 = fdiv reassoc ninf nsz float %1535, %1551
  %1553 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1554 = load float, float* %1553, align 4
  %1555 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1554, float 0x3F1A36E2E0000000)
  %1556 = extractelement <2 x float> %1543, i64 1
  %1557 = fdiv reassoc ninf nsz float %1556, %1555
  %1558 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1552, float %1557)
  %1559 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1548, float %1558)
  %1560 = fcmp reassoc ninf nsz olt float %1559, 0x3FED70A3E0000000
  %1561 = fcmp reassoc ninf nsz ogt float %1535, 0x3EE4F8B580000000
  %.0390 = select i1 %1560, i1 %1561, i1 false
  br i1 %.0390, label %true_block355, label %true_block358

true_block355:                                    ; preds = %true_block349
  %1562 = insertelement <2 x float> poison, float %1535, i64 0
  %1563 = shufflevector <2 x float> %1562, <2 x float> poison, <2 x i32> zeroinitializer
  %1564 = fdiv reassoc ninf nsz <2 x float> %1543, %1563
  %1565 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1564, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1566 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1565, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1567 = fadd reassoc ninf nsz <2 x float> %1566, %1521
  %1568 = fadd reassoc ninf nsz float %.28.ph, 1.000000e+00
  br label %true_block358

true_block358:                                    ; preds = %true_block355, %true_block349, %true_block346
  %.29.ph = phi float [ %.28.ph, %true_block346 ], [ %.28.ph, %true_block349 ], [ %1568, %true_block355 ]
  %1569 = phi <2 x float> [ %1521, %true_block346 ], [ %1521, %true_block349 ], [ %1567, %true_block355 ]
  %1570 = icmp slt i32 %481, %1278
  br i1 %1570, label %true_block361, label %true_block370

true_block361:                                    ; preds = %true_block358
  %1571 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1572 = load float*, float** %1571, align 8
  %1573 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1574 = load i32, i32* %1573, align 4
  %1575 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1576 = load i32, i32* %1575, align 4
  %1577 = mul i32 %1574, %1267
  %1578 = add i32 %1577, %481
  %1579 = mul i32 %1578, %1576
  %1580 = add i32 %1579, 1
  %1581 = sext i32 %1580 to i64
  %1582 = getelementptr float, float* %1572, i64 %1581
  %1583 = load float, float* %1582, align 4
  %1584 = add i32 %1579, 2
  %1585 = insertelement <2 x i32> poison, i32 %1579, i64 0
  %1586 = insertelement <2 x i32> %1585, i32 %1584, i64 1
  %1587 = sext <2 x i32> %1586 to <2 x i64>
  %1588 = insertelement <2 x float*> poison, float* %1572, i64 0
  %1589 = shufflevector <2 x float*> %1588, <2 x float*> poison, <2 x i32> zeroinitializer
  %1590 = getelementptr float, <2 x float*> %1589, <2 x i64> %1587
  %1591 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1590, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1592 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1593 = load float, float* %1592, align 4
  %1594 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1593, float 0x3F1A36E2E0000000)
  %1595 = extractelement <2 x float> %1591, i64 0
  %1596 = fdiv reassoc ninf nsz float %1595, %1594
  %1597 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1598 = load float, float* %1597, align 4
  %1599 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1598, float 0x3F1A36E2E0000000)
  %1600 = fdiv reassoc ninf nsz float %1583, %1599
  %1601 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1602 = load float, float* %1601, align 4
  %1603 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1602, float 0x3F1A36E2E0000000)
  %1604 = extractelement <2 x float> %1591, i64 1
  %1605 = fdiv reassoc ninf nsz float %1604, %1603
  %1606 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1600, float %1605)
  %1607 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1596, float %1606)
  %1608 = fcmp reassoc ninf nsz olt float %1607, 0x3FED70A3E0000000
  %1609 = fcmp reassoc ninf nsz ogt float %1583, 0x3EE4F8B580000000
  %.0388 = select i1 %1608, i1 %1609, i1 false
  br i1 %.0388, label %true_block367, label %true_block370

true_block367:                                    ; preds = %true_block361
  %1610 = insertelement <2 x float> poison, float %1583, i64 0
  %1611 = shufflevector <2 x float> %1610, <2 x float> poison, <2 x i32> zeroinitializer
  %1612 = fdiv reassoc ninf nsz <2 x float> %1591, %1611
  %1613 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1612, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1614 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1613, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1615 = fadd reassoc ninf nsz <2 x float> %1614, %1569
  %1616 = fadd reassoc ninf nsz float %.29.ph, 1.000000e+00
  br label %true_block370

true_block370:                                    ; preds = %true_block367, %true_block361, %true_block358
  %.30.ph = phi float [ %.29.ph, %true_block358 ], [ %.29.ph, %true_block361 ], [ %1616, %true_block367 ]
  %1617 = phi <2 x float> [ %1569, %true_block358 ], [ %1569, %true_block361 ], [ %1615, %true_block367 ]
  %1618 = icmp slt i32 %475, %1278
  br i1 %1618, label %true_block373, label %after_if375

true_block373:                                    ; preds = %true_block370
  %1619 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 1
  %1620 = load float*, float** %1619, align 8
  %1621 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 1
  %1622 = load i32, i32* %1621, align 4
  %1623 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 0, i32 0, i32 2
  %1624 = load i32, i32* %1623, align 4
  %1625 = mul i32 %1622, %1267
  %1626 = add i32 %1625, %475
  %1627 = mul i32 %1626, %1624
  %1628 = add i32 %1627, 1
  %1629 = sext i32 %1628 to i64
  %1630 = getelementptr float, float* %1620, i64 %1629
  %1631 = load float, float* %1630, align 4
  %1632 = add i32 %1627, 2
  %1633 = insertelement <2 x i32> poison, i32 %1627, i64 0
  %1634 = insertelement <2 x i32> %1633, i32 %1632, i64 1
  %1635 = sext <2 x i32> %1634 to <2 x i64>
  %1636 = insertelement <2 x float*> poison, float* %1620, i64 0
  %1637 = shufflevector <2 x float*> %1636, <2 x float*> poison, <2 x i32> zeroinitializer
  %1638 = getelementptr float, <2 x float*> %1637, <2 x i64> %1635
  %1639 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1638, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1640 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 2
  %1641 = load float, float* %1640, align 4
  %1642 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1641, float 0x3F1A36E2E0000000)
  %1643 = extractelement <2 x float> %1639, i64 0
  %1644 = fdiv reassoc ninf nsz float %1643, %1642
  %1645 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 3
  %1646 = load float, float* %1645, align 4
  %1647 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1646, float 0x3F1A36E2E0000000)
  %1648 = fdiv reassoc ninf nsz float %1631, %1647
  %1649 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1276, i64 0, i32 4
  %1650 = load float, float* %1649, align 4
  %1651 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1650, float 0x3F1A36E2E0000000)
  %1652 = extractelement <2 x float> %1639, i64 1
  %1653 = fdiv reassoc ninf nsz float %1652, %1651
  %1654 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1648, float %1653)
  %1655 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1644, float %1654)
  %1656 = fcmp reassoc ninf nsz olt float %1655, 0x3FED70A3E0000000
  %1657 = fcmp reassoc ninf nsz ogt float %1631, 0x3EE4F8B580000000
  %.0386 = select i1 %1656, i1 %1657, i1 false
  br i1 %.0386, label %true_block379, label %after_if375

after_if375:                                      ; preds = %true_block379, %true_block373, %true_block370, %after_if279
  %.31 = phi float [ %1667, %true_block379 ], [ %.30.ph, %true_block373 ], [ %.30.ph, %true_block370 ], [ %.23, %after_if279 ]
  %1658 = phi <2 x float> [ %1666, %true_block379 ], [ %1617, %true_block373 ], [ %1617, %true_block370 ], [ %1266, %after_if279 ]
  %1659 = or i32 %47, 4
  %1660 = icmp slt i32 %1659, %23
  br i1 %1660, label %true_block382, label %after_if471

true_block379:                                    ; preds = %true_block373
  %1661 = insertelement <2 x float> poison, float %1631, i64 0
  %1662 = shufflevector <2 x float> %1661, <2 x float> poison, <2 x i32> zeroinitializer
  %1663 = fdiv reassoc ninf nsz <2 x float> %1639, %1662
  %1664 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1663, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1665 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1664, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1666 = fadd reassoc ninf nsz <2 x float> %1665, %1617
  %1667 = fadd reassoc ninf nsz float %.30.ph, 1.000000e+00
  br label %after_if375

true_block382:                                    ; preds = %after_if375
  %1668 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %1669 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 6
  %1670 = load i32, i32* %1669, align 4
  %1671 = icmp slt i32 %52, %1670
  br i1 %1671, label %true_block385, label %true_block394

true_block385:                                    ; preds = %true_block382
  %1672 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %1673 = load float*, float** %1672, align 8
  %1674 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %1675 = load i32, i32* %1674, align 4
  %1676 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %1677 = load i32, i32* %1676, align 4
  %1678 = mul i32 %1675, %1659
  %1679 = shl i32 %35, 3
  %1680 = mul i32 %1679, %44
  %1681 = sub i32 %1678, %1680
  %1682 = add i32 %lsr.iv, %1681
  %1683 = add i32 %1682, -7
  %1684 = mul i32 %1683, %1677
  %1685 = or i32 %1684, 1
  %1686 = sext i32 %1685 to i64
  %1687 = getelementptr float, float* %1673, i64 %1686
  %1688 = load float, float* %1687, align 4
  %1689 = or i32 %1684, 2
  %1690 = insertelement <2 x i32> poison, i32 %1684, i64 0
  %1691 = insertelement <2 x i32> %1690, i32 %1689, i64 1
  %1692 = sext <2 x i32> %1691 to <2 x i64>
  %1693 = insertelement <2 x float*> poison, float* %1673, i64 0
  %1694 = shufflevector <2 x float*> %1693, <2 x float*> poison, <2 x i32> zeroinitializer
  %1695 = getelementptr float, <2 x float*> %1694, <2 x i64> %1692
  %1696 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1695, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1697 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %1698 = load float, float* %1697, align 4
  %1699 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1698, float 0x3F1A36E2E0000000)
  %1700 = extractelement <2 x float> %1696, i64 0
  %1701 = fdiv reassoc ninf nsz float %1700, %1699
  %1702 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %1703 = load float, float* %1702, align 4
  %1704 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1703, float 0x3F1A36E2E0000000)
  %1705 = fdiv reassoc ninf nsz float %1688, %1704
  %1706 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %1707 = load float, float* %1706, align 4
  %1708 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1707, float 0x3F1A36E2E0000000)
  %1709 = extractelement <2 x float> %1696, i64 1
  %1710 = fdiv reassoc ninf nsz float %1709, %1708
  %1711 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1705, float %1710)
  %1712 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1701, float %1711)
  %1713 = fcmp reassoc ninf nsz olt float %1712, 0x3FED70A3E0000000
  %1714 = fcmp reassoc ninf nsz ogt float %1688, 0x3EE4F8B580000000
  %.0384 = select i1 %1713, i1 %1714, i1 false
  br i1 %.0384, label %true_block391, label %true_block394

true_block391:                                    ; preds = %true_block385
  %1715 = insertelement <2 x float> poison, float %1688, i64 0
  %1716 = shufflevector <2 x float> %1715, <2 x float> poison, <2 x i32> zeroinitializer
  %1717 = fdiv reassoc ninf nsz <2 x float> %1696, %1716
  %1718 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1717, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1719 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1718, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1720 = fadd reassoc ninf nsz <2 x float> %1719, %1658
  %1721 = fadd reassoc ninf nsz float %.31, 1.000000e+00
  br label %true_block394

true_block394:                                    ; preds = %true_block391, %true_block385, %true_block382
  %.32.ph = phi float [ %.31, %true_block382 ], [ %.31, %true_block385 ], [ %1721, %true_block391 ]
  %1722 = phi <2 x float> [ %1658, %true_block382 ], [ %1658, %true_block385 ], [ %1720, %true_block391 ]
  %1723 = icmp slt i32 %478, %1670
  br i1 %1723, label %true_block397, label %true_block406

true_block397:                                    ; preds = %true_block394
  %1724 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %1725 = load float*, float** %1724, align 8
  %1726 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %1727 = load i32, i32* %1726, align 4
  %1728 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %1729 = load i32, i32* %1728, align 4
  %1730 = mul i32 %1727, %1659
  %1731 = add i32 %1730, %478
  %1732 = mul i32 %1731, %1729
  %1733 = sext i32 %1732 to i64
  %1734 = getelementptr float, float* %1725, i64 %1733
  %1735 = load float, float* %1734, align 4
  %1736 = add i32 %1732, 1
  %1737 = sext i32 %1736 to i64
  %1738 = getelementptr float, float* %1725, i64 %1737
  %1739 = load float, float* %1738, align 4
  %1740 = add i32 %1732, 2
  %1741 = sext i32 %1740 to i64
  %1742 = getelementptr float, float* %1725, i64 %1741
  %1743 = load float, float* %1742, align 4
  %1744 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %1745 = load float, float* %1744, align 4
  %1746 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1745, float 0x3F1A36E2E0000000)
  %1747 = fdiv reassoc ninf nsz float %1735, %1746
  %1748 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %1749 = load float, float* %1748, align 4
  %1750 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1749, float 0x3F1A36E2E0000000)
  %1751 = fdiv reassoc ninf nsz float %1739, %1750
  %1752 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %1753 = load float, float* %1752, align 4
  %1754 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1753, float 0x3F1A36E2E0000000)
  %1755 = fdiv reassoc ninf nsz float %1743, %1754
  %1756 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1751, float %1755)
  %1757 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1747, float %1756)
  %1758 = fcmp reassoc ninf nsz olt float %1757, 0x3FED70A3E0000000
  %1759 = fcmp reassoc ninf nsz ogt float %1739, 0x3EE4F8B580000000
  %.0382 = select i1 %1758, i1 %1759, i1 false
  br i1 %.0382, label %true_block403, label %true_block406

true_block403:                                    ; preds = %true_block397
  %1760 = insertelement <2 x float> poison, float %1735, i64 0
  %1761 = insertelement <2 x float> %1760, float %1743, i64 1
  %1762 = insertelement <2 x float> poison, float %1739, i64 0
  %1763 = shufflevector <2 x float> %1762, <2 x float> poison, <2 x i32> zeroinitializer
  %1764 = fdiv reassoc ninf nsz <2 x float> %1761, %1763
  %1765 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1764, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1766 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1765, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1767 = fadd reassoc ninf nsz <2 x float> %1766, %1722
  %1768 = fadd reassoc ninf nsz float %.32.ph, 1.000000e+00
  br label %true_block406

true_block406:                                    ; preds = %true_block403, %true_block397, %true_block394
  %.33.ph = phi float [ %.32.ph, %true_block394 ], [ %.32.ph, %true_block397 ], [ %1768, %true_block403 ]
  %1769 = phi <2 x float> [ %1722, %true_block394 ], [ %1722, %true_block397 ], [ %1767, %true_block403 ]
  %1770 = icmp slt i32 %479, %1670
  br i1 %1770, label %true_block409, label %true_block418

true_block409:                                    ; preds = %true_block406
  %1771 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %1772 = load float*, float** %1771, align 8
  %1773 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %1774 = load i32, i32* %1773, align 4
  %1775 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %1776 = load i32, i32* %1775, align 4
  %1777 = mul i32 %1774, %1659
  %1778 = add i32 %1777, %479
  %1779 = mul i32 %1778, %1776
  %1780 = sext i32 %1779 to i64
  %1781 = getelementptr float, float* %1772, i64 %1780
  %1782 = or i32 %1779, 1
  %1783 = sext i32 %1782 to i64
  %1784 = getelementptr float, float* %1772, i64 %1783
  %1785 = load float, float* %1784, align 4
  %1786 = add i32 %1779, 2
  %1787 = sext i32 %1786 to i64
  %1788 = getelementptr float, float* %1772, i64 %1787
  %1789 = insertelement <2 x float*> poison, float* %1781, i64 0
  %1790 = insertelement <2 x float*> %1789, float* %1788, i64 1
  %1791 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1790, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1792 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %1793 = load float, float* %1792, align 4
  %1794 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1793, float 0x3F1A36E2E0000000)
  %1795 = extractelement <2 x float> %1791, i64 0
  %1796 = fdiv reassoc ninf nsz float %1795, %1794
  %1797 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %1798 = load float, float* %1797, align 4
  %1799 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1798, float 0x3F1A36E2E0000000)
  %1800 = fdiv reassoc ninf nsz float %1785, %1799
  %1801 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %1802 = load float, float* %1801, align 4
  %1803 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1802, float 0x3F1A36E2E0000000)
  %1804 = extractelement <2 x float> %1791, i64 1
  %1805 = fdiv reassoc ninf nsz float %1804, %1803
  %1806 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1800, float %1805)
  %1807 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1796, float %1806)
  %1808 = fcmp reassoc ninf nsz olt float %1807, 0x3FED70A3E0000000
  %1809 = fcmp reassoc ninf nsz ogt float %1785, 0x3EE4F8B580000000
  %.0380 = select i1 %1808, i1 %1809, i1 false
  br i1 %.0380, label %true_block415, label %true_block418

true_block415:                                    ; preds = %true_block409
  %1810 = insertelement <2 x float> poison, float %1785, i64 0
  %1811 = shufflevector <2 x float> %1810, <2 x float> poison, <2 x i32> zeroinitializer
  %1812 = fdiv reassoc ninf nsz <2 x float> %1791, %1811
  %1813 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1812, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1814 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1813, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1815 = fadd reassoc ninf nsz <2 x float> %1814, %1769
  %1816 = fadd reassoc ninf nsz float %.33.ph, 1.000000e+00
  br label %true_block418

true_block418:                                    ; preds = %true_block415, %true_block409, %true_block406
  %.34.ph = phi float [ %.33.ph, %true_block406 ], [ %.33.ph, %true_block409 ], [ %1816, %true_block415 ]
  %1817 = phi <2 x float> [ %1769, %true_block406 ], [ %1769, %true_block409 ], [ %1815, %true_block415 ]
  %1818 = icmp slt i32 %477, %1670
  br i1 %1818, label %true_block421, label %true_block430

true_block421:                                    ; preds = %true_block418
  %1819 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %1820 = load float*, float** %1819, align 8
  %1821 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %1822 = load i32, i32* %1821, align 4
  %1823 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %1824 = load i32, i32* %1823, align 4
  %1825 = mul i32 %1822, %1659
  %1826 = add i32 %1825, %477
  %1827 = mul i32 %1826, %1824
  %1828 = add i32 %1827, 1
  %1829 = sext i32 %1828 to i64
  %1830 = getelementptr float, float* %1820, i64 %1829
  %1831 = load float, float* %1830, align 4
  %1832 = add i32 %1827, 2
  %1833 = insertelement <2 x i32> poison, i32 %1827, i64 0
  %1834 = insertelement <2 x i32> %1833, i32 %1832, i64 1
  %1835 = sext <2 x i32> %1834 to <2 x i64>
  %1836 = insertelement <2 x float*> poison, float* %1820, i64 0
  %1837 = shufflevector <2 x float*> %1836, <2 x float*> poison, <2 x i32> zeroinitializer
  %1838 = getelementptr float, <2 x float*> %1837, <2 x i64> %1835
  %1839 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1838, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1840 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %1841 = load float, float* %1840, align 4
  %1842 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1841, float 0x3F1A36E2E0000000)
  %1843 = extractelement <2 x float> %1839, i64 0
  %1844 = fdiv reassoc ninf nsz float %1843, %1842
  %1845 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %1846 = load float, float* %1845, align 4
  %1847 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1846, float 0x3F1A36E2E0000000)
  %1848 = fdiv reassoc ninf nsz float %1831, %1847
  %1849 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %1850 = load float, float* %1849, align 4
  %1851 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1850, float 0x3F1A36E2E0000000)
  %1852 = extractelement <2 x float> %1839, i64 1
  %1853 = fdiv reassoc ninf nsz float %1852, %1851
  %1854 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1848, float %1853)
  %1855 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1844, float %1854)
  %1856 = fcmp reassoc ninf nsz olt float %1855, 0x3FED70A3E0000000
  %1857 = fcmp reassoc ninf nsz ogt float %1831, 0x3EE4F8B580000000
  %.0378 = select i1 %1856, i1 %1857, i1 false
  br i1 %.0378, label %true_block427, label %true_block430

true_block427:                                    ; preds = %true_block421
  %1858 = insertelement <2 x float> poison, float %1831, i64 0
  %1859 = shufflevector <2 x float> %1858, <2 x float> poison, <2 x i32> zeroinitializer
  %1860 = fdiv reassoc ninf nsz <2 x float> %1839, %1859
  %1861 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1860, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1862 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1861, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1863 = fadd reassoc ninf nsz <2 x float> %1862, %1817
  %1864 = fadd reassoc ninf nsz float %.34.ph, 1.000000e+00
  br label %true_block430

true_block430:                                    ; preds = %true_block427, %true_block421, %true_block418
  %.35.ph = phi float [ %.34.ph, %true_block418 ], [ %.34.ph, %true_block421 ], [ %1864, %true_block427 ]
  %1865 = phi <2 x float> [ %1817, %true_block418 ], [ %1817, %true_block421 ], [ %1863, %true_block427 ]
  %1866 = icmp slt i32 %480, %1670
  br i1 %1866, label %true_block433, label %true_block442

true_block433:                                    ; preds = %true_block430
  %1867 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %1868 = load float*, float** %1867, align 8
  %1869 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %1870 = load i32, i32* %1869, align 4
  %1871 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %1872 = load i32, i32* %1871, align 4
  %1873 = mul i32 %1870, %1659
  %1874 = add i32 %1873, %480
  %1875 = mul i32 %1874, %1872
  %1876 = or i32 %1875, 1
  %1877 = sext i32 %1876 to i64
  %1878 = getelementptr float, float* %1868, i64 %1877
  %1879 = load float, float* %1878, align 4
  %1880 = or i32 %1875, 2
  %1881 = insertelement <2 x i32> poison, i32 %1875, i64 0
  %1882 = insertelement <2 x i32> %1881, i32 %1880, i64 1
  %1883 = sext <2 x i32> %1882 to <2 x i64>
  %1884 = insertelement <2 x float*> poison, float* %1868, i64 0
  %1885 = shufflevector <2 x float*> %1884, <2 x float*> poison, <2 x i32> zeroinitializer
  %1886 = getelementptr float, <2 x float*> %1885, <2 x i64> %1883
  %1887 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1886, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1888 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %1889 = load float, float* %1888, align 4
  %1890 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1889, float 0x3F1A36E2E0000000)
  %1891 = extractelement <2 x float> %1887, i64 0
  %1892 = fdiv reassoc ninf nsz float %1891, %1890
  %1893 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %1894 = load float, float* %1893, align 4
  %1895 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1894, float 0x3F1A36E2E0000000)
  %1896 = fdiv reassoc ninf nsz float %1879, %1895
  %1897 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %1898 = load float, float* %1897, align 4
  %1899 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1898, float 0x3F1A36E2E0000000)
  %1900 = extractelement <2 x float> %1887, i64 1
  %1901 = fdiv reassoc ninf nsz float %1900, %1899
  %1902 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1896, float %1901)
  %1903 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1892, float %1902)
  %1904 = fcmp reassoc ninf nsz olt float %1903, 0x3FED70A3E0000000
  %1905 = fcmp reassoc ninf nsz ogt float %1879, 0x3EE4F8B580000000
  %.0376 = select i1 %1904, i1 %1905, i1 false
  br i1 %.0376, label %true_block439, label %true_block442

true_block439:                                    ; preds = %true_block433
  %1906 = insertelement <2 x float> poison, float %1879, i64 0
  %1907 = shufflevector <2 x float> %1906, <2 x float> poison, <2 x i32> zeroinitializer
  %1908 = fdiv reassoc ninf nsz <2 x float> %1887, %1907
  %1909 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1908, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1910 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1909, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1911 = fadd reassoc ninf nsz <2 x float> %1910, %1865
  %1912 = fadd reassoc ninf nsz float %.35.ph, 1.000000e+00
  br label %true_block442

true_block442:                                    ; preds = %true_block439, %true_block433, %true_block430
  %.36.ph = phi float [ %.35.ph, %true_block430 ], [ %.35.ph, %true_block433 ], [ %1912, %true_block439 ]
  %1913 = phi <2 x float> [ %1865, %true_block430 ], [ %1865, %true_block433 ], [ %1911, %true_block439 ]
  %1914 = icmp slt i32 %476, %1670
  br i1 %1914, label %true_block445, label %true_block454

true_block445:                                    ; preds = %true_block442
  %1915 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %1916 = load float*, float** %1915, align 8
  %1917 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %1918 = load i32, i32* %1917, align 4
  %1919 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %1920 = load i32, i32* %1919, align 4
  %1921 = mul i32 %1918, %1659
  %1922 = add i32 %1921, %476
  %1923 = mul i32 %1922, %1920
  %1924 = add i32 %1923, 1
  %1925 = sext i32 %1924 to i64
  %1926 = getelementptr float, float* %1916, i64 %1925
  %1927 = load float, float* %1926, align 4
  %1928 = add i32 %1923, 2
  %1929 = insertelement <2 x i32> poison, i32 %1923, i64 0
  %1930 = insertelement <2 x i32> %1929, i32 %1928, i64 1
  %1931 = sext <2 x i32> %1930 to <2 x i64>
  %1932 = insertelement <2 x float*> poison, float* %1916, i64 0
  %1933 = shufflevector <2 x float*> %1932, <2 x float*> poison, <2 x i32> zeroinitializer
  %1934 = getelementptr float, <2 x float*> %1933, <2 x i64> %1931
  %1935 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1934, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1936 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %1937 = load float, float* %1936, align 4
  %1938 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1937, float 0x3F1A36E2E0000000)
  %1939 = extractelement <2 x float> %1935, i64 0
  %1940 = fdiv reassoc ninf nsz float %1939, %1938
  %1941 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %1942 = load float, float* %1941, align 4
  %1943 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1942, float 0x3F1A36E2E0000000)
  %1944 = fdiv reassoc ninf nsz float %1927, %1943
  %1945 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %1946 = load float, float* %1945, align 4
  %1947 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1946, float 0x3F1A36E2E0000000)
  %1948 = extractelement <2 x float> %1935, i64 1
  %1949 = fdiv reassoc ninf nsz float %1948, %1947
  %1950 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1944, float %1949)
  %1951 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1940, float %1950)
  %1952 = fcmp reassoc ninf nsz olt float %1951, 0x3FED70A3E0000000
  %1953 = fcmp reassoc ninf nsz ogt float %1927, 0x3EE4F8B580000000
  %.0374 = select i1 %1952, i1 %1953, i1 false
  br i1 %.0374, label %true_block451, label %true_block454

true_block451:                                    ; preds = %true_block445
  %1954 = insertelement <2 x float> poison, float %1927, i64 0
  %1955 = shufflevector <2 x float> %1954, <2 x float> poison, <2 x i32> zeroinitializer
  %1956 = fdiv reassoc ninf nsz <2 x float> %1935, %1955
  %1957 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %1956, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %1958 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %1957, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %1959 = fadd reassoc ninf nsz <2 x float> %1958, %1913
  %1960 = fadd reassoc ninf nsz float %.36.ph, 1.000000e+00
  br label %true_block454

true_block454:                                    ; preds = %true_block451, %true_block445, %true_block442
  %.37.ph = phi float [ %.36.ph, %true_block442 ], [ %.36.ph, %true_block445 ], [ %1960, %true_block451 ]
  %1961 = phi <2 x float> [ %1913, %true_block442 ], [ %1913, %true_block445 ], [ %1959, %true_block451 ]
  %1962 = icmp slt i32 %481, %1670
  br i1 %1962, label %true_block457, label %true_block466

true_block457:                                    ; preds = %true_block454
  %1963 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %1964 = load float*, float** %1963, align 8
  %1965 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %1966 = load i32, i32* %1965, align 4
  %1967 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %1968 = load i32, i32* %1967, align 4
  %1969 = mul i32 %1966, %1659
  %1970 = add i32 %1969, %481
  %1971 = mul i32 %1970, %1968
  %1972 = or i32 %1971, 1
  %1973 = sext i32 %1972 to i64
  %1974 = getelementptr float, float* %1964, i64 %1973
  %1975 = load float, float* %1974, align 4
  %1976 = add i32 %1971, 2
  %1977 = insertelement <2 x i32> poison, i32 %1971, i64 0
  %1978 = insertelement <2 x i32> %1977, i32 %1976, i64 1
  %1979 = sext <2 x i32> %1978 to <2 x i64>
  %1980 = insertelement <2 x float*> poison, float* %1964, i64 0
  %1981 = shufflevector <2 x float*> %1980, <2 x float*> poison, <2 x i32> zeroinitializer
  %1982 = getelementptr float, <2 x float*> %1981, <2 x i64> %1979
  %1983 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %1982, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %1984 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %1985 = load float, float* %1984, align 4
  %1986 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1985, float 0x3F1A36E2E0000000)
  %1987 = extractelement <2 x float> %1983, i64 0
  %1988 = fdiv reassoc ninf nsz float %1987, %1986
  %1989 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %1990 = load float, float* %1989, align 4
  %1991 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1990, float 0x3F1A36E2E0000000)
  %1992 = fdiv reassoc ninf nsz float %1975, %1991
  %1993 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %1994 = load float, float* %1993, align 4
  %1995 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1994, float 0x3F1A36E2E0000000)
  %1996 = extractelement <2 x float> %1983, i64 1
  %1997 = fdiv reassoc ninf nsz float %1996, %1995
  %1998 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1992, float %1997)
  %1999 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %1988, float %1998)
  %2000 = fcmp reassoc ninf nsz olt float %1999, 0x3FED70A3E0000000
  %2001 = fcmp reassoc ninf nsz ogt float %1975, 0x3EE4F8B580000000
  %.0372 = select i1 %2000, i1 %2001, i1 false
  br i1 %.0372, label %true_block463, label %true_block466

true_block463:                                    ; preds = %true_block457
  %2002 = insertelement <2 x float> poison, float %1975, i64 0
  %2003 = shufflevector <2 x float> %2002, <2 x float> poison, <2 x i32> zeroinitializer
  %2004 = fdiv reassoc ninf nsz <2 x float> %1983, %2003
  %2005 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2004, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2006 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2005, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2007 = fadd reassoc ninf nsz <2 x float> %2006, %1961
  %2008 = fadd reassoc ninf nsz float %.37.ph, 1.000000e+00
  br label %true_block466

true_block466:                                    ; preds = %true_block463, %true_block457, %true_block454
  %.38.ph = phi float [ %.37.ph, %true_block454 ], [ %.37.ph, %true_block457 ], [ %2008, %true_block463 ]
  %2009 = phi <2 x float> [ %1961, %true_block454 ], [ %1961, %true_block457 ], [ %2007, %true_block463 ]
  %2010 = icmp slt i32 %475, %1670
  br i1 %2010, label %true_block469, label %after_if471

true_block469:                                    ; preds = %true_block466
  %2011 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 1
  %2012 = load float*, float** %2011, align 8
  %2013 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 1
  %2014 = load i32, i32* %2013, align 4
  %2015 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 0, i32 0, i32 2
  %2016 = load i32, i32* %2015, align 4
  %2017 = mul i32 %2014, %1659
  %2018 = add i32 %2017, %475
  %2019 = mul i32 %2018, %2016
  %2020 = add i32 %2019, 1
  %2021 = sext i32 %2020 to i64
  %2022 = getelementptr float, float* %2012, i64 %2021
  %2023 = load float, float* %2022, align 4
  %2024 = add i32 %2019, 2
  %2025 = insertelement <2 x i32> poison, i32 %2019, i64 0
  %2026 = insertelement <2 x i32> %2025, i32 %2024, i64 1
  %2027 = sext <2 x i32> %2026 to <2 x i64>
  %2028 = insertelement <2 x float*> poison, float* %2012, i64 0
  %2029 = shufflevector <2 x float*> %2028, <2 x float*> poison, <2 x i32> zeroinitializer
  %2030 = getelementptr float, <2 x float*> %2029, <2 x i64> %2027
  %2031 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2030, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2032 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 2
  %2033 = load float, float* %2032, align 4
  %2034 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2033, float 0x3F1A36E2E0000000)
  %2035 = extractelement <2 x float> %2031, i64 0
  %2036 = fdiv reassoc ninf nsz float %2035, %2034
  %2037 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 3
  %2038 = load float, float* %2037, align 4
  %2039 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2038, float 0x3F1A36E2E0000000)
  %2040 = fdiv reassoc ninf nsz float %2023, %2039
  %2041 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1668, i64 0, i32 4
  %2042 = load float, float* %2041, align 4
  %2043 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2042, float 0x3F1A36E2E0000000)
  %2044 = extractelement <2 x float> %2031, i64 1
  %2045 = fdiv reassoc ninf nsz float %2044, %2043
  %2046 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2040, float %2045)
  %2047 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2036, float %2046)
  %2048 = fcmp reassoc ninf nsz olt float %2047, 0x3FED70A3E0000000
  %2049 = fcmp reassoc ninf nsz ogt float %2023, 0x3EE4F8B580000000
  %.0370 = select i1 %2048, i1 %2049, i1 false
  br i1 %.0370, label %true_block475, label %after_if471

after_if471:                                      ; preds = %true_block475, %true_block469, %true_block466, %after_if375
  %.39 = phi float [ %2059, %true_block475 ], [ %.38.ph, %true_block469 ], [ %.38.ph, %true_block466 ], [ %.31, %after_if375 ]
  %2050 = phi <2 x float> [ %2058, %true_block475 ], [ %2009, %true_block469 ], [ %2009, %true_block466 ], [ %1658, %after_if375 ]
  %2051 = or i32 %47, 5
  %2052 = icmp slt i32 %2051, %23
  br i1 %2052, label %true_block478, label %after_if567

true_block475:                                    ; preds = %true_block469
  %2053 = insertelement <2 x float> poison, float %2023, i64 0
  %2054 = shufflevector <2 x float> %2053, <2 x float> poison, <2 x i32> zeroinitializer
  %2055 = fdiv reassoc ninf nsz <2 x float> %2031, %2054
  %2056 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2055, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2057 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2056, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2058 = fadd reassoc ninf nsz <2 x float> %2057, %2009
  %2059 = fadd reassoc ninf nsz float %.38.ph, 1.000000e+00
  br label %after_if471

true_block478:                                    ; preds = %after_if471
  %2060 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %2061 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 6
  %2062 = load i32, i32* %2061, align 4
  %2063 = icmp slt i32 %52, %2062
  br i1 %2063, label %true_block481, label %true_block490

true_block481:                                    ; preds = %true_block478
  %2064 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2065 = load float*, float** %2064, align 8
  %2066 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2067 = load i32, i32* %2066, align 4
  %2068 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2069 = load i32, i32* %2068, align 4
  %2070 = mul i32 %2067, %2051
  %2071 = shl i32 %35, 3
  %2072 = mul i32 %2071, %44
  %2073 = sub i32 %2070, %2072
  %2074 = add i32 %lsr.iv, %2073
  %2075 = add i32 %2074, -7
  %2076 = mul i32 %2075, %2069
  %2077 = sext i32 %2076 to i64
  %2078 = getelementptr float, float* %2065, i64 %2077
  %2079 = load float, float* %2078, align 4
  %2080 = add i32 %2076, 1
  %2081 = sext i32 %2080 to i64
  %2082 = getelementptr float, float* %2065, i64 %2081
  %2083 = load float, float* %2082, align 4
  %2084 = add i32 %2076, 2
  %2085 = sext i32 %2084 to i64
  %2086 = getelementptr float, float* %2065, i64 %2085
  %2087 = load float, float* %2086, align 4
  %2088 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2089 = load float, float* %2088, align 4
  %2090 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2089, float 0x3F1A36E2E0000000)
  %2091 = fdiv reassoc ninf nsz float %2079, %2090
  %2092 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2093 = load float, float* %2092, align 4
  %2094 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2093, float 0x3F1A36E2E0000000)
  %2095 = fdiv reassoc ninf nsz float %2083, %2094
  %2096 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2097 = load float, float* %2096, align 4
  %2098 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2097, float 0x3F1A36E2E0000000)
  %2099 = fdiv reassoc ninf nsz float %2087, %2098
  %2100 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2095, float %2099)
  %2101 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2091, float %2100)
  %2102 = fcmp reassoc ninf nsz olt float %2101, 0x3FED70A3E0000000
  %2103 = fcmp reassoc ninf nsz ogt float %2083, 0x3EE4F8B580000000
  %.0368 = select i1 %2102, i1 %2103, i1 false
  br i1 %.0368, label %true_block487, label %true_block490

true_block487:                                    ; preds = %true_block481
  %2104 = insertelement <2 x float> poison, float %2079, i64 0
  %2105 = insertelement <2 x float> %2104, float %2087, i64 1
  %2106 = insertelement <2 x float> poison, float %2083, i64 0
  %2107 = shufflevector <2 x float> %2106, <2 x float> poison, <2 x i32> zeroinitializer
  %2108 = fdiv reassoc ninf nsz <2 x float> %2105, %2107
  %2109 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2108, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2110 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2109, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2111 = fadd reassoc ninf nsz <2 x float> %2110, %2050
  %2112 = fadd reassoc ninf nsz float %.39, 1.000000e+00
  br label %true_block490

true_block490:                                    ; preds = %true_block487, %true_block481, %true_block478
  %.40.ph = phi float [ %.39, %true_block478 ], [ %.39, %true_block481 ], [ %2112, %true_block487 ]
  %2113 = phi <2 x float> [ %2050, %true_block478 ], [ %2050, %true_block481 ], [ %2111, %true_block487 ]
  %2114 = icmp slt i32 %478, %2062
  br i1 %2114, label %true_block493, label %true_block502

true_block493:                                    ; preds = %true_block490
  %2115 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2116 = load float*, float** %2115, align 8
  %2117 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2118 = load i32, i32* %2117, align 4
  %2119 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2120 = load i32, i32* %2119, align 4
  %2121 = mul i32 %2118, %2051
  %2122 = add i32 %2121, %478
  %2123 = mul i32 %2122, %2120
  %2124 = sext i32 %2123 to i64
  %2125 = getelementptr float, float* %2116, i64 %2124
  %2126 = add i32 %2123, 1
  %2127 = sext i32 %2126 to i64
  %2128 = getelementptr float, float* %2116, i64 %2127
  %2129 = load float, float* %2128, align 4
  %2130 = add i32 %2123, 2
  %2131 = sext i32 %2130 to i64
  %2132 = getelementptr float, float* %2116, i64 %2131
  %2133 = insertelement <2 x float*> poison, float* %2125, i64 0
  %2134 = insertelement <2 x float*> %2133, float* %2132, i64 1
  %2135 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2134, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2136 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2137 = load float, float* %2136, align 4
  %2138 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2137, float 0x3F1A36E2E0000000)
  %2139 = extractelement <2 x float> %2135, i64 0
  %2140 = fdiv reassoc ninf nsz float %2139, %2138
  %2141 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2142 = load float, float* %2141, align 4
  %2143 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2142, float 0x3F1A36E2E0000000)
  %2144 = fdiv reassoc ninf nsz float %2129, %2143
  %2145 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2146 = load float, float* %2145, align 4
  %2147 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2146, float 0x3F1A36E2E0000000)
  %2148 = extractelement <2 x float> %2135, i64 1
  %2149 = fdiv reassoc ninf nsz float %2148, %2147
  %2150 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2144, float %2149)
  %2151 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2140, float %2150)
  %2152 = fcmp reassoc ninf nsz olt float %2151, 0x3FED70A3E0000000
  %2153 = fcmp reassoc ninf nsz ogt float %2129, 0x3EE4F8B580000000
  %.0366 = select i1 %2152, i1 %2153, i1 false
  br i1 %.0366, label %true_block499, label %true_block502

true_block499:                                    ; preds = %true_block493
  %2154 = insertelement <2 x float> poison, float %2129, i64 0
  %2155 = shufflevector <2 x float> %2154, <2 x float> poison, <2 x i32> zeroinitializer
  %2156 = fdiv reassoc ninf nsz <2 x float> %2135, %2155
  %2157 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2156, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2158 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2157, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2159 = fadd reassoc ninf nsz <2 x float> %2158, %2113
  %2160 = fadd reassoc ninf nsz float %.40.ph, 1.000000e+00
  br label %true_block502

true_block502:                                    ; preds = %true_block499, %true_block493, %true_block490
  %.41.ph = phi float [ %.40.ph, %true_block490 ], [ %.40.ph, %true_block493 ], [ %2160, %true_block499 ]
  %2161 = phi <2 x float> [ %2113, %true_block490 ], [ %2113, %true_block493 ], [ %2159, %true_block499 ]
  %2162 = icmp slt i32 %479, %2062
  br i1 %2162, label %true_block505, label %true_block514

true_block505:                                    ; preds = %true_block502
  %2163 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2164 = load float*, float** %2163, align 8
  %2165 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2166 = load i32, i32* %2165, align 4
  %2167 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2168 = load i32, i32* %2167, align 4
  %2169 = mul i32 %2166, %2051
  %2170 = add i32 %2169, %479
  %2171 = mul i32 %2170, %2168
  %2172 = add i32 %2171, 1
  %2173 = sext i32 %2172 to i64
  %2174 = getelementptr float, float* %2164, i64 %2173
  %2175 = load float, float* %2174, align 4
  %2176 = add i32 %2171, 2
  %2177 = insertelement <2 x i32> poison, i32 %2171, i64 0
  %2178 = insertelement <2 x i32> %2177, i32 %2176, i64 1
  %2179 = sext <2 x i32> %2178 to <2 x i64>
  %2180 = insertelement <2 x float*> poison, float* %2164, i64 0
  %2181 = shufflevector <2 x float*> %2180, <2 x float*> poison, <2 x i32> zeroinitializer
  %2182 = getelementptr float, <2 x float*> %2181, <2 x i64> %2179
  %2183 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2182, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2184 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2185 = load float, float* %2184, align 4
  %2186 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2185, float 0x3F1A36E2E0000000)
  %2187 = extractelement <2 x float> %2183, i64 0
  %2188 = fdiv reassoc ninf nsz float %2187, %2186
  %2189 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2190 = load float, float* %2189, align 4
  %2191 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2190, float 0x3F1A36E2E0000000)
  %2192 = fdiv reassoc ninf nsz float %2175, %2191
  %2193 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2194 = load float, float* %2193, align 4
  %2195 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2194, float 0x3F1A36E2E0000000)
  %2196 = extractelement <2 x float> %2183, i64 1
  %2197 = fdiv reassoc ninf nsz float %2196, %2195
  %2198 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2192, float %2197)
  %2199 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2188, float %2198)
  %2200 = fcmp reassoc ninf nsz olt float %2199, 0x3FED70A3E0000000
  %2201 = fcmp reassoc ninf nsz ogt float %2175, 0x3EE4F8B580000000
  %.0364 = select i1 %2200, i1 %2201, i1 false
  br i1 %.0364, label %true_block511, label %true_block514

true_block511:                                    ; preds = %true_block505
  %2202 = insertelement <2 x float> poison, float %2175, i64 0
  %2203 = shufflevector <2 x float> %2202, <2 x float> poison, <2 x i32> zeroinitializer
  %2204 = fdiv reassoc ninf nsz <2 x float> %2183, %2203
  %2205 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2204, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2206 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2205, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2207 = fadd reassoc ninf nsz <2 x float> %2206, %2161
  %2208 = fadd reassoc ninf nsz float %.41.ph, 1.000000e+00
  br label %true_block514

true_block514:                                    ; preds = %true_block511, %true_block505, %true_block502
  %.42.ph = phi float [ %.41.ph, %true_block502 ], [ %.41.ph, %true_block505 ], [ %2208, %true_block511 ]
  %2209 = phi <2 x float> [ %2161, %true_block502 ], [ %2161, %true_block505 ], [ %2207, %true_block511 ]
  %2210 = icmp slt i32 %477, %2062
  br i1 %2210, label %true_block517, label %true_block526

true_block517:                                    ; preds = %true_block514
  %2211 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2212 = load float*, float** %2211, align 8
  %2213 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2214 = load i32, i32* %2213, align 4
  %2215 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2216 = load i32, i32* %2215, align 4
  %2217 = mul i32 %2214, %2051
  %2218 = add i32 %2217, %477
  %2219 = mul i32 %2218, %2216
  %2220 = add i32 %2219, 1
  %2221 = sext i32 %2220 to i64
  %2222 = getelementptr float, float* %2212, i64 %2221
  %2223 = load float, float* %2222, align 4
  %2224 = add i32 %2219, 2
  %2225 = insertelement <2 x i32> poison, i32 %2219, i64 0
  %2226 = insertelement <2 x i32> %2225, i32 %2224, i64 1
  %2227 = sext <2 x i32> %2226 to <2 x i64>
  %2228 = insertelement <2 x float*> poison, float* %2212, i64 0
  %2229 = shufflevector <2 x float*> %2228, <2 x float*> poison, <2 x i32> zeroinitializer
  %2230 = getelementptr float, <2 x float*> %2229, <2 x i64> %2227
  %2231 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2230, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2232 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2233 = load float, float* %2232, align 4
  %2234 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2233, float 0x3F1A36E2E0000000)
  %2235 = extractelement <2 x float> %2231, i64 0
  %2236 = fdiv reassoc ninf nsz float %2235, %2234
  %2237 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2238 = load float, float* %2237, align 4
  %2239 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2238, float 0x3F1A36E2E0000000)
  %2240 = fdiv reassoc ninf nsz float %2223, %2239
  %2241 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2242 = load float, float* %2241, align 4
  %2243 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2242, float 0x3F1A36E2E0000000)
  %2244 = extractelement <2 x float> %2231, i64 1
  %2245 = fdiv reassoc ninf nsz float %2244, %2243
  %2246 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2240, float %2245)
  %2247 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2236, float %2246)
  %2248 = fcmp reassoc ninf nsz olt float %2247, 0x3FED70A3E0000000
  %2249 = fcmp reassoc ninf nsz ogt float %2223, 0x3EE4F8B580000000
  %.0362 = select i1 %2248, i1 %2249, i1 false
  br i1 %.0362, label %true_block523, label %true_block526

true_block523:                                    ; preds = %true_block517
  %2250 = insertelement <2 x float> poison, float %2223, i64 0
  %2251 = shufflevector <2 x float> %2250, <2 x float> poison, <2 x i32> zeroinitializer
  %2252 = fdiv reassoc ninf nsz <2 x float> %2231, %2251
  %2253 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2252, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2254 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2253, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2255 = fadd reassoc ninf nsz <2 x float> %2254, %2209
  %2256 = fadd reassoc ninf nsz float %.42.ph, 1.000000e+00
  br label %true_block526

true_block526:                                    ; preds = %true_block523, %true_block517, %true_block514
  %.43.ph = phi float [ %.42.ph, %true_block514 ], [ %.42.ph, %true_block517 ], [ %2256, %true_block523 ]
  %2257 = phi <2 x float> [ %2209, %true_block514 ], [ %2209, %true_block517 ], [ %2255, %true_block523 ]
  %2258 = icmp slt i32 %480, %2062
  br i1 %2258, label %true_block529, label %true_block538

true_block529:                                    ; preds = %true_block526
  %2259 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2260 = load float*, float** %2259, align 8
  %2261 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2262 = load i32, i32* %2261, align 4
  %2263 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2264 = load i32, i32* %2263, align 4
  %2265 = mul i32 %2262, %2051
  %2266 = add i32 %2265, %480
  %2267 = mul i32 %2266, %2264
  %2268 = add i32 %2267, 1
  %2269 = sext i32 %2268 to i64
  %2270 = getelementptr float, float* %2260, i64 %2269
  %2271 = load float, float* %2270, align 4
  %2272 = add i32 %2267, 2
  %2273 = insertelement <2 x i32> poison, i32 %2267, i64 0
  %2274 = insertelement <2 x i32> %2273, i32 %2272, i64 1
  %2275 = sext <2 x i32> %2274 to <2 x i64>
  %2276 = insertelement <2 x float*> poison, float* %2260, i64 0
  %2277 = shufflevector <2 x float*> %2276, <2 x float*> poison, <2 x i32> zeroinitializer
  %2278 = getelementptr float, <2 x float*> %2277, <2 x i64> %2275
  %2279 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2278, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2280 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2281 = load float, float* %2280, align 4
  %2282 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2281, float 0x3F1A36E2E0000000)
  %2283 = extractelement <2 x float> %2279, i64 0
  %2284 = fdiv reassoc ninf nsz float %2283, %2282
  %2285 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2286 = load float, float* %2285, align 4
  %2287 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2286, float 0x3F1A36E2E0000000)
  %2288 = fdiv reassoc ninf nsz float %2271, %2287
  %2289 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2290 = load float, float* %2289, align 4
  %2291 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2290, float 0x3F1A36E2E0000000)
  %2292 = extractelement <2 x float> %2279, i64 1
  %2293 = fdiv reassoc ninf nsz float %2292, %2291
  %2294 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2288, float %2293)
  %2295 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2284, float %2294)
  %2296 = fcmp reassoc ninf nsz olt float %2295, 0x3FED70A3E0000000
  %2297 = fcmp reassoc ninf nsz ogt float %2271, 0x3EE4F8B580000000
  %.0360 = select i1 %2296, i1 %2297, i1 false
  br i1 %.0360, label %true_block535, label %true_block538

true_block535:                                    ; preds = %true_block529
  %2298 = insertelement <2 x float> poison, float %2271, i64 0
  %2299 = shufflevector <2 x float> %2298, <2 x float> poison, <2 x i32> zeroinitializer
  %2300 = fdiv reassoc ninf nsz <2 x float> %2279, %2299
  %2301 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2300, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2302 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2301, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2303 = fadd reassoc ninf nsz <2 x float> %2302, %2257
  %2304 = fadd reassoc ninf nsz float %.43.ph, 1.000000e+00
  br label %true_block538

true_block538:                                    ; preds = %true_block535, %true_block529, %true_block526
  %.44.ph = phi float [ %.43.ph, %true_block526 ], [ %.43.ph, %true_block529 ], [ %2304, %true_block535 ]
  %2305 = phi <2 x float> [ %2257, %true_block526 ], [ %2257, %true_block529 ], [ %2303, %true_block535 ]
  %2306 = icmp slt i32 %476, %2062
  br i1 %2306, label %true_block541, label %true_block550

true_block541:                                    ; preds = %true_block538
  %2307 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2308 = load float*, float** %2307, align 8
  %2309 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2310 = load i32, i32* %2309, align 4
  %2311 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2312 = load i32, i32* %2311, align 4
  %2313 = mul i32 %2310, %2051
  %2314 = add i32 %2313, %476
  %2315 = mul i32 %2314, %2312
  %2316 = add i32 %2315, 1
  %2317 = sext i32 %2316 to i64
  %2318 = getelementptr float, float* %2308, i64 %2317
  %2319 = load float, float* %2318, align 4
  %2320 = add i32 %2315, 2
  %2321 = insertelement <2 x i32> poison, i32 %2315, i64 0
  %2322 = insertelement <2 x i32> %2321, i32 %2320, i64 1
  %2323 = sext <2 x i32> %2322 to <2 x i64>
  %2324 = insertelement <2 x float*> poison, float* %2308, i64 0
  %2325 = shufflevector <2 x float*> %2324, <2 x float*> poison, <2 x i32> zeroinitializer
  %2326 = getelementptr float, <2 x float*> %2325, <2 x i64> %2323
  %2327 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2326, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2328 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2329 = load float, float* %2328, align 4
  %2330 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2329, float 0x3F1A36E2E0000000)
  %2331 = extractelement <2 x float> %2327, i64 0
  %2332 = fdiv reassoc ninf nsz float %2331, %2330
  %2333 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2334 = load float, float* %2333, align 4
  %2335 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2334, float 0x3F1A36E2E0000000)
  %2336 = fdiv reassoc ninf nsz float %2319, %2335
  %2337 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2338 = load float, float* %2337, align 4
  %2339 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2338, float 0x3F1A36E2E0000000)
  %2340 = extractelement <2 x float> %2327, i64 1
  %2341 = fdiv reassoc ninf nsz float %2340, %2339
  %2342 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2336, float %2341)
  %2343 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2332, float %2342)
  %2344 = fcmp reassoc ninf nsz olt float %2343, 0x3FED70A3E0000000
  %2345 = fcmp reassoc ninf nsz ogt float %2319, 0x3EE4F8B580000000
  %.0358 = select i1 %2344, i1 %2345, i1 false
  br i1 %.0358, label %true_block547, label %true_block550

true_block547:                                    ; preds = %true_block541
  %2346 = insertelement <2 x float> poison, float %2319, i64 0
  %2347 = shufflevector <2 x float> %2346, <2 x float> poison, <2 x i32> zeroinitializer
  %2348 = fdiv reassoc ninf nsz <2 x float> %2327, %2347
  %2349 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2348, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2350 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2349, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2351 = fadd reassoc ninf nsz <2 x float> %2350, %2305
  %2352 = fadd reassoc ninf nsz float %.44.ph, 1.000000e+00
  br label %true_block550

true_block550:                                    ; preds = %true_block547, %true_block541, %true_block538
  %.45.ph = phi float [ %.44.ph, %true_block538 ], [ %.44.ph, %true_block541 ], [ %2352, %true_block547 ]
  %2353 = phi <2 x float> [ %2305, %true_block538 ], [ %2305, %true_block541 ], [ %2351, %true_block547 ]
  %2354 = icmp slt i32 %481, %2062
  br i1 %2354, label %true_block553, label %true_block562

true_block553:                                    ; preds = %true_block550
  %2355 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2356 = load float*, float** %2355, align 8
  %2357 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2358 = load i32, i32* %2357, align 4
  %2359 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2360 = load i32, i32* %2359, align 4
  %2361 = mul i32 %2358, %2051
  %2362 = add i32 %2361, %481
  %2363 = mul i32 %2362, %2360
  %2364 = add i32 %2363, 1
  %2365 = sext i32 %2364 to i64
  %2366 = getelementptr float, float* %2356, i64 %2365
  %2367 = load float, float* %2366, align 4
  %2368 = add i32 %2363, 2
  %2369 = insertelement <2 x i32> poison, i32 %2363, i64 0
  %2370 = insertelement <2 x i32> %2369, i32 %2368, i64 1
  %2371 = sext <2 x i32> %2370 to <2 x i64>
  %2372 = insertelement <2 x float*> poison, float* %2356, i64 0
  %2373 = shufflevector <2 x float*> %2372, <2 x float*> poison, <2 x i32> zeroinitializer
  %2374 = getelementptr float, <2 x float*> %2373, <2 x i64> %2371
  %2375 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2374, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2376 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2377 = load float, float* %2376, align 4
  %2378 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2377, float 0x3F1A36E2E0000000)
  %2379 = extractelement <2 x float> %2375, i64 0
  %2380 = fdiv reassoc ninf nsz float %2379, %2378
  %2381 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2382 = load float, float* %2381, align 4
  %2383 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2382, float 0x3F1A36E2E0000000)
  %2384 = fdiv reassoc ninf nsz float %2367, %2383
  %2385 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2386 = load float, float* %2385, align 4
  %2387 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2386, float 0x3F1A36E2E0000000)
  %2388 = extractelement <2 x float> %2375, i64 1
  %2389 = fdiv reassoc ninf nsz float %2388, %2387
  %2390 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2384, float %2389)
  %2391 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2380, float %2390)
  %2392 = fcmp reassoc ninf nsz olt float %2391, 0x3FED70A3E0000000
  %2393 = fcmp reassoc ninf nsz ogt float %2367, 0x3EE4F8B580000000
  %.0356 = select i1 %2392, i1 %2393, i1 false
  br i1 %.0356, label %true_block559, label %true_block562

true_block559:                                    ; preds = %true_block553
  %2394 = insertelement <2 x float> poison, float %2367, i64 0
  %2395 = shufflevector <2 x float> %2394, <2 x float> poison, <2 x i32> zeroinitializer
  %2396 = fdiv reassoc ninf nsz <2 x float> %2375, %2395
  %2397 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2396, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2398 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2397, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2399 = fadd reassoc ninf nsz <2 x float> %2398, %2353
  %2400 = fadd reassoc ninf nsz float %.45.ph, 1.000000e+00
  br label %true_block562

true_block562:                                    ; preds = %true_block559, %true_block553, %true_block550
  %.46.ph = phi float [ %.45.ph, %true_block550 ], [ %.45.ph, %true_block553 ], [ %2400, %true_block559 ]
  %2401 = phi <2 x float> [ %2353, %true_block550 ], [ %2353, %true_block553 ], [ %2399, %true_block559 ]
  %2402 = icmp slt i32 %475, %2062
  br i1 %2402, label %true_block565, label %after_if567

true_block565:                                    ; preds = %true_block562
  %2403 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 1
  %2404 = load float*, float** %2403, align 8
  %2405 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 1
  %2406 = load i32, i32* %2405, align 4
  %2407 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 0, i32 0, i32 2
  %2408 = load i32, i32* %2407, align 4
  %2409 = mul i32 %2406, %2051
  %2410 = add i32 %2409, %475
  %2411 = mul i32 %2410, %2408
  %2412 = add i32 %2411, 1
  %2413 = sext i32 %2412 to i64
  %2414 = getelementptr float, float* %2404, i64 %2413
  %2415 = load float, float* %2414, align 4
  %2416 = add i32 %2411, 2
  %2417 = insertelement <2 x i32> poison, i32 %2411, i64 0
  %2418 = insertelement <2 x i32> %2417, i32 %2416, i64 1
  %2419 = sext <2 x i32> %2418 to <2 x i64>
  %2420 = insertelement <2 x float*> poison, float* %2404, i64 0
  %2421 = shufflevector <2 x float*> %2420, <2 x float*> poison, <2 x i32> zeroinitializer
  %2422 = getelementptr float, <2 x float*> %2421, <2 x i64> %2419
  %2423 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2422, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2424 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 2
  %2425 = load float, float* %2424, align 4
  %2426 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2425, float 0x3F1A36E2E0000000)
  %2427 = extractelement <2 x float> %2423, i64 0
  %2428 = fdiv reassoc ninf nsz float %2427, %2426
  %2429 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 3
  %2430 = load float, float* %2429, align 4
  %2431 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2430, float 0x3F1A36E2E0000000)
  %2432 = fdiv reassoc ninf nsz float %2415, %2431
  %2433 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2060, i64 0, i32 4
  %2434 = load float, float* %2433, align 4
  %2435 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2434, float 0x3F1A36E2E0000000)
  %2436 = extractelement <2 x float> %2423, i64 1
  %2437 = fdiv reassoc ninf nsz float %2436, %2435
  %2438 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2432, float %2437)
  %2439 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2428, float %2438)
  %2440 = fcmp reassoc ninf nsz olt float %2439, 0x3FED70A3E0000000
  %2441 = fcmp reassoc ninf nsz ogt float %2415, 0x3EE4F8B580000000
  %.0354 = select i1 %2440, i1 %2441, i1 false
  br i1 %.0354, label %true_block571, label %after_if567

after_if567:                                      ; preds = %true_block571, %true_block565, %true_block562, %after_if471
  %.47 = phi float [ %2451, %true_block571 ], [ %.46.ph, %true_block565 ], [ %.46.ph, %true_block562 ], [ %.39, %after_if471 ]
  %2442 = phi <2 x float> [ %2450, %true_block571 ], [ %2401, %true_block565 ], [ %2401, %true_block562 ], [ %2050, %after_if471 ]
  %2443 = or i32 %47, 6
  %2444 = icmp slt i32 %2443, %23
  br i1 %2444, label %true_block574, label %after_if663

true_block571:                                    ; preds = %true_block565
  %2445 = insertelement <2 x float> poison, float %2415, i64 0
  %2446 = shufflevector <2 x float> %2445, <2 x float> poison, <2 x i32> zeroinitializer
  %2447 = fdiv reassoc ninf nsz <2 x float> %2423, %2446
  %2448 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2447, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2449 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2448, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2450 = fadd reassoc ninf nsz <2 x float> %2449, %2401
  %2451 = fadd reassoc ninf nsz float %.46.ph, 1.000000e+00
  br label %after_if567

true_block574:                                    ; preds = %after_if567
  %2452 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %2453 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 6
  %2454 = load i32, i32* %2453, align 4
  %2455 = icmp slt i32 %52, %2454
  br i1 %2455, label %true_block577, label %true_block586

true_block577:                                    ; preds = %true_block574
  %2456 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2457 = load float*, float** %2456, align 8
  %2458 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2459 = load i32, i32* %2458, align 4
  %2460 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2461 = load i32, i32* %2460, align 4
  %2462 = mul i32 %2459, %2443
  %2463 = shl i32 %35, 3
  %2464 = mul i32 %2463, %44
  %2465 = sub i32 %2462, %2464
  %2466 = add i32 %lsr.iv, %2465
  %2467 = add i32 %2466, -7
  %2468 = mul i32 %2467, %2461
  %2469 = sext i32 %2468 to i64
  %2470 = getelementptr float, float* %2457, i64 %2469
  %2471 = load float, float* %2470, align 4
  %2472 = or i32 %2468, 1
  %2473 = sext i32 %2472 to i64
  %2474 = getelementptr float, float* %2457, i64 %2473
  %2475 = load float, float* %2474, align 4
  %2476 = add i32 %2468, 2
  %2477 = sext i32 %2476 to i64
  %2478 = getelementptr float, float* %2457, i64 %2477
  %2479 = load float, float* %2478, align 4
  %2480 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2481 = load float, float* %2480, align 4
  %2482 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2481, float 0x3F1A36E2E0000000)
  %2483 = fdiv reassoc ninf nsz float %2471, %2482
  %2484 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2485 = load float, float* %2484, align 4
  %2486 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2485, float 0x3F1A36E2E0000000)
  %2487 = fdiv reassoc ninf nsz float %2475, %2486
  %2488 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2489 = load float, float* %2488, align 4
  %2490 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2489, float 0x3F1A36E2E0000000)
  %2491 = fdiv reassoc ninf nsz float %2479, %2490
  %2492 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2487, float %2491)
  %2493 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2483, float %2492)
  %2494 = fcmp reassoc ninf nsz olt float %2493, 0x3FED70A3E0000000
  %2495 = fcmp reassoc ninf nsz ogt float %2475, 0x3EE4F8B580000000
  %.0352 = select i1 %2494, i1 %2495, i1 false
  br i1 %.0352, label %true_block583, label %true_block586

true_block583:                                    ; preds = %true_block577
  %2496 = insertelement <2 x float> poison, float %2471, i64 0
  %2497 = insertelement <2 x float> %2496, float %2479, i64 1
  %2498 = insertelement <2 x float> poison, float %2475, i64 0
  %2499 = shufflevector <2 x float> %2498, <2 x float> poison, <2 x i32> zeroinitializer
  %2500 = fdiv reassoc ninf nsz <2 x float> %2497, %2499
  %2501 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2500, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2502 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2501, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2503 = fadd reassoc ninf nsz <2 x float> %2502, %2442
  %2504 = fadd reassoc ninf nsz float %.47, 1.000000e+00
  br label %true_block586

true_block586:                                    ; preds = %true_block583, %true_block577, %true_block574
  %.48.ph = phi float [ %.47, %true_block574 ], [ %.47, %true_block577 ], [ %2504, %true_block583 ]
  %2505 = phi <2 x float> [ %2442, %true_block574 ], [ %2442, %true_block577 ], [ %2503, %true_block583 ]
  %2506 = icmp slt i32 %478, %2454
  br i1 %2506, label %true_block589, label %true_block598

true_block589:                                    ; preds = %true_block586
  %2507 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2508 = load float*, float** %2507, align 8
  %2509 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2510 = load i32, i32* %2509, align 4
  %2511 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2512 = load i32, i32* %2511, align 4
  %2513 = mul i32 %2510, %2443
  %2514 = add i32 %2513, %478
  %2515 = mul i32 %2514, %2512
  %2516 = sext i32 %2515 to i64
  %2517 = getelementptr float, float* %2508, i64 %2516
  %2518 = add i32 %2515, 1
  %2519 = sext i32 %2518 to i64
  %2520 = getelementptr float, float* %2508, i64 %2519
  %2521 = load float, float* %2520, align 4
  %2522 = add i32 %2515, 2
  %2523 = sext i32 %2522 to i64
  %2524 = getelementptr float, float* %2508, i64 %2523
  %2525 = insertelement <2 x float*> poison, float* %2517, i64 0
  %2526 = insertelement <2 x float*> %2525, float* %2524, i64 1
  %2527 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2526, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2528 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2529 = load float, float* %2528, align 4
  %2530 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2529, float 0x3F1A36E2E0000000)
  %2531 = extractelement <2 x float> %2527, i64 0
  %2532 = fdiv reassoc ninf nsz float %2531, %2530
  %2533 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2534 = load float, float* %2533, align 4
  %2535 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2534, float 0x3F1A36E2E0000000)
  %2536 = fdiv reassoc ninf nsz float %2521, %2535
  %2537 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2538 = load float, float* %2537, align 4
  %2539 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2538, float 0x3F1A36E2E0000000)
  %2540 = extractelement <2 x float> %2527, i64 1
  %2541 = fdiv reassoc ninf nsz float %2540, %2539
  %2542 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2536, float %2541)
  %2543 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2532, float %2542)
  %2544 = fcmp reassoc ninf nsz olt float %2543, 0x3FED70A3E0000000
  %2545 = fcmp reassoc ninf nsz ogt float %2521, 0x3EE4F8B580000000
  %.0350 = select i1 %2544, i1 %2545, i1 false
  br i1 %.0350, label %true_block595, label %true_block598

true_block595:                                    ; preds = %true_block589
  %2546 = insertelement <2 x float> poison, float %2521, i64 0
  %2547 = shufflevector <2 x float> %2546, <2 x float> poison, <2 x i32> zeroinitializer
  %2548 = fdiv reassoc ninf nsz <2 x float> %2527, %2547
  %2549 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2548, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2550 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2549, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2551 = fadd reassoc ninf nsz <2 x float> %2550, %2505
  %2552 = fadd reassoc ninf nsz float %.48.ph, 1.000000e+00
  br label %true_block598

true_block598:                                    ; preds = %true_block595, %true_block589, %true_block586
  %.49.ph = phi float [ %.48.ph, %true_block586 ], [ %.48.ph, %true_block589 ], [ %2552, %true_block595 ]
  %2553 = phi <2 x float> [ %2505, %true_block586 ], [ %2505, %true_block589 ], [ %2551, %true_block595 ]
  %2554 = icmp slt i32 %479, %2454
  br i1 %2554, label %true_block601, label %true_block610

true_block601:                                    ; preds = %true_block598
  %2555 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2556 = load float*, float** %2555, align 8
  %2557 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2558 = load i32, i32* %2557, align 4
  %2559 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2560 = load i32, i32* %2559, align 4
  %2561 = mul i32 %2558, %2443
  %2562 = add i32 %2561, %479
  %2563 = mul i32 %2562, %2560
  %2564 = or i32 %2563, 1
  %2565 = sext i32 %2564 to i64
  %2566 = getelementptr float, float* %2556, i64 %2565
  %2567 = load float, float* %2566, align 4
  %2568 = add i32 %2563, 2
  %2569 = insertelement <2 x i32> poison, i32 %2563, i64 0
  %2570 = insertelement <2 x i32> %2569, i32 %2568, i64 1
  %2571 = sext <2 x i32> %2570 to <2 x i64>
  %2572 = insertelement <2 x float*> poison, float* %2556, i64 0
  %2573 = shufflevector <2 x float*> %2572, <2 x float*> poison, <2 x i32> zeroinitializer
  %2574 = getelementptr float, <2 x float*> %2573, <2 x i64> %2571
  %2575 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2574, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2576 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2577 = load float, float* %2576, align 4
  %2578 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2577, float 0x3F1A36E2E0000000)
  %2579 = extractelement <2 x float> %2575, i64 0
  %2580 = fdiv reassoc ninf nsz float %2579, %2578
  %2581 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2582 = load float, float* %2581, align 4
  %2583 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2582, float 0x3F1A36E2E0000000)
  %2584 = fdiv reassoc ninf nsz float %2567, %2583
  %2585 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2586 = load float, float* %2585, align 4
  %2587 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2586, float 0x3F1A36E2E0000000)
  %2588 = extractelement <2 x float> %2575, i64 1
  %2589 = fdiv reassoc ninf nsz float %2588, %2587
  %2590 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2584, float %2589)
  %2591 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2580, float %2590)
  %2592 = fcmp reassoc ninf nsz olt float %2591, 0x3FED70A3E0000000
  %2593 = fcmp reassoc ninf nsz ogt float %2567, 0x3EE4F8B580000000
  %.0348 = select i1 %2592, i1 %2593, i1 false
  br i1 %.0348, label %true_block607, label %true_block610

true_block607:                                    ; preds = %true_block601
  %2594 = insertelement <2 x float> poison, float %2567, i64 0
  %2595 = shufflevector <2 x float> %2594, <2 x float> poison, <2 x i32> zeroinitializer
  %2596 = fdiv reassoc ninf nsz <2 x float> %2575, %2595
  %2597 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2596, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2598 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2597, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2599 = fadd reassoc ninf nsz <2 x float> %2598, %2553
  %2600 = fadd reassoc ninf nsz float %.49.ph, 1.000000e+00
  br label %true_block610

true_block610:                                    ; preds = %true_block607, %true_block601, %true_block598
  %.50.ph = phi float [ %.49.ph, %true_block598 ], [ %.49.ph, %true_block601 ], [ %2600, %true_block607 ]
  %2601 = phi <2 x float> [ %2553, %true_block598 ], [ %2553, %true_block601 ], [ %2599, %true_block607 ]
  %2602 = icmp slt i32 %477, %2454
  br i1 %2602, label %true_block613, label %true_block622

true_block613:                                    ; preds = %true_block610
  %2603 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2604 = load float*, float** %2603, align 8
  %2605 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2606 = load i32, i32* %2605, align 4
  %2607 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2608 = load i32, i32* %2607, align 4
  %2609 = mul i32 %2606, %2443
  %2610 = add i32 %2609, %477
  %2611 = mul i32 %2610, %2608
  %2612 = add i32 %2611, 1
  %2613 = sext i32 %2612 to i64
  %2614 = getelementptr float, float* %2604, i64 %2613
  %2615 = load float, float* %2614, align 4
  %2616 = add i32 %2611, 2
  %2617 = insertelement <2 x i32> poison, i32 %2611, i64 0
  %2618 = insertelement <2 x i32> %2617, i32 %2616, i64 1
  %2619 = sext <2 x i32> %2618 to <2 x i64>
  %2620 = insertelement <2 x float*> poison, float* %2604, i64 0
  %2621 = shufflevector <2 x float*> %2620, <2 x float*> poison, <2 x i32> zeroinitializer
  %2622 = getelementptr float, <2 x float*> %2621, <2 x i64> %2619
  %2623 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2622, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2624 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2625 = load float, float* %2624, align 4
  %2626 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2625, float 0x3F1A36E2E0000000)
  %2627 = extractelement <2 x float> %2623, i64 0
  %2628 = fdiv reassoc ninf nsz float %2627, %2626
  %2629 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2630 = load float, float* %2629, align 4
  %2631 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2630, float 0x3F1A36E2E0000000)
  %2632 = fdiv reassoc ninf nsz float %2615, %2631
  %2633 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2634 = load float, float* %2633, align 4
  %2635 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2634, float 0x3F1A36E2E0000000)
  %2636 = extractelement <2 x float> %2623, i64 1
  %2637 = fdiv reassoc ninf nsz float %2636, %2635
  %2638 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2632, float %2637)
  %2639 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2628, float %2638)
  %2640 = fcmp reassoc ninf nsz olt float %2639, 0x3FED70A3E0000000
  %2641 = fcmp reassoc ninf nsz ogt float %2615, 0x3EE4F8B580000000
  %.0346 = select i1 %2640, i1 %2641, i1 false
  br i1 %.0346, label %true_block619, label %true_block622

true_block619:                                    ; preds = %true_block613
  %2642 = insertelement <2 x float> poison, float %2615, i64 0
  %2643 = shufflevector <2 x float> %2642, <2 x float> poison, <2 x i32> zeroinitializer
  %2644 = fdiv reassoc ninf nsz <2 x float> %2623, %2643
  %2645 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2644, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2646 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2645, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2647 = fadd reassoc ninf nsz <2 x float> %2646, %2601
  %2648 = fadd reassoc ninf nsz float %.50.ph, 1.000000e+00
  br label %true_block622

true_block622:                                    ; preds = %true_block619, %true_block613, %true_block610
  %.51.ph = phi float [ %.50.ph, %true_block610 ], [ %.50.ph, %true_block613 ], [ %2648, %true_block619 ]
  %2649 = phi <2 x float> [ %2601, %true_block610 ], [ %2601, %true_block613 ], [ %2647, %true_block619 ]
  %2650 = icmp slt i32 %480, %2454
  br i1 %2650, label %true_block625, label %true_block634

true_block625:                                    ; preds = %true_block622
  %2651 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2652 = load float*, float** %2651, align 8
  %2653 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2654 = load i32, i32* %2653, align 4
  %2655 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2656 = load i32, i32* %2655, align 4
  %2657 = mul i32 %2654, %2443
  %2658 = add i32 %2657, %480
  %2659 = mul i32 %2658, %2656
  %2660 = or i32 %2659, 1
  %2661 = sext i32 %2660 to i64
  %2662 = getelementptr float, float* %2652, i64 %2661
  %2663 = load float, float* %2662, align 4
  %2664 = add i32 %2659, 2
  %2665 = insertelement <2 x i32> poison, i32 %2659, i64 0
  %2666 = insertelement <2 x i32> %2665, i32 %2664, i64 1
  %2667 = sext <2 x i32> %2666 to <2 x i64>
  %2668 = insertelement <2 x float*> poison, float* %2652, i64 0
  %2669 = shufflevector <2 x float*> %2668, <2 x float*> poison, <2 x i32> zeroinitializer
  %2670 = getelementptr float, <2 x float*> %2669, <2 x i64> %2667
  %2671 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2670, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2672 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2673 = load float, float* %2672, align 4
  %2674 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2673, float 0x3F1A36E2E0000000)
  %2675 = extractelement <2 x float> %2671, i64 0
  %2676 = fdiv reassoc ninf nsz float %2675, %2674
  %2677 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2678 = load float, float* %2677, align 4
  %2679 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2678, float 0x3F1A36E2E0000000)
  %2680 = fdiv reassoc ninf nsz float %2663, %2679
  %2681 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2682 = load float, float* %2681, align 4
  %2683 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2682, float 0x3F1A36E2E0000000)
  %2684 = extractelement <2 x float> %2671, i64 1
  %2685 = fdiv reassoc ninf nsz float %2684, %2683
  %2686 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2680, float %2685)
  %2687 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2676, float %2686)
  %2688 = fcmp reassoc ninf nsz olt float %2687, 0x3FED70A3E0000000
  %2689 = fcmp reassoc ninf nsz ogt float %2663, 0x3EE4F8B580000000
  %.0344 = select i1 %2688, i1 %2689, i1 false
  br i1 %.0344, label %true_block631, label %true_block634

true_block631:                                    ; preds = %true_block625
  %2690 = insertelement <2 x float> poison, float %2663, i64 0
  %2691 = shufflevector <2 x float> %2690, <2 x float> poison, <2 x i32> zeroinitializer
  %2692 = fdiv reassoc ninf nsz <2 x float> %2671, %2691
  %2693 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2692, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2694 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2693, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2695 = fadd reassoc ninf nsz <2 x float> %2694, %2649
  %2696 = fadd reassoc ninf nsz float %.51.ph, 1.000000e+00
  br label %true_block634

true_block634:                                    ; preds = %true_block631, %true_block625, %true_block622
  %.52.ph = phi float [ %.51.ph, %true_block622 ], [ %.51.ph, %true_block625 ], [ %2696, %true_block631 ]
  %2697 = phi <2 x float> [ %2649, %true_block622 ], [ %2649, %true_block625 ], [ %2695, %true_block631 ]
  %2698 = icmp slt i32 %476, %2454
  br i1 %2698, label %true_block637, label %true_block646

true_block637:                                    ; preds = %true_block634
  %2699 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2700 = load float*, float** %2699, align 8
  %2701 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2702 = load i32, i32* %2701, align 4
  %2703 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2704 = load i32, i32* %2703, align 4
  %2705 = mul i32 %2702, %2443
  %2706 = add i32 %2705, %476
  %2707 = mul i32 %2706, %2704
  %2708 = add i32 %2707, 1
  %2709 = sext i32 %2708 to i64
  %2710 = getelementptr float, float* %2700, i64 %2709
  %2711 = load float, float* %2710, align 4
  %2712 = add i32 %2707, 2
  %2713 = insertelement <2 x i32> poison, i32 %2707, i64 0
  %2714 = insertelement <2 x i32> %2713, i32 %2712, i64 1
  %2715 = sext <2 x i32> %2714 to <2 x i64>
  %2716 = insertelement <2 x float*> poison, float* %2700, i64 0
  %2717 = shufflevector <2 x float*> %2716, <2 x float*> poison, <2 x i32> zeroinitializer
  %2718 = getelementptr float, <2 x float*> %2717, <2 x i64> %2715
  %2719 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2718, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2720 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2721 = load float, float* %2720, align 4
  %2722 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2721, float 0x3F1A36E2E0000000)
  %2723 = extractelement <2 x float> %2719, i64 0
  %2724 = fdiv reassoc ninf nsz float %2723, %2722
  %2725 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2726 = load float, float* %2725, align 4
  %2727 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2726, float 0x3F1A36E2E0000000)
  %2728 = fdiv reassoc ninf nsz float %2711, %2727
  %2729 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2730 = load float, float* %2729, align 4
  %2731 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2730, float 0x3F1A36E2E0000000)
  %2732 = extractelement <2 x float> %2719, i64 1
  %2733 = fdiv reassoc ninf nsz float %2732, %2731
  %2734 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2728, float %2733)
  %2735 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2724, float %2734)
  %2736 = fcmp reassoc ninf nsz olt float %2735, 0x3FED70A3E0000000
  %2737 = fcmp reassoc ninf nsz ogt float %2711, 0x3EE4F8B580000000
  %.0342 = select i1 %2736, i1 %2737, i1 false
  br i1 %.0342, label %true_block643, label %true_block646

true_block643:                                    ; preds = %true_block637
  %2738 = insertelement <2 x float> poison, float %2711, i64 0
  %2739 = shufflevector <2 x float> %2738, <2 x float> poison, <2 x i32> zeroinitializer
  %2740 = fdiv reassoc ninf nsz <2 x float> %2719, %2739
  %2741 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2740, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2742 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2741, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2743 = fadd reassoc ninf nsz <2 x float> %2742, %2697
  %2744 = fadd reassoc ninf nsz float %.52.ph, 1.000000e+00
  br label %true_block646

true_block646:                                    ; preds = %true_block643, %true_block637, %true_block634
  %.53.ph = phi float [ %.52.ph, %true_block634 ], [ %.52.ph, %true_block637 ], [ %2744, %true_block643 ]
  %2745 = phi <2 x float> [ %2697, %true_block634 ], [ %2697, %true_block637 ], [ %2743, %true_block643 ]
  %2746 = icmp slt i32 %481, %2454
  br i1 %2746, label %true_block649, label %true_block658

true_block649:                                    ; preds = %true_block646
  %2747 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2748 = load float*, float** %2747, align 8
  %2749 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2750 = load i32, i32* %2749, align 4
  %2751 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2752 = load i32, i32* %2751, align 4
  %2753 = mul i32 %2750, %2443
  %2754 = add i32 %2753, %481
  %2755 = mul i32 %2754, %2752
  %2756 = or i32 %2755, 1
  %2757 = sext i32 %2756 to i64
  %2758 = getelementptr float, float* %2748, i64 %2757
  %2759 = load float, float* %2758, align 4
  %2760 = add i32 %2755, 2
  %2761 = insertelement <2 x i32> poison, i32 %2755, i64 0
  %2762 = insertelement <2 x i32> %2761, i32 %2760, i64 1
  %2763 = sext <2 x i32> %2762 to <2 x i64>
  %2764 = insertelement <2 x float*> poison, float* %2748, i64 0
  %2765 = shufflevector <2 x float*> %2764, <2 x float*> poison, <2 x i32> zeroinitializer
  %2766 = getelementptr float, <2 x float*> %2765, <2 x i64> %2763
  %2767 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2766, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2768 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2769 = load float, float* %2768, align 4
  %2770 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2769, float 0x3F1A36E2E0000000)
  %2771 = extractelement <2 x float> %2767, i64 0
  %2772 = fdiv reassoc ninf nsz float %2771, %2770
  %2773 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2774 = load float, float* %2773, align 4
  %2775 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2774, float 0x3F1A36E2E0000000)
  %2776 = fdiv reassoc ninf nsz float %2759, %2775
  %2777 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2778 = load float, float* %2777, align 4
  %2779 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2778, float 0x3F1A36E2E0000000)
  %2780 = extractelement <2 x float> %2767, i64 1
  %2781 = fdiv reassoc ninf nsz float %2780, %2779
  %2782 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2776, float %2781)
  %2783 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2772, float %2782)
  %2784 = fcmp reassoc ninf nsz olt float %2783, 0x3FED70A3E0000000
  %2785 = fcmp reassoc ninf nsz ogt float %2759, 0x3EE4F8B580000000
  %.0340 = select i1 %2784, i1 %2785, i1 false
  br i1 %.0340, label %true_block655, label %true_block658

true_block655:                                    ; preds = %true_block649
  %2786 = insertelement <2 x float> poison, float %2759, i64 0
  %2787 = shufflevector <2 x float> %2786, <2 x float> poison, <2 x i32> zeroinitializer
  %2788 = fdiv reassoc ninf nsz <2 x float> %2767, %2787
  %2789 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2788, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2790 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2789, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2791 = fadd reassoc ninf nsz <2 x float> %2790, %2745
  %2792 = fadd reassoc ninf nsz float %.53.ph, 1.000000e+00
  br label %true_block658

true_block658:                                    ; preds = %true_block655, %true_block649, %true_block646
  %.54.ph = phi float [ %.53.ph, %true_block646 ], [ %.53.ph, %true_block649 ], [ %2792, %true_block655 ]
  %2793 = phi <2 x float> [ %2745, %true_block646 ], [ %2745, %true_block649 ], [ %2791, %true_block655 ]
  %2794 = icmp slt i32 %475, %2454
  br i1 %2794, label %true_block661, label %after_if663

true_block661:                                    ; preds = %true_block658
  %2795 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 1
  %2796 = load float*, float** %2795, align 8
  %2797 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 1
  %2798 = load i32, i32* %2797, align 4
  %2799 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 0, i32 0, i32 2
  %2800 = load i32, i32* %2799, align 4
  %2801 = mul i32 %2798, %2443
  %2802 = add i32 %2801, %475
  %2803 = mul i32 %2802, %2800
  %2804 = add i32 %2803, 1
  %2805 = sext i32 %2804 to i64
  %2806 = getelementptr float, float* %2796, i64 %2805
  %2807 = load float, float* %2806, align 4
  %2808 = add i32 %2803, 2
  %2809 = insertelement <2 x i32> poison, i32 %2803, i64 0
  %2810 = insertelement <2 x i32> %2809, i32 %2808, i64 1
  %2811 = sext <2 x i32> %2810 to <2 x i64>
  %2812 = insertelement <2 x float*> poison, float* %2796, i64 0
  %2813 = shufflevector <2 x float*> %2812, <2 x float*> poison, <2 x i32> zeroinitializer
  %2814 = getelementptr float, <2 x float*> %2813, <2 x i64> %2811
  %2815 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2814, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2816 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 2
  %2817 = load float, float* %2816, align 4
  %2818 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2817, float 0x3F1A36E2E0000000)
  %2819 = extractelement <2 x float> %2815, i64 0
  %2820 = fdiv reassoc ninf nsz float %2819, %2818
  %2821 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 3
  %2822 = load float, float* %2821, align 4
  %2823 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2822, float 0x3F1A36E2E0000000)
  %2824 = fdiv reassoc ninf nsz float %2807, %2823
  %2825 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2452, i64 0, i32 4
  %2826 = load float, float* %2825, align 4
  %2827 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2826, float 0x3F1A36E2E0000000)
  %2828 = extractelement <2 x float> %2815, i64 1
  %2829 = fdiv reassoc ninf nsz float %2828, %2827
  %2830 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2824, float %2829)
  %2831 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2820, float %2830)
  %2832 = fcmp reassoc ninf nsz olt float %2831, 0x3FED70A3E0000000
  %2833 = fcmp reassoc ninf nsz ogt float %2807, 0x3EE4F8B580000000
  %.0338 = select i1 %2832, i1 %2833, i1 false
  br i1 %.0338, label %true_block667, label %after_if663

after_if663:                                      ; preds = %true_block667, %true_block661, %true_block658, %after_if567
  %.55 = phi float [ %2843, %true_block667 ], [ %.54.ph, %true_block661 ], [ %.54.ph, %true_block658 ], [ %.47, %after_if567 ]
  %2834 = phi <2 x float> [ %2842, %true_block667 ], [ %2793, %true_block661 ], [ %2793, %true_block658 ], [ %2442, %after_if567 ]
  %2835 = or i32 %47, 7
  %2836 = icmp slt i32 %2835, %23
  br i1 %2836, label %true_block670, label %after_if759

true_block667:                                    ; preds = %true_block661
  %2837 = insertelement <2 x float> poison, float %2807, i64 0
  %2838 = shufflevector <2 x float> %2837, <2 x float> poison, <2 x i32> zeroinitializer
  %2839 = fdiv reassoc ninf nsz <2 x float> %2815, %2838
  %2840 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2839, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2841 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2840, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2842 = fadd reassoc ninf nsz <2 x float> %2841, %2793
  %2843 = fadd reassoc ninf nsz float %.54.ph, 1.000000e+00
  br label %after_if663

true_block670:                                    ; preds = %after_if663
  %2844 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %2845 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 6
  %2846 = load i32, i32* %2845, align 4
  %2847 = icmp slt i32 %52, %2846
  br i1 %2847, label %true_block673, label %true_block682

true_block673:                                    ; preds = %true_block670
  %2848 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %2849 = load float*, float** %2848, align 8
  %2850 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %2851 = load i32, i32* %2850, align 4
  %2852 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %2853 = load i32, i32* %2852, align 4
  %2854 = mul i32 %2851, %2835
  %2855 = shl i32 %35, 3
  %2856 = mul i32 %2855, %44
  %2857 = sub i32 %2854, %2856
  %2858 = add i32 %lsr.iv, %2857
  %2859 = add i32 %2858, -7
  %2860 = mul i32 %2859, %2853
  %2861 = add i32 %2860, 1
  %2862 = sext i32 %2861 to i64
  %2863 = getelementptr float, float* %2849, i64 %2862
  %2864 = load float, float* %2863, align 4
  %2865 = add i32 %2860, 2
  %2866 = insertelement <2 x i32> poison, i32 %2860, i64 0
  %2867 = insertelement <2 x i32> %2866, i32 %2865, i64 1
  %2868 = sext <2 x i32> %2867 to <2 x i64>
  %2869 = insertelement <2 x float*> poison, float* %2849, i64 0
  %2870 = shufflevector <2 x float*> %2869, <2 x float*> poison, <2 x i32> zeroinitializer
  %2871 = getelementptr float, <2 x float*> %2870, <2 x i64> %2868
  %2872 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2871, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2873 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %2874 = load float, float* %2873, align 4
  %2875 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2874, float 0x3F1A36E2E0000000)
  %2876 = extractelement <2 x float> %2872, i64 0
  %2877 = fdiv reassoc ninf nsz float %2876, %2875
  %2878 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %2879 = load float, float* %2878, align 4
  %2880 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2879, float 0x3F1A36E2E0000000)
  %2881 = fdiv reassoc ninf nsz float %2864, %2880
  %2882 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %2883 = load float, float* %2882, align 4
  %2884 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2883, float 0x3F1A36E2E0000000)
  %2885 = extractelement <2 x float> %2872, i64 1
  %2886 = fdiv reassoc ninf nsz float %2885, %2884
  %2887 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2881, float %2886)
  %2888 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2877, float %2887)
  %2889 = fcmp reassoc ninf nsz olt float %2888, 0x3FED70A3E0000000
  %2890 = fcmp reassoc ninf nsz ogt float %2864, 0x3EE4F8B580000000
  %.0336 = select i1 %2889, i1 %2890, i1 false
  br i1 %.0336, label %true_block679, label %true_block682

true_block679:                                    ; preds = %true_block673
  %2891 = insertelement <2 x float> poison, float %2864, i64 0
  %2892 = shufflevector <2 x float> %2891, <2 x float> poison, <2 x i32> zeroinitializer
  %2893 = fdiv reassoc ninf nsz <2 x float> %2872, %2892
  %2894 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2893, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2895 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2894, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2896 = fadd reassoc ninf nsz <2 x float> %2895, %2834
  %2897 = fadd reassoc ninf nsz float %.55, 1.000000e+00
  br label %true_block682

true_block682:                                    ; preds = %true_block679, %true_block673, %true_block670
  %.56.ph = phi float [ %.55, %true_block670 ], [ %.55, %true_block673 ], [ %2897, %true_block679 ]
  %2898 = phi <2 x float> [ %2834, %true_block670 ], [ %2834, %true_block673 ], [ %2896, %true_block679 ]
  %2899 = icmp slt i32 %478, %2846
  br i1 %2899, label %true_block685, label %true_block694

true_block685:                                    ; preds = %true_block682
  %2900 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %2901 = load float*, float** %2900, align 8
  %2902 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %2903 = load i32, i32* %2902, align 4
  %2904 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %2905 = load i32, i32* %2904, align 4
  %2906 = mul i32 %2903, %2835
  %2907 = add i32 %2906, %478
  %2908 = mul i32 %2907, %2905
  %2909 = sext i32 %2908 to i64
  %2910 = getelementptr float, float* %2901, i64 %2909
  %2911 = load float, float* %2910, align 4
  %2912 = add i32 %2908, 1
  %2913 = sext i32 %2912 to i64
  %2914 = getelementptr float, float* %2901, i64 %2913
  %2915 = load float, float* %2914, align 4
  %2916 = add i32 %2908, 2
  %2917 = sext i32 %2916 to i64
  %2918 = getelementptr float, float* %2901, i64 %2917
  %2919 = load float, float* %2918, align 4
  %2920 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %2921 = load float, float* %2920, align 4
  %2922 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2921, float 0x3F1A36E2E0000000)
  %2923 = fdiv reassoc ninf nsz float %2911, %2922
  %2924 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %2925 = load float, float* %2924, align 4
  %2926 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2925, float 0x3F1A36E2E0000000)
  %2927 = fdiv reassoc ninf nsz float %2915, %2926
  %2928 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %2929 = load float, float* %2928, align 4
  %2930 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2929, float 0x3F1A36E2E0000000)
  %2931 = fdiv reassoc ninf nsz float %2919, %2930
  %2932 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2927, float %2931)
  %2933 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2923, float %2932)
  %2934 = fcmp reassoc ninf nsz olt float %2933, 0x3FED70A3E0000000
  %2935 = fcmp reassoc ninf nsz ogt float %2915, 0x3EE4F8B580000000
  %.0334 = select i1 %2934, i1 %2935, i1 false
  br i1 %.0334, label %true_block691, label %true_block694

true_block691:                                    ; preds = %true_block685
  %2936 = insertelement <2 x float> poison, float %2911, i64 0
  %2937 = insertelement <2 x float> %2936, float %2919, i64 1
  %2938 = insertelement <2 x float> poison, float %2915, i64 0
  %2939 = shufflevector <2 x float> %2938, <2 x float> poison, <2 x i32> zeroinitializer
  %2940 = fdiv reassoc ninf nsz <2 x float> %2937, %2939
  %2941 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2940, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2942 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2941, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2943 = fadd reassoc ninf nsz <2 x float> %2942, %2898
  %2944 = fadd reassoc ninf nsz float %.56.ph, 1.000000e+00
  br label %true_block694

true_block694:                                    ; preds = %true_block691, %true_block685, %true_block682
  %.57.ph = phi float [ %.56.ph, %true_block682 ], [ %.56.ph, %true_block685 ], [ %2944, %true_block691 ]
  %2945 = phi <2 x float> [ %2898, %true_block682 ], [ %2898, %true_block685 ], [ %2943, %true_block691 ]
  %2946 = icmp slt i32 %479, %2846
  br i1 %2946, label %true_block697, label %true_block706

true_block697:                                    ; preds = %true_block694
  %2947 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %2948 = load float*, float** %2947, align 8
  %2949 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %2950 = load i32, i32* %2949, align 4
  %2951 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %2952 = load i32, i32* %2951, align 4
  %2953 = mul i32 %2950, %2835
  %2954 = add i32 %2953, %479
  %2955 = mul i32 %2954, %2952
  %2956 = sext i32 %2955 to i64
  %2957 = getelementptr float, float* %2948, i64 %2956
  %2958 = add i32 %2955, 1
  %2959 = sext i32 %2958 to i64
  %2960 = getelementptr float, float* %2948, i64 %2959
  %2961 = load float, float* %2960, align 4
  %2962 = add i32 %2955, 2
  %2963 = sext i32 %2962 to i64
  %2964 = getelementptr float, float* %2948, i64 %2963
  %2965 = insertelement <2 x float*> poison, float* %2957, i64 0
  %2966 = insertelement <2 x float*> %2965, float* %2964, i64 1
  %2967 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %2966, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %2968 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %2969 = load float, float* %2968, align 4
  %2970 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2969, float 0x3F1A36E2E0000000)
  %2971 = extractelement <2 x float> %2967, i64 0
  %2972 = fdiv reassoc ninf nsz float %2971, %2970
  %2973 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %2974 = load float, float* %2973, align 4
  %2975 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2974, float 0x3F1A36E2E0000000)
  %2976 = fdiv reassoc ninf nsz float %2961, %2975
  %2977 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %2978 = load float, float* %2977, align 4
  %2979 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2978, float 0x3F1A36E2E0000000)
  %2980 = extractelement <2 x float> %2967, i64 1
  %2981 = fdiv reassoc ninf nsz float %2980, %2979
  %2982 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2976, float %2981)
  %2983 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %2972, float %2982)
  %2984 = fcmp reassoc ninf nsz olt float %2983, 0x3FED70A3E0000000
  %2985 = fcmp reassoc ninf nsz ogt float %2961, 0x3EE4F8B580000000
  %.0332 = select i1 %2984, i1 %2985, i1 false
  br i1 %.0332, label %true_block703, label %true_block706

true_block703:                                    ; preds = %true_block697
  %2986 = insertelement <2 x float> poison, float %2961, i64 0
  %2987 = shufflevector <2 x float> %2986, <2 x float> poison, <2 x i32> zeroinitializer
  %2988 = fdiv reassoc ninf nsz <2 x float> %2967, %2987
  %2989 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %2988, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %2990 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %2989, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %2991 = fadd reassoc ninf nsz <2 x float> %2990, %2945
  %2992 = fadd reassoc ninf nsz float %.57.ph, 1.000000e+00
  br label %true_block706

true_block706:                                    ; preds = %true_block703, %true_block697, %true_block694
  %.58.ph = phi float [ %.57.ph, %true_block694 ], [ %.57.ph, %true_block697 ], [ %2992, %true_block703 ]
  %2993 = phi <2 x float> [ %2945, %true_block694 ], [ %2945, %true_block697 ], [ %2991, %true_block703 ]
  %2994 = icmp slt i32 %477, %2846
  br i1 %2994, label %true_block709, label %true_block718

true_block709:                                    ; preds = %true_block706
  %2995 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %2996 = load float*, float** %2995, align 8
  %2997 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %2998 = load i32, i32* %2997, align 4
  %2999 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %3000 = load i32, i32* %2999, align 4
  %3001 = mul i32 %2998, %2835
  %3002 = add i32 %3001, %477
  %3003 = mul i32 %3002, %3000
  %3004 = add i32 %3003, 1
  %3005 = sext i32 %3004 to i64
  %3006 = getelementptr float, float* %2996, i64 %3005
  %3007 = load float, float* %3006, align 4
  %3008 = add i32 %3003, 2
  %3009 = insertelement <2 x i32> poison, i32 %3003, i64 0
  %3010 = insertelement <2 x i32> %3009, i32 %3008, i64 1
  %3011 = sext <2 x i32> %3010 to <2 x i64>
  %3012 = insertelement <2 x float*> poison, float* %2996, i64 0
  %3013 = shufflevector <2 x float*> %3012, <2 x float*> poison, <2 x i32> zeroinitializer
  %3014 = getelementptr float, <2 x float*> %3013, <2 x i64> %3011
  %3015 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %3014, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %3016 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %3017 = load float, float* %3016, align 4
  %3018 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3017, float 0x3F1A36E2E0000000)
  %3019 = extractelement <2 x float> %3015, i64 0
  %3020 = fdiv reassoc ninf nsz float %3019, %3018
  %3021 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %3022 = load float, float* %3021, align 4
  %3023 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3022, float 0x3F1A36E2E0000000)
  %3024 = fdiv reassoc ninf nsz float %3007, %3023
  %3025 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %3026 = load float, float* %3025, align 4
  %3027 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3026, float 0x3F1A36E2E0000000)
  %3028 = extractelement <2 x float> %3015, i64 1
  %3029 = fdiv reassoc ninf nsz float %3028, %3027
  %3030 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3024, float %3029)
  %3031 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3020, float %3030)
  %3032 = fcmp reassoc ninf nsz olt float %3031, 0x3FED70A3E0000000
  %3033 = fcmp reassoc ninf nsz ogt float %3007, 0x3EE4F8B580000000
  %.0330 = select i1 %3032, i1 %3033, i1 false
  br i1 %.0330, label %true_block715, label %true_block718

true_block715:                                    ; preds = %true_block709
  %3034 = insertelement <2 x float> poison, float %3007, i64 0
  %3035 = shufflevector <2 x float> %3034, <2 x float> poison, <2 x i32> zeroinitializer
  %3036 = fdiv reassoc ninf nsz <2 x float> %3015, %3035
  %3037 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %3036, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %3038 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %3037, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %3039 = fadd reassoc ninf nsz <2 x float> %3038, %2993
  %3040 = fadd reassoc ninf nsz float %.58.ph, 1.000000e+00
  br label %true_block718

true_block718:                                    ; preds = %true_block715, %true_block709, %true_block706
  %.59.ph = phi float [ %.58.ph, %true_block706 ], [ %.58.ph, %true_block709 ], [ %3040, %true_block715 ]
  %3041 = phi <2 x float> [ %2993, %true_block706 ], [ %2993, %true_block709 ], [ %3039, %true_block715 ]
  %3042 = icmp slt i32 %480, %2846
  br i1 %3042, label %true_block721, label %true_block730

true_block721:                                    ; preds = %true_block718
  %3043 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %3044 = load float*, float** %3043, align 8
  %3045 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %3046 = load i32, i32* %3045, align 4
  %3047 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %3048 = load i32, i32* %3047, align 4
  %3049 = mul i32 %3046, %2835
  %3050 = add i32 %3049, %480
  %3051 = mul i32 %3050, %3048
  %3052 = add i32 %3051, 1
  %3053 = sext i32 %3052 to i64
  %3054 = getelementptr float, float* %3044, i64 %3053
  %3055 = load float, float* %3054, align 4
  %3056 = add i32 %3051, 2
  %3057 = insertelement <2 x i32> poison, i32 %3051, i64 0
  %3058 = insertelement <2 x i32> %3057, i32 %3056, i64 1
  %3059 = sext <2 x i32> %3058 to <2 x i64>
  %3060 = insertelement <2 x float*> poison, float* %3044, i64 0
  %3061 = shufflevector <2 x float*> %3060, <2 x float*> poison, <2 x i32> zeroinitializer
  %3062 = getelementptr float, <2 x float*> %3061, <2 x i64> %3059
  %3063 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %3062, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %3064 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %3065 = load float, float* %3064, align 4
  %3066 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3065, float 0x3F1A36E2E0000000)
  %3067 = extractelement <2 x float> %3063, i64 0
  %3068 = fdiv reassoc ninf nsz float %3067, %3066
  %3069 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %3070 = load float, float* %3069, align 4
  %3071 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3070, float 0x3F1A36E2E0000000)
  %3072 = fdiv reassoc ninf nsz float %3055, %3071
  %3073 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %3074 = load float, float* %3073, align 4
  %3075 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3074, float 0x3F1A36E2E0000000)
  %3076 = extractelement <2 x float> %3063, i64 1
  %3077 = fdiv reassoc ninf nsz float %3076, %3075
  %3078 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3072, float %3077)
  %3079 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3068, float %3078)
  %3080 = fcmp reassoc ninf nsz olt float %3079, 0x3FED70A3E0000000
  %3081 = fcmp reassoc ninf nsz ogt float %3055, 0x3EE4F8B580000000
  %.0328 = select i1 %3080, i1 %3081, i1 false
  br i1 %.0328, label %true_block727, label %true_block730

true_block727:                                    ; preds = %true_block721
  %3082 = insertelement <2 x float> poison, float %3055, i64 0
  %3083 = shufflevector <2 x float> %3082, <2 x float> poison, <2 x i32> zeroinitializer
  %3084 = fdiv reassoc ninf nsz <2 x float> %3063, %3083
  %3085 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %3084, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %3086 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %3085, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %3087 = fadd reassoc ninf nsz <2 x float> %3086, %3041
  %3088 = fadd reassoc ninf nsz float %.59.ph, 1.000000e+00
  br label %true_block730

true_block730:                                    ; preds = %true_block727, %true_block721, %true_block718
  %.60.ph = phi float [ %.59.ph, %true_block718 ], [ %.59.ph, %true_block721 ], [ %3088, %true_block727 ]
  %3089 = phi <2 x float> [ %3041, %true_block718 ], [ %3041, %true_block721 ], [ %3087, %true_block727 ]
  %3090 = icmp slt i32 %476, %2846
  br i1 %3090, label %true_block733, label %true_block742

true_block733:                                    ; preds = %true_block730
  %3091 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %3092 = load float*, float** %3091, align 8
  %3093 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %3094 = load i32, i32* %3093, align 4
  %3095 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %3096 = load i32, i32* %3095, align 4
  %3097 = mul i32 %3094, %2835
  %3098 = add i32 %3097, %476
  %3099 = mul i32 %3098, %3096
  %3100 = add i32 %3099, 1
  %3101 = sext i32 %3100 to i64
  %3102 = getelementptr float, float* %3092, i64 %3101
  %3103 = load float, float* %3102, align 4
  %3104 = add i32 %3099, 2
  %3105 = insertelement <2 x i32> poison, i32 %3099, i64 0
  %3106 = insertelement <2 x i32> %3105, i32 %3104, i64 1
  %3107 = sext <2 x i32> %3106 to <2 x i64>
  %3108 = insertelement <2 x float*> poison, float* %3092, i64 0
  %3109 = shufflevector <2 x float*> %3108, <2 x float*> poison, <2 x i32> zeroinitializer
  %3110 = getelementptr float, <2 x float*> %3109, <2 x i64> %3107
  %3111 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %3110, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %3112 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %3113 = load float, float* %3112, align 4
  %3114 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3113, float 0x3F1A36E2E0000000)
  %3115 = extractelement <2 x float> %3111, i64 0
  %3116 = fdiv reassoc ninf nsz float %3115, %3114
  %3117 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %3118 = load float, float* %3117, align 4
  %3119 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3118, float 0x3F1A36E2E0000000)
  %3120 = fdiv reassoc ninf nsz float %3103, %3119
  %3121 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %3122 = load float, float* %3121, align 4
  %3123 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3122, float 0x3F1A36E2E0000000)
  %3124 = extractelement <2 x float> %3111, i64 1
  %3125 = fdiv reassoc ninf nsz float %3124, %3123
  %3126 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3120, float %3125)
  %3127 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3116, float %3126)
  %3128 = fcmp reassoc ninf nsz olt float %3127, 0x3FED70A3E0000000
  %3129 = fcmp reassoc ninf nsz ogt float %3103, 0x3EE4F8B580000000
  %.0326 = select i1 %3128, i1 %3129, i1 false
  br i1 %.0326, label %true_block739, label %true_block742

true_block739:                                    ; preds = %true_block733
  %3130 = insertelement <2 x float> poison, float %3103, i64 0
  %3131 = shufflevector <2 x float> %3130, <2 x float> poison, <2 x i32> zeroinitializer
  %3132 = fdiv reassoc ninf nsz <2 x float> %3111, %3131
  %3133 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %3132, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %3134 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %3133, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %3135 = fadd reassoc ninf nsz <2 x float> %3134, %3089
  %3136 = fadd reassoc ninf nsz float %.60.ph, 1.000000e+00
  br label %true_block742

true_block742:                                    ; preds = %true_block739, %true_block733, %true_block730
  %.61.ph = phi float [ %.60.ph, %true_block730 ], [ %.60.ph, %true_block733 ], [ %3136, %true_block739 ]
  %3137 = phi <2 x float> [ %3089, %true_block730 ], [ %3089, %true_block733 ], [ %3135, %true_block739 ]
  %3138 = icmp slt i32 %481, %2846
  br i1 %3138, label %true_block745, label %true_block754

true_block745:                                    ; preds = %true_block742
  %3139 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %3140 = load float*, float** %3139, align 8
  %3141 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %3142 = load i32, i32* %3141, align 4
  %3143 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %3144 = load i32, i32* %3143, align 4
  %3145 = mul i32 %3142, %2835
  %3146 = add i32 %3145, %481
  %3147 = mul i32 %3146, %3144
  %3148 = add i32 %3147, 1
  %3149 = sext i32 %3148 to i64
  %3150 = getelementptr float, float* %3140, i64 %3149
  %3151 = load float, float* %3150, align 4
  %3152 = add i32 %3147, 2
  %3153 = insertelement <2 x i32> poison, i32 %3147, i64 0
  %3154 = insertelement <2 x i32> %3153, i32 %3152, i64 1
  %3155 = sext <2 x i32> %3154 to <2 x i64>
  %3156 = insertelement <2 x float*> poison, float* %3140, i64 0
  %3157 = shufflevector <2 x float*> %3156, <2 x float*> poison, <2 x i32> zeroinitializer
  %3158 = getelementptr float, <2 x float*> %3157, <2 x i64> %3155
  %3159 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %3158, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %3160 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %3161 = load float, float* %3160, align 4
  %3162 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3161, float 0x3F1A36E2E0000000)
  %3163 = extractelement <2 x float> %3159, i64 0
  %3164 = fdiv reassoc ninf nsz float %3163, %3162
  %3165 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %3166 = load float, float* %3165, align 4
  %3167 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3166, float 0x3F1A36E2E0000000)
  %3168 = fdiv reassoc ninf nsz float %3151, %3167
  %3169 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %3170 = load float, float* %3169, align 4
  %3171 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3170, float 0x3F1A36E2E0000000)
  %3172 = extractelement <2 x float> %3159, i64 1
  %3173 = fdiv reassoc ninf nsz float %3172, %3171
  %3174 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3168, float %3173)
  %3175 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3164, float %3174)
  %3176 = fcmp reassoc ninf nsz olt float %3175, 0x3FED70A3E0000000
  %3177 = fcmp reassoc ninf nsz ogt float %3151, 0x3EE4F8B580000000
  %.0324 = select i1 %3176, i1 %3177, i1 false
  br i1 %.0324, label %true_block751, label %true_block754

true_block751:                                    ; preds = %true_block745
  %3178 = insertelement <2 x float> poison, float %3151, i64 0
  %3179 = shufflevector <2 x float> %3178, <2 x float> poison, <2 x i32> zeroinitializer
  %3180 = fdiv reassoc ninf nsz <2 x float> %3159, %3179
  %3181 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %3180, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %3182 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %3181, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %3183 = fadd reassoc ninf nsz <2 x float> %3182, %3137
  %3184 = fadd reassoc ninf nsz float %.61.ph, 1.000000e+00
  br label %true_block754

true_block754:                                    ; preds = %true_block751, %true_block745, %true_block742
  %.62.ph = phi float [ %.61.ph, %true_block742 ], [ %.61.ph, %true_block745 ], [ %3184, %true_block751 ]
  %3185 = phi <2 x float> [ %3137, %true_block742 ], [ %3137, %true_block745 ], [ %3183, %true_block751 ]
  %3186 = icmp slt i32 %475, %2846
  br i1 %3186, label %true_block757, label %after_if759

true_block757:                                    ; preds = %true_block754
  %3187 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 1
  %3188 = load float*, float** %3187, align 8
  %3189 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 1
  %3190 = load i32, i32* %3189, align 4
  %3191 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 0, i32 0, i32 2
  %3192 = load i32, i32* %3191, align 4
  %3193 = mul i32 %3190, %2835
  %3194 = add i32 %3193, %475
  %3195 = mul i32 %3194, %3192
  %3196 = add i32 %3195, 1
  %3197 = sext i32 %3196 to i64
  %3198 = getelementptr float, float* %3188, i64 %3197
  %3199 = load float, float* %3198, align 4
  %3200 = add i32 %3195, 2
  %3201 = insertelement <2 x i32> poison, i32 %3195, i64 0
  %3202 = insertelement <2 x i32> %3201, i32 %3200, i64 1
  %3203 = sext <2 x i32> %3202 to <2 x i64>
  %3204 = insertelement <2 x float*> poison, float* %3188, i64 0
  %3205 = shufflevector <2 x float*> %3204, <2 x float*> poison, <2 x i32> zeroinitializer
  %3206 = getelementptr float, <2 x float*> %3205, <2 x i64> %3203
  %3207 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %3206, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %3208 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 2
  %3209 = load float, float* %3208, align 4
  %3210 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3209, float 0x3F1A36E2E0000000)
  %3211 = extractelement <2 x float> %3207, i64 0
  %3212 = fdiv reassoc ninf nsz float %3211, %3210
  %3213 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 3
  %3214 = load float, float* %3213, align 4
  %3215 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3214, float 0x3F1A36E2E0000000)
  %3216 = fdiv reassoc ninf nsz float %3199, %3215
  %3217 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %2844, i64 0, i32 4
  %3218 = load float, float* %3217, align 4
  %3219 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3218, float 0x3F1A36E2E0000000)
  %3220 = extractelement <2 x float> %3207, i64 1
  %3221 = fdiv reassoc ninf nsz float %3220, %3219
  %3222 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3216, float %3221)
  %3223 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3212, float %3222)
  %3224 = fcmp reassoc ninf nsz olt float %3223, 0x3FED70A3E0000000
  %3225 = fcmp reassoc ninf nsz ogt float %3199, 0x3EE4F8B580000000
  %.0 = select i1 %3224, i1 %3225, i1 false
  br i1 %.0, label %true_block763, label %after_if759

after_if759:                                      ; preds = %true_block763, %true_block757, %true_block754, %after_if663
  %.63 = phi float [ %3272, %true_block763 ], [ %.62.ph, %true_block757 ], [ %.62.ph, %true_block754 ], [ %.55, %after_if663 ]
  %3226 = phi <2 x float> [ %3271, %true_block763 ], [ %3185, %true_block757 ], [ %3185, %true_block754 ], [ %2834, %after_if663 ]
  %3227 = fcmp reassoc ninf nsz ogt float %.63, 0.000000e+00
  %3228 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.63, float 1.000000e+00)
  %3229 = extractelement <2 x float> %3226, i64 0
  %3230 = fdiv reassoc ninf nsz float %3229, %3228
  %3231 = select reassoc ninf nsz i1 %3227, float %3230, float 0.000000e+00
  %3232 = load float*, float** %25, align 8
  %3233 = load i32, i32* %26, align 4
  %3234 = load i32, i32* %27, align 4
  %3235 = sub i32 %3233, %35
  %3236 = mul i32 %3235, %44
  %3237 = add i32 %.05791045, %3236
  %3238 = mul i32 %3237, %3234
  %3239 = sext i32 %3238 to i64
  %3240 = getelementptr float, float* %3232, i64 %3239
  store float %3231, float* %3240, align 4
  %3241 = extractelement <2 x float> %3226, i64 1
  %3242 = fdiv reassoc ninf nsz float %3241, %3228
  %3243 = select reassoc ninf nsz i1 %3227, float %3242, float 0.000000e+00
  %3244 = load float*, float** %25, align 8
  %3245 = load i32, i32* %26, align 4
  %3246 = load i32, i32* %27, align 4
  %3247 = sub i32 %3245, %35
  %3248 = mul i32 %3247, %44
  %3249 = add i32 %.05791045, %3248
  %3250 = mul i32 %3249, %3246
  %3251 = add i32 %3250, 1
  %3252 = sext i32 %3251 to i64
  %3253 = getelementptr float, float* %3244, i64 %3252
  store float %3243, float* %3253, align 4
  %3254 = select reassoc ninf nsz i1 %3227, float 1.000000e+00, float 0.000000e+00
  %3255 = load float*, float** %25, align 8
  %3256 = load i32, i32* %26, align 4
  %3257 = load i32, i32* %27, align 4
  %3258 = sub i32 %3256, %35
  %3259 = mul i32 %3258, %44
  %3260 = add i32 %.05791045, %3259
  %3261 = mul i32 %3260, %3257
  %3262 = add i32 %3261, 2
  %3263 = sext i32 %3262 to i64
  %3264 = getelementptr float, float* %3255, i64 %3263
  store float %3254, float* %3264, align 4
  %3265 = add nsw i32 %.05791045, 1
  %lsr.iv.next = add i32 %lsr.iv, 8
  %exitcond.not = icmp eq i32 %19, %3265
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block763:                                    ; preds = %true_block757
  %3266 = insertelement <2 x float> poison, float %3199, i64 0
  %3267 = shufflevector <2 x float> %3266, <2 x float> poison, <2 x i32> zeroinitializer
  %3268 = fdiv reassoc ninf nsz <2 x float> %3207, %3267
  %3269 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %3268, <2 x float> <float 0x3FA99999A0000000, float 0x3FA99999A0000000>)
  %3270 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %3269, <2 x float> <float 8.000000e+00, float 8.000000e+00>)
  %3271 = fadd reassoc ninf nsz <2 x float> %3270, %3185
  %3272 = fadd reassoc ninf nsz float %.62.ph, 1.000000e+00
  br label %after_if759
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.84, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.84**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.84*, %struct.RuntimeContext.84** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.84* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.84* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.maxnum.v2f32(<2 x float>, <2 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.minnum.v2f32(<2 x float>, <2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
