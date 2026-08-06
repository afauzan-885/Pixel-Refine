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
define void @_bilinear_resize_offset_kernel_vec3_c136_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bilinear_resize_offset_kernel_vec3_c136_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nosync nounwind
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
  %20 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
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
  %38 = add i32 %27, -1
  %39 = add i32 %31, -1
  %40 = icmp slt i32 %17, %19
  br i1 %40, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %42 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %43 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %45 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %45, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %205, %for_loop_body ]
  %46 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %47 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %46, i64 0, i32 14
  %48 = load i8*, i8** %47, align 8
  %49 = getelementptr inbounds i8, i8* %48, i64 4
  %50 = bitcast i8* %49 to i32*
  %51 = load i32, i32* %50, align 4
  %52 = sdiv i32 %.05, %51
  %53 = mul i32 %52, %51
  %54 = xor i32 %51, %.05
  %55 = icmp slt i32 %54, 0
  %56 = icmp ne i32 %.05, 0
  %57 = icmp ne i32 %.05, %53
  %58 = and i1 %56, %55
  %59 = and i1 %58, %57
  %.neg4 = sext i1 %59 to i32
  %60 = add i32 %52, %.neg4
  %61 = add i32 %60, %23
  %62 = mul i32 %51, -1
  %63 = mul i32 %62, %60
  %64 = add i32 %25, %.05
  %65 = add i32 %64, %63
  %66 = sitofp i32 %61 to float
  %67 = fadd reassoc ninf nsz float %66, 5.000000e-01
  %68 = fmul reassoc ninf nsz float %67, %34
  %69 = fdiv reassoc ninf nsz float %68, %35
  %70 = fadd reassoc ninf nsz float %69, -5.000000e-01
  %71 = sitofp i32 %65 to float
  %72 = fadd reassoc ninf nsz float %71, 5.000000e-01
  %73 = fmul reassoc ninf nsz float %72, %36
  %74 = fdiv reassoc ninf nsz float %73, %37
  %75 = fadd reassoc ninf nsz float %74, -5.000000e-01
  %76 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %77 = fptosi float %76 to i32
  %78 = tail call reassoc ninf nsz float @llvm.floor.f32(float %75)
  %79 = fptosi float %78 to i32
  %80 = sitofp i32 %77 to float
  %81 = fsub reassoc ninf nsz float %70, %80
  %82 = sitofp i32 %79 to float
  %83 = fsub reassoc ninf nsz float %75, %82
  %84 = add i32 %77, 1
  %85 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %86 = tail call i32 @llvm.smin.i32(i32 %38, i32 %85)
  %87 = tail call i32 @llvm.smax.i32(i32 %84, i32 0)
  %88 = tail call i32 @llvm.smin.i32(i32 %38, i32 %87)
  %89 = add i32 %79, 1
  %90 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %91 = tail call i32 @llvm.smin.i32(i32 %39, i32 %90)
  %92 = tail call i32 @llvm.smax.i32(i32 %89, i32 0)
  %93 = tail call i32 @llvm.smin.i32(i32 %39, i32 %92)
  %94 = load float*, float** %41, align 8
  %95 = load i32, i32* %42, align 4
  %96 = mul i32 %86, %95
  %97 = add i32 %91, %96
  %98 = mul i32 %97, 3
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %94, i64 %99
  %101 = load float, float* %100, align 4
  %102 = add i32 %98, 1
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %94, i64 %103
  %105 = load float, float* %104, align 4
  %106 = add i32 %98, 2
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, float* %94, i64 %107
  %109 = load float, float* %108, align 4
  %110 = add i32 %93, %96
  %111 = mul i32 %110, 3
  %112 = sext i32 %111 to i64
  %113 = getelementptr float, float* %94, i64 %112
  %114 = load float, float* %113, align 4
  %115 = add i32 %111, 1
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %94, i64 %116
  %118 = load float, float* %117, align 4
  %119 = add i32 %111, 2
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %94, i64 %120
  %122 = load float, float* %121, align 4
  %123 = mul i32 %88, %95
  %124 = add i32 %123, %91
  %125 = mul i32 %124, 3
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, float* %94, i64 %126
  %128 = load float, float* %127, align 4
  %129 = add i32 %125, 1
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, float* %94, i64 %130
  %132 = load float, float* %131, align 4
  %133 = add i32 %125, 2
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %94, i64 %134
  %136 = load float, float* %135, align 4
  %137 = add i32 %93, %123
  %138 = mul i32 %137, 3
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, float* %94, i64 %139
  %141 = load float, float* %140, align 4
  %142 = add i32 %138, 1
  %143 = sext i32 %142 to i64
  %144 = getelementptr float, float* %94, i64 %143
  %145 = load float, float* %144, align 4
  %146 = add i32 %138, 2
  %147 = sext i32 %146 to i64
  %148 = getelementptr float, float* %94, i64 %147
  %149 = load float, float* %148, align 4
  %150 = fsub reassoc ninf nsz float 1.000000e+00, %83
  %151 = fmul reassoc ninf nsz float %150, %101
  %152 = fmul reassoc ninf nsz float %150, %105
  %153 = fmul reassoc ninf nsz float %150, %109
  %154 = fmul reassoc ninf nsz float %83, %114
  %155 = fmul reassoc ninf nsz float %83, %118
  %156 = fmul reassoc ninf nsz float %83, %122
  %157 = fadd reassoc ninf nsz float %151, %154
  %158 = fadd reassoc ninf nsz float %152, %155
  %159 = fadd reassoc ninf nsz float %153, %156
  %160 = fmul reassoc ninf nsz float %150, %128
  %161 = fmul reassoc ninf nsz float %150, %132
  %162 = fmul reassoc ninf nsz float %150, %136
  %163 = fmul reassoc ninf nsz float %83, %141
  %164 = fmul reassoc ninf nsz float %83, %145
  %165 = fmul reassoc ninf nsz float %83, %149
  %166 = fadd reassoc ninf nsz float %160, %163
  %167 = fadd reassoc ninf nsz float %161, %164
  %168 = fadd reassoc ninf nsz float %162, %165
  %169 = fsub reassoc ninf nsz float 1.000000e+00, %81
  %170 = fmul reassoc ninf nsz float %157, %169
  %171 = fmul reassoc ninf nsz float %158, %169
  %172 = fmul reassoc ninf nsz float %159, %169
  %173 = fmul reassoc ninf nsz float %166, %81
  %174 = fmul reassoc ninf nsz float %167, %81
  %175 = fmul reassoc ninf nsz float %168, %81
  %176 = fadd reassoc ninf nsz float %170, %173
  %177 = fadd reassoc ninf nsz float %171, %174
  %178 = fadd reassoc ninf nsz float %172, %175
  %179 = load float*, float** %43, align 8
  %180 = load i32, i32* %44, align 4
  %181 = sub i32 %180, %51
  %182 = mul i32 %181, 3
  %183 = mul i32 %182, %60
  %184 = add i32 %lsr.iv, %183
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, float* %179, i64 %185
  store float %176, float* %186, align 4
  %187 = load float*, float** %43, align 8
  %188 = load i32, i32* %44, align 4
  %189 = sub i32 %188, %51
  %190 = mul i32 %189, 3
  %191 = mul i32 %190, %60
  %192 = add i32 %lsr.iv, %191
  %193 = add i32 %192, 1
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %187, i64 %194
  store float %177, float* %195, align 4
  %196 = load float*, float** %43, align 8
  %197 = load i32, i32* %44, align 4
  %198 = sub i32 %197, %51
  %199 = mul i32 %198, 3
  %200 = mul i32 %199, %60
  %201 = add i32 %lsr.iv, %200
  %202 = add i32 %201, 2
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, float* %196, i64 %203
  store float %178, float* %204, align 4
  %205 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %205
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
