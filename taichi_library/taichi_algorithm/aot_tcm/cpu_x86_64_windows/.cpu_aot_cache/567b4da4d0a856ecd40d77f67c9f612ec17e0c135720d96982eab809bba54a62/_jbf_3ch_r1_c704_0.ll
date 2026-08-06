; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.36*, void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.36 = type { i8*, %struct.LLVMRuntime.35*, i32, i64* }
%struct.LLVMRuntime.35 = type { %struct.PreallocatedMemoryChunk.31, %struct.PreallocatedMemoryChunk.31, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.32*], [1024 x %struct.NodeManager.33*], [1024 x i8*], i8*, %struct.RandState.34*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.31 = type { i8*, i8*, i64 }
%struct.ListManager.32 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.35* }
%struct.NodeManager.33 = type { %struct.LLVMRuntime.35*, i32, i32, i32, i32, %struct.ListManager.32*, %struct.ListManager.32*, %struct.ListManager.32*, i32 }
%struct.RandState.34 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_jbf_3ch_r1_c704_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_jbf_3ch_r1_c704_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.36* %context, %struct.RuntimeContext.36** %4, align 8
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.36*, i8*, i32)* @function_body, void (%struct.RuntimeContext.36*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.36*, i8*)* null, void (%struct.RuntimeContext.36*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.36* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 5
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 6
  %25 = load float, float* %24, align 4
  %26 = fmul reassoc ninf nsz float %23, -2.000000e+00
  %27 = fneg reassoc ninf nsz float %23
  %28 = icmp slt i32 %17, %19
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %33 = fneg reassoc ninf nsz float %25
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %36 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %36, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %425, %for_loop_body ]
  %37 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %37, i64 0, i32 14
  %39 = load i8*, i8** %38, align 8
  %40 = getelementptr inbounds i8, i8* %39, i64 4
  %41 = bitcast i8* %40 to i32*
  %42 = load i32, i32* %41, align 4
  %43 = sdiv i32 %.05, %42
  %44 = mul i32 %43, %42
  %45 = xor i32 %42, %.05
  %46 = icmp slt i32 %45, 0
  %47 = icmp ne i32 %.05, 0
  %48 = icmp ne i32 %.05, %44
  %49 = and i1 %47, %46
  %50 = and i1 %49, %48
  %.neg4 = sext i1 %50 to i32
  %51 = add i32 %43, %.neg4
  %52 = mul i32 %42, -1
  %53 = mul i32 %52, %51
  %54 = add i32 %.05, %53
  %55 = load float*, float** %29, align 8
  %56 = load i32, i32* %30, align 4
  %57 = sub i32 %56, %42
  %58 = mul i32 %57, %51
  %59 = add i32 %.05, %58
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, float* %55, i64 %60
  %62 = load float, float* %61, align 4
  %63 = add i32 %51, -1
  %64 = getelementptr inbounds i8, i8* %39, i64 8
  %65 = bitcast i8* %64 to i32*
  %66 = load i32, i32* %65, align 4
  %67 = add i32 %66, -1
  %68 = tail call i32 @llvm.smax.i32(i32 %63, i32 0)
  %69 = tail call i32 @llvm.smin.i32(i32 %67, i32 %68)
  %70 = add i32 %54, -1
  %71 = getelementptr inbounds i8, i8* %39, i64 12
  %72 = bitcast i8* %71 to i32*
  %73 = load i32, i32* %72, align 4
  %74 = add i32 %73, -1
  %75 = tail call i32 @llvm.smax.i32(i32 %70, i32 0)
  %76 = tail call i32 @llvm.smin.i32(i32 %74, i32 %75)
  %77 = mul i32 %69, %56
  %78 = add i32 %76, %77
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, float* %55, i64 %79
  %81 = load float, float* %80, align 4
  %82 = fsub reassoc ninf nsz float %81, %62
  %83 = fmul reassoc ninf nsz float %82, %82
  %84 = fmul reassoc ninf nsz float %83, %25
  %85 = fsub reassoc ninf nsz float %26, %84
  %86 = tail call float @expf(float noundef %85) #1
  %87 = load float*, float** %31, align 8
  %88 = load i32, i32* %32, align 4
  %89 = mul i32 %88, %69
  %90 = add i32 %89, %76
  %91 = mul i32 %90, 3
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, float* %87, i64 %92
  %94 = load float, float* %93, align 4
  %95 = add i32 %91, 1
  %96 = sext i32 %95 to i64
  %97 = getelementptr float, float* %87, i64 %96
  %98 = load float, float* %97, align 4
  %99 = add i32 %91, 2
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %87, i64 %100
  %102 = load float, float* %101, align 4
  %103 = fmul reassoc ninf nsz float %94, %86
  %104 = fmul reassoc ninf nsz float %98, %86
  %105 = fmul reassoc ninf nsz float %102, %86
  %106 = fadd reassoc ninf nsz float %86, 0x3D71979980000000
  %107 = tail call i32 @llvm.smax.i32(i32 %54, i32 0)
  %108 = tail call i32 @llvm.smin.i32(i32 %74, i32 %107)
  %109 = load float*, float** %29, align 8
  %110 = load i32, i32* %30, align 4
  %111 = mul i32 %110, %69
  %112 = add i32 %111, %108
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %109, i64 %113
  %115 = load float, float* %114, align 4
  %116 = fsub reassoc ninf nsz float %115, %62
  %117 = fmul reassoc ninf nsz float %116, %116
  %118 = fmul reassoc ninf nsz float %117, %25
  %119 = fsub reassoc ninf nsz float %27, %118
  %120 = tail call float @expf(float noundef %119) #1
  %121 = load float*, float** %31, align 8
  %122 = load i32, i32* %32, align 4
  %123 = mul i32 %122, %69
  %124 = add i32 %123, %108
  %125 = mul i32 %124, 3
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, float* %121, i64 %126
  %128 = load float, float* %127, align 4
  %129 = add i32 %125, 1
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, float* %121, i64 %130
  %132 = load float, float* %131, align 4
  %133 = add i32 %125, 2
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %121, i64 %134
  %136 = load float, float* %135, align 4
  %137 = fmul reassoc ninf nsz float %128, %120
  %138 = fmul reassoc ninf nsz float %132, %120
  %139 = fmul reassoc ninf nsz float %136, %120
  %140 = fadd reassoc ninf nsz float %137, %103
  %141 = fadd reassoc ninf nsz float %138, %104
  %142 = fadd reassoc ninf nsz float %139, %105
  %143 = fadd reassoc ninf nsz float %106, %120
  %144 = add i32 %54, 1
  %145 = tail call i32 @llvm.smax.i32(i32 %144, i32 0)
  %146 = tail call i32 @llvm.smin.i32(i32 %74, i32 %145)
  %147 = load float*, float** %29, align 8
  %148 = load i32, i32* %30, align 4
  %149 = mul i32 %148, %69
  %150 = add i32 %149, %146
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %147, i64 %151
  %153 = load float, float* %152, align 4
  %154 = fsub reassoc ninf nsz float %153, %62
  %155 = fmul reassoc ninf nsz float %154, %154
  %156 = fmul reassoc ninf nsz float %155, %25
  %157 = fsub reassoc ninf nsz float %26, %156
  %158 = tail call float @expf(float noundef %157) #1
  %159 = load float*, float** %31, align 8
  %160 = load i32, i32* %32, align 4
  %161 = mul i32 %160, %69
  %162 = add i32 %161, %146
  %163 = mul i32 %162, 3
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %159, i64 %164
  %166 = load float, float* %165, align 4
  %167 = add i32 %163, 1
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, float* %159, i64 %168
  %170 = load float, float* %169, align 4
  %171 = add i32 %163, 2
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %159, i64 %172
  %174 = load float, float* %173, align 4
  %175 = fmul reassoc ninf nsz float %166, %158
  %176 = fmul reassoc ninf nsz float %170, %158
  %177 = fmul reassoc ninf nsz float %174, %158
  %178 = fadd reassoc ninf nsz float %140, %175
  %179 = fadd reassoc ninf nsz float %141, %176
  %180 = fadd reassoc ninf nsz float %142, %177
  %181 = fadd reassoc ninf nsz float %143, %158
  %182 = tail call i32 @llvm.smax.i32(i32 %51, i32 0)
  %183 = tail call i32 @llvm.smin.i32(i32 %67, i32 %182)
  %184 = load float*, float** %29, align 8
  %185 = load i32, i32* %30, align 4
  %186 = mul i32 %185, %183
  %187 = add i32 %186, %76
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, float* %184, i64 %188
  %190 = load float, float* %189, align 4
  %191 = fsub reassoc ninf nsz float %190, %62
  %192 = fmul reassoc ninf nsz float %191, %191
  %193 = fmul reassoc ninf nsz float %192, %25
  %194 = fsub reassoc ninf nsz float %27, %193
  %195 = tail call float @expf(float noundef %194) #1
  %196 = load float*, float** %31, align 8
  %197 = load i32, i32* %32, align 4
  %198 = mul i32 %197, %183
  %199 = add i32 %198, %76
  %200 = mul i32 %199, 3
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, float* %196, i64 %201
  %203 = load float, float* %202, align 4
  %204 = add i32 %200, 1
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %196, i64 %205
  %207 = load float, float* %206, align 4
  %208 = add i32 %200, 2
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %196, i64 %209
  %211 = load float, float* %210, align 4
  %212 = fmul reassoc ninf nsz float %203, %195
  %213 = fmul reassoc ninf nsz float %207, %195
  %214 = fmul reassoc ninf nsz float %211, %195
  %215 = fadd reassoc ninf nsz float %178, %212
  %216 = fadd reassoc ninf nsz float %179, %213
  %217 = fadd reassoc ninf nsz float %180, %214
  %218 = fadd reassoc ninf nsz float %181, %195
  %219 = load float*, float** %29, align 8
  %220 = load i32, i32* %30, align 4
  %221 = mul i32 %220, %183
  %222 = add i32 %221, %108
  %223 = sext i32 %222 to i64
  %224 = getelementptr float, float* %219, i64 %223
  %225 = load float, float* %224, align 4
  %226 = fsub reassoc ninf nsz float %225, %62
  %227 = fmul reassoc ninf nsz float %226, %226
  %228 = fmul reassoc ninf nsz float %227, %33
  %229 = tail call float @expf(float noundef %228) #1
  %230 = load float*, float** %31, align 8
  %231 = load i32, i32* %32, align 4
  %232 = mul i32 %231, %183
  %233 = add i32 %232, %108
  %234 = mul i32 %233, 3
  %235 = sext i32 %234 to i64
  %236 = getelementptr float, float* %230, i64 %235
  %237 = load float, float* %236, align 4
  %238 = add i32 %234, 1
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, float* %230, i64 %239
  %241 = load float, float* %240, align 4
  %242 = add i32 %234, 2
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, float* %230, i64 %243
  %245 = load float, float* %244, align 4
  %246 = fmul reassoc ninf nsz float %237, %229
  %247 = fmul reassoc ninf nsz float %241, %229
  %248 = fmul reassoc ninf nsz float %245, %229
  %249 = fadd reassoc ninf nsz float %215, %246
  %250 = fadd reassoc ninf nsz float %216, %247
  %251 = fadd reassoc ninf nsz float %217, %248
  %252 = fadd reassoc ninf nsz float %218, %229
  %253 = load float*, float** %29, align 8
  %254 = load i32, i32* %30, align 4
  %255 = mul i32 %254, %183
  %256 = add i32 %255, %146
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, float* %253, i64 %257
  %259 = load float, float* %258, align 4
  %260 = fsub reassoc ninf nsz float %259, %62
  %261 = fmul reassoc ninf nsz float %260, %260
  %262 = fmul reassoc ninf nsz float %261, %25
  %263 = fsub reassoc ninf nsz float %27, %262
  %264 = tail call float @expf(float noundef %263) #1
  %265 = load float*, float** %31, align 8
  %266 = load i32, i32* %32, align 4
  %267 = mul i32 %266, %183
  %268 = add i32 %267, %146
  %269 = mul i32 %268, 3
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, float* %265, i64 %270
  %272 = load float, float* %271, align 4
  %273 = add i32 %269, 1
  %274 = sext i32 %273 to i64
  %275 = getelementptr float, float* %265, i64 %274
  %276 = load float, float* %275, align 4
  %277 = add i32 %269, 2
  %278 = sext i32 %277 to i64
  %279 = getelementptr float, float* %265, i64 %278
  %280 = load float, float* %279, align 4
  %281 = fmul reassoc ninf nsz float %272, %264
  %282 = fmul reassoc ninf nsz float %276, %264
  %283 = fmul reassoc ninf nsz float %280, %264
  %284 = fadd reassoc ninf nsz float %249, %281
  %285 = fadd reassoc ninf nsz float %250, %282
  %286 = fadd reassoc ninf nsz float %251, %283
  %287 = fadd reassoc ninf nsz float %252, %264
  %288 = add i32 %51, 1
  %289 = tail call i32 @llvm.smax.i32(i32 %288, i32 0)
  %290 = tail call i32 @llvm.smin.i32(i32 %67, i32 %289)
  %291 = load float*, float** %29, align 8
  %292 = load i32, i32* %30, align 4
  %293 = mul i32 %292, %290
  %294 = add i32 %293, %76
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, float* %291, i64 %295
  %297 = load float, float* %296, align 4
  %298 = fsub reassoc ninf nsz float %297, %62
  %299 = fmul reassoc ninf nsz float %298, %298
  %300 = fmul reassoc ninf nsz float %299, %25
  %301 = fsub reassoc ninf nsz float %26, %300
  %302 = tail call float @expf(float noundef %301) #1
  %303 = load float*, float** %31, align 8
  %304 = load i32, i32* %32, align 4
  %305 = mul i32 %304, %290
  %306 = add i32 %305, %76
  %307 = mul i32 %306, 3
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, float* %303, i64 %308
  %310 = load float, float* %309, align 4
  %311 = add i32 %307, 1
  %312 = sext i32 %311 to i64
  %313 = getelementptr float, float* %303, i64 %312
  %314 = load float, float* %313, align 4
  %315 = add i32 %307, 2
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, float* %303, i64 %316
  %318 = load float, float* %317, align 4
  %319 = fmul reassoc ninf nsz float %310, %302
  %320 = fmul reassoc ninf nsz float %314, %302
  %321 = fmul reassoc ninf nsz float %318, %302
  %322 = fadd reassoc ninf nsz float %284, %319
  %323 = fadd reassoc ninf nsz float %285, %320
  %324 = fadd reassoc ninf nsz float %286, %321
  %325 = fadd reassoc ninf nsz float %287, %302
  %326 = load float*, float** %29, align 8
  %327 = load i32, i32* %30, align 4
  %328 = mul i32 %327, %290
  %329 = add i32 %328, %108
  %330 = sext i32 %329 to i64
  %331 = getelementptr float, float* %326, i64 %330
  %332 = load float, float* %331, align 4
  %333 = fsub reassoc ninf nsz float %332, %62
  %334 = fmul reassoc ninf nsz float %333, %333
  %335 = fmul reassoc ninf nsz float %334, %25
  %336 = fsub reassoc ninf nsz float %27, %335
  %337 = tail call float @expf(float noundef %336) #1
  %338 = load float*, float** %31, align 8
  %339 = load i32, i32* %32, align 4
  %340 = mul i32 %339, %290
  %341 = add i32 %340, %108
  %342 = mul i32 %341, 3
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, float* %338, i64 %343
  %345 = load float, float* %344, align 4
  %346 = add i32 %342, 1
  %347 = sext i32 %346 to i64
  %348 = getelementptr float, float* %338, i64 %347
  %349 = load float, float* %348, align 4
  %350 = add i32 %342, 2
  %351 = sext i32 %350 to i64
  %352 = getelementptr float, float* %338, i64 %351
  %353 = load float, float* %352, align 4
  %354 = fmul reassoc ninf nsz float %345, %337
  %355 = fmul reassoc ninf nsz float %349, %337
  %356 = fmul reassoc ninf nsz float %353, %337
  %357 = fadd reassoc ninf nsz float %322, %354
  %358 = fadd reassoc ninf nsz float %323, %355
  %359 = fadd reassoc ninf nsz float %324, %356
  %360 = fadd reassoc ninf nsz float %325, %337
  %361 = load float*, float** %29, align 8
  %362 = load i32, i32* %30, align 4
  %363 = mul i32 %362, %290
  %364 = add i32 %363, %146
  %365 = sext i32 %364 to i64
  %366 = getelementptr float, float* %361, i64 %365
  %367 = load float, float* %366, align 4
  %368 = fsub reassoc ninf nsz float %367, %62
  %369 = fmul reassoc ninf nsz float %368, %368
  %370 = fmul reassoc ninf nsz float %369, %25
  %371 = fsub reassoc ninf nsz float %26, %370
  %372 = tail call float @expf(float noundef %371) #1
  %373 = load float*, float** %31, align 8
  %374 = load i32, i32* %32, align 4
  %375 = mul i32 %374, %290
  %376 = add i32 %375, %146
  %377 = mul i32 %376, 3
  %378 = sext i32 %377 to i64
  %379 = getelementptr float, float* %373, i64 %378
  %380 = load float, float* %379, align 4
  %381 = add i32 %377, 1
  %382 = sext i32 %381 to i64
  %383 = getelementptr float, float* %373, i64 %382
  %384 = load float, float* %383, align 4
  %385 = add i32 %377, 2
  %386 = sext i32 %385 to i64
  %387 = getelementptr float, float* %373, i64 %386
  %388 = load float, float* %387, align 4
  %389 = fmul reassoc ninf nsz float %380, %372
  %390 = fmul reassoc ninf nsz float %384, %372
  %391 = fmul reassoc ninf nsz float %388, %372
  %392 = fadd reassoc ninf nsz float %357, %389
  %393 = fadd reassoc ninf nsz float %358, %390
  %394 = fadd reassoc ninf nsz float %359, %391
  %395 = fadd reassoc ninf nsz float %360, %372
  %396 = fdiv reassoc ninf nsz float %392, %395
  %397 = fdiv reassoc ninf nsz float %393, %395
  %398 = fdiv reassoc ninf nsz float %394, %395
  %399 = load float*, float** %34, align 8
  %400 = load i32, i32* %35, align 4
  %401 = sub i32 %400, %42
  %402 = mul i32 %401, 3
  %403 = mul i32 %402, %51
  %404 = add i32 %lsr.iv, %403
  %405 = sext i32 %404 to i64
  %406 = getelementptr float, float* %399, i64 %405
  store float %396, float* %406, align 4
  %407 = load float*, float** %34, align 8
  %408 = load i32, i32* %35, align 4
  %409 = sub i32 %408, %42
  %410 = mul i32 %409, 3
  %411 = mul i32 %410, %51
  %412 = add i32 %lsr.iv, %411
  %413 = add i32 %412, 1
  %414 = sext i32 %413 to i64
  %415 = getelementptr float, float* %407, i64 %414
  store float %397, float* %415, align 4
  %416 = load float*, float** %34, align 8
  %417 = load i32, i32* %35, align 4
  %418 = sub i32 %417, %42
  %419 = mul i32 %418, 3
  %420 = mul i32 %419, %51
  %421 = add i32 %lsr.iv, %420
  %422 = add i32 %421, 2
  %423 = sext i32 %422 to i64
  %424 = getelementptr float, float* %416, i64 %423
  store float %398, float* %424, align 4
  %425 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %425
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn writeonly
declare dso_local float @expf(float noundef) local_unnamed_addr #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.36, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.36**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.36*, %struct.RuntimeContext.36** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.36*, i8*, i32)*, void (%struct.RuntimeContext.36*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.36*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.36*, i8*)*, void (%struct.RuntimeContext.36*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.36* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.36* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.36* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.36*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.36* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #6

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { alwaysinline mustprogress nofree nounwind willreturn writeonly "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
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
