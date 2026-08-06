; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { i8*, %struct.LLVMRuntime.5*, i32, i64* }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.2*], [1024 x %struct.NodeManager.3*], [1024 x i8*], i8*, %struct.RandState.4*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { i8*, i8*, i64 }
%struct.ListManager.2 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.5* }
%struct.NodeManager.3 = type { %struct.LLVMRuntime.5*, i32, i32, i32, i32, %struct.ListManager.2*, %struct.ListManager.2*, %struct.ListManager.2*, i32 }
%struct.RandState.4 = type { i32, i32, i32, i32, i32 }
%struct.range_task_helper_context = type { %struct.RuntimeContext.6*, void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*)*, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @compute_score_map_c698_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @compute_score_map_c698_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast %struct.range_task_helper_context* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 0
  store %struct.RuntimeContext.6* %context, %struct.RuntimeContext.6** %4, align 8
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.6*, i8*, i32)* @function_body, void (%struct.RuntimeContext.6*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.6*, i8*)* null, void (%struct.RuntimeContext.6*, i8*)** %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, %struct.range_task_helper_context* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.6* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %21, i64 0, i32 4
  %23 = load i32, i32* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.preheader
  %.0127173 = phi i32 [ %197, %after_if9 ], [ %17, %for_loop_body.preheader ]
  %25 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %26 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %25, i64 0, i32 14
  %27 = load i8*, i8** %26, align 8
  %28 = getelementptr inbounds i8, i8* %27, i64 4
  %29 = bitcast i8* %28 to i32*
  %30 = load i32, i32* %29, align 4
  %31 = sdiv i32 %.0127173, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.0127173
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %.0127173, 0
  %36 = icmp ne i32 %.0127173, %32
  %37 = and i1 %35, %34
  %38 = and i1 %37, %36
  %.neg169 = sext i1 %38 to i32
  %39 = add i32 %31, %.neg169
  %40 = mul i32 %39, %30
  %41 = mul i32 %30, -1
  %42 = mul i32 %41, %39
  %43 = add i32 %.0127173, %42
  %.not = icmp slt i32 %39, %23
  br i1 %.not, label %false_block8, label %true_block

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %44 = getelementptr inbounds i8, i8* %27, i64 8
  %45 = bitcast i8* %44 to i32*
  %46 = load i32, i32* %45, align 4
  %47 = sub i32 %46, %23
  %48 = icmp sge i32 %39, %47
  %.not170 = icmp slt i32 %43, %23
  %or.cond = select i1 %48, i1 true, i1 %.not170
  br i1 %or.cond, label %false_block8, label %true_block4

true_block4:                                      ; preds = %true_block
  %49 = getelementptr inbounds i8, i8* %27, i64 12
  %50 = bitcast i8* %49 to i32*
  %51 = load i32, i32* %50, align 4
  %52 = sub i32 %51, %23
  %53 = icmp slt i32 %43, %52
  br i1 %53, label %true_block7, label %false_block8

true_block7:                                      ; preds = %true_block4
  %54 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %20, align 8
  %55 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %54, i64 0, i32 0, i32 1
  %56 = load float*, float** %55, align 8
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %54, i64 0, i32 0, i32 0, i32 1
  %58 = load i32, i32* %57, align 4
  %59 = sub i32 %58, %30
  %60 = mul i32 %59, %39
  %61 = add i32 %.0127173, %60
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, float* %56, i64 %62
  %64 = load float, float* %63, align 4
  %65 = add i32 %39, 3
  %66 = mul i32 %58, %65
  %67 = sub i32 %66, %40
  %68 = add i32 %.0127173, %67
  %69 = sext i32 %68 to i64
  %70 = getelementptr float, float* %56, i64 %69
  %71 = load float, float* %70, align 4
  %72 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %71, float 0.000000e+00)
  %73 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %71, float 1.000000e+00)
  %74 = add i32 %68, 1
  %75 = sext i32 %74 to i64
  %76 = getelementptr float, float* %56, i64 %75
  %77 = load float, float* %76, align 4
  %78 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %72, float %77)
  %79 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %73, float %77)
  %80 = add i32 %39, 2
  %81 = mul i32 %58, %80
  %82 = sub i32 %81, %40
  %83 = add i32 %.0127173, %82
  %84 = add i32 %83, 2
  %85 = sext i32 %84 to i64
  %86 = getelementptr float, float* %56, i64 %85
  %87 = load float, float* %86, align 4
  %88 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %78, float %87)
  %89 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %79, float %87)
  %90 = add nsw i32 %39, 1
  %91 = mul i32 %58, %90
  %92 = sub i32 %91, %40
  %93 = add i32 %.0127173, %92
  %94 = add i32 %93, 3
  %95 = sext i32 %94 to i64
  %96 = getelementptr float, float* %56, i64 %95
  %97 = load float, float* %96, align 4
  %98 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %88, float %97)
  %99 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %89, float %97)
  %100 = add i32 %61, 3
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %56, i64 %101
  %103 = load float, float* %102, align 4
  %104 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %98, float %103)
  %105 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %99, float %103)
  %106 = add i32 %39, -1
  %107 = mul i32 %58, %106
  %108 = sub i32 %107, %40
  %109 = add i32 %.0127173, %108
  %110 = add i32 %109, 3
  %111 = sext i32 %110 to i64
  %112 = getelementptr float, float* %56, i64 %111
  %113 = load float, float* %112, align 4
  %114 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %104, float %113)
  %115 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %105, float %113)
  %116 = add i32 %39, -2
  %117 = mul i32 %58, %116
  %118 = sub i32 %117, %40
  %119 = add i32 %.0127173, %118
  %120 = add i32 %119, 2
  %121 = sext i32 %120 to i64
  %122 = getelementptr float, float* %56, i64 %121
  %123 = load float, float* %122, align 4
  %124 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %114, float %123)
  %125 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %115, float %123)
  %126 = add i32 %39, -3
  %127 = mul i32 %58, %126
  %128 = sub i32 %127, %40
  %129 = add i32 %.0127173, %128
  %130 = add i32 %129, 1
  %131 = sext i32 %130 to i64
  %132 = getelementptr float, float* %56, i64 %131
  %133 = load float, float* %132, align 4
  %134 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %124, float %133)
  %135 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %125, float %133)
  %136 = sext i32 %129 to i64
  %137 = getelementptr float, float* %56, i64 %136
  %138 = load float, float* %137, align 4
  %139 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %134, float %138)
  %140 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %135, float %138)
  %141 = add i32 %129, -1
  %142 = sext i32 %141 to i64
  %143 = getelementptr float, float* %56, i64 %142
  %144 = load float, float* %143, align 4
  %145 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %139, float %144)
  %146 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %140, float %144)
  %147 = add i32 %119, -2
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, float* %56, i64 %148
  %150 = load float, float* %149, align 4
  %151 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %145, float %150)
  %152 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %146, float %150)
  %153 = add i32 %109, -3
  %154 = sext i32 %153 to i64
  %155 = getelementptr float, float* %56, i64 %154
  %156 = load float, float* %155, align 4
  %157 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %151, float %156)
  %158 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %152, float %156)
  %159 = add i32 %61, -3
  %160 = sext i32 %159 to i64
  %161 = getelementptr float, float* %56, i64 %160
  %162 = load float, float* %161, align 4
  %163 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %157, float %162)
  %164 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %158, float %162)
  %165 = add i32 %93, -3
  %166 = sext i32 %165 to i64
  %167 = getelementptr float, float* %56, i64 %166
  %168 = load float, float* %167, align 4
  %169 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %163, float %168)
  %170 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %164, float %168)
  %171 = add i32 %83, -2
  %172 = sext i32 %171 to i64
  %173 = getelementptr float, float* %56, i64 %172
  %174 = load float, float* %173, align 4
  %175 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %169, float %174)
  %176 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %170, float %174)
  %177 = add i32 %68, -1
  %178 = sext i32 %177 to i64
  %179 = getelementptr float, float* %56, i64 %178
  %180 = load float, float* %179, align 4
  %181 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %175, float %180)
  %182 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %176, float %180)
  %183 = fsub reassoc ninf nsz float %181, %182
  %184 = fmul reassoc ninf nsz float %183, 0x3FD99999A0000000
  %185 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %184, float 0x3F8EB851E0000000)
  %186 = fcmp reassoc ninf nsz ogt float %183, 0x3F689374C0000000
  br i1 %186, label %true_block10, label %after_if12

false_block8:                                     ; preds = %true_block4, %true_block, %for_loop_body
  %187 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }** %20, align 8
  br label %after_if9

after_if9:                                        ; preds = %after_if134, %false_block8
  %.sink179 = phi { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* [ %54, %after_if134 ], [ %187, %false_block8 ]
  %.088.sink = phi float [ %.088, %after_if134 ], [ 0.000000e+00, %false_block8 ]
  %188 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %.sink179, i64 0, i32 1, i32 1
  %189 = load float*, float** %188, align 8
  %190 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32 }* %.sink179, i64 0, i32 1, i32 0, i32 1
  %191 = load i32, i32* %190, align 4
  %192 = sub i32 %191, %30
  %193 = mul i32 %192, %39
  %194 = add i32 %.0127173, %193
  %195 = sext i32 %194 to i64
  %196 = getelementptr float, float* %189, i64 %195
  store float %.088.sink, float* %196, align 4
  %197 = add nsw i32 %.0127173, 1
  %exitcond.not = icmp eq i32 %19, %197
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %true_block7
  %198 = fadd reassoc ninf nsz float %183, 0x3F847AE140000000
  %199 = fdiv reassoc ninf nsz float 1.000000e+00, %198
  br label %after_if12

after_if12:                                       ; preds = %true_block10, %true_block7
  %.089 = phi float [ %199, %true_block10 ], [ 1.000000e+00, %true_block7 ]
  %200 = fsub reassoc ninf nsz float %64, %71
  %201 = fmul reassoc ninf nsz float %.089, %200
  %202 = fmul reassoc ninf nsz float %.089, %185
  %203 = fcmp reassoc ninf nsz ogt float %201, %202
  br i1 %203, label %after_if15, label %false_block14

false_block14:                                    ; preds = %after_if12
  %neg = fneg reassoc ninf nsz float %202
  %204 = fcmp reassoc ninf nsz olt float %201, %neg
  br i1 %204, label %true_block16, label %after_if15

after_if15:                                       ; preds = %true_block16, %false_block14, %after_if12
  %.0107 = phi float [ %neg19, %true_block16 ], [ 0.000000e+00, %false_block14 ], [ %200, %after_if12 ]
  %.091 = phi i32 [ 0, %true_block16 ], [ 0, %false_block14 ], [ 1, %after_if12 ]
  %.090 = phi i32 [ 1, %true_block16 ], [ 0, %false_block14 ], [ 0, %after_if12 ]
  %205 = fsub reassoc ninf nsz float %64, %77
  %206 = fmul reassoc ninf nsz float %.089, %205
  %207 = fcmp reassoc ninf nsz ogt float %206, %202
  br i1 %207, label %true_block20, label %false_block21

true_block16:                                     ; preds = %false_block14
  %neg19 = fneg reassoc ninf nsz float %200
  br label %after_if15

true_block20:                                     ; preds = %after_if15
  %208 = add nuw nsw i32 %.091, 1
  %209 = fadd reassoc ninf nsz float %.0107, %205
  br label %after_if22

false_block21:                                    ; preds = %after_if15
  %neg23 = fneg reassoc ninf nsz float %202
  %210 = fcmp reassoc ninf nsz olt float %206, %neg23
  br i1 %210, label %true_block24, label %after_if22

after_if22:                                       ; preds = %true_block24, %false_block21, %true_block20
  %.1108 = phi float [ %209, %true_block20 ], [ %215, %true_block24 ], [ %.0107, %false_block21 ]
  %.192 = phi i32 [ %208, %true_block20 ], [ %.091, %true_block24 ], [ %.091, %false_block21 ]
  %.1 = phi i32 [ %.090, %true_block20 ], [ %214, %true_block24 ], [ %.090, %false_block21 ]
  %211 = fsub reassoc ninf nsz float %64, %87
  %212 = fmul reassoc ninf nsz float %.089, %211
  %213 = fcmp reassoc ninf nsz ogt float %212, %202
  br i1 %213, label %true_block28, label %false_block29

true_block24:                                     ; preds = %false_block21
  %214 = add nuw nsw i32 %.090, 1
  %215 = fsub reassoc ninf nsz float %.0107, %205
  br label %after_if22

true_block28:                                     ; preds = %after_if22
  %216 = add nuw nsw i32 %.192, 1
  %217 = fadd reassoc ninf nsz float %.1108, %211
  br label %after_if30

false_block29:                                    ; preds = %after_if22
  %neg31 = fneg reassoc ninf nsz float %202
  %218 = fcmp reassoc ninf nsz olt float %212, %neg31
  br i1 %218, label %true_block32, label %after_if30

after_if30:                                       ; preds = %true_block32, %false_block29, %true_block28
  %.2109 = phi float [ %217, %true_block28 ], [ %223, %true_block32 ], [ %.1108, %false_block29 ]
  %.293 = phi i32 [ %216, %true_block28 ], [ %.192, %true_block32 ], [ %.192, %false_block29 ]
  %.2 = phi i32 [ %.1, %true_block28 ], [ %222, %true_block32 ], [ %.1, %false_block29 ]
  %219 = fsub reassoc ninf nsz float %64, %97
  %220 = fmul reassoc ninf nsz float %.089, %219
  %221 = fcmp reassoc ninf nsz ogt float %220, %202
  br i1 %221, label %true_block36, label %false_block37

true_block32:                                     ; preds = %false_block29
  %222 = add nuw nsw i32 %.1, 1
  %223 = fsub reassoc ninf nsz float %.1108, %211
  br label %after_if30

true_block36:                                     ; preds = %after_if30
  %224 = add nuw nsw i32 %.293, 1
  %225 = fadd reassoc ninf nsz float %.2109, %219
  br label %after_if38

false_block37:                                    ; preds = %after_if30
  %neg39 = fneg reassoc ninf nsz float %202
  %226 = fcmp reassoc ninf nsz olt float %220, %neg39
  br i1 %226, label %true_block40, label %after_if38

after_if38:                                       ; preds = %true_block40, %false_block37, %true_block36
  %.3110 = phi float [ %225, %true_block36 ], [ %231, %true_block40 ], [ %.2109, %false_block37 ]
  %.394 = phi i32 [ %224, %true_block36 ], [ %.293, %true_block40 ], [ %.293, %false_block37 ]
  %.3 = phi i32 [ %.2, %true_block36 ], [ %230, %true_block40 ], [ %.2, %false_block37 ]
  %227 = fsub reassoc ninf nsz float %64, %103
  %228 = fmul reassoc ninf nsz float %.089, %227
  %229 = fcmp reassoc ninf nsz ogt float %228, %202
  br i1 %229, label %true_block44, label %false_block45

true_block40:                                     ; preds = %false_block37
  %230 = add nuw nsw i32 %.2, 1
  %231 = fsub reassoc ninf nsz float %.2109, %219
  br label %after_if38

true_block44:                                     ; preds = %after_if38
  %232 = add nuw nsw i32 %.394, 1
  %233 = fadd reassoc ninf nsz float %.3110, %227
  br label %after_if46

false_block45:                                    ; preds = %after_if38
  %neg47 = fneg reassoc ninf nsz float %202
  %234 = fcmp reassoc ninf nsz olt float %228, %neg47
  br i1 %234, label %true_block48, label %after_if46

after_if46:                                       ; preds = %true_block48, %false_block45, %true_block44
  %.4111 = phi float [ %233, %true_block44 ], [ %239, %true_block48 ], [ %.3110, %false_block45 ]
  %.495 = phi i32 [ %232, %true_block44 ], [ %.394, %true_block48 ], [ %.394, %false_block45 ]
  %.4 = phi i32 [ %.3, %true_block44 ], [ %238, %true_block48 ], [ %.3, %false_block45 ]
  %235 = fsub reassoc ninf nsz float %64, %113
  %236 = fmul reassoc ninf nsz float %.089, %235
  %237 = fcmp reassoc ninf nsz ogt float %236, %202
  br i1 %237, label %true_block52, label %false_block53

true_block48:                                     ; preds = %false_block45
  %238 = add nuw nsw i32 %.3, 1
  %239 = fsub reassoc ninf nsz float %.3110, %227
  br label %after_if46

true_block52:                                     ; preds = %after_if46
  %240 = add nuw nsw i32 %.495, 1
  %241 = fadd reassoc ninf nsz float %.4111, %235
  br label %after_if54

false_block53:                                    ; preds = %after_if46
  %neg55 = fneg reassoc ninf nsz float %202
  %242 = fcmp reassoc ninf nsz olt float %236, %neg55
  br i1 %242, label %true_block56, label %after_if54

after_if54:                                       ; preds = %true_block56, %false_block53, %true_block52
  %.5112 = phi float [ %241, %true_block52 ], [ %247, %true_block56 ], [ %.4111, %false_block53 ]
  %.596 = phi i32 [ %240, %true_block52 ], [ %.495, %true_block56 ], [ %.495, %false_block53 ]
  %.5 = phi i32 [ %.4, %true_block52 ], [ %246, %true_block56 ], [ %.4, %false_block53 ]
  %243 = fsub reassoc ninf nsz float %64, %123
  %244 = fmul reassoc ninf nsz float %.089, %243
  %245 = fcmp reassoc ninf nsz ogt float %244, %202
  br i1 %245, label %true_block60, label %false_block61

true_block56:                                     ; preds = %false_block53
  %246 = add nuw nsw i32 %.4, 1
  %247 = fsub reassoc ninf nsz float %.4111, %235
  br label %after_if54

true_block60:                                     ; preds = %after_if54
  %248 = add nuw nsw i32 %.596, 1
  %249 = fadd reassoc ninf nsz float %.5112, %243
  br label %after_if62

false_block61:                                    ; preds = %after_if54
  %neg63 = fneg reassoc ninf nsz float %202
  %250 = fcmp reassoc ninf nsz olt float %244, %neg63
  br i1 %250, label %true_block64, label %after_if62

after_if62:                                       ; preds = %true_block64, %false_block61, %true_block60
  %.6113 = phi float [ %249, %true_block60 ], [ %255, %true_block64 ], [ %.5112, %false_block61 ]
  %.697 = phi i32 [ %248, %true_block60 ], [ %.596, %true_block64 ], [ %.596, %false_block61 ]
  %.6 = phi i32 [ %.5, %true_block60 ], [ %254, %true_block64 ], [ %.5, %false_block61 ]
  %251 = fsub reassoc ninf nsz float %64, %133
  %252 = fmul reassoc ninf nsz float %.089, %251
  %253 = fcmp reassoc ninf nsz ogt float %252, %202
  br i1 %253, label %true_block68, label %false_block69

true_block64:                                     ; preds = %false_block61
  %254 = add nuw nsw i32 %.5, 1
  %255 = fsub reassoc ninf nsz float %.5112, %243
  br label %after_if62

true_block68:                                     ; preds = %after_if62
  %256 = add nuw nsw i32 %.697, 1
  %257 = fadd reassoc ninf nsz float %.6113, %251
  br label %after_if70

false_block69:                                    ; preds = %after_if62
  %neg71 = fneg reassoc ninf nsz float %202
  %258 = fcmp reassoc ninf nsz olt float %252, %neg71
  br i1 %258, label %true_block72, label %after_if70

after_if70:                                       ; preds = %true_block72, %false_block69, %true_block68
  %.7114 = phi float [ %257, %true_block68 ], [ %263, %true_block72 ], [ %.6113, %false_block69 ]
  %.798 = phi i32 [ %256, %true_block68 ], [ %.697, %true_block72 ], [ %.697, %false_block69 ]
  %.7 = phi i32 [ %.6, %true_block68 ], [ %262, %true_block72 ], [ %.6, %false_block69 ]
  %259 = fsub reassoc ninf nsz float %64, %138
  %260 = fmul reassoc ninf nsz float %.089, %259
  %261 = fcmp reassoc ninf nsz ogt float %260, %202
  br i1 %261, label %true_block76, label %false_block77

true_block72:                                     ; preds = %false_block69
  %262 = add nuw nsw i32 %.6, 1
  %263 = fsub reassoc ninf nsz float %.6113, %251
  br label %after_if70

true_block76:                                     ; preds = %after_if70
  %264 = add nuw nsw i32 %.798, 1
  %265 = fadd reassoc ninf nsz float %.7114, %259
  br label %after_if78

false_block77:                                    ; preds = %after_if70
  %neg79 = fneg reassoc ninf nsz float %202
  %266 = fcmp reassoc ninf nsz olt float %260, %neg79
  br i1 %266, label %true_block80, label %after_if78

after_if78:                                       ; preds = %true_block80, %false_block77, %true_block76
  %.8115 = phi float [ %265, %true_block76 ], [ %271, %true_block80 ], [ %.7114, %false_block77 ]
  %.899 = phi i32 [ %264, %true_block76 ], [ %.798, %true_block80 ], [ %.798, %false_block77 ]
  %.8 = phi i32 [ %.7, %true_block76 ], [ %270, %true_block80 ], [ %.7, %false_block77 ]
  %267 = fsub reassoc ninf nsz float %64, %144
  %268 = fmul reassoc ninf nsz float %.089, %267
  %269 = fcmp reassoc ninf nsz ogt float %268, %202
  br i1 %269, label %true_block84, label %false_block85

true_block80:                                     ; preds = %false_block77
  %270 = add nuw nsw i32 %.7, 1
  %271 = fsub reassoc ninf nsz float %.7114, %259
  br label %after_if78

true_block84:                                     ; preds = %after_if78
  %272 = add nuw nsw i32 %.899, 1
  %273 = fadd reassoc ninf nsz float %.8115, %267
  br label %after_if86

false_block85:                                    ; preds = %after_if78
  %neg87 = fneg reassoc ninf nsz float %202
  %274 = fcmp reassoc ninf nsz olt float %268, %neg87
  br i1 %274, label %true_block88, label %after_if86

after_if86:                                       ; preds = %true_block88, %false_block85, %true_block84
  %.9116 = phi float [ %273, %true_block84 ], [ %279, %true_block88 ], [ %.8115, %false_block85 ]
  %.9100 = phi i32 [ %272, %true_block84 ], [ %.899, %true_block88 ], [ %.899, %false_block85 ]
  %.9 = phi i32 [ %.8, %true_block84 ], [ %278, %true_block88 ], [ %.8, %false_block85 ]
  %275 = fsub reassoc ninf nsz float %64, %150
  %276 = fmul reassoc ninf nsz float %.089, %275
  %277 = fcmp reassoc ninf nsz ogt float %276, %202
  br i1 %277, label %true_block92, label %false_block93

true_block88:                                     ; preds = %false_block85
  %278 = add nuw nsw i32 %.8, 1
  %279 = fsub reassoc ninf nsz float %.8115, %267
  br label %after_if86

true_block92:                                     ; preds = %after_if86
  %280 = add nuw nsw i32 %.9100, 1
  %281 = fadd reassoc ninf nsz float %.9116, %275
  br label %after_if94

false_block93:                                    ; preds = %after_if86
  %neg95 = fneg reassoc ninf nsz float %202
  %282 = fcmp reassoc ninf nsz olt float %276, %neg95
  br i1 %282, label %true_block96, label %after_if94

after_if94:                                       ; preds = %true_block96, %false_block93, %true_block92
  %.10117 = phi float [ %281, %true_block92 ], [ %287, %true_block96 ], [ %.9116, %false_block93 ]
  %.10101 = phi i32 [ %280, %true_block92 ], [ %.9100, %true_block96 ], [ %.9100, %false_block93 ]
  %.10 = phi i32 [ %.9, %true_block92 ], [ %286, %true_block96 ], [ %.9, %false_block93 ]
  %283 = fsub reassoc ninf nsz float %64, %156
  %284 = fmul reassoc ninf nsz float %.089, %283
  %285 = fcmp reassoc ninf nsz ogt float %284, %202
  br i1 %285, label %true_block100, label %false_block101

true_block96:                                     ; preds = %false_block93
  %286 = add nuw nsw i32 %.9, 1
  %287 = fsub reassoc ninf nsz float %.9116, %275
  br label %after_if94

true_block100:                                    ; preds = %after_if94
  %288 = add nuw nsw i32 %.10101, 1
  %289 = fadd reassoc ninf nsz float %.10117, %283
  br label %after_if102

false_block101:                                   ; preds = %after_if94
  %neg103 = fneg reassoc ninf nsz float %202
  %290 = fcmp reassoc ninf nsz olt float %284, %neg103
  br i1 %290, label %true_block104, label %after_if102

after_if102:                                      ; preds = %true_block104, %false_block101, %true_block100
  %.11118 = phi float [ %289, %true_block100 ], [ %295, %true_block104 ], [ %.10117, %false_block101 ]
  %.11102 = phi i32 [ %288, %true_block100 ], [ %.10101, %true_block104 ], [ %.10101, %false_block101 ]
  %.11 = phi i32 [ %.10, %true_block100 ], [ %294, %true_block104 ], [ %.10, %false_block101 ]
  %291 = fsub reassoc ninf nsz float %64, %162
  %292 = fmul reassoc ninf nsz float %.089, %291
  %293 = fcmp reassoc ninf nsz ogt float %292, %202
  br i1 %293, label %true_block108, label %false_block109

true_block104:                                    ; preds = %false_block101
  %294 = add nuw nsw i32 %.10, 1
  %295 = fsub reassoc ninf nsz float %.10117, %283
  br label %after_if102

true_block108:                                    ; preds = %after_if102
  %296 = add nuw nsw i32 %.11102, 1
  %297 = fadd reassoc ninf nsz float %.11118, %291
  br label %after_if110

false_block109:                                   ; preds = %after_if102
  %neg111 = fneg reassoc ninf nsz float %202
  %298 = fcmp reassoc ninf nsz olt float %292, %neg111
  br i1 %298, label %true_block112, label %after_if110

after_if110:                                      ; preds = %true_block112, %false_block109, %true_block108
  %.12119 = phi float [ %297, %true_block108 ], [ %303, %true_block112 ], [ %.11118, %false_block109 ]
  %.12103 = phi i32 [ %296, %true_block108 ], [ %.11102, %true_block112 ], [ %.11102, %false_block109 ]
  %.12 = phi i32 [ %.11, %true_block108 ], [ %302, %true_block112 ], [ %.11, %false_block109 ]
  %299 = fsub reassoc ninf nsz float %64, %168
  %300 = fmul reassoc ninf nsz float %.089, %299
  %301 = fcmp reassoc ninf nsz ogt float %300, %202
  br i1 %301, label %true_block116, label %false_block117

true_block112:                                    ; preds = %false_block109
  %302 = add nuw nsw i32 %.11, 1
  %303 = fsub reassoc ninf nsz float %.11118, %291
  br label %after_if110

true_block116:                                    ; preds = %after_if110
  %304 = add nuw nsw i32 %.12103, 1
  %305 = fadd reassoc ninf nsz float %.12119, %299
  br label %after_if118

false_block117:                                   ; preds = %after_if110
  %neg119 = fneg reassoc ninf nsz float %202
  %306 = fcmp reassoc ninf nsz olt float %300, %neg119
  br i1 %306, label %true_block120, label %after_if118

after_if118:                                      ; preds = %true_block120, %false_block117, %true_block116
  %.13120 = phi float [ %305, %true_block116 ], [ %311, %true_block120 ], [ %.12119, %false_block117 ]
  %.13104 = phi i32 [ %304, %true_block116 ], [ %.12103, %true_block120 ], [ %.12103, %false_block117 ]
  %.13 = phi i32 [ %.12, %true_block116 ], [ %310, %true_block120 ], [ %.12, %false_block117 ]
  %307 = fsub reassoc ninf nsz float %64, %174
  %308 = fmul reassoc ninf nsz float %.089, %307
  %309 = fcmp reassoc ninf nsz ogt float %308, %202
  br i1 %309, label %true_block124, label %false_block125

true_block120:                                    ; preds = %false_block117
  %310 = add nuw nsw i32 %.12, 1
  %311 = fsub reassoc ninf nsz float %.12119, %299
  br label %after_if118

true_block124:                                    ; preds = %after_if118
  %312 = add nuw nsw i32 %.13104, 1
  %313 = fadd reassoc ninf nsz float %.13120, %307
  br label %after_if126

false_block125:                                   ; preds = %after_if118
  %neg127 = fneg reassoc ninf nsz float %202
  %314 = fcmp reassoc ninf nsz olt float %308, %neg127
  br i1 %314, label %true_block128, label %after_if126

after_if126:                                      ; preds = %true_block128, %false_block125, %true_block124
  %.14121 = phi float [ %313, %true_block124 ], [ %319, %true_block128 ], [ %.13120, %false_block125 ]
  %.14105 = phi i32 [ %312, %true_block124 ], [ %.13104, %true_block128 ], [ %.13104, %false_block125 ]
  %.14 = phi i32 [ %.13, %true_block124 ], [ %318, %true_block128 ], [ %.13, %false_block125 ]
  %315 = fsub reassoc ninf nsz float %64, %180
  %316 = fmul reassoc ninf nsz float %.089, %315
  %317 = fcmp reassoc ninf nsz ogt float %316, %202
  br i1 %317, label %true_block132, label %false_block133

true_block128:                                    ; preds = %false_block125
  %318 = add nuw nsw i32 %.13, 1
  %319 = fsub reassoc ninf nsz float %.13120, %307
  br label %after_if126

true_block132:                                    ; preds = %after_if126
  %320 = add nuw nsw i32 %.14105, 1
  %321 = fadd reassoc ninf nsz float %.14121, %315
  br label %after_if134

false_block133:                                   ; preds = %after_if126
  %neg135 = fneg reassoc ninf nsz float %202
  %322 = fcmp reassoc ninf nsz olt float %316, %neg135
  br i1 %322, label %true_block136, label %after_if134

after_if134:                                      ; preds = %true_block136, %false_block133, %true_block132
  %.15122 = phi float [ %321, %true_block132 ], [ %332, %true_block136 ], [ %.14121, %false_block133 ]
  %.15106 = phi i32 [ %320, %true_block132 ], [ %.14105, %true_block136 ], [ %.14105, %false_block133 ]
  %.15 = phi i32 [ %.14, %true_block132 ], [ %331, %true_block136 ], [ %.14, %false_block133 ]
  %323 = fadd reassoc ninf nsz float %181, 0x3F9EB851E0000000
  %324 = fcmp reassoc ninf nsz ogt float %64, %323
  %325 = fsub reassoc ninf nsz float %64, %181
  %326 = fmul reassoc ninf nsz float %325, 1.000000e+01
  %327 = select i1 %324, float %326, float -0.000000e+00
  %.16123 = fadd reassoc ninf nsz float %.15122, %327
  %328 = icmp ugt i32 %.15106, 8
  %329 = select i1 %324, i1 true, i1 %328
  %330 = icmp ugt i32 %.15, 8
  %.0 = select i1 %329, i1 true, i1 %330
  %.088 = select i1 %.0, float %.16123, float 0.000000e+00
  br label %after_if9

true_block136:                                    ; preds = %false_block133
  %331 = add nuw nsw i32 %.14, 1
  %332 = fsub reassoc ninf nsz float %.14121, %315
  br label %after_if134
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.6**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.6*, %struct.RuntimeContext.6** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.6*, i8*, i32)*, void (%struct.RuntimeContext.6*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.6*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.6*, i8*)*, void (%struct.RuntimeContext.6*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.6* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.6* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.6* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.6*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.6* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: argmemonly mustprogress nocallback nofree nounwind willreturn
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #5

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
