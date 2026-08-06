; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { i8*, %struct.LLVMRuntime.5*, i32, i64* }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.2*], [1024 x %struct.NodeManager.3*], [1024 x i8*], i8*, %struct.RandState.4*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { i8*, i8*, i64 }
%struct.ListManager.2 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.5* }
%struct.NodeManager.3 = type { %struct.LLVMRuntime.5*, i32, i32, i32, i32, %struct.ListManager.2*, %struct.ListManager.2*, %struct.ListManager.2*, i32 }
%struct.RandState.4 = type { i32, i32, i32, i32, i32 }
%struct.range_task_helper_context = type { %struct.RuntimeContext.6*, void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*)*, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_jbf_1ch_r1_c698_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_jbf_1ch_r1_c698_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast %struct.range_task_helper_context* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 0
  store %struct.RuntimeContext.6* %context, %struct.RuntimeContext.6** %4, align 8
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.6*, i8*, i32)* @function_body, void (%struct.RuntimeContext.6*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
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
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %288, %for_loop_body ]
  %36 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %37 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %36, i64 0, i32 14
  %38 = load i8*, i8** %37, align 8
  %39 = getelementptr inbounds i8, i8* %38, i64 4
  %40 = bitcast i8* %39 to i32*
  %41 = load i32, i32* %40, align 4
  %42 = sdiv i32 %.05, %41
  %43 = mul i32 %42, %41
  %44 = xor i32 %41, %.05
  %45 = icmp slt i32 %44, 0
  %46 = icmp ne i32 %.05, 0
  %47 = icmp ne i32 %.05, %43
  %48 = and i1 %46, %45
  %49 = and i1 %48, %47
  %.neg4 = sext i1 %49 to i32
  %50 = add i32 %42, %.neg4
  %51 = mul i32 %41, -1
  %52 = mul i32 %51, %50
  %53 = add i32 %.05, %52
  %54 = load float*, float** %29, align 8
  %55 = load i32, i32* %30, align 4
  %56 = sub i32 %55, %41
  %57 = mul i32 %56, %50
  %58 = add i32 %.05, %57
  %59 = sext i32 %58 to i64
  %60 = getelementptr float, float* %54, i64 %59
  %61 = load float, float* %60, align 4
  %62 = add i32 %50, -1
  %63 = getelementptr inbounds i8, i8* %38, i64 8
  %64 = bitcast i8* %63 to i32*
  %65 = load i32, i32* %64, align 4
  %66 = add i32 %65, -1
  %67 = tail call i32 @llvm.smax.i32(i32 %62, i32 0)
  %68 = tail call i32 @llvm.smin.i32(i32 %66, i32 %67)
  %69 = add i32 %53, -1
  %70 = getelementptr inbounds i8, i8* %38, i64 12
  %71 = bitcast i8* %70 to i32*
  %72 = load i32, i32* %71, align 4
  %73 = add i32 %72, -1
  %74 = tail call i32 @llvm.smax.i32(i32 %69, i32 0)
  %75 = tail call i32 @llvm.smin.i32(i32 %73, i32 %74)
  %76 = mul i32 %68, %55
  %77 = add i32 %75, %76
  %78 = sext i32 %77 to i64
  %79 = getelementptr float, float* %54, i64 %78
  %80 = load float, float* %79, align 4
  %81 = fsub reassoc ninf nsz float %80, %61
  %82 = fmul reassoc ninf nsz float %81, %81
  %83 = fmul reassoc ninf nsz float %82, %25
  %84 = fsub reassoc ninf nsz float %26, %83
  %85 = tail call float @expf(float noundef %84) #1
  %86 = load float*, float** %31, align 8
  %87 = load i32, i32* %32, align 4
  %88 = mul i32 %87, %68
  %89 = add i32 %88, %75
  %90 = sext i32 %89 to i64
  %91 = getelementptr float, float* %86, i64 %90
  %92 = load float, float* %91, align 4
  %93 = fmul reassoc ninf nsz float %92, %85
  %94 = fadd reassoc ninf nsz float %85, 0x3D71979980000000
  %95 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %73, i32 %95)
  %97 = load float*, float** %29, align 8
  %98 = load i32, i32* %30, align 4
  %99 = mul i32 %98, %68
  %100 = add i32 %99, %96
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %97, i64 %101
  %103 = load float, float* %102, align 4
  %104 = fsub reassoc ninf nsz float %103, %61
  %105 = fmul reassoc ninf nsz float %104, %104
  %106 = fmul reassoc ninf nsz float %105, %25
  %107 = fsub reassoc ninf nsz float %27, %106
  %108 = tail call float @expf(float noundef %107) #1
  %109 = load float*, float** %31, align 8
  %110 = load i32, i32* %32, align 4
  %111 = mul i32 %110, %68
  %112 = add i32 %111, %96
  %113 = sext i32 %112 to i64
  %114 = getelementptr float, float* %109, i64 %113
  %115 = load float, float* %114, align 4
  %116 = fmul reassoc ninf nsz float %115, %108
  %117 = fadd reassoc ninf nsz float %116, %93
  %118 = fadd reassoc ninf nsz float %94, %108
  %119 = add i32 %53, 1
  %120 = tail call i32 @llvm.smax.i32(i32 %119, i32 0)
  %121 = tail call i32 @llvm.smin.i32(i32 %73, i32 %120)
  %122 = load float*, float** %29, align 8
  %123 = load i32, i32* %30, align 4
  %124 = mul i32 %123, %68
  %125 = add i32 %124, %121
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, float* %122, i64 %126
  %128 = load float, float* %127, align 4
  %129 = fsub reassoc ninf nsz float %128, %61
  %130 = fmul reassoc ninf nsz float %129, %129
  %131 = fmul reassoc ninf nsz float %130, %25
  %132 = fsub reassoc ninf nsz float %26, %131
  %133 = tail call float @expf(float noundef %132) #1
  %134 = load float*, float** %31, align 8
  %135 = load i32, i32* %32, align 4
  %136 = mul i32 %135, %68
  %137 = add i32 %136, %121
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %134, i64 %138
  %140 = load float, float* %139, align 4
  %141 = fmul reassoc ninf nsz float %140, %133
  %142 = fadd reassoc ninf nsz float %117, %141
  %143 = fadd reassoc ninf nsz float %118, %133
  %144 = tail call i32 @llvm.smax.i32(i32 %50, i32 0)
  %145 = tail call i32 @llvm.smin.i32(i32 %66, i32 %144)
  %146 = load float*, float** %29, align 8
  %147 = load i32, i32* %30, align 4
  %148 = mul i32 %147, %145
  %149 = add i32 %148, %75
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, float* %146, i64 %150
  %152 = load float, float* %151, align 4
  %153 = fsub reassoc ninf nsz float %152, %61
  %154 = fmul reassoc ninf nsz float %153, %153
  %155 = fmul reassoc ninf nsz float %154, %25
  %156 = fsub reassoc ninf nsz float %27, %155
  %157 = tail call float @expf(float noundef %156) #1
  %158 = load float*, float** %31, align 8
  %159 = load i32, i32* %32, align 4
  %160 = mul i32 %159, %145
  %161 = add i32 %160, %75
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, float* %158, i64 %162
  %164 = load float, float* %163, align 4
  %165 = fmul reassoc ninf nsz float %164, %157
  %166 = fadd reassoc ninf nsz float %142, %165
  %167 = fadd reassoc ninf nsz float %143, %157
  %168 = load float*, float** %29, align 8
  %169 = load i32, i32* %30, align 4
  %170 = mul i32 %169, %145
  %171 = add i32 %170, %96
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %168, i64 %172
  %174 = load float, float* %173, align 4
  %175 = fsub reassoc ninf nsz float %174, %61
  %176 = fmul reassoc ninf nsz float %175, %175
  %177 = fmul reassoc ninf nsz float %176, %33
  %178 = tail call float @expf(float noundef %177) #1
  %179 = load float*, float** %31, align 8
  %180 = load i32, i32* %32, align 4
  %181 = mul i32 %180, %145
  %182 = add i32 %181, %96
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, float* %179, i64 %183
  %185 = load float, float* %184, align 4
  %186 = fmul reassoc ninf nsz float %185, %178
  %187 = fadd reassoc ninf nsz float %166, %186
  %188 = fadd reassoc ninf nsz float %167, %178
  %189 = load float*, float** %29, align 8
  %190 = load i32, i32* %30, align 4
  %191 = mul i32 %190, %145
  %192 = add i32 %191, %121
  %193 = sext i32 %192 to i64
  %194 = getelementptr float, float* %189, i64 %193
  %195 = load float, float* %194, align 4
  %196 = fsub reassoc ninf nsz float %195, %61
  %197 = fmul reassoc ninf nsz float %196, %196
  %198 = fmul reassoc ninf nsz float %197, %25
  %199 = fsub reassoc ninf nsz float %27, %198
  %200 = tail call float @expf(float noundef %199) #1
  %201 = load float*, float** %31, align 8
  %202 = load i32, i32* %32, align 4
  %203 = mul i32 %202, %145
  %204 = add i32 %203, %121
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %201, i64 %205
  %207 = load float, float* %206, align 4
  %208 = fmul reassoc ninf nsz float %207, %200
  %209 = fadd reassoc ninf nsz float %187, %208
  %210 = fadd reassoc ninf nsz float %188, %200
  %211 = add i32 %50, 1
  %212 = tail call i32 @llvm.smax.i32(i32 %211, i32 0)
  %213 = tail call i32 @llvm.smin.i32(i32 %66, i32 %212)
  %214 = load float*, float** %29, align 8
  %215 = load i32, i32* %30, align 4
  %216 = mul i32 %215, %213
  %217 = add i32 %216, %75
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, float* %214, i64 %218
  %220 = load float, float* %219, align 4
  %221 = fsub reassoc ninf nsz float %220, %61
  %222 = fmul reassoc ninf nsz float %221, %221
  %223 = fmul reassoc ninf nsz float %222, %25
  %224 = fsub reassoc ninf nsz float %26, %223
  %225 = tail call float @expf(float noundef %224) #1
  %226 = load float*, float** %31, align 8
  %227 = load i32, i32* %32, align 4
  %228 = mul i32 %227, %213
  %229 = add i32 %228, %75
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, float* %226, i64 %230
  %232 = load float, float* %231, align 4
  %233 = fmul reassoc ninf nsz float %232, %225
  %234 = fadd reassoc ninf nsz float %209, %233
  %235 = fadd reassoc ninf nsz float %210, %225
  %236 = load float*, float** %29, align 8
  %237 = load i32, i32* %30, align 4
  %238 = mul i32 %237, %213
  %239 = add i32 %238, %96
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %236, i64 %240
  %242 = load float, float* %241, align 4
  %243 = fsub reassoc ninf nsz float %242, %61
  %244 = fmul reassoc ninf nsz float %243, %243
  %245 = fmul reassoc ninf nsz float %244, %25
  %246 = fsub reassoc ninf nsz float %27, %245
  %247 = tail call float @expf(float noundef %246) #1
  %248 = load float*, float** %31, align 8
  %249 = load i32, i32* %32, align 4
  %250 = mul i32 %249, %213
  %251 = add i32 %250, %96
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, float* %248, i64 %252
  %254 = load float, float* %253, align 4
  %255 = fmul reassoc ninf nsz float %254, %247
  %256 = fadd reassoc ninf nsz float %234, %255
  %257 = fadd reassoc ninf nsz float %235, %247
  %258 = load float*, float** %29, align 8
  %259 = load i32, i32* %30, align 4
  %260 = mul i32 %259, %213
  %261 = add i32 %260, %121
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, float* %258, i64 %262
  %264 = load float, float* %263, align 4
  %265 = fsub reassoc ninf nsz float %264, %61
  %266 = fmul reassoc ninf nsz float %265, %265
  %267 = fmul reassoc ninf nsz float %266, %25
  %268 = fsub reassoc ninf nsz float %26, %267
  %269 = tail call float @expf(float noundef %268) #1
  %270 = load float*, float** %31, align 8
  %271 = load i32, i32* %32, align 4
  %272 = mul i32 %271, %213
  %273 = add i32 %272, %121
  %274 = sext i32 %273 to i64
  %275 = getelementptr float, float* %270, i64 %274
  %276 = load float, float* %275, align 4
  %277 = fmul reassoc ninf nsz float %276, %269
  %278 = fadd reassoc ninf nsz float %256, %277
  %279 = fadd reassoc ninf nsz float %257, %269
  %280 = fdiv reassoc ninf nsz float %278, %279
  %281 = load float*, float** %34, align 8
  %282 = load i32, i32* %35, align 4
  %283 = sub i32 %282, %41
  %284 = mul i32 %283, %50
  %285 = add i32 %.05, %284
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, float* %281, i64 %286
  store float %280, float* %287, align 4
  %288 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %288
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
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.6**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.6*, %struct.RuntimeContext.6** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.6* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.6* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
