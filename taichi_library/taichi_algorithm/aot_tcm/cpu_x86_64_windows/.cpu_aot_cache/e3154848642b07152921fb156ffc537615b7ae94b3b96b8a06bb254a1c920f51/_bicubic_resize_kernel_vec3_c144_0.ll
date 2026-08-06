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
define void @_bicubic_resize_kernel_vec3_c144_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 4
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %11, i64 0, i32 5
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
define void @_bicubic_resize_kernel_vec3_c144_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %25 = load i32, i32* %24, align 4
  %26 = sitofp i32 %23 to float
  %27 = sitofp i32 %25 to float
  %28 = add i32 %23, -1
  %29 = add i32 %25, -1
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %31 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %34 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %35 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %35, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.011 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %501, %for_loop_body ]
  %36 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %37 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %36, i64 0, i32 14
  %38 = load i8*, i8** %37, align 8
  %39 = getelementptr inbounds i8, i8* %38, i64 4
  %40 = bitcast i8* %39 to i32*
  %41 = load i32, i32* %40, align 4
  %42 = sdiv i32 %.011, %41
  %43 = mul i32 %42, %41
  %44 = xor i32 %41, %.011
  %45 = icmp slt i32 %44, 0
  %46 = icmp ne i32 %.011, 0
  %47 = icmp ne i32 %.011, %43
  %48 = and i1 %46, %45
  %49 = and i1 %48, %47
  %.neg4 = sext i1 %49 to i32
  %50 = add i32 %42, %.neg4
  %51 = mul i32 %41, -1
  %52 = mul i32 %51, %50
  %53 = add i32 %.011, %52
  %54 = sitofp i32 %50 to float
  %55 = fadd reassoc ninf nsz float %54, 5.000000e-01
  %56 = getelementptr inbounds i8, i8* %38, i64 8
  %57 = bitcast i8* %56 to i32*
  %58 = load i32, i32* %57, align 4
  %59 = sitofp i32 %58 to float
  %60 = fmul reassoc ninf nsz float %55, %26
  %61 = fdiv reassoc ninf nsz float %60, %59
  %62 = fadd reassoc ninf nsz float %61, -5.000000e-01
  %63 = sitofp i32 %53 to float
  %64 = fadd reassoc ninf nsz float %63, 5.000000e-01
  %65 = getelementptr inbounds i8, i8* %38, i64 12
  %66 = bitcast i8* %65 to i32*
  %67 = load i32, i32* %66, align 4
  %68 = sitofp i32 %67 to float
  %69 = fmul reassoc ninf nsz float %64, %27
  %70 = fdiv reassoc ninf nsz float %69, %68
  %71 = fadd reassoc ninf nsz float %70, -5.000000e-01
  %72 = tail call reassoc ninf nsz float @llvm.floor.f32(float %71)
  %73 = fptosi float %72 to i32
  %74 = tail call reassoc ninf nsz float @llvm.floor.f32(float %62)
  %75 = fptosi float %74 to i32
  %76 = sitofp i32 %73 to float
  %77 = fsub reassoc ninf nsz float %71, %76
  %78 = sitofp i32 %75 to float
  %79 = fsub reassoc ninf nsz float %62, %78
  %80 = tail call float @llvm.fabs.f32(float %77)
  %81 = fadd reassoc ninf nsz float %80, 1.000000e+00
  %82 = fmul reassoc ninf nsz float %81, %81
  %83 = fmul reassoc ninf nsz float %81, 7.500000e-01
  %84 = fmul reassoc ninf nsz float %81, -6.000000e+00
  %85 = fsub reassoc ninf nsz float 3.750000e+00, %83
  %reass.mul = fmul reassoc ninf nsz float %82, %85
  %86 = fadd reassoc ninf nsz float %84, 3.000000e+00
  %87 = fadd reassoc ninf nsz float %86, %reass.mul
  %88 = fmul reassoc ninf nsz float %77, %77
  %89 = fmul reassoc ninf nsz float %88, 1.250000e+00
  %90 = fmul reassoc ninf nsz float %89, %80
  %91 = fmul reassoc ninf nsz float %88, 2.250000e+00
  %92 = fsub reassoc ninf nsz float %90, %91
  %93 = fadd reassoc ninf nsz float %92, 1.000000e+00
  %94 = fsub reassoc ninf nsz float 1.000000e+00, %80
  %95 = fmul reassoc ninf nsz float %94, %94
  %96 = fmul reassoc ninf nsz float %94, 1.250000e+00
  %97 = fadd reassoc ninf nsz float %96, -2.250000e+00
  %98 = fmul reassoc ninf nsz float %97, %95
  %99 = fadd reassoc ninf nsz float %98, 1.000000e+00
  %100 = fsub reassoc ninf nsz float 2.000000e+00, %80
  %101 = fmul reassoc ninf nsz float %100, %100
  %102 = fmul reassoc ninf nsz float %100, 7.500000e-01
  %103 = fmul reassoc ninf nsz float %100, -6.000000e+00
  %104 = fsub reassoc ninf nsz float 3.750000e+00, %102
  %reass.mul6 = fmul reassoc ninf nsz float %101, %104
  %105 = fadd reassoc ninf nsz float %103, 3.000000e+00
  %106 = fadd reassoc ninf nsz float %105, %reass.mul6
  %107 = tail call float @llvm.fabs.f32(float %79)
  %108 = fadd reassoc ninf nsz float %107, 1.000000e+00
  %109 = fmul reassoc ninf nsz float %108, %108
  %110 = fmul reassoc ninf nsz float %108, 7.500000e-01
  %111 = fmul reassoc ninf nsz float %108, -6.000000e+00
  %112 = fsub reassoc ninf nsz float 3.750000e+00, %110
  %reass.mul8 = fmul reassoc ninf nsz float %109, %112
  %113 = fadd reassoc ninf nsz float %111, 3.000000e+00
  %114 = fadd reassoc ninf nsz float %113, %reass.mul8
  %115 = fmul reassoc ninf nsz float %79, %79
  %116 = fmul reassoc ninf nsz float %115, 1.250000e+00
  %117 = fmul reassoc ninf nsz float %116, %107
  %118 = fmul reassoc ninf nsz float %115, 2.250000e+00
  %119 = fsub reassoc ninf nsz float %117, %118
  %120 = fadd reassoc ninf nsz float %119, 1.000000e+00
  %121 = fsub reassoc ninf nsz float 1.000000e+00, %107
  %122 = fmul reassoc ninf nsz float %121, %121
  %123 = fmul reassoc ninf nsz float %121, 1.250000e+00
  %124 = fadd reassoc ninf nsz float %123, -2.250000e+00
  %125 = fmul reassoc ninf nsz float %124, %122
  %126 = fadd reassoc ninf nsz float %125, 1.000000e+00
  %127 = fsub reassoc ninf nsz float 2.000000e+00, %107
  %128 = fmul reassoc ninf nsz float %127, %127
  %129 = fmul reassoc ninf nsz float %127, 7.500000e-01
  %130 = fmul reassoc ninf nsz float %127, -6.000000e+00
  %131 = fsub reassoc ninf nsz float 3.750000e+00, %129
  %reass.mul10 = fmul reassoc ninf nsz float %128, %131
  %132 = fadd reassoc ninf nsz float %130, 3.000000e+00
  %133 = fadd reassoc ninf nsz float %132, %reass.mul10
  %134 = add i32 %75, -1
  %135 = tail call i32 @llvm.smax.i32(i32 %134, i32 0)
  %136 = tail call i32 @llvm.smin.i32(i32 %28, i32 %135)
  %137 = add i32 %73, -1
  %138 = tail call i32 @llvm.smax.i32(i32 %137, i32 0)
  %139 = tail call i32 @llvm.smin.i32(i32 %29, i32 %138)
  %140 = load float*, float** %31, align 8
  %141 = load i32, i32* %32, align 4
  %142 = mul i32 %136, %141
  %143 = add i32 %139, %142
  %144 = mul i32 %143, 3
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %140, i64 %145
  %147 = load float, float* %146, align 4
  %148 = add i32 %144, 1
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, float* %140, i64 %149
  %151 = load float, float* %150, align 4
  %152 = add i32 %144, 2
  %153 = sext i32 %152 to i64
  %154 = getelementptr float, float* %140, i64 %153
  %155 = load float, float* %154, align 4
  %156 = fmul reassoc ninf nsz float %87, %147
  %157 = fmul reassoc ninf nsz float %87, %151
  %158 = fmul reassoc ninf nsz float %87, %155
  %159 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %160 = tail call i32 @llvm.smin.i32(i32 %29, i32 %159)
  %161 = add i32 %142, %160
  %162 = mul i32 %161, 3
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %140, i64 %163
  %165 = load float, float* %164, align 4
  %166 = add i32 %162, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, float* %140, i64 %167
  %169 = load float, float* %168, align 4
  %170 = add i32 %162, 2
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %140, i64 %171
  %173 = load float, float* %172, align 4
  %174 = fmul reassoc ninf nsz float %93, %165
  %175 = fmul reassoc ninf nsz float %93, %169
  %176 = fmul reassoc ninf nsz float %93, %173
  %177 = add i32 %73, 1
  %178 = tail call i32 @llvm.smax.i32(i32 %177, i32 0)
  %179 = tail call i32 @llvm.smin.i32(i32 %29, i32 %178)
  %180 = add i32 %179, %142
  %181 = mul i32 %180, 3
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, float* %140, i64 %182
  %184 = load float, float* %183, align 4
  %185 = add i32 %181, 1
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %140, i64 %186
  %188 = load float, float* %187, align 4
  %189 = add i32 %181, 2
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %140, i64 %190
  %192 = load float, float* %191, align 4
  %193 = fmul reassoc ninf nsz float %99, %184
  %194 = fmul reassoc ninf nsz float %99, %188
  %195 = fmul reassoc ninf nsz float %99, %192
  %196 = add i32 %73, 2
  %197 = tail call i32 @llvm.smax.i32(i32 %196, i32 0)
  %198 = tail call i32 @llvm.smin.i32(i32 %29, i32 %197)
  %199 = add i32 %198, %142
  %200 = mul i32 %199, 3
  %201 = sext i32 %200 to i64
  %202 = getelementptr float, float* %140, i64 %201
  %203 = load float, float* %202, align 4
  %204 = add i32 %200, 1
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %140, i64 %205
  %207 = load float, float* %206, align 4
  %208 = add i32 %200, 2
  %209 = sext i32 %208 to i64
  %210 = getelementptr float, float* %140, i64 %209
  %211 = load float, float* %210, align 4
  %212 = fmul reassoc ninf nsz float %106, %203
  %213 = fmul reassoc ninf nsz float %106, %207
  %214 = fmul reassoc ninf nsz float %106, %211
  %215 = fadd reassoc ninf nsz float %193, %174
  %216 = fadd reassoc ninf nsz float %215, %156
  %217 = fadd reassoc ninf nsz float %216, %212
  %218 = fadd reassoc ninf nsz float %194, %175
  %219 = fadd reassoc ninf nsz float %218, %157
  %220 = fadd reassoc ninf nsz float %219, %213
  %221 = fadd reassoc ninf nsz float %195, %176
  %222 = fadd reassoc ninf nsz float %221, %158
  %223 = fadd reassoc ninf nsz float %222, %214
  %224 = fmul reassoc ninf nsz float %217, %114
  %225 = fmul reassoc ninf nsz float %220, %114
  %226 = fmul reassoc ninf nsz float %223, %114
  %227 = tail call i32 @llvm.smax.i32(i32 %75, i32 0)
  %228 = tail call i32 @llvm.smin.i32(i32 %28, i32 %227)
  %229 = mul i32 %228, %141
  %230 = add i32 %139, %229
  %231 = mul i32 %230, 3
  %232 = sext i32 %231 to i64
  %233 = getelementptr float, float* %140, i64 %232
  %234 = load float, float* %233, align 4
  %235 = add i32 %231, 1
  %236 = sext i32 %235 to i64
  %237 = getelementptr float, float* %140, i64 %236
  %238 = load float, float* %237, align 4
  %239 = add i32 %231, 2
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %140, i64 %240
  %242 = load float, float* %241, align 4
  %243 = fmul reassoc ninf nsz float %87, %234
  %244 = fmul reassoc ninf nsz float %87, %238
  %245 = fmul reassoc ninf nsz float %87, %242
  %246 = add i32 %160, %229
  %247 = mul i32 %246, 3
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, float* %140, i64 %248
  %250 = load float, float* %249, align 4
  %251 = add i32 %247, 1
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, float* %140, i64 %252
  %254 = load float, float* %253, align 4
  %255 = add i32 %247, 2
  %256 = sext i32 %255 to i64
  %257 = getelementptr float, float* %140, i64 %256
  %258 = load float, float* %257, align 4
  %259 = fmul reassoc ninf nsz float %93, %250
  %260 = fmul reassoc ninf nsz float %254, %93
  %261 = fmul reassoc ninf nsz float %258, %93
  %262 = fadd reassoc ninf nsz float %243, %259
  %263 = fadd reassoc ninf nsz float %244, %260
  %264 = fadd reassoc ninf nsz float %245, %261
  %265 = add i32 %179, %229
  %266 = mul i32 %265, 3
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, float* %140, i64 %267
  %269 = load float, float* %268, align 4
  %270 = add i32 %266, 1
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, float* %140, i64 %271
  %273 = load float, float* %272, align 4
  %274 = add i32 %266, 2
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, float* %140, i64 %275
  %277 = load float, float* %276, align 4
  %278 = fmul reassoc ninf nsz float %269, %99
  %279 = fmul reassoc ninf nsz float %273, %99
  %280 = fmul reassoc ninf nsz float %277, %99
  %281 = fadd reassoc ninf nsz float %262, %278
  %282 = fadd reassoc ninf nsz float %263, %279
  %283 = fadd reassoc ninf nsz float %264, %280
  %284 = add i32 %198, %229
  %285 = mul i32 %284, 3
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, float* %140, i64 %286
  %288 = load float, float* %287, align 4
  %289 = add i32 %285, 1
  %290 = sext i32 %289 to i64
  %291 = getelementptr float, float* %140, i64 %290
  %292 = load float, float* %291, align 4
  %293 = add i32 %285, 2
  %294 = sext i32 %293 to i64
  %295 = getelementptr float, float* %140, i64 %294
  %296 = load float, float* %295, align 4
  %297 = fmul reassoc ninf nsz float %288, %106
  %298 = fmul reassoc ninf nsz float %292, %106
  %299 = fmul reassoc ninf nsz float %296, %106
  %300 = fadd reassoc ninf nsz float %281, %297
  %301 = fadd reassoc ninf nsz float %282, %298
  %302 = fadd reassoc ninf nsz float %283, %299
  %303 = fmul reassoc ninf nsz float %300, %120
  %304 = fmul reassoc ninf nsz float %301, %120
  %305 = fmul reassoc ninf nsz float %302, %120
  %306 = fadd reassoc ninf nsz float %303, %224
  %307 = fadd reassoc ninf nsz float %304, %225
  %308 = fadd reassoc ninf nsz float %305, %226
  %309 = add i32 %75, 1
  %310 = tail call i32 @llvm.smax.i32(i32 %309, i32 0)
  %311 = tail call i32 @llvm.smin.i32(i32 %28, i32 %310)
  %312 = mul i32 %311, %141
  %313 = add i32 %139, %312
  %314 = mul i32 %313, 3
  %315 = sext i32 %314 to i64
  %316 = getelementptr float, float* %140, i64 %315
  %317 = load float, float* %316, align 4
  %318 = add i32 %314, 1
  %319 = sext i32 %318 to i64
  %320 = getelementptr float, float* %140, i64 %319
  %321 = load float, float* %320, align 4
  %322 = add i32 %314, 2
  %323 = sext i32 %322 to i64
  %324 = getelementptr float, float* %140, i64 %323
  %325 = load float, float* %324, align 4
  %326 = fmul reassoc ninf nsz float %317, %87
  %327 = fmul reassoc ninf nsz float %321, %87
  %328 = fmul reassoc ninf nsz float %325, %87
  %329 = add i32 %312, %160
  %330 = mul i32 %329, 3
  %331 = sext i32 %330 to i64
  %332 = getelementptr float, float* %140, i64 %331
  %333 = load float, float* %332, align 4
  %334 = add i32 %330, 1
  %335 = sext i32 %334 to i64
  %336 = getelementptr float, float* %140, i64 %335
  %337 = load float, float* %336, align 4
  %338 = add i32 %330, 2
  %339 = sext i32 %338 to i64
  %340 = getelementptr float, float* %140, i64 %339
  %341 = load float, float* %340, align 4
  %342 = fmul reassoc ninf nsz float %333, %93
  %343 = fmul reassoc ninf nsz float %337, %93
  %344 = fmul reassoc ninf nsz float %341, %93
  %345 = fadd reassoc ninf nsz float %342, %326
  %346 = fadd reassoc ninf nsz float %343, %327
  %347 = fadd reassoc ninf nsz float %344, %328
  %348 = add i32 %179, %312
  %349 = mul i32 %348, 3
  %350 = sext i32 %349 to i64
  %351 = getelementptr float, float* %140, i64 %350
  %352 = load float, float* %351, align 4
  %353 = add i32 %349, 1
  %354 = sext i32 %353 to i64
  %355 = getelementptr float, float* %140, i64 %354
  %356 = load float, float* %355, align 4
  %357 = add i32 %349, 2
  %358 = sext i32 %357 to i64
  %359 = getelementptr float, float* %140, i64 %358
  %360 = load float, float* %359, align 4
  %361 = fmul reassoc ninf nsz float %352, %99
  %362 = fmul reassoc ninf nsz float %356, %99
  %363 = fmul reassoc ninf nsz float %360, %99
  %364 = fadd reassoc ninf nsz float %345, %361
  %365 = fadd reassoc ninf nsz float %346, %362
  %366 = fadd reassoc ninf nsz float %347, %363
  %367 = add i32 %198, %312
  %368 = mul i32 %367, 3
  %369 = sext i32 %368 to i64
  %370 = getelementptr float, float* %140, i64 %369
  %371 = load float, float* %370, align 4
  %372 = add i32 %368, 1
  %373 = sext i32 %372 to i64
  %374 = getelementptr float, float* %140, i64 %373
  %375 = load float, float* %374, align 4
  %376 = add i32 %368, 2
  %377 = sext i32 %376 to i64
  %378 = getelementptr float, float* %140, i64 %377
  %379 = load float, float* %378, align 4
  %380 = fmul reassoc ninf nsz float %371, %106
  %381 = fmul reassoc ninf nsz float %375, %106
  %382 = fmul reassoc ninf nsz float %379, %106
  %383 = fadd reassoc ninf nsz float %364, %380
  %384 = fadd reassoc ninf nsz float %365, %381
  %385 = fadd reassoc ninf nsz float %366, %382
  %386 = fmul reassoc ninf nsz float %383, %126
  %387 = fmul reassoc ninf nsz float %384, %126
  %388 = fmul reassoc ninf nsz float %385, %126
  %389 = fadd reassoc ninf nsz float %306, %386
  %390 = fadd reassoc ninf nsz float %307, %387
  %391 = fadd reassoc ninf nsz float %308, %388
  %392 = add i32 %75, 2
  %393 = tail call i32 @llvm.smax.i32(i32 %392, i32 0)
  %394 = tail call i32 @llvm.smin.i32(i32 %28, i32 %393)
  %395 = mul i32 %394, %141
  %396 = add i32 %139, %395
  %397 = mul i32 %396, 3
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, float* %140, i64 %398
  %400 = load float, float* %399, align 4
  %401 = add i32 %397, 1
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, float* %140, i64 %402
  %404 = load float, float* %403, align 4
  %405 = add i32 %397, 2
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, float* %140, i64 %406
  %408 = load float, float* %407, align 4
  %409 = fmul reassoc ninf nsz float %400, %87
  %410 = fmul reassoc ninf nsz float %404, %87
  %411 = fmul reassoc ninf nsz float %408, %87
  %412 = add i32 %395, %160
  %413 = mul i32 %412, 3
  %414 = sext i32 %413 to i64
  %415 = getelementptr float, float* %140, i64 %414
  %416 = load float, float* %415, align 4
  %417 = add i32 %413, 1
  %418 = sext i32 %417 to i64
  %419 = getelementptr float, float* %140, i64 %418
  %420 = load float, float* %419, align 4
  %421 = add i32 %413, 2
  %422 = sext i32 %421 to i64
  %423 = getelementptr float, float* %140, i64 %422
  %424 = load float, float* %423, align 4
  %425 = fmul reassoc ninf nsz float %416, %93
  %426 = fmul reassoc ninf nsz float %420, %93
  %427 = fmul reassoc ninf nsz float %424, %93
  %428 = fadd reassoc ninf nsz float %425, %409
  %429 = fadd reassoc ninf nsz float %426, %410
  %430 = fadd reassoc ninf nsz float %427, %411
  %431 = add i32 %179, %395
  %432 = mul i32 %431, 3
  %433 = sext i32 %432 to i64
  %434 = getelementptr float, float* %140, i64 %433
  %435 = load float, float* %434, align 4
  %436 = add i32 %432, 1
  %437 = sext i32 %436 to i64
  %438 = getelementptr float, float* %140, i64 %437
  %439 = load float, float* %438, align 4
  %440 = add i32 %432, 2
  %441 = sext i32 %440 to i64
  %442 = getelementptr float, float* %140, i64 %441
  %443 = load float, float* %442, align 4
  %444 = fmul reassoc ninf nsz float %435, %99
  %445 = fmul reassoc ninf nsz float %439, %99
  %446 = fmul reassoc ninf nsz float %443, %99
  %447 = fadd reassoc ninf nsz float %428, %444
  %448 = fadd reassoc ninf nsz float %429, %445
  %449 = fadd reassoc ninf nsz float %430, %446
  %450 = add i32 %198, %395
  %451 = mul i32 %450, 3
  %452 = sext i32 %451 to i64
  %453 = getelementptr float, float* %140, i64 %452
  %454 = load float, float* %453, align 4
  %455 = add i32 %451, 1
  %456 = sext i32 %455 to i64
  %457 = getelementptr float, float* %140, i64 %456
  %458 = load float, float* %457, align 4
  %459 = add i32 %451, 2
  %460 = sext i32 %459 to i64
  %461 = getelementptr float, float* %140, i64 %460
  %462 = load float, float* %461, align 4
  %463 = fmul reassoc ninf nsz float %454, %106
  %464 = fmul reassoc ninf nsz float %458, %106
  %465 = fmul reassoc ninf nsz float %462, %106
  %466 = fadd reassoc ninf nsz float %447, %463
  %467 = fadd reassoc ninf nsz float %448, %464
  %468 = fadd reassoc ninf nsz float %449, %465
  %469 = fmul reassoc ninf nsz float %466, %133
  %470 = fmul reassoc ninf nsz float %467, %133
  %471 = fmul reassoc ninf nsz float %468, %133
  %472 = fadd reassoc ninf nsz float %389, %469
  %473 = fadd reassoc ninf nsz float %390, %470
  %474 = fadd reassoc ninf nsz float %391, %471
  %475 = load float*, float** %33, align 8
  %476 = load i32, i32* %34, align 4
  %477 = sub i32 %476, %41
  %478 = mul i32 %477, 3
  %479 = mul i32 %478, %50
  %480 = add i32 %lsr.iv, %479
  %481 = sext i32 %480 to i64
  %482 = getelementptr float, float* %475, i64 %481
  store float %472, float* %482, align 4
  %483 = load float*, float** %33, align 8
  %484 = load i32, i32* %34, align 4
  %485 = sub i32 %484, %41
  %486 = mul i32 %485, 3
  %487 = mul i32 %486, %50
  %488 = add i32 %lsr.iv, %487
  %489 = add i32 %488, 1
  %490 = sext i32 %489 to i64
  %491 = getelementptr float, float* %483, i64 %490
  store float %473, float* %491, align 4
  %492 = load float*, float** %33, align 8
  %493 = load i32, i32* %34, align 4
  %494 = sub i32 %493, %41
  %495 = mul i32 %494, 3
  %496 = mul i32 %495, %50
  %497 = add i32 %lsr.iv, %496
  %498 = add i32 %497, 2
  %499 = sext i32 %498 to i64
  %500 = getelementptr float, float* %492, i64 %499
  store float %474, float* %500, align 4
  %501 = add nsw i32 %.011, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %501
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
