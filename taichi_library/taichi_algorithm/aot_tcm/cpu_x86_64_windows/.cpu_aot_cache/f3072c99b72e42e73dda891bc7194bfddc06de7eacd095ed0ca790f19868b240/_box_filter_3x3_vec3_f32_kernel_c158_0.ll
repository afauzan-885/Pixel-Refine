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
define void @_box_filter_3x3_vec3_f32_kernel_c158_0_kernel_0_serial(%struct.RuntimeContext.36* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.36* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, %struct.RuntimeContext.36* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_box_filter_3x3_vec3_f32_kernel_c158_0_kernel_1_range_for(%struct.RuntimeContext.36* %context) local_unnamed_addr #1 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext.36* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %27 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %27, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.05 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %245, %for_loop_body ]
  %28 = load %struct.LLVMRuntime.35*, %struct.LLVMRuntime.35** %3, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.35, %struct.LLVMRuntime.35* %28, i64 0, i32 14
  %30 = load i8*, i8** %29, align 8
  %31 = getelementptr inbounds i8, i8* %30, i64 4
  %32 = bitcast i8* %31 to i32*
  %33 = load i32, i32* %32, align 4
  %34 = sdiv i32 %.05, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.05
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.05, 0
  %39 = icmp ne i32 %.05, %35
  %40 = and i1 %38, %37
  %41 = and i1 %40, %39
  %.neg4 = sext i1 %41 to i32
  %42 = add i32 %34, %.neg4
  %43 = mul i32 %33, -1
  %44 = mul i32 %43, %42
  %45 = add i32 %.05, %44
  %46 = add i32 %42, -1
  %47 = getelementptr inbounds i8, i8* %30, i64 8
  %48 = bitcast i8* %47 to i32*
  %49 = load i32, i32* %48, align 4
  %50 = add i32 %49, -1
  %51 = tail call i32 @llvm.smax.i32(i32 %46, i32 0)
  %52 = tail call i32 @llvm.smin.i32(i32 %50, i32 %51)
  %53 = add i32 %45, -1
  %54 = getelementptr inbounds i8, i8* %30, i64 12
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = add i32 %56, -1
  %58 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %59 = tail call i32 @llvm.smin.i32(i32 %57, i32 %58)
  %60 = load float*, float** %23, align 8
  %61 = load i32, i32* %24, align 4
  %62 = mul i32 %52, %61
  %63 = add i32 %59, %62
  %64 = mul i32 %63, 3
  %65 = sext i32 %64 to i64
  %66 = getelementptr float, float* %60, i64 %65
  %67 = load float, float* %66, align 4
  %68 = add i32 %64, 1
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, float* %60, i64 %69
  %71 = load float, float* %70, align 4
  %72 = add i32 %64, 2
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, float* %60, i64 %73
  %75 = load float, float* %74, align 4
  %76 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %77 = tail call i32 @llvm.smin.i32(i32 %57, i32 %76)
  %78 = add i32 %62, %77
  %79 = mul i32 %78, 3
  %80 = sext i32 %79 to i64
  %81 = getelementptr float, float* %60, i64 %80
  %82 = load float, float* %81, align 4
  %83 = add i32 %79, 1
  %84 = sext i32 %83 to i64
  %85 = getelementptr float, float* %60, i64 %84
  %86 = load float, float* %85, align 4
  %87 = add i32 %79, 2
  %88 = sext i32 %87 to i64
  %89 = getelementptr float, float* %60, i64 %88
  %90 = load float, float* %89, align 4
  %91 = fadd reassoc ninf nsz float %82, %67
  %92 = fadd reassoc ninf nsz float %86, %71
  %93 = fadd reassoc ninf nsz float %90, %75
  %94 = add i32 %45, 1
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = tail call i32 @llvm.smin.i32(i32 %57, i32 %95)
  %97 = add i32 %96, %62
  %98 = mul i32 %97, 3
  %99 = sext i32 %98 to i64
  %100 = getelementptr float, float* %60, i64 %99
  %101 = load float, float* %100, align 4
  %102 = add i32 %98, 1
  %103 = sext i32 %102 to i64
  %104 = getelementptr float, float* %60, i64 %103
  %105 = load float, float* %104, align 4
  %106 = add i32 %98, 2
  %107 = sext i32 %106 to i64
  %108 = getelementptr float, float* %60, i64 %107
  %109 = load float, float* %108, align 4
  %110 = fadd reassoc ninf nsz float %91, %101
  %111 = fadd reassoc ninf nsz float %92, %105
  %112 = fadd reassoc ninf nsz float %93, %109
  %113 = tail call i32 @llvm.smax.i32(i32 %42, i32 0)
  %114 = tail call i32 @llvm.smin.i32(i32 %50, i32 %113)
  %115 = mul i32 %114, %61
  %116 = add i32 %59, %115
  %117 = mul i32 %116, 3
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, float* %60, i64 %118
  %120 = load float, float* %119, align 4
  %121 = add i32 %117, 1
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, float* %60, i64 %122
  %124 = load float, float* %123, align 4
  %125 = add i32 %117, 2
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, float* %60, i64 %126
  %128 = load float, float* %127, align 4
  %129 = fadd reassoc ninf nsz float %110, %120
  %130 = fadd reassoc ninf nsz float %111, %124
  %131 = fadd reassoc ninf nsz float %112, %128
  %132 = add i32 %77, %115
  %133 = mul i32 %132, 3
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %60, i64 %134
  %136 = load float, float* %135, align 4
  %137 = add i32 %133, 1
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %60, i64 %138
  %140 = load float, float* %139, align 4
  %141 = add i32 %133, 2
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, float* %60, i64 %142
  %144 = load float, float* %143, align 4
  %145 = fadd reassoc ninf nsz float %129, %136
  %146 = fadd reassoc ninf nsz float %130, %140
  %147 = fadd reassoc ninf nsz float %131, %144
  %148 = add i32 %96, %115
  %149 = mul i32 %148, 3
  %150 = sext i32 %149 to i64
  %151 = getelementptr float, float* %60, i64 %150
  %152 = load float, float* %151, align 4
  %153 = add i32 %149, 1
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %60, i64 %154
  %156 = load float, float* %155, align 4
  %157 = add i32 %149, 2
  %158 = sext i32 %157 to i64
  %159 = getelementptr float, float* %60, i64 %158
  %160 = load float, float* %159, align 4
  %161 = fadd reassoc ninf nsz float %145, %152
  %162 = fadd reassoc ninf nsz float %146, %156
  %163 = fadd reassoc ninf nsz float %147, %160
  %164 = add i32 %42, 1
  %165 = tail call i32 @llvm.smax.i32(i32 %164, i32 0)
  %166 = tail call i32 @llvm.smin.i32(i32 %50, i32 %165)
  %167 = mul i32 %166, %61
  %168 = add i32 %59, %167
  %169 = mul i32 %168, 3
  %170 = sext i32 %169 to i64
  %171 = getelementptr float, float* %60, i64 %170
  %172 = load float, float* %171, align 4
  %173 = add i32 %169, 1
  %174 = sext i32 %173 to i64
  %175 = getelementptr float, float* %60, i64 %174
  %176 = load float, float* %175, align 4
  %177 = add i32 %169, 2
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %60, i64 %178
  %180 = load float, float* %179, align 4
  %181 = fadd reassoc ninf nsz float %161, %172
  %182 = fadd reassoc ninf nsz float %162, %176
  %183 = fadd reassoc ninf nsz float %163, %180
  %184 = add i32 %167, %77
  %185 = mul i32 %184, 3
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %60, i64 %186
  %188 = load float, float* %187, align 4
  %189 = add i32 %185, 1
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %60, i64 %190
  %192 = load float, float* %191, align 4
  %193 = add i32 %185, 2
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %60, i64 %194
  %196 = load float, float* %195, align 4
  %197 = fadd reassoc ninf nsz float %181, %188
  %198 = fadd reassoc ninf nsz float %182, %192
  %199 = fadd reassoc ninf nsz float %183, %196
  %200 = add i32 %96, %167
  %201 = mul i32 %200, 3
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %60, i64 %202
  %204 = load float, float* %203, align 4
  %205 = add i32 %201, 1
  %206 = sext i32 %205 to i64
  %207 = getelementptr float, float* %60, i64 %206
  %208 = load float, float* %207, align 4
  %209 = add i32 %201, 2
  %210 = sext i32 %209 to i64
  %211 = getelementptr float, float* %60, i64 %210
  %212 = load float, float* %211, align 4
  %213 = fadd reassoc ninf nsz float %197, %204
  %214 = fadd reassoc ninf nsz float %198, %208
  %215 = fadd reassoc ninf nsz float %199, %212
  %216 = fmul reassoc ninf nsz float %213, 0x3FBC71C720000000
  %217 = fmul reassoc ninf nsz float %214, 0x3FBC71C720000000
  %218 = fmul reassoc ninf nsz float %215, 0x3FBC71C720000000
  %219 = load float*, float** %25, align 8
  %220 = load i32, i32* %26, align 4
  %221 = sub i32 %220, %33
  %222 = mul i32 %221, 3
  %223 = mul i32 %222, %42
  %224 = add i32 %lsr.iv, %223
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, float* %219, i64 %225
  store float %216, float* %226, align 4
  %227 = load float*, float** %25, align 8
  %228 = load i32, i32* %26, align 4
  %229 = sub i32 %228, %33
  %230 = mul i32 %229, 3
  %231 = mul i32 %230, %42
  %232 = add i32 %lsr.iv, %231
  %233 = add i32 %232, 1
  %234 = sext i32 %233 to i64
  %235 = getelementptr float, float* %227, i64 %234
  store float %217, float* %235, align 4
  %236 = load float*, float** %25, align 8
  %237 = load i32, i32* %26, align 4
  %238 = sub i32 %237, %33
  %239 = mul i32 %238, 3
  %240 = mul i32 %239, %42
  %241 = add i32 %lsr.iv, %240
  %242 = add i32 %241, 2
  %243 = sext i32 %242 to i64
  %244 = getelementptr float, float* %236, i64 %243
  store float %218, float* %244, align 4
  %245 = add nsw i32 %.05, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %245
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
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
