; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.24*, void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.24 = type { i8*, %struct.LLVMRuntime.23*, i32, i64* }
%struct.LLVMRuntime.23 = type { %struct.PreallocatedMemoryChunk.19, %struct.PreallocatedMemoryChunk.19, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.20*], [1024 x %struct.NodeManager.21*], [1024 x i8*], i8*, %struct.RandState.22*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.19 = type { i8*, i8*, i64 }
%struct.ListManager.20 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.23* }
%struct.NodeManager.21 = type { %struct.LLVMRuntime.23*, i32, i32, i32, i32, %struct.ListManager.20*, %struct.ListManager.20*, %struct.ListManager.20*, i32 }
%struct.RandState.22 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_gaussian_blur_x_1ch_f32_kernel_c194_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 8
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %7, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 4
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = mul i32 %13, %4
  %20 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %7, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %20, i64 0, i32 14
  %22 = bitcast i8** %21 to i32**
  %23 = load i32*, i32** %22, align 8
  store i32 %19, i32* %23, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_x_1ch_f32_kernel_c194_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.24* %context, %struct.RuntimeContext.24** %4, align 8
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.24*, i8*, i32)* @function_body, void (%struct.RuntimeContext.24*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.24*, i8*)* null, void (%struct.RuntimeContext.24*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.24* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %25 = load float*, float** %24, align 8
  %26 = icmp sgt i32 %23, 0
  %27 = icmp sgt i32 %23, 1
  %28 = icmp sgt i32 %23, 2
  %29 = icmp sgt i32 %23, 3
  %30 = icmp sgt i32 %23, 4
  %31 = icmp sgt i32 %23, 5
  %32 = icmp sgt i32 %23, 6
  %33 = icmp sgt i32 %23, 7
  %34 = icmp sgt i32 %23, 8
  %35 = icmp sgt i32 %23, 9
  %36 = icmp sgt i32 %23, 10
  %37 = icmp sgt i32 %23, 11
  %38 = icmp sgt i32 %23, 12
  %39 = icmp sgt i32 %23, 13
  %40 = icmp sgt i32 %23, 14
  %41 = icmp sgt i32 %23, 15
  %42 = icmp slt i32 %17, %19
  br i1 %42, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.051100 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %601, %after_if45 ]
  %47 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  %52 = load i32, i32* %51, align 4
  %53 = sdiv i32 %.051100, %52
  %54 = mul i32 %53, %52
  %55 = xor i32 %52, %.051100
  %56 = icmp slt i32 %55, 0
  %57 = icmp ne i32 %.051100, 0
  %58 = icmp ne i32 %.051100, %54
  %59 = and i1 %57, %56
  %60 = and i1 %59, %58
  %.neg52 = sext i1 %60 to i32
  %61 = load float, float* %25, align 4
  %62 = load float*, float** %43, align 8
  %63 = load i32, i32* %44, align 4
  %64 = add i32 %53, %.neg52
  %65 = mul i32 %64, %52
  %66 = insertelement <2 x i32> poison, i32 %.051100, i64 0
  %67 = insertelement <2 x i32> %66, i32 %63, i64 1
  %68 = insertelement <2 x i32> poison, i32 %65, i64 0
  %69 = insertelement <2 x i32> %68, i32 %64, i64 1
  %70 = sub <2 x i32> %67, %69
  %71 = mul <2 x i32> %67, %69
  %72 = extractelement <2 x i32> %70, i64 0
  %73 = extractelement <2 x i32> %71, i64 1
  %74 = add i32 %72, %73
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, float* %62, i64 %75
  %77 = load float, float* %76, align 4
  %78 = fmul reassoc ninf nsz float %77, %61
  %79 = insertelement <2 x float> poison, float %78, i64 0
  %80 = insertelement <2 x float> %79, float %61, i64 1
  br i1 %26, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %81 = load float*, float** %24, align 8
  %82 = getelementptr float, float* %81, i64 1
  %83 = load float, float* %82, align 4
  %84 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %85 = add <2 x i32> %84, <i32 1, i32 -1>
  %86 = getelementptr inbounds i8, i8* %49, i64 8
  %87 = bitcast i8* %86 to i32*
  %88 = load i32, i32* %87, align 4
  %89 = add i32 %88, -1
  %90 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %85, i1 true)
  %91 = insertelement <2 x i32> poison, i32 %89, i64 0
  %92 = shufflevector <2 x i32> %91, <2 x i32> poison, <2 x i32> zeroinitializer
  %93 = sub <2 x i32> %90, %92
  %94 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %93, <2 x i32> zeroinitializer)
  %95 = mul <2 x i32> %94, <i32 -2, i32 -2>
  %96 = add <2 x i32> %95, %90
  %97 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %96, <2 x i32> zeroinitializer)
  %98 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %97)
  %99 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %100 = add <2 x i32> %98, %99
  %101 = sext <2 x i32> %100 to <2 x i64>
  %102 = insertelement <2 x float*> poison, float* %62, i64 0
  %103 = shufflevector <2 x float*> %102, <2 x float*> poison, <2 x i32> zeroinitializer
  %104 = getelementptr float, <2 x float*> %103, <2 x i64> %101
  %105 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %104, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift = shufflevector <2 x float> %105, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %106 = fadd reassoc ninf nsz <2 x float> %105, %shift
  %107 = insertelement <2 x float> %106, float 2.000000e+00, i64 1
  %108 = insertelement <2 x float> poison, float %83, i64 0
  %109 = shufflevector <2 x float> %108, <2 x float> poison, <2 x i32> zeroinitializer
  %110 = fmul reassoc ninf nsz <2 x float> %107, %109
  %111 = fadd reassoc ninf nsz <2 x float> %110, %80
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %112 = phi <2 x float> [ %111, %true_block ], [ %80, %for_loop_body ]
  br i1 %27, label %true_block1, label %after_if3

true_block1:                                      ; preds = %after_if
  %113 = load float*, float** %24, align 8
  %114 = getelementptr float, float* %113, i64 2
  %115 = load float, float* %114, align 4
  %116 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %117 = add <2 x i32> %116, <i32 2, i32 -2>
  %118 = getelementptr inbounds i8, i8* %49, i64 8
  %119 = bitcast i8* %118 to i32*
  %120 = load i32, i32* %119, align 4
  %121 = add i32 %120, -1
  %122 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %117, i1 true)
  %123 = insertelement <2 x i32> poison, i32 %121, i64 0
  %124 = shufflevector <2 x i32> %123, <2 x i32> poison, <2 x i32> zeroinitializer
  %125 = sub <2 x i32> %122, %124
  %126 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %125, <2 x i32> zeroinitializer)
  %127 = mul <2 x i32> %126, <i32 -2, i32 -2>
  %128 = add <2 x i32> %127, %122
  %129 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %128, <2 x i32> zeroinitializer)
  %130 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %124, <2 x i32> %129)
  %131 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %132 = add <2 x i32> %130, %131
  %133 = sext <2 x i32> %132 to <2 x i64>
  %134 = insertelement <2 x float*> poison, float* %62, i64 0
  %135 = shufflevector <2 x float*> %134, <2 x float*> poison, <2 x i32> zeroinitializer
  %136 = getelementptr float, <2 x float*> %135, <2 x i64> %133
  %137 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %136, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift101 = shufflevector <2 x float> %137, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %138 = fadd reassoc ninf nsz <2 x float> %137, %shift101
  %139 = insertelement <2 x float> %138, float 2.000000e+00, i64 1
  %140 = insertelement <2 x float> poison, float %115, i64 0
  %141 = shufflevector <2 x float> %140, <2 x float> poison, <2 x i32> zeroinitializer
  %142 = fmul reassoc ninf nsz <2 x float> %139, %141
  %143 = fadd reassoc ninf nsz <2 x float> %142, %112
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %after_if
  %144 = phi <2 x float> [ %143, %true_block1 ], [ %112, %after_if ]
  br i1 %28, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %145 = load float*, float** %24, align 8
  %146 = getelementptr float, float* %145, i64 3
  %147 = load float, float* %146, align 4
  %148 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %149 = add <2 x i32> %148, <i32 3, i32 -3>
  %150 = getelementptr inbounds i8, i8* %49, i64 8
  %151 = bitcast i8* %150 to i32*
  %152 = load i32, i32* %151, align 4
  %153 = add i32 %152, -1
  %154 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %149, i1 true)
  %155 = insertelement <2 x i32> poison, i32 %153, i64 0
  %156 = shufflevector <2 x i32> %155, <2 x i32> poison, <2 x i32> zeroinitializer
  %157 = sub <2 x i32> %154, %156
  %158 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %157, <2 x i32> zeroinitializer)
  %159 = mul <2 x i32> %158, <i32 -2, i32 -2>
  %160 = add <2 x i32> %159, %154
  %161 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %160, <2 x i32> zeroinitializer)
  %162 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %156, <2 x i32> %161)
  %163 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %164 = add <2 x i32> %162, %163
  %165 = sext <2 x i32> %164 to <2 x i64>
  %166 = insertelement <2 x float*> poison, float* %62, i64 0
  %167 = shufflevector <2 x float*> %166, <2 x float*> poison, <2 x i32> zeroinitializer
  %168 = getelementptr float, <2 x float*> %167, <2 x i64> %165
  %169 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %168, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift102 = shufflevector <2 x float> %169, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %170 = fadd reassoc ninf nsz <2 x float> %169, %shift102
  %171 = insertelement <2 x float> %170, float 2.000000e+00, i64 1
  %172 = insertelement <2 x float> poison, float %147, i64 0
  %173 = shufflevector <2 x float> %172, <2 x float> poison, <2 x i32> zeroinitializer
  %174 = fmul reassoc ninf nsz <2 x float> %171, %173
  %175 = fadd reassoc ninf nsz <2 x float> %174, %144
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %176 = phi <2 x float> [ %175, %true_block4 ], [ %144, %after_if3 ]
  br i1 %29, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %177 = load float*, float** %24, align 8
  %178 = getelementptr float, float* %177, i64 4
  %179 = load float, float* %178, align 4
  %180 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %181 = add <2 x i32> %180, <i32 4, i32 -4>
  %182 = getelementptr inbounds i8, i8* %49, i64 8
  %183 = bitcast i8* %182 to i32*
  %184 = load i32, i32* %183, align 4
  %185 = add i32 %184, -1
  %186 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %181, i1 true)
  %187 = insertelement <2 x i32> poison, i32 %185, i64 0
  %188 = shufflevector <2 x i32> %187, <2 x i32> poison, <2 x i32> zeroinitializer
  %189 = sub <2 x i32> %186, %188
  %190 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %189, <2 x i32> zeroinitializer)
  %191 = mul <2 x i32> %190, <i32 -2, i32 -2>
  %192 = add <2 x i32> %191, %186
  %193 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %192, <2 x i32> zeroinitializer)
  %194 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %188, <2 x i32> %193)
  %195 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %196 = add <2 x i32> %194, %195
  %197 = sext <2 x i32> %196 to <2 x i64>
  %198 = insertelement <2 x float*> poison, float* %62, i64 0
  %199 = shufflevector <2 x float*> %198, <2 x float*> poison, <2 x i32> zeroinitializer
  %200 = getelementptr float, <2 x float*> %199, <2 x i64> %197
  %201 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %200, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift103 = shufflevector <2 x float> %201, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %202 = fadd reassoc ninf nsz <2 x float> %201, %shift103
  %203 = insertelement <2 x float> %202, float 2.000000e+00, i64 1
  %204 = insertelement <2 x float> poison, float %179, i64 0
  %205 = shufflevector <2 x float> %204, <2 x float> poison, <2 x i32> zeroinitializer
  %206 = fmul reassoc ninf nsz <2 x float> %203, %205
  %207 = fadd reassoc ninf nsz <2 x float> %206, %176
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %208 = phi <2 x float> [ %207, %true_block7 ], [ %176, %after_if6 ]
  br i1 %30, label %true_block10, label %after_if12

true_block10:                                     ; preds = %after_if9
  %209 = load float*, float** %24, align 8
  %210 = getelementptr float, float* %209, i64 5
  %211 = load float, float* %210, align 4
  %212 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %213 = add <2 x i32> %212, <i32 5, i32 -5>
  %214 = getelementptr inbounds i8, i8* %49, i64 8
  %215 = bitcast i8* %214 to i32*
  %216 = load i32, i32* %215, align 4
  %217 = add i32 %216, -1
  %218 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %213, i1 true)
  %219 = insertelement <2 x i32> poison, i32 %217, i64 0
  %220 = shufflevector <2 x i32> %219, <2 x i32> poison, <2 x i32> zeroinitializer
  %221 = sub <2 x i32> %218, %220
  %222 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %221, <2 x i32> zeroinitializer)
  %223 = mul <2 x i32> %222, <i32 -2, i32 -2>
  %224 = add <2 x i32> %223, %218
  %225 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %224, <2 x i32> zeroinitializer)
  %226 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %220, <2 x i32> %225)
  %227 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %228 = add <2 x i32> %226, %227
  %229 = sext <2 x i32> %228 to <2 x i64>
  %230 = insertelement <2 x float*> poison, float* %62, i64 0
  %231 = shufflevector <2 x float*> %230, <2 x float*> poison, <2 x i32> zeroinitializer
  %232 = getelementptr float, <2 x float*> %231, <2 x i64> %229
  %233 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %232, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift104 = shufflevector <2 x float> %233, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %234 = fadd reassoc ninf nsz <2 x float> %233, %shift104
  %235 = insertelement <2 x float> %234, float 2.000000e+00, i64 1
  %236 = insertelement <2 x float> poison, float %211, i64 0
  %237 = shufflevector <2 x float> %236, <2 x float> poison, <2 x i32> zeroinitializer
  %238 = fmul reassoc ninf nsz <2 x float> %235, %237
  %239 = fadd reassoc ninf nsz <2 x float> %238, %208
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %240 = phi <2 x float> [ %239, %true_block10 ], [ %208, %after_if9 ]
  br i1 %31, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if12
  %241 = load float*, float** %24, align 8
  %242 = getelementptr float, float* %241, i64 6
  %243 = load float, float* %242, align 4
  %244 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %245 = add <2 x i32> %244, <i32 6, i32 -6>
  %246 = getelementptr inbounds i8, i8* %49, i64 8
  %247 = bitcast i8* %246 to i32*
  %248 = load i32, i32* %247, align 4
  %249 = add i32 %248, -1
  %250 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %245, i1 true)
  %251 = insertelement <2 x i32> poison, i32 %249, i64 0
  %252 = shufflevector <2 x i32> %251, <2 x i32> poison, <2 x i32> zeroinitializer
  %253 = sub <2 x i32> %250, %252
  %254 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %253, <2 x i32> zeroinitializer)
  %255 = mul <2 x i32> %254, <i32 -2, i32 -2>
  %256 = add <2 x i32> %255, %250
  %257 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %256, <2 x i32> zeroinitializer)
  %258 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %252, <2 x i32> %257)
  %259 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %260 = add <2 x i32> %258, %259
  %261 = sext <2 x i32> %260 to <2 x i64>
  %262 = insertelement <2 x float*> poison, float* %62, i64 0
  %263 = shufflevector <2 x float*> %262, <2 x float*> poison, <2 x i32> zeroinitializer
  %264 = getelementptr float, <2 x float*> %263, <2 x i64> %261
  %265 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %264, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift105 = shufflevector <2 x float> %265, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %266 = fadd reassoc ninf nsz <2 x float> %265, %shift105
  %267 = insertelement <2 x float> %266, float 2.000000e+00, i64 1
  %268 = insertelement <2 x float> poison, float %243, i64 0
  %269 = shufflevector <2 x float> %268, <2 x float> poison, <2 x i32> zeroinitializer
  %270 = fmul reassoc ninf nsz <2 x float> %267, %269
  %271 = fadd reassoc ninf nsz <2 x float> %270, %240
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if12
  %272 = phi <2 x float> [ %271, %true_block13 ], [ %240, %after_if12 ]
  br i1 %32, label %true_block16, label %after_if18

true_block16:                                     ; preds = %after_if15
  %273 = load float*, float** %24, align 8
  %274 = getelementptr float, float* %273, i64 7
  %275 = load float, float* %274, align 4
  %276 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %277 = add <2 x i32> %276, <i32 7, i32 -7>
  %278 = getelementptr inbounds i8, i8* %49, i64 8
  %279 = bitcast i8* %278 to i32*
  %280 = load i32, i32* %279, align 4
  %281 = add i32 %280, -1
  %282 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %277, i1 true)
  %283 = insertelement <2 x i32> poison, i32 %281, i64 0
  %284 = shufflevector <2 x i32> %283, <2 x i32> poison, <2 x i32> zeroinitializer
  %285 = sub <2 x i32> %282, %284
  %286 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %285, <2 x i32> zeroinitializer)
  %287 = mul <2 x i32> %286, <i32 -2, i32 -2>
  %288 = add <2 x i32> %287, %282
  %289 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %288, <2 x i32> zeroinitializer)
  %290 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %284, <2 x i32> %289)
  %291 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %292 = add <2 x i32> %290, %291
  %293 = sext <2 x i32> %292 to <2 x i64>
  %294 = insertelement <2 x float*> poison, float* %62, i64 0
  %295 = shufflevector <2 x float*> %294, <2 x float*> poison, <2 x i32> zeroinitializer
  %296 = getelementptr float, <2 x float*> %295, <2 x i64> %293
  %297 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %296, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift106 = shufflevector <2 x float> %297, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %298 = fadd reassoc ninf nsz <2 x float> %297, %shift106
  %299 = insertelement <2 x float> %298, float 2.000000e+00, i64 1
  %300 = insertelement <2 x float> poison, float %275, i64 0
  %301 = shufflevector <2 x float> %300, <2 x float> poison, <2 x i32> zeroinitializer
  %302 = fmul reassoc ninf nsz <2 x float> %299, %301
  %303 = fadd reassoc ninf nsz <2 x float> %302, %272
  br label %after_if18

after_if18:                                       ; preds = %true_block16, %after_if15
  %304 = phi <2 x float> [ %303, %true_block16 ], [ %272, %after_if15 ]
  br i1 %33, label %true_block19, label %after_if21

true_block19:                                     ; preds = %after_if18
  %305 = load float*, float** %24, align 8
  %306 = getelementptr float, float* %305, i64 8
  %307 = load float, float* %306, align 4
  %308 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %309 = add <2 x i32> %308, <i32 8, i32 -8>
  %310 = getelementptr inbounds i8, i8* %49, i64 8
  %311 = bitcast i8* %310 to i32*
  %312 = load i32, i32* %311, align 4
  %313 = add i32 %312, -1
  %314 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %309, i1 true)
  %315 = insertelement <2 x i32> poison, i32 %313, i64 0
  %316 = shufflevector <2 x i32> %315, <2 x i32> poison, <2 x i32> zeroinitializer
  %317 = sub <2 x i32> %314, %316
  %318 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %317, <2 x i32> zeroinitializer)
  %319 = mul <2 x i32> %318, <i32 -2, i32 -2>
  %320 = add <2 x i32> %319, %314
  %321 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %320, <2 x i32> zeroinitializer)
  %322 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %316, <2 x i32> %321)
  %323 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %324 = add <2 x i32> %322, %323
  %325 = sext <2 x i32> %324 to <2 x i64>
  %326 = insertelement <2 x float*> poison, float* %62, i64 0
  %327 = shufflevector <2 x float*> %326, <2 x float*> poison, <2 x i32> zeroinitializer
  %328 = getelementptr float, <2 x float*> %327, <2 x i64> %325
  %329 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %328, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift107 = shufflevector <2 x float> %329, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %330 = fadd reassoc ninf nsz <2 x float> %329, %shift107
  %331 = insertelement <2 x float> %330, float 2.000000e+00, i64 1
  %332 = insertelement <2 x float> poison, float %307, i64 0
  %333 = shufflevector <2 x float> %332, <2 x float> poison, <2 x i32> zeroinitializer
  %334 = fmul reassoc ninf nsz <2 x float> %331, %333
  %335 = fadd reassoc ninf nsz <2 x float> %334, %304
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if18
  %336 = phi <2 x float> [ %335, %true_block19 ], [ %304, %after_if18 ]
  br i1 %34, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if21
  %337 = load float*, float** %24, align 8
  %338 = getelementptr float, float* %337, i64 9
  %339 = load float, float* %338, align 4
  %340 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %341 = add <2 x i32> %340, <i32 9, i32 -9>
  %342 = getelementptr inbounds i8, i8* %49, i64 8
  %343 = bitcast i8* %342 to i32*
  %344 = load i32, i32* %343, align 4
  %345 = add i32 %344, -1
  %346 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %341, i1 true)
  %347 = insertelement <2 x i32> poison, i32 %345, i64 0
  %348 = shufflevector <2 x i32> %347, <2 x i32> poison, <2 x i32> zeroinitializer
  %349 = sub <2 x i32> %346, %348
  %350 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %349, <2 x i32> zeroinitializer)
  %351 = mul <2 x i32> %350, <i32 -2, i32 -2>
  %352 = add <2 x i32> %351, %346
  %353 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %352, <2 x i32> zeroinitializer)
  %354 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %348, <2 x i32> %353)
  %355 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %356 = add <2 x i32> %354, %355
  %357 = sext <2 x i32> %356 to <2 x i64>
  %358 = insertelement <2 x float*> poison, float* %62, i64 0
  %359 = shufflevector <2 x float*> %358, <2 x float*> poison, <2 x i32> zeroinitializer
  %360 = getelementptr float, <2 x float*> %359, <2 x i64> %357
  %361 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %360, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift108 = shufflevector <2 x float> %361, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %362 = fadd reassoc ninf nsz <2 x float> %361, %shift108
  %363 = insertelement <2 x float> %362, float 2.000000e+00, i64 1
  %364 = insertelement <2 x float> poison, float %339, i64 0
  %365 = shufflevector <2 x float> %364, <2 x float> poison, <2 x i32> zeroinitializer
  %366 = fmul reassoc ninf nsz <2 x float> %363, %365
  %367 = fadd reassoc ninf nsz <2 x float> %366, %336
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if21
  %368 = phi <2 x float> [ %367, %true_block22 ], [ %336, %after_if21 ]
  br i1 %35, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if24
  %369 = load float*, float** %24, align 8
  %370 = getelementptr float, float* %369, i64 10
  %371 = load float, float* %370, align 4
  %372 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %373 = add <2 x i32> %372, <i32 10, i32 -10>
  %374 = getelementptr inbounds i8, i8* %49, i64 8
  %375 = bitcast i8* %374 to i32*
  %376 = load i32, i32* %375, align 4
  %377 = add i32 %376, -1
  %378 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %373, i1 true)
  %379 = insertelement <2 x i32> poison, i32 %377, i64 0
  %380 = shufflevector <2 x i32> %379, <2 x i32> poison, <2 x i32> zeroinitializer
  %381 = sub <2 x i32> %378, %380
  %382 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %381, <2 x i32> zeroinitializer)
  %383 = mul <2 x i32> %382, <i32 -2, i32 -2>
  %384 = add <2 x i32> %383, %378
  %385 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %384, <2 x i32> zeroinitializer)
  %386 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %380, <2 x i32> %385)
  %387 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %388 = add <2 x i32> %386, %387
  %389 = sext <2 x i32> %388 to <2 x i64>
  %390 = insertelement <2 x float*> poison, float* %62, i64 0
  %391 = shufflevector <2 x float*> %390, <2 x float*> poison, <2 x i32> zeroinitializer
  %392 = getelementptr float, <2 x float*> %391, <2 x i64> %389
  %393 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %392, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift109 = shufflevector <2 x float> %393, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %394 = fadd reassoc ninf nsz <2 x float> %393, %shift109
  %395 = insertelement <2 x float> %394, float 2.000000e+00, i64 1
  %396 = insertelement <2 x float> poison, float %371, i64 0
  %397 = shufflevector <2 x float> %396, <2 x float> poison, <2 x i32> zeroinitializer
  %398 = fmul reassoc ninf nsz <2 x float> %395, %397
  %399 = fadd reassoc ninf nsz <2 x float> %398, %368
  br label %after_if27

after_if27:                                       ; preds = %true_block25, %after_if24
  %400 = phi <2 x float> [ %399, %true_block25 ], [ %368, %after_if24 ]
  br i1 %36, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %401 = load float*, float** %24, align 8
  %402 = getelementptr float, float* %401, i64 11
  %403 = load float, float* %402, align 4
  %404 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %405 = add <2 x i32> %404, <i32 11, i32 -11>
  %406 = getelementptr inbounds i8, i8* %49, i64 8
  %407 = bitcast i8* %406 to i32*
  %408 = load i32, i32* %407, align 4
  %409 = add i32 %408, -1
  %410 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %405, i1 true)
  %411 = insertelement <2 x i32> poison, i32 %409, i64 0
  %412 = shufflevector <2 x i32> %411, <2 x i32> poison, <2 x i32> zeroinitializer
  %413 = sub <2 x i32> %410, %412
  %414 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %413, <2 x i32> zeroinitializer)
  %415 = mul <2 x i32> %414, <i32 -2, i32 -2>
  %416 = add <2 x i32> %415, %410
  %417 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %416, <2 x i32> zeroinitializer)
  %418 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %412, <2 x i32> %417)
  %419 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %420 = add <2 x i32> %418, %419
  %421 = sext <2 x i32> %420 to <2 x i64>
  %422 = insertelement <2 x float*> poison, float* %62, i64 0
  %423 = shufflevector <2 x float*> %422, <2 x float*> poison, <2 x i32> zeroinitializer
  %424 = getelementptr float, <2 x float*> %423, <2 x i64> %421
  %425 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %424, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift110 = shufflevector <2 x float> %425, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %426 = fadd reassoc ninf nsz <2 x float> %425, %shift110
  %427 = insertelement <2 x float> %426, float 2.000000e+00, i64 1
  %428 = insertelement <2 x float> poison, float %403, i64 0
  %429 = shufflevector <2 x float> %428, <2 x float> poison, <2 x i32> zeroinitializer
  %430 = fmul reassoc ninf nsz <2 x float> %427, %429
  %431 = fadd reassoc ninf nsz <2 x float> %430, %400
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27
  %432 = phi <2 x float> [ %431, %true_block28 ], [ %400, %after_if27 ]
  br i1 %37, label %true_block31, label %after_if33

true_block31:                                     ; preds = %after_if30
  %433 = load float*, float** %24, align 8
  %434 = getelementptr float, float* %433, i64 12
  %435 = load float, float* %434, align 4
  %436 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %437 = add <2 x i32> %436, <i32 12, i32 -12>
  %438 = getelementptr inbounds i8, i8* %49, i64 8
  %439 = bitcast i8* %438 to i32*
  %440 = load i32, i32* %439, align 4
  %441 = add i32 %440, -1
  %442 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %437, i1 true)
  %443 = insertelement <2 x i32> poison, i32 %441, i64 0
  %444 = shufflevector <2 x i32> %443, <2 x i32> poison, <2 x i32> zeroinitializer
  %445 = sub <2 x i32> %442, %444
  %446 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %445, <2 x i32> zeroinitializer)
  %447 = mul <2 x i32> %446, <i32 -2, i32 -2>
  %448 = add <2 x i32> %447, %442
  %449 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %448, <2 x i32> zeroinitializer)
  %450 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %444, <2 x i32> %449)
  %451 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %452 = add <2 x i32> %450, %451
  %453 = sext <2 x i32> %452 to <2 x i64>
  %454 = insertelement <2 x float*> poison, float* %62, i64 0
  %455 = shufflevector <2 x float*> %454, <2 x float*> poison, <2 x i32> zeroinitializer
  %456 = getelementptr float, <2 x float*> %455, <2 x i64> %453
  %457 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %456, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift111 = shufflevector <2 x float> %457, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %458 = fadd reassoc ninf nsz <2 x float> %457, %shift111
  %459 = insertelement <2 x float> %458, float 2.000000e+00, i64 1
  %460 = insertelement <2 x float> poison, float %435, i64 0
  %461 = shufflevector <2 x float> %460, <2 x float> poison, <2 x i32> zeroinitializer
  %462 = fmul reassoc ninf nsz <2 x float> %459, %461
  %463 = fadd reassoc ninf nsz <2 x float> %462, %432
  br label %after_if33

after_if33:                                       ; preds = %true_block31, %after_if30
  %464 = phi <2 x float> [ %463, %true_block31 ], [ %432, %after_if30 ]
  br i1 %38, label %true_block34, label %after_if36

true_block34:                                     ; preds = %after_if33
  %465 = load float*, float** %24, align 8
  %466 = getelementptr float, float* %465, i64 13
  %467 = load float, float* %466, align 4
  %468 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %469 = add <2 x i32> %468, <i32 13, i32 -13>
  %470 = getelementptr inbounds i8, i8* %49, i64 8
  %471 = bitcast i8* %470 to i32*
  %472 = load i32, i32* %471, align 4
  %473 = add i32 %472, -1
  %474 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %469, i1 true)
  %475 = insertelement <2 x i32> poison, i32 %473, i64 0
  %476 = shufflevector <2 x i32> %475, <2 x i32> poison, <2 x i32> zeroinitializer
  %477 = sub <2 x i32> %474, %476
  %478 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %477, <2 x i32> zeroinitializer)
  %479 = mul <2 x i32> %478, <i32 -2, i32 -2>
  %480 = add <2 x i32> %479, %474
  %481 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %480, <2 x i32> zeroinitializer)
  %482 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %476, <2 x i32> %481)
  %483 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %484 = add <2 x i32> %482, %483
  %485 = sext <2 x i32> %484 to <2 x i64>
  %486 = insertelement <2 x float*> poison, float* %62, i64 0
  %487 = shufflevector <2 x float*> %486, <2 x float*> poison, <2 x i32> zeroinitializer
  %488 = getelementptr float, <2 x float*> %487, <2 x i64> %485
  %489 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %488, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift112 = shufflevector <2 x float> %489, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %490 = fadd reassoc ninf nsz <2 x float> %489, %shift112
  %491 = insertelement <2 x float> %490, float 2.000000e+00, i64 1
  %492 = insertelement <2 x float> poison, float %467, i64 0
  %493 = shufflevector <2 x float> %492, <2 x float> poison, <2 x i32> zeroinitializer
  %494 = fmul reassoc ninf nsz <2 x float> %491, %493
  %495 = fadd reassoc ninf nsz <2 x float> %494, %464
  br label %after_if36

after_if36:                                       ; preds = %true_block34, %after_if33
  %496 = phi <2 x float> [ %495, %true_block34 ], [ %464, %after_if33 ]
  br i1 %39, label %true_block37, label %after_if39

true_block37:                                     ; preds = %after_if36
  %497 = load float*, float** %24, align 8
  %498 = getelementptr float, float* %497, i64 14
  %499 = load float, float* %498, align 4
  %500 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %501 = add <2 x i32> %500, <i32 14, i32 -14>
  %502 = getelementptr inbounds i8, i8* %49, i64 8
  %503 = bitcast i8* %502 to i32*
  %504 = load i32, i32* %503, align 4
  %505 = add i32 %504, -1
  %506 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %501, i1 true)
  %507 = insertelement <2 x i32> poison, i32 %505, i64 0
  %508 = shufflevector <2 x i32> %507, <2 x i32> poison, <2 x i32> zeroinitializer
  %509 = sub <2 x i32> %506, %508
  %510 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %509, <2 x i32> zeroinitializer)
  %511 = mul <2 x i32> %510, <i32 -2, i32 -2>
  %512 = add <2 x i32> %511, %506
  %513 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %512, <2 x i32> zeroinitializer)
  %514 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %508, <2 x i32> %513)
  %515 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %516 = add <2 x i32> %514, %515
  %517 = sext <2 x i32> %516 to <2 x i64>
  %518 = insertelement <2 x float*> poison, float* %62, i64 0
  %519 = shufflevector <2 x float*> %518, <2 x float*> poison, <2 x i32> zeroinitializer
  %520 = getelementptr float, <2 x float*> %519, <2 x i64> %517
  %521 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %520, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift113 = shufflevector <2 x float> %521, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %522 = fadd reassoc ninf nsz <2 x float> %521, %shift113
  %523 = insertelement <2 x float> %522, float 2.000000e+00, i64 1
  %524 = insertelement <2 x float> poison, float %499, i64 0
  %525 = shufflevector <2 x float> %524, <2 x float> poison, <2 x i32> zeroinitializer
  %526 = fmul reassoc ninf nsz <2 x float> %523, %525
  %527 = fadd reassoc ninf nsz <2 x float> %526, %496
  br label %after_if39

after_if39:                                       ; preds = %true_block37, %after_if36
  %528 = phi <2 x float> [ %527, %true_block37 ], [ %496, %after_if36 ]
  br i1 %40, label %true_block40, label %after_if42

true_block40:                                     ; preds = %after_if39
  %529 = load float*, float** %24, align 8
  %530 = getelementptr float, float* %529, i64 15
  %531 = load float, float* %530, align 4
  %532 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %533 = add <2 x i32> %532, <i32 15, i32 -15>
  %534 = getelementptr inbounds i8, i8* %49, i64 8
  %535 = bitcast i8* %534 to i32*
  %536 = load i32, i32* %535, align 4
  %537 = add i32 %536, -1
  %538 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %533, i1 true)
  %539 = insertelement <2 x i32> poison, i32 %537, i64 0
  %540 = shufflevector <2 x i32> %539, <2 x i32> poison, <2 x i32> zeroinitializer
  %541 = sub <2 x i32> %538, %540
  %542 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %541, <2 x i32> zeroinitializer)
  %543 = mul <2 x i32> %542, <i32 -2, i32 -2>
  %544 = add <2 x i32> %543, %538
  %545 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %544, <2 x i32> zeroinitializer)
  %546 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %540, <2 x i32> %545)
  %547 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %548 = add <2 x i32> %546, %547
  %549 = sext <2 x i32> %548 to <2 x i64>
  %550 = insertelement <2 x float*> poison, float* %62, i64 0
  %551 = shufflevector <2 x float*> %550, <2 x float*> poison, <2 x i32> zeroinitializer
  %552 = getelementptr float, <2 x float*> %551, <2 x i64> %549
  %553 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %552, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift114 = shufflevector <2 x float> %553, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %554 = fadd reassoc ninf nsz <2 x float> %553, %shift114
  %555 = insertelement <2 x float> %554, float 2.000000e+00, i64 1
  %556 = insertelement <2 x float> poison, float %531, i64 0
  %557 = shufflevector <2 x float> %556, <2 x float> poison, <2 x i32> zeroinitializer
  %558 = fmul reassoc ninf nsz <2 x float> %555, %557
  %559 = fadd reassoc ninf nsz <2 x float> %558, %528
  br label %after_if42

after_if42:                                       ; preds = %true_block40, %after_if39
  %560 = phi <2 x float> [ %559, %true_block40 ], [ %528, %after_if39 ]
  br i1 %41, label %true_block43, label %after_if45

true_block43:                                     ; preds = %after_if42
  %561 = load float*, float** %24, align 8
  %562 = getelementptr float, float* %561, i64 16
  %563 = load float, float* %562, align 4
  %564 = shufflevector <2 x i32> %70, <2 x i32> poison, <2 x i32> zeroinitializer
  %565 = add <2 x i32> %564, <i32 16, i32 -16>
  %566 = getelementptr inbounds i8, i8* %49, i64 8
  %567 = bitcast i8* %566 to i32*
  %568 = load i32, i32* %567, align 4
  %569 = add i32 %568, -1
  %570 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %565, i1 true)
  %571 = insertelement <2 x i32> poison, i32 %569, i64 0
  %572 = shufflevector <2 x i32> %571, <2 x i32> poison, <2 x i32> zeroinitializer
  %573 = sub <2 x i32> %570, %572
  %574 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %573, <2 x i32> zeroinitializer)
  %575 = mul <2 x i32> %574, <i32 -2, i32 -2>
  %576 = add <2 x i32> %575, %570
  %577 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %576, <2 x i32> zeroinitializer)
  %578 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %572, <2 x i32> %577)
  %579 = shufflevector <2 x i32> %71, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %580 = add <2 x i32> %578, %579
  %581 = sext <2 x i32> %580 to <2 x i64>
  %582 = insertelement <2 x float*> poison, float* %62, i64 0
  %583 = shufflevector <2 x float*> %582, <2 x float*> poison, <2 x i32> zeroinitializer
  %584 = getelementptr float, <2 x float*> %583, <2 x i64> %581
  %585 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %584, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift115 = shufflevector <2 x float> %585, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %586 = fadd reassoc ninf nsz <2 x float> %585, %shift115
  %587 = insertelement <2 x float> %586, float 2.000000e+00, i64 1
  %588 = insertelement <2 x float> poison, float %563, i64 0
  %589 = shufflevector <2 x float> %588, <2 x float> poison, <2 x i32> zeroinitializer
  %590 = fmul reassoc ninf nsz <2 x float> %587, %589
  %591 = fadd reassoc ninf nsz <2 x float> %590, %560
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42
  %592 = phi <2 x float> [ %591, %true_block43 ], [ %560, %after_if42 ]
  %shift116 = shufflevector <2 x float> %592, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %593 = fdiv reassoc ninf nsz <2 x float> %592, %shift116
  %594 = extractelement <2 x float> %593, i64 0
  %595 = load float*, float** %45, align 8
  %596 = load i32, i32* %46, align 4
  %597 = mul i32 %596, %64
  %598 = add i32 %597, %72
  %599 = sext i32 %598 to i64
  %600 = getelementptr float, float* %595, i64 %599
  store float %594, float* %600, align 4
  %601 = add nsw i32 %.051100, 1
  %exitcond.not = icmp eq i32 %19, %601
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.24, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.24**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.24*, %struct.RuntimeContext.24** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.24*, i8*, i32)*, void (%struct.RuntimeContext.24*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.24*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.24*, i8*)*, void (%struct.RuntimeContext.24*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.24* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.24* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.24* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.24*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.24* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
declare <2 x i32> @llvm.abs.v2i32(<2 x i32>, i1 immarg) #7

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
