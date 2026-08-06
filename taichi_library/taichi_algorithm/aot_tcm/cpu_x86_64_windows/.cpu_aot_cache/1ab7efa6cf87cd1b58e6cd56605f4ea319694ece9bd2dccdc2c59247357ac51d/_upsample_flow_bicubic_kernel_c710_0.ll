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
define void @_upsample_flow_bicubic_kernel_c710_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }**
  %1 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %11 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %10, i64 0, i32 0, i32 0, i32 1
  %12 = load i32, i32* %11, align 4
  %13 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 12
  %17 = bitcast i8* %16 to i32*
  store i32 %12, i32* %17, align 4
  %18 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %0, align 8
  %19 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %18, i64 0, i32 1, i32 0, i32 0
  %20 = load i32, i32* %19, align 4
  %21 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %18, i64 0, i32 1, i32 0, i32 1
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
define void @_upsample_flow_bicubic_kernel_c710_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }**
  %21 = load { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }*, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 2
  %23 = load float, float* %22, align 4
  %24 = icmp slt i32 %17, %19
  br i1 %24, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %25 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 0, i32 1
  %26 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 0, i32 0, i32 2
  %28 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 1, i32 0, i32 1
  %30 = getelementptr { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }, { { { i32, i32, i32 }, float* }, { { i32, i32, i32 }, float* }, float }* %21, i64 0, i32 1, i32 0, i32 2
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if378, %for_loop_body.lr.ph
  %.0130626 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %991, %after_if378 ]
  %31 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %32 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %31, i64 0, i32 14
  %33 = load i8*, i8** %32, align 8
  %34 = getelementptr inbounds i8, i8* %33, i64 4
  %35 = bitcast i8* %34 to i32*
  %36 = load i32, i32* %35, align 4
  %37 = sdiv i32 %.0130626, %36
  %38 = mul i32 %37, %36
  %39 = xor i32 %36, %.0130626
  %40 = icmp slt i32 %39, 0
  %41 = icmp ne i32 %.0130626, 0
  %42 = icmp ne i32 %.0130626, %38
  %43 = and i1 %41, %40
  %44 = and i1 %43, %42
  %.neg244 = sext i1 %44 to i32
  %45 = add i32 %37, %.neg244
  %46 = mul i32 %36, -1
  %47 = mul i32 %46, %45
  %48 = add i32 %.0130626, %47
  %49 = sitofp i32 %45 to float
  %50 = fdiv reassoc ninf nsz float %49, %23
  %51 = sitofp i32 %48 to float
  %52 = fdiv reassoc ninf nsz float %51, %23
  %53 = tail call reassoc ninf nsz float @llvm.floor.f32(float %50)
  %54 = fptosi float %53 to i32
  %55 = tail call reassoc ninf nsz float @llvm.floor.f32(float %52)
  %56 = fptosi float %55 to i32
  %57 = sitofp i32 %54 to float
  %58 = fsub reassoc ninf nsz float %50, %57
  %59 = sitofp i32 %56 to float
  %60 = fsub reassoc ninf nsz float %52, %59
  %61 = add i32 %54, -1
  %62 = getelementptr inbounds i8, i8* %33, i64 8
  %63 = bitcast i8* %62 to i32*
  %64 = load i32, i32* %63, align 4
  %65 = add i32 %64, -1
  %66 = tail call i32 @llvm.smin.i32(i32 %61, i32 %65)
  %67 = tail call i32 @llvm.smax.i32(i32 %66, i32 0)
  %68 = add i32 %56, -1
  %69 = getelementptr inbounds i8, i8* %33, i64 12
  %70 = bitcast i8* %69 to i32*
  %71 = load i32, i32* %70, align 4
  %72 = add i32 %71, -1
  %73 = tail call i32 @llvm.smin.i32(i32 %68, i32 %72)
  %74 = tail call i32 @llvm.smax.i32(i32 %73, i32 0)
  %75 = fsub reassoc ninf nsz float -1.000000e+00, %58
  %76 = tail call float @llvm.fabs.f32(float %75)
  %77 = fcmp reassoc ninf nsz ole float %76, 1.000000e+00
  br i1 %77, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if378
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %78 = fmul reassoc ninf nsz float %75, %75
  %79 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add = fadd reassoc ninf nsz float %79, -2.500000e+00
  %reass.mul247 = fmul reassoc ninf nsz float %78, %reass.add
  %80 = fadd reassoc ninf nsz float %reass.mul247, 1.000000e+00
  br label %after_if

false_block:                                      ; preds = %for_loop_body
  %81 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %81, label %true_block1, label %after_if

after_if:                                         ; preds = %true_block1, %false_block, %true_block
  %.0129 = phi float [ %80, %true_block ], [ %89, %true_block1 ], [ 0.000000e+00, %false_block ]
  %82 = fsub reassoc ninf nsz float -1.000000e+00, %60
  %83 = tail call float @llvm.fabs.f32(float %82)
  %84 = fcmp reassoc ninf nsz ole float %83, 1.000000e+00
  br i1 %84, label %true_block4, label %false_block5

true_block1:                                      ; preds = %false_block
  %85 = fmul reassoc ninf nsz float %75, %75
  %86 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg245 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %87 = fsub reassoc ninf nsz float 2.500000e+00, %86
  %reass.mul = fmul reassoc ninf nsz float %85, %87
  %88 = fadd reassoc ninf nsz float %.neg245, 2.000000e+00
  %89 = fadd reassoc ninf nsz float %88, %reass.mul
  br label %after_if

true_block4:                                      ; preds = %after_if
  %90 = fmul reassoc ninf nsz float %82, %82
  %91 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add252 = fadd reassoc ninf nsz float %91, -2.500000e+00
  %reass.mul253 = fmul reassoc ninf nsz float %90, %reass.add252
  %92 = fadd reassoc ninf nsz float %reass.mul253, 1.000000e+00
  br label %after_if6

false_block5:                                     ; preds = %after_if
  %93 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %93, label %true_block7, label %after_if6

after_if6:                                        ; preds = %true_block7, %false_block5, %true_block4
  %.0128 = phi float [ %92, %true_block4 ], [ %111, %true_block7 ], [ 0.000000e+00, %false_block5 ]
  %94 = load float*, float** %25, align 8
  %95 = load i32, i32* %26, align 4
  %96 = load i32, i32* %27, align 4
  %97 = mul i32 %95, %67
  %98 = add i32 %97, %74
  %99 = mul i32 %98, %96
  %100 = sext i32 %99 to i64
  %101 = getelementptr float, float* %94, i64 %100
  %102 = load float, float* %101, align 4
  %103 = fmul reassoc ninf nsz float %.0128, %.0129
  %104 = fmul reassoc ninf nsz float %103, %102
  %105 = tail call i32 @llvm.smin.i32(i32 %56, i32 %72)
  %106 = tail call i32 @llvm.smax.i32(i32 %105, i32 0)
  br i1 %77, label %true_block10, label %false_block11

true_block7:                                      ; preds = %false_block5
  %107 = fmul reassoc ninf nsz float %82, %82
  %108 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg248 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %109 = fsub reassoc ninf nsz float 2.500000e+00, %108
  %reass.mul250 = fmul reassoc ninf nsz float %107, %109
  %110 = fadd reassoc ninf nsz float %.neg248, 2.000000e+00
  %111 = fadd reassoc ninf nsz float %110, %reass.mul250
  br label %after_if6

true_block10:                                     ; preds = %after_if6
  %112 = fmul reassoc ninf nsz float %75, %75
  %113 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add258 = fadd reassoc ninf nsz float %113, -2.500000e+00
  %reass.mul259 = fmul reassoc ninf nsz float %112, %reass.add258
  %114 = fadd reassoc ninf nsz float %reass.mul259, 1.000000e+00
  br label %after_if12

false_block11:                                    ; preds = %after_if6
  %115 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %115, label %true_block13, label %after_if12

after_if12:                                       ; preds = %true_block13, %false_block11, %true_block10
  %.0127 = phi float [ %114, %true_block10 ], [ %123, %true_block13 ], [ 0.000000e+00, %false_block11 ]
  %116 = fneg reassoc ninf nsz float %60
  %117 = tail call float @llvm.fabs.f32(float %116)
  %118 = fcmp reassoc ninf nsz ole float %117, 1.000000e+00
  br i1 %118, label %true_block16, label %false_block17

true_block13:                                     ; preds = %false_block11
  %119 = fmul reassoc ninf nsz float %75, %75
  %120 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg254 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %121 = fsub reassoc ninf nsz float 2.500000e+00, %120
  %reass.mul256 = fmul reassoc ninf nsz float %119, %121
  %122 = fadd reassoc ninf nsz float %.neg254, 2.000000e+00
  %123 = fadd reassoc ninf nsz float %122, %reass.mul256
  br label %after_if12

true_block16:                                     ; preds = %after_if12
  %124 = fmul reassoc ninf nsz float %60, %60
  %125 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add264 = fadd reassoc ninf nsz float %125, -2.500000e+00
  %reass.mul265 = fmul reassoc ninf nsz float %124, %reass.add264
  %126 = fadd reassoc ninf nsz float %reass.mul265, 1.000000e+00
  br label %after_if18

false_block17:                                    ; preds = %after_if12
  %127 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %127, label %true_block19, label %after_if18

after_if18:                                       ; preds = %true_block19, %false_block17, %true_block16
  %.0126 = phi float [ %126, %true_block16 ], [ %143, %true_block19 ], [ 0.000000e+00, %false_block17 ]
  %128 = add i32 %97, %106
  %129 = mul i32 %128, %96
  %130 = sext i32 %129 to i64
  %131 = getelementptr float, float* %94, i64 %130
  %132 = load float, float* %131, align 4
  %133 = fmul reassoc ninf nsz float %.0126, %.0127
  %134 = fmul reassoc ninf nsz float %133, %132
  %135 = fadd reassoc ninf nsz float %134, %104
  %136 = add i32 %56, 1
  %137 = tail call i32 @llvm.smin.i32(i32 %136, i32 %72)
  %138 = tail call i32 @llvm.smax.i32(i32 %137, i32 0)
  br i1 %77, label %true_block22, label %false_block23

true_block19:                                     ; preds = %false_block17
  %139 = fmul reassoc ninf nsz float %60, %60
  %140 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg260 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %141 = fsub reassoc ninf nsz float 2.500000e+00, %140
  %reass.mul262 = fmul reassoc ninf nsz float %139, %141
  %142 = fadd reassoc ninf nsz float %.neg260, 2.000000e+00
  %143 = fadd reassoc ninf nsz float %142, %reass.mul262
  br label %after_if18

true_block22:                                     ; preds = %after_if18
  %144 = fmul reassoc ninf nsz float %75, %75
  %145 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add270 = fadd reassoc ninf nsz float %145, -2.500000e+00
  %reass.mul271 = fmul reassoc ninf nsz float %144, %reass.add270
  %146 = fadd reassoc ninf nsz float %reass.mul271, 1.000000e+00
  br label %after_if24

false_block23:                                    ; preds = %after_if18
  %147 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %147, label %true_block25, label %after_if24

after_if24:                                       ; preds = %true_block25, %false_block23, %true_block22
  %.0125 = phi float [ %146, %true_block22 ], [ %155, %true_block25 ], [ 0.000000e+00, %false_block23 ]
  %148 = fsub reassoc ninf nsz float 1.000000e+00, %60
  %149 = tail call float @llvm.fabs.f32(float %148)
  %150 = fcmp reassoc ninf nsz ole float %149, 1.000000e+00
  br i1 %150, label %true_block28, label %false_block29

true_block25:                                     ; preds = %false_block23
  %151 = fmul reassoc ninf nsz float %75, %75
  %152 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg266 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %153 = fsub reassoc ninf nsz float 2.500000e+00, %152
  %reass.mul268 = fmul reassoc ninf nsz float %151, %153
  %154 = fadd reassoc ninf nsz float %.neg266, 2.000000e+00
  %155 = fadd reassoc ninf nsz float %154, %reass.mul268
  br label %after_if24

true_block28:                                     ; preds = %after_if24
  %156 = fmul reassoc ninf nsz float %148, %148
  %157 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add276 = fadd reassoc ninf nsz float %157, -2.500000e+00
  %reass.mul277 = fmul reassoc ninf nsz float %156, %reass.add276
  %158 = fadd reassoc ninf nsz float %reass.mul277, 1.000000e+00
  br label %after_if30

false_block29:                                    ; preds = %after_if24
  %159 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %159, label %true_block31, label %after_if30

after_if30:                                       ; preds = %true_block31, %false_block29, %true_block28
  %.0124 = phi float [ %158, %true_block28 ], [ %175, %true_block31 ], [ 0.000000e+00, %false_block29 ]
  %160 = add i32 %97, %138
  %161 = mul i32 %160, %96
  %162 = sext i32 %161 to i64
  %163 = getelementptr float, float* %94, i64 %162
  %164 = load float, float* %163, align 4
  %165 = fmul reassoc ninf nsz float %.0124, %.0125
  %166 = fmul reassoc ninf nsz float %165, %164
  %167 = fadd reassoc ninf nsz float %135, %166
  %168 = add i32 %56, 2
  %169 = tail call i32 @llvm.smin.i32(i32 %168, i32 %72)
  %170 = tail call i32 @llvm.smax.i32(i32 %169, i32 0)
  br i1 %77, label %true_block34, label %false_block35

true_block31:                                     ; preds = %false_block29
  %171 = fmul reassoc ninf nsz float %148, %148
  %172 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg272 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %173 = fsub reassoc ninf nsz float 2.500000e+00, %172
  %reass.mul274 = fmul reassoc ninf nsz float %171, %173
  %174 = fadd reassoc ninf nsz float %.neg272, 2.000000e+00
  %175 = fadd reassoc ninf nsz float %174, %reass.mul274
  br label %after_if30

true_block34:                                     ; preds = %after_if30
  %176 = fmul reassoc ninf nsz float %75, %75
  %177 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add282 = fadd reassoc ninf nsz float %177, -2.500000e+00
  %reass.mul283 = fmul reassoc ninf nsz float %176, %reass.add282
  %178 = fadd reassoc ninf nsz float %reass.mul283, 1.000000e+00
  br label %after_if36

false_block35:                                    ; preds = %after_if30
  %179 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %179, label %true_block37, label %after_if36

after_if36:                                       ; preds = %true_block37, %false_block35, %true_block34
  %.0123 = phi float [ %178, %true_block34 ], [ %187, %true_block37 ], [ 0.000000e+00, %false_block35 ]
  %180 = fsub reassoc ninf nsz float 2.000000e+00, %60
  %181 = tail call float @llvm.fabs.f32(float %180)
  %182 = fcmp reassoc ninf nsz ole float %181, 1.000000e+00
  br i1 %182, label %true_block40, label %false_block41

true_block37:                                     ; preds = %false_block35
  %183 = fmul reassoc ninf nsz float %75, %75
  %184 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg278 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %185 = fsub reassoc ninf nsz float 2.500000e+00, %184
  %reass.mul280 = fmul reassoc ninf nsz float %183, %185
  %186 = fadd reassoc ninf nsz float %.neg278, 2.000000e+00
  %187 = fadd reassoc ninf nsz float %186, %reass.mul280
  br label %after_if36

true_block40:                                     ; preds = %after_if36
  %188 = fmul reassoc ninf nsz float %180, %180
  %189 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add288 = fadd reassoc ninf nsz float %189, -2.500000e+00
  %reass.mul289 = fmul reassoc ninf nsz float %188, %reass.add288
  %190 = fadd reassoc ninf nsz float %reass.mul289, 1.000000e+00
  br label %after_if42

false_block41:                                    ; preds = %after_if36
  %191 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %191, label %true_block43, label %after_if42

after_if42:                                       ; preds = %true_block43, %false_block41, %true_block40
  %.0122 = phi float [ %190, %true_block40 ], [ %209, %true_block43 ], [ 0.000000e+00, %false_block41 ]
  %192 = add i32 %97, %170
  %193 = mul i32 %192, %96
  %194 = sext i32 %193 to i64
  %195 = getelementptr float, float* %94, i64 %194
  %196 = load float, float* %195, align 4
  %197 = fmul reassoc ninf nsz float %.0122, %.0123
  %198 = fmul reassoc ninf nsz float %197, %196
  %199 = fadd reassoc ninf nsz float %167, %198
  %200 = tail call i32 @llvm.smin.i32(i32 %54, i32 %65)
  %201 = tail call i32 @llvm.smax.i32(i32 %200, i32 0)
  %202 = fneg reassoc ninf nsz float %58
  %203 = tail call float @llvm.fabs.f32(float %202)
  %204 = fcmp reassoc ninf nsz ole float %203, 1.000000e+00
  br i1 %204, label %true_block46, label %false_block47

true_block43:                                     ; preds = %false_block41
  %205 = fmul reassoc ninf nsz float %180, %180
  %206 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg284 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %207 = fsub reassoc ninf nsz float 2.500000e+00, %206
  %reass.mul286 = fmul reassoc ninf nsz float %205, %207
  %208 = fadd reassoc ninf nsz float %.neg284, 2.000000e+00
  %209 = fadd reassoc ninf nsz float %208, %reass.mul286
  br label %after_if42

true_block46:                                     ; preds = %after_if42
  %210 = fmul reassoc ninf nsz float %58, %58
  %211 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add294 = fadd reassoc ninf nsz float %211, -2.500000e+00
  %reass.mul295 = fmul reassoc ninf nsz float %210, %reass.add294
  %212 = fadd reassoc ninf nsz float %reass.mul295, 1.000000e+00
  br label %after_if48

false_block47:                                    ; preds = %after_if42
  %213 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %213, label %true_block49, label %after_if48

after_if48:                                       ; preds = %true_block49, %false_block47, %true_block46
  %.0121 = phi float [ %212, %true_block46 ], [ %218, %true_block49 ], [ 0.000000e+00, %false_block47 ]
  br i1 %84, label %true_block52, label %false_block53

true_block49:                                     ; preds = %false_block47
  %214 = fmul reassoc ninf nsz float %58, %58
  %215 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg290 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %216 = fsub reassoc ninf nsz float 2.500000e+00, %215
  %reass.mul292 = fmul reassoc ninf nsz float %214, %216
  %217 = fadd reassoc ninf nsz float %.neg290, 2.000000e+00
  %218 = fadd reassoc ninf nsz float %217, %reass.mul292
  br label %after_if48

true_block52:                                     ; preds = %after_if48
  %219 = fmul reassoc ninf nsz float %82, %82
  %220 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add300 = fadd reassoc ninf nsz float %220, -2.500000e+00
  %reass.mul301 = fmul reassoc ninf nsz float %219, %reass.add300
  %221 = fadd reassoc ninf nsz float %reass.mul301, 1.000000e+00
  br label %after_if54

false_block53:                                    ; preds = %after_if48
  %222 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %222, label %true_block55, label %after_if54

after_if54:                                       ; preds = %true_block55, %false_block53, %true_block52
  %.0120 = phi float [ %221, %true_block52 ], [ %236, %true_block55 ], [ 0.000000e+00, %false_block53 ]
  %223 = mul i32 %95, %201
  %224 = add i32 %223, %74
  %225 = mul i32 %224, %96
  %226 = sext i32 %225 to i64
  %227 = getelementptr float, float* %94, i64 %226
  %228 = load float, float* %227, align 4
  %229 = fmul reassoc ninf nsz float %.0120, %.0121
  %230 = fmul reassoc ninf nsz float %229, %228
  %231 = fadd reassoc ninf nsz float %199, %230
  br i1 %204, label %true_block58, label %false_block59

true_block55:                                     ; preds = %false_block53
  %232 = fmul reassoc ninf nsz float %82, %82
  %233 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg296 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %234 = fsub reassoc ninf nsz float 2.500000e+00, %233
  %reass.mul298 = fmul reassoc ninf nsz float %232, %234
  %235 = fadd reassoc ninf nsz float %.neg296, 2.000000e+00
  %236 = fadd reassoc ninf nsz float %235, %reass.mul298
  br label %after_if54

true_block58:                                     ; preds = %after_if54
  %237 = fmul reassoc ninf nsz float %58, %58
  %238 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add306 = fadd reassoc ninf nsz float %238, -2.500000e+00
  %reass.mul307 = fmul reassoc ninf nsz float %237, %reass.add306
  %239 = fadd reassoc ninf nsz float %reass.mul307, 1.000000e+00
  br label %after_if60

false_block59:                                    ; preds = %after_if54
  %240 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %240, label %true_block61, label %after_if60

after_if60:                                       ; preds = %true_block61, %false_block59, %true_block58
  %.0119 = phi float [ %239, %true_block58 ], [ %245, %true_block61 ], [ 0.000000e+00, %false_block59 ]
  br i1 %118, label %true_block64, label %false_block65

true_block61:                                     ; preds = %false_block59
  %241 = fmul reassoc ninf nsz float %58, %58
  %242 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg302 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %243 = fsub reassoc ninf nsz float 2.500000e+00, %242
  %reass.mul304 = fmul reassoc ninf nsz float %241, %243
  %244 = fadd reassoc ninf nsz float %.neg302, 2.000000e+00
  %245 = fadd reassoc ninf nsz float %244, %reass.mul304
  br label %after_if60

true_block64:                                     ; preds = %after_if60
  %246 = fmul reassoc ninf nsz float %60, %60
  %247 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add312 = fadd reassoc ninf nsz float %247, -2.500000e+00
  %reass.mul313 = fmul reassoc ninf nsz float %246, %reass.add312
  %248 = fadd reassoc ninf nsz float %reass.mul313, 1.000000e+00
  br label %after_if66

false_block65:                                    ; preds = %after_if60
  %249 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %249, label %true_block67, label %after_if66

after_if66:                                       ; preds = %true_block67, %false_block65, %true_block64
  %.0118 = phi float [ %248, %true_block64 ], [ %262, %true_block67 ], [ 0.000000e+00, %false_block65 ]
  %250 = add i32 %223, %106
  %251 = mul i32 %250, %96
  %252 = sext i32 %251 to i64
  %253 = getelementptr float, float* %94, i64 %252
  %254 = load float, float* %253, align 4
  %255 = fmul reassoc ninf nsz float %.0118, %.0119
  %256 = fmul reassoc ninf nsz float %255, %254
  %257 = fadd reassoc ninf nsz float %231, %256
  br i1 %204, label %true_block70, label %false_block71

true_block67:                                     ; preds = %false_block65
  %258 = fmul reassoc ninf nsz float %60, %60
  %259 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg308 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %260 = fsub reassoc ninf nsz float 2.500000e+00, %259
  %reass.mul310 = fmul reassoc ninf nsz float %258, %260
  %261 = fadd reassoc ninf nsz float %.neg308, 2.000000e+00
  %262 = fadd reassoc ninf nsz float %261, %reass.mul310
  br label %after_if66

true_block70:                                     ; preds = %after_if66
  %263 = fmul reassoc ninf nsz float %58, %58
  %264 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add318 = fadd reassoc ninf nsz float %264, -2.500000e+00
  %reass.mul319 = fmul reassoc ninf nsz float %263, %reass.add318
  %265 = fadd reassoc ninf nsz float %reass.mul319, 1.000000e+00
  br label %after_if72

false_block71:                                    ; preds = %after_if66
  %266 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %266, label %true_block73, label %after_if72

after_if72:                                       ; preds = %true_block73, %false_block71, %true_block70
  %.0117 = phi float [ %265, %true_block70 ], [ %271, %true_block73 ], [ 0.000000e+00, %false_block71 ]
  br i1 %150, label %true_block76, label %false_block77

true_block73:                                     ; preds = %false_block71
  %267 = fmul reassoc ninf nsz float %58, %58
  %268 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg314 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %269 = fsub reassoc ninf nsz float 2.500000e+00, %268
  %reass.mul316 = fmul reassoc ninf nsz float %267, %269
  %270 = fadd reassoc ninf nsz float %.neg314, 2.000000e+00
  %271 = fadd reassoc ninf nsz float %270, %reass.mul316
  br label %after_if72

true_block76:                                     ; preds = %after_if72
  %272 = fmul reassoc ninf nsz float %148, %148
  %273 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add324 = fadd reassoc ninf nsz float %273, -2.500000e+00
  %reass.mul325 = fmul reassoc ninf nsz float %272, %reass.add324
  %274 = fadd reassoc ninf nsz float %reass.mul325, 1.000000e+00
  br label %after_if78

false_block77:                                    ; preds = %after_if72
  %275 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %275, label %true_block79, label %after_if78

after_if78:                                       ; preds = %true_block79, %false_block77, %true_block76
  %.0116 = phi float [ %274, %true_block76 ], [ %288, %true_block79 ], [ 0.000000e+00, %false_block77 ]
  %276 = add i32 %223, %138
  %277 = mul i32 %276, %96
  %278 = sext i32 %277 to i64
  %279 = getelementptr float, float* %94, i64 %278
  %280 = load float, float* %279, align 4
  %281 = fmul reassoc ninf nsz float %.0116, %.0117
  %282 = fmul reassoc ninf nsz float %281, %280
  %283 = fadd reassoc ninf nsz float %257, %282
  br i1 %204, label %true_block82, label %false_block83

true_block79:                                     ; preds = %false_block77
  %284 = fmul reassoc ninf nsz float %148, %148
  %285 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg320 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %286 = fsub reassoc ninf nsz float 2.500000e+00, %285
  %reass.mul322 = fmul reassoc ninf nsz float %284, %286
  %287 = fadd reassoc ninf nsz float %.neg320, 2.000000e+00
  %288 = fadd reassoc ninf nsz float %287, %reass.mul322
  br label %after_if78

true_block82:                                     ; preds = %after_if78
  %289 = fmul reassoc ninf nsz float %58, %58
  %290 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add330 = fadd reassoc ninf nsz float %290, -2.500000e+00
  %reass.mul331 = fmul reassoc ninf nsz float %289, %reass.add330
  %291 = fadd reassoc ninf nsz float %reass.mul331, 1.000000e+00
  br label %after_if84

false_block83:                                    ; preds = %after_if78
  %292 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %292, label %true_block85, label %after_if84

after_if84:                                       ; preds = %true_block85, %false_block83, %true_block82
  %.0115 = phi float [ %291, %true_block82 ], [ %297, %true_block85 ], [ 0.000000e+00, %false_block83 ]
  br i1 %182, label %true_block88, label %false_block89

true_block85:                                     ; preds = %false_block83
  %293 = fmul reassoc ninf nsz float %58, %58
  %294 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg326 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %295 = fsub reassoc ninf nsz float 2.500000e+00, %294
  %reass.mul328 = fmul reassoc ninf nsz float %293, %295
  %296 = fadd reassoc ninf nsz float %.neg326, 2.000000e+00
  %297 = fadd reassoc ninf nsz float %296, %reass.mul328
  br label %after_if84

true_block88:                                     ; preds = %after_if84
  %298 = fmul reassoc ninf nsz float %180, %180
  %299 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add336 = fadd reassoc ninf nsz float %299, -2.500000e+00
  %reass.mul337 = fmul reassoc ninf nsz float %298, %reass.add336
  %300 = fadd reassoc ninf nsz float %reass.mul337, 1.000000e+00
  br label %after_if90

false_block89:                                    ; preds = %after_if84
  %301 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %301, label %true_block91, label %after_if90

after_if90:                                       ; preds = %true_block91, %false_block89, %true_block88
  %.0114 = phi float [ %300, %true_block88 ], [ %320, %true_block91 ], [ 0.000000e+00, %false_block89 ]
  %302 = add i32 %223, %170
  %303 = mul i32 %302, %96
  %304 = sext i32 %303 to i64
  %305 = getelementptr float, float* %94, i64 %304
  %306 = load float, float* %305, align 4
  %307 = fmul reassoc ninf nsz float %.0114, %.0115
  %308 = fmul reassoc ninf nsz float %307, %306
  %309 = fadd reassoc ninf nsz float %283, %308
  %310 = add i32 %54, 1
  %311 = tail call i32 @llvm.smin.i32(i32 %310, i32 %65)
  %312 = tail call i32 @llvm.smax.i32(i32 %311, i32 0)
  %313 = fsub reassoc ninf nsz float 1.000000e+00, %58
  %314 = tail call float @llvm.fabs.f32(float %313)
  %315 = fcmp reassoc ninf nsz ole float %314, 1.000000e+00
  br i1 %315, label %true_block94, label %false_block95

true_block91:                                     ; preds = %false_block89
  %316 = fmul reassoc ninf nsz float %180, %180
  %317 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg332 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %318 = fsub reassoc ninf nsz float 2.500000e+00, %317
  %reass.mul334 = fmul reassoc ninf nsz float %316, %318
  %319 = fadd reassoc ninf nsz float %.neg332, 2.000000e+00
  %320 = fadd reassoc ninf nsz float %319, %reass.mul334
  br label %after_if90

true_block94:                                     ; preds = %after_if90
  %321 = fmul reassoc ninf nsz float %313, %313
  %322 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add342 = fadd reassoc ninf nsz float %322, -2.500000e+00
  %reass.mul343 = fmul reassoc ninf nsz float %321, %reass.add342
  %323 = fadd reassoc ninf nsz float %reass.mul343, 1.000000e+00
  br label %after_if96

false_block95:                                    ; preds = %after_if90
  %324 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %324, label %true_block97, label %after_if96

after_if96:                                       ; preds = %true_block97, %false_block95, %true_block94
  %.0113 = phi float [ %323, %true_block94 ], [ %329, %true_block97 ], [ 0.000000e+00, %false_block95 ]
  br i1 %84, label %true_block100, label %false_block101

true_block97:                                     ; preds = %false_block95
  %325 = fmul reassoc ninf nsz float %313, %313
  %326 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg338 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %327 = fsub reassoc ninf nsz float 2.500000e+00, %326
  %reass.mul340 = fmul reassoc ninf nsz float %325, %327
  %328 = fadd reassoc ninf nsz float %.neg338, 2.000000e+00
  %329 = fadd reassoc ninf nsz float %328, %reass.mul340
  br label %after_if96

true_block100:                                    ; preds = %after_if96
  %330 = fmul reassoc ninf nsz float %82, %82
  %331 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add348 = fadd reassoc ninf nsz float %331, -2.500000e+00
  %reass.mul349 = fmul reassoc ninf nsz float %330, %reass.add348
  %332 = fadd reassoc ninf nsz float %reass.mul349, 1.000000e+00
  br label %after_if102

false_block101:                                   ; preds = %after_if96
  %333 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %333, label %true_block103, label %after_if102

after_if102:                                      ; preds = %true_block103, %false_block101, %true_block100
  %.0112 = phi float [ %332, %true_block100 ], [ %347, %true_block103 ], [ 0.000000e+00, %false_block101 ]
  %334 = mul i32 %95, %312
  %335 = add i32 %334, %74
  %336 = mul i32 %335, %96
  %337 = sext i32 %336 to i64
  %338 = getelementptr float, float* %94, i64 %337
  %339 = load float, float* %338, align 4
  %340 = fmul reassoc ninf nsz float %.0112, %.0113
  %341 = fmul reassoc ninf nsz float %340, %339
  %342 = fadd reassoc ninf nsz float %309, %341
  br i1 %315, label %true_block106, label %false_block107

true_block103:                                    ; preds = %false_block101
  %343 = fmul reassoc ninf nsz float %82, %82
  %344 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg344 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %345 = fsub reassoc ninf nsz float 2.500000e+00, %344
  %reass.mul346 = fmul reassoc ninf nsz float %343, %345
  %346 = fadd reassoc ninf nsz float %.neg344, 2.000000e+00
  %347 = fadd reassoc ninf nsz float %346, %reass.mul346
  br label %after_if102

true_block106:                                    ; preds = %after_if102
  %348 = fmul reassoc ninf nsz float %313, %313
  %349 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add354 = fadd reassoc ninf nsz float %349, -2.500000e+00
  %reass.mul355 = fmul reassoc ninf nsz float %348, %reass.add354
  %350 = fadd reassoc ninf nsz float %reass.mul355, 1.000000e+00
  br label %after_if108

false_block107:                                   ; preds = %after_if102
  %351 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %351, label %true_block109, label %after_if108

after_if108:                                      ; preds = %true_block109, %false_block107, %true_block106
  %.0111 = phi float [ %350, %true_block106 ], [ %356, %true_block109 ], [ 0.000000e+00, %false_block107 ]
  br i1 %118, label %true_block112, label %false_block113

true_block109:                                    ; preds = %false_block107
  %352 = fmul reassoc ninf nsz float %313, %313
  %353 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg350 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %354 = fsub reassoc ninf nsz float 2.500000e+00, %353
  %reass.mul352 = fmul reassoc ninf nsz float %352, %354
  %355 = fadd reassoc ninf nsz float %.neg350, 2.000000e+00
  %356 = fadd reassoc ninf nsz float %355, %reass.mul352
  br label %after_if108

true_block112:                                    ; preds = %after_if108
  %357 = fmul reassoc ninf nsz float %60, %60
  %358 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add360 = fadd reassoc ninf nsz float %358, -2.500000e+00
  %reass.mul361 = fmul reassoc ninf nsz float %357, %reass.add360
  %359 = fadd reassoc ninf nsz float %reass.mul361, 1.000000e+00
  br label %after_if114

false_block113:                                   ; preds = %after_if108
  %360 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %360, label %true_block115, label %after_if114

after_if114:                                      ; preds = %true_block115, %false_block113, %true_block112
  %.0110 = phi float [ %359, %true_block112 ], [ %373, %true_block115 ], [ 0.000000e+00, %false_block113 ]
  %361 = add i32 %334, %106
  %362 = mul i32 %361, %96
  %363 = sext i32 %362 to i64
  %364 = getelementptr float, float* %94, i64 %363
  %365 = load float, float* %364, align 4
  %366 = fmul reassoc ninf nsz float %.0110, %.0111
  %367 = fmul reassoc ninf nsz float %366, %365
  %368 = fadd reassoc ninf nsz float %342, %367
  br i1 %315, label %true_block118, label %false_block119

true_block115:                                    ; preds = %false_block113
  %369 = fmul reassoc ninf nsz float %60, %60
  %370 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg356 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %371 = fsub reassoc ninf nsz float 2.500000e+00, %370
  %reass.mul358 = fmul reassoc ninf nsz float %369, %371
  %372 = fadd reassoc ninf nsz float %.neg356, 2.000000e+00
  %373 = fadd reassoc ninf nsz float %372, %reass.mul358
  br label %after_if114

true_block118:                                    ; preds = %after_if114
  %374 = fmul reassoc ninf nsz float %313, %313
  %375 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add366 = fadd reassoc ninf nsz float %375, -2.500000e+00
  %reass.mul367 = fmul reassoc ninf nsz float %374, %reass.add366
  %376 = fadd reassoc ninf nsz float %reass.mul367, 1.000000e+00
  br label %after_if120

false_block119:                                   ; preds = %after_if114
  %377 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %377, label %true_block121, label %after_if120

after_if120:                                      ; preds = %true_block121, %false_block119, %true_block118
  %.0109 = phi float [ %376, %true_block118 ], [ %382, %true_block121 ], [ 0.000000e+00, %false_block119 ]
  br i1 %150, label %true_block124, label %false_block125

true_block121:                                    ; preds = %false_block119
  %378 = fmul reassoc ninf nsz float %313, %313
  %379 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg362 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %380 = fsub reassoc ninf nsz float 2.500000e+00, %379
  %reass.mul364 = fmul reassoc ninf nsz float %378, %380
  %381 = fadd reassoc ninf nsz float %.neg362, 2.000000e+00
  %382 = fadd reassoc ninf nsz float %381, %reass.mul364
  br label %after_if120

true_block124:                                    ; preds = %after_if120
  %383 = fmul reassoc ninf nsz float %148, %148
  %384 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add372 = fadd reassoc ninf nsz float %384, -2.500000e+00
  %reass.mul373 = fmul reassoc ninf nsz float %383, %reass.add372
  %385 = fadd reassoc ninf nsz float %reass.mul373, 1.000000e+00
  br label %after_if126

false_block125:                                   ; preds = %after_if120
  %386 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %386, label %true_block127, label %after_if126

after_if126:                                      ; preds = %true_block127, %false_block125, %true_block124
  %.0108 = phi float [ %385, %true_block124 ], [ %399, %true_block127 ], [ 0.000000e+00, %false_block125 ]
  %387 = add i32 %334, %138
  %388 = mul i32 %387, %96
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, float* %94, i64 %389
  %391 = load float, float* %390, align 4
  %392 = fmul reassoc ninf nsz float %.0108, %.0109
  %393 = fmul reassoc ninf nsz float %392, %391
  %394 = fadd reassoc ninf nsz float %368, %393
  br i1 %315, label %true_block130, label %false_block131

true_block127:                                    ; preds = %false_block125
  %395 = fmul reassoc ninf nsz float %148, %148
  %396 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg368 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %397 = fsub reassoc ninf nsz float 2.500000e+00, %396
  %reass.mul370 = fmul reassoc ninf nsz float %395, %397
  %398 = fadd reassoc ninf nsz float %.neg368, 2.000000e+00
  %399 = fadd reassoc ninf nsz float %398, %reass.mul370
  br label %after_if126

true_block130:                                    ; preds = %after_if126
  %400 = fmul reassoc ninf nsz float %313, %313
  %401 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add378 = fadd reassoc ninf nsz float %401, -2.500000e+00
  %reass.mul379 = fmul reassoc ninf nsz float %400, %reass.add378
  %402 = fadd reassoc ninf nsz float %reass.mul379, 1.000000e+00
  br label %after_if132

false_block131:                                   ; preds = %after_if126
  %403 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %403, label %true_block133, label %after_if132

after_if132:                                      ; preds = %true_block133, %false_block131, %true_block130
  %.0107 = phi float [ %402, %true_block130 ], [ %408, %true_block133 ], [ 0.000000e+00, %false_block131 ]
  br i1 %182, label %true_block136, label %false_block137

true_block133:                                    ; preds = %false_block131
  %404 = fmul reassoc ninf nsz float %313, %313
  %405 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg374 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %406 = fsub reassoc ninf nsz float 2.500000e+00, %405
  %reass.mul376 = fmul reassoc ninf nsz float %404, %406
  %407 = fadd reassoc ninf nsz float %.neg374, 2.000000e+00
  %408 = fadd reassoc ninf nsz float %407, %reass.mul376
  br label %after_if132

true_block136:                                    ; preds = %after_if132
  %409 = fmul reassoc ninf nsz float %180, %180
  %410 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add384 = fadd reassoc ninf nsz float %410, -2.500000e+00
  %reass.mul385 = fmul reassoc ninf nsz float %409, %reass.add384
  %411 = fadd reassoc ninf nsz float %reass.mul385, 1.000000e+00
  br label %after_if138

false_block137:                                   ; preds = %after_if132
  %412 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %412, label %true_block139, label %after_if138

after_if138:                                      ; preds = %true_block139, %false_block137, %true_block136
  %.0106 = phi float [ %411, %true_block136 ], [ %431, %true_block139 ], [ 0.000000e+00, %false_block137 ]
  %413 = add i32 %334, %170
  %414 = mul i32 %413, %96
  %415 = sext i32 %414 to i64
  %416 = getelementptr float, float* %94, i64 %415
  %417 = load float, float* %416, align 4
  %418 = fmul reassoc ninf nsz float %.0106, %.0107
  %419 = fmul reassoc ninf nsz float %418, %417
  %420 = fadd reassoc ninf nsz float %394, %419
  %421 = add i32 %54, 2
  %422 = tail call i32 @llvm.smin.i32(i32 %421, i32 %65)
  %423 = tail call i32 @llvm.smax.i32(i32 %422, i32 0)
  %424 = fsub reassoc ninf nsz float 2.000000e+00, %58
  %425 = tail call float @llvm.fabs.f32(float %424)
  %426 = fcmp reassoc ninf nsz ole float %425, 1.000000e+00
  br i1 %426, label %true_block142, label %false_block143

true_block139:                                    ; preds = %false_block137
  %427 = fmul reassoc ninf nsz float %180, %180
  %428 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg380 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %429 = fsub reassoc ninf nsz float 2.500000e+00, %428
  %reass.mul382 = fmul reassoc ninf nsz float %427, %429
  %430 = fadd reassoc ninf nsz float %.neg380, 2.000000e+00
  %431 = fadd reassoc ninf nsz float %430, %reass.mul382
  br label %after_if138

true_block142:                                    ; preds = %after_if138
  %432 = fmul reassoc ninf nsz float %424, %424
  %433 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add390 = fadd reassoc ninf nsz float %433, -2.500000e+00
  %reass.mul391 = fmul reassoc ninf nsz float %432, %reass.add390
  %434 = fadd reassoc ninf nsz float %reass.mul391, 1.000000e+00
  br label %after_if144

false_block143:                                   ; preds = %after_if138
  %435 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %435, label %true_block145, label %after_if144

after_if144:                                      ; preds = %true_block145, %false_block143, %true_block142
  %.0105 = phi float [ %434, %true_block142 ], [ %440, %true_block145 ], [ 0.000000e+00, %false_block143 ]
  br i1 %84, label %true_block148, label %false_block149

true_block145:                                    ; preds = %false_block143
  %436 = fmul reassoc ninf nsz float %424, %424
  %437 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg386 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %438 = fsub reassoc ninf nsz float 2.500000e+00, %437
  %reass.mul388 = fmul reassoc ninf nsz float %436, %438
  %439 = fadd reassoc ninf nsz float %.neg386, 2.000000e+00
  %440 = fadd reassoc ninf nsz float %439, %reass.mul388
  br label %after_if144

true_block148:                                    ; preds = %after_if144
  %441 = fmul reassoc ninf nsz float %82, %82
  %442 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add396 = fadd reassoc ninf nsz float %442, -2.500000e+00
  %reass.mul397 = fmul reassoc ninf nsz float %441, %reass.add396
  %443 = fadd reassoc ninf nsz float %reass.mul397, 1.000000e+00
  br label %after_if150

false_block149:                                   ; preds = %after_if144
  %444 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %444, label %true_block151, label %after_if150

after_if150:                                      ; preds = %true_block151, %false_block149, %true_block148
  %.0104 = phi float [ %443, %true_block148 ], [ %458, %true_block151 ], [ 0.000000e+00, %false_block149 ]
  %445 = mul i32 %95, %423
  %446 = add i32 %445, %74
  %447 = mul i32 %446, %96
  %448 = sext i32 %447 to i64
  %449 = getelementptr float, float* %94, i64 %448
  %450 = load float, float* %449, align 4
  %451 = fmul reassoc ninf nsz float %.0104, %.0105
  %452 = fmul reassoc ninf nsz float %451, %450
  %453 = fadd reassoc ninf nsz float %420, %452
  br i1 %426, label %true_block154, label %false_block155

true_block151:                                    ; preds = %false_block149
  %454 = fmul reassoc ninf nsz float %82, %82
  %455 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg392 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %456 = fsub reassoc ninf nsz float 2.500000e+00, %455
  %reass.mul394 = fmul reassoc ninf nsz float %454, %456
  %457 = fadd reassoc ninf nsz float %.neg392, 2.000000e+00
  %458 = fadd reassoc ninf nsz float %457, %reass.mul394
  br label %after_if150

true_block154:                                    ; preds = %after_if150
  %459 = fmul reassoc ninf nsz float %424, %424
  %460 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add402 = fadd reassoc ninf nsz float %460, -2.500000e+00
  %reass.mul403 = fmul reassoc ninf nsz float %459, %reass.add402
  %461 = fadd reassoc ninf nsz float %reass.mul403, 1.000000e+00
  br label %after_if156

false_block155:                                   ; preds = %after_if150
  %462 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %462, label %true_block157, label %after_if156

after_if156:                                      ; preds = %true_block157, %false_block155, %true_block154
  %.0103 = phi float [ %461, %true_block154 ], [ %467, %true_block157 ], [ 0.000000e+00, %false_block155 ]
  br i1 %118, label %true_block160, label %false_block161

true_block157:                                    ; preds = %false_block155
  %463 = fmul reassoc ninf nsz float %424, %424
  %464 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg398 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %465 = fsub reassoc ninf nsz float 2.500000e+00, %464
  %reass.mul400 = fmul reassoc ninf nsz float %463, %465
  %466 = fadd reassoc ninf nsz float %.neg398, 2.000000e+00
  %467 = fadd reassoc ninf nsz float %466, %reass.mul400
  br label %after_if156

true_block160:                                    ; preds = %after_if156
  %468 = fmul reassoc ninf nsz float %60, %60
  %469 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add408 = fadd reassoc ninf nsz float %469, -2.500000e+00
  %reass.mul409 = fmul reassoc ninf nsz float %468, %reass.add408
  %470 = fadd reassoc ninf nsz float %reass.mul409, 1.000000e+00
  br label %after_if162

false_block161:                                   ; preds = %after_if156
  %471 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %471, label %true_block163, label %after_if162

after_if162:                                      ; preds = %true_block163, %false_block161, %true_block160
  %.0102 = phi float [ %470, %true_block160 ], [ %484, %true_block163 ], [ 0.000000e+00, %false_block161 ]
  %472 = add i32 %445, %106
  %473 = mul i32 %472, %96
  %474 = sext i32 %473 to i64
  %475 = getelementptr float, float* %94, i64 %474
  %476 = load float, float* %475, align 4
  %477 = fmul reassoc ninf nsz float %.0102, %.0103
  %478 = fmul reassoc ninf nsz float %477, %476
  %479 = fadd reassoc ninf nsz float %453, %478
  br i1 %426, label %true_block166, label %false_block167

true_block163:                                    ; preds = %false_block161
  %480 = fmul reassoc ninf nsz float %60, %60
  %481 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg404 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %482 = fsub reassoc ninf nsz float 2.500000e+00, %481
  %reass.mul406 = fmul reassoc ninf nsz float %480, %482
  %483 = fadd reassoc ninf nsz float %.neg404, 2.000000e+00
  %484 = fadd reassoc ninf nsz float %483, %reass.mul406
  br label %after_if162

true_block166:                                    ; preds = %after_if162
  %485 = fmul reassoc ninf nsz float %424, %424
  %486 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add414 = fadd reassoc ninf nsz float %486, -2.500000e+00
  %reass.mul415 = fmul reassoc ninf nsz float %485, %reass.add414
  %487 = fadd reassoc ninf nsz float %reass.mul415, 1.000000e+00
  br label %after_if168

false_block167:                                   ; preds = %after_if162
  %488 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %488, label %true_block169, label %after_if168

after_if168:                                      ; preds = %true_block169, %false_block167, %true_block166
  %.0101 = phi float [ %487, %true_block166 ], [ %493, %true_block169 ], [ 0.000000e+00, %false_block167 ]
  br i1 %150, label %true_block172, label %false_block173

true_block169:                                    ; preds = %false_block167
  %489 = fmul reassoc ninf nsz float %424, %424
  %490 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg410 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %491 = fsub reassoc ninf nsz float 2.500000e+00, %490
  %reass.mul412 = fmul reassoc ninf nsz float %489, %491
  %492 = fadd reassoc ninf nsz float %.neg410, 2.000000e+00
  %493 = fadd reassoc ninf nsz float %492, %reass.mul412
  br label %after_if168

true_block172:                                    ; preds = %after_if168
  %494 = fmul reassoc ninf nsz float %148, %148
  %495 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add420 = fadd reassoc ninf nsz float %495, -2.500000e+00
  %reass.mul421 = fmul reassoc ninf nsz float %494, %reass.add420
  %496 = fadd reassoc ninf nsz float %reass.mul421, 1.000000e+00
  br label %after_if174

false_block173:                                   ; preds = %after_if168
  %497 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %497, label %true_block175, label %after_if174

after_if174:                                      ; preds = %true_block175, %false_block173, %true_block172
  %.0100 = phi float [ %496, %true_block172 ], [ %510, %true_block175 ], [ 0.000000e+00, %false_block173 ]
  %498 = add i32 %445, %138
  %499 = mul i32 %498, %96
  %500 = sext i32 %499 to i64
  %501 = getelementptr float, float* %94, i64 %500
  %502 = load float, float* %501, align 4
  %503 = fmul reassoc ninf nsz float %.0100, %.0101
  %504 = fmul reassoc ninf nsz float %503, %502
  %505 = fadd reassoc ninf nsz float %479, %504
  br i1 %426, label %true_block178, label %false_block179

true_block175:                                    ; preds = %false_block173
  %506 = fmul reassoc ninf nsz float %148, %148
  %507 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg416 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %508 = fsub reassoc ninf nsz float 2.500000e+00, %507
  %reass.mul418 = fmul reassoc ninf nsz float %506, %508
  %509 = fadd reassoc ninf nsz float %.neg416, 2.000000e+00
  %510 = fadd reassoc ninf nsz float %509, %reass.mul418
  br label %after_if174

true_block178:                                    ; preds = %after_if174
  %511 = fmul reassoc ninf nsz float %424, %424
  %512 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add426 = fadd reassoc ninf nsz float %512, -2.500000e+00
  %reass.mul427 = fmul reassoc ninf nsz float %511, %reass.add426
  %513 = fadd reassoc ninf nsz float %reass.mul427, 1.000000e+00
  br label %after_if180

false_block179:                                   ; preds = %after_if174
  %514 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %514, label %true_block181, label %after_if180

after_if180:                                      ; preds = %true_block181, %false_block179, %true_block178
  %.099 = phi float [ %513, %true_block178 ], [ %519, %true_block181 ], [ 0.000000e+00, %false_block179 ]
  br i1 %182, label %true_block184, label %false_block185

true_block181:                                    ; preds = %false_block179
  %515 = fmul reassoc ninf nsz float %424, %424
  %516 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg422 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %517 = fsub reassoc ninf nsz float 2.500000e+00, %516
  %reass.mul424 = fmul reassoc ninf nsz float %515, %517
  %518 = fadd reassoc ninf nsz float %.neg422, 2.000000e+00
  %519 = fadd reassoc ninf nsz float %518, %reass.mul424
  br label %after_if180

true_block184:                                    ; preds = %after_if180
  %520 = fmul reassoc ninf nsz float %180, %180
  %521 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add432 = fadd reassoc ninf nsz float %521, -2.500000e+00
  %reass.mul433 = fmul reassoc ninf nsz float %520, %reass.add432
  %522 = fadd reassoc ninf nsz float %reass.mul433, 1.000000e+00
  br label %after_if186

false_block185:                                   ; preds = %after_if180
  %523 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %523, label %true_block187, label %after_if186

after_if186:                                      ; preds = %true_block187, %false_block185, %true_block184
  %.098 = phi float [ %522, %true_block184 ], [ %546, %true_block187 ], [ 0.000000e+00, %false_block185 ]
  %524 = add i32 %445, %170
  %525 = mul i32 %524, %96
  %526 = sext i32 %525 to i64
  %527 = getelementptr float, float* %94, i64 %526
  %528 = load float, float* %527, align 4
  %529 = fmul reassoc ninf nsz float %.098, %.099
  %530 = fmul reassoc ninf nsz float %529, %528
  %531 = fadd reassoc ninf nsz float %505, %530
  %532 = fmul reassoc ninf nsz float %531, %23
  %533 = load float*, float** %28, align 8
  %534 = load i32, i32* %29, align 4
  %535 = load i32, i32* %30, align 4
  %536 = sub i32 %534, %36
  %537 = mul i32 %536, %45
  %538 = add i32 %.0130626, %537
  %539 = mul i32 %538, %535
  %540 = sext i32 %539 to i64
  %541 = getelementptr float, float* %533, i64 %540
  store float %532, float* %541, align 4
  br i1 %77, label %true_block190, label %false_block191

true_block187:                                    ; preds = %false_block185
  %542 = fmul reassoc ninf nsz float %180, %180
  %543 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg428 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %544 = fsub reassoc ninf nsz float 2.500000e+00, %543
  %reass.mul430 = fmul reassoc ninf nsz float %542, %544
  %545 = fadd reassoc ninf nsz float %.neg428, 2.000000e+00
  %546 = fadd reassoc ninf nsz float %545, %reass.mul430
  br label %after_if186

true_block190:                                    ; preds = %after_if186
  %547 = fmul reassoc ninf nsz float %75, %75
  %548 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add438 = fadd reassoc ninf nsz float %548, -2.500000e+00
  %reass.mul439 = fmul reassoc ninf nsz float %547, %reass.add438
  %549 = fadd reassoc ninf nsz float %reass.mul439, 1.000000e+00
  br label %after_if192

false_block191:                                   ; preds = %after_if186
  %550 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %550, label %true_block193, label %after_if192

after_if192:                                      ; preds = %true_block193, %false_block191, %true_block190
  %.097 = phi float [ %549, %true_block190 ], [ %555, %true_block193 ], [ 0.000000e+00, %false_block191 ]
  br i1 %84, label %true_block196, label %false_block197

true_block193:                                    ; preds = %false_block191
  %551 = fmul reassoc ninf nsz float %75, %75
  %552 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg434 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %553 = fsub reassoc ninf nsz float 2.500000e+00, %552
  %reass.mul436 = fmul reassoc ninf nsz float %551, %553
  %554 = fadd reassoc ninf nsz float %.neg434, 2.000000e+00
  %555 = fadd reassoc ninf nsz float %554, %reass.mul436
  br label %after_if192

true_block196:                                    ; preds = %after_if192
  %556 = fmul reassoc ninf nsz float %82, %82
  %557 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add444 = fadd reassoc ninf nsz float %557, -2.500000e+00
  %reass.mul445 = fmul reassoc ninf nsz float %556, %reass.add444
  %558 = fadd reassoc ninf nsz float %reass.mul445, 1.000000e+00
  br label %after_if198

false_block197:                                   ; preds = %after_if192
  %559 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %559, label %true_block199, label %after_if198

after_if198:                                      ; preds = %true_block199, %false_block197, %true_block196
  %.096 = phi float [ %558, %true_block196 ], [ %576, %true_block199 ], [ 0.000000e+00, %false_block197 ]
  %560 = load float*, float** %25, align 8
  %561 = load i32, i32* %26, align 4
  %562 = load i32, i32* %27, align 4
  %563 = mul i32 %561, %67
  %564 = add i32 %563, %74
  %565 = mul i32 %564, %562
  %566 = add i32 %565, 1
  %567 = sext i32 %566 to i64
  %568 = getelementptr float, float* %560, i64 %567
  %569 = load float, float* %568, align 4
  %570 = fmul reassoc ninf nsz float %.096, %.097
  %571 = fmul reassoc ninf nsz float %570, %569
  br i1 %77, label %true_block202, label %false_block203

true_block199:                                    ; preds = %false_block197
  %572 = fmul reassoc ninf nsz float %82, %82
  %573 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg440 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %574 = fsub reassoc ninf nsz float 2.500000e+00, %573
  %reass.mul442 = fmul reassoc ninf nsz float %572, %574
  %575 = fadd reassoc ninf nsz float %.neg440, 2.000000e+00
  %576 = fadd reassoc ninf nsz float %575, %reass.mul442
  br label %after_if198

true_block202:                                    ; preds = %after_if198
  %577 = fmul reassoc ninf nsz float %75, %75
  %578 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add450 = fadd reassoc ninf nsz float %578, -2.500000e+00
  %reass.mul451 = fmul reassoc ninf nsz float %577, %reass.add450
  %579 = fadd reassoc ninf nsz float %reass.mul451, 1.000000e+00
  br label %after_if204

false_block203:                                   ; preds = %after_if198
  %580 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %580, label %true_block205, label %after_if204

after_if204:                                      ; preds = %true_block205, %false_block203, %true_block202
  %.095 = phi float [ %579, %true_block202 ], [ %585, %true_block205 ], [ 0.000000e+00, %false_block203 ]
  br i1 %118, label %true_block208, label %false_block209

true_block205:                                    ; preds = %false_block203
  %581 = fmul reassoc ninf nsz float %75, %75
  %582 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg446 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %583 = fsub reassoc ninf nsz float 2.500000e+00, %582
  %reass.mul448 = fmul reassoc ninf nsz float %581, %583
  %584 = fadd reassoc ninf nsz float %.neg446, 2.000000e+00
  %585 = fadd reassoc ninf nsz float %584, %reass.mul448
  br label %after_if204

true_block208:                                    ; preds = %after_if204
  %586 = fmul reassoc ninf nsz float %60, %60
  %587 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add456 = fadd reassoc ninf nsz float %587, -2.500000e+00
  %reass.mul457 = fmul reassoc ninf nsz float %586, %reass.add456
  %588 = fadd reassoc ninf nsz float %reass.mul457, 1.000000e+00
  br label %after_if210

false_block209:                                   ; preds = %after_if204
  %589 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %589, label %true_block211, label %after_if210

after_if210:                                      ; preds = %true_block211, %false_block209, %true_block208
  %.094 = phi float [ %588, %true_block208 ], [ %603, %true_block211 ], [ 0.000000e+00, %false_block209 ]
  %590 = add i32 %563, %106
  %591 = mul i32 %590, %562
  %592 = add i32 %591, 1
  %593 = sext i32 %592 to i64
  %594 = getelementptr float, float* %560, i64 %593
  %595 = load float, float* %594, align 4
  %596 = fmul reassoc ninf nsz float %.094, %.095
  %597 = fmul reassoc ninf nsz float %596, %595
  %598 = fadd reassoc ninf nsz float %597, %571
  br i1 %77, label %true_block214, label %false_block215

true_block211:                                    ; preds = %false_block209
  %599 = fmul reassoc ninf nsz float %60, %60
  %600 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg452 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %601 = fsub reassoc ninf nsz float 2.500000e+00, %600
  %reass.mul454 = fmul reassoc ninf nsz float %599, %601
  %602 = fadd reassoc ninf nsz float %.neg452, 2.000000e+00
  %603 = fadd reassoc ninf nsz float %602, %reass.mul454
  br label %after_if210

true_block214:                                    ; preds = %after_if210
  %604 = fmul reassoc ninf nsz float %75, %75
  %605 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add462 = fadd reassoc ninf nsz float %605, -2.500000e+00
  %reass.mul463 = fmul reassoc ninf nsz float %604, %reass.add462
  %606 = fadd reassoc ninf nsz float %reass.mul463, 1.000000e+00
  br label %after_if216

false_block215:                                   ; preds = %after_if210
  %607 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %607, label %true_block217, label %after_if216

after_if216:                                      ; preds = %true_block217, %false_block215, %true_block214
  %.093 = phi float [ %606, %true_block214 ], [ %612, %true_block217 ], [ 0.000000e+00, %false_block215 ]
  br i1 %150, label %true_block220, label %false_block221

true_block217:                                    ; preds = %false_block215
  %608 = fmul reassoc ninf nsz float %75, %75
  %609 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg458 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %610 = fsub reassoc ninf nsz float 2.500000e+00, %609
  %reass.mul460 = fmul reassoc ninf nsz float %608, %610
  %611 = fadd reassoc ninf nsz float %.neg458, 2.000000e+00
  %612 = fadd reassoc ninf nsz float %611, %reass.mul460
  br label %after_if216

true_block220:                                    ; preds = %after_if216
  %613 = fmul reassoc ninf nsz float %148, %148
  %614 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add468 = fadd reassoc ninf nsz float %614, -2.500000e+00
  %reass.mul469 = fmul reassoc ninf nsz float %613, %reass.add468
  %615 = fadd reassoc ninf nsz float %reass.mul469, 1.000000e+00
  br label %after_if222

false_block221:                                   ; preds = %after_if216
  %616 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %616, label %true_block223, label %after_if222

after_if222:                                      ; preds = %true_block223, %false_block221, %true_block220
  %.092 = phi float [ %615, %true_block220 ], [ %630, %true_block223 ], [ 0.000000e+00, %false_block221 ]
  %617 = add i32 %563, %138
  %618 = mul i32 %617, %562
  %619 = add i32 %618, 1
  %620 = sext i32 %619 to i64
  %621 = getelementptr float, float* %560, i64 %620
  %622 = load float, float* %621, align 4
  %623 = fmul reassoc ninf nsz float %.092, %.093
  %624 = fmul reassoc ninf nsz float %623, %622
  %625 = fadd reassoc ninf nsz float %598, %624
  br i1 %77, label %true_block226, label %false_block227

true_block223:                                    ; preds = %false_block221
  %626 = fmul reassoc ninf nsz float %148, %148
  %627 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg464 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %628 = fsub reassoc ninf nsz float 2.500000e+00, %627
  %reass.mul466 = fmul reassoc ninf nsz float %626, %628
  %629 = fadd reassoc ninf nsz float %.neg464, 2.000000e+00
  %630 = fadd reassoc ninf nsz float %629, %reass.mul466
  br label %after_if222

true_block226:                                    ; preds = %after_if222
  %631 = fmul reassoc ninf nsz float %75, %75
  %632 = fmul reassoc ninf nsz float %76, 1.500000e+00
  %reass.add474 = fadd reassoc ninf nsz float %632, -2.500000e+00
  %reass.mul475 = fmul reassoc ninf nsz float %631, %reass.add474
  %633 = fadd reassoc ninf nsz float %reass.mul475, 1.000000e+00
  br label %after_if228

false_block227:                                   ; preds = %after_if222
  %634 = fcmp reassoc ninf nsz olt float %76, 2.000000e+00
  br i1 %634, label %true_block229, label %after_if228

after_if228:                                      ; preds = %true_block229, %false_block227, %true_block226
  %.091 = phi float [ %633, %true_block226 ], [ %639, %true_block229 ], [ 0.000000e+00, %false_block227 ]
  br i1 %182, label %true_block232, label %false_block233

true_block229:                                    ; preds = %false_block227
  %635 = fmul reassoc ninf nsz float %75, %75
  %636 = fmul reassoc ninf nsz float %76, 5.000000e-01
  %.neg470 = fmul reassoc ninf nsz float %76, -4.000000e+00
  %637 = fsub reassoc ninf nsz float 2.500000e+00, %636
  %reass.mul472 = fmul reassoc ninf nsz float %635, %637
  %638 = fadd reassoc ninf nsz float %.neg470, 2.000000e+00
  %639 = fadd reassoc ninf nsz float %638, %reass.mul472
  br label %after_if228

true_block232:                                    ; preds = %after_if228
  %640 = fmul reassoc ninf nsz float %180, %180
  %641 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add480 = fadd reassoc ninf nsz float %641, -2.500000e+00
  %reass.mul481 = fmul reassoc ninf nsz float %640, %reass.add480
  %642 = fadd reassoc ninf nsz float %reass.mul481, 1.000000e+00
  br label %after_if234

false_block233:                                   ; preds = %after_if228
  %643 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %643, label %true_block235, label %after_if234

after_if234:                                      ; preds = %true_block235, %false_block233, %true_block232
  %.090 = phi float [ %642, %true_block232 ], [ %657, %true_block235 ], [ 0.000000e+00, %false_block233 ]
  %644 = add i32 %563, %170
  %645 = mul i32 %644, %562
  %646 = add i32 %645, 1
  %647 = sext i32 %646 to i64
  %648 = getelementptr float, float* %560, i64 %647
  %649 = load float, float* %648, align 4
  %650 = fmul reassoc ninf nsz float %.090, %.091
  %651 = fmul reassoc ninf nsz float %650, %649
  %652 = fadd reassoc ninf nsz float %625, %651
  br i1 %204, label %true_block238, label %false_block239

true_block235:                                    ; preds = %false_block233
  %653 = fmul reassoc ninf nsz float %180, %180
  %654 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg476 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %655 = fsub reassoc ninf nsz float 2.500000e+00, %654
  %reass.mul478 = fmul reassoc ninf nsz float %653, %655
  %656 = fadd reassoc ninf nsz float %.neg476, 2.000000e+00
  %657 = fadd reassoc ninf nsz float %656, %reass.mul478
  br label %after_if234

true_block238:                                    ; preds = %after_if234
  %658 = fmul reassoc ninf nsz float %58, %58
  %659 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add486 = fadd reassoc ninf nsz float %659, -2.500000e+00
  %reass.mul487 = fmul reassoc ninf nsz float %658, %reass.add486
  %660 = fadd reassoc ninf nsz float %reass.mul487, 1.000000e+00
  br label %after_if240

false_block239:                                   ; preds = %after_if234
  %661 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %661, label %true_block241, label %after_if240

after_if240:                                      ; preds = %true_block241, %false_block239, %true_block238
  %.089 = phi float [ %660, %true_block238 ], [ %666, %true_block241 ], [ 0.000000e+00, %false_block239 ]
  br i1 %84, label %true_block244, label %false_block245

true_block241:                                    ; preds = %false_block239
  %662 = fmul reassoc ninf nsz float %58, %58
  %663 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg482 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %664 = fsub reassoc ninf nsz float 2.500000e+00, %663
  %reass.mul484 = fmul reassoc ninf nsz float %662, %664
  %665 = fadd reassoc ninf nsz float %.neg482, 2.000000e+00
  %666 = fadd reassoc ninf nsz float %665, %reass.mul484
  br label %after_if240

true_block244:                                    ; preds = %after_if240
  %667 = fmul reassoc ninf nsz float %82, %82
  %668 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add492 = fadd reassoc ninf nsz float %668, -2.500000e+00
  %reass.mul493 = fmul reassoc ninf nsz float %667, %reass.add492
  %669 = fadd reassoc ninf nsz float %reass.mul493, 1.000000e+00
  br label %after_if246

false_block245:                                   ; preds = %after_if240
  %670 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %670, label %true_block247, label %after_if246

after_if246:                                      ; preds = %true_block247, %false_block245, %true_block244
  %.088 = phi float [ %669, %true_block244 ], [ %685, %true_block247 ], [ 0.000000e+00, %false_block245 ]
  %671 = mul i32 %561, %201
  %672 = add i32 %671, %74
  %673 = mul i32 %672, %562
  %674 = add i32 %673, 1
  %675 = sext i32 %674 to i64
  %676 = getelementptr float, float* %560, i64 %675
  %677 = load float, float* %676, align 4
  %678 = fmul reassoc ninf nsz float %.088, %.089
  %679 = fmul reassoc ninf nsz float %678, %677
  %680 = fadd reassoc ninf nsz float %652, %679
  br i1 %204, label %true_block250, label %false_block251

true_block247:                                    ; preds = %false_block245
  %681 = fmul reassoc ninf nsz float %82, %82
  %682 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg488 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %683 = fsub reassoc ninf nsz float 2.500000e+00, %682
  %reass.mul490 = fmul reassoc ninf nsz float %681, %683
  %684 = fadd reassoc ninf nsz float %.neg488, 2.000000e+00
  %685 = fadd reassoc ninf nsz float %684, %reass.mul490
  br label %after_if246

true_block250:                                    ; preds = %after_if246
  %686 = fmul reassoc ninf nsz float %58, %58
  %687 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add498 = fadd reassoc ninf nsz float %687, -2.500000e+00
  %reass.mul499 = fmul reassoc ninf nsz float %686, %reass.add498
  %688 = fadd reassoc ninf nsz float %reass.mul499, 1.000000e+00
  br label %after_if252

false_block251:                                   ; preds = %after_if246
  %689 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %689, label %true_block253, label %after_if252

after_if252:                                      ; preds = %true_block253, %false_block251, %true_block250
  %.087 = phi float [ %688, %true_block250 ], [ %694, %true_block253 ], [ 0.000000e+00, %false_block251 ]
  br i1 %118, label %true_block256, label %false_block257

true_block253:                                    ; preds = %false_block251
  %690 = fmul reassoc ninf nsz float %58, %58
  %691 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg494 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %692 = fsub reassoc ninf nsz float 2.500000e+00, %691
  %reass.mul496 = fmul reassoc ninf nsz float %690, %692
  %693 = fadd reassoc ninf nsz float %.neg494, 2.000000e+00
  %694 = fadd reassoc ninf nsz float %693, %reass.mul496
  br label %after_if252

true_block256:                                    ; preds = %after_if252
  %695 = fmul reassoc ninf nsz float %60, %60
  %696 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add504 = fadd reassoc ninf nsz float %696, -2.500000e+00
  %reass.mul505 = fmul reassoc ninf nsz float %695, %reass.add504
  %697 = fadd reassoc ninf nsz float %reass.mul505, 1.000000e+00
  br label %after_if258

false_block257:                                   ; preds = %after_if252
  %698 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %698, label %true_block259, label %after_if258

after_if258:                                      ; preds = %true_block259, %false_block257, %true_block256
  %.086 = phi float [ %697, %true_block256 ], [ %712, %true_block259 ], [ 0.000000e+00, %false_block257 ]
  %699 = add i32 %671, %106
  %700 = mul i32 %699, %562
  %701 = add i32 %700, 1
  %702 = sext i32 %701 to i64
  %703 = getelementptr float, float* %560, i64 %702
  %704 = load float, float* %703, align 4
  %705 = fmul reassoc ninf nsz float %.086, %.087
  %706 = fmul reassoc ninf nsz float %705, %704
  %707 = fadd reassoc ninf nsz float %680, %706
  br i1 %204, label %true_block262, label %false_block263

true_block259:                                    ; preds = %false_block257
  %708 = fmul reassoc ninf nsz float %60, %60
  %709 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg500 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %710 = fsub reassoc ninf nsz float 2.500000e+00, %709
  %reass.mul502 = fmul reassoc ninf nsz float %708, %710
  %711 = fadd reassoc ninf nsz float %.neg500, 2.000000e+00
  %712 = fadd reassoc ninf nsz float %711, %reass.mul502
  br label %after_if258

true_block262:                                    ; preds = %after_if258
  %713 = fmul reassoc ninf nsz float %58, %58
  %714 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add510 = fadd reassoc ninf nsz float %714, -2.500000e+00
  %reass.mul511 = fmul reassoc ninf nsz float %713, %reass.add510
  %715 = fadd reassoc ninf nsz float %reass.mul511, 1.000000e+00
  br label %after_if264

false_block263:                                   ; preds = %after_if258
  %716 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %716, label %true_block265, label %after_if264

after_if264:                                      ; preds = %true_block265, %false_block263, %true_block262
  %.085 = phi float [ %715, %true_block262 ], [ %721, %true_block265 ], [ 0.000000e+00, %false_block263 ]
  br i1 %150, label %true_block268, label %false_block269

true_block265:                                    ; preds = %false_block263
  %717 = fmul reassoc ninf nsz float %58, %58
  %718 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg506 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %719 = fsub reassoc ninf nsz float 2.500000e+00, %718
  %reass.mul508 = fmul reassoc ninf nsz float %717, %719
  %720 = fadd reassoc ninf nsz float %.neg506, 2.000000e+00
  %721 = fadd reassoc ninf nsz float %720, %reass.mul508
  br label %after_if264

true_block268:                                    ; preds = %after_if264
  %722 = fmul reassoc ninf nsz float %148, %148
  %723 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add516 = fadd reassoc ninf nsz float %723, -2.500000e+00
  %reass.mul517 = fmul reassoc ninf nsz float %722, %reass.add516
  %724 = fadd reassoc ninf nsz float %reass.mul517, 1.000000e+00
  br label %after_if270

false_block269:                                   ; preds = %after_if264
  %725 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %725, label %true_block271, label %after_if270

after_if270:                                      ; preds = %true_block271, %false_block269, %true_block268
  %.084 = phi float [ %724, %true_block268 ], [ %739, %true_block271 ], [ 0.000000e+00, %false_block269 ]
  %726 = add i32 %671, %138
  %727 = mul i32 %726, %562
  %728 = add i32 %727, 1
  %729 = sext i32 %728 to i64
  %730 = getelementptr float, float* %560, i64 %729
  %731 = load float, float* %730, align 4
  %732 = fmul reassoc ninf nsz float %.084, %.085
  %733 = fmul reassoc ninf nsz float %732, %731
  %734 = fadd reassoc ninf nsz float %707, %733
  br i1 %204, label %true_block274, label %false_block275

true_block271:                                    ; preds = %false_block269
  %735 = fmul reassoc ninf nsz float %148, %148
  %736 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg512 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %737 = fsub reassoc ninf nsz float 2.500000e+00, %736
  %reass.mul514 = fmul reassoc ninf nsz float %735, %737
  %738 = fadd reassoc ninf nsz float %.neg512, 2.000000e+00
  %739 = fadd reassoc ninf nsz float %738, %reass.mul514
  br label %after_if270

true_block274:                                    ; preds = %after_if270
  %740 = fmul reassoc ninf nsz float %58, %58
  %741 = fmul reassoc ninf nsz float %203, 1.500000e+00
  %reass.add522 = fadd reassoc ninf nsz float %741, -2.500000e+00
  %reass.mul523 = fmul reassoc ninf nsz float %740, %reass.add522
  %742 = fadd reassoc ninf nsz float %reass.mul523, 1.000000e+00
  br label %after_if276

false_block275:                                   ; preds = %after_if270
  %743 = fcmp reassoc ninf nsz olt float %203, 2.000000e+00
  br i1 %743, label %true_block277, label %after_if276

after_if276:                                      ; preds = %true_block277, %false_block275, %true_block274
  %.083 = phi float [ %742, %true_block274 ], [ %748, %true_block277 ], [ 0.000000e+00, %false_block275 ]
  br i1 %182, label %true_block280, label %false_block281

true_block277:                                    ; preds = %false_block275
  %744 = fmul reassoc ninf nsz float %58, %58
  %745 = fmul reassoc ninf nsz float %203, 5.000000e-01
  %.neg518 = fmul reassoc ninf nsz float %203, -4.000000e+00
  %746 = fsub reassoc ninf nsz float 2.500000e+00, %745
  %reass.mul520 = fmul reassoc ninf nsz float %744, %746
  %747 = fadd reassoc ninf nsz float %.neg518, 2.000000e+00
  %748 = fadd reassoc ninf nsz float %747, %reass.mul520
  br label %after_if276

true_block280:                                    ; preds = %after_if276
  %749 = fmul reassoc ninf nsz float %180, %180
  %750 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add528 = fadd reassoc ninf nsz float %750, -2.500000e+00
  %reass.mul529 = fmul reassoc ninf nsz float %749, %reass.add528
  %751 = fadd reassoc ninf nsz float %reass.mul529, 1.000000e+00
  br label %after_if282

false_block281:                                   ; preds = %after_if276
  %752 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %752, label %true_block283, label %after_if282

after_if282:                                      ; preds = %true_block283, %false_block281, %true_block280
  %.082 = phi float [ %751, %true_block280 ], [ %766, %true_block283 ], [ 0.000000e+00, %false_block281 ]
  %753 = add i32 %671, %170
  %754 = mul i32 %753, %562
  %755 = add i32 %754, 1
  %756 = sext i32 %755 to i64
  %757 = getelementptr float, float* %560, i64 %756
  %758 = load float, float* %757, align 4
  %759 = fmul reassoc ninf nsz float %.082, %.083
  %760 = fmul reassoc ninf nsz float %759, %758
  %761 = fadd reassoc ninf nsz float %734, %760
  br i1 %315, label %true_block286, label %false_block287

true_block283:                                    ; preds = %false_block281
  %762 = fmul reassoc ninf nsz float %180, %180
  %763 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg524 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %764 = fsub reassoc ninf nsz float 2.500000e+00, %763
  %reass.mul526 = fmul reassoc ninf nsz float %762, %764
  %765 = fadd reassoc ninf nsz float %.neg524, 2.000000e+00
  %766 = fadd reassoc ninf nsz float %765, %reass.mul526
  br label %after_if282

true_block286:                                    ; preds = %after_if282
  %767 = fmul reassoc ninf nsz float %313, %313
  %768 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add534 = fadd reassoc ninf nsz float %768, -2.500000e+00
  %reass.mul535 = fmul reassoc ninf nsz float %767, %reass.add534
  %769 = fadd reassoc ninf nsz float %reass.mul535, 1.000000e+00
  br label %after_if288

false_block287:                                   ; preds = %after_if282
  %770 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %770, label %true_block289, label %after_if288

after_if288:                                      ; preds = %true_block289, %false_block287, %true_block286
  %.081 = phi float [ %769, %true_block286 ], [ %775, %true_block289 ], [ 0.000000e+00, %false_block287 ]
  br i1 %84, label %true_block292, label %false_block293

true_block289:                                    ; preds = %false_block287
  %771 = fmul reassoc ninf nsz float %313, %313
  %772 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg530 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %773 = fsub reassoc ninf nsz float 2.500000e+00, %772
  %reass.mul532 = fmul reassoc ninf nsz float %771, %773
  %774 = fadd reassoc ninf nsz float %.neg530, 2.000000e+00
  %775 = fadd reassoc ninf nsz float %774, %reass.mul532
  br label %after_if288

true_block292:                                    ; preds = %after_if288
  %776 = fmul reassoc ninf nsz float %82, %82
  %777 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add540 = fadd reassoc ninf nsz float %777, -2.500000e+00
  %reass.mul541 = fmul reassoc ninf nsz float %776, %reass.add540
  %778 = fadd reassoc ninf nsz float %reass.mul541, 1.000000e+00
  br label %after_if294

false_block293:                                   ; preds = %after_if288
  %779 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %779, label %true_block295, label %after_if294

after_if294:                                      ; preds = %true_block295, %false_block293, %true_block292
  %.080 = phi float [ %778, %true_block292 ], [ %794, %true_block295 ], [ 0.000000e+00, %false_block293 ]
  %780 = mul i32 %561, %312
  %781 = add i32 %780, %74
  %782 = mul i32 %781, %562
  %783 = add i32 %782, 1
  %784 = sext i32 %783 to i64
  %785 = getelementptr float, float* %560, i64 %784
  %786 = load float, float* %785, align 4
  %787 = fmul reassoc ninf nsz float %.080, %.081
  %788 = fmul reassoc ninf nsz float %787, %786
  %789 = fadd reassoc ninf nsz float %761, %788
  br i1 %315, label %true_block298, label %false_block299

true_block295:                                    ; preds = %false_block293
  %790 = fmul reassoc ninf nsz float %82, %82
  %791 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg536 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %792 = fsub reassoc ninf nsz float 2.500000e+00, %791
  %reass.mul538 = fmul reassoc ninf nsz float %790, %792
  %793 = fadd reassoc ninf nsz float %.neg536, 2.000000e+00
  %794 = fadd reassoc ninf nsz float %793, %reass.mul538
  br label %after_if294

true_block298:                                    ; preds = %after_if294
  %795 = fmul reassoc ninf nsz float %313, %313
  %796 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add546 = fadd reassoc ninf nsz float %796, -2.500000e+00
  %reass.mul547 = fmul reassoc ninf nsz float %795, %reass.add546
  %797 = fadd reassoc ninf nsz float %reass.mul547, 1.000000e+00
  br label %after_if300

false_block299:                                   ; preds = %after_if294
  %798 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %798, label %true_block301, label %after_if300

after_if300:                                      ; preds = %true_block301, %false_block299, %true_block298
  %.079 = phi float [ %797, %true_block298 ], [ %803, %true_block301 ], [ 0.000000e+00, %false_block299 ]
  br i1 %118, label %true_block304, label %false_block305

true_block301:                                    ; preds = %false_block299
  %799 = fmul reassoc ninf nsz float %313, %313
  %800 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg542 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %801 = fsub reassoc ninf nsz float 2.500000e+00, %800
  %reass.mul544 = fmul reassoc ninf nsz float %799, %801
  %802 = fadd reassoc ninf nsz float %.neg542, 2.000000e+00
  %803 = fadd reassoc ninf nsz float %802, %reass.mul544
  br label %after_if300

true_block304:                                    ; preds = %after_if300
  %804 = fmul reassoc ninf nsz float %60, %60
  %805 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add552 = fadd reassoc ninf nsz float %805, -2.500000e+00
  %reass.mul553 = fmul reassoc ninf nsz float %804, %reass.add552
  %806 = fadd reassoc ninf nsz float %reass.mul553, 1.000000e+00
  br label %after_if306

false_block305:                                   ; preds = %after_if300
  %807 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %807, label %true_block307, label %after_if306

after_if306:                                      ; preds = %true_block307, %false_block305, %true_block304
  %.078 = phi float [ %806, %true_block304 ], [ %821, %true_block307 ], [ 0.000000e+00, %false_block305 ]
  %808 = add i32 %780, %106
  %809 = mul i32 %808, %562
  %810 = add i32 %809, 1
  %811 = sext i32 %810 to i64
  %812 = getelementptr float, float* %560, i64 %811
  %813 = load float, float* %812, align 4
  %814 = fmul reassoc ninf nsz float %.078, %.079
  %815 = fmul reassoc ninf nsz float %814, %813
  %816 = fadd reassoc ninf nsz float %789, %815
  br i1 %315, label %true_block310, label %false_block311

true_block307:                                    ; preds = %false_block305
  %817 = fmul reassoc ninf nsz float %60, %60
  %818 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg548 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %819 = fsub reassoc ninf nsz float 2.500000e+00, %818
  %reass.mul550 = fmul reassoc ninf nsz float %817, %819
  %820 = fadd reassoc ninf nsz float %.neg548, 2.000000e+00
  %821 = fadd reassoc ninf nsz float %820, %reass.mul550
  br label %after_if306

true_block310:                                    ; preds = %after_if306
  %822 = fmul reassoc ninf nsz float %313, %313
  %823 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add558 = fadd reassoc ninf nsz float %823, -2.500000e+00
  %reass.mul559 = fmul reassoc ninf nsz float %822, %reass.add558
  %824 = fadd reassoc ninf nsz float %reass.mul559, 1.000000e+00
  br label %after_if312

false_block311:                                   ; preds = %after_if306
  %825 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %825, label %true_block313, label %after_if312

after_if312:                                      ; preds = %true_block313, %false_block311, %true_block310
  %.077 = phi float [ %824, %true_block310 ], [ %830, %true_block313 ], [ 0.000000e+00, %false_block311 ]
  br i1 %150, label %true_block316, label %false_block317

true_block313:                                    ; preds = %false_block311
  %826 = fmul reassoc ninf nsz float %313, %313
  %827 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg554 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %828 = fsub reassoc ninf nsz float 2.500000e+00, %827
  %reass.mul556 = fmul reassoc ninf nsz float %826, %828
  %829 = fadd reassoc ninf nsz float %.neg554, 2.000000e+00
  %830 = fadd reassoc ninf nsz float %829, %reass.mul556
  br label %after_if312

true_block316:                                    ; preds = %after_if312
  %831 = fmul reassoc ninf nsz float %148, %148
  %832 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add564 = fadd reassoc ninf nsz float %832, -2.500000e+00
  %reass.mul565 = fmul reassoc ninf nsz float %831, %reass.add564
  %833 = fadd reassoc ninf nsz float %reass.mul565, 1.000000e+00
  br label %after_if318

false_block317:                                   ; preds = %after_if312
  %834 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %834, label %true_block319, label %after_if318

after_if318:                                      ; preds = %true_block319, %false_block317, %true_block316
  %.076 = phi float [ %833, %true_block316 ], [ %848, %true_block319 ], [ 0.000000e+00, %false_block317 ]
  %835 = add i32 %780, %138
  %836 = mul i32 %835, %562
  %837 = add i32 %836, 1
  %838 = sext i32 %837 to i64
  %839 = getelementptr float, float* %560, i64 %838
  %840 = load float, float* %839, align 4
  %841 = fmul reassoc ninf nsz float %.076, %.077
  %842 = fmul reassoc ninf nsz float %841, %840
  %843 = fadd reassoc ninf nsz float %816, %842
  br i1 %315, label %true_block322, label %false_block323

true_block319:                                    ; preds = %false_block317
  %844 = fmul reassoc ninf nsz float %148, %148
  %845 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg560 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %846 = fsub reassoc ninf nsz float 2.500000e+00, %845
  %reass.mul562 = fmul reassoc ninf nsz float %844, %846
  %847 = fadd reassoc ninf nsz float %.neg560, 2.000000e+00
  %848 = fadd reassoc ninf nsz float %847, %reass.mul562
  br label %after_if318

true_block322:                                    ; preds = %after_if318
  %849 = fmul reassoc ninf nsz float %313, %313
  %850 = fmul reassoc ninf nsz float %314, 1.500000e+00
  %reass.add570 = fadd reassoc ninf nsz float %850, -2.500000e+00
  %reass.mul571 = fmul reassoc ninf nsz float %849, %reass.add570
  %851 = fadd reassoc ninf nsz float %reass.mul571, 1.000000e+00
  br label %after_if324

false_block323:                                   ; preds = %after_if318
  %852 = fcmp reassoc ninf nsz olt float %314, 2.000000e+00
  br i1 %852, label %true_block325, label %after_if324

after_if324:                                      ; preds = %true_block325, %false_block323, %true_block322
  %.075 = phi float [ %851, %true_block322 ], [ %857, %true_block325 ], [ 0.000000e+00, %false_block323 ]
  br i1 %182, label %true_block328, label %false_block329

true_block325:                                    ; preds = %false_block323
  %853 = fmul reassoc ninf nsz float %313, %313
  %854 = fmul reassoc ninf nsz float %314, 5.000000e-01
  %.neg566 = fmul reassoc ninf nsz float %314, -4.000000e+00
  %855 = fsub reassoc ninf nsz float 2.500000e+00, %854
  %reass.mul568 = fmul reassoc ninf nsz float %853, %855
  %856 = fadd reassoc ninf nsz float %.neg566, 2.000000e+00
  %857 = fadd reassoc ninf nsz float %856, %reass.mul568
  br label %after_if324

true_block328:                                    ; preds = %after_if324
  %858 = fmul reassoc ninf nsz float %180, %180
  %859 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add576 = fadd reassoc ninf nsz float %859, -2.500000e+00
  %reass.mul577 = fmul reassoc ninf nsz float %858, %reass.add576
  %860 = fadd reassoc ninf nsz float %reass.mul577, 1.000000e+00
  br label %after_if330

false_block329:                                   ; preds = %after_if324
  %861 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %861, label %true_block331, label %after_if330

after_if330:                                      ; preds = %true_block331, %false_block329, %true_block328
  %.074 = phi float [ %860, %true_block328 ], [ %875, %true_block331 ], [ 0.000000e+00, %false_block329 ]
  %862 = add i32 %780, %170
  %863 = mul i32 %862, %562
  %864 = add i32 %863, 1
  %865 = sext i32 %864 to i64
  %866 = getelementptr float, float* %560, i64 %865
  %867 = load float, float* %866, align 4
  %868 = fmul reassoc ninf nsz float %.074, %.075
  %869 = fmul reassoc ninf nsz float %868, %867
  %870 = fadd reassoc ninf nsz float %843, %869
  br i1 %426, label %true_block334, label %false_block335

true_block331:                                    ; preds = %false_block329
  %871 = fmul reassoc ninf nsz float %180, %180
  %872 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg572 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %873 = fsub reassoc ninf nsz float 2.500000e+00, %872
  %reass.mul574 = fmul reassoc ninf nsz float %871, %873
  %874 = fadd reassoc ninf nsz float %.neg572, 2.000000e+00
  %875 = fadd reassoc ninf nsz float %874, %reass.mul574
  br label %after_if330

true_block334:                                    ; preds = %after_if330
  %876 = fmul reassoc ninf nsz float %424, %424
  %877 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add582 = fadd reassoc ninf nsz float %877, -2.500000e+00
  %reass.mul583 = fmul reassoc ninf nsz float %876, %reass.add582
  %878 = fadd reassoc ninf nsz float %reass.mul583, 1.000000e+00
  br label %after_if336

false_block335:                                   ; preds = %after_if330
  %879 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %879, label %true_block337, label %after_if336

after_if336:                                      ; preds = %true_block337, %false_block335, %true_block334
  %.073 = phi float [ %878, %true_block334 ], [ %884, %true_block337 ], [ 0.000000e+00, %false_block335 ]
  br i1 %84, label %true_block340, label %false_block341

true_block337:                                    ; preds = %false_block335
  %880 = fmul reassoc ninf nsz float %424, %424
  %881 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg578 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %882 = fsub reassoc ninf nsz float 2.500000e+00, %881
  %reass.mul580 = fmul reassoc ninf nsz float %880, %882
  %883 = fadd reassoc ninf nsz float %.neg578, 2.000000e+00
  %884 = fadd reassoc ninf nsz float %883, %reass.mul580
  br label %after_if336

true_block340:                                    ; preds = %after_if336
  %885 = fmul reassoc ninf nsz float %82, %82
  %886 = fmul reassoc ninf nsz float %83, 1.500000e+00
  %reass.add588 = fadd reassoc ninf nsz float %886, -2.500000e+00
  %reass.mul589 = fmul reassoc ninf nsz float %885, %reass.add588
  %887 = fadd reassoc ninf nsz float %reass.mul589, 1.000000e+00
  br label %after_if342

false_block341:                                   ; preds = %after_if336
  %888 = fcmp reassoc ninf nsz olt float %83, 2.000000e+00
  br i1 %888, label %true_block343, label %after_if342

after_if342:                                      ; preds = %true_block343, %false_block341, %true_block340
  %.072 = phi float [ %887, %true_block340 ], [ %903, %true_block343 ], [ 0.000000e+00, %false_block341 ]
  %889 = mul i32 %561, %423
  %890 = add i32 %889, %74
  %891 = mul i32 %890, %562
  %892 = add i32 %891, 1
  %893 = sext i32 %892 to i64
  %894 = getelementptr float, float* %560, i64 %893
  %895 = load float, float* %894, align 4
  %896 = fmul reassoc ninf nsz float %.072, %.073
  %897 = fmul reassoc ninf nsz float %896, %895
  %898 = fadd reassoc ninf nsz float %870, %897
  br i1 %426, label %true_block346, label %false_block347

true_block343:                                    ; preds = %false_block341
  %899 = fmul reassoc ninf nsz float %82, %82
  %900 = fmul reassoc ninf nsz float %83, 5.000000e-01
  %.neg584 = fmul reassoc ninf nsz float %83, -4.000000e+00
  %901 = fsub reassoc ninf nsz float 2.500000e+00, %900
  %reass.mul586 = fmul reassoc ninf nsz float %899, %901
  %902 = fadd reassoc ninf nsz float %.neg584, 2.000000e+00
  %903 = fadd reassoc ninf nsz float %902, %reass.mul586
  br label %after_if342

true_block346:                                    ; preds = %after_if342
  %904 = fmul reassoc ninf nsz float %424, %424
  %905 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add594 = fadd reassoc ninf nsz float %905, -2.500000e+00
  %reass.mul595 = fmul reassoc ninf nsz float %904, %reass.add594
  %906 = fadd reassoc ninf nsz float %reass.mul595, 1.000000e+00
  br label %after_if348

false_block347:                                   ; preds = %after_if342
  %907 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %907, label %true_block349, label %after_if348

after_if348:                                      ; preds = %true_block349, %false_block347, %true_block346
  %.071 = phi float [ %906, %true_block346 ], [ %912, %true_block349 ], [ 0.000000e+00, %false_block347 ]
  br i1 %118, label %true_block352, label %false_block353

true_block349:                                    ; preds = %false_block347
  %908 = fmul reassoc ninf nsz float %424, %424
  %909 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg590 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %910 = fsub reassoc ninf nsz float 2.500000e+00, %909
  %reass.mul592 = fmul reassoc ninf nsz float %908, %910
  %911 = fadd reassoc ninf nsz float %.neg590, 2.000000e+00
  %912 = fadd reassoc ninf nsz float %911, %reass.mul592
  br label %after_if348

true_block352:                                    ; preds = %after_if348
  %913 = fmul reassoc ninf nsz float %60, %60
  %914 = fmul reassoc ninf nsz float %117, 1.500000e+00
  %reass.add600 = fadd reassoc ninf nsz float %914, -2.500000e+00
  %reass.mul601 = fmul reassoc ninf nsz float %913, %reass.add600
  %915 = fadd reassoc ninf nsz float %reass.mul601, 1.000000e+00
  br label %after_if354

false_block353:                                   ; preds = %after_if348
  %916 = fcmp reassoc ninf nsz olt float %117, 2.000000e+00
  br i1 %916, label %true_block355, label %after_if354

after_if354:                                      ; preds = %true_block355, %false_block353, %true_block352
  %.070 = phi float [ %915, %true_block352 ], [ %930, %true_block355 ], [ 0.000000e+00, %false_block353 ]
  %917 = add i32 %889, %106
  %918 = mul i32 %917, %562
  %919 = add i32 %918, 1
  %920 = sext i32 %919 to i64
  %921 = getelementptr float, float* %560, i64 %920
  %922 = load float, float* %921, align 4
  %923 = fmul reassoc ninf nsz float %.070, %.071
  %924 = fmul reassoc ninf nsz float %923, %922
  %925 = fadd reassoc ninf nsz float %898, %924
  br i1 %426, label %true_block358, label %false_block359

true_block355:                                    ; preds = %false_block353
  %926 = fmul reassoc ninf nsz float %60, %60
  %927 = fmul reassoc ninf nsz float %117, 5.000000e-01
  %.neg596 = fmul reassoc ninf nsz float %117, -4.000000e+00
  %928 = fsub reassoc ninf nsz float 2.500000e+00, %927
  %reass.mul598 = fmul reassoc ninf nsz float %926, %928
  %929 = fadd reassoc ninf nsz float %.neg596, 2.000000e+00
  %930 = fadd reassoc ninf nsz float %929, %reass.mul598
  br label %after_if354

true_block358:                                    ; preds = %after_if354
  %931 = fmul reassoc ninf nsz float %424, %424
  %932 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add606 = fadd reassoc ninf nsz float %932, -2.500000e+00
  %reass.mul607 = fmul reassoc ninf nsz float %931, %reass.add606
  %933 = fadd reassoc ninf nsz float %reass.mul607, 1.000000e+00
  br label %after_if360

false_block359:                                   ; preds = %after_if354
  %934 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %934, label %true_block361, label %after_if360

after_if360:                                      ; preds = %true_block361, %false_block359, %true_block358
  %.069 = phi float [ %933, %true_block358 ], [ %939, %true_block361 ], [ 0.000000e+00, %false_block359 ]
  br i1 %150, label %true_block364, label %false_block365

true_block361:                                    ; preds = %false_block359
  %935 = fmul reassoc ninf nsz float %424, %424
  %936 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg602 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %937 = fsub reassoc ninf nsz float 2.500000e+00, %936
  %reass.mul604 = fmul reassoc ninf nsz float %935, %937
  %938 = fadd reassoc ninf nsz float %.neg602, 2.000000e+00
  %939 = fadd reassoc ninf nsz float %938, %reass.mul604
  br label %after_if360

true_block364:                                    ; preds = %after_if360
  %940 = fmul reassoc ninf nsz float %148, %148
  %941 = fmul reassoc ninf nsz float %149, 1.500000e+00
  %reass.add612 = fadd reassoc ninf nsz float %941, -2.500000e+00
  %reass.mul613 = fmul reassoc ninf nsz float %940, %reass.add612
  %942 = fadd reassoc ninf nsz float %reass.mul613, 1.000000e+00
  br label %after_if366

false_block365:                                   ; preds = %after_if360
  %943 = fcmp reassoc ninf nsz olt float %149, 2.000000e+00
  br i1 %943, label %true_block367, label %after_if366

after_if366:                                      ; preds = %true_block367, %false_block365, %true_block364
  %.068 = phi float [ %942, %true_block364 ], [ %957, %true_block367 ], [ 0.000000e+00, %false_block365 ]
  %944 = add i32 %889, %138
  %945 = mul i32 %944, %562
  %946 = add i32 %945, 1
  %947 = sext i32 %946 to i64
  %948 = getelementptr float, float* %560, i64 %947
  %949 = load float, float* %948, align 4
  %950 = fmul reassoc ninf nsz float %.068, %.069
  %951 = fmul reassoc ninf nsz float %950, %949
  %952 = fadd reassoc ninf nsz float %925, %951
  br i1 %426, label %true_block370, label %false_block371

true_block367:                                    ; preds = %false_block365
  %953 = fmul reassoc ninf nsz float %148, %148
  %954 = fmul reassoc ninf nsz float %149, 5.000000e-01
  %.neg608 = fmul reassoc ninf nsz float %149, -4.000000e+00
  %955 = fsub reassoc ninf nsz float 2.500000e+00, %954
  %reass.mul610 = fmul reassoc ninf nsz float %953, %955
  %956 = fadd reassoc ninf nsz float %.neg608, 2.000000e+00
  %957 = fadd reassoc ninf nsz float %956, %reass.mul610
  br label %after_if366

true_block370:                                    ; preds = %after_if366
  %958 = fmul reassoc ninf nsz float %424, %424
  %959 = fmul reassoc ninf nsz float %425, 1.500000e+00
  %reass.add618 = fadd reassoc ninf nsz float %959, -2.500000e+00
  %reass.mul619 = fmul reassoc ninf nsz float %958, %reass.add618
  %960 = fadd reassoc ninf nsz float %reass.mul619, 1.000000e+00
  br label %after_if372

false_block371:                                   ; preds = %after_if366
  %961 = fcmp reassoc ninf nsz olt float %425, 2.000000e+00
  br i1 %961, label %true_block373, label %after_if372

after_if372:                                      ; preds = %true_block373, %false_block371, %true_block370
  %.067 = phi float [ %960, %true_block370 ], [ %966, %true_block373 ], [ 0.000000e+00, %false_block371 ]
  br i1 %182, label %true_block376, label %false_block377

true_block373:                                    ; preds = %false_block371
  %962 = fmul reassoc ninf nsz float %424, %424
  %963 = fmul reassoc ninf nsz float %425, 5.000000e-01
  %.neg614 = fmul reassoc ninf nsz float %425, -4.000000e+00
  %964 = fsub reassoc ninf nsz float 2.500000e+00, %963
  %reass.mul616 = fmul reassoc ninf nsz float %962, %964
  %965 = fadd reassoc ninf nsz float %.neg614, 2.000000e+00
  %966 = fadd reassoc ninf nsz float %965, %reass.mul616
  br label %after_if372

true_block376:                                    ; preds = %after_if372
  %967 = fmul reassoc ninf nsz float %180, %180
  %968 = fmul reassoc ninf nsz float %181, 1.500000e+00
  %reass.add624 = fadd reassoc ninf nsz float %968, -2.500000e+00
  %reass.mul625 = fmul reassoc ninf nsz float %967, %reass.add624
  %969 = fadd reassoc ninf nsz float %reass.mul625, 1.000000e+00
  br label %after_if378

false_block377:                                   ; preds = %after_if372
  %970 = fcmp reassoc ninf nsz olt float %181, 2.000000e+00
  br i1 %970, label %true_block379, label %after_if378

after_if378:                                      ; preds = %true_block379, %false_block377, %true_block376
  %.0 = phi float [ %969, %true_block376 ], [ %996, %true_block379 ], [ 0.000000e+00, %false_block377 ]
  %971 = add i32 %889, %170
  %972 = mul i32 %971, %562
  %973 = add i32 %972, 1
  %974 = sext i32 %973 to i64
  %975 = getelementptr float, float* %560, i64 %974
  %976 = load float, float* %975, align 4
  %977 = fmul reassoc ninf nsz float %.0, %.067
  %978 = fmul reassoc ninf nsz float %977, %976
  %979 = fadd reassoc ninf nsz float %952, %978
  %980 = fmul reassoc ninf nsz float %979, %23
  %981 = load float*, float** %28, align 8
  %982 = load i32, i32* %29, align 4
  %983 = load i32, i32* %30, align 4
  %984 = sub i32 %982, %36
  %985 = mul i32 %984, %45
  %986 = add i32 %.0130626, %985
  %987 = mul i32 %986, %983
  %988 = add i32 %987, 1
  %989 = sext i32 %988 to i64
  %990 = getelementptr float, float* %981, i64 %989
  store float %980, float* %990, align 4
  %991 = add nsw i32 %.0130626, 1
  %exitcond.not = icmp eq i32 %19, %991
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block379:                                    ; preds = %false_block377
  %992 = fmul reassoc ninf nsz float %180, %180
  %993 = fmul reassoc ninf nsz float %181, 5.000000e-01
  %.neg620 = fmul reassoc ninf nsz float %181, -4.000000e+00
  %994 = fsub reassoc ninf nsz float 2.500000e+00, %993
  %reass.mul622 = fmul reassoc ninf nsz float %992, %994
  %995 = fadd reassoc ninf nsz float %.neg620, 2.000000e+00
  %996 = fadd reassoc ninf nsz float %995, %reass.mul622
  br label %after_if378
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.floor.f32(float) #3

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
