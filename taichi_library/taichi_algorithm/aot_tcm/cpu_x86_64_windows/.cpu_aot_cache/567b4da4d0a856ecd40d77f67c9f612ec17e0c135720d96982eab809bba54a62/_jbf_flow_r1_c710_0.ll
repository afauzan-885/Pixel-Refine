; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.72*, void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*, i32)*, void (%struct.RuntimeContext.72*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.72 = type { i8*, %struct.LLVMRuntime.71*, i32, i64* }
%struct.LLVMRuntime.71 = type { %struct.PreallocatedMemoryChunk.67, %struct.PreallocatedMemoryChunk.67, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.68*], [1024 x %struct.NodeManager.69*], [1024 x i8*], i8*, %struct.RandState.70*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.67 = type { i8*, i8*, i64 }
%struct.ListManager.68 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.71* }
%struct.NodeManager.69 = type { %struct.LLVMRuntime.71*, i32, i32, i32, i32, %struct.ListManager.68*, %struct.ListManager.68*, %struct.ListManager.68*, i32 }
%struct.RandState.70 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_jbf_flow_r1_c710_0_kernel_0_serial(%struct.RuntimeContext.72* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.72* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_jbf_flow_r1_c710_0_kernel_1_range_for(%struct.RuntimeContext.72* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.72* %context, %struct.RuntimeContext.72** %4, align 8
  store void (%struct.RuntimeContext.72*, i8*)* null, void (%struct.RuntimeContext.72*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.72*, i8*, i32)* @function_body, void (%struct.RuntimeContext.72*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.72*, i8*)* null, void (%struct.RuntimeContext.72*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.72* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.72* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
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
  %36 = shl i32 %17, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %36, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %344, %for_loop_body ]
  %37 = load %struct.LLVMRuntime.71*, %struct.LLVMRuntime.71** %3, align 8
  %38 = getelementptr inbounds %struct.LLVMRuntime.71, %struct.LLVMRuntime.71* %37, i64 0, i32 14
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
  %91 = shl i32 %90, 1
  %92 = sext i32 %91 to i64
  %93 = getelementptr float, float* %87, i64 %92
  %94 = load float, float* %93, align 4
  %95 = getelementptr float, float* %93, i64 1
  %96 = load float, float* %95, align 4
  %97 = fmul reassoc ninf nsz float %94, %86
  %98 = fmul reassoc ninf nsz float %96, %86
  %99 = fadd reassoc ninf nsz float %86, 0x3D71979980000000
  %100 = tail call i32 @llvm.smax.i32(i32 %54, i32 0)
  %101 = tail call i32 @llvm.smin.i32(i32 %74, i32 %100)
  %102 = load float*, float** %29, align 8
  %103 = load i32, i32* %30, align 4
  %104 = mul i32 %103, %69
  %105 = add i32 %104, %101
  %106 = sext i32 %105 to i64
  %107 = getelementptr float, float* %102, i64 %106
  %108 = load float, float* %107, align 4
  %109 = fsub reassoc ninf nsz float %108, %62
  %110 = fmul reassoc ninf nsz float %109, %109
  %111 = fmul reassoc ninf nsz float %110, %25
  %112 = fsub reassoc ninf nsz float %27, %111
  %113 = tail call float @expf(float noundef %112) #1
  %114 = load float*, float** %31, align 8
  %115 = load i32, i32* %32, align 4
  %116 = mul i32 %115, %69
  %117 = add i32 %116, %101
  %118 = shl i32 %117, 1
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, float* %114, i64 %119
  %121 = load float, float* %120, align 4
  %122 = getelementptr float, float* %120, i64 1
  %123 = load float, float* %122, align 4
  %124 = fmul reassoc ninf nsz float %121, %113
  %125 = fmul reassoc ninf nsz float %123, %113
  %126 = fadd reassoc ninf nsz float %124, %97
  %127 = fadd reassoc ninf nsz float %125, %98
  %128 = fadd reassoc ninf nsz float %99, %113
  %129 = add i32 %54, 1
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 0)
  %131 = tail call i32 @llvm.smin.i32(i32 %74, i32 %130)
  %132 = load float*, float** %29, align 8
  %133 = load i32, i32* %30, align 4
  %134 = mul i32 %133, %69
  %135 = add i32 %134, %131
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, float* %132, i64 %136
  %138 = load float, float* %137, align 4
  %139 = fsub reassoc ninf nsz float %138, %62
  %140 = fmul reassoc ninf nsz float %139, %139
  %141 = fmul reassoc ninf nsz float %140, %25
  %142 = fsub reassoc ninf nsz float %26, %141
  %143 = tail call float @expf(float noundef %142) #1
  %144 = load float*, float** %31, align 8
  %145 = load i32, i32* %32, align 4
  %146 = mul i32 %145, %69
  %147 = add i32 %146, %131
  %148 = shl i32 %147, 1
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, float* %144, i64 %149
  %151 = load float, float* %150, align 4
  %152 = getelementptr float, float* %150, i64 1
  %153 = load float, float* %152, align 4
  %154 = fmul reassoc ninf nsz float %151, %143
  %155 = fmul reassoc ninf nsz float %153, %143
  %156 = fadd reassoc ninf nsz float %126, %154
  %157 = fadd reassoc ninf nsz float %127, %155
  %158 = fadd reassoc ninf nsz float %128, %143
  %159 = tail call i32 @llvm.smax.i32(i32 %51, i32 0)
  %160 = tail call i32 @llvm.smin.i32(i32 %67, i32 %159)
  %161 = load float*, float** %29, align 8
  %162 = load i32, i32* %30, align 4
  %163 = mul i32 %162, %160
  %164 = add i32 %163, %76
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, float* %161, i64 %165
  %167 = load float, float* %166, align 4
  %168 = fsub reassoc ninf nsz float %167, %62
  %169 = fmul reassoc ninf nsz float %168, %168
  %170 = fmul reassoc ninf nsz float %169, %25
  %171 = fsub reassoc ninf nsz float %27, %170
  %172 = tail call float @expf(float noundef %171) #1
  %173 = load float*, float** %31, align 8
  %174 = load i32, i32* %32, align 4
  %175 = mul i32 %174, %160
  %176 = add i32 %175, %76
  %177 = shl i32 %176, 1
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %173, i64 %178
  %180 = load float, float* %179, align 4
  %181 = getelementptr float, float* %179, i64 1
  %182 = load float, float* %181, align 4
  %183 = fmul reassoc ninf nsz float %180, %172
  %184 = fmul reassoc ninf nsz float %182, %172
  %185 = fadd reassoc ninf nsz float %156, %183
  %186 = fadd reassoc ninf nsz float %157, %184
  %187 = fadd reassoc ninf nsz float %158, %172
  %188 = load float*, float** %29, align 8
  %189 = load i32, i32* %30, align 4
  %190 = mul i32 %189, %160
  %191 = add i32 %190, %101
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, float* %188, i64 %192
  %194 = load float, float* %193, align 4
  %195 = fsub reassoc ninf nsz float %194, %62
  %196 = fmul reassoc ninf nsz float %195, %195
  %197 = fmul reassoc ninf nsz float %196, %33
  %198 = tail call float @expf(float noundef %197) #1
  %199 = load float*, float** %31, align 8
  %200 = load i32, i32* %32, align 4
  %201 = mul i32 %200, %160
  %202 = add i32 %201, %101
  %203 = shl i32 %202, 1
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, float* %199, i64 %204
  %206 = load float, float* %205, align 4
  %207 = getelementptr float, float* %205, i64 1
  %208 = load float, float* %207, align 4
  %209 = fmul reassoc ninf nsz float %206, %198
  %210 = fmul reassoc ninf nsz float %208, %198
  %211 = fadd reassoc ninf nsz float %185, %209
  %212 = fadd reassoc ninf nsz float %186, %210
  %213 = fadd reassoc ninf nsz float %187, %198
  %214 = load float*, float** %29, align 8
  %215 = load i32, i32* %30, align 4
  %216 = mul i32 %215, %160
  %217 = add i32 %216, %131
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, float* %214, i64 %218
  %220 = load float, float* %219, align 4
  %221 = fsub reassoc ninf nsz float %220, %62
  %222 = fmul reassoc ninf nsz float %221, %221
  %223 = fmul reassoc ninf nsz float %222, %25
  %224 = fsub reassoc ninf nsz float %27, %223
  %225 = tail call float @expf(float noundef %224) #1
  %226 = load float*, float** %31, align 8
  %227 = load i32, i32* %32, align 4
  %228 = mul i32 %227, %160
  %229 = add i32 %228, %131
  %230 = shl i32 %229, 1
  %231 = sext i32 %230 to i64
  %232 = getelementptr float, float* %226, i64 %231
  %233 = load float, float* %232, align 4
  %234 = getelementptr float, float* %232, i64 1
  %235 = load float, float* %234, align 4
  %236 = fmul reassoc ninf nsz float %233, %225
  %237 = fmul reassoc ninf nsz float %235, %225
  %238 = fadd reassoc ninf nsz float %211, %236
  %239 = fadd reassoc ninf nsz float %212, %237
  %240 = fadd reassoc ninf nsz float %213, %225
  %241 = add i32 %51, 1
  %242 = tail call i32 @llvm.smax.i32(i32 %241, i32 0)
  %243 = tail call i32 @llvm.smin.i32(i32 %67, i32 %242)
  %244 = load float*, float** %29, align 8
  %245 = load i32, i32* %30, align 4
  %246 = mul i32 %245, %243
  %247 = add i32 %246, %76
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, float* %244, i64 %248
  %250 = load float, float* %249, align 4
  %251 = fsub reassoc ninf nsz float %250, %62
  %252 = fmul reassoc ninf nsz float %251, %251
  %253 = fmul reassoc ninf nsz float %252, %25
  %254 = fsub reassoc ninf nsz float %26, %253
  %255 = tail call float @expf(float noundef %254) #1
  %256 = load float*, float** %31, align 8
  %257 = load i32, i32* %32, align 4
  %258 = mul i32 %257, %243
  %259 = add i32 %258, %76
  %260 = shl i32 %259, 1
  %261 = sext i32 %260 to i64
  %262 = getelementptr float, float* %256, i64 %261
  %263 = load float, float* %262, align 4
  %264 = getelementptr float, float* %262, i64 1
  %265 = load float, float* %264, align 4
  %266 = fmul reassoc ninf nsz float %263, %255
  %267 = fmul reassoc ninf nsz float %265, %255
  %268 = fadd reassoc ninf nsz float %238, %266
  %269 = fadd reassoc ninf nsz float %239, %267
  %270 = fadd reassoc ninf nsz float %240, %255
  %271 = load float*, float** %29, align 8
  %272 = load i32, i32* %30, align 4
  %273 = mul i32 %272, %243
  %274 = add i32 %273, %101
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, float* %271, i64 %275
  %277 = load float, float* %276, align 4
  %278 = fsub reassoc ninf nsz float %277, %62
  %279 = fmul reassoc ninf nsz float %278, %278
  %280 = fmul reassoc ninf nsz float %279, %25
  %281 = fsub reassoc ninf nsz float %27, %280
  %282 = tail call float @expf(float noundef %281) #1
  %283 = load float*, float** %31, align 8
  %284 = load i32, i32* %32, align 4
  %285 = mul i32 %284, %243
  %286 = add i32 %285, %101
  %287 = shl i32 %286, 1
  %288 = sext i32 %287 to i64
  %289 = getelementptr float, float* %283, i64 %288
  %290 = load float, float* %289, align 4
  %291 = getelementptr float, float* %289, i64 1
  %292 = load float, float* %291, align 4
  %293 = fmul reassoc ninf nsz float %290, %282
  %294 = fmul reassoc ninf nsz float %292, %282
  %295 = fadd reassoc ninf nsz float %268, %293
  %296 = fadd reassoc ninf nsz float %269, %294
  %297 = fadd reassoc ninf nsz float %270, %282
  %298 = load float*, float** %29, align 8
  %299 = load i32, i32* %30, align 4
  %300 = mul i32 %299, %243
  %301 = add i32 %300, %131
  %302 = sext i32 %301 to i64
  %303 = getelementptr float, float* %298, i64 %302
  %304 = load float, float* %303, align 4
  %305 = fsub reassoc ninf nsz float %304, %62
  %306 = fmul reassoc ninf nsz float %305, %305
  %307 = fmul reassoc ninf nsz float %306, %25
  %308 = fsub reassoc ninf nsz float %26, %307
  %309 = tail call float @expf(float noundef %308) #1
  %310 = load float*, float** %31, align 8
  %311 = load i32, i32* %32, align 4
  %312 = mul i32 %311, %243
  %313 = add i32 %312, %131
  %314 = shl i32 %313, 1
  %315 = sext i32 %314 to i64
  %316 = getelementptr float, float* %310, i64 %315
  %317 = load float, float* %316, align 4
  %318 = getelementptr float, float* %316, i64 1
  %319 = load float, float* %318, align 4
  %320 = fmul reassoc ninf nsz float %317, %309
  %321 = fmul reassoc ninf nsz float %319, %309
  %322 = fadd reassoc ninf nsz float %295, %320
  %323 = fadd reassoc ninf nsz float %296, %321
  %324 = fadd reassoc ninf nsz float %297, %309
  %325 = fdiv reassoc ninf nsz float %322, %324
  %326 = fdiv reassoc ninf nsz float %323, %324
  %327 = load float*, float** %34, align 8
  %328 = load i32, i32* %35, align 4
  %329 = sub i32 %328, %42
  %330 = shl i32 %329, 1
  %331 = mul i32 %330, %51
  %332 = add i32 %lsr.iv, %331
  %333 = sext i32 %332 to i64
  %334 = getelementptr float, float* %327, i64 %333
  store float %325, float* %334, align 4
  %335 = load float*, float** %34, align 8
  %336 = load i32, i32* %35, align 4
  %337 = sub i32 %336, %42
  %338 = shl i32 %337, 1
  %339 = mul i32 %338, %51
  %340 = add i32 %lsr.iv, %339
  %341 = add i32 %340, 1
  %342 = sext i32 %341 to i64
  %343 = getelementptr float, float* %335, i64 %342
  store float %326, float* %343, align 4
  %344 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %344
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
  %4 = alloca %struct.RuntimeContext.72, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.72**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.72*, %struct.RuntimeContext.72** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.72*, i8*, i32)*, void (%struct.RuntimeContext.72*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.72*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.72*, i8*)*, void (%struct.RuntimeContext.72*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.72*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.72* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.72* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.72* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.72, %struct.RuntimeContext.72* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.72* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.72* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.72*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.72* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
