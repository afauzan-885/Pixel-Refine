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
define void @_downsample_2x_offset_kernel_c260_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_downsample_2x_offset_kernel_c260_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 2
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 3
  %25 = load i32, i32* %24, align 4
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 1, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %31 = add i32 %25, %17
  %32 = shl i32 %31, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %32, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.033 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %231, %for_loop_body ]
  %33 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %3, align 8
  %34 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %33, i64 0, i32 14
  %35 = load i8*, i8** %34, align 8
  %36 = getelementptr inbounds i8, i8* %35, i64 4
  %37 = bitcast i8* %36 to i32*
  %38 = load i32, i32* %37, align 4
  %39 = sdiv i32 %.033, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.033
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.033, 0
  %44 = icmp ne i32 %.033, %40
  %45 = and i1 %43, %42
  %46 = and i1 %45, %44
  %.neg4 = sext i1 %46 to i32
  %47 = add i32 %39, %.neg4
  %48 = add i32 %47, %23
  %49 = mul i32 %38, -2
  %50 = mul i32 %49, %47
  %51 = add i32 %lsr.iv, %50
  %52 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %53 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %52, i64 0, i32 0, i32 0, i32 0
  %54 = load i32, i32* %53, align 4
  %55 = add i32 %54, -1
  %56 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %52, i64 0, i32 0, i32 0, i32 1
  %57 = load i32, i32* %56, align 4
  %58 = add i32 %57, -1
  %59 = load float*, float** %27, align 8
  %60 = load i32, i32* %28, align 4
  %61 = tail call i32 @llvm.abs.i32(i32 %51, i1 true)
  %62 = sub i32 %61, %58
  %63 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %.neg8 = mul i32 %63, -2
  %64 = add i32 %.neg8, %61
  %65 = tail call i32 @llvm.smax.i32(i32 %64, i32 0)
  %66 = tail call i32 @llvm.smin.i32(i32 %58, i32 %65)
  %67 = insertelement <2 x i32> poison, i32 %55, i64 0
  %68 = shufflevector <2 x i32> %67, <2 x i32> poison, <2 x i32> zeroinitializer
  %69 = insertelement <2 x i32> poison, i32 %60, i64 0
  %70 = shufflevector <2 x i32> %69, <2 x i32> poison, <2 x i32> zeroinitializer
  %71 = insertelement <4 x i32> poison, i32 %51, i64 0
  %shuffle36 = shufflevector <4 x i32> %71, <4 x i32> poison, <4 x i32> zeroinitializer
  %72 = or <4 x i32> %shuffle36, <i32 1, i32 poison, i32 poison, i32 poison>
  %73 = add <4 x i32> %shuffle36, <i32 poison, i32 2, i32 -2, i32 -1>
  %74 = shufflevector <4 x i32> %72, <4 x i32> %73, <4 x i32> <i32 0, i32 5, i32 6, i32 7>
  %75 = call <4 x i32> @llvm.abs.v4i32(<4 x i32> %74, i1 true)
  %76 = insertelement <4 x i32> poison, i32 %58, i64 0
  %shuffle37 = shufflevector <4 x i32> %76, <4 x i32> poison, <4 x i32> zeroinitializer
  %77 = sub <4 x i32> %75, %shuffle37
  %78 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %77, <4 x i32> zeroinitializer)
  %79 = mul <4 x i32> %78, <i32 -2, i32 -2, i32 -2, i32 -2>
  %80 = add <4 x i32> %79, %75
  %81 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %80, <4 x i32> zeroinitializer)
  %82 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle37, <4 x i32> %81)
  %83 = shufflevector <4 x i32> %82, <4 x i32> poison, <8 x i32> <i32 2, i32 3, i32 undef, i32 0, i32 1, i32 undef, i32 undef, i32 undef>
  %84 = insertelement <8 x i32> %83, i32 %66, i64 2
  %shuffle34 = shufflevector <8 x i32> %84, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2>
  %85 = extractelement <4 x i32> %82, i64 0
  %86 = extractelement <4 x i32> %82, i64 1
  %87 = extractelement <4 x i32> %82, i64 2
  %88 = shl i32 %48, 1
  %89 = insertelement <2 x i32> poison, i32 %88, i64 0
  %90 = shufflevector <2 x i32> %89, <2 x i32> poison, <2 x i32> zeroinitializer
  %91 = add <2 x i32> %90, <i32 -2, i32 -1>
  %92 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %91, i1 true)
  %93 = sub <2 x i32> %92, %68
  %94 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %93, <2 x i32> zeroinitializer)
  %95 = mul <2 x i32> %94, <i32 -2, i32 -2>
  %96 = add <2 x i32> %95, %92
  %97 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %96, <2 x i32> zeroinitializer)
  %98 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %68, <2 x i32> %97)
  %99 = mul <2 x i32> %98, %70
  %shuffle = shufflevector <2 x i32> %99, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1>
  %100 = add <8 x i32> %shuffle, %shuffle34
  %101 = sext <8 x i32> %100 to <8 x i64>
  %102 = extractelement <8 x i64> %101, i64 0
  %103 = getelementptr float, float* %59, i64 %102
  %104 = load float, float* %103, align 4
  %105 = extractelement <8 x i64> %101, i64 1
  %106 = getelementptr float, float* %59, i64 %105
  %107 = load float, float* %106, align 4
  %108 = extractelement <8 x i64> %101, i64 2
  %109 = getelementptr float, float* %59, i64 %108
  %110 = load float, float* %109, align 4
  %111 = extractelement <8 x i64> %101, i64 3
  %112 = getelementptr float, float* %59, i64 %111
  %113 = load float, float* %112, align 4
  %114 = extractelement <8 x i64> %101, i64 4
  %115 = getelementptr float, float* %59, i64 %114
  %116 = load float, float* %115, align 4
  %117 = extractelement <8 x i64> %101, i64 5
  %118 = getelementptr float, float* %59, i64 %117
  %119 = load float, float* %118, align 4
  %120 = extractelement <8 x i64> %101, i64 6
  %121 = getelementptr float, float* %59, i64 %120
  %122 = load float, float* %121, align 4
  %123 = extractelement <8 x i64> %101, i64 7
  %124 = getelementptr float, float* %59, i64 %123
  %125 = load float, float* %124, align 4
  %126 = or i32 %88, 1
  %127 = insertelement <2 x i32> %89, i32 %126, i64 1
  %128 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %127, i1 true)
  %129 = sub <2 x i32> %128, %68
  %130 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %129, <2 x i32> zeroinitializer)
  %131 = mul <2 x i32> %130, <i32 -2, i32 -2>
  %132 = add <2 x i32> %131, %128
  %133 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %132, <2 x i32> zeroinitializer)
  %134 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %68, <2 x i32> %133)
  %135 = mul <2 x i32> %134, %70
  %shuffle38 = shufflevector <2 x i32> %135, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 0, i32 1>
  %136 = shufflevector <2 x i32> %99, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 undef, i32 undef>
  %137 = shufflevector <4 x i32> %136, <4 x i32> %shuffle38, <4 x i32> <i32 0, i32 1, i32 4, i32 4>
  %138 = add <4 x i32> %82, %137
  %139 = sext <4 x i32> %138 to <4 x i64>
  %140 = extractelement <4 x i64> %139, i64 0
  %141 = getelementptr float, float* %59, i64 %140
  %142 = load float, float* %141, align 4
  %143 = extractelement <4 x i64> %139, i64 1
  %144 = getelementptr float, float* %59, i64 %143
  %145 = load float, float* %144, align 4
  %146 = extractelement <4 x i64> %139, i64 2
  %147 = getelementptr float, float* %59, i64 %146
  %148 = load float, float* %147, align 4
  %149 = extractelement <4 x i64> %139, i64 3
  %150 = getelementptr float, float* %59, i64 %149
  %151 = load float, float* %150, align 4
  %152 = insertelement <4 x i32> poison, i32 %66, i64 0
  %153 = shufflevector <4 x i32> %152, <4 x i32> %82, <4 x i32> <i32 0, i32 4, i32 5, i32 6>
  %154 = add <4 x i32> %153, %shuffle38
  %155 = sext <4 x i32> %154 to <4 x i64>
  %156 = extractelement <4 x i64> %155, i64 0
  %157 = getelementptr float, float* %59, i64 %156
  %158 = load float, float* %157, align 4
  %159 = fmul reassoc ninf nsz float %158, 3.600000e+01
  %160 = extractelement <4 x i64> %155, i64 1
  %161 = getelementptr float, float* %59, i64 %160
  %162 = load float, float* %161, align 4
  %163 = extractelement <4 x i64> %155, i64 2
  %164 = getelementptr float, float* %59, i64 %163
  %165 = load float, float* %164, align 4
  %166 = extractelement <4 x i64> %155, i64 3
  %167 = getelementptr float, float* %59, i64 %166
  %168 = load float, float* %167, align 4
  %169 = extractelement <4 x i32> %82, i64 3
  %170 = extractelement <2 x i32> %135, i64 1
  %171 = add i32 %169, %170
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %59, i64 %172
  %174 = load float, float* %173, align 4
  %175 = add i32 %170, %66
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, float* %59, i64 %176
  %178 = load float, float* %177, align 4
  %179 = add i32 %85, %170
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, float* %59, i64 %180
  %182 = load float, float* %181, align 4
  %183 = add i32 %86, %170
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, float* %59, i64 %184
  %186 = load float, float* %185, align 4
  %187 = add i32 %88, 2
  %188 = tail call i32 @llvm.abs.i32(i32 %187, i1 true)
  %189 = sub i32 %188, %55
  %190 = tail call i32 @llvm.smax.i32(i32 %189, i32 0)
  %.neg14 = mul i32 %190, -2
  %191 = add i32 %.neg14, %188
  %192 = tail call i32 @llvm.smax.i32(i32 %191, i32 0)
  %193 = tail call i32 @llvm.smin.i32(i32 %55, i32 %192)
  %194 = mul i32 %193, %60
  %195 = add i32 %87, %194
  %196 = sext i32 %195 to i64
  %197 = getelementptr float, float* %59, i64 %196
  %198 = load float, float* %197, align 4
  %199 = add i32 %169, %194
  %200 = sext i32 %199 to i64
  %201 = getelementptr float, float* %59, i64 %200
  %202 = load float, float* %201, align 4
  %203 = add i32 %194, %66
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, float* %59, i64 %204
  %206 = load float, float* %205, align 4
  %207 = add i32 %85, %194
  %208 = sext i32 %207 to i64
  %209 = getelementptr float, float* %59, i64 %208
  %210 = load float, float* %209, align 4
  %211 = add i32 %86, %194
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, float* %59, i64 %212
  %214 = load float, float* %213, align 4
  %reass.add = fadd reassoc ninf nsz float %113, %107
  %reass.add15 = fadd reassoc ninf nsz float %reass.add, %119
  %reass.add16 = fadd reassoc ninf nsz float %reass.add15, %145
  %reass.add17 = fadd reassoc ninf nsz float %reass.add16, %168
  %reass.add18 = fadd reassoc ninf nsz float %reass.add17, %186
  %reass.add19 = fadd reassoc ninf nsz float %reass.add18, %202
  %reass.add20 = fadd reassoc ninf nsz float %reass.add19, %210
  %reass.mul = fmul reassoc ninf nsz float %reass.add20, 4.000000e+00
  %reass.add21 = fadd reassoc ninf nsz float %151, %125
  %reass.add22 = fadd reassoc ninf nsz float %reass.add21, %162
  %reass.add23 = fadd reassoc ninf nsz float %reass.add22, %178
  %reass.mul24 = fmul reassoc ninf nsz float %reass.add23, 2.400000e+01
  %reass.add25 = fadd reassoc ninf nsz float %142, %122
  %reass.add26 = fadd reassoc ninf nsz float %reass.add25, %174
  %reass.add27 = fadd reassoc ninf nsz float %reass.add26, %182
  %reass.mul28 = fmul reassoc ninf nsz float %reass.add27, 1.600000e+01
  %reass.add29 = fadd reassoc ninf nsz float %148, %110
  %reass.add30 = fadd reassoc ninf nsz float %reass.add29, %165
  %reass.add31 = fadd reassoc ninf nsz float %reass.add30, %206
  %reass.mul32 = fmul reassoc ninf nsz float %reass.add31, 6.000000e+00
  %215 = fadd reassoc ninf nsz float %116, %104
  %216 = fadd reassoc ninf nsz float %215, %159
  %217 = fadd reassoc ninf nsz float %216, %198
  %218 = fadd reassoc ninf nsz float %217, %reass.mul24
  %219 = fadd reassoc ninf nsz float %218, %reass.mul28
  %220 = fadd reassoc ninf nsz float %219, %214
  %221 = fadd reassoc ninf nsz float %220, %reass.mul32
  %222 = fadd reassoc ninf nsz float %221, %reass.mul
  %223 = fmul reassoc ninf nsz float %222, 3.906250e-03
  %224 = load float*, float** %29, align 8
  %225 = load i32, i32* %30, align 4
  %226 = sub i32 %225, %38
  %227 = mul i32 %226, %47
  %228 = add i32 %.033, %227
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %224, i64 %229
  store float %223, float* %230, align 4
  %231 = add nsw i32 %.033, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %231
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #5

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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.abs.v4i32(<4 x i32>, i1 immarg) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
