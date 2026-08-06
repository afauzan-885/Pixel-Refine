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

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_bicubic_sample_kernel_2d_c150_0_kernel_0_serial(%struct.RuntimeContext.24* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.24* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.24, %struct.RuntimeContext.24* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.23*, %struct.LLVMRuntime.23** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.23, %struct.LLVMRuntime.23* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  store i32 %3, i32* %8, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bicubic_sample_kernel_2d_c150_0_kernel_1_range_for(%struct.RuntimeContext.24* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.24* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 4
  %23 = load i32, i32* %22, align 4
  %24 = add i32 %23, -1
  %25 = icmp slt i32 %17, %19
  br i1 %25, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 5
  %27 = load i32, i32* %26, align 4
  %28 = add i32 %27, -1
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %34 = sext i32 %17 to i64
  %wide.trip.count = sext i32 %19 to i64
  %35 = insertelement <4 x i32> poison, i32 %28, i64 0
  %shuffle51 = shufflevector <4 x i32> %35, <4 x i32> poison, <4 x i32> zeroinitializer
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %indvars.iv = phi i64 [ %34, %for_loop_body.lr.ph ], [ %indvars.iv.next, %for_loop_body ]
  %lsr55 = trunc i64 %indvars.iv to i32
  %36 = load float*, float** %29, align 8
  %37 = load i32, i32* %30, align 4
  %38 = mul i32 %37, %lsr55
  %39 = sext i32 %38 to i64
  %40 = getelementptr float, float* %36, i64 %39
  %41 = load float, float* %40, align 4
  %42 = add i32 %38, 1
  %43 = sext i32 %42 to i64
  %44 = getelementptr float, float* %36, i64 %43
  %45 = load float, float* %44, align 4
  %46 = tail call reassoc ninf nsz float @llvm.floor.f32(float %41)
  %47 = fptosi float %46 to i32
  %48 = tail call reassoc ninf nsz float @llvm.floor.f32(float %45)
  %49 = fptosi float %48 to i32
  %50 = sitofp i32 %47 to float
  %51 = fsub reassoc ninf nsz float %41, %50
  %52 = sitofp i32 %49 to float
  %53 = load float*, float** %31, align 8
  %54 = load i32, i32* %32, align 4
  %55 = add i32 %47, -1
  %56 = add i32 %49, -1
  %57 = tail call i32 @llvm.smax.i32(i32 %56, i32 0)
  %58 = tail call i32 @llvm.smin.i32(i32 %24, i32 %57)
  %59 = mul i32 %54, %58
  %60 = add i32 %47, 1
  %61 = add i32 %47, 2
  %62 = insertelement <4 x i32> poison, i32 %55, i64 0
  %63 = insertelement <4 x i32> %62, i32 %47, i64 1
  %64 = insertelement <4 x i32> %63, i32 %60, i64 2
  %65 = insertelement <4 x i32> %64, i32 %61, i64 3
  %66 = call <4 x i32> @llvm.smax.v4i32(<4 x i32> %65, <4 x i32> zeroinitializer)
  %67 = call <4 x i32> @llvm.smin.v4i32(<4 x i32> %shuffle51, <4 x i32> %66)
  %68 = insertelement <4 x i32> poison, i32 %59, i64 0
  %shuffle = shufflevector <4 x i32> %68, <4 x i32> poison, <4 x i32> zeroinitializer
  %69 = add <4 x i32> %shuffle, %67
  %70 = sext <4 x i32> %69 to <4 x i64>
  %71 = extractelement <4 x i64> %70, i64 0
  %72 = getelementptr float, float* %53, i64 %71
  %73 = load float, float* %72, align 4
  %74 = extractelement <4 x i64> %70, i64 1
  %75 = getelementptr float, float* %53, i64 %74
  %76 = load float, float* %75, align 4
  %77 = extractelement <4 x i64> %70, i64 2
  %78 = getelementptr float, float* %53, i64 %77
  %79 = load float, float* %78, align 4
  %80 = extractelement <4 x i64> %70, i64 3
  %81 = getelementptr float, float* %53, i64 %80
  %82 = load float, float* %81, align 4
  %83 = fmul reassoc ninf nsz float %73, -5.000000e-01
  %84 = fmul reassoc ninf nsz float %82, 5.000000e-01
  %reass.add28 = fsub reassoc ninf nsz float %76, %79
  %reass.mul29 = fmul reassoc ninf nsz float %reass.add28, 1.500000e+00
  %85 = fadd reassoc ninf nsz float %84, %83
  %86 = fadd reassoc ninf nsz float %85, %reass.mul29
  %.neg21 = fmul reassoc ninf nsz float %76, -2.500000e+00
  %factor24 = fmul reassoc ninf nsz float %79, 2.000000e+00
  %87 = fadd reassoc ninf nsz float %.neg21, %73
  %88 = fmul reassoc ninf nsz float %79, 5.000000e-01
  %89 = fadd reassoc ninf nsz float %88, %83
  %90 = fmul reassoc ninf nsz float %86, %51
  %91 = fadd reassoc ninf nsz float %87, %factor24
  %92 = fsub reassoc ninf nsz float %91, %84
  %reass.add25 = fadd reassoc ninf nsz float %92, %90
  %reass.mul26 = fmul reassoc ninf nsz float %reass.add25, %51
  %reass.add30 = fadd reassoc ninf nsz float %89, %reass.mul26
  %reass.mul31 = fmul reassoc ninf nsz float %reass.add30, %51
  %93 = fadd reassoc ninf nsz float %reass.mul31, %76
  %94 = tail call i32 @llvm.smax.i32(i32 %49, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %24, i32 %94)
  %96 = mul i32 %54, %95
  %97 = insertelement <4 x i32> poison, i32 %96, i64 0
  %shuffle52 = shufflevector <4 x i32> %97, <4 x i32> poison, <4 x i32> zeroinitializer
  %98 = add <4 x i32> %shuffle52, %67
  %99 = extractelement <4 x i32> %98, i64 0
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %53, i64 %100
  %102 = load float, float* %101, align 4
  %103 = extractelement <4 x i32> %98, i64 1
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, float* %53, i64 %104
  %106 = load float, float* %105, align 4
  %107 = extractelement <4 x i32> %98, i64 2
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, float* %53, i64 %108
  %110 = load float, float* %109, align 4
  %111 = extractelement <4 x i32> %98, i64 3
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, float* %53, i64 %112
  %114 = load float, float* %113, align 4
  %115 = fmul reassoc ninf nsz float %102, -5.000000e-01
  %116 = fmul reassoc ninf nsz float %114, 5.000000e-01
  %reass.add28.1 = fsub reassoc ninf nsz float %106, %110
  %reass.mul29.1 = fmul reassoc ninf nsz float %reass.add28.1, 1.500000e+00
  %117 = fadd reassoc ninf nsz float %116, %115
  %118 = fadd reassoc ninf nsz float %117, %reass.mul29.1
  %.neg21.1 = fmul reassoc ninf nsz float %106, -2.500000e+00
  %factor24.1 = fmul reassoc ninf nsz float %110, 2.000000e+00
  %119 = fadd reassoc ninf nsz float %.neg21.1, %102
  %120 = fmul reassoc ninf nsz float %110, 5.000000e-01
  %121 = fadd reassoc ninf nsz float %120, %115
  %122 = fmul reassoc ninf nsz float %118, %51
  %123 = fadd reassoc ninf nsz float %119, %factor24.1
  %124 = fsub reassoc ninf nsz float %123, %116
  %reass.add25.1 = fadd reassoc ninf nsz float %124, %122
  %reass.mul26.1 = fmul reassoc ninf nsz float %reass.add25.1, %51
  %reass.add30.1 = fadd reassoc ninf nsz float %121, %reass.mul26.1
  %reass.mul31.1 = fmul reassoc ninf nsz float %reass.add30.1, %51
  %125 = fadd reassoc ninf nsz float %reass.mul31.1, %106
  %126 = add i32 %49, 1
  %127 = tail call i32 @llvm.smax.i32(i32 %126, i32 0)
  %128 = tail call i32 @llvm.smin.i32(i32 %24, i32 %127)
  %129 = mul i32 %54, %128
  %130 = insertelement <4 x i32> poison, i32 %129, i64 0
  %shuffle53 = shufflevector <4 x i32> %130, <4 x i32> poison, <4 x i32> zeroinitializer
  %131 = add <4 x i32> %shuffle53, %67
  %132 = extractelement <4 x i32> %131, i64 0
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %53, i64 %133
  %135 = load float, float* %134, align 4
  %136 = extractelement <4 x i32> %131, i64 1
  %137 = sext i32 %136 to i64
  %138 = getelementptr float, float* %53, i64 %137
  %139 = load float, float* %138, align 4
  %140 = extractelement <4 x i32> %131, i64 2
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %53, i64 %141
  %143 = load float, float* %142, align 4
  %144 = extractelement <4 x i32> %131, i64 3
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %53, i64 %145
  %147 = load float, float* %146, align 4
  %148 = fmul reassoc ninf nsz float %135, -5.000000e-01
  %149 = fmul reassoc ninf nsz float %147, 5.000000e-01
  %reass.add28.2 = fsub reassoc ninf nsz float %139, %143
  %reass.mul29.2 = fmul reassoc ninf nsz float %reass.add28.2, 1.500000e+00
  %150 = fadd reassoc ninf nsz float %149, %148
  %151 = fadd reassoc ninf nsz float %150, %reass.mul29.2
  %.neg21.2 = fmul reassoc ninf nsz float %139, -2.500000e+00
  %factor24.2 = fmul reassoc ninf nsz float %143, 2.000000e+00
  %152 = fadd reassoc ninf nsz float %.neg21.2, %135
  %153 = fmul reassoc ninf nsz float %143, 5.000000e-01
  %154 = fadd reassoc ninf nsz float %153, %148
  %155 = fmul reassoc ninf nsz float %151, %51
  %156 = fadd reassoc ninf nsz float %152, %factor24.2
  %157 = fsub reassoc ninf nsz float %156, %149
  %reass.add25.2 = fadd reassoc ninf nsz float %157, %155
  %reass.mul26.2 = fmul reassoc ninf nsz float %reass.add25.2, %51
  %reass.add30.2 = fadd reassoc ninf nsz float %154, %reass.mul26.2
  %reass.mul31.2 = fmul reassoc ninf nsz float %reass.add30.2, %51
  %158 = fadd reassoc ninf nsz float %reass.mul31.2, %139
  %159 = add i32 %49, 2
  %160 = tail call i32 @llvm.smax.i32(i32 %159, i32 0)
  %161 = tail call i32 @llvm.smin.i32(i32 %24, i32 %160)
  %162 = mul i32 %54, %161
  %163 = insertelement <4 x i32> poison, i32 %162, i64 0
  %shuffle54 = shufflevector <4 x i32> %163, <4 x i32> poison, <4 x i32> zeroinitializer
  %164 = add <4 x i32> %shuffle54, %67
  %165 = extractelement <4 x i32> %164, i64 0
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, float* %53, i64 %166
  %168 = load float, float* %167, align 4
  %169 = extractelement <4 x i32> %164, i64 1
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, float* %53, i64 %170
  %172 = load float, float* %171, align 4
  %173 = extractelement <4 x i32> %164, i64 2
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, float* %53, i64 %174
  %176 = load float, float* %175, align 4
  %177 = extractelement <4 x i32> %164, i64 3
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %53, i64 %178
  %180 = load float, float* %179, align 4
  %181 = fmul reassoc ninf nsz float %168, -5.000000e-01
  %182 = fmul reassoc ninf nsz float %180, 5.000000e-01
  %reass.add28.3 = fsub reassoc ninf nsz float %172, %176
  %reass.mul29.3 = fmul reassoc ninf nsz float %reass.add28.3, 1.500000e+00
  %183 = fadd reassoc ninf nsz float %182, %181
  %184 = fadd reassoc ninf nsz float %183, %reass.mul29.3
  %.neg21.3 = fmul reassoc ninf nsz float %172, -2.500000e+00
  %factor24.3 = fmul reassoc ninf nsz float %176, 2.000000e+00
  %185 = fadd reassoc ninf nsz float %.neg21.3, %168
  %186 = fmul reassoc ninf nsz float %176, 5.000000e-01
  %187 = fadd reassoc ninf nsz float %186, %181
  %188 = fmul reassoc ninf nsz float %184, %51
  %189 = fadd reassoc ninf nsz float %185, %factor24.3
  %190 = fsub reassoc ninf nsz float %189, %182
  %reass.add25.3 = fadd reassoc ninf nsz float %190, %188
  %reass.mul26.3 = fmul reassoc ninf nsz float %reass.add25.3, %51
  %reass.add30.3 = fadd reassoc ninf nsz float %187, %reass.mul26.3
  %reass.mul31.3 = fmul reassoc ninf nsz float %reass.add30.3, %51
  %191 = fadd reassoc ninf nsz float %reass.mul31.3, %172
  %192 = fsub reassoc ninf nsz float %45, %52
  %193 = fmul reassoc ninf nsz float %93, -5.000000e-01
  %194 = fmul reassoc ninf nsz float %191, 5.000000e-01
  %reass.add16 = fsub reassoc ninf nsz float %125, %158
  %reass.mul17 = fmul reassoc ninf nsz float %reass.add16, 1.500000e+00
  %195 = fadd reassoc ninf nsz float %194, %193
  %196 = fadd reassoc ninf nsz float %195, %reass.mul17
  %.neg13 = fmul reassoc ninf nsz float %125, -2.500000e+00
  %factor = fmul reassoc ninf nsz float %158, 2.000000e+00
  %197 = fadd reassoc ninf nsz float %.neg13, %93
  %198 = fmul reassoc ninf nsz float %158, 5.000000e-01
  %199 = fadd reassoc ninf nsz float %198, %193
  %200 = fmul reassoc ninf nsz float %196, %192
  %201 = fadd reassoc ninf nsz float %197, %factor
  %202 = fsub reassoc ninf nsz float %201, %194
  %reass.add = fadd reassoc ninf nsz float %202, %200
  %reass.mul = fmul reassoc ninf nsz float %reass.add, %192
  %reass.add18 = fadd reassoc ninf nsz float %199, %reass.mul
  %reass.mul19 = fmul reassoc ninf nsz float %reass.add18, %192
  %203 = fadd reassoc ninf nsz float %reass.mul19, %125
  %204 = load float*, float** %33, align 8
  %scevgep = getelementptr float, float* %204, i64 %indvars.iv
  store float %203, float* %scevgep, align 4
  %indvars.iv.next = add nsw i64 %indvars.iv, 1
  %exitcond.not = icmp eq i64 %wide.trip.count, %indvars.iv.next
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
declare <4 x i32> @llvm.smax.v4i32(<4 x i32>, <4 x i32>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <4 x i32> @llvm.smin.v4i32(<4 x i32>, <4 x i32>) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
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
