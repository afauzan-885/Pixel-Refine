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
define void @_downsample_2x_kernel_3ch_c258_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }** %0, align 8
  %11 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 12
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }** %0, align 8
  %19 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %18, i64 0, i32 1, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %18, i64 0, i32 1, i32 0, i32 1
  %22 = load i32, i32* %21, align 4
  %23 = tail call i32 @llvm.smax.i32(i32 %20, i32 0)
  %24 = tail call i32 @llvm.smax.i32(i32 %22, i32 0)
  %25 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  store i32 %24, i32* %29, align 4
  %30 = mul i32 %24, %23
  %31 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %31, i64 0, i32 14
  %33 = bitcast i8** %32 to i32**
  %34 = load i32*, i32** %33, align 8
  store i32 %30, i32* %34, align 4
  ret void
}

; Function Attrs: nounwind
define void @_downsample_2x_kernel_3ch_c258_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %21 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }**
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }** %21, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %22, i64 0, i32 0, i32 0, i32 2
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %22, i64 0, i32 1, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %22, i64 0, i32 1, i32 0, i32 1
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* } }* %22, i64 0, i32 1, i32 0, i32 2
  %29 = shl i32 %17, 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_body, %for_loop_body.lr.ph
  %lsr.iv = phi i32 [ %29, %for_loop_body.lr.ph ], [ %lsr.iv.next, %for_loop_body ]
  %.073 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %517, %for_loop_body ]
  %30 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %30, i64 0, i32 14
  %32 = load i8*, i8** %31, align 8
  %33 = getelementptr inbounds i8, i8* %32, i64 4
  %34 = bitcast i8* %33 to i32*
  %35 = load i32, i32* %34, align 4
  %36 = sdiv i32 %.073, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.073
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.073, 0
  %41 = icmp ne i32 %.073, %37
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg4 = sext i1 %43 to i32
  %44 = add i32 %36, %.neg4
  %45 = shl i32 %44, 1
  %46 = mul i32 %35, -2
  %47 = mul i32 %46, %44
  %48 = add i32 %lsr.iv, %47
  %49 = add i32 %45, -2
  %50 = tail call i32 @llvm.abs.i32(i32 %49, i1 true)
  %51 = getelementptr inbounds i8, i8* %32, i64 8
  %52 = bitcast i8* %51 to i32*
  %53 = load i32, i32* %52, align 4
  %54 = add i32 %53, -1
  %55 = sub i32 %50, %54
  %56 = tail call i32 @llvm.smax.i32(i32 %55, i32 0)
  %.neg5 = mul i32 %56, -2
  %57 = add i32 %.neg5, %50
  %58 = tail call i32 @llvm.smax.i32(i32 %57, i32 0)
  %59 = tail call i32 @llvm.smin.i32(i32 %54, i32 %58)
  %60 = add i32 %48, -2
  %61 = tail call i32 @llvm.abs.i32(i32 %60, i1 true)
  %62 = getelementptr inbounds i8, i8* %32, i64 12
  %63 = bitcast i8* %62 to i32*
  %64 = load i32, i32* %63, align 4
  %65 = add i32 %64, -1
  %66 = sub i32 %61, %65
  %67 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %.neg6 = mul i32 %67, -2
  %68 = add i32 %.neg6, %61
  %69 = tail call i32 @llvm.smax.i32(i32 %68, i32 0)
  %70 = tail call i32 @llvm.smin.i32(i32 %65, i32 %69)
  %71 = load float*, float** %23, align 8
  %72 = load i32, i32* %24, align 4
  %73 = load i32, i32* %25, align 4
  %74 = mul i32 %59, %72
  %75 = add i32 %70, %74
  %76 = mul i32 %75, %73
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, float* %71, i64 %77
  %79 = load float, float* %78, align 4
  %80 = add i32 %76, 1
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %71, i64 %81
  %83 = load float, float* %82, align 4
  %84 = add i32 %76, 2
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, float* %71, i64 %85
  %87 = load float, float* %86, align 4
  %88 = add i32 %48, -1
  %89 = tail call i32 @llvm.abs.i32(i32 %88, i1 true)
  %90 = sub i32 %89, %65
  %91 = tail call i32 @llvm.smax.i32(i32 %90, i32 0)
  %.neg7 = mul i32 %91, -2
  %92 = add i32 %.neg7, %89
  %93 = tail call i32 @llvm.smax.i32(i32 %92, i32 0)
  %94 = tail call i32 @llvm.smin.i32(i32 %65, i32 %93)
  %95 = add i32 %94, %74
  %96 = mul i32 %95, %73
  %97 = sext i32 %96 to i64
  %98 = getelementptr float, float* %71, i64 %97
  %99 = load float, float* %98, align 4
  %100 = add i32 %96, 1
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %71, i64 %101
  %103 = load float, float* %102, align 4
  %104 = add i32 %96, 2
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, float* %71, i64 %105
  %107 = load float, float* %106, align 4
  %108 = tail call i32 @llvm.abs.i32(i32 %48, i1 true)
  %109 = sub i32 %108, %65
  %110 = tail call i32 @llvm.smax.i32(i32 %109, i32 0)
  %.neg8 = mul i32 %110, -2
  %111 = add i32 %.neg8, %108
  %112 = tail call i32 @llvm.smax.i32(i32 %111, i32 0)
  %113 = tail call i32 @llvm.smin.i32(i32 %65, i32 %112)
  %114 = add i32 %74, %113
  %115 = mul i32 %114, %73
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %71, i64 %116
  %118 = load float, float* %117, align 4
  %119 = add i32 %115, 1
  %120 = sext i32 %119 to i64
  %121 = getelementptr float, float* %71, i64 %120
  %122 = load float, float* %121, align 4
  %123 = add i32 %115, 2
  %124 = sext i32 %123 to i64
  %125 = getelementptr float, float* %71, i64 %124
  %126 = load float, float* %125, align 4
  %127 = add i32 %48, 1
  %128 = tail call i32 @llvm.abs.i32(i32 %127, i1 true)
  %129 = sub i32 %128, %65
  %130 = tail call i32 @llvm.smax.i32(i32 %129, i32 0)
  %.neg9 = mul i32 %130, -2
  %131 = add i32 %.neg9, %128
  %132 = tail call i32 @llvm.smax.i32(i32 %131, i32 0)
  %133 = tail call i32 @llvm.smin.i32(i32 %65, i32 %132)
  %134 = add i32 %133, %74
  %135 = mul i32 %134, %73
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, float* %71, i64 %136
  %138 = load float, float* %137, align 4
  %139 = add i32 %135, 1
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %71, i64 %140
  %142 = load float, float* %141, align 4
  %143 = add i32 %135, 2
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, float* %71, i64 %144
  %146 = load float, float* %145, align 4
  %147 = add i32 %48, 2
  %148 = tail call i32 @llvm.abs.i32(i32 %147, i1 true)
  %149 = sub i32 %148, %65
  %150 = tail call i32 @llvm.smax.i32(i32 %149, i32 0)
  %.neg10 = mul i32 %150, -2
  %151 = add i32 %.neg10, %148
  %152 = tail call i32 @llvm.smax.i32(i32 %151, i32 0)
  %153 = tail call i32 @llvm.smin.i32(i32 %65, i32 %152)
  %154 = add i32 %153, %74
  %155 = mul i32 %154, %73
  %156 = sext i32 %155 to i64
  %157 = getelementptr float, float* %71, i64 %156
  %158 = load float, float* %157, align 4
  %159 = add i32 %155, 1
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, float* %71, i64 %160
  %162 = load float, float* %161, align 4
  %163 = add i32 %155, 2
  %164 = sext i32 %163 to i64
  %165 = getelementptr float, float* %71, i64 %164
  %166 = load float, float* %165, align 4
  %167 = add i32 %45, -1
  %168 = tail call i32 @llvm.abs.i32(i32 %167, i1 true)
  %169 = sub i32 %168, %54
  %170 = tail call i32 @llvm.smax.i32(i32 %169, i32 0)
  %.neg11 = mul i32 %170, -2
  %171 = add i32 %.neg11, %168
  %172 = tail call i32 @llvm.smax.i32(i32 %171, i32 0)
  %173 = tail call i32 @llvm.smin.i32(i32 %54, i32 %172)
  %174 = mul i32 %173, %72
  %175 = add i32 %70, %174
  %176 = mul i32 %175, %73
  %177 = sext i32 %176 to i64
  %178 = getelementptr float, float* %71, i64 %177
  %179 = load float, float* %178, align 4
  %180 = add i32 %176, 1
  %181 = sext i32 %180 to i64
  %182 = getelementptr float, float* %71, i64 %181
  %183 = load float, float* %182, align 4
  %184 = add i32 %176, 2
  %185 = sext i32 %184 to i64
  %186 = getelementptr float, float* %71, i64 %185
  %187 = load float, float* %186, align 4
  %188 = add i32 %94, %174
  %189 = mul i32 %188, %73
  %190 = sext i32 %189 to i64
  %191 = getelementptr float, float* %71, i64 %190
  %192 = load float, float* %191, align 4
  %193 = add i32 %189, 1
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %71, i64 %194
  %196 = load float, float* %195, align 4
  %197 = add i32 %189, 2
  %198 = sext i32 %197 to i64
  %199 = getelementptr float, float* %71, i64 %198
  %200 = load float, float* %199, align 4
  %201 = add i32 %174, %113
  %202 = mul i32 %201, %73
  %203 = sext i32 %202 to i64
  %204 = getelementptr float, float* %71, i64 %203
  %205 = load float, float* %204, align 4
  %206 = add i32 %202, 1
  %207 = sext i32 %206 to i64
  %208 = getelementptr float, float* %71, i64 %207
  %209 = load float, float* %208, align 4
  %210 = add i32 %202, 2
  %211 = sext i32 %210 to i64
  %212 = getelementptr float, float* %71, i64 %211
  %213 = load float, float* %212, align 4
  %214 = add i32 %133, %174
  %215 = mul i32 %214, %73
  %216 = sext i32 %215 to i64
  %217 = getelementptr float, float* %71, i64 %216
  %218 = load float, float* %217, align 4
  %219 = add i32 %215, 1
  %220 = sext i32 %219 to i64
  %221 = getelementptr float, float* %71, i64 %220
  %222 = load float, float* %221, align 4
  %223 = add i32 %215, 2
  %224 = sext i32 %223 to i64
  %225 = getelementptr float, float* %71, i64 %224
  %226 = load float, float* %225, align 4
  %227 = add i32 %153, %174
  %228 = mul i32 %227, %73
  %229 = sext i32 %228 to i64
  %230 = getelementptr float, float* %71, i64 %229
  %231 = load float, float* %230, align 4
  %232 = add i32 %228, 1
  %233 = sext i32 %232 to i64
  %234 = getelementptr float, float* %71, i64 %233
  %235 = load float, float* %234, align 4
  %236 = add i32 %228, 2
  %237 = sext i32 %236 to i64
  %238 = getelementptr float, float* %71, i64 %237
  %239 = load float, float* %238, align 4
  %240 = tail call i32 @llvm.abs.i32(i32 %45, i1 true)
  %241 = sub i32 %240, %54
  %242 = tail call i32 @llvm.smax.i32(i32 %241, i32 0)
  %.neg12 = mul i32 %242, -2
  %243 = add i32 %.neg12, %240
  %244 = tail call i32 @llvm.smax.i32(i32 %243, i32 0)
  %245 = tail call i32 @llvm.smin.i32(i32 %54, i32 %244)
  %246 = mul i32 %245, %72
  %247 = add i32 %70, %246
  %248 = mul i32 %247, %73
  %249 = sext i32 %248 to i64
  %250 = getelementptr float, float* %71, i64 %249
  %251 = load float, float* %250, align 4
  %252 = add i32 %248, 1
  %253 = sext i32 %252 to i64
  %254 = getelementptr float, float* %71, i64 %253
  %255 = load float, float* %254, align 4
  %256 = add i32 %248, 2
  %257 = sext i32 %256 to i64
  %258 = getelementptr float, float* %71, i64 %257
  %259 = load float, float* %258, align 4
  %260 = add i32 %94, %246
  %261 = mul i32 %260, %73
  %262 = sext i32 %261 to i64
  %263 = getelementptr float, float* %71, i64 %262
  %264 = load float, float* %263, align 4
  %265 = add i32 %261, 1
  %266 = sext i32 %265 to i64
  %267 = getelementptr float, float* %71, i64 %266
  %268 = load float, float* %267, align 4
  %269 = add i32 %261, 2
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, float* %71, i64 %270
  %272 = load float, float* %271, align 4
  %273 = add i32 %113, %246
  %274 = mul i32 %273, %73
  %275 = sext i32 %274 to i64
  %276 = getelementptr float, float* %71, i64 %275
  %277 = load float, float* %276, align 4
  %278 = add i32 %274, 1
  %279 = sext i32 %278 to i64
  %280 = getelementptr float, float* %71, i64 %279
  %281 = load float, float* %280, align 4
  %282 = add i32 %274, 2
  %283 = sext i32 %282 to i64
  %284 = getelementptr float, float* %71, i64 %283
  %285 = load float, float* %284, align 4
  %286 = fmul reassoc ninf nsz float %277, 3.600000e+01
  %287 = fmul reassoc ninf nsz float %281, 3.600000e+01
  %288 = fmul reassoc ninf nsz float %285, 3.600000e+01
  %289 = add i32 %133, %246
  %290 = mul i32 %289, %73
  %291 = sext i32 %290 to i64
  %292 = getelementptr float, float* %71, i64 %291
  %293 = load float, float* %292, align 4
  %294 = add i32 %290, 1
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, float* %71, i64 %295
  %297 = load float, float* %296, align 4
  %298 = add i32 %290, 2
  %299 = sext i32 %298 to i64
  %300 = getelementptr float, float* %71, i64 %299
  %301 = load float, float* %300, align 4
  %302 = add i32 %153, %246
  %303 = mul i32 %302, %73
  %304 = sext i32 %303 to i64
  %305 = getelementptr float, float* %71, i64 %304
  %306 = load float, float* %305, align 4
  %307 = add i32 %303, 1
  %308 = sext i32 %307 to i64
  %309 = getelementptr float, float* %71, i64 %308
  %310 = load float, float* %309, align 4
  %311 = add i32 %303, 2
  %312 = sext i32 %311 to i64
  %313 = getelementptr float, float* %71, i64 %312
  %314 = load float, float* %313, align 4
  %315 = or i32 %45, 1
  %316 = tail call i32 @llvm.abs.i32(i32 %315, i1 true)
  %317 = sub i32 %316, %54
  %318 = tail call i32 @llvm.smax.i32(i32 %317, i32 0)
  %.neg13 = mul i32 %318, -2
  %319 = add i32 %.neg13, %316
  %320 = tail call i32 @llvm.smax.i32(i32 %319, i32 0)
  %321 = tail call i32 @llvm.smin.i32(i32 %54, i32 %320)
  %322 = mul i32 %321, %72
  %323 = add i32 %70, %322
  %324 = mul i32 %323, %73
  %325 = sext i32 %324 to i64
  %326 = getelementptr float, float* %71, i64 %325
  %327 = load float, float* %326, align 4
  %328 = add i32 %324, 1
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, float* %71, i64 %329
  %331 = load float, float* %330, align 4
  %332 = add i32 %324, 2
  %333 = sext i32 %332 to i64
  %334 = getelementptr float, float* %71, i64 %333
  %335 = load float, float* %334, align 4
  %336 = add i32 %94, %322
  %337 = mul i32 %336, %73
  %338 = sext i32 %337 to i64
  %339 = getelementptr float, float* %71, i64 %338
  %340 = load float, float* %339, align 4
  %341 = add i32 %337, 1
  %342 = sext i32 %341 to i64
  %343 = getelementptr float, float* %71, i64 %342
  %344 = load float, float* %343, align 4
  %345 = add i32 %337, 2
  %346 = sext i32 %345 to i64
  %347 = getelementptr float, float* %71, i64 %346
  %348 = load float, float* %347, align 4
  %349 = add i32 %322, %113
  %350 = mul i32 %349, %73
  %351 = sext i32 %350 to i64
  %352 = getelementptr float, float* %71, i64 %351
  %353 = load float, float* %352, align 4
  %354 = add i32 %350, 1
  %355 = sext i32 %354 to i64
  %356 = getelementptr float, float* %71, i64 %355
  %357 = load float, float* %356, align 4
  %358 = add i32 %350, 2
  %359 = sext i32 %358 to i64
  %360 = getelementptr float, float* %71, i64 %359
  %361 = load float, float* %360, align 4
  %362 = add i32 %133, %322
  %363 = mul i32 %362, %73
  %364 = sext i32 %363 to i64
  %365 = getelementptr float, float* %71, i64 %364
  %366 = load float, float* %365, align 4
  %367 = add i32 %363, 1
  %368 = sext i32 %367 to i64
  %369 = getelementptr float, float* %71, i64 %368
  %370 = load float, float* %369, align 4
  %371 = add i32 %363, 2
  %372 = sext i32 %371 to i64
  %373 = getelementptr float, float* %71, i64 %372
  %374 = load float, float* %373, align 4
  %375 = add i32 %153, %322
  %376 = mul i32 %375, %73
  %377 = sext i32 %376 to i64
  %378 = getelementptr float, float* %71, i64 %377
  %379 = load float, float* %378, align 4
  %380 = add i32 %376, 1
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, float* %71, i64 %381
  %383 = load float, float* %382, align 4
  %384 = add i32 %376, 2
  %385 = sext i32 %384 to i64
  %386 = getelementptr float, float* %71, i64 %385
  %387 = load float, float* %386, align 4
  %388 = add i32 %45, 2
  %389 = tail call i32 @llvm.abs.i32(i32 %388, i1 true)
  %390 = sub i32 %389, %54
  %391 = tail call i32 @llvm.smax.i32(i32 %390, i32 0)
  %.neg14 = mul i32 %391, -2
  %392 = add i32 %.neg14, %389
  %393 = tail call i32 @llvm.smax.i32(i32 %392, i32 0)
  %394 = tail call i32 @llvm.smin.i32(i32 %54, i32 %393)
  %395 = mul i32 %394, %72
  %396 = add i32 %70, %395
  %397 = mul i32 %396, %73
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, float* %71, i64 %398
  %400 = load float, float* %399, align 4
  %401 = add i32 %397, 1
  %402 = sext i32 %401 to i64
  %403 = getelementptr float, float* %71, i64 %402
  %404 = load float, float* %403, align 4
  %405 = add i32 %397, 2
  %406 = sext i32 %405 to i64
  %407 = getelementptr float, float* %71, i64 %406
  %408 = load float, float* %407, align 4
  %409 = add i32 %94, %395
  %410 = mul i32 %409, %73
  %411 = sext i32 %410 to i64
  %412 = getelementptr float, float* %71, i64 %411
  %413 = load float, float* %412, align 4
  %414 = add i32 %410, 1
  %415 = sext i32 %414 to i64
  %416 = getelementptr float, float* %71, i64 %415
  %417 = load float, float* %416, align 4
  %418 = add i32 %410, 2
  %419 = sext i32 %418 to i64
  %420 = getelementptr float, float* %71, i64 %419
  %421 = load float, float* %420, align 4
  %422 = add i32 %395, %113
  %423 = mul i32 %422, %73
  %424 = sext i32 %423 to i64
  %425 = getelementptr float, float* %71, i64 %424
  %426 = load float, float* %425, align 4
  %427 = add i32 %423, 1
  %428 = sext i32 %427 to i64
  %429 = getelementptr float, float* %71, i64 %428
  %430 = load float, float* %429, align 4
  %431 = add i32 %423, 2
  %432 = sext i32 %431 to i64
  %433 = getelementptr float, float* %71, i64 %432
  %434 = load float, float* %433, align 4
  %435 = add i32 %133, %395
  %436 = mul i32 %435, %73
  %437 = sext i32 %436 to i64
  %438 = getelementptr float, float* %71, i64 %437
  %439 = load float, float* %438, align 4
  %440 = add i32 %436, 1
  %441 = sext i32 %440 to i64
  %442 = getelementptr float, float* %71, i64 %441
  %443 = load float, float* %442, align 4
  %444 = add i32 %436, 2
  %445 = sext i32 %444 to i64
  %446 = getelementptr float, float* %71, i64 %445
  %447 = load float, float* %446, align 4
  %448 = add i32 %153, %395
  %449 = mul i32 %448, %73
  %450 = sext i32 %449 to i64
  %451 = getelementptr float, float* %71, i64 %450
  %452 = load float, float* %451, align 4
  %453 = add i32 %449, 1
  %454 = sext i32 %453 to i64
  %455 = getelementptr float, float* %71, i64 %454
  %456 = load float, float* %455, align 4
  %457 = add i32 %449, 2
  %458 = sext i32 %457 to i64
  %459 = getelementptr float, float* %71, i64 %458
  %460 = load float, float* %459, align 4
  %reass.add = fadd reassoc ninf nsz float %138, %99
  %reass.add15 = fadd reassoc ninf nsz float %reass.add, %179
  %reass.add16 = fadd reassoc ninf nsz float %reass.add15, %231
  %reass.add17 = fadd reassoc ninf nsz float %reass.add16, %327
  %reass.add18 = fadd reassoc ninf nsz float %reass.add17, %379
  %reass.add19 = fadd reassoc ninf nsz float %reass.add18, %413
  %reass.add20 = fadd reassoc ninf nsz float %reass.add19, %439
  %reass.mul = fmul reassoc ninf nsz float %reass.add20, 4.000000e+00
  %reass.add21 = fadd reassoc ninf nsz float %264, %205
  %reass.add22 = fadd reassoc ninf nsz float %reass.add21, %293
  %reass.add23 = fadd reassoc ninf nsz float %reass.add22, %353
  %reass.mul24 = fmul reassoc ninf nsz float %reass.add23, 2.400000e+01
  %reass.add25 = fadd reassoc ninf nsz float %218, %192
  %reass.add26 = fadd reassoc ninf nsz float %reass.add25, %340
  %reass.add27 = fadd reassoc ninf nsz float %reass.add26, %366
  %reass.mul28 = fmul reassoc ninf nsz float %reass.add27, 1.600000e+01
  %reass.add29 = fadd reassoc ninf nsz float %251, %118
  %reass.add30 = fadd reassoc ninf nsz float %reass.add29, %306
  %reass.add31 = fadd reassoc ninf nsz float %reass.add30, %426
  %reass.mul32 = fmul reassoc ninf nsz float %reass.add31, 6.000000e+00
  %461 = fadd reassoc ninf nsz float %158, %79
  %462 = fadd reassoc ninf nsz float %461, %286
  %463 = fadd reassoc ninf nsz float %462, %reass.mul24
  %464 = fadd reassoc ninf nsz float %463, %reass.mul28
  %465 = fadd reassoc ninf nsz float %464, %400
  %466 = fadd reassoc ninf nsz float %465, %reass.mul32
  %467 = fadd reassoc ninf nsz float %466, %452
  %468 = fadd reassoc ninf nsz float %467, %reass.mul
  %reass.add33 = fadd reassoc ninf nsz float %142, %103
  %reass.add34 = fadd reassoc ninf nsz float %reass.add33, %183
  %reass.add35 = fadd reassoc ninf nsz float %reass.add34, %235
  %reass.add36 = fadd reassoc ninf nsz float %reass.add35, %331
  %reass.add37 = fadd reassoc ninf nsz float %reass.add36, %383
  %reass.add38 = fadd reassoc ninf nsz float %reass.add37, %417
  %reass.add39 = fadd reassoc ninf nsz float %reass.add38, %443
  %reass.mul40 = fmul reassoc ninf nsz float %reass.add39, 4.000000e+00
  %reass.add41 = fadd reassoc ninf nsz float %268, %209
  %reass.add42 = fadd reassoc ninf nsz float %reass.add41, %297
  %reass.add43 = fadd reassoc ninf nsz float %reass.add42, %357
  %reass.mul44 = fmul reassoc ninf nsz float %reass.add43, 2.400000e+01
  %reass.add45 = fadd reassoc ninf nsz float %222, %196
  %reass.add46 = fadd reassoc ninf nsz float %reass.add45, %344
  %reass.add47 = fadd reassoc ninf nsz float %reass.add46, %370
  %reass.mul48 = fmul reassoc ninf nsz float %reass.add47, 1.600000e+01
  %reass.add49 = fadd reassoc ninf nsz float %255, %122
  %reass.add50 = fadd reassoc ninf nsz float %reass.add49, %310
  %reass.add51 = fadd reassoc ninf nsz float %reass.add50, %430
  %reass.mul52 = fmul reassoc ninf nsz float %reass.add51, 6.000000e+00
  %469 = fadd reassoc ninf nsz float %162, %83
  %470 = fadd reassoc ninf nsz float %469, %287
  %471 = fadd reassoc ninf nsz float %470, %reass.mul44
  %472 = fadd reassoc ninf nsz float %471, %reass.mul48
  %473 = fadd reassoc ninf nsz float %472, %404
  %474 = fadd reassoc ninf nsz float %473, %reass.mul52
  %475 = fadd reassoc ninf nsz float %474, %456
  %476 = fadd reassoc ninf nsz float %475, %reass.mul40
  %reass.add53 = fadd reassoc ninf nsz float %146, %107
  %reass.add54 = fadd reassoc ninf nsz float %reass.add53, %187
  %reass.add55 = fadd reassoc ninf nsz float %reass.add54, %239
  %reass.add56 = fadd reassoc ninf nsz float %reass.add55, %335
  %reass.add57 = fadd reassoc ninf nsz float %reass.add56, %387
  %reass.add58 = fadd reassoc ninf nsz float %reass.add57, %421
  %reass.add59 = fadd reassoc ninf nsz float %reass.add58, %447
  %reass.mul60 = fmul reassoc ninf nsz float %reass.add59, 4.000000e+00
  %reass.add61 = fadd reassoc ninf nsz float %272, %213
  %reass.add62 = fadd reassoc ninf nsz float %reass.add61, %301
  %reass.add63 = fadd reassoc ninf nsz float %reass.add62, %361
  %reass.mul64 = fmul reassoc ninf nsz float %reass.add63, 2.400000e+01
  %reass.add65 = fadd reassoc ninf nsz float %226, %200
  %reass.add66 = fadd reassoc ninf nsz float %reass.add65, %348
  %reass.add67 = fadd reassoc ninf nsz float %reass.add66, %374
  %reass.mul68 = fmul reassoc ninf nsz float %reass.add67, 1.600000e+01
  %reass.add69 = fadd reassoc ninf nsz float %259, %126
  %reass.add70 = fadd reassoc ninf nsz float %reass.add69, %314
  %reass.add71 = fadd reassoc ninf nsz float %reass.add70, %434
  %reass.mul72 = fmul reassoc ninf nsz float %reass.add71, 6.000000e+00
  %477 = fadd reassoc ninf nsz float %166, %87
  %478 = fadd reassoc ninf nsz float %477, %288
  %479 = fadd reassoc ninf nsz float %478, %reass.mul64
  %480 = fadd reassoc ninf nsz float %479, %reass.mul68
  %481 = fadd reassoc ninf nsz float %480, %408
  %482 = fadd reassoc ninf nsz float %481, %reass.mul72
  %483 = fadd reassoc ninf nsz float %482, %460
  %484 = fadd reassoc ninf nsz float %483, %reass.mul60
  %485 = fmul reassoc ninf nsz float %468, 3.906250e-03
  %486 = fmul reassoc ninf nsz float %476, 3.906250e-03
  %487 = fmul reassoc ninf nsz float %484, 3.906250e-03
  %488 = load float*, float** %26, align 8
  %489 = load i32, i32* %27, align 4
  %490 = load i32, i32* %28, align 4
  %491 = sub i32 %489, %35
  %492 = mul i32 %491, %44
  %493 = add i32 %.073, %492
  %494 = mul i32 %493, %490
  %495 = sext i32 %494 to i64
  %496 = getelementptr float, float* %488, i64 %495
  store float %485, float* %496, align 4
  %497 = load float*, float** %26, align 8
  %498 = load i32, i32* %27, align 4
  %499 = load i32, i32* %28, align 4
  %500 = sub i32 %498, %35
  %501 = mul i32 %500, %44
  %502 = add i32 %.073, %501
  %503 = mul i32 %502, %499
  %504 = add i32 %503, 1
  %505 = sext i32 %504 to i64
  %506 = getelementptr float, float* %497, i64 %505
  store float %486, float* %506, align 4
  %507 = load float*, float** %26, align 8
  %508 = load i32, i32* %27, align 4
  %509 = load i32, i32* %28, align 4
  %510 = sub i32 %508, %35
  %511 = mul i32 %510, %44
  %512 = add i32 %.073, %511
  %513 = mul i32 %512, %509
  %514 = add i32 %513, 2
  %515 = sext i32 %514 to i64
  %516 = getelementptr float, float* %507, i64 %515
  store float %487, float* %516, align 4
  %517 = add nsw i32 %.073, 1
  %lsr.iv.next = add i32 %lsr.iv, 2
  %exitcond.not = icmp eq i32 %19, %517
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
declare i32 @llvm.abs.i32(i32, i1 immarg) #5

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
