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
define void @_bit_reverse_kernel_c266_0_kernel_0_serial(%struct.RuntimeContext.6* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext.6* %context to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %1 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 0, i32 0, i32 0
  %3 = load i32, i32* %2, align 4
  %4 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %5 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %1, i64 0, i32 0, i32 0, i32 1
  %6 = load i32, i32* %5, align 4
  %7 = tail call i32 @llvm.smax.i32(i32 %6, i32 0)
  %8 = getelementptr inbounds %struct.RuntimeContext.6, %struct.RuntimeContext.6* %context, i64 0, i32 1
  %9 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %8, align 8
  %10 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %9, i64 0, i32 14
  %11 = load i8*, i8** %10, align 8
  %12 = getelementptr inbounds i8, i8* %11, i64 4
  %13 = bitcast i8* %12 to i32*
  store i32 %7, i32* %13, align 4
  %14 = mul i32 %7, %4
  %15 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %8, align 8
  %16 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %15, i64 0, i32 14
  %17 = bitcast i8** %16 to i32**
  %18 = load i32*, i32** %17, align 8
  store i32 %14, i32* %18, align 4
  ret void
}

; Function Attrs: nounwind
define void @_bit_reverse_kernel_c266_0_kernel_1_range_for(%struct.RuntimeContext.6* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext.6* %0 to { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }**
  %21 = icmp slt i32 %17, %19
  br i1 %21, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %22 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %23 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %22, i64 0, i32 3
  %24 = load i32, i32* %23, align 4
  %25 = icmp eq i32 %24, 0
  br i1 %25, label %for_loop_body.us.preheader, label %for_loop_body.preheader

for_loop_body.preheader:                          ; preds = %for_loop_body.lr.ph
  br label %for_loop_body

for_loop_body.us.preheader:                       ; preds = %for_loop_body.lr.ph
  br label %for_loop_body.us

for_loop_body.us:                                 ; preds = %after_for3.us, %for_loop_body.us.preheader
  %.01827.us = phi i32 [ %82, %after_for3.us ], [ %17, %for_loop_body.us.preheader ]
  %26 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %27 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %26, i64 0, i32 14
  %28 = load i8*, i8** %27, align 8
  %29 = getelementptr inbounds i8, i8* %28, i64 4
  %30 = bitcast i8* %29 to i32*
  %31 = load i32, i32* %30, align 4
  %32 = sdiv i32 %.01827.us, %31
  %33 = mul i32 %32, %31
  %34 = xor i32 %31, %.01827.us
  %35 = icmp slt i32 %34, 0
  %36 = icmp ne i32 %.01827.us, 0
  %37 = icmp ne i32 %33, %.01827.us
  %38 = and i1 %36, %35
  %39 = and i1 %38, %37
  %.neg19.us = sext i1 %39 to i32
  %40 = add i32 %32, %.neg19.us
  %41 = mul i32 %40, %31
  %42 = sub i32 %.01827.us, %41
  %43 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %44 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %43, i64 0, i32 2
  %45 = load i32, i32* %44, align 4
  %46 = icmp sgt i32 %45, 0
  br i1 %46, label %for_loop_body1.us.preheader, label %after_for3.us

for_loop_body1.us.preheader:                      ; preds = %for_loop_body.us
  %47 = add i32 %45, -1
  %xtraiter = and i32 %45, 7
  %48 = icmp ult i32 %47, 7
  br i1 %48, label %after_for3.us.loopexit.unr-lcssa, label %for_loop_body1.us.preheader.new

for_loop_body1.us.preheader.new:                  ; preds = %for_loop_body1.us.preheader
  %unroll_iter = and i32 %45, -8
  br label %for_loop_body1.us

after_for3.us.loopexit.unr-lcssa.loopexit:        ; preds = %for_loop_body1.us
  br label %after_for3.us.loopexit.unr-lcssa

after_for3.us.loopexit.unr-lcssa:                 ; preds = %after_for3.us.loopexit.unr-lcssa.loopexit, %for_loop_body1.us.preheader
  %.lcssa.ph = phi i32 [ undef, %for_loop_body1.us.preheader ], [ %106, %after_for3.us.loopexit.unr-lcssa.loopexit ]
  %.01624.us.unr = phi i32 [ 0, %for_loop_body1.us.preheader ], [ %106, %after_for3.us.loopexit.unr-lcssa.loopexit ]
  %.01723.us.unr = phi i32 [ %42, %for_loop_body1.us.preheader ], [ %107, %after_for3.us.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  br i1 %lcmp.mod.not, label %after_for3.us, label %for_loop_body1.us.epil.preheader

for_loop_body1.us.epil.preheader:                 ; preds = %after_for3.us.loopexit.unr-lcssa
  br label %for_loop_body1.us.epil

for_loop_body1.us.epil:                           ; preds = %for_loop_body1.us.epil, %for_loop_body1.us.epil.preheader
  %lsr.iv53 = phi i32 [ %xtraiter, %for_loop_body1.us.epil.preheader ], [ %lsr.iv.next54, %for_loop_body1.us.epil ]
  %.01624.us.epil = phi i32 [ %51, %for_loop_body1.us.epil ], [ %.01624.us.unr, %for_loop_body1.us.epil.preheader ]
  %.01723.us.epil = phi i32 [ %52, %for_loop_body1.us.epil ], [ %.01723.us.unr, %for_loop_body1.us.epil.preheader ]
  %49 = shl i32 %.01624.us.epil, 1
  %50 = and i32 %.01723.us.epil, 1
  %51 = or i32 %49, %50
  %52 = ashr i32 %.01723.us.epil, 1
  %lsr.iv.next54 = add nsw i32 %lsr.iv53, -1
  %epil.iter.cmp.not = icmp eq i32 %lsr.iv.next54, 0
  br i1 %epil.iter.cmp.not, label %after_for3.us.loopexit, label %for_loop_body1.us.epil, !llvm.loop !9

after_for3.us.loopexit:                           ; preds = %for_loop_body1.us.epil
  br label %after_for3.us

after_for3.us:                                    ; preds = %after_for3.us.loopexit, %after_for3.us.loopexit.unr-lcssa, %for_loop_body.us
  %.016.lcssa.us = phi i32 [ 0, %for_loop_body.us ], [ %.lcssa.ph, %after_for3.us.loopexit.unr-lcssa ], [ %51, %after_for3.us.loopexit ]
  %53 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %43, i64 0, i32 0, i32 1
  %54 = load float*, float** %53, align 8
  %55 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %43, i64 0, i32 0, i32 0, i32 1
  %56 = load i32, i32* %55, align 4
  %57 = mul i32 %56, %40
  %58 = add i32 %57, %42
  %59 = shl i32 %58, 1
  %60 = sext i32 %59 to i64
  %61 = getelementptr float, float* %54, i64 %60
  %62 = load float, float* %61, align 4
  %63 = getelementptr float, float* %61, i64 1
  %64 = load float, float* %63, align 4
  %65 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %43, i64 0, i32 1, i32 1
  %66 = load float*, float** %65, align 8
  %67 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %43, i64 0, i32 1, i32 0, i32 1
  %68 = load i32, i32* %67, align 4
  %69 = mul i32 %68, %40
  %70 = add i32 %69, %.016.lcssa.us
  %71 = shl i32 %70, 1
  %72 = sext i32 %71 to i64
  %73 = getelementptr float, float* %66, i64 %72
  store float %62, float* %73, align 4
  %74 = load float*, float** %65, align 8
  %75 = load i32, i32* %67, align 4
  %76 = mul i32 %75, %40
  %77 = add i32 %76, %.016.lcssa.us
  %78 = shl i32 %77, 1
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, float* %74, i64 %79
  %81 = getelementptr float, float* %80, i64 1
  store float %64, float* %81, align 4
  %82 = add nsw i32 %.01827.us, 1
  %exitcond30.not = icmp eq i32 %82, %19
  br i1 %exitcond30.not, label %after_for.loopexit, label %for_loop_body.us

for_loop_body1.us:                                ; preds = %for_loop_body1.us, %for_loop_body1.us.preheader.new
  %lsr.iv = phi i32 [ %lsr.iv.next, %for_loop_body1.us ], [ %unroll_iter, %for_loop_body1.us.preheader.new ]
  %.01624.us = phi i32 [ 0, %for_loop_body1.us.preheader.new ], [ %106, %for_loop_body1.us ]
  %.01723.us = phi i32 [ %42, %for_loop_body1.us.preheader.new ], [ %107, %for_loop_body1.us ]
  %83 = shl i32 %.01624.us, 3
  %84 = shl i32 %.01723.us, 2
  %85 = and i32 %84, 4
  %86 = or i32 %83, %85
  %87 = and i32 %.01723.us, 2
  %88 = or i32 %86, %87
  %89 = lshr i32 %.01723.us, 4
  %90 = shl i32 %88, 2
  %.01723.us.mask = and i32 %.01723.us, 4
  %91 = or i32 %.01723.us.mask, %90
  %92 = lshr i32 %.01723.us, 2
  %93 = and i32 %92, 2
  %94 = or i32 %91, %93
  %95 = and i32 %89, 1
  %96 = or i32 %94, %95
  %97 = lshr i32 %.01723.us, 6
  %98 = shl i32 %96, 2
  %99 = and i32 %89, 2
  %100 = or i32 %98, %99
  %101 = and i32 %97, 1
  %102 = or i32 %100, %101
  %103 = lshr i32 %.01723.us, 7
  %104 = shl i32 %102, 1
  %105 = and i32 %103, 1
  %106 = or i32 %104, %105
  %107 = ashr i32 %.01723.us, 8
  %lsr.iv.next = add i32 %lsr.iv, -8
  %niter.ncmp.7 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter.ncmp.7, label %after_for3.us.loopexit.unr-lcssa.loopexit, label %for_loop_body1.us

for_loop_body:                                    ; preds = %after_for7, %for_loop_body.preheader
  %.01827 = phi i32 [ %189, %after_for7 ], [ %17, %for_loop_body.preheader ]
  %108 = load %struct.LLVMRuntime.5*, %struct.LLVMRuntime.5** %3, align 8
  %109 = getelementptr inbounds %struct.LLVMRuntime.5, %struct.LLVMRuntime.5* %108, i64 0, i32 14
  %110 = load i8*, i8** %109, align 8
  %111 = getelementptr inbounds i8, i8* %110, i64 4
  %112 = bitcast i8* %111 to i32*
  %113 = load i32, i32* %112, align 4
  %114 = sdiv i32 %.01827, %113
  %115 = mul i32 %114, %113
  %116 = xor i32 %113, %.01827
  %117 = icmp slt i32 %116, 0
  %118 = icmp ne i32 %.01827, 0
  %119 = icmp ne i32 %115, %.01827
  %120 = and i1 %118, %117
  %121 = and i1 %120, %119
  %.neg19 = sext i1 %121 to i32
  %122 = add i32 %114, %.neg19
  %123 = mul i32 %122, %113
  %124 = sub i32 %.01827, %123
  %125 = load { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }*, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }** %20, align 8
  %126 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %125, i64 0, i32 2
  %127 = load i32, i32* %126, align 4
  %128 = icmp sgt i32 %127, 0
  br i1 %128, label %for_loop_body5.preheader, label %after_for7

for_loop_body5.preheader:                         ; preds = %for_loop_body
  %129 = add i32 %127, -1
  %xtraiter40 = and i32 %127, 7
  %130 = icmp ult i32 %129, 7
  br i1 %130, label %after_for7.loopexit.unr-lcssa, label %for_loop_body5.preheader.new

for_loop_body5.preheader.new:                     ; preds = %for_loop_body5.preheader
  %unroll_iter44 = and i32 %127, -8
  br label %for_loop_body5

after_for.loopexit:                               ; preds = %after_for3.us
  br label %after_for

after_for.loopexit52:                             ; preds = %after_for7
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit52, %after_for.loopexit, %allocs
  ret void

for_loop_body5:                                   ; preds = %for_loop_body5, %for_loop_body5.preheader.new
  %lsr.iv55 = phi i32 [ %lsr.iv.next56, %for_loop_body5 ], [ %unroll_iter44, %for_loop_body5.preheader.new ]
  %.01421 = phi i32 [ 0, %for_loop_body5.preheader.new ], [ %154, %for_loop_body5 ]
  %.120 = phi i32 [ %122, %for_loop_body5.preheader.new ], [ %155, %for_loop_body5 ]
  %131 = shl i32 %.01421, 3
  %132 = shl i32 %.120, 2
  %133 = and i32 %132, 4
  %134 = or i32 %131, %133
  %135 = and i32 %.120, 2
  %136 = or i32 %134, %135
  %137 = lshr i32 %.120, 4
  %138 = shl i32 %136, 2
  %.120.mask = and i32 %.120, 4
  %139 = or i32 %.120.mask, %138
  %140 = lshr i32 %.120, 2
  %141 = and i32 %140, 2
  %142 = or i32 %139, %141
  %143 = and i32 %137, 1
  %144 = or i32 %142, %143
  %145 = lshr i32 %.120, 6
  %146 = shl i32 %144, 2
  %147 = and i32 %137, 2
  %148 = or i32 %146, %147
  %149 = and i32 %145, 1
  %150 = or i32 %148, %149
  %151 = lshr i32 %.120, 7
  %152 = shl i32 %150, 1
  %153 = and i32 %151, 1
  %154 = or i32 %152, %153
  %155 = ashr i32 %.120, 8
  %lsr.iv.next56 = add i32 %lsr.iv55, -8
  %niter45.ncmp.7 = icmp eq i32 %lsr.iv.next56, 0
  br i1 %niter45.ncmp.7, label %after_for7.loopexit.unr-lcssa.loopexit, label %for_loop_body5

after_for7.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body5
  br label %after_for7.loopexit.unr-lcssa

after_for7.loopexit.unr-lcssa:                    ; preds = %after_for7.loopexit.unr-lcssa.loopexit, %for_loop_body5.preheader
  %.lcssa38.ph = phi i32 [ undef, %for_loop_body5.preheader ], [ %154, %after_for7.loopexit.unr-lcssa.loopexit ]
  %.01421.unr = phi i32 [ 0, %for_loop_body5.preheader ], [ %154, %after_for7.loopexit.unr-lcssa.loopexit ]
  %.120.unr = phi i32 [ %122, %for_loop_body5.preheader ], [ %155, %after_for7.loopexit.unr-lcssa.loopexit ]
  %lcmp.mod42.not = icmp eq i32 %xtraiter40, 0
  br i1 %lcmp.mod42.not, label %after_for7, label %for_loop_body5.epil.preheader

for_loop_body5.epil.preheader:                    ; preds = %after_for7.loopexit.unr-lcssa
  br label %for_loop_body5.epil

for_loop_body5.epil:                              ; preds = %for_loop_body5.epil, %for_loop_body5.epil.preheader
  %lsr.iv57 = phi i32 [ %xtraiter40, %for_loop_body5.epil.preheader ], [ %lsr.iv.next58, %for_loop_body5.epil ]
  %.01421.epil = phi i32 [ %158, %for_loop_body5.epil ], [ %.01421.unr, %for_loop_body5.epil.preheader ]
  %.120.epil = phi i32 [ %159, %for_loop_body5.epil ], [ %.120.unr, %for_loop_body5.epil.preheader ]
  %156 = shl i32 %.01421.epil, 1
  %157 = and i32 %.120.epil, 1
  %158 = or i32 %156, %157
  %159 = ashr i32 %.120.epil, 1
  %lsr.iv.next58 = add nsw i32 %lsr.iv57, -1
  %epil.iter41.cmp.not = icmp eq i32 %lsr.iv.next58, 0
  br i1 %epil.iter41.cmp.not, label %after_for7.loopexit, label %for_loop_body5.epil, !llvm.loop !11

after_for7.loopexit:                              ; preds = %for_loop_body5.epil
  br label %after_for7

after_for7:                                       ; preds = %after_for7.loopexit, %after_for7.loopexit.unr-lcssa, %for_loop_body
  %.014.lcssa = phi i32 [ 0, %for_loop_body ], [ %.lcssa38.ph, %after_for7.loopexit.unr-lcssa ], [ %158, %after_for7.loopexit ]
  %160 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %125, i64 0, i32 0, i32 1
  %161 = load float*, float** %160, align 8
  %162 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %125, i64 0, i32 0, i32 0, i32 1
  %163 = load i32, i32* %162, align 4
  %164 = mul i32 %163, %122
  %165 = add i32 %164, %124
  %166 = shl i32 %165, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, float* %161, i64 %167
  %169 = load float, float* %168, align 4
  %170 = getelementptr float, float* %168, i64 1
  %171 = load float, float* %170, align 4
  %172 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %125, i64 0, i32 1, i32 1
  %173 = load float*, float** %172, align 8
  %174 = getelementptr { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }, { { { i32, i32 }, float* }, { { i32, i32 }, float* }, i32, i32 }* %125, i64 0, i32 1, i32 0, i32 1
  %175 = load i32, i32* %174, align 4
  %176 = mul i32 %175, %.014.lcssa
  %177 = add i32 %176, %124
  %178 = shl i32 %177, 1
  %179 = sext i32 %178 to i64
  %180 = getelementptr float, float* %173, i64 %179
  store float %169, float* %180, align 4
  %181 = load float*, float** %172, align 8
  %182 = load i32, i32* %174, align 4
  %183 = mul i32 %182, %.014.lcssa
  %184 = add i32 %183, %124
  %185 = shl i32 %184, 1
  %186 = sext i32 %185 to i64
  %187 = getelementptr float, float* %181, i64 %186
  %188 = getelementptr float, float* %187, i64 1
  store float %171, float* %188, align 4
  %189 = add nsw i32 %.01827, 1
  %exitcond32.not = icmp eq i32 %189, %19
  br i1 %exitcond32.not, label %after_for.loopexit52, label %for_loop_body
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !12

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !14

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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

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
!10 = !{!"llvm.loop.unroll.disable"}
!11 = distinct !{!11, !10}
!12 = distinct !{!12, !13}
!13 = !{!"llvm.loop.mustprogress"}
!14 = distinct !{!14, !13}
