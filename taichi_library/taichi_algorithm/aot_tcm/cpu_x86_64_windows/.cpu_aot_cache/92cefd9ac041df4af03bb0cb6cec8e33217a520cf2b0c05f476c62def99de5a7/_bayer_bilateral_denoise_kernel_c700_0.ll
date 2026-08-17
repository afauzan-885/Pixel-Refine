; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { ptr, ptr, i64 }
%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_bayer_bilateral_denoise_kernel_c82_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %1, i64 0, i32 2
  %3 = load i32, ptr %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, ptr %context, i64 0, i32 1
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %5, i64 0, i32 14
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds i8, ptr %7, i64 8
  %9 = bitcast ptr %8 to ptr
  store i32 %3, ptr %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load ptr, ptr %0, align 8
  %12 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %11, i64 0, i32 3
  %13 = load i32, ptr %12, align 4
  %14 = load ptr, ptr %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %14, i64 0, i32 14
  %16 = load ptr, ptr %15, align 8
  %17 = getelementptr inbounds i8, ptr %16, i64 12
  %18 = bitcast ptr %17 to ptr
  store i32 %13, ptr %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load ptr, ptr %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %20, i64 0, i32 14
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr inbounds i8, ptr %22, i64 4
  %24 = bitcast ptr %23 to ptr
  store i32 %19, ptr %24, align 4
  %25 = mul i32 %19, %10
  %26 = load ptr, ptr %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %26, i64 0, i32 14
  %28 = bitcast ptr %27 to ptr
  %29 = load ptr, ptr %28, align 8
  store i32 %25, ptr %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bayer_bilateral_denoise_kernel_c82_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast ptr %0 to ptr
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 0
  store ptr %context, ptr %4, align 8
  store ptr null, ptr %2, align 8
  store i64 1, ptr %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 2
  store ptr @function_body, ptr %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 3
  store ptr null, ptr %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 5
  %8 = bitcast ptr %7 to ptr
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, ptr %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, ptr %context, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %10, i64 0, i32 10
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %10, i64 0, i32 9
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %4, i64 0, i32 14
  %6 = bitcast ptr %5 to ptr
  %7 = load ptr, ptr %6, align 8
  %8 = load i32, ptr %7, align 4
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
  %20 = bitcast ptr %0 to ptr
  %21 = load ptr, ptr %20, align 8
  %22 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %21, i64 0, i32 4
  %23 = load float, ptr %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = fcmp reassoc ninf nsz ugt float %23, 0.000000e+00
  %26 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %21, i64 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %21, i64 0, i32 0, i32 0, i32 1
  br i1 %25, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  br label %for_loop_body

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %for_loop_body.us, %for_loop_body.us.preheader
  %.06.us = phi i32 [ %226, %for_loop_body.us ], [ %17, %for_loop_body.us.preheader ]
  %28 = load ptr, ptr %3, align 8
  %29 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %28, i64 0, i32 14
  %30 = load ptr, ptr %29, align 8
  %31 = getelementptr inbounds i8, ptr %30, i64 4
  %32 = bitcast ptr %31 to ptr
  %33 = load i32, ptr %32, align 4
  %34 = sdiv i32 %.06.us, %33
  %35 = mul i32 %34, %33
  %36 = xor i32 %33, %.06.us
  %37 = icmp slt i32 %36, 0
  %38 = icmp ne i32 %.06.us, 0
  %39 = icmp ne i32 %.06.us, %35
  %40 = and i1 %38, %37
  %41 = and i1 %40, %39
  %.neg5.us = sext i1 %41 to i32
  %42 = add i32 %34, %.neg5.us
  %43 = mul i32 %33, -1
  %44 = mul i32 %43, %42
  %45 = add i32 %.06.us, %44
  %46 = load ptr, ptr %26, align 8
  %47 = load i32, ptr %27, align 4
  %48 = sub i32 %47, %33
  %49 = mul i32 %48, %42
  %50 = add i32 %.06.us, %49
  %51 = sext i32 %50 to i64
  %52 = getelementptr float, ptr %46, i64 %51
  %53 = load float, ptr %52, align 4
  %54 = fadd reassoc ninf nsz float %53, 0x3F1A36E2E0000000
  %55 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %54)
  %56 = fmul reassoc ninf nsz float %55, %23
  %57 = add i32 %42, -2
  %58 = getelementptr inbounds i8, ptr %30, i64 8
  %59 = bitcast ptr %58 to ptr
  %60 = load i32, ptr %59, align 4
  %61 = add i32 %60, -1
  %62 = tail call i32 @llvm.smax.i32(i32 %57, i32 0)
  %63 = tail call i32 @llvm.smin.i32(i32 %61, i32 %62)
  %64 = add i32 %45, -2
  %65 = getelementptr inbounds i8, ptr %30, i64 12
  %66 = bitcast ptr %65 to ptr
  %67 = load i32, ptr %66, align 4
  %68 = add i32 %67, -1
  %69 = tail call i32 @llvm.smax.i32(i32 %64, i32 0)
  %70 = tail call i32 @llvm.smin.i32(i32 %68, i32 %69)
  %71 = mul i32 %63, %47
  %72 = add i32 %71, %70
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, ptr %46, i64 %73
  %75 = load float, ptr %74, align 4
  %76 = fsub reassoc ninf nsz float %53, %75
  %77 = fneg reassoc ninf nsz float %76
  %neg.us = fmul reassoc ninf nsz float %76, %77
  %78 = fmul reassoc ninf nsz float %56, %56
  %79 = fmul reassoc ninf nsz float %78, 2.000000e+00
  %80 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %79, float 0x3EB0C6F7A0000000)
  %81 = fdiv reassoc ninf nsz float %neg.us, %80
  %82 = tail call float @expf(float noundef %81) #1
  %83 = fmul reassoc ninf nsz float %82, 0x3FD78B5640000000
  %84 = fmul reassoc ninf nsz float %83, %75
  %85 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %86 = tail call i32 @llvm.smin.i32(i32 %68, i32 %85)
  %87 = load ptr, ptr %26, align 8
  %88 = load i32, ptr %27, align 4
  %89 = mul i32 %88, %63
  %90 = add i32 %89, %86
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, ptr %87, i64 %91
  %93 = load float, ptr %92, align 4
  %94 = fsub reassoc ninf nsz float %53, %93
  %95 = fneg reassoc ninf nsz float %94
  %neg1.us = fmul reassoc ninf nsz float %94, %95
  %96 = fdiv reassoc ninf nsz float %neg1.us, %80
  %97 = tail call float @expf(float noundef %96) #1
  %98 = fmul reassoc ninf nsz float %97, 0x3FE368B300000000
  %99 = fmul reassoc ninf nsz float %98, %93
  %100 = fadd reassoc ninf nsz float %99, %84
  %101 = fadd reassoc ninf nsz float %98, %83
  %102 = add i32 %45, 2
  %103 = tail call i32 @llvm.smax.i32(i32 %102, i32 0)
  %104 = tail call i32 @llvm.smin.i32(i32 %68, i32 %103)
  %105 = load ptr, ptr %26, align 8
  %106 = load i32, ptr %27, align 4
  %107 = mul i32 %106, %63
  %108 = add i32 %107, %104
  %109 = sext i32 %108 to i64
  %110 = getelementptr float, ptr %105, i64 %109
  %111 = load float, ptr %110, align 4
  %112 = fsub reassoc ninf nsz float %53, %111
  %113 = fneg reassoc ninf nsz float %112
  %neg2.us = fmul reassoc ninf nsz float %112, %113
  %114 = fdiv reassoc ninf nsz float %neg2.us, %80
  %115 = tail call float @expf(float noundef %114) #1
  %116 = fmul reassoc ninf nsz float %115, 0x3FD78B5640000000
  %117 = fmul reassoc ninf nsz float %116, %111
  %118 = fadd reassoc ninf nsz float %100, %117
  %119 = fadd reassoc ninf nsz float %101, %116
  %120 = tail call i32 @llvm.smax.i32(i32 %42, i32 0)
  %121 = tail call i32 @llvm.smin.i32(i32 %61, i32 %120)
  %122 = load ptr, ptr %26, align 8
  %123 = load i32, ptr %27, align 4
  %124 = mul i32 %123, %121
  %125 = add i32 %124, %70
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, ptr %122, i64 %126
  %128 = load float, ptr %127, align 4
  %129 = fsub reassoc ninf nsz float %53, %128
  %130 = fneg reassoc ninf nsz float %129
  %neg3.us = fmul reassoc ninf nsz float %129, %130
  %131 = fdiv reassoc ninf nsz float %neg3.us, %80
  %132 = tail call float @expf(float noundef %131) #1
  %133 = fmul reassoc ninf nsz float %132, 0x3FE368B300000000
  %134 = fmul reassoc ninf nsz float %133, %128
  %135 = fadd reassoc ninf nsz float %118, %134
  %136 = fadd reassoc ninf nsz float %119, %133
  %137 = load ptr, ptr %26, align 8
  %138 = load i32, ptr %27, align 4
  %139 = mul i32 %138, %121
  %140 = add i32 %139, %86
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, ptr %137, i64 %141
  %143 = load float, ptr %142, align 4
  %144 = fsub reassoc ninf nsz float %53, %143
  %145 = fneg reassoc ninf nsz float %144
  %neg4.us = fmul reassoc ninf nsz float %144, %145
  %146 = fdiv reassoc ninf nsz float %neg4.us, %80
  %147 = tail call float @expf(float noundef %146) #1
  %148 = fmul reassoc ninf nsz float %147, %143
  %149 = fadd reassoc ninf nsz float %135, %148
  %150 = fadd reassoc ninf nsz float %136, %147
  %151 = load ptr, ptr %26, align 8
  %152 = load i32, ptr %27, align 4
  %153 = mul i32 %152, %121
  %154 = add i32 %153, %104
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, ptr %151, i64 %155
  %157 = load float, ptr %156, align 4
  %158 = fsub reassoc ninf nsz float %53, %157
  %159 = fneg reassoc ninf nsz float %158
  %neg5.us = fmul reassoc ninf nsz float %158, %159
  %160 = fdiv reassoc ninf nsz float %neg5.us, %80
  %161 = tail call float @expf(float noundef %160) #1
  %162 = fmul reassoc ninf nsz float %161, 0x3FE368B300000000
  %163 = fmul reassoc ninf nsz float %162, %157
  %164 = fadd reassoc ninf nsz float %149, %163
  %165 = fadd reassoc ninf nsz float %150, %162
  %166 = add i32 %42, 2
  %167 = tail call i32 @llvm.smax.i32(i32 %166, i32 0)
  %168 = tail call i32 @llvm.smin.i32(i32 %61, i32 %167)
  %169 = load ptr, ptr %26, align 8
  %170 = load i32, ptr %27, align 4
  %171 = mul i32 %170, %168
  %172 = add i32 %171, %70
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, ptr %169, i64 %173
  %175 = load float, ptr %174, align 4
  %176 = fsub reassoc ninf nsz float %53, %175
  %177 = fneg reassoc ninf nsz float %176
  %neg6.us = fmul reassoc ninf nsz float %176, %177
  %178 = fdiv reassoc ninf nsz float %neg6.us, %80
  %179 = tail call float @expf(float noundef %178) #1
  %180 = fmul reassoc ninf nsz float %179, 0x3FD78B5640000000
  %181 = fmul reassoc ninf nsz float %180, %175
  %182 = fadd reassoc ninf nsz float %164, %181
  %183 = fadd reassoc ninf nsz float %165, %180
  %184 = load ptr, ptr %26, align 8
  %185 = load i32, ptr %27, align 4
  %186 = mul i32 %185, %168
  %187 = add i32 %186, %86
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, ptr %184, i64 %188
  %190 = load float, ptr %189, align 4
  %191 = fsub reassoc ninf nsz float %53, %190
  %192 = fneg reassoc ninf nsz float %191
  %neg7.us = fmul reassoc ninf nsz float %191, %192
  %193 = fdiv reassoc ninf nsz float %neg7.us, %80
  %194 = tail call float @expf(float noundef %193) #1
  %195 = fmul reassoc ninf nsz float %194, 0x3FE368B300000000
  %196 = fmul reassoc ninf nsz float %195, %190
  %197 = fadd reassoc ninf nsz float %182, %196
  %198 = fadd reassoc ninf nsz float %183, %195
  %199 = load ptr, ptr %26, align 8
  %200 = load i32, ptr %27, align 4
  %201 = mul i32 %200, %168
  %202 = add i32 %201, %104
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, ptr %199, i64 %203
  %205 = load float, ptr %204, align 4
  %206 = fsub reassoc ninf nsz float %53, %205
  %207 = fneg reassoc ninf nsz float %206
  %neg8.us = fmul reassoc ninf nsz float %206, %207
  %208 = fdiv reassoc ninf nsz float %neg8.us, %80
  %209 = tail call float @expf(float noundef %208) #1
  %210 = fmul reassoc ninf nsz float %209, 0x3FD78B5640000000
  %211 = fmul reassoc ninf nsz float %210, %205
  %212 = fadd reassoc ninf nsz float %197, %211
  %213 = fadd reassoc ninf nsz float %198, %210
  %214 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %213, float 0x3EE4F8B580000000)
  %215 = fdiv reassoc ninf nsz float %212, %214
  %216 = load ptr, ptr %20, align 8
  %217 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %216, i64 0, i32 1, i32 1
  %218 = load ptr, ptr %217, align 8
  %219 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %216, i64 0, i32 1, i32 0, i32 1
  %220 = load i32, ptr %219, align 4
  %221 = sub i32 %220, %33
  %222 = mul i32 %221, %42
  %223 = add i32 %.06.us, %222
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, ptr %218, i64 %224
  store float %215, ptr %225, align 4
  %226 = add nsw i32 %.06.us, 1
  %exitcond.not = icmp eq i32 %19, %226
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.preheader
  %.06 = phi i32 [ %260, %for_loop_body ], [ %17, %for_loop_body.preheader ]
  %227 = load ptr, ptr %3, align 8
  %228 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %227, i64 0, i32 14
  %229 = load ptr, ptr %228, align 8
  %230 = getelementptr inbounds i8, ptr %229, i64 4
  %231 = bitcast ptr %230 to ptr
  %232 = load i32, ptr %231, align 4
  %233 = sdiv i32 %.06, %232
  %234 = mul i32 %233, %232
  %235 = xor i32 %232, %.06
  %236 = icmp slt i32 %235, 0
  %237 = icmp ne i32 %.06, 0
  %238 = icmp ne i32 %.06, %234
  %239 = and i1 %237, %236
  %240 = and i1 %239, %238
  %.neg5 = sext i1 %240 to i32
  %241 = add i32 %233, %.neg5
  %242 = load ptr, ptr %26, align 8
  %243 = load i32, ptr %27, align 4
  %244 = sub i32 %243, %232
  %245 = mul i32 %244, %241
  %246 = add i32 %.06, %245
  %247 = sext i32 %246 to i64
  %248 = getelementptr float, ptr %242, i64 %247
  %249 = load float, ptr %248, align 4
  %250 = load ptr, ptr %20, align 8
  %251 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %250, i64 0, i32 1, i32 1
  %252 = load ptr, ptr %251, align 8
  %253 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, float }, ptr %250, i64 0, i32 1, i32 0, i32 1
  %254 = load i32, ptr %253, align 4
  %255 = sub i32 %254, %232
  %256 = mul i32 %255, %241
  %257 = add i32 %.06, %256
  %258 = sext i32 %257 to i64
  %259 = getelementptr float, ptr %252, i64 %258
  store float %249, ptr %259, align 4
  %260 = add nsw i32 %.06, 1
  %exitcond8.not = icmp eq i32 %19, %260
  br i1 %exitcond8.not, label %after_for.loopexit12, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body.us
  br label %after_for

after_for.loopexit12:                             ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit12, %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nofree nounwind willreturn memory(write)
declare dso_local float @expf(float noundef) local_unnamed_addr #4

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #5 {
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast ptr %0 to ptr
  %.sroa.0.0.copyload = load ptr, ptr %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast ptr %.sroa.4.0..sroa_idx to ptr
  %.sroa.4.0.copyload = load ptr, ptr %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast ptr %.sroa.5.0..sroa_idx to ptr
  %.sroa.5.0.copyload = load ptr, ptr %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast ptr %.sroa.7.0..sroa_idx to ptr
  %.sroa.7.0.copyload = load ptr, ptr %.sroa.7.0..sroa_cast, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 32
  %.sroa.8.0..sroa_cast = bitcast ptr %.sroa.8.0..sroa_idx to ptr
  %.sroa.8.0.copyload = load i64, ptr %.sroa.8.0..sroa_cast, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 40
  %.sroa.9.0..sroa_cast = bitcast ptr %.sroa.9.0..sroa_idx to ptr
  %.sroa.9.0.copyload = load i32, ptr %.sroa.9.0..sroa_cast, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 44
  %.sroa.12.0..sroa_cast = bitcast ptr %.sroa.12.0..sroa_idx to ptr
  %.sroa.12.0.copyload = load i32, ptr %.sroa.12.0..sroa_cast, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 48
  %.sroa.15.0..sroa_cast = bitcast ptr %.sroa.15.0..sroa_idx to ptr
  %.sroa.15.0.copyload = load i32, ptr %.sroa.15.0..sroa_cast, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 52
  %.sroa.17.0..sroa_cast = bitcast ptr %.sroa.17.0..sroa_idx to ptr
  %.sroa.17.0.copyload = load i32, ptr %.sroa.17.0..sroa_cast, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq ptr %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast ptr %.sroa.0.0.copyload to ptr
  %9 = bitcast ptr %4 to ptr
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %9, ptr noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, ptr %4, i64 0, i32 2
  store i32 %1, ptr %10, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #7

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { alwaysinline mustprogress nofree nounwind willreturn memory(write) "frame-pointer"="none" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }

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
!7 = !{i32 8, !"PIC Level", i32 2}
!8 = !{i32 7, !"uwtable", i32 1}
!9 = distinct !{!9, !10}
!10 = !{!"llvm.loop.mustprogress"}
!11 = distinct !{!11, !10}
