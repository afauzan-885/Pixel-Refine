; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext*, void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { i8*, %struct.LLVMRuntime*, i32, i64* }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager*], [1024 x %struct.NodeManager*], [1024 x i8*], i8*, %struct.RandState*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { i8*, i8*, i64 }
%struct.ListManager = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime* }
%struct.NodeManager = type { %struct.LLVMRuntime*, i32, i32, i32, i32, %struct.ListManager*, %struct.ListManager*, %struct.ListManager*, i32 }
%struct.RandState = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_remap_kernel_vec3_c310_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 6
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 7
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_remap_kernel_vec3_c310_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext* %context, %struct.RuntimeContext** %4, align 8
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext*, i8*, i32)* @function_body, void (%struct.RuntimeContext*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext*, i8*)* null, void (%struct.RuntimeContext*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %25 = load i32, i32* %24, align 4
  %26 = add i32 %25, -1
  %27 = add i32 %23, -1
  %28 = icmp slt i32 %17, %19
  br i1 %28, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %29 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 1
  %36 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  %37 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %37, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.09 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %214, %for_loop_body ]
  %38 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %39 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %38, i64 0, i32 14
  %40 = load i8*, i8** %39, align 8
  %41 = getelementptr inbounds i8, i8* %40, i64 4
  %42 = bitcast i8* %41 to i32*
  %43 = load i32, i32* %42, align 4
  %44 = sdiv i32 %.09, %43
  %45 = mul i32 %44, %43
  %46 = xor i32 %43, %.09
  %47 = icmp slt i32 %46, 0
  %48 = icmp ne i32 %.09, 0
  %49 = icmp ne i32 %.09, %45
  %50 = and i1 %48, %47
  %51 = and i1 %50, %49
  %.neg4 = sext i1 %51 to i32
  %52 = add i32 %44, %.neg4
  %53 = load float*, float** %29, align 8
  %54 = load i32, i32* %30, align 4
  %55 = sub i32 %54, %43
  %56 = mul i32 %55, %52
  %57 = add i32 %.09, %56
  %58 = sext i32 %57 to i64
  %59 = getelementptr float, float* %53, i64 %58
  %60 = load float, float* %59, align 4
  %61 = load float*, float** %31, align 8
  %62 = load i32, i32* %32, align 4
  %63 = sub i32 %62, %43
  %64 = mul i32 %63, %52
  %65 = add i32 %.09, %64
  %66 = sext i32 %65 to i64
  %67 = getelementptr float, float* %61, i64 %66
  %68 = load float, float* %67, align 4
  %69 = tail call reassoc ninf nsz float @llvm.floor.f32(float %60)
  %70 = fptosi float %69 to i32
  %71 = tail call reassoc ninf nsz float @llvm.floor.f32(float %68)
  %72 = fptosi float %71 to i32
  %73 = sitofp i32 %70 to float
  %74 = fsub reassoc ninf nsz float %60, %73
  %75 = sitofp i32 %72 to float
  %76 = fsub reassoc ninf nsz float %68, %75
  %77 = tail call i32 @llvm.abs.i32(i32 %70, i1 true)
  %78 = sub i32 %77, %26
  %79 = tail call i32 @llvm.smax.i32(i32 %78, i32 0)
  %.neg5 = mul i32 %79, -2
  %80 = add i32 %.neg5, %77
  %81 = tail call i32 @llvm.smax.i32(i32 %80, i32 0)
  %82 = tail call i32 @llvm.smin.i32(i32 %26, i32 %81)
  %83 = tail call i32 @llvm.abs.i32(i32 %72, i1 true)
  %84 = sub i32 %83, %27
  %85 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %.neg6 = mul i32 %85, -2
  %86 = add i32 %.neg6, %83
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = tail call i32 @llvm.smin.i32(i32 %27, i32 %87)
  %89 = add i32 %70, 1
  %90 = tail call i32 @llvm.abs.i32(i32 %89, i1 true)
  %91 = sub i32 %90, %26
  %92 = tail call i32 @llvm.smax.i32(i32 %91, i32 0)
  %.neg7 = mul i32 %92, -2
  %93 = add i32 %.neg7, %90
  %94 = tail call i32 @llvm.smax.i32(i32 %93, i32 0)
  %95 = tail call i32 @llvm.smin.i32(i32 %26, i32 %94)
  %96 = add i32 %72, 1
  %97 = tail call i32 @llvm.abs.i32(i32 %96, i1 true)
  %98 = sub i32 %97, %27
  %99 = tail call i32 @llvm.smax.i32(i32 %98, i32 0)
  %.neg8 = mul i32 %99, -2
  %100 = add i32 %.neg8, %97
  %101 = tail call i32 @llvm.smax.i32(i32 %100, i32 0)
  %102 = tail call i32 @llvm.smin.i32(i32 %27, i32 %101)
  %103 = load float*, float** %33, align 8
  %104 = load i32, i32* %34, align 4
  %105 = mul i32 %88, %104
  %106 = add i32 %105, %82
  %107 = mul i32 %106, 3
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, float* %103, i64 %108
  %110 = load float, float* %109, align 4
  %111 = add i32 %107, 1
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, float* %103, i64 %112
  %114 = load float, float* %113, align 4
  %115 = add i32 %107, 2
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %103, i64 %116
  %118 = load float, float* %117, align 4
  %119 = add i32 %105, %95
  %120 = mul i32 %119, 3
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, float* %103, i64 %121
  %123 = load float, float* %122, align 4
  %124 = add i32 %120, 1
  %125 = sext i32 %124 to i64
  %126 = getelementptr float, float* %103, i64 %125
  %127 = load float, float* %126, align 4
  %128 = add i32 %120, 2
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %103, i64 %129
  %131 = load float, float* %130, align 4
  %132 = mul i32 %102, %104
  %133 = add i32 %132, %82
  %134 = mul i32 %133, 3
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %103, i64 %135
  %137 = load float, float* %136, align 4
  %138 = add i32 %134, 1
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, float* %103, i64 %139
  %141 = load float, float* %140, align 4
  %142 = add i32 %134, 2
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %103, i64 %143
  %145 = load float, float* %144, align 4
  %146 = add i32 %132, %95
  %147 = mul i32 %146, 3
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %103, i64 %148
  %150 = load float, float* %149, align 4
  %151 = add i32 %147, 1
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, float* %103, i64 %152
  %154 = load float, float* %153, align 4
  %155 = add i32 %147, 2
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, float* %103, i64 %156
  %158 = load float, float* %157, align 4
  %159 = fsub reassoc ninf nsz float 1.000000e+00, %74
  %160 = fmul reassoc ninf nsz float %110, %159
  %161 = fmul reassoc ninf nsz float %114, %159
  %162 = fmul reassoc ninf nsz float %118, %159
  %163 = fmul reassoc ninf nsz float %123, %74
  %164 = fmul reassoc ninf nsz float %127, %74
  %165 = fmul reassoc ninf nsz float %131, %74
  %166 = fadd reassoc ninf nsz float %163, %160
  %167 = fadd reassoc ninf nsz float %164, %161
  %168 = fadd reassoc ninf nsz float %165, %162
  %169 = fmul reassoc ninf nsz float %137, %159
  %170 = fmul reassoc ninf nsz float %141, %159
  %171 = fmul reassoc ninf nsz float %145, %159
  %172 = fmul reassoc ninf nsz float %150, %74
  %173 = fmul reassoc ninf nsz float %154, %74
  %174 = fmul reassoc ninf nsz float %158, %74
  %175 = fadd reassoc ninf nsz float %172, %169
  %176 = fadd reassoc ninf nsz float %173, %170
  %177 = fadd reassoc ninf nsz float %174, %171
  %178 = fsub reassoc ninf nsz float 1.000000e+00, %76
  %179 = fmul reassoc ninf nsz float %166, %178
  %180 = fmul reassoc ninf nsz float %167, %178
  %181 = fmul reassoc ninf nsz float %168, %178
  %182 = fmul reassoc ninf nsz float %175, %76
  %183 = fmul reassoc ninf nsz float %176, %76
  %184 = fmul reassoc ninf nsz float %177, %76
  %185 = fadd reassoc ninf nsz float %182, %179
  %186 = fadd reassoc ninf nsz float %183, %180
  %187 = fadd reassoc ninf nsz float %184, %181
  %188 = load float*, float** %35, align 8
  %189 = load i32, i32* %36, align 4
  %190 = sub i32 %189, %43
  %191 = mul i32 %190, 3
  %192 = mul i32 %191, %52
  %193 = add i32 %lsr.iv, %192
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %188, i64 %194
  store float %185, float* %195, align 4
  %196 = load float*, float** %35, align 8
  %197 = load i32, i32* %36, align 4
  %198 = sub i32 %197, %43
  %199 = mul i32 %198, 3
  %200 = mul i32 %199, %52
  %201 = add i32 %lsr.iv, %200
  %202 = add i32 %201, 1
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, float* %196, i64 %203
  store float %186, float* %204, align 4
  %205 = load float*, float** %35, align 8
  %206 = load i32, i32* %36, align 4
  %207 = sub i32 %206, %43
  %208 = mul i32 %207, 3
  %209 = mul i32 %208, %52
  %210 = add i32 %lsr.iv, %209
  %211 = add i32 %210, 2
  %212 = sext i32 %211 to i64
  %213 = getelementptr float, float* %205, i64 %212
  store float %187, float* %213, align 4
  %214 = add nsw i32 %.09, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %214
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
  %4 = alloca %struct.RuntimeContext, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext**
  %.sroa.0.0.copyload = load %struct.RuntimeContext*, %struct.RuntimeContext** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext*, i8*, i32)*, void (%struct.RuntimeContext*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext*, i8*)*, void (%struct.RuntimeContext*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.abs.i32(i32, i1 immarg) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }

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
