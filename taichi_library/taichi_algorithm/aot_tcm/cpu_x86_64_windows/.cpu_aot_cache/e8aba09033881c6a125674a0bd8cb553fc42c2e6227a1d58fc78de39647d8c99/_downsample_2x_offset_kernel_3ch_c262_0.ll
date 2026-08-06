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
define void @_downsample_2x_offset_kernel_3ch_c262_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = mul i32 %7, 3
  %9 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 14
  %12 = load i8*, i8** %11, align 8
  %13 = getelementptr inbounds i8, i8* %12, i64 4
  %14 = bitcast i8* %13 to i32*
  store i32 %8, i32* %14, align 4
  %15 = mul i32 %8, %4
  %16 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %9, align 8
  %17 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %16, i64 0, i32 14
  %18 = bitcast i8** %17 to i32**
  %19 = load i32*, i32** %18, align 8
  store i32 %15, i32* %19, align 4
  ret void
}

; Function Attrs: nounwind
define void @_downsample_2x_offset_kernel_3ch_c262_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 2
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 3
  %25 = load i32, i32* %24, align 4
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 1, i32 1
  %31 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.035 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %288, %for_loop_body ]
  %33 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %34 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %33, i64 0, i32 14
  %35 = load i8*, i8** %34, align 8
  %36 = getelementptr inbounds i8, i8* %35, i64 4
  %37 = bitcast i8* %36 to i32*
  %38 = load i32, i32* %37, align 4
  %39 = sdiv i32 %.035, %38
  %40 = mul i32 %39, %38
  %41 = xor i32 %38, %.035
  %42 = icmp slt i32 %41, 0
  %43 = icmp ne i32 %.035, 0
  %44 = icmp ne i32 %.035, %40
  %45 = and i1 %43, %42
  %46 = and i1 %45, %44
  %.neg4 = sext i1 %46 to i32
  %47 = add i32 %39, %.neg4
  %48 = mul i32 %47, %38
  %49 = mul i32 %38, -1
  %50 = mul i32 %49, %47
  %51 = add i32 %.035, %50
  %52 = sdiv i32 %51, 3
  %53 = icmp slt i32 %51, 0
  %54 = mul nsw i32 %52, 3
  %55 = icmp ne i32 %51, %54
  %56 = and i1 %53, %55
  %.neg5 = sext i1 %56 to i32
  %57 = add i32 %52, %.neg5
  %58 = mul i32 %52, -3
  %59 = mul nsw i32 %.neg5, 3
  %60 = sub i32 %58, %59
  %61 = add i32 %51, %60
  %62 = add i32 %47, %23
  %63 = shl i32 %62, 1
  %64 = add i32 %57, %25
  %65 = shl i32 %64, 1
  %66 = add i32 %63, -2
  %67 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %68 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %67, i64 0, i32 0, i32 0, i32 0
  %69 = load i32, i32* %68, align 4
  %70 = add i32 %69, -1
  %71 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %67, i64 0, i32 0, i32 0, i32 1
  %72 = load i32, i32* %71, align 4
  %73 = add i32 %72, -1
  %74 = load float*, float** %27, align 8
  %75 = load i32, i32* %28, align 4
  %76 = load i32, i32* %29, align 4
  %77 = tail call i32 @llvm.abs.i32(i32 %65, i1 true)
  %78 = sub i32 %77, %73
  %79 = tail call i32 @llvm.smax.i32(i32 %78, i32 0)
  %.neg10 = mul i32 %79, -2
  %80 = add i32 %.neg10, %77
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = tail call i32 @llvm.smin.i32(i32 %73, i32 %81)
  %83 = add i32 %63, -1
  %84 = insertelement <2 x i32> poison, i32 %66, i64 0
  %85 = insertelement <2 x i32> %84, i32 %83, i64 1
  %86 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %85, i1 true)
  %87 = insertelement <2 x i32> poison, i32 %70, i64 0
  %88 = shufflevector <2 x i32> %87, <2 x i32> poison, <2 x i32> zeroinitializer
  %89 = sub <2 x i32> %86, %88
  %90 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %89, <2 x i32> zeroinitializer)
  %91 = mul <2 x i32> %90, <i32 -2, i32 -2>
  %92 = add <2 x i32> %91, %86
  %93 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %92, <2 x i32> zeroinitializer)
  %94 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %88, <2 x i32> %93)
  %95 = insertelement <2 x i32> poison, i32 %75, i64 0
  %96 = shufflevector <2 x i32> %95, <2 x i32> poison, <2 x i32> zeroinitializer
  %97 = mul <2 x i32> %94, %96
  %shuffle36 = shufflevector <2 x i32> %97, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1>
  %98 = insertelement <8 x i32> poison, i32 %76, i64 0
  %shuffle37 = shufflevector <8 x i32> %98, <8 x i32> poison, <8 x i32> zeroinitializer
  %99 = insertelement <8 x i32> poison, i32 %61, i64 0
  %shuffle38 = shufflevector <8 x i32> %99, <8 x i32> poison, <8 x i32> zeroinitializer
  %100 = insertelement <4 x i32> poison, i32 %65, i64 0
  %shuffle40 = shufflevector <4 x i32> %100, <4 x i32> poison, <4 x i32> zeroinitializer
  %101 = or <4 x i32> %shuffle40, <i32 1, i32 poison, i32 poison, i32 poison>
  %102 = add <4 x i32> %shuffle40, <i32 poison, i32 2, i32 -2, i32 -1>
  %103 = shufflevector <4 x i32> %101, <4 x i32> %102, <4 x i32> <i32 0, i32 5, i32 6, i32 7>
  %104 = call <4 x i32> @llvm.abs.v4i32(<4 x i32> %103, i1 true)
  %105 = insertelement <4 x i32> poison, i32 %73, i64 0
  %shuffle41 = shufflevector <4 x i32> %105, <4 x i32> poison, <4 x i32> zeroinitializer
  %106 = sub <4 x i32> %104, %shuffle41
  %107 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %106, <4 x i32> zeroinitializer)
  %108 = mul <4 x i32> %107, <i32 -2, i32 -2, i32 -2, i32 -2>
  %109 = add <4 x i32> %108, %104
  %110 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %109, <4 x i32> zeroinitializer)
  %111 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle41, <4 x i32> %110)
  %112 = shufflevector <4 x i32> %111, <4 x i32> poison, <8 x i32> <i32 2, i32 3, i32 undef, i32 0, i32 1, i32 undef, i32 undef, i32 undef>
  %113 = insertelement <8 x i32> %112, i32 %82, i64 2
  %shuffle = shufflevector <8 x i32> %113, <8 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 4, i32 0, i32 1, i32 2>
  %114 = add <8 x i32> %shuffle, %shuffle36
  %115 = mul <8 x i32> %114, %shuffle37
  %116 = add <8 x i32> %115, %shuffle38
  %117 = sext <8 x i32> %116 to <8 x i64>
  %118 = extractelement <8 x i64> %117, i64 0
  %119 = getelementptr float, float* %74, i64 %118
  %120 = load float, float* %119, align 4
  %121 = extractelement <8 x i64> %117, i64 1
  %122 = getelementptr float, float* %74, i64 %121
  %123 = load float, float* %122, align 4
  %124 = extractelement <8 x i64> %117, i64 2
  %125 = getelementptr float, float* %74, i64 %124
  %126 = load float, float* %125, align 4
  %127 = extractelement <8 x i64> %117, i64 3
  %128 = getelementptr float, float* %74, i64 %127
  %129 = load float, float* %128, align 4
  %130 = extractelement <8 x i64> %117, i64 4
  %131 = getelementptr float, float* %74, i64 %130
  %132 = load float, float* %131, align 4
  %133 = extractelement <8 x i64> %117, i64 5
  %134 = getelementptr float, float* %74, i64 %133
  %135 = load float, float* %134, align 4
  %136 = extractelement <8 x i64> %117, i64 6
  %137 = getelementptr float, float* %74, i64 %136
  %138 = load float, float* %137, align 4
  %139 = extractelement <8 x i64> %117, i64 7
  %140 = getelementptr float, float* %74, i64 %139
  %141 = load float, float* %140, align 4
  %142 = shufflevector <2 x i32> %97, <2 x i32> undef, <4 x i32> <i32 1, i32 1, i32 undef, i32 undef>
  %143 = insertelement <4 x i32> poison, i32 %76, i64 0
  %shuffle42 = shufflevector <4 x i32> %143, <4 x i32> poison, <4 x i32> zeroinitializer
  %144 = insertelement <4 x i32> poison, i32 %61, i64 0
  %shuffle43 = shufflevector <4 x i32> %144, <4 x i32> poison, <4 x i32> zeroinitializer
  %145 = extractelement <4 x i32> %111, i64 0
  %146 = extractelement <4 x i32> %111, i64 1
  %147 = or i32 %63, 1
  %148 = insertelement <2 x i32> poison, i32 %63, i64 0
  %149 = insertelement <2 x i32> %148, i32 %147, i64 1
  %150 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %149, i1 true)
  %151 = sub <2 x i32> %150, %88
  %152 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %151, <2 x i32> zeroinitializer)
  %153 = mul <2 x i32> %152, <i32 -2, i32 -2>
  %154 = add <2 x i32> %153, %150
  %155 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %154, <2 x i32> zeroinitializer)
  %156 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %88, <2 x i32> %155)
  %157 = mul <2 x i32> %156, %96
  %shuffle44 = shufflevector <2 x i32> %157, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 0, i32 1>
  %158 = shufflevector <4 x i32> %142, <4 x i32> %shuffle44, <4 x i32> <i32 0, i32 1, i32 4, i32 4>
  %159 = add <4 x i32> %111, %158
  %160 = mul <4 x i32> %159, %shuffle42
  %161 = add <4 x i32> %160, %shuffle43
  %162 = sext <4 x i32> %161 to <4 x i64>
  %163 = extractelement <4 x i64> %162, i64 0
  %164 = getelementptr float, float* %74, i64 %163
  %165 = load float, float* %164, align 4
  %166 = extractelement <4 x i64> %162, i64 1
  %167 = getelementptr float, float* %74, i64 %166
  %168 = load float, float* %167, align 4
  %169 = extractelement <4 x i64> %162, i64 2
  %170 = getelementptr float, float* %74, i64 %169
  %171 = load float, float* %170, align 4
  %172 = extractelement <4 x i64> %162, i64 3
  %173 = getelementptr float, float* %74, i64 %172
  %174 = load float, float* %173, align 4
  %175 = insertelement <4 x i32> poison, i32 %82, i64 0
  %176 = shufflevector <4 x i32> %175, <4 x i32> %111, <4 x i32> <i32 0, i32 4, i32 5, i32 6>
  %177 = add <4 x i32> %176, %shuffle44
  %178 = mul <4 x i32> %177, %shuffle42
  %179 = add <4 x i32> %178, %shuffle43
  %180 = sext <4 x i32> %179 to <4 x i64>
  %181 = extractelement <4 x i64> %180, i64 0
  %182 = getelementptr float, float* %74, i64 %181
  %183 = load float, float* %182, align 4
  %184 = fmul reassoc ninf nsz float %183, 3.600000e+01
  %185 = extractelement <4 x i64> %180, i64 1
  %186 = getelementptr float, float* %74, i64 %185
  %187 = load float, float* %186, align 4
  %188 = extractelement <4 x i64> %180, i64 2
  %189 = getelementptr float, float* %74, i64 %188
  %190 = load float, float* %189, align 4
  %191 = extractelement <4 x i64> %180, i64 3
  %192 = getelementptr float, float* %74, i64 %191
  %193 = load float, float* %192, align 4
  %194 = extractelement <2 x i32> %157, i64 1
  %195 = add <4 x i32> %111, %shuffle44
  %196 = extractelement <4 x i32> %195, i64 3
  %197 = mul i32 %196, %76
  %198 = sub i32 %197, %48
  %199 = mul i32 %57, 3
  %200 = sub i32 %198, %199
  %201 = add i32 %.035, %200
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %74, i64 %202
  %204 = load float, float* %203, align 4
  %205 = add i32 %82, %194
  %206 = mul i32 %205, %76
  %207 = sub i32 %206, %48
  %208 = sub i32 %207, %199
  %209 = add i32 %.035, %208
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, float* %74, i64 %210
  %212 = load float, float* %211, align 4
  %213 = add i32 %63, 2
  %214 = tail call i32 @llvm.abs.i32(i32 %213, i1 true)
  %215 = sub i32 %214, %70
  %216 = tail call i32 @llvm.smax.i32(i32 %215, i32 0)
  %.neg16 = mul i32 %216, -2
  %217 = add i32 %.neg16, %214
  %218 = tail call i32 @llvm.smax.i32(i32 %217, i32 0)
  %219 = tail call i32 @llvm.smin.i32(i32 %70, i32 %218)
  %220 = mul i32 %219, %75
  %221 = insertelement <4 x i32> poison, i32 %194, i64 0
  %222 = insertelement <4 x i32> %221, i32 %194, i64 1
  %223 = insertelement <4 x i32> %222, i32 %220, i64 2
  %224 = insertelement <4 x i32> %223, i32 %220, i64 3
  %225 = add <4 x i32> %111, %224
  %226 = mul <4 x i32> %225, %shuffle42
  %227 = add <4 x i32> %226, %shuffle43
  %228 = extractelement <4 x i32> %227, i64 0
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %74, i64 %229
  %231 = load float, float* %230, align 4
  %232 = extractelement <4 x i32> %227, i64 1
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, float* %74, i64 %233
  %235 = load float, float* %234, align 4
  %236 = extractelement <4 x i32> %227, i64 2
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, float* %74, i64 %237
  %239 = load float, float* %238, align 4
  %240 = extractelement <4 x i32> %227, i64 3
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, float* %74, i64 %241
  %243 = load float, float* %242, align 4
  %244 = add i32 %82, %220
  %245 = mul i32 %244, %76
  %246 = sub i32 %245, %48
  %247 = sub i32 %246, %199
  %248 = add i32 %.035, %247
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, float* %74, i64 %249
  %251 = load float, float* %250, align 4
  %252 = add i32 %145, %220
  %253 = mul i32 %252, %76
  %254 = sub i32 %253, %48
  %255 = sub i32 %254, %199
  %256 = add i32 %.035, %255
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, float* %74, i64 %257
  %259 = load float, float* %258, align 4
  %260 = add i32 %146, %220
  %261 = mul i32 %260, %76
  %262 = sub i32 %261, %48
  %263 = sub i32 %262, %199
  %264 = add i32 %.035, %263
  %265 = sext i32 %264 to i64
  %266 = getelementptr float, float* %74, i64 %265
  %267 = load float, float* %266, align 4
  %reass.add = fadd reassoc ninf nsz float %129, %123
  %reass.add17 = fadd reassoc ninf nsz float %reass.add, %135
  %reass.add18 = fadd reassoc ninf nsz float %reass.add17, %168
  %reass.add19 = fadd reassoc ninf nsz float %reass.add18, %193
  %reass.add20 = fadd reassoc ninf nsz float %reass.add19, %235
  %reass.add21 = fadd reassoc ninf nsz float %reass.add20, %243
  %reass.add22 = fadd reassoc ninf nsz float %reass.add21, %259
  %reass.mul = fmul reassoc ninf nsz float %reass.add22, 4.000000e+00
  %reass.add23 = fadd reassoc ninf nsz float %174, %141
  %reass.add24 = fadd reassoc ninf nsz float %reass.add23, %187
  %reass.add25 = fadd reassoc ninf nsz float %reass.add24, %212
  %reass.mul26 = fmul reassoc ninf nsz float %reass.add25, 2.400000e+01
  %reass.add27 = fadd reassoc ninf nsz float %165, %138
  %reass.add28 = fadd reassoc ninf nsz float %reass.add27, %204
  %reass.add29 = fadd reassoc ninf nsz float %reass.add28, %231
  %reass.mul30 = fmul reassoc ninf nsz float %reass.add29, 1.600000e+01
  %reass.add31 = fadd reassoc ninf nsz float %171, %126
  %reass.add32 = fadd reassoc ninf nsz float %reass.add31, %190
  %reass.add33 = fadd reassoc ninf nsz float %reass.add32, %251
  %reass.mul34 = fmul reassoc ninf nsz float %reass.add33, 6.000000e+00
  %268 = fadd reassoc ninf nsz float %132, %120
  %269 = fadd reassoc ninf nsz float %268, %184
  %270 = fadd reassoc ninf nsz float %269, %239
  %271 = fadd reassoc ninf nsz float %270, %reass.mul26
  %272 = fadd reassoc ninf nsz float %271, %reass.mul30
  %273 = fadd reassoc ninf nsz float %272, %267
  %274 = fadd reassoc ninf nsz float %273, %reass.mul34
  %275 = fadd reassoc ninf nsz float %274, %reass.mul
  %276 = fmul reassoc ninf nsz float %275, 3.906250e-03
  %277 = load float*, float** %30, align 8
  %278 = load i32, i32* %31, align 4
  %279 = load i32, i32* %32, align 4
  %280 = mul i32 %278, %47
  %281 = add i32 %280, %57
  %282 = mul i32 %281, %279
  %283 = sub i32 %282, %48
  %284 = sub i32 %283, %199
  %285 = add i32 %.035, %284
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, float* %277, i64 %286
  store float %276, float* %287, align 4
  %288 = add nsw i32 %.035, 1
  %exitcond.not = icmp eq i32 %19, %288
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
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
