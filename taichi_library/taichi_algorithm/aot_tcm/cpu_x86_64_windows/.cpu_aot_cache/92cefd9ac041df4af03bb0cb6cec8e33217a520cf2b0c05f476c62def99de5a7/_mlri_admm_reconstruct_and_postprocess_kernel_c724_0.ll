; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { ptr, ptr, i64 }
%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_mlri_admm_reconstruct_and_postprocess_kernel_c134_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %1, i64 0, i32 5
  %3 = load float, ptr %2, align 4
  %4 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %3, float 0x3FB99999A0000000)
  %5 = fdiv reassoc ninf nsz float 1.000000e+00, %4
  %6 = getelementptr inbounds %struct.RuntimeContext.6, ptr %context, i64 0, i32 1
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %7, i64 0, i32 14
  %9 = load ptr, ptr %8, align 8
  %10 = getelementptr inbounds i8, ptr %9, i64 8
  %11 = bitcast ptr %10 to ptr
  store float %5, ptr %11, align 4
  %12 = load ptr, ptr %0, align 8
  %13 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %12, i64 0, i32 6
  %14 = load float, ptr %13, align 4
  %15 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %12, i64 0, i32 8
  %16 = load float, ptr %15, align 4
  %17 = fadd reassoc ninf nsz float %16, %14
  %18 = fmul reassoc ninf nsz float %17, 5.000000e-01
  %19 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %18, float 0x3FB99999A0000000)
  %20 = fdiv reassoc ninf nsz float 1.000000e+00, %19
  %21 = load ptr, ptr %6, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %21, i64 0, i32 14
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds i8, ptr %23, i64 12
  %25 = bitcast ptr %24 to ptr
  store float %20, ptr %25, align 4
  %26 = load ptr, ptr %0, align 8
  %27 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %26, i64 0, i32 7
  %28 = load float, ptr %27, align 4
  %29 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %28, float 0x3FB99999A0000000)
  %30 = fdiv reassoc ninf nsz float 1.000000e+00, %29
  %31 = load ptr, ptr %6, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %31, i64 0, i32 14
  %33 = load ptr, ptr %32, align 8
  %34 = getelementptr inbounds i8, ptr %33, i64 16
  %35 = bitcast ptr %34 to ptr
  store float %30, ptr %35, align 4
  %36 = load ptr, ptr %0, align 8
  %37 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %36, i64 0, i32 9
  %38 = load i32, ptr %37, align 4
  %39 = tail call i32 @llvm.smax.i32(i32 %38, i32 0)
  %40 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %36, i64 0, i32 10
  %41 = load i32, ptr %40, align 4
  %42 = tail call i32 @llvm.smax.i32(i32 %41, i32 0)
  %43 = load ptr, ptr %6, align 8
  %44 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %43, i64 0, i32 14
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds i8, ptr %45, i64 4
  %47 = bitcast ptr %46 to ptr
  store i32 %42, ptr %47, align 4
  %48 = mul i32 %42, %39
  %49 = load ptr, ptr %6, align 8
  %50 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %49, i64 0, i32 14
  %51 = bitcast ptr %50 to ptr
  %52 = load ptr, ptr %51, align 8
  store i32 %48, ptr %52, align 4
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #1

; Function Attrs: nounwind
define void @_mlri_admm_reconstruct_and_postprocess_kernel_c134_0_kernel_1_range_for(ptr %context) local_unnamed_addr #2 {
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
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #2
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #3 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast ptr %0 to ptr
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 1, i32 1
  %24 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 1, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 2, i32 1
  %28 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 2, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 4, i32 1
  %30 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 4, i32 0, i32 1
  %31 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, { { i32, i32, i32 }, ptr }, float, float, float, float, i32, i32 }, ptr %22, i64 0, i32 4, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.010 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %154, %for_loop_body ]
  %32 = load ptr, ptr %3, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %32, i64 0, i32 14
  %34 = load ptr, ptr %33, align 8
  %35 = getelementptr inbounds i8, ptr %34, i64 4
  %36 = bitcast ptr %35 to ptr
  %37 = load i32, ptr %36, align 4
  %38 = sdiv i32 %.010, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %.010
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %.010, 0
  %43 = icmp ne i32 %.010, %39
  %44 = and i1 %42, %41
  %45 = and i1 %44, %43
  %.neg4 = sext i1 %45 to i32
  %46 = add i32 %38, %.neg4
  %47 = load ptr, ptr %23, align 8
  %48 = load i32, ptr %24, align 4
  %49 = sub i32 %48, %37
  %50 = mul i32 %49, %46
  %51 = add i32 %.010, %50
  %52 = sext i32 %51 to i64
  %53 = getelementptr float, ptr %47, i64 %52
  %54 = load float, ptr %53, align 4
  %55 = load ptr, ptr %25, align 8
  %56 = load i32, ptr %26, align 4
  %57 = sub i32 %56, %37
  %58 = mul i32 %57, %46
  %59 = add i32 %.010, %58
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, ptr %55, i64 %60
  %62 = load float, ptr %61, align 4
  %63 = load ptr, ptr %27, align 8
  %64 = load i32, ptr %28, align 4
  %65 = sub i32 %64, %37
  %66 = mul i32 %65, %46
  %67 = add i32 %.010, %66
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, ptr %63, i64 %68
  %70 = load float, ptr %69, align 4
  %71 = getelementptr inbounds i8, ptr %34, i64 8
  %72 = bitcast ptr %71 to ptr
  %73 = load float, ptr %72, align 4
  %74 = fmul reassoc ninf nsz float %73, %54
  %75 = getelementptr inbounds i8, ptr %34, i64 12
  %76 = bitcast ptr %75 to ptr
  %77 = load float, ptr %76, align 4
  %78 = fmul reassoc ninf nsz float %77, %62
  %79 = getelementptr inbounds i8, ptr %34, i64 16
  %80 = bitcast ptr %79 to ptr
  %81 = load float, ptr %80, align 4
  %82 = fmul reassoc ninf nsz float %81, %70
  %83 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %78, float %82)
  %84 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %74, float %83)
  %85 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %78, float %82)
  %86 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %74, float %85)
  %87 = fmul reassoc ninf nsz float %84, 0x40029ACA60000000
  %88 = fadd reassoc ninf nsz float %87, 0xBFF47711E0000000
  %89 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %88, float 0.000000e+00)
  %90 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %89, float 1.000000e+00)
  %factor = fmul reassoc ninf nsz float %90, -2.000000e+00
  %91 = fadd reassoc ninf nsz float %factor, 3.000000e+00
  %92 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %84, float 0x3EE4F8B580000000)
  %93 = fmul reassoc ninf nsz float %86, 0x4001C71C80000000
  %94 = fdiv reassoc ninf nsz float %93, %92
  %95 = fadd reassoc ninf nsz float %94, 0xBFEC71C740000000
  %96 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %95, float 0.000000e+00)
  %97 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %96, float 1.000000e+00)
  %factor9 = fmul reassoc ninf nsz float %97, -2.000000e+00
  %98 = fadd reassoc ninf nsz float %factor9, 3.000000e+00
  %99 = fmul reassoc ninf nsz float %97, %90
  %100 = fmul reassoc ninf nsz float %99, %99
  %101 = fmul reassoc ninf nsz float %100, %91
  %102 = fmul reassoc ninf nsz float %101, %98
  %103 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %62, float %70)
  %104 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %54, float %103)
  %105 = fsub reassoc ninf nsz float 1.000000e+00, %102
  %106 = fmul reassoc ninf nsz float %105, %54
  %107 = fmul reassoc ninf nsz float %102, %104
  %108 = fadd reassoc ninf nsz float %106, %107
  %109 = fmul reassoc ninf nsz float %105, %62
  %110 = fadd reassoc ninf nsz float %109, %107
  %111 = fmul reassoc ninf nsz float %105, %70
  %112 = fadd reassoc ninf nsz float %111, %107
  %113 = fmul reassoc ninf nsz float %108, %108
  %114 = fadd reassoc ninf nsz float %113, 1.000000e+00
  %115 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %114)
  %116 = fdiv reassoc ninf nsz float %108, %115
  %117 = load ptr, ptr %29, align 8
  %118 = load i32, ptr %30, align 4
  %119 = load i32, ptr %31, align 4
  %120 = sub i32 %118, %37
  %121 = mul i32 %120, %46
  %122 = add i32 %.010, %121
  %123 = mul i32 %122, %119
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, ptr %117, i64 %124
  store float %116, ptr %125, align 4
  %126 = fmul reassoc ninf nsz float %110, %110
  %127 = fadd reassoc ninf nsz float %126, 1.000000e+00
  %128 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %127)
  %129 = fdiv reassoc ninf nsz float %110, %128
  %130 = load ptr, ptr %29, align 8
  %131 = load i32, ptr %30, align 4
  %132 = load i32, ptr %31, align 4
  %133 = sub i32 %131, %37
  %134 = mul i32 %133, %46
  %135 = add i32 %.010, %134
  %136 = mul i32 %135, %132
  %137 = add i32 %136, 1
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, ptr %130, i64 %138
  store float %129, ptr %139, align 4
  %140 = fmul reassoc ninf nsz float %112, %112
  %141 = fadd reassoc ninf nsz float %140, 1.000000e+00
  %142 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %141)
  %143 = fdiv reassoc ninf nsz float %112, %142
  %144 = load ptr, ptr %29, align 8
  %145 = load i32, ptr %30, align 4
  %146 = load i32, ptr %31, align 4
  %147 = sub i32 %145, %37
  %148 = mul i32 %147, %46
  %149 = add i32 %.010, %148
  %150 = mul i32 %149, %146
  %151 = add i32 %150, 2
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, ptr %144, i64 %152
  store float %143, ptr %153, align 4
  %154 = add nsw i32 %.010, 1
  %exitcond.not = icmp eq i32 %19, %154
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.sqrt.f32(float) #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #2
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02038) #2
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #2
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
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #2
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #1

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { nounwind }
attributes #3 = { nofree nosync nounwind }
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
