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
define void @_gaussian_blur_y_3ch_f32_kernel_c184_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %10, i64 0, i32 3
  %12 = load i32, i32* %11, align 4
  %13 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %10, i64 0, i32 5
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %21 = tail call i32 @llvm.smax.i32(i32 %12, i32 0)
  %22 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  store i32 %21, i32* %26, align 4
  %27 = mul i32 %21, %20
  %28 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %28, i64 0, i32 14
  %30 = bitcast i8** %29 to i32**
  %31 = load i32*, i32** %30, align 8
  store i32 %27, i32* %31, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_y_3ch_f32_kernel_c184_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %23 = load float*, float** %22, align 8
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.0115231 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %761, %after_if45 ]
  %31 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.0115231, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.0115231
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.0115231, 0
  %42 = icmp ne i32 %.0115231, %38
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg116 = sext i1 %44 to i32
  %45 = load float, float* %23, align 4
  %46 = load float*, float** %25, align 8
  %47 = load i32, i32* %26, align 4
  %48 = load i32, i32* %27, align 4
  %49 = add i32 %37, %.neg116
  %50 = mul i32 %49, %36
  %51 = insertelement <2 x i32> poison, i32 %.0115231, i64 0
  %52 = insertelement <2 x i32> poison, i32 %50, i64 0
  %53 = sub <2 x i32> %51, %52
  %54 = extractelement <2 x i32> %53, i64 0
  %55 = mul i32 %47, %49
  %56 = add i32 %54, %55
  %57 = mul i32 %56, %48
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, float* %46, i64 %58
  %60 = load float, float* %59, align 4
  %61 = fmul reassoc ninf nsz float %60, %45
  %62 = add i32 %57, 1
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, float* %46, i64 %63
  %65 = load float, float* %64, align 4
  %66 = fmul reassoc ninf nsz float %65, %45
  %67 = add i32 %57, 2
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, float* %46, i64 %68
  %70 = load float, float* %69, align 4
  %71 = fmul reassoc ninf nsz float %70, %45
  %72 = getelementptr inbounds i8, i8* %33, i64 8
  %73 = bitcast i8* %72 to i32*
  %74 = load i32, i32* %73, align 4
  %75 = icmp sgt i32 %74, 0
  %76 = insertelement <4 x float> poison, float %61, i64 0
  %77 = insertelement <4 x float> %76, float %66, i64 1
  %78 = insertelement <4 x float> %77, float %71, i64 2
  %79 = insertelement <4 x float> %78, float %45, i64 3
  br i1 %75, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %80 = load float*, float** %22, align 8
  %81 = getelementptr float, float* %80, i64 1
  %82 = load float, float* %81, align 4
  %83 = insertelement <2 x i32> poison, i32 %49, i64 0
  %84 = shufflevector <2 x i32> %83, <2 x i32> poison, <2 x i32> zeroinitializer
  %85 = add <2 x i32> %84, <i32 1, i32 -1>
  %86 = getelementptr inbounds i8, i8* %33, i64 12
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
  %99 = insertelement <2 x i32> poison, i32 %47, i64 0
  %100 = shufflevector <2 x i32> %99, <2 x i32> poison, <2 x i32> zeroinitializer
  %101 = mul <2 x i32> %98, %100
  %102 = shufflevector <2 x i32> %53, <2 x i32> poison, <2 x i32> zeroinitializer
  %103 = add <2 x i32> %101, %102
  %104 = insertelement <2 x i32> poison, i32 %48, i64 0
  %105 = shufflevector <2 x i32> %104, <2 x i32> poison, <2 x i32> zeroinitializer
  %106 = mul <2 x i32> %103, %105
  %107 = sext <2 x i32> %106 to <2 x i64>
  %108 = extractelement <2 x i64> %107, i64 1
  %109 = getelementptr float, float* %46, i64 %108
  %110 = load float, float* %109, align 4
  %111 = extractelement <2 x i64> %107, i64 0
  %112 = getelementptr float, float* %46, i64 %111
  %113 = load float, float* %112, align 4
  %114 = fadd reassoc ninf nsz float %113, %110
  %115 = add <2 x i32> %106, <i32 1, i32 1>
  %116 = sext <2 x i32> %115 to <2 x i64>
  %117 = insertelement <2 x float*> poison, float* %46, i64 0
  %118 = shufflevector <2 x float*> %117, <2 x float*> poison, <2 x i32> zeroinitializer
  %119 = getelementptr float, <2 x float*> %118, <2 x i64> %116
  %120 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %119, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift = shufflevector <2 x float> %120, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %121 = fadd reassoc ninf nsz <2 x float> %120, %shift
  %122 = shufflevector <2 x float> %121, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %123 = add <2 x i32> %106, <i32 2, i32 2>
  %124 = sext <2 x i32> %123 to <2 x i64>
  %125 = getelementptr float, <2 x float*> %118, <2 x i64> %124
  %126 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %125, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift247 = shufflevector <2 x float> %126, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %127 = fadd reassoc ninf nsz <2 x float> %126, %shift247
  %128 = shufflevector <2 x float> %127, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %129 = insertelement <4 x float> poison, float %82, i64 0
  %shuffle245 = shufflevector <4 x float> %129, <4 x float> poison, <4 x i32> zeroinitializer
  %130 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %114, i64 0
  %131 = shufflevector <4 x float> %130, <4 x float> %122, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %132 = shufflevector <4 x float> %131, <4 x float> %128, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %133 = fmul reassoc ninf nsz <4 x float> %shuffle245, %132
  %134 = fadd reassoc ninf nsz <4 x float> %133, %79
  %.not = icmp eq i32 %74, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %135 = getelementptr float, float* %80, i64 2
  %136 = load float, float* %135, align 4
  %137 = add <2 x i32> %84, <i32 2, i32 -2>
  %138 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %137, i1 true)
  %139 = sub <2 x i32> %138, %92
  %140 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %139, <2 x i32> zeroinitializer)
  %141 = mul <2 x i32> %140, <i32 -2, i32 -2>
  %142 = add <2 x i32> %141, %138
  %143 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %142, <2 x i32> zeroinitializer)
  %144 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %143)
  %145 = mul <2 x i32> %144, %100
  %146 = add <2 x i32> %145, %102
  %147 = mul <2 x i32> %146, %105
  %148 = sext <2 x i32> %147 to <2 x i64>
  %149 = extractelement <2 x i64> %148, i64 1
  %150 = getelementptr float, float* %46, i64 %149
  %151 = load float, float* %150, align 4
  %152 = extractelement <2 x i64> %148, i64 0
  %153 = getelementptr float, float* %46, i64 %152
  %154 = load float, float* %153, align 4
  %155 = fadd reassoc ninf nsz float %154, %151
  %156 = add <2 x i32> %147, <i32 1, i32 1>
  %157 = sext <2 x i32> %156 to <2 x i64>
  %158 = getelementptr float, <2 x float*> %118, <2 x i64> %157
  %159 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %158, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift248 = shufflevector <2 x float> %159, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %160 = fadd reassoc ninf nsz <2 x float> %159, %shift248
  %161 = shufflevector <2 x float> %160, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %162 = add <2 x i32> %147, <i32 2, i32 2>
  %163 = sext <2 x i32> %162 to <2 x i64>
  %164 = getelementptr float, <2 x float*> %118, <2 x i64> %163
  %165 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %164, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift249 = shufflevector <2 x float> %165, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %166 = fadd reassoc ninf nsz <2 x float> %165, %shift249
  %167 = shufflevector <2 x float> %166, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %168 = insertelement <4 x float> poison, float %136, i64 0
  %shuffle244 = shufflevector <4 x float> %168, <4 x float> poison, <4 x i32> zeroinitializer
  %169 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %155, i64 0
  %170 = shufflevector <4 x float> %169, <4 x float> %161, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %171 = shufflevector <4 x float> %170, <4 x float> %167, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %172 = fmul reassoc ninf nsz <4 x float> %shuffle244, %171
  %173 = fadd reassoc ninf nsz <4 x float> %172, %134
  %174 = icmp ugt i32 %74, 2
  br i1 %174, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %175 = getelementptr float, float* %80, i64 3
  %176 = load float, float* %175, align 4
  %177 = add <2 x i32> %84, <i32 3, i32 -3>
  %178 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %177, i1 true)
  %179 = sub <2 x i32> %178, %92
  %180 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %179, <2 x i32> zeroinitializer)
  %181 = mul <2 x i32> %180, <i32 -2, i32 -2>
  %182 = add <2 x i32> %181, %178
  %183 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %182, <2 x i32> zeroinitializer)
  %184 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %183)
  %185 = mul <2 x i32> %184, %100
  %186 = add <2 x i32> %185, %102
  %187 = mul <2 x i32> %186, %105
  %188 = sext <2 x i32> %187 to <2 x i64>
  %189 = extractelement <2 x i64> %188, i64 1
  %190 = getelementptr float, float* %46, i64 %189
  %191 = load float, float* %190, align 4
  %192 = extractelement <2 x i64> %188, i64 0
  %193 = getelementptr float, float* %46, i64 %192
  %194 = load float, float* %193, align 4
  %195 = fadd reassoc ninf nsz float %194, %191
  %196 = add <2 x i32> %187, <i32 1, i32 1>
  %197 = sext <2 x i32> %196 to <2 x i64>
  %198 = getelementptr float, <2 x float*> %118, <2 x i64> %197
  %199 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %198, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift250 = shufflevector <2 x float> %199, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %200 = fadd reassoc ninf nsz <2 x float> %199, %shift250
  %201 = shufflevector <2 x float> %200, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %202 = add <2 x i32> %187, <i32 2, i32 2>
  %203 = sext <2 x i32> %202 to <2 x i64>
  %204 = getelementptr float, <2 x float*> %118, <2 x i64> %203
  %205 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %204, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift251 = shufflevector <2 x float> %205, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %206 = fadd reassoc ninf nsz <2 x float> %205, %shift251
  %207 = shufflevector <2 x float> %206, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %208 = insertelement <4 x float> poison, float %176, i64 0
  %shuffle243 = shufflevector <4 x float> %208, <4 x float> poison, <4 x i32> zeroinitializer
  %209 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %195, i64 0
  %210 = shufflevector <4 x float> %209, <4 x float> %201, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %211 = shufflevector <4 x float> %210, <4 x float> %207, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %212 = fmul reassoc ninf nsz <4 x float> %shuffle243, %211
  %213 = fadd reassoc ninf nsz <4 x float> %212, %173
  %.not209 = icmp eq i32 %74, 3
  br i1 %.not209, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %214 = getelementptr float, float* %80, i64 4
  %215 = load float, float* %214, align 4
  %216 = add <2 x i32> %84, <i32 4, i32 -4>
  %217 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %216, i1 true)
  %218 = sub <2 x i32> %217, %92
  %219 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %218, <2 x i32> zeroinitializer)
  %220 = mul <2 x i32> %219, <i32 -2, i32 -2>
  %221 = add <2 x i32> %220, %217
  %222 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %221, <2 x i32> zeroinitializer)
  %223 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %222)
  %224 = mul <2 x i32> %223, %100
  %225 = add <2 x i32> %224, %102
  %226 = mul <2 x i32> %225, %105
  %227 = sext <2 x i32> %226 to <2 x i64>
  %228 = extractelement <2 x i64> %227, i64 1
  %229 = getelementptr float, float* %46, i64 %228
  %230 = load float, float* %229, align 4
  %231 = extractelement <2 x i64> %227, i64 0
  %232 = getelementptr float, float* %46, i64 %231
  %233 = load float, float* %232, align 4
  %234 = fadd reassoc ninf nsz float %233, %230
  %235 = add <2 x i32> %226, <i32 1, i32 1>
  %236 = sext <2 x i32> %235 to <2 x i64>
  %237 = getelementptr float, <2 x float*> %118, <2 x i64> %236
  %238 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %237, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift252 = shufflevector <2 x float> %238, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %239 = fadd reassoc ninf nsz <2 x float> %238, %shift252
  %240 = shufflevector <2 x float> %239, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %241 = add <2 x i32> %226, <i32 2, i32 2>
  %242 = sext <2 x i32> %241 to <2 x i64>
  %243 = getelementptr float, <2 x float*> %118, <2 x i64> %242
  %244 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %243, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift253 = shufflevector <2 x float> %244, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %245 = fadd reassoc ninf nsz <2 x float> %244, %shift253
  %246 = shufflevector <2 x float> %245, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %247 = insertelement <4 x float> poison, float %215, i64 0
  %shuffle242 = shufflevector <4 x float> %247, <4 x float> poison, <4 x i32> zeroinitializer
  %248 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %234, i64 0
  %249 = shufflevector <4 x float> %248, <4 x float> %240, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %250 = shufflevector <4 x float> %249, <4 x float> %246, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %251 = fmul reassoc ninf nsz <4 x float> %shuffle242, %250
  %252 = fadd reassoc ninf nsz <4 x float> %251, %213
  %253 = icmp ugt i32 %74, 4
  br i1 %253, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %254 = getelementptr float, float* %80, i64 5
  %255 = load float, float* %254, align 4
  %256 = add <2 x i32> %84, <i32 5, i32 -5>
  %257 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %256, i1 true)
  %258 = sub <2 x i32> %257, %92
  %259 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %258, <2 x i32> zeroinitializer)
  %260 = mul <2 x i32> %259, <i32 -2, i32 -2>
  %261 = add <2 x i32> %260, %257
  %262 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %261, <2 x i32> zeroinitializer)
  %263 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %262)
  %264 = mul <2 x i32> %263, %100
  %265 = add <2 x i32> %264, %102
  %266 = mul <2 x i32> %265, %105
  %267 = sext <2 x i32> %266 to <2 x i64>
  %268 = extractelement <2 x i64> %267, i64 1
  %269 = getelementptr float, float* %46, i64 %268
  %270 = load float, float* %269, align 4
  %271 = extractelement <2 x i64> %267, i64 0
  %272 = getelementptr float, float* %46, i64 %271
  %273 = load float, float* %272, align 4
  %274 = fadd reassoc ninf nsz float %273, %270
  %275 = add <2 x i32> %266, <i32 1, i32 1>
  %276 = sext <2 x i32> %275 to <2 x i64>
  %277 = getelementptr float, <2 x float*> %118, <2 x i64> %276
  %278 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %277, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift254 = shufflevector <2 x float> %278, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %279 = fadd reassoc ninf nsz <2 x float> %278, %shift254
  %280 = shufflevector <2 x float> %279, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %281 = add <2 x i32> %266, <i32 2, i32 2>
  %282 = sext <2 x i32> %281 to <2 x i64>
  %283 = getelementptr float, <2 x float*> %118, <2 x i64> %282
  %284 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %283, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift255 = shufflevector <2 x float> %284, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %285 = fadd reassoc ninf nsz <2 x float> %284, %shift255
  %286 = shufflevector <2 x float> %285, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %287 = insertelement <4 x float> poison, float %255, i64 0
  %shuffle241 = shufflevector <4 x float> %287, <4 x float> poison, <4 x i32> zeroinitializer
  %288 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %274, i64 0
  %289 = shufflevector <4 x float> %288, <4 x float> %280, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %290 = shufflevector <4 x float> %289, <4 x float> %286, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %291 = fmul reassoc ninf nsz <4 x float> %shuffle241, %290
  %292 = fadd reassoc ninf nsz <4 x float> %291, %252
  %.not210 = icmp eq i32 %74, 5
  br i1 %.not210, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %293 = getelementptr float, float* %80, i64 6
  %294 = load float, float* %293, align 4
  %295 = add <2 x i32> %84, <i32 6, i32 -6>
  %296 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %295, i1 true)
  %297 = sub <2 x i32> %296, %92
  %298 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %297, <2 x i32> zeroinitializer)
  %299 = mul <2 x i32> %298, <i32 -2, i32 -2>
  %300 = add <2 x i32> %299, %296
  %301 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %300, <2 x i32> zeroinitializer)
  %302 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %301)
  %303 = mul <2 x i32> %302, %100
  %304 = add <2 x i32> %303, %102
  %305 = mul <2 x i32> %304, %105
  %306 = sext <2 x i32> %305 to <2 x i64>
  %307 = extractelement <2 x i64> %306, i64 1
  %308 = getelementptr float, float* %46, i64 %307
  %309 = load float, float* %308, align 4
  %310 = extractelement <2 x i64> %306, i64 0
  %311 = getelementptr float, float* %46, i64 %310
  %312 = load float, float* %311, align 4
  %313 = fadd reassoc ninf nsz float %312, %309
  %314 = add <2 x i32> %305, <i32 1, i32 1>
  %315 = sext <2 x i32> %314 to <2 x i64>
  %316 = getelementptr float, <2 x float*> %118, <2 x i64> %315
  %317 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %316, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift256 = shufflevector <2 x float> %317, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %318 = fadd reassoc ninf nsz <2 x float> %317, %shift256
  %319 = shufflevector <2 x float> %318, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %320 = add <2 x i32> %305, <i32 2, i32 2>
  %321 = sext <2 x i32> %320 to <2 x i64>
  %322 = getelementptr float, <2 x float*> %118, <2 x i64> %321
  %323 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %322, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift257 = shufflevector <2 x float> %323, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %324 = fadd reassoc ninf nsz <2 x float> %323, %shift257
  %325 = shufflevector <2 x float> %324, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %326 = insertelement <4 x float> poison, float %294, i64 0
  %shuffle246 = shufflevector <4 x float> %326, <4 x float> poison, <4 x i32> zeroinitializer
  %327 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %313, i64 0
  %328 = shufflevector <4 x float> %327, <4 x float> %319, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %329 = shufflevector <4 x float> %328, <4 x float> %325, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %330 = fmul reassoc ninf nsz <4 x float> %shuffle246, %329
  %331 = fadd reassoc ninf nsz <4 x float> %330, %292
  %332 = icmp ugt i32 %74, 6
  br i1 %332, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %333 = getelementptr float, float* %80, i64 7
  %334 = load float, float* %333, align 4
  %335 = add <2 x i32> %84, <i32 7, i32 -7>
  %336 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %335, i1 true)
  %337 = sub <2 x i32> %336, %92
  %338 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %337, <2 x i32> zeroinitializer)
  %339 = mul <2 x i32> %338, <i32 -2, i32 -2>
  %340 = add <2 x i32> %339, %336
  %341 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %340, <2 x i32> zeroinitializer)
  %342 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %341)
  %343 = mul <2 x i32> %342, %100
  %344 = add <2 x i32> %343, %102
  %345 = mul <2 x i32> %344, %105
  %346 = sext <2 x i32> %345 to <2 x i64>
  %347 = extractelement <2 x i64> %346, i64 1
  %348 = getelementptr float, float* %46, i64 %347
  %349 = load float, float* %348, align 4
  %350 = extractelement <2 x i64> %346, i64 0
  %351 = getelementptr float, float* %46, i64 %350
  %352 = load float, float* %351, align 4
  %353 = fadd reassoc ninf nsz float %352, %349
  %354 = add <2 x i32> %345, <i32 1, i32 1>
  %355 = sext <2 x i32> %354 to <2 x i64>
  %356 = getelementptr float, <2 x float*> %118, <2 x i64> %355
  %357 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %356, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift258 = shufflevector <2 x float> %357, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %358 = fadd reassoc ninf nsz <2 x float> %357, %shift258
  %359 = shufflevector <2 x float> %358, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %360 = add <2 x i32> %345, <i32 2, i32 2>
  %361 = sext <2 x i32> %360 to <2 x i64>
  %362 = getelementptr float, <2 x float*> %118, <2 x i64> %361
  %363 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %362, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift259 = shufflevector <2 x float> %363, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %364 = fadd reassoc ninf nsz <2 x float> %363, %shift259
  %365 = shufflevector <2 x float> %364, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %366 = insertelement <4 x float> poison, float %334, i64 0
  %shuffle240 = shufflevector <4 x float> %366, <4 x float> poison, <4 x i32> zeroinitializer
  %367 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %353, i64 0
  %368 = shufflevector <4 x float> %367, <4 x float> %359, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %369 = shufflevector <4 x float> %368, <4 x float> %365, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %370 = fmul reassoc ninf nsz <4 x float> %shuffle240, %369
  %371 = fadd reassoc ninf nsz <4 x float> %370, %331
  %.not211 = icmp eq i32 %74, 7
  br i1 %.not211, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %372 = getelementptr float, float* %80, i64 8
  %373 = load float, float* %372, align 4
  %374 = add <2 x i32> %84, <i32 8, i32 -8>
  %375 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %374, i1 true)
  %376 = sub <2 x i32> %375, %92
  %377 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %376, <2 x i32> zeroinitializer)
  %378 = mul <2 x i32> %377, <i32 -2, i32 -2>
  %379 = add <2 x i32> %378, %375
  %380 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %379, <2 x i32> zeroinitializer)
  %381 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %380)
  %382 = mul <2 x i32> %381, %100
  %383 = add <2 x i32> %382, %102
  %384 = mul <2 x i32> %383, %105
  %385 = sext <2 x i32> %384 to <2 x i64>
  %386 = extractelement <2 x i64> %385, i64 1
  %387 = getelementptr float, float* %46, i64 %386
  %388 = load float, float* %387, align 4
  %389 = extractelement <2 x i64> %385, i64 0
  %390 = getelementptr float, float* %46, i64 %389
  %391 = load float, float* %390, align 4
  %392 = fadd reassoc ninf nsz float %391, %388
  %393 = add <2 x i32> %384, <i32 1, i32 1>
  %394 = sext <2 x i32> %393 to <2 x i64>
  %395 = getelementptr float, <2 x float*> %118, <2 x i64> %394
  %396 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %395, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift260 = shufflevector <2 x float> %396, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %397 = fadd reassoc ninf nsz <2 x float> %396, %shift260
  %398 = shufflevector <2 x float> %397, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %399 = add <2 x i32> %384, <i32 2, i32 2>
  %400 = sext <2 x i32> %399 to <2 x i64>
  %401 = getelementptr float, <2 x float*> %118, <2 x i64> %400
  %402 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %401, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift261 = shufflevector <2 x float> %402, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %403 = fadd reassoc ninf nsz <2 x float> %402, %shift261
  %404 = shufflevector <2 x float> %403, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %405 = insertelement <4 x float> poison, float %373, i64 0
  %shuffle239 = shufflevector <4 x float> %405, <4 x float> poison, <4 x i32> zeroinitializer
  %406 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %392, i64 0
  %407 = shufflevector <4 x float> %406, <4 x float> %398, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %408 = shufflevector <4 x float> %407, <4 x float> %404, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %409 = fmul reassoc ninf nsz <4 x float> %shuffle239, %408
  %410 = fadd reassoc ninf nsz <4 x float> %409, %371
  %411 = icmp ugt i32 %74, 8
  br i1 %411, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %412 = getelementptr float, float* %80, i64 9
  %413 = load float, float* %412, align 4
  %414 = add <2 x i32> %84, <i32 9, i32 -9>
  %415 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %414, i1 true)
  %416 = sub <2 x i32> %415, %92
  %417 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %416, <2 x i32> zeroinitializer)
  %418 = mul <2 x i32> %417, <i32 -2, i32 -2>
  %419 = add <2 x i32> %418, %415
  %420 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %419, <2 x i32> zeroinitializer)
  %421 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %420)
  %422 = mul <2 x i32> %421, %100
  %423 = add <2 x i32> %422, %102
  %424 = mul <2 x i32> %423, %105
  %425 = sext <2 x i32> %424 to <2 x i64>
  %426 = extractelement <2 x i64> %425, i64 1
  %427 = getelementptr float, float* %46, i64 %426
  %428 = load float, float* %427, align 4
  %429 = extractelement <2 x i64> %425, i64 0
  %430 = getelementptr float, float* %46, i64 %429
  %431 = load float, float* %430, align 4
  %432 = fadd reassoc ninf nsz float %431, %428
  %433 = add <2 x i32> %424, <i32 1, i32 1>
  %434 = sext <2 x i32> %433 to <2 x i64>
  %435 = getelementptr float, <2 x float*> %118, <2 x i64> %434
  %436 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %435, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift262 = shufflevector <2 x float> %436, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %437 = fadd reassoc ninf nsz <2 x float> %436, %shift262
  %438 = shufflevector <2 x float> %437, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %439 = add <2 x i32> %424, <i32 2, i32 2>
  %440 = sext <2 x i32> %439 to <2 x i64>
  %441 = getelementptr float, <2 x float*> %118, <2 x i64> %440
  %442 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %441, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift263 = shufflevector <2 x float> %442, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %443 = fadd reassoc ninf nsz <2 x float> %442, %shift263
  %444 = shufflevector <2 x float> %443, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %445 = insertelement <4 x float> poison, float %413, i64 0
  %shuffle238 = shufflevector <4 x float> %445, <4 x float> poison, <4 x i32> zeroinitializer
  %446 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %432, i64 0
  %447 = shufflevector <4 x float> %446, <4 x float> %438, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %448 = shufflevector <4 x float> %447, <4 x float> %444, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %449 = fmul reassoc ninf nsz <4 x float> %shuffle238, %448
  %450 = fadd reassoc ninf nsz <4 x float> %449, %410
  %.not212 = icmp eq i32 %74, 9
  br i1 %.not212, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %451 = getelementptr float, float* %80, i64 10
  %452 = load float, float* %451, align 4
  %453 = add <2 x i32> %84, <i32 10, i32 -10>
  %454 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %453, i1 true)
  %455 = sub <2 x i32> %454, %92
  %456 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %455, <2 x i32> zeroinitializer)
  %457 = mul <2 x i32> %456, <i32 -2, i32 -2>
  %458 = add <2 x i32> %457, %454
  %459 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %458, <2 x i32> zeroinitializer)
  %460 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %459)
  %461 = mul <2 x i32> %460, %100
  %462 = add <2 x i32> %461, %102
  %463 = mul <2 x i32> %462, %105
  %464 = sext <2 x i32> %463 to <2 x i64>
  %465 = extractelement <2 x i64> %464, i64 1
  %466 = getelementptr float, float* %46, i64 %465
  %467 = load float, float* %466, align 4
  %468 = extractelement <2 x i64> %464, i64 0
  %469 = getelementptr float, float* %46, i64 %468
  %470 = load float, float* %469, align 4
  %471 = fadd reassoc ninf nsz float %470, %467
  %472 = add <2 x i32> %463, <i32 1, i32 1>
  %473 = sext <2 x i32> %472 to <2 x i64>
  %474 = getelementptr float, <2 x float*> %118, <2 x i64> %473
  %475 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %474, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift264 = shufflevector <2 x float> %475, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %476 = fadd reassoc ninf nsz <2 x float> %475, %shift264
  %477 = shufflevector <2 x float> %476, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %478 = add <2 x i32> %463, <i32 2, i32 2>
  %479 = sext <2 x i32> %478 to <2 x i64>
  %480 = getelementptr float, <2 x float*> %118, <2 x i64> %479
  %481 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %480, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift265 = shufflevector <2 x float> %481, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %482 = fadd reassoc ninf nsz <2 x float> %481, %shift265
  %483 = shufflevector <2 x float> %482, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %484 = insertelement <4 x float> poison, float %452, i64 0
  %shuffle237 = shufflevector <4 x float> %484, <4 x float> poison, <4 x i32> zeroinitializer
  %485 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %471, i64 0
  %486 = shufflevector <4 x float> %485, <4 x float> %477, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %487 = shufflevector <4 x float> %486, <4 x float> %483, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %488 = fmul reassoc ninf nsz <4 x float> %shuffle237, %487
  %489 = fadd reassoc ninf nsz <4 x float> %488, %450
  %490 = icmp ugt i32 %74, 10
  br i1 %490, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %491 = getelementptr float, float* %80, i64 11
  %492 = load float, float* %491, align 4
  %493 = add <2 x i32> %84, <i32 11, i32 -11>
  %494 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %493, i1 true)
  %495 = sub <2 x i32> %494, %92
  %496 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %495, <2 x i32> zeroinitializer)
  %497 = mul <2 x i32> %496, <i32 -2, i32 -2>
  %498 = add <2 x i32> %497, %494
  %499 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %498, <2 x i32> zeroinitializer)
  %500 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %499)
  %501 = mul <2 x i32> %500, %100
  %502 = add <2 x i32> %501, %102
  %503 = mul <2 x i32> %502, %105
  %504 = sext <2 x i32> %503 to <2 x i64>
  %505 = extractelement <2 x i64> %504, i64 1
  %506 = getelementptr float, float* %46, i64 %505
  %507 = load float, float* %506, align 4
  %508 = extractelement <2 x i64> %504, i64 0
  %509 = getelementptr float, float* %46, i64 %508
  %510 = load float, float* %509, align 4
  %511 = fadd reassoc ninf nsz float %510, %507
  %512 = add <2 x i32> %503, <i32 1, i32 1>
  %513 = sext <2 x i32> %512 to <2 x i64>
  %514 = getelementptr float, <2 x float*> %118, <2 x i64> %513
  %515 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %514, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift266 = shufflevector <2 x float> %515, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %516 = fadd reassoc ninf nsz <2 x float> %515, %shift266
  %517 = shufflevector <2 x float> %516, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %518 = add <2 x i32> %503, <i32 2, i32 2>
  %519 = sext <2 x i32> %518 to <2 x i64>
  %520 = getelementptr float, <2 x float*> %118, <2 x i64> %519
  %521 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %520, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift267 = shufflevector <2 x float> %521, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %522 = fadd reassoc ninf nsz <2 x float> %521, %shift267
  %523 = shufflevector <2 x float> %522, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %524 = insertelement <4 x float> poison, float %492, i64 0
  %shuffle236 = shufflevector <4 x float> %524, <4 x float> poison, <4 x i32> zeroinitializer
  %525 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %511, i64 0
  %526 = shufflevector <4 x float> %525, <4 x float> %517, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %527 = shufflevector <4 x float> %526, <4 x float> %523, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %528 = fmul reassoc ninf nsz <4 x float> %shuffle236, %527
  %529 = fadd reassoc ninf nsz <4 x float> %528, %489
  %.not213 = icmp eq i32 %74, 11
  br i1 %.not213, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %530 = getelementptr float, float* %80, i64 12
  %531 = load float, float* %530, align 4
  %532 = add <2 x i32> %84, <i32 12, i32 -12>
  %533 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %532, i1 true)
  %534 = sub <2 x i32> %533, %92
  %535 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %534, <2 x i32> zeroinitializer)
  %536 = mul <2 x i32> %535, <i32 -2, i32 -2>
  %537 = add <2 x i32> %536, %533
  %538 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %537, <2 x i32> zeroinitializer)
  %539 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %538)
  %540 = mul <2 x i32> %539, %100
  %541 = add <2 x i32> %540, %102
  %542 = mul <2 x i32> %541, %105
  %543 = sext <2 x i32> %542 to <2 x i64>
  %544 = extractelement <2 x i64> %543, i64 1
  %545 = getelementptr float, float* %46, i64 %544
  %546 = load float, float* %545, align 4
  %547 = extractelement <2 x i64> %543, i64 0
  %548 = getelementptr float, float* %46, i64 %547
  %549 = load float, float* %548, align 4
  %550 = fadd reassoc ninf nsz float %549, %546
  %551 = add <2 x i32> %542, <i32 1, i32 1>
  %552 = sext <2 x i32> %551 to <2 x i64>
  %553 = getelementptr float, <2 x float*> %118, <2 x i64> %552
  %554 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %553, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift268 = shufflevector <2 x float> %554, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %555 = fadd reassoc ninf nsz <2 x float> %554, %shift268
  %556 = shufflevector <2 x float> %555, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %557 = add <2 x i32> %542, <i32 2, i32 2>
  %558 = sext <2 x i32> %557 to <2 x i64>
  %559 = getelementptr float, <2 x float*> %118, <2 x i64> %558
  %560 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %559, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift269 = shufflevector <2 x float> %560, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %561 = fadd reassoc ninf nsz <2 x float> %560, %shift269
  %562 = shufflevector <2 x float> %561, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %563 = insertelement <4 x float> poison, float %531, i64 0
  %shuffle235 = shufflevector <4 x float> %563, <4 x float> poison, <4 x i32> zeroinitializer
  %564 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %550, i64 0
  %565 = shufflevector <4 x float> %564, <4 x float> %556, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %566 = shufflevector <4 x float> %565, <4 x float> %562, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %567 = fmul reassoc ninf nsz <4 x float> %shuffle235, %566
  %568 = fadd reassoc ninf nsz <4 x float> %567, %529
  %569 = icmp ugt i32 %74, 12
  br i1 %569, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %570 = getelementptr float, float* %80, i64 13
  %571 = load float, float* %570, align 4
  %572 = add <2 x i32> %84, <i32 13, i32 -13>
  %573 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %572, i1 true)
  %574 = sub <2 x i32> %573, %92
  %575 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %574, <2 x i32> zeroinitializer)
  %576 = mul <2 x i32> %575, <i32 -2, i32 -2>
  %577 = add <2 x i32> %576, %573
  %578 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %577, <2 x i32> zeroinitializer)
  %579 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %578)
  %580 = mul <2 x i32> %579, %100
  %581 = add <2 x i32> %580, %102
  %582 = mul <2 x i32> %581, %105
  %583 = sext <2 x i32> %582 to <2 x i64>
  %584 = extractelement <2 x i64> %583, i64 1
  %585 = getelementptr float, float* %46, i64 %584
  %586 = load float, float* %585, align 4
  %587 = extractelement <2 x i64> %583, i64 0
  %588 = getelementptr float, float* %46, i64 %587
  %589 = load float, float* %588, align 4
  %590 = fadd reassoc ninf nsz float %589, %586
  %591 = add <2 x i32> %582, <i32 1, i32 1>
  %592 = sext <2 x i32> %591 to <2 x i64>
  %593 = getelementptr float, <2 x float*> %118, <2 x i64> %592
  %594 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %593, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift270 = shufflevector <2 x float> %594, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %595 = fadd reassoc ninf nsz <2 x float> %594, %shift270
  %596 = shufflevector <2 x float> %595, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %597 = add <2 x i32> %582, <i32 2, i32 2>
  %598 = sext <2 x i32> %597 to <2 x i64>
  %599 = getelementptr float, <2 x float*> %118, <2 x i64> %598
  %600 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %599, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift271 = shufflevector <2 x float> %600, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %601 = fadd reassoc ninf nsz <2 x float> %600, %shift271
  %602 = shufflevector <2 x float> %601, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %603 = insertelement <4 x float> poison, float %571, i64 0
  %shuffle234 = shufflevector <4 x float> %603, <4 x float> poison, <4 x i32> zeroinitializer
  %604 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %590, i64 0
  %605 = shufflevector <4 x float> %604, <4 x float> %596, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %606 = shufflevector <4 x float> %605, <4 x float> %602, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %607 = fmul reassoc ninf nsz <4 x float> %shuffle234, %606
  %608 = fadd reassoc ninf nsz <4 x float> %607, %568
  %.not214 = icmp eq i32 %74, 13
  br i1 %.not214, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %609 = getelementptr float, float* %80, i64 14
  %610 = load float, float* %609, align 4
  %611 = add <2 x i32> %84, <i32 14, i32 -14>
  %612 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %611, i1 true)
  %613 = sub <2 x i32> %612, %92
  %614 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %613, <2 x i32> zeroinitializer)
  %615 = mul <2 x i32> %614, <i32 -2, i32 -2>
  %616 = add <2 x i32> %615, %612
  %617 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %616, <2 x i32> zeroinitializer)
  %618 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %617)
  %619 = mul <2 x i32> %618, %100
  %620 = add <2 x i32> %619, %102
  %621 = mul <2 x i32> %620, %105
  %622 = sext <2 x i32> %621 to <2 x i64>
  %623 = extractelement <2 x i64> %622, i64 1
  %624 = getelementptr float, float* %46, i64 %623
  %625 = load float, float* %624, align 4
  %626 = extractelement <2 x i64> %622, i64 0
  %627 = getelementptr float, float* %46, i64 %626
  %628 = load float, float* %627, align 4
  %629 = fadd reassoc ninf nsz float %628, %625
  %630 = add <2 x i32> %621, <i32 1, i32 1>
  %631 = sext <2 x i32> %630 to <2 x i64>
  %632 = getelementptr float, <2 x float*> %118, <2 x i64> %631
  %633 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %632, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift272 = shufflevector <2 x float> %633, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %634 = fadd reassoc ninf nsz <2 x float> %633, %shift272
  %635 = shufflevector <2 x float> %634, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %636 = add <2 x i32> %621, <i32 2, i32 2>
  %637 = sext <2 x i32> %636 to <2 x i64>
  %638 = getelementptr float, <2 x float*> %118, <2 x i64> %637
  %639 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %638, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift273 = shufflevector <2 x float> %639, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %640 = fadd reassoc ninf nsz <2 x float> %639, %shift273
  %641 = shufflevector <2 x float> %640, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %642 = insertelement <4 x float> poison, float %610, i64 0
  %shuffle233 = shufflevector <4 x float> %642, <4 x float> poison, <4 x i32> zeroinitializer
  %643 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %629, i64 0
  %644 = shufflevector <4 x float> %643, <4 x float> %635, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %645 = shufflevector <4 x float> %644, <4 x float> %641, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %646 = fmul reassoc ninf nsz <4 x float> %shuffle233, %645
  %647 = fadd reassoc ninf nsz <4 x float> %646, %608
  %648 = icmp ugt i32 %74, 14
  br i1 %648, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %649 = getelementptr float, float* %80, i64 15
  %650 = load float, float* %649, align 4
  %651 = add <2 x i32> %84, <i32 15, i32 -15>
  %652 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %651, i1 true)
  %653 = sub <2 x i32> %652, %92
  %654 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %653, <2 x i32> zeroinitializer)
  %655 = mul <2 x i32> %654, <i32 -2, i32 -2>
  %656 = add <2 x i32> %655, %652
  %657 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %656, <2 x i32> zeroinitializer)
  %658 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %657)
  %659 = mul <2 x i32> %658, %100
  %660 = add <2 x i32> %659, %102
  %661 = mul <2 x i32> %660, %105
  %662 = sext <2 x i32> %661 to <2 x i64>
  %663 = extractelement <2 x i64> %662, i64 1
  %664 = getelementptr float, float* %46, i64 %663
  %665 = load float, float* %664, align 4
  %666 = extractelement <2 x i64> %662, i64 0
  %667 = getelementptr float, float* %46, i64 %666
  %668 = load float, float* %667, align 4
  %669 = fadd reassoc ninf nsz float %668, %665
  %670 = add <2 x i32> %661, <i32 1, i32 1>
  %671 = sext <2 x i32> %670 to <2 x i64>
  %672 = getelementptr float, <2 x float*> %118, <2 x i64> %671
  %673 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %672, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift274 = shufflevector <2 x float> %673, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %674 = fadd reassoc ninf nsz <2 x float> %673, %shift274
  %675 = shufflevector <2 x float> %674, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %676 = add <2 x i32> %661, <i32 2, i32 2>
  %677 = sext <2 x i32> %676 to <2 x i64>
  %678 = getelementptr float, <2 x float*> %118, <2 x i64> %677
  %679 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %678, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift275 = shufflevector <2 x float> %679, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %680 = fadd reassoc ninf nsz <2 x float> %679, %shift275
  %681 = shufflevector <2 x float> %680, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %682 = insertelement <4 x float> poison, float %650, i64 0
  %shuffle232 = shufflevector <4 x float> %682, <4 x float> poison, <4 x i32> zeroinitializer
  %683 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %669, i64 0
  %684 = shufflevector <4 x float> %683, <4 x float> %675, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %685 = shufflevector <4 x float> %684, <4 x float> %681, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %686 = fmul reassoc ninf nsz <4 x float> %shuffle232, %685
  %687 = fadd reassoc ninf nsz <4 x float> %686, %647
  %.not215 = icmp eq i32 %74, 15
  br i1 %.not215, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %688 = getelementptr float, float* %80, i64 16
  %689 = load float, float* %688, align 4
  %690 = add <2 x i32> %84, <i32 16, i32 -16>
  %691 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %690, i1 true)
  %692 = sub <2 x i32> %691, %92
  %693 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %692, <2 x i32> zeroinitializer)
  %694 = mul <2 x i32> %693, <i32 -2, i32 -2>
  %695 = add <2 x i32> %694, %691
  %696 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %695, <2 x i32> zeroinitializer)
  %697 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %92, <2 x i32> %696)
  %698 = mul <2 x i32> %697, %100
  %699 = add <2 x i32> %698, %102
  %700 = mul <2 x i32> %699, %105
  %701 = sext <2 x i32> %700 to <2 x i64>
  %702 = extractelement <2 x i64> %701, i64 1
  %703 = getelementptr float, float* %46, i64 %702
  %704 = load float, float* %703, align 4
  %705 = extractelement <2 x i64> %701, i64 0
  %706 = getelementptr float, float* %46, i64 %705
  %707 = load float, float* %706, align 4
  %708 = fadd reassoc ninf nsz float %707, %704
  %709 = add <2 x i32> %700, <i32 1, i32 1>
  %710 = sext <2 x i32> %709 to <2 x i64>
  %711 = getelementptr float, <2 x float*> %118, <2 x i64> %710
  %712 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %711, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift276 = shufflevector <2 x float> %712, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %713 = fadd reassoc ninf nsz <2 x float> %712, %shift276
  %714 = shufflevector <2 x float> %713, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %715 = add <2 x i32> %700, <i32 2, i32 2>
  %716 = sext <2 x i32> %715 to <2 x i64>
  %717 = getelementptr float, <2 x float*> %118, <2 x i64> %716
  %718 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %717, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %shift277 = shufflevector <2 x float> %718, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %719 = fadd reassoc ninf nsz <2 x float> %718, %shift277
  %720 = shufflevector <2 x float> %719, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %721 = insertelement <4 x float> poison, float %689, i64 0
  %shuffle = shufflevector <4 x float> %721, <4 x float> poison, <4 x i32> zeroinitializer
  %722 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %708, i64 0
  %723 = shufflevector <4 x float> %722, <4 x float> %714, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %724 = shufflevector <4 x float> %723, <4 x float> %720, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %725 = fmul reassoc ninf nsz <4 x float> %shuffle, %724
  %726 = fadd reassoc ninf nsz <4 x float> %725, %687
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %727 = phi <4 x float> [ %726, %true_block43 ], [ %687, %after_if42 ], [ %647, %after_if39 ], [ %608, %after_if36 ], [ %568, %after_if33 ], [ %529, %after_if30 ], [ %489, %after_if27 ], [ %450, %after_if24 ], [ %410, %after_if21 ], [ %371, %after_if18 ], [ %331, %after_if15 ], [ %292, %after_if12 ], [ %252, %after_if9 ], [ %213, %after_if6 ], [ %173, %after_if3 ], [ %134, %after_if ], [ %79, %for_loop_body ]
  %728 = extractelement <4 x float> %727, i64 0
  %729 = extractelement <4 x float> %727, i64 3
  %730 = fdiv reassoc ninf nsz float %728, %729
  %731 = load float*, float** %28, align 8
  %732 = load i32, i32* %29, align 4
  %733 = load i32, i32* %30, align 4
  %734 = mul i32 %732, %49
  %735 = add i32 %734, %54
  %736 = mul i32 %735, %733
  %737 = sext i32 %736 to i64
  %738 = getelementptr float, float* %731, i64 %737
  store float %730, float* %738, align 4
  %739 = extractelement <4 x float> %727, i64 1
  %740 = fdiv reassoc ninf nsz float %739, %729
  %741 = load float*, float** %28, align 8
  %742 = load i32, i32* %29, align 4
  %743 = load i32, i32* %30, align 4
  %744 = mul i32 %742, %49
  %745 = add i32 %744, %54
  %746 = mul i32 %745, %743
  %747 = add i32 %746, 1
  %748 = sext i32 %747 to i64
  %749 = getelementptr float, float* %741, i64 %748
  store float %740, float* %749, align 4
  %750 = extractelement <4 x float> %727, i64 2
  %751 = fdiv reassoc ninf nsz float %750, %729
  %752 = load float*, float** %28, align 8
  %753 = load i32, i32* %29, align 4
  %754 = load i32, i32* %30, align 4
  %755 = mul i32 %753, %49
  %756 = add i32 %755, %54
  %757 = mul i32 %756, %754
  %758 = add i32 %757, 2
  %759 = sext i32 %758 to i64
  %760 = getelementptr float, float* %752, i64 %759
  store float %751, float* %760, align 4
  %761 = add nsw i32 %.0115231, 1
  %exitcond.not = icmp eq i32 %19, %761
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
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.abs.v2i32(<2 x i32>, i1 immarg) #7

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
