; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime = type { %struct.PreallocatedMemoryChunk, %struct.PreallocatedMemoryChunk, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk = type { ptr, ptr, i64 }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn
define void @_inter_area_vec3_kernel_c680_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %1, i64 0, i32 3
  %3 = load i32, ptr %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext, ptr %context, i64 0, i32 1
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime, ptr %5, i64 0, i32 14
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
  %17 = getelementptr inbounds %struct.LLVMRuntime, ptr %16, i64 0, i32 14
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds i8, ptr %18, i64 12
  %20 = bitcast ptr %19 to ptr
  store float %15, ptr %20, align 4
  %21 = load ptr, ptr %0, align 8
  %22 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %21, i64 0, i32 2
  %23 = load i32, ptr %22, align 4
  %24 = load ptr, ptr %4, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime, ptr %24, i64 0, i32 14
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
  %36 = getelementptr inbounds %struct.LLVMRuntime, ptr %35, i64 0, i32 14
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds i8, ptr %37, i64 16
  %39 = bitcast ptr %38 to ptr
  store float %34, ptr %39, align 4
  %40 = load ptr, ptr %0, align 8
  %41 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %40, i64 0, i32 1, i32 0, i32 0
  %42 = load i32, ptr %41, align 4
  %43 = load ptr, ptr %4, align 8
  %44 = getelementptr inbounds %struct.LLVMRuntime, ptr %43, i64 0, i32 14
  %45 = load ptr, ptr %44, align 8
  %46 = getelementptr inbounds i8, ptr %45, i64 8
  %47 = bitcast ptr %46 to ptr
  store i32 %42, ptr %47, align 4
  %48 = load ptr, ptr %0, align 8
  %49 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32 }, ptr %48, i64 0, i32 1, i32 0, i32 1
  %50 = load i32, ptr %49, align 4
  %51 = load ptr, ptr %4, align 8
  %52 = getelementptr inbounds %struct.LLVMRuntime, ptr %51, i64 0, i32 14
  %53 = load ptr, ptr %52, align 8
  %54 = getelementptr inbounds i8, ptr %53, i64 4
  %55 = bitcast ptr %54 to ptr
  store i32 %50, ptr %55, align 4
  %56 = mul i32 %50, %42
  %57 = load ptr, ptr %4, align 8
  %58 = getelementptr inbounds %struct.LLVMRuntime, ptr %57, i64 0, i32 14
  %59 = bitcast ptr %58 to ptr
  %60 = load ptr, ptr %59, align 8
  store i32 %56, ptr %60, align 4
  ret void
}

; Function Attrs: nounwind
define void @_inter_area_vec3_kernel_c680_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
entry:
  %0 = alloca %0, align 8
  %1 = bitcast ptr %0 to ptr
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %1)
  %2 = getelementptr inbounds %0, ptr %0, i64 0, i32 1
  %3 = getelementptr inbounds %0, ptr %0, i64 0, i32 4
  %4 = getelementptr inbounds %0, ptr %0, i64 0, i32 0
  store ptr %context, ptr %4, align 8
  store ptr null, ptr %2, align 8
  store i64 1, ptr %3, align 8
  %5 = getelementptr inbounds %0, ptr %0, i64 0, i32 2
  store ptr @function_body, ptr %5, align 8
  %6 = getelementptr inbounds %0, ptr %0, i64 0, i32 3
  store ptr null, ptr %6, align 8
  %7 = getelementptr inbounds %0, ptr %0, i64 0, i32 5
  %8 = bitcast ptr %7 to ptr
  store <4 x i32> <i32 0, i32 8, i32 1, i32 1>, ptr %8, align 8
  %9 = getelementptr inbounds %struct.RuntimeContext, ptr %context, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime, ptr %10, i64 0, i32 10
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime, ptr %10, i64 0, i32 9
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext, ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime, ptr %4, i64 0, i32 14
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
  %.02543 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %177, %after_for3 ]
  %27 = load ptr, ptr %3, align 8
  %28 = getelementptr inbounds %struct.LLVMRuntime, ptr %27, i64 0, i32 14
  %29 = load ptr, ptr %28, align 8
  %30 = getelementptr inbounds i8, ptr %29, i64 4
  %31 = bitcast ptr %30 to ptr
  %32 = load i32, ptr %31, align 4
  %33 = srem i32 %.02543, %32
  %34 = sdiv i32 %.02543, %32
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
  %.pre53 = load i32, ptr %24, align 4
  %73 = sub i32 %62, %60
  %min.iters.check = icmp ult i32 %73, 8
  %n.vec = and i32 %73, -8
  %ind.end = add i32 %n.vec, %60
  %.splatinsert = insertelement <8 x i32> poison, i32 %60, i64 0
  %.splat = shufflevector <8 x i32> %.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %70, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert63 = insertelement <8 x float> poison, float %46, i64 0
  %broadcast.splat64 = shufflevector <8 x float> %broadcast.splatinsert63, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert65 = insertelement <8 x float> poison, float %43, i64 0
  %broadcast.splat66 = shufflevector <8 x float> %broadcast.splatinsert65, <8 x float> poison, <8 x i32> zeroinitializer
  %cmp.n = icmp eq i32 %73, %n.vec
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, %for_loop_body1.us.preheader
  %.01738.us = phi i32 [ %75, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ %56, %for_loop_body1.us.preheader ]
  %.01837.us = phi float [ %.lcssa, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.01936.us = phi float [ %.lcssa57, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.02135.us = phi float [ %.lcssa58, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.02334.us = phi float [ %.lcssa59, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %74 = tail call i32 @llvm.smax.i32(i32 %.01738.us, i32 0)
  %75 = add nsw i32 %.01738.us, 1
  %76 = sitofp i32 %.01738.us to float
  %77 = sitofp i32 %75 to float
  %78 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %76, float %51)
  %79 = tail call i32 @llvm.smin.i32(i32 %66, i32 %74)
  %80 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %77, float %54)
  %81 = fsub reassoc ninf nsz float %80, %78
  %82 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %81, float 0.000000e+00)
  %83 = mul i32 %.pre53, %79
  br i1 %min.iters.check, label %for_loop_body5.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body1.us
  %84 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01837.us, i64 0
  %85 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01936.us, i64 0
  %86 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.02135.us, i64 0
  %87 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.02334.us, i64 0
  %broadcast.splatinsert67 = insertelement <8 x float> poison, float %82, i64 0
  %broadcast.splat68 = shufflevector <8 x float> %broadcast.splatinsert67, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert69 = insertelement <8 x i32> poison, i32 %83, i64 0
  %broadcast.splat70 = shufflevector <8 x i32> %broadcast.splatinsert69, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ %84, %vector.ph ], [ %114, %vector.body ]
  %vec.phi60 = phi <8 x float> [ %85, %vector.ph ], [ %113, %vector.body ]
  %vec.phi61 = phi <8 x float> [ %86, %vector.ph ], [ %112, %vector.body ]
  %vec.phi62 = phi <8 x float> [ %87, %vector.ph ], [ %111, %vector.body ]
  %88 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind, <8 x i32> zeroinitializer)
  %89 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat, <8 x i32> %88)
  %90 = add nsw <8 x i32> %vec.ind, splat (i32 1)
  %91 = sitofp <8 x i32> %90 to <8 x float>
  %92 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %91, <8 x float> %broadcast.splat64)
  %93 = sitofp <8 x i32> %vec.ind to <8 x float>
  %94 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %93, <8 x float> %broadcast.splat66)
  %95 = fsub reassoc ninf nsz <8 x float> %92, %94
  %96 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %95, <8 x float> zeroinitializer)
  %97 = fmul reassoc ninf nsz <8 x float> %96, %broadcast.splat68
  %98 = add <8 x i32> %broadcast.splat70, %89
  %99 = mul <8 x i32> %98, splat (i32 3)
  %100 = sext <8 x i32> %99 to <8 x i64>
  %101 = getelementptr float, ptr %.pre, <8 x i64> %100
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %101, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %102 = add <8 x i32> %99, splat (i32 1)
  %103 = sext <8 x i32> %102 to <8 x i64>
  %104 = getelementptr float, ptr %.pre, <8 x i64> %103
  %wide.masked.gather71 = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %104, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %105 = add <8 x i32> %99, splat (i32 2)
  %106 = sext <8 x i32> %105 to <8 x i64>
  %107 = getelementptr float, ptr %.pre, <8 x i64> %106
  %wide.masked.gather72 = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %107, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %108 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather, %97
  %109 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather71, %97
  %110 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather72, %97
  %111 = fadd reassoc ninf nsz <8 x float> %108, %vec.phi62
  %112 = fadd reassoc ninf nsz <8 x float> %109, %vec.phi61
  %113 = fadd reassoc ninf nsz <8 x float> %110, %vec.phi60
  %114 = fadd reassoc ninf nsz <8 x float> %97, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %lsr.iv.next = add i32 %lsr.iv, -8
  %115 = icmp eq i32 %lsr.iv.next, 0
  br i1 %115, label %middle.block, label %vector.body, !llvm.loop !9

middle.block:                                     ; preds = %vector.body
  %116 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %111)
  %117 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %112)
  %118 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %113)
  %119 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %114)
  br i1 %cmp.n, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, label %for_loop_body5.us.preheader

for_loop_body5.us.preheader:                      ; preds = %middle.block, %for_loop_body1.us
  %.030.us.ph = phi i32 [ %60, %for_loop_body1.us ], [ %ind.end, %middle.block ]
  %.129.us.ph = phi float [ %.01837.us, %for_loop_body1.us ], [ %119, %middle.block ]
  %.12028.us.ph = phi float [ %.01936.us, %for_loop_body1.us ], [ %118, %middle.block ]
  %.12227.us.ph = phi float [ %.02135.us, %for_loop_body1.us ], [ %117, %middle.block ]
  %.12426.us.ph = phi float [ %.02334.us, %for_loop_body1.us ], [ %116, %middle.block ]
  br label %for_loop_body5.us

for_loop_body5.us:                                ; preds = %for_loop_body5.us, %for_loop_body5.us.preheader
  %.030.us = phi i32 [ %122, %for_loop_body5.us ], [ %.030.us.ph, %for_loop_body5.us.preheader ]
  %.129.us = phi float [ %149, %for_loop_body5.us ], [ %.129.us.ph, %for_loop_body5.us.preheader ]
  %.12028.us = phi float [ %148, %for_loop_body5.us ], [ %.12028.us.ph, %for_loop_body5.us.preheader ]
  %.12227.us = phi float [ %147, %for_loop_body5.us ], [ %.12227.us.ph, %for_loop_body5.us.preheader ]
  %.12426.us = phi float [ %146, %for_loop_body5.us ], [ %.12426.us.ph, %for_loop_body5.us.preheader ]
  %120 = tail call i32 @llvm.smax.i32(i32 %.030.us, i32 0)
  %121 = tail call i32 @llvm.smin.i32(i32 %70, i32 %120)
  %122 = add nsw i32 %.030.us, 1
  %123 = sitofp i32 %122 to float
  %124 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %123, float %46)
  %125 = sitofp i32 %.030.us to float
  %126 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %125, float %43)
  %127 = fsub reassoc ninf nsz float %124, %126
  %128 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %127, float 0.000000e+00)
  %129 = fmul reassoc ninf nsz float %128, %82
  %130 = add i32 %83, %121
  %131 = mul i32 %130, 3
  %132 = sext i32 %131 to i64
  %133 = getelementptr float, ptr %.pre, i64 %132
  %134 = load float, ptr %133, align 4
  %135 = add i32 %131, 1
  %136 = sext i32 %135 to i64
  %137 = getelementptr float, ptr %.pre, i64 %136
  %138 = load float, ptr %137, align 4
  %139 = add i32 %131, 2
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %.pre, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = fmul reassoc ninf nsz float %134, %129
  %144 = fmul reassoc ninf nsz float %138, %129
  %145 = fmul reassoc ninf nsz float %142, %129
  %146 = fadd reassoc ninf nsz float %143, %.12426.us
  %147 = fadd reassoc ninf nsz float %144, %.12227.us
  %148 = fadd reassoc ninf nsz float %145, %.12028.us
  %149 = fadd reassoc ninf nsz float %129, %.129.us
  %exitcond.not = icmp eq i32 %62, %122
  br i1 %exitcond.not, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, label %for_loop_body5.us, !llvm.loop !11

for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit: ; preds = %for_loop_body5.us
  br label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us

for_loop_test8.for_loop_test4.loopexit_crit_edge.us: ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, %middle.block
  %.lcssa59 = phi float [ %116, %middle.block ], [ %146, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa58 = phi float [ %117, %middle.block ], [ %147, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa57 = phi float [ %118, %middle.block ], [ %148, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %119, %middle.block ], [ %149, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %exitcond51.not = icmp eq i32 %75, %58
  br i1 %exitcond51.not, label %after_for3.loopexit, label %for_loop_body1.us

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3.loopexit:                              ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.023.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa59, %after_for3.loopexit ]
  %.021.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa58, %after_for3.loopexit ]
  %.019.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa57, %after_for3.loopexit ]
  %.018.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa, %after_for3.loopexit ]
  %150 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.018.lcssa, float 0x3E112E0BE0000000)
  %151 = fdiv reassoc ninf nsz float %.023.lcssa, %150
  %152 = fdiv reassoc ninf nsz float %.021.lcssa, %150
  %153 = fdiv reassoc ninf nsz float %.019.lcssa, %150
  %154 = load ptr, ptr %25, align 8
  %155 = load i32, ptr %26, align 4
  %156 = mul i32 %155, %38
  %157 = add i32 %156, %33
  %158 = mul i32 %157, 3
  %159 = sext i32 %158 to i64
  %160 = getelementptr float, ptr %154, i64 %159
  store float %151, ptr %160, align 4
  %161 = load ptr, ptr %25, align 8
  %162 = load i32, ptr %26, align 4
  %163 = mul i32 %162, %38
  %164 = add i32 %163, %33
  %165 = mul i32 %164, 3
  %166 = add i32 %165, 1
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, ptr %161, i64 %167
  store float %152, ptr %168, align 4
  %169 = load ptr, ptr %25, align 8
  %170 = load i32, ptr %26, align 4
  %171 = mul i32 %170, %38
  %172 = add i32 %171, %33
  %173 = mul i32 %172, 3
  %174 = add i32 %173, 2
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %169, i64 %175
  store float %153, ptr %176, align 4
  %177 = add nsw i32 %.02543, 1
  %exitcond52.not = icmp eq i32 %177, %19
  br i1 %exitcond52.not, label %after_for.loopexit, label %for_loop_body
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
  %4 = alloca %struct.RuntimeContext, align 8
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
  %10 = getelementptr inbounds %struct.RuntimeContext, ptr %4, i64 0, i32 2
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
