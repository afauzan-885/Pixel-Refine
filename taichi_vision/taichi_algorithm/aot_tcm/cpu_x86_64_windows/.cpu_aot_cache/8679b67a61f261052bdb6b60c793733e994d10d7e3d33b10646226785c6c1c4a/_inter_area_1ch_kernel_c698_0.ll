; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%struct.RuntimeContext.6 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.5 = type { %struct.PreallocatedMemoryChunk.1, %struct.PreallocatedMemoryChunk.1, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.1 = type { ptr, ptr, i64 }
%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_inter_area_1ch_kernel_c678_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %1, i64 0, i32 3
  %3 = load i32, ptr %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.6, ptr %context, i64 0, i32 1
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %5, i64 0, i32 14
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds i8, ptr %7, i64 24
  %9 = bitcast ptr %8 to ptr
  store i32 %3, ptr %9, align 4
  %10 = sitofp i32 %3 to float
  %11 = load ptr, ptr %0, align 8
  %12 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %11, i64 0, i32 5
  %13 = load i32, ptr %12, align 4
  %14 = sitofp i32 %13 to float
  %15 = fdiv reassoc ninf nsz float %10, %14
  %16 = load ptr, ptr %4, align 8
  %17 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %16, i64 0, i32 14
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds i8, ptr %18, i64 12
  %20 = bitcast ptr %19 to ptr
  store float %15, ptr %20, align 4
  %21 = load ptr, ptr %0, align 8
  %22 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %21, i64 0, i32 2
  %23 = load i32, ptr %22, align 4
  %24 = load ptr, ptr %4, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %24, i64 0, i32 14
  %26 = load ptr, ptr %25, align 8
  %27 = getelementptr inbounds i8, ptr %26, i64 20
  %28 = bitcast ptr %27 to ptr
  store i32 %23, ptr %28, align 4
  %29 = sitofp i32 %23 to float
  %30 = load ptr, ptr %0, align 8
  %31 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %30, i64 0, i32 4
  %32 = load i32, ptr %31, align 4
  %33 = sitofp i32 %32 to float
  %34 = fdiv reassoc ninf nsz float %29, %33
  %35 = load ptr, ptr %4, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %35, i64 0, i32 14
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds i8, ptr %37, i64 16
  %39 = bitcast ptr %38 to ptr
  store float %34, ptr %39, align 4
  %40 = load ptr, ptr %0, align 8
  %41 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %40, i64 0, i32 1, i32 0, i32 0
  %42 = load i32, ptr %41, align 4
  %43 = load ptr, ptr %4, align 8
  %44 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %43, i64 0, i32 14
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds i8, ptr %45, i64 8
  %47 = bitcast ptr %46 to ptr
  store i32 %42, ptr %47, align 4
  %48 = load ptr, ptr %0, align 8
  %49 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %48, i64 0, i32 1, i32 0, i32 1
  %50 = load i32, ptr %49, align 4
  %51 = load ptr, ptr %4, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %51, i64 0, i32 14
  %53 = load ptr, ptr %52, align 8
  %54 = getelementptr inbounds i8, ptr %53, i64 4
  %55 = bitcast ptr %54 to ptr
  store i32 %50, ptr %55, align 4
  %56 = mul i32 %50, %42
  %57 = load ptr, ptr %4, align 8
  %58 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %57, i64 0, i32 14
  %59 = bitcast ptr %58 to ptr
  %60 = load ptr, ptr %59, align 8
  store i32 %56, ptr %60, align 4
  ret void
}

; Function Attrs: nounwind
define void @_inter_area_1ch_kernel_c678_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %struct.range_task_helper_context, align 8
  %1 = bitcast ptr %0 to ptr
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %1)
  %2 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 1
  %3 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 4
  %4 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 0
  store ptr %context, ptr %4, align 8
  store ptr null, ptr %2, align 8
  store i64 1, ptr %3, align 8
  %5 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 2
  store ptr @function_body, ptr %5, align 8
  %6 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 3
  store ptr null, ptr %6, align 8
  %7 = getelementptr inbounds %struct.range_task_helper_context, ptr %0, i64 0, i32 5
  %8 = bitcast ptr %7 to ptr
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, ptr %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext.6, ptr %context, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %10, i64 0, i32 10
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %10, i64 0, i32 9
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.6, ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %4, i64 0, i32 14
  %6 = bitcast ptr %5 to ptr
  %7 = load ptr, ptr %6, align 8
  %8 = load i32, ptr %7, align 4
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
  %21 = bitcast ptr %0 to ptr
  %22 = load ptr, ptr %21, align 8
  %23 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %22, i64 0, i32 0, i32 1
  %24 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %22, i64 0, i32 0, i32 0, i32 1
  %25 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %22, i64 0, i32 1, i32 1
  %26 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %22, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.01727 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %165, %after_for3 ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime.5, ptr %27, i64 0, i32 14
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds i8, ptr %29, i64 4
  %31 = bitcast ptr %30 to ptr
  %32 = load i32, ptr %31, align 4
  %33 = srem i32 %.01727, %32
  %34 = sdiv i32 %.01727, %32
  %35 = getelementptr inbounds i8, ptr %29, i64 8
  %36 = bitcast ptr %35 to ptr
  %37 = load i32, ptr %36, align 4
  %38 = srem i32 %34, %37
  %39 = sitofp i32 %33 to float
  %40 = getelementptr inbounds i8, ptr %29, i64 12
  %41 = bitcast ptr %40 to ptr
  %42 = load float, ptr %41, align 4
  %43 = fmul reassoc ninf nsz float %42, %39
  %44 = add nsw i32 %33, 1
  %45 = sitofp i32 %44 to float
  %46 = fmul reassoc ninf nsz float %42, %45
  %47 = sitofp i32 %38 to float
  %48 = getelementptr inbounds i8, ptr %29, i64 16
  %49 = bitcast ptr %48 to ptr
  %50 = load float, ptr %49, align 4
  %51 = fmul reassoc ninf nsz float %50, %47
  %52 = add i32 %38, 1
  %53 = sitofp i32 %52 to float
  %54 = fmul reassoc ninf nsz float %50, %53
  %55 = tail call reassoc ninf nsz float @llvm.floor.f32(float %51)
  %56 = fptosi float %55 to i32
  %57 = tail call reassoc ninf nsz float @llvm.ceil.f32(float %54)
  %58 = fptosi float %57 to i32
  %59 = tail call reassoc ninf nsz float @llvm.floor.f32(float %43)
  %60 = fptosi float %59 to i32
  %61 = tail call reassoc ninf nsz float @llvm.ceil.f32(float %46)
  %62 = fptosi float %61 to i32
  %63 = getelementptr inbounds i8, ptr %29, i64 20
  %64 = bitcast ptr %63 to ptr
  %65 = load i32, ptr %64, align 4
  %66 = add i32 %65, -1
  %67 = getelementptr inbounds i8, ptr %29, i64 24
  %68 = bitcast ptr %67 to ptr
  %69 = load i32, ptr %68, align 4
  %70 = add i32 %69, -1
  %71 = icmp slt i32 %56, %58
  %72 = icmp sgt i32 %62, %60
  %or.cond = select i1 %71, i1 %72, i1 false
  br i1 %or.cond, label %for_loop_body1.us.preheader, label %after_for3

for_loop_body1.us.preheader:                      ; preds = %for_loop_body
  %.pre = load ptr, ptr %23, align 8
  %.pre33 = load i32, ptr %24, align 4
  %73 = sub i32 %62, %60
  %74 = add i32 %73, -8
  %75 = lshr i32 %74, 3
  %76 = add nuw nsw i32 %75, 1
  %min.iters.check = icmp ult i32 %73, 8
  %n.vec = and i32 %73, -8
  %ind.end = add i32 %n.vec, %60
  %.splatinsert = insertelement <8 x i32> poison, i32 %60, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %70, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert37 = insertelement <8 x float> poison, float %46, i64 0
  %broadcast.splat38 = shufflevector <8 x float> %broadcast.splatinsert37, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert39 = insertelement <8 x float> poison, float %43, i64 0
  %broadcast.splat40 = shufflevector <8 x float> %broadcast.splatinsert39, <8 x float> poison, <8 x i32> zeroinitializer
  %xtraiter = and i32 %76, 1
  %77 = icmp ult i32 %74, 8
  %unroll_iter = and i32 %76, 1073741822
  %lcmp.mod.not = icmp eq i32 %xtraiter, 0
  %cmp.n = icmp eq i32 %73, %n.vec
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, %for_loop_body1.us.preheader
  %.01324.us = phi i32 [ %79, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ %56, %for_loop_body1.us.preheader ]
  %.01423.us = phi float [ %.lcssa, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.01522.us = phi float [ %.lcssa35, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %78 = tail call i32 @llvm.smax.i32(i32 %.01324.us, i32 0)
  %79 = add nsw i32 %.01324.us, 1
  %80 = sitofp i32 %.01324.us to float
  %81 = sitofp i32 %79 to float
  %82 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %80, float %51)
  %83 = tail call i32 @llvm.smin.i32(i32 %66, i32 %78)
  %84 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %81, float %54)
  %85 = fsub reassoc ninf nsz float %84, %82
  %86 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %85, float 0.000000e+00)
  %87 = mul i32 %.pre33, %83
  br i1 %min.iters.check, label %for_loop_body5.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body1.us
  %88 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01423.us, i64 0
  %89 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01522.us, i64 0
  %broadcast.splatinsert41 = insertelement <8 x float> poison, float %86, i64 0
  %broadcast.splat42 = shufflevector <8 x float> %broadcast.splatinsert41, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert43 = insertelement <8 x i32> poison, i32 %87, i64 0
  %broadcast.splat44 = shufflevector <8 x i32> %broadcast.splatinsert43, <8 x i32> poison, <8 x i32> zeroinitializer
  br i1 %77, label %middle.block.unr-lcssa, label %vector.body.preheader

vector.body.preheader:                            ; preds = %vector.ph
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.body.preheader
  %lsr.iv = phi i32 [ %unroll_iter, %vector.body.preheader ], [ %lsr.iv.next, %vector.body ]
  %vec.ind = phi <8 x i32> [ %vec.ind.next.1, %vector.body ], [ %induction, %vector.body.preheader ]
  %vec.phi = phi <8 x float> [ %121, %vector.body ], [ %88, %vector.body.preheader ]
  %vec.phi36 = phi <8 x float> [ %120, %vector.body ], [ %89, %vector.body.preheader ]
  %90 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind, <8 x i32> zeroinitializer)
  %91 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat, <8 x i32> %90)
  %92 = add nsw <8 x i32> %vec.ind, splat (i32 1)
  %93 = sitofp <8 x i32> %92 to <8 x float>
  %94 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %93, <8 x float> %broadcast.splat38)
  %95 = sitofp <8 x i32> %vec.ind to <8 x float>
  %96 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %95, <8 x float> %broadcast.splat40)
  %97 = fsub reassoc ninf nsz <8 x float> %94, %96
  %98 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %97, <8 x float> zeroinitializer)
  %99 = fmul reassoc ninf nsz <8 x float> %98, %broadcast.splat42
  %100 = add <8 x i32> %broadcast.splat44, %91
  %101 = sext <8 x i32> %100 to <8 x i64>
  %102 = getelementptr float, ptr %.pre, <8 x i64> %101
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %102, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %103 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather, %99
  %104 = fadd reassoc ninf nsz <8 x float> %103, %vec.phi36
  %105 = fadd reassoc ninf nsz <8 x float> %99, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %106 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind.next, <8 x i32> zeroinitializer)
  %107 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat, <8 x i32> %106)
  %108 = add <8 x i32> %vec.ind, splat (i32 9)
  %109 = sitofp <8 x i32> %108 to <8 x float>
  %110 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %109, <8 x float> %broadcast.splat38)
  %111 = sitofp <8 x i32> %vec.ind.next to <8 x float>
  %112 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %111, <8 x float> %broadcast.splat40)
  %113 = fsub reassoc ninf nsz <8 x float> %110, %112
  %114 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %113, <8 x float> zeroinitializer)
  %115 = fmul reassoc ninf nsz <8 x float> %114, %broadcast.splat42
  %116 = add <8 x i32> %broadcast.splat44, %107
  %117 = sext <8 x i32> %116 to <8 x i64>
  %118 = getelementptr float, ptr %.pre, <8 x i64> %117
  %wide.masked.gather.1 = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %118, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %119 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather.1, %115
  %120 = fadd reassoc ninf nsz <8 x float> %119, %104
  %121 = fadd reassoc ninf nsz <8 x float> %115, %105
  %vec.ind.next.1 = add <8 x i32> %vec.ind, splat (i32 16)
  %lsr.iv.next = add i32 %lsr.iv, -2
  %niter.ncmp.1 = icmp eq i32 %lsr.iv.next, 0
  br i1 %niter.ncmp.1, label %middle.block.unr-lcssa.loopexit, label %vector.body, !llvm.loop !9

middle.block.unr-lcssa.loopexit:                  ; preds = %vector.body
  br label %middle.block.unr-lcssa

middle.block.unr-lcssa:                           ; preds = %middle.block.unr-lcssa.loopexit, %vector.ph
  %.lcssa47.ph = phi <8 x float> [ undef, %vector.ph ], [ %120, %middle.block.unr-lcssa.loopexit ]
  %.lcssa46.ph = phi <8 x float> [ undef, %vector.ph ], [ %121, %middle.block.unr-lcssa.loopexit ]
  %vec.ind.unr = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next.1, %middle.block.unr-lcssa.loopexit ]
  %vec.phi.unr = phi <8 x float> [ %88, %vector.ph ], [ %121, %middle.block.unr-lcssa.loopexit ]
  %vec.phi36.unr = phi <8 x float> [ %89, %vector.ph ], [ %120, %middle.block.unr-lcssa.loopexit ]
  br i1 %lcmp.mod.not, label %middle.block, label %vector.body.epil

vector.body.epil:                                 ; preds = %middle.block.unr-lcssa
  %122 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind.unr, <8 x i32> zeroinitializer)
  %123 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat, <8 x i32> %122)
  %124 = add nsw <8 x i32> %vec.ind.unr, splat (i32 1)
  %125 = sitofp <8 x i32> %124 to <8 x float>
  %126 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %125, <8 x float> %broadcast.splat38)
  %127 = sitofp <8 x i32> %vec.ind.unr to <8 x float>
  %128 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %127, <8 x float> %broadcast.splat40)
  %129 = fsub reassoc ninf nsz <8 x float> %126, %128
  %130 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %129, <8 x float> zeroinitializer)
  %131 = fmul reassoc ninf nsz <8 x float> %130, %broadcast.splat42
  %132 = add <8 x i32> %broadcast.splat44, %123
  %133 = sext <8 x i32> %132 to <8 x i64>
  %134 = getelementptr float, ptr %.pre, <8 x i64> %133
  %wide.masked.gather.epil = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %134, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %135 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather.epil, %131
  %136 = fadd reassoc ninf nsz <8 x float> %135, %vec.phi36.unr
  %137 = fadd reassoc ninf nsz <8 x float> %131, %vec.phi.unr
  br label %middle.block

middle.block:                                     ; preds = %vector.body.epil, %middle.block.unr-lcssa
  %.lcssa47 = phi <8 x float> [ %.lcssa47.ph, %middle.block.unr-lcssa ], [ %136, %vector.body.epil ]
  %.lcssa46 = phi <8 x float> [ %.lcssa46.ph, %middle.block.unr-lcssa ], [ %137, %vector.body.epil ]
  %138 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa47)
  %139 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %.lcssa46)
  br i1 %cmp.n, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, label %for_loop_body5.us.preheader

for_loop_body5.us.preheader:                      ; preds = %middle.block, %for_loop_body1.us
  %.020.us.ph = phi i32 [ %60, %for_loop_body1.us ], [ %ind.end, %middle.block ]
  %.119.us.ph = phi float [ %.01423.us, %for_loop_body1.us ], [ %139, %middle.block ]
  %.11618.us.ph = phi float [ %.01522.us, %for_loop_body1.us ], [ %138, %middle.block ]
  br label %for_loop_body5.us

for_loop_body5.us:                                ; preds = %for_loop_body5.us, %for_loop_body5.us.preheader
  %.020.us = phi i32 [ %142, %for_loop_body5.us ], [ %.020.us.ph, %for_loop_body5.us.preheader ]
  %.119.us = phi float [ %156, %for_loop_body5.us ], [ %.119.us.ph, %for_loop_body5.us.preheader ]
  %.11618.us = phi float [ %155, %for_loop_body5.us ], [ %.11618.us.ph, %for_loop_body5.us.preheader ]
  %140 = tail call i32 @llvm.smax.i32(i32 %.020.us, i32 0)
  %141 = tail call i32 @llvm.smin.i32(i32 %70, i32 %140)
  %142 = add nsw i32 %.020.us, 1
  %143 = sitofp i32 %142 to float
  %144 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %143, float %46)
  %145 = sitofp i32 %.020.us to float
  %146 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %145, float %43)
  %147 = fsub reassoc ninf nsz float %144, %146
  %148 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %147, float 0.000000e+00)
  %149 = fmul reassoc ninf nsz float %148, %86
  %150 = add i32 %87, %141
  %151 = sext i32 %150 to i64
  %152 = getelementptr float, ptr %.pre, i64 %151
  %153 = load float, ptr %152, align 4
  %154 = fmul reassoc ninf nsz float %153, %149
  %155 = fadd reassoc ninf nsz float %154, %.11618.us
  %156 = fadd reassoc ninf nsz float %149, %.119.us
  %exitcond.not = icmp eq i32 %62, %142
  br i1 %exitcond.not, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, label %for_loop_body5.us, !llvm.loop !11

for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit: ; preds = %for_loop_body5.us
  br label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us

for_loop_test8.for_loop_test4.loopexit_crit_edge.us: ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, %middle.block
  %.lcssa35 = phi float [ %138, %middle.block ], [ %155, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %139, %middle.block ], [ %156, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %exitcond31.not = icmp eq i32 %79, %58
  br i1 %exitcond31.not, label %after_for3.loopexit, label %for_loop_body1.us

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3.loopexit:                              ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.015.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa35, %after_for3.loopexit ]
  %.014.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa, %after_for3.loopexit ]
  %157 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.014.lcssa, float 0x3E112E0BE0000000)
  %158 = fdiv reassoc ninf nsz float %.015.lcssa, %157
  %159 = load ptr, ptr %25, align 8
  %160 = load i32, ptr %26, align 4
  %161 = mul i32 %160, %38
  %162 = add i32 %161, %33
  %163 = sext i32 %162 to i64
  %164 = getelementptr float, ptr %159, i64 %163
  store float %158, ptr %164, align 4
  %165 = add nsw i32 %.01727, 1
  %exitcond32.not = icmp eq i32 %165, %19
  br i1 %exitcond32.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.ceil.f32(float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.6, align 8
  %.sroa.0.0..sroa_cast = bitcast ptr %0 to ptr
  %.sroa.0.0.copyload = load ptr, ptr %.sroa.0.0..sroa_cast, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 8
  %.sroa.4.0..sroa_cast = bitcast ptr %.sroa.4.0..sroa_idx to ptr
  %.sroa.4.0.copyload = load ptr, ptr %.sroa.4.0..sroa_cast, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 16
  %.sroa.5.0..sroa_cast = bitcast ptr %.sroa.5.0..sroa_idx to ptr
  %.sroa.5.0.copyload = load ptr, ptr %.sroa.5.0..sroa_cast, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 24
  %.sroa.7.0..sroa_cast = bitcast ptr %.sroa.7.0..sroa_idx to ptr
  %.sroa.7.0.copyload = load ptr, ptr %.sroa.7.0..sroa_cast, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 32
  %.sroa.8.0..sroa_cast = bitcast ptr %.sroa.8.0..sroa_idx to ptr
  %.sroa.8.0.copyload = load i64, ptr %.sroa.8.0..sroa_cast, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 40
  %.sroa.9.0..sroa_cast = bitcast ptr %.sroa.9.0..sroa_idx to ptr
  %.sroa.9.0.copyload = load i32, ptr %.sroa.9.0..sroa_cast, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 44
  %.sroa.12.0..sroa_cast = bitcast ptr %.sroa.12.0..sroa_idx to ptr
  %.sroa.12.0.copyload = load i32, ptr %.sroa.12.0..sroa_cast, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 48
  %.sroa.15.0..sroa_cast = bitcast ptr %.sroa.15.0..sroa_idx to ptr
  %.sroa.15.0.copyload = load i32, ptr %.sroa.15.0..sroa_cast, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds i8, ptr %0, i64 52
  %.sroa.17.0..sroa_cast = bitcast ptr %.sroa.17.0..sroa_idx to ptr
  %.sroa.17.0.copyload = load i32, ptr %.sroa.17.0..sroa_cast, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq ptr %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %7

7:                                                ; preds = %6, %3
  %8 = bitcast ptr %.sroa.0.0.copyload to ptr
  %9 = bitcast ptr %4 to ptr
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %9, ptr noundef nonnull align 8 dereferenceable(32) %8, i64 32, i1 false)
  %10 = getelementptr inbounds %struct.RuntimeContext.6, ptr %4, i64 0, i32 2
  store i32 %1, ptr %10, align 8
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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02038) #1
  %17 = add nsw i32 %.02038, 1
  %18 = icmp slt i32 %17, %15
  br i1 %18, label %.lr.ph, label %.loopexit.loopexit, !llvm.loop !13

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
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #1
  %.not25.not = icmp sgt i32 %.0, %23
  br i1 %.not25.not, label %.lr.ph41, label %.loopexit.loopexit46, !llvm.loop !15

.loopexit.loopexit:                               ; preds = %.lr.ph
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph41
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %19, %11, %7
  %.not24 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not24, label %25, label %24

24:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #1
  br label %25

25:                                               ; preds = %24, %.loopexit
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.minnum.v8f32(<8 x float>, <8 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.maxnum.v8f32(<8 x float>, <8 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #3

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #7

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn }
attributes #1 = { nounwind }
attributes #2 = { nofree nosync nounwind }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #4 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(read) }

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
!7 = !{i32 8, !"PIC Level", i32 2}
!8 = !{i32 7, !"uwtable", i32 1}
!9 = distinct !{!9, !10}
!10 = !{!"llvm.loop.isvectorized", i32 1}
!11 = distinct !{!11, !12, !10}
!12 = !{!"llvm.loop.unroll.runtime.disable"}
!13 = distinct !{!13, !14}
!14 = !{!"llvm.loop.mustprogress"}
!15 = distinct !{!15, !14}
