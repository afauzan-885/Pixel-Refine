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
define void @_gaussian_blur_y_1ch_f32_kernel_c196_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %15 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 4
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = mul i32 %14, %10
  %21 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %21, i64 0, i32 14
  %23 = bitcast i8** %22 to i32**
  %24 = load i32*, i32** %23, align 8
  store i32 %20, i32* %24, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_y_1ch_f32_kernel_c196_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
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
  %.051100 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %662, %after_if45 ]
  %47 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %47, i64 0, i32 14
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
  %67 = insertelement <2 x i32> poison, i32 %65, i64 0
  %68 = sub <2 x i32> %66, %67
  %69 = extractelement <2 x i32> %68, i64 0
  %70 = mul i32 %63, %64
  %71 = add i32 %69, %70
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, float* %62, i64 %72
  %74 = load float, float* %73, align 4
  %75 = fmul reassoc ninf nsz float %74, %61
  %76 = insertelement <2 x float> poison, float %75, i64 0
  %77 = insertelement <2 x float> %76, float %61, i64 1
  br i1 %26, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %78 = load float*, float** %24, align 8
  %79 = getelementptr float, float* %78, i64 1
  %80 = load float, float* %79, align 4
  %81 = insertelement <2 x i32> poison, i32 %64, i64 0
  %82 = shufflevector <2 x i32> %81, <2 x i32> poison, <2 x i32> zeroinitializer
  %83 = add <2 x i32> %82, <i32 1, i32 -1>
  %84 = getelementptr inbounds i8, i8* %49, i64 8
  %85 = bitcast i8* %84 to i32*
  %86 = load i32, i32* %85, align 4
  %87 = add i32 %86, -1
  %88 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %83, i1 true)
  %89 = insertelement <2 x i32> poison, i32 %87, i64 0
  %90 = shufflevector <2 x i32> %89, <2 x i32> poison, <2 x i32> zeroinitializer
  %91 = sub <2 x i32> %88, %90
  %92 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %91, <2 x i32> zeroinitializer)
  %93 = mul <2 x i32> %92, <i32 -2, i32 -2>
  %94 = add <2 x i32> %93, %88
  %95 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %94, <2 x i32> zeroinitializer)
  %96 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %90, <2 x i32> %95)
  %97 = insertelement <2 x i32> poison, i32 %63, i64 0
  %98 = shufflevector <2 x i32> %97, <2 x i32> poison, <2 x i32> zeroinitializer
  %99 = mul <2 x i32> %96, %98
  %100 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %101 = add <2 x i32> %99, %100
  %102 = sext <2 x i32> %101 to <2 x i64>
  %103 = insertelement <2 x float*> poison, float* %62, i64 0
  %104 = shufflevector <2 x float*> %103, <2 x float*> poison, <2 x i32> zeroinitializer
  %105 = getelementptr float, <2 x float*> %104, <2 x i64> %102
  %106 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %105, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift = shufflevector <2 x float> %106, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %107 = fadd reassoc ninf nsz <2 x float> %106, %shift
  %108 = insertelement <2 x float> %107, float 2.000000e+00, i64 1
  %109 = insertelement <2 x float> poison, float %80, i64 0
  %110 = shufflevector <2 x float> %109, <2 x float> poison, <2 x i32> zeroinitializer
  %111 = fmul reassoc ninf nsz <2 x float> %108, %110
  %112 = fadd reassoc ninf nsz <2 x float> %111, %77
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %113 = phi <2 x float> [ %112, %true_block ], [ %77, %for_loop_body ]
  br i1 %27, label %true_block1, label %after_if3

true_block1:                                      ; preds = %after_if
  %114 = load float*, float** %24, align 8
  %115 = getelementptr float, float* %114, i64 2
  %116 = load float, float* %115, align 4
  %117 = insertelement <2 x i32> poison, i32 %64, i64 0
  %118 = shufflevector <2 x i32> %117, <2 x i32> poison, <2 x i32> zeroinitializer
  %119 = add <2 x i32> %118, <i32 2, i32 -2>
  %120 = getelementptr inbounds i8, i8* %49, i64 8
  %121 = bitcast i8* %120 to i32*
  %122 = load i32, i32* %121, align 4
  %123 = add i32 %122, -1
  %124 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %119, i1 true)
  %125 = insertelement <2 x i32> poison, i32 %123, i64 0
  %126 = shufflevector <2 x i32> %125, <2 x i32> poison, <2 x i32> zeroinitializer
  %127 = sub <2 x i32> %124, %126
  %128 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %127, <2 x i32> zeroinitializer)
  %129 = mul <2 x i32> %128, <i32 -2, i32 -2>
  %130 = add <2 x i32> %129, %124
  %131 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %130, <2 x i32> zeroinitializer)
  %132 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %126, <2 x i32> %131)
  %133 = insertelement <2 x i32> poison, i32 %63, i64 0
  %134 = shufflevector <2 x i32> %133, <2 x i32> poison, <2 x i32> zeroinitializer
  %135 = mul <2 x i32> %132, %134
  %136 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %137 = add <2 x i32> %135, %136
  %138 = sext <2 x i32> %137 to <2 x i64>
  %139 = insertelement <2 x float*> poison, float* %62, i64 0
  %140 = shufflevector <2 x float*> %139, <2 x float*> poison, <2 x i32> zeroinitializer
  %141 = getelementptr float, <2 x float*> %140, <2 x i64> %138
  %142 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %141, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift101 = shufflevector <2 x float> %142, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %143 = fadd reassoc ninf nsz <2 x float> %142, %shift101
  %144 = insertelement <2 x float> %143, float 2.000000e+00, i64 1
  %145 = insertelement <2 x float> poison, float %116, i64 0
  %146 = shufflevector <2 x float> %145, <2 x float> poison, <2 x i32> zeroinitializer
  %147 = fmul reassoc ninf nsz <2 x float> %144, %146
  %148 = fadd reassoc ninf nsz <2 x float> %147, %113
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %after_if
  %149 = phi <2 x float> [ %148, %true_block1 ], [ %113, %after_if ]
  br i1 %28, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %150 = load float*, float** %24, align 8
  %151 = getelementptr float, float* %150, i64 3
  %152 = load float, float* %151, align 4
  %153 = insertelement <2 x i32> poison, i32 %64, i64 0
  %154 = shufflevector <2 x i32> %153, <2 x i32> poison, <2 x i32> zeroinitializer
  %155 = add <2 x i32> %154, <i32 3, i32 -3>
  %156 = getelementptr inbounds i8, i8* %49, i64 8
  %157 = bitcast i8* %156 to i32*
  %158 = load i32, i32* %157, align 4
  %159 = add i32 %158, -1
  %160 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %155, i1 true)
  %161 = insertelement <2 x i32> poison, i32 %159, i64 0
  %162 = shufflevector <2 x i32> %161, <2 x i32> poison, <2 x i32> zeroinitializer
  %163 = sub <2 x i32> %160, %162
  %164 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %163, <2 x i32> zeroinitializer)
  %165 = mul <2 x i32> %164, <i32 -2, i32 -2>
  %166 = add <2 x i32> %165, %160
  %167 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %166, <2 x i32> zeroinitializer)
  %168 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %162, <2 x i32> %167)
  %169 = insertelement <2 x i32> poison, i32 %63, i64 0
  %170 = shufflevector <2 x i32> %169, <2 x i32> poison, <2 x i32> zeroinitializer
  %171 = mul <2 x i32> %168, %170
  %172 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %173 = add <2 x i32> %171, %172
  %174 = sext <2 x i32> %173 to <2 x i64>
  %175 = insertelement <2 x float*> poison, float* %62, i64 0
  %176 = shufflevector <2 x float*> %175, <2 x float*> poison, <2 x i32> zeroinitializer
  %177 = getelementptr float, <2 x float*> %176, <2 x i64> %174
  %178 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %177, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift102 = shufflevector <2 x float> %178, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %179 = fadd reassoc ninf nsz <2 x float> %178, %shift102
  %180 = insertelement <2 x float> %179, float 2.000000e+00, i64 1
  %181 = insertelement <2 x float> poison, float %152, i64 0
  %182 = shufflevector <2 x float> %181, <2 x float> poison, <2 x i32> zeroinitializer
  %183 = fmul reassoc ninf nsz <2 x float> %180, %182
  %184 = fadd reassoc ninf nsz <2 x float> %183, %149
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %185 = phi <2 x float> [ %184, %true_block4 ], [ %149, %after_if3 ]
  br i1 %29, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %186 = load float*, float** %24, align 8
  %187 = getelementptr float, float* %186, i64 4
  %188 = load float, float* %187, align 4
  %189 = insertelement <2 x i32> poison, i32 %64, i64 0
  %190 = shufflevector <2 x i32> %189, <2 x i32> poison, <2 x i32> zeroinitializer
  %191 = add <2 x i32> %190, <i32 4, i32 -4>
  %192 = getelementptr inbounds i8, i8* %49, i64 8
  %193 = bitcast i8* %192 to i32*
  %194 = load i32, i32* %193, align 4
  %195 = add i32 %194, -1
  %196 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %191, i1 true)
  %197 = insertelement <2 x i32> poison, i32 %195, i64 0
  %198 = shufflevector <2 x i32> %197, <2 x i32> poison, <2 x i32> zeroinitializer
  %199 = sub <2 x i32> %196, %198
  %200 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %199, <2 x i32> zeroinitializer)
  %201 = mul <2 x i32> %200, <i32 -2, i32 -2>
  %202 = add <2 x i32> %201, %196
  %203 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %202, <2 x i32> zeroinitializer)
  %204 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %198, <2 x i32> %203)
  %205 = insertelement <2 x i32> poison, i32 %63, i64 0
  %206 = shufflevector <2 x i32> %205, <2 x i32> poison, <2 x i32> zeroinitializer
  %207 = mul <2 x i32> %204, %206
  %208 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %209 = add <2 x i32> %207, %208
  %210 = sext <2 x i32> %209 to <2 x i64>
  %211 = insertelement <2 x float*> poison, float* %62, i64 0
  %212 = shufflevector <2 x float*> %211, <2 x float*> poison, <2 x i32> zeroinitializer
  %213 = getelementptr float, <2 x float*> %212, <2 x i64> %210
  %214 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %213, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift103 = shufflevector <2 x float> %214, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %215 = fadd reassoc ninf nsz <2 x float> %214, %shift103
  %216 = insertelement <2 x float> %215, float 2.000000e+00, i64 1
  %217 = insertelement <2 x float> poison, float %188, i64 0
  %218 = shufflevector <2 x float> %217, <2 x float> poison, <2 x i32> zeroinitializer
  %219 = fmul reassoc ninf nsz <2 x float> %216, %218
  %220 = fadd reassoc ninf nsz <2 x float> %219, %185
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %221 = phi <2 x float> [ %220, %true_block7 ], [ %185, %after_if6 ]
  br i1 %30, label %true_block10, label %after_if12

true_block10:                                     ; preds = %after_if9
  %222 = load float*, float** %24, align 8
  %223 = getelementptr float, float* %222, i64 5
  %224 = load float, float* %223, align 4
  %225 = insertelement <2 x i32> poison, i32 %64, i64 0
  %226 = shufflevector <2 x i32> %225, <2 x i32> poison, <2 x i32> zeroinitializer
  %227 = add <2 x i32> %226, <i32 5, i32 -5>
  %228 = getelementptr inbounds i8, i8* %49, i64 8
  %229 = bitcast i8* %228 to i32*
  %230 = load i32, i32* %229, align 4
  %231 = add i32 %230, -1
  %232 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %227, i1 true)
  %233 = insertelement <2 x i32> poison, i32 %231, i64 0
  %234 = shufflevector <2 x i32> %233, <2 x i32> poison, <2 x i32> zeroinitializer
  %235 = sub <2 x i32> %232, %234
  %236 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %235, <2 x i32> zeroinitializer)
  %237 = mul <2 x i32> %236, <i32 -2, i32 -2>
  %238 = add <2 x i32> %237, %232
  %239 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %238, <2 x i32> zeroinitializer)
  %240 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %234, <2 x i32> %239)
  %241 = insertelement <2 x i32> poison, i32 %63, i64 0
  %242 = shufflevector <2 x i32> %241, <2 x i32> poison, <2 x i32> zeroinitializer
  %243 = mul <2 x i32> %240, %242
  %244 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %245 = add <2 x i32> %243, %244
  %246 = sext <2 x i32> %245 to <2 x i64>
  %247 = insertelement <2 x float*> poison, float* %62, i64 0
  %248 = shufflevector <2 x float*> %247, <2 x float*> poison, <2 x i32> zeroinitializer
  %249 = getelementptr float, <2 x float*> %248, <2 x i64> %246
  %250 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %249, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift104 = shufflevector <2 x float> %250, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %251 = fadd reassoc ninf nsz <2 x float> %250, %shift104
  %252 = insertelement <2 x float> %251, float 2.000000e+00, i64 1
  %253 = insertelement <2 x float> poison, float %224, i64 0
  %254 = shufflevector <2 x float> %253, <2 x float> poison, <2 x i32> zeroinitializer
  %255 = fmul reassoc ninf nsz <2 x float> %252, %254
  %256 = fadd reassoc ninf nsz <2 x float> %255, %221
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %257 = phi <2 x float> [ %256, %true_block10 ], [ %221, %after_if9 ]
  br i1 %31, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if12
  %258 = load float*, float** %24, align 8
  %259 = getelementptr float, float* %258, i64 6
  %260 = load float, float* %259, align 4
  %261 = insertelement <2 x i32> poison, i32 %64, i64 0
  %262 = shufflevector <2 x i32> %261, <2 x i32> poison, <2 x i32> zeroinitializer
  %263 = add <2 x i32> %262, <i32 6, i32 -6>
  %264 = getelementptr inbounds i8, i8* %49, i64 8
  %265 = bitcast i8* %264 to i32*
  %266 = load i32, i32* %265, align 4
  %267 = add i32 %266, -1
  %268 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %263, i1 true)
  %269 = insertelement <2 x i32> poison, i32 %267, i64 0
  %270 = shufflevector <2 x i32> %269, <2 x i32> poison, <2 x i32> zeroinitializer
  %271 = sub <2 x i32> %268, %270
  %272 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %271, <2 x i32> zeroinitializer)
  %273 = mul <2 x i32> %272, <i32 -2, i32 -2>
  %274 = add <2 x i32> %273, %268
  %275 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %274, <2 x i32> zeroinitializer)
  %276 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %270, <2 x i32> %275)
  %277 = insertelement <2 x i32> poison, i32 %63, i64 0
  %278 = shufflevector <2 x i32> %277, <2 x i32> poison, <2 x i32> zeroinitializer
  %279 = mul <2 x i32> %276, %278
  %280 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %281 = add <2 x i32> %279, %280
  %282 = sext <2 x i32> %281 to <2 x i64>
  %283 = insertelement <2 x float*> poison, float* %62, i64 0
  %284 = shufflevector <2 x float*> %283, <2 x float*> poison, <2 x i32> zeroinitializer
  %285 = getelementptr float, <2 x float*> %284, <2 x i64> %282
  %286 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %285, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift105 = shufflevector <2 x float> %286, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %287 = fadd reassoc ninf nsz <2 x float> %286, %shift105
  %288 = insertelement <2 x float> %287, float 2.000000e+00, i64 1
  %289 = insertelement <2 x float> poison, float %260, i64 0
  %290 = shufflevector <2 x float> %289, <2 x float> poison, <2 x i32> zeroinitializer
  %291 = fmul reassoc ninf nsz <2 x float> %288, %290
  %292 = fadd reassoc ninf nsz <2 x float> %291, %257
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if12
  %293 = phi <2 x float> [ %292, %true_block13 ], [ %257, %after_if12 ]
  br i1 %32, label %true_block16, label %after_if18

true_block16:                                     ; preds = %after_if15
  %294 = load float*, float** %24, align 8
  %295 = getelementptr float, float* %294, i64 7
  %296 = load float, float* %295, align 4
  %297 = insertelement <2 x i32> poison, i32 %64, i64 0
  %298 = shufflevector <2 x i32> %297, <2 x i32> poison, <2 x i32> zeroinitializer
  %299 = add <2 x i32> %298, <i32 7, i32 -7>
  %300 = getelementptr inbounds i8, i8* %49, i64 8
  %301 = bitcast i8* %300 to i32*
  %302 = load i32, i32* %301, align 4
  %303 = add i32 %302, -1
  %304 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %299, i1 true)
  %305 = insertelement <2 x i32> poison, i32 %303, i64 0
  %306 = shufflevector <2 x i32> %305, <2 x i32> poison, <2 x i32> zeroinitializer
  %307 = sub <2 x i32> %304, %306
  %308 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %307, <2 x i32> zeroinitializer)
  %309 = mul <2 x i32> %308, <i32 -2, i32 -2>
  %310 = add <2 x i32> %309, %304
  %311 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %310, <2 x i32> zeroinitializer)
  %312 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %306, <2 x i32> %311)
  %313 = insertelement <2 x i32> poison, i32 %63, i64 0
  %314 = shufflevector <2 x i32> %313, <2 x i32> poison, <2 x i32> zeroinitializer
  %315 = mul <2 x i32> %312, %314
  %316 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %317 = add <2 x i32> %315, %316
  %318 = sext <2 x i32> %317 to <2 x i64>
  %319 = insertelement <2 x float*> poison, float* %62, i64 0
  %320 = shufflevector <2 x float*> %319, <2 x float*> poison, <2 x i32> zeroinitializer
  %321 = getelementptr float, <2 x float*> %320, <2 x i64> %318
  %322 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %321, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift106 = shufflevector <2 x float> %322, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %323 = fadd reassoc ninf nsz <2 x float> %322, %shift106
  %324 = insertelement <2 x float> %323, float 2.000000e+00, i64 1
  %325 = insertelement <2 x float> poison, float %296, i64 0
  %326 = shufflevector <2 x float> %325, <2 x float> poison, <2 x i32> zeroinitializer
  %327 = fmul reassoc ninf nsz <2 x float> %324, %326
  %328 = fadd reassoc ninf nsz <2 x float> %327, %293
  br label %after_if18

after_if18:                                       ; preds = %true_block16, %after_if15
  %329 = phi <2 x float> [ %328, %true_block16 ], [ %293, %after_if15 ]
  br i1 %33, label %true_block19, label %after_if21

true_block19:                                     ; preds = %after_if18
  %330 = load float*, float** %24, align 8
  %331 = getelementptr float, float* %330, i64 8
  %332 = load float, float* %331, align 4
  %333 = insertelement <2 x i32> poison, i32 %64, i64 0
  %334 = shufflevector <2 x i32> %333, <2 x i32> poison, <2 x i32> zeroinitializer
  %335 = add <2 x i32> %334, <i32 8, i32 -8>
  %336 = getelementptr inbounds i8, i8* %49, i64 8
  %337 = bitcast i8* %336 to i32*
  %338 = load i32, i32* %337, align 4
  %339 = add i32 %338, -1
  %340 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %335, i1 true)
  %341 = insertelement <2 x i32> poison, i32 %339, i64 0
  %342 = shufflevector <2 x i32> %341, <2 x i32> poison, <2 x i32> zeroinitializer
  %343 = sub <2 x i32> %340, %342
  %344 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %343, <2 x i32> zeroinitializer)
  %345 = mul <2 x i32> %344, <i32 -2, i32 -2>
  %346 = add <2 x i32> %345, %340
  %347 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %346, <2 x i32> zeroinitializer)
  %348 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %342, <2 x i32> %347)
  %349 = insertelement <2 x i32> poison, i32 %63, i64 0
  %350 = shufflevector <2 x i32> %349, <2 x i32> poison, <2 x i32> zeroinitializer
  %351 = mul <2 x i32> %348, %350
  %352 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %353 = add <2 x i32> %351, %352
  %354 = sext <2 x i32> %353 to <2 x i64>
  %355 = insertelement <2 x float*> poison, float* %62, i64 0
  %356 = shufflevector <2 x float*> %355, <2 x float*> poison, <2 x i32> zeroinitializer
  %357 = getelementptr float, <2 x float*> %356, <2 x i64> %354
  %358 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %357, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift107 = shufflevector <2 x float> %358, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %359 = fadd reassoc ninf nsz <2 x float> %358, %shift107
  %360 = insertelement <2 x float> %359, float 2.000000e+00, i64 1
  %361 = insertelement <2 x float> poison, float %332, i64 0
  %362 = shufflevector <2 x float> %361, <2 x float> poison, <2 x i32> zeroinitializer
  %363 = fmul reassoc ninf nsz <2 x float> %360, %362
  %364 = fadd reassoc ninf nsz <2 x float> %363, %329
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if18
  %365 = phi <2 x float> [ %364, %true_block19 ], [ %329, %after_if18 ]
  br i1 %34, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if21
  %366 = load float*, float** %24, align 8
  %367 = getelementptr float, float* %366, i64 9
  %368 = load float, float* %367, align 4
  %369 = insertelement <2 x i32> poison, i32 %64, i64 0
  %370 = shufflevector <2 x i32> %369, <2 x i32> poison, <2 x i32> zeroinitializer
  %371 = add <2 x i32> %370, <i32 9, i32 -9>
  %372 = getelementptr inbounds i8, i8* %49, i64 8
  %373 = bitcast i8* %372 to i32*
  %374 = load i32, i32* %373, align 4
  %375 = add i32 %374, -1
  %376 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %371, i1 true)
  %377 = insertelement <2 x i32> poison, i32 %375, i64 0
  %378 = shufflevector <2 x i32> %377, <2 x i32> poison, <2 x i32> zeroinitializer
  %379 = sub <2 x i32> %376, %378
  %380 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %379, <2 x i32> zeroinitializer)
  %381 = mul <2 x i32> %380, <i32 -2, i32 -2>
  %382 = add <2 x i32> %381, %376
  %383 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %382, <2 x i32> zeroinitializer)
  %384 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %378, <2 x i32> %383)
  %385 = insertelement <2 x i32> poison, i32 %63, i64 0
  %386 = shufflevector <2 x i32> %385, <2 x i32> poison, <2 x i32> zeroinitializer
  %387 = mul <2 x i32> %384, %386
  %388 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %389 = add <2 x i32> %387, %388
  %390 = sext <2 x i32> %389 to <2 x i64>
  %391 = insertelement <2 x float*> poison, float* %62, i64 0
  %392 = shufflevector <2 x float*> %391, <2 x float*> poison, <2 x i32> zeroinitializer
  %393 = getelementptr float, <2 x float*> %392, <2 x i64> %390
  %394 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %393, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift108 = shufflevector <2 x float> %394, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %395 = fadd reassoc ninf nsz <2 x float> %394, %shift108
  %396 = insertelement <2 x float> %395, float 2.000000e+00, i64 1
  %397 = insertelement <2 x float> poison, float %368, i64 0
  %398 = shufflevector <2 x float> %397, <2 x float> poison, <2 x i32> zeroinitializer
  %399 = fmul reassoc ninf nsz <2 x float> %396, %398
  %400 = fadd reassoc ninf nsz <2 x float> %399, %365
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if21
  %401 = phi <2 x float> [ %400, %true_block22 ], [ %365, %after_if21 ]
  br i1 %35, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if24
  %402 = load float*, float** %24, align 8
  %403 = getelementptr float, float* %402, i64 10
  %404 = load float, float* %403, align 4
  %405 = insertelement <2 x i32> poison, i32 %64, i64 0
  %406 = shufflevector <2 x i32> %405, <2 x i32> poison, <2 x i32> zeroinitializer
  %407 = add <2 x i32> %406, <i32 10, i32 -10>
  %408 = getelementptr inbounds i8, i8* %49, i64 8
  %409 = bitcast i8* %408 to i32*
  %410 = load i32, i32* %409, align 4
  %411 = add i32 %410, -1
  %412 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %407, i1 true)
  %413 = insertelement <2 x i32> poison, i32 %411, i64 0
  %414 = shufflevector <2 x i32> %413, <2 x i32> poison, <2 x i32> zeroinitializer
  %415 = sub <2 x i32> %412, %414
  %416 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %415, <2 x i32> zeroinitializer)
  %417 = mul <2 x i32> %416, <i32 -2, i32 -2>
  %418 = add <2 x i32> %417, %412
  %419 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %418, <2 x i32> zeroinitializer)
  %420 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %414, <2 x i32> %419)
  %421 = insertelement <2 x i32> poison, i32 %63, i64 0
  %422 = shufflevector <2 x i32> %421, <2 x i32> poison, <2 x i32> zeroinitializer
  %423 = mul <2 x i32> %420, %422
  %424 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %425 = add <2 x i32> %423, %424
  %426 = sext <2 x i32> %425 to <2 x i64>
  %427 = insertelement <2 x float*> poison, float* %62, i64 0
  %428 = shufflevector <2 x float*> %427, <2 x float*> poison, <2 x i32> zeroinitializer
  %429 = getelementptr float, <2 x float*> %428, <2 x i64> %426
  %430 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %429, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift109 = shufflevector <2 x float> %430, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %431 = fadd reassoc ninf nsz <2 x float> %430, %shift109
  %432 = insertelement <2 x float> %431, float 2.000000e+00, i64 1
  %433 = insertelement <2 x float> poison, float %404, i64 0
  %434 = shufflevector <2 x float> %433, <2 x float> poison, <2 x i32> zeroinitializer
  %435 = fmul reassoc ninf nsz <2 x float> %432, %434
  %436 = fadd reassoc ninf nsz <2 x float> %435, %401
  br label %after_if27

after_if27:                                       ; preds = %true_block25, %after_if24
  %437 = phi <2 x float> [ %436, %true_block25 ], [ %401, %after_if24 ]
  br i1 %36, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %438 = load float*, float** %24, align 8
  %439 = getelementptr float, float* %438, i64 11
  %440 = load float, float* %439, align 4
  %441 = insertelement <2 x i32> poison, i32 %64, i64 0
  %442 = shufflevector <2 x i32> %441, <2 x i32> poison, <2 x i32> zeroinitializer
  %443 = add <2 x i32> %442, <i32 11, i32 -11>
  %444 = getelementptr inbounds i8, i8* %49, i64 8
  %445 = bitcast i8* %444 to i32*
  %446 = load i32, i32* %445, align 4
  %447 = add i32 %446, -1
  %448 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %443, i1 true)
  %449 = insertelement <2 x i32> poison, i32 %447, i64 0
  %450 = shufflevector <2 x i32> %449, <2 x i32> poison, <2 x i32> zeroinitializer
  %451 = sub <2 x i32> %448, %450
  %452 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %451, <2 x i32> zeroinitializer)
  %453 = mul <2 x i32> %452, <i32 -2, i32 -2>
  %454 = add <2 x i32> %453, %448
  %455 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %454, <2 x i32> zeroinitializer)
  %456 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %450, <2 x i32> %455)
  %457 = insertelement <2 x i32> poison, i32 %63, i64 0
  %458 = shufflevector <2 x i32> %457, <2 x i32> poison, <2 x i32> zeroinitializer
  %459 = mul <2 x i32> %456, %458
  %460 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %461 = add <2 x i32> %459, %460
  %462 = sext <2 x i32> %461 to <2 x i64>
  %463 = insertelement <2 x float*> poison, float* %62, i64 0
  %464 = shufflevector <2 x float*> %463, <2 x float*> poison, <2 x i32> zeroinitializer
  %465 = getelementptr float, <2 x float*> %464, <2 x i64> %462
  %466 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %465, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift110 = shufflevector <2 x float> %466, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %467 = fadd reassoc ninf nsz <2 x float> %466, %shift110
  %468 = insertelement <2 x float> %467, float 2.000000e+00, i64 1
  %469 = insertelement <2 x float> poison, float %440, i64 0
  %470 = shufflevector <2 x float> %469, <2 x float> poison, <2 x i32> zeroinitializer
  %471 = fmul reassoc ninf nsz <2 x float> %468, %470
  %472 = fadd reassoc ninf nsz <2 x float> %471, %437
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27
  %473 = phi <2 x float> [ %472, %true_block28 ], [ %437, %after_if27 ]
  br i1 %37, label %true_block31, label %after_if33

true_block31:                                     ; preds = %after_if30
  %474 = load float*, float** %24, align 8
  %475 = getelementptr float, float* %474, i64 12
  %476 = load float, float* %475, align 4
  %477 = insertelement <2 x i32> poison, i32 %64, i64 0
  %478 = shufflevector <2 x i32> %477, <2 x i32> poison, <2 x i32> zeroinitializer
  %479 = add <2 x i32> %478, <i32 12, i32 -12>
  %480 = getelementptr inbounds i8, i8* %49, i64 8
  %481 = bitcast i8* %480 to i32*
  %482 = load i32, i32* %481, align 4
  %483 = add i32 %482, -1
  %484 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %479, i1 true)
  %485 = insertelement <2 x i32> poison, i32 %483, i64 0
  %486 = shufflevector <2 x i32> %485, <2 x i32> poison, <2 x i32> zeroinitializer
  %487 = sub <2 x i32> %484, %486
  %488 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %487, <2 x i32> zeroinitializer)
  %489 = mul <2 x i32> %488, <i32 -2, i32 -2>
  %490 = add <2 x i32> %489, %484
  %491 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %490, <2 x i32> zeroinitializer)
  %492 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %486, <2 x i32> %491)
  %493 = insertelement <2 x i32> poison, i32 %63, i64 0
  %494 = shufflevector <2 x i32> %493, <2 x i32> poison, <2 x i32> zeroinitializer
  %495 = mul <2 x i32> %492, %494
  %496 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %497 = add <2 x i32> %495, %496
  %498 = sext <2 x i32> %497 to <2 x i64>
  %499 = insertelement <2 x float*> poison, float* %62, i64 0
  %500 = shufflevector <2 x float*> %499, <2 x float*> poison, <2 x i32> zeroinitializer
  %501 = getelementptr float, <2 x float*> %500, <2 x i64> %498
  %502 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %501, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift111 = shufflevector <2 x float> %502, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %503 = fadd reassoc ninf nsz <2 x float> %502, %shift111
  %504 = insertelement <2 x float> %503, float 2.000000e+00, i64 1
  %505 = insertelement <2 x float> poison, float %476, i64 0
  %506 = shufflevector <2 x float> %505, <2 x float> poison, <2 x i32> zeroinitializer
  %507 = fmul reassoc ninf nsz <2 x float> %504, %506
  %508 = fadd reassoc ninf nsz <2 x float> %507, %473
  br label %after_if33

after_if33:                                       ; preds = %true_block31, %after_if30
  %509 = phi <2 x float> [ %508, %true_block31 ], [ %473, %after_if30 ]
  br i1 %38, label %true_block34, label %after_if36

true_block34:                                     ; preds = %after_if33
  %510 = load float*, float** %24, align 8
  %511 = getelementptr float, float* %510, i64 13
  %512 = load float, float* %511, align 4
  %513 = insertelement <2 x i32> poison, i32 %64, i64 0
  %514 = shufflevector <2 x i32> %513, <2 x i32> poison, <2 x i32> zeroinitializer
  %515 = add <2 x i32> %514, <i32 13, i32 -13>
  %516 = getelementptr inbounds i8, i8* %49, i64 8
  %517 = bitcast i8* %516 to i32*
  %518 = load i32, i32* %517, align 4
  %519 = add i32 %518, -1
  %520 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %515, i1 true)
  %521 = insertelement <2 x i32> poison, i32 %519, i64 0
  %522 = shufflevector <2 x i32> %521, <2 x i32> poison, <2 x i32> zeroinitializer
  %523 = sub <2 x i32> %520, %522
  %524 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %523, <2 x i32> zeroinitializer)
  %525 = mul <2 x i32> %524, <i32 -2, i32 -2>
  %526 = add <2 x i32> %525, %520
  %527 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %526, <2 x i32> zeroinitializer)
  %528 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %522, <2 x i32> %527)
  %529 = insertelement <2 x i32> poison, i32 %63, i64 0
  %530 = shufflevector <2 x i32> %529, <2 x i32> poison, <2 x i32> zeroinitializer
  %531 = mul <2 x i32> %528, %530
  %532 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %533 = add <2 x i32> %531, %532
  %534 = sext <2 x i32> %533 to <2 x i64>
  %535 = insertelement <2 x float*> poison, float* %62, i64 0
  %536 = shufflevector <2 x float*> %535, <2 x float*> poison, <2 x i32> zeroinitializer
  %537 = getelementptr float, <2 x float*> %536, <2 x i64> %534
  %538 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %537, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift112 = shufflevector <2 x float> %538, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %539 = fadd reassoc ninf nsz <2 x float> %538, %shift112
  %540 = insertelement <2 x float> %539, float 2.000000e+00, i64 1
  %541 = insertelement <2 x float> poison, float %512, i64 0
  %542 = shufflevector <2 x float> %541, <2 x float> poison, <2 x i32> zeroinitializer
  %543 = fmul reassoc ninf nsz <2 x float> %540, %542
  %544 = fadd reassoc ninf nsz <2 x float> %543, %509
  br label %after_if36

after_if36:                                       ; preds = %true_block34, %after_if33
  %545 = phi <2 x float> [ %544, %true_block34 ], [ %509, %after_if33 ]
  br i1 %39, label %true_block37, label %after_if39

true_block37:                                     ; preds = %after_if36
  %546 = load float*, float** %24, align 8
  %547 = getelementptr float, float* %546, i64 14
  %548 = load float, float* %547, align 4
  %549 = insertelement <2 x i32> poison, i32 %64, i64 0
  %550 = shufflevector <2 x i32> %549, <2 x i32> poison, <2 x i32> zeroinitializer
  %551 = add <2 x i32> %550, <i32 14, i32 -14>
  %552 = getelementptr inbounds i8, i8* %49, i64 8
  %553 = bitcast i8* %552 to i32*
  %554 = load i32, i32* %553, align 4
  %555 = add i32 %554, -1
  %556 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %551, i1 true)
  %557 = insertelement <2 x i32> poison, i32 %555, i64 0
  %558 = shufflevector <2 x i32> %557, <2 x i32> poison, <2 x i32> zeroinitializer
  %559 = sub <2 x i32> %556, %558
  %560 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %559, <2 x i32> zeroinitializer)
  %561 = mul <2 x i32> %560, <i32 -2, i32 -2>
  %562 = add <2 x i32> %561, %556
  %563 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %562, <2 x i32> zeroinitializer)
  %564 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %558, <2 x i32> %563)
  %565 = insertelement <2 x i32> poison, i32 %63, i64 0
  %566 = shufflevector <2 x i32> %565, <2 x i32> poison, <2 x i32> zeroinitializer
  %567 = mul <2 x i32> %564, %566
  %568 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %569 = add <2 x i32> %567, %568
  %570 = sext <2 x i32> %569 to <2 x i64>
  %571 = insertelement <2 x float*> poison, float* %62, i64 0
  %572 = shufflevector <2 x float*> %571, <2 x float*> poison, <2 x i32> zeroinitializer
  %573 = getelementptr float, <2 x float*> %572, <2 x i64> %570
  %574 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %573, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift113 = shufflevector <2 x float> %574, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %575 = fadd reassoc ninf nsz <2 x float> %574, %shift113
  %576 = insertelement <2 x float> %575, float 2.000000e+00, i64 1
  %577 = insertelement <2 x float> poison, float %548, i64 0
  %578 = shufflevector <2 x float> %577, <2 x float> poison, <2 x i32> zeroinitializer
  %579 = fmul reassoc ninf nsz <2 x float> %576, %578
  %580 = fadd reassoc ninf nsz <2 x float> %579, %545
  br label %after_if39

after_if39:                                       ; preds = %true_block37, %after_if36
  %581 = phi <2 x float> [ %580, %true_block37 ], [ %545, %after_if36 ]
  br i1 %40, label %true_block40, label %after_if42

true_block40:                                     ; preds = %after_if39
  %582 = load float*, float** %24, align 8
  %583 = getelementptr float, float* %582, i64 15
  %584 = load float, float* %583, align 4
  %585 = insertelement <2 x i32> poison, i32 %64, i64 0
  %586 = shufflevector <2 x i32> %585, <2 x i32> poison, <2 x i32> zeroinitializer
  %587 = add <2 x i32> %586, <i32 15, i32 -15>
  %588 = getelementptr inbounds i8, i8* %49, i64 8
  %589 = bitcast i8* %588 to i32*
  %590 = load i32, i32* %589, align 4
  %591 = add i32 %590, -1
  %592 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %587, i1 true)
  %593 = insertelement <2 x i32> poison, i32 %591, i64 0
  %594 = shufflevector <2 x i32> %593, <2 x i32> poison, <2 x i32> zeroinitializer
  %595 = sub <2 x i32> %592, %594
  %596 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %595, <2 x i32> zeroinitializer)
  %597 = mul <2 x i32> %596, <i32 -2, i32 -2>
  %598 = add <2 x i32> %597, %592
  %599 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %598, <2 x i32> zeroinitializer)
  %600 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %594, <2 x i32> %599)
  %601 = insertelement <2 x i32> poison, i32 %63, i64 0
  %602 = shufflevector <2 x i32> %601, <2 x i32> poison, <2 x i32> zeroinitializer
  %603 = mul <2 x i32> %600, %602
  %604 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %605 = add <2 x i32> %603, %604
  %606 = sext <2 x i32> %605 to <2 x i64>
  %607 = insertelement <2 x float*> poison, float* %62, i64 0
  %608 = shufflevector <2 x float*> %607, <2 x float*> poison, <2 x i32> zeroinitializer
  %609 = getelementptr float, <2 x float*> %608, <2 x i64> %606
  %610 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %609, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift114 = shufflevector <2 x float> %610, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %611 = fadd reassoc ninf nsz <2 x float> %610, %shift114
  %612 = insertelement <2 x float> %611, float 2.000000e+00, i64 1
  %613 = insertelement <2 x float> poison, float %584, i64 0
  %614 = shufflevector <2 x float> %613, <2 x float> poison, <2 x i32> zeroinitializer
  %615 = fmul reassoc ninf nsz <2 x float> %612, %614
  %616 = fadd reassoc ninf nsz <2 x float> %615, %581
  br label %after_if42

after_if42:                                       ; preds = %true_block40, %after_if39
  %617 = phi <2 x float> [ %616, %true_block40 ], [ %581, %after_if39 ]
  br i1 %41, label %true_block43, label %after_if45

true_block43:                                     ; preds = %after_if42
  %618 = load float*, float** %24, align 8
  %619 = getelementptr float, float* %618, i64 16
  %620 = load float, float* %619, align 4
  %621 = insertelement <2 x i32> poison, i32 %64, i64 0
  %622 = shufflevector <2 x i32> %621, <2 x i32> poison, <2 x i32> zeroinitializer
  %623 = add <2 x i32> %622, <i32 16, i32 -16>
  %624 = getelementptr inbounds i8, i8* %49, i64 8
  %625 = bitcast i8* %624 to i32*
  %626 = load i32, i32* %625, align 4
  %627 = add i32 %626, -1
  %628 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %623, i1 true)
  %629 = insertelement <2 x i32> poison, i32 %627, i64 0
  %630 = shufflevector <2 x i32> %629, <2 x i32> poison, <2 x i32> zeroinitializer
  %631 = sub <2 x i32> %628, %630
  %632 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %631, <2 x i32> zeroinitializer)
  %633 = mul <2 x i32> %632, <i32 -2, i32 -2>
  %634 = add <2 x i32> %633, %628
  %635 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %634, <2 x i32> zeroinitializer)
  %636 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %630, <2 x i32> %635)
  %637 = insertelement <2 x i32> poison, i32 %63, i64 0
  %638 = shufflevector <2 x i32> %637, <2 x i32> poison, <2 x i32> zeroinitializer
  %639 = mul <2 x i32> %636, %638
  %640 = shufflevector <2 x i32> %68, <2 x i32> poison, <2 x i32> zeroinitializer
  %641 = add <2 x i32> %639, %640
  %642 = sext <2 x i32> %641 to <2 x i64>
  %643 = insertelement <2 x float*> poison, float* %62, i64 0
  %644 = shufflevector <2 x float*> %643, <2 x float*> poison, <2 x i32> zeroinitializer
  %645 = getelementptr float, <2 x float*> %644, <2 x i64> %642
  %646 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %645, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift115 = shufflevector <2 x float> %646, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %647 = fadd reassoc ninf nsz <2 x float> %646, %shift115
  %648 = insertelement <2 x float> %647, float 2.000000e+00, i64 1
  %649 = insertelement <2 x float> poison, float %620, i64 0
  %650 = shufflevector <2 x float> %649, <2 x float> poison, <2 x i32> zeroinitializer
  %651 = fmul reassoc ninf nsz <2 x float> %648, %650
  %652 = fadd reassoc ninf nsz <2 x float> %651, %617
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42
  %653 = phi <2 x float> [ %652, %true_block43 ], [ %617, %after_if42 ]
  %shift116 = shufflevector <2 x float> %653, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %654 = fdiv reassoc ninf nsz <2 x float> %653, %shift116
  %655 = extractelement <2 x float> %654, i64 0
  %656 = load float*, float** %45, align 8
  %657 = load i32, i32* %46, align 4
  %658 = mul i32 %657, %64
  %659 = add i32 %658, %69
  %660 = sext i32 %659 to i64
  %661 = getelementptr float, float* %656, i64 %660
  store float %655, float* %661, align 4
  %662 = add nsw i32 %.051100, 1
  %exitcond.not = icmp eq i32 %19, %662
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
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
