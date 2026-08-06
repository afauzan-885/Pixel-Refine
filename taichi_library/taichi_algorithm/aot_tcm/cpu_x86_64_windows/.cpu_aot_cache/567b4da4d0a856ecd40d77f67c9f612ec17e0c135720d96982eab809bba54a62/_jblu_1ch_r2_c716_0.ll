; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.108*, void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*, i32)*, void (%struct.RuntimeContext.108*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.108 = type { i8*, %struct.LLVMRuntime.107*, i32, i64* }
%struct.LLVMRuntime.107 = type { %struct.PreallocatedMemoryChunk.103, %struct.PreallocatedMemoryChunk.103, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.104*], [1024 x %struct.NodeManager.105*], [1024 x i8*], i8*, %struct.RandState.106*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.103 = type { i8*, i8*, i64 }
%struct.ListManager.104 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.107* }
%struct.NodeManager.105 = type { %struct.LLVMRuntime.107*, i32, i32, i32, i32, %struct.ListManager.104*, %struct.ListManager.104*, %struct.ListManager.104*, i32 }
%struct.RandState.106 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_jblu_1ch_r2_c716_0_kernel_0_serial(%struct.RuntimeContext.108* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.108* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %1, i64 0, i32 5
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %11, i64 0, i32 6
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_jblu_1ch_r2_c716_0_kernel_1_range_for(%struct.RuntimeContext.108* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.108* %context, %struct.RuntimeContext.108** %4, align 8
  store void (%struct.RuntimeContext.108*, i8*)* null, void (%struct.RuntimeContext.108*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.108*, i8*, i32)* @function_body, void (%struct.RuntimeContext.108*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.108*, i8*)* null, void (%struct.RuntimeContext.108*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.108* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.108* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 3
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 4
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 7
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 8
  %29 = load float, float* %28, align 4
  %30 = sitofp i32 %23 to float
  %31 = sitofp i32 %25 to float
  %32 = add i32 %23, -1
  %33 = add i32 %25, -1
  %34 = fmul reassoc ninf nsz float %27, -8.000000e+00
  %35 = fmul reassoc ninf nsz float %27, -5.000000e+00
  %36 = fmul reassoc ninf nsz float %27, -4.000000e+00
  %37 = fmul reassoc ninf nsz float %27, -2.000000e+00
  %38 = fneg reassoc ninf nsz float %27
  %39 = icmp slt i32 %17, %19
  br i1 %39, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %40 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %42 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %44 = fneg reassoc ninf nsz float %29
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %46 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %745, %for_loop_body ]
  %47 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %3, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %47, i64 0, i32 14
  %49 = load i8*, i8** %48, align 8
  %50 = getelementptr inbounds i8, i8* %49, i64 4
  %51 = bitcast i8* %50 to i32*
  %52 = load i32, i32* %51, align 4
  %53 = sdiv i32 %.05, %52
  %54 = mul i32 %53, %52
  %55 = xor i32 %52, %.05
  %56 = icmp slt i32 %55, 0
  %57 = icmp ne i32 %.05, 0
  %58 = icmp ne i32 %.05, %54
  %59 = and i1 %57, %56
  %60 = and i1 %59, %58
  %.neg4 = sext i1 %60 to i32
  %61 = add i32 %53, %.neg4
  %62 = mul i32 %52, -1
  %63 = mul i32 %62, %61
  %64 = add i32 %.05, %63
  %65 = sitofp i32 %61 to float
  %66 = fmul reassoc ninf nsz float %65, %30
  %67 = getelementptr inbounds i8, i8* %49, i64 8
  %68 = bitcast i8* %67 to i32*
  %69 = load i32, i32* %68, align 4
  %70 = sitofp i32 %69 to float
  %71 = fdiv reassoc ninf nsz float %66, %70
  %72 = tail call reassoc ninf nsz float @llvm.floor.f32(float %71)
  %73 = fptosi float %72 to i32
  %74 = sitofp i32 %64 to float
  %75 = fmul reassoc ninf nsz float %74, %31
  %76 = getelementptr inbounds i8, i8* %49, i64 12
  %77 = bitcast i8* %76 to i32*
  %78 = load i32, i32* %77, align 4
  %79 = sitofp i32 %78 to float
  %80 = fdiv reassoc ninf nsz float %75, %79
  %81 = tail call reassoc ninf nsz float @llvm.floor.f32(float %80)
  %82 = fptosi float %81 to i32
  %83 = load float*, float** %40, align 8
  %84 = load i32, i32* %41, align 4
  %85 = sub i32 %84, %52
  %86 = mul i32 %85, %61
  %87 = add i32 %.05, %86
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, float* %83, i64 %88
  %90 = load float, float* %89, align 4
  %91 = add i32 %73, -2
  %92 = tail call i32 @llvm.smax.i32(i32 %91, i32 0)
  %93 = tail call i32 @llvm.smin.i32(i32 %32, i32 %92)
  %94 = add i32 %82, -2
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %33, i32 %95)
  %97 = sitofp i32 %93 to float
  %98 = fmul reassoc ninf nsz float %97, %70
  %99 = fdiv reassoc ninf nsz float %98, %30
  %100 = fadd reassoc ninf nsz float %99, 5.000000e-01
  %101 = fptosi float %100 to i32
  %102 = add i32 %69, -1
  %103 = tail call i32 @llvm.smax.i32(i32 %101, i32 0)
  %104 = tail call i32 @llvm.smin.i32(i32 %102, i32 %103)
  %105 = sitofp i32 %96 to float
  %106 = fmul reassoc ninf nsz float %105, %79
  %107 = fdiv reassoc ninf nsz float %106, %31
  %108 = fadd reassoc ninf nsz float %107, 5.000000e-01
  %109 = fptosi float %108 to i32
  %110 = add i32 %78, -1
  %111 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %112 = tail call i32 @llvm.smin.i32(i32 %110, i32 %111)
  %113 = mul i32 %104, %84
  %114 = add i32 %112, %113
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, float* %83, i64 %115
  %117 = load float, float* %116, align 4
  %118 = fsub reassoc ninf nsz float %117, %90
  %119 = fmul reassoc ninf nsz float %118, %118
  %120 = fmul reassoc ninf nsz float %119, %29
  %121 = fsub reassoc ninf nsz float %34, %120
  %122 = tail call float @expf(float noundef %121) #1
  %123 = load float*, float** %42, align 8
  %124 = load i32, i32* %43, align 4
  %125 = mul i32 %93, %124
  %126 = add i32 %96, %125
  %127 = sext i32 %126 to i64
  %128 = getelementptr float, float* %123, i64 %127
  %129 = load float, float* %128, align 4
  %130 = fmul reassoc ninf nsz float %129, %122
  %131 = fadd reassoc ninf nsz float %122, 0x3D71979980000000
  %132 = add i32 %82, -1
  %133 = tail call i32 @llvm.smax.i32(i32 %132, i32 0)
  %134 = tail call i32 @llvm.smin.i32(i32 %33, i32 %133)
  %135 = sitofp i32 %134 to float
  %136 = fmul reassoc ninf nsz float %135, %79
  %137 = fdiv reassoc ninf nsz float %136, %31
  %138 = fadd reassoc ninf nsz float %137, 5.000000e-01
  %139 = fptosi float %138 to i32
  %140 = tail call i32 @llvm.smax.i32(i32 %139, i32 0)
  %141 = tail call i32 @llvm.smin.i32(i32 %110, i32 %140)
  %142 = load float*, float** %40, align 8
  %143 = load i32, i32* %41, align 4
  %144 = mul i32 %104, %143
  %145 = add i32 %141, %144
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, float* %142, i64 %146
  %148 = load float, float* %147, align 4
  %149 = fsub reassoc ninf nsz float %148, %90
  %150 = fmul reassoc ninf nsz float %149, %149
  %151 = fmul reassoc ninf nsz float %150, %29
  %152 = fsub reassoc ninf nsz float %35, %151
  %153 = tail call float @expf(float noundef %152) #1
  %154 = load float*, float** %42, align 8
  %155 = load i32, i32* %43, align 4
  %156 = mul i32 %155, %93
  %157 = add i32 %156, %134
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, float* %154, i64 %158
  %160 = load float, float* %159, align 4
  %161 = fmul reassoc ninf nsz float %160, %153
  %162 = fadd reassoc ninf nsz float %161, %130
  %163 = fadd reassoc ninf nsz float %131, %153
  %164 = tail call i32 @llvm.smax.i32(i32 %82, i32 0)
  %165 = tail call i32 @llvm.smin.i32(i32 %33, i32 %164)
  %166 = sitofp i32 %165 to float
  %167 = fmul reassoc ninf nsz float %166, %79
  %168 = fdiv reassoc ninf nsz float %167, %31
  %169 = fadd reassoc ninf nsz float %168, 5.000000e-01
  %170 = fptosi float %169 to i32
  %171 = tail call i32 @llvm.smax.i32(i32 %170, i32 0)
  %172 = tail call i32 @llvm.smin.i32(i32 %110, i32 %171)
  %173 = load float*, float** %40, align 8
  %174 = load i32, i32* %41, align 4
  %175 = mul i32 %104, %174
  %176 = add i32 %175, %172
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, float* %173, i64 %177
  %179 = load float, float* %178, align 4
  %180 = fsub reassoc ninf nsz float %179, %90
  %181 = fmul reassoc ninf nsz float %180, %180
  %182 = fmul reassoc ninf nsz float %181, %29
  %183 = fsub reassoc ninf nsz float %36, %182
  %184 = tail call float @expf(float noundef %183) #1
  %185 = load float*, float** %42, align 8
  %186 = load i32, i32* %43, align 4
  %187 = mul i32 %186, %93
  %188 = add i32 %187, %165
  %189 = sext i32 %188 to i64
  %190 = getelementptr float, float* %185, i64 %189
  %191 = load float, float* %190, align 4
  %192 = fmul reassoc ninf nsz float %191, %184
  %193 = fadd reassoc ninf nsz float %162, %192
  %194 = fadd reassoc ninf nsz float %163, %184
  %195 = add i32 %82, 1
  %196 = tail call i32 @llvm.smax.i32(i32 %195, i32 0)
  %197 = tail call i32 @llvm.smin.i32(i32 %33, i32 %196)
  %198 = sitofp i32 %197 to float
  %199 = fmul reassoc ninf nsz float %198, %79
  %200 = fdiv reassoc ninf nsz float %199, %31
  %201 = fadd reassoc ninf nsz float %200, 5.000000e-01
  %202 = fptosi float %201 to i32
  %203 = tail call i32 @llvm.smax.i32(i32 %202, i32 0)
  %204 = tail call i32 @llvm.smin.i32(i32 %110, i32 %203)
  %205 = load float*, float** %40, align 8
  %206 = load i32, i32* %41, align 4
  %207 = mul i32 %206, %104
  %208 = add i32 %207, %204
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %205, i64 %209
  %211 = load float, float* %210, align 4
  %212 = fsub reassoc ninf nsz float %211, %90
  %213 = fmul reassoc ninf nsz float %212, %212
  %214 = fmul reassoc ninf nsz float %213, %29
  %215 = fsub reassoc ninf nsz float %35, %214
  %216 = tail call float @expf(float noundef %215) #1
  %217 = load float*, float** %42, align 8
  %218 = load i32, i32* %43, align 4
  %219 = mul i32 %218, %93
  %220 = add i32 %219, %197
  %221 = sext i32 %220 to i64
  %222 = getelementptr float, float* %217, i64 %221
  %223 = load float, float* %222, align 4
  %224 = fmul reassoc ninf nsz float %223, %216
  %225 = fadd reassoc ninf nsz float %193, %224
  %226 = fadd reassoc ninf nsz float %194, %216
  %227 = add i32 %82, 2
  %228 = tail call i32 @llvm.smax.i32(i32 %227, i32 0)
  %229 = tail call i32 @llvm.smin.i32(i32 %33, i32 %228)
  %230 = sitofp i32 %229 to float
  %231 = fmul reassoc ninf nsz float %230, %79
  %232 = fdiv reassoc ninf nsz float %231, %31
  %233 = fadd reassoc ninf nsz float %232, 5.000000e-01
  %234 = fptosi float %233 to i32
  %235 = tail call i32 @llvm.smax.i32(i32 %234, i32 0)
  %236 = tail call i32 @llvm.smin.i32(i32 %110, i32 %235)
  %237 = load float*, float** %40, align 8
  %238 = load i32, i32* %41, align 4
  %239 = mul i32 %238, %104
  %240 = add i32 %239, %236
  %241 = sext i32 %240 to i64
  %242 = getelementptr float, float* %237, i64 %241
  %243 = load float, float* %242, align 4
  %244 = fsub reassoc ninf nsz float %243, %90
  %245 = fmul reassoc ninf nsz float %244, %244
  %246 = fmul reassoc ninf nsz float %245, %29
  %247 = fsub reassoc ninf nsz float %34, %246
  %248 = tail call float @expf(float noundef %247) #1
  %249 = load float*, float** %42, align 8
  %250 = load i32, i32* %43, align 4
  %251 = mul i32 %250, %93
  %252 = add i32 %251, %229
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, float* %249, i64 %253
  %255 = load float, float* %254, align 4
  %256 = fmul reassoc ninf nsz float %255, %248
  %257 = fadd reassoc ninf nsz float %225, %256
  %258 = fadd reassoc ninf nsz float %226, %248
  %259 = add i32 %73, -1
  %260 = tail call i32 @llvm.smax.i32(i32 %259, i32 0)
  %261 = tail call i32 @llvm.smin.i32(i32 %32, i32 %260)
  %262 = sitofp i32 %261 to float
  %263 = fmul reassoc ninf nsz float %262, %70
  %264 = fdiv reassoc ninf nsz float %263, %30
  %265 = fadd reassoc ninf nsz float %264, 5.000000e-01
  %266 = fptosi float %265 to i32
  %267 = tail call i32 @llvm.smax.i32(i32 %266, i32 0)
  %268 = tail call i32 @llvm.smin.i32(i32 %102, i32 %267)
  %269 = load float*, float** %40, align 8
  %270 = load i32, i32* %41, align 4
  %271 = mul i32 %270, %268
  %272 = add i32 %271, %112
  %273 = sext i32 %272 to i64
  %274 = getelementptr float, float* %269, i64 %273
  %275 = load float, float* %274, align 4
  %276 = fsub reassoc ninf nsz float %275, %90
  %277 = fmul reassoc ninf nsz float %276, %276
  %278 = fmul reassoc ninf nsz float %277, %29
  %279 = fsub reassoc ninf nsz float %35, %278
  %280 = tail call float @expf(float noundef %279) #1
  %281 = load float*, float** %42, align 8
  %282 = load i32, i32* %43, align 4
  %283 = mul i32 %282, %261
  %284 = add i32 %283, %96
  %285 = sext i32 %284 to i64
  %286 = getelementptr float, float* %281, i64 %285
  %287 = load float, float* %286, align 4
  %288 = fmul reassoc ninf nsz float %287, %280
  %289 = fadd reassoc ninf nsz float %257, %288
  %290 = fadd reassoc ninf nsz float %258, %280
  %291 = load float*, float** %40, align 8
  %292 = load i32, i32* %41, align 4
  %293 = mul i32 %292, %268
  %294 = add i32 %293, %141
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, float* %291, i64 %295
  %297 = load float, float* %296, align 4
  %298 = fsub reassoc ninf nsz float %297, %90
  %299 = fmul reassoc ninf nsz float %298, %298
  %300 = fmul reassoc ninf nsz float %299, %29
  %301 = fsub reassoc ninf nsz float %37, %300
  %302 = tail call float @expf(float noundef %301) #1
  %303 = load float*, float** %42, align 8
  %304 = load i32, i32* %43, align 4
  %305 = mul i32 %304, %261
  %306 = add i32 %305, %134
  %307 = sext i32 %306 to i64
  %308 = getelementptr float, float* %303, i64 %307
  %309 = load float, float* %308, align 4
  %310 = fmul reassoc ninf nsz float %309, %302
  %311 = fadd reassoc ninf nsz float %289, %310
  %312 = fadd reassoc ninf nsz float %290, %302
  %313 = load float*, float** %40, align 8
  %314 = load i32, i32* %41, align 4
  %315 = mul i32 %314, %268
  %316 = add i32 %315, %172
  %317 = sext i32 %316 to i64
  %318 = getelementptr float, float* %313, i64 %317
  %319 = load float, float* %318, align 4
  %320 = fsub reassoc ninf nsz float %319, %90
  %321 = fmul reassoc ninf nsz float %320, %320
  %322 = fmul reassoc ninf nsz float %321, %29
  %323 = fsub reassoc ninf nsz float %38, %322
  %324 = tail call float @expf(float noundef %323) #1
  %325 = load float*, float** %42, align 8
  %326 = load i32, i32* %43, align 4
  %327 = mul i32 %326, %261
  %328 = add i32 %327, %165
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, float* %325, i64 %329
  %331 = load float, float* %330, align 4
  %332 = fmul reassoc ninf nsz float %331, %324
  %333 = fadd reassoc ninf nsz float %311, %332
  %334 = fadd reassoc ninf nsz float %312, %324
  %335 = load float*, float** %40, align 8
  %336 = load i32, i32* %41, align 4
  %337 = mul i32 %336, %268
  %338 = add i32 %337, %204
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, float* %335, i64 %339
  %341 = load float, float* %340, align 4
  %342 = fsub reassoc ninf nsz float %341, %90
  %343 = fmul reassoc ninf nsz float %342, %342
  %344 = fmul reassoc ninf nsz float %343, %29
  %345 = fsub reassoc ninf nsz float %37, %344
  %346 = tail call float @expf(float noundef %345) #1
  %347 = load float*, float** %42, align 8
  %348 = load i32, i32* %43, align 4
  %349 = mul i32 %348, %261
  %350 = add i32 %349, %197
  %351 = sext i32 %350 to i64
  %352 = getelementptr float, float* %347, i64 %351
  %353 = load float, float* %352, align 4
  %354 = fmul reassoc ninf nsz float %353, %346
  %355 = fadd reassoc ninf nsz float %333, %354
  %356 = fadd reassoc ninf nsz float %334, %346
  %357 = load float*, float** %40, align 8
  %358 = load i32, i32* %41, align 4
  %359 = mul i32 %358, %268
  %360 = add i32 %359, %236
  %361 = sext i32 %360 to i64
  %362 = getelementptr float, float* %357, i64 %361
  %363 = load float, float* %362, align 4
  %364 = fsub reassoc ninf nsz float %363, %90
  %365 = fmul reassoc ninf nsz float %364, %364
  %366 = fmul reassoc ninf nsz float %365, %29
  %367 = fsub reassoc ninf nsz float %35, %366
  %368 = tail call float @expf(float noundef %367) #1
  %369 = load float*, float** %42, align 8
  %370 = load i32, i32* %43, align 4
  %371 = mul i32 %370, %261
  %372 = add i32 %371, %229
  %373 = sext i32 %372 to i64
  %374 = getelementptr float, float* %369, i64 %373
  %375 = load float, float* %374, align 4
  %376 = fmul reassoc ninf nsz float %375, %368
  %377 = fadd reassoc ninf nsz float %355, %376
  %378 = fadd reassoc ninf nsz float %356, %368
  %379 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %380 = tail call i32 @llvm.smin.i32(i32 %32, i32 %379)
  %381 = sitofp i32 %380 to float
  %382 = fmul reassoc ninf nsz float %381, %70
  %383 = fdiv reassoc ninf nsz float %382, %30
  %384 = fadd reassoc ninf nsz float %383, 5.000000e-01
  %385 = fptosi float %384 to i32
  %386 = tail call i32 @llvm.smax.i32(i32 %385, i32 0)
  %387 = tail call i32 @llvm.smin.i32(i32 %102, i32 %386)
  %388 = load float*, float** %40, align 8
  %389 = load i32, i32* %41, align 4
  %390 = mul i32 %389, %387
  %391 = add i32 %390, %112
  %392 = sext i32 %391 to i64
  %393 = getelementptr float, float* %388, i64 %392
  %394 = load float, float* %393, align 4
  %395 = fsub reassoc ninf nsz float %394, %90
  %396 = fmul reassoc ninf nsz float %395, %395
  %397 = fmul reassoc ninf nsz float %396, %29
  %398 = fsub reassoc ninf nsz float %36, %397
  %399 = tail call float @expf(float noundef %398) #1
  %400 = load float*, float** %42, align 8
  %401 = load i32, i32* %43, align 4
  %402 = mul i32 %401, %380
  %403 = add i32 %402, %96
  %404 = sext i32 %403 to i64
  %405 = getelementptr float, float* %400, i64 %404
  %406 = load float, float* %405, align 4
  %407 = fmul reassoc ninf nsz float %406, %399
  %408 = fadd reassoc ninf nsz float %377, %407
  %409 = fadd reassoc ninf nsz float %378, %399
  %410 = load float*, float** %40, align 8
  %411 = load i32, i32* %41, align 4
  %412 = mul i32 %411, %387
  %413 = add i32 %412, %141
  %414 = sext i32 %413 to i64
  %415 = getelementptr float, float* %410, i64 %414
  %416 = load float, float* %415, align 4
  %417 = fsub reassoc ninf nsz float %416, %90
  %418 = fmul reassoc ninf nsz float %417, %417
  %419 = fmul reassoc ninf nsz float %418, %29
  %420 = fsub reassoc ninf nsz float %38, %419
  %421 = tail call float @expf(float noundef %420) #1
  %422 = load float*, float** %42, align 8
  %423 = load i32, i32* %43, align 4
  %424 = mul i32 %423, %380
  %425 = add i32 %424, %134
  %426 = sext i32 %425 to i64
  %427 = getelementptr float, float* %422, i64 %426
  %428 = load float, float* %427, align 4
  %429 = fmul reassoc ninf nsz float %428, %421
  %430 = fadd reassoc ninf nsz float %408, %429
  %431 = fadd reassoc ninf nsz float %409, %421
  %432 = load float*, float** %40, align 8
  %433 = load i32, i32* %41, align 4
  %434 = mul i32 %433, %387
  %435 = add i32 %434, %172
  %436 = sext i32 %435 to i64
  %437 = getelementptr float, float* %432, i64 %436
  %438 = load float, float* %437, align 4
  %439 = fsub reassoc ninf nsz float %438, %90
  %440 = fmul reassoc ninf nsz float %439, %439
  %441 = fmul reassoc ninf nsz float %440, %44
  %442 = tail call float @expf(float noundef %441) #1
  %443 = load float*, float** %42, align 8
  %444 = load i32, i32* %43, align 4
  %445 = mul i32 %444, %380
  %446 = add i32 %445, %165
  %447 = sext i32 %446 to i64
  %448 = getelementptr float, float* %443, i64 %447
  %449 = load float, float* %448, align 4
  %450 = fmul reassoc ninf nsz float %449, %442
  %451 = fadd reassoc ninf nsz float %430, %450
  %452 = fadd reassoc ninf nsz float %431, %442
  %453 = load float*, float** %40, align 8
  %454 = load i32, i32* %41, align 4
  %455 = mul i32 %454, %387
  %456 = add i32 %455, %204
  %457 = sext i32 %456 to i64
  %458 = getelementptr float, float* %453, i64 %457
  %459 = load float, float* %458, align 4
  %460 = fsub reassoc ninf nsz float %459, %90
  %461 = fmul reassoc ninf nsz float %460, %460
  %462 = fmul reassoc ninf nsz float %461, %29
  %463 = fsub reassoc ninf nsz float %38, %462
  %464 = tail call float @expf(float noundef %463) #1
  %465 = load float*, float** %42, align 8
  %466 = load i32, i32* %43, align 4
  %467 = mul i32 %466, %380
  %468 = add i32 %467, %197
  %469 = sext i32 %468 to i64
  %470 = getelementptr float, float* %465, i64 %469
  %471 = load float, float* %470, align 4
  %472 = fmul reassoc ninf nsz float %471, %464
  %473 = fadd reassoc ninf nsz float %451, %472
  %474 = fadd reassoc ninf nsz float %452, %464
  %475 = load float*, float** %40, align 8
  %476 = load i32, i32* %41, align 4
  %477 = mul i32 %476, %387
  %478 = add i32 %477, %236
  %479 = sext i32 %478 to i64
  %480 = getelementptr float, float* %475, i64 %479
  %481 = load float, float* %480, align 4
  %482 = fsub reassoc ninf nsz float %481, %90
  %483 = fmul reassoc ninf nsz float %482, %482
  %484 = fmul reassoc ninf nsz float %483, %29
  %485 = fsub reassoc ninf nsz float %36, %484
  %486 = tail call float @expf(float noundef %485) #1
  %487 = load float*, float** %42, align 8
  %488 = load i32, i32* %43, align 4
  %489 = mul i32 %488, %380
  %490 = add i32 %489, %229
  %491 = sext i32 %490 to i64
  %492 = getelementptr float, float* %487, i64 %491
  %493 = load float, float* %492, align 4
  %494 = fmul reassoc ninf nsz float %493, %486
  %495 = fadd reassoc ninf nsz float %473, %494
  %496 = fadd reassoc ninf nsz float %474, %486
  %497 = add i32 %73, 1
  %498 = tail call i32 @llvm.smax.i32(i32 %497, i32 0)
  %499 = tail call i32 @llvm.smin.i32(i32 %32, i32 %498)
  %500 = sitofp i32 %499 to float
  %501 = fmul reassoc ninf nsz float %500, %70
  %502 = fdiv reassoc ninf nsz float %501, %30
  %503 = fadd reassoc ninf nsz float %502, 5.000000e-01
  %504 = fptosi float %503 to i32
  %505 = tail call i32 @llvm.smax.i32(i32 %504, i32 0)
  %506 = tail call i32 @llvm.smin.i32(i32 %102, i32 %505)
  %507 = load float*, float** %40, align 8
  %508 = load i32, i32* %41, align 4
  %509 = mul i32 %508, %506
  %510 = add i32 %509, %112
  %511 = sext i32 %510 to i64
  %512 = getelementptr float, float* %507, i64 %511
  %513 = load float, float* %512, align 4
  %514 = fsub reassoc ninf nsz float %513, %90
  %515 = fmul reassoc ninf nsz float %514, %514
  %516 = fmul reassoc ninf nsz float %515, %29
  %517 = fsub reassoc ninf nsz float %35, %516
  %518 = tail call float @expf(float noundef %517) #1
  %519 = load float*, float** %42, align 8
  %520 = load i32, i32* %43, align 4
  %521 = mul i32 %520, %499
  %522 = add i32 %521, %96
  %523 = sext i32 %522 to i64
  %524 = getelementptr float, float* %519, i64 %523
  %525 = load float, float* %524, align 4
  %526 = fmul reassoc ninf nsz float %525, %518
  %527 = fadd reassoc ninf nsz float %495, %526
  %528 = fadd reassoc ninf nsz float %496, %518
  %529 = load float*, float** %40, align 8
  %530 = load i32, i32* %41, align 4
  %531 = mul i32 %530, %506
  %532 = add i32 %531, %141
  %533 = sext i32 %532 to i64
  %534 = getelementptr float, float* %529, i64 %533
  %535 = load float, float* %534, align 4
  %536 = fsub reassoc ninf nsz float %535, %90
  %537 = fmul reassoc ninf nsz float %536, %536
  %538 = fmul reassoc ninf nsz float %537, %29
  %539 = fsub reassoc ninf nsz float %37, %538
  %540 = tail call float @expf(float noundef %539) #1
  %541 = load float*, float** %42, align 8
  %542 = load i32, i32* %43, align 4
  %543 = mul i32 %542, %499
  %544 = add i32 %543, %134
  %545 = sext i32 %544 to i64
  %546 = getelementptr float, float* %541, i64 %545
  %547 = load float, float* %546, align 4
  %548 = fmul reassoc ninf nsz float %547, %540
  %549 = fadd reassoc ninf nsz float %527, %548
  %550 = fadd reassoc ninf nsz float %528, %540
  %551 = load float*, float** %40, align 8
  %552 = load i32, i32* %41, align 4
  %553 = mul i32 %552, %506
  %554 = add i32 %553, %172
  %555 = sext i32 %554 to i64
  %556 = getelementptr float, float* %551, i64 %555
  %557 = load float, float* %556, align 4
  %558 = fsub reassoc ninf nsz float %557, %90
  %559 = fmul reassoc ninf nsz float %558, %558
  %560 = fmul reassoc ninf nsz float %559, %29
  %561 = fsub reassoc ninf nsz float %38, %560
  %562 = tail call float @expf(float noundef %561) #1
  %563 = load float*, float** %42, align 8
  %564 = load i32, i32* %43, align 4
  %565 = mul i32 %564, %499
  %566 = add i32 %565, %165
  %567 = sext i32 %566 to i64
  %568 = getelementptr float, float* %563, i64 %567
  %569 = load float, float* %568, align 4
  %570 = fmul reassoc ninf nsz float %569, %562
  %571 = fadd reassoc ninf nsz float %549, %570
  %572 = fadd reassoc ninf nsz float %550, %562
  %573 = load float*, float** %40, align 8
  %574 = load i32, i32* %41, align 4
  %575 = mul i32 %574, %506
  %576 = add i32 %575, %204
  %577 = sext i32 %576 to i64
  %578 = getelementptr float, float* %573, i64 %577
  %579 = load float, float* %578, align 4
  %580 = fsub reassoc ninf nsz float %579, %90
  %581 = fmul reassoc ninf nsz float %580, %580
  %582 = fmul reassoc ninf nsz float %581, %29
  %583 = fsub reassoc ninf nsz float %37, %582
  %584 = tail call float @expf(float noundef %583) #1
  %585 = load float*, float** %42, align 8
  %586 = load i32, i32* %43, align 4
  %587 = mul i32 %586, %499
  %588 = add i32 %587, %197
  %589 = sext i32 %588 to i64
  %590 = getelementptr float, float* %585, i64 %589
  %591 = load float, float* %590, align 4
  %592 = fmul reassoc ninf nsz float %591, %584
  %593 = fadd reassoc ninf nsz float %571, %592
  %594 = fadd reassoc ninf nsz float %572, %584
  %595 = load float*, float** %40, align 8
  %596 = load i32, i32* %41, align 4
  %597 = mul i32 %596, %506
  %598 = add i32 %597, %236
  %599 = sext i32 %598 to i64
  %600 = getelementptr float, float* %595, i64 %599
  %601 = load float, float* %600, align 4
  %602 = fsub reassoc ninf nsz float %601, %90
  %603 = fmul reassoc ninf nsz float %602, %602
  %604 = fmul reassoc ninf nsz float %603, %29
  %605 = fsub reassoc ninf nsz float %35, %604
  %606 = tail call float @expf(float noundef %605) #1
  %607 = load float*, float** %42, align 8
  %608 = load i32, i32* %43, align 4
  %609 = mul i32 %608, %499
  %610 = add i32 %609, %229
  %611 = sext i32 %610 to i64
  %612 = getelementptr float, float* %607, i64 %611
  %613 = load float, float* %612, align 4
  %614 = fmul reassoc ninf nsz float %613, %606
  %615 = fadd reassoc ninf nsz float %593, %614
  %616 = fadd reassoc ninf nsz float %594, %606
  %617 = add i32 %73, 2
  %618 = tail call i32 @llvm.smax.i32(i32 %617, i32 0)
  %619 = tail call i32 @llvm.smin.i32(i32 %32, i32 %618)
  %620 = sitofp i32 %619 to float
  %621 = fmul reassoc ninf nsz float %620, %70
  %622 = fdiv reassoc ninf nsz float %621, %30
  %623 = fadd reassoc ninf nsz float %622, 5.000000e-01
  %624 = fptosi float %623 to i32
  %625 = tail call i32 @llvm.smax.i32(i32 %624, i32 0)
  %626 = tail call i32 @llvm.smin.i32(i32 %102, i32 %625)
  %627 = load float*, float** %40, align 8
  %628 = load i32, i32* %41, align 4
  %629 = mul i32 %628, %626
  %630 = add i32 %629, %112
  %631 = sext i32 %630 to i64
  %632 = getelementptr float, float* %627, i64 %631
  %633 = load float, float* %632, align 4
  %634 = fsub reassoc ninf nsz float %633, %90
  %635 = fmul reassoc ninf nsz float %634, %634
  %636 = fmul reassoc ninf nsz float %635, %29
  %637 = fsub reassoc ninf nsz float %34, %636
  %638 = tail call float @expf(float noundef %637) #1
  %639 = load float*, float** %42, align 8
  %640 = load i32, i32* %43, align 4
  %641 = mul i32 %640, %619
  %642 = add i32 %641, %96
  %643 = sext i32 %642 to i64
  %644 = getelementptr float, float* %639, i64 %643
  %645 = load float, float* %644, align 4
  %646 = fmul reassoc ninf nsz float %645, %638
  %647 = fadd reassoc ninf nsz float %615, %646
  %648 = fadd reassoc ninf nsz float %616, %638
  %649 = load float*, float** %40, align 8
  %650 = load i32, i32* %41, align 4
  %651 = mul i32 %650, %626
  %652 = add i32 %651, %141
  %653 = sext i32 %652 to i64
  %654 = getelementptr float, float* %649, i64 %653
  %655 = load float, float* %654, align 4
  %656 = fsub reassoc ninf nsz float %655, %90
  %657 = fmul reassoc ninf nsz float %656, %656
  %658 = fmul reassoc ninf nsz float %657, %29
  %659 = fsub reassoc ninf nsz float %35, %658
  %660 = tail call float @expf(float noundef %659) #1
  %661 = load float*, float** %42, align 8
  %662 = load i32, i32* %43, align 4
  %663 = mul i32 %662, %619
  %664 = add i32 %663, %134
  %665 = sext i32 %664 to i64
  %666 = getelementptr float, float* %661, i64 %665
  %667 = load float, float* %666, align 4
  %668 = fmul reassoc ninf nsz float %667, %660
  %669 = fadd reassoc ninf nsz float %647, %668
  %670 = fadd reassoc ninf nsz float %648, %660
  %671 = load float*, float** %40, align 8
  %672 = load i32, i32* %41, align 4
  %673 = mul i32 %672, %626
  %674 = add i32 %673, %172
  %675 = sext i32 %674 to i64
  %676 = getelementptr float, float* %671, i64 %675
  %677 = load float, float* %676, align 4
  %678 = fsub reassoc ninf nsz float %677, %90
  %679 = fmul reassoc ninf nsz float %678, %678
  %680 = fmul reassoc ninf nsz float %679, %29
  %681 = fsub reassoc ninf nsz float %36, %680
  %682 = tail call float @expf(float noundef %681) #1
  %683 = load float*, float** %42, align 8
  %684 = load i32, i32* %43, align 4
  %685 = mul i32 %684, %619
  %686 = add i32 %685, %165
  %687 = sext i32 %686 to i64
  %688 = getelementptr float, float* %683, i64 %687
  %689 = load float, float* %688, align 4
  %690 = fmul reassoc ninf nsz float %689, %682
  %691 = fadd reassoc ninf nsz float %669, %690
  %692 = fadd reassoc ninf nsz float %670, %682
  %693 = load float*, float** %40, align 8
  %694 = load i32, i32* %41, align 4
  %695 = mul i32 %694, %626
  %696 = add i32 %695, %204
  %697 = sext i32 %696 to i64
  %698 = getelementptr float, float* %693, i64 %697
  %699 = load float, float* %698, align 4
  %700 = fsub reassoc ninf nsz float %699, %90
  %701 = fmul reassoc ninf nsz float %700, %700
  %702 = fmul reassoc ninf nsz float %701, %29
  %703 = fsub reassoc ninf nsz float %35, %702
  %704 = tail call float @expf(float noundef %703) #1
  %705 = load float*, float** %42, align 8
  %706 = load i32, i32* %43, align 4
  %707 = mul i32 %706, %619
  %708 = add i32 %707, %197
  %709 = sext i32 %708 to i64
  %710 = getelementptr float, float* %705, i64 %709
  %711 = load float, float* %710, align 4
  %712 = fmul reassoc ninf nsz float %711, %704
  %713 = fadd reassoc ninf nsz float %691, %712
  %714 = fadd reassoc ninf nsz float %692, %704
  %715 = load float*, float** %40, align 8
  %716 = load i32, i32* %41, align 4
  %717 = mul i32 %716, %626
  %718 = add i32 %717, %236
  %719 = sext i32 %718 to i64
  %720 = getelementptr float, float* %715, i64 %719
  %721 = load float, float* %720, align 4
  %722 = fsub reassoc ninf nsz float %721, %90
  %723 = fmul reassoc ninf nsz float %722, %722
  %724 = fmul reassoc ninf nsz float %723, %29
  %725 = fsub reassoc ninf nsz float %34, %724
  %726 = tail call float @expf(float noundef %725) #1
  %727 = load float*, float** %42, align 8
  %728 = load i32, i32* %43, align 4
  %729 = mul i32 %728, %619
  %730 = add i32 %729, %229
  %731 = sext i32 %730 to i64
  %732 = getelementptr float, float* %727, i64 %731
  %733 = load float, float* %732, align 4
  %734 = fmul reassoc ninf nsz float %733, %726
  %735 = fadd reassoc ninf nsz float %713, %734
  %736 = fadd reassoc ninf nsz float %714, %726
  %737 = fdiv reassoc ninf nsz float %735, %736
  %738 = load float*, float** %45, align 8
  %739 = load i32, i32* %46, align 4
  %740 = sub i32 %739, %52
  %741 = mul i32 %740, %61
  %742 = add i32 %.05, %741
  %743 = sext i32 %742 to i64
  %744 = getelementptr float, float* %738, i64 %743
  store float %737, float* %744, align 4
  %745 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %745
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @expf(float noundef) local_unnamed_addr #4

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #5 {
  %4 = alloca %struct.RuntimeContext.108, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.108**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.108*, %struct.RuntimeContext.108** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.108*, i8*, i32)*, void (%struct.RuntimeContext.108*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.108*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.108* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.108* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.108* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.108* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.108* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.108*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.108* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #7 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
