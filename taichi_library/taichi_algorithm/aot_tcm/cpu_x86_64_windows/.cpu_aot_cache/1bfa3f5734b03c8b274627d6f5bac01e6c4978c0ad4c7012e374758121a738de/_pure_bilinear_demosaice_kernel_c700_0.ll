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
define void @_pure_bilinear_demosaice_kernel_c700_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 2
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 16
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fsub reassoc ninf nsz float %3, %5
  %13 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %12, float 1.000000e+00)
  %14 = fdiv reassoc ninf nsz float 1.000000e+00, %13
  %15 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 20
  %19 = bitcast i8* %18 to float*
  store float %14, float* %19, align 4
  %20 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %21 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %20, i64 0, i32 4
  %22 = load i32, i32* %21, align 4
  %23 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %24 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %23, i64 0, i32 14
  %25 = load i8*, i8** %24, align 8
  %26 = getelementptr inbounds i8, i8* %25, i64 8
  %27 = bitcast i8* %26 to i32*
  store i32 %22, i32* %27, align 4
  %28 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %29 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %29, i64 0, i32 5
  %31 = load i32, i32* %30, align 4
  %32 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 12
  %36 = bitcast i8* %35 to i32*
  store i32 %31, i32* %36, align 4
  %37 = tail call i32 @llvm.smax.i32(i32 %31, i32 0)
  %38 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  store i32 %37, i32* %42, align 4
  %43 = mul i32 %37, %28
  %44 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %45 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %44, i64 0, i32 14
  %46 = bitcast i8** %45 to i32**
  %47 = load i32*, i32** %46, align 8
  store i32 %43, i32* %47, align 4
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_pure_bilinear_demosaice_kernel_c700_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #2 {
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
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #3 {
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.lr.ph
  %.02032 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %192, %after_if9 ]
  %28 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %28, i64 0, i32 14
  %30 = load i8*, i8** %29, align 8
  %31 = getelementptr inbounds i8, i8* %30, i64 4
  %32 = bitcast i8* %31 to i32*
  %33 = load i32, i32* %32, align 4
  %34 = sdiv i32 %.02032, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.02032
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.02032, 0
  %39 = icmp ne i32 %.02032, %35
  %40 = and i1 %38, %37
  %41 = and i1 %40, %39
  %.neg21 = sext i1 %41 to i32
  %42 = add i32 %34, %.neg21
  %43 = mul i32 %42, %33
  %44 = mul i32 %33, -1
  %45 = mul i32 %44, %42
  %46 = add i32 %.02032, %45
  %47 = insertelement <2 x i32> poison, i32 %46, i64 0
  %48 = insertelement <2 x i32> %47, i32 %42, i64 1
  %49 = sdiv <2 x i32> %48, <i32 2, i32 2>
  %50 = icmp slt <2 x i32> %48, zeroinitializer
  %51 = shl nsw <2 x i32> %49, <i32 1, i32 1>
  %52 = icmp ne <2 x i32> %51, %48
  %53 = and <2 x i1> %50, %52
  %54 = zext <2 x i1> %53 to <2 x i32>
  %55 = sub nsw <2 x i32> %54, %49
  %56 = shl <2 x i32> %55, <i32 1, i32 1>
  %57 = sub <2 x i32> zeroinitializer, %48
  %58 = icmp eq <2 x i32> %56, %57
  %59 = load { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %60 = extractelement <2 x i1> %58, i64 1
  br i1 %60, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %61 = extractelement <2 x i1> %58, i64 0
  br i1 %61, label %true_block1, label %false_block2

false_block:                                      ; preds = %for_loop_body
  %62 = extractelement <2 x i1> %58, i64 0
  br i1 %62, label %true_block4, label %false_block5

after_if:                                         ; preds = %false_block5, %true_block4, %false_block2, %true_block1
  %.019.in = phi i32* [ %139, %true_block1 ], [ %140, %false_block2 ], [ %141, %true_block4 ], [ %142, %false_block5 ]
  %.019 = load i32, i32* %.019.in, align 4
  %63 = add i32 %42, -1
  %64 = getelementptr inbounds i8, i8* %30, i64 8
  %65 = bitcast i8* %64 to i32*
  %66 = load i32, i32* %65, align 4
  %67 = add i32 %66, -1
  %68 = add i32 %42, 1
  %69 = add i32 %46, -1
  %70 = getelementptr inbounds i8, i8* %30, i64 12
  %71 = bitcast i8* %70 to i32*
  %72 = load i32, i32* %71, align 4
  %73 = add i32 %72, -1
  %74 = add i32 %46, 1
  %75 = load float*, float** %23, align 8
  %76 = load i32, i32* %24, align 4
  %77 = mul i32 %76, %42
  %78 = sub i32 %76, %33
  %79 = mul i32 %78, %42
  %80 = add i32 %.02032, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %75, i64 %81
  %83 = load float, float* %82, align 4
  %84 = getelementptr inbounds i8, i8* %30, i64 16
  %85 = bitcast i8* %84 to float*
  %86 = load float, float* %85, align 4
  %87 = fsub reassoc ninf nsz float %83, %86
  %88 = getelementptr inbounds i8, i8* %30, i64 20
  %89 = bitcast i8* %88 to float*
  %90 = load float, float* %89, align 4
  %91 = fmul reassoc ninf nsz float %87, %90
  %92 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %91, float 0.000000e+00)
  %93 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %92, float 1.000000e+00)
  %94 = tail call i32 @llvm.smax.i32(i32 %63, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %67, i32 %68)
  %96 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %97 = tail call i32 @llvm.smin.i32(i32 %73, i32 %74)
  %98 = insertelement <2 x i32> poison, i32 %76, i64 0
  %99 = shufflevector <2 x i32> %98, <2 x i32> poison, <2 x i32> zeroinitializer
  %100 = insertelement <2 x i32> poison, i32 %94, i64 0
  %101 = insertelement <2 x i32> %100, i32 %95, i64 1
  %102 = mul <2 x i32> %99, %101
  %103 = extractelement <2 x i32> %102, i64 0
  %104 = sub i32 %103, %43
  %105 = add i32 %.02032, %104
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, float* %75, i64 %106
  %108 = load float, float* %107, align 4
  %109 = fsub reassoc ninf nsz float %108, %86
  %110 = fmul reassoc ninf nsz float %109, %90
  %111 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %110, float 0.000000e+00)
  %112 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %111, float 1.000000e+00)
  %113 = extractelement <2 x i32> %102, i64 1
  %114 = sub i32 %113, %43
  %115 = add i32 %.02032, %114
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %75, i64 %116
  %118 = load float, float* %117, align 4
  %119 = fsub reassoc ninf nsz float %118, %86
  %120 = fmul reassoc ninf nsz float %119, %90
  %121 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %120, float 0.000000e+00)
  %122 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %121, float 1.000000e+00)
  %123 = add i32 %77, %96
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %75, i64 %124
  %126 = load float, float* %125, align 4
  %127 = fsub reassoc ninf nsz float %126, %86
  %128 = fmul reassoc ninf nsz float %127, %90
  %129 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %128, float 0.000000e+00)
  %130 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %129, float 1.000000e+00)
  %131 = add i32 %77, %97
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %75, i64 %132
  %134 = load float, float* %133, align 4
  %135 = fsub reassoc ninf nsz float %134, %86
  %136 = fmul reassoc ninf nsz float %135, %90
  %137 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %136, float 0.000000e+00)
  %138 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %137, float 1.000000e+00)
  switch i32 %.019, label %false_block11 [
    i32 0, label %true_block7
    i32 2, label %true_block10
  ]

true_block1:                                      ; preds = %true_block
  %139 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 6
  br label %after_if

false_block2:                                     ; preds = %true_block
  %140 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 7
  br label %after_if

true_block4:                                      ; preds = %false_block
  %141 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 8
  br label %after_if

false_block5:                                     ; preds = %false_block
  %142 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 9
  br label %after_if

true_block7:                                      ; preds = %after_if
  %143 = shufflevector <2 x i32> %102, <2 x i32> undef, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %144 = insertelement <4 x i32> poison, i32 %96, i64 0
  %145 = insertelement <4 x i32> %144, i32 %97, i64 1
  %shuffle42 = shufflevector <4 x i32> %145, <4 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %146 = add <4 x i32> %143, %shuffle42
  %147 = sext <4 x i32> %146 to <4 x i64>
  %148 = insertelement <4 x float*> poison, float* %75, i64 0
  %shuffle41 = shufflevector <4 x float*> %148, <4 x float*> poison, <4 x i32> zeroinitializer
  %149 = getelementptr float, <4 x float*> %shuffle41, <4 x i64> %147
  %150 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %149, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %151 = insertelement <4 x float> poison, float %86, i64 0
  %shuffle43 = shufflevector <4 x float> %151, <4 x float> poison, <4 x i32> zeroinitializer
  %152 = fsub reassoc ninf nsz <4 x float> %150, %shuffle43
  %153 = insertelement <4 x float> poison, float %90, i64 0
  %shuffle44 = shufflevector <4 x float> %153, <4 x float> poison, <4 x i32> zeroinitializer
  %154 = fmul reassoc ninf nsz <4 x float> %152, %shuffle44
  %155 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %154, <4 x float> zeroinitializer)
  %156 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %155, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %157 = fadd reassoc ninf nsz float %122, %112
  %158 = fadd reassoc ninf nsz float %157, %130
  %159 = fadd reassoc ninf nsz float %158, %138
  %160 = fmul reassoc ninf nsz float %159, 2.500000e-01
  %161 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %156)
  %162 = fmul reassoc ninf nsz float %161, 2.500000e-01
  br label %after_if9

after_if9:                                        ; preds = %after_if18, %true_block10, %true_block7
  %.017 = phi float [ %93, %true_block7 ], [ %211, %true_block10 ], [ %., %after_if18 ]
  %.016 = phi float [ %160, %true_block7 ], [ %209, %true_block10 ], [ %93, %after_if18 ]
  %.015 = phi float [ %162, %true_block7 ], [ %93, %true_block10 ], [ %.36, %after_if18 ]
  %163 = load float*, float** %25, align 8
  %164 = load i32, i32* %26, align 4
  %165 = load i32, i32* %27, align 4
  %166 = sub i32 %164, %33
  %167 = mul i32 %166, %42
  %168 = add i32 %.02032, %167
  %169 = mul i32 %168, %165
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, float* %163, i64 %170
  store float %.017, float* %171, align 4
  %172 = load float*, float** %25, align 8
  %173 = load i32, i32* %26, align 4
  %174 = load i32, i32* %27, align 4
  %175 = sub i32 %173, %33
  %176 = mul i32 %175, %42
  %177 = add i32 %.02032, %176
  %178 = mul i32 %177, %174
  %179 = add i32 %178, 1
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, float* %172, i64 %180
  store float %.016, float* %181, align 4
  %182 = load float*, float** %25, align 8
  %183 = load i32, i32* %26, align 4
  %184 = load i32, i32* %27, align 4
  %185 = sub i32 %183, %33
  %186 = mul i32 %185, %42
  %187 = add i32 %.02032, %186
  %188 = mul i32 %187, %184
  %189 = add i32 %188, 2
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %182, i64 %190
  store float %.015, float* %191, align 4
  %192 = add nsw i32 %.02032, 1
  %exitcond.not = icmp eq i32 %19, %192
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %after_if
  %shuffle37 = shufflevector <2 x i32> %102, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %193 = insertelement <4 x i32> poison, i32 %96, i64 0
  %194 = insertelement <4 x i32> %193, i32 %97, i64 1
  %shuffle38 = shufflevector <4 x i32> %194, <4 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %195 = add <4 x i32> %shuffle37, %shuffle38
  %196 = sext <4 x i32> %195 to <4 x i64>
  %197 = insertelement <4 x float*> poison, float* %75, i64 0
  %shuffle = shufflevector <4 x float*> %197, <4 x float*> poison, <4 x i32> zeroinitializer
  %198 = getelementptr float, <4 x float*> %shuffle, <4 x i64> %196
  %199 = call <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*> %198, i32 4, <4 x i1> <i1 true, i1 true, i1 true, i1 true>, <4 x float> undef)
  %200 = insertelement <4 x float> poison, float %86, i64 0
  %shuffle39 = shufflevector <4 x float> %200, <4 x float> poison, <4 x i32> zeroinitializer
  %201 = fsub reassoc ninf nsz <4 x float> %199, %shuffle39
  %202 = insertelement <4 x float> poison, float %90, i64 0
  %shuffle40 = shufflevector <4 x float> %202, <4 x float> poison, <4 x i32> zeroinitializer
  %203 = fmul reassoc ninf nsz <4 x float> %201, %shuffle40
  %204 = call reassoc ninf nsz <4 x float> @llvm.maxnum.v4f32(<4 x float> %203, <4 x float> zeroinitializer)
  %205 = call reassoc ninf nsz <4 x float> @llvm.minnum.v4f32(<4 x float> %204, <4 x float> <float 1.000000e+00, float 1.000000e+00, float 1.000000e+00, float 1.000000e+00>)
  %206 = fadd reassoc ninf nsz float %122, %112
  %207 = fadd reassoc ninf nsz float %206, %130
  %208 = fadd reassoc ninf nsz float %207, %138
  %209 = fmul reassoc ninf nsz float %208, 2.500000e-01
  %210 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v4f32(float -0.000000e+00, <4 x float> %205)
  %211 = fmul reassoc ninf nsz float %210, 2.500000e-01
  br label %after_if9

false_block11:                                    ; preds = %after_if
  br i1 %60, label %after_if15, label %after_if15.thread

after_if15:                                       ; preds = %false_block11
  %212 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 6
  %213 = and i32 %96, 2147483646
  %.not31 = icmp eq i32 %96, %213
  %214 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 7
  %spec.select = select i1 %.not31, i32* %212, i32* %214
  br label %after_if18

after_if15.thread:                                ; preds = %false_block11
  %215 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 8
  %216 = and i32 %96, 2147483646
  %.not3134 = icmp eq i32 %96, %216
  %217 = getelementptr { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float, float, i32, i32, i32, i32, i32, i32 }* %59, i64 0, i32 9
  %spec.select35 = select i1 %.not3134, i32* %215, i32* %217
  br label %after_if18

after_if18:                                       ; preds = %after_if15.thread, %after_if15
  %.013.in = phi i32* [ %spec.select, %after_if15 ], [ %spec.select35, %after_if15.thread ]
  %.013 = load i32, i32* %.013.in, align 4
  %218 = icmp eq i32 %.013, 0
  %219 = fadd reassoc ninf nsz float %138, %130
  %220 = fmul reassoc ninf nsz float %219, 5.000000e-01
  %221 = fadd reassoc ninf nsz float %122, %112
  %222 = fmul reassoc ninf nsz float %221, 5.000000e-01
  %. = select i1 %218, float %220, float %222
  %.36 = select i1 %218, float %222, float %220
  br label %after_if9
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.4.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #2
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
  call void %.sroa.7.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #2
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #1

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #1

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <4 x float> @llvm.masked.gather.v4f32.v4p0f32(<4 x float*>, i32 immarg, <4 x i1>, <4 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.maxnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x float> @llvm.minnum.v4f32(<4 x float>, <4 x float>) #8

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v4f32(float, <4 x float>) #9

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #9 = { nocallback nofree nosync nounwind readnone willreturn }

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
