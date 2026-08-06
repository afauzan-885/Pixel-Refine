; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.84*, void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.84 = type { i8*, %struct.LLVMRuntime.83*, i32, i64* }
%struct.LLVMRuntime.83 = type { %struct.PreallocatedMemoryChunk.79, %struct.PreallocatedMemoryChunk.79, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.80*], [1024 x %struct.NodeManager.81*], [1024 x i8*], i8*, %struct.RandState.82*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.79 = type { i8*, i8*, i64 }
%struct.ListManager.80 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.83* }
%struct.NodeManager.81 = type { %struct.LLVMRuntime.83*, i32, i32, i32, i32, %struct.ListManager.80*, %struct.ListManager.80*, %struct.ListManager.80*, i32 }
%struct.RandState.82 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_jbf_flow_r2_c712_0_kernel_0_serial(%struct.RuntimeContext.84* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.84* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_jbf_flow_r2_c712_0_kernel_1_range_for(%struct.RuntimeContext.84* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.84* %context, %struct.RuntimeContext.84** %4, align 8
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.84*, i8*, i32)* @function_body, void (%struct.RuntimeContext.84*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.84*, i8*)* null, void (%struct.RuntimeContext.84*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.84* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.84* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 5
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 6
  %25 = load float, float* %24, align 4
  %26 = fmul reassoc ninf nsz float %23, -8.000000e+00
  %27 = fmul reassoc ninf nsz float %23, -5.000000e+00
  %28 = fmul reassoc ninf nsz float %23, -4.000000e+00
  %29 = fmul reassoc ninf nsz float %23, -2.000000e+00
  %30 = fneg reassoc ninf nsz float %23
  %31 = icmp slt i32 %17, %19
  br i1 %31, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %36 = fneg reassoc ninf nsz float %25
  %37 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %38 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %21, i64 0, i32 2, i32 0, i32 1
  %39 = shl i32 %17, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %39, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %791, %for_loop_body ]
  %40 = load %struct.LLVMRuntime.83*, %struct.LLVMRuntime.83** %3, align 8
  %41 = getelementptr inbounds %struct.LLVMRuntime.83, %struct.LLVMRuntime.83* %40, i64 0, i32 14
  %42 = load i8*, i8** %41, align 8
  %43 = getelementptr inbounds i8, i8* %42, i64 4
  %44 = bitcast i8* %43 to i32*
  %45 = load i32, i32* %44, align 4
  %46 = sdiv i32 %.05, %45
  %47 = mul i32 %46, %45
  %48 = xor i32 %45, %.05
  %49 = icmp slt i32 %48, 0
  %50 = icmp ne i32 %.05, 0
  %51 = icmp ne i32 %.05, %47
  %52 = and i1 %50, %49
  %53 = and i1 %52, %51
  %.neg4 = sext i1 %53 to i32
  %54 = add i32 %46, %.neg4
  %55 = mul i32 %45, -1
  %56 = mul i32 %55, %54
  %57 = add i32 %.05, %56
  %58 = load float*, float** %32, align 8
  %59 = load i32, i32* %33, align 4
  %60 = sub i32 %59, %45
  %61 = mul i32 %60, %54
  %62 = add i32 %.05, %61
  %63 = sext i32 %62 to i64
  %64 = getelementptr float, float* %58, i64 %63
  %65 = load float, float* %64, align 4
  %66 = add i32 %54, -2
  %67 = getelementptr inbounds i8, i8* %42, i64 8
  %68 = bitcast i8* %67 to i32*
  %69 = load i32, i32* %68, align 4
  %70 = add i32 %69, -1
  %71 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %72 = tail call i32 @llvm.smin.i32(i32 %70, i32 %71)
  %73 = add i32 %57, -2
  %74 = getelementptr inbounds i8, i8* %42, i64 12
  %75 = bitcast i8* %74 to i32*
  %76 = load i32, i32* %75, align 4
  %77 = add i32 %76, -1
  %78 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %79 = tail call i32 @llvm.smin.i32(i32 %77, i32 %78)
  %80 = mul i32 %72, %59
  %81 = add i32 %79, %80
  %82 = sext i32 %81 to i64
  %83 = getelementptr float, float* %58, i64 %82
  %84 = load float, float* %83, align 4
  %85 = fsub reassoc ninf nsz float %84, %65
  %86 = fmul reassoc ninf nsz float %85, %85
  %87 = fmul reassoc ninf nsz float %86, %25
  %88 = fsub reassoc ninf nsz float %26, %87
  %89 = tail call float @expf(float noundef %88) #1
  %90 = load float*, float** %34, align 8
  %91 = load i32, i32* %35, align 4
  %92 = mul i32 %91, %72
  %93 = add i32 %92, %79
  %94 = shl i32 %93, 1
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, float* %90, i64 %95
  %97 = load float, float* %96, align 4
  %98 = getelementptr float, float* %96, i64 1
  %99 = load float, float* %98, align 4
  %100 = fmul reassoc ninf nsz float %97, %89
  %101 = fmul reassoc ninf nsz float %99, %89
  %102 = fadd reassoc ninf nsz float %89, 0x3D71979980000000
  %103 = add i32 %57, -1
  %104 = tail call i32 @llvm.smax.i32(i32 %103, i32 0)
  %105 = tail call i32 @llvm.smin.i32(i32 %77, i32 %104)
  %106 = load float*, float** %32, align 8
  %107 = load i32, i32* %33, align 4
  %108 = mul i32 %107, %72
  %109 = add i32 %108, %105
  %110 = sext i32 %109 to i64
  %111 = getelementptr float, float* %106, i64 %110
  %112 = load float, float* %111, align 4
  %113 = fsub reassoc ninf nsz float %112, %65
  %114 = fmul reassoc ninf nsz float %113, %113
  %115 = fmul reassoc ninf nsz float %114, %25
  %116 = fsub reassoc ninf nsz float %27, %115
  %117 = tail call float @expf(float noundef %116) #1
  %118 = load float*, float** %34, align 8
  %119 = load i32, i32* %35, align 4
  %120 = mul i32 %119, %72
  %121 = add i32 %120, %105
  %122 = shl i32 %121, 1
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, float* %118, i64 %123
  %125 = load float, float* %124, align 4
  %126 = getelementptr float, float* %124, i64 1
  %127 = load float, float* %126, align 4
  %128 = fmul reassoc ninf nsz float %125, %117
  %129 = fmul reassoc ninf nsz float %127, %117
  %130 = fadd reassoc ninf nsz float %128, %100
  %131 = fadd reassoc ninf nsz float %129, %101
  %132 = fadd reassoc ninf nsz float %102, %117
  %133 = tail call i32 @llvm.smax.i32(i32 %57, i32 0)
  %134 = tail call i32 @llvm.smin.i32(i32 %77, i32 %133)
  %135 = load float*, float** %32, align 8
  %136 = load i32, i32* %33, align 4
  %137 = mul i32 %136, %72
  %138 = add i32 %137, %134
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, float* %135, i64 %139
  %141 = load float, float* %140, align 4
  %142 = fsub reassoc ninf nsz float %141, %65
  %143 = fmul reassoc ninf nsz float %142, %142
  %144 = fmul reassoc ninf nsz float %143, %25
  %145 = fsub reassoc ninf nsz float %28, %144
  %146 = tail call float @expf(float noundef %145) #1
  %147 = load float*, float** %34, align 8
  %148 = load i32, i32* %35, align 4
  %149 = mul i32 %148, %72
  %150 = add i32 %149, %134
  %151 = shl i32 %150, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, float* %147, i64 %152
  %154 = load float, float* %153, align 4
  %155 = getelementptr float, float* %153, i64 1
  %156 = load float, float* %155, align 4
  %157 = fmul reassoc ninf nsz float %154, %146
  %158 = fmul reassoc ninf nsz float %156, %146
  %159 = fadd reassoc ninf nsz float %130, %157
  %160 = fadd reassoc ninf nsz float %131, %158
  %161 = fadd reassoc ninf nsz float %132, %146
  %162 = add i32 %57, 1
  %163 = tail call i32 @llvm.smax.i32(i32 %162, i32 0)
  %164 = tail call i32 @llvm.smin.i32(i32 %77, i32 %163)
  %165 = load float*, float** %32, align 8
  %166 = load i32, i32* %33, align 4
  %167 = mul i32 %166, %72
  %168 = add i32 %167, %164
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, float* %165, i64 %169
  %171 = load float, float* %170, align 4
  %172 = fsub reassoc ninf nsz float %171, %65
  %173 = fmul reassoc ninf nsz float %172, %172
  %174 = fmul reassoc ninf nsz float %173, %25
  %175 = fsub reassoc ninf nsz float %27, %174
  %176 = tail call float @expf(float noundef %175) #1
  %177 = load float*, float** %34, align 8
  %178 = load i32, i32* %35, align 4
  %179 = mul i32 %178, %72
  %180 = add i32 %179, %164
  %181 = shl i32 %180, 1
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, float* %177, i64 %182
  %184 = load float, float* %183, align 4
  %185 = getelementptr float, float* %183, i64 1
  %186 = load float, float* %185, align 4
  %187 = fmul reassoc ninf nsz float %184, %176
  %188 = fmul reassoc ninf nsz float %186, %176
  %189 = fadd reassoc ninf nsz float %159, %187
  %190 = fadd reassoc ninf nsz float %160, %188
  %191 = fadd reassoc ninf nsz float %161, %176
  %192 = add i32 %57, 2
  %193 = tail call i32 @llvm.smax.i32(i32 %192, i32 0)
  %194 = tail call i32 @llvm.smin.i32(i32 %77, i32 %193)
  %195 = load float*, float** %32, align 8
  %196 = load i32, i32* %33, align 4
  %197 = mul i32 %196, %72
  %198 = add i32 %197, %194
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, float* %195, i64 %199
  %201 = load float, float* %200, align 4
  %202 = fsub reassoc ninf nsz float %201, %65
  %203 = fmul reassoc ninf nsz float %202, %202
  %204 = fmul reassoc ninf nsz float %203, %25
  %205 = fsub reassoc ninf nsz float %26, %204
  %206 = tail call float @expf(float noundef %205) #1
  %207 = load float*, float** %34, align 8
  %208 = load i32, i32* %35, align 4
  %209 = mul i32 %208, %72
  %210 = add i32 %209, %194
  %211 = shl i32 %210, 1
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, float* %207, i64 %212
  %214 = load float, float* %213, align 4
  %215 = getelementptr float, float* %213, i64 1
  %216 = load float, float* %215, align 4
  %217 = fmul reassoc ninf nsz float %214, %206
  %218 = fmul reassoc ninf nsz float %216, %206
  %219 = fadd reassoc ninf nsz float %189, %217
  %220 = fadd reassoc ninf nsz float %190, %218
  %221 = fadd reassoc ninf nsz float %191, %206
  %222 = add i32 %54, -1
  %223 = tail call i32 @llvm.smax.i32(i32 %222, i32 0)
  %224 = tail call i32 @llvm.smin.i32(i32 %70, i32 %223)
  %225 = load float*, float** %32, align 8
  %226 = load i32, i32* %33, align 4
  %227 = mul i32 %226, %224
  %228 = add i32 %227, %79
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %225, i64 %229
  %231 = load float, float* %230, align 4
  %232 = fsub reassoc ninf nsz float %231, %65
  %233 = fmul reassoc ninf nsz float %232, %232
  %234 = fmul reassoc ninf nsz float %233, %25
  %235 = fsub reassoc ninf nsz float %27, %234
  %236 = tail call float @expf(float noundef %235) #1
  %237 = load float*, float** %34, align 8
  %238 = load i32, i32* %35, align 4
  %239 = mul i32 %238, %224
  %240 = add i32 %239, %79
  %241 = shl i32 %240, 1
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, float* %237, i64 %242
  %244 = load float, float* %243, align 4
  %245 = getelementptr float, float* %243, i64 1
  %246 = load float, float* %245, align 4
  %247 = fmul reassoc ninf nsz float %244, %236
  %248 = fmul reassoc ninf nsz float %246, %236
  %249 = fadd reassoc ninf nsz float %219, %247
  %250 = fadd reassoc ninf nsz float %220, %248
  %251 = fadd reassoc ninf nsz float %221, %236
  %252 = load float*, float** %32, align 8
  %253 = load i32, i32* %33, align 4
  %254 = mul i32 %253, %224
  %255 = add i32 %254, %105
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, float* %252, i64 %256
  %258 = load float, float* %257, align 4
  %259 = fsub reassoc ninf nsz float %258, %65
  %260 = fmul reassoc ninf nsz float %259, %259
  %261 = fmul reassoc ninf nsz float %260, %25
  %262 = fsub reassoc ninf nsz float %29, %261
  %263 = tail call float @expf(float noundef %262) #1
  %264 = load float*, float** %34, align 8
  %265 = load i32, i32* %35, align 4
  %266 = mul i32 %265, %224
  %267 = add i32 %266, %105
  %268 = shl i32 %267, 1
  %269 = sext i32 %268 to i64
  %270 = getelementptr float, float* %264, i64 %269
  %271 = load float, float* %270, align 4
  %272 = getelementptr float, float* %270, i64 1
  %273 = load float, float* %272, align 4
  %274 = fmul reassoc ninf nsz float %271, %263
  %275 = fmul reassoc ninf nsz float %273, %263
  %276 = fadd reassoc ninf nsz float %249, %274
  %277 = fadd reassoc ninf nsz float %250, %275
  %278 = fadd reassoc ninf nsz float %251, %263
  %279 = load float*, float** %32, align 8
  %280 = load i32, i32* %33, align 4
  %281 = mul i32 %280, %224
  %282 = add i32 %281, %134
  %283 = sext i32 %282 to i64
  %284 = getelementptr float, float* %279, i64 %283
  %285 = load float, float* %284, align 4
  %286 = fsub reassoc ninf nsz float %285, %65
  %287 = fmul reassoc ninf nsz float %286, %286
  %288 = fmul reassoc ninf nsz float %287, %25
  %289 = fsub reassoc ninf nsz float %30, %288
  %290 = tail call float @expf(float noundef %289) #1
  %291 = load float*, float** %34, align 8
  %292 = load i32, i32* %35, align 4
  %293 = mul i32 %292, %224
  %294 = add i32 %293, %134
  %295 = shl i32 %294, 1
  %296 = sext i32 %295 to i64
  %297 = getelementptr float, float* %291, i64 %296
  %298 = load float, float* %297, align 4
  %299 = getelementptr float, float* %297, i64 1
  %300 = load float, float* %299, align 4
  %301 = fmul reassoc ninf nsz float %298, %290
  %302 = fmul reassoc ninf nsz float %300, %290
  %303 = fadd reassoc ninf nsz float %276, %301
  %304 = fadd reassoc ninf nsz float %277, %302
  %305 = fadd reassoc ninf nsz float %278, %290
  %306 = load float*, float** %32, align 8
  %307 = load i32, i32* %33, align 4
  %308 = mul i32 %307, %224
  %309 = add i32 %308, %164
  %310 = sext i32 %309 to i64
  %311 = getelementptr float, float* %306, i64 %310
  %312 = load float, float* %311, align 4
  %313 = fsub reassoc ninf nsz float %312, %65
  %314 = fmul reassoc ninf nsz float %313, %313
  %315 = fmul reassoc ninf nsz float %314, %25
  %316 = fsub reassoc ninf nsz float %29, %315
  %317 = tail call float @expf(float noundef %316) #1
  %318 = load float*, float** %34, align 8
  %319 = load i32, i32* %35, align 4
  %320 = mul i32 %319, %224
  %321 = add i32 %320, %164
  %322 = shl i32 %321, 1
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, float* %318, i64 %323
  %325 = load float, float* %324, align 4
  %326 = getelementptr float, float* %324, i64 1
  %327 = load float, float* %326, align 4
  %328 = fmul reassoc ninf nsz float %325, %317
  %329 = fmul reassoc ninf nsz float %327, %317
  %330 = fadd reassoc ninf nsz float %303, %328
  %331 = fadd reassoc ninf nsz float %304, %329
  %332 = fadd reassoc ninf nsz float %305, %317
  %333 = load float*, float** %32, align 8
  %334 = load i32, i32* %33, align 4
  %335 = mul i32 %334, %224
  %336 = add i32 %335, %194
  %337 = sext i32 %336 to i64
  %338 = getelementptr float, float* %333, i64 %337
  %339 = load float, float* %338, align 4
  %340 = fsub reassoc ninf nsz float %339, %65
  %341 = fmul reassoc ninf nsz float %340, %340
  %342 = fmul reassoc ninf nsz float %341, %25
  %343 = fsub reassoc ninf nsz float %27, %342
  %344 = tail call float @expf(float noundef %343) #1
  %345 = load float*, float** %34, align 8
  %346 = load i32, i32* %35, align 4
  %347 = mul i32 %346, %224
  %348 = add i32 %347, %194
  %349 = shl i32 %348, 1
  %350 = sext i32 %349 to i64
  %351 = getelementptr float, float* %345, i64 %350
  %352 = load float, float* %351, align 4
  %353 = getelementptr float, float* %351, i64 1
  %354 = load float, float* %353, align 4
  %355 = fmul reassoc ninf nsz float %352, %344
  %356 = fmul reassoc ninf nsz float %354, %344
  %357 = fadd reassoc ninf nsz float %330, %355
  %358 = fadd reassoc ninf nsz float %331, %356
  %359 = fadd reassoc ninf nsz float %332, %344
  %360 = tail call i32 @llvm.smax.i32(i32 %54, i32 0)
  %361 = tail call i32 @llvm.smin.i32(i32 %70, i32 %360)
  %362 = load float*, float** %32, align 8
  %363 = load i32, i32* %33, align 4
  %364 = mul i32 %363, %361
  %365 = add i32 %364, %79
  %366 = sext i32 %365 to i64
  %367 = getelementptr float, float* %362, i64 %366
  %368 = load float, float* %367, align 4
  %369 = fsub reassoc ninf nsz float %368, %65
  %370 = fmul reassoc ninf nsz float %369, %369
  %371 = fmul reassoc ninf nsz float %370, %25
  %372 = fsub reassoc ninf nsz float %28, %371
  %373 = tail call float @expf(float noundef %372) #1
  %374 = load float*, float** %34, align 8
  %375 = load i32, i32* %35, align 4
  %376 = mul i32 %375, %361
  %377 = add i32 %376, %79
  %378 = shl i32 %377, 1
  %379 = sext i32 %378 to i64
  %380 = getelementptr float, float* %374, i64 %379
  %381 = load float, float* %380, align 4
  %382 = getelementptr float, float* %380, i64 1
  %383 = load float, float* %382, align 4
  %384 = fmul reassoc ninf nsz float %381, %373
  %385 = fmul reassoc ninf nsz float %383, %373
  %386 = fadd reassoc ninf nsz float %357, %384
  %387 = fadd reassoc ninf nsz float %358, %385
  %388 = fadd reassoc ninf nsz float %359, %373
  %389 = load float*, float** %32, align 8
  %390 = load i32, i32* %33, align 4
  %391 = mul i32 %390, %361
  %392 = add i32 %391, %105
  %393 = sext i32 %392 to i64
  %394 = getelementptr float, float* %389, i64 %393
  %395 = load float, float* %394, align 4
  %396 = fsub reassoc ninf nsz float %395, %65
  %397 = fmul reassoc ninf nsz float %396, %396
  %398 = fmul reassoc ninf nsz float %397, %25
  %399 = fsub reassoc ninf nsz float %30, %398
  %400 = tail call float @expf(float noundef %399) #1
  %401 = load float*, float** %34, align 8
  %402 = load i32, i32* %35, align 4
  %403 = mul i32 %402, %361
  %404 = add i32 %403, %105
  %405 = shl i32 %404, 1
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, float* %401, i64 %406
  %408 = load float, float* %407, align 4
  %409 = getelementptr float, float* %407, i64 1
  %410 = load float, float* %409, align 4
  %411 = fmul reassoc ninf nsz float %408, %400
  %412 = fmul reassoc ninf nsz float %410, %400
  %413 = fadd reassoc ninf nsz float %386, %411
  %414 = fadd reassoc ninf nsz float %387, %412
  %415 = fadd reassoc ninf nsz float %388, %400
  %416 = load float*, float** %32, align 8
  %417 = load i32, i32* %33, align 4
  %418 = mul i32 %417, %361
  %419 = add i32 %418, %134
  %420 = sext i32 %419 to i64
  %421 = getelementptr float, float* %416, i64 %420
  %422 = load float, float* %421, align 4
  %423 = fsub reassoc ninf nsz float %422, %65
  %424 = fmul reassoc ninf nsz float %423, %423
  %425 = fmul reassoc ninf nsz float %424, %36
  %426 = tail call float @expf(float noundef %425) #1
  %427 = load float*, float** %34, align 8
  %428 = load i32, i32* %35, align 4
  %429 = mul i32 %428, %361
  %430 = add i32 %429, %134
  %431 = shl i32 %430, 1
  %432 = sext i32 %431 to i64
  %433 = getelementptr float, float* %427, i64 %432
  %434 = load float, float* %433, align 4
  %435 = getelementptr float, float* %433, i64 1
  %436 = load float, float* %435, align 4
  %437 = fmul reassoc ninf nsz float %434, %426
  %438 = fmul reassoc ninf nsz float %436, %426
  %439 = fadd reassoc ninf nsz float %413, %437
  %440 = fadd reassoc ninf nsz float %414, %438
  %441 = fadd reassoc ninf nsz float %415, %426
  %442 = load float*, float** %32, align 8
  %443 = load i32, i32* %33, align 4
  %444 = mul i32 %443, %361
  %445 = add i32 %444, %164
  %446 = sext i32 %445 to i64
  %447 = getelementptr float, float* %442, i64 %446
  %448 = load float, float* %447, align 4
  %449 = fsub reassoc ninf nsz float %448, %65
  %450 = fmul reassoc ninf nsz float %449, %449
  %451 = fmul reassoc ninf nsz float %450, %25
  %452 = fsub reassoc ninf nsz float %30, %451
  %453 = tail call float @expf(float noundef %452) #1
  %454 = load float*, float** %34, align 8
  %455 = load i32, i32* %35, align 4
  %456 = mul i32 %455, %361
  %457 = add i32 %456, %164
  %458 = shl i32 %457, 1
  %459 = sext i32 %458 to i64
  %460 = getelementptr float, float* %454, i64 %459
  %461 = load float, float* %460, align 4
  %462 = getelementptr float, float* %460, i64 1
  %463 = load float, float* %462, align 4
  %464 = fmul reassoc ninf nsz float %461, %453
  %465 = fmul reassoc ninf nsz float %463, %453
  %466 = fadd reassoc ninf nsz float %439, %464
  %467 = fadd reassoc ninf nsz float %440, %465
  %468 = fadd reassoc ninf nsz float %441, %453
  %469 = load float*, float** %32, align 8
  %470 = load i32, i32* %33, align 4
  %471 = mul i32 %470, %361
  %472 = add i32 %471, %194
  %473 = sext i32 %472 to i64
  %474 = getelementptr float, float* %469, i64 %473
  %475 = load float, float* %474, align 4
  %476 = fsub reassoc ninf nsz float %475, %65
  %477 = fmul reassoc ninf nsz float %476, %476
  %478 = fmul reassoc ninf nsz float %477, %25
  %479 = fsub reassoc ninf nsz float %28, %478
  %480 = tail call float @expf(float noundef %479) #1
  %481 = load float*, float** %34, align 8
  %482 = load i32, i32* %35, align 4
  %483 = mul i32 %482, %361
  %484 = add i32 %483, %194
  %485 = shl i32 %484, 1
  %486 = sext i32 %485 to i64
  %487 = getelementptr float, float* %481, i64 %486
  %488 = load float, float* %487, align 4
  %489 = getelementptr float, float* %487, i64 1
  %490 = load float, float* %489, align 4
  %491 = fmul reassoc ninf nsz float %488, %480
  %492 = fmul reassoc ninf nsz float %490, %480
  %493 = fadd reassoc ninf nsz float %466, %491
  %494 = fadd reassoc ninf nsz float %467, %492
  %495 = fadd reassoc ninf nsz float %468, %480
  %496 = add i32 %54, 1
  %497 = tail call i32 @llvm.smax.i32(i32 %496, i32 0)
  %498 = tail call i32 @llvm.smin.i32(i32 %70, i32 %497)
  %499 = load float*, float** %32, align 8
  %500 = load i32, i32* %33, align 4
  %501 = mul i32 %500, %498
  %502 = add i32 %501, %79
  %503 = sext i32 %502 to i64
  %504 = getelementptr float, float* %499, i64 %503
  %505 = load float, float* %504, align 4
  %506 = fsub reassoc ninf nsz float %505, %65
  %507 = fmul reassoc ninf nsz float %506, %506
  %508 = fmul reassoc ninf nsz float %507, %25
  %509 = fsub reassoc ninf nsz float %27, %508
  %510 = tail call float @expf(float noundef %509) #1
  %511 = load float*, float** %34, align 8
  %512 = load i32, i32* %35, align 4
  %513 = mul i32 %512, %498
  %514 = add i32 %513, %79
  %515 = shl i32 %514, 1
  %516 = sext i32 %515 to i64
  %517 = getelementptr float, float* %511, i64 %516
  %518 = load float, float* %517, align 4
  %519 = getelementptr float, float* %517, i64 1
  %520 = load float, float* %519, align 4
  %521 = fmul reassoc ninf nsz float %518, %510
  %522 = fmul reassoc ninf nsz float %520, %510
  %523 = fadd reassoc ninf nsz float %493, %521
  %524 = fadd reassoc ninf nsz float %494, %522
  %525 = fadd reassoc ninf nsz float %495, %510
  %526 = load float*, float** %32, align 8
  %527 = load i32, i32* %33, align 4
  %528 = mul i32 %527, %498
  %529 = add i32 %528, %105
  %530 = sext i32 %529 to i64
  %531 = getelementptr float, float* %526, i64 %530
  %532 = load float, float* %531, align 4
  %533 = fsub reassoc ninf nsz float %532, %65
  %534 = fmul reassoc ninf nsz float %533, %533
  %535 = fmul reassoc ninf nsz float %534, %25
  %536 = fsub reassoc ninf nsz float %29, %535
  %537 = tail call float @expf(float noundef %536) #1
  %538 = load float*, float** %34, align 8
  %539 = load i32, i32* %35, align 4
  %540 = mul i32 %539, %498
  %541 = add i32 %540, %105
  %542 = shl i32 %541, 1
  %543 = sext i32 %542 to i64
  %544 = getelementptr float, float* %538, i64 %543
  %545 = load float, float* %544, align 4
  %546 = getelementptr float, float* %544, i64 1
  %547 = load float, float* %546, align 4
  %548 = fmul reassoc ninf nsz float %545, %537
  %549 = fmul reassoc ninf nsz float %547, %537
  %550 = fadd reassoc ninf nsz float %523, %548
  %551 = fadd reassoc ninf nsz float %524, %549
  %552 = fadd reassoc ninf nsz float %525, %537
  %553 = load float*, float** %32, align 8
  %554 = load i32, i32* %33, align 4
  %555 = mul i32 %554, %498
  %556 = add i32 %555, %134
  %557 = sext i32 %556 to i64
  %558 = getelementptr float, float* %553, i64 %557
  %559 = load float, float* %558, align 4
  %560 = fsub reassoc ninf nsz float %559, %65
  %561 = fmul reassoc ninf nsz float %560, %560
  %562 = fmul reassoc ninf nsz float %561, %25
  %563 = fsub reassoc ninf nsz float %30, %562
  %564 = tail call float @expf(float noundef %563) #1
  %565 = load float*, float** %34, align 8
  %566 = load i32, i32* %35, align 4
  %567 = mul i32 %566, %498
  %568 = add i32 %567, %134
  %569 = shl i32 %568, 1
  %570 = sext i32 %569 to i64
  %571 = getelementptr float, float* %565, i64 %570
  %572 = load float, float* %571, align 4
  %573 = getelementptr float, float* %571, i64 1
  %574 = load float, float* %573, align 4
  %575 = fmul reassoc ninf nsz float %572, %564
  %576 = fmul reassoc ninf nsz float %574, %564
  %577 = fadd reassoc ninf nsz float %550, %575
  %578 = fadd reassoc ninf nsz float %551, %576
  %579 = fadd reassoc ninf nsz float %552, %564
  %580 = load float*, float** %32, align 8
  %581 = load i32, i32* %33, align 4
  %582 = mul i32 %581, %498
  %583 = add i32 %582, %164
  %584 = sext i32 %583 to i64
  %585 = getelementptr float, float* %580, i64 %584
  %586 = load float, float* %585, align 4
  %587 = fsub reassoc ninf nsz float %586, %65
  %588 = fmul reassoc ninf nsz float %587, %587
  %589 = fmul reassoc ninf nsz float %588, %25
  %590 = fsub reassoc ninf nsz float %29, %589
  %591 = tail call float @expf(float noundef %590) #1
  %592 = load float*, float** %34, align 8
  %593 = load i32, i32* %35, align 4
  %594 = mul i32 %593, %498
  %595 = add i32 %594, %164
  %596 = shl i32 %595, 1
  %597 = sext i32 %596 to i64
  %598 = getelementptr float, float* %592, i64 %597
  %599 = load float, float* %598, align 4
  %600 = getelementptr float, float* %598, i64 1
  %601 = load float, float* %600, align 4
  %602 = fmul reassoc ninf nsz float %599, %591
  %603 = fmul reassoc ninf nsz float %601, %591
  %604 = fadd reassoc ninf nsz float %577, %602
  %605 = fadd reassoc ninf nsz float %578, %603
  %606 = fadd reassoc ninf nsz float %579, %591
  %607 = load float*, float** %32, align 8
  %608 = load i32, i32* %33, align 4
  %609 = mul i32 %608, %498
  %610 = add i32 %609, %194
  %611 = sext i32 %610 to i64
  %612 = getelementptr float, float* %607, i64 %611
  %613 = load float, float* %612, align 4
  %614 = fsub reassoc ninf nsz float %613, %65
  %615 = fmul reassoc ninf nsz float %614, %614
  %616 = fmul reassoc ninf nsz float %615, %25
  %617 = fsub reassoc ninf nsz float %27, %616
  %618 = tail call float @expf(float noundef %617) #1
  %619 = load float*, float** %34, align 8
  %620 = load i32, i32* %35, align 4
  %621 = mul i32 %620, %498
  %622 = add i32 %621, %194
  %623 = shl i32 %622, 1
  %624 = sext i32 %623 to i64
  %625 = getelementptr float, float* %619, i64 %624
  %626 = load float, float* %625, align 4
  %627 = getelementptr float, float* %625, i64 1
  %628 = load float, float* %627, align 4
  %629 = fmul reassoc ninf nsz float %626, %618
  %630 = fmul reassoc ninf nsz float %628, %618
  %631 = fadd reassoc ninf nsz float %604, %629
  %632 = fadd reassoc ninf nsz float %605, %630
  %633 = fadd reassoc ninf nsz float %606, %618
  %634 = add i32 %54, 2
  %635 = tail call i32 @llvm.smax.i32(i32 %634, i32 0)
  %636 = tail call i32 @llvm.smin.i32(i32 %70, i32 %635)
  %637 = load float*, float** %32, align 8
  %638 = load i32, i32* %33, align 4
  %639 = mul i32 %638, %636
  %640 = add i32 %639, %79
  %641 = sext i32 %640 to i64
  %642 = getelementptr float, float* %637, i64 %641
  %643 = load float, float* %642, align 4
  %644 = fsub reassoc ninf nsz float %643, %65
  %645 = fmul reassoc ninf nsz float %644, %644
  %646 = fmul reassoc ninf nsz float %645, %25
  %647 = fsub reassoc ninf nsz float %26, %646
  %648 = tail call float @expf(float noundef %647) #1
  %649 = load float*, float** %34, align 8
  %650 = load i32, i32* %35, align 4
  %651 = mul i32 %650, %636
  %652 = add i32 %651, %79
  %653 = shl i32 %652, 1
  %654 = sext i32 %653 to i64
  %655 = getelementptr float, float* %649, i64 %654
  %656 = load float, float* %655, align 4
  %657 = getelementptr float, float* %655, i64 1
  %658 = load float, float* %657, align 4
  %659 = fmul reassoc ninf nsz float %656, %648
  %660 = fmul reassoc ninf nsz float %658, %648
  %661 = fadd reassoc ninf nsz float %631, %659
  %662 = fadd reassoc ninf nsz float %632, %660
  %663 = fadd reassoc ninf nsz float %633, %648
  %664 = load float*, float** %32, align 8
  %665 = load i32, i32* %33, align 4
  %666 = mul i32 %665, %636
  %667 = add i32 %666, %105
  %668 = sext i32 %667 to i64
  %669 = getelementptr float, float* %664, i64 %668
  %670 = load float, float* %669, align 4
  %671 = fsub reassoc ninf nsz float %670, %65
  %672 = fmul reassoc ninf nsz float %671, %671
  %673 = fmul reassoc ninf nsz float %672, %25
  %674 = fsub reassoc ninf nsz float %27, %673
  %675 = tail call float @expf(float noundef %674) #1
  %676 = load float*, float** %34, align 8
  %677 = load i32, i32* %35, align 4
  %678 = mul i32 %677, %636
  %679 = add i32 %678, %105
  %680 = shl i32 %679, 1
  %681 = sext i32 %680 to i64
  %682 = getelementptr float, float* %676, i64 %681
  %683 = load float, float* %682, align 4
  %684 = getelementptr float, float* %682, i64 1
  %685 = load float, float* %684, align 4
  %686 = fmul reassoc ninf nsz float %683, %675
  %687 = fmul reassoc ninf nsz float %685, %675
  %688 = fadd reassoc ninf nsz float %661, %686
  %689 = fadd reassoc ninf nsz float %662, %687
  %690 = fadd reassoc ninf nsz float %663, %675
  %691 = load float*, float** %32, align 8
  %692 = load i32, i32* %33, align 4
  %693 = mul i32 %692, %636
  %694 = add i32 %693, %134
  %695 = sext i32 %694 to i64
  %696 = getelementptr float, float* %691, i64 %695
  %697 = load float, float* %696, align 4
  %698 = fsub reassoc ninf nsz float %697, %65
  %699 = fmul reassoc ninf nsz float %698, %698
  %700 = fmul reassoc ninf nsz float %699, %25
  %701 = fsub reassoc ninf nsz float %28, %700
  %702 = tail call float @expf(float noundef %701) #1
  %703 = load float*, float** %34, align 8
  %704 = load i32, i32* %35, align 4
  %705 = mul i32 %704, %636
  %706 = add i32 %705, %134
  %707 = shl i32 %706, 1
  %708 = sext i32 %707 to i64
  %709 = getelementptr float, float* %703, i64 %708
  %710 = load float, float* %709, align 4
  %711 = getelementptr float, float* %709, i64 1
  %712 = load float, float* %711, align 4
  %713 = fmul reassoc ninf nsz float %710, %702
  %714 = fmul reassoc ninf nsz float %712, %702
  %715 = fadd reassoc ninf nsz float %688, %713
  %716 = fadd reassoc ninf nsz float %689, %714
  %717 = fadd reassoc ninf nsz float %690, %702
  %718 = load float*, float** %32, align 8
  %719 = load i32, i32* %33, align 4
  %720 = mul i32 %719, %636
  %721 = add i32 %720, %164
  %722 = sext i32 %721 to i64
  %723 = getelementptr float, float* %718, i64 %722
  %724 = load float, float* %723, align 4
  %725 = fsub reassoc ninf nsz float %724, %65
  %726 = fmul reassoc ninf nsz float %725, %725
  %727 = fmul reassoc ninf nsz float %726, %25
  %728 = fsub reassoc ninf nsz float %27, %727
  %729 = tail call float @expf(float noundef %728) #1
  %730 = load float*, float** %34, align 8
  %731 = load i32, i32* %35, align 4
  %732 = mul i32 %731, %636
  %733 = add i32 %732, %164
  %734 = shl i32 %733, 1
  %735 = sext i32 %734 to i64
  %736 = getelementptr float, float* %730, i64 %735
  %737 = load float, float* %736, align 4
  %738 = getelementptr float, float* %736, i64 1
  %739 = load float, float* %738, align 4
  %740 = fmul reassoc ninf nsz float %737, %729
  %741 = fmul reassoc ninf nsz float %739, %729
  %742 = fadd reassoc ninf nsz float %715, %740
  %743 = fadd reassoc ninf nsz float %716, %741
  %744 = fadd reassoc ninf nsz float %717, %729
  %745 = load float*, float** %32, align 8
  %746 = load i32, i32* %33, align 4
  %747 = mul i32 %746, %636
  %748 = add i32 %747, %194
  %749 = sext i32 %748 to i64
  %750 = getelementptr float, float* %745, i64 %749
  %751 = load float, float* %750, align 4
  %752 = fsub reassoc ninf nsz float %751, %65
  %753 = fmul reassoc ninf nsz float %752, %752
  %754 = fmul reassoc ninf nsz float %753, %25
  %755 = fsub reassoc ninf nsz float %26, %754
  %756 = tail call float @expf(float noundef %755) #1
  %757 = load float*, float** %34, align 8
  %758 = load i32, i32* %35, align 4
  %759 = mul i32 %758, %636
  %760 = add i32 %759, %194
  %761 = shl i32 %760, 1
  %762 = sext i32 %761 to i64
  %763 = getelementptr float, float* %757, i64 %762
  %764 = load float, float* %763, align 4
  %765 = getelementptr float, float* %763, i64 1
  %766 = load float, float* %765, align 4
  %767 = fmul reassoc ninf nsz float %764, %756
  %768 = fmul reassoc ninf nsz float %766, %756
  %769 = fadd reassoc ninf nsz float %742, %767
  %770 = fadd reassoc ninf nsz float %743, %768
  %771 = fadd reassoc ninf nsz float %744, %756
  %772 = fdiv reassoc ninf nsz float %769, %771
  %773 = fdiv reassoc ninf nsz float %770, %771
  %774 = load float*, float** %37, align 8
  %775 = load i32, i32* %38, align 4
  %776 = sub i32 %775, %45
  %777 = shl i32 %776, 1
  %778 = mul i32 %777, %54
  %779 = add i32 %lsr.iv, %778
  %780 = sext i32 %779 to i64
  %781 = getelementptr float, float* %774, i64 %780
  store float %772, float* %781, align 4
  %782 = load float*, float** %37, align 8
  %783 = load i32, i32* %38, align 4
  %784 = sub i32 %783, %45
  %785 = shl i32 %784, 1
  %786 = mul i32 %785, %54
  %787 = add i32 %lsr.iv, %786
  %788 = add i32 %787, 1
  %789 = sext i32 %788 to i64
  %790 = getelementptr float, float* %782, i64 %789
  store float %773, float* %790, align 4
  %791 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %791
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
  %4 = alloca %struct.RuntimeContext.84, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.84**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.84*, %struct.RuntimeContext.84** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.84*, i8*, i32)*, void (%struct.RuntimeContext.84*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.84*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.84*, i8*)*, void (%struct.RuntimeContext.84*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.84* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.84* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.84, %struct.RuntimeContext.84* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.84* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.84*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.84* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
