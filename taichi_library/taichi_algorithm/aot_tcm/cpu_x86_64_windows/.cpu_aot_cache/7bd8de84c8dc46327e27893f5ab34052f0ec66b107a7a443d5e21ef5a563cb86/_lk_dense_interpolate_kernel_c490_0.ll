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
define void @_lk_dense_interpolate_kernel_c490_0_kernel_0_serial(%struct.RuntimeContext.60* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.60* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %1, i64 0, i32 1, i32 0, i32 1
  %5 = load i32, i32* %4, align 4
  %6 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %1, i64 0, i32 0, i32 0, i32 0
  %7 = load i32, i32* %6, align 4
  %8 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 16
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %0, align 8
  %15 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %14, i64 0, i32 0, i32 0, i32 1
  %16 = load i32, i32* %15, align 4
  %17 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %8, align 8
  %18 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %17, i64 0, i32 14
  %19 = load i8*, i8** %18, align 8
  %20 = getelementptr inbounds i8, i8* %19, i64 12
  %21 = bitcast i8* %20 to i32*
  store i32 %16, i32* %21, align 4
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %0, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %22, i64 0, i32 2
  %24 = load i32, i32* %23, align 4
  %25 = sitofp i32 %24 to float
  %26 = fdiv reassoc ninf nsz float 1.000000e+00, %25
  %27 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %8, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %27, i64 0, i32 14
  %29 = load i8*, i8** %28, align 8
  %30 = getelementptr inbounds i8, i8* %29, i64 8
  %31 = bitcast i8* %30 to float*
  store float %26, float* %31, align 4
  %32 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %33 = tail call i32 @llvm.smax.i32(i32 %5, i32 0)
  %34 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %8, align 8
  %35 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %34, i64 0, i32 14
  %36 = load i8*, i8** %35, align 8
  %37 = getelementptr inbounds i8, i8* %36, i64 4
  %38 = bitcast i8* %37 to i32*
  store i32 %33, i32* %38, align 4
  %39 = mul i32 %33, %32
  %40 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %8, align 8
  %41 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %40, i64 0, i32 14
  %42 = bitcast i8** %41 to i32**
  %43 = load i32*, i32** %42, align 8
  store i32 %39, i32* %43, align 4
  ret void
}

; Function Attrs: nounwind
define void @_lk_dense_interpolate_kernel_c490_0_kernel_1_range_for(%struct.RuntimeContext.60* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.60* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %20, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %22, i64 0, i32 3
  %24 = load i32, i32* %23, align 4
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %22, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %22, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %22, i64 0, i32 0, i32 0, i32 2
  %28 = insertelement <2 x i32> poison, i32 %24, i64 0
  %29 = shufflevector <2 x i32> %28, <2 x i32> poison, <2 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.011 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %228, %after_if ]
  %30 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %.011, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.011
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.011, 0
  %41 = icmp ne i32 %.011, %37
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg5 = sext i1 %43 to i32
  %44 = add i32 %36, %.neg5
  %45 = mul i32 %35, -1
  %46 = mul i32 %45, %44
  %47 = add i32 %.011, %46
  %48 = getelementptr inbounds i8, i8* %32, i64 8
  %49 = bitcast i8* %48 to float*
  %50 = load float, float* %49, align 4
  %51 = getelementptr inbounds i8, i8* %32, i64 12
  %52 = insertelement <2 x i32> poison, i32 %44, i64 0
  %53 = insertelement <2 x i32> %52, i32 %47, i64 1
  %54 = sub <2 x i32> %53, %29
  %55 = sitofp <2 x i32> %54 to <2 x float>
  %56 = insertelement <2 x float> poison, float %50, i64 0
  %57 = shufflevector <2 x float> %56, <2 x float> poison, <2 x i32> zeroinitializer
  %58 = fmul reassoc ninf nsz <2 x float> %57, %55
  %59 = call reassoc ninf nsz <2 x float> @llvm.floor.v2f32(<2 x float> %58)
  %60 = fptosi <2 x float> %59 to <2 x i32>
  %61 = bitcast i8* %51 to <2 x i32>*
  %62 = load <2 x i32>, <2 x i32>* %61, align 4
  %63 = add <2 x i32> %62, <i32 -1, i32 -1>
  %shuffle = shufflevector <2 x i32> %63, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %64 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %60, <2 x i32> %shuffle)
  %65 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %64, <2 x i32> zeroinitializer)
  %66 = extractelement <2 x i32> %65, i64 1
  %67 = add nuw i32 %66, 1
  %68 = extractelement <2 x i32> %63, i64 0
  %69 = tail call i32 @llvm.smin.i32(i32 %67, i32 %68)
  %70 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %71 = extractelement <2 x i32> %65, i64 0
  %72 = add nuw i32 %71, 1
  %73 = extractelement <2 x i32> %63, i64 1
  %74 = tail call i32 @llvm.smin.i32(i32 %72, i32 %73)
  %75 = tail call i32 @llvm.smax.i32(i32 %74, i32 0)
  %76 = sitofp <2 x i32> %65 to <2 x float>
  %77 = fsub reassoc ninf nsz <2 x float> %58, %76
  %78 = call reassoc ninf nsz <2 x float> @llvm.minnum.v2f32(<2 x float> %77, <2 x float> <float 1.000000e+00, float 1.000000e+00>)
  %79 = call reassoc ninf nsz <2 x float> @llvm.maxnum.v2f32(<2 x float> %78, <2 x float> zeroinitializer)
  %80 = extractelement <2 x float> %79, i64 1
  %factor = fmul reassoc ninf nsz float %80, -2.000000e+00
  %81 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %82 = fmul reassoc ninf nsz <2 x float> %79, %79
  %83 = insertelement <2 x float> %79, float -2.000000e+00, i64 0
  %84 = fmul reassoc ninf nsz <2 x float> %79, %83
  %85 = insertelement <2 x float> poison, float %81, i64 1
  %86 = fmul reassoc ninf nsz <2 x float> %84, %85
  %87 = extractelement <2 x float> %82, i64 0
  %88 = extractelement <2 x float> %84, i64 0
  %89 = fadd reassoc ninf nsz float %88, 3.000000e+00
  %90 = fmul reassoc ninf nsz float %87, %89
  %91 = fsub reassoc ninf nsz float 1.000000e+00, %90
  %92 = load float*, float** %25, align 8
  %93 = load i32, i32* %26, align 4
  %94 = load i32, i32* %27, align 4
  %95 = mul i32 %71, %93
  %96 = add i32 %66, %95
  %97 = mul i32 %96, %94
  %98 = add i32 %97, 2
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %92, i64 %99
  %101 = load float, float* %100, align 4
  %102 = fmul reassoc ninf nsz float %91, %101
  %103 = extractelement <2 x float> %86, i64 1
  %104 = fsub reassoc ninf nsz float 1.000000e+00, %103
  %105 = fmul reassoc ninf nsz float %102, %104
  %106 = add i32 %70, %95
  %107 = mul i32 %106, %94
  %108 = add i32 %107, 2
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, float* %92, i64 %109
  %111 = load float, float* %110, align 4
  %112 = fmul reassoc ninf nsz float %91, %111
  %113 = fmul reassoc ninf nsz float %112, %103
  %114 = mul i32 %75, %93
  %115 = add i32 %114, %66
  %116 = mul i32 %115, %94
  %117 = add i32 %116, 2
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, float* %92, i64 %118
  %120 = load float, float* %119, align 4
  %121 = fmul reassoc ninf nsz float %90, %120
  %122 = fmul reassoc ninf nsz float %121, %104
  %123 = add i32 %70, %114
  %124 = mul i32 %123, %94
  %125 = add i32 %124, 2
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, float* %92, i64 %126
  %128 = load float, float* %127, align 4
  %129 = fmul reassoc ninf nsz float %90, %128
  %130 = fmul reassoc ninf nsz float %129, %103
  %131 = fadd reassoc ninf nsz float %130, %113
  %132 = fadd reassoc ninf nsz float %131, %105
  %133 = fadd reassoc ninf nsz float %132, %122
  %134 = fcmp reassoc ninf nsz ogt float %133, 0x3EB0C6F7A0000000
  br i1 %134, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %135 = sext i32 %97 to i64
  %136 = getelementptr float, float* %92, i64 %135
  %137 = load float, float* %136, align 4
  %138 = fmul reassoc ninf nsz float %137, %105
  %139 = sext i32 %107 to i64
  %140 = getelementptr float, float* %92, i64 %139
  %141 = load float, float* %140, align 4
  %142 = fmul reassoc ninf nsz float %141, %113
  %143 = fadd reassoc ninf nsz float %142, %138
  %144 = sext i32 %116 to i64
  %145 = getelementptr float, float* %92, i64 %144
  %146 = load float, float* %145, align 4
  %147 = fmul reassoc ninf nsz float %146, %122
  %148 = fadd reassoc ninf nsz float %143, %147
  %149 = sext i32 %124 to i64
  %150 = getelementptr float, float* %92, i64 %149
  %151 = load float, float* %150, align 4
  %152 = fmul reassoc ninf nsz float %151, %130
  %153 = fadd reassoc ninf nsz float %148, %152
  %154 = fdiv reassoc ninf nsz float %153, %133
  %155 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %20, align 8
  %156 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %155, i64 0, i32 1, i32 1
  %157 = load float*, float** %156, align 8
  %158 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %155, i64 0, i32 1, i32 0, i32 1
  %159 = load i32, i32* %158, align 4
  %160 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %155, i64 0, i32 1, i32 0, i32 2
  %161 = load i32, i32* %160, align 4
  %162 = sub i32 %159, %35
  %163 = mul i32 %162, %44
  %164 = add i32 %.011, %163
  %165 = mul i32 %164, %161
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, float* %157, i64 %166
  store float %154, float* %167, align 4
  %168 = load float*, float** %25, align 8
  %169 = load i32, i32* %26, align 4
  %170 = load i32, i32* %27, align 4
  %171 = mul i32 %169, %71
  %172 = add i32 %171, %66
  %173 = mul i32 %172, %170
  %174 = add i32 %173, 1
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, float* %168, i64 %175
  %177 = load float, float* %176, align 4
  %178 = fmul reassoc ninf nsz float %177, %105
  %179 = add i32 %171, %70
  %180 = mul i32 %179, %170
  %181 = add i32 %180, 1
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, float* %168, i64 %182
  %184 = load float, float* %183, align 4
  %185 = fmul reassoc ninf nsz float %184, %113
  %186 = fadd reassoc ninf nsz float %185, %178
  %187 = mul i32 %169, %75
  %188 = add i32 %187, %66
  %189 = mul i32 %188, %170
  %190 = add i32 %189, 1
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, float* %168, i64 %191
  %193 = load float, float* %192, align 4
  %194 = fmul reassoc ninf nsz float %193, %122
  %195 = fadd reassoc ninf nsz float %186, %194
  %196 = add i32 %187, %70
  %197 = mul i32 %196, %170
  %198 = add i32 %197, 1
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, float* %168, i64 %199
  %201 = load float, float* %200, align 4
  %202 = fmul reassoc ninf nsz float %201, %130
  %203 = fadd reassoc ninf nsz float %195, %202
  %204 = fdiv reassoc ninf nsz float %203, %133
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %205 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }** %20, align 8
  %206 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %205, i64 0, i32 1, i32 1
  %207 = load float*, float** %206, align 8
  %208 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %205, i64 0, i32 1, i32 0, i32 1
  %209 = load i32, i32* %208, align 4
  %210 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, float }* %205, i64 0, i32 1, i32 0, i32 2
  %211 = load i32, i32* %210, align 4
  %212 = sub i32 %209, %35
  %213 = mul i32 %212, %44
  %214 = add i32 %.011, %213
  %215 = mul i32 %214, %211
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, float* %207, i64 %216
  store float 0.000000e+00, float* %217, align 4
  br label %after_if

after_if:                                         ; preds = %false_block, %true_block
  %.sink23 = phi float** [ %206, %false_block ], [ %156, %true_block ]
  %.sink22 = phi i32* [ %208, %false_block ], [ %158, %true_block ]
  %.sink21 = phi i32* [ %210, %false_block ], [ %160, %true_block ]
  %.sink = phi float [ 0.000000e+00, %false_block ], [ %204, %true_block ]
  %218 = load float*, float** %.sink23, align 8
  %219 = load i32, i32* %.sink22, align 4
  %220 = load i32, i32* %.sink21, align 4
  %221 = sub i32 %219, %35
  %222 = mul i32 %221, %44
  %223 = add i32 %.011, %222
  %224 = mul i32 %223, %220
  %225 = add i32 %224, 1
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, float* %218, i64 %226
  store float %.sink, float* %227, align 4
  %228 = add nsw i32 %.011, 1
  %exitcond.not = icmp eq i32 %19, %228
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
declare <2 x float> @llvm.floor.v2f32(<2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.minnum.v2f32(<2 x float>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.maxnum.v2f32(<2 x float>, <2 x float>) #7

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
