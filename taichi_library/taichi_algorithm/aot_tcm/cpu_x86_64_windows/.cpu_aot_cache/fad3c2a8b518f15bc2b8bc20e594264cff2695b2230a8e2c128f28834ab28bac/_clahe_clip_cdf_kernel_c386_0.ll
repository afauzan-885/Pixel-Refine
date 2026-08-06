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
define void @_clahe_clip_cdf_kernel_c386_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %1, i64 0, i32 2
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = bitcast i8** %6 to i32**
  %8 = load i32*, i32** %7, align 8
  store i32 %3, i32* %8, align 4
  ret void
}

; Function Attrs: nounwind
define void @_clahe_clip_cdf_kernel_c386_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 3
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 4
  %25 = load i32, i32* %24, align 4
  %26 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %27 = load i32, i32* %26, align 4
  %28 = add i32 %23, -1
  %29 = sitofp i32 %27 to float
  %30 = sitofp i32 %28 to float
  %31 = icmp slt i32 %23, 0
  %32 = icmp slt i32 %17, %19
  br i1 %32, label %for_loop_test4.preheader.lr.ph, label %after_for

for_loop_test4.preheader.lr.ph:                   ; preds = %allocs
  %33 = icmp sgt i32 %23, 0
  %34 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %35 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %36 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 1
  %37 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, i32, i32, i32, i32 }* %21, i64 0, i32 1, i32 0, i32 1
  %xtraiter = and i32 %23, 1
  %38 = icmp eq i32 %28, 0
  %unroll_iter = and i32 %23, -2
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  %xtraiter50 = and i32 %23, 3
  %39 = icmp ult i32 %28, 3
  %unroll_iter52 = and i32 %23, -4
  %lcmp.mod51.not = icmp eq i32 %xtraiter50, 0
  br label %for_loop_test4.preheader

after_for.loopexit:                               ; preds = %after_for20
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

for_loop_test4.preheader:                         ; preds = %after_for20, %for_loop_test4.preheader.lr.ph
  %.02744 = phi i32 [ %17, %for_loop_test4.preheader.lr.ph ], [ %204, %after_for20 ]
  br i1 %33, label %for_loop_body1.preheader, label %after_for3

for_loop_body1.preheader:                         ; preds = %for_loop_test4.preheader
  br i1 %38, label %after_for3.loopexit.unr-lcssa, label %for_loop_body1.preheader64

for_loop_body1.preheader64:                       ; preds = %for_loop_body1.preheader
  br label %for_loop_body1

for_loop_body1:                                   ; preds = %after_if.1, %for_loop_body1.preheader64
  %.02537 = phi i32 [ %82, %after_if.1 ], [ 0, %for_loop_body1.preheader64 ]
  %.02636 = phi i32 [ %.1.1, %after_if.1 ], [ 0, %for_loop_body1.preheader64 ]
  %40 = load i32*, i32** %34, align 8
  %41 = load i32, i32* %35, align 4
  %42 = mul i32 %.02744, %41
  %43 = add i32 %.02537, %42
  %44 = sext i32 %43 to i64
  %45 = getelementptr i32, i32* %40, i64 %44
  %46 = load i32, i32* %45, align 4
  %47 = icmp sgt i32 %46, %25
  br i1 %47, label %true_block, label %after_if

after_for3.loopexit.unr-lcssa.loopexit:           ; preds = %after_if.1
  br label %after_for3.loopexit.unr-lcssa

after_for3.loopexit.unr-lcssa:                    ; preds = %after_for3.loopexit.unr-lcssa.loopexit, %for_loop_body1.preheader
  %.1.lcssa.ph = phi i32 [ undef, %for_loop_body1.preheader ], [ %.1.1, %after_for3.loopexit.unr-lcssa.loopexit ]
  %.02537.unr = phi i32 [ 0, %for_loop_body1.preheader ], [ %82, %after_for3.loopexit.unr-lcssa.loopexit ]
  %.02636.unr = phi i32 [ 0, %for_loop_body1.preheader ], [ %.1.1, %after_for3.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for3, label %for_loop_body1.epil

for_loop_body1.epil:                              ; preds = %after_for3.loopexit.unr-lcssa
  %48 = load i32*, i32** %34, align 8
  %49 = load i32, i32* %35, align 4
  %50 = mul i32 %49, %.02744
  %51 = add i32 %50, %.02537.unr
  %52 = sext i32 %51 to i64
  %53 = getelementptr i32, i32* %48, i64 %52
  %54 = load i32, i32* %53, align 4
  %55 = icmp sgt i32 %54, %25
  br i1 %55, label %true_block.epil, label %after_for3

true_block.epil:                                  ; preds = %for_loop_body1.epil
  %56 = sub i32 %.02636.unr, %25
  %57 = add i32 %56, %54
  store i32 %25, i32* %53, align 4
  br label %after_for3

after_for3:                                       ; preds = %true_block.epil, %for_loop_body1.epil, %after_for3.loopexit.unr-lcssa, %for_loop_test4.preheader
  %.026.lcssa = phi i32 [ 0, %for_loop_test4.preheader ], [ %.1.lcssa.ph, %after_for3.loopexit.unr-lcssa ], [ %57, %true_block.epil ], [ %.02636.unr, %for_loop_body1.epil ]
  %58 = sdiv i32 %.026.lcssa, %23
  %59 = mul i32 %58, %23
  %60 = xor i32 %.026.lcssa, %23
  %61 = icmp slt i32 %60, 0
  %62 = icmp ne i32 %.026.lcssa, 0
  %63 = icmp ne i32 %59, %.026.lcssa
  %64 = and i1 %62, %61
  %65 = and i1 %64, %63
  %.neg33 = sext i1 %65 to i32
  %66 = add i32 %58, %.neg33
  %67 = mul i32 %66, %23
  %68 = sub i32 %.026.lcssa, %67
  br i1 %33, label %for_loop_body5.preheader, label %after_for7

for_loop_body5.preheader:                         ; preds = %after_for3
  br i1 %39, label %after_for7.loopexit.unr-lcssa, label %for_loop_body5.preheader63

for_loop_body5.preheader63:                       ; preds = %for_loop_body5.preheader
  br label %for_loop_body5

true_block:                                       ; preds = %for_loop_body1
  %69 = sub i32 %.02636, %25
  %70 = add i32 %69, %46
  store i32 %25, i32* %45, align 4
  br label %after_if

after_if:                                         ; preds = %true_block, %for_loop_body1
  %.1 = phi i32 [ %70, %true_block ], [ %.02636, %for_loop_body1 ]
  %71 = load i32*, i32** %34, align 8
  %72 = load i32, i32* %35, align 4
  %73 = mul i32 %.02744, %72
  %74 = add i32 %.02537, %73
  %75 = add i32 %74, 1
  %76 = sext i32 %75 to i64
  %77 = getelementptr i32, i32* %71, i64 %76
  %78 = load i32, i32* %77, align 4
  %79 = icmp sgt i32 %78, %25
  br i1 %79, label %true_block.1, label %after_if.1

true_block.1:                                     ; preds = %after_if
  %80 = sub i32 %.1, %25
  %81 = add i32 %80, %78
  store i32 %25, i32* %77, align 4
  br label %after_if.1

after_if.1:                                       ; preds = %true_block.1, %after_if
  %.1.1 = phi i32 [ %81, %true_block.1 ], [ %.1, %after_if ]
  %82 = add nuw i32 %.02537, 2
  %niter.ncmp.1 = icmp eq i32 %unroll_iter, %82
  br i1 %niter.ncmp.1, label %after_for3.loopexit.unr-lcssa.loopexit, label %for_loop_body1

for_loop_body5:                                   ; preds = %for_loop_body5, %for_loop_body5.preheader63
  %.02438 = phi i32 [ %118, %for_loop_body5 ], [ 0, %for_loop_body5.preheader63 ]
  %83 = load i32*, i32** %34, align 8
  %84 = load i32, i32* %35, align 4
  %85 = mul i32 %.02744, %84
  %86 = add i32 %.02438, %85
  %87 = sext i32 %86 to i64
  %88 = getelementptr i32, i32* %83, i64 %87
  %89 = load i32, i32* %88, align 4
  %90 = add i32 %89, %66
  store i32 %90, i32* %88, align 4
  %91 = load i32*, i32** %34, align 8
  %92 = load i32, i32* %35, align 4
  %93 = mul i32 %.02744, %92
  %94 = add i32 %.02438, %93
  %95 = add i32 %94, 1
  %96 = sext i32 %95 to i64
  %97 = getelementptr i32, i32* %91, i64 %96
  %98 = load i32, i32* %97, align 4
  %99 = add i32 %98, %66
  store i32 %99, i32* %97, align 4
  %100 = load i32*, i32** %34, align 8
  %101 = load i32, i32* %35, align 4
  %102 = mul i32 %.02744, %101
  %103 = add i32 %.02438, %102
  %104 = add i32 %103, 2
  %105 = sext i32 %104 to i64
  %106 = getelementptr i32, i32* %100, i64 %105
  %107 = load i32, i32* %106, align 4
  %108 = add i32 %107, %66
  store i32 %108, i32* %106, align 4
  %109 = load i32*, i32** %34, align 8
  %110 = load i32, i32* %35, align 4
  %111 = mul i32 %.02744, %110
  %112 = add i32 %.02438, %111
  %113 = add i32 %112, 3
  %114 = sext i32 %113 to i64
  %115 = getelementptr i32, i32* %109, i64 %114
  %116 = load i32, i32* %115, align 4
  %117 = add i32 %116, %66
  store i32 %117, i32* %115, align 4
  %118 = add nuw i32 %.02438, 4
  %niter53.ncmp.3 = icmp eq i32 %unroll_iter52, %118
  br i1 %niter53.ncmp.3, label %after_for7.loopexit.unr-lcssa.loopexit, label %for_loop_body5

after_for7.loopexit.unr-lcssa.loopexit:           ; preds = %for_loop_body5
  br label %after_for7.loopexit.unr-lcssa

after_for7.loopexit.unr-lcssa:                    ; preds = %after_for7.loopexit.unr-lcssa.loopexit, %for_loop_body5.preheader
  %.02438.unr = phi i32 [ 0, %for_loop_body5.preheader ], [ %118, %after_for7.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod51.not, label %after_for7, label %for_loop_body5.epil.preheader

for_loop_body5.epil.preheader:                    ; preds = %after_for7.loopexit.unr-lcssa
  br label %for_loop_body5.epil

for_loop_body5.epil:                              ; preds = %for_loop_body5.epil, %for_loop_body5.epil.preheader
  %lsr.iv = phi i32 [ %xtraiter50, %for_loop_body5.epil.preheader ], [ %lsr.iv.next, %for_loop_body5.epil ]
  %.02438.epil = phi i32 [ %127, %for_loop_body5.epil ], [ %.02438.unr, %for_loop_body5.epil.preheader ]
  %119 = load i32*, i32** %34, align 8
  %120 = load i32, i32* %35, align 4
  %121 = mul i32 %.02744, %120
  %122 = add i32 %.02438.epil, %121
  %123 = sext i32 %122 to i64
  %124 = getelementptr i32, i32* %119, i64 %123
  %125 = load i32, i32* %124, align 4
  %126 = add i32 %125, %66
  store i32 %126, i32* %124, align 4
  %127 = add nuw nsw i32 %.02438.epil, 1
  %lsr.iv.next = add nsw i32 %lsr.iv, -1
  %epil.iter.cmp.not = icmp eq i32 %lsr.iv.next, 0
  br i1 %epil.iter.cmp.not, label %after_for7.loopexit, label %for_loop_body5.epil, !llvm.loop !9

after_for7.loopexit:                              ; preds = %for_loop_body5.epil
  br label %after_for7

after_for7:                                       ; preds = %after_for7.loopexit, %after_for7.loopexit.unr-lcssa, %after_for3
  %128 = icmp sgt i32 %68, 0
  br i1 %128, label %true_block9, label %after_if11

true_block9:                                      ; preds = %after_for7
  %129 = sdiv i32 %23, %68
  %130 = mul i32 %129, %68
  %131 = icmp ne i32 %130, %23
  %132 = and i1 %31, %131
  %.neg34 = sext i1 %132 to i32
  %133 = add i32 %129, %.neg34
  %134 = tail call i32 @llvm.smax.i32(i32 %133, i32 1)
  br i1 %33, label %after_if17.preheader, label %after_for20

after_if17.preheader:                             ; preds = %true_block9
  br label %after_if17

after_if11.loopexit:                              ; preds = %after_if17
  br label %after_if11

after_if11:                                       ; preds = %after_if11.loopexit, %after_for7
  br i1 %33, label %for_loop_body18.preheader, label %after_for20

for_loop_body18.preheader:                        ; preds = %after_if11
  br i1 %38, label %after_for20.loopexit.unr-lcssa, label %for_loop_body18.preheader62

for_loop_body18.preheader62:                      ; preds = %for_loop_body18.preheader
  br label %for_loop_body18

after_if17:                                       ; preds = %after_if17, %after_if17.preheader
  %.02241 = phi i32 [ %143, %after_if17 ], [ %68, %after_if17.preheader ]
  %.02340 = phi i32 [ %144, %after_if17 ], [ 0, %after_if17.preheader ]
  %135 = load i32*, i32** %34, align 8
  %136 = load i32, i32* %35, align 4
  %137 = mul i32 %.02744, %136
  %138 = add i32 %.02340, %137
  %139 = sext i32 %138 to i64
  %140 = getelementptr i32, i32* %135, i64 %139
  %141 = load i32, i32* %140, align 4
  %142 = add i32 %141, 1
  store i32 %142, i32* %140, align 4
  %143 = add nsw i32 %.02241, -1
  %144 = add i32 %.02340, %134
  %145 = icmp ugt i32 %.02241, 1
  %146 = icmp slt i32 %144, %23
  %spec.select = select i1 %145, i1 %146, i1 false
  br i1 %spec.select, label %after_if17, label %after_if11.loopexit

for_loop_body18:                                  ; preds = %for_loop_body18, %for_loop_body18.preheader62
  %.043 = phi i32 [ %185, %for_loop_body18 ], [ 0, %for_loop_body18.preheader62 ]
  %.02042 = phi i32 [ %173, %for_loop_body18 ], [ 0, %for_loop_body18.preheader62 ]
  %147 = load i32*, i32** %34, align 8
  %148 = load i32, i32* %35, align 4
  %149 = mul i32 %.02744, %148
  %150 = add i32 %.043, %149
  %151 = sext i32 %150 to i64
  %152 = getelementptr i32, i32* %147, i64 %151
  %153 = load i32, i32* %152, align 4
  %154 = add i32 %153, %.02042
  %155 = sitofp i32 %154 to float
  %156 = fmul reassoc ninf nsz float %155, %30
  %157 = fdiv reassoc ninf nsz float %156, %29
  %158 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %157, float %30)
  %159 = load float*, float** %36, align 8
  %160 = load i32, i32* %37, align 4
  %161 = mul i32 %.02744, %160
  %162 = add i32 %.043, %161
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, float* %159, i64 %163
  store float %158, float* %164, align 4
  %165 = load i32*, i32** %34, align 8
  %166 = load i32, i32* %35, align 4
  %167 = mul i32 %.02744, %166
  %168 = add i32 %.043, %167
  %169 = add i32 %168, 1
  %170 = sext i32 %169 to i64
  %171 = getelementptr i32, i32* %165, i64 %170
  %172 = load i32, i32* %171, align 4
  %173 = add i32 %172, %154
  %174 = sitofp i32 %173 to float
  %175 = fmul reassoc ninf nsz float %174, %30
  %176 = fdiv reassoc ninf nsz float %175, %29
  %177 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %176, float %30)
  %178 = load float*, float** %36, align 8
  %179 = load i32, i32* %37, align 4
  %180 = mul i32 %.02744, %179
  %181 = add i32 %.043, %180
  %182 = add i32 %181, 1
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, float* %178, i64 %183
  store float %177, float* %184, align 4
  %185 = add nuw i32 %.043, 2
  %niter58.ncmp.1 = icmp eq i32 %unroll_iter, %185
  br i1 %niter58.ncmp.1, label %after_for20.loopexit.unr-lcssa.loopexit, label %for_loop_body18

after_for20.loopexit.unr-lcssa.loopexit:          ; preds = %for_loop_body18
  br label %after_for20.loopexit.unr-lcssa

after_for20.loopexit.unr-lcssa:                   ; preds = %after_for20.loopexit.unr-lcssa.loopexit, %for_loop_body18.preheader
  %.043.unr = phi i32 [ 0, %for_loop_body18.preheader ], [ %185, %after_for20.loopexit.unr-lcssa.loopexit ]
  %.02042.unr = phi i32 [ 0, %for_loop_body18.preheader ], [ %173, %after_for20.loopexit.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %after_for20, label %for_loop_body18.epil

for_loop_body18.epil:                             ; preds = %after_for20.loopexit.unr-lcssa
  %186 = load i32*, i32** %34, align 8
  %187 = load i32, i32* %35, align 4
  %188 = mul i32 %187, %.02744
  %189 = add i32 %188, %.043.unr
  %190 = sext i32 %189 to i64
  %191 = getelementptr i32, i32* %186, i64 %190
  %192 = load i32, i32* %191, align 4
  %193 = add i32 %192, %.02042.unr
  %194 = sitofp i32 %193 to float
  %195 = fmul reassoc ninf nsz float %194, %30
  %196 = fdiv reassoc ninf nsz float %195, %29
  %197 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %196, float %30)
  %198 = load float*, float** %36, align 8
  %199 = load i32, i32* %37, align 4
  %200 = mul i32 %199, %.02744
  %201 = add i32 %200, %.043.unr
  %202 = sext i32 %201 to i64
  %203 = getelementptr float, float* %198, i64 %202
  store float %197, float* %203, align 4
  br label %after_for20

after_for20:                                      ; preds = %for_loop_body18.epil, %after_for20.loopexit.unr-lcssa, %after_if11, %true_block9
  %204 = add nsw i32 %.02744, 1
  %exitcond48.not = icmp eq i32 %204, %19
  br i1 %exitcond48.not, label %after_for.loopexit, label %for_loop_test4.preheader
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare float @llvm.minnum.f32(float, float) #3

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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !11

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !13

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

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
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
!10 = !{!"llvm.loop.unroll.disable"}
!11 = distinct !{!11, !12}
!12 = !{!"llvm.loop.mustprogress"}
!13 = distinct !{!13, !12}
