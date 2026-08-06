; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.108*, void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*, i32)*, void (%struct.RuntimeContext.108*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.108 = type { i8*, %struct.LLVMRuntime.107*, i32, i64* }
%struct.LLVMRuntime.107 = type { %struct.PreallocatedMemoryChunk.103, %struct.PreallocatedMemoryChunk.103, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.104*], [1024 x %struct.NodeManager.105*], [1024 x i8*], i8*, %struct.RandState.106*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.103 = type { i8*, i8*, i64 }
%struct.ListManager.104 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.107* }
%struct.NodeManager.105 = type { %struct.LLVMRuntime.107*, i32, i32, i32, i32, %struct.ListManager.104*, %struct.ListManager.104*, %struct.ListManager.104*, i32 }
%struct.RandState.106 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_ha_to_grayscale_3channel_kernel_c718_0_kernel_0_serial(%struct.RuntimeContext.108* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.108* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 8
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 9
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_ha_to_grayscale_3channel_kernel_c718_0_kernel_1_range_for(%struct.RuntimeContext.108* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.108* %context, %struct.RuntimeContext.108** %4, align 8
  store void (%struct.RuntimeContext.108*, i8*)* null, void (%struct.RuntimeContext.108*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.108*, i8*, i32)* @function_body, void (%struct.RuntimeContext.108*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.108*, i8*)* null, void (%struct.RuntimeContext.108*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.108* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.108* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %23 = load float, float* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %25 = load float, float* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 7
  %27 = load float, float* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %29 = load float, float* %28, align 4
  %30 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %23, float 0x3FB99999A0000000)
  %31 = fadd reassoc ninf nsz float %27, %25
  %32 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %29, float 0x3FB99999A0000000)
  %33 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %34 = load float*, float** %33, align 8
  %35 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %36 = load i32, i32* %35, align 4
  %37 = getelementptr float, float* %34, i64 1
  %38 = getelementptr float, float* %34, i64 2
  %39 = sext i32 %36 to i64
  %40 = getelementptr float, float* %34, i64 %39
  %41 = add i32 %36, 1
  %42 = sext i32 %41 to i64
  %43 = getelementptr float, float* %34, i64 %42
  %44 = add i32 %36, 2
  %45 = sext i32 %44 to i64
  %46 = getelementptr float, float* %34, i64 %45
  %47 = shl i32 %36, 1
  %48 = sext i32 %47 to i64
  %49 = getelementptr float, float* %34, i64 %48
  %50 = getelementptr float, float* %49, i64 1
  %51 = add i32 %47, 2
  %52 = sext i32 %51 to i64
  %53 = getelementptr float, float* %34, i64 %52
  %54 = fmul reassoc ninf nsz float %31, 5.000000e-01
  %55 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %54, float 0x3FB99999A0000000)
  %56 = icmp slt i32 %17, %19
  br i1 %56, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %57 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %58 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %59 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 1
  %60 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if9, %for_loop_body.lr.ph
  %.03998 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %220, %after_if9 ]
  %61 = load %struct.LLVMRuntime.107*, %struct.LLVMRuntime.107** %3, align 8
  %62 = getelementptr inbounds %struct.LLVMRuntime.107, %struct.LLVMRuntime.107* %61, i64 0, i32 14
  %63 = load i8*, i8** %62, align 8
  %64 = getelementptr inbounds i8, i8* %63, i64 4
  %65 = bitcast i8* %64 to i32*
  %66 = load i32, i32* %65, align 4
  %67 = sdiv i32 %.03998, %66
  %68 = mul i32 %67, %66
  %69 = xor i32 %66, %.03998
  %70 = icmp slt i32 %69, 0
  %71 = icmp ne i32 %.03998, 0
  %72 = icmp ne i32 %.03998, %68
  %73 = and i1 %71, %70
  %74 = and i1 %73, %72
  %.neg57 = sext i1 %74 to i32
  %75 = add i32 %67, %.neg57
  %76 = mul i32 %75, %66
  %77 = mul i32 %66, -1
  %78 = mul i32 %77, %75
  %79 = add i32 %.03998, %78
  %80 = sdiv i32 %75, 2
  %81 = icmp slt i32 %75, 0
  %82 = shl nsw i32 %80, 1
  %83 = icmp ne i32 %82, %75
  %84 = and i1 %81, %83
  %.neg58.neg = zext i1 %84 to i32
  %.neg60 = sub nsw i32 %.neg58.neg, %80
  %.neg59 = shl i32 %.neg60, 1
  %85 = sdiv i32 %79, 2
  %86 = icmp slt i32 %79, 0
  %87 = shl i32 %85, 1
  %88 = icmp ne i32 %79, %87
  %89 = and i1 %86, %88
  %.neg61.neg = zext i1 %89 to i32
  %90 = add i32 %76, %87
  %91 = shl nuw nsw i32 %.neg61.neg, 1
  %92 = sub i32 %90, %91
  %93 = add i32 %92, 1
  %94 = sub i32 0, %75
  %95 = icmp eq i32 %.neg59, %94
  %.not = icmp eq i32 %92, %.03998
  %96 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  br i1 %95, label %true_block, label %false_block

after_for.loopexit:                               ; preds = %after_if9
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  br i1 %.not, label %true_block1, label %false_block2

false_block:                                      ; preds = %for_loop_body
  br i1 %.not, label %true_block4, label %false_block5

after_if:                                         ; preds = %false_block5, %true_block4, %false_block2, %true_block1
  %.038.in = phi i32* [ %105, %true_block1 ], [ %106, %false_block2 ], [ %107, %true_block4 ], [ %108, %false_block5 ]
  %.038 = load i32, i32* %.038.in, align 4
  %97 = load float*, float** %57, align 8
  %98 = load i32, i32* %58, align 4
  %99 = sub i32 %98, %66
  %100 = mul i32 %99, %75
  %101 = add i32 %.03998, %100
  %102 = sext i32 %101 to i64
  %103 = getelementptr float, float* %97, i64 %102
  %104 = load float, float* %103, align 4
  switch i32 %.038, label %false_block23 [
    i32 0, label %true_block7
    i32 2, label %true_block22
  ]

true_block1:                                      ; preds = %true_block
  %105 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 10
  br label %after_if

false_block2:                                     ; preds = %true_block
  %106 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 11
  br label %after_if

true_block4:                                      ; preds = %false_block
  %107 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 12
  br label %after_if

false_block5:                                     ; preds = %false_block
  %108 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 13
  br label %after_if

true_block7:                                      ; preds = %after_if
  %109 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 1
  %110 = load float*, float** %109, align 8
  %111 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 0, i32 1
  %112 = load i32, i32* %111, align 4
  %113 = sub i32 %112, %66
  %114 = mul i32 %113, %75
  %115 = add i32 %.03998, %114
  %116 = sext i32 %115 to i64
  %117 = getelementptr float, float* %110, i64 %116
  %118 = load float, float* %117, align 4
  %119 = icmp sgt i32 %75, 0
  br i1 %119, label %true_block10, label %after_if9

after_if9:                                        ; preds = %true_block70, %true_block67, %after_if66, %true_block58, %true_block55, %after_if54, %true_block34, %true_block31, %true_block25, %true_block22, %true_block19, %true_block16, %true_block10, %true_block7
  %.034 = phi float [ %118, %true_block19 ], [ %357, %true_block34 ], [ %.135, %true_block58 ], [ %.2, %true_block70 ], [ %118, %true_block10 ], [ %118, %true_block7 ], [ %118, %true_block16 ], [ %104, %true_block25 ], [ %104, %true_block22 ], [ %104, %true_block31 ], [ %.135, %after_if54 ], [ %.135, %true_block55 ], [ %.2, %after_if66 ], [ %.2, %true_block67 ]
  %.033 = phi float [ %283, %true_block19 ], [ %293, %true_block34 ], [ %437, %true_block58 ], [ %511, %true_block70 ], [ %104, %true_block10 ], [ %104, %true_block7 ], [ %104, %true_block16 ], [ %293, %true_block25 ], [ %293, %true_block22 ], [ %293, %true_block31 ], [ %104, %after_if54 ], [ %104, %true_block55 ], [ %104, %after_if66 ], [ %104, %true_block67 ]
  %120 = fdiv reassoc ninf nsz float %.034, %30
  %121 = fdiv reassoc ninf nsz float %104, %55
  %122 = fdiv reassoc ninf nsz float %.033, %32
  %123 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %121, float %122)
  %124 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %120, float %123)
  %125 = fmul reassoc ninf nsz float %124, 0x4011642C80000000
  %126 = fadd reassoc ninf nsz float %125, 0xC00A1642C0000000
  %127 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %126, float 0.000000e+00)
  %128 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %127, float 1.000000e+00)
  %129 = fmul reassoc ninf nsz float %128, %128
  %factor97 = fmul reassoc ninf nsz float %128, -2.000000e+00
  %130 = fadd reassoc ninf nsz float %factor97, 3.000000e+00
  %131 = fmul reassoc ninf nsz float %129, %130
  %132 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %104, float %.033)
  %133 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.034, float %132)
  %134 = fsub reassoc ninf nsz float 1.000000e+00, %131
  %135 = fmul reassoc ninf nsz float %134, %.034
  %136 = fmul reassoc ninf nsz float %131, %133
  %137 = fadd reassoc ninf nsz float %135, %136
  %138 = fmul reassoc ninf nsz float %134, %104
  %139 = fadd reassoc ninf nsz float %138, %136
  %140 = fmul reassoc ninf nsz float %134, %.033
  %141 = fadd reassoc ninf nsz float %140, %136
  %142 = load float, float* %34, align 4
  %143 = fmul reassoc ninf nsz float %137, %142
  %144 = load float, float* %37, align 4
  %145 = fmul reassoc ninf nsz float %139, %144
  %146 = fadd reassoc ninf nsz float %143, %145
  %147 = load float, float* %38, align 4
  %148 = fmul reassoc ninf nsz float %141, %147
  %149 = fadd reassoc ninf nsz float %146, %148
  %150 = load float, float* %40, align 4
  %151 = fmul reassoc ninf nsz float %137, %150
  %152 = load float, float* %43, align 4
  %153 = fmul reassoc ninf nsz float %139, %152
  %154 = fadd reassoc ninf nsz float %151, %153
  %155 = load float, float* %46, align 4
  %156 = fmul reassoc ninf nsz float %141, %155
  %157 = fadd reassoc ninf nsz float %154, %156
  %158 = load float, float* %49, align 4
  %159 = fmul reassoc ninf nsz float %137, %158
  %160 = load float, float* %50, align 4
  %161 = fmul reassoc ninf nsz float %139, %160
  %162 = fadd reassoc ninf nsz float %159, %161
  %163 = load float, float* %53, align 4
  %164 = fmul reassoc ninf nsz float %141, %163
  %165 = fadd reassoc ninf nsz float %162, %164
  %166 = fmul reassoc ninf nsz float %149, %149
  %167 = fadd reassoc ninf nsz float %166, 1.000000e+00
  %168 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %167)
  %169 = fdiv reassoc ninf nsz float %149, %168
  %170 = fmul reassoc ninf nsz float %157, %157
  %171 = fadd reassoc ninf nsz float %170, 1.000000e+00
  %172 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %171)
  %173 = fdiv reassoc ninf nsz float %157, %172
  %174 = fmul reassoc ninf nsz float %165, %165
  %175 = fadd reassoc ninf nsz float %174, 1.000000e+00
  %176 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %175)
  %177 = fdiv reassoc ninf nsz float %165, %176
  %178 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %169, float 0.000000e+00)
  %179 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %178, float 1.000000e+00)
  %180 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %179)
  %181 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %173, float 0.000000e+00)
  %182 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %181, float 1.000000e+00)
  %183 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %182)
  %184 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %177, float 0.000000e+00)
  %185 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %184, float 1.000000e+00)
  %186 = tail call reassoc ninf nsz float @llvm.sqrt.f32(float %185)
  %187 = fmul reassoc ninf nsz float %180, 0x3FD3A00620000000
  %188 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %187
  %189 = fmul reassoc ninf nsz float %188, %180
  %190 = fadd reassoc ninf nsz float %189, 0xBFE9435AA0000000
  %191 = fmul reassoc ninf nsz float %190, %180
  %192 = fadd reassoc ninf nsz float %191, 0x3FF4E33660000000
  %193 = fmul reassoc ninf nsz float %180, 0x3FD322D0E0000000
  %194 = fmul reassoc ninf nsz float %193, %192
  %195 = fmul reassoc ninf nsz float %183, 0x3FD3A00620000000
  %196 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %195
  %197 = fmul reassoc ninf nsz float %196, %183
  %198 = fadd reassoc ninf nsz float %197, 0xBFE9435AA0000000
  %199 = fmul reassoc ninf nsz float %198, %183
  %200 = fadd reassoc ninf nsz float %199, 0x3FF4E33660000000
  %201 = fmul reassoc ninf nsz float %183, 0x3FE2C8B440000000
  %202 = fmul reassoc ninf nsz float %201, %200
  %203 = fadd reassoc ninf nsz float %194, %202
  %204 = fmul reassoc ninf nsz float %186, 0x3FD3A00620000000
  %205 = fsub reassoc ninf nsz float 0x3FE94CF0E0000000, %204
  %206 = fmul reassoc ninf nsz float %205, %186
  %207 = fadd reassoc ninf nsz float %206, 0xBFE9435AA0000000
  %208 = fmul reassoc ninf nsz float %207, %186
  %209 = fadd reassoc ninf nsz float %208, 0x3FF4E33660000000
  %210 = fmul reassoc ninf nsz float %186, 0x3FBD2F1AA0000000
  %211 = fmul reassoc ninf nsz float %210, %209
  %212 = fadd reassoc ninf nsz float %203, %211
  %213 = load float*, float** %59, align 8
  %214 = load i32, i32* %60, align 4
  %215 = sub i32 %214, %66
  %216 = mul i32 %215, %75
  %217 = add i32 %.03998, %216
  %218 = sext i32 %217 to i64
  %219 = getelementptr float, float* %213, i64 %218
  store float %212, float* %219, align 4
  %220 = add nsw i32 %.03998, 1
  %exitcond.not = icmp eq i32 %19, %220
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

true_block10:                                     ; preds = %true_block7
  %221 = getelementptr inbounds i8, i8* %63, i64 8
  %222 = bitcast i8* %221 to i32*
  %223 = load i32, i32* %222, align 4
  %224 = add i32 %223, -1
  %225 = icmp slt i32 %75, %224
  %226 = icmp sgt i32 %79, 0
  %or.cond = select i1 %225, i1 %226, i1 false
  br i1 %or.cond, label %true_block16, label %after_if9

true_block16:                                     ; preds = %true_block10
  %227 = getelementptr inbounds i8, i8* %63, i64 12
  %228 = bitcast i8* %227 to i32*
  %229 = load i32, i32* %228, align 4
  %230 = add i32 %229, -1
  %231 = icmp slt i32 %79, %230
  br i1 %231, label %true_block19, label %after_if9

true_block19:                                     ; preds = %true_block16
  %232 = add nsw i32 %75, -1
  %233 = insertelement <2 x i32> poison, i32 %79, i64 0
  %234 = shufflevector <2 x i32> %233, <2 x i32> poison, <2 x i32> zeroinitializer
  %235 = add nsw <2 x i32> %234, <i32 1, i32 -1>
  %236 = mul i32 %98, %232
  %237 = add nuw nsw i32 %75, 1
  %238 = mul i32 %98, %237
  %239 = mul i32 %112, %232
  %240 = mul i32 %112, %237
  %241 = insertelement <2 x i32> poison, i32 %236, i64 0
  %242 = shufflevector <2 x i32> %241, <2 x i32> poison, <2 x i32> zeroinitializer
  %243 = add <2 x i32> %242, %235
  %244 = sext <2 x i32> %243 to <2 x i64>
  %245 = insertelement <2 x float*> poison, float* %97, i64 0
  %246 = shufflevector <2 x float*> %245, <2 x float*> poison, <2 x i32> zeroinitializer
  %247 = getelementptr float, <2 x float*> %246, <2 x i64> %244
  %248 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %247, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %249 = insertelement <2 x i32> poison, i32 %238, i64 0
  %250 = shufflevector <2 x i32> %249, <2 x i32> poison, <2 x i32> zeroinitializer
  %251 = shufflevector <2 x i32> %235, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %252 = add <2 x i32> %250, %251
  %253 = sext <2 x i32> %252 to <2 x i64>
  %254 = getelementptr float, <2 x float*> %246, <2 x i64> %253
  %255 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %254, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %256 = fsub reassoc ninf nsz <2 x float> %248, %255
  %257 = call <2 x float> @llvm.fabs.v2f32(<2 x float> %256)
  %258 = fadd reassoc ninf nsz <2 x float> %257, <float 1.000000e+00, float 1.000000e+00>
  %259 = fdiv reassoc ninf nsz <2 x float> <float 1.000000e+00, float 1.000000e+00>, %258
  %260 = insertelement <2 x i32> poison, i32 %239, i64 0
  %261 = shufflevector <2 x i32> %260, <2 x i32> poison, <2 x i32> zeroinitializer
  %262 = add <2 x i32> %261, %235
  %263 = sext <2 x i32> %262 to <2 x i64>
  %264 = insertelement <2 x float*> poison, float* %110, i64 0
  %265 = shufflevector <2 x float*> %264, <2 x float*> poison, <2 x i32> zeroinitializer
  %266 = getelementptr float, <2 x float*> %265, <2 x i64> %263
  %267 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %266, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %268 = insertelement <2 x i32> poison, i32 %240, i64 0
  %269 = shufflevector <2 x i32> %268, <2 x i32> poison, <2 x i32> zeroinitializer
  %270 = add <2 x i32> %269, %251
  %271 = sext <2 x i32> %270 to <2 x i64>
  %272 = getelementptr float, <2 x float*> %265, <2 x i64> %271
  %273 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %272, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %274 = fadd reassoc ninf nsz <2 x float> %248, %255
  %275 = fsub reassoc ninf nsz <2 x float> %267, %274
  %276 = fadd reassoc ninf nsz <2 x float> %275, %273
  %277 = fmul reassoc ninf nsz <2 x float> %276, %259
  %shift = shufflevector <2 x float> %277, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %278 = fadd reassoc ninf nsz <2 x float> %277, %shift
  %279 = extractelement <2 x float> %278, i64 0
  %shift99 = shufflevector <2 x float> %259, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %280 = fadd reassoc ninf nsz <2 x float> %259, %shift99
  %281 = extractelement <2 x float> %280, i64 0
  %factor82 = fmul reassoc ninf nsz float %281, 2.000000e+00
  %282 = fdiv reassoc ninf nsz float %279, %factor82
  %283 = fadd reassoc ninf nsz float %282, %104
  br label %after_if9

true_block22:                                     ; preds = %after_if
  %284 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 1
  %285 = load float*, float** %284, align 8
  %286 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 0, i32 1
  %287 = load i32, i32* %286, align 4
  %288 = sub i32 %287, %66
  %289 = mul i32 %288, %75
  %290 = add i32 %.03998, %289
  %291 = sext i32 %290 to i64
  %292 = getelementptr float, float* %285, i64 %291
  %293 = load float, float* %292, align 4
  %294 = icmp sgt i32 %75, 0
  br i1 %294, label %true_block25, label %after_if9

false_block23:                                    ; preds = %after_if
  %.not64 = icmp eq i32 %93, %.03998
  br i1 %95, label %true_block37, label %false_block38

true_block25:                                     ; preds = %true_block22
  %295 = getelementptr inbounds i8, i8* %63, i64 8
  %296 = bitcast i8* %295 to i32*
  %297 = load i32, i32* %296, align 4
  %298 = add i32 %297, -1
  %299 = icmp slt i32 %75, %298
  %300 = icmp sgt i32 %79, 0
  %or.cond69 = select i1 %299, i1 %300, i1 false
  br i1 %or.cond69, label %true_block31, label %after_if9

true_block31:                                     ; preds = %true_block25
  %301 = getelementptr inbounds i8, i8* %63, i64 12
  %302 = bitcast i8* %301 to i32*
  %303 = load i32, i32* %302, align 4
  %304 = add i32 %303, -1
  %305 = icmp slt i32 %79, %304
  br i1 %305, label %true_block34, label %after_if9

true_block34:                                     ; preds = %true_block31
  %306 = add nsw i32 %75, -1
  %307 = insertelement <2 x i32> poison, i32 %79, i64 0
  %308 = shufflevector <2 x i32> %307, <2 x i32> poison, <2 x i32> zeroinitializer
  %309 = add nsw <2 x i32> %308, <i32 1, i32 -1>
  %310 = mul i32 %98, %306
  %311 = add nuw nsw i32 %75, 1
  %312 = mul i32 %98, %311
  %313 = mul i32 %287, %306
  %314 = mul i32 %287, %311
  %315 = insertelement <2 x i32> poison, i32 %310, i64 0
  %316 = shufflevector <2 x i32> %315, <2 x i32> poison, <2 x i32> zeroinitializer
  %317 = add <2 x i32> %316, %309
  %318 = sext <2 x i32> %317 to <2 x i64>
  %319 = insertelement <2 x float*> poison, float* %97, i64 0
  %320 = shufflevector <2 x float*> %319, <2 x float*> poison, <2 x i32> zeroinitializer
  %321 = getelementptr float, <2 x float*> %320, <2 x i64> %318
  %322 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %321, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %323 = insertelement <2 x i32> poison, i32 %312, i64 0
  %324 = shufflevector <2 x i32> %323, <2 x i32> poison, <2 x i32> zeroinitializer
  %325 = shufflevector <2 x i32> %309, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %326 = add <2 x i32> %324, %325
  %327 = sext <2 x i32> %326 to <2 x i64>
  %328 = getelementptr float, <2 x float*> %320, <2 x i64> %327
  %329 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %328, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %330 = fsub reassoc ninf nsz <2 x float> %322, %329
  %331 = call <2 x float> @llvm.fabs.v2f32(<2 x float> %330)
  %332 = fadd reassoc ninf nsz <2 x float> %331, <float 1.000000e+00, float 1.000000e+00>
  %333 = fdiv reassoc ninf nsz <2 x float> <float 1.000000e+00, float 1.000000e+00>, %332
  %334 = insertelement <2 x i32> poison, i32 %313, i64 0
  %335 = shufflevector <2 x i32> %334, <2 x i32> poison, <2 x i32> zeroinitializer
  %336 = add <2 x i32> %335, %309
  %337 = sext <2 x i32> %336 to <2 x i64>
  %338 = insertelement <2 x float*> poison, float* %285, i64 0
  %339 = shufflevector <2 x float*> %338, <2 x float*> poison, <2 x i32> zeroinitializer
  %340 = getelementptr float, <2 x float*> %339, <2 x i64> %337
  %341 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %340, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %342 = insertelement <2 x i32> poison, i32 %314, i64 0
  %343 = shufflevector <2 x i32> %342, <2 x i32> poison, <2 x i32> zeroinitializer
  %344 = add <2 x i32> %343, %325
  %345 = sext <2 x i32> %344 to <2 x i64>
  %346 = getelementptr float, <2 x float*> %339, <2 x i64> %345
  %347 = call <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*> %346, i32 4, <2 x i1> <i1 true, i1 true>, <2 x float> undef)
  %348 = fadd reassoc ninf nsz <2 x float> %322, %329
  %349 = fsub reassoc ninf nsz <2 x float> %341, %348
  %350 = fadd reassoc ninf nsz <2 x float> %349, %347
  %351 = fmul reassoc ninf nsz <2 x float> %350, %333
  %shift100 = shufflevector <2 x float> %351, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %352 = fadd reassoc ninf nsz <2 x float> %351, %shift100
  %353 = extractelement <2 x float> %352, i64 0
  %shift101 = shufflevector <2 x float> %333, <2 x float> poison, <2 x i32> <i32 1, i32 undef>
  %354 = fadd reassoc ninf nsz <2 x float> %333, %shift101
  %355 = extractelement <2 x float> %354, i64 0
  %factor = fmul reassoc ninf nsz float %355, 2.000000e+00
  %356 = fdiv reassoc ninf nsz float %353, %factor
  %357 = fadd reassoc ninf nsz float %356, %104
  br label %after_if9

true_block37:                                     ; preds = %false_block23
  br i1 %.not64, label %true_block40, label %false_block41

false_block38:                                    ; preds = %false_block23
  br i1 %.not64, label %true_block43, label %false_block44

after_if39:                                       ; preds = %false_block44, %true_block43, %false_block41, %true_block40
  %.026.in.in = phi i32* [ %358, %true_block40 ], [ %359, %false_block41 ], [ %360, %true_block43 ], [ %361, %false_block44 ]
  %.026.in = load i32, i32* %.026.in.in, align 4
  %.026 = icmp eq i32 %.026.in, 0
  br i1 %.026, label %true_block46, label %false_block47

true_block40:                                     ; preds = %true_block37
  %358 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 10
  br label %after_if39

false_block41:                                    ; preds = %true_block37
  %359 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 11
  br label %after_if39

true_block43:                                     ; preds = %false_block38
  %360 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 12
  br label %after_if39

false_block44:                                    ; preds = %false_block38
  %361 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 13
  br label %after_if39

true_block46:                                     ; preds = %after_if39
  %362 = icmp sgt i32 %79, 0
  br i1 %362, label %true_block49, label %after_if54

false_block47:                                    ; preds = %after_if39
  %363 = icmp sgt i32 %75, 0
  br i1 %363, label %true_block61, label %after_if66

true_block49:                                     ; preds = %true_block46
  %364 = getelementptr inbounds i8, i8* %63, i64 12
  %365 = bitcast i8* %364 to i32*
  %366 = load i32, i32* %365, align 4
  %367 = add i32 %366, -1
  %368 = icmp slt i32 %79, %367
  br i1 %368, label %true_block52, label %after_if54

true_block52:                                     ; preds = %true_block49
  %369 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 1
  %370 = load float*, float** %369, align 8
  %371 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 0, i32 1
  %372 = load i32, i32* %371, align 4
  %373 = sub i32 %372, %66
  %374 = mul i32 %373, %75
  %375 = add i32 %.03998, %374
  %376 = add i32 %375, -1
  %377 = sext i32 %376 to i64
  %378 = getelementptr float, float* %370, i64 %377
  %379 = load float, float* %378, align 4
  %380 = add i32 %101, -1
  %381 = sext i32 %380 to i64
  %382 = getelementptr float, float* %97, i64 %381
  %383 = load float, float* %382, align 4
  %384 = add i32 %375, 1
  %385 = sext i32 %384 to i64
  %386 = getelementptr float, float* %370, i64 %385
  %387 = load float, float* %386, align 4
  %388 = add i32 %101, 1
  %389 = sext i32 %388 to i64
  %390 = getelementptr float, float* %97, i64 %389
  %391 = load float, float* %390, align 4
  %392 = fadd reassoc ninf nsz float %379, %387
  %393 = fadd reassoc ninf nsz float %383, %391
  %394 = fsub reassoc ninf nsz float %392, %393
  %395 = fmul reassoc ninf nsz float %394, 5.000000e-01
  %396 = fadd reassoc ninf nsz float %395, %104
  br label %after_if54

after_if54:                                       ; preds = %true_block52, %true_block49, %true_block46
  %.135 = phi float [ %396, %true_block52 ], [ %104, %true_block46 ], [ %104, %true_block49 ]
  %397 = icmp sgt i32 %75, 0
  br i1 %397, label %true_block55, label %after_if9

true_block55:                                     ; preds = %after_if54
  %398 = getelementptr inbounds i8, i8* %63, i64 8
  %399 = bitcast i8* %398 to i32*
  %400 = load i32, i32* %399, align 4
  %401 = add i32 %400, -1
  %402 = icmp slt i32 %75, %401
  br i1 %402, label %true_block58, label %after_if9

true_block58:                                     ; preds = %true_block55
  %403 = add nsw i32 %75, -1
  %404 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 1
  %405 = load float*, float** %404, align 8
  %406 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 0, i32 1
  %407 = load i32, i32* %406, align 4
  %408 = mul i32 %407, %403
  %409 = sub i32 %408, %76
  %410 = add i32 %.03998, %409
  %411 = sext i32 %410 to i64
  %412 = getelementptr float, float* %405, i64 %411
  %413 = load float, float* %412, align 4
  %414 = mul i32 %98, %403
  %415 = sub i32 %414, %76
  %416 = add i32 %.03998, %415
  %417 = sext i32 %416 to i64
  %418 = getelementptr float, float* %97, i64 %417
  %419 = load float, float* %418, align 4
  %420 = add nuw nsw i32 %75, 1
  %421 = mul i32 %407, %420
  %422 = sub i32 %421, %76
  %423 = add i32 %.03998, %422
  %424 = sext i32 %423 to i64
  %425 = getelementptr float, float* %405, i64 %424
  %426 = load float, float* %425, align 4
  %427 = mul i32 %98, %420
  %428 = sub i32 %427, %76
  %429 = add i32 %.03998, %428
  %430 = sext i32 %429 to i64
  %431 = getelementptr float, float* %97, i64 %430
  %432 = load float, float* %431, align 4
  %433 = fadd reassoc ninf nsz float %413, %426
  %434 = fadd reassoc ninf nsz float %419, %432
  %435 = fsub reassoc ninf nsz float %433, %434
  %436 = fmul reassoc ninf nsz float %435, 5.000000e-01
  %437 = fadd reassoc ninf nsz float %436, %104
  br label %after_if9

true_block61:                                     ; preds = %false_block47
  %438 = getelementptr inbounds i8, i8* %63, i64 8
  %439 = bitcast i8* %438 to i32*
  %440 = load i32, i32* %439, align 4
  %441 = add i32 %440, -1
  %442 = icmp slt i32 %75, %441
  br i1 %442, label %true_block64, label %after_if66

true_block64:                                     ; preds = %true_block61
  %443 = add nsw i32 %75, -1
  %444 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 1
  %445 = load float*, float** %444, align 8
  %446 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 0, i32 1
  %447 = load i32, i32* %446, align 4
  %448 = mul i32 %447, %443
  %449 = sub i32 %448, %76
  %450 = add i32 %.03998, %449
  %451 = sext i32 %450 to i64
  %452 = getelementptr float, float* %445, i64 %451
  %453 = load float, float* %452, align 4
  %454 = mul i32 %98, %443
  %455 = sub i32 %454, %76
  %456 = add i32 %.03998, %455
  %457 = sext i32 %456 to i64
  %458 = getelementptr float, float* %97, i64 %457
  %459 = load float, float* %458, align 4
  %460 = add nuw nsw i32 %75, 1
  %461 = mul i32 %447, %460
  %462 = sub i32 %461, %76
  %463 = add i32 %.03998, %462
  %464 = sext i32 %463 to i64
  %465 = getelementptr float, float* %445, i64 %464
  %466 = load float, float* %465, align 4
  %467 = mul i32 %98, %460
  %468 = sub i32 %467, %76
  %469 = add i32 %.03998, %468
  %470 = sext i32 %469 to i64
  %471 = getelementptr float, float* %97, i64 %470
  %472 = load float, float* %471, align 4
  %473 = fadd reassoc ninf nsz float %453, %466
  %474 = fadd reassoc ninf nsz float %459, %472
  %475 = fsub reassoc ninf nsz float %473, %474
  %476 = fmul reassoc ninf nsz float %475, 5.000000e-01
  %477 = fadd reassoc ninf nsz float %476, %104
  br label %after_if66

after_if66:                                       ; preds = %true_block64, %true_block61, %false_block47
  %.2 = phi float [ %477, %true_block64 ], [ %104, %false_block47 ], [ %104, %true_block61 ]
  %478 = icmp sgt i32 %79, 0
  br i1 %478, label %true_block67, label %after_if9

true_block67:                                     ; preds = %after_if66
  %479 = getelementptr inbounds i8, i8* %63, i64 12
  %480 = bitcast i8* %479 to i32*
  %481 = load i32, i32* %480, align 4
  %482 = add i32 %481, -1
  %483 = icmp slt i32 %79, %482
  br i1 %483, label %true_block70, label %after_if9

true_block70:                                     ; preds = %true_block67
  %484 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 1
  %485 = load float*, float** %484, align 8
  %486 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %96, i64 0, i32 0, i32 0, i32 1
  %487 = load i32, i32* %486, align 4
  %488 = sub i32 %487, %66
  %489 = mul i32 %488, %75
  %490 = add i32 %.03998, %489
  %491 = add i32 %490, -1
  %492 = sext i32 %491 to i64
  %493 = getelementptr float, float* %485, i64 %492
  %494 = load float, float* %493, align 4
  %495 = add i32 %101, -1
  %496 = sext i32 %495 to i64
  %497 = getelementptr float, float* %97, i64 %496
  %498 = load float, float* %497, align 4
  %499 = add i32 %490, 1
  %500 = sext i32 %499 to i64
  %501 = getelementptr float, float* %485, i64 %500
  %502 = load float, float* %501, align 4
  %503 = add i32 %101, 1
  %504 = sext i32 %503 to i64
  %505 = getelementptr float, float* %97, i64 %504
  %506 = load float, float* %505, align 4
  %507 = fadd reassoc ninf nsz float %494, %502
  %508 = fadd reassoc ninf nsz float %498, %506
  %509 = fsub reassoc ninf nsz float %507, %508
  %510 = fmul reassoc ninf nsz float %509, 5.000000e-01
  %511 = fadd reassoc ninf nsz float %510, %104
  br label %after_if9
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.sqrt.f32(float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.108, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.108**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.108*, %struct.RuntimeContext.108** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.108*, i8*, i32)*, void (%struct.RuntimeContext.108*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.108*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.108*, i8*)*, void (%struct.RuntimeContext.108*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.108*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.108* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.108* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.108* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.108, %struct.RuntimeContext.108* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.108* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.108* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.108*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.108* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <2 x float> @llvm.masked.gather.v2f32.v2p0f32(<2 x float*>, i32 immarg, <2 x i1>, <2 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare <2 x float> @llvm.fabs.v2f32(<2 x float>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { nocallback nofree nosync nounwind readnone speculatable willreturn }

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
