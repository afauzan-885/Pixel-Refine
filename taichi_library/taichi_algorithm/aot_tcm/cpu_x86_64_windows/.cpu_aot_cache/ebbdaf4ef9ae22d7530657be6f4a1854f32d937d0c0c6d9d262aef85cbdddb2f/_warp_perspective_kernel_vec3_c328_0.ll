; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.168*, void (%struct.RuntimeContext.168*, i8*)*, void (%struct.RuntimeContext.168*, i8*, i32)*, void (%struct.RuntimeContext.168*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.168 = type { i8*, %struct.LLVMRuntime.167*, i32, i64* }
%struct.LLVMRuntime.167 = type { %struct.PreallocatedMemoryChunk.163, %struct.PreallocatedMemoryChunk.163, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.164*], [1024 x %struct.NodeManager.165*], [1024 x i8*], i8*, %struct.RandState.166*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.163 = type { i8*, i8*, i64 }
%struct.ListManager.164 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.167* }
%struct.NodeManager.165 = type { %struct.LLVMRuntime.167*, i32, i32, i32, i32, %struct.ListManager.164*, %struct.ListManager.164*, %struct.ListManager.164*, i32 }
%struct.RandState.166 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_warp_perspective_kernel_vec3_c328_0_kernel_0_serial(%struct.RuntimeContext.168* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.168* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 5
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 6
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.168, %struct.RuntimeContext.168* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.167*, %struct.LLVMRuntime.167** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.167, %struct.LLVMRuntime.167* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.167*, %struct.LLVMRuntime.167** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.167, %struct.LLVMRuntime.167* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_warp_perspective_kernel_vec3_c328_0_kernel_1_range_for(%struct.RuntimeContext.168* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.168* %context, %struct.RuntimeContext.168** %4, align 8
  store void (%struct.RuntimeContext.168*, i8*)* null, void (%struct.RuntimeContext.168*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.168*, i8*, i32)* @function_body, void (%struct.RuntimeContext.168*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.168*, i8*)* null, void (%struct.RuntimeContext.168*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.168, %struct.RuntimeContext.168* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.167*, %struct.LLVMRuntime.167** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.167, %struct.LLVMRuntime.167* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.167, %struct.LLVMRuntime.167* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.168* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.168, %struct.RuntimeContext.168* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.167*, %struct.LLVMRuntime.167** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.167, %struct.LLVMRuntime.167* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.168* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %27 = load float*, float** %26, align 8
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %29 = load i32, i32* %28, align 4
  %30 = getelementptr float, float* %27, i64 1
  %31 = getelementptr float, float* %27, i64 2
  %32 = sext i32 %29 to i64
  %33 = getelementptr float, float* %27, i64 %32
  %34 = add i32 %29, 1
  %35 = sext i32 %34 to i64
  %36 = getelementptr float, float* %27, i64 %35
  %37 = add i32 %29, 2
  %38 = sext i32 %37 to i64
  %39 = getelementptr float, float* %27, i64 %38
  %40 = shl i32 %29, 1
  %41 = sext i32 %40 to i64
  %42 = getelementptr float, float* %27, i64 %41
  %43 = getelementptr float, float* %42, i64 1
  %44 = add i32 %40, 2
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, float* %27, i64 %45
  %47 = add i32 %25, -1
  %48 = add i32 %23, -1
  %49 = icmp slt i32 %17, %19
  br i1 %49, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %50 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %51 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %52 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %53 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %54 = mul i32 %17, 3
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %54, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.09 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %244, %for_loop_body ]
  %55 = load %struct.LLVMRuntime.167*, %struct.LLVMRuntime.167** %3, align 8
  %56 = getelementptr inbounds %struct.LLVMRuntime.167, %struct.LLVMRuntime.167* %55, i64 0, i32 14
  %57 = load i8*, i8** %56, align 8
  %58 = getelementptr inbounds i8, i8* %57, i64 4
  %59 = bitcast i8* %58 to i32*
  %60 = load i32, i32* %59, align 4
  %61 = sdiv i32 %.09, %60
  %62 = mul i32 %61, %60
  %63 = xor i32 %60, %.09
  %64 = icmp slt i32 %63, 0
  %65 = icmp ne i32 %.09, 0
  %66 = icmp ne i32 %.09, %62
  %67 = and i1 %65, %64
  %68 = and i1 %67, %66
  %.neg4 = sext i1 %68 to i32
  %69 = add i32 %61, %.neg4
  %70 = mul i32 %60, -1
  %71 = mul i32 %70, %69
  %72 = add i32 %.09, %71
  %73 = load float, float* %27, align 4
  %74 = sitofp i32 %72 to float
  %75 = fmul reassoc ninf nsz float %73, %74
  %76 = load float, float* %30, align 4
  %77 = sitofp i32 %69 to float
  %78 = fmul reassoc ninf nsz float %76, %77
  %79 = load float, float* %31, align 4
  %80 = fadd reassoc ninf nsz float %78, %79
  %81 = fadd reassoc ninf nsz float %80, %75
  %82 = load float, float* %33, align 4
  %83 = fmul reassoc ninf nsz float %82, %74
  %84 = load float, float* %36, align 4
  %85 = fmul reassoc ninf nsz float %84, %77
  %86 = load float, float* %39, align 4
  %87 = fadd reassoc ninf nsz float %85, %86
  %88 = fadd reassoc ninf nsz float %87, %83
  %89 = load float, float* %42, align 4
  %90 = fmul reassoc ninf nsz float %89, %74
  %91 = load float, float* %43, align 4
  %92 = fmul reassoc ninf nsz float %91, %77
  %93 = load float, float* %46, align 4
  %94 = fadd reassoc ninf nsz float %92, 0x3E112E0BE0000000
  %95 = fadd reassoc ninf nsz float %94, %90
  %96 = fadd reassoc ninf nsz float %95, %93
  %97 = fdiv reassoc ninf nsz float %81, %96
  %98 = fdiv reassoc ninf nsz float %88, %96
  %99 = tail call reassoc ninf nsz float @llvm.floor.f32(float %97)
  %100 = fptosi float %99 to i32
  %101 = tail call reassoc ninf nsz float @llvm.floor.f32(float %98)
  %102 = fptosi float %101 to i32
  %103 = sitofp i32 %100 to float
  %104 = fsub reassoc ninf nsz float %97, %103
  %105 = sitofp i32 %102 to float
  %106 = fsub reassoc ninf nsz float %98, %105
  %107 = tail call i32 @llvm.abs.i32(i32 %100, i1 true)
  %108 = sub i32 %107, %47
  %109 = tail call i32 @llvm.smax.i32(i32 %108, i32 0)
  %.neg5 = mul i32 %109, -2
  %110 = add i32 %.neg5, %107
  %111 = tail call i32 @llvm.smax.i32(i32 %110, i32 0)
  %112 = tail call i32 @llvm.smin.i32(i32 %47, i32 %111)
  %113 = tail call i32 @llvm.abs.i32(i32 %102, i1 true)
  %114 = sub i32 %113, %48
  %115 = tail call i32 @llvm.smax.i32(i32 %114, i32 0)
  %.neg6 = mul i32 %115, -2
  %116 = add i32 %.neg6, %113
  %117 = tail call i32 @llvm.smax.i32(i32 %116, i32 0)
  %118 = tail call i32 @llvm.smin.i32(i32 %48, i32 %117)
  %119 = add i32 %100, 1
  %120 = tail call i32 @llvm.abs.i32(i32 %119, i1 true)
  %121 = sub i32 %120, %47
  %122 = tail call i32 @llvm.smax.i32(i32 %121, i32 0)
  %.neg7 = mul i32 %122, -2
  %123 = add i32 %.neg7, %120
  %124 = tail call i32 @llvm.smax.i32(i32 %123, i32 0)
  %125 = tail call i32 @llvm.smin.i32(i32 %47, i32 %124)
  %126 = add i32 %102, 1
  %127 = tail call i32 @llvm.abs.i32(i32 %126, i1 true)
  %128 = sub i32 %127, %48
  %129 = tail call i32 @llvm.smax.i32(i32 %128, i32 0)
  %.neg8 = mul i32 %129, -2
  %130 = add i32 %.neg8, %127
  %131 = tail call i32 @llvm.smax.i32(i32 %130, i32 0)
  %132 = tail call i32 @llvm.smin.i32(i32 %48, i32 %131)
  %133 = load float*, float** %50, align 8
  %134 = load i32, i32* %51, align 4
  %135 = mul i32 %118, %134
  %136 = add i32 %135, %112
  %137 = mul i32 %136, 3
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %133, i64 %138
  %140 = load float, float* %139, align 4
  %141 = add i32 %137, 1
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, float* %133, i64 %142
  %144 = load float, float* %143, align 4
  %145 = add i32 %137, 2
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, float* %133, i64 %146
  %148 = load float, float* %147, align 4
  %149 = add i32 %135, %125
  %150 = mul i32 %149, 3
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %133, i64 %151
  %153 = load float, float* %152, align 4
  %154 = add i32 %150, 1
  %155 = sext i32 %154 to i64
  %156 = getelementptr float, float* %133, i64 %155
  %157 = load float, float* %156, align 4
  %158 = add i32 %150, 2
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %133, i64 %159
  %161 = load float, float* %160, align 4
  %162 = mul i32 %132, %134
  %163 = add i32 %162, %112
  %164 = mul i32 %163, 3
  %165 = sext i32 %164 to i64
  %166 = getelementptr float, float* %133, i64 %165
  %167 = load float, float* %166, align 4
  %168 = add i32 %164, 1
  %169 = sext i32 %168 to i64
  %170 = getelementptr float, float* %133, i64 %169
  %171 = load float, float* %170, align 4
  %172 = add i32 %164, 2
  %173 = sext i32 %172 to i64
  %174 = getelementptr float, float* %133, i64 %173
  %175 = load float, float* %174, align 4
  %176 = add i32 %162, %125
  %177 = mul i32 %176, 3
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %133, i64 %178
  %180 = load float, float* %179, align 4
  %181 = add i32 %177, 1
  %182 = sext i32 %181 to i64
  %183 = getelementptr float, float* %133, i64 %182
  %184 = load float, float* %183, align 4
  %185 = add i32 %177, 2
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %133, i64 %186
  %188 = load float, float* %187, align 4
  %189 = fsub reassoc ninf nsz float 1.000000e+00, %104
  %190 = fmul reassoc ninf nsz float %189, %140
  %191 = fmul reassoc ninf nsz float %189, %144
  %192 = fmul reassoc ninf nsz float %189, %148
  %193 = fmul reassoc ninf nsz float %104, %153
  %194 = fmul reassoc ninf nsz float %104, %157
  %195 = fmul reassoc ninf nsz float %161, %104
  %196 = fadd reassoc ninf nsz float %190, %193
  %197 = fadd reassoc ninf nsz float %191, %194
  %198 = fadd reassoc ninf nsz float %192, %195
  %199 = fmul reassoc ninf nsz float %167, %189
  %200 = fmul reassoc ninf nsz float %171, %189
  %201 = fmul reassoc ninf nsz float %175, %189
  %202 = fmul reassoc ninf nsz float %180, %104
  %203 = fmul reassoc ninf nsz float %184, %104
  %204 = fmul reassoc ninf nsz float %188, %104
  %205 = fadd reassoc ninf nsz float %202, %199
  %206 = fadd reassoc ninf nsz float %203, %200
  %207 = fadd reassoc ninf nsz float %204, %201
  %208 = fsub reassoc ninf nsz float 1.000000e+00, %106
  %209 = fmul reassoc ninf nsz float %196, %208
  %210 = fmul reassoc ninf nsz float %197, %208
  %211 = fmul reassoc ninf nsz float %198, %208
  %212 = fmul reassoc ninf nsz float %205, %106
  %213 = fmul reassoc ninf nsz float %206, %106
  %214 = fmul reassoc ninf nsz float %207, %106
  %215 = fadd reassoc ninf nsz float %212, %209
  %216 = fadd reassoc ninf nsz float %213, %210
  %217 = fadd reassoc ninf nsz float %214, %211
  %218 = load float*, float** %52, align 8
  %219 = load i32, i32* %53, align 4
  %220 = sub i32 %219, %60
  %221 = mul i32 %220, 3
  %222 = mul i32 %221, %69
  %223 = add i32 %lsr.iv, %222
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %218, i64 %224
  store float %215, float* %225, align 4
  %226 = load float*, float** %52, align 8
  %227 = load i32, i32* %53, align 4
  %228 = sub i32 %227, %60
  %229 = mul i32 %228, 3
  %230 = mul i32 %229, %69
  %231 = add i32 %lsr.iv, %230
  %232 = add i32 %231, 1
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, float* %226, i64 %233
  store float %216, float* %234, align 4
  %235 = load float*, float** %52, align 8
  %236 = load i32, i32* %53, align 4
  %237 = sub i32 %236, %60
  %238 = mul i32 %237, 3
  %239 = mul i32 %238, %69
  %240 = add i32 %lsr.iv, %239
  %241 = add i32 %240, 2
  %242 = sext i32 %241 to i64
  %243 = getelementptr float, float* %235, i64 %242
  store float %217, float* %243, align 4
  %244 = add nsw i32 %.09, 1
  %lsr.iv.next = add i32 %lsr.iv, 3
  %exitcond.not = icmp eq i32 %19, %244
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
  %4 = alloca %struct.RuntimeContext.168, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.168**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.168*, %struct.RuntimeContext.168** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.168*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.168*, i8*)*, void (%struct.RuntimeContext.168*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.168*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.168*, i8*, i32)*, void (%struct.RuntimeContext.168*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.168*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.168*, i8*)*, void (%struct.RuntimeContext.168*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.168*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.168* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.168* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.168* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.168, %struct.RuntimeContext.168* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.168* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.168* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.168*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.168* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
