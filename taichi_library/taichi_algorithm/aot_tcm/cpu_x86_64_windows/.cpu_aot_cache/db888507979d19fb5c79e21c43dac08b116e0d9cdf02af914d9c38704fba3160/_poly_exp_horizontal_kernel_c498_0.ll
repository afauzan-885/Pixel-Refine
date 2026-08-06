; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext*, void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { i8*, %struct.LLVMRuntime*, i32, i64* }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager*], [1024 x %struct.NodeManager*], [1024 x i8*], i8*, %struct.RandState*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { i8*, i8*, i64 }
%struct.ListManager = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime* }
%struct.NodeManager = type { %struct.LLVMRuntime*, i32, i32, i32, i32, %struct.ListManager*, %struct.ListManager*, %struct.ListManager*, i32 }
%struct.RandState = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_poly_exp_horizontal_kernel_c498_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %1, i64 0, i32 3
  %6 = load i32, i32* %5, align 4
  %7 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %8 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %7, align 8
  %9 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %8, i64 0, i32 14
  %10 = load i8*, i8** %9, align 8
  %11 = getelementptr inbounds i8, i8* %10, i64 8
  %12 = bitcast i8* %11 to i32*
  store i32 %6, i32* %12, align 4
  %13 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %14 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %7, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 4
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = mul i32 %13, %4
  %20 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %7, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %20, i64 0, i32 14
  %22 = bitcast i8** %21 to i32**
  %23 = load i32*, i32** %22, align 8
  store i32 %19, i32* %23, align 4
  ret void
}

; Function Attrs: nounwind
define void @_poly_exp_horizontal_kernel_c498_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext* %context, %struct.RuntimeContext** %4, align 8
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext*, i8*, i32)* @function_body, void (%struct.RuntimeContext*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 9
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 5
  %25 = load float, float* %24, align 4
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 6
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 7
  %29 = load float, float* %28, align 4
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 8
  %31 = load float, float* %30, align 4
  %32 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 4, i32 1
  %33 = load float*, float** %32, align 8
  %34 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 4, i32 0, i32 1
  %35 = icmp sgt i32 %23, 0
  %36 = icmp sgt i32 %23, 1
  %37 = icmp sgt i32 %23, 2
  %38 = icmp sgt i32 %23, 3
  %39 = icmp sgt i32 %23, 4
  %40 = icmp sgt i32 %23, 5
  %41 = icmp sgt i32 %23, 6
  %42 = icmp sgt i32 %23, 7
  %43 = icmp sgt i32 %23, 8
  %44 = icmp sgt i32 %23, 9
  %45 = icmp sgt i32 %23, 10
  %46 = icmp slt i32 %17, %19
  br i1 %46, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %47 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 0, i32 1
  %48 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %49 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %50 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 1, i32 1
  %51 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %52 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32, i32 }, float* }, float, float, float, float, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if30, %for_loop_body.lr.ph
  %.0124126 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %832, %after_if30 ]
  %53 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %53, i64 0, i32 14
  %55 = load i8*, i8** %54, align 8
  %56 = getelementptr inbounds i8, i8* %55, i64 4
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = sdiv i32 %.0124126, %58
  %60 = mul i32 %59, %58
  %61 = xor i32 %58, %.0124126
  %62 = icmp slt i32 %61, 0
  %63 = icmp ne i32 %.0124126, 0
  %64 = icmp ne i32 %.0124126, %60
  %65 = and i1 %63, %62
  %66 = and i1 %65, %64
  %.neg125 = sext i1 %66 to i32
  %67 = load float*, float** %47, align 8
  %68 = load i32, i32* %48, align 4
  %69 = load i32, i32* %49, align 4
  %70 = add i32 %59, %.neg125
  %71 = mul i32 %70, %58
  %72 = insertelement <2 x i32> poison, i32 %.0124126, i64 0
  %73 = insertelement <2 x i32> %72, i32 %68, i64 1
  %74 = insertelement <2 x i32> poison, i32 %71, i64 0
  %75 = insertelement <2 x i32> %74, i32 %70, i64 1
  %76 = sub <2 x i32> %73, %75
  %77 = mul <2 x i32> %73, %75
  %78 = extractelement <2 x i32> %76, i64 0
  %79 = extractelement <2 x i32> %77, i64 1
  %80 = add i32 %78, %79
  %81 = mul i32 %80, %69
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, float* %67, i64 %82
  %84 = load float, float* %83, align 4
  %85 = load float, float* %33, align 4
  %86 = fmul reassoc ninf nsz float %85, %84
  %87 = insertelement <2 x i32> poison, i32 %81, i64 0
  %88 = shufflevector <2 x i32> %87, <2 x i32> poison, <2 x i32> zeroinitializer
  %89 = add <2 x i32> %88, <i32 1, i32 2>
  %90 = sext <2 x i32> %89 to <2 x i64>
  %91 = insertelement <2 x float*> poison, float* %67, i64 0
  %92 = shufflevector <2 x float*> %91, <2 x float*> poison, <2 x i32> zeroinitializer
  %93 = getelementptr float, <2 x float*> %92, <2 x i64> %90
  %94 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %93, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %95 = insertelement <2 x float> poison, float %85, i64 0
  %96 = shufflevector <2 x float> %95, <2 x float> poison, <2 x i32> zeroinitializer
  %97 = fmul reassoc ninf nsz <2 x float> %94, %96
  br i1 %35, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if30
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %98 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %99 = add <2 x i32> %98, <i32 1, i32 -1>
  %100 = getelementptr inbounds i8, i8* %55, i64 8
  %101 = bitcast i8* %100 to i32*
  %102 = load i32, i32* %101, align 4
  %103 = add i32 %102, -1
  %104 = insertelement <2 x i32> poison, i32 %103, i64 0
  %105 = shufflevector <2 x i32> %104, <2 x i32> poison, <2 x i32> zeroinitializer
  %106 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %99, <2 x i32> %105)
  %107 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %106, <2 x i32> zeroinitializer)
  %108 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %109 = add <2 x i32> %107, %108
  %110 = insertelement <2 x i32> poison, i32 %69, i64 0
  %111 = shufflevector <2 x i32> %110, <2 x i32> poison, <2 x i32> zeroinitializer
  %112 = mul <2 x i32> %109, %111
  %113 = sext <2 x i32> %112 to <2 x i64>
  %114 = getelementptr float, <2 x float*> %92, <2 x i64> %113
  %115 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %114, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %116 = extractelement <2 x float> %115, i64 0
  %117 = extractelement <2 x float> %115, i64 1
  %118 = fadd reassoc ninf nsz float %116, %117
  %119 = load float*, float** %32, align 8
  %120 = load i32, i32* %34, align 4
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, float* %119, i64 %121
  %123 = load float, float* %122, align 4
  %124 = fmul reassoc ninf nsz float %123, %118
  %125 = fadd reassoc ninf nsz float %124, %86
  %126 = add i32 %120, 2
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, float* %119, i64 %127
  %129 = load float, float* %128, align 4
  %130 = fmul reassoc ninf nsz float %129, %118
  %131 = fsub reassoc ninf nsz float %116, %117
  %132 = add i32 %120, 1
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %119, i64 %133
  %135 = load float, float* %134, align 4
  %136 = fmul reassoc ninf nsz float %135, %131
  %137 = shufflevector <2 x i32> %112, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %138 = add <2 x i32> %137, <i32 1, i32 2>
  %139 = sext <2 x i32> %138 to <2 x i64>
  %140 = getelementptr float, <2 x float*> %92, <2 x i64> %139
  %141 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %140, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %142 = shufflevector <2 x i32> %112, <2 x i32> poison, <2 x i32> zeroinitializer
  %143 = add <2 x i32> %142, <i32 1, i32 2>
  %144 = sext <2 x i32> %143 to <2 x i64>
  %145 = getelementptr float, <2 x float*> %92, <2 x i64> %144
  %146 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %145, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %147 = fadd reassoc ninf nsz <2 x float> %146, %141
  %148 = insertelement <2 x float> poison, float %123, i64 0
  %149 = shufflevector <2 x float> %148, <2 x float> poison, <2 x i32> zeroinitializer
  %150 = fmul reassoc ninf nsz <2 x float> %149, %147
  %151 = fsub reassoc ninf nsz <2 x float> %146, %141
  %152 = extractelement <2 x float> %151, i64 0
  %153 = fmul reassoc ninf nsz float %135, %152
  %154 = fadd reassoc ninf nsz <2 x float> %150, %97
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %.0113 = phi float [ %125, %true_block ], [ %86, %for_loop_body ]
  %.0102 = phi float [ %136, %true_block ], [ 0.000000e+00, %for_loop_body ]
  %.080 = phi float [ %130, %true_block ], [ 0.000000e+00, %for_loop_body ]
  %.0 = phi float [ %153, %true_block ], [ 0.000000e+00, %for_loop_body ]
  %155 = phi <2 x float> [ %154, %true_block ], [ %97, %for_loop_body ]
  br i1 %36, label %true_block1, label %after_if3

true_block1:                                      ; preds = %after_if
  %156 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %157 = add <2 x i32> %156, <i32 2, i32 -2>
  %158 = getelementptr inbounds i8, i8* %55, i64 8
  %159 = bitcast i8* %158 to i32*
  %160 = load i32, i32* %159, align 4
  %161 = add i32 %160, -1
  %162 = insertelement <2 x i32> poison, i32 %161, i64 0
  %163 = shufflevector <2 x i32> %162, <2 x i32> poison, <2 x i32> zeroinitializer
  %164 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %157, <2 x i32> %163)
  %165 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %164, <2 x i32> zeroinitializer)
  %166 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %167 = add <2 x i32> %165, %166
  %168 = insertelement <2 x i32> poison, i32 %69, i64 0
  %169 = shufflevector <2 x i32> %168, <2 x i32> poison, <2 x i32> zeroinitializer
  %170 = mul <2 x i32> %167, %169
  %171 = sext <2 x i32> %170 to <2 x i64>
  %172 = getelementptr float, <2 x float*> %92, <2 x i64> %171
  %173 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %172, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %174 = extractelement <2 x float> %173, i64 0
  %175 = extractelement <2 x float> %173, i64 1
  %176 = fadd reassoc ninf nsz float %174, %175
  %177 = load float*, float** %32, align 8
  %178 = load i32, i32* %34, align 4
  %179 = shl i32 %178, 1
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, float* %177, i64 %180
  %182 = load float, float* %181, align 4
  %183 = fmul reassoc ninf nsz float %182, %176
  %184 = fadd reassoc ninf nsz float %183, %.0113
  %185 = add i32 %179, 2
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %177, i64 %186
  %188 = load float, float* %187, align 4
  %189 = fmul reassoc ninf nsz float %188, %176
  %190 = fadd reassoc ninf nsz float %189, %.080
  %191 = fsub reassoc ninf nsz float %174, %175
  %192 = getelementptr float, float* %181, i64 1
  %193 = load float, float* %192, align 4
  %194 = fmul reassoc ninf nsz float %193, %191
  %195 = fadd reassoc ninf nsz float %194, %.0102
  %196 = shufflevector <2 x i32> %170, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %197 = add <2 x i32> %196, <i32 1, i32 2>
  %198 = sext <2 x i32> %197 to <2 x i64>
  %199 = getelementptr float, <2 x float*> %92, <2 x i64> %198
  %200 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %199, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %201 = shufflevector <2 x i32> %170, <2 x i32> poison, <2 x i32> zeroinitializer
  %202 = add <2 x i32> %201, <i32 1, i32 2>
  %203 = sext <2 x i32> %202 to <2 x i64>
  %204 = getelementptr float, <2 x float*> %92, <2 x i64> %203
  %205 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %204, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %206 = fadd reassoc ninf nsz <2 x float> %205, %200
  %207 = insertelement <2 x float> poison, float %182, i64 0
  %208 = shufflevector <2 x float> %207, <2 x float> poison, <2 x i32> zeroinitializer
  %209 = fmul reassoc ninf nsz <2 x float> %208, %206
  %210 = fsub reassoc ninf nsz <2 x float> %205, %200
  %211 = extractelement <2 x float> %210, i64 0
  %212 = fmul reassoc ninf nsz float %193, %211
  %213 = fadd reassoc ninf nsz float %212, %.0
  %214 = fadd reassoc ninf nsz <2 x float> %209, %155
  br label %after_if3

after_if3:                                        ; preds = %true_block1, %after_if
  %.1114 = phi float [ %184, %true_block1 ], [ %.0113, %after_if ]
  %.1103 = phi float [ %195, %true_block1 ], [ %.0102, %after_if ]
  %.181 = phi float [ %190, %true_block1 ], [ %.080, %after_if ]
  %.1 = phi float [ %213, %true_block1 ], [ %.0, %after_if ]
  %215 = phi <2 x float> [ %214, %true_block1 ], [ %155, %after_if ]
  br i1 %37, label %true_block4, label %after_if6

true_block4:                                      ; preds = %after_if3
  %216 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %217 = add <2 x i32> %216, <i32 3, i32 -3>
  %218 = getelementptr inbounds i8, i8* %55, i64 8
  %219 = bitcast i8* %218 to i32*
  %220 = load i32, i32* %219, align 4
  %221 = add i32 %220, -1
  %222 = insertelement <2 x i32> poison, i32 %221, i64 0
  %223 = shufflevector <2 x i32> %222, <2 x i32> poison, <2 x i32> zeroinitializer
  %224 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %217, <2 x i32> %223)
  %225 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %224, <2 x i32> zeroinitializer)
  %226 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %227 = add <2 x i32> %225, %226
  %228 = insertelement <2 x i32> poison, i32 %69, i64 0
  %229 = shufflevector <2 x i32> %228, <2 x i32> poison, <2 x i32> zeroinitializer
  %230 = mul <2 x i32> %227, %229
  %231 = sext <2 x i32> %230 to <2 x i64>
  %232 = getelementptr float, <2 x float*> %92, <2 x i64> %231
  %233 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %232, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %234 = extractelement <2 x float> %233, i64 0
  %235 = extractelement <2 x float> %233, i64 1
  %236 = fadd reassoc ninf nsz float %234, %235
  %237 = load float*, float** %32, align 8
  %238 = load i32, i32* %34, align 4
  %239 = mul i32 %238, 3
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %237, i64 %240
  %242 = load float, float* %241, align 4
  %243 = fmul reassoc ninf nsz float %242, %236
  %244 = fadd reassoc ninf nsz float %243, %.1114
  %245 = add i32 %239, 2
  %246 = sext i32 %245 to i64
  %247 = getelementptr float, float* %237, i64 %246
  %248 = load float, float* %247, align 4
  %249 = fmul reassoc ninf nsz float %248, %236
  %250 = fadd reassoc ninf nsz float %249, %.181
  %251 = fsub reassoc ninf nsz float %234, %235
  %252 = add i32 %239, 1
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, float* %237, i64 %253
  %255 = load float, float* %254, align 4
  %256 = fmul reassoc ninf nsz float %255, %251
  %257 = fadd reassoc ninf nsz float %256, %.1103
  %258 = shufflevector <2 x i32> %230, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %259 = add <2 x i32> %258, <i32 1, i32 2>
  %260 = sext <2 x i32> %259 to <2 x i64>
  %261 = getelementptr float, <2 x float*> %92, <2 x i64> %260
  %262 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %261, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %263 = shufflevector <2 x i32> %230, <2 x i32> poison, <2 x i32> zeroinitializer
  %264 = add <2 x i32> %263, <i32 1, i32 2>
  %265 = sext <2 x i32> %264 to <2 x i64>
  %266 = getelementptr float, <2 x float*> %92, <2 x i64> %265
  %267 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %266, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %268 = fadd reassoc ninf nsz <2 x float> %267, %262
  %269 = insertelement <2 x float> poison, float %242, i64 0
  %270 = shufflevector <2 x float> %269, <2 x float> poison, <2 x i32> zeroinitializer
  %271 = fmul reassoc ninf nsz <2 x float> %270, %268
  %272 = fsub reassoc ninf nsz <2 x float> %267, %262
  %273 = extractelement <2 x float> %272, i64 0
  %274 = fmul reassoc ninf nsz float %255, %273
  %275 = fadd reassoc ninf nsz float %274, %.1
  %276 = fadd reassoc ninf nsz <2 x float> %271, %215
  br label %after_if6

after_if6:                                        ; preds = %true_block4, %after_if3
  %.2115 = phi float [ %244, %true_block4 ], [ %.1114, %after_if3 ]
  %.2104 = phi float [ %257, %true_block4 ], [ %.1103, %after_if3 ]
  %.282 = phi float [ %250, %true_block4 ], [ %.181, %after_if3 ]
  %.2 = phi float [ %275, %true_block4 ], [ %.1, %after_if3 ]
  %277 = phi <2 x float> [ %276, %true_block4 ], [ %215, %after_if3 ]
  %278 = extractelement <2 x float> %277, i64 0
  %279 = extractelement <2 x float> %277, i64 1
  br i1 %38, label %true_block7, label %after_if9

true_block7:                                      ; preds = %after_if6
  %280 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %281 = add <2 x i32> %280, <i32 4, i32 -4>
  %282 = getelementptr inbounds i8, i8* %55, i64 8
  %283 = bitcast i8* %282 to i32*
  %284 = load i32, i32* %283, align 4
  %285 = add i32 %284, -1
  %286 = insertelement <2 x i32> poison, i32 %285, i64 0
  %287 = shufflevector <2 x i32> %286, <2 x i32> poison, <2 x i32> zeroinitializer
  %288 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %281, <2 x i32> %287)
  %289 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %288, <2 x i32> zeroinitializer)
  %290 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %291 = add <2 x i32> %289, %290
  %292 = insertelement <2 x i32> poison, i32 %69, i64 0
  %293 = shufflevector <2 x i32> %292, <2 x i32> poison, <2 x i32> zeroinitializer
  %294 = mul <2 x i32> %291, %293
  %295 = sext <2 x i32> %294 to <2 x i64>
  %296 = extractelement <2 x i64> %295, i64 1
  %297 = getelementptr float, float* %67, i64 %296
  %298 = load float, float* %297, align 4
  %299 = extractelement <2 x i64> %295, i64 0
  %300 = getelementptr float, float* %67, i64 %299
  %301 = load float, float* %300, align 4
  %302 = add <2 x i32> %294, <i32 1, i32 1>
  %303 = sext <2 x i32> %302 to <2 x i64>
  %304 = getelementptr float, <2 x float*> %92, <2 x i64> %303
  %305 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %304, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %306 = add <2 x i32> %294, <i32 2, i32 2>
  %307 = sext <2 x i32> %306 to <2 x i64>
  %308 = getelementptr float, <2 x float*> %92, <2 x i64> %307
  %309 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %308, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %310 = fadd reassoc ninf nsz float %301, %298
  %311 = load float*, float** %32, align 8
  %312 = load i32, i32* %34, align 4
  %313 = shl i32 %312, 2
  %314 = sext i32 %313 to i64
  %315 = getelementptr float, float* %311, i64 %314
  %316 = load float, float* %315, align 4
  %317 = fmul reassoc ninf nsz float %316, %310
  %318 = fadd reassoc ninf nsz float %317, %.2115
  %319 = getelementptr float, float* %315, i64 2
  %320 = load float, float* %319, align 4
  %321 = fmul reassoc ninf nsz float %320, %310
  %322 = fadd reassoc ninf nsz float %321, %.282
  %323 = fsub reassoc ninf nsz float %301, %298
  %324 = getelementptr float, float* %315, i64 1
  %325 = load float, float* %324, align 4
  %326 = fmul reassoc ninf nsz float %325, %323
  %327 = fadd reassoc ninf nsz float %326, %.2104
  %328 = extractelement <2 x float> %305, i64 0
  %329 = extractelement <2 x float> %305, i64 1
  %330 = fadd reassoc ninf nsz float %328, %329
  %331 = fmul reassoc ninf nsz float %316, %330
  %332 = fadd reassoc ninf nsz float %331, %278
  %333 = fsub reassoc ninf nsz float %328, %329
  %334 = fmul reassoc ninf nsz float %325, %333
  %335 = fadd reassoc ninf nsz float %334, %.2
  %shift = shufflevector <2 x float> %309, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %336 = fadd reassoc ninf nsz <2 x float> %309, %shift
  %337 = extractelement <2 x float> %336, i64 0
  %338 = fmul reassoc ninf nsz float %316, %337
  %339 = fadd reassoc ninf nsz float %338, %279
  br label %after_if9

after_if9:                                        ; preds = %true_block7, %after_if6
  %.3116 = phi float [ %318, %true_block7 ], [ %.2115, %after_if6 ]
  %.3105 = phi float [ %327, %true_block7 ], [ %.2104, %after_if6 ]
  %.394 = phi float [ %332, %true_block7 ], [ %278, %after_if6 ]
  %.383 = phi float [ %322, %true_block7 ], [ %.282, %after_if6 ]
  %.372 = phi float [ %339, %true_block7 ], [ %279, %after_if6 ]
  %.3 = phi float [ %335, %true_block7 ], [ %.2, %after_if6 ]
  br i1 %39, label %true_block10, label %after_if12

true_block10:                                     ; preds = %after_if9
  %340 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %341 = add <2 x i32> %340, <i32 5, i32 -5>
  %342 = getelementptr inbounds i8, i8* %55, i64 8
  %343 = bitcast i8* %342 to i32*
  %344 = load i32, i32* %343, align 4
  %345 = add i32 %344, -1
  %346 = insertelement <2 x i32> poison, i32 %345, i64 0
  %347 = shufflevector <2 x i32> %346, <2 x i32> poison, <2 x i32> zeroinitializer
  %348 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %341, <2 x i32> %347)
  %349 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %348, <2 x i32> zeroinitializer)
  %350 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %351 = add <2 x i32> %349, %350
  %352 = insertelement <2 x i32> poison, i32 %69, i64 0
  %353 = shufflevector <2 x i32> %352, <2 x i32> poison, <2 x i32> zeroinitializer
  %354 = mul <2 x i32> %351, %353
  %355 = sext <2 x i32> %354 to <2 x i64>
  %356 = extractelement <2 x i64> %355, i64 1
  %357 = getelementptr float, float* %67, i64 %356
  %358 = load float, float* %357, align 4
  %359 = extractelement <2 x i64> %355, i64 0
  %360 = getelementptr float, float* %67, i64 %359
  %361 = load float, float* %360, align 4
  %362 = add <2 x i32> %354, <i32 1, i32 1>
  %363 = sext <2 x i32> %362 to <2 x i64>
  %364 = getelementptr float, <2 x float*> %92, <2 x i64> %363
  %365 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %364, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %366 = add <2 x i32> %354, <i32 2, i32 2>
  %367 = sext <2 x i32> %366 to <2 x i64>
  %368 = getelementptr float, <2 x float*> %92, <2 x i64> %367
  %369 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %368, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %370 = fadd reassoc ninf nsz float %361, %358
  %371 = load float*, float** %32, align 8
  %372 = load i32, i32* %34, align 4
  %373 = mul i32 %372, 5
  %374 = sext i32 %373 to i64
  %375 = getelementptr float, float* %371, i64 %374
  %376 = load float, float* %375, align 4
  %377 = fmul reassoc ninf nsz float %376, %370
  %378 = fadd reassoc ninf nsz float %377, %.3116
  %379 = add i32 %373, 2
  %380 = sext i32 %379 to i64
  %381 = getelementptr float, float* %371, i64 %380
  %382 = load float, float* %381, align 4
  %383 = fmul reassoc ninf nsz float %382, %370
  %384 = fadd reassoc ninf nsz float %383, %.383
  %385 = fsub reassoc ninf nsz float %361, %358
  %386 = add i32 %373, 1
  %387 = sext i32 %386 to i64
  %388 = getelementptr float, float* %371, i64 %387
  %389 = load float, float* %388, align 4
  %390 = fmul reassoc ninf nsz float %389, %385
  %391 = fadd reassoc ninf nsz float %390, %.3105
  %392 = extractelement <2 x float> %365, i64 0
  %393 = extractelement <2 x float> %365, i64 1
  %394 = fadd reassoc ninf nsz float %392, %393
  %395 = fmul reassoc ninf nsz float %376, %394
  %396 = fadd reassoc ninf nsz float %395, %.394
  %397 = fsub reassoc ninf nsz float %392, %393
  %398 = fmul reassoc ninf nsz float %389, %397
  %399 = fadd reassoc ninf nsz float %398, %.3
  %shift127 = shufflevector <2 x float> %369, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %400 = fadd reassoc ninf nsz <2 x float> %369, %shift127
  %401 = extractelement <2 x float> %400, i64 0
  %402 = fmul reassoc ninf nsz float %376, %401
  %403 = fadd reassoc ninf nsz float %402, %.372
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %after_if9
  %.4117 = phi float [ %378, %true_block10 ], [ %.3116, %after_if9 ]
  %.4106 = phi float [ %391, %true_block10 ], [ %.3105, %after_if9 ]
  %.495 = phi float [ %396, %true_block10 ], [ %.394, %after_if9 ]
  %.484 = phi float [ %384, %true_block10 ], [ %.383, %after_if9 ]
  %.473 = phi float [ %403, %true_block10 ], [ %.372, %after_if9 ]
  %.4 = phi float [ %399, %true_block10 ], [ %.3, %after_if9 ]
  br i1 %40, label %true_block13, label %after_if15

true_block13:                                     ; preds = %after_if12
  %404 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %405 = add <2 x i32> %404, <i32 6, i32 -6>
  %406 = getelementptr inbounds i8, i8* %55, i64 8
  %407 = bitcast i8* %406 to i32*
  %408 = load i32, i32* %407, align 4
  %409 = add i32 %408, -1
  %410 = insertelement <2 x i32> poison, i32 %409, i64 0
  %411 = shufflevector <2 x i32> %410, <2 x i32> poison, <2 x i32> zeroinitializer
  %412 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %405, <2 x i32> %411)
  %413 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %412, <2 x i32> zeroinitializer)
  %414 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %415 = add <2 x i32> %413, %414
  %416 = insertelement <2 x i32> poison, i32 %69, i64 0
  %417 = shufflevector <2 x i32> %416, <2 x i32> poison, <2 x i32> zeroinitializer
  %418 = mul <2 x i32> %415, %417
  %419 = sext <2 x i32> %418 to <2 x i64>
  %420 = extractelement <2 x i64> %419, i64 1
  %421 = getelementptr float, float* %67, i64 %420
  %422 = load float, float* %421, align 4
  %423 = extractelement <2 x i64> %419, i64 0
  %424 = getelementptr float, float* %67, i64 %423
  %425 = load float, float* %424, align 4
  %426 = add <2 x i32> %418, <i32 1, i32 1>
  %427 = sext <2 x i32> %426 to <2 x i64>
  %428 = getelementptr float, <2 x float*> %92, <2 x i64> %427
  %429 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %428, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %430 = add <2 x i32> %418, <i32 2, i32 2>
  %431 = sext <2 x i32> %430 to <2 x i64>
  %432 = getelementptr float, <2 x float*> %92, <2 x i64> %431
  %433 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %432, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %434 = fadd reassoc ninf nsz float %425, %422
  %435 = load float*, float** %32, align 8
  %436 = load i32, i32* %34, align 4
  %437 = mul i32 %436, 6
  %438 = sext i32 %437 to i64
  %439 = getelementptr float, float* %435, i64 %438
  %440 = load float, float* %439, align 4
  %441 = fmul reassoc ninf nsz float %440, %434
  %442 = fadd reassoc ninf nsz float %441, %.4117
  %443 = add i32 %437, 2
  %444 = sext i32 %443 to i64
  %445 = getelementptr float, float* %435, i64 %444
  %446 = load float, float* %445, align 4
  %447 = fmul reassoc ninf nsz float %446, %434
  %448 = fadd reassoc ninf nsz float %447, %.484
  %449 = fsub reassoc ninf nsz float %425, %422
  %450 = getelementptr float, float* %439, i64 1
  %451 = load float, float* %450, align 4
  %452 = fmul reassoc ninf nsz float %451, %449
  %453 = fadd reassoc ninf nsz float %452, %.4106
  %454 = extractelement <2 x float> %429, i64 0
  %455 = extractelement <2 x float> %429, i64 1
  %456 = fadd reassoc ninf nsz float %454, %455
  %457 = fmul reassoc ninf nsz float %440, %456
  %458 = fadd reassoc ninf nsz float %457, %.495
  %459 = fsub reassoc ninf nsz float %454, %455
  %460 = fmul reassoc ninf nsz float %451, %459
  %461 = fadd reassoc ninf nsz float %460, %.4
  %shift128 = shufflevector <2 x float> %433, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %462 = fadd reassoc ninf nsz <2 x float> %433, %shift128
  %463 = extractelement <2 x float> %462, i64 0
  %464 = fmul reassoc ninf nsz float %440, %463
  %465 = fadd reassoc ninf nsz float %464, %.473
  br label %after_if15

after_if15:                                       ; preds = %true_block13, %after_if12
  %.5118 = phi float [ %442, %true_block13 ], [ %.4117, %after_if12 ]
  %.5107 = phi float [ %453, %true_block13 ], [ %.4106, %after_if12 ]
  %.596 = phi float [ %458, %true_block13 ], [ %.495, %after_if12 ]
  %.585 = phi float [ %448, %true_block13 ], [ %.484, %after_if12 ]
  %.574 = phi float [ %465, %true_block13 ], [ %.473, %after_if12 ]
  %.5 = phi float [ %461, %true_block13 ], [ %.4, %after_if12 ]
  br i1 %41, label %true_block16, label %after_if18

true_block16:                                     ; preds = %after_if15
  %466 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %467 = add <2 x i32> %466, <i32 7, i32 -7>
  %468 = getelementptr inbounds i8, i8* %55, i64 8
  %469 = bitcast i8* %468 to i32*
  %470 = load i32, i32* %469, align 4
  %471 = add i32 %470, -1
  %472 = insertelement <2 x i32> poison, i32 %471, i64 0
  %473 = shufflevector <2 x i32> %472, <2 x i32> poison, <2 x i32> zeroinitializer
  %474 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %467, <2 x i32> %473)
  %475 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %474, <2 x i32> zeroinitializer)
  %476 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %477 = add <2 x i32> %475, %476
  %478 = insertelement <2 x i32> poison, i32 %69, i64 0
  %479 = shufflevector <2 x i32> %478, <2 x i32> poison, <2 x i32> zeroinitializer
  %480 = mul <2 x i32> %477, %479
  %481 = sext <2 x i32> %480 to <2 x i64>
  %482 = extractelement <2 x i64> %481, i64 1
  %483 = getelementptr float, float* %67, i64 %482
  %484 = load float, float* %483, align 4
  %485 = extractelement <2 x i64> %481, i64 0
  %486 = getelementptr float, float* %67, i64 %485
  %487 = load float, float* %486, align 4
  %488 = add <2 x i32> %480, <i32 1, i32 1>
  %489 = sext <2 x i32> %488 to <2 x i64>
  %490 = getelementptr float, <2 x float*> %92, <2 x i64> %489
  %491 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %490, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %492 = add <2 x i32> %480, <i32 2, i32 2>
  %493 = sext <2 x i32> %492 to <2 x i64>
  %494 = getelementptr float, <2 x float*> %92, <2 x i64> %493
  %495 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %494, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %496 = fadd reassoc ninf nsz float %487, %484
  %497 = load float*, float** %32, align 8
  %498 = load i32, i32* %34, align 4
  %499 = mul i32 %498, 7
  %500 = sext i32 %499 to i64
  %501 = getelementptr float, float* %497, i64 %500
  %502 = load float, float* %501, align 4
  %503 = fmul reassoc ninf nsz float %502, %496
  %504 = fadd reassoc ninf nsz float %503, %.5118
  %505 = add i32 %499, 2
  %506 = sext i32 %505 to i64
  %507 = getelementptr float, float* %497, i64 %506
  %508 = load float, float* %507, align 4
  %509 = fmul reassoc ninf nsz float %508, %496
  %510 = fadd reassoc ninf nsz float %509, %.585
  %511 = fsub reassoc ninf nsz float %487, %484
  %512 = add i32 %499, 1
  %513 = sext i32 %512 to i64
  %514 = getelementptr float, float* %497, i64 %513
  %515 = load float, float* %514, align 4
  %516 = fmul reassoc ninf nsz float %515, %511
  %517 = fadd reassoc ninf nsz float %516, %.5107
  %518 = extractelement <2 x float> %491, i64 0
  %519 = extractelement <2 x float> %491, i64 1
  %520 = fadd reassoc ninf nsz float %518, %519
  %521 = fmul reassoc ninf nsz float %502, %520
  %522 = fadd reassoc ninf nsz float %521, %.596
  %523 = fsub reassoc ninf nsz float %518, %519
  %524 = fmul reassoc ninf nsz float %515, %523
  %525 = fadd reassoc ninf nsz float %524, %.5
  %shift129 = shufflevector <2 x float> %495, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %526 = fadd reassoc ninf nsz <2 x float> %495, %shift129
  %527 = extractelement <2 x float> %526, i64 0
  %528 = fmul reassoc ninf nsz float %502, %527
  %529 = fadd reassoc ninf nsz float %528, %.574
  br label %after_if18

after_if18:                                       ; preds = %true_block16, %after_if15
  %.6119 = phi float [ %504, %true_block16 ], [ %.5118, %after_if15 ]
  %.6108 = phi float [ %517, %true_block16 ], [ %.5107, %after_if15 ]
  %.697 = phi float [ %522, %true_block16 ], [ %.596, %after_if15 ]
  %.686 = phi float [ %510, %true_block16 ], [ %.585, %after_if15 ]
  %.675 = phi float [ %529, %true_block16 ], [ %.574, %after_if15 ]
  %.6 = phi float [ %525, %true_block16 ], [ %.5, %after_if15 ]
  br i1 %42, label %true_block19, label %after_if21

true_block19:                                     ; preds = %after_if18
  %530 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %531 = add <2 x i32> %530, <i32 8, i32 -8>
  %532 = getelementptr inbounds i8, i8* %55, i64 8
  %533 = bitcast i8* %532 to i32*
  %534 = load i32, i32* %533, align 4
  %535 = add i32 %534, -1
  %536 = insertelement <2 x i32> poison, i32 %535, i64 0
  %537 = shufflevector <2 x i32> %536, <2 x i32> poison, <2 x i32> zeroinitializer
  %538 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %531, <2 x i32> %537)
  %539 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %538, <2 x i32> zeroinitializer)
  %540 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %541 = add <2 x i32> %539, %540
  %542 = insertelement <2 x i32> poison, i32 %69, i64 0
  %543 = shufflevector <2 x i32> %542, <2 x i32> poison, <2 x i32> zeroinitializer
  %544 = mul <2 x i32> %541, %543
  %545 = sext <2 x i32> %544 to <2 x i64>
  %546 = extractelement <2 x i64> %545, i64 1
  %547 = getelementptr float, float* %67, i64 %546
  %548 = load float, float* %547, align 4
  %549 = extractelement <2 x i64> %545, i64 0
  %550 = getelementptr float, float* %67, i64 %549
  %551 = load float, float* %550, align 4
  %552 = add <2 x i32> %544, <i32 1, i32 1>
  %553 = sext <2 x i32> %552 to <2 x i64>
  %554 = getelementptr float, <2 x float*> %92, <2 x i64> %553
  %555 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %554, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %556 = add <2 x i32> %544, <i32 2, i32 2>
  %557 = sext <2 x i32> %556 to <2 x i64>
  %558 = getelementptr float, <2 x float*> %92, <2 x i64> %557
  %559 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %558, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %560 = fadd reassoc ninf nsz float %551, %548
  %561 = load float*, float** %32, align 8
  %562 = load i32, i32* %34, align 4
  %563 = shl i32 %562, 3
  %564 = sext i32 %563 to i64
  %565 = getelementptr float, float* %561, i64 %564
  %566 = load float, float* %565, align 4
  %567 = fmul reassoc ninf nsz float %566, %560
  %568 = fadd reassoc ninf nsz float %567, %.6119
  %569 = getelementptr float, float* %565, i64 2
  %570 = load float, float* %569, align 4
  %571 = fmul reassoc ninf nsz float %570, %560
  %572 = fadd reassoc ninf nsz float %571, %.686
  %573 = fsub reassoc ninf nsz float %551, %548
  %574 = getelementptr float, float* %565, i64 1
  %575 = load float, float* %574, align 4
  %576 = fmul reassoc ninf nsz float %575, %573
  %577 = fadd reassoc ninf nsz float %576, %.6108
  %578 = extractelement <2 x float> %555, i64 0
  %579 = extractelement <2 x float> %555, i64 1
  %580 = fadd reassoc ninf nsz float %578, %579
  %581 = fmul reassoc ninf nsz float %566, %580
  %582 = fadd reassoc ninf nsz float %581, %.697
  %583 = fsub reassoc ninf nsz float %578, %579
  %584 = fmul reassoc ninf nsz float %575, %583
  %585 = fadd reassoc ninf nsz float %584, %.6
  %shift130 = shufflevector <2 x float> %559, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %586 = fadd reassoc ninf nsz <2 x float> %559, %shift130
  %587 = extractelement <2 x float> %586, i64 0
  %588 = fmul reassoc ninf nsz float %566, %587
  %589 = fadd reassoc ninf nsz float %588, %.675
  br label %after_if21

after_if21:                                       ; preds = %true_block19, %after_if18
  %.7120 = phi float [ %568, %true_block19 ], [ %.6119, %after_if18 ]
  %.7109 = phi float [ %577, %true_block19 ], [ %.6108, %after_if18 ]
  %.798 = phi float [ %582, %true_block19 ], [ %.697, %after_if18 ]
  %.787 = phi float [ %572, %true_block19 ], [ %.686, %after_if18 ]
  %.776 = phi float [ %589, %true_block19 ], [ %.675, %after_if18 ]
  %.7 = phi float [ %585, %true_block19 ], [ %.6, %after_if18 ]
  br i1 %43, label %true_block22, label %after_if24

true_block22:                                     ; preds = %after_if21
  %590 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %591 = add <2 x i32> %590, <i32 9, i32 -9>
  %592 = getelementptr inbounds i8, i8* %55, i64 8
  %593 = bitcast i8* %592 to i32*
  %594 = load i32, i32* %593, align 4
  %595 = add i32 %594, -1
  %596 = insertelement <2 x i32> poison, i32 %595, i64 0
  %597 = shufflevector <2 x i32> %596, <2 x i32> poison, <2 x i32> zeroinitializer
  %598 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %591, <2 x i32> %597)
  %599 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %598, <2 x i32> zeroinitializer)
  %600 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %601 = add <2 x i32> %599, %600
  %602 = insertelement <2 x i32> poison, i32 %69, i64 0
  %603 = shufflevector <2 x i32> %602, <2 x i32> poison, <2 x i32> zeroinitializer
  %604 = mul <2 x i32> %601, %603
  %605 = sext <2 x i32> %604 to <2 x i64>
  %606 = extractelement <2 x i64> %605, i64 1
  %607 = getelementptr float, float* %67, i64 %606
  %608 = load float, float* %607, align 4
  %609 = extractelement <2 x i64> %605, i64 0
  %610 = getelementptr float, float* %67, i64 %609
  %611 = load float, float* %610, align 4
  %612 = add <2 x i32> %604, <i32 1, i32 1>
  %613 = sext <2 x i32> %612 to <2 x i64>
  %614 = getelementptr float, <2 x float*> %92, <2 x i64> %613
  %615 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %614, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %616 = add <2 x i32> %604, <i32 2, i32 2>
  %617 = sext <2 x i32> %616 to <2 x i64>
  %618 = getelementptr float, <2 x float*> %92, <2 x i64> %617
  %619 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %618, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %620 = fadd reassoc ninf nsz float %611, %608
  %621 = load float*, float** %32, align 8
  %622 = load i32, i32* %34, align 4
  %623 = mul i32 %622, 9
  %624 = sext i32 %623 to i64
  %625 = getelementptr float, float* %621, i64 %624
  %626 = load float, float* %625, align 4
  %627 = fmul reassoc ninf nsz float %626, %620
  %628 = fadd reassoc ninf nsz float %627, %.7120
  %629 = add i32 %623, 2
  %630 = sext i32 %629 to i64
  %631 = getelementptr float, float* %621, i64 %630
  %632 = load float, float* %631, align 4
  %633 = fmul reassoc ninf nsz float %632, %620
  %634 = fadd reassoc ninf nsz float %633, %.787
  %635 = fsub reassoc ninf nsz float %611, %608
  %636 = add i32 %623, 1
  %637 = sext i32 %636 to i64
  %638 = getelementptr float, float* %621, i64 %637
  %639 = load float, float* %638, align 4
  %640 = fmul reassoc ninf nsz float %639, %635
  %641 = fadd reassoc ninf nsz float %640, %.7109
  %642 = extractelement <2 x float> %615, i64 0
  %643 = extractelement <2 x float> %615, i64 1
  %644 = fadd reassoc ninf nsz float %642, %643
  %645 = fmul reassoc ninf nsz float %626, %644
  %646 = fadd reassoc ninf nsz float %645, %.798
  %647 = fsub reassoc ninf nsz float %642, %643
  %648 = fmul reassoc ninf nsz float %639, %647
  %649 = fadd reassoc ninf nsz float %648, %.7
  %shift131 = shufflevector <2 x float> %619, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %650 = fadd reassoc ninf nsz <2 x float> %619, %shift131
  %651 = extractelement <2 x float> %650, i64 0
  %652 = fmul reassoc ninf nsz float %626, %651
  %653 = fadd reassoc ninf nsz float %652, %.776
  br label %after_if24

after_if24:                                       ; preds = %true_block22, %after_if21
  %.8121 = phi float [ %628, %true_block22 ], [ %.7120, %after_if21 ]
  %.8110 = phi float [ %641, %true_block22 ], [ %.7109, %after_if21 ]
  %.899 = phi float [ %646, %true_block22 ], [ %.798, %after_if21 ]
  %.888 = phi float [ %634, %true_block22 ], [ %.787, %after_if21 ]
  %.877 = phi float [ %653, %true_block22 ], [ %.776, %after_if21 ]
  %.8 = phi float [ %649, %true_block22 ], [ %.7, %after_if21 ]
  br i1 %44, label %true_block25, label %after_if27

true_block25:                                     ; preds = %after_if24
  %654 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %655 = add <2 x i32> %654, <i32 10, i32 -10>
  %656 = getelementptr inbounds i8, i8* %55, i64 8
  %657 = bitcast i8* %656 to i32*
  %658 = load i32, i32* %657, align 4
  %659 = add i32 %658, -1
  %660 = insertelement <2 x i32> poison, i32 %659, i64 0
  %661 = shufflevector <2 x i32> %660, <2 x i32> poison, <2 x i32> zeroinitializer
  %662 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %655, <2 x i32> %661)
  %663 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %662, <2 x i32> zeroinitializer)
  %664 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %665 = add <2 x i32> %663, %664
  %666 = insertelement <2 x i32> poison, i32 %69, i64 0
  %667 = shufflevector <2 x i32> %666, <2 x i32> poison, <2 x i32> zeroinitializer
  %668 = mul <2 x i32> %665, %667
  %669 = sext <2 x i32> %668 to <2 x i64>
  %670 = extractelement <2 x i64> %669, i64 1
  %671 = getelementptr float, float* %67, i64 %670
  %672 = load float, float* %671, align 4
  %673 = extractelement <2 x i64> %669, i64 0
  %674 = getelementptr float, float* %67, i64 %673
  %675 = load float, float* %674, align 4
  %676 = add <2 x i32> %668, <i32 1, i32 1>
  %677 = sext <2 x i32> %676 to <2 x i64>
  %678 = getelementptr float, <2 x float*> %92, <2 x i64> %677
  %679 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %678, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %680 = add <2 x i32> %668, <i32 2, i32 2>
  %681 = sext <2 x i32> %680 to <2 x i64>
  %682 = getelementptr float, <2 x float*> %92, <2 x i64> %681
  %683 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %682, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %684 = fadd reassoc ninf nsz float %675, %672
  %685 = load float*, float** %32, align 8
  %686 = load i32, i32* %34, align 4
  %687 = mul i32 %686, 10
  %688 = sext i32 %687 to i64
  %689 = getelementptr float, float* %685, i64 %688
  %690 = load float, float* %689, align 4
  %691 = fmul reassoc ninf nsz float %690, %684
  %692 = fadd reassoc ninf nsz float %691, %.8121
  %693 = add i32 %687, 2
  %694 = sext i32 %693 to i64
  %695 = getelementptr float, float* %685, i64 %694
  %696 = load float, float* %695, align 4
  %697 = fmul reassoc ninf nsz float %696, %684
  %698 = fadd reassoc ninf nsz float %697, %.888
  %699 = fsub reassoc ninf nsz float %675, %672
  %700 = getelementptr float, float* %689, i64 1
  %701 = load float, float* %700, align 4
  %702 = fmul reassoc ninf nsz float %701, %699
  %703 = fadd reassoc ninf nsz float %702, %.8110
  %704 = extractelement <2 x float> %679, i64 0
  %705 = extractelement <2 x float> %679, i64 1
  %706 = fadd reassoc ninf nsz float %704, %705
  %707 = fmul reassoc ninf nsz float %690, %706
  %708 = fadd reassoc ninf nsz float %707, %.899
  %709 = fsub reassoc ninf nsz float %704, %705
  %710 = fmul reassoc ninf nsz float %701, %709
  %711 = fadd reassoc ninf nsz float %710, %.8
  %shift132 = shufflevector <2 x float> %683, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %712 = fadd reassoc ninf nsz <2 x float> %683, %shift132
  %713 = extractelement <2 x float> %712, i64 0
  %714 = fmul reassoc ninf nsz float %690, %713
  %715 = fadd reassoc ninf nsz float %714, %.877
  br label %after_if27

after_if27:                                       ; preds = %true_block25, %after_if24
  %.9122 = phi float [ %692, %true_block25 ], [ %.8121, %after_if24 ]
  %.9111 = phi float [ %703, %true_block25 ], [ %.8110, %after_if24 ]
  %.9100 = phi float [ %708, %true_block25 ], [ %.899, %after_if24 ]
  %.989 = phi float [ %698, %true_block25 ], [ %.888, %after_if24 ]
  %.978 = phi float [ %715, %true_block25 ], [ %.877, %after_if24 ]
  %.9 = phi float [ %711, %true_block25 ], [ %.8, %after_if24 ]
  br i1 %45, label %true_block28, label %after_if30

true_block28:                                     ; preds = %after_if27
  %716 = shufflevector <2 x i32> %76, <2 x i32> poison, <2 x i32> zeroinitializer
  %717 = add <2 x i32> %716, <i32 11, i32 -11>
  %718 = getelementptr inbounds i8, i8* %55, i64 8
  %719 = bitcast i8* %718 to i32*
  %720 = load i32, i32* %719, align 4
  %721 = add i32 %720, -1
  %722 = insertelement <2 x i32> poison, i32 %721, i64 0
  %723 = shufflevector <2 x i32> %722, <2 x i32> poison, <2 x i32> zeroinitializer
  %724 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %717, <2 x i32> %723)
  %725 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %724, <2 x i32> zeroinitializer)
  %726 = shufflevector <2 x i32> %77, <2 x i32> poison, <2 x i32> <i32 1, i32 1>
  %727 = add <2 x i32> %725, %726
  %728 = insertelement <2 x i32> poison, i32 %69, i64 0
  %729 = shufflevector <2 x i32> %728, <2 x i32> poison, <2 x i32> zeroinitializer
  %730 = mul <2 x i32> %727, %729
  %731 = sext <2 x i32> %730 to <2 x i64>
  %732 = extractelement <2 x i64> %731, i64 1
  %733 = getelementptr float, float* %67, i64 %732
  %734 = load float, float* %733, align 4
  %735 = extractelement <2 x i64> %731, i64 0
  %736 = getelementptr float, float* %67, i64 %735
  %737 = load float, float* %736, align 4
  %738 = add <2 x i32> %730, <i32 1, i32 1>
  %739 = sext <2 x i32> %738 to <2 x i64>
  %740 = getelementptr float, <2 x float*> %92, <2 x i64> %739
  %741 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %740, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %742 = add <2 x i32> %730, <i32 2, i32 2>
  %743 = sext <2 x i32> %742 to <2 x i64>
  %744 = getelementptr float, <2 x float*> %92, <2 x i64> %743
  %745 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %744, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %746 = fadd reassoc ninf nsz float %737, %734
  %747 = load float*, float** %32, align 8
  %748 = load i32, i32* %34, align 4
  %749 = mul i32 %748, 11
  %750 = sext i32 %749 to i64
  %751 = getelementptr float, float* %747, i64 %750
  %752 = load float, float* %751, align 4
  %753 = fmul reassoc ninf nsz float %752, %746
  %754 = fadd reassoc ninf nsz float %753, %.9122
  %755 = add i32 %749, 2
  %756 = sext i32 %755 to i64
  %757 = getelementptr float, float* %747, i64 %756
  %758 = load float, float* %757, align 4
  %759 = fmul reassoc ninf nsz float %758, %746
  %760 = fadd reassoc ninf nsz float %759, %.989
  %761 = fsub reassoc ninf nsz float %737, %734
  %762 = add i32 %749, 1
  %763 = sext i32 %762 to i64
  %764 = getelementptr float, float* %747, i64 %763
  %765 = load float, float* %764, align 4
  %766 = fmul reassoc ninf nsz float %765, %761
  %767 = fadd reassoc ninf nsz float %766, %.9111
  %768 = extractelement <2 x float> %741, i64 0
  %769 = extractelement <2 x float> %741, i64 1
  %770 = fadd reassoc ninf nsz float %768, %769
  %771 = fmul reassoc ninf nsz float %752, %770
  %772 = fadd reassoc ninf nsz float %771, %.9100
  %773 = fsub reassoc ninf nsz float %768, %769
  %774 = fmul reassoc ninf nsz float %765, %773
  %775 = fadd reassoc ninf nsz float %774, %.9
  %shift133 = shufflevector <2 x float> %745, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %776 = fadd reassoc ninf nsz <2 x float> %745, %shift133
  %777 = extractelement <2 x float> %776, i64 0
  %778 = fmul reassoc ninf nsz float %752, %777
  %779 = fadd reassoc ninf nsz float %778, %.978
  br label %after_if30

after_if30:                                       ; preds = %true_block28, %after_if27
  %.10123 = phi float [ %754, %true_block28 ], [ %.9122, %after_if27 ]
  %.10112 = phi float [ %767, %true_block28 ], [ %.9111, %after_if27 ]
  %.10101 = phi float [ %772, %true_block28 ], [ %.9100, %after_if27 ]
  %.1090 = phi float [ %760, %true_block28 ], [ %.989, %after_if27 ]
  %.1079 = phi float [ %779, %true_block28 ], [ %.978, %after_if27 ]
  %.10 = phi float [ %775, %true_block28 ], [ %.9, %after_if27 ]
  %780 = fmul reassoc ninf nsz float %.10101, %25
  %781 = load float*, float** %50, align 8
  %782 = load i32, i32* %51, align 4
  %783 = load i32, i32* %52, align 4
  %784 = mul i32 %782, %70
  %785 = add i32 %784, %78
  %786 = mul i32 %785, %783
  %787 = sext i32 %786 to i64
  %788 = getelementptr float, float* %781, i64 %787
  store float %780, float* %788, align 4
  %789 = fmul reassoc ninf nsz float %.10112, %25
  %790 = load float*, float** %50, align 8
  %791 = load i32, i32* %51, align 4
  %792 = load i32, i32* %52, align 4
  %793 = mul i32 %791, %70
  %794 = add i32 %793, %78
  %795 = mul i32 %794, %792
  %796 = add i32 %795, 1
  %797 = sext i32 %796 to i64
  %798 = getelementptr float, float* %790, i64 %797
  store float %789, float* %798, align 4
  %799 = fmul reassoc ninf nsz float %.10123, %27
  %800 = fmul reassoc ninf nsz float %.1079, %29
  %801 = fadd reassoc ninf nsz float %800, %799
  %802 = load float*, float** %50, align 8
  %803 = load i32, i32* %51, align 4
  %804 = load i32, i32* %52, align 4
  %805 = mul i32 %803, %70
  %806 = add i32 %805, %78
  %807 = mul i32 %806, %804
  %808 = add i32 %807, 2
  %809 = sext i32 %808 to i64
  %810 = getelementptr float, float* %802, i64 %809
  store float %801, float* %810, align 4
  %811 = fmul reassoc ninf nsz float %.1090, %29
  %812 = fadd reassoc ninf nsz float %811, %799
  %813 = load float*, float** %50, align 8
  %814 = load i32, i32* %51, align 4
  %815 = load i32, i32* %52, align 4
  %816 = mul i32 %814, %70
  %817 = add i32 %816, %78
  %818 = mul i32 %817, %815
  %819 = add i32 %818, 3
  %820 = sext i32 %819 to i64
  %821 = getelementptr float, float* %813, i64 %820
  store float %812, float* %821, align 4
  %822 = fmul reassoc ninf nsz float %.10, %31
  %823 = load float*, float** %50, align 8
  %824 = load i32, i32* %51, align 4
  %825 = load i32, i32* %52, align 4
  %826 = mul i32 %824, %70
  %827 = add i32 %826, %78
  %828 = mul i32 %827, %825
  %829 = add i32 %828, 4
  %830 = sext i32 %829 to i64
  %831 = getelementptr float, float* %823, i64 %830
  store float %822, float* %831, align 4
  %832 = add nsw i32 %.0124126, 1
  %exitcond.not = icmp eq i32 %19, %832
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext**
  %.sroa.0.0.copyload = load %struct.RuntimeContext*, %struct.RuntimeContext** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

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
