; ModuleID = 'kernel'
source_filename = "kernel"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.44.35228"

%struct.range_task_helper_context = type { ptr, ptr, ptr, ptr, i64, i32, i32, i32, i32 }
%struct.RuntimeContext.7 = type { ptr, ptr, i32, ptr }

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none)
define void @_lk_adaptive_refine_kernel_c492_0_kernel_0_serial(ptr nocapture readonly %context) local_unnamed_addr #0 {
entry:
  %0 = load ptr, ptr %context, align 8
  %1 = load i32, ptr %0, align 4
  %2 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %3 = load ptr, ptr %2, align 8
  %4 = getelementptr inbounds nuw i8, ptr %3, i64 32872
  %5 = load ptr, ptr %4, align 8
  %6 = getelementptr inbounds nuw i8, ptr %5, i64 8
  store i32 %1, ptr %6, align 4
  %7 = load ptr, ptr %context, align 8
  %8 = getelementptr i8, ptr %7, i64 4
  %9 = load i32, ptr %8, align 4
  %10 = load ptr, ptr %2, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 32872
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %12, i64 12
  store i32 %9, ptr %13, align 4
  %14 = load ptr, ptr %context, align 8
  %15 = getelementptr i8, ptr %14, i64 32
  %16 = load i32, ptr %15, align 4
  %17 = getelementptr i8, ptr %14, i64 36
  %18 = load i32, ptr %17, align 4
  %19 = tail call i32 @llvm.smax.i32(i32 %16, i32 0)
  %20 = tail call i32 @llvm.smax.i32(i32 %18, i32 0)
  %21 = load ptr, ptr %2, align 8
  %22 = getelementptr inbounds nuw i8, ptr %21, i64 32872
  %23 = load ptr, ptr %22, align 8
  %24 = getelementptr inbounds nuw i8, ptr %23, i64 4
  store i32 %20, ptr %24, align 4
  %25 = mul i32 %20, %19
  %26 = load ptr, ptr %2, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  store i32 %25, ptr %28, align 4
  ret void
}

define void @_lk_adaptive_refine_kernel_c492_0_kernel_1_range_for(ptr %context) local_unnamed_addr {
cpu_parallel_range_for.exit:
  %0 = alloca %struct.range_task_helper_context, align 8
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %0)
  %1 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %2 = getelementptr inbounds nuw i8, ptr %0, i64 16
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 24
  %4 = getelementptr inbounds nuw i8, ptr %0, i64 32
  store ptr %context, ptr %0, align 8
  store ptr null, ptr %1, align 8
  store i64 1, ptr %4, align 8
  store ptr @function_body, ptr %2, align 8
  store ptr null, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %0, i64 40
  store i32 0, ptr %5, align 8
  %6 = getelementptr inbounds nuw i8, ptr %0, i64 44
  store i32 8, ptr %6, align 4
  %7 = getelementptr inbounds nuw i8, ptr %0, i64 52
  store i32 1, ptr %7, align 4
  %8 = getelementptr inbounds nuw i8, ptr %0, i64 48
  store i32 1, ptr %8, align 8
  %9 = getelementptr inbounds nuw i8, ptr %context, i64 8
  %10 = load ptr, ptr %9, align 8
  %11 = getelementptr inbounds nuw i8, ptr %10, i64 8288
  %12 = load ptr, ptr %11, align 8
  %13 = getelementptr inbounds nuw i8, ptr %10, i64 8280
  %14 = load ptr, ptr %13, align 8
  call void %12(ptr noundef %14, i32 noundef 8, i32 noundef 8, ptr noundef nonnull %0, ptr noundef nonnull @cpu_parallel_range_for_task) #8
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %0)
  ret void
}

; Function Attrs: nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none)
define internal void @function_body(ptr nocapture readonly %0, ptr nocapture readnone %1, i32 %2) #1 {
allocs:
  %3 = getelementptr inbounds nuw i8, ptr %0, i64 8
  %4 = load ptr, ptr %3, align 8
  %5 = getelementptr inbounds nuw i8, ptr %4, i64 32872
  %6 = load ptr, ptr %5, align 8
  %7 = load i32, ptr %6, align 4
  %8 = add i32 %7, 7
  %9 = sdiv i32 %8, 8
  %10 = icmp slt i32 %8, 0
  %11 = shl nsw i32 %9, 3
  %12 = icmp ne i32 %11, %8
  %13 = and i1 %10, %12
  %.neg = sext i1 %13 to i32
  %14 = add nsw i32 %9, %.neg
  %15 = tail call i32 @llvm.smax.i32(i32 %14, i32 512)
  %16 = mul i32 %15, %2
  %17 = add i32 %16, %15
  %18 = tail call i32 @llvm.smin.i32(i32 %7, i32 %17)
  %19 = load ptr, ptr %0, align 8
  %20 = getelementptr i8, ptr %19, i64 100
  %21 = load i32, ptr %20, align 4
  %22 = icmp slt i32 %16, %18
  br i1 %22, label %for_loop_body.lr.ph, label %after_for

for_loop_body.lr.ph:                              ; preds = %allocs
  %23 = getelementptr i8, ptr %19, i64 72
  %24 = getelementptr i8, ptr %19, i64 60
  %25 = getelementptr i8, ptr %19, i64 64
  br label %for_loop_body

for_loop_body:                                    ; preds = %after_if3, %for_loop_body.lr.ph
  %.05387 = phi i32 [ %16, %for_loop_body.lr.ph ], [ %113, %after_if3 ]
  %26 = load ptr, ptr %3, align 8
  %27 = getelementptr inbounds nuw i8, ptr %26, i64 32872
  %28 = load ptr, ptr %27, align 8
  %29 = getelementptr inbounds nuw i8, ptr %28, i64 4
  %30 = load i32, ptr %29, align 4
  %31 = sdiv i32 %.05387, %30
  %32 = mul i32 %31, %30
  %33 = xor i32 %30, %.05387
  %34 = icmp slt i32 %33, 0
  %35 = icmp ne i32 %32, %.05387
  %36 = and i1 %34, %35
  %.neg57 = sext i1 %36 to i32
  %37 = add i32 %31, %.neg57
  %38 = mul i32 %37, %30
  %39 = sub i32 %.05387, %38
  %40 = load ptr, ptr %23, align 8
  %41 = load i32, ptr %24, align 4
  %42 = load i32, ptr %25, align 4
  %43 = mul i32 %37, %41
  %44 = add i32 %39, %43
  %45 = mul i32 %44, %42
  %46 = add i32 %45, 2
  %47 = sext i32 %46 to i64
  %48 = getelementptr float, ptr %40, i64 %47
  %49 = load float, ptr %48, align 4
  %50 = fptosi float %49 to i32
  %.not = icmp sgt i32 %21, %50
  br i1 %.not, label %after_if3, label %true_block

after_for.loopexit:                               ; preds = %after_if3
  br label %after_for

after_for:                                        ; preds = %after_for.loopexit, %allocs
  ret void

true_block:                                       ; preds = %for_loop_body
  %51 = load ptr, ptr %0, align 8
  %52 = getelementptr i8, ptr %51, i64 48
  %53 = load ptr, ptr %52, align 8
  %54 = getelementptr i8, ptr %51, i64 36
  %55 = load i32, ptr %54, align 4
  %56 = getelementptr i8, ptr %51, i64 40
  %57 = load i32, ptr %56, align 4
  %58 = mul i32 %55, %37
  %59 = add i32 %58, %39
  %60 = mul i32 %59, %57
  %61 = add i32 %60, 2
  %62 = sext i32 %61 to i64
  %63 = getelementptr float, ptr %53, i64 %62
  %64 = load float, ptr %63, align 4
  %65 = fcmp reassoc ninf nsz ogt float %64, 5.000000e-01
  br i1 %65, label %true_block1, label %after_if3

true_block1:                                      ; preds = %true_block
  %66 = getelementptr i8, ptr %51, i64 80
  %67 = load i32, ptr %66, align 4
  %68 = getelementptr i8, ptr %51, i64 88
  %69 = load i32, ptr %68, align 4
  %70 = add i32 %69, %67
  %71 = shl i32 %70, 1
  %72 = sitofp i32 %71 to float
  %73 = tail call i32 @llvm.smax.i32(i32 %67, i32 2)
  %74 = uitofp nneg i32 %73 to float
  %75 = sext i32 %60 to i64
  %76 = getelementptr float, ptr %53, i64 %75
  %77 = load float, ptr %76, align 4
  %78 = add i32 %60, 1
  %79 = sext i32 %78 to i64
  %80 = getelementptr float, ptr %53, i64 %79
  %81 = load float, ptr %80, align 4
  %82 = sext i32 %45 to i64
  %83 = getelementptr float, ptr %40, i64 %82
  %84 = load float, ptr %83, align 4
  %85 = add i32 %45, 1
  %86 = sext i32 %85 to i64
  %87 = getelementptr float, ptr %40, i64 %86
  %88 = load float, ptr %87, align 4
  %89 = getelementptr i8, ptr %51, i64 92
  %90 = load i32, ptr %89, align 4
  %91 = icmp sgt i32 %90, 0
  br i1 %91, label %for_loop_body4.lr.ph, label %true_block24

for_loop_body4.lr.ph:                             ; preds = %true_block1
  %92 = shl i32 %69, 1
  %neg = sub i32 0, %69
  %93 = add i32 %69, 1
  %94 = tail call i32 @llvm.smax.i32(i32 %neg, i32 %93)
  %95 = add i32 %94, %69
  %96 = mul i32 %95, %95
  %97 = getelementptr i8, ptr %51, i64 84
  %98 = getelementptr inbounds nuw i8, ptr %28, i64 8
  %99 = getelementptr inbounds nuw i8, ptr %28, i64 12
  %100 = mul i32 %67, %37
  %101 = mul i32 %67, %39
  %102 = icmp sgt i32 %96, 0
  %103 = icmp slt i32 %95, 0
  %.neg60 = sub i32 %101, %69
  %104 = getelementptr i8, ptr %51, i64 8
  %105 = getelementptr i8, ptr %51, i64 4
  %106 = getelementptr i8, ptr %51, i64 24
  %107 = getelementptr i8, ptr %51, i64 20
  %108 = or disjoint i32 %92, 1
  %109 = mul i32 %108, %108
  %110 = sitofp i32 %109 to float
  %neg19 = fneg reassoc ninf nsz float %74
  %neg20 = fneg reassoc ninf nsz float %72
  %111 = getelementptr i8, ptr %51, i64 96
  %min.iters.check = icmp ult i32 %96, 8
  %n.vec = and i32 %96, 2147483640
  %broadcast.splatinsert = insertelement <8 x i32> poison, i32 %95, i64 0
  %broadcast.splat = shufflevector <8 x i32> %broadcast.splatinsert, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert150 = insertelement <8 x i1> poison, i1 %103, i64 0
  %broadcast.splat151 = shufflevector <8 x i1> %broadcast.splatinsert150, <8 x i1> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert152 = insertelement <8 x i32> poison, i32 %69, i64 0
  %broadcast.splat153 = shufflevector <8 x i32> %broadcast.splatinsert152, <8 x i32> poison, <8 x i32> zeroinitializer
  %cmp.n = icmp eq i32 %96, %n.vec
  %112 = mul i32 %95, -1
  br label %for_loop_body4.outer

after_if3.loopexit:                               ; preds = %after_if10.thread
  br label %after_if3

after_if3:                                        ; preds = %true_block24, %after_for6, %after_if3.loopexit, %true_block, %for_loop_body
  %113 = add nsw i32 %.05387, 1
  %exitcond94.not = icmp eq i32 %113, %18
  br i1 %exitcond94.not, label %after_for.loopexit, label %for_loop_body

for_loop_body4:                                   ; preds = %for_loop_body4.outer, %after_if10
  %.04081 = phi i32 [ %241, %after_if10 ], [ %.04081.ph, %for_loop_body4.outer ]
  %.04180 = phi float [ %.1, %after_if10 ], [ %.04180.ph, %for_loop_body4.outer ]
  %.04279 = phi float [ %.143, %after_if10 ], [ %.04279.ph, %for_loop_body4.outer ]
  %.04677 = phi i32 [ %.147, %after_if10 ], [ %.04478.ph, %for_loop_body4.outer ]
  %.04876 = phi float [ %.149, %after_if10 ], [ %.04876.ph, %for_loop_body4.outer ]
  %.05075 = phi float [ %.151, %after_if10 ], [ %.05075.ph, %for_loop_body4.outer ]
  %114 = icmp eq i32 %.04677, 1
  br i1 %114, label %true_block8, label %after_if10

after_for6:                                       ; preds = %after_if10
  br i1 %.not133, label %after_if3, label %true_block24

true_block8:                                      ; preds = %for_loop_body4
  %115 = load i32, ptr %97, align 4
  %116 = load i32, ptr %98, align 4
  %117 = add i32 %116, -1
  %118 = load i32, ptr %99, align 4
  %119 = add i32 %118, -1
  %120 = add i32 %115, %100
  br i1 %102, label %for_loop_body11.lr.ph, label %after_for13

for_loop_body11.lr.ph:                            ; preds = %true_block8
  %121 = add i32 %.neg60, %115
  %122 = load ptr, ptr %104, align 8
  %123 = load i32, ptr %105, align 4
  %124 = load ptr, ptr %106, align 8
  %125 = load i32, ptr %107, align 4
  br i1 %min.iters.check, label %for_loop_body11.preheader, label %vector.ph

vector.ph:                                        ; preds = %for_loop_body11.lr.ph
  %broadcast.splatinsert154 = insertelement <8 x i32> poison, i32 %120, i64 0
  %broadcast.splat155 = shufflevector <8 x i32> %broadcast.splatinsert154, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert156 = insertelement <8 x i32> poison, i32 %121, i64 0
  %broadcast.splat157 = shufflevector <8 x i32> %broadcast.splatinsert156, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert158 = insertelement <8 x float> poison, float %.05075, i64 0
  %broadcast.splat159 = shufflevector <8 x float> %broadcast.splatinsert158, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert160 = insertelement <8 x float> poison, float %.04876, i64 0
  %broadcast.splat161 = shufflevector <8 x float> %broadcast.splatinsert160, <8 x float> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert162 = insertelement <8 x i32> poison, i32 %117, i64 0
  %broadcast.splat163 = shufflevector <8 x i32> %broadcast.splatinsert162, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert164 = insertelement <8 x i32> poison, i32 %119, i64 0
  %broadcast.splat165 = shufflevector <8 x i32> %broadcast.splatinsert164, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert166 = insertelement <8 x i32> poison, i32 %123, i64 0
  %broadcast.splat167 = shufflevector <8 x i32> %broadcast.splatinsert166, <8 x i32> poison, <8 x i32> zeroinitializer
  %broadcast.splatinsert171 = insertelement <8 x i32> poison, i32 %125, i64 0
  %broadcast.splat172 = shufflevector <8 x i32> %broadcast.splatinsert171, <8 x i32> poison, <8 x i32> zeroinitializer
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %lsr.iv = phi i32 [ %lsr.iv.next, %vector.body ], [ %n.vec, %vector.ph ]
  %vec.ind = phi <8 x i32> [ <i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6, i32 7>, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %233, %vector.body ]
  %vec.phi145 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %231, %vector.body ]
  %vec.phi146 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %229, %vector.body ]
  %vec.phi147 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %227, %vector.body ]
  %vec.phi148 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %225, %vector.body ]
  %vec.phi149 = phi <8 x float> [ zeroinitializer, %vector.ph ], [ %223, %vector.body ]
  %126 = sdiv <8 x i32> %vec.ind, %broadcast.splat
  %127 = mul <8 x i32> %126, %broadcast.splat
  %128 = icmp ne <8 x i32> %127, %vec.ind
  %129 = and <8 x i1> %broadcast.splat151, %128
  %130 = sext <8 x i1> %129 to <8 x i32>
  %131 = add <8 x i32> %126, %130
  %132 = sub <8 x i32> %131, %broadcast.splat153
  %133 = mul <8 x i32> %broadcast.splat, %131
  %134 = add <8 x i32> %broadcast.splat155, %132
  %135 = add <8 x i32> %broadcast.splat157, %vec.ind
  %136 = sub <8 x i32> %135, %133
  %137 = sitofp <8 x i32> %134 to <8 x float>
  %138 = sitofp <8 x i32> %136 to <8 x float>
  %139 = fadd reassoc ninf nsz <8 x float> %broadcast.splat159, %138
  %140 = fadd reassoc ninf nsz <8 x float> %broadcast.splat161, %137
  %141 = add <8 x i32> %136, splat (i32 1)
  %142 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %134, <8 x i32> %broadcast.splat163)
  %143 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %142, <8 x i32> zeroinitializer)
  %144 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %141, <8 x i32> %broadcast.splat165)
  %145 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %144, <8 x i32> zeroinitializer)
  %146 = add <8 x i32> %136, splat (i32 -1)
  %147 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %146, <8 x i32> %broadcast.splat165)
  %148 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %147, <8 x i32> zeroinitializer)
  %149 = mul <8 x i32> %143, %broadcast.splat167
  %150 = add <8 x i32> %149, %145
  %151 = sext <8 x i32> %150 to <8 x i64>
  %152 = getelementptr float, ptr %122, <8 x i64> %151
  %wide.masked.gather = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %152, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %153 = add <8 x i32> %149, %148
  %154 = sext <8 x i32> %153 to <8 x i64>
  %155 = getelementptr float, ptr %122, <8 x i64> %154
  %wide.masked.gather168 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %155, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %156 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather, %wide.masked.gather168
  %157 = fmul reassoc ninf nsz <8 x float> %156, splat (float 5.000000e-01)
  %158 = add <8 x i32> %134, splat (i32 1)
  %159 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %158, <8 x i32> %broadcast.splat163)
  %160 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %159, <8 x i32> zeroinitializer)
  %161 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %136, <8 x i32> %broadcast.splat165)
  %162 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %161, <8 x i32> zeroinitializer)
  %163 = add <8 x i32> %134, splat (i32 -1)
  %164 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %163, <8 x i32> %broadcast.splat163)
  %165 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %164, <8 x i32> zeroinitializer)
  %166 = mul <8 x i32> %160, %broadcast.splat167
  %167 = add <8 x i32> %166, %162
  %168 = sext <8 x i32> %167 to <8 x i64>
  %169 = getelementptr float, ptr %122, <8 x i64> %168
  %wide.masked.gather169 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %169, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %170 = mul <8 x i32> %165, %broadcast.splat167
  %171 = add <8 x i32> %170, %162
  %172 = sext <8 x i32> %171 to <8 x i64>
  %173 = getelementptr float, ptr %122, <8 x i64> %172
  %wide.masked.gather170 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %173, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %174 = fsub reassoc ninf nsz <8 x float> %wide.masked.gather169, %wide.masked.gather170
  %175 = fmul reassoc ninf nsz <8 x float> %174, splat (float 5.000000e-01)
  %176 = tail call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %139)
  %177 = fptosi <8 x float> %176 to <8 x i32>
  %178 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %177, <8 x i32> %broadcast.splat165)
  %179 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %178, <8 x i32> zeroinitializer)
  %180 = tail call reassoc ninf nsz <8 x float> @llvm.floor.v8f32(<8 x float> %140)
  %181 = fptosi <8 x float> %180 to <8 x i32>
  %182 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %181, <8 x i32> %broadcast.splat163)
  %183 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %182, <8 x i32> zeroinitializer)
  %184 = add nuw <8 x i32> %179, splat (i32 1)
  %185 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %184, <8 x i32> %broadcast.splat165)
  %186 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %185, <8 x i32> zeroinitializer)
  %187 = add nuw <8 x i32> %183, splat (i32 1)
  %188 = tail call <8 x i32> @llvm.smin.v8i32(<8 x i32> %187, <8 x i32> %broadcast.splat163)
  %189 = tail call <8 x i32> @llvm.smax.v8i32(<8 x i32> %188, <8 x i32> zeroinitializer)
  %190 = uitofp nneg <8 x i32> %179 to <8 x float>
  %191 = fsub reassoc ninf nsz <8 x float> %139, %190
  %192 = uitofp nneg <8 x i32> %183 to <8 x float>
  %193 = fsub reassoc ninf nsz <8 x float> %140, %192
  %194 = mul <8 x i32> %183, %broadcast.splat172
  %195 = add <8 x i32> %194, %179
  %196 = sext <8 x i32> %195 to <8 x i64>
  %197 = getelementptr float, ptr %124, <8 x i64> %196
  %wide.masked.gather173 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %197, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %198 = add <8 x i32> %186, %194
  %199 = sext <8 x i32> %198 to <8 x i64>
  %200 = getelementptr float, ptr %124, <8 x i64> %199
  %wide.masked.gather174 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %200, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %201 = mul <8 x i32> %189, %broadcast.splat172
  %202 = add <8 x i32> %201, %179
  %203 = sext <8 x i32> %202 to <8 x i64>
  %204 = getelementptr float, ptr %124, <8 x i64> %203
  %wide.masked.gather175 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %204, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %205 = add <8 x i32> %201, %186
  %206 = sext <8 x i32> %205 to <8 x i64>
  %207 = getelementptr float, ptr %124, <8 x i64> %206
  %wide.masked.gather176 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %207, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %208 = fsub reassoc ninf nsz <8 x float> splat (float 1.000000e+00), %191
  %209 = fmul reassoc ninf nsz <8 x float> %208, %wide.masked.gather173
  %210 = fmul reassoc ninf nsz <8 x float> %191, %wide.masked.gather174
  %211 = fadd reassoc ninf nsz <8 x float> %209, %210
  %212 = fmul reassoc ninf nsz <8 x float> %208, %wide.masked.gather175
  %213 = fmul reassoc ninf nsz <8 x float> %191, %wide.masked.gather176
  %214 = fadd reassoc ninf nsz <8 x float> %212, %213
  %215 = fsub reassoc ninf nsz <8 x float> %214, %211
  %216 = fmul reassoc ninf nsz <8 x float> %215, %193
  %217 = add <8 x i32> %149, %162
  %218 = sext <8 x i32> %217 to <8 x i64>
  %219 = getelementptr float, ptr %122, <8 x i64> %218
  %wide.masked.gather177 = tail call <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr> %219, i32 4, <8 x i1> splat (i1 true), <8 x float> poison)
  %220 = fsub reassoc ninf nsz <8 x float> %211, %wide.masked.gather177
  %221 = fadd reassoc ninf nsz <8 x float> %220, %216
  %222 = fmul reassoc ninf nsz <8 x float> %157, %157
  %223 = fadd reassoc ninf nsz <8 x float> %222, %vec.phi149
  %224 = fmul reassoc ninf nsz <8 x float> %175, %157
  %225 = fadd reassoc ninf nsz <8 x float> %224, %vec.phi148
  %226 = fmul reassoc ninf nsz <8 x float> %175, %175
  %227 = fadd reassoc ninf nsz <8 x float> %226, %vec.phi147
  %228 = fmul reassoc ninf nsz <8 x float> %221, %157
  %229 = fadd reassoc ninf nsz <8 x float> %228, %vec.phi146
  %230 = fmul reassoc ninf nsz <8 x float> %221, %175
  %231 = fadd reassoc ninf nsz <8 x float> %230, %vec.phi145
  %232 = tail call <8 x float> @llvm.fabs.v8f32(<8 x float> %221)
  %233 = fadd reassoc ninf nsz <8 x float> %232, %vec.phi
  %vec.ind.next = add <8 x i32> %vec.ind, splat (i32 8)
  %lsr.iv.next = add i32 %lsr.iv, -8
  %234 = icmp eq i32 %lsr.iv.next, 0
  br i1 %234, label %middle.block, label %vector.body, !llvm.loop !10

middle.block:                                     ; preds = %vector.body
  %235 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %233)
  %236 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %231)
  %237 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %229)
  %238 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %227)
  %239 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %225)
  %240 = tail call reassoc ninf nsz float @llvm.vector.reduce.fadd.v8f32(float 0.000000e+00, <8 x float> %223)
  br i1 %cmp.n, label %after_for13, label %for_loop_body11.preheader

for_loop_body11.preheader:                        ; preds = %middle.block, %for_loop_body11.lr.ph
  %.069.ph = phi i32 [ 0, %for_loop_body11.lr.ph ], [ %n.vec, %middle.block ]
  %.03468.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %235, %middle.block ]
  %.03567.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %236, %middle.block ]
  %.03666.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %237, %middle.block ]
  %.03765.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %238, %middle.block ]
  %.03864.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %239, %middle.block ]
  %.03963.ph = phi float [ 0.000000e+00, %for_loop_body11.lr.ph ], [ %240, %middle.block ]
  br label %for_loop_body11

after_if10:                                       ; preds = %true_block21, %false_block16, %for_loop_body4
  %.151 = phi float [ %382, %true_block21 ], [ %382, %false_block16 ], [ %.05075, %for_loop_body4 ]
  %.149 = phi float [ %384, %true_block21 ], [ %384, %false_block16 ], [ %.04876, %for_loop_body4 ]
  %.147 = phi i32 [ 0, %true_block21 ], [ 1, %false_block16 ], [ 0, %for_loop_body4 ]
  %.143 = phi float [ %364, %true_block21 ], [ %364, %false_block16 ], [ %.04279, %for_loop_body4 ]
  %.1 = phi float [ %363, %true_block21 ], [ %363, %false_block16 ], [ %.04180, %for_loop_body4 ]
  %241 = add nuw nsw i32 %.04081, 1
  %exitcond93.not = icmp eq i32 %241, %90
  br i1 %exitcond93.not, label %after_for6, label %for_loop_body4

after_if10.thread:                                ; preds = %after_for13
  %242 = add nuw nsw i32 %.04081, 1
  %exitcond93.not110 = icmp eq i32 %242, %90
  br i1 %exitcond93.not110, label %after_if3.loopexit, label %for_loop_body4.outer

for_loop_body4.outer:                             ; preds = %after_if10.thread, %for_loop_body4.lr.ph
  %.04081.ph = phi i32 [ %242, %after_if10.thread ], [ 0, %for_loop_body4.lr.ph ]
  %.04180.ph = phi float [ %363, %after_if10.thread ], [ %88, %for_loop_body4.lr.ph ]
  %.04279.ph = phi float [ %364, %after_if10.thread ], [ %84, %for_loop_body4.lr.ph ]
  %.not133 = phi i1 [ true, %after_if10.thread ], [ false, %for_loop_body4.lr.ph ]
  %.04478.ph = phi i32 [ 0, %after_if10.thread ], [ 1, %for_loop_body4.lr.ph ]
  %.04876.ph = phi float [ %.04876, %after_if10.thread ], [ %81, %for_loop_body4.lr.ph ]
  %.05075.ph = phi float [ %.05075, %after_if10.thread ], [ %77, %for_loop_body4.lr.ph ]
  br label %for_loop_body4

for_loop_body11:                                  ; preds = %for_loop_body11, %for_loop_body11.preheader
  %.069 = phi i32 [ %359, %for_loop_body11 ], [ %.069.ph, %for_loop_body11.preheader ]
  %.03468 = phi float [ %358, %for_loop_body11 ], [ %.03468.ph, %for_loop_body11.preheader ]
  %.03567 = phi float [ %356, %for_loop_body11 ], [ %.03567.ph, %for_loop_body11.preheader ]
  %.03666 = phi float [ %354, %for_loop_body11 ], [ %.03666.ph, %for_loop_body11.preheader ]
  %.03765 = phi float [ %352, %for_loop_body11 ], [ %.03765.ph, %for_loop_body11.preheader ]
  %.03864 = phi float [ %350, %for_loop_body11 ], [ %.03864.ph, %for_loop_body11.preheader ]
  %.03963 = phi float [ %348, %for_loop_body11 ], [ %.03963.ph, %for_loop_body11.preheader ]
  %243 = sdiv i32 %.069, %95
  %244 = mul i32 %243, %95
  %245 = icmp ne i32 %.069, %244
  %246 = and i1 %103, %245
  %.neg58 = sext i1 %246 to i32
  %247 = add i32 %243, %.neg58
  %248 = sub i32 %247, %69
  %249 = add i32 %120, %248
  %250 = mul i32 %112, %247
  %251 = add i32 %121, %.069
  %252 = add i32 %251, %250
  %253 = sitofp i32 %249 to float
  %254 = sitofp i32 %252 to float
  %255 = fadd reassoc ninf nsz float %.05075, %254
  %256 = fadd reassoc ninf nsz float %.04876, %253
  %257 = add i32 %252, 1
  %258 = tail call i32 @llvm.smin.i32(i32 %249, i32 %117)
  %259 = tail call i32 @llvm.smax.i32(i32 %258, i32 0)
  %260 = tail call i32 @llvm.smin.i32(i32 %257, i32 %119)
  %261 = tail call i32 @llvm.smax.i32(i32 %260, i32 0)
  %262 = add i32 %252, -1
  %263 = tail call i32 @llvm.smin.i32(i32 %262, i32 %119)
  %264 = tail call i32 @llvm.smax.i32(i32 %263, i32 0)
  %265 = mul i32 %259, %123
  %266 = add i32 %265, %261
  %267 = sext i32 %266 to i64
  %268 = getelementptr float, ptr %122, i64 %267
  %269 = load float, ptr %268, align 4
  %270 = add i32 %265, %264
  %271 = sext i32 %270 to i64
  %272 = getelementptr float, ptr %122, i64 %271
  %273 = load float, ptr %272, align 4
  %274 = fsub reassoc ninf nsz float %269, %273
  %275 = fmul reassoc ninf nsz float %274, 5.000000e-01
  %276 = add i32 %249, 1
  %277 = tail call i32 @llvm.smin.i32(i32 %276, i32 %117)
  %278 = tail call i32 @llvm.smax.i32(i32 %277, i32 0)
  %279 = tail call i32 @llvm.smin.i32(i32 %252, i32 %119)
  %280 = tail call i32 @llvm.smax.i32(i32 %279, i32 0)
  %281 = add i32 %249, -1
  %282 = tail call i32 @llvm.smin.i32(i32 %281, i32 %117)
  %283 = tail call i32 @llvm.smax.i32(i32 %282, i32 0)
  %284 = mul i32 %278, %123
  %285 = add i32 %284, %280
  %286 = sext i32 %285 to i64
  %287 = getelementptr float, ptr %122, i64 %286
  %288 = load float, ptr %287, align 4
  %289 = mul i32 %283, %123
  %290 = add i32 %289, %280
  %291 = sext i32 %290 to i64
  %292 = getelementptr float, ptr %122, i64 %291
  %293 = load float, ptr %292, align 4
  %294 = fsub reassoc ninf nsz float %288, %293
  %295 = fmul reassoc ninf nsz float %294, 5.000000e-01
  %296 = tail call reassoc ninf nsz float @llvm.floor.f32(float %255)
  %297 = fptosi float %296 to i32
  %298 = tail call i32 @llvm.smin.i32(i32 %297, i32 %119)
  %299 = tail call i32 @llvm.smax.i32(i32 %298, i32 0)
  %300 = tail call reassoc ninf nsz float @llvm.floor.f32(float %256)
  %301 = fptosi float %300 to i32
  %302 = tail call i32 @llvm.smin.i32(i32 %301, i32 %117)
  %303 = tail call i32 @llvm.smax.i32(i32 %302, i32 0)
  %304 = add nuw i32 %299, 1
  %305 = tail call i32 @llvm.smin.i32(i32 %304, i32 %119)
  %306 = tail call i32 @llvm.smax.i32(i32 %305, i32 0)
  %307 = add nuw i32 %303, 1
  %308 = tail call i32 @llvm.smin.i32(i32 %307, i32 %117)
  %309 = tail call i32 @llvm.smax.i32(i32 %308, i32 0)
  %310 = uitofp nneg i32 %299 to float
  %311 = fsub reassoc ninf nsz float %255, %310
  %312 = uitofp nneg i32 %303 to float
  %313 = fsub reassoc ninf nsz float %256, %312
  %314 = mul i32 %303, %125
  %315 = add i32 %314, %299
  %316 = sext i32 %315 to i64
  %317 = getelementptr float, ptr %124, i64 %316
  %318 = load float, ptr %317, align 4
  %319 = add i32 %306, %314
  %320 = sext i32 %319 to i64
  %321 = getelementptr float, ptr %124, i64 %320
  %322 = load float, ptr %321, align 4
  %323 = mul i32 %309, %125
  %324 = add i32 %323, %299
  %325 = sext i32 %324 to i64
  %326 = getelementptr float, ptr %124, i64 %325
  %327 = load float, ptr %326, align 4
  %328 = add i32 %323, %306
  %329 = sext i32 %328 to i64
  %330 = getelementptr float, ptr %124, i64 %329
  %331 = load float, ptr %330, align 4
  %332 = fsub reassoc ninf nsz float 1.000000e+00, %311
  %333 = fmul reassoc ninf nsz float %332, %318
  %334 = fmul reassoc ninf nsz float %311, %322
  %335 = fadd reassoc ninf nsz float %333, %334
  %336 = fmul reassoc ninf nsz float %332, %327
  %337 = fmul reassoc ninf nsz float %311, %331
  %338 = fadd reassoc ninf nsz float %336, %337
  %339 = fsub reassoc ninf nsz float %338, %335
  %340 = fmul reassoc ninf nsz float %339, %313
  %341 = add i32 %265, %280
  %342 = sext i32 %341 to i64
  %343 = getelementptr float, ptr %122, i64 %342
  %344 = load float, ptr %343, align 4
  %345 = fsub reassoc ninf nsz float %335, %344
  %346 = fadd reassoc ninf nsz float %345, %340
  %347 = fmul reassoc ninf nsz float %275, %275
  %348 = fadd reassoc ninf nsz float %347, %.03963
  %349 = fmul reassoc ninf nsz float %295, %275
  %350 = fadd reassoc ninf nsz float %349, %.03864
  %351 = fmul reassoc ninf nsz float %295, %295
  %352 = fadd reassoc ninf nsz float %351, %.03765
  %353 = fmul reassoc ninf nsz float %346, %275
  %354 = fadd reassoc ninf nsz float %353, %.03666
  %355 = fmul reassoc ninf nsz float %346, %295
  %356 = fadd reassoc ninf nsz float %355, %.03567
  %357 = tail call noundef float @llvm.fabs.f32(float %346)
  %358 = fadd reassoc ninf nsz float %357, %.03468
  %359 = add nuw nsw i32 %.069, 1
  %exitcond.not = icmp eq i32 %96, %359
  br i1 %exitcond.not, label %after_for13.loopexit, label %for_loop_body11, !llvm.loop !13

after_for13.loopexit:                             ; preds = %for_loop_body11
  br label %after_for13

after_for13:                                      ; preds = %after_for13.loopexit, %middle.block, %true_block8
  %.039.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %240, %middle.block ], [ %348, %after_for13.loopexit ]
  %.038.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %239, %middle.block ], [ %350, %after_for13.loopexit ]
  %.037.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %238, %middle.block ], [ %352, %after_for13.loopexit ]
  %.036.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %237, %middle.block ], [ %354, %after_for13.loopexit ]
  %.035.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %236, %middle.block ], [ %356, %after_for13.loopexit ]
  %.034.lcssa = phi float [ 0.000000e+00, %true_block8 ], [ %235, %middle.block ], [ %358, %after_for13.loopexit ]
  %360 = fmul reassoc ninf nsz float %.037.lcssa, %.039.lcssa
  %361 = fmul reassoc ninf nsz float %.038.lcssa, %.038.lcssa
  %362 = fsub reassoc ninf nsz float %360, %361
  %363 = tail call noundef float @llvm.fabs.f32(float %362)
  %364 = fdiv reassoc ninf nsz float %.034.lcssa, %110
  %365 = fcmp reassoc ninf nsz olt float %363, 0x3F1A36E2E0000000
  br i1 %365, label %after_if10.thread, label %false_block16

false_block16:                                    ; preds = %after_for13
  %366 = fdiv reassoc ninf nsz float 1.000000e+00, %362
  %367 = fmul reassoc ninf nsz float %.035.lcssa, %.038.lcssa
  %368 = fmul reassoc ninf nsz float %.036.lcssa, %.037.lcssa
  %369 = fsub reassoc ninf nsz float %367, %368
  %370 = fmul reassoc ninf nsz float %369, %366
  %371 = fmul reassoc ninf nsz float %.036.lcssa, %.038.lcssa
  %372 = fmul reassoc ninf nsz float %.035.lcssa, %.039.lcssa
  %373 = fsub reassoc ninf nsz float %371, %372
  %374 = fmul reassoc ninf nsz float %373, %366
  %375 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %74, float %370)
  %376 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg19, float %375)
  %377 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %74, float %374)
  %378 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg19, float %377)
  %379 = fadd reassoc ninf nsz float %376, %.05075
  %380 = fadd reassoc ninf nsz float %378, %.04876
  %381 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %72, float %379)
  %382 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg20, float %381)
  %383 = tail call reassoc ninf nsz float @llvm.minnum.f32(float %72, float %380)
  %384 = tail call reassoc ninf nsz float @llvm.maxnum.f32(float %neg20, float %383)
  %385 = fmul reassoc ninf nsz float %376, %376
  %386 = fmul reassoc ninf nsz float %378, %378
  %387 = fadd reassoc ninf nsz float %385, %386
  %388 = load float, ptr %111, align 4
  %389 = fmul reassoc ninf nsz float %388, %388
  %390 = fcmp reassoc ninf nsz olt float %387, %389
  br i1 %390, label %true_block21, label %after_if10

true_block21:                                     ; preds = %false_block16
  br label %after_if10

true_block24:                                     ; preds = %after_for6, %true_block1
  %.041.lcssa103 = phi float [ %.1, %after_for6 ], [ %88, %true_block1 ]
  %.042.lcssa102 = phi float [ %.143, %after_for6 ], [ %84, %true_block1 ]
  %.048.lcssa101 = phi float [ %.149, %after_for6 ], [ %81, %true_block1 ]
  %.050.lcssa100 = phi float [ %.151, %after_for6 ], [ %77, %true_block1 ]
  store float %.050.lcssa100, ptr %76, align 4
  store float %.048.lcssa101, ptr %80, align 4
  store float %.042.lcssa102, ptr %83, align 4
  store float %.041.lcssa103, ptr %87, align 4
  %391 = fmul reassoc ninf nsz float %.050.lcssa100, %.050.lcssa100
  %392 = fmul reassoc ninf nsz float %.048.lcssa101, %.048.lcssa101
  %393 = fadd reassoc ninf nsz float %392, %391
  %394 = load ptr, ptr %23, align 8
  %395 = load i32, ptr %24, align 4
  %396 = load i32, ptr %25, align 4
  %397 = mul i32 %395, %37
  %398 = add i32 %397, %39
  %399 = mul i32 %398, %396
  %400 = add i32 %399, 3
  %401 = sext i32 %400 to i64
  %402 = getelementptr float, ptr %394, i64 %401
  store float %393, ptr %402, align 4
  br label %after_if3
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.floor.f32(float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.minnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.maxnum.f32(float, float) #2

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.fabs.f32(float) #2

; Function Attrs: alwaysinline mustprogress nounwind uwtable
define internal void @cpu_parallel_range_for_task(ptr nocapture noundef readonly %0, i32 noundef %1, i32 noundef %2) #3 {
  %4 = alloca %struct.RuntimeContext.7, align 8
  %.sroa.0.0.copyload = load ptr, ptr %0, align 8
  %.sroa.4.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 8
  %.sroa.4.0.copyload = load ptr, ptr %.sroa.4.0..sroa_idx, align 8
  %.sroa.5.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 16
  %.sroa.5.0.copyload = load ptr, ptr %.sroa.5.0..sroa_idx, align 8
  %.sroa.7.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 24
  %.sroa.7.0.copyload = load ptr, ptr %.sroa.7.0..sroa_idx, align 8
  %.sroa.8.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 32
  %.sroa.8.0.copyload = load i64, ptr %.sroa.8.0..sroa_idx, align 8
  %.sroa.9.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 40
  %.sroa.9.0.copyload = load i32, ptr %.sroa.9.0..sroa_idx, align 8
  %.sroa.12.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 44
  %.sroa.12.0.copyload = load i32, ptr %.sroa.12.0..sroa_idx, align 4
  %.sroa.15.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 48
  %.sroa.15.0.copyload = load i32, ptr %.sroa.15.0..sroa_idx, align 8
  %.sroa.17.0..sroa_idx = getelementptr inbounds nuw i8, ptr %0, i64 52
  %.sroa.17.0.copyload = load i32, ptr %.sroa.17.0..sroa_idx, align 4
  %5 = alloca i8, i64 %.sroa.8.0.copyload, align 8
  %.not = icmp eq ptr %.sroa.4.0.copyload, null
  br i1 %.not, label %7, label %6

6:                                                ; preds = %3
  call void %.sroa.4.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
  br label %7

7:                                                ; preds = %6, %3
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(32) %4, ptr noundef nonnull align 8 dereferenceable(32) %.sroa.0.0.copyload, i64 32, i1 false)
  %8 = getelementptr inbounds nuw i8, ptr %4, i64 16
  store i32 %1, ptr %8, align 8
  switch i32 %.sroa.17.0.copyload, label %.loopexit [
    i32 1, label %9
    i32 -1, label %16
  ]

9:                                                ; preds = %7
  %10 = mul nsw i32 %.sroa.15.0.copyload, %2
  %11 = add nsw i32 %10, %.sroa.9.0.copyload
  %12 = add nsw i32 %11, %.sroa.15.0.copyload
  %.sroa.speculated28 = call i32 @llvm.smin.i32(i32 %.sroa.12.0.copyload, i32 %12)
  %13 = icmp slt i32 %11, %.sroa.speculated28
  br i1 %13, label %.lr.ph41.preheader, label %.loopexit

.lr.ph41.preheader:                               ; preds = %9
  br label %.lr.ph41

.lr.ph41:                                         ; preds = %.lr.ph41, %.lr.ph41.preheader
  %.02040 = phi i32 [ %14, %.lr.ph41 ], [ %11, %.lr.ph41.preheader ]
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.02040) #8
  %14 = add i32 %.02040, 1
  %15 = icmp slt i32 %14, %.sroa.speculated28
  br i1 %15, label %.lr.ph41, label %.loopexit.loopexit, !llvm.loop !14

16:                                               ; preds = %7
  %17 = mul nsw i32 %.sroa.15.0.copyload, %2
  %18 = sub nsw i32 %.sroa.12.0.copyload, %17
  %19 = mul nsw i32 %18, %.sroa.15.0.copyload
  %.sroa.speculated = call i32 @llvm.smax.i32(i32 %.sroa.9.0.copyload, i32 %19)
  %.not24.not38 = icmp sgt i32 %18, %.sroa.speculated
  br i1 %.not24.not38, label %.lr.ph.preheader, label %.loopexit

.lr.ph.preheader:                                 ; preds = %16
  br label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %.lr.ph.preheader
  %.0.in39 = phi i32 [ %.0, %.lr.ph ], [ %18, %.lr.ph.preheader ]
  %.0 = add i32 %.0.in39, -1
  call void %.sroa.5.0.copyload(ptr noundef nonnull %4, ptr noundef nonnull %5, i32 noundef %.0) #8
  %.not24.not = icmp sgt i32 %.0, %.sroa.speculated
  br i1 %.not24.not, label %.lr.ph, label %.loopexit.loopexit46, !llvm.loop !16

.loopexit.loopexit:                               ; preds = %.lr.ph41
  br label %.loopexit

.loopexit.loopexit46:                             ; preds = %.lr.ph
  br label %.loopexit

.loopexit:                                        ; preds = %.loopexit.loopexit46, %.loopexit.loopexit, %16, %9, %7
  %.not25 = icmp eq ptr %.sroa.7.0.copyload, null
  br i1 %.not25, label %21, label %20

20:                                               ; preds = %.loopexit
  call void %.sroa.7.0.copyload(ptr noundef %.sroa.0.0.copyload, ptr noundef nonnull %5) #8
  br label %21

21:                                               ; preds = %20, %.loopexit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #4

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smin.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.smax.i32(i32, i32) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #6

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smin.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x i32> @llvm.smax.v8i32(<8 x i32>, <8 x i32>) #5

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(read)
declare <8 x float> @llvm.masked.gather.v8f32.v8p0(<8 x ptr>, i32 immarg, <8 x i1>, <8 x float>) #7

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.floor.v8f32(<8 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare <8 x float> @llvm.fabs.v8f32(<8 x float>) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.vector.reduce.fadd.v8f32(float, <8 x float>) #5

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(readwrite, inaccessiblemem: none) }
attributes #1 = { nofree norecurse nosync nounwind memory(readwrite, inaccessiblemem: none) }
attributes #2 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { alwaysinline mustprogress nounwind uwtable "frame-pointer"="none" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #5 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #7 = { nocallback nofree nosync nounwind willreturn memory(read) }
attributes #8 = { nounwind }

!llvm.linker.options = !{!0, !1, !2, !3, !4, !5}
!llvm.ident = !{!6}
!llvm.module.flags = !{!7, !8, !9}

!0 = !{!"/FAILIFMISMATCH:\22_MSC_VER=1900\22"}
!1 = !{!"/FAILIFMISMATCH:\22_ITERATOR_DEBUG_LEVEL=0\22"}
!2 = !{!"/FAILIFMISMATCH:\22RuntimeLibrary=MT_StaticRelease\22"}
!3 = !{!"/DEFAULTLIB:libcpmt.lib"}
!4 = !{!"/FAILIFMISMATCH:\22_CRT_STDIO_ISO_WIDE_SPECIFIERS=0\22"}
!5 = !{!"/alternatename:_Avx2WmemEnabled=_Avx2WmemEnabledWeakValue"}
!6 = !{!"clang version 14.0.6"}
!7 = !{i32 1, !"wchar_size", i32 2}
!8 = !{i32 8, !"PIC Level", i32 2}
!9 = !{i32 7, !"uwtable", i32 1}
!10 = distinct !{!10, !11, !12}
!11 = !{!"llvm.loop.isvectorized", i32 1}
!12 = !{!"llvm.loop.unroll.runtime.disable"}
!13 = distinct !{!13, !12, !11}
!14 = distinct !{!14, !15}
!15 = !{!"llvm.loop.mustprogress"}
!16 = distinct !{!16, !15}
