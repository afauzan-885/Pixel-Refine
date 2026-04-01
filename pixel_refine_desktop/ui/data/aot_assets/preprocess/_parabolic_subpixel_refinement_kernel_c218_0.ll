; ModuleID = 'kernel'
source_filename = "kernel"
target triple = "nvptx64-nvidia-cuda"

%struct.RuntimeContext.85 = type { i8*, %struct.LLVMRuntime.84*, i32, i64* }
%struct.LLVMRuntime.84 = type { %struct.PreallocatedMemoryChunk.80, %struct.PreallocatedMemoryChunk.80, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.81*], [1024 x %struct.NodeManager.82*], [1024 x i8*], i8*, %struct.RandState.83*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.80 = type { i8*, i8*, i64 }
%struct.ListManager.81 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.84* }
%struct.NodeManager.82 = type { %struct.LLVMRuntime.84*, i32, i32, i32, i32, %struct.ListManager.81*, %struct.ListManager.81*, %struct.ListManager.81*, i32 }
%struct.RandState.83 = type { i32, i32, i32, i32, i32 }

@"$str" = private addrspace(1) constant [11 x i8] c"__CUDA_FTZ\00"

define void @_parabolic_subpixel_refinement_kernel_c218_0_kernel_0_serial(%struct.RuntimeContext.85* byval(%struct.RuntimeContext.85) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %context, i32 0, i32 0
  %1 = bitcast i8** %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %2 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %1, align 8
  %3 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %2, i32 0, i32 6
  %4 = load i32, i32* %3, align 4
  %5 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %context)
  %6 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %5, i64 8)
  %7 = bitcast i8* %6 to i32*
  store i32 %4, i32* %7, align 4
  %8 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %context, i32 0, i32 0
  %9 = bitcast i8** %8 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %10 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %9, align 8
  %11 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %10, i32 0, i32 7
  %12 = load i32, i32* %11, align 4
  %13 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %context)
  %14 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %13, i64 16)
  %15 = bitcast i8* %14 to i32*
  store i32 %12, i32* %15, align 4
  %16 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %context, i32 0, i32 0
  %17 = bitcast i8** %16 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %18 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %17, align 8
  %19 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %18, i32 0, i32 4
  %20 = load i32, i32* %19, align 4
  %21 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %context)
  %22 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %21, i64 12)
  %23 = bitcast i8* %22 to i32*
  store i32 %20, i32* %23, align 4
  %24 = add i32 %20, %4
  %25 = sub i32 %24, 1
  %26 = sdiv i32 %25, %4
  %27 = icmp slt i32 %25, 0
  %28 = icmp slt i32 %4, 0
  %29 = mul i32 %4, %26
  %30 = icmp ne i1 %27, %28
  %31 = icmp ne i32 %25, 0
  %32 = icmp ne i32 %29, %25
  %33 = icmp ne i1 %30, false
  %34 = icmp ne i1 %31, false
  %35 = and i1 %33, %34
  %36 = icmp ne i1 %35, false
  %37 = icmp ne i1 %32, false
  %38 = and i1 %36, %37
  %39 = zext i1 %38 to i32
  %40 = sub i32 %26, %39
  %41 = call i32 @max_i32(i32 0, i32 %40)
  %42 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %context, i32 0, i32 0
  %43 = bitcast i8** %42 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %44 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %43, align 8
  %45 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %44, i32 0, i32 5
  %46 = load i32, i32* %45, align 4
  %47 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %context)
  %48 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %47, i64 20)
  %49 = bitcast i8* %48 to i32*
  store i32 %46, i32* %49, align 4
  %50 = add i32 %46, %12
  %51 = sub i32 %50, 1
  %52 = sdiv i32 %51, %12
  %53 = icmp slt i32 %51, 0
  %54 = icmp slt i32 %12, 0
  %55 = mul i32 %12, %52
  %56 = icmp ne i1 %53, %54
  %57 = icmp ne i32 %51, 0
  %58 = icmp ne i32 %55, %51
  %59 = icmp ne i1 %56, false
  %60 = icmp ne i1 %57, false
  %61 = and i1 %59, %60
  %62 = icmp ne i1 %61, false
  %63 = icmp ne i1 %58, false
  %64 = and i1 %62, %63
  %65 = zext i1 %64 to i32
  %66 = sub i32 %52, %65
  %67 = call i32 @max_i32(i32 0, i32 %66)
  %68 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %context)
  %69 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %68, i64 4)
  %70 = bitcast i8* %69 to i32*
  store i32 %67, i32* %70, align 4
  %71 = mul i32 %41, %67
  %72 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %context)
  %73 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %72, i64 0)
  %74 = bitcast i8* %73 to i32*
  store i32 %71, i32* %74, align 4
  br label %final
}

define void @_parabolic_subpixel_refinement_kernel_c218_0_kernel_1_range_for(%struct.RuntimeContext.85* byval(%struct.RuntimeContext.85) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %context)
  %1 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %0, i64 0)
  %2 = bitcast i8* %1 to i32*
  %3 = load i32, i32* %2, align 4
  call void @gpu_parallel_range_for(%struct.RuntimeContext.85* %context, i32 0, i32 %3, void (%struct.RuntimeContext.85*, i8*)* null, void (%struct.RuntimeContext.85*, i8*, i32)* @function_body, void (%struct.RuntimeContext.85*, i8*)* null, i64 1)
  br label %final
}

define internal void @function_body(%struct.RuntimeContext.85* %0, i8* %1, i32 %2) {
allocs:
  %3 = alloca i32, align 4
  %4 = alloca float, align 4
  %5 = alloca float, align 4
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  %8 = alloca i32, align 4
  %9 = alloca i32, align 4
  %10 = alloca i32, align 4
  %11 = alloca float, align 4
  %12 = alloca float, align 4
  %13 = alloca i32, align 4
  %14 = alloca i32, align 4
  %15 = alloca i32, align 4
  %16 = alloca i32, align 4
  %17 = alloca i32, align 4
  %18 = alloca float, align 4
  %19 = alloca float, align 4
  %20 = alloca i32, align 4
  %21 = alloca i32, align 4
  %22 = alloca i32, align 4
  %23 = alloca i32, align 4
  %24 = alloca i32, align 4
  %25 = alloca float, align 4
  %26 = alloca float, align 4
  %27 = alloca i32, align 4
  %28 = alloca i32, align 4
  %29 = alloca i32, align 4
  %30 = alloca i32, align 4
  %31 = alloca i32, align 4
  %32 = alloca float, align 4
  %33 = alloca float, align 4
  %34 = alloca i32, align 4
  %35 = alloca i32, align 4
  %36 = alloca i32, align 4
  %37 = alloca i32, align 4
  %38 = alloca i32, align 4
  %39 = alloca float, align 4
  %40 = alloca float, align 4
  %41 = alloca i32, align 4
  %42 = alloca i1, align 1
  br label %entry

final:                                            ; preds = %after_for163
  ret void

entry:                                            ; preds = %allocs
  br label %function_body

function_body:                                    ; preds = %entry
  store i32 %2, i32* %3, align 4
  %43 = load i32, i32* %3, align 4
  %44 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %0)
  %45 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %44, i64 4)
  %46 = bitcast i8* %45 to i32*
  %47 = load i32, i32* %46, align 4
  %48 = sdiv i32 %43, %47
  %49 = icmp slt i32 %43, 0
  %50 = icmp slt i32 %47, 0
  %51 = mul i32 %47, %48
  %52 = icmp ne i1 %49, %50
  %53 = icmp ne i32 %43, 0
  %54 = icmp ne i32 %51, %43
  %55 = icmp ne i1 %52, false
  %56 = icmp ne i1 %53, false
  %57 = and i1 %55, %56
  %58 = icmp ne i1 %57, false
  %59 = icmp ne i1 %54, false
  %60 = and i1 %58, %59
  %61 = zext i1 %60 to i32
  %62 = sub i32 %48, %61
  %63 = mul i32 %62, %47
  %64 = sub i32 %43, %63
  %65 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %0)
  %66 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %65, i64 8)
  %67 = bitcast i8* %66 to i32*
  %68 = load i32, i32* %67, align 4
  %69 = mul i32 %62, %68
  %70 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %0)
  %71 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %70, i64 12)
  %72 = bitcast i8* %71 to i32*
  %73 = load i32, i32* %72, align 4
  %74 = sub i32 %73, %68
  %75 = call i32 @max_i32(i32 0, i32 %69)
  %76 = call i32 @min_i32(i32 %74, i32 %75)
  %77 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %0)
  %78 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %77, i64 16)
  %79 = bitcast i8* %78 to i32*
  %80 = load i32, i32* %79, align 4
  %81 = mul i32 %64, %80
  %82 = call %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* %0)
  %83 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.84* %82, i64 20)
  %84 = bitcast i8* %83 to i32*
  %85 = load i32, i32* %84, align 4
  %86 = sub i32 %85, %80
  %87 = call i32 @max_i32(i32 0, i32 %81)
  %88 = call i32 @min_i32(i32 %86, i32 %87)
  %89 = sdiv i32 %68, 2
  %90 = icmp slt i32 %68, 0
  %91 = shl i32 %89, 1
  %92 = icmp ne i1 %90, false
  %93 = icmp ne i32 %68, 0
  %94 = icmp ne i32 %91, %68
  %95 = icmp ne i1 %92, false
  %96 = icmp ne i1 %93, false
  %97 = and i1 %95, %96
  %98 = icmp ne i1 %97, false
  %99 = icmp ne i1 %94, false
  %100 = and i1 %98, %99
  %101 = zext i1 %100 to i32
  %102 = sub i32 %89, %101
  %103 = add i32 %76, %102
  %104 = sdiv i32 %80, 2
  %105 = icmp slt i32 %80, 0
  %106 = shl i32 %104, 1
  %107 = icmp ne i1 %105, false
  %108 = icmp ne i32 %80, 0
  %109 = icmp ne i32 %106, %80
  %110 = icmp ne i1 %107, false
  %111 = icmp ne i1 %108, false
  %112 = and i1 %110, %111
  %113 = icmp ne i1 %112, false
  %114 = icmp ne i1 %109, false
  %115 = and i1 %113, %114
  %116 = zext i1 %115 to i32
  %117 = sub i32 %104, %116
  %118 = add i32 %88, %117
  %119 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %0, i32 0, i32 0
  %120 = bitcast i8** %119 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %121 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %120, align 8
  %122 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %121, i32 0, i32 2
  %123 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 1
  %124 = load float*, float** %123, align 8
  %125 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 0, i32 0
  %126 = load i32, i32* %125, align 4
  %127 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 0, i32 1
  %128 = load i32, i32* %127, align 4
  %129 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 0, i32 2
  %130 = load i32, i32* %129, align 4
  %131 = mul i32 0, %126
  %132 = add i32 %131, %103
  %133 = mul i32 %132, %128
  %134 = add i32 %133, %118
  %135 = mul i32 %134, %130
  %136 = add i32 %135, 0
  %137 = getelementptr float, float* %124, i32 %136
  %138 = load float, float* %137, align 4
  %139 = call reassoc ninf nsz float @llvm.round.f32(float %138)
  %140 = fptosi float %139 to i32
  %141 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 1
  %142 = load float*, float** %141, align 8
  %143 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 0, i32 0
  %144 = load i32, i32* %143, align 4
  %145 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 0, i32 1
  %146 = load i32, i32* %145, align 4
  %147 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %122, i32 0, i32 0, i32 2
  %148 = load i32, i32* %147, align 4
  %149 = mul i32 0, %144
  %150 = add i32 %149, %103
  %151 = mul i32 %150, %146
  %152 = add i32 %151, %118
  %153 = mul i32 %152, %148
  %154 = add i32 %153, 1
  %155 = getelementptr float, float* %142, i32 %154
  %156 = load float, float* %155, align 4
  %157 = call reassoc ninf nsz float @llvm.round.f32(float %156)
  %158 = fptosi float %157 to i32
  %159 = add i32 %76, %158
  %160 = add i32 %88, %140
  %161 = sub i32 %160, 1
  store float 0.000000e+00, float* %4, align 4
  store float 0.000000e+00, float* %5, align 4
  %162 = call i32 @max_i32(i32 0, i32 %68)
  %163 = call i32 @max_i32(i32 0, i32 %80)
  %164 = mul i32 %162, %163
  %165 = sub i32 %73, 1
  %166 = sub i32 %85, 1
  %167 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %0, i32 0, i32 0
  %168 = bitcast i8** %167 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %169 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %168, align 8
  %170 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %169, i32 0, i32 0
  %171 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %0, i32 0, i32 0
  %172 = bitcast i8** %171 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %173 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %172, align 8
  %174 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %173, i32 0, i32 1
  %175 = icmp slt i32 %163, 0
  store i32 0, i32* %6, align 4
  br label %for_loop_test

for_loop_body:                                    ; preds = %for_loop_test
  %176 = load i32, i32* %6, align 4
  %177 = sdiv i32 %176, %163
  %178 = icmp slt i32 %176, 0
  %179 = mul i32 %163, %177
  %180 = icmp ne i1 %178, %175
  %181 = icmp ne i32 %176, 0
  %182 = icmp ne i32 %179, %176
  %183 = icmp ne i1 %180, false
  %184 = icmp ne i1 %181, false
  %185 = and i1 %183, %184
  %186 = icmp ne i1 %185, false
  %187 = icmp ne i1 %182, false
  %188 = and i1 %186, %187
  %189 = zext i1 %188 to i32
  %190 = sub i32 %177, %189
  %191 = mul i32 %190, %163
  %192 = sub i32 %176, %191
  %193 = add i32 %76, %190
  store i32 0, i32* %7, align 4
  store i32 %193, i32* %7, align 4
  %194 = icmp slt i32 %193, 0
  %195 = icmp ne i1 %194, false
  br i1 %195, label %true_block, label %false_block

for_loop_inc:                                     ; preds = %after_if24
  %196 = load i32, i32* %6, align 4
  %197 = add i32 %196, 1
  store i32 %197, i32* %6, align 4
  br label %for_loop_test

after_for:                                        ; preds = %for_loop_test
  %198 = mul i32 %68, %80
  %199 = sitofp i32 %198 to float
  %200 = load float, float* %4, align 4
  %201 = fdiv reassoc ninf nsz float %200, %199
  %202 = load float, float* %5, align 4
  %203 = fdiv reassoc ninf nsz float %202, %199
  %204 = fmul reassoc ninf nsz float %201, %201
  %205 = fsub reassoc ninf nsz float %203, %204
  %206 = call reassoc ninf nsz float @llvm.maxnum.f32(float 0.000000e+00, float %205)
  %207 = add i32 %160, 1
  store float 0.000000e+00, float* %11, align 4
  store float 0.000000e+00, float* %12, align 4
  store i32 0, i32* %13, align 4
  br label %for_loop_test28

for_loop_test:                                    ; preds = %for_loop_inc, %function_body
  %208 = load i32, i32* %6, align 4
  %209 = icmp slt i32 %208, %164
  br i1 %209, label %for_loop_body, label %after_for

true_block:                                       ; preds = %for_loop_body
  %neg = sub i32 0, %193
  store i32 %neg, i32* %7, align 4
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  br label %after_if

after_if:                                         ; preds = %false_block, %true_block
  %210 = load i32, i32* %7, align 4
  %211 = load i32, i32* %72, align 4
  %212 = icmp sge i32 %210, %211
  %213 = icmp ne i1 %212, false
  br i1 %213, label %true_block1, label %false_block2

true_block1:                                      ; preds = %after_if
  %214 = shl i32 %165, 1
  %215 = load i32, i32* %7, align 4
  %216 = sub i32 %214, %215
  store i32 %216, i32* %7, align 4
  br label %after_if3

false_block2:                                     ; preds = %after_if
  br label %after_if3

after_if3:                                        ; preds = %false_block2, %true_block1
  %217 = load i32, i32* %7, align 4
  %218 = call i32 @max_i32(i32 0, i32 %217)
  %219 = call i32 @min_i32(i32 %165, i32 %218)
  %220 = add i32 %88, %192
  store i32 0, i32* %8, align 4
  store i32 %220, i32* %8, align 4
  %221 = icmp slt i32 %220, 0
  %222 = icmp ne i1 %221, false
  br i1 %222, label %true_block4, label %false_block5

true_block4:                                      ; preds = %after_if3
  %neg7 = sub i32 0, %220
  store i32 %neg7, i32* %8, align 4
  br label %after_if6

false_block5:                                     ; preds = %after_if3
  br label %after_if6

after_if6:                                        ; preds = %false_block5, %true_block4
  %223 = load i32, i32* %8, align 4
  %224 = load i32, i32* %84, align 4
  %225 = icmp sge i32 %223, %224
  %226 = icmp ne i1 %225, false
  br i1 %226, label %true_block8, label %false_block9

true_block8:                                      ; preds = %after_if6
  %227 = shl i32 %166, 1
  %228 = load i32, i32* %8, align 4
  %229 = sub i32 %227, %228
  store i32 %229, i32* %8, align 4
  br label %after_if10

false_block9:                                     ; preds = %after_if6
  br label %after_if10

after_if10:                                       ; preds = %false_block9, %true_block8
  %230 = load i32, i32* %8, align 4
  %231 = call i32 @max_i32(i32 0, i32 %230)
  %232 = call i32 @min_i32(i32 %166, i32 %231)
  %233 = add i32 %159, %190
  store i32 0, i32* %9, align 4
  store i32 %233, i32* %9, align 4
  %234 = icmp slt i32 %233, 0
  %235 = icmp ne i1 %234, false
  br i1 %235, label %true_block11, label %false_block12

true_block11:                                     ; preds = %after_if10
  %neg14 = sub i32 0, %233
  store i32 %neg14, i32* %9, align 4
  br label %after_if13

false_block12:                                    ; preds = %after_if10
  br label %after_if13

after_if13:                                       ; preds = %false_block12, %true_block11
  %236 = load i32, i32* %9, align 4
  %237 = icmp sge i32 %236, %211
  %238 = icmp ne i1 %237, false
  br i1 %238, label %true_block15, label %false_block16

true_block15:                                     ; preds = %after_if13
  %239 = shl i32 %165, 1
  %240 = load i32, i32* %9, align 4
  %241 = sub i32 %239, %240
  store i32 %241, i32* %9, align 4
  br label %after_if17

false_block16:                                    ; preds = %after_if13
  br label %after_if17

after_if17:                                       ; preds = %false_block16, %true_block15
  %242 = load i32, i32* %9, align 4
  %243 = call i32 @max_i32(i32 0, i32 %242)
  %244 = call i32 @min_i32(i32 %165, i32 %243)
  %245 = add i32 %161, %192
  store i32 0, i32* %10, align 4
  store i32 %245, i32* %10, align 4
  %246 = icmp slt i32 %245, 0
  %247 = icmp ne i1 %246, false
  br i1 %247, label %true_block18, label %false_block19

true_block18:                                     ; preds = %after_if17
  %neg21 = sub i32 0, %245
  store i32 %neg21, i32* %10, align 4
  br label %after_if20

false_block19:                                    ; preds = %after_if17
  br label %after_if20

after_if20:                                       ; preds = %false_block19, %true_block18
  %248 = load i32, i32* %10, align 4
  %249 = icmp sge i32 %248, %224
  %250 = icmp ne i1 %249, false
  br i1 %250, label %true_block22, label %false_block23

true_block22:                                     ; preds = %after_if20
  %251 = shl i32 %166, 1
  %252 = load i32, i32* %10, align 4
  %253 = sub i32 %251, %252
  store i32 %253, i32* %10, align 4
  br label %after_if24

false_block23:                                    ; preds = %after_if20
  br label %after_if24

after_if24:                                       ; preds = %false_block23, %true_block22
  %254 = load i32, i32* %10, align 4
  %255 = call i32 @max_i32(i32 0, i32 %254)
  %256 = call i32 @min_i32(i32 %166, i32 %255)
  %257 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 1
  %258 = load float*, float** %257, align 8
  %259 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 0
  %260 = load i32, i32* %259, align 4
  %261 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 1
  %262 = load i32, i32* %261, align 4
  %263 = mul i32 0, %260
  %264 = add i32 %263, %219
  %265 = mul i32 %264, %262
  %266 = add i32 %265, %232
  %267 = getelementptr float, float* %258, i32 %266
  %268 = load float, float* %267, align 4
  %269 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 1
  %270 = load float*, float** %269, align 8
  %271 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 0
  %272 = load i32, i32* %271, align 4
  %273 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 1
  %274 = load i32, i32* %273, align 4
  %275 = mul i32 0, %272
  %276 = add i32 %275, %244
  %277 = mul i32 %276, %274
  %278 = add i32 %277, %256
  %279 = getelementptr float, float* %270, i32 %278
  %280 = load float, float* %279, align 4
  %281 = fsub reassoc ninf nsz float %268, %280
  %282 = load float, float* %4, align 4
  %283 = fadd reassoc ninf nsz float %282, %281
  store float %283, float* %4, align 4
  %284 = fmul reassoc ninf nsz float %281, %281
  %285 = load float, float* %5, align 4
  %286 = fadd reassoc ninf nsz float %285, %284
  store float %286, float* %5, align 4
  br label %for_loop_inc

for_loop_body25:                                  ; preds = %for_loop_test28
  %287 = load i32, i32* %13, align 4
  %288 = sdiv i32 %287, %163
  %289 = icmp slt i32 %287, 0
  %290 = mul i32 %163, %288
  %291 = icmp ne i1 %289, %175
  %292 = icmp ne i32 %287, 0
  %293 = icmp ne i32 %290, %287
  %294 = icmp ne i1 %291, false
  %295 = icmp ne i1 %292, false
  %296 = and i1 %294, %295
  %297 = icmp ne i1 %296, false
  %298 = icmp ne i1 %293, false
  %299 = and i1 %297, %298
  %300 = zext i1 %299 to i32
  %301 = sub i32 %288, %300
  %302 = mul i32 %301, %163
  %303 = sub i32 %287, %302
  %304 = add i32 %76, %301
  store i32 0, i32* %14, align 4
  store i32 %304, i32* %14, align 4
  %305 = icmp slt i32 %304, 0
  %306 = icmp ne i1 %305, false
  br i1 %306, label %true_block29, label %false_block30

for_loop_inc26:                                   ; preds = %after_if56
  %307 = load i32, i32* %13, align 4
  %308 = add i32 %307, 1
  store i32 %308, i32* %13, align 4
  br label %for_loop_test28

after_for27:                                      ; preds = %for_loop_test28
  %309 = load float, float* %11, align 4
  %310 = fdiv reassoc ninf nsz float %309, %199
  %311 = load float, float* %12, align 4
  %312 = fdiv reassoc ninf nsz float %311, %199
  %313 = fmul reassoc ninf nsz float %310, %310
  %314 = fsub reassoc ninf nsz float %312, %313
  %315 = call reassoc ninf nsz float @llvm.maxnum.f32(float 0.000000e+00, float %314)
  store float 0.000000e+00, float* %18, align 4
  store float 0.000000e+00, float* %19, align 4
  store i32 0, i32* %20, align 4
  br label %for_loop_test60

for_loop_test28:                                  ; preds = %for_loop_inc26, %after_for
  %316 = load i32, i32* %13, align 4
  %317 = icmp slt i32 %316, %164
  br i1 %317, label %for_loop_body25, label %after_for27

true_block29:                                     ; preds = %for_loop_body25
  %neg32 = sub i32 0, %304
  store i32 %neg32, i32* %14, align 4
  br label %after_if31

false_block30:                                    ; preds = %for_loop_body25
  br label %after_if31

after_if31:                                       ; preds = %false_block30, %true_block29
  %318 = load i32, i32* %14, align 4
  %319 = load i32, i32* %72, align 4
  %320 = icmp sge i32 %318, %319
  %321 = icmp ne i1 %320, false
  br i1 %321, label %true_block33, label %false_block34

true_block33:                                     ; preds = %after_if31
  %322 = shl i32 %165, 1
  %323 = load i32, i32* %14, align 4
  %324 = sub i32 %322, %323
  store i32 %324, i32* %14, align 4
  br label %after_if35

false_block34:                                    ; preds = %after_if31
  br label %after_if35

after_if35:                                       ; preds = %false_block34, %true_block33
  %325 = load i32, i32* %14, align 4
  %326 = call i32 @max_i32(i32 0, i32 %325)
  %327 = call i32 @min_i32(i32 %165, i32 %326)
  %328 = add i32 %88, %303
  store i32 0, i32* %15, align 4
  store i32 %328, i32* %15, align 4
  %329 = icmp slt i32 %328, 0
  %330 = icmp ne i1 %329, false
  br i1 %330, label %true_block36, label %false_block37

true_block36:                                     ; preds = %after_if35
  %neg39 = sub i32 0, %328
  store i32 %neg39, i32* %15, align 4
  br label %after_if38

false_block37:                                    ; preds = %after_if35
  br label %after_if38

after_if38:                                       ; preds = %false_block37, %true_block36
  %331 = load i32, i32* %15, align 4
  %332 = load i32, i32* %84, align 4
  %333 = icmp sge i32 %331, %332
  %334 = icmp ne i1 %333, false
  br i1 %334, label %true_block40, label %false_block41

true_block40:                                     ; preds = %after_if38
  %335 = shl i32 %166, 1
  %336 = load i32, i32* %15, align 4
  %337 = sub i32 %335, %336
  store i32 %337, i32* %15, align 4
  br label %after_if42

false_block41:                                    ; preds = %after_if38
  br label %after_if42

after_if42:                                       ; preds = %false_block41, %true_block40
  %338 = load i32, i32* %15, align 4
  %339 = call i32 @max_i32(i32 0, i32 %338)
  %340 = call i32 @min_i32(i32 %166, i32 %339)
  %341 = add i32 %159, %301
  store i32 0, i32* %16, align 4
  store i32 %341, i32* %16, align 4
  %342 = icmp slt i32 %341, 0
  %343 = icmp ne i1 %342, false
  br i1 %343, label %true_block43, label %false_block44

true_block43:                                     ; preds = %after_if42
  %neg46 = sub i32 0, %341
  store i32 %neg46, i32* %16, align 4
  br label %after_if45

false_block44:                                    ; preds = %after_if42
  br label %after_if45

after_if45:                                       ; preds = %false_block44, %true_block43
  %344 = load i32, i32* %16, align 4
  %345 = icmp sge i32 %344, %319
  %346 = icmp ne i1 %345, false
  br i1 %346, label %true_block47, label %false_block48

true_block47:                                     ; preds = %after_if45
  %347 = shl i32 %165, 1
  %348 = load i32, i32* %16, align 4
  %349 = sub i32 %347, %348
  store i32 %349, i32* %16, align 4
  br label %after_if49

false_block48:                                    ; preds = %after_if45
  br label %after_if49

after_if49:                                       ; preds = %false_block48, %true_block47
  %350 = load i32, i32* %16, align 4
  %351 = call i32 @max_i32(i32 0, i32 %350)
  %352 = call i32 @min_i32(i32 %165, i32 %351)
  %353 = add i32 %207, %303
  store i32 0, i32* %17, align 4
  store i32 %353, i32* %17, align 4
  %354 = icmp slt i32 %353, 0
  %355 = icmp ne i1 %354, false
  br i1 %355, label %true_block50, label %false_block51

true_block50:                                     ; preds = %after_if49
  %neg53 = sub i32 0, %353
  store i32 %neg53, i32* %17, align 4
  br label %after_if52

false_block51:                                    ; preds = %after_if49
  br label %after_if52

after_if52:                                       ; preds = %false_block51, %true_block50
  %356 = load i32, i32* %17, align 4
  %357 = icmp sge i32 %356, %332
  %358 = icmp ne i1 %357, false
  br i1 %358, label %true_block54, label %false_block55

true_block54:                                     ; preds = %after_if52
  %359 = shl i32 %166, 1
  %360 = load i32, i32* %17, align 4
  %361 = sub i32 %359, %360
  store i32 %361, i32* %17, align 4
  br label %after_if56

false_block55:                                    ; preds = %after_if52
  br label %after_if56

after_if56:                                       ; preds = %false_block55, %true_block54
  %362 = load i32, i32* %17, align 4
  %363 = call i32 @max_i32(i32 0, i32 %362)
  %364 = call i32 @min_i32(i32 %166, i32 %363)
  %365 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 1
  %366 = load float*, float** %365, align 8
  %367 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 0
  %368 = load i32, i32* %367, align 4
  %369 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 1
  %370 = load i32, i32* %369, align 4
  %371 = mul i32 0, %368
  %372 = add i32 %371, %327
  %373 = mul i32 %372, %370
  %374 = add i32 %373, %340
  %375 = getelementptr float, float* %366, i32 %374
  %376 = load float, float* %375, align 4
  %377 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 1
  %378 = load float*, float** %377, align 8
  %379 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 0
  %380 = load i32, i32* %379, align 4
  %381 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 1
  %382 = load i32, i32* %381, align 4
  %383 = mul i32 0, %380
  %384 = add i32 %383, %352
  %385 = mul i32 %384, %382
  %386 = add i32 %385, %364
  %387 = getelementptr float, float* %378, i32 %386
  %388 = load float, float* %387, align 4
  %389 = fsub reassoc ninf nsz float %376, %388
  %390 = load float, float* %11, align 4
  %391 = fadd reassoc ninf nsz float %390, %389
  store float %391, float* %11, align 4
  %392 = fmul reassoc ninf nsz float %389, %389
  %393 = load float, float* %12, align 4
  %394 = fadd reassoc ninf nsz float %393, %392
  store float %394, float* %12, align 4
  br label %for_loop_inc26

for_loop_body57:                                  ; preds = %for_loop_test60
  %395 = load i32, i32* %20, align 4
  %396 = sdiv i32 %395, %163
  %397 = icmp slt i32 %395, 0
  %398 = mul i32 %163, %396
  %399 = icmp ne i1 %397, %175
  %400 = icmp ne i32 %395, 0
  %401 = icmp ne i32 %398, %395
  %402 = icmp ne i1 %399, false
  %403 = icmp ne i1 %400, false
  %404 = and i1 %402, %403
  %405 = icmp ne i1 %404, false
  %406 = icmp ne i1 %401, false
  %407 = and i1 %405, %406
  %408 = zext i1 %407 to i32
  %409 = sub i32 %396, %408
  %410 = mul i32 %409, %163
  %411 = sub i32 %395, %410
  %412 = add i32 %76, %409
  store i32 0, i32* %21, align 4
  store i32 %412, i32* %21, align 4
  %413 = icmp slt i32 %412, 0
  %414 = icmp ne i1 %413, false
  br i1 %414, label %true_block61, label %false_block62

for_loop_inc58:                                   ; preds = %after_if88
  %415 = load i32, i32* %20, align 4
  %416 = add i32 %415, 1
  store i32 %416, i32* %20, align 4
  br label %for_loop_test60

after_for59:                                      ; preds = %for_loop_test60
  %417 = load float, float* %18, align 4
  %418 = fdiv reassoc ninf nsz float %417, %199
  %419 = load float, float* %19, align 4
  %420 = fdiv reassoc ninf nsz float %419, %199
  %421 = fmul reassoc ninf nsz float %418, %418
  %422 = fsub reassoc ninf nsz float %420, %421
  %423 = call reassoc ninf nsz float @llvm.maxnum.f32(float 0.000000e+00, float %422)
  %424 = sub i32 %159, 1
  store float 0.000000e+00, float* %25, align 4
  store float 0.000000e+00, float* %26, align 4
  store i32 0, i32* %27, align 4
  br label %for_loop_test92

for_loop_test60:                                  ; preds = %for_loop_inc58, %after_for27
  %425 = load i32, i32* %20, align 4
  %426 = icmp slt i32 %425, %164
  br i1 %426, label %for_loop_body57, label %after_for59

true_block61:                                     ; preds = %for_loop_body57
  %neg64 = sub i32 0, %412
  store i32 %neg64, i32* %21, align 4
  br label %after_if63

false_block62:                                    ; preds = %for_loop_body57
  br label %after_if63

after_if63:                                       ; preds = %false_block62, %true_block61
  %427 = load i32, i32* %21, align 4
  %428 = load i32, i32* %72, align 4
  %429 = icmp sge i32 %427, %428
  %430 = icmp ne i1 %429, false
  br i1 %430, label %true_block65, label %false_block66

true_block65:                                     ; preds = %after_if63
  %431 = shl i32 %165, 1
  %432 = load i32, i32* %21, align 4
  %433 = sub i32 %431, %432
  store i32 %433, i32* %21, align 4
  br label %after_if67

false_block66:                                    ; preds = %after_if63
  br label %after_if67

after_if67:                                       ; preds = %false_block66, %true_block65
  %434 = load i32, i32* %21, align 4
  %435 = call i32 @max_i32(i32 0, i32 %434)
  %436 = call i32 @min_i32(i32 %165, i32 %435)
  %437 = add i32 %88, %411
  store i32 0, i32* %22, align 4
  store i32 %437, i32* %22, align 4
  %438 = icmp slt i32 %437, 0
  %439 = icmp ne i1 %438, false
  br i1 %439, label %true_block68, label %false_block69

true_block68:                                     ; preds = %after_if67
  %neg71 = sub i32 0, %437
  store i32 %neg71, i32* %22, align 4
  br label %after_if70

false_block69:                                    ; preds = %after_if67
  br label %after_if70

after_if70:                                       ; preds = %false_block69, %true_block68
  %440 = load i32, i32* %22, align 4
  %441 = load i32, i32* %84, align 4
  %442 = icmp sge i32 %440, %441
  %443 = icmp ne i1 %442, false
  br i1 %443, label %true_block72, label %false_block73

true_block72:                                     ; preds = %after_if70
  %444 = shl i32 %166, 1
  %445 = load i32, i32* %22, align 4
  %446 = sub i32 %444, %445
  store i32 %446, i32* %22, align 4
  br label %after_if74

false_block73:                                    ; preds = %after_if70
  br label %after_if74

after_if74:                                       ; preds = %false_block73, %true_block72
  %447 = load i32, i32* %22, align 4
  %448 = call i32 @max_i32(i32 0, i32 %447)
  %449 = call i32 @min_i32(i32 %166, i32 %448)
  %450 = add i32 %159, %409
  store i32 0, i32* %23, align 4
  store i32 %450, i32* %23, align 4
  %451 = icmp slt i32 %450, 0
  %452 = icmp ne i1 %451, false
  br i1 %452, label %true_block75, label %false_block76

true_block75:                                     ; preds = %after_if74
  %neg78 = sub i32 0, %450
  store i32 %neg78, i32* %23, align 4
  br label %after_if77

false_block76:                                    ; preds = %after_if74
  br label %after_if77

after_if77:                                       ; preds = %false_block76, %true_block75
  %453 = load i32, i32* %23, align 4
  %454 = icmp sge i32 %453, %428
  %455 = icmp ne i1 %454, false
  br i1 %455, label %true_block79, label %false_block80

true_block79:                                     ; preds = %after_if77
  %456 = shl i32 %165, 1
  %457 = load i32, i32* %23, align 4
  %458 = sub i32 %456, %457
  store i32 %458, i32* %23, align 4
  br label %after_if81

false_block80:                                    ; preds = %after_if77
  br label %after_if81

after_if81:                                       ; preds = %false_block80, %true_block79
  %459 = load i32, i32* %23, align 4
  %460 = call i32 @max_i32(i32 0, i32 %459)
  %461 = call i32 @min_i32(i32 %165, i32 %460)
  %462 = add i32 %160, %411
  store i32 0, i32* %24, align 4
  store i32 %462, i32* %24, align 4
  %463 = icmp slt i32 %462, 0
  %464 = icmp ne i1 %463, false
  br i1 %464, label %true_block82, label %false_block83

true_block82:                                     ; preds = %after_if81
  %neg85 = sub i32 0, %462
  store i32 %neg85, i32* %24, align 4
  br label %after_if84

false_block83:                                    ; preds = %after_if81
  br label %after_if84

after_if84:                                       ; preds = %false_block83, %true_block82
  %465 = load i32, i32* %24, align 4
  %466 = icmp sge i32 %465, %441
  %467 = icmp ne i1 %466, false
  br i1 %467, label %true_block86, label %false_block87

true_block86:                                     ; preds = %after_if84
  %468 = shl i32 %166, 1
  %469 = load i32, i32* %24, align 4
  %470 = sub i32 %468, %469
  store i32 %470, i32* %24, align 4
  br label %after_if88

false_block87:                                    ; preds = %after_if84
  br label %after_if88

after_if88:                                       ; preds = %false_block87, %true_block86
  %471 = load i32, i32* %24, align 4
  %472 = call i32 @max_i32(i32 0, i32 %471)
  %473 = call i32 @min_i32(i32 %166, i32 %472)
  %474 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 1
  %475 = load float*, float** %474, align 8
  %476 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 0
  %477 = load i32, i32* %476, align 4
  %478 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 1
  %479 = load i32, i32* %478, align 4
  %480 = mul i32 0, %477
  %481 = add i32 %480, %436
  %482 = mul i32 %481, %479
  %483 = add i32 %482, %449
  %484 = getelementptr float, float* %475, i32 %483
  %485 = load float, float* %484, align 4
  %486 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 1
  %487 = load float*, float** %486, align 8
  %488 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 0
  %489 = load i32, i32* %488, align 4
  %490 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 1
  %491 = load i32, i32* %490, align 4
  %492 = mul i32 0, %489
  %493 = add i32 %492, %461
  %494 = mul i32 %493, %491
  %495 = add i32 %494, %473
  %496 = getelementptr float, float* %487, i32 %495
  %497 = load float, float* %496, align 4
  %498 = fsub reassoc ninf nsz float %485, %497
  %499 = load float, float* %18, align 4
  %500 = fadd reassoc ninf nsz float %499, %498
  store float %500, float* %18, align 4
  %501 = fmul reassoc ninf nsz float %498, %498
  %502 = load float, float* %19, align 4
  %503 = fadd reassoc ninf nsz float %502, %501
  store float %503, float* %19, align 4
  br label %for_loop_inc58

for_loop_body89:                                  ; preds = %for_loop_test92
  %504 = load i32, i32* %27, align 4
  %505 = sdiv i32 %504, %163
  %506 = icmp slt i32 %504, 0
  %507 = mul i32 %163, %505
  %508 = icmp ne i1 %506, %175
  %509 = icmp ne i32 %504, 0
  %510 = icmp ne i32 %507, %504
  %511 = icmp ne i1 %508, false
  %512 = icmp ne i1 %509, false
  %513 = and i1 %511, %512
  %514 = icmp ne i1 %513, false
  %515 = icmp ne i1 %510, false
  %516 = and i1 %514, %515
  %517 = zext i1 %516 to i32
  %518 = sub i32 %505, %517
  %519 = mul i32 %518, %163
  %520 = sub i32 %504, %519
  %521 = add i32 %76, %518
  store i32 0, i32* %28, align 4
  store i32 %521, i32* %28, align 4
  %522 = icmp slt i32 %521, 0
  %523 = icmp ne i1 %522, false
  br i1 %523, label %true_block93, label %false_block94

for_loop_inc90:                                   ; preds = %after_if120
  %524 = load i32, i32* %27, align 4
  %525 = add i32 %524, 1
  store i32 %525, i32* %27, align 4
  br label %for_loop_test92

after_for91:                                      ; preds = %for_loop_test92
  %526 = load float, float* %25, align 4
  %527 = fdiv reassoc ninf nsz float %526, %199
  %528 = load float, float* %26, align 4
  %529 = fdiv reassoc ninf nsz float %528, %199
  %530 = fmul reassoc ninf nsz float %527, %527
  %531 = fsub reassoc ninf nsz float %529, %530
  %532 = call reassoc ninf nsz float @llvm.maxnum.f32(float 0.000000e+00, float %531)
  %533 = add i32 %159, 1
  store float 0.000000e+00, float* %32, align 4
  store float 0.000000e+00, float* %33, align 4
  store i32 0, i32* %34, align 4
  br label %for_loop_test124

for_loop_test92:                                  ; preds = %for_loop_inc90, %after_for59
  %534 = load i32, i32* %27, align 4
  %535 = icmp slt i32 %534, %164
  br i1 %535, label %for_loop_body89, label %after_for91

true_block93:                                     ; preds = %for_loop_body89
  %neg96 = sub i32 0, %521
  store i32 %neg96, i32* %28, align 4
  br label %after_if95

false_block94:                                    ; preds = %for_loop_body89
  br label %after_if95

after_if95:                                       ; preds = %false_block94, %true_block93
  %536 = load i32, i32* %28, align 4
  %537 = load i32, i32* %72, align 4
  %538 = icmp sge i32 %536, %537
  %539 = icmp ne i1 %538, false
  br i1 %539, label %true_block97, label %false_block98

true_block97:                                     ; preds = %after_if95
  %540 = shl i32 %165, 1
  %541 = load i32, i32* %28, align 4
  %542 = sub i32 %540, %541
  store i32 %542, i32* %28, align 4
  br label %after_if99

false_block98:                                    ; preds = %after_if95
  br label %after_if99

after_if99:                                       ; preds = %false_block98, %true_block97
  %543 = load i32, i32* %28, align 4
  %544 = call i32 @max_i32(i32 0, i32 %543)
  %545 = call i32 @min_i32(i32 %165, i32 %544)
  %546 = add i32 %88, %520
  store i32 0, i32* %29, align 4
  store i32 %546, i32* %29, align 4
  %547 = icmp slt i32 %546, 0
  %548 = icmp ne i1 %547, false
  br i1 %548, label %true_block100, label %false_block101

true_block100:                                    ; preds = %after_if99
  %neg103 = sub i32 0, %546
  store i32 %neg103, i32* %29, align 4
  br label %after_if102

false_block101:                                   ; preds = %after_if99
  br label %after_if102

after_if102:                                      ; preds = %false_block101, %true_block100
  %549 = load i32, i32* %29, align 4
  %550 = load i32, i32* %84, align 4
  %551 = icmp sge i32 %549, %550
  %552 = icmp ne i1 %551, false
  br i1 %552, label %true_block104, label %false_block105

true_block104:                                    ; preds = %after_if102
  %553 = shl i32 %166, 1
  %554 = load i32, i32* %29, align 4
  %555 = sub i32 %553, %554
  store i32 %555, i32* %29, align 4
  br label %after_if106

false_block105:                                   ; preds = %after_if102
  br label %after_if106

after_if106:                                      ; preds = %false_block105, %true_block104
  %556 = load i32, i32* %29, align 4
  %557 = call i32 @max_i32(i32 0, i32 %556)
  %558 = call i32 @min_i32(i32 %166, i32 %557)
  %559 = add i32 %424, %518
  store i32 0, i32* %30, align 4
  store i32 %559, i32* %30, align 4
  %560 = icmp slt i32 %559, 0
  %561 = icmp ne i1 %560, false
  br i1 %561, label %true_block107, label %false_block108

true_block107:                                    ; preds = %after_if106
  %neg110 = sub i32 0, %559
  store i32 %neg110, i32* %30, align 4
  br label %after_if109

false_block108:                                   ; preds = %after_if106
  br label %after_if109

after_if109:                                      ; preds = %false_block108, %true_block107
  %562 = load i32, i32* %30, align 4
  %563 = icmp sge i32 %562, %537
  %564 = icmp ne i1 %563, false
  br i1 %564, label %true_block111, label %false_block112

true_block111:                                    ; preds = %after_if109
  %565 = shl i32 %165, 1
  %566 = load i32, i32* %30, align 4
  %567 = sub i32 %565, %566
  store i32 %567, i32* %30, align 4
  br label %after_if113

false_block112:                                   ; preds = %after_if109
  br label %after_if113

after_if113:                                      ; preds = %false_block112, %true_block111
  %568 = load i32, i32* %30, align 4
  %569 = call i32 @max_i32(i32 0, i32 %568)
  %570 = call i32 @min_i32(i32 %165, i32 %569)
  %571 = add i32 %160, %520
  store i32 0, i32* %31, align 4
  store i32 %571, i32* %31, align 4
  %572 = icmp slt i32 %571, 0
  %573 = icmp ne i1 %572, false
  br i1 %573, label %true_block114, label %false_block115

true_block114:                                    ; preds = %after_if113
  %neg117 = sub i32 0, %571
  store i32 %neg117, i32* %31, align 4
  br label %after_if116

false_block115:                                   ; preds = %after_if113
  br label %after_if116

after_if116:                                      ; preds = %false_block115, %true_block114
  %574 = load i32, i32* %31, align 4
  %575 = icmp sge i32 %574, %550
  %576 = icmp ne i1 %575, false
  br i1 %576, label %true_block118, label %false_block119

true_block118:                                    ; preds = %after_if116
  %577 = shl i32 %166, 1
  %578 = load i32, i32* %31, align 4
  %579 = sub i32 %577, %578
  store i32 %579, i32* %31, align 4
  br label %after_if120

false_block119:                                   ; preds = %after_if116
  br label %after_if120

after_if120:                                      ; preds = %false_block119, %true_block118
  %580 = load i32, i32* %31, align 4
  %581 = call i32 @max_i32(i32 0, i32 %580)
  %582 = call i32 @min_i32(i32 %166, i32 %581)
  %583 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 1
  %584 = load float*, float** %583, align 8
  %585 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 0
  %586 = load i32, i32* %585, align 4
  %587 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 1
  %588 = load i32, i32* %587, align 4
  %589 = mul i32 0, %586
  %590 = add i32 %589, %545
  %591 = mul i32 %590, %588
  %592 = add i32 %591, %558
  %593 = getelementptr float, float* %584, i32 %592
  %594 = load float, float* %593, align 4
  %595 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 1
  %596 = load float*, float** %595, align 8
  %597 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 0
  %598 = load i32, i32* %597, align 4
  %599 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 1
  %600 = load i32, i32* %599, align 4
  %601 = mul i32 0, %598
  %602 = add i32 %601, %570
  %603 = mul i32 %602, %600
  %604 = add i32 %603, %582
  %605 = getelementptr float, float* %596, i32 %604
  %606 = load float, float* %605, align 4
  %607 = fsub reassoc ninf nsz float %594, %606
  %608 = load float, float* %25, align 4
  %609 = fadd reassoc ninf nsz float %608, %607
  store float %609, float* %25, align 4
  %610 = fmul reassoc ninf nsz float %607, %607
  %611 = load float, float* %26, align 4
  %612 = fadd reassoc ninf nsz float %611, %610
  store float %612, float* %26, align 4
  br label %for_loop_inc90

for_loop_body121:                                 ; preds = %for_loop_test124
  %613 = load i32, i32* %34, align 4
  %614 = sdiv i32 %613, %163
  %615 = icmp slt i32 %613, 0
  %616 = mul i32 %163, %614
  %617 = icmp ne i1 %615, %175
  %618 = icmp ne i32 %613, 0
  %619 = icmp ne i32 %616, %613
  %620 = icmp ne i1 %617, false
  %621 = icmp ne i1 %618, false
  %622 = and i1 %620, %621
  %623 = icmp ne i1 %622, false
  %624 = icmp ne i1 %619, false
  %625 = and i1 %623, %624
  %626 = zext i1 %625 to i32
  %627 = sub i32 %614, %626
  %628 = mul i32 %627, %163
  %629 = sub i32 %613, %628
  %630 = add i32 %76, %627
  store i32 0, i32* %35, align 4
  store i32 %630, i32* %35, align 4
  %631 = icmp slt i32 %630, 0
  %632 = icmp ne i1 %631, false
  br i1 %632, label %true_block125, label %false_block126

for_loop_inc122:                                  ; preds = %after_if152
  %633 = load i32, i32* %34, align 4
  %634 = add i32 %633, 1
  store i32 %634, i32* %34, align 4
  br label %for_loop_test124

after_for123:                                     ; preds = %for_loop_test124
  %635 = load float, float* %32, align 4
  %636 = fdiv reassoc ninf nsz float %635, %199
  %637 = load float, float* %33, align 4
  %638 = fdiv reassoc ninf nsz float %637, %199
  %639 = fmul reassoc ninf nsz float %636, %636
  %640 = fsub reassoc ninf nsz float %638, %639
  %641 = call reassoc ninf nsz float @llvm.maxnum.f32(float 0.000000e+00, float %640)
  store float 0.000000e+00, float* %39, align 4
  %642 = fadd reassoc ninf nsz float %315, %206
  %643 = fadd reassoc ninf nsz float %423, %423
  %644 = fsub reassoc ninf nsz float %642, %643
  %645 = fadd reassoc ninf nsz float %644, %644
  %646 = call reassoc ninf nsz float @__nv_fabsf(float %645)
  %647 = fcmp reassoc ninf nsz ogt float %646, 0x3EB0C6F7A0000000
  %648 = icmp ne i1 %647, false
  br i1 %648, label %true_block153, label %false_block154

for_loop_test124:                                 ; preds = %for_loop_inc122, %after_for91
  %649 = load i32, i32* %34, align 4
  %650 = icmp slt i32 %649, %164
  br i1 %650, label %for_loop_body121, label %after_for123

true_block125:                                    ; preds = %for_loop_body121
  %neg128 = sub i32 0, %630
  store i32 %neg128, i32* %35, align 4
  br label %after_if127

false_block126:                                   ; preds = %for_loop_body121
  br label %after_if127

after_if127:                                      ; preds = %false_block126, %true_block125
  %651 = load i32, i32* %35, align 4
  %652 = load i32, i32* %72, align 4
  %653 = icmp sge i32 %651, %652
  %654 = icmp ne i1 %653, false
  br i1 %654, label %true_block129, label %false_block130

true_block129:                                    ; preds = %after_if127
  %655 = shl i32 %165, 1
  %656 = load i32, i32* %35, align 4
  %657 = sub i32 %655, %656
  store i32 %657, i32* %35, align 4
  br label %after_if131

false_block130:                                   ; preds = %after_if127
  br label %after_if131

after_if131:                                      ; preds = %false_block130, %true_block129
  %658 = load i32, i32* %35, align 4
  %659 = call i32 @max_i32(i32 0, i32 %658)
  %660 = call i32 @min_i32(i32 %165, i32 %659)
  %661 = add i32 %88, %629
  store i32 0, i32* %36, align 4
  store i32 %661, i32* %36, align 4
  %662 = icmp slt i32 %661, 0
  %663 = icmp ne i1 %662, false
  br i1 %663, label %true_block132, label %false_block133

true_block132:                                    ; preds = %after_if131
  %neg135 = sub i32 0, %661
  store i32 %neg135, i32* %36, align 4
  br label %after_if134

false_block133:                                   ; preds = %after_if131
  br label %after_if134

after_if134:                                      ; preds = %false_block133, %true_block132
  %664 = load i32, i32* %36, align 4
  %665 = load i32, i32* %84, align 4
  %666 = icmp sge i32 %664, %665
  %667 = icmp ne i1 %666, false
  br i1 %667, label %true_block136, label %false_block137

true_block136:                                    ; preds = %after_if134
  %668 = shl i32 %166, 1
  %669 = load i32, i32* %36, align 4
  %670 = sub i32 %668, %669
  store i32 %670, i32* %36, align 4
  br label %after_if138

false_block137:                                   ; preds = %after_if134
  br label %after_if138

after_if138:                                      ; preds = %false_block137, %true_block136
  %671 = load i32, i32* %36, align 4
  %672 = call i32 @max_i32(i32 0, i32 %671)
  %673 = call i32 @min_i32(i32 %166, i32 %672)
  %674 = add i32 %533, %627
  store i32 0, i32* %37, align 4
  store i32 %674, i32* %37, align 4
  %675 = icmp slt i32 %674, 0
  %676 = icmp ne i1 %675, false
  br i1 %676, label %true_block139, label %false_block140

true_block139:                                    ; preds = %after_if138
  %neg142 = sub i32 0, %674
  store i32 %neg142, i32* %37, align 4
  br label %after_if141

false_block140:                                   ; preds = %after_if138
  br label %after_if141

after_if141:                                      ; preds = %false_block140, %true_block139
  %677 = load i32, i32* %37, align 4
  %678 = icmp sge i32 %677, %652
  %679 = icmp ne i1 %678, false
  br i1 %679, label %true_block143, label %false_block144

true_block143:                                    ; preds = %after_if141
  %680 = shl i32 %165, 1
  %681 = load i32, i32* %37, align 4
  %682 = sub i32 %680, %681
  store i32 %682, i32* %37, align 4
  br label %after_if145

false_block144:                                   ; preds = %after_if141
  br label %after_if145

after_if145:                                      ; preds = %false_block144, %true_block143
  %683 = load i32, i32* %37, align 4
  %684 = call i32 @max_i32(i32 0, i32 %683)
  %685 = call i32 @min_i32(i32 %165, i32 %684)
  %686 = add i32 %160, %629
  store i32 0, i32* %38, align 4
  store i32 %686, i32* %38, align 4
  %687 = icmp slt i32 %686, 0
  %688 = icmp ne i1 %687, false
  br i1 %688, label %true_block146, label %false_block147

true_block146:                                    ; preds = %after_if145
  %neg149 = sub i32 0, %686
  store i32 %neg149, i32* %38, align 4
  br label %after_if148

false_block147:                                   ; preds = %after_if145
  br label %after_if148

after_if148:                                      ; preds = %false_block147, %true_block146
  %689 = load i32, i32* %38, align 4
  %690 = icmp sge i32 %689, %665
  %691 = icmp ne i1 %690, false
  br i1 %691, label %true_block150, label %false_block151

true_block150:                                    ; preds = %after_if148
  %692 = shl i32 %166, 1
  %693 = load i32, i32* %38, align 4
  %694 = sub i32 %692, %693
  store i32 %694, i32* %38, align 4
  br label %after_if152

false_block151:                                   ; preds = %after_if148
  br label %after_if152

after_if152:                                      ; preds = %false_block151, %true_block150
  %695 = load i32, i32* %38, align 4
  %696 = call i32 @max_i32(i32 0, i32 %695)
  %697 = call i32 @min_i32(i32 %166, i32 %696)
  %698 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 1
  %699 = load float*, float** %698, align 8
  %700 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 0
  %701 = load i32, i32* %700, align 4
  %702 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %170, i32 0, i32 0, i32 1
  %703 = load i32, i32* %702, align 4
  %704 = mul i32 0, %701
  %705 = add i32 %704, %660
  %706 = mul i32 %705, %703
  %707 = add i32 %706, %673
  %708 = getelementptr float, float* %699, i32 %707
  %709 = load float, float* %708, align 4
  %710 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 1
  %711 = load float*, float** %710, align 8
  %712 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 0
  %713 = load i32, i32* %712, align 4
  %714 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %174, i32 0, i32 0, i32 1
  %715 = load i32, i32* %714, align 4
  %716 = mul i32 0, %713
  %717 = add i32 %716, %685
  %718 = mul i32 %717, %715
  %719 = add i32 %718, %697
  %720 = getelementptr float, float* %711, i32 %719
  %721 = load float, float* %720, align 4
  %722 = fsub reassoc ninf nsz float %709, %721
  %723 = load float, float* %32, align 4
  %724 = fadd reassoc ninf nsz float %723, %722
  store float %724, float* %32, align 4
  %725 = fmul reassoc ninf nsz float %722, %722
  %726 = load float, float* %33, align 4
  %727 = fadd reassoc ninf nsz float %726, %725
  store float %727, float* %33, align 4
  br label %for_loop_inc122

true_block153:                                    ; preds = %after_for123
  %728 = fsub reassoc ninf nsz float %315, %206
  %neg156 = fneg reassoc ninf nsz float %728
  %729 = fdiv reassoc ninf nsz float %neg156, %645
  store float %729, float* %39, align 4
  br label %after_if155

false_block154:                                   ; preds = %after_for123
  br label %after_if155

after_if155:                                      ; preds = %false_block154, %true_block153
  %730 = load float, float* %39, align 4
  %731 = call reassoc ninf nsz float @llvm.maxnum.f32(float -5.000000e-01, float %730)
  %732 = call reassoc ninf nsz float @llvm.minnum.f32(float 5.000000e-01, float %731)
  store float 0.000000e+00, float* %40, align 4
  %733 = fadd reassoc ninf nsz float %641, %532
  %734 = fsub reassoc ninf nsz float %733, %643
  %735 = fadd reassoc ninf nsz float %734, %734
  %736 = call reassoc ninf nsz float @__nv_fabsf(float %735)
  %737 = fcmp reassoc ninf nsz ogt float %736, 0x3EB0C6F7A0000000
  %738 = icmp ne i1 %737, false
  br i1 %738, label %true_block157, label %false_block158

true_block157:                                    ; preds = %after_if155
  %739 = fsub reassoc ninf nsz float %641, %532
  %neg160 = fneg reassoc ninf nsz float %739
  %740 = fdiv reassoc ninf nsz float %neg160, %735
  store float %740, float* %40, align 4
  br label %after_if159

false_block158:                                   ; preds = %after_if155
  br label %after_if159

after_if159:                                      ; preds = %false_block158, %true_block157
  %741 = load float, float* %40, align 4
  %742 = call reassoc ninf nsz float @llvm.maxnum.f32(float -5.000000e-01, float %741)
  %743 = call reassoc ninf nsz float @llvm.minnum.f32(float 5.000000e-01, float %742)
  %744 = sitofp i32 %140 to float
  %745 = fadd reassoc ninf nsz float %744, %732
  %746 = sitofp i32 %158 to float
  %747 = fadd reassoc ninf nsz float %746, %743
  store i32 0, i32* %41, align 4
  br label %for_loop_test164

for_loop_body161:                                 ; preds = %for_loop_test164
  %748 = load i32, i32* %41, align 4
  %749 = sdiv i32 %748, %163
  %750 = icmp slt i32 %748, 0
  %751 = mul i32 %163, %749
  %752 = icmp ne i1 %750, %175
  %753 = icmp ne i32 %748, 0
  %754 = icmp ne i32 %751, %748
  %755 = icmp ne i1 %752, false
  %756 = icmp ne i1 %753, false
  %757 = and i1 %755, %756
  %758 = icmp ne i1 %757, false
  %759 = icmp ne i1 %754, false
  %760 = and i1 %758, %759
  %761 = zext i1 %760 to i32
  %762 = sub i32 %749, %761
  %763 = mul i32 %762, %163
  %764 = sub i32 %748, %763
  %765 = add i32 %76, %762
  %766 = load i32, i32* %72, align 4
  %767 = icmp slt i32 %765, %766
  store i1 false, i1* %42, align 1
  store i1 %767, i1* %42, align 1
  %768 = icmp ne i1 %767, false
  br i1 %768, label %true_block165, label %false_block166

for_loop_inc162:                                  ; preds = %after_if170
  %769 = load i32, i32* %41, align 4
  %770 = add i32 %769, 1
  store i32 %770, i32* %41, align 4
  br label %for_loop_test164

after_for163:                                     ; preds = %for_loop_test164
  br label %final

for_loop_test164:                                 ; preds = %for_loop_inc162, %after_if159
  %771 = load i32, i32* %41, align 4
  %772 = icmp slt i32 %771, %164
  br i1 %772, label %for_loop_body161, label %after_for163

true_block165:                                    ; preds = %for_loop_body161
  %773 = add i32 %88, %764
  %774 = load i32, i32* %84, align 4
  %775 = icmp slt i32 %773, %774
  store i1 %775, i1* %42, align 1
  br label %after_if167

false_block166:                                   ; preds = %for_loop_body161
  br label %after_if167

after_if167:                                      ; preds = %false_block166, %true_block165
  %776 = load i1, i1* %42, align 1
  %777 = icmp ne i1 %776, false
  br i1 %777, label %true_block168, label %false_block169

true_block168:                                    ; preds = %after_if167
  %778 = add i32 %88, %764
  %779 = getelementptr %struct.RuntimeContext.85, %struct.RuntimeContext.85* %0, i32 0, i32 0
  %780 = bitcast i8** %779 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }**
  %781 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }** %780, align 8
  %782 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32 }* %781, i32 0, i32 3
  %783 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 1
  %784 = load float*, float** %783, align 8
  %785 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 0, i32 0
  %786 = load i32, i32* %785, align 4
  %787 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 0, i32 1
  %788 = load i32, i32* %787, align 4
  %789 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 0, i32 2
  %790 = load i32, i32* %789, align 4
  %791 = mul i32 0, %786
  %792 = add i32 %791, %765
  %793 = mul i32 %792, %788
  %794 = add i32 %793, %778
  %795 = mul i32 %794, %790
  %796 = add i32 %795, 0
  %797 = getelementptr float, float* %784, i32 %796
  store float %745, float* %797, align 4
  %798 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 1
  %799 = load float*, float** %798, align 8
  %800 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 0, i32 0
  %801 = load i32, i32* %800, align 4
  %802 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 0, i32 1
  %803 = load i32, i32* %802, align 4
  %804 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %782, i32 0, i32 0, i32 2
  %805 = load i32, i32* %804, align 4
  %806 = mul i32 0, %801
  %807 = add i32 %806, %765
  %808 = mul i32 %807, %803
  %809 = add i32 %808, %778
  %810 = mul i32 %809, %805
  %811 = add i32 %810, 1
  %812 = getelementptr float, float* %799, i32 %811
  store float %747, float* %812, align 4
  br label %after_if170

false_block169:                                   ; preds = %after_if167
  br label %after_if170

after_if170:                                      ; preds = %false_block169, %true_block168
  br label %for_loop_inc162
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.round.f32(float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #0

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @min_i32(i32 noundef %0, i32 noundef %1) #1 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 %1, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  %5 = load i32, i32* %4, align 4
  %6 = load i32, i32* %3, align 4
  %7 = icmp slt i32 %5, %6
  br i1 %7, label %8, label %10

8:                                                ; preds = %2
  %9 = load i32, i32* %4, align 4
  br label %12

10:                                               ; preds = %2
  %11 = load i32, i32* %3, align 4
  br label %12

12:                                               ; preds = %10, %8
  %13 = phi i32 [ %9, %8 ], [ %11, %10 ]
  ret i32 %13
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @max_i32(i32 noundef %0, i32 noundef %1) #1 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  store i32 %1, i32* %3, align 4
  store i32 %0, i32* %4, align 4
  %5 = load i32, i32* %4, align 4
  %6 = load i32, i32* %3, align 4
  %7 = icmp sgt i32 %5, %6
  br i1 %7, label %8, label %10

8:                                                ; preds = %2
  %9 = load i32, i32* %4, align 4
  br label %12

10:                                               ; preds = %2
  %11 = load i32, i32* %3, align 4
  br label %12

12:                                               ; preds = %10, %8
  %13 = phi i32 [ %9, %8 ], [ %11, %10 ]
  ret i32 %13
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal %struct.LLVMRuntime.84* @RuntimeContext_get_runtime(%struct.RuntimeContext.85* noundef %0) #1 {
  %2 = alloca %struct.RuntimeContext.85*, align 8
  store %struct.RuntimeContext.85* %0, %struct.RuntimeContext.85** %2, align 8
  %3 = load %struct.RuntimeContext.85*, %struct.RuntimeContext.85** %2, align 8
  %4 = getelementptr inbounds %struct.RuntimeContext.85, %struct.RuntimeContext.85* %3, i32 0, i32 1
  %5 = load %struct.LLVMRuntime.84*, %struct.LLVMRuntime.84** %4, align 8
  ret %struct.LLVMRuntime.84* %5
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i8* @get_temporary_pointer(%struct.LLVMRuntime.84* noundef %0, i64 noundef %1) #1 {
  %3 = alloca i64, align 8
  %4 = alloca %struct.LLVMRuntime.84*, align 8
  store i64 %1, i64* %3, align 8
  store %struct.LLVMRuntime.84* %0, %struct.LLVMRuntime.84** %4, align 8
  %5 = load %struct.LLVMRuntime.84*, %struct.LLVMRuntime.84** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.84, %struct.LLVMRuntime.84* %5, i32 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = load i64, i64* %3, align 8
  %9 = getelementptr inbounds i8, i8* %7, i64 %8
  ret i8* %9
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @gpu_parallel_range_for(%struct.RuntimeContext.85* noundef %0, i32 noundef %1, i32 noundef %2, void (%struct.RuntimeContext.85*, i8*)* noundef %3, void (%struct.RuntimeContext.85*, i8*, i32)* noundef %4, void (%struct.RuntimeContext.85*, i8*)* noundef %5, i64 noundef %6) #1 {
  %8 = alloca i64, align 8
  %9 = alloca void (%struct.RuntimeContext.85*, i8*)*, align 8
  %10 = alloca void (%struct.RuntimeContext.85*, i8*, i32)*, align 8
  %11 = alloca void (%struct.RuntimeContext.85*, i8*)*, align 8
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca %struct.RuntimeContext.85*, align 8
  %15 = alloca i32, align 4
  %16 = alloca i8*, align 8
  %17 = alloca i64, align 8
  %18 = alloca i8*, align 8
  store i64 %6, i64* %8, align 8
  store void (%struct.RuntimeContext.85*, i8*)* %5, void (%struct.RuntimeContext.85*, i8*)** %9, align 8
  store void (%struct.RuntimeContext.85*, i8*, i32)* %4, void (%struct.RuntimeContext.85*, i8*, i32)** %10, align 8
  store void (%struct.RuntimeContext.85*, i8*)* %3, void (%struct.RuntimeContext.85*, i8*)** %11, align 8
  store i32 %2, i32* %12, align 4
  store i32 %1, i32* %13, align 4
  store %struct.RuntimeContext.85* %0, %struct.RuntimeContext.85** %14, align 8
  %19 = call i32 @thread_idx()
  %20 = call i32 @block_dim()
  %21 = call i32 @block_idx()
  %22 = mul nsw i32 %20, %21
  %23 = add nsw i32 %19, %22
  %24 = load i32, i32* %13, align 4
  %25 = add nsw i32 %23, %24
  store i32 %25, i32* %15, align 4
  %26 = load i64, i64* %8, align 8
  %27 = call i8* @llvm.stacksave()
  store i8* %27, i8** %16, align 8
  %28 = alloca i8, i64 %26, align 8
  store i64 %26, i64* %17, align 8
  %29 = getelementptr inbounds i8, i8* %28, i64 0
  store i8* %29, i8** %18, align 8
  %30 = load void (%struct.RuntimeContext.85*, i8*)*, void (%struct.RuntimeContext.85*, i8*)** %11, align 8
  %31 = icmp ne void (%struct.RuntimeContext.85*, i8*)* %30, null
  br i1 %31, label %32, label %36

32:                                               ; preds = %7
  %33 = load void (%struct.RuntimeContext.85*, i8*)*, void (%struct.RuntimeContext.85*, i8*)** %11, align 8
  %34 = load i8*, i8** %18, align 8
  %35 = load %struct.RuntimeContext.85*, %struct.RuntimeContext.85** %14, align 8
  call void %33(%struct.RuntimeContext.85* noundef %35, i8* noundef %34)
  br label %36

36:                                               ; preds = %32, %7
  br label %37

37:                                               ; preds = %41, %36
  %38 = load i32, i32* %15, align 4
  %39 = load i32, i32* %12, align 4
  %40 = icmp slt i32 %38, %39
  br i1 %40, label %41, label %51

41:                                               ; preds = %37
  %42 = load void (%struct.RuntimeContext.85*, i8*, i32)*, void (%struct.RuntimeContext.85*, i8*, i32)** %10, align 8
  %43 = load i32, i32* %15, align 4
  %44 = load i8*, i8** %18, align 8
  %45 = load %struct.RuntimeContext.85*, %struct.RuntimeContext.85** %14, align 8
  call void %42(%struct.RuntimeContext.85* noundef %45, i8* noundef %44, i32 noundef %43)
  %46 = call i32 @block_dim()
  %47 = call i32 @grid_dim()
  %48 = mul nsw i32 %46, %47
  %49 = load i32, i32* %15, align 4
  %50 = add nsw i32 %49, %48
  store i32 %50, i32* %15, align 4
  br label %37, !llvm.loop !20

51:                                               ; preds = %37
  %52 = load void (%struct.RuntimeContext.85*, i8*)*, void (%struct.RuntimeContext.85*, i8*)** %9, align 8
  %53 = icmp ne void (%struct.RuntimeContext.85*, i8*)* %52, null
  br i1 %53, label %54, label %58

54:                                               ; preds = %51
  %55 = load void (%struct.RuntimeContext.85*, i8*)*, void (%struct.RuntimeContext.85*, i8*)** %9, align 8
  %56 = load i8*, i8** %18, align 8
  %57 = load %struct.RuntimeContext.85*, %struct.RuntimeContext.85** %14, align 8
  call void %55(%struct.RuntimeContext.85* noundef %57, i8* noundef %56)
  br label %58

58:                                               ; preds = %54, %51
  %59 = load i8*, i8** %16, align 8
  call void @llvm.stackrestore(i8* %59)
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @thread_idx() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.tid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_dim() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ntid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_idx() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare i8* @llvm.stacksave() #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @grid_dim() #1 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.nctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare void @llvm.stackrestore(i8*) #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.nctaid.x() #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ctaid.x() #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ntid.x() #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.tid.x() #0

; Function Attrs: alwaysinline inlinehint
define internal float @__nv_fabsf(float %f) #3 {
  %call = call i32 @__nvvm_reflect(i8* addrspacecast (i8 addrspace(1)* getelementptr inbounds ([11 x i8], [11 x i8] addrspace(1)* @"$str", i32 0, i32 0) to i8*))
  %1 = icmp ne i32 %call, 0
  br i1 %1, label %2, label %4

2:                                                ; preds = %0
  %3 = call float @llvm.nvvm.fabs.ftz.f(float %f)
  br label %6

4:                                                ; preds = %0
  %5 = call float @llvm.nvvm.fabs.f(float %f)
  br label %6

6:                                                ; preds = %4, %2
  %retval.0 = phi float [ %3, %2 ], [ %5, %4 ]
  ret float %retval.0
}

; Function Attrs: alwaysinline
declare i32 @__nvvm_reflect(i8*) #4

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.fabs.ftz.f(float) #0

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.nvvm.fabs.f(float) #0

attributes #0 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #1 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #2 = { nocallback nofree nosync nounwind willreturn }
attributes #3 = { alwaysinline inlinehint }
attributes #4 = { alwaysinline }

!nvvm.annotations = !{!0, !1, !2, !3, !4, !5, !6, !7, !6, !8, !8, !8, !8, !9, !9, !8}
!llvm.linker.options = !{!10, !11, !12, !13, !14}
!llvm.ident = !{!15}
!nvvmir.version = !{!16}
!llvm.module.flags = !{!17, !18, !19}

!0 = !{void (%struct.RuntimeContext.85*)* @_parabolic_subpixel_refinement_kernel_c218_0_kernel_0_serial, !"kernel", i32 1}
!1 = !{void (%struct.RuntimeContext.85*)* @_parabolic_subpixel_refinement_kernel_c218_0_kernel_0_serial, !"maxntidx", i32 1}
!2 = !{void (%struct.RuntimeContext.85*)* @_parabolic_subpixel_refinement_kernel_c218_0_kernel_0_serial, !"minctasm", i32 2}
!3 = !{void (%struct.RuntimeContext.85*)* @_parabolic_subpixel_refinement_kernel_c218_0_kernel_1_range_for, !"kernel", i32 1}
!4 = !{void (%struct.RuntimeContext.85*)* @_parabolic_subpixel_refinement_kernel_c218_0_kernel_1_range_for, !"maxntidx", i32 128}
!5 = !{void (%struct.RuntimeContext.85*)* @_parabolic_subpixel_refinement_kernel_c218_0_kernel_1_range_for, !"minctasm", i32 2}
!6 = !{null, !"align", i32 8}
!7 = !{null, !"align", i32 8, !"align", i32 65544, !"align", i32 131080}
!8 = !{null, !"align", i32 16}
!9 = !{null, !"align", i32 16, !"align", i32 65552, !"align", i32 131088}
!10 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!11 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!12 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!13 = !{!"/DEFAULTLIB:libcpmt.lib"}
!14 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!15 = !{!"clang version 14.0.6"}
!16 = !{i32 1, i32 4}
!17 = !{i32 1, !"wchar_size", i32 2}
!18 = !{i32 7, !"PIC Level", i32 2}
!19 = !{i32 7, !"uwtable", i32 1}
!20 = distinct !{!20, !21}
!21 = !{!"llvm.loop.mustprogress"}
