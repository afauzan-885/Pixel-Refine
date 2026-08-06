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
define void @_bgr2lab_kernel_c352_0_kernel_0_serial(%struct.RuntimeContext.48* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.48* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 3
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
define void @_bgr2lab_kernel_c352_0_kernel_1_range_for(%struct.RuntimeContext.48* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.48* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 2
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %161, %for_loop_body ]
  %29 = load %struct.LLVMRuntime.47*, %struct.LLVMRuntime.47** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime.47, %struct.LLVMRuntime.47* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.05, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.05
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.05, 0
  %40 = icmp ne i32 %.05, %36
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg4 = sext i1 %42 to i32
  %43 = add i32 %35, %.neg4
  %44 = load float*, float** %23, align 8
  %45 = load i32, i32* %24, align 4
  %46 = load i32, i32* %25, align 4
  %47 = sub i32 %45, %34
  %48 = mul i32 %47, %43
  %49 = add i32 %.05, %48
  %50 = mul i32 %49, %46
  %51 = sext i32 %50 to i64
  %52 = getelementptr float, float* %44, i64 %51
  %53 = load float, float* %52, align 4
  %54 = fmul reassoc ninf nsz float %53, 0x3F70101020000000
  %55 = fcmp reassoc ninf nsz ogt float %54, 0x3FA4B5DCC0000000
  %56 = fmul reassoc ninf nsz float %53, 0x3F6E736160000000
  %57 = fadd reassoc ninf nsz float %56, 0x3FAAB12340000000
  %58 = fmul reassoc ninf nsz float %53, 0x3F33E45660000000
  %59 = insertelement <2 x i32> poison, i32 %50, i64 0
  %60 = shufflevector <2 x i32> %59, <2 x i32> poison, <2 x i32> zeroinitializer
  %61 = add <2 x i32> %60, <i32 2, i32 1>
  %62 = sext <2 x i32> %61 to <2 x i64>
  %63 = insertelement <2 x float*> poison, float* %44, i64 0
  %64 = shufflevector <2 x float*> %63, <2 x float*> poison, <2 x i32> zeroinitializer
  %65 = getelementptr float, <2 x float*> %64, <2 x i64> %62
  %66 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %65, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %67 = fmul reassoc ninf nsz <2 x float> %66, <float 0x3F70101020000000, float 0x3F70101020000000>
  %68 = extractelement <2 x float> %66, i64 0
  %69 = fmul reassoc ninf nsz float %68, 0x3F6E736160000000
  %70 = fadd reassoc ninf nsz float %69, 0x3FAAB12340000000
  %71 = tail call float @powf(float noundef %70, float noundef 0x4003333340000000) #1
  %72 = fcmp reassoc ninf nsz ogt <2 x float> %67, <float 0x3FA4B5DCC0000000, float 0x3FA4B5DCC0000000>
  %73 = extractelement <2 x float> %66, i64 1
  %74 = fmul reassoc ninf nsz float %73, 0x3F6E736160000000
  %75 = fadd reassoc ninf nsz float %74, 0x3FAAB12340000000
  %76 = tail call float @powf(float noundef %75, float noundef 0x4003333340000000) #1
  %77 = fmul reassoc ninf nsz <2 x float> %66, <float 0x3F33E45660000000, float 0x3F33E45660000000>
  %78 = insertelement <2 x float> poison, float %71, i64 0
  %79 = insertelement <2 x float> %78, float %76, i64 1
  %80 = select <2 x i1> %72, <2 x float> %79, <2 x float> %77
  %81 = tail call float @powf(float noundef %57, float noundef 0x4003333340000000) #1
  %82 = select reassoc ninf nsz i1 %55, float %81, float %58
  %83 = fmul reassoc ninf nsz <2 x float> %80, <float 0x3FDA65AF80000000, float 0x3FD6E286E0000000>
  %shift = shufflevector <2 x float> %83, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %84 = fadd reassoc ninf nsz <2 x float> %83, %shift
  %85 = extractelement <2 x float> %84, i64 0
  %86 = fmul reassoc ninf nsz float %82, 0x3FC7189380000000
  %87 = fadd reassoc ninf nsz float %85, %86
  %88 = fmul reassoc ninf nsz <2 x float> %80, <float 0x3FCB38DDA0000000, float 0x3FE6E286E0000000>
  %shift6 = shufflevector <2 x float> %88, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %89 = fadd reassoc ninf nsz <2 x float> %88, %shift6
  %90 = extractelement <2 x float> %89, i64 0
  %91 = fmul reassoc ninf nsz float %82, 0x3FB27A0FA0000000
  %92 = fadd reassoc ninf nsz float %90, %91
  %93 = fmul reassoc ninf nsz <2 x float> %80, <float 0x3F93CC4420000000, float 0x3FBE835DE0000000>
  %shift7 = shufflevector <2 x float> %93, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %94 = fadd reassoc ninf nsz <2 x float> %93, %shift7
  %95 = extractelement <2 x float> %94, i64 0
  %96 = fmul reassoc ninf nsz float %82, 0x3FEE68E420000000
  %97 = fadd reassoc ninf nsz float %95, %96
  %98 = fmul reassoc ninf nsz float %87, 0x3FF0D57280000000
  %99 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %98, float 0x3DDB7CDFE0000000)
  %100 = tail call float @powf(float noundef %99, float noundef 0x3FD5555560000000) #1
  %101 = fmul reassoc ninf nsz float %87, 0x402062B560000000
  %102 = fadd reassoc ninf nsz float %101, 0x3FC1A7B960000000
  %103 = fcmp reassoc ninf nsz ogt float %98, 0x3F82231840000000
  %104 = select reassoc ninf nsz i1 %103, float %100, float %102
  %105 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %92, float 0x3DDB7CDFE0000000)
  %106 = tail call float @powf(float noundef %105, float noundef 0x3FD5555560000000) #1
  %107 = fmul reassoc ninf nsz float %92, 0x401F25E360000000
  %108 = fadd reassoc ninf nsz float %107, 0x3FC1A7B960000000
  %109 = fcmp reassoc ninf nsz ogt float %92, 0x3F82231840000000
  %110 = select reassoc ninf nsz i1 %109, float %106, float %108
  %111 = fmul reassoc ninf nsz float %97, 0x3FED63AC20000000
  %112 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %111, float 0x3DDB7CDFE0000000)
  %113 = tail call float @powf(float noundef %112, float noundef 0x3FD5555560000000) #1
  %114 = fmul reassoc ninf nsz float %97, 0x401C9B5AE0000000
  %115 = fadd reassoc ninf nsz float %114, 0x3FC1A7B960000000
  %116 = fcmp reassoc ninf nsz ogt float %111, 0x3F82231840000000
  %117 = select reassoc ninf nsz i1 %116, float %113, float %115
  %118 = fsub reassoc ninf nsz float %104, %110
  %119 = fmul reassoc ninf nsz float %118, 5.000000e+02
  %120 = fsub reassoc ninf nsz float %110, %117
  %121 = fmul reassoc ninf nsz float %120, 2.000000e+02
  %122 = fmul reassoc ninf nsz float %110, 0x40727CCCC0000000
  %123 = fadd reassoc ninf nsz float %122, 0xC044666660000000
  %124 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %123, float 0.000000e+00)
  %125 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %124, float 2.550000e+02)
  %126 = load float*, float** %26, align 8
  %127 = load i32, i32* %27, align 4
  %128 = load i32, i32* %28, align 4
  %129 = sub i32 %127, %34
  %130 = mul i32 %129, %43
  %131 = add i32 %.05, %130
  %132 = mul i32 %131, %128
  %133 = sext i32 %132 to i64
  %134 = getelementptr float, float* %126, i64 %133
  store float %125, float* %134, align 4
  %135 = fadd reassoc ninf nsz float %119, 1.280000e+02
  %136 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %135, float 0.000000e+00)
  %137 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %136, float 2.550000e+02)
  %138 = load float*, float** %26, align 8
  %139 = load i32, i32* %27, align 4
  %140 = load i32, i32* %28, align 4
  %141 = sub i32 %139, %34
  %142 = mul i32 %141, %43
  %143 = add i32 %.05, %142
  %144 = mul i32 %143, %140
  %145 = add i32 %144, 1
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, float* %138, i64 %146
  store float %137, float* %147, align 4
  %148 = fadd reassoc ninf nsz float %121, 1.280000e+02
  %149 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %148, float 0.000000e+00)
  %150 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %149, float 2.550000e+02)
  %151 = load float*, float** %26, align 8
  %152 = load i32, i32* %27, align 4
  %153 = load i32, i32* %28, align 4
  %154 = sub i32 %152, %34
  %155 = mul i32 %154, %43
  %156 = add i32 %.05, %155
  %157 = mul i32 %156, %153
  %158 = add i32 %157, 2
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %151, i64 %159
  store float %150, float* %160, align 4
  %161 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %161
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @powf(float noundef, float noundef) local_unnamed_addr #4

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #5 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }
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
