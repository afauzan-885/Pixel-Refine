; ModuleID = 'kernel'
source_filename = "kernel"
target triple = "nvptx64-nvidia-cuda"

%struct.RuntimeContext.49 = type { i8*, %struct.LLVMRuntime.48*, i32, i64* }
%struct.LLVMRuntime.48 = type { %struct.PreallocatedMemoryChunk.44, %struct.PreallocatedMemoryChunk.44, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.45*], [1024 x %struct.NodeManager.46*], [1024 x i8*], i8*, %struct.RandState.47*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.44 = type { i8*, i8*, i64 }
%struct.ListManager.45 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.48* }
%struct.NodeManager.46 = type { %struct.LLVMRuntime.48*, i32, i32, i32, i32, %struct.ListManager.45*, %struct.ListManager.45*, %struct.ListManager.45*, i32 }
%struct.RandState.47 = type { i32, i32, i32, i32, i32 }

@"$str" = private addrspace(1) constant [11 x i8] c"__CUDA_FTZ\00"

define void @_upsample_flow_kernel_c154_0_kernel_0_serial(%struct.RuntimeContext.49* byval(%struct.RuntimeContext.49) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %context, i32 0, i32 0
  %1 = bitcast i8** %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %2 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %1, align 8
  %3 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %2, i32 0, i32 4
  %4 = load i32, i32* %3, align 4
  %5 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %context)
  %6 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %5, i64 12)
  %7 = bitcast i8* %6 to i32*
  store i32 %4, i32* %7, align 4
  %8 = call i32 @max_i32(i32 0, i32 %4)
  %9 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %context, i32 0, i32 0
  %10 = bitcast i8** %9 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %10, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %11, i32 0, i32 5
  %13 = load i32, i32* %12, align 4
  %14 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %context)
  %15 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %14, i64 8)
  %16 = bitcast i8* %15 to i32*
  store i32 %13, i32* %16, align 4
  %17 = call i32 @max_i32(i32 0, i32 %13)
  %18 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %context)
  %19 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %18, i64 4)
  %20 = bitcast i8* %19 to i32*
  store i32 %17, i32* %20, align 4
  %21 = mul i32 %8, %17
  %22 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %context)
  %23 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %22, i64 0)
  %24 = bitcast i8* %23 to i32*
  store i32 %21, i32* %24, align 4
  br label %final
}

define void @_upsample_flow_kernel_c154_0_kernel_1_range_for(%struct.RuntimeContext.49* byval(%struct.RuntimeContext.49) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %context)
  %1 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %0, i64 0)
  %2 = bitcast i8* %1 to i32*
  %3 = load i32, i32* %2, align 4
  call void @gpu_parallel_range_for(%struct.RuntimeContext.49* %context, i32 0, i32 %3, void (%struct.RuntimeContext.49*, i8*)* null, void (%struct.RuntimeContext.49*, i8*, i32)* @function_body, void (%struct.RuntimeContext.49*, i8*)* null, i64 1)
  br label %final
}

define internal void @function_body(%struct.RuntimeContext.49* %0, i8* %1, i32 %2) {
allocs:
  %3 = alloca i32, align 4
  %4 = alloca float, align 4
  %5 = alloca i1, align 1
  %6 = alloca i1, align 1
  %7 = alloca i1, align 1
  %8 = alloca float, align 4
  %9 = alloca float, align 4
  %10 = alloca float, align 4
  %11 = alloca float, align 4
  %12 = alloca float, align 4
  %13 = alloca float, align 4
  %14 = alloca float, align 4
  %15 = alloca float, align 4
  %16 = alloca float, align 4
  %17 = alloca i1, align 1
  %18 = alloca i1, align 1
  %19 = alloca i1, align 1
  %20 = alloca float, align 4
  %21 = alloca float, align 4
  %22 = alloca float, align 4
  %23 = alloca float, align 4
  %24 = alloca float, align 4
  %25 = alloca float, align 4
  %26 = alloca float, align 4
  %27 = alloca float, align 4
  br label %entry

final:                                            ; preds = %after_if69
  ret void

entry:                                            ; preds = %allocs
  br label %function_body

function_body:                                    ; preds = %entry
  store i32 %2, i32* %3, align 4
  %28 = load i32, i32* %3, align 4
  %29 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %0)
  %30 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %29, i64 4)
  %31 = bitcast i8* %30 to i32*
  %32 = load i32, i32* %31, align 4
  %33 = sdiv i32 %28, %32
  %34 = icmp slt i32 %28, 0
  %35 = icmp slt i32 %32, 0
  %36 = mul i32 %32, %33
  %37 = icmp ne i1 %34, %35
  %38 = icmp ne i32 %28, 0
  %39 = icmp ne i32 %36, %28
  %40 = icmp ne i1 %37, false
  %41 = icmp ne i1 %38, false
  %42 = and i1 %40, %41
  %43 = icmp ne i1 %42, false
  %44 = icmp ne i1 %39, false
  %45 = and i1 %43, %44
  %46 = zext i1 %45 to i32
  %47 = sub i32 %33, %46
  %48 = mul i32 %47, %32
  %49 = sub i32 %28, %48
  %50 = sitofp i32 %49 to float
  %51 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %52 = bitcast i8** %51 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %53 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %52, align 8
  %54 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %53, i32 0, i32 3
  %55 = load i32, i32* %54, align 4
  %56 = sitofp i32 %55 to float
  %57 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %0)
  %58 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %57, i64 8)
  %59 = bitcast i8* %58 to i32*
  %60 = load i32, i32* %59, align 4
  %61 = sitofp i32 %60 to float
  %62 = fdiv reassoc ninf nsz float %56, %61
  %63 = fmul reassoc ninf nsz float %50, %62
  %64 = sitofp i32 %47 to float
  %65 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %66 = bitcast i8** %65 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %67 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %66, align 8
  %68 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %67, i32 0, i32 2
  %69 = load i32, i32* %68, align 4
  %70 = sitofp i32 %69 to float
  %71 = call %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* %0)
  %72 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.48* %71, i64 12)
  %73 = bitcast i8* %72 to i32*
  %74 = load i32, i32* %73, align 4
  %75 = sitofp i32 %74 to float
  %76 = fdiv reassoc ninf nsz float %70, %75
  %77 = fmul reassoc ninf nsz float %64, %76
  store float 0.000000e+00, float* %4, align 4
  %78 = fcmp reassoc ninf nsz olt float %63, 1.000000e+00
  store i1 false, i1* %5, align 1
  store i1 %78, i1* %5, align 1
  %79 = icmp ne i1 %78, false
  br i1 %79, label %true_block, label %false_block

true_block:                                       ; preds = %function_body
  br label %after_if

false_block:                                      ; preds = %function_body
  %80 = fcmp reassoc ninf nsz olt float %77, 1.000000e+00
  store i1 false, i1* %6, align 1
  store i1 %80, i1* %6, align 1
  %81 = icmp ne i1 %80, false
  br i1 %81, label %true_block1, label %false_block2

after_if:                                         ; preds = %after_if3, %true_block
  %82 = load i1, i1* %5, align 1
  %83 = call reassoc ninf nsz float @llvm.floor.f32(float %63)
  %84 = fptosi float %83 to i32
  %85 = call reassoc ninf nsz float @llvm.floor.f32(float %77)
  %86 = fptosi float %85 to i32
  %87 = icmp ne i1 %82, false
  br i1 %87, label %true_block7, label %false_block8

true_block1:                                      ; preds = %false_block
  br label %after_if3

false_block2:                                     ; preds = %false_block
  %88 = sub i32 %55, 2
  %89 = sitofp i32 %88 to float
  %90 = fcmp reassoc ninf nsz oge float %63, %89
  store i1 false, i1* %7, align 1
  store i1 %90, i1* %7, align 1
  %91 = icmp ne i1 %90, false
  br i1 %91, label %true_block4, label %false_block5

after_if3:                                        ; preds = %after_if6, %true_block1
  %92 = load i1, i1* %6, align 1
  store i1 %92, i1* %5, align 1
  br label %after_if

true_block4:                                      ; preds = %false_block2
  br label %after_if6

false_block5:                                     ; preds = %false_block2
  %93 = sub i32 %69, 2
  %94 = sitofp i32 %93 to float
  %95 = fcmp reassoc ninf nsz oge float %77, %94
  store i1 %95, i1* %7, align 1
  br label %after_if6

after_if6:                                        ; preds = %false_block5, %true_block4
  %96 = load i1, i1* %7, align 1
  store i1 %96, i1* %6, align 1
  br label %after_if3

true_block7:                                      ; preds = %after_if
  %97 = sub i32 %55, 1
  %98 = call i32 @max_i32(i32 0, i32 %84)
  %99 = call i32 @min_i32(i32 %97, i32 %98)
  %100 = sub i32 %69, 1
  %101 = call i32 @max_i32(i32 0, i32 %86)
  %102 = call i32 @min_i32(i32 %100, i32 %101)
  %103 = add i32 %84, 1
  %104 = call i32 @max_i32(i32 0, i32 %103)
  %105 = call i32 @min_i32(i32 %97, i32 %104)
  %106 = add i32 %86, 1
  %107 = call i32 @max_i32(i32 0, i32 %106)
  %108 = call i32 @min_i32(i32 %100, i32 %107)
  %109 = sitofp i32 %84 to float
  %110 = fsub reassoc ninf nsz float %63, %109
  %111 = sitofp i32 %86 to float
  %112 = fsub reassoc ninf nsz float %77, %111
  %113 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %114 = bitcast i8** %113 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %115 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %114, align 8
  %116 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %115, i32 0, i32 0
  %117 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 1
  %118 = load float*, float** %117, align 8
  %119 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 0
  %120 = load i32, i32* %119, align 4
  %121 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 1
  %122 = load i32, i32* %121, align 4
  %123 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 2
  %124 = load i32, i32* %123, align 4
  %125 = mul i32 0, %120
  %126 = add i32 %125, %102
  %127 = mul i32 %126, %122
  %128 = add i32 %127, %99
  %129 = mul i32 %128, %124
  %130 = add i32 %129, 0
  %131 = getelementptr float, float* %118, i32 %130
  %132 = load float, float* %131, align 4
  %133 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 1
  %134 = load float*, float** %133, align 8
  %135 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 0
  %136 = load i32, i32* %135, align 4
  %137 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 1
  %138 = load i32, i32* %137, align 4
  %139 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 2
  %140 = load i32, i32* %139, align 4
  %141 = mul i32 0, %136
  %142 = add i32 %141, %102
  %143 = mul i32 %142, %138
  %144 = add i32 %143, %105
  %145 = mul i32 %144, %140
  %146 = add i32 %145, 0
  %147 = getelementptr float, float* %134, i32 %146
  %148 = load float, float* %147, align 4
  %149 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 1
  %150 = load float*, float** %149, align 8
  %151 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 0
  %152 = load i32, i32* %151, align 4
  %153 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 1
  %154 = load i32, i32* %153, align 4
  %155 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 2
  %156 = load i32, i32* %155, align 4
  %157 = mul i32 0, %152
  %158 = add i32 %157, %108
  %159 = mul i32 %158, %154
  %160 = add i32 %159, %99
  %161 = mul i32 %160, %156
  %162 = add i32 %161, 0
  %163 = getelementptr float, float* %150, i32 %162
  %164 = load float, float* %163, align 4
  %165 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 1
  %166 = load float*, float** %165, align 8
  %167 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 0
  %168 = load i32, i32* %167, align 4
  %169 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 1
  %170 = load i32, i32* %169, align 4
  %171 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %116, i32 0, i32 0, i32 2
  %172 = load i32, i32* %171, align 4
  %173 = mul i32 0, %168
  %174 = add i32 %173, %108
  %175 = mul i32 %174, %170
  %176 = add i32 %175, %105
  %177 = mul i32 %176, %172
  %178 = add i32 %177, 0
  %179 = getelementptr float, float* %166, i32 %178
  %180 = load float, float* %179, align 4
  %181 = fsub reassoc ninf nsz float 1.000000e+00, %110
  %182 = fmul reassoc ninf nsz float %132, %181
  %183 = fmul reassoc ninf nsz float %148, %110
  %184 = fadd reassoc ninf nsz float %182, %183
  %185 = fmul reassoc ninf nsz float %164, %181
  %186 = fmul reassoc ninf nsz float %180, %110
  %187 = fadd reassoc ninf nsz float %185, %186
  %188 = fsub reassoc ninf nsz float 1.000000e+00, %112
  %189 = fmul reassoc ninf nsz float %184, %188
  %190 = fmul reassoc ninf nsz float %187, %112
  %191 = fadd reassoc ninf nsz float %189, %190
  store float %191, float* %4, align 4
  br label %after_if9

false_block8:                                     ; preds = %after_if
  %192 = sitofp i32 %84 to float
  %193 = fsub reassoc ninf nsz float %63, %192
  %194 = sitofp i32 %86 to float
  %195 = fsub reassoc ninf nsz float %77, %194
  %196 = fadd reassoc ninf nsz float %193, 1.000000e+00
  %197 = call reassoc ninf nsz float @__nv_fabsf(float %196)
  store float 0.000000e+00, float* %8, align 4
  %198 = fcmp reassoc ninf nsz ole float %197, 1.000000e+00
  %199 = icmp ne i1 %198, false
  br i1 %199, label %true_block10, label %false_block11

after_if9:                                        ; preds = %after_if54, %true_block7
  %200 = load float, float* %4, align 4
  store float 0.000000e+00, float* %16, align 4
  store i1 false, i1* %17, align 1
  store i1 %78, i1* %17, align 1
  %201 = icmp ne i1 %78, false
  br i1 %201, label %true_block58, label %false_block59

true_block10:                                     ; preds = %false_block8
  %202 = fmul reassoc ninf nsz float %197, 1.500000e+00
  %203 = fmul reassoc ninf nsz float %202, %197
  %204 = fmul reassoc ninf nsz float %203, %197
  %205 = fmul reassoc ninf nsz float %197, 2.500000e+00
  %206 = fmul reassoc ninf nsz float %205, %197
  %207 = fsub reassoc ninf nsz float %204, %206
  %208 = fadd reassoc ninf nsz float %207, 1.000000e+00
  store float %208, float* %8, align 4
  br label %after_if12

false_block11:                                    ; preds = %false_block8
  %209 = fcmp reassoc ninf nsz olt float %197, 2.000000e+00
  %210 = icmp ne i1 %209, false
  br i1 %210, label %true_block13, label %false_block14

after_if12:                                       ; preds = %after_if15, %true_block10
  %211 = call reassoc ninf nsz float @__nv_fabsf(float %193)
  store float 0.000000e+00, float* %9, align 4
  %212 = fcmp reassoc ninf nsz ole float %211, 1.000000e+00
  %213 = icmp ne i1 %212, false
  br i1 %213, label %true_block16, label %false_block17

true_block13:                                     ; preds = %false_block11
  %214 = fmul reassoc ninf nsz float %197, -5.000000e-01
  %215 = fmul reassoc ninf nsz float %214, %197
  %216 = fmul reassoc ninf nsz float %215, %197
  %217 = fmul reassoc ninf nsz float %197, 2.500000e+00
  %218 = fmul reassoc ninf nsz float %217, %197
  %219 = fadd reassoc ninf nsz float %216, %218
  %220 = fmul reassoc ninf nsz float %197, 4.000000e+00
  %221 = fsub reassoc ninf nsz float %219, %220
  %222 = fadd reassoc ninf nsz float %221, 2.000000e+00
  store float %222, float* %8, align 4
  br label %after_if15

false_block14:                                    ; preds = %false_block11
  br label %after_if15

after_if15:                                       ; preds = %false_block14, %true_block13
  br label %after_if12

true_block16:                                     ; preds = %after_if12
  %223 = fmul reassoc ninf nsz float %211, 1.500000e+00
  %224 = fmul reassoc ninf nsz float %223, %211
  %225 = fmul reassoc ninf nsz float %224, %211
  %226 = fmul reassoc ninf nsz float %211, 2.500000e+00
  %227 = fmul reassoc ninf nsz float %226, %211
  %228 = fsub reassoc ninf nsz float %225, %227
  %229 = fadd reassoc ninf nsz float %228, 1.000000e+00
  store float %229, float* %9, align 4
  br label %after_if18

false_block17:                                    ; preds = %after_if12
  %230 = fcmp reassoc ninf nsz olt float %211, 2.000000e+00
  %231 = icmp ne i1 %230, false
  br i1 %231, label %true_block19, label %false_block20

after_if18:                                       ; preds = %after_if21, %true_block16
  %232 = fsub reassoc ninf nsz float 1.000000e+00, %193
  %233 = call reassoc ninf nsz float @__nv_fabsf(float %232)
  store float 0.000000e+00, float* %10, align 4
  %234 = fcmp reassoc ninf nsz ole float %233, 1.000000e+00
  %235 = icmp ne i1 %234, false
  br i1 %235, label %true_block22, label %false_block23

true_block19:                                     ; preds = %false_block17
  %236 = fmul reassoc ninf nsz float %211, -5.000000e-01
  %237 = fmul reassoc ninf nsz float %236, %211
  %238 = fmul reassoc ninf nsz float %237, %211
  %239 = fmul reassoc ninf nsz float %211, 2.500000e+00
  %240 = fmul reassoc ninf nsz float %239, %211
  %241 = fadd reassoc ninf nsz float %238, %240
  %242 = fmul reassoc ninf nsz float %211, 4.000000e+00
  %243 = fsub reassoc ninf nsz float %241, %242
  %244 = fadd reassoc ninf nsz float %243, 2.000000e+00
  store float %244, float* %9, align 4
  br label %after_if21

false_block20:                                    ; preds = %false_block17
  br label %after_if21

after_if21:                                       ; preds = %false_block20, %true_block19
  br label %after_if18

true_block22:                                     ; preds = %after_if18
  %245 = fmul reassoc ninf nsz float %233, 1.500000e+00
  %246 = fmul reassoc ninf nsz float %245, %233
  %247 = fmul reassoc ninf nsz float %246, %233
  %248 = fmul reassoc ninf nsz float %233, 2.500000e+00
  %249 = fmul reassoc ninf nsz float %248, %233
  %250 = fsub reassoc ninf nsz float %247, %249
  %251 = fadd reassoc ninf nsz float %250, 1.000000e+00
  store float %251, float* %10, align 4
  br label %after_if24

false_block23:                                    ; preds = %after_if18
  %252 = fcmp reassoc ninf nsz olt float %233, 2.000000e+00
  %253 = icmp ne i1 %252, false
  br i1 %253, label %true_block25, label %false_block26

after_if24:                                       ; preds = %after_if27, %true_block22
  %254 = fsub reassoc ninf nsz float 2.000000e+00, %193
  %255 = call reassoc ninf nsz float @__nv_fabsf(float %254)
  store float 0.000000e+00, float* %11, align 4
  %256 = fcmp reassoc ninf nsz ole float %255, 1.000000e+00
  %257 = icmp ne i1 %256, false
  br i1 %257, label %true_block28, label %false_block29

true_block25:                                     ; preds = %false_block23
  %258 = fmul reassoc ninf nsz float %233, -5.000000e-01
  %259 = fmul reassoc ninf nsz float %258, %233
  %260 = fmul reassoc ninf nsz float %259, %233
  %261 = fmul reassoc ninf nsz float %233, 2.500000e+00
  %262 = fmul reassoc ninf nsz float %261, %233
  %263 = fadd reassoc ninf nsz float %260, %262
  %264 = fmul reassoc ninf nsz float %233, 4.000000e+00
  %265 = fsub reassoc ninf nsz float %263, %264
  %266 = fadd reassoc ninf nsz float %265, 2.000000e+00
  store float %266, float* %10, align 4
  br label %after_if27

false_block26:                                    ; preds = %false_block23
  br label %after_if27

after_if27:                                       ; preds = %false_block26, %true_block25
  br label %after_if24

true_block28:                                     ; preds = %after_if24
  %267 = fmul reassoc ninf nsz float %255, 1.500000e+00
  %268 = fmul reassoc ninf nsz float %267, %255
  %269 = fmul reassoc ninf nsz float %268, %255
  %270 = fmul reassoc ninf nsz float %255, 2.500000e+00
  %271 = fmul reassoc ninf nsz float %270, %255
  %272 = fsub reassoc ninf nsz float %269, %271
  %273 = fadd reassoc ninf nsz float %272, 1.000000e+00
  store float %273, float* %11, align 4
  br label %after_if30

false_block29:                                    ; preds = %after_if24
  %274 = fcmp reassoc ninf nsz olt float %255, 2.000000e+00
  %275 = icmp ne i1 %274, false
  br i1 %275, label %true_block31, label %false_block32

after_if30:                                       ; preds = %after_if33, %true_block28
  %276 = load float, float* %8, align 4
  %277 = load float, float* %9, align 4
  %278 = load float, float* %10, align 4
  %279 = load float, float* %11, align 4
  %280 = fadd reassoc ninf nsz float %195, 1.000000e+00
  %281 = call reassoc ninf nsz float @__nv_fabsf(float %280)
  store float 0.000000e+00, float* %12, align 4
  %282 = fcmp reassoc ninf nsz ole float %281, 1.000000e+00
  %283 = icmp ne i1 %282, false
  br i1 %283, label %true_block34, label %false_block35

true_block31:                                     ; preds = %false_block29
  %284 = fmul reassoc ninf nsz float %255, -5.000000e-01
  %285 = fmul reassoc ninf nsz float %284, %255
  %286 = fmul reassoc ninf nsz float %285, %255
  %287 = fmul reassoc ninf nsz float %255, 2.500000e+00
  %288 = fmul reassoc ninf nsz float %287, %255
  %289 = fadd reassoc ninf nsz float %286, %288
  %290 = fmul reassoc ninf nsz float %255, 4.000000e+00
  %291 = fsub reassoc ninf nsz float %289, %290
  %292 = fadd reassoc ninf nsz float %291, 2.000000e+00
  store float %292, float* %11, align 4
  br label %after_if33

false_block32:                                    ; preds = %false_block29
  br label %after_if33

after_if33:                                       ; preds = %false_block32, %true_block31
  br label %after_if30

true_block34:                                     ; preds = %after_if30
  %293 = fmul reassoc ninf nsz float %281, 1.500000e+00
  %294 = fmul reassoc ninf nsz float %293, %281
  %295 = fmul reassoc ninf nsz float %294, %281
  %296 = fmul reassoc ninf nsz float %281, 2.500000e+00
  %297 = fmul reassoc ninf nsz float %296, %281
  %298 = fsub reassoc ninf nsz float %295, %297
  %299 = fadd reassoc ninf nsz float %298, 1.000000e+00
  store float %299, float* %12, align 4
  br label %after_if36

false_block35:                                    ; preds = %after_if30
  %300 = fcmp reassoc ninf nsz olt float %281, 2.000000e+00
  %301 = icmp ne i1 %300, false
  br i1 %301, label %true_block37, label %false_block38

after_if36:                                       ; preds = %after_if39, %true_block34
  %302 = call reassoc ninf nsz float @__nv_fabsf(float %195)
  store float 0.000000e+00, float* %13, align 4
  %303 = fcmp reassoc ninf nsz ole float %302, 1.000000e+00
  %304 = icmp ne i1 %303, false
  br i1 %304, label %true_block40, label %false_block41

true_block37:                                     ; preds = %false_block35
  %305 = fmul reassoc ninf nsz float %281, -5.000000e-01
  %306 = fmul reassoc ninf nsz float %305, %281
  %307 = fmul reassoc ninf nsz float %306, %281
  %308 = fmul reassoc ninf nsz float %281, 2.500000e+00
  %309 = fmul reassoc ninf nsz float %308, %281
  %310 = fadd reassoc ninf nsz float %307, %309
  %311 = fmul reassoc ninf nsz float %281, 4.000000e+00
  %312 = fsub reassoc ninf nsz float %310, %311
  %313 = fadd reassoc ninf nsz float %312, 2.000000e+00
  store float %313, float* %12, align 4
  br label %after_if39

false_block38:                                    ; preds = %false_block35
  br label %after_if39

after_if39:                                       ; preds = %false_block38, %true_block37
  br label %after_if36

true_block40:                                     ; preds = %after_if36
  %314 = fmul reassoc ninf nsz float %302, 1.500000e+00
  %315 = fmul reassoc ninf nsz float %314, %302
  %316 = fmul reassoc ninf nsz float %315, %302
  %317 = fmul reassoc ninf nsz float %302, 2.500000e+00
  %318 = fmul reassoc ninf nsz float %317, %302
  %319 = fsub reassoc ninf nsz float %316, %318
  %320 = fadd reassoc ninf nsz float %319, 1.000000e+00
  store float %320, float* %13, align 4
  br label %after_if42

false_block41:                                    ; preds = %after_if36
  %321 = fcmp reassoc ninf nsz olt float %302, 2.000000e+00
  %322 = icmp ne i1 %321, false
  br i1 %322, label %true_block43, label %false_block44

after_if42:                                       ; preds = %after_if45, %true_block40
  %323 = fsub reassoc ninf nsz float 1.000000e+00, %195
  %324 = call reassoc ninf nsz float @__nv_fabsf(float %323)
  store float 0.000000e+00, float* %14, align 4
  %325 = fcmp reassoc ninf nsz ole float %324, 1.000000e+00
  %326 = icmp ne i1 %325, false
  br i1 %326, label %true_block46, label %false_block47

true_block43:                                     ; preds = %false_block41
  %327 = fmul reassoc ninf nsz float %302, -5.000000e-01
  %328 = fmul reassoc ninf nsz float %327, %302
  %329 = fmul reassoc ninf nsz float %328, %302
  %330 = fmul reassoc ninf nsz float %302, 2.500000e+00
  %331 = fmul reassoc ninf nsz float %330, %302
  %332 = fadd reassoc ninf nsz float %329, %331
  %333 = fmul reassoc ninf nsz float %302, 4.000000e+00
  %334 = fsub reassoc ninf nsz float %332, %333
  %335 = fadd reassoc ninf nsz float %334, 2.000000e+00
  store float %335, float* %13, align 4
  br label %after_if45

false_block44:                                    ; preds = %false_block41
  br label %after_if45

after_if45:                                       ; preds = %false_block44, %true_block43
  br label %after_if42

true_block46:                                     ; preds = %after_if42
  %336 = fmul reassoc ninf nsz float %324, 1.500000e+00
  %337 = fmul reassoc ninf nsz float %336, %324
  %338 = fmul reassoc ninf nsz float %337, %324
  %339 = fmul reassoc ninf nsz float %324, 2.500000e+00
  %340 = fmul reassoc ninf nsz float %339, %324
  %341 = fsub reassoc ninf nsz float %338, %340
  %342 = fadd reassoc ninf nsz float %341, 1.000000e+00
  store float %342, float* %14, align 4
  br label %after_if48

false_block47:                                    ; preds = %after_if42
  %343 = fcmp reassoc ninf nsz olt float %324, 2.000000e+00
  %344 = icmp ne i1 %343, false
  br i1 %344, label %true_block49, label %false_block50

after_if48:                                       ; preds = %after_if51, %true_block46
  %345 = fsub reassoc ninf nsz float 2.000000e+00, %195
  %346 = call reassoc ninf nsz float @__nv_fabsf(float %345)
  store float 0.000000e+00, float* %15, align 4
  %347 = fcmp reassoc ninf nsz ole float %346, 1.000000e+00
  %348 = icmp ne i1 %347, false
  br i1 %348, label %true_block52, label %false_block53

true_block49:                                     ; preds = %false_block47
  %349 = fmul reassoc ninf nsz float %324, -5.000000e-01
  %350 = fmul reassoc ninf nsz float %349, %324
  %351 = fmul reassoc ninf nsz float %350, %324
  %352 = fmul reassoc ninf nsz float %324, 2.500000e+00
  %353 = fmul reassoc ninf nsz float %352, %324
  %354 = fadd reassoc ninf nsz float %351, %353
  %355 = fmul reassoc ninf nsz float %324, 4.000000e+00
  %356 = fsub reassoc ninf nsz float %354, %355
  %357 = fadd reassoc ninf nsz float %356, 2.000000e+00
  store float %357, float* %14, align 4
  br label %after_if51

false_block50:                                    ; preds = %false_block47
  br label %after_if51

after_if51:                                       ; preds = %false_block50, %true_block49
  br label %after_if48

true_block52:                                     ; preds = %after_if48
  %358 = fmul reassoc ninf nsz float %346, 1.500000e+00
  %359 = fmul reassoc ninf nsz float %358, %346
  %360 = fmul reassoc ninf nsz float %359, %346
  %361 = fmul reassoc ninf nsz float %346, 2.500000e+00
  %362 = fmul reassoc ninf nsz float %361, %346
  %363 = fsub reassoc ninf nsz float %360, %362
  %364 = fadd reassoc ninf nsz float %363, 1.000000e+00
  store float %364, float* %15, align 4
  br label %after_if54

false_block53:                                    ; preds = %after_if48
  %365 = fcmp reassoc ninf nsz olt float %346, 2.000000e+00
  %366 = icmp ne i1 %365, false
  br i1 %366, label %true_block55, label %false_block56

after_if54:                                       ; preds = %after_if57, %true_block52
  %367 = load float, float* %12, align 4
  %368 = load float, float* %13, align 4
  %369 = load float, float* %14, align 4
  %370 = load float, float* %15, align 4
  %371 = sub i32 %86, 1
  %372 = sub i32 %84, 1
  %373 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %374 = bitcast i8** %373 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %375 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %374, align 8
  %376 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %375, i32 0, i32 0
  %377 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %378 = load float*, float** %377, align 8
  %379 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %380 = load i32, i32* %379, align 4
  %381 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %382 = load i32, i32* %381, align 4
  %383 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %384 = load i32, i32* %383, align 4
  %385 = mul i32 0, %380
  %386 = add i32 %385, %371
  %387 = mul i32 %386, %382
  %388 = add i32 %387, %372
  %389 = mul i32 %388, %384
  %390 = add i32 %389, 0
  %391 = getelementptr float, float* %378, i32 %390
  %392 = load float, float* %391, align 4
  %393 = fmul reassoc ninf nsz float %392, %276
  %394 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %395 = load float*, float** %394, align 8
  %396 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %397 = load i32, i32* %396, align 4
  %398 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %399 = load i32, i32* %398, align 4
  %400 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %401 = load i32, i32* %400, align 4
  %402 = mul i32 0, %397
  %403 = add i32 %402, %371
  %404 = mul i32 %403, %399
  %405 = add i32 %404, %84
  %406 = mul i32 %405, %401
  %407 = add i32 %406, 0
  %408 = getelementptr float, float* %395, i32 %407
  %409 = load float, float* %408, align 4
  %410 = fmul reassoc ninf nsz float %409, %277
  %411 = fadd reassoc ninf nsz float %393, %410
  %412 = sub i32 %84, -1
  %413 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %414 = load float*, float** %413, align 8
  %415 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %416 = load i32, i32* %415, align 4
  %417 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %418 = load i32, i32* %417, align 4
  %419 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %420 = load i32, i32* %419, align 4
  %421 = mul i32 0, %416
  %422 = add i32 %421, %371
  %423 = mul i32 %422, %418
  %424 = add i32 %423, %412
  %425 = mul i32 %424, %420
  %426 = add i32 %425, 0
  %427 = getelementptr float, float* %414, i32 %426
  %428 = load float, float* %427, align 4
  %429 = fmul reassoc ninf nsz float %428, %278
  %430 = fadd reassoc ninf nsz float %411, %429
  %431 = sub i32 %84, -2
  %432 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %433 = load float*, float** %432, align 8
  %434 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %435 = load i32, i32* %434, align 4
  %436 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %437 = load i32, i32* %436, align 4
  %438 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %439 = load i32, i32* %438, align 4
  %440 = mul i32 0, %435
  %441 = add i32 %440, %371
  %442 = mul i32 %441, %437
  %443 = add i32 %442, %431
  %444 = mul i32 %443, %439
  %445 = add i32 %444, 0
  %446 = getelementptr float, float* %433, i32 %445
  %447 = load float, float* %446, align 4
  %448 = fmul reassoc ninf nsz float %447, %279
  %449 = fadd reassoc ninf nsz float %430, %448
  %450 = fmul reassoc ninf nsz float %449, %367
  %451 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %452 = load float*, float** %451, align 8
  %453 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %454 = load i32, i32* %453, align 4
  %455 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %456 = load i32, i32* %455, align 4
  %457 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %458 = load i32, i32* %457, align 4
  %459 = mul i32 0, %454
  %460 = add i32 %459, %86
  %461 = mul i32 %460, %456
  %462 = add i32 %461, %372
  %463 = mul i32 %462, %458
  %464 = add i32 %463, 0
  %465 = getelementptr float, float* %452, i32 %464
  %466 = load float, float* %465, align 4
  %467 = fmul reassoc ninf nsz float %466, %276
  %468 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %469 = load float*, float** %468, align 8
  %470 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %471 = load i32, i32* %470, align 4
  %472 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %473 = load i32, i32* %472, align 4
  %474 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %475 = load i32, i32* %474, align 4
  %476 = mul i32 0, %471
  %477 = add i32 %476, %86
  %478 = mul i32 %477, %473
  %479 = add i32 %478, %84
  %480 = mul i32 %479, %475
  %481 = add i32 %480, 0
  %482 = getelementptr float, float* %469, i32 %481
  %483 = load float, float* %482, align 4
  %484 = fmul reassoc ninf nsz float %483, %277
  %485 = fadd reassoc ninf nsz float %467, %484
  %486 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %487 = load float*, float** %486, align 8
  %488 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %489 = load i32, i32* %488, align 4
  %490 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %491 = load i32, i32* %490, align 4
  %492 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %493 = load i32, i32* %492, align 4
  %494 = mul i32 0, %489
  %495 = add i32 %494, %86
  %496 = mul i32 %495, %491
  %497 = add i32 %496, %412
  %498 = mul i32 %497, %493
  %499 = add i32 %498, 0
  %500 = getelementptr float, float* %487, i32 %499
  %501 = load float, float* %500, align 4
  %502 = fmul reassoc ninf nsz float %501, %278
  %503 = fadd reassoc ninf nsz float %485, %502
  %504 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %505 = load float*, float** %504, align 8
  %506 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %507 = load i32, i32* %506, align 4
  %508 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %509 = load i32, i32* %508, align 4
  %510 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %511 = load i32, i32* %510, align 4
  %512 = mul i32 0, %507
  %513 = add i32 %512, %86
  %514 = mul i32 %513, %509
  %515 = add i32 %514, %431
  %516 = mul i32 %515, %511
  %517 = add i32 %516, 0
  %518 = getelementptr float, float* %505, i32 %517
  %519 = load float, float* %518, align 4
  %520 = fmul reassoc ninf nsz float %519, %279
  %521 = fadd reassoc ninf nsz float %503, %520
  %522 = fmul reassoc ninf nsz float %521, %368
  %523 = fadd reassoc ninf nsz float %450, %522
  %524 = sub i32 %86, -1
  %525 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %526 = load float*, float** %525, align 8
  %527 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %528 = load i32, i32* %527, align 4
  %529 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %530 = load i32, i32* %529, align 4
  %531 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %532 = load i32, i32* %531, align 4
  %533 = mul i32 0, %528
  %534 = add i32 %533, %524
  %535 = mul i32 %534, %530
  %536 = add i32 %535, %372
  %537 = mul i32 %536, %532
  %538 = add i32 %537, 0
  %539 = getelementptr float, float* %526, i32 %538
  %540 = load float, float* %539, align 4
  %541 = fmul reassoc ninf nsz float %540, %276
  %542 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %543 = load float*, float** %542, align 8
  %544 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %545 = load i32, i32* %544, align 4
  %546 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %547 = load i32, i32* %546, align 4
  %548 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %549 = load i32, i32* %548, align 4
  %550 = mul i32 0, %545
  %551 = add i32 %550, %524
  %552 = mul i32 %551, %547
  %553 = add i32 %552, %84
  %554 = mul i32 %553, %549
  %555 = add i32 %554, 0
  %556 = getelementptr float, float* %543, i32 %555
  %557 = load float, float* %556, align 4
  %558 = fmul reassoc ninf nsz float %557, %277
  %559 = fadd reassoc ninf nsz float %541, %558
  %560 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %561 = load float*, float** %560, align 8
  %562 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %563 = load i32, i32* %562, align 4
  %564 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %565 = load i32, i32* %564, align 4
  %566 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %567 = load i32, i32* %566, align 4
  %568 = mul i32 0, %563
  %569 = add i32 %568, %524
  %570 = mul i32 %569, %565
  %571 = add i32 %570, %412
  %572 = mul i32 %571, %567
  %573 = add i32 %572, 0
  %574 = getelementptr float, float* %561, i32 %573
  %575 = load float, float* %574, align 4
  %576 = fmul reassoc ninf nsz float %575, %278
  %577 = fadd reassoc ninf nsz float %559, %576
  %578 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %579 = load float*, float** %578, align 8
  %580 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %581 = load i32, i32* %580, align 4
  %582 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %583 = load i32, i32* %582, align 4
  %584 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %585 = load i32, i32* %584, align 4
  %586 = mul i32 0, %581
  %587 = add i32 %586, %524
  %588 = mul i32 %587, %583
  %589 = add i32 %588, %431
  %590 = mul i32 %589, %585
  %591 = add i32 %590, 0
  %592 = getelementptr float, float* %579, i32 %591
  %593 = load float, float* %592, align 4
  %594 = fmul reassoc ninf nsz float %593, %279
  %595 = fadd reassoc ninf nsz float %577, %594
  %596 = fmul reassoc ninf nsz float %595, %369
  %597 = fadd reassoc ninf nsz float %523, %596
  %598 = sub i32 %86, -2
  %599 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %600 = load float*, float** %599, align 8
  %601 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %602 = load i32, i32* %601, align 4
  %603 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %604 = load i32, i32* %603, align 4
  %605 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %606 = load i32, i32* %605, align 4
  %607 = mul i32 0, %602
  %608 = add i32 %607, %598
  %609 = mul i32 %608, %604
  %610 = add i32 %609, %372
  %611 = mul i32 %610, %606
  %612 = add i32 %611, 0
  %613 = getelementptr float, float* %600, i32 %612
  %614 = load float, float* %613, align 4
  %615 = fmul reassoc ninf nsz float %614, %276
  %616 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %617 = load float*, float** %616, align 8
  %618 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %619 = load i32, i32* %618, align 4
  %620 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %621 = load i32, i32* %620, align 4
  %622 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %623 = load i32, i32* %622, align 4
  %624 = mul i32 0, %619
  %625 = add i32 %624, %598
  %626 = mul i32 %625, %621
  %627 = add i32 %626, %84
  %628 = mul i32 %627, %623
  %629 = add i32 %628, 0
  %630 = getelementptr float, float* %617, i32 %629
  %631 = load float, float* %630, align 4
  %632 = fmul reassoc ninf nsz float %631, %277
  %633 = fadd reassoc ninf nsz float %615, %632
  %634 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %635 = load float*, float** %634, align 8
  %636 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %637 = load i32, i32* %636, align 4
  %638 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %639 = load i32, i32* %638, align 4
  %640 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %641 = load i32, i32* %640, align 4
  %642 = mul i32 0, %637
  %643 = add i32 %642, %598
  %644 = mul i32 %643, %639
  %645 = add i32 %644, %412
  %646 = mul i32 %645, %641
  %647 = add i32 %646, 0
  %648 = getelementptr float, float* %635, i32 %647
  %649 = load float, float* %648, align 4
  %650 = fmul reassoc ninf nsz float %649, %278
  %651 = fadd reassoc ninf nsz float %633, %650
  %652 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 1
  %653 = load float*, float** %652, align 8
  %654 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 0
  %655 = load i32, i32* %654, align 4
  %656 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 1
  %657 = load i32, i32* %656, align 4
  %658 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %376, i32 0, i32 0, i32 2
  %659 = load i32, i32* %658, align 4
  %660 = mul i32 0, %655
  %661 = add i32 %660, %598
  %662 = mul i32 %661, %657
  %663 = add i32 %662, %431
  %664 = mul i32 %663, %659
  %665 = add i32 %664, 0
  %666 = getelementptr float, float* %653, i32 %665
  %667 = load float, float* %666, align 4
  %668 = fmul reassoc ninf nsz float %667, %279
  %669 = fadd reassoc ninf nsz float %651, %668
  %670 = fmul reassoc ninf nsz float %669, %370
  %671 = fadd reassoc ninf nsz float %597, %670
  store float %671, float* %4, align 4
  br label %after_if9

true_block55:                                     ; preds = %false_block53
  %672 = fmul reassoc ninf nsz float %346, -5.000000e-01
  %673 = fmul reassoc ninf nsz float %672, %346
  %674 = fmul reassoc ninf nsz float %673, %346
  %675 = fmul reassoc ninf nsz float %346, 2.500000e+00
  %676 = fmul reassoc ninf nsz float %675, %346
  %677 = fadd reassoc ninf nsz float %674, %676
  %678 = fmul reassoc ninf nsz float %346, 4.000000e+00
  %679 = fsub reassoc ninf nsz float %677, %678
  %680 = fadd reassoc ninf nsz float %679, 2.000000e+00
  store float %680, float* %15, align 4
  br label %after_if57

false_block56:                                    ; preds = %false_block53
  br label %after_if57

after_if57:                                       ; preds = %false_block56, %true_block55
  br label %after_if54

true_block58:                                     ; preds = %after_if9
  br label %after_if60

false_block59:                                    ; preds = %after_if9
  %681 = fcmp reassoc ninf nsz olt float %77, 1.000000e+00
  store i1 false, i1* %18, align 1
  store i1 %681, i1* %18, align 1
  %682 = icmp ne i1 %681, false
  br i1 %682, label %true_block61, label %false_block62

after_if60:                                       ; preds = %after_if63, %true_block58
  %683 = load i1, i1* %17, align 1
  %684 = icmp ne i1 %683, false
  br i1 %684, label %true_block67, label %false_block68

true_block61:                                     ; preds = %false_block59
  br label %after_if63

false_block62:                                    ; preds = %false_block59
  %685 = sub i32 %55, 2
  %686 = sitofp i32 %685 to float
  %687 = fcmp reassoc ninf nsz oge float %63, %686
  store i1 false, i1* %19, align 1
  store i1 %687, i1* %19, align 1
  %688 = icmp ne i1 %687, false
  br i1 %688, label %true_block64, label %false_block65

after_if63:                                       ; preds = %after_if66, %true_block61
  %689 = load i1, i1* %18, align 1
  store i1 %689, i1* %17, align 1
  br label %after_if60

true_block64:                                     ; preds = %false_block62
  br label %after_if66

false_block65:                                    ; preds = %false_block62
  %690 = sub i32 %69, 2
  %691 = sitofp i32 %690 to float
  %692 = fcmp reassoc ninf nsz oge float %77, %691
  store i1 %692, i1* %19, align 1
  br label %after_if66

after_if66:                                       ; preds = %false_block65, %true_block64
  %693 = load i1, i1* %19, align 1
  store i1 %693, i1* %18, align 1
  br label %after_if63

true_block67:                                     ; preds = %after_if60
  %694 = sub i32 %55, 1
  %695 = call i32 @max_i32(i32 0, i32 %84)
  %696 = call i32 @min_i32(i32 %694, i32 %695)
  %697 = sub i32 %69, 1
  %698 = call i32 @max_i32(i32 0, i32 %86)
  %699 = call i32 @min_i32(i32 %697, i32 %698)
  %700 = add i32 %84, 1
  %701 = call i32 @max_i32(i32 0, i32 %700)
  %702 = call i32 @min_i32(i32 %694, i32 %701)
  %703 = add i32 %86, 1
  %704 = call i32 @max_i32(i32 0, i32 %703)
  %705 = call i32 @min_i32(i32 %697, i32 %704)
  %706 = sitofp i32 %84 to float
  %707 = fsub reassoc ninf nsz float %63, %706
  %708 = sitofp i32 %86 to float
  %709 = fsub reassoc ninf nsz float %77, %708
  %710 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %711 = bitcast i8** %710 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %712 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %711, align 8
  %713 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %712, i32 0, i32 0
  %714 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 1
  %715 = load float*, float** %714, align 8
  %716 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 0
  %717 = load i32, i32* %716, align 4
  %718 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 1
  %719 = load i32, i32* %718, align 4
  %720 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 2
  %721 = load i32, i32* %720, align 4
  %722 = mul i32 0, %717
  %723 = add i32 %722, %699
  %724 = mul i32 %723, %719
  %725 = add i32 %724, %696
  %726 = mul i32 %725, %721
  %727 = add i32 %726, 1
  %728 = getelementptr float, float* %715, i32 %727
  %729 = load float, float* %728, align 4
  %730 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 1
  %731 = load float*, float** %730, align 8
  %732 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 0
  %733 = load i32, i32* %732, align 4
  %734 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 1
  %735 = load i32, i32* %734, align 4
  %736 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 2
  %737 = load i32, i32* %736, align 4
  %738 = mul i32 0, %733
  %739 = add i32 %738, %699
  %740 = mul i32 %739, %735
  %741 = add i32 %740, %702
  %742 = mul i32 %741, %737
  %743 = add i32 %742, 1
  %744 = getelementptr float, float* %731, i32 %743
  %745 = load float, float* %744, align 4
  %746 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 1
  %747 = load float*, float** %746, align 8
  %748 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 0
  %749 = load i32, i32* %748, align 4
  %750 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 1
  %751 = load i32, i32* %750, align 4
  %752 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 2
  %753 = load i32, i32* %752, align 4
  %754 = mul i32 0, %749
  %755 = add i32 %754, %705
  %756 = mul i32 %755, %751
  %757 = add i32 %756, %696
  %758 = mul i32 %757, %753
  %759 = add i32 %758, 1
  %760 = getelementptr float, float* %747, i32 %759
  %761 = load float, float* %760, align 4
  %762 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 1
  %763 = load float*, float** %762, align 8
  %764 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 0
  %765 = load i32, i32* %764, align 4
  %766 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 1
  %767 = load i32, i32* %766, align 4
  %768 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %713, i32 0, i32 0, i32 2
  %769 = load i32, i32* %768, align 4
  %770 = mul i32 0, %765
  %771 = add i32 %770, %705
  %772 = mul i32 %771, %767
  %773 = add i32 %772, %702
  %774 = mul i32 %773, %769
  %775 = add i32 %774, 1
  %776 = getelementptr float, float* %763, i32 %775
  %777 = load float, float* %776, align 4
  %778 = fsub reassoc ninf nsz float 1.000000e+00, %707
  %779 = fmul reassoc ninf nsz float %729, %778
  %780 = fmul reassoc ninf nsz float %745, %707
  %781 = fadd reassoc ninf nsz float %779, %780
  %782 = fmul reassoc ninf nsz float %761, %778
  %783 = fmul reassoc ninf nsz float %777, %707
  %784 = fadd reassoc ninf nsz float %782, %783
  %785 = fsub reassoc ninf nsz float 1.000000e+00, %709
  %786 = fmul reassoc ninf nsz float %781, %785
  %787 = fmul reassoc ninf nsz float %784, %709
  %788 = fadd reassoc ninf nsz float %786, %787
  store float %788, float* %16, align 4
  br label %after_if69

false_block68:                                    ; preds = %after_if60
  %789 = sitofp i32 %84 to float
  %790 = fsub reassoc ninf nsz float %63, %789
  %791 = sitofp i32 %86 to float
  %792 = fsub reassoc ninf nsz float %77, %791
  %793 = fadd reassoc ninf nsz float %790, 1.000000e+00
  %794 = call reassoc ninf nsz float @__nv_fabsf(float %793)
  store float 0.000000e+00, float* %20, align 4
  %795 = fcmp reassoc ninf nsz ole float %794, 1.000000e+00
  %796 = icmp ne i1 %795, false
  br i1 %796, label %true_block70, label %false_block71

after_if69:                                       ; preds = %after_if114, %true_block67
  %797 = load float, float* %16, align 4
  %798 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %799 = bitcast i8** %798 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %800 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %799, align 8
  %801 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %800, i32 0, i32 6
  %802 = load float, float* %801, align 4
  %803 = fmul reassoc ninf nsz float %200, %802
  %804 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %805 = bitcast i8** %804 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %806 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %805, align 8
  %807 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %806, i32 0, i32 1
  %808 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 1
  %809 = load float*, float** %808, align 8
  %810 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 0, i32 0
  %811 = load i32, i32* %810, align 4
  %812 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 0, i32 1
  %813 = load i32, i32* %812, align 4
  %814 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 0, i32 2
  %815 = load i32, i32* %814, align 4
  %816 = mul i32 0, %811
  %817 = add i32 %816, %47
  %818 = mul i32 %817, %813
  %819 = add i32 %818, %49
  %820 = mul i32 %819, %815
  %821 = add i32 %820, 0
  %822 = getelementptr float, float* %809, i32 %821
  store float %803, float* %822, align 4
  %823 = fmul reassoc ninf nsz float %797, %802
  %824 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 1
  %825 = load float*, float** %824, align 8
  %826 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 0, i32 0
  %827 = load i32, i32* %826, align 4
  %828 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 0, i32 1
  %829 = load i32, i32* %828, align 4
  %830 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %807, i32 0, i32 0, i32 2
  %831 = load i32, i32* %830, align 4
  %832 = mul i32 0, %827
  %833 = add i32 %832, %47
  %834 = mul i32 %833, %829
  %835 = add i32 %834, %49
  %836 = mul i32 %835, %831
  %837 = add i32 %836, 1
  %838 = getelementptr float, float* %825, i32 %837
  store float %823, float* %838, align 4
  br label %final

true_block70:                                     ; preds = %false_block68
  %839 = fmul reassoc ninf nsz float %794, 1.500000e+00
  %840 = fmul reassoc ninf nsz float %839, %794
  %841 = fmul reassoc ninf nsz float %840, %794
  %842 = fmul reassoc ninf nsz float %794, 2.500000e+00
  %843 = fmul reassoc ninf nsz float %842, %794
  %844 = fsub reassoc ninf nsz float %841, %843
  %845 = fadd reassoc ninf nsz float %844, 1.000000e+00
  store float %845, float* %20, align 4
  br label %after_if72

false_block71:                                    ; preds = %false_block68
  %846 = fcmp reassoc ninf nsz olt float %794, 2.000000e+00
  %847 = icmp ne i1 %846, false
  br i1 %847, label %true_block73, label %false_block74

after_if72:                                       ; preds = %after_if75, %true_block70
  %848 = call reassoc ninf nsz float @__nv_fabsf(float %790)
  store float 0.000000e+00, float* %21, align 4
  %849 = fcmp reassoc ninf nsz ole float %848, 1.000000e+00
  %850 = icmp ne i1 %849, false
  br i1 %850, label %true_block76, label %false_block77

true_block73:                                     ; preds = %false_block71
  %851 = fmul reassoc ninf nsz float %794, -5.000000e-01
  %852 = fmul reassoc ninf nsz float %851, %794
  %853 = fmul reassoc ninf nsz float %852, %794
  %854 = fmul reassoc ninf nsz float %794, 2.500000e+00
  %855 = fmul reassoc ninf nsz float %854, %794
  %856 = fadd reassoc ninf nsz float %853, %855
  %857 = fmul reassoc ninf nsz float %794, 4.000000e+00
  %858 = fsub reassoc ninf nsz float %856, %857
  %859 = fadd reassoc ninf nsz float %858, 2.000000e+00
  store float %859, float* %20, align 4
  br label %after_if75

false_block74:                                    ; preds = %false_block71
  br label %after_if75

after_if75:                                       ; preds = %false_block74, %true_block73
  br label %after_if72

true_block76:                                     ; preds = %after_if72
  %860 = fmul reassoc ninf nsz float %848, 1.500000e+00
  %861 = fmul reassoc ninf nsz float %860, %848
  %862 = fmul reassoc ninf nsz float %861, %848
  %863 = fmul reassoc ninf nsz float %848, 2.500000e+00
  %864 = fmul reassoc ninf nsz float %863, %848
  %865 = fsub reassoc ninf nsz float %862, %864
  %866 = fadd reassoc ninf nsz float %865, 1.000000e+00
  store float %866, float* %21, align 4
  br label %after_if78

false_block77:                                    ; preds = %after_if72
  %867 = fcmp reassoc ninf nsz olt float %848, 2.000000e+00
  %868 = icmp ne i1 %867, false
  br i1 %868, label %true_block79, label %false_block80

after_if78:                                       ; preds = %after_if81, %true_block76
  %869 = fsub reassoc ninf nsz float 1.000000e+00, %790
  %870 = call reassoc ninf nsz float @__nv_fabsf(float %869)
  store float 0.000000e+00, float* %22, align 4
  %871 = fcmp reassoc ninf nsz ole float %870, 1.000000e+00
  %872 = icmp ne i1 %871, false
  br i1 %872, label %true_block82, label %false_block83

true_block79:                                     ; preds = %false_block77
  %873 = fmul reassoc ninf nsz float %848, -5.000000e-01
  %874 = fmul reassoc ninf nsz float %873, %848
  %875 = fmul reassoc ninf nsz float %874, %848
  %876 = fmul reassoc ninf nsz float %848, 2.500000e+00
  %877 = fmul reassoc ninf nsz float %876, %848
  %878 = fadd reassoc ninf nsz float %875, %877
  %879 = fmul reassoc ninf nsz float %848, 4.000000e+00
  %880 = fsub reassoc ninf nsz float %878, %879
  %881 = fadd reassoc ninf nsz float %880, 2.000000e+00
  store float %881, float* %21, align 4
  br label %after_if81

false_block80:                                    ; preds = %false_block77
  br label %after_if81

after_if81:                                       ; preds = %false_block80, %true_block79
  br label %after_if78

true_block82:                                     ; preds = %after_if78
  %882 = fmul reassoc ninf nsz float %870, 1.500000e+00
  %883 = fmul reassoc ninf nsz float %882, %870
  %884 = fmul reassoc ninf nsz float %883, %870
  %885 = fmul reassoc ninf nsz float %870, 2.500000e+00
  %886 = fmul reassoc ninf nsz float %885, %870
  %887 = fsub reassoc ninf nsz float %884, %886
  %888 = fadd reassoc ninf nsz float %887, 1.000000e+00
  store float %888, float* %22, align 4
  br label %after_if84

false_block83:                                    ; preds = %after_if78
  %889 = fcmp reassoc ninf nsz olt float %870, 2.000000e+00
  %890 = icmp ne i1 %889, false
  br i1 %890, label %true_block85, label %false_block86

after_if84:                                       ; preds = %after_if87, %true_block82
  %891 = fsub reassoc ninf nsz float 2.000000e+00, %790
  %892 = call reassoc ninf nsz float @__nv_fabsf(float %891)
  store float 0.000000e+00, float* %23, align 4
  %893 = fcmp reassoc ninf nsz ole float %892, 1.000000e+00
  %894 = icmp ne i1 %893, false
  br i1 %894, label %true_block88, label %false_block89

true_block85:                                     ; preds = %false_block83
  %895 = fmul reassoc ninf nsz float %870, -5.000000e-01
  %896 = fmul reassoc ninf nsz float %895, %870
  %897 = fmul reassoc ninf nsz float %896, %870
  %898 = fmul reassoc ninf nsz float %870, 2.500000e+00
  %899 = fmul reassoc ninf nsz float %898, %870
  %900 = fadd reassoc ninf nsz float %897, %899
  %901 = fmul reassoc ninf nsz float %870, 4.000000e+00
  %902 = fsub reassoc ninf nsz float %900, %901
  %903 = fadd reassoc ninf nsz float %902, 2.000000e+00
  store float %903, float* %22, align 4
  br label %after_if87

false_block86:                                    ; preds = %false_block83
  br label %after_if87

after_if87:                                       ; preds = %false_block86, %true_block85
  br label %after_if84

true_block88:                                     ; preds = %after_if84
  %904 = fmul reassoc ninf nsz float %892, 1.500000e+00
  %905 = fmul reassoc ninf nsz float %904, %892
  %906 = fmul reassoc ninf nsz float %905, %892
  %907 = fmul reassoc ninf nsz float %892, 2.500000e+00
  %908 = fmul reassoc ninf nsz float %907, %892
  %909 = fsub reassoc ninf nsz float %906, %908
  %910 = fadd reassoc ninf nsz float %909, 1.000000e+00
  store float %910, float* %23, align 4
  br label %after_if90

false_block89:                                    ; preds = %after_if84
  %911 = fcmp reassoc ninf nsz olt float %892, 2.000000e+00
  %912 = icmp ne i1 %911, false
  br i1 %912, label %true_block91, label %false_block92

after_if90:                                       ; preds = %after_if93, %true_block88
  %913 = load float, float* %20, align 4
  %914 = load float, float* %21, align 4
  %915 = load float, float* %22, align 4
  %916 = load float, float* %23, align 4
  %917 = fadd reassoc ninf nsz float %792, 1.000000e+00
  %918 = call reassoc ninf nsz float @__nv_fabsf(float %917)
  store float 0.000000e+00, float* %24, align 4
  %919 = fcmp reassoc ninf nsz ole float %918, 1.000000e+00
  %920 = icmp ne i1 %919, false
  br i1 %920, label %true_block94, label %false_block95

true_block91:                                     ; preds = %false_block89
  %921 = fmul reassoc ninf nsz float %892, -5.000000e-01
  %922 = fmul reassoc ninf nsz float %921, %892
  %923 = fmul reassoc ninf nsz float %922, %892
  %924 = fmul reassoc ninf nsz float %892, 2.500000e+00
  %925 = fmul reassoc ninf nsz float %924, %892
  %926 = fadd reassoc ninf nsz float %923, %925
  %927 = fmul reassoc ninf nsz float %892, 4.000000e+00
  %928 = fsub reassoc ninf nsz float %926, %927
  %929 = fadd reassoc ninf nsz float %928, 2.000000e+00
  store float %929, float* %23, align 4
  br label %after_if93

false_block92:                                    ; preds = %false_block89
  br label %after_if93

after_if93:                                       ; preds = %false_block92, %true_block91
  br label %after_if90

true_block94:                                     ; preds = %after_if90
  %930 = fmul reassoc ninf nsz float %918, 1.500000e+00
  %931 = fmul reassoc ninf nsz float %930, %918
  %932 = fmul reassoc ninf nsz float %931, %918
  %933 = fmul reassoc ninf nsz float %918, 2.500000e+00
  %934 = fmul reassoc ninf nsz float %933, %918
  %935 = fsub reassoc ninf nsz float %932, %934
  %936 = fadd reassoc ninf nsz float %935, 1.000000e+00
  store float %936, float* %24, align 4
  br label %after_if96

false_block95:                                    ; preds = %after_if90
  %937 = fcmp reassoc ninf nsz olt float %918, 2.000000e+00
  %938 = icmp ne i1 %937, false
  br i1 %938, label %true_block97, label %false_block98

after_if96:                                       ; preds = %after_if99, %true_block94
  %939 = call reassoc ninf nsz float @__nv_fabsf(float %792)
  store float 0.000000e+00, float* %25, align 4
  %940 = fcmp reassoc ninf nsz ole float %939, 1.000000e+00
  %941 = icmp ne i1 %940, false
  br i1 %941, label %true_block100, label %false_block101

true_block97:                                     ; preds = %false_block95
  %942 = fmul reassoc ninf nsz float %918, -5.000000e-01
  %943 = fmul reassoc ninf nsz float %942, %918
  %944 = fmul reassoc ninf nsz float %943, %918
  %945 = fmul reassoc ninf nsz float %918, 2.500000e+00
  %946 = fmul reassoc ninf nsz float %945, %918
  %947 = fadd reassoc ninf nsz float %944, %946
  %948 = fmul reassoc ninf nsz float %918, 4.000000e+00
  %949 = fsub reassoc ninf nsz float %947, %948
  %950 = fadd reassoc ninf nsz float %949, 2.000000e+00
  store float %950, float* %24, align 4
  br label %after_if99

false_block98:                                    ; preds = %false_block95
  br label %after_if99

after_if99:                                       ; preds = %false_block98, %true_block97
  br label %after_if96

true_block100:                                    ; preds = %after_if96
  %951 = fmul reassoc ninf nsz float %939, 1.500000e+00
  %952 = fmul reassoc ninf nsz float %951, %939
  %953 = fmul reassoc ninf nsz float %952, %939
  %954 = fmul reassoc ninf nsz float %939, 2.500000e+00
  %955 = fmul reassoc ninf nsz float %954, %939
  %956 = fsub reassoc ninf nsz float %953, %955
  %957 = fadd reassoc ninf nsz float %956, 1.000000e+00
  store float %957, float* %25, align 4
  br label %after_if102

false_block101:                                   ; preds = %after_if96
  %958 = fcmp reassoc ninf nsz olt float %939, 2.000000e+00
  %959 = icmp ne i1 %958, false
  br i1 %959, label %true_block103, label %false_block104

after_if102:                                      ; preds = %after_if105, %true_block100
  %960 = fsub reassoc ninf nsz float 1.000000e+00, %792
  %961 = call reassoc ninf nsz float @__nv_fabsf(float %960)
  store float 0.000000e+00, float* %26, align 4
  %962 = fcmp reassoc ninf nsz ole float %961, 1.000000e+00
  %963 = icmp ne i1 %962, false
  br i1 %963, label %true_block106, label %false_block107

true_block103:                                    ; preds = %false_block101
  %964 = fmul reassoc ninf nsz float %939, -5.000000e-01
  %965 = fmul reassoc ninf nsz float %964, %939
  %966 = fmul reassoc ninf nsz float %965, %939
  %967 = fmul reassoc ninf nsz float %939, 2.500000e+00
  %968 = fmul reassoc ninf nsz float %967, %939
  %969 = fadd reassoc ninf nsz float %966, %968
  %970 = fmul reassoc ninf nsz float %939, 4.000000e+00
  %971 = fsub reassoc ninf nsz float %969, %970
  %972 = fadd reassoc ninf nsz float %971, 2.000000e+00
  store float %972, float* %25, align 4
  br label %after_if105

false_block104:                                   ; preds = %false_block101
  br label %after_if105

after_if105:                                      ; preds = %false_block104, %true_block103
  br label %after_if102

true_block106:                                    ; preds = %after_if102
  %973 = fmul reassoc ninf nsz float %961, 1.500000e+00
  %974 = fmul reassoc ninf nsz float %973, %961
  %975 = fmul reassoc ninf nsz float %974, %961
  %976 = fmul reassoc ninf nsz float %961, 2.500000e+00
  %977 = fmul reassoc ninf nsz float %976, %961
  %978 = fsub reassoc ninf nsz float %975, %977
  %979 = fadd reassoc ninf nsz float %978, 1.000000e+00
  store float %979, float* %26, align 4
  br label %after_if108

false_block107:                                   ; preds = %after_if102
  %980 = fcmp reassoc ninf nsz olt float %961, 2.000000e+00
  %981 = icmp ne i1 %980, false
  br i1 %981, label %true_block109, label %false_block110

after_if108:                                      ; preds = %after_if111, %true_block106
  %982 = fsub reassoc ninf nsz float 2.000000e+00, %792
  %983 = call reassoc ninf nsz float @__nv_fabsf(float %982)
  store float 0.000000e+00, float* %27, align 4
  %984 = fcmp reassoc ninf nsz ole float %983, 1.000000e+00
  %985 = icmp ne i1 %984, false
  br i1 %985, label %true_block112, label %false_block113

true_block109:                                    ; preds = %false_block107
  %986 = fmul reassoc ninf nsz float %961, -5.000000e-01
  %987 = fmul reassoc ninf nsz float %986, %961
  %988 = fmul reassoc ninf nsz float %987, %961
  %989 = fmul reassoc ninf nsz float %961, 2.500000e+00
  %990 = fmul reassoc ninf nsz float %989, %961
  %991 = fadd reassoc ninf nsz float %988, %990
  %992 = fmul reassoc ninf nsz float %961, 4.000000e+00
  %993 = fsub reassoc ninf nsz float %991, %992
  %994 = fadd reassoc ninf nsz float %993, 2.000000e+00
  store float %994, float* %26, align 4
  br label %after_if111

false_block110:                                   ; preds = %false_block107
  br label %after_if111

after_if111:                                      ; preds = %false_block110, %true_block109
  br label %after_if108

true_block112:                                    ; preds = %after_if108
  %995 = fmul reassoc ninf nsz float %983, 1.500000e+00
  %996 = fmul reassoc ninf nsz float %995, %983
  %997 = fmul reassoc ninf nsz float %996, %983
  %998 = fmul reassoc ninf nsz float %983, 2.500000e+00
  %999 = fmul reassoc ninf nsz float %998, %983
  %1000 = fsub reassoc ninf nsz float %997, %999
  %1001 = fadd reassoc ninf nsz float %1000, 1.000000e+00
  store float %1001, float* %27, align 4
  br label %after_if114

false_block113:                                   ; preds = %after_if108
  %1002 = fcmp reassoc ninf nsz olt float %983, 2.000000e+00
  %1003 = icmp ne i1 %1002, false
  br i1 %1003, label %true_block115, label %false_block116

after_if114:                                      ; preds = %after_if117, %true_block112
  %1004 = load float, float* %24, align 4
  %1005 = load float, float* %25, align 4
  %1006 = load float, float* %26, align 4
  %1007 = load float, float* %27, align 4
  %1008 = sub i32 %86, 1
  %1009 = sub i32 %84, 1
  %1010 = getelementptr %struct.RuntimeContext.49, %struct.RuntimeContext.49* %0, i32 0, i32 0
  %1011 = bitcast i8** %1010 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }**
  %1012 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }** %1011, align 8
  %1013 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32, i32, i32, float }* %1012, i32 0, i32 0
  %1014 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1015 = load float*, float** %1014, align 8
  %1016 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1017 = load i32, i32* %1016, align 4
  %1018 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1019 = load i32, i32* %1018, align 4
  %1020 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1021 = load i32, i32* %1020, align 4
  %1022 = mul i32 0, %1017
  %1023 = add i32 %1022, %1008
  %1024 = mul i32 %1023, %1019
  %1025 = add i32 %1024, %1009
  %1026 = mul i32 %1025, %1021
  %1027 = add i32 %1026, 1
  %1028 = getelementptr float, float* %1015, i32 %1027
  %1029 = load float, float* %1028, align 4
  %1030 = fmul reassoc ninf nsz float %1029, %913
  %1031 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1032 = load float*, float** %1031, align 8
  %1033 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1034 = load i32, i32* %1033, align 4
  %1035 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1036 = load i32, i32* %1035, align 4
  %1037 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1038 = load i32, i32* %1037, align 4
  %1039 = mul i32 0, %1034
  %1040 = add i32 %1039, %1008
  %1041 = mul i32 %1040, %1036
  %1042 = add i32 %1041, %84
  %1043 = mul i32 %1042, %1038
  %1044 = add i32 %1043, 1
  %1045 = getelementptr float, float* %1032, i32 %1044
  %1046 = load float, float* %1045, align 4
  %1047 = fmul reassoc ninf nsz float %1046, %914
  %1048 = fadd reassoc ninf nsz float %1030, %1047
  %1049 = sub i32 %84, -1
  %1050 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1051 = load float*, float** %1050, align 8
  %1052 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1053 = load i32, i32* %1052, align 4
  %1054 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1055 = load i32, i32* %1054, align 4
  %1056 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1057 = load i32, i32* %1056, align 4
  %1058 = mul i32 0, %1053
  %1059 = add i32 %1058, %1008
  %1060 = mul i32 %1059, %1055
  %1061 = add i32 %1060, %1049
  %1062 = mul i32 %1061, %1057
  %1063 = add i32 %1062, 1
  %1064 = getelementptr float, float* %1051, i32 %1063
  %1065 = load float, float* %1064, align 4
  %1066 = fmul reassoc ninf nsz float %1065, %915
  %1067 = fadd reassoc ninf nsz float %1048, %1066
  %1068 = sub i32 %84, -2
  %1069 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1070 = load float*, float** %1069, align 8
  %1071 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1072 = load i32, i32* %1071, align 4
  %1073 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1074 = load i32, i32* %1073, align 4
  %1075 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1076 = load i32, i32* %1075, align 4
  %1077 = mul i32 0, %1072
  %1078 = add i32 %1077, %1008
  %1079 = mul i32 %1078, %1074
  %1080 = add i32 %1079, %1068
  %1081 = mul i32 %1080, %1076
  %1082 = add i32 %1081, 1
  %1083 = getelementptr float, float* %1070, i32 %1082
  %1084 = load float, float* %1083, align 4
  %1085 = fmul reassoc ninf nsz float %1084, %916
  %1086 = fadd reassoc ninf nsz float %1067, %1085
  %1087 = fmul reassoc ninf nsz float %1086, %1004
  %1088 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1089 = load float*, float** %1088, align 8
  %1090 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1091 = load i32, i32* %1090, align 4
  %1092 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1093 = load i32, i32* %1092, align 4
  %1094 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1095 = load i32, i32* %1094, align 4
  %1096 = mul i32 0, %1091
  %1097 = add i32 %1096, %86
  %1098 = mul i32 %1097, %1093
  %1099 = add i32 %1098, %1009
  %1100 = mul i32 %1099, %1095
  %1101 = add i32 %1100, 1
  %1102 = getelementptr float, float* %1089, i32 %1101
  %1103 = load float, float* %1102, align 4
  %1104 = fmul reassoc ninf nsz float %1103, %913
  %1105 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1106 = load float*, float** %1105, align 8
  %1107 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1108 = load i32, i32* %1107, align 4
  %1109 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1110 = load i32, i32* %1109, align 4
  %1111 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1112 = load i32, i32* %1111, align 4
  %1113 = mul i32 0, %1108
  %1114 = add i32 %1113, %86
  %1115 = mul i32 %1114, %1110
  %1116 = add i32 %1115, %84
  %1117 = mul i32 %1116, %1112
  %1118 = add i32 %1117, 1
  %1119 = getelementptr float, float* %1106, i32 %1118
  %1120 = load float, float* %1119, align 4
  %1121 = fmul reassoc ninf nsz float %1120, %914
  %1122 = fadd reassoc ninf nsz float %1104, %1121
  %1123 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1124 = load float*, float** %1123, align 8
  %1125 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1126 = load i32, i32* %1125, align 4
  %1127 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1128 = load i32, i32* %1127, align 4
  %1129 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1130 = load i32, i32* %1129, align 4
  %1131 = mul i32 0, %1126
  %1132 = add i32 %1131, %86
  %1133 = mul i32 %1132, %1128
  %1134 = add i32 %1133, %1049
  %1135 = mul i32 %1134, %1130
  %1136 = add i32 %1135, 1
  %1137 = getelementptr float, float* %1124, i32 %1136
  %1138 = load float, float* %1137, align 4
  %1139 = fmul reassoc ninf nsz float %1138, %915
  %1140 = fadd reassoc ninf nsz float %1122, %1139
  %1141 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1142 = load float*, float** %1141, align 8
  %1143 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1144 = load i32, i32* %1143, align 4
  %1145 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1146 = load i32, i32* %1145, align 4
  %1147 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1148 = load i32, i32* %1147, align 4
  %1149 = mul i32 0, %1144
  %1150 = add i32 %1149, %86
  %1151 = mul i32 %1150, %1146
  %1152 = add i32 %1151, %1068
  %1153 = mul i32 %1152, %1148
  %1154 = add i32 %1153, 1
  %1155 = getelementptr float, float* %1142, i32 %1154
  %1156 = load float, float* %1155, align 4
  %1157 = fmul reassoc ninf nsz float %1156, %916
  %1158 = fadd reassoc ninf nsz float %1140, %1157
  %1159 = fmul reassoc ninf nsz float %1158, %1005
  %1160 = fadd reassoc ninf nsz float %1087, %1159
  %1161 = sub i32 %86, -1
  %1162 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1163 = load float*, float** %1162, align 8
  %1164 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1165 = load i32, i32* %1164, align 4
  %1166 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1167 = load i32, i32* %1166, align 4
  %1168 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1169 = load i32, i32* %1168, align 4
  %1170 = mul i32 0, %1165
  %1171 = add i32 %1170, %1161
  %1172 = mul i32 %1171, %1167
  %1173 = add i32 %1172, %1009
  %1174 = mul i32 %1173, %1169
  %1175 = add i32 %1174, 1
  %1176 = getelementptr float, float* %1163, i32 %1175
  %1177 = load float, float* %1176, align 4
  %1178 = fmul reassoc ninf nsz float %1177, %913
  %1179 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1180 = load float*, float** %1179, align 8
  %1181 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1182 = load i32, i32* %1181, align 4
  %1183 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1184 = load i32, i32* %1183, align 4
  %1185 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1186 = load i32, i32* %1185, align 4
  %1187 = mul i32 0, %1182
  %1188 = add i32 %1187, %1161
  %1189 = mul i32 %1188, %1184
  %1190 = add i32 %1189, %84
  %1191 = mul i32 %1190, %1186
  %1192 = add i32 %1191, 1
  %1193 = getelementptr float, float* %1180, i32 %1192
  %1194 = load float, float* %1193, align 4
  %1195 = fmul reassoc ninf nsz float %1194, %914
  %1196 = fadd reassoc ninf nsz float %1178, %1195
  %1197 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1198 = load float*, float** %1197, align 8
  %1199 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1200 = load i32, i32* %1199, align 4
  %1201 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1202 = load i32, i32* %1201, align 4
  %1203 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1204 = load i32, i32* %1203, align 4
  %1205 = mul i32 0, %1200
  %1206 = add i32 %1205, %1161
  %1207 = mul i32 %1206, %1202
  %1208 = add i32 %1207, %1049
  %1209 = mul i32 %1208, %1204
  %1210 = add i32 %1209, 1
  %1211 = getelementptr float, float* %1198, i32 %1210
  %1212 = load float, float* %1211, align 4
  %1213 = fmul reassoc ninf nsz float %1212, %915
  %1214 = fadd reassoc ninf nsz float %1196, %1213
  %1215 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1216 = load float*, float** %1215, align 8
  %1217 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1218 = load i32, i32* %1217, align 4
  %1219 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1220 = load i32, i32* %1219, align 4
  %1221 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1222 = load i32, i32* %1221, align 4
  %1223 = mul i32 0, %1218
  %1224 = add i32 %1223, %1161
  %1225 = mul i32 %1224, %1220
  %1226 = add i32 %1225, %1068
  %1227 = mul i32 %1226, %1222
  %1228 = add i32 %1227, 1
  %1229 = getelementptr float, float* %1216, i32 %1228
  %1230 = load float, float* %1229, align 4
  %1231 = fmul reassoc ninf nsz float %1230, %916
  %1232 = fadd reassoc ninf nsz float %1214, %1231
  %1233 = fmul reassoc ninf nsz float %1232, %1006
  %1234 = fadd reassoc ninf nsz float %1160, %1233
  %1235 = sub i32 %86, -2
  %1236 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1237 = load float*, float** %1236, align 8
  %1238 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1239 = load i32, i32* %1238, align 4
  %1240 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1241 = load i32, i32* %1240, align 4
  %1242 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1243 = load i32, i32* %1242, align 4
  %1244 = mul i32 0, %1239
  %1245 = add i32 %1244, %1235
  %1246 = mul i32 %1245, %1241
  %1247 = add i32 %1246, %1009
  %1248 = mul i32 %1247, %1243
  %1249 = add i32 %1248, 1
  %1250 = getelementptr float, float* %1237, i32 %1249
  %1251 = load float, float* %1250, align 4
  %1252 = fmul reassoc ninf nsz float %1251, %913
  %1253 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1254 = load float*, float** %1253, align 8
  %1255 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1256 = load i32, i32* %1255, align 4
  %1257 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1258 = load i32, i32* %1257, align 4
  %1259 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1260 = load i32, i32* %1259, align 4
  %1261 = mul i32 0, %1256
  %1262 = add i32 %1261, %1235
  %1263 = mul i32 %1262, %1258
  %1264 = add i32 %1263, %84
  %1265 = mul i32 %1264, %1260
  %1266 = add i32 %1265, 1
  %1267 = getelementptr float, float* %1254, i32 %1266
  %1268 = load float, float* %1267, align 4
  %1269 = fmul reassoc ninf nsz float %1268, %914
  %1270 = fadd reassoc ninf nsz float %1252, %1269
  %1271 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1272 = load float*, float** %1271, align 8
  %1273 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1274 = load i32, i32* %1273, align 4
  %1275 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1276 = load i32, i32* %1275, align 4
  %1277 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1278 = load i32, i32* %1277, align 4
  %1279 = mul i32 0, %1274
  %1280 = add i32 %1279, %1235
  %1281 = mul i32 %1280, %1276
  %1282 = add i32 %1281, %1049
  %1283 = mul i32 %1282, %1278
  %1284 = add i32 %1283, 1
  %1285 = getelementptr float, float* %1272, i32 %1284
  %1286 = load float, float* %1285, align 4
  %1287 = fmul reassoc ninf nsz float %1286, %915
  %1288 = fadd reassoc ninf nsz float %1270, %1287
  %1289 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 1
  %1290 = load float*, float** %1289, align 8
  %1291 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 0
  %1292 = load i32, i32* %1291, align 4
  %1293 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 1
  %1294 = load i32, i32* %1293, align 4
  %1295 = getelementptr { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }* %1013, i32 0, i32 0, i32 2
  %1296 = load i32, i32* %1295, align 4
  %1297 = mul i32 0, %1292
  %1298 = add i32 %1297, %1235
  %1299 = mul i32 %1298, %1294
  %1300 = add i32 %1299, %1068
  %1301 = mul i32 %1300, %1296
  %1302 = add i32 %1301, 1
  %1303 = getelementptr float, float* %1290, i32 %1302
  %1304 = load float, float* %1303, align 4
  %1305 = fmul reassoc ninf nsz float %1304, %916
  %1306 = fadd reassoc ninf nsz float %1288, %1305
  %1307 = fmul reassoc ninf nsz float %1306, %1007
  %1308 = fadd reassoc ninf nsz float %1234, %1307
  store float %1308, float* %16, align 4
  br label %after_if69

true_block115:                                    ; preds = %false_block113
  %1309 = fmul reassoc ninf nsz float %983, -5.000000e-01
  %1310 = fmul reassoc ninf nsz float %1309, %983
  %1311 = fmul reassoc ninf nsz float %1310, %983
  %1312 = fmul reassoc ninf nsz float %983, 2.500000e+00
  %1313 = fmul reassoc ninf nsz float %1312, %983
  %1314 = fadd reassoc ninf nsz float %1311, %1313
  %1315 = fmul reassoc ninf nsz float %983, 4.000000e+00
  %1316 = fsub reassoc ninf nsz float %1314, %1315
  %1317 = fadd reassoc ninf nsz float %1316, 2.000000e+00
  store float %1317, float* %27, align 4
  br label %after_if117

false_block116:                                   ; preds = %false_block113
  br label %after_if117

after_if117:                                      ; preds = %false_block116, %true_block115
  br label %after_if114
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #0

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
define internal %struct.LLVMRuntime.48* @RuntimeContext_get_runtime(%struct.RuntimeContext.49* noundef %0) #1 {
  %2 = alloca %struct.RuntimeContext.49*, align 8
  store %struct.RuntimeContext.49* %0, %struct.RuntimeContext.49** %2, align 8
  %3 = load %struct.RuntimeContext.49*, %struct.RuntimeContext.49** %2, align 8
  %4 = getelementptr inbounds %struct.RuntimeContext.49, %struct.RuntimeContext.49* %3, i32 0, i32 1
  %5 = load %struct.LLVMRuntime.48*, %struct.LLVMRuntime.48** %4, align 8
  ret %struct.LLVMRuntime.48* %5
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i8* @get_temporary_pointer(%struct.LLVMRuntime.48* noundef %0, i64 noundef %1) #1 {
  %3 = alloca i64, align 8
  %4 = alloca %struct.LLVMRuntime.48*, align 8
  store i64 %1, i64* %3, align 8
  store %struct.LLVMRuntime.48* %0, %struct.LLVMRuntime.48** %4, align 8
  %5 = load %struct.LLVMRuntime.48*, %struct.LLVMRuntime.48** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.48, %struct.LLVMRuntime.48* %5, i32 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = load i64, i64* %3, align 8
  %9 = getelementptr inbounds i8, i8* %7, i64 %8
  ret i8* %9
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @gpu_parallel_range_for(%struct.RuntimeContext.49* noundef %0, i32 noundef %1, i32 noundef %2, void (%struct.RuntimeContext.49*, i8*)* noundef %3, void (%struct.RuntimeContext.49*, i8*, i32)* noundef %4, void (%struct.RuntimeContext.49*, i8*)* noundef %5, i64 noundef %6) #1 {
  %8 = alloca i64, align 8
  %9 = alloca void (%struct.RuntimeContext.49*, i8*)*, align 8
  %10 = alloca void (%struct.RuntimeContext.49*, i8*, i32)*, align 8
  %11 = alloca void (%struct.RuntimeContext.49*, i8*)*, align 8
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca %struct.RuntimeContext.49*, align 8
  %15 = alloca i32, align 4
  %16 = alloca i8*, align 8
  %17 = alloca i64, align 8
  %18 = alloca i8*, align 8
  store i64 %6, i64* %8, align 8
  store void (%struct.RuntimeContext.49*, i8*)* %5, void (%struct.RuntimeContext.49*, i8*)** %9, align 8
  store void (%struct.RuntimeContext.49*, i8*, i32)* %4, void (%struct.RuntimeContext.49*, i8*, i32)** %10, align 8
  store void (%struct.RuntimeContext.49*, i8*)* %3, void (%struct.RuntimeContext.49*, i8*)** %11, align 8
  store i32 %2, i32* %12, align 4
  store i32 %1, i32* %13, align 4
  store %struct.RuntimeContext.49* %0, %struct.RuntimeContext.49** %14, align 8
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
  %30 = load void (%struct.RuntimeContext.49*, i8*)*, void (%struct.RuntimeContext.49*, i8*)** %11, align 8
  %31 = icmp ne void (%struct.RuntimeContext.49*, i8*)* %30, null
  br i1 %31, label %32, label %36

32:                                               ; preds = %7
  %33 = load void (%struct.RuntimeContext.49*, i8*)*, void (%struct.RuntimeContext.49*, i8*)** %11, align 8
  %34 = load i8*, i8** %18, align 8
  %35 = load %struct.RuntimeContext.49*, %struct.RuntimeContext.49** %14, align 8
  call void %33(%struct.RuntimeContext.49* noundef %35, i8* noundef %34)
  br label %36

36:                                               ; preds = %32, %7
  br label %37

37:                                               ; preds = %41, %36
  %38 = load i32, i32* %15, align 4
  %39 = load i32, i32* %12, align 4
  %40 = icmp slt i32 %38, %39
  br i1 %40, label %41, label %51

41:                                               ; preds = %37
  %42 = load void (%struct.RuntimeContext.49*, i8*, i32)*, void (%struct.RuntimeContext.49*, i8*, i32)** %10, align 8
  %43 = load i32, i32* %15, align 4
  %44 = load i8*, i8** %18, align 8
  %45 = load %struct.RuntimeContext.49*, %struct.RuntimeContext.49** %14, align 8
  call void %42(%struct.RuntimeContext.49* noundef %45, i8* noundef %44, i32 noundef %43)
  %46 = call i32 @block_dim()
  %47 = call i32 @grid_dim()
  %48 = mul nsw i32 %46, %47
  %49 = load i32, i32* %15, align 4
  %50 = add nsw i32 %49, %48
  store i32 %50, i32* %15, align 4
  br label %37, !llvm.loop !20

51:                                               ; preds = %37
  %52 = load void (%struct.RuntimeContext.49*, i8*)*, void (%struct.RuntimeContext.49*, i8*)** %9, align 8
  %53 = icmp ne void (%struct.RuntimeContext.49*, i8*)* %52, null
  br i1 %53, label %54, label %58

54:                                               ; preds = %51
  %55 = load void (%struct.RuntimeContext.49*, i8*)*, void (%struct.RuntimeContext.49*, i8*)** %9, align 8
  %56 = load i8*, i8** %18, align 8
  %57 = load %struct.RuntimeContext.49*, %struct.RuntimeContext.49** %14, align 8
  call void %55(%struct.RuntimeContext.49* noundef %57, i8* noundef %56)
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

!0 = !{void (%struct.RuntimeContext.49*)* @_upsample_flow_kernel_c154_0_kernel_0_serial, !"kernel", i32 1}
!1 = !{void (%struct.RuntimeContext.49*)* @_upsample_flow_kernel_c154_0_kernel_0_serial, !"maxntidx", i32 1}
!2 = !{void (%struct.RuntimeContext.49*)* @_upsample_flow_kernel_c154_0_kernel_0_serial, !"minctasm", i32 2}
!3 = !{void (%struct.RuntimeContext.49*)* @_upsample_flow_kernel_c154_0_kernel_1_range_for, !"kernel", i32 1}
!4 = !{void (%struct.RuntimeContext.49*)* @_upsample_flow_kernel_c154_0_kernel_1_range_for, !"maxntidx", i32 128}
!5 = !{void (%struct.RuntimeContext.49*)* @_upsample_flow_kernel_c154_0_kernel_1_range_for, !"minctasm", i32 2}
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
