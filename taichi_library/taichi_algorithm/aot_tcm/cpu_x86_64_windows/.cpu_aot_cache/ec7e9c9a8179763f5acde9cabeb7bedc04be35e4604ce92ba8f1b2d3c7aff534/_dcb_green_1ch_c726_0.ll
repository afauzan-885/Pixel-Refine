; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.120*, void (%struct.RuntimeContext.120*, i8*)*, void (%struct.RuntimeContext.120*, i8*, i32)*, void (%struct.RuntimeContext.120*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.120 = type { i8*, %struct.LLVMRuntime.119*, i32, i64* }
%struct.LLVMRuntime.119 = type { %struct.PreallocatedMemoryChunk.115, %struct.PreallocatedMemoryChunk.115, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.116*], [1024 x %struct.NodeManager.117*], [1024 x i8*], i8*, %struct.RandState.118*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.115 = type { i8*, i8*, i64 }
%struct.ListManager.116 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.119* }
%struct.NodeManager.117 = type { %struct.LLVMRuntime.119*, i32, i32, i32, i32, %struct.ListManager.116*, %struct.ListManager.116*, %struct.ListManager.116*, i32 }
%struct.RandState.118 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_dcb_green_1ch_c726_0_kernel_0_serial(%struct.RuntimeContext.120* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.120* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %1, i64 0, i32 8
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %11, i64 0, i32 9
  %13 = load i32, i32* %12, align 4
  %14 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %15 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %14, i64 0, i32 14
  %16 = load i8*, i8** %15, align 8
  %17 = getelementptr inbounds i8, i8* %16, i64 12
  %18 = bitcast i8* %17 to i32*
  store i32 %13, i32* %18, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %13, i32 0)
  %20 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %21 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %20, i64 0, i32 14
  %22 = load i8*, i8** %21, align 8
  %23 = getelementptr inbounds i8, i8* %22, i64 4
  %24 = bitcast i8* %23 to i32*
  store i32 %19, i32* %24, align 4
  %25 = mul i32 %19, %10
  %26 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %4, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %26, i64 0, i32 14
  %28 = bitcast i8** %27 to i32**
  %29 = load i32*, i32** %28, align 8
  store i32 %25, i32* %29, align 4
  ret void
}

; Function Attrs: nounwind
define void @_dcb_green_1ch_c726_0_kernel_1_range_for(%struct.RuntimeContext.120* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.120* %context, %struct.RuntimeContext.120** %4, align 8
  store void (%struct.RuntimeContext.120*, i8*)* null, void (%struct.RuntimeContext.120*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.120*, i8*, i32)* @function_body, void (%struct.RuntimeContext.120*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.120*, i8*)* null, void (%struct.RuntimeContext.120*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(%struct.RuntimeContext.120* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.120* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 10
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 11
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 12
  %27 = load i32, i32* %26, align 4
  %28 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %21, i64 0, i32 13
  %29 = load i32, i32* %28, align 4
  %30 = icmp slt i32 %17, %19
  br i1 %30, label %for_loop_body.preheader, label %after_for

for_loop_body.preheader:                          ; preds = %allocs
  %31 = sub i32 0, %17
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if12, %for_loop_body.preheader
  %lsr.iv = phi i32 [ %31, %for_loop_body.preheader ], [ %lsr.iv.next, %after_if12 ]
  %.04983 = phi i32 [ %140, %after_if12 ], [ %17, %for_loop_body.preheader ]
  %32 = load %struct.LLVMRuntime.119*, %struct.LLVMRuntime.119** %3, align 8
  %33 = getelementptr inbounds %struct.LLVMRuntime.119, %struct.LLVMRuntime.119* %32, i64 0, i32 14
  %34 = load i8*, i8** %33, align 8
  %35 = getelementptr inbounds i8, i8* %34, i64 4
  %36 = bitcast i8* %35 to i32*
  %37 = load i32, i32* %36, align 4
  %38 = sdiv i32 %.04983, %37
  %39 = mul i32 %38, %37
  %40 = xor i32 %37, %.04983
  %41 = icmp slt i32 %40, 0
  %42 = icmp ne i32 %.04983, 0
  %43 = icmp ne i32 %.04983, %39
  %44 = and i1 %42, %41
  %45 = and i1 %44, %43
  %.neg51 = sext i1 %45 to i32
  %46 = add i32 %38, %.neg51
  %47 = mul i32 %46, %37
  %48 = mul i32 %37, -1
  %49 = mul i32 %48, %46
  %50 = add i32 %.04983, %49
  %51 = sdiv i32 %46, 2
  %52 = icmp slt i32 %46, 0
  %53 = shl nsw i32 %51, 1
  %54 = icmp ne i32 %53, %46
  %55 = and i1 %52, %54
  %.neg52.neg = zext i1 %55 to i32
  %.neg54 = sub nsw i32 %.neg52.neg, %51
  %.neg53 = shl i32 %.neg54, 1
  %56 = sub i32 0, %46
  %57 = icmp eq i32 %.neg53, %56
  %58 = sdiv i32 %50, 2
  %59 = icmp slt i32 %50, 0
  %60 = shl nsw i32 %58, 1
  %61 = icmp ne i32 %50, %60
  %62 = and i1 %59, %61
  %.neg55.neg = zext i1 %62 to i32
  %.neg57 = sub nsw i32 %.neg55.neg, %58
  %.neg56 = shl i32 %.neg57, 1
  %63 = add i32 %lsr.iv, %47
  %.not = icmp eq i32 %63, %.neg56
  %. = select i1 %.not, i32 %23, i32 %25
  %.72 = select i1 %.not, i32 %27, i32 %29
  %.048 = select i1 %57, i32 %., i32 %.72
  switch i32 %.048, label %false_block11 [
    i32 3, label %true_block10
    i32 1, label %true_block10
  ]

after_for.loopexit:                               ; preds = %after_if12
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block10:                                     ; preds = %for_loop_body, %for_loop_body
  %64 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %65 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 6
  %66 = load float, float* %65, align 4
  %67 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 7
  %68 = load float, float* %67, align 4
  %69 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 3
  %70 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 1
  %71 = load float*, float** %70, align 8
  %72 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 0, i32 0, i32 1
  %73 = load i32, i32* %72, align 4
  %74 = sub i32 %73, %37
  %75 = mul i32 %74, %46
  %76 = add i32 %.04983, %75
  %77 = sext i32 %76 to i64
  %78 = getelementptr float, float* %71, i64 %77
  %79 = load float, float* %78, align 4
  %80 = fsub reassoc ninf nsz float %79, %66
  %81 = fsub reassoc ninf nsz float %68, %66
  %82 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %81, float 1.000000e+00)
  %83 = fdiv reassoc ninf nsz float %80, %82
  %84 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %83, float 0.000000e+00)
  %85 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %84, float 1.000000e+00)
  switch i32 %.048, label %after_if24 [
    i32 3, label %true_block28
    i32 2, label %true_block25
  ]

false_block11:                                    ; preds = %for_loop_body
  %86 = add i32 %46, -1
  %87 = tail call i32 @llvm.smax.i32(i32 %86, i32 0)
  %88 = getelementptr inbounds i8, i8* %34, i64 8
  %89 = bitcast i8* %88 to i32*
  %90 = load i32, i32* %89, align 4
  %91 = add i32 %90, -1
  %92 = add i32 %46, 1
  %93 = tail call i32 @llvm.smin.i32(i32 %91, i32 %92)
  %94 = add i32 %50, -1
  %95 = tail call i32 @llvm.smax.i32(i32 %94, i32 0)
  %96 = getelementptr inbounds i8, i8* %34, i64 12
  %97 = bitcast i8* %96 to i32*
  %98 = load i32, i32* %97, align 4
  %99 = add i32 %98, -1
  %100 = add i32 %50, 1
  %101 = tail call i32 @llvm.smin.i32(i32 %99, i32 %100)
  %102 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }** %20, align 8
  %103 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 6
  %104 = load float, float* %103, align 4
  %105 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 7
  %106 = load float, float* %105, align 4
  %107 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 2
  %108 = load float, float* %107, align 4
  %109 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 3
  %110 = load float, float* %109, align 4
  %111 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 4
  %112 = load float, float* %111, align 4
  %113 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 5
  %114 = load float, float* %113, align 4
  %115 = and i32 %95, 2147483646
  %.not61 = icmp eq i32 %95, %115
  %.75 = select i1 %.not61, i32 %23, i32 %25
  %.76 = select i1 %.not61, i32 %27, i32 %29
  %.040 = select i1 %57, i32 %.75, i32 %.76
  %116 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 0, i32 1
  %117 = load float*, float** %116, align 8
  %118 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %102, i64 0, i32 0, i32 0, i32 1
  %119 = load i32, i32* %118, align 4
  %120 = mul i32 %119, %46
  %121 = add i32 %120, %95
  %122 = sext i32 %121 to i64
  %123 = getelementptr float, float* %117, i64 %122
  %124 = load float, float* %123, align 4
  %125 = fsub reassoc ninf nsz float %124, %104
  %126 = fsub reassoc ninf nsz float %106, %104
  %127 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %126, float 1.000000e+00)
  %128 = fdiv reassoc ninf nsz float %125, %127
  %129 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %128, float 0.000000e+00)
  %130 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %129, float 1.000000e+00)
  switch i32 %.040, label %after_if42.fold.split [
    i32 0, label %after_if42
    i32 2, label %true_block43
    i32 3, label %true_block46
  ]

after_if12:                                       ; preds = %after_if96, %after_if24
  %.sink93 = phi { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* [ %102, %after_if96 ], [ %64, %after_if24 ]
  %.sink = phi float [ %194, %after_if96 ], [ %141, %after_if24 ]
  %131 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink93, i64 0, i32 1, i32 1
  %132 = load float*, float** %131, align 8
  %133 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %.sink93, i64 0, i32 1, i32 0, i32 1
  %134 = load i32, i32* %133, align 4
  %135 = sub i32 %134, %37
  %136 = mul i32 %135, %46
  %137 = add i32 %.04983, %136
  %138 = sext i32 %137 to i64
  %139 = getelementptr float, float* %132, i64 %138
  store float %.sink, float* %139, align 4
  %140 = add nsw i32 %.04983, 1
  %lsr.iv.next = add i32 %lsr.iv, -1
  %exitcond.not = icmp eq i32 %19, %140
  br i1 %exitcond.not, label %after_for.loopexit, label %for_loop_body

after_if24:                                       ; preds = %true_block28, %true_block25, %true_block10
  %.041.in = phi float* [ %142, %true_block25 ], [ %143, %true_block28 ], [ %69, %true_block10 ]
  %.041 = load float, float* %.041.in, align 4
  %141 = fmul reassoc ninf nsz float %.041, %85
  br label %after_if12

true_block25:                                     ; preds = %true_block10
  %142 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 4
  br label %after_if24

true_block28:                                     ; preds = %true_block10
  %143 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, float, float, float, float, float, float, i32, i32, i32, i32, i32, i32 }* %64, i64 0, i32 5
  br label %after_if24

after_if42.fold.split:                            ; preds = %false_block11
  br label %after_if42

after_if42:                                       ; preds = %true_block46, %true_block43, %after_if42.fold.split, %false_block11
  %.037 = phi float [ %112, %true_block43 ], [ %114, %true_block46 ], [ %108, %false_block11 ], [ %110, %after_if42.fold.split ]
  %144 = sdiv i32 %101, 2
  %145 = icmp slt i32 %101, 0
  %146 = shl nsw i32 %144, 1
  %147 = icmp ne i32 %146, %101
  %148 = and i1 %145, %147
  %.neg62.neg = zext i1 %148 to i32
  %.neg64 = sub nsw i32 %.neg62.neg, %144
  %.neg63 = shl i32 %.neg64, 1
  %149 = sub i32 0, %101
  %.not65 = icmp eq i32 %.neg63, %149
  %.77 = select i1 %.not65, i32 %23, i32 %25
  %.78 = select i1 %.not65, i32 %27, i32 %29
  %.036 = select i1 %57, i32 %.77, i32 %.78
  %150 = add i32 %120, %101
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, float* %117, i64 %151
  %153 = load float, float* %152, align 4
  %154 = fsub reassoc ninf nsz float %153, %104
  %155 = fdiv reassoc ninf nsz float %154, %127
  %156 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %155, float 0.000000e+00)
  %157 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %156, float 1.000000e+00)
  switch i32 %.036, label %after_if60.fold.split [
    i32 0, label %after_if60
    i32 2, label %true_block61
    i32 3, label %true_block64
  ]

true_block43:                                     ; preds = %false_block11
  br label %after_if42

true_block46:                                     ; preds = %false_block11
  br label %after_if42

after_if60.fold.split:                            ; preds = %after_if42
  br label %after_if60

after_if60:                                       ; preds = %true_block64, %true_block61, %after_if60.fold.split, %after_if42
  %.033 = phi float [ %112, %true_block61 ], [ %114, %true_block64 ], [ %108, %after_if42 ], [ %110, %after_if60.fold.split ]
  %158 = and i32 %87, 2147483646
  %159 = icmp eq i32 %87, %158
  %.032 = select i1 %159, i32 %., i32 %.72
  %160 = mul i32 %119, %87
  %161 = sub i32 %160, %47
  %162 = add i32 %.04983, %161
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %117, i64 %163
  %165 = load float, float* %164, align 4
  %166 = fsub reassoc ninf nsz float %165, %104
  %167 = fdiv reassoc ninf nsz float %166, %127
  %168 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %167, float 0.000000e+00)
  %169 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %168, float 1.000000e+00)
  switch i32 %.032, label %after_if78.fold.split [
    i32 0, label %after_if78
    i32 2, label %true_block79
    i32 3, label %true_block82
  ]

true_block61:                                     ; preds = %after_if42
  br label %after_if60

true_block64:                                     ; preds = %after_if42
  br label %after_if60

after_if78.fold.split:                            ; preds = %after_if60
  br label %after_if78

after_if78:                                       ; preds = %true_block82, %true_block79, %after_if78.fold.split, %after_if60
  %.029 = phi float [ %112, %true_block79 ], [ %114, %true_block82 ], [ %108, %after_if60 ], [ %110, %after_if78.fold.split ]
  %170 = sdiv i32 %93, 2
  %171 = icmp slt i32 %93, 0
  %172 = shl nsw i32 %170, 1
  %173 = icmp ne i32 %172, %93
  %174 = and i1 %171, %173
  %.neg69.neg = zext i1 %174 to i32
  %.neg71 = sub nsw i32 %.neg69.neg, %170
  %.neg70 = shl i32 %.neg71, 1
  %175 = sub i32 0, %93
  %176 = icmp eq i32 %.neg70, %175
  %.028 = select i1 %176, i32 %., i32 %.72
  %177 = mul i32 %119, %93
  %178 = sub i32 %177, %47
  %179 = add i32 %.04983, %178
  %180 = sext i32 %179 to i64
  %181 = getelementptr float, float* %117, i64 %180
  %182 = load float, float* %181, align 4
  %183 = fsub reassoc ninf nsz float %182, %104
  %184 = fdiv reassoc ninf nsz float %183, %127
  %185 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %184, float 0.000000e+00)
  %186 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %185, float 1.000000e+00)
  switch i32 %.028, label %after_if96.fold.split [
    i32 0, label %after_if96
    i32 2, label %true_block97
    i32 3, label %true_block100
  ]

true_block79:                                     ; preds = %after_if60
  br label %after_if78

true_block82:                                     ; preds = %after_if60
  br label %after_if78

after_if96.fold.split:                            ; preds = %after_if78
  br label %after_if96

after_if96:                                       ; preds = %true_block100, %true_block97, %after_if96.fold.split, %after_if78
  %.0 = phi float [ %112, %true_block97 ], [ %114, %true_block100 ], [ %108, %after_if78 ], [ %110, %after_if96.fold.split ]
  %187 = fmul reassoc ninf nsz float %.037, %130
  %188 = fmul reassoc ninf nsz float %.033, %157
  %189 = fadd reassoc ninf nsz float %188, %187
  %190 = fmul reassoc ninf nsz float %.029, %169
  %191 = fadd reassoc ninf nsz float %189, %190
  %192 = fmul reassoc ninf nsz float %.0, %186
  %193 = fadd reassoc ninf nsz float %191, %192
  %194 = fmul reassoc ninf nsz float %193, 2.500000e-01
  br label %after_if12

true_block97:                                     ; preds = %after_if78
  br label %after_if96

true_block100:                                    ; preds = %after_if78
  br label %after_if96
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.120, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.120**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.120*, %struct.RuntimeContext.120** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.120*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.120*, i8*)*, void (%struct.RuntimeContext.120*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.120*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.120*, i8*, i32)*, void (%struct.RuntimeContext.120*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.120*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.120*, i8*)*, void (%struct.RuntimeContext.120*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.120*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.120* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.120* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.120* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.120, %struct.RuntimeContext.120* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.120* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.120* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.120*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.120* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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
