; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.108*, void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*, i32)*, void (%struct.RuntimeContext.108*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.108 = type { i8*, %struct.LLVMRuntime.107*, i32, i64* }
%struct.LLVMRuntime.107 = type { %struct.PreallocatedMemoryChunk.103, %struct.PreallocatedMemoryChunk.103, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.104*], [1024 x %struct.NodeManager.105*], [1024 x i8*], i8*, %struct.RandState.106*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.103 = type { i8*, i8*, i64 }
%struct.ListManager.104 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.107* }
%struct.NodeManager.105 = type { %struct.LLVMRuntime.107*, i32, i32, i32, i32, %struct.ListManager.104*, %struct.ListManager.104*, %struct.ListManager.104*, i32 }
%struct.RandState.106 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_dcb_highlight_apply_c724_0_kernel_0_serial(%struct.RuntimeContext.108* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.108* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1, i64 0, i32 6
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_highlight_apply_c724_0_kernel_1_range_for(%struct.RuntimeContext.108* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.108* %context, %struct.RuntimeContext.108** %4, align 8
  store void (%struct.RuntimeContext.108*, i8*)* null, void (%struct.RuntimeContext.108*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.108*, i8*, i32)* @function_body, void (%struct.RuntimeContext.108*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.108*, i8*)* null, void (%struct.RuntimeContext.108*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.108* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.108* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %24 = load float, float* %23, align 4
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %26 = load float, float* %22, align 4
  %27 = load float, float* %25, align 4
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 8
  %29 = load i32, i32* %28, align 4
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 9
  %31 = load i32, i32* %30, align 4
  %32 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %24, float 0x3F1A36E2E0000000)
  %33 = insertelement <2 x float> poison, float %27, i64 0
  %34 = insertelement <2 x float> %33, float %26, i64 1
  %35 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %34, <2 x float> <float 0x3F1A36E2E0000000, float 0x3F1A36E2E0000000>)
  %36 = add i32 %29, -1
  %37 = add i32 %31, -1
  %38 = icmp slt i32 %17, %19
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %40 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %41 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %42 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %43 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %44 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  %45 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %46 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %47 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, float, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.01014 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %176, %after_if ]
  %48 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %3, align 8
  %49 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %48, i64 0, i32 14
  %50 = load i8*, i8** %49, align 8
  %51 = getelementptr inbounds i8, i8* %50, i64 4
  %52 = bitcast i8* %51 to i32*
  %53 = load i32, i32* %52, align 4
  %54 = sdiv i32 %.01014, %53
  %55 = mul i32 %54, %53
  %56 = xor i32 %53, %.01014
  %57 = icmp slt i32 %56, 0
  %58 = icmp ne i32 %.01014, 0
  %59 = icmp ne i32 %.01014, %55
  %60 = and i1 %58, %57
  %61 = and i1 %60, %59
  %.neg11 = sext i1 %61 to i32
  %62 = add i32 %54, %.neg11
  %63 = mul i32 %53, -1
  %64 = mul i32 %63, %62
  %65 = add i32 %.01014, %64
  %66 = load float*, float** %39, align 8
  %67 = load i32, i32* %40, align 4
  %68 = load i32, i32* %41, align 4
  %69 = sub i32 %67, %53
  %70 = mul i32 %69, %62
  %71 = add i32 %.01014, %70
  %72 = mul i32 %71, %68
  %73 = add i32 %72, 1
  %74 = sext i32 %73 to i64
  %75 = getelementptr float, float* %66, i64 %74
  %76 = load float, float* %75, align 4
  %77 = add i32 %72, 2
  %78 = insertelement <2 x i32> poison, i32 %77, i64 0
  %79 = insertelement <2 x i32> %78, i32 %72, i64 1
  %80 = sext <2 x i32> %79 to <2 x i64>
  %81 = insertelement <2 x float*> poison, float* %66, i64 0
  %82 = shufflevector <2 x float*> %81, <2 x float*> poison, <2 x i32> zeroinitializer
  %83 = getelementptr float, <2 x float*> %82, <2 x i64> %80
  %84 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %83, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %85 = fdiv reassoc ninf nsz float %76, %32
  %86 = fdiv reassoc ninf nsz <2 x float> %84, %35
  %87 = extractelement <2 x float> %86, i64 0
  %88 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %85, float %87)
  %89 = extractelement <2 x float> %86, i64 1
  %90 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %89, float %88)
  %91 = fmul reassoc ninf nsz float %90, 0x401C924920000000
  %92 = fadd reassoc ninf nsz float %91, 0xC017FFFFE0000000
  %93 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %92, float 0.000000e+00)
  %94 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %93, float 1.000000e+00)
  %95 = sdiv i32 %62, 8
  %96 = icmp slt i32 %62, 0
  %97 = shl nsw i32 %95, 3
  %98 = icmp ne i32 %97, %62
  %99 = and i1 %96, %98
  %.neg12 = sext i1 %99 to i32
  %100 = add nsw i32 %95, %.neg12
  %101 = tail call i32 @llvm.smin.i32(i32 %100, i32 %36)
  %102 = sdiv i32 %65, 8
  %103 = icmp slt i32 %65, 0
  %104 = shl nsw i32 %102, 3
  %105 = icmp ne i32 %65, %104
  %106 = and i1 %103, %105
  %.neg13 = sext i1 %106 to i32
  %107 = add nsw i32 %102, %.neg13
  %108 = tail call i32 @llvm.smin.i32(i32 %107, i32 %37)
  %109 = load float*, float** %42, align 8
  %110 = load i32, i32* %43, align 4
  %111 = load i32, i32* %44, align 4
  %112 = mul i32 %101, %110
  %113 = add i32 %108, %112
  %114 = mul i32 %113, %111
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, float* %109, i64 %115
  %117 = load float, float* %116, align 4
  %118 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %117, float 0x3FA99999A0000000)
  %119 = add i32 %114, 1
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %109, i64 %120
  %122 = load float, float* %121, align 4
  %123 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %122, float 0x3FA99999A0000000)
  %124 = fcmp reassoc ninf nsz ult float %85, 0x3FEEB851E0000000
  br i1 %124, label %after_if, label %true_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %125 = extractelement <2 x float> %84, i64 1
  %126 = fdiv reassoc ninf nsz float %125, %118
  %127 = extractelement <2 x float> %84, i64 0
  %128 = fdiv reassoc ninf nsz float %127, %123
  %129 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %126, float %128)
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %.08 = phi float [ %129, %true_block ], [ %76, %for_loop_body ]
  %130 = fcmp reassoc ninf nsz ult <2 x float> %86, <float 0x3FEEB851E0000000, float 0x3FEEB851E0000000>
  %131 = fmul reassoc ninf nsz float %.08, %118
  %132 = extractelement <2 x i1> %130, i64 1
  %133 = extractelement <2 x float> %84, i64 1
  %.09 = select i1 %132, float %133, float %131
  %134 = fmul reassoc ninf nsz float %.08, %123
  %135 = extractelement <2 x i1> %130, i64 0
  %136 = extractelement <2 x float> %84, i64 0
  %.0 = select i1 %135, float %136, float %134
  %137 = fsub reassoc ninf nsz float 1.000000e+00, %94
  %138 = fmul reassoc ninf nsz float %137, %133
  %139 = fmul reassoc ninf nsz float %.09, %94
  %140 = fadd reassoc ninf nsz float %139, %138
  %141 = load float*, float** %45, align 8
  %142 = load i32, i32* %46, align 4
  %143 = load i32, i32* %47, align 4
  %144 = sub i32 %142, %53
  %145 = mul i32 %144, %62
  %146 = add i32 %.01014, %145
  %147 = mul i32 %146, %143
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %141, i64 %148
  store float %140, float* %149, align 4
  %150 = fmul reassoc ninf nsz float %137, %76
  %151 = fmul reassoc ninf nsz float %.08, %94
  %152 = fadd reassoc ninf nsz float %151, %150
  %153 = load float*, float** %45, align 8
  %154 = load i32, i32* %46, align 4
  %155 = load i32, i32* %47, align 4
  %156 = sub i32 %154, %53
  %157 = mul i32 %156, %62
  %158 = add i32 %.01014, %157
  %159 = mul i32 %158, %155
  %160 = add i32 %159, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %153, i64 %161
  store float %152, float* %162, align 4
  %163 = fmul reassoc ninf nsz float %137, %136
  %164 = fmul reassoc ninf nsz float %.0, %94
  %165 = fadd reassoc ninf nsz float %164, %163
  %166 = load float*, float** %45, align 8
  %167 = load i32, i32* %46, align 4
  %168 = load i32, i32* %47, align 4
  %169 = sub i32 %167, %53
  %170 = mul i32 %169, %62
  %171 = add i32 %.01014, %170
  %172 = mul i32 %171, %168
  %173 = add i32 %172, 2
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, float* %166, i64 %174
  store float %165, float* %175, align 4
  %176 = add nsw i32 %.01014, 1
  %exitcond.not = icmp eq i32 %19, %176
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.108, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.108**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.108*, %struct.RuntimeContext.108** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.108*, i8*, i32)*, void (%struct.RuntimeContext.108*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.108*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.108* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.108* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.108* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.108* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.108* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.108*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.108* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
