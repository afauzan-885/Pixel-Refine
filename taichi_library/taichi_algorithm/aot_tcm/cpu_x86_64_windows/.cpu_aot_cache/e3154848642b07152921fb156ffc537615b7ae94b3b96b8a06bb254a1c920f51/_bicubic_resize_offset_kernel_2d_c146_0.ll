; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.48*, void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.48 = type { i8*, %struct.LLVMRuntime.47*, i32, i64* }
%struct.LLVMRuntime.47 = type { %struct.PreallocatedMemoryChunk.43, %struct.PreallocatedMemoryChunk.43, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.44*], [1024 x %struct.NodeManager.45*], [1024 x i8*], i8*, %struct.RandState.46*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.43 = type { i8*, i8*, i64 }
%struct.ListManager.44 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.47* }
%struct.NodeManager.45 = type { %struct.LLVMRuntime.47*, i32, i32, i32, i32, %struct.ListManager.44*, %struct.ListManager.44*, %struct.ListManager.44*, i32 }
%struct.RandState.46 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_bicubic_resize_offset_kernel_2d_c146_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bicubic_resize_offset_kernel_2d_c146_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.48* %context, %struct.RuntimeContext.48** %4, align 8
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.48*, i8*, i32)* @function_body, void (%struct.RuntimeContext.48*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.48*, i8*)* null, void (%struct.RuntimeContext.48*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.48* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %29 = load i32, i32* %28, align 4
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %31 = load i32, i32* %30, align 4
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %33 = load i32, i32* %32, align 4
  %34 = sitofp i32 %27 to float
  %35 = sitofp i32 %29 to float
  %36 = sitofp i32 %31 to float
  %37 = sitofp i32 %33 to float
  %38 = icmp slt i32 %17, %19
  br i1 %38, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %39 = add i32 %31, -1
  %40 = add i32 %27, -1
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %42 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %45 = insertelement <2 x i32> poison, i32 %40, i64 0
  %46 = shufflevector <2 x i32> %45, <2 x i32> poison, <2 x i32> zeroinitializer
  %47 = insertelement <4 x i32> poison, i32 %39, i64 0
  %shuffle18 = shufflevector <4 x i32> %47, <4 x i32> poison, <4 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.017 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %262, %for_loop_body ]
  %48 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %49 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %48, i64 0, i32 14
  %50 = load i8*, i8** %49, align 8
  %51 = getelementptr inbounds i8, i8* %50, i64 4
  %52 = bitcast i8* %51 to i32*
  %53 = load i32, i32* %52, align 4
  %54 = sdiv i32 %.017, %53
  %55 = mul i32 %54, %53
  %56 = xor i32 %53, %.017
  %57 = icmp slt i32 %56, 0
  %58 = icmp ne i32 %.017, 0
  %59 = icmp ne i32 %.017, %55
  %60 = and i1 %58, %57
  %61 = and i1 %60, %59
  %.neg4 = sext i1 %61 to i32
  %62 = add i32 %54, %.neg4
  %63 = add i32 %62, %23
  %64 = mul i32 %53, -1
  %65 = mul i32 %64, %62
  %66 = add i32 %25, %.017
  %67 = add i32 %66, %65
  %68 = sitofp i32 %63 to float
  %69 = fadd reassoc ninf nsz float %68, 5.000000e-01
  %70 = fmul reassoc ninf nsz float %69, %34
  %71 = fdiv reassoc ninf nsz float %70, %35
  %72 = fadd reassoc ninf nsz float %71, -5.000000e-01
  %73 = sitofp i32 %67 to float
  %74 = fadd reassoc ninf nsz float %73, 5.000000e-01
  %75 = fmul reassoc ninf nsz float %74, %36
  %76 = fdiv reassoc ninf nsz float %75, %37
  %77 = fadd reassoc ninf nsz float %76, -5.000000e-01
  %78 = tail call reassoc ninf nsz float @llvm.floor.f32(float %77)
  %79 = fptosi float %78 to i32
  %80 = tail call reassoc ninf nsz float @llvm.floor.f32(float %72)
  %81 = fptosi float %80 to i32
  %82 = sitofp i32 %79 to float
  %83 = fsub reassoc ninf nsz float %77, %82
  %84 = tail call float @llvm.fabs.f32(float %83)
  %85 = fadd reassoc ninf nsz float %84, 1.000000e+00
  %86 = fmul reassoc ninf nsz float %85, %85
  %87 = fmul reassoc ninf nsz float %85, 7.500000e-01
  %88 = fmul reassoc ninf nsz float %85, -6.000000e+00
  %89 = fsub reassoc ninf nsz float 3.750000e+00, %87
  %reass.mul = fmul reassoc ninf nsz float %86, %89
  %90 = fadd reassoc ninf nsz float %88, 3.000000e+00
  %91 = fadd reassoc ninf nsz float %90, %reass.mul
  %92 = fmul reassoc ninf nsz float %83, %83
  %93 = fmul reassoc ninf nsz float %92, 1.250000e+00
  %94 = fmul reassoc ninf nsz float %93, %84
  %95 = fmul reassoc ninf nsz float %92, 2.250000e+00
  %96 = fsub reassoc ninf nsz float %94, %95
  %97 = fadd reassoc ninf nsz float %96, 1.000000e+00
  %98 = fsub reassoc ninf nsz float 1.000000e+00, %84
  %99 = fmul reassoc ninf nsz float %98, %98
  %100 = fmul reassoc ninf nsz float %98, 1.250000e+00
  %101 = fadd reassoc ninf nsz float %100, -2.250000e+00
  %102 = fmul reassoc ninf nsz float %101, %99
  %103 = fadd reassoc ninf nsz float %102, 1.000000e+00
  %104 = fsub reassoc ninf nsz float 2.000000e+00, %84
  %105 = fmul reassoc ninf nsz float %104, %104
  %106 = fmul reassoc ninf nsz float %104, 7.500000e-01
  %107 = fmul reassoc ninf nsz float %104, -6.000000e+00
  %108 = fsub reassoc ninf nsz float 3.750000e+00, %106
  %reass.mul8 = fmul reassoc ninf nsz float %105, %108
  %109 = fadd reassoc ninf nsz float %107, 3.000000e+00
  %110 = fadd reassoc ninf nsz float %109, %reass.mul8
  %111 = sitofp i32 %81 to float
  %112 = fsub reassoc ninf nsz float %72, %111
  %113 = tail call float @llvm.fabs.f32(float %112)
  %114 = fadd reassoc ninf nsz float %113, 1.000000e+00
  %115 = fmul reassoc ninf nsz float %114, %114
  %116 = fmul reassoc ninf nsz float %114, 7.500000e-01
  %117 = fmul reassoc ninf nsz float %114, -6.000000e+00
  %118 = fsub reassoc ninf nsz float 3.750000e+00, %116
  %reass.mul10 = fmul reassoc ninf nsz float %115, %118
  %119 = fadd reassoc ninf nsz float %117, 3.000000e+00
  %120 = fadd reassoc ninf nsz float %119, %reass.mul10
  %121 = fmul reassoc ninf nsz float %112, %112
  %122 = fmul reassoc ninf nsz float %113, 1.250000e+00
  %reass.add11 = fadd reassoc ninf nsz float %122, -2.250000e+00
  %reass.mul12 = fmul reassoc ninf nsz float %121, %reass.add11
  %123 = fadd reassoc ninf nsz float %reass.mul12, 1.000000e+00
  %124 = fsub reassoc ninf nsz float 1.000000e+00, %113
  %125 = fmul reassoc ninf nsz float %124, %124
  %126 = fmul reassoc ninf nsz float %124, 1.250000e+00
  %reass.add13 = fadd reassoc ninf nsz float %126, -2.250000e+00
  %reass.mul14 = fmul reassoc ninf nsz float %125, %reass.add13
  %127 = fadd reassoc ninf nsz float %reass.mul14, 1.000000e+00
  %128 = fsub reassoc ninf nsz float 2.000000e+00, %113
  %129 = fmul reassoc ninf nsz float %128, %128
  %130 = fmul reassoc ninf nsz float %128, 7.500000e-01
  %131 = fmul reassoc ninf nsz float %128, -6.000000e+00
  %132 = fsub reassoc ninf nsz float 3.750000e+00, %130
  %reass.mul16 = fmul reassoc ninf nsz float %129, %132
  %133 = fadd reassoc ninf nsz float %131, 3.000000e+00
  %134 = fadd reassoc ninf nsz float %133, %reass.mul16
  %135 = add i32 %81, -1
  %136 = add i32 %79, -1
  %137 = load float*, float** %41, align 8
  %138 = load i32, i32* %42, align 4
  %139 = add i32 %79, 1
  %140 = add i32 %79, 2
  %141 = insertelement <4 x i32> poison, i32 %136, i64 0
  %142 = insertelement <4 x i32> %141, i32 %79, i64 1
  %143 = insertelement <4 x i32> %142, i32 %139, i64 2
  %144 = insertelement <4 x i32> %143, i32 %140, i64 3
  %145 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %144, <4 x i32> zeroinitializer)
  %146 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle18, <4 x i32> %145)
  %shuffle19 = shufflevector <4 x i32> %146, <4 x i32> poison, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 0, i32 1, i32 2, i32 3>
  %147 = insertelement <2 x i32> poison, i32 %135, i64 0
  %148 = insertelement <2 x i32> %147, i32 %81, i64 1
  %149 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %148, <2 x i32> zeroinitializer)
  %150 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %46, <2 x i32> %149)
  %151 = insertelement <2 x i32> poison, i32 %138, i64 0
  %152 = shufflevector <2 x i32> %151, <2 x i32> poison, <2 x i32> zeroinitializer
  %153 = mul <2 x i32> %150, %152
  %shuffle = shufflevector <2 x i32> %153, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1>
  %154 = add <8 x i32> %shuffle, %shuffle19
  %155 = sext <8 x i32> %154 to <8 x i64>
  %156 = extractelement <8 x i64> %155, i64 0
  %157 = getelementptr float, float* %137, i64 %156
  %158 = load float, float* %157, align 4
  %159 = fmul reassoc ninf nsz float %91, %158
  %160 = extractelement <8 x i64> %155, i64 1
  %161 = getelementptr float, float* %137, i64 %160
  %162 = load float, float* %161, align 4
  %163 = fmul reassoc ninf nsz float %97, %162
  %164 = extractelement <8 x i64> %155, i64 2
  %165 = getelementptr float, float* %137, i64 %164
  %166 = load float, float* %165, align 4
  %167 = fmul reassoc ninf nsz float %103, %166
  %168 = extractelement <8 x i64> %155, i64 3
  %169 = getelementptr float, float* %137, i64 %168
  %170 = load float, float* %169, align 4
  %171 = fmul reassoc ninf nsz float %110, %170
  %172 = fadd reassoc ninf nsz float %167, %163
  %173 = fadd reassoc ninf nsz float %172, %159
  %174 = fadd reassoc ninf nsz float %173, %171
  %175 = fmul reassoc ninf nsz float %174, %120
  %176 = extractelement <8 x i64> %155, i64 4
  %177 = getelementptr float, float* %137, i64 %176
  %178 = load float, float* %177, align 4
  %179 = fmul reassoc ninf nsz float %91, %178
  %180 = extractelement <8 x i64> %155, i64 5
  %181 = getelementptr float, float* %137, i64 %180
  %182 = load float, float* %181, align 4
  %183 = fmul reassoc ninf nsz float %97, %182
  %184 = extractelement <8 x i64> %155, i64 6
  %185 = getelementptr float, float* %137, i64 %184
  %186 = load float, float* %185, align 4
  %187 = fmul reassoc ninf nsz float %103, %186
  %188 = extractelement <8 x i64> %155, i64 7
  %189 = getelementptr float, float* %137, i64 %188
  %190 = load float, float* %189, align 4
  %191 = fmul reassoc ninf nsz float %110, %190
  %192 = fadd reassoc ninf nsz float %187, %183
  %193 = fadd reassoc ninf nsz float %192, %179
  %194 = fadd reassoc ninf nsz float %193, %191
  %195 = fmul reassoc ninf nsz float %194, %123
  %196 = fadd reassoc ninf nsz float %175, %195
  %197 = insertelement <2 x i32> poison, i32 %81, i64 0
  %198 = shufflevector <2 x i32> %197, <2 x i32> poison, <2 x i32> zeroinitializer
  %199 = add <2 x i32> %198, <i32 1, i32 2>
  %200 = call <2 x i32> @llvm.smax.v2i32(<2 x i32> %199, <2 x i32> zeroinitializer)
  %201 = call <2 x i32> @llvm.smin.v2i32(<2 x i32> %46, <2 x i32> %200)
  %202 = mul <2 x i32> %201, %152
  %shuffle20 = shufflevector <2 x i32> %202, <2 x i32> poison, <8 x i32> <i32 0, i32 0, i32 0, i32 0, i32 1, i32 1, i32 1, i32 1>
  %203 = shufflevector <4 x i32> %146, <4 x i32> undef, <8 x i32> <i32 0, i32 1, i32 2, i32 3, i32 0, i32 1, i32 2, i32 3>
  %204 = add <8 x i32> %shuffle20, %203
  %205 = extractelement <8 x i32> %204, i64 0
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, float* %137, i64 %206
  %208 = load float, float* %207, align 4
  %209 = fmul reassoc ninf nsz float %91, %208
  %210 = extractelement <8 x i32> %204, i64 1
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %137, i64 %211
  %213 = load float, float* %212, align 4
  %214 = fmul reassoc ninf nsz float %97, %213
  %215 = extractelement <8 x i32> %204, i64 2
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, float* %137, i64 %216
  %218 = load float, float* %217, align 4
  %219 = fmul reassoc ninf nsz float %103, %218
  %220 = extractelement <8 x i32> %204, i64 3
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %137, i64 %221
  %223 = load float, float* %222, align 4
  %224 = fmul reassoc ninf nsz float %110, %223
  %225 = fadd reassoc ninf nsz float %219, %214
  %226 = fadd reassoc ninf nsz float %225, %209
  %227 = fadd reassoc ninf nsz float %226, %224
  %228 = fmul reassoc ninf nsz float %227, %127
  %229 = fadd reassoc ninf nsz float %196, %228
  %230 = extractelement <8 x i32> %204, i64 4
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, float* %137, i64 %231
  %233 = load float, float* %232, align 4
  %234 = fmul reassoc ninf nsz float %91, %233
  %235 = extractelement <8 x i32> %204, i64 5
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, float* %137, i64 %236
  %238 = load float, float* %237, align 4
  %239 = fmul reassoc ninf nsz float %97, %238
  %240 = extractelement <8 x i32> %204, i64 6
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, float* %137, i64 %241
  %243 = load float, float* %242, align 4
  %244 = fmul reassoc ninf nsz float %103, %243
  %245 = extractelement <8 x i32> %204, i64 7
  %246 = sext i32 %245 to i64
  %247 = getelementptr float, float* %137, i64 %246
  %248 = load float, float* %247, align 4
  %249 = fmul reassoc ninf nsz float %110, %248
  %250 = fadd reassoc ninf nsz float %244, %239
  %251 = fadd reassoc ninf nsz float %250, %234
  %252 = fadd reassoc ninf nsz float %251, %249
  %253 = fmul reassoc ninf nsz float %252, %134
  %254 = fadd reassoc ninf nsz float %229, %253
  %255 = load float*, float** %43, align 8
  %256 = load i32, i32* %44, align 4
  %257 = sub i32 %256, %53
  %258 = mul i32 %257, %62
  %259 = add i32 %.017, %258
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, float* %255, i64 %260
  store float %254, float* %261, align 4
  %262 = add nsw i32 %.017, 1
  %exitcond.not = icmp eq i32 %19, %262
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.48, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.48**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.48*, %struct.RuntimeContext.48** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.48*, i8*, i32)*, void (%struct.RuntimeContext.48*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.48*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.48*, i8*)*, void (%struct.RuntimeContext.48*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.48* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.48* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.48, %struct.RuntimeContext.48* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.48* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.48*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.48* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
declare <2 x i32> @llvm.smax.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x i32> @llvm.smin.v2i32(<2 x i32>, <2 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #7

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
