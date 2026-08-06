; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.204*, void (%struct.RuntimeContext.204*, i8*)*, void (%struct.RuntimeContext.204*, i8*, i32)*, void (%struct.RuntimeContext.204*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.204 = type { i8*, %struct.LLVMRuntime.203*, i32, i64* }
%struct.LLVMRuntime.203 = type { %struct.PreallocatedMemoryChunk.199, %struct.PreallocatedMemoryChunk.199, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.200*], [1024 x %struct.NodeManager.201*], [1024 x i8*], i8*, %struct.RandState.202*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.199 = type { i8*, i8*, i64 }
%struct.ListManager.200 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.203* }
%struct.NodeManager.201 = type { %struct.LLVMRuntime.203*, i32, i32, i32, i32, %struct.ListManager.200*, %struct.ListManager.200*, %struct.ListManager.200*, i32 }
%struct.RandState.202 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_warp_perspective_offset_kernel_c330_0_kernel_0_serial(%struct.RuntimeContext.204* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.204* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.204, %struct.RuntimeContext.204* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.203*, %struct.LLVMRuntime.203** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.203, %struct.LLVMRuntime.203* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.203*, %struct.LLVMRuntime.203** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.203, %struct.LLVMRuntime.203* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_warp_perspective_offset_kernel_c330_0_kernel_1_range_for(%struct.RuntimeContext.204* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.204* %context, %struct.RuntimeContext.204** %4, align 8
  store void (%struct.RuntimeContext.204*, i8*)* null, void (%struct.RuntimeContext.204*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.204*, i8*, i32)* @function_body, void (%struct.RuntimeContext.204*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.204*, i8*)* null, void (%struct.RuntimeContext.204*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.204, %struct.RuntimeContext.204* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.203*, %struct.LLVMRuntime.203** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.203, %struct.LLVMRuntime.203* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.203, %struct.LLVMRuntime.203* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.204* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.204, %struct.RuntimeContext.204* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.203*, %struct.LLVMRuntime.203** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.203, %struct.LLVMRuntime.203* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.204* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %27 = load float*, float** %26, align 8
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %29 = load i32, i32* %28, align 4
  %30 = getelementptr float, float* %27, i64 1
  %31 = getelementptr float, float* %27, i64 2
  %32 = sext i32 %29 to i64
  %33 = getelementptr float, float* %27, i64 %32
  %34 = add i32 %29, 1
  %35 = sext i32 %34 to i64
  %36 = getelementptr float, float* %27, i64 %35
  %37 = add i32 %29, 2
  %38 = sext i32 %37 to i64
  %39 = getelementptr float, float* %27, i64 %38
  %40 = shl i32 %29, 1
  %41 = sext i32 %40 to i64
  %42 = getelementptr float, float* %27, i64 %41
  %43 = getelementptr float, float* %42, i64 1
  %44 = add i32 %40, 2
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, float* %27, i64 %45
  %47 = icmp slt i32 %17, %19
  br i1 %47, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %48 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %49 = load i32, i32* %48, align 4
  %50 = add i32 %49, -1
  %51 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %52 = load i32, i32* %51, align 4
  %53 = add i32 %52, -1
  %54 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %55 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %56 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %58 = insertelement <2 x i32> poison, i32 %50, i64 0
  %59 = shufflevector <2 x i32> %58, <2 x i32> poison, <2 x i32> zeroinitializer
  %60 = insertelement <2 x i32> poison, i32 %53, i64 0
  %61 = shufflevector <2 x i32> %60, <2 x i32> poison, <2 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.010 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %175, %for_loop_body ]
  %62 = load %struct.LLVMRuntime.203*, %struct.LLVMRuntime.203** %3, align 8
  %63 = getelementptr inbounds %struct.LLVMRuntime.203, %struct.LLVMRuntime.203* %62, i64 0, i32 14
  %64 = load i8*, i8** %63, align 8
  %65 = getelementptr inbounds i8, i8* %64, i64 4
  %66 = bitcast i8* %65 to i32*
  %67 = load i32, i32* %66, align 4
  %68 = sdiv i32 %.010, %67
  %69 = mul i32 %68, %67
  %70 = xor i32 %67, %.010
  %71 = icmp slt i32 %70, 0
  %72 = icmp ne i32 %.010, 0
  %73 = icmp ne i32 %.010, %69
  %74 = and i1 %72, %71
  %75 = and i1 %74, %73
  %.neg4 = sext i1 %75 to i32
  %76 = add i32 %68, %.neg4
  %77 = add i32 %76, %23
  %78 = mul i32 %67, -1
  %79 = mul i32 %78, %76
  %80 = add i32 %25, %.010
  %81 = add i32 %80, %79
  %82 = load float, float* %27, align 4
  %83 = sitofp i32 %81 to float
  %84 = fmul reassoc ninf nsz float %82, %83
  %85 = load float, float* %30, align 4
  %86 = sitofp i32 %77 to float
  %87 = fmul reassoc ninf nsz float %85, %86
  %88 = load float, float* %31, align 4
  %89 = fadd reassoc ninf nsz float %87, %88
  %90 = fadd reassoc ninf nsz float %89, %84
  %91 = load float, float* %33, align 4
  %92 = fmul reassoc ninf nsz float %91, %83
  %93 = load float, float* %36, align 4
  %94 = fmul reassoc ninf nsz float %93, %86
  %95 = load float, float* %39, align 4
  %96 = fadd reassoc ninf nsz float %94, %95
  %97 = fadd reassoc ninf nsz float %96, %92
  %98 = load float, float* %42, align 4
  %99 = fmul reassoc ninf nsz float %98, %83
  %100 = load float, float* %43, align 4
  %101 = fmul reassoc ninf nsz float %100, %86
  %102 = load float, float* %46, align 4
  %103 = fadd reassoc ninf nsz float %101, 0x3E112E0BE0000000
  %104 = fadd reassoc ninf nsz float %103, %102
  %105 = fadd reassoc ninf nsz float %104, %99
  %106 = fdiv reassoc ninf nsz float %90, %105
  %107 = fdiv reassoc ninf nsz float %97, %105
  %108 = tail call reassoc ninf nsz float @llvm.floor.f32(float %106)
  %109 = fptosi float %108 to i32
  %110 = tail call reassoc ninf nsz float @llvm.floor.f32(float %107)
  %111 = fptosi float %110 to i32
  %112 = sitofp i32 %109 to float
  %113 = fsub reassoc ninf nsz float %106, %112
  %114 = sitofp i32 %111 to float
  %115 = fsub reassoc ninf nsz float %107, %114
  %116 = add i32 %109, 1
  %117 = add i32 %111, 1
  %118 = load float*, float** %54, align 8
  %119 = load i32, i32* %55, align 4
  %120 = insertelement <2 x i32> poison, i32 %109, i64 0
  %121 = insertelement <2 x i32> %120, i32 %116, i64 1
  %122 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %121, i1 true)
  %123 = sub <2 x i32> %122, %61
  %124 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %123, <2 x i32> zeroinitializer)
  %125 = mul <2 x i32> %124, <i32 -2, i32 -2>
  %126 = add <2 x i32> %125, %122
  %127 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %126, <2 x i32> zeroinitializer)
  %128 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %61, <2 x i32> %127)
  %shuffle11 = shufflevector <2 x i32> %128, <2 x i32> poison, <4 x i32> <i32 0, i32 1, i32 0, i32 1>
  %129 = insertelement <2 x i32> poison, i32 %111, i64 0
  %130 = insertelement <2 x i32> %129, i32 %117, i64 1
  %131 = call <2 x i32> @llvm.abs.v2i32(<2 x i32> %130, i1 true)
  %132 = sub <2 x i32> %131, %59
  %133 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %132, <2 x i32> zeroinitializer)
  %134 = mul <2 x i32> %133, <i32 -2, i32 -2>
  %135 = add <2 x i32> %134, %131
  %136 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %135, <2 x i32> zeroinitializer)
  %137 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %59, <2 x i32> %136)
  %138 = insertelement <2 x i32> poison, i32 %119, i64 0
  %139 = shufflevector <2 x i32> %138, <2 x i32> poison, <2 x i32> zeroinitializer
  %140 = mul <2 x i32> %137, %139
  %shuffle = shufflevector <2 x i32> %140, <2 x i32> poison, <4 x i32> <i32 0, i32 0, i32 1, i32 1>
  %141 = add <4 x i32> %shuffle, %shuffle11
  %142 = extractelement <4 x i32> %141, i64 0
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %118, i64 %143
  %145 = load float, float* %144, align 4
  %146 = extractelement <4 x i32> %141, i64 1
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %118, i64 %147
  %149 = load float, float* %148, align 4
  %150 = extractelement <4 x i32> %141, i64 2
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %118, i64 %151
  %153 = load float, float* %152, align 4
  %154 = extractelement <4 x i32> %141, i64 3
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %118, i64 %155
  %157 = load float, float* %156, align 4
  %158 = fsub reassoc ninf nsz float 1.000000e+00, %113
  %159 = fmul reassoc ninf nsz float %158, %145
  %160 = fmul reassoc ninf nsz float %113, %149
  %161 = fadd reassoc ninf nsz float %159, %160
  %162 = fmul reassoc ninf nsz float %158, %153
  %163 = fmul reassoc ninf nsz float %113, %157
  %164 = fadd reassoc ninf nsz float %162, %163
  %165 = fsub reassoc ninf nsz float %164, %161
  %166 = fmul reassoc ninf nsz float %165, %115
  %167 = fadd reassoc ninf nsz float %166, %161
  %168 = load float*, float** %56, align 8
  %169 = load i32, i32* %57, align 4
  %170 = sub i32 %169, %67
  %171 = mul i32 %170, %76
  %172 = add i32 %.010, %171
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, float* %168, i64 %173
  store float %167, float* %174, align 4
  %175 = add nsw i32 %.010, 1
  %exitcond.not = icmp eq i32 %19, %175
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.204, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.204**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.204*, %struct.RuntimeContext.204** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.204*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.204*, i8*)*, void (%struct.RuntimeContext.204*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.204*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.204*, i8*, i32)*, void (%struct.RuntimeContext.204*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.204*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.204*, i8*)*, void (%struct.RuntimeContext.204*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.204*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.204* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.204* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.204* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.204, %struct.RuntimeContext.204* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.204* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.204* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.204*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.204* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.abs.v2i32(<2 x i32>, i1 immarg) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
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
