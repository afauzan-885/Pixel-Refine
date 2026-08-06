; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.216*, void (%struct.RuntimeContext.216*, i8*)*, void (%struct.RuntimeContext.216*, i8*, i32)*, void (%struct.RuntimeContext.216*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.216 = type { i8*, %struct.LLVMRuntime.215*, i32, i64* }
%struct.LLVMRuntime.215 = type { %struct.PreallocatedMemoryChunk.211, %struct.PreallocatedMemoryChunk.211, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.212*], [1024 x %struct.NodeManager.213*], [1024 x i8*], i8*, %struct.RandState.214*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.211 = type { i8*, i8*, i64 }
%struct.ListManager.212 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.215* }
%struct.NodeManager.213 = type { %struct.LLVMRuntime.215*, i32, i32, i32, i32, %struct.ListManager.212*, %struct.ListManager.212*, %struct.ListManager.212*, i32 }
%struct.RandState.214 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_warp_perspective_offset_kernel_vec3_c332_0_kernel_0_serial(%struct.RuntimeContext.216* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.216* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 2, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.216, %struct.RuntimeContext.216* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.215*, %struct.LLVMRuntime.215** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.215, %struct.LLVMRuntime.215* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.215*, %struct.LLVMRuntime.215** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.215, %struct.LLVMRuntime.215* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_warp_perspective_offset_kernel_vec3_c332_0_kernel_1_range_for(%struct.RuntimeContext.216* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.216* %context, %struct.RuntimeContext.216** %4, align 8
  store void (%struct.RuntimeContext.216*, i8*)* null, void (%struct.RuntimeContext.216*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.216*, i8*, i32)* @function_body, void (%struct.RuntimeContext.216*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.216*, i8*)* null, void (%struct.RuntimeContext.216*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.216, %struct.RuntimeContext.216* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.215*, %struct.LLVMRuntime.215** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.215, %struct.LLVMRuntime.215* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.215, %struct.LLVMRuntime.215* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.216* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.216, %struct.RuntimeContext.216* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.215*, %struct.LLVMRuntime.215** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.215, %struct.LLVMRuntime.215* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.216* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %29 = load i32, i32* %28, align 4
  %30 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %31 = load float*, float** %30, align 8
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %33 = load i32, i32* %32, align 4
  %34 = getelementptr float, float* %31, i64 1
  %35 = getelementptr float, float* %31, i64 2
  %36 = sext i32 %33 to i64
  %37 = getelementptr float, float* %31, i64 %36
  %38 = add i32 %33, 1
  %39 = sext i32 %38 to i64
  %40 = getelementptr float, float* %31, i64 %39
  %41 = add i32 %33, 2
  %42 = sext i32 %41 to i64
  %43 = getelementptr float, float* %31, i64 %42
  %44 = shl i32 %33, 1
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, float* %31, i64 %45
  %47 = getelementptr float, float* %46, i64 1
  %48 = add i32 %44, 2
  %49 = sext i32 %48 to i64
  %50 = getelementptr float, float* %31, i64 %49
  %51 = add i32 %29, -1
  %52 = add i32 %27, -1
  %53 = icmp slt i32 %17, %19
  br i1 %53, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %54 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %55 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %56 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %58 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %58, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.09 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %250, %for_loop_body ]
  %59 = load %struct.LLVMRuntime.215*, %struct.LLVMRuntime.215** %3, align 8
  %60 = getelementptr inbounds %struct.LLVMRuntime.215, %struct.LLVMRuntime.215* %59, i64 0, i32 14
  %61 = load i8*, i8** %60, align 8
  %62 = getelementptr inbounds i8, i8* %61, i64 4
  %63 = bitcast i8* %62 to i32*
  %64 = load i32, i32* %63, align 4
  %65 = sdiv i32 %.09, %64
  %66 = mul i32 %65, %64
  %67 = xor i32 %64, %.09
  %68 = icmp slt i32 %67, 0
  %69 = icmp ne i32 %.09, 0
  %70 = icmp ne i32 %.09, %66
  %71 = and i1 %69, %68
  %72 = and i1 %71, %70
  %.neg4 = sext i1 %72 to i32
  %73 = add i32 %65, %.neg4
  %74 = add i32 %73, %23
  %75 = mul i32 %64, -1
  %76 = mul i32 %75, %73
  %77 = add i32 %25, %.09
  %78 = add i32 %77, %76
  %79 = load float, float* %31, align 4
  %80 = sitofp i32 %78 to float
  %81 = fmul reassoc ninf nsz float %79, %80
  %82 = load float, float* %34, align 4
  %83 = sitofp i32 %74 to float
  %84 = fmul reassoc ninf nsz float %82, %83
  %85 = load float, float* %35, align 4
  %86 = fadd reassoc ninf nsz float %84, %85
  %87 = fadd reassoc ninf nsz float %86, %81
  %88 = load float, float* %37, align 4
  %89 = fmul reassoc ninf nsz float %88, %80
  %90 = load float, float* %40, align 4
  %91 = fmul reassoc ninf nsz float %90, %83
  %92 = load float, float* %43, align 4
  %93 = fadd reassoc ninf nsz float %91, %92
  %94 = fadd reassoc ninf nsz float %93, %89
  %95 = load float, float* %46, align 4
  %96 = fmul reassoc ninf nsz float %95, %80
  %97 = load float, float* %47, align 4
  %98 = fmul reassoc ninf nsz float %97, %83
  %99 = load float, float* %50, align 4
  %100 = fadd reassoc ninf nsz float %98, 0x3E112E0BE0000000
  %101 = fadd reassoc ninf nsz float %100, %99
  %102 = fadd reassoc ninf nsz float %101, %96
  %103 = fdiv reassoc ninf nsz float %87, %102
  %104 = fdiv reassoc ninf nsz float %94, %102
  %105 = tail call reassoc ninf nsz float @llvm.floor.f32(float %103)
  %106 = fptosi float %105 to i32
  %107 = tail call reassoc ninf nsz float @llvm.floor.f32(float %104)
  %108 = fptosi float %107 to i32
  %109 = sitofp i32 %106 to float
  %110 = fsub reassoc ninf nsz float %103, %109
  %111 = sitofp i32 %108 to float
  %112 = fsub reassoc ninf nsz float %104, %111
  %113 = tail call i32 @llvm.abs.i32(i32 %106, i1 true)
  %114 = sub i32 %113, %51
  %115 = tail call i32 @llvm.smax.i32(i32 %114, i32 0)
  %.neg5 = mul i32 %115, -2
  %116 = add i32 %.neg5, %113
  %117 = tail call i32 @llvm.smax.i32(i32 %116, i32 0)
  %118 = tail call i32 @llvm.smin.i32(i32 %51, i32 %117)
  %119 = tail call i32 @llvm.abs.i32(i32 %108, i1 true)
  %120 = sub i32 %119, %52
  %121 = tail call i32 @llvm.smax.i32(i32 %120, i32 0)
  %.neg6 = mul i32 %121, -2
  %122 = add i32 %.neg6, %119
  %123 = tail call i32 @llvm.smax.i32(i32 %122, i32 0)
  %124 = tail call i32 @llvm.smin.i32(i32 %52, i32 %123)
  %125 = add i32 %106, 1
  %126 = tail call i32 @llvm.abs.i32(i32 %125, i1 true)
  %127 = sub i32 %126, %51
  %128 = tail call i32 @llvm.smax.i32(i32 %127, i32 0)
  %.neg7 = mul i32 %128, -2
  %129 = add i32 %.neg7, %126
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 0)
  %131 = tail call i32 @llvm.smin.i32(i32 %51, i32 %130)
  %132 = add i32 %108, 1
  %133 = tail call i32 @llvm.abs.i32(i32 %132, i1 true)
  %134 = sub i32 %133, %52
  %135 = tail call i32 @llvm.smax.i32(i32 %134, i32 0)
  %.neg8 = mul i32 %135, -2
  %136 = add i32 %.neg8, %133
  %137 = tail call i32 @llvm.smax.i32(i32 %136, i32 0)
  %138 = tail call i32 @llvm.smin.i32(i32 %52, i32 %137)
  %139 = load float*, float** %54, align 8
  %140 = load i32, i32* %55, align 4
  %141 = mul i32 %124, %140
  %142 = add i32 %141, %118
  %143 = mul i32 %142, 3
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, float* %139, i64 %144
  %146 = load float, float* %145, align 4
  %147 = add i32 %143, 1
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %139, i64 %148
  %150 = load float, float* %149, align 4
  %151 = add i32 %143, 2
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, float* %139, i64 %152
  %154 = load float, float* %153, align 4
  %155 = add i32 %141, %131
  %156 = mul i32 %155, 3
  %157 = sext i32 %156 to i64
  %158 = getelementptr float, float* %139, i64 %157
  %159 = load float, float* %158, align 4
  %160 = add i32 %156, 1
  %161 = sext i32 %160 to i64
  %162 = getelementptr float, float* %139, i64 %161
  %163 = load float, float* %162, align 4
  %164 = add i32 %156, 2
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, float* %139, i64 %165
  %167 = load float, float* %166, align 4
  %168 = mul i32 %138, %140
  %169 = add i32 %168, %118
  %170 = mul i32 %169, 3
  %171 = sext i32 %170 to i64
  %172 = getelementptr float, float* %139, i64 %171
  %173 = load float, float* %172, align 4
  %174 = add i32 %170, 1
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, float* %139, i64 %175
  %177 = load float, float* %176, align 4
  %178 = add i32 %170, 2
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, float* %139, i64 %179
  %181 = load float, float* %180, align 4
  %182 = add i32 %168, %131
  %183 = mul i32 %182, 3
  %184 = sext i32 %183 to i64
  %185 = getelementptr float, float* %139, i64 %184
  %186 = load float, float* %185, align 4
  %187 = add i32 %183, 1
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, float* %139, i64 %188
  %190 = load float, float* %189, align 4
  %191 = add i32 %183, 2
  %192 = sext i32 %191 to i64
  %193 = getelementptr float, float* %139, i64 %192
  %194 = load float, float* %193, align 4
  %195 = fsub reassoc ninf nsz float 1.000000e+00, %110
  %196 = fmul reassoc ninf nsz float %195, %146
  %197 = fmul reassoc ninf nsz float %195, %150
  %198 = fmul reassoc ninf nsz float %195, %154
  %199 = fmul reassoc ninf nsz float %110, %159
  %200 = fmul reassoc ninf nsz float %110, %163
  %201 = fmul reassoc ninf nsz float %110, %167
  %202 = fadd reassoc ninf nsz float %196, %199
  %203 = fadd reassoc ninf nsz float %197, %200
  %204 = fadd reassoc ninf nsz float %198, %201
  %205 = fmul reassoc ninf nsz float %195, %173
  %206 = fmul reassoc ninf nsz float %177, %195
  %207 = fmul reassoc ninf nsz float %181, %195
  %208 = fmul reassoc ninf nsz float %186, %110
  %209 = fmul reassoc ninf nsz float %190, %110
  %210 = fmul reassoc ninf nsz float %194, %110
  %211 = fadd reassoc ninf nsz float %208, %205
  %212 = fadd reassoc ninf nsz float %209, %206
  %213 = fadd reassoc ninf nsz float %210, %207
  %214 = fsub reassoc ninf nsz float 1.000000e+00, %112
  %215 = fmul reassoc ninf nsz float %202, %214
  %216 = fmul reassoc ninf nsz float %203, %214
  %217 = fmul reassoc ninf nsz float %204, %214
  %218 = fmul reassoc ninf nsz float %211, %112
  %219 = fmul reassoc ninf nsz float %212, %112
  %220 = fmul reassoc ninf nsz float %213, %112
  %221 = fadd reassoc ninf nsz float %218, %215
  %222 = fadd reassoc ninf nsz float %219, %216
  %223 = fadd reassoc ninf nsz float %220, %217
  %224 = load float*, float** %56, align 8
  %225 = load i32, i32* %57, align 4
  %226 = sub i32 %225, %64
  %227 = mul i32 %226, 3
  %228 = mul i32 %227, %73
  %229 = add i32 %lsr.iv, %228
  %230 = sext i32 %229 to i64
  %231 = getelementptr float, float* %224, i64 %230
  store float %221, float* %231, align 4
  %232 = load float*, float** %56, align 8
  %233 = load i32, i32* %57, align 4
  %234 = sub i32 %233, %64
  %235 = mul i32 %234, 3
  %236 = mul i32 %235, %73
  %237 = add i32 %lsr.iv, %236
  %238 = add i32 %237, 1
  %239 = sext i32 %238 to i64
  %240 = getelementptr float, float* %232, i64 %239
  store float %222, float* %240, align 4
  %241 = load float*, float** %56, align 8
  %242 = load i32, i32* %57, align 4
  %243 = sub i32 %242, %64
  %244 = mul i32 %243, 3
  %245 = mul i32 %244, %73
  %246 = add i32 %lsr.iv, %245
  %247 = add i32 %246, 2
  %248 = sext i32 %247 to i64
  %249 = getelementptr float, float* %241, i64 %248
  store float %223, float* %249, align 4
  %250 = add nsw i32 %.09, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %250
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
  %4 = alloca %struct.RuntimeContext.216, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.216**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.216*, %struct.RuntimeContext.216** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.216*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.216*, i8*)*, void (%struct.RuntimeContext.216*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.216*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.216*, i8*, i32)*, void (%struct.RuntimeContext.216*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.216*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.216*, i8*)*, void (%struct.RuntimeContext.216*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.216*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.216* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.216* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.216* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.216, %struct.RuntimeContext.216* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.216* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.216* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.216*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.216* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
