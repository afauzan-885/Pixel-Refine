; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.102 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.101 = type { %struct.PreallocatedMemoryChunk.97, %struct.PreallocatedMemoryChunk.97, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.97 = type { ptr, ptr, i64 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_mlri_admm_to_grayscale_3channel_kernel_c96_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %1, i64 0, i32 9
  %3 = load i32, ptr %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %1, i64 0, i32 10
  %6 = load i32, ptr %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.102, ptr %context, i64 0, i32 1
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.101, ptr %9, i64 0, i32 14
  %11 = load ptr, ptr %10, align 8
  %12 = getelementptr inbounds i8, ptr %11, i64 4
  %13 = bitcast ptr %12 to ptr
  store i32 %7, ptr %13, align 4
  %14 = mul i32 %7, %4
  %15 = load ptr, ptr %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.101, ptr %15, i64 0, i32 14
  %17 = bitcast ptr %16 to ptr
  %18 = load ptr, ptr %17, align 8
  store i32 %14, ptr %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_mlri_admm_to_grayscale_3channel_kernel_c96_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast ptr %0 to ptr
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %1)
  %2 = getelementptr inbounds %0, ptr %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, ptr %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, ptr %0, i64 0, i32 0
  store ptr %context, ptr %4, align 8
  store ptr null, ptr %2, align 8
  store i64 1, ptr %3, align 8
  %5 = getelementptr inbounds %0, ptr %0, i64 0, i32 2
  store ptr @function_body, ptr %5, align 8
  %6 = getelementptr inbounds %0, ptr %0, i64 0, i32 3
  store ptr null, ptr %6, align 8
  %7 = getelementptr inbounds %0, ptr %0, i64 0, i32 5
  %8 = bitcast ptr %7 to ptr
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, ptr %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.102, ptr %context, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.101, ptr %10, i64 0, i32 10
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.101, ptr %10, i64 0, i32 9
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.102, ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.101, ptr %4, i64 0, i32 14
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
  %22 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 5
  %23 = load float, ptr %22, align 4
  %24 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 6
  %25 = load float, ptr %24, align 4
  %26 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 8
  %27 = load float, ptr %26, align 4
  %28 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 7
  %29 = load float, ptr %28, align 4
  %30 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %23, float 0x3FB99999A0000000)
  %31 = fadd reassoc ninf nsz float %27, %25
  %32 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %29, float 0x3FB99999A0000000)
  %33 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 3, i32 1
  %34 = load ptr, ptr %33, align 8
  %35 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 3, i32 0, i32 1
  %36 = load i32, ptr %35, align 4
  %37 = getelementptr float, ptr %34, i64 1
  %38 = getelementptr float, ptr %34, i64 2
  %39 = sext i32 %36 to i64
  %40 = getelementptr float, ptr %34, i64 %39
  %41 = add i32 %36, 1
  %42 = sext i32 %41 to i64
  %43 = getelementptr float, ptr %34, i64 %42
  %44 = add i32 %36, 2
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, ptr %34, i64 %45
  %47 = shl i32 %36, 1
  %48 = sext i32 %47 to i64
  %49 = getelementptr float, ptr %34, i64 %48
  %50 = getelementptr float, ptr %49, i64 1
  %51 = add i32 %47, 2
  %52 = sext i32 %51 to i64
  %53 = getelementptr float, ptr %34, i64 %52
  %54 = fmul reassoc ninf nsz float %31, 5.000000e-01
  %55 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %54, float 0x3FB99999A0000000)
  %56 = icmp slt i32 %17, %19
  br i1 %56, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %57 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 1, i32 1
  %58 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 1, i32 0, i32 1
  %59 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 0, i32 1
  %60 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 0, i32 0, i32 1
  %61 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 2, i32 1
  %62 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 2, i32 0, i32 1
  %63 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 4, i32 1
  %64 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %21, i64 0, i32 4, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.07 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %204, %for_loop_body ]
  %65 = load ptr, ptr %3, align 8
  %66 = getelementptr inbounds %struct.LLVMRuntime.101, ptr %65, i64 0, i32 14
  %67 = load ptr, ptr %66, align 8
  %68 = getelementptr inbounds i8, ptr %67, i64 4
  %69 = bitcast ptr %68 to ptr
  %70 = load i32, ptr %69, align 4
  %71 = sdiv i32 %.07, %70
  %72 = mul i32 %71, %70
  %73 = xor i32 %70, %.07
  %74 = icmp slt i32 %73, 0
  %75 = icmp ne i32 %.07, 0
  %76 = icmp ne i32 %.07, %72
  %77 = and i1 %75, %74
  %78 = and i1 %77, %76
  %.neg4 = sext i1 %78 to i32
  %79 = add i32 %71, %.neg4
  %80 = load ptr, ptr %57, align 8
  %81 = load i32, ptr %58, align 4
  %82 = sub i32 %81, %70
  %83 = mul i32 %82, %79
  %84 = add i32 %.07, %83
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, ptr %80, i64 %85
  %87 = load float, ptr %86, align 4
  %88 = load ptr, ptr %59, align 8
  %89 = load i32, ptr %60, align 4
  %90 = sub i32 %89, %70
  %91 = mul i32 %90, %79
  %92 = add i32 %.07, %91
  %93 = sext i32 %92 to i64
  %94 = getelementptr float, ptr %88, i64 %93
  %95 = load float, ptr %94, align 4
  %96 = load ptr, ptr %61, align 8
  %97 = load i32, ptr %62, align 4
  %98 = sub i32 %97, %70
  %99 = mul i32 %98, %79
  %100 = add i32 %.07, %99
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, ptr %96, i64 %101
  %103 = load float, ptr %102, align 4
  %104 = fdiv reassoc ninf nsz float %87, %30
  %105 = fdiv reassoc ninf nsz float %95, %55
  %106 = fdiv reassoc ninf nsz float %103, %32
  %107 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %105, float %106)
  %108 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %104, float %107)
  %109 = fmul reassoc ninf nsz float %108, 0x4011642C80000000
  %110 = fadd reassoc ninf nsz float %109, 0xC00A1642C0000000
  %111 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %110, float 0.000000e+00)
  %112 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %111, float 1.000000e+00)
  %113 = fmul reassoc ninf nsz float %112, %112
  %factor = fmul reassoc ninf nsz float %112, -2.000000e+00
  %114 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %115 = fmul reassoc ninf nsz float %113, %114
  %116 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %95, float %103)
  %117 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %87, float %116)
  %118 = fsub reassoc ninf nsz float 1.000000e+00, %115
  %119 = fmul reassoc ninf nsz float %118, %87
  %120 = fmul reassoc ninf nsz float %115, %117
  %121 = fadd reassoc ninf nsz float %119, %120
  %122 = fmul reassoc ninf nsz float %118, %95
  %123 = fadd reassoc ninf nsz float %122, %120
  %124 = fmul reassoc ninf nsz float %118, %103
  %125 = fadd reassoc ninf nsz float %124, %120
  %126 = load float, ptr %34, align 4
  %127 = fmul reassoc ninf nsz float %121, %126
  %128 = load float, ptr %37, align 4
  %129 = fmul reassoc ninf nsz float %123, %128
  %130 = fadd reassoc ninf nsz float %127, %129
  %131 = load float, ptr %38, align 4
  %132 = fmul reassoc ninf nsz float %125, %131
  %133 = fadd reassoc ninf nsz float %130, %132
  %134 = load float, ptr %40, align 4
  %135 = fmul reassoc ninf nsz float %121, %134
  %136 = load float, ptr %43, align 4
  %137 = fmul reassoc ninf nsz float %123, %136
  %138 = fadd reassoc ninf nsz float %135, %137
  %139 = load float, ptr %46, align 4
  %140 = fmul reassoc ninf nsz float %125, %139
  %141 = fadd reassoc ninf nsz float %138, %140
  %142 = load float, ptr %49, align 4
  %143 = fmul reassoc ninf nsz float %121, %142
  %144 = load float, ptr %50, align 4
  %145 = fmul reassoc ninf nsz float %123, %144
  %146 = fadd reassoc ninf nsz float %143, %145
  %147 = load float, ptr %53, align 4
  %148 = fmul reassoc ninf nsz float %125, %147
  %149 = fadd reassoc ninf nsz float %146, %148
  %150 = fmul reassoc ninf nsz float %133, %133
  %151 = fadd reassoc ninf nsz float %150, 1.000000e+00
  %152 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %151)
  %153 = fdiv reassoc ninf nsz float %133, %152
  %154 = fmul reassoc ninf nsz float %141, %141
  %155 = fadd reassoc ninf nsz float %154, 1.000000e+00
  %156 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %155)
  %157 = fdiv reassoc ninf nsz float %141, %156
  %158 = fmul reassoc ninf nsz float %149, %149
  %159 = fadd reassoc ninf nsz float %158, 1.000000e+00
  %160 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %159)
  %161 = fdiv reassoc ninf nsz float %149, %160
  %162 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %153, float 0.000000e+00)
  %163 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %162, float 1.000000e+00)
  %164 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %163)
  %165 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %157, float 0.000000e+00)
  %166 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %165, float 1.000000e+00)
  %167 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %166)
  %168 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %161, float 0.000000e+00)
  %169 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %168, float 1.000000e+00)
  %170 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %169)
  %171 = fmul reassoc ninf nsz float %164, 0x3FD3A00620000000
  %172 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %171
  %173 = fmul reassoc ninf nsz float %172, %164
  %174 = fadd reassoc ninf nsz float %173, 0xBFE9435AA0000000
  %175 = fmul reassoc ninf nsz float %174, %164
  %176 = fadd reassoc ninf nsz float %175, 0x3FF4E33660000000
  %177 = fmul reassoc ninf nsz float %164, 0x3FD322D0E0000000
  %178 = fmul reassoc ninf nsz float %177, %176
  %179 = fmul reassoc ninf nsz float %167, 0x3FD3A00620000000
  %180 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %179
  %181 = fmul reassoc ninf nsz float %180, %167
  %182 = fadd reassoc ninf nsz float %181, 0xBFE9435AA0000000
  %183 = fmul reassoc ninf nsz float %182, %167
  %184 = fadd reassoc ninf nsz float %183, 0x3FF4E33660000000
  %185 = fmul reassoc ninf nsz float %167, 0x3FE2C8B440000000
  %186 = fmul reassoc ninf nsz float %185, %184
  %187 = fadd reassoc ninf nsz float %178, %186
  %188 = fmul reassoc ninf nsz float %170, 0x3FD3A00620000000
  %189 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %188
  %190 = fmul reassoc ninf nsz float %189, %170
  %191 = fadd reassoc ninf nsz float %190, 0xBFE9435AA0000000
  %192 = fmul reassoc ninf nsz float %191, %170
  %193 = fadd reassoc ninf nsz float %192, 0x3FF4E33660000000
  %194 = fmul reassoc ninf nsz float %170, 0x3FBD2F1AA0000000
  %195 = fmul reassoc ninf nsz float %194, %193
  %196 = fadd reassoc ninf nsz float %187, %195
  %197 = load ptr, ptr %63, align 8
  %198 = load i32, ptr %64, align 4
  %199 = sub i32 %198, %70
  %200 = mul i32 %199, %79
  %201 = add i32 %.07, %200
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, ptr %197, i64 %202
  store float %196, ptr %203, align 4
  %204 = add nsw i32 %.07, 1
  %exitcond.not = icmp eq i32 %19, %204
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.102, align 8
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
  %10 = getelementptr inbounds %struct.RuntimeContext.102, ptr %4, i64 0, i32 2
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
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }

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
