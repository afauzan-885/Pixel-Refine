; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { %struct.RuntimeContext.420*, void (%struct.RuntimeContext.420*, i8*)*, void (%struct.RuntimeContext.420*, i8*, i32)*, void (%struct.RuntimeContext.420*, i8*)*, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.420 = type { i8*, %struct.LLVMRuntime.419*, i32, i64* }
%struct.LLVMRuntime.419 = type { %struct.PreallocatedMemoryChunk.415, %struct.PreallocatedMemoryChunk.415, i8* (i8*, i64, i64)*, void (i8*)*, void (i8*, ...)*, i32 (i8*, i64, i8*, i8*)*, i8*, [512 x i8*], [512 x i64], i8*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, [1024 x %struct.ListManager.416*], [1024 x %struct.NodeManager.417*], [1024 x i8*], i8*, %struct.RandState.418*, i8*, void (i8*, i8*)*, void (i8*)*, [2048 x i8], [32 x i64], i32, i64, i8*, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.415 = type { i8*, i8*, i64 }
%struct.ListManager.416 = type { [131072 x i8*], i64, i64, i32, i32, i32, %struct.LLVMRuntime.419* }
%struct.NodeManager.417 = type { %struct.LLVMRuntime.419*, i32, i32, i32, i32, %struct.ListManager.416*, %struct.ListManager.416*, %struct.ListManager.416*, i32 }
%struct.RandState.418 = type { i32, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_stitch_tile_batch_vec3_kernel_c744_0_kernel_0_serial(%struct.RuntimeContext.420* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.420* %context to { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }**
  %1 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %1, i64 0, i32 7
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.420, %struct.RuntimeContext.420* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime.419*, %struct.LLVMRuntime.419** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.419, %struct.LLVMRuntime.419* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  store i32 %3, i32* %8, align 4
  ret void
}

; Function Attrs: nounwind
define void @_stitch_tile_batch_vec3_kernel_c744_0_kernel_1_range_for(%struct.RuntimeContext.420* %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast %0* %0 to i8*
  call void @llvm.lifetime.start.p0i8(i64 56, i8* nonnull %1)
  %2 = getelementptr inbounds %0, %0* %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, %0* %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, %0* %0, i64 0, i32 0
  store %struct.RuntimeContext.420* %context, %struct.RuntimeContext.420** %4, align 8
  store void (%struct.RuntimeContext.420*, i8*)* null, void (%struct.RuntimeContext.420*, i8*)** %2, align 8
  store i64 1, i64* %3, align 8
  %5 = getelementptr inbounds %0, %0* %0, i64 0, i32 2
  store void (%struct.RuntimeContext.420*, i8*, i32)* @function_body, void (%struct.RuntimeContext.420*, i8*, i32)** %5, align 8
  %6 = getelementptr inbounds %0, %0* %0, i64 0, i32 3
  store void (%struct.RuntimeContext.420*, i8*)* null, void (%struct.RuntimeContext.420*, i8*)** %6, align 8
  %7 = getelementptr inbounds %0, %0* %0, i64 0, i32 5
  %8 = bitcast i32* %7 to <4 x i32>*
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, <4 x i32>* %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.420, %struct.RuntimeContext.420* %context, i64 0, i32 1
  %10 = load %struct.LLVMRuntime.419*, %struct.LLVMRuntime.419** %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.419, %struct.LLVMRuntime.419* %10, i64 0, i32 10
  %12 = load void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)*, void (i8*, i32, i32, i8*, void (i8*, i32, i32)*)** %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.419, %struct.LLVMRuntime.419* %10, i64 0, i32 9
  %14 = load i8*, i8** %13, align 8
  call void %12(i8* noundef %14, i32 noundef 8, i32 noundef 8, i8* noundef nonnull %1, void (i8*, i32, i32)* noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0i8(i64 56, i8* nonnull %1)
  ret void
}

; Function Attrs: nofree nounwind
define internal void @function_body(%struct.RuntimeContext.420* nocapture readonly %0, i8* nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.420, %struct.RuntimeContext.420* %0, i64 0, i32 1
  %4 = load %struct.LLVMRuntime.419*, %struct.LLVMRuntime.419** %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.419, %struct.LLVMRuntime.419* %4, i64 0, i32 14
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
  %20 = bitcast %struct.RuntimeContext.420* %0 to { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }**
  %21 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 8
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 9
  %25 = load i32, i32* %24, align 4
  %26 = tail call i32 @llvm.smax.i32(i32 %23, i32 0)
  %27 = tail call i32 @llvm.smax.i32(i32 %25, i32 0)
  %28 = mul i32 %27, %26
  %29 = icmp slt i32 %17, %19
  br i1 %29, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %30 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 5, i32 1
  %31 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 6, i32 1
  %32 = icmp sgt i32 %28, 0
  %33 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 2, i32 1
  %34 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 2, i32 0, i32 1
  %35 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %36 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %37 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %38 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %39 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 2
  %40 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 3
  %41 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 3, i32 1
  %42 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 3, i32 0, i32 1
  %43 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 3, i32 0, i32 2
  %44 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 4, i32 1
  %45 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32 }, float* }, { { i32, i32 }, float* }, { { i32 }, i32* }, { { i32 }, i32* }, i32, i32, i32 }* %21, i64 0, i32 4, i32 0, i32 1
  br i1 %32, label %for_loop_body.us.preheader, label %after_for

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  %46 = sext i32 %17 to i64
  %wide.trip.count = sext i32 %19 to i64
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_body.us.preheader
  %indvars.iv = phi i64 [ %46, %for_loop_body.us.preheader ], [ %indvars.iv.next, %for_loop_test4.after_for3_crit_edge.us ]
  %47 = load i32*, i32** %30, align 8
  %48 = getelementptr i32, i32* %47, i64 %indvars.iv
  %49 = load i32, i32* %48, align 4
  %50 = load i32*, i32** %31, align 8
  %51 = getelementptr i32, i32* %50, i64 %indvars.iv
  %52 = load i32, i32* %51, align 4
  %53 = trunc i64 %indvars.iv to i32
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body.us
  %.09.us = phi i32 [ 0, %for_loop_body.us ], [ %149, %for_loop_body1.us ]
  %54 = udiv i32 %.09.us, %27
  %.recomposed = urem i32 %.09.us, %27
  %55 = add i32 %54, %49
  %56 = add i32 %.recomposed, %52
  %57 = load float*, float** %33, align 8
  %58 = load i32, i32* %34, align 4
  %59 = mul i32 %58, %54
  %60 = add i32 %59, %.recomposed
  %61 = sext i32 %60 to i64
  %62 = getelementptr float, float* %57, i64 %61
  %63 = load float, float* %62, align 4
  %64 = load float*, float** %35, align 8
  %65 = load i32, i32* %36, align 4
  %66 = mul i32 %65, %54
  %67 = add i32 %66, %.recomposed
  %68 = sext i32 %67 to i64
  %69 = getelementptr float, float* %64, i64 %68
  %70 = load float, float* %69, align 4
  %71 = fmul reassoc ninf nsz float %70, %63
  %72 = load float*, float** %37, align 8
  %73 = load i32, i32* %38, align 4
  %74 = load i32, i32* %39, align 4
  %75 = load i32, i32* %40, align 4
  %76 = mul i32 %73, %53
  %77 = add i32 %76, %54
  %78 = mul i32 %77, %74
  %79 = add i32 %78, %.recomposed
  %80 = mul i32 %79, %75
  %81 = sext i32 %80 to i64
  %82 = getelementptr float, float* %72, i64 %81
  %83 = load float, float* %82, align 4
  %84 = fmul reassoc ninf nsz float %83, %71
  %85 = load float*, float** %41, align 8
  %86 = load i32, i32* %42, align 4
  %87 = load i32, i32* %43, align 4
  %88 = mul i32 %86, %55
  %89 = add i32 %88, %56
  %90 = mul i32 %89, %87
  %91 = sext i32 %90 to i64
  %92 = getelementptr float, float* %85, i64 %91
  %93 = atomicrmw fadd float* %92, float %84 seq_cst, align 4
  %94 = load float*, float** %37, align 8
  %95 = load i32, i32* %38, align 4
  %96 = load i32, i32* %39, align 4
  %97 = load i32, i32* %40, align 4
  %98 = mul i32 %95, %53
  %99 = add i32 %98, %54
  %100 = mul i32 %99, %96
  %101 = add i32 %100, %.recomposed
  %102 = mul i32 %101, %97
  %103 = add i32 %102, 1
  %104 = sext i32 %103 to i64
  %105 = getelementptr float, float* %94, i64 %104
  %106 = load float, float* %105, align 4
  %107 = fmul reassoc ninf nsz float %106, %71
  %108 = load float*, float** %41, align 8
  %109 = load i32, i32* %42, align 4
  %110 = load i32, i32* %43, align 4
  %111 = mul i32 %109, %55
  %112 = add i32 %111, %56
  %113 = mul i32 %112, %110
  %114 = add i32 %113, 1
  %115 = sext i32 %114 to i64
  %116 = getelementptr float, float* %108, i64 %115
  %117 = atomicrmw fadd float* %116, float %107 seq_cst, align 4
  %118 = load float*, float** %37, align 8
  %119 = load i32, i32* %38, align 4
  %120 = load i32, i32* %39, align 4
  %121 = load i32, i32* %40, align 4
  %122 = mul i32 %119, %53
  %123 = add i32 %122, %54
  %124 = mul i32 %123, %120
  %125 = add i32 %124, %.recomposed
  %126 = mul i32 %125, %121
  %127 = add i32 %126, 2
  %128 = sext i32 %127 to i64
  %129 = getelementptr float, float* %118, i64 %128
  %130 = load float, float* %129, align 4
  %131 = fmul reassoc ninf nsz float %130, %71
  %132 = load float*, float** %41, align 8
  %133 = load i32, i32* %42, align 4
  %134 = load i32, i32* %43, align 4
  %135 = mul i32 %133, %55
  %136 = add i32 %135, %56
  %137 = mul i32 %136, %134
  %138 = add i32 %137, 2
  %139 = sext i32 %138 to i64
  %140 = getelementptr float, float* %132, i64 %139
  %141 = atomicrmw fadd float* %140, float %131 seq_cst, align 4
  %142 = load float*, float** %44, align 8
  %143 = load i32, i32* %45, align 4
  %144 = mul i32 %143, %55
  %145 = add i32 %144, %56
  %146 = sext i32 %145 to i64
  %147 = getelementptr float, float* %142, i64 %146
  %148 = atomicrmw fadd float* %147, float %71 seq_cst, align 4
  %149 = add nuw nsw i32 %.09.us, 1
  %exitcond.not = icmp eq i32 %28, %149
  br i1 %exitcond.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_body1.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %for_loop_body1.us
  %indvars.iv.next = add nsw i64 %indvars.iv, 1
  %exitcond13.not = icmp eq i64 %indvars.iv.next, %wide.trip.count
  br i1 %exitcond13.not, label %after_for.loopexit, label %for_loop_body.us

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %for_loop_body.lr.ph, %allocs
  ret void
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.420, align 8
  %.sroa.0.0..sroa_cast = bitcast i8* %0 to %struct.RuntimeContext.420**
  %.sroa.0.0.copyload = load %struct.RuntimeContext.420*, %struct.RuntimeContext.420** %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast i8* %.sroa.4.0..sroa_idx to void (%struct.RuntimeContext.420*, i8*)**
  %.sroa.4.0.copyload = load void (%struct.RuntimeContext.420*, i8*)*, void (%struct.RuntimeContext.420*, i8*)** %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast i8* %.sroa.5.0..sroa_idx to void (%struct.RuntimeContext.420*, i8*, i32)**
  %.sroa.5.0.copyload = load void (%struct.RuntimeContext.420*, i8*, i32)*, void (%struct.RuntimeContext.420*, i8*, i32)** %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, i8* %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast i8* %.sroa.7.0..sroa_idx to void (%struct.RuntimeContext.420*, i8*)**
  %.sroa.7.0.copyload = load void (%struct.RuntimeContext.420*, i8*)*, void (%struct.RuntimeContext.420*, i8*)** %.sroa.7.0..sroa_cast, align 8
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
  %.not = icmp eq void (%struct.RuntimeContext.420*, i8*)* %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(%struct.RuntimeContext.420* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast %struct.RuntimeContext.420* %.sroa.0.0.copyload to i8*
  %9 = bitcast %struct.RuntimeContext.420* %4 to i8*
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* noundef nonnull align 8 dereferenceable(32) %9, i8* noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.420, %struct.RuntimeContext.420* %4, i64 0, i32 2
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.420* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.02038) #1
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
  call void %.sroa.5.0.copyload(%struct.RuntimeContext.420* noundef nonnull %4, i8* noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !11

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq void (%struct.RuntimeContext.420*, i8*)* %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(%struct.RuntimeContext.420* noundef %.sroa.0.0.copyload, i8* noundef nonnull %5) #1
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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
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
