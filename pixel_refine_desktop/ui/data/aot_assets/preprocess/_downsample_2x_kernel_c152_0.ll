; ModuleID = 'kernel'
source_filename = "kernel"
target triple = "nvptx64-nvidia-cuda"

%struct.RuntimeContext.25 = type { i8*, %struct.LLVMRuntime.24*, i32, i64* }
%struct.LLVMRuntime.24 = type { %struct.PreallocatedMemoryChunk.20, %struct.PreallocatedMemoryChunk.20, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.21*], [1024 x %struct.NodeManager.22*], [1024 x i8*], i8*, %struct.RandState.23*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.20 = type { i8*, i8*, i64 }
%struct.ListManager.21 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.24* }
%struct.NodeManager.22 = type { %struct.LLVMRuntime.24*, i32, i32, i32, i32, %struct.ListManager.21*, %struct.ListManager.21*, %struct.ListManager.21*, i32 }
%struct.RandState.23 = type { i32, i32, i32, i32, i32 }

define void @_downsample_2x_kernel_c152_0_kernel_0_serial(%struct.RuntimeContext.25* byval(%struct.RuntimeContext.25) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = getelementptr %struct.RuntimeContext.25, %struct.RuntimeContext.25* %context, i32 0, i32 0
  %1 = bitcast i8** %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %2 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %1, align 8
  %3 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %2, i32 0, i32 4
  %4 = load i32, i32* %3, align 4
  %5 = call i32 @max_i32(i32 0, i32 %4)
  %6 = getelementptr %struct.RuntimeContext.25, %struct.RuntimeContext.25* %context, i32 0, i32 0
  %7 = bitcast i8** %6 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %8 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %7, align 8
  %9 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %8, i32 0, i32 5
  %10 = load i32, i32* %9, align 4
  %11 = call i32 @max_i32(i32 0, i32 %10)
  %12 = call %struct.LLVMRuntime.24* @RuntimeContext_get_runtime(%struct.RuntimeContext.25* %context)
  %13 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.24* %12, i64 4)
  %14 = bitcast i8* %13 to i32*
  store i32 %11, i32* %14, align 4
  %15 = mul i32 %5, %11
  %16 = call %struct.LLVMRuntime.24* @RuntimeContext_get_runtime(%struct.RuntimeContext.25* %context)
  %17 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.24* %16, i64 0)
  %18 = bitcast i8* %17 to i32*
  store i32 %15, i32* %18, align 4
  br label %final
}

define void @_downsample_2x_kernel_c152_0_kernel_1_range_for(%struct.RuntimeContext.25* byval(%struct.RuntimeContext.25) %context) {
entry:
  br label %body

final:                                            ; preds = %body
  ret void

body:                                             ; preds = %entry
  %0 = call %struct.LLVMRuntime.24* @RuntimeContext_get_runtime(%struct.RuntimeContext.25* %context)
  %1 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.24* %0, i64 0)
  %2 = bitcast i8* %1 to i32*
  %3 = load i32, i32* %2, align 4
  call void @gpu_parallel_range_for(%struct.RuntimeContext.25* %context, i32 0, i32 %3, void (%struct.RuntimeContext.25*, i8*)* null, void (%struct.RuntimeContext.25*, i8*, i32)* @function_body, void (%struct.RuntimeContext.25*, i8*)* null, i64 1)
  br label %final
}

define internal void @function_body(%struct.RuntimeContext.25* %0, i8* %1, i32 %2) {
allocs:
  %3 = alloca i32, align 4
  br label %entry

final:                                            ; preds = %function_body
  ret void

entry:                                            ; preds = %allocs
  br label %function_body

function_body:                                    ; preds = %entry
  store i32 %2, i32* %3, align 4
  %4 = load i32, i32* %3, align 4
  %5 = call %struct.LLVMRuntime.24* @RuntimeContext_get_runtime(%struct.RuntimeContext.25* %0)
  %6 = call i8* @get_temporary_pointer(%struct.LLVMRuntime.24* %5, i64 4)
  %7 = bitcast i8* %6 to i32*
  %8 = load i32, i32* %7, align 4
  %9 = sdiv i32 %4, %8
  %10 = icmp slt i32 %4, 0
  %11 = icmp slt i32 %8, 0
  %12 = mul i32 %8, %9
  %13 = icmp ne i1 %10, %11
  %14 = icmp ne i32 %4, 0
  %15 = icmp ne i32 %12, %4
  %16 = icmp ne i1 %13, false
  %17 = icmp ne i1 %14, false
  %18 = and i1 %16, %17
  %19 = icmp ne i1 %18, false
  %20 = icmp ne i1 %15, false
  %21 = and i1 %19, %20
  %22 = zext i1 %21 to i32
  %23 = sub i32 %9, %22
  %24 = mul i32 %23, %8
  %25 = sub i32 %4, %24
  %26 = shl i32 %23, 1
  %27 = shl i32 %25, 1
  %28 = add i32 %26, -2
  %29 = getelementptr %struct.RuntimeContext.25, %struct.RuntimeContext.25* %0, i32 0, i32 0
  %30 = bitcast i8** %29 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %31 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %30, align 8
  %32 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %31, i32 0, i32 2
  %33 = load i32, i32* %32, align 4
  %34 = sub i32 %33, 1
  %35 = call i32 @max_i32(i32 0, i32 %28)
  %36 = call i32 @min_i32(i32 %34, i32 %35)
  %37 = add i32 %27, -2
  %38 = getelementptr %struct.RuntimeContext.25, %struct.RuntimeContext.25* %0, i32 0, i32 0
  %39 = bitcast i8** %38 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %40 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %39, align 8
  %41 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %40, i32 0, i32 3
  %42 = load i32, i32* %41, align 4
  %43 = sub i32 %42, 1
  %44 = call i32 @max_i32(i32 0, i32 %37)
  %45 = call i32 @min_i32(i32 %43, i32 %44)
  %46 = getelementptr %struct.RuntimeContext.25, %struct.RuntimeContext.25* %0, i32 0, i32 0
  %47 = bitcast i8** %46 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %48 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %47, align 8
  %49 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %48, i32 0, i32 0
  %50 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %51 = load float*, float** %50, align 8
  %52 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %53 = load i32, i32* %52, align 4
  %54 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %55 = load i32, i32* %54, align 4
  %56 = mul i32 0, %53
  %57 = add i32 %56, %36
  %58 = mul i32 %57, %55
  %59 = add i32 %58, %45
  %60 = getelementptr float, float* %51, i32 %59
  %61 = load float, float* %60, align 4
  %62 = add i32 %27, -1
  %63 = call i32 @max_i32(i32 0, i32 %62)
  %64 = call i32 @min_i32(i32 %43, i32 %63)
  %65 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %66 = load float*, float** %65, align 8
  %67 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %68 = load i32, i32* %67, align 4
  %69 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %70 = load i32, i32* %69, align 4
  %71 = mul i32 0, %68
  %72 = add i32 %71, %36
  %73 = mul i32 %72, %70
  %74 = add i32 %73, %64
  %75 = getelementptr float, float* %66, i32 %74
  %76 = load float, float* %75, align 4
  %77 = fmul reassoc ninf nsz float %76, 4.000000e+00
  %78 = fadd reassoc ninf nsz float %61, %77
  %79 = call i32 @max_i32(i32 0, i32 %27)
  %80 = call i32 @min_i32(i32 %43, i32 %79)
  %81 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %82 = load float*, float** %81, align 8
  %83 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %84 = load i32, i32* %83, align 4
  %85 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %86 = load i32, i32* %85, align 4
  %87 = mul i32 0, %84
  %88 = add i32 %87, %36
  %89 = mul i32 %88, %86
  %90 = add i32 %89, %80
  %91 = getelementptr float, float* %82, i32 %90
  %92 = load float, float* %91, align 4
  %93 = fmul reassoc ninf nsz float %92, 6.000000e+00
  %94 = fadd reassoc ninf nsz float %78, %93
  %95 = add i32 %27, 1
  %96 = call i32 @max_i32(i32 0, i32 %95)
  %97 = call i32 @min_i32(i32 %43, i32 %96)
  %98 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %99 = load float*, float** %98, align 8
  %100 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %101 = load i32, i32* %100, align 4
  %102 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %103 = load i32, i32* %102, align 4
  %104 = mul i32 0, %101
  %105 = add i32 %104, %36
  %106 = mul i32 %105, %103
  %107 = add i32 %106, %97
  %108 = getelementptr float, float* %99, i32 %107
  %109 = load float, float* %108, align 4
  %110 = fmul reassoc ninf nsz float %109, 4.000000e+00
  %111 = fadd reassoc ninf nsz float %94, %110
  %112 = add i32 %27, 2
  %113 = call i32 @max_i32(i32 0, i32 %112)
  %114 = call i32 @min_i32(i32 %43, i32 %113)
  %115 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %116 = load float*, float** %115, align 8
  %117 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %118 = load i32, i32* %117, align 4
  %119 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %120 = load i32, i32* %119, align 4
  %121 = mul i32 0, %118
  %122 = add i32 %121, %36
  %123 = mul i32 %122, %120
  %124 = add i32 %123, %114
  %125 = getelementptr float, float* %116, i32 %124
  %126 = load float, float* %125, align 4
  %127 = fadd reassoc ninf nsz float %111, %126
  %128 = add i32 %26, -1
  %129 = call i32 @max_i32(i32 0, i32 %128)
  %130 = call i32 @min_i32(i32 %34, i32 %129)
  %131 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %132 = load float*, float** %131, align 8
  %133 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %134 = load i32, i32* %133, align 4
  %135 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %136 = load i32, i32* %135, align 4
  %137 = mul i32 0, %134
  %138 = add i32 %137, %130
  %139 = mul i32 %138, %136
  %140 = add i32 %139, %45
  %141 = getelementptr float, float* %132, i32 %140
  %142 = load float, float* %141, align 4
  %143 = fmul reassoc ninf nsz float %142, 4.000000e+00
  %144 = fadd reassoc ninf nsz float %127, %143
  %145 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %146 = load float*, float** %145, align 8
  %147 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %148 = load i32, i32* %147, align 4
  %149 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %150 = load i32, i32* %149, align 4
  %151 = mul i32 0, %148
  %152 = add i32 %151, %130
  %153 = mul i32 %152, %150
  %154 = add i32 %153, %64
  %155 = getelementptr float, float* %146, i32 %154
  %156 = load float, float* %155, align 4
  %157 = fmul reassoc ninf nsz float %156, 1.600000e+01
  %158 = fadd reassoc ninf nsz float %144, %157
  %159 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %160 = load float*, float** %159, align 8
  %161 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %162 = load i32, i32* %161, align 4
  %163 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %164 = load i32, i32* %163, align 4
  %165 = mul i32 0, %162
  %166 = add i32 %165, %130
  %167 = mul i32 %166, %164
  %168 = add i32 %167, %80
  %169 = getelementptr float, float* %160, i32 %168
  %170 = load float, float* %169, align 4
  %171 = fmul reassoc ninf nsz float %170, 2.400000e+01
  %172 = fadd reassoc ninf nsz float %158, %171
  %173 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %174 = load float*, float** %173, align 8
  %175 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %176 = load i32, i32* %175, align 4
  %177 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %178 = load i32, i32* %177, align 4
  %179 = mul i32 0, %176
  %180 = add i32 %179, %130
  %181 = mul i32 %180, %178
  %182 = add i32 %181, %97
  %183 = getelementptr float, float* %174, i32 %182
  %184 = load float, float* %183, align 4
  %185 = fmul reassoc ninf nsz float %184, 1.600000e+01
  %186 = fadd reassoc ninf nsz float %172, %185
  %187 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %188 = load float*, float** %187, align 8
  %189 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %190 = load i32, i32* %189, align 4
  %191 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %192 = load i32, i32* %191, align 4
  %193 = mul i32 0, %190
  %194 = add i32 %193, %130
  %195 = mul i32 %194, %192
  %196 = add i32 %195, %114
  %197 = getelementptr float, float* %188, i32 %196
  %198 = load float, float* %197, align 4
  %199 = fmul reassoc ninf nsz float %198, 4.000000e+00
  %200 = fadd reassoc ninf nsz float %186, %199
  %201 = call i32 @max_i32(i32 0, i32 %26)
  %202 = call i32 @min_i32(i32 %34, i32 %201)
  %203 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %204 = load float*, float** %203, align 8
  %205 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %206 = load i32, i32* %205, align 4
  %207 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %208 = load i32, i32* %207, align 4
  %209 = mul i32 0, %206
  %210 = add i32 %209, %202
  %211 = mul i32 %210, %208
  %212 = add i32 %211, %45
  %213 = getelementptr float, float* %204, i32 %212
  %214 = load float, float* %213, align 4
  %215 = fmul reassoc ninf nsz float %214, 6.000000e+00
  %216 = fadd reassoc ninf nsz float %200, %215
  %217 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %218 = load float*, float** %217, align 8
  %219 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %220 = load i32, i32* %219, align 4
  %221 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %222 = load i32, i32* %221, align 4
  %223 = mul i32 0, %220
  %224 = add i32 %223, %202
  %225 = mul i32 %224, %222
  %226 = add i32 %225, %64
  %227 = getelementptr float, float* %218, i32 %226
  %228 = load float, float* %227, align 4
  %229 = fmul reassoc ninf nsz float %228, 2.400000e+01
  %230 = fadd reassoc ninf nsz float %216, %229
  %231 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %232 = load float*, float** %231, align 8
  %233 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %234 = load i32, i32* %233, align 4
  %235 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %236 = load i32, i32* %235, align 4
  %237 = mul i32 0, %234
  %238 = add i32 %237, %202
  %239 = mul i32 %238, %236
  %240 = add i32 %239, %80
  %241 = getelementptr float, float* %232, i32 %240
  %242 = load float, float* %241, align 4
  %243 = fmul reassoc ninf nsz float %242, 3.600000e+01
  %244 = fadd reassoc ninf nsz float %230, %243
  %245 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %246 = load float*, float** %245, align 8
  %247 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %248 = load i32, i32* %247, align 4
  %249 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %250 = load i32, i32* %249, align 4
  %251 = mul i32 0, %248
  %252 = add i32 %251, %202
  %253 = mul i32 %252, %250
  %254 = add i32 %253, %97
  %255 = getelementptr float, float* %246, i32 %254
  %256 = load float, float* %255, align 4
  %257 = fmul reassoc ninf nsz float %256, 2.400000e+01
  %258 = fadd reassoc ninf nsz float %244, %257
  %259 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %260 = load float*, float** %259, align 8
  %261 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %262 = load i32, i32* %261, align 4
  %263 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %264 = load i32, i32* %263, align 4
  %265 = mul i32 0, %262
  %266 = add i32 %265, %202
  %267 = mul i32 %266, %264
  %268 = add i32 %267, %114
  %269 = getelementptr float, float* %260, i32 %268
  %270 = load float, float* %269, align 4
  %271 = fmul reassoc ninf nsz float %270, 6.000000e+00
  %272 = fadd reassoc ninf nsz float %258, %271
  %273 = add i32 %26, 1
  %274 = call i32 @max_i32(i32 0, i32 %273)
  %275 = call i32 @min_i32(i32 %34, i32 %274)
  %276 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %277 = load float*, float** %276, align 8
  %278 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %279 = load i32, i32* %278, align 4
  %280 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %281 = load i32, i32* %280, align 4
  %282 = mul i32 0, %279
  %283 = add i32 %282, %275
  %284 = mul i32 %283, %281
  %285 = add i32 %284, %45
  %286 = getelementptr float, float* %277, i32 %285
  %287 = load float, float* %286, align 4
  %288 = fmul reassoc ninf nsz float %287, 4.000000e+00
  %289 = fadd reassoc ninf nsz float %272, %288
  %290 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %291 = load float*, float** %290, align 8
  %292 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %293 = load i32, i32* %292, align 4
  %294 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %295 = load i32, i32* %294, align 4
  %296 = mul i32 0, %293
  %297 = add i32 %296, %275
  %298 = mul i32 %297, %295
  %299 = add i32 %298, %64
  %300 = getelementptr float, float* %291, i32 %299
  %301 = load float, float* %300, align 4
  %302 = fmul reassoc ninf nsz float %301, 1.600000e+01
  %303 = fadd reassoc ninf nsz float %289, %302
  %304 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %305 = load float*, float** %304, align 8
  %306 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %307 = load i32, i32* %306, align 4
  %308 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %309 = load i32, i32* %308, align 4
  %310 = mul i32 0, %307
  %311 = add i32 %310, %275
  %312 = mul i32 %311, %309
  %313 = add i32 %312, %80
  %314 = getelementptr float, float* %305, i32 %313
  %315 = load float, float* %314, align 4
  %316 = fmul reassoc ninf nsz float %315, 2.400000e+01
  %317 = fadd reassoc ninf nsz float %303, %316
  %318 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %319 = load float*, float** %318, align 8
  %320 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %321 = load i32, i32* %320, align 4
  %322 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %323 = load i32, i32* %322, align 4
  %324 = mul i32 0, %321
  %325 = add i32 %324, %275
  %326 = mul i32 %325, %323
  %327 = add i32 %326, %97
  %328 = getelementptr float, float* %319, i32 %327
  %329 = load float, float* %328, align 4
  %330 = fmul reassoc ninf nsz float %329, 1.600000e+01
  %331 = fadd reassoc ninf nsz float %317, %330
  %332 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %333 = load float*, float** %332, align 8
  %334 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %335 = load i32, i32* %334, align 4
  %336 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %337 = load i32, i32* %336, align 4
  %338 = mul i32 0, %335
  %339 = add i32 %338, %275
  %340 = mul i32 %339, %337
  %341 = add i32 %340, %114
  %342 = getelementptr float, float* %333, i32 %341
  %343 = load float, float* %342, align 4
  %344 = fmul reassoc ninf nsz float %343, 4.000000e+00
  %345 = fadd reassoc ninf nsz float %331, %344
  %346 = add i32 %26, 2
  %347 = call i32 @max_i32(i32 0, i32 %346)
  %348 = call i32 @min_i32(i32 %34, i32 %347)
  %349 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %350 = load float*, float** %349, align 8
  %351 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %352 = load i32, i32* %351, align 4
  %353 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %354 = load i32, i32* %353, align 4
  %355 = mul i32 0, %352
  %356 = add i32 %355, %348
  %357 = mul i32 %356, %354
  %358 = add i32 %357, %45
  %359 = getelementptr float, float* %350, i32 %358
  %360 = load float, float* %359, align 4
  %361 = fadd reassoc ninf nsz float %345, %360
  %362 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %363 = load float*, float** %362, align 8
  %364 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %365 = load i32, i32* %364, align 4
  %366 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %367 = load i32, i32* %366, align 4
  %368 = mul i32 0, %365
  %369 = add i32 %368, %348
  %370 = mul i32 %369, %367
  %371 = add i32 %370, %64
  %372 = getelementptr float, float* %363, i32 %371
  %373 = load float, float* %372, align 4
  %374 = fmul reassoc ninf nsz float %373, 4.000000e+00
  %375 = fadd reassoc ninf nsz float %361, %374
  %376 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %377 = load float*, float** %376, align 8
  %378 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %379 = load i32, i32* %378, align 4
  %380 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %381 = load i32, i32* %380, align 4
  %382 = mul i32 0, %379
  %383 = add i32 %382, %348
  %384 = mul i32 %383, %381
  %385 = add i32 %384, %80
  %386 = getelementptr float, float* %377, i32 %385
  %387 = load float, float* %386, align 4
  %388 = fmul reassoc ninf nsz float %387, 6.000000e+00
  %389 = fadd reassoc ninf nsz float %375, %388
  %390 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %391 = load float*, float** %390, align 8
  %392 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %393 = load i32, i32* %392, align 4
  %394 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %395 = load i32, i32* %394, align 4
  %396 = mul i32 0, %393
  %397 = add i32 %396, %348
  %398 = mul i32 %397, %395
  %399 = add i32 %398, %97
  %400 = getelementptr float, float* %391, i32 %399
  %401 = load float, float* %400, align 4
  %402 = fmul reassoc ninf nsz float %401, 4.000000e+00
  %403 = fadd reassoc ninf nsz float %389, %402
  %404 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 1
  %405 = load float*, float** %404, align 8
  %406 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 0
  %407 = load i32, i32* %406, align 4
  %408 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %49, i32 0, i32 0, i32 1
  %409 = load i32, i32* %408, align 4
  %410 = mul i32 0, %407
  %411 = add i32 %410, %348
  %412 = mul i32 %411, %409
  %413 = add i32 %412, %114
  %414 = getelementptr float, float* %405, i32 %413
  %415 = load float, float* %414, align 4
  %416 = fadd reassoc ninf nsz float %403, %415
  %417 = fmul reassoc ninf nsz float %416, 3.906250e-03
  %418 = getelementptr %struct.RuntimeContext.25, %struct.RuntimeContext.25* %0, i32 0, i32 0
  %419 = bitcast i8** %418 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %420 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %419, align 8
  %421 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %420, i32 0, i32 1
  %422 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %421, i32 0, i32 1
  %423 = load float*, float** %422, align 8
  %424 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %421, i32 0, i32 0, i32 0
  %425 = load i32, i32* %424, align 4
  %426 = getelementptr { { i32, i32 }, float* }, { { i32, i32 }, float* }* %421, i32 0, i32 0, i32 1
  %427 = load i32, i32* %426, align 4
  %428 = mul i32 0, %425
  %429 = add i32 %428, %23
  %430 = mul i32 %429, %427
  %431 = add i32 %430, %25
  %432 = getelementptr float, float* %423, i32 %431
  store float %417, float* %432, align 4
  br label %final
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @min_i32(i32 noundef %0, i32 noundef %1) #0 {
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
define internal i32 @max_i32(i32 noundef %0, i32 noundef %1) #0 {
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
define internal %struct.LLVMRuntime.24* @RuntimeContext_get_runtime(%struct.RuntimeContext.25* noundef %0) #0 {
  %2 = alloca %struct.RuntimeContext.25*, align 8
  store %struct.RuntimeContext.25* %0, %struct.RuntimeContext.25** %2, align 8
  %3 = load %struct.RuntimeContext.25*, %struct.RuntimeContext.25** %2, align 8
  %4 = getelementptr inbounds %struct.RuntimeContext.25, %struct.RuntimeContext.25* %3, i32 0, i32 1
  %5 = load %struct.LLVMRuntime.24*, %struct.LLVMRuntime.24** %4, align 8
  ret %struct.LLVMRuntime.24* %5
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i8* @get_temporary_pointer(%struct.LLVMRuntime.24* noundef %0, i64 noundef %1) #0 {
  %3 = alloca i64, align 8
  %4 = alloca %struct.LLVMRuntime.24*, align 8
  store i64 %1, i64* %3, align 8
  store %struct.LLVMRuntime.24* %0, %struct.LLVMRuntime.24** %4, align 8
  %5 = load %struct.LLVMRuntime.24*, %struct.LLVMRuntime.24** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.24, %struct.LLVMRuntime.24* %5, i32 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = load i64, i64* %3, align 8
  %9 = getelementptr inbounds i8, i8* %7, i64 %8
  ret i8* %9
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @gpu_parallel_range_for(%struct.RuntimeContext.25* noundef %0, i32 noundef %1, i32 noundef %2, void (%struct.RuntimeContext.25*, i8*)* noundef %3, void (%struct.RuntimeContext.25*, i8*, i32)* noundef %4, void (%struct.RuntimeContext.25*, i8*)* noundef %5, i64 noundef %6) #0 {
  %8 = alloca i64, align 8
  %9 = alloca void (%struct.RuntimeContext.25*, i8*)*, align 8
  %10 = alloca void (%struct.RuntimeContext.25*, i8*, i32)*, align 8
  %11 = alloca void (%struct.RuntimeContext.25*, i8*)*, align 8
  %12 = alloca i32, align 4
  %13 = alloca i32, align 4
  %14 = alloca %struct.RuntimeContext.25*, align 8
  %15 = alloca i32, align 4
  %16 = alloca i8*, align 8
  %17 = alloca i64, align 8
  %18 = alloca i8*, align 8
  store i64 %6, i64* %8, align 8
  store void (%struct.RuntimeContext.25*, i8*)* %5, void (%struct.RuntimeContext.25*, i8*)** %9, align 8
  store void (%struct.RuntimeContext.25*, i8*, i32)* %4, void (%struct.RuntimeContext.25*, i8*, i32)** %10, align 8
  store void (%struct.RuntimeContext.25*, i8*)* %3, void (%struct.RuntimeContext.25*, i8*)** %11, align 8
  store i32 %2, i32* %12, align 4
  store i32 %1, i32* %13, align 4
  store %struct.RuntimeContext.25* %0, %struct.RuntimeContext.25** %14, align 8
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
  %30 = load void (%struct.RuntimeContext.25*, i8*)*, void (%struct.RuntimeContext.25*, i8*)** %11, align 8
  %31 = icmp ne void (%struct.RuntimeContext.25*, i8*)* %30, null
  br i1 %31, label %32, label %36

32:                                               ; preds = %7
  %33 = load void (%struct.RuntimeContext.25*, i8*)*, void (%struct.RuntimeContext.25*, i8*)** %11, align 8
  %34 = load i8*, i8** %18, align 8
  %35 = load %struct.RuntimeContext.25*, %struct.RuntimeContext.25** %14, align 8
  call void %33(%struct.RuntimeContext.25* noundef %35, i8* noundef %34)
  br label %36

36:                                               ; preds = %32, %7
  br label %37

37:                                               ; preds = %41, %36
  %38 = load i32, i32* %15, align 4
  %39 = load i32, i32* %12, align 4
  %40 = icmp slt i32 %38, %39
  br i1 %40, label %41, label %51

41:                                               ; preds = %37
  %42 = load void (%struct.RuntimeContext.25*, i8*, i32)*, void (%struct.RuntimeContext.25*, i8*, i32)** %10, align 8
  %43 = load i32, i32* %15, align 4
  %44 = load i8*, i8** %18, align 8
  %45 = load %struct.RuntimeContext.25*, %struct.RuntimeContext.25** %14, align 8
  call void %42(%struct.RuntimeContext.25* noundef %45, i8* noundef %44, i32 noundef %43)
  %46 = call i32 @block_dim()
  %47 = call i32 @grid_dim()
  %48 = mul nsw i32 %46, %47
  %49 = load i32, i32* %15, align 4
  %50 = add nsw i32 %49, %48
  store i32 %50, i32* %15, align 4
  br label %37, !llvm.loop !20

51:                                               ; preds = %37
  %52 = load void (%struct.RuntimeContext.25*, i8*)*, void (%struct.RuntimeContext.25*, i8*)** %9, align 8
  %53 = icmp ne void (%struct.RuntimeContext.25*, i8*)* %52, null
  br i1 %53, label %54, label %58

54:                                               ; preds = %51
  %55 = load void (%struct.RuntimeContext.25*, i8*)*, void (%struct.RuntimeContext.25*, i8*)** %9, align 8
  %56 = load i8*, i8** %18, align 8
  %57 = load %struct.RuntimeContext.25*, %struct.RuntimeContext.25** %14, align 8
  call void %55(%struct.RuntimeContext.25* noundef %57, i8* noundef %56)
  br label %58

58:                                               ; preds = %54, %51
  %59 = load i8*, i8** %16, align 8
  call void @llvm.stackrestore(i8* %59)
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @thread_idx() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.tid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_dim() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ntid.x()
  ret i32 %0
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @block_idx() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.ctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare i8* @llvm.stacksave() #1

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal i32 @grid_dim() #0 {
entry:
  %0 = call i32 @llvm.nvvm.read.ptx.sreg.nctaid.x()
  ret i32 %0
}

; Function Attrs: nocallback nofree nosync nounwind willreturn
declare void @llvm.stackrestore(i8*) #1

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.nctaid.x() #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ctaid.x() #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.ntid.x() #2

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.nvvm.read.ptx.sreg.tid.x() #2

attributes #0 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind willreturn }
attributes #2 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

!nvvm.annotations = !{!0, !1, !2, !3, !4, !5, !6, !7, !6, !8, !8, !8, !8, !9, !9, !8}
!llvm.linker.options = !{!10, !11, !12, !13, !14}
!llvm.ident = !{!15}
!nvvmir.version = !{!16}
!llvm.module.flags = !{!17, !18, !19}

!0 = !{void (%struct.RuntimeContext.25*)* @_downsample_2x_kernel_c152_0_kernel_0_serial, !"kernel", i32 1}
!1 = !{void (%struct.RuntimeContext.25*)* @_downsample_2x_kernel_c152_0_kernel_0_serial, !"maxntidx", i32 1}
!2 = !{void (%struct.RuntimeContext.25*)* @_downsample_2x_kernel_c152_0_kernel_0_serial, !"minctasm", i32 2}
!3 = !{void (%struct.RuntimeContext.25*)* @_downsample_2x_kernel_c152_0_kernel_1_range_for, !"kernel", i32 1}
!4 = !{void (%struct.RuntimeContext.25*)* @_downsample_2x_kernel_c152_0_kernel_1_range_for, !"maxntidx", i32 128}
!5 = !{void (%struct.RuntimeContext.25*)* @_downsample_2x_kernel_c152_0_kernel_1_range_for, !"minctasm", i32 2}
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
