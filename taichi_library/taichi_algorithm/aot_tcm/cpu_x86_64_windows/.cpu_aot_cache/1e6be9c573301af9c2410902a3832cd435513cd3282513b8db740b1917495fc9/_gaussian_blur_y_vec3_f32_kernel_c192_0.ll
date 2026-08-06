; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.60*, void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.60 = type { i8*, %struct.LLVMRuntime.59*, i32, i64* }
%struct.LLVMRuntime.59 = type { %struct.PreallocatedMemoryChunk.55, %struct.PreallocatedMemoryChunk.55, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.56*], [1024 x %struct.NodeManager.57*], [1024 x i8*], i8*, %struct.RandState.58*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.55 = type { i8*, i8*, i64 }
%struct.ListManager.56 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.59* }
%struct.NodeManager.57 = type { %struct.LLVMRuntime.59*, i32, i32, i32, i32, %struct.ListManager.56*, %struct.ListManager.56*, %struct.ListManager.56*, i32 }
%struct.RandState.58 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_gaussian_blur_y_vec3_f32_kernel_c192_0_kernel_0_serial(%struct.RuntimeContext.60* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.60* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 12
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %0, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %10, i64 0, i32 3
  %12 = load i32, i32* %11, align 4
  %13 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %10, i64 0, i32 5
  %14 = load i32, i32* %13, align 4
  %15 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %15, i64 0, i32 14
  %17 = load i8*, i8** %16, align 8
  %18 = getelementptr inbounds i8, i8* %17, i64 8
  %19 = bitcast i8* %18 to i32*
  store i32 %14, i32* %19, align 4
  %20 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %21 = tail call i32 @llvm.smax.i32(i32 %12, i32 0)
  %22 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  store i32 %21, i32* %26, align 4
  %27 = mul i32 %21, %20
  %28 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %4, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %28, i64 0, i32 14
  %30 = bitcast i8** %29 to i32**
  %31 = load i32*, i32** %30, align 8
  store i32 %27, i32* %31, align 4
  ret void
}

; Function Attrs: nounwind
define void @_gaussian_blur_y_vec3_f32_kernel_c192_0_kernel_1_range_for(%struct.RuntimeContext.60* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.60* %context, %struct.RuntimeContext.60** %4, align 8
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.60*, i8*, i32)* @function_body, void (%struct.RuntimeContext.60*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.60* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.60* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 4, i32 1
  %23 = load float*, float** %22, align 8
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, { { i32 }, float* }, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if45, %for_loop_body.lr.ph
  %.0115231 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %753, %after_if45 ]
  %29 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.0115231, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.0115231
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.0115231, 0
  %40 = icmp ne i32 %.0115231, %36
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg116 = sext i1 %42 to i32
  %43 = load float, float* %23, align 4
  %44 = load float*, float** %25, align 8
  %45 = load i32, i32* %26, align 4
  %46 = add i32 %35, %.neg116
  %47 = mul i32 %46, %34
  %48 = insertelement <2 x i32> poison, i32 %.0115231, i64 0
  %49 = insertelement <2 x i32> poison, i32 %47, i64 0
  %50 = sub <2 x i32> %48, %49
  %51 = extractelement <2 x i32> %50, i64 0
  %52 = mul i32 %45, %46
  %53 = add i32 %51, %52
  %54 = mul i32 %53, 3
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, float* %44, i64 %55
  %57 = load float, float* %56, align 4
  %58 = add i32 %54, 1
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, float* %44, i64 %59
  %61 = load float, float* %60, align 4
  %62 = add i32 %54, 2
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, float* %44, i64 %63
  %65 = load float, float* %64, align 4
  %66 = fmul reassoc ninf nsz float %57, %43
  %67 = fmul reassoc ninf nsz float %61, %43
  %68 = fmul reassoc ninf nsz float %65, %43
  %69 = getelementptr inbounds i8, i8* %31, i64 8
  %70 = bitcast i8* %69 to i32*
  %71 = load i32, i32* %70, align 4
  %72 = icmp sgt i32 %71, 0
  %73 = insertelement <4 x float> poison, float %66, i64 0
  %74 = insertelement <4 x float> %73, float %67, i64 1
  %75 = insertelement <4 x float> %74, float %68, i64 2
  %76 = insertelement <4 x float> %75, float %43, i64 3
  br i1 %72, label %after_if, label %after_if45

after_for.loopexit:                               ; preds = %after_if45
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_if:                                         ; preds = %for_loop_body
  %77 = load float*, float** %22, align 8
  %78 = getelementptr float, float* %77, i64 1
  %79 = load float, float* %78, align 4
  %80 = insertelement <2 x i32> poison, i32 %46, i64 0
  %81 = shufflevector <2 x i32> %80, <2 x i32> poison, <2 x i32> zeroinitializer
  %82 = add <2 x i32> %81, <i32 1, i32 -1>
  %83 = getelementptr inbounds i8, i8* %31, i64 12
  %84 = bitcast i8* %83 to i32*
  %85 = load i32, i32* %84, align 4
  %86 = add i32 %85, -1
  %87 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %82, i1 true)
  %88 = insertelement <2 x i32> poison, i32 %86, i64 0
  %89 = shufflevector <2 x i32> %88, <2 x i32> poison, <2 x i32> zeroinitializer
  %90 = sub <2 x i32> %87, %89
  %91 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %90, <2 x i32> zeroinitializer)
  %92 = mul <2 x i32> %91, <i32 -2, i32 -2>
  %93 = add <2 x i32> %92, %87
  %94 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %93, <2 x i32> zeroinitializer)
  %95 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %94)
  %96 = insertelement <2 x i32> poison, i32 %45, i64 0
  %97 = shufflevector <2 x i32> %96, <2 x i32> poison, <2 x i32> zeroinitializer
  %98 = mul <2 x i32> %95, %97
  %99 = shufflevector <2 x i32> %50, <2 x i32> poison, <2 x i32> zeroinitializer
  %100 = add <2 x i32> %98, %99
  %101 = mul <2 x i32> %100, <i32 3, i32 3>
  %102 = sext <2 x i32> %101 to <2 x i64>
  %103 = extractelement <2 x i64> %102, i64 1
  %104 = getelementptr float, float* %44, i64 %103
  %105 = load float, float* %104, align 4
  %106 = extractelement <2 x i64> %102, i64 0
  %107 = getelementptr float, float* %44, i64 %106
  %108 = load float, float* %107, align 4
  %109 = add <2 x i32> %101, <i32 1, i32 1>
  %110 = sext <2 x i32> %109 to <2 x i64>
  %111 = insertelement <2 x float*> poison, float* %44, i64 0
  %112 = shufflevector <2 x float*> %111, <2 x float*> poison, <2 x i32> zeroinitializer
  %113 = getelementptr float, <2 x float*> %112, <2 x i64> %110
  %114 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %113, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %115 = add <2 x i32> %101, <i32 2, i32 2>
  %116 = sext <2 x i32> %115 to <2 x i64>
  %117 = getelementptr float, <2 x float*> %112, <2 x i64> %116
  %118 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %117, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %119 = fadd reassoc ninf nsz float %108, %105
  %shift = shufflevector <2 x float> %114, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %120 = fadd reassoc ninf nsz <2 x float> %114, %shift
  %121 = shufflevector <2 x float> %120, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift247 = shufflevector <2 x float> %118, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %122 = fadd reassoc ninf nsz <2 x float> %118, %shift247
  %123 = shufflevector <2 x float> %122, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %124 = insertelement <4 x float> poison, float %79, i64 0
  %shuffle245 = shufflevector <4 x float> %124, <4 x float> poison, <4 x i32> zeroinitializer
  %125 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %119, i64 0
  %126 = shufflevector <4 x float> %125, <4 x float> %121, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %127 = shufflevector <4 x float> %126, <4 x float> %123, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %128 = fmul reassoc ninf nsz <4 x float> %shuffle245, %127
  %129 = fadd reassoc ninf nsz <4 x float> %128, %76
  %.not = icmp eq i32 %71, 1
  br i1 %.not, label %after_if45, label %after_if3

after_if3:                                        ; preds = %after_if
  %130 = getelementptr float, float* %77, i64 2
  %131 = load float, float* %130, align 4
  %132 = add <2 x i32> %81, <i32 2, i32 -2>
  %133 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %132, i1 true)
  %134 = sub <2 x i32> %133, %89
  %135 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %134, <2 x i32> zeroinitializer)
  %136 = mul <2 x i32> %135, <i32 -2, i32 -2>
  %137 = add <2 x i32> %136, %133
  %138 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %137, <2 x i32> zeroinitializer)
  %139 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %138)
  %140 = mul <2 x i32> %139, %97
  %141 = add <2 x i32> %140, %99
  %142 = mul <2 x i32> %141, <i32 3, i32 3>
  %143 = sext <2 x i32> %142 to <2 x i64>
  %144 = extractelement <2 x i64> %143, i64 1
  %145 = getelementptr float, float* %44, i64 %144
  %146 = load float, float* %145, align 4
  %147 = extractelement <2 x i64> %143, i64 0
  %148 = getelementptr float, float* %44, i64 %147
  %149 = load float, float* %148, align 4
  %150 = add <2 x i32> %142, <i32 1, i32 1>
  %151 = sext <2 x i32> %150 to <2 x i64>
  %152 = getelementptr float, <2 x float*> %112, <2 x i64> %151
  %153 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %152, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %154 = add <2 x i32> %142, <i32 2, i32 2>
  %155 = sext <2 x i32> %154 to <2 x i64>
  %156 = getelementptr float, <2 x float*> %112, <2 x i64> %155
  %157 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %156, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %158 = fadd reassoc ninf nsz float %149, %146
  %shift248 = shufflevector <2 x float> %153, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %159 = fadd reassoc ninf nsz <2 x float> %153, %shift248
  %160 = shufflevector <2 x float> %159, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift249 = shufflevector <2 x float> %157, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %161 = fadd reassoc ninf nsz <2 x float> %157, %shift249
  %162 = shufflevector <2 x float> %161, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %163 = insertelement <4 x float> poison, float %131, i64 0
  %shuffle244 = shufflevector <4 x float> %163, <4 x float> poison, <4 x i32> zeroinitializer
  %164 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %158, i64 0
  %165 = shufflevector <4 x float> %164, <4 x float> %160, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %166 = shufflevector <4 x float> %165, <4 x float> %162, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %167 = fmul reassoc ninf nsz <4 x float> %shuffle244, %166
  %168 = fadd reassoc ninf nsz <4 x float> %167, %129
  %169 = icmp ugt i32 %71, 2
  br i1 %169, label %after_if6, label %after_if45

after_if6:                                        ; preds = %after_if3
  %170 = getelementptr float, float* %77, i64 3
  %171 = load float, float* %170, align 4
  %172 = add <2 x i32> %81, <i32 3, i32 -3>
  %173 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %172, i1 true)
  %174 = sub <2 x i32> %173, %89
  %175 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %174, <2 x i32> zeroinitializer)
  %176 = mul <2 x i32> %175, <i32 -2, i32 -2>
  %177 = add <2 x i32> %176, %173
  %178 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %177, <2 x i32> zeroinitializer)
  %179 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %178)
  %180 = mul <2 x i32> %179, %97
  %181 = add <2 x i32> %180, %99
  %182 = mul <2 x i32> %181, <i32 3, i32 3>
  %183 = sext <2 x i32> %182 to <2 x i64>
  %184 = extractelement <2 x i64> %183, i64 1
  %185 = getelementptr float, float* %44, i64 %184
  %186 = load float, float* %185, align 4
  %187 = extractelement <2 x i64> %183, i64 0
  %188 = getelementptr float, float* %44, i64 %187
  %189 = load float, float* %188, align 4
  %190 = add <2 x i32> %182, <i32 1, i32 1>
  %191 = sext <2 x i32> %190 to <2 x i64>
  %192 = getelementptr float, <2 x float*> %112, <2 x i64> %191
  %193 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %192, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %194 = add <2 x i32> %182, <i32 2, i32 2>
  %195 = sext <2 x i32> %194 to <2 x i64>
  %196 = getelementptr float, <2 x float*> %112, <2 x i64> %195
  %197 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %196, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %198 = fadd reassoc ninf nsz float %189, %186
  %shift250 = shufflevector <2 x float> %193, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %199 = fadd reassoc ninf nsz <2 x float> %193, %shift250
  %200 = shufflevector <2 x float> %199, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift251 = shufflevector <2 x float> %197, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %201 = fadd reassoc ninf nsz <2 x float> %197, %shift251
  %202 = shufflevector <2 x float> %201, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %203 = insertelement <4 x float> poison, float %171, i64 0
  %shuffle243 = shufflevector <4 x float> %203, <4 x float> poison, <4 x i32> zeroinitializer
  %204 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %198, i64 0
  %205 = shufflevector <4 x float> %204, <4 x float> %200, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %206 = shufflevector <4 x float> %205, <4 x float> %202, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %207 = fmul reassoc ninf nsz <4 x float> %shuffle243, %206
  %208 = fadd reassoc ninf nsz <4 x float> %207, %168
  %.not209 = icmp eq i32 %71, 3
  br i1 %.not209, label %after_if45, label %after_if9

after_if9:                                        ; preds = %after_if6
  %209 = getelementptr float, float* %77, i64 4
  %210 = load float, float* %209, align 4
  %211 = add <2 x i32> %81, <i32 4, i32 -4>
  %212 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %211, i1 true)
  %213 = sub <2 x i32> %212, %89
  %214 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %213, <2 x i32> zeroinitializer)
  %215 = mul <2 x i32> %214, <i32 -2, i32 -2>
  %216 = add <2 x i32> %215, %212
  %217 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %216, <2 x i32> zeroinitializer)
  %218 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %217)
  %219 = mul <2 x i32> %218, %97
  %220 = add <2 x i32> %219, %99
  %221 = mul <2 x i32> %220, <i32 3, i32 3>
  %222 = sext <2 x i32> %221 to <2 x i64>
  %223 = extractelement <2 x i64> %222, i64 1
  %224 = getelementptr float, float* %44, i64 %223
  %225 = load float, float* %224, align 4
  %226 = extractelement <2 x i64> %222, i64 0
  %227 = getelementptr float, float* %44, i64 %226
  %228 = load float, float* %227, align 4
  %229 = add <2 x i32> %221, <i32 1, i32 1>
  %230 = sext <2 x i32> %229 to <2 x i64>
  %231 = getelementptr float, <2 x float*> %112, <2 x i64> %230
  %232 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %231, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %233 = add <2 x i32> %221, <i32 2, i32 2>
  %234 = sext <2 x i32> %233 to <2 x i64>
  %235 = getelementptr float, <2 x float*> %112, <2 x i64> %234
  %236 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %235, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %237 = fadd reassoc ninf nsz float %228, %225
  %shift252 = shufflevector <2 x float> %232, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %238 = fadd reassoc ninf nsz <2 x float> %232, %shift252
  %239 = shufflevector <2 x float> %238, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift253 = shufflevector <2 x float> %236, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %240 = fadd reassoc ninf nsz <2 x float> %236, %shift253
  %241 = shufflevector <2 x float> %240, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %242 = insertelement <4 x float> poison, float %210, i64 0
  %shuffle242 = shufflevector <4 x float> %242, <4 x float> poison, <4 x i32> zeroinitializer
  %243 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %237, i64 0
  %244 = shufflevector <4 x float> %243, <4 x float> %239, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %245 = shufflevector <4 x float> %244, <4 x float> %241, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %246 = fmul reassoc ninf nsz <4 x float> %shuffle242, %245
  %247 = fadd reassoc ninf nsz <4 x float> %246, %208
  %248 = icmp ugt i32 %71, 4
  br i1 %248, label %after_if12, label %after_if45

after_if12:                                       ; preds = %after_if9
  %249 = getelementptr float, float* %77, i64 5
  %250 = load float, float* %249, align 4
  %251 = add <2 x i32> %81, <i32 5, i32 -5>
  %252 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %251, i1 true)
  %253 = sub <2 x i32> %252, %89
  %254 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %253, <2 x i32> zeroinitializer)
  %255 = mul <2 x i32> %254, <i32 -2, i32 -2>
  %256 = add <2 x i32> %255, %252
  %257 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %256, <2 x i32> zeroinitializer)
  %258 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %257)
  %259 = mul <2 x i32> %258, %97
  %260 = add <2 x i32> %259, %99
  %261 = mul <2 x i32> %260, <i32 3, i32 3>
  %262 = sext <2 x i32> %261 to <2 x i64>
  %263 = extractelement <2 x i64> %262, i64 1
  %264 = getelementptr float, float* %44, i64 %263
  %265 = load float, float* %264, align 4
  %266 = extractelement <2 x i64> %262, i64 0
  %267 = getelementptr float, float* %44, i64 %266
  %268 = load float, float* %267, align 4
  %269 = add <2 x i32> %261, <i32 1, i32 1>
  %270 = sext <2 x i32> %269 to <2 x i64>
  %271 = getelementptr float, <2 x float*> %112, <2 x i64> %270
  %272 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %271, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %273 = add <2 x i32> %261, <i32 2, i32 2>
  %274 = sext <2 x i32> %273 to <2 x i64>
  %275 = getelementptr float, <2 x float*> %112, <2 x i64> %274
  %276 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %275, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %277 = fadd reassoc ninf nsz float %268, %265
  %shift254 = shufflevector <2 x float> %272, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %278 = fadd reassoc ninf nsz <2 x float> %272, %shift254
  %279 = shufflevector <2 x float> %278, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift255 = shufflevector <2 x float> %276, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %280 = fadd reassoc ninf nsz <2 x float> %276, %shift255
  %281 = shufflevector <2 x float> %280, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %282 = insertelement <4 x float> poison, float %250, i64 0
  %shuffle241 = shufflevector <4 x float> %282, <4 x float> poison, <4 x i32> zeroinitializer
  %283 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %277, i64 0
  %284 = shufflevector <4 x float> %283, <4 x float> %279, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %285 = shufflevector <4 x float> %284, <4 x float> %281, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %286 = fmul reassoc ninf nsz <4 x float> %shuffle241, %285
  %287 = fadd reassoc ninf nsz <4 x float> %286, %247
  %.not210 = icmp eq i32 %71, 5
  br i1 %.not210, label %after_if45, label %after_if15

after_if15:                                       ; preds = %after_if12
  %288 = getelementptr float, float* %77, i64 6
  %289 = load float, float* %288, align 4
  %290 = add <2 x i32> %81, <i32 6, i32 -6>
  %291 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %290, i1 true)
  %292 = sub <2 x i32> %291, %89
  %293 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %292, <2 x i32> zeroinitializer)
  %294 = mul <2 x i32> %293, <i32 -2, i32 -2>
  %295 = add <2 x i32> %294, %291
  %296 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %295, <2 x i32> zeroinitializer)
  %297 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %296)
  %298 = mul <2 x i32> %297, %97
  %299 = add <2 x i32> %298, %99
  %300 = mul <2 x i32> %299, <i32 3, i32 3>
  %301 = sext <2 x i32> %300 to <2 x i64>
  %302 = extractelement <2 x i64> %301, i64 1
  %303 = getelementptr float, float* %44, i64 %302
  %304 = load float, float* %303, align 4
  %305 = extractelement <2 x i64> %301, i64 0
  %306 = getelementptr float, float* %44, i64 %305
  %307 = load float, float* %306, align 4
  %308 = add <2 x i32> %300, <i32 1, i32 1>
  %309 = sext <2 x i32> %308 to <2 x i64>
  %310 = getelementptr float, <2 x float*> %112, <2 x i64> %309
  %311 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %310, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %312 = add <2 x i32> %300, <i32 2, i32 2>
  %313 = sext <2 x i32> %312 to <2 x i64>
  %314 = getelementptr float, <2 x float*> %112, <2 x i64> %313
  %315 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %314, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %316 = fadd reassoc ninf nsz float %307, %304
  %shift256 = shufflevector <2 x float> %311, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %317 = fadd reassoc ninf nsz <2 x float> %311, %shift256
  %318 = shufflevector <2 x float> %317, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift257 = shufflevector <2 x float> %315, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %319 = fadd reassoc ninf nsz <2 x float> %315, %shift257
  %320 = shufflevector <2 x float> %319, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %321 = insertelement <4 x float> poison, float %289, i64 0
  %shuffle246 = shufflevector <4 x float> %321, <4 x float> poison, <4 x i32> zeroinitializer
  %322 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %316, i64 0
  %323 = shufflevector <4 x float> %322, <4 x float> %318, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %324 = shufflevector <4 x float> %323, <4 x float> %320, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %325 = fmul reassoc ninf nsz <4 x float> %shuffle246, %324
  %326 = fadd reassoc ninf nsz <4 x float> %325, %287
  %327 = icmp ugt i32 %71, 6
  br i1 %327, label %after_if18, label %after_if45

after_if18:                                       ; preds = %after_if15
  %328 = getelementptr float, float* %77, i64 7
  %329 = load float, float* %328, align 4
  %330 = add <2 x i32> %81, <i32 7, i32 -7>
  %331 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %330, i1 true)
  %332 = sub <2 x i32> %331, %89
  %333 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %332, <2 x i32> zeroinitializer)
  %334 = mul <2 x i32> %333, <i32 -2, i32 -2>
  %335 = add <2 x i32> %334, %331
  %336 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %335, <2 x i32> zeroinitializer)
  %337 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %336)
  %338 = mul <2 x i32> %337, %97
  %339 = add <2 x i32> %338, %99
  %340 = mul <2 x i32> %339, <i32 3, i32 3>
  %341 = sext <2 x i32> %340 to <2 x i64>
  %342 = extractelement <2 x i64> %341, i64 1
  %343 = getelementptr float, float* %44, i64 %342
  %344 = load float, float* %343, align 4
  %345 = extractelement <2 x i64> %341, i64 0
  %346 = getelementptr float, float* %44, i64 %345
  %347 = load float, float* %346, align 4
  %348 = add <2 x i32> %340, <i32 1, i32 1>
  %349 = sext <2 x i32> %348 to <2 x i64>
  %350 = getelementptr float, <2 x float*> %112, <2 x i64> %349
  %351 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %350, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %352 = add <2 x i32> %340, <i32 2, i32 2>
  %353 = sext <2 x i32> %352 to <2 x i64>
  %354 = getelementptr float, <2 x float*> %112, <2 x i64> %353
  %355 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %354, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %356 = fadd reassoc ninf nsz float %347, %344
  %shift258 = shufflevector <2 x float> %351, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %357 = fadd reassoc ninf nsz <2 x float> %351, %shift258
  %358 = shufflevector <2 x float> %357, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift259 = shufflevector <2 x float> %355, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %359 = fadd reassoc ninf nsz <2 x float> %355, %shift259
  %360 = shufflevector <2 x float> %359, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %361 = insertelement <4 x float> poison, float %329, i64 0
  %shuffle240 = shufflevector <4 x float> %361, <4 x float> poison, <4 x i32> zeroinitializer
  %362 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %356, i64 0
  %363 = shufflevector <4 x float> %362, <4 x float> %358, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %364 = shufflevector <4 x float> %363, <4 x float> %360, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %365 = fmul reassoc ninf nsz <4 x float> %shuffle240, %364
  %366 = fadd reassoc ninf nsz <4 x float> %365, %326
  %.not211 = icmp eq i32 %71, 7
  br i1 %.not211, label %after_if45, label %after_if21

after_if21:                                       ; preds = %after_if18
  %367 = getelementptr float, float* %77, i64 8
  %368 = load float, float* %367, align 4
  %369 = add <2 x i32> %81, <i32 8, i32 -8>
  %370 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %369, i1 true)
  %371 = sub <2 x i32> %370, %89
  %372 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %371, <2 x i32> zeroinitializer)
  %373 = mul <2 x i32> %372, <i32 -2, i32 -2>
  %374 = add <2 x i32> %373, %370
  %375 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %374, <2 x i32> zeroinitializer)
  %376 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %375)
  %377 = mul <2 x i32> %376, %97
  %378 = add <2 x i32> %377, %99
  %379 = mul <2 x i32> %378, <i32 3, i32 3>
  %380 = sext <2 x i32> %379 to <2 x i64>
  %381 = extractelement <2 x i64> %380, i64 1
  %382 = getelementptr float, float* %44, i64 %381
  %383 = load float, float* %382, align 4
  %384 = extractelement <2 x i64> %380, i64 0
  %385 = getelementptr float, float* %44, i64 %384
  %386 = load float, float* %385, align 4
  %387 = add <2 x i32> %379, <i32 1, i32 1>
  %388 = sext <2 x i32> %387 to <2 x i64>
  %389 = getelementptr float, <2 x float*> %112, <2 x i64> %388
  %390 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %389, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %391 = add <2 x i32> %379, <i32 2, i32 2>
  %392 = sext <2 x i32> %391 to <2 x i64>
  %393 = getelementptr float, <2 x float*> %112, <2 x i64> %392
  %394 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %393, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %395 = fadd reassoc ninf nsz float %386, %383
  %shift260 = shufflevector <2 x float> %390, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %396 = fadd reassoc ninf nsz <2 x float> %390, %shift260
  %397 = shufflevector <2 x float> %396, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift261 = shufflevector <2 x float> %394, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %398 = fadd reassoc ninf nsz <2 x float> %394, %shift261
  %399 = shufflevector <2 x float> %398, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %400 = insertelement <4 x float> poison, float %368, i64 0
  %shuffle239 = shufflevector <4 x float> %400, <4 x float> poison, <4 x i32> zeroinitializer
  %401 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %395, i64 0
  %402 = shufflevector <4 x float> %401, <4 x float> %397, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %403 = shufflevector <4 x float> %402, <4 x float> %399, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %404 = fmul reassoc ninf nsz <4 x float> %shuffle239, %403
  %405 = fadd reassoc ninf nsz <4 x float> %404, %366
  %406 = icmp ugt i32 %71, 8
  br i1 %406, label %after_if24, label %after_if45

after_if24:                                       ; preds = %after_if21
  %407 = getelementptr float, float* %77, i64 9
  %408 = load float, float* %407, align 4
  %409 = add <2 x i32> %81, <i32 9, i32 -9>
  %410 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %409, i1 true)
  %411 = sub <2 x i32> %410, %89
  %412 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %411, <2 x i32> zeroinitializer)
  %413 = mul <2 x i32> %412, <i32 -2, i32 -2>
  %414 = add <2 x i32> %413, %410
  %415 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %414, <2 x i32> zeroinitializer)
  %416 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %415)
  %417 = mul <2 x i32> %416, %97
  %418 = add <2 x i32> %417, %99
  %419 = mul <2 x i32> %418, <i32 3, i32 3>
  %420 = sext <2 x i32> %419 to <2 x i64>
  %421 = extractelement <2 x i64> %420, i64 1
  %422 = getelementptr float, float* %44, i64 %421
  %423 = load float, float* %422, align 4
  %424 = extractelement <2 x i64> %420, i64 0
  %425 = getelementptr float, float* %44, i64 %424
  %426 = load float, float* %425, align 4
  %427 = add <2 x i32> %419, <i32 1, i32 1>
  %428 = sext <2 x i32> %427 to <2 x i64>
  %429 = getelementptr float, <2 x float*> %112, <2 x i64> %428
  %430 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %429, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %431 = add <2 x i32> %419, <i32 2, i32 2>
  %432 = sext <2 x i32> %431 to <2 x i64>
  %433 = getelementptr float, <2 x float*> %112, <2 x i64> %432
  %434 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %433, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %435 = fadd reassoc ninf nsz float %426, %423
  %shift262 = shufflevector <2 x float> %430, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %436 = fadd reassoc ninf nsz <2 x float> %430, %shift262
  %437 = shufflevector <2 x float> %436, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift263 = shufflevector <2 x float> %434, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %438 = fadd reassoc ninf nsz <2 x float> %434, %shift263
  %439 = shufflevector <2 x float> %438, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %440 = insertelement <4 x float> poison, float %408, i64 0
  %shuffle238 = shufflevector <4 x float> %440, <4 x float> poison, <4 x i32> zeroinitializer
  %441 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %435, i64 0
  %442 = shufflevector <4 x float> %441, <4 x float> %437, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %443 = shufflevector <4 x float> %442, <4 x float> %439, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %444 = fmul reassoc ninf nsz <4 x float> %shuffle238, %443
  %445 = fadd reassoc ninf nsz <4 x float> %444, %405
  %.not212 = icmp eq i32 %71, 9
  br i1 %.not212, label %after_if45, label %after_if27

after_if27:                                       ; preds = %after_if24
  %446 = getelementptr float, float* %77, i64 10
  %447 = load float, float* %446, align 4
  %448 = add <2 x i32> %81, <i32 10, i32 -10>
  %449 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %448, i1 true)
  %450 = sub <2 x i32> %449, %89
  %451 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %450, <2 x i32> zeroinitializer)
  %452 = mul <2 x i32> %451, <i32 -2, i32 -2>
  %453 = add <2 x i32> %452, %449
  %454 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %453, <2 x i32> zeroinitializer)
  %455 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %454)
  %456 = mul <2 x i32> %455, %97
  %457 = add <2 x i32> %456, %99
  %458 = mul <2 x i32> %457, <i32 3, i32 3>
  %459 = sext <2 x i32> %458 to <2 x i64>
  %460 = extractelement <2 x i64> %459, i64 1
  %461 = getelementptr float, float* %44, i64 %460
  %462 = load float, float* %461, align 4
  %463 = extractelement <2 x i64> %459, i64 0
  %464 = getelementptr float, float* %44, i64 %463
  %465 = load float, float* %464, align 4
  %466 = add <2 x i32> %458, <i32 1, i32 1>
  %467 = sext <2 x i32> %466 to <2 x i64>
  %468 = getelementptr float, <2 x float*> %112, <2 x i64> %467
  %469 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %468, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %470 = add <2 x i32> %458, <i32 2, i32 2>
  %471 = sext <2 x i32> %470 to <2 x i64>
  %472 = getelementptr float, <2 x float*> %112, <2 x i64> %471
  %473 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %472, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %474 = fadd reassoc ninf nsz float %465, %462
  %shift264 = shufflevector <2 x float> %469, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %475 = fadd reassoc ninf nsz <2 x float> %469, %shift264
  %476 = shufflevector <2 x float> %475, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift265 = shufflevector <2 x float> %473, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %477 = fadd reassoc ninf nsz <2 x float> %473, %shift265
  %478 = shufflevector <2 x float> %477, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %479 = insertelement <4 x float> poison, float %447, i64 0
  %shuffle237 = shufflevector <4 x float> %479, <4 x float> poison, <4 x i32> zeroinitializer
  %480 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %474, i64 0
  %481 = shufflevector <4 x float> %480, <4 x float> %476, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %482 = shufflevector <4 x float> %481, <4 x float> %478, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %483 = fmul reassoc ninf nsz <4 x float> %shuffle237, %482
  %484 = fadd reassoc ninf nsz <4 x float> %483, %445
  %485 = icmp ugt i32 %71, 10
  br i1 %485, label %after_if30, label %after_if45

after_if30:                                       ; preds = %after_if27
  %486 = getelementptr float, float* %77, i64 11
  %487 = load float, float* %486, align 4
  %488 = add <2 x i32> %81, <i32 11, i32 -11>
  %489 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %488, i1 true)
  %490 = sub <2 x i32> %489, %89
  %491 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %490, <2 x i32> zeroinitializer)
  %492 = mul <2 x i32> %491, <i32 -2, i32 -2>
  %493 = add <2 x i32> %492, %489
  %494 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %493, <2 x i32> zeroinitializer)
  %495 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %494)
  %496 = mul <2 x i32> %495, %97
  %497 = add <2 x i32> %496, %99
  %498 = mul <2 x i32> %497, <i32 3, i32 3>
  %499 = sext <2 x i32> %498 to <2 x i64>
  %500 = extractelement <2 x i64> %499, i64 1
  %501 = getelementptr float, float* %44, i64 %500
  %502 = load float, float* %501, align 4
  %503 = extractelement <2 x i64> %499, i64 0
  %504 = getelementptr float, float* %44, i64 %503
  %505 = load float, float* %504, align 4
  %506 = add <2 x i32> %498, <i32 1, i32 1>
  %507 = sext <2 x i32> %506 to <2 x i64>
  %508 = getelementptr float, <2 x float*> %112, <2 x i64> %507
  %509 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %508, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %510 = add <2 x i32> %498, <i32 2, i32 2>
  %511 = sext <2 x i32> %510 to <2 x i64>
  %512 = getelementptr float, <2 x float*> %112, <2 x i64> %511
  %513 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %512, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %514 = fadd reassoc ninf nsz float %505, %502
  %shift266 = shufflevector <2 x float> %509, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %515 = fadd reassoc ninf nsz <2 x float> %509, %shift266
  %516 = shufflevector <2 x float> %515, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift267 = shufflevector <2 x float> %513, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %517 = fadd reassoc ninf nsz <2 x float> %513, %shift267
  %518 = shufflevector <2 x float> %517, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %519 = insertelement <4 x float> poison, float %487, i64 0
  %shuffle236 = shufflevector <4 x float> %519, <4 x float> poison, <4 x i32> zeroinitializer
  %520 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %514, i64 0
  %521 = shufflevector <4 x float> %520, <4 x float> %516, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %522 = shufflevector <4 x float> %521, <4 x float> %518, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %523 = fmul reassoc ninf nsz <4 x float> %shuffle236, %522
  %524 = fadd reassoc ninf nsz <4 x float> %523, %484
  %.not213 = icmp eq i32 %71, 11
  br i1 %.not213, label %after_if45, label %after_if33

after_if33:                                       ; preds = %after_if30
  %525 = getelementptr float, float* %77, i64 12
  %526 = load float, float* %525, align 4
  %527 = add <2 x i32> %81, <i32 12, i32 -12>
  %528 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %527, i1 true)
  %529 = sub <2 x i32> %528, %89
  %530 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %529, <2 x i32> zeroinitializer)
  %531 = mul <2 x i32> %530, <i32 -2, i32 -2>
  %532 = add <2 x i32> %531, %528
  %533 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %532, <2 x i32> zeroinitializer)
  %534 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %533)
  %535 = mul <2 x i32> %534, %97
  %536 = add <2 x i32> %535, %99
  %537 = mul <2 x i32> %536, <i32 3, i32 3>
  %538 = sext <2 x i32> %537 to <2 x i64>
  %539 = extractelement <2 x i64> %538, i64 1
  %540 = getelementptr float, float* %44, i64 %539
  %541 = load float, float* %540, align 4
  %542 = extractelement <2 x i64> %538, i64 0
  %543 = getelementptr float, float* %44, i64 %542
  %544 = load float, float* %543, align 4
  %545 = add <2 x i32> %537, <i32 1, i32 1>
  %546 = sext <2 x i32> %545 to <2 x i64>
  %547 = getelementptr float, <2 x float*> %112, <2 x i64> %546
  %548 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %547, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %549 = add <2 x i32> %537, <i32 2, i32 2>
  %550 = sext <2 x i32> %549 to <2 x i64>
  %551 = getelementptr float, <2 x float*> %112, <2 x i64> %550
  %552 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %551, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %553 = fadd reassoc ninf nsz float %544, %541
  %shift268 = shufflevector <2 x float> %548, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %554 = fadd reassoc ninf nsz <2 x float> %548, %shift268
  %555 = shufflevector <2 x float> %554, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift269 = shufflevector <2 x float> %552, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %556 = fadd reassoc ninf nsz <2 x float> %552, %shift269
  %557 = shufflevector <2 x float> %556, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %558 = insertelement <4 x float> poison, float %526, i64 0
  %shuffle235 = shufflevector <4 x float> %558, <4 x float> poison, <4 x i32> zeroinitializer
  %559 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %553, i64 0
  %560 = shufflevector <4 x float> %559, <4 x float> %555, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %561 = shufflevector <4 x float> %560, <4 x float> %557, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %562 = fmul reassoc ninf nsz <4 x float> %shuffle235, %561
  %563 = fadd reassoc ninf nsz <4 x float> %562, %524
  %564 = icmp ugt i32 %71, 12
  br i1 %564, label %after_if36, label %after_if45

after_if36:                                       ; preds = %after_if33
  %565 = getelementptr float, float* %77, i64 13
  %566 = load float, float* %565, align 4
  %567 = add <2 x i32> %81, <i32 13, i32 -13>
  %568 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %567, i1 true)
  %569 = sub <2 x i32> %568, %89
  %570 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %569, <2 x i32> zeroinitializer)
  %571 = mul <2 x i32> %570, <i32 -2, i32 -2>
  %572 = add <2 x i32> %571, %568
  %573 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %572, <2 x i32> zeroinitializer)
  %574 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %573)
  %575 = mul <2 x i32> %574, %97
  %576 = add <2 x i32> %575, %99
  %577 = mul <2 x i32> %576, <i32 3, i32 3>
  %578 = sext <2 x i32> %577 to <2 x i64>
  %579 = extractelement <2 x i64> %578, i64 1
  %580 = getelementptr float, float* %44, i64 %579
  %581 = load float, float* %580, align 4
  %582 = extractelement <2 x i64> %578, i64 0
  %583 = getelementptr float, float* %44, i64 %582
  %584 = load float, float* %583, align 4
  %585 = add <2 x i32> %577, <i32 1, i32 1>
  %586 = sext <2 x i32> %585 to <2 x i64>
  %587 = getelementptr float, <2 x float*> %112, <2 x i64> %586
  %588 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %587, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %589 = add <2 x i32> %577, <i32 2, i32 2>
  %590 = sext <2 x i32> %589 to <2 x i64>
  %591 = getelementptr float, <2 x float*> %112, <2 x i64> %590
  %592 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %591, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %593 = fadd reassoc ninf nsz float %584, %581
  %shift270 = shufflevector <2 x float> %588, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %594 = fadd reassoc ninf nsz <2 x float> %588, %shift270
  %595 = shufflevector <2 x float> %594, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift271 = shufflevector <2 x float> %592, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %596 = fadd reassoc ninf nsz <2 x float> %592, %shift271
  %597 = shufflevector <2 x float> %596, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %598 = insertelement <4 x float> poison, float %566, i64 0
  %shuffle234 = shufflevector <4 x float> %598, <4 x float> poison, <4 x i32> zeroinitializer
  %599 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %593, i64 0
  %600 = shufflevector <4 x float> %599, <4 x float> %595, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %601 = shufflevector <4 x float> %600, <4 x float> %597, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %602 = fmul reassoc ninf nsz <4 x float> %shuffle234, %601
  %603 = fadd reassoc ninf nsz <4 x float> %602, %563
  %.not214 = icmp eq i32 %71, 13
  br i1 %.not214, label %after_if45, label %after_if39

after_if39:                                       ; preds = %after_if36
  %604 = getelementptr float, float* %77, i64 14
  %605 = load float, float* %604, align 4
  %606 = add <2 x i32> %81, <i32 14, i32 -14>
  %607 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %606, i1 true)
  %608 = sub <2 x i32> %607, %89
  %609 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %608, <2 x i32> zeroinitializer)
  %610 = mul <2 x i32> %609, <i32 -2, i32 -2>
  %611 = add <2 x i32> %610, %607
  %612 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %611, <2 x i32> zeroinitializer)
  %613 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %612)
  %614 = mul <2 x i32> %613, %97
  %615 = add <2 x i32> %614, %99
  %616 = mul <2 x i32> %615, <i32 3, i32 3>
  %617 = sext <2 x i32> %616 to <2 x i64>
  %618 = extractelement <2 x i64> %617, i64 1
  %619 = getelementptr float, float* %44, i64 %618
  %620 = load float, float* %619, align 4
  %621 = extractelement <2 x i64> %617, i64 0
  %622 = getelementptr float, float* %44, i64 %621
  %623 = load float, float* %622, align 4
  %624 = add <2 x i32> %616, <i32 1, i32 1>
  %625 = sext <2 x i32> %624 to <2 x i64>
  %626 = getelementptr float, <2 x float*> %112, <2 x i64> %625
  %627 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %626, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %628 = add <2 x i32> %616, <i32 2, i32 2>
  %629 = sext <2 x i32> %628 to <2 x i64>
  %630 = getelementptr float, <2 x float*> %112, <2 x i64> %629
  %631 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %630, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %632 = fadd reassoc ninf nsz float %623, %620
  %shift272 = shufflevector <2 x float> %627, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %633 = fadd reassoc ninf nsz <2 x float> %627, %shift272
  %634 = shufflevector <2 x float> %633, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift273 = shufflevector <2 x float> %631, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %635 = fadd reassoc ninf nsz <2 x float> %631, %shift273
  %636 = shufflevector <2 x float> %635, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %637 = insertelement <4 x float> poison, float %605, i64 0
  %shuffle233 = shufflevector <4 x float> %637, <4 x float> poison, <4 x i32> zeroinitializer
  %638 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %632, i64 0
  %639 = shufflevector <4 x float> %638, <4 x float> %634, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %640 = shufflevector <4 x float> %639, <4 x float> %636, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %641 = fmul reassoc ninf nsz <4 x float> %shuffle233, %640
  %642 = fadd reassoc ninf nsz <4 x float> %641, %603
  %643 = icmp ugt i32 %71, 14
  br i1 %643, label %after_if42, label %after_if45

after_if42:                                       ; preds = %after_if39
  %644 = getelementptr float, float* %77, i64 15
  %645 = load float, float* %644, align 4
  %646 = add <2 x i32> %81, <i32 15, i32 -15>
  %647 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %646, i1 true)
  %648 = sub <2 x i32> %647, %89
  %649 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %648, <2 x i32> zeroinitializer)
  %650 = mul <2 x i32> %649, <i32 -2, i32 -2>
  %651 = add <2 x i32> %650, %647
  %652 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %651, <2 x i32> zeroinitializer)
  %653 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %652)
  %654 = mul <2 x i32> %653, %97
  %655 = add <2 x i32> %654, %99
  %656 = mul <2 x i32> %655, <i32 3, i32 3>
  %657 = sext <2 x i32> %656 to <2 x i64>
  %658 = extractelement <2 x i64> %657, i64 1
  %659 = getelementptr float, float* %44, i64 %658
  %660 = load float, float* %659, align 4
  %661 = extractelement <2 x i64> %657, i64 0
  %662 = getelementptr float, float* %44, i64 %661
  %663 = load float, float* %662, align 4
  %664 = add <2 x i32> %656, <i32 1, i32 1>
  %665 = sext <2 x i32> %664 to <2 x i64>
  %666 = getelementptr float, <2 x float*> %112, <2 x i64> %665
  %667 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %666, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %668 = add <2 x i32> %656, <i32 2, i32 2>
  %669 = sext <2 x i32> %668 to <2 x i64>
  %670 = getelementptr float, <2 x float*> %112, <2 x i64> %669
  %671 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %670, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %672 = fadd reassoc ninf nsz float %663, %660
  %shift274 = shufflevector <2 x float> %667, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %673 = fadd reassoc ninf nsz <2 x float> %667, %shift274
  %674 = shufflevector <2 x float> %673, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift275 = shufflevector <2 x float> %671, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %675 = fadd reassoc ninf nsz <2 x float> %671, %shift275
  %676 = shufflevector <2 x float> %675, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %677 = insertelement <4 x float> poison, float %645, i64 0
  %shuffle232 = shufflevector <4 x float> %677, <4 x float> poison, <4 x i32> zeroinitializer
  %678 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %672, i64 0
  %679 = shufflevector <4 x float> %678, <4 x float> %674, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %680 = shufflevector <4 x float> %679, <4 x float> %676, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %681 = fmul reassoc ninf nsz <4 x float> %shuffle232, %680
  %682 = fadd reassoc ninf nsz <4 x float> %681, %642
  %.not215 = icmp eq i32 %71, 15
  br i1 %.not215, label %after_if45, label %true_block43

true_block43:                                     ; preds = %after_if42
  %683 = getelementptr float, float* %77, i64 16
  %684 = load float, float* %683, align 4
  %685 = add <2 x i32> %81, <i32 16, i32 -16>
  %686 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %685, i1 true)
  %687 = sub <2 x i32> %686, %89
  %688 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %687, <2 x i32> zeroinitializer)
  %689 = mul <2 x i32> %688, <i32 -2, i32 -2>
  %690 = add <2 x i32> %689, %686
  %691 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %690, <2 x i32> zeroinitializer)
  %692 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %89, <2 x i32> %691)
  %693 = mul <2 x i32> %692, %97
  %694 = add <2 x i32> %693, %99
  %695 = mul <2 x i32> %694, <i32 3, i32 3>
  %696 = sext <2 x i32> %695 to <2 x i64>
  %697 = extractelement <2 x i64> %696, i64 1
  %698 = getelementptr float, float* %44, i64 %697
  %699 = load float, float* %698, align 4
  %700 = extractelement <2 x i64> %696, i64 0
  %701 = getelementptr float, float* %44, i64 %700
  %702 = load float, float* %701, align 4
  %703 = add <2 x i32> %695, <i32 1, i32 1>
  %704 = sext <2 x i32> %703 to <2 x i64>
  %705 = getelementptr float, <2 x float*> %112, <2 x i64> %704
  %706 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %705, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %707 = add <2 x i32> %695, <i32 2, i32 2>
  %708 = sext <2 x i32> %707 to <2 x i64>
  %709 = getelementptr float, <2 x float*> %112, <2 x i64> %708
  %710 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %709, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %711 = fadd reassoc ninf nsz float %702, %699
  %shift276 = shufflevector <2 x float> %706, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %712 = fadd reassoc ninf nsz <2 x float> %706, %shift276
  %713 = shufflevector <2 x float> %712, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %shift277 = shufflevector <2 x float> %710, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %714 = fadd reassoc ninf nsz <2 x float> %710, %shift277
  %715 = shufflevector <2 x float> %714, <2 x float> poison, <4 x i32> <i32 0, i32 undef, i32 undef, i32 undef>
  %716 = insertelement <4 x float> poison, float %684, i64 0
  %shuffle = shufflevector <4 x float> %716, <4 x float> poison, <4 x i32> zeroinitializer
  %717 = insertelement <4 x float> <float poison, float poison, float poison, float 2.000000e+00>, float %711, i64 0
  %718 = shufflevector <4 x float> %717, <4 x float> %713, <4 x i32> <i32 0, i32 4, i32 undef, i32 3>
  %719 = shufflevector <4 x float> %718, <4 x float> %715, <4 x i32> <i32 0, i32 1, i32 4, i32 3>
  %720 = fmul reassoc ninf nsz <4 x float> %shuffle, %719
  %721 = fadd reassoc ninf nsz <4 x float> %720, %682
  br label %after_if45

after_if45:                                       ; preds = %true_block43, %after_if42, %after_if39, %after_if36, %after_if33, %after_if30, %after_if27, %after_if24, %after_if21, %after_if18, %after_if15, %after_if12, %after_if9, %after_if6, %after_if3, %after_if, %for_loop_body
  %722 = phi <4 x float> [ %721, %true_block43 ], [ %682, %after_if42 ], [ %642, %after_if39 ], [ %603, %after_if36 ], [ %563, %after_if33 ], [ %524, %after_if30 ], [ %484, %after_if27 ], [ %445, %after_if24 ], [ %405, %after_if21 ], [ %366, %after_if18 ], [ %326, %after_if15 ], [ %287, %after_if12 ], [ %247, %after_if9 ], [ %208, %after_if6 ], [ %168, %after_if3 ], [ %129, %after_if ], [ %76, %for_loop_body ]
  %723 = extractelement <4 x float> %722, i64 0
  %724 = extractelement <4 x float> %722, i64 3
  %725 = fdiv reassoc ninf nsz float %723, %724
  %726 = extractelement <4 x float> %722, i64 1
  %727 = fdiv reassoc ninf nsz float %726, %724
  %728 = extractelement <4 x float> %722, i64 2
  %729 = fdiv reassoc ninf nsz float %728, %724
  %730 = load float*, float** %27, align 8
  %731 = load i32, i32* %28, align 4
  %732 = mul i32 %731, %46
  %733 = add i32 %732, %51
  %734 = mul i32 %733, 3
  %735 = sext i32 %734 to i64
  %736 = getelementptr float, float* %730, i64 %735
  store float %725, float* %736, align 4
  %737 = load float*, float** %27, align 8
  %738 = load i32, i32* %28, align 4
  %739 = mul i32 %738, %46
  %740 = add i32 %739, %51
  %741 = mul i32 %740, 3
  %742 = add i32 %741, 1
  %743 = sext i32 %742 to i64
  %744 = getelementptr float, float* %737, i64 %743
  store float %727, float* %744, align 4
  %745 = load float*, float** %27, align 8
  %746 = load i32, i32* %28, align 4
  %747 = mul i32 %746, %46
  %748 = add i32 %747, %51
  %749 = mul i32 %748, 3
  %750 = add i32 %749, 2
  %751 = sext i32 %750 to i64
  %752 = getelementptr float, float* %745, i64 %751
  store float %729, float* %752, align 4
  %753 = add nsw i32 %.0115231, 1
  %exitcond.not = icmp eq i32 %19, %753
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.60, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.60**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.60*, %struct.RuntimeContext.60** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.60* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.60* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
