; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.96*, void (%struct.RuntimeContext.96*, i8*)*, void (%struct.RuntimeContext.96*, i8*, i32)*, void (%struct.RuntimeContext.96*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.96 = type { i8*, %struct.LLVMRuntime.95*, i32, i64* }
%struct.LLVMRuntime.95 = type { %struct.PreallocatedMemoryChunk.91, %struct.PreallocatedMemoryChunk.91, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.92*], [1024 x %struct.NodeManager.93*], [1024 x i8*], i8*, %struct.RandState.94*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.91 = type { i8*, i8*, i64 }
%struct.ListManager.92 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.95* }
%struct.NodeManager.93 = type { %struct.LLVMRuntime.95*, i32, i32, i32, i32, %struct.ListManager.92*, %struct.ListManager.92*, %struct.ListManager.92*, i32 }
%struct.RandState.94 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_dcb_highlight_ratio_propagate_c722_0_kernel_0_serial(%struct.RuntimeContext.96* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.96* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %11, i64 0, i32 3
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_highlight_ratio_propagate_c722_0_kernel_1_range_for(%struct.RuntimeContext.96* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.96* %context, %struct.RuntimeContext.96** %4, align 8
  store void (%struct.RuntimeContext.96*, i8*)* null, void (%struct.RuntimeContext.96*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.96*, i8*, i32)* @function_body, void (%struct.RuntimeContext.96*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.96*, i8*)* null, void (%struct.RuntimeContext.96*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.96* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.96* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 0, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if, %for_loop_body.lr.ph
  %.091198 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %110, %after_if ]
  %26 = load %struct.LLVMRuntime.95*, %struct.LLVMRuntime.95** %3, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.95, %struct.LLVMRuntime.95* %26, i64 0, i32 14
  %28 = load i8*, i8** %27, align 8
  %29 = getelementptr inbounds i8, i8* %28, i64 4
  %30 = bitcast i8* %29 to i32*
  %31 = load i32, i32* %30, align 4
  %32 = sdiv i32 %.091198, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.091198
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.091198, 0
  %37 = icmp ne i32 %.091198, %33
  %38 = and i1 %36, %35
  %39 = and i1 %38, %37
  %.neg132 = sext i1 %39 to i32
  %40 = add i32 %32, %.neg132
  %41 = mul i32 %40, %31
  %42 = sub i32 %.091198, %41
  %43 = mul i32 %31, -1
  %44 = mul i32 %43, %40
  %45 = add i32 %.091198, %44
  %46 = load float*, float** %23, align 8
  %47 = load i32, i32* %24, align 4
  %48 = load i32, i32* %25, align 4
  %49 = mul i32 %40, %47
  %50 = sub i32 %47, %31
  %51 = mul i32 %50, %40
  %52 = add i32 %.091198, %51
  %53 = mul i32 %52, %48
  %54 = add i32 %53, 2
  %55 = sext i32 %54 to i64
  %56 = getelementptr float, float* %46, i64 %55
  %57 = load float, float* %56, align 4
  %58 = fcmp reassoc ninf nsz ogt float %57, 0.000000e+00
  br i1 %58, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %59 = sext i32 %53 to i64
  %60 = getelementptr float, float* %46, i64 %59
  %61 = load float, float* %60, align 4
  %62 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %63 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %62, i64 0, i32 1, i32 1
  %64 = load float*, float** %63, align 8
  %65 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %62, i64 0, i32 1, i32 0, i32 1
  %66 = load i32, i32* %65, align 4
  %67 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %62, i64 0, i32 1, i32 0, i32 2
  %68 = load i32, i32* %67, align 4
  %69 = sub i32 %66, %31
  %70 = mul i32 %69, %40
  %71 = add i32 %.091198, %70
  %72 = mul i32 %71, %68
  %73 = sext i32 %72 to i64
  %74 = getelementptr float, float* %64, i64 %73
  store float %61, float* %74, align 4
  %75 = load float*, float** %23, align 8
  %76 = load i32, i32* %24, align 4
  %77 = load i32, i32* %25, align 4
  %78 = sub i32 %76, %31
  %79 = mul i32 %78, %40
  %80 = add i32 %.091198, %79
  %81 = mul i32 %80, %77
  %82 = add i32 %81, 1
  %83 = sext i32 %82 to i64
  %84 = getelementptr float, float* %75, i64 %83
  %85 = load float, float* %84, align 4
  %86 = load float*, float** %63, align 8
  %87 = load i32, i32* %65, align 4
  %88 = load i32, i32* %67, align 4
  %89 = sub i32 %87, %31
  %90 = mul i32 %89, %40
  %91 = add i32 %.091198, %90
  %92 = mul i32 %91, %88
  %93 = add i32 %92, 1
  %94 = sext i32 %93 to i64
  %95 = getelementptr float, float* %86, i64 %94
  store float %85, float* %95, align 4
  %96 = load float, float* %56, align 4
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %97 = add i32 %40, -1
  %98 = add i32 %45, -1
  %99 = icmp sgt i32 %97, -1
  br i1 %99, label %true_block1, label %after_if27

after_if:                                         ; preds = %after_if117, %true_block
  %.sink215 = phi float** [ %318, %after_if117 ], [ %63, %true_block ]
  %.sink214 = phi i32* [ %320, %after_if117 ], [ %65, %true_block ]
  %.sink213 = phi i32* [ %322, %after_if117 ], [ %67, %true_block ]
  %.sink = phi float [ %342, %after_if117 ], [ %96, %true_block ]
  %100 = load float*, float** %.sink215, align 8
  %101 = load i32, i32* %.sink214, align 4
  %102 = load i32, i32* %.sink213, align 4
  %103 = sub i32 %101, %31
  %104 = mul i32 %103, %40
  %105 = add i32 %.091198, %104
  %106 = mul i32 %105, %102
  %107 = add i32 %106, 2
  %108 = sext i32 %107 to i64
  %109 = getelementptr float, float* %100, i64 %108
  store float %.sink, float* %109, align 4
  %110 = add nsw i32 %.091198, 1
  %exitcond.not = icmp eq i32 %19, %110
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block1:                                      ; preds = %false_block
  %111 = getelementptr inbounds i8, i8* %28, i64 8
  %112 = bitcast i8* %111 to i32*
  %113 = load i32, i32* %112, align 4
  %114 = icmp slt i32 %97, %113
  %115 = icmp sgt i32 %98, -1
  %or.cond = select i1 %114, i1 %115, i1 false
  br i1 %or.cond, label %true_block7, label %true_block16

true_block7:                                      ; preds = %true_block1
  %116 = getelementptr inbounds i8, i8* %28, i64 12
  %117 = bitcast i8* %116 to i32*
  %118 = load i32, i32* %117, align 4
  %119 = icmp slt i32 %98, %118
  br i1 %119, label %true_block10, label %true_block16

true_block10:                                     ; preds = %true_block7
  %120 = mul i32 %97, %47
  %121 = sub i32 %120, %41
  %122 = add i32 %.091198, %121
  %123 = add i32 %122, -1
  %124 = mul i32 %123, %48
  %125 = add i32 %124, 2
  %126 = sext i32 %125 to i64
  %127 = getelementptr float, float* %46, i64 %126
  %128 = load float, float* %127, align 4
  %129 = fcmp reassoc ninf nsz ogt float %128, 0.000000e+00
  br i1 %129, label %true_block13, label %true_block16

true_block13:                                     ; preds = %true_block10
  %130 = sext i32 %124 to i64
  %131 = getelementptr float, float* %46, i64 %130
  %132 = load float, float* %131, align 4
  %133 = fmul reassoc ninf nsz float %132, 0x3FE6A09E60000000
  %134 = add i32 %124, 1
  %135 = sext i32 %134 to i64
  %136 = getelementptr float, float* %46, i64 %135
  %137 = load float, float* %136, align 4
  %138 = fmul reassoc ninf nsz float %137, 0x3FE6A09E60000000
  br label %true_block16

true_block16:                                     ; preds = %true_block13, %true_block10, %true_block7, %true_block1
  %.083.ph = phi float [ 0.000000e+00, %true_block1 ], [ 0.000000e+00, %true_block7 ], [ 0.000000e+00, %true_block10 ], [ %133, %true_block13 ]
  %.075.ph = phi float [ 0.000000e+00, %true_block1 ], [ 0.000000e+00, %true_block7 ], [ 0.000000e+00, %true_block10 ], [ %138, %true_block13 ]
  %.074.ph = phi float [ 0.000000e+00, %true_block1 ], [ 0.000000e+00, %true_block7 ], [ 0.000000e+00, %true_block10 ], [ 0x3FE6A09E60000000, %true_block13 ]
  %139 = icmp sgt i32 %45, -1
  %or.cond149 = select i1 %114, i1 %139, i1 false
  br i1 %or.cond149, label %true_block22, label %true_block31

true_block22:                                     ; preds = %true_block16
  %140 = getelementptr inbounds i8, i8* %28, i64 12
  %141 = bitcast i8* %140 to i32*
  %142 = load i32, i32* %141, align 4
  %143 = icmp slt i32 %45, %142
  br i1 %143, label %true_block25, label %true_block31

true_block25:                                     ; preds = %true_block22
  %144 = mul i32 %97, %47
  %145 = sub i32 %144, %41
  %146 = add i32 %.091198, %145
  %147 = mul i32 %146, %48
  %148 = add i32 %147, 2
  %149 = sext i32 %148 to i64
  %150 = getelementptr float, float* %46, i64 %149
  %151 = load float, float* %150, align 4
  %152 = fcmp reassoc ninf nsz ogt float %151, 0.000000e+00
  br i1 %152, label %true_block28, label %true_block31

after_if27:                                       ; preds = %false_block
  %153 = add i32 %42, 1
  br label %after_if42

true_block28:                                     ; preds = %true_block25
  %154 = sext i32 %147 to i64
  %155 = getelementptr float, float* %46, i64 %154
  %156 = load float, float* %155, align 4
  %157 = fadd reassoc ninf nsz float %156, %.083.ph
  %158 = add i32 %147, 1
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, float* %46, i64 %159
  %161 = load float, float* %160, align 4
  %162 = fadd reassoc ninf nsz float %161, %.075.ph
  %163 = fadd reassoc ninf nsz float %.074.ph, 1.000000e+00
  br label %true_block31

true_block31:                                     ; preds = %true_block28, %true_block25, %true_block22, %true_block16
  %.184.ph = phi float [ %.083.ph, %true_block16 ], [ %.083.ph, %true_block22 ], [ %.083.ph, %true_block25 ], [ %157, %true_block28 ]
  %.176.ph = phi float [ %.075.ph, %true_block16 ], [ %.075.ph, %true_block22 ], [ %.075.ph, %true_block25 ], [ %162, %true_block28 ]
  %.1.ph = phi float [ %.074.ph, %true_block16 ], [ %.074.ph, %true_block22 ], [ %.074.ph, %true_block25 ], [ %163, %true_block28 ]
  %164 = add i32 %45, 1
  %165 = icmp sgt i32 %164, -1
  %or.cond150 = select i1 %114, i1 %165, i1 false
  br i1 %or.cond150, label %true_block37, label %true_block31.after_if42_crit_edge

true_block31.after_if42_crit_edge:                ; preds = %true_block31
  br label %after_if42

true_block37:                                     ; preds = %true_block31
  %166 = getelementptr inbounds i8, i8* %28, i64 12
  %167 = bitcast i8* %166 to i32*
  %168 = load i32, i32* %167, align 4
  %169 = icmp slt i32 %164, %168
  br i1 %169, label %true_block40, label %true_block37.true_block46_crit_edge

true_block37.true_block46_crit_edge:              ; preds = %true_block37
  br label %true_block46

true_block40:                                     ; preds = %true_block37
  %170 = mul i32 %97, %47
  %171 = sub i32 %170, %41
  %172 = add i32 %.091198, %171
  %173 = add i32 %172, 1
  %174 = mul i32 %173, %48
  %175 = add i32 %174, 2
  %176 = sext i32 %175 to i64
  %177 = getelementptr float, float* %46, i64 %176
  %178 = load float, float* %177, align 4
  %179 = fcmp reassoc ninf nsz ogt float %178, 0.000000e+00
  br i1 %179, label %true_block43, label %true_block40.true_block46_crit_edge

true_block40.true_block46_crit_edge:              ; preds = %true_block40
  br label %true_block46

after_if42:                                       ; preds = %true_block31.after_if42_crit_edge, %after_if27
  %180 = phi i32 [ %153, %after_if27 ], [ %164, %true_block31.after_if42_crit_edge ]
  %.285 = phi float [ 0.000000e+00, %after_if27 ], [ %.184.ph, %true_block31.after_if42_crit_edge ]
  %.277 = phi float [ 0.000000e+00, %after_if27 ], [ %.176.ph, %true_block31.after_if42_crit_edge ]
  %.2 = phi float [ 0.000000e+00, %after_if27 ], [ %.1.ph, %true_block31.after_if42_crit_edge ]
  %181 = icmp sgt i32 %40, -1
  br i1 %181, label %after_if42.true_block46_crit_edge, label %after_if72

after_if42.true_block46_crit_edge:                ; preds = %after_if42
  %.phi.trans.insert = getelementptr inbounds i8, i8* %28, i64 8
  %.phi.trans.insert199 = bitcast i8* %.phi.trans.insert to i32*
  %.pre = load i32, i32* %.phi.trans.insert199, align 4
  br label %true_block46

true_block43:                                     ; preds = %true_block40
  %182 = sext i32 %174 to i64
  %183 = getelementptr float, float* %46, i64 %182
  %184 = load float, float* %183, align 4
  %185 = fmul reassoc ninf nsz float %184, 0x3FE6A09E60000000
  %186 = fadd reassoc ninf nsz float %185, %.184.ph
  %187 = add i32 %174, 1
  %188 = sext i32 %187 to i64
  %189 = getelementptr float, float* %46, i64 %188
  %190 = load float, float* %189, align 4
  %191 = fmul reassoc ninf nsz float %190, 0x3FE6A09E60000000
  %192 = fadd reassoc ninf nsz float %191, %.176.ph
  %193 = fadd reassoc ninf nsz float %.1.ph, 0x3FE6A09E60000000
  br label %true_block46

true_block46:                                     ; preds = %true_block43, %after_if42.true_block46_crit_edge, %true_block40.true_block46_crit_edge, %true_block37.true_block46_crit_edge
  %194 = phi i32 [ %.pre, %after_if42.true_block46_crit_edge ], [ %113, %true_block37.true_block46_crit_edge ], [ %113, %true_block40.true_block46_crit_edge ], [ %113, %true_block43 ]
  %.2173 = phi float [ %.2, %after_if42.true_block46_crit_edge ], [ %.1.ph, %true_block37.true_block46_crit_edge ], [ %.1.ph, %true_block40.true_block46_crit_edge ], [ %193, %true_block43 ]
  %.277172 = phi float [ %.277, %after_if42.true_block46_crit_edge ], [ %.176.ph, %true_block37.true_block46_crit_edge ], [ %.176.ph, %true_block40.true_block46_crit_edge ], [ %192, %true_block43 ]
  %.285171 = phi float [ %.285, %after_if42.true_block46_crit_edge ], [ %.184.ph, %true_block37.true_block46_crit_edge ], [ %.184.ph, %true_block40.true_block46_crit_edge ], [ %186, %true_block43 ]
  %195 = phi i32 [ %180, %after_if42.true_block46_crit_edge ], [ %164, %true_block37.true_block46_crit_edge ], [ %164, %true_block40.true_block46_crit_edge ], [ %164, %true_block43 ]
  %196 = icmp slt i32 %40, %194
  %197 = icmp sgt i32 %98, -1
  %or.cond151 = select i1 %196, i1 %197, i1 false
  br i1 %or.cond151, label %true_block52, label %true_block61

true_block52:                                     ; preds = %true_block46
  %198 = getelementptr inbounds i8, i8* %28, i64 12
  %199 = bitcast i8* %198 to i32*
  %200 = load i32, i32* %199, align 4
  %201 = icmp slt i32 %98, %200
  br i1 %201, label %true_block55, label %true_block61

true_block55:                                     ; preds = %true_block52
  %202 = add i32 %52, -1
  %203 = mul i32 %202, %48
  %204 = add i32 %203, 2
  %205 = sext i32 %204 to i64
  %206 = getelementptr float, float* %46, i64 %205
  %207 = load float, float* %206, align 4
  %208 = fcmp reassoc ninf nsz ogt float %207, 0.000000e+00
  br i1 %208, label %true_block58, label %true_block61

true_block58:                                     ; preds = %true_block55
  %209 = sext i32 %203 to i64
  %210 = getelementptr float, float* %46, i64 %209
  %211 = load float, float* %210, align 4
  %212 = fadd reassoc ninf nsz float %211, %.285171
  %213 = add i32 %203, 1
  %214 = sext i32 %213 to i64
  %215 = getelementptr float, float* %46, i64 %214
  %216 = load float, float* %215, align 4
  %217 = fadd reassoc ninf nsz float %216, %.277172
  %218 = fadd reassoc ninf nsz float %.2173, 1.000000e+00
  br label %true_block61

true_block61:                                     ; preds = %true_block58, %true_block55, %true_block52, %true_block46
  %.3179 = phi float [ %218, %true_block58 ], [ %.2173, %true_block46 ], [ %.2173, %true_block55 ], [ %.2173, %true_block52 ]
  %.378178 = phi float [ %217, %true_block58 ], [ %.277172, %true_block46 ], [ %.277172, %true_block55 ], [ %.277172, %true_block52 ]
  %.386177 = phi float [ %212, %true_block58 ], [ %.285171, %true_block46 ], [ %.285171, %true_block55 ], [ %.285171, %true_block52 ]
  %219 = icmp sgt i32 %195, -1
  %or.cond152 = select i1 %196, i1 %219, i1 false
  br i1 %or.cond152, label %true_block67, label %after_if72

true_block67:                                     ; preds = %true_block61
  %220 = getelementptr inbounds i8, i8* %28, i64 12
  %221 = bitcast i8* %220 to i32*
  %222 = load i32, i32* %221, align 4
  %223 = icmp slt i32 %195, %222
  br i1 %223, label %true_block70, label %after_if72.thread

true_block70:                                     ; preds = %true_block67
  %224 = add i32 %195, %49
  %225 = mul i32 %224, %48
  %226 = add i32 %225, 2
  %227 = sext i32 %226 to i64
  %228 = getelementptr float, float* %46, i64 %227
  %229 = load float, float* %228, align 4
  %230 = fcmp reassoc ninf nsz ogt float %229, 0.000000e+00
  br i1 %230, label %true_block73, label %after_if72.thread

after_if72.thread:                                ; preds = %true_block73, %true_block70, %true_block67
  %.487.ph = phi float [ %.386177, %true_block67 ], [ %.386177, %true_block70 ], [ %238, %true_block73 ]
  %.479.ph = phi float [ %.378178, %true_block67 ], [ %.378178, %true_block70 ], [ %243, %true_block73 ]
  %.4.ph = phi float [ %.3179, %true_block67 ], [ %.3179, %true_block70 ], [ %244, %true_block73 ]
  %231 = add nuw nsw i32 %40, 1
  br label %true_block76

after_if72:                                       ; preds = %true_block61, %after_if42
  %232 = phi i32 [ %195, %true_block61 ], [ %180, %after_if42 ]
  %.487 = phi float [ %.386177, %true_block61 ], [ %.285, %after_if42 ]
  %.479 = phi float [ %.378178, %true_block61 ], [ %.277, %after_if42 ]
  %.4 = phi float [ %.3179, %true_block61 ], [ %.2, %after_if42 ]
  %233 = add i32 %40, 1
  %234 = icmp sgt i32 %233, -1
  br i1 %234, label %after_if72.true_block76_crit_edge, label %after_if117

after_if72.true_block76_crit_edge:                ; preds = %after_if72
  %.phi.trans.insert200 = getelementptr inbounds i8, i8* %28, i64 8
  %.phi.trans.insert201 = bitcast i8* %.phi.trans.insert200 to i32*
  %.pre202 = load i32, i32* %.phi.trans.insert201, align 4
  br label %true_block76

true_block73:                                     ; preds = %true_block70
  %235 = sext i32 %225 to i64
  %236 = getelementptr float, float* %46, i64 %235
  %237 = load float, float* %236, align 4
  %238 = fadd reassoc ninf nsz float %237, %.386177
  %239 = add i32 %225, 1
  %240 = sext i32 %239 to i64
  %241 = getelementptr float, float* %46, i64 %240
  %242 = load float, float* %241, align 4
  %243 = fadd reassoc ninf nsz float %242, %.378178
  %244 = fadd reassoc ninf nsz float %.3179, 1.000000e+00
  br label %after_if72.thread

true_block76:                                     ; preds = %after_if72.true_block76_crit_edge, %after_if72.thread
  %245 = phi i32 [ %194, %after_if72.thread ], [ %.pre202, %after_if72.true_block76_crit_edge ]
  %246 = phi i32 [ %231, %after_if72.thread ], [ %233, %after_if72.true_block76_crit_edge ]
  %.4185 = phi float [ %.4.ph, %after_if72.thread ], [ %.4, %after_if72.true_block76_crit_edge ]
  %.479184 = phi float [ %.479.ph, %after_if72.thread ], [ %.479, %after_if72.true_block76_crit_edge ]
  %.487183 = phi float [ %.487.ph, %after_if72.thread ], [ %.487, %after_if72.true_block76_crit_edge ]
  %247 = phi i32 [ %195, %after_if72.thread ], [ %232, %after_if72.true_block76_crit_edge ]
  %248 = icmp slt i32 %246, %245
  %249 = icmp sgt i32 %98, -1
  %or.cond153 = select i1 %248, i1 %249, i1 false
  br i1 %or.cond153, label %true_block82, label %true_block91

true_block82:                                     ; preds = %true_block76
  %250 = getelementptr inbounds i8, i8* %28, i64 12
  %251 = bitcast i8* %250 to i32*
  %252 = load i32, i32* %251, align 4
  %253 = icmp slt i32 %98, %252
  br i1 %253, label %true_block85, label %true_block91

true_block85:                                     ; preds = %true_block82
  %254 = mul i32 %246, %47
  %255 = sub i32 %254, %41
  %256 = add i32 %.091198, %255
  %257 = add i32 %256, -1
  %258 = mul i32 %257, %48
  %259 = add i32 %258, 2
  %260 = sext i32 %259 to i64
  %261 = getelementptr float, float* %46, i64 %260
  %262 = load float, float* %261, align 4
  %263 = fcmp reassoc ninf nsz ogt float %262, 0.000000e+00
  br i1 %263, label %true_block88, label %true_block91

true_block88:                                     ; preds = %true_block85
  %264 = sext i32 %258 to i64
  %265 = getelementptr float, float* %46, i64 %264
  %266 = load float, float* %265, align 4
  %267 = fmul reassoc ninf nsz float %266, 0x3FE6A09E60000000
  %268 = fadd reassoc ninf nsz float %267, %.487183
  %269 = add i32 %258, 1
  %270 = sext i32 %269 to i64
  %271 = getelementptr float, float* %46, i64 %270
  %272 = load float, float* %271, align 4
  %273 = fmul reassoc ninf nsz float %272, 0x3FE6A09E60000000
  %274 = fadd reassoc ninf nsz float %273, %.479184
  %275 = fadd reassoc ninf nsz float %.4185, 0x3FE6A09E60000000
  br label %true_block91

true_block91:                                     ; preds = %true_block88, %true_block85, %true_block82, %true_block76
  %.5191 = phi float [ %275, %true_block88 ], [ %.4185, %true_block76 ], [ %.4185, %true_block85 ], [ %.4185, %true_block82 ]
  %.580190 = phi float [ %274, %true_block88 ], [ %.479184, %true_block76 ], [ %.479184, %true_block85 ], [ %.479184, %true_block82 ]
  %.588189 = phi float [ %268, %true_block88 ], [ %.487183, %true_block76 ], [ %.487183, %true_block85 ], [ %.487183, %true_block82 ]
  %276 = icmp sgt i32 %45, -1
  %or.cond154 = select i1 %248, i1 %276, i1 false
  br i1 %or.cond154, label %true_block97, label %true_block106

true_block97:                                     ; preds = %true_block91
  %277 = getelementptr inbounds i8, i8* %28, i64 12
  %278 = bitcast i8* %277 to i32*
  %279 = load i32, i32* %278, align 4
  %280 = icmp slt i32 %45, %279
  br i1 %280, label %true_block100, label %true_block106

true_block100:                                    ; preds = %true_block97
  %281 = mul i32 %246, %47
  %282 = sub i32 %281, %41
  %283 = add i32 %.091198, %282
  %284 = mul i32 %283, %48
  %285 = add i32 %284, 2
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, float* %46, i64 %286
  %288 = load float, float* %287, align 4
  %289 = fcmp reassoc ninf nsz ogt float %288, 0.000000e+00
  br i1 %289, label %true_block103, label %true_block106

true_block103:                                    ; preds = %true_block100
  %290 = sext i32 %284 to i64
  %291 = getelementptr float, float* %46, i64 %290
  %292 = load float, float* %291, align 4
  %293 = fadd reassoc ninf nsz float %292, %.588189
  %294 = add i32 %284, 1
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, float* %46, i64 %295
  %297 = load float, float* %296, align 4
  %298 = fadd reassoc ninf nsz float %297, %.580190
  %299 = fadd reassoc ninf nsz float %.5191, 1.000000e+00
  br label %true_block106

true_block106:                                    ; preds = %true_block103, %true_block100, %true_block97, %true_block91
  %.689.ph = phi float [ %.588189, %true_block91 ], [ %.588189, %true_block97 ], [ %.588189, %true_block100 ], [ %293, %true_block103 ]
  %.681.ph = phi float [ %.580190, %true_block91 ], [ %.580190, %true_block97 ], [ %.580190, %true_block100 ], [ %298, %true_block103 ]
  %.6.ph = phi float [ %.5191, %true_block91 ], [ %.5191, %true_block97 ], [ %.5191, %true_block100 ], [ %299, %true_block103 ]
  %300 = icmp sgt i32 %247, -1
  %or.cond155 = select i1 %248, i1 %300, i1 false
  br i1 %or.cond155, label %true_block112, label %after_if117

true_block112:                                    ; preds = %true_block106
  %301 = getelementptr inbounds i8, i8* %28, i64 12
  %302 = bitcast i8* %301 to i32*
  %303 = load i32, i32* %302, align 4
  %304 = icmp slt i32 %247, %303
  br i1 %304, label %true_block115, label %after_if117

true_block115:                                    ; preds = %true_block112
  %305 = mul i32 %246, %47
  %306 = add i32 %247, %305
  %307 = mul i32 %306, %48
  %308 = add i32 %307, 2
  %309 = sext i32 %308 to i64
  %310 = getelementptr float, float* %46, i64 %309
  %311 = load float, float* %310, align 4
  %312 = fcmp reassoc ninf nsz ogt float %311, 0.000000e+00
  br i1 %312, label %true_block118, label %after_if117

after_if117:                                      ; preds = %true_block118, %true_block115, %true_block112, %true_block106, %after_if72
  %.790 = phi float [ %347, %true_block118 ], [ %.689.ph, %true_block115 ], [ %.689.ph, %true_block112 ], [ %.689.ph, %true_block106 ], [ %.487, %after_if72 ]
  %.782 = phi float [ %353, %true_block118 ], [ %.681.ph, %true_block115 ], [ %.681.ph, %true_block112 ], [ %.681.ph, %true_block106 ], [ %.479, %after_if72 ]
  %.7 = phi float [ %354, %true_block118 ], [ %.6.ph, %true_block115 ], [ %.6.ph, %true_block112 ], [ %.6.ph, %true_block106 ], [ %.4, %after_if72 ]
  %313 = fcmp reassoc ninf nsz ogt float %.7, 0.000000e+00
  %314 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.7, float 0x3EE4F8B580000000)
  %315 = fdiv reassoc ninf nsz float %.790, %314
  %316 = select reassoc ninf nsz i1 %313, float %315, float 1.000000e+00
  %317 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }** %20, align 8
  %318 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %317, i64 0, i32 1, i32 1
  %319 = load float*, float** %318, align 8
  %320 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %317, i64 0, i32 1, i32 0, i32 1
  %321 = load i32, i32* %320, align 4
  %322 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, i32, i32 }* %317, i64 0, i32 1, i32 0, i32 2
  %323 = load i32, i32* %322, align 4
  %324 = sub i32 %321, %31
  %325 = mul i32 %324, %40
  %326 = add i32 %.091198, %325
  %327 = mul i32 %326, %323
  %328 = sext i32 %327 to i64
  %329 = getelementptr float, float* %319, i64 %328
  store float %316, float* %329, align 4
  %330 = fdiv reassoc ninf nsz float %.782, %314
  %331 = select reassoc ninf nsz i1 %313, float %330, float 1.000000e+00
  %332 = load float*, float** %318, align 8
  %333 = load i32, i32* %320, align 4
  %334 = load i32, i32* %322, align 4
  %335 = sub i32 %333, %31
  %336 = mul i32 %335, %40
  %337 = add i32 %.091198, %336
  %338 = mul i32 %337, %334
  %339 = add i32 %338, 1
  %340 = sext i32 %339 to i64
  %341 = getelementptr float, float* %332, i64 %340
  store float %331, float* %341, align 4
  %342 = select reassoc ninf nsz i1 %313, float 1.000000e+00, float 0.000000e+00
  br label %after_if

true_block118:                                    ; preds = %true_block115
  %343 = sext i32 %307 to i64
  %344 = getelementptr float, float* %46, i64 %343
  %345 = load float, float* %344, align 4
  %346 = fmul reassoc ninf nsz float %345, 0x3FE6A09E60000000
  %347 = fadd reassoc ninf nsz float %346, %.689.ph
  %348 = add i32 %307, 1
  %349 = sext i32 %348 to i64
  %350 = getelementptr float, float* %46, i64 %349
  %351 = load float, float* %350, align 4
  %352 = fmul reassoc ninf nsz float %351, 0x3FE6A09E60000000
  %353 = fadd reassoc ninf nsz float %352, %.681.ph
  %354 = fadd reassoc ninf nsz float %.6.ph, 0x3FE6A09E60000000
  br label %after_if117
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.96, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.96**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.96*, %struct.RuntimeContext.96** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.96*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.96*, i8*)*, void (%struct.RuntimeContext.96*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.96*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.96*, i8*, i32)*, void (%struct.RuntimeContext.96*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.96*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.96*, i8*)*, void (%struct.RuntimeContext.96*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.96*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.96* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.96* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.96* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.96, %struct.RuntimeContext.96* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.96* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.96* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.96*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.96* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
