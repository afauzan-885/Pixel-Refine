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
define void @_sobel_kernel_vec3_c200_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 4
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
define void @_sobel_kernel_vec3_c200_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %20 = icmp slt i32 %17, %19
  br i1 %20, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %21 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %21, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 1, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2, i32 1
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 2, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %.064 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %227, %for_loop_body ]
  %29 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %30 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %29, i64 0, i32 14
  %31 = load i8*, i8** %30, align 8
  %32 = getelementptr inbounds i8, i8* %31, i64 4
  %33 = bitcast i8* %32 to i32*
  %34 = load i32, i32* %33, align 4
  %35 = sdiv i32 %.064, %34
  %36 = mul i32 %35, %34
  %37 = xor i32 %34, %.064
  %38 = icmp slt i32 %37, 0
  %39 = icmp ne i32 %.064, 0
  %40 = icmp ne i32 %.064, %36
  %41 = and i1 %39, %38
  %42 = and i1 %41, %40
  %.neg4 = sext i1 %42 to i32
  %43 = add i32 %35, %.neg4
  %44 = mul i32 %43, %34
  %45 = add i32 %43, -1
  %46 = getelementptr inbounds i8, i8* %31, i64 8
  %47 = bitcast i8* %46 to i32*
  %48 = load i32, i32* %47, align 4
  %49 = add i32 %48, -1
  %50 = mul i32 %34, -1
  %51 = mul i32 %50, %43
  %52 = add i32 %.064, %51
  %53 = add i32 %52, -1
  %54 = getelementptr inbounds i8, i8* %31, i64 12
  %55 = bitcast i8* %54 to i32*
  %56 = load i32, i32* %55, align 4
  %57 = add i32 %56, -1
  %58 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %59 = tail call i32 @llvm.smin.i32(i32 %49, i32 %58)
  %60 = tail call i32 @llvm.smax.i32(i32 %53, i32 0)
  %61 = tail call i32 @llvm.smin.i32(i32 %57, i32 %60)
  %62 = load float*, float** %23, align 8
  %63 = load i32, i32* %24, align 4
  %64 = mul i32 %59, %63
  %65 = add i32 %61, %64
  %66 = mul i32 %65, 3
  %67 = sext i32 %66 to i64
  %68 = getelementptr float, float* %62, i64 %67
  %69 = load float, float* %68, align 4
  %70 = add i32 %66, 1
  %71 = sext i32 %70 to i64
  %72 = getelementptr float, float* %62, i64 %71
  %73 = load float, float* %72, align 4
  %74 = add i32 %66, 2
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, float* %62, i64 %75
  %77 = load float, float* %76, align 4
  %78 = sub i32 %64, %44
  %79 = add i32 %.064, %78
  %80 = mul i32 %79, 3
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %62, i64 %81
  %83 = load float, float* %82, align 4
  %84 = add i32 %80, 1
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, float* %62, i64 %85
  %87 = load float, float* %86, align 4
  %88 = add i32 %80, 2
  %89 = sext i32 %88 to i64
  %90 = getelementptr float, float* %62, i64 %89
  %91 = load float, float* %90, align 4
  %92 = add i32 %52, 1
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = tail call i32 @llvm.smin.i32(i32 %57, i32 %93)
  %95 = add i32 %94, %64
  %96 = mul i32 %95, 3
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, float* %62, i64 %97
  %99 = load float, float* %98, align 4
  %100 = add i32 %96, 1
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %62, i64 %101
  %103 = load float, float* %102, align 4
  %104 = add i32 %96, 2
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, float* %62, i64 %105
  %107 = load float, float* %106, align 4
  %108 = mul i32 %43, %63
  %109 = add i32 %61, %108
  %110 = mul i32 %109, 3
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, float* %62, i64 %111
  %113 = load float, float* %112, align 4
  %114 = add i32 %110, 1
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, float* %62, i64 %115
  %117 = load float, float* %116, align 4
  %118 = add i32 %110, 2
  %119 = sext i32 %118 to i64
  %120 = getelementptr float, float* %62, i64 %119
  %121 = load float, float* %120, align 4
  %122 = add i32 %94, %108
  %123 = mul i32 %122, 3
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %62, i64 %124
  %126 = load float, float* %125, align 4
  %127 = add i32 %123, 1
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, float* %62, i64 %128
  %130 = load float, float* %129, align 4
  %131 = add i32 %123, 2
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, float* %62, i64 %132
  %134 = load float, float* %133, align 4
  %135 = add i32 %43, 1
  %136 = tail call i32 @llvm.smax.i32(i32 %135, i32 0)
  %137 = tail call i32 @llvm.smin.i32(i32 %49, i32 %136)
  %138 = mul i32 %137, %63
  %139 = add i32 %61, %138
  %140 = mul i32 %139, 3
  %141 = sext i32 %140 to i64
  %142 = getelementptr float, float* %62, i64 %141
  %143 = load float, float* %142, align 4
  %144 = add i32 %140, 1
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %62, i64 %145
  %147 = load float, float* %146, align 4
  %148 = add i32 %140, 2
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, float* %62, i64 %149
  %151 = load float, float* %150, align 4
  %152 = sub i32 %138, %44
  %153 = add i32 %.064, %152
  %154 = mul i32 %153, 3
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %62, i64 %155
  %157 = load float, float* %156, align 4
  %158 = add i32 %154, 1
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %62, i64 %159
  %161 = load float, float* %160, align 4
  %162 = add i32 %154, 2
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %62, i64 %163
  %165 = load float, float* %164, align 4
  %166 = add i32 %94, %138
  %167 = mul i32 %166, 3
  %168 = sext i32 %167 to i64
  %169 = getelementptr float, float* %62, i64 %168
  %170 = load float, float* %169, align 4
  %171 = add i32 %167, 1
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %62, i64 %172
  %174 = load float, float* %173, align 4
  %175 = add i32 %167, 2
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, float* %62, i64 %176
  %178 = load float, float* %177, align 4
  %reass.add = fsub reassoc ninf nsz float %126, %113
  %reass.mul = fmul reassoc ninf nsz float %reass.add, 2.000000e+00
  %179 = fadd reassoc ninf nsz float %99, %reass.mul
  %180 = fadd reassoc ninf nsz float %69, %143
  %181 = fsub reassoc ninf nsz float %179, %180
  %182 = fadd reassoc ninf nsz float %181, %170
  %reass.add50 = fsub reassoc ninf nsz float %130, %117
  %reass.mul51 = fmul reassoc ninf nsz float %reass.add50, 2.000000e+00
  %183 = fadd reassoc ninf nsz float %103, %reass.mul51
  %184 = fadd reassoc ninf nsz float %73, %147
  %185 = fsub reassoc ninf nsz float %183, %184
  %186 = fadd reassoc ninf nsz float %185, %174
  %reass.add53 = fsub reassoc ninf nsz float %134, %121
  %reass.mul54 = fmul reassoc ninf nsz float %reass.add53, 2.000000e+00
  %187 = fadd reassoc ninf nsz float %107, %reass.mul54
  %188 = fadd reassoc ninf nsz float %77, %151
  %189 = fsub reassoc ninf nsz float %187, %188
  %190 = fadd reassoc ninf nsz float %189, %178
  %reass.add56 = fsub reassoc ninf nsz float %157, %83
  %reass.mul57 = fmul reassoc ninf nsz float %reass.add56, 2.000000e+00
  %191 = fadd reassoc ninf nsz float %69, %99
  %192 = fsub reassoc ninf nsz float %143, %191
  %193 = fadd reassoc ninf nsz float %192, %reass.mul57
  %194 = fadd reassoc ninf nsz float %193, %170
  %reass.add59 = fsub reassoc ninf nsz float %161, %87
  %reass.mul60 = fmul reassoc ninf nsz float %reass.add59, 2.000000e+00
  %195 = fadd reassoc ninf nsz float %73, %103
  %196 = fsub reassoc ninf nsz float %147, %195
  %197 = fadd reassoc ninf nsz float %196, %reass.mul60
  %198 = fadd reassoc ninf nsz float %197, %174
  %reass.add62 = fsub reassoc ninf nsz float %165, %91
  %reass.mul63 = fmul reassoc ninf nsz float %reass.add62, 2.000000e+00
  %199 = fadd reassoc ninf nsz float %77, %107
  %200 = fsub reassoc ninf nsz float %151, %199
  %201 = fadd reassoc ninf nsz float %200, %reass.mul63
  %202 = fadd reassoc ninf nsz float %201, %178
  %203 = fmul reassoc ninf nsz float %182, 0x3FD322D0E0000000
  %204 = fmul reassoc ninf nsz float %186, 0x3FE2C8B440000000
  %205 = fmul reassoc ninf nsz float %190, 0x3FBD2F1AA0000000
  %206 = fadd reassoc ninf nsz float %204, %203
  %207 = fadd reassoc ninf nsz float %206, %205
  %208 = load float*, float** %25, align 8
  %209 = load i32, i32* %26, align 4
  %210 = sub i32 %209, %34
  %211 = mul i32 %210, %43
  %212 = add i32 %.064, %211
  %213 = sext i32 %212 to i64
  %214 = getelementptr float, float* %208, i64 %213
  store float %207, float* %214, align 4
  %215 = fmul reassoc ninf nsz float %194, 0x3FD322D0E0000000
  %216 = fmul reassoc ninf nsz float %198, 0x3FE2C8B440000000
  %217 = fmul reassoc ninf nsz float %202, 0x3FBD2F1AA0000000
  %218 = fadd reassoc ninf nsz float %216, %215
  %219 = fadd reassoc ninf nsz float %218, %217
  %220 = load float*, float** %27, align 8
  %221 = load i32, i32* %28, align 4
  %222 = sub i32 %221, %34
  %223 = mul i32 %222, %43
  %224 = add i32 %.064, %223
  %225 = sext i32 %224 to i64
  %226 = getelementptr float, float* %220, i64 %225
  store float %219, float* %226, align 4
  %227 = add nsw i32 %.064, 1
  %exitcond.not = icmp eq i32 %19, %227
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_body
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
