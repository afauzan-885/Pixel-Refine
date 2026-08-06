; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.60*, void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.60 = type { i8*, %struct.LLVMRuntime.59*, i32, i64* }
%struct.LLVMRuntime.59 = type { %struct.PreallocatedMemoryChunk.55, %struct.PreallocatedMemoryChunk.55, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.56*], [1024 x %struct.NodeManager.57*], [1024 x i8*], i8*, %struct.RandState.58*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.55 = type { i8*, i8*, i64 }
%struct.ListManager.56 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.59* }
%struct.NodeManager.57 = type { %struct.LLVMRuntime.59*, i32, i32, i32, i32, %struct.ListManager.56*, %struct.ListManager.56*, %struct.ListManager.56*, i32 }
%struct.RandState.58 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_bicubic_resize_offset_kernel_vec3_c148_0_kernel_0_serial(%struct.RuntimeContext.60* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.60* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 1, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bicubic_resize_offset_kernel_vec3_c148_0_kernel_1_range_for(%struct.RuntimeContext.60* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.60* %context, %struct.RuntimeContext.60** %4, align 8
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.60*, i8*, i32)* @function_body, void (%struct.RuntimeContext.60*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.60*, i8*)* null, void (%struct.RuntimeContext.60*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.60* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.60* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
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
  %.011 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %505, %for_loop_body ]
  %46 = load %struct.LLVMRuntime.59*, %struct.LLVMRuntime.59** %3, align 8
  %47 = getelementptr inbounds %struct.LLVMRuntime.59, %struct.LLVMRuntime.59* %46, i64 0, i32 14
  %48 = load i8*, i8** %47, align 8
  %49 = getelementptr inbounds i8, i8* %48, i64 4
  %50 = bitcast i8* %49 to i32*
  %51 = load i32, i32* %50, align 4
  %52 = sdiv i32 %.011, %51
  %53 = mul i32 %52, %51
  %54 = xor i32 %51, %.011
  %55 = icmp slt i32 %54, 0
  %56 = icmp ne i32 %.011, 0
  %57 = icmp ne i32 %.011, %53
  %58 = and i1 %56, %55
  %59 = and i1 %58, %57
  %.neg4 = sext i1 %59 to i32
  %60 = add i32 %52, %.neg4
  %61 = add i32 %60, %23
  %62 = mul i32 %51, -1
  %63 = mul i32 %62, %60
  %64 = add i32 %25, %.011
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
  %76 = tail call reassoc ninf nsz float @llvm.floor.f32(float %75)
  %77 = fptosi float %76 to i32
  %78 = tail call reassoc ninf nsz float @llvm.floor.f32(float %70)
  %79 = fptosi float %78 to i32
  %80 = sitofp i32 %77 to float
  %81 = fsub reassoc ninf nsz float %75, %80
  %82 = tail call float @llvm.fabs.f32(float %81)
  %83 = fadd reassoc ninf nsz float %82, 1.000000e+00
  %84 = fmul reassoc ninf nsz float %83, %83
  %85 = fmul reassoc ninf nsz float %83, 7.500000e-01
  %86 = fmul reassoc ninf nsz float %83, -6.000000e+00
  %87 = fsub reassoc ninf nsz float 3.750000e+00, %85
  %reass.mul = fmul reassoc ninf nsz float %84, %87
  %88 = fadd reassoc ninf nsz float %86, 3.000000e+00
  %89 = fadd reassoc ninf nsz float %88, %reass.mul
  %90 = fmul reassoc ninf nsz float %81, %81
  %91 = fmul reassoc ninf nsz float %90, 1.250000e+00
  %92 = fmul reassoc ninf nsz float %91, %82
  %93 = fmul reassoc ninf nsz float %90, 2.250000e+00
  %94 = fsub reassoc ninf nsz float %92, %93
  %95 = fadd reassoc ninf nsz float %94, 1.000000e+00
  %96 = fsub reassoc ninf nsz float 1.000000e+00, %82
  %97 = fmul reassoc ninf nsz float %96, %96
  %98 = fmul reassoc ninf nsz float %96, 1.250000e+00
  %99 = fadd reassoc ninf nsz float %98, -2.250000e+00
  %100 = fmul reassoc ninf nsz float %99, %97
  %101 = fadd reassoc ninf nsz float %100, 1.000000e+00
  %102 = fsub reassoc ninf nsz float 2.000000e+00, %82
  %103 = fmul reassoc ninf nsz float %102, %102
  %104 = fmul reassoc ninf nsz float %102, 7.500000e-01
  %105 = fmul reassoc ninf nsz float %102, -6.000000e+00
  %106 = fsub reassoc ninf nsz float 3.750000e+00, %104
  %reass.mul6 = fmul reassoc ninf nsz float %103, %106
  %107 = fadd reassoc ninf nsz float %105, 3.000000e+00
  %108 = fadd reassoc ninf nsz float %107, %reass.mul6
  %109 = sitofp i32 %79 to float
  %110 = fsub reassoc ninf nsz float %70, %109
  %111 = tail call float @llvm.fabs.f32(float %110)
  %112 = fadd reassoc ninf nsz float %111, 1.000000e+00
  %113 = fmul reassoc ninf nsz float %112, %112
  %114 = fmul reassoc ninf nsz float %112, 7.500000e-01
  %115 = fmul reassoc ninf nsz float %112, -6.000000e+00
  %116 = fsub reassoc ninf nsz float 3.750000e+00, %114
  %reass.mul8 = fmul reassoc ninf nsz float %113, %116
  %117 = fadd reassoc ninf nsz float %115, 3.000000e+00
  %118 = fadd reassoc ninf nsz float %117, %reass.mul8
  %119 = fmul reassoc ninf nsz float %110, %110
  %120 = fmul reassoc ninf nsz float %119, 1.250000e+00
  %121 = fmul reassoc ninf nsz float %120, %111
  %122 = fmul reassoc ninf nsz float %119, 2.250000e+00
  %123 = fsub reassoc ninf nsz float %121, %122
  %124 = fadd reassoc ninf nsz float %123, 1.000000e+00
  %125 = fsub reassoc ninf nsz float 1.000000e+00, %111
  %126 = fmul reassoc ninf nsz float %125, %125
  %127 = fmul reassoc ninf nsz float %125, 1.250000e+00
  %128 = fadd reassoc ninf nsz float %127, -2.250000e+00
  %129 = fmul reassoc ninf nsz float %128, %126
  %130 = fadd reassoc ninf nsz float %129, 1.000000e+00
  %131 = fsub reassoc ninf nsz float 2.000000e+00, %111
  %132 = fmul reassoc ninf nsz float %131, %131
  %133 = fmul reassoc ninf nsz float %131, 7.500000e-01
  %134 = fmul reassoc ninf nsz float %131, -6.000000e+00
  %135 = fsub reassoc ninf nsz float 3.750000e+00, %133
  %reass.mul10 = fmul reassoc ninf nsz float %132, %135
  %136 = fadd reassoc ninf nsz float %134, 3.000000e+00
  %137 = fadd reassoc ninf nsz float %136, %reass.mul10
  %138 = add i32 %79, -1
  %139 = tail call i32 @llvm.smax.i32(i32 %138, i32 0)
  %140 = tail call i32 @llvm.smin.i32(i32 %38, i32 %139)
  %141 = add i32 %77, -1
  %142 = tail call i32 @llvm.smax.i32(i32 %141, i32 0)
  %143 = tail call i32 @llvm.smin.i32(i32 %39, i32 %142)
  %144 = load float*, float** %41, align 8
  %145 = load i32, i32* %42, align 4
  %146 = mul i32 %140, %145
  %147 = add i32 %143, %146
  %148 = mul i32 %147, 3
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, float* %144, i64 %149
  %151 = load float, float* %150, align 4
  %152 = add i32 %148, 1
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %144, i64 %153
  %155 = load float, float* %154, align 4
  %156 = add i32 %148, 2
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %144, i64 %157
  %159 = load float, float* %158, align 4
  %160 = fmul reassoc ninf nsz float %89, %151
  %161 = fmul reassoc ninf nsz float %89, %155
  %162 = fmul reassoc ninf nsz float %89, %159
  %163 = tail call i32 @llvm.smax.i32(i32 %77, i32 0)
  %164 = tail call i32 @llvm.smin.i32(i32 %39, i32 %163)
  %165 = add i32 %146, %164
  %166 = mul i32 %165, 3
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, float* %144, i64 %167
  %169 = load float, float* %168, align 4
  %170 = add i32 %166, 1
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %144, i64 %171
  %173 = load float, float* %172, align 4
  %174 = add i32 %166, 2
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, float* %144, i64 %175
  %177 = load float, float* %176, align 4
  %178 = fmul reassoc ninf nsz float %95, %169
  %179 = fmul reassoc ninf nsz float %95, %173
  %180 = fmul reassoc ninf nsz float %95, %177
  %181 = add i32 %77, 1
  %182 = tail call i32 @llvm.smax.i32(i32 %181, i32 0)
  %183 = tail call i32 @llvm.smin.i32(i32 %39, i32 %182)
  %184 = add i32 %183, %146
  %185 = mul i32 %184, 3
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %144, i64 %186
  %188 = load float, float* %187, align 4
  %189 = add i32 %185, 1
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %144, i64 %190
  %192 = load float, float* %191, align 4
  %193 = add i32 %185, 2
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %144, i64 %194
  %196 = load float, float* %195, align 4
  %197 = fmul reassoc ninf nsz float %101, %188
  %198 = fmul reassoc ninf nsz float %101, %192
  %199 = fmul reassoc ninf nsz float %101, %196
  %200 = add i32 %77, 2
  %201 = tail call i32 @llvm.smax.i32(i32 %200, i32 0)
  %202 = tail call i32 @llvm.smin.i32(i32 %39, i32 %201)
  %203 = add i32 %202, %146
  %204 = mul i32 %203, 3
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %144, i64 %205
  %207 = load float, float* %206, align 4
  %208 = add i32 %204, 1
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %144, i64 %209
  %211 = load float, float* %210, align 4
  %212 = add i32 %204, 2
  %213 = sext i32 %212 to i64
  %214 = getelementptr float, float* %144, i64 %213
  %215 = load float, float* %214, align 4
  %216 = fmul reassoc ninf nsz float %108, %207
  %217 = fmul reassoc ninf nsz float %108, %211
  %218 = fmul reassoc ninf nsz float %108, %215
  %219 = fadd reassoc ninf nsz float %197, %178
  %220 = fadd reassoc ninf nsz float %219, %160
  %221 = fadd reassoc ninf nsz float %220, %216
  %222 = fadd reassoc ninf nsz float %198, %179
  %223 = fadd reassoc ninf nsz float %222, %161
  %224 = fadd reassoc ninf nsz float %223, %217
  %225 = fadd reassoc ninf nsz float %199, %180
  %226 = fadd reassoc ninf nsz float %225, %162
  %227 = fadd reassoc ninf nsz float %226, %218
  %228 = fmul reassoc ninf nsz float %221, %118
  %229 = fmul reassoc ninf nsz float %224, %118
  %230 = fmul reassoc ninf nsz float %227, %118
  %231 = tail call i32 @llvm.smax.i32(i32 %79, i32 0)
  %232 = tail call i32 @llvm.smin.i32(i32 %38, i32 %231)
  %233 = mul i32 %232, %145
  %234 = add i32 %143, %233
  %235 = mul i32 %234, 3
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, float* %144, i64 %236
  %238 = load float, float* %237, align 4
  %239 = add i32 %235, 1
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %144, i64 %240
  %242 = load float, float* %241, align 4
  %243 = add i32 %235, 2
  %244 = sext i32 %243 to i64
  %245 = getelementptr float, float* %144, i64 %244
  %246 = load float, float* %245, align 4
  %247 = fmul reassoc ninf nsz float %89, %238
  %248 = fmul reassoc ninf nsz float %89, %242
  %249 = fmul reassoc ninf nsz float %89, %246
  %250 = add i32 %164, %233
  %251 = mul i32 %250, 3
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, float* %144, i64 %252
  %254 = load float, float* %253, align 4
  %255 = add i32 %251, 1
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, float* %144, i64 %256
  %258 = load float, float* %257, align 4
  %259 = add i32 %251, 2
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, float* %144, i64 %260
  %262 = load float, float* %261, align 4
  %263 = fmul reassoc ninf nsz float %95, %254
  %264 = fmul reassoc ninf nsz float %95, %258
  %265 = fmul reassoc ninf nsz float %95, %262
  %266 = add i32 %183, %233
  %267 = mul i32 %266, 3
  %268 = sext i32 %267 to i64
  %269 = getelementptr float, float* %144, i64 %268
  %270 = load float, float* %269, align 4
  %271 = add i32 %267, 1
  %272 = sext i32 %271 to i64
  %273 = getelementptr float, float* %144, i64 %272
  %274 = load float, float* %273, align 4
  %275 = add i32 %267, 2
  %276 = sext i32 %275 to i64
  %277 = getelementptr float, float* %144, i64 %276
  %278 = load float, float* %277, align 4
  %279 = fmul reassoc ninf nsz float %101, %270
  %280 = fmul reassoc ninf nsz float %101, %274
  %281 = fmul reassoc ninf nsz float %278, %101
  %282 = add i32 %202, %233
  %283 = mul i32 %282, 3
  %284 = sext i32 %283 to i64
  %285 = getelementptr float, float* %144, i64 %284
  %286 = load float, float* %285, align 4
  %287 = add i32 %283, 1
  %288 = sext i32 %287 to i64
  %289 = getelementptr float, float* %144, i64 %288
  %290 = load float, float* %289, align 4
  %291 = add i32 %283, 2
  %292 = sext i32 %291 to i64
  %293 = getelementptr float, float* %144, i64 %292
  %294 = load float, float* %293, align 4
  %295 = fmul reassoc ninf nsz float %286, %108
  %296 = fmul reassoc ninf nsz float %290, %108
  %297 = fmul reassoc ninf nsz float %294, %108
  %298 = fadd reassoc ninf nsz float %279, %263
  %299 = fadd reassoc ninf nsz float %298, %247
  %300 = fadd reassoc ninf nsz float %299, %295
  %301 = fadd reassoc ninf nsz float %280, %264
  %302 = fadd reassoc ninf nsz float %301, %248
  %303 = fadd reassoc ninf nsz float %302, %296
  %304 = fadd reassoc ninf nsz float %281, %265
  %305 = fadd reassoc ninf nsz float %304, %249
  %306 = fadd reassoc ninf nsz float %305, %297
  %307 = fmul reassoc ninf nsz float %300, %124
  %308 = fmul reassoc ninf nsz float %303, %124
  %309 = fmul reassoc ninf nsz float %306, %124
  %310 = fadd reassoc ninf nsz float %228, %307
  %311 = fadd reassoc ninf nsz float %229, %308
  %312 = fadd reassoc ninf nsz float %230, %309
  %313 = add i32 %79, 1
  %314 = tail call i32 @llvm.smax.i32(i32 %313, i32 0)
  %315 = tail call i32 @llvm.smin.i32(i32 %38, i32 %314)
  %316 = mul i32 %315, %145
  %317 = add i32 %143, %316
  %318 = mul i32 %317, 3
  %319 = sext i32 %318 to i64
  %320 = getelementptr float, float* %144, i64 %319
  %321 = load float, float* %320, align 4
  %322 = add i32 %318, 1
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, float* %144, i64 %323
  %325 = load float, float* %324, align 4
  %326 = add i32 %318, 2
  %327 = sext i32 %326 to i64
  %328 = getelementptr float, float* %144, i64 %327
  %329 = load float, float* %328, align 4
  %330 = fmul reassoc ninf nsz float %321, %89
  %331 = fmul reassoc ninf nsz float %325, %89
  %332 = fmul reassoc ninf nsz float %329, %89
  %333 = add i32 %316, %164
  %334 = mul i32 %333, 3
  %335 = sext i32 %334 to i64
  %336 = getelementptr float, float* %144, i64 %335
  %337 = load float, float* %336, align 4
  %338 = add i32 %334, 1
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, float* %144, i64 %339
  %341 = load float, float* %340, align 4
  %342 = add i32 %334, 2
  %343 = sext i32 %342 to i64
  %344 = getelementptr float, float* %144, i64 %343
  %345 = load float, float* %344, align 4
  %346 = fmul reassoc ninf nsz float %337, %95
  %347 = fmul reassoc ninf nsz float %341, %95
  %348 = fmul reassoc ninf nsz float %345, %95
  %349 = fadd reassoc ninf nsz float %346, %330
  %350 = fadd reassoc ninf nsz float %347, %331
  %351 = fadd reassoc ninf nsz float %348, %332
  %352 = add i32 %183, %316
  %353 = mul i32 %352, 3
  %354 = sext i32 %353 to i64
  %355 = getelementptr float, float* %144, i64 %354
  %356 = load float, float* %355, align 4
  %357 = add i32 %353, 1
  %358 = sext i32 %357 to i64
  %359 = getelementptr float, float* %144, i64 %358
  %360 = load float, float* %359, align 4
  %361 = add i32 %353, 2
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, float* %144, i64 %362
  %364 = load float, float* %363, align 4
  %365 = fmul reassoc ninf nsz float %356, %101
  %366 = fmul reassoc ninf nsz float %360, %101
  %367 = fmul reassoc ninf nsz float %364, %101
  %368 = fadd reassoc ninf nsz float %349, %365
  %369 = fadd reassoc ninf nsz float %350, %366
  %370 = fadd reassoc ninf nsz float %351, %367
  %371 = add i32 %202, %316
  %372 = mul i32 %371, 3
  %373 = sext i32 %372 to i64
  %374 = getelementptr float, float* %144, i64 %373
  %375 = load float, float* %374, align 4
  %376 = add i32 %372, 1
  %377 = sext i32 %376 to i64
  %378 = getelementptr float, float* %144, i64 %377
  %379 = load float, float* %378, align 4
  %380 = add i32 %372, 2
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, float* %144, i64 %381
  %383 = load float, float* %382, align 4
  %384 = fmul reassoc ninf nsz float %375, %108
  %385 = fmul reassoc ninf nsz float %379, %108
  %386 = fmul reassoc ninf nsz float %383, %108
  %387 = fadd reassoc ninf nsz float %368, %384
  %388 = fadd reassoc ninf nsz float %369, %385
  %389 = fadd reassoc ninf nsz float %370, %386
  %390 = fmul reassoc ninf nsz float %387, %130
  %391 = fmul reassoc ninf nsz float %388, %130
  %392 = fmul reassoc ninf nsz float %389, %130
  %393 = fadd reassoc ninf nsz float %310, %390
  %394 = fadd reassoc ninf nsz float %311, %391
  %395 = fadd reassoc ninf nsz float %312, %392
  %396 = add i32 %79, 2
  %397 = tail call i32 @llvm.smax.i32(i32 %396, i32 0)
  %398 = tail call i32 @llvm.smin.i32(i32 %38, i32 %397)
  %399 = mul i32 %398, %145
  %400 = add i32 %143, %399
  %401 = mul i32 %400, 3
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, float* %144, i64 %402
  %404 = load float, float* %403, align 4
  %405 = add i32 %401, 1
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, float* %144, i64 %406
  %408 = load float, float* %407, align 4
  %409 = add i32 %401, 2
  %410 = sext i32 %409 to i64
  %411 = getelementptr float, float* %144, i64 %410
  %412 = load float, float* %411, align 4
  %413 = fmul reassoc ninf nsz float %404, %89
  %414 = fmul reassoc ninf nsz float %408, %89
  %415 = fmul reassoc ninf nsz float %412, %89
  %416 = add i32 %399, %164
  %417 = mul i32 %416, 3
  %418 = sext i32 %417 to i64
  %419 = getelementptr float, float* %144, i64 %418
  %420 = load float, float* %419, align 4
  %421 = add i32 %417, 1
  %422 = sext i32 %421 to i64
  %423 = getelementptr float, float* %144, i64 %422
  %424 = load float, float* %423, align 4
  %425 = add i32 %417, 2
  %426 = sext i32 %425 to i64
  %427 = getelementptr float, float* %144, i64 %426
  %428 = load float, float* %427, align 4
  %429 = fmul reassoc ninf nsz float %420, %95
  %430 = fmul reassoc ninf nsz float %424, %95
  %431 = fmul reassoc ninf nsz float %428, %95
  %432 = fadd reassoc ninf nsz float %429, %413
  %433 = fadd reassoc ninf nsz float %430, %414
  %434 = fadd reassoc ninf nsz float %431, %415
  %435 = add i32 %183, %399
  %436 = mul i32 %435, 3
  %437 = sext i32 %436 to i64
  %438 = getelementptr float, float* %144, i64 %437
  %439 = load float, float* %438, align 4
  %440 = add i32 %436, 1
  %441 = sext i32 %440 to i64
  %442 = getelementptr float, float* %144, i64 %441
  %443 = load float, float* %442, align 4
  %444 = add i32 %436, 2
  %445 = sext i32 %444 to i64
  %446 = getelementptr float, float* %144, i64 %445
  %447 = load float, float* %446, align 4
  %448 = fmul reassoc ninf nsz float %439, %101
  %449 = fmul reassoc ninf nsz float %443, %101
  %450 = fmul reassoc ninf nsz float %447, %101
  %451 = fadd reassoc ninf nsz float %432, %448
  %452 = fadd reassoc ninf nsz float %433, %449
  %453 = fadd reassoc ninf nsz float %434, %450
  %454 = add i32 %202, %399
  %455 = mul i32 %454, 3
  %456 = sext i32 %455 to i64
  %457 = getelementptr float, float* %144, i64 %456
  %458 = load float, float* %457, align 4
  %459 = add i32 %455, 1
  %460 = sext i32 %459 to i64
  %461 = getelementptr float, float* %144, i64 %460
  %462 = load float, float* %461, align 4
  %463 = add i32 %455, 2
  %464 = sext i32 %463 to i64
  %465 = getelementptr float, float* %144, i64 %464
  %466 = load float, float* %465, align 4
  %467 = fmul reassoc ninf nsz float %458, %108
  %468 = fmul reassoc ninf nsz float %462, %108
  %469 = fmul reassoc ninf nsz float %466, %108
  %470 = fadd reassoc ninf nsz float %451, %467
  %471 = fadd reassoc ninf nsz float %452, %468
  %472 = fadd reassoc ninf nsz float %453, %469
  %473 = fmul reassoc ninf nsz float %470, %137
  %474 = fmul reassoc ninf nsz float %471, %137
  %475 = fmul reassoc ninf nsz float %472, %137
  %476 = fadd reassoc ninf nsz float %393, %473
  %477 = fadd reassoc ninf nsz float %394, %474
  %478 = fadd reassoc ninf nsz float %395, %475
  %479 = load float*, float** %43, align 8
  %480 = load i32, i32* %44, align 4
  %481 = sub i32 %480, %51
  %482 = mul i32 %481, 3
  %483 = mul i32 %482, %60
  %484 = add i32 %lsr.iv, %483
  %485 = sext i32 %484 to i64
  %486 = getelementptr float, float* %479, i64 %485
  store float %476, float* %486, align 4
  %487 = load float*, float** %43, align 8
  %488 = load i32, i32* %44, align 4
  %489 = sub i32 %488, %51
  %490 = mul i32 %489, 3
  %491 = mul i32 %490, %60
  %492 = add i32 %lsr.iv, %491
  %493 = add i32 %492, 1
  %494 = sext i32 %493 to i64
  %495 = getelementptr float, float* %487, i64 %494
  store float %477, float* %495, align 4
  %496 = load float*, float** %43, align 8
  %497 = load i32, i32* %44, align 4
  %498 = sub i32 %497, %51
  %499 = mul i32 %498, 3
  %500 = mul i32 %499, %60
  %501 = add i32 %lsr.iv, %500
  %502 = add i32 %501, 2
  %503 = sext i32 %502 to i64
  %504 = getelementptr float, float* %496, i64 %503
  store float %478, float* %504, align 4
  %505 = add nsw i32 %.011, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %505
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.60, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.60**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.60*, %struct.RuntimeContext.60** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.60*, i8*, i32)*, void (%struct.RuntimeContext.60*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.60*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.60*, i8*)*, void (%struct.RuntimeContext.60*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.60* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.60* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.60, %struct.RuntimeContext.60* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.60* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.60*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.60* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
