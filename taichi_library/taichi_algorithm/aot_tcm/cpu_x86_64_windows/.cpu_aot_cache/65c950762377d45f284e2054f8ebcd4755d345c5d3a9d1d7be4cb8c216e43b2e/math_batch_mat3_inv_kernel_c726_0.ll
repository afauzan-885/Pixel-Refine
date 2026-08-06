; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.186*, void (%struct.RuntimeContext.186*, i8*)*, void (%struct.RuntimeContext.186*, i8*, i32)*, void (%struct.RuntimeContext.186*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.186 = type { i8*, %struct.LLVMRuntime.185*, i32, i64* }
%struct.LLVMRuntime.185 = type { %struct.PreallocatedMemoryChunk.181, %struct.PreallocatedMemoryChunk.181, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.182*], [1024 x %struct.NodeManager.183*], [1024 x i8*], i8*, %struct.RandState.184*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.181 = type { i8*, i8*, i64 }
%struct.ListManager.182 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.185* }
%struct.NodeManager.183 = type { %struct.LLVMRuntime.185*, i32, i32, i32, i32, %struct.ListManager.182*, %struct.ListManager.182*, %struct.ListManager.182*, i32 }
%struct.RandState.184 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @math_batch_mat3_inv_kernel_c726_0_kernel_0_serial(%struct.RuntimeContext.186* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.186* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.186, %struct.RuntimeContext.186* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.185*, %struct.LLVMRuntime.185** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.185, %struct.LLVMRuntime.185* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  store i32 %3, i32* %8, align 4
  ret void
}

; Function Attrs: nounwind
define void @math_batch_mat3_inv_kernel_c726_0_kernel_1_range_for(%struct.RuntimeContext.186* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.186* %context, %struct.RuntimeContext.186** %4, align 8
  store void (%struct.RuntimeContext.186*, i8*)* null, void (%struct.RuntimeContext.186*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.186*, i8*, i32)* @function_body, void (%struct.RuntimeContext.186*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.186*, i8*)* null, void (%struct.RuntimeContext.186*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.186, %struct.RuntimeContext.186* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.185*, %struct.LLVMRuntime.185** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.185, %struct.LLVMRuntime.185* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.185, %struct.LLVMRuntime.185* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.186* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.186, %struct.RuntimeContext.186* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.185*, %struct.LLVMRuntime.185** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.185, %struct.LLVMRuntime.185* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.186* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }* %22, i64 0, i32 0, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.04 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %192, %after_if ]
  %26 = load float*, float** %23, align 8
  %27 = load i32, i32* %24, align 4
  %28 = load i32, i32* %25, align 4
  %29 = mul i32 %27, %.04
  %30 = mul i32 %29, %28
  %31 = sext i32 %30 to i64
  %32 = getelementptr float, float* %26, i64 %31
  %33 = load float, float* %32, align 4
  %34 = add i32 %30, 1
  %35 = sext i32 %34 to i64
  %36 = getelementptr float, float* %26, i64 %35
  %37 = load float, float* %36, align 4
  %38 = add i32 %30, 2
  %39 = sext i32 %38 to i64
  %40 = getelementptr float, float* %26, i64 %39
  %41 = load float, float* %40, align 4
  %42 = add i32 %29, 1
  %43 = mul i32 %42, %28
  %44 = sext i32 %43 to i64
  %45 = getelementptr float, float* %26, i64 %44
  %46 = load float, float* %45, align 4
  %47 = add i32 %43, 1
  %48 = sext i32 %47 to i64
  %49 = getelementptr float, float* %26, i64 %48
  %50 = load float, float* %49, align 4
  %51 = add i32 %43, 2
  %52 = sext i32 %51 to i64
  %53 = getelementptr float, float* %26, i64 %52
  %54 = load float, float* %53, align 4
  %55 = add i32 %29, 2
  %56 = mul i32 %55, %28
  %57 = sext i32 %56 to i64
  %58 = getelementptr float, float* %26, i64 %57
  %59 = load float, float* %58, align 4
  %60 = add i32 %56, 1
  %61 = sext i32 %60 to i64
  %62 = getelementptr float, float* %26, i64 %61
  %63 = load float, float* %62, align 4
  %64 = add i32 %56, 2
  %65 = sext i32 %64 to i64
  %66 = getelementptr float, float* %26, i64 %65
  %67 = load float, float* %66, align 4
  %68 = fmul reassoc ninf nsz float %67, %50
  %69 = fmul reassoc ninf nsz float %63, %54
  %70 = fsub reassoc ninf nsz float %68, %69
  %71 = fmul reassoc ninf nsz float %70, %33
  %72 = fmul reassoc ninf nsz float %67, %46
  %73 = fmul reassoc ninf nsz float %59, %54
  %74 = fsub reassoc ninf nsz float %72, %73
  %75 = fmul reassoc ninf nsz float %74, %37
  %76 = fsub reassoc ninf nsz float %71, %75
  %77 = fmul reassoc ninf nsz float %63, %46
  %78 = fmul reassoc ninf nsz float %59, %50
  %79 = fsub reassoc ninf nsz float %77, %78
  %80 = fmul reassoc ninf nsz float %79, %41
  %81 = fadd reassoc ninf nsz float %76, %80
  %82 = tail call float @llvm.fabs.f32(float %81)
  %83 = fcmp reassoc ninf nsz ogt float %82, 0x3DDB7CDFE0000000
  br i1 %83, label %true_block, label %after_if

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %84 = fdiv reassoc ninf nsz float 1.000000e+00, %81
  %85 = fmul reassoc ninf nsz float %84, %70
  %86 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }** %20, align 8
  %87 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }* %86, i64 0, i32 1, i32 1
  %88 = load float*, float** %87, align 8
  %89 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }* %86, i64 0, i32 1, i32 0, i32 1
  %90 = load i32, i32* %89, align 4
  %91 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32 }* %86, i64 0, i32 1, i32 0, i32 2
  %92 = load i32, i32* %91, align 4
  %93 = mul i32 %90, %.04
  %94 = mul i32 %93, %92
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, float* %88, i64 %95
  store float %85, float* %96, align 4
  %97 = fmul reassoc ninf nsz float %63, %41
  %98 = fmul reassoc ninf nsz float %67, %37
  %99 = fsub reassoc ninf nsz float %97, %98
  %100 = fmul reassoc ninf nsz float %84, %99
  %101 = load float*, float** %87, align 8
  %102 = load i32, i32* %89, align 4
  %103 = load i32, i32* %91, align 4
  %104 = mul i32 %102, %.04
  %105 = mul i32 %104, %103
  %106 = add i32 %105, 1
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, float* %101, i64 %107
  store float %100, float* %108, align 4
  %109 = fmul reassoc ninf nsz float %54, %37
  %110 = fmul reassoc ninf nsz float %50, %41
  %111 = fsub reassoc ninf nsz float %109, %110
  %112 = fmul reassoc ninf nsz float %84, %111
  %113 = load float*, float** %87, align 8
  %114 = load i32, i32* %89, align 4
  %115 = load i32, i32* %91, align 4
  %116 = mul i32 %114, %.04
  %117 = mul i32 %116, %115
  %118 = add i32 %117, 2
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, float* %113, i64 %119
  store float %112, float* %120, align 4
  %121 = fsub reassoc ninf nsz float %73, %72
  %122 = fmul reassoc ninf nsz float %84, %121
  %123 = load float*, float** %87, align 8
  %124 = load i32, i32* %89, align 4
  %125 = load i32, i32* %91, align 4
  %126 = mul i32 %124, %.04
  %127 = add i32 %126, 1
  %128 = mul i32 %127, %125
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %123, i64 %129
  store float %122, float* %130, align 4
  %131 = fmul reassoc ninf nsz float %67, %33
  %132 = fmul reassoc ninf nsz float %59, %41
  %133 = fsub reassoc ninf nsz float %131, %132
  %134 = fmul reassoc ninf nsz float %84, %133
  %135 = load float*, float** %87, align 8
  %136 = load i32, i32* %89, align 4
  %137 = load i32, i32* %91, align 4
  %138 = mul i32 %136, %.04
  %139 = add i32 %138, 1
  %140 = mul i32 %139, %137
  %141 = add i32 %140, 1
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, float* %135, i64 %142
  store float %134, float* %143, align 4
  %144 = fmul reassoc ninf nsz float %46, %41
  %145 = fmul reassoc ninf nsz float %54, %33
  %146 = fsub reassoc ninf nsz float %144, %145
  %147 = fmul reassoc ninf nsz float %84, %146
  %148 = load float*, float** %87, align 8
  %149 = load i32, i32* %89, align 4
  %150 = load i32, i32* %91, align 4
  %151 = mul i32 %149, %.04
  %152 = add i32 %151, 1
  %153 = mul i32 %152, %150
  %154 = add i32 %153, 2
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %148, i64 %155
  store float %147, float* %156, align 4
  %157 = fmul reassoc ninf nsz float %84, %79
  %158 = load float*, float** %87, align 8
  %159 = load i32, i32* %89, align 4
  %160 = load i32, i32* %91, align 4
  %161 = mul i32 %159, %.04
  %162 = add i32 %161, 2
  %163 = mul i32 %162, %160
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %158, i64 %164
  store float %157, float* %165, align 4
  %166 = fmul reassoc ninf nsz float %59, %37
  %167 = fmul reassoc ninf nsz float %63, %33
  %168 = fsub reassoc ninf nsz float %166, %167
  %169 = fmul reassoc ninf nsz float %84, %168
  %170 = load float*, float** %87, align 8
  %171 = load i32, i32* %89, align 4
  %172 = load i32, i32* %91, align 4
  %173 = mul i32 %171, %.04
  %174 = add i32 %173, 2
  %175 = mul i32 %174, %172
  %176 = add i32 %175, 1
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, float* %170, i64 %177
  store float %169, float* %178, align 4
  %179 = fmul reassoc ninf nsz float %50, %33
  %180 = fmul reassoc ninf nsz float %46, %37
  %181 = fsub reassoc ninf nsz float %179, %180
  %182 = fmul reassoc ninf nsz float %84, %181
  %183 = load float*, float** %87, align 8
  %184 = load i32, i32* %89, align 4
  %185 = load i32, i32* %91, align 4
  %186 = mul i32 %184, %.04
  %187 = add i32 %186, 2
  %188 = mul i32 %187, %185
  %189 = add i32 %188, 2
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %183, i64 %190
  store float %182, float* %191, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body
  %192 = add nsw i32 %.04, 1
  %exitcond.not = icmp eq i32 %19, %192
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.186, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.186**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.186*, %struct.RuntimeContext.186** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.186*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.186*, i8*)*, void (%struct.RuntimeContext.186*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.186*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.186*, i8*, i32)*, void (%struct.RuntimeContext.186*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.186*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.186*, i8*)*, void (%struct.RuntimeContext.186*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.186*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.186* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.186* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.186* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.186, %struct.RuntimeContext.186* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.186* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.186* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.186*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.186* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
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
