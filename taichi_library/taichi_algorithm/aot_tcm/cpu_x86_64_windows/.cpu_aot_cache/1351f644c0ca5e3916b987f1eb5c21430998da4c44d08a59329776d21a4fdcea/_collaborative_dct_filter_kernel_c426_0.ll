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

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_collaborative_dct_filter_kernel_c426_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }**
  %1 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }** %0, align 8
  %2 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %1, i64 0, i32 9
  %3 = load float, float* %2, align 4
  %4 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %1, i64 0, i32 8
  %5 = load float, float* %4, align 4
  %6 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %7 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %8 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %7, i64 0, i32 14
  %9 = load i8*, i8** %8, align 8
  %10 = getelementptr inbounds i8, i8* %9, i64 8
  %11 = bitcast i8* %10 to float*
  store float %5, float* %11, align 4
  %12 = fmul reassoc ninf nsz float %5, %3
  %13 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %14 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %13, i64 0, i32 14
  %15 = load i8*, i8** %14, align 8
  %16 = getelementptr inbounds i8, i8* %15, i64 4
  %17 = bitcast i8* %16 to float*
  store float %12, float* %17, align 4
  %18 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }** %0, align 8
  %19 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %18, i64 0, i32 5
  %20 = load i32, i32* %19, align 4
  %21 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %6, align 8
  %22 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %21, i64 0, i32 14
  %23 = bitcast i8** %22 to i32**
  %24 = load i32*, i32** %23, align 8
  store i32 %20, i32* %24, align 4
  ret void
}

; Function Attrs: nounwind
define void @_collaborative_dct_filter_kernel_c426_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }**
  %21 = load { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }*, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }** %20, align 8
  %22 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 6
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 7
  %25 = load i32, i32* %24, align 4
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_test4.preheader.lr.ph, label %after_for

for_loop_test4.preheader.lr.ph:                   ; preds = %allocs
  %27 = icmp sgt i32 %23, 0
  %28 = icmp sgt i32 %25, 0
  %29 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 3, i32 1
  %30 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 3, i32 0, i32 1
  %31 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 1
  %32 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 1
  %33 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 2
  %34 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 0, i32 0, i32 3
  %35 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 4, i32 1
  %36 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 4, i32 0, i32 1
  %37 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 4, i32 0, i32 2
  %38 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 4, i32 0, i32 3
  %39 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 1
  %40 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 1
  %41 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 2
  %42 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 1, i32 0, i32 3
  %43 = getelementptr { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }, { { { i32, i32, i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, { { i32 }, float* }, { { i32, i32 }, float* }, { { i32, i32, i32, i32 }, float* }, i32, i32, i32, float, float }* %21, i64 0, i32 2, i32 1
  %44 = sext i32 %17 to i64
  %wide.trip.count194 = sext i32 %19 to i64
  br i1 %27, label %for_loop_test4.preheader.us.preheader, label %for_loop_test4.preheader.preheader

for_loop_test4.preheader.preheader:               ; preds = %for_loop_test4.preheader.lr.ph
  %45 = sub nsw i64 %wide.trip.count194, %44
  %46 = xor i64 %44, -1
  %47 = add nsw i64 %46, %wide.trip.count194
  %xtraiter323 = and i64 %45, 3
  %lcmp.mod324.not = icmp eq i64 %xtraiter323, 0
  br i1 %lcmp.mod324.not, label %for_loop_test4.preheader.prol.loopexit, label %for_loop_test4.preheader.prol.preheader

for_loop_test4.preheader.prol.preheader:          ; preds = %for_loop_test4.preheader.preheader
  %48 = shl nuw nsw i64 %xtraiter323, 2
  br label %for_loop_test4.preheader.prol

for_loop_test4.preheader.prol:                    ; preds = %for_loop_test4.preheader.prol, %for_loop_test4.preheader.prol.preheader
  %lsr.iv447 = phi i64 [ %48, %for_loop_test4.preheader.prol.preheader ], [ %lsr.iv.next448, %for_loop_test4.preheader.prol ]
  %indvars.iv196.prol = phi i64 [ %indvars.iv.next197.prol, %for_loop_test4.preheader.prol ], [ %44, %for_loop_test4.preheader.prol.preheader ]
  %49 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %50 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %49, i64 0, i32 14
  %51 = load i8*, i8** %50, align 8
  %52 = getelementptr inbounds i8, i8* %51, i64 8
  %53 = bitcast i8* %52 to float*
  %54 = load float, float* %53, align 4
  %55 = fmul reassoc ninf nsz float %54, %54
  %56 = fdiv reassoc ninf nsz float 1.000000e+00, %55
  %57 = load float*, float** %43, align 8
  %scevgep446 = getelementptr float, float* %57, i64 %indvars.iv196.prol
  store float %56, float* %scevgep446, align 4
  %indvars.iv.next197.prol = add nsw i64 %indvars.iv196.prol, 1
  %lsr.iv.next448 = add nsw i64 %lsr.iv447, -4
  %prol.iter325.cmp.not = icmp eq i64 %lsr.iv.next448, 0
  br i1 %prol.iter325.cmp.not, label %for_loop_test4.preheader.prol.loopexit.loopexit, label %for_loop_test4.preheader.prol, !llvm.loop !9

for_loop_test4.preheader.prol.loopexit.loopexit:  ; preds = %for_loop_test4.preheader.prol
  br label %for_loop_test4.preheader.prol.loopexit

for_loop_test4.preheader.prol.loopexit:           ; preds = %for_loop_test4.preheader.prol.loopexit.loopexit, %for_loop_test4.preheader.preheader
  %indvars.iv196.unr = phi i64 [ %44, %for_loop_test4.preheader.preheader ], [ %indvars.iv.next197.prol, %for_loop_test4.preheader.prol.loopexit.loopexit ]
  %58 = icmp ult i64 %47, 3
  br i1 %58, label %after_for, label %for_loop_test4.preheader.preheader346

for_loop_test4.preheader.preheader346:            ; preds = %for_loop_test4.preheader.prol.loopexit
  br label %for_loop_test4.preheader

for_loop_test4.preheader.us.preheader:            ; preds = %for_loop_test4.preheader.lr.ph
  %wide.trip.count186 = zext i32 %25 to i64
  %59 = add nsw i64 %wide.trip.count186, -1
  %60 = and i64 %wide.trip.count186, 4294967280
  %61 = add nsw i64 %60, -16
  %62 = lshr exact i64 %61, 4
  %63 = add nuw nsw i64 %62, 1
  %min.iters.check262 = icmp ult i32 %25, 16
  %64 = trunc i64 %59 to i32
  %65 = icmp ugt i64 %59, 4294967295
  %xtraiter = and i64 %63, 1
  %66 = icmp eq i64 %61, 0
  %unroll_iter = and i64 %63, 2305843009213693950
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %cmp.n267 = icmp eq i64 %60, %wide.trip.count186
  %xtraiter294 = and i64 %wide.trip.count186, 3
  %lcmp.mod295.not = icmp eq i64 %xtraiter294, 0
  %67 = sub i64 0, %xtraiter294
  br label %for_loop_test4.preheader.us

for_loop_test4.preheader.us:                      ; preds = %for_loop_test4.after_for3_crit_edge.us, %for_loop_test4.preheader.us.preheader
  %indvar = phi i32 [ 0, %for_loop_test4.preheader.us.preheader ], [ %indvar.next, %for_loop_test4.after_for3_crit_edge.us ]
  %indvars.iv191 = phi i64 [ %44, %for_loop_test4.preheader.us.preheader ], [ %indvars.iv.next192, %for_loop_test4.after_for3_crit_edge.us ]
  %lsr439 = trunc i64 %indvars.iv191 to i32
  %68 = add i32 %17, %indvar
  br label %for_loop_test8.preheader.us

after_for43.us.loopexit:                          ; preds = %for_loop_test48.after_for47_crit_edge.us.us
  br label %after_for43.us

after_for43.us:                                   ; preds = %for_loop_test8.preheader.us, %for_loop_test20.preheader.us, %for_loop_test32.preheader.us, %for_loop_test44.preheader.us, %after_for43.us.loopexit
  %.1.lcssa.us202 = phi i32 [ %.3.us.us.us, %for_loop_test44.preheader.us ], [ %.3.us.us.us, %for_loop_test32.preheader.us ], [ %.06996.us, %for_loop_test20.preheader.us ], [ %.06996.us, %for_loop_test8.preheader.us ], [ %.3.us.us.us, %after_for43.us.loopexit ]
  %69 = add nuw nsw i32 %.06897.us, 1
  %exitcond190.not = icmp eq i32 %69, %23
  br i1 %exitcond190.not, label %for_loop_test4.after_for3_crit_edge.us, label %for_loop_test8.preheader.us

for_loop_test44.preheader.us:                     ; preds = %for_loop_test36.after_for35_crit_edge.us.us
  br i1 true, label %for_loop_test52.preheader.us.us.us.preheader.preheader, label %after_for43.us

for_loop_test52.preheader.us.us.us.preheader.preheader: ; preds = %for_loop_test44.preheader.us
  br label %for_loop_test52.preheader.us.us.us.preheader

for_loop_test32.preheader.us:                     ; preds = %for_loop_test24.after_for23_crit_edge.us.us
  br i1 true, label %for_loop_test40.preheader.us.us.us.preheader.preheader, label %after_for43.us

for_loop_test40.preheader.us.us.us.preheader.preheader: ; preds = %for_loop_test32.preheader.us
  br label %for_loop_test40.preheader.us.us.us.preheader

for_loop_test20.preheader.us:                     ; preds = %for_loop_test12.after_for11_crit_edge.split.us.us.us.us
  br i1 true, label %for_loop_test28.preheader.us.us.us.preheader.preheader, label %after_for43.us

for_loop_test28.preheader.us.us.us.preheader.preheader: ; preds = %for_loop_test20.preheader.us
  br label %for_loop_test28.preheader.us.us.us.preheader

for_loop_test8.preheader.us:                      ; preds = %after_for43.us, %for_loop_test4.preheader.us
  %.06897.us = phi i32 [ 0, %for_loop_test4.preheader.us ], [ %69, %after_for43.us ]
  %.06996.us = phi i32 [ 0, %for_loop_test4.preheader.us ], [ %.1.lcssa.us202, %after_for43.us ]
  br i1 %28, label %for_loop_test12.preheader.us.us.us.preheader, label %after_for43.us

for_loop_test12.preheader.us.us.us.preheader:     ; preds = %for_loop_test8.preheader.us
  br label %for_loop_test12.preheader.us.us.us

for_loop_test4.after_for3_crit_edge.us:           ; preds = %after_for43.us
  %70 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %71 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %70, i64 0, i32 14
  %72 = load i8*, i8** %71, align 8
  %73 = getelementptr inbounds i8, i8* %72, i64 8
  %74 = bitcast i8* %73 to float*
  %75 = load float, float* %74, align 4
  %76 = tail call i32 @llvm.smax.i32(i32 %.1.lcssa.us202, i32 1)
  %77 = sitofp i32 %76 to float
  %78 = fmul reassoc ninf nsz float %75, %75
  %79 = fmul reassoc ninf nsz float %78, %77
  %80 = fdiv reassoc ninf nsz float 1.000000e+00, %79
  %81 = load float*, float** %43, align 8
  %82 = getelementptr float, float* %81, i64 %indvars.iv191
  store float %80, float* %82, align 4
  %indvars.iv.next192 = add nsw i64 %indvars.iv191, 1
  %indvar.next = add i32 %indvar, 1
  %exitcond195.not = icmp eq i64 %indvars.iv.next192, %wide.trip.count194
  br i1 %exitcond195.not, label %after_for.loopexit, label %for_loop_test4.preheader.us

for_loop_test28.preheader.us.us.us.preheader:     ; preds = %for_loop_test24.after_for23_crit_edge.us.us, %for_loop_test28.preheader.us.us.us.preheader.preheader
  %.06384.us.us = phi i32 [ %83, %for_loop_test24.after_for23_crit_edge.us.us ], [ 0, %for_loop_test28.preheader.us.us.us.preheader.preheader ]
  %.183.us.us = phi i32 [ %.3.us.us.us, %for_loop_test24.after_for23_crit_edge.us.us ], [ %.06996.us, %for_loop_test28.preheader.us.us.us.preheader.preheader ]
  br label %for_loop_test28.preheader.us.us.us

for_loop_test24.after_for23_crit_edge.us.us:      ; preds = %after_if.us.us.us
  %83 = add nuw nsw i32 %.06384.us.us, 1
  %exitcond173.not = icmp eq i32 %83, %25
  br i1 %exitcond173.not, label %for_loop_test32.preheader.us, label %for_loop_test28.preheader.us.us.us.preheader

for_loop_test28.preheader.us.us.us:               ; preds = %after_if.us.us.us, %for_loop_test28.preheader.us.us.us.preheader
  %.06281.us.us.us = phi i32 [ %169, %after_if.us.us.us ], [ 0, %for_loop_test28.preheader.us.us.us.preheader ]
  %.280.us.us.us = phi i32 [ %.3.us.us.us, %after_if.us.us.us ], [ %.183.us.us, %for_loop_test28.preheader.us.us.us.preheader ]
  %84 = load float*, float** %35, align 8
  %85 = load i32, i32* %36, align 4
  %86 = load i32, i32* %37, align 4
  %87 = load i32, i32* %38, align 4
  %88 = mul i32 %85, %lsr439
  %89 = add i32 %88, %.06897.us
  %90 = mul i32 %89, %86
  %91 = add i32 %90, %.06384.us.us
  %92 = mul i32 %91, %87
  %93 = load float*, float** %29, align 8
  %94 = load i32, i32* %30, align 4
  %95 = mul i32 %94, %.06281.us.us.us
  br i1 %min.iters.check262, label %for_loop_body25.us.us.us.preheader, label %vector.scevcheck238

vector.scevcheck238:                              ; preds = %for_loop_test28.preheader.us.us.us
  %96 = add i32 %92, %64
  %97 = icmp slt i32 %96, %92
  %98 = add i32 %95, %64
  %99 = icmp slt i32 %98, %95
  %100 = or i1 %99, %65
  %101 = or i1 %97, %100
  br i1 %101, label %for_loop_body25.us.us.us.preheader, label %vector.ph242

vector.ph242:                                     ; preds = %vector.scevcheck238
  br i1 %66, label %middle.block239.unr-lcssa, label %vector.body247.preheader

vector.body247.preheader:                         ; preds = %vector.ph242
  br label %vector.body247

vector.body247:                                   ; preds = %vector.body247, %vector.body247.preheader
  %lsr.iv376 = phi i64 [ %unroll_iter, %vector.body247.preheader ], [ %lsr.iv.next377, %vector.body247 ]
  %lsr.iv374 = phi i32 [ %95, %vector.body247.preheader ], [ %lsr.iv.next375, %vector.body247 ]
  %lsr.iv372 = phi i32 [ %92, %vector.body247.preheader ], [ %lsr.iv.next373, %vector.body247 ]
  %index248 = phi i64 [ %index.next255.1, %vector.body247 ], [ 0, %vector.body247.preheader ]
  %vec.phi249 = phi <8 x float> [ %130, %vector.body247 ], [ zeroinitializer, %vector.body247.preheader ]
  %vec.phi250 = phi <8 x float> [ %131, %vector.body247 ], [ zeroinitializer, %vector.body247.preheader ]
  %102 = sext i32 %lsr.iv372 to i64
  %103 = getelementptr float, float* %84, i64 %102
  %104 = bitcast float* %103 to <8 x float>*
  %wide.load251 = load <8 x float>, <8 x float>* %104, align 4
  %105 = getelementptr float, float* %103, i64 8
  %106 = bitcast float* %105 to <8 x float>*
  %wide.load252 = load <8 x float>, <8 x float>* %106, align 4
  %107 = sext i32 %lsr.iv374 to i64
  %108 = getelementptr float, float* %93, i64 %107
  %109 = bitcast float* %108 to <8 x float>*
  %wide.load253 = load <8 x float>, <8 x float>* %109, align 4
  %110 = getelementptr float, float* %108, i64 8
  %111 = bitcast float* %110 to <8 x float>*
  %wide.load254 = load <8 x float>, <8 x float>* %111, align 4
  %112 = fmul reassoc ninf nsz <8 x float> %wide.load253, %wide.load251
  %113 = fmul reassoc ninf nsz <8 x float> %wide.load254, %wide.load252
  %114 = fadd reassoc ninf nsz <8 x float> %112, %vec.phi249
  %115 = fadd reassoc ninf nsz <8 x float> %113, %vec.phi250
  %116 = add i32 %lsr.iv372, 16
  %117 = sext i32 %116 to i64
  %118 = getelementptr float, float* %84, i64 %117
  %119 = bitcast float* %118 to <8 x float>*
  %wide.load251.1 = load <8 x float>, <8 x float>* %119, align 4
  %120 = getelementptr float, float* %118, i64 8
  %121 = bitcast float* %120 to <8 x float>*
  %wide.load252.1 = load <8 x float>, <8 x float>* %121, align 4
  %122 = add i32 %lsr.iv374, 16
  %123 = sext i32 %122 to i64
  %124 = getelementptr float, float* %93, i64 %123
  %125 = bitcast float* %124 to <8 x float>*
  %wide.load253.1 = load <8 x float>, <8 x float>* %125, align 4
  %126 = getelementptr float, float* %124, i64 8
  %127 = bitcast float* %126 to <8 x float>*
  %wide.load254.1 = load <8 x float>, <8 x float>* %127, align 4
  %128 = fmul reassoc ninf nsz <8 x float> %wide.load253.1, %wide.load251.1
  %129 = fmul reassoc ninf nsz <8 x float> %wide.load254.1, %wide.load252.1
  %130 = fadd reassoc ninf nsz <8 x float> %128, %114
  %131 = fadd reassoc ninf nsz <8 x float> %129, %115
  %index.next255.1 = add i64 %index248, 32
  %lsr.iv.next373 = add i32 %lsr.iv372, 32
  %lsr.iv.next375 = add i32 %lsr.iv374, 32
  %lsr.iv.next377 = add i64 %lsr.iv376, -2
  %niter301.ncmp.1 = icmp eq i64 %lsr.iv.next377, 0
  br i1 %niter301.ncmp.1, label %middle.block239.unr-lcssa.loopexit, label %vector.body247, !llvm.loop !11

middle.block239.unr-lcssa.loopexit:               ; preds = %vector.body247
  br label %middle.block239.unr-lcssa

middle.block239.unr-lcssa:                        ; preds = %middle.block239.unr-lcssa.loopexit, %vector.ph242
  %.lcssa284.ph = phi <8 x float> [ undef, %vector.ph242 ], [ %130, %middle.block239.unr-lcssa.loopexit ]
  %.lcssa283.ph = phi <8 x float> [ undef, %vector.ph242 ], [ %131, %middle.block239.unr-lcssa.loopexit ]
  %index248.unr = phi i64 [ 0, %vector.ph242 ], [ %index.next255.1, %middle.block239.unr-lcssa.loopexit ]
  %vec.phi249.unr = phi <8 x float> [ zeroinitializer, %vector.ph242 ], [ %130, %middle.block239.unr-lcssa.loopexit ]
  %vec.phi250.unr = phi <8 x float> [ zeroinitializer, %vector.ph242 ], [ %131, %middle.block239.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block239, label %vector.body247.epil

vector.body247.epil:                              ; preds = %middle.block239.unr-lcssa
  %132 = trunc i64 %index248.unr to i32
  %133 = add i32 %92, %132
  %134 = sext i32 %133 to i64
  %135 = getelementptr float, float* %84, i64 %134
  %136 = bitcast float* %135 to <8 x float>*
  %wide.load251.epil = load <8 x float>, <8 x float>* %136, align 4
  %137 = getelementptr float, float* %135, i64 8
  %138 = bitcast float* %137 to <8 x float>*
  %wide.load252.epil = load <8 x float>, <8 x float>* %138, align 4
  %139 = add i32 %95, %132
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, float* %93, i64 %140
  %142 = bitcast float* %141 to <8 x float>*
  %wide.load253.epil = load <8 x float>, <8 x float>* %142, align 4
  %143 = getelementptr float, float* %141, i64 8
  %144 = bitcast float* %143 to <8 x float>*
  %wide.load254.epil = load <8 x float>, <8 x float>* %144, align 4
  %145 = fmul reassoc ninf nsz <8 x float> %wide.load253.epil, %wide.load251.epil
  %146 = fmul reassoc ninf nsz <8 x float> %wide.load254.epil, %wide.load252.epil
  %147 = fadd reassoc ninf nsz <8 x float> %145, %vec.phi249.unr
  %148 = fadd reassoc ninf nsz <8 x float> %146, %vec.phi250.unr
  br label %middle.block239

middle.block239:                                  ; preds = %vector.body247.epil, %middle.block239.unr-lcssa
  %.lcssa284 = phi <8 x float> [ %.lcssa284.ph, %middle.block239.unr-lcssa ], [ %147, %vector.body247.epil ]
  %.lcssa283 = phi <8 x float> [ %.lcssa283.ph, %middle.block239.unr-lcssa ], [ %148, %vector.body247.epil ]
  %bin.rdx256 = fadd reassoc ninf nsz <8 x float> %.lcssa283, %.lcssa284
  %149 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx256)
  br i1 %cmp.n267, label %for_loop_test28.after_for27_crit_edge.us.us.us, label %for_loop_body25.us.us.us.preheader

for_loop_body25.us.us.us.preheader:               ; preds = %middle.block239, %vector.scevcheck238, %for_loop_test28.preheader.us.us.us
  %indvars.iv167.ph = phi i64 [ 0, %vector.scevcheck238 ], [ 0, %for_loop_test28.preheader.us.us.us ], [ %60, %middle.block239 ]
  %.06177.us.us.us.ph = phi float [ 0.000000e+00, %vector.scevcheck238 ], [ 0.000000e+00, %for_loop_test28.preheader.us.us.us ], [ %149, %middle.block239 ]
  %150 = xor i64 %indvars.iv167.ph, -1
  %151 = add nsw i64 %150, %wide.trip.count186
  br i1 %lcmp.mod295.not, label %for_loop_body25.us.us.us.prol.loopexit, label %for_loop_body25.us.us.us.prol.preheader

for_loop_body25.us.us.us.prol.preheader:          ; preds = %for_loop_body25.us.us.us.preheader
  %152 = zext i32 %95 to i64
  %153 = zext i32 %92 to i64
  br label %for_loop_body25.us.us.us.prol

for_loop_body25.us.us.us.prol:                    ; preds = %for_loop_body25.us.us.us.prol, %for_loop_body25.us.us.us.prol.preheader
  %lsr.iv380 = phi i64 [ %xtraiter294, %for_loop_body25.us.us.us.prol.preheader ], [ %lsr.iv.next381, %for_loop_body25.us.us.us.prol ]
  %indvars.iv167.prol = phi i64 [ %indvars.iv.next168.prol, %for_loop_body25.us.us.us.prol ], [ %indvars.iv167.ph, %for_loop_body25.us.us.us.prol.preheader ]
  %.06177.us.us.us.prol = phi float [ %163, %for_loop_body25.us.us.us.prol ], [ %.06177.us.us.us.ph, %for_loop_body25.us.us.us.prol.preheader ]
  %154 = add i64 %153, %indvars.iv167.prol
  %tmp379 = trunc i64 %154 to i32
  %155 = sext i32 %tmp379 to i64
  %156 = getelementptr float, float* %84, i64 %155
  %157 = load float, float* %156, align 4
  %158 = add i64 %152, %indvars.iv167.prol
  %tmp378 = trunc i64 %158 to i32
  %159 = sext i32 %tmp378 to i64
  %160 = getelementptr float, float* %93, i64 %159
  %161 = load float, float* %160, align 4
  %162 = fmul reassoc ninf nsz float %161, %157
  %163 = fadd reassoc ninf nsz float %162, %.06177.us.us.us.prol
  %indvars.iv.next168.prol = add nuw nsw i64 %indvars.iv167.prol, 1
  %lsr.iv.next381 = add nsw i64 %lsr.iv380, -1
  %prol.iter304.cmp.not = icmp eq i64 %lsr.iv.next381, 0
  br i1 %prol.iter304.cmp.not, label %for_loop_body25.us.us.us.prol.loopexit.loopexit, label %for_loop_body25.us.us.us.prol, !llvm.loop !13

for_loop_body25.us.us.us.prol.loopexit.loopexit:  ; preds = %for_loop_body25.us.us.us.prol
  %164 = add i64 %xtraiter294, %indvars.iv167.ph
  br label %for_loop_body25.us.us.us.prol.loopexit

for_loop_body25.us.us.us.prol.loopexit:           ; preds = %for_loop_body25.us.us.us.prol.loopexit.loopexit, %for_loop_body25.us.us.us.preheader
  %.lcssa285.unr = phi float [ undef, %for_loop_body25.us.us.us.preheader ], [ %163, %for_loop_body25.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv167.unr = phi i64 [ %indvars.iv167.ph, %for_loop_body25.us.us.us.preheader ], [ %164, %for_loop_body25.us.us.us.prol.loopexit.loopexit ]
  %.06177.us.us.us.unr = phi float [ %.06177.us.us.us.ph, %for_loop_body25.us.us.us.preheader ], [ %163, %for_loop_body25.us.us.us.prol.loopexit.loopexit ]
  %165 = icmp ult i64 %151, 3
  br i1 %165, label %for_loop_test28.after_for27_crit_edge.us.us.us, label %for_loop_body25.us.us.us.preheader344

for_loop_body25.us.us.us.preheader344:            ; preds = %for_loop_body25.us.us.us.prol.loopexit
  %166 = zext i32 %92 to i64
  %167 = zext i32 %95 to i64
  br label %for_loop_body25.us.us.us

false_block.us.us.us:                             ; preds = %for_loop_test28.after_for27_crit_edge.us.us.us
  store float 0.000000e+00, float* %229, align 4
  br label %after_if.us.us.us

true_block.us.us.us:                              ; preds = %for_loop_test28.after_for27_crit_edge.us.us.us
  store float %.lcssa209, float* %229, align 4
  %168 = add i32 %.280.us.us.us, 1
  br label %after_if.us.us.us

after_if.us.us.us:                                ; preds = %true_block.us.us.us, %false_block.us.us.us
  %.3.us.us.us = phi i32 [ %168, %true_block.us.us.us ], [ %.280.us.us.us, %false_block.us.us.us ]
  %169 = add nuw nsw i32 %.06281.us.us.us, 1
  %exitcond172.not = icmp eq i32 %169, %25
  br i1 %exitcond172.not, label %for_loop_test24.after_for23_crit_edge.us.us, label %for_loop_test28.preheader.us.us.us

for_loop_body25.us.us.us:                         ; preds = %for_loop_body25.us.us.us, %for_loop_body25.us.us.us.preheader344
  %indvars.iv167 = phi i64 [ %indvars.iv.next168.3, %for_loop_body25.us.us.us ], [ %indvars.iv167.unr, %for_loop_body25.us.us.us.preheader344 ]
  %.06177.us.us.us = phi float [ %209, %for_loop_body25.us.us.us ], [ %.06177.us.us.us.unr, %for_loop_body25.us.us.us.preheader344 ]
  %170 = add i64 %166, %indvars.iv167
  %tmp389 = trunc i64 %170 to i32
  %171 = sext i32 %tmp389 to i64
  %172 = getelementptr float, float* %84, i64 %171
  %173 = load float, float* %172, align 4
  %174 = add i64 %167, %indvars.iv167
  %tmp388 = trunc i64 %174 to i32
  %175 = sext i32 %tmp388 to i64
  %176 = getelementptr float, float* %93, i64 %175
  %177 = load float, float* %176, align 4
  %178 = fmul reassoc ninf nsz float %177, %173
  %179 = fadd reassoc ninf nsz float %178, %.06177.us.us.us
  %180 = add i64 %170, 1
  %tmp386 = trunc i64 %180 to i32
  %181 = sext i32 %tmp386 to i64
  %182 = getelementptr float, float* %84, i64 %181
  %183 = load float, float* %182, align 4
  %184 = add i64 %174, 1
  %tmp387 = trunc i64 %184 to i32
  %185 = sext i32 %tmp387 to i64
  %186 = getelementptr float, float* %93, i64 %185
  %187 = load float, float* %186, align 4
  %188 = fmul reassoc ninf nsz float %187, %183
  %189 = fadd reassoc ninf nsz float %188, %179
  %190 = add i64 %170, 2
  %tmp384 = trunc i64 %190 to i32
  %191 = sext i32 %tmp384 to i64
  %192 = getelementptr float, float* %84, i64 %191
  %193 = load float, float* %192, align 4
  %194 = add i64 %174, 2
  %tmp385 = trunc i64 %194 to i32
  %195 = sext i32 %tmp385 to i64
  %196 = getelementptr float, float* %93, i64 %195
  %197 = load float, float* %196, align 4
  %198 = fmul reassoc ninf nsz float %197, %193
  %199 = fadd reassoc ninf nsz float %198, %189
  %200 = add i64 %170, 3
  %tmp382 = trunc i64 %200 to i32
  %201 = sext i32 %tmp382 to i64
  %202 = getelementptr float, float* %84, i64 %201
  %203 = load float, float* %202, align 4
  %204 = add i64 %174, 3
  %tmp383 = trunc i64 %204 to i32
  %205 = sext i32 %tmp383 to i64
  %206 = getelementptr float, float* %93, i64 %205
  %207 = load float, float* %206, align 4
  %208 = fmul reassoc ninf nsz float %207, %203
  %209 = fadd reassoc ninf nsz float %208, %199
  %indvars.iv.next168.3 = add nuw nsw i64 %indvars.iv167, 4
  %exitcond171.not.3 = icmp eq i64 %wide.trip.count186, %indvars.iv.next168.3
  br i1 %exitcond171.not.3, label %for_loop_test28.after_for27_crit_edge.us.us.us.loopexit, label %for_loop_body25.us.us.us, !llvm.loop !14

for_loop_test28.after_for27_crit_edge.us.us.us.loopexit: ; preds = %for_loop_body25.us.us.us
  br label %for_loop_test28.after_for27_crit_edge.us.us.us

for_loop_test28.after_for27_crit_edge.us.us.us:   ; preds = %for_loop_test28.after_for27_crit_edge.us.us.us.loopexit, %for_loop_body25.us.us.us.prol.loopexit, %middle.block239
  %.lcssa209 = phi float [ %149, %middle.block239 ], [ %.lcssa285.unr, %for_loop_body25.us.us.us.prol.loopexit ], [ %209, %for_loop_test28.after_for27_crit_edge.us.us.us.loopexit ]
  %210 = tail call float @llvm.fabs.f32(float %.lcssa209)
  %211 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %212 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %211, i64 0, i32 14
  %213 = load i8*, i8** %212, align 8
  %214 = getelementptr inbounds i8, i8* %213, i64 4
  %215 = bitcast i8* %214 to float*
  %216 = load float, float* %215, align 4
  %217 = fcmp reassoc ninf nsz ogt float %210, %216
  %218 = load float*, float** %31, align 8
  %219 = load i32, i32* %32, align 4
  %220 = load i32, i32* %33, align 4
  %221 = load i32, i32* %34, align 4
  %222 = mul i32 %219, %lsr439
  %223 = add i32 %222, %.06897.us
  %224 = mul i32 %223, %220
  %225 = add i32 %224, %.06384.us.us
  %226 = mul i32 %225, %221
  %227 = add i32 %226, %.06281.us.us.us
  %228 = sext i32 %227 to i64
  %229 = getelementptr float, float* %218, i64 %228
  br i1 %217, label %true_block.us.us.us, label %false_block.us.us.us

for_loop_test40.preheader.us.us.us.preheader:     ; preds = %for_loop_test36.after_for35_crit_edge.us.us, %for_loop_test40.preheader.us.us.us.preheader.preheader
  %.05990.us.us = phi i32 [ %233, %for_loop_test36.after_for35_crit_edge.us.us ], [ 0, %for_loop_test40.preheader.us.us.us.preheader.preheader ]
  %230 = add i32 %.05990.us.us, %64
  %231 = icmp slt i32 %230, %.05990.us.us
  %232 = or i1 %231, %65
  br label %for_loop_test40.preheader.us.us.us

for_loop_test36.after_for35_crit_edge.us.us:      ; preds = %for_loop_test40.after_for39_crit_edge.us.us.us
  %233 = add nuw nsw i32 %.05990.us.us, 1
  %exitcond181.not = icmp eq i32 %233, %25
  br i1 %exitcond181.not, label %for_loop_test44.preheader.us, label %for_loop_test40.preheader.us.us.us.preheader

for_loop_test40.preheader.us.us.us:               ; preds = %for_loop_test40.after_for39_crit_edge.us.us.us, %for_loop_test40.preheader.us.us.us.preheader
  %.05889.us.us.us = phi i32 [ %400, %for_loop_test40.after_for39_crit_edge.us.us.us ], [ 0, %for_loop_test40.preheader.us.us.us.preheader ]
  %234 = load float*, float** %29, align 8
  %235 = load i32, i32* %30, align 4
  %236 = load float*, float** %31, align 8
  %237 = load i32, i32* %32, align 4
  %238 = load i32, i32* %33, align 4
  %239 = load i32, i32* %34, align 4
  %240 = mul i32 %237, %lsr439
  %241 = add i32 %240, %.06897.us
  %242 = mul i32 %241, %238
  br i1 %min.iters.check262, label %for_loop_body37.us.us.us.preheader, label %vector.scevcheck216

vector.scevcheck216:                              ; preds = %for_loop_test40.preheader.us.us.us
  %ident.check217 = icmp ne i32 %235, 1
  %ident.check218 = icmp ne i32 %239, 1
  %243 = add i32 %.05889.us.us.us, %242
  %244 = add i32 %243, %64
  %245 = icmp slt i32 %244, %243
  %246 = or i1 %ident.check217, %232
  %247 = or i1 %246, %ident.check218
  %248 = or i1 %245, %247
  br i1 %248, label %for_loop_body37.us.us.us.preheader, label %vector.ph222

vector.ph222:                                     ; preds = %vector.scevcheck216
  br i1 %66, label %middle.block219.unr-lcssa, label %vector.body227.preheader

vector.body227.preheader:                         ; preds = %vector.ph222
  %249 = shl i32 %235, 4
  %250 = shl i32 %235, 5
  %251 = add i32 %242, 16
  %252 = mul i32 %239, %251
  %253 = add i32 %.05889.us.us.us, %252
  %254 = shl i32 %239, 5
  %255 = mul i32 %238, %239
  %256 = mul i32 %255, %241
  %257 = add i32 %.05889.us.us.us, %256
  br label %vector.body227

vector.body227:                                   ; preds = %vector.body227, %vector.body227.preheader
  %lsr.iv396 = phi i64 [ %unroll_iter, %vector.body227.preheader ], [ %lsr.iv.next397, %vector.body227 ]
  %lsr.iv394 = phi i32 [ %257, %vector.body227.preheader ], [ %lsr.iv.next395, %vector.body227 ]
  %lsr.iv392 = phi i32 [ %253, %vector.body227.preheader ], [ %lsr.iv.next393, %vector.body227 ]
  %lsr.iv390 = phi i32 [ %.05990.us.us, %vector.body227.preheader ], [ %lsr.iv.next391, %vector.body227 ]
  %index228 = phi i64 [ %index.next235.1, %vector.body227 ], [ 0, %vector.body227.preheader ]
  %vec.phi229 = phi <8 x float> [ %285, %vector.body227 ], [ zeroinitializer, %vector.body227.preheader ]
  %vec.phi230 = phi <8 x float> [ %286, %vector.body227 ], [ zeroinitializer, %vector.body227.preheader ]
  %258 = sext i32 %lsr.iv390 to i64
  %259 = getelementptr float, float* %234, i64 %258
  %260 = bitcast float* %259 to <8 x float>*
  %wide.load231 = load <8 x float>, <8 x float>* %260, align 4
  %261 = getelementptr float, float* %259, i64 8
  %262 = bitcast float* %261 to <8 x float>*
  %wide.load232 = load <8 x float>, <8 x float>* %262, align 4
  %263 = sext i32 %lsr.iv394 to i64
  %264 = getelementptr float, float* %236, i64 %263
  %265 = bitcast float* %264 to <8 x float>*
  %wide.load233 = load <8 x float>, <8 x float>* %265, align 4
  %266 = getelementptr float, float* %264, i64 8
  %267 = bitcast float* %266 to <8 x float>*
  %wide.load234 = load <8 x float>, <8 x float>* %267, align 4
  %268 = fmul reassoc ninf nsz <8 x float> %wide.load233, %wide.load231
  %269 = fmul reassoc ninf nsz <8 x float> %wide.load234, %wide.load232
  %270 = fadd reassoc ninf nsz <8 x float> %268, %vec.phi229
  %271 = fadd reassoc ninf nsz <8 x float> %269, %vec.phi230
  %272 = add i32 %249, %lsr.iv390
  %273 = sext i32 %272 to i64
  %274 = getelementptr float, float* %234, i64 %273
  %275 = bitcast float* %274 to <8 x float>*
  %wide.load231.1 = load <8 x float>, <8 x float>* %275, align 4
  %276 = getelementptr float, float* %274, i64 8
  %277 = bitcast float* %276 to <8 x float>*
  %wide.load232.1 = load <8 x float>, <8 x float>* %277, align 4
  %278 = sext i32 %lsr.iv392 to i64
  %279 = getelementptr float, float* %236, i64 %278
  %280 = bitcast float* %279 to <8 x float>*
  %wide.load233.1 = load <8 x float>, <8 x float>* %280, align 4
  %281 = getelementptr float, float* %279, i64 8
  %282 = bitcast float* %281 to <8 x float>*
  %wide.load234.1 = load <8 x float>, <8 x float>* %282, align 4
  %283 = fmul reassoc ninf nsz <8 x float> %wide.load233.1, %wide.load231.1
  %284 = fmul reassoc ninf nsz <8 x float> %wide.load234.1, %wide.load232.1
  %285 = fadd reassoc ninf nsz <8 x float> %283, %270
  %286 = fadd reassoc ninf nsz <8 x float> %284, %271
  %index.next235.1 = add i64 %index228, 32
  %lsr.iv.next391 = add i32 %lsr.iv390, %250
  %lsr.iv.next393 = add i32 %lsr.iv392, %254
  %lsr.iv.next395 = add i32 %lsr.iv394, %254
  %lsr.iv.next397 = add i64 %lsr.iv396, -2
  %niter310.ncmp.1 = icmp eq i64 %lsr.iv.next397, 0
  br i1 %niter310.ncmp.1, label %middle.block219.unr-lcssa.loopexit, label %vector.body227, !llvm.loop !15

middle.block219.unr-lcssa.loopexit:               ; preds = %vector.body227
  br label %middle.block219.unr-lcssa

middle.block219.unr-lcssa:                        ; preds = %middle.block219.unr-lcssa.loopexit, %vector.ph222
  %.lcssa287.ph = phi <8 x float> [ undef, %vector.ph222 ], [ %285, %middle.block219.unr-lcssa.loopexit ]
  %.lcssa286.ph = phi <8 x float> [ undef, %vector.ph222 ], [ %286, %middle.block219.unr-lcssa.loopexit ]
  %index228.unr = phi i64 [ 0, %vector.ph222 ], [ %index.next235.1, %middle.block219.unr-lcssa.loopexit ]
  %vec.phi229.unr = phi <8 x float> [ zeroinitializer, %vector.ph222 ], [ %285, %middle.block219.unr-lcssa.loopexit ]
  %vec.phi230.unr = phi <8 x float> [ zeroinitializer, %vector.ph222 ], [ %286, %middle.block219.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block219, label %vector.body227.epil

vector.body227.epil:                              ; preds = %middle.block219.unr-lcssa
  %287 = trunc i64 %index228.unr to i32
  %288 = mul i32 %235, %287
  %289 = add i32 %288, %.05990.us.us
  %290 = sext i32 %289 to i64
  %291 = getelementptr float, float* %234, i64 %290
  %292 = bitcast float* %291 to <8 x float>*
  %wide.load231.epil = load <8 x float>, <8 x float>* %292, align 4
  %293 = getelementptr float, float* %291, i64 8
  %294 = bitcast float* %293 to <8 x float>*
  %wide.load232.epil = load <8 x float>, <8 x float>* %294, align 4
  %295 = add i32 %242, %287
  %296 = mul i32 %295, %239
  %297 = add i32 %296, %.05889.us.us.us
  %298 = sext i32 %297 to i64
  %299 = getelementptr float, float* %236, i64 %298
  %300 = bitcast float* %299 to <8 x float>*
  %wide.load233.epil = load <8 x float>, <8 x float>* %300, align 4
  %301 = getelementptr float, float* %299, i64 8
  %302 = bitcast float* %301 to <8 x float>*
  %wide.load234.epil = load <8 x float>, <8 x float>* %302, align 4
  %303 = fmul reassoc ninf nsz <8 x float> %wide.load233.epil, %wide.load231.epil
  %304 = fmul reassoc ninf nsz <8 x float> %wide.load234.epil, %wide.load232.epil
  %305 = fadd reassoc ninf nsz <8 x float> %303, %vec.phi229.unr
  %306 = fadd reassoc ninf nsz <8 x float> %304, %vec.phi230.unr
  br label %middle.block219

middle.block219:                                  ; preds = %vector.body227.epil, %middle.block219.unr-lcssa
  %.lcssa287 = phi <8 x float> [ %.lcssa287.ph, %middle.block219.unr-lcssa ], [ %305, %vector.body227.epil ]
  %.lcssa286 = phi <8 x float> [ %.lcssa286.ph, %middle.block219.unr-lcssa ], [ %306, %vector.body227.epil ]
  %bin.rdx236 = fadd reassoc ninf nsz <8 x float> %.lcssa286, %.lcssa287
  %307 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx236)
  br i1 %cmp.n267, label %for_loop_test40.after_for39_crit_edge.us.us.us, label %for_loop_body37.us.us.us.preheader

for_loop_body37.us.us.us.preheader:               ; preds = %middle.block219, %vector.scevcheck216, %for_loop_test40.preheader.us.us.us
  %indvars.iv175.ph = phi i64 [ 0, %vector.scevcheck216 ], [ 0, %for_loop_test40.preheader.us.us.us ], [ %60, %middle.block219 ]
  %.05786.us.us.us.ph = phi float [ 0.000000e+00, %vector.scevcheck216 ], [ 0.000000e+00, %for_loop_test40.preheader.us.us.us ], [ %307, %middle.block219 ]
  %308 = xor i64 %indvars.iv175.ph, -1
  %309 = add nsw i64 %308, %wide.trip.count186
  br i1 %lcmp.mod295.not, label %for_loop_body37.us.us.us.prol.loopexit, label %for_loop_body37.us.us.us.prol.preheader

for_loop_body37.us.us.us.prol.preheader:          ; preds = %for_loop_body37.us.us.us.preheader
  %310 = trunc i64 %indvars.iv175.ph to i32
  %311 = add i32 %242, %310
  %312 = mul i32 %239, %311
  %313 = add i32 %.05889.us.us.us, %312
  %314 = mul i32 %235, %310
  %315 = add i32 %.05990.us.us, %314
  br label %for_loop_body37.us.us.us.prol

for_loop_body37.us.us.us.prol:                    ; preds = %for_loop_body37.us.us.us.prol, %for_loop_body37.us.us.us.prol.preheader
  %lsr.iv402 = phi i32 [ %315, %for_loop_body37.us.us.us.prol.preheader ], [ %lsr.iv.next403, %for_loop_body37.us.us.us.prol ]
  %lsr.iv400 = phi i32 [ %313, %for_loop_body37.us.us.us.prol.preheader ], [ %lsr.iv.next401, %for_loop_body37.us.us.us.prol ]
  %lsr.iv398 = phi i64 [ 0, %for_loop_body37.us.us.us.prol.preheader ], [ %lsr.iv.next399, %for_loop_body37.us.us.us.prol ]
  %.05786.us.us.us.prol = phi float [ %323, %for_loop_body37.us.us.us.prol ], [ %.05786.us.us.us.ph, %for_loop_body37.us.us.us.prol.preheader ]
  %316 = sext i32 %lsr.iv402 to i64
  %317 = getelementptr float, float* %234, i64 %316
  %318 = load float, float* %317, align 4
  %319 = sext i32 %lsr.iv400 to i64
  %320 = getelementptr float, float* %236, i64 %319
  %321 = load float, float* %320, align 4
  %322 = fmul reassoc ninf nsz float %321, %318
  %323 = fadd reassoc ninf nsz float %322, %.05786.us.us.us.prol
  %lsr.iv.next399 = add nsw i64 %lsr.iv398, -1
  %lsr.iv.next401 = add i32 %lsr.iv400, %239
  %lsr.iv.next403 = add i32 %lsr.iv402, %235
  %prol.iter313.cmp.not = icmp eq i64 %67, %lsr.iv.next399
  br i1 %prol.iter313.cmp.not, label %for_loop_body37.us.us.us.prol.loopexit.loopexit, label %for_loop_body37.us.us.us.prol, !llvm.loop !16

for_loop_body37.us.us.us.prol.loopexit.loopexit:  ; preds = %for_loop_body37.us.us.us.prol
  %324 = sub i64 %indvars.iv175.ph, %67
  br label %for_loop_body37.us.us.us.prol.loopexit

for_loop_body37.us.us.us.prol.loopexit:           ; preds = %for_loop_body37.us.us.us.prol.loopexit.loopexit, %for_loop_body37.us.us.us.preheader
  %.lcssa288.unr = phi float [ undef, %for_loop_body37.us.us.us.preheader ], [ %323, %for_loop_body37.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv175.unr = phi i64 [ %indvars.iv175.ph, %for_loop_body37.us.us.us.preheader ], [ %324, %for_loop_body37.us.us.us.prol.loopexit.loopexit ]
  %.05786.us.us.us.unr = phi float [ %.05786.us.us.us.ph, %for_loop_body37.us.us.us.preheader ], [ %323, %for_loop_body37.us.us.us.prol.loopexit.loopexit ]
  %325 = icmp ult i64 %309, 3
  br i1 %325, label %for_loop_test40.after_for39_crit_edge.us.us.us, label %for_loop_body37.us.us.us.preheader343

for_loop_body37.us.us.us.preheader343:            ; preds = %for_loop_body37.us.us.us.prol.loopexit
  %326 = trunc i64 %indvars.iv175.unr to i32
  %327 = add nuw i32 %326, 3
  %328 = mul i32 %235, %327
  %329 = shl i32 %235, 2
  %330 = add i32 %242, 3
  %331 = add i32 %330, %326
  %332 = mul i32 %239, %331
  %333 = add i32 %.05889.us.us.us, %332
  %334 = shl i32 %239, 2
  %335 = add nuw i32 %326, 2
  %336 = mul i32 %235, %335
  %337 = add i32 %242, 2
  %338 = add i32 %337, %326
  %339 = mul i32 %239, %338
  %340 = add i32 %.05889.us.us.us, %339
  %341 = add nuw i32 %326, 1
  %342 = mul i32 %235, %341
  %343 = add i32 %242, 1
  %344 = add i32 %343, %326
  %345 = mul i32 %239, %344
  %346 = add i32 %.05889.us.us.us, %345
  %347 = sub i64 %wide.trip.count186, %indvars.iv175.unr
  %348 = add i32 %242, %326
  %349 = mul i32 %239, %348
  %350 = add i32 %.05889.us.us.us, %349
  %351 = mul i32 %235, %326
  br label %for_loop_body37.us.us.us

for_loop_body37.us.us.us:                         ; preds = %for_loop_body37.us.us.us, %for_loop_body37.us.us.us.preheader343
  %lsr.iv414 = phi i32 [ %350, %for_loop_body37.us.us.us.preheader343 ], [ %lsr.iv.next415, %for_loop_body37.us.us.us ]
  %lsr.iv412 = phi i64 [ %347, %for_loop_body37.us.us.us.preheader343 ], [ %lsr.iv.next413, %for_loop_body37.us.us.us ]
  %lsr.iv410 = phi i32 [ %346, %for_loop_body37.us.us.us.preheader343 ], [ %lsr.iv.next411, %for_loop_body37.us.us.us ]
  %lsr.iv408 = phi i32 [ %340, %for_loop_body37.us.us.us.preheader343 ], [ %lsr.iv.next409, %for_loop_body37.us.us.us ]
  %lsr.iv406 = phi i32 [ %333, %for_loop_body37.us.us.us.preheader343 ], [ %lsr.iv.next407, %for_loop_body37.us.us.us ]
  %lsr.iv404 = phi i32 [ %.05990.us.us, %for_loop_body37.us.us.us.preheader343 ], [ %lsr.iv.next405, %for_loop_body37.us.us.us ]
  %.05786.us.us.us = phi float [ %387, %for_loop_body37.us.us.us ], [ %.05786.us.us.us.unr, %for_loop_body37.us.us.us.preheader343 ]
  %352 = add i32 %351, %lsr.iv404
  %353 = sext i32 %352 to i64
  %354 = getelementptr float, float* %234, i64 %353
  %355 = load float, float* %354, align 4
  %356 = sext i32 %lsr.iv414 to i64
  %357 = getelementptr float, float* %236, i64 %356
  %358 = load float, float* %357, align 4
  %359 = fmul reassoc ninf nsz float %358, %355
  %360 = fadd reassoc ninf nsz float %359, %.05786.us.us.us
  %361 = add i32 %342, %lsr.iv404
  %362 = sext i32 %361 to i64
  %363 = getelementptr float, float* %234, i64 %362
  %364 = load float, float* %363, align 4
  %365 = sext i32 %lsr.iv410 to i64
  %366 = getelementptr float, float* %236, i64 %365
  %367 = load float, float* %366, align 4
  %368 = fmul reassoc ninf nsz float %367, %364
  %369 = fadd reassoc ninf nsz float %368, %360
  %370 = add i32 %336, %lsr.iv404
  %371 = sext i32 %370 to i64
  %372 = getelementptr float, float* %234, i64 %371
  %373 = load float, float* %372, align 4
  %374 = sext i32 %lsr.iv408 to i64
  %375 = getelementptr float, float* %236, i64 %374
  %376 = load float, float* %375, align 4
  %377 = fmul reassoc ninf nsz float %376, %373
  %378 = fadd reassoc ninf nsz float %377, %369
  %379 = add i32 %328, %lsr.iv404
  %380 = sext i32 %379 to i64
  %381 = getelementptr float, float* %234, i64 %380
  %382 = load float, float* %381, align 4
  %383 = sext i32 %lsr.iv406 to i64
  %384 = getelementptr float, float* %236, i64 %383
  %385 = load float, float* %384, align 4
  %386 = fmul reassoc ninf nsz float %385, %382
  %387 = fadd reassoc ninf nsz float %386, %378
  %lsr.iv.next405 = add i32 %lsr.iv404, %329
  %lsr.iv.next407 = add i32 %lsr.iv406, %334
  %lsr.iv.next409 = add i32 %lsr.iv408, %334
  %lsr.iv.next411 = add i32 %lsr.iv410, %334
  %lsr.iv.next413 = add i64 %lsr.iv412, -4
  %lsr.iv.next415 = add i32 %lsr.iv414, %334
  %exitcond179.not.3 = icmp eq i64 %lsr.iv.next413, 0
  br i1 %exitcond179.not.3, label %for_loop_test40.after_for39_crit_edge.us.us.us.loopexit, label %for_loop_body37.us.us.us, !llvm.loop !17

for_loop_test40.after_for39_crit_edge.us.us.us.loopexit: ; preds = %for_loop_body37.us.us.us
  br label %for_loop_test40.after_for39_crit_edge.us.us.us

for_loop_test40.after_for39_crit_edge.us.us.us:   ; preds = %for_loop_test40.after_for39_crit_edge.us.us.us.loopexit, %for_loop_body37.us.us.us.prol.loopexit, %middle.block219
  %.lcssa210 = phi float [ %307, %middle.block219 ], [ %.lcssa288.unr, %for_loop_body37.us.us.us.prol.loopexit ], [ %387, %for_loop_test40.after_for39_crit_edge.us.us.us.loopexit ]
  %388 = load float*, float** %35, align 8
  %389 = load i32, i32* %36, align 4
  %390 = load i32, i32* %37, align 4
  %391 = load i32, i32* %38, align 4
  %392 = mul i32 %389, %lsr439
  %393 = add i32 %392, %.06897.us
  %394 = mul i32 %393, %390
  %395 = add i32 %394, %.05990.us.us
  %396 = mul i32 %395, %391
  %397 = add i32 %396, %.05889.us.us.us
  %398 = sext i32 %397 to i64
  %399 = getelementptr float, float* %388, i64 %398
  store float %.lcssa210, float* %399, align 4
  %400 = add nuw nsw i32 %.05889.us.us.us, 1
  %exitcond180.not = icmp eq i32 %400, %25
  br i1 %exitcond180.not, label %for_loop_test36.after_for35_crit_edge.us.us, label %for_loop_test40.preheader.us.us.us

for_loop_test52.preheader.us.us.us.preheader:     ; preds = %for_loop_test48.after_for47_crit_edge.us.us, %for_loop_test52.preheader.us.us.us.preheader.preheader
  %.05595.us.us = phi i32 [ %401, %for_loop_test48.after_for47_crit_edge.us.us ], [ 0, %for_loop_test52.preheader.us.us.us.preheader.preheader ]
  br label %for_loop_test52.preheader.us.us.us

for_loop_test48.after_for47_crit_edge.us.us:      ; preds = %for_loop_test52.after_for51_crit_edge.us.us.us
  %401 = add nuw nsw i32 %.05595.us.us, 1
  %exitcond189.not = icmp eq i32 %401, %25
  br i1 %exitcond189.not, label %after_for43.us.loopexit, label %for_loop_test52.preheader.us.us.us.preheader

for_loop_test52.preheader.us.us.us:               ; preds = %for_loop_test52.after_for51_crit_edge.us.us.us, %for_loop_test52.preheader.us.us.us.preheader
  %.05494.us.us.us = phi i32 [ %555, %for_loop_test52.after_for51_crit_edge.us.us.us ], [ 0, %for_loop_test52.preheader.us.us.us.preheader ]
  %402 = load float*, float** %35, align 8
  %403 = load i32, i32* %36, align 4
  %404 = load i32, i32* %37, align 4
  %405 = load i32, i32* %38, align 4
  %406 = mul i32 %403, %lsr439
  %407 = add i32 %406, %.06897.us
  %408 = mul i32 %407, %404
  %409 = add i32 %408, %.05595.us.us
  %410 = mul i32 %409, %405
  %411 = load float*, float** %29, align 8
  %412 = load i32, i32* %30, align 4
  br i1 %min.iters.check262, label %for_loop_body49.us.us.us.preheader, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %for_loop_test52.preheader.us.us.us
  %413 = mul i32 %68, %403
  %414 = add i32 %.06897.us, %413
  %415 = mul i32 %404, %414
  %416 = add i32 %.05595.us.us, %415
  %417 = mul i32 %405, %416
  %418 = add i32 %417, %64
  %419 = icmp slt i32 %418, %417
  %420 = or i1 %419, %65
  %ident.check = icmp ne i32 %412, 1
  %421 = add i32 %.05494.us.us.us, %64
  %422 = icmp slt i32 %421, %.05494.us.us.us
  %423 = or i1 %420, %ident.check
  %424 = or i1 %422, %423
  br i1 %424, label %for_loop_body49.us.us.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %vector.scevcheck
  br i1 %66, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  %425 = shl i32 %412, 4
  %426 = shl i32 %412, 5
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv420 = phi i64 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next421, %vector.body ]
  %lsr.iv418 = phi i32 [ %.05494.us.us.us, %vector.body.preheader ], [ %lsr.iv.next419, %vector.body ]
  %lsr.iv416 = phi i32 [ %410, %vector.body.preheader ], [ %lsr.iv.next417, %vector.body ]
  %index = phi i64 [ %index.next.1, %vector.body ], [ 0, %vector.body.preheader ]
  %vec.phi = phi <8 x float> [ %455, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %vec.phi212 = phi <8 x float> [ %456, %vector.body ], [ zeroinitializer, %vector.body.preheader ]
  %427 = sext i32 %lsr.iv416 to i64
  %428 = getelementptr float, float* %402, i64 %427
  %429 = bitcast float* %428 to <8 x float>*
  %wide.load = load <8 x float>, <8 x float>* %429, align 4
  %430 = getelementptr float, float* %428, i64 8
  %431 = bitcast float* %430 to <8 x float>*
  %wide.load213 = load <8 x float>, <8 x float>* %431, align 4
  %432 = sext i32 %lsr.iv418 to i64
  %433 = getelementptr float, float* %411, i64 %432
  %434 = bitcast float* %433 to <8 x float>*
  %wide.load214 = load <8 x float>, <8 x float>* %434, align 4
  %435 = getelementptr float, float* %433, i64 8
  %436 = bitcast float* %435 to <8 x float>*
  %wide.load215 = load <8 x float>, <8 x float>* %436, align 4
  %437 = fmul reassoc ninf nsz <8 x float> %wide.load214, %wide.load
  %438 = fmul reassoc ninf nsz <8 x float> %wide.load215, %wide.load213
  %439 = fadd reassoc ninf nsz <8 x float> %437, %vec.phi
  %440 = fadd reassoc ninf nsz <8 x float> %438, %vec.phi212
  %441 = add i32 %lsr.iv416, 16
  %442 = sext i32 %441 to i64
  %443 = getelementptr float, float* %402, i64 %442
  %444 = bitcast float* %443 to <8 x float>*
  %wide.load.1 = load <8 x float>, <8 x float>* %444, align 4
  %445 = getelementptr float, float* %443, i64 8
  %446 = bitcast float* %445 to <8 x float>*
  %wide.load213.1 = load <8 x float>, <8 x float>* %446, align 4
  %447 = add i32 %425, %lsr.iv418
  %448 = sext i32 %447 to i64
  %449 = getelementptr float, float* %411, i64 %448
  %450 = bitcast float* %449 to <8 x float>*
  %wide.load214.1 = load <8 x float>, <8 x float>* %450, align 4
  %451 = getelementptr float, float* %449, i64 8
  %452 = bitcast float* %451 to <8 x float>*
  %wide.load215.1 = load <8 x float>, <8 x float>* %452, align 4
  %453 = fmul reassoc ninf nsz <8 x float> %wide.load214.1, %wide.load.1
  %454 = fmul reassoc ninf nsz <8 x float> %wide.load215.1, %wide.load213.1
  %455 = fadd reassoc ninf nsz <8 x float> %453, %439
  %456 = fadd reassoc ninf nsz <8 x float> %454, %440
  %index.next.1 = add i64 %index, 32
  %lsr.iv.next417 = add i32 %lsr.iv416, 32
  %lsr.iv.next419 = add i32 %lsr.iv418, %426
  %lsr.iv.next421 = add i64 %lsr.iv420, -2
  %niter319.ncmp.1 = icmp eq i64 %lsr.iv.next421, 0
  br i1 %niter319.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !18

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa290.ph = phi <8 x float> [ undef, %vector.ph ], [ %455, %middle.block.unr-lcssa.loopexit ]
  %.lcssa289.ph = phi <8 x float> [ undef, %vector.ph ], [ %456, %middle.block.unr-lcssa.loopexit ]
  %index.unr = phi i64 [ 0, %vector.ph ], [ %index.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %455, %middle.block.unr-lcssa.loopexit ]
  %vec.phi212.unr = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %456, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %457 = trunc i64 %index.unr to i32
  %458 = add i32 %410, %457
  %459 = sext i32 %458 to i64
  %460 = getelementptr float, float* %402, i64 %459
  %461 = bitcast float* %460 to <8 x float>*
  %wide.load.epil = load <8 x float>, <8 x float>* %461, align 4
  %462 = getelementptr float, float* %460, i64 8
  %463 = bitcast float* %462 to <8 x float>*
  %wide.load213.epil = load <8 x float>, <8 x float>* %463, align 4
  %464 = mul i32 %412, %457
  %465 = add i32 %464, %.05494.us.us.us
  %466 = sext i32 %465 to i64
  %467 = getelementptr float, float* %411, i64 %466
  %468 = bitcast float* %467 to <8 x float>*
  %wide.load214.epil = load <8 x float>, <8 x float>* %468, align 4
  %469 = getelementptr float, float* %467, i64 8
  %470 = bitcast float* %469 to <8 x float>*
  %wide.load215.epil = load <8 x float>, <8 x float>* %470, align 4
  %471 = fmul reassoc ninf nsz <8 x float> %wide.load214.epil, %wide.load.epil
  %472 = fmul reassoc ninf nsz <8 x float> %wide.load215.epil, %wide.load213.epil
  %473 = fadd reassoc ninf nsz <8 x float> %471, %vec.phi.unr
  %474 = fadd reassoc ninf nsz <8 x float> %472, %vec.phi212.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa290 = phi <8 x float> [ %.lcssa290.ph, %middle.block.unr-lcssa ], [ %473, %vector.body.epil ]
  %.lcssa289 = phi <8 x float> [ %.lcssa289.ph, %middle.block.unr-lcssa ], [ %474, %vector.body.epil ]
  %bin.rdx = fadd reassoc ninf nsz <8 x float> %.lcssa289, %.lcssa290
  %475 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx)
  br i1 %cmp.n267, label %for_loop_test52.after_for51_crit_edge.us.us.us, label %for_loop_body49.us.us.us.preheader

for_loop_body49.us.us.us.preheader:               ; preds = %middle.block, %vector.scevcheck, %for_loop_test52.preheader.us.us.us
  %indvars.iv183.ph = phi i64 [ 0, %vector.scevcheck ], [ 0, %for_loop_test52.preheader.us.us.us ], [ %60, %middle.block ]
  %.05391.us.us.us.ph = phi float [ 0.000000e+00, %vector.scevcheck ], [ 0.000000e+00, %for_loop_test52.preheader.us.us.us ], [ %475, %middle.block ]
  %476 = xor i64 %indvars.iv183.ph, -1
  %477 = add nsw i64 %476, %wide.trip.count186
  br i1 %lcmp.mod295.not, label %for_loop_body49.us.us.us.prol.loopexit, label %for_loop_body49.us.us.us.prol.preheader

for_loop_body49.us.us.us.prol.preheader:          ; preds = %for_loop_body49.us.us.us.preheader
  %478 = trunc i64 %indvars.iv183.ph to i32
  %479 = mul i32 %412, %478
  %480 = add i32 %.05494.us.us.us, %479
  %481 = zext i32 %410 to i64
  br label %for_loop_body49.us.us.us.prol

for_loop_body49.us.us.us.prol:                    ; preds = %for_loop_body49.us.us.us.prol, %for_loop_body49.us.us.us.prol.preheader
  %lsr.iv425 = phi i64 [ %xtraiter294, %for_loop_body49.us.us.us.prol.preheader ], [ %lsr.iv.next426, %for_loop_body49.us.us.us.prol ]
  %lsr.iv422 = phi i32 [ %480, %for_loop_body49.us.us.us.prol.preheader ], [ %lsr.iv.next423, %for_loop_body49.us.us.us.prol ]
  %indvars.iv183.prol = phi i64 [ %indvars.iv.next184.prol, %for_loop_body49.us.us.us.prol ], [ %indvars.iv183.ph, %for_loop_body49.us.us.us.prol.preheader ]
  %.05391.us.us.us.prol = phi float [ %490, %for_loop_body49.us.us.us.prol ], [ %.05391.us.us.us.ph, %for_loop_body49.us.us.us.prol.preheader ]
  %482 = add i64 %481, %indvars.iv183.prol
  %tmp424 = trunc i64 %482 to i32
  %483 = sext i32 %tmp424 to i64
  %484 = getelementptr float, float* %402, i64 %483
  %485 = load float, float* %484, align 4
  %486 = sext i32 %lsr.iv422 to i64
  %487 = getelementptr float, float* %411, i64 %486
  %488 = load float, float* %487, align 4
  %489 = fmul reassoc ninf nsz float %488, %485
  %490 = fadd reassoc ninf nsz float %489, %.05391.us.us.us.prol
  %indvars.iv.next184.prol = add nuw nsw i64 %indvars.iv183.prol, 1
  %lsr.iv.next423 = add i32 %lsr.iv422, %412
  %lsr.iv.next426 = add nsw i64 %lsr.iv425, -1
  %prol.iter322.cmp.not = icmp eq i64 %lsr.iv.next426, 0
  br i1 %prol.iter322.cmp.not, label %for_loop_body49.us.us.us.prol.loopexit.loopexit, label %for_loop_body49.us.us.us.prol, !llvm.loop !19

for_loop_body49.us.us.us.prol.loopexit.loopexit:  ; preds = %for_loop_body49.us.us.us.prol
  %491 = add i64 %xtraiter294, %indvars.iv183.ph
  br label %for_loop_body49.us.us.us.prol.loopexit

for_loop_body49.us.us.us.prol.loopexit:           ; preds = %for_loop_body49.us.us.us.prol.loopexit.loopexit, %for_loop_body49.us.us.us.preheader
  %.lcssa291.unr = phi float [ undef, %for_loop_body49.us.us.us.preheader ], [ %490, %for_loop_body49.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv183.unr = phi i64 [ %indvars.iv183.ph, %for_loop_body49.us.us.us.preheader ], [ %491, %for_loop_body49.us.us.us.prol.loopexit.loopexit ]
  %.05391.us.us.us.unr = phi float [ %.05391.us.us.us.ph, %for_loop_body49.us.us.us.preheader ], [ %490, %for_loop_body49.us.us.us.prol.loopexit.loopexit ]
  %492 = icmp ult i64 %477, 3
  br i1 %492, label %for_loop_test52.after_for51_crit_edge.us.us.us, label %for_loop_body49.us.us.us.preheader342

for_loop_body49.us.us.us.preheader342:            ; preds = %for_loop_body49.us.us.us.prol.loopexit
  %493 = zext i32 %410 to i64
  %494 = trunc i64 %indvars.iv183.unr to i32
  %495 = add nuw i32 %494, 3
  %496 = mul i32 %412, %495
  %497 = add i32 %.05494.us.us.us, %496
  %498 = shl i32 %412, 2
  %499 = add nuw i32 %494, 2
  %500 = mul i32 %412, %499
  %501 = add i32 %.05494.us.us.us, %500
  %502 = add nuw i32 %494, 1
  %503 = mul i32 %412, %502
  %504 = add i32 %.05494.us.us.us, %503
  %505 = mul i32 %412, %494
  %506 = add i32 %.05494.us.us.us, %505
  br label %for_loop_body49.us.us.us

for_loop_body49.us.us.us:                         ; preds = %for_loop_body49.us.us.us, %for_loop_body49.us.us.us.preheader342
  %lsr.iv436 = phi i32 [ %506, %for_loop_body49.us.us.us.preheader342 ], [ %lsr.iv.next437, %for_loop_body49.us.us.us ]
  %lsr.iv434 = phi i32 [ %504, %for_loop_body49.us.us.us.preheader342 ], [ %lsr.iv.next435, %for_loop_body49.us.us.us ]
  %lsr.iv431 = phi i32 [ %501, %for_loop_body49.us.us.us.preheader342 ], [ %lsr.iv.next432, %for_loop_body49.us.us.us ]
  %lsr.iv428 = phi i32 [ %497, %for_loop_body49.us.us.us.preheader342 ], [ %lsr.iv.next429, %for_loop_body49.us.us.us ]
  %indvars.iv183 = phi i64 [ %indvars.iv.next184.3, %for_loop_body49.us.us.us ], [ %indvars.iv183.unr, %for_loop_body49.us.us.us.preheader342 ]
  %.05391.us.us.us = phi float [ %542, %for_loop_body49.us.us.us ], [ %.05391.us.us.us.unr, %for_loop_body49.us.us.us.preheader342 ]
  %507 = add i64 %493, %indvars.iv183
  %tmp438 = trunc i64 %507 to i32
  %508 = sext i32 %tmp438 to i64
  %509 = getelementptr float, float* %402, i64 %508
  %510 = load float, float* %509, align 4
  %511 = sext i32 %lsr.iv436 to i64
  %512 = getelementptr float, float* %411, i64 %511
  %513 = load float, float* %512, align 4
  %514 = fmul reassoc ninf nsz float %513, %510
  %515 = fadd reassoc ninf nsz float %514, %.05391.us.us.us
  %516 = add i64 %507, 1
  %tmp433 = trunc i64 %516 to i32
  %517 = sext i32 %tmp433 to i64
  %518 = getelementptr float, float* %402, i64 %517
  %519 = load float, float* %518, align 4
  %520 = sext i32 %lsr.iv434 to i64
  %521 = getelementptr float, float* %411, i64 %520
  %522 = load float, float* %521, align 4
  %523 = fmul reassoc ninf nsz float %522, %519
  %524 = fadd reassoc ninf nsz float %523, %515
  %525 = add i64 %507, 2
  %tmp430 = trunc i64 %525 to i32
  %526 = sext i32 %tmp430 to i64
  %527 = getelementptr float, float* %402, i64 %526
  %528 = load float, float* %527, align 4
  %529 = sext i32 %lsr.iv431 to i64
  %530 = getelementptr float, float* %411, i64 %529
  %531 = load float, float* %530, align 4
  %532 = fmul reassoc ninf nsz float %531, %528
  %533 = fadd reassoc ninf nsz float %532, %524
  %534 = add i64 %507, 3
  %tmp427 = trunc i64 %534 to i32
  %535 = sext i32 %tmp427 to i64
  %536 = getelementptr float, float* %402, i64 %535
  %537 = load float, float* %536, align 4
  %538 = sext i32 %lsr.iv428 to i64
  %539 = getelementptr float, float* %411, i64 %538
  %540 = load float, float* %539, align 4
  %541 = fmul reassoc ninf nsz float %540, %537
  %542 = fadd reassoc ninf nsz float %541, %533
  %indvars.iv.next184.3 = add nuw nsw i64 %indvars.iv183, 4
  %lsr.iv.next429 = add i32 %lsr.iv428, %498
  %lsr.iv.next432 = add i32 %lsr.iv431, %498
  %lsr.iv.next435 = add i32 %lsr.iv434, %498
  %lsr.iv.next437 = add i32 %lsr.iv436, %498
  %exitcond187.not.3 = icmp eq i64 %wide.trip.count186, %indvars.iv.next184.3
  br i1 %exitcond187.not.3, label %for_loop_test52.after_for51_crit_edge.us.us.us.loopexit, label %for_loop_body49.us.us.us, !llvm.loop !20

for_loop_test52.after_for51_crit_edge.us.us.us.loopexit: ; preds = %for_loop_body49.us.us.us
  br label %for_loop_test52.after_for51_crit_edge.us.us.us

for_loop_test52.after_for51_crit_edge.us.us.us:   ; preds = %for_loop_test52.after_for51_crit_edge.us.us.us.loopexit, %for_loop_body49.us.us.us.prol.loopexit, %middle.block
  %.lcssa211 = phi float [ %475, %middle.block ], [ %.lcssa291.unr, %for_loop_body49.us.us.us.prol.loopexit ], [ %542, %for_loop_test52.after_for51_crit_edge.us.us.us.loopexit ]
  %543 = load float*, float** %39, align 8
  %544 = load i32, i32* %40, align 4
  %545 = load i32, i32* %41, align 4
  %546 = load i32, i32* %42, align 4
  %547 = mul i32 %544, %lsr439
  %548 = add i32 %547, %.06897.us
  %549 = mul i32 %548, %545
  %550 = add i32 %549, %.05595.us.us
  %551 = mul i32 %550, %546
  %552 = add i32 %551, %.05494.us.us.us
  %553 = sext i32 %552 to i64
  %554 = getelementptr float, float* %543, i64 %553
  store float %.lcssa211, float* %554, align 4
  %555 = add nuw nsw i32 %.05494.us.us.us, 1
  %exitcond188.not = icmp eq i32 %555, %25
  br i1 %exitcond188.not, label %for_loop_test48.after_for47_crit_edge.us.us, label %for_loop_test52.preheader.us.us.us

for_loop_test12.preheader.us.us.us:               ; preds = %for_loop_test12.after_for11_crit_edge.split.us.us.us.us, %for_loop_test12.preheader.us.us.us.preheader
  %.06776.us.us.us = phi i32 [ %715, %for_loop_test12.after_for11_crit_edge.split.us.us.us.us ], [ 0, %for_loop_test12.preheader.us.us.us.preheader ]
  br label %for_loop_test16.preheader.us.us.us.us

for_loop_test16.preheader.us.us.us.us:            ; preds = %for_loop_test16.after_for15_crit_edge.us.us.us.us, %for_loop_test12.preheader.us.us.us
  %.06675.us.us.us.us = phi i32 [ 0, %for_loop_test12.preheader.us.us.us ], [ %714, %for_loop_test16.after_for15_crit_edge.us.us.us.us ]
  %556 = load float*, float** %29, align 8
  %557 = load i32, i32* %30, align 4
  %558 = mul i32 %557, %.06776.us.us.us
  %559 = load float*, float** %31, align 8
  %560 = load i32, i32* %32, align 4
  %561 = load i32, i32* %33, align 4
  %562 = load i32, i32* %34, align 4
  %563 = mul i32 %560, %lsr439
  %564 = add i32 %563, %.06897.us
  %565 = mul i32 %564, %561
  br i1 %min.iters.check262, label %for_loop_body13.us.us.us.us.preheader, label %vector.scevcheck258

vector.scevcheck258:                              ; preds = %for_loop_test16.preheader.us.us.us.us
  %566 = add i32 %558, %64
  %567 = icmp slt i32 %566, %558
  %568 = or i1 %567, %65
  %ident.check259 = icmp ne i32 %562, 1
  %569 = add i32 %.06675.us.us.us.us, %565
  %570 = add i32 %569, %64
  %571 = icmp slt i32 %570, %569
  %572 = or i1 %568, %ident.check259
  %573 = or i1 %571, %572
  br i1 %573, label %for_loop_body13.us.us.us.us.preheader, label %vector.ph263

vector.ph263:                                     ; preds = %vector.scevcheck258
  br i1 %66, label %middle.block260.unr-lcssa, label %vector.body268.preheader

vector.body268.preheader:                         ; preds = %vector.ph263
  %574 = add i32 %565, 16
  %575 = mul i32 %562, %574
  %576 = add i32 %.06675.us.us.us.us, %575
  %577 = shl i32 %562, 5
  %578 = mul i32 %561, %562
  %579 = mul i32 %578, %564
  %580 = add i32 %.06675.us.us.us.us, %579
  br label %vector.body268

vector.body268:                                   ; preds = %vector.body268, %vector.body268.preheader
  %lsr.iv354 = phi i64 [ %unroll_iter, %vector.body268.preheader ], [ %lsr.iv.next355, %vector.body268 ]
  %lsr.iv352 = phi i32 [ %580, %vector.body268.preheader ], [ %lsr.iv.next353, %vector.body268 ]
  %lsr.iv350 = phi i32 [ %576, %vector.body268.preheader ], [ %lsr.iv.next351, %vector.body268 ]
  %lsr.iv = phi i32 [ %558, %vector.body268.preheader ], [ %lsr.iv.next, %vector.body268 ]
  %index269 = phi i64 [ %index.next276.1, %vector.body268 ], [ 0, %vector.body268.preheader ]
  %vec.phi270 = phi <8 x float> [ %608, %vector.body268 ], [ zeroinitializer, %vector.body268.preheader ]
  %vec.phi271 = phi <8 x float> [ %609, %vector.body268 ], [ zeroinitializer, %vector.body268.preheader ]
  %581 = sext i32 %lsr.iv to i64
  %582 = getelementptr float, float* %556, i64 %581
  %583 = bitcast float* %582 to <8 x float>*
  %wide.load272 = load <8 x float>, <8 x float>* %583, align 4
  %584 = getelementptr float, float* %582, i64 8
  %585 = bitcast float* %584 to <8 x float>*
  %wide.load273 = load <8 x float>, <8 x float>* %585, align 4
  %586 = sext i32 %lsr.iv352 to i64
  %587 = getelementptr float, float* %559, i64 %586
  %588 = bitcast float* %587 to <8 x float>*
  %wide.load274 = load <8 x float>, <8 x float>* %588, align 4
  %589 = getelementptr float, float* %587, i64 8
  %590 = bitcast float* %589 to <8 x float>*
  %wide.load275 = load <8 x float>, <8 x float>* %590, align 4
  %591 = fmul reassoc ninf nsz <8 x float> %wide.load274, %wide.load272
  %592 = fmul reassoc ninf nsz <8 x float> %wide.load275, %wide.load273
  %593 = fadd reassoc ninf nsz <8 x float> %591, %vec.phi270
  %594 = fadd reassoc ninf nsz <8 x float> %592, %vec.phi271
  %595 = add i32 %lsr.iv, 16
  %596 = sext i32 %595 to i64
  %597 = getelementptr float, float* %556, i64 %596
  %598 = bitcast float* %597 to <8 x float>*
  %wide.load272.1 = load <8 x float>, <8 x float>* %598, align 4
  %599 = getelementptr float, float* %597, i64 8
  %600 = bitcast float* %599 to <8 x float>*
  %wide.load273.1 = load <8 x float>, <8 x float>* %600, align 4
  %601 = sext i32 %lsr.iv350 to i64
  %602 = getelementptr float, float* %559, i64 %601
  %603 = bitcast float* %602 to <8 x float>*
  %wide.load274.1 = load <8 x float>, <8 x float>* %603, align 4
  %604 = getelementptr float, float* %602, i64 8
  %605 = bitcast float* %604 to <8 x float>*
  %wide.load275.1 = load <8 x float>, <8 x float>* %605, align 4
  %606 = fmul reassoc ninf nsz <8 x float> %wide.load274.1, %wide.load272.1
  %607 = fmul reassoc ninf nsz <8 x float> %wide.load275.1, %wide.load273.1
  %608 = fadd reassoc ninf nsz <8 x float> %606, %593
  %609 = fadd reassoc ninf nsz <8 x float> %607, %594
  %index.next276.1 = add i64 %index269, 32
  %lsr.iv.next = add i32 %lsr.iv, 32
  %lsr.iv.next351 = add i32 %lsr.iv350, %577
  %lsr.iv.next353 = add i32 %lsr.iv352, %577
  %lsr.iv.next355 = add i64 %lsr.iv354, -2
  %niter.ncmp.1 = icmp eq i64 %lsr.iv.next355, 0
  br i1 %niter.ncmp.1, label %middle.block260.unr-lcssa.loopexit, label %vector.body268, !llvm.loop !21

middle.block260.unr-lcssa.loopexit:               ; preds = %vector.body268
  br label %middle.block260.unr-lcssa

middle.block260.unr-lcssa:                        ; preds = %middle.block260.unr-lcssa.loopexit, %vector.ph263
  %.lcssa281.ph = phi <8 x float> [ undef, %vector.ph263 ], [ %608, %middle.block260.unr-lcssa.loopexit ]
  %.lcssa280.ph = phi <8 x float> [ undef, %vector.ph263 ], [ %609, %middle.block260.unr-lcssa.loopexit ]
  %index269.unr = phi i64 [ 0, %vector.ph263 ], [ %index.next276.1, %middle.block260.unr-lcssa.loopexit ]
  %vec.phi270.unr = phi <8 x float> [ zeroinitializer, %vector.ph263 ], [ %608, %middle.block260.unr-lcssa.loopexit ]
  %vec.phi271.unr = phi <8 x float> [ zeroinitializer, %vector.ph263 ], [ %609, %middle.block260.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block260, label %vector.body268.epil

vector.body268.epil:                              ; preds = %middle.block260.unr-lcssa
  %610 = trunc i64 %index269.unr to i32
  %611 = add i32 %558, %610
  %612 = sext i32 %611 to i64
  %613 = getelementptr float, float* %556, i64 %612
  %614 = bitcast float* %613 to <8 x float>*
  %wide.load272.epil = load <8 x float>, <8 x float>* %614, align 4
  %615 = getelementptr float, float* %613, i64 8
  %616 = bitcast float* %615 to <8 x float>*
  %wide.load273.epil = load <8 x float>, <8 x float>* %616, align 4
  %617 = add i32 %565, %610
  %618 = mul i32 %617, %562
  %619 = add i32 %618, %.06675.us.us.us.us
  %620 = sext i32 %619 to i64
  %621 = getelementptr float, float* %559, i64 %620
  %622 = bitcast float* %621 to <8 x float>*
  %wide.load274.epil = load <8 x float>, <8 x float>* %622, align 4
  %623 = getelementptr float, float* %621, i64 8
  %624 = bitcast float* %623 to <8 x float>*
  %wide.load275.epil = load <8 x float>, <8 x float>* %624, align 4
  %625 = fmul reassoc ninf nsz <8 x float> %wide.load274.epil, %wide.load272.epil
  %626 = fmul reassoc ninf nsz <8 x float> %wide.load275.epil, %wide.load273.epil
  %627 = fadd reassoc ninf nsz <8 x float> %625, %vec.phi270.unr
  %628 = fadd reassoc ninf nsz <8 x float> %626, %vec.phi271.unr
  br label %middle.block260

middle.block260:                                  ; preds = %vector.body268.epil, %middle.block260.unr-lcssa
  %.lcssa281 = phi <8 x float> [ %.lcssa281.ph, %middle.block260.unr-lcssa ], [ %627, %vector.body268.epil ]
  %.lcssa280 = phi <8 x float> [ %.lcssa280.ph, %middle.block260.unr-lcssa ], [ %628, %vector.body268.epil ]
  %bin.rdx277 = fadd reassoc ninf nsz <8 x float> %.lcssa280, %.lcssa281
  %629 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %bin.rdx277)
  br i1 %cmp.n267, label %for_loop_test16.after_for15_crit_edge.us.us.us.us, label %for_loop_body13.us.us.us.us.preheader

for_loop_body13.us.us.us.us.preheader:            ; preds = %middle.block260, %vector.scevcheck258, %for_loop_test16.preheader.us.us.us.us
  %indvars.iv.ph = phi i64 [ 0, %vector.scevcheck258 ], [ 0, %for_loop_test16.preheader.us.us.us.us ], [ %60, %middle.block260 ]
  %.06573.us.us.us.us.ph = phi float [ 0.000000e+00, %vector.scevcheck258 ], [ 0.000000e+00, %for_loop_test16.preheader.us.us.us.us ], [ %629, %middle.block260 ]
  %630 = xor i64 %indvars.iv.ph, -1
  %631 = add nsw i64 %630, %wide.trip.count186
  br i1 %lcmp.mod295.not, label %for_loop_body13.us.us.us.us.prol.loopexit, label %for_loop_body13.us.us.us.us.prol.preheader

for_loop_body13.us.us.us.us.prol.preheader:       ; preds = %for_loop_body13.us.us.us.us.preheader
  %632 = trunc i64 %indvars.iv.ph to i32
  %633 = add i32 %565, %632
  %634 = mul i32 %562, %633
  %635 = add i32 %.06675.us.us.us.us, %634
  %636 = zext i32 %558 to i64
  br label %for_loop_body13.us.us.us.us.prol

for_loop_body13.us.us.us.us.prol:                 ; preds = %for_loop_body13.us.us.us.us.prol, %for_loop_body13.us.us.us.us.prol.preheader
  %lsr.iv358 = phi i64 [ %xtraiter294, %for_loop_body13.us.us.us.us.prol.preheader ], [ %lsr.iv.next359, %for_loop_body13.us.us.us.us.prol ]
  %lsr.iv356 = phi i32 [ %635, %for_loop_body13.us.us.us.us.prol.preheader ], [ %lsr.iv.next357, %for_loop_body13.us.us.us.us.prol ]
  %indvars.iv.prol = phi i64 [ %indvars.iv.next.prol, %for_loop_body13.us.us.us.us.prol ], [ %indvars.iv.ph, %for_loop_body13.us.us.us.us.prol.preheader ]
  %.06573.us.us.us.us.prol = phi float [ %645, %for_loop_body13.us.us.us.us.prol ], [ %.06573.us.us.us.us.ph, %for_loop_body13.us.us.us.us.prol.preheader ]
  %637 = add i64 %636, %indvars.iv.prol
  %tmp = trunc i64 %637 to i32
  %638 = sext i32 %tmp to i64
  %639 = getelementptr float, float* %556, i64 %638
  %640 = load float, float* %639, align 4
  %641 = sext i32 %lsr.iv356 to i64
  %642 = getelementptr float, float* %559, i64 %641
  %643 = load float, float* %642, align 4
  %644 = fmul reassoc ninf nsz float %643, %640
  %645 = fadd reassoc ninf nsz float %644, %.06573.us.us.us.us.prol
  %indvars.iv.next.prol = add nuw nsw i64 %indvars.iv.prol, 1
  %lsr.iv.next357 = add i32 %lsr.iv356, %562
  %lsr.iv.next359 = add nsw i64 %lsr.iv358, -1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next359, 0
  br i1 %prol.iter.cmp.not, label %for_loop_body13.us.us.us.us.prol.loopexit.loopexit, label %for_loop_body13.us.us.us.us.prol, !llvm.loop !22

for_loop_body13.us.us.us.us.prol.loopexit.loopexit: ; preds = %for_loop_body13.us.us.us.us.prol
  %646 = add i64 %xtraiter294, %indvars.iv.ph
  br label %for_loop_body13.us.us.us.us.prol.loopexit

for_loop_body13.us.us.us.us.prol.loopexit:        ; preds = %for_loop_body13.us.us.us.us.prol.loopexit.loopexit, %for_loop_body13.us.us.us.us.preheader
  %.lcssa282.unr = phi float [ undef, %for_loop_body13.us.us.us.us.preheader ], [ %645, %for_loop_body13.us.us.us.us.prol.loopexit.loopexit ]
  %indvars.iv.unr = phi i64 [ %indvars.iv.ph, %for_loop_body13.us.us.us.us.preheader ], [ %646, %for_loop_body13.us.us.us.us.prol.loopexit.loopexit ]
  %.06573.us.us.us.us.unr = phi float [ %.06573.us.us.us.us.ph, %for_loop_body13.us.us.us.us.preheader ], [ %645, %for_loop_body13.us.us.us.us.prol.loopexit.loopexit ]
  %647 = icmp ult i64 %631, 3
  br i1 %647, label %for_loop_test16.after_for15_crit_edge.us.us.us.us, label %for_loop_body13.us.us.us.us.preheader345

for_loop_body13.us.us.us.us.preheader345:         ; preds = %for_loop_body13.us.us.us.us.prol.loopexit
  %648 = zext i32 %558 to i64
  %649 = add i32 %565, 3
  %650 = trunc i64 %indvars.iv.unr to i32
  %651 = add i32 %649, %650
  %652 = mul i32 %562, %651
  %653 = add i32 %.06675.us.us.us.us, %652
  %654 = shl i32 %562, 2
  %655 = add i32 %565, 2
  %656 = add i32 %655, %650
  %657 = mul i32 %562, %656
  %658 = add i32 %.06675.us.us.us.us, %657
  %659 = add i32 %565, 1
  %660 = add i32 %659, %650
  %661 = mul i32 %562, %660
  %662 = add i32 %.06675.us.us.us.us, %661
  %663 = add i32 %565, %650
  %664 = mul i32 %562, %663
  %665 = add i32 %.06675.us.us.us.us, %664
  br label %for_loop_body13.us.us.us.us

for_loop_body13.us.us.us.us:                      ; preds = %for_loop_body13.us.us.us.us, %for_loop_body13.us.us.us.us.preheader345
  %lsr.iv369 = phi i32 [ %665, %for_loop_body13.us.us.us.us.preheader345 ], [ %lsr.iv.next370, %for_loop_body13.us.us.us.us ]
  %lsr.iv367 = phi i32 [ %662, %for_loop_body13.us.us.us.us.preheader345 ], [ %lsr.iv.next368, %for_loop_body13.us.us.us.us ]
  %lsr.iv364 = phi i32 [ %658, %for_loop_body13.us.us.us.us.preheader345 ], [ %lsr.iv.next365, %for_loop_body13.us.us.us.us ]
  %lsr.iv361 = phi i32 [ %653, %for_loop_body13.us.us.us.us.preheader345 ], [ %lsr.iv.next362, %for_loop_body13.us.us.us.us ]
  %indvars.iv = phi i64 [ %indvars.iv.next.3, %for_loop_body13.us.us.us.us ], [ %indvars.iv.unr, %for_loop_body13.us.us.us.us.preheader345 ]
  %.06573.us.us.us.us = phi float [ %701, %for_loop_body13.us.us.us.us ], [ %.06573.us.us.us.us.unr, %for_loop_body13.us.us.us.us.preheader345 ]
  %666 = add i64 %648, %indvars.iv
  %tmp371 = trunc i64 %666 to i32
  %667 = sext i32 %tmp371 to i64
  %668 = getelementptr float, float* %556, i64 %667
  %669 = load float, float* %668, align 4
  %670 = sext i32 %lsr.iv369 to i64
  %671 = getelementptr float, float* %559, i64 %670
  %672 = load float, float* %671, align 4
  %673 = fmul reassoc ninf nsz float %672, %669
  %674 = fadd reassoc ninf nsz float %673, %.06573.us.us.us.us
  %675 = add i64 %666, 1
  %tmp366 = trunc i64 %675 to i32
  %676 = sext i32 %tmp366 to i64
  %677 = getelementptr float, float* %556, i64 %676
  %678 = load float, float* %677, align 4
  %679 = sext i32 %lsr.iv367 to i64
  %680 = getelementptr float, float* %559, i64 %679
  %681 = load float, float* %680, align 4
  %682 = fmul reassoc ninf nsz float %681, %678
  %683 = fadd reassoc ninf nsz float %682, %674
  %684 = add i64 %666, 2
  %tmp363 = trunc i64 %684 to i32
  %685 = sext i32 %tmp363 to i64
  %686 = getelementptr float, float* %556, i64 %685
  %687 = load float, float* %686, align 4
  %688 = sext i32 %lsr.iv364 to i64
  %689 = getelementptr float, float* %559, i64 %688
  %690 = load float, float* %689, align 4
  %691 = fmul reassoc ninf nsz float %690, %687
  %692 = fadd reassoc ninf nsz float %691, %683
  %693 = add i64 %666, 3
  %tmp360 = trunc i64 %693 to i32
  %694 = sext i32 %tmp360 to i64
  %695 = getelementptr float, float* %556, i64 %694
  %696 = load float, float* %695, align 4
  %697 = sext i32 %lsr.iv361 to i64
  %698 = getelementptr float, float* %559, i64 %697
  %699 = load float, float* %698, align 4
  %700 = fmul reassoc ninf nsz float %699, %696
  %701 = fadd reassoc ninf nsz float %700, %692
  %indvars.iv.next.3 = add nuw nsw i64 %indvars.iv, 4
  %lsr.iv.next362 = add i32 %lsr.iv361, %654
  %lsr.iv.next365 = add i32 %lsr.iv364, %654
  %lsr.iv.next368 = add i32 %lsr.iv367, %654
  %lsr.iv.next370 = add i32 %lsr.iv369, %654
  %exitcond.not.3 = icmp eq i64 %wide.trip.count186, %indvars.iv.next.3
  br i1 %exitcond.not.3, label %for_loop_test16.after_for15_crit_edge.us.us.us.us.loopexit, label %for_loop_body13.us.us.us.us, !llvm.loop !23

for_loop_test16.after_for15_crit_edge.us.us.us.us.loopexit: ; preds = %for_loop_body13.us.us.us.us
  br label %for_loop_test16.after_for15_crit_edge.us.us.us.us

for_loop_test16.after_for15_crit_edge.us.us.us.us: ; preds = %for_loop_test16.after_for15_crit_edge.us.us.us.us.loopexit, %for_loop_body13.us.us.us.us.prol.loopexit, %middle.block260
  %.lcssa = phi float [ %629, %middle.block260 ], [ %.lcssa282.unr, %for_loop_body13.us.us.us.us.prol.loopexit ], [ %701, %for_loop_test16.after_for15_crit_edge.us.us.us.us.loopexit ]
  %702 = load float*, float** %35, align 8
  %703 = load i32, i32* %36, align 4
  %704 = load i32, i32* %37, align 4
  %705 = load i32, i32* %38, align 4
  %706 = mul i32 %703, %lsr439
  %707 = add i32 %706, %.06897.us
  %708 = mul i32 %707, %704
  %709 = add i32 %708, %.06776.us.us.us
  %710 = mul i32 %709, %705
  %711 = add i32 %710, %.06675.us.us.us.us
  %712 = sext i32 %711 to i64
  %713 = getelementptr float, float* %702, i64 %712
  store float %.lcssa, float* %713, align 4
  %714 = add nuw nsw i32 %.06675.us.us.us.us, 1
  %exitcond164.not = icmp eq i32 %714, %25
  br i1 %exitcond164.not, label %for_loop_test12.after_for11_crit_edge.split.us.us.us.us, label %for_loop_test16.preheader.us.us.us.us

for_loop_test12.after_for11_crit_edge.split.us.us.us.us: ; preds = %for_loop_test16.after_for15_crit_edge.us.us.us.us
  %715 = add nuw nsw i32 %.06776.us.us.us, 1
  %exitcond165.not = icmp eq i32 %715, %25
  br i1 %exitcond165.not, label %for_loop_test20.preheader.us, label %for_loop_test12.preheader.us.us.us

after_for.loopexit:                               ; preds = %for_loop_test4.after_for3_crit_edge.us
  br label %after_for

after_for.loopexit347:                            ; preds = %for_loop_test4.preheader
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit347, %after_for.loopexit, %for_loop_test4.preheader.prol.loopexit, %allocs
  ret void

for_loop_test4.preheader:                         ; preds = %for_loop_test4.preheader, %for_loop_test4.preheader.preheader346
  %indvars.iv196 = phi i64 [ %indvars.iv.next197.3, %for_loop_test4.preheader ], [ %indvars.iv196.unr, %for_loop_test4.preheader.preheader346 ]
  %716 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %717 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %716, i64 0, i32 14
  %718 = load i8*, i8** %717, align 8
  %719 = getelementptr inbounds i8, i8* %718, i64 8
  %720 = bitcast i8* %719 to float*
  %721 = load float, float* %720, align 4
  %722 = fmul reassoc ninf nsz float %721, %721
  %723 = fdiv reassoc ninf nsz float 1.000000e+00, %722
  %724 = load float*, float** %43, align 8
  %scevgep443 = getelementptr float, float* %724, i64 %indvars.iv196
  store float %723, float* %scevgep443, align 4
  %725 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %726 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %725, i64 0, i32 14
  %727 = load i8*, i8** %726, align 8
  %728 = getelementptr inbounds i8, i8* %727, i64 8
  %729 = bitcast i8* %728 to float*
  %730 = load float, float* %729, align 4
  %731 = fmul reassoc ninf nsz float %730, %730
  %732 = fdiv reassoc ninf nsz float 1.000000e+00, %731
  %733 = load float*, float** %43, align 8
  %scevgep444 = getelementptr float, float* %733, i64 1
  %scevgep445 = getelementptr float, float* %scevgep444, i64 %indvars.iv196
  store float %732, float* %scevgep445, align 4
  %734 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %735 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %734, i64 0, i32 14
  %736 = load i8*, i8** %735, align 8
  %737 = getelementptr inbounds i8, i8* %736, i64 8
  %738 = bitcast i8* %737 to float*
  %739 = load float, float* %738, align 4
  %740 = fmul reassoc ninf nsz float %739, %739
  %741 = fdiv reassoc ninf nsz float 1.000000e+00, %740
  %742 = load float*, float** %43, align 8
  %scevgep441 = getelementptr float, float* %742, i64 2
  %scevgep442 = getelementptr float, float* %scevgep441, i64 %indvars.iv196
  store float %741, float* %scevgep442, align 4
  %743 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %744 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %743, i64 0, i32 14
  %745 = load i8*, i8** %744, align 8
  %746 = getelementptr inbounds i8, i8* %745, i64 8
  %747 = bitcast i8* %746 to float*
  %748 = load float, float* %747, align 4
  %749 = fmul reassoc ninf nsz float %748, %748
  %750 = fdiv reassoc ninf nsz float 1.000000e+00, %749
  %751 = load float*, float** %43, align 8
  %scevgep = getelementptr float, float* %751, i64 3
  %scevgep440 = getelementptr float, float* %scevgep, i64 %indvars.iv196
  store float %750, float* %scevgep440, align 4
  %indvars.iv.next197.3 = add nsw i64 %indvars.iv196, 4
  %exitcond200.not.3 = icmp eq i64 %wide.trip.count194, %indvars.iv.next197.3
  br i1 %exitcond200.not.3, label %after_for.loopexit347, label %for_loop_test4.preheader
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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !24

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !26

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

; Function Attrs: nocallback nofree nosync nounwind readnone willreturn
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readnone willreturn }

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
!10 = !{!"llvm.loop.unroll.disable"}
!11 = distinct !{!11, !12}
!12 = !{!"llvm.loop.isvectorized", i32 1}
!13 = distinct !{!13, !10}
!14 = distinct !{!14, !12}
!15 = distinct !{!15, !12}
!16 = distinct !{!16, !10}
!17 = distinct !{!17, !12}
!18 = distinct !{!18, !12}
!19 = distinct !{!19, !10}
!20 = distinct !{!20, !12}
!21 = distinct !{!21, !12}
!22 = distinct !{!22, !10}
!23 = distinct !{!23, !12}
!24 = distinct !{!24, !25}
!25 = !{!"llvm.loop.mustprogress"}
!26 = distinct !{!26, !25}
