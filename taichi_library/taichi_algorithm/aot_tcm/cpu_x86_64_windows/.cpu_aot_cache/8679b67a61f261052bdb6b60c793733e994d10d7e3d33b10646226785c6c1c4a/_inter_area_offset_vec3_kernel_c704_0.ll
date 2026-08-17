; ModuleID = '<string>'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.34.31937"

%0 = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.36 = type { ptr, ptr, i32, ptr }
%struct.LLVMRuntime.35 = type { %struct.PreallocatedMemoryChunk.31, %struct.PreallocatedMemoryChunk.31, ptr, ptr, ptr, ptr, ptr, [512 x ptr], [512 x i64], ptr, ptr, [1024 x ptr], [1024 x ptr], [1024 x ptr], ptr, ptr, ptr, ptr, ptr, [2048 x i8], [32 x i64], i32, i64, ptr, i32, i32, i64 }
%struct.PreallocatedMemoryChunk.31 = type { ptr, ptr, i64 }

; Function Attrs: mustprogress nofree nosync nounwind willreturn
define void @_inter_area_offset_vec3_kernel_c684_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = bitcast ptr %context to ptr
  %1 = load ptr, ptr %0, align 8
  %2 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %1, i64 0, i32 3
  %3 = load i32, ptr %2, align 4
  %4 = getelementptr inbounds %struct.RuntimeContext.36, ptr %context, i64 0, i32 1
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %5, i64 0, i32 14
  %7 = load ptr, ptr %6, align 8
  %8 = getelementptr inbounds i8, ptr %7, i64 20
  %9 = bitcast ptr %8 to ptr
  store i32 %3, ptr %9, align 4
  %10 = sitofp i32 %3 to float
  %11 = load ptr, ptr %0, align 8
  %12 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %11, i64 0, i32 5
  %13 = load i32, ptr %12, align 4
  %14 = sitofp i32 %13 to float
  %15 = fdiv reassoc ninf nsz float %10, %14
  %16 = load ptr, ptr %4, align 8
  %17 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %16, i64 0, i32 14
  %18 = load ptr, ptr %17, align 8
  %19 = getelementptr inbounds i8, ptr %18, i64 8
  %20 = bitcast ptr %19 to ptr
  store float %15, ptr %20, align 4
  %21 = load ptr, ptr %0, align 8
  %22 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 2
  %23 = load i32, ptr %22, align 4
  %24 = load ptr, ptr %4, align 8
  %25 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %24, i64 0, i32 14
  %26 = load ptr, ptr %25, align 8
  %27 = getelementptr inbounds i8, ptr %26, i64 16
  %28 = bitcast ptr %27 to ptr
  store i32 %23, ptr %28, align 4
  %29 = sitofp i32 %23 to float
  %30 = load ptr, ptr %0, align 8
  %31 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %30, i64 0, i32 4
  %32 = load i32, ptr %31, align 4
  %33 = sitofp i32 %32 to float
  %34 = fdiv reassoc ninf nsz float %29, %33
  %35 = load ptr, ptr %4, align 8
  %36 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %35, i64 0, i32 14
  %37 = load ptr, ptr %36, align 8
  %38 = getelementptr inbounds i8, ptr %37, i64 12
  %39 = bitcast ptr %38 to ptr
  store float %34, ptr %39, align 4
  %40 = load ptr, ptr %0, align 8
  %41 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %40, i64 0, i32 1, i32 0, i32 0
  %42 = load i32, ptr %41, align 4
  %43 = tail call i32 @llvm.smax.i32(i32 %42, i32 0)
  %44 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %40, i64 0, i32 1, i32 0, i32 1
  %45 = load i32, ptr %44, align 4
  %46 = tail call i32 @llvm.smax.i32(i32 %45, i32 0)
  %47 = load ptr, ptr %4, align 8
  %48 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %47, i64 0, i32 14
  %49 = load ptr, ptr %48, align 8
  %50 = getelementptr inbounds i8, ptr %49, i64 4
  %51 = bitcast ptr %50 to ptr
  store i32 %46, ptr %51, align 4
  %52 = mul i32 %46, %43
  %53 = load ptr, ptr %4, align 8
  %54 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %53, i64 0, i32 14
  %55 = bitcast ptr %54 to ptr
  %56 = load ptr, ptr %55, align 8
  store i32 %52, ptr %56, align 4
  ret void
}

; Function Attrs: nounwind
define void @_inter_area_offset_vec3_kernel_c684_0_kernel_1_range_for(ptr %context) local_unnamed_addr #1 {
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
  %9 = getelementptr inbounds %struct.RuntimeContext.36, ptr %context, i64 0, i32 1
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %10, i64 0, i32 10
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %10, i64 0, i32 9
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %1, ptr noundef nonnull @cpu_parallel_range_for_task) #1
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %1)
  ret void
}

; Function Attrs: nofree nosync nounwind
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #2 {
allocs:
  %3 = getelementptr inbounds %struct.RuntimeContext.36, ptr %0, i64 0, i32 1
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %4, i64 0, i32 14
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
  %20 = bitcast ptr %0 to ptr
  %21 = load ptr, ptr %20, align 8
  %22 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 6
  %23 = bitcast ptr %22 to ptr
  %24 = load <2 x i32>, ptr %23, align 4
  %25 = icmp slt i32 %17, %19
  br i1 %25, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %26 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 0, i32 1
  %27 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 0, i32 0, i32 1
  %28 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 1, i32 1
  %29 = getelementptr { { { i32, i32 }, ptr }, { { i32, i32 }, ptr }, i32, i32, i32, i32, i32, i32 }, ptr %21, i64 0, i32 1, i32 0, i32 1
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_for3, %for_loop_body.lr.ph
  %.02544 = phi i32 [ %17, %for_loop_body.lr.ph ], [ %185, %after_for3 ]
  %30 = load ptr, ptr %3, align 8
  %31 = getelementptr inbounds %struct.LLVMRuntime.35, ptr %30, i64 0, i32 14
  %32 = load ptr, ptr %31, align 8
  %33 = getelementptr inbounds i8, ptr %32, i64 4
  %34 = bitcast ptr %33 to ptr
  %35 = load i32, ptr %34, align 4
  %36 = sdiv i32 %.02544, %35
  %37 = mul i32 %36, %35
  %38 = xor i32 %35, %.02544
  %39 = icmp slt i32 %38, 0
  %40 = icmp ne i32 %.02544, 0
  %41 = icmp ne i32 %37, %.02544
  %42 = and i1 %40, %39
  %43 = and i1 %42, %41
  %.neg26 = sext i1 %43 to i32
  %44 = add i32 %36, %.neg26
  %45 = mul i32 %44, %35
  %46 = sub i32 %.02544, %45
  %47 = getelementptr inbounds i8, ptr %32, i64 8
  %48 = getelementptr inbounds i8, ptr %32, i64 16
  %49 = bitcast ptr %48 to ptr
  %50 = load i32, ptr %49, align 4
  %51 = add i32 %50, -1
  %52 = getelementptr inbounds i8, ptr %32, i64 20
  %53 = bitcast ptr %52 to ptr
  %54 = load i32, ptr %53, align 4
  %55 = add i32 %54, -1
  %56 = insertelement <2 x i32> poison, i32 %44, i64 0
  %57 = insertelement <2 x i32> %56, i32 %46, i64 1
  %58 = add <2 x i32> %57, %24
  %shuffle = shufflevector <2 x i32> %58, <2 x i32> poison, <2 x i32> <i32 1, i32 0>
  %59 = sitofp <2 x i32> %shuffle to <2 x float>
  %60 = bitcast ptr %47 to ptr
  %61 = load <2 x float>, ptr %60, align 4
  %62 = fmul reassoc ninf nsz <2 x float> %61, %59
  %63 = add <2 x i32> %shuffle, splat (i32 1)
  %64 = sitofp <2 x i32> %63 to <2 x float>
  %65 = fmul reassoc ninf nsz <2 x float> %61, %64
  %66 = call reassoc ninf nsz <2 x float> @llvm.floor.v2f32(<2 x float> %62)
  %67 = call reassoc ninf nsz <2 x float> @llvm.ceil.v2f32(<2 x float> %65)
  %68 = fptosi <2 x float> %66 to <2 x i32>
  %69 = fptosi <2 x float> %67 to <2 x i32>
  %70 = icmp sgt <2 x i32> %69, %68
  %71 = extractelement <2 x i1> %70, i64 0
  %72 = extractelement <2 x i1> %70, i64 1
  %or.cond = select i1 %72, i1 %71, i1 false
  br i1 %or.cond, label %for_loop_body1.us.preheader, label %after_for3

for_loop_body1.us.preheader:                      ; preds = %for_loop_body
  %.pre = load ptr, ptr %26, align 8
  %.pre54 = load i32, ptr %27, align 4
  %73 = extractelement <2 x i32> %69, i64 0
  %74 = extractelement <2 x i32> %68, i64 0
  %75 = sub i32 %73, %74
  %76 = extractelement <2 x i32> %68, i64 1
  %77 = extractelement <2 x float> %62, i64 1
  %78 = extractelement <2 x float> %65, i64 1
  %min.iters.check = icmp ult i32 %75, 8
  %n.vec = and i32 %75, -8
  %ind.end = add i32 %n.vec, %74
  %.splat = shufflevector <2 x i32> %68, <2 x i32> poison, <8 x i32> zeroinitializer
  %induction = add <8 x i32> %.splat, <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>
  %broadcast.splat = shufflevector <2 x float> %65, <2 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splat65 = shufflevector <2 x float> %62, <2 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert68 = insertelement <8 x i32> poison, i32 %55, i64 0
  %broadcast.splat69 = shufflevector <8 x i32> %broadcast.splatinsert68, <8 x i32> poison, <8 x i32> zeroinitializer
  %cmp.n = icmp eq i32 %75, %n.vec
  %79 = extractelement <2 x float> %65, i64 0
  %80 = extractelement <2 x float> %62, i64 0
  %81 = extractelement <2 x i32> %69, i64 1
  br label %for_loop_body1.us

for_loop_body1.us:                                ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, %for_loop_body1.us.preheader
  %.01739.us = phi i32 [ %82, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ %76, %for_loop_body1.us.preheader ]
  %.01838.us = phi float [ %.lcssa, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.01937.us = phi float [ %.lcssa58, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.02136.us = phi float [ %.lcssa59, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %.02335.us = phi float [ %.lcssa60, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us ], [ 0.000000e+00, %for_loop_body1.us.preheader ]
  %82 = add nsw i32 %.01739.us, 1
  %83 = sitofp i32 %.01739.us to float
  %84 = tail call i32 @llvm.smax.i32(i32 %.01739.us, i32 0)
  %85 = sitofp i32 %82 to float
  %86 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %83, float %77)
  %87 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %85, float %78)
  %88 = tail call i32 @llvm.smin.i32(i32 %51, i32 %84)
  %89 = fsub reassoc ninf nsz float %87, %86
  %90 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %89, float 0.000000e+00)
  %91 = mul i32 %.pre54, %88
  br i1 %min.iters.check, label %for_loop_body5.us.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body1.us
  %92 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01838.us, i64 0
  %93 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.01937.us, i64 0
  %94 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.02136.us, i64 0
  %95 = insertelement <8 x float> <float poison, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00, float 0.000000e+00>, float %.02335.us, i64 0
  %broadcast.splatinsert66 = insertelement <8 x float> poison, float %90, i64 0
  %broadcast.splat67 = shufflevector <8 x float> %broadcast.splatinsert66, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert70 = insertelement <8 x i32> poison, i32 %91, i64 0
  %broadcast.splat71 = shufflevector <8 x i32> %broadcast.splatinsert70, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ %92, %vector.ph ], [ %122, %vector.body ]
  %vec.phi61 = phi <8 x float> [ %93, %vector.ph ], [ %121, %vector.body ]
  %vec.phi62 = phi <8 x float> [ %94, %vector.ph ], [ %120, %vector.body ]
  %vec.phi63 = phi <8 x float> [ %95, %vector.ph ], [ %119, %vector.body ]
  %96 = add nsw <8 x i32> %vec.ind, splat (i32 1)
  %97 = sitofp <8 x i32> %96 to <8 x float>
  %98 = call reassoc ninf nsz <8 x float> @llvm.minnum.v8f32(<8 x float> %97, <8 x float> %broadcast.splat)
  %99 = sitofp <8 x i32> %vec.ind to <8 x float>
  %100 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %99, <8 x float> %broadcast.splat65)
  %101 = fsub reassoc ninf nsz <8 x float> %98, %100
  %102 = call reassoc ninf nsz <8 x float> @llvm.maxnum.v8f32(<8 x float> %101, <8 x float> zeroinitializer)
  %103 = fmul reassoc ninf nsz <8 x float> %102, %broadcast.splat67
  %104 = call <8 x i32> @llvm.smax.v8i32(<8 x i32> %vec.ind, <8 x i32> zeroinitializer)
  %105 = call <8 x i32> @llvm.smin.v8i32(<8 x i32> %broadcast.splat69, <8 x i32> %104)
  %106 = add <8 x i32> %broadcast.splat71, %105
  %107 = mul <8 x i32> %106, splat (i32 3)
  %108 = sext <8 x i32> %107 to <8 x i64>
  %109 = getelementptr float, ptr %.pre, <8 x i64> %108
  %wide.masked.gather = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %109, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %110 = add <8 x i32> %107, splat (i32 1)
  %111 = sext <8 x i32> %110 to <8 x i64>
  %112 = getelementptr float, ptr %.pre, <8 x i64> %111
  %wide.masked.gather72 = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %112, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %113 = add <8 x i32> %107, splat (i32 2)
  %114 = sext <8 x i32> %113 to <8 x i64>
  %115 = getelementptr float, ptr %.pre, <8 x i64> %114
  %wide.masked.gather73 = call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %115, i32 4, <8 x i1> splat (i1 true), <8 x float> undef)
  %116 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather, %103
  %117 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather72, %103
  %118 = fmul reassoc ninf nsz <8 x float> %wide.masked.gather73, %103
  %119 = fadd reassoc ninf nsz <8 x float> %116, %vec.phi63
  %120 = fadd reassoc ninf nsz <8 x float> %117, %vec.phi62
  %121 = fadd reassoc ninf nsz <8 x float> %118, %vec.phi61
  %122 = fadd reassoc ninf nsz <8 x float> %103, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %lsr.iv.next = add i32 %lsr.iv, -8
  %123 = icmp eq i32 %lsr.iv.next, 0
  br i1 %123, label %middle.block, label %vector.body, !llvm.loop !9

middle.block:                                     ; preds = %vector.body
  %124 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %119)
  %125 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %120)
  %126 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %121)
  %127 = call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float -0.000000e+00, <8 x float> %122)
  br i1 %cmp.n, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us, label %for_loop_body5.us.preheader

for_loop_body5.us.preheader:                      ; preds = %middle.block, %for_loop_body1.us
  %.031.us.ph = phi i32 [ %74, %for_loop_body1.us ], [ %ind.end, %middle.block ]
  %.130.us.ph = phi float [ %.01838.us, %for_loop_body1.us ], [ %127, %middle.block ]
  %.12029.us.ph = phi float [ %.01937.us, %for_loop_body1.us ], [ %126, %middle.block ]
  %.12228.us.ph = phi float [ %.02136.us, %for_loop_body1.us ], [ %125, %middle.block ]
  %.12427.us.ph = phi float [ %.02335.us, %for_loop_body1.us ], [ %124, %middle.block ]
  br label %for_loop_body5.us

for_loop_body5.us:                                ; preds = %for_loop_body5.us, %for_loop_body5.us.preheader
  %.031.us = phi i32 [ %128, %for_loop_body5.us ], [ %.031.us.ph, %for_loop_body5.us.preheader ]
  %.130.us = phi float [ %157, %for_loop_body5.us ], [ %.130.us.ph, %for_loop_body5.us.preheader ]
  %.12029.us = phi float [ %156, %for_loop_body5.us ], [ %.12029.us.ph, %for_loop_body5.us.preheader ]
  %.12228.us = phi float [ %155, %for_loop_body5.us ], [ %.12228.us.ph, %for_loop_body5.us.preheader ]
  %.12427.us = phi float [ %154, %for_loop_body5.us ], [ %.12427.us.ph, %for_loop_body5.us.preheader ]
  %128 = add nsw i32 %.031.us, 1
  %129 = sitofp i32 %128 to float
  %130 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %129, float %79)
  %131 = sitofp i32 %.031.us to float
  %132 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %131, float %80)
  %133 = fsub reassoc ninf nsz float %130, %132
  %134 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %133, float 0.000000e+00)
  %135 = fmul reassoc ninf nsz float %134, %90
  %136 = tail call i32 @llvm.smax.i32(i32 %.031.us, i32 0)
  %137 = tail call i32 @llvm.smin.i32(i32 %55, i32 %136)
  %138 = add i32 %91, %137
  %139 = mul i32 %138, 3
  %140 = sext i32 %139 to i64
  %141 = getelementptr float, ptr %.pre, i64 %140
  %142 = load float, ptr %141, align 4
  %143 = add i32 %139, 1
  %144 = sext i32 %143 to i64
  %145 = getelementptr float, ptr %.pre, i64 %144
  %146 = load float, ptr %145, align 4
  %147 = add i32 %139, 2
  %148 = sext i32 %147 to i64
  %149 = getelementptr float, ptr %.pre, i64 %148
  %150 = load float, ptr %149, align 4
  %151 = fmul reassoc ninf nsz float %142, %135
  %152 = fmul reassoc ninf nsz float %146, %135
  %153 = fmul reassoc ninf nsz float %150, %135
  %154 = fadd reassoc ninf nsz float %151, %.12427.us
  %155 = fadd reassoc ninf nsz float %152, %.12228.us
  %156 = fadd reassoc ninf nsz float %153, %.12029.us
  %157 = fadd reassoc ninf nsz float %135, %.130.us
  %exitcond.not = icmp eq i32 %73, %128
  br i1 %exitcond.not, label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, label %for_loop_body5.us, !llvm.loop !11

for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit: ; preds = %for_loop_body5.us
  br label %for_loop_test8.for_loop_test4.loopexit_crit_edge.us

for_loop_test8.for_loop_test4.loopexit_crit_edge.us: ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit, %middle.block
  %.lcssa60 = phi float [ %124, %middle.block ], [ %154, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa59 = phi float [ %125, %middle.block ], [ %155, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa58 = phi float [ %126, %middle.block ], [ %156, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %.lcssa = phi float [ %127, %middle.block ], [ %157, %for_loop_test8.for_loop_test4.loopexit_crit_edge.us.loopexit ]
  %exitcond52.not = icmp eq i32 %82, %81
  br i1 %exitcond52.not, label %after_for3.loopexit, label %for_loop_body1.us

after_for.loopexit:                               ; preds = %after_for3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

after_for3.loopexit:                              ; preds = %for_loop_test8.for_loop_test4.loopexit_crit_edge.us
  br label %after_for3

after_for3:                                       ; preds = %after_for3.loopexit, %for_loop_body
  %.023.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa60, %after_for3.loopexit ]
  %.021.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa59, %after_for3.loopexit ]
  %.019.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa58, %after_for3.loopexit ]
  %.018.lcssa = phi float [ 0.000000e+00, %for_loop_body ], [ %.lcssa, %after_for3.loopexit ]
  %158 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %.018.lcssa, float 0x3E112E0BE0000000)
  %159 = fdiv reassoc ninf nsz float %.023.lcssa, %158
  %160 = fdiv reassoc ninf nsz float %.021.lcssa, %158
  %161 = fdiv reassoc ninf nsz float %.019.lcssa, %158
  %162 = load ptr, ptr %28, align 8
  %163 = load i32, ptr %29, align 4
  %164 = mul i32 %163, %44
  %165 = add i32 %164, %46
  %166 = mul i32 %165, 3
  %167 = sext i32 %166 to i64
  %168 = getelementptr float, ptr %162, i64 %167
  store float %159, ptr %168, align 4
  %169 = load ptr, ptr %28, align 8
  %170 = load i32, ptr %29, align 4
  %171 = mul i32 %170, %44
  %172 = add i32 %171, %46
  %173 = mul i32 %172, 3
  %174 = add i32 %173, 1
  %175 = sext i32 %174 to i64
  %176 = getelementptr float, ptr %169, i64 %175
  store float %160, ptr %176, align 4
  %177 = load ptr, ptr %28, align 8
  %178 = load i32, ptr %29, align 4
  %179 = mul i32 %178, %44
  %180 = add i32 %179, %46
  %181 = mul i32 %180, 3
  %182 = add i32 %181, 2
  %183 = sext i32 %182 to i64
  %184 = getelementptr float, ptr %177, i64 %183
  store float %161, ptr %184, align 4
  %185 = add nsw i32 %.02544, 1
  %exitcond53.not = icmp eq i32 %185, %19
  br i1 %exitcond53.not, label %after_for.loopexit, label %for_loop_body
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #3

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #4 {
  %4 = alloca %struct.RuntimeContext.36, align 8
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
  %10 = getelementptr inbounds %struct.RuntimeContext.36, ptr %4, i64 0, i32 2
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
declare <8 x float> @llvm.minnum.v8f32(<8 x float>, <8 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.maxnum.v8f32(<8 x float>, <8 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <2 x float> @llvm.ceil.v2f32(<2 x float>) #3

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <2 x float> @llvm.floor.v2f32(<2 x float>) #3

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #7

attributes #0 = { mustprogress nofree nosync nounwind willreturn }
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
