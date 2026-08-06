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
define void @_hough_peaks_kernel_c402_0_kernel_0_serial(%struct.RuntimeContext* nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast %struct.RuntimeContext* %context to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }**
  %1 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }** %0, align 8
  %2 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %1, i64 0, i32 3
  %3 = load i32, i32* %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, %struct.RuntimeContext* %context, i64 0, i32 1
  %5 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %5, i64 0, i32 14
  %7 = load i8*, i8** %6, align 8
  %8 = getelementptr inbounds i8, i8* %7, i64 8
  %9 = bitcast i8* %8 to i32*
  store i32 %3, i32* %9, align 4
  %10 = tail call i32 @llvm.smax.i32(i32 %3, i32 0)
  %11 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }** %0, align 8
  %12 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %11, i64 0, i32 4
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
define void @_hough_peaks_kernel_c402_0_kernel_1_range_for(%struct.RuntimeContext* %context) local_unnamed_addr #1 {
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

; Function Attrs: nofree nounwind
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
  %20 = bitcast %struct.RuntimeContext* %0 to { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }**
  %21 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }** %20, align 8
  %22 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 5
  %23 = load i32, i32* %22, align 4
  %24 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 6
  %25 = load i32, i32* %24, align 4
  %.fr74 = freeze i32 %25
  %neg = sub i32 0, %.fr74
  %26 = icmp slt i32 %17, %19
  br i1 %26, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %27 = add i32 %.fr74, 1
  %28 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 1
  %29 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %21, i64 0, i32 0, i32 0, i32 1
  %30 = icmp sgt i32 %27, %neg
  %31 = sext i32 %neg to i64
  %wide.trip.count80 = sext i32 %27 to i64
  %32 = xor i64 %31, -1
  %33 = add nsw i64 %32, %wide.trip.count80
  %34 = sub i32 %17, %.fr74
  %35 = sub nsw i64 %wide.trip.count80, %31
  %36 = add nsw i64 %35, -8
  %37 = lshr i64 %36, 3
  %38 = add nuw nsw i64 %37, 1
  %min.iters.check107 = icmp ult i64 %35, 8
  %39 = trunc i64 %33 to i32
  %40 = icmp ugt i64 %33, 4294967295
  %n.vec110 = and i64 %35, -8
  %ind.end111 = add nsw i64 %n.vec110, %31
  %.splatinsert119 = insertelement <8 x i32> poison, i32 %neg, i64 0
  %.splat120 = shufflevector <8 x i32> %.splatinsert119, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction121 = add <8 x i32> %.splat120, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %xtraiter = and i64 %38, 1
  %41 = icmp ult i64 %36, 8
  %unroll_iter = and i64 %38, 4611686018427387902
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  %cmp.n113 = icmp eq i64 %35, %n.vec110
  %42 = sub nsw i64 0, %wide.trip.count80
  %.splatinsert = insertelement <8 x i64> poison, i64 %31, i64 0
  %.splat = shufflevector <8 x i64> %.splatinsert, <8 x i64> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i64> %.splat, <i64 0, i64 1, i64 2, i64 3, i64 4, i64 5, i64 6, i64 7>
  br label %for_loop_body

for_loop_body:                                    ; preds = %for_loop_inc, %for_loop_body.lr.ph
  %indvar = phi i32 [ 0, %for_loop_body.lr.ph ], [ %indvar.next, %for_loop_inc ]
  %.02036 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %265, %for_loop_inc ]
  %43 = add i32 %34, %indvar
  %44 = load %struct.LLVMRuntime*, %struct.LLVMRuntime** %3, align 8
  %45 = getelementptr inbounds %struct.LLVMRuntime, %struct.LLVMRuntime* %44, i64 0, i32 14
  %46 = load i8*, i8** %45, align 8
  %47 = getelementptr inbounds i8, i8* %46, i64 4
  %48 = bitcast i8* %47 to i32*
  %49 = load i32, i32* %48, align 4
  %50 = sdiv i32 %.02036, %49
  %51 = mul i32 %50, %49
  %52 = xor i32 %49, %.02036
  %53 = icmp slt i32 %52, 0
  %54 = icmp ne i32 %.02036, 0
  %55 = icmp ne i32 %51, %.02036
  %56 = and i1 %54, %53
  %57 = and i1 %56, %55
  %.neg28 = sext i1 %57 to i32
  %58 = add i32 %50, %.neg28
  %59 = mul i32 %58, %49
  %60 = sub i32 %.02036, %59
  %61 = load i32*, i32** %28, align 8
  %62 = load i32, i32* %29, align 4
  %63 = mul i32 %58, %62
  %64 = add i32 %60, %63
  %65 = sext i32 %64 to i64
  %66 = getelementptr i32, i32* %61, i64 %65
  %67 = load i32, i32* %66, align 4
  %68 = icmp slt i32 %67, %23
  br i1 %68, label %for_loop_inc, label %for_loop_test4.preheader

for_loop_test4.preheader:                         ; preds = %for_loop_body
  br i1 %30, label %for_loop_body1.lr.ph, label %true_block31

for_loop_body1.lr.ph:                             ; preds = %for_loop_test4.preheader
  %69 = getelementptr inbounds i8, i8* %46, i64 8
  %70 = bitcast i8* %69 to i32*
  %71 = getelementptr inbounds i8, i8* %46, i64 12
  %72 = bitcast i8* %71 to i32*
  %73 = sub i32 %43, %59
  %broadcast.splatinsert124 = insertelement <8 x i32> poison, i32 %60, i64 0
  %broadcast.splat125 = shufflevector <8 x i32> %broadcast.splatinsert124, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert126 = insertelement <8 x i32*> poison, i32* %72, i64 0
  %broadcast.splat127 = shufflevector <8 x i32*> %broadcast.splatinsert126, <8 x i32*> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert130 = insertelement <8 x i32> poison, i32 %67, i64 0
  %broadcast.splat131 = shufflevector <8 x i32> %broadcast.splatinsert130, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert91 = insertelement <8 x i32*> poison, i32* %70, i64 0
  %broadcast.splat92 = shufflevector <8 x i32*> %broadcast.splatinsert91, <8 x i32*> poison, <8 x i32> zeroinitializer
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.after_for7_crit_edge.us, %for_loop_body1.lr.ph
  %.01834.us = phi i32 [ %neg, %for_loop_body1.lr.ph ], [ %77, %for_loop_test8.after_for7_crit_edge.us ]
  %.01933.us = phi i1 [ true, %for_loop_body1.lr.ph ], [ %.us-phi.us, %for_loop_test8.after_for7_crit_edge.us ]
  %74 = add i32 %.01834.us, %58
  %.fr = freeze i32 %74
  %75 = icmp sgt i32 %.fr, -1
  %76 = mul i32 %.fr, %62
  br i1 %75, label %for_loop_body5.lr.ph.split.us.us, label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us.loopexit:  ; preds = %for_loop_inc6.us.us66.1
  br label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us.loopexit156: ; preds = %for_loop_inc6.us.us.us.1
  br label %for_loop_test8.after_for7_crit_edge.us

for_loop_test8.after_for7_crit_edge.us:           ; preds = %for_loop_body5.us.us.us.prol.loopexit, %middle.block105, %for_loop_body5.us.us57.prol.loopexit, %middle.block, %for_loop_test8.after_for7_crit_edge.us.loopexit156, %for_loop_test8.after_for7_crit_edge.us.loopexit, %for_loop_body1.us
  %.us-phi.us = phi i1 [ %.01933.us, %for_loop_body1.us ], [ %rdx.select, %middle.block ], [ %rdx.select138, %middle.block105 ], [ %.1.us.us67.lcssa.unr, %for_loop_body5.us.us57.prol.loopexit ], [ %.1.us.us.us.lcssa.unr, %for_loop_body5.us.us.us.prol.loopexit ], [ %.1.us.us67.1, %for_loop_test8.after_for7_crit_edge.us.loopexit ], [ %.1.us.us.us.1, %for_loop_test8.after_for7_crit_edge.us.loopexit156 ]
  %77 = add nsw i32 %.01834.us, 1
  %exitcond82.not = icmp eq i32 %.01834.us, %.fr74
  br i1 %exitcond82.not, label %after_for3, label %for_loop_body1.us

for_loop_body5.lr.ph.split.us.us:                 ; preds = %for_loop_body1.us
  %78 = icmp eq i32 %.01834.us, 0
  br i1 %78, label %for_loop_body5.us.us57.preheader, label %for_loop_body5.us.us.us.preheader

for_loop_body5.us.us57.preheader:                 ; preds = %for_loop_body5.lr.ph.split.us.us
  br i1 %min.iters.check107, label %for_loop_body5.us.us57.preheader141, label %vector.scevcheck

vector.scevcheck:                                 ; preds = %for_loop_body5.us.us57.preheader
  %79 = add i32 %73, %76
  %80 = add i32 %79, %39
  %81 = icmp slt i32 %80, %79
  %82 = or i1 %81, %40
  br i1 %82, label %for_loop_body5.us.us57.preheader141, label %vector.ph

vector.ph:                                        ; preds = %vector.scevcheck
  %minmax.ident.splatinsert = insertelement <8 x i1> poison, i1 %.01933.us, i64 0
  %minmax.ident.splat = shufflevector <8 x i1> %minmax.ident.splatinsert, <8 x i1> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert93 = insertelement <8 x i32> poison, i32 %.fr, i64 0
  %broadcast.splat94 = shufflevector <8 x i32> %broadcast.splatinsert93, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %41, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv164 = phi i64 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next165, %vector.body ]
  %vec.ind = phi <8 x i64> [ %vec.ind.next.1, %vector.body ], [ %induction, %vector.body.preheader ]
  %vec.phi = phi <8 x i1> [ %predphi101.1, %vector.body ], [ %minmax.ident.splat, %vector.body.preheader ]
  %vec.ind89 = phi <8 x i32> [ %vec.ind.next90.1, %vector.body ], [ %induction121, %vector.body.preheader ]
  %83 = icmp ne <8 x i64> %vec.ind, zeroinitializer
  %84 = add <8 x i32> %broadcast.splat125, %vec.ind89
  %wide.masked.gather = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat92, i32 4, <8 x i1> %83, <8 x i32> undef)
  %85 = icmp slt <8 x i32> %broadcast.splat94, %wide.masked.gather
  %86 = icmp sgt <8 x i32> %84, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %87 = select <8 x i1> %85, <8 x i1> %86, <8 x i1> zeroinitializer
  %88 = select <8 x i1> %83, <8 x i1> %87, <8 x i1> zeroinitializer
  %wide.masked.gather97 = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat127, i32 4, <8 x i1> %88, <8 x i32> undef)
  %89 = icmp slt <8 x i32> %84, %wide.masked.gather97
  %90 = extractelement <8 x i32> %84, i64 0
  %91 = add i32 %90, %76
  %92 = sext i32 %91 to i64
  %93 = getelementptr i32, i32* %61, i64 %92
  %94 = select <8 x i1> %88, <8 x i1> %89, <8 x i1> zeroinitializer
  %95 = bitcast i32* %93 to <8 x i32>*
  %wide.masked.load = call <8 x i32> @llvm.masked.load.v8i32.p0v8i32(<8 x i32>* %95, i32 4, <8 x i1> %94, <8 x i32> poison)
  %96 = icmp sle <8 x i32> %wide.masked.load, %broadcast.splat131
  %97 = select <8 x i1> %96, <8 x i1> %vec.phi, <8 x i1> zeroinitializer
  %98 = xor <8 x i1> %87, <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>
  %99 = select <8 x i1> %83, <8 x i1> %98, <8 x i1> zeroinitializer
  %predphi100 = select <8 x i1> %94, <8 x i1> %97, <8 x i1> %vec.phi
  %predphi101 = select <8 x i1> %99, <8 x i1> %vec.phi, <8 x i1> %predphi100
  %vec.ind.next90 = add <8 x i32> %vec.ind89, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %100 = icmp ne <8 x i64> %vec.ind, <i64 -8, i64 -8, i64 -8, i64 -8, i64 -8, i64 -8, i64 -8, i64 -8>
  %101 = add <8 x i32> %broadcast.splat125, %vec.ind.next90
  %wide.masked.gather.1 = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat92, i32 4, <8 x i1> %100, <8 x i32> undef)
  %102 = icmp slt <8 x i32> %broadcast.splat94, %wide.masked.gather.1
  %103 = icmp sgt <8 x i32> %101, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %104 = select <8 x i1> %102, <8 x i1> %103, <8 x i1> zeroinitializer
  %105 = select <8 x i1> %100, <8 x i1> %104, <8 x i1> zeroinitializer
  %wide.masked.gather97.1 = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat127, i32 4, <8 x i1> %105, <8 x i32> undef)
  %106 = icmp slt <8 x i32> %101, %wide.masked.gather97.1
  %107 = extractelement <8 x i32> %101, i64 0
  %108 = add i32 %107, %76
  %109 = sext i32 %108 to i64
  %110 = getelementptr i32, i32* %61, i64 %109
  %111 = select <8 x i1> %105, <8 x i1> %106, <8 x i1> zeroinitializer
  %112 = bitcast i32* %110 to <8 x i32>*
  %wide.masked.load.1 = call <8 x i32> @llvm.masked.load.v8i32.p0v8i32(<8 x i32>* %112, i32 4, <8 x i1> %111, <8 x i32> poison)
  %113 = icmp sle <8 x i32> %wide.masked.load.1, %broadcast.splat131
  %114 = select <8 x i1> %113, <8 x i1> %predphi101, <8 x i1> zeroinitializer
  %115 = xor <8 x i1> %104, <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>
  %116 = select <8 x i1> %100, <8 x i1> %115, <8 x i1> zeroinitializer
  %predphi100.1 = select <8 x i1> %111, <8 x i1> %114, <8 x i1> %predphi101
  %predphi101.1 = select <8 x i1> %116, <8 x i1> %predphi101, <8 x i1> %predphi100.1
  %vec.ind.next.1 = add <8 x i64> %vec.ind, <i64 16, i64 16, i64 16, i64 16, i64 16, i64 16, i64 16, i64 16>
  %vec.ind.next90.1 = add <8 x i32> %vec.ind89, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %lsr.iv.next165 = add i64 %lsr.iv164, -2
  %niter151.ncmp.1 = icmp eq i64 %lsr.iv.next165, 0
  br i1 %niter151.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %predphi101.lcssa.ph = phi <8 x i1> [ undef, %vector.ph ], [ %predphi101.1, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i64> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x i1> [ %minmax.ident.splat, %vector.ph ], [ %predphi101.1, %middle.block.unr-lcssa.loopexit ]
  %vec.ind89.unr = phi <8 x i32> [ %induction121, %vector.ph ], [ %vec.ind.next90.1, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %117 = icmp ne <8 x i64> %vec.ind.unr, zeroinitializer
  %118 = add <8 x i32> %broadcast.splat125, %vec.ind89.unr
  %wide.masked.gather.epil = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat92, i32 4, <8 x i1> %117, <8 x i32> undef)
  %119 = icmp slt <8 x i32> %broadcast.splat94, %wide.masked.gather.epil
  %120 = icmp sgt <8 x i32> %118, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %121 = select <8 x i1> %119, <8 x i1> %120, <8 x i1> zeroinitializer
  %122 = select <8 x i1> %117, <8 x i1> %121, <8 x i1> zeroinitializer
  %wide.masked.gather97.epil = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat127, i32 4, <8 x i1> %122, <8 x i32> undef)
  %123 = icmp slt <8 x i32> %118, %wide.masked.gather97.epil
  %124 = extractelement <8 x i32> %118, i64 0
  %125 = add i32 %124, %76
  %126 = sext i32 %125 to i64
  %127 = getelementptr i32, i32* %61, i64 %126
  %128 = select <8 x i1> %122, <8 x i1> %123, <8 x i1> zeroinitializer
  %129 = bitcast i32* %127 to <8 x i32>*
  %wide.masked.load.epil = call <8 x i32> @llvm.masked.load.v8i32.p0v8i32(<8 x i32>* %129, i32 4, <8 x i1> %128, <8 x i32> poison)
  %130 = icmp sle <8 x i32> %wide.masked.load.epil, %broadcast.splat131
  %131 = select <8 x i1> %130, <8 x i1> %vec.phi.unr, <8 x i1> zeroinitializer
  %132 = xor <8 x i1> %121, <i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true, i1 true>
  %133 = select <8 x i1> %117, <8 x i1> %132, <8 x i1> zeroinitializer
  %predphi100.epil = select <8 x i1> %128, <8 x i1> %131, <8 x i1> %vec.phi.unr
  %predphi101.epil = select <8 x i1> %133, <8 x i1> %vec.phi.unr, <8 x i1> %predphi100.epil
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %predphi101.lcssa = phi <8 x i1> [ %predphi101.lcssa.ph, %middle.block.unr-lcssa ], [ %predphi101.epil, %vector.body.epil ]
  %rdx.select.cmp = xor <8 x i1> %predphi101.lcssa, %minmax.ident.splat
  %134 = bitcast <8 x i1> %rdx.select.cmp to i8
  %.not140 = icmp eq i8 %134, 0
  %rdx.select = select i1 %.not140, i1 %.01933.us, i1 false
  br i1 %cmp.n113, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us.us57.preheader141

for_loop_body5.us.us57.preheader141:              ; preds = %middle.block, %vector.scevcheck, %for_loop_body5.us.us57.preheader
  %indvars.iv78.ph = phi i64 [ %31, %vector.scevcheck ], [ %31, %for_loop_body5.us.us57.preheader ], [ %ind.end111, %middle.block ]
  %.231.us.us59.ph = phi i1 [ %.01933.us, %vector.scevcheck ], [ %.01933.us, %for_loop_body5.us.us57.preheader ], [ %rdx.select, %middle.block ]
  %135 = sub nsw i64 %wide.trip.count80, %indvars.iv78.ph
  %136 = xor i64 %indvars.iv78.ph, -1
  %xtraiter152 = and i64 %135, 1
  %lcmp.mod153.not = icmp eq i64 %xtraiter152, 0
  br i1 %lcmp.mod153.not, label %for_loop_body5.us.us57.prol.loopexit, label %for_loop_body5.us.us57.prol

for_loop_body5.us.us57.prol:                      ; preds = %for_loop_body5.us.us57.preheader141
  %137 = icmp eq i64 %indvars.iv78.ph, 0
  br i1 %137, label %for_loop_inc6.us.us66.prol, label %after_if14.us.us60.prol

after_if14.us.us60.prol:                          ; preds = %for_loop_body5.us.us57.prol
  %138 = trunc i64 %indvars.iv78.ph to i32
  %139 = add i32 %60, %138
  %140 = load i32, i32* %70, align 4
  %141 = icmp slt i32 %.fr, %140
  %142 = icmp sgt i32 %139, -1
  %or.cond.us.us62.prol = select i1 %141, i1 %142, i1 false
  br i1 %or.cond.us.us62.prol, label %true_block22.us.us63.prol, label %for_loop_inc6.us.us66.prol

true_block22.us.us63.prol:                        ; preds = %after_if14.us.us60.prol
  %143 = load i32, i32* %72, align 4
  %144 = icmp slt i32 %139, %143
  br i1 %144, label %true_block25.us.us64.prol, label %for_loop_inc6.us.us66.prol

true_block25.us.us64.prol:                        ; preds = %true_block22.us.us63.prol
  %145 = add i32 %139, %76
  %146 = sext i32 %145 to i64
  %147 = getelementptr i32, i32* %61, i64 %146
  %148 = load i32, i32* %147, align 4
  %149 = icmp sle i32 %148, %67
  %spec.select30.us.us65.prol = select i1 %149, i1 %.231.us.us59.ph, i1 false
  br label %for_loop_inc6.us.us66.prol

for_loop_inc6.us.us66.prol:                       ; preds = %true_block25.us.us64.prol, %true_block22.us.us63.prol, %after_if14.us.us60.prol, %for_loop_body5.us.us57.prol
  %.1.us.us67.prol = phi i1 [ %.231.us.us59.ph, %for_loop_body5.us.us57.prol ], [ %.231.us.us59.ph, %true_block22.us.us63.prol ], [ %spec.select30.us.us65.prol, %true_block25.us.us64.prol ], [ %.231.us.us59.ph, %after_if14.us.us60.prol ]
  %indvars.iv.next79.prol = add nsw i64 %indvars.iv78.ph, 1
  br label %for_loop_body5.us.us57.prol.loopexit

for_loop_body5.us.us57.prol.loopexit:             ; preds = %for_loop_inc6.us.us66.prol, %for_loop_body5.us.us57.preheader141
  %.1.us.us67.lcssa.unr = phi i1 [ undef, %for_loop_body5.us.us57.preheader141 ], [ %.1.us.us67.prol, %for_loop_inc6.us.us66.prol ]
  %indvars.iv78.unr = phi i64 [ %indvars.iv78.ph, %for_loop_body5.us.us57.preheader141 ], [ %indvars.iv.next79.prol, %for_loop_inc6.us.us66.prol ]
  %.231.us.us59.unr = phi i1 [ %.231.us.us59.ph, %for_loop_body5.us.us57.preheader141 ], [ %.1.us.us67.prol, %for_loop_inc6.us.us66.prol ]
  %150 = icmp eq i64 %136, %42
  br i1 %150, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us.us57.preheader154

for_loop_body5.us.us57.preheader154:              ; preds = %for_loop_body5.us.us57.prol.loopexit
  %151 = mul nsw i64 %indvars.iv78.unr, -1
  %152 = add i32 %60, %76
  %153 = trunc i64 %indvars.iv78.unr to i32
  %154 = add i32 %152, %153
  %155 = zext i32 %154 to i64
  %156 = add i32 %60, %153
  %157 = zext i32 %156 to i64
  br label %for_loop_body5.us.us57

for_loop_body5.us.us.us.preheader:                ; preds = %for_loop_body5.lr.ph.split.us.us
  %.pre = load i32, i32* %70, align 4
  %158 = icmp slt i32 %.fr, %.pre
  br i1 %min.iters.check107, label %for_loop_body5.us.us.us.preheader142, label %vector.scevcheck104

vector.scevcheck104:                              ; preds = %for_loop_body5.us.us.us.preheader
  %159 = add i32 %73, %76
  %160 = add i32 %159, %39
  %161 = icmp slt i32 %160, %159
  %162 = or i1 %161, %40
  br i1 %162, label %for_loop_body5.us.us.us.preheader142, label %vector.ph108

vector.ph108:                                     ; preds = %vector.scevcheck104
  %minmax.ident.splatinsert117 = insertelement <8 x i1> poison, i1 %.01933.us, i64 0
  %minmax.ident.splat118 = shufflevector <8 x i1> %minmax.ident.splatinsert117, <8 x i1> poison, <8 x i32> zeroinitializer
  br i1 %41, label %middle.block105.unr-lcssa, label %vector.body114.preheader

vector.body114.preheader:                         ; preds = %vector.ph108
  br label %vector.body114

vector.body114:                                   ; preds = %vector.body114, %vector.body114.preheader
  %lsr.iv = phi i64 [ %unroll_iter, %vector.body114.preheader ], [ %lsr.iv.next, %vector.body114 ]
  %vec.phi116 = phi <8 x i1> [ %predphi133.1, %vector.body114 ], [ %minmax.ident.splat118, %vector.body114.preheader ]
  %vec.ind122 = phi <8 x i32> [ %vec.ind.next123.1, %vector.body114 ], [ %induction121, %vector.body114.preheader ]
  %163 = add <8 x i32> %broadcast.splat125, %vec.ind122
  %164 = icmp sgt <8 x i32> %163, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %165 = select i1 %158, <8 x i1> %164, <8 x i1> zeroinitializer
  %wide.masked.gather128 = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat127, i32 4, <8 x i1> %165, <8 x i32> undef)
  %166 = icmp slt <8 x i32> %163, %wide.masked.gather128
  %167 = extractelement <8 x i32> %163, i64 0
  %168 = add i32 %167, %76
  %169 = sext i32 %168 to i64
  %170 = getelementptr i32, i32* %61, i64 %169
  %171 = select <8 x i1> %165, <8 x i1> %166, <8 x i1> zeroinitializer
  %172 = bitcast i32* %170 to <8 x i32>*
  %wide.masked.load129 = call <8 x i32> @llvm.masked.load.v8i32.p0v8i32(<8 x i32>* %172, i32 4, <8 x i1> %171, <8 x i32> poison)
  %173 = icmp sle <8 x i32> %wide.masked.load129, %broadcast.splat131
  %174 = select <8 x i1> %173, <8 x i1> %vec.phi116, <8 x i1> zeroinitializer
  %predphi133 = select <8 x i1> %171, <8 x i1> %174, <8 x i1> %vec.phi116
  %vec.ind.next123 = add <8 x i32> %vec.ind122, <i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8, i32 8>
  %175 = add <8 x i32> %broadcast.splat125, %vec.ind.next123
  %176 = icmp sgt <8 x i32> %175, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %177 = select i1 %158, <8 x i1> %176, <8 x i1> zeroinitializer
  %wide.masked.gather128.1 = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat127, i32 4, <8 x i1> %177, <8 x i32> undef)
  %178 = icmp slt <8 x i32> %175, %wide.masked.gather128.1
  %179 = extractelement <8 x i32> %175, i64 0
  %180 = add i32 %179, %76
  %181 = sext i32 %180 to i64
  %182 = getelementptr i32, i32* %61, i64 %181
  %183 = select <8 x i1> %177, <8 x i1> %178, <8 x i1> zeroinitializer
  %184 = bitcast i32* %182 to <8 x i32>*
  %wide.masked.load129.1 = call <8 x i32> @llvm.masked.load.v8i32.p0v8i32(<8 x i32>* %184, i32 4, <8 x i1> %183, <8 x i32> poison)
  %185 = icmp sle <8 x i32> %wide.masked.load129.1, %broadcast.splat131
  %186 = select <8 x i1> %185, <8 x i1> %predphi133, <8 x i1> zeroinitializer
  %predphi133.1 = select <8 x i1> %183, <8 x i1> %186, <8 x i1> %predphi133
  %vec.ind.next123.1 = add <8 x i32> %vec.ind122, <i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16, i32 16>
  %lsr.iv.next = add i64 %lsr.iv, -2
  %niter.ncmp.1 = icmp eq i64 %lsr.iv.next, 0
  br i1 %niter.ncmp.1, label %middle.block105.unr-lcssa.loopexit, label %vector.body114, !llvm.loop !11

middle.block105.unr-lcssa.loopexit:               ; preds = %vector.body114
  br label %middle.block105.unr-lcssa

middle.block105.unr-lcssa:                        ; preds = %middle.block105.unr-lcssa.loopexit, %vector.ph108
  %predphi133.lcssa.ph = phi <8 x i1> [ undef, %vector.ph108 ], [ %predphi133.1, %middle.block105.unr-lcssa.loopexit ]
  %vec.phi116.unr = phi <8 x i1> [ %minmax.ident.splat118, %vector.ph108 ], [ %predphi133.1, %middle.block105.unr-lcssa.loopexit ]
  %vec.ind122.unr = phi <8 x i32> [ %induction121, %vector.ph108 ], [ %vec.ind.next123.1, %middle.block105.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block105, label %vector.body114.epil

vector.body114.epil:                              ; preds = %middle.block105.unr-lcssa
  %187 = add <8 x i32> %broadcast.splat125, %vec.ind122.unr
  %188 = icmp sgt <8 x i32> %187, <i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1, i32 -1>
  %189 = select i1 %158, <8 x i1> %188, <8 x i1> zeroinitializer
  %wide.masked.gather128.epil = call <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*> %broadcast.splat127, i32 4, <8 x i1> %189, <8 x i32> undef)
  %190 = icmp slt <8 x i32> %187, %wide.masked.gather128.epil
  %191 = extractelement <8 x i32> %187, i64 0
  %192 = add i32 %191, %76
  %193 = sext i32 %192 to i64
  %194 = getelementptr i32, i32* %61, i64 %193
  %195 = select <8 x i1> %189, <8 x i1> %190, <8 x i1> zeroinitializer
  %196 = bitcast i32* %194 to <8 x i32>*
  %wide.masked.load129.epil = call <8 x i32> @llvm.masked.load.v8i32.p0v8i32(<8 x i32>* %196, i32 4, <8 x i1> %195, <8 x i32> poison)
  %197 = icmp sle <8 x i32> %wide.masked.load129.epil, %broadcast.splat131
  %198 = select <8 x i1> %197, <8 x i1> %vec.phi116.unr, <8 x i1> zeroinitializer
  %predphi133.epil = select <8 x i1> %195, <8 x i1> %198, <8 x i1> %vec.phi116.unr
  br label %middle.block105

middle.block105:                                  ; preds = %vector.body114.epil, %middle.block105.unr-lcssa
  %predphi133.lcssa = phi <8 x i1> [ %predphi133.lcssa.ph, %middle.block105.unr-lcssa ], [ %predphi133.epil, %vector.body114.epil ]
  %rdx.select.cmp137 = xor <8 x i1> %predphi133.lcssa, %minmax.ident.splat118
  %199 = bitcast <8 x i1> %rdx.select.cmp137 to i8
  %.not = icmp eq i8 %199, 0
  %rdx.select138 = select i1 %.not, i1 %.01933.us, i1 false
  br i1 %cmp.n113, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us.us.us.preheader142

for_loop_body5.us.us.us.preheader142:             ; preds = %middle.block105, %vector.scevcheck104, %for_loop_body5.us.us.us.preheader
  %indvars.iv.ph = phi i64 [ %31, %vector.scevcheck104 ], [ %31, %for_loop_body5.us.us.us.preheader ], [ %ind.end111, %middle.block105 ]
  %.231.us.us.us.ph = phi i1 [ %.01933.us, %vector.scevcheck104 ], [ %.01933.us, %for_loop_body5.us.us.us.preheader ], [ %rdx.select138, %middle.block105 ]
  %200 = sub nsw i64 %wide.trip.count80, %indvars.iv.ph
  %201 = xor i64 %indvars.iv.ph, -1
  %xtraiter145 = and i64 %200, 1
  %lcmp.mod146.not = icmp eq i64 %xtraiter145, 0
  br i1 %lcmp.mod146.not, label %for_loop_body5.us.us.us.prol.loopexit, label %for_loop_body5.us.us.us.prol

for_loop_body5.us.us.us.prol:                     ; preds = %for_loop_body5.us.us.us.preheader142
  %202 = trunc i64 %indvars.iv.ph to i32
  %203 = add i32 %60, %202
  %204 = icmp sgt i32 %203, -1
  %or.cond.us.us.us.prol = select i1 %158, i1 %204, i1 false
  br i1 %or.cond.us.us.us.prol, label %true_block22.us.us.us.prol, label %for_loop_inc6.us.us.us.prol

true_block22.us.us.us.prol:                       ; preds = %for_loop_body5.us.us.us.prol
  %205 = load i32, i32* %72, align 4
  %206 = icmp slt i32 %203, %205
  br i1 %206, label %true_block25.us.us.us.prol, label %for_loop_inc6.us.us.us.prol

true_block25.us.us.us.prol:                       ; preds = %true_block22.us.us.us.prol
  %207 = add i32 %203, %76
  %208 = sext i32 %207 to i64
  %209 = getelementptr i32, i32* %61, i64 %208
  %210 = load i32, i32* %209, align 4
  %211 = icmp sle i32 %210, %67
  %spec.select30.us.us.us.prol = select i1 %211, i1 %.231.us.us.us.ph, i1 false
  br label %for_loop_inc6.us.us.us.prol

for_loop_inc6.us.us.us.prol:                      ; preds = %true_block25.us.us.us.prol, %true_block22.us.us.us.prol, %for_loop_body5.us.us.us.prol
  %.1.us.us.us.prol = phi i1 [ %.231.us.us.us.ph, %true_block22.us.us.us.prol ], [ %spec.select30.us.us.us.prol, %true_block25.us.us.us.prol ], [ %.231.us.us.us.ph, %for_loop_body5.us.us.us.prol ]
  %indvars.iv.next.prol = add nsw i64 %indvars.iv.ph, 1
  br label %for_loop_body5.us.us.us.prol.loopexit

for_loop_body5.us.us.us.prol.loopexit:            ; preds = %for_loop_inc6.us.us.us.prol, %for_loop_body5.us.us.us.preheader142
  %.1.us.us.us.lcssa.unr = phi i1 [ undef, %for_loop_body5.us.us.us.preheader142 ], [ %.1.us.us.us.prol, %for_loop_inc6.us.us.us.prol ]
  %indvars.iv.unr = phi i64 [ %indvars.iv.ph, %for_loop_body5.us.us.us.preheader142 ], [ %indvars.iv.next.prol, %for_loop_inc6.us.us.us.prol ]
  %.231.us.us.us.unr = phi i1 [ %.231.us.us.us.ph, %for_loop_body5.us.us.us.preheader142 ], [ %.1.us.us.us.prol, %for_loop_inc6.us.us.us.prol ]
  %212 = icmp eq i64 %201, %42
  br i1 %212, label %for_loop_test8.after_for7_crit_edge.us, label %for_loop_body5.us.us.us.preheader155

for_loop_body5.us.us.us.preheader155:             ; preds = %for_loop_body5.us.us.us.prol.loopexit
  %213 = add i32 %60, %76
  %214 = trunc i64 %indvars.iv.unr to i32
  %215 = add i32 %213, %214
  %216 = zext i32 %215 to i64
  %217 = add i32 %60, %214
  %218 = zext i32 %217 to i64
  %219 = sub i64 %wide.trip.count80, %indvars.iv.unr
  br label %for_loop_body5.us.us.us

for_loop_body5.us.us57:                           ; preds = %for_loop_inc6.us.us66.1, %for_loop_body5.us.us57.preheader154
  %lsr.iv166 = phi i64 [ 0, %for_loop_body5.us.us57.preheader154 ], [ %lsr.iv.next167, %for_loop_inc6.us.us66.1 ]
  %indvars.iv78 = phi i64 [ %indvars.iv.next79.1, %for_loop_inc6.us.us66.1 ], [ %indvars.iv78.unr, %for_loop_body5.us.us57.preheader154 ]
  %.231.us.us59 = phi i1 [ %.1.us.us67.1, %for_loop_inc6.us.us66.1 ], [ %.231.us.us59.unr, %for_loop_body5.us.us57.preheader154 ]
  %220 = icmp eq i64 %151, %lsr.iv166
  br i1 %220, label %for_loop_inc6.us.us66, label %after_if14.us.us60

after_if14.us.us60:                               ; preds = %for_loop_body5.us.us57
  %221 = add i64 %157, %lsr.iv166
  %222 = load i32, i32* %70, align 4
  %223 = icmp slt i32 %.fr, %222
  %tmp170 = trunc i64 %221 to i32
  %224 = icmp sgt i32 %tmp170, -1
  %or.cond.us.us62 = select i1 %223, i1 %224, i1 false
  br i1 %or.cond.us.us62, label %true_block22.us.us63, label %for_loop_inc6.us.us66

true_block22.us.us63:                             ; preds = %after_if14.us.us60
  %225 = load i32, i32* %72, align 4
  %226 = icmp slt i32 %tmp170, %225
  br i1 %226, label %true_block25.us.us64, label %for_loop_inc6.us.us66

true_block25.us.us64:                             ; preds = %true_block22.us.us63
  %227 = add i64 %155, %lsr.iv166
  %tmp168 = trunc i64 %227 to i32
  %228 = sext i32 %tmp168 to i64
  %229 = getelementptr i32, i32* %61, i64 %228
  %230 = load i32, i32* %229, align 4
  %231 = icmp sle i32 %230, %67
  %spec.select30.us.us65 = select i1 %231, i1 %.231.us.us59, i1 false
  br label %for_loop_inc6.us.us66

for_loop_inc6.us.us66:                            ; preds = %true_block25.us.us64, %true_block22.us.us63, %after_if14.us.us60, %for_loop_body5.us.us57
  %.1.us.us67 = phi i1 [ %.231.us.us59, %for_loop_body5.us.us57 ], [ %.231.us.us59, %true_block22.us.us63 ], [ %spec.select30.us.us65, %true_block25.us.us64 ], [ %.231.us.us59, %after_if14.us.us60 ]
  %indvars.iv.next79 = add nsw i64 %indvars.iv78, 1
  %232 = icmp eq i64 %indvars.iv.next79, 0
  br i1 %232, label %for_loop_inc6.us.us66.1, label %after_if14.us.us60.1

after_if14.us.us60.1:                             ; preds = %for_loop_inc6.us.us66
  %233 = add i64 %157, %lsr.iv166
  %234 = add i64 %233, 1
  %235 = load i32, i32* %70, align 4
  %236 = icmp slt i32 %.fr, %235
  %tmp173 = trunc i64 %234 to i32
  %237 = icmp sgt i32 %tmp173, -1
  %or.cond.us.us62.1 = select i1 %236, i1 %237, i1 false
  br i1 %or.cond.us.us62.1, label %true_block22.us.us63.1, label %for_loop_inc6.us.us66.1

true_block22.us.us63.1:                           ; preds = %after_if14.us.us60.1
  %238 = load i32, i32* %72, align 4
  %239 = icmp slt i32 %tmp173, %238
  br i1 %239, label %true_block25.us.us64.1, label %for_loop_inc6.us.us66.1

true_block25.us.us64.1:                           ; preds = %true_block22.us.us63.1
  %240 = add i64 %155, %lsr.iv166
  %241 = add i64 %240, 1
  %tmp171 = trunc i64 %241 to i32
  %242 = sext i32 %tmp171 to i64
  %243 = getelementptr i32, i32* %61, i64 %242
  %244 = load i32, i32* %243, align 4
  %245 = icmp sle i32 %244, %67
  %spec.select30.us.us65.1 = select i1 %245, i1 %.1.us.us67, i1 false
  br label %for_loop_inc6.us.us66.1

for_loop_inc6.us.us66.1:                          ; preds = %true_block25.us.us64.1, %true_block22.us.us63.1, %after_if14.us.us60.1, %for_loop_inc6.us.us66
  %.1.us.us67.1 = phi i1 [ %.1.us.us67, %for_loop_inc6.us.us66 ], [ %.1.us.us67, %true_block22.us.us63.1 ], [ %spec.select30.us.us65.1, %true_block25.us.us64.1 ], [ %.1.us.us67, %after_if14.us.us60.1 ]
  %indvars.iv.next79.1 = add nsw i64 %indvars.iv78, 2
  %lsr.iv.next167 = add i64 %lsr.iv166, 2
  %exitcond81.not.1 = icmp eq i64 %indvars.iv.next79.1, %wide.trip.count80
  br i1 %exitcond81.not.1, label %for_loop_test8.after_for7_crit_edge.us.loopexit, label %for_loop_body5.us.us57, !llvm.loop !12

for_loop_body5.us.us.us:                          ; preds = %for_loop_inc6.us.us.us.1, %for_loop_body5.us.us.us.preheader155
  %lsr.iv157 = phi i64 [ 0, %for_loop_body5.us.us.us.preheader155 ], [ %lsr.iv.next158, %for_loop_inc6.us.us.us.1 ]
  %.231.us.us.us = phi i1 [ %.1.us.us.us.1, %for_loop_inc6.us.us.us.1 ], [ %.231.us.us.us.unr, %for_loop_body5.us.us.us.preheader155 ]
  %246 = add i64 %218, %lsr.iv157
  %tmp163 = trunc i64 %246 to i32
  %247 = icmp sgt i32 %tmp163, -1
  %or.cond.us.us.us = select i1 %158, i1 %247, i1 false
  br i1 %or.cond.us.us.us, label %true_block22.us.us.us, label %for_loop_inc6.us.us.us

true_block22.us.us.us:                            ; preds = %for_loop_body5.us.us.us
  %248 = load i32, i32* %72, align 4
  %249 = icmp slt i32 %tmp163, %248
  br i1 %249, label %true_block25.us.us.us, label %for_loop_inc6.us.us.us

true_block25.us.us.us:                            ; preds = %true_block22.us.us.us
  %250 = add i64 %216, %lsr.iv157
  %tmp161 = trunc i64 %250 to i32
  %251 = sext i32 %tmp161 to i64
  %252 = getelementptr i32, i32* %61, i64 %251
  %253 = load i32, i32* %252, align 4
  %254 = icmp sle i32 %253, %67
  %spec.select30.us.us.us = select i1 %254, i1 %.231.us.us.us, i1 false
  br label %for_loop_inc6.us.us.us

for_loop_inc6.us.us.us:                           ; preds = %true_block25.us.us.us, %true_block22.us.us.us, %for_loop_body5.us.us.us
  %.1.us.us.us = phi i1 [ %.231.us.us.us, %true_block22.us.us.us ], [ %spec.select30.us.us.us, %true_block25.us.us.us ], [ %.231.us.us.us, %for_loop_body5.us.us.us ]
  %255 = add i64 %246, 1
  %tmp160 = trunc i64 %255 to i32
  %256 = icmp sgt i32 %tmp160, -1
  %or.cond.us.us.us.1 = select i1 %158, i1 %256, i1 false
  br i1 %or.cond.us.us.us.1, label %true_block22.us.us.us.1, label %for_loop_inc6.us.us.us.1

true_block22.us.us.us.1:                          ; preds = %for_loop_inc6.us.us.us
  %257 = load i32, i32* %72, align 4
  %258 = icmp slt i32 %tmp160, %257
  br i1 %258, label %true_block25.us.us.us.1, label %for_loop_inc6.us.us.us.1

true_block25.us.us.us.1:                          ; preds = %true_block22.us.us.us.1
  %259 = add i64 %216, %lsr.iv157
  %260 = add i64 %259, 1
  %tmp = trunc i64 %260 to i32
  %261 = sext i32 %tmp to i64
  %262 = getelementptr i32, i32* %61, i64 %261
  %263 = load i32, i32* %262, align 4
  %264 = icmp sle i32 %263, %67
  %spec.select30.us.us.us.1 = select i1 %264, i1 %.1.us.us.us, i1 false
  br label %for_loop_inc6.us.us.us.1

for_loop_inc6.us.us.us.1:                         ; preds = %true_block25.us.us.us.1, %true_block22.us.us.us.1, %for_loop_inc6.us.us.us
  %.1.us.us.us.1 = phi i1 [ %.1.us.us.us, %true_block22.us.us.us.1 ], [ %spec.select30.us.us.us.1, %true_block25.us.us.us.1 ], [ %.1.us.us.us, %for_loop_inc6.us.us.us ]
  %lsr.iv.next158 = add i64 %lsr.iv157, 2
  %exitcond.not.1 = icmp eq i64 %219, %lsr.iv.next158
  br i1 %exitcond.not.1, label %for_loop_test8.after_for7_crit_edge.us.loopexit156, label %for_loop_body5.us.us.us, !llvm.loop !13

for_loop_inc:                                     ; preds = %true_block34, %true_block31, %after_for3, %for_loop_body
  %265 = add nsw i32 %.02036, 1
  %indvar.next = add i32 %indvar, 1
  %exitcond83.not = icmp eq i32 %265, %19
  br i1 %exitcond83.not, label %after_for.loopexit, label %for_loop_body

after_for.loopexit:                               ; preds = %for_loop_inc
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3:                                       ; preds = %for_loop_test8.after_for7_crit_edge.us
  br i1 %.us-phi.us, label %true_block31, label %for_loop_inc

true_block31:                                     ; preds = %after_for3, %for_loop_test4.preheader
  %266 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }** %20, align 8
  %267 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %266, i64 0, i32 2, i32 1
  %268 = load i32*, i32** %267, align 8
  %269 = atomicrmw add i32* %268, i32 1 seq_cst, align 4
  %270 = load { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }*, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }** %20, align 8
  %271 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %270, i64 0, i32 7
  %272 = load i32, i32* %271, align 4
  %273 = icmp slt i32 %269, %272
  br i1 %273, label %true_block34, label %for_loop_inc

true_block34:                                     ; preds = %true_block31
  %274 = sitofp i32 %58 to float
  %275 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %270, i64 0, i32 1, i32 1
  %276 = load float*, float** %275, align 8
  %277 = getelementptr { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }, { { { i32, i32 }, i32* }, { { i32, i32 }, float* }, { { i32 }, i32* }, i32, i32, i32, i32, i32 }* %270, i64 0, i32 1, i32 0, i32 1
  %278 = load i32, i32* %277, align 4
  %279 = mul i32 %278, %269
  %280 = sext i32 %279 to i64
  %281 = getelementptr float, float* %276, i64 %280
  store float %274, float* %281, align 4
  %282 = sitofp i32 %60 to float
  %283 = load float*, float** %275, align 8
  %284 = load i32, i32* %277, align 4
  %285 = mul i32 %284, %269
  %286 = add i32 %285, 1
  %287 = sext i32 %286 to i64
  %288 = getelementptr float, float* %283, i64 %287
  store float %282, float* %288, align 4
  %289 = load i32, i32* %66, align 4
  %290 = sitofp i32 %289 to float
  %291 = load float*, float** %275, align 8
  %292 = load i32, i32* %277, align 4
  %293 = mul i32 %292, %269
  %294 = add i32 %293, 2
  %295 = sext i32 %294 to i64
  %296 = getelementptr float, float* %291, i64 %295
  store float %290, float* %296, align 4
  br label %for_loop_inc
}

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(i8* nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
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
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !14

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
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !16

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
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.start.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: argmemonly nocallback nofree nosync nounwind willreturn
declare void @llvm.lifetime.end.p0i8(i64 immarg, i8* nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind readonly willreturn
declare <8 x i32> @llvm.masked.gather.v8i32.v8p0i32(<8 x i32*>, i32 immarg, <8 x i1>, <8 x i32>) #7

; Function Attrs: argmemonly nocallback nofree nosync nounwind readonly willreturn
declare <8 x i32> @llvm.masked.load.v8i32.p0v8i32(<8 x i32>*, i32 immarg, <8 x i1>, <8 x i32>) #8

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nounwind }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { argmemonly mustprogress nocallback nofree nounwind willreturn }
attributes #5 = { mustprogress nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #6 = { argmemonly nocallback nofree nosync nounwind willreturn }
attributes #7 = { nocallback nofree nosync nounwind readonly willreturn }
attributes #8 = { argmemonly nocallback nofree nosync nounwind readonly willreturn }

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
!10 = !{!"llvm.loop.isvectorized", i32 1}
!11 = distinct !{!11, !10}
!12 = distinct !{!12, !10}
!13 = distinct !{!13, !10}
!14 = distinct !{!14, !15}
!15 = !{!"llvm.loop.mustprogress"}
!16 = distinct !{!16, !15}
