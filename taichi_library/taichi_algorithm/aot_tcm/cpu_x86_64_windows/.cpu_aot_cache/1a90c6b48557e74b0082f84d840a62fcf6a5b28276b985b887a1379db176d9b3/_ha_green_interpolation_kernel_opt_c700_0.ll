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
define void @_ha_green_interpolation_kernel_opt_c700_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 3
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
define void @_ha_green_interpolation_kernel_opt_c700_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %21 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }**
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if12, %for_loop_body.lr.ph
  %.054112 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %81, %after_if12 ]
  %22 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %23 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %22, i64 0, i32 14
  %24 = load i8*, i8** %23, align 8
  %25 = getelementptr inbounds i8, i8* %24, i64 4
  %26 = bitcast i8* %25 to i32*
  %27 = load i32, i32* %26, align 4
  %28 = sdiv i32 %.054112, %27
  %29 = mul i32 %28, %27
  %30 = xor i32 %27, %.054112
  %31 = icmp slt i32 %30, 0
  %32 = icmp ne i32 %.054112, 0
  %33 = icmp ne i32 %.054112, %29
  %34 = and i1 %32, %31
  %35 = and i1 %34, %33
  %.neg81 = sext i1 %35 to i32
  %36 = add i32 %28, %.neg81
  %37 = mul i32 %36, %27
  %38 = mul i32 %27, -1
  %39 = mul i32 %38, %36
  %40 = add i32 %.054112, %39
  %41 = insertelement <2 x i32> poison, i32 %40, i64 0
  %42 = insertelement <2 x i32> %41, i32 %36, i64 1
  %43 = sdiv <2 x i32> %42, <i32 2, i32 2>
  %44 = icmp slt <2 x i32> %42, zeroinitializer
  %45 = shl nsw <2 x i32> %43, <i32 1, i32 1>
  %46 = icmp ne <2 x i32> %45, %42
  %47 = and <2 x i1> %44, %46
  %48 = zext <2 x i1> %47 to <2 x i32>
  %49 = sub nsw <2 x i32> %48, %43
  %50 = shl <2 x i32> %49, <i32 1, i32 1>
  %51 = sub <2 x i32> zeroinitializer, %42
  %52 = icmp eq <2 x i32> %50, %51
  %53 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }** %21, align 8
  %54 = extractelement <2 x i1> %52, i64 1
  br i1 %54, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if12
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %55 = extractelement <2 x i1> %52, i64 0
  br i1 %55, label %true_block1, label %false_block2

false_block:                                      ; preds = %for_loop_body
  %56 = extractelement <2 x i1> %52, i64 0
  br i1 %56, label %true_block4, label %false_block5

after_if:                                         ; preds = %false_block5, %true_block4, %false_block2, %true_block1
  %.053.in = phi i32* [ %57, %true_block1 ], [ %58, %false_block2 ], [ %59, %true_block4 ], [ %60, %false_block5 ]
  %.053 = load i32, i32* %.053.in, align 4
  switch i32 %.053, label %false_block11 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

true_block1:                                      ; preds = %true_block
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 4
  br label %after_if

false_block2:                                     ; preds = %true_block
  %58 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 5
  br label %after_if

true_block4:                                      ; preds = %false_block
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 6
  br label %after_if

false_block5:                                     ; preds = %false_block
  %60 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 7
  br label %after_if

true_block10:                                     ; preds = %after_if, %after_if
  %61 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 1
  %62 = load float*, float** %61, align 8
  %63 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 0, i32 1
  %64 = load i32, i32* %63, align 4
  %65 = sub i32 %64, %27
  %66 = mul i32 %65, %36
  %67 = add i32 %.054112, %66
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, float* %62, i64 %68
  %70 = load float, float* %69, align 4
  br label %after_if12

false_block11:                                    ; preds = %after_if
  %71 = icmp sgt i32 %36, 1
  br i1 %71, label %true_block13, label %false_block23

after_if12:                                       ; preds = %after_if78, %false_block29, %true_block28, %true_block25, %true_block10
  %.sink = phi float [ %179, %true_block28 ], [ %183, %false_block29 ], [ %174, %true_block25 ], [ %274, %after_if78 ], [ %70, %true_block10 ]
  %72 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 1, i32 1
  %73 = load float*, float** %72, align 8
  %74 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 1, i32 0, i32 1
  %75 = load i32, i32* %74, align 4
  %76 = sub i32 %75, %27
  %77 = mul i32 %76, %36
  %78 = add i32 %.054112, %77
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, float* %73, i64 %79
  store float %.sink, float* %80, align 4
  %81 = add nsw i32 %.054112, 1
  %exitcond.not = icmp eq i32 %19, %81
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block13:                                     ; preds = %false_block11
  %82 = getelementptr inbounds i8, i8* %24, i64 8
  %83 = bitcast i8* %82 to i32*
  %84 = load i32, i32* %83, align 4
  %85 = add i32 %84, -2
  %86 = icmp slt i32 %36, %85
  %87 = icmp sgt i32 %40, 1
  %or.cond = select i1 %86, i1 %87, i1 false
  br i1 %or.cond, label %true_block19, label %false_block23.thread

true_block19:                                     ; preds = %true_block13
  %88 = getelementptr inbounds i8, i8* %24, i64 12
  %89 = bitcast i8* %88 to i32*
  %90 = load i32, i32* %89, align 4
  %91 = add i32 %90, -2
  %92 = icmp slt i32 %40, %91
  br i1 %92, label %true_block22, label %false_block23.thread

true_block22:                                     ; preds = %true_block19
  %93 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 1
  %94 = load float*, float** %93, align 8
  %95 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 0, i32 1
  %96 = load i32, i32* %95, align 4
  %97 = sub i32 %96, %27
  %98 = mul i32 %97, %36
  %99 = add i32 %.054112, %98
  %100 = add i32 %99, -1
  %101 = sext i32 %100 to i64
  %102 = getelementptr float, float* %94, i64 %101
  %103 = load float, float* %102, align 4
  %104 = add i32 %99, 1
  %105 = sext i32 %104 to i64
  %106 = getelementptr float, float* %94, i64 %105
  %107 = load float, float* %106, align 4
  %108 = fsub reassoc ninf nsz float %103, %107
  %109 = tail call float @llvm.fabs.f32(float %108)
  %110 = sext i32 %99 to i64
  %111 = getelementptr float, float* %94, i64 %110
  %112 = load float, float* %111, align 4
  %factor = fmul reassoc ninf nsz float %112, 2.000000e+00
  %113 = add i32 %99, -2
  %114 = sext i32 %113 to i64
  %115 = getelementptr float, float* %94, i64 %114
  %116 = load float, float* %115, align 4
  %117 = add i32 %99, 2
  %118 = sext i32 %117 to i64
  %119 = getelementptr float, float* %94, i64 %118
  %120 = load float, float* %119, align 4
  %121 = fadd reassoc ninf nsz float %120, %116
  %122 = fsub reassoc ninf nsz float %factor, %121
  %123 = tail call float @llvm.fabs.f32(float %122)
  %124 = fadd reassoc ninf nsz float %123, %109
  %125 = add nsw i32 %36, -1
  %126 = mul i32 %96, %125
  %127 = sub i32 %126, %37
  %128 = add i32 %.054112, %127
  %129 = sext i32 %128 to i64
  %130 = getelementptr float, float* %94, i64 %129
  %131 = load float, float* %130, align 4
  %132 = add nuw nsw i32 %36, 1
  %133 = mul i32 %96, %132
  %134 = sub i32 %133, %37
  %135 = add i32 %.054112, %134
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, float* %94, i64 %136
  %138 = load float, float* %137, align 4
  %139 = fsub reassoc ninf nsz float %131, %138
  %140 = tail call float @llvm.fabs.f32(float %139)
  %141 = add nsw i32 %36, -2
  %142 = mul i32 %96, %141
  %143 = sub i32 %142, %37
  %144 = add i32 %.054112, %143
  %145 = sext i32 %144 to i64
  %146 = getelementptr float, float* %94, i64 %145
  %147 = load float, float* %146, align 4
  %148 = add nuw i32 %36, 2
  %149 = mul i32 %96, %148
  %150 = sub i32 %149, %37
  %151 = add i32 %.054112, %150
  %152 = sext i32 %151 to i64
  %153 = getelementptr float, float* %94, i64 %152
  %154 = load float, float* %153, align 4
  %155 = fadd reassoc ninf nsz float %147, %154
  %156 = fsub reassoc ninf nsz float %factor, %155
  %157 = tail call float @llvm.fabs.f32(float %156)
  %158 = fadd reassoc ninf nsz float %157, %140
  %159 = fsub reassoc ninf nsz float %124, %158
  %160 = tail call float @llvm.fabs.f32(float %159)
  %161 = fcmp reassoc ninf nsz olt float %160, 0x3FA1EB8520000000
  br i1 %161, label %true_block25, label %false_block26

false_block23.thread:                             ; preds = %true_block19, %true_block13
  %162 = add nsw i32 %36, -1
  br label %true_block31

false_block23:                                    ; preds = %false_block11
  %163 = add i32 %36, -1
  %164 = icmp sgt i32 %163, -1
  br i1 %164, label %false_block23.true_block31_crit_edge, label %after_if42

false_block23.true_block31_crit_edge:             ; preds = %false_block23
  %.phi.trans.insert = getelementptr inbounds i8, i8* %24, i64 8
  %.phi.trans.insert113 = bitcast i8* %.phi.trans.insert to i32*
  %.pre = load i32, i32* %.phi.trans.insert113, align 4
  br label %true_block31

true_block25:                                     ; preds = %true_block22
  %165 = fadd reassoc ninf nsz float %107, %103
  %166 = fadd reassoc ninf nsz float %165, %131
  %167 = fadd reassoc ninf nsz float %166, %138
  %168 = fmul reassoc ninf nsz float %167, 2.500000e-01
  %169 = fmul reassoc ninf nsz float %112, 4.000000e+00
  %170 = fadd reassoc ninf nsz float %121, %147
  %171 = fadd reassoc ninf nsz float %170, %154
  %172 = fsub reassoc ninf nsz float %169, %171
  %173 = fmul reassoc ninf nsz float %172, 1.250000e-01
  %174 = fadd reassoc ninf nsz float %173, %168
  br label %after_if12

false_block26:                                    ; preds = %true_block22
  %175 = fcmp reassoc ninf nsz olt float %124, %158
  br i1 %175, label %true_block28, label %false_block29

true_block28:                                     ; preds = %false_block26
  %176 = fadd reassoc ninf nsz float %107, %103
  %177 = fmul reassoc ninf nsz float %176, 5.000000e-01
  %178 = fmul reassoc ninf nsz float %122, 2.500000e-01
  %179 = fadd reassoc ninf nsz float %178, %177
  br label %after_if12

false_block29:                                    ; preds = %false_block26
  %180 = fadd reassoc ninf nsz float %138, %131
  %181 = fmul reassoc ninf nsz float %180, 5.000000e-01
  %182 = fmul reassoc ninf nsz float %156, 2.500000e-01
  %183 = fadd reassoc ninf nsz float %182, %181
  br label %after_if12

true_block31:                                     ; preds = %false_block23.true_block31_crit_edge, %false_block23.thread
  %184 = phi i32 [ %84, %false_block23.thread ], [ %.pre, %false_block23.true_block31_crit_edge ]
  %185 = phi i32 [ %162, %false_block23.thread ], [ %163, %false_block23.true_block31_crit_edge ]
  %186 = icmp slt i32 %185, %184
  %187 = icmp sgt i32 %40, -1
  %or.cond98 = select i1 %186, i1 %187, i1 false
  br i1 %or.cond98, label %true_block37, label %after_if42

true_block37:                                     ; preds = %true_block31
  %188 = getelementptr inbounds i8, i8* %24, i64 12
  %189 = bitcast i8* %188 to i32*
  %190 = load i32, i32* %189, align 4
  %191 = icmp slt i32 %40, %190
  br i1 %191, label %true_block40, label %after_if42

true_block40:                                     ; preds = %true_block37
  %192 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 1
  %193 = load float*, float** %192, align 8
  %194 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 0, i32 1
  %195 = load i32, i32* %194, align 4
  %196 = mul i32 %195, %185
  %197 = sub i32 %196, %37
  %198 = add i32 %.054112, %197
  %199 = sext i32 %198 to i64
  %200 = getelementptr float, float* %193, i64 %199
  %201 = load float, float* %200, align 4
  %202 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %201, i64 0
  br label %after_if42

after_if42:                                       ; preds = %true_block40, %true_block37, %true_block31, %false_block23
  %203 = phi <2 x float> [ %202, %true_block40 ], [ zeroinitializer, %true_block37 ], [ zeroinitializer, %false_block23 ], [ zeroinitializer, %true_block31 ]
  %204 = add i32 %36, 1
  %205 = icmp sgt i32 %204, -1
  br i1 %205, label %true_block43, label %after_if54

true_block43:                                     ; preds = %after_if42
  %206 = getelementptr inbounds i8, i8* %24, i64 8
  %207 = bitcast i8* %206 to i32*
  %208 = load i32, i32* %207, align 4
  %209 = icmp slt i32 %204, %208
  %210 = icmp sgt i32 %40, -1
  %or.cond99 = select i1 %209, i1 %210, i1 false
  br i1 %or.cond99, label %true_block49, label %after_if54

true_block49:                                     ; preds = %true_block43
  %211 = getelementptr inbounds i8, i8* %24, i64 12
  %212 = bitcast i8* %211 to i32*
  %213 = load i32, i32* %212, align 4
  %214 = icmp slt i32 %40, %213
  br i1 %214, label %true_block52, label %after_if54

true_block52:                                     ; preds = %true_block49
  %215 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 1
  %216 = load float*, float** %215, align 8
  %217 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 0, i32 1
  %218 = load i32, i32* %217, align 4
  %219 = mul i32 %218, %204
  %220 = sub i32 %219, %37
  %221 = add i32 %.054112, %220
  %222 = sext i32 %221 to i64
  %223 = getelementptr float, float* %216, i64 %222
  %224 = load float, float* %223, align 4
  %225 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %224, i64 0
  %226 = fadd reassoc ninf nsz <2 x float> %225, %203
  br label %after_if54

after_if54:                                       ; preds = %true_block52, %true_block49, %true_block43, %after_if42
  %227 = phi <2 x float> [ %226, %true_block52 ], [ %203, %true_block49 ], [ %203, %after_if42 ], [ %203, %true_block43 ]
  %228 = add i32 %40, -1
  %229 = icmp sgt i32 %36, -1
  br i1 %229, label %true_block55, label %after_if78

true_block55:                                     ; preds = %after_if54
  %230 = getelementptr inbounds i8, i8* %24, i64 8
  %231 = bitcast i8* %230 to i32*
  %232 = load i32, i32* %231, align 4
  %233 = icmp slt i32 %36, %232
  %234 = icmp sgt i32 %228, -1
  %or.cond100 = select i1 %233, i1 %234, i1 false
  br i1 %or.cond100, label %true_block61, label %true_block67

true_block61:                                     ; preds = %true_block55
  %235 = getelementptr inbounds i8, i8* %24, i64 12
  %236 = bitcast i8* %235 to i32*
  %237 = load i32, i32* %236, align 4
  %238 = icmp slt i32 %228, %237
  br i1 %238, label %true_block64, label %true_block67

true_block64:                                     ; preds = %true_block61
  %239 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 1
  %240 = load float*, float** %239, align 8
  %241 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 0, i32 1
  %242 = load i32, i32* %241, align 4
  %243 = sub i32 %242, %27
  %244 = mul i32 %243, %36
  %245 = add i32 %.054112, %244
  %246 = add i32 %245, -1
  %247 = sext i32 %246 to i64
  %248 = getelementptr float, float* %240, i64 %247
  %249 = load float, float* %248, align 4
  %250 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %249, i64 0
  %251 = fadd reassoc ninf nsz <2 x float> %250, %227
  br label %true_block67

true_block67:                                     ; preds = %true_block64, %true_block61, %true_block55
  %252 = phi <2 x float> [ %227, %true_block55 ], [ %227, %true_block61 ], [ %251, %true_block64 ]
  %253 = add i32 %40, 1
  %254 = icmp sgt i32 %253, -1
  %or.cond101 = select i1 %233, i1 %254, i1 false
  br i1 %or.cond101, label %true_block73, label %after_if78

true_block73:                                     ; preds = %true_block67
  %255 = getelementptr inbounds i8, i8* %24, i64 12
  %256 = bitcast i8* %255 to i32*
  %257 = load i32, i32* %256, align 4
  %258 = icmp slt i32 %253, %257
  br i1 %258, label %true_block76, label %after_if78

true_block76:                                     ; preds = %true_block73
  %259 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 1
  %260 = load float*, float** %259, align 8
  %261 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32, i32, i32, i32, i32 }* %53, i64 0, i32 0, i32 0, i32 1
  %262 = load i32, i32* %261, align 4
  %263 = sub i32 %262, %27
  %264 = mul i32 %263, %36
  %265 = add i32 %.054112, %264
  %266 = add i32 %265, 1
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, float* %260, i64 %267
  %269 = load float, float* %268, align 4
  %270 = insertelement <2 x float> <float poison, float 1.000000e+00>, float %269, i64 0
  %271 = fadd reassoc ninf nsz <2 x float> %270, %252
  br label %after_if78

after_if78:                                       ; preds = %true_block76, %true_block73, %true_block67, %after_if54
  %272 = phi <2 x float> [ %271, %true_block76 ], [ %252, %true_block73 ], [ %252, %true_block67 ], [ %227, %after_if54 ]
  %shift = shufflevector <2 x float> %272, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %273 = fdiv reassoc ninf nsz <2 x float> %272, %shift
  %274 = extractelement <2 x float> %273, i64 0
  br label %after_if12
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.fabs.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
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
