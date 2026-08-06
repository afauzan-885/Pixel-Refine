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
define void @_jbf_1ch_r2_c700_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }* %11, i64 0, i32 4
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_jbf_1ch_r2_c700_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, float, float }**
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
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %655, %for_loop_body ]
  %39 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %40 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %39, i64 0, i32 14
  %41 = load i8*, i8** %40, align 8
  %42 = getelementptr inbounds i8, i8* %41, i64 4
  %43 = bitcast i8* %42 to i32*
  %44 = load i32, i32* %43, align 4
  %45 = sdiv i32 %.05, %44
  %46 = mul i32 %45, %44
  %47 = xor i32 %44, %.05
  %48 = icmp slt i32 %47, 0
  %49 = icmp ne i32 %.05, 0
  %50 = icmp ne i32 %.05, %46
  %51 = and i1 %49, %48
  %52 = and i1 %51, %50
  %.neg4 = sext i1 %52 to i32
  %53 = add i32 %45, %.neg4
  %54 = mul i32 %44, -1
  %55 = mul i32 %54, %53
  %56 = add i32 %.05, %55
  %57 = load float*, float** %32, align 8
  %58 = load i32, i32* %33, align 4
  %59 = sub i32 %58, %44
  %60 = mul i32 %59, %53
  %61 = add i32 %.05, %60
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, float* %57, i64 %62
  %64 = load float, float* %63, align 4
  %65 = add i32 %53, -2
  %66 = getelementptr inbounds i8, i8* %41, i64 8
  %67 = bitcast i8* %66 to i32*
  %68 = load i32, i32* %67, align 4
  %69 = add i32 %68, -1
  %70 = tail call i32 @llvm.smax.i32(i32 %65, i32 0)
  %71 = tail call i32 @llvm.smin.i32(i32 %69, i32 %70)
  %72 = add i32 %56, -2
  %73 = getelementptr inbounds i8, i8* %41, i64 12
  %74 = bitcast i8* %73 to i32*
  %75 = load i32, i32* %74, align 4
  %76 = add i32 %75, -1
  %77 = tail call i32 @llvm.smax.i32(i32 %72, i32 0)
  %78 = tail call i32 @llvm.smin.i32(i32 %76, i32 %77)
  %79 = mul i32 %71, %58
  %80 = add i32 %78, %79
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %57, i64 %81
  %83 = load float, float* %82, align 4
  %84 = fsub reassoc ninf nsz float %83, %64
  %85 = fmul reassoc ninf nsz float %84, %84
  %86 = fmul reassoc ninf nsz float %85, %25
  %87 = fsub reassoc ninf nsz float %26, %86
  %88 = tail call float @expf(float noundef %87) #1
  %89 = load float*, float** %34, align 8
  %90 = load i32, i32* %35, align 4
  %91 = mul i32 %90, %71
  %92 = add i32 %91, %78
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, float* %89, i64 %93
  %95 = load float, float* %94, align 4
  %96 = fmul reassoc ninf nsz float %95, %88
  %97 = fadd reassoc ninf nsz float %88, 0x3D71979980000000
  %98 = add i32 %56, -1
  %99 = tail call i32 @llvm.smax.i32(i32 %98, i32 0)
  %100 = tail call i32 @llvm.smin.i32(i32 %76, i32 %99)
  %101 = load float*, float** %32, align 8
  %102 = load i32, i32* %33, align 4
  %103 = mul i32 %102, %71
  %104 = add i32 %103, %100
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, float* %101, i64 %105
  %107 = load float, float* %106, align 4
  %108 = fsub reassoc ninf nsz float %107, %64
  %109 = fmul reassoc ninf nsz float %108, %108
  %110 = fmul reassoc ninf nsz float %109, %25
  %111 = fsub reassoc ninf nsz float %27, %110
  %112 = tail call float @expf(float noundef %111) #1
  %113 = load float*, float** %34, align 8
  %114 = load i32, i32* %35, align 4
  %115 = mul i32 %114, %71
  %116 = add i32 %115, %100
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, float* %113, i64 %117
  %119 = load float, float* %118, align 4
  %120 = fmul reassoc ninf nsz float %119, %112
  %121 = fadd reassoc ninf nsz float %120, %96
  %122 = fadd reassoc ninf nsz float %97, %112
  %123 = tail call i32 @llvm.smax.i32(i32 %56, i32 0)
  %124 = tail call i32 @llvm.smin.i32(i32 %76, i32 %123)
  %125 = load float*, float** %32, align 8
  %126 = load i32, i32* %33, align 4
  %127 = mul i32 %126, %71
  %128 = add i32 %127, %124
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %125, i64 %129
  %131 = load float, float* %130, align 4
  %132 = fsub reassoc ninf nsz float %131, %64
  %133 = fmul reassoc ninf nsz float %132, %132
  %134 = fmul reassoc ninf nsz float %133, %25
  %135 = fsub reassoc ninf nsz float %28, %134
  %136 = tail call float @expf(float noundef %135) #1
  %137 = load float*, float** %34, align 8
  %138 = load i32, i32* %35, align 4
  %139 = mul i32 %138, %71
  %140 = add i32 %139, %124
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %137, i64 %141
  %143 = load float, float* %142, align 4
  %144 = fmul reassoc ninf nsz float %143, %136
  %145 = fadd reassoc ninf nsz float %121, %144
  %146 = fadd reassoc ninf nsz float %122, %136
  %147 = add i32 %56, 1
  %148 = tail call i32 @llvm.smax.i32(i32 %147, i32 0)
  %149 = tail call i32 @llvm.smin.i32(i32 %76, i32 %148)
  %150 = load float*, float** %32, align 8
  %151 = load i32, i32* %33, align 4
  %152 = mul i32 %151, %71
  %153 = add i32 %152, %149
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %150, i64 %154
  %156 = load float, float* %155, align 4
  %157 = fsub reassoc ninf nsz float %156, %64
  %158 = fmul reassoc ninf nsz float %157, %157
  %159 = fmul reassoc ninf nsz float %158, %25
  %160 = fsub reassoc ninf nsz float %27, %159
  %161 = tail call float @expf(float noundef %160) #1
  %162 = load float*, float** %34, align 8
  %163 = load i32, i32* %35, align 4
  %164 = mul i32 %163, %71
  %165 = add i32 %164, %149
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, float* %162, i64 %166
  %168 = load float, float* %167, align 4
  %169 = fmul reassoc ninf nsz float %168, %161
  %170 = fadd reassoc ninf nsz float %145, %169
  %171 = fadd reassoc ninf nsz float %146, %161
  %172 = add i32 %56, 2
  %173 = tail call i32 @llvm.smax.i32(i32 %172, i32 0)
  %174 = tail call i32 @llvm.smin.i32(i32 %76, i32 %173)
  %175 = load float*, float** %32, align 8
  %176 = load i32, i32* %33, align 4
  %177 = mul i32 %176, %71
  %178 = add i32 %177, %174
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, float* %175, i64 %179
  %181 = load float, float* %180, align 4
  %182 = fsub reassoc ninf nsz float %181, %64
  %183 = fmul reassoc ninf nsz float %182, %182
  %184 = fmul reassoc ninf nsz float %183, %25
  %185 = fsub reassoc ninf nsz float %26, %184
  %186 = tail call float @expf(float noundef %185) #1
  %187 = load float*, float** %34, align 8
  %188 = load i32, i32* %35, align 4
  %189 = mul i32 %188, %71
  %190 = add i32 %189, %174
  %191 = sext i32 %190 to i64
  %192 = getelementptr float, float* %187, i64 %191
  %193 = load float, float* %192, align 4
  %194 = fmul reassoc ninf nsz float %193, %186
  %195 = fadd reassoc ninf nsz float %170, %194
  %196 = fadd reassoc ninf nsz float %171, %186
  %197 = add i32 %53, -1
  %198 = tail call i32 @llvm.smax.i32(i32 %197, i32 0)
  %199 = tail call i32 @llvm.smin.i32(i32 %69, i32 %198)
  %200 = load float*, float** %32, align 8
  %201 = load i32, i32* %33, align 4
  %202 = mul i32 %201, %199
  %203 = add i32 %202, %78
  %204 = sext i32 %203 to i64
  %205 = getelementptr float, float* %200, i64 %204
  %206 = load float, float* %205, align 4
  %207 = fsub reassoc ninf nsz float %206, %64
  %208 = fmul reassoc ninf nsz float %207, %207
  %209 = fmul reassoc ninf nsz float %208, %25
  %210 = fsub reassoc ninf nsz float %27, %209
  %211 = tail call float @expf(float noundef %210) #1
  %212 = load float*, float** %34, align 8
  %213 = load i32, i32* %35, align 4
  %214 = mul i32 %213, %199
  %215 = add i32 %214, %78
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, float* %212, i64 %216
  %218 = load float, float* %217, align 4
  %219 = fmul reassoc ninf nsz float %218, %211
  %220 = fadd reassoc ninf nsz float %195, %219
  %221 = fadd reassoc ninf nsz float %196, %211
  %222 = load float*, float** %32, align 8
  %223 = load i32, i32* %33, align 4
  %224 = mul i32 %223, %199
  %225 = add i32 %224, %100
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, float* %222, i64 %226
  %228 = load float, float* %227, align 4
  %229 = fsub reassoc ninf nsz float %228, %64
  %230 = fmul reassoc ninf nsz float %229, %229
  %231 = fmul reassoc ninf nsz float %230, %25
  %232 = fsub reassoc ninf nsz float %29, %231
  %233 = tail call float @expf(float noundef %232) #1
  %234 = load float*, float** %34, align 8
  %235 = load i32, i32* %35, align 4
  %236 = mul i32 %235, %199
  %237 = add i32 %236, %100
  %238 = sext i32 %237 to i64
  %239 = getelementptr float, float* %234, i64 %238
  %240 = load float, float* %239, align 4
  %241 = fmul reassoc ninf nsz float %240, %233
  %242 = fadd reassoc ninf nsz float %220, %241
  %243 = fadd reassoc ninf nsz float %221, %233
  %244 = load float*, float** %32, align 8
  %245 = load i32, i32* %33, align 4
  %246 = mul i32 %245, %199
  %247 = add i32 %246, %124
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, float* %244, i64 %248
  %250 = load float, float* %249, align 4
  %251 = fsub reassoc ninf nsz float %250, %64
  %252 = fmul reassoc ninf nsz float %251, %251
  %253 = fmul reassoc ninf nsz float %252, %25
  %254 = fsub reassoc ninf nsz float %30, %253
  %255 = tail call float @expf(float noundef %254) #1
  %256 = load float*, float** %34, align 8
  %257 = load i32, i32* %35, align 4
  %258 = mul i32 %257, %199
  %259 = add i32 %258, %124
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, float* %256, i64 %260
  %262 = load float, float* %261, align 4
  %263 = fmul reassoc ninf nsz float %262, %255
  %264 = fadd reassoc ninf nsz float %242, %263
  %265 = fadd reassoc ninf nsz float %243, %255
  %266 = load float*, float** %32, align 8
  %267 = load i32, i32* %33, align 4
  %268 = mul i32 %267, %199
  %269 = add i32 %268, %149
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, float* %266, i64 %270
  %272 = load float, float* %271, align 4
  %273 = fsub reassoc ninf nsz float %272, %64
  %274 = fmul reassoc ninf nsz float %273, %273
  %275 = fmul reassoc ninf nsz float %274, %25
  %276 = fsub reassoc ninf nsz float %29, %275
  %277 = tail call float @expf(float noundef %276) #1
  %278 = load float*, float** %34, align 8
  %279 = load i32, i32* %35, align 4
  %280 = mul i32 %279, %199
  %281 = add i32 %280, %149
  %282 = sext i32 %281 to i64
  %283 = getelementptr float, float* %278, i64 %282
  %284 = load float, float* %283, align 4
  %285 = fmul reassoc ninf nsz float %284, %277
  %286 = fadd reassoc ninf nsz float %264, %285
  %287 = fadd reassoc ninf nsz float %265, %277
  %288 = load float*, float** %32, align 8
  %289 = load i32, i32* %33, align 4
  %290 = mul i32 %289, %199
  %291 = add i32 %290, %174
  %292 = sext i32 %291 to i64
  %293 = getelementptr float, float* %288, i64 %292
  %294 = load float, float* %293, align 4
  %295 = fsub reassoc ninf nsz float %294, %64
  %296 = fmul reassoc ninf nsz float %295, %295
  %297 = fmul reassoc ninf nsz float %296, %25
  %298 = fsub reassoc ninf nsz float %27, %297
  %299 = tail call float @expf(float noundef %298) #1
  %300 = load float*, float** %34, align 8
  %301 = load i32, i32* %35, align 4
  %302 = mul i32 %301, %199
  %303 = add i32 %302, %174
  %304 = sext i32 %303 to i64
  %305 = getelementptr float, float* %300, i64 %304
  %306 = load float, float* %305, align 4
  %307 = fmul reassoc ninf nsz float %306, %299
  %308 = fadd reassoc ninf nsz float %286, %307
  %309 = fadd reassoc ninf nsz float %287, %299
  %310 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %311 = tail call i32 @llvm.smin.i32(i32 %69, i32 %310)
  %312 = load float*, float** %32, align 8
  %313 = load i32, i32* %33, align 4
  %314 = mul i32 %313, %311
  %315 = add i32 %314, %78
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, float* %312, i64 %316
  %318 = load float, float* %317, align 4
  %319 = fsub reassoc ninf nsz float %318, %64
  %320 = fmul reassoc ninf nsz float %319, %319
  %321 = fmul reassoc ninf nsz float %320, %25
  %322 = fsub reassoc ninf nsz float %28, %321
  %323 = tail call float @expf(float noundef %322) #1
  %324 = load float*, float** %34, align 8
  %325 = load i32, i32* %35, align 4
  %326 = mul i32 %325, %311
  %327 = add i32 %326, %78
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, float* %324, i64 %328
  %330 = load float, float* %329, align 4
  %331 = fmul reassoc ninf nsz float %330, %323
  %332 = fadd reassoc ninf nsz float %308, %331
  %333 = fadd reassoc ninf nsz float %309, %323
  %334 = load float*, float** %32, align 8
  %335 = load i32, i32* %33, align 4
  %336 = mul i32 %335, %311
  %337 = add i32 %336, %100
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, float* %334, i64 %338
  %340 = load float, float* %339, align 4
  %341 = fsub reassoc ninf nsz float %340, %64
  %342 = fmul reassoc ninf nsz float %341, %341
  %343 = fmul reassoc ninf nsz float %342, %25
  %344 = fsub reassoc ninf nsz float %30, %343
  %345 = tail call float @expf(float noundef %344) #1
  %346 = load float*, float** %34, align 8
  %347 = load i32, i32* %35, align 4
  %348 = mul i32 %347, %311
  %349 = add i32 %348, %100
  %350 = sext i32 %349 to i64
  %351 = getelementptr float, float* %346, i64 %350
  %352 = load float, float* %351, align 4
  %353 = fmul reassoc ninf nsz float %352, %345
  %354 = fadd reassoc ninf nsz float %332, %353
  %355 = fadd reassoc ninf nsz float %333, %345
  %356 = load float*, float** %32, align 8
  %357 = load i32, i32* %33, align 4
  %358 = mul i32 %357, %311
  %359 = add i32 %358, %124
  %360 = sext i32 %359 to i64
  %361 = getelementptr float, float* %356, i64 %360
  %362 = load float, float* %361, align 4
  %363 = fsub reassoc ninf nsz float %362, %64
  %364 = fmul reassoc ninf nsz float %363, %363
  %365 = fmul reassoc ninf nsz float %364, %36
  %366 = tail call float @expf(float noundef %365) #1
  %367 = load float*, float** %34, align 8
  %368 = load i32, i32* %35, align 4
  %369 = mul i32 %368, %311
  %370 = add i32 %369, %124
  %371 = sext i32 %370 to i64
  %372 = getelementptr float, float* %367, i64 %371
  %373 = load float, float* %372, align 4
  %374 = fmul reassoc ninf nsz float %373, %366
  %375 = fadd reassoc ninf nsz float %354, %374
  %376 = fadd reassoc ninf nsz float %355, %366
  %377 = load float*, float** %32, align 8
  %378 = load i32, i32* %33, align 4
  %379 = mul i32 %378, %311
  %380 = add i32 %379, %149
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, float* %377, i64 %381
  %383 = load float, float* %382, align 4
  %384 = fsub reassoc ninf nsz float %383, %64
  %385 = fmul reassoc ninf nsz float %384, %384
  %386 = fmul reassoc ninf nsz float %385, %25
  %387 = fsub reassoc ninf nsz float %30, %386
  %388 = tail call float @expf(float noundef %387) #1
  %389 = load float*, float** %34, align 8
  %390 = load i32, i32* %35, align 4
  %391 = mul i32 %390, %311
  %392 = add i32 %391, %149
  %393 = sext i32 %392 to i64
  %394 = getelementptr float, float* %389, i64 %393
  %395 = load float, float* %394, align 4
  %396 = fmul reassoc ninf nsz float %395, %388
  %397 = fadd reassoc ninf nsz float %375, %396
  %398 = fadd reassoc ninf nsz float %376, %388
  %399 = load float*, float** %32, align 8
  %400 = load i32, i32* %33, align 4
  %401 = mul i32 %400, %311
  %402 = add i32 %401, %174
  %403 = sext i32 %402 to i64
  %404 = getelementptr float, float* %399, i64 %403
  %405 = load float, float* %404, align 4
  %406 = fsub reassoc ninf nsz float %405, %64
  %407 = fmul reassoc ninf nsz float %406, %406
  %408 = fmul reassoc ninf nsz float %407, %25
  %409 = fsub reassoc ninf nsz float %28, %408
  %410 = tail call float @expf(float noundef %409) #1
  %411 = load float*, float** %34, align 8
  %412 = load i32, i32* %35, align 4
  %413 = mul i32 %412, %311
  %414 = add i32 %413, %174
  %415 = sext i32 %414 to i64
  %416 = getelementptr float, float* %411, i64 %415
  %417 = load float, float* %416, align 4
  %418 = fmul reassoc ninf nsz float %417, %410
  %419 = fadd reassoc ninf nsz float %397, %418
  %420 = fadd reassoc ninf nsz float %398, %410
  %421 = add i32 %53, 1
  %422 = tail call i32 @llvm.smax.i32(i32 %421, i32 0)
  %423 = tail call i32 @llvm.smin.i32(i32 %69, i32 %422)
  %424 = load float*, float** %32, align 8
  %425 = load i32, i32* %33, align 4
  %426 = mul i32 %425, %423
  %427 = add i32 %426, %78
  %428 = sext i32 %427 to i64
  %429 = getelementptr float, float* %424, i64 %428
  %430 = load float, float* %429, align 4
  %431 = fsub reassoc ninf nsz float %430, %64
  %432 = fmul reassoc ninf nsz float %431, %431
  %433 = fmul reassoc ninf nsz float %432, %25
  %434 = fsub reassoc ninf nsz float %27, %433
  %435 = tail call float @expf(float noundef %434) #1
  %436 = load float*, float** %34, align 8
  %437 = load i32, i32* %35, align 4
  %438 = mul i32 %437, %423
  %439 = add i32 %438, %78
  %440 = sext i32 %439 to i64
  %441 = getelementptr float, float* %436, i64 %440
  %442 = load float, float* %441, align 4
  %443 = fmul reassoc ninf nsz float %442, %435
  %444 = fadd reassoc ninf nsz float %419, %443
  %445 = fadd reassoc ninf nsz float %420, %435
  %446 = load float*, float** %32, align 8
  %447 = load i32, i32* %33, align 4
  %448 = mul i32 %447, %423
  %449 = add i32 %448, %100
  %450 = sext i32 %449 to i64
  %451 = getelementptr float, float* %446, i64 %450
  %452 = load float, float* %451, align 4
  %453 = fsub reassoc ninf nsz float %452, %64
  %454 = fmul reassoc ninf nsz float %453, %453
  %455 = fmul reassoc ninf nsz float %454, %25
  %456 = fsub reassoc ninf nsz float %29, %455
  %457 = tail call float @expf(float noundef %456) #1
  %458 = load float*, float** %34, align 8
  %459 = load i32, i32* %35, align 4
  %460 = mul i32 %459, %423
  %461 = add i32 %460, %100
  %462 = sext i32 %461 to i64
  %463 = getelementptr float, float* %458, i64 %462
  %464 = load float, float* %463, align 4
  %465 = fmul reassoc ninf nsz float %464, %457
  %466 = fadd reassoc ninf nsz float %444, %465
  %467 = fadd reassoc ninf nsz float %445, %457
  %468 = load float*, float** %32, align 8
  %469 = load i32, i32* %33, align 4
  %470 = mul i32 %469, %423
  %471 = add i32 %470, %124
  %472 = sext i32 %471 to i64
  %473 = getelementptr float, float* %468, i64 %472
  %474 = load float, float* %473, align 4
  %475 = fsub reassoc ninf nsz float %474, %64
  %476 = fmul reassoc ninf nsz float %475, %475
  %477 = fmul reassoc ninf nsz float %476, %25
  %478 = fsub reassoc ninf nsz float %30, %477
  %479 = tail call float @expf(float noundef %478) #1
  %480 = load float*, float** %34, align 8
  %481 = load i32, i32* %35, align 4
  %482 = mul i32 %481, %423
  %483 = add i32 %482, %124
  %484 = sext i32 %483 to i64
  %485 = getelementptr float, float* %480, i64 %484
  %486 = load float, float* %485, align 4
  %487 = fmul reassoc ninf nsz float %486, %479
  %488 = fadd reassoc ninf nsz float %466, %487
  %489 = fadd reassoc ninf nsz float %467, %479
  %490 = load float*, float** %32, align 8
  %491 = load i32, i32* %33, align 4
  %492 = mul i32 %491, %423
  %493 = add i32 %492, %149
  %494 = sext i32 %493 to i64
  %495 = getelementptr float, float* %490, i64 %494
  %496 = load float, float* %495, align 4
  %497 = fsub reassoc ninf nsz float %496, %64
  %498 = fmul reassoc ninf nsz float %497, %497
  %499 = fmul reassoc ninf nsz float %498, %25
  %500 = fsub reassoc ninf nsz float %29, %499
  %501 = tail call float @expf(float noundef %500) #1
  %502 = load float*, float** %34, align 8
  %503 = load i32, i32* %35, align 4
  %504 = mul i32 %503, %423
  %505 = add i32 %504, %149
  %506 = sext i32 %505 to i64
  %507 = getelementptr float, float* %502, i64 %506
  %508 = load float, float* %507, align 4
  %509 = fmul reassoc ninf nsz float %508, %501
  %510 = fadd reassoc ninf nsz float %488, %509
  %511 = fadd reassoc ninf nsz float %489, %501
  %512 = load float*, float** %32, align 8
  %513 = load i32, i32* %33, align 4
  %514 = mul i32 %513, %423
  %515 = add i32 %514, %174
  %516 = sext i32 %515 to i64
  %517 = getelementptr float, float* %512, i64 %516
  %518 = load float, float* %517, align 4
  %519 = fsub reassoc ninf nsz float %518, %64
  %520 = fmul reassoc ninf nsz float %519, %519
  %521 = fmul reassoc ninf nsz float %520, %25
  %522 = fsub reassoc ninf nsz float %27, %521
  %523 = tail call float @expf(float noundef %522) #1
  %524 = load float*, float** %34, align 8
  %525 = load i32, i32* %35, align 4
  %526 = mul i32 %525, %423
  %527 = add i32 %526, %174
  %528 = sext i32 %527 to i64
  %529 = getelementptr float, float* %524, i64 %528
  %530 = load float, float* %529, align 4
  %531 = fmul reassoc ninf nsz float %530, %523
  %532 = fadd reassoc ninf nsz float %510, %531
  %533 = fadd reassoc ninf nsz float %511, %523
  %534 = add i32 %53, 2
  %535 = tail call i32 @llvm.smax.i32(i32 %534, i32 0)
  %536 = tail call i32 @llvm.smin.i32(i32 %69, i32 %535)
  %537 = load float*, float** %32, align 8
  %538 = load i32, i32* %33, align 4
  %539 = mul i32 %538, %536
  %540 = add i32 %539, %78
  %541 = sext i32 %540 to i64
  %542 = getelementptr float, float* %537, i64 %541
  %543 = load float, float* %542, align 4
  %544 = fsub reassoc ninf nsz float %543, %64
  %545 = fmul reassoc ninf nsz float %544, %544
  %546 = fmul reassoc ninf nsz float %545, %25
  %547 = fsub reassoc ninf nsz float %26, %546
  %548 = tail call float @expf(float noundef %547) #1
  %549 = load float*, float** %34, align 8
  %550 = load i32, i32* %35, align 4
  %551 = mul i32 %550, %536
  %552 = add i32 %551, %78
  %553 = sext i32 %552 to i64
  %554 = getelementptr float, float* %549, i64 %553
  %555 = load float, float* %554, align 4
  %556 = fmul reassoc ninf nsz float %555, %548
  %557 = fadd reassoc ninf nsz float %532, %556
  %558 = fadd reassoc ninf nsz float %533, %548
  %559 = load float*, float** %32, align 8
  %560 = load i32, i32* %33, align 4
  %561 = mul i32 %560, %536
  %562 = add i32 %561, %100
  %563 = sext i32 %562 to i64
  %564 = getelementptr float, float* %559, i64 %563
  %565 = load float, float* %564, align 4
  %566 = fsub reassoc ninf nsz float %565, %64
  %567 = fmul reassoc ninf nsz float %566, %566
  %568 = fmul reassoc ninf nsz float %567, %25
  %569 = fsub reassoc ninf nsz float %27, %568
  %570 = tail call float @expf(float noundef %569) #1
  %571 = load float*, float** %34, align 8
  %572 = load i32, i32* %35, align 4
  %573 = mul i32 %572, %536
  %574 = add i32 %573, %100
  %575 = sext i32 %574 to i64
  %576 = getelementptr float, float* %571, i64 %575
  %577 = load float, float* %576, align 4
  %578 = fmul reassoc ninf nsz float %577, %570
  %579 = fadd reassoc ninf nsz float %557, %578
  %580 = fadd reassoc ninf nsz float %558, %570
  %581 = load float*, float** %32, align 8
  %582 = load i32, i32* %33, align 4
  %583 = mul i32 %582, %536
  %584 = add i32 %583, %124
  %585 = sext i32 %584 to i64
  %586 = getelementptr float, float* %581, i64 %585
  %587 = load float, float* %586, align 4
  %588 = fsub reassoc ninf nsz float %587, %64
  %589 = fmul reassoc ninf nsz float %588, %588
  %590 = fmul reassoc ninf nsz float %589, %25
  %591 = fsub reassoc ninf nsz float %28, %590
  %592 = tail call float @expf(float noundef %591) #1
  %593 = load float*, float** %34, align 8
  %594 = load i32, i32* %35, align 4
  %595 = mul i32 %594, %536
  %596 = add i32 %595, %124
  %597 = sext i32 %596 to i64
  %598 = getelementptr float, float* %593, i64 %597
  %599 = load float, float* %598, align 4
  %600 = fmul reassoc ninf nsz float %599, %592
  %601 = fadd reassoc ninf nsz float %579, %600
  %602 = fadd reassoc ninf nsz float %580, %592
  %603 = load float*, float** %32, align 8
  %604 = load i32, i32* %33, align 4
  %605 = mul i32 %604, %536
  %606 = add i32 %605, %149
  %607 = sext i32 %606 to i64
  %608 = getelementptr float, float* %603, i64 %607
  %609 = load float, float* %608, align 4
  %610 = fsub reassoc ninf nsz float %609, %64
  %611 = fmul reassoc ninf nsz float %610, %610
  %612 = fmul reassoc ninf nsz float %611, %25
  %613 = fsub reassoc ninf nsz float %27, %612
  %614 = tail call float @expf(float noundef %613) #1
  %615 = load float*, float** %34, align 8
  %616 = load i32, i32* %35, align 4
  %617 = mul i32 %616, %536
  %618 = add i32 %617, %149
  %619 = sext i32 %618 to i64
  %620 = getelementptr float, float* %615, i64 %619
  %621 = load float, float* %620, align 4
  %622 = fmul reassoc ninf nsz float %621, %614
  %623 = fadd reassoc ninf nsz float %601, %622
  %624 = fadd reassoc ninf nsz float %602, %614
  %625 = load float*, float** %32, align 8
  %626 = load i32, i32* %33, align 4
  %627 = mul i32 %626, %536
  %628 = add i32 %627, %174
  %629 = sext i32 %628 to i64
  %630 = getelementptr float, float* %625, i64 %629
  %631 = load float, float* %630, align 4
  %632 = fsub reassoc ninf nsz float %631, %64
  %633 = fmul reassoc ninf nsz float %632, %632
  %634 = fmul reassoc ninf nsz float %633, %25
  %635 = fsub reassoc ninf nsz float %26, %634
  %636 = tail call float @expf(float noundef %635) #1
  %637 = load float*, float** %34, align 8
  %638 = load i32, i32* %35, align 4
  %639 = mul i32 %638, %536
  %640 = add i32 %639, %174
  %641 = sext i32 %640 to i64
  %642 = getelementptr float, float* %637, i64 %641
  %643 = load float, float* %642, align 4
  %644 = fmul reassoc ninf nsz float %643, %636
  %645 = fadd reassoc ninf nsz float %623, %644
  %646 = fadd reassoc ninf nsz float %624, %636
  %647 = fdiv reassoc ninf nsz float %645, %646
  %648 = load float*, float** %37, align 8
  %649 = load i32, i32* %38, align 4
  %650 = sub i32 %649, %44
  %651 = mul i32 %650, %53
  %652 = add i32 %.05, %651
  %653 = sext i32 %652 to i64
  %654 = getelementptr float, float* %648, i64 %653
  store float %647, float* %654, align 4
  %655 = add nsw i32 %.05, 1
  %exitcond.not = icmp eq i32 %19, %655
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
